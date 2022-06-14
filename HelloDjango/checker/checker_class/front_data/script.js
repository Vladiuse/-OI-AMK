// $(document).ready(function(){


        let currentUrl = window.location.origin
        let toggleTime = 300;
        let isDebug = false;
        // let errorCount = 0;
        let debugClass = '__debug';
        let debugMsgClass = '__debug_msg';
        let formNoSelectClass = '__debug_no_select';
        let fromInputNotelClass = '__debug_no_tel';
        let debugScritpDate = '__debug_script_date'
        let doubleImgStyle = '__debug_double'
        let toolbarErrorClass = '__error';


        let imgBoubleCounter = 0;
        let imgBoubleLen = 0;
        let lastDoubleScr = ''
        let PhoneMask = '';

        // $.fn.removeClassStartingWith = function (filter) {
        // $(this).removeClass(function (index, className) {
        //     return (className.match(new RegExp("\\S*" + filter + "\\S*", 'g')) || []).join(' ')
        //     });
        // return this;
        // };


        // MAIN
        function onOffDebug(){
            if (isDebug){
                // updateErrorMarker();
                findAlla();
                FormSelectBebug();
                formInputType();
                findPrice();
                findCurrency();
                findImgLink();
                findDivLink();
                findSpanWarning();
                findSpanPercent();
                findSriptsDate();
                findImgDouble();
                findDiscount();
                findCity();
                loadBackAnalize();
                showInputTypes();
            }
            else{
                removeAllDebug()
            }

        }
        $(document).ready(function(){
            // Если заргужены данные с бэка KMA
            if (typeof(country_list)=='object'){
                getDiscount();
                getPricesAdmin();
                getPhoneCode();
            }
        })
        

        // Получить обьект сообщения о ошибке
        function getMsg(){
            let msg = $('<span></span>')
            msg.addClass(debugMsgClass)
            return msg
        }

        // Удаление всех классов и элементов debug
        function removeAllDebug(){
            RemoveIoPlaceholder();
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
            removeDebugMsg()
        }

        // удаление сообщений о ошибках с лэндинга
        function removeDebugMsg(){
            let msgs = $('.' + debugMsgClass)
            console.log(msgs.length, 'msgs')
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
            // console.log(formsNoSelect.length, 'xxxxx')
            formsNoSelect.each(function(){
                let msg = getMsg()
                msg.text('Нет селекта страны!!!')
                $(this).append(msg)
                // plusError()
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
            console.log(inputsNoTel)
            inputsNoTel.addClass(fromInputNotelClass)
            // if (inputsNoTel.length != 0){plusError();}
        }

        // Выборка всех ссылок
        function findAlla(){
            let links = $('a')
            links.addClass(debugClass)
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
      

        // Поиск меток с бэка Даты
        function findSpanWarning(){
            let elems = $('span.__back-date')
            elems.addClass(debugClass)
        }
        // Удалить
        function findSpanPercent(){
            let elems = $('span.__back-percent')
            elems.addClass(debugClass)
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

        // УДалить!
        // function plusError(){
        //     errorCount ++
        //     updateErrorMarker()
        // }
        // УДалить!
        // Обновить кол-во ошибок в тулбаре
        // function updateErrorMarker(){
        //     let marker = $('#oi-toolbar .error-counter .marker')
        //     let markerInfo = $('#oi-toolbar .error-counter .info')
        //     if (errorCount == 0){
        //         marker.css('background-color', 'green')

        //     } else {
        //         marker.css('background-color', 'red')
        //     }
        //     markerInfo.text(errorCount)
        // }



        // закрытие тулбара при скроле
        // $(window).scroll(function (event) {
        //     var scroll = $(window).scrollTop();
        //     let toolbar = $('#oi-toolbar #back-info')
        //     console.log(toolbar.css('display'))
        // });

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
        


        // Получить Маску телефона страны API
        function getPhoneCode(){
            url = currentUrl+ '/kma/get_phone_code/'
            data = {'country_code': country}
                $.get(url, data, function(response){
                    console.log(response)
                    if (response['success'] == true){
                        $('#oi-phone-code').text('+'+response['phone_code'])
                        PhoneMask = '+'+response['phone_code'];
                    }
                    else{$('#oi-phone-code').text(response['message'])}
                })
        }

        // typeof(country_list)=='object'
  
        // Получить скитку из обьекта js
        function getDiscount(){
            if (typeof(country_list)=='object'){
                let discount = country_list[country].discount
                $('#oi-admin-discount').text(discount+'%')
            } else {
                $('#oi-admin-discount').text('Ошибка')
            }
        }
        

        // Получить цены из обьекта js
        function getPricesAdmin(){
            s1 = country_list[country].s1
            s2 = country_list[country].s2
            s3 = country_list[country].s3
            s4 = country_list[country].s4
            curr = country_list[country].curr
            let price_text = `${s1}(${s4}) ${curr}`
            if (s2 != 0) {price_text+= `<br>Доставка: <span>(${s2})</span>`}
            $('#oi-admin-price').html(price_text)
        }

        // getRekvAdmin()
        // Получить реквизиты из обьекта js
        // function getRekvAdmin(){
        //     if ($('rekv,js-agreement-rekv').length ==0){
        //         $('#oi-rekv').text('Тэг не найден')  
        //     } else {
        //         $('#oi-rekv').text('Стоят')  
        //     }
            
        // }

        // Добавить офферы в тулбар
        function addOffersTool(offers){
            if (offers.length != 1){$('.oi-back-offers').addClass(toolbarErrorClass)}
            for (pos in offers){
                offer = offers[pos]
                let span = '<p>' + offer + '</p>'
                $('#oi-back-offers').after(span)
            }
            
        }
        // Добавить валюты в тулбар
        function addCurrTool(currs){
            if (currs.length != 1){$('.oi-back-currs').addClass(toolbarErrorClass)}
            for (pos in currs){
                curr = currs[pos]
                let span = '<p>' + curr + '</p>'
                $('#oi-back-currs').after(span)
            }
        }
        // Добавить маски в тулбар
        function addPhoneMaksTool(phone_codes){
            for (pos in phone_codes){
                let code = phone_codes[pos]
                let span = '<p>' + code + '</p>'
                $('#oi-back-phones').after(span)
                if (code != PhoneMask) {$('.oi-back-phones').addClass(toolbarErrorClass)}
            }
        }
        // Добавить даты в тулбар
        function addDatesTool(dates){
            let keys = ['oi-dates_correct', 'oi-dates_incorrect', 'oi-years', 'oi-years_old']
            for (pos in keys){
                let id = keys[pos]
                // console.log(id, typeof(id),id=='io-dates_correct', 'io-dates_correct')
                for (pos in dates[id]){
                        let date = dates[id][pos]
                        let span = '<p>' + date + '</p>'
                        $('#'+id).after(span)
                    }

            }
            // for (pos in dates){
            //     let date = dates[pos]
            //     let span = '<p>' + date + '</p>'
            //     $('#oi-back-dates').after(span)
            // }
        }
        // Добавить слова/падежы гео в туллбар 
        function addGeoWordsTool(geo_words){
            for (geo in geo_words){
                let words = geo_words[geo]
                if (geo != country){$('#oi-geo-words').addClass(toolbarErrorClass)}
                let span = '<p>' + geo + '</p>'
                $('#oi-geo-words').after(span)
                for (pos in words){
                    let word = words[pos]
                    let span = '<p>' + word + '</p>'
                    $('#oi-geo-words-words').after(span)
                }
            }
        }

        // Загрузда данных анализа текста API
        function loadBackAnalize(){
            let url = currentUrl + '/checker/analiz_land_text/'
            let page_title = $('title').clone()
            let send_text = $('body').clone()
            send_text.find('#oi-toolbar').remove()
            send_text.find('#test-block').remove()
            send_text.find('#polit').remove()
            send_text.find('#agreement').remove()


            send_text = send_text.html()
            send_text += page_title.html()
            
            data = {'land_text': send_text}
            $.post(url, data, function(response){
                console.log(response)
                if (response['success']){
                    offers = response.result['offers']
                    currs = response.result['currencys']
                    dates = response.result['dates_on_land']
                    phone_codes = response.result['phone_codes']
                    //geo_words = response.result['geo_words']
                    geo_words = response.result['geo_words_templates']

                    addOffersTool(offers)
                    addCurrTool(currs)
                    addPhoneMaksTool(phone_codes)
                    addDatesTool(dates)
                    addGeoWordsTool(geo_words)

                } else {
                    console.log('Ошибка загрузки анализатора')
                }
                
            })
        }
        $('#test-click').click(function(){
            loadBackAnalize()
            })

        // открытие оригинальной ссылки
        $('#oi-toolbar .original-link p').click(function(){
            let url = $(this).attr('data-href')
            console.log(url)
            window.open(url, '_blank').focus();
            })

        // показать\скрыть тулбар
        $('#oi-toolbar .oi-header').click(function(){
            $('#oi-toolbar .__oi_close').toggle(toggleTime)
            $('#oi-toolbar').toggleClass('__close')
            // $('#oi-toolbar #back-info').toggle(300)
            })

        // Скролл по дублям картинок
        $('#back-info img').click(function(){
            $('img.__focus_img').removeClass('__focus_img')
            let src = $(this).attr('src')
            // console.log(src, 'src дубля')
            if (src != lastDoubleScr){imgBoubleCounter = 0}
            lastDoubleScr = src
            let imgs = $('img.'+doubleImgStyle).filter(function(){
                if ($(this).attr('src') == src){return true}
            })
            // console.log(imgs, 'Найденые дубли')
            imgBoubleLen = imgs.length
            console.log(imgBoubleCounter, imgBoubleLen)
            imgs.get(imgBoubleCounter).scrollIntoView({block: "center", behavior: "smooth"});
            $(imgs.get(imgBoubleCounter)).addClass('__focus_img') // xxx
            imgBoubleCounter ++
            if (imgBoubleCounter  >= imgBoubleLen) {imgBoubleCounter=0; console.log('Сброс счетчика')}
            })

        // $('*').click( function(){
        //     if ($(this).children().length == 1){
        //         console.log($(this))
        //     }
        // })

        var entityMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '/': '&#x2F;',
            '`': '&#x60;',
            '=': '&#x3D;'
          };
          
          function escapeHtml (string) {
            return String(string).replace(/[&<>"'`=\/]/g, function (s) {
              return entityMap[s];
            });
          }

        var body = document.querySelector('body');
        body.onclick = function(event) {
            if (event.ctrlKey){
                console.log('click')
                $('#oi-message-result').removeClass('__true')
                let dateWindow = $('#oi-message-text')
                let elem = $(event.target)
                elemHtml = elem.parent().html()
                let parentHtml = elem.parent().parent().html()
                new_text = escapeHtml(elemHtml)

                new_text = new_text.replaceAll('↓', '<br>')
                new_text = new_text.replaceAll('__back-date', '') 
                new_text = new_text.replaceAll('__debug_script_date', '') 
                new_text = new_text.replaceAll('date', '<span>date</span>')
                if (new_text.length > 600) {new_text='Слишком много букв'}
                dateWindow.html(new_text)
                console.log(new_text.length)
                if (new_text.includes('date')|| new_text.includes('year')) {
                    $('#oi-message-result').text('Скрипт')
                    $('#oi-message-result').addClass('__true')
                } else {
                    $('#oi-message-result').text('Нет скрипта')
                }
                $('#oi-date-pop-wrapper').fadeIn(300).delay(2000).fadeOut(700);
                // console.log(elemHtml)
            }
            };
        // Включение тулбара клавишами
        $(document).keyup(function(e) {
            // i = 73 p = 80 q = 81 y = 17 b = 66
            let oiToolbar = $('#oi-toolbar')
            if (e.ctrlKey && e.keyCode == 66) {
                console.log('INTEGRATION')
                if (isDebug){isDebug = false}else{isDebug = true}
                oiToolbar.toggle(500)
                onOffDebug()
            }
    });
// })