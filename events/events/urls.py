from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view
from django.urls import path


schema_view = get_schema_view(title="Example API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/events/', include('api.urls')),
    path('schema/', schema_view),
]
