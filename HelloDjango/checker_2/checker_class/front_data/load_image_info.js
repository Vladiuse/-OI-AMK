

// const IMAGE_LOAD_INFO = '/get-img-info/'
const IMAGE_LOAD_INFO = '{{ request.scheme }}://{{ request.META.HTTP_HOST }}{%url 'checker_2:get_img_info' %}'
const POPOVER_TEMPLATE = '<div class="popover" role="tooltip"><div class="popover-arrow"></div><div class="popover-header"></div><div class="popover-body"></div></div>'
var popover_display = 'show'

function get_image_extension(href){
    var result = undefined
    var href = href.toLowerCase()
    let extensions = ['.png','.gif', '.bmp', '.webp', '.jpg', '.jpeg','data:image']
    extensions.forEach(function(ext){
        if (href.includes(ext))
        {result= ext}
    })
    return result
}

function is_need_to_load(href){
    if (href==''){return false}
    result = true
    const NOT_LOAD = [
        'chrome-extension',
        'data:image',
        '.gif',
        '.svg',
    ]
    NOT_LOAD.forEach(function(elem){
        if (href.includes(elem)){
            result = false
        }
    })
    return result
}

function get_base_tag_href(){
    base = $('base').attr('href')
    if (base){return base}
    return false
}
function get_base_url(){
    base = ''
    if (base_href){
        base = base_href
    }else {base = window.location.origin + window.location.pathname}
    base = base.replace('index.html', '')
    return base
}

function add_http_to_url(url){
    if (!url.startsWith('http')){
        url = base_url +url
    }
    return url
}

const base_href = get_base_tag_href()
const base_url = get_base_url()


function get_img_info(img){
    let href = img.attr('src')
    img.css('border-bottom', '3px dashed red')
    if (!img.hasClass('load')){
        img.addClass('load')
        if (is_need_to_load(href)){
            href = add_http_to_url(href)
            data = {'img_href': href}
                $.post(IMAGE_LOAD_INFO, data=data,function(res){
                add_bubble_img(img, res,href)
                })
        } else{
            add_extention_bubble(img,href)
        }
    }
}

function add_bubble_img(img, back_data,href){
    let color_style = get_bubble_style_class(img, back_data)
    let HDiff = Math.round(back_data['width']/img.width()*10)/10

    var image_display_style = img.css('display')

    var page_size = `page: ${img.width()}x${img.height()}`
    var orig_size = `orig: ${back_data['width']}x${back_data['height']}`
    var img_size = 'size: ' + back_data['bytes'] + 'kb'
    var coof_compression = `coof: x${HDiff}`
    var coof_small = `x<b>${HDiff}</b>`
    var image_ext = `ext: <b>${get_image_extension(href)}</b>`
    var image_display = `display: ${image_display_style}`


    // POPOVER
    if (popover_display=='show'){
        img.css('border-left', '3px dashed green')
    } else {
        img.css('border-left', '3px dashed red')
    }
    console.log('Set popover', popover_display)
    var bs_text = [
        page_size,orig_size,img_size,coof_compression,
        image_ext,image_display].join('<br>')
    // img.attr('data-bs-html', true)
    img.attr('data-bs-toggle', 'popover')
    img.attr('data-bs-html', true)
    img.attr('title', coof_small)
    img.attr('data-bs-content', bs_text)
    img.attr('data-bs-placement', get_position_of_bubble())
    img.attr('data-bs-custom-class', color_style)
    img.popover({ template: POPOVER_TEMPLATE}).popover(popover_display)
}
var POSITION = 0
function get_position_of_bubble(){
    let data = {
        1: 'left',
        2: 'top',
        3: 'right',
        4: 'bottom',
    }
    POSITION ++
    if (POSITION == 5) {POSITION = 1}
    return data[POSITION]
}

function add_extention_bubble(img,href){
    let ext = get_image_extension(href)
    img.attr('data-bs-toggle', 'popover')
    img.attr('data-bs-html', true)
    img.attr('title', ext)
    // img.attr('data-bs-content', ext)
    img.attr('data-bs-placement', 'right')
    img.popover({ template: POPOVER_TEMPLATE}).popover(popover_display)
}

function get_bubble_style_class(img, back_data){
    let GREEN = 1.3
    let YELLOW = 1.8
    let ORANGE = 3
    let RED = 3
    let HDiff = Math.round(back_data['width']/img.width()*10)/10
    if (HDiff <= GREEN)
        {return 'green'}
    if (HDiff > GREEN && HDiff <= YELLOW)
        {return 'yellow'}
    if (HDiff > YELLOW && HDiff <= ORANGE)
        {return 'orange'}
    if (HDiff > ORANGE)
        {return 'red'}
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

function handleImg(myImg, observer){
    myImg.forEach(myImgSingle => {
    if (myImgSingle.intersectionRatio > 0){
        img = $(myImgSingle.target)
        img.css('border-top', '5px dashed black')
        get_img_info(img)
    }
    })
}

var observer = new IntersectionObserver(handleImg, options);

IMAGES.forEach(img => {
    observer.observe(img)

})

function HidePopover(){
    $('img[data-bs-toggle="popover"]').popover('hide')
}
function ShowPopover(){
    $('img[data-bs-toggle="popover"]').popover('show')
}

function On(){
    var images = document.querySelectorAll(ImgNotLoadedSelector)
    observer = new IntersectionObserver(handleImg, options);

    images.forEach(img => {
        observer.observe(img)

    })
    ShowPopover()
}

function Off(){
    IMAGES.forEach(img => {
        observer.unobserve(img)
    })
    observer.disconnect();
    HidePopover()
}

