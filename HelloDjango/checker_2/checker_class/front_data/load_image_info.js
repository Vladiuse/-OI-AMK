// const IMAGE_LOAD_INFO = 'http://127.0.0.1:8000/checker_2/get-img-info/'
const IMAGE_LOAD_INFO = 'http://127.0.0.1:8000/checker_2/domains/3062/site-images/'
const CSRF_TOKEN = getCookie('csrftoken');
var popover_display = 'show'
const table = document.getElementById('window-table')
var image_files = {}
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
class ImageFile {
    constructor(src, img_tag) {
        this.src = src;
        this.backend_data = null;
        this._is_loaded = false
        this.response = null;
        this._is_req_error = null;
        this.site_images = [new SiteImage(this, img_tag), ];
    }

    add_image_tag(img_tag) {
        var site_image = new SiteImage(this, img_tag)
        this.site_images.push(site_image)
        if (this._is_loaded) {

            if (this._is_req_error == false) {
                site_image.add_loaded_popover()
            } else {
                print('addd_req_error')
                site_image.add_req_error_popover(this._is_req_error)
            }
        }

        if (this.is_need_to_load() == false) {
            site_image.add_not_loaded_popover()
        }
    }

    set_is_loaded() {
        this._is_loaded = true
    }

    load_back_info() {
        let _class = this
        var data = {
            'image_url': this.full_src(),
            'csrfmiddlewaretoken': CSRF_TOKEN,
        }
        console.warn('LOAD', this.src)
        $.post(IMAGE_LOAD_INFO, data = data, )
            .done(function (res, ) {
                print('DONE')
                _class.response = res;
                _class._is_req_error = false
                _class.backend_data = res
                _class.site_images.forEach(function (site_image) {
                    site_image.add_loaded_popover()
                })
            })
            .fail(function (res) {
                print('FAIL')
                _class.response = res;
                _class._is_req_error = true
                _class.site_images.forEach(function (site_image) {
                    site_image.add_req_error_popover(res)
                })

            })
            .always(function (res) {
                _class.set_is_loaded()
            })
    }

    is_need_to_load() {
        var ALLOWED_IMG_FORMATS = ['.jpg', '.jpeg', '.bmp', '.webp', '.png']
        if (this.src == '') {
            return false
        }
        return ALLOWED_IMG_FORMATS.includes(this.image_extension())
    }
    image_extension() {
        var result = 'No exception'
        var href = this.src.toLowerCase()
        let extensions = ['.png', '.gif', '.bmp', '.webp', '.jpg', '.jpeg', 'data:image']
        extensions.forEach(function (ext) {
            if (href.includes(ext)) {
                result = ext
            }
        })
        return result
    }

    full_src() {
        let url = this.src;
        if (!url.startsWith('http')) {
            url = base_url + url
        }
        return url
    }

    process() {
        if (this.is_need_to_load()) {
            this.load_back_info()
        } else {
            this.site_images.forEach(function (site_image) {
                site_image.add_not_loaded_popover()
            })
        }
    }

    show_popovers() {
        this.site_images.forEach(function (site_image) {
            site_image.show_popover()
        })
    }
    hide_popovers() {
        this.site_images.forEach(function (site_image) {
            site_image.hide_popover()
        })
    }
}
class SiteImage {

    constructor(file, img_tag) {
        this.file = file;
        this.img = img_tag;
        this.popover = null;
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

    add_popover(title, content = '', customClass = '') {
        const options = {
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


    add_loaded_popover() {
        let coof = `x${this.image_commpress()}`
        let page_size = `page: ${this.img.naturalWidth}x${this.img.naturalHeight}`
        let orig_size = `orig: ${this.img.width}x${this.img.height}`
        let img_size = `size: ${this.file.backend_data['image']['orig_img_params']['size_text']}`
        let content_text = [
            page_size, orig_size, img_size
        ].join('<br>')
        let popover_style = this.get_popover_style_class()
        this.add_popover(coof, content_text, popover_style)
    }

    add_not_loaded_popover() {
        let title = this.file.image_extension()
        this.add_popover(title)
    }

    add_req_error_popover(req_error) {
        let text = JSON.stringify(req_error)
        this.add_popover('Error REQ', text, 'red')
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


const base_href = get_base_tag_href()
const base_url = get_base_url()

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
    var image_observed_class = '_observed'
    myImg.forEach(myImgSingle => {
        if (myImgSingle.intersectionRatio > 0) {
            img = myImgSingle.target
            if (!img.classList.contains(image_observed_class)) {
                img.classList.add(image_observed_class)
                if (img.src in image_files) {
                    print(1)
                    image_file = image_files[img.src];
                    image_file.add_image_tag(img)
                } else {
                    var image_file = new ImageFile(img.src, img)
                    image_files[img.src] = image_file
                    image_file.process()
                }
            }
        }
    })
}

var observer = null;

function HidePopover() {
    for (src in image_files){
        var image_file = image_files[src]
        image_file.hide_popovers()
    }
}

function ShowPopover() {
    for (src in image_files){
        var image_file = image_files[src]
        image_file.show_popovers()
    }
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
    if (observer) {
        console.log('OFF')
        IMAGES.forEach(img => {
            observer.unobserve(img)
        })
        observer.disconnect();
        HidePopover()
    }
}