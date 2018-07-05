
function plotgroupedbar(user){


var chart = d3.select("#groupedbarchart"),
    margin = {top: 20, right: 20, bottom: 70, left: 50},
    chartwidth = +chart.attr("width") - margin.left - margin.right,
    chartheight = +chart.attr("height") - margin.top - margin.bottom,
    chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var xScale = d3.scaleLinear()
    .domain([200,200+chartwidth]).range([200,200+chartwidth]);
var yScale = d3.scaleLinear()
    .domain([0,400]).range([0,400]);
var parseTime = d3.timeParse("%d/%m/%y");
var parseMonthAxis = d3.timeFormat("%Y-%m");
var x0 = d3.scaleBand()
    .rangeRound([0, chartwidth])
    .paddingInner(0.1);

var x1 = d3.scaleBand()
    .padding(0.05);
var y = d3.scaleLinear()
    .rangeRound([chartheight, 0]);
color.domain(mykeys);


var area = d3.area()
    .x(function(d) { return x(d.data.date); })
    .y0(function(d) { return y(d[0]); })
    .y1(function(d) { return y(d[1]); });

var kcoreline = d3.line()
    .curve(d3.curveMonotoneX)
    .x(function(d) {return x0(parseTime(d.date)) +(x0.bandwidth()/2); })
    .y(function(d) {return y(d.kcore); });
    var avg_total_object = []
    var kcore_vals = []
    for (var month in data){
        var avg_totals = data[month].avg_totals;
        var keys = Object.keys(avg_totals);
        avg_totals["date"] = data[month].date;
        avg_totals["stats"] = data[month].stats;
        avg_total_object.push(avg_totals);
        kcore_vals.push({"kcore":data[month].kcore,"date":data[month].date});
        console.log(data[month].kcore); console.log(data[month].date);
    }

  var maxDateVal = d3.max(avg_total_object, function(d){
    var vals = d3.keys(d).map(function(key){ return key !== 'date' && key !== 'stats' ? d[key] : 0 });
    return d3.max(vals);
  });
  
  // Set domains for axes
  x0.domain(avg_total_object.map(function(d) { return parseTime(d.date); }));
  x1.domain(keys).rangeRound([0, x0.bandwidth()]);
  y.domain([0,maxDateVal]);

  chartg.append("g")
    .selectAll("g")
    .data(avg_total_object)
    .enter().append("g")
      .attr("transform", function(d) { return "translate(" + x0(parseTime(d.date)) + ",0)"; })
      .attr("id", function(d) { return d.key; })
      .attr("clip-path", "url(#clip)")
    .selectAll("rect")
    .data(function(d) { return keys.map(function(key) { return {key: key, value: d[key], stats: d.stats}; });  })
    .enter().append("rect")
      .attr("x", function(d) { return x1(d.key); })
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return chartheight - y(d.value); })
      .attr("width", function(d){ return x1.bandwidth();})
       .attr("fill", function(d) { return color(d.key); })
   .on("mouseover", function(d) { 
        var html_content = "";
        for(var meta in d.stats){
            if(meta == d.key){ //If this holds the interactions of this particular type
                for(var statistic in d.stats[meta]){
                    if(d.stats[meta][statistic].length > 0)
                        html_content += prettyKeys[statistic] + ": " + d.stats[meta][statistic].length + "<br/>";
                }
            }
        }
        d3.select(this).style("opacity",0.7);
        div.transition()		
                .duration(200)		
                .style("opacity", .9);		
            div	.html(html_content)	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
   })
  .on("mouseout", function() {
    d3.select(this).style("opacity",1);
    div.transition()		
       .duration(500)		
       .style("opacity", 0);
  });
  
  
  var linepath = chartg.append("path")
    .datum(kcore_vals)
    .attr("class","mypath")
    .attr("clip-path", "url(#clip)")
    .attr("d",kcoreline)
    .style("stroke", "black")
    .style("stroke-width",3.5);
    
chartg.selectAll("circle")
      .data(kcore_vals)
      .enter().append("circle")
      .attr("class","mydot")
      .attr("r", 6)
      .attr("clip-path","url(#clip)")
      .attr("cx", function(d) {return x0(parseTime(d.date)) + (x0.bandwidth()/2); } )
      .attr("cy", function(d) {return y(d.kcore); } )
       .on("mouseover", function(d) {
            var html_content = "";
            d3.select(this).attr("r",8);
            div.transition()		
                .duration(200)		
                .style("opacity", .9);		
            div	.html(html_content)	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
        .on("mouseout", function(d) {	
            d3.select(this).attr("r",6);
            div.transition()		
                .duration(500)		
                .style("opacity", 0);	
        });
  var clip = chartg.append("clipPath")
    .attr("id", "clip");
  var clipRect = clip.append("rect")
    .attr("width", 0)
    .attr("height", chartheight);
  var totalWidth = chartwidth;
  
  clipRect.transition()
    .duration(4000)
    .ease(d3.easeLinear)
    .attr("width", totalWidth)
 
 
  chartg.append("g")
      .attr("transform", "translate(0," + chartheight + ")")
      .attr("class","axis")
      .call(d3.axisBottom(x0).tickFormat(formatDate));

  chartg.append("g")
      .attr("class","axis")
      .call(d3.axisLeft(y).ticks(4))
      .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Commonshare");

  
  //Adapted from http://zeroviscosity.com/d3-js-step-by-step/step-3-adding-a-legend
  var legendRectSize = 18;
  var legendSpacing = 4;
  var opacity = 1;
  var legend = chartg.selectAll(".legend")
    .data(color.domain())
    .enter()
    .append('g')
    .attr('class','legend')
    .on("mouseover",function(d){d3.select(this).style('fill',color);document.body.style.cursor = "pointer";})
    .on("mouseout",function(d){d3.select(this).style('fill','black');document.body.style.cursor = "auto";})
    .on("click",function(d){legendclick(d);d3.select(this).style('opacity',opacity);});
    
    
  legend.append('rect')
  .attr('width', legendRectSize)
  .attr('height', legendRectSize)
  .style('fill',color)
  .style('stroke',color);
  
  legend.append('text')
  .attr('x', legendRectSize + legendSpacing)
  .attr('y', legendRectSize - legendSpacing)
  .text(function(d) { return d;});
  var olddate = "";
    legend.attr('transform', function(d,i){
        var element = d3.select(this).node();
        var elementwidth = 150;
        var width = legendRectSize + legendSpacing;
        var horz = elementwidth * i;
        var vert = -20;
        return 'translate(' + (horz) + ',' + vert + ')';
    })
  function legendclick(d){
    if(d3.select("#"+d).style("visibility") == "visible"){
        d3.select("#"+d).style("visibility","hidden");
        d3.selectAll(".mydot"+d).style("visibility","hidden");
        opacity = 0.5;
    }
    else{
        d3.select("#"+d).style("visibility","visible");
        d3.selectAll(".mydot"+d).style("visibility","visible");
        opacity = 1;
    }
  }
  function legendmove(){
      document.body.style.cursor = "pointer";
  }

}
