from django.contrib import admin

from .models import User, Recipe, Ingredient, Tag, IngredientName

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientName)
admin.site.register(Tag)
