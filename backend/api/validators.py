from django.core.validators import RegexValidator


validate_username = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='Напишите валидный ник.'
)
