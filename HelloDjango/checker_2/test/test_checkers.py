from django.test import TestCase
from checker_2.checker_class.checkers import PhoneCountryMask, Check
from kma.models import Country
from checker_2.checker_class.kma_land import KMALand
from checker_2.checker_class.link_checker import LinkChecker
from unittest.mock import Mock


def get_kma_land(source_text=''):
    try:
        kma_land = KMALand(source_text=source_text, url='')
    except BaseException:
        pass
    return kma_land


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









