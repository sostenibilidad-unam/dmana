# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Person, AgencyEdge, Action, Project, \
    Sector, Variable, MentalEdge, Category, \
    Power, PowerEdge, Organization, SocialEdge

import nwa.agency_edge_admin_actions as aexn
import nwa.mental_edge_admin_actions as mmxn
import nwa.power_edge_admin_actions as pexn
import nwa.social_edge_admin_actions as sexn


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
class SocialEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['source__name', 'target__name']
    list_display = ['source', 'target',
                    'influence', 'distance', 'interaction', 'polarity',
                    'project']

    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter), 'interaction')

    autocomplete_fields = ['source', 'target', ]

    actions = [sexn.download_as_graphml,
               sexn.download_as_dot,
               sexn.download_as_pdf, ]


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
               mmxn.download_as_graphml,
               mmxn.download_as_dot,
               mmxn.download_as_pdf, ]

    autocomplete_fields = ['source', 'target', 'person', ]

    def copy_to_latest_project(self, request, queryset):
        project = Project.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.project = project
            edge.save()
    copy_to_latest_project.\
        short_description = "Copy selected edges to latest project"



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

    actions = [
        'copy_to_latest_project',
        pexn.download_as_graphml,
        pexn.download_as_pdf,
        pexn.download_as_dot,
    ]

    def copy_to_latest_project(self, request, queryset):
        project = Project.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.project = project
            edge.save()
    copy_to_latest_project.\
        short_description = "Copy selected edges to latest project"


@admin.register(AgencyEdge)
class AgencyEdgeAdmin(JustMine, admin.ModelAdmin):
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

    actions = [aexn.download_as_graphml,
               aexn.relationship_diagram_as_pdf,
               aexn.download_as_dot,
               aexn.download_as_pdf, ]
