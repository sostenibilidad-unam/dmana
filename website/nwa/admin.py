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
        if obj is not None and obj.author != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None\
           and obj.author != request.user\
           and request.user.is_superuser is False:
            return False
        else:
            return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs['queryset'] = db_field.related_model.objects.filter(
            author=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class EgoEdgeInline(admin.TabularInline):
#     model = EgoEdge
#     fk_name = 'source'
#     extra = 1


# class ActionEdgeInline(admin.TabularInline):
#     model = ActionEdge
#     fk_name = 'alter'
#     extra = 0


class PowerEdgeInline(JustMine, admin.TabularInline):
    model = PowerEdge
    fk_name = 'person'
    extra = 1


class MentalEdgeInline(JustMine, admin.TabularInline):
    model = MentalEdge
    fk_name = 'ego'
    extra = 1


class PersonAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'sector', 'avatar_name', 'image_tag']

    list_filter = (
        ('sector', admin.RelatedOnlyFieldListFilter), )

    inlines = [#EgoEdgeInline,
               #ActionEdgeInline,
               PowerEdgeInline,
               MentalEdgeInline]


admin.site.register(Person, PersonAdmin)


# class EgoEdgeAdmin(admin.ModelAdmin):
#     search_fields = ['source__name', 'target__name', 'phase__phase']
#     list_display = ['id', 'source', 'influence_source',
#                     'target', 'influence_target',
#                     'distance', 'polarity', 'interaction', 'phase']

#     list_filter = ('phase',)

#     actions = ['copy_to_latest_phase', ]

#     def copy_to_latest_phase(self, request, queryset):
#         phase = Phase.objects.last()
#         for edge in queryset:
#             edge.pk = None
#             edge.phase = phase
#             edge.save()
#     copy_to_latest_phase.\
#         short_description = "Copy selected edges to latest phase"

# admin.site.register(EgoEdge, EgoEdgeAdmin)


@admin.register(Sector)
class SectorAdmin(JustMine, admin.ModelAdmin):

    list_display = ['sector']

    def get_queryset(self, request):
        qs = super(SectorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)


#admin.site.register(Sector, SectorAdmin)


class PhaseAdmin(JustMine, admin.ModelAdmin):
    exclude = ('author', )
    list_display = ['phase', 'author']


admin.site.register(Phase, PhaseAdmin)


admin.site.register(Category)


class VariableAdmin(JustMine, admin.ModelAdmin):
    list_display = ['name', ]


admin.site.register(Variable, VariableAdmin)


class ActionAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['action', ]
    list_display = ['action', 'category', 'in_degree']
    list_filter = ('category', )


admin.site.register(Action, ActionAdmin)


# class ActionEdgeAdmin(admin.ModelAdmin):
#     search_fields = ['alter__name', 'action__action']
#     list_display = ['id', 'alter', 'action', 'phase']

#     actions = ['copy_to_latest_phase']

#     list_filter = ('phase',)

#     def copy_to_latest_phase(self, request, queryset):
#         phase = Phase.objects.last()
#         for edge in queryset:
#             edge.pk = None
#             edge.phase = phase
#             edge.save()
#     copy_to_latest_phase.\
#         short_description = "Copy selected edges to latest phase"


# admin.site.register(ActionEdge, ActionEdgeAdmin)


class MentalEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['ego__name']
    list_display = ['ego', 'source', 'target', 'phase']

    list_filter = ('phase',)

    actions = ['copy_to_latest_phase']

    def copy_to_latest_phase(self, request, queryset):
        phase = Phase.objects.last()
        for edge in queryset:
            edge.pk = None
            edge.phase = phase
            edge.save()
    copy_to_latest_phase.\
        short_description = "Copy selected edges to latest phase"


admin.site.register(MentalEdge, MentalEdgeAdmin)


@admin.register(Power)
class PowerAdmin(JustMine, admin.ModelAdmin):
    pass


class PowerEdgeAdmin(JustMine, admin.ModelAdmin):
    search_fields = ['person__name', 'power__name']
    list_display = ['person', 'power', 'phase']

    list_filter = ('phase',)

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
