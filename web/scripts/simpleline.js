function plotsimpleline(user){

var chart = d3.select("#linechart"),
    margin = {top: 20, right: 20, bottom: 70, left: 50},
    chartwidth = +chart.attr("width") - margin.left - margin.right,
    chartheight = +chart.attr("height") - margin.top - margin.bottom,
    chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var xScale = d3.scaleLinear()
    .domain([200,200+chartwidth]).range([200,200+chartwidth]);
var yScale = d3.scaleLinear()
    .domain([0,400]).range([0,400]);
var x = d3.scaleTime()
    .rangeRound([0, chartwidth]);
var y = d3.scaleLinear()
    .rangeRound([chartheight, 0]);

var line = d3.line()
    .curve(d3.curveMonotoneX)
    .x(function(d) { return x(parseTime(d.date)); })
    .y(function(d) { return y(d.total); });

var kcoreline = d3.line()
    .curve(d3.curveMonotoneX)
    .x(function(d) { return x(parseTime(d.date)); })
    .y(function(d) { return y(d.kcore); });
    
    var kcorelist = []
    var avg_total_object = []
    for (var month in data){
        var avg_totals = data[month].avg_totals; 
        var keys = Object.keys(avg_totals);        
        for (var name in avg_totals){
            if(avg_totals.hasOwnProperty(name)){
                if(!(name in avg_total_object))
                    avg_total_object[name] = [];
                avg_total_object[name].push({"id": name, "stats": data[month].stats, "date":data[month].date, "total": avg_totals[name]}); 
            }
        };
        data[month].kcore = +data[month].kcore
        kcorelist.push({"date":data[month].date,"kcore":data[month].kcore});
    }

  var avgdata_list = Object.keys(avg_total_object).map(function(k) { return {"id": k, "date":data[month].date, "values":avg_total_object[k] };});  
  x.domain([
  d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return parseTime(d.date); });}),
  d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return parseTime(d.date); });})
  ]);
  
  y.domain([
  d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return d.total; });}),
  d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return d.total; });})
  ]);
  
  for(var i = 0; i < keys.length; i++){
    mykeys.push(String(keys[i]));
  }
  color = d3.scaleOrdinal() // D3 Version 4
  .domain(mykeys)
  .range(['#a6cee3','#1f78b4','#b2df8a','#33a02c']);
     
    var meta = chartg.selectAll('.meta')
    .data(avgdata_list)
    .enter().append("g")
    .attr("class","meta");
   
    meta.append("path")
    .attr("class","line")
    .attr("clip-path", "url(#clip)")
    .attr("id",function(d){return d.id;})
    .attr("d",function(d){return line(d.values);})
    .style("stroke", function(d) { return color(d.id); });

    var linepath = chartg.append("path")
    .datum(kcorelist)
    .attr("class","mypath")
    .attr("clip-path", "url(#clip)")
    .attr("d",kcoreline)
    .style("stroke","black")
    .style("stroke-width",2.5);
   
  var clip = chartg.append("clipPath")
    .attr("id", "clip");
  var clipRect = clip.append("rect")
    .attr("width", 0)
    .attr("height", 400);
  var totalLength = chartwidth;
  
  clipRect.transition()
    .duration(5000)
    .ease(d3.easeLinear)
    .attr("width", totalLength)
 
   chartg.selectAll(".dots")
    .data(avgdata_list)
    .enter().append("g")
    .attr("class", "dots")
    .selectAll("circle")
    .data(function(d) {return d.values; })
      .enter().append("circle")
      .attr("class",function(d){return "mydot" + d.id;})
      .style("fill", function(d) { return color(d.id); })
      .attr("id",function(d,i) { return "dot"+ d.id + "-" + (i);})
      .attr("r", 4)
      .attr("clip-path","url(#clip)")
      .attr("cx", function(d) {return x(parseTime(d.date)); } )
      .attr("cy", function(d) {return y(d.total); } )
       .on("mouseover", function(d) {
            var html_content = "";
            for(var meta in d.stats){
                if(meta == d.id){ //If this holds the interactions of this particular type
                    for(var statistic in d.stats[meta]){
                        if(d.stats[meta][statistic].length > 0)
                            html_content += prettyKeys[statistic] + ": " + d.stats[meta][statistic].length + "<br/>";
                    }
                }
            }
            d3.select(this).attr("r",8);
            div.transition()		
                .duration(200)		
                .style("opacity", .9);		
            div	.html(html_content)	
                .style("left", (d3.event.pageX) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })					
        .on("mouseout", function(d) {	
            d3.select(this).attr("r",4);
            div.transition()		
                .duration(500)		
                .style("opacity", 0);	
        });
      
  

 
  chartg.append("g")
      .attr("transform", "translate(0," + chartheight + ")")
      .attr("class","axis")
      .call(d3.axisBottom(x).ticks(numticks).tickFormat(formatDate));

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
    });
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