//Much code taken from https://www.visualcinnamon.com/2015/09/placing-text-on-arcs.html
var chart = d3.select("#donut");
chartg = chart.append("g");
var donut_defined = false;
var pie = d3.pie()
	.startAngle(-90 * Math.PI / 180)
	.endAngle(-90 * Math.PI / 180 + 2 * Math.PI)
	.sort(null)
	.value(function (d) {
		return d[1];
	})
;

var arc = d3.arc()
	.outerRadius(90)
	.innerRadius(70);
var arcs = chartg.selectAll(".arc");
var donut_labels = chartg.selectAll(".donutText");
var kcoretext = chartg.append("text")
	.style("font-size", "70")
	.style("font-family", "'Dosis', sans-serif");

function plotdonut(mydata) {

	$("#donut").bind("wheel mousewheel", function (e) {
		e.preventDefault()
	});

	var width = 240,
	height = 240;
	radius = Math.min(width, height) / 2;

	var edgetotals = mydata.edgetotals;
	var edgekeys = Object.keys(edgetotals);
	var piesegments = [];
	for (var i = 0; i < edgekeys.length; i++) {
		piesegments.push([edgekeys[i], edgetotals[edgekeys[i]]]);
	}
	kcoretext.text(mydata.kcore)
	.style("opacity", 0)
	.transition().duration(400)
	.style("opacity", "1");
	var element = kcoretext.node();
	var elementwidth = element.getBoundingClientRect().width;
	var elementheight = element.getBoundingClientRect().height;
	kcoretext.attr("transform", "translate(" + ((width / 2) - (elementwidth / 2)) + "," + ((height / 2) + (elementheight / 4)) + ")");
	arcs = arcs.data(pie(piesegments));
	if (donut_defined == true) {

		arcs.transition().duration(400).attrTween("d", arcTween)
		.on("end", function (d, i) {
			this._current = d;
			var firstArcSection = /(^.+?)L/;
			var wholeArcSection = /[^A]*A[^A]*/;

			console.log(d3.select(this).attr("d"));
			var regex = firstArcSection.exec(d3.select(this).attr("d"));
			var newArc;
			if (regex == null) {
				regex = wholeArcSection.exec(d3.select(this).attr("d"));
				newArc = regex[0];
				console.log(newArc);
			} else
				newArc = regex[1];
			newArc = newArc.replace(/,/g, " ");
			var end = (d.endAngle / (Math.PI / 180));
			var start = (d.startAngle / (Math.PI / 180));
			if (d.endAngle > 90 * Math.PI / 180 && start > (180 - end) && (end - start) % 360 != 0) {
				var startLoc = /M(.*?)A/;
				var middleLoc,endLoc;

				if ((end - start) < 180) {
					middleLoc = /A(.*?)0 0 1/;
					endLoc = /0 0 1 (.*?)$/;
				} else {
					middleLoc = /A(.*?)0 1 1/;
					endLoc = /0 1 1 (.*?)$/;
				}
				var newStart = endLoc.exec(newArc)[1];
				var newEnd = startLoc.exec(newArc)[1];
				var middleSec = middleLoc.exec(newArc)[1];

				if ((end - start) < 180)
					numbers = "0 0 0 ";
				else
					numbers = "0 1 0 ";
				newArc = "M" + newStart + "A" + middleSec + numbers + newEnd;
			} 

			d3.select("#donutArc" + i)
			.attr("d", newArc)
			.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
			.style("fill", "none");
		});
	} else {
		arcs = arcs.enter().append("path")
			.attr("id", function (d, i) {
				return "monthArc_" + i;
			}) //Unique id for each slice
			.attr("class", "arc")
			.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
			.attr("d", arc)
			.each(function (d, i) {
				this._current = d;
				var firstArcSection = /(^.+?)L/;
				var wholeArcSection = /[^A]*A[^A]*/;

				var regex = firstArcSection.exec(d3.select(this).attr("d"));
				var newArc;
				if (regex == null) {
					regex = wholeArcSection.exec(d3.select(this).attr("d"));
					newArc = regex[0];
				} else
					newArc = regex[1];
				newArc = newArc.replace(/,/g, " ");
				var end = (d.endAngle / (Math.PI / 180));
				var start = (d.startAngle / (Math.PI / 180));

				if (d.endAngle > 90 * Math.PI / 180 && start > (180 - end) && (end - start) % 360 != 0) {

                    var startLoc = /M(.*?)A/;
					var middleLoc, endLoc;
					if ((end - start) < 180) {
						middleLoc = /A(.*?)0 0 1/;
						endLoc = /0 0 1 (.*?)$/;
					} else {
						middleLoc = /A(.*?)0 1 1/;
						endLoc = /0 1 1 (.*?)$/;
					}

					var newStart = endLoc.exec(newArc)[1];
					var newEnd = startLoc.exec(newArc)[1];
					var middleSec = middleLoc.exec(newArc)[1];
					var numbers;
					if ((end - start) < 180)
						numbers = "0 0 0 ";
					else
						numbers = "0 1 0 ";
					newArc = "M" + newStart + "A" + middleSec + numbers + newEnd;
				} 

				chartg.append("path")
				.attr("class", "hiddenDonutArcs")
				.attr("id", "donutArc" + i)
				.attr("d", newArc)
				.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")

				.style("fill", "none");
			})
			.style("fill", function (d) {
				return color(d.data[0]);
			});

		donut_defined = true;

	}

	donut_labels = donut_labels.data(pie(piesegments));
	console.log(donut_labels);
	donut_labels.exit().remove();
	donut_labels = donut_labels
		.enter().append("text")
		.merge(donut_labels)
		.attr("class", "donutText")
		.attr("dy", function (d, i) {
			var degreeEnd = (d.endAngle / (Math.PI / 180));
			var degreeStart = (d.startAngle / (Math.PI / 180));
			return (d.endAngle > 90 * Math.PI / 180 && degreeStart > (180 - degreeEnd) && ((degreeEnd - degreeStart) % 360 != 0) ? 18 : -11);
		});
	d3.selectAll(".textypath").remove();
	donut_labels.append("textPath")
	.attr("class", "textypath")
	.attr("startOffset", "50%")
	.style("text-anchor", "middle")
	.attr("xlink:href", function (d, i) {
		return "#donutArc" + i;
	})

	.text(function (d) {
		if (d.data[1] > 0)
			return d.data[0];
		return "";
	})
        .on("mouseover", function(d) {
        d3.select(this).style("cursor", "pointer"); 
        d3.select(this).style("fill", "#E7472E"); 
      })    
      .on("mouseout",function(d){
         d3.select(this).style("fill",color(d.data[0]));          
      }) 
	.style("font-size", "18px")
	.style("fill", function (d) {
		return color(d.data[0]);
	})
	.style("font-weight", "bold"); ;

	function arcTween(a) {
		var i = d3.interpolate(this._current, a);
		this._current = i(0);
		return function (t) {
			return arc(i(t));
		};
	}
}
