import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn
import networkx as nx

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
    fig, ax = plt.subplots(figsize=(10, 10))

    # same network, return empty plot
    if G.edges == H.edges:
        return plt

    # grab set of nodes from all graphs
    nodelist = set()
    for g in [G, H, ]:
        for node in g.nodes:
            nodelist.add(node)

    g = nx.to_pandas_adjacency(G, nodelist=nodelist)
    h = nx.to_pandas_adjacency(H, nodelist=nodelist)

    h.replace(1, 2, inplace=True)
    a = g + h

    # drop zeros from resulting dataframe
    a = a.loc[(a != 0).any(1)]
    a = a.loc[:, (a != 0).any(axis=0)]

    ax = seaborn.heatmap(a,
                         cbar=False,
                         square=True,
                         linewidths=1.5,
                         cmap=['white', 'red', 'blue', 'purple'])

    ax.set_xticklabels(labels=list(a.columns), rotation=45,
                       rotation_mode="anchor", ha="right", fontsize=7)

    ax.set_yticklabels(labels=list(a.index), fontsize=7)

    plt.xlabel("target")
    plt.ylabel("source")               
    
    fig.tight_layout()

    return plt



def graph_contrast_report(G, H):

    # same network, return empty plot
    if G.edges == H.edges:
        return "same graph"

    # grab set of nodes from all graphs
    nodelist = set()
    for g in [G, H, ]:
        for node in g.nodes:
            nodelist.add(node)

    g = nx.to_pandas_adjacency(G, nodelist=nodelist)
    h = nx.to_pandas_adjacency(H, nodelist=nodelist)

    h.replace(1, 2, inplace=True)
    a = g + h

    # drop zeros from resulting dataframe
    a = a.loc[(a != 0).any(1)]
    a = a.loc[:, (a != 0).any(axis=0)]

    no_change = 0
    deletion = 0
    insertion = 0
    purple = 0
    for r in a.to_numpy():
        row = list(r)
        no_change += row.count(0)
        deletion += row.count(1)
        insertion += row.count(2)
        purple += row.count(3)

    return (no_change,
            deletion,
            insertion,
            purple)
