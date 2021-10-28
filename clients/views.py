from django.shortcuts import HttpResponse
from django.views.generic import ListView

from clients.models import Domain


def index(request):
    return HttpResponse(
        f"<center><h2>Hello everyone to {request.tenant.name} gym</h2></center>"
    )


class ClientsView(ListView):
    model = Domain
    template_name = 'site_links.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        links = []
        for obj in Domain.objects.all():
            if len(self.request.headers['host'].split(":")) > 1:
                links.append(f"{obj.domain}:{self.request.headers['host'].split(':')[-1]}")
            else:
                links.append(obj.domain)
        context['links'] = links
        return context
