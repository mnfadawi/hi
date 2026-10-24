"""Trace the ICH logo's solid-colour layers (black text/star, orange, green)
into SVG paths on top of an upscaled copy, so the logo prints sharp."""
import sys, base64, io
import numpy as np
from PIL import Image, ImageFilter
import potrace

src, out_svg = sys.argv[1], sys.argv[2]
S = 4
im = Image.open(src).convert("RGB")
W, H = im.size
big = im.resize((W * S, H * S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
a = np.asarray(big, dtype=np.int32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
masks = {
    "#111111": (np.maximum(np.maximum(r, g), b) < 50) & (g - r < 12),
    "#ee5a24": (r > 170) & (g < 140) & (b < 100) & (r - g > 70),
    "#344e33": (g - r >= 14) & (g - b >= 14) & (r < 110) & (g < 130),
}

def to_d(path):
    parts = []
    for c in path:
        x, y = c.start_point.x, c.start_point.y
        parts.append(f"M{x:.1f},{y:.1f}")
        for seg in c.segments:
            if seg.is_corner:
                parts.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                parts.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        parts.append("Z")
    return "".join(parts)

layers = []
for color, m in masks.items():
    bm = potrace.Bitmap(~m)  # potracer traces the False (dark) pixels
    p = bm.trace(turdsize=120, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.0, opticurve=True, opttolerance=0.2)
    layers.append(f'<path fill="{color}" fill-rule="evenodd" d="{to_d(p)}"/>')
    print(color, int(m.sum()))

# Base: upscaled + sharpened raster (keeps the multicolour mosque drawing).
base = im.resize((W * S, H * S), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))
buf = io.BytesIO(); base.save(buf, "PNG", optimize=True)
b64 = base64.b64encode(buf.getvalue()).decode()
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*S} {H*S}">'
       f'<image width="{W*S}" height="{H*S}" href="data:image/png;base64,{b64}"/>'
       + "".join(layers) + "</svg>")
open(out_svg, "w").write(svg)
print("svg bytes", len(svg))
