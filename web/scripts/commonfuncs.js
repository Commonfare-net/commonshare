//Common functions
var data = {};
var node_data = {};
var graph_data = {};

var keytypes = {
    "story": ['create_story','comment_story','rcomment_story'],
    "listing": ['create_listing','comment_listing','rcomment_listing'],
    "transaction": ['transaction'],
    "social": ['conversation']
};
var mykeys = ['social','story','transaction','listing'];
var range = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c'];

var brightrange = [d3.rgb('#a6cee3').brighter(0.3),d3.rgb('#1f78b4').brighter(0.3),d3.rgb('#b2df8a').brighter(0.3),d3.rgb('#33a02c').brighter(0.3)];
var nodetypes = ['commoner','story','listing'];
var noderange = ['#33a02c','#1f78b4','purple'];

nodecolor = d3.scaleOrdinal()
.domain(nodetypes)
.range(noderange);
color = d3.scaleOrdinal() // D3 Version 4
		.domain(mykeys)
		.range(range);
brightercolor = d3.scaleOrdinal()
        .domain(mykeys)
        .range(brightrange);
        
var urlParams = new URLSearchParams(window.location.search);
var userid = urlParams.get('userid'); 
var lang = urlParams.get('lang');

var parseTime = d3.timeParse("%Y/%m/%d");
var tooltipFormat = d3.timeFormat("%b %d");

function getDateText(data){
    console.log("lang is " + lang);
    if(lang == 'it')
        return italianDate(tooltipFormat(data.date)) + "-" + italianDate(tooltipFormat(d3.timeWeek.offset(data.date,2)));
    else if(lang == 'hr')
        return croatianDate(tooltipFormat(data.date)) + "-" + croatianDate(tooltipFormat(d3.timeWeek.offset(data.date,2)));
    else
        return tooltipFormat(data.date) + "-" + tooltipFormat(d3.timeWeek.offset(data.date,2))
    }
function getItalianDateText(data){
    return italianDate(tooltipFormat(data.date)) + "-" + italianDate(tooltipFormat(d3.timeWeek.offset(data.date,2)))
}
function getCroatianDateText(data){
    return croatianDate(tooltipFormat(data.date)) + "-" + croatianDate(tooltipFormat(d3.timeWeek.offset(data.date,2)))
}
function findNode(node) {
	return node['id'] == userid;
}

function italianDate(date){
    var monthabb = date.split(" ")[0];
    var ital;
    switch(monthabb){
        case "Jan":
            ital = "gen";break;
        case "Feb":
            ital = "feb";break;
        case "Mar":
            ital = "mar";break;
        case "Apr":
            ital = "apr";break;
        case "May":
            ital = "mag";break;
        case "Jun":
            ital = "giu";break;
        case "Jul":
            ital = "lug";break;
        case "Aug":
            ital = "ago";break;
        case "Sep":
            ital = "set";break;
        case "Oct":
            ital = "ott";break;
        case "Nov":
            ital = "nov";break;
        case "Dec":
            ital = "dic";break;
    
    }
    return ital + " " + date.split(" ")[1];
}
function croatianDate(date){
    var monthabb = date.split(" ")[0];
    var ital;
    switch(monthabb){
        case "Jan":
            ital = "sij";break;
        case "Feb":
            ital = "vel";break;
        case "Mar":
            ital = "ožu";break;
        case "Apr":
            ital = "tra";break;
        case "May":
            ital = "svi";break;
        case "Jun":
            ital = "lip";break;
        case "Jul":
            ital = "srp";break;
        case "Aug":
            ital = "kol";break;
        case "Sep":
            ital = "ruj";break;
        case "Oct":
            ital = "lis";break;
        case "Nov":
            ital = "stu";break;
        case "Dec":
            ital = "pro";break;
    
    }
    return ital + " " + date.split(" ")[1];
}
function getUrl(type, name){
    var prefix;
    if(type == 'commoner' || type == 'transaction' || type == 'social')
        prefix = "https://commonfare.net/en/commoners/";
    if(type == 'listing')
        prefix = "https://commonfare.net/en/listings/";
    if(type == 'story')
        prefix = "https://commonfare.net/en/stories/";
    
    name = name.normalize('NFD').replace(/[\u0300-\u036f]/g, "");
            name = name.replace(/[^a-z0-9/s _-]/gi, '').toLowerCase();

        name = name.split(' ');
        var result = '';
        for (var i = 0; i < name.length; i++) {
            if ((name.length - 1) == i) {
                result += name[i];
            } else {
                result += name[i] + '-';
            }
        }
        result = result.replace('---','-');
        var storyurl = prefix + result;
        return storyurl;
}