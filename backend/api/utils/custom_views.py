from typing import Optional


class MultiSerializerViewSetMixin:
    """
    Mixin for selecting an appropriate
    serializer from `serializer_classes`.
    """

    serializer_classes: str | None = None

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()
