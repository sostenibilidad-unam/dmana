from .models import Person, AgencyEdge, Action, Sector, Category
import networkx as nx
from pprint import pprint


def agency_hiveplot(queryset):
    g = nx.DiGraph()

    sectors = {}
    categories = {}

    for e in queryset:

        g.add_node(e.person, type='person',
                   sector=str(e.person.sector),
                   ego=e.person.ego)

        # populate categories dict
        if e.action.category in categories:
            categories[e.action.category].add(e.action)
        else:
            categories[e.action.category] = set([e.action, ])

        g.add_node(e.action, type='action',
                   category=str(e.action.category))

        # populate sectors dict
        for p in e.people.all():
            if p.sector in sectors:
                sectors[p.sector].add(p)
            else:
                sectors[p.sector] = set([p, ])

        g.add_edge(e.person,
                   e.action,
                   people=", ".join([str(p)
                                    for p in e.people.all()]))

    pprint(categories)
    return g
