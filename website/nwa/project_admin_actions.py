from .models import SocialEdge, AgencyEdge, PowerEdge, MentalEdge, Project


def duplicate_project(self, request, queryset):

    for p in queryset:
        duproject = Project(project=p.project + " (duplicate)",
                            author=request.user)
        duproject.save()

        for edgelist in (MentalEdge, SocialEdge, PowerEdge):
            for edge in edgelist.objects.filter(project=p,
                                                author=request.user):
                edge.pk = None
                edge.project = duproject
                edge.save()

        for edge in AgencyEdge.objects.filter(project=p, author=request.user):
            people = list(edge.people.all())
            edge.pk = None
            edge.project = duproject
            edge.save()
            edge.people.set(people)
            edge.save()


duplicate_project.\
    short_description = "Make duplicate copy of selected project, including edgelists"
