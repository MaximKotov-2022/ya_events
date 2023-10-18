import datetime
import locale
import logging
from typing import List
from urllib.request import urlopen

from bs4 import BeautifulSoup

MONTHS_CHOICE = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

def site_parsing() -> str:
    """Получение данных сайта (парсинг).

    :rtype: bs4.element.Tag
    :return: тип данных объекта BeautifulSoup, представляющий HTML теги
    """
    url = "https://events.yandex.ru/"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    events = soup.find(class_='events__container')
    return events


def date_converter(date: str):
    """Конвертер строки даты к виду гггг-мм-дд.

    :param date: дата в виде строки ДН, дата месяц
    :type date: str

    :rtype: str
    :return: Вид datetime ГГГГ-ММ-ДД
    """

    # [0] - день недели (ПН, ВТ...), [1] - дата (день месяца, 1-31),
    # [2] - месяц (январь и т.д.).
    date = date.split()
    # Проверка на наличие в дате слов "сегодня" или "завтра"
    flag_data_today_tomorrow = False

    if date[0] == 'сегодня':
        date[0] = str(datetime.date.today())
        flag_data_today_tomorrow = True
    elif date[0] == 'завтра':
        date[0] = str(datetime.date.today() + datetime.timedelta(days=1))
        flag_data_today_tomorrow = True

    if flag_data_today_tomorrow is False:
        date_number = date[1]
        if len(date_number) < 2:
            date_number = '0' + date_number

        try:
            date_month = MONTHS_CHOICE[date[2].replace(',', '')]
            logging.info('date_month', date_month)
        except (KeyError, IndexError):
            logging.warning('Перехвачена ошибка')
            date_month = MONTHS_CHOICE[date[2].replace(',', '')]
        date_year = str(datetime.date.today().year)

        return (
            datetime.datetime.strptime(
            date_year + '-' + date_month + '-' + date_number,
            "%Y-%m-%d").date()
        )
    else:
        return date[0]


def processing_data_website() -> list:
    """Обработка данных сайта после парсинга.

    В методе выделяем отдельные данные (дату, название, сайт мероприятий),
    а затем добавляем их в массив, который возвращаем для дальнейших
    операций.

    :rtype: list
    :return: Возвращает список (массив) со словарями, имеющими ключи
    date, name, site
    """
    events = site_parsing()
    data_events = []

    for event in events:
        logging.info('Парсинг информации о каждом мероприятии')
        if len(event) != 0:
            # Получаем информацию о дате проведения мероприятия.
            date_find_in_event = event.find(class_='event-card__date')
            if 'Дата уточняется' not in date_find_in_event:
                try:
                    date = date_converter(date_find_in_event.text)
                    logging.info('Дата мероприятия: {}'.format(date))
                except TypeError:
                    logging.warning('Неверный формат даты: {}'.format(
                        date_find_in_event.get_text()))
                    date = None

            name = event.find(class_='event-card__title')

            # Создаём ссылку. Так как в некоторых мероприятиях указана полная
            # ссылка на регистрацию, то мы делаем проверку для создания ссылки.
            if 'https' not in event.find('a').get('href'):
                site = (
                    'https://events.yandex.ru'
                    + event.find('a').get('href')
                )
            else:
                site = event.find('a').get('href')

            data_events.append(
                {
                    "date": str(date),
                    "name": name,
                    "site": site,
                }
            )

    return data_events


def process_information_parsing() -> list[str]:
    """Обработка информации после парсинга.
    Возвращает строчку с данными о событиях для бота.

    :rtype: str
    :return: строка в формате, подходящем для отображения в боте у
    пользователей
    """

    data = processing_data_website()
    text = []
    locale.setlocale(locale.LC_ALL, '')
    for event in data:
        date = (
            datetime.datetime.strptime(event['date'], "%Y-%m-%d")
        ).strftime("%a, %d %B")
        name = event['name']
        site = event['site']
        text.append(f'Дата: {date}\nНазвание: {name}\nСайт: {site}\n\n\n')

    return text
