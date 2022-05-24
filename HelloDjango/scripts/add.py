from kma.models import PhoneNumber, OfferPosition


def add_phones():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/Тесты - Лист13.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            short, phone, ru_full_name = line.split(',')
            model = PhoneNumber(
                short=short,
                phone=phone,
                ru_full_name=ru_full_name
            )
            try:
                model.save()
            except BaseException:
                pass

def add_phone_codes():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/Тесты - Лист13.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line = line[:-1]
            short, phone, ru_full_name, phone_code, currency = line.split(',')
            model = PhoneNumber.objects.get(short=short)
            model.currency = currency
            model.save()
    

def add_offers():
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/offers.csv') as file:
        for line in file:
            if line.endswith('\n'):
                line=line[:-1]
            if line.endswith("'"):
                line = line[:-1]
            offer = OfferPosition(name=line)
            offer.save()
    print('END')

add_phone_codes()