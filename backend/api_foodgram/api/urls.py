from api.views import (DjoserUserViewSet, IngredientViewSet, RecipeViewSet,
                       TagViewSet)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register('users', DjoserUserViewSet, basename='user-list')
router.register('tags', TagViewSet, basename='tag-list')
router.register('recipes', RecipeViewSet, basename='recipe-list')
router.register('ingredients', IngredientViewSet, basename='ingredient-list')

urlpatterns = [

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
