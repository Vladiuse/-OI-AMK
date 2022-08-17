import requests as req
from bs4 import BeautifulSoup
from .kma_land import KMALand
from .text_fixxer import DomFixxer
from .check_list_view import CheckListView
from .check_list_view import CheckListView
from kma.models import PhoneNumber


class Check:
    DESCRIPTION = 'No'
    KEY_NAME = 'No'

    WARNING = 'warning'
    ERROR = 'error'

    STATUS_SET = {}

    def __init__(self, land, text_finder_result):
        self.land = land
        self.text_finder_result = text_finder_result
        self.errors = set()
        self.info = set()
        self.result = dict()

    def process(self):
        pass

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
        phome_codes_on_land = self.text_finder_result['phone_codes']
        country_phone_code = '+'+self.land.phone_code
        for code in phome_codes_on_land:
            if code == country_phone_code:
                self.info.add(self.MASK_ON_LAND)
            else:
                self.info.add(self.INCORECT_MASK_ON_LAND)

class Currency(Check):
    DESCRIPTION = 'Поиск валют по тексту'
    KEY_NAME = 'currencies_on_land'

    NO_CURRENCIES = 'Валюты не найдены'
    MORE_ONE_CURRENCIES = 'Найдена валюта другой страны'

    STATUS_SET = {
        NO_CURRENCIES : Check.WARNING,
        MORE_ONE_CURRENCIES: Check.ERROR,
    }

    def process(self):
        currency = self.land.curr
        currencies_on_land = self.text_finder_result['currencys']
        if not currencies_on_land:
            self.info.add(self.NO_CURRENCIES)
        for c in currencies_on_land:
            if c != currency:
                self.info.add(self.MORE_ONE_CURRENCIES)
class OffersInLand(Check):
    DESCRIPTION = 'Поиск офферов по тексту'
    KEY_NAME = 'offers_on_land'

    NO_OFFER_FIND = 'Не найден не один оффер'
    MORE_ONE_OFFER_FOUND = 'Найдено больше одного оффера'

    STATUS_SET = {
        NO_OFFER_FIND: Check.WARNING,
        MORE_ONE_OFFER_FOUND: Check.ERROR,
    }


    def process(self):
        offers_in_land = self.text_finder_result['offers']
        if not offers_in_land:
            self.info.add(self.NO_OFFER_FIND)
        if len(offers_in_land) > 1:
            self.info.add(self.MORE_ONE_OFFER_FOUND)


class UrlChecker:

    def __init__(self, source_text, url, user):
        self.land = KMALand(source_text, url, escape_chars=True)
        self.check_list = CheckListView(land=self.land, user=user)
        self.user = user

    def process(self):
        self.land.add_site_attrs()
        self.land.process()
        self.check_list.process()
        self.land.phone_code = PhoneNumber.get_phone_code_by_country(self.land.country)
