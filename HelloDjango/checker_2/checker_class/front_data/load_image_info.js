// const IMAGE_LOAD_INFO = 'http://127.0.0.1:8000/checker_2/get-img-info/'
const IMAGE_LOAD_INFO = 'http://127.0.0.1:8000/checker_2/domains/3062/site-images/'
const  CSRF_TOKEN = getCookie('csrftoken');
var popover_display = 'show'
const table = document.getElementById('window-table')
var site_images = []
var RES = null;

function print(...args) {
    console.log(...args);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class SiteImage {

    constructor(img, popover, backend_data) {
        this.img = img;
        this.popover = popover;
        this.backend_data = backend_data;
        this.is_loaded = false
    }

    is_need_to_load() {
        var ALLOWED_IMG_FORMATS = ['.jpg', '.jpeg', '.bmp', '.webp', '.png']
        if (this.img.src == '') {
            return false
        }
        return ALLOWED_IMG_FORMATS.includes(this.image_extension())
    }

    image_commpress() {
        return Math.round((this.img.naturalWidth / this.img.width) * 10) / 10
    }

    get_popover_style_class() {
        let GREEN = 1.3
        let YELLOW = 1.8
        let ORANGE = 3
        let RED = 3
        let HDiff = this.image_commpress()
        if (HDiff <= GREEN) {
            return 'green'
        }
        if (HDiff > GREEN && HDiff <= YELLOW) {
            return 'yellow'
        }
        if (HDiff > YELLOW && HDiff <= ORANGE) {
            return 'orange'
        }
        if (HDiff > ORANGE) {
            return 'red'
        }
    }

    image_extension() {
        var result = undefined
        var href = this.img.src.toLowerCase()
        let extensions = ['.png', '.gif', '.bmp', '.webp', '.jpg', '.jpeg', 'data:image']
        extensions.forEach(function (ext) {
            if (href.includes(ext)) {
                result = ext
            }
        })
        return result
    }

    full_src() {
        let url = this.img.src;
        if (!url.startsWith('http')) {
            url = base_url + url
        }
        return url
    }
    add_popover(title, content = '', customClass = '') {
        const options = {
            // 'template':POPOVER_TEMPLATE,
            'html': true,
            'content': content,
            'title': title,
            'customClass': customClass,
        }
        let popover = new bootstrap.Popover(this.img, options)
        this.popover = popover;
        popover.show()
        popover.tip.addEventListener("click", (event) => click(event, popover));
    }

    hide_popover() {
        this.popover.hide()
    }
    show_popover() {
        this.popover.show()
    }

    load_back_info() {
        let _class = this
        var data = {
            'image_url': this.full_src(),
            'csrfmiddlewaretoken': CSRF_TOKEN,
        }
        $.post(IMAGE_LOAD_INFO, data = data, )
            .done(function (res, ) {
                print('DONE')
                _class.backend_data = res
                _class.add_loaded_popover()
            })
            .fail(function (res) {
                print('FAIL')
                _class.add_req_error_popover()
            })
    }

    add_loaded_popover() {
        let coof = `x${this.image_commpress()}`
        let page_size = `page: ${this.img.naturalWidth}x${this.img.naturalHeight}`
        let orig_size = `orig: ${this.img.width}x${this.img.height}`
        let img_size = `size: ${this.backend_data['image']['orig_img_params']['size_text']}`
        let content_text = [
            page_size, orig_size, img_size
        ].join('<br>')
        let popover_style = this.get_popover_style_class()
        this.add_popover(coof, content_text, popover_style)
    }

    add_not_loaded_popover() {
        let title = this.image_extension()
        this.add_popover(title)
    }

    add_req_error_popover() {
        this.add_popover('Error REQ', '', 'red')
    }

    process() {
        if (this.is_need_to_load()) {
            this.load_back_info()
        } else {
            this.add_not_loaded_popover()
        }
    }
}

var gif = document.getElementById('gif')

let site_image = new SiteImage(gif)


function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function add_image_in_table(src, orig_size, page_size, weight) {
    let row = table.insertRow(-1)
    let c1 = row.insertCell(-1);
    print(c1)
    let c2 = row.insertCell(-1);
    let c3 = row.insertCell(-1);
    let c4 = row.insertCell(-1);
    let c5 = row.insertCell(-1);
    c1.innerText = src
    c2.innerText = orig_size
    c3.innerText = page_size
    c4.innerText = weight
}

function click(event, popover, img) {
    let title = popover.tip.querySelector('h3')
    print(title)
    title.innerHTML = 'CLICK popover'
    print('CLICK POPOVER')
    print(popover.tip.id)
    print(event)
    print(event.target)
    print(event.target.tagName)
    if (event.target.tagName == 'A') {

    }
}

function get_image_extension(href) {
    var result = undefined
    var href = href.toLowerCase()
    let extensions = ['.png', '.gif', '.bmp', '.webp', '.jpg', '.jpeg', 'data:image']
    extensions.forEach(function (ext) {
        if (href.includes(ext)) {
            result = ext
        }
    })
    return result
}

function is_need_to_load(href) {
    if (href == '') {
        return false
    }
    result = true
    const NOT_LOAD = [
        'chrome-extension',
        'data:image',
        '.gif',
        '.svg',
    ]
    NOT_LOAD.forEach(function (elem) {
        if (href.includes(elem)) {
            result = false
        }
    })
    return result
}

function get_base_tag_href() {
    base = $('base').attr('href')
    if (base) {
        return base
    }
    return false
}

function get_base_url() {
    base = ''
    if (base_href) {
        base = base_href
    } else {
        base = window.location.origin + window.location.pathname
    }
    base = base.replace('index.html', '')
    return base
}

function add_http_to_url(url) {
    if (!url.startsWith('http')) {
        url = base_url + url
    }
    return url
}

const base_href = get_base_tag_href()
const base_url = get_base_url()


function get_img_info(img) {
    let href = img.attr('src')
    img.css('border-bottom', '3px dashed red')
    if (!img.hasClass('load')) {
        img.addClass('load')
        if (is_need_to_load(href)) {
            href = add_http_to_url(href)
            data = {
                'img_href': href
            }
            data = {
                'image_url': href,
                'page_width': img.width(),
                'page_height': img.height(),
                'domain': 1,
            }
            $.post(IMAGE_LOAD_INFO, data = data, function (res) {
                console.log(res)
                add_bubble_img(img, res, href)
            })
        } else {
            add_extention_bubble(img, href)
        }
    }
}

function add_bubble_img(img, back_data, href) {
    var img_js = img.get(0)
    let color_style = get_bubble_style_class(img, back_data)
    let HDiff = Math.round(back_data['image']['orig_img_params']['width'] / img.width() * 10) / 10

    var image_display_style = img.css('display')

    var page_size = `page: ${img.width()}x${img.height()}`
    var orig_size = `orig: ${back_data['image']['orig_img_params']['width']}x${back_data['image']['orig_img_params']['height']}`
    var img_size = 'size: ' + back_data['image']['orig_img_params']['size_text']
    var coof_compression = `coof: x${HDiff}`
    var coof_small = `x<b>${HDiff}</b>`
    var image_ext = `ext: <b>${get_image_extension(href)}</b>`
    var image_display = `display: ${image_display_style}`
    var add_button = '<a>ADD</a>'


    // POPOVER TEST
    if (popover_display == 'show') {
        img.css('border-left', '3px dashed green')
    } else {
        img.css('border-left', '3px dashed red')
    }

    // POPOVER TEST
    var bs_text = [add_button,
        page_size, orig_size, img_size, coof_compression,
        image_ext, image_display
    ].join('<br>')
    img.attr('data-bs-toggle', 'popover')
    img.attr('data-bs-html', true)
    img.attr('title', coof_small)
    img.attr('data-bs-content', bs_text)
    img.attr('data-bs-placement', get_position_of_bubble())
    img.attr('data-bs-custom-class', color_style)
    img.popover({
        template: POPOVER_TEMPLATE,
    }).popover(popover_display)
    let image_id = getRandomInt(9999)
    img.attr('id', image_id)
    let image = document.getElementById(image_id)
    var popover = bootstrap.Popover.getInstance(image)
    popover.tip.addEventListener("click", (event) => click(event, popover, img_js));

}
var POSITION = 0

function get_position_of_bubble() {
    let data = {
        1: 'left',
        2: 'top',
        3: 'right',
        4: 'bottom',
    }
    POSITION++
    if (POSITION == 5) {
        POSITION = 1
    }
    return data[POSITION]
}

function add_extention_bubble(img, href) {
    let ext = get_image_extension(href)
    img.attr('data-bs-toggle', 'popover')
    img.attr('data-bs-html', true)
    img.attr('title', ext)
    // img.attr('data-bs-content', ext)
    img.attr('data-bs-placement', 'right')
    img.popover({
        template: POPOVER_TEMPLATE
    }).popover(popover_display)
}

function get_bubble_style_class(img, back_data) {
    let GREEN = 1.3
    let YELLOW = 1.8
    let ORANGE = 3
    let RED = 3
    let original_width = back_data['image']['orig_img_params']['width']
    let HDiff = Math.round(original_width / img.width() * 10) / 10
    if (HDiff <= GREEN) {
        return 'green'
    }
    if (HDiff > GREEN && HDiff <= YELLOW) {
        return 'yellow'
    }
    if (HDiff > YELLOW && HDiff <= ORANGE) {
        return 'orange'
    }
    if (HDiff > ORANGE) {
        return 'red'
    }
}



// LAZY LOAD
const ImgSelector = 'body img'
const ImgNotLoadedSelector = 'body img:not(.load)'
const IMAGES = document.querySelectorAll('body img')

var POPOVER_DISPLAY = false

const options = {
    root: null,
    rootMargin: '100px',
    threshold: 0.1,
}

function handleImg(myImg, observer) {
    myImg.forEach(myImgSingle => {
        if (myImgSingle.intersectionRatio > 0) {
            // img = $(myImgSingle.target)
            // img.css('border-top', '5px dashed black')
            // get_img_info(img)
            img = myImgSingle.target
            if (!img.classList.contains('_loaded')) {
                img.classList.add('_loaded')
                site_image = new SiteImage(img)
                site_images.push(site_image)
                site_image.process()
            }
        }
    })
}

var observer = null;
function HidePopover() {
    // $('img[data-bs-toggle="popover"]').popover('hide')
    site_images.forEach(site_image => {
        site_image.hide_popover()
    })
}

function ShowPopover() {
    // $('img[data-bs-toggle="popover"]').popover('show')
    site_images.forEach(site_image => {
        site_image.show_popover()
    })
}

function On() {
    console.log('ON')
    var images = document.querySelectorAll(ImgNotLoadedSelector)
    observer = new IntersectionObserver(handleImg, options);

    images.forEach(img => {
        observer.observe(img)

    })
    ShowPopover()
}

function Off() {
    if (observer){
        console.log('OFF')
        IMAGES.forEach(img => {
            observer.unobserve(img)
        })
        observer.disconnect();
        HidePopover()
    }
}


$('body').on('click', '.popover a', function () {
    console.log('click')
})