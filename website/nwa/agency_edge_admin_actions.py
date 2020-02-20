import pygraphviz as pgv
import tempfile
from django.urls import reverse
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.conf import settings
from os import path
from .models import SocialEdge
from .networks import agency_network, agency_agraph, agency_agraph_orgs2cats, agency_ego_alter, \
    agency_ego_alter_action, agency_ego_alter_agraph, agency_alter_action, agency_alter_action_agraph
from .scale import Scale
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import networkx as nx
import uuid
import matplotlib.pyplot as plt
from .agency_hiveplot import AgencyHiveplot
from django.conf import settings


def download_ego_alter_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(agency_ego_alter(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_ego_alter.dot"'
    return response


download_ego_alter_as_dot.\
    short_description = "Download Ego-Alter network in DOT format for Graphviz"


def download_ego_alter_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       agency_ego_alter(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_ego_alter.graphml"'
    return response

download_ego_alter_as_graphml.\
    short_description = "Download Ego-Alter network in GraphML format for Cytoscape"



def extract_social_network(modeladmin, request, queryset):
    for e in queryset:
        for alter in e.people.all():
            try:
                se = SocialEdge(source=e.person,
                                target=alter,
                                project=e.project,
                                author=e.author)
                se.save()
            except IntegrityError:
                pass
            
    return HttpResponseRedirect(reverse('admin:nwa_socialedge_changelist'))

extract_social_network.\
    short_description = "Create social edges from selected agency edges"



def download_ego_alter_action_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       agency_ego_alter_action(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_ego_alter_action.graphml"'
    return response

download_ego_alter_action_as_graphml.\
    short_description = "Download Ego-Alter-Action network in GraphML format for Cytoscape"


def download_ego_alter_as_pdf(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = agency_ego_alter_agraph(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_ego_alter.pdf"'
        return response


download_ego_alter_as_pdf.\
    short_description = "Download Ego-Alter network as PDF"




def download_alter_action_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(agency_alter_action(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_alter_action.dot"'
    return response


download_alter_action_as_dot.\
    short_description = "Download Alter-Action network in DOT format for Graphviz"


def download_alter_action_as_graphml(modeladmin, request, queryset):
    response = HttpResponse(
        "\n".join([l
                   for l in
                   nx.readwrite.graphml.generate_graphml(
                       agency_alter_action(queryset))]),
        content_type="application/xml")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_alter_action.graphml"'
    return response

download_alter_action_as_graphml.\
    short_description = "Download Alter-Action network in GraphML format for Cytoscape"


def download_alter_action_as_pdf(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = agency_alter_action_agraph(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_ego_alter.pdf"'
        return response


download_alter_action_as_pdf.\
    short_description = "Download Alter-Action network as PDF"




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
    short_description = "Agency Network in GraphML format for Cytoscape"


def download_as_dot(modeladmin, request, queryset):
    A = nx.nx_agraph.to_agraph(agency_network(queryset))
    response = HttpResponse(A.string(),
                            content_type="text/dot")
    response['Content-Disposition'] \
        = 'attachment; filename="agency_network.dot"'
    return response


download_as_dot.\
    short_description = "Agency Network in DOT format for Graphviz"


def download_as_pajek(modeladmin, request, queryset):
    with tempfile.SpooledTemporaryFile() as tmp:
        G = agency_network(queryset)
        nx.write_pajek(G, tmp)
        tmp.seek(0)
        response = HttpResponse(tmp.read(),
                                content_type="text/net")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.net"'
        return response


download_as_pajek.\
    short_description = "Download Pajek format"


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
            = 'attachment; filename="agency_relationship_diagram.pdf"'
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
            = 'attachment; filename="relationship_diagram_orgs2cats.pdf"'
        return response


relationship_diagram_orgs2cats.\
    short_description = "Download orgs2cats relationship diagram as PDF"


def create_visjs(modeladmin, request, queryset):
    export_id = uuid.uuid4()

    g = agency_network(queryset)

    bc = nx.betweenness_centrality(g)

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

    edges = []
    edge_data = {}
    for e in queryset:
        edges.append(e)
        edge_data['a%s' % e.action.id] = (
            "<h2>%s</h2><ul>" % e.action.action
            + " ".join(["<li>%s</li>" % str(p)
                        for p in e.people.all()])
            + "</ul>")

    filename = "%s.html" % export_id
    with open(path.join(settings.EXPORT,
                        filename),
              'w',
              encoding='utf-8') as f:
        f.write(render_to_string(
            'nwa/agency.html',
            {'nodes': set([("p%s" % e.person.id,
                            bc[e.person],
                            e.person.name,
                            '#b3cde3')
                           for e in queryset]
                          + [("a%s" % e.action.id,
                              bc[e.action],
                              e.action.action,
                              '#ccebc5')
                             for e in queryset]),
             'edges': edges,
             'edge_data': edge_data,
             'export_id': export_id
             }))
    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + filename)


create_visjs.\
    short_description = "Create interactive browser based visualization"


def create_agency_hiveplot(modeladmin, request, queryset):
    print(len(list(queryset)))
    ah = AgencyHiveplot(queryset)
    ah.add_ego_axis()
    ah.add_sector_axes()
    ah.add_actioncat_axes()
    ah.connect_axes()

    export_id = uuid.uuid4()
    filename = "%s.svg" % export_id

    ah.save(path.join(settings.EXPORT,
                      filename))
    del(ah)
    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + filename)

create_agency_hiveplot.\
    short_description = "create agency hiveplot"
