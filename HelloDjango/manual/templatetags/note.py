from django import template
from django.template import loader
from django.utils.safestring import mark_safe
import random as r


S = '$'
register = template.Library()

@register.tag
def notice(parser, token):
    return Note(parser, token=token)

@register.tag
def note(parser, token):
    return Notice(parser, token=token)

@register.tag
def slider(parser, token):
    return Slider(parser, token=token)

@register.tag
def img(parser, token):
    return Img(parser, token=token)

@register.tag
def code(parser, token):
    return Code(parser, token=token)

@register.tag
def news(parser, token):
    return NewsTemplate(parser, token=token)

@register.tag
def check(parser, token):
    return Check(parser, token=token)

@register.tag
def news_desc(parser, token):
    return NewsDesc(parser, token=token)



    

# @register.tag(name="note")
# def do_note_primary(parser, token):
#     return do_note(parser, 'primary')



class Node(template.Node):
    TEMPLATE_PATH = ''
    DEFAULT = 'p'
    SCHEMA = {
    'p': {}
}

    def __init__(self, parser, token):
        self.nodelist = parser.parse(('end',))
        parser.delete_first_token()
        self.token = token
        self.attrs = []
        self.content = dict()

    def get_content(self, output):
        output = output.strip()
        self.content.update({'text': output})

    def get_type(self):
        self.attrs = self.token.contents.split()[1:]
        try:
            type = self.token.contents.split()[1]
        except IndexError:
            type = self.DEFAULT
        try:
            template_content = self.SCHEMA[type]
        except KeyError:
            template_content = self.SCHEMA[self.DEFAULT]
        self.content.update(template_content)

    def render(self, context, ):
        output = self.nodelist.render(context)
        self.get_type()
        self.get_content(output)
        template = loader.get_template(self.TEMPLATE_PATH)
        output = template.render(self.content)
        return output


class Note(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/note_block.html'
    DEFAULT = 'p'
    SCHEMA = {
        'd': {
            'icon': 'exclamation-triangle-fill',
            'class': 'danger'
        },
        'p': {
            'icon': 'info-fill',
            'class': 'primary'
        },
        'w': {
            'icon': 'exclamation-triangle-fill',
            'class': 'warning'
        },
        's': {
            'icon': 'check-circle-fill',
            'class': 'success'
        },
    }
    def get_content(self, output):
        output = output.strip()
        output = mark_safe(output)
        self.content.update(
            {'text': output}
        )

class Notice(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/notice.html'
    DEFAULT = 'p'
    SCHEMA = {
        'd': {
            'class': 'danger'
        },
        'p': {
            'class': 'primary'
        },
        'w': {
            'class': 'warning'
        },
        's': {
            'class': 'success'
        },
    }

    def get_content(self, output):
        output = output.strip()
        title, *lines = output.split('\n')
        text = ''.join(lines)
        text = mark_safe(text)
        self.content.update(
            {'title': title, 'text': text}
        )

class Slider(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/slider.html'
    DEFAULT = 'white'
    SCHEMA = {
        'white': {
            'class': ''
        },
        'w': {
            'class': ''
        },
        'dark': {
            'class': 'carousel-dark'
        },
        'd': {
            'class': 'carousel-dark'
        },
    }

    def get_content(self, output):
        output = output.strip()
        links = output.split('\n')
        result = []
        for link in links:
            link.strip()
            if S in link:
                text, href = link.split(S)
                text, href = text.strip(), href.strip()
                result.append({'href': href, 'text': text})
            else:
                result.append({'href': link})
        self.content.update(
            {'links': result,
             'slider_id': f'slider-{r.randint(0,100)}'
             }
        )

class Img(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/img.html'
    def get_content(self, output):
        output = output.strip()
        if S in output:
            text, href = output.split(S)
            text, href = text.strip(), href.strip()
            result = {'text': text, 'href': href}
        else:
            result = {'href': output}
        self.content.update({'img': result})

class Code(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/code.html'
    def get_content(self, output):
        output = output.strip()
        print('***'*10)
        print(self.attrs)
        if 'safe' in self.attrs:
            self.content.update({'text': mark_safe(output)})
        else:
            self.content.update({'text': output})

class NewsTemplate(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/news_templates.html'

    def get_content(self, output):
        output = output.strip()
        title, *lines = output.split('\n')
        text = ''.join(lines)
        text = mark_safe(text)
        self.content.update(
            {'title': title, 'text': text}
        )

class Check(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/check.html'

    def get_content(self, output):
        output = output.strip()
        checked =''
        if 'c' in self.attrs:
            checked='checked'
        self.content.update(
            {'text': output, 'checked': checked}
        )

class NewsDesc(Node):
    TEMPLATE_PATH = 'manual/blocks_templates/news_description.html'
    def get_content(self, output):
        output = output.strip()
        if S in output:
            ru, eng = output.split(S)
            ru, eng = ru.strip(), eng.strip()
            result = {'ru': mark_safe(ru), 'eng': mark_safe(eng)}
        else:
            result = {'ru': mark_safe(output)}
        self.content.update(result)