function plotsplitarea(user){

    var charts = d3.selectAll(".splitareachart").on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		}),
    margin = {top: 5, right: 50, bottom: 20, left: 40},
    chartwidth = +charts.attr("width") - margin.left - margin.right,
    chartheight = +charts.attr("height") - margin.top - margin.bottom,
    chartg = charts.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var titles = d3.selectAll(".splitarea-title");

var x = d3.scaleTime()
    .rangeRound([0, chartwidth*3]);
var y = d3.scaleLinear()
    .rangeRound([chartheight,0]);
var z = d3.scaleOrdinal(d3.schemeCategory10);

var zoom = d3.zoom()
.scaleExtent([0.33,1])
.translateExtent([[0,0],[charts.attr('width')*3+50,charts.attr("height")]])
.on('zoom',zoomed);

$(".splitareachart").bind("wheel mousewheel", function(e) {e.preventDefault()});
var currentMonthGap = 2;

function zoomed() {
    var xz = d3.event.transform.rescaleX(x);
    gX.call(xAxis.scale(xz));
     var selection = $(".splitareaaxis > .tick");
    var tickdistance = selection.eq(1).position().left - selection.eq(0).position().left;
  
    if(tickdistance < 50)
        currentMonthGap++;
    else if(tickdistance > 100)
        currentMonthGap--;
    xAxis.ticks(d3.timeMonth.every(Math.max(1,currentMonthGap)));
          d3.selectAll(".splitareaaxis > .tick").attr("transform",function(){return "translate("+ (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";});

    area.x(function(d) { return xz(d.date)+20; })    
    linepath.attr("d", function(d) { return area(d.values);});
    dots.attr("cx", function(d) {return xz(d.date)+20; } )
}
var area = d3.area()
    .x(function(d) {return x(d.date)+20; })
    .y1(function(d) {return y(d.total); })


    var lists_of_metas = {}
    var kcorelist = []
    var storylist = []
    var discussionlist = []
    var friendshiplist = []
    var transactionlist = []
 //   lists_of_metas["kcore"] = []
    for (var month in data){    
        var cumu_totals = node_data[month].cumu_totals;    
        for (var name in cumu_totals){
            if(cumu_totals.hasOwnProperty(name)){
                if(!(name in lists_of_metas))
                    lists_of_metas[name] = [];
                 if(month != 0){
                              var monthsWithZero = d3.timeMonth.count(node_data[month-1].date,node_data[month].date) -1;
                              for(var i = 0; i < monthsWithZero; i++){
                                lists_of_metas[name].push({"id": name, "stats": {}, "date":d3.timeMonth.offset(node_data[month-1].date,i+1), "total": 0}); 
                              }
                        } 
                lists_of_metas[name].push({"id": name, "date":node_data[month].date, "stats":node_data[month].stats, "total": cumu_totals[name]}); 
            }
        };
        node_data[month].kcore = +node_data[month].kcore
        
    }
 
  var avgdata_list = Object.keys(lists_of_metas).map(function(k) { return {"id": k, "values":lists_of_metas[k] };});  
  console.log("AVGDATLIST");
  console.log(avgdata_list);
  x.domain([
  d3.min(avgdata_list,function(c) {return d3.min(c.values, function(d) {return d.date; });}),
  d3.max(avgdata_list,function(c) { return d3.max(c.values, function(d) {return d.date; });})
  ]);
    //So that single ticks are positioned in the center of the axis
    if (x.domain()[0].getTime() == x.domain()[1].getTime()) {
    var dateLess = d3.timeMonth.offset(x.domain()[0], -1);
    var dateMore = d3.timeMonth.offset(x.domain()[0], 1);
    x.domain([dateLess, dateMore])
}
  y.domain([
  0,
  d3.max(avgdata_list,function(c) {if(c.id == 'date' || c.id == 'stats')return 0; return d3.max(c.values, function(d) {return d.total; });})
  ]);
    area.y0(y(0));
  //  kcoreline.y0(y(0));
  z.domain(avgdata_list.map(function(c) { return c.id; }));
  

  //Animation code from https://stackoverflow.com/questions/47986520/how-to-synchronize-animation-of-path-and-area
  var linepath = chartg.append("path")
    .data(avgdata_list)
    .attr("class", "area")
    .attr("clip-path", "url(#clip)")
    .attr("d",function(d){return area(d.values);})
    .style("fill", function(d) { return color(d.id); });

    titles.data(avgdata_list)
    .each(function(d){d3.select(this).node().innerHTML = d.id;
                      d3.select(this).node().style.color = color(d.id);});
  //  .style('fill',function(d){return z(d.id);});
    
   var dots = chartg.append("g")
    .data(avgdata_list)
    .attr("class", "dots")
    .selectAll("circle")
    .data(function(d,i) {return d.values; })
      .enter().append("circle")
      .attr("class","mydot")
      .style("fill", function(d) { return color(d.id); })
      .attr("id",function(d,i) { return "dot"+ d.total + "-" + (i);})
      .attr("r", 3)
      .attr("clip-path","url(#clip)")
      .attr("cx", function(d) {return x(d.date)+20; } )
      .attr("cy", function(d) {return y(d.total); } )
 		.on("mouseover", function (d) {
			d3.select(this).attr("r", 8);
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
			d3.select(this).attr("r", 4);
		})
		.on("click", function (d, i) {
			drawTooltipGraph(d.date, d.id);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		});

      var clip = charts.append("clipPath")
        .attr("id", "clip");
      var clipRect = clip.append("rect")
        .attr("width", charts.attr("width"))
        .attr("height", chartheight);
        
    var xAxis = d3.axisBottom(x).tickFormat(anotherFormat).ticks(d3.timeMonth.every(2));
     var gX = chartg.append("g")
      .attr("transform", "translate(0," + chartheight + ")")
      .attr("class","axis splitareaaxis")
      .call(xAxis);
          d3.selectAll(".splitareaaxis > .tick").attr("transform",function(){return "translate("+ (getTranslation(d3.select(this).attr("transform"))[0] + 20) + ",0)";});

  charts.call(zoom);
  
  chartg.append("g")
      .attr("class","axis")
      .call(d3.axisLeft(y).ticks(3));

}
