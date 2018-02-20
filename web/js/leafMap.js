
// show a map in leafMap div
var mymap = L.map('leafMap').setView([43.656399, -79.380795], 14);

var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a>'

var stamenTileUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png'
var stamenTileAttrib = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>';

var geoDataSourceURL = 'https://www.petesstuff.ml/geojsonData'
L.tileLayer(stamenTileUrl,{
    attribution: stamenTileAttrib,
    minZoom: 0,
    maxZoom: 20
    }).addTo(mymap)

// L.tileLayer(osmUrl,{
//     attribution: osmAttrib,
//     minZoom: 0,
//     maxZoom: 20
//     }).addTo(mymap)

var markerGroup;

var msMin = 1000*60;
var msHour = msMin*60;
var msDay = msHour*24;

// 20s
var updateInterval = 20000;
var timenow = new Date()


// var oldstr = '2017-12-11 19:26:14.901590Z'
// var oldstrdate = new Date(oldstr)
// console.log('time now: '+timenow)
// console.log('old time: '+oldstrdate)

// var thisdiff = getTimeDiff(oldstr)
// var diffDaysd = Math.floor(thisdiff/msDay);
// var diffHoursd = Math.floor((thisdiff%msDay)/msHour);
// var diffMinsd = Math.floor(((thisdiff%msDay)%msHour)/msMin);
// console.log('difference of '+diffDaysd+' days, '+diffHoursd+' hours, and '+diffMinsd+' minutes')
// console.log('thisdiff = '+thisdiff)
// var thisScale = thisdiff/msDay
// thisScale = Math.min(0.0,thisScale)
// thisScale = Math.max(1.0,thisScale)
// console.log('scale = '+(thisdiff%msDay)/msDay)

function getTimeDiff(datestr)
{
    // get the time difference (in ms) between now and the time provided
    var tweetTime = new Date(datestr)
    var diff = timenow.getTime() - tweetTime.getTime();

    return diff    
}


function popupFeature(feature, layer) 
{
    // add a popup to each feature (tweet)
    // check that required properties are present
    if (feature.properties && feature.properties.tweet_id_str && feature.properties.datetime_utc) 
    {
        // compute time since tweet
        var timediffms = getTimeDiff(feature.properties.datetime_utc +'Z')
        var hours = Math.floor(timediffms/msHour)
        timediffms -= hours*msHour
        var mins = Math.floor(timediffms/msMin)

        // compose the popup html
        var tweetedAgo = '<a href="https://twitter.com/statuses/'+feature.properties.tweet_id_str+'">Tweeted</a> ';
        if (hours >=1.0) tweetedAgo += hours + ' hours and ';
        tweetedAgo += mins + ' minutes ago';

        // bind the popup to the feature
        layer.bindPopup(tweetedAgo);
    }
}

function styleFeature(feature)
{
    // apply styling to each feature (circlemarker)
    var timediffms = getTimeDiff(feature.properties.datetime_utc +'Z')
    var diffDays = Math.floor(timediffms/msDay);
    var diffHours = Math.floor((timediffms%msDay)/msHour);
    var diffMins = Math.floor(((timediffms%msDay)%msHour)/msMin);
    
    // get a value between 0 and 1, based on fraction of a day since tweet
    // things older than 24 hours should not show up in the geojson response
    // 0  is very recent, 1 is 24 hours ago
    var diffScale = timediffms/msDay
    // console.log('diffScale = '+diffScale)
    diffScale = Math.max(0,diffScale)
    diffScale = Math.min(1.0,diffScale)
    // compute color based on scale. 
    // use hsl, h=0 is red, h=240 is blue
    var h_color = diffScale*240

    // marker opacity, fully opaque for recent tweets, transparent for older
    var opac = 1.0 - 0.8*diffScale

    return {
        color: 'hsl('+h_color+',100%,50%)',
        fillOpacity: opac
        };

}

function getdataFinish(geojsondata,success, returnCode)
{
    // callback from geojson request
    timenow = new Date()
    console.log('sucess: '+success+', returncode: '+returnCode)

    //remove any existing markers
    if (markerGroup) {markerGroup.remove();}
    
    // add markers based on geojson data
    // use styling and popup functions defined above
    markerGroup = L.geoJson(geojsondata,
    {
        style: styleFeature,
        onEachFeature: popupFeature,
        pointToLayer: function (feature, latlng) {return L.circleMarker(latlng,{radius: 5, stroke:false});}
    }).addTo(mymap)
}

// get initial marker data
console.log('getting initial marker data')
$.ajax(
    {
      dataType: "jsonp",
      url: geoDataSourceURL,
      success:getdataFinish
    });

// update marker data every few seconds
var inter = setInterval(
    function()
    {
        console.log('automatic update, sending request')
        $.ajax(
        {
          dataType: "jsonp",
          url: geoDataSourceURL,
          success:getdataFinish
        });
    }, updateInterval);
