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
    categories = {}

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

        g.add_edge(e.person,
                   e.action,
                   people=", ".join([str(p)
                                    for p in e.people.all()]))
        
        # populate action categories dict
        if e.action.category in categories:
            categories[e.action.category].add(e.action)
        else:
            categories[e.action.category] = set([e.action, ])

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

    # sort sectors by length
    sec_len = {sector: len(sectors[sector])
               for sector in sectors}
    sorted_sec_len = sorted(sec_len.items(), key=operator.itemgetter(1))

    # our hiveplot object
    h = Hiveplot( 'agency_hive.svg')
    offcenter = 10
    spacer = 10
    ego_node_size = 10
    alter_node_size = 5
    angle = 0

    # create alter axes
    alter_axes = {}
    alter_axes_scales = {}
    start = offcenter
    end = 0
    for sector, sec_len in sorted_sec_len:
        if sector is None:
            continue
        axis_len = sec_len * alter_node_size
        
        end = start + axis_len
        
        alter_axes[sector] = Axis(start=start, end=end,
                                  angle=angle, stroke="grey")

        alter_axes_scales[sector] = Scale(
            domain=[start, end],
            range=[0, 1])
        
        
        start = end + spacer        
    
    
    # ego_count = Alter.objects.filter(name__contains='TL0').count()
    # ego_scale= Scale(domain=[Alter.objects.order_by('degree')[0].degree,
    #                          Alter.objects.order_by('-degree')[0].degree],
    #                  range=[5, 30])
    h.axes = list(alter_axes.values())

    
    ego_axis = Axis(start=offcenter, end=end,
                    angle=angle - 120, stroke="firebrick")

    h.axes.append(ego_axis)

    # create action axis
    action_axis = Axis(start=offcenter, end=end,
                       angle=angle + 120, stroke="darkgreen")

    pprint(in_degree)
    # populate action axis
    for cat in categories:
        i = 0.0
        for action in categories[cat]:
            node = Node(action)
            action_axis.add_node(node,
                                 i / len(categories[cat]))
            i += 1
            node.dwg = node.dwg.circle(center = (node.x, node.y),
                                       r      = in_degree[action],
                                       fill   = 'orange',
                                       fill_opacity = 0.5,
                                       stroke = random.choice(['red','crimson','coral','purple']),
                                       stroke_width = 0.3)
        
    h.axes.append(action_axis)

    
    h.save()
    return g
