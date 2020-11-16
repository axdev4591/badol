
// Initialisation après chargement du DOM
document.addEventListener("DOMContentLoaded", function() {


checkMethod = document.getElementById("checkMethod");
var ctxP = "";
var ctxP2 = "";
var ctxP4 = "";
var mlabels = "";
var mdata = "";

var resetCanvas = function(){
  $('#myChart').remove();
  $('#pc1').append('<canvas id="myChart" width="800" height="400"></canvas>');

  $('#myChart2').remove();
  $('#pc2').append('<canvas id="myChart2" width="50" height="50"></canvas>');

  $('#myChart4').remove();
  $('#pc4').append('<canvas id="myChart4" width="48" height="50"></canvas>');

  
};

/*************************
 *                       *  
 *                       *
 *  GRAPH CHART METHODS  *
 *                       *
 *                       *
 *************************/
  const renderChart = (data, labels) =>{

    var myPieChart = new Chart(ctxP, {
      plugins: [ChartDataLabels],
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: "montant",
          data: data,
          fill: false,
          lineTension: 0,
          borderColor: "#00ccff",
          pointBorderWidth: 3,
          backgroundColor:'#00ccff',
    
        }],
        borderWidth: 1
      },
      options: {
    
        title: {
            display: true,
            text: "Statistique des dépenses",
            fontSize: 18,
            color:'#00ccff'
        },
        
        responsive: true,
        maintainAspectRatio: false,
        responsiveAnimationDuration: 0,
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true,
              callback: function(value, index, values) {
                if(parseInt(value) >= 1000){
                  return  value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "");
                } else {
                  return value;
                }
              }
            }
          }]
        },
        legend: {
          position: 'right',
          labels: {
            padding: 20,
            boxWidth: 10
          }
        },
        plugins: {
          datalabels: {
            formatter: (value, ctx) => {
              let sum = 0;
              let dataArr = ctx.chart.data.datasets[0].data;
              dataArr.map(data => {
                sum += data;
              });
              let percentage = (value * 100 / sum).toFixed(2) + "%";
              return percentage;
            },
            color: 'black',
            labels: {
              title: {
                font: {
                  size: '14'
                }
              }
            }
          }
        }
      }
    });
    
      };
    
  const renderChart2 = (data, labels) =>{
    
        var myPieChart = new Chart(ctxP2, {
          plugins: [ChartDataLabels],
          type: 'pie',
          data: {
            labels: labels,
            datasets: [{
              label: "montant",
              data: data,
              backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ]
            }],
            borderWidth: 1
          },
          options: {
        
            title: {
                display: true,
                fontSize: 25,
            },
            
            responsive: true,
            legend: {
              position: 'right',
              labels: {
                padding: 20,
                boxWidth: 10
              }
            },
            plugins: {
              datalabels: {
                formatter: (value, ctx) => {
                  let sum = 0;
                  let dataArr = ctx.chart.data.datasets[0].data;
                  dataArr.map(data => {
                    sum += data;
                  });
                  let percentage = (value * 100 / sum).toFixed(2) + "%";
                  return percentage;
                },
                color: 'black',
                labels: {
                  title: {
                    font: {
                      size: '14'
                    }
                  }
                }
              }
            }
          }
        });
        
          };
         


  const renderChart4 = (data, labels) =>{

    var myPieChart = new Chart(ctxP4, {
      plugins: [ChartDataLabels],
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          label: "montant",
          data: data,
          backgroundColor: [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)'
        ],
        borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
        ]
        }],
        borderWidth: 1
      },
      options: {
    
        title: {
            display: true,
            fontSize: 25,
        },
        
        responsive: true,
        legend: {
          position: 'right',
          labels: {
            padding: 20,
            boxWidth: 10
          }
        },
        plugins: {
          datalabels: {
            formatter: (value, ctx) => {
              let sum = 0;
              let dataArr = ctx.chart.data.datasets[0].data;
              dataArr.map(data => {
                sum += data;
              });
              let percentage = (value * 100 / sum).toFixed(2) + "%";
              return percentage;
            },
            color: 'black',
            labels: {
              title: {
                font: {
                  size: '14'
                }
              }
            }
          }
        }
      }
    });
    
      };


/*************************
 *                       *  
 *                       *
 *    GET API FETCH      *
 *                       *
 *                       *
 *************************/

  function getexpense(){

      fetch('/expense_category_summary')
      .then((res)=>res.json())
      .then((results)=>{
          console.log("data for get", results);
          const category_data = results.expense_data;
            mlabels = Object.keys(category_data);
            mdata = Object.values(category_data);
          if(checkMethod.textContent == 'false'){
          resetCanvas();
          ctxP = document.getElementById("myChart").getContext('2d');
          ctxP2 = document.getElementById("myChart2").getContext('2d');
          ctxP4 = document.getElementById("myChart4").getContext('2d');

          renderChart(mdata, mlabels); 
          renderChart2(mdata, mlabels);
          renderChart4(mdata, mlabels); 

          }

      });

}
document.onload =  getexpense();




/*************************
 *                       *  
 *                       *
 *     POST API FETCH    *
 *                       *
 *                       *
 *************************/


  // mettre ici le code à exécuter
  var myform = document.getElementById("myform");

myform.addEventListener('submit', function(e) {
     checkMethod.innerHTML = "True"

      e.preventDefault();

      const formData = new FormData(this);

      fetch('/expense_category_summary', {
        method: 'post',
        body: formData
      }).
      then((res)=>res.json()).
      then((results)=>{
        console.log("data for post", results);
        const category_data = results.expense_data;
        mlabels = Object.keys(category_data);
        mdata = Object.values(category_data);
        if(checkMethod.textContent == 'True'){

          resetCanvas();
          ctxP = document.getElementById("myChart").getContext('2d');
          ctxP2 = document.getElementById("myChart2").getContext('2d');
          ctxP4 = document.getElementById("myChart4").getContext('2d');

          renderChart(mdata, mlabels); 
          renderChart2(mdata, mlabels);
          renderChart4(mdata, mlabels);  
          }
      }).
      catch(function(error){
        console.log(error);
      })
 

  });


/************side bar********** */

  // Get the container element
//var btnContainer = document.getElementById("nav-item");
 
var header = document.getElementById("myside");
var btns = document.getElementsByClassName("nav-link");
//console.log(btns[0]);
for (var i = 0; i < btns.length; i++) {
  console.log("before clickefbn");

  btns[i].addEventListener("click", function() {
  var current = document.getElementsByClassName("active");
  console.log("is clickefbn");
  current[0].className = current[0].className.replace(" active", "");
  this.className += " active";
  });
}


function switchChannel(el){
  // find all the elements in your channel list and loop over them
  Array.prototype.slice.call(document.querySelectorAll('ul[data-tag="channelList"] li')).forEach(function(element){
    // remove the selected class
    element.classList.remove('active');
  });
  // add the selected class to the element that was clicked
  console.log('add class')
  el.classList.add('active');
}
});
    
