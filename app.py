import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Retro Cable TV", layout="wide")

# Replace with your raw GitHub URL for channels.json
CHANNELS_JSON_URL = "https://raw.githubusercontent.com/jaggrllc/free-tv-network/main/channels.json"

html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RETRO CABLE TV</title>
<style>
:root {{ --crt: #0a0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #111; color: #eee; font-family: 'Courier New', monospace; }}
.tv-bezel {{ width: 100%; display: flex; flex-direction: column; align-items: center; padding: 10px; }}
.crt {{ width: min(95vw, 1100px); aspect-ratio: 16/9; background: #000; border-radius: 18px; box-shadow: inset 0 0 60px #000, 0 0 30px #000; position: relative; overflow: hidden; }}
video {{ width: 100%; height: 100%; object-fit: contain; }}
#staticCanvas {{ position: absolute; inset: 0; pointer-events: none; display: none; }}
.overlay {{ position: absolute; top: 12px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,.8); padding: 8px 20px; border-radius: 6px; font-size: 1.2rem; opacity: 0; transition: opacity .4s; z-index: 10; }}
.overlay.show {{ opacity: 1; }}
.clock {{ margin-top: 8px; font-size: 1.5rem; color: var(--crt); text-shadow: 0 0 8px var(--crt); }}
.remote {{ display: flex; gap: 10px; margin: 8px 0; flex-wrap: wrap; justify-content: center; }}
button {{ background: #333; color: #fff; border: 2px solid #555; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-family: inherit; }}
button:hover {{ background: #0a7; }}
.guide {{ width: 100%; max-height: 25vh; overflow-y: auto; background: #000c; border-top: 2px solid #333; margin-top: 6px; }}
.guide-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 4px; padding: 6px; }}
.ch-cell {{ background: #222; padding: 6px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }}
.ch-cell:hover, .ch-cell.active {{ background: #0a7; }}
</style>
</head>
<body>
<div class="tv-bezel">
  <div class="crt" id="crt">
    <video id="player" playsinline></video>
    <canvas id="staticCanvas"></canvas>
    <div id="overlay" class="overlay"></div>
  </div>
  <div class="clock" id="clock">--:--:--</div>
  <div class="remote">
    <button id="chDown">CH ▼</button>
    <button id="chUp">CH ▲</button>
    <button id="muteBtn">MUTE</button>
    <button id="surfBtn">AUTO-SURF 15s</button>
  </div>
  <div class="guide"><div class="guide-grid" id="guide"></div></div>
</div>
<script>
const CHANNELS_JSON_URL = "{CHANNELS_JSON_URL}";
const video = document.getElementById('player');
const overlay = document.getElementById('overlay');
const clockEl = document.getElementById('clock');
const canvas = document.getElementById('staticCanvas');
const ctx = canvas.getContext('2d');
let channels = [], currentCh = 0, muted = false, surfTimer = null, titleTimeout = null, audioCtx;

function updateClock() {{ clockEl.textContent = new Date().toLocaleTimeString(); }}
setInterval(updateClock, 1000); updateClock();

function playStatic() {{
  canvas.style.display = 'block';
  canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight;
  const id = setInterval(() => {{
    const img = ctx.createImageData(canvas.width, canvas.height);
    for (let i = 0; i < img.data.length; i += 4) {{
      const v = Math.random() * 255;
      img.data[i] = img.data[i+1] = img.data[i+2] = v; img.data[i+3] = 255;
    }}
    ctx.putImageData(img, 0, 0);
  }}, 50);
  setTimeout(() => {{ clearInterval(id); canvas.style.display = 'none'; }}, 350);
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const buf = audioCtx.createBuffer(1, audioCtx.sampleRate * 0.35, audioCtx.sampleRate);
  const out = buf.getChannelData(0);
  for (let i = 0; i < out.length; i++) out[i] = Math.random() * 2 - 1;
  const src = audioCtx.createBufferSource(); src.buffer = buf; src.connect(audioCtx.destination); src.start();
}}

function showTitle(text) {{
  overlay.textContent = text; overlay.classList.add('show');
  clearTimeout(titleTimeout);
  titleTimeout = setTimeout(() => overlay.classList.remove('show'), 4000);
}}

function getTotalDuration(ch) {{ return ch.playlist.reduce((s, v) => s + (v.duration || 600), 0); }}

function syncToClock(ch) {{
  const total = getTotalDuration(ch);
  const offset = (Date.now() / 1000) % total;
  let acc = 0;
  for (let i = 0; i < ch.playlist.length; i++) {{
    const d = ch.playlist[i].duration || 600;
    if (acc + d > offset) return {{ index: i, time: offset - acc }};
    acc += d;
  }}
  return {{ index: 0, time: 0 }};
}}

function loadChannel(n) {{
  if (n < 0 || n >= channels.length) return;
  currentCh = n;
  playStatic();
  const ch = channels[n];
  showTitle(`You're watching ${{ch.name}}`);
  const {{ index, time }} = syncToClock(ch);
  playItem(ch, index, time);
  document.querySelectorAll('.ch-cell').forEach((c, i) => c.classList.toggle('active', i === n));
}}

function playItem(ch, idx, seek = 0) {{
  if (idx >= ch.playlist.length) idx = 0;
  const item = ch.playlist[idx];
  video.src = item.url;
  video.currentTime = seek;
  video.play().catch(() => {{}});
  video.onended = () => playItem(ch, idx + 1);
  video.onerror = () => playItem(ch, idx + 1);  // automatic failover
}}

async function init() {{
  try {{
    const res = await fetch(CHANNELS_JSON_URL);
    channels = await res.json();
  }} catch (e) {{
    channels = [{{ number: 1, name: "CH 001 – Demo", playlist: [{{ url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", duration: 600 }}] }}];
  }}
  const guide = document.getElementById('guide');
  channels.forEach((ch, i) => {{
    const cell = document.createElement('div');
    cell.className = 'ch-cell';
    cell.textContent = `${{String(ch.number).padStart(3,'0')}} ${{ch.name}}`;
    cell.onclick = () => loadChannel(i);
    guide.appendChild(cell);
  }});
  loadChannel(0);
}}

document.getElementById('chUp').onclick = () => loadChannel((currentCh + 1) % channels.length);
document.getElementById('chDown').onclick = () => loadChannel((currentCh - 1 + channels.length) % channels.length);
document.getElementById('muteBtn').onclick = () => {{ muted = !muted; video.muted = muted; }};
document.getElementById('surfBtn').onclick = () => {{
  if (surfTimer) {{ clearInterval(surfTimer); surfTimer = null; return; }}
  surfTimer = setInterval(() => loadChannel((currentCh + 1) % channels.length), 15000);
}};

let keypad = '';
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowUp') loadChannel((currentCh + 1) % channels.length);
  if (e.key === 'ArrowDown') loadChannel((currentCh - 1 + channels.length) % channels.length);
  if (e.key === 'm' || e.key === 'M') {{ muted = !muted; video.muted = muted; }}
  if (e.key >= '0' && e.key <= '9') {{
    keypad += e.key;
    if (keypad.length === 3) {{
      const num = parseInt(keypad, 10);
      const idx = channels.findIndex(c => c.number === num);
      if (idx !== -1) loadChannel(idx);
      keypad = '';
    }}
  }}
}});

init();
</script>
</body>
</html>
"""

components.html(html, height=980, scrolling=True)
st.caption("Channel title shows briefly. Clock is local time. Channels load from GitHub.")
