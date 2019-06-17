import networkx as nx
import pygraphviz as pgv


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


def power_network(queryset):
    g = nx.Graph()
    for e in queryset:
        g.add_node(e.person, type='person')
        g.add_node(e.power.name, type='power')
        g.add_edge(e.person.name,
                   e.power.name)
    return g


def power_agraph(queryset):
    g = pgv.AGraph()
    g.graph_attr['splines'] = 'true'

    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   shape='box')
        g.add_node(e.power.name,
                   colorscheme='set13', color=3,
                   shape='egg')
        g.add_edge(e.person,
                   e.power.name,
                   colorscheme='set13', color=1)
    return g


def agency_network(queryset):
    g = nx.DiGraph()
    for e in queryset:
        g.add_node(e.person, type='person',
                   sector=str(e.person.sector),
                   ego=e.person.ego)
        g.add_node(e.action, type='action',
                   category=str(e.action.category))
        g.add_edge(e.person,
                   e.action,
                   distance="" if e.distance is None else e.distance,
                   interaction="" if e.interaction is None else e.interaction,
                   polarity="" if e.polarity is None else e.polarity,
                   people=",".join([str(p)
                                    for p in e.people.all()]))
    return g


def agency_agraph(queryset):
    g = pgv.AGraph(directed=True)
    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   shape='box')
        g.add_node(e.action,
                   colorscheme='set13', color=3, shape="egg")
        g.add_edge(e.person,
                   e.action)
    return g
