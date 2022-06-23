from django.shortcuts import render

# Create your views here.

blocks = [{'ЭЛЕМЕНТЫ ДОКУМЕНТАЦИИ': [{'Обратить внимание': '/manual/note'},
                            {'Блок с текстом': '/manual/text_block'},
                            {'Списки': [{'С точками': '/manual/list_point'},
                                        {'Нумерованый': '/manual/list_num'}]},
                            {'Картинка': '/manual/picture'},
                            {'Слайдеры': [{'Без подписи': '/manual/slider'},
                                          {'С подписью': '/manual/slider_text'}]}]},
 {'Заведение оффера': [{'SS оффер': '/manual/ss_offer'}]},
 {'Баги': None}]

def index(request):
    content = {
        'blocks': blocks
        }
    return render(request, 'manual/index.html', content)

def show_page(request, page_path):
    page_path = page_path.replace('.', '/')
    content = {
        'text': 'texttexttexttexttexttexttext',
        'test': [1,2,3,4,5]
        }
    return render(request, f'manual/{page_path}.html', content)


