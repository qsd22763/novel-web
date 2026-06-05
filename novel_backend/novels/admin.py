from django.contrib import admin
from .models import AdminUser


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'real_name', 'is_active', 'created_at', 'last_login']
    list_filter = ['is_active']
    search_fields = ['username', 'real_name']
    readonly_fields = ['password', 'created_at', 'last_login']
