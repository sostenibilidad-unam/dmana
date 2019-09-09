import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn
import networkx as nx
from pprint import pprint


def networks_from_qs(queryset):
    # split into edgelists for person/project combinations
    edges = {}
    for edge in queryset:
        el = edges.get((edge.person, edge.project),
                       [])
        el.append((edge.source, edge.target))
        edges[(edge.person, edge.project)] = el

    networks = []
    for k in edges:
        g = nx.Graph()
        g.add_edges_from(edges[k])
        networks.append(g)

    return networks


def graph_contrast_heatmap(G, H):

    # grab set of nodes from all graphs
    networks = [G, H, ]

    nodelist = set()
    for g in networks:
        for node in g.nodes:
            nodelist.add(node)

    g = nx.to_pandas_adjacency(G, nodelist=nodelist)
    h = nx.to_pandas_adjacency(H, nodelist=nodelist)

    a = g - h

    seaborn.palplot(seaborn.diverging_palette(220, 20, n=3, center='light'))

    fig, ax = plt.subplots(figsize=(10, 10))
    # im = ax.imshow(a)

    # ax.set_xticks(range(len(nodelist)))
    # ax.set_yticks(range(len(nodelist)))

    # ax.set_xticklabels(nodelist)
    # ax.set_yticklabels(nodelist)

    # plt.setp(ax.get_yticklabels(), fontsize=8)
    # plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
    #          rotation_mode="anchor", fontsize=8)

    ax = seaborn.heatmap(a,
                         cbar=False,
                         center=0,
                         square=True,
                         linewidths=1.5,
                         cmap=['red', 'white', 'green'])

    ax.set_xticklabels(labels=nodelist, rotation=45,
                       rotation_mode="anchor", ha="right", fontsize=7)

    ax.set_yticklabels(labels=nodelist, fontsize=7)
#    xlab.set_rotation(45)

    fig.tight_layout()

    plt.savefig('/tmp/aguas.png')
