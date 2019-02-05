//Much code taken from https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html
function updateDonut(value) {
	if (value == -1)
		if (currentdonut == maxindex - 1)
			return;
		else
			currentdonut++;
	else
		if (currentdonut == 0)
			return;
		else
			currentdonut--;
	plotdonut(graph_data[currentdonut], node_data[currentdonut]);
	$('#donutdate').text(getDateText(node_data[currentdonut]));
}

var currentdonut = 0;
var maxindex = 0;
d3.json('../data/output/userdata/' + userid + '.json', function (results) {
	for (var fortnight = 0; fortnight < results.length; fortnight++) {
		node_data[fortnight] = results[fortnight]['nodes'].find(findNode);
		node_data[fortnight].date = parseTime(node_data[fortnight].date);
		graph_data[fortnight] = results[fortnight];
		//This is necessary for D3 to map source and target indices to their respective nodes
		plotdonut(graph_data[fortnight], node_data[fortnight]);
		maxindex++;
	}
	plotdonut(graph_data[0], node_data[0]);

	$('#donutdate').text(getDateText(node_data[currentdonut]));
});
function getDateText(data) {
	console.log("lang is " + lang);
	if (lang == 'it')
		return italianDate(tooltipFormat(data.date)) + "-" + italianDate(tooltipFormat(d3.timeWeek.offset(data.date, 2)));
	else if (lang == 'hr')
		return croatianDate(tooltipFormat(data.date)) + "-" + croatianDate(tooltipFormat(d3.timeWeek.offset(data.date, 2)));
	else
		return tooltipFormat(data.date) + "-" + tooltipFormat(d3.timeWeek.offset(data.date, 2))
}
function italianDate(date) {
	var monthabb = date.split(" ")[0];
	var month_map = {
		"Jan": "gen",
		"Feb": "feb",
		"Mar": "mar",
		"Apr": "apr",
		"May": "mag",
		"Jun": "giu",
		"Jul": "lug",
		"Aug": "ago",
		"Sep": "set",
		"Oct": "ott",
		"Nov": "nov",
		"Dec": "dic"
	};
	return month_map[monthabb] + " " + date.split(" ")[1];
}
function croatianDate(date) {
	var monthabb = date.split(" ")[0];
	var month_map = {
		"Jan": "sij",
		"Feb": "vel",
		"Mar": "ožu",
		"Apr": "tra",
		"May": "svi",
		"Jun": "lip",
		"Jul": "srp",
		"Aug": "kol",
		"Sep": "ruj",
		"Oct": "lis",
		"Nov": "stu",
		"Dec": "pro"
	};
	return month_map[monthabb] + " " + date.split(" ")[1];
}

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

var myReturnText;
if (lang == "hr")
	myReturnText = "povratak";
else if (lang == "it")
	myReturnText = "ritorna";
else
	myReturnText = "return";

//Filter for the outside glow
var filter = defs.append("filter")
	.attr("id", "glow");
filter.append("feGaussianBlur")
.attr("stdDeviation", "3.5")
.attr("result", "coloredBlur");
var feMerge = filter.append("feMerge");
feMerge.append("feMergeNode")
.attr("in", "coloredBlur");
feMerge.append("feMergeNode")
.attr("in", "SourceGraphic");
var arcs = chartg.selectAll(".arc");
var donut_labels = chartg.selectAll(".donutText");
var kcoretext = chartg.append("text")
	.attr("id", "coretext")
	.style("font-size", "70px")
	.style("font-family", "'Dosis', sans-serif");

var returntext = chartg.append("text")
	.style("font-size", "16px")
	.style("font-family", "'Dosis', sans-serif");
var typetext = chart.append("text")
	.style("font-size", "28px")
	.style("font-family", "'Dosis', sans-serif");
var descriptiontext = chart.append("text")
	.style("font-size", "14px")
	.style("font-family", "'Dosis', sans-serif");
function links_of_type(data, key) {
	var linktypes = keytypes[key];
	var type_links = [];
	for (var link in data.links) {
		if (data.links[link].source.id == userid || data.links[link].target.id == userid)
			if ("edgemeta" in data.links[link] && data.links[link].edgemeta.includes(key)) {

				if (data.links[link].target.id == userid)
					target = data.links[link].source;
				else
					target = data.links[link].target;
				data.links[link]["name"] = target.t;
				data.links[link]["value"] = data.links[link].edgeweight[target.id];
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
			.style("filter", "url(#glow)");
			//	.style("fill", function (d) {
			//		if (areChildren == false)
			//		return brightercolor(d.data.name);
			//return brightercolor(donutParent);
			//});
			if (areChildren == true) {
				oldhtml = $("#donutdescription").html();
				$("#donutdescription").html("<h5 class='overlay'>" + d.data.name + "</h5>");
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
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "broj stvorenih priča: " + create_story + "</br>komentari na priče: " + comment_story;
						if (lang == "it")
							return "storie create: " + create_story + "</br>commenti di storia: " + comment_story;
						return "Stories created: " + create_story + "</br>Story comments: " + comment_story;
					});
				} else if (donutParent == 'listing') {
					if (childdata['create_listing'] != undefined)
						create_listing += childdata['create_listing'].length;
					if (childdata['comment_listing'] != undefined)
						comment_listing += childdata['comment_listing'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "broj unesenih unosa: " + create_listing + "</br>komentari na unosi: " + comment_listing;
						if (lang == "it")
							return "inserzioni creati: " + create_listing + "</br>commenti inserzioni: " + comment_listing;
						return "Listings created: " + create_listing + "</br>Listing comments: " + comment_listing;
					});
				} else if (donutParent == 'transaction') {
					if (childdata['transaction'] != undefined)
						transaction += childdata['transaction'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "transkacije: " + transaction;
						if (lang == "it")
							return "transazioni: " + transaction;
						return "Transactions: " + transaction;
					});
				} else if (donutParent == 'social') {
					if (childdata['conversation'] != undefined)
						conversation += childdata['conversation'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "razgovori: " + conversation;
						if (lang == "it")
							return "conversazioni: " + conversation;
						return "Conversations: " + conversation;
					});
				}
			};
			var descwidth = $("#donutdescription").outerWidth(true);
		})
		.on("mouseout", function (d) {
			d3.select(this).style("filter", "");
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
			if (d.data.children != undefined && d.data.label != undefined) {
				if (d.data.type == 'transaction' || d.data.type == 'social')
					nodename = d.data.target.label.split('_')[1];
				else
					nodename = d.data.name;
				var url = getUrl(d.data.type, nodename);
				//	var win = window.open(url, '_blank');
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
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "broj stvorenih priča: " + create_story + "</br>komentari na priče: " + comment_story;
						if (lang == "it")
							return "storie create: " + create_story + "</br>commenti di storia: " + comment_story;
						return "Stories created: " + create_story + "</br>Story comments: " + comment_story;
					});
				} else if (donutParent == 'listing') {
					if (childdata['create_listing'] != undefined)
						create_listing += childdata['create_listing'].length;
					if (childdata['comment_listing'] != undefined)
						comment_listing += childdata['comment_listing'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "broj unesenih unosa: " + create_listing + "</br>komentari na unosi: " + comment_listing;
						if (lang == "it")
							return "inserzioni creati: " + create_listing + "</br>commenti inserzioni: " + comment_listing;
						return "Listings created: " + create_listing + "</br>Listing comments: " + comment_listing;
					});
				} else if (donutParent == 'transaction') {
					if (childdata['transaction'] != undefined)
						transaction += childdata['transaction'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "transkacije: " + transaction;
						if (lang == "it")
							return "transazioni: " + transaction;
						return "Transactions: " + transaction;
					});
				} else if (donutParent == 'social') {
					if (childdata['conversation'] != undefined)
						conversation += childdata['conversation'].length;
					$("#donutdescription").html(function () {
						if (lang == "hr")
							return "razgovori: " + conversation;
						if (lang == "it")
							return "conversazioni: " + conversation;
						return "Conversations: " + conversation;
					});
				}
			};
			var descwidth = $("#donutdescription").outerWidth(true);
			makeTextNode(donutParent, myReturnText);

			makearcs(d.data.children, true);

		});
	if (areChildren == true) {
		arcs.each(function (d) {
			//Here is some maths to figure out where it goes
			var centrex = 120,
			centrey = 120;
			var startangle = d.startAngle;
			var endangle = d.endAngle;
			var angle = (((startangle + endangle) * (180 / Math.PI)) / 2) * (Math.PI / 180);
			var ypos = centrey + (-Math.cos(angle) * 80);
			var xpos = centrex + Math.sin(angle) * 80;
			var circleg = chartg.append("g").attr("class", "arcimage")
				.attr("transform", "translate(" + xpos + "," + ypos + ")")
				.style("pointer-events", "none");
			circleg.append("circle")
			.attr("r", 15)
			.style("fill", "white")
			.style("stroke-width", "3px")
			.style("stroke", color(d.data.edgemeta[0]));
			circleg.append("svg:image")
			.attr('class', 'donutimage')
			.attr('x', -10)
			.attr('y', -10)
			.attr('width', 20)
			.attr('height', 20)
			.attr("xlink:href", function () {
				var actiontype = d.data.children[0][0];
				if (actiontype == 'create_story')
					return "icons/authorstory.png";
				if (actiontype == 'create_listing')
					return "icons/authorlisting.png";
				if (actiontype == 'comment_story')
					return "icons/commentstory.png";
				if (actiontype == 'comment_listing')
					return "icons/commentlisting.png";
				if (donutParent == 'transaction')
					return "icons/transaction.png";
				if (donutParent == 'social')
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
	returntext.attr("class", "returntext");
}

function italiantranslate(english) {
	if (english == "social")
		return "sociali";
	if (english == "transaction")
		return "transazioni";
	if (english == "listing")
		return "inserzione";
	return "storie";
}
function croatiantranslate(english) {
	if (english == "social")
		return "razgovori";
	if (english == "transaction")
		return "transkacije";
	if (english == "listing")
		return "unosi";
	return "priče";
}

var original_segments;
function plotdonut(graphdata, mydata) {

	$("#donut").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});
	//Have to do the manual mapping
	graphdata.links.forEach(function (e) {
		e.source = isNaN(e.source) ? e.source : graphdata.nodes.filter(function (d) {
				return d.id == e.source;
			})[0];
		e.target = isNaN(e.target) ? e.target : graphdata.nodes.filter(function (d) {
				return d.id == e.target;
			})[0];
		e.children = [];
	});
	var edgetotals = mydata.edgetotals;
	var piesegments = [];
	if (('edgetotals' in mydata)) {
		var edgekeys = Object.keys(edgetotals);
		for (var i = 0; i < edgekeys.length; i++) {
			piesegments.push({
				"name": edgekeys[i],
				"value": edgetotals[edgekeys[i]],
				"children": links_of_type(graphdata, edgekeys[i])
			});
		}
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
		//if (d.data.value > 0)
		if (lang == "hr")
			return croatiantranslate(d.data.name);
		if (lang == "it")
			return italiantranslate(d.data.name);
		return d.data.name;
		//return "";
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