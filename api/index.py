"""
Vercel Serverless entry point for Django.
Optimized for minimal cold-start time.
Uses ASGI handler compatible with @vercel/python@5.x
"""
import os
import sys
import traceback
import json

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


def _init_django():
    """Initialize Django exactly once."""
    global _asgi_app, _init_error
    if _asgi_app is not None or _init_error is not None:
        return

    try:
        import django
        django.setup()
        from django.core.asgi import get_asgi_application
        _asgi_app = get_asgi_application()
    except Exception as e:
        _init_error = e
        print(f"[Vercel] Django init FAILED:\n{traceback.format_exc()}", flush=True)


# Initialize Django at module load time (cold start)
_init_django()


async def application(scope, receive, send):
    """ASGI3 application - entry point for Vercel Python runtime."""
    # If Django failed to init, return error immediately
    if _init_error:
        error_msg = str(_init_error)
        await send({
            'type': 'http.response.start',
            'status': 503,
            'headers': [[b'content-type', b'application/json']],
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps({
                'error': 'Django init failed',
                'detail': error_msg[:500],
            }).encode(),
        })
        return

    # Delegate to Django's ASGI app
    try:
        await _asgi_app(scope, receive, send)
    except Exception as e:
        print(f"[Vercel] Request ERROR: {e}\n{traceback.format_exc()}", flush=True)
        try:
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [[b'content-type', b'application/json']],
            })
            await send({
                'type': 'http.response.body',
                'body': json.dumps({
                    'error': 'Request failed',
                    'detail': str(e)[:300],
                }).encode(),
            })
        except Exception:
            pass  # Headers already sent


# For older Vercel runtimes that expect a handler(request) function
def handler(request):
    """Legacy synchronous handler fallback."""
    import asyncio

    async def asgi_wrapper(scope, receive, send):
        await application(scope, receive, send)

    # Convert request to ASGI scope and run
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(asgi_wrapper(
            {
                'type': 'http',
                'method': request.get('method', 'GET'),
                'path': request.get('path', '/'),
                'query_string': request.get('query', '').encode(),
                'headers': [
                    [k.encode(), v.encode()] for k, v in request.get('headers', {}).items()
                ],
            },
            lambda: None,
            None,
        ))
    finally:
        loop.close()


app = application
