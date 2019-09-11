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

    networks = {}
    for k in edges:
        g = nx.DiGraph()
        g.add_edges_from(edges[k])
        networks[k] = g

    return networks


def graph_contrast_heatmap(G, H):

    # grab set of nodes from all graphs
    nodelist = set()
    for g in [G, H, ]:
        for node in g.nodes:
            nodelist.add(node)

    g = nx.to_pandas_adjacency(G, nodelist=nodelist)
    h = nx.to_pandas_adjacency(H, nodelist=nodelist)

    a = g - h

    # drop zeros from resulting dataframe
    a = a.loc[(a != 0).any(1)]
    a = a.loc[:, (a != 0).any(axis=0)]

    fig, ax = plt.subplots(figsize=(10, 10))

    ax = seaborn.heatmap(a,
                         cbar=False,
                         center=0,
                         square=True,
                         linewidths=1.5,
                         cmap=['red', 'white', 'green'])

    ax.set_xticklabels(labels=nodelist, rotation=45,
                       rotation_mode="anchor", ha="right", fontsize=7)

    ax.set_yticklabels(labels=nodelist, fontsize=7)

    fig.tight_layout()

    return plt
