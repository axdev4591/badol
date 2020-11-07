


function reply_click(clicked_id)
  {    

    var Link = "/income/income-delete/";
    document.querySelector("#btndel").href = ""; 
    var Link = "/income/income-delete/";

        
      Link  = Link.concat(clicked_id);
      console.log('Link income id: ', Link);
      
     document.querySelector("#btndel").href = Link; 
  
}

