from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'manual/index.html')

def note(request):
    return render(request, 'manual/examples/note.html')

def text_block(request):
    return render(request, 'manual/examples/text_block.html')


def list_point(request):
    return render(request, 'manual/examples/list_point.html')

def list_num(request):
    return render(request, 'manual/examples/list_num.html')

def picture(request):
    return render(request, 'manual/examples/picture.html')

def slider(request):
    return render(request, 'manual/examples/slider.html')

def slider_text(request):
    return render(request, 'manual/examples/slider_text.html')


# OFFERS ADD 

def ss_offer(request):
    return render(request, 'manual/add_offer/ss_offer.html')
