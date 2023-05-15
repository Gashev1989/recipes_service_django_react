from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'measurement_unit',)
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


class RecipeIngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('recipe', 'ingredient', 'amount', 'measurment_unit',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
