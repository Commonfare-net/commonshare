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
var data_count = 0;
var taglistindex;
var indexstart = 0;
var strengthslider = 0;
var tag;
var filtertype;
var filternodetype;
var c_nodes = [];
var global_communities = {};
var ids_to_titles = {};
var parseTime = d3.timeParse("%Y/%m/%d");
var svg = d3.select("#bigvis");
var width = Number(svg.attr("width"));
var height = Number(svg.attr("height"));
var plotType = "stories";

function zoomFunction() {
    var new_xScale = d3.event.transform.rescaleX(xScale);
    var new_yScale = d3.event.transform.rescaleY(yScale);
    g.attr("transform", d3.event.transform);
}
var zoom = d3.zoom().on("zoom", zoomFunction);
svg.call(zoom);
var g = svg.append("g").attr("transform", "translate(250,250) scale (.35,.35)");
var extralines = g.append("g").attr("z-index", -3);
var link = g.append("g")
    .attr("stroke", "#000")
    .attr("stroke-width", 1.5)
    .selectAll(".link");
var node = g.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .selectAll(".node");
var convexHull = g.append("path").attr("class", "hull");
svg.call(zoom.transform, d3.zoomIdentity.translate(250, 250).scale(0.35));

var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

//Clear any markers on the graph showing dynamic communities
function clearDyn() {
    d3.select(".hull").style("opacity", 0);
    d3.selectAll(".marker").remove();
    c_nodes = [];
    draw();
}

/**
* This loops through the data files folder until it can't find any more.
* It then queues them all up and after that begins rendering them one by one.
* @param {d3.queue} queue - structure from D3 library containing queued JSON files
*/
function loadDataFiles(queue) {
    var data_url = "../data/output/graphdata/" + data_count + ".json";
    $.ajax({
        url: data_url,
        type: "HEAD",
        error: function () {
            queue.awaitAll(function (error, results) {
                //That's all the files, start drawing the graphs!
                if (error) {
                    throw error;
                }
                for (i = 0; i < results.length; i+=1) {
                    data[i] = results[i];
                    if (i > 0){
                        datalist[i - 1] = results[i];
                    }
                    drawn[i] = false;
                }
                datalist.reverse();
                drawAreaChart();
                draw();
                var len = Object.keys(data).length;
                if (slideradded == false) {
                    addDateSlider();
                    addStrengthSlider();
                    sliderhandle.attr("cx", dateslidex(len-1));
                } 
                else {
                    sliderhandle.attr("cx", dateslidex(len-1));
                    d3.selectAll(".ticktext")
                    .style("fill", "black")
                    .style("font-weight", "normal");
                }
                indexstart = 1;
                draw();
            });
        },
        success: function () {
            //Found a file, add it to the queue and keep looking
            queue.defer(d3.json, data_url);
            data_count++;
            loadDataFiles(queue);
        }
    });
}
loadDataFiles(q);

/**
* One 'tick' of the simulation - moves nodes, links and the 'extra' links 
**/
function ticked() {
    link
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});
    
    extralines.selectAll(".extralines")
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});
    
    node
    .attr("cx", function (d) {return d.x;})
    .attr("cy", function (d) {return d.y;});
}

//Functions that reposition nodes and their links when a node is dragged
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

/**
* Define what happens when the user mouses over a node on the graph...
* @param {json} d - JSON data of the hovered node
*/
function mouseOverNode(d){
    d3.select("#n"+indexstart+"_"+d.id)
    .attr("fill", d3.color("orange"));
    sourcelinks = link.filter(function (e) {
        return e.source.id == d.id || e.target.id == d.id;
    });
    //Here we save what the link width and colour were so they can be restored
    sourcelinks.each(function (d) {
        d3.select(this)
        .attr("oldstrokeval", d3.select(this).style("stroke-width"))
        .attr("oldcolourval", d3.select(this).style("stroke"))
        .style("stroke", "green");
    });    
    //Tooltip functions
    div.transition().duration(200).style("opacity", 0.9);
    nodename = ("name" in d ? d.name : d.title);
        div.html(nodename + "</br>" + d.kcore)
        .style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px")
        .style("background", function () {
            return (d.type == "commoner") ? "lightsteelblue" : "pink";
        });
}

/**
* ...and this is what happens when the user moves the mouse out again
**/
function mouseOutNode(d){
    d3.select("#n"+indexstart+"_"+d.id)
    .attr("fill", function (d) {
        return (colluders.indexOf(d.id) > -1) ? d3.color("darkred") : 
        (c_nodes.indexOf(d.id) > -1) ? d3.color("orange") :    
        d3.select(this).attr("stroke");
    });
    //Set the neighbour links' width and colour back to what they were
    sourcelinks.each(function (d) {
        d3.select(this)
        .style("stroke", d3.select(this).attr("oldcolourval"));
    });
    sourcelinks.each(function (d) {
        d3.select(this)
        .style("stroke-width", d3.select(this).attr("oldstrokeval"));
    });
    div.transition().duration(500).style("opacity", 0);    
}

/**
* Update the metrics that show below the graph
*/
function updateMetrics(){
    $("#nodenums").text(graph.node_num);
    $("#edgenums").text(graph.edge_num);
    $("#commoners").text(graph.commoners);
    $("#stories").text(graph.stories);
    $("#listings").text(graph.listings);
    $("#tags").text(graph.tags);
    $("#convos").text(graph.convo);
    $("#transactions").text(graph.trans);
    $("#written").text(graph.create);
    $("#comments").text(graph.comment);   
}

/**
* Currently quite a monolithic method containing all necessary functions
* for drawing the force-directed graph and adding its interactivity. 
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
    updateMetrics();
    selected_node = "";
    var maxval = 0;
    node = node.data(graph.nodes, function (d) {
            return d.id + indexstart;
        });
    link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });
    populateListBoxes();
    //Flatten 2D colluders array for search simplicity
    colluders = (
    "colluders" in graph ? graph.colluders.flat() : []);
    
    node.exit().transition()
    .attr("r", 0)
    .remove();
    
    //Add all the nodes, their styling and their interactivity
    //Also logs the maximum strength of interaction so that the strength
    //slider can be updated
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
            return (c_nodes.indexOf(d.id) > -1) ? 20 : (d.kcore*2)+5;
        })
        .attr("stroke", function (d) {
            if (d.type == "commoner"){
                return d3.color("steelblue");
            }
            if (d.type == "listing"){
                return d3.color("purple");
            }
            if (d.type == "tag"){
                return d3.color("green");
            }
            return d3.color("red");
        })
        .attr("stroke-width", function (d) {
            return (colluders.indexOf(d.id) > -1) ? 4 :
                   (c_nodes.indexOf(d.id) > -1) ? 7 : 0;
        })
        .attr("fill", function (d) {
            return (colluders.indexOf(d.id) > -1) ? d3.color("darkred") : 
                (c_nodes.indexOf(d.id) > -1) ? d3.color("orange") : 
                d3.select(this).attr("stroke");
        })
        .style("opacity", function (d) {
            if (d.maxweight < strengthslider){
                return 0;
            }
            if (filtertype == "tag") {
                return (tag == "all" ||
                   (d.type == "tag" && d.name == tag) ||
                   d.tags.includes(tag)) ? 1 : 0.15;
            } 
            if (filtertype == "network") {
                return (tag == "all" || d.nodemeta.includes(tag)) ? 1 : 0.15;
            } 
            return 1;
        })
        .on("click", function (od) {
            window.open("../html/personal_viz.html?userid=" + od.id, "_blank");
        })
        .on("mouseover",mouseOverNode,this)
        .on("mouseout", mouseOutNode,this);
        
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
    
    drawArrowHeads();
    
    link.exit()
    .remove();
    
    //Add links and all their styling (colour, thickness, arrowheads etc)
    link = link.enter().append("line")
        .attr("class", "line")
        .merge(link)
        .attr("stroke-width", function (d) {
            if ("tag_story" in d || "tag_commoner" in d || "tag_listing" in d){
                return 0.25;
            }
            if ("edgemeta" in d && d.edgemeta.includes("social") &&
                d.edgemeta.includes("transaction")){
                return 3;
            }
            return ("edgeweight" in d) ? Math.max(1,d.edgeweight) : 2;
        })
        .attr("edgemeta", function (d) {
            return d.id + JSON.stringify(d.edgemeta);
        })
        .style("stroke", function (d) {
            if (c_nodes.indexOf(d.source.id) > -1 &&
                c_nodes.indexOf(d.target.id) > -1){
                return "orange";
            }
            if("edgemeta" in d){
                if (d.edgemeta.includes("story")){
                    return "red";
                }
                if (d.edgemeta.includes("social") &&
                    d.edgemeta.includes("transaction")){
                    return "#FFC31E";
                }
                if (d.edgemeta.includes("social")){
                    return "orange";
                }
                if (d.edgemeta.includes("listing")){
                    return "purple";
                }
                if (d.edgemeta.includes("transaction")){
                    return "darkblue";
                }
            }
            return "black";
        })
        .style("stroke-dasharray", function (d) {
            if ("edgemeta" in d && d.edgemeta.includes("social") &&
                d.edgemeta.includes("transaction")){
                return "20,10";
            }
            return 0;
        })
        .attr("marker-end", function (d) {
            if (nodetypes[d.source.id] == "commoner" &&
                 nodetypes[d.target.id] != "tag") {
                return "url(#mend" + d.source.id + "-" + d.target.id + ")";
            }
            return null;
        })
        .attr("marker-start", function (d) {
            if (nodetypes[d.target.id] == "commoner" &&
                 nodetypes[d.source.id] != "tag") {
                return "url(#mstart" + d.source.id + "-" + d.target.id + ")";
            }
            return null;
        })
        .style("opacity", function (d) {
            if ("maxweight" in d && d.maxweight < strengthslider ||
               (strengthslider > 0 && d.maxweight == undefined)){
                return 0;
            }
            if (filtertype == "tag") {
                if (tag == "all" ||
                (d.source.type == "tag" && d.source.name == tag) ||
                (d.target.type == "tag" && d.target.name == tag)){
                    return 1;
                }
                return 0.15;
            } 
            else if (filtertype == "network") {
                if (tag == "all" ||
                (d.edgemeta != null && d.edgemeta.includes(tag))){
                    return 1;
                }
                return 0.15;
            } 
            return 1;
        });

    sim.nodes(graph.nodes);
    clusters = {};
    node.each(function (d) {
        var radius = d.kcore;
        var clusterID = d.cluster;
        if (!clusters[clusterID] || (radius > clusters[clusterID].kcore)) {
            clusters[clusterID] = d;
        }
    });
    
    //Manually tick through the simulation and stop when it reaches a certain 'alpha' value
    //so it doesn't continue to waste processing power
    sim.force("link").links(graph.links);
    if (drawn[indexstart] == false) {
        drawn[indexstart] = true;
        sim.alpha(1);
        n = Math.ceil(Math.log(sim.alphaMin())/Math.log(1-sim.alphaDecay()));
        for (i = 0; i < n; i+=1) {
            sim.tick();
        }
        if ((data_count - 1) > (indexstart + 1)) {
            indexstart++;
            draw();
        } else {
            data_count = 1;
        }
    }
    ticked();

    //Once the simulation has stopped, can add the necessary extra lines needed
    //for the 'dashed' arrow colour effect
    addDashedArrowLines();
    
    $("#loadingDiv").css("display", "none");
    chartsvg.call(areazoom.transform,
        d3.zoomIdentity.translate(0, 0).scale(0.33));
    drawNewChart(plotType);
}