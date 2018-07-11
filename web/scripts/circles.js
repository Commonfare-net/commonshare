
function plotcirclechart(user){

var chart = d3.select("#circlechart"),
    margin = {top: 20, right: 20, bottom: 70, left: 100},
    chartwidth = +chart.attr("width") - margin.left - margin.right,
    chartheight = +chart.attr("height") - margin.top - margin.bottom,
    chartg = chart.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var xScale = d3.scaleLinear()
    .domain([200,200+chartwidth]).range([200,200+chartwidth]);
var yScale = d3.scaleLinear()
    .domain([0,400]).range([0,400]);
var zoom =d3.zoom().on("zoom",zoomFunction);
chart.call(zoom);

//Zooming function
function zoomFunction(){
    var new_xScale = d3.event.transform.rescaleX(xScale)
    var new_yScale = d3.event.transform.rescaleY(yScale)
    chartg.attr("transform", d3.event.transform)
};
function children(d) {
  return d.cumu_array;
}
 function summer(total, num) {
    return isNaN(num) ? total : total + num;
}
  
    var mincore = 9999, maxcore = 0;
    var cumu_total_object = []
    for (var month in data){
        var cumu_totals = data[month].cumu_totals;
        var cumu_array = d3.keys(cumu_totals).map(function(key){return {"name":key,"total":cumu_totals[key],"kcore":data[month].kcore,"stats":data[month].stats};});
        var keys = Object.keys(cumu_totals);
        mincore = data[month].kcore < mincore ? data[month].kcore : mincore;
        maxcore = data[month].kcore > maxcore ? data[month].kcore : maxcore;
        data[month]["overall"] = Object.values(cumu_totals).reduce(summer,0);

        data[month]["cumu_array"] = cumu_array;
        cumu_totals["date"] = data[month].date;
        cumu_totals["stats"] = data[month].stats;
        cumu_total_object.push(cumu_totals);
    
    }
    var months = cumu_total_object.map(function(d) { return d.date; });
    var xdisplacements = [];
    var ydisplacements = [];
    var count = 0;
    var total = 0;
    var maxdiameter = 0;
    for(var month in data){
       xdisplacements[count] = total;
       var diameter = data[month]["cumu_array"][0].kcore * 9 + 50;
       total = total + diameter;
       count++;
       if(diameter > maxdiameter)
          maxdiameter = diameter;
    };
    count = 0;
    for(var month in data){
        var diameter = data[month]["cumu_array"][0].kcore * 9;
        ydisplacements[count] = (maxdiameter/2) - (diameter/2);
        count++;
    }
    var y = d3.scaleOrdinal()
    .domain(months)
    .range(ydisplacements);
    var x = d3.scaleOrdinal()
      .domain(months)
      .range(xdisplacements);
      
var monthname = d3.timeFormat("%b");

//This is silly but because the pack layout size can't be updated dynamically, we have to make one for every circle we're using
var packs = [];
for (var i = 0; i < months.length; i++){
    var size = data[i]["cumu_array"][0].kcore;
    var scaledsize = size*9 + 30;
    packs[i] = d3.pack()
    .size([scaledsize,scaledsize])
    .padding(2);  
     if(data[i]["overall"] == 0) //Even though a node's kcore might be 1, they still might not have contributed any meaningful actions
        packs[i].radius(function(){return 0;});
}
  
  var monthpack = chartg.append("g")
    .selectAll("g")
    .data(data)
    .enter().append("g")
    .selectAll(".node")
    .data(function(d){
            return packs[data.indexOf(d)](d3.hierarchy(d,children)
                    .sum(function(e) { return e.total; })
                    .sort(function(a, b) { return b.value - a.value; }))
                  .descendants();
          })
    .enter().append("g")
      .attr("class", function(d) {return d.children ? "node" : "leaf node"; })
      .attr("transform", function(d) {
      return d.children ? "translate(" + (d.x + x(d.data.date)) + "," + (d.y + y(d.data.date)) + ")" : 
                          "translate(" + (d.x + x(d.parent.data.date)) + "," + (d.y + y(d.parent.data.date)) + ")"; });

    
    monthpack.append("circle")
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) {return d.children ? "blue" : color(d.data.name); })
      .style("opacity",function(d) {return d.children ? 0.3 : 1;})
        .on("mouseover", function(d) { 
        var html_content = "";
       
        for(var meta in d.data.stats){
            if(meta == d.data.name){ //If this holds the interactions of this particular type
                for(var statistic in d.data.stats[meta]){
                    if(d.data.stats[meta][statistic].length > 0)
                        html_content += prettyKeys[statistic] + ": " + d.data.stats[meta][statistic].length + "<br/>";
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
        d3.select(this).style("opacity",function(d){return d.children ? 0.3 : 1;});
        div.transition()		
           .duration(500)		
           .style("opacity", 0);
      });
         monthpack.append("text")
        .attr("dx",function(d){return  -14;})
        .attr("dy", function(d){return d.children ? d.data.kcore*5 + 30 : 0;})
	    .text(function(d){return d.children ? monthname(parseTime(d.data.date)) : "";});
 var element = chartg.node();
        var elementwidth = element.getBoundingClientRect().width;
        chart.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(chart.attr("width")/elementwidth));

      //  chartg.attr("transform", "translate(" + ((800)-(elementwidth/2)) + "," + margin.top + ")");
}