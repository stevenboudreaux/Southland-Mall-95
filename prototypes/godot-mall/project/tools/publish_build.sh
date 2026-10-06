#!/bin/bash
# usage: tools/publish_build.sh <builddir> "<commit message>"   (run from the project folder)
# Replaces the godot-build branch with this build and the project's current lightmaps, as one
# commit, and force-pushes it. Its workflow then asks main's Pages workflow to redeploy.
# <builddir> is an export from tools/export_web.sh (index.desktop.pck, index.mobile.pck, ...).
# Old builds never pile up: see design/godot-build-hosting.md.
set -e
SRC=$(realpath "$1"); MSG=$2
[ -s "$SRC/index.desktop.pck" ] && [ -s "$SRC/index.mobile.pck" ] || { echo "not a split export: $SRC"; exit 1; }
grep -q '"desktop": [1-9]' "$SRC/index.html" || { echo "index.html has no pack sizes (export with tools/export_web.sh)"; exit 1; }
for f in exr exr.import lmbake; do for m in night day; do [ -s main_$m.$f ] || { echo "missing main_$m.$f"; exit 1; }; done; done
REPO=$(git rev-parse --show-toplevel)
W=$(mktemp -d)
git -C "$REPO" fetch -q origin godot-build
git -C "$REPO" archive origin/godot-build README.md .github | tar -x -C "$W"
mkdir -p "$W/play" "$W/lightmaps"
cp "$SRC"/index.* "$W/play/"
cp main_night.exr main_night.exr.import main_night.lmbake main_day.exr main_day.exr.import main_day.lmbake "$W/lightmaps/"
cd "$W"
git init -q -b godot-build
git add -A
git -c user.name="Steven Boudreaux" -c user.email="steven_boudreaux@outlook.com" commit -q -m "$MSG"
git push -q --force "$(git -C "$REPO" remote get-url origin)" godot-build 2>&1 | grep -iv "moved\|new location\|github.com/stevenboudreaux\|^remote: *$\|GH001\|gh.io\|lfs\|recommended maximum" || true
echo "published $(git rev-parse --short HEAD)"
cd / && rm -rf "$W"
