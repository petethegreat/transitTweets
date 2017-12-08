
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



