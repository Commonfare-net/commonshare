// Calculate initial width
var boxWidth = $("#linechartdiv").innerWidth();
$("#linechart").attr("width", boxWidth);

$(window).resize(function () {
    boxWidth = $("#linechartdiv").innerWidth();
    $("#linechart").attr("width", boxWidth);

});

function plotsimpleline() {
    
    $("#linechart").on("wheel mousewheel", function (e) {
        e.preventDefault();
    });

    var tooltip_div = d3.select("body").append("div")
        .attr("class", "tooltip");

    //Positioning of divs programmatically
    var margin = {
        top: 50,
        right: 0,
        bottom: 150,
        left: 0
    };
    var chart = d3.select("#linechart");
    var chartwidth = +chart.attr("width") - margin.left - margin.right;
    var chartheight = +chart.attr("height") - margin.top - margin.bottom;
    var chartg = chart.append("g")
        .attr("transform", "translate(" + 0 + "," + margin.top + ")");

    chart.append("rect")
    .attr("id", "captureRect")
    .attr("class", "captureoverlay")
    .attr("width", chartwidth)
    .attr("height", chartheight)
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .on("mousemove", mousemove)
    .on("mouseout",mouseout);

    var x = d3.scaleTime()
        .rangeRound([0, chartwidth * 2]);
    var y = d3.scaleLinear()
        .rangeRound([chartheight, 0]);
    var zoom = d3.zoom()
        .scaleExtent([0.5, 2])
        .translateExtent([[0, 0],
                [chartwidth * 2 + 50, chart.attr("height")]])
        .on("zoom", zoomed);

    var currentMonthGap = 1;
    var transform;

    //Zooming and translation function
    //Repositions lines and adjusts x-axis tick spacing
    function zoomed() {
        transform = d3.event.transform;
        var xz = d3.event.transform.rescaleX(x);
        gX.call(xAxis.scale(xz));
        d3.select("#commonshare_circle")
        .attr("cx", -10)
        .attr("cy", -10);
        d3.select("#commonshare_text")
        .attr("x", -10)
        .attr("y", -10);

        //Recalculate tick numbers
        var selection = $("#simplelineaxis > .tick");
        left_tick_pos = selection.eq(0).position().left;
        right_tick_pos = selection.eq(1).position().left;
        var tickdistance = right_tick_pos - left_tick_pos;
        if (tickdistance < 50) {
            currentMonthGap++;
        } else if (tickdistance > 100) {
            currentMonthGap = Math.max(1, --currentMonthGap);
        }
        //Pick a sensible tick range based on timediff
        xAxis.ticks(spacingFunc.every(Math.max(1, currentMonthGap)));
        
        gX.call(xAxis);

        d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
            var t = getTranslation(d3.select(this).attr("transform"))[0];
            return "translate(" + t + ",0)";
        });

        kcoreline.x(function (d) {
            return xz(d.date);
        });

        linepath.attr("d", kcoreline);
    }

    var kcoreline = d3.line()
        .x(function (d) {
            return x(d.date);
        })
        .y(function (d) {
            return y(d.kcore);
        });

    var kcorelist = [];
    Object.keys(data).forEach(function (month) {
        node_data[month].kcore = +node_data[month].kcore;
        kcorelist.push({
            "date": node_data[month].date,
            "kcore": node_data[month].kcore
        });
    });
    x.domain([
        d3.min(kcorelist, function (c) {return c.date;}),
        d3.max(kcorelist, function (c) {return c.date;})
        ]);
    y.domain([
        d3.min(kcorelist, function (d) {return d.kcore;}),
        d3.max(kcorelist, function (d) {return d.kcore;})
        ]);
    //Commonshare line
    var linepath = chartg.append("path")
        .datum(kcorelist)
        .attr("id", "commonshare_line")
        .attr("clip-path", "url(#clip)")
        .attr("d", kcoreline);

    //Clipping rectangle
    var clip = chartg.append("clipPath")
        .attr("id", "clip");
    var clipRect = clip.append("rect")
        .attr("width", chart.attr("width"))
        .attr("height", chart.attr("height"))
        .attr("y", -10);

    //X axis
    var xAxis = d3.axisBottom(x).tickFormat(tickf).ticks(spacingFunc.every(1));
    var gX = chartg.append("g")
        .attr("transform", "translate(0," + chartheight + ")")
        .attr("class", "axis")
        .attr("id", "simplelineaxis")
        .call(xAxis);
    d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
        var t = getTranslation(d3.select(this).attr("transform"))[0];
        return "translate(" + t + ",0)";
    });

    //Y axis
    chartg.append("g")
    .attr("class", "axis")
    .call(d3.axisLeft(y).ticks(4).tickSize(-chartwidth))
    .append("text")
    .attr("fill", "var(--cf-green)")
    .attr("transform", "rotate(-90)")
    .attr("y", -10)
    .attr("x", 0)
    .attr("dy", "-1em")
    .attr("text-anchor", "end")
    .text("Commonshare")
    .style("font-size", "14px");

   
    previousIndex = 0;

    //Commonshare point circles and text
    chart.append("circle")
    .attr("r", 6)
    .attr("id", "commonshare_circle");

    chart.append("text")
    .attr("id", "commonshare_text");

    //Couple of utility functions
    var bisectDate = d3.bisector(function (d, x) {
            return x - d.date;
        }).left;

    var otheruser;
    function findOtherNode(node) {
        return node.id == otheruser;
    }

    function mouseout(){
        tooltip_div.transition()
        .duration(200)
        .style("opacity", 0);
    }
    //Function that shows/hides different information when
    //moving the mouse over the chart
    function mousemove() {
        //Calculate the nearest date that the cursor is over
        var xt = transform.rescaleX(x);
        var yt = transform.rescaleY(y);
        var x0 = xt.invert(d3.mouse(this)[0]);
        var i = bisectDate(node_data, x0);
        if (previousIndex == i) {
            return;
        }
        previousIndex = i;
        d1 = node_data[i];
        //Auto-update the donut
        currentdonut = i;
        plotdonut(graph_data[i], node_data[i]);
            chartpos = d3.select("#linechart").node().getBoundingClientRect();

       // console.log("Chartpos: " + chartpos.x + "," + chartpos.y);        
        tooltip_div.transition()
        .duration(200)
        .style("opacity", 1);
        var toolTipText = "";
        var interaction_types =
            ["create_story", "create_listing",
            "comment_story", "comment_listing",
            "conversation", "transaction"];
        for (i = 0; i < interaction_types.length; i++) {
            var type = interaction_types[i];
            if (type in d1 && d1[type].length > 0) {
                toolTipText += tooltipTranslate(type) +
                d1[type].length + "</br>";
            }
        }
        tooltip_div.html(toolTipText)
        .style("left", (xt(d1.date) + margin.left + 10 + chartpos.x) + "px")
        .style("top", (y(d1.kcore) + margin.top - 20) + chartpos.y + window.scrollY + "px");
        //Update the commonshare circle position and text
        d3.select("#commonshare_circle")
        .attr("cx", xt(d1.date) + margin.left)
        .attr("cy", y(d1.kcore) + margin.top)
        .style("pointer-events","none");

        d3.select("#commonshare_text")
        .attr("x", xt(d1.date) + margin.left)
        .attr("y", y(d1.kcore) + margin.top - 10)
        .html("")
        .text(d1.kcore)
        .style("pointer-events","none");

    }

    chart.call(zoom);
    chart.call(zoom.scaleBy, 2);
    chart.call(zoom.translateBy,  - (chart.attr("width") * 2), 0);
}
