/**
These are all the functions and variables that relate to the area chart on the admin dashboard
**/

var chartsvg = d3.select("#lgraph");
var x = d3.scaleTime().rangeRound([40, chartsvg.attr("width") * 3]);
var y = d3.scaleLinear().range([$("#lgraph").height() - 20, 20]);

//Function that defines the positions of each point on the area chart
var valueline = d3.area()
    .x(function (d) {
        return x(parseTime(d.date));
    })
    .y0(y(0))
    .y1(function (d) {
        return y(Number(d[plotType]));
    });
var plotpath;

//Colours for the area/points of each metric type
var fillcolour = {
    "listings": ["purple", "yellow"],
    "commoners": ["steelblue", "darkblue"],
    "stories": ["red", "darkgreen"],
    "tags": ["green", "yellow"],
    "convo": ["orange", "darkblue"],
    "trans": ["darkblue", "steelblue"],
    "create": ["darkred", "orange"],
    "comment": ["red", "green"]
};

//Text for the axis of each metric type
var axistext = {
    "listings": "Active listings",
    "commoners": "Active Commoners",
    "stories": "Active stories",
    "tags": "Tags used",
    "convo": "Conversations started",
    "trans": "Transactions made",
    "create": "Stories written",
    "comment": "Story comments"
};

/**
* This is needed to translate ticks to the right place
*/
function getTranslation(transform) {
    var t = document.createElementNS("http://www.w3.org/2000/svg", "g");
    t.setAttributeNS(null, "transform", transform);
    var matrix = t.transform.baseVal.consolidate().matrix;
    return [matrix.e, matrix.f];
}

$("#lgraph").bind("wheel mousewheel", function (e) {
    e.preventDefault();
});
chartg = chartsvg.append("g");

var areazoom = d3.zoom()
    .scaleExtent([0.33, 2])
    .translateExtent([[0, 0],
     [chartsvg.attr("width") * 3 + 50, chartsvg.attr("height")]])
    .on("zoom", areazoomed);
chartsvg.call(areazoom);
    
var currentMonthGap = 1;

/**
* Draws the area chart after loading all necessary data
* Defaults to show number of stories written over time
*/
function drawAreaChart(){
    // Scale the range of the data
    x.domain(d3.extent(datalist, function (d) {
        return parseTime(d.date);
    }));
    y.domain([0, d3.max(datalist, function (d) {
        return (
            Number.isNaN(Number(d.stories)) ? 0 : +d.stories);
    })]);

    var anotherFormat = d3.timeFormat("%b'%y");
    xAxis = d3.axisBottom(x)
           .tickFormat(anotherFormat)
           .ticks(d3.timeMonth.every(1));
    // Add the X Axis
    gX = chartg.append("g")
        .attr("id", "simplelineaxis")
        .attr("transform", "translate(0," +
         ($("#lgraph").height() - 20) + ")")
        .call(xAxis);
    // Add the Y Axis
    gY = chartg.append("g")
        .attr("class", "yline")
        .attr("transform", "translate(40,0)")
        .call(d3.axisLeft(y));

    chartsvg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0)
    .attr("x", 0 - ($("#lgraph").height() / 2))
    .attr("dy", "1em")
    .attr("id", "ylabel")
    .style("text-anchor", "middle")
    .style("font-family", "Calibri")
    .style("font-weight", "bold")
    .text("");
}

/**
* Redraws the area chart to show a different attribute plotted over time
* @param {string} type - string representing type of attribute to plot (e.g., 'listings','commoners','stories' etc.)
*/
function drawNewChart(type) {
    if (type == ""){
        return;
    }
    plotType = type;
    chartg.select(".yline").remove();
    chartg.select(".plotline").remove();
    chartg.selectAll(".dots").remove();

    $("#ylabel").text(axistext[type]);
    y.domain([0, d3.max(datalist, function (d) {
        return (
            Number.isNaN(Number(d[plotType])) ? 0 : +d[plotType]);
    })]);
    // Add the valueline path.
    plotpath = chartg.append("path")
        .data([datalist])
        .attr("fill", fillcolour[plotType][0])
        .attr("opacity", 0.5)
        .attr("stroke-width", 1.5)
        .attr("class", "plotline")
        .attr("d", valueline);
    chartg.append("g")
    .attr("class", "yline")
    .attr("transform", "translate(40,0)")
    .call(d3.axisLeft(y));
    dots = chartg.selectAll(".dots")
        .data(datalist)
        .enter().append("circle")
        .attr("class", "dots")
        .style("fill", function (d) {
            if (d.date == currentDate){
                return fillcolour[plotType][1];
            }
            return fillcolour[plotType][0];
        })
        .attr("r", function (d) {
            if (d.date == currentDate){
                return 6;
            }
            return 4;
        })
        .attr("cx", valueline.x())
        .attr("cy", function (d) {
            return y(+d[plotType]);
        })
        //Show/hide tooltips
        .on("mouseover", function (d) {
            d3.select(this).attr("r", 8);
            d3.select(this).style("cursor", "pointer");
            div.transition()
            .duration(200)
            .style("opacity", 0.9);
            div.html(d.date + "</br>" + d[plotType])
            .style("left", (d3.event.pageX - 38) + "px")
            .style("top", (d3.event.pageY - 50) + "px")
            .style("background", "transparent");

        })
        .on("mouseout", function (d) {
            d3.select(this).attr("r", 4);
            div.transition()
            .duration(500)
            .style("opacity", 0);
        });
}

/**
* Zooming and panning function for the area chart. Recalculates tick
* numbers and positions, and position of filled area itself
*/
function areazoomed() {
    var xz = d3.event.transform.rescaleX(x);
    gX.call(xAxis.scale(xz));
    
    //Recalculate tick numbers so they don't get 
    //too far apart or too close together
    var t= $("#simplelineaxis > .tick");
    if(t.length == 0){
        return;
    }
    var tickdistance = t.eq(1).position().left - t.eq(0).position().left;
    if (tickdistance < 50){
        currentMonthGap += 1;
    }
    else if (tickdistance > 100){
        currentMonthGap -= 1;
    }
    xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
    d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
        return "translate(" +
        (getTranslation(d3.select(this).attr("transform"))[0]) +
        ",0)";
    });
    d3.selectAll(".dots").attr("cx", function (d) {
        return xz(parseTime(d.date));
    });
    valueline.x(function (d) {
        return xz(parseTime(d.date));
    });
    if (plotpath == undefined){
        return;
    }
    plotpath.attr("d", valueline);

}