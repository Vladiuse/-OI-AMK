from django.shortcuts import render
from django.http import HttpResponse
from .models import Site, SiteCategoty, Languege, Cataloge, Tag, SiteLocal, Siteremote
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .func import transform_list_object
from django.conf import settings
from django.contrib.auth.decorators import login_required
import requests as req
from bs4 import BeautifulSoup
import os

@login_required
def index(request):
    s = SiteLocal()
    s.update_sites_models()
    archive_url = SiteLocal.SITE_DOMAIN
    current_domain = str(request.get_host())
    tags = Tag.objects.all()
    if current_domain.startswith('127'):
        current_domain = f'http://{current_domain}/'
    else:
        current_domain = f'https://{current_domain}/'
    content = {
        # 'sites': sites,
        # 'categorys': categorys,
        'archive_url': archive_url,
        'current_domain': current_domain,
        'tags': tags,
        }
    return render(request, 'archive/main.html', content)

@login_required
def get_sites_n_categorys(request):
    categorys = SiteCategoty.objects.values()
    sites = Site.objects.order_by('name').values()
    langueges = Languege.objects.values()
    cataloges = Cataloge.objects.all().values()
    tags = Tag.objects.all().values()
    answer = {
        'sites': list(sites),
        'categorys': list(categorys),
        'langueges': transform_list_object(list(langueges)),
        'cataloges': transform_list_object(list(cataloges)),
        'tags': transform_list_object(list(tags)),
    }
    return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def add_site_category(request):
    if request.method == 'POST':
        try:
            new_category_name = request.POST['category_name']
            category = SiteCategoty(name=new_category_name)
            category.save()
            answer = {
                'success': True,
                'category_name': category.name,
                'category_id': category.pk
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': error
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def update_category(request):
    """Обновление категории"""
    if request.method == 'POST':
        try:
            new_cat_name = request.POST['new_cat_name']
            card_id = request.POST['card_id']
            category = SiteCategoty.objects.get(name=new_cat_name)
            card = Site.objects.get(pk=card_id)
            card.category = category
            card.save()
            answer = {
                'success': True,
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': error
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def update_name_n_desc(request):
    """Обновить название или описание сайта"""
    if request.method == 'POST':
        try:
            new_site_name = request.POST['site_name']
            new_site_desc = request.POST['site_desc']
            new_lang_id = request.POST['lang_id']
            site_id = request.POST['site_id']
            site = Site.objects.get(pk=site_id)
            lang = Languege.objects.get(pk=new_lang_id)
            site.name = new_site_name
            site.description = new_site_desc
            site.languege = lang
            site.save()
            answer = {
                    'success': True,
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': error
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def add_cataloge(request):
    """Добавить новый каталог"""
    if request.method == 'POST':
        try:
            cataloge_name = request.POST['catalog_name']
            category_id = request.POST['category_id']
            category = SiteCategoty.objects.get(pk=category_id)
            catalog = Cataloge()
            catalog.name = cataloge_name
            catalog.category = category
            catalog.save()
            answer = {
                'success': True,
                'cataloge': {
                    'id': catalog.pk,
                    'name': catalog.name,
                    'category_id': catalog.category.pk,
                }
                
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': error
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def add_site_to_cataloge(request):
    """Добавить сайт в каталог"""
    if request.method == 'POST':
        try:
            site_id = request.POST['site_id']
            catalog_id = request.POST['cataloge_id']
            # print(catalog_id, len(catalog_id),type(catalog_id),'xxxxxxxxxxxxxxxxxxxx')
            site = Site.objects.get(pk=site_id)
            if catalog_id:
                cataloge = Cataloge.objects.get(pk=catalog_id)
            else:
                cataloge = None
            site.cataloge = cataloge
            site.save()
            answer = {
                'success': True,
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': str(error)
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def remove_cataloge(request):
    """Удаление каталога"""
    if request.method == 'POST':
        try:
            catalog_id = request.POST['cataloge_id']
            catalog = Cataloge.objects.get(pk=catalog_id)
            sites_in_cat_ids = []
            sites_set = catalog.site_set.all()
            for site in sites_set:
                sites_in_cat_ids.append(site.id)
            catalog.delete()
            answer = {
                'success': True,
                'sites_in_cataloge': sites_in_cat_ids,
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': str(error)
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def add_remote_site(request):
    """Добавление удаленного сайта"""
    if request.method == 'POST':
        try:
            site_name=request.POST['site-name']
            site_desc = request.POST['site-desc']
            site_url = request.POST['site-url']
            lang_id = request.POST['site-lang']
            try:
                lang = Languege.objects.get(pk=lang_id)
            except:
                lang = None
            site_remote = Siteremote(
                name=site_name, 
                description=site_desc,
                languege=lang,
                path=site_url,
            )
            site_remote.save()
            site_remote.load_screenshot()
            site_remote.fix_image_size()
            site = {
                'id': site_remote.pk,
                'name': site_name,
                'description': site_desc,
                'path': site_remote.path,
                'tag_id': None,
                'languege_id': site_remote.languege,
                'image': site_remote.image.name,
                'category_id': None,
                'cataloge_id': None,
            }
            answer = {
                'success': True,
                'site': site,
            }
            return JsonResponse(answer, safe=False)
        except BaseException as error:
            answer = {
                'success': False,
                'error': str(error)
            }
            return JsonResponse(answer, safe=False)
    else:
        answer = {
            'success': False,
            'error': 'Wrong method'
        }
        return JsonResponse(answer, safe=False)

# def test(request):
#     with open('./script.js') as file:
#         script = file.read()
#     with open('./styles.css') as file:
#         styles = file.read()
#     with open('./block.html') as file:
#         block = file.read()
#     url = 'https://blog-feed.org/blog2-herbamanan/?ufl=14114'
#     res = req.get(url)
#     text = res.text
#     soup = BeautifulSoup(text, 'lxml')
#     script_tag = soup.new_tag("script")
#     script_tag.string = script
#     soup.html.body.append(script_tag)
#
#     styles_tag = soup.new_tag('style')
#     styles_tag.string = styles
#     soup.html.head.insert(0,styles_tag)
#
#     div_soup = BeautifulSoup(block, 'lxml')
#     div_soup = div_soup.find('div', {"id": "oi-toolbar"})
#     soup.html.body.insert(0,div_soup)
#     # div_tag.string = block
#
#
#
#     return HttpResponse(str(soup))
    # if request.method == 'POST':
    #     name = request.POST['name']
    #     phone = request.POST['phone']
    #     test = Test(name=name, phone=phone)
    #     test.save()
    #     tests = Test.objects.all()
    #     content = {
    #         'tests': tests
    #     }
    #     return render(request, 'archive/test.html', content)
    # else:
    #     tests = Test.objects.all()
    #     content = {
    #         'tests': tests
    #     }
    # return render(request, 'archive/test.html', content)



