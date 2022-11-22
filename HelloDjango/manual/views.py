from django.shortcuts import render
import yaml
from django.conf import settings
from django.template import Template
from django.template import Context
from django.http import HttpResponse


PERSONS = {
    'test_potok_man': '@Славик',
    'test_integration': '@Славик', # ответственный за тест интеграции с реклом
    'настройка_интеграции': '@Славик',
    'чат_верстка_ои': 'kma_oi_правки',
    'распределение_таски_промо': 'Сергей Сульженко',
    'vitrina_web': 'vitrina', # веб для витрины
}

class Block:

    def __init__(self, block_data):
        self.data = block_data
        self.name = None
        self.links = []

    def process(self):
        self.get_name()
        self.get_links()


    def get_name(self):
        for block_name, links in self.data.items():
            self.name = block_name

    def get_links(self):
        links = self.data[self.name]
        for link in links:
            r_link = {}
            for link_name, link_path in link.items():
                r_link['name'] = link_name
                r_link['path'] = link_path
                r_link['type'] = True
                r_link['sub'] = []
                if isinstance(link_path, list):
                    r_link['type'] = False
                    subs_li = []
                    for sub_link in link_path:
                        for name, path in sub_link.items():
                            sub ={}
                            sub['name'] = name
                            sub['path'] = path
                            subs_li.append(sub)
                    r_link['sub'] = subs_li
            self.links.append(r_link)

    def __iter__(self):
        pass

def get_side_links():
    yaml_path = str(settings.BASE_DIR) + '/manual/side.yaml'
    with open(yaml_path, encoding='utf-8') as f:
        template = yaml.safe_load(f)
    blocks = []
    for block_data in template:
        block = Block(block_data)
        block.process()
        blocks.append(block)
    return blocks

def index(request):
    content = {
        'blocks': get_side_links()
        }
    content.update(PERSONS)
    return render(request, 'manual/index.html', content)

def show_page(request, page_path):
    page_path = page_path.replace('.', '/')
    content = {
        'blocks': get_side_links()
        }
    content.update(PERSONS)
    return render(request, f'manual/{page_path}.html', content)



