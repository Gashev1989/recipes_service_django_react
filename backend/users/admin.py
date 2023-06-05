from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = (
        'username',
        'email',
        'password',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email',)
    list_editable = ('password',)


class SubscribeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('user', 'author',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
