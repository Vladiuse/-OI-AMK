import os
import time
import json
import zipfile
from urllib.parse import urlparse
from django.urls import reverse
from rest_framework.decorators import api_view, action, permission_classes, authentication_classes
from .serializers import SiteImagesSerializer, UserSiteSerializer
from rest_framework.response import Response
from rest_framework import viewsets
from shell import *
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import UserSiteCheckPoint, ActualUserList, CheckerUserSetting, SiteImage, CropTask, CropImage
from .checker_class.link_checker import LinkChecker
from django.template import Template
from django.template import RequestContext
from bs4 import BeautifulSoup
from .checker_class.errors import CheckerError
from .forms import CheckerUserSettingsForm
from .img_info import get_image_info
from django.views.decorators.http import require_http_methods
from rest_framework import permissions

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
        actual_user_list = ActualUserList.get_or_create(request.user, url)
        url_checker = LinkChecker(actual_user_list=actual_user_list, user=request.user, request=request)
        url_checker.load_url()
        url_checker.process()
        content = {
            'checker': url_checker,
            'kma': url_checker.land,
            'user_settings': settings,
        }
        if 'no-iframe' in request.POST:
            return HttpResponse(url_checker.land.iframe_srcdoc)
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
        actual_user_list = ActualUserList.objects.get(user=request.user, url=checked_url)
        url_checker = LinkChecker(actual_user_list, request.user, source_text=land_text)
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

@csrf_exempt
@require_http_methods(['GET','POST'])
def image_info(request):
    if request.method == 'GET':
        return JsonResponse({'x':'x'})
    img_href = request.POST['img_href']
    info = get_image_info(img_href)
    return JsonResponse(info, safe=True)





class DomainViewSet(viewsets.ModelViewSet):
    queryset = ActualUserList.objects.all()
    serializer_class = UserSiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteImageViewSet(viewsets.ModelViewSet):
    serializer_class = SiteImagesSerializer

    permission_classes = [permissions.IsAuthenticated]

    lookup_field = 'image_id'
    lookup_url_kwarg = 'image_id'

    # def domain(self):
    #     return ActualUserList.objects.get(pk=self.kwargs['domain_id'])

    def get_queryset(self):
        return SiteImage.objects.filter(domain_id=self.kwargs['domain_id'])

    @action(methods=['GET', 'POST'], detail=True)
    def create_or_update(self, request, *args, **kwargs):
        try:
            site_image = SiteImage.objects.get(
                domain_id=self.kwargs['domain_id'],
                image_url=self.request.data['image_url'])
            serializer = self.get_serializer(site_image, data=request.data)
        except SiteImage.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site_image = serializer.save(domain_id=self.kwargs['domain_id'])
        load_result = site_image.load_orig_img()
        return Response({
            'image': serializer.data,
            'load_result': load_result,
        })

    def get_object(self):
        if 'image_id' in self.kwargs:
            return SiteImage.objects.get(pk=self.kwargs['image_id'])
        else:
            return SiteImage.objects.get(
                domain_id=self.kwargs['domain_id'],
                image_url=self.request.data['image_url'])

    @action(detail=True, methods=['GET'])
    def load_orig(self, request, image_id):
        obj = self.get_object()
        obj.load_orig_img()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def make_thumb(self, request, image_id):
        obj = self.get_object()
        obj.make_thumb()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def load_make_thumb(self, request, image_id):
        obj = self.get_object()
        res = obj.load_make_thumb()
        serializer = self.get_serializer(obj)
        return Response({
            'result': res,
            'image': serializer.data
        })
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


@api_view(['GET', 'POST'], )
@permission_classes([permissions.IsAuthenticated])
def crop_images(request, domain_id):
    images_to_crop = request.POST['images_to_crop']
    images_to_crop = json.loads(images_to_crop)
    if not images_to_crop:
        return Response({
            'status': False,
            'mgs': 'No images to crop'
        })
    time.sleep(0.7)
    error = {
        'status': False,
        'mgs': 'Not created'
    }
    if len(images_to_crop) != SiteImage.objects.filter(pk__in=images_to_crop).count():
        error = {
            'status': False,
            'mgs': 'Count not match'
        }
        return Response(error)
    images = SiteImage.objects.filter(pk__in=images_to_crop)
    domain = ActualUserList.objects.get(pk=domain_id)
    task = CropTask.create_crop_task(domain, images,images_to_crop)
    # for image in images:
    #     size = (images_to_crop[str(image.pk)]['width'],images_to_crop[str(image.pk)]['height'])
    #     image.make_thumb(size)
    # zip_file_path = os.path.join(settings.MEDIA_ROOT, '_archive', 'test.zip')
    # zip_file = zipfile.ZipFile(zip_file_path, 'w')
    # for image in images:
    #     img_name_in_zip = urlparse(image.image_url).path
    #     if urlparse(image.image_url).query:
    #         img_name_in_zip += '?' + urlparse(image.image_url).query
    #     zip_file.write(image.thumb.path, img_name_in_zip)
    # zip_file.close()
    success = {
        'status': True,
        # 'archive_url': os.path.relpath(zip_file_path, settings.BASE_DIR),
        'archive_url': reverse('checker_2:crop_task', args=[task.pk,]),
    }
    return Response(success)

def crop_task(request, task_id):
    task = CropTask.objects.get(pk=task_id)
    crop_images = CropImage.objects.filter(task=task)
    content = {
        'task': task,
        'crop_images': crop_images,
    }
    return render(request, 'checker_2/task.html', content)
