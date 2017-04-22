
function add_question(type){
  var base_div=document.getElementById("ques_list");
  var new_question_div=document.createElement("div");
  var count=0;
  while(document.getElementById("ques_"+count+".div")!=null)count++;
  new_question_div.id="ques_"+count+".div";
  new_question_div.name="ques_"+count+".div";
  new_question_div.setAttribute("class", "form-group row well");
  new_question_div.style.backgroundColor="#f8f8f8";
  new_question_div.style.border="1px solid #e7e7e7";


  // append info div
  var info_div=document.createElement("div");
  info_div.style.fontSize="13px";
  info_div.style.marginLeft="5px";
  info_div.style.marginTop="-10px";
  info_div.style.marginBottom="10px";

  var b=document.createElement("b");
  if(type==0)b.innerHTML="Single Choice";
  else if(type==1)b.innerHTML="Multiple Choice";
  else if(type==2)b.innerHTML="True or False";
  else b.innerHTML="Essay";
  info_div.appendChild(b);
  new_question_div.appendChild(info_div);

  var new_question_div_head=document.createElement("div");
  new_question_div_head.setAttribute("class", "row");
  new_question_div.appendChild(new_question_div_head);

  var new_question_type=document.createElement("input");
  new_question_type.id="ques_"+count+".type";
  new_question_type.name="ques_"+count+".type";
  new_question_type.type="Hidden";
  new_question_type.value=type;
  new_question_div_head.appendChild(new_question_type);

  var question_number = count + 1;
  var new_question_description=document.createElement("input");
  new_question_description.id="ques_"+count+".description";
  new_question_description.name="ques_"+count+".description";
  new_question_description.type="text";
  new_question_description.setAttribute("class", "form-control");
  new_question_description.setAttribute("required", "required");
  new_question_description.placeholder="Enter question";

  var new_question_description_div=document.createElement("div");
  new_question_description_div.setAttribute("class", "col-md-6");
  new_question_description_div.appendChild(new_question_description);
  new_question_div_head.appendChild(new_question_description_div);

  var new_question_div_button=document.createElement("div");
  new_question_div_button.setAttribute("class","ques_button");
  new_question_div_head.appendChild(new_question_div_button);

  var new_question_delete=document.createElement("span");
  new_question_delete.setAttribute("class", "pull-left btn glyphicon glyphicon-trash");
  new_question_delete.setAttribute("onclick","delete_question(this)");
  new_question_div_button.appendChild(new_question_delete);

  if (type <2) {
    var new_question_add=document.createElement("span");
    new_question_add.setAttribute("class", "pull-left btn glyphicon glyphicon-plus");
    new_question_add.setAttribute("onclick","add_option(this,"+type+")");
    new_question_div_button.appendChild(new_question_add);
  }

  var new_option_ul=document.createElement("ul");
  new_option_ul.setAttribute("class", "form-inline");
  new_option_ul.style.listStyleType="none";
  new_question_div.appendChild(new_option_ul);

  if(type<2){
    new_option_ul.innerHTML=
    "<li class=\"row\"><input class=\"col-md-7 form-control\" type=\"text\" id=\"ques_"+
    count+".option_0\" name=\"ques_"+count+".option_0\" placeholder=\"new option\" required/>"+
    "<div class=\"col-md-5 option_button\">"+
    "<span class=\"btn glyphicon glyphicon-trash\" title=\"Click to delete this option\" onclick=\"delete_option(this)\"></span></div></li>"+
    "<li class=\"row\"><input class=\"col-md-7 form-control\" type=\"text\" id=\"ques_"+
    count+".option_1\" name=\"ques_"+count+".option_1\" placeholder=\"new option\" required/>"+
    "<div class=\"col-md-5 option_button\">"+
    "<span class=\"btn glyphicon glyphicon-trash\" title=\"Click to delete this option\" onclick=\"delete_option(this)\"></span></div></li>"+
    "<li class=\"row\"><input class=\"col-md-7 form-control\" type=\"text\" id=\"ques_"+
    count+".option_2\" name=\"ques_"+count+".option_2\" placeholder=\"new option\" required/>"+
    "<div class=\"col-md-5 option_button\">"+
    "<span class=\"btn glyphicon glyphicon-trash\" title=\"Click to delete this option\" onclick=\"delete_option(this)\"></span></div></li>";
  }

  base_div.appendChild(new_question_div);
  new_question_description.focus();
}

function delete_question(obj){
  count=obj.parentNode.parentNode.parentNode.id.split('_')[1].split('.')[0];
  var current_question=document.getElementById("ques_"+count+".div");
  current_question.parentNode.removeChild(current_question);
  count++;
  current_question=document.getElementById("ques_"+count+".div");
  while(current_question!=null){
    var question_div=document.getElementById("ques_"+count+".div");
    question_div.id="ques_"+(count-1)+".div";
    question_div.name="ques_"+(count-1)+".div";

    var question_type=document.getElementById("ques_"+count+".type");
    question_type.id="ques_"+(count-1)+".type";
    question_type.name="ques_"+(count-1)+".type";
    var type=question_type.value;

    var question_description=document.getElementById("ques_"+count+".description");
    question_description.id="ques_"+(count-1)+".description";
    question_description.name="ques_"+(count-1)+".description";


    if(type<2){
      var option_count=0;
      var current_option=document.getElementById("ques_"+count+".option_"+option_count);
      while(current_option!=null){
        current_option.id="ques_"+(count-1)+".option_"+option_count;
        current_option.name="ques_"+(count-1)+".option_"+option_count;
        option_count++;
        current_option=document.getElementById("ques_"+count+".option_"+option_count);
      }
    }

    count++;
    current_question=document.getElementById("ques_"+count+".div");
  }
}

function add_option(obj,type){
  var count=obj.parentNode.parentNode.parentNode.id.split('_')[1].split('.')[0];
  var ul=obj.parentNode.parentNode.nextSibling;
  var ocount=0;
  var radio;
  if(type==0)radio="radio";
  else radio="checkbox";
  while(document.getElementById("ques_"+count+".option_"+ocount)!=null)ocount++;
  var li=document.createElement("li");
  li.setAttribute("class","row");
  li.innerHTML="<input class=\"col-md-7 form-control\" type=\"text\" id=\"ques_"+
    count+".option_"+ocount+"\" name=\"ques_"+count+".option_"+ocount+"\" placeholder=\"new option\" required/>"+
    "<div class=\"col-md-5 option_button\">"+
    "<span class=\"btn glyphicon glyphicon-trash\" title=\"Click to delete this option\" onclick=\"delete_option(this)\"></span></div>";
  ul.appendChild(li);
  document.getElementById("ques_"+count+".option_"+ocount).focus();
}

function delete_option(obj){
  var option=obj.parentNode.previousSibling;
  var li=option.parentNode;
  var ul=li.parentNode;
  var ques_count=option.id.split('_')[1].split('.')[0];
  var option_count=option.id.split('_')[2];
  ul.removeChild(li);
  option_count++;
  var current_option=document.getElementById("ques_"+ques_count+".option_"+option_count);
  while(current_option!=null){
    current_option.id="ques_"+ques_count+".option_"+(option_count-1);
    current_option.name="ques_"+ques_count+".option_"+(option_count-1);
    option_count++;
    current_option=document.getElementById("ques_"+ques_count+".option_"+option_count);
  }
}
