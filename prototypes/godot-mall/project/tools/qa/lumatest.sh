#!/bin/bash
# usage: lumatest.sh <name> <exr> [lmbake] -> export with that lightmap, shoot Sears/Shoe cams, print luma
set -e
N=$1; R=/home/claude/southland-mall-95; P=$R/prototypes/godot-mall/project
cp "$2" $P/main.exr; [ -n "$3" ] && cp "$3" $P/main.lmbake
cd $P && timeout 900 godot --headless --path . --import > /dev/null 2>&1
mkdir -p $R/.scratch/builds/$N && timeout 300 godot --headless --path . --export-release Web $R/.scratch/builds/$N/index.html > /dev/null 2>&1
cd $R && CAMS='{"searsW":"-60,-90,90,-5","searsE":"-60,-90,-90,-5","shoe":"0,14,0,-8"}' timeout 900 python3 .scratch/movetest.py .scratch/builds/$N/index.html .scratch/shots/$N > /dev/null 2>&1 || true
python3 -c "
from PIL import Image,ImageStat
print('$N', ' '.join('%s=%.1f'%(c,ImageStat.Stat(Image.open('.scratch/shots/$N-%s.png'%c).convert('L')).mean[0]) for c in ['searsW','searsE','shoe']))"
