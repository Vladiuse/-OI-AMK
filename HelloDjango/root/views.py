from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'root/index.html')
    # return HttpResponse('WORK')

