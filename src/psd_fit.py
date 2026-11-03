#!/usr/bin/env python3
"""PSD pass-2 fit (t108u): Aiko's work/p2/layouts JSON = the layer records of psd/RHW_{Landscape,Portrait}.psd (previews in
   psd/previews_pass2). Rebuild the pieces whose placement must match the PSD exactly:
   - bg-*: Background + (FS: FS_PurpleGrade multiply) + Reel_Back + FX_LanternGlow (screen), full stage
   - frame-ov-{l,p}: Reel_Dividers + Reel_Frame + Lanterns, full stage, drawn ABOVE the reels (as in the PSD)
   - sym-*: native PSD symbol size on the 400 sprite canvas (sprite px = stage px * 400 / (256 * SYM_K))
   - psd_fit.json: reel window, board, logo, wheel, hamster boxes (stage px) for tools/psd_patch.py"""
import json, os
from PIL import Image, ImageChops
ROOT = '/workspace/aiko/projects/ReapersHamsterWheel'; LAY = ROOT + '/work/p2/layouts'; OUT = '/workspace/rhw/assets'
LS = 1920 / 2752; SYM_K = 0.8
J = lambda n: json.load(open(f'{LAY}/{n}.json'))
def blend(cv, im, mode, op):
    if op < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * op)))
    if mode == 'normal': return Image.alpha_composite(cv, im)
    base = cv.convert('RGB'); top = Image.alpha_composite(Image.new('RGBA', cv.size, (0, 0, 0, 255) if mode == 'screen' else (255, 255, 255, 255)), im).convert('RGB')
    out = (ImageChops.multiply if mode == 'multiply' else ImageChops.screen)(base, top).convert('RGBA'); out.putalpha(cv.getchannel('A')); return out
def compose(name, keep, size, sc, opaque=False):
    W, H = size; cv = Image.new('RGBA', size, (0, 0, 0, 255 if opaque else 0))
    for l in J(name)['layers']:
        if not keep(l): continue
        im = Image.open(l['src']).convert('RGBA').resize((max(1, round(l['qw'] * sc)), max(1, round(l['qh'] * sc))), Image.LANCZOS)
        lay = Image.new('RGBA', size, (0, 0, 0, 0)); lay.paste(im, (round(l['qx'] * sc), round(l['qy'] * sc)))
        cv = blend(cv, lay, l.get('blend', 'normal'), l.get('opacity', 1))
    return cv
def save(im, n, q=80, rgb=False):
    (im.convert('RGB') if rgb else im).save(f'{OUT}/{n}', 'WEBP', quality=q, method=6); print(n, im.size, os.path.getsize(f'{OUT}/{n}') // 1024, 'KB')
BGK = lambda l: l.get('group') == 'Background' or l['name'] in ('FS_PurpleGrade', 'Reel_Back', 'FX_LanternGlow')
OVK = lambda l: l['name'] in ('Reel_Dividers', 'Reel_Frame') or l.get('group') == 'Lanterns'
V = {'l': ('RHW_L_00_BaseGame', 'RHW_L_07_FreeSpins_Scene', (1920, 1072), LS), 'p': ('RHW_P_00_BaseGame', 'RHW_P_07_FreeSpins_Scene', (1080, 1920), 1)}
out = {}
for v, (b, f, size, sc) in V.items():
    nm = 'landscape' if v == 'l' else 'portrait'
    save(compose(b, BGK, size, sc, True), f'bg-{nm}.webp', 80, True)
    save(compose(f, BGK, size, sc, True), f'bg-{nm}-fs.webp', 80, True)
    save(compose(b, OVK, size, sc), f'frame-ov-{v}.webp', 82)
    box = lambda n: next([l['qx'] * sc, l['qy'] * sc, (l['qx'] + l['qw']) * sc, (l['qy'] + l['qh']) * sc] for l in J(b)['layers'] if l['name'] == n)
    out[v] = {k: [round(x, 1) for x in box(n)] for k, n in [('reelBack', 'Reel_Back'), ('logo', 'Logo'), ('wheel', 'Wheel_Body'), ('hamster', 'Hamster_Full'),
              ('r1c1', 'Sym_r1c1_J'), ('r4c5', 'Sym_r4c5_J')]}
# hamster: map the idle still's visible art onto Hamster_Full's visible art
hb = Image.open(ROOT + '/elements/shared/Hamster_Full.png').getchannel('A').point(lambda x: 255 if x > 40 else 0).getbbox()
hs = Image.open(ROOT + '/elements/shared/Hamster_Full.png').size
st = Image.open(f'{OUT}/croc-still.webp').convert('RGBA'); sb = st.getchannel('A').point(lambda x: 255 if x > 40 else 0).getbbox()
for v in out:
    X0, Y0, X1, Y1 = out[v]['hamster']; kx = (X1 - X0) / hs[0]; ky = (Y1 - Y0) / hs[1]
    ax0, ay0, ax1, ay1 = X0 + hb[0] * kx, Y0 + hb[1] * ky, X0 + hb[2] * kx, Y0 + hb[3] * ky   # art box on stage
    k = (ay1 - ay0) / (sb[3] - sb[1])                                                            # still px -> stage px (height match)
    cx = (ax0 + ax1) / 2 - ((sb[0] + sb[2]) / 2) * k
    out[v]['crocBox'] = [round(cx, 1), round(ay0 - sb[1] * k, 1), round(cx + st.size[0] * k, 1), round(ay0 - sb[1] * k + st.size[1] * k, 1)]
# symbols at PSD native size
SYM = {'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A', 'KEY': 'Cross', 'STUD': 'Potion', 'BANDANA': 'Spellbook', 'RING': 'Lantern',
       'BLADE': 'CrocSkull', 'BOTTLE': 'Scythe', 'W': 'WILD', 'CROWN': 'SCATTER', 'XW': 'WILD'}
lay = {l['name'].split('_', 2)[2]: l for l in J('RHW_L_00_BaseGame')['layers'] if l['name'].startswith('Sym_')}
f = 400 / (256 * SYM_K) * LS
for g, n in SYM.items():
    l = lay[n]; im = Image.open(l['src']).convert('RGBA').resize((round(l['qw'] * f), round(l['qh'] * f)), Image.LANCZOS)
    c = Image.new('RGBA', (400, 400), (0, 0, 0, 0)); c.alpha_composite(im, ((400 - im.size[0]) // 2, (400 - im.size[1]) // 2)); save(c, f'sym-{g}.webp', 88)
co = Image.open(ROOT + '/elements/fx_skullCoin_1.png').convert('RGBA'); co.thumbnail((300, 300), Image.LANCZOS)
c = Image.new('RGBA', (400, 400)); c.alpha_composite(co, ((400 - co.size[0]) // 2, (400 - co.size[1]) // 2)); save(c, 'sym-COIN.webp', 88)
out['symK'] = SYM_K
json.dump(out, open(f'{OUT}/psd_fit.json', 'w'), indent=1); print(json.dumps(out))
