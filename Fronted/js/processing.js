/* ═══════════════════════════════════════════
   PROCESSING VISUALIZATIONS — the showstopper
   Uses ECharts + canvas. Animated step-by-step.
   ═══════════════════════════════════════════ */

const STEPS = ['Loading Audio', 'Preprocessing', 'MFCC Extraction', 'ECapa Embedding', 'Packaging .whl'];
let stepIndex = 0;
let elapsed = 0;
let progress = 0;

function startProcessing() {
  // elapsed timer
  setInterval(() => {
    elapsed += 0.1;
    const el = document.getElementById('elapsed');
    if (el) el.textContent = elapsed.toFixed(1) + 's';
  }, 100);

  // progress + step advance
  const stepInterval = setInterval(() => {
    progress = Math.min(100, progress + Math.random() * 6 + 3);
    updateProgress();
    if (progress > (stepIndex + 1) * 20 && stepIndex < STEPS.length - 1) {
      completeStep(stepIndex);
      stepIndex++;
      activateStep(stepIndex);
    }
    if (progress >= 100) {
      clearInterval(stepInterval);
      completeStep(STEPS.length - 1);
      setTimeout(showComplete, 800);
    }
  }, 600);

  // kick off visuals
  renderMFCC();
  renderWaveform();
  renderPitch();
  renderEmbeddingBars();
  renderUMAP();
}

function updateProgress() {
  const bar = document.getElementById('progress-bar');
  const pct = document.getElementById('progress-pct');
  if (bar) bar.style.width = Math.round(progress) + '%';
  if (pct) pct.textContent = Math.round(progress) + '%';
}

function activateStep(i) {
  const row = document.querySelector(`.proc-step[data-i="${i}"]`);
  if (!row) return;
  row.classList.add('active');
  row.querySelector('.proc-dot').innerHTML = '<span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>';
}

function completeStep(i) {
  const row = document.querySelector(`.proc-step[data-i="${i}"]`);
  if (!row) return;
  row.classList.remove('active');
  row.classList.add('done');
  row.querySelector('.proc-dot').innerHTML = '<i class="fa-solid fa-check text-xs"></i>';
}

function showComplete() {
  const cta = document.getElementById('complete-cta');
  if (cta) cta.classList.remove('hidden');
}

/* ── Panel 1: MFCC Heatmap (canvas, draws column by column) ── */
function renderMFCC() {
  const canvas = document.getElementById('mfcc-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width = canvas.clientWidth;
  const H = canvas.height = canvas.clientHeight;
  const rows = 13, cols = 60;
  const cw = W / cols, ch = H / rows;
  let col = 0;

  function colorFor(v) {
    // dark blue -> cyan -> yellow -> red
    if (v < 0.33) return `rgb(${20},${Math.floor(80+v*300)},${Math.floor(120+v*300)})`;
    if (v < 0.66) return `rgb(${Math.floor(v*255)},${Math.floor(200+v*55)},${Math.floor(80)})`;
    return `rgb(255,${Math.floor(200-(v-0.66)*400)},40)`;
  }

  const grid = [];
  for (let r=0;r<rows;r++){ grid[r]=[]; for(let c=0;c<cols;c++){ grid[r][c]=Math.abs(Math.sin(r*0.5+c*0.2)+Math.random()*0.6); } }

  const iv = setInterval(() => {
    if (col >= cols) { clearInterval(iv); return; }
    for (let r=0;r<rows;r++){
      ctx.fillStyle = colorFor(Math.min(1, grid[r][col]));
      ctx.fillRect(col*cw, r*ch, cw+1, ch+1);
    }
    col++;
  }, 35);
}

/* ── Panel 2: Waveform + Energy (ECharts) ── */
function renderWaveform() {
  const el = document.getElementById('waveform-chart');
  if (!el || typeof echarts === 'undefined') return;
  const chart = echarts.init(el);
  const n = 120;
  const wave = [], energy = [];
  for (let i=0;i<n;i++){
    const w = Math.sin(i*0.3)*Math.sin(i*0.05)*0.8 + (Math.random()-0.5)*0.3;
    wave.push(w);
    energy.push(Math.abs(w)*0.7);
  }
  chart.setOption({
    grid: { left: 8, right: 8, top: 10, bottom: 10 },
    xAxis: { type:'category', show:false, data: wave.map((_,i)=>i) },
    yAxis: { type:'value', min:-1, max:1, axisLine:{show:false}, splitLine:{lineStyle:{color:'rgba(255,255,255,0.06)'}}, axisLabel:{show:false} },
    series: [
      { type:'line', data:energy, areaStyle:{color:'rgba(99,102,241,0.3)'}, lineStyle:{width:0}, symbol:'none', smooth:true },
      { type:'line', data:wave, lineStyle:{color:'#00D4FF',width:1.2}, symbol:'none', smooth:false },
    ],
    animationDuration: 1500,
  });
  window.addEventListener('resize',()=>chart.resize());
}

/* ── Panel 3: Pitch Contour F0 (ECharts, animated draw) ── */
function renderPitch() {
  const el = document.getElementById('pitch-chart');
  if (!el || typeof echarts === 'undefined') return;
  const chart = echarts.init(el);
  const n=80, data=[];
  for(let i=0;i<n;i++){ data.push(120 + Math.sin(i*0.15)*40 + Math.sin(i*0.04)*30 + (Math.random()-0.5)*8); }
  chart.setOption({
    grid:{left:8,right:8,top:10,bottom:10},
    xAxis:{type:'category',show:false,data:data.map((_,i)=>i)},
    yAxis:{type:'value',min:60,max:240,axisLine:{show:false},splitLine:{lineStyle:{color:'rgba(255,255,255,0.06)'}},axisLabel:{show:false}},
    series:[{type:'line',data,lineStyle:{color:'#F59E0B',width:2.5},symbol:'none',smooth:true,
      areaStyle:{color:'rgba(245,158,11,0.08)'}}],
    animationDuration:2200, animationEasing:'cubicOut',
  });
  window.addEventListener('resize',()=>chart.resize());
}

/* ── Panel 4: Embedding 192-dim bars (canvas, staggered) ── */
function renderEmbeddingBars() {
  const wrap = document.getElementById('embed-bars');
  if (!wrap) return;
  const N = 192;
  const vals = [];
  for (let i=0;i<N;i++){ vals.push((Math.random()-0.5)*2); }
  for (let i=0;i<N;i++){
    const bar = document.createElement('span');
    const v = vals[i];
    const h = Math.abs(v)*100;
    bar.style.cssText = `display:inline-block;width:100%;border-radius:1px;height:0;transition:height .3s ease;` +
      (v>=0 ? 'background:#00D4FF;align-self:flex-end;' : 'background:#EC4899;align-self:flex-start;');
    bar.dataset.h = h;
    wrap.appendChild(bar);
    setTimeout(()=>{ bar.style.height = (5+h*0.45)+'%'; }, i*12);
  }
}

/* ── UMAP scatter (ECharts) ── */
function renderUMAP() {
  const el = document.getElementById('umap-chart');
  if (!el || typeof echarts === 'undefined') return;
  const chart = echarts.init(el);
  const pop=[], sim=[];
  for(let i=0;i<260;i++){ pop.push([Math.random()*100-50, Math.random()*100-50]); }
  for(let i=0;i<40;i++){ sim.push([18+Math.random()*14, 12+Math.random()*14]); }
  chart.setOption({
    grid:{left:10,right:10,top:10,bottom:10},
    xAxis:{show:false,min:-55,max:55},
    yAxis:{show:false,min:-55,max:55},
    series:[
      {name:'Population',type:'scatter',symbolSize:5,data:pop,itemStyle:{color:'rgba(148,163,184,0.35)'}},
      {name:'Similar speakers',type:'scatter',symbolSize:7,data:sim,itemStyle:{color:'rgba(168,85,247,0.65)'}},
      {name:'Your voiceprint',type:'scatter',symbolSize:22,symbol:'pin',data:[[25,19]],
        itemStyle:{color:'#00D4FF',shadowBlur:20,shadowColor:'#00D4FF'}},
    ],
    animationDuration:1800,
  });
  window.addEventListener('resize',()=>chart.resize());
}
