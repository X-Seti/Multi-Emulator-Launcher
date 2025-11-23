#!/usr/bin/env python3
# generate_retro_exports.py
# Requires: Pillow, numpy
# pip install pillow numpy

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import os

# Helper: nearest palette color
def nearest_palette_color(color, palette):
    cr, cg, cb = color
    best = palette[0]
    best_dist = float('inf')
    for p in palette:
        pr, pg, pb = p
        d = (cr-pr)**2 + (cg-pg)**2 + (cb-pb)**2
        if d < best_dist:
            best_dist = d
            best = p
    return tuple(best)

# Input path (your uploaded file)
input_path = "/mnt/data/readdead-loading.png"
out_dir = "/mnt/data/out_emulator_files"
os.makedirs(out_dir, exist_ok=True)

# Load base image
img = Image.open(input_path).convert("RGB")

# 1) Create modified loading screen with corner text "DMA Design 1991"
loading = img.copy()
draw = ImageDraw.Draw(loading)
text = "DMA Design 1991"
margin = 6
font_size = max(10, img.size[0] // 64)
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
except:
    font = ImageFont.load_default()
tw, th = draw.textsize(text, font=font)
pos = (loading.size[0] - tw - margin, loading.size[1] - th - margin)
outline_color = (0,0,0)
fill_color = (255,255,255)
for ox, oy in [(-1,0),(1,0),(0,-1),(0,1)]:
    draw.text((pos[0]+ox, pos[1]+oy), text, font=font, fill=outline_color)
draw.text(pos, text, font=font, fill=fill_color)
loading_path = os.path.join(out_dir, "loading_dma1991.png")
loading.save(loading_path)
print("Saved:", loading_path)

# 2) Generate Rhodes & Valentine stylized screens
def stylize_scene(base_img, mode="rhodes"):
    img = base_img.copy().convert("RGB")
    w,h = img.size
    target_ratio = 4/3
    cur_ratio = w/h
    if cur_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w)//2
        img = img.crop((left, 0, left+new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h)//2
        img = img.crop((0, top, w, top+new_h))
    img = img.resize((320,240), Image.Resampling.LANCZOS)

    if mode == "rhodes":
        r,g,b = img.split()
        r = ImageEnhance.Brightness(r).enhance(1.05)
        g = ImageEnhance.Brightness(g).enhance(0.98)
        b = ImageEnhance.Brightness(b).enhance(0.95)
        img = Image.merge("RGB", (r,g,b))
        img = ImageOps.posterize(img, 4)
        bloom = img.filter(ImageFilter.GaussianBlur(radius=6))
        bloom = ImageEnhance.Brightness(bloom).enhance(1.15)
        img = Image.blend(img, bloom, 0.15)
    elif mode == "valentine":
        img = ImageOps.autocontrast(img)
        gray = ImageOps.grayscale(img)
        img = ImageOps.colorize(gray, black="#101018", white="#d0d6e0")
        arr = np.array(img).astype(np.int16)
        noise = (np.random.randn(*arr.shape) * 6).astype(np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr, "RGB")
        img = ImageOps.posterize(img, 5)
    else:
        img = ImageOps.autocontrast(img)
    return img

rhodes = stylize_scene(img, "rhodes")
valentine = stylize_scene(img, "valentine")
rhodes_path = os.path.join(out_dir, "rhodes_scene.png")
valentine_path = os.path.join(out_dir, "valentine_scene.png")
rhodes.save(rhodes_path); print("Saved:", rhodes_path)
valentine.save(valentine_path); print("Saved:", valentine_path)

# 3) 16-bit style conversions (PNG outputs)
def quantize_palette(img, palette_rgb):
    arr = np.array(img.convert("RGB"))
    h,w,_ = arr.shape
    out = np.zeros_like(arr)
    for y in range(h):
        for x in range(w):
            out[y,x] = nearest_palette_color(tuple(arr[y,x]), palette_rgb)
    return Image.fromarray(out)

# Amiga-like 32-color palette (example)
amiga_palette = [
    (0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),
    (128,128,128),(128,0,0),(0,128,0),(0,0,128),(128,128,0),(128,0,128),(0,128,128),(192,192,192),
    (64,64,64),(64,0,0),(0,64,0),(0,0,64),(64,64,0),(64,0,64),(0,64,64),(96,96,96),
    (160,160,160),(200,100,50),(100,200,50),(50,150,200),(240,200,160),(120,80,200),(200,120,160),(80,200,160)
]
amiga_img = img.resize((320,256), Image.Resampling.LANCZOS)
amiga_quant = quantize_palette(amiga_img, amiga_palette)
amiga_png_path = os.path.join(out_dir, "amiga_32color.png")
amiga_quant.save(amiga_png_path); print("Saved:", amiga_png_path)

# SNES-style (256 colors) via PIL adaptive quantize + 15-bit rounding
def build_snes_palette(image, n=256):
    q = image.convert('P', palette=Image.ADAPTIVE, colors=n)
    palette = q.getpalette()[:n*3]
    pal = []
    for i in range(n):
        r = palette[i*3]; g = palette[i*3+1]; b = palette[i*3+2]
        r5 = (r >> 3) << 3; g5 = (g >> 3) << 3; b5 = (b >> 3) << 3
        pal.append((r5,g5,b5))
    return pal

snes_pal = build_snes_palette(img, n=256)
snes_img = quantize_palette(img.resize((256,224), Image.Resampling.LANCZOS), snes_pal)
snes_png_path = os.path.join(out_dir, "snes_256color.png")
snes_img.save(snes_png_path); print("Saved:", snes_png_path)

# Genesis-style (3 bits/channel -> 64-color)
def build_genesis_palette(image, n=64):
    q = image.convert('P', palette=Image.ADAPTIVE, colors=n)
    palette = q.getpalette()[:n*3]
    pal = []
    for i in range(n):
        r = palette[i*3]; g = palette[i*3+1]; b = palette[i*3+2]
        r3 = (r >> 5) << 5; g3 = (g >> 5) << 5; b3 = (b >> 5) << 5
        pal.append((r3,g3,b3))
    return pal

gen_pal = build_genesis_palette(img, n=64)
gen_img = quantize_palette(img.resize((320,224), Image.Resampling.LANCZOS), gen_pal)
gen_png_path = os.path.join(out_dir, "genesis_64color.png")
gen_img.save(gen_png_path); print("Saved:", gen_png_path)

# 4) Simple ZX Spectrum-style conversions for the loading screen and both scenes (visual PNGs)
def simple_zx_convert(image):
    im = image.resize((256,192), Image.Resampling.LANCZOS).convert("RGB")
    arr = np.array(im)
    out = np.zeros_like(arr)
    for by in range(0,192,8):
        for bx in range(0,256,8):
            block = arr[by:by+8,bx:bx+8]
            avg = block.mean(axis=(0,1))
            ink = nearest_palette_color(tuple(avg), [(215,215,215),(0,0,0)])
            paper = (0,0,0) if ink != (0,0,0) else (215,215,215)
            for y in range(block.shape[0]):
                for x in range(block.shape[1]):
                    p = block[y,x]
                    d_ink = ((p-ink)**2).sum()
                    d_pap = ((p-paper)**2).sum()
                    out[by+y,bx+x] = ink if d_ink < d_pap else paper
    return Image.fromarray(out)

simple_zx_convert(loading).save(os.path.join(out_dir, "loading_dma1991_zx.png"))
simple_zx_convert(rhodes).save(os.path.join(out_dir, "rhodes_zx.png"))
simple_zx_convert(valentine).save(os.path.join(out_dir, "valentine_zx.png"))
print("Saved ZX-style PNGs.")

# 5) Placeholders for emulator-ready files (these are simplified placeholders)
# ZX .scr (6144 bitmap + 768 attribute bytes)
def create_zx_scr_from_binary(image, out_path):
    spec = image.resize((256,192)).convert("L")
    bitmap = (np.array(spec) < 128).astype(np.uint8)
    scr = bytearray(6144)
    for y in range(192):
        block = (y // 64)
        row_in_block = y % 64
        char_row = row_in_block % 8
        y_offset = block * 2048 + char_row * 256 + (row_in_block // 8) * 32
        for xbyte in range(32):
            b = 0
            for bit in range(8):
                b = (b << 1) | int(bitmap[y, xbyte*8 + bit])
            scr[y_offset + xbyte] = b
    attrs = bytearray([0x07] * 768)
    with open(out_path, "wb") as f:
        f.write(scr + attrs)

create_zx_scr_from_binary(loading, os.path.join(out_dir, "image.scr"))
print("Saved ZX .scr placeholder.")

# C64 Koala placeholder (actual packed multicolor conversion is more complex)
koa = bytearray()
koa += b"\x00\x60"
koa += bytearray(8000)
koa += bytearray(1000)
koa += bytearray(1000)
koa += b"\x00"
with open(os.path.join(out_dir, "image.koa"), "wb") as f:
    f.write(koa)
print("Saved C64 .koa placeholder.")

# CPC raw .scr placeholder (raw per-pixel bytes)
cpc_img = img.resize((160,200)).convert("RGB")
with open(os.path.join(out_dir, "image_cpc.scr"), "wb") as f:
    f.write(cpc_img.tobytes())
print("Saved CPC .scr placeholder (raw).")

# BBC placeholder file
with open(os.path.join(out_dir, "image.ssd"), "wb") as f:
    f.write(b"PLACEHOLDER_BBC_SSD\\n")
print("Saved BBC .ssd placeholder.")

# Done: list files
print("Files written to:", out_dir)
for fn in sorted(os.listdir(out_dir)):
    print(" -", fn)
