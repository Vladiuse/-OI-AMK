from io import BytesIO
from PIL import Image
import requests as req
import sys

href = 'https://previewpreland.pro/shinval-buzova/img/xpic8.jpg.pagespeed.ic.7nzA5C5noP.jpg'


def get_image_info(href):
    res = req.get(href)
    bound = BytesIO(res.content)
    img = Image.open(bound)
    w, h = img.size
    try:
        bytes = res.headers['Content-Length']
        bytes_from = 'headers'
    except KeyError:
        bytes = sys.getsizeof(res.content)
        bytes_from = 'request'
    result = {
        'width': w,
        'height': h,
        'bytes': round(int(bytes) / 1024, 2),
        'bytes_from': bytes_from,
    }
    return result