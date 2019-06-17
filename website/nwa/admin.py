# -*- coding: utf-8 -*-
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.template.loader import render_to_string
from django.contrib import admin
from django.http import HttpResponse
from .networks import mental_model, power_network, power_agraph, \
    agency_network, agency_agraph
import networkx as nx
import pygraphviz as pgv
import tempfile

from .models import Person, AgencyEdge, Action, Project, \
    Sector, Variable, MentalEdge, Category, \
    Power, PowerEdge, Organization, SocialEdge


class JustMine(object):
    exclude = ('author', )

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser is True:
                return True
            if obj.author == request.user:
                return True
        return False

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if request.user.is_superuser is True:
                return True
            if obj.author == request.user:
                return True
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['queryset'] = db_field.related_model.objects.filter(
            author=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        kwargs['queryset'] = db_field.related_model.objects.filter(
            author=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.author = request.user
            instance.save()
        formset.save_m2m()


class AgencyEdgeInline(JustMine, admin.TabularInline):
    model = AgencyEdge
    fk_name = 'person'
    extra = 1
    classes = ('grp-collapse grp-closed',)
    autocomplete_fields = ['person', 'action', 'people']


class SocialEdgelistInline(JustMine, admin.TabularInline):
    model = SocialEdge
    fk_name = 'source'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['source', 'target']


class PowerEdgeInline(JustMine, admin.TabularInline):
    model = PowerEdge
    fk_name = 'person'
    extra = 1
    classes = ('grp-collapse grp-closed',)
    autocomplete_fields = ['person', 'power', ]


class MentalEdgeInline(JustMine, admin.TabularInline):
    model = MentalEdge
    fk_name = 'person'
    extra = 1
    classes = ('grp-collapse grp-closed',)
    autocomplete_fields = ['source', 'target', ]


@admin.register(Person)
class PersonAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name', 'avatar_name', 'organization__organization']
    list_display = ['name', 'avatar_name', 'organization', 'sector', 'ego', ]

    list_filter = (
        ('sector', admin.RelatedOnlyFieldListFilter), 'ego')

    inlines = [AgencyEdgeInline,
               SocialEdgelistInline,
               PowerEdgeInline,
               MentalEdgeInline]

    fieldsets = (
        ('', {
            'fields': ('name',
                       'sector',
                       'organization',
                       'description',
                       'avatar_name',
                       'avatar_pic',
                       'ego', ),
        }),
    )


@admin.register(Sector)
class SectorAdmin(JustMine, admin.ModelAdmin):

    list_display = ['sector']

    def get_queryset(self, request):
        qs = super(SectorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)


class PersonAdminInline(JustMine, admin.TabularInline):
    model = Person
    fk_name = 'organization'
    extra = 1
    classes = ('grp-collapse grp-open',)


@admin.register(Organization)
class OrganizationAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['organization', ]
    list_display = ['organization']
    inlines = [PersonAdminInline, ]

    def get_queryset(self, request):
        qs = super(OrganizationAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)


@admin.register(SocialEdge)
class SocialEdgelistAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['source__name', 'source__name']
    list_display = ['source', 'target', 'project']

    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter), )

    autocomplete_fields = ['source', 'target', ]

    # actions = [
    #            'download_as_graphml',
    #            'download_as_pdf',
    #            'download_as_dot', ]


    # def download_as_graphml(self, request, queryset):
    #     response = HttpResponse(
    #         "\n".join([l
    #                    for l in
    #                    nx.readwrite.graphml.generate_graphml(
    #                        power_network(queryset))]),
    #         content_type="application/xml")
    #     response[
    #         'Content-Disposition'] = 'attachment; filename="power_network.graphml"'
    #     return response
    # download_as_graphml.\
    #     short_description = "Download GraphML format suitalbe for Cytoscape"

    # def download_as_dot(self, request, queryset):
    #     A = nx.nx_agraph.to_agraph(power_network(queryset))
    #     response = HttpResponse(A.string(),
    #                             content_type="text/dot")
    #     response[
    #         'Content-Disposition'] = 'attachment; filename="power_network.dot"'
    #     return response
    # download_as_dot.\
    #     short_description = "Download DOT format for Graphviz"

    # def download_as_pdf(self, request, queryset):
    #     tmp = tempfile.SpooledTemporaryFile()
    #     # nx.drawing.nx_pydot.to_pydot(power_network(queryset)).create_pdf(),
    #     G = power_agraph(queryset)
    #     G.draw(tmp, format='pdf', prog='neato')
    #     tmp.seek(0)
    #     response = HttpResponse(
    #         tmp.read(),
    #         content_type="application/pdf")
    #     response[
    #         'Content-Disposition'] = 'attachment; filename="power_network.pdf"'
    #     return response
    # download_as_pdf.\
    #     short_description = "Download as PDF"


class AgencyEdgelistInline(JustMine, admin.TabularInline):
    model = AgencyEdge
    fk_name = 'project'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['person', 'people', 'action']


class SocialEdgelistInline(JustMine, admin.TabularInline):
    model = SocialEdge
    fk_name = 'project'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['source', 'target']


class PowerEdgelistInline(JustMine, admin.TabularInline):
    model = PowerEdge
    fk_name = 'project'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['person', 'power', ]


class MentalEdgelistInline(JustMine, admin.TabularInline):
    model = MentalEdge
    fk_name = 'project'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['source', 'target', ]


@admin.register(Project)
class ProjectAdmin(JustMine, admin.ModelAdmin):
    exclude = ('author', )
    list_display = ['project']

    inlines = [AgencyEdgelistInline,
               SocialEdgelistInline,
               PowerEdgelistInline,
               MentalEdgelistInline]

    def duplicate_project(self, request, queryset):

        for p in queryset:
            p.pk = None
            p.project = p.project + " (duplicate)"
            p.save()

            # TODO: copy all edgelists

    duplicate_project.\
        short_description = "Make duplicate copy of selected project"

    actions = [duplicate_project]


@admin.register(Category)
class CategoryAdmin(JustMine, admin.ModelAdmin):
    pass


@admin.register(Variable)
class VariableAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', ]


class AgencyEdgelistInline(JustMine, admin.TabularInline):
    model = AgencyEdge
    fk_name = 'action'
    extra = 1
    classes = ('grp-collapse grp-open',)
    autocomplete_fields = ['person', 'people']


@admin.register(Action)
class ActionAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['action', ]
    list_display = ['action', 'category', ]
    inlines = [AgencyEdgelistInline, ]
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter), )


@admin.register(MentalEdge)
class MentalEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name']
    list_display = ['person', 'source', 'target', 'project']

    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter), )

    actions = ['copy_to_latest_project',
               'download_as_graphml',
               'download_as_dot',
               'download_as_pdf', ]

    autocomplete_fields = ['source', 'target', 'person', ]

    def copy_to_latest_project(self, request, queryset):
        project = Project.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.project = project
            edge.save()
    copy_to_latest_project.\
        short_description = "Copy selected edges to latest project"

    def download_as_graphml(self, request, queryset):
        response = HttpResponse(
            "\n".join([l
                       for l in
                       nx.readwrite.graphml.generate_graphml(
                           mental_model(queryset))]),
            content_type="application/xml")
        response['Content-Disposition'] \
            = 'attachment; filename="cognitive_map.graphml"'
        return response
    download_as_graphml.\
        short_description = "Download GraphML format suitalbe for Cytoscape"

    def download_as_dot(self, request, queryset):
        A = nx.nx_agraph.to_agraph(mental_model(queryset))
        response = HttpResponse(A.string(),
                                content_type="text/dot")
        response[
            'Content-Disposition'] = 'attachment; filename="cognitive_map.dot"'
        return response
    download_as_dot.\
        short_description = "Download DOT format for Graphviz"

    def download_as_pdf(self, request, queryset):
        response = HttpResponse(
            nx.drawing.nx_pydot.to_pydot(mental_model(queryset)).create_pdf(),
            content_type="application/pdf")
        response[
            'Content-Disposition'] = 'attachment; filename="cognitive_map.pdf"'
        return response
    download_as_pdf.\
        short_description = "Download as PDF"


@admin.register(Power)
class PowerAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name']


@admin.register(PowerEdge)
class PowerEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name', 'power__name']
    list_display = ['person', 'power', 'project']

    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter), )

    autocomplete_fields = ['person', 'power', ]

    actions = ['copy_to_latest_project',
               'download_as_graphml',
               'download_as_pdf',
               'download_as_dot', ]

    def copy_to_latest_project(self, request, queryset):
        project = Project.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.project = project
            edge.save()
    copy_to_latest_project.\
        short_description = "Copy selected edges to latest project"

    def download_as_graphml(self, request, queryset):
        response = HttpResponse(
            "\n".join([l
                       for l in
                       nx.readwrite.graphml.generate_graphml(
                           power_network(queryset))]),
            content_type="application/xml")
        response['Content-Disposition'] \
            = 'attachment; filename="power_network.graphml"'
        return response
    download_as_graphml.\
        short_description = "Download GraphML format suitalbe for Cytoscape"

    def download_as_dot(self, request, queryset):
        A = nx.nx_agraph.to_agraph(power_network(queryset))
        response = HttpResponse(A.string(),
                                content_type="text/dot")
        response[
            'Content-Disposition'] = 'attachment; filename="power_network.dot"'
        return response
    download_as_dot.\
        short_description = "Download DOT format for Graphviz"

    def download_as_pdf(self, request, queryset):
        tmp = tempfile.SpooledTemporaryFile()
        # nx.drawing.nx_pydot.to_pydot(power_network(queryset)).create_pdf(),
        G = power_agraph(queryset)
        G.draw(tmp, format='pdf', prog='neato')
        tmp.seek(0)
        response = HttpResponse(
            tmp.read(),
            content_type="application/pdf")
        response[
            'Content-Disposition'] = 'attachment; filename="power_network.pdf"'
        return response
    download_as_pdf.\
        short_description = "Download as PDF"


@admin.register(AgencyEdge)
class AgencyEdgeAdmin(AdminAdvancedFiltersMixin, JustMine, admin.ModelAdmin):
    search_fields = ['person__name', 'action__action']
    list_display = ['id', 'person', 'action', 'project', ]

    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter), )

    advanced_filter_fields = (
        'person__name',
        'action__name',
        'distance',
        'interaction',
        'polarity',
        'project',
    )

    autocomplete_fields = ['person', 'action', 'people']

    actions = ['download_as_graphml',
               'agency_cluster_as_pdf',
               'relationship_diagram_as_pdf',
               'download_as_dot',
               'download_as_pdf', ]

    def download_as_graphml(self, request, queryset):
        response = HttpResponse(
            "\n".join([l
                       for l in
                       nx.readwrite.graphml.generate_graphml(
                           agency_network(queryset))]),
            content_type="application/xml")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.graphml"'
        return response
    download_as_graphml.\
        short_description = "Download GraphML format suitalbe for Cytoscape"

    def download_as_dot(self, request, queryset):
        A = nx.nx_agraph.to_agraph(agency_network(queryset))
        response = HttpResponse(A.string(),
                                content_type="text/dot")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.dot"'
        return response
    download_as_dot.\
        short_description = "Download DOT format for Graphviz"

    def download_as_pdf(self, request, queryset):
        with tempfile.SpooledTemporaryFile() as tmp:
            G = agency_agraph(queryset)
            G.draw(tmp, format='pdf', prog='neato')
            tmp.seek(0)
            response = HttpResponse(
                tmp.read(),
                content_type="application/pdf")
        response['Content-Disposition'] \
            = 'attachment; filename="agency_network.pdf"'
        return response
    download_as_pdf.\
        short_description = "Download as PDF"

    def relationship_diagram_as_pdf(self, request, queryset):
        egos = set()
        egos_alters = set()
        alters = set()
        actions = set()
        alters_actions = set()
        for e in queryset:
            egos.add(e.person)
            actions.add(e.action)
            for p in e.people.all():
                egos_alters.add((e.person.id, p.id))
                alters.add(p)
                alters_actions.add((p.id, e.action.id))
        A = pgv.AGraph()
        A.from_string(render_to_string('nwa/relationship_diagram.dot',
                                       {'queryset': queryset,
                                        'egos': egos,
                                        'egos_alters': egos_alters,
                                        'alters': alters,
                                        'actions': actions,
                                        'alters_actions': alters_actions
                                        }).encode('utf-8'))
        with tempfile.SpooledTemporaryFile() as tmp:
            A.draw(tmp, format='pdf', prog='dot')
            tmp.seek(0)
            response = HttpResponse(
                tmp.read(),
                content_type="application/pdf")
            response['Content-Disposition'] \
                = 'attachment; filename="power_network.pdf"'
            return response
    relationship_diagram_as_pdf.\
        short_description = "Download Relationship Diagram as PDF"

    def agency_cluster_as_pdf(self, request, queryset):
        egos = set()
        egos_alters = set()
        alters = set()
        actions = set()
        alters_actions = set()
        for e in queryset:
            egos.add(e.person)
            actions.add(e.action)
            for p in e.people.all():
                egos_alters.add((e.person.id, p.id))
                alters.add(p)
                alters_actions.add((p.id, e.action.id))
        A = pgv.AGraph()
        st = render_to_string('nwa/agency_cluster.dot',
                              {'queryset': queryset,
                               'egos': egos,
                               'egos_alters': egos_alters,
                               'alters': alters,
                               'actions': actions,
                               'alters_actions': alters_actions
                               }).encode('utf-8')
        print(st)
        A.from_string(st)
        with tempfile.SpooledTemporaryFile() as tmp:
            A.draw(tmp, format='pdf', prog='dot')
            tmp.seek(0)
            response = HttpResponse(
                tmp.read(),
                content_type="application/pdf")
            response['Content-Disposition'] \
                = 'attachment; filename="power_network.pdf"'
            return response
    agency_cluster_as_pdf.\
        short_description = "Cluster diagram as PDF"
