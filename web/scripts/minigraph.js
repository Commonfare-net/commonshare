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
	minig.attr("transform", d3.event.transform)
};
var zoom = d3.zoom()
	.scaleExtent([0.5, 2])
	.on("zoom", zoomFunction);

var chartdiv;
var minichart;
chartdiv = d3.select("#minigraph").attr("clip-path", "url(#mini-clip)"),
minichart = chartdiv.append("g");
minichart.append('defs').append("clipPath").attr("id", "mini-clip")
.append('ellipse')
.attr('cx', 100)
.attr('cy', 100)
.attr('rx', 85)
.attr('ry', 85);
mlabelsg = d3.select("#minilabels").append("g").attr("class", "minilabels");
minichart.append('ellipse')
.attr('cx', 100)
.attr('cy', 100)
.attr('rx', 85)
.attr('ry', 85)
.attr('fill', 'none')
.style('stroke', 'red')
.style('stroke-width', '4');
var textnode;
chartdiv.call(zoom);
var central_core;
minig = minichart.append("g").attr("class", "minipack");

function plotminigraph(mydata) {
	d3.select("#nodeg").remove();
	d3.select("#linkg").remove();
	$(".minilabels").html("");
	var links = minig.append("g").attr("id", "linkg").attr("stroke", "#000").selectAll(".link");
	var nodes = minig.append("g").attr("id", "nodeg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
	var minisim = d3.forceSimulation()
		.alphaDecay(0.05)
		.force("charge", d3.forceManyBody().strength(function (d) {
				return -300;
			}))
		.force('collision', d3.forceCollide().radius(function (d) {
				return d3.select("#circ" + d.id).attr("r");
			}))
		.force("link", d3.forceLink().distance(70).id(function (d) {
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
	$("#minigraph").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var width = 200,
	height = 200;

	nodes =
		nodes.data(mydata.nodes.filter(function(d){console.log(d);return d.type != "tag";}), function (d) {
			if (d.id == userid) {
				d.fx = width / 2;
				d.fy = height / 2;
				central_core = d.kcore;
			}

			return d.id;
		});

	nodes.exit().remove();

	nodes = nodes.enter().append("g").attr("class", "node")
		.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		})
		.attr("id", function (d) {
			return "n" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		});

	nodes.append('circle')
	.attr("r", function (d) {
		if (d.id == userid)
			return 1;
		return Math.max(d.kcore * 2 + 5, 16);
	})
	.attr("id", function (d) {
		return "circ" + d.id;
	})
	.attr("fill", function (d) {
		if (d.id == userid)
			return "none";
		return 'white';
		if (d.type == "commoner")
			return d3.color("steelblue");
		if (d.type == "listing")
			return d3.color("purple");
		if (d.type == "tag")
			return d3.color("lightgreen");
		return d3.color("red");
	})
	.attr("stroke", function (d) {
		if (d.id == userid)
			return "none";
		if (d.type == "commoner")
			return "#33a02c";
		if (d.type == "listing")
			return d3.color("purple");
		if (d.type == "tag")
			return d3.color("lightgreen");
		return "#1f78b4";
	})
	.attr("stroke-width", "3");

    links = links.data(mydata.links.filter(function(d){console.log(d);return "edgemeta" in d;}), function (d) {
			if (d.source.id == undefined)
				return d.source + "-" + d.target;
			return d.source.id + "-" + d.target.id;
		});
	links.exit().remove();
	links = links.enter().append("g");

	linklines = links.append("line")
		.attr("class", "line")
		.attr("id", function (d) {
			if (d.source.id == undefined)
				return d.source + "-" + d.target;
			return d.source.id + "-" + d.target.id;
		})
		.attr("stroke-width", 3)
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", function (d) {
			var nodetouse;
			if (d.source.id != undefined && d.source.id != userid)
				nodetouse = d.source.id;
			else if (d.target.id != undefined && d.target.id != userid)
				nodetouse = d.target.id;
			else if (d.source != userid)
				nodetouse = d.source;
			else
				nodetouse = d.target;
			return d3.select("#circ" + nodetouse).attr("stroke");
		});
	minisim.nodes(mydata.nodes.filter(function(d){console.log(d);return d.type != "tag";})).on("tick", ticked);
	minisim.force("link").links(mydata.links.filter(function(d){console.log(d);return "edgemeta" in d;}));
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
			var numicons = 0;
			if ("conversation" in d && d["conversation"].length > 0)
				numicons++;
			if ("transaction" in d && d["transaction"].length > 0)
				numicons++;

			if ("conversation" in d && d["conversation"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return numicons == 2 ? -24 : -12
				}).attr('y', -15)
				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceconversation.png");
			if ("transaction" in d && d["transaction"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return numicons == 2 ? 0 : -12
				}).attr('y', -15)

				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcetransaction.png");
		} else if (interacting_type == "story") { //Creations and comments
			var numicons = 0;
			if ("create_story" in d && d["create_story"].length > 0)
				numicons++;
			if ("comment_story" in d && d["comment_story"].length > 0)
				numicons++;
			if ("create_story" in d && d["create_story"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return numicons == 2 ? -4 : -12
				}).attr('y', -15)

				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceauthorstory.png");
			if ("comment_story" in d && d["comment_story"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return numicons == 2 ? -20 : -12
				}).attr('y', -15)

				.attr('width', 20).attr('height', 23)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcecommentstory.png")
		} else if (interacting_type == "listing") { //Creations and comments
			var numicons = 0;
			if ("create_listing" in d && d["create_listing"].length > 0)
				numicons++;
			if ("comment_listing" in d && d["comment_listing"].length > 0)
				numicons++;
			if ("create_listing" in d && d["create_listing"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return numicons == 2 ? -4 : -12
				}).attr('y', -15)

				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceauthorlisting.png");
			if ("comment_listing" in d && d["comment_listing"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image").attr('x', function () {
					return numicons == 2 ? -20 : -12
				}).attr('y', -15)

				.attr('width', 20).attr('height', 23)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcecommentlisting.png")
		}
		d3.select("#n" + interacting_node)
		.on("mouseover", function (d) {
		//	infotooltip.transition()
		//	.duration(200)
		//	.style("opacity", .9);
			if (d.type == "commoner") {
				nodename = d.name;
		//		infotooltip.style("background", "lightgrey");
				labelToHighlight = "#minicommonerlabel";
			} else if (d.type == "story") {
				nodename = d.title;
		//		infotooltip.style("background", "pink");
				labelToHighlight = "#ministorylabel";
			} else if (d.type == "listing") {
				nodename = d.title;
		//		infotooltip.style("background", "mediumpurple");
				labelToHighlight = "#minilistinglabel";
			}
			d3.select(this).select('circle').style("filter", "url(#glow)");
			d3.select(this).style("cursor", "pointer");
			d3.select(labelToHighlight).style("fill", "#E7472E");
			$("#minidescription").html("<h5 class='overlay'>" + nodename + "</h5>");

		})
		.on("mouseout", function (d) {
			d3.select(this).select('circle').style("filter", "")
			d3.select(labelToHighlight).style("fill", nodecolor(d.type));
			$("#minidescription").html("");
		})
        .on("click",function(d){
            if(d.type == 'commoner')
                nodename = d.label.split('_')[1];
            var url = getUrl(d.type,nodename);
          //  var win = window.open(url, '_blank');
        })
        ;

	});
    var nodename;
	var labelToHighlight;
	mlabelsg.append("path")
	.attr("id", "mcirclepath") //Unique id of the path
	.attr("d", "M 45,35 A 90,90 0 0,1 165,35") //png path
	.style("fill", "none")
	.style("stroke", "none");

	mlabelsg.append("path")
	.attr("id", "mlistingpath") //Unique id of the path
	.attr("d", "M 150,195 A 90,90 0 0,0 200,75") //png path
	.style("fill", "none")
	.style("stroke", "none");

	mlabelsg.append("path")
	.attr("id", "msocialpath") //Unique id of the path
	.attr("d", "M 10,75 A 90,90 0 0,0 70,195") //png path
	.style("fill", "none")
	.style("stroke", "none");
	var blabels = mlabelsg.append("text")
		.attr("class", "labeltext")

		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#mcirclepath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("commoners")
		.attr("id", "minicommonerlabel")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
			d3.select(this).style("fill", "#E7472E");
		})
		.on("mouseout", function (d) {
			d3.select(this).style("fill", nodecolor("commoner"));
		})
		.style("fill", nodecolor("commoner"))

		var blistinglabels = mlabelsg.append("text")
		.attr("class", "labeltext")
		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#mlistingpath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("listings")
		.attr("id", "minilistinglabel")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
			d3.select(this).style("fill", "#E7472E");

		})
		.on("mouseout", function (d) {
			d3.select(this).style("fill", nodecolor("listing"));
		})
		.style("font-size", "18px")
		.style("fill", nodecolor("listing"))
		.style("font-weight", "bold");

	var bsociallabels = mlabelsg.append("text")
		.attr("class", "labeltext")

		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#msocialpath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("stories")
		.attr("id", "ministorylabel")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
			d3.select(this).style("fill", "#E7472E");

		})
		.on("mouseout", function (d) {
			d3.select(this).style("fill", nodecolor("story"));
		})
		.style("font-size", "18px")
		.style("fill", nodecolor("story"))
		.style("font-weight", "bold");
	function ticked() {
		linklines
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

		nodes.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		});
	}
	d3.select("#minitext").remove();
	var minitextnode = minig.append("text")
		.attr("id", "minitext")
		.attr("stroke", "white")
		.attr("text-anchor", "middle")
		.style("font-family", "'Dosis', sans-serif")
		.attr("x", 100);

	minitextnode.style("font-size", Math.max(50, central_core * 3 + 6) + "px")
	.text(central_core);
	minitextnode.attr("y", 100 + (minitextnode.node().getBoundingClientRect().height / 4));

}
