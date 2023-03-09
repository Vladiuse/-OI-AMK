import unittest
from bs4 import BeautifulSoup
from HelloDjango.checker_2.checker_class.dom_fixxer import Img, DomFixxerMixin


class DomFixerTest(unittest.TestCase):

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
        dom = DomFixxerMixin()
        dom.soup = soup
        dom.add_base_tag('http://goole.com')
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
        dom = DomFixxerMixin()
        dom.soup = soup
        dom.add_base_tag('http://goole.com')
        self.assertTrue(dom.soup.find('base'))
        self.assertTrue(dom.soup.find('base')['href'] == 'http://goole.com')

    def test_add_css(self):
        css = """
        body{
        color: red;
        }
        """
        dom = DomFixxerMixin()
        dom.soup = self.soup
        dom.add_css(css)
        css_in_land = self.soup.find('style')
        self.assertIn(css, str(css_in_land))

    def test_add_js(self):
        js = """
        console.log();
        """
        dom = DomFixxerMixin()
        dom.soup = self.soup
        dom.add_js(js)
        js_in_land =  dom.soup.find('script')
        self.assertIn(js, str(js_in_land))

    def test_img_double_find(self):
        html = """
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
            <img src="some_img.jpg">
            <img src="some_img.jpg">
            <img src="some_img_1.jpg">
            <img src="some_img_1.jpg">
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        dom = DomFixxerMixin()
        dom.find_double_img(soup)
        images = soup.find_all('img')
        for img in images:
            self.assertIn(Img.IMG_DOUBLE_CLASS, img['class'])

    def test_img_double_not_all(self):
        html = """
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
            <img src="some_img.jpg">
            <img src="some_img.jpg">
            <img src="some_img_1.jpg">
            <img src="some_img_2.jpg">
            <img src="some_img_3.jpg">
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        dom = DomFixxerMixin()
        dom.find_double_img(soup)
        images = soup.find_all('img', attrs={'class': Img.IMG_DOUBLE_CLASS})
        self.assertTrue(len(images) == 2, msg="Проверка на количество")
        for img in images:
            self.assertIn(Img.IMG_DOUBLE_CLASS, img['class'], msg="Проверка на наличие класса")
        not_double_images = soup.find_all('img', attrs={'class': None})
        self.assertTrue(len(not_double_images) == 3, msg="Проверка на количество картинок не дублей")

    def test_img_double_lazy_data_src(self):
        html = """
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
            <img src="some_img.jpg" data-src="some_image.png">
            <img src="some_img.jpg" data-src="some_image.png">
            <img src="some_img_1.jpg">
            <img src="some_img_2.jpg">
            <img src="some_img_3.jpg">
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'lxml')
        dom = DomFixxerMixin()
        dom.find_double_img(soup)
        images = soup.find_all('img', attrs={'class': Img.IMG_DOUBLE_CLASS})
        self.assertTrue(len(images) == 2, msg="Проверка на количество")
        not_double_images = soup.find_all('img', attrs={'class': None})
        self.assertTrue(len(not_double_images) == 3, msg="Проверка на количество картинок не дублей")






if __name__ == '__main__':
    unittest.main()
