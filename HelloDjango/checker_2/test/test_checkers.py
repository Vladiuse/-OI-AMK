from django.test import TestCase
from checker_2.checker_class.checkers import PhoneCountryMask, Check, Currency,OffersInLand
from kma.models import Country, KmaCurrency, OfferPosition
from checker_2.checker_class.kma_land import KMALand
from checker_2.checker_class.link_checker import LinkChecker
from unittest.mock import Mock




class PhoneCountryMaskTest(TestCase):

    def setUp(self) -> None:
        self.RU = Country.objects.create(iso='ru', ru_full_name='russia', phone_code='7')
        self.BY = Country.objects.create(iso='by', ru_full_name='belarus', phone_code='375')
        self.UA = Country.objects.create(iso='ua', ru_full_name='ucraine', phone_code='380')
        self.land = Mock()
        self.link_checker = Mock()
        self.link_checker.current_country = self.RU
        #
        self.link_checker.countrys = Country.objects.all()

    def test_find_countries_phone_code_on_land_no_found(self):
        self.land.human_text_lower = 'some text dodsd'
        checker = PhoneCountryMask(self.land, self.link_checker)
        countries = checker.find_countries_phone_code_on_land()
        self.assertEqual(len(countries), 0)

    def test_find_countries_phone_code_on_land_find_current(self):
        self.land.human_text_lower = 'some text +7 dodsd'
        checker = PhoneCountryMask(self.land, self.link_checker)
        countries = checker.find_countries_phone_code_on_land()
        self.assertEqual(len(countries), 1)

    def test_test_checkers_find_incorrect_codes(self):
        self.land.human_text_lower = 'some text +380 dodsd'
        checker = PhoneCountryMask(self.land, self.link_checker)
        countries = checker.find_countries_phone_code_on_land()
        self.assertEqual(len(countries), 1)
        self.assertTrue(self.UA in countries)

    def test_test_checkers_find_two_incorrect(self):
        self.land.human_text_lower = 'some text +380 dodsd +375 dfsd'
        checker = PhoneCountryMask(self.land, self.link_checker)
        countries = checker.find_countries_phone_code_on_land()
        self.assertEqual(len(countries), 2)
        self.assertTrue(self.UA in countries)
        self.assertTrue(self.BY in countries)

    def test_separate_correct_incorrect_only_one_1(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.separate_countries_by_error_type([self.RU])
        self.assertTrue(checker.is_curr_country_phone_on_land)

    def test_separate_correct_and_not(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.separate_countries_by_error_type([self.RU, self.BY])
        self.assertTrue(checker.is_curr_country_phone_on_land)
        self.assertTrue(len(checker.incorrect_countries), 1)
        self.assertTrue(self.BY in checker.incorrect_countries)

    def test_separate_only_incorrect(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.separate_countries_by_error_type([self.UA, self.BY])
        self.assertFalse(checker.is_curr_country_phone_on_land)
        self.assertTrue(len(checker.incorrect_countries), 2)
        self.assertTrue(self.BY in checker.incorrect_countries)
        self.assertTrue(self.UA in checker.incorrect_countries)

    def test_add_mess_current_country(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.is_curr_country_phone_on_land = True
        checker.add_messages()
        self.assertEqual(len(checker.messages), 1)
        self.assertEqual(checker.messages[0]['status'],Check.WARNING)

    def test_add_mess_incorrect(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.incorrect_countries = [self.BY]
        checker.add_messages()
        self.assertEqual(len(checker.messages), 1)
        self.assertEqual(checker.messages[0]['status'],Check.ERROR)

    def test_messages_add_both(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.is_curr_country_phone_on_land = True
        checker.incorrect_countries = [self.BY]
        checker.add_messages()
        self.assertEqual(len(checker.messages), 2)

    def test_corect_message_text_correct(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.is_curr_country_phone_on_land = True
        checker.add_messages()
        mess = checker.messages[0]
        self.assertTrue('+'+self.RU.phone_code in mess['items'])

    def test_corect_message_text_incorrect(self):
        checker = PhoneCountryMask(self.land, self.link_checker)
        checker.incorrect_countries = [self.BY]
        checker.add_messages()
        mess = checker.messages[0]
        self.assertTrue('+'+self.BY.phone_code in mess['items'])




class CurrencyTest(TestCase):

    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.link_checker.currencys = KmaCurrency.actual.prefetch_related('country_set').all()
        self.RU = Country.objects.create(iso='ru', ru_full_name='russia', phone_code='7')
        self.link_checker.current_country = self.RU
        #create
        self.RUB = KmaCurrency.objects.create(name='some', iso='rub', iso_3366='rus', kma_code='руб.')
        self.BYN = KmaCurrency.objects.create(name='some2', iso='byn', iso_3366='bnr', kma_code='бел')
        self.USD = KmaCurrency.objects.create(name='some3', iso='usd', iso_3366='usa',)

        self.BY = Country.objects.create(iso='by', ru_full_name='belarus', phone_code='375')
        self.UA = Country.objects.create(iso='ua', ru_full_name='ucraine', phone_code='380')

        self.RU.curr.add(self.RUB)
        self.BY.curr.add(self.BYN)
        self.UA.curr.add(self.USD)



        self.check = Currency(self.land, self.link_checker)


    def test_no_fount(self):
        self.land.human_text_lower = 'some text dodsd'
        self.check.find_currencys()
        self.assertFalse(self.check.incorrect_currencys)
        self.assertFalse(self.check.incorrect_cyrrencys_code)

    def test_find_correct_curr(self):
        self.land.human_text_lower = 'some text dodsd руб. dasdas'
        self.check.find_currencys()
        self.assertEqual(self.check.is_find_current_currency, 'РУБ.')

    def test_find_icorect_curr_code(self):
        self.land.human_text_lower = 'some text dodsd rub dasdas  rus  dsd'
        self.check.find_currencys()
        self.assertTrue(len(self.check.incorrect_cyrrencys_code), 2)
        self.assertTrue('RUB' in self.check.incorrect_cyrrencys_code)
        self.assertTrue('RUS' in self.check.incorrect_cyrrencys_code)

    def find_incorrect_country_curr(self):
        self.land.human_text_lower = 'some usa dodsd uds dasdas  rus  byn csdasd bnr'
        self.check.find_currencys()
        self.assertTrue(len(self.check.incorrect_currencys), 4)


    def test_add_mess_no_currs_found(self):
        self.check.add_messages()
        self.assertTrue(len(self.check.messages), 1)
        mess = self.check.messages[0]
        self.assertEqual(mess['text'], Currency.NO_CURRENCIES)

    def test_add_mess_curr_found(self):
        self.check.is_find_current_currency = 'XXX'
        self.check.add_messages()
        self.assertTrue(len(self.check.messages), 1)
        mess = self.check.messages[0]
        self.assertEqual(mess['text'], Currency.CURR_FOUND)

    def test_mess_incorrect_curr_code(self):
        self.check.incorrect_cyrrencys_code.add('XXX')
        self.check.add_messages()
        self.assertTrue(len(self.check.messages), 1)
        mess = self.check.messages[0]
        self.assertEqual(mess['text'], Currency.INCORRECT_CURE_CODE)

    def test_add_medd_incorrect_currency(self):
        self.check.incorrect_currencys.add('XXX')
        self.check.add_messages()
        self.assertTrue(len(self.check.messages), 1)
        mess = self.check.messages[0]
        self.assertEqual(mess['text'], Currency.INCORRECT_COUNTRY_CURRENCY)

    def test_find_all_errors(self):
        self.check.is_find_current_currency = 'XXX'
        self.check.incorrect_cyrrencys_code.add('XXX')
        self.check.incorrect_currencys.add('XXX')
        self.check.add_messages()
        self.assertTrue(len(self.check.messages), 3)


class OffersInLandTest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.link_checker.offers = OfferPosition.objects.all()
        self.link_checker.land_data = dict()
        self.checker = OffersInLand(self.land, self.link_checker)

        # create
        for name in 'offer', 'two words':
            OfferPosition.objects.create(name=name)

    def test_no_offers_found(self):
        self.land.human_text_lower = ''
        self.checker.find_offers()
        self.assertEqual(len(self.checker.offers_in_land), 0)

    def test_find_some_offers(self):
        self.land.human_text_lower = 'some text offer aaaaa two words dsadas'
        self.checker.find_offers()
        self.assertEqual(len(self.checker.offers_in_land), 2)

    def test_add_mesages_no_offers(self):
        self.checker.add_messages()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'],OffersInLand.NO_OFFER_FIND)

    def test_add_mess_more_than_one_found(self):
        self.checker.offers_in_land = {'1', '2'}
        self.checker.add_messages()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'],OffersInLand.MORE_ONE_OFFER_FOUND)

    def test_add_to_link_checker_find_offer(self):
        self.checker.offers_in_land = {'1',}
        self.checker.return_find_offer()
        self.assertEqual(self.link_checker.land_data['offer_name'], '1')

    def test_not_add_to_link_checker_find_offer(self):
        self.checker.return_find_offer()
        self.assertTrue('offer_name' not in self.link_checker.land_data)




















