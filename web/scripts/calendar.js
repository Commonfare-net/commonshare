function pathMonth(t0) {
  var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
      d0 = t0.getDay(), 
      w0 = d3.timeWeek.count(d3.timeYear(t0), t0) - d3.timeWeek.count(d3.timeYear(t0), startYear) 
      + ((d3.timeMonth.count(d3.timeYear(t0), t0)-d3.timeMonth.count(d3.timeYear(t0),startYear)) * 40)/cellSize,
      d1 = t1.getDay(), 
      w1 = d3.timeWeek.count(d3.timeYear(t1), t1) - d3.timeWeek.count(d3.timeYear(t1), startYear)
      + ((d3.timeMonth.count(d3.timeYear(t1), t1)-d3.timeMonth.count(d3.timeYear(t1),startYear)) * 40)/cellSize;
  return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
      + "H" + w0 * cellSize + "V" + 7 * cellSize
      + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
      + "H" + (w1 + 1) * cellSize + "V" + 0
      + "H" + (w0 + 1) * cellSize + "Z";
}
function calendarsummer(total, num) {
    return total + num[1];
}
function sumStats(stats){
    var sumStats = {};
    for (var k in stats){
        sumStats[k] = Object.values(stats[k]).reduce(calendarsummer,0);
    }
    return sumStats;
}
    var startYear;
    var cellSize = 28;

function plotcalendars(user){

    var chart = d3.select("#calendarchart"),
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
//chart.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(0.3));

//Zooming function
function zoomFunction(){
    var new_xScale = d3.event.transform.rescaleX(xScale)
    var new_yScale = d3.event.transform.rescaleY(yScale)
    chartg.attr("transform", d3.event.transform)
};
    var formatDay = d3.timeFormat("%w"), // day of the week
        formatWeek = d3.timeFormat("%U"), // week number of the year
        formatMonth = d3.timeFormat("%m"), // month number
        formatMonthName = d3.timeFormat("%B"),
        formatYear = d3.timeFormat("%Y"),
        formatDayOfMonth = d3.timeFormat("%d"),
        formatMyFormat = d3.timeFormat("%Y/%m/%d");
    var formatAbbMonth = d3.timeFormat("%b");

  var monthdates = [];
  var keys = [];
    for (var month in data){
        var cumu_totals = data[month].cumu_totals;
        keys = Object.keys(cumu_totals);
        monthdates.push(data[month].date);
    }        
    startYear = parseTime(monthdates[0]);
    //Set up colour range (darker green means higher value to actions)
    var buckets = 7,
    greens = ['#f3a396','#f09081','#ee7e6c','#eb6b57','#e95942','#e7472e','#cf3f29'];


    
    var calendar = chartg.selectAll(".calendar")
        .data(data) 
        .enter().append("g")
        .attr("class","calendar");
    
    var monthname = calendar
            .append("text")
            .style("font-size",24)
            .text(function(d){return formatAbbMonth(parseTime(d.date));})
            .attr("x", function(d) {
            
            return (d3.timeWeek.count(d3.timeYear(parseTime(d.date)), parseTime(d.date))-d3.timeWeek.count(d3.timeYear(parseTime(d.date)),startYear)) * cellSize + ((d3.timeMonth.count(d3.timeYear(parseTime(d.date)), parseTime(d.date))-d3.timeMonth.count(d3.timeYear(parseTime(d.date)),startYear)) * 40)
            })
            .attr("y",220);
    

      
    var rect = calendar.selectAll(".rect")
        .data(function(d){

            var year = +formatYear(parseTime(d.date));
            var month = +formatMonth(parseTime(d.date))-1;
           
            var mapped = d3.timeDays(new Date(year,month,1), new Date(year,month+1,1)).map((val, index, arr) => {   
                if(d.stats == null)
                    return {date: val, stats: {}, sumval: 0};
                else{
                    console.log("val is " + val + " and stats are...");
                    console.log(d.stats[formatMyFormat(val)]);
                    if(formatMyFormat(val) in d.stats)
                        console.log("And sumval is more than 0!");
                    return {
                        date: val, //The original date becomes 'date' in the returned object
                        stats: d.stats[formatMyFormat(val)], //And the interactions for this date in the graphdata are returned as 'stats'
                        sumvals: sumStats(d.stats[formatMyFormat(val)]),
                        sumval: formatMyFormat(val) in d.stats ? 4 : 0
                    };
                    
                }
            });
        return mapped;
            })
        .enter().append("g")
        .attr("class","rect");

    var color = d3.scaleOrdinal() // D3 Version 4
  .domain(keys)
  .range(['#a6cee3','#1f78b4','#b2df8a','#33a02c']);
                  
    rect.append("rect")
        .attr("class", "day")
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("x", function(d) {
            return (d3.timeWeek.count(d3.timeYear(d.date), d.date)-d3.timeWeek.count(d3.timeYear(d.date),startYear)) * cellSize
            + (d3.timeMonth.count(d3.timeYear(d.date), d.date)-d3.timeMonth.count(d3.timeYear(d.date),startYear)) * 40

        })
        .attr("y", function(d) { 
          var week_diff = formatWeek(d.date) - formatWeek(new Date(formatYear(d.date), formatMonth(d.date)-1, 1) );
          return d.date.getDay() * cellSize;
     //     return (week_diff*cellSize);// + cellSize*8 - cellSize/2;
        });
    rect.selectAll(".minirect")
        .data(data,function(d){return d.stats;})
        .enter().append("rect")
        .attr("class","minirect");
        
    rect.append("text") 
        .style("font-size",11)
         .attr("x", function(d) {    
         return (d3.timeWeek.count(d3.timeYear(d.date), d.date) -d3.timeWeek.count(d3.timeYear(d.date),startYear)) * cellSize
         + (d3.timeMonth.count(d3.timeYear(d.date), d.date)-d3.timeMonth.count(d3.timeYear(d.date),startYear)) * 40
         // return 30 + formatDay(d.date) * cellSize + 20; 
        })
        
        .attr("y", function(d) { 
          var week_diff = formatWeek(d.date) - formatWeek(new Date(formatYear(d.date), formatMonth(d.date)-1, 1) );
          return (d.date.getDay()+1) * cellSize - 5;
         // return 15+ (week_diff*cellSize);// + cellSize*8 - cellSize/2;
        })
        .text(function(d){return formatDayOfMonth(d.date);});
        
    rect.filter(function(d) {return d.sumval > 0; })
        .select("rect").style("fill",function(d){
            console.log("Filtered in " + d.date);
            var max = 0;
            var mostinfluential;
            for(var k in d.sumvals){
                if(d.sumvals[k] > max){
                    max = d.sumvals[k];
                    mostinfluential = k;
                }
            }
            console.log("the colour is gonna be " + k);
            return color(k);
            
        })
        .select("title")
            .text(function(d) { return d + ": "; });

    rect.filter(function(d) {return d.sumval > 0; }).on("mouseover", mouseover);
    rect.filter(function(d) {return d.sumval > 0; }).on("mouseout", mouseout);
    function mouseover(d) {
        var html_content = "";
    //   html_content = d.sumvals;

       for(var meta in d.stats){
            for(var statistic in d.stats[meta]){
                   html_content += prettyKeys[statistic] + ": " + d.stats[meta][statistic][0] + "<br/>";
            }
        }        
        
        div.transition()        
            .duration(200)      
            .style("opacity", .9); 
         div.html(html_content)	
            .style("left", (d3.event.pageX) + "px")		
            .style("top", (d3.event.pageY - 28) + "px");     
      }
      
      function mouseout (d) {
        div.transition()        
            .duration(500)      
            .style("opacity", 0);   
      }
      
          chartg.append("g")
    .attr("fill", "none")
    .attr("stroke", "#000")
    .selectAll("path")
    .data(function(d) { return d3.timeMonths(parseTime(monthdates[0]),parseTime(monthdates[monthdates.length-1])); })
    .enter().append("path")
    .attr("d", pathMonth);
    
     var element = chartg.node();
        var elementwidth = element.getBoundingClientRect().width;
        chart.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(chart.attr("width")/elementwidth));
    }