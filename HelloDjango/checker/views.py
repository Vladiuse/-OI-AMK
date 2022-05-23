from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .checker_class import DomFixxer, TextFixxer
import requests as req
from bs4 import BeautifulSoup

# Create your views here.

def index(requests):
    return render(requests, 'checker/index.html')

def check_url(request):
    # try:
    url = request.GET['url']
    # url = '1https://blog-feed.org/blog2-herbamanan/?ufl=14114'
    res = req.get(url)
    if res.status_code != 200:
        return HttpResponse(f'Error: res.status_code != 200, Ссылка не работает!')
    text = res.text
    t_fix = TextFixxer(text)
    t_fix.process()
    text = t_fix.text
    soup = BeautifulSoup(text, 'lxml')
    dom = DomFixxer(soup, url=url)
    dom.process()
    htm_page = str(dom.soup)
    return HttpResponse(htm_page)

    
# def check_url(request):
#     # try:
#     url = request.GET['url']
#     # url = '1https://blog-feed.org/blog2-herbamanan/?ufl=14114'
#     res = req.get(url)
#     if res.status_code != 200:
#         return HttpResponse(f'Error: res.status_code != 200, Ссылка не работает!')
#     text = res.text
#     text = TextFixxer.fix_dates(text)
#     soup = BeautifulSoup(text, 'lxml')
#     FrontElems.add_elems_to_text(soup, url=url)
#     return HttpResponse(str(soup))


def fix_ready_body(requests):
    body = requests.POST['body']
    body = TextFixxer.fix_dates(body)
    data = {'body': body}
    return JsonResponse(data, safe=False)
 #    except BaseException as error:
 #        return HttpResponse(f'Error: {error}')
 #