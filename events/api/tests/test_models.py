from django.test import TestCase
from api.models import Event


class EventModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = Event.objects.create(
            date='2001-12-31',
            name='Название мероприятия',
            site='https://ya.ru/'
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        event = EventModelTest.event
        field_verboses = {
            'date': 'Дата',
            'name': 'Название',
            'site': 'Сайт',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    event._meta.get_field(field).verbose_name, expected_value)
