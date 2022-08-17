from django.contrib.auth.models import AbstractUser
from django.db import models


class IngredientName(models.Model):
    name = models.CharField(max_length=79)
    measurement_unit = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    ingredient_name = models.ForeignKey(
        IngredientName,
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.ingredient_name.name


class Tag(models.Model):
    name = models.CharField(max_length=256)
    color = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    ### ТУТ НУЖНО ВЫВЕСТИ АВТОРА РЕЦЕПТА
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes'
    )
    #  ВЫВЕСТИ
    # is_favorited = models.BooleanField(default=False)
    # is_in_shopping_cart = models.BooleanField(default=False)
    name = models.CharField(max_length=256)
    image = models.ImageField()
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    subscriptions = models.ManyToManyField(
        'self',
        related_name='follower',
        symmetrical=False,
        blank=True
    )
    recipes = models.ForeignKey(
        Recipe,
        related_name='author',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    favorited = models.ManyToManyField(
        Recipe,
        related_name='favored_user',
        blank=True
    )
    shopping_cart = models.ManyToManyField(
        Recipe,
        related_name='cart_user',
        blank=True
    )
