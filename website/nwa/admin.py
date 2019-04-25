# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Person, AgencyEdge, Action, Phase, \
    Sector, Variable, MentalEdge, Category, \
    Power, PowerEdge


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

# class ActionEdgeInline(admin.TabularInline):
#     model = ActionEdge
#     fk_name = 'alter'
#     extra = 0

class AgencyEdgeInline(JustMine, admin.TabularInline):
    model = AgencyEdge
    fk_name = 'person'
    extra = 1
    classes = ('grp-collapse grp-closed',)
    autocomplete_fields = ['person', 'action', 'people'] 
    
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
    search_fields = ['name', 'avatar_name']
    list_display = ['name', 'sector', 'avatar_name',]
    
    list_filter = (
        ('sector', admin.RelatedOnlyFieldListFilter), )

    inlines = [AgencyEdgeInline,
               # ActionEdgeInline,
               PowerEdgeInline,
               MentalEdgeInline]

    fieldsets = (
        ('', {
            'fields': ('name', 'sector', 'description', 'avatar_name', 'avatar_pic', 'ego', ),
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


@admin.register(Phase)
class PhaseAdmin(JustMine, admin.ModelAdmin):
    exclude = ('author', )
    list_display = ['phase', 'author']


@admin.register(Category)
class CategoryAdmin(JustMine, admin.ModelAdmin):
    pass


@admin.register(Variable)
class VariableAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name']    
    list_display = ['name', ]


@admin.register(Action)
class ActionAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['action', ]
    list_display = ['action', 'category', 'in_degree']
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter), )


@admin.register(AgencyEdge)
class AgencyEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name', 'action__action']
    list_display = ['id', 'person', 'action', 'phase']
    
    list_filter = (
        ('phase', admin.RelatedOnlyFieldListFilter), )

    autocomplete_fields = ['person', 'action', 'people']
    
#     actions = ['copy_to_latest_phase']

#     def copy_to_latest_phase(self, request, queryset):
#         phase = Phase.objects.last()
#         for edge in queryset:
#             edge.pk = None
#             edge.phase = phase
#             edge.save()
#     copy_to_latest_phase.\
#         short_description = "Copy selected edges to latest phase"


@admin.register(MentalEdge)
class MentalEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name']
    list_display = ['person', 'source', 'target', 'phase']

    list_filter = (
        ('phase', admin.RelatedOnlyFieldListFilter), )

    actions = ['copy_to_latest_phase']

    autocomplete_fields = ['source', 'target', 'person', ]
    
    def copy_to_latest_phase(self, request, queryset):
        phase = Phase.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.phase = phase
            edge.save()
    copy_to_latest_phase.\
        short_description = "Copy selected edges to latest phase"


@admin.register(Power)
class PowerAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name']    


class PowerEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name', 'power__name']
    list_display = ['person', 'power', 'phase']

    list_filter = (
        ('phase', admin.RelatedOnlyFieldListFilter), )

    autocomplete_fields = ['person', 'power', ]
    
    actions = ['copy_to_latest_phase']

    def copy_to_latest_phase(self, request, queryset):
        phase = Phase.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.phase = phase
            edge.save()
    copy_to_latest_phase.\
        short_description = "Copy selected edges to latest phase"


admin.site.register(PowerEdge, PowerEdgeAdmin)


admin.site.site_header = "Agency Network Serializer"
admin.site.site_title = "AgNes Admin Portal"
admin.site.index_title = "Agency network database administrator"
