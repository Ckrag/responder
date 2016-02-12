var requestInterval = 3000;
var mainChart = null

$( document ).ready(function() {
  init();
});

function init(){
  // Show some loading or something til first ajax request returns

  //startEventLoop();
  loadData();
}

function loadData(){
  $.ajax({
    url: "http://localhost:9001", 
    type: "GET",
    dataType: "jsonp",
    format: "json",
    jsonpCallback: "jsonpCallback",
    timeout: requestInterval - 200, //Just to make sure its done in time..

    success: function(result){
      updateGraph(JSON.stringify(result));
    },
    error: function(xhr, textStatus, errorThrown){
       console.log('request failed: ' + errorThrown);
    }
  });
}

function configChart(chart, chartData){
  // We are setting a few options for our chart and override the defaults
  
  var options = {
    // Don't draw the line chart points
    showPoint: false,
    // Disable line smoothing
    lineSmooth: false,
    // X-Axis specific configuration
    axisX: {
      // We can disable the grid for this axis
      showGrid: false,
      // and also don't show the label
      showLabel: true
    },
    // Y-Axis specific configuration
    axisY: {
      // Lets offset the chart a bit from the labels
      offset: 100,
      // The label interpolation function enables you to modify the values
      // used for the labels on each axis. Here we are converting the
      // values into million pound.
      labelInterpolationFnc: function(value) {
        return value;
      }
    }
  };

  chart = new Chartist.Line('#main-chart', chartData, options);
}

function updateGraph(jsonData){

  var dataObject = JSON.parse(jsonData);

  var api_count = dataObject.api_count;
  var data = dataObject.api_data;

  var chartData = {
    labels: [],
    series: []
  };

  for (var i = 0; i < api_count; i++) {
    chartData.series.push([]);
  };

  for (var i = 0; i < data.length; i++) {
    chartData.labels[i] = convertUnixToReadable(data[i].timestamp);

    var responses = data[i].api_responsetimes;

    for (var j = 0; j < responses.length; j++) {
      chartData.series[j].push(responses[j].response_time); 
    };
  };

  if(mainChart === null){
    configChart(mainChart, chartData);
  } else {
    mainChart.update(chartData);
  }
}

function convertUnixToReadable(unixTimeStamp){
  var date = new Date(unixTimeStamp*1000);
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var seconds = date.getSeconds();

  return hours + ":" + minutes + ":" + seconds;
}

function startEventLoop(){
  var action = function() {
      loadData();
  };
  setInterval(action, requestInterval);
}