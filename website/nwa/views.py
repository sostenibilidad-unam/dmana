from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from nwa.models import AgencyEdge
from django.shortcuts import HttpResponseRedirect
from pprint import pprint


class DeleteAction(LoginRequiredMixin, View):
    login_url = '/accountlogin/'

    def post(self, request, *args, **kwargs):
        model = request.POST['model']
        
        if model == "AgencyEdge":
            EdgeList = AgencyEdge

        for obj_id in request.POST.getlist('obj_ids'):
            obj = EdgeList.objects.get(pk=obj_id)
            obj.delete()
            
        return HttpResponseRedirect('/admin/nwa/%s' % model.lower())


