import streamlit as st
import requests
import openai
import serpapi
import json

st.set_page_config(page_title="Spelunkr Clone Helper", layout="wide")
st.title("🎬 Spelunkr-style Internet Archive MP4 Player Generator")

# Initialize session state for stored settings
if "custom_instructions" not in st.session_state:
    st.session_state.custom_instructions = ""
if "search_query" not in st.session_state:
    st.session_state.search_query = "vhs cartoon"
if "item_identifier" not in st.session_state:
    st.session_state.item_identifier = ""
if "last_mp4_url" not in st.session_state:
    st.session_state.last_mp4_url = ""
if "last_identifier" not in st.session_state:
    st.session_state.last_identifier = ""
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""

# --- Secret keys in the sidebar ---
with st.sidebar:
    st.header("API Keys")
    openai_key = st.text_input("OpenAI API Key", type="password")
    serpapi_key = st.text_input("SerpAPI Key", type="password")
    st.caption("These stay only in your browser session.")

# --- Stored customized settings ---
st.subheader("Your Customized Settings")
st.session_state.custom_instructions = st.text_area(
    "Custom instructions (these are remembered while the app is open):",
    value=st.session_state.custom_instructions,
    height=200,
    placeholder="Example: Make a simple dark-themed player with autoplay off, show the title, and only use the best MP4."
)

col1, col2 = st.columns(2)
with col1:
    st.session_state.search_query = st.text_input(
        "Search Internet Archive for movies",
        value=st.session_state.search_query
    )
with col2:
    st.session_state.item_identifier = st.text_input(
        "Or paste a specific Archive identifier",
        value=st.session_state.item_identifier
    )

# Buttons
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    generate_clicked = st.button("Generate / Save Settings & Player")
with col_btn2:
    update_clicked = st.button("UPDATE PLAYER (get latest MP4)")

def get_best_mp4(identifier):
    """Check Internet Archive metadata in real-time and return best MP4."""
    meta_url = f"https://archive.org/metadata/{identifier}"
    try:
        meta = requests.get(meta_url, timeout=15).json()
    except Exception as e:
        st.error(f"Could not reach Internet Archive: {e}")
        return None, None

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
        return None, identifier
    best = max(playable, key=lambda x: x["size"])
    return best, identifier

def generate_player_code(mp4_url, identifier, custom_instructions, openai_key):
    if not openai_key:
        return "Error: OpenAI API key required."
    openai.api_key = openai_key
    prompt = f"""
You are helping build a Spelunkr-style embed.
User custom instructions:
{custom_instructions}

Current best MP4 URL from Internet Archive (checked live):
{mp4_url}

Title/identifier: {identifier}

Generate clean, ready-to-copy HTML5 <video> player code that embeds this MP4.
Follow the user's custom instructions exactly.
Also give a short note about current availability.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI error: {e}"

# --- Generate / Save Settings & Player ---
if generate_clicked:
    if not openai_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    # Resolve identifier
    if st.session_state.item_identifier.strip():
        identifier = st.session_state.item_identifier.strip()
    else:
        params = {
            "q": f"{st.session_state.search_query} AND mediatype:movies",
            "fl[]": "identifier,title",
            "rows": 5,
            "output": "json"
        }
        try:
            r = requests.get("https://archive.org/advancedsearch.php", params=params, timeout=15)
            data = r.json()
            docs = data.get("response", {}).get("docs", [])
            if not docs:
                st.warning("No results found.")
                st.stop()
            identifier = docs[0]["identifier"]
            st.info(f"Using first result: {docs[0].get('title', identifier)}")
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    best, identifier = get_best_mp4(identifier)
    if not best:
        st.error("No ready-to-play MP4 found right now for this item.")
        st.stop()

    st.session_state.last_mp4_url = best["url"]
    st.session_state.last_identifier = identifier
    st.success(f"Found playable MP4: {best['name']}")
    st.write(best["url"])

    # Generate code with stored custom settings
    st.session_state.generated_code = generate_player_code(
        best["url"], identifier, st.session_state.custom_instructions, openai_key
    )

# --- UPDATE PLAYER button (real-time latest MP4) ---
if update_clicked:
    if not st.session_state.last_identifier:
        st.warning("Generate a player first so the app knows which item to update.")
        st.stop()
    if not openai_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    st.info("Checking Internet Archive for the latest MP4 in real-time...")
    best, identifier = get_best_mp4(st.session_state.last_identifier)
    if not best:
        st.error("No ready-to-play MP4 found right now.")
        st.stop()

    st.session_state.last_mp4_url = best["url"]
    st.success(f"Updated! Latest MP4: {best['name']}")
    st.write(best["url"])

    # Regenerate using the stored custom settings
    st.session_state.generated_code = generate_player_code(
        best["url"], identifier, st.session_state.custom_instructions, openai_key
    )

# Optional SerpAPI (unchanged)
if serpapi_key and st.session_state.last_identifier:
    try:
        client = serpapi.Client(api_key=serpapi_key)
        serp_results = client.search({"engine": "google", "q": f"Internet Archive {st.session_state.last_identifier}"})
        with st.expander("SerpAPI related results"):
            st.write(serp_results.get("organic_results", [])[:3])
    except Exception as e:
        st.warning(f"SerpAPI skipped: {e}")

# Display generated code
if st.session_state.generated_code:
    st.subheader("Generated HTML5 Player Code")
    st.code(st.session_state.generated_code, language="html")
    st.subheader("Preview")
    st.components.v1.html(st.session_state.generated_code, height=400)

st.caption("Custom settings are remembered while this Streamlit app session is open. Click UPDATE PLAYER anytime to re-check Internet Archive for the newest MP4 and regenerate the code.")
