
function plotcirclechart(user,varnodedata,vargraphdata,divid){

    if(varnodedata == null)
        varnodedata = node_data;
    if(vargraphdata == null)
        vargraphdata = graph_data;
    if(divid == null)
        divid = "circlechart";
    var chart = d3.select("#"+divid).on("click", function (d) {
			div
			.style("opacity", 0)
			.style("left", "0px")
			.style("top", "0px");
		}),
        chartg = chart.append("g");

     $("#"+divid).bind("wheel mousewheel", function(e) {e.preventDefault()});
       
    var zoom = d3.zoom()
        .scaleExtent([0.33,2])
        .translateExtent([[0,0],[chart.attr('width'),chart.attr("height")]])
        .on('zoom',zoomed);
    function zoomed() {
        chartg.attr("transform", d3.event.transform);
    }

    function children(d) {
      return d.cumu_array;
    }
     function summer(total, num) {
        return (isNaN(num) || num instanceof Date) ? total : total + num;
    }

    var mincore = 9999, maxcore = 0;
    var cumu_total_object = []
    for (var month in data){
        var cumu_totals = varnodedata[month].cumu_totals;
        var cumu_array = d3.keys(cumu_totals).map(function(key){return {"name":key,"total":cumu_totals[key],"kcore":varnodedata[month].kcore,"stats":varnodedata[month].stats};});
        var keys = Object.keys(cumu_totals);
        mincore = varnodedata[month].kcore < mincore ? varnodedata[month].kcore : mincore;
        maxcore = varnodedata[month].kcore > maxcore ? varnodedata[month].kcore : maxcore;
        cumu_totals["overall"] = Object.values(cumu_totals).reduce(summer,0);
        cumu_totals["kcore"] = varnodedata[month].kcore;
        cumu_totals["cumu_array"] = cumu_array;
        cumu_totals["date"] = varnodedata[month].date;
        cumu_totals["stats"] = varnodedata[month].stats;
         if(month != 0){
              var cumu_array = d3.keys(cumu_totals).map(function(key){return {"name":key,"total":0,"kcore":0,"stats":{}};});
              var monthsWithZero = d3.timeMonth.count(varnodedata[month-1].date,varnodedata[month].date) -1;
              for(var i = 0; i < monthsWithZero; i++){
                  totals = {};
                  for(var j in keys){
                    totals[keys[j]] = 0;
                  }
                  totals['overall'] = 0;
                  totals['cumu_array'] = cumu_array;
                  totals['stats'] = {}
                    console.log(d3.timeMonth.offset(varnodedata[month-1].date,i+1));
                    totals['date'] = d3.timeMonth.offset(varnodedata[month-1].date,i+1);
                    console.log(totals);
                    cumu_total_object.push(totals); 
              }
        } 
        cumu_total_object.push(cumu_totals);
    
    }
  	var color = d3.scaleOrdinal() // D3 Version 4
		.domain(keys)
		.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);
        
    var months = cumu_total_object.map(function(d) { return d.date; });
    var xdisplacements = [];
    var ydisplacements = [];
    var count = 0;
    var total = 0;
    var maxdiameter = 0;
    for(var month in cumu_total_object){
       xdisplacements[count] = total;
       var diameter = cumu_total_object[month]["cumu_array"][0].kcore * 9 + 50;
       total = total + diameter;
       count++;
       if(diameter > maxdiameter)
          maxdiameter = diameter;
    };
    count = 0;
    for(var month in cumu_total_object){
        var diameter = cumu_total_object[month]["cumu_array"][0].kcore * 9;
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
    console.log(cumu_total_object);
    for (var i = 0; i < months.length; i++){
        var size = cumu_total_object[i]["cumu_array"][0].kcore;
        var scaledsize = size*9 + 30;
        packs[i] = d3.pack()
        .size([scaledsize,scaledsize])
        .padding(2);  
         if(cumu_total_object[i]["overall"] == 0) //Even though a node's kcore might be 1, they still might not have contributed any meaningful actions
            packs[i].radius(function(){return 0;});
    }
      
  var monthpack = chartg.append("g")
    .selectAll("g")
    .data(cumu_total_object)
    .enter().append("g")
    .selectAll(".node")
    .data(function(d){
            return packs[cumu_total_object.indexOf(d)](d3.hierarchy(d,children)
                    .sum(function(e) {console.log(e);if(e.name == "date" || e.name == "stats")return 0; return e.total; })
                    .sort(function(a, b) {console.log(a);console.log(b);return b.value - a.value; }))
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
		.on("mouseover", function (d) {
			d3.select(this).style("cursor", "pointer");
		})
		.on("mouseout", function (d) {
		})
		.on("click", function (d, i) {
			drawTooltipGraph(d.parent.data.date, d.data.name,null,vargraphdata);

			div
			.transition()
			.duration(200)
			.style("opacity", .9)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		})
      
    monthpack.append("text")
        .attr("dx",function(d){return  -14;})
        .attr("dy", function(d){return d.children && d.data.kcore != null ? d.data.kcore*5 + 30 : 0;})
	    .text(function(d){return d.children ? monthname(d.data.date) : "";});
    
    var element = chartg.node();
    var elementwidth = element.getBoundingClientRect().width;
    var elementheight = element.getBoundingClientRect().height;
    zoom.translateExtent([[0,0],[elementwidth,elementheight]])
    zoom.scaleBy(chartg,1);
    chart.call(zoom);

}