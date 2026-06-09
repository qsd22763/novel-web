"""
Vercel Serverless entry point for Django.
Uses ASGI handler for better compatibility with Vercel's Python runtime.
"""
import os
import sys

# === Path setup ===
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)

# === Django settings (must be before any Django import) ===
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# === Lazy Django initialization ===
# Only initialize once, reuse the app for subsequent requests
_app = None

def get_app():
    global _app
    if _app is None:
        import django
        django.setup()
        from django.core.asgi import get_asgi_application
        _app = get_asgi_application()
    return _app

# === Vercel handler ===
async def handler(request):
    """ASGI handler for Vercel serverless."""
    app = get_app()
    return await app(request)

# Also export WSGI-style for compatibility
app = handler
