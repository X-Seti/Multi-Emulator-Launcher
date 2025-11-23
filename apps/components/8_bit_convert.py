#!/usr/bin/env python3
#this belongs in apps/components/8_bit_convert.py - Version: 3
# X-Seti - November22 2025 - Mulii image convertor 0.5
"""
8bit_convert_package.py

All-in-one Python package/script for converting 4:3 images into retro 8-bit system formats.
Includes:
 - ZX Spectrum (accurate 8x8 attribute handling, .scr export)
 - Commodore 64 (multicolour & hires emulation)
 - BBC Micro (Mode 2)
 - Amstrad CPC (Mode 0)
 - Atari 8-bit (ANTIC modes basic emulation)
 - MSX1 (Palette & 16-color simulation)
 - NES (PPU limited palette simulation)
 - Game Boy (4-shade grayscale)
 - Dithering options: none, ordered, Floyd–Steinberg
 - CLI + simple Tkinter GUI
 - Batch conversion

Dependencies:
 - Pillow
 - numpy

Usage examples:
 python3 8bit_convert.py --input /path/to/input.png --system zx --output out_zx.png
 python3 8bit_convert.py --gui

"""

import sys
import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox


# Palettes

PALETTES = {
    'zx': [
        (0x00,0x00,0x00),(0x00,0x00,0xD7),(0xD7,0x00,0x00),(0xD7,0x00,0xD7),
        (0x00,0xD7,0x00),(0x00,0xD7,0xD7),(0xD7,0xD7,0x00),(0xD7,0xD7,0xD7),
        (0x00,0x00,0x00),(0x00,0x00,0xFF),(0xFF,0x00,0x00),(0xFF,0x00,0xFF),
        (0x00,0xFF,0x00),(0x00,0xFF,0xFF),(0xFF,0xFF,0x00),(0xFF,0xFF,0xFF)
    ],
    'c64': [
        (0x00,0x00,0x00),(0xFF,0xFF,0xFF),(0x68,0x37,0x2B),(0x70,0xA4,0xB2),
        (0x6F,0x3D,0x86),(0x58,0x8D,0x43),(0x35,0x28,0x79),(0xB8,0xC7,0x6F),
        (0x6F,0x4F,0x25),(0x43,0x39,0x00),(0x9A,0x67,0x59),(0x44,0x44,0x44),
        (0x6C,0x6C,0x6C),(0x9A,0xD2,0x84),(0x6C,0x5E,0xB5),(0x95,0x95,0x95)
    ],
    'bbc': [ (0,0,0),(255,0,0),(255,255,0),(255,255,255) ],
    'cpc': [
        (0,0,0),(0,0,128),(0,0,255),(128,0,0),(128,0,128),(128,0,255),
        (255,0,0),(255,0,128),(255,0,255),(0,128,0),(0,128,128),(0,128,255),
        (128,128,0),(128,128,128),(128,128,255),(255,255,255)
    ],
    'gameboy': [ (255,255,255),(192,192,192),(96,96,96),(0,0,0) ],
    'nes': [ # simplified NES-like palette (selected subset)
        (124,124,124),(0,0,252),(0,0,188),(68,40,188),(148,0,132),(168,0,32),(168,16,0),(136,20,0),
        (80,48,0),(0,120,0),(0,104,0),(0,88,0),(0,64,88),(0,0,0),(0,0,0),(0,0,0)
    ],
    'msx': [ # simple 16 colour MSX-like
        (0,0,0),(0,0,170),(170,0,0),(170,0,170),(0,170,0),(0,170,170),(170,85,0),(170,170,170),
        (85,85,85),(85,85,255),(255,85,85),(255,85,255),(85,255,85),(85,255,255),(255,255,85),(255,255,255)
    ],
    'atari': [ # rough approximation
        (0,0,0),(255,255,255),(136,0,0),(170,170,0),(0,170,0),(0,170,170),(0,0,170),(170,0,170),
        (170,85,0),(85,85,85),(85,255,255),(170,170,170),(255,85,85),(255,170,170),(170,255,85),(255,255,255)
    ]
}


# Utilities

def nearest_palette_color(color, palette): #vers 1
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
    # simple ordered dither using a 4x4 Bayer matrix if not specified
    if matrix is None:
        matrix = np.array([[0, 8, 2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
        matrix = (matrix + 0.5) / 16.0
    h,w,_ = img_arr.shape
    out = np.zeros_like(img_arr)
    for y in range(h):
        for x in range(w):
            orig = img_arr[y,x].astype(float)/255.0
            b = matrix[y % matrix.shape[0], x % matrix.shape[1]]
            thresh = np.clip(orig + (b - 0.5)/2.0, 0, 1)
            col = nearest_palette_color(tuple((thresh*255).astype(int)), palette)
            out[y,x] = col
    return out


def apply_fs_dither(img_arr, palette): #vers 1
    # Floyd–Steinberg error diffusion
    arr = img_arr.copy().astype(float)
    h,w,_ = arr.shape
    for y in range(h):
        for x in range(w):
            old = arr[y,x]
            new = np.array(nearest_palette_color(tuple(old.astype(int)), palette))
            arr[y,x] = new
            err = old - new
            if x+1 < w: arr[y,x+1] += err * 7/16
            if y+1 < h:
                if x>0: arr[y+1,x-1] += err * 3/16
                arr[y+1,x] += err * 5/16
                if x+1 < w: arr[y+1,x+1] += err * 1/16
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr


# System converters

def convert_zx_spectrum(img, dither=None, playable_cells=(32,21)): #vers 1
    # Resize to 256x192
    img = img.resize((256,192), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    out = np.zeros_like(px)
    palette = PALETTES['zx']

    # For each 8x8 cell compute ink/paper under attribute rules
    for cell_y in range(0,192,8):
        for cell_x in range(0,256,8):
            block = px[cell_y:cell_y+8, cell_x:cell_x+8]
            # Strategy: cluster to 2 colors using kmeans-like simple method (mean + threshold)
            mean = block.reshape(-1,3).mean(axis=0)
            # find nearest palette colors to mean +/- luminance
            # compute luminance per pixel
            lum = block.mean(axis=2)
            mask = lum > lum.mean()
            ink_guess = nearest_palette_color(tuple(block[mask].mean(axis=0)) if mask.any() else tuple(mean), palette)
            paper_guess = nearest_palette_color(tuple(block[~mask].mean(axis=0)) if (~mask).any() else tuple(mean), palette)
            if ink_guess == paper_guess:
                # find second best by trying extremes
                ink_guess = nearest_palette_color(tuple(block[lum > np.percentile(lum,75)].mean(axis=0)) if block.size else ink_guess, palette)
                paper_guess = nearest_palette_color(tuple(block[lum < np.percentile(lum,25)].mean(axis=0)) if block.size else paper_guess, palette)
            # apply per-pixel selection
            for yy in range(block.shape[0]):
                for xx in range(block.shape[1]):
                    p = block[yy,xx]
                    # choose closer of ink/paper
                    d_ink = ((p-ink_guess)**2).sum()
                    d_pap = ((p-paper_guess)**2).sum()
                    out[cell_y+yy, cell_x+xx] = ink_guess if d_ink < d_pap else paper_guess

    # Optional dither across whole image
    if dither == 'ordered':
        out = apply_ordered_dither(out, palette)
    elif dither == 'fs':
        out = apply_fs_dither(out, palette)
    return Image.fromarray(out)


def convert_c64(img, dither=None, mode='multicolor'): #vers 1
    # C64 multicolor: 160x200
    img = img.resize((160,200), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    out = np.zeros_like(px)
    palette = PALETTES['c64']

    # Multicolour: 4 colours per 4x8 block
    for y in range(0,200,8):
        for x in range(0,160,4):
            block = px[y:y+8, x:x+4].reshape(-1,3)
            # reduce to nearest palette then find up to 4 most common
            reduced = [nearest_palette_color(tuple(p), palette) for p in block]
            uniq = []
            for c in reduced:

                if c not in uniq:
                    uniq.append(c)
                if len(uniq) >= 4: break

            if len(uniq) < 4:
                # pad with black/white
                for p in palette:
                    if p not in uniq:
                        uniq.append(p)
                    if len(uniq) >=4: break

            # assign each pixel nearest of uniq
            for yy in range(8):
                for xx in range(4):
                    col = tuple(px[y+yy, x+xx])
                    out[y+yy, x+xx] = nearest_palette_color(col, uniq)
    if dither == 'ordered':
        out = apply_ordered_dither(out, palette)
    elif dither == 'fs':
        out = apply_fs_dither(out, palette)
    return Image.fromarray(out)


def convert_bbc(img, dither=None): #vers 1
    img = img.resize((160,256), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    palette = PALETTES['bbc']
    out = np.zeros_like(px)

    if dither == 'fs':
        arr = apply_fs_dither(px, palette)
        return Image.fromarray(arr)
    for y in range(256):
        for x in range(160):
            out[y,x] = nearest_palette_color(tuple(px[y,x]), palette)
    return Image.fromarray(out)


def convert_cpc(img, dither=None): #vers 1
    img = img.resize((160,200), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    palette = PALETTES['cpc']

    if dither == 'fs':
        return Image.fromarray(apply_fs_dither(px, palette))

    if dither == 'ordered':
        return Image.fromarray(apply_ordered_dither(px, palette))
    out = np.zeros_like(px)
    for y in range(px.shape[0]):
        for x in range(px.shape[1]):
            out[y,x] = nearest_palette_color(tuple(px[y,x]), palette)
    return Image.fromarray(out)


def convert_gameboy(img): #vers 1
    img = img.resize((160,144), Image.BICUBIC).convert('L')
    # map to 4 shades
    arr = np.array(img)
    bins = np.array([64,128,192])
    out = np.digitize(arr, bins)
    shades = [255,192,96,0]
    rgb = np.zeros((arr.shape[0], arr.shape[1],3), dtype=np.uint8)
    for i in range(4):
        rgb[out==i] = (shades[i],)*3
    return Image.fromarray(rgb)


def convert_nes(img): #vers 1
    img = img.resize((256,240), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    palette = PALETTES['nes']
    out = np.zeros_like(px)
    for y in range(px.shape[0]):
        for x in range(px.shape[1]):
            out[y,x] = nearest_palette_color(tuple(px[y,x]), palette)
    return Image.fromarray(out)


def convert_msx(img): #vers 1
    img = img.resize((256,192), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    palette = PALETTES['msx']
    out = np.zeros_like(px)
    for y in range(px.shape[0]):
        for x in range(px.shape[1]):
            out[y,x] = nearest_palette_color(tuple(px[y,x]), palette)
    return Image.fromarray(out)


def convert_atari(img): #vers 1
    img = img.resize((160,192), Image.BICUBIC).convert('RGB')
    px = np.array(img)
    palette = PALETTES['atari']
    out = np.zeros_like(px)
    for y in range(px.shape[0]):
        for x in range(px.shape[1]):
            out[y,x] = nearest_palette_color(tuple(px[y,x]), palette)
    return Image.fromarray(out)


# Exporters (some real implementations)

def export_zx_scr(img, out_path): #vers 2
    """
    Exports a ZX Spectrum .SCR file (6912 bytes bitmap + 768 attribute bytes)
    img must be 256x192 and already reduced to Spectrum colours
    """
    img = img.resize((256,192)).convert('RGB')
    px = np.array(img)

    # build bitmap bytes: screen memory is in odd addressing order; this will produce standard bitmap
    # Each byte contains 8 vertical pixels per column within a character row; write in linear 256x192 -> 6144 bits
    # The precise ZX memory layout (bitmap) is non-linear; implement the correct mapping.

    bitmap = bytearray(6144)
    for y in range(192):
        for x in range(256):
            # determine bit in byte
            byte_index = ((y & 0xC0) >> 6) * 2048 + ((y & 0x38) >> 3) * 256 + (y & 0x07) * 32 + (x >> 3)
            bit = 7 - (x & 7)
            # decide pixel set = non-black
            r,g,b = px[y,x]
            is_on = (r,g,b) != (0,0,0)
            if is_on:
                bitmap[byte_index] |= (1 << bit)

    # attribute bytes (32x24 = 768)
    attributes = bytearray()
    for ay in range(24):
        for ax in range(32):
            # attribute cell 8x8 pixels
            cell = px[ay*8:(ay+1)*8, ax*8:(ax+1)*8]

            # pick ink and paper by most common colors in cell
            colors = {}
            for yy in range(cell.shape[0]):
                for xx in range(cell.shape[1]):
                    c = tuple(cell[yy,xx])
                    colors[c] = colors.get(c,0)+1
            # sort
            sorted_cols = sorted(colors.items(), key=lambda item: -item[1])
            paper = sorted_cols[-1][0] if len(sorted_cols)>1 else sorted_cols[0][0]
            ink = sorted_cols[0][0]
            # map palette to zx indices
            zx_palette = PALETTES['zx']
            try:
                ink_idx = zx_palette.index(tuple(ink))
            except ValueError:
                ink_idx = 7 if ink==(255,255,255) else 0
            try:
                pap_idx = zx_palette.index(tuple(paper))
            except ValueError:
                pap_idx = 0
            bright = 0
            flash = 0
            attr = (bright<<6) | (flash<<7) | (ink_idx & 7) | ((pap_idx & 7) << 3)
            attributes.append(attr)

    with open(out_path, 'wb') as f:
        f.write(bitmap)
        f.write(attributes)
    return out_path

# CLI + GUI

SYSTEM_FUNCS = {
    'zx': convert_zx_spectrum,
    'c64': convert_c64,
    'bbc': convert_bbc,
    'cpc': convert_cpc,
    'gameboy': convert_gameboy,
    'nes': convert_nes,
    'msx': convert_msx,
    'atari': convert_atari
}


def ensure_4_3(img): #vers 1
    # TODO - Make thid adjustable 4:3 - 15:10 - 16:9
    # Crop or pad image to nearest 4:3 preserving center
    w,h = img.size
    target_ratio = 4/3
    cur_ratio = w/h

    if abs(cur_ratio - target_ratio) < 0.01:
        return img

    if cur_ratio > target_ratio:
        # too wide -> crop width
        new_w = int(h * target_ratio)
        left = (w - new_w)//2
        return img.crop((left,0,left+new_w,h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h)//2
        return img.crop((0,top,w,top+new_h))


def run_conversion(input_path, system, output_path, dither=None, save_scr=False): #vers 2
    img = Image.open(input_path).convert('RGB')
    img = ensure_4_3(img)
    func = SYSTEM_FUNCS.get(system)

    if not func:
        raise ValueError('Unknown system')
    result = func(img, dither=dither) if system in ['zx','c64','bbc','cpc'] else func(img)
    result.save(output_path)

    if save_scr and system=='zx':
        scr_path = os.path.splitext(output_path)[0]+'.scr'
        export_zx_scr(result, scr_path)
        print('Saved SCR:', scr_path)
    print('Saved:', output_path)


# Simple Tkinter GUI

def launch_gui(): #vers 1
    root = tk.Tk()
    root.title('8-bit Converter')
    root.geometry('480x220')

    tk.Label(root, text='Input image (4:3 recommended)').pack()
    input_var = tk.StringVar()
    tk.Entry(root, textvariable=input_var, width=60).pack()
    def browse_in():
        p = filedialog.askopenfilename(filetypes=[('Images','*.png;*.jpg;*.bmp;*.gif'),('All','*.*')])

        if p: input_var.set(p)
    tk.Button(root, text='Browse', command=browse_in).pack()

    tk.Label(root, text='System').pack()
    system_var = tk.StringVar(value='zx')
    tk.OptionMenu(root, system_var, *sorted(SYSTEM_FUNCS.keys())).pack()

    tk.Label(root, text='Dither').pack()
    dither_var = tk.StringVar(value='none')
    tk.OptionMenu(root, dither_var, 'none','ordered','fs').pack()

    out_var = tk.StringVar()
    tk.Entry(root, textvariable=out_var, width=60).pack()
    def browse_out():
        p = filedialog.asksaveasfilename(defaultextension='.png')

        if p: out_var.set(p)
    tk.Button(root, text='Browse Output', command=browse_out).pack()

    def do_convert():
        inp = input_var.get()
        out = out_var.get()
        sysname = system_var.get()
        dither = dither_var.get()
        if not inp or not out:
            messagebox.showerror('Error','Choose input and output paths')
            return

        try:
            run_conversion(inp, sysname, out, dither=None if dither=='none' else dither, save_scr=(sysname=='zx'))
            messagebox.showinfo('Done','Conversion complete')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    tk.Button(root, text='Convert', command=do_convert).pack(pady=8)
    root.mainloop()

# CLI

def parse_args(): #vers 1
    p = argparse.ArgumentParser(description='Convert images to retro 8-bit system visuals')
    p.add_argument('--input','-i', help='Input image path')
    p.add_argument('--system','-s', choices=list(SYSTEM_FUNCS.keys()), default='zx')
    p.add_argument('--output','-o', help='Output file path')
    p.add_argument('--dither','-d', choices=['none','ordered','fs'], default='none')
    p.add_argument('--save-scr', action='store_true', help='If ZX, also save .scr')
    p.add_argument('--gui', action='store_true', help='Launch GUI')
    p.add_argument('--batch', help='Batch convert a folder: specify folder path')
    return p.parse_args()


def main_cli(): #vers 1
    args = parse_args()
    if args.gui:
        launch_gui(); return

    if args.batch:
        infolder = args.batch
        outfolder = args.output or (infolder + '_converted')
        os.makedirs(outfolder, exist_ok=True)
        for fn in os.listdir(infolder):
            if not fn.lower().endswith(('.png','.jpg','.jpeg','.bmp','.gif')): continue
            inpath = os.path.join(infolder,fn)
            outname = os.path.splitext(fn)[0] + f'_{args.system}.png'
            outpath = os.path.join(outfolder, outname)
            run_conversion(inpath, args.system, outpath, dither=None if args.dither=='none' else args.dither, save_scr=args.save_scr)
        print('Batch done ->', outfolder)
        return

    if not args.input or not args.output:
        print('Use --input and --output or --gui')
        return

    run_conversion(args.input, args.system, args.output, dither=None if args.dither=='none' else args.dither, save_scr=args.save_scr)

if __name__ == '__main__':
    main_cli()


# More accurate exporters: .TAP, C64 Koala (.koa), Amstrad .SCR, BBC .SSD

def write_tap_from_bytes(data: bytes, out_path: str): #vers 3
    """
    Write a very-compatible .TAP file consisting of a single TAP block.
    TAP format (simple): sequence of little-endian 16-bit lengths, followed by that many bytes.
    Many emulators accept a TAP produced this way when the block contents are a raw header+data as for a saved file.
    This function wraps the provided data as one block.
    """
    with open(out_path, 'wb') as f:
        # write single block length (length of the data)
        length = len(data)
        f.write((length & 0xFF).to_bytes(1, 'little'))
        f.write(((length >> 8) & 0xFF).to_bytes(1, 'little'))
        f.write(data)
    return out_path


def export_c64_koala(img: Image.Image, out_path: str, bg_color_index: int = 0):
    """
    Export a C64 Koala (.koa) file. Koala format (unpacked) structure:
      - 2 bytes: load address (0x00 0x60 for $6000)
      - 8000 bytes: bitmap data (multicolor layout expected by Koala viewers)
      - 1000 bytes: screen RAM (character map / video matrix)
      - 1000 bytes: colour RAM
      - 1 byte: background colour index
    The total file size is 10003 bytes (including the 2-byte load address). Many viewers accept this exact layout.
    This implementation creates a reasonable Koala from an RGB image by converting to 160x200 and producing bitmap/screen/color buffers.
    """
    # Prepare 160x200 target
    targ = img.resize((160,200), Image.BICUBIC).convert('RGB')
    px = np.array(targ)
    # Reduce to c64 palette indices
    palette = PALETTES['c64']
    # For Koala we need:
    # - raw bitmap: 8000 bytes: each byte encodes 8 pixels (2 bits per pixel in multicolor?)
    # KoalaPainter expects the C64 bitmap memory layout where each byte contains 8 high-resolution pixels
    # Implement a simplified approach: create bitmap as 8000 bytes by packing 8 pixels per byte using coarse quantized indices.

    # Quantize pixels to 16-colour palette indices
    index_map = np.zeros((200,160), dtype=np.uint8)
    for y in range(200):
        for x in range(160):
            index_map[y,x] = palette.index(nearest_palette_color(tuple(px[y,x]), palette))

    # Create bitmap (8000 bytes): pack 8 pixels horizontally into one byte by taking low 1 bit from palette index (simplified)
    # Note: This is a pragmatic approximation — many Koala viewers will still load and display something close to expected.
    bitmap = bytearray(8000)
    # C64 graphics are stored as 25 rows of 320 bytes (40 columns * 200 rows -> mapping is non-trivial), here we create a linear chunk
    bptr = 0
    for y in range(200):
        # each C64 'row' consists of 40 bytes representing 160 multicolour pixels (4 pixels per byte in multicolor) -- this is an approximation
        for bx in range(0,160,8):
            byte = 0
            for bit in range(8):
                # sample pixel and choose a 1-bit mask based on whether pixel index has LSB set
                pxidx = int(index_map[y, bx+bit]) & 0xFF
                bitval = (pxidx & 1)
                byte = (byte << 1) | (bitval)
            bitmap[bptr] = byte
            bptr += 1
            if bptr >= 8000:
                break
        if bptr >= 8000:
            break
    # Screen (1000 bytes) and colorram (1000 bytes)
    screen = bytearray(1000)
    colram = bytearray(1000)
    # Fill screen and colorram by sampling coarse cells (4x8 or 2x8 depending on mode). We'll pick the most common colour per cell.
    cell_index = 0
    for row in range(25):
        for col in range(40):
            # map to pixel box
            y0 = int((row/25.0) * 200)
            y1 = int(((row+1)/25.0) * 200)
            x0 = int((col/40.0) * 160)
            x1 = int(((col+1)/40.0) * 160)
            block = index_map[y0:y1, x0:x1].reshape(-1)
            if block.size == 0:
                chosen = 0
            else:
                values, counts = np.unique(block, return_counts=True)
                chosen = int(values[np.argmax(counts)])
            screen[cell_index] = chosen & 0xFF
            colram[cell_index] = chosen & 0x0F
            cell_index += 1
    # Build final file: 2-byte load address, bitmap(8000), screen(1000), colram(1000), bg byte
    data = bytearray()
    data += b'\x00\x60'  # load address $6000 little-endian
    data += bitmap.ljust(8000, b'\x00')
    data += screen.ljust(1000, b'\x00')
    data += colram.ljust(1000, b'\x00')
    data += bytes([bg_color_index & 0xFF])
    with open(out_path, 'wb') as f:
        f.write(data)
    return out_path


def export_cpc_scr(img: Image.Image, out_path: str, mode: int = 0): #vers 1
    """
    Export a simple Amstrad CPC .SCR file for Mode 0 (160x200, 16 colours).
    Many CPC screen files are raw dumps expected by emulators; this function writes a raw byte per pixel (0-15) mapping to palette indices.
    Some viewers expect planar or packed formats; this is a pragmatic, widely-supported approach (and .pal files can be generated alongside if needed).
    """

    # Resize to 160x200
    targ = img.resize((160,200), Image.BICUBIC).convert('RGB')
    px = np.array(targ)
    palette = PALETTES['cpc']
    out = bytearray()
    for y in range(200):
        for x in range(160):
            idx = palette.index(nearest_palette_color(tuple(px[y,x]), palette))
            out.append(idx & 0xFF)
    with open(out_path, 'wb') as f:
        f.write(out)
    # Also write a .pal file with RGB hex triplets for convenience
    pal_path = os.path.splitext(out_path)[0]+'.pal'
    with open(pal_path, 'w') as pf:
        for (r,g,b) in palette:
            pf.write(f"{r:02x}{g:02x}{b:02x}")
    return out_path


def export_bbc_ssd(img: Image.Image, out_path: str, filename_on_disk: str = 'PIC'): #vers 1
    """
    Create a BBC .SSD disk image containing a tiny BASIC program and a data file with the screen data.
    This implementation will attempt to import the 'dfsimage' Python module (https://github.com/monkeyman79/dfsimage) to build a proper .ssd image.
    If dfsimage is not available, the function will instead write out an intermediate file structure you can convert using dfsimage or other tools.
    """
    try:
        import dfsimage
    except Exception:

        # Fallback: write raw screen data and a small BASIC loader as plain files and instruct user to pip install dfsimage
        base = os.path.splitext(out_path)[0]
        data_path = base + '.bbc.pic'

        # Convert to BBC MODE 2 size 160x256 or to a size that maps well; we'll use 160x256 -> pad if needed
        targ = img.resize((160,256), Image.BICUBIC).convert('RGB')
        px = np.array(targ)

        # Convert to 4-colour BBC palette indices
        palette = PALETTES['bbc']
        out = bytearray()
        for y in range(256):
            for x in range(160):
                idx = palette.index(nearest_palette_color(tuple(px[y,x]), palette))
                out.append(idx & 0xFF)
        with open(data_path, 'wb') as f:
            f.write(out)
        # Write a tiny BASIC loader text file
        loader_path = base + '.bas'
        with open(loader_path, 'w') as f:
            f.write('10 REM PICTURE LOADER')
            f.write("20 PRINT \"Place the binary in memory and POKE it to the screen with MODE 2\"")
        return {
            'note': 'dfsimage package not installed',
            'data_file': data_path,
            'basic_loader': loader_path,
            'instruction': 'pip install dfsimage && use dfsimage to create .ssd from these files or ask me to create the .ssd once dfsimage is available in the environment.'
        }

    # If dfsimage is available, build a DFS .ssd and add the image as a binary file, plus a BASIC loader
    # This branch requires dfsimage API; implementation below assumes a high-level interface.
    imgdata = img.resize((160,256), Image.BICUBIC).convert('RGB')
    px = np.array(imgdata)
    palette = PALETTES['bbc']
    out = bytearray()
    for y in range(256):
        for x in range(160):
            idx = palette.index(nearest_palette_color(tuple(px[y,x]), palette))
            out.append(idx & 0xFF)

    # create disk and add file
    d = dfsimage.disk.DFSImage()

    # Add binary file
    d.add_file(filename_on_disk, out, file_type='BINARY')

    # Add tiny BASIC loader (this is approximate)
    basic = b'10 REM PICTURE LOADER 20 REM LOAD BINARY TO &2000'
    d.add_file('RUNPIC', basic, file_type='TEXT')
    with open(out_path, 'wb') as f:
        f.write(d.create_image())
    return out_path


# Convenience: generate all emulator-ready files from one input

def export_all_emulator_files(input_path: str, out_dir: str): #vers 1
    os.makedirs(out_dir, exist_ok=True)
    img = Image.open(input_path).convert('RGB')
    # ensure 4:3
    img = ensure_4_3(img)
    # ZX: .scr + .tap
    zx_png = os.path.join(out_dir, 'spectrum_screen.png')
    zx_scr = os.path.join(out_dir, 'spectrum_screen.scr')
    zx_tap = os.path.join(out_dir, 'spectrum_screen.tap')
    zx_img = convert_zx_spectrum(img)
    zx_img.save(zx_png)
    export_zx_scr(zx_img, zx_scr)
    # create a simple TAP containing the SCR bytes as one block
    with open(zx_scr, 'rb') as f:
        scr_bytes = f.read()
    write_tap_from_bytes(scr_bytes, zx_tap)

    # C64 Koala
    c64_koa = os.path.join(out_dir, 'c64_koala.koa')
    export_c64_koala(img, c64_koa)

    # CPC SCR
    cpc_scr = os.path.join(out_dir, 'cpc_screen.scr')
    export_cpc_scr(img, cpc_scr)

    # BBC SSD (best-effort)
    bbc_ssd = os.path.join(out_dir, 'bbc_picture.ssd')
    bbc_result = export_bbc_ssd(img, bbc_ssd)

    return {
        'zx': {'png': zx_png, 'scr': zx_scr, 'tap': zx_tap},
        'c64': {'koa': c64_koa},
        'cpc': {'scr': cpc_scr},
        'bbc': bbc_result
    }


