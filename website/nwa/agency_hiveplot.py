from .models import Person, AgencyEdge, Action, Sector, Category
import networkx as nx
from pprint import pprint
from pyveplot import Hiveplot, Node, Axis
import operator
from .scale import Scale
import random
import svgwrite

##########################
# create hiveplot object #
##########################
h = Hiveplot('agency_hive.svg')
offcenter = 10
spacer = 4
angle = 0


def add_nodes_to_axis(axis, axis_len, spacer, nodes):
    i = 0.5 * nodes[0][1]
    for v, k in nodes:
        i += k
        node = Node(v)
        axis.add_node(node,
                      i / axis_len)
        i += k + spacer
        gr = svgwrite.container.Group()
        gr.add(h.dwg.circle(
            center=(node.x, node.y),
            r=k,
            fill='navy',
            fill_opacity=0.5,
            stroke='grey',
            stroke_width=0.3))
        node.dwg.add(gr)


def agency_hiveplot(queryset):
    g = nx.DiGraph()

    sectors = {}
    action_category = {}

    for e in queryset:
        # create NX graph
        g.add_node(e.person, type='person',
                   sector=str(e.person.sector),
                   ego=e.person.ego)

        g.add_node(e.action, type='action',
                   category=str(e.action.category))

        for p in e.people.all():
            g.add_node(p, type='person',
                       sector=str(p.sector),
                       ego=p.ego)
            # ego to alter
            g.add_edge(e.person,
                       p)
            # alter to action
            g.add_edge(p,
                       e.action)
        # ego to action
        g.add_edge(e.person,
                   e.action,
                   people=", ".join([str(p)
                                    for p in e.people.all()]))

        # populate action categories dict
        if e.action.category in action_category:
            action_category[e.action.category].add(e.action)
        else:
            action_category[e.action.category] = set([e.action, ])

        # populate sectors dict from people in edge
        for p in e.people.all():

            if p.sector in sectors:
                sectors[p.sector].add(p)
            else:
                sectors[p.sector] = set([p, ])

        # add egos to sectors dict
        if e.person.sector in sectors:
            sectors[e.person.sector].add(e.person)
        else:
            sectors[e.person.sector] = set([e.person.sector, ])

    # create in-degrees dict
    in_degree = {v: g.in_degree(v) for v in g.nodes}

    # sorted ego list
    egos_out_deg = {v: g.out_degree(v)
                    for v in g.nodes
                    if g.nodes[v]['type'] == 'person'
                    and g.nodes[v]['ego'] is True}
    sorted_egos_out_deg = sorted(egos_out_deg.items(),
                                 key=operator.itemgetter(1))
    # sort categories by length
    action_cats_len = {cat: len(action_category[cat])
                       for cat in action_category}
    sorted_action_cats = sorted(action_cats_len.items(),
                                key=operator.itemgetter(1))

    # sort sectors by length
    sec_len = {sector: len(sectors[sector])
               for sector in sectors}
    sorted_sec_len = sorted(sec_len.items(), key=operator.itemgetter(1))


    # create ego axis
    ego_len = sum([(degree * 2) + spacer
                   for ego, degree in sorted_egos_out_deg])
    ego_axis = Axis(start=offcenter, end=ego_len,
                    angle=angle - 120, stroke="firebrick", stroke_width=1.4)

    i = 0.5 * sorted_egos_out_deg[0][1]

    for ego, degree in sorted_egos_out_deg:
        i += degree

        node = Node(ego)
        ego_axis.add_node(node,
                          i / ego_len)
        i += degree + spacer

        gr = svgwrite.container.Group(style='font-size:%s' % (degree * 0.5))
        gr.add(
            h.dwg.circle(
            center=(node.x, node.y),
            r=g.out_degree(ego),
            fill='gold',
            fill_opacity=1.0,
            stroke='firebrick',
            stroke_width=1.4))

        gr.add(node.dwg.text(ego.name,
                             insert=(node.x - degree * 0.7,
                                     node.y)))
        node.dwg.add(gr)


    # create alter axes
    alter_axes = {}
    start = offcenter
    end = 0
    sorted_alter_nodes = []
    for sector, sec_len in sorted_sec_len:

        nodes = {person: in_degree[person] for person in sectors[sector]
                 if type(person) is Person and person.ego is False}
        sorted_nodes = sorted(nodes.items(), key=operator.itemgetter(1))

        if not sorted_nodes:
            continue

        sorted_alter_nodes += [node for node, deg in sorted_nodes]

        axis_len = sum([(degree * 2) + spacer
                        for person, degree in sorted_nodes])

        end = start + axis_len

        alter_axis = Axis(start=start, end=end,
                          angle=angle, stroke="grey")

        add_nodes_to_axis(
            axis=alter_axis,
            axis_len=axis_len,
            spacer=spacer,
            nodes=sorted_nodes)

        alter_axes[sector] = alter_axis

        start = end + (spacer * 4)

    # create action axes
    action_axes = {}
    start = offcenter
    end = 0
    sorted_action_nodes = []
    for category, cat_len in sorted_action_cats:
        nodes = {action: in_degree[action]
                 for action in action_category[category]}
        sorted_nodes = sorted(nodes.items(), key=operator.itemgetter(1))
        if not sorted_nodes:
            continue

        axis_len = sum([(degree * 2) + spacer
                        for action, degree in sorted_nodes])
        end = start + axis_len

        action_axes[category] = Axis(start=start, end=end,
                                     angle=angle + 120, stroke="darkgreen")

        sorted_action_nodes += [node for node, degree in sorted_nodes]

        # populate action axis with nodes
        add_nodes_to_axis(
            nodes=sorted_nodes,
            axis=action_axes[category],
            axis_len=axis_len,
            spacer=spacer)

        start = end + (spacer * 4)

    # place axes in hiveplot
    h.axes.append(ego_axis)
    h.axes += list(alter_axes.values())
    h.axes += list(action_axes.values())

    #################
    # connect edges #
    #################
    i = 0
    j = 0
    for u in g.edges:
        (s, t) = u
        if (
                type(s) is Person and s.ego is True
                and
                type(t) is Person and t.ego is False):
            for sector, sec_len in sorted_sec_len:
                if sector in alter_axes and t in alter_axes[sector].nodes:
                    h.connect(ego_axis, s, egos_out_deg[s] ** 1.5,
                              alter_axes[sector], t, -40,
                              stroke='black',
                              stroke_width=1.666,
                              stroke_opacity=0.33)

        if (
                type(s) is Person and s.ego is True
                and
                type(t) is Action):
            for category, cat_len in sorted_action_cats:
                if t in action_axes[category].nodes:
                    i += 1
                    h.connect(
                        action_axes[category], t, sorted_action_nodes.index(t) ** 1.4,
                        ego_axis, s, egos_out_deg[s] ** 1.25,
                        stroke='black',
                        stroke_width=1.666,
                        stroke_opacity=0.33)

        if (
                type(s) is Person and s.ego is False
                and
                type(t) is Action):
            for sector, sec_len in sorted_sec_len:
                if sector in alter_axes and s in alter_axes[sector].nodes:
                    for category, cat_len in sorted_action_cats:
                        if t in action_axes[category].nodes:
                            j += 1
                            h.connect(alter_axes[sector], s, sorted_alter_nodes.index(s) * 1.25,
                                      action_axes[category], t, sorted_action_nodes.index(t) ** 1.4,
                                      stroke='navy',
                                      stroke_width=1.666,
                                      stroke_opacity=0.33)

    h.save()
    return g
