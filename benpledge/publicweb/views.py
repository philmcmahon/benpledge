from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader


def index(request):
    context = {}
    return render(request, 'publicweb/index.html', context)



    # django.shortcuts.render_to_response('register.html',
        # dict(userform=uf),
        # context_instance=django.template.RequestContext(request))