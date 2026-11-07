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
# Built for a pinned board people walk past: one huge hook, little text, clear order.
HOOK_H, HDR_H, PHONE_H, LABEL_H = 430, 270, 540, 75
PROMISE_H, SVC_H, NUM_H = 215, 300, 230
FOOT_H = CH - (HOOK_H + HDR_H + PHONE_H + LABEL_H + PROMISE_H + SVC_H + NUM_H)
assert FOOT_H >= 420, FOOT_H

card = Image.new('RGB', (CW, CH), BG)
y_ph = HOOK_H + HDR_H
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


# 1. HOOK — the one line that stops someone walking past
y = 0
d.rectangle([0, 0, CW, HOOK_H], fill=ORANGE)
center('BROKEN PHONE?', 175, fit('BROKEN PHONE?', CW - 2 * PAD, 280), WHITE)
sub = 'Cracked Screen  ·  Dead Battery  ·  Won\'t Charge'
center(sub, 355, fit(sub, CW - 3 * PAD, 84), '#1A1A1A')
y = HOOK_H

# 2. WHO — brand
logo = Image.open(os.path.join(OUT, 'assets', 'logo_pe_cropped.png')).convert('RGB')
LOGO_H = 170
logo = logo.resize((int(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
row_cy = y + 110
fb = fit('PHONE ELECTRIK', CW - 2 * PAD - logo.width - 60, 175)
name_w = d.textlength('PHONE ELECTRIK', font=fb)
x0 = (CW - (logo.width + 60 + name_w)) // 2
card.paste(logo, (int(x0), row_cy - LOGO_H // 2))
tx = x0 + logo.width + 60
d.text((tx, row_cy), 'PHONE ', font=fb, fill=WHITE, anchor='lm')
d.text((tx + d.textlength('PHONE ', font=fb), row_cy), 'ELECTRIK', font=fb, fill=ORANGE, anchor='lm')
tag = 'Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Game Consoles  ·  Apple Watches'
center(tag, y + HDR_H - 40, fit(tag, CW - 2 * PAD, 58), '#BBBBBB')
y += HDR_H


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
fl = ImageFont.truetype(BOLD, 52)
center('iPhone 17 Pro Max', y + LABEL_H // 2, fl, '#BBBBBB', CW // 4)
center('Samsung Galaxy S26', y + LABEL_H // 2, fl, '#BBBBBB', 3 * CW // 4)
y += LABEL_H

# 3. WHY COME IN
d.rectangle([0, y, CW, y + PROMISE_H], fill='#181818')
d.rectangle([0, y, CW, y + 5], fill=ORANGE)
p1 = 'Most Repairs Done While You Wait'
p2 = '90-Day Warranty  ·  Any Brand, Any Model  ·  Walk-Ins Welcome'
center(p1, y + 80, fit(p1, CW - 120, 100), ORANGE)
center(p2, y + 160, fit(p2, CW - 120, 60), WHITE)
y += PROMISE_H

# 4. WHAT WE DO — two money lanes
d.rectangle([0, y, CW, y + SVC_H], fill=WHITE)
half = CW // 2
d.rectangle([half - 3, y + 45, half + 3, y + SVC_H - 45], fill='#DDDDDD')
colw = half - 2 * PAD
ft = ImageFont.truetype(BOLD, min(fit('WE BUY & SELL', colw, 115).size, fit('WE REPAIR', colw, 115).size))
center('WE REPAIR', y + 100, ft, ORANGE, half // 2)
center('WE BUY & SELL', y + 100, ft, BLACK, half + half // 2)
a = 'Screens · Batteries · Ports · Cameras'
b = 'Phones · Tablets · Laptops'
fs = ImageFont.truetype(BOLD, min(fit(a, colw, 60).size, fit(b, colw, 60).size))
center(a, y + 215, fs, '#222222', half // 2)
center(b, y + 215, fs, '#222222', half + half // 2)
y += SVC_H

# 5. CALL
d.rectangle([0, y, CW, y + NUM_H], fill=ORANGE)
t = 'CALL / TEXT  (323) 348-6756'
center(t, y + NUM_H // 2, fit(t, CW - 120, 190), WHITE)
y += NUM_H

# 6. WHERE + tell a friend, QR on the right
d.rectangle([0, y, CW, CH], fill='#141414')
QR = FOOT_H - 120
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=20)
q.add_data('https://phoneelectrik.com/links')
q.make(fit=True)
qimg = q.make_image(fill_color='black', back_color='white').convert('RGB').resize((QR, QR), Image.NEAREST)
qx = CW - PAD - QR
card.paste(qimg, (qx, y + 35))
center('SCAN ME', y + 35 + QR + 42, ImageFont.truetype(BOLD, 50), ORANGE, qx + QR // 2)
left_w = qx - 2 * PAD
lines = [
    ('3025 Artesia Blvd STE 101', WHITE, 78),
    ('Torrance, CA 90504', WHITE, 78),
    ('Mon–Sat 9AM–8PM  ·  Sun 10AM–6PM', '#BBBBBB', 60),
    ('Love us? Tell a friend & leave a review!', ORANGE, 60),
]
fbig = ImageFont.truetype(BOLD, min(fit(t, left_w, sz).size for t, _, sz in lines if sz == 78))
fsm = ImageFont.truetype(BOLD, min(fit(t, left_w, sz).size for t, _, sz in lines if sz == 60))
ys = [y + 85, y + 175, y + 285, y + 385]
for (t, c, sz), yy in zip(lines, ys):
    d.text((PAD, yy), t, font=fbig if sz == 78 else fsm, fill=c, anchor='lm')

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
pd.rectangle([W // 2 - 360, ty - 24, W // 2 + 360, ty + 24], fill=WHITE)
pd.text((W // 2, ty), 'TAKE ONE  ·  SHARE WITH A FRIEND', font=cap_f, fill='#444', anchor='mm')

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
