from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingRecipe, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow, User

from .filters import RecipeFilter
from .paginators import PagePagination
from .permissions import IsAdminIsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, SubscribeSerializer, TagSerializer,
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        """Добавить/удалить из избранного."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if not FavoriteRecipe.objects.filter(user=request.user,
                                                 recipe=recipe).exists():
                FavoriteRecipe.objects.create(
                    user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже есть в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(FavoriteRecipe, user=request.user,
                              recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        """Добавить/удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=request.data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingRecipe.objects.filter(user=request.user,
                                                 recipe=recipe).exists():
                ShoppingRecipe.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже есть в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingRecipe, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def download_shopping_cart(self, request):
        """Загрузить список покупок."""
        user = request.user
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shop_recipe__user=user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        now = datetime.now().strftime('%d/%m/%Y')
        filename = f'{now}_{user.username}_shopping_card.txt'
        shopping_card = ('===Foodgram===\n')
        for ing in ingredients:
            shopping_card += (
                f'{ing.name} ({ing.measurement_unit}) - {ing.total_amount}\n'
            )
        response = HttpResponse(
            shopping_card,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class UsersViewSet(UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    add_serializer = SubscribeSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=PagePagination)
    def subscriptions(self, request):
        """Показать подписки пользователя."""
        user = self.request.user
        authors = User.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Подписаться/отписаться от автора."""
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не подписывались на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
