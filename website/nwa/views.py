from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from nwa.models import AgencyEdge, SocialEdge, PowerEdge, MentalEdge, Project
from django.shortcuts import HttpResponseRedirect


class DeleteAction(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def post(self, request, *args, **kwargs):
        model = request.POST['model']
        
        if model == "AgencyEdge":
            EdgeList = AgencyEdge
        elif model == 'SocialEdge':
            EdgeList = SocialEdge
        elif model == 'PowerEdge':
            EdgeList = PowerEdge
        elif model == 'MentalEdge':
            EdgeList = MentalEdge
            
        for obj_id in request.POST.getlist('obj_ids'):
            obj = EdgeList.objects.get(pk=obj_id)
            obj.delete()
            
        return HttpResponseRedirect('/admin/nwa/%s' % model.lower())





class CopyAction(LoginRequiredMixin, View):
    login_url = '/account/login/'

    def post(self, request, *args, **kwargs):
        model = request.POST['model']

        new_project = Project.objects.get(pk=request.POST['project'])
        
        if model == "AgencyEdge":
            EdgeList = AgencyEdge
        elif model == 'SocialEdge':
            EdgeList = SocialEdge
        elif model == 'PowerEdge':
            EdgeList = PowerEdge
        elif model == 'MentalEdge':
            EdgeList = MentalEdge

        for obj_id in request.POST.getlist('obj_ids'):
            obj = EdgeList.objects.get(pk=obj_id)
            obj.pk = None
            obj.project = new_project
            print(obj, obj.project)
            #obj.save()
            
        return HttpResponseRedirect('/admin/nwa/%s' % model.lower())
    
