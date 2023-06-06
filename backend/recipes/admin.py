from django.contrib import admin

from .models import (Component, FavoriteRecipe, Ingredient, Recipe,
                     ShoppingCart, Tag)


class ComponentInline(admin.TabularInline):
    model = Component
    extra = 1
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'author', 'in_favorite')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [ComponentInline]

    def in_favorite(self, obj):
        return obj.favorite.count()


class ComponentAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('recipe', 'ingredient', 'amount')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
