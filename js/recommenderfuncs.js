//Common functions for graph recommenders
   var closestnodes = [];
   
var graph = {};
var xScale = d3.scaleLinear()
	.domain([0, 500]).range([0, 500]);
var yScale = d3.scaleLinear()
	.domain([0, 500]).range([0, 500]);

//Zooming function
function zoomFunction() {
	var new_xScale = d3.event.transform.rescaleX(xScale)
		var new_yScale = d3.event.transform.rescaleY(yScale)
		g.attr("transform", d3.event.transform)
};
var zoom = d3.zoom().on("zoom", zoomFunction);
var svg = d3.select(".bigvis"), width = +svg.attr("width"), height = +svg.attr("height");
svg.call(zoom);

var g = svg.append("g").attr("transform", "translate(250,250) scale (.35,.35)"),
link = g.append("g").attr("stroke", "#000").attr("stroke-width", 1.5).selectAll(".link"),
node = g.append("g").attr("stroke", "#fff").attr("stroke-width", 1.5).selectAll(".node");
svg.call(zoom.transform, d3.zoomIdentity.translate(0,0).scale(1));

//Tooltip functions from http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
var div = d3.select("body").append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);

    //zoom transform from https://bl.ocks.org/mbostock/b783fbb2e673561d214e09c7fb5cedee allows clicked node to be zoomed in on
function transform() {
	translatex = d3.select("#n" + userid).attr("cx");
	translatey = d3.select("#n" + userid).attr("cy");
	return d3.zoomIdentity
	.translate(width / 2, height / 2)
	.scale(3)
	.translate(-translatex, -translatey);
}
function insert(element, array) {
  if(element.closeness == undefined)
    return;
  array.push(element);
  array.sort(function(a, b) {
    return b.closeness - a.closeness;
  });
 }
 //These forces are tweaked to attract connected nodes to the center
var simulation = d3.forceSimulation()
	.alphaDecay(0.05)
	.force("charge", d3.forceManyBody().strength(function (d) {
            if(d.closeness == undefined || d.closeness == 0)
                return -100;
            return -100/(d.closeness);
            //return 0;
		}))
	.force("link", d3.forceLink().distance(50).id(function (d) {
			return d.id;
		})) //Need the function here to draw links between nodes based on their ID rather than their index
	.force("x", d3.forceX().x(function (d) {
			return width / 2;
		}).strength(function (d) {
            if(d.id == userid)
                return 1;
            if(d.closeness == undefined || d.closeness == 0)
                return 0.05;
            return Math.min(0.05*d.closeness,0.35);
		}))
	.force("y", d3.forceY().y(function (d) {
			return height / 2;
		}).strength(function (d) {
            if(d.id == userid)
                return 1;
            if(d.closeness == undefined || d.closeness == 0)
                return 0.05;
            return Math.min(0.05*d.closeness,0.35);
            }))
            ;
 function mouseovernode(d,node){
            var selection;
			selected_node = d.id;
            if(!isNaN(node))
                selection = this;
            else
                selection = node;
            if(d3.select(selection).style("opacity") == 0.15)
                return;
            d3.selectAll(".circlenode").style("opacity",0.15);
                
            var sharedfriends = [];
            var sharedtags = [];
            var sharedstories = [];
            d3.select("#n"+selected_node).style("opacity",1);
            d3.select("#n"+userid).style("opacity",1);
            for(var i = 0; i < d.inbetweens.length; i++){
                d3.select("#n"+d.inbetweens[i]).style("opacity",1);
                if(nodetypes[d.inbetweens[i]] == "tag")
                    sharedtags.push(nodenames[d.inbetweens[i]]);
                else if(nodetypes[d.inbetweens[i]] == "commoner")
                    sharedfriends.push(nodenames[d.inbetweens[i]]);
                else if(nodetypes[d.inbetweens[i]] == "story")
                    sharedstories.push(nodenames[d.inbetweens[i]]);
                d3.select("#l"+d.id+"-"+d.inbetweens[i]).style("opacity",1);
                d3.select("#l"+d.inbetweens[i]+"-"+d.id).style("opacity",1);
                d3.select("#l"+d.inbetweens[i]+"-"+userid).style("opacity",1);
                d3.select("#l"+userid+"-"+d.inbetweens[i]).style("opacity",1);
            }                
			d3.select(selection).attr("fill", d3.color("orange"));
			sourcelinks = link.filter(function (d) {
					return d.source.id == selected_node || d.target.id == selected_node;
				});

			sourcelinks.each(function (d) {
				d3.select(this).attr("oldstrokeval", d3.select(this).style("stroke-width"));
				d3.select(this).attr("oldcolourval", d3.select(this).style("stroke"));
				d3.select(this).style("stroke", 'green');

			});
			//Add the tooltips, formatted based on whether they represent a user or story
			div.transition()
			.duration(200)
			.style("opacity", .9);
			if (d.type == "commoner" || d.type == "tag") {
                $('.card-title').text(d.name);
                $('.card-text').html("Shared friends: <b>" + sharedfriends + "</b></br>Shared stories: <b>"+sharedstories+"</b></br>Shared tags: <b>" + sharedtags+ "</b>");
			} else {
                $('.card-title').text(d.title);
                $('.card-text').html("Shared friends: <b>" + sharedfriends + "</b></br>Shared stories: <b>"+sharedstories+"</b></br>Shared tags: <b>" + sharedtags+ "</b>");
			}
    }
    function mouseoutnode(d,node) {
     var selection;
     		d3.selectAll('.circlenode').style("opacity", function (d) { //Make nodes and links transparent if they aren't linked to tags
			if((d.inbetweens != undefined && d.inbetweens.length > 0 && d.type != "tag") || d.id == userid)
            return 1;
            d3.select(this).style("pointer-events","none");
            return 0.15;
		})
			selected_node = d.id;
            if(!isNaN(node))
                selection = this;
            else
                selection = node;
          if(d3.select(selection).style("opacity") == 0.15)
                return;
            for(var i = 0; i < d.inbetweens.length; i++){
                d3.select("#n"+d.inbetweens[i]).style("opacity",0.15);
                d3.select("#l"+d.id+"-"+d.inbetweens[i]).style("opacity",0.15);
                d3.select("#l"+d.inbetweens[i]+"-"+d.id).style("opacity",0.15);
                d3.select("#l"+d.inbetweens[i]+"-"+userid).style("opacity",0.15);
                d3.select("#l"+userid+"-"+d.inbetweens[i]).style("opacity",0.15);
            }        
			//Set the colour of links back to black, and the thickness to its original value
			d3.select(selection).attr("fill", function (d) {
            if (d.id == userid)
				return d3.color("orange");
				if (d.type == "commoner")
					return d3.color("steelblue");
				if (d.type == "listing")
					return d3.color("purple");
				if (d.type == "tag")
					return d3.color("lightgreen");
				return d3.color("red");
			});
			sourcelinks.each(function (d) {
				d3.select(selection).style("stroke", d3.select(selection).attr("oldcolourval"));
			});
			sourcelinks.each(function (d) {
				d3.select(selection).style("stroke-width", d3.select(selection).attr("oldstrokeval"));
			});
			div.transition()
			.duration(500)
			.style("opacity", 0);
		}
        
        	//Updates to make on simulation 'tick'
	function ticked() {
		link
		.attr("x1", function (d) {
			return d.source.x;
		})
		.attr("y1", function (d) {
			return d.source.y;
		})
		.attr("x2", function (d) {
			return d.target.x;
		})
		.attr("y2", function (d) {
			return d.target.y;
		});

		node
		.attr("cx", function (d) {
			return d.x;
		})
		.attr("cy", function (d) {
			return d.y;
		});
	}
    function renderList(){
    var listContainer = $('.list-group');
		listContainer.empty();
		for (var i = 0; i < closestnodes.length; i++) {
			var tagname = closestnodes[i].type == 'story' || closestnodes[i].type == 'listing' ? closestnodes[i].title : closestnodes[i].name;
			var source = "";
            if(closestnodes[i].type == "story")
                source = "icons/storyicon.svg";
            else if(closestnodes[i].type == "listing")
                source = "icons/listingicon.svg";
            else if(closestnodes[i].type == "commoner")
                source = "icons/usericon.svg";
            else
                continue;
//                source = "icons/tagicon.svg";
			listContainer.append('<a href="#" class="list-group-item" type="' + closestnodes[i].type + '"id="'+closestnodes[i].id+'">' + tagname + '<img src="'+source+'" height="30" width="30"/>');
		}
        $('a').mouseover(function(e){
            var node = d3.select("#n"+$(this).attr("id"));
            mouseovernode(node.datum(),"#n"+$(this).attr("id"));
        });
        $('a').mouseout(function(e){
            var node = d3.select("#n"+$(this).attr("id"));
            mouseoutnode(node.datum(),"#n"+$(this).attr("id"));
        });
		$('a').click(function (e) {
			e.preventDefault();
            var node = $(this).attr("type");
            var id = $(this).attr("id");
            console.log("Type is " + node);
                if(node == "commoner")
            	window.open('https://djr53.host.cs.st-andrews.ac.uk/commonfare/web/social_recommender.html?userid=' + id);
                else if(node =="story" || node == "listing")
            	window.open('https://djr53.host.cs.st-andrews.ac.uk/commonfare/web/object_recommender.html?objectid=' + id);
			var content = $(this).ignore("span").text(); // or var clickedBtnID = this.id
		});
    }
    
    function addLinks(){
        link.exit()
	.remove();
	link = link.enter().append("line")
		.attr("class", "line")
		.merge(link)
        .attr("id", function (d) {
			return "l"+d.source+"-"+d.target;
		}) 
		.attr("stroke-width", function (d) {
            if('edgeweight' in d)
                return Math.min(8,d.edgeweight[d.source.id]);
			if ('create_story' in d || 'create_listing' in d)
				return 4.5;
			else if ('tag_story' in d || 'tag_commoner' in d || 'tag_listing' in d)
				return 0.25;
			return 2;
		})
		.attr("edgemeta", function (d) {
			return d.id + JSON.stringify(d.edgemeta);
		})
		.style("stroke", function (d) {
			if ('edgemeta' in d && d.edgemeta.includes('story'))
				return 'red';
			if ('edgemeta' in d && d.edgemeta.includes('social'))
				return 'orange';
			if ('edgemeta' in d && d.edgemeta.includes('listing'))
				return 'purple';
			if ('edgemeta' in d && d.edgemeta.includes('transaction'))
				return 'darkblue';
			return 'black';
		})
		.attr("marker-end", function (d) {
			if ((nodetypes[d.source.id] == 'commoner' && nodetypes[d.target.id] != 'tag')) {
				return "url(#mend" + d.source.id + "-" + d.target.id + ")";
			}
			return null;
		})
		.attr("marker-start", function (d) {
			if ((nodetypes[d.target.id] == 'commoner' && nodetypes[d.source.id] != 'tag')) {
				return "url(#mstart" + d.source.id + "-" + d.target.id + ")";
			}
			return null;
		})
		.style("opacity", function (d) {
                return 0.15;
		});
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