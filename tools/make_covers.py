"""Render the Fen & Nubi cover photos (YouTube banner and Facebook cover).

Run from the repo root:  python tools/make_covers.py
Writes social/cover_youtube_2560x1440.png and social/cover_facebook_1640x624.png.
Requires Pillow and the Inter font (/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf).
"""
import sys, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
FONT="/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
def cutout(path, box=None, thresh=40):
    im=Image.open(path).convert("RGB")
    if box: im=im.crop(box)
    w,h=im.size; key=(255,0,255)
    for pt in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,h-1)]:
        if im.getpixel(pt)[0]>235: ImageDraw.floodfill(im,pt,key,thresh=thresh)
    mask=Image.eval(ImageChops.difference(im,Image.new("RGB",im.size,key)).convert("L"),lambda v:255 if v>8 else 0)
    mask=mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    orig=Image.open(path).convert("RGBA")
    if box: orig=orig.crop(box)
    orig.putalpha(mask); return orig.crop(mask.getbbox())
def scene(W,H):
    bg=Image.new("RGB",(W,H)); d=ImageDraw.Draw(bg)
    for y in range(H):
        t=y/H; c=tuple(int(a+(b-a)*t) for a,b in zip((150,215,240),(225,243,250)))
        d.line([(0,y),(W,y)],fill=c)
    cl=Image.new("RGBA",(W,H),(255,255,255,0)); dc=ImageDraw.Draw(cl); random.seed(4)
    for _ in range(9):
        x=random.randint(0,W); y=random.randint(int(H*.05),int(H*.35)); s=random.randint(int(H*.06),int(H*.11))
        for dx,dy,r in [(0,0,1),(s*.9,s*.2,.8),(-s*.9,s*.25,.75),(s*.4,-s*.35,.85)]:
            dc.ellipse([x+dx-s*r*1.3,y+dy-s*r,x+dx+s*r*1.3,y+dy+s*r],fill=(255,255,255,235))
    bg.paste(cl.filter(ImageFilter.GaussianBlur(H*.004)),(0,0),cl.filter(ImageFilter.GaussianBlur(H*.004)))
    hl=Image.new("RGBA",(W,H),(0,0,0,0)); dh=ImageDraw.Draw(hl)
    dh.ellipse([-W*.2,H*.62,W*.65,H*1.6],fill=(150,205,120,255))
    dh.ellipse([W*.35,H*.66,W*1.25,H*1.6],fill=(135,195,110,255))
    dh.ellipse([-W*.1,H*.76,W*1.1,H*1.8],fill=(165,215,130,255))
    for _ in range(int(W*H/30000)):
        x=random.randint(0,W); y=random.randint(int(H*.72),H); r=random.randint(int(H*.004),int(H*.008))
        dh.ellipse([x-r,y-r,x+r,y+r],fill=random.choice([(255,190,210,255),(255,230,120,255),(255,255,255,255),(210,190,250,255)]))
    bg.paste(hl,(0,0),hl); return bg.convert("RGBA")
def put(bg,ch,h,cx,bottom):
    ch=ch.resize((int(ch.width*h/ch.height),h),Image.LANCZOS)
    sh=Image.new("RGBA",bg.size,(0,0,0,0)); ImageDraw.Draw(sh).ellipse([cx-ch.width*.38,bottom-h*.035,cx+ch.width*.38,bottom+h*.035],fill=(40,70,40,70))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(h*.02)))
    bg.alpha_composite(ch,(int(cx-ch.width/2),int(bottom-ch.height)))
def text(bg,s,size,cx,cy,fill,stroke):
    d=ImageDraw.Draw(bg); f=ImageFont.truetype(FONT,size)
    d.text((cx,cy),s,font=f,fill=fill,anchor="mm",stroke_width=max(2,size//14),stroke_fill=stroke)
fen=cutout("shared/characters/char_001.png",(45,100,615,950)); nubi=cutout("shared/characters/char_002.png",(0,0,1024,872),thresh=75)
# Clear the grey floor shadow around Nubi's feet: low-saturation light pixels in the bottom band
hsv=nubi.convert("RGB").convert("HSV"); al=nubi.getchannel("A"); px=al.load(); hp=hsv.load()
for y in range(int(nubi.height*0.86), nubi.height):
    for x in range(nubi.width):
        h_,s_,v_=hp[x,y]
        if s_<70 and v_>120: px[x,y]=0
nubi.putalpha(al.filter(ImageFilter.GaussianBlur(0.8)))
TAG="Lustige Geschichten & Lieder für Kinder"
# YouTube banner 2560x1440, safe area 1546x423 centred (y 508-931)
W,H=2560,1440; bg=scene(W,H)
put(bg,fen,410,650,926); put(bg,nubi,300,1900,926)
text(bg,"Fen & Nubi",150,W/2,660,(255,255,255),(40,60,90)); text(bg,TAG,46,W/2,800,(255,224,102),(40,60,90))
bg.convert("RGB").save("social/cover_youtube_2560x1440.png")
# Facebook cover 1640x624, keep content in the centre ~1100 px
W,H=1640,624; bg=scene(W,H)
put(bg,fen,400,390,600); put(bg,nubi,300,1250,600)
text(bg,"Fen & Nubi",110,W/2,250,(255,255,255),(40,60,90)); text(bg,TAG,30,W/2,355,(255,224,102),(40,60,90))
bg.convert("RGB").save("social/cover_facebook_1640x624.png")
