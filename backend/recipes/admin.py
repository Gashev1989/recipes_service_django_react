from django.contrib import admin

from .models import Ingredient, Tag, Recipe


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'unit_of_measure',)
    search_fields = ('name',)
    list_filter = ('name', )


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'author',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tag',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe,RecipeAdmin)
