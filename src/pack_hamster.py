#!/usr/bin/env python3
"""Animoto game_pack_v1 hamster clips 02-09 -> reduced CRC1 bins (one seq each) on a shared 'world' box of the 1920x1080
   reference canvas (all clips + the still share the feet pivot 911,824 there). Writes assets/ham-NN.bin, ham-still.webp and
   ham.json (world box, per-clip crop box in world px, fps, frames, frame-0 visible-body centre)."""
import io, json, struct, os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
G = '/workspace/aiko/projects/ReapersHamsterWheel/animations/game_pack_v1'
OUT = '/workspace/rhw/assets'
U = [400, 0, 1480, 1040]          # world box in canvas px (clips are clipped to it)
K = 0.5                           # stored px per canvas px
Q = 64
def read(p):
    B = open(p, 'rb').read(); n = struct.unpack_from('<I', B, 4)[0]; o = 8; seqs = []
    for _ in range(n):
        fps, c = struct.unpack_from('<II', B, o); o += 8; lens = struct.unpack_from(f'<{c}I', B, o); o += 4 * c; seqs.append((fps / 1000, lens))
    fr = []
    for fps, lens in seqs:
        for l in lens: fr.append(B[o:o + l]); o += l
    return seqs[0][0], fr
def abox(im): return im.getchannel('A').point(lambda v: 255 if v > 40 else 0).getbbox()
def job(c):
    fps, fr = read(f"{G}/{c['files']['crc1']}")
    rs = c['renderScale']; ox, oy = c['cropOffset']; fw, fh = c['frameSize']
    X0, Y0, X1, Y1 = max(U[0], ox), max(U[1], oy), min(U[2], ox + fw * rs), min(U[3], oy + fh * rs)
    w, h = round((X1 - X0) * K), round((Y1 - Y0) * K)
    blob, lens, cx0 = b'', [], None
    for i, d in enumerate(fr):
        im = Image.open(io.BytesIO(d)).convert('RGBA')
        im = im.crop((round((X0 - ox) / rs), round((Y0 - oy) / rs), round((X1 - ox) / rs), round((Y1 - oy) / rs))).resize((w, h), Image.LANCZOS)
        if i == 0:
            b = abox(im); cx0 = X0 + (b[0] + b[2]) / 2 / K
        bb = io.BytesIO(); im.save(bb, 'WEBP', quality=Q, method=4); lens.append(len(bb.getvalue())); blob += bb.getvalue()
    n = c['name'][:2]
    open(f'{OUT}/ham-{n}.bin', 'wb').write(b'CRC1' + struct.pack('<III', 1, round(fps * 1000), len(lens)) + struct.pack(f'<{len(lens)}I', *lens) + blob)
    return {'name': c['name'], 'f': f'ham-{n}.bin', 'fps': fps, 'n': len(lens), 'box': [X0 - U[0], Y0 - U[1], X1 - X0, Y1 - Y0], 'cx0': round(cx0 - U[0], 1),
            'kb': os.path.getsize(f'{OUT}/ham-{n}.bin') // 1024}
if __name__ == '__main__':
    m = json.load(open(f'{G}/manifest.json'))
    clips = [c for c in m['clips'] if c['group'] == 'hamster' and c['name'] != '01_idle']
    with ProcessPoolExecutor() as ex: res = list(ex.map(job, clips))
    st = Image.open(f'{G}/hamster/lj_dropin/hamster-still.webp').convert('RGBA'); cb = m['ljDropIn']['canvasBox']
    b = abox(st); still = {'box': [cb[0] - U[0], cb[1] - U[1], st.size[0], st.size[1]], 'cx': round(cb[0] + (b[0] + b[2]) / 2 - U[0], 1),
                           'top': cb[1] + b[1] - U[1], 'feet': [911 - U[0], 824 - U[1]]}
    st.save(f'{OUT}/ham-still.webp', 'WEBP', quality=88)
    json.dump({'world': U, 'still': still, 'clips': res}, open(f'{OUT}/ham.json', 'w'), indent=1)
    for r in res: print(r)
    print('still', still, 'total KB', sum(r['kb'] for r in res))
