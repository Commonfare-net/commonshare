function zoomCookie() {
	var center = getBoundingBoxCenterX(cookiechart); //rect is the charts parent which expands while zooming
	var chartsWidth = (2 * center) * d3.event.transform.k;
	d3.event.transform.x = center - chartsWidth / 2;
	d3.event.transform.y = center - chartsWidth / 2;
	cookieg.attr("transform", d3.event.transform)
};
var cookiezoom = d3.zoom()
	.scaleExtent([0.5, 2])
	.on("zoom", zoomCookie);

var cookiechart = d3.select("#cookie"),
        cookieg = cookiechart.append("g");
        cookiechart.call(cookiezoom);
  var monthpack = cookieg.append("g").attr("class","cookiepack");
        var cookietext = cookieg.append("text")
        .attr("text-anchor", "middle")
        .attr("stroke","white")
		.style("font-family", "'Dosis', sans-serif");
function plotcookie(mydata){

        d3.select(".cookiepack").html("");

     $("#cookie").bind("wheel mousewheel", function(e) {e.preventDefault()});
    
    var width = 200,
        height = 200,
  	    color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);

    function children(d) {
      return d.cumu_array;
    }
     function summer(total, num) {
        return (isNaN(num) || num instanceof Date) ? total : total + num;
    }

    var cumu_totals = JSON.parse(JSON.stringify(mydata.cumu_totals));
    var cumu_array = d3.keys(cumu_totals).map(function(key){return {"id":mydata.id,"name":key,"total":cumu_totals[key],"kcore":mydata.kcore,"stats":mydata.stats};});
   // cumu_array.push({"name":"commonshare","total":1,"kcore":mydata.kcore});
    var keys = Object.keys(cumu_totals);
    cumu_totals["overall"] = Object.values(cumu_totals).reduce(summer,0);
    cumu_totals["kcore"] = mydata.kcore;
    cumu_totals["cumu_array"] = cumu_array;
    cumu_totals["date"] = mydata.date;
    cumu_totals["stats"] = mydata.stats;
    console.log(cumu_totals);
    var xdisplacements = [];
    var ydisplacements = [];

    var monthname = d3.timeFormat("%b");
    var circlepack;
    //This is silly but because the pack layout size can't be updated dynamically, we have to make one for every circle we're using
    var size = cumu_totals["cumu_array"][0].kcore;
    var scaledsize = size*9 + 30;
    circlepack = d3.pack()
    .size([scaledsize,scaledsize])
    .padding(2);  

    monthpack.selectAll('.cookiecircle').data(circlepack(d3.hierarchy(cumu_totals,children)
                    .sum(function(e) {console.log(e);if(e.name == "date" || e.name == "stats")return 0; return e.total; })
                    .sort(function(a, b) {console.log(a);console.log(b);return b.value - a.value; }))
                  .descendants()).enter().append("circle")
      .attr("class","cookiecircle")
      .attr("transform", function(d) {
      return d.children ? "translate(" + (d.x + width/2 - d.r) + "," + (d.y + height/2 - d.r) + ")" : 
                          "translate(" + (d.x + width/2 - d.parent.r) + "," + (d.y + height/2 - d.parent.r) + ")"; 
      })
      .style("fill", function(d) {if(d.children != null) return "blue"; if(d.data.name == "commonshare")return "blue"; return color(d.data.name); })
      .style("opacity",function(d) {return d.children ? 0.3 : d.data.name == "commonshare" ? 0 : 1;})
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
		})
		.on("click", function (d, i) {
			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		}).transition()
      .duration(750)
      .attr("r",function(d){return d.r;});


	cookietext.text(size);
    cookietext.attr("x",function(){return width/2;});
    cookietext.attr("y",function(){return height/2 + (cookietext.node().getBoundingClientRect().width/4);});
    cookietext
  .transition()
      .duration(750)
        .style("font-size",Math.max(50,size*3+6));
        }