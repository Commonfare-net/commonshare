
function plotstackedbar(user) {

	var chart = d3.select("#stackedbarchart"),
	margin = {
		top: 20,
		right: 20,
		bottom: 70,
		left: 40
	},
	chartwidth = +chart.attr("width") - margin.left - margin.right,
	chartheight = +chart.attr("height") - margin.top - margin.bottom,
	chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var parseMonthAxis = d3.timeFormat("%Y-%m");
	var x = d3.scaleTime()
		.rangeRound([0, chartwidth * 3]);

	var y = d3.scaleLinear()
		.rangeRound([chartheight, 0]);
	color.domain(mykeys);
	var zoom = d3.zoom()
		.scaleExtent([0.33, 1])
		.translateExtent([[0, 0], [chart.attr('width') * 4, chart.attr("height")]])
		.on('zoom', zoomed);

	$("#stackedbarchart").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var currentMonthGap = 1;

	function zoomed() {
		var xz = d3.event.transform.rescaleX(x);
		var scale = d3.event.transform.k;
		var selection = $("#stackedaxis > .tick");
		if (selection.length < 2)
			return;
		var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;

		if (tickdistance < 50)
			currentMonthGap++;
		else if (tickdistance > 100)
			currentMonthGap--;

		xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
		gX.call(xAxis.scale(xz)); 
		d3.selectAll("#stackedaxis > .tick").attr("transform", function () {
			return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 40) + ",0)";
		});
		rects.attr("x", function (d) {
			return xz(d.data.date) + 40 - (25 * scale);
		});
		rects.attr("width", 50 * scale);
	}

	var stack = d3.stack();
	var cumu_total_object = []
	for (var month in data) {
		var cumu_totals = data[month].cumu_totals;
		var keys = Object.keys(cumu_totals);
		var index = keys.indexOf("date");
		if (index > -1) {
			keys.splice(index, 1);
		}
		var index = keys.indexOf("stats");
		if (index > -1) {
			keys.splice(index, 1);
		}
		cumu_totals["date"] = data[month].date;
		cumu_totals["stats"] = data[month].stats;
		if (month != 0) {

			var monthsWithZero = d3.timeMonth.count(data[month - 1].date, data[month].date) - 1;
			for (var i = 0; i < monthsWithZero; i++) {
				totals = {};
				for (var j in keys) {
					totals[keys[j]] = 0;
				}
				totals['stats'] = {}
				totals['date'] = d3.timeMonth.offset(data[month - 1].date, i + 1);
				cumu_total_object.push(totals);
			}
		}
		cumu_total_object.push(cumu_totals);
		console.log(cumu_total_object);
	}

	var maxDateVal = d3.max(cumu_total_object, function (d) {
			var vals = d3.keys(d).map(function (key) {
					return key !== 'date' && key !== 'stats' ? d[key] : 0
				});
			return d3.sum(vals);
		});

	x.domain([
			d3.min(cumu_total_object, function (d) {
				return d.date;
			}),
			d3.max(cumu_total_object, function (d) {
				return d.date;
			})
		]);

	y.domain([0, maxDateVal])

	stack.keys(keys);
	stack.order(d3.stackOrderNone);
	stack.offset(d3.stackOffsetNone);

	var rects = chartg.append("g")
		.selectAll("g")
		.data(d3.stack().keys(keys)(cumu_total_object))
		.enter().append("g")
		.attr("id", function (d) {
			return d.key;
		})
		.attr("fill", function (d) {
			return color(d.key);
		})
		.attr("clip-path", "url(#clip)")
		.selectAll("rect")
		.data(function (d) {
			console.log(d);
			return d;
		})
		.enter().append("rect")
		.attr("x", function (d) {
			return x(d.data.date) + 15;
		}) 
		.attr("y", function (d) {
			return y(d[1]);
		})
		.attr("height", function (d) {
			return y(d[0]) - y(d[1]);
		})
		.attr("width", 50)
		.on("mouseover", function (d) {
			var html_content = "";
			for (var meta in d.data.stats) {
				if (meta == d3.select(this.parentNode).attr("id")) { //If this holds the interactions of this particular type
					for (var statistic in d.data.stats[meta]) {
						if (d.data.stats[meta][statistic].length > 0)
							html_content += prettyKeys[statistic] + ": " + d.data.stats[meta][statistic].length + "<br/>";
					}
				}
			}
			d3.select(this).style("opacity", 0.7);
			div.transition()
			.duration(200)
			.style("opacity", .9);
			div.html(html_content)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		})
		.on("mouseout", function () {
			d3.select(this).style("opacity", 1);
			div.transition()
			.duration(500)
			.style("opacity", 0);
		});

	var clip = chartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", chart.attr("width"))
		.attr("height", chart.attr("height"));

	var xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(1));
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis")
		.attr("id", "stackedaxis")
		.attr('clip-path', 'url(#clip')
		.call(xAxis);

	d3.selectAll("#stackedaxis > .tick").attr("transform", function () {
		return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 40) + ",0)";
	});

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

	color.domain(mykeys);

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
	var olddate = "";
	legend.attr('transform', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 150;
		var width = legendRectSize + legendSpacing;
		var horz = elementwidth * i;
		var vert = -20;
		return 'translate(' + (horz) + ',' + vert + ')';
	})
	function legendclick(d) {
		if (d3.select("#" + d).style("visibility") == "visible") {
			d3.select("#" + d).style("visibility", "hidden");
			d3.selectAll(".mydot" + d).style("visibility", "hidden");
			opacity = 0.5;
		} else {
			d3.select("#" + d).style("visibility", "visible");
			d3.selectAll(".mydot" + d).style("visibility", "visible");
			opacity = 1;
		}
	}

	chart.call(zoom);
}
