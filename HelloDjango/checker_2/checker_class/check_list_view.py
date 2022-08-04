from checker_2.models import CheckPoint, CheckBlock


class CheckListView:

    def __init__(self, *, land_type, discount_type, country, lang):
        self.land_type = land_type
        self.discount_type = discount_type
        self.country = country
        self.lang = lang

    def is_need_add(self, check_point):
        if check_point.land_type in [self.land_type, None] and \
                check_point.discount_type in [self.discount_type, None] and \
                (self.country in check_point.for_geo or check_point.for_geo == '') and \
                (self.lang in check_point.for_lang or check_point.for_lang == ''):
            return True

    def get_list(self):
        all = CheckBlock.objects.prefetch_related('checkpoint_set').all()
        res = list()
        for b in all:
            dic = {
                'name': b.name,
                'subs': []
            }
            for c in b.checkpoint_set.all():
                if self.is_need_add(c):
                    dic['subs'].append(c.text)
            if dic['subs']:
                res.append(dic)
        return res
