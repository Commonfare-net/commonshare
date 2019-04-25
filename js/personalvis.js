var urlParams = new URLSearchParams(window.location.search);
var uid = urlParams.get("userid"); // "edit"
var lang = urlParams.get("lang");
var langindex = (
    (lang=="it") ? 1 : (lang=="hr") ? 2 : 0);
//Need maxindex to know how far to go with donut date picker
var maxindex = 0;

/**
* Load all our files and then plot the donut and line charts
**/
d3.json("../data/output/userdata/" + uid + ".json").then((results) => {
    data = results;
    initDonutVars();
    for (var i = 0; i < results.length; i+=1) {
        node_data[i] = results[i]["nodes"].find(findNode);
        node_data[i].date = parseTime(node_data[i].date);
        graph_data[i] = results[i];
        plotDonut(graph_data[i], node_data[i]);
        maxindex+=1;
    }
    plotDonut(graph_data[0], node_data[0]);
    numticks = results.length;
    plotLine();
}).catch(err => {
    console.log(err);
});

var datafilecounter = 1;
var drawn = {};

//Colour scheme

var keys = ["social", "story", "transaction", "listing"];
var color = d3.scaleOrdinal() // D3 Version 4
    .domain(keys)
    .range(["#3ab2e3", "#7245ba", "#a2d733", "#e04776"]);
var mykeys = [];

var parseTime = d3.timeParse("%Y/%m/%d");

//Various date formats
var formatDate = d3.timeFormat("%Y/%m/%d");
var tickf = d3.timeFormat("%b-%y");
var ttf = d3.timeFormat("%b %d");
var noActivityText;
var myReturnText;

var data = {};
var node_data = [];
var graph_data = {};
var numticks = 0;

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

var var1;
var var2;
var translations = {
    "social" : ["social","sociali","razgovori"],
    "transaction" : ["transaction","transazioni","transkacije"],
    "listing" : ["listing","inserzione","unosi"],
    "story" : ["story","storie","priče"],
    "donutcreate_story": ["wrote this story</br>","scritto questa storia</br>","napisao je ovu priču</br>"],
    "donutcomment_story" : [" comments on this story</br>"," commenti di storia</br>", " komentari na priče</br>"],
    "donutcreate_listing" : ["created this listing</br>","creato questo inserzione</br>","izradio je ovaj unos</br>"],
    "donutcomment_listing" : [" comments on this listing</br>"," commenti inserzioni</br>"," komentari na unosi</br>"],
    "donutconversation" : ["conversation with ","conversazione con ","razgovr s "],
    "donuttransaction" : ["transactions with this commoner: ","transazioni con questo commoner: ","transakcije s tom commoner: "],
    
    "tooltipcreate_story": ["Stories written: ","storie create: ","broj stvorenih priča: "],
    "tooltipcomment_story" : ["Story comments: ","commenti di storia: ", "komentari na priče: "],
    "tooltipcreate_listing" : ["Listings created: ","inserzioni creati: ","broj unesenih unosa: "],
    "tooltipcomment_listing" : ["Listing comments: ","commenti inserzioni: ","komentari na unosi: "],
    "tooltipconversation" : ["Conversations: ","conversazioni: ","razgovori: "],
    "tooltiptransaction" : ["Transactions: ","transazioni: ","transakcije: "],
    
    "Jan": ["Jan","gen","sij"],
    "Feb": ["Feb","feb","vel"],
    "Mar": ["Mar","mar","ožu"],
    "Apr": ["Apr","apr","tra"],
    "May": ["May","mag","svi"],
    "Jun": ["Jun","giu","lip"],
    "Jul": ["Jul","lug","srp"],
    "Aug": ["Aug","ago","kol"],
    "Sep": ["Sep","set","ruj"],
    "Oct": ["Oct","ott","lis"],
    "Nov": ["Nov","nov","stu"],
    "Dec": ["Dec","dic","pro"],
}
function translate(label){
    return translations[label][langindex];
}

function donutSummaryTranslate(type,x,y){
    dtranslations = {
    "donutstory":
    [`Stories created: ${x}</br>Story comments: ${y}`,`storie create: ${x}</br>commenti di storia: ${y}`,`broj stvorenih priča: ${x}</br>komentari na priče: ${y}`],
    "donutsocial":
    [`Conversations: ${x}`,`conversazioni: ${x}`,`razgovori: ${x}`],
    "donuttransaction": 
    [`Transactions: ${x}`,`transazioni: ${x}`,`transkacije: ${x}`],
    "donutlisting": 
    [`Listings created: ${x}</br>Listing comments: ${y}`,`inserzioni creati: ${x}</br>commenti inserzioni: ${y}`,`broj unesenih unosa: ${x}</br>komentari na unosi: ${y}`]
    }
    return dtranslations[type][langindex];
}
 
function getDateText(d) {
    return abb(ttf(d.date)) + "-" + abb(ttf(d3.timeWeek.offset(d.date, 2)));
}
function abb(date) {
    var monthabb = date.split(" ")[0];
    return translate(monthabb) + " " + date.split(" ")[1];
}

function findNode(node) {
    return node["id"] == uid;
}
//From https://stackoverflow.com/questions/38224875/replacing-d3-transform-in-d3-v4/38230545#38230545
function getTranslation(transform) {

    var g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.setAttributeNS(null, "transform", transform);
    var matrix = g.transform.baseVal.consolidate().matrix;

    return [matrix.e, matrix.f];
}
