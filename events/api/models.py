from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Event(models.Model):
    date = models.DateField(
        verbose_name='Дата',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,)
    site = models.URLField(
        verbose_name='Сайт',
        max_length=254,)

    def __str__(self):
        return self.name
