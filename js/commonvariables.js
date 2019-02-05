var datafilecounter = 1;
var drawn = {};

var keys = ['social', 'story', 'transaction', 'listing'];
var color = d3.scaleOrdinal() // D3 Version 4
	.domain(keys)
	.range(['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c']);
var mykeys = [];
var prettyKeys = {
	"create_story": "Wrote story ",
	"create_listing": "Created listing ",
	"conversation": "Started conversation with "
};
var formatDate = d3.timeFormat("%Y/%m/%d");
var parseTime = d3.timeParse("%Y/%m/%d");
var tickf = d3.timeFormat("%b'%y");
var urlParams = new URLSearchParams(window.location.search);
var userid = urlParams.get('userid'); // "edit"
var lang = urlParams.get('lang');
var tooltipFormat = d3.timeFormat("%b %d");

var data = {};
var node_data = [];
var graph_data = {};
var numticks = 0;

//Tooltip functions from http://www.d3noob.org/2013/01/adding-tooltips-to-d3js-graph.html
var div = d3.select("body").append("div")
	.attr("class", "tooltip").style("width", "150px").style("height", "150px")
	.style("opacity", 0);

var keytypes = {
	"story": ['create_story', 'comment_story'],
	"listing": ['create_listing', 'comment_listing'],
	"transaction": ['transaction'],
	"social": ['conversation']
};
var overtooltip = false;
var overnode = false;

function findNode(node) {
	return node['id'] == userid;
}
//From https://stackoverflow.com/questions/38224875/replacing-d3-transform-in-d3-v4/38230545#38230545
function getTranslation(transform) {

	var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
	g.setAttributeNS(null, "transform", transform);
	var matrix = g.transform.baseVal.consolidate().matrix;

	return [matrix.e, matrix.f];
}