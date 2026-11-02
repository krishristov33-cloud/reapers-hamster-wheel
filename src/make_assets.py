#!/usr/bin/env python3
"""Reaper's Hamster Wheel: build assets/ from Aiko's art (pass-1). Re-run after Aiko's pass-2 lands.
   ROOT = Aiko's project; layouts in work/p1/layouts/RHW_{L,P}_NN_*.json drive every full-screen composite."""
import json, os, struct, glob, shutil
from PIL import Image
ROOT = '/workspace/aiko/projects/ReapersHamsterWheel'
LAY = ROOT + '/work/p2/layouts'      # pass 2 (2026-11-03)
OUT = '/workspace/rhw/assets'
LJ = '/workspace/rhw/assets_lj'
os.makedirs(OUT, exist_ok=True)
A = lambda p: Image.open(os.path.join(ROOT, p)).convert('RGBA')
LS = 1920 / 2752                      # Aiko landscape px -> LJ landscape stage px (1920x1072)

def compose(name, keep, size, scale):
    """composite the layout's layers that keep(layer) accepts, onto a transparent canvas"""
    d = json.load(open(f'{LAY}/{name}.json'))
    W, H = size
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for l in d['layers']:
        if not keep(l): continue
        src = l['src']
        if not os.path.exists(src): print('  missing', src); continue
        im = Image.open(src).convert('RGBA')
        w, h = max(1, round(l['qw'] * scale)), max(1, round(l['qh'] * scale))
        im = im.resize((w, h), Image.LANCZOS)
        if l.get('opacity', 1) < 1:
            a = im.getchannel('A').point(lambda v, o=l['opacity']: int(v * o)); im.putalpha(a)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        layer.paste(im, (round(l['qx'] * scale), round(l['qy'] * scale)))
        cv = Image.alpha_composite(cv, layer)
    return cv

def save(im, name, q=82, rgb=False):
    p = os.path.join(OUT, name)
    (im.convert('RGB') if rgb else im).save(p, 'WEBP', quality=q, method=6)
    print(f'{name:32s} {im.size} {os.path.getsize(p)//1024} KB')

BG = lambda l: l.get('group') == 'Background'
def purple(im):
    t = Image.new('RGBA', im.size, (60, 10, 90, 60)); return Image.alpha_composite(im, t)
# 1) backgrounds: sky / tombstones / fog only (reels, hamster, wheel, logo are live pieces)
save(compose('RHW_L_00_BaseGame', BG, (1920, 1072), LS), 'bg-landscape.webp', 80, True)
save(compose('RHW_P_00_BaseGame', BG, (1080, 1920), 1), 'bg-portrait.webp', 80, True)
save(purple(compose('RHW_L_07_FreeSpins_Scene', BG, (1920, 1072), LS)), 'bg-landscape-fs.webp', 80, True)
save(purple(compose('RHW_P_07_FreeSpins_Scene', BG, (1080, 1920), 1)), 'bg-portrait-fs.webp', 80, True)

# 2) reel frame: back + dividers + frame + lanterns in frame-source px (1152x864), window [128,100,1023,784]
fm = json.load(open(ROOT + '/work/p1/frame_meta.json'))
fr = Image.new('RGBA', (1152, 864), (0, 0, 0, 0))
x0, y0, x1, y1 = fm['window']
back = Image.new('RGBA', (x1 - x0, y1 - y0), Image.open(ROOT + '/elements/shared/Reel_Back_px.png').convert('RGBA').getpixel((1, 1))[:3] + (224,))
fr.paste(back, (x0, y0))
for f in ['Reel_Dividers_src', 'Reel_Frame_src']:
    fr = Image.alpha_composite(fr, A(f'elements/shared/{f}.png'))
for n, (a, b, c, d) in fm['lanterns']:
    im = A(f'elements/shared/{n}.png').resize((c - a, d - b), Image.LANCZOS)
    lay = Image.new('RGBA', fr.size, (0, 0, 0, 0)); lay.paste(im, (a, b)); fr = Image.alpha_composite(fr, lay)
fr = fr.resize((1152, 864), Image.LANCZOS)
save(fr, 'reelframe.webp', 85)
# free spins: the same frame with a purple tint over the reel back
fsf = fr.copy(); tint = Image.new('RGBA', (x1 - x0, y1 - y0), (70, 20, 90, 70))
lay = Image.new('RGBA', fr.size, (0, 0, 0, 0)); lay.paste(tint, (x0, y0)); fsf = Image.alpha_composite(fsf, lay)
save(fsf, 'reelframe-fs.webp', 85)

# 3) logo (in-game)
lg = A('elements/shared/Logo_BaseGame.png'); lg.thumbnail((760, 400)); save(lg, 'logo.webp', 88)

# 4) symbols: 400x400 canvas, art fitted into FIT px, centred (LJ sprite contract)
SYM = {'J': 'Sym_J', 'Q': 'Sym_Q', 'K': 'Sym_K', 'A': 'Sym_A', 'KEY': 'Sym_Cross', 'STUD': 'Sym_Potion_v2',
       'BANDANA': 'Sym_Spellbook', 'RING': 'Sym_Lantern', 'BLADE': 'Sym_CrocSkull', 'BOTTLE': 'Sym_Scythe',
       'W': 'Sym_WILD', 'CROWN': 'Sym_SCATTER', 'XW': 'Sym_WILD'}
FIT = {'W': 330, 'CROWN': 330}
def sprite(im, fit):
    im = im.copy(); im.thumbnail((fit, fit), Image.LANCZOS)
    if max(im.size) < fit:
        k = fit / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    c = Image.new('RGBA', (400, 400), (0, 0, 0, 0)); c.paste(im, ((400 - im.width) // 2, (400 - im.height) // 2), im); return c
for s, f in SYM.items():
    save(sprite(A(f'elements/shared/{f}.png'), FIT.get(s, 310)), f'sym-{s}.webp', 88)
save(sprite(A('elements/fx_skullCoin_1.png'), 300), 'sym-COIN.webp', 88)

# 5) wheel of doom (static art; the page lights its notches)
wb = A('elements/shared/Wheel_Body.png'); wb.thumbnail((420, 520)); save(wb, 'wheel.webp', 85)
sm = A('elements/shared/Wheel_SkullMarker.png'); sm.thumbnail((120, 220)); save(sm, 'wheel-skull.webp', 88)

# 6) splashes, full-screen composites per view (no underlay / darken: the page dims the game itself)
NOT_UNDER = lambda l: l['name'] not in ('Underlay_Game', 'Darken')
BOX = {}
def screen(nn, keep, tag, crop=False):
    L = sorted(glob.glob(f'{LAY}/RHW_L_{nn}_*.json'))[0].split('/')[-1][:-5]
    P = sorted(glob.glob(f'{LAY}/RHW_P_{nn}_*.json'))[0].split('/')[-1][:-5]
    for v, name, size, sc in (('l', L, (1920, 1072), LS), ('p', P, (1080, 1920), 1)):
        im = compose(name, keep, size, sc)
        box = [0, 0, size[0], size[1]]
        if crop:
            b = im.getbbox(); im = im.crop(b); box = [b[0], b[1], b[2] - b[0], b[3] - b[1]]
        BOX[f'{tag}-{v}'] = box
        save(im, f'splash-{tag}-{v}.webp', 78)
COUNT = lambda l: l['group'] in ('Sign_10FreeSpins', 'FS_Counter')
TITLE = lambda l: l['group'] == 'Title'
# REAP SPINS trigger: frame = everything but the title + "10 FREE SPINS" text; congrats = title; count = the text
screen('02', lambda l: NOT_UNDER(l) and not TITLE(l) and not COUNT(l), 'fs-frame')
screen('02', TITLE, 'fs-congrats', True)
screen('02', COUNT, 'fs-count', True)
# REAP SPINS total win: frame = all but the title text; title = TOTAL WIN text
screen('03', lambda l: NOT_UNDER(l) and l['group'] != 'Title', 'tw-frame')
screen('03', TITLE, 'tw-title', True)
screen('04', NOT_UNDER, 'bigwin')
screen('05', NOT_UNDER, 'megawin')
screen('06', NOT_UNDER, 'epicwin')
# intro: the whole screen (its own background)
screen('01', lambda l: True, 'intro')

SKIP_HAMSTER = True
# 7) the hamster idle — SUPERSEDED: Animoto's game_pack_v1 lj_dropin bin is copied over this output (see README)
# 7) the hamster idle (LJ croc player: CRC1 = 2 loops of webp frames), common crop over both loops
SEQ = ROOT + '/animations/sequences'
seqs = [] if SKIP_HAMSTER else ['01_idle', '05_smug_cheer']
metas = [json.load(open(f'{SEQ}/{s}/{s}.json')) for s in seqs]
bx0 = 0 if not seqs else min(m['cropOffset'][0] for m in metas); by0 = 0 if not seqs else min(m['cropOffset'][1] for m in metas)
bx1 = 1 if not seqs else max(m['cropOffset'][0] + m['width'] for m in metas); by1 = 1 if not seqs else max(m['cropOffset'][1] + m['height'] for m in metas)
TH = 460; k = TH / (by1 - by0); TW = round((bx1 - bx0) * k)
blob = b''; head = b'CRC1' + struct.pack('<I', len(seqs)); tables = b''
STEP = 2                                           # every 2nd frame (12 fps) keeps the file light
for s, m in zip(seqs, metas):
    files = sorted(glob.glob(f'{SEQ}/{s}/{s}_*.png'))[::STEP]
    lens = []
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGBA'); c = Image.new('RGBA', (bx1 - bx0, by1 - by0), (0, 0, 0, 0))
        c.paste(im, (m['cropOffset'][0] - bx0, m['cropOffset'][1] - by0)); c = c.resize((TW, TH), Image.LANCZOS)
        import io; b = io.BytesIO(); c.save(b, 'WEBP', quality=72, method=4); data = b.getvalue()
        lens.append(len(data)); blob += data
        if s == seqs[0] and i == 0: c.save(OUT + '/croc-still.webp', 'WEBP', quality=85)
    tables += struct.pack('<II', int(m['fps'] / STEP * 1000), len(lens)) + b''.join(struct.pack('<I', x) for x in lens)
if seqs: open(OUT + '/croc-idle.bin', 'wb').write(head + tables + blob)
print('croc-idle.bin', TW, TH, os.path.getsize(OUT + '/croc-idle.bin') // 1024, 'KB')
json.dump({'hamster': [TW, TH], 'boxes': BOX}, open(OUT + '/meta.json', 'w'))

# 8) kept from LEVEE JAW (UI chrome, font, music, spin button pieces, START plate)
for f in ['roboto.woff2', 'theme.mp3']:            # UI2: no LEVEE JAW UI sheet / spin / START plates any more
    shutil.copy(f'{LJ}/{f}', f'{OUT}/{f}')

# Animoto game pack v1 drop-in (overrides step 7)
PK = ROOT + '/animations/game_pack_v1/hamster/lj_dropin'
if os.path.exists(PK):
    shutil.copy(PK + '/hamster-idle.bin', OUT + '/croc-idle.bin'); shutil.copy(PK + '/hamster-still.webp', OUT + '/croc-still.webp')
    m = json.load(open(OUT + '/meta.json')); m['hamster'] = [464, 622]; json.dump(m, open(OUT + '/meta.json', 'w'))
