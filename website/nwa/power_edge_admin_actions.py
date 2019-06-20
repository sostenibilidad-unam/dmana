from .networks import power_network, power_agraph
from django.http import HttpResponse
import networkx as nx
import tempfile


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
