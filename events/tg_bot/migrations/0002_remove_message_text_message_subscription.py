# Generated by Django 4.2.6 on 2023-10-22 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tg_bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='text',
        ),
        migrations.AddField(
            model_name='message',
            name='subscription',
            field=models.BooleanField(default=1, verbose_name='Текст'),
            preserve_default=False,
        ),
    ]
