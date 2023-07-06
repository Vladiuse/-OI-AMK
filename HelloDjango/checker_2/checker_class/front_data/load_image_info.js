

// const IMAGE_LOAD_INFO = '/get-img-info/'
const IMAGE_LOAD_INFO = '{{ request.scheme }}://{{ request.META.HTTP_HOST }}{%url 'checker_2:get_img_info' %}'
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
var bubbles = []


// MarkAllImages()
// window.addEventListener('resize', remove_bubbles);
function get_img_info(img){
    let href = img.attr('src')
    img.css('border', '2px dashed red')
    if (!img.hasClass('load')){
        img.addClass('load')
        if (is_need_to_load(href)){
            href = add_http_to_url(href)
            data = {'img_href': href}
                $.post(IMAGE_LOAD_INFO, data=data,function(res){
                add_bubble_img(img, res)
                })
        }
    }
}

function add_bubble_img(img, back_data){
    let BUBLE_MARGIN = 3
    //
    let bubble = document.createElement('div')
    bubble.classList.add('bubble')
    set_bubble_on_image(bubble,img)
    $('body').append(bubble)
    bubble.classList.add(
        get_bubble_style_class(img, back_data)
        )
    add_text_to_buuble(bubble,`page: ${img.width()}x${img.height()}`)
    add_text_to_buuble(bubble,`orig: ${back_data['width']}x${back_data['height']}`)
    add_text_to_buuble(bubble,'size: ' + back_data['bytes'] + 'kb')
    let HDiff = Math.round(back_data['width']/img.width()*10)/10
    add_text_to_buuble(bubble,`coof: x${HDiff}`)
    add_text_to_buuble(bubble,`x${HDiff}`, 'coof')


    bubbles.push({
        'bubble': bubble,
        'img': img,
    })
}
function fix_bubbles_positions(){
    bubbles.forEach(function(item){
        set_bubble_on_image(
            item['bubble'],
            item['img'],
        )
    })
}

$(document).click(function(e) { 
    // Check for left button
    fix_bubbles_positions()
    });

function set_bubble_on_image(bubble,img){
    let BUBLE_MARGIN = 3
    bubble.style.top = img.offset().top + BUBLE_MARGIN + 'px'
    bubble.style.left = img.offset().left + BUBLE_MARGIN + 'px'
}

function add_text_to_buuble(bubble,text, _class){
    let TEXT_TAG = 'p'
    let elem = document.createElement(TEXT_TAG)
    elem.textContent += text
    bubble.appendChild(elem)
    if (_class != undefined){elem.classList.add(_class)}
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

function remove_bubbles(){
    $('.bubble').remove()
    $('img.load').removeClass('load')
}


$('img').click(function(){
    get_img_info($(this))
})


function markImage(img){
    get_img_info($(img))
}


// LAZY LOAD
const images = document.querySelectorAll('body img')

const options = {
    root: null,
    rootMargin: '100px',
    threshold: 0.1,
}

function handleImg(myImg, observer){
    myImg.forEach(myImgSingle => {
    if (myImgSingle.intersectionRatio > 0){
    //   loadImage(myImgSingle.target)
        markImage(myImgSingle.target)
    }
    })
}


const observer = new IntersectionObserver(handleImg, options);

images.forEach(img => {
    observer.observe(img)
})

