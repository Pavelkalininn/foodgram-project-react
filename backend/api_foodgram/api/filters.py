import django_filters

from recipes.models import Recipe

FILTER_CHOICES = (
    (1, True),
    (0, False)
)


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(
        field_name='tags',
        lookup_expr='slug'
    )
    author = django_filters.CharFilter(
        field_name='author',
        lookup_expr='id'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=FILTER_CHOICES,
        field_name='is_in_shopping_cart',
        method='is_in_shopping_cart_filter'
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=FILTER_CHOICES,
        field_name='is_favorited',
        method='is_favorited_filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def is_in_shopping_cart_filter(self, queryset, name, value):
        if int(value):
            queryset = queryset.filter(cart__author=self.request.user.id)
        return queryset

    def is_favorited_filter(self, queryset, name, value):
        if int(value):
            queryset = queryset.filter(favorite__author=self.request.user.id)
        return queryset
