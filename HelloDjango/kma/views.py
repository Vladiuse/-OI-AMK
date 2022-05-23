from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import DefaultWeb, PhoneNumber
from django.views.decorators.csrf import csrf_exempt


def default_webs(request):
    webs = DefaultWeb.objects.all()
    content = {
        'webs': webs
    }
    return render(request, 'kma/default_webs.html', content)

def phones(request):
    phones = PhoneNumber.objects.all().order_by('short')
    content = {
        'phones': phones,
    }
    return render(request, 'kma/phones.html', content)


@csrf_exempt
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
