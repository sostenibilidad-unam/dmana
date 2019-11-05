from .models import Sector, Category
import networkx as nx
import pyveplot
from pyveplot import Hiveplot, Node, Axis
import random
import uuid
from os import path
import tempfile
import svgwrite

# action colors
ac = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
      '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6',
      '#6a3d9a', '#ffff99', '#b15928',
      '#8dd3c7', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
      '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5',
      '#ffed6f']

# sector colors
sc = ['#8dd3c7', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
      '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5',
      '#ffed6f', '#8dd3c7', '#bebada', '#fb8072', '#80b1d3', '#fdb462',
      '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5',]

ego_color = '#b2df8a'


class AgencyHiveplot:

    def __init__(self, queryset):

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
        if self.g.degree(v) > 2:
            node.add_label("%s k=%s" % (v, self.g.degree(v)),
                           angle=axis.angle + 90 * orientation,
                           scale=scale)

    def add_ego_axis(self):
        axis = Axis(start=40, angle=90,
                    stroke=ego_color, stroke_width=1.1)
        for v in self.k:
            v = v[0]
            if ('ego' in self.g.node[v] and self.g.node[v]['ego'] is True):
                self.add_node_to_axis(v, axis, 'blue')  # sector colors
        self.h.axes.append(axis)

    def add_sector_axes(self):
        end = 40
        for sector in self.sectors:
            sector_color = sc[self.sectors.index(sector)]
            axis = Axis(start=end, angle=90 + 120,
                        stroke=sector_color, stroke_width=1.1)

            for v in self.k:
                v = v[0]
                if ('ego' in self.g.node[v] and self.g.node[v]['ego'] is False
                        and self.g.node[v]['sector'] == str(sector)):
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
            cat_color = ac[self.cats.index(cat)]
            axis = Axis(start=end, angle=90 + 120 + 120,
                        stroke=cat_color, stroke_width=1.1)
            for v in self.k:
                v = v[0]
                if (self.g.node[v]['type'] == 'action'
                    and
                   self.g.node[v]['category'] == str(cat)):

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
            cat_color = ac[self.cats.index(axis.name)]
            self.h.connect_axes(self.h.axes[n],
                                self.h.axes[0],
                                self.g.edges,
                                stroke_width=0.5,
                                stroke=cat_color)

        for axis in self.people:
            n = self.h.axes.index(axis)
            sector_color = sc[self.sectors.index(axis.name)]
            self.h.connect_axes(self.h.axes[0],
                                self.h.axes[n],
                                self.g.edges,
                                stroke_width=0.5,
                                stroke=sector_color)

        for p in self.people:
            n = self.h.axes.index(p)
            sector_color = sc[self.sectors.index(p.name)]
            for a in self.actions:
                m = self.h.axes.index(a)
                cat_color = ac[self.cats.index(a.name)]
                self.h.connect_axes(self.h.axes[n],
                                    self.h.axes[m],
                                    self.g.edges,
                                    stroke_width=0.5,
                                    stroke=sector_color)

    def save(self, filename):
        self.h.save(filename)
        tmp_file = tempfile.SpooledTemporaryFile()
        pyveplot.dwg = svgwrite.Drawing(tmp_file)
