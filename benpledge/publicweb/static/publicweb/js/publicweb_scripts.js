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
    // $('#house_map').mapster({
    //     fillColor: 'ff0000',
    //     fillOpacity: 0.5
    // });
    google.maps.event.addDomListener(window, 'load', initialize);

});

var updateDurationText = function() {
    var slider_value = pledgeSlider.getValue();
    $("#duration-text").html(slider_value + ' months');
};
var pledgeSlider = $('#pledge-slider').slider({
        formater: function(value) {
            return value + ' months';
        }
    })
    .on('slide', updateDurationText)
    .data('slider');

function updatePledgeForm(item) {
    var x = $("#123-interest-only");
    console.log(x.is(':checked'));
    if ($("#123-interest-only").is(':checked')) {
        $("#pledge-form-elements").slideUp();
    }
    else {
        $("#pledge-form-elements").slideDown();
    }
}


var geocoder;
var map;
function initialize() {
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(51.4500388, -2.5588662);
    var mapOptions = {
        center: latlng,
        zoom: 13
    };
    map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);
    // mapPledges();
}


/**
This code doesn't work yet - too many requests.
Should store latlng.
*/
function plotStreet(address_components) {
    address = (address_components[1].long_name + ", " + 
        address_components[2].long_name + ", Bristol, UK");
    // console.log(address_components);
    console.log(address);
    geocoder.geocode( {'address':address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
        var latlng = results[0].geometry.location;
        marker = new google.maps.Marker({
            position: latlng,
            map: map
        });
    } else {
        console.log('plotStreet Geocode was not successful for the following reason: ' + status);
    }
    });
}

function codeLatLng(latlng) {
    geocoder.geocode({'latLng': latlng}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
        if (results[0]) {
            // code below
            plotStreet(results[0].address_components);
        } else {
            console.log('No results found');
            }
    } else {
        console.log('codeLatlng Geocoder failed due to: ' + status);
    }
    });
}

function codePostcode(address) {
    address += ", UK"
    var latlng = null;
    geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            codeLatLng(results[0].geometry.location);
        } else {
            console.log('codePostcode Geocode was not successful for the following reason: ' + status);
        }
    });
}

function mapPledges() {
    var pledgeData = getPledgeData();
    for (var pledge in pledgeData) {
        codePostcode(pledgeData[pledge].postcode);
    }
}


// map.setZoom(11);
//         marker = new google.maps.Marker({
//             position: latlng,
//             map: map
//         });
//         infowindow.setContent(results[1].formatted_address);
//         infowindow.open(map, marker);

// $('area').each(function() {
//     $(this).qtip({
//         content: {
//             text: $(this).title
//         },
//         position: {
//             target : 'mouse',
//             adjust: {
//                 // Use initial position rather than continually following the mouse
//                 //mouse: false
//             }
//         },
//         // style: {
//         //     tip: {
//         //         corner: 'left bottom'
//         //     }
//         // }
//     });
// });