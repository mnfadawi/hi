# "Rate Us On" sign — QR + NFC

6 × 4 in landscape insert for the counter acrylic holder.

- `rate-us-on-nfc-sign.pdf`: print this at **100% / Actual size**, with background graphics on.
- `rate-us-on-nfc-sign.png`: 1800 × 1200 px (300 DPI) preview/print image.
- `sign.html`: the source. `make_qr.py` regenerates the QR data.

| Side | QR opens | NFC sticker |
|------|----------|-------------|
| Google | `https://www.google.com/search?q=phone+electrik+reviews&ie=UTF-8&oe=UTF-8&hl=en-us&client=safari#ebo=1` (same as the old sign) | stick on the left "TAP HERE" circle |
| Yelp | `https://www.yelp.com/biz/phone-electrik-torrance-2` | stick on the right "TAP HERE" circle |

- QR codes use high error correction, 1.42 in square. Both are verified to decode to the links above.
- TAP HERE circles are 30 mm across, sized for 25 mm round NFC stickers on the outside of the acrylic. They're centered under each QR, about 3 in apart.
- Program each sticker with the same link as the QR above it (NFC Tools app → Write → URL).
