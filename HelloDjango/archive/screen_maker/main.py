from selenium import webdriver
from time import sleep
import datetime
from pytils import translit
import requests as req


def load_screenshot(url, path_to_save, image_name):
    api_load_image(url, path_to_save,image_name)
    # load_image_selenium(url, path_to_save, image_name)


def load_image_selenium(url, path_to_save, image_name):
    """Загруска скриншота через силениум"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1000,1000")
        browser = webdriver.Chrome('./chromedriver', options=options)
        browser.get(url)
        sleep(1)
        browser.get_screenshot_as_file(path_to_save + image_name)
        browser.quit()
    except BaseException as error:
        print(error)
        with open('./logs/browser.txt', 'a') as file:
            msg = f'{datetime.datetime.now()} - {error}'
            if not msg.endswith('\n'):
                msg += '\n'
            file.write(msg)


def api_load_image(url, path_to_save, image_name):
    """Загрузка сриншота через сервис"""
    service_url = 'https://render-tron.appspot.com/screenshot/'
    res = req.get(service_url + url, stream=True)
    if res.status_code == 200:
        with open(path_to_save + image_name, 'wb') as file:
            for chunk in res:
                file.write(chunk)


if __name__ == '__main__':
    s = 'Китаец(GE).png'
    s = translit.slugify(s)
    print(s)
    exit()
    load_screenshot(
        url='https://b.pro.uromexilforte-new.com/?lang=lv',
        path_to_save=f'',
        image_name=f'./test_images/test.png'
    )

    # https://pythobyte.com/how-to-take-a-screenshot-using-python-selenium-1bgdfdw9s8-e0ae9305/
