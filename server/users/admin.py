"""
Admin configuration for the users app.

This module defines the admin interface for the custom User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    """
    Admin interface for the custom User model.
    
    Configures the admin panel display, filtering, and editing options for users.
    """
    model = User
    list_display = ('id', 'username', 'email', 'phone_number', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone_number', 'profile', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'profile', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'phone_number',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)