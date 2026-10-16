#!/bin/bash
# Prepares npc/skins/<Name>.png (256 px, VRAM-compressed import) from npc_src/chars/<Name>.png,
# imports the project, then runs tools/npc/bake_npcs.gd. See that file for what comes out.
# Usage, from prototypes/godot-mall/project with godot on PATH:  tools/npc/stage_src.sh
set -e
cd "$(dirname "$0")/../.."
mkdir -p npc/skins
python3 - <<'EOF'
from PIL import Image
import glob, os
n = 0
for src in sorted(glob.glob('npc_src/chars/*.png')):
    name = os.path.basename(src)
    im = Image.open(src).convert('RGBA').resize((256, 256), Image.LANCZOS)
    im.save('npc/skins/' + name, optimize=True)
    imp = 'npc/skins/' + name + '.import'
    if not os.path.exists(imp):
        open(imp, 'w').write('''[remap]

importer="texture"
type="CompressedTexture2D"

[deps]

source_file="res://npc/skins/%s"

[params]

compress/mode=2
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=true
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=0
''' % name)
    n += 1
print('textures:', n)
EOF
timeout 1200 godot --headless --path . --import > /dev/null 2>&1 || true
timeout 600 godot --headless --path . --script res://tools/npc/bake_npcs.gd 2>&1 | grep -v "^\s*$" | grep -v "ALSA\|at: \|WARNING\|leaked\|still in use\|PagedAllocator"
# Mixamo's own characters (npc_src/mixamo/*.fbx): pass 1 writes their textures, import, pass 2 bakes
if ls npc_src/mixamo/*.fbx > /dev/null 2>&1; then
  timeout 900 godot --headless --path . --script res://tools/npc/bake_mixamo.gd 2>&1 | grep "REIMPORT\|tris\|SKIP\|skins.json"
  timeout 1200 godot --headless --path . --import > /dev/null 2>&1 || true
  timeout 900 godot --headless --path . --script res://tools/npc/bake_mixamo.gd 2>&1 | grep "REIMPORT\|tris\|SKIP\|skins.json"
fi
du -sh npc/skins npc/anims.res
