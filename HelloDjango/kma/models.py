from django.db import models

class DefaultWeb(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя веба', unique=True)

    def __str__(self):
        return self.name

class PhoneNumber(models.Model):
    short = models.CharField(max_length=2, verbose_name='Код страны', unique=True)
    phone = models.CharField(max_length=15, verbose_name='Валидный номер')
    ru_full_name = models.CharField(max_length=20, verbose_name='Русское название', blank=True, unique=True)




