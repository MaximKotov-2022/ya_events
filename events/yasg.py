from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="YA_Events API",
      default_version='v1',
      description="Документация для приложения api проекта YA_Events",
      # terms_of_service="URL страницы с пользовательским соглашением",
      contact=openapi.Contact(email="admin@ya_events.ru"),
      license=openapi.License(name="BSD License"),
   ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
    url(r'swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-swagger-yaml'),

]