import unittest
from unittest.mock import MagicMock
from HelloDjango.checker_2.checker_class.kma_land import KMALand
from HelloDjango.checker_2.checker_class.errors import NoUflParamPreLand, IncorrectPreLandUrl

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


if __name__ == '__main__':
    unittest.main()



