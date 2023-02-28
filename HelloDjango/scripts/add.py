import csv
# from kma.models import Country


def add_countrys():
    path = '/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/db_data/all_countrys.csv'
    with open(path) as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            name, iso, iso3, *other = line
            iso, iso3 = iso.lower(), iso3.lower()
            try:
                country = Country.objects.get(pk=iso)
                country.iso3 = iso3
            except:
                country = Country(iso=iso, iso3=iso3, ru_full_name=name)
                print(country)
            country.save()


def add_currencys():
    path = '/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/scripts/db_data/all_currencys.csv'
    s = set()
    with open(path) as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            name, countrys, iso, iso3, uni_char = line

add_currencys()