import os

from kma.models import PhoneNumber, OfferPosition


def add_phones():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/Тесты - Лист13.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            short, phone, ru_full_name, phone_code, currency = line.split(',')
            model = PhoneNumber(
                short=short,
                phone=phone,
                ru_full_name=ru_full_name,
                phone_code=phone_code,
                currency=currency,
            )
            try:
                model.save()
                print(model)
            except BaseException:
                print(line)



def add_phone_codes():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/Тесты - Лист13.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            short, phone, ru_full_name, phone_code, currency = line.split(',')
            model = PhoneNumber.objects.get(short=short)
            model.currency = currency
            model.save()


def fix_offers_names():
    offers = OfferPosition.objects.all()
    for offer in offers:
        if '+' in offer.name and not offer.name.endswith('+'):
            print(offer)



def add_geo_words():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/geo_words.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            name, short, *templates = line.split(',')
            templates = set(templates)
            templates.remove('')
            print(name, short, templates)
            try:
                phone = PhoneNumber.objects.get(short=short)
                dic = {'templates': list(templates)}
                phone.words.update(dic)
                phone.save()
                print(phone)
            except:
                print(short, 'Not Found')


phones = PhoneNumber.objects.all()
for p in phones:
    print(p.short,p.words['templates'])



