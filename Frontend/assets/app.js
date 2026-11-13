/* Phiversity local API helpers */
window.lf={
  async get(p){const r=await fetch(p);if(!r.ok)throw new Error((await r.json().catch(()=>({}))).error||r.status);return r.json()},
  async post(p,body){const r=await fetch(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||r.status);return d},
  el(tag,attrs,children){const n=document.createElement(tag);for(const[k,v]of Object.entries(attrs||{})){if(k==='text')n.textContent=v;else if(k==='html')n.innerHTML=v;else n.setAttribute(k,v)}(children||[]).forEach(c=>n.appendChild(c));return n},
  fmt:s=>Math.round(s)+'s of narration',
  date:t=>new Date(t*1000).toLocaleString(),
  /* poll /api/jobs/{id} until it finishes; onUpdate(job) runs on every tick.
     Returns stop(). onGone() fires if the job can no longer be fetched. */
  watchJob(id,onUpdate,onGone,ms=2000){
    let stopped=false,timer=null;
    const tick=async()=>{
      let job;
      try{job=await lf.get('/api/jobs/'+id)}catch(e){if(!stopped){stopped=true;onGone&&onGone(e)}return}
      if(stopped)return;
      if(onUpdate(job)===false||job.status==='done'||job.status==='error'){stopped=true;return}
      timer=setTimeout(tick,ms);
    };
    tick();
    return()=>{stopped=true;clearTimeout(timer)};
  }
};

/* phi-player: the video previewer used across the app.
   lf.player(host,{src,preload,poster}) builds one self-contained player. */
window.lfPlayer=(host,opts={})=>{
  const video=lf.el('video',{src:opts.src||'',preload:opts.preload||'metadata',playsinline:''});
  if(opts.poster)video.setAttribute('poster',opts.poster);
  const play=lf.el('button',{class:'pp','aria-label':'Play',text:'\u25B6'});
  const cur=lf.el('span',{class:'cur',text:'0:00'});
  const seek=lf.el('input',{class:'seek',type:'range',min:'0',max:'100',step:'0.1',value:'0','aria-label':'Seek'});
  const dur=lf.el('span',{class:'dur',text:'0:00'});
  const mute=lf.el('button',{class:'pm','aria-label':'Mute',text:'\uD83D\uDD0A'});
  const vol=lf.el('input',{class:'vol',type:'range',min:'0',max:'1',step:'0.05',value:'1','aria-label':'Volume'});
  const full=lf.el('button',{class:'pf','aria-label':'Fullscreen',text:'\u26F6'});
  const bar=lf.el('div',{class:'bar'},[play,cur,seek,dur,mute,vol,full]);
  const box=lf.el('div',{class:'phi-player',tabindex:'0'},[video,bar]);
  host.appendChild(box);

  const fmt=s=>{s=Math.floor(s||0);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')};
  const toggle=()=>video.paused?video.play():video.pause();
  play.onclick=toggle; video.onclick=toggle;
  video.onplay =()=>{play.textContent='\u275A\u275A';play.setAttribute('aria-label','Pause')};
  video.onpause=()=>{play.textContent='\u25B6';  play.setAttribute('aria-label','Play')};

  video.onloadedmetadata=()=>dur.textContent=fmt(video.duration);
  video.ontimeupdate=()=>{cur.textContent=fmt(video.currentTime);seek.value=video.duration?video.currentTime/video.duration*100:0};
  seek.oninput=()=>{if(video.duration)video.currentTime=seek.value/100*video.duration};

  vol.oninput=()=>{video.volume=vol.value;video.muted=video.volume===0};
  mute.onclick=()=>video.muted=!video.muted;
  video.onvolumechange=()=>{
    mute.textContent=(video.muted||video.volume===0)?'\uD83D\uDD07':'\uD83D\uDD0A';
    mute.setAttribute('aria-label',video.muted?'Unmute':'Mute');
    vol.value=video.muted?0:video.volume;
  };

  full.onclick=()=>document.fullscreenElement?document.exitFullscreen():box.requestFullscreen();

  box.onkeydown=e=>{
    if(e.target.tagName==='INPUT')return;
    if(e.key===' '){e.preventDefault();toggle()}
    if(e.key==='m'||e.key==='M')video.muted=!video.muted;
    if(e.key==='ArrowRight')video.currentTime+=5;
    if(e.key==='ArrowLeft')video.currentTime-=5;
  };
  return box;
};

