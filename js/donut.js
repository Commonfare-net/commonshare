var currentdonut = 0;
var chart = d3.select("#donut");
var chartg = chart.append("g");
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
var defs = chart.append("defs");

var myReturnText;
if (lang == "hr") {
	myReturnText = "povratak";
} else if (lang == "it") {
	myReturnText = "ritorna";
} else {
	myReturnText = "return";
}
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

//Much code taken from https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html

var arcs = chartg.selectAll(".arc");
var donut_labels = chartg.selectAll(".donutText");
var kcoretext = chartg.append("text")
	.attr("id", "core_text");
var returntext = chart.append("text")
    .attr("id","return_text")
    .text(myReturnText)
    .style("font-size","20px");
var bunchg = chart.append("g").attr('class', 'bunchpack');

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

function getDateText(d) {
	if (lang == 'it') {
		return itDate(ttf(d.date)) + "-" + itDate(ttf(d3.timeWeek.offset(d.date, 2)));
	} else if (lang == 'hr') {
		return hrDate(ttf(d.date)) + "-" + hrDate(ttf(d3.timeWeek.offset(d.date, 2)));
	}
	return ttf(d.date) + "-" + ttf(d3.timeWeek.offset(d.date, 2))
}
function itDate(date) {
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
function hrDate(date) {
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

function links_of_type(d, key) {
	var linktypes = keytypes[key];
	var type_links = [];
	for (var link in d.links) {
		if ((d.links[link].source.id == uid || d.links[link].target.id == uid) &&
			"edgemeta" in d.links[link] && d.links[link].edgemeta.includes(key)) {
			if (d.links[link].target.id == uid) {
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
		var middleLoc, endLoc;
		if ((end - start) < 180) {
			middleLoc = /A(.*?)0 0 1/;
			endLoc = /0 0 1 (.*?)$/;
		} 
        else {
			middleLoc = /A(.*?)0 1 1/;
			endLoc = /0 1 1 (.*?)$/;
		}
		var newStart = endLoc.exec(newArc)[1];
		var newEnd = startLoc.exec(newArc)[1];
		var middleSec = middleLoc.exec(newArc)[1];
		var numbers;
		if ((end - start) < 180) {
			numbers = "0 0 0 ";
		} 
        else {
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
		.attr("d",arc)
		.each(arcMaths)
		.style("fill", color(donutParent))
        .style("filter", "") 
        .on("mouseover",null)
		.on("mouseout",null)
        .on("click",null);
        
        arcs.transition()
        .duration(500)
        .attr("d", biggerarc);
    var bubble = d3.pack()
        .size([width-40, height-40])
        .padding(1.5);
    var data = {"children":piesegments};
    var root = d3.hierarchy(data)
       .sum(function(d) { return d.value ? d.value : 1; });
       
    console.log(root);
    bubble(root); 
        
     var node = chartg.selectAll(".node")
        .data(root.children)
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function(d) {
            console.log(d);
            return "translate(" + (d.x+20) + "," + (d.y+20) + ")";
        });    
        
      node.append("circle")
      .attr("fill",color(donutParent))
      .attr("stroke",function(d){
          //highlight those created
          if(('create_story' in d.data && d.data.create_story.length > 0) ||
            ('create_listing' in d.data && d.data.create_listing.length > 0))
                return 'yellow';
          return 'white';
      })
      .attr("stroke-width","2px")
      .on("mouseover", function (d) {
			d3.select(this)
            .style("cursor", "pointer")
            .style("filter", "url(#glow)");
			oldhtml = $("#donut_description").html();
            console.log("DATA");
            console.log(d.data);
            console.log(d);
			$("#donut_description").html(function(){
                if('transaction' in d.data && donutParent == "transaction"){
                    if(lang=="hr")
                        return "transakcije s tom commoner: " + d.data.transaction.length;
                    else if(lang=="it")
                        return "transazioni con questo commoner: " + d.data.transaction.length;
                    return "transactions with this commoner: " + d.data.transaction.length;
                }
                else if('conversation' in d.data){
                    if(lang=="hr")
                        return "razgovr s " + d.data.name;
                    else if(lang=="it")
                        return "conversazione con" + d.data.name;
                    return "conversation with " + d.data.name;
                }
                var returntext = "<b>"+d.data.name + "</b></br>";
                if('create_story' in d.data && d.data.create_story.length > 0){
                   if(lang=="hr")
                       returntext += "napisao je ovu priču</br>";
                   else if(lang=="it")
                       returntext += "scritto questa storia</br>";
                   else
                       returntext += "wrote this story</br>";
                }
                if('create_listing' in d.data && d.data.create_listing.length > 0){
                   if(lang=="hr")
                       returntext += "izradio je ovaj unos</br>";
                   else if(lang=="it")
                       returntext += "creato questo inserzione</br>";
                   else
                       returntext += "created this listing</br>";
                }
                if('comment_story' in d.data && d.data.comment_story.length > 0){
                   if(lang=="hr")
                       returntext += "komentari na priče: " + d.data.comment_story.length;
                   else if(lang=="it")
                       returntext += "commenti di storia: " + d.data.comment_story.length;
                   else
                    returntext += "received " + d.data.comment_story.length + " comments on this story";
                }
                if('comment_listing' in d.data && d.data.comment_listing.length > 0){
                   if(lang=="hr")
                       returntext += "komentari na unosi: " + d.data.comment_listing.length;
                   else if(lang=="it")
                       returntext += "commenti inserzioni: " + d.data.comment_listing.length;
                   else
                    returntext += "received " + d.data.comment_listing.length + " comments on this listing";
                }
                return returntext;
            });
			return;
		})
		.on("mouseout", function (d) {
			d3.select(this)
            .style("filter", "");;
			$("#donut_description").html(oldhtml);
		})
		.on("click", function (d) {
			//In theory could link to the story/commoner/listing in question here
            //by using their ID. 
		})
      .transition()
      .duration(500)
        .attr("r", function(d) {return d.r;})
        
        
      node.append("text")
      .attr("dy", ".3em")
      .style("text-anchor", "middle")
      .style("fill",function(d){
          //highlight those created
          if(('create_story' in d.data && d.data.create_story.length > 0) ||
            ('create_listing' in d.data && d.data.create_listing.length > 0))
                return 'yellow';
          return 'white';
      })
      .style("pointer-events","none")
      .style("font-size",function(d){return (d.r)+ "px"})
      .text(function(d) {if(donutParent == "transaction")return "cc"; return d.data.name.substr(0,2)});
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
		.style("stroke", function (d) {
			return "none";
		})
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
   $('.arc').on('touchstart',function(e){
      e.preventDefault();
      if($(this).attr("sel") == "true"){
        d3.selectAll('.arc').style("filter","").attr("sel","false");  
        donut_labels.style("visibility", "hidden");
        positionReturnText();
        makechildarcs(d3.select($(this)[0]).datum().data.children);  
      }
      else{
        d3.selectAll('.arc').style("filter","").attr("sel","false");
        $(this).attr("sel","true");
        $(this).css("filter","url(#glow)");
        addInfoText(d3.select($(this)[0]).datum());
      }
         $('.arc').off('touchstart');

   });
}

function addInfoText(d){
    donutParent = d.data.name;
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
            $("#donut_description").html(function () {
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
            $("#donut_description").html(function () {
                if (lang == "hr")
                    return "broj unesenih unosa: " + create_listing + "</br>komentari na unosi: " + comment_listing;
                if (lang == "it")
                    return "inserzioni creati: " + create_listing + "</br>commenti inserzioni: " + comment_listing;
                return "Listings created: " + create_listing + "</br>Listing comments: " + comment_listing;
            });
        } else if (donutParent == 'transaction') {
            if (childdata['transaction'] != undefined)
                transaction += childdata['transaction'].length;
            $("#donut_description").html(function () {
                if (lang == "hr")
                    return "transkacije: " + transaction;
                if (lang == "it")
                    return "transazioni: " + transaction;
                return "Transactions: " + transaction;
            });
        } else if (donutParent == 'social') {
            if (childdata['conversation'] != undefined)
                conversation += childdata['conversation'].length;
            $("#donut_description").html(function () {
                if (lang == "hr")
                    return "razgovori: " + conversation;
                if (lang == "it")
                    return "conversazioni: " + conversation;
                return "Conversations: " + conversation;
            });
        }
    };
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
function positionCommonshareText(){
    returntext.style("display","none");
    kcoretext.style("display","block");
    var kcorenode = kcoretext.node();
	var kcorewidth = kcorenode.getBoundingClientRect().width;
	var kcoreheight = kcorenode.getBoundingClientRect().height;

	kcoretext.attr("transform", "translate(" + ((width / 2) - (kcorewidth / 2)) +
		"," + ((height / 2) + (kcoreheight / 4)) + ")");    
}

function positionReturnText(){
    returntext.style("display","inline-block");
	kcoretext.style("display","none");
    var returntextnode = returntext.node();
	var returnwidth = returntextnode.getBoundingClientRect().width;
	var returnheight = returntextnode.getBoundingClientRect().height;
	returntext.attr("transform", "translate(" + ((width / 2) - (returnwidth / 2)) +
		",15)");
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
	kcoretext.text(function(){
     if(mydata.kcore == "0"){
         kcoretext.style('font-size','16px');
         if(lang=="hr")
             return "nema vidljive aktivnosti";
         else if(lang=="it")
             return "nessuna attività visibile";
         return "No visible activity";
     }
     kcoretext.style('font-size','60px');
     kcoretext.style('fill','var(--cf-green)');
     kcoretext.style('font-weight','700');
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