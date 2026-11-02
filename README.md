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
