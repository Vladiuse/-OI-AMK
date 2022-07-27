from bs4 import BeautifulSoup
import requests as req
import re
from pprint import pprint

def find_in_text(text: str, offers: list):
    text = text.lower()
    result = {}
    for offer in offers:
        pettern = f'\W{offer.lower()}\W'
        # pettern = f'[\.\s<>\-\d«»]{1}{offer.lower()}[\.\s<>\-«»\d]{1}'
        res = re.findall(pettern, text)
        if res:
            result.update({offer: len(res)})

    return result

def find_word_template_in_text(word_template, text):
    """Поиск шаблона слова по тексту"""
    regEx = '\W'+word_template+'[\W\w]{0,6}[\s.\-;:,]'
    regEx = '\W'+word_template+'[\W\w]{0,6}[.\-;:,]'
    symbols_to_clean = """ .-;:”,"\n"""
    res = re.findall(regEx, text)
    clean_result = []
    for word in res:
        word = word.strip()
        for char in symbols_to_clean:
            word = word.replace(char, '')
        clean_result.append(word)
    return clean_result


class TextAnaliz:

    def __init__(self, land_text, data):
        self.land_text = land_text
        self.data = data
        self.result = dict()

        self.soup = BeautifulSoup(self.land_text, 'lxml')
        self.clean_land_text = self.soup.text

    def add_placeholders_text(self):
        inputs = self.soup.find_all('input')
        placeholders_text = ['']
        for inpt in inputs:
            try:
                placeholder = inpt['placeholder']
                placeholders_text.append(placeholder)
            except KeyError:
                pass
        placeholders_text = ' '.join(placeholders_text)
        self.clean_land_text += placeholders_text


    def process(self):
        self.drop_some_tags()
        self.add_placeholders_text()
        self.clean_land_text = self.soup.text

        self.find_offers()
        self.find_currensy()
        self.find_phone_codes()
        self.find_dates()
        self.find_geo_words()
        self.find_geo_templates_words()
        self.find_scripts()
        # print(self.result)

    def drop_some_tags(self):
        """Убрать элементы тулбара и полиси"""
        ids = ['oi-toolbar', 'test-block', 'polit', 'agreement']
        for id in ids:
            print(id, id in str(self.soup))
            elem = self.soup.find(id=id)
            if elem:
                elem.decompose()
            

            #         // send_text.find('#oi-toolbar').remove()
            # // send_text.find('#test-block').remove()
            # // send_text.find('#polit').remove()
            # // send_text.find('#agreement').remove()

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
        # pattern = '\D\d\d\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'
        pattern = '\D[12]{1}[890]{1}\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}' # выкидывает неактуальные года
        text = self.clean_land_text
        dates = re.findall(pattern, text)
        dates = list(set(dates))
        chars = '\n() \xa0'
        start_end = ' -.,:;"'
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
        clean_dates = TextAnaliz.sort_dates(clean_dates)
        self.result.update({'dates_on_land': clean_dates})

    def find_geo_words(self):
        """Поиск статичных слов относящихся к стране"""
        geo_words = self.data['geo_words']
        text = self.clean_land_text.lower()
        result = {}
        for geo_short, words in geo_words.items():
            res = find_in_text(text, words)
            if res:
                result.update({geo_short: list(res)})
        # pprint(result)
        self.result.update({'geo_words': result})

    def find_scripts(self):
        # yaMetrika = 'yametrica'
        # to_find = [
        #     {'name': someKMA, 'find': 'duhost'},
        #      {'name': yaMetrika, 'find': 'https://mc.yandex.ru/metrika'},
        #      ]
        soup = BeautifulSoup(self.land_text, 'lxml')
        scripts = soup.find_all('script')
        scripts_block = '' 
        for script in scripts: 
            scripts_block += str(script)
        socialFish = TextAnaliz.find_social(scripts_block)
        yam = TextAnaliz.find_yam(scripts_block)
        result = {
            'socialFish': socialFish,
            'yam': yam,
        }

        # for i in to_find:
        #     if i['find'] in scripts_block:
        #         result[i['name']] = True
        self.result.update({
            'scripts': result,
        })
    @staticmethod
    def find_yam(scripts_blocks):
        yam_link= 'https://mc.yandex.ru/metrika'
        yam_id = ';ym('
        if yam_link in scripts_blocks:
            pos = scripts_blocks.find(yam_id)
            if pos != -1:
                yam_id = scripts_blocks[pos+ 4:pos+12]
                return yam_id
            else:
                return 'not found'
        else:
            return False


    @staticmethod
    def find_social(scripts_blocks):
        socialFish = 'duhost'
        if socialFish in scripts_blocks:
            return True
        else:
            return False


    def find_geo_templates_words(self):
        """Поиск слов по шаблонам"""
        geo_words_templates = self.data['geo_words_templates']
        text = self.clean_land_text.lower()
        result = {}
        for geo, word_templates in geo_words_templates.items():
            res = []
            for template in word_templates:
                find = find_word_template_in_text(word_template=template, text=text)
                res.extend(find)
            res = list(set(res))
            if res:
                result.update({geo: res})
        self.result.update({'geo_words_templates': result})


    @staticmethod
    def sort_dates(dates:list):
        dates_correct = []
        dates_incorrect = []
        years = []
        years_old = []
        for date in dates:
            if len(date) == 4:
                if int(date) in range(2020,2023):
                    years.append(date)
                else:
                    years_old.append(date)
            else:
                if date.count('.') != 2 or int(date[-2:]) not in range(20,23):
                    dates_incorrect.append(date)
                else:
                    dates_correct.append(date)
        result = {
            'oi-dates_correct': dates_correct,
            'oi-dates_incorrect': dates_incorrect,
            'oi-years': years,
            'oi-years_old': years_old,
        }
        for k, v in result.items():
            v.sort(reverse=True)
        return result




if __name__ == '__main__':

    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/test/coutrys_find/text.txt') as file:
        text = file.read()
    russia_text = text.lower()
    # print(russia_text)
    #
    # result = find_word_template_in_text('росси', russia_text)
    # print(result)
