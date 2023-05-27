from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UsersViewSet

v1_router = DefaultRouter()
v1_router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
v1_router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    r'users',
    UsersViewSet,
    basename='users'
)
v1_router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)


urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
