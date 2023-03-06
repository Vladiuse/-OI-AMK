from datetime import datetime
import re
from collections import defaultdict


class Check:
    DESCRIPTION = 'No'
    KEY_NAME = 'No'

    WARNING = 'warning'
    ERROR = 'error'
    INFO = 'info'

    STATUS_SET = {}

    def __init__(self, land, url_checker):
        self.land = land
        self.url_checker = url_checker
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
        phone_codes_on_land = []
        for country in self.url_checker.countrys:
            if '+' + country.phone_code in self.land.human_text_lower:
                phone_codes_on_land.append(country)
        incorrect_countrys = set()
        for country in phone_codes_on_land:
            if country.iso == self.land.country:
                self.add_mess(self.MASK_ON_LAND, '+'+country.phone_code)
            else:
                incorrect_countrys.add('+'+country.phone_code)
        if incorrect_countrys:
            self.add_mess(self.INCORECT_MASK_ON_LAND, *incorrect_countrys)


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
    def process(self):
        incorrect_currencys = set()
        incorrect_cyrrencys_code = set()
        for currency in self.url_checker.currencys:
            # main curr
            reg = '[\W\d]'+currency.main_curr+'[.\W\d]'
            if re.search(reg, self.land.human_text_lower):
                if self.url_checker.current_country not in currency.country_set.all():
                    incorrect_currencys.add(currency.main_curr.upper())
                else:
                    self.add_mess(self.CURR_FOUND, currency.main_curr.upper())

            # other currs codes
            for curr in currency.other_currs:
                reg = '[\W\d]' + curr + '[.\W\d]'
                if re.search(reg, self.land.human_text_lower):
                    if self.url_checker.current_country not in currency.country_set.all():
                        incorrect_currencys.add(curr.upper())
                    else:
                        incorrect_cyrrencys_code.add(curr.upper())

        if not self.messages:
            self.add_mess(self.NO_CURRENCIES)
        if incorrect_currencys:
            self.add_mess(self.INCORRECT_COUNTRY_CURRENCY, *incorrect_currencys)
        if incorrect_cyrrencys_code:
            self.add_mess(self.INCORRECT_CURE_CODE, *incorrect_cyrrencys_code)



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
        if not offers_in_land:
            self.add_mess(self.NO_OFFER_FIND)
        if len(offers_in_land) > 1:
            self.add_mess(self.MORE_ONE_OFFER_FOUND, *offers_in_land)
        if len(offers_in_land) == 1:
            self.url_checker.land_data['offer_name'] = offers_in_land[0]
            # self.add_mess(self.ONE_OFFER_FOUND, *offers_in_land)


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
        self.search_by_template()

    def search_by_word(self):
        pass

    def search_by_template(self):
        for country in self.url_checker.countrys:
            templates = country.words['templates']
            country_words_found = []
            for template in templates:
                regEx = '\W' + template + '[\W\w][^\s]{0,6}[.\-;:,«»\s]'
                # symbols_to_clean = """ .-;:”,"\n"""
                find_templates = re.findall(regEx, self.land.human_text_lower)
                country_words_found += find_templates
            if country_words_found:
                country_words_found = set(country_words_found)
                if country.iso == self.land.country:
                    self.add_mess(self.ALL_COUNTRYS,*country_words_found)
                else:
                    self.add_mess(self.INCORECT_COUNTRY,*country_words_found)



class CountyLang(Check):
    DESCRIPTION = 'Правильный язык сайта'
    KEY_NAME = 'country_lang'

    INCORRECT_LANG = 'Указан не вырный язык сайта'

    STATUS_SET = {
        INCORRECT_LANG: Check.WARNING,
    }

    def process(self):
        site_lang = self.land.language
        country_langs = None
        for country in self.url_checker.countrys:
            if self.land.country == country.iso:
                country_langs = country.language.all()
        if not any(site_lang == country_lang.iso for country_lang in country_langs):
            needed_langs = [lang.iso for lang in country_langs]
            self.add_mess(self.INCORRECT_LANG, 'должен быть', *needed_langs)


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
        self.search_undefined()
        self.search_nan()
        self.search_null()
        if self.vars_in_text:
            self.add_mess(self.JS_VARIABLE_IN_TEXT, *self.vars_in_text)

    def search_undefined(self):
        if self.UNDEFINED in self.land.human_text_lower:
            self.vars_in_text.add(self.UNDEFINED)

    def search_nan(self):
        if self.NaN in self.land.get_human_land_text():
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
        land_human_text = self.land.get_human_land_text()
        if float(self.land.discount) <= 50 and self.STAR_CHAR in land_human_text:
            self.add_mess(self.STAR_ON_SITE)
        if self.land.discount_type == 'full_price':
            if self.STAR_CHAR in self.land.get_human_land_text():
                self.add_mess(self.STAR_ON_SITE)
        else:
            if self.STAR_CHAR not in self.land.get_human_land_text():
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
        land_human_text = self.land.get_human_land_text()
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
    LEN_OF_TEXT_BLOCK = 1000
    CROP_TEXT_BLOCK = 10

    def process(self):
        self.space_before_end_of_sentence()
        self.space_before_after_brackets()

    def space_before_end_of_sentence(self):
        html_peaces = re.findall(r' {1,3}[.?!]', self.land.human_text_lower)
        html_peaces = set(map(lambda elem: f'"{elem}"', html_peaces))
        if html_peaces:
            self.add_mess(self.EXTRA_SPACE_SENTENCE, *html_peaces)

    def space_before_after_brackets(self):
        text = self.land.human_text_lower
        SPASE_BEFORE_REG = self.BRACKET_CHARS_OPEN + '\s{1,3}.{5,1000}\S' + self.BRACKET_CHARS_CLOSE
        SPASE_AFTER_REG = self.BRACKET_CHARS_OPEN + '\S{1,3}.{5,1000}\s' + self.BRACKET_CHARS_CLOSE
        TWO_SPACE = self.BRACKET_CHARS_OPEN + '\s{1,3}.{5,1000}\s{1,3}' + self.BRACKET_CHARS_CLOSE

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
        if self.land.land_type == 'land':
            rekv = self.land.soup.find('rekv')
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
        phones = re.findall('\+?\d[\d()\- x]{9,18}[\dx]', self.land.human_text_lower)
        if phones:
            self.add_mess(self.FOUND_PHONE_NUMBER, *phones)

class IncorrectDataInComments(Check):
    #TODO
    pass

class PercentCharCorrectSide(Check):
    DESCRIPTION = 'Неправильная сторона %'
    KEY_NAME = 'old_price_on_land'

    INCORRECTS = '% не с той стороны'
    STATUS_SET = {
        INCORRECTS: Check.WARNING,
    }

    RIGHT_SIDE = '\d{1,6} ?%'
    LEFT_SIDE = '% ?\d{1,6}'

    NO_LIKE_OTHER_LANGS = ['tr', 'ar']

    def process(self):
        country_langs = [lang.iso for lang in self.url_checker.current_languages]
        if any(self.NO_LIKE_OTHER_LANGS) in country_langs:
            regEx = self.RIGHT_SIDE
        else:
            regEx = self.LEFT_SIDE
        incorrect_percent_side = re.findall(regEx, self.land.human_text_lower)
        if incorrect_percent_side:
            incorrect_percent_side = set(incorrect_percent_side)
            self.add_mess(self.INCORRECTS, *incorrect_percent_side)


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
        for country in self.url_checker.countrys:
            for city in country.city_set.all():
                city_parts = city.name.split('-')
                if all(part in land_words for part in city_parts) or city.name in land_words:
                # if city.name in land_words:
                    if country != self.url_checker.current_country:
                        geo_city_in_text[country.pk].append(city.name)
        for country, citys in geo_city_in_text.items():
            citys.insert(0,country.upper())
            self.add_mess(self.INCORRECTS_CITY_GEO, *citys)


KMA_checkers = [
    PhoneCountryMask, OffersInLand, Currency, Dates,
    GeoWords, CountyLang, PhpTempVar, JsVarsInText, StarCharInText, HtmlPeaceOfCodeInText, SpaceCharInTest,RekvOnPage,
    NoOldPrice,PercentCharCorrectSide, CityInText,FindPhoneNumbers
]
