"""Run: python3 make_poster.py  →  generates poster.png  (8.5×11 in @ 300 DPI)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg, io, os

W, H   = 2550, 3300
BOLD   = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
BASE   = os.path.dirname(__file__)

BG     = '#0D0D0D'
ORANGE = '#F26522'
WHITE  = '#FFFFFF'
GREY   = '#AAAAAA'
BLACK  = '#111111'
BLUE   = '#4fc3e8'

GAP    = 6
SLOT_W = (W - GAP) // 2   # 1272 px each phone slot
PAD    = 60
LOGO_SZ = 160

# ── Measure phone images FIRST so sections never overflow ─────────────────────
p1 = os.path.join(BASE, 'IMG_0096.jpeg')
p2 = os.path.join(BASE, 'IMG_0097.jpeg')

def natural_h(path):
    iw, ih = Image.open(path).size
    return int(ih * SLOT_W / iw)

TARGET_H = min(natural_h(p1), natural_h(p2))   # 1534 px — same height both phones

# Fixed section heights (everything except footer which fills the rest)
HDR_H    = 380
PHONE_H  = TARGET_H          # exact — phones never overflow
LABEL_H  = 80
DEVICE_H = 80
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

def center_text(text, y, color, size):
    fnt, bb = fit_font(text, W - PAD * 2, size)
    draw.text(((W - (bb[2]-bb[0])) // 2, y), text, font=fnt, fill=color)
    return bb[3] - bb[1]   # return actual rendered height

# ── Logo ──────────────────────────────────────────────────────────────────────
svg_bytes = cairosvg.svg2png(url=os.path.join(BASE, 'logo.svg'),
                              output_width=LOGO_SZ, output_height=LOGO_SZ)
logo_img = Image.open(io.BytesIO(svg_bytes)).convert('RGBA')
r, g, b, a = logo_img.split()
tinted = Image.merge('RGBA', (
    r.point(lambda x: int(x * .95)),
    g.point(lambda x: int(x * .40)),
    b.point(lambda x: int(x * .10)), a))
LOGO_Y = 30
canvas.paste(tinted, (PAD, LOGO_Y), mask=a)

# ── Brand: PHONE (white) ElectriK (orange) — same font, same size ────────────
logo_r     = PAD + LOGO_SZ + 28
TEXT_MAX_W = W - logo_r - PAD
fnt_brand, _ = fit_font('PHONE ElectriK', TEXT_MAX_W, 240)
BRAND_Y = max(LOGO_Y + (LOGO_SZ - fnt_brand.size) // 2, 12)

bb_p  = draw.textbbox((0, 0), 'PHONE', font=fnt_brand)
bb_sp = draw.textbbox((0, 0), ' ',     font=fnt_brand)
draw.text((logo_r, BRAND_Y), 'PHONE', font=fnt_brand, fill=WHITE)
draw.text((logo_r + (bb_p[2]-bb_p[0]) + (bb_sp[2]-bb_sp[0]), BRAND_Y),
          'ElectriK', font=fnt_brand, fill=ORANGE)

# ── Tagline ───────────────────────────────────────────────────────────────────
TAG_Y   = BRAND_Y + fnt_brand.size + 10
tag_txt = 'Repair:  Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers'
fnt_tag, bb_tag = fit_font(tag_txt, W - PAD * 2, 60)
draw.text(((W - (bb_tag[2]-bb_tag[0])) // 2, TAG_Y), tag_txt, font=fnt_tag, fill=GREY)

# ── Phone images — exact height, no overflow ──────────────────────────────────
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

# ── Phone labels ──────────────────────────────────────────────────────────────
fnt_lbl = ImageFont.truetype(BOLD, 58)
lbl1, lbl2 = 'iPhone 17 Pro Max', 'Samsung Galaxy S26'
bb1 = draw.textbbox((0, 0), lbl1, font=fnt_lbl)
bb2 = draw.textbbox((0, 0), lbl2, font=fnt_lbl)
LBL_Y = LABEL_Y + (LABEL_H - (bb1[3]-bb1[1])) // 2
draw.text((SLOT_W//2 - (bb1[2]-bb1[0])//2, LBL_Y), lbl1, font=fnt_lbl, fill=ORANGE)
draw.text((SLOT_W+GAP + SLOT_W//2 - (bb2[2]-bb2[0])//2, LBL_Y), lbl2, font=fnt_lbl, fill=BLUE)

# ── Device strip ──────────────────────────────────────────────────────────────
draw.rectangle([0, DEVICE_Y, W, DEVICE_Y+DEVICE_H], fill='#1a1a1a')
dev_txt = 'We Repair:  Cell Phones  ·  iPads  ·  MacBooks  ·  Laptops  ·  Computers'
fnt_dev, bb_dev = fit_font(dev_txt, W-100, 58)
dev_y = DEVICE_Y + (DEVICE_H - (bb_dev[3]-bb_dev[1])) // 2
draw.text(((W-(bb_dev[2]-bb_dev[0]))//2, dev_y), dev_txt, font=fnt_dev, fill=WHITE)

# ── White band: BUY · SELL · REPAIR ──────────────────────────────────────────
draw.rectangle([0, WHITE_Y, W, WHITE_Y+WHITE_H], fill=WHITE)
draw.rectangle([0, WHITE_Y, W, WHITE_Y+8], fill=BLACK)
draw.rectangle([0, WHITE_Y+WHITE_H-8, W, WHITE_Y+WHITE_H], fill=BLACK)

bsr_parts = [('BUY',BLACK),('  ·  ','#888'),('SELL',BLACK),('  ·  ','#888'),('REPAIR',ORANGE)]
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

# ── Footer — large, bright, readable from far away ───────────────────────────
draw.rectangle([0, FOOTER_Y, W, H], fill='#141414')
draw.rectangle([0, FOOTER_Y, W, FOOTER_Y+8], fill=ORANGE)

lines = [
    ('WALK-IN  ·  NO APPOINTMENT NEEDED',               ORANGE),
    ('MON–SAT  9AM–8PM   ·   SUN  10AM–6PM',            WHITE),
    ('3025 Artesia Blvd STE 101  ·  Torrance, CA 90504', WHITE),
]

# Size all three lines to the same large font so they look uniform
fnt_footer, _ = fit_font(max(lines, key=lambda l: len(l[0]))[0], W-PAD*2, 110)

line_h   = fnt_footer.size
line_gap = 34
total_h  = line_h * len(lines) + line_gap * (len(lines)-1)
y = FOOTER_Y + 8 + (FOOTER_H - 8 - total_h) // 2

for text, color in lines:
    bb = draw.textbbox((0,0), text, font=fnt_footer)
    draw.text(((W-(bb[2]-bb[0]))//2, y), text, font=fnt_footer, fill=color)
    y += line_h + line_gap

# ── Save PNG + PDF ────────────────────────────────────────────────────────────
png_out = os.path.join(BASE, 'poster.png')
pdf_out = os.path.join(BASE, 'poster.pdf')
canvas.save(png_out, dpi=(300, 300))
canvas.save(pdf_out, 'PDF', resolution=300)
print('Saved:', png_out)
print('Saved:', pdf_out)
