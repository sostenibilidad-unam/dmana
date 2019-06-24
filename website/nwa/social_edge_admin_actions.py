import tempfile
from .networks import social_agraph, social_network
from .models import Sector
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
import networkx as nx
from color_tol import sequential, qualitative


def download_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       social_network(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="ego_network.graphml"'
    return response


download_as_graphml.\
    short_description = "Download GraphML format suitalbe for Cytoscape"


def download_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(social_network(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response['Content-Disposition'] \
        = 'attachment; filename="ego_network.dot"'
    return response


download_as_dot.\
    short_description = "Download DOT format for Graphviz"


def download_as_pdf(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = social_agraph(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="ego_network.pdf"'
        return response


download_as_pdf.\
    short_description = "Download as PDF"


def create_visjs(modeladmin, request, queryset):

    g = social_network(queryset)
        
    edgecolors = list(reversed(sequential(5).html_colors))

    edges = []
    for e in queryset:
        e.color = edgecolors[e.distance]
        e.length = (e.distance ** 3) + 1
        edges.append(e)

    
    degree = g.in_degree()
    bc = nx.betweenness_centrality(g)


    colors = qualitative(Sector.objects.count() + 1).html_colors
    sectorcolor = {c[0]:c[1]
                   for c in zip(list(Sector.objects.all()) + [None, ],
                                colors)}


    # STATICFILES_DIRS                 
    with open('/home/rgarcia/tmp/aguas.html', 'w') as f:
        f.write(render_to_string(
            'nwa/force_directed.html',
            {'nodes': set([(e.source.id,
                            bc[e.source],
                            e.source.name,
                            sectorcolor[e.source.sector])
                           for e in queryset] \
                          + [(e.target.id,
                              bc[e.target],
                              e.target.name,
                              sectorcolor[e.target.sector])
                             for e in queryset]),
             'edges': edges
            }))
    return HttpResponseRedirect("/export/")


create_visjs.\
    short_description = "Export as interactive webpage"
