/**
* This file contains all the code for responding to the graph 'widgets'
**/

var df = d3.timeFormat("%d/%m/%y %H:%M");
var datediff = 0;
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
Toggle whether to show/hide tag nodes and edges

@param checkboxelem - The check box that triggered this function
**/
function toggletags(checkboxelem) {
    var opacity = (checkboxelem.checked) ? 0 : 1;
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
Toggle whether to show the cumulative graph or the slider

@param checkboxelem - The check box that triggered this function
**/
function toggledate(checkboxelem) {
    clearDyn();
    //Show the cumulative graph
    if (checkboxelem.checked) {
        len = Object.keys(data).length;
        //Set the date slider text to show first date to last date
        $("#curdate").text(df(parseTime(data[len-1].date)) +
        " to " + df(parseTime(data[1].date)));
        //and disable it from interaction
        $("#myslider").css("opacity", 0.4);
        $("#myslider").css("pointer-events", "none");
        currentDate = data[1].date;
        sliderhandle.attr("cx", dateslidex(Object.keys(data).length - 1));
        indexstart = 0;
        draw();
    //Show the dynamic graphs
    } 
    else {
        $("#curdate").text(df(parseTime(data[1].date).getTime()-datediff) +
        " to " + df(parseTime(data[1].date)));
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
*/
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
    //When user clicks on a dynamic community, either add the 'convex hull'
    //around community members (for cumulative graph) or add the 'community'
    //class to relevant nodes so that they are highlighted, and redraw
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
        //Add the triangle markers on date slider to show points 
        //where the community was active
        for (x = 0; x < global_communities[name][1].length; x+=1) {
            date = global_communities[name][1][x];
            xpos = dateslidex(Object.keys(data).length - date - 1);
            ypos = -10;
            dateslider.append("path")
            .attr("d", "M " + xpos + " " + ypos + " l -4 -8 l 8 0 z")
            .attr("class", "marker");
        }
        //Draw the convex hull
        if (indexstart == 0) {
            var hull = d3.polygonHull(c_nodes.map(function (d) {
                return [d3.select("#n" + indexstart + "_" + d).attr("cx"),
                d3.select("#n" + indexstart + "_" + d).attr("cy")];
            }));
            convexHull.datum(hull).attr("d", function (d) {
                return "M" + d.join("L") + "Z";
            });
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

/**
Function to remove convex hull, triangle markers,
and highlighted nodes that appear when a dynamic
community is selected
**/
function clearDyn() {
    d3.select(".hull").attr("d", 0);
    d3.selectAll(".marker").remove();
    c_nodes = [];
    draw();
}

/**
Function for filtering based on network type
(e.g., stories written, transactions, comments)
**/
function nwfilter(nwname) {
    filtertype = "network";
    tag = nwname;
    draw();
}

/**
Updates the strength slider with new values

At each time step, the maximum link strength will be
different so the maximum value and increments of the 
slider have to be updated on every redraw.
@param {int} currentpos - position on slider before redrawing
@param {int} maxval - maximum link strength of this time step 
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
Adds the strength slider initially

The strength slider allows a user to filter the graph based on link strength.
This sets the slider's initial position and values. It is then updated on
each subsequent redraw through the 'updateStrengthSlider' function above
**/
function addStrengthSlider() {
    var ss = document.getElementById("strengthSlider");
    var strengthslidersvg = d3.select(".strengthslider");
    
    //Get the slider's dimensions and set the linear scale based on its width
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

    //Reset slider handle and its dragging listener
    var sshandle = slider.append("circle")
        .attr("class", "handle")
        .attr("r", 9)
        .call(d3.drag()
            .on("drag", function () {
                var linkstrength = Math.round(slidex.invert(d3.event.x));
                if (linkstrength != strengthslider) {
                    strengthslider = linkstrength;
                    d3.select("#strength").text(strengthslider);
                    draw();
                }
                sshandle.attr("cx", slidex(slidex.invert(d3.event.x)));
            }));
}

/**
This adds the 'date slider' allowing the user to go back and 
forth through the graphs over time
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
    $("#curdate").text(df(parseTime(datalist[len-1].date).getTime()-datediff) +
        " to " + df(parseTime(datalist[len-1].date)));
    currentDate = datalist[len-1].date;
    
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
            $("#curdate").text(df(parseTime(datalist[sel].date).getTime()-datediff) +
            " to " + df(parseTime(datalist[sel].date)));
            draw();
        }));
}
