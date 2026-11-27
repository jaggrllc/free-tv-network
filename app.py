import streamlit as st
import json
import os

st.set_page_config(page_title="Channel Player", layout="wide")
st.title("🎬 Channel Player")

# Load channels.json
CHANNELS = []
if os.path.exists("channels.json"):
    try:
        with open("channels.json", "r") as f:
            CHANNELS = json.load(f)
        st.success(f"Loaded {len(CHANNELS)} channel(s)")
    except Exception as e:
        st.error(f"Could not load channels.json: {e}")
else:
    st.error("channels.json not found in the repo.")

if not CHANNELS:
    st.stop()

# Pick a channel
options = [f"{c['channel_number']}: {c['name']}" for c in CHANNELS]
choice = st.selectbox("Choose a channel", options)
channel = CHANNELS[options.index(choice)]

st.write(f"**Name:** {channel['name']}")
st.write(f"**Identifier:** {channel.get('identifier', 'N/A')}")

# Show the videos and a player
if channel.get("videos"):
    video = channel["videos"][0]  # Use the first video
    url = video["url"]
    title = video.get("title", "Video")
    duration = video.get("duration", "")

    st.subheader(f"Now Playing: {title}")
    if duration:
        st.caption(f"Duration: {duration}")

    # Native Streamlit video player (most reliable)
    st.video(url)

    # Also show the HTML5 code you can copy
    html_code = f'''<video controls width="640" height="360">
  <source src="{url}" type="video/mp4">
  Your browser does not support the video tag.
</video>'''
    st.subheader("HTML5 Embed Code")
    st.code(html_code, language="html")
else:
    st.warning("No videos found in this channel.")
