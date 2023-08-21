from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, 'users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
