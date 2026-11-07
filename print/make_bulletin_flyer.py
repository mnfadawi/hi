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
SYM = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BANNER_H, HDR_H, PHONE_H, LABEL_H = 190, 300, 560, 85
PROMISE_H, SVC_H, NUM_H = 250, 470, 230
FOOT_H = CH - (BANNER_H + HDR_H + PHONE_H + LABEL_H + PROMISE_H + SVC_H + NUM_H)
assert FOOT_H >= 400, FOOT_H

card = Image.new('RGB', (CW, CH), BG)
y_ph = BANNER_H + HDR_H
glow = Image.new('RGB', (CW, CH), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([0, y_ph + 40, CW // 2, y_ph + PHONE_H], fill='#2a0f00')
gd.ellipse([CW // 2, y_ph + 40, CW, y_ph + PHONE_H], fill='#001a2e')
card = Image.blend(card, glow.filter(ImageFilter.GaussianBlur(110)), 0.85)
d = ImageDraw.Draw(card)


def fit(text, max_w, size, font=BOLD):
    while size > 20:
        f = ImageFont.truetype(font, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(font, size)


def center(text, y, f, fill, cx=None):
    d.text((CW // 2 if cx is None else cx, y), text, font=f, fill=fill, anchor='mm')


# 1. Hook banner — speaks to the person walking past with a problem
y = 0
d.rectangle([0, 0, CW, BANNER_H], fill=ORANGE)
hook = 'CRACKED SCREEN?  DEAD BATTERY?  WE FIX IT!'
center(hook, BANNER_H // 2, fit(hook, CW - 2 * PAD, 130), WHITE)
y = BANNER_H

# 2. Brand
logo = Image.open(os.path.join(OUT, 'assets', 'logo_pe_cropped.png')).convert('RGB')
LOGO_H = 190
logo = logo.resize((int(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
row_cy = y + 115
fb = fit('PHONE ELECTRIK', CW - 2 * PAD - logo.width - 60, 200)
name_w = d.textlength('PHONE ELECTRIK', font=fb)
x0 = (CW - (logo.width + 60 + name_w)) // 2
card.paste(logo, (int(x0), row_cy - LOGO_H // 2))
tx = x0 + logo.width + 60
d.text((tx, row_cy), 'PHONE ', font=fb, fill=WHITE, anchor='lm')
d.text((tx + d.textlength('PHONE ', font=fb), row_cy), 'ELECTRIK', font=fb, fill=ORANGE, anchor='lm')
tag = 'Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers  ·  Game Consoles  ·  Apple Watches'
center(tag, y + HDR_H - 45, fit(tag, CW - 2 * PAD, 62), ORANGE)
y += HDR_H


# 3. Phones (smaller than the stand sign — the words do the selling here)
def rounded(img, r=50):
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
fl = ImageFont.truetype(BOLD, 60)
center('iPhone 17 Pro Max', y + LABEL_H // 2, fl, ORANGE, CW // 4)
center('Samsung Galaxy S26', y + LABEL_H // 2, fl, WHITE, 3 * CW // 4)
y += LABEL_H

# 4. Promise strip — the reason to walk in today
d.rectangle([0, y, CW, y + PROMISE_H], fill='#181818')
d.rectangle([0, y, CW, y + 5], fill=ORANGE)
p1 = 'Most Repairs Done While You Wait  ·  90-Day Warranty'
p2 = 'Any Brand, Any Model: Apple · Samsung · Motorola · LG · OnePlus · Google Pixel & More'
p3 = 'Walk in, no appointment needed. We are happy to help!'
center(p1, y + 70, fit(p1, CW - 80, 84), ORANGE)
center(p2, y + 145, fit(p2, CW - 80, 56), WHITE)
center(p3, y + 208, fit(p3, CW - 80, 54), WHITE)
y += PROMISE_H

# 5. Two clear money lanes: we REPAIR / we BUY & SELL
d.rectangle([0, y, CW, y + SVC_H], fill=WHITE)
half = CW // 2
d.rectangle([half - 3, y + 40, half + 3, y + SVC_H - 40], fill='#DDDDDD')
colw = half - 2 * PAD


def column(cx, title, tcol, lines):
    center(title, y + 75, fit(title, colw, 120), tcol, cx)
    fsz = min(fit(t, colw, 54).size for t in lines)
    f = ImageFont.truetype(BOLD, fsz)
    for k, t in enumerate(lines):
        center(t, y + 175 + k * 72, f, BLACK, cx)


column(half // 2, 'WE REPAIR', ORANGE, [
    'Screens  ·  Batteries',
    'Charging Ports  ·  Cameras',
    'Back Glass  ·  Liquid Damage',
    'Data Transfer & Recovery',
])
column(half + half // 2, 'WE BUY & SELL', BLACK, [
    'Selling your phone or tablet?',
    'Walk in, we\'ll take a look.',
    'Refurbished iPhone · iPad',
    'Samsung · MacBook',
])
y += SVC_H

# 6. Phone number
d.rectangle([0, y, CW, y + NUM_H], fill=ORANGE)
center('CALL / TEXT  (323) 348-6756', y + NUM_H // 2, fit('CALL / TEXT  (323) 348-6756', CW - 120, 190), WHITE)
y += NUM_H

# 7. Footer: where we are + ask for support, QR on the right
d.rectangle([0, y, CW, CH], fill='#141414')
QR = FOOT_H - 110
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=20)
q.add_data('https://phoneelectrik.com/links')
q.make(fit=True)
qimg = q.make_image(fill_color='black', back_color='white').convert('RGB').resize((QR, QR), Image.NEAREST)
qx = CW - PAD - QR
card.paste(qimg, (qx, y + 30))
center('SCAN ME', y + 30 + QR + 40, ImageFont.truetype(BOLD, 50), ORANGE, qx + QR // 2)
left_w = qx - 2 * PAD
lines = [
    ('3025 Artesia Blvd STE 101, Torrance, CA 90504', WHITE),
    ('MON–SAT 9AM–8PM  ·  SUN 10AM–6PM', WHITE),
    ('Support your local Torrance repair shop!', ORANGE),
    ('Happy customer? Scan & leave us a review', ORANGE),
    ('Scan for directions · reviews · Instagram · TikTok', WHITE),
]
fsz = min(fit(t, left_w, 70).size for t, _ in lines)
ff = ImageFont.truetype(BOLD, fsz)
step = (FOOT_H - 50) / len(lines)
for i, (t, c) in enumerate(lines):
    d.text((PAD, y + 25 + step * (i + 0.5)), t, font=ff, fill=c, anchor='lm')

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
    td.text((tab.width // 2, 200), '3025 Artesia Blvd', font=ImageFont.truetype(REG, 38), fill='#333', anchor='mm')
    tab = tab.rotate(90, expand=True)
    page.paste(tab, (int(M + i * tw + 12), ty + 15))

png = os.path.join(OUT, 'phone-electrik-bulletin-flyer.png')
pdf = os.path.join(OUT, 'phone-electrik-bulletin-flyer.pdf')
page.save(png, dpi=(DPI, DPI))
with open(pdf, 'wb') as f:
    f.write(img2pdf.convert(png, layout_fun=img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))))
print('saved', png, pdf)
