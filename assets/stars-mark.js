/* Dots that become the logo (homepage, local study).
   Only at the end of the page: as the CTA band scrolls in, small brand-coloured dots appear around it and each one takes its place in the Σύνοιδα logo;
   the real image then fades in on top and the dots leave.
   The canvas is part of the page (absolute, not fixed), so it scrolls natively with the band: the dots form the logo exactly where the image sits, with no lag.
   No-op with reduced motion, without canvas, or when .cta-mark is absent (the static logo stays visible). */
(function(){
  var mark=document.querySelector('.cta-mark'), img=mark&&mark.querySelector('img'), band=mark&&mark.closest('section');
  if(!mark||!img||!band||!window.requestAnimationFrame) return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var cv=document.createElement('canvas'), g=cv.getContext&&cv.getContext('2d'); if(!g) return;
  cv.className='starfield'; cv.setAttribute('aria-hidden','true');

  var PAL=['#8DC63F','#ED1C24','#00AEEF','#F7941D','#58595B'], RGB=[[141,198,63],[237,28,36],[0,174,239],[247,148,29],[88,89,91]];
  var W=0,CH=0,dpr=1,P=[],t0=0,ready=false,cvTop=-1,lastM=-1,ms=-1,last=0;
  function nearest(r,gr,b){ var best=0,bd=1e9; for(var i=0;i<RGB.length;i++){ var d=(r-RGB[i][0])*(r-RGB[i][0])+(gr-RGB[i][1])*(gr-RGB[i][1])+(b-RGB[i][2])*(b-RGB[i][2]); if(d<bd){bd=d;best=i;} } return best; }

  function build(){
    /* targets: opaque, non-white pixels of the logo, picked at random with sub-pixel jitter so the dots never line up in a grid */
    var sw=210, sh=Math.round(sw*img.naturalHeight/img.naturalWidth), oc=document.createElement('canvas'); oc.width=sw; oc.height=sh;
    var og=oc.getContext('2d'); og.drawImage(img,0,0,sw,sh); var d;
    try{ d=og.getImageData(0,0,sw,sh).data; }catch(e){ return false; }
    var pts=[], step=1;
    for(var y=0;y<sh;y+=step) for(var x=0;x<sw;x+=step){ var i=(y*sw+x)*4; if(d[i+3]<140) continue; if(d[i]>235&&d[i+1]>235&&d[i+2]>235) continue;
      pts.push([(x+Math.random())/sw,(y+Math.random())/sh,nearest(d[i],d[i+1],d[i+2])]); }
    var max=window.innerWidth<768?1300:2600; 
    if(pts.length>max){ for(var n=0;n<max;n++){ var j=n+Math.floor(Math.random()*(pts.length-n)), q=pts[n]; pts[n]=pts[j]; pts[j]=q; } pts.length=max; }
    P=pts.map(function(t){ var z=0.2+0.8*Math.pow(Math.random(),1.6);
      return {tx:t[0],ty:t[1],c:t[2],s:Math.floor(Math.random()*4),hx:Math.random(),hy:Math.random(),z:z,d:Math.random(),ph:Math.random()*6.283,sw:(Math.random()-.5)*2}; });
    return P.length>0;
  }
  /* the canvas covers the band plus some page above it, in document coordinates */
  function layout(){
    var vh=window.innerHeight, b=band.getBoundingClientRect(), lead=Math.round(vh*0.6), top=Math.round(b.top+window.scrollY-lead), w=document.documentElement.clientWidth, h=Math.round(b.height+lead);
    if(top===cvTop&&w===W&&h===CH) return; cvTop=top; W=w; CH=h; dpr=Math.min(window.devicePixelRatio||1,2);
    cv.style.top=top+'px'; cv.style.width=w+'px'; cv.style.height=h+'px'; cv.width=Math.round(w*dpr); cv.height=Math.round(h*dpr); g.setTransform(dpr,0,0,dpr,0,0); lastM=-1;
  }
  function ease(x){ return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2; }

  function draw(ts){
    requestAnimationFrame(draw); if(document.hidden||!ready) return;
    if(!t0) t0=ts; var t=(ts-t0)/1000, vh=window.innerHeight; layout();
    var c0=cv.getBoundingClientRect(), r=mark.getBoundingClientRect();
    /* 0 nothing yet … 1 logo. Starts once the mark is well inside the screen (88%), done when it sits near the top, at 18% (or wherever the page ends, if sooner) */
    var low=r.top+window.scrollY-(document.documentElement.scrollHeight-vh), end=Math.max(vh*0.18,low+24), span=Math.max(vh*0.88-end,vh*0.3), m=Math.min(Math.max((end+span-r.top)/span,0),1);
    /* unhurried: the animation trails the scroll a little, so even a fast flick plays out calmly. Only progress trails; positions never do. */
    var dt=Math.min((ts-(last||ts))/1000,0.1); last=ts; if(ms<0) ms=m; ms+=(m-ms)*(1-Math.exp(-dt*2.2)); if(Math.abs(m-ms)<0.0015) ms=m; m=ms;
    /* the logo itself is always the real image: it condenses out of the swarm (soft, then sharp) as the dots pour in.
       Each dot melts into it on arrival, so there is never a logo made of dots. */
    var im=Math.min(Math.max((m-0.3)/0.62,0),1); im=im*im*(3-2*im); img.style.opacity=im.toFixed(3); img.style.filter=im<1?'blur('+((1-im)*9).toFixed(1)+'px)':'';
    if(c0.bottom<0||c0.top>vh||m<=0||m>=1){ if(lastM!==m){ g.clearRect(0,0,W,CH); lastM=m; } return; }
    lastM=m;
    var L=r.left-c0.left, T=r.top-c0.top, dot=Math.max(r.width/210*0.95,0.9);   /* constant while scrolling: canvas and mark move together */
    var show=Math.min(m/0.15,1);
    g.clearRect(0,0,W,CH);
    for(var i=0;i<P.length;i++){ var p=P[i];
      var c=ease(Math.min(Math.max((m-p.d*0.36)/0.6,0),1)), free=1-c;   /* dots keep pouring in over the whole span; the last lands at m=0.96 */
      var sx=p.hx*W+Math.sin(t*0.25+p.ph)*10*p.z*free, sy=p.hy*CH+(1-m)*p.z*140;
      var tx=L+p.tx*r.width, ty=T+p.ty*r.height, bend=Math.sin(c*Math.PI)*p.sw*W*0.08;
      var x=sx+(tx-sx)*c+bend, y=sy+(ty-sy)*c-Math.abs(bend)*0.3;
      var tw=1-0.3*free*(0.5+0.5*Math.sin(t*1.4+p.ph*3)), a=Math.min(0.3+0.55*p.z+0.3*c,1)*tw*show*(1-c*c*c*c), rad=(0.9+2.1*p.z)*free+dot*c;   /* brightens on the way in, gone on arrival */
      if(a<0.01) continue;
      /* a free dot wears a bright brand colour; it takes its logo colour (grey for the wordmark) on the way in */
      var k=p.s===p.c?1:Math.min(Math.max((c-0.35)/0.5,0),1);
      if(k<1){ g.globalAlpha=a*(1-k); g.fillStyle=PAL[p.s]; g.beginPath(); g.arc(x,y,rad,0,6.283); g.fill(); }
      if(k>0){ g.globalAlpha=a*k; g.fillStyle=PAL[p.c]; g.beginPath(); g.arc(x,y,rad,0,6.283); g.fill(); } }
    g.globalAlpha=1;
  }
  function start(){ if(ready||!build()) return; document.documentElement.classList.add('stars-on'); document.body.appendChild(cv); layout(); ready=true; requestAnimationFrame(draw); }
  /* the CTA image is lazy; fetch it now so the targets exist before the visitor gets there */
  img.loading='eager'; if(img.complete&&img.naturalWidth) start(); else img.addEventListener('load',start);
})();
