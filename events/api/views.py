from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from .get_data_parsing import processing_data_website
from .models import Event
from .permissions import AdminOnly, ReadOnly
from .serializers import EventSerializer


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [ReadOnly()]
        return [AdminOnly()]

    # Получаем данные после парсинга и добавляем (или обновляем) данных в БД.
    data = processing_data_website()
    for event_data in data:
        name = event_data['name'].text
        site = event_data['site']
        date = event_data['date']
        obj, created = Event.objects.get_or_create(name=name,
                                                   site=site,
                                                   date=date)
        if not created:
            setattr(obj, 'site', site)
            obj.save()

    def delete_missing_events(self):
        """Получаем названия мероприятий, которых больше нет на сайте с
        мероприятиями, но есть в БД.
        """
        events_db = self.queryset
        events_website = processing_data_website()

        events_db_name = set(event.name for event in events_db)
        events_website_name = set(
            event_data['name'].text for event_data in events_website
        )
        missing_events_names = events_db_name - events_website_name

        Event.objects.filter(name__in=missing_events_names).delete()

        return 0

    def list(self, request):
        self.delete_missing_events()
        return super().list(request)

    def create(self, request):
        self.delete_missing_events()
        return super().create(request)

    def update(self, request, pk=None):
        self.delete_missing_events()
        return super().update(request, pk)

    def partial_update(self, request, pk=None):
        self.delete_missing_events()
        return super().partial_update(request, pk)

    def destroy(self, request, pk=None):
        self.delete_missing_events()
        return super().destroy(request, pk)
