$( "a" ).click(function( event ) {
    event.preventDefault();})

var body = document.querySelector('body');
        body.onclick = function(event) {
            console.log(event.target.tagName)
            let elem = $(event.target)
        }