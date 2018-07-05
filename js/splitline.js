function plotsplitline(user){

    var charts = d3.selectAll(".commonchart"),
        margin = {top: 5, right: 50, bottom: 20, left: 50},
        chartwidth = +charts.attr("width") - margin.left - margin.right,
        chartheight = +charts.attr("height") - margin.top - margin.bottom,
        chartg = charts.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var xScale = d3.scaleLinear()
    .domain([0,chartwidth]).range([0,chartwidth]);
var yScale = d3.scaleLinear()
    .domain([0,chartheight]).range([0,chartheight]);
    var titles = d3.selectAll(".commonchart-title");

    var parseTime = d3.timeParse("%d/%m/%y");
    var parseMonthAxis = d3.timeFormat("%Y-%m");

    var x = d3.scaleTime()
        .rangeRound([0, chartwidth]);
    var y = d3.scaleLinear()
        .rangeRound([chartheight, 0]);
    var z = d3.scaleOrdinal(d3.schemeCategory10);


    var line = d3.line()
        .curve(d3.curveMonotoneX)
        .x(function(d) { return x(parseTime(d.date)); })
        .y(function(d) { return y(d.total); });

    var kcoreline = d3.line()
        .curve(d3.curveMonotoneX)
        .x(function(d) { return x(parseTime(d.date)); })
        .y(function(d) { return y(d.kcore); });
        var lists_of_metas = {}
        var kcorelist = []
        var storylist = []
        var discussionlist = []
        var friendshiplist = []
        var transactionlist = []
     //   lists_of_metas["kcore"] = []
        for (var month in data){
            var avg_totals = data[month].avg_totals; 
            var keys = Object.keys(avg_totals);
            for (var name in avg_totals){
                if(avg_totals.hasOwnProperty(name)){
                    if(!(name in lists_of_metas))
                        lists_of_metas[name] = [];
                    lists_of_metas[name].push({"id": name, "date":data[month].date, "stats":data[month].stats, "total": avg_totals[name]}); 
                }
            };
            data[month].kcore = +data[month].kcore
            
      //      lists_of_metas["kcore"].push({"id": "kcore", "date":data[month].date,"total":data[month].kcore});
        }

      var avgdata_list = Object.keys(lists_of_metas).map(function(k) { return {"id": k, "values":lists_of_metas[k] };});  

      x.domain([
      d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return parseTime(d.date); });}),
      d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return parseTime(d.date); });})
      ]);
      
      y.domain([
      d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return d.total; });}),
      d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return d.total; });})
      ]);
      

      //Animation code from https://stackoverflow.com/questions/47986520/how-to-synchronize-animation-of-path-and-area
      var linepath = chartg.append("path")
        .data(avgdata_list)
        .attr("class","mypath")
       // .attr("clip-path", "url(#clip)")
        .attr("d",function(d){return line(d.values);})
        .style("stroke", function(d) { return color(d.id); });

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

      /*
      var clip = chartg.append("clipPath")
        .attr("id", "clip");
      var clipRect = clip.append("rect")
        .attr("width", 0)
        .attr("height", 150);
      var totalLength = chartwidth;
      
      clipRect.transition()
        .duration(5000)
        .ease(d3.easeLinear)
        .attr("width", totalLength)
     */
      chartg.append("g")
          .attr("transform", "translate(0," + chartheight + ")")
          .attr("class","axis")
          .call(d3.axisBottom(x).tickFormat(monthLetter))
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