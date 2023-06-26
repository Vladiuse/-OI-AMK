from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User


class CopyPasteText(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name =  models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self):
        return self.name


class ActualCountryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(phone='')


class Country(models.Model):
    objects = models.Manager()
    actual = ActualCountryManager()

    iso = models.CharField(
        max_length=2,
        verbose_name='Код страны ISO',
        unique=True,
        primary_key=True,
    )
    iso3 = models.CharField(
        max_length=3,
        verbose_name='ISO 3',
        unique=True,
        blank=True,
        null=True,
    )
    ru_full_name = models.CharField(
        max_length=60,
        verbose_name='Русское название',
        blank=True,
        unique=True,
    )
    phone = models.CharField(
        max_length=15,
        verbose_name='Валидный номер',
        blank=True,
    )
    phone_code = models.CharField(
        max_length=15,
        verbose_name='Моб код страны',
        blank=True,
    )
    words = models.JSONField(
        default={"words": [], "templates": []},
        verbose_name='Слова под гео'
    )
    language = models.ManyToManyField(
        'Language',
        blank=True,
    )
    curr = models.ManyToManyField(
        'Currency',
        blank=True,
    )

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.pk.upper()

    @staticmethod
    def get_country_phone(*countrys_iso) -> dict:
        """Возвразает словарь
        ключ:county_iso
        значение: номер телефона
        """
        phones = Country.objects.filter(iso__in=countrys_iso).values()
        country_phone = dict()
        for p in phones:
            dic = {p['iso']: p['phone']}
            country_phone.update(dic)
        return country_phone


class CityToTextSearchManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(use_in_text_search=False)


class City(models.Model):
    objects = models.Manager()
    text_search = CityToTextSearchManager()

    name = models.CharField(
        max_length=50,
        verbose_name='Название города',
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
    )
    use_in_text_search = models.BooleanField(default=True)

    class Meta:
        unique_together = [['name', 'country'], ]

    def save(self, **kwargs):
        self.name = self.name.lower()
        self.name = self.name.strip()
        super().save()

    def __str__(self):
        return self.name


class Language(models.Model):
    iso = models.CharField(
        max_length=2,
        verbose_name='Код iso языка',
        primary_key=True)
    russian_name = models.CharField(
        max_length=25,
        verbose_name='Русское название',
        blank=True
    )

    class Meta:
        ordering = ['iso']

    def __str__(self):
        return f'{self.russian_name}({self.iso.upper()})'


class ActualCurrencyManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().annotate(count=Count('country')).filter(count__gt=0)


class Currency(models.Model):
    objects = models.Manager()
    actual = ActualCurrencyManager()

    name = models.CharField(
        max_length=60,
        verbose_name='Название валюты'
    )
    iso = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name='Код валюты',
        unique=True)
    iso_3366 = models.CharField(
        max_length=3,
        verbose_name='ISO 3166-1',
        unique=True,
        blank=True,
        null=True
    )
    kma_code = models.CharField(
        max_length=5,
        verbose_name='Валюта в кма',
        blank=True,
        default=''
    )

    def __str__(self):
        return f'<{self.iso.upper()}> {self.name}'


class KmaCurrency(Currency):
    class Meta:
        proxy = True

    @property
    def main_curr(self):
        if self.kma_code:
            return self.kma_code
        return self.iso

    @property
    def other_currs(self):
        other = []
        if self.kma_code:
            other = [self.iso]
        if self.iso_3366:
            other.append(self.iso_3366)
        return other


class OfferPosition(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Оффер',
        unique=True,
    )

    def save(self, **kwargs):
        self.name = str(self.name).lower()
        super().save(**kwargs)

    def __str__(self):
        return str(self.name).title()

    class Meta:
        verbose_name = 'Оффер'
        verbose_name_plural = 'Офферы'


class UserApiKey(models.Model):
    token = models.CharField(
        max_length=40,
        unique=True,
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.user.username
