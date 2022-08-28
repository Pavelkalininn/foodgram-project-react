from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Favorite,
    Ingredient,
    IngredientName,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
    User
)

EMPTY_VALUE = 'значение не задано'


class CustomUserAdmin(UserAdmin):
    search_fields = ('username', 'email', 'first_name')
    list_filter = ('username', 'email', 'first_name')
    empty_value_display = EMPTY_VALUE


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author', 'tags', 'text')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = EMPTY_VALUE
    list_display = (
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'add_to_favorites_count'
    )

    def add_to_favorites_count(self, obj):
        return obj.favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('ingredient_name', )
    list_filter = ('ingredient_name', )
    empty_value_display = EMPTY_VALUE


admin.site.register(Tag)
admin.site.register(IngredientName)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(User, CustomUserAdmin)
