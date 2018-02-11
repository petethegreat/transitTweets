
// Draw plot circles according to lat/long from tweet objects

data = {
        "datetime_utc": "2017-12-02 19:25:43.385302", 
        "geo_latt": 43.663882691173065, 
        "geo_long": -79.35721220008752, 
        "id": 1
    }


console.log('doin stuff')
$.ajax(
{
  dataType: "jsonp",
  url: 'http://127.0.0.1:5000/geoData',
  success:getDataFinish
});
// this is asynchronous


// define height and width
var margin = {
    left:50,
    top:10,
    bottom:25,
    right:10
}

var totalWidth = 600;
var totalHeight = 600;
var width = totalWidth - margin.left - margin.right;
var height = totalHeight - margin.top - margin.bottom;

var updateInterval = 5000;

// define scale ranges (domains based off data)
var x = d3.scaleLinear().range([0,width]);
var y = d3.scaleLinear().range([height,0]);

var xAxis = d3.axisBottom().ticks(5)
var yAxis = d3.axisLeft().ticks(5)

// create an svg container for stuff
var svg = d3.select('#geoCircles')
    .append("svg:svg")
        .attr("width",totalWidth)
        .attr("height",totalHeight)
        .attr('style','background-color: #ffffff;')
    .append('g')
        .attr('transform','translate('+margin.left +',' + margin.top + ')');


function getDataFinish(pulledData,success, returnCode)
{
    data = pulledData
    console.log('getting json data: '+success)

    x.domain(d3.extent(data,function(d){return d.geo_long}));
    y.domain(d3.extent(data,function(d){return d.geo_latt}));

    // could also create a time - colour scale, and set marker fill colour based on age
    
    // add some markers based on data
    svg.selectAll('circle').data(data).enter().append('circle')
        .attr("cx",function(d){return x(d.geo_long)})
        .attr("cy",function(d){return y(d.geo_latt)})
        .attr("r",5)
        .attr('fill','red');

    xAxis.scale(x)
    yAxis.scale(y)



     // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
}

function updateFinish(pulledData,success, returnCode)
{
    data = pulledData
    console.log('updating elements: '+success)

    // select exisiting circles
    var selection = svg.selectAll('circle').data(data)

    // update existing ( colour might change)
    selection.attr("cx",function(d){return x(d.geo_long)})
        .attr("cy",function(d){return y(d.geo_latt)})
        .attr("r",5)
        .attr('fill','red');

    // add circles for any new datapoints
    selection.enter().append('circle')
        .attr("cx",function(d){return x(d.geo_long)})
        .attr("cy",function(d){return y(d.geo_latt)})
        .attr("r",5)
        .attr('fill','red');

    // delete any that are no longer relevant (> 24 hrs)
    selection.exit().remove()

    // rescale axes (update domain)
    x.domain(d3.extent(data,function(d){return d.geo_long}));
    y.domain(d3.extent(data,function(d){return d.geo_latt}));

    // make a transition
    // var svg = d3.select('#geoCircles').transition();
    var trans = svg.transition()

    // Make the changes
    // svg.select(".line")   // change the line
    //     .duration(750)
    //     .attr("d", valueline(data));
    trans.select(".x.axis") // change the x axis
        .duration(750)
        .call(xAxis);
    trans.select(".y.axis") // change the y axis
        .duration(750)
        .call(yAxis);

    svg.selectAll('circle').data(data).transition().duration(750)
        .attr("cx",function(d){return x(d.geo_long)})
        .attr("cy",function(d){return y(d.geo_latt)})

}

// update things every few seconds
var inter = setInterval(
    function()
    {
        console.log('automatic update, sending request')
        $.ajax(
        {
          dataType: "jsonp",
          url: 'http://127.0.0.1:5000/geoData',
          success:updateFinish
        });

    }, updateInterval);

