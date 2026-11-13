#!/usr/bin/env python3
"""Turn the scripts in videos.json into vertical 1080x1920 TikTok/Reels/Shorts videos.

Usage:  python3 tiktok/make_videos.py            # render every video
        python3 tiktok/make_videos.py battery    # render videos whose id contains "battery"

Every slide is read out loud by an AI voice (Kokoro). Add a trending sound at low
volume inside TikTok/Instagram on top of it for extra reach.
Wrap words in *stars* in videos.json to color them orange.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out")
W, H, FPS = 1080, 1920, 30
BG, ORANGE, WHITE, MUTED = (17, 17, 17), (242, 101, 34), (255, 255, 255), (176, 190, 197)
FONT_DIR = "/usr/share/fonts/opentype/inter"
# TikTok's buttons cover the right edge and its caption covers the bottom: keep text out of there.
SAFE_L, SAFE_R, SAFE_TOP, SAFE_BOTTOM = 80, W - 170, 260, H - 420


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Inter-{weight}.otf"), size)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def parse(text):
    """'Your *battery is* dying' -> [('Your', False), ('battery', True), ('is', True), ('dying', False)]"""
    words, inside = [], False
    for raw in text.split():
        starts = raw.startswith("*")
        hl = inside or starts
        if starts:
            inside = True
        if raw.rstrip(".,?!:").endswith("*"):
            inside = False
            hl = True
        words.append((raw.replace("*", ""), hl))
    return words


def wrap(words, fnt, max_w):
    lines, line = [], []
    space = fnt.getlength(" ")
    for w in words:
        trial = line + [w]
        width = sum(fnt.getlength(x[0]) for x in trial) + space * (len(trial) - 1)
        if line and width > max_w:
            lines.append(line)
            line = [w]
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def fit(words, weight, max_size, max_w, max_h, line_gap=1.12):
    size = max_size
    while size > 40:
        fnt = font(weight, size)
        lines = wrap(words, fnt, max_w)
        if len(lines) * size * line_gap <= max_h and all(
            sum(fnt.getlength(x[0]) for x in ln) + fnt.getlength(" ") * (len(ln) - 1) <= max_w for ln in lines
        ):
            return fnt, lines, size
        size -= 4
    fnt = font(weight, size)
    return fnt, wrap(words, fnt, max_w), size


def draw_lines(img, lines, fnt, size, cx, top, t, color=WHITE, line_gap=1.12):
    """Draw word-wrapped lines centered on cx, each line sliding up and fading in."""
    space = fnt.getlength(" ")
    for i, ln in enumerate(lines):
        p = ease_out((t - i * 0.05) / 0.22)
        if p <= 0:
            continue
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        width = sum(fnt.getlength(x[0]) for x in ln) + space * (len(ln) - 1)
        x = cx - width / 2
        y = top + i * size * line_gap + (1 - p) * 60
        for word, hl in ln:
            d.text((x, y), word, font=fnt, fill=(ORANGE if hl else color) + (int(255 * p),))
            x += fnt.getlength(word) + space
        img.alpha_composite(layer)


def background(frame):
    """Dark background with drifting orange speed lines, like the logo."""
    img = Image.new("RGBA", (W, H), BG + (255,))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shift = (frame * 3) % 480
    for k in range(-2, 7):
        y = k * 480 + shift - 200
        for j, (length, alpha) in enumerate([(520, 34), (380, 24), (260, 16)]):
            yy = y + j * 46
            d.polygon([(W - length, yy), (W + 40, yy), (W + 10, yy + 22), (W - length - 30, yy + 22)],
                      fill=ORANGE + (alpha,))
    img.alpha_composite(layer)
    return img


LOGO = Image.open(os.path.join(ROOT, "logo-pe.png")).convert("RGBA")
MARK = Image.open(os.path.join(ROOT, "logo_pe_mark.png")).convert("RGBA")


def paste_scaled(img, src, width, cx, top, alpha=1.0):
    h = int(src.height * width / src.width)
    s = src.resize((width, h), Image.LANCZOS)
    if alpha < 1:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s.putalpha(a)
    img.alpha_composite(s, (int(cx - width / 2), int(top)))
    return h


def render_slide(img, slide, t, idx, total, handle):
    kind = slide.get("type", "text")
    cx = (SAFE_L + SAFE_R) / 2
    d = ImageDraw.Draw(img)

    if kind != "end":
        paste_scaled(img, MARK, 130, cx, 100)
        tf = font("Bold", 34)
        tag = "TORRANCE  ·  WALK-INS WELCOME"
        d.text((cx - tf.getlength(tag) / 2, 192), tag, font=tf, fill=MUTED)

    if kind == "hook":
        words = parse(slide["text"])
        fnt, lines, size = fit(words, "Black", 150, SAFE_R - SAFE_L, 900)
        block_h = len(lines) * size * 1.12
        pop = 1 + 0.05 * math.sin(min(t / 0.6, 1) * math.pi)  # small "punch" as it lands
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_lines(layer, lines, fnt, size, cx, (SAFE_TOP + SAFE_BOTTOM) / 2 - block_h / 2, 10)
        if pop != 1:
            big = layer.resize((int(W * pop), int(H * pop)), Image.LANCZOS)
            layer = big.crop(((big.width - W) // 2, (big.height - H) // 2,
                              (big.width - W) // 2 + W, (big.height - H) // 2 + H))
        img.alpha_composite(layer)

    elif kind == "text":
        # measure the whole block first so it can be centered vertically
        words = parse(slide["text"])
        fnt, lines, size = fit(words, "ExtraBold", 104, SAFE_R - SAFE_L, 560)
        block = (170 if slide.get("label") else 0) + len(lines) * size * 1.12
        if slide.get("sub"):
            sfnt, slines, ssize = fit(parse(slide["sub"]), "SemiBold", 60, SAFE_R - SAFE_L, 400)
            block += 50 + len(slines) * ssize * 1.25
        top = max(SAFE_TOP + 80, (SAFE_TOP + 80 + SAFE_BOTTOM) / 2 - block / 2)
        if slide.get("label"):
            lp = ease_out(t / 0.2)
            lf = font("Black", 64)
            label = slide["label"]
            lw = lf.getlength(label)
            pad = 30
            box = Image.new("RGBA", img.size, (0, 0, 0, 0))
            bd = ImageDraw.Draw(box)
            x0 = cx - lw / 2 - pad
            bd.rounded_rectangle((x0, top, x0 + lw + pad * 2, top + 100), 20, fill=ORANGE + (int(255 * lp),))
            bd.text((cx - lw / 2, top + 14), label, font=lf, fill=WHITE + (int(255 * lp),))
            img.alpha_composite(box)
            top += 170
        draw_lines(img, lines, fnt, size, cx, top, t)
        if slide.get("sub"):
            sub_top = top + len(lines) * size * 1.12 + 50
            draw_lines(img, slines, sfnt, ssize, cx, sub_top, t - 0.2, color=MUTED, line_gap=1.25)

    elif kind == "qr":
        # a big scannable QR code with a short line above and the web address below
        top = SAFE_TOP + 40
        if slide.get("label"):
            lf = font("Black", 60)
            lw = lf.getlength(slide["label"])
            d.rounded_rectangle((cx - lw / 2 - 28, top, cx + lw / 2 + 28, top + 94), 20, fill=ORANGE)
            d.text((cx - lw / 2, top + 13), slide["label"], font=lf, fill=WHITE)
            top += 130
        fnt, lines, size = fit(parse(slide["text"]), "ExtraBold", 84, SAFE_R - SAFE_L, 200)
        draw_lines(img, lines, fnt, size, cx, top, t)
        top += len(lines) * size * 1.12 + 30
        q = Image.open(os.path.join(HERE, slide["image"])).convert("RGBA")
        qs = 560
        d.rounded_rectangle((cx - qs / 2 - 24, top, cx + qs / 2 + 24, top + qs + 48), 28, fill=WHITE)
        img.alpha_composite(q.resize((qs, qs), Image.NEAREST), (int(cx - qs / 2), int(top + 24)))
        top += qs + 48 + 30
        if slide.get("sub"):
            sfnt, slines, ssize = fit(parse(slide["sub"]), "Bold", 58, SAFE_R - SAFE_L, 160)
            draw_lines(img, slines, sfnt, ssize, cx, top, 10, color=WHITE)

    elif kind == "end":
        p = ease_out(t / 0.35)
        h = paste_scaled(img, LOGO, 520, cx, 300, alpha=p)
        y = 300 + h + 30
        for text, weight, size, color in [
            (slide.get("text", "Phone ElectriK"), "Black", 84, WHITE),
            (slide.get("badge", "*90-day warranty*"), "ExtraBold", 60, WHITE),
            (slide.get("sub", "3025 Artesia Blvd, Torrance"), "SemiBold", 50, MUTED),
            (slide.get("phone", ""), "SemiBold", 50, MUTED),
            (slide.get("cta", "Walk in today. We've got you."), "ExtraBold", 62, ORANGE),
        ]:
            if not text:
                continue
            words = parse(text)
            fnt, lines, sz = fit(words, weight, size, SAFE_R - SAFE_L, 300)
            draw_lines(img, lines, fnt, sz, cx, y, t - 0.15, color=color, line_gap=1.2)
            y += len(lines) * sz * 1.2 + 30

    x0, x1 = cx - 220, cx + 220
    d.rounded_rectangle((x0, 262, x1, 270), 4, fill=(60, 60, 60))
    d.rounded_rectangle((x0, 262, x0 + (x1 - x0) * (idx + min(t / slide["seconds"], 1)) / total, 270), 4, fill=ORANGE)


# ---------- voiceover ----------
# Kokoro is a free, natural-sounding AI voice that runs on this computer.
# Model files go in tiktok/models (see README.md). Voices: af_heart, af_bella, am_michael, am_adam...
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "1.15"))
MODELS = os.path.join(HERE, "models")
CACHE = os.path.join(HERE, ".voice_cache")
SR = 24000
_kokoro = None

SPOKEN = [("ElectriK", "Electric"), ("Blvd", "Boulevard"), ("→", ","), ("&", "and"), ("·", ","),
          ("3025 Artesia", "thirty twenty five Artesia"), ("iPHONE", "iPhone"), ("90-day", "ninety day"),
          ("(323) 348-6756", "3 2 3, 3 4 8, 6 7 5 6"), ("PS5", "P S 5"), ("PS4", "P S 4"), ("HDMI", "H D M I"), (" SE ", " S E ")]


def spoken(slide):
    if "say" in slide:
        text = slide["say"]
    else:
        text = slide["text"] + (". " + slide["sub"] if slide.get("sub") else "")
        if slide["type"] == "end":
            text = (slide.get("text", "Phone ElectriK") + ". " + slide.get("sub", "") + ". "
                    + slide.get("cta", ""))
    text = text.replace("*", "")
    for a, b in SPOKEN:
        text = text.replace(a, b)
    return text


def speak(text, voice):
    """Return the voiceover for one slide as a numpy array (cached on disk)."""
    import hashlib
    import numpy as np
    import soundfile as sf
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f"{voice}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(path):
        global _kokoro
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(os.path.join(MODELS, "kokoro-v1.0.int8.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
        audio, sr = _kokoro.create(text, voice=voice, speed=SPEED, lang="en-us")
        sf.write(path, audio, sr)
    audio, _ = sf.read(path, dtype="float32")
    return np.asarray(audio)


def render(video, handle, voice=True):
    import numpy as np
    import soundfile as sf
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, video["id"] + ".mp4")
    slides = [dict(s) for s in video["slides"]]
    # each slide lasts at least its written time, longer if the voice needs it
    lead, tail = 0.1, 0.3
    clips = []
    for s in slides:
        clip = speak(spoken(s), video.get("voice", VOICE)) if voice else np.zeros(0, dtype="float32")
        s["seconds"] = round(max(s["seconds"], lead + len(clip) / SR + tail) * FPS) / FPS
        clips.append(clip)
    track = np.zeros(int(sum(s["seconds"] for s in slides) * SR) + SR, dtype="float32")
    pos = 0.0
    for s, clip in zip(slides, clips):
        a = int((pos + lead) * SR)
        track[a:a + len(clip)] += clip
        pos += s["seconds"]
    wav = os.path.join(OUT, video["id"] + ".tmp.wav")
    sf.write(wav, track[:int(pos * SR)], SR)

    frames = [(i, f) for i, s in enumerate(slides) for f in range(round(s["seconds"] * FPS))]
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", wav,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100", "-ac", "2",
         "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", path],
        stdin=subprocess.PIPE)
    start = {}
    for n, (i, f) in enumerate(frames):
        start.setdefault(i, n)
        img = background(n)
        render_slide(img, slides[i], (n - start[i]) / FPS, i, len(slides), handle)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    os.remove(wav)
    # also save a still of the opening, to use as the cover image
    cover = background(0)
    render_slide(cover, slides[0], 2.0, 0, len(slides), handle)
    cover.convert("RGB").save(os.path.join(OUT, video["id"] + "-cover.jpg"), quality=90)
    print("made", os.path.relpath(path, ROOT), f"({len(frames) / FPS:.1f}s)", flush=True)


def with_ending(video, data):
    """Every video ends with the same 'why us' slide and the shop's end card."""
    return {**video, "slides": video["slides"] + [data["end"]]}


if __name__ == "__main__":
    data = json.load(open(os.path.join(HERE, "videos.json")))
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    for v in data["videos"]:
        if want in v["id"]:
            render(with_ending(v, data), data["handle"])
