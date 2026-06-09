"""
Vercel Serverless entry point for Django.
Optimized for minimal cold-start time (< 10s).
"""
import os
import sys
import traceback

# === Path setup ===
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)

# === Environment (MUST be before any Django import) ===
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings_vercel')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# === Lazy ASGI singleton with error handling ===
_asgi_app = None
_init_error = None

def get_asgi():
    """Get or create the ASGI application."""
    global _asgi_app, _init_error
    if _init_error:
        raise _init_error
    if _asgi_app is None:
        try:
            import django
            django.setup()
            from django.core.asgi import get_asgi_application
            _asgi_app = get_asgi_application()
        except Exception as e:
            _init_error = e
            print(f"[Vercel] Django init FAILED:\n{traceback.format_exc()}")
            raise
    return _asgi_app


async def handler(request):
    """Vercel serverless function entry point."""
    try:
        app = get_asgi()
        return await app(request)
    except Exception as e:
        # Return a JSON error response instead of crashing silently
        error_msg = str(e)
        stack = traceback.format_exc()
        print(f"[Vercel] Request handler ERROR:\n{stack}")

        # Try to return a structured error response
        try:
            from django.http import JsonResponse
            response = JsonResponse({
                'error': 'Server Error',
                'detail': error_msg[:500],
                'type': type(e).__name__,
            }, status=503)
            # Convert Django response to ASGI response
            return response
        except Exception:
            # Fallback if even Django's response creation fails
            return {
                'statusCode': 503,
                'headers': {'Content-Type': 'application/json'},
                'body': f'{{"error":"Django init failed","detail":"{error_msg[:200]}"}}',
            }


# Compatibility exports
app = handler
try:
    application = get_asgi()
except Exception:
    application = handler  # Fallback: use raw handler if Django won't start
