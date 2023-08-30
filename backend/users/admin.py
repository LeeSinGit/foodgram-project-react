from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'date_joined',
    )
    list_display_links = ['username', 'email']
    search_fields = ('email', 'username')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user', 'date_added')
    list_display_links = ['author']
    search_fields = (
        'author__email',
        'user__email',
        'author__username',
        'user__username'
    )

    def get_queryset(self, request):
        """
        Используем select_related для заджойнивания авторов
        и зафетчивания всех связанных пользователей.
        """
        queryset = super().get_queryset(
            request
        ).select_related(
            'author',
            'user'
        )
        return queryset
