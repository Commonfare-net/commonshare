//Much code taken from https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html
var chart = d3.select("#donut");
chartg = chart.append("g");
var donut_defined = false;
var pie = d3.pie()
	.startAngle(-90 * Math.PI / 180)
	.endAngle(-90 * Math.PI / 180 + 2 * Math.PI)
	.sort(null)
	.value(function (d) {
		return d.value;
	});

var arc = d3.arc()
	.outerRadius(90)
	.innerRadius(70);
var defs = chart.append("defs");

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
var arcs = chartg.selectAll(".arc");
var donut_labels = chartg.selectAll(".donutText");
var kcoretext = chartg.append("text")
	.style("font-size", "70")
	.style("font-family", "'Dosis', sans-serif");

var returntext = chartg.append("text")
	.style("font-size", "16")
	.style("font-family", "'Dosis', sans-serif");
var typetext = chart.append("text")
	.style("font-size", "28")
	.style("font-family", "'Dosis', sans-serif");
var descriptiontext = chart.append("text")
	.style("font-size", "14")
	.style("font-family", "'Dosis', sans-serif");
function links_of_type(data, key) {
	var linktypes = keytypes[key];
	var type_links = [];
	for (var link in data.links) {
		if (data.links[link].edgemeta.includes(key)) {

			if (data.links[link].target.id == userid)
				target = data.links[link].source;
			else
				target = data.links[link].target;
			if (target.type == "commoner")
				data.links[link]["name"] = target.name;
			else
				data.links[link]["name"] = target.title;
			data.links[link]["value"] = data.links[link].edgeweight[target.id];
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

function makearcs(piesegments, areChildren) {
    console.log("PIES ARE");
    console.log(piesegments);
	arcs = arcs.data(pie(piesegments));
	arcs.exit().remove();
	d3.selectAll(".hiddenDonutArcs").remove();
    d3.selectAll(".arcimage").remove()
	if (areChildren == false)
		donut_labels.style("visibility", "visible");
    
    var oldhtml;
       arcs = arcs.enter().append("path")
			.attr("id", function (d, i) {
				return "monthArc_" + i;
			}) //Unique id for each slice
			.attr("class", "arc")
			.attr("transform", "translate(" + donutwidth / 2 + "," + donutheight / 2 + ")")
			.merge(arcs)
			.attr("d", arc)
			.each(function (d, i) {
				this._current = d;
				var firstArcSection = /(^.+?)L/;
				var wholeArcSection = /[^A]*A[^A]*/;

				var regex = firstArcSection.exec(d3.select(this).attr("d"));
				var newArc;
				if (regex == null) {
					regex = wholeArcSection.exec(d3.select(this).attr("d"));
					newArc = regex[0];
				} else
					newArc = regex[1];
				newArc = newArc.replace(/,/g, " ");
				var end = (d.endAngle / (Math.PI / 180));
				var start = (d.startAngle / (Math.PI / 180));

				if (d.endAngle > 90 * Math.PI / 180 && start > (180 - end) && (end - start) % 360 != 0) {

					var startLoc = /M(.*?)A/;
					var middleLoc,
					endLoc;
					if ((end - start) < 180) {
						middleLoc = /A(.*?)0 0 1/;
						endLoc = /0 0 1 (.*?)$/;
					} else {
						middleLoc = /A(.*?)0 1 1/;
						endLoc = /0 1 1 (.*?)$/;
					}

					var newStart = endLoc.exec(newArc)[1];
					var newEnd = startLoc.exec(newArc)[1];
					var middleSec = middleLoc.exec(newArc)[1];
					var numbers;
					if ((end - start) < 180)
						numbers = "0 0 0 ";
					else
						numbers = "0 1 0 ";
					newArc = "M" + newStart + "A" + middleSec + numbers + newEnd;
				}

				chartg.append("path")
				.attr("class", "hiddenDonutArcs")
				.attr("id", "donutArc" + i)
				.attr("d", newArc)
				.attr("transform", "translate(" + donutwidth / 2 + "," + donutheight / 2 + ")")

				.style("fill", "none");
			})
			.style("fill", function (d) {
				if (areChildren == false)
					return color(d.data.name);
				return color(donutParent);
			})
			.style("stroke", function (d) {
				if (areChildren == false)
					return "none";
				return "white";
			})
			.style("stroke-width", function (d) {
				if (areChildren == false)
					return "0";
				return "3";
			})
			.on("mouseover", function (d) {
				d3.select(this).style("cursor", "pointer")
                .style("filter","url(#glow)")
                .style("fill",function(d){
 				if (areChildren == false)
					return brightercolor(d.data.name);
				return brightercolor(donutParent);                   
                });
				if (areChildren == true){
                    console.log(d);
                    oldhtml = $("#donutdescription").html();
                    $("#donutdescription").html("<h5 class='overlay'>"+d.data.name+"</h5>");
                    return;
                }
				donut_defined = false;
				donutParent = d.data.name;
				//donut_labels.style("visibility", "hidden");
				kcoretext.style("display", "none");
				var create_story = 0,
				comment_story = 0,
				create_listing = 0,
				comment_listing = 0,
				conversation = 0,
				transaction = 0;
				for (var i = 0; i < d.data.children.length; i++) {
					var childdata = d.data.children[i];
					if (donutParent == 'story') {
						if (childdata['create_story'] != undefined)
							create_story += childdata['create_story'].length;
						if (childdata['comment_story'] != undefined)
							comment_story += childdata['comment_story'].length;
						$("#donutdescription").html("Stories created: " + create_story + "</br>Story comments: " + comment_story);
					} else if (donutParent == 'listing') {
						if (childdata['create_listing'] != undefined)
							create_listing += childdata['create_listing'].length;
						if (childdata['comment_listing'] != undefined)
							comment_listing += childdata['comment_listing'].length;
						$("#donutdescription").html("Listings created: " + create_listing + "</br>Listing comments: " + comment_listing);
					} else if (donutParent == 'transaction') {
						if (childdata['transaction'] != undefined)
							transaction += childdata['transaction'].length;
						$("#donutdescription").html("Transactions: " + transaction);
					} else if (donutParent == 'social') {
						if (childdata['conversation'] != undefined)
							conversation += childdata['conversation'].length;
						$("#donutdescription").html("Conversations: " + conversation);
					}
				};
				var descwidth = $("#donutdescription").outerWidth(true);
			})
			.on("mouseout", function (d) {
              d3.select(this).style("filter","");
				if (areChildren == false) {
					d3.select(this).style("fill", color(d.data.name));
					

                    kcoretext.style("display", "inline-block");
					$("#donutdescription").html("");
				} else {
					d3.select(this).style("fill", color(donutParent));
                    $("#donutdescription").html(oldhtml);
                }
			})
			.on("click", function (d) {
                console.log(d);
                if(d.data.children != undefined && d.data.label != undefined){
                 if(d.data.type == 'transaction' || d.data.type == 'social')
                    nodename = d.data.target.label.split('_')[1];
                else
                    nodename = d.data.name;
                var url = getUrl(d.data.type,nodename);
                var win = window.open(url, '_blank');
                return;
                }
				donut_defined = false;
				donutParent = d.data.name;
				donut_labels.style("visibility", "hidden");
				kcoretext.style("display", "none");
				var create_story = 0,
				comment_story = 0,
				create_listing = 0,
				comment_listing = 0,
				conversation = 0,
				transaction = 0;
				for (var i = 0; i < d.data.children.length; i++) {
					var childdata = d.data.children[i];
					if (donutParent == 'story') {
						if (childdata['create_story'] != undefined)
							create_story += childdata['create_story'].length;
						if (childdata['comment_story'] != undefined)
							comment_story += childdata['comment_story'].length;
						$("#donutdescription").html("Stories created: " + create_story + "</br>Story comments: " + comment_story);
					} else if (donutParent == 'listing') {
						if (childdata['create_listing'] != undefined)
							create_listing += childdata['create_listing'].length;
						if (childdata['comment_listing'] != undefined)
							comment_listing += childdata['comment_listing'].length;
						$("#donutdescription").html("Listings created: " + create_listing + "</br>Listing comments: " + comment_listing);
					} else if (donutParent == 'transaction') {
						if (childdata['transaction'] != undefined)
							transaction += childdata['transaction'].length;
						$("#donutdescription").html("Transactions: " + transaction);
					} else if (donutParent == 'social') {
						if (childdata['conversation'] != undefined)
							conversation += childdata['conversation'].length;
						$("#donutdescription").html("Conversations: " + conversation);
					}
				};
				var descwidth = $("#donutdescription").outerWidth(true);
				makeTextNode(donutParent, "return");

				makearcs(d.data.children, true);

			});
            if(areChildren == true){
               arcs.each(function(d){
                   console.log(d);
                   //Here is some maths to figure out where it goes
                   var centrex = 120, centrey = 120;
                   var startangle = d.startAngle;
                   var endangle = d.endAngle;
                   var angle = (((startangle+endangle)*(180/Math.PI))/2)*(Math.PI/180);
                   var ypos = centrey + (-Math.cos(angle)*80);
                   var xpos = centrex + Math.sin(angle)*80;
                  var circleg = chartg.append("g").attr("class","arcimage")
                  .attr("transform","translate("+xpos+","+ypos+")")
                  .style("pointer-events","none");
                  console.log("angle is " + angle);
                  console.log("x translate and y translate " + Math.cos(angle)*80 + ", " + Math.sin(angle)*80);
                  circleg.append("circle")
                    .attr("r",15)
                    .style("fill","white")
                    .style("stroke-width","3px")
                    .style("stroke",color(d.data.edgemeta[0]));
                 circleg.append("svg:image")
                .attr('class','donutimage')
				.attr('x', -10)
				.attr('y', -10)
				.attr('width',20)
				.attr('height',20)
				.attr("xlink:href",function(){
                   var actiontype = d.data.children[0][0];
                    if(actiontype == 'create_story')
                        return "icons/authorstory.png";
                    if(actiontype == 'create_listing')
                        return "icons/authorlisting.png";
                    if(actiontype == 'comment_story')
                        return "icons/commentstory.png";
                    if(actiontype == 'comment_listing')
                        return "icons/commentlisting.png";
                    if(actiontype == 'transaction')
                        return "icons/transaction.png";
                    if(actiontype == 'conversation')
                        return "icons/conversation.png";
                });
               });
            }
	if (areChildren == false)
		donut_defined = true;

}
d3.selectAll(".textypath")
.attr("xlink:href", function (d, i) {
	return "#donutArc" + i;
})
//}
var donutwidth = 240,
donutheight = 240;

function arcTween(a) {
	delete this._current["data"];
	delete a["data"];
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function (t) {
		return arc(i(t));
	};
}

function makeTextNode(thetext, thereturntext) {
	returntext.text(thereturntext);	
    var returntextnode = returntext.node();
	var returnwidth = returntextnode.getBoundingClientRect().width;
	var returnheight = returntextnode.getBoundingClientRect().height;

	var kcorenode = kcoretext.node();
	var kcorewidth = kcorenode.getBoundingClientRect().width;
	var kcoreheight = kcorenode.getBoundingClientRect().height;

	kcoretext.attr("transform", "translate(" + ((donutwidth / 2) - (kcorewidth / 2)) + "," + ((donutheight / 2) + (kcoreheight / 4)) + ")");
	returntext.attr("transform", "translate(" + ((donutwidth / 2) - (returnwidth / 2)) + ",25)");
    returntext.attr("class","returntext");
}
var original_segments;
function plotdonut(graphdata, mydata) {

	$("#donut").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});
  //Have to do the manual mapping
  graphdata.links.forEach(function(e) {
    e.source = isNaN(e.source) ? e.source : graphdata.nodes.filter(function(d) {console.log(d.id + '-' + e.source); return d.id == e.source; })[0];
    e.target = isNaN(e.target) ? e.target : graphdata.nodes.filter(function(d) { return d.id == e.target; })[0];
  });
	var edgetotals = mydata.edgetotals;
	var edgekeys = Object.keys(edgetotals);
	var piesegments = [];
	for (var i = 0; i < edgekeys.length; i++) {
		piesegments.push({
			"name": edgekeys[i],
			"value": edgetotals[edgekeys[i]],
			"children": links_of_type(graphdata, edgekeys[i])
		});
	}
	original_segments = piesegments;
	kcoretext.style("display", "inline-block")
	.text(mydata.kcore)
	makeTextNode("", "");
	$("#donutdescription").html("");
	makearcs(piesegments, false);

	donut_labels = donut_labels.data(pie(piesegments));
	donut_labels.exit().remove();
	donut_labels = donut_labels
		.enter().append("text")
		.merge(donut_labels)
		.attr("class", "donutText")
		.attr("dy", function (d, i) {
			var degreeEnd = (d.endAngle / (Math.PI / 180));
			var degreeStart = (d.startAngle / (Math.PI / 180));
			return (d.endAngle > 90 * Math.PI / 180 && degreeStart > (180 - degreeEnd) && ((degreeEnd - degreeStart) % 360 != 0) ? 18 : -11);
		});
	d3.selectAll(".textypath").remove();
	donut_labels.append("textPath")
	.text(function (d) {
		if (d.data.value > 0)
			return d.data.name;
		return "";
	})
	.attr("class", "textypath")
	.attr("startOffset", "50%")
	.style("text-anchor", "middle")
	.attr("xlink:href", function (d, i) {
		return "#donutArc" + i;
	})
	.style("font-size", "18px")
	.style("fill", function (d) {
		return color(d3.select(this).text());
	})

	.style("font-weight", "bold"); ;

	returntext.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");
	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", "black");
	})
	.on("click", function (d) {
		donut_defined = false;
		donut_labels.style("visibility", "visible")
		.style("fill", function (d) {
			return color(d3.select(this).text());
		});
		kcoretext.style("display", "inline-block");
		$("#donutdescription").html("");
		makeTextNode("", "");
		makearcs(original_segments, false);

	});

}
var donutParent;
