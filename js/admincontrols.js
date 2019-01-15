//controls yo
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
$("#cleardyn").click(function(e){
    e.preventDefault();
    clearDyn();
});

function clearDyn(){
    d3.select(".hull").attr("d", 0);
    d3.selectAll(".marker").remove();
    c_nodes = [];
    draw();
}

function toggletags(checkboxelem){
    node.each(function(d){
       if(d.type == "tag")
           d3.select(this).style("opacity",checkboxelem.checked);
    });
    link.each(function(d){
       if(d.source.type == "tag" || d.target.type == "tag")
           d3.select(this).style("opacity",checkboxelem.checked);
    });
}
function toggledate(type) {
    clearDyn();
    var datafilecounter = 0;
    var queue = d3.queue();
    var indexstart = 1;
    if(type === "all"){
        $("#curdate").text("All time");
        $("#myslider").css("opacity", 0.4);
        $("#myslider").css("pointer-events", "none");
        currentDate = data[1].date;
        sliderhandle.attr("cx", dateslidex(Object.keys(data).length-1));
        indexstart = 0;
        draw();
    }
    else{
        loadDateFiles(queue,type);
        $("#myslider").css("opacity", 1);
        $("#myslider").css("pointer-events", "auto");    
    }
}

function togglegroups(checkboxelem) {
    
    if (checkboxelem.checked){
        active_simulation = community_sim;
    }
    else{
        active_simulation = simulation;
    }
    active_simulation
        .nodes(graph.nodes)
        .force("link")
        .links(graph.links)
        .alpha(1);
    n = Math.ceil(Math.log(active_simulation.alphaMin())
        / Math.log(1 - active_simulation.alphaDecay()));
    
    for (var i = 0; i < n; ++i) {
        active_simulation.tick();
    }
    
    node.transition()
        .duration(2000)
        .attr("cx", function (d) {return d.x;})
        .attr("cy", function (d) {return d.y;})

    link.transition()
        .duration(2000)
        .attr("x1", function (d) {return d.source.x;})
        .attr("y1", function (d) {return d.source.y;})
        .attr("x2", function (d) {return d.target.x;})
        .attr("y2", function (d) {return d.target.y;});

    extrashit.selectAll(".extralines")
        .transition()
        .duration(2000)
        .attr("x1", function (d) {return d.source.x;})
        .attr("y1", function (d) {return d.source.y;})
        .attr("x2", function (d) {return d.target.x;})
        .attr("y2", function (d) {return d.target.y;});
    if(indexstart == 0){
        var hull = d3.polygonHull(c_nodes.map(function (d) {
            return [d3.select("#n" + indexstart + "_" + d).datum().x,
                    d3.select("#n" + indexstart + "_" + d).datum().y];
        }));
        convexHull.datum(hull);
        convexHull
        .transition()
        .duration(2000)
        .attr("d", function (d) {
            return "M" + d.join("L") + "Z";
        });
    }
}
