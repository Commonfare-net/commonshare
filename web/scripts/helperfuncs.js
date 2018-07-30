var prettyKeys = {
	"create_story": "Wrote this story",
	"comment_story": "Left a comment",
	"rcomment_story": "Received a comment",
	"create_listing": "Created this listing",
	"comment_listing": "Left a comment",
	"rcomment_listing": "Received a comment",
	"transaction": "Completed a transaction",
	"rtransaction": "Completed a transaction",
	"conversation": "Started a conversation",
	"rconversation": "Started a conversation"
};
var color; //The colour scale, gets set in the simple line part and then used everywhere else
var mykeys = [];

var parseTime = d3.timeParse("%Y/%m/%d");
var formatDate = d3.timeFormat("%b-%y");
var anotherFormat = d3.timeFormat("%b'%y");
var tooltipFormat = d3.timeFormat("%b %d");
var urlParams = new URLSearchParams(window.location.search);
var userid = urlParams.get('userid'); // "edit"
var datafilecounter = 1;
var drawn = {};
var data = {};
var node_data = {};
var graph_data = {};
var numticks = 0;
function monthLetter(date) {
  var str = formatDate(date);
  return str.substr(0,2);
}   
//Tooltip functions from http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
var div = d3.select("body").append("div")
	.attr("class", "tooltip").style("width", "150px").style("height", "150px")
	.style("opacity", 0);

var infotooltip = d3.select("body").append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);
var overtooltip = false;
var overnode = false;

var divsvg = div.append("svg").attr("width", 150).attr("height", 150),
link = divsvg.append("g").attr("stroke", "#000").selectAll(".link"),
node = divsvg.append("g").attr("id", "nodeg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node"),
width = +divsvg.attr("width"), height = +divsvg.attr("height");
function findNode(node) {
	return node['id'] == userid;
}
//From https://stackoverflow.com/questions/38224875/replacing-d3-transform-in-d3-v4/38230545#38230545
function getTranslation(transform) {

	var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
	g.setAttributeNS(null, "transform", transform);
	var matrix = g.transform.baseVal.consolidate().matrix;

	return [matrix.e, matrix.f];
}

//Updates to make on simulation 'tick'
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

	node
	.attr("cx", function (d) {
		return d.x;
	})
	.attr("cy", function (d) {
		return d.y;
	});
}

function drawTooltipGraph(date, filtertype, graphindex,vargraphdata) {
    console.log("filter type is " + filtertype);
	if (graphindex != null) {
		personalgraph = vargraphdata[node_data[graphindex].date]
	} else {
		personalgraph = vargraphdata[date];
	}
	console.log(personalgraph);

	var nodes_to_show = [];
    var central_data;
	node = node.data(personalgraph.nodes, function (d) {
			if (d.id == userid) {
				d.fx = width / 2;
				d.fy = height / 2;
                central_data = d;
			}
			return d.id;
		});

	link = link.data(personalgraph.links, function (d) {
			return d.source.id + "-" + d.target.id;
		});
	console.log(node);
	console.log(link);
	node.exit().remove();
	node = node.enter().append("circle")
		.merge(node)
		.attr("id", function (d) {
			return "n" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		})
		.attr("r", function (d) {
			return (d.kcore * 2) + 5;
		})
		.attr("fill", function (d) {
			if (d.id == userid)
				return d3.color("orange");
			if (d.type == "commoner")
				return d3.color("steelblue");
			if (d.type == "listing")
				return d3.color("purple");
			if (d.type == "tag")
				return d3.color("lightgreen");
			return d3.color("red");
		})
        .style("opacity", function(d) { //Make nodes and links transparent if they aren't linked to tags
            if(d.nodemeta.includes(filtertype) || filtertype == "all")
                return 1; 
            return 0.15;
        }) 
        .on("mouseover",function(d){
            console.log(central_data);
            var statsdata = "";
            for(var key in central_data.stats){
                if(key == d.id){
                    console.log(central_data.stats[key]);
                    for(var i = 0; i < central_data.stats[key].length; i++){ // in central_data.stats[key]){
                       statsdata += tooltipFormat(parseTime(central_data.stats[key][i][1])) + ": " + prettyKeys[central_data.stats[key][i][0]] + "</br>"; 
                    }
                }
            }
            overnode = true;
            infotooltip.transition()        
                .duration(200)      
                .style("opacity", .9); 
            var name;
            if(d.type == "commoner" || d.type=="tag"){
                name = "<b>" + d.name + "</b>";
                infotooltip.style("background", "lightsteelblue");
            }
            else{
                name = "<b>" + d.title + "</b>";
                infotooltip.style("background", "pink");    
            }
            infotooltip.html(name + "</br><div>" + statsdata + "</div>")  
                   .style("left", (d3.event.pageX) + "px")     
                   .style("top", (d3.event.pageY - 28) + "px")
        })
        .on("mouseout",function(d){
             overnode = false;
             infotooltip.transition()        
            .duration(500)      
            .style("opacity", 0); 
        })
        ;
	link.exit().remove();
	link = link.enter().append("line")
		.attr("class", "line")
        .attr("id",function(d){return d.source.id + "-" + d.target.id;})
		.merge(link).attr("stroke-width", function (d) {
			if (typeof d.edgeweight !== "undefined") {
				var sum = 0;
				for (var key in d.edgeweight) {
					if (d.edgeweight.hasOwnProperty(key)) {
						sum = d.edgeweight[key];
                        console.log("Sum is now " + sum);
					}
				};
				return Math.sqrt(sum);
			}
			return 1.5;
		})
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", "green")
            .style("opacity", function(d) {
            if(d.edgemeta.includes(filtertype) || filtertype == "all")
                return 1; 
            return 0.15;
        
    });
	var simulation = d3.forceSimulation()
		.alphaDecay(0.05)
		.nodes(personalgraph.nodes)
		.force("charge", d3.forceManyBody().strength(function (d) {
				return -300;
			}))
		.force("link", d3.forceLink().distance(50).iterations(10).id(function (d) {
				return d.id;
			})) //Need the function here to draw links between nodes based on their ID rather than their index
		.force("x", d3.forceX().x(function (d) {
				if (d.kcore == 0)
					return 100;
				return width / 2;
			}).strength(function (d) {
				if (d.kcore == 0)
					return 0.4;
				return 0.1;
			}))
		.force("y", d3.forceY().y(function (d) {
				if (d.kcore == 0)
					return 100;
				return height / 2;
			}).strength(function (d) {
				if (d.kcore == 0)
					return 0.4;
				return 0.1;
			}))
		.on("tick", ticked);
	// Update and restart the simulation.
	simulation.force("link").links(personalgraph.links);

	var element = d3.select("#nodeg").node();
	var elementwidth = element.getBoundingClientRect().width;
	var elementheight = element.getBoundingClientRect().height;
	console.log("width and height are " + elementwidth + "," + elementheight);
}
