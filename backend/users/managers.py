from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User.

    Этот менеджер предоставляет методы для
    создания обычных пользователей и суперпользователей.
    """

    def create_user(
            self,
            email,
            username,
            first_name,
            last_name,
            password=None,
            **extra_fields
    ):
        """
        Создает и сохраняет обычного пользователя с указанными данными.

        Args:
            email (str): Электронная почта пользователя.
            username (str): Ник пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            password (str, optional): Пароль пользователя. Defaults to None.
            **extra_fields: Дополнительные поля пользователя.

        Returns:
            User: Созданный пользователь.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email,
            username,
            password=None,
            **extra_fields
    ):
        """
        Создает и сохраняет суперпользователя с указанными данными.

        Args:
            email (str): Электронная почта пользователя.
            username (str): Ник пользователя.
            first_name (str): Имя пользователя.
            last_name (str): Фамилия пользователя.
            password (str, optional): Пароль пользователя. Defaults to None.
            **extra_fields: Дополнительные поля пользователя.

        Returns:
            User: Созданный суперпользователь.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            email,
            password,
            **extra_fields
        )
