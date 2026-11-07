#!/usr/bin/env python3
"""Write SCRIPTS.md and SCRIPTS.txt: what every video says, plus its captions. Run captions.py first."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "videos.json")))
e = d["end"]
end_line = " · ".join(x.replace("*", "") for x in [e["text"], e["badge"], e["sub"], e["phone"], e["cta"]])
md = ["# All videos: what each one says, plus its captions", "",
      f"Every video ends with the same screen: **{end_line}**", ""]
for v in d["videos"]:
    md += ["---", f"## {v['id']}: {v['title']}", "", "**What's on screen (and what the voice says):**"]
    for i, s in enumerate(v["slides"], 1):
        lab = f"**{s['label']}:** " if s.get("label") else ""
        sub = f" _({s['sub']})_" if s.get("sub") else ""
        md.append(f"{i}. {lab}{s['text'].replace('*', '')}{sub}")
    md += ["", "**Captions for this video:**", "", "```",
           open(os.path.join(HERE, "out", v["id"] + ".txt")).read().strip(), "```", ""]
text = "\n".join(md)
open(os.path.join(HERE, "SCRIPTS.md"), "w").write(text)
plain = re.sub(r"\*\*|```", "", text)
plain = re.sub(r"^## ", "\n", plain, flags=re.M)
plain = re.sub(r"^# ", "", plain, flags=re.M)
plain = re.sub(r"^---$", "=" * 40, plain, flags=re.M)
plain = re.sub(r"_\((.*?)\)_", r"(\1)", plain)
open(os.path.join(HERE, "SCRIPTS.txt"), "w").write(plain)
print("wrote SCRIPTS.md and SCRIPTS.txt")
