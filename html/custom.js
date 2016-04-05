var requestInterval = 3000;
var lineChart = null;
var timespan = 40;
var graphLifeSpan = 3600000; // 1 hour

var chartData = null;

var colorApiMap = [];

var startTime = new Date().getTime();

$( document ).ready(function() {
  init();
});

function init(){
  // Show some loading or something til first ajax request returns
  startEventLoop();
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
      onDataLoaded(JSON.stringify(result));
    },
    error: function(xhr, textStatus, errorThrown){
       console.log('request failed: ' + errorThrown);
    }
  });
}

function onDataLoaded(jsonData){
  var dataObject = JSON.parse(jsonData);

  if(dataObject.api_count === 0){
    // No apis, do nothing.
    // When we handle changing number of apis, start out drawing an empty
    // Some day :o)
    return;
  }

  if(chartData === null){
    createChartData(dataObject);
  } else {
    updateChartData(dataObject);
  }
}

function configChart(chart, chartData){
  var chart = document.getElementById('main-chart');
  var chartContext = chart.getContext('2d');

  Chart.defaults.global.legend.position = "bottom";
  Chart.defaults.global.legend.labels.fontSize = 25;
  Chart.defaults.global.legend.labels.boxWidth = 80;

  Chart.defaults.global.tooltips.enabled = true;
  Chart.defaults.global.tooltips.bodyFontStyle = "normal";
  Chart.defaults.global.tooltips.footerFontStyle = "normal";

  Chart.defaults.global.tooltips.titleFontSize = 18;
  Chart.defaults.global.tooltips.bodyFontSize = 15;
  Chart.defaults.global.tooltips.footerFontSize = 15;

  Chart.defaults.global.tooltips.callbacks.title = function(tooltipItem, data) { 
    return data.datasets[tooltipItem[0].datasetIndex].label;
  }

  Chart.defaults.global.tooltips.callbacks.label = function(tooltipItem, data) {
    return tooltipItem.xLabel;
  }

  Chart.defaults.global.tooltips.callbacks.beforeFooter = function(tooltipItem, data) {
    return tooltipItem[0].yLabel;
  }

  Chart.defaults.global.tooltips.callbacks.footer = function(tooltipItem, data) { 
    return data.responseCodeSets[tooltipItem[0].datasetIndex][tooltipItem[0].index];
  }

  lineChart = new Chart(chartContext, {
    type: 'line',
    data: chartData,
    options: {
      scales: {
        yAxes: [{
          ticks: {
            min: 0,
            max: 5,
            stepWidth: 1
          }
        }]
      }
    }
  });
}

function createChartData(dataObject){

  chartData = {
    labels: [],
    datasets: [],
    unixTimeStamps: [],
    responseCodeSets: []
  };
  
  var api_count = dataObject.api_count;
  var api_meta_data = dataObject.api_meta_data;
  var data = dataObject.api_data;

  for (var i = 0; i < api_count; i++) {
    chartData.datasets.push(createDataSet(api_meta_data[i]));
    chartData.responseCodeSets.push([]);
  };

  for (var i = 0; i < data.length; i++) {
    chartData.labels[i] = convertUnixToReadable(data[i].timestamp);
    chartData.unixTimeStamps[i] = data[i].timestamp;

    var responses = data[i].api_responsetimes;

    for (var j = 0; j < responses.length; j++) {
      chartData.datasets[j].data.push(responses[j].response_time);
      chartData.responseCodeSets[j].push(responses[j].response_code);
    };
  };

  // setup chart
  configChart(lineChart, chartData);
}

function createDataSet(api_meta_data){
  var name = (api_meta_data.pretty_name.length != 0) ? api_meta_data.pretty_name : api_meta_data.request_url;
  var color = (api_meta_data.pretty_color.length != 0) ? api_meta_data.pretty_color : getRandomColors(1)[0];

  rgbColor = hexToRgbaString(color, 1);

  return {
      borderColor : hexToRgbaString(color, 0.5),
      pointBorderColor : hexToRgbaString(color, 1),
      fill: false,
      backgroundColor : hexToRgbaString(color, 1),
      data : [],
      label : name
    }
}

function updateChartData(dataObject){

  var api_count = dataObject.api_count;
  var api_meta_data = dataObject.api_meta_data;
  var data = dataObject.api_data;

  for (var i = 0; i < data.length; i++) {
    chartData.labels[i] = convertUnixToReadable(data[i].timestamp);
    chartData.unixTimeStamps[i] = data[i].timestamp;

    var responses = data[i].api_responsetimes;
    
    for (var j = 0; j < responses.length; j++) {
      chartData.datasets[j].data.shift();
      chartData.datasets[j].data.push(responses[j].response_time);
      chartData.responseCodeSets[j].shift();
      chartData.responseCodeSets[j].push(responses[j].response_code);
    };
  };

  lineChart.update();
}

// Method expects two arrays of equal length
/**
Since the n'th indentation has most matching items
The new array must have n-1 new values, since this is the number of items before this index

newArr:  [0,2,3,4,5,6]
oldArr:        [4,5,6,3,7,4]
                    |
                3rd index from the top, is where most matches occur between the two lists

example would return 3
**/
function getArrayChangeOffset(newArray, oldArray){

  //validity check
  if(newArray.length != oldArray.length){
    // if not, simply return the difference, so it knows how many new values were added
    return newArray.length - oldArray.length;
  }

  var indexOffset = 0;
  var matchesForIndexOffset = [];

  for (var i = 0; i < oldArray.length; i++) {
    //find index-offset where most values match
    var matchCount = 0;

    for (var j = 0; j < oldArray.length - i; j++) {
      if(oldArray[j+i] === newArray[j]){
        matchCount++;
      }
    }
    matchesForIndexOffset[i] = matchCount;
    indexOffset++;
  };

  var highestIndex = 0;
  var highestValue = 0;
  for (var i = 0; i < matchesForIndexOffset.length; i++) {
    if(matchesForIndexOffset[i] > highestValue){
      highestIndex = i;
      highestValue = matchesForIndexOffset[i];
    }
  };

  return highestIndex;
  
}

function getRandomColors(numberOfColors){
  var colors = [];
  for (var i = 0; i < numberOfColors; i++) {
    colors.push('#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6));
  }
  return colors;
}

function convertUnixToReadable(unixTimeStamp){
  var date = new Date(unixTimeStamp*1000);
  var hours = String(date.getHours());
  var minutes = String(date.getMinutes());
  var seconds = String(date.getSeconds());

  if(hours.length === 1){
    hours = "0" + hours;
  }

  if(minutes.length === 1){
    minutes = "0" + minutes;
  }

  if(seconds.length === 1){
    seconds = "0" + seconds;
  }

  return hours + ":" + minutes + ":" + seconds;
}

function startEventLoop(){
  // Load instantly first time
  loadData()

  var action = function() {
      // Continue running app for a certain time
      now = new Date().getTime();

      if(now < startTime + graphLifeSpan){
        loadData();
      } else {
        //'reload' app when its been running too long. To avoid JS dying after several days of runtime
        window.location.reload();
      }
      
  };
  setInterval(action, requestInterval);
}

function hexToRgb(hex) {
  // FULL CREDIT GOES TO USER 'TIM DAWN' - http://stackoverflow.com/a/5624139
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function hexToRgbaString(hex, alpha){
  rgbObj = hexToRgb(hex);
  return "rgba(" + rgbObj.r + "," + rgbObj.g + "," + rgbObj.b + "," + alpha + ")";
}