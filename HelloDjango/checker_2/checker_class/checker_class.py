from .kma_land import KMALand
from .check_list_view import get_check_list
from kma.models import Country, OfferPosition, Language, Currency, KmaCurrency
from .checkers import checks_list, Check
from .errors import NoCountryInDB


class UrlChecker:

    def __init__(self, source_text, url, user):
        self.source_text = source_text
        self.url = url
        self.user = user

        self.land = None
        self.check_list = None
        # db datalanguage
        self.offers = OfferPosition.objects.all()
        self.countrys = Country.actual.prefetch_related('language').all()
        self.currencys = KmaCurrency.actual.prefetch_related('country_set').all()

    def process(self):
        self.land = KMALand(self.source_text, self.url, escape_chars=True)
        self.check_list = get_check_list(self.land, self.user)  # TODO filter not added before land processed
        self.land.add_site_attrs()
        self.land.find_n_mark_img_doubles()
        self.land.phone_code = Country.get_phone_code_by_country(self.land.country)
        try:
            self.land.full_lang = Language.objects.get(pk=self.land.language)
        except Language.DoesNotExist:
            self.land.full_lang = 'no lang in BD'

    def text_analiz(self):
        self.land = KMALand(source_text=self.source_text, url=self.url, parser='lxml')
        land = self.land
        land.drop_tags_from_dom(KMALand.POLICY_IDS)
        messages = []
        for check in checks_list:
            check = check(land=land, url_checker=self)
            check.process()
            messages += check.messages
        statuses = set()
        for m in messages:
            statuses.add(m['status'])
        jeneral_status = ''
        if Check.INFO in statuses:
            jeneral_status = Check.INFO
        if Check.WARNING in statuses:
            jeneral_status = Check.WARNING
        if Check.ERROR in statuses:
            jeneral_status = Check.ERROR
        result = {
            'new': messages,
            'jeneral_status': jeneral_status
        }
        return result

    @property
    def current_country(self):
        for country in self.countrys:
            if country.iso == self.land.country:
                return country
        raise NoCountryInDB

    @property
    def current_languages(self):
        return self.current_country.language.all()

