from django.db import models
import networkx as nx
from django.conf import settings
from django.contrib.auth.models import User


class Phase(models.Model):
    phase = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.phase


class Sector(models.Model):
    sector = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.sector

    class Meta:
        verbose_name_plural = "Economy sectors"


class Power(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name_plural = "Avatar powers"


class Person(models.Model):
    name = models.CharField(max_length=200)
    sector = models.ForeignKey(Sector, null=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    degree = models.IntegerField(default=0)

    avatar_name = models.CharField(max_length=200, blank=True)
    avatar_pic = models.ImageField(blank=True, null=True,
                                   upload_to='avatars/')

    ego = models.BooleanField(default=False)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def mental_model(self, phase):
        g = nx.DiGraph()

        for e in self.mentaledge_set.filter(phase=phase):
            g.add_edge(e.source.name,
                       e.target.name)
        return g

    def compound_mental_model(self, phase):
        g = nx.DiGraph()

        for e in self.mentaledge_set.filter(phase=phase):
            g.add_node(e.source.name, egos=[])

            g.add_node(e.target.name, egos=[])

            g.add_edge(e.source.name,
                       e.target.name)
        return g

    def power_network(self, phase):
        g = nx.Graph()

        for e in self.powers.filter(phase=phase):
            g.add_node(e.source.name,
                       shape="ellipse",
                       width=120,
                       height=120,
                       avatar=e.source.avatar_url())
            g.add_node(e.target.name,
                       shape="octagon",
                       width=90,
                       height=90)

            g.add_edge(e.source.name,
                       e.target.name)
        return g

    def avatar_url(self):
        if self.avatar_pic:
            return u"%s%s" % (settings.MEDIA_URL, self.avatar_pic)
        else:
            return None

    def image_tag(self):
        if self.avatar_pic:
            return u'<img src="/media/%s" width="40px"/>' % self.avatar_pic
        else:
            return u'&nbsp;'

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    
    def __str__(self):
        return u"%s (%s)" % (self.avatar_name, self.name)

    class Meta:
        verbose_name_plural = "People"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def alters(self):
        return [a for a in self.action_set.all()]

    def get_degree(self):
        return sum([a.in_degree for a in self.alters()])

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Actions categories"

    def __str__(self):
        return u"%s" % self.name


class Action(models.Model):
    action = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)

    in_degree = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def update_in_degree(self, phase):
        self.in_degree = self.actor_set.filter(phase=phase).count()

    def __str__(self):
        return u"%s" % self.action


class AgencyEdge(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    distance = models.IntegerField(blank=True, null=True)

    interaction = models.CharField(max_length=20, blank=True, null=True)

    polarity = models.IntegerField(blank=True, null=True)

    people = models.ManyToManyField(Person,
                                    related_name='people',
                                    blank=True)

    phase = models.ForeignKey(Phase, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s->%s" % (self.person, self.action)

    class Meta:
        verbose_name_plural = "Agency edgelist"


class PowerEdge(models.Model):
    person = models.ForeignKey(Person,
                               related_name='powers',
                               on_delete=models.CASCADE)
    power = models.ForeignKey(Power,
                              related_name='wielded_by',
                              on_delete=models.CASCADE)

    phase = models.ForeignKey(Phase, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s -> %s" % (self.person, self.power)

    class Meta:
        verbose_name_plural = "Avatar power edgelist"


class Variable(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name_plural = "Cognitive map variables"


class MentalEdge(models.Model):
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)
    source = models.ForeignKey(Variable,
                               related_name='leads_to',
                               null=True,
                               on_delete=models.CASCADE)
    target = models.ForeignKey(Variable,
                               related_name='caused_by',
                               null=True,
                               on_delete=models.CASCADE)

    phase = models.ForeignKey(Phase, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"(%s)->(%s)" % (self.source, self.target)

    class Meta:
        verbose_name_plural = "Cognitive map edgelist"
