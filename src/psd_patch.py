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
H = json.load(open('/workspace/rhw/assets/ham.json')); UW, UH = H['world'][2] - H['world'][0], H['world'][3] - H['world'][1]
sb = H['still']['box']
cbL = F['l']['crocBox']; kL = (cbL[2] - cbL[0]) / sb[2]                       # landscape: as the PSD Hamster_Full
oxL, oyL = cbL[0] - sb[0] * kL, cbL[1] - sb[1] * kL
kP = (F['p']['crocBox'][2] - F['p']['crocBox'][0]) / sb[2] * 0.85            # t111u: portrait slightly smaller
oxP = 540 - H['still']['cx'] * kP                                            # t112u: visible body centred on the screen
oyP = 165 - H['still']['top'] * kP                                           # scythe tip at the logo; waist up shows above the reels
box = lambda ox, oy, k: [round(ox, 1), round(oy, 1), round(ox + UW * k, 1), round(oy + UH * k, 1)]
V['landscape']['croc'] = {'box': box(oxL, oyL, kL), 'front': False}
V['portrait']['croc'] = {'box': box(oxP, oyP, kP), 'front': False}
L['croc'] = {'box': box(oxL, oyL, kL)}
for v, n in (('landscape', 'l'), ('portrait', 'p')):
    x0, y0, x1, y1 = F[n]['logo']; V[v]['logo'] = [x0, y0, round((x1 - x0) / L['logo'][2], 4)]
V['portrait']['logo'] = [540 - 380 * 0.6, 18, 0.6]
# landscape HUD: the PSD wheel sits right of the reels and the frame reaches the bottom -> spin cluster top right, thin bottom bar
lu = V['landscape']['ui']
lu.update({'bSpin': [1712, 866, 0.95], 'bAuto': [1600, 862, 0.62], 'bTurbo': [1588, 946, 0.95], 'bCoins': [1600, 996, 0.62],
           'bHome': [14, 1002, 0.8], 'bMinus': [80, 1003, 0.85], 'bBetBar': [146, 994, 0.85], 'bPlus': [282, 1003, 0.85],
           'bFull': [1628, 14, 0.8], 'bMusic': [1700, 14, 0.8], 'bSound': [1772, 14, 0.8], 'bMenu': [1844, 14, 0.8]})
lt = V['landscape']['text']
for key, x, y, w in (('balance', 22, 955, 186), ('lastWin', 230, 955, 154), ('bet', 150, 1027, 124)): lt[key].update({'x': x, 'y': y, 'h': 26, 'size': 32, 'w': w})
lt['prompt'] = dict(lt.get('prompt', {}), y=1046, h=20)
lt['footer'] = {k: {'x': 0, 'y': 1990, 'w': 10, 'h': 10, 'size': 10} for k in ['totalBet', 'sessionId', 'rtp', 'chance', 'totalWin', 'clock']}
pu = V['portrait']['ui']   # portrait: play cluster centred under the raised reels
pu.update({'bSpin': [458, 1620, 0.82], 'bAuto': [176, 1658, 0.72], 'bMinus': [339, 1672, 0.85], 'bPlus': [679, 1672, 0.85],
           'bTurbo': [795, 1674, 1.2], 'bHome': [22, 22, 0.8], 'bMenu': [100, 22, 0.8], 'bCoins': [178, 18, 0.7], 'bBetBar': [462, 1824, 1]})
s = s[:m.start(1)] + json.dumps([L], separators=(',', ':')) + s[m.end(1):]
rep("  #hBar{position:absolute;left:0;top:944px;width:1920px;height:128px;", "  html:not(.portrait) #hBar{display:none}\n  #hBar{position:absolute;left:0;top:1000px;width:1920px;height:72px;")
rep("  #hBal{left:200px;top:954px;width:350px;height:80px} #hWin{left:1350px;top:954px;width:320px;height:80px} #hBet{left:880px;top:954px;width:163px;height:80px}",
    "  #hBal{left:14px;top:924px;width:200px;height:62px} #hWin{left:222px;top:924px;width:170px;height:62px} #hBet{left:146px;top:996px;width:132px;height:66px}\n"
    "  html:not(.portrait) .hpanel span{font-size:14px;top:4px}")
wl = F['l']['wheel']
rep("  #wheel{position:absolute;left:28px;top:96px;width:262px;height:317px;",
    f"  #wheel{{position:absolute;left:{wl[0]}px;top:{wl[1]}px;width:{round(wl[2]-wl[0],1)}px;height:{round(wl[3]-wl[1],1)}px;")
rep("  #wheel.fs{opacity:0}", "  html.portrait #wheel{left:830px;top:215px;width:230px;height:278px}\n  #wheel.fs{filter:brightness(.8) saturate(.85) hue-rotate(-25deg)}   /* PSD 07: the wheel stays, purple-graded */")
rep("  fsPanel: { L: [22, 106, 262, 150], P: [785, 470, 262, 150] },", "  fsPanel: { L: [22, 106, 262, 150], P: [20, 300, 250, 150] },")
# the PSD frame (dividers + frame + lanterns) over the reels, one full-stage image per orientation
rep('  <div id="xwl"></div>\n', '  <div id="xwl"></div>\n  <img id="frameOv" alt="">\n')
rep("  .soulfly{", "  #frameOv{position:absolute;left:0;top:0;width:1920px;height:1072px;pointer-events:none} html.portrait #frameOv{width:1080px;height:1920px}\n  .soulfly{")
rep("  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",", "  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",\n  'frame-ov-l.webp': \"/*__ASSET:frame-ov-l.webp__*/\",\n  'frame-ov-p.webp': \"/*__ASSET:frame-ov-p.webp__*/\",")
rep("    paintBg(v);\n    const [tx, ty, s] = v.board;", "    paintBg(v);\n    { const fo = g('frameOv'), u = asset(name === 'portrait' ? 'frame-ov-p.webp' : 'frame-ov-l.webp'); if (fo && u) setSrc(fo, u); }\n    const [tx, ty, s] = v.board;")
open(P, 'w', encoding='utf-8').write(s); print('psd ok', V['portrait']['board'])
