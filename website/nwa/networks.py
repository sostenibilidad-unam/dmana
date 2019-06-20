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
    g = pgv.AGraph(spline='splines', overlap='false', outputorder='edgesfirst')

    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   style='filled', fillcolor='white',
                   shape='box')
        g.add_node(e.power.name,
                   colorscheme='set13', color=3,
                   style='filled', fillcolor='white',
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
    g = pgv.AGraph(directed=True, overlap='scale')
    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   shape='box')
        g.add_node(e.action,
                   colorscheme='set13', color=3,
                   shape="box",
                   fontsize='9',
                   style='filled', fillcolor='white')
        g.add_edge(e.person,
                   e.action)
    return g


def social_network(queryset):
    """
    return a networkx DiGraph object
    from a Django Orm Queryset of social edges
    """
    g = nx.DiGraph()
    for e in queryset:
        g.add_edge(e.source,
                   e.target,
                   influence=e.influence,
                   distance=e.distance,
                   interaction=e.interaction,
                   polarity=e.polarity)
    return g


def social_agraph(queryset):
    g = pgv.AGraph(directed=True, spline='splines', overlap='false', outputorder='edgesfirst')
    scheme = "gnbu%s" % (max([e.distance for e in queryset]) + 1)


    sectors = [e.source.sector for e in queryset]
    sectors += [e.target.sector for e in queryset]
    sectors = list(set(sectors))

    if len(sectors) <= 12:
        nodescheme = "set3%s" % len(sectors)
    else:
        nodescheme = "X11"
    print(nodescheme)
    print(sectors)

    for e in queryset:
        print(sectors.index(e.source.sector) + 1)
        fillcolor="/%s/%s" % (nodescheme, sectors.index(e.source.sector) + 1)
        g.add_node(e.source,
                   shape='box',
                   fontsize='9',
                   style='filled',
                   fillcolor=fillcolor)
        fillcolor="/%s/%s" % (nodescheme, sectors.index(e.target.sector) + 1)
        g.add_node(e.target,
                   shape="box",
                   fontsize='9',
                   style='filled',
                   fillcolor=fillcolor)

        if e.polarity == 1:
            arrowhead = 'normal'
        elif e.polarity == 0:
            arrowhead = 'dot'
        elif e.polarity == -1:
            arrowhead = 'inv'

        penwidth = 0.5 + (e.distance * 1.3)

        g.add_edge(e.source,
                   e.target,
                   colorscheme=scheme, color=1 + e.influence,
                   arrowhead=arrowhead,
                   penwidth=penwidth)
    return g
