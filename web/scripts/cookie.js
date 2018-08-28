function zoomCookie() {
	var center = getBoundingBoxCenterX(cookiechart); //rect is the charts parent which expands while zooming
	var chartsWidth = (2 * center) * d3.event.transform.k;
	d3.event.transform.x = center - chartsWidth / 2;
	d3.event.transform.y = center - chartsWidth / 2;
	cookieg.attr("transform", d3.event.transform)
};

var width = 200,
height = 200;

var cookiechart = d3.select("#cookie").on("click", function () {
		zoom(root);
	}),
cookieg = cookiechart.append("g");
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
	.text("stories")
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
	.text("listings")
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
	.text("transactions")
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
	.text("social")
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
	.style("font-size", "70")
	.style("font-family", "'Dosis', sans-serif");
var circles;
var view, margin = 20;
var labellist = [labels, sociallabels, transactionlabels, listinglabels];
function plotcookie(graphdata, mydata) {

	d3.select(".cookiepack").html("");

	$("#cookie").bind("wheel mousewheel", function (e) {
		e.preventDefault()
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
			if (data.links[link].edgemeta.includes(key)) {

				data.links[link]["children"] = [];
				for (var x in linktypes) {
					if (linktypes[x]in data.links[link]) {
						var array = data.links[link][linktypes[x]];
						for (var y = 0; y < array.length; y++) {
							data.links[link]["children"].push([linktypes[x]].concat(array[y]));
						}
					}
				}
				type_links.push(data.links[link]);
			}
		}
		return type_links;
	}

	var cumu_totals = JSON.parse(JSON.stringify(mydata.cumu_totals));
	var cumu_array = d3.keys(cumu_totals).map(function (key) {
			return {
				"id": mydata.id,
				"name": key,
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
	//This is silly but because the pack layout size can't be updated dynamically, we have to make one for every circle we're using
	var size = cumu_totals["children"][0].kcore;
	//var scaledsize = size*9 + 30;
	//Here I'll try to make the size consistent
	var scaledsize = Math.max(size * 9 + 30, 150);
	circlepack = d3.pack()
		.size([scaledsize, scaledsize])
		.padding(function(d){return 5;});
	root = d3.hierarchy(cumu_totals, children);
	var focus = root;
	console.log("ROOOOOT");
	console.log(root);
	circles = monthpack.selectAll('.cookiecircle').data(circlepack(root
				//Will need to figure out another way of resizing things
				.sum(function (e) {
					if (e.name == "date" || e.name == "stats")
						return 0;
					if (e.total != null)
						return e.total;
                    if (e.children)
                        return 1
                    return 0.5;
				})
				.sort(function (a, b) {
					return b.value - a.value;
				}))
			.descendants())
		.enter().append("g");
		var interaction_data = "";

	circles.append("circle")
	.attr("class", "cookiecircle")
	.on("click", function (d) {
		if (focus !== d)
			zoom(d), d3.event.stopPropagation();
	})
    
	.style("fill", function (d) {
        if (d.children == null)
            return "white";
		if (d.children != null && d.parent != null)
			return color(d.data.name);
		if (d.parent != null)
			return color(d.parent.data.name);
		return "none";
	})
	.style("opacity", function (d) {
		return d.children ? 0.7 : 1;
	})
	.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");

		var name;
        console.log(d.data.target);
        var datasource;
        if(d.data.target == undefined && d.parent.data.target == undefined)
            return null;
		if (d.data.target == undefined)
           datasource = d.parent.data;
        else
            datasource = d.data;
        infotooltip.transition()
		.duration(200)
		.style("opacity", .9);
        var target;
        if(datasource.target.id == userid)
            target = datasource.source;
        else
            target = datasource.target;
		if (target.type == 'commoner') {
			name = "<b>" + target.name + "</b>";
			infotooltip.style("background", "lightgrey");
		} else if (target.type == "story") {
			name = "<b>" + target.title + "</b>";
			infotooltip.style("background", "pink");
		} else if (target.type == "listing") {
			name = "<b>" + target.title + "</b>";
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

    cookieimages = circles.append("svg:image")
				.attr('x', function(d){return -d.r})
				.attr('y', function(d){return -d.r})
				.attr('width', function(d){return d.children ? 0 : d.r*2})
				.attr('height', function(d){return d.children ? 0 : d.r*2})
				.attr("xlink:href", function(d){
                    if(d.data[0] == 'create_story')
                        return "icons/authorstory.svg";
                    if(d.data[0] == 'create_listing')
                        return "icons/authorlisting.svg";
                    if(d.data[0] == 'comment_story')
                        return "icons/commentstory.svg";
                    if(d.data[0] == 'comment_listing')
                        return "icons/commentlisting.svg";
                    if(d.data[0] == 'transaction')
                        return "icons/transaction.svg";
                    if(d.data[0] == 'conversation')
                        return "icons/conversation.svg";                    
                })
                .style("pointer-events","none");
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
	zoomTo([root.x, root.y, root.r * 2 + margin]);

}
function zoom(d) {
	var focus0 = focus;
	focus = d;
    if(d == root)
        cookietext.style("display","inline-block");
    else
        cookietext.style("display","none");
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