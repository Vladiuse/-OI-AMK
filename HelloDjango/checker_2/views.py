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
from .checker_class.checker_class import UrlChecker
from django.template import Template
from django.template import RequestContext
from bs4 import BeautifulSoup
from .checker_class.errors import CheckerError

from shell import *



# Create your views here.


def read_check_list():
    yaml_path = str(settings.BASE_DIR) + '/checker_2/check_list.yaml'
    with open(yaml_path, encoding='utf-8') as f:
        template = yaml.safe_load(f)
    for k,v in template.items():
        if v is None:
            template[k] = []
    return template

@login_required
def index(request):
    settings = CheckerUserSetting.objects.get(user=request.user)
    content = {
        'user_settings':settings,
    }
    return render(request, 'checker_2/index.html', content)

@login_required
def check_url(request):
    # получения кода для iframe
    url = request.GET['url']
    url = KMALand.format_url(url)
    start = time.time()
    settings = CheckerUserSetting.objects.get(user=request.user)
    left_bar = request.GET['checker_leftbar']
    click_elem = request.GET['checker_clickelems']
    other = request.GET['checker_other_elems']
    left_bar = True if left_bar.lower() == 'true' else False
    click_elem = True if click_elem.lower() == 'true' else False
    other = True if other.lower() == 'true' else False
    settings.left_bar = left_bar
    settings.click_elem = click_elem
    settings.other = other
    settings.save()
    try:
        res = req.get(url)
    except ConnectionError:
        content = {
            'error_text': 'Ссылка не работает',
            'user_settings':settings,
        }
        return render(request, 'checker_2/index.html', content)
    end_load_url = time.time()
    print(f'Site Load:{round(end_load_url - start,2)}')
    if res.status_code != 200:
        content = {
            'error_text': 'Ссылка не работает',
            'user_settings':settings,
        }
        return render(request, 'checker_2/index.html', content)
    else:
        try:
            url_checker = UrlChecker(res.text, url=url, user=request.user)
            url_checker.process()
            content = {
                'checker': url_checker,
                'kma': url_checker.land,
                'user_settings': settings,
            }
            end = time.time()

            print(f'Total:{round(end - start, 2)}')
            print(ST)
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
        url_checker = UrlChecker
        result = url_checker.text_analiz(land_text)
        answer = {
            'success': True,
            'result': result['old'],
            'new_checker': result['new'],
            'jeneral_status': result['jeneral_status'],
        }
    except IndentationError as error:
        answer = {
            'success': False,
            'error': str(error),
        }
    return JsonResponse(answer, safe=False)


@login_required
def test(request):
    content = {
        'var': 'VAR',
        'list': list(range(10)),
    }
    return render(request, 'checker_2/test.html', content)

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
def doc_page(request):
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



