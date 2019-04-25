
/**
* This switches the simulation to one of the two functions below 
* and moves the nodes and links to their appropriate places
*/
function togglegroups(checkboxelem) {
    sim = (checkboxelem.checked) ? community_sim : simulation;
    sim.nodes(graph.nodes);
    sim.force("link").links(graph.links);
    sim.alpha(1);
    //Manual ticking to calculate final position of nodes before moving them
    n = Math.ceil(Math.log(sim.alphaMin()) / Math.log(1 - sim.alphaDecay()));
    for (i = 0; i < n; i+=1) {
        sim.tick();
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

    extralines.selectAll(".extralines")
    .transition()
    .duration(2000)
    .attr("x1", function (d) {return d.source.x;})
    .attr("y1", function (d) {return d.source.y;})
    .attr("x2", function (d) {return d.target.x;})
    .attr("y2", function (d) {return d.target.y;});
    
    //Changes the position of the 'convex hull' around the nodes
    if (indexstart == 0) {
        var hull = d3.polygonHull(c_nodes.map(function (d) {
            return [d3.select("#n" + indexstart + "_" + d).datum().x,
            d3.select("#n" + indexstart + "_" + d).datum().y];
        }));
        convexHull.datum(hull);
        convexHull
        .transition()
        .duration(2000)
        .attr("d", function (d) {return "M" + d.join("L") + "Z";});
    }
}

//Standard force-directed simulation
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
            return d.id;
      }).distance(100))
    .force("collision", d3.forceCollide().radius(function(d) {
        return 20;
    }))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("x", d3.forceX().x(width / 2).strength(0.2))
    .force("y", d3.forceY().y(height / 2).strength(0.2))
    .stop();
    
//Clustering simulation, uses the forceCluster function 
var community_sim = d3.forceSimulation()
    .force("charge", d3.forceManyBody().strength(-10))
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }).strength(0))
    .force("center", d3.forceCenter(500 / 2, 600 / 2))
    .force("cluster", forceCluster)
    .force("collide", d3.forceCollide(22).strength(0.9))
    .stop();
var sim = simulation;

/**
* Clustering function to bunch nodes 
* that are in the same cluster together
*/
function forceCluster(alpha) {
        console.log("ALpha is " + alpha);

    node.each(function (d) {
        cluster = clusters[d.cluster];
        if (cluster === d){
            return;
        }
        var xpos = d.x - cluster.x;
        var ypos = d.y - cluster.y;
        var l = Math.sqrt(xpos * xpos + ypos * ypos);
        var r = d.kcore + cluster.kcore;
        if (l != r) {
            l = (l - r) / l * alpha;
            d.x -= xpos *= l;
            d.y -= ypos *= l;
            cluster.x += xpos;
            cluster.y += ypos;
        }
    });
}