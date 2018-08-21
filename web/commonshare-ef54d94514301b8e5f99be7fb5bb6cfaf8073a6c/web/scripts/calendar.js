var startYear;
var cellSize = 25;

function plotcalendars(user,varnodedata,vargraphdata,divid) {

    if(varnodedata == null)
        varnodedata = node_data;
    if(vargraphdata == null)
        vargraphdata = graph_data;
    if(divid == null)
        divid = "calendarchart";
	var chart = d3.select("#"+divid).on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		}),
	chartg = chart.append("g");

	var zoom = d3.zoom()
		.scaleExtent([0.33, 2])
		.translateExtent([[0, 0], [Infinity, chart.attr("height")]]).on('zoom', zoomed);
	function zoomed() {
		chartg.attr("transform", d3.event.transform);
	}

	var formatWeek = d3.timeFormat("%U"), // week number of the year
	formatMonth = d3.timeFormat("%m"), // month number
	formatYear = d3.timeFormat("%Y"),
	formatDayOfMonth = d3.timeFormat("%d"),
	formatMyFormat = d3.timeFormat("%Y/%m/%d"),
	formatAbbMonth = d3.timeFormat("%b");

	var monthdates = [];
	var keys = [];
	for (var month in data) {
		var cumu_totals = varnodedata[month].cumu_totals;
		keys = Object.keys(cumu_totals);
		if (month != 0) {
			var monthsWithZero = d3.timeMonth.count(varnodedata[month - 1].date, varnodedata[month].date) - 1;
			for (var i = 0; i < monthsWithZero; i++) {
				monthdates.push({
					'date': d3.timeMonth.offset(varnodedata[month - 1].date, i + 1),
					'stats': {}
				});
			}
		}
		monthdates.push({
			'date': varnodedata[month].date,
			'stats': varnodedata[month].stats
		});
	}

	startYear = monthdates[0]['date'];

	var calendar = chartg.selectAll(".calendar")
		.data(monthdates)
		.enter().append("g")
		.attr("class", "calendar");

	var monthname = calendar
		.append("text")
		.style("font-size", 24)
		.text(function (d) {
			return formatAbbMonth(d.date);
		})
		.attr("x", function (d) {
			return (d3.timeWeek.count(d3.timeYear(d.date), d.date) - d3.timeWeek.count(d3.timeYear(d.date), startYear)) * cellSize + ((d3.timeMonth.count(d3.timeYear(d.date), d.date) - d3.timeMonth.count(d3.timeYear(d.date), startYear)) * 40)
		})
		.attr("y", 200);

	var rect = calendar.selectAll(".rect")
		.data(function (d) {

			var year = +formatYear(d.date);
			var month = +formatMonth(d.date) - 1;

			var mapped = d3.timeDays(new Date(year, month, 1), new Date(year, month + 1, 1)).map((val, index, arr) => {
					if (d.stats == null)
						return {
							date: val,
							stats: {},
							sumval: 0
						};
					else {
						return {
							date: val, //The original date becomes 'date' in the returned object
							stats: d.stats[formatMyFormat(val)], //And the interactions for this date in the graphdata are returned as 'stats'
							sumvals: sumStats(d.stats[formatMyFormat(val)]),
							sumval: formatMyFormat(val)in d.stats ? 4 : 0
						};
					}
				});
			return mapped;
		})
		.enter().append("g")
		.attr("class", "rect");

	var color = d3.scaleOrdinal() // D3 Version 4
		.domain(keys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);

	rect.append("rect")
	.attr("class", "day")
	.attr("width", cellSize)
	.attr("height", cellSize)
	.attr("x", function (d) {
		return (d3.timeWeek.count(d3.timeYear(d.date), d.date) - d3.timeWeek.count(d3.timeYear(d.date), startYear)) * cellSize
		 + (d3.timeMonth.count(d3.timeYear(d.date), d.date) - d3.timeMonth.count(d3.timeYear(d.date), startYear)) * 40

	})
	.attr("y", function (d) {
		var week_diff = formatWeek(d.date) - formatWeek(new Date(formatYear(d.date), formatMonth(d.date) - 1, 1));
		return d.date.getDay() * cellSize;
	})
    ;
	rect.selectAll(".minirect")
	.data(varnodedata, function (d) {
		return d.stats;
	})
	.enter().append("rect")
	.attr("class", "minirect");

	rect.append("text")
	.style("font-size", 11)
	.attr("x", function (d) {
		return (d3.timeWeek.count(d3.timeYear(d.date), d.date) - d3.timeWeek.count(d3.timeYear(d.date), startYear)) * cellSize
		 + (d3.timeMonth.count(d3.timeYear(d.date), d.date) - d3.timeMonth.count(d3.timeYear(d.date), startYear)) * 40
	})

	.attr("y", function (d) {
		var week_diff = formatWeek(d.date) - formatWeek(new Date(formatYear(d.date), formatMonth(d.date) - 1, 1));
		return (d.date.getDay() + 1) * cellSize - 5;
	})
	.text(function (d) {
		return formatDayOfMonth(d.date);
	}) 
    .style("pointer-events","none")
    .on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
		});

	rect.filter(function (d) {
		return d.sumval > 0;
	})
	.select("rect").style("fill", function (d) {
		//    console.log("Filtered in " + d.date);
		var max = 0;
		var mostinfluential;
		for (var k in d.sumvals) {
			if (d.sumvals[k] > max) {
				max = d.sumvals[k];
				mostinfluential = k;
			}
		}
		return color(k);

	})
    .on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
		})
		.on("click", function (d, i) {
            console.log("date is " + d.date);
            var old_date = new Date(d.date.getTime());
            var new_date = new Date(d.date.getTime());
            new_date.setDate(1);
			drawTooltipGraph(new_date, old_date,null,vargraphdata);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		})
	.select("title")
	.text(function (d) {
		return d + ": ";
	})
    		;

    /*
	rect.filter(function (d) {
		return d.sumval > 0;
	}).on("mouseover", mouseover);
	rect.filter(function (d) {
		return d.sumval > 0;
	}).on("mouseout", mouseout);
	function mouseover(d) {
		var html_content = "";

		for (var meta in d.stats) {
			for (var statistic in d.stats[meta]) {
				html_content += prettyKeys[statistic] + ": " + d.stats[meta][statistic][0] + "<br/>";
			}
		}

		div.transition()
		.duration(200)
		.style("opacity", .9);
		div.html(html_content)
		.style("left", (d3.event.pageX) + "px")
		.style("top", (d3.event.pageY - 28) + "px");
	}

	function mouseout(d) {
		div.transition()
		.duration(500)
		.style("opacity", 0);
	}
*/
	chartg.append("g")
	.attr("fill", "none")
	.attr("stroke", "#000")
	.selectAll("path")
	.data(function (d) {
		return d3.timeMonths(monthdates[0]['date'], monthdates[monthdates.length - 1]['date']);
	})
	.enter().append("path")
	.attr("d", pathMonth);

	var element = chartg.node();
	var elementwidth = element.getBoundingClientRect().width;
	var elementheight = element.getBoundingClientRect().height;
	zoom.translateExtent([[0, 0], [elementwidth, elementheight]])
	zoom.scaleBy(chartg, 1);
	chart.call(zoom);
}
function pathMonth(t0) {
	var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
	d0 = t0.getDay(),
	w0 = d3.timeWeek.count(d3.timeYear(t0), t0) - d3.timeWeek.count(d3.timeYear(t0), startYear)
		 + ((d3.timeMonth.count(d3.timeYear(t0), t0) - d3.timeMonth.count(d3.timeYear(t0), startYear)) * 40) / cellSize,
	d1 = t1.getDay(),
	w1 = d3.timeWeek.count(d3.timeYear(t1), t1) - d3.timeWeek.count(d3.timeYear(t1), startYear)
		 + ((d3.timeMonth.count(d3.timeYear(t1), t1) - d3.timeMonth.count(d3.timeYear(t1), startYear)) * 40) / cellSize;
	return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
	 + "H" + w0 * cellSize + "V" + 7 * cellSize
	 + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
	 + "H" + (w1 + 1) * cellSize + "V" + 0
	 + "H" + (w0 + 1) * cellSize + "Z";
}
function calendarsummer(total, num) {
	return total + num[1];
}
function sumStats(stats) {
	var sumStats = {};
	for (var k in stats) {
		sumStats[k] = Object.values(stats[k]).reduce(calendarsummer, 0);
	}
	return sumStats;
}