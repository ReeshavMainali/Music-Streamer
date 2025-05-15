"""
WSGI config for melostream project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melostream.settings')

application = get_wsgi_application()