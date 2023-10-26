import datetime
import locale
import logging
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

# logging.basicConfig(
#     format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
#     level=logging.INFO,
#     filename='bot.log',
#     filemode='w',
#     encoding='utf-8',
# )

TOKEN = os.getenv('TOKEN')
RETRY_PERIOD = int(os.getenv('RETRY_PERIOD', 1800))


def process_information_parsing() -> str:
    """Обработка информации после парсинга.
    Возвращает строчку с данными о событиях для бота.

    :rtype: str
    :return: строка в формате, подходящем для отображения в боте у
    пользователей
    """

    response = requests.get('http://127.0.0.1:8000/api/v1/events/')
    if response.status_code == 200:
        data = requests.get(url='http://127.0.0.1:8000/api/v1/events/').json()

    text = []
    locale.setlocale(locale.LC_ALL, '')

    for event in data:
        date = datetime.datetime.strptime(
            event['date'], "%Y-%m-%d").date()
        name = event['name']
        site = event['site']
        text.append(f'Дата: {date}\nНазвание: {name}\nСайт: {site}\n\n\n')

    return ''.join(text)


def send_message(chat_id, context, text):
    """
    Отправка сообщений.

    Принимает текст сообщения и отправляет его в указанный чат с использованием
    переданного объекта контекста.

    :param chat_id: идентификатор чата, в который будет отправлено сообщение.
    :type chat_id: int
    :param context: Объект контекста, предоставляющий доступ к ресурсам и
    информации, связанным с текущим обработчиком сообщений.
    :type context: telegram.ext.CallbackContext
    :param text: Текст сообщения, которое нужно отправить.
    :type text: str
    :return: Возвращает 0 в случае успешной отправки сообщения.
    :rtype: int
    """

    buttons = ReplyKeyboardMarkup([
        ['Все мероприятия'],
        ['Подписаться', 'Отписаться'],
    ],
        resize_keyboard=True,
    )

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=buttons,
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
    )

    return 0


def all_events(update: Update, context: CallbackContext):
    """
    Обработка команды 'Все мероприятия'.

    :param update: Обновление.
    :type update: telegram.Update
    :param context: Контекст.
    :type context: telegram.ext.callbackcontext.CallbackContext
    :return: Возвращает 0 в случае успешной отправки сообщения.
    :rtype: int
    """

    chat_id = update.message.chat_id

    Subscription.objects.get_or_create(
        profile__external_id=chat_id,
        defaults={
            'profile': Profile.objects.get_or_create(
                external_id=update.message.chat_id,
                name=update.effective_user.username)[0],
            'subscription': False
        }
    )
    data = process_information_parsing()
    send_message(chat_id,
                 context,
                 data)

    return data


def checking_data_changes() -> bool:
    """
    Проверка изменений/обновлений данных с сайта.

    Если данные изменились, то возвращается True
    Если нет - False.

    :return: Логическое значение, указывающее, есть ли какие-либо обновления
    :rtype: bool
    """

    while True:
        old_data = process_information_parsing()
        time.sleep(RETRY_PERIOD)  # Интервал проверки обновлений на сайте
        new_data = process_information_parsing()
        logging.debug(f'Равны ли старые и новые данные:{old_data == new_data}')
        if old_data != new_data:
            return True
        return False


def hi_say_first_message(update: Update, context: CallbackContext):
    """
    Отправка первого сообщения.

    Получение инфо о возможностях бота.

    :param update: Объект обновления.
    :param context: Контекст обратного вызова.
    :return: Результат работы функции send_message.
    """
    chat_id = update.effective_chat.id
    text = ("Привет! Это бот для получения информации о событиях "
            "Яндекса.\n"

            "<u>Все мероприятия</u> - узнать об актуальных событиях\n"

            "<u>Подписаться</u> - получать сообщения при обновлении "
            "информации.\n"

            "<u>Отписаться</u> - отписаться от уведомлений."
            )

    return send_message(chat_id,
                        context,
                        text=text,)


def subscribe(update: Update, context: CallbackContext):
    """
    Подписка пользователя на получение обновлений.

    :param update: Объект обновления.
    :param context: Контекст обратного вызова.
    :return: Возвращает 0 в случае успешной отправки сообщения.
    :rtype: Int
    """
    chat_id = update.effective_chat.id

    subscription, created = Subscription.objects.get_or_create(
        profile__external_id=chat_id,
        defaults={
            'profile': Profile.objects.get_or_create(
                external_id=update.message.chat_id,
                name=update.effective_user.username)[0],
            'subscription': True
        }
    )

    if subscription.subscription:
        update.message.reply_text('Вы уже подписаны на обновления')
    else:
        # Если подписка уже есть, то обновляем значение поля subscription в БД
        subscription.subscription = True
        subscription.save()
        update.message.reply_text('Вы успешно подписались на обновления')
    check_updates(update, context)

    return 0


def unsubscribe(update: Update, context: CallbackContext):
    """
    Отписка пользователя от получений обновлений.

    :param update: Объект обновления.
    :param context: Контекст обратного вызова.
    :return: Возвращает 0 в случае успешной отправки сообщения.
    :rtype: Int
    """
    chat_id = update.effective_chat.id

    subscription, created = Subscription.objects.get_or_create(
        profile__external_id=chat_id,
        defaults={
            'profile': Profile.objects.get_or_create(
                external_id=update.message.chat_id,
                name=update.effective_user.username)[0],
            'subscription': False
        }
    )

    if subscription.subscription:
        # Если подписка уже есть, то обновляем значение поля subscription в БД
        subscription.subscription = False
        subscription.save()
        update.message.reply_text('Вы отписались от обновлений')
    else:
        update.message.reply_text('Вы не подписаны на обновления')

    return 0


def check_updates(update: Update, context: CallbackContext):
    """
    Функция постоянно проверяет наличие изменений в данных и отправляет
    сообщения подписанным пользователям.

    :param update: Объект обновления.
    :param context: Контекст обратного вызова.
    :return: Возвращает 0.
    :rtype: Int
    """
    while True:
        if checking_data_changes():
            subscriptions = Subscription.objects.filter(subscription=True)
            for subscription in subscriptions:
                chat_id = subscription.profile.external_id
                send_message(chat_id, context, process_information_parsing())
    return 0


def do_echo(update: Update, context: CallbackContext):
    """
    Обрабатывает текст, которого нет в командах.
    Добавляет данные о пользователе в БД.

    :param update: Объект обновления.
    :param context: Контекст обратного вызова.
    :return: Возвращает 0 в случае успешной отправки сообщения.
    :rtype: int
    """
    chat_id = update.message.chat_id

    Subscription.objects.get_or_create(
        profile__external_id=chat_id,
        defaults={
            'profile': Profile.objects.get_or_create(
                external_id=update.message.chat_id,
                name=update.effective_user.username)[0],
            'subscription': False
        }
    )

    update.message.reply_text(text='Неизвестная команда')

    return 0


class Command(BaseCommand):
    """Команды Telegram-бота."""

    help = 'Телеграмм-бот'

    def handle(self, *args, **kwargs):
        """
        Обработчик команд бота.

        :param args: Аргументы команды.
        :type args: Any
        :param kwargs: Аргументы ключевого слова команды.
        :type kwargs: Any
        :return: None
        """

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
        # updater = Updater(token=TOKEN)

        # Обработки команд
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
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Подписаться'),
            subscribe,
            run_async=True,
        )
        )
        updater.dispatcher.add_handler(MessageHandler(
            Filters.text('Отписаться'),
            unsubscribe,
            run_async=True,
        )
        )

        # Обработчик сообщений по умолчанию
        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        updater.start_polling()
        updater.idle()
