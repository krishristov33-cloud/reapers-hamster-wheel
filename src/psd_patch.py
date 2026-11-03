#!/usr/bin/env python3
"""PSD fit (t108u) for src/rhw_template.html, run after patch.py and before anim_patch.py: layout numbers from
   assets/psd_fit.json (tools/psd_fit.py), the frame overlay above the reels, wheel / FS panel / HUD clear of the PSD art."""
import json, re
P = '/workspace/rhw/src/rhw_template.html'
s = open(P, encoding='utf-8').read()
F = json.load(open('/workspace/rhw/assets/psd_fit.json'))
def rep(a, b):
    global s
    if s.count(a) != 1: raise SystemExit(f'miss {s.count(a)}: {a[:90]}')
    s = s.replace(a, b)
m = re.search(r'const LAYOUT = (\[.*?\])\[0\] \|\| null;', s, flags=re.S)
L = json.loads(m.group(1))[0]; V = L['views']
L['symScale'] = F['symK']
rbL, rbP = F['l']['reelBack'], F['p']['reelBack']
k = ((rbP[2] - rbP[0]) / (rbL[2] - rbL[0]) + (rbP[3] - rbP[1]) / (rbL[3] - rbL[1])) / 2
V['portrait']['board'] = [round(rbP[0] - rbL[0] * k, 2), round(rbP[1] - rbL[1] * k, 2), round(k, 5)]
V['landscape']['board'] = [0, 0, 1]
V['landscape']['croc'] = {'box': F['l']['crocBox'], 'front': False}
V['portrait']['croc'] = {'box': F['p']['crocBox'], 'front': False}
L['croc'] = {'box': F['l']['crocBox']}
for v, n in (('landscape', 'l'), ('portrait', 'p')):
    x0, y0, x1, y1 = F[n]['logo']; V[v]['logo'] = [x0, y0, round((x1 - x0) / L['logo'][2], 4)]
# landscape HUD: the PSD wheel sits right of the reels and the frame reaches the bottom -> spin cluster top right, thin bottom bar
lu = V['landscape']['ui']
lu.update({'bSpin': [1700, 118, 1.0], 'bAuto': [1588, 120, 0.75], 'bTurbo': [1574, 228, 1], 'bCoins': [1588, 282, 0.75],
           'bHome': [22, 1012, 0.85], 'bFull': [100, 1012, 0.85], 'bMinus': [802, 1010, 0.85], 'bBetBar': [884, 1003, 1],
           'bPlus': [1046, 1010, 0.85], 'bMusic': [1700, 1012, 0.85], 'bSound': [1772, 1012, 0.85], 'bMenu': [1844, 1012, 0.85]})
lt = V['landscape']['text']
for key, x, w in (('balance', 210, 330), ('lastWin', 1360, 300), ('bet', 884, 155)): lt[key].update({'x': x, 'y': 1034, 'h': 28, 'size': 36, 'w': w})
lt['prompt'] = dict(lt.get('prompt', {}), y=972)
s = s[:m.start(1)] + json.dumps([L], separators=(',', ':')) + s[m.end(1):]
rep("  #hBar{position:absolute;left:0;top:944px;width:1920px;height:128px;", "  #hBar{position:absolute;left:0;top:1000px;width:1920px;height:72px;")
rep("  #hBal{left:200px;top:954px;width:350px;height:80px} #hWin{left:1350px;top:954px;width:320px;height:80px} #hBet{left:880px;top:954px;width:163px;height:80px}",
    "  #hBal{left:200px;top:1004px;width:350px;height:64px} #hWin{left:1350px;top:1004px;width:320px;height:64px} #hBet{left:880px;top:1004px;width:163px;height:64px}\n"
    "  html:not(.portrait) .hpanel span{font-size:14px;top:4px}")
wl = F['l']['wheel']
rep("  #wheel{position:absolute;left:28px;top:96px;width:262px;height:317px;",
    f"  #wheel{{position:absolute;left:{wl[0]}px;top:{wl[1]}px;width:{round(wl[2]-wl[0],1)}px;height:{round(wl[3]-wl[1],1)}px;")
rep("  #wheel.fs{opacity:0}", "  #wheel.fs{filter:brightness(.8) saturate(.85) hue-rotate(-25deg)}   /* PSD 07: the wheel stays, purple-graded */")
rep("  fsPanel: { L: [22, 106, 262, 150], P: [785, 470, 262, 150] },", "  fsPanel: { L: [22, 106, 262, 150], P: [810, 282, 250, 150] },")
# the PSD frame (dividers + frame + lanterns) over the reels, one full-stage image per orientation
rep('  <div id="xwl"></div>\n', '  <div id="xwl"></div>\n  <img id="frameOv" alt="">\n')
rep("  .soulfly{", "  #frameOv{position:absolute;left:0;top:0;width:1920px;height:1072px;pointer-events:none} html.portrait #frameOv{width:1080px;height:1920px}\n  .soulfly{")
rep("  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",", "  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",\n  'frame-ov-l.webp': \"/*__ASSET:frame-ov-l.webp__*/\",\n  'frame-ov-p.webp': \"/*__ASSET:frame-ov-p.webp__*/\",")
rep("    paintBg(v);\n    const [tx, ty, s] = v.board;", "    paintBg(v);\n    { const fo = g('frameOv'), u = asset(name === 'portrait' ? 'frame-ov-p.webp' : 'frame-ov-l.webp'); if (fo && u) setSrc(fo, u); }\n    const [tx, ty, s] = v.board;")
open(P, 'w', encoding='utf-8').write(s); print('psd ok', V['portrait']['board'])
