console.log('MY SCRIPNT START')
// $(document).ready(function(){
    let toggleTime = 300;

    let isDebug = false;
    let debugClass = '__debug';
    let debugMsgClass = '__debug_msg';
    let formNoSelectClass = '__debug_no_select';
    let fromInputNotelClass = '__debug_no_tel';
    let debugScritpDate = '__debug_script_date';
    let doubleImgStyle = '__debug_double';
    let toolbarErrorClass = '__error';


    let imgBoubleCounter = 0;
    let imgBoubleLen = 0;
    let lastDoubleScr = ''


    function showCkickEmems(){
        // кликабельные элементы
        findAlla();
        findImgLink();
        findDivLink();
    }

    function showFormEmels(){
        // форма
        FormSelectBebug(); 
        formInputType();
        showInputTypes();

    }

    function showPrices(){
        // цены и скидки
        findPrice();
        findCurrency();
        findDiscount();
        findCity();
    }

    function showDates(){
        // Даты
        findSriptsDate();
    }

    function showImages(){
        // Картинки
        findImgDouble();
    }

    // MAIN
    function onOffDebug(){
        if (isDebug){
            // кликабельные элементы
            // findAlla();
            // findImgLink();
            // findDivLink();
            
            // форма
            // FormSelectBebug(); 
            // formInputType();
            // showInputTypes();
            
            // цены и скидки
            // findPrice();
            // findCurrency();
            // findDiscount();
            // findCity();

            // Даты
            // findSriptsDate();

            // Картинки
            findImgDouble();

        }
        else{
            removeAllDebug()
        }

    }

    // Получить обьект сообщения о ошибке
    function getMsg(){
        let msg = $('<span></span>')
        msg.addClass(debugMsgClass)
        return msg
    }

    // Удаление всех классов и элементов debug
    function removeAllDebug(){
        RemoveIoPlaceholder();
        removeDebugMsg()
        let forms = $('form.'+formNoSelectClass)
        forms.removeClass(formNoSelectClass)
        let scriptDate = $('.' + debugScritpDate).removeClass(debugScritpDate)
        $('input').removeClass(fromInputNotelClass)
        x = document.querySelectorAll('.__debug');
        for (pos in x){
            let elem = x[pos]
            if (elem.classList != undefined){
                elem.classList.remove(debugClass);
            }
        }
    }

    // удаление сообщений о ошибках с лэндинга
    function removeDebugMsg(){
        let msgs = $('.' + debugMsgClass)
        msgs.remove()
    }

    // Выбор форм с ошибками селекта(его отсутствия)
    function FormSelectBebug(){
        let forms = $('form')
        let formsNoSelect = forms.filter(function(){
            if($(this).find('select').length == 0){
                return true
            }
        })

        formsNoSelect.addClass(formNoSelectClass)
        formsNoSelect.each(function(){
            let msg = getMsg()
            msg.text('Нет селекта страны!!!')
            $(this).append(msg)
        })
    }

    // Поиск инпутов с некоректным атрибутом type
    function formInputType(){
        let inputs = $('form input[name=phone]')
        let inputsNoTel = inputs.filter(function(){
            if ($(this).attr('type') != 'tel'){
                return true
            }
        })
        inputsNoTel.addClass(fromInputNotelClass)
    }

    // Выборка всех ссылок
    function findAlla(){
        let links = $('a')
        console.log(toggleTime, 'toggleTime FROM my SCRIPT IN FUNC');
        links.addClass(debugClass)
    }

    // Выборка картинок внутри ссылок
    function findImgLink(){
        let imgs = $('a img') // button input img svg path
        imgs.addClass(debugClass)
        imgs.each(function(){
            let link = $(this).parent()
            if (link.children().length == 1){
                link.removeClass(debugClass)
            }
        })
      }

    // Выборка <div> внутри ссылок
    function findDivLink(){
        let divs = $('a div') // button input img svg path
        divs.addClass(debugClass)
        divs.each(function(){
            let link = $(this).parent()
            if (link.children().length == 1){
                link.removeClass(debugClass)
            }
        })
    }
    
    // Выборка всех цен (по классу)
    function findPrice(){
        let allPrices = $('.price_land_s1,.price_land_s2,.price_land_s3,.price_land_s4')
        allPrices.addClass(debugClass)
    }

    // Выборка всех валют (по классу)
    function findCurrency(){
        let currencys = $('.price_land_curr')
        currencys.addClass(debugClass)
    }

    // поиск скидки
    function findDiscount(){
        let discounts = $('.price_land_discount')
        discounts.addClass(debugClass)
    }

    function showInputTypes(){
        let inputs = $('input')
        inputs.each(function(){
            if ($(this).attr('placeholder') != undefined){
                $(this).attr('oi-placeholder', $(this).attr('placeholder'))
                let new_placeholder = $(this).attr('placeholder') + ' | type=' + $(this).attr('type')
                new_placeholder.replaceAll('  ', ' ')
                $(this).attr('placeholder', new_placeholder)
            } else {
                $(this).attr('oi-placeholder', '')
                $(this).attr('placeholder', 'type=' + $(this).attr('type'))
            }
            
            
        })
    }
    function RemoveIoPlaceholder(){
        let inputs = $('input')
        inputs.each(function(){
            $(this).attr('placeholder',$(this).attr('oi-placeholder') )
        })
    }

    // Поиск элементов с script внутри (возможно это скрипт даты)
    function findSriptsDate(){
        let elems = $('body script')
            elems = elems.filter(function(){
                if ($(this).parent().is('body') != true) {return true}
            })
            elems.addClass(debugScritpDate)
            elems.text('!!!')
        }
    
    function findCity(){
        $('.geocity,.user-city').addClass(debugClass)
    }

    // Поиск и добавление рамки для дублей картинок
    function findImgDouble(){
        let imgDouble = $('img.'+doubleImgStyle)
        imgDouble.addClass(debugClass)
    }
    
    // Скролл по дублям картинок
    function doubleImgScroll(img_hash){
        $('img.__focus_img').removeClass('__focus_img')
        // let src = $(this).attr('data-oi-img')
        let src = img_hash
        // console.log(src, 'src дубля')
        if (src != lastDoubleScr){imgBoubleCounter = 0}
        lastDoubleScr = src
        let imgs = $('img.'+doubleImgStyle).filter(function(){
            if ($(this).attr('data-oi-img-double') == src){return true}
        })
        imgBoubleLen = imgs.length
        console.log(imgBoubleCounter, imgBoubleLen)
        imgs.get(imgBoubleCounter).scrollIntoView({block: "center", behavior: "smooth"});
        $(imgs.get(imgBoubleCounter)).addClass('__focus_img') // xxx
        imgBoubleCounter ++
        if (imgBoubleCounter  >= imgBoubleLen) {imgBoubleCounter=0; console.log('Сброс счетчика')}
    }

    $('#back-info img').click(function(){
        
        })


    // Включение тулбара клавишами
    $(document).keyup(function(e) {
        // i = 73 p = 80 q = 81 y = 17 b = 66
        let oiToolbar = $('#oi-toolbar')
        if (e.ctrlKey && e.keyCode == 66) {
            console.log('%c OI-INTEGRATION DEBUG TOOL', 'background: #212529; color: #73BC9E; font-weight:bold; padding:3px');
            if (isDebug){isDebug = false}else{isDebug = true}
            oiToolbar.toggle(500)
            onOffDebug()
        }
});
console.log('MY SCRIPNT END')