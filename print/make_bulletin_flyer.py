"""Phone ElectriK bulletin-board flyer (pinned on a board: people read it or snap a photo).

Run from the repo root:  python3 print/make_bulletin_flyer.py
Makes print/phone-electrik-bulletin-flyer.png + .pdf (US Letter, 300 DPI).
White 0.4" margin on every side so no printer cuts anything off.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf, os, qrcode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'print')
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

ORANGE, WHITE, DARK, BG, GREY = '#F26522', '#FFFFFF', '#1A1A1A', '#0D0D0D', '#BBBBBB'
DPI = 300
W, H = int(8.5 * DPI), int(11 * DPI)
M = int(0.4 * DPI)
CW, CH = W - 2 * M, H - 2 * M
PAD = 70

HOOK_H, BRAND_H, PHONE_H, LABEL_H, INFO_H, NUM_H = 520, 300, 860, 80, 430, 350
FOOT_H = CH - (HOOK_H + BRAND_H + PHONE_H + LABEL_H + INFO_H + NUM_H)
assert FOOT_H >= 480, FOOT_H

card = Image.new('RGB', (CW, CH), BG)
py = HOOK_H + BRAND_H
glow = Image.new('RGB', (CW, CH), BG)
gd = ImageDraw.Draw(glow)
gd.ellipse([40, py + 60, CW // 2, py + PHONE_H], fill='#2a0f00')
gd.ellipse([CW // 2, py + 60, CW - 40, py + PHONE_H], fill='#001a2e')
card = Image.blend(card, glow.filter(ImageFilter.GaussianBlur(120)), 0.85)
d = ImageDraw.Draw(card)


def fit(text, max_w, size):
    while size > 20:
        f = ImageFont.truetype(BOLD, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(BOLD, size)


def center(text, y, f, fill, cx=None):
    d.text((CW // 2 if cx is None else cx, y), text, font=f, fill=fill, anchor='mm')


# 1. Headline
y = 0
d.rectangle([0, 0, CW, HOOK_H], fill=ORANGE)
center('BROKEN PHONE?', 215, fit('BROKEN PHONE?', CW - 2 * PAD, 320), WHITE)
sub = 'We fix it. Most repairs done while you wait.'
center(sub, 425, fit(sub, CW - 3 * PAD, 84), DARK)
y = HOOK_H

# 2. Brand
logo = Image.open(os.path.join(OUT, 'assets', 'logo_pe_cropped.png')).convert('RGB')
LOGO_H = 180
logo = logo.resize((int(logo.width * LOGO_H / logo.height), LOGO_H), Image.LANCZOS)
cy = y + 145
fb = fit('PHONE ELECTRIK', CW - 2 * PAD - logo.width - 60, 180)
nw = d.textlength('PHONE ELECTRIK', font=fb)
x0 = (CW - (logo.width + 60 + nw)) // 2
card.paste(logo, (int(x0), cy - LOGO_H // 2))
tx = x0 + logo.width + 60
d.text((tx, cy), 'PHONE ', font=fb, fill=WHITE, anchor='lm')
d.text((tx + d.textlength('PHONE ', font=fb), cy), 'ELECTRIK', font=fb, fill=ORANGE, anchor='lm')
y += BRAND_H


# 3. Phones
def rounded(img, r=60):
    img = img.convert('RGBA')
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.width - 1, img.height - 1], r, fill=255)
    img.putalpha(m)
    return img


for i, fn in enumerate(['IMG_0096.jpeg', 'IMG_0097.jpeg']):
    im = Image.open(os.path.join(ROOT, fn))
    s = min(PHONE_H / im.height, (CW // 2 - 80) / im.width)
    im = rounded(im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS))
    sx = i * CW // 2 + (CW // 2 - im.width) // 2
    card.paste(im, (sx, y + PHONE_H - im.height), im)
y += PHONE_H
fl = ImageFont.truetype(BOLD, 50)
center('iPhone 17 Pro Max', y + LABEL_H // 2, fl, GREY, CW // 4)
center('Samsung Galaxy S26', y + LABEL_H // 2, fl, GREY, 3 * CW // 4)
y += LABEL_H

# 4. What we do (three clean lines, all centred)
d.rectangle([CW // 2 - 300, y + 30, CW // 2 + 300, y + 36], fill=ORANGE)
i1 = 'Screens  ·  Batteries  ·  Charging Ports  ·  Cameras'
i2 = 'We Buy & Sell Phones, Tablets & Laptops'
i3 = 'Any Brand  ·  Any Model  ·  90-Day Warranty  ·  Walk-Ins Welcome'
fi = ImageFont.truetype(BOLD, min(fit(i1, CW - 2 * PAD, 84).size, fit(i2, CW - 2 * PAD, 84).size))
center(i1, y + 135, fi, WHITE)
center(i2, y + 255, fi, ORANGE)
center(i3, y + 365, fit(i3, CW - 2 * PAD, 60), GREY)
y += INFO_H

# 5. Phone number
d.rectangle([0, y, CW, y + NUM_H], fill=ORANGE)
center('CALL OR TEXT', y + 75, ImageFont.truetype(BOLD, 62), DARK)
center('(323) 348-6756', y + 220, fit('(323) 348-6756', CW - 2 * PAD, 210), WHITE)
y += NUM_H

# 6. Where + QR
QR = FOOT_H - 150
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2, box_size=20)
q.add_data('https://phoneelectrik.com/links')
q.make(fit=True)
qimg = q.make_image(fill_color='black', back_color='white').convert('RGB').resize((QR, QR), Image.NEAREST)
qx = CW - PAD - QR
card.paste(qimg, (qx, y + 50))
center('SCAN ME', y + 50 + QR + 48, ImageFont.truetype(BOLD, 52), ORANGE, qx + QR // 2)
lw = qx - 2 * PAD
fa = fit('3025 Artesia Blvd STE 101', lw, 84)
fs = fit('Snap a photo & share with a friend!', lw, 62)
d.text((PAD, y + 110), '3025 Artesia Blvd STE 101', font=fa, fill=WHITE, anchor='lm')
d.text((PAD, y + 205), 'Torrance, CA 90504', font=fa, fill=WHITE, anchor='lm')
d.text((PAD, y + 315), 'Mon–Sat 9AM–8PM  ·  Sun 10AM–6PM', font=fs, fill=GREY, anchor='lm')
d.text((PAD, y + 420), 'Snap a photo & share with a friend!', font=fs, fill=ORANGE, anchor='lm')

# Page with white margin, rounded card
page = Image.new('RGB', (W, H), WHITE)
mask = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW - 1, CH - 1], 40, fill=255)
page.paste(card, (M, M), mask)

png = os.path.join(OUT, 'phone-electrik-bulletin-flyer.png')
pdf = os.path.join(OUT, 'phone-electrik-bulletin-flyer.pdf')
page.save(png, dpi=(DPI, DPI))
with open(pdf, 'wb') as f:
    f.write(img2pdf.convert(png, layout_fun=img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))))
print('saved', png, pdf)
