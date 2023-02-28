from checker_2.models import CheckPoint, CheckBlock, UserSiteCheckPoint, ActualUserList
from django.db.models import Q, Prefetch

def get_check_list(land, user):
    user_check_list = ActualUserList.get_or_create(user,land.url)
    user_check_points = UserSiteCheckPoint.objects.filter(user_list=user_check_list)
    checks = CheckPoint.objects.filter(
        Q(land_type__iexact=land.land_type) | Q(land_type__iexact=''),
        Q(discount_type__iexact=land.discount_type) | Q(discount_type__iexact=''),
        Q(for_geo__icontains=land.country) | Q(for_geo__iexact=''),
        Q(for_lang__icontains=land.language) | Q(for_lang__iexact=''),
        Q(filter__in=land.land_attrs) | Q(filter__iexact=''),
    )
    blocks_w_checks = CheckBlock.objects.prefetch_related(
        Prefetch('checkpoint_set', queryset=checks)
    ).prefetch_related(
        Prefetch('checkpoint_set__usersitecheckpoint_set', queryset=user_check_points)
    )
    return blocks_w_checks
