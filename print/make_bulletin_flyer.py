"""Phone ElectriK bulletin-board flyer.

Run from the repo root:  python3 print/make_bulletin_flyer.py
Makes print/phone-electrik-bulletin-flyer.png + .pdf (US Letter, 300 DPI).

Based on the CELL PHONE REPAIR stand sign (make_poster.py on the
phone-mockup-cracked-screen branch), adapted for a bulletin board:
  - white safety margin on every side so home/office printers never cut it off
  - QR code (phoneelectrik.com/links: call, directions, reviews, socials)
  - 90-day warranty line
  - tear-off tabs with the phone number along the bottom
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf, os, qrcode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'print')
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'

ORANGE, WHITE, BLACK, BG = '#F26522', '#FFFFFF', '#111111', '#0D0D0D'
DPI = 300
W, H = int(8.5 * DPI), int(11 * DPI)          # 2550 x 3300
M = int(0.4 * DPI)                              # 0.4" white margin all round
TAB_H = int(1.55 * DPI)                         # tear-off strip
TAB_GAP = 40
CW = W - 2 * M
CH = H - 2 * M - TAB_H - TAB_GAP
PAD = 50

page = Image.new('RGB', (W, H), WHITE)

# ── Card (the sign itself) ────────────────────────────────────────────────────
BANNER_H, HDR_H, PHONE_H, LABEL_H = 170, 330, 790, 95
DEVICE_H, RSB_H, NUM_H = 250, 215, 255
FOOT_H = CH - (BANNER_H + HDR_H + PHONE_H + LABEL_H + DEVICE_H + RSB_H + NUM_H)
assert FOOT_H >= 420, FOOT_H

card = Image.new('RGB', (CW, CH), BG)
y_ph = BANNER_H + HDR_H
glow = Image.new('RGB', (CW, CH), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([0, y_ph + 60, CW // 2, y_ph + PHONE_H], fill='#2a0f00')
gd.ellipse([CW // 2, y_ph + 60, CW, y_ph + PHONE_H], fill='#001a2e')
card = Image.blend(card, glow.filter(ImageFilter.GaussianBlur(110)), 0.85)
d = ImageDraw.Draw(card)


def fit(text, max_w, size, font=BOLD):
    while size > 20:
        f = ImageFont.truetype(font, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(font, size)


def center(text, y, f, fill, draw=None):
    (draw or d).text((CW // 2, y), text, font=f, fill=fill, anchor='mm')


y = 0
# Banner
d.rectangle([0, 0, CW, BANNER_H], fill=ORANGE)
center('CELL PHONE REPAIR', BANNER_H // 2, fit('CELL PHONE REPAIR', CW - 2 * PAD, 160), WHITE)
y = BANNER_H

# Header: logo + PHONE ELECTRIK, tagline
logo = Image.open(os.path.join(OUT, 'assets', 'logo_pe_cropped.png')).convert('RGB')
LOGO_H = 200
logo = logo.resize((int(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
row_cy = y + 125
fb = fit('PHONE ELECTRIK', CW - 2 * PAD - logo.width - 60, 210)
name_w = d.textlength('PHONE ELECTRIK', font=fb)
x0 = (CW - (logo.width + 60 + name_w)) // 2
card.paste(logo, (int(x0), row_cy - LOGO_H // 2))
tx = x0 + logo.width + 60
d.text((tx, row_cy), 'PHONE ', font=fb, fill=WHITE, anchor='lm')
d.text((tx + d.textlength('PHONE ', font=fb), row_cy), 'ELECTRIK', font=fb, fill=ORANGE, anchor='lm')
tag = 'Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers  ·  Game Consoles  ·  Apple Watches'
center(tag, y + HDR_H - 50, fit(tag, CW - 2 * PAD, 64), ORANGE)
y += HDR_H


# Phones
def rounded(img, r=60):
    img = img.convert('RGBA')
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    img.putalpha(m)
    return img


for i, fn in enumerate(['IMG_0096.jpeg', 'IMG_0097.jpeg']):
    im = Image.open(os.path.join(ROOT, fn))
    s = min(PHONE_H / im.height, (CW // 2 - 60) / im.width)
    im = rounded(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS))
    sx = i * CW // 2 + (CW // 2 - im.width) // 2
    card.paste(im, (sx, y + PHONE_H - im.height), im)
y += PHONE_H
fl = ImageFont.truetype(BOLD, 66)
d.text((CW // 4, y + LABEL_H // 2), 'iPhone 17 Pro Max', font=fl, fill=ORANGE, anchor='mm')
d.text((3 * CW // 4, y + LABEL_H // 2), 'Samsung Galaxy S26', font=fl, fill=WHITE, anchor='mm')
y += LABEL_H

# Device strip
d.rectangle([0, y, CW, y + DEVICE_H], fill='#181818')
d.rectangle([0, y, CW, y + 5], fill=ORANGE)
l1 = 'We Fix Any Device — Any Brand, Any Model'
l2 = 'Apple  ·  Samsung  ·  Motorola  ·  LG  ·  OnePlus  ·  Google Pixel  ·  & More'
l3 = 'Bring it in — We are happy to help!'
center(l1, y + 62, fit(l1, CW - 80, 78), ORANGE)
center(l2, y + 135, fit(l2, CW - 80, 62), WHITE)
center(l3, y + 200, fit(l3, CW - 80, 60), WHITE)
y += DEVICE_H

# REPAIR · SELL · BUY
d.rectangle([0, y, CW, y + RSB_H], fill=WHITE)
d.rectangle([0, y, CW, y + 8], fill=BLACK)
d.rectangle([0, y + RSB_H - 8, CW, y + RSB_H], fill=BLACK)
parts = [('REPAIR', ORANGE), ('  ·  ', '#333'), ('SELL', BLACK), ('  ·  ', '#333'), ('BUY', BLACK)]
full = ''.join(t for t, _ in parts)
fr = fit(full, CW - 120, 180)
x = (CW - d.textlength(full, font=fr)) / 2
for t, c in parts:
    d.text((x, y + RSB_H // 2), t, font=fr, fill=c, anchor='lm')
    x += d.textlength(t, font=fr)
y += RSB_H

# Phone number
d.rectangle([0, y, CW, y + NUM_H], fill=ORANGE)
center('(323) 348-6756', y + NUM_H // 2, fit('(323) 348-6756', CW - 120, 220), WHITE)
y += NUM_H

# Footer: info left, QR right
d.rectangle([0, y, CW, CH], fill='#141414')
QR = FOOT_H - 70
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=20)
q.add_data('https://phoneelectrik.com/links')
q.make(fit=True)
qimg = q.make_image(fill_color='black', back_color='white').convert('RGB').resize((QR, QR), Image.NEAREST)
qx = CW - PAD - QR
card.paste(qimg, (qx, y + 35))
left_w = qx - 2 * PAD
lines = [
    ('90-DAY WARRANTY ON EVERY REPAIR', ORANGE),
    ('WALK-IN  ·  NO APPOINTMENT NEEDED', WHITE),
    ('MON–SAT 9AM–8PM  ·  SUN 10AM–6PM', WHITE),
    ('3025 Artesia Blvd STE 101, Torrance, CA 90504', WHITE),
    ('SCAN QR:  call · directions · reviews · follow us', ORANGE),
]
ff = fit(max((t for t, _ in lines), key=lambda t: d.textlength(t, font=ImageFont.truetype(BOLD, 60))), left_w, 70)
step = (FOOT_H - 60) / len(lines)
for i, (t, c) in enumerate(lines):
    d.text((PAD, y + 30 + step * (i + 0.5)), t, font=ff, fill=c, anchor='lm')

# Paste card with rounded corners
mask = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW - 1, CH - 1], 36, fill=255)
page.paste(card, (M, M), mask)

# ── Tear-off tabs ─────────────────────────────────────────────────────────────
pd = ImageDraw.Draw(page)
ty = M + CH + TAB_GAP
N = 8
tw = CW / N


def dashed(x1, y1, x2, y2, dash=22, gap=14, w=4):
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    n = 0.0
    while n < L:
        e = min(n + dash, L)
        pd.line([(x1 + (x2 - x1) * n / L, y1 + (y2 - y1) * n / L),
                 (x1 + (x2 - x1) * e / L, y1 + (y2 - y1) * e / L)], fill='#777', width=w)
        n += dash + gap


dashed(M, ty, M + CW, ty)
for i in range(N + 1):
    dashed(M + i * tw, ty, M + i * tw, ty + TAB_H)
cap_f = ImageFont.truetype(BOLD, 34)
pd.rectangle([W // 2 - 260, ty - 24, W // 2 + 260, ty + 24], fill=WHITE)
pd.text((W // 2, ty), 'TEAR OFF & TAKE ONE', font=cap_f, fill='#444', anchor='mm')

for i in range(N):
    tab = Image.new('RGB', (TAB_H - 30, int(tw) - 24), WHITE)
    td = ImageDraw.Draw(tab)
    td.text((tab.width // 2, 50), 'PHONE ELECTRIK', font=ImageFont.truetype(BOLD, 44), fill=ORANGE, anchor='mm')
    td.text((tab.width // 2, 125), '(323) 348-6756', font=ImageFont.truetype(BOLD, 62), fill=BLACK, anchor='mm')
    td.text((tab.width // 2, 200), 'Repair · Sell · Buy', font=ImageFont.truetype(REG, 38), fill='#333', anchor='mm')
    tab = tab.rotate(90, expand=True)
    page.paste(tab, (int(M + i * tw + 12), ty + 15))

png = os.path.join(OUT, 'phone-electrik-bulletin-flyer.png')
pdf = os.path.join(OUT, 'phone-electrik-bulletin-flyer.pdf')
page.save(png, dpi=(DPI, DPI))
with open(pdf, 'wb') as f:
    f.write(img2pdf.convert(png, layout_fun=img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))))
print('saved', png, pdf)
