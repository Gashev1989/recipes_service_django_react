from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingRecipe, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )


class TagAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('name', 'author', 'in_favorite')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    inlines = [RecipeIngredientInline]

    def in_favorite(self, obj):
        return obj.favorite_recipe.count()


class RecipeIngredientAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingRecipe)
