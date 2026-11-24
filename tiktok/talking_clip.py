#!/usr/bin/env python3
"""Turn a real phone-recorded clip into a branded post: on-screen captions timed to the speech,
the Torrance/walk-ins tag at the top, and the shop's end card at the end.

Usage: python3 tiktok/talking_clip.py clip.json
clip.json: {"id": "...", "source": "path/to/raw.mov", "start": 0.4, "end": 55.6,
            "captions": [[start_sec, end_sec, "text with *orange* words"], ...]}
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
import make_videos as mv

W, H, FPS = mv.W, mv.H, mv.FPS


def caption_layer(text):
    """A dark rounded box with big white text, orange for *starred* words, sitting at chest height."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    words = mv.parse(text)
    fnt, lines, size = mv.fit(words, "ExtraBold", 84, W - 220, 360)
    line_h = size * 1.15
    box_h = len(lines) * line_h + 60
    top = 1180
    d = ImageDraw.Draw(layer)
    widths = [sum(fnt.getlength(w) for w, _ in ln) + fnt.getlength(" ") * (len(ln) - 1) for ln in lines]
    bw = max(widths) + 80
    d.rounded_rectangle((W / 2 - bw / 2, top, W / 2 + bw / 2, top + box_h), 28, fill=(17, 17, 17, 200))
    mv.draw_lines(layer, lines, fnt, size, W / 2, top + 26, 10, line_gap=1.15)
    return layer


def top_tag():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tf = mv.font("Bold", 34)
    tag = "PHONE ELECTRIK  ·  TORRANCE  ·  WALK-INS WELCOME"
    tw = tf.getlength(tag)
    d.rounded_rectangle((W / 2 - tw / 2 - 26, 120, W / 2 + tw / 2 + 26, 186), 33, fill=(17, 17, 17, 190))
    d.text((W / 2 - tw / 2, 132), tag, font=tf, fill=mv.WHITE)
    return layer


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    os.makedirs(mv.OUT, exist_ok=True)
    out = os.path.join(mv.OUT, cfg["id"] + ".mp4")
    start, end = cfg["start"], cfg["end"]
    tag = top_tag()
    caps = [(a, b, caption_layer(t)) for a, b, t in cfg["captions"]]

    # 1) the talking part, with overlays, cleaned-up audio
    talk = out + ".talk.mp4"
    reader = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", cfg["source"],
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    writer = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-ss", str(start), "-to", str(end), "-i", cfg["source"],
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-af", "highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100", "-ac", "2",
         "-c:a", "aac", "-b:a", "160k", "-shortest", talk], stdin=subprocess.PIPE)
    n = 0
    frame_bytes = W * H * 3
    while True:
        buf = reader.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        t = n / FPS
        img = Image.frombuffer("RGB", (W, H), buf).convert("RGBA")
        img.alpha_composite(tag)
        for a, b, layer in caps:
            if a - start <= t < b - start:
                img.alpha_composite(layer)
        writer.stdin.write(img.convert("RGB").tobytes())
        n += 1
    writer.stdin.close(); writer.wait(); reader.wait()

    # 2) the shop's end card (no voice)
    end_card = out + ".end.mp4"
    data = json.load(open(os.path.join(mv.HERE, "videos.json")))
    slide = dict(data["end"], seconds=3.0)
    w2 = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", end_card],
        stdin=subprocess.PIPE)
    for i in range(int(3.0 * FPS)):
        img = mv.background(i)
        mv.render_slide(img, slide, i / FPS, 0, 1, "")
        w2.stdin.write(img.convert("RGB").tobytes())
    w2.stdin.close(); w2.wait()

    # 3) join them
    lst = out + ".txt"
    open(lst, "w").write(f"file '{os.path.abspath(talk)}'\nfile '{os.path.abspath(end_card)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    for f in (talk, end_card, lst):
        os.remove(f)
    print("made", os.path.relpath(out, mv.ROOT))


if __name__ == "__main__":
    main(sys.argv[1])
