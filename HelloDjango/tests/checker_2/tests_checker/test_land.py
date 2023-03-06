import unittest
from HelloDjango.checker_2.checker_class.land import Land
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












