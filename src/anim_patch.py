#!/usr/bin/env python3
"""wire Animoto's symbol animations v1 (atlases from tools/pack_anims.py) into src/rhw_template.html (run after patch.py)"""
import json
P = '/workspace/rhw/src/rhw_template.html'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    if s.count(a) != 1: raise SystemExit(f'miss {s.count(a)}: {a[:80]}')
    s = s.replace(a, b)
M = json.load(open('/workspace/rhw/assets/anims.json'))
meta = ',\n'.join(f"  '{k}': {{ u: \"/*__ASSET:{v['f']}__*/\", n: {v['n']}, c: {v['c']}, loop: {str(v['loop']).lower()} }}" for k, v in M.items())
JS = r"""
/* RHW: symbol animations v1 (Animoto PNG fallback -> WebP atlases, 15 fps, re-fitted onto the sym-*.webp canvas) */
const SA_META = {
""" + meta + r"""
};
const SA = (() => {
  const FPS = 15, act = new Map();
  let raf = 0;
  const has = (k) => !CALM_FX() && !!(SA_META[k] && SA_META[k].u);
  function frame(p, i) {
    const m = p.m, rows = Math.ceil(m.n / m.c), c = i % m.c, r = (i / m.c) | 0;
    p.el.style.backgroundPosition = `${(c * 100) / (m.c - 1)}% ${rows > 1 ? (r * 100) / (rows - 1) : 0}%`;
  }
  function tick(t) {
    raf = 0;
    for (const [host, p] of act) {
      if (p.t0 == null) p.t0 = t;
      let i = Math.floor(((t - p.t0) / 1000) * FPS);
      if (p.m.loop) i %= p.m.n;
      else if (i >= p.m.n) { end(host, p); continue; }
      if (i !== p.i) { p.i = i; frame(p, i); }
    }
    if (act.size) raf = requestAnimationFrame(tick);
  }
  function end(host, p) {
    act.delete(host); p.el.remove();
    if (p.o.hideEnd) host.classList.add('sagone'); else host.classList.remove('saon');
    p.o.onEnd && p.o.onEnd();
    if (!p.o.hideEnd && !p.o.noIdle) setTimeout(() => idle(host), 0);
  }
  // t114u: resting symbols loop their idle (random phase so the board breathes unevenly, not in lockstep)
  function idle(host) {
    if (!host || !host.isConnected || act.has(host) || host.classList.contains('reaped') || host.classList.contains('sagone')) return;
    const k = host.dataset.s + ':idle'; if (!has(k)) return;
    play(host, k, { phase: Math.random() * SA_META[k].n * 1000 / 30 });
  }
  function stop(host) {
    const p = act.get(host); if (!p) return;
    act.delete(host); p.el.remove(); host.classList.remove('saon');
  }
  function play(host, key, o = {}) {
    if (!host || !has(key)) return false;
    stop(host);
    const m = SA_META[key], rows = Math.ceil(m.n / m.c);
    const el = document.createElement('div'); el.className = 'sa';
    el.style.backgroundImage = `url("${m.u}")`; el.style.backgroundSize = `${m.c * 100}% ${rows * 100}%`;
    host.appendChild(el); host.classList.add('saon'); host.classList.remove('sagone');
    const p = { el, m, o, i: -1, key, t0: o.phase != null ? performance.now() - o.phase : null }; frame(p, 0); act.set(host, p);
    if (!raf) raf = requestAnimationFrame(tick);
    return true;
  }
  return {
    has, play, stop, idle,
    idleReel(r) { for (let k = 0; k < NR; k++) idle(visCell(r, k)); },
    idleAll() { for (let r = 0; r < 5; r++) for (let k = 0; k < NR; k++) idle(visCell(r, k)); },
    stopAll(keep) { for (const [h, p] of [...act]) if (!keep || !keep(p.key)) stop(h); },
    stopKey(k) { for (const [h, p] of [...act]) if (p.key === k) stop(h); },
    wait: (ms) => new Promise((r) => setTimeout(r, ms)),
  };
})();
"""
CSS = """
  .sa{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;background-repeat:no-repeat}
  .saon>img,.saon>.plaque,.sagone>img,.sagone>.plaque{visibility:hidden}
  .cell.saon.pop{animation:none}
  .cell.reaped>img{opacity:.32;filter:saturate(.35) brightness(1.35) drop-shadow(0 0 18px #9cff5a)}
  .ghostx{position:absolute;left:0;right:0;top:58%;text-align:center;font:900 64px/1 SPRoboto,Roboto,Arial,sans-serif;color:rgba(225,255,180,.5);-webkit-text-stroke:3px rgba(8,28,0,.55);paint-order:stroke fill;pointer-events:none;text-shadow:0 0 18px rgba(124,255,58,.6)}
  .coinx.go{transition:transform .8s cubic-bezier(.4,0,.7,1),opacity .8s;transform:translate(-50%,-220px) scale(1.15);opacity:0}
"""
rep("  .soulfly img{width:100%;height:100%}", "  .soulfly img{width:100%;height:100%}" + CSS)
rep("async function wheelPush(st) {", JS + "async function wheelPush(st) {")
# setCell: a new symbol clears a collected (hidden) coin
rep("  const b = reel === 2 && !!bottom;\n  const rw = row == null ? -1 : row;\n  if (d.dataset.s === s",
    "  const b = reel === 2 && !!bottom;\n  const rw = row == null ? -1 : row;\n  if (d.dataset.s !== s && typeof SA !== 'undefined') { SA.stop(d); d.classList.remove('sagone', 'reaped'); d.querySelectorAll('.ghostx').forEach((e) => e.remove()); }\n  if (d.dataset.s === s")
# wins: each winning cell plays its win one-shot
rep("    c && c.classList.add('pop');\n", "    c && c.classList.add('pop');\n    if (c) SA.play(c, c.dataset.s + ':win');\n")
rep("  // an Expanding Wild column dims like its cells", "  SA.idleAll();\n  // an Expanding Wild column dims like its cells")
rep("async function rollSet(grid, reels, opts) {\n", "async function rollSet(grid, reels, opts) {\n  SA.stopAll();                                // t114u: spinning reels never carry an anim\n")
rep("function clearWins() {\n", "function clearWins() {\n  SA.stopAll((k) => k.startsWith('COIN:'));\n")
# scatter lands on reel stop
rep("      setReel(r, col);\n      sfx.stop(r);\n",
    "      setReel(r, col);\n      sfx.stop(r);\n      for (let k = 0; k < NR; k++) { const c = visCell(r, k); if (c && c.dataset.s === 'CROWN') SA.play(c, 'CROWN:land'); }\n      SA.idleReel(r);\n")
# 2+ scatters: the landed scatters loop their anticipation while a reel is teased
rep("  anticEls[r] = { el, stopSnd: sfx.antic(kind) };\n",
    "  anticEls[r] = { el, stopSnd: sfx.antic(kind) };\n"
    "  if (kind === 'scatter') for (let q = 0; q < r; q++) for (let k = 0; k < NR; k++) { const c = visCell(q, k); if (c && c.dataset.s === 'CROWN') SA.play(c, 'CROWN:anticipation'); }\n")
rep("  const a = anticEls[r]; if (!a) return;\n", "  const a = anticEls[r]; if (!a) return;\n  if (!Object.keys(anticEls).some((q) => +q !== r)) SA.stopKey('CROWN:anticipation');\n")
# flyoff loop while flying, notch_hit at the wheel
rep("    const im = document.createElement('img'); if (spriteURL.CROWN) setSrc(im, spriteURL.CROWN); f.appendChild(im);",
    "    let im = null; if (c) SA.stop(c);\n"
    "    if (SA.has('CROWN:flyoff')) { f.style.width = f.style.height = '200px'; f.style.margin = '-100px 0 0 -100px'; SA.play(f, 'CROWN:flyoff'); }\n"
    "    else { im = document.createElement('img'); if (spriteURL.CROWN) setSrc(im, spriteURL.CROWN); f.appendChild(im); }")
rep("    f.remove();\n    n = Math.min(WHEEL_N, n + 1);",
    "    SA.stop(f); f.remove();\n"
    "    if (SA.has('CROWN:notchhit') || SA.has('CROWN:notch_hit')) { const h = document.createElement('div'); h.className = 'soulfly';\n"
    "      Object.assign(h.style, { left: to[0] + 'px', top: to[1] + 'px', width: '200px', height: '200px', margin: '-100px 0 0 -100px' }); stage.appendChild(h);\n"
    "      SA.play(h, 'CROWN:notch_hit', { hideEnd: true, onEnd: () => h.remove() }); }\n"
    "    n = Math.min(WHEEL_N, n + 1);")
# REAP SPINS: reap_to_coin -> SkullCoin idle (+ code-drawn multiplier) -> collect
rep("async function reapCoins(st) {\n  const L = $('coinl');\n",
    "async function reapCoins(st) {\n  const L = $('coinl');\n  if (SA.has('J:reap_to_coin')) return reapCoinsAnim(st, L);\n")
rep("      await fsTotalSplash(featC);            // COLLECT switches back to the base game look\n",
    "      await fsTotalSplash(featC);            // COLLECT switches back to the base game look\n"
    "      fillSet = 'base'; SA.stopAll(); for (let r = 0; r < 5; r++) setReel(r, Array.from({ length: NR }, () => visualSym())); SA.idleAll();   // t114u: fresh base board\n")
rep("// intro splash: the whole screen", r"""async function reapCoinsAnim(st, L) {
  sfx.royals();
  const tags = [];
  await Promise.all(st.coins.map(([r, k, m], i) => new Promise((res) => {
    const c = visCell(r, k); if (!c) return res();
    setTimeout(() => {
      const toCoin = () => {
        setCell(c, 'COIN', r, false, k); state.grid[r][k] = 'COIN';
        SA.play(c, 'COIN:idle');
        const t = document.createElement('div'); t.className = 'coinx'; t.textContent = 'x' + m;
        t.style.left = CX[r] + 'px'; t.style.top = CY[k] + 46 + 'px'; L.appendChild(t); tags.push(t);
        res();
      };
      if (!SA.play(c, c.dataset.s + ':reap_to_coin', { onEnd: toCoin })) toCoin();
    }, i * 90);
  })));
  prompt(`SKULL COINS  ×${st.mult}`, 'gold');
  await SA.wait(speedMode === 'turbo' ? 250 : 650);
  st.coins.forEach(([r, k, m]) => { const c = visCell(r, k); if (c) SA.play(c, 'COIN:collect', { hideEnd: true, onEnd: () => {
    c.classList.remove('sagone'); c.classList.add('reaped');
    const gx = document.createElement('div'); gx.className = 'ghostx'; gx.textContent = 'x' + m; c.appendChild(gx); } }); });
  tags.forEach((t) => t.classList.add('go'));
  await SA.wait(900);
}
// QA hook (headless screen compare): the splash screens + FS look
window.RHW_QA = { fsSplash, winSplash, fsTotalSplash, fsLook, introSplash, SA, SA_META };
setTimeout(() => SA.idleAll(), 900);   // t114u: the first board idles too
// intro splash: the whole screen""")
open(P, 'w', encoding='utf-8').write(s)
print('anim ok', len(s))
