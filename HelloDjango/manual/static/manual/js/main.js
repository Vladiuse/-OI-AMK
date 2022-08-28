//Скрипт для карточек описания новостей
function cardShowLang(card,lang){
    card.find('p').hide()
    card.find('p.'+lang).show()
    card.find('.card-body img').hide()
    card.find('.card-body img.'+lang).show()
}
$('#manual').on('click','.news_desc a.nav-link',function(e){
    e.preventDefault()
    let lang = $(this).attr('data-lang')
    let card = $(this).closest('.card')
    card.find('a').removeClass('active')
    $(this).addClass('active')
    cardShowLang(card,lang)
})
$('#manual').on('click','.news_desc a',function(e){
    e.preventDefault()})

console.log('LOAD MANUAL RU/ENG window')

//Скрипт для карточек описания новостей
// function cardShowLang(card,lang){
//     card.find('p').hide()
//     card.find('p.'+lang).show()
//     card.find('.card-body img').hide()
//     card.find('.card-body img.'+lang).show()
// }
// $('.news_desc a.nav-link').click(function(e){
//     e.preventDefault()
//     let lang = $(this).attr('data-lang')
//     let card = $(this).closest('.card')
//     card.find('a').removeClass('active')
//     $(this).addClass('active')
//     cardShowLang(card,lang)
// })
// $('.news_desc a').click(function(e){
//     e.preventDefault()})

// console.log('LOAD MANUAL RU/ENG window')

