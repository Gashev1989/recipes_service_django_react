from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                    UsersViewSet)

v1_router = DefaultRouter()
v1_router.register(
    r'recipes',
    RecipesViewSet,
    basename='recipes'
)
v1_router.register(
    r'tags',
    TagsViewSet,
    basename='tags'
)
v1_router.register(
    r'users',
    UsersViewSet,
    basename='users'
)
v1_router.register(
    r'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)


urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
