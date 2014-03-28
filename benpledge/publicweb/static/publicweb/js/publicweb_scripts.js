/*
* rwdImageMaps jQuery plugin v1.5
*
* Allows image maps to be used in a responsive design by recalculating the area coordinates to match the actual image size on load and window.resize
*
* Copyright (c) 2013 Matt Stow
* https://github.com/stowball/jQuery-rwdImageMaps
* http://mattstow.com
* Licensed under the MIT license
*/
;(function(a){a.fn.rwdImageMaps=function(){var c=this;var b=function(){c.each(function(){if(typeof(a(this).attr("usemap"))=="undefined"){return}var e=this,d=a(e);a("<img />").load(function(){var g="width",m="height",n=d.attr(g),j=d.attr(m);if(!n||!j){var o=new Image();o.src=d.attr("src");if(!n){n=o.width}if(!j){j=o.height}}var f=d.width()/100,k=d.height()/100,i=d.attr("usemap").replace("#",""),l="coords";a('map[name="'+i+'"]').find("area").each(function(){var r=a(this);if(!r.data(l)){r.data(l,r.attr(l))}var q=r.data(l).split(","),p=new Array(q.length);for(var h=0;h<p.length;++h){if(h%2===0){p[h]=parseInt(((q[h]/n)*100)*f)}else{p[h]=parseInt(((q[h]/j)*100)*k)}}r.attr(l,p.toString())})}).attr("src",d.attr("src"))})};a(window).resize(b).trigger("resize");return this}})(jQuery);

$(document).ready(function(e) {
    $("#sortable-measures-table").tablesorter(); 
    $('img[usemap]').rwdImageMaps();
    $('area').each(function() {
        $(this).qtip({
            content: {
                text: $(this).title
            },
            position: {
                target : 'mouse',
                adjust: {
                    // Use initial position rather than continually following the mouse
                    //mouse: false
                }
            },
            // style: {
            //     tip: {
            //         corner: 'left bottom'
            //     }
            // }
        });
    });
});

// var pledgeSlider = $('#pledge-slider').slider({
//         formater: function(value) {
//             return value + ' months';
//         }
//     })
//     .on('slide', updateDurationText)
//     .data('slider');
var updateDurationText = function() {
    var slider_value = pledgeSlider.getValue();
    $("#duration-text").html(slider_value + ' months');
};
console.log("no non nonononono");
var pledgeSlider = $('#pledge-slider').slider({
        formater: function(value) {
            return value + ' months';
        }
    })
    .on('slide', updateDurationText)
    .data('slider');


    //.on('slide', update_duration_text);