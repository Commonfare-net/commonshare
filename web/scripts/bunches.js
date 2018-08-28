
function zoomBunch() {
	var center = getBoundingBoxCenterX(bunchchart); //rect is the charts parent which expands while zooming
	var chartsWidth = (2 * center) * d3.event.transform.k;
	d3.event.transform.x = center - chartsWidth / 2;
	d3.event.transform.y = center - chartsWidth / 2;
		bunchcircles.attr("transform", d3.event.transform)
};
var bunchzoom = d3.zoom()
	.scaleExtent([0.5, 2])
	.on("zoom", zoomBunch);
	bunchchart = d3.select("#bunches"),
    labelsg = bunchchart.append("g").attr("class","bunchlabels");
	bunchg = bunchchart.append("g").attr('class','bunchpack');
    

  

function plotbunches(mydata) {
        d3.select(".bunchpack").html("");

	$("#bunches").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var width = 200,
	height = 200;

    var innerwidth = 180;
    var innerheight = 180;
    
	var centroid = {
		"source": "0",
		"target": "0",
		"edgemeta": ["story"],
		"centroid": "true"
	};
    
    bunchg.append("clipPath")       // define a clip path
    .attr("id", "ellipse-clip") // give the clipPath an ID
  .append("ellipse")          // shape it as an ellipse
    .attr("cx", 100)         // position the x-centre
    .attr("cy", 100)         // position the y-centre
    .attr("rx", 80)         // set the x radius
    .attr("ry", 80);         // set the y radius
    
	bunchnode = bunchg.append("g").attr("id", "bunchg").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
    	bunchg.call(bunchzoom);

	bunchnode = bunchnode.data(mydata.links.concat([centroid]), function (d) {
			return d.source + '-' + d.target;
		});
	bunchnode = bunchnode
		.enter().append("g")
                .attr("clip-path", "url(#ellipse-clip)")
;

	bunchcircles = bunchnode
		.append("circle")
		.attr("r", function (d) {
			console.log(d);
			if (d.centroid == null && (d.edgeweight == null || d.edgeweight[userid] == null))
				return 0;
			if (d.centroid != null)
				return mydata.nodes.find(findNode).kcore * 3 + 6;
			return d.edgeweight[userid] * 2 + 5;
		})
		.attr("fill", function (d) {
			if (d.centroid != null)
				return "orange";
			return color(d.edgemeta[0]);
		})
		.on("mouseover", function (d) {
			//	console.log(central_data);
			var statsdata = "";
			/*
			for (var key in central_data.stats) {
			if (key == d.id) {
			console.log(central_data.stats[key]);
			for (var i = 0; i < central_data.stats[key].length; i++) { // in central_data.stats[key]){
			statsdata += tooltipFormat(parseTime(central_data.stats[key][i][1])) + ": " + prettyKeys[central_data.stats[key][i][0]] + "</br>";
			}
			}
			}
			 */
			overnode = true;
			infotooltip.transition()
			.duration(200)
			.style("opacity", .9);
			var sourcetarget;
			sourcetarget = "<b>Source: " + d.source + ". Target: " + d.target + "</b>";
			infotooltip.style("background", "lightsteelblue");
			infotooltip.html(sourcetarget + "</br><div>Weight: " + d.edgeweight[userid] + "</div>")
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px")
		})
		.on("mouseout", function (d) {
			overnode = false;
			infotooltip.transition()
			.duration(500)
			.style("opacity", 0);
		});
	textnode = bunchg.append("text")
		.attr("stroke", "white")
		.attr("text-anchor", "middle")
		.style("font-size", "48")
		.style("font-family", "'Dosis', sans-serif")
		.text(mydata.nodes.find(findNode).kcore);

	//});

	var simulation = d3.forceSimulation()
		.alphaDecay(0.05)
		.velocityDecay(0.2)

		.nodes(mydata.links.concat([centroid]))
		.force("collide", d3.forceCollide().radius(function (d) {
				if (d.centroid != null)
					return mydata.nodes.find(findNode).kcore * 3 + 6;
				if (d.edgeweight == null || d.edgeweight[userid] == null)
					return 0;
				return d.edgeweight[userid] * 2 + 5;
			}).iterations(2))
		//Need the function here to draw links between nodes based on their ID rather than their index
		.force("x", d3.forceX().x(width / 2).strength(function (d) {
				if (d.centroid != null)
					return 2;
				return 0.2;
			}))
		.force("y", d3.forceY().y(height / 2).strength(function (d) {
				if (d.centroid != null)
					return 2;
				return 0.2;
			}))
		.force("cluster", cluster)

		.on("tick", mytick);
	// Update and restart the simulation.
	//simulation.force("link").links(mydata.links);
	//cluster.force("drag").links(mydata.links);
      labelsg.append("path")
    .attr("id", "bcirclepath") //Unique id of the path
    .attr("d", "M 100,15 A 85,85 0 0,1 185,100") //SVG path
    .style("fill", "none")
    .style("stroke", "none");  
  


  labelsg.append("path")
    .attr("id", "blistingpath") //Unique id of the path
    .attr("d", "M 100,195 A 95,95 0 0,0 195,100") //SVG path
    .style("fill", "none")
    .style("stroke", "none");  
  


  labelsg.append("path")
    .attr("id", "btransactionpath") //Unique id of the path
    .attr("d", "M 15,100 A 85,85 0 0,1 100,15") //SVG path
    .style("fill", "none")
    .style("stroke", "none");  
  

    
  labelsg.append("path")
    .attr("id", "bsocialpath") //Unique id of the path
    .attr("d", "M 0,100 A 95,95 0 0,0 100,195") //SVG path
    .style("fill", "none")
    .style("stroke", "none");  
      var blabels = labelsg.append("text")
      .attr("class","labeltext")
      
   .append("textPath") //append a textPath to the text element
    .attr("xlink:href", "#bcirclepath") //place the ID of the path here
    .style("text-anchor","middle") //place the text halfway on the arc
    .attr("startOffset", "50%")
    .text("stories")
    .on("mouseover", function(d) {
        d3.select(this).style("cursor", "pointer"); 
        d3.select(this).style("fill", "#E7472E"); 
      })    
      .on("mouseout",function(d){
         d3.select(this).style("fill",color("story"));          
      })      
    .style("fill",color("story"))
    
      var blistinglabels = labelsg.append("text")
      .attr("class","labeltext")
   .append("textPath") //append a textPath to the text element
    .attr("xlink:href", "#blistingpath") //place the ID of the path here
    .style("text-anchor","middle") //place the text halfway on the arc
    .attr("startOffset", "50%")
    .text("listings")
    .on("mouseover", function(d) {
        d3.select(this).style("cursor", "pointer");
        d3.select(this).style("fill", "#E7472E"); 
        
      })   
      .on("mouseout",function(d){
         d3.select(this).style("fill",color("listing"));          
      })      
    .style("font-size","18px")
    .style("fill",color("listing"))
    .style("font-weight","bold"); 
    
    var btransactionlabels = labelsg.append("text")
       .attr("class","labeltext")
   
   .append("textPath") //append a textPath to the text element
    .attr("xlink:href", "#btransactionpath") //place the ID of the path here
    .style("text-anchor","middle") //place the text halfway on the arc
    .attr("startOffset", "50%")
    .text("transactions")
    .on("mouseover", function(d) {
        d3.select(this).style("cursor", "pointer"); 
        d3.select(this).style("fill", "#E7472E"); 
      })
         .on("mouseout",function(d){
         d3.select(this).style("fill",color("transaction"));          
      })   
    .style("font-size","18px")
    .style("fill",color("transaction"))
    .style("font-weight","bold");     

    var bsociallabels = labelsg.append("text")
      .attr("class","labeltext")
    
   .append("textPath") //append a textPath to the text element
    .attr("xlink:href", "#bsocialpath") //place the ID of the path here
    .style("text-anchor","middle") //place the text halfway on the arc
    .attr("startOffset", "50%")
    .text("social")
    .on("mouseover", function(d) {
        d3.select(this).style("cursor", "pointer");
        d3.select(this).style("fill", "#E7472E"); 
        
      })
      .on("mouseout",function(d){
         d3.select(this).style("fill",color("social"));          
      })      
    .style("font-size","18px")
    .style("fill",color("social"))
    .style("font-weight","bold"); 

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

	bunchcircles
	.attr("cx", function (d) {
		if (d.centroid != null)
			textnode.attr("x", d.x);
		return d.x;
	})
	.attr("cy", function (d) {
		if (d.centroid != null)
			textnode.attr("y", d.y + textnode.node().getBoundingClientRect().height/4);
		return d.y;
	});
}
