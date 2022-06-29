from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return redirect('kma:phones')
    return render(request, 'root/index.html')
    # return HttpResponse('WORK')

