function filter(tagname, button) {
    filtertype = "tag";
	tag = tagname;

	var buttons = document.getElementsByTagName("button");
	for (var i = 0; i < buttons.length; i++) {
		var currentbutton = buttons[i];
		currentbutton.style.background = '#fff';
		currentbutton.style.color = '#37474f';
	}
    draw();
	button.style.color = "#fff";
	button.style.borderColor = "#37474f";
	button.style.background = "#37474f";
}
var tagvalue = "all";
var networkvalue = "all";
var currentfilter = "";

//Functions for filtering based on tag/network type buttons
function nwfilter(nwname) {
    filtertype = "network";
    tag = nwname;
    
    draw();
}

var linksliderhandle;
var sliderhandle;
//New date slider code (adapted from https://bl.ocks.org/mbostock/6452972)

function updateStrengthSlider(currentpos, maxval) {
	var strengthsliderslider = document.getElementById("strengthslider");
	var strengthslidersvg = d3.select(".strengthslider");
	margin = {
		right: 50,
		left: 50,
		top: 100,
		bottom: 50
	},
	height = +strengthslidersvg.attr("height");
	var sliderwidth = parseFloat(window.getComputedStyle(strengthsliderslider).width) - margin.left - margin.right;
	var slidex = d3.scaleLinear()
		.domain([0, maxval])
		.range([0, sliderwidth])
		.clamp(true);

	var ticks = d3.select(".strengthslider").select(".ticks").selectAll(".ticktext");
	ticks = ticks.data(slidex.ticks(maxval*10));

	ticks.exit().remove();

	ticks = ticks
		.enter().append("g")
		.attr("class", "ticktext")
		.attr("id", function (d, i) {
			return "tick" + i;
		})
		.merge(ticks)
		.attr("transform", function (d, i) {
			return "translate(" + slidex((i*1.0)/10.0) + ",0)";
		});

	ticks.append("text")
	.text(function (d, i) {
		if (i % 10 != 0)
			return "";
		return i/10.0;
	})
	.attr("class", "tickz")
	.style("text-anchor", "end");

	var strengthsliderhandle = strengthslidersvg.select(".handle")
		.call(d3.drag()
			.on("drag", function () {
				var linkstrength = Math.round( slidex.invert(d3.event.x) * 10) / 10; //Round to 1dp! Math.round(slidex.invert(d3.event.x));
				if (linkstrength != strengthslider) {
					strengthslider = linkstrength;
					d3.select("#strength").text(strengthslider);
                    draw();
				}
				strengthsliderhandle.attr("cx", slidex(slidex.invert(d3.event.x)));
			}));
	strengthsliderhandle.attr("cx", slidex(Math.min(currentpos, maxval)));
}

function addStrengthSlider() {
	var strengthsliderslider = document.getElementById("strengthslider");
	var strengthslidersvg = d3.select(".strengthslider");
	margin = {
		right: 50,
		left: 50,
		top: 100,
		bottom: 50
	},
	height = +strengthslidersvg.attr("height");
	var sliderwidth = parseFloat(window.getComputedStyle(strengthsliderslider).width) - margin.left - margin.right;
	var slidex = d3.scaleLinear()
		.domain([0, 10])
		.range([0, sliderwidth])
		.clamp(true);

	var slider = strengthslidersvg.append("g")
		.attr("class", "slider")
		.attr("transform", "translate(" + margin.left + "," + height / 2 + ")");

	slider.append("line")
	.attr("class", "track")
	.attr("x1", slidex.range()[0])
	.attr("x2", slidex.range()[1])
	.select(function () {
		return this.parentNode.appendChild(this.cloneNode(true));
	})
	.attr("class", "track-inset")
	.select(function () {
		return this.parentNode.appendChild(this.cloneNode(true));
	})
	.attr("class", "track-overlay");

	var ticks = slider.insert("g", ".track-overlay")
		.attr("class", "ticks")
		.attr("transform", "translate(0,25)");

	var ticktext = ticks.selectAll(".ticktext")
		.data(slidex.ticks(10))
		.enter().append("g")
		.attr("class", "ticktext")
		.attr("id", function (d, i) {
			return "tick" + i;
		})
		.attr("transform", function (d, i) {
			return "translate(" + slidex(i) + ",0)";
		});
/*
	ticktext.append("text")
	.text(function (d, i) {
		if (i % 2 == 1)
			return "";
		return i;
	})
	.attr("class", "tickz")
	.style("text-anchor", "end");
*/
	var strengthsliderhandle = slider.append("circle")
		.attr("class", "handle")
		.attr("r", 9)
		.call(d3.drag()
			.on("drag", function () {
				var linkstrength = Math.round(slidex.invert(d3.event.x));
				if (linkstrength != strengthslider) {
					//strengthsliderpos = linkstrength;
					strengthslider = linkstrength;
					d3.select("#strength").text(strengthslider);
                    draw();
				}
				strengthsliderhandle.attr("cx", slidex(slidex.invert(d3.event.x)));
			}));
}
var currentDate;
var dateslidex;
function addDateSlider() {
	slideradded = true;
	var s = document.getElementById("myslider");

	var slidesvg = d3.select(".myslider"),
	margin = {
		right: 50,
		left: 50,
		top: 100,
		bottom: 50
	},
	height = +slidesvg.attr("height");
	var sliderwidth = parseFloat(window.getComputedStyle(s).width) - margin.left - margin.right;
	dateslidex = d3.scaleLinear()
		.domain([0, datalist.length-1])
		.range([0, sliderwidth])
		.clamp(true);

	dateslider = slidesvg.append("g")
		.attr("class", "slider")
		.attr("transform", "translate(" + margin.left + "," + height / 2 + ")");

	dateslider.append("line")
	.attr("class", "track")
	.attr("x1", dateslidex.range()[0])
	.attr("x2", dateslidex.range()[1])
	.select(function () {
		return this.parentNode.appendChild(this.cloneNode(true));
	})
	.attr("class", "track-inset")
	.select(function () {
		return this.parentNode.appendChild(this.cloneNode(true));
	})
	.attr("class", "track-overlay");

	var ticks = dateslider.insert("g", ".track-overlay")
		.attr("class", "ticks")
		.attr("transform", "translate(0,25)");

	var ticktext = ticks.selectAll(".ticktext")
		.data(dateslidex.ticks(6))
		.enter().append("g")
		.attr("class", "ticktext")
		.attr("id", function (d) {
			return "tick" + d;
		})
		.attr("transform", function (d, i) {
			return "translate(" + dateslidex((i*datalist.length)/5) + ",0)";
		});

	ticktext.append("text")
	.text(function (d, i) {
        if(i == 0)
            return formatWeek(parseTime(datalist[0].date));
        else{
            index = Math.round((datalist.length) * (i/5.0));
            if(i > 5)
                return "";
            return formatWeek(parseTime(datalist[index-1].date));
        }
    })
	.attr("class", "tickz")
	.style("text-anchor", "middle");
    $("#curdate").text(formatWeek(parseTime(datalist[0].date)) + " to " + formatWeek(d3.utcDay.offset(parseTime(datalist[0].date),14)));
    currentDate = datalist[ Object.keys(data).length-2].date;
	sliderhandle = dateslider.append("circle")
		.attr("class", "handle")
		.attr("r", 9)
		.call(d3.drag()
			.on("drag", function () {
				var selected_date = Math.round(dateslidex.invert(d3.event.x));
				var actual_date = Object.keys(data).length - selected_date - 1;
                if (actual_date != indexstart) {
					//sliderpos = selected_date;
                   
					indexstart = actual_date;
                     currentDate = datalist[selected_date].date;
                    $("#curdate").text(formatWeek(d3.utcDay.offset(parseTime(datalist[selected_date].date),-14)) + " to " + formatWeek(parseTime(datalist[selected_date].date))  );
                    draw();
				}
				sliderhandle.attr("cx", dateslidex(dateslidex.invert(d3.event.x)));
			}));
}
