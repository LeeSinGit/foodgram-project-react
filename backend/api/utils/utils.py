from typing import Type

from rest_framework import exceptions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django.db.models import Model

from api.config.config import ALREADY_SIGNED
from api.serializers import UserSerializer
from baseapp.models import Recipe
from users.models import Subscription, User


def get_author(id: int) -> User:
    """
    Получить автора по его идентификатору.

    Args:
        id (int): Идентификатор пользователя.

    Returns:
        User: Объект пользователя.
    """
    return get_object_or_404(User, id=id)


def perform_favorite_or_cart_action(
    user: User,
    recipe: Recipe,
    model: type[Model],
    serializer_class: type[Serializer],
    error_message: str,
    request
) -> Response:
    """
    Выполнить действие "Избранное" или "Список покупок" для рецепта.

    Args:
        user (User): Пользователь, выполняющий действие.
        recipe (Recipe): Рецепт.
        model (Model): Модель "Избранное" или "Список покупок".
        serializer_class (Serializer): Класс сериализатора рецепта.
        error_message (str): Сообщение об ошибке.
        request: Запрос.

    Returns:
        Response: Ответ на действие.
    """
    if request.method == 'POST':
        existing_objects = model.objects.filter(user=user, recipe=recipe)
        if existing_objects.exists():
            raise exceptions.ValidationError(error_message)

        model.objects.create(user=user, recipe=recipe)
        serializer = serializer_class(recipe, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        deleted_count, _ = model.objects.filter(
            user=user,
            recipe=recipe
        ).delete()

        if deleted_count == 0:
            raise exceptions.ValidationError(error_message)

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def perform_subscribe_action(author: User, context) -> Response:
    """
    Выполнить действие "Подписаться" на автора.

    Args:
        author (User): Автор, на которого подписываемся.
        context (dict): Контекст запроса.

    Returns:
        Response: Ответ на действие.
    """
    subscription, created = Subscription.objects.get_or_create(
        author=author, user=context['request'].user
    )

    if created:
        user_serializer = UserSerializer(author, context=context)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    return Response(
        {'detail': ALREADY_SIGNED},
        status=status.HTTP_400_BAD_REQUEST
    )
