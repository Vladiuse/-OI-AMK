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

    

# def add_offers():
#     with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/offers.csv') as file:
#         for line in file:
#             if line.endswith('\n'):
#                 line=line[:-1]
#             if line.endswith("'"):
#                 line = line[:-1]
#             offer = OfferPosition(name=line)
#             offer.save()
#     print('END')

# def add_offers():
#     error_count = 0
#     with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/offers.csv') as file:
#         for line in file:
#             offer, *_ = line.split('-')
#             offer = offer.strip()
#             try:
#                 new = OfferPosition(name=offer)
#                 new.save()
#                 print(new.name)
#             except:
#                 error_count += 1
#     print(error_count)

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
            name, short, *words = line.split(',')
            try:
                phone = PhoneNumber.objects.get(short=short)
                phone.words['words'] = words
                phone.save()
                print(phone.words)
            except:
                print(name, short)
