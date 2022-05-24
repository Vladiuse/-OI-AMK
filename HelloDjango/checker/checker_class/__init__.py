import re
from bs4 import BeautifulSoup
import os
import requests as req
from django.conf import settings
from .text_finder import TextAnaliz


SPAN_CLASS_BACK = '__back-date '
SPAN_DATE_ERROR = ' __debug_date_error'
SPAN_CLASS_PERCENT = '__back-percent '

TOOLBAR_HTML_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/block.html'
TOOLBAR_STYLES_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/styles.css'
TOOLBAR_JS_FILE = str(settings.BASE_DIR) + '/checker/checker_class/front_data/script.js'
TEST_DATES = str(settings.BASE_DIR) + '/checker/checker_class/front_data/test_dates.html'

def is_date_correct(date):
    """Проверка коректности даты"""
    for char in '-/\\':
        if char in date:
            return False
    return True


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
        self.add_test_dates()
        # старая '>.*(\d{1,2}[.\\/-]\d{1,2}[.\\/-]\d{2,4}).*?<|>.*(\d\d\d\d).*?<'
        # работает но летят тэги path svg
        # self.text = re.sub(r'[<>\s]{1}(\d{1,2}[.\\/-]\d{1,2}[.\\/-]\d{2,4}|\d\d\d\d)[<>.\s]{1}', self.wrap_dates, self.text)
        # self.text = re.sub(r'<[\w\s]+>[\s.\d]*(\d\d\d\d|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4})[\s.\d]*<[/\w\s]+>', self.wrap_dates, self.text)
        # self.text = re.sub(r'<[\w\s]+>[\s\wА-Яа-я]*(\d\d\d\d|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4})[\s\wА-Яа-я]*<[/\w\s]+>', # добавил русские буквы
        #                    self.wrap_dates,
        #                    self.text)
        self.text = re.sub(r'<[\w\s]+>[\s\wА-Яа-я.,;:"!?@#$%&*(){}\']*(\D\d\d\d\d[^0-9%]|\d{1,2}[.\\/\--]\d{1,2}[.\\/\--]\d{2,4})[\s\wА-Яа-я.,;:"!?@#$%&*(){}\']*<[/\w\s]+>', # добавил Спецсимолы
                           self.wrap_dates,
                           self.text)
        # r'<[=\w\d\s"\-]*>[\t\r\n]?\d\d\d\d[\t\r\n\s]?<[/\w\s]+>'
        self.text = re.sub(r'<[=\w\d\s"\-]*>[\t\r\n\s\-]?(\d\d\d\d|\d{4}[\s\-]{1,3}\d{4})[\t\r\n\s\-]?<[/\w\s]+>',
                           self.wrap_dates,
                           self.text)
        # ONE
        # self.text = re.sub(r'(\d{1,3}[\s-]?%[^;])',
        #                    self.wrap_percent,
        #                    self.text)



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


    # @staticmethod
    # def span_wrap_percent(percent):
    #     percent = percent.group(0)
    #     span_class = SPAN_CLASS_PERCENT
    #     res = f'<span class="{span_class}" >{percent}</span>'
    #     return res

    # @staticmethod
    # def wrap_percent(string):
    #     """Поиск процентов xxx%"""
    #     percent = string.group(0)
    #     date = re.sub(r'(\d{1,3}[\s-]?%[^;])', TextFixxer.span_wrap_percent, percent)
    #     return date






    def add_test_dates(self):
        with open(TEST_DATES, encoding='utf-8') as file:
            dates = file.read()
        body_pos = self.text.find('</body>')
        self.text = self.text[:body_pos] + dates + self.text[body_pos:]


    # def process(self):
    #     """Главная функция"""
    #     self.text = re.sub(r'>.*\b(19|20\d\d)\b.*?<', self.wrap_years, self.text)
    #     self.text = re.sub(r'>.*\b([-.\d]\d[./\\]\d{1,2}[./\\]\d{2,4})\b.*?<', self.wrap_dates, self.text)
    #
    # @staticmethod
    # def wrap_years(string):
    #     """Поиск дат 19хх 20хх и оборачивание в тэг и класса"""
    #     _class = SPAN_CLASS_BACK
    #     res = f'<span class="{SPAN_CLASS_BACK}">{string.group(0)}</span>'
    #     return res
    #
    # @staticmethod
    # def wrap_dates(string):
    #     """Поиск дат хх.хх.хххх и оборачивание в тэг"""
    #     date = string.group(0)
    #     _class = SPAN_CLASS_BACK
    #     if '\\' in date or '/' in date:
    #         _class += SPAN_ERROR
    #     if not is_date_correct(date):
    #         _class += ' error' if not _class.endswith(SPAN_ERROR) else ''
    #     res = f'<span class="{_class}">{string.group(0)}</span>'
    #     return res


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
        self.add_bouble_img_in_tool()
        self.add_checked_url_in_toolbar()
        self.add_base_tag()
        self.fix_style_link()
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
        self.soup.html.head.append(styles_tag)

    def add_js(self):
        """Добавить скрипт на сайт"""
        script_tag = self.soup.new_tag("script")
        script_tag.string = self.script
        self.soup.html.body.append(script_tag)

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
        #TODO Проверить работу на картинках без класса (по идее вылетит - а должет добавить класс)
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

    # def add_test_dates(self):
    #     dates = ['01.10.20', '1.10.20','01.1.20','1.1.20','01.10.2020','01-10-20', '1/10/20','01\\1\\20','1-1.20','01\\10//2020',]
    #     for date in dates:
    #         new_tag = self.soup.new_tag('p')
    #         new_tag.string = date
    #         self.soup.html.body.append(new_tag)


    def fix_all_tags(self):
        pass

    def add_base_tag(self):
        base = self.soup.find('base')
        if not base:
            url = self.url
            if '?' in self.url:
                url = self.url.split('?')[0]
            new_base = self.soup.new_tag('base')
            new_base['href'] = url
            self.soup.html.head.insert(0, new_base)

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


if __name__ == '__main__':
    TOOLBAR_HTML_FILE = './checker/checker_class/front_data/block.html'
    TOOLBAR_STYLES_FILE = './checker/checker_class/front_data/styles.css'
    TOOLBAR_JS_FILE = './checker/checker_class/front_data/script.js'
    url = 'https://blog-feed.org/blog-dialux-ge/?ufl=14153'
    res = req.get(url)
    print(res.text)
    print('href="css/A.bmmfp.css.pagespeed.c' in res.text)
    exit()
    soup = BeautifulSoup(res.text, 'lxml')
    dom = DomFixxer(soup, url)
    dom.process()
    # print(dom.soup)





