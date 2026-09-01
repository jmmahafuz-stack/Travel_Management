from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import PackageViewSet

router = SimpleRouter()
router.register('', PackageViewSet, basename='package')

urlpatterns = [
	path('', include(router.urls)),
]
