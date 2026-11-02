#!/usr/bin/env python3
"""LEVEE JAW template -> REAPER'S HAMSTER WHEEL template (src/rhw_template.html). Every edit is an exact-string
   replacement that must match once, so a changed source fails loudly."""
import json, re
SRC = '/workspace/rhw/src/lj_template.html'
OUT = '/workspace/rhw/src/rhw_template.html'
s = open(SRC, encoding='utf-8').read()
meta = json.load(open('/workspace/rhw/assets/meta.json'))
B = meta['boxes']
def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count: raise SystemExit(f'patch: expected {count} match(es), found {n}: {old[:90]!r}')
    s = s.replace(old, new)
def rep_re(pat, new):
    global s
    m = re.findall(pat, s, flags=re.S)
    if len(m) != 1: raise SystemExit(f'patch: regex matched {len(m)}: {pat[:80]}')
    s = re.sub(pat, lambda _: new, s, flags=re.S)

# ---------------------------------------------------------------- head / engine
rep('<title>LEVEE JAW — playable prototype</title>', "<title>REAPER'S HAMSTER WHEEL — playable prototype</title>")
eng = open('/workspace/rhw/src/engine.js', encoding='utf-8').read()
rep_re(r'<script>/\* =+\r?\n   LEVEE JAW — math engine.*?</script>', '<script>' + eng + '</script>')

# ---------------------------------------------------------------- layout (board px, 1920x1072 board)
WX0, WX1, WY0, WY1 = 494, 1422, 115, 825          # reel window: 5 x 185.6, 4 x 177.5
cw, ch = (WX1 - WX0) / 5, (WY1 - WY0) / 4
cx = [[round(WX0 + i * cw, 1), round(WX0 + (i + 1) * cw, 1)] for i in range(5)]
cy = [[round(WY0 + i * ch, 1), round(WY0 + (i + 1) * ch, 1)] for i in range(4)]
# Aiko's frame source 1152x864, window [128,100,1023,784] fitted onto the reel window
sx, sy = (WX1 - WX0) / 895, (WY1 - WY0) / 684
RF = [round(WX0 - 128 * sx, 1), round(WY0 - 100 * sy, 1)]; RF += [round(RF[0] + 1152 * sx, 1), round(RF[1] + 864 * sy, 1)]
HW, HH = meta['hamster']
hamL = [-30, 440, -30 + round(500 * HW / HH), 940]
hamP = [60, 250, 60 + round(560 * HW / HH), 810]
m = re.search(r'const LAYOUT = (\[.*?\])\[0\] \|\| null;', s, flags=re.S)
L = json.loads(m.group(1))[0]
L['cells'] = {'x': cx, 'y': cy, 'cx': [round((a + b) / 2, 1) for a, b in cx], 'cy': [round((a + b) / 2, 1) for a, b in cy]}
L['reel2'] = {'x': cx[2], 'window': [WY0, WY1]}
L['reelFrame'] = RF
L['symScale'] = 0.62
L['sprites'] = {}
L['logo'] = [0, 0, 760, 301]
L['croc'] = {'box': hamL}
V = L['views']
V['landscape']['croc'] = {'box': hamL, 'front': True}
V['landscape']['logo'] = [770, -14, 0.5]
V['portrait']['croc'] = {'box': hamP, 'front': False}
V['portrait']['logo'] = [369, 92, 0.45]
s = s[:m.start(1)] + json.dumps([L], separators=(',', ':')) + s[m.end(1):]

# ---------------------------------------------------------------- SKIN data
rep("  title: 'LEVEE JAW',", "  title: \"REAPER'S HAMSTER WHEEL\",")
rep_re(r"  names: \{ J: 'J'.*?CROWN: 'Brass Maldo SCATTER' \},",
  "  names: { J: 'J', Q: 'Q', K: 'K', A: 'A', KEY: 'Grave Cross', STUD: 'Poison Potion', BANDANA: 'Spellbook',\n"
  "    CASH: '(unused)', RING: 'Wisp Lantern', BLADE: 'Croc Skull', BOTTLE: 'Swamp Scythe', W: 'Grim Hamster WILD',\n"
  "    XW: '(unused)', CROWN: 'Soul Bubble SCATTER', COIN: 'Skull Coin' },")
rep_re(r"  short: \{ KEY: 'GLOVE'.*?XW: 'EXPANDING WILD' \},",
  "  short: { KEY: 'CROSS', STUD: 'POTION', BANDANA: 'SPELLBOOK', CASH: '-', RING: 'LANTERN', BLADE: 'CROC SKULL',\n"
  "    BOTTLE: 'SCYTHE', W: 'WILD', XW: '-', COIN: 'SKULL COIN' },")
rep("scatterCaps: 'BRASS MALDOS', scatter: 'Brass Maldo', scatters: 'Brass Maldos', wild: 'Levee Toll Coin wild',\n    wilds: 'Levee Toll Coin wilds',",
    "scatterCaps: 'SCATTERS', scatter: 'Scatter', scatters: 'Scatters', wild: 'Grim Hamster wild',\n    wilds: 'Grim Hamster wilds',")
rep("BOTTLE: ['CASH', '#9ac080'], W: ['COIN', '#ffd15a'], XW: ['XW', '#ff5a5a'], CROWN: ['MALDO', '#d9a648'] },",
    "BOTTLE: ['SCYTHE', '#9ac080'], W: ['WILD', '#9cff5a'], XW: ['XW', '#ff5a5a'], CROWN: ['SCATTER', '#9cff5a'], COIN: ['x', '#ffd15a'] },")
fs = lambda k: B[k]
rep("      L: { frame: [278, 106, 1402, 773], congrats: [648, 268, 634, 441], count: [867, 473, 189, 144], start: [749, 746, 426, 156] },",
    f"      L: {{ frame: {fs('fs-frame-l')}, congrats: {fs('fs-congrats-l')}, count: {fs('fs-count-l')}, start: [1500, 900, 340, 125] }},")
rep("      P: { frame: [169.6, 400.4, 741.4, 1063.5], congrats: [280.3, 670.9, 521.7, 363.9], count: [460.2, 839.8, 156, 119.3], start: [362.9, 1065, 351.6, 128.4] },",
    f"      P: {{ frame: {fs('fs-frame-p')}, congrats: {fs('fs-congrats-p')}, count: {fs('fs-count-p')}, start: [362.9, 1640, 351.6, 128.4] }},")
rep("      L: { amount: [380, 466, 1160, 158], title: [548, 626, 834, 92] },\n      P: { amount: [222, 834, 636, 130], title: [200, 966, 680, 76] },",
    f"      L: {{ amount: [675, 912, 599, 84], title: {fs('tw-title-l')}, frame: {fs('tw-frame-l')} }},\n"
    f"      P: {{ amount: [268, 1340, 572, 80], title: {fs('tw-title-p')}, frame: {fs('tw-frame-p')} }},")
rep("      big: 15, mega: 50,\n      L: { big: [556.5, 145, 807, 655], mega: [579.5, 54, 761, 746], counter: [210, 812, 1500, 130] },\n      P: { big: [96.2, 499.5, 887.7, 720.5], mega: [101.7, 360.3, 876.6, 859.7], counter: [30, 1224, 1020, 120] },",
    "      big: 15, mega: 50, epic: 100,\n      L: { big: [0, 0, 1920, 1072], mega: [0, 0, 1920, 1072], counter: [675, 912, 599, 84] },\n      P: { big: [0, 0, 1080, 1920], mega: [0, 0, 1080, 1920], counter: [268, 1340, 572, 80] },")
rep("frameBox: [277.1, 53.9, 1641.1, 973.1], fade: 500 },", f"frameBox: {RF}, fade: 500 }},")
rep("  qa: { x: 1300, y: 150 },", "  qa: { x: 1300, y: 150 },\n  // RHW: the wheel of doom (PLACEHOLDER art: static body, the page lights one notch per scatter)\n  wheel: { notches: 8 },")
# asset map: drop LEVEE JAW-only art, add RHW pieces (build.py maps key -> assets/<name> or its .webp twin)
rep("  'xw-expanded.png': \"/*__ASSET:xw-expanded.png__*/\", // Expanding Wild, full-reel column (artist art 2026-10-16)\n", "")
rep("  'sym-CROWN.png': \"/*__ASSET:sym-CROWN.png__*/\",\n",
    "  'sym-CROWN.png': \"/*__ASSET:sym-CROWN.png__*/\",\n  'sym-COIN.png': \"/*__ASSET:sym-COIN.png__*/\",\n"
    "  'wheel.webp': \"/*__ASSET:wheel.webp__*/\",\n  'wheel-skull.webp': \"/*__ASSET:wheel-skull.webp__*/\",\n" +
    ''.join(f"  'splash-{n}-{v}.webp': \"/*__ASSET:splash-{n}-{v}.webp__*/\",\n" for n in ['tw-frame', 'tw-title', 'bigwin', 'megawin', 'epicwin', 'intro'] for v in 'lp'))
rep("  'splash-bigwin.webp': \"/*__ASSET:splash-bigwin.webp__*/\",\n  'splash-megawin.webp': \"/*__ASSET:splash-megawin.webp__*/\",\n", "")

# ---------------------------------------------------------------- geometry: 4 rows
rep("const P = Math.round((CY[2] - CY[0]) / 2);                                          // strip pitch",
    "const NR = CELLY.length;                                                             // RHW: rows (4)\nconst ROWIDX = Array.from({ length: NR }, (_, k) => k);\nconst P = Math.round((CY[NR - 1] - CY[0]) / (NR - 1));                              // strip pitch")
rep("const CELLY2 = [[R2Y[0], CELLY[0][1]], CELLY[1], [CELLY[2][0], R2Y[1]]];", "const CELLY2 = CELLY;                                  // RHW: reel 2 is a normal reel")
rep(": [x0, CELLY[0][0], x1 - x0, CELLY[2][1] - CELLY[0][0]]));", ": [x0, CELLY[0][0], x1 - x0, CELLY[NR - 1][1] - CELLY[0][0]]));")
rep("""  layStrip(r, [pads[0], col[0], col[1], col[2], pads[1]], [3], (i) => (i >= 1 && i <= 3 ? i - 1 : -1));""",
    """  layStrip(r, [pads[0], ...col.slice(0, NR), pads[1]], [NR], (i) => (i >= 1 && i <= NR ? i - 1 : -1));""")
rep("    const cur = state.grid[r] || [visualSym(), visualSym(), visualSym()];", "    const cur = state.grid[r] || ROWIDX.map(visualSym);")
rep("    const vTop = ((fillN0 + 3) * P + 22 + ov) / tSeg * RUN_SPLIT.slope;", "    const vTop = ((fillN0 + NR) * P + 22 + ov) / tSeg * RUN_SPLIT.slope;")
rep("""    layStrip(r, list, [3, fillN + 6],                 // the landing bottom cell and the departing one
      (i) => (i >= 1 && i <= 3 ? i - 1 : i >= fillN + 4 && i <= fillN + 6 ? i - fillN - 4 : -1));   // row of each cell""",
    """    layStrip(r, list, [NR, fillN + 2 * NR],
      (i) => (i >= 1 && i <= NR ? i - 1 : i >= fillN + NR + 1 && i <= fillN + 2 * NR ? i - fillN - NR - 1 : -1));""")
rep("by - wy + (fillN + 3) * P + 'px' });", "by - wy + (fillN + NR) * P + 'px' });")
rep("    const travel = (fillN + 3) * P;", "    const travel = (fillN + NR) * P;")
rep("  const ks = [0, 1, 2].filter((k) => col[k] === SP.WILD || col[k] === XWID);", "  const ks = ROWIDX.filter((k) => col[k] === SP.WILD || col[k] === XWID);")
rep("  for (let r = 0; r < 5; r++) for (let k = 0; k < 3; k++) { const c = visCell(r, k); if (c) c.classList.remove('dim', 'pop', 'crownhit'); }",
    "  for (let r = 0; r < 5; r++) for (let k = 0; k < NR; k++) { const c = visCell(r, k); if (c) c.classList.remove('dim', 'pop', 'crownhit'); }")
rep("  for (let r = 0; r < 5; r++) for (let k = 0; k < 3; k++) {\n    const key = r + ',' + k, c = visCell(r, k);",
    "  for (let r = 0; r < 5; r++) for (let k = 0; k < NR; k++) {\n    const key = r + ',' + k, c = visCell(r, k);")
rep("  xwEls.forEach((el, r) => el && el.classList.toggle('dim', ![0, 1, 2].some(", "  xwEls.forEach((el, r) => el && el.classList.toggle('dim', !ROWIDX.some(")
rep("  wins.forEach(drawLine);\n", "  // RHW: ways wins: framed cells only, no line paths\n")
rep("    const [r, k] = w.cells[1];\n    t.style.left = CX[r] + 'px'; t.style.top = (CY[k] + 86) + 'px';",
    "    const [r, k] = w.cells[0];\n    t.style.left = CX[r] + 'px'; t.style.top = (CY[k] + 60) + 'px';")
rep("""  return `${w.board === 'L' ? 'LEFT' : 'RIGHT'} ${ROWSHORT[w.line] || 'LINE ' + (w.line + 1)} · 3× ${name} · ${fmt(winC(w.pay))} EUR`;""",
    """  return `${w.count}× ${name} · ${w.ways} WAY${w.ways > 1 ? 'S' : ''}${w.mult > 1 ? ' · x' + w.mult : ''} · ${fmt(winC(w.pay))} EUR`;""")
rep("const g = [0, 1, 2, 3, 4].map(() => [pick(), pick(), pick()]);", "const g = [0, 1, 2, 3, 4].map(() => ROWIDX.map(pick));")
rep("  return [['J', 'KEY', 'Q'], ['Q', 'CASH', 'K'], ['W', 'RING', 'STUD'], ['A', 'BLADE', 'K'], ['K', 'A', 'BANDANA']];",
    "  return [['J', 'KEY', 'Q', 'A'], ['Q', 'RING', 'K', 'J'], ['W', 'RING', 'STUD', 'Q'], ['A', 'BLADE', 'K', 'KEY'], ['K', 'A', 'BANDANA', 'J']];")
rep("    layStrip(r, [visualSym(), col[0], col[1], col[2], ...Array.from({ length: 28 }, visualSym)]);",
    "    layStrip(r, [visualSym(), ...col, ...Array.from({ length: 28 }, visualSym)]);")
rep("  await rollSet(land, spun, { noScatterAntic: st.kind === 'free' });", "  await rollSet(st.land || land, spun, { noScatterAntic: true });   // RHW: scatters feed the wheel, no 2-scatter tease")
rep("      const land = st.grid.map((col) => col.slice());", "      const land = (st.land || st.grid).map((col) => col.slice());")

# ---------------------------------------------------------------- feature intro: no royal clearing (royals become skull coins)
rep_re(r"async function featureIntro\(\) \{.*?\n\}\n/\* debug:",
"""async function featureIntro() {
  prompt('REAP SPINS — THE HAMSTER REAPS THE ROYALS', 'gold');
  const flashed = crocFlash('feature');
  shake('feature');
  fillSet = 'free';
  await flashed;
  await sleep(300);
}
/* debug:""")
rep_re(r"function dbgStep\(st, round, i\) \{.*?\n\}\n",
"""function dbgStep(st, round, i) {
  const pay = st.wins && st.wins.length ? `${st.wins.length} way win(s) ${st.stepWin}×` : 'no win';
  if (st.kind === 'base') dbg(`base: ${pay} · scatters ${(st.scatters || []).length} · wheel ${st.wheelFrom}→${st.wheelTo}/${SP.WHEEL_NOTCHES}` + (st.reap ? ' · REAP SPINS!' : ''));
  else dbg(`reap ${st.index}/${NFS}: skull coins ${st.coins.length}` + (st.coins.length ? ` (x${st.mult})` : '') + ` · ${pay}`);
}
""")

# ---------------------------------------------------------------- RHW layers: wheel, skull coin labels, intro
rep('<canvas id="croc"></canvas><img id="logo" alt="">',
    '<canvas id="croc"></canvas><div id="wheel"><img id="wheelBody" alt=""><img id="wheelSkull" alt=""><div id="wheelDots"></div><div id="wheelTxt"></div></div><img id="logo" alt="">')
rep("  #logo{position:absolute;pointer-events:none}",
"""  #logo{position:absolute;pointer-events:none}
  /* RHW: wheel of doom (left of the reels in landscape, top right in portrait) */
  #wheel{position:absolute;left:28px;top:96px;width:262px;height:317px;pointer-events:none;z-index:3;transition:opacity .4s}
  html.portrait #wheel{left:800px;top:250px;width:240px;height:290px}
  #wheel.fs{opacity:0}
  #wheelBody{position:absolute;inset:0;width:100%;height:100%;transform-origin:49% 40%}
  #wheelSkull{position:absolute;left:39.2%;top:35.6%;width:19%;height:29.2%;transform-origin:50% 20%}
  #wheelSkull.hot{animation:skullhot .5s ease-in-out infinite}
  @keyframes skullhot{0%,100%{filter:brightness(1) drop-shadow(0 0 0 #9cff5a);scale:1}50%{filter:brightness(2) drop-shadow(0 0 26px #9cff5a);scale:1.25}}
  #wheelDots i{position:absolute;width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:#1d2a14;border:3px solid #5f7a3a;box-shadow:0 0 4px #000}
  #wheelDots i.on{background:#b8ff6a;border-color:#eaffc8;box-shadow:0 0 14px 4px #7dff3a}
  #wheelDots i.skull{width:30px;height:30px;margin:-15px 0 0 -15px;background:#2a0f0f;border-color:#ff5a5a}
  #wheelDots i.skull.on{background:#ff6a3a;box-shadow:0 0 20px 6px #ff3a1a}
  #wheelTxt{position:absolute;left:0;right:0;bottom:-34px;text-align:center;font:900 28px/1 SPRoboto,Roboto,Arial,sans-serif;color:#d8ff9a;
    -webkit-text-stroke:5px #102208;paint-order:stroke fill;letter-spacing:.04em}
  .soulfly{position:absolute;width:150px;height:150px;margin:-75px 0 0 -75px;pointer-events:none;z-index:60;filter:drop-shadow(0 0 18px #9cff5a)}
  .soulfly img{width:100%;height:100%}
  /* RHW: skull coin multiplier labels on the reels */
  #coinl{position:absolute;left:0;top:0;width:1920px;height:1072px;pointer-events:none}
  .coinx{position:absolute;transform:translate(-50%,-50%);font:900 54px/1 SPRoboto,Roboto,Arial,sans-serif;color:#fff2a8;
    -webkit-text-stroke:7px #4a2600;paint-order:stroke fill;text-shadow:0 0 18px #ffb020}""")
rep("  <div id=\"fx\"></div>\n", "  <div id=\"fx\"></div>\n  <div id=\"coinl\"></div>\n")
rep("  ['reelframe', 'reels', 'xwl', 'lines', 'fx', 'held'].forEach((id) => g(id) && board.appendChild(g(id)));",
    "  ['reelframe', 'reels', 'xwl', 'lines', 'fx', 'coinl', 'held'].forEach((id) => g(id) && board.appendChild(g(id)));")

RHW_JS = r"""
/* ============================================================== RHW: wheel of doom, skull coins, intro */
const WHEEL_N = SP.WHEEL_NOTCHES || 8;
let wheelPos = 0;
(function () {
  const b = $('wheelBody'), k = $('wheelSkull');
  if (asset('wheel.webp')) setSrc(b, asset('wheel.webp')); if (asset('wheel-skull.webp')) setSrc(k, asset('wheel-skull.webp'));
  const d = $('wheelDots');
  for (let i = 0; i < WHEEL_N; i++) {           // notches round the rim; the last one is the skull
    const a = -Math.PI / 2 + (i + 1) / WHEEL_N * Math.PI * 2, el = document.createElement('i');
    el.style.left = 49 + Math.cos(a) * 36 + '%'; el.style.top = 40 + Math.sin(a) * 30 + '%';
    if (i === WHEEL_N - 1) el.className = 'skull';
    d.appendChild(el);
  }
})();
function wheelShow(n) {
  [...$('wheelDots').children].forEach((el, i) => el.classList.toggle('on', i < n));
  $('wheelTxt').textContent = n >= WHEEL_N ? 'REAP!' : `${n} / ${WHEEL_N}`;
  $('wheelSkull').classList.toggle('hot', n >= WHEEL_N);
}
wheelShow(0);
const stagePt = (el) => { const s = stage.getBoundingClientRect(), k = s.width / stage.offsetWidth || 1, b = el.getBoundingClientRect();
  return [(b.left + b.width / 2 - s.left) / k, (b.top + b.height / 2 - s.top) / k]; };
// each landed scatter flies off the grid into the wheel and pushes it one notch
async function wheelPush(st) {
  const cells = st.scatters || [];
  let n = st.wheelFrom;
  const to = stagePt($('wheelBody'));
  for (const [r, k] of cells) {
    const c = visCell(r, k);
    if (c) c.classList.add('crownhit');
    const from = c ? stagePt(c) : to;
    const f = document.createElement('div'); f.className = 'soulfly';
    const im = document.createElement('img'); if (spriteURL.CROWN) setSrc(im, spriteURL.CROWN); f.appendChild(im);
    Object.assign(f.style, { left: from[0] + 'px', top: from[1] + 'px' });
    stage.appendChild(f);
    sfx.wildLand(false);
    const ms = speedMode === 'turbo' ? 320 : 620;
    if (!CALM_FX()) await f.animate([{ transform: 'scale(1)', opacity: 1 }, { transform: 'scale(1.3)', opacity: 1, offset: 0.2 },
      { transform: `translate(${to[0] - from[0]}px,${to[1] - from[1]}px) scale(.35)`, opacity: 0.6 }],
      { duration: ms, easing: 'cubic-bezier(.5,0,.6,1)', fill: 'forwards' }).finished.catch(() => {});
    f.remove();
    n = Math.min(WHEEL_N, n + 1);
    wheelShow(n);
    $('wheelBody').animate([{ rotate: '0deg' }, { rotate: '-9deg' }, { rotate: '3deg' }, { rotate: '0deg' }], { duration: 420, easing: 'ease-out' });
    shake('scatterLand');
  }
  dbg(`wheel ${st.wheelFrom} -> ${n} / ${WHEEL_N}`);
  if (n >= WHEEL_N) { sfx.crown(); await sleep(900); }
}
// REAP SPINS: royals that landed are reaped into skull coins with a multiplier; the spin's win is x their sum
async function reapCoins(st) {
  const L = $('coinl');
  sfx.royals();
  st.coins.forEach(([r, k, m], i) => {
    const c = visCell(r, k); if (!c) return;
    setTimeout(() => {
      setCell(c, 'COIN', r, false, k); state.grid[r][k] = 'COIN';
      if (!CALM_FX()) c.animate([{ filter: 'brightness(3)', scale: '1.3' }, { filter: 'brightness(1)', scale: '1' }], { duration: 380, easing: 'ease-out' });
      const t = document.createElement('div'); t.className = 'coinx'; t.textContent = 'x' + m;
      t.style.left = CX[r] + 'px'; t.style.top = CY[k] + 46 + 'px'; L.appendChild(t);
    }, CALM_FX() ? 0 : i * 70);
  });
  await sleep(st.coins.length * 70 + 420);
  prompt(`SKULL COINS  ×${st.mult}`, 'gold');
  await sleep(380);
}
// intro splash: the whole screen, tap to play (?nointro skips it)
async function introSplash() {
  if (!asset('splash-intro-l.webp') || /[?&]nointro/.test(location.search)) return;
  spOpen(); spRoot.classList.add('intro');
  const [b, i] = spBox([0, 0, 1920, 1072], [0, 0, 1080, 1920], ''); spImg(i, 'intro', true);
  const tip = document.createElement('div'); tip.style.cssText = 'position:absolute;left:0;right:0;bottom:1.5%;text-align:center;font:900 46px/1 SPRoboto,Roboto,Arial,sans-serif;color:#e6ffb8;-webkit-text-stroke:7px #0d2206;paint-order:stroke fill;letter-spacing:.08em';
  tip.textContent = 'TAP TO PLAY'; i.appendChild(tip);
  spAnim(b, [{ opacity: 0 }, { opacity: 1 }], 500, 0, 'ease-out');
  await spWait(debugAuto ? 300 : 0);
  sfx.click();
  await spClose();
}
"""
rep("/* ================================================================================================ round */", RHW_JS + "\n/* ================================================================================================ round */")
rep("#splash .sp-in{position:absolute;inset:0}", "#splash .sp-in{position:absolute;inset:0}\n  #splash.intro .sp-dim{opacity:1;background:#000}")

# ---------------------------------------------------------------- round flow
rep("  const opts = pendingForce ? { force: pendingForce } : undefined;\n  pendingForce = null;",
    "  const opts = { wheel: wheelPos };\n  if (pendingForce) opts.force = pendingForce;\n  pendingForce = null;")
rep("  round.qaForce = opts ? opts.force : null;", "  round.qaForce = opts.force || null;")
rep("  dbg(`round ${roundNo}` + (opts ? ' (forced: ' + Object.keys(opts.force)", "  dbg(`round ${roundNo}` + (opts.force ? ' (forced: ' + Object.keys(opts.force)")
rep("        prompt('');\n        clearWins();\n      }\n      const spun",
    "        prompt('');\n        clearWins(); $('coinl').textContent = '';\n      }\n      const spun")
rep("      dbgStep(st, round, i);\n      const wins = st.wins || [];",
    "      if (st.kind === 'base' && st.scatters && st.scatters.length) await wheelPush(st);\n"
    "      if (st.kind === 'free' && st.coins && st.coins.length) await reapCoins(st);\n"
    "      dbgStep(st, round, i);\n      const wins = st.wins || [];")
rep("`${wins.length} LINES · WIN ${fmt(winC(st.stepWin))} EUR`", "`${wins.length} WAY WINS · WIN ${fmt(winC(st.stepWin))} EUR`")
rep("        if (st.kind !== 'free') prompt(wins.length === 1", "        prompt(st.kind === 'free' ? `REAP WIN ${fmt(winC(st.stepWin))} EUR` + (st.mult > 1 ? `  (×${st.mult})` : '') : wins.length === 1")
rep("      if (st.crowns && st.crowns.length >= 3) {", "      if (st.reap) {")
rep("        await crownCelebration(st.crowns);", "        await crownCelebration(st.scatters || []);\n        wheelPos = 0; wheelShow(0);")
rep("    if (featureOn) {\n      clearWins();", "    wheelPos = round.wheelEnd; wheelShow(wheelPos);\n    if (featureOn) {\n      clearWins(); $('coinl').textContent = '';")
rep("    fsPanel.classList.remove('on');\n    fsLook(false);", "    fsPanel.classList.remove('on');\n    fsLook(false); $('coinl').textContent = '';")
rep("  fsLookOn = on;\n", "  fsLookOn = on;\n  $('wheel').classList.toggle('fs', on);\n")

# ---------------------------------------------------------------- splashes: RHW art (full screen pieces)
rep("  const [gb] = spBox(grow(F.L.frame, -F.glow), grow(F.P.frame, -F.glow), 'sp-halo');   // inside the frame's edge",
    "  const [gb] = spBox(F.L.frame, F.P.frame, '');   // RHW: the art carries its own glow")
rep("  const [gb] = spBox(grow(F.L.frame, -F.glow), grow(F.P.frame, -F.glow), 'sp-halo');\n  const [fb, fi] = spBox(F.L.frame, F.P.frame, 'sp-breathe'); spImg(fi, 'fs-frame', true);\n  const [cb, ci] = spBox(F.L.congrats, F.P.congrats, 'sp-congrats sp-crop'); spImg(ci, 'fs-congrats', true);",
    "  const [gb] = spBox(T.L.frame, T.P.frame, '');\n  const [fb, fi] = spBox(T.L.frame, T.P.frame, ''); spImg(fi, 'tw-frame', true);\n  const [cb, ci] = spBox(T.L.title, T.P.title, 'sp-congrats'); spImg(ci, 'tw-title', true);")
rep("  const [tb, ti] = spBox(T.L.title, T.P.title, 'sp-text sp-title'); ti.textContent = 'TOTAL WIN';",
    "  const [tb, ti] = spBox(T.L.title, T.P.title, 'sp-text sp-title'); ti.textContent = '';   // RHW: TOTAL WIN is in the art")
rep("  const [rb] = spBox(grow(W.L[tier], W.glow * 1.6), grow(W.P[tier], W.glow * 1.3), 'sp-rays');\n  const [gb] = spBox(grow(W.L[tier], W.glow), grow(W.P[tier], W.glow * 0.8), 'sp-glow');\n  const [bb, bi] = spBox(W.L.big, W.P.big, 'sp-breathe'); spImg(bi, 'bigwin');",
    "  const [rb] = spBox(W.L[tier], W.P[tier], '');\n  const [gb] = spBox(W.L[tier], W.P[tier], '');\n  const [bb, bi] = spBox(W.L.big, W.P.big, ''); spImg(bi, 'bigwin', true);")
rep("  if (mega) { const p = spBox(W.L.mega, W.P.mega, 'sp-breathe'); mb = p[0]; spImg(p[1], 'megawin'); mb.style.visibility = 'hidden'; }",
    "  if (mega) { const p = spBox(W.L.mega, W.P.mega, ''); mb = p[0]; spImg(p[1], x >= W.epic ? 'epicwin' : 'megawin', true); mb.style.visibility = 'hidden'; }")

# ---------------------------------------------------------------- QA hooks: ?force=reap, SP_DEBUG.forceReap()
rep("  forceFeature() { qaMark('forceFeature'); pendingForce = Object.assign(pendingForce || {}, { crowns: true }); return 'next spin forces 3 scatters' + forceClash(); },",
    "  forceFeature() { qaMark('forceFeature'); pendingForce = Object.assign(pendingForce || {}, { crowns: true }); return 'next spin pushes the wheel to the skull (REAP SPINS)'; },\n"
    "  forceReap() { return this.forceFeature(); },\n  get wheel() { return wheelPos; },")
rep("requestAnimationFrame(prewarm);\nhud(); idlePrompt();",
    "requestAnimationFrame(prewarm);\nhud(); idlePrompt();\n"
    "if (/[?&]force=reap/.test(location.search)) SP_DEBUG.forceFeature();   // QA: the first spin triggers REAP SPINS\n"
    "setTimeout(introSplash, 50);")

# ---------------------------------------------------------------- rules panel (short, prototype)
rep_re(r"function renderRules\(\) \{.*?\n\}\n\n/\* =+ QA: simulator \*/",
r"""function renderRules() {
  const r = $('rules'); r.textContent = '';
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const x = el('button', 'x', '×'); x.onclick = closeMenus; r.appendChild(x);
  r.appendChild(el('h2', '', `${SKIN.title} — RULES & PAYTABLE (PROTOTYPE)`));
  r.appendChild(el('div', 'note', 'PROTOTYPE: placeholder maths, nothing is tuned. Built on the LEVEE JAW engine shell.'));
  r.appendChild(el('h3', '', '5 reels × 4 rows · 1,024 ways'));
  r.appendChild(el('div', '', 'Wins pay left to right on adjacent reels, 3+ of a kind; the Grim Hamster WILD substitutes for every pay symbol. Pays below are × total bet for 3 / 4 / 5 of a kind, per way.'));
  const g = el('div', 'pays');
  Object.keys(SP.PAYTABLE).sort((a, b) => SP.PAYTABLE[b][2] - SP.PAYTABLE[a][2]).forEach((s) => {
    const p = el('div', 'pay'); const ic = el('div', 'ic'); ic.appendChild(makeCell(s, 1)); p.appendChild(ic);
    p.appendChild(el('b', '', SP.PAYTABLE[s].join(' / ') + '×')); p.appendChild(el('span', '', LABEL[s] || s)); g.appendChild(p);
  });
  [['CROWN', 'SCATTER', 'pushes the Wheel of Doom one notch'], ['COIN', 'SKULL COIN', 'REAP SPINS only: ×2 / ×3 / ×5']].forEach(([s, b, t]) => {
    const p = el('div', 'pay'); const ic = el('div', 'ic'); ic.appendChild(makeCell(s, 1)); p.appendChild(ic);
    p.appendChild(el('b', '', b)); p.appendChild(el('span', '', t)); g.appendChild(p);
  });
  r.appendChild(g);
  r.appendChild(el('h3', '', 'Wheel of Doom'));
  r.appendChild(el('div', '', `Every Scatter that lands flies off the grid into the wheel and pushes it one notch. When the wheel reaches the skull (${WHEEL_N} notches) REAP SPINS start and the wheel resets. The wheel keeps its position between spins.`));
  r.appendChild(el('h3', '', 'REAP SPINS'));
  r.appendChild(el('div', '', `${NFS} free spins. Every J, Q, K or A that lands is reaped into a Skull Coin with a multiplier (×2, ×3 or ×5). A free spin's way wins are multiplied by the sum of the Skull Coin multipliers on screen. No retrigger. A round pays at most ${SP.CAP}× the bet.`));
  r.appendChild(el('h3', '', 'Controls'));
  r.appendChild(el('div', 'note', 'Spin: big button or Space. Hold for turbo spins. A autoplay · T turbo · B bet menu · I rules · G debug overlay · D simulator. QA: add ?force=reap to the URL (or SP_DEBUG.forceReap() in the console) to trigger REAP SPINS on the next spin; ?nointro skips the intro.'));
}

/* ====================================================================================== QA: simulator */""")
rep_re(r"  setText\('fMax', 'CHANCE OF MAX WIN PER LINE:[^\n]*", "  setText('fMax', 'WAYS: 1024  PROTOTYPE');")
rep("    const x = SP.playRound(r);\n", "    const x = SP.playRound(r, { wheel: a.wheel || 0 }); a.wheel = x.wheelEnd;\n")
rep('<h4>LEVEE JAW — IN-BROWSER SIMULATOR</h4>', "<h4>REAPER'S HAMSTER WHEEL — SIMULATOR (prototype maths)</h4>")
rep('LEVEE JAW plays in landscape.', "REAPER'S HAMSTER WHEEL plays in landscape.")
rep("  d.textContent = 'LEVEE JAW DEBUG  (G hides)\\n'", "  d.textContent = 'RHW DEBUG  (G hides)\\n'")
rep("  const line = '[LJ] ' + msg;", "  const line = '[RHW] ' + msg;")
open(OUT, 'w', encoding='utf-8').write(s)
print('ok', len(s))
