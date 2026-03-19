from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'username', 'get_full_name', 'is_verified', 'total_analyses', 'created_at']
    list_filter   = ['is_verified', 'is_staff', 'state']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering      = ['-created_at']
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Kishan Sathi', {'fields': ('phone', 'state', 'is_verified')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'experience', 'farm_size', 'district']
    search_fields = ['user__email', 'district']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display  = ['user', 'action', 'ip_address', 'timestamp']
    list_filter   = ['action']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'timestamp']
