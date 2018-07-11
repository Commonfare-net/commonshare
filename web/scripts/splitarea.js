function plotsplitarea(user){

    var charts = d3.selectAll(".splitareachart"),
    margin = {top: 5, right: 50, bottom: 20, left: 50},
    chartwidth = +charts.attr("width") - margin.left - margin.right,
    chartheight = +charts.attr("height") - margin.top - margin.bottom,
    chartg = charts.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var titles = d3.selectAll(".splitarea-title");
var xScale = d3.scaleLinear()
    .domain([0,chartwidth]).range([0,chartwidth]);
var yScale = d3.scaleLinear()
    .domain([0,chartheight]).range([0,chartheight]);
var x = d3.scaleTime()
    .rangeRound([0, chartwidth]);
var y = d3.scaleLinear()
    .rangeRound([chartheight,0]);
var z = d3.scaleOrdinal(d3.schemeCategory10);


var area = d3.area()
    .x(function(d) {return x(parseTime(d.date)); })
    .y1(function(d) {return y(d.total); })


var kcoreline = d3.area()
    .x(function(d) {return x(parseTime(d.date)); })
    .y1(function(d) {return y(d.kcore); })
    var lists_of_metas = {}
    var kcorelist = []
    var storylist = []
    var discussionlist = []
    var friendshiplist = []
    var transactionlist = []
 //   lists_of_metas["kcore"] = []
    for (var month in data){
        var cumu_totals = data[month].cumu_totals;    
        for (var name in cumu_totals){
            if(cumu_totals.hasOwnProperty(name)){
                if(!(name in lists_of_metas))
                    lists_of_metas[name] = [];
                lists_of_metas[name].push({"id": name, "date":data[month].date, "stats":data[month].stats, "total": cumu_totals[name]}); 
            }
        };
        data[month].kcore = +data[month].kcore
        
   //     lists_of_metas["kcore"].push({"id": "kcore", "date":data[month].date,"total":data[month].kcore});
    }
 
  var avgdata_list = Object.keys(lists_of_metas).map(function(k) { return {"id": k, "values":lists_of_metas[k] };});  
    
  x.domain([
  d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return parseTime(d.date); });}),
  d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return parseTime(d.date); });})
  ]);
  
  y.domain([
  0,
  d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return d.total; });})
  ]);
    area.y0(y(0));
    kcoreline.y0(y(0));
  z.domain(avgdata_list.map(function(c) { return c.id; }));
  

  //Animation code from https://stackoverflow.com/questions/47986520/how-to-synchronize-animation-of-path-and-area
  var linepath = chartg.append("path")
    .data(avgdata_list)
    .attr("class", "area")
   // .attr("clip-path", "url(#clip)")
    .attr("d",function(d){return area(d.values);})
    .style("fill", function(d) { return color(d.id); });

    titles.data(avgdata_list)
    .each(function(d){d3.select(this).node().innerHTML = d.id;
                      d3.select(this).node().style.color = color(d.id);});
  //  .style('fill',function(d){return z(d.id);});
    
     chartg.append("g")
    .data(avgdata_list)
    .attr("class", "dots")
    .selectAll("circle")
    .data(function(d,i) {return d.values; })
      .enter().append("circle")
      .attr("class","mydot")
      .style("fill", function(d) { return color(d.id); })
      .attr("id",function(d,i) { return "dot"+ d.total + "-" + (i);})
      .attr("r", 3)
     // .attr("clip-path","url(#clip)")
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
       }) 
      ; 

  chartg.append("g")
      .attr("transform", "translate(0," + chartheight + ")")
      .attr("class","axis")
      .call(d3.axisBottom(x).ticks(numticks).tickFormat(monthLetter))
      .selectAll("text")	
       // .style("text-anchor", "end")
        .attr("dy", "0.71em");
        //.attr("transform", "rotate(-65)");;


  chartg.append("g")
      .attr("class","axis")
      .call(d3.axisLeft(y).ticks(3))
      .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("Commonshare");

}