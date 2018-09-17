
function zoomBunch() {
	var center = getBoundingBoxCenterX(bunchchart); //rect is the charts parent which expands while zooming
	var chartsWidth = (2 * center) * d3.event.transform.k;
	d3.event.transform.x = center - chartsWidth / 2;
	d3.event.transform.y = center - chartsWidth / 2;
	bunchg.attr("transform", d3.event.transform)
};
var bunchzoom = d3.zoom()
	.scaleExtent([0.5, 2])
	.on("zoom", zoomBunch);
bunchchart = d3.select("#bunches").attr("clip-path","url(#my-clip)");
labelsg = d3.select("#bunchlabels").append("g").attr("class", "bunchlabels");
bunchchart.append('defs').append("clipPath").attr("id", "my-clip")
	.append('ellipse')
    .attr('cx', 100)
    .attr('cy', 100)
    .attr('rx', 85)
    .attr('ry', 85);
bunchchart.append('ellipse')
    .attr('cx', 100)
    .attr('cy', 100)
    .attr('rx', 85)
    .attr('ry', 85)
    .attr('fill','none')
    .style('stroke','red')
    .style('stroke-width','4');
bunchg = bunchchart.append("g").attr('class', 'bunchpack');


     // give the clipPath an ID;
function plotbunches(mydata) {
	d3.select(".bunchpack").html("");
    d3.select(".bunchlabels").html("");
	d3.select("#bunchg").remove();
	d3.select("#bunchlinks").remove();
	$("#bunches").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var width = 200,
	height = 200;

	var innerwidth = 180;
	var innerheight = 180;

	bunchnode = bunchg.append("g").attr("id", "bunchg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
	bunchchart.call(bunchzoom);
	bunchlinks = bunchg.append("g").attr("id", "bunchlinks").selectAll(".link");

	bunchnode = bunchnode.data(mydata.nodes.filter(function(d){console.log(d);return d.type != "tag";}), function (d) {
			return d.id;
		});
	bunchnode.exit().remove();

    var labelToHighlight;
	bunchnode = bunchnode
		.enter().append("g")
		.attr("class", "node")
        
		.attr("transform", function (d) {
			return "translate(" + d.x + "," + d.y + ")";
		})
		.attr("type", function (d) {
			return d.type;
		})
		.attr("id", function (d) {
			return "bunch" + d.id
		})
		.on("mouseover", function (d) {
			infotooltip.transition()
			.duration(200)
			.style("opacity", .9);
			if (d.type == "commoner")
				nodename = d.name;
			else
				nodename = d.title;
			sourcetarget = "<b>" + nodename + "</b>";
            if (d.type == "commoner")
                labelToHighlight = "#bunchescommonerlabel";
            else if (d.type == "story") 
                labelToHighlight = "#bunchesstorylabel";             
			else if (d.type == "listing") 
                labelToHighlight = "#buncheslistinglabel";			
            
			infotooltip.style("background", "lightsteelblue");
            d3.select(this).select('circle').style("filter","url(#glow)");
            d3.select(this).style("cursor", "pointer");
            d3.select(labelToHighlight).style("fill", "#E7472E");
            /*
			infotooltip.html(sourcetarget + "</br><div>Commonshare: " + d.kcore + "</div>")
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px")*/
            $("#bunchesdescription").html("<h5 class='overlay'>"+nodename+"</h5>");
		})
		.on("mouseout", function (d) {
	//		infotooltip.transition()
		//	.duration(500)
			//.style("opacity", 0);
            d3.select(this).select('circle').style("filter","")
            d3.select(labelToHighlight).style("fill",nodecolor(d.type));            
            $("#bunchesdescription").html("");

		})
                .on("click",function(d){
            if(d.type == 'commoner')
                nodename = d.label.split('_')[1];
            var url = getUrl(d.type,nodename);
            var win = window.open(url, '_blank');
        })
			var nodename;

	bunchcircles = bunchnode
		.append("circle")
		.attr("r", function (d) {
			if (d.id == userid)
				return Math.max(d.kcore * 5, 20);
			return Math.max(d.kcore * 2, 15);
		})
		.attr("fill", function (d) {
			if (d.id == userid)
				return "orange";
			return 'white';
		})
		.attr("stroke", function (d) {
			if (d.id == userid)
				return "orange";
			if (d.type == "commoner")
				return "#33a02c";
			if (d.type == "listing")
				return d3.color("purple");
			return "#1f78b4";
		})
		.attr("stroke-width", "3")
        

	bunchlinks = bunchlinks.data(mydata.links.filter(function(d){console.log(d);return "edgemeta" in d;}), function (d) {
			if (d.source.id == undefined)
				return d.source + "-" + d.target;
			return d.source.id + "-" + d.target.id;
		});
	bunchlinks.exit().remove();

	bunchlinks = bunchlinks.enter().append("line")
		.attr("class", "line")
		.attr("id", function (d) {
			if (d.source.id == undefined)
				return d.source + "-" + d.target;
			return d.source.id + "-" + d.target.id;
		})
		.attr("stroke-width",3)
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
			return d3.select("#bunch" + nodetouse).attr("stroke");
		});

	textnode = bunchg.append("text")
		.attr("stroke", "white")
		.attr("text-anchor", "middle")
		.style("font-size", "48")
		.style("font-family", "'Dosis', sans-serif")
		.text(mydata.nodes.find(findNode).kcore)
		.style("pointer-events", "none");

	bunchlinks.each(function (d) {
		var interacting_node;
		var interacting_type;
		if (d.source.id == undefined) {
			//Who and what is this interacting node?
			if (d.source == userid) {
				interacting_node = d.target;
				interacting_type = d3.select("#bunch" + interacting_node).attr("type");
			} else if (d.target == userid) {
				interacting_node = d.source;
				interacting_type = d3.select("#bunch" + interacting_node).attr("type");
			}
		} else {
			if (d.source.id == userid) {
				interacting_node = d.target.id;
				interacting_type = d.target.type;
			} else if (d.target.id == userid) {
				interacting_node = d.source.id;
				interacting_type = d.source.type;
			}
		}
        var two_icons = false;
		//Wordy placement of the SVGs
		if (interacting_type == "commoner") { //Transactions and conversations
			if ("conversation" in d && d["conversation"].length > 0 && "transaction" in d && d["transaction"].length > 0)
				two_icons = true;
			if ("conversation" in d && d["conversation"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return two_icons ? -24 : -12
				}).attr('y', -15)
				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceconversation.png");
			if ("transaction" in d && d["transaction"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return two_icons ? 0 : -12
				}).attr('y', -15)
				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcetransaction.png");
		} else if (interacting_type == "story") { //Creations and comments
			if ("create_story" in d && d["create_story"].length > 0 && "comment_story" in d && d["comment_story"].length > 0)
				two_icons = true;
			if ("create_story" in d && d["create_story"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return two_icons ? -4 : -12
				}).attr('y', -15)
				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceauthorstory.png");
			if ("comment_story" in d && d["comment_story"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return two_icons ? -20 : -12
				}).attr('y', -15)
				.attr('width', 20).attr('height', 23)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcecommentstory.png")
		} else if (interacting_type == "listing") { //Creations and comments
			var numicons = 0;
			if ("create_listing" in d && d["create_listing"].length > 0 && "comment_listing" in d && d["comment_listing"].length > 0)
				two_icons = true;
			if ("create_listing" in d && d["create_listing"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image")
				.attr('x', function () {
					return two_icons ? -4 : -12
				}).attr('y', -15)
				.attr('width', 25).attr('height', 30)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forceauthorlisting.png");
			if ("comment_listing" in d && d["comment_listing"].length > 0)
				d3.select("#bunch" + interacting_node)
				.append("svg:image").attr('x', function () {
					return two_icons ? -20 : -12
				}).attr('y', -15)
				.attr('width', 20).attr('height', 23)
				.attr('class', 'linkimage').attr("xlink:href", "icons/forcecommentlisting.png")
		}
	});

	var simulation = d3.forceSimulation()
		.alphaDecay(0.05)
		.velocityDecay(0.2)

		.nodes(mydata.nodes.filter(function(d){console.log(d);return d.type != "tag";}))
		.force("collide", d3.forceCollide().radius(function (d) {
				if (d.id == userid)
					return Math.max(d.kcore * 5, 22);
				return Math.max(d.kcore * 2, 15);
			}).iterations(2))
		//Need the function here to draw links between nodes based on their ID rather than their index
		.force("x", d3.forceX().x(width / 2).strength(function (d) {
				if (d.id == userid)
					return 1;
				return 0.2;
			}))
		.force("y", d3.forceY().y(height / 2).strength(function (d) {
				if (d.id == userid)
					return 1;
				return 0.2;
			}))
		.force("cluster", cluster)
		.on("tick", mytick);

	labelsg.append("path")
	.attr("id", "bcirclepath") //Unique id of the path
	.attr("d", "M 45,35 A 90,90 0 0,1 165,35") //SVG path
	.style("fill", "none")
	.style("stroke", "none");

	labelsg.append("path")
	.attr("id", "blistingpath") //Unique id of the path
	.attr("d", "M 150,195 A 90,90 0 0,0 200,75") //SVG path
	.style("fill", "none")
	.style("stroke", "none");

	labelsg.append("path")
	.attr("id", "bsocialpath") //Unique id of the path
	.attr("d", "M 10,75 A 90,90 0 0,0 70,195") //SVG path
	.style("fill", "none")
	.style("stroke", "none");
	var blabels = labelsg.append("text")
		.attr("class", "labeltext")

		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#bcirclepath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("commoners")
        .attr("id","bunchescommonerlabel")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
			d3.select(this).style("fill", "#E7472E");
		})
		.on("mouseout", function (d) {
			d3.select(this).style("fill", nodecolor("commoner"));
		})
		.style("fill", nodecolor("commoner"))

		var blistinglabels = labelsg.append("text")
		.attr("class", "labeltext")
		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#blistingpath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("listings")
        .attr("id","buncheslistinglabel")
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

	var bsociallabels = labelsg.append("text")
		.attr("class", "labeltext")

		.append("textPath") //append a textPath to the text element
		.attr("xlink:href", "#bsocialpath") //place the ID of the path here
		.style("text-anchor", "middle") //place the text halfway on the arc
		.attr("startOffset", "50%")
		.text("stories")
        .attr("id","bunchesstorylabel")
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

}
// Move d to be adjacent to the cluster node.
function cluster(alpha) {
	return function (d) {
		var cluster = centroid;
		if (cluster === d)
			return;
		var x = d.x - cluster.x,
		y = d.y - cluster.y,
		l = Math.sqrt(x * x + y * y),
		r = d.radius + cluster.radius;
		if (l != r) {
			l = (l - r) / l * alpha;
			d.x -= x *= l;
			d.y -= y *= l;
			cluster.x += x;
			cluster.y += y;
		}
	};
}
function mytick(e) {

	bunchnode.attr("transform", function (d) {
		return "translate(" + d.x + "," + d.y + ")";
	}).each(function (d) {
		if (d.id == userid) {
			textnode.attr("x", d.x);
			textnode.attr("y", d.y + textnode.node().getBoundingClientRect().height / 4);
		}
	});
 //   bunchlinks.attr("transform", function(d){
 //       return "translate(" + d.source.x + "," + d.source.y + ")";
 //   });
	
}
