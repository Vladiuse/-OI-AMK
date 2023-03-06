from bs4 import BeautifulSoup
from .dom_fixxer import DomFixxer
import re

class Land:

    TYPES_REL = ['shortcut icon', 'icon', 'apple-touch-icon', 'apple-touch-icon-precomposed', 'image/x-icon']

    def __init__(self, source_text, url, *, parser='html5lib', escape_chars=False):
        self.source_text = Land.re_escape_html_chars(source_text) if escape_chars else source_text
        self.url = url
        self.soup = BeautifulSoup(self.source_text, parser)
        self.human_text = None
        self._human_land_text_lower = None
        self.img_doubles = None
        self._dates = None
        self._years = None

        with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/media/tech/checker/source.html', 'w') as file:
            file.write(source_text)

    def find_dates(self):
        pattern = '19\d\d|20\d\d|\d{1,2}[.\\\/]\d{1,2}[.\\\/]\d{2,4}'  # убран захват символов перед датой
        text = self.human_text
        dates_n_years = re.findall(pattern, text)
        dates_n_years = list(set(dates_n_years))
        self._dates = []
        self._years = []
        for i in dates_n_years:
            if len(i) == 4:
                self._years.append(i)
            else:
                self._dates.append(i)

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
        unique = filter(lambda word: len(word) >= 3, unique)
        return set(unique)

    @property
    def years(self):
        if self._years is None:
            self.find_dates()
        return self._years

    @property
    def dates(self):
        if self._dates is None:
            self.find_dates()
        return self._dates

    def get_no_protocol_url(self):
        return self.url.replace('http://', '')

    def _get_title(self):
        """найти title сайта"""
        title = self.soup.find('title')
        return title.text

    def _is_video_tag_on_site(self):
        """Есть ли на сайте тэг video"""
        if self.soup.find_all('video'):
            return True

    def get_favicon_links(self, add_base_url=True):
        links = self.soup.find_all('link')
        links = list(filter(self.is_favicon_links, links))
        if add_base_url:
            for l in links:
                try:
                    if not l['href'].startswith('http'):
                        l['href'] = Land.get_url_for_base_tag(self.url) + l['href']
                        yield str(l)
                except KeyError:
                    pass

    @staticmethod
    def is_favicon_links(link):
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

    @staticmethod
    def re_escape_html_chars(html_text):
        chars = [('&copy;', '©'), ('&#8211;', '-'), ('&#8220;', '“'), ('&#8221;', '”'), ('&#39;', "'"), ('&nbsp;', ' '),
                 ('&quot;', '"'),
                 ('&apos;', "'"),
                 ('&&', '@@'), ('&', '&amp;&amp;'), ('@@', '&&')]
        for char, chat_to in chars:
            html_text = html_text.replace(char, chat_to)
        return html_text

    @staticmethod
    def escape_html_for_iframe(html_text):
        chars = [
            # ('&', '&amp;&amp;'),
            ('"', '&quot;'), ("'", '&apos;')]
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
        if not self.human_text:
            clean_land_text = self.soup.text
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
            self.human_text = clean_land_text
            with open('/home/vlad/PycharmProjects/-OI-AMK/HelloDjango/media/tech/checker/text.html', 'w') as file:
                file.write(self.human_text_lower)
        return self.human_text

    @property
    def human_text_lower(self):
        if not self._human_land_text_lower:
            self._human_land_text_lower = self.get_human_land_text().lower()
        return self._human_land_text_lower

    @property
    def title(self):
        return self._get_title()

    def is_yam_script(self):
        yam_link = 'https://mc.yandex.ru/metrika'
        for script in self.scripts:
            if yam_link in script:
                return True
