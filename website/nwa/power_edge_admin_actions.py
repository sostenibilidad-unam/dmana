from .networks import power_network, power_agraph
import tempfile
from django.http import HttpResponse
import networkx as nx
import uuid
import matplotlib.pyplot as plt
from os import path
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect



def download_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       power_network(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="power_network.graphml"'
    return response


download_as_graphml.\
    short_description = "Download GraphML format suitalbe for Cytoscape"


def download_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(power_network(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response[
        'Content-Disposition'] = 'attachment; filename="power_network.dot"'
    return response


download_as_dot.\
    short_description = "Download DOT format for Graphviz"


def download_as_pajek(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        g = power_network(queryset)
        nx.write_pajek(g, tmp)
        tmp.seek(0)
        response = HttpResponse(tmp.read(),
                                content_type="text/net")
        response['Content-Disposition'] \
            = 'attachment; filename="power_network.net"'
        return response


download_as_pajek.\
    short_description = "Download Pajek format"


def download_as_pdf(modeladmin, request, queryset):
    tmp = tempfile.SpooledTemporaryFile()
    # nx.drawing.nx_pydot.to_pydot(power_network(queryset)).create_pdf(),
    G = power_agraph(queryset)
    G.draw(tmp, format='pdf', prog='neato')
    tmp.seek(0)
    response = HttpResponse(
        tmp.read(),
        content_type="application/pdf")
    response[
        'Content-Disposition'] = 'attachment; filename="power_network.pdf"'
    return response


download_as_pdf.\
    short_description = "Download as PDF"


def create_visjs(modeladmin, request, queryset):
    export_id = uuid.uuid4()

    g = power_network(queryset)

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

    filename = "%s.html" % export_id
    with open(path.join(settings.EXPORT,
                        filename),
              'w',
              encoding='utf-8') as f:
        f.write(render_to_string(
            'nwa/power_network.html',
            {'nodes': [(v,
                       g.node[v]['type'])
                       for v in g.nodes],
             'edges': g.edges,
             'export_id': export_id
             }))
    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + filename)


create_visjs.\
    short_description = "Create interactive browser based visualization"
