import re
import hashlib
from bs4 import BeautifulSoup
import requests as req
from django.conf import settings

SPAN_CLASS_BACK = '__back-date '
SPAN_DATE_ERROR = ' __debug_date_error'
SPAN_CLASS_PERCENT = '__back-percent '

TOOLBAR_HTML_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/block.html'
TOOLBAR_STYLES_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/styles.css'
TOOLBAR_JS_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/script.js'
TEST_DATES = str(settings.BASE_DIR) + '/checker/checker_class/front_data/test_dates.html'

TOOLBAR_NO_JS_FILE = str(settings.BASE_DIR) + '/checker/checker_class/wb/wb.js'


def is_date_correct(date):
    """Проверка коректности даты"""
    for char in '-/\\':
        if char in date:
            return False
    return True


class Img:
    css_tyle = ' __debug_double'
    to_find_img_attr = 'data-oi-img'
    oi_double_attr = 'data-oi-img-double'
    ATTRS = [
        'data-src',
        'data-pagespeed-lazy-src',
        
    ]

    ALL_IMG_SRCS = []
    IMG_SRC_DOUBLES = dict()

    def __init__(self, img_soup):
        self.img = img_soup
        self.src = None
        self.attrs_src = set()
        self.main_src = None

    def process(self):
        self._get_src()
        self._get_attrs_srcs()
        self._get_main_src()
        Img.ALL_IMG_SRCS.append(self.main_src)

    @staticmethod
    def reset():
        Img.IMG_SRC_DOUBLES.clear()
        Img.ALL_IMG_SRCS.clear()

    def set_img_as_double(self):
        if Img.ALL_IMG_SRCS.count(self.main_src) > 1:
            try:
                self.img['class'] = ' '.join(self.img['class']) + Img.css_tyle
            except KeyError:
                self.img['class'] = Img.css_tyle
            sha_hash = hashlib.sha256(str(self.main_src).encode('utf-8')).hexdigest()
            sha_hash = sha_hash[-6:]
            self.img[Img.oi_double_attr] = sha_hash
            Img.IMG_SRC_DOUBLES[sha_hash] = self.main_src

    def _get_main_src(self):
        """Определить главный src"""
        if self.src:
            if self.src.endswith('.gif') and self.attrs_src:
                for src in self.attrs_src:
                    self.main_src = src
            else:
                self.main_src = self.src

    def _get_src(self):
        """Получить src картинки"""
        try:
            self.src = self.img['src']
        except KeyError:
            pass

    def _get_attrs_srcs(self):
        """Получить все остальные scr с других аттрибутов"""
        for attr in Img.ATTRS:
            try:
                self.attrs_src.add(self.img[attr])
            except KeyError:
                pass


def find_img_double(soup) -> set:
    """Поиск дублей карртинок в html """
    # soup = BeautifulSoup(text, 'lxml')
    images = soup.find_all('img')
    srcs = []
    srcs_double = set()
    for img in images:
        try:
            src = img['src']
            srcs.append(src)
        except KeyError:
            pass
    for src in srcs:
        if srcs.count(src) > 1:
            srcs_double.add(src)
    return srcs_double


class TextFixxer:
    """Внесение изменений в исходный код страницы"""

    def __init__(self, text):
        self.text = text

    def process(self):
        # self.add_test_dates()
        self.text = re.sub(
            r'<[\w\s]+>[\s\wА-Яа-я.,;:"!?@#$%&*(){}\']*(\D\d\d\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4})[\s\wА-Яа-я.,;:"!?@#$%&*(){}\']*<[/\w\s]+>',
            # добавил Спецсимолы
            self.wrap_dates,
            self.text)
        self.text = re.sub(r'<[=\w\d\s"\-]*>[\t\r\n\s\-]?(\d\d\d\d|\d{4}[\s\-]{1,3}\d{4})[\t\r\n\s\-]?<[/\w\s]+>',
                           self.wrap_dates,
                           self.text)

    @staticmethod
    def span_wrap(date_s):
        date = date_s.group(0)
        span_class = SPAN_CLASS_BACK
        if not is_date_correct(date):
            span_class += SPAN_DATE_ERROR
        res = f'<span class="{span_class}" >{date}</span>'
        return res

    @staticmethod
    def wrap_dates(string):
        """Поиск дат хх.хх.хххх и оборачивание в тэг"""
        date_string = string.group(0)
        date = re.sub(r'\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4}|\d\d\d\d', TextFixxer.span_wrap, date_string)
        return date

    def add_test_dates(self):
        with open(TEST_DATES, encoding='utf-8') as file:
            dates = file.read()
        body_pos = self.text.find('</body>')
        self.text = self.text[:body_pos] + dates + self.text[body_pos:]


class DomFixxer:
    """Изменение верстки сайта"""

    def __init__(self, soup, url):
        self.soup = soup
        self.toolbar = None
        self.styles = None
        self.script = None
        self.url = url

    def process(self):
        self.load_files()
        # self.add_bouble_img_in_tool()
        self.find_double_img()
        self.add_checked_url_in_toolbar()
        self.add_base_tag()
        # self.fix_style_link()
        # self.add_test_dates()

        self.add_html()
        self.add_css()
        self.add_js()

    def load_files(self):
        with open(TOOLBAR_HTML_FILE, encoding='utf-8') as file:
            self.toolbar = file.read()
        self.toolbar = BeautifulSoup(self.toolbar, 'lxml')
        with open(TOOLBAR_STYLES_FILE, encoding='utf-8') as file:
            self.styles = file.read()
        with open(TOOLBAR_JS_FILE, encoding='utf-8') as file:
            self.script = file.read()

    def add_html(self):
        # div_soup = BeautifulSoup(self.toolbar, 'lxml')
        div_soup = self.toolbar.find('div', {"id": "oi-toolbar"})
        self.soup.html.body.insert(0, div_soup)

    def add_css(self):
        """Добавить стили на сайт"""
        styles_tag = self.soup.new_tag('style')
        styles_tag.string = self.styles
        # self.soup.html.head.insert(0, styles_tag)
        self.soup.html.body.append(styles_tag)

    def add_js(self):
        """Добавить скрипт на сайт"""
        script_tag = self.soup.new_tag("script")
        script_tag.string = self.script
        self.soup.html.body.append(script_tag)

    def find_double_img(self):
        imgs_tags = self.soup.find_all('img')
        Img.reset()
        imgs = [Img(img) for img in imgs_tags]
        [img.process() for img in imgs]
        [img.set_img_as_double() for img in imgs]
        div_toolbar = self.toolbar.find('div', {"id": "back-info"})
        if Img.IMG_SRC_DOUBLES:
            p_info = self.soup.new_tag('p')
            p_info.string = 'Картинки дубли:'
            div_toolbar.append(p_info)
        for hash, src in Img.IMG_SRC_DOUBLES.items():
            new_img = self.toolbar.new_tag('img', src=src)
            new_img[Img.to_find_img_attr] = hash
            div_toolbar.append(new_img)

    def add_bouble_img_in_tool(self):
        double_imgs_src = find_img_double(self.soup)
        self.add_calss_img_boudle()
        div_toolbar = self.toolbar.find('div', {"id": "back-info"})
        if double_imgs_src:
            p_info = self.soup.new_tag('p')
            p_info.string = 'Картинки дубли:'
            div_toolbar.append(p_info)
        for img_scr in double_imgs_src:
            new_img = self.toolbar.new_tag('img', src=img_scr)
            div_toolbar.append(new_img)

    def add_calss_img_boudle(self):
        """Добавление стиля обводки для дублей картинки"""
        css_tyle = ' __debug_double'
        double_imgs_src = find_img_double(self.soup)
        for src in double_imgs_src:
            imgs = self.soup.find_all('img')
            for img in imgs:
                try:
                    if img['src'] == src:
                        img['class'] = ' '.join(img['class']) + css_tyle
                except KeyError:
                    img['class'] = css_tyle

    def add_checked_url_in_toolbar(self):
        self.toolbar.find(id="original-link")['data-href'] = self.url

    def fix_all_tags(self):
        pass

    def add_base_tag(self):
        url = self.url
        if '?' in self.url:
            url = self.url.split('?')[0]
        if not url.endswith('/'):
            url += '/'
        base = self.soup.find('base')
        if not base:
            new_base = self.soup.new_tag('base')
            new_base['href'] = url
            self.soup.html.head.insert(0, new_base)
        else:
            base['href'] = url

    def fix_style_link(self):
        href = 'css/bmmfp.css'
        new_href = 'css/A.bmmfp.css.pagespeed.cf.TbIz99oGpz.css'
        link_style = self.soup.find('link', {'href': href})
        if link_style:
            new_link = self.soup.new_tag('link')
            new_link['href'] = new_href
            new_link['media'] = "all"
            new_link['rel'] = "stylesheet"
            new_link['type'] = "text/css"
            self.soup.html.head.insert(0, new_link)
            # link_style['href'] = new_href

    def fix_relativ_path(self):
        pass

    def load_wb(self):
        with open(TOOLBAR_NO_JS_FILE, encoding='utf-8') as file:
            self.script = file.read()

    def add_wb(self):
        script_tag = self.soup.new_tag("script")
        script_tag.string = self.script
        self.soup.html.body.append(script_tag)


if __name__ == '__main__':
    TOOLBAR_HTML_FILE = './checker/checker_class/front_data/block.html'
    TOOLBAR_STYLES_FILE = './checker/checker_class/front_data/styles.css'
    TOOLBAR_JS_FILE = './checker/checker_class/front_data/script.js'
    url = 'https://blog-feed.org/blog-dialux-ge/?ufl=14153'
    res = req.get(url)
    # print(res.text)
    # print('href="css/A.bmmfp.css.pagespeed.c' in res.text)
    # exit()
    soup = BeautifulSoup(res.text, 'lxml')
    dom = DomFixxer(soup, url)
    dom.process()
    # print(dom.soup)
