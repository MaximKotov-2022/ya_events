from django.http import HttpResponse

from .get_data_parsing import GetData


def index(request):
    data = GetData.processing_data_website(None)
    return HttpResponse(f'Главная страница1111 {data}')
