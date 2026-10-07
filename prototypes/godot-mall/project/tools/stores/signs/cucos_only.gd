## Rebuilds only the Cucos sign's two meshes (gen/w1/dyn_w8cf_sign.res and ..._glow.res) with the
## same code the wing build runs (wave8.gd cucos_sign), so the sign can change without a rebuild
## or a rebake: the sign is a dynamic mesh, outside the lightmap.
## Run: godot --headless --path . --script res://tools/stores/signs/cucos_only.gd
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
	var GEN = "res://gen/w1/"
	var old = load(GEN + "dyn_w8cf_sign.res")
	if old:
		print("old sign aabb ", old.get_aabb())
	var b = Mini.new()
	# Cucos's front (build_mall.gd BUILT_RECTS): x 22..36 at z = -86, facing north; laid out from the viewer's left
	load("res://tools/stores/small/wave8.gd").cucos_sign(b, Vector3(36, 0, -86), Vector3(-1, 0, 0), Vector3(0, 0, -1), 14.0, 2.9)
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
