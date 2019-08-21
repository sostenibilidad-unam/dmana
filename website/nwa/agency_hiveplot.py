from .models import Person, AgencyEdge, Action, Sector, Category
import networkx as nx
from pprint import pprint
from pyveplot import Hiveplot, Node, Axis
import operator


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

        g.add_edge(e.person,
                   e.action,
                   people=", ".join([str(p)
                                    for p in e.people.all()]))
        
        # populate categories dict
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
    start = offcenter
    end = 0
    for sector, sec_len in sorted_sec_len:
        if sector is None:
            continue
        axis_len = sec_len * alter_node_size
        
        end = start + axis_len
        
        alter_axes[sector] = Axis(start=start, end=end,
                                  angle=angle, stroke="grey")

        start = end + spacer
        
        

    h.axes = alter_axes.values()

    h.save()
    return g
