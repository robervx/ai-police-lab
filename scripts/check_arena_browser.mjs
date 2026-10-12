// Chrome must be running with --remote-debugging-port=9222 and a temporary profile.
// node scripts/check_arena_browser.mjs [arena URL] [screenshot path] [2|4]
import {writeFile} from 'node:fs/promises';
const base=process.argv[2]||'http://127.0.0.1:8765';
const count=Number(process.argv[4]||4);
if(![2,4].includes(count))throw new Error('Expected 2 or 4 participants');
const pages=await (await fetch('http://127.0.0.1:9222/json')).json();
const page=pages.find(p=>p.type==='page');
if(!page)throw new Error('No Chrome page');
const ws=new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let next=0;const pending=new Map(),errors=[];
ws.onmessage=({data})=>{const event=JSON.parse(data);if(event.id){const {resolve,reject}=pending.get(event.id);pending.delete(event.id);event.error?reject(event.error):resolve(event.result);}else if(event.method==='Runtime.exceptionThrown'){errors.push(event.params.exceptionDetails.text);}};
function command(method,params={}){return new Promise((resolve,reject)=>{const id=++next;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const result=await command('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(result.exceptionDetails)throw new Error(JSON.stringify(result.exceptionDetails));return result.result.value;}
async function until(expression){for(let i=0;i<100;i++){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,100));}throw new Error('Timeout: '+expression);}
function assert(value,message){if(!value)throw new Error(message);}
try{
 await command('Runtime.enable');await command('Page.enable');
 await command('Emulation.setDeviceMetricsOverride',{width:1800,height:1100,deviceScaleFactor:1,mobile:false});
 await command('Page.navigate',{url:base});
 await until('document.readyState === "complete" && !!document.getElementById("demo")');
 await evaluate(`document.getElementById('demo-size').value='${count}';document.getElementById('demo').click()`);
 await until('document.getElementById("message").textContent.startsWith("Demo guardada")');
 assert(await evaluate(`document.querySelectorAll('.lane-header').length===${count}`),'Expected lanes');
 await evaluate('document.getElementById("step").click()');
 assert(await evaluate(`document.querySelectorAll('.event').length===${count}`),'Step shows one event each');
 await evaluate('document.getElementById("play").click()');
 await until('Number(document.getElementById("position").value)>=3');
 await evaluate('document.getElementById("play").click()');
 assert(await evaluate('document.getElementById("play").textContent.includes("Reproducir")'),'Pause control');
 await evaluate('const slider=document.getElementById("position");slider.value=slider.max;slider.dispatchEvent(new Event("input"))');
 assert(await evaluate(`document.querySelectorAll('.session_closed').length===${count}`),'Seek reaches all closures');
 assert(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),'No desktop horizontal overflow');
 if(process.argv[3]){const shot=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await writeFile(process.argv[3],Buffer.from(shot.data,'base64'));}
 await command('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 assert(await evaluate('document.documentElement.scrollWidth<=window.innerWidth'),'No mobile horizontal overflow');
 await evaluate('document.getElementById("reset").click()');
 assert(await evaluate('document.querySelectorAll(".event").length===0'),'Reset clears events');
 // Capture the real download handler's Blob without saving to a personal profile.
 await evaluate(`window.exported=[];window.originalCreateURL=URL.createObjectURL;URL.createObjectURL=function(blob){window.exported.push(blob);return window.originalCreateURL(blob)};HTMLAnchorElement.prototype.click=function(){window.downloadName=this.download};`);
 for(const format of ['json','jsonl','csv']){
  await evaluate(`window.exported=[];document.getElementById('export-format').value='${format}';document.getElementById('download').click()`);
  await until('window.exported.length===1');
  const content=await evaluate('window.exported[0].text()');
  assert(await evaluate(`window.downloadName.endsWith('.${format}')`),'Download extension');
  if(format==='json')assert(JSON.parse(content).lanes.length===count,'JSON lanes');
  if(format==='jsonl'){
   const rows=content.trim().split('\n').map(line=>JSON.parse(line));
   assert(rows.filter(row=>row.record_type==='participant').length===count,'JSONL participant rows');
   assert(rows.filter(row=>row.event_type==='session_closed').length===count,'JSONL complete export after reset');
  }
  if(format==='csv')assert(content.startsWith('record_type,projection_version,run_id,participant_id,'),'CSV schema');
  assert(!['provider_request','citizen_diagnostic','truth_private'].some(key=>content.includes(key)),'Private events excluded');
 }
 // Force a failed selection and confirm no stale lane/export survives.
 await evaluate(`const select=document.getElementById('runs');select.append(new Option('Missing','00000000-0000-0000-0000-000000000000'));select.value='00000000-0000-0000-0000-000000000000';select.dispatchEvent(new Event('change'));`);
 await until('document.getElementById("message").textContent.includes("No se pudo")');
 assert(await evaluate('document.querySelectorAll(".lane-header").length===0 && document.getElementById("download").disabled'),'Failed selection clears stale data');
 assert(errors.length===0,'No browser exceptions: '+errors.join(','));
 console.log(`Chrome: ${count} lanes, step, play/pause, seek, reset, responsive layout, JSON/JSONL/CSV downloads and failed-selection isolation passed.`);
}finally{ws.close();}
