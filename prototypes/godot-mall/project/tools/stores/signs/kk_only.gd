## Rebuilds only the Karmelkorn sign (gen/w2/dyn_s6kf_sign.res and ..._glow.res) with the same code
## the wing build runs (store2.gd kk_sign, both fronts), so the sign can change without a rebuild
## or a rebake: these are dynamic meshes, outside the lightmap. (Oct 7: the old flat letters were the
## only thing in gen/w2/dyn_s6kf_props.res; that mesh went, and wing2.tscn's node for it now holds
## the sign and its glow, as a full build would make them.)
## Run: godot --headless --path . --script res://tools/stores/signs/kk_only.gd
extends SceneTree

class Mini:
	var dyn_acc = {}
	var mats = {}
	const LANE_H = 4.6
	func st(group, mname, _dynamic = false):
		if not dyn_acc.has(group):
			dyn_acc[group] = {}
		if not dyn_acc[group].has(mname):
			var s = SurfaceTool.new()
			s.begin(Mesh.PRIMITIVE_TRIANGLES)
			dyn_acc[group][mname] = s
		return dyn_acc[group][mname]
	func mat(name):
		if mats.has(name):
			return mats[name]
		var m = StandardMaterial3D.new()
		m.resource_name = name
		if not load("res://tools/stores/signs/channel.gd").fill_mat(m, name.substr(3), self):
			push_error("unknown material " + name)
		mats[name] = m
		return m

func _initialize():
	var GEN = "res://gen/w2/"
	# Karmelkorn's frame (build_mall.gd BUILT_RECTS: x -36..-20, z 60..70): the north front at z = 60
	# looking north, laid out from x = -36; the east front at x = -20. W 16, D 10, head 2.7 (store2.gd).
	var a = Vector3(-36, 0, 60)
	var t = Vector3(1, 0, 0)
	var n = Vector3(0, 0, -1)
	var W = 16.0
	var D = 10.0
	var head = 2.7
	var S2 = load("res://tools/stores/small/store2.gd")
	var b = Mini.new()
	S2.kk_sign(b, a + t * (W * 0.5) - n * -0.25 + Vector3.UP * (head + S2.KK_LIFT), n)
	var e0 = a + t * W
	S2.kk_sign(b, e0 - n * (D * 0.5) + Vector3.UP * (head + S2.KK_LIFT) + t * 0.25, t)
	for gname in b.dyn_acc:
		var am = ArrayMesh.new()
		var tris = 0
		for mname in b.dyn_acc[gname]:
			var s = b.dyn_acc[gname][mname]
			s.index()
			s.commit(am, Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)
			am.surface_set_material(am.get_surface_count() - 1, b.mat(mname))
			tris += am.surface_get_array_index_len(am.get_surface_count() - 1) / 3
		ResourceSaver.save(am, GEN + "dyn_" + gname + ".res")
		print("wrote dyn_", gname, " surfaces ", am.get_surface_count(), " tris ", tris, " aabb ", am.get_aabb())
	quit()
