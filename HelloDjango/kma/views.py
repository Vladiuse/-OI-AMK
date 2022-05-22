from django.shortcuts import render
from django.http import HttpResponse
from .models import DefaultWeb, PhoneNumber


def default_webs(request):
    webs = DefaultWeb.objects.all()
    content = {
        'webs': webs
    }
    return render(request, 'kma/default_webs.html', content)

def phones(request):
    phones = PhoneNumber.objects.all().order_by('short')
    content = {
        'phones': phones,
    }
    return render(request, 'kma/phones.html', content)