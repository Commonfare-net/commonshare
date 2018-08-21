
function plotdonut(mydata){

    var chart = d3.select("#donut");
        chartg = chart.append("g");

     $("#donut").bind("wheel mousewheel", function(e) {e.preventDefault()});


    var width = 200,
        height = 200,
        color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']); 
    
    radius = Math.min(width, height) / 2;

    console.log(mydata);
    var edgetotals = mydata.edgetotals;
    console.log(mydata.edgetotals);
    var edgekeys = Object.keys(edgetotals);
    var piesegments = [];
    for(var i = 0; i < edgekeys.length; i++){
        piesegments.push([edgekeys[i],edgetotals[edgekeys[i]]]);
    }
    console.log(piesegments);
    var pie = d3.pie()
        .sort(null)
        .value(function(d) {
            return d[1];
        });

    var arc = d3.arc()
        .outerRadius(radius)
        .innerRadius(radius * 0.8);

        
   var kcore = chartg.append("text")
   .style("font-size","70")
         .style("font-family","'Dosis', sans-serif")

   //.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
   .text(mydata.kcore);
   var element = kcore.node();
	var elementwidth = element.getBoundingClientRect().width;
	var elementheight = element.getBoundingClientRect().height;
    console.log("number height is "  + elementheight);
   kcore.attr("transform", "translate(" + ((width / 2)-(elementwidth/2)) + "," + ((height / 2)+(elementheight/4)) + ")");

var g = chartg.selectAll(".arc")
      .data(pie(piesegments))
    .enter().append("g")
      .attr("class", "arc")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

      
      g.append("path")
      .attr("d", arc)
      .style("fill", function(d) { return color(d.data[0]); })
          
      g.append("text")
      .style("text-anchor","middle")
      .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
      .attr("dy", ".35em")
      .style("font-family","'Dosis', sans-serif")
      .text(function(d) { console.log(d.data[0]);if(d.data[1] >= 1)return d.data[0];return ""; });

      }