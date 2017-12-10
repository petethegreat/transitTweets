
// show a map in leafMap div
var mymap = L.map('leafMap').setView([43.656399, -79.380795], 14);

var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a>'

var stamenTileUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png'
var stamenTileAttrib = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>';


L.tileLayer(stamenTileUrl,{
    attribution: stamenTileAttrib,
    minZoom: 0,
    maxZoom: 20
    }).addTo(mymap)

var markerGroup;


var updateInterval = 5000;

function getdataFinish(geojsondata,success, returnCode)
{
    console.log('sucess: '+success+', returncode: '+returnCode)

    if (markerGroup) {markerGroup.remove();}
    
    markerGroup = L.geoJson(geojsondata,
    {
        style: function(feature){ return {color: '#00ff00'};},
        pointToLayer: function (feature, latlng) {return L.circleMarker(latlng,{radius: 10, stroke:false, fillOpacity:1.0});}
    }).addTo(mymap)
}

console.log('getting initial marker data')
$.ajax(
    {
      dataType: "jsonp",
      url: 'http://127.0.0.1:5000/geojsonData',
      success:getdataFinish
    });

var inter = setInterval(
    function()
    {
        console.log('automatic update, sending request')
        $.ajax(
        {
          dataType: "jsonp",
          url: 'http://127.0.0.1:5000/geojsonData',
          success:getdataFinish
        });

    }, updateInterval);







// add a layergroup
// for each item/feature in the json, create a marker
// add the marker to the layergroup

// on update, clear the layergroup, and refill it
// maybe look at geoJson. 

