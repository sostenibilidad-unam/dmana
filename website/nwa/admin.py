# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Person, AgencyEdge, Action, Phase, \
    Sector, Variable, MentalEdge, Category, \
    Power, PowerEdge


# class EgoEdgeInline(admin.TabularInline):
#     model = EgoEdge
#     fk_name = 'source'
#     extra = 1


# class ActionEdgeInline(admin.TabularInline):
#     model = ActionEdge
#     fk_name = 'alter'
#     extra = 0


class PowerEdgeInline(admin.TabularInline):
    model = PowerEdge
    fk_name = 'source'
    extra = 1


class MentalEdgeInline(admin.TabularInline):
    model = MentalEdge
    fk_name = 'ego'
    extra = 1


class PersonAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'sector', 'avatar_name', 'image_tag']

    list_filter = ('sector', )

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


admin.site.register(Sector)

class PhaseAdmin(admin.ModelAdmin):
    exclude = ('author', )
    list_display = ['phase', 'author']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.author != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.author != request.user and request.user.is_superuser is False:
            return False
        return True

    def get_queryset(self, request):
        print('soy super')        
        qs = super(PhaseAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

admin.site.register(Phase, PhaseAdmin)


admin.site.register(Category)


class VariableAdmin(admin.ModelAdmin):
    list_display = ['name', ]


admin.site.register(Variable, VariableAdmin)


class ActionAdmin(admin.ModelAdmin):
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


class MentalEdgeAdmin(admin.ModelAdmin):
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

admin.site.register(Power)


class PowerEdgeAdmin(admin.ModelAdmin):
    search_fields = ['source__name', 'target__name']
    list_display = ['source', 'target', 'phase']

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
