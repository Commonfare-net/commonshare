//Ensure all JSON files are loaded before initiating visualisation
d3.json('../data/output/userdata/' + userid + '.json', function (results) {
	data = results;
	for (var fortnight = 0; fortnight < results.length; fortnight++) {
		node_data[fortnight] = results[fortnight]['nodes'].find(findNode);
		node_data[fortnight].date = parseTime(node_data[fortnight].date);
		graph_data[fortnight] = results[fortnight];
	}

	numticks = results.length;
	plotsimpleline(userid);
});

function plotsimpleline(user) {

	var margin = {
		top: 50,
		right: 20,
		bottom: 70,
		left: 50
	},
	chart = d3.select("#linechart"),
	chartwidth = +chart.attr("width") - margin.left - margin.right,
	chartheight = +chart.attr("height") - margin.top - margin.bottom,
	chartg = chart.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")

		chart.append('rect')
		.attr('id', 'captureRect')
		.attr('class', 'captureoverlay')
		.attr('width', chartwidth)
		.attr('height', chartheight)
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
		.on('mousemove', mousemove);

	$("#linechart").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

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
	function zoomed() {
		transform = d3.event.transform;
		var xz = d3.event.transform.rescaleX(x);
		gX.call(xAxis.scale(xz));
		d3.selectAll(".metacircles")
		.attr("cx", -10)
		.attr("cy", -10);
		d3.select("#kcorecircle")
		.attr("cx", -10)
		.attr("cy", -10);
		d3.select("#kcoretext")
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
		})
		.style("stroke-width", 2);

	var linepath = chartg.append("path")
		.datum(kcorelist)
		.attr("class", "mypath")
		.attr("clip-path", "url(#clip)")
		.attr("d", kcoreline)
		.style("stroke", "#E7472E")
		.style("stroke-width", 3);

	var clip = chartg.append("clipPath")
		.attr("id", "clip");
	var clipRect = clip.append("rect")
		.attr("width", chart.attr("width"))
		.attr("height", chart.attr("height"))
		.attr("y", -10)

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

	chartg.append("g")
	.attr("class", "axis")
	.call(d3.axisLeft(y).ticks(4))
	.append("text")
	.attr("fill", "#000")
	.attr("transform", "rotate(-90)")
	.attr("y", -10)
	.attr("x", 0)
	.attr("dy", "-1em")
	.attr("text-anchor", "end")
	.text("Commonshare")
	.style("font-size", "20px");

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

	legend.append('circle')
	.attr('r', legendRectSize / 2)
	.style('fill', color)
	.style('stroke', color);

	legend.append('text')
	.attr('x', legendRectSize / 2 + legendSpacing)
	.attr('y', legendRectSize / 2 - legendSpacing)
	.text(function (d) {
		return d;
	});

	legend.attr('xpos', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 250;
		var width = legendRectSize + legendSpacing;
		var horz = 50 + elementwidth * i;
		return horz;
	});
	legend.attr('ypos', 275);
	legend.attr('transform', function (d, i) {
		var element = d3.select(this).node();
		var elementwidth = 250;
		var width = legendRectSize + legendSpacing;
		var horz = 50 + elementwidth * i;
		var vert = 275;
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
			d3.selectAll(".mydot" + d).style("visibility", "hidden");
			opacity = 0.5;
		} else {
			d3.selectAll("." + d).style("visibility", "visible");
			d3.selectAll(".mydot" + d).style("visibility", "visible");
			opacity = 1;
		}
	}

	previousIndex = 0;
	chart.selectAll(".metacircles")
	.data(keys)
	.enter()
	.append("circle")
	.attr("class", "metacircles")
	.attr("r", 4)
	.style("fill", function (d) {
		return color(d)
	});

	chart.append("circle")
	.attr("r", 6)
	.attr("id", "kcorecircle")
	.style("fill", "#E7472E");
	chart.append("text")
	.attr("id", "kcoretext");
	var bisectDate = d3.bisector(function (d, x) {
			return x - d.date;
		}).left;

	var otheruser;
	function findOtherNode(node) {
		return node['id'] == otheruser;
	}
	function mousemove() {
		var xt = transform.rescaleX(x),
		yt = transform.rescaleY(y);
		var x0 = xt.invert(d3.mouse(this)[0]),
		i = bisectDate(node_data, x0);
		if (previousIndex == i) {
			return;
		}
		previousIndex = i;
		d1 = node_data[i];
		d3.selectAll(".metacircles")
		.attr("cx", xt(d1.date) + margin.left + 20)
		.attr("cy", function (d) {
			if ("cumu" in d1) {
				return y(d1.cumu[d]) + margin.top;
			}
			return y(0) + margin.top;
		})
		.each(function (d) {
			d3.select("#info" + d).html("");
			var div_info = "";
			//Need to accumulate values for comments
			//Because of the JSON structure this isn't very nice right now
			trans_num = 0;
			r_comments = {};

			if ("cumu" in d1) {
				var keys = keytypes[d];
				for (var k = 0; k < keys.length; k++) {
					var actions_taken = d1[keys[k]];
					if (actions_taken == null) {
						continue;
					}
					for (var j = 0; j < actions_taken.length; j++) {
						var pair = actions_taken[j].split("-");
						if (pair[0] != userid) {
							otheruser = pair[0];
						} else {
							otheruser = pair[1];
						}
						user = graph_data[i]['nodes'].find(findOtherNode);
						if (keys[k] == "transaction") {
							trans_num++;
						} else if ((user.type == 'story' || user.type == 'listing') && otheruser == pair[0]) {
							if (user.t in r_comments) {
								r_comments[user.t]++;
							} else {
								r_comments[user.t] = 1;
							}
						} else {
							div_info += (prettyKeys[keys[k]] + user.t + "<br/><br/>");
						}
					}
				}
				if (trans_num > 0) {
					div_info += ("Completed " + trans_num + " transactions");
				}
				for (var story in r_comments) {
					div_info += ("Received " + r_comments[story] + " comments on " + story + "<br/><br/>");
				}
				d3.select("#info" + d).html(div_info);
			}
		});
		d3.select("#kcorecircle")
		.attr("cx", xt(d1.date) + margin.left + 20)
		.attr("cy", y(d1.kcore) + margin.top);
		var comtext = d3.select("#kcoretext")
			.attr("x", xt(d1.date) + margin.left + 20)
			.attr("y", y(d1.kcore) + margin.top - 10);
		comtext.html("");
		comtext.style("font-weight", "bold")
		.style("text-anchor", "middle")
		.style("fill", "#E7472E")
		.style("font-size", "20px")
		.style("font-family", "'Dosis', sans-serif")
		.text(d1.kcore);

	}
	chart.call(zoom);
	chart.call(zoom.scaleBy, 2);
	chart.call(zoom.translateBy,  - (chart.attr('width') * 2), 0);
}