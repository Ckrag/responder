var requestInterval = 3000;
var mainChart = null;
var timespan = 40;

var chartData = null;

var colorApiMap = [];

$( document ).ready(function() {
  init();
});

function init(){
  // Show some loading or something til first ajax request returns
  startEventLoop();
}

function addApiVisual(name, color){
  var html_string = "<div class='api_entry'><p class='api_name'><span style='background-color:" + color + ";'class='api_color'></span>" + name + "</p></div>";
  $("#api_info_box").append(html_string);
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

  if(dataObject.api_count == 0){
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
  var chartContext = document.getElementById('main-chart').getContext('2d');
  mainChart = new Chart(chartContext).Line(chartData, {
    scaleOverride : true,
    scaleSteps : 3,
    scaleStepWidth: 1,
    scaleStartValue: 0
  });
}

function createChartData(dataObject){

  chartData = {
    labels: [],
    datasets: [],
    unixTimeStamps: []
  };
  
  var api_count = dataObject.api_count;
  var api_names = dataObject.api_names;
  var data = dataObject.api_data;

  for (var i = 0; i < api_count; i++) {
    chartData.datasets.push(createDataSet(api_names[i]));
  };

  for (var i = 0; i < data.length; i++) {
    chartData.labels[i] = convertUnixToReadable(data[i].timestamp);
    chartData.unixTimeStamps[i] = data[i].timestamp;

    var responses = data[i].api_responsetimes;

    for (var j = 0; j < responses.length; j++) {
      chartData.datasets[j].data.push(responses[j].response_time); 
    };
  };

  // setup chart
  configChart(mainChart, chartData);

}

function createDataSet(apiName){
  var color = getRandomColors(1)[0];
  colorApiMap.push({ 
    name : apiName,
    color : color
   });

  addApiVisual(apiName, color);

  return {
      fillColor : "rgba(172,194,132,0.0)",
      strokeColor : color,
      pointColor : "#fff",
      pointStrokeColor : "#9DB86D",
      data : [],
      name : apiName
    }
}

// WHAT IF WE DONT HAVE MAX YET. NEW DATA CAN HOLD LONGER SETS !!!!!
function updateChartData(dataObject){

  var api_count = dataObject.api_count;
  var api_names = dataObject.api_names;
  var data = dataObject.api_data;

  var newLabels = [];
  var newResponseTimeSets = [];
  var newReponseTimestamps = []

  for (var i = 0; i < data.length; i++) {
    newLabels[i] = convertUnixToReadable(data[i].timestamp);
    newReponseTimestamps[i] = data[i].timestamp;

    var responses = data[i].api_responsetimes;

    var responseSet = [];

    for (var j = 0; j < responses.length; j++) {
      responseSet.push(responses[j].response_time);
    };
    newResponseTimeSets.push(responseSet);
  };

  var offsetIndex = getArrayChangeOffset(newReponseTimestamps, chartData.unixTimeStamps);

  for (var i = 0; i < offsetIndex; i++) {

    // Don't remove old entries until the graph shows full 'timespan'
    if(chartData.labels.length == timespan){
      mainChart.removeData();
    }

    var newData = [];
    //update old datasets by iterating over them.
    for (var j = 0; j < chartData.datasets.length; j++) {
      //console.log("response lookup: " + newResponseTimeSets.length + " - 1 - " + i + "["+j+"]");
      newData.push(newResponseTimeSets[newResponseTimeSets.length - offsetIndex + i][j]);
    };
    mainChart.addData(newData, newLabels[newLabels.length - offsetIndex + i]);
  };

  chartData.unixTimeStamps = newReponseTimestamps;
  for (var i = 0; i < newResponseTimeSets.length; i++) {
    for (var j = 0; j < chartData.datasets.length; j++) {
      chartData.datasets[j][i] = newResponseTimeSets[i][j];
    };
  };
}

// Method expects two arrays of equal length
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
      if(oldArray[j+i] == newArray[j]){
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

  /**
  Since the n'th indentation has most matching items
  The new array must have n-1 new values, since this is the number of items before this index

  newArr:  [0,2,3,4,5,6]
  oldArr:        [4,5,6,3,7,4]
                      |
                  3rd index from the top, is where most matches occur between the two lists
  
  example would return 3
  **/

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

  if(hours.length == 1){
    hours = "0" + hours;
  }

  if(minutes.length == 1){
    minutes = "0" + minutes;
  }

  if(seconds.length == 1){
    seconds = "0" + seconds;
  }

  return hours + ":" + minutes + ":" + seconds;
}

function startEventLoop(){
  // Load instantly first time
  loadData()

  var action = function() {
      loadData();
  };
  setInterval(action, requestInterval);
}