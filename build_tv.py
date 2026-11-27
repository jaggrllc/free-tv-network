#!/usr/bin/env python3
"""
build_tv.py
Searches Internet Archive for retro content and builds channels.json.
Run: python build_tv.py
Requires: pip install internetarchive
"""
import json
import time
import random
from internetarchive import search_items, get_item

TOPICS = [
    "1990s anime", "skateboarding", "MTV music videos", "infomercials",
    "sitcoms", "tech shows", "game shows", "extreme sports",
    "public domain movies", "classic cartoons", "old commercials",
    "educational film", "saturday morning", "vhs", "public domain"
]

ADJECTIVES = ["Radical", "Totally", "Awesome", "Funky", "Groovy", "Tubular", "Wicked"]
NOUNS = ["Zone", "Channel", "TV", "Network", "Theater", "Hour", "Blast"]

def make_name(topic):
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}: {topic.title()}"

def get_good_mp4s(identifier, max_n=5):
    try:
        item = get_item(identifier)
        videos = []
        for f in item.files:
            name = getattr(f, "name", "") or f.get("name", "")
            fmt = (getattr(f, "format", "") or f.get("format", "")).lower()
            size = int(getattr(f, "size", 0) or f.get("size", 0) or 0)
            length = getattr(f, "length", None) or f.get("length", 0)
            try:
                dur = float(length) if length else 300
            except:
                dur = 300
            if (size > 1_000_000 and name.lower().endswith(".mp4") and
                any(x in fmt for x in ["h.264", "mpeg4", "512kb", "h264"])):
                videos.append({
                    "url": f"https://archive.org/download/{identifier}/{name}",
                    "duration": int(dur),
                    "title": name[:80]
                })
                if len(videos) >= max_n:
                    break
        return videos
    except Exception as e:
        print(f"  Skip {identifier}: {e}")
        return []

def build(num_channels=50):  # Start with 50; increase later
    channels = []
    used = set()
    print(f"Building up to {num_channels} channels...")

    for topic in TOPICS * 10:  # Cycle topics
        if len(channels) >= num_channels:
            break
        query = f"{topic} AND mediatype:movies"
        print(f"Searching: {query}")
        try:
            results = search_items(query, fields=["identifier"], params={"rows": 40})
            for result in results:
                ident = result["identifier"]
                if ident in used:
                    continue
                vids = get_good_mp4s(ident, 5)
                if vids:
                    channels.append({
                        "channel_number": len(channels) + 1,
                        "name": make_name(topic),
                        "topic": topic,
                        "videos": vids,
                        "commercials": []  # Add real commercial URLs later
                    })
                    used.add(ident)
                    print(f"  → Channel {len(channels)}: {ident} ({len(vids)} videos)")
                    break
            time.sleep(1.2)
        except Exception as e:
            print(f"Search error: {e}")
            time.sleep(3)

    with open("channels.json", "w") as f:
        json.dump(channels, f, indent=2)
    print(f"\nSaved {len(channels)} channels to channels.json")

if __name__ == "__main__":
    build(50)  # Change to 500 when ready (will take hours)
