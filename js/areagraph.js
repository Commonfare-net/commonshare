//This will be javascript innit
var fillcolour = {"listings": ["purple", "yellow"],
        "commoners": ["steelblue", "darkblue"],
        "stories": ["red", "darkgreen"],
        "tags": ["green", "yellow"],
        "convo": ["orange", "darkblue"],
        "trans": ["darkblue", "steelblue"],
        "create": ["darkred", "orange"],
        "comment": ["red", "green"]};
var axistext = {"listings": "Active listings",
        "commoners": "Active Commoners",
        "stories": "Active stories",
        "tags": "Tags used",
        "convo": "Conversations started",
        "trans": "Transactions made",
        "create": "Stories written",
        "comment": "Story comments"};
var chartsvg = d3.select("#lgraph");
$("#lgraph").bind("wheel mousewheel", function (e) {
    e.preventDefault();
});
var chartg = chartsvg.append("g");

var x = d3.scaleTime().rangeRound([40, chartsvg.attr("width") * 3]);
var y = d3.scaleLinear().range([$("#lgraph").height() - 20, 20]);
var width = chartsvg.attr("width"),
    height = chartsvg.attr("height");
var areazoom = d3.zoom()
    .scaleExtent([0.33, 2])
    .translateExtent([[0, 0],[width * 3 + 50, height]])
    .on("zoom", areazoomed);
var valueline = d3.area()
    .x(function(d) {return x(parseTime(d.date)); })
    .y0(y(0))
    .y1(function(d) {return y(+d[plotType]); });
var plotType;
function newplot(type){

    if(type == ""){return;}
        plotType = type;

    chartg.select(".yline").remove();
    chartg.select(".plotline").remove();
    chartg.selectAll(".dots").remove();
    $("#ylabel").text(axistext[type]);
    y.domain([0, d3.max(datalist, function(d) {
        return (Number.isNaN(d[plotType]) ? 0 : +d[plotType]);
    })]);
    var plotpath = chartg.append("path")
        .data([datalist])
        .attr("fill",fillcolour[plotType][0])
        .attr("opacity",0.5)
        .attr("stroke-width",1.5)
        .attr("class", "plotline")
        .attr("d", valueline);
    chartg.append("g")
        .attr("class","yline")
        .attr("transform", "translate(40,0)")
        .call(d3.axisLeft(y));
    var dots = chartg.selectAll(".dots")
        .data(datalist)
        .enter()
        .append("circle")
        .attr("class", "dots")
        .style("fill",function(d){
            if(d.date == currentDate){
                return fillcolour[plotType][1];
            }
            return fillcolour[plotType][0];
        })
        .attr("r",function(d){
            if(d.date == currentDate){
                return 6;
            }
            return 4;
        })
        .attr("cx", valueline.x())
        .attr("cy", function (d) {
            return y(+d[plotType]);
        })
        .on("mouseover", function (d,i,n) {
            d3.select(n[i]).attr("r", 8);
            d3.select(n[i]).style("cursor", "pointer");
            div.transition()
                .duration(200)
                .style("opacity", 0.9);
            div.html(d.date + "</br>" + d[plotType])
                .style("left", (d3.event.pageX -38) + "px")
                .style("top", (d3.event.pageY - 50) + "px")
                .style("background", "transparent");
        })
        .on("mouseout", function (d) {
            d3.select(n[i]).attr("r", 4);
            div.transition()
                .duration(500)
                .style("opacity",0);
        });
}

function areazoomed() {
 //   if(plotpath == undefined)return;
    var xz = d3.event.transform.rescaleX(x);
    gX.call(xAxis.scale(xz));
    //Recalculate tick numbers
    var selection = $("#simplelineaxis > .tick");
    var tickdistance = selection.eq(1).position().left
        - selection.eq(0).position().left;

    if (tickdistance < 50){
        currentMonthGap++;
    }
    else if (tickdistance > 100){
        currentMonthGap--;
    }
    xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
    d3.selectAll("#simplelineaxis > .tick").attr("transform", function(d,i,n){
        return "translate("
        + (getTranslation(d3.select(n[i]).attr("transform"))[0])
        + ",0)";
    });
        d3.selectAll(".dots").attr("cx", function (d) {
            return xz(parseTime(d.date));
        });
    valueline.x(function (d) {
        return xz(parseTime(d.date));
    });
    if(plotpath == undefined){
        return;
    }
    plotpath.attr("d", valueline);

}