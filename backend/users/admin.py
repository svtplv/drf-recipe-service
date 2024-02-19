from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2'
                ),
            },
        ),
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
    )
    list_editable = ('email', 'is_active')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по электронной почте или имени пользователя.'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    autocomplete_fields = ('user', 'author')
    search_fields = ('user__username',)
    search_help_text = 'Поиск по пользователю.'
