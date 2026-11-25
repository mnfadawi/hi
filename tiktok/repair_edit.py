#!/usr/bin/env python3
"""Turn a long, wide repair recording into a branded YouTube video and vertical Shorts.

Usage: python3 tiktok/repair_edit.py tiktok/clips/<plan>.json [long|shorts|all]

The plan lists pieces of the recording ("from"/"to" in seconds), how fast to play each one,
an on-screen label, and an optional line for the AI voice. Long videos are 1920x1080;
Shorts are 1080x1920 crops around the phone ("cx" = the phone's x position in the recording).
"""
import json, os, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
import make_videos as mv

ORANGE, WHITE, DARK = mv.ORANGE, mv.WHITE, (17, 17, 17)
SR = mv.SR


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def atempo(speed):
    """ffmpeg's atempo only takes 0.5-2.0 per step, so chain it."""
    parts, s = [], speed
    while s > 2.0:
        parts.append("atempo=2.0"); s /= 2.0
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


# ---------- overlay images ----------
def label_png(path, W, H, label, text, sub=None, wide=True):
    """A step label: orange pill with the step name and a dark box with the text, lower third."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    scale = 1.0 if wide else 1.25
    max_w = (W * 0.62) if wide else (W - 160)
    fnt, lines, size = mv.fit(mv.parse(text), "ExtraBold", int(64 * scale), max_w, 260 * scale)
    widths = [sum(fnt.getlength(w) for w, _ in ln) + fnt.getlength(" ") * (len(ln) - 1) for ln in lines]
    box_w = max(widths) + 70
    lh = size * 1.15
    sub_h = 0
    if sub:
        sfnt, slines, ssize = mv.fit(mv.parse(sub), "SemiBold", int(40 * scale), max_w, 120 * scale)
        sub_h = len(slines) * ssize * 1.2 + 14
        box_w = max(box_w, max(sum(sfnt.getlength(w) for w, _ in ln) + sfnt.getlength(" ") * (len(ln) - 1) for ln in slines) + 70)
    box_h = len(lines) * lh + sub_h + 50
    if wide:
        x0, y0 = 70, H - box_h - 90
        cx = x0 + box_w / 2
    else:
        x0, y0 = (W - box_w) / 2, 330  # near the top, clear of the phone (it sits low in the shot)
        cx = W / 2
    if label:
        lf = mv.font("Black", int(40 * scale))
        lw = lf.getlength(label)
        lx = x0 if wide else cx - lw / 2 - 24
        d.rounded_rectangle((lx, y0 - 76 * scale, lx + lw + 48, y0 - 12), 16, fill=ORANGE)
        d.text((lx + 24, y0 - 70 * scale), label, font=lf, fill=WHITE)
    d.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), 24, fill=DARK + (215,))
    mv.draw_lines(img, lines, fnt, size, cx, y0 + 22, 10, line_gap=1.15)
    if sub:
        mv.draw_lines(img, slines, sfnt, ssize, cx, y0 + 22 + len(lines) * lh + 10, 10, color=mv.MUTED, line_gap=1.2)
    img.save(path)


def tag_png(path, W, H, wide=True):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tf = mv.font("Bold", 34)
    tag = "PHONE ELECTRIK  ·  TORRANCE  ·  WALK-INS WELCOME"
    tw = tf.getlength(tag)
    x = (W - tw - 52 - 40) if wide else (W - tw) / 2 - 26
    y = 40 if wide else 120
    d.rounded_rectangle((x, y, x + tw + 52, y + 66), 33, fill=DARK + (190,))
    d.text((x + 26, y + 12), tag, font=tf, fill=WHITE)
    img.save(path)


def card_png(path, W, H, lines_spec, logo=True):
    """A full-screen branded card (title / subscribe / end) on the dark speed-line background."""
    if (W, H) == (mv.W, mv.H):
        img = mv.background(0)
    else:
        img = Image.new("RGBA", (W, H), DARK + (255,))
        d0 = ImageDraw.Draw(img)
        for y in (50, H - 190):  # stripes only along the top and bottom, clear of the text
            for j, (length, a) in enumerate([(700, 40), (520, 28), (360, 18)]):
                yy = y + j * 46
                d0.polygon([(W - length, yy), (W + 40, yy), (W + 10, yy + 22), (W - length - 30, yy + 22)], fill=ORANGE + (a,))
    y = H * (0.16 if W > H else 0.2)
    if logo:
        h = mv.paste_scaled(img, mv.LOGO if W <= H else mv.MARK, 380 if W > H else 520, W / 2, y)
        y += h + 40
    for text, weight, size, color in lines_spec:
        fnt, lines, sz = mv.fit(mv.parse(text), weight, size, W * 0.8, 400)
        mv.draw_lines(img, lines, fnt, sz, W / 2, y, 10, color=color, line_gap=1.15)
        y += len(lines) * sz * 1.15 + 30
    img.convert("RGB").save(path)


# ---------- building blocks ----------
def voice_track(say, dur, lead=0.3):
    """The AI voice line placed near the start of a piece, padded or trimmed to the piece's length."""
    out = np.zeros(int(dur * SR), dtype="float32")
    if say:
        clip = mv.speak(mv.spoken({"type": "text", "text": say}), mv.VOICE)
        a = int(lead * SR)
        n = min(len(clip), len(out) - a)
        if n > 0:
            out[a:a + n] = clip[:n]
    return out


def piece(src, seg, W, H, wide, tmp, idx, tag):
    """One piece of the recording: cut, speed up, crop (Shorts), label, voice + quiet workshop sound."""
    a, b, speed = seg["from"], seg["to"], seg.get("speed", 1.0)
    dur = (b - a) / speed
    if seg.get("voice") and not seg.get("no_stretch"):
        need = len(mv.speak(mv.spoken({"type": "text", "text": seg["voice"]}), mv.VOICE)) / SR + 0.7
        if need > dur:  # slow the piece down just enough for the voice to finish
            speed = max(0.5, (b - a) / need); dur = (b - a) / speed
    vwav = os.path.join(tmp, f"v{idx}.wav")
    sf.write(vwav, voice_track(seg.get("voice"), dur), SR)
    ovl = os.path.join(tmp, f"l{idx}.png")
    if seg.get("text"):
        label_png(ovl, W, H, seg.get("label"), seg["text"], seg.get("sub"), wide)
    else:
        Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(ovl)
    if wide:
        z = seg.get("zoom")  # [cx, cy, width] to zoom in on part of the shot
        if z:
            zw = int(z[2]); zh = int(zw * 9 / 16)
            geo = f"crop={zw}:{zh}:{int(z[0] - zw / 2)}:{int(z[1] - zh / 2)},scale={W}:{H}"
        else:
            geo = f"scale={W}:{H}"
    else:
        cw = seg.get("cw", 540)  # a little tighter than full height, so the phone fills more of the screen
        ch = int(cw * 16 / 9)
        cx = min(max(seg.get("cx", 960), cw / 2), 1920 - cw / 2)
        cy = min(max(seg.get("cy", 640), ch / 2), 1080 - ch / 2)
        geo = f"crop={cw}:{ch}:{int(cx - cw / 2)}:{int(cy - ch / 2)},scale={W}:{H}:flags=lanczos"
    amb = seg.get("ambient", 0.25)
    out = os.path.join(tmp, f"p{idx:02d}.mp4")
    ff("-ss", str(a), "-to", str(b), "-i", src, "-i", ovl, "-i", tag, "-i", vwav,
       "-filter_complex",
       f"[0:v]setpts=PTS/{speed},fps={mv.FPS},{geo},setsar=1[v0];[v0][1:v]overlay=0:0[v1];[v1][2:v]overlay=0:0[v];"
       f"[0:a]{atempo(speed)},volume={amb},aresample={SR},apad[amb];[3:a]volume=1.6[vo];"
       f"[amb][vo]amix=inputs=2:duration=longest:normalize=0,atrim=0:{dur:.3f},aresample=44100[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ac", "2", out)
    return out


def card_piece(png, seconds, say, tmp, idx):
    vwav = os.path.join(tmp, f"cv{idx}.wav")
    if say:
        need = len(mv.speak(mv.spoken({"type": "text", "text": say}), mv.VOICE)) / SR + 0.6
        seconds = max(seconds, need)
    sf.write(vwav, voice_track(say, seconds, lead=0.2), SR)
    out = os.path.join(tmp, f"c{idx:02d}.mp4")
    ff("-loop", "1", "-i", png, "-i", vwav, "-t", f"{seconds:.3f}", "-r", str(mv.FPS),
       "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
       "-af", "aresample=44100", "-c:a", "aac", "-b:a", "160k", "-ac", "2", out)
    return out


def join(parts, out):
    lst = out + ".txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    ff("-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-preset", "medium", "-crf", "22",
       "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out)
    os.remove(lst)


def build(plan, video, src, wide):
    W, H = (1920, 1080) if wide else (mv.W, mv.H)
    end = json.load(open(os.path.join(mv.HERE, "videos.json")))["end"]
    with tempfile.TemporaryDirectory() as tmp:
        tag = os.path.join(tmp, "tag.png"); tag_png(tag, W, H, wide)
        parts = []
        for i, item in enumerate(video["parts"]):
            if item.get("card"):
                png = os.path.join(tmp, f"card{i}.png")
                spec = [(t, wgt, sz, ORANGE if col == "orange" else (mv.MUTED if col == "muted" else WHITE))
                        for t, wgt, sz, col in item["lines"]]
                card_png(png, W, H, spec, logo=item.get("logo", True))
                parts.append(card_piece(png, item.get("seconds", 2.5), item.get("voice"), tmp, i))
            else:
                parts.append(piece(src, item, W, H, wide, tmp, i, tag))
        # the shop's end card
        png = os.path.join(tmp, "end.png")
        if wide:
            card_png(png, W, H, [(end["text"], "Black", 84, WHITE), (end["badge"], "ExtraBold", 54, WHITE),
                                 ("3025 Artesia Blvd STE 101, Torrance, CA 90504 · (323) 348-6756", "SemiBold", 42, mv.MUTED),
                                 (end["cta"], "ExtraBold", 58, ORANGE)])
        else:
            img = mv.background(0); mv.render_slide(img, dict(end, seconds=3.5), 5, 0, 1, "")
            img.convert("RGB").save(png)
        parts.append(card_piece(png, 3.5, None, tmp, 99))
        out = os.path.join(mv.OUT, video["id"] + ".mp4")
        join(parts, out)
        print("made", os.path.relpath(out, mv.ROOT))


if __name__ == "__main__":
    plan = json.load(open(sys.argv[1]))
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    src = os.path.join(mv.HERE, plan["source"])
    for v in plan["videos"]:
        if which == "all" or which == v.get("kind") or which == v["id"]:
            build(plan, v, src, v.get("kind") == "long")
