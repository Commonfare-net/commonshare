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

function plotminigraph(mydata) {
	d3.select("#nodeg").remove();
	d3.select("#linkg").remove();
	var links = minichart.append("g").attr("id", "linkg").attr("stroke", "#000").selectAll(".link");
	var nodes = minichart.append("g").attr("id", "nodeg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
	var minisim = d3.forceSimulation()
		.alphaDecay(0.05)
		.force("charge", d3.forceManyBody().strength(function (d) {
				return -300;
			}))
            .force('collision', d3.forceCollide().radius(function(d) {
    return d3.select("#circ"+d.id).attr("r");
  }))
		.force("link", d3.forceLink().distance(80).id(function (d) {
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
		nodes.data(mydata.nodes, function (d) {
			if (d.id == userid) {
				d.fx = width / 2;
				d.fy = height / 2;
				central_core = d.kcore;
			}

			return d.id;
		});

	console.log(nodes);
	nodes.exit().remove();

	nodes = nodes.enter().append("g").attr("class", "node")
		.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		})
		.attr("id", function (d) {
            console.log("PERSON DATA");
			return "n" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		});

	nodes.append('circle')
	.attr("r", function (d) {
        		if (d.id == userid)
                    return 1;
		return Math.max(d.kcore * 2 + 5,16);
	})
    .attr("id", function (d) {
            console.log("PERSON DATA");
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
    .attr("stroke", function(d){
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
    .attr("stroke-width","3")
	.on("mouseout", function (d) {
		infotooltip.transition()
		.duration(500)
		.style("opacity", 0);
	});

	links = links.data(mydata.links, function (d) {
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
		.attr("stroke-width", function (d) {
			/*if (typeof d.edgeweight !== "undefined") {
				var sum = 0;
				for (var key in d.edgeweight) {
					if (d.edgeweight.hasOwnProperty(key)) {
						sum = d.edgeweight[key];
					}
				};
				return Math.sqrt(sum);
			}*/
			return 3;
		})
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", function(d){
             var nodetouse;
             if(d.source.id != undefined && d.source.id != userid)
                 nodetouse = d.source.id;
             else if(d.target.id != undefined && d.target.id != userid)
                 nodetouse = d.target.id;
             else if(d.source != userid)
                 nodetouse = d.source;
             else
                 nodetouse = d.target;
             console.log(nodetouse);
             console.log(d3.select("#circ"+nodetouse).attr("r"));
             return d3.select("#circ"+nodetouse).attr("stroke");
        });
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
            var numicons = 0;
			if ("conversation" in d && d["conversation"].length > 0)
                numicons++;
 			if ("transaction" in d && d["transaction"].length > 0)
                numicons++;
            
			if ("conversation" in d && d["conversation"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
                .attr('x',function(){return numicons == 2 ? -24 : -12}).attr('y',-15)
				.attr('width', 25).attr('height', 30)
				.attr('class','linkimage').attr("xlink:href", "icons/forceconversation.svg");
			if ("transaction" in d && d["transaction"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
				                .attr('x',function(){return numicons == 2 ? 0 : -12}).attr('y',-15)

                .attr('width', 25).attr('height', 30)
				.attr('class','linkimage').attr("xlink:href", "icons/forcetransaction.svg");
		} else if (interacting_type == "story") { //Creations and comments
                    var numicons = 0;
			if ("create_story" in d && d["create_story"].length > 0)
                numicons++;
 			if ("comment_story" in d && d["comment_story"].length > 0)
                numicons++;
			if ("create_story" in d && d["create_story"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
                                .attr('x',function(){return numicons == 2 ? -24 : -12}).attr('y',-15)

				.attr('width', 25).attr('height', 30)
				.attr('class','linkimage').attr("xlink:href", "icons/forceauthorstory.svg");
			if ("comment_story" in d && d["comment_story"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
                                .attr('x',function(){return numicons == 2 ? 0 : -12}).attr('y',-15)

				.attr('width', 20).attr('height', 23)
				.attr('class','linkimage').attr("xlink:href", "icons/forcecommentstory.svg")
		} else if (interacting_type == "listing") { //Creations and comments
                    var numicons = 0;
			if ("create_listing" in d && d["create_listing"].length > 0)
                numicons++;
 			if ("comment_listing" in d && d["comment_listing"].length > 0)
                numicons++;
			if ("create_listing" in d && d["create_listing"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")
                                .attr('x',function(){return numicons == 2 ? -24 : -12}).attr('y',-15)

				.attr('width', 25).attr('height', 30)
				.attr('class','linkimage').attr("xlink:href", "icons/forceauthorlisting.svg");
			if ("comment_listing" in d && d["comment_listing"].length > 0)
				d3.select("#n" + interacting_node)
				.append("svg:image")                .attr('x',function(){return numicons == 2 ? 0 : -12}).attr('y',-15)

				.attr('width', 20).attr('height', 23)
				.attr('class','linkimage').attr("xlink:href", "icons/forcecommentlisting.svg")
		}
		d3.select("#n" + interacting_node)
		.on("mouseover", function (d) {
			infotooltip.transition()
			.duration(200)
			.style("opacity", .9);
			var name;
			if (d.type == "commoner") {
				name = "<b>" + d.name + "</b>";
				infotooltip.style("background", "lightgrey");
			} else if (d.type == "story") {
				name = "<b>" + d.title + "</b>";
				infotooltip.style("background", "pink");
			} else if (d.type == "listing") {
				name = "<b>" + d.title + "</b>";
				infotooltip.style("background", "mediumpurple");
			}
			infotooltip.html(name + "</br><div>" + interaction_data + "</div>")
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px")
		})
        .on("mouseout", function (d) {
			infotooltip.transition()
			.duration(500)
			.style("opacity", 0);
		});

	});
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
		/*		.attr("cx", function (d) {
		return d.x;
		})
		.attr("cy", function (d) {
		return d.y;
		});*/
	}
	d3.select("#minitext").remove();
	var minitextnode = minichart.append("text")
		.attr("id", "minitext")
		.attr("stroke", "white")
		.attr("text-anchor", "middle")
		.style("font-family", "'Dosis', sans-serif")
		.attr("x", 100);

	minitextnode.style("font-size", Math.max(50, central_core * 3 + 6))
	.text(central_core);
	minitextnode.attr("y", 100 + (minitextnode.node().getBoundingClientRect().height / 4));

}
