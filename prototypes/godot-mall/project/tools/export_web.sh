#!/bin/bash
# usage: tools/export_web.sh <outdir> [wings]   (run from the project folder, godot on PATH)
# Exports the web build: the mall in two wings (design/godot-wings.md), each as two game files
# that differ only in texture formats, so each device downloads one wing in one format:
#   w1.desktop.pck / w2.desktop.pck  S3TC and BPTC  (computer GPUs)
#   w1.mobile.pck  / w2.mobile.pck   ETC2 and ASTC  (phones, tablets, VR headsets)
# plus the shared index.html / .js / .wasm. web/shell.html picks the wing (?wing=) and the
# format at load time; scripts/mall_runtime.gd switches format once if it guessed wrong. Writes
# the pack sizes into index.html for the loading bar and the cache name. Presets "Wing 1 Desktop",
# "Wing 1 Mobile", "Wing 2 Desktop", "Wing 2 Mobile" in export_presets.cfg.
# [wings]: "1 2" (default). Exporting one wing keeps the other wing's files already in <outdir>.
set -e
OUT=$(realpath -m "$1"); T=$OUT.tmp; WINGS=${2:-"1 2"}
rm -rf "$T"; mkdir -p "$OUT" "$T"
for w in $WINGS; do
  for k in desktop mobile; do
    K=$(echo $k | sed 's/./\U&/')
    mkdir -p "$T/$w$k"
    timeout 600 godot --headless --path . --export-release "Wing $w $K" "$T/$w$k/index.html" > "$T/w$w-$k.log" 2>&1 || true
    [ -s "$T/$w$k/index.pck" ] || { echo "export failed (wing $w $k), see $T/w$w-$k.log"; exit 1; }
    cp "$T/$w$k/index.pck" "$OUT/w$w.$k.pck"
  done
done
F=$(echo $WINGS | cut -d' ' -f1)
for f in "$T/${F}desktop/"index.*; do
  b=$(basename "$f"); [ "$b" = "index.pck" ] || cp "$f" "$OUT/$b"
done
rm -f "$OUT/index.pck" "$OUT/index.desktop.pck" "$OUT/index.mobile.pck"
for w in 1 2; do for k in desktop mobile; do [ -s "$OUT/w$w.$k.pck" ] || { echo "missing $OUT/w$w.$k.pck"; exit 1; }; done; done
S1D=$(stat -c %s "$OUT/w1.desktop.pck"); S1M=$(stat -c %s "$OUT/w1.mobile.pck")
S2D=$(stat -c %s "$OUT/w2.desktop.pck"); S2M=$(stat -c %s "$OUT/w2.mobile.pck")
sed -i "s|const PACK_SIZES = {\"w1\": {\"desktop\": 0, \"mobile\": 0}, \"w2\": {\"desktop\": 0, \"mobile\": 0}};|const PACK_SIZES = {\"w1\": {\"desktop\": $S1D, \"mobile\": $S1M}, \"w2\": {\"desktop\": $S2D, \"mobile\": $S2M}};|" "$OUT/index.html"
grep -q "\"desktop\": $S1D" "$OUT/index.html" || { echo "could not write pack sizes into index.html"; exit 1; }
rm -rf "$T"
echo "wing1 desktop $S1D mobile $S1M  wing2 desktop $S2D mobile $S2M"
