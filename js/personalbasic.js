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
        plotBasicDonut(graph_data[i], node_data[i]);
        maxindex+=1;
    }
    plotBasicDonut(graph_data[0], node_data[0]);
    numticks = results.length;
    plotsimpleline();
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

var parseTime = d3.timeParse("%Y/%m/%d %H:%M");

//Various date formats
var formatDate = d3.timeFormat("%Y/%m/%d");
var tickf = d3.timeFormat("%H:%M");
var ttf = d3.timeFormat("%b %d");
var data = {};
var node_data = [];
var graph_data = {};
var numticks = 0;
var myReturnText = "return";
var noActivityText = "No visible activity";

function getDateText(d) {
    return ttf(d.date) + "-" + ttf(d3.timeWeek.offset(d.date, 2))
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
