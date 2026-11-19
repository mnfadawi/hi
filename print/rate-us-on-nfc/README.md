# "Rate Us On" sign — QR + NFC

8.5 × 5.5 in landscape insert (half a letter sheet) for the counter acrylic holder.

- **`PRINT-ME-rate-us-on-sign.pdf`**: print this one. Letter paper, one sign per page, cut on the dashed line. The cut sign is 7.9 × 5.1 in. Print at **100% / Actual size** with background graphics on.
- `rate-us-on-nfc-sign.pdf`: one sign, page size 8.5 × 5.5 in.
- `rate-us-on-nfc-sign.png`: 2550 × 1650 px (300 DPI) preview/print image.
- `sign.html`: the source (`print.html` places it on the letter page). `make_qr.py` regenerates the QR data.

| Side | QR opens | NFC sticker |
|------|----------|-------------|
| Google | `https://www.google.com/search?q=phone+electrik+reviews&ie=UTF-8&oe=UTF-8&hl=en-us&client=safari#ebo=1` (same as the old sign) | stick on the left "TAP HERE" circle |
| Yelp | `https://www.yelp.com/biz/phone-electrik-torrance-2` | stick on the right "TAP HERE" circle |

- QR codes use high error correction, 1.6 in square. Both are verified to decode to the links above.
- TAP HERE circles are 30 mm across, sized for 25 mm round NFC stickers on the outside of the acrylic. They're centered under each QR, about 4.25 in apart.
- Program each sticker with the same link as the QR above it (NFC Tools app → Write → URL).
