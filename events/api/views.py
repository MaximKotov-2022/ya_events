from django.http import HttpResponse
from .get_data_parsing import GetData

def index(request):
    data = GetData.processing_data_website()
    print(data.__str__())
    return HttpResponse(f'Главная страница {data}')
