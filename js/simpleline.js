// Calculate initialwidth
var boxWidth = $("#linechartdiv").innerWidth();
$("#linechart").attr("width", boxWidth);

$(window).resize(function () {
	boxWidth = $("#linechartdiv").innerWidth();
	$("#linechart").attr("width", boxWidth);

})

function plotsimpleline(user) {
    console.log("HOW MANY TIMES");
	$("#linechart").on("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	//http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
	var tooltip_div = d3.select("body").append("div")
		.attr("class", "tooltip");

	//Positioning of divs programmatically
	var margin = {
		top: 50,
		right: 20,
		bottom: 150,
		left: 50
	},
	chart = d3.select("#linechart"),
	chartwidth = +chart.attr("width") - margin.left - margin.right,
	chartheight = +chart.attr("height") - margin.top - margin.bottom,
	chartg = chart.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	chart.append('rect')
	.attr('id', 'captureRect')
	.attr('class', 'captureoverlay')
	.attr('width', chartwidth)
	.attr('height', chartheight)
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	.on('mousemove', mousemove)
    .on('mouseout',mouseout);

	var x = d3.scaleTime()
		.rangeRound([0, chartwidth * 2]);
	var y = d3.scaleLinear()
		.rangeRound([chartheight, 0]);
	var zoom = d3.zoom()
		.scaleExtent([0.5, 2])
		.translateExtent([[0, 0],
				[chartwidth * 2 + 50, chart.attr("height")]])
		.on('zoom', zoomed);

	var currentMonthGap = 1;
	var transform;

	//Zooming and translation function
	//Repositions lines and adjusts x-axis tick spacing
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
			return "translate(" + (t + 20) + ",0)";
		});

		kcoreline.x(function (d) {
			return xz(d.date) + 20;
		});

		linepath.attr("d", kcoreline);
		line.x(function (d) {
			return xz(d.date) + 20;
		})
		metapath.attr("d", function (d) {
			return line(d.values);
		});
	}

	var line = d3.line()
		.x(function (d) {
			return x(d.date) + 20;
		})
		.y(function (d) {
			return y(d.total);
		});

	var kcoreline = d3.line()
		.x(function (d) {
			return x(d.date) + 20;
		})
		.y(function (d) {
			return y(d.kcore);
		});

	var kcorelist = []
	var avg_total_object = []
	for (var month in data) {
		var avg_totals = node_data[month].cumu;
		if (avg_totals == null) {
			for (var name in keys) {
				if (!(keys[name]in avg_total_object)) {
					avg_total_object[keys[name]] = [];
				}
				avg_total_object[keys[name]].push({
					"id": keys[name],
					"stats": {},
					"date": node_data[month].date,
					"total": 0
				});
			}
		} else {
			for (var name in avg_totals) {
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
			};
		}
		node_data[month].kcore = +node_data[month].kcore;
		kcorelist.push({
			"date": node_data[month].date,
			"kcore": node_data[month].kcore
		});
	}

	var avgdata_list = Object.keys(avg_total_object).map(function (k) {
			return {
				"id": k,
				"date": node_data[month].date,
				"values": avg_total_object[k]
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
	y.domain([
			d3.min(kcorelist, function (d) {
				return d.kcore;
			}),
			d3.max(kcorelist, function (d) {
				return d.kcore;
			})
		]);

	var meta = chartg.selectAll('.meta')
		.data(avgdata_list)
		.enter().append("g")
		.attr("class", "meta");

	//Lines for social/stories/transactions/listings
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
		})
		.style("stroke-width", 2);

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
	var xAxis = d3.axisBottom(x).tickFormat(tickf).ticks(d3.timeMonth.every(1));
	var gX = chartg.append("g")
		.attr("transform", "translate(0," + chartheight + ")")
		.attr("class", "axis")
		.attr("id", "simplelineaxis")
		.call(xAxis);
	d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
		var t = getTranslation(d3.select(this).attr("transform"))[0];
		return "translate(" + (t + 20) + ",0)";
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
	.style("font-size", "14px")

	//Styling and positioning of the legend
	//http://zeroviscosity.com/d3-js-step-by-step/step-3-adding-a-legend
	var legendRectSize = 15;
	var legendSpacing = 6;
	var opacity = 1;
	var legend = chartg.selectAll(".legend")
		.data(keys)
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
		})
        .each(function(d){
        })
        ;

	legend.append('circle')
	.attr('r', legendRectSize / 2)
	.style('fill', 'none')
	.style('stroke', color)
	.style('stroke-width', 2);

	legend.append('text')
	.attr('x', legendRectSize / 2 + legendSpacing)
	.attr('y', legendRectSize / 1.4 - legendSpacing)
	.text(function (d) {
		if (lang == "hr")
			return croatiantranslate(d);
		if (lang == "it")
			return italiantranslate(d);
		return d;
	});

	legend.attr('xpos', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 240;
		var width = legendRectSize + legendSpacing;
		var horz = 50 + elementwidth * i;
		return horz;
	});
	legend.attr('ypos', 275);
	legend.attr('transform', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 240;
		var width = legendRectSize + legendSpacing;
		var horz = 5 + i % 2 * elementwidth;
		var vert = 295 + parseInt(i / 2) * 35;
		return 'translate(' + (horz) + ',' + vert + ')';
	});

	legend.each(function (d) {
		d3.select('body')
		.append('div')
		.style('position', 'absolute')
		.style('left', d3.select(this).node().getBoundingClientRect().x + "px")
		.style('top', (d3.select(this).node().getBoundingClientRect().y + 20) + "px")
		.attr('id', 'info' + d)
		.attr('class', 'infodiv');
	});

	function legendclick(d) {
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

	previousIndex = 0;

	//Story/social/transaction/listing circles that appear on hover
	chart.selectAll(".metacircles")
	.data(keys)
	.enter()
	.append("circle")
	.attr("class", "metacircles")
	.attr("id", function (d) {
		return "metacircle_" + d
	})
	.attr("r", 4)
	.style("fill", function (d) {
		return color(d)
	});

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
		return node['id'] == otheruser;
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
		var xt = transform.rescaleX(x),
		yt = transform.rescaleY(y);
		var x0 = xt.invert(d3.mouse(this)[0]),
		i = bisectDate(node_data, x0);
		if (previousIndex == i) {
			return;
		}
        
		previousIndex = i;
		d1 = node_data[i];
		//Auto-update the donut
		currentdonut = i;
		plotdonut(graph_data[i], node_data[i]);
		d3.selectAll(".metacircles")
		.attr("cx", xt(d1.date) + margin.left + 20)
		.attr("cy", function (d) {
			if ("cumu" in d1) {
				return y(d1.cumu[d]) + margin.top;
			}
			return y(0) + margin.top;
		})
        .style("pointer-events","none");

		var chartpos = d3.select("#linechart").node().getBoundingClientRect();
		tooltip_div.transition()
		.duration(200)
		.style("opacity", 1);
		console.log(d1);
		var toolTipText = "";
		var interaction_types =
			['create_story', 'create_listing',
			'comment_story', 'comment_listing',
			'conversation', 'transaction'];
		for (var i = 0; i < interaction_types.length; i++) {
			var type = interaction_types[i];
			if (type in d1 && d1[type].length > 0) {
				toolTipText += tooltipTranslate(type) +
				d1[type].length + "</br>";
			}
		}
		tooltip_div.html(toolTipText)
		.style("left", (xt(d1.date) + margin.left + 30 + chartpos.x) + "px")
		.style("top", (y(d1.kcore) + margin.top - 20 + chartpos.y) + "px");
		//Update the commonshare circle position and text
		d3.select("#commonshare_circle")
		.attr("cx", xt(d1.date) + margin.left + 20)
		.attr("cy", y(d1.kcore) + margin.top)
        .style("pointer-events","none");

		d3.select("#commonshare_text")
		.attr("x", xt(d1.date) + margin.left + 20)
		.attr("y", y(d1.kcore) + margin.top - 10)
		.html("")
		.text(d1.kcore)
        .style("pointer-events","none");

	}

	chart.call(zoom);
	chart.call(zoom.scaleBy, 2);
	chart.call(zoom.translateBy,  - (chart.attr('width') * 2), 0);
}
