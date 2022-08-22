from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    Tag,
    IngredientName,
    Subscription,
    User,
    Favorite,
    ShoppingCart
)

admin.site.register(Tag)
admin.site.register(IngredientName)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(User)
