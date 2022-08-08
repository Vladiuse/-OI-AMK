import hashlib
from bs4 import BeautifulSoup
from django.conf import settings


TOOLBAR_STYLES_FILE = str(settings.BASE_DIR) + '/checker_2/checker_class/front_data/styles.css'
TOOLBAR_JS_FILE = str(settings.BASE_DIR) + '/checker_2/checker_class/front_data/script.js'


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


class DomFixxer:
    """Изменение верстки сайта"""

    def __init__(self, soup, url):
        self.soup = soup
        self.url = url
        self.base_tag_url = ''
        self.title = ''
        self.styles = None
        self.script = None
        self.img_doubles = list()


    def process(self):
        self.add_base_tag()
        self.get_title()
        self.load_files()
        self.find_double_img()

        self.add_css()
        self.add_js()

    def load_files(self):
        with open(TOOLBAR_STYLES_FILE, encoding='utf-8') as file:
            self.styles = file.read()
        with open(TOOLBAR_JS_FILE, encoding='utf-8') as file:
            script = file.read()
            self.script = script


    def add_css(self):
        """Добавить стили на сайт"""
        styles_tag = self.soup.new_tag('style')
        styles_tag.string = self.styles
        self.soup.html.body.append(styles_tag)

    def add_js(self):
        """Добавить скрипт на сайт"""
        script_tag = self.soup.new_tag("script")
        script_tag.string = self.script
        self.soup.html.body.append(script_tag)

    def find_double_img(self):
        """Поиск на сайте дублей картинок и добавление к ним соответствующих атрибутов"""
        imgs_tags = self.soup.find_all('img')
        Img.reset()
        imgs = [Img(img) for img in imgs_tags]
        [img.process() for img in imgs]
        [img.set_img_as_double() for img in imgs]
        for hash, src in Img.IMG_SRC_DOUBLES.items():
            if not src.startswith('https'):
                src = self.base_tag_url + src
            dic = {

                'hash': hash,
                'src': src,
            }
            self.img_doubles.append(dic)


    def add_base_tag(self):
        url = self.url
        if '?' in self.url:
            url = self.url.split('?')[0]
        if not url.endswith('/'):
            url += '/'
        self.base_tag_url = url
        base = self.soup.find('base')
        if not base:
            new_base = self.soup.new_tag('base')
            new_base['href'] = url
            self.soup.html.head.insert(0, new_base)
        else:
            base['href'] = url


    def get_title(self):
        """найти title сайта"""
        title = self.soup.find('title')
        self.title = title.text

    def is_video_on_site(self):
        """Есть ли на сайте тэг video"""
        if self.soup.find_all('video'):
            return True

