from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from api.config.config import (
    ALREADY_IN_FAVORITES,
    PROHIBITION_OF_SELF_SIGNING,
    SUCCESSFUL_UNSUBSCRIPTION,
)
from api.filter import RecipeFilter
from api.mixins import (
    MultiSerializerViewSetMixin,
    TagAndIngridientMixin,
    ViewMixin,
)
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
from baseapp.models import Favorite, Ingredient, Recipe, RecipeIngredients, Tag
from users.models import Subscription


User = get_user_model()


class UserViewSet(DjoserUserViewSet, ViewMixin):
    """Представление для операций с пользователями."""

    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissions,)
    add_serializer = SubscriptionSerializer
    link_model = Subscription
    pagination_class = CustomPagination

    def get_queryset(self):
        """Аннотация для подсчета количества рецептов."""
        queryset = super().get_queryset()
        queryset = queryset.annotate(recipes_count=Count('recipes'))
        return queryset

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Подписаться на пользователя."""
        context = self.get_serializer_context()

        author = get_author(id)

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
        author = get_author(id)

        deleted_count, _ = self.link_model.objects.filter(
            author=author, user=context['request'].user
        ).delete()

        if deleted_count > 0:
            return Response(
                {'detail': SUCCESSFUL_UNSUBSCRIPTION},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': f'{self.link_model.__name__} не существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class RecipeViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    """
    Представление для операций с рецептами.
    """

    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    serializer_classes = {
        'list': RecipeSerializer,
        'retrieve': RecipeSerializer,
        'create': RecipeCreateUpdateSerializer,
        'partial_update': RecipeCreateUpdateSerializer,
    }

    def get_queryset(self):
        queryset = Recipe.objects.all()
        queryset = queryset.select_related('author')
        queryset = queryset.prefetch_related(
            Prefetch('tags', queryset=Tag.objects.all()),
            Prefetch(
                'recipeingredients_set',
                queryset=RecipeIngredients.objects.select_related(
                    'ingredient'
                ),
            ),
        )
        return queryset

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
            request,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        buy_list_text = self.get_shopping_list_text()

        response = HttpResponse(buy_list_text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response

    def get_shopping_list_text(self):
        """
        Создает текстовый список покупок на
        основе рецептов из списка покупок пользователя.
        """
        shopping_cart_recipes = Recipe.objects.filter(
            in_shopping_list__user=self.request.user
        ).prefetch_related(
            Prefetch(
                'recipeingredients_set',
                queryset=RecipeIngredients.objects.select_related(
                    'ingredient'
                ),
            )
        ).distinct()

        buy_list_text = 'Список покупок:\n\n'

        for recipe in shopping_cart_recipes:
            recipe_ingredients = recipe.recipeingredients_set.all()
            for ingredient in recipe_ingredients:
                ingredient_name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                total_amount = ingredient.amount
                buy_list_text += (
                    f'{ingredient_name}, {total_amount} {measurement_unit}\n'
                )

        return buy_list_text
