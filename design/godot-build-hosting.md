# Godot mall build: how it is stored and served

> **Since Demo 16 (Oct 7, 2026) the mall ships in two wings:** `w1.*.pck` and `w2.*.pck` instead of
> `index.*.pck`, lightmaps `wing<n>_{night,day}.*` instead of `main_*`, and the stand-in pictures in
> `standin/` on `godot-build`. See `design/godot-wings.md`, which supersedes the file names below.

**Asked for (Steven, Oct 6, 2026):**
- "get rid of all of the waste": the texture formats a device never uses, and the unused 8-bit front paintings;
- "get rid of all of the clones in the repository and just have the one file each time that gets replaced";
- no change for his wide-screen monitor or a later VR port (Meta Quest);
- before-and-after screenshots for anything that lowers resolution. Nothing here does.

## Two game files, one per kind of GPU
- **The files:** `tools/export_web.sh <outdir>` exports the presets "Web Desktop" and "Web Mobile" (`export_presets.cfg`) and writes:
  - `index.desktop.pck`: textures in S3TC and BPTC, for computer GPUs;
  - `index.mobile.pck`: ETC2 and ASTC, for phones, tablets and VR headsets (the Quest browser takes these);
  - the shared `index.html`, `.js` and `.wasm`.
  - The two files differ only in texture formats. Every model, texture and light bake is the same resolution in both.
- **Before:** one `index.pck` carried both sets, and every device downloaded both. That was 65.9 MB at Demo 9b; each file is now 47.8 MB.
- **Both presets leave out** the old 8-bit storefront paintings (`tex/fronts/*`, `fronts.json`; off since `USE_FRONT_ART = false`).
- **Picking the file** (`web/shell.html`, before the engine starts):
  - `?pack=desktop|mobile` wins;
  - then a choice remembered in this browser (localStorage `southland-pack`);
  - then the WebGL2 extensions: S3TC + BPTC → desktop, ETC2 + ASTC → mobile;
  - then the user agent.
  - The choice is in `window.__mallPack`.
- **Safety net** (`scripts/mall_runtime.gd` `_check_pack()`): if the engine reports that this GPU lacks the formats of the file it got, but has the other set, it remembers the other file and reloads once. A sessionStorage flag stops loops.
- **Test:** `tools/qa/packtest.py <build>/index.html <out>` hides one set of extensions to imitate a phone GPU and a computer GPU, plus a wrong remembered guess. All three passed on Oct 6, as did movetest with 0 errors for both files.
- **Wide screens and VR:** texture formats don't depend on screen size or shape. A Quest port would use the mobile file's formats either way.

## One copy of the build, replaced each time
- **main no longer holds the build or the lightmaps** (`.gitignore`: `prototypes/godot-mall/play/index.*` and `project/main_*.exr|.exr.import|.lmbake`).
- **They live on the `godot-build` branch:** `play/` (the export) and `lightmaps/`, as a single commit that each publish replaces with `git push --force`.
- **Serving:** `.github/workflows/pages.yml` on main deploys the site to GitHub Pages: everything on main, plus `godot-build:play/*` copied into `prototypes/godot-mall/play/`.
  - It runs on every push to main.
  - `godot-build`'s own workflow starts it when a new build is pushed.
- **Pages setting:** Settings → Pages → Source must be "GitHub Actions". The "Deploy from a branch" setting would serve main without the Godot build.
- **History (done Oct 6, ~4 pm):** the old builds and lightmaps, `play3b/` and the `godot-court` build and bakes were removed from the history of every branch with `git filter-repo`, and all ten branches force-pushed.
  - Before: 755 MiB, mostly 18 old game files (239 MB) and 36 old light bakes (353 MB).
  - After: 149 MiB for the whole repository, `godot-build` included.
  - GitHub's own size figure drops only after GitHub cleans up the unreachable objects.
  - **Backup of the old history:** `~/GodotProjects/southland-backup-2026-10-06.bundle` on Steven's MacBook Air (705 MB, all 10 branches as of Demo 9b; `git clone southland-backup-2026-10-06.bundle` restores it).
  - Commit ids changed. Any older clone must be re-cloned or reset to the new `origin/main`; never push an old clone's branches back.

## Publishing a demo now
1. **Bake on the Mac.** If the project there has no lightmaps yet, copy them from the branch first: `git fetch origin godot-build && git archive FETCH_HEAD lightmaps | tar -x`, then move `lightmaps/*` into `prototypes/godot-mall/project/`.
2. **Bring the bake back and check it:** `tools/qa/bakecheck.sh` (it now calls `export_web.sh`).
3. **Commit code changes to main** as usual. There is no build or lightmap to commit.
4. **Replace the build branch** from the project folder: `tools/publish_build.sh <builddir> "chore: Godot mall Demo N build and lightmaps"`. It takes the export and the project's six `main_*` lightmap files and force-pushes them to `godot-build` as one commit, keeping the branch's README and workflow.
5. **Wait for the deploy:** Pages redeploys in a minute or two (Actions tab: "Deploy site to Pages"; check it with `gh run list -R stevenboudreaux/Southland-Mall-95 -L 3`).
- **For a change that needs no rebake** (probe-lit parts only), take the lightmaps from the branch, rebuild, export and do step 4.
