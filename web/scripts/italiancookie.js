
var width = 200,
height = 200;

var cookiechart = d3.select("#cookie").on("click", function () {
		zoom(root);
	}),
cookieg = cookiechart.append("g");
var defs = cookieg.append("defs");

//Filter for the outside glow
var filter = defs.append("filter")
    .attr("id","glow");
filter.append("feGaussianBlur")
    .attr("stdDeviation","3.5")
    .attr("result","coloredBlur");
var feMerge = filter.append("feMerge");
feMerge.append("feMergeNode")
    .attr("in","coloredBlur");
feMerge.append("feMergeNode")
    .attr("in","SourceGraphic");
var monthpack = cookieg.append("g").attr("class", "cookiepack")
	.attr("transform", "translate(" + (width / 2) + "," + (height / 2) + ")")
	.on("click", function () {
		zoom(root);
	}); ;

cookieg.append("path")
.attr("id", "circlepath") //Unique id of the path
.attr("d", "M 100,15 A 85,85 0 0,1 185,100") //SVG path
.style("fill", "none")
.style("stroke", "none");

var labels = cookieg.append("text")
	.attr("class", "labeltext")
	.append("textPath") //append a textPath to the text element
	.attr("xlink:href", "#circlepath") //place the ID of the path here
	.style("text-anchor", "middle") //place the text halfway on the arc
	.attr("startOffset", "50%")
	.text("storie")
    .attr("id","cookiestorylabel")
	.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");

	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", color("story"));
	})
	.style("font-size", "18px")
	.style("fill", color("story"))
	.style("font-weight", "bold");
cookieg.append("path")
.attr("id", "listingpath") //Unique id of the path
.attr("d", "M 100,195 A 95,95 0 0,0 195,100") //SVG path
.style("fill", "none")
.style("stroke", "none");

var listinglabels = cookieg.append("text")
	.attr("class", "labeltext")

	.append("textPath") //append a textPath to the text element
	.attr("xlink:href", "#listingpath") //place the ID of the path here
	.style("text-anchor", "middle") //place the text halfway on the arc
	.attr("startOffset", "50%")
	.text("inserzione")
    .attr("id","cookielistinglabel")
	.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");

	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", color("listing"));
	})
	.style("font-size", "18px")
	.style("fill", color("listing"))
	.style("font-weight", "bold");

cookieg.append("path")
.attr("id", "transactionpath") //Unique id of the path
.attr("d", "M 15,100 A 85,85 0 0,1 100,15") //SVG path
.style("fill", "none")
.style("stroke", "none");

var transactionlabels = cookieg.append("text")
	.attr("class", "labeltext")

	.append("textPath") //append a textPath to the text element
	.attr("xlink:href", "#transactionpath") //place the ID of the path here
	.style("text-anchor", "middle") //place the text halfway on the arc
	.attr("startOffset", "50%")
	.text("transazioni")
    .attr("id","cookietransactionlabel")
	.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");

	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", color("transaction"));
	})
	.style("font-size", "18px")
	.style("fill", color("transaction"))
	.style("font-weight", "bold");

cookieg.append("path")
.attr("id", "socialpath") //Unique id of the path
.attr("d", "M 5,100 A 95,95 0 0,0 100,195") //SVG path
.style("fill", "none")
.style("stroke", "none");

var sociallabels = cookieg.append("text")
	.attr("class", "labeltext")

	.append("textPath") //append a textPath to the text element
	.attr("xlink:href", "#socialpath") //place the ID of the path here
	.style("text-anchor", "middle") //place the text halfway on the arc
	.attr("startOffset", "50%")
	.text("sociali")
    .attr("id","cookiesociallabel")
	.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");

	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", color("social"));
	})
	.style("font-size", "18px")
	.style("fill", color("social"))
	.style("font-weight", "bold");

cookietext = cookieg.append("text")
	.attr("text-anchor", "middle")
	.attr("stroke", "white")
	.style("font-size", "50px")
	.style("font-family", "'Dosis', sans-serif");
var view, margin = 20;
var labellist = [labels, sociallabels, transactionlabels, listinglabels];
var newplot = false;
	
function plotcookie(graphdata, mydata) {
    newplot = true;
	d3.select(".cookiepack").html("");

	$("#cookie").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

  //Have to do the manual mapping
  graphdata.links.forEach(function(e) {
    e.source = isNaN(e.source) ? e.source : graphdata.nodes.filter(function(d) {console.log(d.id + '-' + e.source); return d.id == e.source; })[0];
    e.target = isNaN(e.target) ? e.target : graphdata.nodes.filter(function(d) { return d.id == e.target; })[0];
    e["children"] = [];
  });
	function children(d) {
		return d.children;
	}
	function summer(total, num) {
		return (isNaN(num) || num instanceof Date) ? total : total + num;
	}
	function links_of_type(data, key) {
		var linktypes = keytypes[key];
		var type_links = [];
		for (var link in data.links) {
            if(data.links[link].source.id == userid || data.links[link].target.id == userid)
                if ("edgemeta" in data.links[link] && data.links[link].edgemeta.includes(key)) {
                    for (var x in linktypes) {
                        if (linktypes[x]in data.links[link]) {
                            var array = data.links[link][linktypes[x]];
                            for (var y = 0; y < array.length; y++) {
                                var childtopush = [linktypes[x]].concat(array[y]);
                                    data.links[link]["children"].push(childtopush);
                                    console.log("PUSHING " + childtopush);
                            }
                        }
                    }
                    type_links.push(data.links[link]);
                }
		}
		return type_links;
	}
        

    console.log(mydata.cumu_totals);
	var cumu_totals = JSON.parse(JSON.stringify(mydata.cumu_totals));
	var cumu_array = d3.keys(cumu_totals).map(function (key) {
			return {
				"id": mydata.id,
				"type": key,
				"children": links_of_type(graphdata, key),
				"total": cumu_totals[key],
				"kcore": mydata.kcore,
				"stats": mydata.stats
			};
		});
        
	// cumu_array.push({"name":"commonshare","total":1,"kcore":mydata.kcore});
	var keys = Object.keys(cumu_totals);
	cumu_totals["overall"] = Object.values(cumu_totals).reduce(summer, 0);
	cumu_totals["kcore"] = mydata.kcore;
	cumu_totals["children"] = cumu_array;
	cumu_totals["date"] = mydata.date;
	cumu_totals["stats"] = mydata.stats;
	var xdisplacements = [];
	var ydisplacements = [];

	var monthname = d3.timeFormat("%b");
	var circlepack;

	var size = cumu_totals["children"][0].kcore;
  //  console.log("WOOAH");
  //  console.log(cumu_totals);
	//var scaledsize = size*9 + 30;
	//Here I'll try to make the size consistent
	var scaledsize = Math.max(size * 9 + 30, 150);
	circlepack = d3.pack()
		.size([scaledsize, scaledsize])
		.padding(function(d){return 5;});
	root = d3.hierarchy(cumu_totals, children);
	var focus = root;
	circles = monthpack.selectAll('.cookiecircle').data(circlepack(root
                .each(function(d){
                    if(d.children == undefined){
                        var parentnode = d.parent.parent;
                        if(parentnode != null && keytypes[parentnode.data.type].includes(d.data[0]) == false){
                           var parentchild = d.parent.children;
                           var index = parentchild.indexOf(d);
                           parentchild[index] = {"value" : 0};
                        }
                    }
                })
				//Will need to figure out another way of resizing things
				.sum(function (e) {
                    console.log(e);
                    if(e == undefined)
                    return 0;
					if (e.type == "date" || e.type == "stats")
						return 0;
                    
					if (e.total != null)
						return e.total;
                    
                                        
                    return 0.5;
				})
				.sort(function (a, b) {
					return b.value - a.value;
				}))
			.descendants())
		.enter().append("g");
		var interaction_data = "";

	circles.append("circle")
    .style("pointer-events",function(d){
      if(d.children == undefined)
            return "none";
      return "auto";
    })
	.attr("class", function(d){
        if(d.parent == root || d.parent == null){
            console.log(d);
            return "cookiecircle parental";
        }
       
        if(d.children == null)
            return "cookiecircle cookiechild cookie" + d.parent.data.type;
        else
            return "cookiecircle cookiechild cookie" + d.data.type;
            
    })
	.on("click", function (d) {
        if(d.children != undefined && d.parent != root && d.parent != undefined){
            var nodename = d.data.name;
            if(d.data.type == 'commoner')
                nodename = d.label.split('_')[1];
            var url = getUrl(d.data.type,nodename);
          //  var win = window.open(url, '_blank');
            return;
        }
		if (focus !== d)
			zoom(d), d3.event.stopPropagation();
	})
    .style("visibility",function(d){
      if(d.parent == root || d.parent == undefined)
            return "visible";
        return  "hidden";
    })
	.style("fill", function (d) {
		if (d.children != null && d.parent != null)
			if(d.data.type != null)
                return color(d.data.type);
            else
                return color(d.parent.data.type);
		return "white";
	})
	.style("opacity", function (d) {
		return d.children ? 0.7 : 1;
	})
	.on("mouseover", function (d) {
		
		var name;
        var datasource;
        if(d.parent == undefined)
            return;
        if(d.data.target == undefined && d.parent == root)
            datasource = d.data;
		else if (d.data.target == undefined)
           datasource = d.parent.data;
        else
            datasource = d.data;
        d3.select(this).style("cursor", "pointer");
        console.log(datasource);
        if(datasource.type == undefined)
            labelToHighlight = "#cookie"+d.parent.data.type + "label";
        else
            labelToHighlight = "#cookie"+datasource.type + "label";
            
            d3.select(this).style("cursor", "pointer");
            oldLabelColour = d3.select(labelToHighlight).style("fill");
            d3.select(labelToHighlight).style("fill", "#E7472E");
            
                     d3.select(this).style("filter","url(#glow)");
        var target;
        if(datasource.target == undefined)return;
        if(datasource.target.id == userid)
            target = datasource.source;
        else
            target = datasource.target;
		if (target.type == 'commoner')
			name = target.name;
		 else
			name = target.title;
        $("#cookiedescription").html("<h5 class='overlay'>"+name+"</h5>");

	})
	.on("mouseout", function (d) {
	    $("#cookiedescription").html("");
            d3.select(this).style("filter","")
            d3.select(labelToHighlight).style("fill",oldLabelColour);
    })
    ;
    var labelToHighlight;
    var oldLabelColour;
    cookieimages = circles.append("svg:image")
				.attr('x', function(d){return -d.r})
				.attr('y', function(d){return -d.r})
                .attr("class",function(d){if(d.data == undefined)return "cookieimage"; return "cookieimage cookiechild cookie"+d.data.name;})
				.attr('width', function(d){return d.children ? 0 : d.r*2})
				.attr('height', function(d){return d.children ? 0 : d.r*2})
				.attr("xlink:href", function(d){
                    if(d.data == undefined)
                        return "";
                    if(d.data[0] == 'create_story')
                        return "icons/authorstory.png";
                    if(d.data[0] == 'create_listing')
                        return "icons/authorlisting.png";
                    if(d.data[0] == 'comment_story')
                        return "icons/commentstory.png";
                    if(d.data[0] == 'comment_listing')
                        return "icons/commentlisting.png";
                    if(d.data[0] == 'transaction')
                        return "icons/transaction.png";
                    if(d.data[0] == 'conversation')
                        return "icons/conversation.png";                    
                })
                .style("visibility","hidden")
                .style("pointer-events","none");
                	zoomTo([root.x, root.y, root.r * 2 + margin]);

	cookietext.text(size)
	.attr("x", function () {
		return width / 2;
	})
    .attr("y", function () {
		return height / 2 + (cookietext.node().getBoundingClientRect().height / 4);
	})
	.style("opacity", 0)
	.transition().duration(400)
    .style("pointer-events","none")
	.style("opacity", "1");
    zoom(root);

}
function zoom(d) {
	var focus0 = focus;
	focus = d;
    console.log(d);
    if(d == root){
        
        d3.selectAll(".cookiechild").style("visibility","hidden");
        cookietext.style("display","inline-block")
        	.attr("x", function () {
		return width / 2;
	})
    .attr("y", function () {
		return height / 2 + (cookietext.node().getBoundingClientRect().height / 4);
	});
       // cookieimages.style("visibility","hidden");
    }
    else{
        d3.selectAll(".cookiechild").style("visibility","visible");
        cookieimages.style("visibility","visible")
                        //.style("filter","url(#glow)")

        ;
        cookietext.style("display","none");
	}
    var transition = d3.transition()
		.duration(750)
		.tween("zoom", function (d) {
			var i = d3.interpolateZoom(view, [focus.x, focus.y, focus.r * 2 + margin]);
			return function (t) {
				zoomTo(i(t));
			};
		});
}
function zoomTo(v) {
	var k = 200 / v[2];
	view = v;
	circles.attr("transform", function (d) {
		return "translate(" + (d.x - v[0]) * k + "," + (d.y - v[1]) * k + ")";
	});
	d3.selectAll(".cookiecircle").attr("r", function (d) {
		return d.r * k;
	});
     cookieimages.attr('x', function(d){return -d.r *k})
				.attr('y', function(d){return -d.r*k})
				.attr('width', function(d){return d.children ? 0 : d.r*2*k})
				.attr('height', function(d){return d.children ? 0 : d.r*2*k});

}