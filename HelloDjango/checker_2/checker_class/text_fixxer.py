import hashlib
from bs4 import BeautifulSoup
from django.conf import settings


class Img:
    IMG_DOUBLE_CLASS = ' __debug_double'
    # to_find_img_attr = 'data-oi-img'
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
        """Отличтить хранилище картинок"""
        Img.IMG_SRC_DOUBLES.clear()
        Img.ALL_IMG_SRCS.clear()

    def set_img_as_double(self):
        if Img.ALL_IMG_SRCS.count(self.main_src) > 1:
            try:
                self.img['class'] = ' '.join(self.img['class']) + Img.IMG_DOUBLE_CLASS
            except KeyError:
                self.img['class'] = Img.IMG_DOUBLE_CLASS
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
        # bad code bottom!!!
        if self.main_src is None:
            self.main_src = 'no_scr'

    def _get_src(self):
        """Получить src картинки"""
        try:
            self.src = self.img['src']
        except KeyError:
            pass
            # bad code bottom!!!
            self.scr = 'no_scr'

    def _get_attrs_srcs(self):
        """Получить все остальные scr с других аттрибутов"""
        for attr in Img.ATTRS:
            try:
                self.attrs_src.add(self.img[attr])
            except KeyError:
                pass


class DomFixxer:
    """Изменение верстки сайта"""

    @staticmethod
    def add_css(soup, css_text):
        """Добавить стили на сайт"""
        styles_tag = soup.new_tag('style')
        styles_tag.string = css_text
        soup.html.body.append(styles_tag)

    @staticmethod
    def add_js(soup, js_text):
        """Добавить скрипт на сайт"""
        script_tag = soup.new_tag("script")
        script_tag.string = js_text
        soup.html.body.append(script_tag)

    @staticmethod
    def find_double_img(soup, base_url='') -> list:
        """Поиск на сайте дублей картинок и добавление к ним соответствующих атрибутов"""
        img_doubles = list()
        imgs_tags = soup.find_all('img')
        Img.reset()
        imgs = [Img(img) for img in imgs_tags]
        [img.process() for img in imgs]
        [img.set_img_as_double() for img in imgs]
        for hash, src in Img.IMG_SRC_DOUBLES.items():
            if not src.startswith('http'):
                src = base_url + src
            dic = {
                'hash': hash,
                'src': src,
            }
            img_doubles.append(dic)
        return img_doubles

    @staticmethod
    def add_base_tag(soup, url):
        """Добавить тэг base или замена его href"""
        base = soup.find('base')
        if base:
            base.extract()
        new_base = soup.new_tag('base')
        new_base['href'] = url
        soup.html.head.insert(0, new_base)

