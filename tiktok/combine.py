#!/usr/bin/env python3
"""Join every video in videos.json into one long video: tiktok/out/00-full-video.mp4.

Each video's opening becomes a "PART n OF 5" title card. The warranty slide and the
shop ending appear once, at the very end.
"""
import json, os
import make_videos as mv

data = json.load(open(os.path.join(mv.HERE, "videos.json")))
order = ["battery", "rice", "screen", "charging", "more-than"]  # strongest first
parts = sorted(data["videos"], key=lambda v: next(i for i, k in enumerate(order) if k in v["id"]))
problems = [v for v in parts if "more-than" not in v["id"]]
slides = [
    {"type": "hook", "text": f"{len(problems)} phone problems you should *never* ignore", "seconds": 2.8},
    {"type": "text", "text": "We're *Phone ElectriK* in Torrance, and we fix these every day", "sub": "Save this. You'll need it.", "seconds": 3.0},
]
why = end = None
for n, v in enumerate(parts, 1):
    for i, s in enumerate(v["slides"]):
        if s["type"] == "end":
            end = s
        elif s.get("label") == "WHY US":
            why = s
        elif s.get("label") == "DON'T WAIT":
            continue  # one shared call to action at the end instead
        elif i == 0:
            label = "BONUS" if n > len(problems) else f"PART {n} OF {len(problems)}"
            slides.append({"type": "text", "label": label, "text": s["text"], "seconds": 2.6})
        else:
            slides.append(s)
slides += [
    {"type": "text", "label": "DON'T WAIT", "text": "Sound like your phone? Come see us *today*",
     "sub": "Walk in. Batteries, screens, charging ports, water damage and more.", "seconds": 3.6},
    why,
    {**end, "text": "Torrance's *Phone ElectriK*", "cta": "Walk in today. We've got you."},
]
mv.render({"id": "00-full-video", "slides": slides}, data["handle"])
