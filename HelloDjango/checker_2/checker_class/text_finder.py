import re


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
    regEx = '\W' + word_template + '[\W\w]{0,6}[\s.\-;:,]'
    regEx = '\W' + word_template + '[\W\w][^\s]{0,6}[.\-;:,«»\s]'
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
    """Класс анализа кода страницы после отрисовки"""

    def __init__(self, *, source_text, human_text, data):
        self.source_text = source_text
        self.human_text = human_text
        self.data = data
        self.result = dict()

    def process(self):
        self.find_offers()
        self.find_currensy()
        self.find_phone_codes()
        self.find_dates()
        self.find_geo_words()
        self.find_geo_templates_words()

    def find_offers(self):
        offers = self.data['offers']
        offers = find_in_text(self.human_text, offers)
        self.result.update({'offers': list(offers)})

    def find_currensy(self):
        currensys = self.data['currencys']
        currensys = find_in_text(self.human_text, currensys)
        self.result.update({'currencys': list(currensys)})

    def find_phone_codes(self):
        phone_codes = self.data['phone_codes']
        text = self.human_text.lower()
        result = {}
        for p_code in phone_codes:
            p_code = '+' + p_code
            res = text.count(p_code)
            if res:
                result.update({p_code: res})
        self.result.update({'phone_codes': list(result)})

    # def find_dates_old(self):
    #     pattern = '\D[12]{1}[890]{1}\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'  # выкидывает неактуальные года
    #     text = self.human_text
    #     dates = re.findall(pattern, text)
    #     dates = list(set(dates))
    #     chars = '\n() \xa0'
    #     start_end = ' -.,:;"'
    #     clean_dates = []
    #     for date in dates:
    #         for char in chars:
    #             date = date.replace(char, '')
    #         if date[-1] in start_end:
    #             date = date[:-1]
    #         if date[0] in start_end:
    #             date = date[1:]
    #         clean_dates.append(date)
    #     clean_dates = list(set(clean_dates))
    #     self.result.update({'dates_on_land': clean_dates})

    def find_dates(self):
        pattern = '19\d\d|20\d\d|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'  # убран захват символов перед датой
        text = self.human_text
        #with open('/home/vlad/PycharmProjects/-OI-AMK/test_ьн.html','w') as file:
         #   file.write(text)
        dates_n_years = re.findall(pattern, text)
        dates_n_years = list(set(dates_n_years))
        dates = []
        years = []
        for i in dates_n_years:
            if len(i) == 4:
                years.append(i)
            else:
                dates.append(i)
        self.result.update({
            'dates_on_land': dates,
            'years_on_land': years,
        })


    def find_geo_words(self):
        """Поиск статичных слов относящихся к стране"""
        geo_words = self.data['geo_words']
        text = self.human_text.lower()
        result = {}
        for geo_short, words in geo_words.items():
            res = find_in_text(text, words)
            if res:
                result.update({geo_short: list(res)})
        self.result.update({'geo_words': result})

    def find_geo_templates_words(self):
        """Поиск слов по шаблонам"""
        geo_words_templates = self.data['geo_words_templates']
        text = self.human_text.lower()
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

    # @staticmethod
    # def sort_dates(dates: list):
    #     dates_correct = []
    #     dates_incorrect = []
    #     years = []
    #     years_old = []
    #     for date in dates:
    #         if len(date) == 4:
    #             if int(date) in range(2020, 2023):
    #                 years.append(date)
    #             else:
    #                 years_old.append(date)
    #         else:
    #             if date.count('.') != 2 or int(date[-2:]) not in range(20, 23):
    #                 dates_incorrect.append(date)
    #             else:
    #                 dates_correct.append(date)
    #     result = {
    #         'oi-dates_correct': dates_correct,
    #         'oi-dates_incorrect': dates_incorrect,
    #         'oi-years': years,
    #         'oi-years_old': years_old,
    #     }
    #     for k, v in result.items():
    #         v.sort(reverse=True)
    #     return result


if __name__ == '__main__':
    with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/test/coutrys_find/text.txt') as file:
        text = file.read()
    russia_text = text.lower()
