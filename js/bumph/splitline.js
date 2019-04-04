function plotsplitline(user) {

	var charts = d3.selectAll(".commonchart").on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		});
	var margin = {
		top: 5,
		right: 50,
		bottom: 20,
		left: 20
	},
	chartwidth = +charts.attr("width") - margin.left - margin.right,
	chartheight = +charts.attr("height") - margin.top - margin.bottom,
	chartg = charts.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var titles = d3.selectAll(".commonchart-title");
	var zoom = d3.zoom()
		.scaleExtent([0.33, 1])
		.translateExtent([[0, 0], [charts.attr('width') * 3 + 50, charts.attr("height")]])
		.on('zoom', zoomed);

	$(".commonchart").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});
	var currentMonthGap = 2;

	function zoomed() {
		var xz = d3.event.transform.rescaleX(x);
		gX.call(xAxis.scale(xz));
		var selection = $(".splitlineaxis > .tick");
		var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;
		d3.selectAll(".splitlineaxis > .tick").attr("transform", function () {
			return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
		});

		if (tickdistance < 50)
			currentMonthGap++;
		else if (tickdistance > 100)
			currentMonthGap--;
		xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));

		line.x(function (d) {
			return xz(d.date) + 20;
		})
		linepath.attr("d", function (d) {
			return line(d.values);
		});
		dots.attr("cx", function (d) {
			return xz(d.date) + 20;
		})
	}

	var parseMonthAxis = d3.timeFormat("%Y-%m");

	var x = d3.scaleTime()
		.rangeRound([0, chartwidth * 3]);
	var y = d3.scaleLinear()
		.rangeRound([chartheight, 0]);
	var z = d3.scaleOrdinal(d3.schemeCategory10);

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
	var lists_of_metas = {}
	var kcorelist = []
	var storylist = []
	var discussionlist = []
	var friendshiplist = []
	var transactionlist = []

	for (var month in data) {
        
		var avg_totals = node_data[month].avg;
		var keys = Object.keys(avg_totals);
        //	color = d3.scaleOrdinal() // D3 Version 4
		//.domain(keys)
		//.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);
		for (var name in avg_totals) {
			if (avg_totals.hasOwnProperty(name)) {
				if (!(name in lists_of_metas))
					lists_of_metas[name] = [];
				if (month != 0) {
					var monthsWithZero = d3.timeMonth.count(node_data[month - 1].date, node_data[month].date) - 1;
					for (var i = 0; i < monthsWithZero; i++) {
						lists_of_metas[name].push({
							"id": name,
							"stats": {},
							"date": d3.timeMonth.offset(node_data[month - 1].date, i + 1),
							"total": 0
						});
					}
				}
				lists_of_metas[name].push({
					"id": name,
					"date": node_data[month].date,
					"stats": node_data[month].stats,
					"total": avg_totals[name]
				});
			}
		};
		node_data[month].kcore = +node_data[month].kcore

	}

	var avgdata_list = Object.keys(lists_of_metas).map(function (k) {
			return {
				"id": k,
				"values": lists_of_metas[k]
			};
		});

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

	var linepath = chartg.append("path")
		.data(avgdata_list)
		.attr("class", "mypath")
		.attr("clip-path", "url(#lineclip)")
		.attr("d", function (d) {
			return line(d.values);
		})
		.style("stroke", function (d) {
			return color(d.id);
		});

	titles.data(avgdata_list)
	.each(function (d) {
		d3.select(this).node().innerHTML = d.id;
		d3.select(this).node().style.color = color(d.id);
	});

	var dots = chartg.append("g")
		.data(avgdata_list)
		.attr("class", "dots")
		.selectAll("circle")
		.data(function (d, i) {
			return d.values;
		})
		.enter().append("circle")
		.attr("class", "mydot")
		.style("fill", function (d) {
			return color(d.id);
		})
		.attr("id", function (d, i) {
			return "dot" + d.total + "-" + (i);
		})
		.attr("r", 3)
		.attr("clip-path", "url(#lineclip)")
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
			drawTooltipGraph(d.date, d.id);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		});

	var clip = charts.append("clipPath")
		.attr("id", "lineclip");
	var clipRect = clip.append("rect")
		.attr("width", charts.attr("width"))
		.attr("height", chartheight);

	var xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(2));
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis splitlineaxis")
		.call(xAxis);

	d3.selectAll(".splitlineaxis > .tick").attr("transform", function () {
		return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";
	});

	chartg.append("g")
	.attr("class", "axis")
	.call(d3.axisLeft(y).ticks(3));
    
	charts.call(zoom);

}
