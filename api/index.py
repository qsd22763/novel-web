"""
Vercel Serverless entry point - Minimal version.
Tests if Python + Django can even start on Vercel.
"""
import os
import sys
import json
import traceback

# Path setup
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)

# Environment BEFORE Django imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings_vercel')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


def handler(request):
    """Synchronous handler - simplest possible entry point."""
    try:
        # Step 1: Try importing django
        import django
        django_version = django.VERSION

        # Step 2: Try django.setup()
        django.setup()

        # Step 3: Get WSGI application
        from django.core.wsgi import get_wsgi_application
        wsgi_app = get_wsgi_application()

        # Step 4: Process the request through Django
        from io import BytesIO
        from wsgiref.headers import Headers

        method = request.get('method', 'GET')
        path = request.get('path', '/')
        query_string = request.get('query', '')

        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'SERVER_NAME': 'vercel',
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }

        headers = request.get('headers', {})
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key == 'CONTENT_TYPE':
                environ['CONTENT_TYPE'] = value
            elif key == 'CONTENT_LENGTH':
                environ['CONTENT_LENGTH'] = value
            else:
                environ['HTTP_' + key] = value

        response_data = {}

        def start_response(status, response_headers):
            response_data['status'] = status
            response_data['headers'] = dict(response_headers)

        result = wsgi_app(environ, start_response)
        body = b''.join(result)

        status_code = int(response_data.get('status', '200').split()[0])
        resp_headers = {k: v for k, v in response_data.get('headers', {}).items()}

        return {
            'statusCode': status_code,
            'headers': resp_headers,
            'body': body.decode('utf-8', errors='replace'),
        }

    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"[Vercel] ERROR:\n{error_detail}", flush=True)
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Django startup failed',
                'detail': str(e),
                'traceback': error_detail[-1000:],
            }),
        }


# Also export as app for compatibility
app = handler
