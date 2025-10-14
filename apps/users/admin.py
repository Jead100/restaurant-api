from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Demo", {"fields": ("is_demo", "demo_expires_at")}),
    )
    list_display = ("username", "email", "is_staff", "is_demo", "demo_expires_at")
