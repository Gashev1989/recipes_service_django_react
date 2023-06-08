# from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

# from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
#                            ShoppingCart, Tag)
from recipes.models import (Component, FavoriteRecipe, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe, User

from .filters import RecipeFilter
from .paginators import PagePagination
from .permissions import IsAdminIsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminIsAuthorOrReadOnly,)
    pagination_class = PagePagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    def _handler_post_request(
            self, request=None, serializer=None,
            user=None, recipe=None):
        """Обработчик POST-запросов."""
        serializer = serializer(data={
            'user': user.id,
            'recipe': recipe.id,
        }, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handler_delete_request(
            self, recipe=None, user=None, model=None,
            error_message=None):
        """Обработчик DELETE-запросов."""
        obj = model.objects.filter(user=user, recipe=recipe)
        if not obj.exists():
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(
            {'message': 'Рецепт успешно удален.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        """Добавить/удалить из избранного."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        model = FavoriteRecipe

        if request.method == 'POST':
            return self._handler_post_request(
                request=request,
                serializer=FavoriteRecipeSerializer,
                user=user,
                recipe=recipe,
            )

        if request.method == 'DELETE':
            return self._handler_delete_request(
                recipe=recipe,
                user=user,
                model=model,
                error_message='Рецепт не добавлялся в избранное.'
            )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        """Добавить/удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user
        model = ShoppingCart

        if request.method == 'POST':
            return self._handler_post_request(
                request=request,
                serializer=ShoppingCartSerializer,
                user=user,
                recipe=recipe,
            )

        if request.method == 'DELETE':
            return self._handler_delete_request(
                recipe=recipe,
                user=user,
                model=model,
                error_message='Рецепт не добавлялся в корзину покупок.'
            )

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated],
            pagination_class=None)
    def download_shopping_cart(self, request):
        """"Загрузить список покупок."""
#        user = request.user
#        recipes = Recipe.objects.filter(shop_cart__user=user)
#        ingredients = Ingredient.objects.filter(
#            recipe__in=recipes).annotate(
#                total_amount=Sum('amount')
#        )
#        shopping_card = ('===Foodgram===\n')
#        for ing in ingredients:
#            shopping_card += (
#                f'{ing.name}: {ing.total_amount} {ing.measurement_unit}\n'
#            )

#        user = request.user
#        components = Component.objects.filter(recipe__shop_cart__user=user)
#        ingredients = components.values(
#            'ingredient__name', 'ingredient__measurement_unit'
#        ).annotate(total_amount=Sum('amount'))
#        shopping_card = ('===Foodgram===\n')
#        for ingredient in ingredients:
#            shopping_card.append(
#                f"{ingredient['ingredient__name']} "
#                + f"{ingredient['total_amount']}"
#                + f"({ingredient['ingredient__measurement_unit']}) "
#                + '\n'
#            )
#        for ing in ingredients:
#            shopping_card += (
#                f'{ing.name}: {ing.total_amount} {ing.measurement_unit}\n'
#            )
#        ingredients = (
#            Component.objects
#            .filter(recipe__shop_cart__user=request.user)
#            .values('ingredient')
#            .annotate(total_amount=Sum('amount'))
#            .values_list('ingredient__name', 'total_amount',
#                         'ingredient__measurement_unit')
#        )
#        shop_list = []
#        [shop_list.append(
#            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
#        file_name = 'shopping_list.txt'
#        response = HttpResponse(
#            '===Foodgram===\n' + '\n'.join(shop_list),
#            content_type='text/plain'
#        )

        shopping_list = {}
        ingredients = Component.objects.filter(
            recipe__shop_cart__user=request.user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        shop_list = ([f"* {item}:{value['amount']}"
                      f"{value['measurement_unit']}\n"
                      for item, value in shopping_list.items()])
        shop_list.append('\n ===Made by FoodGram===')
        file_name = 'shopping_list.txt'
        response = HttpResponse(shop_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


class UsersViewSet(UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    add_serializer = SubscribeSerializer

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=PagePagination)
    def subscriptions(self, request):
        """Показать подписки пользователя."""
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписаться/отписаться от автора."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(user=user, author=author)

        if request.method == 'POST':
            serializer = SubscriptionSerializer(data={
                'user': request.user.id,
                'author': author.id
            }, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не подписывались на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
