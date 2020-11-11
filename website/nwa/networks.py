import networkx as nx
import pygraphviz as pgv
from collections import OrderedDict
import pyexcel as pe
from io import BytesIO



def mental_model(queryset):
    """
    return a networkx DiGraph object
    from a Django Orm Queryset of mental edges
    """
    g = nx.DiGraph()
    for e in queryset:
        w = g.get_edge_data(e.source.name,
                            e.target.name,
                            default={'w': 0})['w']
        w += 1
        g.add_edge(e.source.name,
                   e.target.name,
                   w=w)
    return g


def power_network(queryset):
    g = nx.Graph()
    for e in queryset:
        g.add_node(e.person.name, type='person')
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


def agency_ego_alter(queryset):
    g = nx.DiGraph()
    for e in queryset:
        g.add_node(str(e.person), type='person',
                   sector=str(e.person.sector),
                   ego=e.person.ego)
        for alter in e.people.all():
            g.add_node(str(alter), type='alter',
                       sector=str(alter.sector),
                       ego=False)
            action = g.get_edge_data(e.person, str(alter), default={'action': ''})['action']
            action += ", " + str(e.action)

            if action.startswith(', '):
                action = action[2:]

            g.add_edge(e.person,
                       str(alter),
                       action=action)
    return g


def agency_ego_alter_action(queryset):
    g = nx.DiGraph()
    for e in queryset:
        g.add_node(str(e.person), type='person',
                   sector=str(e.person.sector),
                   ego=e.person.ego)
        g.add_node(str(e.action), type='action')

        for alter in e.people.all():
            g.add_node(str(alter), type='alter',
                       sector=str(alter.sector),
                       ego=False)

            g.add_edge(str(e.person),
                       str(alter))

            g.add_edge(str(alter),
                       str(e.action))

    return g


def agency_ego_alter_action_agraph(queryset):
    g = pgv.AGraph(directed=True, overlap=False,
                   outputmode='edgesfirst')
    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   shape='box',
                   style='filled', fillcolor='white')
        g.add_node(str(e.action),
                   colorscheme='set13', color=5,
                   shape='egg')

        for alter in e.people.all():
            g.add_node(str(alter),
                       colorscheme='set13', color=3,
                       shape="box",
                       fontsize='9',
                       style='filled', fillcolor='white')

            g.add_edge(e.person,
                       str(alter),
                       colorscheme='set13',
                       color=2)

            g.add_edge(str(alter),
                       str(e.action),
                       colorscheme='set13',
                       color=3)


    return g



def agency_ego_alter_agraph(queryset):
    g = pgv.AGraph(directed=True, overlap='scale')
    for e in queryset:
        g.add_node(e.person,
                   colorscheme='set13', color=2,
                   shape='box')
        for alter in e.people.all():
            g.add_node(str(alter),
                       colorscheme='set13', color=3,
                       shape="box",
                       fontsize='9',
                       style='filled', fillcolor='white')

            g.add_edge(e.person,
                       str(alter))

    return g



def agency_alter_action(queryset):
    g = nx.DiGraph()
    for e in queryset:
        g.add_node(str(e.action), type='action')
        for alter in e.people.all():
            g.add_node(str(alter), type='person',
                       sector=str(alter.sector))

            w = g.get_edge_data(str(alter),
                                str(e.action),
                                default={'w': 0})['w']
            w += 1
            g.add_edge(str(alter),
                       str(e.action),
                       w=w)
    return g


def agency_alter_action_agraph(queryset):
    g = pgv.AGraph(directed=True, overlap='scale')
    h = agency_alter_action(queryset)
    for e in h.edges:
        for node in e:
            if h.node[node]['type'] == 'person':
                g.add_node(node,
                           colorscheme='set13', color=2,
                           shape="box",
                           fontsize='9',
                           style='filled', fillcolor='white')
            else:
                g.add_node(node,
                           colorscheme='set13', color=3,
                           shape="box",
                           fontsize='9',
                           style='filled', fillcolor='white')

        g.add_edge(e[0],
                   e[1],
                   penwidth=h.get_edge_data(*e)['w'])

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
                   people=", ".join([str(p)
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



def network_analisis_report(g):

    try:
        diameter = nx.diameter(g)
    except Exception as e:
        diameter = str(e)
    try:
        aspl = nx.average_shortest_path_length(g)
    except Exception as e:
        aspl = str(e)

    report = [
        ['number of nodes',
         'number of edges',
         'diameter',
         'average shortest path length',
         'average clustering'],
        [len(g.nodes),
         len(g.edges),
         diameter,
         aspl,
         nx.average_clustering(g)]]

    io = BytesIO()
    sheet = pe.Sheet(report, name="network analisis")
    sheet.save_to_memory("ods", io)
    return io
