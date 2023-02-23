from django import forms
from .models import CheckerUserSetting


class CheckerUserSettingsForm(forms.ModelForm):

    class Meta:
        model = CheckerUserSetting
        exclude = ['user']
