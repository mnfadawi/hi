"""Run: python3 make_poster.py  →  generates poster.png  (8.5×11 in @ 300 DPI)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import img2pdf, os

W, H   = 2550, 3300
BOLD   = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
BASE   = os.path.dirname(__file__)

BG     = '#0D0D0D'
ORANGE = '#F26522'
WHITE  = '#FFFFFF'
BLACK  = '#111111'

GAP    = 6
SLOT_W = (W - GAP) // 2
PAD    = 60

p1 = os.path.join(BASE, 'IMG_0096.jpeg')
p2 = os.path.join(BASE, 'IMG_0097.jpeg')

def natural_h(path):
    iw, ih = Image.open(path).size
    return int(ih * SLOT_W / iw)

# Cap phone height so lower sections get enough room
PHONE_H  = min(natural_h(p1), natural_h(p2), 1200)

HDR_H    = 580
LABEL_H  = 120
DEVICE_H = 310
WHITE_H  = 300
ORANGE_H = 360
FOOTER_H = H - HDR_H - PHONE_H - LABEL_H - DEVICE_H - WHITE_H - ORANGE_H

PHONE_Y  = HDR_H
LABEL_Y  = PHONE_Y  + PHONE_H
DEVICE_Y = LABEL_Y  + LABEL_H
WHITE_Y  = DEVICE_Y + DEVICE_H
ORANGE_Y = WHITE_Y  + WHITE_H
FOOTER_Y = ORANGE_Y + ORANGE_H

assert FOOTER_Y + FOOTER_H == H, f"sections sum to {FOOTER_Y+FOOTER_H}, need {H}"

# ── Canvas + glow ─────────────────────────────────────────────────────────────
canvas = Image.new('RGB', (W, H), BG)
glow   = Image.new('RGB', (W, H), BG)
gd     = ImageDraw.Draw(glow)
gd.ellipse([0,            PHONE_Y + 60, SLOT_W,        PHONE_Y + PHONE_H], fill='#2a0f00')
gd.ellipse([SLOT_W + GAP, PHONE_Y + 60, W,             PHONE_Y + PHONE_H], fill='#001a2e')
glow   = glow.filter(ImageFilter.GaussianBlur(120))
canvas = Image.blend(canvas, glow, alpha=0.85)
draw   = ImageDraw.Draw(canvas)

def fit_font(text, max_w, start_size, step=4):
    size = start_size
    while size > 24:
        f = ImageFont.truetype(BOLD, size)
        bb = draw.textbbox((0, 0), text, font=f)
        if (bb[2] - bb[0]) <= max_w:
            return f, bb
        size -= step
    f = ImageFont.truetype(BOLD, size)
    return f, draw.textbbox((0, 0), text, font=f)

# ── Orange banner at the very top: CELL PHONE REPAIR ─────────────────────────
BANNER_H = 150
draw.rectangle([0, 0, W, BANNER_H], fill=ORANGE)
fnt_banner, _ = fit_font('CELL PHONE REPAIR', W - PAD * 2, 130)
draw.text((W // 2, BANNER_H // 2), 'CELL PHONE REPAIR',
          font=fnt_banner, fill=WHITE, anchor='mm')

# ── Header: logo top-left + PHONE ELECTRIK to the right ──────────────────────
logo_img = Image.open(os.path.join(BASE, 'logo_pe_cropped.png')).convert('RGB')
lw, lh   = logo_img.size
LOGO_H   = 240
LOGO_W   = int(lw * LOGO_H / lh)
logo_img = logo_img.resize((LOGO_W, LOGO_H), Image.LANCZOS)

TAG_RESERVE  = 130
CONTENT_TOP  = BANNER_H + 14
CONTENT_BOT  = HDR_H - TAG_RESERVE
content_cy   = (CONTENT_TOP + CONTENT_BOT) // 2

# Logo — centered vertically in the content zone
logo_y = content_cy - LOGO_H // 2
canvas.paste(logo_img, (PAD, logo_y))

logo_r     = PAD + LOGO_W + 80
TEXT_MAX_W = W - logo_r - PAD

# "PHONE ELECTRIK" — centered vertically with the logo
fnt_brand, _ = fit_font('PHONE ELECTRIK', TEXT_MAX_W, 240)
bb_b    = draw.textbbox((0, 0), 'PHONE ELECTRIK', font=fnt_brand)
brand_h = bb_b[3] - bb_b[1]
BRAND_Y = content_cy - brand_h // 2

bb_p  = draw.textbbox((0, 0), 'PHONE', font=fnt_brand)
bb_sp = draw.textbbox((0, 0), ' ',     font=fnt_brand)
draw.text((logo_r, BRAND_Y), 'PHONE', font=fnt_brand, fill=WHITE)
draw.text((logo_r + (bb_p[2]-bb_p[0]) + (bb_sp[2]-bb_sp[0]), BRAND_Y),
          'ELECTRIK', font=fnt_brand, fill=ORANGE)

# Tagline
TAG_Y   = CONTENT_BOT + (TAG_RESERVE - 80) // 2
tag_txt = 'Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers  ·  Game Consoles'
fnt_tag, bb_tag = fit_font(tag_txt, W - PAD * 2, 80)
draw.text(((W - (bb_tag[2]-bb_tag[0])) // 2, TAG_Y), tag_txt, font=fnt_tag, fill=ORANGE)

# ── Phone images ──────────────────────────────────────────────────────────────
def round_corners(img, radius=80):
    img = img.convert('RGBA')
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width-1, img.height-1], radius=radius, fill=255)
    img.putalpha(mask)
    return img

def paste_phone(path, slot_x):
    img = Image.open(path)
    iw, ih = img.size
    scale = PHONE_H / ih
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    img = round_corners(img)
    x = slot_x + (SLOT_W - nw) // 2
    y = PHONE_Y + (PHONE_H - nh)
    canvas.paste(img, (x, y), mask=img.split()[3])

paste_phone(p1, 0)
paste_phone(p2, SLOT_W + GAP)

# ── Phone labels ──────────────────────────────────────────────────────────────
fnt_lbl = ImageFont.truetype(BOLD, 76)
lbl1, lbl2 = 'iPhone 17 Pro Max', 'Samsung Galaxy S26'
bb1 = draw.textbbox((0, 0), lbl1, font=fnt_lbl)
bb2 = draw.textbbox((0, 0), lbl2, font=fnt_lbl)
LBL_Y = LABEL_Y + (LABEL_H - (bb1[3]-bb1[1])) // 2
draw.text((SLOT_W//2 - (bb1[2]-bb1[0])//2, LBL_Y), lbl1, font=fnt_lbl, fill=ORANGE)
draw.text((SLOT_W+GAP + SLOT_W//2 - (bb2[2]-bb2[0])//2, LBL_Y), lbl2, font=fnt_lbl, fill=WHITE)

# ── Device strip ──────────────────────────────────────────────────────────────
draw.rectangle([0, DEVICE_Y, W, DEVICE_Y+DEVICE_H], fill='#181818')
draw.rectangle([0, DEVICE_Y, W, DEVICE_Y+5], fill=ORANGE)

dev_line1 = 'We Fix Any Device — Any Brand, Any Model'
dev_line2 = 'Apple  ·  Samsung  ·  Motorola  ·  LG  ·  OnePlus  ·  Google Pixel  ·  & More'
dev_line3 = 'Bring it in — We are happy to help!'

fnt_d1, bb_d1 = fit_font(dev_line1, W - 80, 84)
fnt_d2, bb_d2 = fit_font(dev_line2, W - 80, 72)
fnt_d3, bb_d3 = fit_font(dev_line3, W - 80, 68)

gap12 = 18
gap23 = 14
total_dev_h = ((bb_d1[3]-bb_d1[1]) + gap12 +
               (bb_d2[3]-bb_d2[1]) + gap23 +
               (bb_d3[3]-bb_d3[1]))
dy = DEVICE_Y + 5 + (DEVICE_H - 5 - total_dev_h) // 2

draw.text(((W-(bb_d1[2]-bb_d1[0]))//2, dy), dev_line1, font=fnt_d1, fill=ORANGE)
dy += (bb_d1[3]-bb_d1[1]) + gap12
draw.text(((W-(bb_d2[2]-bb_d2[0]))//2, dy), dev_line2, font=fnt_d2, fill=WHITE)
dy += (bb_d2[3]-bb_d2[1]) + gap23
draw.text(((W-(bb_d3[2]-bb_d3[0]))//2, dy), dev_line3, font=fnt_d3, fill=WHITE)

# ── White band: BUY · SELL · REPAIR ──────────────────────────────────────────
draw.rectangle([0, WHITE_Y, W, WHITE_Y+WHITE_H], fill=WHITE)
draw.rectangle([0, WHITE_Y,   W, WHITE_Y+10],        fill=BLACK)
draw.rectangle([0, WHITE_Y+WHITE_H-10, W, WHITE_Y+WHITE_H], fill=BLACK)

bsr_parts = [('REPAIR', ORANGE), ('  ·  ', '#333'), ('SELL', BLACK), ('  ·  ', '#333'), ('BUY', BLACK)]
bsr_sz = 210
while bsr_sz > 60:
    fb = ImageFont.truetype(BOLD, bsr_sz)
    tw = sum(draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0] for t,_ in bsr_parts)
    if tw <= W - 80: break
    bsr_sz -= 4
tw = sum(draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0] for t,_ in bsr_parts)
x  = (W - tw) // 2                  # horizontally centered
cy = WHITE_Y + WHITE_H // 2         # vertical center of band
for txt, clr in bsr_parts:
    bb = draw.textbbox((0,0), txt, font=fb)
    draw.text((x, cy), txt, font=fb, fill=clr, anchor='lm')
    x += bb[2] - bb[0]

# ── Orange band: phone number ─────────────────────────────────────────────────
draw.rectangle([0, ORANGE_Y, W, ORANGE_Y+ORANGE_H], fill=ORANGE)
fnt_num, _ = fit_font('(323) 348-6756', W - 80, 280)
draw.text((W//2, ORANGE_Y + ORANGE_H//2), '(323) 348-6756',
          font=fnt_num, fill=WHITE, anchor='mm')

# ── Footer ────────────────────────────────────────────────────────────────────
draw.rectangle([0, FOOTER_Y, W, H], fill='#141414')
draw.rectangle([0, FOOTER_Y, W, FOOTER_Y+12], fill=ORANGE)

footer_lines = [
    ('WALK-IN  ·  NO APPOINTMENT NEEDED',                ORANGE),
    ('MON–SAT  9AM–8PM   ·   SUN  10AM–6PM',             WHITE),
    ('3025 Artesia Blvd STE 101  ·  Torrance, CA 90504', WHITE),
]

fnt_footer, _ = fit_font(
    max(footer_lines, key=lambda l: len(l[0]))[0], W - PAD*2, 130)

footer_bbs = [draw.textbbox((0,0), t, font=fnt_footer) for t, _ in footer_lines]
line_hs    = [bb[3]-bb[1] for bb in footer_bbs]
line_gap   = 32
total_h    = sum(line_hs) + line_gap * (len(footer_lines)-1)
y = FOOTER_Y + 12 + (FOOTER_H - 12 - total_h) // 2

for (text, color), bb, lh in zip(footer_lines, footer_bbs, line_hs):
    draw.text(((W-(bb[2]-bb[0]))//2, y), text, font=fnt_footer, fill=color)
    y += lh + line_gap

# ── Save ─────────────────────────────────────────────────────────────────────
png_out = os.path.join(BASE, 'poster.png')
pdf_out = os.path.join(BASE, 'poster.pdf')
canvas.save(png_out, dpi=(300, 300))
letter = (img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11))
with open(pdf_out, 'wb') as f:
    f.write(img2pdf.convert(png_out, layout_fun=img2pdf.get_layout_fun(letter)))
print('Saved poster.png + poster.pdf')
