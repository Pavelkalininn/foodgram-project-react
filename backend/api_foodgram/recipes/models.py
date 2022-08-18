from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# class User(AbstractUser):
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
#     username = models.CharField(max_length=150,
#                                 verbose_name='Логин')
#     first_name = models.CharField(max_length=150,
#                                   verbose_name='Имя')
#     last_name = models.CharField(max_length=150,
#                                  verbose_name='Фамилия')
#     email = models.EmailField(unique=True,
#                               verbose_name='Почта')
#
#     class Meta:
#         ordering = ('-id',)
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'


class IngredientName(models.Model):
    name = models.CharField(max_length=79)
    measurement_unit = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Наименование ингредиента'
        verbose_name_plural = 'Наименования ингредиентов'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Ingredient(models.Model):
    ingredient_name = models.ForeignKey(
        IngredientName,
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient_name} - {self.amount}'


class Tag(models.Model):
    name = models.CharField(max_length=256)
    color = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        blank=True,
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes'
    )

    name = models.CharField(max_length=256)
    image = models.ImageField()
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_user',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_author',
        verbose_name='Подписчик'
    )

    class Meta:
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
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='unique_cart_recipe'),
        ]

    def __str__(self):
        return f'{self.author } {self.recipe}'