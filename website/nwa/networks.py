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
    g = pgv.AGraph(overlap='scale', splines="spline", outputmode="edgesfirst")
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


def agency_agraph_orgs2cats(queryset):
    g = pgv.AGraph(directed=True,
                   overlap='false',
                   splines='spline',
                   outputmode='edgesfirst')
    max_people = max([e.people.count()
                      for e in queryset]) + 1
    edgescheme = "purd%s" % max_people
    for e in queryset:
        g.add_node(e.person.org_or_self(),
                   colorscheme='set13', color=2,
                   shape='box',
                   style='filled', fillcolor='white')
        g.add_node(e.action.category_or_action(),
                   colorscheme='set13', color=3,
                   shape="egg",
                   fontsize='9',
                   style='filled', fillcolor='white')
        g.add_edge(e.person.org_or_self(),
                   e.action.category_or_action(),
                   penwidth=e.people.count(),
                   colorscheme=edgescheme,
                   color=e.people.count() + 1)
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
    g = pgv.AGraph(directed=True,
                   spline='splines',
                   overlap='false',
                   outputorder='edgesfirst')
    max_distance = max([e.distance for e in queryset]) + 1
    edgescheme = "gnbu%s" % max_distance

    sectors = [e.source.sector for e in queryset]
    sectors += [e.target.sector for e in queryset]
    sectors = list(set(sectors))

    if len(sectors) <= 12:
        nodescheme = "set3%s" % len(sectors)
    else:
        nodescheme = "X11"

    for e in queryset:
        print(sectors.index(e.source.sector) + 1)
        fillcolor = "/%s/%s" % (nodescheme,
                                sectors.index(e.source.sector) + 1)
        g.add_node(e.source,
                   shape='box',
                   fontsize='9',
                   style='filled',
                   fillcolor=fillcolor)
        fillcolor = "/%s/%s" % (nodescheme,
                                sectors.index(e.target.sector) + 1)
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

        penwidth = 0.5 + (e.influence * 1.3)

        style = "dashed" if e.interaction == 'E' else "solid"

        g.add_edge(e.source,
                   e.target,
                   style=style,
                   colorscheme=edgescheme,
                   color=max_distance - e.distance,
                   arrowhead=arrowhead,
                   penwidth=penwidth)
    return g
