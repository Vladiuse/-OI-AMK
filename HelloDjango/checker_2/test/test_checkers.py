from django.test import TestCase
from checker_2.checker_class.checkers import PhoneCountryMask, Check, Currency,OffersInLand, Dates,\
    GeoWords, CountyLang, PhpTempVar, JsVarsInText, StarCharInText, HtmlPeaceOfCodeInText, SpaceCharInTest , \
    RekvOnPage

from kma.models import Country, KmaCurrency, OfferPosition, Language
from checker_2.checker_class.kma_land import KMALand
from checker_2.checker_class.link_checker import LinkChecker
from unittest.mock import Mock
from datetime import date as _date
from datetime import datetime, timedelta
from bs4 import BeautifulSoup




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

    def test_add_messages_no_offers(self):
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


class DatesCheckTest(TestCase):


    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.land.dates = []
        self.land.years = []
        self.checker = Dates(self.land, self.link_checker)

    def test_is_incorrect_date_format_no(self):
        for correct_date in '20.20.2020', '2020.12.10', '20.10.10':
            self.assertFalse(Dates.is_incorrect_date_format(correct_date))

    def test_test_is_incorrect_date_format(self):
        for incorrect_date in '20\\20\\2020', '2020/12/10':
            self.assertTrue(Dates.is_incorrect_date_format(incorrect_date))

    def test_make_date_point_delimeter(self):
        dates_to_test = ['20\\20\\2020','20/20/2020', '20.20.2020']
        for date in dates_to_test:
            self.assertEqual(self.checker.make_date_point_delimeter(date), '20.20.2020')

    def test_make_date_Y(self):
        result = self.checker.make_date('10.10.2020')
        self.assertTrue(isinstance(result, _date))

    def test_make_date_y(self):
        result = self.checker.make_date('10.10.20')
        self.assertTrue(isinstance(result, _date))

    def test_not_create_date(self):
        result = self.checker.make_date('1010.10.20')
        self.assertFalse(result)

    def test_is_date_incorrect_correct(self):
        self.assertFalse(self.checker.is_date_incorrect('10.10.20'))

    def test_is_date_incorrect_incorrect_day(self):
        self.assertTrue(self.checker.is_date_incorrect('40.10.20'))

    def test_is_date_incorrect_incorrect_day(self):
        self.assertTrue(self.checker.is_date_incorrect('10.13.20'))

    def test_is_date_from_future_yes(self):
        for format in '%d.%m.%Y', '%d.%m.%y':
            tomorrow = (datetime.today() + timedelta(days=1)).strftime(format)
            self.assertTrue(self.checker.is_date_from_future(tomorrow))

    def test_is_date_from_future_not(self):
        for format in '%d.%m.%Y', '%d.%m.%y':
            today = datetime.today().strftime(format)
            self.assertFalse(self.checker.is_date_from_future(today))

    def test_get_earliest_date(self):
        dates = ['10.10.10', '10/12/20', '10.10.2012', '10\\10\\2012', '123']
        self.assertEqual(self.checker.get_earliest_date(dates), '10.10.2010')


    def test_process_dates(self):
        tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d.%m.%y')
        self.checker.dates = ['10\\10\\10', tomorrow, '20.20.20']
        self.checker.process_dates()
        self.assertEqual(self.checker.incorrect_format_dates, ['10\\10\\10'])
        self.assertEqual(self.checker.incorrect_dates, ['20.20.20'])
        self.assertEqual(self.checker.earliest_date, '10.10.2010')
        self.assertEqual(self.checker.future_dates, [tomorrow])

    def test_add_messages_yesrs(self):
        self.checker.years = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.ALL_YEARS)

    def test_add_messages_all_dates(self):
        self.checker.dates = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.ALL_DATES)

    def test_add_messages_incorrect_format_dates(self):
        self.checker.incorrect_format_dates = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.INCORRECT_DATE_FORMAT)

    def test_add_messages_incorrect_format_dates(self):
        self.checker.incorrect_dates = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.INCORRECT_DATE)

    def test_add_messages_future_dates(self):
        self.checker.future_dates = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.FUTURE_DATE)

    def test_add_messages_incorrect_earliest_date(self):
        self.checker.earliest_date = ['1']
        self.checker.add_messages()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], Dates.EARLIEST_DATE)


class GeoWordsTest(TestCase):

    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.link_checker.countrys = Country.objects.all()
        # create
        ru_words = {"words": [], "templates": ['росси', 'русск']}
        self.RU = Country.objects.create(iso='ru', ru_full_name='russia',words=ru_words)
        by_words = {"words": [], "templates": ['беларус',]}
        self.BY = Country.objects.create(iso='by', ru_full_name='belarus', words=by_words)
        ua_words = {"words": [], "templates": ['украин',]}
        self.UA = Country.objects.create(iso='ua', ru_full_name='ucraine', words=ua_words)

        self.link_checker.current_country = self.RU

        self.checker = GeoWords(self.land, self.link_checker)


    def test_func_currect_country_words(self):
        self.land.human_text_lower = 'ntrc русский ыа российский'
        self.checker.search_by_template()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertTrue(GeoWords.CURRENT_COUNTRY in mess['text'])

    def test_func_not_currect_country_words(self):
        self.land.human_text_lower = 'ntrc беларус ыа буларусский'
        self.checker.search_by_template()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertTrue(GeoWords.INCORECT_COUNTRY in mess['text'])

    def test_func_not_currect_country_words_two(self):
        self.land.human_text_lower = 'ntrc беларус ыа украинский выфв '
        self.checker.search_by_template()
        self.assertEqual(len(self.checker.messages), 2)

    def test_no_found(self):
        self.land.human_text_lower = ''
        self.checker.search_by_template()
        self.assertEqual(len(self.checker.messages), 0)


    def test_clead_word(self):
        words = [
            ['__word++','word'],
            ['11word11', 'word'],
            ['- word;.', 'word'],
        ]
        for word, res in words:
            self.assertEqual(self.checker.clean_word(word), res)



class CountyLangTest(TestCase):

    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()

        self.checker = CountyLang(self.land, self.link_checker)
        self.land.language = 'ru'
        self.RU = Country.objects.create(iso='ru', ru_full_name='russia', phone_code='7')
        self.BY = Country.objects.create(iso='by', ru_full_name='belarus', phone_code='375')
        self.UA = Country.objects.create(iso='ua', ru_full_name='ucraine', phone_code='380')

        self.RU_LANG = Language.objects.create(iso='ru')
        self.BY_LANG = Language.objects.create(iso='by')
        self.UA_LANG_1 = Language.objects.create(iso='u1')
        self.UA_LANG_2 = Language.objects.create(iso='u2')

        self.RU.language.add(self.RU_LANG)
        self.BY.language.add(self.BY_LANG)
        self.UA.language.add(self.UA_LANG_1, self.UA_LANG_2)

        self.link_checker.countrys = Country.objects.all()
        self.link_checker.current_country = self.RU
        self.link_checker.current_languages = self.RU.language.all()

    def test_correct_lang(self):
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)


    def test_lang_incorrect(self):
        self.link_checker.current_country = self.BY
        self.link_checker.current_languages = self.BY.language.all()
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertTrue(CountyLang.INCORRECT_LANG in mess['text'])

    def test_need_langs_more_one(self):
        self.link_checker.current_country = self.UA
        self.link_checker.current_languages = self.UA.language.all()
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(len(mess['items']), 2)


class PhpTempVartest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = PhpTempVar(self.land, self.link_checker)

    def test_clean_text(self):
        self.land.human_text = ''
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)


    def test_find_php_template(self):
        self.land.human_text = 'some test {$php_var.sads} dasdasd'
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], PhpTempVar.VARIABLE_ON_SITE)


class JsVarsInTexttest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = JsVarsInText(self.land, self.link_checker)
        self.land.human_text_lower = ''
        self.land.human_text = ''

    def test_clean_text(self):
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)

    def test_process(self):
        self.land.human_text_lower = 'das undefined dsad null sdad'
        self.land.human_text = 'das undefined dsad null sdad NaN dsadasd'
        self.checker.process()
        self.assertEqual(len(self.checker.vars_in_text), 3)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], JsVarsInText.JS_VARIABLE_IN_TEXT)


    def test_search_undefined(self):
        self.land.human_text_lower = 'some text undefined sdsad'
        self.checker.search_undefined()
        self.assertTrue(JsVarsInText.UNDEFINED in self.checker.vars_in_text)

    def test_search_nan(self):
        self.land.human_text = 'some NaN undefined sdsad'
        self.checker.search_nan()
        self.assertTrue(JsVarsInText.NaN in self.checker.vars_in_text)

    def test_search_nan_lower(self):
        self.land.human_text = 'some nan undefined sdsad'
        self.checker.search_nan()
        self.assertTrue(JsVarsInText.NaN not in self.checker.vars_in_text)

    def test_search_null(self):
        self.land.human_text_lower = 'some text null sdsad'
        self.checker.search_null()
        self.assertTrue(JsVarsInText.NULL in self.checker.vars_in_text)

    def test_add_messages(self):
        self.checker.vars_in_text = {JsVarsInText.NULL, JsVarsInText.UNDEFINED, JsVarsInText.NaN}
        self.checker.add_messages()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], JsVarsInText.JS_VARIABLE_IN_TEXT)



class StarCharInTextTest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = StarCharInText(self.land, self.link_checker)

    def test_full_price_no_star(self):
        self.land.human_text = ''
        self.land.discount_type = KMALand.FULL_PRICE
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)

    def test_full_price_star_in_text(self):
        self.land.human_text = 'dsads dsad * sdad'
        self.land.discount_type = KMALand.FULL_PRICE
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], StarCharInText.STAR_ON_SITE)

    def test_low_price_no_star(self):
        self.land.human_text = ''
        self.land.discount_type = KMALand.LOW_PRICE
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], StarCharInText.STAR_NOT_IN_TEXT)

    def test_low_price_star_in_text(self):
        self.land.human_text = 'dsads dsad * sdad'
        self.land.discount_type = KMALand.LOW_PRICE
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)




class HtmlPeaceOfCodeInTextTest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = HtmlPeaceOfCodeInText(self.land, self.link_checker)

    def test_no_found(self):
        self.land.human_text = ''
        self.checker.process()
        self.assertEqual(len(self.checker.messages),0)

    def test_find_comment_peace_1(self):
        self.land.human_text = 'dasdas <!- dsadsadasd'
        self.checker.process()
        self.assertEqual(len(self.checker.messages),1)
        mess = self.checker.messages[0]
        self.assertTrue('<!-' in  mess['items'])

    def test_find_comment_peace_2(self):
        self.land.human_text = 'dasdas --> dsadsadasd'
        self.checker.process()
        self.assertEqual(len(self.checker.messages),1)
        mess = self.checker.messages[0]
        self.assertTrue('-->' in  mess['items'])

    def test_correct_message_text(self):
        self.land.human_text = 'dasdas --> dsadsadasd'
        self.checker.process()
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], HtmlPeaceOfCodeInText.HTML_PEACE_IN_TEXT)




class SpaceCharInTestTest(TestCase):

    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = SpaceCharInTest(self.land, self.link_checker)

    def test_cleand_text(self):
        self.land.human_text_lower = ''
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)

    def test_space_before_end_of_sentence(self):
        examples = [
            'some testds . dasd ',
            'some testds ! dasd ',
            'some testds ? dasd ',
        ]
        for text in examples:
            self.land.human_text_lower = text
            self.checker.space_before_end_of_sentence()
            self.assertEqual(len(self.checker.messages), 1)
            mess = self.checker.messages[0]
            self.assertEqual(mess['text'], SpaceCharInTest.EXTRA_SPACE_SENTENCE)
            self.assertEqual(len(mess['items']), 1)
            self.checker.messages.clear()



class RekvOnPageTest(TestCase):
    def setUp(self) -> None:
        self.land = Mock()
        self.link_checker = Mock()
        self.checker = RekvOnPage(self.land, self.link_checker)

    def test_no_revk_land_type(self):
        self.land.land_type = KMALand.LAND
        text = ''
        self.land.soup = BeautifulSoup(text, 'lxml')
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 1)
        mess = self.checker.messages[0]
        self.assertEqual(mess['text'], RekvOnPage.NO_REKV)

    def test_find_recv_land_type(self):
        self.land.land_type = KMALand.LAND
        text = 'dasd dssad das '
        self.land.soup = BeautifulSoup(text, 'lxml')
        rekv = self.land.soup.new_tag(KMALand.REQUISITES_TAG)
        rekv.string = 'sdasdsa dsada'
        self.land.soup.html.body.append(rekv)
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)

    def test_no_rekv_pre_land_type(self):
        self.land.land_type = KMALand.PRE_LAND
        text = ''
        self.land.soup = BeautifulSoup(text, 'lxml')
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)

    def test_find_recv_preland_type(self):
        self.land.land_type = KMALand.PRE_LAND
        text = 'dasd dssad das '
        self.land.soup = BeautifulSoup(text, 'lxml')
        rekv = self.land.soup.new_tag(KMALand.REQUISITES_TAG)
        rekv.string = 'sdasdsa dsada'
        self.land.soup.html.body.append(rekv)
        self.checker.process()
        self.assertEqual(len(self.checker.messages), 0)






