"""
EdgeOne Pages - Django WSGI 后端入口
路径: cloud-functions/api/index.py  ->  映射到 /api 路由
"""
import os
import sys

# 将项目根目录加入 Python 路径，以便导入 novel_backend
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BACKEND_DIR = os.path.join(_BASE_DIR, 'novel_backend')
sys.path.insert(0, _BACKEND_DIR)

# Django 环境变量（必须在 import django 之前设置）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings_vercel')
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

# 导入 Django 并初始化
import django
django.setup()

# 导出 WSGI 应用（EdgeOne 自动检测框架模式）
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
