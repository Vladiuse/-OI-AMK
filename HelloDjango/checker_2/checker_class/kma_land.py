import re
import json
from json import JSONDecodeError
import requests as req
from urllib.parse import urlparse, urlunparse
import os
from .land import Land
from .errors import NoUflParamPreLand, IncorrectPreLandUrl, NoAdminSiteDataScript
import os



class KMALand(Land):
    """Сайт KMA"""

    LAND = 'land'
    PRE_LAND = 'preland'
    FULL_PRICE = 'full_price'
    LOW_PRICE = 'low_price'

    TEST_DOMAINS = [
        '127.0.0.1',
        'vladiuse.beget.tech',
        'vim-store.ru',
    ]
    PRE_LAND_DOMAINS = ['blog-feed.org', 'blogs-info.info', 'previewpreland.pro', 'feed-news.org',
                        'blogs-feed.org'] + TEST_DOMAINS
    INCORRECT_PRE_LAND_URLS = ['previewpreland.pro']
    NOT_WORKED_PRE_LAND_DOMAINS = ['blogs-info.info']
    MAIN_PRE_LAND_DOMAIN = 'blog-feed.org'
    PRE_LAND_ADMIN_UTM = 'ufl='
    POLICY_IDS = ['polit', 'agreement']
    REQUISITES_TAG = 'rekv'
    OLD_PRICE_CLASS = ''

    # data to add on page
    STYLES_FILE = './front_data/styles.css'
    JS_FILE = './front_data/script.js'




    def __init__(self, source_text, url, **kwargs):
        super().__init__(source_text=source_text, url=url, **kwargs)
        self.validate_url()
        self.__kma_script = self._find_kma_back_data()
        self.country = self._country()
        self.language = self._language()
        self.country_list = self._country_list()
        self.list_of_parameters = self._list_of_parameters()
        self.list_of_form_parameters = self._list_of_form_parameters()

    def validate_url(self):
        if self.land_type == KMALand.PRE_LAND:
            for domain in KMALand.INCORRECT_PRE_LAND_URLS:
                if domain in self.url:
                    raise IncorrectPreLandUrl
            if KMALand.PRE_LAND_ADMIN_UTM not in self.url:
                raise NoUflParamPreLand

    @staticmethod
    def prepare_url(url):
        url = super(KMALand, KMALand).prepare_url(url)
        for domain in KMALand.NOT_WORKED_PRE_LAND_DOMAINS:
            url = url.replace(domain, KMALand.MAIN_PRE_LAND_DOMAIN)
        return url

    @property
    def display_url(self):
        if self.land_type == KMALand.LAND:
            return super().get_no_protocol_url()
        else:
            s, n, p, a, q, frag = urlparse(self.url)
            return urlunparse(['', '', p, a, q, frag])


    def _find_kma_back_data(self) -> str:
        """Ищет и возвражает тело скрипта с переменными для лэндинга"""
        # soup = BeautifulSoup(self.source_text, 'html5')
        # scripts = soup.find_all('script')
        for script in self.scripts:
            if 'country_list' in script and 'country=' in script:
                return script
        raise NoAdminSiteDataScript

    def _country(self) -> str:
        """Поиск в js коде переменной country - возвращает ее значение"""
        block = re.search(r"country='\w\w'", self.__kma_script)
        country_w_brackets = re.search(r"'\w\w'", block.group(0))
        country = country_w_brackets.group(0).replace("'", '')
        return country.lower()

    def _language(self) -> str:
        """Поиск в js коде переменной language - возвращает ее значение"""
        block = re.search(r'"language":"\w\w"', self.__kma_script)
        language_w_brackets = re.search(r'"\w\w"', block.group(0))
        language = language_w_brackets.group(0).replace('"', '')
        return language.lower()

    def _country_list(self) -> dict:
        """Поиск в js коде переменной country_list - возвращает ее значение"""
        start = self.__kma_script.find('country_list=') + len('country_list=')
        end = self.__kma_script.find('}};') + 2
        var = self.__kma_script[start:end]
        country_list = json.loads(var)
        dic = dict()
        for k, v in country_list.items():
            dic[k.lower()] = v
        return dic

    def _list_of_parameters(self) -> dict:
        """Поиск в js коде переменной list_of_parameters - возвращает ее значение"""
        start = self.__kma_script.find('list_of_parameters=') + len('list_of_parameters=')
        if start == -1:
            return dict()
        end = self.__kma_script.find('};', start) + 1
        var = self.__kma_script[start:end]
        try:
            list_of_parameters = json.loads(var)
        except JSONDecodeError:
            return dict()
        dic = dict()
        for k, v in list_of_parameters.items():
            dic[k.lower()] = v
        return dic

    def _list_of_form_parameters(self) -> dict:
        # for preland
        """Поиск в js коде переменной list_of_form_parameters - возвращает ее значение"""
        start = self.__kma_script.find("list_of_form_parameters='") + len("list_of_form_parameters='")
        end = self.__kma_script.find("';", start) + 0
        var = self.__kma_script[start:end]
        try:
            list_of_form_parameters = json.loads(var)
        except JSONDecodeError:
            return dict()
        dic = dict()
        for k, v in list_of_form_parameters.items():
            dic[k.lower()] = v
        return dic

    def add_site_attrs(self):
        super().add_site_attrs()
        if len(self.country_list) > 1:
            self.land_attrs.append('more_one_select')

    @property
    def iframe_srcdoc(self):
        modul_path = os.path.dirname(__file__)
        styles_path = os.path.join(modul_path, self.STYLES_FILE)
        js_path = os.path.join(modul_path, self.JS_FILE)
        with open(styles_path, encoding='utf-8') as file:
            style_text = file.read()
            self.add_css(style_text)
        with open(js_path, encoding='utf-8') as file:
            js_text = file.read()
            self.add_js(js_text)
        self.add_base_tag(self.base_url)
        html_code = str(self.soup)
        return html_code

    def is_social_script(self):
        socialFish = 'duhost'
        for script in self.scripts:
            if socialFish in script:
                return True

    @property
    def discount_type(self):
        """Получить тип скидки"""
        discount = self.country_list[self.country]['discount']
        if float(discount) > 50:
            return KMALand.LOW_PRICE
        else:
            return KMALand.FULL_PRICE

    def _get_land_type(self):
        """Получить тип сайта"""
        for domain in self.PRE_LAND_DOMAINS:
            if domain in self.url:
                return KMALand.PRE_LAND
        return KMALand.LAND

    @property
    def land_type(self):
        return self._get_land_type()

    @property
    def s1(self):
        return self.country_list[self.country]['s1']

    @property
    def s2(self):
        return self.country_list[self.country]['s2']

    @property
    def s3(self):
        return self.country_list[self.country]['s3']

    @property
    def s4(self):
        return self.country_list[self.country]['s4']

    @property
    def discount(self):
        return self.country_list[self.country]['discount']

    @property
    def curr(self):
        return self.country_list[self.country]['curr']

    @property
    def offer_id(self):
        if self.list_of_form_parameters:
            return self.list_of_form_parameters['offer_id']
        else:
            return self.list_of_parameters['offer_id']

    @property
    def landing_id(self):
        return self.list_of_parameters['landing']

    @property
    def preland_id(self):
        return self.list_of_form_parameters['transit']

    @property
    def get_land_admin_url(self):
        if self.land_type == 'land':
            kma_land_url = f'https://cpanel.kma.biz/offer/module/landing/update?offer_id={self.offer_id}&id={self.landing_id}'
            return kma_land_url
        else:
            kma_preland_url = f'https://cpanel.kma.biz/offer/module/transit/update?offer_id={self.offer_id}&id={self.preland_id}'
            return kma_preland_url

    def get_commision_page_url(self):
        return f'https://cpanel.kma.biz/offer/module/commission/index?offer_id={self.offer_id}'


if __name__ == '__main__':
    url = 'https://blog-feed.org/elle-breasty/?ufl=14926'
    res = req.get(url)
    kma = Land(res.text, url)
