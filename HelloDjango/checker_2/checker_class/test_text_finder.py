import unittest
from text_finder import find_in_text, find_word_template_in_text
from text_finder import TextAnaliz, TextFinder


class TextFinderTest1(unittest.TestCase):

    def test_find_in_text(self):
        text = """
        some text for test text
        """
        words = ['text', 'for']
        res = find_in_text(text, words)
        self.assertEqual(res, {'text': 2, 'for': 1})

    def test_find_word_template_in_text(self):
        temp = 'росси'
        text = """
        какойто текст россия тарпшг российский адвыафды российские, ;dsdas dasd
        """
        res = find_word_template_in_text(temp, text)
        self.assertEqual(res,['россия', 'российский', 'российские'])

    def test_find_dates(self):
        text = """
        dlskd 13.11.20 dlsdsa 13.11.2022. dsadasd 3.1.2022.  dsadasd3-11-2022dsadasda 3/11/2022dds 1999 dlasd 1980
        """
        analizer = TextAnaliz(
            source_text=text, human_text=text, data={}
        )
        analizer.find_dates()
        self.assertEqual(set(analizer.result['dates_on_land']), set(['13.11.20', '13.11.2022', '3.1.2022','3-11-2022' ,'3/11/2022']))
        self.assertEqual(set(analizer.result['years_on_land']),
                         set(['1999','1980' ]))


class TextFinderTest(unittest.TestCase):

    def test_find_dates_n_years(self):
        text = """
         1999 dlasd 1980
        """
        res = TextFinder.find_years(text)
        self.assertEqual(set(res), {'1999', '1980'})

    def test_find_dates(self):
        text = """
        dlskd 13.11.20 dlsdsa 13.11.2022. dsadasd 3.1.2022.  dsadasd3-11-2022dsadasda 3/11/2022dds
        """
        res = TextFinder.find_dates(text)
        self.assertEqual(set(res), {'13.11.20', '13.11.2022', '3.1.2022', '3-11-2022', '3/11/2022'})

    def test_find_words_by_root(self):
        text = """
        какойто текст россия тарпшг российский адвыафды российские, ;dsdas dasd русский вывы русские.
        """
        words_roots = ['росси', 'русск']
        res = TextFinder.find_word_by_root(text, *words_roots)
        self.assertEqual(set(res), {'россия', 'российский', 'российские', 'русский', 'русские'})

    def test_find_words(self):
        text = """
        какойто текст россия RUB100 тарпшг российский адвыафды BYN российские, ;dsdas dasd  русский вывы русские EUR.
        """
        words = {'RUB', 'EUR', 'BYN'}
        res = TextFinder.find_words(text, *words)
        self.assertEqual(set(res), {'RUB100', 'BYN', 'EUR'})



if __name__ == '__main__':
    unittest.main()