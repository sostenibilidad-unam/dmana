from .models import Person, AgencyEdge, Action, Sector, Category
import networkx as nx
from pprint import pprint
from pyveplot import Hiveplot, Node, Axis
import operator
from .scale import Scale
import random


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
    sorted_in_degree = sorted(in_degree.items(), key=operator.itemgetter(1))

    # sorted ego list
    egos_out_deg = {v: g.out_degree(v)
                    for v in g.nodes
                    if g.nodes[v]['type']=='person' and g.nodes[v]['ego'] is True}
    sorted_egos_out_deg = sorted(egos_out_deg.items(), key=operator.itemgetter(1))
    # sort sectors by length
    sec_len = {sector: len(sectors[sector])
               for sector in sectors}
    sorted_sec_len = sorted(sec_len.items(), key=operator.itemgetter(1))


    # our hiveplot object
    h = Hiveplot('agency_hive.svg')
    offcenter = 10
    spacer = 10
    ego_spacer = 1
    node_size = 10.0
    angle = 0

    # scale max degree to node_size set above
    deg_scale = Scale(domain=[1.0, max(in_degree.values())],
                      range=[1.0, node_size])

    ego_scale = Scale(domain=[1.0, max(egos_out_deg.values())],
                      range=[1.0, node_size])

    # create ego axis
    ego_len = sum([(degree * 2) + spacer
                   for ego, degree in sorted_egos_out_deg])
    ego_axis = Axis(start=offcenter, end=ego_len,
                    angle=angle - 120, stroke="firebrick")

    i = 0.5 * sorted_egos_out_deg[0][1]

    for ego, degree in sorted_egos_out_deg:
        i += degree
        
        node = Node(ego)
        ego_axis.add_node(node,
                          i / ego_len)
        i += degree + spacer
        
        node.dwg = node.dwg.circle(
            center=(node.x, node.y),
            r=g.out_degree(ego),
            fill='orange',
            fill_opacity=0.5,
            stroke=random.choice(['red',
                                  'crimson',
                                  'coral',
                                  'purple']),
            stroke_width=0.3)



    # create alter axes
    alter_axes = {}
    alter_axes_scales = {}
    start = offcenter
    end = 0
    for sector, sec_len in sorted_sec_len:
        if sector is None:
            continue
        axis_len = sec_len * node_size

        end = start + axis_len

        alter_axes[sector] = Axis(start=start, end=end,
                                  angle=angle, stroke="grey")

        alter_axes_scales[sector] = Scale(
            domain=[start, end],
            range=[0, 1])

        start = end + spacer


    # create action axis
    action_axis = Axis(start=offcenter, end=end,
                       angle=angle + 120, stroke="darkgreen")

    # populate action axis
    for cat in action_category:
        i = 0.5
        for action, degree in sorted_in_degree:
            if type(action) is not Action:
                continue

            node = Node(action)
            action_axis.add_node(node,
                                 i / len(action_category[cat]))
            i += 1.0
            node.dwg = node.dwg.circle(
                center=(node.x, node.y),
                r=0.5 * deg_scale.linear(in_degree[action]),
                fill='navy',
                fill_opacity=0.5,
                stroke=random.choice(['grey',
                                      'green',
                                      'blue',
                                      'navy']),
                stroke_width=0.3)

    h.axes.append(ego_axis)
    h.axes += list(alter_axes.values())
    h.axes.append(action_axis)


    h.save()
    return g