import re

#TODO сдкелать функции через принятия параметров и return (неудобно писать тесты)

def clead_word(word):
    """
    отчистка строки от не букв
    """
    clean_word = ''
    for char in word:
        if char.isalpha():
            clean_word += char
    return clean_word


def find_in_text(text: str, offers: list):
    text = text.lower()
    result = {}
    for offer in offers:
        pettern = f'\W{offer.lower()}\W'
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

    def find_dates(self):
        pattern = '19\d\d|20\d\d|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'  # убран захват символов перед датой
        text = self.human_text
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


class TextFinder:

    YEAR = '19\d\d|20\d\d'
    DATES  = '\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'
    DATES_N_YEARS = '19\d\d|20\d\d|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}'


    @staticmethod
    def find_dates_n_years(text):
        dates_n_years = re.findall(TextFinder.DATES_N_YEARS, text)
        dates_n_years = list(set(dates_n_years))
        dates = []
        years = []
        for i in dates_n_years:
            if len(i) == 4:
                years.append(i)
            else:
                dates.append(i)
        result = {
            'dates': dates,
            'years': years,
        }
        return result

    @staticmethod
    def find_years(text):
        return TextFinder.find_dates_n_years(text)['years']

    @staticmethod
    def find_dates(text):
        return TextFinder.find_dates_n_years(text)['dates']


    @staticmethod
    def find_words(text, *words) -> list:
        result = list()
        for word in words:
            pattern = '\\b\d{0,4}'+word+'\d{0,4}\\b'
            res = re.findall(pattern, text)
            result += res
        return list(set(result))

    @staticmethod
    def is_word_in_text(text, word):
        pattern = '\\b\d{0,4}' + word + '\d{0,4}\\b'
        res = re.search(pattern, text)
        return bool(res)


    @staticmethod
    def find_word_by_root(text, *words_roots) -> list:
        """Поиск в тексте слов по его корню"""
        result = list()
        for word_root in words_roots:
            pattern = word_root + '[\w\W][^\s]{0,5}'
            res = re.findall(pattern, text)
            result += res
        result = map(clead_word, result)
        return list(result)



if __name__ == '__main__':
    text = """
            какойто текст россия 1RUB100 тарпшг российский адвыафды BYN российские, ;dsdas dasd  русский вывы русские EUR.
"""
    print(re.findall('\\b\d{0,4}RUB\d{0,4}\\b', text))



