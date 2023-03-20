from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import ActualUserList, CheckBlock, CheckPoint, UserSiteCheckPoint



class ActualUserListTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('test', 'some@mail.com', 'password')
        self.test_url = 'https://google.com '
        self.today = timezone.now().date()
        self.old_date = timezone.now().date() - timedelta(days=8)

    def create_check_list(self):
        for block_id in range(3):
            block = CheckBlock.objects.create(name='block_'+ str(block_id))
            for check_point_id in range(3):
                CheckPoint.objects.create(text='text', parent=block)

    def test_dell_old_user_lists(self):
        user_list = ActualUserList(
            user=self.user,
            url=self.test_url,
        )
        user_list.save()
        user_list.date = self.old_date
        user_list.save()
        ActualUserList.dell_old()
        self.assertEqual(ActualUserList.objects.count(), 0)

    def test_dell_old_not_old_date(self):
        user_list = ActualUserList(
            user=self.user,
            url=self.test_url,
        )
        user_list.save()
        user_list.date = self.today
        user_list.save()
        ActualUserList.dell_old()
        self.assertEqual(ActualUserList.objects.count(), 1)


    def test_test_dell_old_one_old_date(self):
        for i in range(2):
            user_list = ActualUserList(
                user=self.user,
                url=self.test_url + str(i),
            )
            user_list.save()
        user_list.date = self.old_date
        user_list.save()
        ActualUserList.dell_old()
        self.assertEqual(ActualUserList.objects.count(), 1)

    def test_create_check_list(self):
        self.create_check_list()
        blocks_count = CheckBlock.objects.count()
        check_points_count = CheckPoint.objects.count()
        self.assertEqual(blocks_count, 3)
        self.assertEqual(check_points_count, 9)

    def test_delete_check_point_if_block_dell(self):
        self.create_check_list()
        CheckBlock.objects.all().delete()
        self.assertEqual(CheckPoint.objects.count(), 0)

    def test_create_new_user_check_list(self):
        self.create_check_list()
        ActualUserList.get_or_create(self.user, self.test_url)
        user_check_point_count = UserSiteCheckPoint.objects.count()
        self.assertEqual(user_check_point_count, 9)

    def test_get_or_create_not_create(self):
        self.create_check_list()
        ActualUserList.objects.create(user=self.user, url=self.test_url)
        self.assertEqual(UserSiteCheckPoint.objects.count(), 0)
        # get or create
        ActualUserList.get_or_create(self.user, self.test_url)
        self.assertEqual(UserSiteCheckPoint.objects.count(), 0)

    def test_create_user_check_list_2_users_one_link(self):
        self.create_check_list()
        second_user = User.objects.create_user('second_user', 'xxx@mail.com', 'password')
        ActualUserList.get_or_create(self.user, self.test_url)
        ActualUserList.get_or_create(second_user, self.test_url)
        count_of_user_check_points = UserSiteCheckPoint.objects.count()
        self.assertEqual(count_of_user_check_points, 9 * 2)


    def test_add_user_site_check_point_if_add_new_check_point(self):
        self.create_check_list()
        block = CheckBlock.objects.last()
        ActualUserList.get_or_create(self.user, self.test_url)
        self.assertEqual(UserSiteCheckPoint.objects.count(),9)
        new_check = CheckPoint(text='some text', parent=block)
        new_check.save()
        self.assertEqual(UserSiteCheckPoint.objects.count(),10)

    def test_add_user_site_check_point_if_edit_check_point(self):
        self.create_check_list()
        ActualUserList.get_or_create(self.user, self.test_url)
        check_point = CheckPoint.objects.last()
        check_point.text = 'dasdas'
        check_point.save()
        self.assertEqual(CheckPoint.objects.count(), 9)






