from rest_framework import permissions
from rest_framework.request import Request


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Правило доступа, позволяющее изменять объекты только автору,
    администратору или разрешенным методам (SAFE_METHODS).
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Проверка доступа к объекту.

        Args:
            request (Request): Запрос.
            view: Представление.
            obj: Объект, к которому осуществляется доступ.

        Returns:
            bool: Результат проверки доступа.
        """
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Правило доступа, позволяющее выполнять разрешенные методы
    (SAFE_METHODS) администраторам.
    """

    def has_permission(self, request: Request, view) -> bool:
        """
        Проверка доступа.

        Args:
            request (Request): Запрос.
            view: Представление.

        Returns:
            bool: Результат проверки доступа.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )
