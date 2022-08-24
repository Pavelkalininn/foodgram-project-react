from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.filters import RecipeFilter
from api.paginations import LargeResultsSetPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (
    UserSerializer, TagSerializer, RecipeSerializer, IngredientSerializer,
    SubscriptionSerializer, UserCreateSerializer, IngredientNameSerializer
)
from api.utils import shopping_cart_data_creator, cart_favorite_add_or_delete
from recipes.models import (
    User,
    Tag,
    Recipe,
    Ingredient,
    IngredientName,
    ShoppingCart, Favorite, Subscription
)


class UserViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('recipes__limit',)

    def get_queryset(self):
        if self.action not in ('subscriptions', 'subscribe'):
            return User.objects.all()
        user = get_object_or_404(
            User,
            id=self.request.user.pk
        )
        subscriptions = [
            sub.user for sub in user.subscription_from_author.all()
        ]
        return subscriptions

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in (
                'me',
                'subscriptions',
                'subscribe'
        ) or self.kwargs.get('pk'):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, pk):
        if not pk.isnumeric() or int(pk) <= 0:
            raise ValidationError(
                'Id пользователя должен быть положительной цифрой.'
            )
        if not User.objects.filter(id=pk).exists():
            raise ValidationError(
                {'errors': f'Не обнаружено пользователя с таким id'}
            )
        user = get_object_or_404(User, id=pk)
        author = request.user
        subscription_exists = Subscription.objects.filter(
            author=author,
            user=user
        ).exists()
        if self.request.method == "POST":
            if subscription_exists:
                raise ValidationError(
                    'Этот пользователь уже добавлен'
                )
            Subscription.objects.create(
                author=author,
                user=user
            )
            serializer = SubscriptionSerializer(
                self.get_queryset(),
                context={"request": request},
                many=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not subscription_exists:
            raise ValidationError(
                {'errors': f'Вы не подписаны на этого автора'}
            )
        subscription = get_object_or_404(
            Subscription,
            user=user,
            author=author
        )
        subscription.delete()
        return Response(
            {'detail': 'Подписка успешно отменена'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        context = {"request": request}
        recipe_limit = self.request.query_params.get('recipes_limit')
        if recipe_limit:
            if (not recipe_limit.isnumeric()
                    or int(recipe_limit) < 0):
                raise ValidationError(
                    {
                        'errors':
                        'Параметр recipe_limit должен быть числом больше нуля'
                     }
                )
            context['recipes_limit'] = int(self.request.query_params.get(
                'recipes_limit')
            )
        serializer = self.get_serializer(
            self.get_queryset(),
            context=context,
            many=True
        )
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(user, context={"request": request})
        return Response(serializer.data)


class TagViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ('tags', 'author')
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        tag_ids = self.request.data.get('tags')
        ingredients = []
        for ingredient in self.request.data.get('ingredients'):
            ingredient_name = get_object_or_404(
                IngredientName,
                id=ingredient.get('id')
            )
            ingredient, _ = Ingredient.objects.get_or_create(
                ingredient_name=ingredient_name,
                amount=ingredient.get('amount'),
            )
            ingredients.append(ingredient)
        tags = Tag.objects.filter(id__in=tag_ids)
        serializer.save(
            author=self.request.user,
            tags=tags,
            ingredients=ingredients
        )

    @action(
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        detail=False
    )
    def get_shopping_cart(self, request):
        return HttpResponse(
            shopping_cart_data_creator(request.user),
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': 'attachment; filename="shopping_list.txt"',
            }
        )

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def shopping_cart(self, request, pk):
        return cart_favorite_add_or_delete(
            pk,
            request,
            ShoppingCart
        )

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def favorite(self, request, pk):
        return cart_favorite_add_or_delete(
            pk,
            request,
            Favorite
        )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = IngredientName.objects.all()
    serializer_class = IngredientNameSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
