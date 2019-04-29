// Calculate initialwidth
var boxWidth = $("#linechartdiv").innerWidth();
$("#linechart").attr("width", boxWidth);

$(window).resize(function () {
	boxWidth = $("#linechartdiv").innerWidth();
	$("#linechart").attr("width", boxWidth);

});
var transform;
previousIndex = 0;
//Positioning of divs programmatically
var lmargin = {
	top: 50,
	right: 0,
	bottom: 150,
	left: 0
};

var tooltip_div = d3.select("body").append("div")
	.attr("class", "tooltip");

var xAxis;
var gX;
var line;
var kcoreline;
var linepath;
var metapath;
var lchart = d3.select("#linechart");
var lchartwidth = +lchart.attr("width") - lmargin.left - lmargin.right;
var lchartheight = +lchart.attr("height") - lmargin.top - lmargin.bottom;
var lchartg = lchart.append("g")
	.attr("transform", "translate(" + 0 + "," + lmargin.top + ")");
var x = d3.scaleTime()
	.rangeRound([0, lchartwidth * 2]);
var y = d3.scaleLinear()
	.rangeRound([lchartheight, 0]);

var bisectDate = d3.bisector(function (d, x) {
		return x - d.date;
	}).left;

var avg_total_object = [];

/**
* Populates the 'kcorelist' array with Objects that contain a date and the commonshare value at that time
* so that the commonshare line can be plotted
* @returns {Object[]} list of date/commonshare Objects
*/
function populateCore(){
	avg_total_object = [];
    kcorelist = [];
	Object.keys(data).forEach(function (month) {
		var avg_totals = node_data[month].cumu;
		if (avg_totals == null) {
			Object.keys(keys).forEach(function (name) {
				if (!(keys[name]in avg_total_object)) {
					avg_total_object[keys[name]] = [];
				}
				avg_total_object[keys[name]].push({
					"id": keys[name],
					"stats": {},
					"date": node_data[month].date,
					"total": 0
				});
			});
		} else {
			Object.keys(avg_totals).forEach(function (name) {
				if (avg_totals.hasOwnProperty(name)) {
					if (!(name in avg_total_object)) {
						avg_total_object[name] = [];
					}
					avg_total_object[name].push({
						"id": name,
						"stats": node_data[month].stats,
						"date": node_data[month].date,
						"total": avg_totals[name]
					});
				}
			});
		}
		node_data[month].kcore = +node_data[month].kcore;
		kcorelist.push({
			"date": node_data[month].date,
			"kcore": node_data[month].kcore
		});
	}); 
    return kcorelist;    
}

/**
* For each interaction type (story/social/etc) maps its name to a nested object that contains both its name and 
* its data values over time. 
* @returns {Object} interaction types mapped to Objects containing their ID and data values over time
*/
function populateAvg(){
    var avgdata_list = Object.keys(avg_total_object).map(function (k) {
        return {
            "id": k,
            "values": avg_total_object[k]
        };
    });
   return avgdata_list;
}

/**
* Main function for drawing the axes in the correct position and adding the various lines 
* onto the chart. 
*/
function plotLine() {
	$("#linechart").on("wheel mousewheel", function (e) {
		e.preventDefault();
	});

	lchart.append("rect")
	.attr("id", "captureRect")
	.attr("class", "captureoverlay")
	.attr("width", lchartwidth)
	.attr("height", lchartheight)
	.attr("transform", "translate(" + lmargin.left + "," + lmargin.top + ")")
	.on("mousemove", mousemove)
	.on("mouseout", mouseout);

	var zoom = d3.zoom()
		.scaleExtent([0.5, 2])
		.translateExtent([[0, 0],
				[lchartwidth * 2 + 50, lchart.attr("height")]])
		.on("zoom", zoomed);

	line = d3.line()
		.x(function (d) {
			return x(d.date);
		})
		.y(function (d) {
			return y(d.total);
		});

	kcoreline = d3.line()
		.x(function (d) {
			return x(d.date);
		})
		.y(function (d) {
			return y(d.kcore);
		});

	kcorelist = populateCore();
    avgdata_list = populateAvg();

	x.domain([
    d3.min(avgdata_list, function (c) {
        return d3.min(c.values, function (d) {
            return d.date;
        });
    }),
    d3.max(avgdata_list, function (c) {
        return d3.max(c.values, function (d) {
            return d.date;
        });
    })
	]);
    
	y.domain([
        d3.min(kcorelist, function (d) {return d.kcore;}),
        d3.max(kcorelist, function (d) {return d.kcore;})
    ]);
    
	//Commonshare line
	linepath = lchartg.append("path")
		.datum(kcorelist)
		.attr("id", "commonshare_line")
		.attr("clip-path", "url(#clip)")
		.attr("d", kcoreline);
	var meta = lchartg.selectAll(".meta")
		.data(avgdata_list)
		.enter().append("g")
		.attr("class", "meta");

	//Lines for social/stories/transactions/listings
	metapath = meta.append("path")
		.attr("clip-path", "url(#clip)")
		.attr("id", function (d) {
			return d.id;
		})
		.attr("class", function (d) {
			return "line " + d.id;
		})
		.attr("d", function (d) {
			return line(d.values);
		})
		.style("stroke", function (d) {
			return color(d.id);
		})
		.style("stroke-width", 2)
		.style("visibility", "hidden"); //hidden by default

	//Clipping rectangle
	var clip = lchartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", lchart.attr("width"))
		.attr("height", lchart.attr("height"))
		.attr("y", -10);

	//X axis
	xAxis = d3.axisBottom(x).tickFormat(tickf).ticks(d3.timeMonth.every(1));
	gX = lchartg.append("g")
		.attr("transform", "translate(0," + lchartheight + ")")
		.attr("class", "axis")
		.attr("id", "simplelineaxis")
		.call(xAxis);
	d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
		var t = getTranslation(d3.select(this).attr("transform"))[0];
		return "translate(" + t + ",0)";
	});

	//Y axis
	lchartg.append("g")
	.attr("class", "axis")
	.call(d3.axisLeft(y).ticks(4).tickSize(-lchartwidth))
	.append("text")
	.attr("fill", "var(--cf-green)")
	.attr("transform", "rotate(-90)")
	.attr("y", -10)
	.attr("x", 0)
	.attr("dy", "-1em")
	.attr("text-anchor", "end")
	.text("Commonshare")
	.style("font-size", "14px");

	addLegend();

	//Story/social/transaction/listing circles that appear on hover
	lchart.selectAll(".metacircles")
	.data(keys)
	.enter()
	.append("circle")
	.attr("class", "metacircles")
	.attr("id", function (d) {
		return "metacircle_" + d;
	})
	.attr("r", 4)
	.style("fill", function (d) {
		return color(d);
	})
	.style("visibility", "hidden"); //hidden by default

	//Commonshare point circles and text
	lchart.append("circle")
	.attr("r", 6)
	.attr("id", "commonshare_circle");

	lchart.append("text")
	.attr("id", "commonshare_text");

	lchart.call(zoom);
	lchart.call(zoom.scaleBy, 2);
	lchart.call(zoom.translateBy,  - (lchart.attr("width") * 2), 0);
}

var opacity = 0.5;

/**
* Behaviour of legend items when they are clicked (i.e., hide/show their respective line and data points)
*/
function legendClick(d) {
	if (d3.selectAll("." + d).style("visibility") == "visible") {
		d3.selectAll("." + d).style("visibility", "hidden");
		d3.selectAll("#metacircle_" + d).style("visibility", "hidden");
		opacity = 0.5;
	} else {
		d3.selectAll("." + d).style("visibility", "visible");
		d3.selectAll("#metacircle_" + d).style("visibility", "visible");
		opacity = 1;
	}
}
var currentMonthGap = 1;


/**
* Zooming and translation function
* Repositions lines and adjusts x-axis tick spacing
*/
function zoomed() {
	transform = d3.event.transform;
	var xz = d3.event.transform.rescaleX(x);
	gX.call(xAxis.scale(xz));
	d3.selectAll(".metacircles")
	.attr("cx", -10)
	.attr("cy", -10);
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
	xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
	gX.call(xAxis);

	d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
		var t = getTranslation(d3.select(this).attr("transform"))[0];
		return "translate(" + t + ",0)";
	});

	kcoreline.x(function (d) {
		return xz(d.date);
	});

	linepath.attr("d", kcoreline);
	line.x(function (d) {
		return xz(d.date);
	});
	metapath.attr("d", function (d) {
		return line(d.values);
	});
}

//Remove tooltip on mouse out
function mouseout() {
	tooltip_div.transition()
	.duration(200)
	.style("opacity", 0);
}

/**
* Function that shows/hides different information when
* moving the mouse over the chart. Also updates the donut chart to show the current
* point being hovered over 
*/
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
	plotDonut(graph_data[i], node_data[i]);
	d3.selectAll(".metacircles")
	.attr("cx", xt(d1.date) + lmargin.left)
	.attr("cy", function (d) {
		if ("cumu" in d1) {
			return y(d1.cumu[d]) + lmargin.top;
		}
		return y(0) + lmargin.top;
	})
	.style("pointer-events", "none");

	var chartpos = d3.select("#linechart").node().getBoundingClientRect();

	tooltip_div.transition()
	.duration(200)
	.style("opacity", 1);
	console.log(d1);
	var toolTipText = "";
	var interaction_types =
		["create_story", "create_listing",
		"comment_story", "comment_listing",
		"conversation", "transaction"];
	for (i = 0; i < interaction_types.length; i++) {
		var type = interaction_types[i];
		if (type in d1 && d1[type].length > 0) {
			toolTipText += translate("tooltip" + type) +
			d1[type].length + "</br>";
		}
	}
	tooltip_div.html(toolTipText)
	.style("left", (xt(d1.date) + lmargin.left + 10 + chartpos.x) + "px")
	.style("top", (y(d1.kcore) + lmargin.top - 20 + chartpos.y + window.scrollY) + "px");
	//Update the commonshare circle position and text
	d3.select("#commonshare_circle")
	.attr("cx", xt(d1.date) + lmargin.left)
	.attr("cy", y(d1.kcore) + lmargin.top)
	.style("pointer-events", "none");

	d3.select("#commonshare_text")
	.attr("x", xt(d1.date) + lmargin.left)
	.attr("y", y(d1.kcore) + lmargin.top - 10)
	.html("")
	.text(d1.kcore)
	.style("pointer-events", "none");

}

/**
* Calculates the position of legend elements and adds them to the chart.
* Code mainly from http://zeroviscosity.com/d3-js-step-by-step/step-3-adding-a-legend
*/
function addLegend() {

	var legendRectSize = 15;
	var legendSpacing = 6;

	var legend = lchartg.selectAll(".legend")
		.data(keys)
		.enter()
		.append("g")
		.attr("class", "legend")
		.on("mouseover", function (d) {
			d3.select(this).style("fill", color);
			document.body.style.cursor = "pointer";
		})
		.on("mouseout", function (d) {
			d3.select(this).style("fill", "black");
			document.body.style.cursor = "auto";
		})
		.on("click", function (d) {
			legendClick(d);
			d3.select(this).style("opacity", opacity);
		})
		.style("opacity", opacity);

	legend.append("circle")
	.attr("r", legendRectSize / 2)
	.style("fill", "none")
	.style("stroke", color)
	.style("stroke-width", 2);

	legend.append("text")
	.attr("x", legendRectSize / 2 + legendSpacing)
	.attr("y", legendRectSize / 1.4 - legendSpacing)
	.text(function (d) {
        return translate(d);
	});

	legend.attr("xpos", function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 240;
		var width = legendRectSize + legendSpacing;
		var horz = 50 + elementwidth * i;
		return horz;
	});
	legend.attr("ypos", 275);
	legend.attr("transform", function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 240;
		var width = legendRectSize + legendSpacing;
		var horz = 25 + i % 2 * elementwidth;
		var vert = 295 + parseInt(i / 2) * 35;
		return "translate(" + (horz) + "," + vert + ")";
	});

	legend.each(function (d) {
		d3.select("body")
		.append("div")
		.style("position", "absolute")
		.style("left", d3.select(this).node().getBoundingClientRect().x + "px")
		.style("top", (d3.select(this).node().getBoundingClientRect().y + 20) + "px")
		.attr("id", "info" + d)
		.attr("class", "infodiv");
	});
}