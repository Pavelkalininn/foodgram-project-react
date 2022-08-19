from api import views
from api.views import (UserViewSet, RecipeViewSet,
                       FavoriteViewSet, SubscriptionViewSet, IngredientViewSet,
                       TagViewSet, IngredientNameViewSet)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='user-list')
router.register('tags', TagViewSet, basename='tag-list')
router.register('recipes', RecipeViewSet, basename='recipe-list')

router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite_changing'
)
router.register(
    'subscriptions',
    SubscriptionViewSet,
    basename='subscription-list'
)
router.register('ingredients', IngredientViewSet, basename='ingredient-list')
router.register(
    'ingredient_names', IngredientNameViewSet, basename='ingredient_name-list')
urlpatterns = [
    path('v1/', include(router.urls)),
    path('recipes/download_shopping_cart',
         views.get_shopping_cart,
         name='shopping-cart')
]
