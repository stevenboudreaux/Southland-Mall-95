# NPC character sources (not in the repo)

The shoppers and window mannequins (`scripts/npcs.gd`, `scripts/npc_body.gd`) use baked skins in
`prototypes/godot-mall/project/npc/skins/` and the clips in `npc/anims.res`. The sources they were
baked from are big (35–90 MB per Mixamo character, 70 MB for the pack) and are gitignored under
`project/npc_src/chars/` and `project/npc_src/mixamo/`. Where to find them again:

| Source | Where | Notes |
|---|---|---|
| "Characters PSX" pack v1.2 (bought, 138 rigged FBX + textures) | Steven's Mac, `~/Downloads/Characters_psx_1.2` (also `Characters_Extras_01`, and the two .rar uploads of Oct 15) | Mixamo-rigged (`mixamorig:*`). Two scale batches, handled by `tools/npc/bake_npcs.gd`. 114 baked (killers, monsters, dancers and the untextured Female_01 left out). |
| Mixamo characters Ch01, Ch02, Ch06, Ch08, Ch12, Ch13, Ch17, Ch21, Ch22, Ch23, Ch26, Ch27, Ch28, Ch36, Ch37, Ch38, Ch41, Ch42, Remy | mixamo.com (Adobe login), "nonPBR" FBX download; uploaded by Steven Oct 15 17:28–17:34 | Bones `mixamorig1:*`, renamed at bake by `tools/npc/bake_mixamo.gd`. Ch36 is the featureless figure used for the window mannequins. |
| Mixamo clips Walking, Standing Idle, Looking Around, Sitting Idle (Demo 36, retired) | mixamo.com, FBX "without skin", 30 fps, on the pack's Character_01 | In the repo: `project/npc_src/anims/`. **Not used since Demo 38**: Character_01's arm and spine bones point ~180° from the Mixamo skins', which twisted every body. |
| Steven's clip library (Oct 16, ~93 FBX: locomotion packs, drunk pack, gestures pack, sitting, talking, arcade reactions, Texting While Standing) | Steven's Mac, `~/Desktop/Mixamo` (connected folder), downloaded on **Ch01**, without skin, 30 fps | Copied to `project/npc_src/mixamo_clips/` (gitignored) with lower-case names, plus `npc_src/ref/Ch01_nonPBR.fbx`. Their `.fbx.import` must keep `animation/remove_immutable_tracks=false`. Baked by `tools/npc/bake_clips.gd` into `npc/anims.res` (71 clips, 2.7 MB) and `npc/anims.json`. |

Clips: `godot --headless --path . --script res://tools/npc/bake_clips.gd` (`-- --stats` lists each clip's length, loop, hips drift and walk speed). New downloads: on Ch01, "Without Skin", 30 fps; walks may be In Place or not (both are handled).

Rebake: put the sources back in `npc_src/`, then from the project folder with godot on PATH
`tools/npc/stage_src.sh` (pack) and `godot --headless --path . --script res://tools/npc/bake_mixamo.gd`
(twice: the first run writes the textures and asks for an import). Both write `npc/skins.json`.

Mixamo's licence lets the characters and animations ship inside a game; the files themselves
are not redistributed, which is one reason they stay out of the repo.
