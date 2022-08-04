import requests as req
from bs4 import BeautifulSoup
from .kma_land import KMALand
from .text_fixxer import DomFixxer
from .check_list_view import CheckListView
from kma.models import PhoneNumber



class UrlChecker:

    def __init__(self, url):
        self.url = UrlChecker.format_url(url)
        self.land_source = str()
        self.page = str()

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

    def process(self):
        self.kma = self.kma(self.url, self.land_source)
        self.kma.phone_code = PhoneNumber.get_phone_code_by_country(self.kma.country)
        soup = BeautifulSoup(self.land_source, 'html5lib')
        self.dom = self.dom(soup, url=self.url)
        self.dom.process()
        html_page = str(self.dom.soup)
        html_page = html_page.replace('"', '&quot;')
        html_page = html_page.replace("'", '&apos;')
        self.page = html_page