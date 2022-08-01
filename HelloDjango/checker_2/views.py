from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .checker_class.text_fixxer import DomFixxer, TextFixxer, TOOLBAR_STYLES_FILE
from .checker_class.text_finder import TextAnaliz
from .checker_class.kma_info import get_rekl_by_id
from .checker_class.kma_land import KMALand
from kma.models import OfferPosition, PhoneNumber
import requests as req
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.conf import settings
# Create your views here.
import yaml

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
    with open(TOOLBAR_STYLES_FILE, encoding='utf-8') as file:
        debug_styles = file.read()
    content = {
        'debug_styles': debug_styles,
    }
    return render(requests, 'checker_2/index.html', content)

@login_required
def check_url(request):
    # получения кода для iframe
    url = request.GET['url']
    url = url.strip()
    url = url.replace('https://', 'http://')
    res = req.get(url)
    if res.status_code != 200:
        return HttpResponse(f'Error: res.status_code != 200, Ссылка не работает!')
    # 
    text = res.text
    kma = KMALand(url, text)
    kma.phone_code = PhoneNumber.get_phone_code_by_country(kma.country)
    t_fix = TextFixxer(text)
    t_fix.process()
    text = t_fix.text
    soup = BeautifulSoup(text, 'html5lib')
    dom = DomFixxer(soup, url=url)
    dom.process()
    htm_page = str(dom.soup)
    htm_page = htm_page.replace('"', '&quot;')
    htm_page = htm_page.replace("'", '&apos;')
    content = {
        'land': htm_page,
        'checker_list': read_check_list(),
        'kma': kma,
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
        analizer = TextAnaliz(land_text=land_text, data=data)
        analizer.process()
        answer = {
            'success': True,
            'result': analizer.result,
        }
    except BaseException as error:
        answer = {
            'success': False,
            'error': str(error),
        }
    return JsonResponse(answer, safe=False)
