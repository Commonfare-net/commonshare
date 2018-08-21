function plotsimpleline(user,varnodedata,vargraphdata,divid) {

    if(varnodedata == null)
        varnodedata = node_data;
    if(vargraphdata == null)
        vargraphdata = graph_data;
    if(divid == null)
        divid = "linechart";
	var margin = {
		top: 20,
		right: 20,
		bottom: 70,
		left: 50
	},
	chart = d3.select("#"+divid).on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		}),
	chartwidth = +chart.attr("width") - margin.left - margin.right,
	chartheight = +chart.attr("height") - margin.top - margin.bottom,
	chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	$("#"+divid).bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

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
		//Recalculate tick numbers
		var selection = $("#simplelineaxis > .tick");
		var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;

		if (tickdistance < 50)
			currentMonthGap++;
		else if (tickdistance > 100)
			currentMonthGap--;
		xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
		d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
			return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
		});

		kcoreline.x(function (d) {
			return xz(d.date) + 20;
		})
		linepath.attr("d", kcoreline);
		line.x(function (d) {
			return xz(d.date) + 20;
		})
		metapath.attr("d", function (d) {
			return line(d.values);
		});
		dots.attr("cx", function (d) {
			return xz(d.date) + 20;
		})
	}

	var line = d3.line()
		.curve(d3.curveMonotoneX)
		.x(function (d) {
			return x(d.date) + 20;
		})
		.y(function (d) {
			return y(d.total);
		});

	var kcoreline = d3.line()
		.curve(d3.curveMonotoneX)
		.x(function (d) {
			return x(d.date) + 20;
		})
		.y(function (d) {
			return y(d.kcore);
		});
	var keys;
	var kcorelist = []
	var avg_total_object = []
	console.log(data);
	for (var month in data) {
		var avg_totals = varnodedata[month].avg_totals;
		//data[month].date = parseTime(data[month].date);
		keys = Object.keys(avg_totals);
		for (var name in avg_totals) {
			if (avg_totals.hasOwnProperty(name)) {
				if (!(name in avg_total_object))
					avg_total_object[name] = [];
				//Add in necessary zero values here too
				if (month != 0) {
					var monthsWithZero = d3.timeMonth.count(varnodedata[month - 1].date, varnodedata[month].date) - 1;
					for (var i = 0; i < monthsWithZero; i++) {
						avg_total_object[name].push({
							"id": name,
							"stats": {},
							"date": d3.timeMonth.offset(varnodedata[month - 1].date, i + 1),
							"total": 0
						});
					}
				}
				avg_total_object[name].push({
					"id": name,
					"stats": varnodedata[month].stats,
					"date": varnodedata[month].date,
					"total": avg_totals[name]
				});
			}
		};
		varnodedata[month].kcore = +varnodedata[month].kcore;
		console.log("month is " + month);
		//Add in necessary zero values
		if (month != 0) {
			var monthsWithZero = d3.timeMonth.count(varnodedata[month - 1].date, varnodedata[month].date) - 1;
			for (var i = 0; i < monthsWithZero; i++) {
				kcorelist.push({
					"date": d3.timeMonth.offset(varnodedata[month - 1].date, i + 1),
					"kcore": 0
				});
			}
		}
		kcorelist.push({
			"date": varnodedata[month].date,
			"kcore": varnodedata[month].kcore
		});
	}

	var avgdata_list = Object.keys(avg_total_object).map(function (k) {
			return {
				"id": k,
				"date": varnodedata[month].date,
				"values": avg_total_object[k]
			};
		});
	console.log(avgdata_list);

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
	//So that single ticks are positioned in the center of the axis
	if (x.domain()[0].getTime() == x.domain()[1].getTime()) {
		var dateLess = d3.timeMonth.offset(x.domain()[0], -1);
		var dateMore = d3.timeMonth.offset(x.domain()[0], 1);
		x.domain([dateLess, dateMore])
	}
	y.domain([
			d3.min(avgdata_list, function (c) {
				return d3.min(c.values, function (d) {
					return d.total;
				});
			}),
			d3.max(avgdata_list, function (c) {
				return d3.max(c.values, function (d) {
					return d.total;
				});
			})
		]);

	for (var i = 0; i < keys.length; i++) {
		mykeys.push(String(keys[i]));
	}
	color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);

	var meta = chartg.selectAll('.meta')
		.data(avgdata_list)
		.enter().append("g")
		.attr("class", "meta");

	var metapath = meta.append("path")
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
		});

	var linepath = chartg.append("path")
		.datum(kcorelist)
		.attr("class", "mypath")
		.attr("clip-path", "url(#clip)")
		.attr("d", kcoreline)
		.style("stroke", "black")
		.style("stroke-width", 2.5);

	var clip = chartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", chart.attr("width"))
		.attr("height", chart.attr("height"));
	var totalLength = chartwidth;

	var dots = chartg.selectAll(".dots")
		.data(avgdata_list)
		.enter().append("g")
		.attr("class",function(d){return "dots " + d.id})
		.selectAll("circle")
		.data(function (d) {
			return d.values;
		})
		.enter().append("circle")
		.attr("class", function (d) {
			return "mydot" + d.id;
		})
		.style("fill", function (d) {
			return color(d.id);
		})
		.attr("id", function (d, i) {
			return "dot" + d.id + "-" + (i);
		})
		.attr("r", 4)
		.attr("clip-path", "url(#clip)")
		.attr("cx", function (d) {
			return x(d.date) + 20;
		})
		.attr("cy", function (d) {
			return y(d.total);
		})
		.on("mouseover", function (d) {
			d3.select(this).attr("r", 8);
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("r", 4);
		})
		.on("click", function (d, i) {
			drawTooltipGraph(d.date, d.id,null,vargraphdata);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		});

	var xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(1));
	console.log(avgdata_list);
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis")
		.attr("id", "simplelineaxis")
		.call(xAxis);
	d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
		return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
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

	legend.attr('transform', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 150;
		var width = legendRectSize + legendSpacing;
		var horz = elementwidth * i;
		var vert = -20;
		return 'translate(' + (horz) + ',' + vert + ')';
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