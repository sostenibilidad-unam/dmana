import pygraphviz as pgv
import tempfile
from django.template.loader import render_to_string
from .networks import agency_network, agency_agraph, agency_agraph_orgs2cats
from django.http import HttpResponse
import networkx as nx


def download_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       agency_network(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_network.graphml"'
    return response


download_as_graphml.\
    short_description = "Download GraphML format suitalbe for Cytoscape"


def download_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(agency_network(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_network.dot"'
    return response


download_as_dot.\
    short_description = "Download DOT format for Graphviz"


def download_as_pdf(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = agency_agraph(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.pdf"'
        return response


download_as_pdf.\
    short_description = "Download as PDF"


def download_orgs2cats_as_pdf(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = agency_agraph_orgs2cats(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.pdf"'
        return response


download_orgs2cats_as_pdf.\
    short_description = "Download orgs2cats as PDF"


def relationship_diagram_as_pdf(modeladmin, request, queryset):
    egos = set()
    egos_alters = set()
    alters = set()
    actions = set()
    alters_actions = set()
    for e in queryset:
        egos.add(e.person)
        actions.add(e.action)
        for p in e.people.all():
            egos_alters.add((e.person.id, p.id))
            alters.add(p)
            alters_actions.add((p.id, e.action.id))
    A = pgv.AGraph()
    A.from_string(render_to_string('nwa/relationship_diagram.dot',
                                   {'queryset': queryset,
                                    'egos': egos,
                                    'egos_alters': egos_alters,
                                    'alters': alters,
                                    'actions': actions,
                                    'alters_actions': alters_actions
                                    }).encode('utf-8'))
    with tempfile.SpooledTemporaryFile() as tmp:
        A.draw(tmp, format='pdf', prog='dot')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="power_network.pdf"'
        return response


relationship_diagram_as_pdf.\
    short_description = "Download Relationship Diagram as PDF"


def relationship_diagram_orgs2cats(modeladmin, request, queryset):
    egos = set()
    egos_alters = set()
    alters = set()
    actions = set()
    alters_actions = set()
    for e in queryset:
        egos.add(e.person.org_or_self())
        actions.add(e.action.category_or_action())
        for p in e.people.all():
            egos_alters.add((e.person.org_or_self().id, p.org_or_self().id))
            alters.add(p.org_or_self())
            alters_actions.add((p.org_or_self().id,
                                e.action.category_or_action().id))
    A = pgv.AGraph()
    A.from_string(render_to_string('nwa/relationship_diagram.dot',
                                   {'egos': egos,
                                    'egos_alters': egos_alters,
                                    'alters': alters,
                                    'alters_actions': alters_actions,
                                    'actions': actions
                                    }).encode('utf-8'))
    with tempfile.SpooledTemporaryFile() as tmp:
        A.draw(tmp, format='pdf', prog='dot')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="power_network_orgs2cats.pdf"'
        return response


relationship_diagram_orgs2cats.\
    short_description = "Download orgs2cats relationship diagram as PDF"