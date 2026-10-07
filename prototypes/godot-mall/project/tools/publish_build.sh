#!/bin/bash
# usage: tools/publish_build.sh <builddir> "<commit message>"   (run from the project folder)
# Replaces the godot-build branch with this build and the project's current lightmaps, as one
# commit, and force-pushes it. Its workflow then asks main's Pages workflow to redeploy.
# <builddir> is an export from tools/export_web.sh (w1/w2 .desktop.pck and .mobile.pck, ...).
# Old builds never pile up: see design/godot-build-hosting.md.
# Refuses to publish when either wing's stand-in pictures (tex/standin/from_w<n>_*.png) were not
# captured from that wing as it is now (tools/wing_hash.sh; design/godot-wings.md): run
# tools/capture_standin.sh <n> and export again.
set -e
SRC=$(realpath "$1"); MSG=$2
for w in 1 2; do for k in desktop mobile; do [ -s "$SRC/w$w.$k.pck" ] || { echo "not a wing export: $SRC (no w$w.$k.pck)"; exit 1; }; done; done
grep -q '"w1": {"desktop": [1-9]' "$SRC/index.html" || { echo "index.html has no pack sizes (export with tools/export_web.sh)"; exit 1; }
for w in 1 2; do for f in exr exr.import lmbake; do for m in night day; do [ -s wing${w}_$m.$f ] || { echo "missing wing${w}_$m.$f"; exit 1; }; done; done; done
for w in 1 2; do
  for m in night day; do [ -s tex/standin/from_w${w}_$m.png ] || { echo "no stand-in pictures of wing $w ($m): run tools/capture_standin.sh $w"; exit 1; }; done
  H=$(tools/wing_hash.sh $w); S=$(cat tex/standin/from_w$w.stamp 2>/dev/null || echo none)
  [ "$H" = "$S" ] || { echo "wing $w changed since its stand-in pictures were taken (stamp $S, now $H): run tools/capture_standin.sh $w, export, publish"; exit 1; }
  for k in desktop mobile; do [ "$SRC/w$((3-w)).$k.pck" -nt tex/standin/from_w${w}_night.png ] || { echo "the export is older than wing $w's stand-in pictures: export again"; exit 1; }; done
done
REPO=$(git rev-parse --show-toplevel)
W=$(mktemp -d)
git -C "$REPO" fetch -q origin godot-build
git -C "$REPO" archive origin/godot-build README.md .github | tar -x -C "$W"
mkdir -p "$W/play" "$W/lightmaps" "$W/standin"
cp "$SRC"/index.* "$SRC"/w1.*.pck "$SRC"/w2.*.pck "$W/play/"
cp wing1_night.* wing1_day.* wing2_night.* wing2_day.* "$W/lightmaps/"
cp tex/standin/*.png tex/standin/*.stamp "$W/standin/"
cd "$W"
git init -q -b godot-build
git add -A
git -c user.name="Steven Boudreaux" -c user.email="steven_boudreaux@outlook.com" commit -q -m "$MSG"
git push -q --force "$(git -C "$REPO" remote get-url origin)" godot-build 2>&1 | grep -iv "moved\|new location\|github.com/stevenboudreaux\|^remote: *$\|GH001\|gh.io\|lfs\|recommended maximum" || true
echo "published $(git rev-parse --short HEAD)"
cd / && rm -rf "$W"
