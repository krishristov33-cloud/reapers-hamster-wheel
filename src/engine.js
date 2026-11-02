/* =========================================================================
   REAPER'S HAMSTER WHEEL — prototype engine (built on LEVEE JAW's engine API)
   -------------------------------------------------------------------------
   PROTOTYPE MATH: every weight / pay below is a placeholder (no RTP tuning).
   5 reels x 4 rows, 1,024 ways (left to right, adjacent reels, 3+ of a kind).
   WHEEL OF DOOM: every SCATTER (CROWN id) that lands in the base game pushes
   the wheel one notch; when it reaches the skull (WHEEL_NOTCHES) REAP SPINS
   start: 10 free spins. The wheel then resets. The wheel position is passed
   in by the page (opts.wheel) and returned (round.wheelEnd).
   REAP SPINS: J/Q/K/A that land are reaped into SKULL COINS (COIN id) with a
   multiplier (x2/x3/x5). Coins do not pay themselves; a free spin's win is multiplied by
   the sum of the coin multipliers on screen. No retrigger.
   The global name SaltPimp is kept so LEVEE JAW's page code reads it as-is.
   ========================================================================= */
(function (root) {
  'use strict';
  const ROWS = 4, REELS = 5;
  const SYMBOLS = ['J', 'Q', 'K', 'A', 'KEY', 'STUD', 'BANDANA', 'CASH',
                   'RING', 'BLADE', 'BOTTLE', 'W', 'XW', 'CROWN', 'COIN'];
  const LABELS = { J: 'J', Q: 'Q', K: 'K', A: 'A', KEY: 'Grave Cross', STUD: 'Poison Potion', BANDANA: 'Spellbook',
    CASH: '(unused)', RING: 'Wisp Lantern', BLADE: 'Croc Skull', BOTTLE: 'Swamp Scythe', W: 'Grim Hamster WILD',
    XW: '(unused)', CROWN: 'Soul SCATTER', COIN: 'Skull Coin' };
  const WILD = 'W', XW = 'XW', SCATTER = 'CROWN', COIN = 'COIN';
  const ROYALS = ['J', 'Q', 'K', 'A'];
  const isWild = (s) => s === WILD;
  /* pays x TOTAL bet for 3 / 4 / 5 of a kind, per way (PLACEHOLDER) */
  const PAYTABLE = {
    J: [0.02, 0.05, 0.1], Q: [0.02, 0.05, 0.1], K: [0.02, 0.05, 0.15], A: [0.02, 0.05, 0.15],
    KEY: [0.03, 0.1, 0.2], STUD: [0.04, 0.1, 0.25], BANDANA: [0.05, 0.15, 0.3],
    RING: [0.08, 0.2, 0.5], BLADE: [0.1, 0.25, 0.6], BOTTLE: [0.15, 0.4, 1], W: [0.25, 0.75, 2.5],
  };
  const PAYS = {}; for (const s of Object.keys(PAYTABLE)) PAYS[s] = PAYTABLE[s][2];
  const WEIGHTS = { J: 16, Q: 16, K: 15, A: 15, KEY: 10, STUD: 9, BANDANA: 8, CASH: 0, RING: 6, BLADE: 5, BOTTLE: 4,
    W: 2.2, XW: 0, CROWN: 1.3, COIN: 0 };
  const FEATURE_WEIGHTS = Object.assign({}, WEIGHTS, { J: 2.5, Q: 2.5, K: 2.5, A: 2.5, W: 2.6, CROWN: 0 });
  const FREE_SPINS = 10, CAP = 5000, WHEEL_NOTCHES = 8;
  const COIN_MULTS = [2, 2, 2, 3, 3, 5];
  const LINES = [];

  function makeRng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function makeTable(w) { const syms = [], cum = []; let tot = 0; for (const s of SYMBOLS) { const x = w[s] || 0; if (x > 0) { tot += x; syms.push(s); cum.push(tot); } } return { syms, cum, tot }; }
  const BASE_T = makeTable(WEIGHTS), FEAT_T = makeTable(FEATURE_WEIGHTS);
  function draw(rng, t) { const x = rng() * t.tot; for (let i = 0; i < t.cum.length; i++) if (x < t.cum[i]) return t.syms[i]; return t.syms[t.syms.length - 1]; }
  const round2 = (x) => Math.round(x * 100) / 100;
  const cloneGrid = (g) => g.map((c) => c.slice());
  function spinGrid(rng, t) { const g = []; for (let r = 0; r < REELS; r++) { g.push([]); for (let k = 0; k < ROWS; k++) g[r].push(draw(rng, t)); } return g; }

  /* 1,024 ways: for each pay symbol, count adjacent reels from reel 0 that hold it or a wild */
  function scoreGrid(grid, mult) {
    const wins = []; let total = 0;
    for (const sym of Object.keys(PAYTABLE)) {
      let n = 0, ways = 1; const cells = [];
      for (let r = 0; r < REELS; r++) {
        const hit = []; for (let k = 0; k < ROWS; k++) { const s = grid[r][k]; if (s === sym || isWild(s)) hit.push([r, k]); }
        if (!hit.length) break;
        n++; ways *= hit.length; cells.push(...hit);
      }
      if (n < 3) continue;
      if (sym !== WILD && !cells.some(([r, k]) => grid[r][k] === sym)) continue;   // all-wild ways pay as W only
      const pay = round2(PAYTABLE[sym][n - 3] * ways * (mult || 1));
      if (pay <= 0) continue;
      total += pay;
      wins.push({ board: 'L', line: 0, symbol: sym, count: n, ways, mult: mult || 1, cells, pay });
    }
    return { wins, total: round2(total) };
  }
  function crownCells(grid) { const o = []; for (let r = 0; r < REELS; r++) for (let k = 0; k < ROWS; k++) if (grid[r][k] === SCATTER) o.push([r, k]); return o; }
  function validGrid(g) { return Array.isArray(g) && g.length === REELS && g.every((c) => Array.isArray(c) && c.length === ROWS && c.every((s) => SYMBOLS.indexOf(s) >= 0)); }

  function playRound(rng, opts) {
    const force = (opts && opts.force) || {};
    let wheel = Math.max(0, Math.min(WHEEL_NOTCHES - 1, (opts && opts.wheel) | 0));
    const steps = []; let running = 0, capReached = false;
    const push = (st) => { const next = Math.min(CAP, round2(running + st.stepWinRaw)); st.stepWin = round2(next - running);
      if (st.stepWin < st.stepWinRaw) st.capped = true; if (!capReached && next >= CAP) { st.capReached = capReached = true; }
      running = next; st.runningTotal = running; steps.push(st); };
    let grid;
    if (force.grid && validGrid(force.grid)) grid = cloneGrid(force.grid);
    else {
      grid = spinGrid(rng, BASE_T);
      if (force.crowns) {                       // QA: enough scatters to reach the skull this spin (at least 1)
        const need = Math.max(1, WHEEL_NOTCHES - wheel);
        const have = crownCells(grid).length;
        const reels = [0, 1, 2, 3, 4].sort(() => rng() - 0.5);
        for (let i = 0; i < need - have && i < 10; i++) grid[reels[i % 5]][(Math.floor(i / 5) * 2 + Math.floor(rng() * 2)) % ROWS] = SCATTER;
        if (crownCells(grid).length < need) wheel = WHEEL_NOTCHES - crownCells(grid).length;
      }
    }
    const s0 = scoreGrid(grid);
    const sc = crownCells(grid);
    const wheelStart = wheel;
    const wheelHit = wheel + sc.length >= WHEEL_NOTCHES;
    const base = { kind: 'base', grid: cloneGrid(grid), spun: [0, 1, 2, 3, 4], xwLand: [], expanded: [], wins: s0.wins,
      stepWinRaw: s0.total, scatters: sc, wheelFrom: wheelStart, wheelTo: Math.min(WHEEL_NOTCHES, wheel + sc.length) };
    push(base);
    const baseWin = base.stepWin;
    wheel = wheelHit ? 0 : wheel + sc.length;
    let featureRaw = 0;
    if (wheelHit) {
      base.crowns = sc.length >= 3 ? sc : sc.concat([[-1, -1], [-1, -1], [-1, -1]]).slice(0, Math.max(3, sc.length));
      base.reap = true;
      for (let i = 1; i <= FREE_SPINS; i++) {
        const land = spinGrid(rng, FEAT_T);
        const coins = [], g = cloneGrid(land);
        for (let r = 0; r < REELS; r++) for (let k = 0; k < ROWS; k++) if (ROYALS.indexOf(land[r][k]) >= 0) {
          const m = COIN_MULTS[Math.floor(rng() * COIN_MULTS.length)]; coins.push([r, k, m]); g[r][k] = COIN;
        }
        const mult = coins.length ? coins.reduce((a, c) => a + c[2], 0) : 1;
        const s = scoreGrid(g, mult);
        const st = { kind: 'free', index: i, grid: g, land, coins, mult, spun: [0, 1, 2, 3, 4], xwLand: [], expanded: [],
          wins: s.wins, stepWinRaw: s.total };
        push(st); st.paid = st.stepWin; featureRaw = round2(featureRaw + s.total);
        if (capReached) break;
      }
    }
    const raw = round2(s0.total + featureRaw), totalWin = Math.min(CAP, raw);
    return { steps, baseWin, featureWin: round2(totalWin - baseWin), featureRaw, rawWin: raw, totalWin, capped: raw > CAP,
      capReached, copied: false, featureTriggered: wheelHit, wheelStart, wheelEnd: wheel };
  }
  const BETS_CENTS = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000];
  function winCents(x, betCents) { return Math.round(Math.round(x * 100) * betCents / 100); }
  root.SaltPimp = { SYMBOLS, LABELS, PAYS, PAYTABLE, LINES, CAP, WILD, XW, SCATTER, COIN, ROYALS, ROWS, REELS,
    WEIGHTS, FEATURE_WEIGHTS, FREE_SPINS, WHEEL_NOTCHES, COIN_MULTS, RTP_LABEL: 'PROTOTYPE (untuned)',
    BETS_CENTS, winCents, makeRng, makeRngWide: makeRng, playRound, scoreGrid, crownCells, PROTOTYPE: true };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.SaltPimp;
})(typeof globalThis !== 'undefined' ? globalThis : this);
