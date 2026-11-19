# "Rate Us On" sign — QR + NFC

8.5 × 5.5 in landscape insert (half a letter sheet) for the counter acrylic holder.

- **`PRINT-ME-rate-us-on-sign.pdf`**: print this one. Letter paper with three sizes, one per page: A = 7 × 4.53 in, B = 6.5 × 4.21 in, C = 6 × 3.88 in. Print only the page that fits the holder, at **100% / Actual size** with background graphics on, then cut on the dashed line. (`print.html` + `make_print_pdf.py` rebuild it.)
- `rate-us-on-nfc-sign.pdf`: one sign, page size 8.5 × 5.5 in.
- `rate-us-on-nfc-sign.png`: 2550 × 1650 px (300 DPI) preview/print image.
- `sign.html`: the source. `make_qr.py` regenerates the QR data.

| Side | QR opens | NFC sticker |
|------|----------|-------------|
| Google | `https://www.google.com/search?q=phone+electrik+reviews&ie=UTF-8&oe=UTF-8&hl=en-us&client=safari#ebo=1` (same as the old sign) | stick on the left "TAP HERE" circle |
| Yelp | `https://www.yelp.com/biz/phone-electrik-torrance-2` | stick on the right "TAP HERE" circle |

- QR codes use high error correction and are verified to decode to the links above.
- Each orange circle is 40 mm on the full-size sign (28 mm on size C), so a 25 mm NFC sticker stuck on the **outside of the acrylic**, right on the circle, leaves a visible orange ring. "TAP HERE ▼" sits above the circle, so the sticker doesn't cover it.
- Program each sticker with the same link as the QR above it (NFC Tools app → Write → URL).
