import datetime
import locale
import os
import time

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram import Bot, ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)
from telegram.utils.request import Request

from tg_bot.models import Profile, Subscription

load_dotenv()

TOKEN = os.getenv('TOKEN')
RETRY_PERIOD = 1800


def process_information_parsing() -> str:
    """Обработка информации после парсинга.
    Возвращает строчку с данными о событиях для бота.

    :rtype: str
    :return: строка в формате, подходящем для отображения в боте у
    пользователей
    """

    response = requests.get('http://127.0.0.1:8000/api/v1/events/')
    if response.status_code == 200:
        data = (
            requests.get(url='http://127.0.0.1:8000/api/v1/events/')
        ).json()
    text = []
    locale.setlocale(locale.LC_ALL, '')
    for event in data:
        date = datetime.datetime.strptime(
            event['date'], "%Y-%m-%d"
        ).date()
        name = event['name']
        site = event['site']
        text.append(f'Дата: {date}\nНазвание: {name}\nСайт: {site}\n\n\n')

    return ''.join(text)


def send_message(self, context, text):
    """Отправка сообщений.

    Принимает текст сообщения.
    """

    chat = self.effective_chat

    buttons = ReplyKeyboardMarkup([
        ['Все мероприятия'],
        ['Подписаться', 'Отписаться'],
    ],
        resize_keyboard=True,
    )

    context.bot.send_message(
        chat_id=chat.id,
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
    )
    return 0


def all_events(self, context):
    """Актуальные мероприятия."""

    text = process_information_parsing()

    return send_message(
            self,
            context,
            text=text,
        )


def checking_data_changes(self, context):
    """Проверка изменений/обновлений данных с сайта.

    Если данные изменились, то возвращается True
    Если нет - False."""

    while True:
        old_data = process_information_parsing()
        time.sleep(RETRY_PERIOD)  # Интервал проверки обновлений на сайте
        new_data = process_information_parsing()

        if old_data != new_data:
            old_data = new_data
            return True
        return False


def hi_say_first_message(self, context):
    """Отправка первого сообщения.

    Получение инфо о возможностях бота."""

    text = ("Привет! Это бот для получения информации о событиях "
            "Яндекса.\n"

            "<u>Все мероприятия</u> - узнать об актуальных событиях\n"

            "<u>Подписаться</u> - получать сообщения при обновлении "
            "информации.\n"

            "<u>Отписаться</u> - отписаться от уведомлений."
            )

    return send_message(
            self,
            context,
            text=text,
        )


def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    obj, created = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    # sub, created = Subscription.objects.update(
    #     external_id=chat_id,
    #     subscription=subscription_status,
    # )
    data = str(process_information_parsing())
    update.message.reply_text(
        text=data,
    )


class Command(BaseCommand):
    help = 'Телеграмм-бот'

    def handle(self, *args, **kwargs):
        # Подключение
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=TOKEN,
        )

        # Обработчики
        updater = Updater(
            bot=bot,
            use_context=True,

        )
        message_handler = MessageHandler(Filters.text, do_echo)
        updater = Updater(token=TOKEN)

        updater.dispatcher.add_handler(CommandHandler(
            'start',
            hi_say_first_message,
            run_async=True,
        )
        )
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Все мероприятия'),
            all_events,
            run_async=True,
        )
        )
        # updater.dispatcher.add_handler(MessageHandler(
        #     Filters.text('Подписаться'),
        #     subscribe_updates,
        #     run_async=True,
        # )
        # )
        # updater.dispatcher.add_handler(MessageHandler(
        #     Filters.text('Отписаться'),
        #     unsubscribe,
        #     run_async=True,
        # )
        # )

        updater.dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()
