from bs4 import BeautifulSoup
import re
import json
import requests as req


class KMALand:
    """Сайт KMA"""
    PRE_LAND_DOMAINS = ['blog-feed.org']
    LAND_ADMIN_UTM = 'ufl'

    def __init__(self, url, land_text):
        self.url = url
        self.land_text = land_text
        self.__kma_script = self._find_kma_back_data()
        self.country = self._country()
        self.language = self._language()
        self.country_list = self._country_list()

    def _find_kma_back_data(self) -> str:
        """Ищет и возвражает тело скрипта с переменными для лэндинга"""
        soup = BeautifulSoup(self.land_text, 'lxml')
        scripts = soup.find_all('script')
        kma_script = ''
        for s in scripts:
            if s.text.startswith('tmp_data_to_server'):
                kma_script = s.text
                break
        return kma_script

    def _country(self) -> str:
        """Поиск в js коде переменной country - возвращает ее значение"""
        block = re.search(r"country='\w\w'", self.__kma_script)
        country = re.search(r"'\w\w'", block.group(0))
        country = country.group(0).replace("'", '')
        return country

    def _language(self) -> str:
        """Поиск в js коде переменной language - возвращает ее значение"""
        block = re.search(r'"language":"\w\w"', self.__kma_script)
        country = re.search(r'"\w\w"', block.group(0))
        return country.group(0).replace('"', '')

    def _country_list(self) -> dict:
        """Поиск в js коде переменной country_list - возвращает ее значение"""
        start = self.__kma_script.find('country_list=') + len('country_list=')
        end = self.__kma_script.find(';json_quer')
        var = self.__kma_script[start:end]
        return json.loads(var)

    @property
    def discount_type(self):
        discount = self.country_list[self.country]['discount']
        if int(discount) < 50:
            return 'low_price'
        else:
            return 'full_price'

    @property
    def land_type(self):
        for domain in self.PRE_LAND_DOMAINS:
            if domain in self.url:
                return 'pre_land'
        return 'land'

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


if __name__ == '__main__':
    url = 'https://blog-feed.org/elle-breasty/?ufl=14926'
    res = req.get(url)
    kma = KMALand(url, res.text)
    print(kma.s1)
    print(kma.s2)
    print(kma.s3)
    print(kma.s4)
    print(kma.discount)
