"""
Vercel Serverless entry point for Django.
Optimized for minimal cold-start time (< 10s).

Key optimizations:
- All heavy imports at module level (build-time pre-warming)
- Lazy ASGI creation with singleton pattern
- No redundant re-initialization per request
"""
import os
import sys

# === Path setup ===
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)
sys.path.insert(0, _BACKEND_DIR)  # Ensure it's first

# === Environment (MUST be before any Django import) ===
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings_vercel')
# Tell Django we're in an async/ASGI context
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# === Pre-import Django core (module-level = happens at cold start) ===
import django
from django.core.asgi import get_asgi_application

# === Singleton: Initialize Django ONCE and reuse ===
_asgi_app = None

def get_asgi():
    """Get or create the ASGI application (lazy singleton)."""
    global _asgi_app
    if _asgi_app is None:
        django.setup()
        _asgi_app = get_asgi_application()
    return _asgi_app

# === Vercel handler ===
async def handler(request):
    """Vercel serverless function entry point."""
    app = get_asgi()
    return await app(request)

# Compatibility exports
app = handler
application = get_asgi()
