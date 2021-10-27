# at carbackend/backend/users/views.py

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.generic import View

User = get_user_model()


class EmailVerify(View):

    def get(self, request, token):
        if token:
            try:
                user = User.objects.get(activation_token=token)
                user.activation_token = None
                user.is_email_verified = True
                user.save()
                return HttpResponse("<center>Verified Successful</center>")
            except User.DoesNotExist:
                return HttpResponse("<center>Wrong or expired token!</center>")
