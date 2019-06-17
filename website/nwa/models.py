from django.db import models
import networkx as nx
from django.conf import settings
from django.contrib.auth.models import User


class Project(models.Model):
    project = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.project


class Sector(models.Model):
    sector = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.sector

    class Meta:
        verbose_name_plural = "Economy sectors"
        ordering = ['sector']

class Organization(models.Model):
    organization = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.organization

    class Meta:
        verbose_name_plural = "Organizations"
        ordering = ['organization']

class Power(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name_plural = "Avatar powers"
        ordering = ['name', ]


class Person(models.Model):
    name = models.CharField(max_length=200, unique=True)
    sector = models.ForeignKey(Sector,
                               null=True, blank=True,
                               on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization,
                                     null=True, blank=True,
                                     on_delete=models.SET_NULL)

    description = models.TextField(blank=True)

    avatar_name = models.CharField(max_length=200, blank=True)
    avatar_pic = models.ImageField(blank=True, null=True,
                                   upload_to='avatars/')

    ego = models.BooleanField(default=False)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

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
        name = u"%s" % self.name

        if self.avatar_name:
            name += u' "%s"' % self.avatar_name

        if self.organization and self.organization.organization != self.name:
            name += u" (%s)" % self.organization

        return name

    class Meta:
        verbose_name_plural = "People"
        ordering = ['name']


class Category(models.Model):
    name = models.CharField(max_length=100)

    def alters(self):
        return [a for a in self.action_set.all()]

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Actions categories"
        ordering = ["name", ]

    def __str__(self):
        return u"%s" % self.name


class Action(models.Model):
    action = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.action

    class Meta:
        ordering = ['action']


class SocialEdge(models.Model):
    source = models.ForeignKey(Person,
                               related_name='outbound',
                               on_delete=models.CASCADE)
    target = models.ForeignKey(Person,
                               related_name='inbound',
                               on_delete=models.CASCADE)

    influence = models.IntegerField(blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    interaction = models.CharField(max_length=20, blank=True, null=True)
    polarity = models.IntegerField(blank=True, null=True)

    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Social Edgelist"
        unique_together = (('source', 'target'),)

    def __str__(self):
        return u"%s -> %s" % (self.source, self.target)


class AgencyEdge(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    people = models.ManyToManyField(Person,
                                    related_name='agency_actor_in',
                                    blank=True)

    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s->%s" % (self.person, self.action)

    class Meta:
        verbose_name_plural = "Agency Edgelist"
        unique_together = (('person', 'action'),)



class PowerEdge(models.Model):
    person = models.ForeignKey(Person,
                               related_name='powers',
                               on_delete=models.CASCADE)
    power = models.ForeignKey(Power,
                              related_name='wielded_by',
                              on_delete=models.CASCADE)

    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s -> %s" % (self.person, self.power)

    class Meta:
        verbose_name_plural = "Avatar power Edgelist"


class Variable(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name_plural = "Cognitive map variables"
        ordering = ["name", ]


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

    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return u"(%s)->(%s)" % (self.source, self.target)

    class Meta:
        verbose_name_plural = "Cognitive map Edgelist"
