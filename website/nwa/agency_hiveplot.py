from .models import Person, AgencyEdge, Action, Sector, Category
import networkx as nx
from pprint import pprint
from pyveplot import Hiveplot, Node, Axis
import operator
from .scale import Scale
import random
import svgwrite
import uuid
from django.conf import settings
from os import path
from django.http import HttpResponseRedirect

c = ['#e41a1c', '#377eb8', '#4daf4a',
     '#984ea3', '#ff7f00', '#ffff33',
     '#a65628', '#f781bf', '#999999',]



class AgencyHiveplot:

    def __init__(self, queryset):

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
        self.g = g

        self.h = Hiveplot('tmp')


        
    def add_node_to_axis(self, v, axis, circle_color, fill_opacity=0.7):
        # create node object
        node = Node(radius=self.g.degree(v),
                    label="node %s k=%s" % (v, self.g.degree(v)))
        # add it to axis
        axis.add_node(v, node)
        # once it has x, y coordinates, add a circle
        node.add_circle(fill=circle_color,
                        stroke=circle_color,
                        stroke_width=0.1,
                        fill_opacity=fill_opacity)
        if axis.angle < 180:
            orientation = -1
            scale = 0.6
        else:
            orientation = 1
            scale = 0.35
        # also add a label
        node.add_label("%s k=%s" % (v, self.g.degree(v)),
                       angle=axis.angle + 90 * orientation,
                       scale=scale)


    def add_ego_axis(self):
        axis = Axis(start=20, angle=90,
                    stroke=random.choice(c), stroke_width=1.1)
        for v in self.g.nodes:  # sort 'em
            if ('ego' in self.g.node[v] and self.g.node[v]['ego'] is True):
                self.add_node_to_axis(v, axis, 'blue')  # sector colors
        self.h.axes.append(axis)

        
    def add_sector_axes(self):
        for sector in Sector.objects.all():
            axis = Axis(start=20, angle=90 + 120,
                        stroke=random.choice(c), stroke_width=1.1)
            for v in self.g.nodes:  # sort 'em
                if ('ego' in self.g.node[v] and self.g.node[v]['ego'] == False
                        and self.g.node[v]['sector'] == str(sector)):
                    self.add_node_to_axis(v, axis, circle_color='purple')  # sector colors
            self.h.axes.append(axis)


    def add_actioncat_axes(self):
        for cat in Category.objects.all():
            axis = Axis(start=20, angle=90 + 120 + 120,
                        stroke=random.choice(c), stroke_width=1.1)
            for v in self.g.nodes:  # sort 'em
                print(str(cat))
                if (self.g.node[v]['type'] == 'action' and self.g.node[v]['category'] == str(cat)):
                    self.add_node_to_axis(v, axis, circle_color='firebrick')  # sector colors
            self.h.axes.append(axis)


    def save(self):
        export_id = uuid.uuid4()
        print("aguas")
        self.filename = '%s_hiveplot.svg' % export_id
        self.h.save(path.join(settings.EXPORT,
                              self.filename))

            


