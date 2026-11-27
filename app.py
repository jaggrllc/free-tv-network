import streamlit as st
import requests
import openai
import json
import os

st.set_page_config(page_title="Spelunkr Clone Helper", layout="wide")
st.title("🎬 Spelunkr-style Channel Player Generator")

# Load channels.json if it exists
CHANNELS = []
if os.path.exists("channels.json"):
    try:
        with open("channels.json", "r") as f:
            CHANNELS = json.load(f)
        st.success(f"Loaded {len(CHANNELS)} channels from channels.json")
    except Exception as e:
        st.error(f"Could not load channels.json: {e}")
else:
    st.info("channels.json not found. Generate it with generate_channels.py and commit it to the repo.")

# Session state
if "custom_instructions" not in st.session_state:
    st.session_state.custom_instructions = "Make a simple dark-themed 90s-style player."
if "selected_channel" not in st.session_state:
    st.session_state.selected_channel = None
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "last_mp4_url" not in st.session_state:
    st.session_state.last_mp4_url = ""

with st.sidebar:
    st.header("API Keys")
    openai_key = st.text_input("OpenAI API Key", type="password")

st.subheader("Custom Instructions (remembered in this session)")
st.session_state.custom_instructions = st.text_area(
    "Instructions for the generated player:",
    value=st.session_state.custom_instructions,
    height=150
)

if CHANNELS:
    channel_options = [f"{c['channel_number']}: {c['name']}" for c in CHANNELS]
    selected = st.selectbox("Choose a channel", channel_options)
    idx = channel_options.index(selected)
    channel = CHANNELS[idx]
    st.session_state.selected_channel = channel

    st.write(f"**Topic:** {channel.get('topic', 'N/A')}")
    st.write("**Videos in this channel:**")
    for i, v in enumerate(channel["videos"], 1):
        st.write(f"{i}. {v['title']} — {v['duration']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Player from Channel"):
            if not openai_key:
                st.error("Enter OpenAI key")
                st.stop()
            # Use the first video by default
            best_url = channel["videos"][0]["url"]
            st.session_state.last_mp4_url = best_url
            # Generate code (simplified; expand with your previous OpenAI logic)
            st.session_state.generated_code = f"""
<video controls width="640" height="360" style="background:#000;border:4px solid #ff00ff;">
  <source src="{best_url}" type="video/mp4">
  Your browser does not support the video tag.
</video>
<p>Now playing on {channel['name']}</p>
"""
    with col2:
        if st.button("UPDATE PLAYER (latest MP4)"):
            if not channel:
                st.warning("Select a channel first")
                st.stop()
            # Real-time check using the identifier
            identifier = channel.get("identifier")
            if identifier:
                meta = requests.get(f"https://archive.org/metadata/{identifier}", timeout=15).json()
                # ... (reuse previous get_best_mp4 logic here)
                st.info("Live check completed (implement full logic as needed).")
else:
    st.warning("Add channels.json to the repo to enable channel selection.")

if st.session_state.generated_code:
    st.subheader("Generated HTML5 Player Code")
    st.code(st.session_state.generated_code, language="html")
    st.components.v1.html(st.session_state.generated_code, height=400)
