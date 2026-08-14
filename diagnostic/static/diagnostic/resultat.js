(function(){
  "use strict";
  var body=document.body,eventUrl=body.dataset.eventUrl,sessionId=body.dataset.sessionId,feedbackUrl=body.dataset.feedbackUrl;
  var csrf=document.querySelector("[name=csrfmiddlewaretoken]").value,rating=0;
  function event(name){var data={session_id:sessionId,nom:name,ecran:"resultat",device:innerWidth<700?"mobile":"desktop"};if(window.gtag)gtag("event","diagnostic_"+name,data);fetch(eventUrl,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data),keepalive:true}).catch(function(){})}
  document.querySelectorAll("[data-track]").forEach(function(link){link.addEventListener("click",function(){event(this.dataset.track)})});
  document.querySelectorAll("[data-rating]").forEach(function(button){button.addEventListener("click",function(){rating=Number(this.dataset.rating);document.querySelectorAll("[data-rating]").forEach(function(btn){btn.classList.toggle("active",Number(btn.dataset.rating)===rating)});document.getElementById("feedback-submit").disabled=false})});
  document.getElementById("feedback-submit").addEventListener("click",function(){var button=this,error=document.getElementById("feedback-error");button.disabled=true;fetch(feedbackUrl,{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":csrf},body:JSON.stringify({note:rating,commentaire:document.getElementById("feedback").value.trim()})}).then(function(r){return r.json().then(function(data){if(!r.ok)throw new Error(data.error||"Une erreur est survenue.");return data})}).then(function(){document.querySelector(".feedback-form").hidden=true;document.querySelector(".thanks").hidden=false}).catch(function(err){button.disabled=false;error.textContent=err.message;error.hidden=false})});
})();
