from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title="Example API")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('schema/', schema_view),
]
