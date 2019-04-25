/**
* This file contains all the code for responding to the graph 'widgets'
**/

var df = d3.timeFormat("%d/%m/%y");
var currentDate;
var dateslidex;

/**
* Helper function to get unique values from an array
**/
Array.prototype.unique = function () {
    var a = this.concat();
    for (i = 0; i < a.length; i+=1) {
        for (j = i + 1; j < a.length; j+=1) {
            if (a[i] === a[j]){
                a.splice(j, 1);
                j-=1;
            }
        }
    }
    return a;
};

/**
* Toggle whether to show/hide tag nodes and edges
* @param {checkbox} chk - HTML checkbox element
**/
function toggleTags(chk) {
    var opacity = (chk.checked) ? 0 : 1;
    node.each(function (d) {
        if (d.type == "tag"){
            d3.select(this).style("opacity", opacity);
        }
    });
    link.each(function (d) {
        if (d.source.type == "tag" || d.target.type == "tag"){
            d3.select(this).style("opacity", opacity);
        }
    });
}

/**
* Toggle whether to show the cumulative graph or the slider
* @param {checkbox} chk - HTML checkbox element
**/
function toggleDate(chk) {
    clearDyn();
    //Show the cumulative graph?
    if (chk.checked) {
        len = Object.keys(data).length;
        $("#curdate").text(df(parseTime(data[len-1].date)) +
        " to " + df(parseTime(data[1].date)));
        $("#myslider").css("opacity", 0.4);
        $("#myslider").css("pointer-events", "none");
        currentDate = data[1].date;
        sliderhandle.attr("cx", dateslidex(Object.keys(data).length - 1));
        indexstart = 0;
        draw();
    //Show the dynamic graphs
    } else {
        $("#curdate").text(df(parseTime(data[1].date))+" to "+
        df(d3.utcDay.offset(parseTime(data[1].date), 7)));
        $("#myslider").css("opacity", 1);
        $("#myslider").css("pointer-events", "auto");
        indexstart = 1;
        draw();
    }
}

/**
* There are list boxes for both the dynamic communities and
* the tag names/counts. This function fills them with the 
* data from the graph files
**/
function populateListBoxes(){
    tagcounts = graph.tagcount;
    dc = (
    "dynamic_comms" in graph ? graph.dynamic_comms : {});

    Object.keys(dc).forEach(function(comm){
        global_community = [];
        dates = [];
        for (i = 0; i < dc[comm].length; i += 2) {
            dates.push(dc[comm][i]);
        }
        for (i = 1; i < dc[comm].length; i += 2) {
            global_community = global_community.concat(dc[comm][i]);
        }
        global_communities[comm] = [global_community.unique(), dates];
    });
    var commContainer = $("#comm-group");
    var commMembers = $("#comm-members");
    commContainer.empty();
    Object.keys(global_communities).forEach(function(comm){
        commContainer.append("<a href='#' class='list-group-item community'>" +
        comm + "</a>");
    });
    $(".community").click(function (e) {
        e.preventDefault();
        commMembers.empty();
        d3.selectAll(".marker").remove();
        name = $(this).text();
        c_nodes = global_communities[name][0];
        for (i = 0; i < c_nodes.length; i+=1) {
            commMembers.append(
            "<a href='#' class='list-group-item community'>" +
            ids_to_titles[c_nodes[i]] + "</a>");
        }
        for (com = 0; com < global_communities[name][1].length; com+=1) {
            date = global_communities[name][1][com];
            xpos = dateslidex(Object.keys(data).length - date - 1);
            ypos = -10;
            dateslider.append("path")
            .attr("d", "M " + xpos + " " + ypos + " l -4 -8 l 8 0 z")
            .attr("class", "marker");
        }
        if (indexstart == 0) {
            var hull = d3.polygonHull(c_nodes.map(function (d) {
                return [d3.select("#n" + indexstart + "_" + d).attr("cx"),
                d3.select("#n" + indexstart + "_" + d).attr("cy")];
            }));
            convexHull.datum(hull).attr("d", function (d) {
                return "M" + d.join("L") + "Z";
            });
            d3.select(".hull").style("opacity", 0.6);
        } else {
            draw();
        }
    });
    
    //Populates the tag list box with the tag names and counts
    var listBox = $("#list-group");
    if (taglistindex != indexstart) {
        taglistindex = indexstart;
        listBox.empty();
        if(tagcounts != null){
            for (i = 0; i < tagcounts.length; i+=1) {
                tagname = tagcounts[i][0];
                tagnum = tagcounts[i][1];
                listBox.append("<a href='#' class='list-group-item taga'>"+
                tagname + "<span class='badge'>" + tagnum + "</span></a>");
            }
        }
        $(".taga").click(function (e) {
            e.preventDefault();
            filtertype = "tag";
            tag = $(this).ignore("span").text();
            draw();
        });
    }
}

//Functions to clear tag/network/community filters
$("#cleartags").click(function (e) {
    e.preventDefault();
    tag = "all";
    draw();
    return false;
});
$("#clearnw").click(function (e) {
    e.preventDefault();
    tag = "all";
    draw();
    return false;
});
$("#cleardyn").click(function (e) {
    e.preventDefault();
    clearDyn();
});

//Function for filtering based on network type buttons
function nwfilter(nwname) {
    filtertype = "network";
    tag = nwname;
    draw();
}

/**
* Updates the strength slider with new maximum value. This involves changing
* the tick positions as well as the x-position of the handle on the updated scale
* @param {int} currentpos - position of handle on strength slider before updating
* @param {int} maxval - new maximum value of strength slider after updating
**/
function updateStrengthSlider(currentpos, maxval) {
    var ss = document.getElementById("strengthSlider");
    var strengthslidersvg = d3.select(".strengthslider");
    margin = {
        right: 50,
        left: 50,
        top: 100,
        bottom: 50
    };
    var height = +strengthslidersvg.attr("height");
    var sliderwidth = parseFloat(window.getComputedStyle(ss).width)
    - margin.left - margin.right;
    var slidex = d3.scaleLinear()
        .domain([0, maxval])
        .range([0, sliderwidth])
        .clamp(true);

    var ticks = d3.select(".strengthslider")
        .select(".ticks")
        .selectAll(".ticktext");
    ticks = ticks.data(slidex.ticks(maxval*10));

    ticks.exit().remove();

    ticks = ticks
        .enter().append("g")
        .attr("class", "ticktext")
        .attr("id", function (d, i) {
            return "tick" + i;
        })
        .merge(ticks)
        .attr("transform", function (d, i) {
            return "translate(" + slidex((i*1.0)/10.0) + ",0)";
        });

    ticks.append("text")
    .text(function (d, i) {
        if (i % 10 != 0){
            return "";
        }
        return i/10.0;
    })
    .attr("class", "tickz")
    .style("text-anchor", "end");

    var sshandle = strengthslidersvg.select(".handle")
        .call(d3.drag()
            .on("drag", function () {
                var linkstrength = Math.round(slidex.invert(d3.event.x)*10)/10;
                if (linkstrength != strengthslider) {
                    strengthslider = linkstrength;
                    d3.select("#strength").text(strengthslider);
                    draw();
                }
                sshandle.attr("cx", slidex(slidex.invert(d3.event.x)));
            }));
    sshandle.attr("cx", slidex(Math.min(currentpos, maxval)));
}

/**
* Add the slider that allows graph to be filtered based on link strength. When
* the graph is updated, this slider's scale is updated in :func:`updateStrengthSlider`
**/
function addStrengthSlider() {
    var ss = document.getElementById("strengthSlider");
    var strengthslidersvg = d3.select(".strengthslider");
    margin = {
        right: 50,
        left: 50,
        top: 100,
        bottom: 50
    };
    var height = +strengthslidersvg.attr("height");
    var sliderwidth = parseFloat(window.getComputedStyle(ss).width)
    - margin.left - margin.right;
    var slidex = d3.scaleLinear()
        .domain([0, 10])
        .range([0, sliderwidth])
        .clamp(true);

    var slider = strengthslidersvg.append("g")
    .attr("class", "slider")
    .attr("transform", "translate(" + margin.left + "," + height / 2 + ")");

    slider.append("line")
    .attr("class", "track")
    .attr("x1", slidex.range()[0])
    .attr("x2", slidex.range()[1])
    .select(function () {
        return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-inset")
    .select(function () {
        return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-overlay");

    var ticks = slider.insert("g", ".track-overlay")
        .attr("class", "ticks")
        .attr("transform", "translate(0,25)");

    var ticktext = ticks.selectAll(".ticktext")
        .data(slidex.ticks(10))
        .enter().append("g")
        .attr("class", "ticktext")
        .attr("id", function (d, i) {
            return "tick" + i;
        })
        .attr("transform", function (d, i) {
            return "translate(" + slidex(i) + ",0)";
        });

    var sshandle = slider.append("circle")
        .attr("class", "handle")
        .attr("r", 9)
        .call(d3.drag()
            .on("drag", function () {
                var linkstrength = Math.round(slidex.invert(d3.event.x));
                if (linkstrength != strengthslider) {
                    //strengthsliderpos = linkstrength;
                    strengthslider = linkstrength;
                    d3.select("#strength").text(strengthslider);
                    draw();
                }
                sshandle.attr("cx", slidex(slidex.invert(d3.event.x)));
            }));
}

/**
* Add the 'date slider' allowing the user to go back and forth through
* the graphs over time
**/
function addDateSlider() {
    slideradded = true;
    var s = document.getElementById("myslider");
    var slidesvg = d3.select(".myslider");
    
    //Get the slider's dimensions and set the linear scale based on its width
    var margin = {
        right: 50,
        left: 50,
        top: 100,
        bottom: 50
    };
    var height = +slidesvg.attr("height");
    var sliderwidth = parseFloat(window.getComputedStyle(s).width)
    - margin.left - margin.right;
    
    dateslidex = d3.scaleLinear()
        .domain([0, datalist.length-1])
        .range([0, sliderwidth])
        .clamp(true);

    dateslider = slidesvg.append("g")
    .attr("class", "slider")
    .attr("transform", "translate(" + margin.left + "," + height / 2 + ")");

    dateslider.append("line")
    .attr("class", "track")
    .attr("x1", dateslidex.range()[0])
    .attr("x2", dateslidex.range()[1])
    .select(function () {
        return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-inset")
    .select(function () {
        return this.parentNode.appendChild(this.cloneNode(true));
    })
    .attr("class", "track-overlay");

    var ticks = dateslider.insert("g", ".track-overlay")
        .attr("class", "ticks")
        .attr("transform", "translate(0,25)");

    var ticktext = ticks.selectAll(".ticktext")
        .data(dateslidex.ticks(6))
        .enter().append("g")
        .attr("class", "ticktext")
        .attr("id", function (d) {
            return "tick" + d;
        })
        .attr("transform", function (d, i) {
            return "translate(" + dateslidex((i*datalist.length)/5) + ",0)";
        });

    ticktext.append("text")
    .text(function (d, i) {
        if(i == 0){
            return df(parseTime(datalist[0].date));
        }
        else{
            index = Math.round((datalist.length) * (i/5.0));
            return (i>5) ? "" : df(parseTime(datalist[index-1].date));
        }
    })
    .attr("class", "tickz")
    .style("text-anchor", "middle");
    
    var len = datalist.length;
    $("#curdate").text(df(parseTime(datalist[len-2].date)) +
    " to " +
    df(d3.utcDay.offset(parseTime(datalist[len-2].date),14)));
    currentDate = datalist[len-2].date;
    
    //Add the wee circle that acts as the handle, and its behaviour
    sliderhandle = dateslider.append("circle")
    .attr("class", "handle")
    .attr("id","sliderhandle")
    .attr("r", 9)
    .call(d3.drag()
        .on("drag", function () {
            var sel = Math.round(dateslidex.invert(d3.event.x));
            var actual_date = Object.keys(data).length - sel - 1;
            sliderhandle.attr("cx", dateslidex(dateslidex.invert(d3.event.x)));                
            if (actual_date == indexstart) {
                return;
            }
            indexstart = actual_date;
            currentDate = datalist[sel].date;
            $("#curdate").text(
            df(d3.utcDay.offset(parseTime(datalist[sel].date),-14))+ 
            " to " + 
            df(parseTime(datalist[sel].date)));
            draw();
        }));
}
