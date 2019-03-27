var chartsvg = d3.select("#lgraph");
var x = d3.scaleTime().rangeRound([40, chartsvg.attr('width') * 3]);
var y = d3.scaleLinear().range([$("#lgraph").height() - 20, 20]);
var valueline = d3.area()
	.x(function (d) {
		return x(parseTime(d.date));
	})
	.y0(y(0))
	.y1(function (d) {
		return y(+d[plotType]);
	});
var plotType;
var data = {};
var datalist = []; //Adding this for the line graph, might not be necessary
var drawn = {};
var xScale = d3.scaleLinear()
	.domain([0, 500]).range([0, 500]);
var yScale = d3.scaleLinear()
	.domain([0, 600]).range([0, 600]);
var dateslider;
var dateslidex;
var slideradded = false;
var q = d3.queue();
var datafilecounter = 0;
var taglistindex;
var indexstart = 0;
var strengthslider = 0;
var tag;
var filtertype;
var filternodetype;
var c_nodes = [];
var global_communities = {};
var ids_to_titles = {};
var parseTime = d3.timeParse("%Y/%m/%d %H:%M");
var formatWeek = d3.timeFormat("%d/%m/%y");
function zoomFunction() {
	var new_xScale = d3.event.transform.rescaleX(xScale);
	var new_yScale = d3.event.transform.rescaleY(yScale);
	g.attr("transform", d3.event.transform)
};
var zoom = d3.zoom().on("zoom", zoomFunction);
var svg = d3.select("#bigvis"), width = +svg.attr("width"), height = +svg.attr("height");
svg.call(zoom);
var g = svg.append("g").attr("transform", "translate(250,250) scale (.35,.35)");
extrashit = g.append("g").attr("z-index", -3);
link = g.append("g").attr("stroke", "#000").attr("stroke-width", 1.5).selectAll(".link"),
node = g.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
convexHull = g.append("path").attr("class", "hull");
svg.call(zoom.transform, d3.zoomIdentity.translate(250, 250).scale(0.35));
var simulation = d3.forceSimulation()
	.force("link", d3.forceLink().id(function (d) {
			return d.id;
		}))
     .force('collision', d3.forceCollide().radius(function(d) {
    return 20;
  }))
	.force("charge", d3.forceManyBody().strength(-300))
	.force("x", d3.forceX().x(width / 2).strength(0.1))
	.force("y", d3.forceY().y(height / 2).strength(0.1))
	.stop();
var community_sim = d3.forceSimulation()
	.force("charge", d3.forceManyBody().strength(-10))
	.force("link", d3.forceLink().id(function (d) {
			return d.id;
		}).strength(0))
	.force('center', d3.forceCenter(500 / 2, 600 / 2))
	.force('cluster', forceCluster)
	.force('collide', d3.forceCollide(22).strength(0.9))
	.stop();
var active_simulation = simulation;
//Tooltip functions from http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
var div = d3.select("body").append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);
//https://stackoverflow.com/questions/1584370/how-to-merge-two-arrays-in-javascript-and-de-duplicate-items
Array.prototype.unique = function () {
	var a = this.concat();
	for (var i = 0; i < a.length; ++i) {
		for (var j = i + 1; j < a.length; ++j) {
			if (a[i] === a[j])
				a.splice(j--, 1);
		}
	}
	return a;
};
var plotpath;

fillcolour = {
	"listings": ["purple", "yellow"],
	"commoners": ["steelblue", "darkblue"],
	"stories": ["red", "darkgreen"],
	"tags": ["green", "yellow"],
	"convo": ["orange", "darkblue"],
	"trans": ["darkblue", "steelblue"],
	"create": ["darkred", "orange"],
	"comment": ["red", "green"]
};
axistext = {
	"listings": "Active listings",
	"commoners": "Active Commoners",
	"stories": "Active stories",
	"tags": "Tags used",
	"convo": "Conversations started",
	"trans": "Transactions made",
	"create": "Stories written",
	"comment": "Story comments"
};

$("#lgraph").bind("wheel mousewheel", function (e) {
	e.preventDefault()
});
chartg = chartsvg.append("g"); //.attr("transform", "translate(30,20)");

var areazoom = d3.zoom()
	.scaleExtent([0.33, 2])
	.translateExtent([[0, 0], [chartsvg.attr('width') * 3 + 50, chartsvg.attr("height")]])
	.on('zoom', areazoomed);
var currentMonthGap = 1;

function newplot(type) {
	if (type == '')
		return;
	plotType = type;
	chartg.select(".yline").remove();
	chartg.select(".plotline").remove();
	chartg.selectAll(".dots").remove();

	$("#ylabel").text(axistext[type]);
	y.domain([0, d3.max(datalist, function (d) {
				return isNaN(d[plotType]) ? 0 : +d[plotType];
			})]);
	// Add the valueline path.
	plotpath = chartg.append("path")
		.data([datalist])
		.attr("fill", fillcolour[plotType][0])
		.attr("opacity", 0.5)
		.attr("stroke-width", 1.5)
		.attr("class", "plotline")
		.attr("d", valueline);
	chartg.append("g")
	.attr('class', 'yline')
	.attr("transform", "translate(40,0)")
	.call(d3.axisLeft(y));
	dots = chartg.selectAll(".dots")
		.data(datalist)
		.enter().append("circle")
		.attr("class", "dots")
		.style("fill", function (d) {
			if (d.date == currentDate)
				return fillcolour[plotType][1];
			return fillcolour[plotType][0];
		})
		.attr("r", function (d) {
			if (d.date == currentDate)
				return 6;
			return 4;
		})
		.attr("cx", valueline.x())
		.attr("cy", function (d) {
			return y(+d[plotType]);
		})
		.on("mouseover", function (d) {
			d3.select(this).attr("r", 8);
			d3.select(this).style("cursor", "pointer");
			div.transition()
			.duration(200)
			.style("opacity", .9);
			div.html(d.date + "</br>" + d[plotType])
			.style("left", (d3.event.pageX - 38) + "px")
			.style("top", (d3.event.pageY - 50) + "px")
			.style("background", "transparent");

		})
		.on("mouseout", function (d) {
			d3.select(this).attr("r", 4);
			div.transition()
			.duration(500)
			.style("opacity", 0);
		})
}
function clearDyn() {
	d3.select('.hull').attr('d', 0);
	d3.selectAll(".marker").remove();
	c_nodes = [];
	draw();
}
function toggletags(checkboxelem) {
	if (checkboxelem.checked) {
		node.each(function (d) {
			if (d.type == 'tag')
				d3.select(this).style('opacity', 0);
		});
		link.each(function (d) {
			if (d.source.type == 'tag' || d.target.type == 'tag')
				d3.select(this).style("opacity", 0);
		});
	} else {
		node.each(function (d) {
			if (d.type == 'tag')
				d3.select(this).style('opacity', 1);
		});
		link.each(function (d) {
			if (d.source.type == 'tag' || d.target.type == 'tag')
				d3.select(this).style("opacity", 1);
		});
	}
}
function toggledate(checkboxelem) {
	clearDyn();
	if (checkboxelem.checked) {
		$("#curdate").text(formatWeek(parseTime(data[Object.keys(data).length - 1].date)) + " to " + formatWeek(parseTime(data[1].date)));
		$('#myslider').css('opacity', 0.4);
		$('#myslider').css('pointer-events', 'none');
		currentDate = data[1].date;
		sliderhandle.attr("cx", dateslidex(Object.keys(data).length - 1));
		indexstart = 0;
		draw();
	} else {
		$("#curdate").text(formatWeek(parseTime(data[1].date)) + " to " + formatWeek(d3.utcDay.offset(parseTime(data[1].date), 7)));
		$('#myslider').css('opacity', 1);
		$('#myslider').css('pointer-events', 'auto');
		indexstart = 1;
		draw();
	}
}
function togglegroups(checkboxelem) {
	if (checkboxelem.checked)
		active_simulation = community_sim;
	else
		active_simulation = simulation;

	active_simulation.nodes(graph.nodes);
	active_simulation.force("link").links(graph.links);
	active_simulation.alpha(1);
	for (var i = 0, n = Math.ceil(Math.log(active_simulation.alphaMin()) / Math.log(1 - active_simulation.alphaDecay())); i < n; ++i) {
		active_simulation.tick();
	}
	node
	.transition()
	.duration(2000)
	.attr("cx", function (d) {
		return d.x;
	})
	.attr("cy", function (d) {
		return d.y;
	})
	link
	.transition()
	.duration(2000)
	.attr("x1", function (d) {
		return d.source.x;
	})
	.attr("y1", function (d) {
		return d.source.y;
	})
	.attr("x2", function (d) {
		return d.target.x;
	})
	.attr("y2", function (d) {
		return d.target.y;
	});

	extrashit.selectAll(".extralines")
	.transition()
	.duration(2000)
	.attr("x1", function (d) {
		return d.source.x;
	})
	.attr("y1", function (d) {
		return d.source.y;
	})
	.attr("x2", function (d) {
		return d.target.x;
	})
	.attr("y2", function (d) {
		return d.target.y;
	});
	if (indexstart == 0) {
		var hull = d3.polygonHull(c_nodes.map(function (d) {
					return [d3.select("#n" + indexstart + "_" + d).datum().x, d3.select("#n" + indexstart + "_" + d).datum().y];
				}));
		convexHull.datum(hull);
		convexHull
		.transition()
		.duration(2000)
		.attr("d", function (d) {
			return "M" + d.join("L") + "Z";
		});
	}
}
function getTranslation(transform) {
	var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
	g.setAttributeNS(null, "transform", transform);
	var matrix = g.transform.baseVal.consolidate().matrix;
	return [matrix.e, matrix.f];
}
function areazoomed() {
	//   if(plotpath == undefined)return;
	var xz = d3.event.transform.rescaleX(x);
	gX.call(xAxis.scale(xz));
	//Recalculate tick numbers
	var selection = $("#simplelineaxis > .tick");
    if(selection.length == 0)
        return;
	var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;
	if (tickdistance < 50)
		currentMonthGap++;
	else if (tickdistance > 100)
		currentMonthGap--;
	xAxis.ticks(d3.timeMonth.every(Math.max(1, currentMonthGap)));
	d3.selectAll("#simplelineaxis > .tick").attr("transform", function () {
		return "translate(" + (getTranslation(d3.select(this).attr("transform"))[0]) + ",0)";
	});
	d3.selectAll(".dots").attr("cx", function (d) {
		return xz(parseTime(d.date));
	})
	valueline.x(function (d) {
		return xz(parseTime(d.date));
	});
	if (plotpath == undefined)
		return;
	plotpath.attr("d", valueline);

}

function loadDataFiles(queue) {
	var url = "../data/output/graphdata/yearly/" + datafilecounter + ".json";
	$.ajax({
		url: url,
		type: 'HEAD',
		error: function () {
			queue.awaitAll(function (error, results) {
				if (error)
					throw error;
				else {
					for (var i = 0; i < results.length; i++) {
						data[i] = results[i];
						if (i > 0)
							datalist[i - 1] = results[i];
						drawn[i] = false;
					}
					datalist.reverse();
					// Scale the range of the data
					x.domain(d3.extent(datalist, function (d) {
							return parseTime(d.date);
						}));
					y.domain([0, d3.max(datalist, function (d) {
								return isNaN(d.stories) ? 0 : +d.stories;
							})]);
					plotType = 'stories';
					// Add the valueline path.
					var anotherFormat = d3.timeFormat("%b'%y");
					xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(1));
					// Add the X Axis
					gX = chartg.append("g")
						.attr("id", "simplelineaxis")
						.attr("transform", "translate(0," + ($("#lgraph").height() - 20) + ")")
						.call(xAxis);
					// Add the Y Axis
					gY = chartg.append("g")
						.attr('class', 'yline')
						.attr("transform", "translate(40,0)")
						.call(d3.axisLeft(y));

					chartsvg.append("text")
					.attr("transform", "rotate(-90)")
					.attr("y", 0)
					.attr("x", 0 - ($("#lgraph").height() / 2))
					.attr("dy", "1em")
					.attr("id", "ylabel")
					.style("text-anchor", "middle")
					.style("font-family", "Calibri")
					.style("font-weight", "bold")
					.text("");
					draw();
					if (slideradded == false) {
						addDateSlider();
						addStrengthSlider();
						sliderhandle.attr("cx", dateslidex(Object.keys(data).length - 1));
					} else {
						sliderhandle.attr("cx", dateslidex(Object.keys(data).length - 1));
						d3.selectAll(".ticktext")
						.style("fill", "black")
						.style("font-weight", "normal");
					}
					indexstart = 1;
					draw();

				}
			});
		},
		success: function () {
			queue.defer(d3.json, url);
			datafilecounter++;
			loadDataFiles(queue);
		}
	});
}
loadDataFiles(q);
function forceCluster(alpha) {
	node.each(function (d) {
		cluster = clusters[d.cluster];
		if (cluster === d)
			return;
		let x = d.x - cluster.x,
		y = d.y - cluster.y,
		l = Math.sqrt(x * x + y * y),
		r = d.kcore + cluster.kcore;
		if (l != r) {
			l = (l - r) / l * alpha;
			d.x -= x *= l;
			d.y -= y *= l;
			cluster.x += x;
			cluster.y += y;
		}
	});
}
function draw() {
	$(".mybox").prop('checked', false);
	nodetypes = {};
	//https://stackoverflow.com/questions/11347779/jquery-exclude-children-from-text
	$.fn.ignore = function (sel) {
		return this.clone().find(sel || ">*").remove().end();
	};
	graph = data[indexstart];
	communities = graph.communities;
	$('#nodenums').text(graph.node_num);
	$('#edgenums').text(graph.edge_num);
	$('#commoners').text(graph.commoners);
	$('#stories').text(graph.stories);
	$('#listings').text(graph.listings);
	$('#tags').text(graph.tags);
	$('#convos').text(graph.convo);
	$('#transactions').text(graph.trans);
	$('#written').text(graph.create);
	$('#comments').text(graph.comment);
	selected_node = "";
	var maxval = 0;
	node = node.data(graph.nodes, function (d) {
			return d.id + indexstart;
		});
	link = link.data(graph.links, function (d) {
			return d.source.id + "-" + d.target.id;
		});
	tagcounts = graph.tagcount;
	dc = graph.dynamic_comms;
	var colluders = "colluders" in graph ? graph.colluders : [];
    var trusted = "trusted" in graph ? graph.trusted : [];
    var untrusted = "untrusted" in graph ? graph.untrusted : [];
	for (var comm in dc) {
		global_community = [];
		dates = [];
		for (var i = 0; i < dc[comm].length; i += 2) {
			dates.push(dc[comm][i]);
		}
		for (var i = 1; i < dc[comm].length; i += 2) {
			global_community = global_community.concat(dc[comm][i]);
		}
		global_communities[comm] = [global_community.unique(), dates];
	}
	var commContainer = $('#comm-group');
	var commMembers = $('#comm-members');
	commContainer.empty();
	for (var comm in global_communities) {
		commContainer.append('<a href="#" class="list-group-item community">' + comm + '</a>')
	}
	$('.community').click(function (e) {
		e.preventDefault();
		commMembers.empty();
		d3.selectAll(".marker").remove();
		name = $(this).text();
		c_nodes = global_communities[name][0];
		for (var i = 0; i < c_nodes.length; i++) {
			commMembers.append('<a href="#" class="list-group-item community">' + ids_to_titles[c_nodes[i]] + '</a>')
		}
		for (var x = 0; x < global_communities[name][1].length; x++) {
			var date = global_communities[name][1][x];
			dateslider.append('path')
			.attr('d', function (d) {
				var x = dateslidex(Object.keys(data).length - date - 1),
				y = -10;
				return 'M ' + x + ' ' + y + ' l -4 -8 l 8 0 z';
			})
			.attr('class', 'marker');
		}
		if (indexstart == 0) {
			var hull = d3.polygonHull(c_nodes.map(function (d) {
						return [d3.select("#n" + indexstart + "_" + d).attr("cx"), d3.select("#n" + indexstart + "_" + d).attr("cy")];
					}));
			convexHull.datum(hull).attr("d", function (d) {
				return "M" + d.join("L") + "Z";
			});
		} else {
			draw();
		}
	});
	var listContainer = $('#list-group');
	if (taglistindex != indexstart) {
		taglistindex = indexstart;
		listContainer.empty();
        if(tagcounts != null){
            for (var i = 0; i < tagcounts.length; i++) {
                var tagname = tagcounts[i][0];
                var tagnum = tagcounts[i][1];
                listContainer.append('<a href="#" class="list-group-item taga">' + tagname + '<span class="badge">' + tagnum + '</span></a>');
            }
        }
		$('.taga').click(function (e) {
			e.preventDefault();
			filtertype = "tag";
			tag = $(this).ignore("span").text(); // or var clickedBtnID = this.id
			draw();
			return false;
		});
	}
	node.exit().transition()
	.attr("r", 0)
	.remove();
	node = node.enter().append("circle")
		.call(d3.drag()
			.on("start", dragstarted)
			.on("drag", dragged)
			.on("end", dragended))
		.merge(node)
		.each(function (d) {
			nodetypes[d.id] = d.type;
			if (isNaN(d.maxweight))
				d.maxweight = 0;
			maxval = Math.max(maxval, d.maxweight);
		})
		.attr("id", function (d) {
			return "n" + indexstart + "_" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		})
		.attr("r", function (d) {
			if (c_nodes.indexOf(d.id) > -1)
				return 20;
			return (d.kcore * 2) + 5;
		})
		.attr("stroke", function (d) {
			if (d.type == "commoner")
				return d3.color("steelblue");
			if (d.type == "listing")
				return d3.color("purple");
			if (d.type == "tag")
				return d3.color("green");
			return d3.color("red");
		})
		.attr("stroke-width", function (d) {
			for (var i = 0; i < colluders.length; i++) {
				if (colluders[i].includes(d.id))
					return 4;
			}
			if (c_nodes.indexOf(d.id) > -1)
				return 7;
			return 0;
		})
		.attr("fill", function (d) {
			for (var i = 0; i < colluders.length; i++) {
				if (colluders[i].includes(d.id))
					return d3.color("darkred");
			}
            if (trusted.indexOf(d.id) > -1)
                return d3.color("blue");
            if (untrusted.indexOf(d.id) > -1)
                return d3.color("red");
			if (c_nodes.indexOf(d.id) > -1)
				return d3.color("orange");
			if (d.type == "commoner")
				return d3.color("steelblue");
			if (d.type == "listing")
				return d3.color("purple");
			if (d.type == "tag")
				return d3.color("green");
			return d3.color("purple");
		}) //Coloured based on their type
		.style("opacity", function (d) { //Make nodes and links transparent if they aren't linked to tags
            if (trusted.length > 0){
                if (trusted.indexOf(d.id) > -1 || untrusted.indexOf(d.id) > -1)
                    return 1;
                return 0;
            }
			if (d.maxweight < strengthslider)
				return 0;
			if (filtertype == "tag") {
				if (tag == "all" || (d.type == "tag" && d.name == tag) || d.tags.includes(tag))
					return 1;
				return 0.15;
			} else if (filtertype == "network") {
				if (tag == "all" || d.nodemeta.includes(tag))
					return 1;
				return 0.15;
			} else {
				return 1;
			}
		})
		.on("click", function (od) {
			window.open('../html/personal_viz.html?userid=' + od.id, '_blank');
		})
		//Node and link highlighting
		.on("mouseover", function (d) {
			selected_node = d.id;
			d3.select(this).attr("fill", d3.color("orange"));
			sourcelinks = link.filter(function (d) {
					return d.source.id == selected_node || d.target.id == selected_node;
				});
                message = "";
			sourcelinks.each(function (d) {
                
                if(selected_node == d.source.id){
                    message += (d.target.id + ' weight: ' + d.edgeweight[d.source.id] + "<br/>");
                }
                else{
                    message += (d.source.id + ' weight: ' +  d.edgeweight[d.target.id] + "<br/>");
                }
				d3.select(this).attr("oldstrokeval", d3.select(this).style("stroke-width"));
				d3.select(this).attr("oldcolourval", d3.select(this).style("stroke"));
				d3.select(this).style("stroke", 'green');
			});
			//Add the tooltips, formatted based on whether they represent a user or story
			div.transition()
			.duration(200)
			.style("opacity", .9);
			/*if (d.type == "commoner" || d.type == "tag") {
				div.html(d.name + "</br>" + d.kcore)
				.style("left", (d3.event.pageX) + "px")
				.style("top", (d3.event.pageY - 28) + "px")
				.style("background", function () {
					if (d.type == "commoner")
						return "lightsteelblue";
					return "green";
				});
			} else {*/
                if(d.label == null)d.label = d.id;
				div.html("label: " + d.label + ". commonshare: " + d.kcore + "<br/>" + message)
				.style("left", (d3.event.pageX) + "px")
				.style("top", (d3.event.pageY - 28) + "px")
				.style("background", "lightsteelblue");
			//}
		})
		.on("mouseout", function (d) {
			//Set the colour of links back to black, and the thickness to its original value
			d3.select(this).attr("fill", function (d) {
				for (var i = 0; i < colluders.length; i++) {
					if (colluders[i].includes(d.id))
						return d3.color("darkred");
				}
                if (trusted.indexOf(d.id) > -1)
                return d3.color("blue");
            if (untrusted.indexOf(d.id) > -1)
                return d3.color("red");
				if (c_nodes.indexOf(d.id) > -1)
					return d3.color("orange");
				if (d.type == "commoner")
					return d3.color("steelblue");
				if (d.type == "listing")
					return d3.color("purple");
				if (d.type == "tag")
					return d3.color("green");
				return d3.color("purple");
			});
			sourcelinks.each(function (d) {
				d3.select(this).style("stroke", d3.select(this).attr("oldcolourval"));
			});
			sourcelinks.each(function (d) {
				d3.select(this).style("stroke-width", d3.select(this).attr("oldstrokeval"));
			});
			div.transition()
			.duration(500)
			.style("opacity", 0);
		});
	updateStrengthSlider(strengthslider, maxval);
	if (indexstart == 0)
		for (var comm in global_communities) {
			nodeids = global_communities[comm][0];
			for (var i = 0; i < nodeids.length; i++) {
				var nodedata = d3.select("#n0_" + nodeids[i]).datum();
				if ('name' in nodedata)
					ids_to_titles[nodeids[i]] = nodedata['name'];
				else
					ids_to_titles[nodeids[i]] = nodedata['title'];
			}
		}
	//Arrowheads that show the direction of the interaction. Have to be drawn manually
	svg.selectAll("defs").remove();
	svg.append("defs").selectAll("marker")
	.data(graph.links)
	.enter().append("marker")
	.each(function (d) {
		if ('create_story' in d || 'create_listing' in d)
			d.size = 2;
		else
			d.size = 1;
	})
	.attr("id", function (d) {
		return "mend" + d.source.id + "-" + d.target.id;
	})
	.attr("viewBox", function (d) {
		if (d.size == 2)
			return "0 -10 20 20";
		return "0 -5 10 10"
	})
	.attr("refX", function (d) {
		if (d.target.id == null)
			return 10;
		if (d3.select("#n" + indexstart + "_" + d.target.id).empty())
			return 10;
		radius = d3.select("#n" + indexstart + "_" + d.target.id).attr("r");
		return (d.size * 10) + parseInt(radius);
	})
	.attr("markerUnits", "userSpaceOnUse")
	.attr("markerWidth", function (d) {
		return d.size * 10;
	})
	.attr("markerHeight", function (d) {
		return d.size * 10;
	})
	.attr("orient", "auto")
	.append("path")
	.attr("d", function (d) {
		if (d.size == 2)
			return "M0,-10L20,0L0,10";
		return "M0,-5L10,0L0,5"
	})
	.style("stroke", function (d) {
		if (d.size == 2)
			return "darkred";
		return "white";
	})
	.style("stroke-width", function (d) {
		if (d.size == 2)
			return 3;
		return 0;
	})
	.style("fill", function (d) {
		if (d.size == 2)
			return 'darkred';
		if (c_nodes.indexOf(d.source.id) > -1 && c_nodes.indexOf(d.target.id) > -1)
			return 'orange';
		if ('edgemeta' in d && d.edgemeta.includes('story'))
			return 'red';
		if ('edgemeta' in d && d.edgemeta.includes('social'))
			return 'orange';
		if ('edgemeta' in d && d.edgemeta.includes('listing'))
			return 'purple';
		if ('edgemeta' in d && d.edgemeta.includes('transaction'))
			return 'darkblue';
		return 'black';
	})
    .on('mouseover',function(d){
        console.log('messages sent: ' + d.initiated[d.target.id] + ', messages received: ' + d.initiated[d.source.id]);
    });
	svg.append("defs").selectAll("marker")
	.data(graph.links)
	.enter().append("marker")
	.each(function (d) {
		if ('create_story' in d || 'create_listing' in d)
			d.size = 2;
		else
			d.size = 1;
	})
	.attr("id", function (d) {
		return "mstart" + d.source.id + "-" + d.target.id;
	})
	.attr("viewBox", function (d) {
		if (d.size == 2)
			return "-20 -10 20 20";
		return "-10 -5 10 10"
	})
	.attr("refX", function (d) {
		if (d.source.id == null)
			return 10;
		if (d3.select("#n" + indexstart + "_" + d.source.id).empty())
			return 10;
		radius = d3.select("#n" + indexstart + "_" + d.source.id).attr("r");
		return  - (d.size * 10) - parseInt(radius);
	})
	.attr("markerUnits", "userSpaceOnUse")
	.attr("markerWidth", function (d) {
		return d.size * 10;
	})
	.attr("markerHeight", function (d) {
		return d.size * 10;
	})
	.attr("orient", "auto")
	.append("path")
	.attr("d", function (d) {
		if (d.size == 2)
			return "M0,-10L-20,0L0,10";
		return "M0,-5L-10,0L0,5"
	})
	.style("stroke", function (d) {
		if (d.size == 2)
			return "darkred";
		return "white";
	})
	.style("stroke-width", function (d) {
		if (d.size == 2)
			return 3;
		return 0;
	})
	.style("fill", function (d) {
		if (d.size == 2)
			return 'darkred';
		if (c_nodes.indexOf(d.source.id) > -1 && c_nodes.indexOf(d.target.id) > -1)
			return 'orange';
		if ('edgemeta' in d && d.edgemeta.includes('story'))
			return 'red';
		if ('edgemeta' in d && d.edgemeta.includes('social'))
			return 'orange';
		if ('edgemeta' in d && d.edgemeta.includes('listing'))
			return 'purple';
		if ('edgemeta' in d && d.edgemeta.includes('transaction'))
			return 'darkblue';
		return 'black';
	});
    ;

	link.exit()
	.remove();
	link = link.enter().append("line")
		.attr("class", "line")
		.merge(link)
		.attr("stroke-width", function (d) {
			if ('tag_story' in d || 'tag_commoner' in d || 'tag_listing' in d)
				return 0.25;
			//if ('create_story' in d || 'create_listing' in d)
			//		return 4.5;
			if ('edgemeta' in d && d.edgemeta.includes('social') && d.edgemeta.includes('transaction'))
				return 3;
			if ('edgeweight' in d){
                //return 1;
                return Math.min(8, d.edgeweight[d.source.id]);
            }
			return 2;
		})
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", function (d) {
			if (c_nodes.indexOf(d.source.id) > -1 && c_nodes.indexOf(d.target.id) > -1)
				return 'orange';
			if ('edgemeta' in d && d.edgemeta.includes('story'))
				return 'red';
			if ('edgemeta' in d && d.edgemeta.includes('social') && d.edgemeta.includes('transaction')) //Needs to be brigher
				return '#FFC31E';
			if ('edgemeta' in d && d.edgemeta.includes('social'))
				return 'orange';
			if ('edgemeta' in d && d.edgemeta.includes('listing'))
				return 'purple';
			if ('edgemeta' in d && d.edgemeta.includes('transaction'))
				return 'darkblue';
			//return 'black';
            //Let's try and add some sort of HSV colouring in here
            vals = [];
            for (var key in d.edgeweight){
                vals.push(d.edgeweight[key]);
            }
            var saturation = Math.max(20,80-d.maxweight);
            return "hsl(0,100%," + saturation +"%)";
		})
		.style("stroke-dasharray", function (d) {
			if ('edgemeta' in d && d.edgemeta.includes('social') && d.edgemeta.includes('transaction'))
				return "20,10";
			return 0;
		})
		.attr("marker-end", function (d) {
      //      if(d.edgeweight[d.source.id] != undefined){
		//		return "url(#mend" + d.source.id + "-" + d.target.id + ")";
          //  }
			return null;
		})
		.attr("marker-start", function (d) {
          // if(d.edgeweight[d.target.id] != undefined){
			//	return "url(#mstart" + d.source.id + "-" + d.target.id + ")";
           //}
            return null;
		})
		.style("opacity", function (d) {
            if (trusted.length > 0){
                if( (trusted.indexOf(d.source.id) > -1 || untrusted.indexOf(d.source.id) > -1) &&
                    (trusted.indexOf(d.target.id) > -1 || untrusted.indexOf(d.target.id) > -1))
                    return 1;
                return 0;
            }
			if ('maxweight' in d && d.maxweight < strengthslider || (strengthslider > 0 && d.maxweight == undefined))
				return 0;
			if (filtertype == "tag") {
				if (tag == "all" || (d.source.type == "tag" && d.source.name == tag) || (d.target.type == "tag" && d.target.name == tag))
					return 1;
				return 0.15;
			} else if (filtertype == "network") {
				if (tag == "all" || (d.edgemeta != null && d.edgemeta.includes(tag)))
					return 1;
				return 0.15;
			} else {
				return 1;
			}
		});
	function ticked() {
		link
		.attr("x1", function (d) {
			return d.source.x;
		})
		.attr("y1", function (d) {
			return d.source.y;
		})
		.attr("x2", function (d) {
			return d.target.x;
		})
		.attr("y2", function (d) {
			return d.target.y;
		});
		extrashit.selectAll(".extralines")
		.attr("x1", function (d) {
			return d.source.x;
		})
		.attr("y1", function (d) {
			return d.source.y;
		})
		.attr("x2", function (d) {
			return d.target.x;
		})
		.attr("y2", function (d) {
			return d.target.y;
		});
		node
		.attr("cx", function (d) {
			return d.x;
		})
		.attr("cy", function (d) {
			return d.y;
		});
	}
	//Dragging functions
	function dragstarted(d) {
		d3.event.sourceEvent.stopPropagation();
		d.fx = d.x;
		d.fy = d.y;
	}
	function dragged(d) {
		d.fx = d3.event.x;
		d.fy = d3.event.y;
		d.x = d3.event.x;
		d.y = d3.event.y;
		ticked();
	}
	function dragended(d) {
		d.fx = null;
		d.fy = null;
	}
	// Update and restart the simulation.
	active_simulation.nodes(graph.nodes);
	clusters = {};
	node.each(function (d) {
		var radius = d.kcore;
		var clusterID = d.cluster;
		if (!clusters[clusterID] || (radius > clusters[clusterID].kcore)) {
			clusters[clusterID] = d;
		}
	});
	active_simulation.force("link").links(graph.links);
	if (drawn[indexstart] == false) {
		drawn[indexstart] = true;
		active_simulation.alpha(1);
        
		for (var i = 0, n = Math.ceil(Math.log(active_simulation.alphaMin()) / Math.log(1 - active_simulation.alphaDecay())); i < n; ++i) {
			active_simulation.tick();
		}
		if ((datafilecounter - 1) > (indexstart + 1)) {
			indexstart++;
			draw();
		} else {
			datafilecounter = 1;
		}
	}
	link
	.attr("x1", function (d) {
		return d.source.x;
	})
	.attr("y1", function (d) {
		return d.source.y;
	})
	.attr("x2", function (d) {
		return d.target.x;
	})
	.attr("y2", function (d) {
		return d.target.y;
	});
	node
	.attr("cx", function (d) {
		return d.x;
	})
	.attr("cy", function (d) {
		return d.y;
	});

	extrashit.selectAll(".extralines").remove();

	extrashit.selectAll(".extralines")
	.data(graph.links.filter(function (d) {
			return 'edgemeta' in d && d.edgemeta.includes('social') && d.edgemeta.includes('transaction');
		})) //Add the links. Thickness is currently determined by the square root of the sum of the weight from either node
	.enter().append('line')
	.attr('class', 'extralines')
	.style('stroke', 'darkblue')
	.attr('stroke-width', 2)
	.attr('z-index', -5)
	.style("opacity", function (d) {
		if (d.maxweight < strengthslider || (strengthslider > 0 && d.maxweight == undefined))
			return 0;
		if (filtertype == "tag") {
			if (tag == "all" || (d.source.type == "tag" && d.source.name == tag) || (d.target.type == "tag" && d.target.name == tag))
				return 1;
			return 0.15;
		} else if (filtertype == "network") {
			if (tag == "all" || (d.edgemeta != null && d.edgemeta.includes(tag)))
				return 1;
			return 0.15;
		} else {
			return 1;
		}
	})
	.attr("x1", function (d) {
		return d.source.x;
	})
	.attr("y1", function (d) {
		return d.source.y;
	})
	.attr("x2", function (d) {
		return d.target.x;
	})
	.attr("y2", function (d) {
		return d.target.y;
	});
	$('#loadingDiv').css('display', 'none');
	//chartsvg.call(areazoom.transform, d3.zoomIdentity.translate(0, 0).scale(0.33));
	//newplot(plotType);
}
$('#cleartags').click(function (e) {
	e.preventDefault();
	tag = "all";
	draw();
	return false;
});
$('#clearnw').click(function (e) {
	e.preventDefault();
	tag = "all";
	draw();
	return false;
});
$('#cleardyn').click(function (e) {
	e.preventDefault();
	clearDyn();
});
//chartsvg.call(areazoom.transform, d3.zoomIdentity.translate(0,0).scale(0.33));