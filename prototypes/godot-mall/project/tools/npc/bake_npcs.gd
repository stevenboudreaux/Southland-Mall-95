## Bakes the NPC character pack and the Mixamo clips into lean, shippable resources.
##
## Sources (not shipped; chars/ is gitignored, see production/npc-sources.md):
##   npc_src/chars/<Name>.fbx + <Name>.png   the bought "Characters PSX" pack, Mixamo-rigged
##   npc_src/anims/<Clip>.fbx                Mixamo clips downloaded "without skin" on Character_01
## Output:
##   npc/skins/<Name>.scn   the imported character with a fresh material on npc/skins/<Name>.png
##                          and its one-frame AnimationPlayer removed (~45 KB each)
##   npc/skins/<Name>.png   256 px copy of the texture (VRAM-compressed by its .import)
##   npc/anims.res          AnimationLibrary: walk, idle, look, sit; the walk's forward root motion
##                          is removed (the engine moves the body) and every clip loops
##   npc/skins.json         manifest: id, sex, group, scale (to metres), hips (skeleton units),
##                          height_m, kid, plus the clips' natural walk speed
## Run (after the pngs are downscaled by tools/npc/stage_src.sh and the project is imported):
##   godot --headless --path . --script res://tools/npc/bake_npcs.gd
##
## Scale: the pack is two batches. The original files (01–33, Female_01–16, …) are ~2.66× metres
## (hips rest ≈ 2.70); the Extras (34+, Male_33+) are in metres (hips ≈ 0.9). Every skin gets
## `scale` so its hips land near the clips' 1.01 m, and the engine scales the clips' position
## tracks by `hips / anim_hips` per skin so the bob matches (see scripts/npc_body.gd).
extends SceneTree

const SRC_CHARS := "res://npc_src/chars/"
const SRC_ANIMS := "res://npc_src/anims/"
const OUT := "res://npc/skins/"
const BIG_BATCH_RATIO := 2.6627   # Character_01's hips (2.6974) over the clips' (1.0130)
const CLIPS := {"walk": "Walking", "idle": "Standing_Idle", "look": "Looking_Around", "sit": "Sitting_Idle"}

func _initialize() -> void:
	var manifest := {"skins": [], "anim_hips": 0.0, "walk_mps": 0.0}
	# ---- clips
	var lib := AnimationLibrary.new()
	var anim_hips := 0.0
	for key in CLIPS:
		var scene: Node = load(SRC_ANIMS + CLIPS[key] + ".fbx").instantiate()
		var sk: Skeleton3D = scene.find_child("Skeleton3D", true, false)
		if anim_hips == 0.0: anim_hips = sk.get_bone_rest(sk.find_bone("mixamorig_Hips")).origin.y
		var ap: AnimationPlayer = scene.find_child("AnimationPlayer", true, false)
		var a: Animation = ap.get_animation(ap.get_animation_list()[0]).duplicate(true)
		a.loop_mode = Animation.LOOP_LINEAR
		for t in range(a.get_track_count()):
			if a.track_get_type(t) == Animation.TYPE_POSITION_3D and str(a.track_get_path(t)).ends_with("Hips"):
				var p0: Vector3 = a.track_get_key_value(t, 0)
				var p1: Vector3 = a.track_get_key_value(t, a.track_get_key_count(t) - 1)
				if key == "walk":
					manifest.walk_mps = snappedf((p1 - p0).length() / a.length, 0.001)
				# keep the vertical bob, drop the travel: the body node moves instead
				for k in range(a.track_get_key_count(t)):
					var v: Vector3 = a.track_get_key_value(t, k)
					a.track_set_key_value(t, k, Vector3(p0.x, v.y, p0.z))
		lib.add_animation(key, a)
		print("clip ", key, " len ", snappedf(a.length, 0.01), " tracks ", a.get_track_count())
		scene.free()
	manifest.anim_hips = anim_hips
	var err := ResourceSaver.save(lib, "res://npc/anims.res")
	print("anims.res ", err, " walk ", manifest.walk_mps, " m/s, anim hips ", anim_hips)
	# ---- skins
	var dir := DirAccess.open(SRC_CHARS)
	var names := []
	for f in dir.get_files():
		if f.ends_with(".fbx"): names.append(f.get_basename())
	names.sort()
	for id in names:
		var ps: PackedScene = load(SRC_CHARS + id + ".fbx")
		if ps == null: print("SKIP ", id, ": no import"); continue
		var root: Node3D = ps.instantiate()
		var sk: Skeleton3D = root.find_child("Skeleton3D", true, false)
		var ap: AnimationPlayer = root.find_child("AnimationPlayer", true, false)
		if ap: root.remove_child(ap); ap.free()
		var hips: float = sk.get_bone_rest(sk.find_bone("mixamorig_Hips")).origin.y
		var big := hips > 1.8
		var scale := 1.0 / BIG_BATCH_RATIO if big else 1.0
		var top := 0.0
		for b in range(sk.get_bone_count()): top = max(top, sk.get_bone_global_rest(b).origin.y)
		var tex: Texture2D = load(OUT + id + ".png")
		var tris := 0
		for mi in root.find_children("*", "MeshInstance3D", true, false):
			for s in range(mi.mesh.get_surface_count()):
				var m := StandardMaterial3D.new()
				m.albedo_texture = tex; m.roughness = 0.95; m.metallic_specular = 0.1
				mi.mesh.surface_set_material(s, m)
				tris += mi.mesh.surface_get_arrays(s)[Mesh.ARRAY_INDEX].size() / 3
			mi.set_surface_override_material(0, null)
		root.name = id
		root.scale = Vector3.ONE * scale
		_own(root, root)
		var out := PackedScene.new(); out.pack(root)
		err = ResourceSaver.save(out, OUT + id + ".scn", ResourceSaver.FLAG_COMPRESS)
		var entry := {"id": id, "scn": OUT + id + ".scn", "sex": "f" if "Female" in id else "m",
			"group": _group(id), "scale": snappedf(scale, 0.0001), "hips": snappedf(hips, 0.0001),
			"height_m": snappedf(top * scale, 0.01), "kid": top * scale < 1.45, "tris": tris}
		manifest.skins.append(entry)
		print(id, " ", err, " ", entry.group, " ", entry.height_m, " m ", tris, " tris")
		root.free()
	var f := FileAccess.open("res://npc/skins.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(manifest, "\t"))
	print("skins.json: ", manifest.skins.size(), " skins")
	quit()

func _own(n: Node, owner: Node) -> void:
	for c in n.get_children():
		c.owner = owner
		_own(c, owner)

func _group(id: String) -> String:
	for g in ["Police", "Sheriff", "Firefighter", "Doctor", "HM"]:
		if g in id: return {"Police": "police", "Sheriff": "police", "Firefighter": "fire", "Doctor": "doctor", "HM": "hazmat"}[g]
	return "civ"
