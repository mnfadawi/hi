#!/usr/bin/env python3
"""Build the USB-ready vertical welcome sign for a Samsung TV mounted on its side.

The TV only ever sees a normal 1920x1080 landscape file, so it never rotates,
rescales or "corrects" anything. The portrait art is baked in sideways, so it
reads upright once the panel is physically turned 90 degrees.

Outputs, per mount direction:
  PhoneElectriK-Welcome.mp4   slide 1 only (../tv-poster.png)
  PhoneElectriK-2Slide.mp4    slide 1 (15 s) -> slide 2 services (15 s), looping
  PhoneElectriK-5Slide.mp4    welcome (10 s) -> fixed while you wait (10 s) ->
                              our repair services (12 s) -> need a phone? (10 s)
                              -> save our number QR (12 s), with an orange wipe
                              between slides and glowing "Ask us!" button and QR
  *.jpg                       baseline still of each slide, for checking orientation

Run:    python3 usb-sign/build.py          (everything)
        python3 usb-sign/build.py loop     (only the 5-slide loop)
Needs Pillow, numpy, ffmpeg, node + playwright.
"""
import json, os, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.join(HERE, "..", "tv-poster.png")
SERVICES_HTML = os.path.join(HERE, "slide2-services.html")
# 5-slide loop: (page, seconds on screen). Short enough that a walk-in sees
# every slide; the QR slide gets extra time to pull out a phone and scan.
LOOP_SLIDES = [
    (None, 10),                                             # welcome poster
    (os.path.join(HERE, "slide-fix.html"), 10),
    (os.path.join(HERE, "slide-services.html"), 12),        # more to read
    (os.path.join(HERE, "slide-phones.html"), 10),          # glowing "Ask us!"
    (os.path.join(HERE, "slide-save-number.html"), 12),     # glowing QR frame
]
WIPE_S = 0.6          # orange band sweeps down between slides
PULSE_S = 1.6         # one glow cycle of a slide's [data-pulse] element
DURATION_LOOP_S = 15 * 60  # its motion costs more bytes; Repeat One loops it
FPS = 30
SLIDE_S = 15          # 2-slide loop: each slide shows this long, then a clean cut
SHINE_S = 12          # Welcome loop: one shine sweep per cycle
DURATION_S = 30 * 60  # 30-minute file: Repeat restarts only twice an hour
GOP = FPS * SLIDE_S   # 2-slide loop: one keyframe exactly at each slide change
BAR_H = 18            # orange accent bars at top/bottom of each slide

# Physical mount -> how the portrait art must be turned to sit upright on it.
VARIANTS = {
    "TV-turned-CLOCKWISE": Image.Transpose.ROTATE_90,          # art turned left
    "TV-turned-COUNTERCLOCKWISE": Image.Transpose.ROTATE_270,  # art turned right
}


def load_poster(pure_black=False):
    img = Image.open(POSTER).convert("RGB")
    assert img.size == (1080, 1920), img.size
    if pure_black:
        # Poster background is #0d0d0d; stretch levels so it becomes #000000
        # while white stays white.
        a = np.asarray(img, dtype=np.float32)
        img = Image.fromarray(((a - 13) * 255 / 242).clip(0, 255).round().astype(np.uint8))
    return img


def render_services(tmp):
    out = os.path.join(tmp, "services.png")
    subprocess.run(["node", os.path.join(HERE, "render_slide.js"), SERVICES_HTML, out],
                   check=True)
    img = Image.open(out).convert("RGB")
    assert img.size == (1080, 1920), img.size
    return img


def render_slide(src, tmp, name, lit=False):
    """Render a 1080x1920 slide page; with lit=True also return the glowing
    variant and the [data-pulse] box (x, y, w, h)."""
    out = os.path.join(tmp, name + ".png")
    cmd = ["node", os.path.join(HERE, "render_slide.js"), src, out]
    if lit:
        cmd.append(os.path.join(tmp, name + "-lit.png"))
    res = subprocess.run(cmd, check=True, capture_output=True, text=True)
    img = Image.open(out).convert("RGB")
    assert img.size == (1080, 1920), img.size
    if not lit:
        return img
    box = json.loads(res.stdout.strip().splitlines()[-1])
    return img, Image.open(cmd[-1]).convert("RGB"), box


def shine(arr, t):
    """Soft highlight gliding across the orange bars (t in 0..1 = one pass).
    Keeps the picture from being a perfectly still frame without distracting
    from the content."""
    if not 0.0 <= t <= 1.0:
        return arr
    w = arr.shape[1]
    xs = np.arange(w, dtype=np.float32)
    cx = -200 + t * (w + 400)
    g = np.exp(-((xs - cx) / 90.0) ** 2)[None, :, None] * 0.55
    f = arr.copy()
    for y0, y1 in ((0, BAR_H), (arr.shape[0] - BAR_H, arr.shape[0])):
        band = f[y0:y1]
        f[y0:y1] = band + (255 - band) * g
    return f


def welcome_frames(slide):
    arr = np.asarray(slide, dtype=np.float32)
    n = FPS * SHINE_S
    for i in range(n):
        # sweep runs for the first 40% of the cycle, then rests
        yield shine(arr, i / (n * 0.4))


def two_slide_frames(slides):
    # A hard cut, not a crossfade: a fade repaints every pixel for half a
    # second and multiplied the file size ~5x for no gain on the wall.
    for slide in slides:
        arr = np.asarray(slide, dtype=np.float32)
        for i in range(FPS * SLIDE_S):
            yield shine(arr, i / (FPS * SHINE_S * 0.4))


def wipe(old, new, t):
    """Orange band sweeping top to bottom: new slide above it, old below."""
    h = old.shape[0]
    band = 260
    edge = int(-band + t * (h + band))
    f = old.copy()
    top = max(0, min(h, edge))
    f[:top] = new[:top]
    b0, b1 = max(0, edge), max(0, min(h, edge + band))
    if b1 > b0:
        ys = (np.arange(b0, b1) - edge) / band          # 0..1 down the band
        shade = (1 - 0.35 * np.abs(ys - 0.5) * 2)[:, None, None]
        f[b0:b1] = np.array([242, 101, 34], dtype=np.float32) * shade
    return f


def loop_frames(slides):
    """slides: list of (image, seconds, lit_image or None, pulse box or None)."""
    arrs = [np.asarray(s[0], dtype=np.float32) for s in slides]
    nw = int(FPS * WIPE_S)
    pad = 60  # glow spreads beyond the element
    for k, (_, secs, lit, box) in enumerate(slides):
        cur, nxt = arrs[k], arrs[(k + 1) % len(arrs)]
        if lit is not None:
            lit = np.asarray(lit, dtype=np.float32)
            x0, y0 = max(0, int(box["x"]) - pad), max(0, int(box["y"]) - pad)
            x1 = min(1080, int(box["x"] + box["w"]) + pad)
            y1 = min(1920, int(box["y"] + box["h"]) + pad)
        n = FPS * secs
        for i in range(n):
            f = cur
            if lit is not None:
                m = 0.5 - 0.5 * np.cos(2 * np.pi * i / (FPS * PULSE_S))
                f = cur.copy()
                f[y0:y1, x0:x1] = cur[y0:y1, x0:x1] * (1 - m) + lit[y0:y1, x0:x1] * m
            f = shine(f, i / (FPS * SHINE_S * 0.4))
            j = i - (n - nw)
            if j >= 0:  # last WIPE_S of each slide wipes into the next
                f = wipe(f, nxt, (j + 1) / nw)
            yield f


def encode(frames, transpose, out_mp4, tmp, gop=GOP, duration=DURATION_S, keyframes=None):
    frame_dir = os.path.join(tmp, "frames")
    os.makedirs(frame_dir)
    count = 0
    for i, f in enumerate(frames):
        Image.fromarray(f.clip(0, 255).astype(np.uint8)).transpose(transpose) \
            .save(os.path.join(frame_dir, f"f{i:04d}.png"), compress_level=1)
        count += 1
    # Encode one seamless cycle (starts on an IDR)...
    cycle = os.path.join(tmp, "cycle.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", os.path.join(frame_dir, "f%04d.png"),
        "-vf", "format=yuv420p,setsar=1",
        # Constrained Baseline: no B-frames/CABAC, lightest decode there is
        "-c:v", "libx264", "-preset", "slow", "-profile:v", "baseline", "-level", "4.0",
        "-crf", "18", "-maxrate", "8M", "-bufsize", "8M",
        "-g", str(gop), "-keyint_min", str(gop), "-sc_threshold", "0",
        *(["-force_key_frames", ",".join(map(str, keyframes))] if keyframes else []),
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-color_range", "tv",
        cycle,
    ], check=True)
    # ...then repeat it bit-for-bit (no re-encode) to fill the full length,
    # rounded to whole cycles so the picture and the silent audio end together
    # and Repeat restarts on a clean slide boundary.
    cycle_s = count / FPS
    cycles = max(1, round(duration / cycle_s))
    duration = cycles * cycle_s
    listing = os.path.join(tmp, "list.txt")
    with open(listing, "w") as fh:
        fh.write(f"file '{cycle}'\n" * cycles)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", listing,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-map", "0:v", "-map", "1:a", "-t", str(duration),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "32k",
        "-map_metadata", "-1", "-movflags", "+faststart",
        out_mp4,
    ], check=True)
    shutil.rmtree(frame_dir)


def save_jpg(img, transpose, path):
    # Baseline JPEG, 4:2:0, sRGB, no EXIF (no orientation tag).
    img.transpose(transpose).save(path, "JPEG", quality=92, subsampling="4:2:0",
                                  progressive=False, optimize=True)


def build_loop(tmp):
    slides = []
    for k, (src, secs) in enumerate(LOOP_SLIDES):
        if src is None:
            slides.append((load_poster(pure_black=True), secs, None, None))
        elif "data-pulse" in open(src).read():
            img, lit, box = render_slide(src, tmp, f"slide{k}", lit=True)
            slides.append((img, secs, lit, box))
        else:
            slides.append((render_slide(src, tmp, f"slide{k}"), secs, None, None))
    starts = [sum(s for _, s in LOOP_SLIDES[:k]) for k in range(len(LOOP_SLIDES))]
    for name, transpose in VARIANTS.items():
        stem = os.path.join(HERE, name, "PhoneElectriK-")
        for k, (img, *_) in enumerate(slides[1:], start=2):
            save_jpg(img, transpose, stem + f"5Slide-slide{k}.jpg")
        encode(loop_frames(slides), transpose, stem + "5Slide.mp4", tmp,
               gop=FPS * max(s for _, s in LOOP_SLIDES), duration=DURATION_LOOP_S,
               keyframes=starts)
        print("built 5-slide loop", name)


def main():
    tmp = tempfile.mkdtemp()
    if sys.argv[1:] == ["loop"]:
        try:
            build_loop(tmp)
        finally:
            shutil.rmtree(tmp)
        return
    try:
        welcome = load_poster()
        slides = (load_poster(pure_black=True), render_services(tmp))
        for name, transpose in VARIANTS.items():
            out_dir = os.path.join(HERE, name)
            os.makedirs(out_dir, exist_ok=True)
            stem = os.path.join(out_dir, "PhoneElectriK-")
            save_jpg(welcome, transpose, stem + "Welcome.jpg")
            save_jpg(slides[1], transpose, stem + "Services.jpg")
            encode(welcome_frames(welcome), transpose, stem + "Welcome.mp4", tmp,
                   gop=FPS * SHINE_S)
            encode(two_slide_frames(slides), transpose, stem + "2Slide.mp4", tmp)
            print("built", name)
        build_loop(tmp)
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
