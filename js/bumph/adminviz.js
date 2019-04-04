//graphstuff innit

function getTranslation(transform) {

    var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttributeNS(null, "transform", transform);
    var matrix = g.transform.baseVal.consolidate().matrix;
    return [matrix.e, matrix.f];
}
var zoom = d3.zoom().on("zoom", zoomFunction);
svg.call(zoom);
svg.call(zoom.transform, d3.zoomIdentity.translate(250, 250).scale(0.35));

function zoomFunction() {
    var new_xScale = d3.event.transform.rescaleX(xScale);
    var new_yScale = d3.event.transform.rescaleY(yScale);
    g.attr("transform", d3.event.transform)
};

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {return d.id;}))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("x", d3.forceX().x(width / 2).strength(0.1))
    .force("y", d3.forceY().y(height / 2).strength(0.1))
    .stop();

var community_sim = d3.forceSimulation()
    .force("charge", d3.forceManyBody().strength(-10))
    .force("link", d3.forceLink().id(function (d) {
                                        return d.id;})
                                     .strength(0))
    .force("center", d3.forceCenter(500 / 2, 600 / 2))
    .force("cluster", forceCluster)
    .force("collide", d3.forceCollide(22).strength(0.9))
    .stop();
var active_simulation = simulation;


function queueFinished(results){
    datalist = [];
    data = {};
    for (var i = 0; i < results.length; i++) {
        data[i] = results[i];
        if(i>0)
            datalist[i-1] = results[i];
        drawn[i] = false;
    }
    datalist.reverse();
    // Scale the range of the data
    x.domain(d3.extent(datalist,
            function(d) {
                return parseTime(d.date);
            }));
    y.domain([0, d3.max(datalist,
            function(d) {
                return isNaN(d.stories) ? 0 : +d.stories;
            })]);
    plotType = "stories";
    // Add the valueline path.
      var anotherFormat = d3.timeFormat("%b'%y");

    xAxis = d3.axisBottom(x)
    .tickFormat(anotherFormat)
    .ticks(d3.timeMonth.every(1));

    // Add the X Axis
    gX = chartg.append("g")
      .attr("id", "simplelineaxis")
      .attr("transform","translate(0,"+($("#lgraph").height()-20)+")")
      .call(xAxis);

    // Add the Y Axis
    gY = chartg.append("g")
      .attr("class","yline")
      .attr("transform", "translate(40,0)")
      .call(d3.axisLeft(y));
    chartsvg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0)
      .attr("x",0 - ($("#lgraph").height() / 2))
      .attr("dy", "1em")
      .attr("id","ylabel")
      .style("text-anchor", "middle")
      .style("font-family", "Calibri")
      .style("font-weight", "bold")
      .text("");
    draw();
    if (slideradded == false) {
        addDateSlider();
        addStrengthSlider();
        sliderhandle.attr("cx", dateslidex(Object.keys(data).length-1));
    } else {
        updateDateSlider(granularity);
        sliderhandle.attr("cx", dateslidex(Object.keys(data).length-1));
        d3.selectAll(".ticktext")
        .style("fill", "black")
        .style("font-weight", "normal");
    }
    indexstart = 1;
    draw();
}

function loadDataFiles(queue,granularity) {
    $("#loadingDiv").css("display","inline");
    var url = "../data/output/graphdata/"
    + granularity + "/" + datafilecounter + ".json";
    $.ajax({
        url: url,
        type: "HEAD",
        error: function () {
            queue.awaitAll(function (error, results) {
                if (error)
                    throw error;
                queueFinished(results);
            });
        },
        success: function () {
            queue.defer(d3.json, url);
            datafilecounter++;
            loadDataFiles(queue,granularity);
        }
    });
}

loadDataFiles(q,"biweekly");

function forceCluster(alpha) {
    node.each(function (d) {
        cluster = clusters[d.cluster];

        if (cluster === d)
            return;

        let x = d.x - cluster.x,
        y = d.y - cluster.y,
        l = Math.sqrt(x * x + y * y),
        r = d.kcore + cluster.kcore;

        if (l != r) {
            l = (l - r) / l * alpha;
            d.x -= x *= l;
            d.y -= y *= l;
            cluster.x += x;
            cluster.y += y;
        }
    });
}


function draw() {

    $(".mybox").prop("checked", false);
    nodetypes = {};

    $.fn.ignore = function (sel) {
        return this.clone().find(sel || ">*").remove().end();
    };
    graph = data[indexstart];
    communities = graph.communities;
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
    selected_node = "";
    var maxval = 0;
    node = node.data(graph.nodes, function (d) {
            return d.id + indexstart;
        });

    link = link.data(graph.links, function (d) {
            return d.source.id + "-" + d.target.id;
        });

    tagcounts = graph.tagcount;
    dc = graph.dynamic_comms;
    var colluders = "colluders" in graph ? graph.colluders : [];
    for (var comm in dc) {
        global_community = [];
        dates = [];
        for (var i = 0; i < dc[comm].length; i += 2) {
            dates.push(dc[comm][i]);
        }
        for (var i = 1; i < dc[comm].length; i += 2) {
            global_community = global_community.concat(dc[comm][i]);
        }
        global_communities[comm] = [global_community.unique(), dates];

    }
    var commContainer = $("#comm-group");
    var commMembers = $("#comm-members");
    commContainer.empty();

    for (var comm in global_communities) {
        commContainer.append(
            "<a href='#' class='list-group-item community'>"
            + comm + "</a>")
    }
    $(".community").click(function (e) {
        e.preventDefault();
        commMembers.empty();
        d3.selectAll(".marker").remove();
        name = $(this).text();
        c_nodes = global_communities[name][0];
        for (var i = 0; i < c_nodes.length; i++) {
            commMembers.append(
            "<a href='#' class='list-group-item community'>"
            + ids_to_titles[c_nodes[i]] + "</a>");
        }
        for (var x = 0; x < global_communities[name][1].length; x++) {
            var date = global_communities[name][1][x];
            dateslider.append("path")
            .attr("d", function (d) {
                var x = dateslidex(Object.keys(data).length-date-1),
                y = -10;
                return "M " + x + " " + y + " l -4 -8 l 8 0 z";
            })
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
        } else {
            draw();
        }
    });

    var listContainer = $("#list-group");
    if (taglistindex != indexstart) {
        taglistindex = indexstart;
        listContainer.empty();
        for (var i = 0; i < tagcounts.length; i++) {
            var tagname = tagcounts[i][0];
            var tagnum = tagcounts[i][1];
            listContainer.append(
                "<a href='#' class='list-group-item taga'>" + tagname
                + "<span class='badge'>" + tagnum + "</span></a>"
            );
        }
        $(".taga").click(function (e) {
            e.preventDefault();
            filtertype = "tag";
            tag = $(this).ignore("span").text();
            draw();
            return false;
        });
    }

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
            if (isNaN(d.maxweight))
                d.maxweight = 0;
            maxval = Math.max(maxval, d.maxweight);
        })

        .attr("id", function (d) {
            return "n" + indexstart + "_" + d.id;
        }) //Now each datum can be accessed as a DOM element
        .attr("meta", function (d) {
            return "n" + JSON.stringify(d.type);
        })
        .attr("r", function (d) {
            if (c_nodes.indexOf(d.id) > -1)
                return 20;
            return (d.kcore * 2) + 5;
        })
        .attr("stroke",function(d){
           if (d.type == "commoner")
                return d3.color("steelblue");
            if (d.type == "listing")
                return d3.color("purple");
            if (d.type == "tag")
                return d3.color("green");
            return d3.color("red");
        })
        .attr("stroke-width",function(d){
            for(var i=0; i < colluders.length; i++){
                if(colluders[i].includes(d.id))
                    return 4;
            }
            if (c_nodes.indexOf(d.id) > -1)
                return 7;
            return 0;
        })
        .attr("fill", function (d) {
            for(var i=0; i < colluders.length; i++){
                if(colluders[i].includes(d.id))
                    return d3.color("darkred");
            }
            if (c_nodes.indexOf(d.id) > -1)
                return d3.color("orange");
            if (d.type == "commoner")
                return d3.color("steelblue");
            if (d.type == "listing")
                return d3.color("purple");
            if (d.type == "tag")
                return d3.color("green");
            return d3.color("red");
        }) //Coloured based on their type
        .style("opacity", function (d) { //Make nodes and links transparent
            if(d.maxweight < strengthslider)
                return 0;
            if (filtertype == "tag") {
                if (tag == "all" || (d.type == "tag" && d.name == tag)
                    || d.tags.includes(tag))
                    return 1;
                return 0.15;
            } else if (filtertype == "network") {
                if (tag == "all" || d.nodemeta.includes(tag))
                    return 1;
                return 0.15;
            } else {
                return 1;
            }
        })
        .on("click", function (od) {
            window.open("https://djr53.host.cs.st-andrews.ac.uk/"
            + "commonfare/web/personal_simplified.html?userid=" + od.id,
            "_blank");
        })
        //Node and link highlighting
        .on("mouseover", function (d) {
            selected_node = d.id;
            d3.select(this).attr("fill", d3.color("orange"));
            sourcelinks = link.filter(function (d) {
                return d.source.id == selected_node
                       || d.target.id == selected_node;
            });

            sourcelinks.each(function (d) {
                d3.select(this).attr("oldstrokeval",
                d3.select(this).style("stroke-width"));

                d3.select(this).attr("oldcolourval",
                d3.select(this).style("stroke"));

                d3.select(this).style("stroke", "green");

            });
            //Add the tooltips, formatted
            div.transition()
            .duration(200)
            .style("opacity", 0.9);
            if (d.type == "commoner" || d.type == "tag") {
                div.html(d.name + "</br>" + d.kcore)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px")
                .style("background", function () {
                    if (d.type == "commoner")
                        return "lightsteelblue";
                    return "green";
                });
            } else {
                div.html(d.title + "</br>" + d.kcore)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px")
                .style("background", "pink");
            }
        })
        .on("mouseout", function (d) {
            //Set the colour of links back to black
            d3.select(this).attr("fill", function (d) {
                for(var i=0; i < colluders.length; i++){
                    if(colluders[i].includes(d.id))
                        return d3.color("darkred");
                }
                if (c_nodes.indexOf(d.id) > -1)
                    return d3.color("orange");
                if (d.type == "commoner")
                    return d3.color("steelblue");
                if (d.type == "listing")
                    return d3.color("purple");
                if (d.type == "tag")
                    return d3.color("green");
                return d3.color("red");
            });
            sourcelinks.each(function (d) {
                d3.select(this).style("stroke",
                d3.select(this).attr("oldcolourval"));
            });
            sourcelinks.each(function (d) {
                d3.select(this).style("stroke-width",
                d3.select(this).attr("oldstrokeval"));
            });
            div.transition()
            .duration(500)
            .style("opacity", 0);
        });
    updateStrengthSlider(strengthslider, maxval);

    if (indexstart == 0)
        for (var comm in global_communities) {
            nodeids = global_communities[comm][0];
            for (var i = 0; i < nodeids.length; i++) {
                var nodedata = d3.select("#n0_" + nodeids[i]).datum();
                if ("name" in nodedata)
                    ids_to_titles[nodeids[i]] = nodedata["name"];
                else
                    ids_to_titles[nodeids[i]] = nodedata["title"];

            }

        }
    //Arrowheads that show the direction of the interaction.
    svg.selectAll("defs").remove();
    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    .each(function (d) {
        if ("create_story" in d || "create_listing" in d)
            d.size = 2;
        else
            d.size = 1;
    })
    .attr("id", function (d) {
        return "mend" + d.source.id + "-" + d.target.id;
    })

    .attr("viewBox", function (d) {
        if (d.size == 2)
            return "0 -10 20 20";
        return "0 -5 10 10"
    })
    .attr("refX", function (d) {
        if (d.target.id == null)
            return 10;
        if (d3.select("#n" + indexstart + "_" + d.target.id).empty())
            return 10;
        radius = d3.select("#n" + indexstart + "_" + d.target.id).attr("r");
        return (d.size * 10) + parseInt(radius);
    })
    .attr("markerUnits", "userSpaceOnUse")
    .attr("markerWidth", function (d) {
        return d.size * 10;
    })
    .attr("markerHeight", function (d) {
        return d.size * 10;
    })
    .attr("orient", "auto")
    .append("path")
    .attr("d", function (d) {
        if (d.size == 2)
            return "M0,-10L20,0L0,10";
        return "M0,-5L10,0L0,5"
    })
    .style("stroke",function(d){
        if (d.size == 2)
            return "darkred";
        return "white";
    })
    .style("stroke-width",function(d){
        if (d.size == 2)
           return 3;
       return 0;
    })
    .style("fill", function (d) {
        if (d.size == 2)
            return "darkred";
        if (c_nodes.indexOf(d.source.id) > -1
            && c_nodes.indexOf(d.target.id) > -1)
            return "orange";
        if ("edgemeta" in d && d.edgemeta.includes("story"))
            return "red";
        if ("edgemeta" in d && d.edgemeta.includes("social"))
            return "orange";
        if ("edgemeta" in d && d.edgemeta.includes("listing"))
            return "purple";
        if ("edgemeta" in d && d.edgemeta.includes("transaction"))
            return "darkblue";
        return "black";
    });

    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    .each(function (d) {
        if ("create_story" in d || "create_listing" in d)
            d.size = 2;
        else
            d.size = 1;
    })
    .attr("id", function (d) {
        return "mstart" + d.source.id + "-" + d.target.id;
    })
    .attr("viewBox", function (d) {
        if (d.size == 2)
            return "-20 -10 20 20";
        return "-10 -5 10 10"
    })
    .attr("refX", function (d) {
        if (d.source.id == null)
            return 10;
        if (d3.select("#n" + indexstart + "_" + d.source.id).empty())
            return 10;
        radius = d3.select("#n" + indexstart + "_" + d.source.id).attr("r");
        return  - (d.size * 10) - parseInt(radius);
    })
    .attr("markerUnits", "userSpaceOnUse")
    .attr("markerWidth", function (d) {
        return d.size * 10;
    })
    .attr("markerHeight", function (d) {
        return d.size * 10;
    })
    .attr("orient", "auto")
    .append("path")
    .attr("d", function (d) {
        if (d.size == 2)
            return "M0,-10L-20,0L0,10";
        return "M0,-5L-10,0L0,5"
    })
    .style("stroke",function(d){
        if (d.size == 2)
            return "darkred";
        return "white";
    })
    .style("stroke-width",function(d){
        if (d.size == 2)
           return 3;
       return 0;
    })
    .style("fill", function (d) {
        if (d.size == 2)
            return "darkred";
        if (c_nodes.indexOf(d.source.id) > -1
            && c_nodes.indexOf(d.target.id) > -1)
            return "orange";
        if ("edgemeta" in d && d.edgemeta.includes("story"))
            return "red";
        if ("edgemeta" in d && d.edgemeta.includes("social"))
            return "orange";
        if ("edgemeta" in d && d.edgemeta.includes("listing"))
            return "purple";
        if ("edgemeta" in d && d.edgemeta.includes("transaction"))
            return "darkblue";
        return "black";
    });



    link.exit()
    .remove();
    link = link.enter().append("line")
        .attr("class", "line")
        .merge(link)
        .attr("stroke-width", function (d) {
            if ("tag_story" in d || "tag_commoner" in d || "tag_listing" in d)
                return 0.25;

            //if ('create_story' in d || 'create_listing' in d)
        //        return 4.5;
            if ("edgemeta" in d && d.edgemeta.includes("social")
                && d.edgemeta.includes("transaction"))
                return 3;
          //  if ('edgeweight' in d)
        //        return Math.min(8, d.edgeweight[d.source.id]);
            return 2;
        })
        .attr("edgemeta", function (d) {
            return d.id + JSON.stringify(d.edgemeta);
        })
        .style("stroke", function (d) {
            if (c_nodes.indexOf(d.source.id) > -1
                && c_nodes.indexOf(d.target.id) > -1)
                return "orange";
            if ("edgemeta" in d && d.edgemeta.includes("story"))
                return "red";
            if ("edgemeta" in d && d.edgemeta.includes("social")
                && d.edgemeta.includes("transaction"))
                return "#FFC31E";
            if ("edgemeta" in d && d.edgemeta.includes("social"))
                return "orange";
            if ("edgemeta" in d && d.edgemeta.includes("listing"))
                return "purple";
            if ("edgemeta" in d && d.edgemeta.includes("transaction"))
                return "darkblue";
            return "black";
        })
        .style("stroke-dasharray",function(d){
            if ("edgemeta" in d && d.edgemeta.includes("social")
                && d.edgemeta.includes("transaction"))
                return "20,10";
            return 0;
            })
        .attr("marker-end", function (d) {
            if ((nodetypes[d.source.id] == "commoner"
                && nodetypes[d.target.id] != "tag")) {
                return "url(#mend" + d.source.id + "-" + d.target.id + ")";
            }
            return null;
        })
        .attr("marker-start", function (d) {
            if ((nodetypes[d.target.id] == "commoner"
                && nodetypes[d.source.id] != "tag")) {
                return "url(#mstart" + d.source.id + "-" + d.target.id + ")";
            }
            return null;
        })
        .style("opacity", function (d) {
            if ("maxweight" in d && d.maxweight < strengthslider
                || (strengthslider > 0 && d.maxweight == undefined))
                return 0;
            if (filtertype == "tag") {
                if (tag == "all"
                    || (d.source.type == "tag" && d.source.name == tag)
                    || (d.target.type == "tag" && d.target.name == tag))
                    return 1;
                return 0.15;
            } else if (filtertype == "network") {
                if (tag == "all"
                    || (d.edgemeta != null && d.edgemeta.includes(tag)))
                    return 1;
                return 0.15;
            } else {
                return 1;
            }
        });

    function ticked() {
        link
        .attr("x1", function (d) {return d.source.x;})
        .attr("y1", function (d) {return d.source.y;})
        .attr("x2", function (d) {return d.target.x;})
        .attr("y2", function (d) {return d.target.y;});
        extrashit.selectAll(".extralines")
        .attr("x1", function (d) {return d.source.x;})
        .attr("y1", function (d) {return d.source.y;})
        .attr("x2", function (d) {return d.target.x;})
        .attr("y2", function (d) {return d.target.y;});
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

    // Update and restart the simulation.
    active_simulation.nodes(graph.nodes);
    clusters = {};
    node.each(function (d) {
        var radius = d.kcore;
        var clusterID = d.cluster;
        if (!clusters[clusterID] || (radius > clusters[clusterID].kcore)){
            clusters[clusterID] = d;
        }
    });
    console.log("AND NOW WE ARE HERE");
    active_simulation.force("link").links(graph.links);
    if (drawn[indexstart] == false) {
        drawn[indexstart] = true;
        active_simulation.alpha(1);
        n = Math.ceil(Math.log(active_simulation.alphaMin())
            / Math.log(1 - active_simulation.alphaDecay()));
        for (var i = 0; i < n; ++i) {
            active_simulation.tick();
        }
        if ((datafilecounter - 1) > (indexstart + 1)) {
            indexstart++;
            draw();
        } else {
            datafilecounter = 1;
        }
    }
    link
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});

    node
    .attr("cx", function (d) {return d.x;})
    .attr("cy", function (d) {return d.y;});

    extrashit.selectAll(".extralines").remove();

    extrashit.selectAll(".extralines")
    .data(graph.links.filter(function(d){
        return "edgemeta" in d && d.edgemeta.includes("social")
            && d.edgemeta.includes("transaction");
    }))
    .enter().append("line")
    .attr("class","extralines")
    .style("stroke","darkblue")
    .attr("stroke-width",2)
    .attr("z-index",-5)
    .style("opacity", function (d) {
        if (d.maxweight < strengthslider
            ||(strengthslider > 0 && d.maxweight == undefined))
            return 0;
        if (filtertype == "tag") {
            if (tag == "all"
                || (d.source.type == "tag" && d.source.name == tag)
                || (d.target.type == "tag" && d.target.name == tag))
                return 1;
            return 0.15;
        } else if (filtertype == "network") {
            if (tag == "all"
                || (d.edgemeta != null && d.edgemeta.includes(tag)))
                return 1;
            return 0.15;
        } else {
            return 1;
        }
        })
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});
    $("#loadingDiv").css("display","none");
        chartsvg.call(areazoom.transform,
        d3.zoomIdentity.translate(0,0).scale(0.33));
        newplot(plotType);

}