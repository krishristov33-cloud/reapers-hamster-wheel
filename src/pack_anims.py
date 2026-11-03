#!/usr/bin/env python3
"""Animoto symbol animations v1 (PNG fallback, 400x400 @30fps, straight alpha) -> WebP atlases for the canvas build.
   Each frame is re-fitted onto the game sprite canvas (alpha-bbox of the anim's first frame matched to sym-X.webp,
   which also fixes the WILD's off-centre texture box), downscaled to PX and decimated to 15 fps (one-shots keep the last frame)."""
import glob, json, os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
SRC = '/workspace/aiko/projects/ReapersHamsterWheel/animations/symbols'
OUT = '/workspace/rhw/assets'
PX, COLS, Q = 180, 10, 68          # t111u: full 30 fps (no decimation), 180 px cells
MAP = {'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A', 'KEY': 'Cross', 'STUD': 'Potion', 'BANDANA': 'Spellbook', 'RING': 'Lantern',
       'BLADE': 'CrocSkull', 'BOTTLE': 'Scythe', 'W': 'WILD', 'CROWN': 'SCATTER', 'COIN': 'SkullCoin'}
JOBS = [(g, 'win') for g in MAP if g not in ('CROWN', 'COIN')] + [(g, 'reap_to_coin') for g in 'JQKA'] + \
       [('CROWN', a) for a in ('land', 'anticipation', 'flyoff', 'notch_hit')] + [('COIN', a) for a in ('idle', 'collect')] + [(g, 'idle') for g in MAP if g != 'COIN']
LOOP = {'anticipation', 'flyoff', 'idle'}

REF = OUT + '/psd_sym'                 # PSD-size stills written by tools/psd_fit.py (the placement reference)
IDLE_PX = 160                           # t114u: idle loops a bit smaller (they run on every resting cell)

def fitxf(g, first):
    """scale/offset (floats) mapping the anim canvas onto the PSD still's canvas (both 400x400): alpha bboxes matched"""
    th = lambda im: im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    a = th(Image.open(first).convert('RGBA')); b = th(Image.open(f'{REF}/sym-{g}.webp').convert('RGBA'))
    s = ((b[2] - b[0]) / (a[2] - a[0]) + (b[3] - b[1]) / (a[3] - a[1])) / 2
    return s, (b[0] + b[2]) / 2 - (a[0] + a[2]) / 2 * s, (b[1] + b[3]) / 2 - (a[1] + a[3]) / 2 * s

def place(f, s, ox, oy):
    """one anim frame on the 400 sprite canvas, exact (sub-pixel) affine placement"""
    im = Image.open(f).convert('RGBA')
    return im.transform((400, 400), Image.AFFINE, (1 / s, 0, -ox / s, 0, 1 / s, -oy / s), Image.BICUBIC)

def job(ga):
    g, an = ga
    fr = sorted(glob.glob(f'{SRC}/{MAP[g]}/png/{an}/*.png'))
    base = sorted(glob.glob(f'{SRC}/{MAP[g]}/png/idle/*.png'))[0]       # every anim of a symbol uses the idle f0 fit
    s, ox, oy = fitxf(g, base)
    px = IDLE_PX if an == 'idle' else PX
    n = len(fr); rows = (n + COLS - 1) // COLS
    at = Image.new('RGBA', (COLS * px, rows * px), (0, 0, 0, 0))
    for i, f in enumerate(fr):
        at.paste(place(f, s, ox, oy).resize((px, px), Image.LANCZOS), ((i % COLS) * px, (i // COLS) * px))
    if an == 'idle':                                                     # the reel still = idle frame 0, same placement
        place(base, s, ox, oy).save(f'{OUT}/sym-{g}.webp', 'WEBP', quality=90, method=6)
    name = f'anim-{g}-{an.replace("_", "")}.webp'
    at.save(f'{OUT}/{name}', 'WEBP', quality=Q, method=4)
    return f'{g}:{an}', {'f': name, 'n': n, 'c': COLS, 'loop': an in LOOP, 'fps': 30, 'kb': os.path.getsize(f'{OUT}/{name}') // 1024, 's': round(s, 3)}

if __name__ == '__main__':
    with ProcessPoolExecutor() as ex: res = dict(ex.map(job, JOBS))
    json.dump(res, open(f'{OUT}/anims.json', 'w'), indent=0)
    for k, v in res.items(): print(k, v)
    print('total KB', sum(v['kb'] for v in res.values()))
