from api.validators import validate_username
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE, DateTimeField, F, ForeignKey, Model, Q


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=150,
        blank=False,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=False,
        max_length=150
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        verbose_name='Groups',
        related_name='custom_user_set',
        help_text='Группы, к которым принадлежит этот пользователь',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        verbose_name='Разрешения пользователя',
        related_name='custom_user_set',
        help_text='Конкретные разрешения для этого пользователя.',
        related_query_name='user'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username')

    def __str__(self):
        return self.email


class Subscription(Model):
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscribers',
        to=User,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Подписчик',
        related_name='subscribed_to',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='Повторяющаяся подписка'
            ),
            models.CheckConstraint(
                check=~Q(author=F('user')),
                name='Запрет самоподписки'
            ),
        ]

    def __repr__(self) -> str:
        return f'{self.user} - {self.author}'
