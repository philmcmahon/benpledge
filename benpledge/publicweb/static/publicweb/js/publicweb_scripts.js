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


/* Publicweb Scripts */

// when slider moved, update text next to form element
var updateDurationText = function() {
    var slider_value = pledgeSlider.getValue();
    $("#duration-text").html(slider_value + ' months');
};

// setup slider form element on plege form
var pledgeSlider = $('#pledge-slider').slider({
        formater: function(value) {
            return value + ' months';
        }
    })
    .on('slide', updateDurationText)
    .data('slider');

// hides pledge form elements when 'interest only' checked
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
    var mapInitial = getMapInitial();
    // initialise map with default location and zoom
    var latlng = new google.maps.LatLng(mapInitial.latitude, mapInitial.longitude);
    var mapOptions = {
        center: latlng,
        zoom: mapInitial.zoom
    };
    map = new google.maps.Map(document.getElementById("map-canvas"),
        mapOptions);
    mapPledges();
}

// content for marker info window
function generateInfoWindowContent(title, dateMade, deadline, timeRemaining, savings, panelType) {
    console.log(panelType)
    var panelContent= '<div id="content">' +
        '<div id="siteNotice">' +
        '</div>' +
        '<div class="panel ' + panelType +'">' +
        '<div class="panel-heading">' +
        '<h3 class="panel-title">' + title + ' </h3>' +
        '</div>' +
        '<div class="panel-body">' +
        '<table class="table table-bordered">' +
        '<tr>' +
        '<th>Date Made<br></th>' +
        '<td>' + dateMade + '</td>' +
        '</tr>' +
        '<tr>' +
        '<th>Deadline</th>' +
        '<td>' + deadline + '</td>' +
        '</tr>' +
        '<tr>' +
        '<th>Time Remaining</th>' +
        '<td>' + timeRemaining + '</td>' +
        '</tr>' +
        '</table>' +
        '</div>' +
        '<div class="panel-footer">' +
        'Energy reduction: ' + savings + ' kWh' +
        '</div>' +
        '</div>' +
        '</div>';
    return panelContent
}



var infoWindow;
var marker, i;
var oms;


function mapPledges() {
    // setup oms
    infoWindow = new google.maps.InfoWindow();
    oms = new OverlappingMarkerSpiderfier(map, {keepSpiderfied: true});
    // when 'spiderfied' (collapsed) marker clicked
    // close the info window
    oms.addListener('spiderfy', function(markers) {
      infoWindow.close();
    });
    // when marker clicked, open info window 
    oms.addListener('click', function(marker, event) {
        infoWindow.setContent(marker.desc);
        infoWindow.open(map, marker);
    });

    // get pledge data from template
    var pledgeData = getPledgeData();
    var image = getIconLocation();

    var latlng, title, pledge, location;
    i = 0;
    // loop through pledges, plot on map
    for (var p in pledgeData) {
        location = pledgeData[p].position;
        pledge = pledgeData[p].pledge;
        // create LatLng object
        latlng = new google.maps.LatLng(location.lat, location.lng);
        // set colour of info window, marker title
        if (pledge['complete'] == "True") {
            title = pledge.measure + " pledged and completed by " + pledge.user;  
            panelType = "panel-success"; 
        } else {
            title = pledge.measure + " pledged by " + pledge.user;  
            panelType = "panel-primary";
        }
        
        // create marker object
        marker = new google.maps.Marker({
            position: latlng,
            map: map,
            icon: image,
            title: title,
        });
        // pass pledge details to generateInfoWindowContent
        marker.desc = generateInfoWindowContent(title,
                pledge.date_made, pledge.deadline, pledge.time_remaining, pledge.savings, panelType);
        // add the marker to the map
        oms.addMarker(marker);
        i++;
    }
}

$(document).ready(function(e) {
    // setup sortable tables
    $("#sortable-measures-table").tablesorter();
    $("#sortable-pledges-table").tablesorter();
    $("#sortable-users-table").tablesorter();
    // for image map on general_measures
    $('img[usemap]').rwdImageMaps();
    // for edit_pledge form
    $("#id_deadline").datepicker();
    // when page has loaded, initialise the map
    google.maps.event.addDomListener(window, 'load', initialize);
});


