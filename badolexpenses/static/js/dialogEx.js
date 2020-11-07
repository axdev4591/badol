

function reply_click(clicked_id)
  {    
    document.querySelector("#btndel").href = ""; 
    var Link = "/expense-delete/";

      Link  = Link.concat(clicked_id);
      console.log('Link expense id: ', Link);
      document.querySelector("#btndel").href = Link; 

}

 