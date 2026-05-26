"""Run: python3 make_poster.py  →  generates poster.png"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg, io, os

W, H = 2160, 2880
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

BG     = '#0D0D0D'
ORANGE = '#F26522'
WHITE  = '#FFFFFF'
GREY   = '#999999'
BLACK  = '#111111'
BLUE   = '#4fc3e8'

# Section heights — must sum to H=2880
HDR_H    = 400
PHONE_H  = 1350
LABEL_H  = 90
DEVICE_H = 90
WHITE_H  = 300
ORANGE_H = 360
FOOTER_H = 290  # 400+1350+90+90+300+360+290 = 2880

HDR_Y    = 0
PHONE_Y  = HDR_H
LABEL_Y  = PHONE_Y  + PHONE_H
DEVICE_Y = LABEL_Y  + LABEL_H
WHITE_Y  = DEVICE_Y + DEVICE_H
ORANGE_Y = WHITE_Y  + WHITE_H
FOOTER_Y = ORANGE_Y + ORANGE_H

assert FOOTER_Y + FOOTER_H == H

PAD     = 60
LOGO_SZ = 160
GAP     = 6
SLOT_W  = (W - GAP) // 2  # 1077

# ── Glow layer (phone background atmosphere) ──────────────────────────────────
canvas = Image.new('RGB', (W, H), BG)
glow   = Image.new('RGB', (W, H), BG)
gd     = ImageDraw.Draw(glow)
gd.ellipse([0,           PHONE_Y + 60, SLOT_W,       PHONE_Y + PHONE_H], fill='#1f0b00')
gd.ellipse([SLOT_W + GAP, PHONE_Y + 60, W,            PHONE_Y + PHONE_H], fill='#001320')
glow   = glow.filter(ImageFilter.GaussianBlur(100))
canvas = Image.blend(canvas, glow, alpha=0.78)

draw = ImageDraw.Draw(canvas)

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

# ── Logo ──────────────────────────────────────────────────────────────────────
svg_bytes = cairosvg.svg2png(url=os.path.join(os.path.dirname(__file__), 'logo.svg'),
                              output_width=LOGO_SZ, output_height=LOGO_SZ)
logo_img = Image.open(io.BytesIO(svg_bytes)).convert('RGBA')
r, g, b, a = logo_img.split()
tinted = Image.merge('RGBA', (
    r.point(lambda x: int(x * .95)),
    g.point(lambda x: int(x * .40)),
    b.point(lambda x: int(x * .10)), a))
LOGO_Y = 40
canvas.paste(tinted, (PAD, LOGO_Y), mask=a)

# ── Brand: PHONE (white) ElectriK (orange) — same line ───────────────────────
logo_r     = PAD + LOGO_SZ + 28
TEXT_MAX_W = W - logo_r - PAD
fnt_brand, _ = fit_font('PHONE ElectriK', TEXT_MAX_W, 240)
BRAND_Y = max(LOGO_Y + (LOGO_SZ - fnt_brand.size) // 2, 16)

bb_p  = draw.textbbox((0, 0), 'PHONE', font=fnt_brand)
bb_sp = draw.textbbox((0, 0), ' ',     font=fnt_brand)
draw.text((logo_r, BRAND_Y), 'PHONE', font=fnt_brand, fill=WHITE)
ek_x = logo_r + (bb_p[2] - bb_p[0]) + (bb_sp[2] - bb_sp[0])
draw.text((ek_x, BRAND_Y), 'ElectriK', font=fnt_brand, fill=ORANGE)

# ── Tagline (centered under brand) ───────────────────────────────────────────
TAG_Y   = BRAND_Y + fnt_brand.size + 16
tag_txt = 'Repair:  Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers'
fnt_tag, bb_tag = fit_font(tag_txt, W - PAD * 2, 60)
draw.text(((W - (bb_tag[2] - bb_tag[0])) // 2, TAG_Y), tag_txt, font=fnt_tag, fill=GREY)

# ── Phone images (cover-fill, edge-to-edge) ───────────────────────────────────
def paste_phone_cover(path, slot_x):
    img = Image.open(path)
    iw, ih = img.size
    scale = max(SLOT_W / iw, PHONE_H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    if nw > SLOT_W:
        cx = (nw - SLOT_W) // 2
        img = img.crop((cx, 0, cx + SLOT_W, nh))
        nw = SLOT_W
    if nh > PHONE_H:
        img = img.crop((0, nh - PHONE_H, nw, nh))
        nh = PHONE_H
    canvas.paste(img, (slot_x, PHONE_Y + (PHONE_H - nh)))

base = os.path.dirname(__file__)
paste_phone_cover(os.path.join(base, 'IMG_0096.jpeg'), 0)
paste_phone_cover(os.path.join(base, 'IMG_0097.jpeg'), SLOT_W + GAP)

# ── Phone labels ──────────────────────────────────────────────────────────────
fnt_lbl = ImageFont.truetype(BOLD, 56)
lbl1, lbl2 = 'iPhone 17 Pro Max', 'Samsung Galaxy S26'
bb1 = draw.textbbox((0, 0), lbl1, font=fnt_lbl)
bb2 = draw.textbbox((0, 0), lbl2, font=fnt_lbl)
LBL_Y = LABEL_Y + (LABEL_H - (bb1[3] - bb1[1])) // 2
draw.text((SLOT_W // 2 - (bb1[2] - bb1[0]) // 2, LBL_Y), lbl1, font=fnt_lbl, fill=ORANGE)
draw.text((SLOT_W + GAP + SLOT_W // 2 - (bb2[2] - bb2[0]) // 2, LBL_Y), lbl2, font=fnt_lbl, fill=BLUE)

# ── Device strip ──────────────────────────────────────────────────────────────
draw.rectangle([0, DEVICE_Y, W, DEVICE_Y + DEVICE_H], fill='#161616')
dev_txt = 'We Repair:  Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers'
fnt_dev, bb_dev = fit_font(dev_txt, W - 100, 58)
dev_y = DEVICE_Y + (DEVICE_H - (bb_dev[3] - bb_dev[1])) // 2
draw.text(((W - (bb_dev[2] - bb_dev[0])) // 2, dev_y), dev_txt, font=fnt_dev, fill=GREY)

# ── White band: BUY · SELL · REPAIR ──────────────────────────────────────────
draw.rectangle([0, WHITE_Y, W, WHITE_Y + WHITE_H], fill=WHITE)
draw.rectangle([0, WHITE_Y, W, WHITE_Y + 8], fill=BLACK)
draw.rectangle([0, WHITE_Y + WHITE_H - 8, W, WHITE_Y + WHITE_H], fill=BLACK)

bsr_parts = [('BUY', BLACK), ('  ·  ', '#888'), ('SELL', BLACK), ('  ·  ', '#888'), ('REPAIR', ORANGE)]
bsr_sz = 200
while bsr_sz > 60:
    fb = ImageFont.truetype(BOLD, bsr_sz)
    tw = sum((draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0]) for t,_ in bsr_parts)
    if tw <= W - 80:
        break
    bsr_sz -= 4
bsr_h_bb = draw.textbbox((0, 0), 'BUY', font=fb)
bsr_h_val = bsr_h_bb[3] - bsr_h_bb[1]
tw = sum((draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0]) for t,_ in bsr_parts)
x = (W - tw) // 2
y = WHITE_Y + (WHITE_H - bsr_h_val) // 2
for txt, clr in bsr_parts:
    bb = draw.textbbox((0, 0), txt, font=fb)
    draw.text((x, y), txt, font=fb, fill=clr)
    x += bb[2] - bb[0]

# ── Orange band: phone number ─────────────────────────────────────────────────
draw.rectangle([0, ORANGE_Y, W, ORANGE_Y + ORANGE_H], fill=ORANGE)
fnt_num, bb_num = fit_font('(323)  348-6756', W - 80, 270)
draw.text(
    ((W - (bb_num[2] - bb_num[0])) // 2,
     ORANGE_Y + (ORANGE_H - (bb_num[3] - bb_num[1])) // 2),
    '(323)  348-6756', font=fnt_num, fill=WHITE)

# ── Footer ────────────────────────────────────────────────────────────────────
draw.rectangle([0, FOOTER_Y, W, H], fill=BG)
fnt_wi  = ImageFont.truetype(BOLD, 72)
fnt_hrs = ImageFont.truetype(BOLD, 58)
fnt_adr = ImageFont.truetype(BOLD, 48)

wi_txt  = 'WALK-INS WELCOME'
hrs_txt = 'MON–SAT  9AM–8PM   ·   SUN  10AM–6PM'
adr_txt = '3025 Artesia Blvd STE 101   ·   Torrance, CA 90504'

bb = draw.textbbox((0, 0), wi_txt, font=fnt_wi)
draw.text(((W - (bb[2] - bb[0])) // 2, FOOTER_Y + 18), wi_txt, font=fnt_wi, fill=ORANGE)
bb = draw.textbbox((0, 0), hrs_txt, font=fnt_hrs)
draw.text(((W - (bb[2] - bb[0])) // 2, FOOTER_Y + 106), hrs_txt, font=fnt_hrs, fill=WHITE)
bb = draw.textbbox((0, 0), adr_txt, font=fnt_adr)
draw.text(((W - (bb[2] - bb[0])) // 2, FOOTER_Y + 178), adr_txt, font=fnt_adr, fill=GREY)

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), 'poster.png')
canvas.save(out)
print('Saved:', out)
