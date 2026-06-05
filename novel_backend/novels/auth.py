"""
墨香书阁 — 自定义认证模块
支持 AdminUser 模型的 Session 认证 + 管理员权限校验
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login as django_login
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import AdminUser


# ══════════════════════════════════════════════
# 1. AdminUser 认证后端（兼容 Django Auth 体系）
# ══════════════════════════════════════════════

class AdminUserBackend(BaseBackend):
    """
    AdminUser 专用认证后端。
    让 AdminUser 实例能通过 Django 的 authenticate() / login() / SessionAuthentication
    完整流程，使 request.user 在后续请求中正确还原为 AdminUser（而非 AnonymousUser）。
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """用账号密码校验 AdminUser"""
        if not username or not password:
            return None
        try:
            admin = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist:
            return None
        if not admin.check_password(password):
            return None
        if not admin.is_active:
            return None
        return admin

    def get_user(self, user_id):
        """Session 还原时根据 user_id 获取 AdminUser"""
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None


# ══════════════════════════════════════════════
# 2. 管理员权限类（替代 DRF 内置 IsAdminUser）
# ══════════════════════════════════════════════

class IsAdminUserOrStaff(BasePermission):
    """
    同时兼容两种管理员身份：
      - Django User 且 is_staff=True（原有逻辑）
      - AdminUser 实例（新增逻辑）
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Django User.is_staff
        if getattr(user, 'is_staff', False):
            return True
        # AdminUser 实例（已通过认证即有权限）
        if isinstance(user, AdminUser):
            return True
        return False


# ══════════════════════════════════════════════
# 3. 兼容 AdminUser 的 Session 认证
# ══════════════════════════════════════════════

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """豁免 CSRF 校验的 Session 认证（保留原有功能）"""

    def enforce_csrf(self, request):
        return


def admin_login(request, admin: AdminUser) -> None:
    """
    管理员登录：将 AdminUser 写入 Django Session。
    必须指定 backend，否则 SessionAuthentication 无法还原用户。
    """
    admin.backend = '%s.%s' % (AdminUserBackend.__module__, AdminUserBackend.__qualname__)
    django_login(request, admin)
