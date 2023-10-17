from django.http import HttpResponse

from .get_data_parsing import processing_data_website


def index(request):
    data = processing_data_website()
    return HttpResponse(f'Главная страница1111 {data}')
