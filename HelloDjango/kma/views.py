from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Country, UserApiKey, CopyPasteText, Language
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .test_lead.kma_leads import KmaAPITest, KmaAPiError


@login_required
def default_webs(request):
    default_webs = CopyPasteText.objects.get(pk='default_webs')
    content = {
        'default_webs': default_webs,
    }
    return render(request, 'kma/default_webs.html', content)


@login_required
def discount_text(request):
    langs = Language.objects.exclude(discount_text__exact='').order_by('russian_name')
    content = {
        'langs': langs,
    }
    return render(request, 'kma/discount_text.html', content)

@login_required
def phones(requests):
    phones = Country.actual.prefetch_related('language').prefetch_related('curr').order_by('ru_full_name')
    test_integration_text = CopyPasteText.objects.get(pk='slava_test_rekl')
    try:
        user_api_key = UserApiKey.objects.get(user=requests.user)
        content = {
            'phones': phones,
            'user_api_key': user_api_key,
            'test_names': KmaAPITest.TEST_NAMES,
            'test_integration_text': test_integration_text,
        }
        return render(requests, 'kma/phones.html', content)
    except UserApiKey.DoesNotExist:
        content = {
            'phones': phones,
        }
        return render(requests, 'kma/phones.html', content)


@csrf_exempt
@login_required
def get_phone_code(request):
    try:
        country_code = request.GET['country_code']
        country_code = country_code.lower()
        phone_model = Country.objects.get(short=country_code)
        answer = {
            'success': True,
            'phone_code': phone_model.phone_code,
        }
    except BaseException as error:
        answer = {
            'success': False,
            'message': str(error)
        }
    return JsonResponse(answer, safe=False)

@login_required
def manual(request):
    return render(request, 'kma/manual/index.html')



@login_required
@csrf_exempt
def test_rekl(requests):
    try:
        countrys = requests.POST['countrys']
        countrys_list = countrys.split(',')
        test_name = requests.POST['test_name']
        offer_id = requests.POST['offer_id']
        country_phones = Country.get_country_phone(*countrys_list)
        user_api_key = UserApiKey.objects.get(user=requests.user)
        kma = KmaAPITest(user_api_key.token,offer_id, country_phones, test_name)
        kma.test_offer()
        answer = {
            'success': True,
            'link': kma.get_tracker_link(),
            'leads': kma.get_leads_data(),
        }
    except KmaAPiError as error:
        answer = {
            'success': False,
            'message': str(error.__doc__),
            'data': error.data,
        }
    return JsonResponse(answer, safe=False)

@login_required
@csrf_exempt
def get_offer(requests):
    try:
        offer_id = requests.POST['offer_id']
        user_api = UserApiKey.objects.get(user=requests.user)
        offer_data = KmaAPITest.get_offer(offer_id, user_api.token)
        answer = {
            'success': True,
            'offer_data': offer_data,
        }
    except BaseException as error:
        answer = {
            'success': False,
            'message': str(error)
        }
    return JsonResponse(answer)