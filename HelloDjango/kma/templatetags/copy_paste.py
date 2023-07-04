from django.template import Library
from kma.models import CopyPasteText
from django.shortcuts import get_object_or_404

register = Library()


@register.simple_tag
def copy_paste(id):
    obj = get_object_or_404(CopyPasteText,pk=id)
    return obj.text

