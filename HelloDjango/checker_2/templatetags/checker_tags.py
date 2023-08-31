from django import template
import os
register = template.Library()

def file_ext(value):
    return os.path.splitext(value)[1]

register.filter('file_ext',file_ext)