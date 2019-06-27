import tempfile
from .networks import social_agraph, social_network
from .models import Sector
from .scale import Scale
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
import networkx as nx
from django.conf import settings
from os import path
import uuid
import matplotlib.pyplot as plt


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
    export_id = str(uuid.uuid4())

    g = social_network(queryset)

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

    scale = Scale(domain=[0, 1.0],
                  range=[0, 255])
    max_distance = max([e.distance for e in queryset])
    dist_scale = Scale(domain=[0, max_distance],
                       range=[0, max_distance + 1])

    cm = plt.get_cmap('GnBu', lut=5)

    edges = []
    for e in queryset:
        e.color = tuple([scale.linear(c)
                         for c in cm(int(dist_scale.linear_inv(e.distance)))])
        e.length = (e.distance ** 3) + 1
        edges.append(e)

    bc = nx.betweenness_centrality(g)

    sector_count = Sector.objects.count()
    cm = plt.get_cmap('Set3', lut=sector_count)
    n = 1
    sectorcolor = {None: tuple([scale.linear(c) for c in cm(n)])}
    for sector in Sector.objects.all():
        sectorcolor[sector] = tuple([scale.linear(c) for c in cm(n)])
        n += 1

    filename = "%s.html" % export_id
    with open(path.join(settings.EXPORT,
                        filename), 'w') as f:
        f.write(render_to_string(
            'nwa/force_directed.html',
            {'nodes': set([(e.source.id,
                            bc[e.source],
                            e.source.name,
                            sectorcolor[e.source.sector])
                           for e in queryset]
                          + [(e.target.id,
                              bc[e.target],
                              e.target.name,
                              sectorcolor[e.target.sector])
                             for e in queryset]),
             'edges': edges,
             'export_id': export_id
             }))
    return HttpResponseRedirect(settings.STATIC_URL
                                + 'networks/' + filename)


create_visjs.\
    short_description = "Export as interactive webpage"
