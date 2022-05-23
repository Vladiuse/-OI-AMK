// $(document).ready(function(){

        let toogleTime = 300;
        let isDebug = false;
        let errorCount = 0;
        let debugClass = '__debug';
        let debugMsgClass = '__debug_msg';
        let formNoSelectClass = '__debug_no_select';
        let fromInputNotelClass = '__debug_no_tel';
        let debugScritpDate = '__debug_script_date'
        let doubleImgStyle = '__debug_double'
        let lastDoubleScr = ''

        let imgBoubleCounter = 0;
        let imgBoubleLen = 0;

        $.fn.removeClassStartingWith = function (filter) {
        $(this).removeClass(function (index, className) {
            return (className.match(new RegExp("\\S*" + filter + "\\S*", 'g')) || []).join(' ')
            });
        return this;
        };


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
                findSpanWarning();
                findSriptsDate();
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
            console.log(msg, 'getMsg')
            return msg
        }

        // Удаление всех классов и элементов debug
        function removeAllDebug(){
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
            console.log(formsNoSelect.length, 'xxxxx')
            formsNoSelect.each(function(){
                let msg = getMsg()
                msg.text('No select')
                $(this).append(msg)
                // plusError()
            })
        }

        // Поиск инпутов с некоректным атрибутом type
        function formInputType(){
            let inputs = $('form input[name=phone]')
            console.log(inputs)
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
            // поиск ссылок
            let links = $('a')
            links.addClass(debugClass)
        }

        // Выборка всех цен (по классу)
        function findPrice(){
            let oldPrice = $('.price_land_s4')
            let newPrice = $('.price_land_s1')
            oldPrice.addClass(debugClass)
            newPrice.addClass(debugClass)
        }

        // Выборка всех валют (по классу)
        function findCurrency(){
            let currencys = $('.price_land_curr')
            currencys.addClass(debugClass)
        }

        // Выборка картинок внутри ссылок
        function findImgLink(){
            let imgs = $('a img')
            imgs.addClass(debugClass)
            imgs.parent().removeClass(debugClass)

        }

        // Поиск меток с бэка
        function findSpanWarning(){
            let elems = $('span.__back-date')
            elems.addClass(debugClass)
        }

        // УДалить!
        function plusError(){
            errorCount ++
            updateErrorMarker()
        }

        // Обновить кол-во ошибок в тулбаре
        function updateErrorMarker(){
            let marker = $('#oi-toolbar .error-counter .marker')
            let markerInfo = $('#oi-toolbar .error-counter .info')
            if (errorCount == 0){
                marker.css('background-color', 'green')

            } else {
                marker.css('background-color', 'red')
            }
            markerInfo.text(errorCount)
        }

        // показать\скрыть тулбар
        $('#oi-toolbar .header').click(function(){
            $('#oi-toolbar .__oi_close').toggle(toogleTime)
            $('#oi-toolbar').toggleClass('__close')
            // $('#oi-toolbar #back-info').toggle(300)
        })

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

        // открытие оригинальной ссылки
        $('#oi-toolbar .original-link p').click(function(){
            let url = $(this).attr('data-href')
            console.log(url)
            window.open(url, '_blank').focus();
        })

        // Поиск и добавление рамки для дублей картинок
        function findImgDouble(){
            let imgDouble = $('img.'+doubleImgStyle)
            imgDouble.addClass(debugClass)
        }

        // Скролл по дублям картинок
        $('#back-info img').click(function(){
        // let imgBoubleCounter = 0;
        // let imgBoubleLen = 0;
            $('img.__focus_img').removeClass('__focus_img')
            let src = $(this).attr('src')
            console.log(src, 'src дубля')
            if (src != lastDoubleScr){imgBoubleCounter = 0}
            lastDoubleScr = src
            let imgs = $('img.'+doubleImgStyle).filter(function(){
                if ($(this).attr('src') == src){return true}
            })
            console.log(imgs, 'Найденые дубли')
            imgBoubleLen = imgs.length
            console.log(imgBoubleCounter, imgBoubleLen)
            imgs.get(imgBoubleCounter).scrollIntoView({block: "center", behavior: "smooth"});

            $(imgs.get(imgBoubleCounter)).addClass('__focus_img') // xxx

            imgBoubleCounter ++
            if (imgBoubleCounter  >= imgBoubleLen) {imgBoubleCounter=0; console.log('Сброс счетчика')}
        })


        // Включение тулбара клавишами
        $(document).keyup(function(e) {
            // i = 73 p = 80 q = 81 y = 17 b = 66
            let oiToolbar = $('#oi-toolbar')
            if (e.ctrlKey && e.keyCode == 66) {
                console.log('INTEGRATIONS')
                if (isDebug){isDebug = false}else{isDebug = true}
                oiToolbar.toggle(500)
                onOffDebug()
            }
    });
// })