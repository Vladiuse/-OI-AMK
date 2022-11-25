import unittest
from text_fixxer import DomFixxer
from bs4 import BeautifulSoup


class DomFixxerTest(unittest.TestCase):

    def setUp(self):
        self.html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>

        </body>
        </html>
        """
        self.soup = BeautifulSoup(self.html, 'lxml')

    def test_add_base_tag(self):
        text = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>

        </body>
        </html>
        """
        soup = BeautifulSoup(text, 'lxml')
        dom = DomFixxer()
        dom.add_base_tag(soup, 'http://goole.com')
        self.assertTrue(soup.find('base'))
        self.assertTrue(soup.find('base')['href'] == 'http://goole.com')

    def test_change_base_href(self):
        text = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <base href="http://some.com">
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>

        </body>
        </html>
        """
        soup = BeautifulSoup(text, 'lxml')
        dom = DomFixxer()
        dom.add_base_tag(soup, 'http://goole.com')
        self.assertTrue(soup.find('base'))
        self.assertTrue(soup.find('base')['href'] == 'http://goole.com')

    def test_add_css(self):
        css = """
        body{
        color: red;
        }
        """
        dom = DomFixxer()
        dom.add_css(self.soup, css)
        css_in_land = self.soup.find('style')
        self.assertIn(css, str(css_in_land))

    def test_add_js(self):
        js = """
        console.log();
        """
        dom = DomFixxer()
        dom.add_js(self.soup, js)
        js_in_land = self.soup.find('script')
        self.assertIn(js, str(js_in_land))


if __name__ == '__main__':
    unittest.main()
