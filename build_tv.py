#!/usr/bin/env python3
"""
build_tv.py
Generates channels.json with 500 channels of public-domain / Archive.org MP4s.
Requires: pip install internetarchive
Run weekly via cron/GitHub Actions to refresh broken links.
"""
import json
import random
import time
from internetarchive import search_items, get_item

TOPICS = [
    "public domain cartoon", "Chavo del Ocho", "El Chavo", "Chapulin Colorado",
    "professional wrestling 80s", "90s infomercial", "retro commercial",
    "NASA space documentary", "public domain documentary", "Prelinger",
    "1990s anime", "skateboarding 90s", "MTV music video", "90s sitcom",
    "tech show 90s", "game show", "extreme sports 90s", "Spanish novela",
    "wrestling NWA", "educational film", "industrial film", "home movie 80s",
    "public domain western", "sci-fi public domain", "classic commercial"
]

COMMERCIAL_TOPICS = ["retro commercial", "infomercial 80s", "90s advertisement", "Prelinger commercial"]

def find_mp4s(query, limit=30):
    results = []
    try:
        search = search_items(f'{query} mediatype:movies', fields=['identifier', 'title'])
        for item in list(search)[:limit]:
            try:
                ia_item = get_item(item['identifier'])
                for f in ia_item.get_files(formats=['h.264', 'MPEG4', '512Kb MPEG4']):
                    if f.name.lower().endswith('.mp4'):
                        results.append({
                            "title": item.get('title', item['identifier']),
                            "url": f"https://archive.org/download/{item['identifier']}/{f.name}",
                            "duration": 600  # placeholder; real duration requires probing or metadata
                        })
                        break
            except Exception:
                continue
            if len(results) >= 8:
                break
    except Exception as e:
        print(f"Search failed for '{query}': {e}")
    return results

def main():
    all_videos = []
    for topic in TOPICS:
        print(f"Searching: {topic}")
        vids = find_mp4s(topic)
        all_videos.extend(vids)
        time.sleep(1)

    commercials = []
    for topic in COMMERCIAL_TOPICS:
        commercials.extend(find_mp4s(topic, limit=15))

    # Build 500 channels
    channels = []
    for i in range(1, 501):
        random.shuffle(all_videos)
        playlist = random.sample(all_videos, min(5, len(all_videos)))
        # Insert 60s commercial after each show
        full_playlist = []
        for v in playlist:
            full_playlist.append(v)
            if commercials:
                full_playlist.append(random.choice(commercials) | {"duration": 60, "is_commercial": True})
        channels.append({
            "number": i,
            "name": f"CH {i:03d} – {random.choice(['ToonTown', 'Nova TV', 'Lucha Libre', 'Infomercial Hour', 'Space Channel', 'Retro Hits', 'Documental', 'Wrestling Classic'])} {random.randint(1,99)}",
            "playlist": full_playlist
        })

    with open("channels.json", "w") as f:
        json.dump(channels, f, indent=2)
    print(f"Wrote {len(channels)} channels to channels.json")

if __name__ == "__main__":
    main()
