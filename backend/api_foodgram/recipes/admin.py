from django.contrib import admin

from .models import Recipe, Ingredient, Tag, IngredientName, Subscription, User

admin.site.register(Subscription)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientName)
admin.site.register(Tag)
admin.site.register(User)

