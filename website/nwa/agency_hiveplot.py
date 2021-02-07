from .models import Sector, Category
import networkx as nx
import pyveplot
from pyveplot import Hiveplot, Node, Axis
import random
import uuid
from os import path
import tempfile
import svgwrite
from SecretColors.palette import Palette



ego_color = '#b2df8a'


class AgencyHiveplot:

    def __init__(self, queryset, label_threshold=2):

        self.label_threshold = label_threshold
        
        g = nx.DiGraph()

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
        self.h = Hiveplot()

        # sort nodes by degree
        self.k = list(nx.degree(g))
        self.k.sort(key=lambda tup: tup[1])

        self.actions = []
        self.people = []

        self.sectors = list(Sector.objects.all())
        self.cats = list(Category.objects.all())


        # create color palettes
        p = Palette("clarity")

        self.ac = p.random(no_of_colors=len(self.cats),
                           shade=45)

        # sector colors
        self.sc = p.random(no_of_colors=len(self.sectors),
                           shade=50)

        
        
    def add_node_to_axis(self, v, axis, circle_color, fill_opacity=0.7):
        # create node object
        node = Node(radius=self.g.degree(v),
                    label="")
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
        if self.g.degree(v) > self.label_threshold:
            node.add_label("%s k=%s" % (v, self.g.degree(v)),
                           angle=axis.angle + 90 * orientation,
                           scale=scale)

    def add_ego_axis(self):
        axis = Axis(start=40, angle=90,
                    stroke=ego_color, stroke_width=1.1)
        for v in self.k:
            v = v[0]
            if ('ego' in self.g.nodes[v] and self.g.nodes[v]['ego'] is True):
                self.add_node_to_axis(v, axis, 'blue')  # sector colors
        self.h.axes.append(axis)

    def add_sector_axes(self):
        end = 40
        for sector in self.sectors:
            sector_color = self.sc[self.sectors.index(sector)]
            axis = Axis(start=end, angle=90 + 120,
                        stroke=sector_color, stroke_width=1.1)

            for v in self.k:
                v = v[0]
                if ('ego' in self.g.nodes[v] and self.g.nodes[v]['ego'] is False
                        and self.g.nodes[v]['sector'] == str(sector)):
                    self.add_node_to_axis(v, axis,
                                          circle_color=sector_color)

            axis.auto_place_nodes()
            if axis.length() > 0:
                end = axis.end + 30
            axis.name = sector
            self.h.axes.append(axis)
            self.people.append(axis)

    def add_actioncat_axes(self):
        end = 40
        for cat in self.cats:
            cat_color = self.ac[self.cats.index(cat)]
            axis = Axis(start=end, angle=90 + 120 + 120,
                        stroke=cat_color, stroke_width=1.1)
            for v in self.k:
                v = v[0]
                if (self.g.nodes[v]['type'] == 'action'
                    and
                   self.g.nodes[v]['category'] == str(cat)):

                    self.add_node_to_axis(v, axis,
                                          circle_color=cat_color)
            axis.auto_place_nodes()
            if axis.length() > 0:
                end = axis.end + 30
            axis.name = cat
            self.h.axes.append(axis)
            self.actions.append(axis)

    def connect_axes(self):
        for axis in self.actions:
            n = self.h.axes.index(axis)
            cat_color = self.ac[self.cats.index(axis.name)]
            self.h.connect_axes(self.h.axes[n],
                                self.h.axes[0],
                                self.g.edges,
                                stroke_width=0.5,
                                stroke=cat_color)

        for axis in self.people:
            n = self.h.axes.index(axis)
            sector_color = self.sc[self.sectors.index(axis.name)]
            self.h.connect_axes(self.h.axes[0],
                                self.h.axes[n],
                                self.g.edges,
                                stroke_width=0.5,
                                stroke=sector_color)

        for p in self.people:
            n = self.h.axes.index(p)
            sector_color = self.sc[self.sectors.index(p.name)]
            for a in self.actions:
                m = self.h.axes.index(a)
                cat_color = self.ac[self.cats.index(a.name)]
                self.h.connect_axes(self.h.axes[n],
                                    self.h.axes[m],
                                    self.g.edges,
                                    stroke_width=0.5,
                                    stroke=sector_color)

    def save(self, filename):
        self.h.save(filename)
        tmp_file = tempfile.SpooledTemporaryFile()
        pyveplot.dwg = svgwrite.Drawing(tmp_file)
