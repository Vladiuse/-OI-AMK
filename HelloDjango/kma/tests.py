from django.test import TestCase
from .models import Country, City, Currency, KmaCurrency

class CountryTest(TestCase):

    def test_actual_country_manager(self):
        country_with_phone = Country.objects.create(iso='ru', phone='123', ru_full_name='123')
        not_actual_country = Country.objects.create(iso='xx', ru_full_name='sdasd')
        actual = Country.actual.all()
        self.assertTrue(country_with_phone in actual)
        self.assertTrue(not_actual_country not in actual)


class CityTest(TestCase):

    def setUp(self) -> None:
        self.RU = Country.objects.create(iso='ru', ru_full_name='123')

    def test_citys_for_text_search(self):
        use_in_serach = City.objects.create(name='xx', country=self.RU)
        not_use_in_search = City.objects.create(name='yy', country=self.RU, use_in_text_search=False)
        citys = City.text_search.all()
        self.assertTrue(use_in_serach in citys)
        self.assertTrue(not_use_in_search not in citys)



class CurrencyTest(TestCase):
    def setUp(self) -> None:
        self.RU = Country.objects.create(iso='ru', ru_full_name='123')

    def test_not_actual_currency_manager(self):
        actual_curr = Currency.objects.create(iso='xx', name='xx')
        not_actual = Currency.objects.create(iso='yy', name='yy')
        self.RU.curr.add(actual_curr)
        currencys = Currency.actual.all()
        self.assertTrue(actual_curr in currencys)
        self.assertTrue(not_actual not in currencys)

    def test_not_actual_currency_manager_few_currs(self):
        actual = []
        for name in ['xx', 'yy', 'zz']:
            c = Currency.objects.create(iso=name, name=name)
            actual.append(c)
            self.RU.curr.add(c)
        for name in ['11', '22', '33']:
            Currency.objects.create(iso=name, name=name)
        currencys = Currency.actual.all()
        self.assertTrue(len(currencys), 3)
        for curr in actual:
            self.assertTrue(curr in currencys)


class KmaCurrencyTest(TestCase):

    def setUp(self) -> None:
        self.no_kma_curr = KmaCurrency.objects.create(name='belarus', iso='byn', iso_3366='bnr')
        self.kma_curr = KmaCurrency.objects.create(name='russia', iso='rub', iso_3366='rus', kma_code='руб')

    def test_no_kma_curr_main_curr(self):
        self.assertEqual(self.no_kma_curr.main_curr, 'byn')

    def test_no_kma_curr_other_curs(self):
        other = self.no_kma_curr.other_currs
        self.assertEqual(len(other), 1)
        self.assertTrue('bnr' in other)

    def test_kma_currency_main_curr(self):
        self.assertEqual(self.kma_curr.main_curr, 'руб')

    def test_kma_curr_other_curs(self):
        other = self.kma_curr.other_currs
        self.assertEqual(other, ['rub', 'rus'])





