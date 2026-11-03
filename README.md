# REAPER'S HAMSTER WHEEL — fast playable prototype

Live: https://krishristov33-cloud.github.io/reapers-hamster-wheel/

This is a single self-contained `index.html` (~20 MB, every asset is inlined). It's a **fork of LEVEE JAW** (krishristov33-cloud/levee-jaw v11) and reuses its reels, spin loop, UI, autoplay, turbo, splash system and free-spins flow. The art is Aiko's RHW pass 1; the hamster idle is Animoto's game_pack_v1 lj_dropin. **Placeholder maths: nothing is tuned.**

## What works
- **5 reels × 4 rows, 1,024 ways** (left to right, 3+ adjacent reels). The WILD substitutes.
- **Wheel of Doom** (left of the reels; top right in portrait): every Scatter that lands flies off the grid into the wheel and lights one notch. 8 notches: the 8th is the skull, and reaching it starts REAP SPINS. The wheel keeps its position between spins and resets after the feature.
- **REAP SPINS**: 10 free spins on the purple FS background. Every J/Q/K/A that lands turns into a **Skull Coin with a multiplier** (x2/x3/x5). The spin's way wins are multiplied by the sum of the coins on screen. There's no retrigger.
- Screens: intro splash (tap to play), REAP SPINS trigger (title + "10 FREE SPINS" + START), REAP SPINS total win (counter on the plaque), and BIG (15x) / MEGA (50x) / EPIC (100x) win.
- The hamster idle loop (with the smug cheer as the rare second idle) plays on the croc canvas.

## Faked or missing
- The maths is placeholder: RTP is untuned and well over 100%, and pays and weights are made up.
- The wheel is static art with glowing notches and a wobble. It doesn't actually rotate or land, and Animoto's wheel clips (wheel/crc1) aren't wired in yet.
- There's no hamster celebration clip on trigger (it only flashes). Hamster event emotes aren't wired.
- Skull coins don't pay on their own and aren't wild; they only multiply.
- The UI chrome (buttons, top jackpot bars, BUY BONUS, spin button, START/COLLECT plates) and the music are still LEVEE JAW's. Buy Bonus is decorative.
- Portrait base/FS uses the pass-1 layout and LEVEE JAW's portrait board arrangement.

## QA
- `?force=reap`: the first spin triggers REAP SPINS. In the console, `SP_DEBUG.forceReap()` does it for the next spin.
- `?nointro` skips the intro. G toggles the debug overlay and D opens the simulator.

## Rebuild / swapping in Aiko's pass 2
The source lives on the shared box at `/workspace/rhw/` (`tools/make_assets.py`, `tools/patch.py`, `tools/build.py`, `src/engine.js`).
1. `python3 tools/make_assets.py` rebuilds every image from Aiko's `work/p1/layouts/RHW_{L,P}_NN_*.json` + `elements/`. All full-screen screens (02 trigger, 03 total win, 04/05/06 big/mega/epic, 01 intro) are composited per view straight from those layouts, so a pass-2 layout or element with the same name gets picked up automatically. The portrait backgrounds come from `RHW_P_00` / `RHW_P_07`. If pass 2 lands in a new folder (e.g. `work/p2/layouts`), change `LAY` at the top of the script.
2. `python3 tools/patch.py && python3 tools/build.py` writes `dist/index.html`. The reel window / frame fit and the hamster boxes are at the top of the layout section in `patch.py` (WX0..WY1, hamL, hamP). The splash text boxes (counter on the plaque) are `L/P amount` and `counter` there too.


## Update: UI2 + Aiko pass 2
- I removed the Levee Jaw UI: the jackpot bars, the tournament button, Buy Bonus, the UI sheet, the spin sprites, the START/COLLECT plates and the footer bar art.
- I replaced it with a minimal CSS HUD in the toxic style: BALANCE/BET/WIN panels, a glowing SPIN button that turns into a STOP square, AUTO/TURBO/BET/menu/info/music/FX buttons, and START/COLLECT pills.
- LAY now points to work/p2/layouts. In portrait the reels are lower and wider, and the hamster, wheel and HUD have been moved to fit. Win amounts have a glow halo because the boards are gone. The Potion sprite is now Sym_Potion_v2.


## Update: PSD fit, symbol animations, music (t107u–t109u)
- **Layout from Aiko's PSDs.** `work/p2/layouts/*.json` holds the PSD layer records. `tools/psd_fit.py` builds four pieces from them:
  - the backgrounds (BG + Reel_Back + lantern glow, plus the FS purple grade)
  - a full-stage frame overlay above the reels (dividers + frame + lanterns)
  - the symbols at their native PSD size
  - `assets/psd_fit.json`, which holds the reel grid, logo, wheel and hamster boxes
  `tools/psd_patch.py` applies these numbers: the reel grid is Reel_Back in landscape, and portrait uses board scale 1.075. In landscape the wheel sits right of the reels and the SPIN cluster is top right.
- **Symbol animations v1 (Animoto).** `tools/pack_anims.py` packs the PNG sequences into WebP atlases (200 px, 15 fps), re-fitted onto the sprite canvas. `tools/anim_patch.py` wires them:
  - win one-shots on winning cells
  - SCATTER: land, an anticipation loop, a flyoff loop while flying to the wheel, and notch_hit at the wheel
  - REAP SPINS: reap_to_coin, then the SkullCoin idle loop with the xN label drawn by code, then collect
- **Music.** Kris's `music/reapers_hamster_wheel.mp3` is re-encoded with ffmpeg (trim silence, 96 kbps mono) into `assets/theme.mp3`. It is the looping BGM, starts after the first tap, and the HUD ♪ toggle controls it.
- **Rebuild order:** `make_assets.py` -> `psd_fit.py` -> `pack_anims.py` -> `patch.py` -> `psd_patch.py` -> `anim_patch.py` -> `build.py`
- **QA hook:** `window.RHW_QA` (fsSplash / winSplash / fsTotalSplash / fsLook). `qa_cmp.py` uses it for the screen-vs-PSD contact sheet.

## Update: fix pass 3 (t111u/t112u)
- **Portrait:** the reels moved up 180 px together with the frame and Reel_Back. The hamster is 15% smaller, sits behind Reel_Back, and is centred on its visible body (alpha bounding box). The play controls are a centred cluster under the reels.
- **Landscape:** the play cluster is at the bottom right. The money panels moved to the bottom left, off the frame's beam and lanterns. The Levee Jaw footer line is gone.
- **Hamster:** the default idle is code-driven (breathing, squash, bob and a slight tilt on the still, anchored at the feet). Every 15 s it plays one of Animoto's clips 02-09 once, in order. `tools/pack_hamster.py` packs them at 0.5 scale and 24 fps. The lj_dropin idle bin is no longer used.
- **Royals:** J/Q/K/A stills come from Aiko's fixed symbols_split parts (boards). The re-exported animations already include the boards.
- **Symbol animations:** full 30 fps with no decimation (180 px cells). The frame is computed from performance.now() elapsed time.
- **Rebuild order:** make_assets -> psd_fit -> pack_anims -> pack_hamster -> patch -> psd_patch -> anim_patch -> fix3_patch -> build

## Update: fix pass 4 (t114u)
- **Symbol idle loops:** every resting symbol loops its idle (160 px, 30 fps, random phase). Wins, scatter land and reaps hand back to the idle when they finish.
- **Alignment:** every symbol's anims use one exact affine fit from its idle frame 0 to the PSD still. The reel still is now that same frame 0, so there's no pop when an anim starts (checked: ≤1 px at 180 px).
- **REAP SPINS:** a collected coin leaves a faint skull and a ghost "xN" until the next spin. After the total-win splash the base game gets a fresh full board.
- **Portrait HUD:** no BET button; i bottom-left, ≡ bottom-right.
- **Landscape:** reels/frame at 91 %. All buttons and readouts sit in one bottom line; SPIN stays bottom right.
- **Reel_Back:** grown 6 px a side.
