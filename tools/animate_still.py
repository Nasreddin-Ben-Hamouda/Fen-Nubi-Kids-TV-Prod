"""Animate a still scene for free: slow push-in, gentle bob/sway, falling petals.

Usage: python tools/animate_still.py scene.png frames_dir   (writes 192 PNG frames = 8 s at 24 fps)
Then: ffmpeg -framerate 24 -i frames_dir/%04d.png -i audio_source.mp4 -map 0:v -map 1:a -t 8 -c:v libx264 -pix_fmt yuv420p out.mp4
"""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
SW, SH = src.size
W, H, FPS, N = 720, 1280, 24, 192
random.seed(7)
petals = [dict(x=random.uniform(0, W), y=random.uniform(-H, H), s=random.uniform(10, 17),
               vy=random.uniform(60, 110), sway=random.uniform(20, 45), ph=random.uniform(0, 6.28),
               rot=random.uniform(0, 360), c=random.choice([(255,190,210),(255,205,220),(250,175,200)])) for _ in range(16)]
clamp = lambda v, lo, hi: max(lo, min(hi, v))
for f in range(N):
    t = f / FPS
    z = 1.12 + 0.08 * (t / 8) + 0.006 * math.sin(2 * math.pi * t / 1.6)
    ch = SH / z; cw = ch * 9 / 16
    cx = clamp(SW * 0.52 + 6 * math.sin(2 * math.pi * t / 4), cw / 2, SW - cw / 2)
    cy = clamp(SH * 0.62 - 20 * (t / 8), ch / 2, SH - ch / 2)
    fr = src.resize((W, H), Image.LANCZOS, box=(cx - cw/2, cy - ch/2, cx + cw/2, cy + ch/2)).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for p in petals:
        y = (p["y"] + p["vy"] * t) % (H + 100) - 50
        x = p["x"] + p["sway"] * math.sin(p["ph"] + t * 1.7)
        a = math.radians(p["rot"] + 40 * t); s = p["s"]
        pts = [(x + s * math.cos(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.55),
                y + s * math.sin(a + k * math.pi / 2) * (1 if k % 2 == 0 else 0.55)) for k in range(4)]
        d.polygon(pts, fill=p["c"] + (215,))
    fr.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.8)))
    fr.convert("RGB").save(f"{out}/{f:04d}.png")
