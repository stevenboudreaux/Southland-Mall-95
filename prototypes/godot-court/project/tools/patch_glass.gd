## Re-applies the glass material to the saved dynamic glass mesh without a rebuild
## (glass is not part of the lightmap, so no re-bake is needed).
extends SceneTree
func _initialize() -> void:
	var m: ArrayMesh = load("res://gen/dyn_glass.res")
	for i in m.get_surface_count():
		var g: StandardMaterial3D = m.surface_get_material(i)
		g.albedo_color = Color(0.78, 0.86, 0.86, 0.10)
		g.metallic_specular = 0.5
		g.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
	ResourceSaver.save(m, "res://gen/dyn_glass.res")
	print("glass patched")
	quit()
