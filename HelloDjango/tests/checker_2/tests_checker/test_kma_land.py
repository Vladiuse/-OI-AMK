import unittest
from bs4 import BeautifulSoup
from unittest.mock import MagicMock
from HelloDjango.checker_2.checker_class.land import Land
from HelloDjango.checker_2.checker_class.kma_land import KMALand
from HelloDjango.checker_2.checker_class.errors import NoUflParamPreLand, IncorrectPreLandUrl

LAND_LINK = 'http://x.ketomatcha-new.com/'
PRELAND_LINK = 'https://feed-news.org/visio-blog/?ufl=17446'

LAND_SCRIPT = """
<script>
var country='CZ',
user_country='BY',
lang='cs',
host='x.ketomatcha-new.com',tmp_data_to_server='/',tmp_data_request_id='aa74b43e35abfa166f6ea55b3d7b2062',
country_list={"CZ":
{"s1":920,"s2":0,"s3":920,"s4":1840,"discount":"50","curr":"CZK","specialfields":[],"rekv":"© All rights reserved\u003Cbr\u003E2023.\u003Cbr\u003E","campaign":"4573"},"ES":{"s1":39,"s2":0,"s3":39,"s4":78,"discount":"50","curr":"Euro","specialfields":[],"rekv":"© All rights reserved\u003Cbr\u003E2023.\u003Cbr\u003E","campaign":"4573"},
"HU":{"s1":11400,"s2":0,"s3":11400,"s4":22800,"discount":"50","curr":"HUF","specialfields":[],"rekv":"© All rights reserved\u003Cbr\u003E2023.\u003Cbr\u003E","campaign":"4573"},"IT":{"s1":39,"s2":0,"s3":39,"s4":78,"discount":"50","curr":"Euro","specialfields":[],"rekv":"© All rights reserved\u003Cbr\u003E2023.\u003Cbr\u003E","campaign":"4573"},
"PL":{"s1":155,"s2":0,"s3":155,"s4":310,"discount":"50","curr":"PLN","specialfields":[],"rekv":"© All rights reserved\u003Cbr\u003E2023.\u003Cbr\u003E","campaign":"4573"}};var list_of_parameters={"language":"cs","offer_id":"6445","landing":"19970","campaign":"4573","order_source":"1","request_id":"aa74b43e35abfa166f6ea55b3d7b2062","return_url":"http:\/\/x.ketomatcha-new.com"};var action_url='https://trackerlead.biz/';var source_popup_operator='13';var source_popup_out='12';var isJsonEnable=false;var text_item_is_free='zdarma';var KMAText={'validation_name':'Určete správný název.','validation_phone1':'Toto telefonní číslo může obsahovat pouze číslice, \"+\", \"-\", \"(\", \")\" a mezery.','validation_phone2':'Váš telefon je příliš malá čísla.','validation_phone3':'Váš telefon příliš mnoho číslic.','comebacker_text':'POZOR'};
</script>
"""
PRE_LAND_SCIPT = """
<script>
tmp_data_to_server="https://feed-news.org/";
country_list={"RS":{"s1":3690,"s2":0,"s3":3690,"s4":7380,"discount":"50","curr":"RSD","specialfields":[],"rekv":"Netline LLC\u003Cbr\u003E129281, Moscow, ul. Izumrudnaya, d. 13, k. 2, et. 1, pom. 1, kom. 2, of. 4\u003Cbr\u003E","campaign":"5917"}};json_query={"ufl":"17446"};
country='RS';action_url="https://trackerlead.biz/";request_id='5d96f689254d9fbf81eec11e2bf9cf8d';list_of_form_parameters='{"scenario":"normal_blog","language":"sr","offer_id":"7355","transit":"17446","campaign":"5917","order_source":"2","return_url":"https:\/\/feed-news.org\/visio-blog"}';city='Brest';isJsonEnable=0;text_item_is_free='besplatno';KMAText={'validation_name':'Napisite tačno ime i prezime.','validation_phone1':'Broj telefona moze da sadrzi samo cifre.simbole \"+\", \"-\", \"(\", \")\" i razmake.','validation_phone2':'U vasem telefonu je jako malo cifara!','validation_phone3':'Vaš telefon previše cifre.','comebacker_text':'WARNING'};
</script>

"""


class UrlKmaLandTest(unittest.TestCase):

    def test_validate_url_preland(self):
        kma = KMALand(PRE_LAND_SCIPT, PRELAND_LINK)
        self.assertEqual(kma.land_type, KMALand.PRE_LAND)

    def test_validate_url_preland_no_url(self):
        with self.assertRaises(NoUflParamPreLand) as conext:
            KMALand(PRE_LAND_SCIPT, f'http://{KMALand.MAIN_PRE_LAND_DOMAIN}/')

    def test_validate_url_incorrect_preland_url(self):
        self.assertRaises(IncorrectPreLandUrl, KMALand, PRE_LAND_SCIPT, f'http://{KMALand.INCORRECT_PRE_LAND_URLS}/')

    def test_validate_url_land_type(self):
        try:
            kma = KMALand(LAND_SCRIPT, LAND_LINK)
            self.assertTrue(kma.land_type, KMALand.LAND)
        except (IncorrectPreLandUrl, NoUflParamPreLand):
            self.fail()

    def test_prepare_url(self):
        for domain in KMALand.NOT_WORKED_PRE_LAND_DOMAINS:
            url = KMALand.prepare_url(f'http://{domain}/')
            self.assertTrue(KMALand.MAIN_PRE_LAND_DOMAIN in url)

    def test_display_url_land(self):
        kma = KMALand(LAND_SCRIPT, 'http://google.com/')
        self.assertEqual(kma.display_url, 'google.com/')

    def test_display_url_pre_land(self):
        kma = KMALand(PRE_LAND_SCIPT, PRELAND_LINK)
        self.assertEqual(kma.display_url, '/visio-blog/?ufl=17446')


class KmaLandAttrsTest(unittest.TestCase):

    # def setUp(self) -> None:
    #     self.KMA_MOCK_RU = KMALand
    #     self.KMA_MOCK_RU._find_kma_back_data = MagicMock(return_value='')
    #     self.KMA_MOCK_RU._country = MagicMock(return_value='ru')
    #     self.KMA_MOCK_RU._language = MagicMock(return_value='ru')
    #     self.KMA_MOCK_RU._country_list = MagicMock(return_value=[1,2,3])
    #     self.KMA_MOCK_RU._list_of_parameters = MagicMock(return_value='')

    def test_video_audio_in_text(self):
        html = """
        <video>123</video>
        <audio></audio>
        """

        kma = KMALand(html + LAND_SCRIPT, LAND_LINK)
        kma.add_site_attrs()
        self.assertTrue('video' in kma.land_attrs)
        self.assertTrue('audio' in kma.land_attrs)

    def test_many_country(self):
        kma = KMALand(LAND_SCRIPT, LAND_LINK)
        kma.country_list = [1, 2, 3, ]
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
        self.assertEqual(script, '<script>country_list="some";country="BY"</script>')

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
