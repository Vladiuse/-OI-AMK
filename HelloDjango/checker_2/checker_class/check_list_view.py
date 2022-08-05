from checker_2.models import CheckPoint, CheckBlock


class CheckListView:

    def __init__(self, *, land_type, discount_type, country, lang):
        self.land_type = land_type
        self.discount_type = discount_type
        self.country = country
        self.lang = lang
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
                (self.lang in check_point.for_lang or check_point.for_lang == ''):
            return True

    def process(self):
        all = CheckBlock.objects.prefetch_related('checkpoint_set').all()
        for b in all:
            dic = {
                'name': b.name,
                'subs': []
            }
            for c in b.checkpoint_set.all():
                if self.is_need_add(c):
                    dic['subs'].append(c.text)
            if dic['subs']:
                self.check_list.append(dic)