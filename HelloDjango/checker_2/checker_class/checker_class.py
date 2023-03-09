from .kma_land import KMALand
from .check_list_view import get_check_list
from kma.models import Country, OfferPosition, Language, Currency, KmaCurrency, City
from .checkers import KMA_checkers, Check
from .errors import NoCountryInDB, UrlNotLoad
import requests as req
from django.db.models import Prefetch


class UrlChecker:

    def __init__(self,  url, user, source_text=None):
        self.source_text = source_text
        self.url = url
        self.user = user
        self.messages = list()
        self.land_data = {
            'offer_name': None
        }

        self.land = None
        self.check_list = None
        # db datalanguage
        self.offers = OfferPosition.objects.all()
        self.citys = City.text_search.all()
        self.countrys = Country.actual.prefetch_related('language').prefetch_related(
            Prefetch('city_set', queryset=self.citys)).all()
        self.currencys = KmaCurrency.actual.prefetch_related('country_set').all()

    def load_url(self):
        url = KMALand.format_url(self.url)
        try:
            res = req.get(url)
        except ConnectionError:
            raise UrlNotLoad
        if res.status_code != 200:
            raise UrlNotLoad
        res.encoding = 'utf-8'
        self.source_text = res.text

    def process(self):
        self.land = KMALand(self.source_text, self.url)
        self.land.add_site_attrs()
        self.check_list = get_check_list(self.land, self.user)
        self.land.find_n_mark_img_doubles()
        self.land.phone_code = self.current_country.phone_code
        try:
            self.land.full_lang = Language.objects.get(pk=self.land.language)
        except Language.DoesNotExist:
            self.land.full_lang = 'no lang in BD'

    def text_analiz(self):
        self.land = KMALand(source_text=self.source_text, url=self.url, parser='lxml')
        self.land.drop_tags_from_dom(KMALand.POLICY_IDS)
        for check in KMA_checkers:
            check = check(land=self.land, url_checker=self)
            check.process()
            self.messages += check.messages
        result = {
            'new_checker': self.messages,
            'jeneral_status': self.get_jeneral_check_status(),
        }
        result.update(self.land_data)
        return result

    def get_jeneral_check_status(self):
        statuses = set()
        for m in self.messages:
            statuses.add(m['status'])
        jeneral_status = ''
        if Check.INFO in statuses:
            jeneral_status = Check.INFO
        if Check.WARNING in statuses:
            jeneral_status = Check.WARNING
        if Check.ERROR in statuses:
            jeneral_status = Check.ERROR
        return jeneral_status


    @property
    def current_country(self):
        for country in self.countrys:
            if country.iso == self.land.country:
                return country
        raise NoCountryInDB

    @property
    def current_languages(self):
        return self.current_country.language.all()

