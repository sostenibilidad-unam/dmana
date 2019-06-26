from .networks import mental_model
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template.loader import render_to_string
import networkx as nx
import uuid
import matplotlib.pyplot as plt
from os import path


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

    response = HttpResponse(
        nx.drawing.nx_pydot.to_pydot(g).create_pdf(),
        content_type="application/pdf")
    response[
        'Content-Disposition'] = 'attachment; filename="cognitive_map.pdf"'
    return response


download_as_pdf.\
    short_description = "Download as PDF"


def create_visjs(modeladmin, request, queryset):
    export_id = uuid.uuid4()

    g = mental_model(queryset)

    fig = plt.figure(figsize=(5, 5), dpi=100)
    degree_sequence = sorted(dict(nx.degree(g)).values(),
                             reverse=True)
    f = plt.loglog(degree_sequence,
                   marker='.',
                   linewidth=0.3,
                   color='navy',
                   alpha=0.3)
    filename = '%s_degree_loglog.png' % export_id
    fig.savefig(path.join(settings.EXPORT,
                          filename))

    bc = nx.betweenness_centrality(g)

    nodes = set()
    for e in queryset:
        if g.in_degree(e.source.name) == 0:
            color = 'green'
        elif g.out_degree(e.source.name) == 0:
            color = 'red'
        else:
            color = '#aabbdd'
        nodes.add((e.source.id, bc[e.source.name], e.source.name, color))

        if g.in_degree(e.target.name) == 0:
            color = 'green'
        elif g.out_degree(e.target.name) == 0:
            color = 'red'
        else:
            color = '#aabbdd'
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
    short_description = "Export as interactive webpage"
