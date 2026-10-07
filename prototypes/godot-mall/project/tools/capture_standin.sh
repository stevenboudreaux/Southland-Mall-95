#!/bin/bash
# usage: tools/capture_standin.sh <wing>   (from the project folder; godot 4.7.2 on PATH, xvfb-run)
# Captures wing <wing>'s storefronts, night and day, from its baked build into
# tex/standin/from_w<wing>_{night,day}.png for the other wing's stand-in, and stamps them with
# tools/wing_hash.sh (design/godot-wings.md). The wing's lightmaps must be in the project and
# imported (godot --headless --path . --import). Takes a few minutes per mode in software GL.
set -e
W=$1
for M in night day; do
  timeout 1500 xvfb-run -a -s "-screen 0 1280x720x24" godot --path . --rendering-driver opengl3 --resolution 640x360 \
    --script res://tools/capture_standin.gd -- --wing=$W --mode=$M 2>&1 | grep -E "capturing|wrote|ERROR|error" | grep -v "RID alloc\|resources still\|Pages in use" | head -20
  [ -s tex/standin/from_w${W}_$M.png ] || { echo "capture failed: wing $W $M"; exit 1; }
done
tools/wing_hash.sh $W > tex/standin/from_w$W.stamp
echo "stamped wing $W stand-in: $(cat tex/standin/from_w$W.stamp)"
