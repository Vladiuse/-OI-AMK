import yaml
import requests as req
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .checker_class.text_finder import TextAnaliz
from .checker_class.kma_land import KMALand, Land
from kma.models import OfferPosition, PhoneNumber
from .models import UserSiteCheckPoint
from .checker_class.check_list_view import CheckListView
from .checker_class import UrlChecker
from qr_code.qrcode.utils import QRCodeOptions


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
def index(requests):
    # with open(TOOLBAR_STYLES_FILE, encoding='utf-8') as file:
    #     debug_styles = file.read()
    # content = {
    #     'debug_styles': debug_styles,
    # }
    return render(requests, 'checker_2/index.html')

@login_required
def check_url(request):
    # получения кода для iframe
    url = request.GET['url']
    url = KMALand.format_url(url)
    res = req.get(url)
    if res.status_code != 200:
        raise ZeroDivisionError
    else:
        url_checker = UrlChecker(res.text, url=url, user=request.user)
        url_checker.process()
        content = {
            'checker': url_checker,
            'kma': url_checker.land,
        }
        return render(request, 'checker_2/frame.html', content)


@login_required
@csrf_exempt
def analiz_land_text(request):
    try:
        land_text = request.POST['land_text']
        offers = OfferPosition.objects.values('name')
        offers_names = [offer['name'] for offer in offers]
        phones = PhoneNumber.objects.values('short','currency', 'phone_code', 'words')
        phone_codes = [phone['phone_code'] for phone in phones]
        currencys = [phone['currency'] for phone in phones]
        geo_words = {}
        geo_words_templates = {}
        for phone in phones:
            if phone['words']['words']:
                dic = {phone['short']: phone['words']['words']}
                geo_words.update(dic)
        for phone in phones:
            if phone['words']['templates']:
                dic = {phone['short']: phone['words']['templates']}
                geo_words_templates.update(dic)
        data = {
            'offers': offers_names,
            'currencys': currencys,
            'phone_codes': phone_codes,
            'geo_words': geo_words,
            'geo_words_templates': geo_words_templates,
        }
        land = Land(source_text=land_text,url='0', parser='lxml')
        land.drop_tags_from_dom(KMALand.POLICY_IDS)
        human_text = land.get_human_land_text()
        analizer = TextAnaliz(source_text=str(land.soup.text),human_text=human_text, data=data)
        analizer.process()
        answer = {
            'success': True,
            'result': analizer.result,
        }
    except IndexError as error:
        answer = {
            'success': False,
            'error': str(error),
        }
    return JsonResponse(answer, safe=False)


@login_required
def check_list(request):

    url = 'https://1111.com'

    check_list = CheckListView(
    land_type='pre_land',
    discount_type='full_price',
    country='th',
    lang='ru',
    land_attrs=[ 'more_one_select'],
    user=request.user,
    url=url,
    )
    check_list.process()
    # content = {'check_list': check_list}
    content = {
        'checked_url': url,
        'check_list': check_list,
        'url': 'https://www.youtube.com/',
        'my_options' : QRCodeOptions(size='20', border=6, error_correction='Q',image_format='png',
                                     # dark_color='#2496ff',
                                     dark_color='white',
                                     light_color='#404040',
                                     ),
    }
    return render(request, 'checker_2/check_list.html', content)

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
            check_point = UserSiteCheckPoint.objects.get(user=user, check_point_id=check_point_id, url=checked_url)
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

