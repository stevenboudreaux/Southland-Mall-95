#!/bin/bash
# usage: tools/export_web.sh <outdir>   (run from the project folder, godot on PATH)
# Exports the web build as two game files that differ only in texture formats, so each
# device downloads one:
#   index.desktop.pck  S3TC and BPTC  (computer GPUs)
#   index.mobile.pck   ETC2 and ASTC  (phones, tablets, VR headsets)
# plus the shared index.html / .js / .wasm. web/shell.html picks the file at load time and
# scripts/mall_runtime.gd switches once if it guessed wrong. Writes the pack sizes into
# index.html for the loading bar. Presets "Web Desktop" and "Web Mobile" in export_presets.cfg.
set -e
OUT=$(realpath -m "$1"); T=$OUT.tmp
rm -rf "$T"; mkdir -p "$OUT" "$T/d" "$T/m"
timeout 400 godot --headless --path . --export-release "Web Desktop" "$T/d/index.html" > "$T/desktop.log" 2>&1 || true
timeout 400 godot --headless --path . --export-release "Web Mobile" "$T/m/index.html" > "$T/mobile.log" 2>&1 || true
for k in d m; do [ -s "$T/$k/index.pck" ] || { echo "export failed ($k), see $T"; exit 1; }; done
rm -f "$OUT"/index.*
cp "$T/d/"index.* "$OUT/"
rm -f "$OUT/index.pck"
cp "$T/d/index.pck" "$OUT/index.desktop.pck"
cp "$T/m/index.pck" "$OUT/index.mobile.pck"
SD=$(stat -c %s "$OUT/index.desktop.pck"); SM=$(stat -c %s "$OUT/index.mobile.pck")
sed -i "s|const PACK_SIZES = {\"desktop\": 0, \"mobile\": 0};|const PACK_SIZES = {\"desktop\": $SD, \"mobile\": $SM};|" "$OUT/index.html"
grep -q "\"desktop\": $SD" "$OUT/index.html" || { echo "could not write pack sizes into index.html"; exit 1; }
rm -rf "$T"
echo "desktop $SD  mobile $SM"
