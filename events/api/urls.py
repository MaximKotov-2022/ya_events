from django.urls import include, path
from rest_framework import routers

from .views import EventViewSet

router = routers.DefaultRouter()
router.register('events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
