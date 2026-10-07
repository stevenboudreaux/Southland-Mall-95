#!/bin/bash
# usage: tools/wing_hash.sh <wing>   (from the project folder)
# One fingerprint of everything that decides how a wing looks: its generated meshes and data
# (gen/w<wing>/), its lightmaps (wing<wing>_night/day.exr), the scene, and every texture outside
# tex/standin. tools/capture_standin.sh stamps the stand-in pictures with it; tools/publish_build.sh
# compares (design/godot-wings.md).
W=$1
{ ls gen/w$W/* wing${W}_night.exr wing${W}_day.exr 2>/dev/null; find tex -type f -name "*.png" -not -path "tex/standin/*"; } | sort | xargs md5sum 2>/dev/null | md5sum | cut -c1-32
