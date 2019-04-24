/**
* This draws the arrows to be drawn on either end 
* of each link to show directionality. 
*/
function drawArrowHeads(){
    svg.selectAll("defs").remove();
    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    //Creation edges have bigger arrowheads
    .each(function (d) {
        d.size = ("create_story" in d || "create_listing" in d) ? 2 : 1;
    })
    .attr("id", function (d) {
        return "mend" + d.source.id + "-" + d.target.id;
    })
    .attr("viewBox", function (d) {
        return (d.size == 2) ? "0 -10 20 20" : "0 -5 10 10";
    })
    .attr("refX", function (d) {
        if (d.target.id == null || 
        (d3.select("#n" + indexstart + "_" + d.target.id).empty())){
            return 10;
        }
        radius = d3.select("#n"+indexstart+"_"+d.target.id).attr("r");
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
        return (d.size == 2) ? "M0,-10L20,0L0,10" : "M0,-5L10,0L0,5";
    })
    .style("stroke", function (d) {
        return (d.size == 2) ? "darkred" : "white";
    })
    .style("stroke-width", function (d) {
        return (d.size == 2) ? 3 : 0;
    })
    .style("fill", function (d) {
        if (d.size == 2){
            return "darkred";
        }
        if (c_nodes.indexOf(d.source.id) > -1 &&
            c_nodes.indexOf(d.target.id) > -1){
            return "orange";
        }
        if("edgemeta" in d){
            if(d.edgemeta.includes("story")){
                return "red";
            }
            if(d.edgemeta.includes("social")){
                return "orange"; 
            }
            if(d.edgemeta.includes("listing")){
                return "purple"; 
            }
            if(d.edgemeta.includes("transaction")){
                return "darkblue";                
            }
        }
        return "black";
    });
    svg.append("defs").selectAll("marker")
    .data(graph.links)
    .enter().append("marker")
    .each(function (d) {
        d.size = ("create_story" in d || "create_listing" in d) ? 2 : 1;
    })
    .attr("id", function (d) {
        return "mstart" + d.source.id + "-" + d.target.id;
    })
    .attr("viewBox", function (d) {
        return (d.size == 2) ? "-20 -10 20 20" : "-10 -5 10 10";
    })
    .attr("refX", function (d) {
        if (d.source.id == null || 
        (d3.select("#n" + indexstart + "_" + d.source.id).empty())){
            return 10;
        }
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
        return (d.size == 2) ? "M0,-10L-20,0L0,10" : "M0,-5L-10,0L0,5";
    })
    .style("stroke", function (d) {
        return (d.size == 2) ? "darkred" : "white";
    })
    .style("stroke-width", function (d) {
        return (d.size == 2) ? 3 : 0;
    })
    .style("fill", function (d) {
        if (d.size == 2){
            return "darkred";
        }
        if (c_nodes.indexOf(d.source.id) > -1 &&
            c_nodes.indexOf(d.target.id) > -1){
            return "orange";
        }
        if("edgemeta" in d){
            if (d.edgemeta.includes("story")){
                return "red";
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
    });
}

/**
 * This allows the links between Commoners that have both transactions and
 * conversations to have the blue-yellow dashed pattern. 
 */
function addDashedArrowLines(){
    extralines.selectAll(".extralines").remove();
    extralines.selectAll(".extralines")
    .data(graph.links.filter(function (d) {
        return "edgemeta" in d && d.edgemeta.includes("social")
        && d.edgemeta.includes("transaction");
     }))
    .enter().append("line")
    .attr("class", "extralines")
    .style("stroke", "darkblue")
    .attr("stroke-width", 2)
    .attr("z-index", -5)
    .style("opacity", function (d) {
        if (d.maxweight < strengthslider ||
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
    })
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});    
}