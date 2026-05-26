"""Run: python3 make_poster.py  →  generates poster.png  (8.5×11 in @ 300 DPI)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg, io, os

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
LOGO_SZ = 160

# ── Measure phone images FIRST so sections never overflow ─────────────────────
p1 = os.path.join(BASE, 'IMG_0096.jpeg')
p2 = os.path.join(BASE, 'IMG_0097.jpeg')

def natural_h(path):
    iw, ih = Image.open(path).size
    return int(ih * SLOT_W / iw)

TARGET_H = min(natural_h(p1), natural_h(p2))

HDR_H    = 560
PHONE_H  = TARGET_H
LABEL_H  = 90
DEVICE_H = 230
WHITE_H  = 260
ORANGE_H = 320
FOOTER_H = H - HDR_H - PHONE_H - LABEL_H - DEVICE_H - WHITE_H - ORANGE_H

PHONE_Y  = HDR_H
LABEL_Y  = PHONE_Y  + PHONE_H
DEVICE_Y = LABEL_Y  + LABEL_H
WHITE_Y  = DEVICE_Y + DEVICE_H
ORANGE_Y = WHITE_Y  + WHITE_H
FOOTER_Y = ORANGE_Y + ORANGE_H

assert FOOTER_Y + FOOTER_H == H, f"sections sum to {FOOTER_Y+FOOTER_H}, need {H}"

# ── Glow ─────────────────────────────────────────────────────────────────────
canvas = Image.new('RGB', (W, H), BG)
glow   = Image.new('RGB', (W, H), BG)
gd     = ImageDraw.Draw(glow)
gd.ellipse([0,            PHONE_Y + 60, SLOT_W,        PHONE_Y + PHONE_H], fill='#1f0b00')
gd.ellipse([SLOT_W + GAP, PHONE_Y + 60, W,             PHONE_Y + PHONE_H], fill='#001320')
glow   = glow.filter(ImageFilter.GaussianBlur(100))
canvas = Image.blend(canvas, glow, alpha=0.78)
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

# ── Logo (PE brand logo — centered, fills header) ────────────────────────────
logo_img = Image.open(os.path.join(BASE, 'logo_pe_cropped.png')).convert('RGB')
lw, lh   = logo_img.size   # 858 × 606
logo_h   = HDR_H - 110     # leave room for tagline below
logo_w   = int(lw * logo_h / lh)
logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
logo_x   = (W - logo_w) // 2
canvas.paste(logo_img, (logo_x, 18))

# ── Tagline — WHITE, large, below the logo ───────────────────────────────────
TAG_Y   = 18 + logo_h + 14
tag_txt = 'Repair:  Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers  ·  Game Consoles'
fnt_tag, bb_tag = fit_font(tag_txt, W - PAD * 2, 68)
draw.text(((W - (bb_tag[2]-bb_tag[0])) // 2, TAG_Y), tag_txt, font=fnt_tag, fill=WHITE)

# ── Phone images ──────────────────────────────────────────────────────────────
def round_corners(img, radius=70):
    img = img.convert('RGBA')
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width-1, img.height-1], radius=radius, fill=255)
    img.putalpha(mask)
    return img

def paste_phone(path, slot_x):
    img = Image.open(path)
    iw, ih = img.size
    scale = TARGET_H / ih
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    img = round_corners(img)
    x = slot_x + (SLOT_W - nw) // 2
    y = PHONE_Y + (PHONE_H - nh)
    canvas.paste(img, (x, y), mask=img.split()[3])

paste_phone(p1, 0)
paste_phone(p2, SLOT_W + GAP)

# ── Phone labels — both WHITE for maximum visibility ─────────────────────────
fnt_lbl = ImageFont.truetype(BOLD, 62)
lbl1, lbl2 = 'iPhone 17 Pro Max', 'Samsung Galaxy S26'
bb1 = draw.textbbox((0, 0), lbl1, font=fnt_lbl)
bb2 = draw.textbbox((0, 0), lbl2, font=fnt_lbl)
LBL_Y = LABEL_Y + (LABEL_H - (bb1[3]-bb1[1])) // 2
draw.text((SLOT_W//2 - (bb1[2]-bb1[0])//2, LBL_Y), lbl1, font=fnt_lbl, fill=ORANGE)
draw.text((SLOT_W+GAP + SLOT_W//2 - (bb2[2]-bb2[0])//2, LBL_Y), lbl2, font=fnt_lbl, fill=WHITE)

# ── Device strip — all lines WHITE or ORANGE, nothing grey ───────────────────
draw.rectangle([0, DEVICE_Y, W, DEVICE_Y+DEVICE_H], fill='#1a1a1a')

dev_line1 = 'We Repair Any Device — Any Brand, Any Model'
dev_line2 = 'Apple  ·  Samsung  ·  Motorola  ·  LG  ·  OnePlus  ·  Google Pixel  ·  & Many More Makes & Models'
dev_line3 = "Don't see your device? Bring it in — We are more than happy to help you!"

fnt_d1, bb_d1 = fit_font(dev_line1, W-100, 66)
fnt_d2, bb_d2 = fit_font(dev_line2, W-100, 56)
fnt_d3, bb_d3 = fit_font(dev_line3, W-100, 54)

total_dev_h = ((bb_d1[3]-bb_d1[1]) + 16 +
               (bb_d2[3]-bb_d2[1]) + 16 +
               (bb_d3[3]-bb_d3[1]))
dy = DEVICE_Y + (DEVICE_H - total_dev_h) // 2

draw.text(((W-(bb_d1[2]-bb_d1[0]))//2, dy), dev_line1, font=fnt_d1, fill=ORANGE)
dy += (bb_d1[3]-bb_d1[1]) + 16
draw.text(((W-(bb_d2[2]-bb_d2[0]))//2, dy), dev_line2, font=fnt_d2, fill=WHITE)
dy += (bb_d2[3]-bb_d2[1]) + 16
draw.text(((W-(bb_d3[2]-bb_d3[0]))//2, dy), dev_line3, font=fnt_d3, fill=WHITE)

# ── White band: BUY · SELL · REPAIR ──────────────────────────────────────────
draw.rectangle([0, WHITE_Y, W, WHITE_Y+WHITE_H], fill=WHITE)
draw.rectangle([0, WHITE_Y, W, WHITE_Y+8], fill=BLACK)
draw.rectangle([0, WHITE_Y+WHITE_H-8, W, WHITE_Y+WHITE_H], fill=BLACK)

bsr_parts = [('BUY',BLACK),('  ·  ','#555'),('SELL',BLACK),('  ·  ','#555'),('REPAIR',ORANGE)]
bsr_sz = 190
while bsr_sz > 60:
    fb = ImageFont.truetype(BOLD, bsr_sz)
    tw = sum((draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0]) for t,_ in bsr_parts)
    if tw <= W-80: break
    bsr_sz -= 4
bsr_h = draw.textbbox((0,0),'BUY',font=fb)[3]-draw.textbbox((0,0),'BUY',font=fb)[1]
tw    = sum((draw.textbbox((0,0),t,font=fb)[2]-draw.textbbox((0,0),t,font=fb)[0]) for t,_ in bsr_parts)
x, y  = (W-tw)//2, WHITE_Y+(WHITE_H-bsr_h)//2
for txt, clr in bsr_parts:
    bb = draw.textbbox((0,0), txt, font=fb)
    draw.text((x, y), txt, font=fb, fill=clr)
    x += bb[2]-bb[0]

# ── Orange band: phone number ─────────────────────────────────────────────────
draw.rectangle([0, ORANGE_Y, W, ORANGE_Y+ORANGE_H], fill=ORANGE)
fnt_num, _ = fit_font('(323) 348-6756', W-80, 260)
draw.text((W//2, ORANGE_Y+ORANGE_H//2), '(323) 348-6756',
          font=fnt_num, fill=WHITE, anchor='mm')

# ── Footer — large, bright, all WHITE/ORANGE ─────────────────────────────────
draw.rectangle([0, FOOTER_Y, W, H], fill='#161616')
draw.rectangle([0, FOOTER_Y, W, FOOTER_Y+10], fill=ORANGE)

footer_lines = [
    ('WALK-IN  ·  NO APPOINTMENT NEEDED',                  ORANGE),
    ('MON–SAT  9AM–8PM   ·   SUN  10AM–6PM',               WHITE),
    ('3025 Artesia Blvd STE 101  ·  Torrance, CA 90504',   WHITE),
]

# Size every footer line to fill the full width at the same size
fnt_footer, _ = fit_font(
    max(footer_lines, key=lambda l: len(l[0]))[0], W - PAD*2, 120)

line_h   = fnt_footer.size
line_gap = 40
total_h  = line_h * len(footer_lines) + line_gap * (len(footer_lines)-1)
y = FOOTER_Y + 10 + (FOOTER_H - 10 - total_h) // 2

for text, color in footer_lines:
    bb = draw.textbbox((0,0), text, font=fnt_footer)
    draw.text(((W-(bb[2]-bb[0]))//2, y), text, font=fnt_footer, fill=color)
    y += line_h + line_gap

# ── Save ─────────────────────────────────────────────────────────────────────
canvas.save(os.path.join(BASE, 'poster.png'), dpi=(300, 300))
canvas.save(os.path.join(BASE, 'poster.pdf'), 'PDF', resolution=300)
print('Saved poster.png + poster.pdf')
