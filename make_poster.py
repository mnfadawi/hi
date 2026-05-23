"""Run: python3 make_poster.py  →  generates poster.png"""
from PIL import Image, ImageDraw, ImageFont
import cairosvg, io, os

W, H = 2160, 2880
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

BG     = '#0D0D0D'
ORANGE = '#F26522'
WHITE  = '#FFFFFF'
GREY   = '#AAAAAA'
BLACK  = '#111111'

PINK_H   = 1950
WHITE_H  = 330
ORANGE_H = 360
FOOTER_H = H - PINK_H - WHITE_H - ORANGE_H

canvas = Image.new('RGB', (W, H), BG)
draw   = ImageDraw.Draw(canvas)

PAD = 80
GAP = 60

def fit_font(text, max_w, start_size):
    size = start_size
    while size > 20:
        f = ImageFont.truetype(BOLD, size)
        bb = draw.textbbox((0,0), text, font=f)
        if (bb[2]-bb[0]) <= max_w:
            return f, bb
        size -= 4
    f = ImageFont.truetype(BOLD, size)
    return f, draw.textbbox((0,0), text, font=f)

# Logo
svg_bytes = cairosvg.svg2png(url=os.path.join(os.path.dirname(__file__), 'logo.svg'),
                              output_width=160, output_height=160)
logo_img = Image.open(io.BytesIO(svg_bytes)).convert('RGBA')
r,g,b,a  = logo_img.split()
tinted   = Image.merge('RGBA',(r.point(lambda x:int(x*.95)),g.point(lambda x:int(x*.40)),b.point(lambda x:int(x*.10)),a))
canvas.paste(tinted,(PAD,55),mask=a)

# Brand text
BRAND_SIZE = 195
fnt_brand = ImageFont.truetype(BOLD, BRAND_SIZE)
fnt_tag   = ImageFont.truetype(BOLD, 64)
logo_r = PAD + 160 + 30
draw.text((logo_r, 48), 'PHONE',    font=fnt_brand, fill=WHITE)
draw.text((logo_r, 48+BRAND_SIZE+8), 'ElectriK', font=fnt_brand, fill=ORANGE)
TAG_Y = 48 + BRAND_SIZE*2 + 30
draw.text((PAD, TAG_Y), 'CELL PHONE  +  TABLET REPAIR AND ACCESSORIES', font=fnt_tag, fill=GREY)

# Phone images
PHONE_TOP = TAG_Y + 90
PHONE_H   = PINK_H - PHONE_TOP
PHONE_W   = (W - PAD*2 - GAP) // 2

def paste_phone(path, slot_x):
    img = Image.open(path)
    iw, ih = img.size
    scale = min(PHONE_W/iw, PHONE_H/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = slot_x + (PHONE_W-nw)//2
    y = PHONE_TOP + (PHONE_H-nh)
    canvas.paste(img,(x,y))

base = os.path.dirname(__file__)
paste_phone(os.path.join(base,'IMG_0096.jpeg'), PAD)
paste_phone(os.path.join(base,'IMG_0097.jpeg'), PAD+PHONE_W+GAP)

# White band
WY = PINK_H
draw.rectangle([0,WY,W,WY+WHITE_H], fill=WHITE)
draw.rectangle([0,WY,W,WY+10], fill=BLACK)
draw.rectangle([0,WY+WHITE_H-10,W,WY+WHITE_H], fill=BLACK)
bsr_txt = 'BUY  ·  SELL  ·  REPAIR'
fnt_bsr, bb = fit_font(bsr_txt, W-80, 220)
draw.text(((W-(bb[2]-bb[0]))//2, WY+(WHITE_H-(bb[3]-bb[1]))//2), bsr_txt, font=fnt_bsr, fill=BLACK)

# Orange band
OY = WY+WHITE_H
draw.rectangle([0,OY,W,OY+ORANGE_H], fill=ORANGE)
num_txt = '(323)  348-6756'
fnt_num, bb = fit_font(num_txt, W-80, 240)
draw.text(((W-(bb[2]-bb[0]))//2, OY+(ORANGE_H-(bb[3]-bb[1]))//2), num_txt, font=fnt_num, fill=WHITE)

# Footer
FY = OY+ORANGE_H
draw.rectangle([0,FY,W,H], fill='#0D0D0D')
fnt_hrs = ImageFont.truetype(BOLD, 64)
fnt_adr = ImageFont.truetype(BOLD, 52)
hrs = 'MON–SAT  9AM–8PM   ·   SUN  10AM–6PM   ·   Walk-Ins Welcome'
adr = '3025 Artesia Blvd STE 101   ·   Torrance, CA 90504'
bb = draw.textbbox((0,0), hrs, font=fnt_hrs)
draw.text(((W-(bb[2]-bb[0]))//2, FY+28), hrs, font=fnt_hrs, fill=WHITE)
bb = draw.textbbox((0,0), adr, font=fnt_adr)
draw.text(((W-(bb[2]-bb[0]))//2, FY+112), adr, font=fnt_adr, fill=GREY)

out = os.path.join(os.path.dirname(__file__), 'poster.png')
canvas.save(out)
print('Saved:', out)
