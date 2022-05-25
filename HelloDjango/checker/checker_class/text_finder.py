from bs4 import BeautifulSoup
import requests as req
import re


def find_in_text(text: str, offers: list):
    text = text.lower()
    result = {}
    for offer in offers:
        pettern = f'\W{offer.lower()}\W'
        res = re.findall(pettern, text)
        if res:
            result.update({offer: len(res)})

    return result


class TextAnaliz:

    def __init__(self, land_text, data):
        self.land_text = land_text
        self.data = data
        self.result = dict()

        self.soup = BeautifulSoup(self.land_text, 'lxml')
        self.clean_land_text = self.soup.text


    def process(self):
        self.find_offers()
        self.find_currensy()
        self.find_phone_codes()
        self.find_dates()
        print(self.result)

    def find_offers(self):
        offers = self.data['offers']
        offers = find_in_text(self.clean_land_text, offers)
        self.result.update({'offers': list(offers)})


    def find_currensy(self):
        currensys = self.data['currencys']
        currensys = find_in_text(self.clean_land_text, currensys)
        self.result.update({'currencys': list(currensys)})


    def find_phone_codes(self):
        phone_codes = self.data['phone_codes']
        text = self.clean_land_text.lower()
        result = {}
        for p_code in phone_codes:
            p_code = '+' + p_code
            res = text.count(p_code)
            if res:
                result.update({p_code: res})
        self.result.update({'phone_codes': list(result)})


    def find_dates(self):
        pattern = '\D\d\d\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'
        text = self.clean_land_text
        dates = re.findall(pattern, text)
        dates = list(set(dates))
        print(dates)
        chars = '\n() /'
        start_end = ' -.'
        clean_dates = []
        for date in dates:
            for char in chars:
                date = date.replace(char, '')
            if date[-1] in start_end:
                date = date[:-1]
            if date[0] in start_end:
                date = date[1:]
            clean_dates.append(date)
        clean_dates = list(set(clean_dates))
        self.result.update({'dates_on_land': clean_dates})



if __name__ == '__main__':
    dates = [' 2030\n', ' 4444-', '1.10.20', '10.01.1020', '1/10/20', '1.1.20', '01.10.2020', '/2020 ', ' 2022)', '(2030)', '24.05.2022', ' 2030 ', '01.10.20', '01.1.2020', '\n1111\n', '01-10-20', '1-1.20', ' 2020 ', '\n2030\n']
    chars = '() /'
    start_end = ' -.'
