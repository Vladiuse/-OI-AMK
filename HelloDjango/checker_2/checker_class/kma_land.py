from bs4 import BeautifulSoup
import re
import json
import requests as req
from .text_fixxer import DomFixxer
from django.conf import settings


class Land:

    def __init__(self, source_text, url, *, parser='html5lib', escape_chars=False):
        self.source_text = Land.re_escape_html_chars(source_text) if escape_chars else source_text
        self.url = url
        self.soup = BeautifulSoup(self.source_text, parser)
        self.human_text = None
        self.img_doubles = None

    def _get_title(self):
        """найти title сайта"""
        title = self.soup.find('title')
        return title

    def _is_video_tag_on_site(self):
        """Есть ли на сайте тэг video"""
        if self.soup.find_all('video'):
            return True

    @property
    def scripts(self):
        for script in self.soup.find_all('script'):
            yield str(script)


    @staticmethod
    def re_escape_html_chars(html_text):
        print('START RE', len(html_text))
        chars = [('&nbsp;', ' '), ('&quot;', '"'), ('&apos;', "'"), ('&&', '@@'), ('&', '&amp;&amp;'), ('@@', '&&')]
        for char, chat_to in chars:
            html_text = html_text.replace(char, chat_to)
        print('START RE', len(html_text))
        return html_text

    @staticmethod
    def escape_html_for_iframe(html_text):
        chars = [('&', '&amp;&amp;'), ('"', '&quot;'), ("'", '&apos;')]
        for char, chat_to in chars:
            html_text = html_text.replace(char, chat_to)
        return html_text

    @staticmethod
    def get_url_for_base_tag(url):
        if '?' in url:
            url = url.split('?')[0]
        if not url.endswith('/'):
            url += '/'
        return url

    def add_style_tag(self, style_text):
        DomFixxer.add_css(self.soup, style_text)

    def add_script_tag(self, scritp_text):
        DomFixxer.add_js(self.soup, scritp_text)

    def add_base_tag(self):
        url_base_tag = self.get_url_for_base_tag(self.url)
        DomFixxer.add_base_tag(self.soup, url_base_tag)

    def find_n_mark_img_doubles(self):
        base_url = self.get_url_for_base_tag(self.url)
        self.img_doubles = DomFixxer.find_double_img(self.soup, base_url=base_url)

    def drop_tags_from_dom(self, elems_ids):
        for id in elems_ids:
            elem = self.soup.find(id=id)
            if elem:
                elem.decompose()

    def get_human_land_text(self):
        clean_land_text = self.source_text.text
        clean_land_text += ' ' + self.title
        inputs = self.soup.find_all('input')
        placeholders_text = ['']
        for inpt in inputs:
            try:
                placeholder = inpt['placeholder']
                placeholders_text.append(placeholder)
            except KeyError:
                pass
        placeholders_text = ' '.join(placeholders_text)
        clean_land_text += placeholders_text
        return clean_land_text

    @property
    def title(self):
        return self._get_title()

    @staticmethod
    def find_yam(scripts_blocks):
        yam_link = 'https://mc.yandex.ru/metrika'
        yam_id = ';ym('
        if yam_link in scripts_blocks:
            pos = scripts_blocks.find(yam_id)
            if pos != -1:
                yam_id = scripts_blocks[pos + 4:pos + 12]
                return yam_id
            else:
                return 'not found'
        else:
            return False


class KMALand(Land):
    """Сайт KMA"""
    PRE_LAND_DOMAINS = ['blog-feed.org']
    LAND_ADMIN_UTM = 'ufl'
    STYLES_FILE = str(settings.BASE_DIR) + '/checker_2/checker_class/front_data/styles.css'
    JS_FILE = str(settings.BASE_DIR) + '/checker_2/checker_class/front_data/script.js'

    def __init__(self, source_text, url, **kwargs):
        super().__init__(source_text=source_text, url=url, **kwargs)
        self.__kma_script = self._find_kma_back_data()
        self.country = self._country()
        self.language = self._language()
        self.country_list = self._country_list()
        self.land_attrs = list()

    @staticmethod
    def format_url(url):
        url = url.strip()
        url = url.replace('https://', 'http://')
        return url

    def _find_kma_back_data(self) -> str:
        """Ищет и возвражает тело скрипта с переменными для лэндинга"""
        # soup = BeautifulSoup(self.source_text, 'html5')
        # scripts = soup.find_all('script')
        for script in self.scripts:
            if 'country_list' in script:
                return script

    def _country(self) -> str:
        """Поиск в js коде переменной country - возвращает ее значение"""
        block = re.search(r"country='\w\w'", self.__kma_script)
        country_w_brackets = re.search(r"'\w\w'", block.group(0))
        country = country_w_brackets.group(0).replace("'", '')
        return country.lower()

    def _language(self) -> str:
        """Поиск в js коде переменной language - возвращает ее значение"""
        block = re.search(r'"language":"\w\w"', self.__kma_script)
        language_w_brackets = re.search(r'"\w\w"', block.group(0))
        language = language_w_brackets.group(0).replace('"', '')
        return language.lower()

    def _country_list(self) -> dict:
        """Поиск в js коде переменной country_list - возвращает ее значение"""
        start = self.__kma_script.find('country_list=') + len('country_list=')
        end = self.__kma_script.find('}};') + 2
        var = self.__kma_script[start:end]
        country_list = json.loads(var)
        dic = dict()
        for k, v in country_list.items():
            dic[k.lower()] = v
        return dic

    def add_site_attrs(self):
        if self._is_video_tag_on_site():
            self.land_attrs.append('video')

        if len(self.country_list) > 1:
            self.land_attrs.append('more_one_select')

    @property
    def iframe_srcdoc(self):
        with open(self.STYLES_FILE, encoding='utf-8') as file:
            style_text = file.read()
            self.add_style_tag(style_text)
        with open(self.JS_FILE, encoding='utf-8') as file:
            js_text = file.read()
            self.add_script_tag(js_text)
        self.add_base_tag()
        self.find_n_mark_img_doubles()
        html_code = str(self.soup)
        html_code = self.escape_html_for_iframe(html_code)
        return html_code



    @staticmethod
    def find_social(scripts_blocks):
        socialFish = 'duhost'
        if socialFish in scripts_blocks:
            return True
        else:
            return False

    @property
    def discount_type(self):
        """Получить тип скидки"""
        discount = self.country_list[self.country]['discount']
        if int(discount) > 50:
            return 'low_price'
        else:
            return 'full_price'

    @property
    def land_type(self):
        """Получить тип сайта"""
        for domain in self.PRE_LAND_DOMAINS:
            if domain in self.url:
                return 'pre_land'
        return 'land'

    @property
    def s1(self):
        return self.country_list[self.country]['s1']

    @property
    def s2(self):
        return self.country_list[self.country]['s2']

    @property
    def s3(self):
        return self.country_list[self.country]['s3']

    @property
    def s4(self):
        return self.country_list[self.country]['s4']

    @property
    def discount(self):
        return self.country_list[self.country]['discount']

    @property
    def curr(self):
        return self.country_list[self.country]['curr']


if __name__ == '__main__':
    url = 'https://blog-feed.org/elle-breasty/?ufl=14926'
    res = req.get(url)
    kma = KMALand(url, res.text)
    print(kma.s1)
    print(kma.s2)
    print(kma.s3)
    print(kma.s4)
    print(kma.discount)
