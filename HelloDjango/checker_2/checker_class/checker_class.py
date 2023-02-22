from .kma_land import KMALand
from .text_finder import TextAnaliz
from .check_list_view import get_check_list
from kma.models import PhoneNumber, OfferPosition, Language
from .checkers import checks_list, Check

class UrlChecker:

    def __init__(self, source_text, url, user):
        self.land = KMALand(source_text, url, escape_chars=True)
        self.check_list = get_check_list(self.land, user)
        self.user = user

    def process(self):
        self.land.add_site_attrs()
        self.land.process()
        self.land.phone_code = PhoneNumber.get_phone_code_by_country(self.land.country)
        try:
            self.land.full_lang = Language.objects.get(pk=self.land.language)
        except Language.DoesNotExist:
            self.land.full_lang = 'no lang in BD'

    @staticmethod
    def text_analiz(land_text):
        data_for_text_analiz = UrlChecker.get_data_for_text_analiz()
        land = KMALand(source_text=land_text, url='0', parser='lxml')
        land.drop_tags_from_dom(KMALand.POLICY_IDS)
        # land.phone_code = PhoneNumber.get_phone_code_by_country(land.country)
        country_db_data = PhoneNumber.objects.get(short=land.country)
        land.phone_code = country_db_data.phone_code
        land.available_langs = country_db_data.langs
        human_text = land.get_human_land_text()
        analizer = TextAnaliz(source_text=str(land.soup.text), human_text=human_text.lower(), data=data_for_text_analiz)
        analizer.process()
        old_analizer_result = analizer.result
        messages = []
        for check in checks_list:
            check = check(land=land, text_finder_result=analizer.result)
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
            'old': old_analizer_result,
            'new': messages,
            'jeneral_status': jeneral_status
        }
        return result


    @staticmethod
    def get_data_for_text_analiz():
        offers = OfferPosition.objects.values('name')
        offers_names = [offer['name'] for offer in offers]
        phones = PhoneNumber.objects.values('short', 'currency', 'phone_code', 'words')
        phone_codes = [phone['phone_code'] for phone in phones]
        currencys = [phone['currency'] for phone in phones]
        geo_words = {}
        geo_words_templates = {}
        for phone in phones:
            if phone['words']['words']:
                dic = {phone['short']: phone['words']['words']}
                geo_words.update(dic)
        for phone in phones:
            if phone['words']['templates']:
                dic = {phone['short']: phone['words']['templates']}
                geo_words_templates.update(dic)
        data_for_text_analiz = {
            'offers': offers_names,
            'currencys': currencys,
            'phone_codes': phone_codes,
            'geo_words': geo_words,
            'geo_words_templates': geo_words_templates,
        }
        return data_for_text_analiz
