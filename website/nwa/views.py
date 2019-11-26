from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from nwa.models import AgencyEdge, SocialEdge, PowerEdge, MentalEdge
from django.shortcuts import HttpResponseRedirect


class DeleteAction(LoginRequiredMixin, View):
    login_url = '/accountlogin/'

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


