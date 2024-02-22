var _data;
var _labels;
var myPieChart = null; // "global" access...
var interval;

//Plots
function getData() {
  $.ajax({
   url: "/get_data",
   type: "get",
   success: function(response) {
     full_data = JSON.parse(response.payload);
     _data = full_data['data'];
     _labels = full_data['labels'];
     myChart.data.labels = _labels;
     myChart.data.datasets[0].data = _data;
     myChart.update('none');
   },
 });
 }

function lineChart() {
let ctx = document.getElementById('lineChart').getContext('2d');
myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: _labels,
        datasets: [{
            label: 'Data points',
            data: _data,
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            pointBorderColor: 'rgb(0, 0, 0)',
            pointRadius: 5,
            pointStyle: 'cross',
            showLine: false,
            lineTension: 0.1
        }]
    },
    options: {
            scales:{
            x: {
                display: false
            }
        },
    responsive: false,
  plugins: {
    legend: {
      display: false
    }
    }
    }
});
}

//Buttons
function btnStopStart() {
  var x = document.getElementById("button_stop_start");
  if (x.innerHTML === "Stop") {
     stopData();
  x.innerHTML = "Start";
  } else if (x.innerHTML === "Start") {
   showGraph(document.getElementById("chartDiv"));
   startData();
   x.innerHTML = "Stop";
  }
}

function hideGraph() {
  var x = document.getElementById("chartDiv");
  x.style.display = "none";
  document.getElementById("button_show").innerHTML = "Show";
}

function showGraph() {
  var x = document.getElementById("chartDiv");
  x.style.display = "block";
  document.getElementById("button_show").innerHTML = "Hide";
}

function btnToggleGraph() {
  var x = document.getElementById("chartDiv");
  if (x.style.display === "none") {
    showGraph();
  }
  else {
  hideGraph();
  }
}

function btnResetData() {
  showGraph();
  resetData();
  var x = document.getElementById("button_stop_start");
  x.innerHTML = "Stop"
  startData();
 }

function btnToggleFreeze() {
  var x = document.getElementById("button_freeze");
  if (x.innerHTML === "Set to Manual camera settings") {
     freezeSettings();
     x.innerHTML = "Set to Auto camera settings";
  } else if (x.innerHTML === "Set to Auto camera settings") {
     unfreezeSettings();
     x.innerHTML = "Set to Manual camera settings";
  }
 }

function btnfreeze_reset() {
  var x = document.getElementById("button_freeze");
  x.innerHTML = "Set to Manual camera settings";
}

//Ajax calls
function startData() {
  $.ajax({
   url: "/start_data",
   type: "get",
 });
 clearInterval(interval);
 interval = setInterval(getData, 300);
}

function stopData() {
  $.ajax({
   url: "/stop_data",
   type: "get",
 });
 clearInterval(interval);
}

function resetData() {
  $.ajax({
   url: "/reset_data",
   type: "get",
 }); }

function freezeSettings() {
  $.ajax({
   url: "/freeze_settings",
   type: "get",
 }); }

function unfreezeSettings() {
  $.ajax({
   url: "/unfreeze_settings",
   type: "get",
 }); }

// MAIN
$(document).ready(function() {
  lineChart();
});


