from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .checker_class.text_fixxer import DomFixxer, TextFixxer, TOOLBAR_STYLES_FILE
from .checker_class.text_finder import TextAnaliz
from kma.models import OfferPosition, PhoneNumber
import requests as req
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index(requests):
    with open(TOOLBAR_STYLES_FILE, encoding='utf-8') as file:
        debug_styles = file.read()
    content = {
        'debug_styles': debug_styles,
    }
    return render(requests, 'checker/index.html', content)

@login_required
def check_url(request):
    # try:
    url = request.GET['url']
    url = url.strip()
    url = url.replace('https://', 'http://')
    res = req.get(url)
    if res.status_code != 200:
        return HttpResponse(f'Error: res.status_code != 200, Ссылка не работает!')
    text = res.text
    t_fix = TextFixxer(text)
    t_fix.process()
    text = t_fix.text
    soup = BeautifulSoup(text, 'html5lib')
    dom = DomFixxer(soup, url=url)
    dom.process()
    htm_page = str(dom.soup)
    return HttpResponse(htm_page)


@login_required
@csrf_exempt
def analiz_land_text(request):
    try:
        land_text = request.POST['land_text']
        # print('россииа' in land_text)
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


@login_required
def check_url_no_js(request):
    url = request.GET['url']
    # url = '1https://blog-feed.org/blog2-herbamanan/?ufl=14114'
    res = req.get(url)
    if res.status_code != 200:
        return HttpResponse(f'Error: res.status_code != 200, Ссылка не работает!')
    text = res.text
    soup = BeautifulSoup(text, 'lxml')
    for script in soup.find_all('script'):
        script.decompose()
    jq = soup.new_tag('script')
    jq['src'] = 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'
    soup.html.head.append(jq)
    dom_fixxer = DomFixxer(soup, url)
    dom_fixxer.load_wb()
    dom_fixxer.add_wb()
    return HttpResponse(str(dom_fixxer.soup))