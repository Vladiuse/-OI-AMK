from kma.models import PhoneNumber

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