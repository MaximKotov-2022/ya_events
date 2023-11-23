import os

from django.core.mail import send_mail
from django.template.loader import render_to_string
from dotenv import load_dotenv
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from .get_data_parsing import processing_data_website
from .models import Event
from .permissions import AdminOnly, ReadOnly
from .serializers import EventSerializer

load_dotenv()


def email_post_message():
    subject = 'Письмо с новыми мероприятиями'
    from_email = os.getenv('EMAIL_HOST_USER')
    message = ('Здравствуйте! Приглашаем вас на наше мероприятие'
               'Будем рады видеть вас там!')
    recipient_list = [os.getenv('EMAIL_HOST_USER'), ]
    msg_html = render_to_string('email.html',
                                {'title': subject,
                                 'message': message})

    send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, html_message=msg_html)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [ReadOnly()]
        return [AdminOnly()]

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

    def list(self, request, *args, **kwargs):
        """Получаем данные после парсинга и добавляем (или обновляем)
        данных в БД.
        """
        data_from_the_site = processing_data_website()
        for event_data in data_from_the_site:
            name = event_data['name'].text
            site = event_data['site']
            date = event_data['date']

            obj, created = Event.objects.get_or_create(name=name,
                                                       site=site,
                                                       date=date)
            if not created:
                setattr(obj, 'site', site)
                obj.save()
        self.delete_missing_events()
        return super().list(request)
