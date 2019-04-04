
function plotgroupedbar(user,varnodedata,vargraphdata,divid) {

    if(varnodedata == null)
        varnodedata = node_data;
    if(vargraphdata == null)
        vargraphdata = graph_data;
    if(divid == null)
        divid = "groupedbarchart";
    
	var chart = d3.select("#"+divid).on("click", function (d) {
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

	var parseMonthAxis = d3.timeFormat("%Y-%m");
	var x0 = d3.scaleTime()
		.rangeRound([0, chartwidth * 3]);

	var x1 = d3.scaleBand()
		.padding(0.05);
	var y = d3.scaleLinear()
		.rangeRound([chartheight, 0]);
    color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);    
	color.domain(mykeys);

	var zoom = d3.zoom()
		.scaleExtent([0.33, 1])
		.translateExtent([[0, 0], [chart.attr('width') * 4, chart.attr("height")]])
		.on('zoom', zoomed);

	$("#"+divid).bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});
	var currentMonthGap = 1;
	function zoomed() {
		var xz = d3.event.transform.rescaleX(x0);
		var scale = d3.event.transform.k;
		var selection = $("#groupedaxis > .tick");
		if (selection.length < 2)
			return;

		var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;

		if (tickdistance < 50)
			currentMonthGap++;
		else if (tickdistance > 100)
			currentMonthGap--;

		xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
		x1.rangeRound([0, 50 * scale * 4]);

		gX.call(xAxis.scale(xz)); 
		d3.selectAll("#groupedaxis > .tick").attr("transform", function () {
			return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 40) + ",0)";
		});

		rects.attr("x", function (d) {
			return xz(d.date) + 40 + x1(d.key) - (100 * scale);
		});
		rects.attr("width", 50 * scale);
	
		kcoreline.x(function (d) {
			return xz(d.date) + 40;
		})
		linepath.attr("d", kcoreline);
		dots.attr("cx", function (d) {
			return xz(d.date) + 40;
		})
	}

	var kcoreline = d3.line()
		.curve(d3.curveMonotoneX)
		.x(function (d) {
			return x0(d.date) + 40;
		})
		.y(function (d) {
			return y(d.kcore);
		});
	var avg_total_object = []
	var kcore_vals = []
	for (var month in data) {
		var avg_totals = varnodedata[month].avg;
		var keys = Object.keys(avg_totals);
		avg_totals["date"] = varnodedata[month].date;
		avg_totals["stats"] = varnodedata[month].stats;

		if (month != 0) {

			var monthsWithZero = d3.timeMonth.count(varnodedata[month - 1].date, varnodedata[month].date) - 1;
			for (var i = 0; i < monthsWithZero; i++) {
				totals = {};
				for (var j in keys) {
					totals[keys[j]] = 0;
				}
				totals['stats'] = {}
				console.log(d3.timeMonth.offset(varnodedata[month - 1].date, i + 1));
				totals['date'] = d3.timeMonth.offset(varnodedata[month - 1].date, i + 1);
				console.log(totals);
				avg_total_object.push(totals);
			}
		}

		avg_total_object.push(avg_totals);
		kcore_vals.push({
			"kcore": varnodedata[month].kcore,
			"date": varnodedata[month].date
		});

	}

	var maxDateVal = d3.max(avg_total_object, function (d) {
			var vals = d3.keys(d).map(function (key) {
					return key !== 'date' && key !== 'stats' ? d[key] : 0
				});
			return d3.max(vals);
		});

	x0.domain([
			d3.min(avg_total_object, function (d) {
				return d.date;
			}),
			d3.max(avg_total_object, function (d) {
				return d.date;
			})
		]);
	x1.domain(keys).rangeRound([0, 200]);
	y.domain([0, maxDateVal]);

	var rectgroup = chartg.append("g")
		.selectAll("g")
		.data(avg_total_object)
		.enter().append("g")
		.attr("id", function (d) {
			return d.key;
		})
		.attr("clip-path", "url(#clip)");

	var rects = rectgroup.selectAll("rect")
		.data(function (d) {
			return keys.map(function (key) {
				return {
					key: key,
					value: d[key],
					stats: d.stats,
					date: d.date
				};
			});
		})
		.enter().append("rect")
		.attr("x", function (d) {
			return x0(d.date) + x1(d.key) -60;
		})
		.attr("y", function (d) {
			return y(d.value);
		})
		.attr("height", function (d) {
			return chartheight - y(d.value);
		})
		.attr("width", function (d) {
			return Math.min(x1.bandwidth(), 50);
		})
		.attr("fill", function (d) {
			return color(d.key);
		})
		.attr("clip-path", "url(#clip)")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
		})
		.on("click", function (d, i) {
			drawTooltipGraph(d.date, d.key,null,vargraphdata);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		})

	var linepath = chartg.append("path")
		.datum(kcore_vals)
		.attr("class", "mypath")
		.attr("clip-path", "url(#clip)")
		.attr("d", kcoreline)
		.style("stroke", "black")
		.style("stroke-width", 3.5);

	var dots = chartg.selectAll("circle")
		.data(kcore_vals)
		.enter().append("circle")
		.attr("class", "mydot")
		.attr("r", 6)
		.attr("clip-path", "url(#clip)")
		.attr("cx", function (d) {
			return x0(d.date) + 40;
		})
		.attr("cy", function (d) {
			return y(d.kcore);
		})
		.on("mouseover", function (d) {
			var html_content = "";
			d3.select(this).attr("r", 8);
			div.transition()
			.duration(200)
			.style("opacity", .9);
			div.html(html_content)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("r", 6);
			div.transition()
			.duration(500)
			.style("opacity", 0);
		});

	var clip = chartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", chart.attr('width'))
		.attr("height", chart.attr('height'));
	var totalWidth = chartwidth;
8
	var xAxis = d3.axisBottom(x0).tickFormat(anotherFormat).ticks(d3.timeMonth.every(1));
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis")
		.attr("id", "groupedaxis")
		.attr('clip-path', 'url(#clip')
		.call(xAxis);
	d3.selectAll("#groupedaxis > .tick").attr("transform", function () {
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

	chart.call(zoom);

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

}
