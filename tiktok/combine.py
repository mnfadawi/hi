#!/usr/bin/env python3
"""Join the main videos into one long video: tiktok/out/00-full-video.mp4.

Each video's opening becomes a "PART n OF 4" title card. The call to action,
the warranty slide and the shop ending appear once, at the very end.
"""
import json, os
import make_videos as mv

data = json.load(open(os.path.join(mv.HERE, "videos.json")))
by_id = {v["id"]: v for v in data["videos"]}
problems = [by_id[i] for i in ["02-battery-signs", "01-water-damage", "03-cracked-screen", "04-charging-port"]]
bonus = by_id["05-more-than-phones"]

slides = [
    {"type": "hook", "text": f"{len(problems)} phone problems you should *never* ignore", "seconds": 2.8},
    {"type": "text", "text": "We're *Phone ElectriK* in Torrance, and we fix these every day",
     "sub": "Save this. You'll need it.", "seconds": 3.0},
]
for n, v in enumerate(problems + [bonus], 1):
    for i, s in enumerate(v["slides"]):
        if s.get("label") in ("DON'T WAIT", "DON'T SEE YOURS?"):
            continue  # one shared call to action at the end instead
        if i == 0:
            label = "BONUS" if v is bonus else f"PART {n} OF {len(problems)}"
            slides.append({**s, "type": "text", "label": label, "seconds": 2.6})
        else:
            slides.append(s)
slides.append({"type": "text", "label": "DON'T WAIT", "text": "Sound like your phone? Come see us *today*",
               "sub": "Walk in. Batteries, screens, charging ports, water damage and more.", "seconds": 3.6})
mv.render(mv.with_ending({"id": "00-full-video", "slides": slides}, data), data["handle"])
