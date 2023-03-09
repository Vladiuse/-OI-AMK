import unittest
from bs4 import BeautifulSoup
from unittest.mock import MagicMock
from HelloDjango.checker_2.checker_class.land import Land
from HelloDjango.checker_2.checker_class.kma_land import KMALand
from HelloDjango.checker_2.checker_class.errors import NoUflParamPreLand, IncorrectPreLandUrl

PRELAND_LINK = 'https://feed-news.org/visio-blog/?ufl=17446'

class UrlKmaLandTest(unittest.TestCase):

    def setUp(self):
        mock = MagicMock(return_value='')
        self.KMA_MOCK = KMALand
        self.KMA_MOCK._find_kma_back_data = mock
        self.KMA_MOCK._country = mock
        self.KMA_MOCK._language = mock
        self.KMA_MOCK._country_list = mock
        self.KMA_MOCK._list_of_parameters = mock
        self.KMA_MOCK._list_of_form_parameters = mock

    def test_validate_url_preland(self):
        kma = self.KMA_MOCK('', f'http://{KMALand.MAIN_PRE_LAND_DOMAIN}/ufl=100')
        self.assertEqual(kma.land_type, KMALand.PRE_LAND)

    def test_validate_url_preland_no_url(self):
        with self.assertRaises(NoUflParamPreLand) as conext:
            KMALand('', f'http://{KMALand.MAIN_PRE_LAND_DOMAIN}/')

    def test_validate_url_incorrect_preland_url(self):
        self.assertRaises(IncorrectPreLandUrl,self.KMA_MOCK, '', f'http://{KMALand.INCORRECT_PRE_LAND_URLS}/')


    def test_validate_url_land_type(self):
        try:
            kma = self.KMA_MOCK('', f'http://google.com/')
            self.assertTrue(kma.land_type, KMALand.LAND)
        except (IncorrectPreLandUrl, NoUflParamPreLand):
            self.fail()

    def test_prepare_url(self):
        for domain in KMALand.NOT_WORKED_PRE_LAND_DOMAINS:
            url = KMALand.prepare_url(f'http://{domain}/')
            self.assertTrue(KMALand.MAIN_PRE_LAND_DOMAIN in url)

    def test_display_url_land(self):
        mock = MagicMock(return_value=KMALand.LAND)
        kma = self.KMA_MOCK('', 'http://google.com/')
        kma._get_land_type = mock
        self.assertEqual(kma.display_url, 'google.com/')

    def test_display_url_pre_land(self):
        mock = MagicMock(return_value=KMALand.PRE_LAND)
        kma = self.KMA_MOCK('', 'http://google.com/some_path/#123')
        kma._get_land_type = mock
        self.assertEqual(kma.display_url, '/some_path/#123')


class KmaLandAttrsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.KMA_MOCK_RU = KMALand
        self.KMA_MOCK_RU._find_kma_back_data = MagicMock(return_value='')
        self.KMA_MOCK_RU._country = MagicMock(return_value='ru')
        self.KMA_MOCK_RU._language = MagicMock(return_value='ru')
        self.KMA_MOCK_RU._country_list = MagicMock(return_value=[1,2,3])
        self.KMA_MOCK_RU._list_of_parameters = MagicMock(return_value='')

    def test_video_audio_in_text(self):
        html = """
        <video>123</video>
        <audio></audio>
        """

        kma = self.KMA_MOCK_RU(html, 'https://google.com/')
        kma.add_site_attrs()
        self.assertTrue('video' in kma.land_attrs)
        self.assertTrue('audio' in kma.land_attrs)

    def test_many_country(self):
        kma = self.KMA_MOCK_RU('html', 'https://google.com/')
        kma.add_site_attrs()
        self.assertTrue('more_one_select' in kma.land_attrs)

class KmaLandBackDataTest(unittest.TestCase):

    def setUp(self) -> None:
        script_preland = """
<script>tmp_data_to_server="https://feed-news.org/";
country_list={"RS":{"s1":3690,"s2":0,"s3":3690,"s4":7380,
"discount":"50","curr":"RSD","specialfields":[],
"rekv":"Netline LLC\u003Cbr\u003E129281, Moscow, ul. Izumrudnaya, d. 13, k. 2, et. 1, pom. 1, kom. 2, of. 4\u003Cbr\u003E","campaign":"5917"}};
json_query={"ufl":"17446"};
country='RS';
action_url="https://trackerlead.biz/";
request_id='35d6f68a9d9cefb38d6337e585bdd8ba';
list_of_form_parameters='{"scenario":"normal_blog","language":"sr","offer_id":"7355","transit":"17446","campaign":"5917","order_source":"2","return_url":"https:\/\/feed-news.org\/visio-blog"}';
city='Brest';isJsonEnable=0;text_item_is_free='besplatno';
KMAText={'validation_name':'Napisite tačno ime i prezime.','validation_phone1':'Broj telefona moze da sadrzi samo cifre.simbole \"+\", \"-\", \"(\", \")\" i razmake.','validation_phone2':'U vasem telefonu je jako malo cifara!','validation_phone3':'Vaš telefon previše cifre.','comebacker_text':'WARNING'};</script>

        """

        self.kma = KMALand(script_preland, PRELAND_LINK)
    def test_find_back_data_script(self):
        script = """
        <script>some_code</script>
        <script>country_list="some";country="BY"</script>
          <script>some_code</script>
        """
        self.kma.soup = BeautifulSoup(script, 'lxml')
        script = self.kma._find_kma_back_data()
        self.assertEqual(script,'<script>country_list="some";country="BY"</script>')

    def test_get_prices(self):
        self.assertEqual(self.kma.s1, 3690)
        self.assertEqual(self.kma.s2, 0)
        self.assertEqual(self.kma.s3, 3690)
        self.assertEqual(self.kma.s4, 7380)

    def test_get_params(self):
        self.assertEqual(self.kma.curr, 'rsd')
        self.assertEqual(self.kma.discount, '50')

    def test_get_discount_type(self):
        self.assertEqual(self.kma.discount_type, KMALand.FULL_PRICE)
        self.kma.country_list['rs']['discount'] = '90.9'
        self.assertEqual(self.kma.discount_type, KMALand.LOW_PRICE)

    def test_get_discount_type1(self):
        self.assertEqual(self.kma.discount_type, KMALand.FULL_PRICE)

    def test_get_offer_id(self):
        self.assertEqual(self.kma.offer_id, '7355')






if __name__ == '__main__':
    unittest.main()




