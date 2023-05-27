from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору/тегу/подписке/наличию в списке покупок."""
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all(),)
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shop__user=self.request.user)
        return queryset
