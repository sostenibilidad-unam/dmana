from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from django.contrib.contenttypes.models import ContentType


class AccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        user = request.user
        if not user.is_staff:
            user.is_staff = True

            for ct in ContentType.objects.filter(app_label='nwa'):
                for permission in ct.permission_set.all():
                    user.user_permissions.add(permission)

            user.save()

        return resolve_url('/admin/')
