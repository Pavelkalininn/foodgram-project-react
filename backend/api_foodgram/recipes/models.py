from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Логин',
        validators=(RegexValidator(regex=r'^[\w.@+-]+\Z'), )
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class IngredientName(models.Model):
    name = models.CharField(
        max_length=79,
        verbose_name='Наименование ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Наименование ингредиента'
        verbose_name_plural = 'Наименования ингредиентов'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Ingredient(models.Model):
    ingredient_name = models.ForeignKey(
        IngredientName,
        related_name='ingredient',
        verbose_name='Наименование ингредиента',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient_name} - {self.amount}'


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Наименование тэга'
    )
    color = models.CharField(
        max_length=10,
        verbose_name='Цвет тэга'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг тэга'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор',
        blank=True,
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    name = models.CharField(
        max_length=256,
        verbose_name='Наименование'
    )
    image = models.ImageField(
        verbose_name='Фото'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe'),
        ]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_from_author',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_from_user',
        verbose_name='Подписчик'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'),
        ]

    def __str__(self):
        return f'{self.author } {self.user}'


class Favorite(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_favorite'),
        ]

    def __str__(self):
        return f'{self.author } {self.recipe}'


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт в корзине'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_cart_recipe'),
        ]

    def __str__(self):
        return f'{self.author } {self.recipe}'
