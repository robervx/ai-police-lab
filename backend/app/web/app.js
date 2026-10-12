"use strict";
const $ = id => document.getElementById(id);
let data = null, cursor = 0, timer = null, fetching = false, selectionVersion = 0;
const statusLabels = {complete:"Traza completa · cierre registrado",incomplete:"Incompleta · sin cierre registrado",invalid:"Traza dañada · solo prefijo válido",unreadable:"Traza no legible",not_started:"Sin traza registrada"};
const eventLabels = {agent_action_requested:"AGENTE",citizen_utterance:"TESTIMONIO",tool_result:"RESULTADO DEL MOTOR",agent_action_rejected:"ACCIÓN RECHAZADA",session_closed:"CIERRE REGISTRADO"};
const fieldLabels = {question:"Pregunta",message:"Mensaje",target:"Personaje",output:"Resultado",available:"Disponible",recorded:"Registrado",material_effect:"Efecto material",final_decision:"Decisión final",actions_taken:"Actuaciones",verified_facts:"Observaciones según el agente",unverified_claims:"Testimonios según el agente",remaining_uncertainties:"Incertidumbres",justification:"Justificación",reason:"Motivo",decision:"Decisión",observation_id:"Observación",check_id:"Comprobación"};
function el(tag, text, cls) {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function maxSteps(){return data ? Math.max(0,...data.lanes.map(l=>l.events.length)) : 0;}
function stop(){clearInterval(timer);timer=null;$('play').textContent='▶ Reproducir';$('play').setAttribute('aria-label','Reproducir');}
function renderEvent(event){
 const card=el('article',undefined,'event '+event.type), head=el('div',undefined,'event-head');
 head.append(el('strong',eventLabels[event.type]||event.type),el('span',`T${event.turn} · #${event.seq}`));card.append(head);
 for(const [key,value] of Object.entries(event.payload)){
  if(key==='source')continue;
  if(key==='action'){card.append(el('strong',value));continue;}
  if(key!=='text')card.append(el('span',fieldLabels[key]||key,'field-label'));
  if(Array.isArray(value)){const list=el('ul');for(const item of value)list.append(el('li',item));card.append(list);}
  else card.append(el('p',typeof value==='boolean'?(value?'Sí':'No'):value));
 }return card;
}
function render(){
 const max=maxSteps();cursor=Math.min(cursor,max);$('position').max=max;$('position').value=cursor;$('counter').textContent=`${cursor} / ${max}`;
 for(const id of ['play','step','reset','position'])$(id).disabled=!max;
 $('download').disabled=!data;
 $('conditions').textContent=data?.conditions_warning||'';
 if(!data){
  $('scenario').textContent='Sin selección cargada';$('intro').textContent='Selecciona una ejecución disponible o inicia una demo local.';
  $('lanes').replaceChildren(...[1,2].map(i=>{const lane=el('article',undefined,'lane empty');lane.append(el('h2',`Participante ${i}`),el('p','Sin datos cargados.'));return lane;}));return;
 }
 $('scenario').textContent=data.lanes[0].scenario||'Escenario no disponible';
 $('intro').textContent=data.lanes.find(l=>l.intro)?.intro||'No hay un aviso público disponible en la traza.';
 const container=$('lanes');container.classList.toggle('four',data.lanes.length>2);const previousScroll=[...container.querySelectorAll('.stream')].map(n=>n.scrollTop);container.replaceChildren();
 data.lanes.forEach((lane,index)=>{
  const article=el('article',undefined,'lane'),header=el('header',undefined,'lane-header');
  header.append(el('span',`CARRIL 0${index+1} · ${lane.provider==='local'?'DEMO LOCAL CON GUION':lane.provider||'SIN DATOS'}`,'lane-label'));
  header.append(el('h2',lane.model||lane.participant),el('span',statusLabels[lane.status]||'Estado desconocido','status '+lane.status));
  if(lane.model)header.append(el('p','Identificador de modelo solicitado','metadata'));
  header.append(el('p',`Participante: ${lane.participant}`,'metadata'));
  if(lane.citizen)header.append(el('p',`Ciudadano: ${lane.citizen}`,'metadata'));
  header.append(el('p','Revisión humana no incorporada a esta vista','metadata'));article.append(header);
  const stream=el('div',undefined,'stream');stream.setAttribute('aria-label',`Eventos de ${lane.participant}`);stream.tabIndex=0;
  for(const event of lane.events.slice(0,cursor))stream.append(renderEvent(event));
  if(!cursor||!lane.events.length)stream.append(el('p',lane.events.length?'Pulsa Reproducir o Paso para recorrer los eventos.':'No hay eventos públicos disponibles.','empty'));
  article.append(stream);container.append(article);stream.scrollTop=timer||$('follow').checked?stream.scrollHeight:previousScroll[index]||0;
 });
}
async function request(url,options){const response=await fetch(url,options);if(!response.ok)throw new Error('No se pudo leer o completar la solicitud.');return response.json();}
async function loadRuns(preferred){
 const runs=await request('/api/runs'),selected=preferred||$('runs').value;
 $('runs').replaceChildren();
 if(!runs.length){$('runs').append(new Option('Todavía no hay ejecuciones',''));selectionVersion++;stop();data=null;cursor=0;render();return;}
 runs.forEach((r,i)=>$('runs').append(new Option(`${i===0?'Más reciente · ':''}${r.id}`,r.id)));
 $('runs').value=runs.some(r=>r.id===selected)?selected:runs[0].id;
}
async function loadSelected(reset=false){
 const id=$('runs').value;if(!id)return;
 const generation=++selectionVersion;
 if(reset||data?.run_id!==id){stop();cursor=0;data=null;render();}
 const next=await request('/api/runs/'+encodeURIComponent(id));
 if(generation!==selectionVersion||$('runs').value!==id)return;
 data=next;if($('follow').checked)cursor=maxSteps();render();
 $('message').textContent='';
}
function error(error){$('message').textContent=error.message;}
$('runs').addEventListener('change',()=>loadSelected(true).catch(error));
$('refresh').addEventListener('click',async()=>{try{await loadRuns();await loadSelected();$('message').textContent='Vista actualizada desde los eventos guardados.';}catch(e){error(e);}});
$('demo').addEventListener('click',async()=>{
 $('demo').disabled=true;const size=$('demo-size').value;$('message').textContent=`Ejecutando ${size} sesiones locales sin APIs…`;
 try{stop();const result=await request(size==='4'?'/api/demo/4':'/api/demo',{method:'POST',headers:{'X-Lab-Request':'demo'}});await loadRuns(result.run_id);$('follow').checked=false;await loadSelected(true);$('message').textContent='Demo guardada. Pulsa Reproducir para explorar los recorridos.';}
 catch(e){error(e);}finally{$('demo').disabled=false;}
});
$('play').addEventListener('click',()=>{
 if(timer){stop();return;}if(cursor>=maxSteps())cursor=0;$('follow').checked=false;
 $('play').textContent='Ⅱ Pausa';$('play').setAttribute('aria-label','Pausar');
 timer=setInterval(()=>{cursor++;render();if(cursor>=maxSteps())stop();},700);render();
});
$('step').addEventListener('click',()=>{stop();$('follow').checked=false;cursor=Math.min(cursor+1,maxSteps());render();});
$('reset').addEventListener('click',()=>{stop();$('follow').checked=false;cursor=0;render();});
$('position').addEventListener('input',()=>{stop();$('follow').checked=false;cursor=Number($('position').value);render();});
$('follow').addEventListener('change',()=>{stop();if($('follow').checked){cursor=maxSteps();render();}});
$('download').addEventListener('click',async()=>{
 if(!data)return;const snapshot=data,format=$('export-format').value;
 try{
  let blob;
  if(format==='json')blob=new Blob([JSON.stringify({projection_version:'arena-public-v2',...snapshot},null,2)],{type:'application/json'});
  else {const response=await fetch(`/api/runs/${encodeURIComponent(snapshot.run_id)}/export.${format}`);if(!response.ok)throw new Error('No se pudo exportar la ejecución.');blob=await response.blob();}
  const url=URL.createObjectURL(blob),a=el('a');a.href=url;a.download=`arena-${snapshot.run_id}.${format}`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }catch(e){error(e);}
});
setInterval(async()=>{if(!$('follow').checked||fetching)return;fetching=true;try{await loadSelected();}catch(e){error(e);}finally{fetching=false;}},2000);
(async()=>{try{await loadRuns();await loadSelected(true);}catch(e){error(e);}})();
