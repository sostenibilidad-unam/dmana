import networkx as nx


def mental_model(queryset):
    """
    return a networkx DiGraph object
    from a Django Orm Queryset of mental edges
    """
    g = nx.DiGraph()
    for e in queryset:
        g.add_edge(e.source.name,
                   e.target.name)
    return g
