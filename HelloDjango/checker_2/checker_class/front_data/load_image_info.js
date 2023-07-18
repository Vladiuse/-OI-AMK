const IMAGE_LOAD_INFO = 'http://127.0.0.1:8000/checker_2/domains/3062/site-images/'
const CSRF_TOKEN = getCookie('csrftoken');
const table = document.getElementById('window-table')
var image_files = {}
var images_tags = []
var RES = null;
const domToInstance = new Map();

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
var bigWindowFrame = null

class ImageCropTool {
    constructor() {
        this.tool_block = null;
        this.table = null;
        // this.table = document.getElementById('crop-images-table')
        this.added_files = {}
    }

    set_table(tool_block){
        this.tool_block = tool_block
        var table = tool_block.querySelector('#crop-images-table')
        this.table = table
        // console.log(table)
        // console.log(tool_block.querySelector('*'))
    }

    show_file_img_count(){
        var file_count_block = this.tool_block.querySelector('#files-count')
        var image_tags_count_block = this.tool_block.querySelector('#image-tags-count')
        file_count_block.innerHTML =   `Файлов найдено: ${Object.keys(image_files).length}шт.`;
        image_tags_count_block.innerHTML = `Картинок найдено: ${images_tags.length}шт.`
    }

    create_table() {
        var table = document.createElement('table')
        this.table = table
        table.id = 'crop-images-table'
        var thead = document.createElement('thead')
        var tbody = document.createElement('tbody')
        var headRow = document.createElement('tr')
        table.appendChild(thead)
        table.appendChild(tbody)
        thead.appendChild(headRow)
        var colNames = ['Image', 'Orig size', 'Page size', 'Weight', 'Thumb', 'Remove']
        colNames.forEach(colName => {
            var headCell = document.createElement('th')
            headCell.innerText = colName
            headRow.appendChild(headCell)
        })
        return table
    }

    add_image_file(image_file) {
        if (image_file._is_add_in_tool == false) {
            image_file._is_add_in_tool = true
            this._add_row(image_file)
        } else {
            console.warn('Image already in tool', image_file)
        }
    }

    _add_row(image_file) {
        var row = document.createElement('tr')
        row.id = 'db-image-'+image_file.back_img_id
        var first_image = image_file.site_images[0]
        var image_tag = document.createElement('img')
        image_tag.src = image_file.src

        var c0_file_back_id = document.createElement('td')
        var c1_image = document.createElement('td')
        var c2_orig_size = document.createElement('td')
        var c3_page_size = document.createElement('td')
        var c4_weight = document.createElement('td')
        var c5_thumb = document.createElement('td')
        var c6_remove = document.createElement('td')
        var file_cells = [c1_image, c2_orig_size, c4_weight, c5_thumb, c6_remove]
        c6_remove.classList.add('_remove')

        c0_file_back_id.innerText = image_file.back_img_id
        c1_image.appendChild(image_tag)
        c2_orig_size.innerText = image_file.orig_img_size_text()
        // c3_page_size.innerText = first_image.size_text()

        c5_thumb.innerText = image_file.crop_size_text
        c4_weight.innerText = image_file.file_size_text()
        c6_remove.innerHTML = '<span>X</span>'

        row.appendChild(c0_file_back_id)
        row.appendChild(c1_image)
        row.appendChild(c2_orig_size)
        row.appendChild(c3_page_size)
        row.appendChild(c4_weight)
        row.appendChild(c5_thumb)
        row.appendChild(c6_remove)

        this.table.querySelector('tbody').append(row)
        if (image_file.length == 1) {
            c3_page_size.innerText = first_image.size_text()
        } else {
            var size_dict = {}
            // CREATE size dict
            for (let i = 0; i < image_file.length; i++) {
                site_image = image_file.site_images[i]
                if (site_image.size_text() in size_dict) {
                    size_dict[site_image.size_text()].push(site_image)
                } else {
                    size_dict[site_image.size_text()] = [site_image, ]
                }
            }
            // add rowspan
            file_cells.forEach(function (elem) {
                elem.rowSpan = Object.keys(size_dict).length
            })
            var counter = 0
            for (var size in size_dict) {
                var curr_zise_images_count = size_dict[size].length
                var image_size_text = `${curr_zise_images_count}шт : ${size}`
                if (size == image_file.crop_size_text) {
                    image_size_text = image_size_text + ' crop size'
                }
                if (counter == 0) {
                    counter = 1
                    c3_page_size.innerText = image_size_text
                } else {
                    var dop_row = document.createElement('tr')
                    var c3_page_size_dop = document.createElement('td')                    
                    c3_page_size_dop.innerText = image_size_text
                    dop_row.appendChild(c3_page_size_dop)
                    this.table.querySelector('tbody').append(dop_row)
                }

            }
        }

    }

    remove_rows() {
        this.table.querySelector('tbody').replaceChildren()
        for (var key in image_files) {
            var image_file = image_files[key]
            image_file._is_add_in_tool = false
        }
    }


    drow_files() {
        this.remove_rows()
        for (var key in image_files) {
            var file = image_files[key]
            if (file.is_need_to_load()) {
                this.add_image_file(file)
            }
        }
    }
}

var image_crop_tool = new ImageCropTool()

class ImageFile {
    constructor(src) {
        this.src = src;
        this.backend_data = null;
        this._is_loaded = false
        this.response = null;
        this._is_req_error = null;
        this.site_images = [];
        this._is_add_in_tool = false;
    }

    get crop_size() {
        var width = this.site_images[0].img.width
        var height = this.site_images[0].img.height
        for (var i = 1; i < this.length; i++) {
            var site_image = this.site_images[i]
            if (site_image.img.width > width) {
                width = site_image.img.width
                height = site_image.img.height
            }
        }
        return {
            'width': width,
            'height': height,
        }
    }
    get back_img_id(){
        return this.backend_data['image']['id']
    }

    get crop_size_text() {
        return `${this.crop_size['width']}x${this.crop_size['height']}`
    }

    get length() {
        return this.site_images.length
    }

    file_size_text() {
        return this.backend_data['image']['orig_img_params']['size_text']
    }

    orig_img_size_text() {
        var w = this.backend_data['image']['orig_img_params']['width']
        var h = this.backend_data['image']['orig_img_params']['height']
        return `${w}x${h}`
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
        images_tags.push(this)
        domToInstance.set(img_tag, this)
    }


    image_commpress() {
        return Math.round((this.img.naturalWidth / this.img.width) * 10) / 10
    }

    size_text() {
        return `${this.img.width}x${this.img.height}`
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
                    image_file = image_files[img.src];
                    image_file.add_image_tag(img)
                } else {
                    var image_file = new ImageFile(img.src)
                    image_file.add_image_tag(img)
                    image_file.process()
                    image_files[img.src] = image_file
                }
            }
        }
    })
}

var observer = null;

function HidePopover() {
    for (src in image_files) {
        var image_file = image_files[src]
        image_file.hide_popovers()
    }
}

function ShowPopover() {
    for (src in image_files) {
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