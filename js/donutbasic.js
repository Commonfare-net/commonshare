
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

var width = 240;
var height = 280;
var donutParent;
var index = 0;

/**
* Some local donut variables
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

    //https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html
    arcs = chartg.selectAll(".arc");
    donut_labels = chartg.selectAll(".donutText");
    kcoretext = chartg.append("text")
        .attr("id", "core_text");
}

function plotBasicDonut(graphdata, mydata) {
    $("#donutdate").text(getDateText(mydata));
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
    var edgetotals = mydata.edgetotals;
    var piesegments = [];
    if ("edgetotals" in mydata) {
        var edgekeys = Object.keys(edgetotals);
        for (i = 0; i < edgekeys.length; i+=1) {
            piesegments.push({
                "name": edgekeys[i],
                "value": edgetotals[edgekeys[i]],
                "children": links_of_type(graphdata, edgekeys[i])
            });
        }
    }
    original_segments = piesegments;

    //Default text rather than just displaying
    //a big 0 when the commoner has done nothing
    kcoretext.text(function () {
        if (mydata.kcore == "0") {
            kcoretext.style("font-size", "16px");
            return noActivityText;
        }
        kcoretext.style("font-size", "60px");
        kcoretext.style("fill", "var(--cf-green)");
        kcoretext.style("font-weight", "700");
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
        if (lang == "hr"){
            return croatiantranslate(d.data.name);
        }
        if (lang == "it"){
            return italiantranslate(d.data.name);
        }
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
}
/**
* Called when user clicks left (value = 1) or right (value = -1) arrow
**/
function updateBasicDonut(value) {
    if (value == -1) {
        index = Math.min(maxindex - 1, ++index);
    } else {
        index = Math.max(0, --index);
    }
    plotBasicDonut(graph_data[index], node_data[index]);
    $("#donut_description").html("");
}

function links_of_type(d, key) {
    var types = keytypes[key];
    var type_links = [];
    Object.keys(d.links).forEach(function(link){
        if ((d.links[link].source.id == uid ||
            d.links[link].target.id == uid) &&
            "edgemeta" in d.links[link] &&
            d.links[link].edgemeta.includes(key)) {
            if (d.links[link].target.id == uid) {
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
                for (y = 0; y < array.length; y+=1) {
                    d.links[link].children.push([types[x]].concat(array[y]));
                }
            });
            type_links.push(d.links[link]);
        }
    });
    return type_links;
}

/**
* Maths to determine where the arcs need to begin and end
**/
function arcMaths(d, i) {
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
    .attr("id", "donutArc" + i)
    .attr("d", newArc)
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
    .style("fill", "none");
}

function makearcs(piesegments) {
    d3.selectAll(".node")
    .remove();
    arcs = arcs.data(pie(piesegments));
    arcs.exit().remove();
    d3.selectAll(".hiddenDonutArcs").remove();
    d3.selectAll(".arcimage").remove();
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
    $(".arc").off("touchstart");
    $(".arc").on("touchstart", function (e) {
        e.preventDefault();
        d3.selectAll(".arc").style("filter", "").attr("sel", "false");
        $(this).attr("sel", "true");
        $(this).css("filter", "url(#glow)");
        addInfoText(d3.select($(this)[0]).datum());
        $(".arc").off("touchstart");
    });
}

function addInfoText(d) {
    $("#donut_description").html(function () {
        return "none yet";//donutSummaryTranslate(donutParent,var1count,var2count);
    });
}
function arcTween(a) {
    delete this.current.data;
    delete a.data;
    var i = d3.interpolate(this.current, a);
    this.current = i(0);
    return function (t) {
        return arc(i(t));
    };
}

function positionCommonshareText() {
    kcoretext.style("display", "block");
    var kcorenode = kcoretext.node();
    var kwidth = kcorenode.getBoundingClientRect().width;
    var kcoreheight = kcorenode.getBoundingClientRect().height;

    kcoretext.attr("transform", "translate(" + ((width/2) - (kwidth/2)) +
        "," + ((height / 2) + (kcoreheight / 4)) + ")");
}

var original_segments;