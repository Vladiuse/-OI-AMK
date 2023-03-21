import yaml
import requests as req
from requests.exceptions import ConnectionError
import time
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .checker_class.kma_land import KMALand
from .models import UserSiteCheckPoint, ActualUserList, CheckerUserSetting
from .checker_class.link_checker import LinkChecker
from django.template import Template
from django.template import RequestContext
from bs4 import BeautifulSoup
from .checker_class.errors import CheckerError
from .forms import CheckerUserSettingsForm
from shell import *


@login_required
def index(request):
    settings = CheckerUserSetting.objects.get(user=request.user)
    settings_form = CheckerUserSettingsForm(instance=settings, prefix='ch_set')
    content = {
        'settings_form':settings_form,
    }
    return render(request, 'checker_2/index.html', content)

@login_required
def check_url(request):
    # получения кода для iframe
    url = request.POST['url']
    settings = CheckerUserSetting.objects.get(user=request.user)
    setting_form = CheckerUserSettingsForm(request.POST, instance=settings, prefix='ch_set')
    if setting_form.is_valid():
        setting_form.user = request.user
        setting_form.save()
    try:
        url_checker = LinkChecker(url=url, user=request.user)
        url_checker.load_url()
        url_checker.process()
        content = {
            'checker': url_checker,
            'kma': url_checker.land,
            'user_settings': settings,
        }
        return render(request, 'checker_2/frame.html', content)
    except CheckerError as error:
        content = {
            'error_text': error.__doc__,
            'user_settings':settings,
        }
        return render(request, 'checker_2/index.html', content)


@login_required
@csrf_exempt
def analiz_land_text(request):
    try:
        land_text = request.POST['land_text']
        checked_url = request.POST['checked_url']
        url_checker = LinkChecker(checked_url, request.user, source_text=land_text)
        result = url_checker.text_analiz()
        answer = result
        answer['success'] = True
    except BaseException as error:
        print(error)
        answer = {
            'success': False,
            'error': str(error), #TODO добавит на фронт сообщение об ошибке
        }
    # print(ST)
    return JsonResponse(answer, safe=False)




@login_required
def change_status_of_user_checklist(request):
    """Изменение статуса у чекпоинта списка проверки сайта"""
    if request.method == 'POST':
        user = request.user
        check_point_id = request.POST['check_point_id']
        checked_url = request.POST['checked_url']
        status = request.POST['status']
        if status == 'true':
            status = True
        else:
            status = False
        try:
            user_list = ActualUserList.objects.get(user=user,url=checked_url)
            check_point = UserSiteCheckPoint.objects.get(check_point_id=check_point_id, user_list=user_list)
            check_point.is_checked = status
            check_point.save()
            answer = {
                'success': True,
            }
            return JsonResponse(answer, safe=False)
        except UserSiteCheckPoint.DoesNotExist as error:
            answer = {
                'success': False,
                'error': str(error),
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method',
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def doc_page(request):  #TODO -  перенести в kma?
    manual_land = request.POST['manual_land']
    manual_land = manual_land.replace('.', '/')
    block_id = None
    if '#' in manual_land:
        manual_land, block_id = manual_land.split('#')
    file_path = str(settings.BASE_DIR) + f'/manual/templates/manual/{manual_land}.html'
    with open(file_path, encoding='utf-8') as file:
        text = file.read()
    to_remove = ["{% extends 'manual/base.html' %}", "{% block content %}", "{%endblock%}", "{% endblock %}"]
    for tag in to_remove:
        text  = text.replace(tag, '')
    if block_id:
        soup = BeautifulSoup(text,'lxml')
        text_block = soup.find('div', {'id': block_id})
        text = str(text_block)
    text = '{% load note %}\n'+text
    context = RequestContext(request,{'x': 'xxxx'})
    t = Template(text)
    res = t.render(context)
    return HttpResponse(res)


def dell_old(requests):
    try:
        deleted_records = ActualUserList.dell_old()
        res = {
            'status': 'success',
            'deleted_records': deleted_records
        }
    except BaseException as error:
        res = {
            'status': 'error',
            'error': str(error),
        }
    return JsonResponse(res)


@login_required
def test(request):
    settings = CheckerUserSetting.objects.get(user=request.user)
    if request.method == 'POST':
        form = CheckerUserSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.user = request.user
            form.save()

    form = CheckerUserSettingsForm(instance=settings)
    content = {
        'form': form,
    }
    return render(request, 'checker_2/test.html', content)

