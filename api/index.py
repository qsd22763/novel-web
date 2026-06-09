"""
Vercel Serverless entry point for Django.
"""
import os
import sys

# === Path setup ===
# This file is at: project_root/api/index.py
# Django backend is at: project_root/novel_backend/
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)

# === Django settings ===
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')

# === Initialize Django ===
import django
django.setup()

# === WSGI application ===
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel Python runtime exports
app = application
handler = application
