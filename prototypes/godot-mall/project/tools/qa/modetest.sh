#!/bin/bash
# usage: modetest.sh <name> [project-dir]
# Exports the project's web build once, then shoots the Sears hall (W/E) and the
# Shoe Dept. court at night (?time=night, the default) and day (?time=day) and
# prints the mean luma of each shot, so two bakes can be compared by what the
# game shows. Needs godot 4.7 on PATH and `python3 -m http.server 8765` at the
# repo root (started here if port 8765 is free).
set -e
N=$1; R=$(git -C "$(dirname "$0")" rev-parse --show-toplevel); P=${2:-$R/prototypes/godot-mall/project}
cd "$P" && timeout 900 godot --headless --path . --import > /dev/null 2>&1 || true
mkdir -p "$R/.scratch/builds/$N" && timeout 300 godot --headless --path . --export-release Web "$R/.scratch/builds/$N/index.html" > /dev/null 2>&1
cd "$R" && mkdir -p .scratch/shots
if ! curl -s -o /dev/null http://127.0.0.1:8765/; then (python3 -m http.server 8765 > /dev/null 2>&1 &); sleep 1; fi
for M in night day; do
  CAMS="{\"searsW\":\"-60,-90,90,-5&time=$M\",\"searsE\":\"-60,-90,-90,-5&time=$M\",\"shoe\":\"0,14,0,-8&time=$M\"}" \
    timeout 900 python3 "$P/tools/qa/movetest.py" ".scratch/builds/$N/index.html" ".scratch/shots/$N-$M" > ".scratch/shots/$N-$M.log" 2>&1 || true
  python3 -c "
from PIL import Image,ImageStat
print('$N $M', ' '.join('%s=%.1f'%(c,ImageStat.Stat(Image.open('.scratch/shots/$N-$M-%s.png'%c).convert('L')).mean[0]) for c in ['searsW','searsE','shoe']))"
done
