from checker_2.models import CheckPoint, CheckBlock, UserSiteCheckPoint, ActualUserList


class CheckListView:

    def __init__(self, *, land_type, discount_type, country, lang, land_attrs, user, url):
        self.land_type = land_type
        self.discount_type = discount_type
        self.country = country
        self.lang = lang
        self.user = user
        self.url = url
        self.land_attrs = land_attrs
        self.check_list = list()

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self.check_list):
            raise StopIteration
        block = self.check_list[self.i]
        self.i += 1
        return block

    def is_need_add(self, check_point):
        if check_point.land_type in [self.land_type, None] and \
                check_point.discount_type in [self.discount_type, None] and \
                (self.country in check_point.for_geo or check_point.for_geo == '') and \
                (self.lang in check_point.for_lang or check_point.for_lang == '') and \
                (check_point.filter in self.land_attrs or check_point.filter == ''):
            return True

    def process(self):
        all = CheckBlock.objects.prefetch_related('checkpoint_set').all()
        # try:
        #     print(ActualUserList.objects.get(user=self.user, url=self.url), 'xxxxxxxxxx')
        #     user_check_list = UserSiteCheckPoint.get_user_ckecklist_dict(user_model=self.user, url=self.url)
        #     print('Загружен созданый')
        # except ActualUserList.DoesNotExist as error:
        #     new_ckeck_list_record = ActualUserList(user=self.user, url=self.url)
        #     new_ckeck_list_record.save()
        #     user_check_list = UserSiteCheckPoint.make_user_url_list(user_model=self.user, url=self.url)
        #     print('СОЗДАН НОВЫЙ!!!')
        user_check_list = UserSiteCheckPoint.get_list(user_model=self.user, url=self.url)
        for b in all:
            dic = {
                'name': b.name,
                'subs': []
            }
            for c in b.checkpoint_set.all():
                if self.is_need_add(c):
                    c.is_checked = user_check_list[c.id]['is_checked']
                    dic['subs'].append(c)
            # если блок чеклиста имеет пункты проверки(не пуст)
            if dic['subs']:
                self.check_list.append(dic)
