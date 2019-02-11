var datafilecounter = 1;
var drawn = {};

//GIANLUCA Colour scheme

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
var keytypes = {
	"story": ['create_story', 'comment_story'],
	"listing": ['create_listing', 'comment_listing'],
	"transaction": ['transaction'],
	"social": ['conversation']
};

var parseTime = d3.timeParse("%Y/%m/%d");

//Various date formats
var formatDate = d3.timeFormat("%Y/%m/%d");
var tickf = d3.timeFormat("%b'%y");
var ttf = d3.timeFormat("%b %d");

var urlParams = new URLSearchParams(window.location.search);
var uid = urlParams.get('userid'); // "edit"
var lang = urlParams.get('lang');

var data = {};
var node_data = [];
var graph_data = {};
var numticks = 0;





//Load data from JSON files into format readable by D3 
var maxindex = 0;
d3.json('../data/output/userdata/' + uid + '.json', function (results) {
	data = results;
	for (var fortnight = 0; fortnight < results.length; fortnight++) {
		node_data[fortnight] = results[fortnight]['nodes'].find(findNode);
		node_data[fortnight].date = parseTime(node_data[fortnight].date);
		graph_data[fortnight] = results[fortnight];
        plotdonut(graph_data[fortnight], node_data[fortnight]);
		maxindex++;
	}
    
	plotdonut(graph_data[0], node_data[0]);
	$('#donutdate').text(getDateText(node_data[currentdonut]));
	numticks = results.length;
	plotsimpleline(uid);
});

function findNode(node) {
	return node['id'] == uid;
}
//From https://stackoverflow.com/questions/38224875/replacing-d3-transform-in-d3-v4/38230545#38230545
function getTranslation(transform) {

	var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
	g.setAttributeNS(null, "transform", transform);
	var matrix = g.transform.baseVal.consolidate().matrix;

	return [matrix.e, matrix.f];
}