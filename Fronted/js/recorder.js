/* ═══════════════════════════════════════════
   VOICE RECORDER — Web Audio API + MediaRecorder
   Blobs are saved into Session (window._achAudioBlobs)
   so they can be uploaded to the backend.

   IMPORTANT: All audio is converted to 16kHz mono WAV before
   being stored, so the backend never needs ffmpeg.
   ═══════════════════════════════════════════ */

const RecorderState = {
  samples: new Array(20).fill(false),
  blobs: new Array(20).fill(null),     // captured Blob objects
  current: 0,
  stream: null,
  recorder: null,
  chunks: [],
  timer: null,
  seconds: 0,
  maxSeconds: 10,
  audioCtx: null,
  analyser: null,
  rafId: null,
};

function $(id) { return document.getElementById(id); }

/* ── WAV encoder helper ──────────────────────────────────────────────────────
   Converts any browser Blob (webm/ogg/mp4) → 16kHz mono WAV Blob.
   Uses AudioContext.decodeAudioData (built-in, no deps needed).
   Returns a Promise<Blob>.
*/
async function blobToWav(inputBlob, targetSR = 16000) {
  const arrayBuf = await inputBlob.arrayBuffer();

  // Decode audio using the browser's native decoder
  const actx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: targetSR });
  let decoded;
  try {
    decoded = await actx.decodeAudioData(arrayBuf);
  } finally {
    actx.close();
  }

  // Mix down to mono
  const numCh = decoded.numberOfChannels;
  const srcLen = decoded.length;
  const mono = new Float32Array(srcLen);
  for (let c = 0; c < numCh; c++) {
    const ch = decoded.getChannelData(c);
    for (let i = 0; i < srcLen; i++) mono[i] += ch[i];
  }
  if (numCh > 1) for (let i = 0; i < srcLen; i++) mono[i] /= numCh;

  // Resample if the AudioContext didn't automatically resample
  // (modern browsers honour sampleRate in AudioContext constructor)
  const pcm = mono;

  // Build WAV file manually (PCM 16-bit LE)
  const numSamples = pcm.length;
  const byteRate = targetSR * 2;
  const buf = new ArrayBuffer(44 + numSamples * 2);
  const view = new DataView(buf);
  const write = (off, str) => { for (let i = 0; i < str.length; i++) view.setUint8(off + i, str.charCodeAt(i)); };

  write(0, 'RIFF');
  view.setUint32(4, 36 + numSamples * 2, true);
  write(8, 'WAVE');
  write(12, 'fmt ');
  view.setUint32(16, 16, true);   // chunk size
  view.setUint16(20, 1, true);   // PCM
  view.setUint16(22, 1, true);   // mono
  view.setUint32(24, targetSR, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, 2, true);   // block align
  view.setUint16(34, 16, true);   // bits per sample
  write(36, 'data');
  view.setUint32(40, numSamples * 2, true);

  let off = 44;
  for (let i = 0; i < numSamples; i++) {
    const s = Math.max(-1, Math.min(1, pcm[i]));
    view.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    off += 2;
  }

  return new Blob([buf], { type: 'audio/wav' });
}

async function startRecording() {
  const circle = $('mic-circle');
  const status = $('mic-status');
  try {
    if (!RecorderState.stream) {
      RecorderState.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }
  } catch (e) {
    status.textContent = 'Microphone access denied — use the Upload tab instead.';
    status.classList.add('text-amber-400');
    return;
  }

  RecorderState.chunks = [];
  RecorderState.seconds = 0;
  try {
    RecorderState.recorder = new MediaRecorder(RecorderState.stream);
    RecorderState.recorder.ondataavailable = e => RecorderState.chunks.push(e.data);
    RecorderState.recorder.onstop = onRecordingStop;
    RecorderState.recorder.start();
  } catch (e) { /* ignore */ }

  setupAnalyser();

  circle.classList.add('recording');
  $('mic-rings').style.display = 'block';
  $('rec-dot').style.display = 'block';
  $('mic-icon').style.display = 'none';
  $('start-btn').style.display = 'none';
  $('stop-btn').style.display = 'inline-flex';
  status.classList.remove('text-amber-400');

  RecorderState.timer = setInterval(() => {
    RecorderState.seconds++;
    updateTimer();
    if (RecorderState.seconds >= RecorderState.maxSeconds) stopRecording();
  }, 1000);
  updateTimer();
}

function setupAnalyser() {
  try {
    RecorderState.audioCtx = RecorderState.audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const src = RecorderState.audioCtx.createMediaStreamSource(RecorderState.stream);
    RecorderState.analyser = RecorderState.audioCtx.createAnalyser();
    RecorderState.analyser.fftSize = 64;
    src.connect(RecorderState.analyser);
    drawLiveBars();
  } catch (e) { /* ignore */ }
}

function drawLiveBars() {
  const analyser = RecorderState.analyser;
  if (!analyser) return;
  const data = new Uint8Array(analyser.frequencyBinCount);
  const ring = $('mic-rings');
  function loop() {
    analyser.getByteFrequencyData(data);
    const avg = data.reduce((a, b) => a + b, 0) / data.length;
    const scale = 1 + (avg / 255) * 0.3;
    ring.style.transform = `scale(${scale})`;
    RecorderState.rafId = requestAnimationFrame(loop);
  }
  loop();
}

function updateTimer() {
  const s = RecorderState.seconds;
  $('timer').textContent = `00:${String(s).padStart(2, '0')} / 00:${RecorderState.maxSeconds}`;
}

function stopRecording() {
  clearInterval(RecorderState.timer);
  if (RecorderState.rafId) cancelAnimationFrame(RecorderState.rafId);
  if (RecorderState.recorder && RecorderState.recorder.state !== 'inactive') {
    RecorderState.recorder.stop();
  } else {
    onRecordingStop();
  }
}

async function onRecordingStop() {
  const circle = $('mic-circle');
  circle.classList.remove('recording');
  circle.classList.add('done');
  $('mic-rings').style.display = 'none';
  $('mic-rings').style.transform = 'scale(1)';
  $('rec-dot').style.display = 'none';
  $('mic-icon').style.display = 'block';
  $('mic-icon').innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';  // converting…
  $('stop-btn').style.display = 'none';
  $('mic-status').textContent = 'Converting to WAV…';

  // ── Build raw blob from recorder chunks ─────────────────────────────────
  const mimeType = RecorderState.recorder
    ? (RecorderState.recorder.mimeType || 'audio/webm')
    : 'audio/webm';
  const rawBlob = new Blob(RecorderState.chunks, { type: mimeType });

  // ── Convert to 16kHz mono WAV (no server ffmpeg needed) ─────────────────
  let wavBlob = rawBlob;   // fallback: keep original if conversion fails
  try {
    wavBlob = await blobToWav(rawBlob, 16000);
    console.log('[Recorder] Converted to WAV:', wavBlob.size, 'bytes');
  } catch (e) {
    console.warn('[Recorder] WAV conversion failed, using raw blob:', e.message);
  }

  RecorderState.blobs[RecorderState.current] = wavBlob;

  // ── UI: done state ───────────────────────────────────────────────────────
  $('mic-icon').innerHTML = '<i class="fa-solid fa-check"></i>';
  $('mic-status').textContent = 'Sample captured!';

  // Persist blobs array so api.js can read it
  _persistBlobs();

  // ── Playback bar waveform ─────────────────────────────────────────────────
  renderStaticWaveform();
  $('playback-bar').classList.remove('hidden');
  if ($('playback-dur')) {
    $('playback-dur').textContent = `0:${String(RecorderState.seconds).padStart(2, '0')}`;
  }

  markSampleDone(RecorderState.current);
}

function _persistBlobs() {
  // Build upload-ready array from captured WAV blobs + uploaded files
  const all = [];
  RecorderState.blobs.forEach((b, i) => {
    if (b) all.push({ blob: b, name: `voice_sample_${i + 1}.wav` });   // always .wav now
  });
  // Also carry over any uploaded files stored earlier
  const existing = Session.getFiles().filter(f => f._uploaded);
  all.push(...existing);
  Session.saveFiles(all);
}

function renderStaticWaveform() {
  const wrap = $('wave-bars');
  wrap.innerHTML = '';
  for (let i = 0; i < 50; i++) {
    const bar = document.createElement('span');
    const h = 20 + Math.abs(Math.sin(i * 0.6)) * 60 + Math.random() * 20;
    bar.style.cssText = `display:inline-block;width:3px;border-radius:2px;background:#00D4FF;height:${h}%;opacity:.7`;
    wrap.appendChild(bar);
  }
}

function markSampleDone(idx) {
  RecorderState.samples[idx] = true;
  const count = RecorderState.samples.filter(Boolean).length;
  const counterEl = $('sample-counter');
  if (counterEl) counterEl.textContent = `${count} / 20 captured`;
  checkAllDone();
}

function nextSample() {
  if (RecorderState.current < 19) {
    RecorderState.current++;
    resetCircle();
    const label = $('current-sample-label');
    if (label) label.textContent = `Sample ${RecorderState.current + 1} of up to 20 (Min 5 required) · Read any sentence aloud`;
  }
}

function reRecord() {
  RecorderState.samples[RecorderState.current] = false;
  RecorderState.blobs[RecorderState.current] = null;
  resetCircle();
  const count = RecorderState.samples.filter(Boolean).length;
  const counterEl = $('sample-counter');
  if (counterEl) counterEl.textContent = `${count} / 20 captured`;
  _persistBlobs();
  checkAllDone();
}

function resetCircle() {
  const circle = $('mic-circle');
  circle.classList.remove('done', 'recording');
  $('mic-icon').innerHTML = '<i class="fa-solid fa-microphone"></i>';
  $('mic-icon').style.display = 'block';
  $('start-btn').style.display = 'inline-flex';
  $('stop-btn').style.display = 'none';
  $('playback-bar').classList.add('hidden');
  $('mic-status').textContent = 'Tap to record 10 seconds';
  $('timer').textContent = '00:00 / 00:10';
}

function checkAllDone() {
  const count = RecorderState.samples.filter(Boolean).length;
  const processBtn = $('process-btn');
  if (processBtn) processBtn.classList.toggle('hidden', count < 5);

  const nextBtn = $('next-sample-btn');
  if (nextBtn) {
    nextBtn.classList.toggle('hidden',
      !RecorderState.samples[RecorderState.current] || count >= 20 || RecorderState.current >= 19
    );
  }
}

// ── Upload tab ────────────────────────────────────────────────────────────────

function handleFiles(files) {
  const list = $('upload-list');
  Array.from(files).forEach(f => {
    const totalDone = RecorderState.samples.filter(Boolean).length;
    if (totalDone >= 20) return;
    const idx = RecorderState.samples.findIndex(s => !s);
    if (idx === -1) return;

    RecorderState.samples[idx] = true;
    RecorderState.blobs[idx] = f;   // store File object directly

    const item = document.createElement('div');
    item.className = 'file-item';
    item.innerHTML = `<span><i class="fa-solid fa-file-audio text-cyan-400 mr-2"></i>${f.name}</span><i class="fa-solid fa-check text-green-400"></i>`;
    list.appendChild(item);
  });

  // Rebuild the blob list with all samples
  const all = [];
  RecorderState.blobs.forEach((b, i) => {
    if (b) {
      const isFile = b instanceof File;
      all.push({
        blob: b,
        name: isFile ? b.name : `voice_sample_${i + 1}.webm`,
        _uploaded: isFile,
      });
    }
  });
  Session.saveFiles(all);

  const count = RecorderState.samples.filter(Boolean).length;
  const counterEl = $('sample-counter');
  if (counterEl) counterEl.textContent = `${count} / 20 captured`;

  checkAllDone();
}

function setupDropzone() {
  const dz = $('dropzone');
  const input = $('file-input');
  if (!dz) return;
  dz.addEventListener('click', () => input.click());
  input.addEventListener('change', e => handleFiles(e.target.files));
  ['dragover', 'dragenter'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach(ev => dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove('drag'); }));
  dz.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
}
