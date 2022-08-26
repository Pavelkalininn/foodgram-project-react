import django_filters

from recipes.models import Recipe, Tag

FILTER_CHOICES = (
    (1, True),
    (0, False)
)
FLAG_ON = '1'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
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
        if value == FLAG_ON:
            queryset = queryset.filter(cart__author=self.request.user.id)
        return queryset

    def is_favorited_filter(self, queryset, name, value):
        if value == FLAG_ON:
            queryset = queryset.filter(favorite__author=self.request.user.id)
        return queryset
