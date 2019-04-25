var data = {};
var datalist = [];
var drawn = {};
var xScale = d3.scaleLinear()
    .domain([0, 500]).range([0, 500]);
var yScale = d3.scaleLinear()
    .domain([0, 600]).range([0, 600]);
var dateslider;
var dateslidex;
var slideradded = false;
var q = d3.queue();
var datafilecounter = 0;
var indexstart = 0;
var strengthslider = 0;
var c_nodes = [];
var global_communities = {};
var ids_to_titles = {};
var parseTime = d3.timeParse("%Y/%m/%d %H:%M");
var active_simulation;
function zoomFunction() {
    var new_xScale = d3.event.transform.rescaleX(xScale);
    var new_yScale = d3.event.transform.rescaleY(yScale);
    g.attr("transform", d3.event.transform);

    }
var zoom = d3.zoom().on("zoom", zoomFunction);
var svg = d3.select("#bigvis");
var width = +svg.attr("width");
var height = +svg.attr("height");
svg.call(zoom);
var g = svg.append("g").attr("transform", "translate(250,250) scale (.35,.35)");
link = g.append("g")
       .attr("stroke", "#000")
       .attr("stroke-width", 1.5).selectAll(".link");
node = g.append("g")
       .attr("stroke", "#fff")
       .attr("stroke-width", 1.5).selectAll(".node");
svg.call(zoom.transform, d3.zoomIdentity.translate(250, 250).scale(0.35));
/*
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
            return d.id;
        }))
     .force("collision", d3.forceCollide().radius(function(d) {
    return 20;
  }))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("x", d3.forceX().x(width / 2).strength(0.1))
    .force("y", d3.forceY().y(height / 2).strength(0.1))
    .stop();
var community_sim = d3.forceSimulation()
    .force("charge", d3.forceManyBody().strength(-10))
    .force("link", d3.forceLink().id(function (d) {
            return d.id;
        }).strength(0))
    .force("center", d3.forceCenter(500 / 2, 600 / 2))
    .force("cluster", forceCluster)
    .force("collide", d3.forceCollide(22).strength(0.9))
    .stop();*/
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);
Array.prototype.unique = function () {
    var a = this.concat();
    for (i = 0; i < a.length; i+=1) {
        for (j = i + 1; j < a.length; j+=1) {
            if (a[i] === a[j]){
                a.splice(j--, 1);
            }
        }
    }
    return a;
};
/*
function togglegroups(checkboxelem) {
    if (checkboxelem.checked){
        active_simulation = community_sim;
    }
    else{
        active_simulation = simulation;
    }
    active_simulation.nodes(graph.nodes);
    active_simulation.force("link").links(graph.links);
    active_simulation.alpha(1);
    n = Math.ceil(Math.log(active_simulation.alphaMin()) /
    Math.log(1 - active_simulation.alphaDecay()));
    for (i = 0; i < n; i+=1) {
        active_simulation.tick();
    }
    node
    .transition()
    .duration(2000)
    .attr("cx", function (d) {return d.x;})
    .attr("cy", function (d) {return d.y;});
    link
    .transition()
    .duration(2000)
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});
}
*/
function loadDataFiles(queue) {
    var data_url = "../data/output/graphdata/"+datafilecounter+".json";
    $.ajax({
        url: data_url,
        type: "HEAD",
        error: function () {
            queue.awaitAll(function (error, results) {
                if (error){
                    throw error;
                }
                for (d = 0; d < results.length; d+=1) {
                    data[d] = results[d];
                    if (d > 0){
                        datalist[d - 1] = results[d];
                    }
                    drawn[d] = false;
                }
                if(results.length > 1){
                    datediff = parseTime(datalist[0].date).getTime() - parseTime(datalist[1].date).getTime();
                }
                datalist.reverse();
                draw();
                var len = Object.keys(data).length -1;
                if (slideradded == false) {
                    addDateSlider();
                    addStrengthSlider();
                    sliderhandle.attr("cx", dateslidex(len));
                } else {
                    sliderhandle.attr("cx", dateslidex(len));
                    d3.selectAll(".ticktext")
                    .style("fill", "black")
                    .style("font-weight", "normal");
                }
                indexstart = 1;
                draw();
            });
        },
        success: function () {
            queue.defer(d3.json, data_url);
            datafilecounter++;
            loadDataFiles(queue);
        }
    });
}
loadDataFiles(q);
/*
function forceCluster(alpha) {
    node.each(function (d) {
        cluster = clusters[d.cluster];
        if (cluster === d){
            return;
        }
        var x = d.x - cluster.x;
        var y = d.y - cluster.y;
        var l = Math.sqrt(x * x + y * y);
        var r = d.kcore + cluster.kcore;
        if (l != r) {
            l = (l - r) / l * alpha;
            d.x -= x *= l;
            d.y -= y *= l;
            cluster.x += x;
            cluster.y += y;
        }
    });
}
*/
function draw() {
    $(".mybox").prop("checked", false);
    nodetypes = {};
    //https://stackoverflow.com/questions/11347779
    $.fn.ignore = function (sel) {
        return this.clone().find(sel || ">*").remove().end();
    };
    graph = data[indexstart];
    communities = graph.communities;
    selected_node = "";
    var maxval = 0;
    node = node.data(graph.nodes, function (d) {
            return d.id + indexstart;
        });
    link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });
    dc = (
    "dynamic_comms" in graph ? graph.dynamic_comms : {});
    var colluders = (
    "colluders" in graph ? graph.colluders : []);
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
    var c = $("#comm-group");
    var members = $("#comm-members");
    c.empty();
    Object.keys(global_communities).forEach(function(comm){
        c.append("<a href='#' class='list-group-item community'>"+comm+"</a>");
    });
    $(".community").click(function (e) {
        e.preventDefault();
        members.empty();
        d3.selectAll(".marker").remove();
        name = $(this).text();
        c_nodes = global_communities[name][0];
        for (i = 0; i < c_nodes.length; i+=1) {
            members.append("<a href='#' class='list-group-item community'>" +
            ids_to_titles[c_nodes[i]] + "</a>");
        }
        for (x = 0; x < global_communities[name][1].length; x+=1) {
            date = global_communities[name][1][x];
            xpos = dateslidex(Object.keys(data).length - date - 1);
            ypos = -10;
            dateslider.append("path")
            .attr("d","M " + xpos + " " + ypos + " l -4 -8 l 8 0 z")
            .attr("class", "marker");
        }
        if (indexstart > 0) {
            draw();
        }
    });
    node.exit().transition()
        .attr("r", 0)
        .remove();
    node = node.enter().append("circle")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .merge(node)
        .each(function (d) {
            nodetypes[d.id] = d.type;
            if (Number.isNaN(Number(d.maxweight))){
                d.maxweight = 0;
            }
            maxval = Math.max(maxval, d.maxweight);
        })
        .attr("id", function (d) {
            return "n" + indexstart + "_" + d.id;
        })
        .attr("meta", function (d) {
            return "n" + JSON.stringify(d.type);
        })
        .attr("r", function (d) {
            if (c_nodes.indexOf(d.id) > -1){
                return 20;
            }
            return (d.kcore * 2) + 5;
        })
        .attr("stroke", d3.color("red"))
        .attr("stroke-width", function (d) {
            for (i = 0; i < colluders.length; i+=1) {
                if (colluders[i].includes(d.id)){
                    return 4;
                }
            }
            if (c_nodes.indexOf(d.id) > -1){
                return 7;
            }
            return 0;
        })
        .attr("fill", function (d) {
            for (i = 0; i < colluders.length; i+=1) {
                if (colluders[i].includes(d.id)){
                    return d3.color("darkred");
                }
            }
            if (c_nodes.indexOf(d.id) > -1){
                return d3.color("orange");
            }
            return d3.color("purple");
        }) //Coloured based on their type
        .style("opacity", function (d) {
            if (d.maxweight < strengthslider){
                return 0;
            }
            return 1;
        })
        .on("click", function (od) {
            window.open("../html/personal_basic.html?userid="+od.id,"_blank");
        })
        .on("mouseover", function (d) {
            sel = d.id;
            d3.select(this).attr("fill", d3.color("orange"));
            sourcelinks = link.filter(function (d) {
                return d.source.id == sel || d.target.id == sel;
            });
            message = "";
            sourcelinks.each(function (d) {
                if(sel == d.source.id){
                    message += (d.target.id + " weight: " +
                    d.edgeweight[d.source.id] + "<br/>");
                }
                else{
                    message += (d.source.id + " weight: " +
                    d.edgeweight[d.target.id] + "<br/>");
                }
                var oldwidth = d3.select(this).style("stroke-width");
                var oldcolour = d3.select(this).style("stroke");
                d3.select(this).attr("oldstrokeval",oldwidth);
                d3.select(this).attr("oldcolourval",oldcolour);
                d3.select(this).style("stroke", "green");
            });
            div.transition()
            .duration(200)
            .style("opacity", 0.9);
            if(d.label == null){
                d.label = d.id;
            }
            div.html("label: "+ d.label +". commonshare: " + d.kcore +
            "<br/>" + message)
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px")
            .style("background", "lightsteelblue");
        })
        .on("mouseout", function (d) {
            d3.select(this).attr("fill", function (d) {
                for (i = 0; i < colluders.length; i+=1) {
                    if (colluders[i].includes(d.id)){
                        return d3.color("darkred");
                    }
                }
                if (c_nodes.indexOf(d.id) > -1){
                    return d3.color("orange");
                }
                return d3.color("purple");
            });
            sourcelinks.each(function (d) {
                var oldcolour = d3.select(this).attr("oldcolourval");
                d3.select(this).style("stroke", oldcolour);
            });
            sourcelinks.each(function (d) {
                var oldwidth = d3.select(this).attr("oldstrokeval");
                d3.select(this).style("stroke-width", oldwidth);
            });
            div.transition()
            .duration(500)
            .style("opacity", 0);
        });

    updateStrengthSlider(strengthslider, maxval);
    if (indexstart == 0){
        Object.keys(global_communities).forEach(function(comm){
            nodeids = global_communities[comm][0];
            for (i = 0; i < nodeids.length; i+=1) {
                nodedata = d3.select("#n0_" + nodeids[i]).datum();
                if ("name" in nodedata){
                    ids_to_titles[nodeids[i]] = nodedata.name;
                }
                else{
                    ids_to_titles[nodeids[i]] = nodedata.title;
                }
            }
        });
    }
    function hs(d){
        return (
        d.maxweight == undefined ? 2 : d.maxweight < 0 ? 0 : Math.min(8, d.maxweight+1));
    }

    //Arrowheads that show the direction of the interaction
    svg.selectAll("defs").remove();
    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    .attr("id", function (d) {
        return "mend" + d.source.id + "-" + d.target.id;
    })
    .attr("viewBox",function(d){
        return "0 " + (-hs(d)) + " " + (hs(d)*2) + " " + (hs(d) * 2);
    })
    .attr("refX", function (d) {
        if (d.target.id == null ||
        d3.select("#n" + indexstart + "_" + d.target.id).empty()){
            return hs(d) * 2;
        }
        radius = d3.select("#n" + indexstart + "_" + d.target.id).attr("r");
        return 0;
    })
    .attr("markerUnits", "userSpaceOnUse")
    .attr("markerWidth",function(d){return hs(d)*2;})
    .attr("markerHeight",function(d){return hs(d)*2;})
    .attr("orient", "auto")
    .append("path")
    .attr("d",function(d){
        return "M0," + (-hs(d)) + "L" + (hs(d)) + ",0L0," + hs(d);
    })
    .style("fill","black");
    //Now the other direction
    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    .attr("id", function (d) {
        return "mstart" + d.source.id + "-" + d.target.id;
    })
    .attr("viewBox",function(d){
        return -(hs(d)*2) + " " + -(hs(d)) + " " + (hs(d)*2) + " " + (hs(d)*2);
    })
    .attr("refX", function (d) {
        if (d.source.id == null ||
        d3.select("#n" + indexstart + "_" + d.source.id).empty()){
            return 10;
        }
        radius = d3.select("#n" + indexstart + "_" + d.source.id).attr("r");
        return 0;
    })
    .attr("markerUnits", "userSpaceOnUse")
    .attr("markerWidth",function(d){return hs(d)*2;})
    .attr("markerHeight",function(d){return hs(d)*2;})
    .attr("orient", "auto")
    .append("path")
    .attr("d",function(d){
        return "M0," + (-hs(d)) + "L-" + (hs(d)) + ",0L0," + hs(d);
    })
    .style("fill","black");

    link.exit()
    .remove();
    link = link.enter().append("line")
        .attr("class", "line")
        .merge(link)
        .attr("stroke-width", function (d) {
            if ("edgeweight" in d){
                return Math.min(8, d.maxweight);
            }
            return 2;
        })
        .attr("edgemeta", function (d) {
            return d.id + JSON.stringify(d.edgemeta);
        })
        .style("stroke", function (d) {
            vals = [];
            Object.keys(d.edgeweight).forEach(function(key){
                vals.push(d.edgeweight[key]);
            });
            var saturation = Math.max(20,80-d.maxweight);
            return "hsl(0,100%," + saturation +"%)";
        })
        .attr("marker-end", function (d) {
            if(d.edgeweight[d.source.id] != undefined){

                d3.select("#mend" + d.source.id + "-" + d.target.id + " path")
                .style("fill",d3.select(this).style("stroke"));
                return "url(#mend" + d.source.id + "-" + d.target.id + ")";
            }
            return null;
        })
        .attr("marker-start", function (d) {
           if(d.edgeweight[d.target.id] != undefined){
                d3.select("#mstart" + d.source.id + "-" + d.target.id + " path")
                .style("fill",d3.select(this).style("stroke"));
                return "url(#mstart" + d.source.id + "-" + d.target.id + ")";
           }
            return null;
        })
        .style("opacity", function (d) {
            if ("maxweight" in d && d.maxweight < strengthslider ||
            (strengthslider > 0 && d.maxweight == undefined)){
                return 0;
            }
            return 1;
        });
    function getTheta(d1,d2){
      var dx = d2.x - d1.x;
      var dy = d2.y - d1.y;
      return Math.atan2(dy, dx);
    }
    function ticked() {
        link
        .attr("x1", function (d) {return d.source.x +
        ((5+(d.source.kcore)*2)+parseInt(d3.select(this).attr("stroke-width")))*
        Math.cos(getTheta(d.source,d.target));})
        .attr("y1", function (d) {return d.source.y +
        ((5+(d.source.kcore)*2)+parseInt(d3.select(this).attr("stroke-width")))*
        Math.sin(getTheta(d.source,d.target));})
        .attr("x2", function (d) {return d.target.x +
        ((5+(d.target.kcore)*2)+parseInt(d3.select(this).attr("stroke-width")))*
        Math.cos(getTheta(d.target,d.source));})
        .attr("y2", function (d) {return d.target.y +
        ((5+(d.target.kcore)*2)+parseInt(d3.select(this).attr("stroke-width")))*
        Math.sin(getTheta(d.target,d.source));});
        node
        .attr("cx", function (d) {return d.x;})
        .attr("cy", function (d) {return d.y;});
    }
    //Dragging functions
    function dragstarted(d) {
        d3.event.sourceEvent.stopPropagation();
        d.fx = d.x;
        d.fy = d.y;
    }
    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
        d.x = d3.event.x;
        d.y = d3.event.y;
        ticked();
    }
    function dragended(d) {
        d.fx = null;
        d.fy = null;
    }
    if(active_simulation == undefined){
        active_simulation = simulation;
    }
    // Update and restart the simulation.
    active_simulation.nodes(graph.nodes);
    clusters = {};
    node.each(function (d) {
        var radius = d.kcore;
        var clusterID = d.cluster;
        if (!clusters[clusterID] || (radius > clusters[clusterID].kcore)) {
            clusters[clusterID] = d;
        }
    });
    active_simulation.force("link").links(graph.links);
    if (drawn[indexstart] == false) {
        drawn[indexstart] = true;
        active_simulation.alpha(1);
        n = Math.ceil(Math.log(active_simulation.alphaMin()) /
        Math.log(1 - active_simulation.alphaDecay()));
        for (i = 0; i < n; i+=1) {
            active_simulation.tick();
        }
        if ((datafilecounter - 1) > (indexstart + 1)) {
            indexstart++;
            draw();
        } else {
            datafilecounter = 1;
        }
    }
    ticked();
    $("#loadingDiv").css("display", "none");
}

$("#cleardyn").click(function (e) {
    e.preventDefault();
    clearDyn();
});