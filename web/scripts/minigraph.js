//Updates to make on simulation 'tick'

var xScale = d3.scaleLinear()
	.domain([0, 200]).range([0, 200]);
var yScale = d3.scaleLinear()
	.domain([0, 200]).range([0, 200]);

function getBoundingBoxCenterX(selection) {
	var element = selection.node();
	var bbox = element.getBBox();
	return bbox.x + bbox.width / 2;
}
//Zooming function
function zoomFunction() {
	var center = getBoundingBoxCenterX(chartdiv); //rect is the charts parent which expands while zooming
	var chartsWidth = (2 * center) * d3.event.transform.k;
	d3.event.transform.x = center - chartsWidth / 2;
	d3.event.transform.y = center - chartsWidth / 2;
	minichart.attr("transform", d3.event.transform)
};
var zoom = d3.zoom()
	.scaleExtent([0.5, 2])
	.on("zoom", zoomFunction);

var chartdiv;
var minichart;
chartdiv = d3.select("#minigraph"),
minichart = chartdiv.append("g");
var textnode;
chartdiv.call(zoom);
var central_core;
var minisim = d3.forceSimulation()
	.alphaDecay(0.05)
	.force("charge", d3.forceManyBody().strength(function (d) {
			return -300;
		}))
	.force("link", d3.forceLink().distance(60).iterations(10).id(function (d) {
			return d.id;
		})) //Need the function here to draw links between nodes based on their ID rather than their index
	.force("x", d3.forceX().x(function (d) {
			return 100;
		}).strength(function (d) {
			if (d.kcore == 0)
				return 0.4;
			return 0.1;
		}))
	.force("y", d3.forceY().y(function (d) {
			return 100;
		}).strength(function (d) {
			if (d.kcore == 0)
				return 0.4;
			return 0.1;
		}));
var links = minichart.append("g").attr("stroke", "#000").selectAll(".link");
var nodes = minichart.append("g").attr("id", "nodeg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
var minitextnode = minichart.append("text")
	.attr("stroke", "white")
	.attr("text-anchor", "middle")
	.style("font-family", "'Dosis', sans-serif")
	.attr("x", 100);
function plotminigraph(mydata) {

	$("#minigraph").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var width = 200,
	height = 200,
	color = d3.scaleOrdinal()
		.range(["#7A99AC", "#E4002B"]);

	nodes =
		nodes.data(mydata.nodes, function (d) {
			if (d.id == userid) {
				d.fx = width / 2;
				d.fy = height / 2;
				central_core = d.kcore;
			}

			return d.id;
		});

	nodes.exit().remove();

	nodes = nodes.enter().append("circle").attr("class", "node")
		.attr("id", function (d) {
			return "n" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		})
		.attr("r", function (d) {
			return d.kcore * 2 + 5;
		})
		.attr("fill", function (d) {
			if (d.id == userid)
				return d3.color("white");
			if (d.type == "commoner")
				return d3.color("steelblue");
			if (d.type == "listing")
				return d3.color("purple");
			if (d.type == "tag")
				return d3.color("lightgreen");
			return d3.color("red");
		})
		.on("mouseout", function (d) {
			infotooltip.transition()
			.duration(500)
			.style("opacity", 0);
		});

	links = links.data(mydata.links, function (d) {
			return d.source.id + "-" + d.target.id;
		});
	links.exit().remove();
	links = links.enter().append("line")
		.attr("class", "line")
		.attr("id", function (d) {
			return d.source.id + "-" + d.target.id;
		})
		.attr("stroke-width", function (d) {
			if (typeof d.edgeweight !== "undefined") {
				var sum = 0;
				for (var key in d.edgeweight) {
					if (d.edgeweight.hasOwnProperty(key)) {
						sum = d.edgeweight[key];
					}
				};
				return Math.sqrt(sum);
			}
			return 1.5;
		})
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", "green");
	minisim.nodes(mydata.nodes).on("tick", ticked);
	minisim.force("link").links(mydata.links);
	minisim.alpha(1).restart();

	links.each(function (d) {
		var interacting_node;
		var interacting_type;
		//Who and what is this interacting node?
		if (d.source.id == userid) {
			interacting_node = d.target.id;
			interacting_type = d.target.type;
		} else if (d.target.id == userid) {
			interacting_node = d.source.id;
			interacting_type = d.source.type;
		} else {
			return;
		}
		var interaction_data = "";
		//Find the relevant interactions between them
		if (interacting_type == "commoner") { //Transactions and conversations
			if ("conversation" in d)
				interaction_data += "Had a conversation</br>";
			if ("transaction" in d)
				interaction_data += "Completed transactions</br>";
		} else if (interacting_type == "story") { //Creations and comments
			if ("create_story" in d)
				interaction_data += "Wrote this story</br>";
			if ("comment_story" in d)
				interaction_data += "Left a comment</br>";
		} else if (interacting_type == "listing") { //Creations and comments
			if ("create_listing" in d)
				interaction_data += "Created this listing</br>";
			if ("comment_listing" in d)
				interaction_data += "Left a comment</br>";
		}
		d3.select("#n" + interacting_node)
		.on("mouseover", function (d) {
			infotooltip.transition()
			.duration(200)
			.style("opacity", .9);
			var name;
			if (d.type == "commoner") {
				name = "<b>" + d.name + "</b>";
				infotooltip.style("background", "lightsteelblue");
			} else if (d.type == "story") {
				name = "<b>" + d.title + "</b>";
				infotooltip.style("background", "pink");
			} else if (d.type == "listing") {
				name = "<b>" + d.title + "</b>";
				infotooltip.style("background", "lightpurple");
			}
			infotooltip.html(name + "</br><div>" + interaction_data + "</div>")
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px")
		});

	});
	function ticked() {
		links
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

		nodes
		.attr("cx", function (d) {
			return d.x;
		})
		.attr("cy", function (d) {
			return d.y;
		});
	}

	minitextnode.style("font-size", Math.max(50, central_core * 3 + 6))
	.text(central_core);
	minitextnode.attr("y", 100 + (minitextnode.node().getBoundingClientRect().height / 4));

}
