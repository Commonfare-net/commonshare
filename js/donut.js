var currentdonut = 0;

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

var biggerarc = d3.arc()
	.outerRadius(120)
	.innerRadius(100);

d3.selectAll(".textpath")
.attr("xlink:href", function (d, i) {
	return "#donutArc" + i;
})

var width = 240,
height = 280;
var donutParent;

function updateDonut(value) {
	if (value == -1) {
		currentdonut = Math.min(maxindex - 1, ++currentdonut);
	} else {
		currentdonut = Math.max(0, --currentdonut);
	}
	plotdonut(graph_data[currentdonut], node_data[currentdonut]);
	$('#donut_description').html('');
}

function links_of_type(d, key) {
    var platform_uid;
    for (var n in d.nodes){
        if(d.nodes[n].platform_id == uid){
            platform_uid = d.nodes[n].id;
            console.log("platform_uid is " + platform_uid);
            break;
        }
    }    
	var linktypes = keytypes[key];
	var type_links = [];
	for (var link in d.links) {
		if ((d.links[link].source.id == platform_uid || d.links[link].target.id == platform_uid) &&
			"edgemeta" in d.links[link] && d.links[link].edgemeta.includes(key)) {
			if (d.links[link].target.id == platform_uid) {
				target = d.links[link].source;
			} else {
				target = d.links[link].target;
			}
			d.links[link]["name"] = target.t;
			d.links[link]["value"] = d.links[link].edgeweight[target.id];
			for (var x in linktypes) {
				if (d.links[link][linktypes[x]] == undefined) {
					continue;
				}
				var array = d.links[link][linktypes[x]];
				for (var y = 0; y < array.length; y++) {
					d.links[link]["children"].push([linktypes[x]].concat(array[y]));
				}
			}
			type_links.push(d.links[link]);
		}
	}
	return type_links;
}

//Some mathematics to determine where the arcs need to begin and end
function arcMaths(d, i) {
	this._current = d;
	var firstArcSection = /(^.+?)L/;
	var wholeArcSection = /[^A]*A[^A]*/;
	var regex = firstArcSection.exec(d3.select(this).attr("d"));
	var newArc;
	if (regex == null) {
		regex = wholeArcSection.exec(d3.select(this).attr("d"));
		newArc = regex[0];
	} else {
		newArc = regex[1];
	}
	newArc = newArc.replace(/,/g, " ");
	var end = (d.endAngle / (Math.PI / 180));
	var start = (d.startAngle / (Math.PI / 180));

	if (d.endAngle > 90 * Math.PI / 180 &&
		start > (180 - end) &&
		(end - start) % 360 != 0) {
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
		if ((end - start) < 180) {
			numbers = "0 0 0 ";
		} else {
			numbers = "0 1 0 ";
		}
		newArc = "M" + newStart + "A" + middleSec + numbers + newEnd;
	}
	chartg.append("path")
	.attr("class", "hiddenDonutArcs")
	.attr("id", "donutArc" + i)
	.attr("d", newArc)
	.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
	.style("fill", "none");
}
function makechildarcs(piesegments) {
	console.log(piesegments);
	arcs = arcs.data(pie(piesegments));
	arcs.exit().remove();
	d3.selectAll(".hiddenDonutArcs").remove();
	//All this does now is make a nice coloured circle.
	//There is surely an easier way but it doesn't really matter.
	arcs = arcs.enter().append("path")
		.attr("id", function (d, i) {
			return "monthArc_" + i;
		})
		.attr("class", "arc")
		.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
		.merge(arcs)
		.attr("d", arc)
		.each(arcMaths)
		.style("fill", color(donutParent))
		.style("filter", "")
		.on("mouseover", null)
		.on("mouseout", null)
		.on("click", null);

	arcs.transition()
	.duration(500)
	.attr("d", biggerarc);
	var bubble = d3.pack()
		.size([width - 40, height - 40])
		.padding(1.5);
	var data = {
		"children": piesegments
	};
	var root = d3.hierarchy(data)
		.sum(function (d) {
			return d.value ? d.value : 1;
		});
	bubble(root);

	var node = chartg.selectAll(".node")
		.data(root.children)
		.enter()
		.append("g")
		.attr("class", "node")
		.attr("transform", function (d) {
			return "translate(" + (d.x + 20) + "," + (d.y + 20) + ")";
		});

	node.append("circle")
	.attr("fill", color(donutParent))
	.attr("stroke", function (d) {
		//highlight those created
		if (('create_story' in d.data && d.data.create_story.length > 0) ||
			('create_listing' in d.data && d.data.create_listing.length > 0))
			return 'yellow';
		return 'white';
	})
	.attr("stroke-width", "2px")
	.on("mouseover", function (d) {
		d3.select(this)
		.style("cursor", "pointer")
		.style("filter", "url(#glow)");
		oldhtml = $("#donut_description").html();
		$("#donut_description").html(function () {
			if ('transaction' in d.data && donutParent == "transaction") {
                return donutTranslate('transaction') +d.data.transaction.length;
			}
            if ('conversation' in d.data) {
                return donutTranslate('conversation') + d.data.name;
			}
            var returntext = "<b>" + d.data.name + "</b></br>";
			if ('create_story' in d.data && d.data.create_story.length > 0){
				returntext += donutTranslate('create_story');
			}
			if ('create_listing' in d.data && d.data.create_listing.length > 0){
                returntext += donutTranslate('create_listing');
			}
			if ('comment_story' in d.data && d.data.comment_story.length > 0){
				returntext += d.data.comment_story.length +
                donutTranslate('comment_story');
			}
			if ('comment_listing' in d.data && d.data.comment_listing.length > 0){
                returntext += d.data.comment_listing.length +
                donutTranslate('comment_listing');
			}
			return returntext;
		});
	})
	.on("mouseout", function (d) {
		d3.select(this)
		.style("filter", ""); ;
		$("#donut_description").html(oldhtml);
	})
	.on("click", function (d) {
		//In theory could link to the story/commoner/listing in question here
		//by using their ID.
	})
	.transition()
	.duration(500)
	.attr("r", function (d) {
		return d.r;
	})

	node.append("text")
	.attr("dy", ".3em")
	.style("text-anchor", "middle")
	.style("fill", function (d) {
		//highlight those created
		if (('create_story' in d.data && d.data.create_story.length > 0) ||
			('create_listing' in d.data && d.data.create_listing.length > 0))
			return 'yellow';
		return 'white';
	})
	.style("pointer-events", "none")
	.style("font-size", function (d) {
		return (d.r) + "px"
	})
	.text(function (d) {
		if (donutParent == "transaction")
			return "cc";
		return d.data.name.substr(0, 2)
	});
}

function makearcs(piesegments) {
	d3.selectAll(".node")
	.remove();
	arcs = arcs.data(pie(piesegments));
	arcs.exit().remove();
	d3.selectAll(".hiddenDonutArcs").remove();
	d3.selectAll(".arcimage").remove()
	donut_labels.style("visibility", "visible");
	var oldhtml;
	arcs = arcs.enter().append("path")
		.attr("id", function (d, i) {
			return "monthArc_" + i;
		})
		.attr("class", "arc")
		.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
		.merge(arcs)
		.attr("d", arc)
		.each(arcMaths)
		.style("fill", function (d) {
			return color(d.data.name);
		})
		.style("stroke","none")
		.style("stroke-width", "0")
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer")
			.style("filter", "url(#glow)");
			addInfoText(d);
		})
		.on("mouseout", function (d) {
			d3.select(this).style("filter", "");
			d3.select(this).style("fill", color(d.data.name));
			kcoretext.style("display", "block");
		})
		.on("click", function (d) {
			donut_labels.style("visibility", "hidden");
			positionReturnText();
			makechildarcs(d.data.children);
		});
	$('.arc').off('touchstart');
	$('.arc').on('touchstart', function (e) {
		e.preventDefault();
		if ($(this).attr("sel") == "true") {
			d3.selectAll('.arc').style("filter", "").attr("sel", "false");
			donut_labels.style("visibility", "hidden");
			positionReturnText();
			makechildarcs(d3.select($(this)[0]).datum().data.children);
		} else {
			d3.selectAll('.arc').style("filter", "").attr("sel", "false");
			$(this).attr("sel", "true");
			$(this).css("filter", "url(#glow)");
			addInfoText(d3.select($(this)[0]).datum());
		}
		$('.arc').off('touchstart');

	});
}

function addInfoText(d) {
	donutParent = d.data.name;
    var1count = 0, var2count = 0;
    if (donutParent == "story") {
        var1 = "create_story"; var2 = "comment_story";
    }
    else if(donutParent == "listing"){
        var1 = "create_listing";var2 = "comment_listing";
    }
    else if(donutParent == "transaction"){
        var1 = "transaction";var2 = "transaction";
    }
    else{
        var1 = "conversation";var2 = "conversation";
    }
	for (var i = 0; i < d.data.children.length; i++) {
		var childdata = d.data.children[i];
        if(childdata[var1] != undefined)
            var1count += childdata[var1].length;
        if(childdata[var2] != undefined)
            var2count += childdata[var2].length;
	};
    $("#donut_description").html(function () {
        return donutSummaryTranslate(donutParent,var1count,var2count);
    });
}
function arcTween(a) {
	delete this._current["data"];
	delete a["data"];
	var i = d3.interpolate(this._current, a);
	this._current = i(0);
	return function (t) {
		return arc(i(t));
	};
}

//GIANLUCA Depending on the number of digits in the commonshare
//Or width of the 'return' text, these are dynamically positioned in
//the two functions below.
function positionCommonshareText() {
	returntext.style("display", "none");
	kcoretext.style("display", "block");
	var kcorenode = kcoretext.node();
	var kcorewidth = kcorenode.getBoundingClientRect().width;
	var kcoreheight = kcorenode.getBoundingClientRect().height;

	kcoretext.attr("transform", "translate(" + ((width / 2) - (kcorewidth / 2)) +
		"," + ((height / 2) + (kcoreheight / 4)) + ")");
}

function positionReturnText() {
	returntext.style("display", "inline-block");
	kcoretext.style("display", "none");
	var returntextnode = returntext.node();
	var returnwidth = returntextnode.getBoundingClientRect().width;
	returntext.attr("transform", "translate(" + ((width/2)-(returnwidth/2)) + ",15)");
}

var original_segments;

// initialise variables here to avoid declaring them globally
function initDonutVars() {
	chart = d3.select("#donut");
	chartg = chart.append("g");
	defs = chart.append("defs");


	//Filter for the outside glow
	filter = defs.append("filter")
		.attr("id", "glow");
	filter.append("feGaussianBlur")
		.attr("stdDeviation", "3.5")
		.attr("result", "coloredBlur");

	feMerge = filter.append("feMerge");
	feMerge.append("feMergeNode")
		.attr("in", "coloredBlur");
	feMerge.append("feMergeNode")
		.attr("in", "SourceGraphic");

	//https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html

	arcs = chartg.selectAll(".arc");
	donut_labels = chartg.selectAll(".donutText");
	kcoretext = chartg.append("text")
		.attr("id", "core_text");
	returntext = chart.append("text")
		.attr("id", "return_text")
		.text(myReturnText)
		.style("font-size", "20px");
	bunchg = chart.append("g").attr('class', 'bunchpack');
}

function plotdonut(graphdata, mydata) {
	$('#donutdate').text(getDateText(mydata));

	$("#donut").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

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

	//GIANLUCA Here I add some default text rather than just displaying
	//a big 0 when the commoner has done nothing
	kcoretext.text(function () {
		if (mydata.kcore == "0") {
			kcoretext.style('font-size', '16px');
            return noActivityText;
		}
		kcoretext.style('font-size', '60px');
		kcoretext.style('fill', 'var(--cf-green)');
		kcoretext.style('font-weight', '700');
		return mydata.kcore;
	});
	positionCommonshareText();
	$("#desc").html("");
	makearcs(piesegments);

	donut_labels = donut_labels.data(pie(piesegments));
	donut_labels.exit().remove();
	donut_labels = donut_labels
		.enter().append("text")
		.merge(donut_labels)
		.attr("class", "donutText")
		.attr("dy", function (d, i) {
			var degreeEnd = (d.endAngle / (Math.PI / 180));
			var degreeStart = (d.startAngle / (Math.PI / 180));
			return (d.endAngle > 90 * Math.PI / 180
				 && degreeStart > (180 - degreeEnd)
				 && ((degreeEnd - degreeStart) % 360 != 0) ? 18 : -11);
		});

	d3.selectAll(".textpath").remove();
	donut_labels.append("textPath")
	.text(function (d) {
		if (lang == "hr")
			return croatiantranslate(d.data.name);
		if (lang == "it")
			return italiantranslate(d.data.name);
		return d.data.name;
	})
	.attr("class", "textpath")
	.attr("startOffset", "50%")
	.attr("xlink:href", function (d, i) {
		return "#donutArc" + i;
	})
	.style("fill", function (d) {
		return color(d3.select(this).text());
	});

	//GIANLUCA Functions for what happens when mouse is over/out of 'return' text
	returntext.on("mouseover", function (d) {
		d3.select(this).style("cursor", "pointer");
		d3.select(this).style("fill", "#E7472E");
	})
	.on("mouseout", function (d) {
		d3.select(this).style("fill", "var(--cf-green)");
	})
	.on("click", function (d) {
		donut_labels
		.style("visibility", "visible")
		.style("fill", function (d) {
			return color(d3.select(this).text());
		});
		kcoretext.style("display", "inline-block");
		$("#desc").html("");
		positionCommonshareText();
		makearcs(original_segments);
	});
}
