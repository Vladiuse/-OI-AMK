import unittest
from bs4 import BeautifulSoup
from HelloDjango.checker_2.checker_class.land import Land
from HelloDjango.checker_2.checker_class.errors import CheckerError
from unittest.mock import MagicMock

class TestLandSoup(unittest.TestCase):

    def setUp(self):
        html_code = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Title</title>
                    </head>
                    <body>
                    <h1>Some Text</h1>
                    <video></video>
                    <audio></audio>
                    </body>
                    </html>
        """
        self.land = Land(source_text=html_code, url='')
        self.empty_land = Land(source_text='', url='')


    def test_get_title_of_land(self):
        title = self.land._get_title()
        self.assertEqual(title, 'Title')

    def test_title_prop(self):
        self.assertEqual(self.land.title, 'Title')

    def test_is_video_tag_in(self):
        self.assertTrue(self.land._is_video_tag_on_site())

    def test_video_not_in(self):
        html = """
        <body>
        <p>dasdd</p> dada
        </body>
        """
        land = Land(html, url='')
        self.assertFalse(land._is_video_tag_on_site())

    def test_is_audio_tag_in(self):
        self.assertTrue(self.land._is_audio_tag_on_site())

    def test_audio_not_in(self):
        html = """
        <body>
        <p>dasdd</p> dada
        </body>
        """
        land = Land(html, url='')
        self.assertFalse(land._is_audio_tag_on_site())

    def test_human_text_from_placeholders(self):
        html = """
        <input autocomplete="name" class="input_form" name="name" placeholder="XXX" required="" style="text-align: left" type="text" oldvalue="">
        <input autocomplete="tel" class="input_form" name="phone" placeholder="YYY" required="" style="text-align: left" type="tel" oldvalue="">
        """
        land = Land(html, url='')
        placeholders = land._human_text_from_placeholders()
        self.assertTrue(len(placeholders) == 2)
        self.assertTrue('XXX' in placeholders)
        self.assertTrue('YYY' in placeholders)


    def test_human_text_from_input_values(self):
        html = """
        <input name="scenario" type="hidden" value="zzz">
        <input name="language"  value="yyy">
        <input name="some"  value="xxx">
        """
        land = Land(html, url='')
        values  = land._human_text_from_input_values()
        self.assertTrue(len(values) == 2)
        self.assertTrue('xxx' in values)
        self.assertTrue('yyy' in values)
        self.assertTrue('zzz' not in values)

    def test_get_human_text(self):
        human_text = self.land.human_text
        self.assertTrue('Some Text' in human_text, 'text from document')

    def test_get_human_text_title_add(self):
        human_text = self.land.human_text
        self.assertTrue('Title' in human_text, 'text from page <title>')

    def test_human_text_placehodlers_n_values_in_text(self):
        html = """
        <body>
        <p>paragraph</p>
        <input name="scenario" type="hidden" value="zzz">
        <input name="some"  value="xxx">
        <input autocomplete="name" class="input_form" name="name" placeholder="XXX" required="" style="text-align: left" type="text" oldvalue="">
        </body>
        """
        land = Land(html, url='')
        self.assertTrue('paragraph' in land.human_text)
        self.assertTrue('xxx' in land.human_text, 'text from input value')
        self.assertTrue('XXX' in land.human_text, 'text from input placeholder')
        self.assertTrue('zzz' not in land.human_text, 'text from hidden input')

    def test_human_text_count_call(self):
        html = """some text"""
        land = Land(html, url='')
        mock = MagicMock(retur_value='')
        land._human_text_from_placeholders = mock
        for _ in range(3):
            x = land.human_text
        self.assertEqual(1, mock.call_count, 'count of method calls')

    def test_human_text_lower_count_calls(self):
        html = """some text"""
        land = Land(html, url='')
        mock = MagicMock(retur_value='')
        land._human_text_from_placeholders = mock
        for _ in range(3):
            x = land.human_text_lower
        self.assertEqual(1, mock.call_count, 'count of method calls')

    def test_get_human_lower_text(self):
        html = """Some Text"""
        land = Land(html, url='')
        result = land.human_text_lower
        self.assertTrue('some' in result)
        self.assertTrue('text' in result)
        self.assertTrue('Some' not in result)
        self.assertTrue('Text' not in result)

    def test_yandex_script_on_page(self):
        html = """
                <body>
        <p>paragraph</p>
        <input autocomplete="name" class="input_form" name="name" placeholder="XXX" required="" style="text-align: left" type="text" oldvalue="">
        <script>
        some code https://mc.yandex.ru/metrika some code;
        </script>
        </body>
        """
        land = Land(html, url='')
        self.assertTrue(land.is_yam_script())


    def test_yandex_script_not_on_page(self):
        html = """
                <body>
        <p>paragraph</p>
        <input autocomplete="name" class="input_form" name="name" placeholder="XXX" required="" style="text-align: left" type="text" oldvalue="">
        </body>
        """
        land = Land(html, url='')
        self.assertFalse(land.is_yam_script())

    def test_get_scripts(self):
        html = """
                <body>
        <p>paragraph</p>
            <script>
        some code https://mc.yandex.ru/metrika some code;
        </script>
            <script>
        let xxx = '123';
        </script>
        </body>
        """
        land = Land(html, url='')
        text = ''
        count = 0
        for script in land.scripts:
            text += script
            count += 1
        self.assertTrue('xxx' in text)
        self.assertTrue('https://mc.yandex.ru/metrika' in text)
        self.assertTrue(count == 2)

    def test_is_favicon_links_raise_error(self):
        link = '<link rel="ICO">'
        link_bs  = BeautifulSoup(link, 'lxml')
        with self.assertRaises(CheckerError) as context:
            self.empty_land.is_favicon_links(link)
            self.empty_land.is_favicon_links(link_bs)

    def test_is_favicon_links_true(self):
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        links = [
            '<link rel="ICO" href="some">',
            '<link rel="XXX aaaa" type="" href="some">',
            '<link rel="" type="ICO" href="some">',
            '<link type="YYY" rel="" href="some">',
        ]
        for link in links:
            soup = BeautifulSoup(link, 'lxml')
            link = soup.find('link')
            self.assertTrue(Land.is_favicon_links(link), str(link))

    def test_is_favicon_links_no_href(self):
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        links = [
            '<link rel="ICO" href="">',
            '<link rel="XXX aaaa" type="" href="">',
            '<link rel="" type="ICO" >',
            '<link type="YYY" rel="" >',
        ]
        for link in links:
            soup = BeautifulSoup(link, 'lxml')
            link = soup.find('link')
            self.assertFalse(Land.is_favicon_links(link), str(link))


    def test_is_favicon_links_no_attrs(self):
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        links = [
            '<link rel="">',
            '<link type="">',
            '<link rel="" type="">',
            '<link rel="some gfg" type="sddwd">',
        ]
        for link in links:
            soup = BeautifulSoup(link, 'lxml')
            link = soup.find('link')
            self.assertFalse(Land.is_favicon_links(link))

    def test_get_favicon_links(self):
        html = """
        <head>
        <base href="https://feed-news.org/otoryx-blog/"/>
        <meta charset=utf-8 />
        <link rel=preconnect href="https://fonts.googleapis.com">
        <link rel=preconnect href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=Roboto&family=Roboto+Condensed&display=swap" rel=stylesheet>
        <link rel=stylesheet href="css/A.main.css.pagespeed.cf.c9kfEOZmfL.css">
        '<link rel="ICO" href="some">',
        '<link type="XXX" href="some">',
        </head>
        <body>
        some text
        </body>
        """
        land  = Land(html, url='')
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        fav_links = land.get_favicon_links()
        self.assertEqual(len(fav_links), 2)

    def test_get_favicon_links_no_add_base_url(self):
        html = """
        <head>
        <link href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=Roboto&family=Roboto+Condensed&display=swap" rel=stylesheet>
        <link rel=stylesheet href="css/A.main.css.pagespeed.cf.c9kfEOZmfL.css">
        '<link rel="ICO" href="some">',
        '<link type="XXX" href="some">',
        </head>
        <body>
        some text
        </body>
        """
        land = Land(html, url='')
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        fav_links = land.get_favicon_links(add_base_url=False)
        self.assertEqual(len(fav_links), 2)
        for link in fav_links:
            link = BeautifulSoup(link, 'lxml').find('link')
            self.assertEqual(link['href'], 'some')

    def test_get_favicon_links_add_base_url_no_http(self):
        html = """
        '<link rel="ICO" href="some">',
        """
        land = Land(html, url='')
        mock  = MagicMock(return_value='http://google.com/')
        Land.TYPES_REL = ['ICO', 'XXX', 'YYY']
        Land.get_url_for_base_tag = mock
        fav_links = land.get_favicon_links(add_base_url=True)
        self.assertEqual(len(fav_links), 1)
        link = fav_links[0]
        self.assertTrue(isinstance(link, str))
        link = BeautifulSoup(link, 'lxml').find('link')
        self.assertTrue(link['href']=='http://google.com/some')


class LandUrlFuncsTest(unittest.TestCase):

    def setUp(self):
        self.empty_land = Land(source_text='', url='')


    def test_get_no_protokol_url_http(self):
        self.empty_land.url = 'http://google.com/some'
        self.assertEqual(self.empty_land.get_no_protocol_url(), 'google.com/some')

    def test_get_no_protokol_url_https(self):
        self.empty_land.url = 'https://google.com/some'
        self.assertEqual(self.empty_land.get_no_protocol_url(), 'google.com/some')

    def test_get_url_for_base_tag(self):
        url = 'https://feed-news.org/visio-blog/#some?ufl=17446'
        self.assertEqual(self.empty_land.get_url_for_base_tag(url), 'https://feed-news.org/visio-blog/')


class LandDateSearchTest(unittest.TestCase):
    def setUp(self):
        self.empty_land = Land(source_text='', url='')

    def test_years_search_change_attr_type_call_dates(self):
        x = self.empty_land.dates
        self.assertEqual(self.empty_land._dates, [])
        self.assertEqual(self.empty_land._years, [])

    def test_years_search_change_attr_type_call_years(self):
        x = self.empty_land.years
        self.assertEqual(self.empty_land._dates, [])
        self.assertEqual(self.empty_land._years, [])

    def test_dates_years_search_count_call(self):
        self.empty_land._dates, self.empty_land._years = [],[]
        mock = MagicMock(return_value='')
        x = self.empty_land.dates
        x = self.empty_land.years
        self.assertEqual(mock.call_count, 0)

    def test_search_years(self):
        text = '_2020 sada 1990d 2500 _'
        land = Land(text, url='')
        res = land._find_years(land.human_text)
        self.assertEqual(len(res), 3)
        for date in '2020', '1990', '2500':
            self.assertTrue(date in res)

    def test_no_search_years(self):
        text1 = '312312323213321'
        text2 = """
        1800 dasd
        2200  dsd 
        2100 dsda
        """
        for text in text1, text2:
            land = Land(text, url='')
            res = land._find_years(land.human_text)
            self.assertEqual(len(res), 0)

    def test_search_years_some_chars_before_after(self):
        text = '_2020_  a1990a .2500.'
        land = Land(text, url='')
        res = land._find_years(land.human_text)
        self.assertEqual(len(res), 3)
        for date in '2020', '1990', '2500':
            self.assertTrue(date in res)


    def test_search_years_number_before_after(self):
        text = '202019992020'
        land = Land(text, url='')
        res = land._find_years(land.human_text)
        self.assertEqual(len(res), 0)

    def test_find_dates_end_year_full(self):
        text = """
        01.01.2020 
        01.01.1920 
        01.01.2500
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 3)
        for date in text.split():
            date = date.strip()
            self.assertTrue(date in res)


    def test_test_find_dates_end_year_full_separs(self):
        text = """
        01/01/2020
        01\\01\\1920
        01-01-2500
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 3)
        for date in text.split():
            date = date.strip()
            self.assertTrue(date in res)


    def test_find_dates_start_year_full(self):
        text = """
        2020.01.01 
        1920.01.01 
        2500.01.01
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 3)
        for date in text.split():
            date = date.strip()
            self.assertTrue(date in res)

    def test_find_dates_start_year_full_separs(self):
        text = """
        2020/01/01 
        1920\\01\\01 
        2500-01-01
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 3)
        for date in text.split():
            date = date.strip()
            self.assertTrue(date in res)

    def test_short_dates(self):
        text = """
        20.01.01 
        20.01.01 
        00.01.01
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 3)

    def test_short_dates_separs(self):
        text = """
        20/01/01 ds
        20\\01\\01 ds
        20-20-10
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 2)
        self.assertTrue('20-20-20' not in res)

    def test_no_search_dates(self):
        text = """
        20.20.230 
        201.10.10
        
        20\\20\\230 
        201\\10\\10
        
        20/20/230 
        201/10/10
        
        10-10-10
        """
        res = self.empty_land._find_dates(text)
        self.assertEqual(len(res), 0)

    def test_search_years_not_in_dates(self):
        text = """
        text 
        20.10.2020 text
        20.10.1980 text
        2020.10.10 text
        
        20.10.10 text
        10.10.20 text
        
        2021
        2022
        some text end
        """
        land = Land(text, url='')
        land._find_dates_n_years()
        self.assertTrue(len(land.years),2)
        for year in '2021', '2022':
            self.assertTrue(year in land.years)
        for year in '2020', '1980':
            self.assertTrue(year not in land.years)


class LandUniqueWordsTest(unittest.TestCase):

    def test_unique_words(self):
        text = 'some get text some'
        land = Land(text, url='')
        unique = land.unique_words
        self.assertTrue(len(unique) == 3)

    def test_unique_words_split_text(self):
        text = 'some_text-text!xxx;yyy ddd'
        land = Land(text, url='')
        unique = land.unique_words
        self.assertEqual(len(unique),5)

    def test_unique_words_word_find(self):
        text = 'some_text-text!xxx;yyy'
        land = Land(text, url='')
        unique = land.unique_words
        for word in 'some', 'text-text', 'xxx', 'yyy':
            self.assertTrue(word in unique)

    def test_unique_words_drop_short(self):
        text = 'xx yy zz'
        land = Land(text, url='')
        unique = land.unique_words
        self.assertTrue(len(unique)==0)


if __name__ == '__main__':
    unittest.main()




