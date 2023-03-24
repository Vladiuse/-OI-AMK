from datetime import datetime
import re
from collections import defaultdict
from .kma_land import KMALand

class Check:
    DESCRIPTION = 'No'
    KEY_NAME = 'No'

    WARNING = 'warning'
    ERROR = 'error'
    INFO = 'info'

    STATUS_SET = {}

    def __init__(self, land, link_checker):
        self.land = land
        self.link_checker = link_checker
        self.errors = set()
        self.info = set()
        self.messages = list()

    def process(self):
        pass

    def add_mess(self, error_text, *args, text=None):
        message = {
            'text': error_text if not text else text,
            'status': self.STATUS_SET[error_text],
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_curr_country_phone_on_land = False
        self.incorrect_countries = []

    def process(self):
        countrys = self.find_countries_phone_code_on_land()
        self.separate_countries_by_error_type(countrys)
        self.add_messages()

    def find_countries_phone_code_on_land(self) -> list:
        country_phone_codes_on_land = []
        for country in self.link_checker.countrys:
            if '+' + country.phone_code in self.land.human_text_lower:
                country_phone_codes_on_land.append(country)
        return country_phone_codes_on_land

    def separate_countries_by_error_type(self, countries):
        for country in countries:
            if country == self.link_checker.current_country:
                self.is_curr_country_phone_on_land = True
            else:
                self.incorrect_countries.append(country)

    def add_messages(self):
        # info
        if self.is_curr_country_phone_on_land:
            self.add_mess(self.MASK_ON_LAND, '+' + self.link_checker.current_country.phone_code)
        # error
        if self.incorrect_countries:
            phone_codes = ['+'+country.phone_code for country in self.incorrect_countries]
            self.add_mess(self.INCORECT_MASK_ON_LAND, *phone_codes)


class Currency(Check):
    DESCRIPTION = 'Поиск валют по тексту'
    KEY_NAME = 'currencies_on_land'

    NO_CURRENCIES = 'Валюты не найдены'
    INCORRECT_COUNTRY_CURRENCY = 'Найдена валюта другой страны'
    CURR_FOUND = 'Найденая валюта'
    INCORRECT_CURE_CODE = 'Неправильный код валюты'

    STATUS_SET = {
        NO_CURRENCIES: Check.WARNING,
        INCORRECT_CURE_CODE: Check.WARNING,
        INCORRECT_COUNTRY_CURRENCY: Check.ERROR,
        CURR_FOUND: Check.INFO,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_find_current_currency = False
        self.incorrect_currencys = set()
        self.incorrect_cyrrencys_code = set()

    def process(self):
        self.find_currencys()
        self.add_messages()

    def find_currencys(self):
        for currency in self.link_checker.currencys:
            # main curr
            reg = '[\W\d]'+currency.main_curr+'[.\W\d]'
            #TODO - проэкронировать точку
            if re.search(reg, self.land.human_text_lower):
                if self.link_checker.current_country not in currency.country_set.all():
                    self.incorrect_currencys.add(currency.main_curr.upper())
                else:
                    self.is_find_current_currency = currency.main_curr.upper()

            # other currs codes
            for curr in currency.other_currs:
                reg = '[\W\d]' + curr + '[.\W\d]'
                if re.search(reg, self.land.human_text_lower):
                    if self.link_checker.current_country not in currency.country_set.all():
                        self.incorrect_currencys.add(curr.upper())
                    else:
                        self.incorrect_cyrrencys_code.add(curr.upper())

    def add_messages(self):
        if self.is_find_current_currency:
            self.add_mess(self.CURR_FOUND, self.is_find_current_currency)
        if self.incorrect_currencys:
            self.add_mess(self.INCORRECT_COUNTRY_CURRENCY, *self.incorrect_currencys)
        if self.incorrect_cyrrencys_code:
            self.add_mess(self.INCORRECT_CURE_CODE, *self.incorrect_cyrrencys_code)
        if not self.messages:
            self.add_mess(self.NO_CURRENCIES)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.offers_in_land = set()

    def process(self):
        self.find_offers()
        self.add_messages()
        self.return_find_offer()

    def find_offer(self, offer_name):
        # TODO
        pass

    def find_offers(self):
        offers = self.link_checker.offers
        for offer in offers:
            if re.search('\W' + offer.name + '\W', self.land.human_text_lower):
                self.offers_in_land.add(str(offer))

    def add_messages(self):
        if not self.offers_in_land:
            self.add_mess(self.NO_OFFER_FIND)
        if len(self.offers_in_land) > 1:
            self.add_mess(self.MORE_ONE_OFFER_FOUND, *self.offers_in_land)

    def return_find_offer(self):
        if len(self.offers_in_land) == 1:
            for offer in self.offers_in_land:
                self.link_checker.land_data['offer_name'] = offer



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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dates = list(set(self.land.dates))
        self.years = list(set(self.land.years))
        #
        self.incorrect_format_dates = None
        self.incorrect_dates = None
        self.future_dates = None
        self.earliest_date = None

    def process(self):
        self.process_dates()
        self.add_messages()

    def process_dates(self):
        self.incorrect_format_dates = list(filter(self.is_incorrect_date_format, self.dates))
        self.incorrect_dates = list(filter(self.is_date_incorrect, self.dates))
        self.future_dates = list(filter(self.is_date_from_future, self.dates))
        self.earliest_date = self.get_earliest_date(self.dates)

    def add_messages(self):
        if self.years:
            self.years.sort(key=lambda x: int(x))
            self.add_mess(self.ALL_YEARS, *self.years)

        if self.dates:
            self.add_mess(self.ALL_DATES, *self.dates)

        if self.incorrect_format_dates:
            self.add_mess(self.INCORRECT_DATE_FORMAT, *self.incorrect_format_dates)

        if self.incorrect_dates:
            self.add_mess(self.INCORRECT_DATE, *self.incorrect_dates)

        if self.future_dates:
            self.add_mess(self.FUTURE_DATE, *self.future_dates)

        if self.earliest_date:
            self.add_mess(self.EARLIEST_DATE, self.earliest_date)


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

    CURRENT_COUNTRY = 'Найдена страна'
    INCORECT_COUNTRY = 'Другие страны'

    STATUS_SET = {
        CURRENT_COUNTRY: Check.WARNING,
        INCORECT_COUNTRY: Check.ERROR,
    }

    def process(self):
        self.search_by_template()

    def search_by_word(self):
        pass

    def search_by_template(self):
        for country in self.link_checker.countrys:
            templates = country.words['templates']
            country_words_found = set()
            for template in templates:
                regEx = '\W' + template + '[\W\w][^\s]{0,6}[.\-;:,«»\s]'
                find_templates = re.findall(regEx, self.land.human_text_lower)
                for temp in find_templates:
                    temp = self.clean_word(temp)
                    country_words_found.add(temp)
            if country_words_found:
                if country == self.link_checker.current_country:
                    self.add_mess(self.CURRENT_COUNTRY, *country_words_found,
                                  text=f'{self.CURRENT_COUNTRY} ({country})')
                else:
                    self.add_mess(self.INCORECT_COUNTRY,*country_words_found,
                                  text=f'{self.INCORECT_COUNTRY} ({country})')

    def clean_word(self,word):
        return ''.join(filter(lambda char: char.isalpha(), word))




class CountyLang(Check):
    DESCRIPTION = 'Правильный язык сайта'
    KEY_NAME = 'country_lang'

    INCORRECT_LANG = 'Указан не вырный язык сайта'

    STATUS_SET = {
        INCORRECT_LANG: Check.WARNING,
    }


    def process(self):
        currenc_country_langs_iso = [lang.iso for lang in self.link_checker.current_languages]
        if self.land.language not in currenc_country_langs_iso:
            needed_langs = [str(lang) for lang in self.link_checker.current_languages]
            self.add_mess(self.INCORRECT_LANG, *needed_langs, text=f'{self.INCORRECT_LANG}, должен быть')



class PhpTempVar(Check):
    DESCRIPTION = 'Поиск переменных шаблонов PHP'
    KEY_NAME = 'php_template_vars'

    VARIABLE_ON_SITE = 'Найдена переменная шаблона'

    STATUS_SET = {
        VARIABLE_ON_SITE: Check.ERROR,
    }

    def process(self):
        land_human_text = self.land.human_text
        var_templates = re.findall(r'\{\$[\S.]{1,40}}', land_human_text)
        if var_templates:
            self.add_mess(self.VARIABLE_ON_SITE, *var_templates)


class JsVarsInText(Check):
    DESCRIPTION = 'Поиск undefined по тектсу'
    KEY_NAME = 'undefined_in_text'

    UNDEFINED = 'undefined'
    NaN = 'NaN'
    NULL = 'null'
	
    # UNDEFINED_IN_TEXT = 'Найден undefined в тексте'
    # Nan_IN_TEXT = 'Найден NaN в тексте'
    # NULL_IN_TEXT = 'Найден null в тексте'
    JS_VARIABLE_IN_TEXT = 'Найдены переменные скрипта'
    STATUS_SET = {
        # UNDEFINED_IN_TEXT: Check.ERROR,
        # Nan_IN_TEXT: Check.ERROR,
        # NULL_IN_TEXT: Check.ERROR,
        JS_VARIABLE_IN_TEXT: Check.ERROR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vars_in_text = set()

    def process(self):
    #TODO искать через r'\WVAR\W'
        self.search_undefined()
        self.search_nan()
        self.search_null()
        if self.vars_in_text:
            self.add_mess(self.JS_VARIABLE_IN_TEXT, *self.vars_in_text)

    def search_undefined(self):
        if self.UNDEFINED in self.land.human_text_lower:
            self.vars_in_text.add(self.UNDEFINED)

    def search_nan(self):
        if self.NaN in self.land.human_text:
            self.vars_in_text.add(self.NaN)

    def search_null(self):
        if self.NULL in self.land.human_text_lower:
            self.vars_in_text.add(self.NULL)



class StarCharInText(Check):
    DESCRIPTION = 'Поиск * в текста'
    KEY_NAME = 'star_in_text'

    STAR_ON_SITE = 'Найдена * в тексте'
    STAR_NOT_IN_TEXT = '* не найдена'

    STATUS_SET = {
        STAR_ON_SITE: Check.WARNING,
        STAR_NOT_IN_TEXT: Check.WARNING,
    }
    STAR_CHAR = '*'

    def process(self):
        if self.land.discount_type == KMALand.FULL_PRICE:
            if self.STAR_CHAR in self.land.human_text:
                self.add_mess(self.STAR_ON_SITE)
        else:
            if self.STAR_CHAR not in self.land.human_text:
                self.add_mess(self.STAR_NOT_IN_TEXT)


class HtmlPeaceOfCodeInText(Check):
    # супчик выкидывает их из текста(
    DESCRIPTION = 'Поиск элементов кода html'
    KEY_NAME = 'html_code_peace_in_text'

    HTML_PEACE_IN_TEXT = 'Элементы html кода найдены в тексте'
    STATUS_SET = {
        HTML_PEACE_IN_TEXT: Check.WARNING,
    }

    def process(self):
        land_human_text = self.land.human_text
        html_peaces = set(re.findall(r'<!?-?|-{0,2}>', land_human_text))
        if html_peaces:
            self.add_mess(self.HTML_PEACE_IN_TEXT, *html_peaces)

class SpaceCharInTest(Check):
    DESCRIPTION = 'Поиск лишних пробелов кода html'
    KEY_NAME = 'extra_spaces'

    EXTRA_SPACE_SENTENCE = 'Лишний пробел в конце предложения'
    EXTRA_SPACE_TEXT_BLOCK_BEFORE = 'Лишний пробел перед ковычкой'
    EXTRA_SPACE_TEXT_BLOCK_AFTER = 'Лишний пробел после ковычки'
    EXTRA_SPACE_TEXT_BLOCK_TOW = 'Лишние провебы перед ковычками'
    STATUS_SET = {
        EXTRA_SPACE_SENTENCE: Check.WARNING,
        EXTRA_SPACE_TEXT_BLOCK_BEFORE: Check.WARNING,
        EXTRA_SPACE_TEXT_BLOCK_AFTER: Check.WARNING,
        EXTRA_SPACE_TEXT_BLOCK_TOW: Check.WARNING,
    }
    BRACKET_CHARS_OPEN = '["\'“«]'
    BRACKET_CHARS_CLOSE = '["\'”»]'
    LEN_OF_TEXT_BLOCK = 100
    CROP_TEXT_BLOCK = 10

    def process(self):
        self.space_before_end_of_sentence()
        # self.space_before_after_brackets()

    def space_before_end_of_sentence(self):
        html_peaces = re.findall(r' {1,3}[.?!]', self.land.human_text_lower)
        html_peaces = set(map(lambda elem: f'"{elem}"', html_peaces))
        if html_peaces:
            self.add_mess(self.EXTRA_SPACE_SENTENCE, *html_peaces)

    def space_before_after_brackets(self):
        text = self.land.human_text_lower
        SPASE_BEFORE_REG = self.BRACKET_CHARS_OPEN + '\s{1,3}.{5,100}\S' + self.BRACKET_CHARS_CLOSE
        SPASE_AFTER_REG = self.BRACKET_CHARS_OPEN + '\S{1,3}.{5,100}\s' + self.BRACKET_CHARS_CLOSE
        TWO_SPACE = self.BRACKET_CHARS_OPEN + '\s{1,3}.{5,100}\s{1,3}' + self.BRACKET_CHARS_CLOSE

        before = re.findall(SPASE_BEFORE_REG,text)
        if before:
            before = map(lambda text_block: text_block[:self.CROP_TEXT_BLOCK], before)
            self.add_mess(self.EXTRA_SPACE_TEXT_BLOCK_AFTER, *before)

        after = re.findall(SPASE_AFTER_REG,text)
        if after:
            after_ = map(lambda text_block: text_block[len(after) - self.CROP_TEXT_BLOCK:], after)
            self.add_mess(self.EXTRA_SPACE_TEXT_BLOCK_BEFORE, *after_)

        two = re.findall(TWO_SPACE,text)
        if two:
            two_ = map(lambda text_block: text_block[:self.CROP_TEXT_BLOCK] + '...' + text_block[len(after) - self.CROP_TEXT_BLOCK:], two)
            self.add_mess(self.EXTRA_SPACE_TEXT_BLOCK_TOW, *two_)

class RekvOnPage(Check):
    DESCRIPTION = 'Поиск реквизитов на лэнде'
    KEY_NAME = 'rekv_on_land'

    NO_REKV = 'Реквизиты не найдены'
    STATUS_SET = {
        NO_REKV: Check.ERROR,
    }

    def process(self):
        # TODO нет типа лэнда
        if self.land.land_type == KMALand.LAND:
            rekv = self.land.soup.find(KMALand.REQUISITES_TAG)
            if rekv is None or not len(rekv.text):
                self.add_mess(self.NO_REKV)


class NoOldPrice(Check):
    DESCRIPTION = 'Наличие старой цена'
    KEY_NAME = 'old_price_on_land'

    NO_OLD_PRICE = 'Отстутствует старая цена'
    STATUS_SET = {
        NO_OLD_PRICE: Check.WARNING,
    }

    def process(self):
        old_price = self.land.soup.select('.price_land_s4')
        if not old_price:
            self.add_mess(self.NO_OLD_PRICE)


class FindPhoneNumbers(Check):
    DESCRIPTION = 'Наличие номера на сайте'
    KEY_NAME = 'phone_number_in_text'

    FOUND_PHONE_NUMBER = 'Найден номер телефона'
    STATUS_SET = {
        FOUND_PHONE_NUMBER: Check.WARNING,
    }
    def process(self):
        phones = re.findall('\+\s?\d[\d()\- x]{7,18}[\dx]', self.land.human_text_lower)
        if phones:
            self.add_mess(self.FOUND_PHONE_NUMBER, *phones)



class PercentCharCorrectSide(Check):
    DESCRIPTION = 'Неправильная сторона %'
    KEY_NAME = 'old_price_on_land'

    INCORRECTS = '% не с той стороны'
    SPACE_PERCENT_FIND = 'Лишний пробел у процента'
    STATUS_SET = {
        INCORRECTS: Check.WARNING,
        SPACE_PERCENT_FIND: Check.WARNING,
    }

    RIGHT_SIDE = '\d{1,6} ?[%٪]'
    LEFT_SIDE = '[%٪] ?\d{1,6}'

    SPACE_PERCENT = '\d{1,6} [%٪]|[%٪] \d{1,6}'

    NO_LIKE_OTHER_LANGS = ['tr']

    def process(self):
        self.percent_incorrect_side()
        self.percent_n_space()

    def percent_incorrect_side(self):
        # todo rewrite check on cluntry, not lang(cat be not set)
        country_langs = [lang.iso for lang in self.link_checker.current_languages]
        if any(lang in country_langs for lang in self.NO_LIKE_OTHER_LANGS):
            regEx = self.RIGHT_SIDE
        else:
            regEx = self.LEFT_SIDE
        incorrect_percent_side = re.findall(regEx, self.land.human_text_lower)
        if incorrect_percent_side:
            incorrect_percent_side = set(incorrect_percent_side)
            self.add_mess(self.INCORRECTS, *incorrect_percent_side)

    def percent_n_space(self):
        space_percent = re.findall(self.SPACE_PERCENT, self.land.human_text)
        if space_percent:
            self.add_mess(self.SPACE_PERCENT_FIND, *space_percent)



class CityInText(Check):
    DESCRIPTION = 'Поиск городов'
    KEY_NAME = 'city_search'

    INCORRECTS_CITY_GEO = 'Найден город другого гео'
    STATUS_SET = {
        INCORRECTS_CITY_GEO: Check.WARNING,
    }

    def process(self):
        land_words = self.land.unique_words
        geo_city_in_text = defaultdict(list)
        for country in self.link_checker.countrys:
            for city in country.city_set.all():
                city_parts = city.name.split('-')
                if all(part in land_words for part in city_parts) or city.name in land_words:
                # if city.name in land_words:
                    if country != self.link_checker.current_country:
                        geo_city_in_text[country.pk].append(city.name)
        for country, citys in geo_city_in_text.items():
            citys.insert(0,country.upper())
            self.add_mess(self.INCORRECTS_CITY_GEO, *citys,
                          text=f'{self.INCORRECTS_CITY_GEO} ({country.upper()})')


class IncorrectDataInComments(Check):
    #TODO
    pass

class KmaFormCheck(Check):
    #TODO
    pass

KMA_checkers = [
    PhoneCountryMask, OffersInLand, Currency, Dates,
    GeoWords, CountyLang, PhpTempVar, JsVarsInText, StarCharInText, HtmlPeaceOfCodeInText, SpaceCharInTest,RekvOnPage,
    NoOldPrice,PercentCharCorrectSide, CityInText,FindPhoneNumbers
]

if __name__ == '__main__':
    pass