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
LK = 0.91                                                                   # t114u: landscape reels at 91 %
LT = [round(960 - 960 * LK, 2), round(128 - 135 * LK, 2)]                   # centred, frame top at y 128
V['landscape']['board'] = [LT[0], LT[1], LK]
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
# t114u: ONE line across the bottom (SPIN stays bottom right): info menu sound FX fullscreen | BALANCE | - BET + | WIN | AUTO TURBO
YC, SM = 1029, 0.8
groups = [[('bHome', 76 * SM), ('bMenu', 76 * SM), ('bMusic', 76 * SM), ('bSound', 76 * SM), ('bFull', 76 * SM)], [('hBal', 230)],
          [('bMinus', 72 * 0.85), ('hBet', 150), ('bPlus', 72 * 0.85)], [('hWin', 230)], [('bAuto', 122 * 0.52), ('bTurbo', 108)]]
inner = 10; gw = [sum(w for _, w in g) + inner * (len(g) - 1) for g in groups]
gap = (1690 - 14 - sum(gw)) / (len(groups) - 1); x = 14; POS = {}
for g, w0 in zip(groups, gw):
    for n, w in g: POS[n] = (round(x, 1), w); x += w + inner
    x += gap - inner
lu.update({'bSpin': [1712, 866, 0.95], 'bCoins': [-400, -400, 0.5], 'bBetBar': [POS['hBet'][0] - 2, 986, 1],
           'bAuto': [POS['bAuto'][0], YC - 32, 0.52], 'bTurbo': [POS['bTurbo'][0], YC - 24, 1],
           'bMinus': [POS['bMinus'][0], YC - 31, 0.85], 'bPlus': [POS['bPlus'][0], YC - 31, 0.85]})
for n in ('bHome', 'bMenu', 'bMusic', 'bSound', 'bFull'): lu[n] = [POS[n][0], YC - 30, SM]
lt = V['landscape']['text']
for key, pn in (('balance', 'hBal'), ('lastWin', 'hWin'), ('bet', 'hBet')):
    lt[key].update({'x': POS[pn][0] + 8, 'y': YC, 'h': 26, 'size': 32, 'w': POS[pn][1] - 16})
lt['prompt'] = dict(lt.get('prompt', {}), y=956, h=20)
lt['footer'] = {k: {'x': 0, 'y': 1990, 'w': 10, 'h': 10, 'size': 10} for k in ['totalBet', 'sessionId', 'rtp', 'chance', 'totalWin', 'clock']}
HUDL = ' '.join(f"#{n}{{left:{POS[n][0]}px;top:{YC - 31}px;width:{POS[n][1]}px;height:62px}}" for n in ('hBal', 'hBet', 'hWin'))
pu = V['portrait']['ui']   # portrait: play cluster centred under the raised reels
pu.update({'bSpin': [458, 1620, 0.82], 'bAuto': [176, 1658, 0.72], 'bMinus': [339, 1672, 0.85], 'bPlus': [679, 1672, 0.85],
           'bTurbo': [795, 1674, 1.2], 'bHome': [24, 1676, 0.8], 'bMenu': [995, 1676, 0.8], 'bCoins': [-400, -400, 0.5], 'bBetBar': [462, 1824, 1]})   # t114u: no BET button; i bottom-left, ≡ bottom-right
s = s[:m.start(1)] + json.dumps([L], separators=(',', ':')) + s[m.end(1):]
rep("  #hBar{position:absolute;left:0;top:944px;width:1920px;height:128px;", "  #hBar{position:absolute;left:0;top:984px;width:1920px;height:88px;")
rep("  #hBal{left:200px;top:954px;width:350px;height:80px} #hWin{left:1350px;top:954px;width:320px;height:80px} #hBet{left:880px;top:954px;width:163px;height:80px}",
    "  " + HUDL + "\n"
    "  html:not(.portrait) .hpanel span{font-size:14px;top:4px}")
wl = F['l']['wheel']
rep("  #wheel{position:absolute;left:28px;top:96px;width:262px;height:317px;",
    f"  #wheel{{position:absolute;left:{wl[0]}px;top:{wl[1]}px;width:{round(wl[2]-wl[0],1)}px;height:{round(wl[3]-wl[1],1)}px;")
rep("  #wheel.fs{opacity:0}", "  html.portrait #wheel{left:830px;top:215px;width:230px;height:278px}\n  #wheel.fs{filter:brightness(.8) saturate(.85) hue-rotate(-25deg)}   /* PSD 07: the wheel stays, purple-graded */")
rep("  fsPanel: { L: [22, 106, 262, 150], P: [785, 470, 262, 150] },", "  fsPanel: { L: [22, 106, 262, 150], P: [20, 300, 250, 150] },")
# the PSD frame (dividers + frame + lanterns) over the reels, one full-stage image per orientation
rep('  <div id="xwl"></div>\n', '  <div id="xwl"></div>\n  <img id="frameOv" alt="">\n')
rep("  .soulfly{", "  #frameOv{position:absolute;left:0;top:0;width:1920px;height:1072px;pointer-events:none} html.portrait #frameOv{width:1080px;height:1920px}\n  html:not(.portrait) #frameOv,html:not(.portrait) #reelBackOv{transform-origin:0 0;transform:translate(" + f"{LT[0]}px,{LT[1]}px) scale({LK})" + "}\n  .soulfly{")
rep("  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",", "  'reelframe.png': \"/*__ASSET:reelframe.png__*/\",\n  'frame-ov-l.webp': \"/*__ASSET:frame-ov-l.webp__*/\",\n  'frame-ov-p.webp': \"/*__ASSET:frame-ov-p.webp__*/\",")
rep("    paintBg(v);\n    const [tx, ty, s] = v.board;", "    paintBg(v);\n    { const fo = g('frameOv'), u = asset(name === 'portrait' ? 'frame-ov-p.webp' : 'frame-ov-l.webp'); if (fo && u) setSrc(fo, u); }\n    const [tx, ty, s] = v.board;")
open(P, 'w', encoding='utf-8').write(s); print('psd ok', V['portrait']['board'])
