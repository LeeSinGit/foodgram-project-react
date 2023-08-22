from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'date_joined',
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('date_joined', 'email', 'first_name')

    def get_queryset(self, request):
        """
        Используем select_related для заджойнивания групп
        и зафетчивания разрешений.
        """
        queryset = super().get_queryset(
            request
        ).select_related(
            'groups'
        ).prefetch_related(
            'user_permissions'
        )
        return queryset


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user', 'date_added')
    search_fields = ('id', 'author', 'user', 'date_added')
    list_filter = ('id', 'author', 'user')

    def get_queryset(self, request):
        """
        Используем select_related для заджойнивания авторов
        и зафетчивания всех связанных пользователей.
        """
        queryset = super().get_queryset(
            request
        ).select_related(
            'author'
        ).prefetch_related(
            'user'
        )
        return queryset
