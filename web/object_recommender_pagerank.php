<!DOCTYPE html>
<meta charset="utf-8">
<head>
<link rel="stylesheet" type="text/css" href="css/buttons.css" />
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<link rel="stylesheet" type="text/css" href="css/commonfare.css"></head>
        
<body>
<?php
$output = shell_exec("python pagerank.py data/moredataparsed.gexf " . $_GET["objectid"]);
echo $output;?><br>

    <!--Container for the network viz-->
    <svg style="width:40%; float:left; display:inline-block;" class="bigvis" width="500" height="500"></svg>
    <div class="card" style="margin-top:50px;display:inline-block;float:left;width: 300px;">
      <div class="card-body">
        <h5 class="card-title"></h5>
        <p class="card-text"></p>
      </div>
    </div>
    <div class="list-group" id="list-group" style="margin-top:50px; width:30%;float:right;display:inline-block;margin-right:100px; text-align: center">
    </div>        
</body>

<?php echo '
<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="scripts/recommenderfuncs.js"></script>
<script>
var urlParams = new URLSearchParams(window.location.search);
var userid = urlParams.get("objectid"); 
//All this stuff is for the network viz
var graph = {};

 
function loadDataFiles(view) {
	var url = "data/objectdata/"+userid+".json";
	$.ajax({

		url: url,
		type: "HEAD",
		error: function () {},
		success: function () {
			d3.json(url, function (results) {
                graph = results;
            	draw(0, "all");    
                
            });
		}
	});
}

loadDataFiles("cumulative");

function draw(tag, filtertype) {
	nodetypes = {};
    nodenames = {};
    
	//https://stackoverflow.com/questions/11347779/jquery-exclude-children-from-text
	$.fn.ignore = function (sel) {
		return this.clone().find(sel || ">*").remove().end();
	};

	selected_node = "";
	node = node.data(graph.nodes, function (d) {
			return d.id;
		});
	link = link.data(graph.links, function (d) {
			return d.source + "-" + d.target;
		});
	tagcounts = graph.tagcount;

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
            nodenames[d.id] = (d.type == "story") ? d.title : d.name;
            
		})
        .attr("class","circlenode")

		.attr("id", function (d) {
			return "n" + d.id;
		}) //Now each datum can be accessed as a DOM element
		.attr("meta", function (d) {
			return "n" + JSON.stringify(d.type);
		})
		.attr("r", function (d) {
            insert(d,closestnodes);
             if(d.id == userid)
                return 12;       
            return 5 + d.closeness;
            if(d.kcore == undefined)
                return 1;
			return (d.kcore * 2) + 5;
		})
		.attr("fill", function (d) {
			if (d.id == userid)
				return d3.color("orange");
			if (d.type == "commoner")
				return d3.color("steelblue");
			if (d.type == "listing")
				return d3.color("purple");
			if (d.type == "tag")
				return d3.color("lightgreen");
			return d3.color("red");
		}) //Coloured based on their type
		.style("opacity", function (d) { //Make nodes and links transparent if they arent linked to tags
			if((d.inbetweens != undefined && d.inbetweens.length > 0 && d.type != "tag") || d.id == userid)
            return 1;
                        d3.select(this).style("pointer-events","none");

            return 0.15;
		})
		.on("click", function (od) {
            if(od.type == "commoner")
            	window.open("https://djr53.host.cs.st-andrews.ac.uk/commonfare/web/social_recommender.html?userid=" + od.id, "_blank");
            else if(od.type == "listing" || od.type == "story")
            				window.open("https://djr53.host.cs.st-andrews.ac.uk/commonfare/web/object_recommender.html?objectid=" + od.id, "_blank");

			//Reset previously clicked nodes colour
			if (userid != "")
				d3.select("#n" + userid).attr("fill", function (d) {
					if (d.type == "commoner")
						return d3.color("steelblue");
					if (d.type == "listing")
						return d3.color("purple");
					if (d.type == "tag")
						return d3.color("lightgreen");
					return d3.color("red");
				}) //Coloured based on their type

		})
		//Node and link highlighting
		.on("mouseover", mouseovernode)
		.on("mouseout", mouseoutnode);

	addLinks();
	
        
    renderList();
    simulation.nodes(graph.nodes)
              .on("tick",ticked);
    simulation.force("link").links(graph.links);

}

</script>'
?>