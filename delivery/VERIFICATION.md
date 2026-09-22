# 2026-09-22 — Keyboard orientation / wrist correction (current)

- Rotated the entire physical keyboard plane 180 degrees before perspective projection. This rotates keycaps, legends, numeric pad and every input landing/highlight together. Space is closest to the character; numpad is on character-right / viewer-left.
- Removed the previous up-to-58-degree palm rotation. Every palm now keeps its approved downward finger direction, with a vertically aligned wrist. A curved sleeve joins the fixed shoulder to the wrist; the cropped rectangular sleeve fringe was removed using the palm contour.
- Updated direction tests to the actual character perspective rather than the former spectator perspective; tests were seen failing before the fix. Check `tools/test_input_positions.py` for row order, left/right order, numpad and wrist-axis assertions.
- Actual Windows Raw Input test passed 13 physical keys / sided modifiers, release and mouse extremes: `validation/input-position-native/20260922-122405/summary.json`. Native output inspected in `native-key-contact.png`.
- Final ZIP key-A and release checks passed (`20260922-122626`, `20260922-122752`); blink and pointer reversal passed (`20260922-122756`, `20260922-122800`). An earlier import attempt failed to activate the adapter; sequential retry passed. That failed attempt is retained and is not counted as a pass.
- Updated the installed Ruotengwu with the native-import-tested package; verified MOC3 hash and a post-install key-A render. BongoCat gracefully restarted. Position and scale, settings file preserved; model is shown on restart. Evidence: `validation/orientation-v3-install/installation.json`.
- Prior version backed up under `revisions/before-keyboard-orientation-fix/`. No application code changed. Existing stock single-key overlay/merged Enter limitations remain.

---

# Input-position correction — 2026-09-22 (current revision)

The prior v1 report below is historical. Its generic key press/release test did NOT prove that different physical keys land at different positions. That omission was reported by the user and is corrected in this revision.

## Current changes and evidence
- Mouse mesh displacement: ±90 source pixels X and ±36 Y, versus ±15/±9 previously (6× horizontal, 4× vertical). Actual native palm travel measured about 41.7px horizontally and 15.5px vertically in the test capture.
- Full QWERTY, function row, navigation and numpad layout replaces generic unlabelled key blocks. Per-key overlays move the connected keyboard arm to that key and highlight it; the resting Live2D keyboard arm hides during a press. Face, blink, breath and mouse remain true Live2D deformation.
- Native import can misassign sided modifiers if multiple aliases share a virtual-key code. Only canonical physical key filenames are shipped; left/right Shift, Ctrl and Alt order is preserved by importer.
- Actual keyboard events were delivered to an owned blank sink and received by installed BongoCat 1.11.0 via Raw Input. A, D, J, P, Z, Space, Enter, UpArrow, numpad 1 and both Shift/Ctrl sides produced distinct measured hand positions. Key releases returned the resting hand. This is not a parameter-only simulation.
- Authoritative run: `validation/input-position-native/20260922-005613/summary.json` plus its frame images and runtime log. `tools/test_actual_keys.py` refuses to inject keys when focus is not its owned sink, releases held inputs and restores pointer/focus on exit.
- Asset regression: `tools/test_input_positions.py` originally failed because all keys had identical transparent textures; it now passes distinct textures, physical row ordering, sided modifiers and range specification. Existing source/layers/model structural gates also pass.
- Final ZIP key A, Tab and release native audits: `20260922-010235`, `20260922-010239`, `20260922-010243`. Native pointer reversal and blink-pose checks: `20260922-010248`, `20260922-010252`.
- Updated installed `Ruotengwu` via a staged copy of the native-import-tested package. Old installed package, model ZIP, source and scripts are under `revisions/before-input-position-fix/`. BongoCat was gracefully restarted; final native key audit passed, MOC3 hash matched, settings and window size/position were preserved. Evidence: `validation/input-v2-install/installation.json`.

## Native 1.11.0 limitations (not claimed fixed)
- One keyboard hand shows the latest pressed key. Releasing it returns to rest even if an earlier key is still held; simultaneous multi-finger/chord restoration is not implemented by the stock overlay runtime.
- Main Enter and numpad Enter both arrive as `Return`; both Windows keys arrive as `Meta`. A skin cannot distinguish them. F13–F24 use function-row alternatives with an explicit label.
- The full pose set is standard ANSI/QWERTY rather than an inferred scan of a user's custom keyboard layout.

---

# Historical v1 evidence (not the current input implementation)

# Ruotengwu verification — 2026-09-21

## Scope and source

Approved source: `source/approved.png`, lossless copy of the user's approved v3 design. The model is genuinely exported MOC3, with 19 final source layers, 22 Drawables, 23 parameters and one 4096px atlas. Head/eye/blink/breath/hair and input meshes are independent; the desktop is rooted separately from moving head/body transforms.

## Authoritative runtime

Executable: `C:\Users\wjx\AppData\Local\Programs\BongoCat\BongoCat.exe`, version **1.11.0**. Native audit reports **renderer=cubism-native**. Test instances use their own `BONGO_CAT_TEST_INSTANCE_ID` and `--storage-root`; this is the installed software, not a replacement web renderer.

## Passed checks

1. Source preservation, valid alpha/size, white inference composite, independent input layers, semantic names in saved PSD, MOC3 signature, all manifest references, required parameter declarations, editable CMO3, required keyboard aliases: `tools/check_assets.py source|inputs|layers|model`.
2. Pinned PSD2Live export checks neutral geometry and MOC3/CMO3 readback. Two small caveats are listed below.
3. **10 native scenarios passed** in `validation/native/20260921-233720/summary.json`: idle, key-left, key-tab-left, key-left-release, mouse-left, mouse-right, mouse-move, mouse-move-mirror, mouse-reverse, mouse-hand-screen. Press/release report correct parameter values.
4. Pixel comparisons prove nontrivial *visible* changes, not just parameter names: keyboard press/release changed 491 pixels only in keyboard-hand bounds; mouse clicks changed 481 pixels in mouse-hand bounds; mouse movement changed 13,470 pixels. See `validation/visual-checks.json`.
5. Ten actual native pose captures inspected: neutral, eyes closed, half blink, left/right, up/down, tilt ±12, mouth. Face, glasses and hair remain attached; no gross holes or duplicated limbs visible. `validation/native-poses-contact.png`.
6. Automatic idle blink observed in unmodified final-runtime capture: frame 020 closed, adjacent 019/021 open. Breathing/head/hair motion also visible. `validation/idle-eyes-all.png`. Preview GIF uses real captures from the final model, not simulated image motion.
7. Final ZIP import separately passed key-left, key-left-release, mouse-left and mouse-reverse, in runs `20260921-234417`, `20260921-234421`, `20260921-234426`, `20260921-234430`. Imported MOC3 SHA-256 equals final exported MOC3. Import-generated model ID is `Ruotengwu-Live2D`.
8. Installed through BongoCat's importer into the real user model directory as **Ruotengwu**. Installed native key-left audit passed and MOC3 hash matched. Existing settings/session hashes were unchanged; original main BongoCat process was not terminated. `validation/installed/`.

## Corrections made from evidence

- New PSD API ignored `layer_name`; switched to the actual `name` parameter and added a semantic-name regression check.
- Generic inpainting smeared black sleeve/mouse pixels into hidden grey desktop. Replaced it with a source-specific grey surface and adjacent-keycap reconstruction; visual/region check added.
- Default exporter horizontal range ±45 caused native pointer reversal to exceed BongoCat's smooth-step bound. Set desktop range to ±30 and tilt ±12; reversal now passes. Full portrait yaw keys remain in editable source.
- Native installed Cubism JSON loader rejected a compact one-line diagnostic motion fixture. Pretty-printed UTF-8 fixtures with final newline load correctly. Shipping files already use the valid pretty format.
- ZIP import uses archive stem as model ID; verifier now checks the correct expected ID AND hashes the imported MOC3.

## Limitations / not represented as passed

- `mouse-screen` built-in audit fails on **both this model and the shipped standard cat**. Its assertions demand near-zero head motion at screen center despite the runtime's automatic breathing/idle. Preserved independent baseline evidence in `validation/baseline-screen/`; it is not included among the ten passing scenarios. Pointer-direction, reversal smoothness and hand-extreme audits passed independently.
- One early isolated test process exited with Windows access violation during shutdown, after its key-release audit had passed, while real desktop interaction was hitting the test window. Later click-through isolated tests, repeated key-release, final ZIP imports and real installation all exited normally. No claim that this proves every software teardown race absent.
- A closed-mouth mesh bounds readback differs by under 1 source pixel horizontally. Visual inspection found no visible issue at desktop size.
- CMO3 editable texture layers are reconstructed from the atlas by PSD2Live; original Photoshop linked-edit association is not retained. Full PSD and PNG layers are supplied.
- This is the approved standard keyboard+mouse desk model, not a gamepad layout or a webcam/audio tracking setup.
- Camera capture/multi-monitor hardware configurations other than this machine were not tested. Windows computer-use capture failed with `SetIsBorderRequired ... 0x80004002`; all presented model captures instead come from BongoCat's actual OpenGL framebuffer.
- Automated layer inference has been manually repaired and visually checked at the stated poses, not asserted to be a commercial all-angle hand-painted rig.

## No unrelated edits

No BongoCat application source files were changed. Work is confined to the new artifact tree and a plan file. Old art, old Live2D project and existing user models are preserved.
