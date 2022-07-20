import requests
from bs4 import BeautifulSoup

def get_rekl_by_id(offer_id,camp_id):
    """Получение рекла по ади оффера и айди кампании"""
    URL = 'https://cpanel.kma.biz/'
    URL_LOGIN = 'https://cpanel.kma.biz/user/login'
    client = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        "Referer": "https://vim-store.ru/"
    }
    client.headers.update(headers)
    res = client.get(URL_LOGIN)  # sets the cookie

    soup = BeautifulSoup(res.text, 'lxml')
    token = soup.find('input', {'name': '_csrf-backend'})['value']
    # print(res, f'get token - {token}')
    login_data = {
        '_csrf-backend': token,
        'login-form[login]': 'v.doronin',
        'login-form[password]': 'djvHN729',
    }
    r = client.post(URL_LOGIN, data=login_data, headers=headers)
    # print(r, 'req LOGIn')
    r = client.get(f'https://cpanel.kma.biz/offer/module/campaign/update?offer_id={offer_id}&id={camp_id}', headers=headers)
    # print(r, 'req get cAMP',)
    soup = BeautifulSoup(r.text, 'lxml')
    select = soup.find('select', {'id': 'campaign-company_id'})
    option = select.find('option', {'selected': True})
    if option:
        return option.text
    return False