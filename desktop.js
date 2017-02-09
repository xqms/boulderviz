var loader1 = "<div style='padding:40px 0 0 0'><img border='0' alt='loading...' src='grafiken/loader.gif'></div>";
var loader2 = "<img style='width:30px; height:30px; position:relative; top:7px; left:-2px' border='0' alt='loading...' src='grafiken/loader.gif'>";

var userId = 0;
var userPwd = 0;
var userKat = 0;

function init(){
	
	userId = 0;
	userPwd = 0;
	userKat = 0;
	
	/*
	document.getElementById("link_a").style.color = "#0063DC";
	document.getElementById("link_b").style.color = "#0063DC";
	document.getElementById("link_c").style.color = "#0063DC";
	document.getElementById("link_d").style.color = "#0063DC";
	document.getElementById("link_e").style.color = "#0063DC";
	document.getElementById("link_f").style.color = "#0063DC";
	document.getElementById("link_g").style.color = "#0063DC";
	document.getElementById("link_h").style.color = "#0063DC";
	*/
	
	setFrame();
	
}

function myAjax(myScript,myData,myDataType,myTarget,use){
	$.ajax({  
		type: "POST",  
		url: myScript,  
		data: myData,  
		dataType: myDataType,
		success: function(phpData){  
  			document.getElementById(myTarget).innerHTML = phpData; 
  			if(use == 'login' && phpData == "nope"){
  				document.getElementById('login').style.display = "block";
  				document.getElementById('userData').innerHTML = "";
  				document.getElementById('errorMsg').style.display = "block";
  			}
  			if(use == 'login' && phpData != "nope"){
  				document.getElementById('errorMsg').style.display = "none";
  			}
 		}  
	}); 
} 

function login(){
	
	var id = document.getElementById('user').value;
	var pwd = document.getElementById('pwd').value;
	
	if(id == 0 || pwd == ""){
		alert("climber?");
	}
	else{
		
		document.getElementById('login').style.display = "none";
		document.getElementById('userData').innerHTML = loader1;
	
		userId = id;
		userPwd = pwd;
		
		var myScript = "userData.php";
		var myData = "id=" + id + "&pwd=" + pwd;
		var myTarget = "userData";
		var myDataType = "html";
		var use = "login";
		
		myAjax(myScript,myData,myDataType,myTarget,use);
	}
	
}

function loginShow(){
	
	var id = document.getElementById('user').value;
	var pwd = document.getElementById('pwd').value;
	
	if(id == 0 || pwd == ""){
		alert("climber?");
	}
	else{
		
		document.getElementById('login').style.display = "none";
		document.getElementById('userData').innerHTML = loader1;
	
		userId = id;
		userPwd = pwd;
		
		var myScript = "userDataShow.php";
		var myData = "id=" + id + "&pwd=" + pwd;
		var myTarget = "userData";
		var myDataType = "html";
		var use = "login";
		
		myAjax(myScript,myData,myDataType,myTarget,use);
	}
	
}

function logout(){
	
	document.getElementById('login').style.display = "block";
	document.getElementById('userData').innerHTML = "";
	document.getElementById('errorMsg').style.display = "none";
	
	userId = 0;
	userPwd = 0;
	userKat = 0;
	
	document.getElementById('formLogin').reset();
	
}

function logoutClimber(){
	
	document.getElementById('login').style.display = "block";
	document.getElementById('userData').innerHTML = "";
	document.getElementById('errorMsg').style.display = "none";
	
	document.getElementById('formLogin1').reset();
	
}

function logoutBoulder(){
	
	document.getElementById('login').style.display = "block";
	document.getElementById('userData').innerHTML = "";
	document.getElementById('errorMsg').style.display = "none";
	
	document.getElementById('formLogin2').reset();
	
}

function generate_scorecard(farb_key){
	
	document.getElementById('scorecard').innerHTML = loader1;
	
	var myScript = "getScorecard.php";
	var myData = "farb_key=" + farb_key + "&pwd=" + userPwd + "&user_id=" + userId;
	var myTarget = "scorecard";
	var myDataType = "html";
	var use = "scorecard";

	myAjax(myScript,myData,myDataType,myTarget,use);
	
}

function generate_scorecard_show(farb_key){
	
	document.getElementById('scorecard').innerHTML = loader1;
	
	var myScript = "getScorecardShow.php";
	var myData = "farb_key=" + farb_key + "&pwd=" + userPwd + "&user_id=" + userId;
	var myTarget = "scorecard";
	var myDataType = "html";
	var use = "scorecard";

	myAjax(myScript,myData,myDataType,myTarget,use);
	
}

function scoreNeu(user_id, farb_key, b, wert){
	
	var e = "b" + b;
	document.getElementById(e).innerHTML = loader2;
	
	var myScript = "scoreNeu.php";
	var myData = "farb_key=" + farb_key + "&pwd=" + userPwd + "&user_id=" + userId + "&b=" + b + "&wert=" + wert;
	var myTarget = e;
	var myDataType = "html";
	var use = "scoreNeu";

	myAjax(myScript,myData,myDataType,myTarget,use);
}

function loginBoulder(){
	
	var farb_key = document.getElementById('farb_key').value;
	var boulder = document.getElementById('boulder').value;
	
	if(farb_key == 0 || boulder == ""){
		alert("Farbe + Boulder?");
	}
	else{
		
		document.getElementById('login').style.display = "none";
		document.getElementById('userData').innerHTML = loader1;
		
		var myScript = "showBoulder.php";
		var myData = "farb_key=" + farb_key + "&boulder=" + boulder;
		var myTarget = "userData";
		var myDataType = "html";
		var use = "loginBoulder";
		
		myAjax(myScript,myData,myDataType,myTarget,use);
		
	}
	
}







