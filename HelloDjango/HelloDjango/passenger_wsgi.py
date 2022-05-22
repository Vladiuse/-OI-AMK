"""
WSGI config for HelloDjango project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os, sys
from django.core.wsgi import get_wsgi_application

site_user_root_dir = '/home/v/vladiuse/kma_oi/public_html'
sys.path.insert(0, os.path.join(site_user_root_dir, 'HelloDjango'))
sys.path.insert(1, os.path.join(site_user_root_dir, 'venv/lib/python3.6/site-packages'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HelloDjango.settings')

application = get_wsgi_application()
