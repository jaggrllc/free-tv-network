import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TV Channel Player", layout="wide")

st.title("TV Channel MP4 Player")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body { background: #111; color: #eee; font-family: system-ui, sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; padding: 20px; }
  .tv { background: linear-gradient(145deg, #2a2a2a, #1a1a1a); border-radius: 18px; padding: 22px 22px 28px; box-shadow: 0 10px 40px rgba(0,0,0,.7), inset 0 0 0 4px #444; }
  .screen { position: relative; width: min(90vw, 800px); aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; }
  video { width: 100%; height: 100%; object-fit: contain; }
  .channel-title { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,.75); color: #fff; padding: 10px 24px; border-radius: 8px; font-size: 1.4rem; font-weight: 600; opacity: 0; transition: opacity 0.4s; pointer-events: none; z-index: 10; }
  .channel-title.visible { opacity: 1; }
  .clock { font-family: 'Courier New', monospace; font-size: 1.8rem; font-weight: bold; color: #0f0; background: #000; padding: 6px 18px; border-radius: 6px; border: 2px solid #333; margin-top: 12px; letter-spacing: 2px; text-align: center; }
  .channels { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 16px; }
  .ch-btn { background: #333; color: #fff; border: 1px solid #555; padding: 10px 16px; border-radius: 6px; cursor: pointer; }
  .ch-btn:hover, .ch-btn.active { background: #0a7; }
</style>
</head>
<body>
  <div class="tv">
    <div class="screen">
      <video id="player" playsinline controls></video>
      <div id="titleOverlay" class="channel-title"></div>
    </div>
  </div>
  <div id="clock" class="clock">--:--:--</div>
  <div class="channels" id="channelButtons"></div>

<script>
const channels = [
  { title: "Big Buck Bunny", src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" },
  { title: "Elephant Dream", src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" },
  { title: "Sintel", src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4" },
  { title: "Tears of Steel", src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" }
];

const video = document.getElementById('player');
const titleOverlay = document.getElementById('titleOverlay');
const clockEl = document.getElementById('clock');
const buttonsContainer = document.getElementById('channelButtons');
let titleTimeout = null;
let currentIndex = -1;

function updateClock() {
  clockEl.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
setInterval(updateClock, 1000);
updateClock();

function showTitle(title) {
  titleOverlay.textContent = title;
  titleOverlay.classList.add('visible');
  clearTimeout(titleTimeout);
  titleTimeout = setTimeout(() => titleOverlay.classList.remove('visible'), 15000);
}

function activateChannel(index) {
  if (index === currentIndex) return;
  currentIndex = index;
  const ch = channels[index];
  video.src = ch.src;
  video.load();
  video.play().catch(() => {});
  showTitle(ch.title);
  document.querySelectorAll('.ch-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
}

channels.forEach((ch, i) => {
  const btn = document.createElement('button');
  btn.className = 'ch-btn';
  btn.textContent = `CH ${i + 1}: ${ch.title}`;
  btn.onclick = () => activateChannel(i);
  buttonsContainer.appendChild(btn);
});
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)

st.caption("Channel title appears for 15 seconds after activation. Clock shows your local time.")

Deployment steps (GitHub + Streamlit Cloud only)

    Create a new public GitHub repository.
    Add the file above as app.py (and a simple requirements.txt containing just streamlit).
    Go to share.streamlit.io, sign in with GitHub, and deploy the repo.
    Streamlit Cloud gives you a public URL. The player (with temporary channel titles and the centered local-time clock) runs entirely in the cloud.

You can later replace the hard-coded channel list with a channels.json fetched from the same repo or any public URL.

Want me to adjust the layout, add more channels, or switch to loading from an external JSON?
Switch to loading from a JSON histed on GitHub.

Updated app.py — loads channels from a JSON file hosted on GitHub (raw URL).

Replace YOUR_USERNAME and YOUR_REPO with your actual GitHub details (or any public raw URL).
python

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TV Channel Player", layout="wide")

st.title("TV Channel MP4 Player")

# Change this to your raw GitHub URL for channels.json
CHANNELS_JSON_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/channels.json"

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ background: #111; color: #eee; font-family: system-ui, sans-serif; margin: 0; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
  .tv {{ background: linear-gradient(145deg, #2a2a2a, #1a1a1a); border-radius: 18px; padding: 22px 22px 28px; box-shadow: 0 10px 40px rgba(0,0,0,.7), inset 0 0 0 4px #444; }}
  .screen {{ position: relative; width: min(90vw, 800px); aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; }}
  video {{ width: 100%; height: 100%; object-fit: contain; }}
  .channel-title {{ position: absolute; top: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,.75); color: #fff; padding: 10px 24px; border-radius: 8px; font-size: 1.4rem; font-weight: 600; opacity: 0; transition: opacity 0.4s; pointer-events: none; z-index: 10; }}
  .channel-title.visible {{ opacity: 1; }}
  .clock {{ font-family: 'Courier New', monospace; font-size: 1.8rem; font-weight: bold; color: #0f0; background: #000; padding: 6px 18px; border-radius: 6px; border: 2px solid #333; margin-top: 12px; letter-spacing: 2px; text-align: center; }}
  .channels {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 16px; }}
  .ch-btn {{ background: #333; color: #fff; border: 1px solid #555; padding: 10px 16px; border-radius: 6px; cursor: pointer; }}
  .ch-btn:hover, .ch-btn.active {{ background: #0a7; }}
  .status {{ color: #fa0; margin-top: 10px; }}
</style>
</head>
<body>
  <div class="tv">
    <div class="screen">
      <video id="player" playsinline controls></video>
      <div id="titleOverlay" class="channel-title"></div>
    </div>
  </div>
  <div id="clock" class="clock">--:--:--</div>
  <div class="channels" id="channelButtons"></div>
  <div id="status" class="status">Loading channels...</div>

<script>
const CHANNELS_JSON_URL = "{CHANNELS_JSON_URL}";
const video = document.getElementById('player');
const titleOverlay = document.getElementById('titleOverlay');
const clockEl = document.getElementById('clock');
const buttonsContainer = document.getElementById('channelButtons');
const statusEl = document.getElementById('status');
let titleTimeout = null;
let currentIndex = -1;
let channels = [];

function updateClock() {{
  clockEl.textContent = new Date().toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit', second: '2-digit' }});
}}
setInterval(updateClock, 1000);
updateClock();

function showTitle(title) {{
  titleOverlay.textContent = title;
  titleOverlay.classList.add('visible');
  clearTimeout(titleTimeout);
  titleTimeout = setTimeout(() => titleOverlay.classList.remove('visible'), 15000);
}}

function activateChannel(index) {{
  if (index === currentIndex) return;
  currentIndex = index;
  const ch = channels[index];
  video.src = ch.src;
  video.load();
  video.play().catch(() => {{}});
  showTitle(ch.title);
  document.querySelectorAll('.ch-btn').forEach((btn, i) => btn.classList.toggle('active', i === index));
}}

function buildButtons() {{
  buttonsContainer.innerHTML = '';
  channels.forEach((ch, i) => {{
    const btn = document.createElement('button');
    btn.className = 'ch-btn';
    btn.textContent = `CH ${{i + 1}}: ${{ch.title}}`;
    btn.onclick = () => activateChannel(i);
    buttonsContainer.appendChild(btn);
  }});
}}

async function loadChannels() {{
  try {{
    const res = await fetch(CHANNELS_JSON_URL);
    if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
    channels = await res.json();
    if (!Array.isArray(channels)) throw new Error('JSON is not an array');
    statusEl.textContent = `Loaded ${{channels.length}} channels`;
    buildButtons();
  }} catch (err) {{
    statusEl.textContent = `Could not load channels.json: ${{err.message}}`;
    console.error(err);
  }}
}}

loadChannels();
</script>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=True)

st.caption("Channel title shows for 15 seconds after activation. Clock shows your local time. Channels loaded from GitHub.")

Example channels.json (upload to your GitHub repo)
json

[
  {
    "title": "Big Buck Bunny",
    "src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
  },
  {
    "title": "Elephant Dream",
    "src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
  },
  {
    "title": "Sintel",
    "src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
  },
  {
    "title": "Tears of Steel",
    "src": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"
  }
]

Steps

    Add app.py and channels.json to your public GitHub repo.
    Update the CHANNELS_JSON_URL line in app.py to the raw URL of your channels.json (click the file on GitHub → Raw → copy the URL).
    Deploy / redeploy on Streamlit Community Cloud (linked to the same repo).

The player will fetch the JSON at runtime, show the channel title for 15 seconds on activation, and keep the centered local-time clock below the TV. No local computer needed.

