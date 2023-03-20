from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import ActualUserList



class ActualUserListTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('test', 'some@mail.com', 'password')
        self.test_url = 'https://google.com'
        self.today = timezone.now().date()
        self.old_date = timezone.now().date() - timedelta(days=8)

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


