from .networks import mental_model
from django.http import HttpResponse
import networkx as nx


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
