#!/usr/bin/env python3
# X-Seti - November23 2025 - Multi-Emulator Launcher - Retro System Converter
#this belongs in apps/components/retro_convert.py - Version: 1
"""
Retro System Converter - Handles conversion to 8-bit and 16-bit retro system formats.
Supports ZX Spectrum, C64, CPC, BBC, Amiga, SNES, Genesis/Mega Drive, and more.
Includes texture utilities for resizing, bit depth adjustment, and upscaling.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import os
from pathlib import Path
from typing import Optional, Tuple, List

##Methods list -
# apply_ordered_dither
# build_amiga_palette
# build_genesis_palette
# build_snes_palette
# convert_to_amiga
# convert_to_bbc
# convert_to_c64_koala
# convert_to_cpc
# convert_to_genesis
# convert_to_snes
# convert_to_zx_spectrum
# create_loading_screen
# nearest_palette_color
# quantize_palette
# resize_texture
# stylize_scene
# texture_adjust_bit_depth
# texture_upscale
# zx_spectrum_simple

# ============================================================================
# CORE PALETTE FUNCTIONS
# ============================================================================

def nearest_palette_color(color, palette): #vers 1
    """Find nearest color in palette using Euclidean distance"""
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

def apply_ordered_dither(img_arr, palette, matrix=None): #vers 1
    """Apply ordered dithering using Bayer matrix"""
    if matrix is None:
        # 4x4 Bayer matrix
        matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]) / 16.0
    
    h, w = img_arr.shape[:2]
    mh, mw = matrix.shape
    out = np.zeros_like(img_arr)
    
    for y in range(h):
        for x in range(w):
            threshold = matrix[y % mh, x % mw]
            pixel = img_arr[y, x] + (threshold - 0.5) * 32
            pixel = np.clip(pixel, 0, 255)
            out[y, x] = nearest_palette_color(tuple(pixel.astype(int)), palette)
    
    return out

def quantize_palette(img, palette_rgb): #vers 1
    """Quantize image to specific RGB palette"""
    arr = np.array(img.convert("RGB"))
    h, w, _ = arr.shape
    out = np.zeros_like(arr)
    for y in range(h):
        for x in range(w):
            out[y, x] = nearest_palette_color(tuple(arr[y, x]), palette_rgb)
    return Image.fromarray(out)

# ============================================================================
# 16-BIT PALETTE BUILDERS
# ============================================================================

def build_amiga_palette(): #vers 1
    """Build standard 32-color Amiga palette"""
    return [
        (0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255),
        (128,128,128),(128,0,0),(0,128,0),(0,0,128),(128,128,0),(128,0,128),(0,128,128),(192,192,192),
        (64,64,64),(64,0,0),(0,64,0),(0,0,64),(64,64,0),(64,0,64),(0,64,64),(96,96,96),
        (160,160,160),(200,100,50),(100,200,50),(50,150,200),(240,200,160),(120,80,200),(200,120,160),(80,200,160)
    ]

def build_snes_palette(image, n=256): #vers 1
    """Build SNES 15-bit palette (5 bits per channel)"""
    q = image.convert('P', palette=Image.ADAPTIVE, colors=n)
    palette = q.getpalette()[:n*3]
    pal = []
    for i in range(n):
        r = palette[i*3]
        g = palette[i*3+1]
        b = palette[i*3+2]
        # Round to 5 bits per channel
        r5 = (r >> 3) << 3
        g5 = (g >> 3) << 3
        b5 = (b >> 3) << 3
        pal.append((r5, g5, b5))
    return pal

def build_genesis_palette(image, n=64): #vers 1
    """Build Genesis/Mega Drive 9-bit palette (3 bits per channel)"""
    q = image.convert('P', palette=Image.ADAPTIVE, colors=n)
    palette = q.getpalette()[:n*3]
    pal = []
    for i in range(n):
        r = palette[i*3]
        g = palette[i*3+1]
        b = palette[i*3+2]
        # Round to 3 bits per channel
        r3 = (r >> 5) << 5
        g3 = (g >> 5) << 5
        b3 = (b >> 5) << 5
        pal.append((r3, g3, b3))
    return pal

# ============================================================================
# TEXTURE UTILITIES
# ============================================================================

def resize_texture(image: Image.Image, width: int, height: int, 
                   maintain_aspect: bool = True) -> Image.Image: #vers 1
    """Resize texture with optional aspect ratio preservation"""
    if maintain_aspect:
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        return image
    else:
        return image.resize((width, height), Image.Resampling.LANCZOS)

def texture_adjust_bit_depth(image: Image.Image, bits_per_channel: int) -> Image.Image: #vers 1
    """Adjust image bit depth (e.g., 8-bit to 5-bit per channel)"""
    if bits_per_channel >= 8:
        return image
    
    arr = np.array(image.convert("RGB"))
    shift = 8 - bits_per_channel
    mask = (0xFF >> shift) << shift
    arr = (arr >> shift) << shift
    return Image.fromarray(arr.astype(np.uint8))

def texture_upscale(image: Image.Image, scale_factor: int = 2, 
                    method: str = 'lanczos') -> Image.Image: #vers 1
    """Upscale texture using various methods"""
    w, h = image.size
    new_size = (w * scale_factor, h * scale_factor)
    
    methods = {
        'nearest': Image.Resampling.NEAREST,
        'bilinear': Image.Resampling.BILINEAR,
        'bicubic': Image.Resampling.BICUBIC,
        'lanczos': Image.Resampling.LANCZOS
    }
    
    resample = methods.get(method.lower(), Image.Resampling.LANCZOS)
    return image.resize(new_size, resample)

# ============================================================================
# STYLIZATION FUNCTIONS
# ============================================================================

def create_loading_screen(image: Image.Image, text: str = "DMA Design 1991", 
                         font_path: Optional[str] = None) -> Image.Image: #vers 1
    """Create loading screen with corner text overlay"""
    loading = image.copy()
    draw = ImageDraw.Draw(loading)
    margin = 6
    font_size = max(10, image.size[0] // 64)
    
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pos = (loading.size[0] - tw - margin, loading.size[1] - th - margin)
    
    # Draw outline
    outline_color = (0, 0, 0)
    fill_color = (255, 255, 255)
    for ox, oy in [(-1,0), (1,0), (0,-1), (0,1)]:
        draw.text((pos[0]+ox, pos[1]+oy), text, font=font, fill=outline_color)
    draw.text(pos, text, font=font, fill=fill_color)
    
    return loading

def stylize_scene(base_img: Image.Image, mode: str = "rhodes") -> Image.Image: #vers 1
    """Stylize scene with various effects (rhodes/valentine style)"""
    img = base_img.copy().convert("RGB")
    w, h = img.size
    
    # Crop to 4:3 aspect ratio
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
    
    img = img.resize((320, 240), Image.Resampling.LANCZOS)
    
    if mode == "rhodes":
        r, g, b = img.split()
        r = ImageEnhance.Brightness(r).enhance(1.05)
        g = ImageEnhance.Brightness(g).enhance(0.98)
        b = ImageEnhance.Brightness(b).enhance(0.95)
        img = Image.merge("RGB", (r, g, b))
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

# ============================================================================
# 8-BIT SYSTEM CONVERTERS
# ============================================================================

def convert_to_zx_spectrum(image: Image.Image, output_path: str, 
                          mode: str = "scr") -> str: #vers 1
    """Convert image to ZX Spectrum format (.scr file)"""
    spec = image.resize((256, 192)).convert("L")
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
    
    # Attributes (white on black)
    attrs = bytearray([0x07] * 768)
    
    with open(output_path, "wb") as f:
        f.write(scr + attrs)
    
    return output_path

def zx_spectrum_simple(image: Image.Image) -> Image.Image: #vers 1
    """Simple ZX Spectrum visual conversion (PNG output)"""
    im = image.resize((256, 192), Image.Resampling.LANCZOS).convert("RGB")
    arr = np.array(im)
    out = np.zeros_like(arr)
    
    for by in range(0, 192, 8):
        for bx in range(0, 256, 8):
            block = arr[by:by+8, bx:bx+8]
            avg = block.mean(axis=(0, 1))
            ink = nearest_palette_color(tuple(avg), [(215,215,215), (0,0,0)])
            paper = (0,0,0) if ink != (0,0,0) else (215,215,215)
            
            for y in range(block.shape[0]):
                for x in range(block.shape[1]):
                    p = block[y, x]
                    d_ink = ((p - ink)**2).sum()
                    d_pap = ((p - paper)**2).sum()
                    out[by+y, bx+x] = ink if d_ink < d_pap else paper
    
    return Image.fromarray(out)

def convert_to_c64_koala(image: Image.Image, output_path: str) -> str: #vers 2
    """Convert image to C64 Koala format (.koa file)"""
    # Resize to C64 multicolor resolution
    c64_img = image.resize((160, 200), Image.Resampling.LANCZOS)
    
    # C64 palette (simplified 16 colors)
    c64_palette = [
        (0,0,0), (255,255,255), (136,0,0), (170,255,238),
        (204,68,204), (0,204,85), (0,0,170), (238,238,119),
        (221,136,85), (102,68,0), (255,119,119), (51,51,51),
        (119,119,119), (170,255,102), (0,136,255), (187,187,187)
    ]
    
    # Quantize to C64 palette
    arr = np.array(c64_img.convert("RGB"))
    h, w = arr.shape[:2]
    
    # Build bitmap data
    bitmap = bytearray(8000)
    screen = bytearray(1000)
    colram = bytearray(1000)
    bg_color_index = 0
    
    # Simple cell-based color selection
    cell_index = 0
    for cy in range(0, h, 8):
        for cx in range(0, w, 4):
            if cy + 8 <= h and cx + 4 <= w:
                block = arr[cy:cy+8, cx:cx+4]
                avg = block.mean(axis=(0, 1))
                chosen = nearest_palette_color(tuple(avg.astype(int)), c64_palette)
                color_idx = c64_palette.index(chosen)
                screen[cell_index] = color_idx & 0xFF
                colram[cell_index] = color_idx & 0x0F
                cell_index += 1
    
    # Build final file: load address $6000 (0x6000) little-endian
    data = bytearray()
    data += b'\x00\x60'  # load address $6000 little-endian
    data += bitmap.ljust(8000, b'\x00')
    data += screen.ljust(1000, b'\x00')
    data += colram.ljust(1000, b'\x00')
    data += bytes([bg_color_index & 0xFF])
    
    with open(output_path, 'wb') as f:
        f.write(data)
    
    return output_path

def convert_to_cpc(image: Image.Image, output_path: str) -> str: #vers 1
    """Convert image to Amstrad CPC format (raw .scr)"""
    cpc_img = image.resize((160, 200), Image.Resampling.LANCZOS).convert("RGB")
    
    with open(output_path, "wb") as f:
        f.write(cpc_img.tobytes())
    
    return output_path

def convert_to_bbc(image: Image.Image, output_path: str) -> str: #vers 1
    """Convert image to BBC Micro format (.ssd placeholder)"""
    # Placeholder for BBC disk format
    with open(output_path, "wb") as f:
        f.write(b"BBC_MICRO_IMAGE_PLACEHOLDER\n")
        f.write(image.resize((320, 256)).tobytes())
    
    return output_path

# ============================================================================
# 16-BIT SYSTEM CONVERTERS
# ============================================================================

def convert_to_amiga(image: Image.Image, output_path: str) -> str: #vers 1
    """Convert image to Amiga 32-color format (PNG output)"""
    amiga_palette = build_amiga_palette()
    amiga_img = image.resize((320, 256), Image.Resampling.LANCZOS)
    amiga_quant = quantize_palette(amiga_img, amiga_palette)
    amiga_quant.save(output_path)
    return output_path

def convert_to_snes(image: Image.Image, output_path: str) -> str: #vers 1
    """Convert image to SNES 256-color format with 15-bit palette (PNG output)"""
    snes_pal = build_snes_palette(image, n=256)
    snes_img = quantize_palette(image.resize((256, 224), Image.Resampling.LANCZOS), snes_pal)
    snes_img.save(output_path)
    return output_path

def convert_to_genesis(image: Image.Image, output_path: str) -> str: #vers 1
    """Convert image to Genesis/Mega Drive 64-color format (PNG output)"""
    gen_pal = build_genesis_palette(image, n=64)
    gen_img = quantize_palette(image.resize((320, 224), Image.Resampling.LANCZOS), gen_pal)
    gen_img.save(output_path)
    return output_path

# ============================================================================
# BATCH CONVERSION HELPERS
# ============================================================================

def batch_convert_retro(input_path: str, output_dir: str, 
                       systems: Optional[List[str]] = None) -> dict: #vers 1
    """
    Batch convert image to multiple retro systems
    
    Args:
        input_path: Path to input image
        output_dir: Directory for output files
        systems: List of system names (None = all systems)
    
    Returns:
        Dictionary mapping system names to output paths
    """
    os.makedirs(output_dir, exist_ok=True)
    img = Image.open(input_path).convert("RGB")
    base_name = Path(input_path).stem
    
    results = {}
    
    all_systems = {
        'zx': lambda: convert_to_zx_spectrum(img, os.path.join(output_dir, f"{base_name}_zx.scr")),
        'c64': lambda: convert_to_c64_koala(img, os.path.join(output_dir, f"{base_name}_c64.koa")),
        'cpc': lambda: convert_to_cpc(img, os.path.join(output_dir, f"{base_name}_cpc.scr")),
        'bbc': lambda: convert_to_bbc(img, os.path.join(output_dir, f"{base_name}_bbc.ssd")),
        'amiga': lambda: convert_to_amiga(img, os.path.join(output_dir, f"{base_name}_amiga.png")),
        'snes': lambda: convert_to_snes(img, os.path.join(output_dir, f"{base_name}_snes.png")),
        'genesis': lambda: convert_to_genesis(img, os.path.join(output_dir, f"{base_name}_genesis.png")),
    }
    
    target_systems = systems if systems else all_systems.keys()
    
    for system in target_systems:
        if system in all_systems:
            try:
                results[system] = all_systems[system]()
            except Exception as e:
                results[system] = f"Error: {str(e)}"
    
    return results
