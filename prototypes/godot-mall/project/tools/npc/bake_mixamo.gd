## Bakes Mixamo's own characters (Ch01…, Remy: the "nonPBR" FBX downloads, 35–90 MB each with
## 4K textures and 30–45 k triangles) into lean shippable skins, like tools/npc/bake_npcs.gd
## does for the bought pack. Steven, Oct 15 2026 17:28: "absorb these characters into the first
## build … these are just such a better quality npc skin".
##
## Per character:
##   - bones renamed mixamorig1_* → mixamorig_* (and the skin binds with them) so the shared
##     clips in npc/anims.res drive them;
##   - every mesh rebuilt from one of the importer's own LOD index sets (meshoptimizer keeps the
##     skin weights), compacted to the vertices it uses: `target_tris` picks the level;
##   - eyelash meshes dropped; hair/eyebrow materials get alpha scissor, the rest are opaque;
##     normal maps dropped;
##   - each albedo saved once as npc/skins/<Id>_<n>.png at `tex_px` (1024 default). New pngs
##     need an import pass before the scene can reference them, so the script writes them and
##     prints REIMPORT; tools/npc/stage_src.sh runs it again after `--import`.
##   - npc/skins/<Id>.scn, and an entry (group "mixamo", scale 1) merged into npc/skins.json.
## Run:  godot --headless --path . --script res://tools/npc/bake_mixamo.gd -- [--tris=8000] [--px=1024]
extends SceneTree

var src := "res://npc_src/mixamo/"
var out := "res://npc/skins/"
var target_tris := 8000
var tex_px := 1024

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--tris="): target_tris = int(a.substr(7))
		elif a.begins_with("--px="): tex_px = int(a.substr(5))
		elif a.begins_with("--src="): src = a.substr(6)
		elif a.begins_with("--out="): out = a.substr(6)
	var dir := DirAccess.open(src)
	if dir == null: print("no ", src); quit(); return
	var ids := []
	for f in dir.get_files():
		if f.ends_with(".fbx"): ids.append(f.get_basename())
	ids.sort()
	# pass 1: textures
	var wrote := 0
	for id in ids:
		wrote += _write_textures(id)
	if wrote > 0:
		print("REIMPORT: wrote ", wrote, " textures; import, then run again")
		quit(); return
	# pass 2: scenes
	var mf := {"skins": []}
	if FileAccess.file_exists("res://npc/skins.json"):
		var j = JSON.parse_string(FileAccess.get_file_as_string("res://npc/skins.json"))
		if j is Dictionary: mf = j
	var keep := []
	for e in mf.get("skins", []):
		if str(e.get("group", "")) != "mixamo": keep.append(e)
	for id in ids:
		var e := _bake(id)
		if not e.is_empty(): keep.append(e)
	mf.skins = keep
	var f := FileAccess.open("res://npc/skins.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(mf, "\t"))
	print("skins.json: ", keep.size(), " skins")
	quit()

## The albedo of every material in the file, saved small. Returns how many were new.
func _write_textures(id: String) -> int:
	var ps: PackedScene = load(src + id + ".fbx")
	if ps == null: print("SKIP ", id, ": no import"); return 0
	var root: Node = ps.instantiate()
	var n := 0; var seen := {}
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		for s in range(mi.mesh.get_surface_count()):
			var m = mi.mesh.surface_get_material(s)
			if not (m is BaseMaterial3D) or m.albedo_texture == null: continue
			var key := str(m.albedo_texture.get_rid())
			if seen.has(key): continue
			seen[key] = true
			var path := _tex_path(id, seen.size() - 1)
			if FileAccess.file_exists(path): continue
			var img: Image = m.albedo_texture.get_image()
			if img.is_compressed(): img.decompress()
			var px := tex_px if seen.size() == 1 else tex_px / 2   # the body atlas full size, hair etc. half
			img.resize(px, px, Image.INTERPOLATE_LANCZOS)
			img.save_png(path)
			_write_import(path)
			n += 1
	root.free()
	return n

func _tex_path(id: String, i: int) -> String:
	return out + id + ("_%d" % i) + ".png"

func _write_import(png: String) -> void:
	var f := FileAccess.open(png + ".import", FileAccess.WRITE)
	f.store_string('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n[deps]\n\nsource_file="%s"\n\n[params]\n\ncompress/mode=2\ncompress/high_quality=false\ncompress/lossy_quality=0.7\ncompress/uastc_level=0\ncompress/rdo_quality_loss=0.0\ncompress/hdr_compression=1\ncompress/normal_map=0\ncompress/channel_pack=0\nmipmaps/generate=true\nmipmaps/limit=-1\nroughness/mode=0\nroughness/src_normal=""\nprocess/fix_alpha_border=true\nprocess/premult_alpha=false\nprocess/normal_map_invert_y=false\nprocess/hdr_as_srgb=false\nprocess/hdr_clamp_exposure=false\nprocess/size_limit=0\ndetect_3d/compress_to=0\n' % png)

func _bake(id: String) -> Dictionary:
	var ps: PackedScene = load(src + id + ".fbx")
	if ps == null: return {}
	var root: Node3D = ps.instantiate()
	var sk: Skeleton3D = root.find_child("Skeleton3D", true, false)
	var ap: AnimationPlayer = root.find_child("AnimationPlayer", true, false)
	if ap: root.remove_child(ap); ap.free()
	# bone names
	var renames := {}
	for b in range(sk.get_bone_count()):
		var nm := sk.get_bone_name(b)
		var pos := nm.find("_")
		if nm.begins_with("mixamorig") and pos > 0:
			var nn := "mixamorig" + nm.substr(pos)
			if nn != nm:
				renames[nm] = nn
				sk.set_bone_name(b, nn)
	var hips := sk.find_bone("mixamorig_Hips")
	if hips < 0: print("SKIP ", id, ": no Hips"); root.free(); return {}
	var hips_y := sk.get_bone_rest(hips).origin.y
	var top := 0.0
	for b in range(sk.get_bone_count()): top = max(top, sk.get_bone_global_rest(b).origin.y)
	# meshes
	var seen := {}
	var tris_total := 0
	var meshes := []
	var full_tris := 0
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		if "Eyelash" in mi.name or "eyelash" in mi.name:
			mi.get_parent().remove_child(mi); mi.free(); continue
		meshes.append(mi)
		for s in range(mi.mesh.get_surface_count()):
			full_tris += mi.mesh.surface_get_arrays(s)[Mesh.ARRAY_INDEX].size() / 3
	for mi in meshes:
		var am := ArrayMesh.new()
		for s in range(mi.mesh.get_surface_count()):
			var m = mi.mesh.surface_get_material(s)
			var mat := StandardMaterial3D.new()
			mat.roughness = 0.9; mat.metallic_specular = 0.15
			if m is BaseMaterial3D and m.albedo_texture != null:
				var key := str(m.albedo_texture.get_rid())
				if not seen.has(key): seen[key] = seen.size()
				mat.albedo_texture = load(_tex_path(id, seen[key]))
				var mname := str(m.resource_name).to_lower()
				if "hair" in mname or "brow" in mname or "lash" in mname:
					mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
					mat.alpha_scissor_threshold = 0.5
					mat.cull_mode = BaseMaterial3D.CULL_DISABLED
			var share := float(mi.mesh.surface_get_arrays(s)[Mesh.ARRAY_INDEX].size() / 3) / float(maxi(full_tris, 1))
			var arrays := _lod_arrays(mi.mesh, s, int(target_tris * share))
			am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
			am.surface_set_material(am.get_surface_count() - 1, mat)
			tris_total += arrays[Mesh.ARRAY_INDEX].size() / 3
		mi.mesh = am
		mi.set_surface_override_material(0, null)
		if mi.skin:
			var skin: Skin = mi.skin.duplicate()
			for i in range(skin.get_bind_count()):
				var bn := skin.get_bind_name(i)
				if renames.has(bn): skin.set_bind_name(i, renames[bn])
			mi.skin = skin
	root.name = id
	# a few older Mixamo files are not in metres (Remy came in at 3.7 m): bring them to ~1.76 m
	var scale := 1.0
	if top > 2.2 or top < 1.3: scale = 1.76 / top
	root.scale = Vector3.ONE * scale
	_own(root, root)
	var packed := PackedScene.new(); packed.pack(root)
	var err := ResourceSaver.save(packed, out + id + ".scn", ResourceSaver.FLAG_COMPRESS)
	var e := {"id": id, "scn": out + id + ".scn", "sex": "?", "group": "mixamo", "scale": snappedf(scale, 0.0001),
		"hips": snappedf(hips_y, 0.0001), "height_m": snappedf(top * scale, 0.01), "kid": false, "tris": tris_total}
	print(id, " ", err, " ", tris_total, " tris, ", seen.size(), " textures, ", e.height_m, " m")
	root.free()
	return e

## The surface's arrays rebuilt on the importer LOD closest to target_tris, compacted.
func _lod_arrays(mesh: Mesh, s: int, want: int) -> Array:
	var arrays: Array = mesh.surface_get_arrays(s)
	var full: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var sd: Dictionary = RenderingServer.mesh_get_surface(mesh.get_rid(), s)
	var vcount: int = sd.vertex_count
	var best: PackedInt32Array = full
	var best_d := absi(full.size() / 3 - want)
	for l in sd.get("lods", []):
		var idx := _indices(l.index_data, vcount)
		var d := absi(idx.size() / 3 - want)
		if d < best_d: best_d = d; best = idx
	# compact
	var remap := PackedInt32Array(); remap.resize(vcount); remap.fill(-1)
	var order := PackedInt32Array()
	var new_idx := PackedInt32Array(); new_idx.resize(best.size())
	for i in range(best.size()):
		var v := best[i]
		if remap[v] < 0: remap[v] = order.size(); order.append(v)
		new_idx[i] = remap[v]
	var outa := []
	outa.resize(Mesh.ARRAY_MAX)
	for k in [Mesh.ARRAY_VERTEX, Mesh.ARRAY_NORMAL, Mesh.ARRAY_TANGENT, Mesh.ARRAY_TEX_UV]:
		var a = arrays[k]
		if a == null: continue
		var per := 4 if k == Mesh.ARRAY_TANGENT else 1
		var na = a.duplicate(); na.resize(order.size() * per)
		for i in range(order.size()):
			for j in range(per): na[i * per + j] = a[order[i] * per + j]
		outa[k] = na
	# skin weights: Mixamo files carry 8 per vertex; keep the 4 strongest, renormalised, since the
	# surface is re-added as a plain 4-weight mesh (8 would need ARRAY_FLAG_USE_8_BONE_WEIGHTS and
	# would bind vertices to the wrong bones if read as 4)
	var bones = arrays[Mesh.ARRAY_BONES]; var weights = arrays[Mesh.ARRAY_WEIGHTS]
	if bones != null and weights != null:
		var per: int = bones.size() / vcount
		var nb := PackedInt32Array(); nb.resize(order.size() * 4)
		var nw := PackedFloat32Array(); nw.resize(order.size() * 4)
		for i in range(order.size()):
			var v: int = order[i]
			var pairs := []
			for j in range(per): pairs.append([float(weights[v * per + j]), int(bones[v * per + j])])
			pairs.sort_custom(func(x, y): return x[0] > y[0])
			var total := 0.0
			for j in range(4): total += pairs[j][0] if j < pairs.size() else 0.0
			for j in range(4):
				if j < pairs.size():
					nb[i * 4 + j] = pairs[j][1]; nw[i * 4 + j] = pairs[j][0] / total if total > 0.0 else (1.0 if j == 0 else 0.0)
				else:
					nb[i * 4 + j] = 0; nw[i * 4 + j] = 0.0
		outa[Mesh.ARRAY_BONES] = nb
		outa[Mesh.ARRAY_WEIGHTS] = nw
	outa[Mesh.ARRAY_INDEX] = new_idx
	return outa

func _indices(data: PackedByteArray, vcount: int) -> PackedInt32Array:
	var r := PackedInt32Array()
	if vcount <= 65536:
		r.resize(data.size() / 2)
		for i in range(r.size()): r[i] = data.decode_u16(i * 2)
	else:
		r.resize(data.size() / 4)
		for i in range(r.size()): r[i] = data.decode_u32(i * 4)
	return r

func _own(n: Node, owner: Node) -> void:
	for c in n.get_children():
		c.owner = owner
		_own(c, owner)
