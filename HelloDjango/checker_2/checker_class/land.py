from bs4 import BeautifulSoup
from .dom_fixxer import DomFixxerMixin
import re
from .errors import CheckerError
from bs4.element import Tag
from urllib.parse import urlparse, urlunparse

class Land(DomFixxerMixin):

    TYPES_REL = ['shortcut icon', 'icon', 'apple-touch-icon', 'apple-touch-icon-precomposed', 'image/x-icon']

    def __init__(self, source_text, actual_user_list, *, parser='html5lib',):
        self.source_text = source_text
        self.actual_user_list = actual_user_list
        self.url = self.actual_user_list.url
        self.soup = BeautifulSoup(self.source_text, parser)
        self._human_text = None
        self._human_land_text_lower = None
        self.img_doubles = None
        self._dates = None
        self._years = None
        self.land_attrs = None



    @staticmethod
    def prepare_url(url):
        url = url.strip()
        url = url.replace('https://', 'http://')
        return url

    def get_no_protocol_url(self):
        url = self.url
        for s in 'https://','http://':
            url = url.replace(s,'')
        return url

    @property
    def display_url(self):
        return self.get_no_protocol_url()

    @property
    def base_url(self):
        return self.get_url_for_base_tag(self.url)


    def get_url_for_base_tag(self,url):
        s, n, p, a, q, frag = urlparse(url)
        base_url = urlunparse([s, n, p, '', '', ''])
        return base_url


    @property
    def title(self):
        return self._get_title()

    def _find_years(self, text):
        pattern = '\D(19\d\d|20\d\d|25\d\d)\D'
        years_in_text = re.findall(pattern, text)
        clean_years = []
        for year in years_in_text:
            clean_year = re.sub('\D', '', year)
            clean_years.append(clean_year)
        return clean_years

    def _find_dates(self, text):
        date_in_text = []
        clean_dates = []
        pattern_d_m_y = '\D\d{1,2}[.\\\/-]\d{1,2}[.\\\/-]\d{4}\D'
        pattern_y_m_d = '\D\d{4}[.\\\/-]\d{1,2}[.\\\/-]\d{1,2}\D'
        pattern_6_digit = '\D\d{2}[.\\\/]\d{1,2}[.\\\/]\d{1,2}\D|\Dd{1,2}[.\\\/]\d{1,2}[.\\\/]\d{2}\D'
        for pattern in pattern_d_m_y,pattern_y_m_d, pattern_6_digit:
            dates = re.findall(pattern,text)
            date_in_text.extend(dates)

        for date in date_in_text:
            clean_date = date[1:-1]
            clean_dates.append(clean_date)
        return clean_dates


    def _find_dates_n_years(self):
        text = self.human_text
        self._dates = self._find_dates(text)
        for date in self._dates:
            text = text.replace(date, '')
        self._years = self._find_years(text)

    @property
    def unique_words(self):
        unique = set()
        word = ''
        for char in self.human_text_lower:
            if char.isalpha() or char.isdigit() or char == '-':
                word += char
            else:
                unique.add(word)
                word = ''
        else:
            unique.add(word)
        unique = filter(lambda word: len(word) >= 3, unique)
        return set(unique)

    @property
    def years(self):
        if self._years is None:
            self._find_dates_n_years()
        return self._years

    @property
    def dates(self):
        if self._dates is None:
            self._find_dates_n_years()
        return self._dates

    def _get_title(self):
        """найти title сайта"""
        title = self.soup.find('title')
        return title.text

    def is_html_tag_on_page(self, tag_name):
        if self.soup.find(tag_name):
            return True

    def _is_video_tag_on_site(self):
        """Есть ли на сайте тэг video"""
        return self.is_html_tag_on_page('video')

    def _is_audio_tag_on_site(self):
        """Есть ли на сайте тэг audio"""
        return self.is_html_tag_on_page('audio')

    def get_favicon_links(self, add_base_url=True):
        links = self.soup.find_all('link')
        links = list(filter(self.is_favicon_links, links))
        if add_base_url:
            for link in links:
                if not link['href'].startswith('http'):
                    link['href'] = self.get_url_for_base_tag(self.base_url) + link['href']
        links = list(map(lambda link: str(link), links))
        return links

    @staticmethod
    def is_favicon_links(link:Tag):
        if not isinstance(link, Tag):
            raise CheckerError
        try:
            if not link['href']:
                return False
        except KeyError:
            return False
        res = []
        for attr in ['rel', 'type']:
            try:
                a = link[attr]
                if isinstance(a, str):
                    res.append(a)
                if isinstance(a, list):
                    res.extend(a)
            except KeyError:
                pass
        for attr in res:
            if attr in Land.TYPES_REL:
                return True

    @property
    def scripts(self):
        for script in self.soup.find_all('script'):
            yield str(script)

    def add_site_attrs(self):
        self.land_attrs = []
        if self._is_video_tag_on_site():
            self.land_attrs.append('video')

        if self._is_audio_tag_on_site():
            self.land_attrs.append('audio')


    def find_n_mark_img_doubles(self):
        # base_url = self.get_url_for_base_tag(self.url)
        self.img_doubles = DomFixxerMixin.find_double_img(self.soup, base_url=self.base_url)

    def drop_tags_from_dom(self, elems_ids):
        for id in elems_ids:
            elem = self.soup.find(id=id)
            if elem:
                elem.decompose()
    @property
    def human_text(self):
        if self._human_text is None:
            clean_land_text = self.soup.text
            clean_land_text += ' '.join(self._human_text_from_placeholders())
            clean_land_text += ' '.join(self._human_text_from_input_values())
            self._human_text = clean_land_text
        return self._human_text

    def _human_text_from_placeholders(self) -> list:
        inputs = self.soup.find_all('input')
        placeholders_text = list()
        for inpt in inputs:
            try:
                placeholder = inpt['placeholder']
                placeholders_text.append(placeholder)
            except KeyError:
                pass
        return placeholders_text

    def _human_text_from_input_values(self) -> list:
        inputs = self.soup.find_all('input')
        values = []
        for inp in inputs:
            value = ''
            is_hidden = False
            try:
                value = inp['value']
            except KeyError:
                pass
            try:
                if inp['type'] == 'hidden':
                    is_hidden = True
            except KeyError:
                pass
            if value and not is_hidden:
                values.append(value)
        return values

    @property
    def human_text_lower(self):
        if not self._human_land_text_lower:
            self._human_land_text_lower = self.human_text.lower()
        return self._human_land_text_lower

    def is_yam_script(self):
        yam_link = 'https://mc.yandex.ru/metrika'
        for script in self.scripts:
            if yam_link in script:
                return True
