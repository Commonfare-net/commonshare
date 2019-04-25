//A default D3 pie chart generator
var pie = d3.pie()
    .startAngle(-90 * Math.PI / 180)
    .endAngle(-90 * Math.PI / 180 + 2 * Math.PI)
    .sort(null)
    .value(function (d) {
        return d.value;
    });

//Arc for the donut segments
var arc = d3.arc()
    .outerRadius(90)
    .innerRadius(70);

//Arc along which text labels are displayed
var biggerarc = d3.arc()
    .outerRadius(120)
    .innerRadius(100);

d3.selectAll(".textpath")
.attr("xlink:href", function (d, i) {
    return "#donutArc" + i;
});

var keytypes = {
    "story": ["create_story", "comment_story"],
    "listing": ["create_listing", "comment_listing"],
    "transaction": ["transaction"],
    "social": ["conversation"]
};
var width = 240;
var height = 280;
var donutParent;
var index = 0;

var original_segments;

/**
* Set up donut position and local variables
**/
function initDonutVars() {
    var chart = d3.select("#donut");
    chartg = chart.append("g");
    defs = chart.append("defs");

    //Filters for the outside glow
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

    arcs = chartg.selectAll(".arc");
    donut_labels = chartg.selectAll(".donutText");
    kcoretext = chartg.append("text")
        .attr("id", "core_text");
    returntext = chart.append("text")
        .attr("id", "return_text")
        .text(myReturnText)
        .style("font-size", "20px");
        //Functions for what happens with "return" text
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
        generateArcs(original_segments);
    });
    bunchg = chart.append("g").attr("class", "bunchpack");
}

/**
* Called every time a new donut needs to be generated. Updates 'graphdata' to ensure links point to
* node data and not just node IDs, generates a JSON array of the Commoner's interactions for each type,
* and positions the initial donut segments, labels, and commonshare value text
* @param {json} graphdata - JSON representation of ego-centric graph of Commoner's interactions
* @param {json} mydata - JSON representation of node-specific data of the Commoner
*/
function plotDonut(graphdata, nodedata) {
    $("#donutdate").text(getDateText(nodedata));

    $("#donut").bind("wheel mousewheel", function (e) {
        e.preventDefault();
    });

    //Awkward bit of code to ensure that the 'source' and 'target' of each
    //edge are node objects themselves and not just their IDs
    graphdata.links.forEach(function (e) {
        e.source = (
        Number.isNaN(Number(e.source)) ? e.source : graphdata.nodes.filter(
        function (d) {
                return d.id == e.source;
            })[0]);
        e.target = (
        Number.isNaN(Number(e.target)) ? e.target : graphdata.nodes.filter(
        function (d) {
                return d.id == e.target;
            })[0]);
        e.children = [];
    });
    var edgetotals = nodedata.edgetotals;
    var piesegments = [];
    if ("edgetotals" in nodedata) {
        var edgekeys = Object.keys(edgetotals);
        for (i = 0; i < edgekeys.length; i+=1) {
            piesegments.push({
                "name": edgekeys[i],
                "value": edgetotals[edgekeys[i]],
                "children": interactionsOfType(graphdata, edgekeys[i])
            });
        }
    }
    original_segments = piesegments;

    //Default text rather than just displaying
    //a big 0 when the commoner has done nothing
    kcoretext.text(function () {
        if (nodedata.kcore == "0") {
            kcoretext.style("font-size", "16px");
            return noActivityText;
        }
        kcoretext.style("font-size", "60px");
        kcoretext.style("fill", "var(--cf-green)");
        kcoretext.style("font-weight", "700");
        return nodedata.kcore;
    });
    positionCommonshareText();
    $("#desc").html("");
    generateArcs(piesegments);

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
        return translate(d.data.name);
    })
    .attr("class", "textpath")
    .attr("startOffset", "50%")
    .attr("xlink:href", function (d, i) {
        return "#donutArc" + i;
    })
    .style("fill", function (d) {
        return color(d3.select(this).text());
    });
}
/**
* Function tied to the arrows on the donut date picker; updates donut
* to show donut for earlier or later actions
* @param {int} value - sets whether to show earlier (-1) or later (1) donut
*/
function updateDonut(value) {
    if (value == -1) {
        index = Math.min(maxindex - 1, ++index);
    } else {
        index = Math.max(0, --index);
    }
    plotDonut(graph_data[index], node_data[index]);
    $("#donut_description").html("");
}

/**
* Finds links in the interaction graph coming from the Commoner in question,
* filters based on the given interaction type (e.g., story, social) and returns
* these in a JSON array
* @param {json} d - JSON representation of all graph data at this time
* @param {string} key - string reprsenting interaction type to filter on
* @returns {json[]} - JSON array of interactions of type 'key'
*/
function interactionsOfType(d, key) {
    var platform_uid = uid;
    //Matches GEXF IDs to platform IDs 
    //(unless we're on personal_viz.html)
    if(window.location.href.includes("personal_viz")){
        for (var n in d.nodes){
            if(d.nodes[n].platform_id == uid){
                platform_uid = d.nodes[n].id;
                console.log("platform_uid is " + platform_uid);
                break;
            }
        }
    }
    var types = keytypes[key];
    var type_links = [];
    Object.keys(d.links).forEach(function(link){
        if ((d.links[link].source.id == platform_uid ||
            d.links[link].target.id == platform_uid) &&
            "edgemeta" in d.links[link] &&
            d.links[link].edgemeta.includes(key)) {
            if (d.links[link].target.id == platform_uid) {
                target = d.links[link].source;
            } else {
                target = d.links[link].target;
            }
            d.links[link].name = target.t;
            d.links[link].value = d.links[link].edgeweight[target.id];
            Object.keys(types).forEach(function(x){
                if (d.links[link][types[x]] == undefined) {
                    return;
                }
                var array = d.links[link][types[x]];
                for (obj = 0; obj < array.length; obj+=1) {
                    d.links[link].children.push([types[x]].concat(array[obj]));
                }
            });
            type_links.push(d.links[link]);
        }
    });
    return type_links;
}

/**
* Function to create the path of a donut arc's text, by inspecting
* and modifying the path of the arc itself.
* Code from https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html
* @param {json} d - JSON representation of the arc path
* @param {int} index - index of data being shown in the 'data' array
*/
function calculateTextPath(d, index) {
    this.current = d;
    var firstArcSection = /(^.+?)L/m;
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
        var middleLoc;
        var endLoc;
        if ((end - start) < 180) {
            middleLoc = /A(.*?)0\s0\s1/;
            endLoc = /0\s0\s1\s(.*?)$/;
        } else {
            middleLoc = /A(.*?)0\s1\s1/;
            endLoc = /0\s1\s1\s(.*?)$/;
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
    .attr("id", "donutArc" + index)
    .attr("d", newArc)
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
    .style("fill", "none");
}

/**
* This generates the 'bubble' view of a Commoner's interactions of a certain type, 
* called when a donut segment is clicked or double-tapped on. Creates a bubble for
* each object interacted with (i.e., each story or each Commoner)
* @param {json[]} piesegments - JSON array of interactions specific to clicked segment
*/
function generateBubbles(piesegments) {
    arcs = arcs.data(pie(piesegments));
    arcs.exit().remove();
    d3.selectAll(".hiddenDonutArcs").remove();
    //All this does now is make a nice coloured circle.
    //There is surely an easier way but it doesn"t really matter.
    arcs = arcs.enter().append("path")
        .attr("id", function (d, i) {
            return "monthArc_" + i;
        })
        .attr("class", "arc")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
        .merge(arcs)
        .attr("d", arc)
        //.each(arcMaths)
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
            return (
            d.value ? d.value : 1);
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
        if (("create_story" in d.data && d.data.create_story.length > 0) ||
            ("create_listing" in d.data && d.data.create_listing.length > 0)){
            return "yellow";
        }
        return "white";
    })
    .attr("stroke-width", "2px")
    .on("mouseover", function (d) {
        d3.select(this)
        .style("cursor", "pointer")
        .style("filter", "url(#glow)");
        oldhtml = $("#donut_description").html();
        $("#donut_description").html(function () {
            if ("transaction" in d.data && donutParent == "transaction") {
                return translate("donuttransaction") +d.data.transaction.length;
            }
            if ("conversation" in d.data) {
                return translate("donutconversation") + d.data.name;
            }
            var returntext = "<b>" + d.data.name + "</b></br>";
            if ("create_story" in d.data && d.data.create_story.length > 0){
                returntext += translate("donutcreate_story");
            }
            if ("create_listing" in d.data && d.data.create_listing.length > 0){
                returntext += translate("donutcreate_listing");
            }
            if ("comment_story" in d.data && d.data.comment_story.length>0){
                returntext += d.data.comment_story.length +
                translate("donutcomment_story");
            }
            if ("comment_listing" in d.data && d.data.comment_listing.length>0){
                returntext += d.data.comment_listing.length +
                translate("donutcomment_listing");
            }
            return returntext;
        });
    })
    .on("mouseout", function (d) {
        d3.select(this)
        .style("filter", "");
        $("#donut_description").html(oldhtml);
    })
    .transition()
    .duration(500)
    .attr("r", function (d) {
        return d.r;
    });

    node.append("text")
    .attr("dy", ".3em")
    .style("text-anchor", "middle")
    .style("fill", function (d) {
        //highlight those created
        if (("create_story" in d.data && d.data.create_story.length > 0) ||
            ("create_listing" in d.data && d.data.create_listing.length > 0)){
            return "yellow";
        }
        return "white";
    })
    .style("pointer-events", "none")
    .style("font-size", function (d) {
        return (d.r) + "px";
    })
    .text(function (d) {
        if (donutParent == "transaction"){
            return "cc";
        }
        return d.data.name.substr(0, 2);
    });
}


/**
* Positions the segments of the donut and their text labels based on a JSON array of
* interaction types, and adds all touch/hover/click listeners on the segments
* @param {json[]} piesegments - JSON array representing interaction types
*/
function generateArcs(piesegments) {
    d3.selectAll(".node")
    .remove();
    arcs = arcs.data(pie(piesegments));
    arcs.exit().remove();
    d3.selectAll(".hiddenDonutArcs")
    .remove();
    d3.selectAll(".arcimage")
    .remove();
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
        .each(calculateTextPath)
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
            generateBubbles(d.data.children);
        });
    $(".arc").off("touchstart");
    $(".arc").on("touchstart", function (e) {
        e.preventDefault();
        if ($(this).attr("sel") == "true") {
            d3.selectAll(".arc").style("filter", "").attr("sel", "false");
            donut_labels.style("visibility", "hidden");
            positionReturnText();
            generateBubbles(d3.select($(this)[0]).datum().data.children);
        } else {
            d3.selectAll(".arc").style("filter", "").attr("sel", "false");
            $(this).attr("sel", "true");
            $(this).css("filter", "url(#glow)");
            addInfoText(d3.select($(this)[0]).datum());
        }
        $(".arc").off("touchstart");

    });
}

/**
* Generates additional information text underneath the donut when user hovers over (desktop)
* or taps on (mobile) a donut segment. Text is dependent on type of data the segment represents
* @param {json} d - Underlying JSON data of donut segment
*/
function addInfoText(d) {
    donutParent = d.data.name;
    var1count = 0;
    var2count = 0;
    console.log(d.data);
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
    for (i = 0; i < d.data.children.length; i+=1) {
        childdata = d.data.children[i];
        if(childdata[var1] != undefined){
            var1count += childdata[var1].length;
        }
        if(childdata[var2] != undefined){
            var2count += childdata[var2].length;
        }
    }
    console.log("var1count: " + var1count + ", var2count: " + var2count);
    $("#donut_description").html(function () {
        return donutSummaryTranslate("donut"+donutParent,var1count,var2count);
    });
}

/**
* Positions commonshare value in the centre of the donut, which is dependent
* on its width
*/
function positionCommonshareText() {
    returntext.style("display", "none");
    kcoretext.style("display", "block");
    var kcorenode = kcoretext.node();
    var kwidth = kcorenode.getBoundingClientRect().width;
    var kcoreheight = kcorenode.getBoundingClientRect().height;

    kcoretext.attr("transform", "translate(" + ((width/2) - (kwidth/2)) +
        "," + ((height / 2) + (kcoreheight / 4)) + ")");
}

/**
* Centres 'return' text, which is also dependent on its width in a
* given language
*/
function positionReturnText() {
    returntext.style("display", "inline-block");
    kcoretext.style("display", "none");
    var returntextnode = returntext.node();
    var rwidth = returntextnode.getBoundingClientRect().width;
    returntext.attr("transform", "translate("+((width/2)-(rwidth/2))+",15)");
}