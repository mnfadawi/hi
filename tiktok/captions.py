#!/usr/bin/env python3
"""Write tiktok/CAPTIONS.md: a ready-to-paste caption for every video for TikTok, Instagram, Facebook and YouTube."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "videos.json")))

SHOP = ["📍 Phone ElectriK · 3025 Artesia Blvd STE 101, Torrance, CA",
        "📞 Call or text (323) 348-6756",
        "🕘 Mon–Sat 9AM–8PM · Sun 10AM–6PM",
        "🚶 No appointment needed · 🛡️ 90-day warranty on every repair"]
LOCAL = "#phoneelectrik #torrance #southbay #phonerepair"

full = {
    "id": "00-full-video",
    "title": "4 phone problems you should never ignore",
    "caption": "4 phone problems you should NEVER ignore 📱🔥 Save this so you have it when you need it.",
    "tags": "#batterylife #waterdamage #crackedscreen #chargingport",
}

out = ["# Captions for every video",
       "",
       "Copy the box for the platform you're posting on. Every caption ends with the shop's info and hashtags.",
       "On TikTok and Instagram, always tag the location **Phone ElectriK, Torrance**.",
       ""]
for v in [full] + data["videos"]:
    tags = " ".join(dict.fromkeys(f"{v['tags']} {LOCAL}".split()))  # no repeats
    out += [f"## {v['id']}.mp4: {v['title']}", "",
            "**TikTok**", "```", f"{v['caption']} Walk in today, no appointment needed. 📍 Torrance", "", tags, "```",
            "**Instagram Reels**", "```", v["caption"], "", *SHOP, "", tags, "```",
            "**Facebook Reels**", "```", v["caption"], "",
            "Come see us at Phone ElectriK: 3025 Artesia Blvd STE 101, Torrance.",
            "📞 Call or text (323) 348-6756 · Open 7 days · No appointment needed",
            "🛡️ 90-day warranty on every repair", "", "#phonerepair #torrance #southbay", "```",
            "**YouTube Shorts**", "",
            "Title:", "```", f"{v['title']} #shorts", "```",
            "Description:", "```", v["caption"], "", *SHOP, "🌐 phoneelectrik.com", "", tags + " #shorts", "```", ""]
open(os.path.join(HERE, "CAPTIONS.md"), "w").write("\n".join(out))
print("wrote CAPTIONS.md for", len(data["videos"]) + 1, "videos")
