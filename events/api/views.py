from rest_framework.viewsets import ModelViewSet

from .get_data_parsing import processing_data_website
from .models import Event
from .serializers import EventSerializer


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

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


