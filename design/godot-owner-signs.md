# Owner-editable signs (Godot mall)

**Asked for (Steven, Oct 6, 2026):** in owner mode, change the names written on the arcade cabinets in Pocket Change, and the words on Kay-Bee Toys' hanging department boards.

## What it does
- **Signs covered:**
  - the marquee title of every upright video cabinet in Pocket Change (72, ids `pc.video.01` to `pc.video.72`, numbered in build order), of the four basketball games (`pc.hoops.1`–`4`) and of the three claw machines (`pc.crane.1`–`3`);
  - the eight Kay-Bee department boards (`kb.dept.1` to `kb.dept.8`; both faces of a board change together).
- **Who is the owner:** any browser where the mall editor has been unlocked (localStorage `southland-editor` = `1`, set by the main game's secret code), or any visit with `?owner=1` added to the play URL. Being the owner only shows the buttons; publishing still needs a GitHub token with write access.
- **Editing:**
  - The owner sees **Edit signs** and **Publish signs** at the top left.
  - With Edit signs on, tap or click a sign within about 16 m. A text box opens: type the new words, or leave it empty to restore the original.
  - The change shows at once. It is kept in this browser (localStorage `southland-signs-draft`) until it is published.
- **Publishing:**
  - **Publish signs** merges the drafts into `prototypes/godot-mall/play/signs.json` on `main`, using the GitHub contents API.
  - It uses the token the main game's editor Publish keeps in this browser (`southland-gh`). If no token is saved, it asks for one and does not keep it.
  - Everyone sees the change about a minute later, once GitHub Pages updates. No rebuild, export or rebake is needed.

## How it is built
- **Build time:**
  - `tools/build_mall.gd` `sign_add()` records each sign's faces in world space in `gen/signs.json`.
  - The callers are `pocket_change/video.gd` `_sign()` (from `_marquee` and `_housing`) and `kay_bee/store.gd` `dept()`.
- **Run time:**
  - `scripts/signs.gd` (node `Signs` in `main.tscn`) loads the list and the published `play/signs.json`, plus the owner's draft.
  - For each changed sign it lays a word-free copy of the art just in front of the painted sign: `tex/pc/video_marquees_blank.png` (from `paint_video.py` `paint_marquees_blank()`) or `tex/kb/dept_blank.png` (from `paint_store.py` `dept_blank()`). It then draws the words with a Label3D in that marquee's title colours.
  - Signs that are not changed show the original painted art, untouched.
- **Publish code:** `window.mallSigns` in `web/shell.html`.
- **Test:** `tools/qa/signstest.py` (it loads as the owner with a draft, then runs the tap-and-type flow).

## Not covered yet
- The other machines' names: skee-ball, racers, pinball, the ride and air hockey.
- The cabinets' lower-front and bezel art, which repeat the original title.
