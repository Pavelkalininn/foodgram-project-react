from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.filters import RecipeFilter
from api.paginations import LargeResultsSetPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (IngredientNameSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, ShoppingCartSerializer,
                             SubscriptionCreateSerializer,
                             SubscriptionRecipeSerializer,
                             SubscriptionSerializer,
                             SubscriptionsGetSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer)
from api.utils import shopping_cart_data_creator
from api_foodgram.settings import DELETE_SUCCESS
from recipes.models import (Favorite, IngredientName, Recipe, ShoppingCart,
                            Subscription, Tag, User)


class UserViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pagination_class = LargeResultsSetPagination

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
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        if self.action == 'subscribe':
            return SubscriptionsGetSerializer
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.kwargs.get('pk'):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        serializer = SubscriptionCreateSerializer(
            data={'user': pk, 'author': request.user.pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == "POST":
            Subscription.objects.create(**serializer.validated_data)
            serializer = self.get_serializer_class()(
                self.get_queryset(),
                context={"request": request},
                many=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = get_object_or_404(
            Subscription,
            **serializer.validated_data
        )
        subscription.delete()
        return Response(
            {'detail': DELETE_SUCCESS.format(name='Подписка')},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        context = {"request": request}
        recipes_limit = self.request.query_params.get('recipes_limit')
        serializer = SubscriptionsGetSerializer(
            data={
                'author': request.user.pk,
                'recipes_limit': recipes_limit
            }
        )
        serializer.is_valid(raise_exception=True)
        recipes_limit = serializer.validated_data.get('recipes_limit')
        if recipes_limit:
            context['recipes_limit'] = recipes_limit
        input_serializer = self.get_serializer(
            self.get_queryset(),
            context=context,
            many=True
        )
        return Response(input_serializer.data)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
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
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ('tags', 'author')
    permission_classes = (AuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def cart_favorite_add_or_delete(
            self,
            recipe_id,
            request,
            model_class
    ):
        serializer = ShoppingCartSerializer(
            data={'recipe': recipe_id, 'author': request.user.pk},
            context={
                'request': request,
                'model_class': model_class
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            model_class.objects.create(**serializer.validated_data)
            recipe = get_object_or_404(
                Recipe,
                id=serializer.validated_data.get('recipe').id
            )
            serializer = SubscriptionRecipeSerializer(
                recipe,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        current_object = get_object_or_404(
            model_class,
            **serializer.validated_data
        )
        current_object.delete()
        return Response(
            data={'detail': DELETE_SUCCESS.format(name='Рецепт')},
            status=status.HTTP_204_NO_CONTENT
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
                'Content-Disposition':
                    'attachment; filename="shopping_list.txt"',
            }
        )

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def shopping_cart(self, request, pk):
        return self.cart_favorite_add_or_delete(
            pk,
            request,
            ShoppingCart
        )

    @action(
        methods=('POST', 'DELETE'),
        permission_classes=(IsAuthenticated,),
        filterset_class=RecipeFilter,
        detail=True
    )
    def favorite(self, request, pk):
        return self.cart_favorite_add_or_delete(
            pk,
            request,
            Favorite
        )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = IngredientName.objects.all()
    serializer_class = IngredientNameSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
