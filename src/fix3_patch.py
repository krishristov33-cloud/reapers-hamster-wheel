#!/usr/bin/env python3
"""t111u/t112u fixes for src/rhw_template.html, run after anim_patch.py: Reel_Back layer over the hamster, code-driven hamster
   idle (15 s) cycling Animoto's 8 clips once each, symbol animations at the source 30 fps on real elapsed time."""
import json, re
P = '/workspace/rhw/src/rhw_template.html'
s = open(P, encoding='utf-8').read()
def rep(a, b):
    global s
    if s.count(a) != 1: raise SystemExit(f'miss {s.count(a)}: {a[:90]}')
    s = s.replace(a, b)
H = json.load(open('/workspace/rhw/assets/ham.json'))
# 1) Reel_Back between the hamster and the symbols
rep('  <div id="reels"></div>\n', '  <img id="reelBackOv" alt="">\n  <div id="reels"></div>\n')
rep("  #frameOv{position:absolute;", "  #reelBackOv{position:absolute;left:0;top:0;width:1920px;height:1072px;pointer-events:none} html.portrait #reelBackOv{width:1080px;height:1920px}\n  #frameOv{position:absolute;")
rep("  'frame-ov-l.webp': \"/*__ASSET:frame-ov-l.webp__*/\",",
    "  'frame-ov-l.webp': \"/*__ASSET:frame-ov-l.webp__*/\",\n  'reelback-l.webp': \"/*__ASSET:reelback-l.webp__*/\",\n  'reelback-p.webp': \"/*__ASSET:reelback-p.webp__*/\",\n"
    "  'ham-still.webp': \"/*__ASSET:ham-still.webp__*/\",\n" + ''.join(f"  '{c['f']}': \"/*__ASSET:{c['f']}__*/\",\n" for c in H['clips']).rstrip('\n'))
rep("if (fo && u) setSrc(fo, u); }", "if (fo && u) setSrc(fo, u);\n      const rb = g('reelBackOv'), ru = asset(name === 'portrait' ? 'reelback-p.webp' : 'reelback-l.webp'); if (rb && ru) setSrc(rb, ru); }")
rep("stg.insertBefore(cv, v.croc.front ? top : board);", "stg.insertBefore(cv, v.croc.front ? top : (g('reelBackOv') || board));")
# 2) hamster: code idle + clip cycle (replaces LEVEE JAW's crocPlayer)
U = H['world']; meta = {'W': U[2] - U[0], 'H': U[3] - U[1], 'k': 0.5, 'still': H['still'],
                        'clips': [{'f': c['f'], 'name': c['name'], 'box': c['box'], 'fps': c['fps'], 'n': c['n']} for c in H['clips']]}
HAM = r"""(function hamPlayer() {
  /* RHW t111u: the default idle is CODE-driven (breathing / squash / bob / tilt on the still, anchored at the feet); every 15 s
     one of Animoto's clips plays once (in order, cycling), then back to the code idle. All clips share the still's canvas,
     so the feet and the visible body stay put when they switch (t112u: the view boxes centre the visible body). */
  const cv = document.getElementById('croc'); if (!cv) return;
  const M = """ + json.dumps(meta) + r""";
  const K = M.k, IDLE_MS = 15000, g2 = cv.getContext('2d');
  cv.width = Math.round(M.W * K); cv.height = Math.round(M.H * K);
  const st = new Image(); let stOK = false; st.onload = () => { stOK = true; }; const su = asset('ham-still.webp'); if (su) setSrc(st, su);
  const calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const [fx, fy] = M.still.feet, [sx0, sy0, sw, sh] = M.still.box;
  let mode = 'idle', tIdle = performance.now(), ci = 0, clip = null, next = null, loading = false;
  function decode(i) {
    const c = M.clips[i], u = asset(c.f); if (!u || !window.createImageBitmap) return Promise.resolve(null);
    const b = atob(u.slice(u.indexOf(',') + 1)), B = new Uint8Array(b.length);
    for (let j = 0; j < b.length; j++) B[j] = b.charCodeAt(j);
    const dv = new DataView(B.buffer), n = dv.getUint32(12, true), fps = dv.getUint32(8, true) / 1000;
    let o = 16 + 4 * n; const parts = [];
    for (let j = 0; j < n; j++) { const l = dv.getUint32(16 + 4 * j, true); parts.push(B.subarray(o, o + l)); o += l; }
    return Promise.all(parts.map((p) => createImageBitmap(new Blob([p], { type: 'image/webp' })))).then((bm) => ({ c, bm, fps }));
  }
  function prefetch() {
    if (loading || next) return; loading = true;
    const i = ci; decode(i).then((r) => { next = r; loading = false; }).catch(() => { loading = false; ci = (ci + 1) % M.clips.length; });
  }
  function idle(now) {
    if (!stOK) return;
    const t = (now - tIdle) / 1000, b = Math.sin((2 * Math.PI * t) / 3.4);
    const sy = 1 + 0.014 * b, sx = 1 - 0.006 * b;                       // breathing + slight squash (feet anchored)
    const bob = -2.2 * (0.5 + 0.5 * Math.sin((2 * Math.PI * t) / 3.4 - 0.7));
    const tilt = (0.6 * Math.PI / 180) * Math.sin((2 * Math.PI * t) / 6.1);
    g2.save(); g2.scale(K, K); g2.translate(fx, fy + bob); g2.rotate(tilt); g2.scale(sx, sy); g2.translate(-fx, -fy);
    g2.drawImage(st, sx0, sy0, sw, sh); g2.restore();
  }
  function frame(now) {
    requestAnimationFrame(frame);
    g2.clearRect(0, 0, cv.width, cv.height);
    if (mode === 'clip') {
      const i = Math.floor(((now - clip.t0) / 1000) * clip.fps);
      if (i < clip.bm.length) { const [x, y, w, h] = clip.c.box; g2.drawImage(clip.bm[i], x * K, y * K, w * K, h * K); return; }
      clip.bm.forEach((b) => b.close && b.close()); clip = null; mode = 'idle'; tIdle = now; ci = (ci + 1) % M.clips.length;
      window.RHW_HAM = { last: M.clips[(ci + M.clips.length - 1) % M.clips.length].name, next: M.clips[ci].name };
    }
    idle(now);
    if (calm) return;
    if (now - tIdle > IDLE_MS - 6000) prefetch();
    if (now - tIdle >= IDLE_MS && next) { clip = next; next = null; clip.t0 = now; mode = 'clip'; }
  }
  requestAnimationFrame(frame);
  window.RHW_HAM_SKIP = () => { tIdle -= IDLE_MS; };                    // QA: jump to the next clip
})();"""
m = re.search(r'\(function crocPlayer\(\) \{.*?\n\}\)\(\);', s, flags=re.S)
assert m and m.group(0).count('(function') == 1, 'crocPlayer block'
s = s[:m.start()] + HAM + s[m.end():]
# 3) symbol animations at the source 30 fps, real elapsed time
rep("  const FPS = 15, act = new Map();", "  const FPS = 30, act = new Map();   // t111u: the source rate (no decimation); frame = elapsed ms * 30 / 1000")
rep("      if (p.t0 == null) p.t0 = t;", "      if (p.t0 == null) p.t0 = performance.now();\n      t = performance.now();")
rep("  function tick(t) {", "  function tick(t) {   // rAF time is only the wake-up; the frame comes from performance.now() - t0")
open(P, 'w', encoding='utf-8').write(s); print('fix3 ok')
