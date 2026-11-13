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

TIKTOK_END = "📍 Phone ElectriK · 3025 Artesia Blvd, Torrance · 🛡️ 90-day warranty · 🚶 Walk-ins welcome"

out = ["# Captions for every video",
       "",
       "Copy the box for the platform you're posting on. Every caption ends with the shop's info and hashtags.",
       "On TikTok and Instagram, always tag the location **Phone ElectriK, Torrance**.",
       ""]
for v in data["videos"]:
    tags = " ".join(dict.fromkeys(f"{v['tags']} {LOCAL}".split()))  # no repeats
    # a plain-text caption file next to each video, with the same name: 01-water-damage.mp4 -> 01-water-damage.txt
    line = "-" * 40
    open(os.path.join(HERE, "out", v["id"] + ".txt"), "w").write("\n".join([
        f"VIDEO: {v['id']}.mp4", f"TOPIC: {v['title']}", "",
        line, "TIKTOK (caption)", line,
        v["caption"], "", TIKTOK_END, "", tags, "",
        line, "INSTAGRAM REELS (caption)", line,
        v["caption"], "", *SHOP, "", tags, "",
        line, "FACEBOOK REELS (description)", line,
        v["caption"], "", "Come see us at Phone ElectriK: 3025 Artesia Blvd STE 101, Torrance.",
        "📞 Call or text (323) 348-6756 · Open 7 days · No appointment needed",
        "🛡️ 90-day warranty on every repair", "", "#phonerepair #torrance #southbay", "",
        line, "YOUTUBE SHORTS", line,
        "TITLE:", f"{v['title']} #shorts", "", "DESCRIPTION:",
        v["caption"], "", *SHOP, "🌐 phoneelectrik.com", "", tags + " #shorts", ""]))
    out += [f"## {v['id']}.mp4: {v['title']}", "",
            "**TikTok**", "```", v["caption"], "", TIKTOK_END, "", tags, "```",
            "**Instagram Reels**", "```", v["caption"], "", *SHOP, "", tags, "```",
            "**Facebook Reels**", "```", v["caption"], "",
            "Come see us at Phone ElectriK: 3025 Artesia Blvd STE 101, Torrance.",
            "📞 Call or text (323) 348-6756 · Open 7 days · No appointment needed",
            "🛡️ 90-day warranty on every repair", "", "#phonerepair #torrance #southbay", "```",
            "**YouTube Shorts**", "",
            "Title:", "```", f"{v['title']} #shorts", "```",
            "Description:", "```", v["caption"], "", *SHOP, "🌐 phoneelectrik.com", "", tags + " #shorts", "```", ""]
open(os.path.join(HERE, "CAPTIONS.md"), "w").write("\n".join(out))
print("wrote CAPTIONS.md for", len(data["videos"]), "videos")
