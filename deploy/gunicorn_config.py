# Gunicorn 配置文件
import multiprocessing

bind = '127.0.0.1:8000'
workers = 2                    # 2核服务器用 2 worker
worker_class = 'sync'
timeout = 120
keepalive = 5
max_requests = 5000           # 每个 worker 处理 5000 个请求后重启（防止内存泄漏）
max_requests_jitter = 500
preload_app = True            # 启动时预加载应用

# 日志
accesslog = '/var/log/novel/gunicorn_access.log'
errorlog = '/var/log/novel/gunicorn_error.log'
loglevel = 'info'

# 进程相关
pidfile = '/var/run/novel/gunicorn.pid'
tmp_upload_dir = None

# 安全
limit_request_line = 8190
limit_request_fields = 100
