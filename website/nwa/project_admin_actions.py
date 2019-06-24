import tempfile
from .networks import social_agraph, social_network
from .models import Sector
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .models import SocialEdge, AgencyEdge, PowerEdge, MentalEdge, Project


def duplicate_project(self, request, queryset):

    for p in queryset:
        duproject = Project(project=p.project + " (duplicate)",
                            author=request.user)
        duproject.save()

        for edgelist in (MentalEdge, SocialEdge, AgencyEdge, PowerEdge):
            for edge in edgelist.objects.filter(project=p,
                                                author=request.user):
                edge.pk = None
                edge.project = duproject
                edge.save()

duplicate_project.\
    short_description = "Make duplicate copy of selected project, including edgelists"
