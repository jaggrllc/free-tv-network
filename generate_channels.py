import json
import time
import random
from internetarchive import search_items, get_item

# 500 different retro-themed search topics (short list shown; expand or generate more as needed)
RETRO_TOPICS = [
    "80s cartoons", "90s sitcoms", "public domain movies", "vhs commercials",
    "saturday morning cartoons", "retro anime", "classic sci-fi", "old training films",
    "vintage commercials", "public domain horror", "80s music videos", "educational films 1970s",
    "toonami", "nickelodeon 90s", "disney public domain", "old game shows",
    # ... add more up to 500, or generate them programmatically
] * 50  # Temporary multiplier to reach ~500; replace with real unique list

# Fun 90s-style channel name generators
ADJECTIVES = ["Radical", "Totally", "Awesome", "Funky", "Groovy", "Tubular", "Bodacious", "Wicked", "Fresh", "Cool"]
NOUNS = ["Cartoons", "Zone", "Channel", "TV", "Network", "Block", "Hour", "Show", "Time", "Theater"]

def make_90s_name(topic):
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}: {topic.title()}"

def get_playable_mp4s(identifier, max_videos=5):
    """Return up to max_videos playable MP4s with duration from an item."""
    try:
        item = get_item(identifier)
        videos = []
        for f in item.files:
            name = f.get("name", "")
            fmt = f.get("format", "").lower()
            size = int(f.get("size", 0) or 0)
            length = f.get("length", "unknown")
            if size > 100000 and name.lower().endswith(".mp4") and any(x in fmt for x in ["h.264", "mpeg4", "mp4"]):
                url = f"https://archive.org/download/{identifier}/{name}"
                videos.append({
                    "url": url,
                    "duration": str(length),
                    "title": name
                })
                if len(videos) >= max_videos:
                    break
        return videos
    except Exception as e:
        print(f"Error on {identifier}: {e}")
        return []

def generate_channels(num_channels=500):
    channels = []
    used_identifiers = set()
    topic_idx = 0

    print(f"Generating {num_channels} channels... (this will take a while)")

    while len(channels) < num_channels and topic_idx < len(RETRO_TOPICS):
        topic = RETRO_TOPICS[topic_idx % len(RETRO_TOPICS)]
        topic_idx += 1
        query = f"{topic} AND mediatype:movies AND format:mp4"

        try:
            results = search_items(query, fields=["identifier", "title"], params={"rows": 20})
            for result in results:
                identifier = result["identifier"]
                if identifier in used_identifiers:
                    continue
                videos = get_playable_mp4s(identifier, max_videos=5)
                if len(videos) >= 5:
                    channel = {
                        "channel_number": len(channels) + 1,
                        "name": make_90s_name(topic),
                        "topic": topic,
                        "identifier": identifier,
                        "videos": videos
                    }
                    channels.append(channel)
                    used_identifiers.add(identifier)
                    print(f"Channel {len(channels)}: {channel['name']} ({identifier})")
                    break
                time.sleep(0.5)  # Be nice to the API
        except Exception as e:
            print(f"Search error for '{topic}': {e}")
            time.sleep(2)

        if len(channels) % 10 == 0:
            # Save progress
            with open("channels.json", "w") as f:
                json.dump(channels, f, indent=2)
            print(f"Progress saved: {len(channels)} channels")

    with open("channels.json", "w") as f:
        json.dump(channels, f, indent=2)
    print(f"Done! Saved {len(channels)} channels to channels.json")

if __name__ == "__main__":
    generate_channels(500)
