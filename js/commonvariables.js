var datafilecounter = 1;
var drawn = {};

//GIANLUCA Colour scheme

var keys = ['social', 'story', 'transaction', 'listing'];
var color = d3.scaleOrdinal() // D3 Version 4
	.domain(keys)
	.range(['#3ab2e3', '#7245ba', '#a2d733', '#e04776']);
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
var tickf = d3.timeFormat("%b\n%y");
var ttf = d3.timeFormat("%b %d");

var urlParams = new URLSearchParams(window.location.search);
var uid = urlParams.get('userid'); // "edit"
var lang = urlParams.get('lang');

var noActivityText;
var myReturnText;

if (lang == "hr") {
	myReturnText = "povratak";
    noActivityText = "nema vidljive aktivnosti";
} else if (lang == "it") {
	myReturnText = "ritorna";
    noActivityText = "nessuna attività visibile";
} else {
	myReturnText = "return";
    noActivityText = "No visible activity";
}

function italiantranslate(english) {
    console.log("ENGLISH IS " + english);
	if (english == "social")
		return "sociali";
	if (english == "transaction")
		return "transazioni";
	if (english == "listing")
		return "inserzione";
	return "storie";
}
function croatiantranslate(english) {
        console.log("ENGLISH IS " + english);

	if (english == "social")
		return "razgovori";
	if (english == "transaction")
		return "transkacije";
	if (english == "listing")
		return "unosi";
	return "priče";
}

function donutTranslate(type){
    if(type == "create_story"){
        if(lang=="hr") return "napisao je ovu priču</br>";
       if(lang=="it") return "scritto questa storia</br>";
       return "wrote this story</br>"
    }
    if(type == "comment_story"){
       if(lang=="hr") return " komentari na priče</br>";
       if(lang=="it") return " commenti di storia</br>";
       return " comments on this story</br>"
    }
    if(type == "create_listing"){
        if(lang=="hr") return "izradio je ovaj unos</br>";
       if(lang=="it") return "creato questo inserzione</br>";
       return "created this listing</br>"
    }
    if(type == "comment_listing"){
       if(lang=="hr") return " komentari na unosi</br>";
       if(lang=="it") return " commenti inserzioni</br>";
       return " comments on this listing</br>"
    }
    if(type == "conversation"){
       if(lang=="hr") return "razgovr s ";
       if(lang=="it") return "conversazione con ";
       return "conversation with "
    }
    if(type == "transaction"){
       if(lang=="hr") return "transakcije s tom commoner: ";
       if(lang=="it") return "transazioni con questo commoner: ";
       return "transactions with this commoner: "
    }
}

function donutSummaryTranslate(type,var1,var2){
    if(type=="story"){
       if(lang=="hr")
           return "broj stvorenih priča: " + var1 + "</br>komentari na priče: " + var2;
       if(lang=="it")
           return "storie create: " + var1 + "</br>commenti di storia: " + var2;
       return "Stories created: " + var1 + "</br>Story comments: " + var2;
    }
    if(type=="social"){
       if(lang=="hr") return "razgovori: " + var1;
       if(lang=="it") return "conversazioni: " + var1;
       return "Conversations: " + var1;
    }
    if(type=="transaction"){
       if(lang=="hr") return "transkacije: " + var1;
       if(lang=="it") return "transazioni: " + var1;
       return "Transactions: " + var1;
    }
    if(type=="listing"){
       if(lang=="hr")
           return "broj unesenih unosa: " + var1 + "</br>komentari na unosi: " + var2;
       if(lang=="it")
           return "inserzioni creati: " + var1 + "</br>commenti inserzioni: " + var2;
       return "Listings created: " + var1 + "</br>Listing comments: " + var2;
    }
}
function tooltipTranslate(type){
    if(type == "create_story"){
       if(lang=="hr") return "broj stvorenih priča: ";
       if(lang=="it") return "storie create: ";
       return "Stories written: "
    }
    if(type == "comment_story"){
        if(lang=="hr") return "komentari na priče: ";
        if(lang=="it") return "commenti di storia: ";
        return "Story comments: ";
    }
    if(type == "create_listing"){
        if(lang=="hr") return "broj unesenih unosa: ";
        if(lang=="it") return "inserzioni creati: ";
        return "Listings created: ";
    }
    if(type == "comment_listing"){
        if(lang=="hr") return "komentari na unosi: ";
        if(lang=="it") return "commenti inserzioni: ";
        return "Listing comments: ";
    }
    if(type == "transaction"){
        if(lang=="hr") return "transkacije: ";
        if(lang=="it") return "transazioni: ";
        return "Transactions: ";
    }
    if(type == "conversation"){
        if(lang=="hr") return "razgovori: ";
        if(lang=="it") return "conversazioni: ";
        return "Conversations: ";
    }
}

function getDateText(d) {
	if (lang == 'it') {
		return itDate(ttf(d.date)) + "-" + itDate(ttf(d3.timeWeek.offset(d.date, 2)));
	} else if (lang == 'hr') {
		return hrDate(ttf(d.date)) + "-" + hrDate(ttf(d3.timeWeek.offset(d.date, 2)));
	}
	return ttf(d.date) + "-" + ttf(d3.timeWeek.offset(d.date, 2))
}
function itDate(date) {
	var monthabb = date.split(" ")[0];
	var month_map = {
		"Jan": "gen",
		"Feb": "feb",
		"Mar": "mar",
		"Apr": "apr",
		"May": "mag",
		"Jun": "giu",
		"Jul": "lug",
		"Aug": "ago",
		"Sep": "set",
		"Oct": "ott",
		"Nov": "nov",
		"Dec": "dic"
	};
	return month_map[monthabb] + " " + date.split(" ")[1];
}
function hrDate(date) {
	var monthabb = date.split(" ")[0];
	var month_map = {
		"Jan": "sij",
		"Feb": "vel",
		"Mar": "ožu",
		"Apr": "tra",
		"May": "svi",
		"Jun": "lip",
		"Jul": "srp",
		"Aug": "kol",
		"Sep": "ruj",
		"Oct": "lis",
		"Nov": "stu",
		"Dec": "pro"
	};
	return month_map[monthabb] + " " + date.split(" ")[1];
}

var data = {};
var node_data = [];
var graph_data = {};
var numticks = 0;





//Load data from JSON files into format readable by D3
var maxindex = 0;

d3.json('../data/output/userdata/' + uid + '.json').then(results => {
	data = results;
	initDonutVars();
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
}).catch(err => {
	console.log(err);
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
