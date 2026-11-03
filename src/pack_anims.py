#!/usr/bin/env python3
"""Animoto symbol animations v1 (PNG fallback, 400x400 @30fps, straight alpha) -> WebP atlases for the canvas build.
   Each frame is re-fitted onto the game sprite canvas (alpha-bbox of the anim's first frame matched to sym-X.webp,
   which also fixes the WILD's off-centre texture box), downscaled to PX and decimated to 15 fps (one-shots keep the last frame)."""
import glob, json, os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
SRC = '/workspace/aiko/projects/ReapersHamsterWheel/animations/symbols'
OUT = '/workspace/rhw/assets'
PX, COLS, Q = 180, 10, 76          # t111u: full 30 fps (no decimation), 180 px cells
MAP = {'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A', 'KEY': 'Cross', 'STUD': 'Potion', 'BANDANA': 'Spellbook', 'RING': 'Lantern',
       'BLADE': 'CrocSkull', 'BOTTLE': 'Scythe', 'W': 'WILD', 'CROWN': 'SCATTER', 'COIN': 'SkullCoin'}
JOBS = [(g, 'win') for g in MAP if g not in ('CROWN', 'COIN')] + [(g, 'reap_to_coin') for g in 'JQKA'] + \
       [('CROWN', a) for a in ('land', 'anticipation', 'flyoff', 'notch_hit')] + [('COIN', a) for a in ('idle', 'collect')]
LOOP = {'anticipation', 'flyoff', 'idle'}

def fitxf(g, first):
    """scale/offset that maps the anim canvas onto the static sprite canvas (both 400x400)"""
    a = Image.open(first).getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    b = Image.open(f'{OUT}/sym-{g}.webp').convert('RGBA').getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
    s = ((b[2] - b[0]) / (a[2] - a[0]) + (b[3] - b[1]) / (a[3] - a[1])) / 2
    cxa, cya = (a[0] + a[2]) / 2, (a[1] + a[3]) / 2; cxb, cyb = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    return s, cxb - cxa * s, cyb - cya * s

def job(ga):
    g, an = ga
    fr = sorted(glob.glob(f'{SRC}/{MAP[g]}/png/{an}/*.png'))
    base = sorted(glob.glob(f'{SRC}/{MAP[g]}/png/{"idle" if an != "reap_to_coin" else an}/*.png'))[0]
    s, ox, oy = fitxf(g, base)
    k = PX / 400
    pick = fr                                   # every source frame (30 fps)
    n = len(pick); rows = (n + COLS - 1) // COLS
    at = Image.new('RGBA', (COLS * PX, rows * PX), (0, 0, 0, 0))
    for i, f in enumerate(pick):
        im = Image.open(f).convert('RGBA')
        im = im.resize((round(400 * s * k), round(400 * s * k)), Image.LANCZOS)
        at.alpha_composite(im, (round((i % COLS) * PX + ox * k), round((i // COLS) * PX + oy * k))) if ox >= 0 and oy >= 0 else \
            at.paste(Image.alpha_composite(Image.new('RGBA', (PX, PX)), _crop(im, ox * k, oy * k)), ((i % COLS) * PX, (i // COLS) * PX))
    name = f'anim-{g}-{an.replace("_", "")}.webp'
    at.save(f'{OUT}/{name}', 'WEBP', quality=Q, method=4)
    return f'{g}:{an}', {'f': name, 'n': n, 'c': COLS, 'loop': an in LOOP, 'fps': 30, 'kb': os.path.getsize(f'{OUT}/{name}') // 1024, 's': round(s, 3)}

def _crop(im, ox, oy):
    c = Image.new('RGBA', (PX, PX)); c.alpha_composite(im, (0, 0), (round(-ox), round(-oy))) if True else None
    return c

if __name__ == '__main__':
    with ProcessPoolExecutor() as ex: res = dict(ex.map(job, JOBS))
    json.dump(res, open(f'{OUT}/anims.json', 'w'), indent=0)
    for k, v in res.items(): print(k, v)
    print('total KB', sum(v['kb'] for v in res.values()))
