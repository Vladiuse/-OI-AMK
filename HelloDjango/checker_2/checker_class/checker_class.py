import requests as req
from bs4 import BeautifulSoup
from .kma_land import KMALand
from .text_fixxer import DomFixxer
from .check_list_view import CheckListView
from .check_list_view import CheckListView
# from kma.models import PhoneNumber



class UrlChecker:

    def __init__(self, source_text, url, user):
        self.land = KMALand(source_text, url, escape_chars=True)
        self.check_list = CheckListView(land=self.land, user=user)
        self.user = user

    def process(self):
        self.check_list.process()
        # self.kma.phone_code = PhoneNumber.get_phone_code_by_country(self.land.country)


        # soup = BeautifulSoup(self.land_source, 'html5lib')
        #
        # self.dom = self.dom(soup, url=self.url)
        # self.dom.process()
        # html_page = str(self.dom.soup)
        # self.land_source = self.land_source.replace('&', '&amp;&amp;')
        # html_page = html_page.replace('"', '&quot;')
        # html_page = html_page.replace("'", '&apos;')
        # self.page = html_page
        # self.add_site_attrs()
        # self.check_list = self.check_list(
        #     land_type=self.kma.land_type,
        #     discount_type=self.kma.discount_type,
        #     country=self.kma.country,
        #     lang=self.kma.language,
        #     land_attrs=self.land_attrs,
        #     user=self.user,
        #     url=self.url
        # )
        # self.check_list.process()
