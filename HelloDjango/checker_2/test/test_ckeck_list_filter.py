from django.test import TestCase
from django.contrib.auth.models import User
from ..models import CheckBlock, CheckPoint
from ..checker_class.kma_land import KMALand

class FakeLand:

    def __init__(self, land_type='', discount_type='', country='', language=''):
        self.url = 'https://google.com/'
        self.land_type = land_type
        self.discount_type = discount_type
        self.country = country
        self.language = language
        self.land_attrs = []


class CheckPointFilterTest(TestCase):

    def setUp(self) -> None:
        self.block = CheckBlock.objects.create(name='xxx')
        self.user = User.objects.create_user('vlad', 'some@gmail.com', 'password')
        self.check_point_no_type = CheckPoint.objects.create(text='', parent=self.block)


    def test_check_list_filter_land_type(self):
        # create
        check_point_land = CheckPoint.objects.create(text='', parent=self.block, land_type=KMALand.LAND)
        check_point_preland = CheckPoint.objects.create(text='', parent=self.block, land_type=KMALand.PRE_LAND)

        land = FakeLand(land_type=KMALand.LAND)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(check_point_land in check_points)
        self.assertTrue(check_point_preland not in check_points)

    def test_check_list_filter_pre_land_type(self):
        # create
        check_point_land = CheckPoint.objects.create(text='', parent=self.block, land_type=KMALand.LAND)
        check_point_preland = CheckPoint.objects.create(text='', parent=self.block, land_type=KMALand.PRE_LAND)

        land = FakeLand(land_type=KMALand.PRE_LAND)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(check_point_preland in check_points)
        self.assertTrue(check_point_land not in check_points)


    def test_check_list_filter_discount_type_full(self):
        #create
        check_point_full_price = CheckPoint.objects.create(text='', parent=self.block, discount_type=KMALand.FULL_PRICE)
        check_point_full_low_price = CheckPoint.objects.create(text='', parent=self.block, discount_type=KMALand.LOW_PRICE)

        land = FakeLand(discount_type=KMALand.FULL_PRICE)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(check_point_full_price in check_points, 'фулл прайс есть в списке')
        self.assertTrue(check_point_full_low_price not in check_points , 'лой прайс не в списке')

    def test_check_list_filter_discount_type_low(self):
        #create
        check_point_full_price = CheckPoint.objects.create(text='', parent=self.block, discount_type=KMALand.FULL_PRICE)
        check_point_full_low_price = CheckPoint.objects.create(text='', parent=self.block, discount_type=KMALand.LOW_PRICE)

        land = FakeLand(discount_type=KMALand.LOW_PRICE)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(check_point_full_price not in check_points,  'фулл прайс не в списке')
        self.assertTrue(check_point_full_low_price in check_points, 'лой прайс в списке')


    def test_filter_country_one_set(self):
        #create
        ru_check_point = CheckPoint.objects.create(text='', parent=self.block, for_geo='ru')
        by_check_point = CheckPoint.objects.create(text='', parent=self.block, for_geo='by')

        land = FakeLand(country='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(ru_check_point in check_points)
        self.assertTrue(by_check_point not in check_points)

    def test_filter_country_many_set(self):
        multi_country_check = CheckPoint.objects.create(text='', parent=self.block, for_geo='ru,by,ua,de')
        land = FakeLand(country='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(multi_country_check in check_points)

    def test_filter_country_many_set_variants(self):
        vars = [
            ['ru, by, ua, de', 'с пробелами'],
            [' ru,by,ua,de ', 'с пробелами вначале и конце'],
            ['by,ua,ru', 'нужное гео в конце без зяпятой'],
            ['by,ua,ru,', 'нужное гео в конце c зяпятой'],
        ]
        land = FakeLand(country='ru')
        for geo, msg in vars:
            CheckPoint.objects.create(text='', parent=self.block, for_geo=geo)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), len(vars) + 1)

    def test_filter_country_many_set_variants_co_current(self):
        vars = [
            ['by, ua, de', 'с пробелами'],
            ['by,ua,de ', 'с пробелами вначале и конце'],
            ['by,ua', 'нужное гео в конце без зяпятой'],
            ['by,ua,', 'нужное гео в конце c зяпятой'],
        ]
        land = FakeLand(country='ru')
        for geo, msg in vars:
            CheckPoint.objects.create(text='', parent=self.block, for_geo=geo)
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points),1)


    def test_filter_lang_one_set(self):
        #create
        ru_check_point = CheckPoint.objects.create(text='', parent=self.block, for_lang='ru')
        by_check_point = CheckPoint.objects.create(text='', parent=self.block, for_lang='by')

        land = FakeLand(language='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(ru_check_point in check_points)
        self.assertTrue(by_check_point not in check_points)

    def test_filter_lang_many_set(self):
        ru_check_point = CheckPoint.objects.create(text='', parent=self.block, for_lang='ru,en,ar')
        by_check_point = CheckPoint.objects.create(text='', parent=self.block, for_lang='by')
        land = FakeLand(language='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 2)
        self.assertTrue(ru_check_point in check_points)
        self.assertTrue(by_check_point not in check_points)

    def test_filter_lang_many_vars(self):
        vars = [
            ['ru, by, ua, de', 'с пробелами'],
            [' ru,by,ua,de ', 'с пробелами вначале и конце'],
            ['by,ua,ru', 'нужное гео в конце без зяпятой'],
            ['by,ua,ru,', 'нужное гео в конце c зяпятой'],
        ]
        for lang, msg in vars:
            CheckPoint.objects.create(text='', parent=self.block, for_lang=lang)
        land = FakeLand(language='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), len(vars)+1)

    def test_filter_lang_many_no_vars(self):
        vars = [
            ['by, ua, de', 'с пробелами'],
            ['by,ua,de ', 'с пробелами вначале и конце'],
            ['by,ua', 'нужное гео в конце без зяпятой'],
            ['by,ua,', 'нужное гео в конце c зяпятой'],
        ]
        for lang, msg in vars:
            CheckPoint.objects.create(text='', parent=self.block, for_lang=lang)
        land = FakeLand(language='ru')
        check_points = CheckPoint.filter_check_points(land)
        self.assertEqual(len(check_points), 1)

    def test_filter_other_attrs_in(self):
        check = CheckPoint.objects.create(text='', parent=self.block, filter='some-filter')
        land = FakeLand()
        land.land_attrs.append('some-filter')
        check_points = CheckPoint.filter_check_points(land)
        self.assertTrue(len(check_points), 2)
        self.assertTrue(check in check_points)

    def test_filter_other_attrs_no_find(self):
        check = CheckPoint.objects.create(text='', parent=self.block, filter='some-filter')
        land = FakeLand()
        check_points = CheckPoint.filter_check_points(land)
        self.assertTrue(len(check_points), 1)
        self.assertTrue(check not in check_points)

    def test_filter_other_attrs_many_filters_find_all(self):
        check_1 = CheckPoint.objects.create(text='', parent=self.block, filter='some-filter')
        check_2 = CheckPoint.objects.create(text='', parent=self.block, filter='another-filter')
        land = FakeLand()
        land.land_attrs = ['some-filter','another-filter']
        check_points = CheckPoint.filter_check_points(land)
        self.assertTrue(len(check_points), 3)
        for check in check_1, check_2:
            self.assertTrue(check in check_points)

    def test_filter_other_attrs_many_filters_find_some(self):
        check_1 = CheckPoint.objects.create(text='', parent=self.block, filter='some-filter')
        check_2 = CheckPoint.objects.create(text='', parent=self.block, filter='another-filter')
        check_3 = CheckPoint.objects.create(text='', parent=self.block, filter='no_need_find')
        land = FakeLand()
        land.land_attrs = ['some-filter','another-filter']
        check_points = CheckPoint.filter_check_points(land)
        self.assertTrue(len(check_points), 3)
        self.assertTrue(check_3 not in check_points)







