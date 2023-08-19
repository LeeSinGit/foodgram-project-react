from django.apps import AppConfig


class BaseappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'baseapp'
    verbose_name = 'Главное приложение'
