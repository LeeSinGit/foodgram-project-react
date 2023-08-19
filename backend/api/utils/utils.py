from api.serializers import UserSerializer
from rest_framework import exceptions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from users.models import Subscription, User


def get_author(id):
    """
    Получить автора по его идентификатору.

    Args:
        id (int): Идентификатор пользователя.

    Returns:
        User: Объект пользователя.
    """
    return get_object_or_404(User, id=id)


def perform_favorite_or_cart_action(
    user,
    recipe,
    model,
    serializer_class,
    error_message,
    request
):
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
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(error_message)

        model.objects.create(user=user, recipe=recipe)
        serializer = serializer_class(recipe, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not model.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(error_message)

        obj = get_object_or_404(model, user=user, recipe=recipe)
        obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def perform_subscribe_action(author, context):
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
    else:
        return Response(
            {'detail': 'Вы уже подписаны на этого автора.'},
            status=status.HTTP_400_BAD_REQUEST
        )
