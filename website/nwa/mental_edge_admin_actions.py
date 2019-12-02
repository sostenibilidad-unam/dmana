from .networks import mental_model
import tempfile
from .mental_model_contrast import networks_from_qs, graph_contrast_heatmap
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template.loader import render_to_string
import networkx as nx
import uuid
import matplotlib.pyplot as plt
import matplotlib
from os import path, mkdir
from itertools import combinations
from django.utils.text import slugify


def contrast_heatmaps(modeladmin, request, queryset):
    export_id = str(uuid.uuid4())
    networks = networks_from_qs(queryset)

    outdir = path.join(settings.EXPORT, export_id)
    mkdir(outdir)

    with open(path.join(outdir, 'index.html'), 'w') as index:
        plots = {}
        for pair in combinations(networks, 2):

            g = networks[pair[0]]
            h = networks[pair[1]]
            plt = graph_contrast_heatmap(g, h)
            filename = "%s.png" % slugify(pair)
            plt.savefig(path.join(outdir, filename),
                        dpi=300)
            title = "<span style=\"color:red\">%s %s</span> vs. <span style=\"color:blue\">%s %s</span>" % (pair[0][0],
                                         pair[0][1],
                                         pair[1][0],
                                         pair[1][1])
            plots[title] = (settings.STATIC_URL
                            + 'networks/'
                            + export_id + "/"
                            + filename)

        index.write(render_to_string('nwa/mm_contrast_heatmaps.html',
                                     {'plots': plots}))

    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + export_id + "/index.html")


contrast_heatmaps.\
    short_description = "Contrast adjacency \
    matrices of mental maps. Choose different projects or different egos."


def download_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       mental_model(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="cognitive_map.graphml"'
    return response


download_as_graphml.\
    short_description = "Download GraphML format suitalbe for Cytoscape"


def download_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(mental_model(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response[
        'Content-Disposition'] = 'attachment; filename="cognitive_map.dot"'
    return response


download_as_dot.\
    short_description = "Download DOT format for Graphviz"


def download_as_pdf(modeladmin, request, queryset):

    g = mental_model(queryset)

    for n in g.nodes:
        if g.in_degree(n) == 0:
            g.nodes[n]['color'] = 'green'
        elif g.out_degree(n) == 0:
            g.nodes[n]['color'] = 'red'
        else:
            g.nodes[n]['color'] = 'black'

    lut = max([g.get_edge_data(*e)['w'] for e in g.edges])
    cmap = matplotlib.cm.get_cmap('Blues', lut)
    
    for e in g.edges:
        w = g.get_edge_data(*e)['w']
        g.add_edge(*e,
                   penwidth=w*2,
                   color=matplotlib.colors.rgb2hex(cmap(w)[:3]))

    response = HttpResponse(
        nx.drawing.nx_pydot.to_pydot(g).create_pdf(),
        content_type="application/pdf")
    response[
        'Content-Disposition'] = 'attachment; filename="cognitive_map.pdf"'
    return response


download_as_pdf.\
    short_description = "Download as PDF"


def download_as_pajek(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        g = mental_model(queryset)
        nx.write_pajek(g, tmp)
        tmp.seek(0)
        response = HttpResponse(tmp.read(),
                                content_type="text/net")
        response['Content-Disposition'] \
            = 'attachment; filename="mental_model.net"'
        return response


download_as_pajek.\
    short_description = "Download Pajek format"


def create_visjs(modeladmin, request, queryset):
    export_id = str(uuid.uuid4())

    g = mental_model(queryset)

    fig = plt.figure(figsize=(7, 5), dpi=100)
    degree_sequence = sorted(dict(nx.degree(g)).values(),
                             reverse=True)
    f = plt.loglog(degree_sequence,
                   marker='.',
                   linewidth=0.3,
                   color='navy',
                   alpha=0.3)
    ax = plt.gca()
    ax.set(xlabel='degree', ylabel='frequency',
       title='Connectivity degree (log-log)')
    
    filename = '%s_degree_loglog.png' % export_id
    fig.savefig(path.join(settings.EXPORT,
                          filename))

    bc = nx.betweenness_centrality(g)

    nodes = set()
    for e in queryset:

        e.width = g.get_edge_data(e.source.name, e.target.name)['w'] * 2
        
        if g.in_degree(e.source.name) == 0:
            color = '#ccebc5'
        elif g.out_degree(e.source.name) == 0:
            color = '#fbb4ae'
        else:
            color = '#b3cde3'
        nodes.add((e.source.id, bc[e.source.name], e.source.name, color))

        if g.in_degree(e.target.name) == 0:
            color = '#ccebc5'
        elif g.out_degree(e.target.name) == 0:
            color = '#fbb4ae'
        else:
            color = '#b3cde3'
        nodes.add((e.target.id, bc[e.target.name], e.target.name, color))

    filename = "%s.html" % export_id
    with open(path.join(settings.EXPORT,
                        filename), 'w') as f:
        f.write(render_to_string(
            'nwa/mm.html',
            {'nodes': nodes,
             'edges': queryset,
             'export_id': export_id
             }))
    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + filename)


create_visjs.\
    short_description = "Create interactive browser based visualization"
