from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from django.db.models import Model, Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from api.config.config import COMPLETED_EARLIER
from api.permissions import IsAdminOrReadOnly


class ViewMixin:
    """Добавляет дополнительные методы."""

    add_serializer: ModelSerializer = None
    link_model: Model = None

    def _create_relation(self, obj_id) -> Response:
        """Добавляет связь многие ко многим между объектами."""
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            self.link_model(None, obj.pk, self.request.user.pk).save()
        except IntegrityError:
            return Response(
                {'error': COMPLETED_EARLIER},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer: ModelSerializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def _delete_relation(self, q: Q) -> Response:
        """Удаляет связь многие ко многим между объектами."""
        deleted_count, _ = (
            self.link_model.objects.filter(
                q & Q(user=self.request.user)
            ).delete()
        )
        if deleted_count == 0:
            return Response(
                {'error': f'{self.link_model.__name__} не существует'},
                status=HTTP_400_BAD_REQUEST,
            )
        return Response(status=HTTP_204_NO_CONTENT)


class TagAndIngridientMixin:
    """Миксина для списка тегов и ингридиентов."""

    permission_classes = (IsAdminOrReadOnly,)


class MultiSerializerViewSetMixin:
    """
    Mixin for selecting an appropriate
    serializer from `serializer_classes`.
    """

    serializer_classes: str

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()
