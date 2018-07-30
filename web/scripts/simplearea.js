function plotsimplearea(user) {

	var chart = d3.select("#areachart").on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		}),
	margin = {
		top: 20,
		right: 20,
		bottom: 70,
		left: 40
	},
	chartwidth = +chart.attr("width") - margin.left - margin.right,
	chartheight = +chart.attr("height") - margin.top - margin.bottom,
	chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	$("#areachart").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var parseMonthAxis = d3.timeFormat("%Y-%m");

	var x = d3.scaleTime()
		.rangeRound([0, chartwidth * 3]);
	var y = d3.scaleLinear()
		.rangeRound([chartheight, 0]);
	var zoom = d3.zoom()
		.scaleExtent([0.33, 1])
		.translateExtent([[0, 0], [chart.attr('width') * 3 + 50, chart.attr("height")]])
		.on('zoom', zoomed);
	var currentMonthGap = 1;

	function zoomed() {
		var xz = d3.event.transform.rescaleX(x);
		gX.call(xAxis.scale(xz));
		var selection = $("#simpleareaaxis > .tick");
		var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;
		d3.selectAll("#simpleareaaxis > .tick").attr("transform", function () {
			return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
		});

		if (tickdistance < 50)
			currentMonthGap++;
		else if (tickdistance > 100)
			currentMonthGap--;
		xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));

		area.x(function (d) {
			return xz(d.data.date) + 20;
		})
		metapath.attr("d", area);
		dots.attr("cx", function (d) {
			return xz(d.data.date) + 20;
		})
	}
	color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);
	color.domain(mykeys);
	var area = d3.area()
		.x(function (d) {
			return x(d.data.date) + 20;
		})
		.y0(function (d) {
			return y(d[0]);
		})
		.y1(function (d) {
			return y(d[1]);
		});

	var stack = d3.stack();
	var cumu_total_object = []
	for (var month in data) {

		var cumu_totals = node_data[month].cumu_totals;
		var keys = Object.keys(cumu_totals);
		cumu_totals["date"] = node_data[month].date;
		cumu_totals["stats"] = node_data[month].stats;
		if (month != 0) {

			var monthsWithZero = d3.timeMonth.count(node_data[month - 1].date, node_data[month].date) - 1;
			for (var i = 0; i < monthsWithZero; i++) {
				var mytotals = {};
				for (var j in keys) {
					mytotals[keys[j]] = 0;
				}
				mytotals['stats'] = {}
				mytotals['date'] = d3.timeMonth.offset(node_data[month - 1].date, i + 1);
				console.log(mytotals['date']);
				cumu_total_object.push(mytotals);
			}
		}
		cumu_total_object.push(cumu_totals);
	}
	console.log(cumu_total_object);

	var maxDateVal = d3.max(cumu_total_object, function (d) {
			var vals = d3.keys(d).map(function (key) {
					return key !== 'date' && key !== 'stats' ? d[key] : 0
				});
			return d3.sum(vals);
		});

	// Set domains for axes
	x.domain(d3.extent(cumu_total_object, function (d) {
			return d.date;
		}));
	//So that single ticks are positioned in the center of the axis
	if (x.domain()[0].getTime() == x.domain()[1].getTime()) {
		var dateLess = d3.timeMonth.offset(x.domain()[0], -1);
		var dateMore = d3.timeMonth.offset(x.domain()[0], 1);
		x.domain([dateLess, dateMore])
	}
	y.domain([0, maxDateVal])

	stack.keys(keys);
	stack.order(d3.stackOrderNone);
	stack.offset(d3.stackOffsetNone);

	var meta = chartg.selectAll('.meta')
		.data(stack(cumu_total_object))
		.enter().append("g")
		.attr("class", "meta");

	var metapath = meta.append("path")
		.attr("class", function(d){return "area "+ d.key;})
		.attr("clip-path", "url(#clip)")
		.attr("d", area)
		.style("fill", function (d) {
			return color(d.key);
		})
		.style("opacity", 0.6);

	var dots = chartg.selectAll(".dots")
		.data(stack(cumu_total_object))
		.enter().append("g")
		.attr("id", function (d) {
			return d.key;
		})
        .attr("class", function (d) {
            return d.key;
        })
		.selectAll("circle")
		.data(function (d, index) {
			return d;
		})
		.enter().append("circle")
		.attr("class", function (d) {
			return "mydot" + d.id;
		})
		.style("fill", function (d) {
			return color(d3.select(this.parentNode).attr("id"));
		})
		.attr("r", 4)
		.attr("clip-path", "url(#clip)")
		.attr("cx", function (d) {
			return x(d.data.date) + 20;
		})
		.attr("cy", function (d) {
			return y(d[1]);
		})
		.on("mouseover", function (d) {
			d3.select(this).attr("r", 8);
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("r", 4);
		})
		.on("click", function (d, i) {
			drawTooltipGraph(d.date, d.id);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		});

	var xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(1));
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis")
		.attr("id", "simpleareaaxis")
		.call(xAxis);

	chartg.append("g")
	.attr("class", "axis")
	.call(d3.axisLeft(y).ticks(4))
	.append("text")
	.attr("fill", "#000")
	.attr("transform", "rotate(-90)")
	.attr("y", 6)
	.attr("dy", "-2em")
	.attr("text-anchor", "end")
	.text("Commonshare");

	//Adapted from http://zeroviscosity.com/d3-js-step-by-step/step-3-adding-a-legend
	var legendRectSize = 18;
	var legendSpacing = 4;
	var opacity = 1;
	var legend = chartg.selectAll(".legend")
		.data(color.domain())
		.enter()
		.append('g')
		.attr('class', 'legend')
		.on("mouseover", function (d) {
			d3.select(this).style('fill', color);
			document.body.style.cursor = "pointer";
		})
		.on("mouseout", function (d) {
			d3.select(this).style('fill', 'black');
			document.body.style.cursor = "auto";
		})
		.on("click", function (d) {
			legendclick(d);
			d3.select(this).style('opacity', opacity);
		});

	var clip = chartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", chart.attr("width"))
		.attr("height", chart.attr("height"));

	legend.append('rect')
	.attr('width', legendRectSize)
	.attr('height', legendRectSize)
	.style('fill', color)
	.style('stroke', color);

	legend.append('text')
	.attr('x', legendRectSize + legendSpacing)
	.attr('y', legendRectSize - legendSpacing)
	.text(function (d) {
		return d;
	});

	legend.attr('transform', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 150;
		var width = legendRectSize + legendSpacing;
		var horz = elementwidth * i;
		var vert = -20;
		return 'translate(' + (horz) + ',' + vert + ')';
	})
	var olddate = "";
	d3.selectAll("#simpleareaaxis > .tick").attr("transform", function () {
		return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
	});

	function legendclick(d) {
		if (d3.selectAll("." + d).style("visibility") == "visible") {
			d3.selectAll("." + d).style("visibility", "hidden");
			d3.selectAll(".mydot" + d).style("visibility", "hidden");
			opacity = 0.5;
		} else {
			d3.selectAll("." + d).style("visibility", "visible");
			d3.selectAll(".mydot" + d).style("visibility", "visible");
			opacity = 1;
		}
	}
	chart.call(zoom);

}
