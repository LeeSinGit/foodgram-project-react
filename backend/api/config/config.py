# backend/api/views.py
PROHIBITION_OF_SELF_SIGNING = 'Вы не можете подписаться на себя!'
SUCCESSFUL_UNSUBSCRIPTION = 'Вы успешно отписались!'
ALREADY_IN_FAVORITES = 'Рецепт уже в избранном!'
ALREADY_ON_THE_SHOPPING_LIST = 'Рецепт уже в списке покупок!'


# backend/api/serializers.py
ONE_OR_MORE_INGREDIENTS = 'Введите 1 или более ингридиетов.'
COOKING_TIME = 'Время приготовления не может быть меньше одной минуты.'


# backend/api/mixins.py
COMPLETED_EARLIER = 'Действие выполнено ранее.'


# backend/api/mixins.py
AT_LEAST_ONE_TAG = 'Нужно добавить хотя бы один тег.'
IDENTICAL_ONES_ARE_NOT_ALLOWED = 'Два идентичных ингредиента недопустимы.'
ALREADY_SIGNED = 'Вы уже подписаны на этого автора.'
