import requests as req
from bs4 import BeautifulSoup
from .kma_land import KMALand
from .text_fixxer import DomFixxer
from .check_list_view import CheckListView
from .check_list_view import CheckListView
from kma.models import PhoneNumber



class UrlChecker:

    def __init__(self, url):
        self.url = UrlChecker.format_url(url)
        self.land_source = str()
        self.page = str()
        self.land_attrs = list()

        self.is_url_work()
        self.dom = DomFixxer
        self.kma = KMALand
        self.check_list = CheckListView



    @staticmethod
    def format_url(url):
        url = url.strip()
        url = url.replace('https://', 'http://')
        return url

    def is_url_work(self):
        res = req.get(self.url)
        if res.status_code != 200:
            raise ZeroDivisionError
        else:
            self.land_source = res.text

    def add_site_attrs(self):
        if self.dom.is_video_on_site():
            self.land_attrs.append('video')

        if len(self.kma.country_list) > 1:
            self.land_attrs.append('more_one_select')

    def process(self):
        self.kma = self.kma(self.url, self.land_source)
        self.kma.phone_code = PhoneNumber.get_phone_code_by_country(self.kma.country)
        self.land_source = self.land_source.replace('&nbsp;', ' ')
        self.land_source = self.land_source.replace('&quot;', '"')
        self.land_source = self.land_source.replace('&apos;', "'")

        self.land_source = self.land_source.replace('&&', '@@')
        self.land_source = self.land_source.replace('&', '&amp;&amp;')
        self.land_source = self.land_source.replace('@@', '&&')



        soup = BeautifulSoup(self.land_source, 'html5lib')

        self.dom = self.dom(soup, url=self.url)
        self.dom.process()
        html_page = str(self.dom.soup)
        self.land_source = self.land_source.replace('&', '&amp;&amp;')
        html_page = html_page.replace('"', '&quot;')
        html_page = html_page.replace("'", '&apos;')
        self.page = html_page
        self.add_site_attrs()
        self.check_list = self.check_list(
            land_type=self.kma.land_type,
            discount_type=self.kma.discount_type,
            country=self.kma.country,
            lang=self.kma.language,
            land_attrs=self.land_attrs
        )
        self.check_list.process()
