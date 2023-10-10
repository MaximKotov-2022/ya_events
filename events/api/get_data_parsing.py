import datetime
import locale
import logging
from datetime import date
from urllib.request import urlopen

from bs4 import BeautifulSoup


class GetData:
    """Описание методов обработки данных с сайта."""

    MONTHS = {
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

    @staticmethod
    def site_parsing() -> str:
        """Получение данных сайта (парсинг)."""
        url = "https://events.yandex.ru/"
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        events = soup.find(class_='events__container')

        return events

    def date_converter(self, date: str) -> date:
        '''Конвертер даты к виду гггг-мм-дд. Принмает: строку.'''

        date = date.split()
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
                date_month = self.MONTHS[date[2].replace(',', '')]
                logging.info('date_month', date_month)
            except (KeyError, IndexError):
                logging.warning('Перехвачена ошибка')
                date_month = self.MONTHS[date[2].replace(',', '')]
            date_year = str(datetime.date.today().year)

            return (
                datetime.datetime.strptime(
                date_year + '-' + date_month + '-' + date_number,
                "%Y-%m-%d").date()
            )
        else:
            return date[0]

    @staticmethod
    def processing_data_website() -> list:
        """Обработка данных сайта после парсинга.
        Возвращает словарь (date, name, site). Сериализация.
        """

        events = GetData.site_parsing()
        data_events = []

        for event in events:
            logging.debug('Парсинг информации о каждом мероприятии')
            if len(event) != 0:
                date_find_in_event = event.find(class_='event-card__date').text
                if 'Дата уточняется' not in date_find_in_event:
                    date = GetData.date_converter(date_find_in_event)
                name = event.find(class_='event-card__title').text
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

    def process_information_parsing(self) -> list:
        """Обработка информации после парсинга.
        Возвращает строчку с данными о событиях для БОТа."""

        data = GetData.processing_data_website()
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
