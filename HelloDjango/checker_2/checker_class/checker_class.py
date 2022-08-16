import requests as req
from bs4 import BeautifulSoup
from .kma_land import KMALand
from .text_fixxer import DomFixxer
from .check_list_view import CheckListView
from .check_list_view import CheckListView
from kma.models import PhoneNumber


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
