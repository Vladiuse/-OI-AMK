from datetime import datetime
import re


class Check:
    DESCRIPTION = 'No'
    KEY_NAME = 'No'

    WARNING = 'warning'
    ERROR = 'error'
    INFO = 'info'

    STATUS_SET = {}

    def __init__(self, land, url_checker,text_finder_result):
        self.land = land
        self.url_checker = url_checker
        self.text_finder_result = text_finder_result
        self.errors = set()
        self.info = set()
        self.messages = list()

    def process(self):
        pass

    def add_mess(self, message_text, *args):
        message = {
            'text': message_text,
            'status': self.STATUS_SET[message_text],
            'items': args,
        }
        self.messages.append(message)


class PhoneCountryMask(Check):
    DESCRIPTION = 'Поиск моб кодов стран'
    KEY_NAME = 'phone_country_code'

    MASK_ON_LAND = 'Найден моб код'
    INCORECT_MASK_ON_LAND = 'Найден моб код другого гео'

    STATUS_SET = {
        MASK_ON_LAND: Check.WARNING,
        INCORECT_MASK_ON_LAND: Check.ERROR,
    }

    def process(self):
        phone_codes_on_land = self.text_finder_result['phone_codes']
        country_phone_code = '+' + self.land.phone_code
        for code in phone_codes_on_land:
            if code == country_phone_code:
                self.add_mess(self.MASK_ON_LAND, code)
            else:
                self.add_mess(self.INCORECT_MASK_ON_LAND, code)


class Currency(Check):
    DESCRIPTION = 'Поиск валют по тексту'
    KEY_NAME = 'currencies_on_land'

    NO_CURRENCIES = 'Валюты не найдены'
    MORE_ONE_CURRENCIES = 'Найдена валюта другой страны'
    ONE_CURR_FOUND = 'Найденая валюта'

    STATUS_SET = {
        NO_CURRENCIES: Check.WARNING,
        MORE_ONE_CURRENCIES: Check.ERROR,
        ONE_CURR_FOUND: Check.INFO,
    }

    def process(self):
        currency = self.land.curr.lower()
        currencies_on_land = self.text_finder_result['currencys']
        if '' in currencies_on_land:
            currencies_on_land.remove('')
        if not currencies_on_land:
            self.add_mess(self.NO_CURRENCIES)
        for curr in currencies_on_land:
            if curr == currency:
                self.add_mess(self.ONE_CURR_FOUND, curr.upper())
            if curr != currency and curr not in ['all', 'try', 'gel', 'peso']:
                self.add_mess(self.MORE_ONE_CURRENCIES, curr)


class OffersInLand(Check):
    DESCRIPTION = 'Поиск офферов по тексту'
    KEY_NAME = 'offers_on_land'

    NO_OFFER_FIND = 'Не найден не один оффер'
    MORE_ONE_OFFER_FOUND = 'Найдено больше одного оффера'
    ONE_OFFER_FOUND = 'Оффер'

    STATUS_SET = {
        NO_OFFER_FIND: Check.WARNING,
        MORE_ONE_OFFER_FOUND: Check.ERROR,
        ONE_OFFER_FOUND: Check.INFO
    }

    def process(self):
        offers = self.url_checker.offers
        offers_in_land = list()
        for offer in offers:
            if re.search('\W'+offer.name+'\W', self.land.human_text_lower):
                offers_in_land.append(str(offer))
        # offers_in_land = self.text_finder_result['offers']
        if not offers_in_land:
            self.add_mess(self.NO_OFFER_FIND)
        if len(offers_in_land) > 1:
            self.add_mess(self.MORE_ONE_OFFER_FOUND, *offers_in_land)
        if len(offers_in_land) == 1:
            self.add_mess(self.ONE_OFFER_FOUND, *offers_in_land)


class Dates(Check):
    DESCRIPTION = 'Поиск дат по тексту'
    KEY_NAME = 'dates_on_land'

    ALL_YEARS = 'Года'
    ALL_DATES = 'Даты'
    INCORRECT_DATE_FORMAT = 'Некоректный формат'
    INCORRECT_DATE = 'Некоректный день или месяц'
    FUTURE_DATE = 'Дата из будущего'
    EARLIEST_DATE = 'Самая ранняя дата'

    STATUS_SET = {
        ALL_YEARS: Check.INFO,
        ALL_DATES: Check.INFO,
        EARLIEST_DATE: Check.INFO,
        INCORRECT_DATE_FORMAT: Check.WARNING,
        INCORRECT_DATE: Check.ERROR,
        FUTURE_DATE: Check.ERROR,
    }

    def process(self):
        dates = self.land.dates
        years = self.land.years
        if years:
            years.sort(key=lambda x: int(x))
            self.add_mess(self.ALL_YEARS, *years)
        if dates:
            self.add_mess(self.ALL_DATES, *dates)

        incorrect_format_dates = list(filter(self.is_incorrect_date_format, dates))
        if incorrect_format_dates:
            self.add_mess(self.INCORRECT_DATE_FORMAT, *incorrect_format_dates)

        incorrect_dates = list(filter(self.is_date_incorrect, dates))
        if incorrect_dates:
            self.add_mess(self.INCORRECT_DATE, *incorrect_dates)

        future_dates = list(filter(self.is_date_from_future, dates))
        if future_dates:
            self.add_mess(self.FUTURE_DATE, *future_dates)
        earliest_date = self.get_earliest_date(dates)
        if earliest_date:
            self.add_mess(self.EARLIEST_DATE, earliest_date)

    @staticmethod
    def is_incorrect_date_format(date):
        chars = '-\\/'
        for char in chars:
            if char in date:
                return True

    @staticmethod
    def make_date_point_delimeter(date: str) -> str:
        """Привести дату к формату хх.хх.хх"""
        new_date = ''
        for char in date:
            if char.isdigit():
                new_date += char
            else:
                new_date += '.'
        return new_date

    @staticmethod
    def make_date(date: str):
        """Создать обьект даты или вернуть None"""
        date = Dates.make_date_point_delimeter(date)
        correct_date = None
        for year_format in 'yY':
            try:
                correct_date = datetime.strptime(date, '%d.%m.%' + year_format).date()
            except ValueError:
                pass
        return correct_date

    @staticmethod
    def is_date_incorrect(date):
        """Правильный ли день и месяц у даты"""
        return not bool(Dates.make_date(date))

    @staticmethod
    def is_date_from_future(date: str):
        """Явзяеться ли дата датой из будущего"""
        date = Dates.make_date(date)
        if date:
            today = datetime.today().date()
            if date > today:
                return True
        return False

    @staticmethod
    def get_earliest_date(dates: list):
        dates_obj = []
        for date in dates:
            date = Dates.make_date(date)
            if date:
                dates_obj.append(date)
        dates_obj.sort()
        if dates_obj:
            earliest_date = dates_obj[0]
            return earliest_date.strftime('%d.%m.%Y')


class GeoWords(Check):
    DESCRIPTION = 'Поиск стран по тексту'
    KEY_NAME = 'countrys_in_land'

    ALL_COUNTRYS = 'Найдена страна'
    INCORECT_COUNTRY = 'Другие страны'

    STATUS_SET = {
        ALL_COUNTRYS: Check.WARNING,
        INCORECT_COUNTRY: Check.ERROR,
    }

    def process(self):
        countrys = self.text_finder_result['geo_words_templates']
        for iso, countrys in countrys.items():
            countrys.insert(0, iso.upper())
            if self.land.country == iso:
                self.add_mess(self.ALL_COUNTRYS, *countrys)
            else:
                self.add_mess(self.INCORECT_COUNTRY, *countrys)


class CountyLang(Check):
    DESCRIPTION = 'Правильный язык сайта'
    KEY_NAME = 'country_lang'

    INCORRECT_LANG = 'Указан не вырный язык сайта'

    STATUS_SET = {
        INCORRECT_LANG: Check.WARNING,
    }

    def process(self):
        site_lang = self.land.language
        list_of_langs = self.land.available_langs.split(',')
        if site_lang not in self.land.available_langs:
            self.add_mess(self.INCORRECT_LANG, 'должен быть', *list_of_langs)


class PhpTempVar(Check):
    DESCRIPTION = 'Поиск переменных шаблонов PHP'
    KEY_NAME = 'php_template_vars'

    VARIABLE_ON_SITE = 'Найдена переменная шаблона'

    STATUS_SET = {
        VARIABLE_ON_SITE: Check.ERROR,
    }

    def process(self):
        land_human_text = self.land.get_human_land_text()
        var_templates = re.findall(r'\{\$[\S.]{1,40}}', land_human_text)
        if var_templates:
            self.add_mess(self.VARIABLE_ON_SITE, *var_templates)


class UndefinedInText(Check):
    DESCRIPTION = 'Поиск undefined по тектсу'
    KEY_NAME = 'undefined_in_text'

    UNDEFINED_IN_TEXT = 'Найден undefined в тексте'
    STATUS_SET = {
        UNDEFINED_IN_TEXT: Check.ERROR,
    }

    def process(self):

        land_human_text = self.land.get_human_land_text()
        print(self.land.human_text)
        if 'undefined' in land_human_text:
            self.add_mess(self.UNDEFINED_IN_TEXT)


class StarCharInText(Check):
    DESCRIPTION = 'Поиск * в текста'
    KEY_NAME = 'star_in_text'

    VARIABLE_ON_SITE = 'Найдена * в тексте'

    STATUS_SET = {
        VARIABLE_ON_SITE: Check.WARNING,
    }
    STAR_CHAR = '*'

    def process(self):
        land_human_text = self.land.get_human_land_text()
        if float(self.land.discount) <= 50 and self.STAR_CHAR in land_human_text:
            self.add_mess(self.VARIABLE_ON_SITE)


class HtmlPeaceOfCodeInText(Check):
    # супчик выкидывает их из текста(
    DESCRIPTION = 'Поиск элементов кода html'
    KEY_NAME = 'html_code_peace_in_text'

    HTML_PEACE_IN_TEXT = 'Элементы html кода найдены в тексте'
    STATUS_SET = {
        HTML_PEACE_IN_TEXT: Check.WARNING,
    }

    def process(self):
        land_human_text = self.land.get_human_land_text()
        html_peaces = set(re.findall(r'<!?-?|-{0,2}>', land_human_text))
        if html_peaces:
            self.add_mess(self.HTML_PEACE_IN_TEXT, *html_peaces)

class SpaceCharInTest(Check):
    DESCRIPTION = 'Поиск лишних пробелов кода html'
    KEY_NAME = 'extra_spaces'

    EXTRA_SPACE = 'Лишний пробел'
    STATUS_SET = {
        EXTRA_SPACE: Check.WARNING,
    }

    def process(self):
        land_human_text = self.land.get_human_land_text()
        html_peaces = set(re.findall(r' {1,3}[\\.?!]', land_human_text))
        html_bracket_peaces = set(re.findall(r' {1,3}["\'»]|["\'«] {1,3}', land_human_text))
        # TODO write new req - this not work
        html_peaces = set(map(lambda x: f'"{x}"', html_peaces))
        html_bracket_peaces = set(map(lambda x: f'<{x}>', html_bracket_peaces))
        result = html_peaces | html_bracket_peaces
        if result:
            self.add_mess(self.EXTRA_SPACE, *result)

class RekvOnPage(Check):
    DESCRIPTION = 'Поиск реквизитов на лэнде'
    KEY_NAME = 'rekv_on_land'

    NO_REKV = 'Реквизиты не найдены'
    STATUS_SET = {
        NO_REKV: Check.ERROR,
    }

    def process(self):
        # TODO нет типа лэнда
        if self.land.land_type == 'land':
            rekv = self.land.soup.find('rekv')
            if rekv is None or not len(rekv.text):
                self.add_mess(self.NO_REKV)

checks_list = [
    PhoneCountryMask, OffersInLand, Currency, Dates,
    GeoWords, CountyLang, PhpTempVar, UndefinedInText, StarCharInText, HtmlPeaceOfCodeInText, SpaceCharInTest,RekvOnPage
]
