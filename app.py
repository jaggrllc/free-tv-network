import streamlit as st
import requests
import openai
import serpapi
import json

st.set_page_config(page_title="Spelunkr Clone Helper", layout="wide")
st.title("🎬 Spelunkr-style Internet Archive MP4 Player Generator")

# --- Secret keys in the sidebar ---
with st.sidebar:
    st.header("API Keys")
    openai_key = st.text_input("OpenAI API Key", type="password")
    serpapi_key = st.text_input("SerpAPI Key", type="password")
    st.caption("These stay only in your browser session.")

# --- Big customization text box ---
st.subheader("Customize the robot's job")
custom_instructions = st.text_area(
    "Write a big note here (anything you want the app to do or how the player should look/behave):",
    height=200,
    placeholder="Example: Make a simple dark-themed player with autoplay off, show the title, and only use the best MP4. Also list 3 similar Archive items."
)

# --- Search / Identifier ---
col1, col2 = st.columns(2)
with col1:
    search_query = st.text_input("Search Internet Archive for movies", "vhs cartoon")
with col2:
    item_identifier = st.text_input("Or paste a specific Archive identifier", "")

if st.button("Check current MP4s & Generate Player Code"):
    if not openai_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    # 1. Search or use identifier
    if item_identifier:
        identifier = item_identifier.strip()
    else:
        # Simple search via Archive advancedsearch
        params = {
            "q": f"{search_query} AND mediatype:movies",
            "fl[]": "identifier,title",
            "rows": 5,
            "output": "json"
        }
        r = requests.get("https://archive.org/advancedsearch.php", params=params)
        data = r.json()
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            st.warning("No results found.")
            st.stop()
        identifier = docs[0]["identifier"]
        st.info(f"Using first result: {docs[0].get('title', identifier)}")

    # 2. Check current files (this keeps it "abreast" of availability)
    meta_url = f"https://archive.org/metadata/{identifier}"
    meta = requests.get(meta_url).json()
    files = meta.get("files", [])

    playable = []
    for f in files:
        name = f.get("name", "")
        fmt = f.get("format", "").lower()
        size = int(f.get("size", 0) or 0)
        if size > 0 and name.lower().endswith(".mp4") and any(x in fmt for x in ["h.264", "mpeg4", "mp4"]):
            url = f"https://archive.org/download/{identifier}/{name}"
            playable.append({"name": name, "url": url, "size": size})

    if not playable:
        st.error("No ready-to-play MP4 found right now for this item.")
        st.stop()

    best = max(playable, key=lambda x: x["size"])  # biggest (usually best quality)
    st.success(f"Found playable MP4: {best['name']}")
    st.write(best["url"])

    # Optional SerpAPI search (example: related info)
    if serpapi_key:
        try:
            client = serpapi.Client(api_key=serpapi_key)
            serp_results = client.search({"engine": "google", "q": f"Internet Archive {identifier}"})
            st.expander("SerpAPI related results").write(serp_results.get("organic_results", [])[:3])
        except Exception as e:
            st.warning(f"SerpAPI skipped: {e}")

    # 3. Ask OpenAI to generate customized HTML5 player code
    openai.api_key = openai_key
    prompt = f"""
You are helping build a Spelunkr-style embed.
User custom instructions:
{custom_instructions}

Current best MP4 URL from Internet Archive (checked live):
{best['url']}

Title/identifier: {identifier}

Generate clean, ready-to-copy HTML5 <video> player code that embeds this MP4.
Follow the user's custom instructions exactly.
Also give a short note about current availability.
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    generated = response.choices[0].message.content

    st.subheader("Generated HTML5 Player Code")
    st.code(generated, language="html")

    st.subheader("Preview (if the browser allows)")
    st.components.v1.html(generated, height=400)
