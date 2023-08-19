from api.config.config import (
    ALREADY_IN_FAVORITES,
    ALREADY_ON_THE_SHOPPING_LIST,
    PROHIBITION_OF_SELF_SIGNING,
    SUCCESSFUL_UNSUBSCRIPTION,
)
from api.filter import RecipeFilter
from api.mixins import TagAndIngridientMixin, ViewMixin
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer,
    MiniRecipeSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
)
from api.utils.utils import (
    get_author,
    perform_favorite_or_cart_action,
    perform_subscribe_action,
)
from baseapp.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Subscription


User = get_user_model()


class UserViewSet(DjoserUserViewSet, ViewMixin):
    """Представление для операций с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissions,)
    add_serializer = SubscriptionSerializer
    link_model = Subscription
    pagination_class = CustomPagination

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Подписаться на пользователя."""

        context = self.get_serializer_context()

        try:
            author = get_author(id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if author == context['request'].user:
            return Response(
                {'detail': PROHIBITION_OF_SELF_SIGNING},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = self.link_model.objects.get_or_create(
            author=author, user=context['request'].user
        )

        return perform_subscribe_action(author, context)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Отписаться от пользователя."""

        context = self.get_serializer_context()

        try:
            author = get_author(id)
            subscription = self.link_model.objects.get(
                author=author, user=context['request'].user
            )
            subscription.delete()
            return Response(
                {'detail': SUCCESSFUL_UNSUBSCRIPTION},
                status=status.HTTP_204_NO_CONTENT
            )
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Получить список подписок пользователя."""

        page = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet, TagAndIngridientMixin):
    """Представление для операций с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


class IngredientsViewSet(ModelViewSet, TagAndIngridientMixin):
    """Представление для операций с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    lookup_field = 'id'


class RecipeViewSet(ModelViewSet):
    """Представление для операций с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """
        Возвращает соответствующий класс
        сериализатора в зависимости от действия.
        """

        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        """Добавить или удалить рецепт из избранного."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        error_message = ALREADY_IN_FAVORITES
        return perform_favorite_or_cart_action(
            user,
            recipe,
            Favorite,
            MiniRecipeSerializer,
            error_message,
            request
        )

    @action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None):
        """Добавить или удалить рецепт из списка покупок."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        error_message = ALREADY_ON_THE_SHOPPING_LIST
        return perform_favorite_or_cart_action(
            user,
            recipe,
            ShoppingCart,
            MiniRecipeSerializer,
            error_message,
            request
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipeIngredients.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )

        buy_list_text = 'Список покупок:\n\n'
        for item in buy_list:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            buy_list_text += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )

        response = HttpResponse(buy_list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response
