from django.db import models


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя ТГ',
        unique=True
    )
    name = models.TextField(
        verbose_name='Имя пользователя',
    )

    def __str__(self):
        return f'{ self.external_id } { self.name }'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Subscription(models.Model):
    profile = models.ForeignKey(
        to='tg_bot.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    subscription = models.BooleanField(
        verbose_name='Подписка',
        default=False,
    )
    created_at = models.DateTimeField(
        verbose_name='Время подписки',
        auto_now=True,
    )

    def __str__(self):
        return f'Подписка { self.pk } от { self.profile }'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
