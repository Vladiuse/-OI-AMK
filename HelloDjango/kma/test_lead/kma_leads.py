import requests as req
import socket
# from .kma_lead_errors import CreateStreamError, SendLeadError
import random as r
from datetime import date
from datetime import timedelta


class KmaAPiError(BaseException):
    """Ошибка kma API"""

    def __init__(self, data):
        self.data = data

class CreateStreamError(KmaAPiError):
    """Ошибка создания потока"""


class SendLeadError(KmaAPiError):
    """Ошибка отправки лида"""


def get_time_delta_for_trecher():
    today = date.today()
    week_ago = today - timedelta(days=7)
    return f"{week_ago.strftime('%d.%m.%Y')}+-+{today.strftime('%d.%m.%Y')}"

def get_ip():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr


def fix_phone_tail(phone:str):
    """поменять послендние 4 цифры в номере на рандомные"""
    phone = phone[:-4] + str(r.randint(1000,9999))
    return phone

API_KEY = 'T5Ug9l_5gStBTeg6mUCUSQ25hjAZbRjO'
REFERER = 'Referer: https://facobook.com/'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded'
}
class Lead:

    def __init__(self, name, phone, country,channel, token):
        self.token = token
        self.name = name
        self.phone = phone
        self.country = country
        self.channel = channel
        self.data = dict()

    def send(self, referer=REFERER, ip=get_ip()):
        # если дубль лида {"code":13,"message":"Duplicate of order!"}
        # all good {'code': 0, 'message': 'OK', 'status': 'ok', 'order': 1033507426, 'country': 'ES'}
        # {'code': 0, 'message': 'OK', 'status': 'fake', 'order': 1033553974, 'country': 'BY'}
        # {'code': 0, 'message': 'OK', 'status': 'ok', 'order': 1033553976, 'country': 'HU'}
        # {'code': 0, 'message': 'OK', 'status': 'fake', 'order': 1033553979, 'country': 'BY'}

        # [{'code': 0, 'message': 'OK', 'status': 'success', 'order': 1033553974, 'country': 'BY', 'send_country': 'by'},
        #  {'code': 0, 'message': 'OK', 'status': 'success', 'order': 1033553976, 'country': 'HU', 'send_country': 'hu'},
        #  {'code': 0, 'message': 'OK', 'status': 'danger', 'order': 1033553979, 'country': 'BY', 'send_country': 'ru'}]

        url = 'https://api.kma.biz/lead/add'
        data = {
            'channel': self.channel,
            'name': self.name,
            'phone': self.phone,
            'ip': ip,
            'country': self.country,
            'referer': referer,
            'token': self.token,
        }
        res = req.post(url, data=data, headers=headers)
        self.data = res.json()

    def add_data(self):
        self.add_status()
        self.data.update({'send_country':self.country})

    def add_status(self):
        if not self.is_send_success():
            self.data.update({'result_status': 'error'})
            return
        if self.status != 'ok':
            self.data.update({'result_status': 'danger'})
            return
        if not self.is_result_geo_correct():
            self.data.update({'result_status': 'danger'})
            return
        self.data.update({'result_status': 'success'})


    def is_send_success(self):
        try:
            if self.data['message'] == 'OK':
                return True
        except KeyError:
            return False

    def is_result_geo_correct(self):
        try:
            if self.country == self.data['country'].lower():
                return True
        except KeyError:
            return False

    @property
    def order(self):
        try:
            return str(self.data['order'])
        except KeyError:
            return ''

    @property
    def status(self):
        try:
            return str(self.data['status'])
        except KeyError:
            return ''



class KmaAPITest:
    TEST_NAME_1 = 'Пробный_заказ'
    TEST_NAME_2 = 'Probniy_zakaz'
    TEST_NAME_1 = 'тест'
    TEST_NAME_2 = 'test'

    def __init__(self, token,offer_id, country_n_phone: dict, custom_name=False):
        self.token = token
        self.offer_id = offer_id
        self.country_n_phone = country_n_phone
        self.test_name = KmaAPITest.TEST_NAME_1 if not custom_name else KmaAPITest.TEST_NAME_2
        self.leads = list()

    @staticmethod
    def create_stream(offer_id, token) -> str:
        """Создание потока в пп - возвращает айди созданого потока"""
        url = 'https://api.kma.biz/channel/create'
        params = {
            'offer_id': offer_id,
            'source_id': 1,
            'token': token
        }
        res = req.get(url, params=params)
        if res.json()['success'] != True:
            raise CreateStreamError(data=res.json())
        return res.json()['channel']


    def test_offer(self):
        """Протестировать оффер"""
        channel_id = self.create_stream(self.offer_id, self.token)
        # channel_id = 'zXweZF'
        for country, phone in self.country_n_phone.items():
            phone = fix_phone_tail(phone)
            lead = Lead(self.test_name, phone, country,channel_id, self.token)
            lead.send()
            lead.add_data()
            self.leads.append(lead)
        # if not self.is_all_lead_send():
        #     raise SendLeadError

    def get_leads_ids(self):
        """Получить номера заказов лидов для ссылки на трекер"""
        leads_ids = []
        for lead in self.leads:
            if lead.order:
                leads_ids.append(lead.order)
        return leads_ids

    # def is_all_lead_send(self):
    #     """Все ли лиды успешно отправлены"""
    #     return all([lead.success for lead in self.leads])

    def get_tracker_link(self):
        """Получить ссылку"""
        timedelta = get_time_delta_for_trecher()
        leads_ids = self.get_leads_ids()
        leads_ids_str = '+'.join(leads_ids)
        url = f'https://cpanel.kma.biz/tracker/module/lead/index?action=submit&LeadSearch%5Bcreated_at_%5D={timedelta}&LeadSearch%5Border_id%5D={leads_ids_str}&LeadSearch%5Boffer_ids_%5D=&LeadSearch%5Bis_company_not%5D=0&LeadSearch%5Bcompany_ids_%5D=&LeadSearch%5Bwebmaster_ids_%5D=&LeadSearch%5Bgeo_%5D=&LeadSearch%5Bstatus_type_%5D=&LeadSearch%5Bclient_name%5D=&LeadSearch%5Bclient_phone_normalized%5D=&LeadSearch%5Bcurrency_id_%5D=&LeadSearch%5Bis_mobile_%5D=&LeadSearch%5Bip%5D=&LeadSearch%5Breferrer%5D=&LeadSearch%5Bcompany_order_id%5D=&LeadSearch%5Bmanager_om_ids_%5D=&LeadSearch%5Bextra_params_%5D=&LeadSearch%5Bdata1%5D=&LeadSearch%5Bdata2%5D=&LeadSearch%5Bdata3%5D=&LeadSearch%5Bdata4%5D=&LeadSearch%5Bdata5%5D=&LeadSearch%5Bcategories_%5D=&LeadSearch%5Bapproved_at_%5D=&LeadSearch%5Bis_send_%5D=&LeadSearch%5Bdevice_type_%5D=&LeadSearch%5Bfake_reason_%5D=&LeadSearch%5Bclient_sex_%5D=&LeadSearch%5Bclient_age_from%5D=&LeadSearch%5Bclient_age_to%5D=&LeadSearch%5Border_source_%5D=&LeadSearch%5Bchannel_id%5D=&LeadSearch%5Bbuyout_status_%5D=&LeadSearch%5Bexternal_webmaster%5D=&LeadSearch%5Bmodel_pay_%5D=&LeadSearch%5Btype_traffic%5D='
        return url

    def get_leads_data(self):
        leads_data = []
        for lead in self.leads:
            leads_data.append(lead.data)
        return leads_data

    @staticmethod
    def get_offer(offer_id, token):
        url = f'https://api.kma.biz/?method=getoffers&token={token}&return_type=json'
        res = req.get(url)
        result = res.json()
        for offer in result['offers']:
            if offer['id'] == offer_id:
                return offer
        return {'name': 'No offer found'}



# if __name__ == '__main__':
#     print(KmaAPITest.get_offer('5657'))
