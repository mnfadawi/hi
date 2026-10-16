#!/usr/bin/env python3
"""Build the USB-ready vertical welcome sign for a Samsung TV mounted on its side.

The TV only ever sees a normal 1920x1080 landscape file, so it never rotates,
rescales or "corrects" anything. The portrait poster is baked in sideways, so
it reads upright once the panel is physically turned 90 degrees.

Source: ../tv-poster.png (1080x1920 portrait design)
Run:    python3 usb-sign/build.py   (needs Pillow, numpy, ffmpeg)
"""
import os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "tv-poster.png")
FPS = 30
CYCLE_S = 12          # one shine sweep per cycle; cycle repeats seamlessly
DURATION_S = 30 * 60  # 30-minute file: Repeat restarts only twice an hour
BAR_H = 18            # orange accent bars at top/bottom of tv-poster.png

# Physical mount -> how the portrait art must be turned to sit upright on it.
VARIANTS = {
    "TV-turned-CLOCKWISE": Image.Transpose.ROTATE_90,          # art turned left
    "TV-turned-COUNTERCLOCKWISE": Image.Transpose.ROTATE_270,  # art turned right
}


def shine_frames(base):
    """Soft highlight gliding across the orange bars: keeps the picture from
    being a perfectly still frame without distracting from the content."""
    arr = np.asarray(base, dtype=np.float32)
    w = arr.shape[1]
    xs = np.arange(w, dtype=np.float32)
    n = FPS * CYCLE_S
    for i in range(n):
        # sweep runs for the first 40% of the cycle, then rests
        t = i / (n * 0.4)
        f = arr.copy()
        if t <= 1.0:
            cx = -200 + t * (w + 400)
            g = np.exp(-((xs - cx) / 90.0) ** 2)[None, :, None] * 0.55
            for y0, y1 in ((0, BAR_H), (arr.shape[0] - BAR_H, arr.shape[0])):
                band = f[y0:y1]
                f[y0:y1] = band + (255 - band) * g
        yield Image.fromarray(f.clip(0, 255).astype(np.uint8))


def build(name, transpose, base):
    out_dir = os.path.join(HERE, name)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, "PhoneElectriK-Welcome")

    # Still fallback: baseline JPEG, 4:2:0, sRGB, no EXIF (no orientation tag).
    base.transpose(transpose).save(stem + ".jpg", "JPEG", quality=92,
                                   subsampling="4:2:0", progressive=False,
                                   optimize=True)

    tmp = tempfile.mkdtemp()
    try:
        for i, fr in enumerate(shine_frames(base)):
            fr.transpose(transpose).save(os.path.join(tmp, f"f{i:04d}.png"),
                                         compress_level=1)
        # Encode one seamless cycle as a single closed GOP (starts on an IDR)...
        cycle = os.path.join(tmp, "cycle.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
            "-vf", "format=yuv420p,setsar=1",
            # Constrained Baseline: no B-frames/CABAC, lightest decode there is
            "-c:v", "libx264", "-preset", "slow", "-profile:v", "baseline", "-level", "4.0",
            "-crf", "18", "-maxrate", "8M", "-bufsize", "8M",
            "-g", str(FPS * CYCLE_S), "-keyint_min", str(FPS * CYCLE_S), "-sc_threshold", "0",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-color_range", "tv",
            cycle,
        ], check=True)
        # ...then repeat it bit-for-bit (no re-encode) to fill the full length.
        listing = os.path.join(tmp, "list.txt")
        with open(listing, "w") as fh:
            fh.write(f"file '{cycle}'\n" * (DURATION_S // CYCLE_S))
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", listing,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-map", "0:v", "-map", "1:a", "-t", str(DURATION_S),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "32k",
            "-map_metadata", "-1", "-movflags", "+faststart",
            stem + ".mp4",
        ], check=True)
    finally:
        shutil.rmtree(tmp)


def main():
    base = Image.open(SRC).convert("RGB")
    assert base.size == (1080, 1920), base.size
    for name, transpose in VARIANTS.items():
        build(name, transpose, base)
        print("built", name)


if __name__ == "__main__":
    main()
