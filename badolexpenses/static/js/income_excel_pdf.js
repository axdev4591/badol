/*** check if date field is not empty, display <input type="submit" value="Valider" class="btn btn-outline-primary rounded" style="margin-top: 2em;" style="border-radius: 12px;"/> */
// Initialisation après chargement du DOM

import { saveAs } from "./FileSaver.js";
document.addEventListener("DOMContentLoaded", function() {




  function formatDate() {

    var d = new Date(),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    var time = new Date().getTime()
    return [day, month, year, time].join('-');
}


/************************************
 *                                  *  
 *                                  *
 *     PDF HANDLING  POST API FETCH *
 *                                  *
 *                                  *
 ************************************/


document.getElementById('pdf').onclick = function () {

  var formData = new FormData();

  var  startdate = document.querySelector("#formexport [name='startdate']");
  var startdate = startdate.value;
  var enddate = document.querySelector("#formexport [name='enddate']");
  var enddate = enddate.value;

  formData.append('startdate', startdate);
  formData.append('enddate', enddate);

  var data = {'startdate':startdate, 'enddate':enddate} 

  console.log("start date: "+startdate+ " enddate: "+enddate)
  console.log(formData)

var http = new XMLHttpRequest();
var url = '/income/iexport_pdf';
var params = 'orem=ipsum&name=binny';
http.open('POST', url, true);


http.setRequestHeader('Content-type', 'application/pdf');
http.responseType = "blob";

http.onreadystatechange = function() {
    if(http.readyState == 4 && http.status == 200) {
        //alert(http.responseText);
        
        var file = new Blob([http.response], { 
          type: 'application/pdf' 
      });
      
      console.log(formatDate())
  
      var filename = "badol-income-".concat(formatDate());
      filename = filename.concat(".pdf")
      // Generate file download directly in the browser !
      saveAs(file, filename);
    }
}

http.send("startdate="+startdate+"&enddate="+enddate);

}




/************************************
 *                                  *  
 *                                  *
 *   EXCEL HANDLING  POST API FETCH *
 *                                  *
 *                                  *
 ************************************/


document.getElementById('excel').onclick = function () {

  var formData = new FormData();

  var  startdate = document.querySelector("#formexport [name='startdate']");
  var startdate = startdate.value;
  var enddate = document.querySelector("#formexport [name='enddate']");
  var enddate = enddate.value;

  formData.append('startdate', startdate);
  formData.append('enddate', enddate);

  var data = {'startdate':startdate, 'enddate':enddate} 

  console.log("start date: "+startdate+ " enddate: "+enddate)
  console.log(formData)

var http = new XMLHttpRequest();
var url = '/income/iexport_excel';
//var params = 'orem=ipsum&name=binny';
http.open('POST', url, true);

http.setRequestHeader('Content-type', 'text/ms-excel');
http.responseType = "blob";

http.onreadystatechange = function() {
    if(http.readyState == 4 && http.status == 200) {

        var file = new Blob([http.response], { 
          type: 'text/ms-excel' 
      });
      
      console.log(formatDate())
  
      var filename = "badol-income-".concat(formatDate());
      filename = filename.concat(".xls")
      // Generate file download directly in the browser !
      saveAs(file, filename);
    }
}

http.send("startdate="+startdate+"&enddate="+enddate);

}


});