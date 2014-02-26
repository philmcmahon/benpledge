from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader


def index(request):
    context = {}
    return render(request, 'publicweb/index.html', context)

def profile(request):
    context = {}
    return render(request, 'publicweb/base_profile.html')