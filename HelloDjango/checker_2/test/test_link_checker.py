from django.test import TestCase
from checker_2.checker_class.link_checker import LinkChecker
from checker_2.checker_class.checkers import Check
from checker_2.checker_class.land import Land
from kma.models import Country, Language

class LinkCheckerTest(TestCase):

    def setUp(self) -> None:
        self.land = Land(source_text='',url='https://google.com/')
        self.link_checker = LinkChecker('https://google.com/',1)

    def test_jeneral_status_info(self):
        messages = [{'status': Check.INFO }, {'status': Check.INFO}]
        self.link_checker.messages = messages
        result_status = self.link_checker.get_jeneral_check_status()
        self.assertEqual(result_status, Check.INFO)

    def test_jeneral_status_warning(self):
        messages = [{'status': Check.INFO }, {'status': Check.WARNING}]
        self.link_checker.messages = messages
        result_status = self.link_checker.get_jeneral_check_status()
        self.assertEqual(result_status, Check.WARNING)

    def test_jeneral_status_error(self):
        messages = [{'status': Check.INFO }, {'status': Check.WARNING}, {'status': Check.ERROR}]
        self.link_checker.messages = messages
        result_status = self.link_checker.get_jeneral_check_status()
        self.assertEqual(result_status, Check.ERROR)

    def test_get_current_country_model(self):
        self.land.country = 'ru'
        ru = Country.objects.create(ru_full_name='ru', iso='ru', phone='123')
        link_checker = LinkChecker('https://google.com/','1')
        link_checker.land = self.land
        for iso in 'by', 'en', 'xx':
            Country.objects.create(ru_full_name=iso, iso=iso, phone='123')
        curr_country = link_checker.current_country
        self.assertEqual(ru, curr_country)

    def test_get_langs_of_curr_country(self):
        self.land.country = 'ru'
        link_checker = LinkChecker('https://google.com/','1')
        link_checker.land = self.land
        #
        ru = Country.objects.create(ru_full_name='ru', iso='ru', phone='123')
        ru_lang = Language.objects.create(iso='ru')
        ru.language.add(ru_lang)
        for iso in 'en', 'by', 'ua':
            Language.objects.create(iso=iso)
        self.assertEqual(len(link_checker.current_languages), 1)
        self.assertTrue(ru_lang in link_checker.current_languages)

    def test_get_langs_of_curr_country_not_one_lang(self):
        self.land.country = 'ru'
        link_checker = LinkChecker('https://google.com/','1')
        link_checker.land = self.land
        #
        ru = Country.objects.create(ru_full_name='ru', iso='ru', phone='123')
        for iso in 'en', 'ru':
            lang = Language.objects.create(iso=iso)
            ru.language.add(lang)
        self.assertEqual(len(link_checker.current_languages), 2)




