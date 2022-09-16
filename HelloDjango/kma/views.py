from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import DefaultWeb, PhoneNumber
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .test_lead.kma_leads import KmaAPITest
from .test_lead.kma_lead_errors import KmaAPiError


@login_required
def default_webs(request):
    webs = DefaultWeb.objects.all()
    content = {
        'webs': webs
    }
    return render(request, 'kma/default_webs.html', content)

@login_required
def phones(request):
    phones = PhoneNumber.objects.all().order_by('short')
    content = {
        'phones': phones,
    }
    return render(request, 'kma/phones.html', content)


@csrf_exempt
@login_required
def get_phone_code(request):
    try:
        country_code = request.GET['country_code']
        country_code = country_code.lower()
        phone_model = PhoneNumber.objects.get(short=country_code)
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
        print(test_name)
        country_phones = PhoneNumber.get_country_phone(*countrys_list)
        test_name = False if test_name != 'eng_test' else True
        kma = KmaAPITest(offer_id, country_phones, test_name)
        kma.test_offer()
        answer = {
            'success': True,
            'link': kma.get_tracker_link(),
        }
    except KmaAPiError as error:
        answer = {
            'success': False,
            'message': str(error.__doc__)
        }
    return JsonResponse(answer, safe=False)
