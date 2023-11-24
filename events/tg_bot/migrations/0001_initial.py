# Generated by Django 2.2.19 on 2023-11-23 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(unique=True, verbose_name='ID пользователя ТГ')),
                ('name', models.TextField(verbose_name='Имя пользователя')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription', models.BooleanField(default=False, verbose_name='Подписка')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Время подписки')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tg_bot.Profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
    ]
