"""Regenerate the QR codes for sign.html (high error correction).

Writes qr.json; sign.html embeds the resulting SVG paths.
"""
import json
import qrcode

URLS = {
    # Same Google link as the previous sign. Swap in the direct
    # g.page/r/.../review link once it's available.
    "google": "https://www.google.com/search?q=phone+electrik+reviews&ie=UTF-8&oe=UTF-8&hl=en-us&client=safari#ebo=1",
    "yelp": "https://www.yelp.com/biz/phone-electrik-torrance-2",
}

out = {}
for key, url in URLS.items():
    q = qrcode.QRCode(border=0, error_correction=qrcode.constants.ERROR_CORRECT_H)
    q.add_data(url)
    q.make(fit=True)
    m = q.get_matrix()
    d = "".join(f"M{x},{y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
    out[key] = {"n": len(m), "d": d, "url": url}
json.dump(out, open("qr.json", "w"))
