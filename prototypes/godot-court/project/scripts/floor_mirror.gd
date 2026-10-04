## Glossy floor: renders the scene from a camera mirrored under the floor
## (y = 0) into a small viewport, and the floor shader blends it in by a
## Fresnel term, the way polished terrazzo mirrors the lights and storefronts.
## The baked lightmap still lights the floor; the reflection is added on top.
extends Node

@export var scale := 0.5          # reflection resolution vs. the screen
@export var strength := 0.55
var vp: SubViewport
var mcam: Camera3D
var mat_cache := {}

const SHADER := """
shader_type spatial;
render_mode specular_schlick_ggx;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D refl_tex : source_color, filter_linear, repeat_disable;
uniform float roughness = 0.14;
uniform float strength = 0.55;
uniform vec2 px = vec2(0.002, 0.003);
void fragment() {
	vec3 a = texture(albedo_tex, UV).rgb;
	vec2 ruv = vec2(SCREEN_UV.x, 1.0 - SCREEN_UV.y);
	// soft vertical smear like a polished floor (5 taps)
	vec3 r = texture(refl_tex, ruv).rgb * 0.36;
	r += texture(refl_tex, ruv + vec2(0.0, px.y)).rgb * 0.22;
	r += texture(refl_tex, ruv - vec2(0.0, px.y)).rgb * 0.22;
	r += texture(refl_tex, ruv + vec2(px.x, px.y * 2.5)).rgb * 0.10;
	r += texture(refl_tex, ruv - vec2(px.x, px.y * 2.5)).rgb * 0.10;
	float ndv = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float fres = 0.05 + 0.95 * pow(1.0 - ndv, 4.0);
	float k = mix(0.22, 1.0, fres) * strength;
	// darker tiles mirror more visibly than light ones
	float lum = dot(a, vec3(0.3, 0.59, 0.11));
	k *= mix(1.15, 0.7, lum);
	ALBEDO = a * (1.0 - k * 0.45);
	ROUGHNESS = roughness;
	SPECULAR = 0.5;
	EMISSION = r * r * k * 1.1;
}
"""

func _ready() -> void:
	vp = SubViewport.new()
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.msaa_3d = Viewport.MSAA_DISABLED
	vp.positional_shadow_atlas_size = 0
	add_child(vp)
	mcam = Camera3D.new()
	vp.add_child(mcam)
	mcam.current = true
	var sh := Shader.new()
	sh.code = SHADER
	for mi in _meshes(get_tree().current_scene):
		var m: Mesh = mi.mesh
		for i in m.get_surface_count():
			var sm := m.surface_get_material(i)
			if sm is StandardMaterial3D and sm.resource_name.begins_with("floor_"):
				if not mat_cache.has(sm.resource_name):
					var s := ShaderMaterial.new()
					s.shader = sh
					s.set_shader_parameter("albedo_tex", sm.albedo_texture)
					s.set_shader_parameter("refl_tex", vp.get_texture())
					s.set_shader_parameter("roughness", sm.roughness)
					s.set_shader_parameter("strength", strength)
					mat_cache[sm.resource_name] = s
				mi.set_surface_override_material(i, mat_cache[sm.resource_name])
	_dress_interiors()
	_resize()
	get_viewport().size_changed.connect(_resize)

func _meshes(n: Node) -> Array:
	var out := []
	if n is MeshInstance3D and n.mesh:
		out.append(n)
	for c in n.get_children():
		out += _meshes(c)
	return out

func _resize() -> void:
	var s := get_viewport().get_visible_rect().size
	vp.size = Vector2i(max(64, int(s.x * scale)), max(64, int(s.y * scale)))
	for k in mat_cache:
		mat_cache[k].set_shader_parameter("px", Vector2(1.5 / vp.size.x, 2.0 / vp.size.y))

func _process(_dt: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null or cam == mcam:
		return
	var t := cam.global_transform
	# reflect across y = 0, then flip the camera's local y to keep it right-handed;
	# the shader flips SCREEN_UV.y to undo that.
	var S := Basis(Vector3(1, 0, 0), Vector3(0, -1, 0), Vector3(0, 0, 1))
	var b := S * t.basis
	b.y = -b.y
	mcam.global_transform = Transform3D(b, Vector3(t.origin.x, -t.origin.y, t.origin.z))
	mcam.fov = cam.fov
	mcam.near = cam.near
	mcam.far = cam.far

## Store side walls: shelving with merchandise on the vertical faces (seen at an
## angle through the glass), plain ceiling. Render-only, so the baked light stays.
const INTERIOR := """
shader_type spatial;
uniform sampler2D shelf_tex : source_color, filter_linear_mipmap, repeat_enable;
varying vec3 wpos;
varying vec3 wnrm;
void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	wnrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}
void fragment() {
	vec3 base = vec3(0.925, 0.902, 0.855);
	if (abs(wnrm.y) < 0.5) {
		float u = abs(wnrm.x) > 0.5 ? wpos.z : wpos.x;
		vec3 t = texture(shelf_tex, vec2(u / 3.4, 1.0 - wpos.y / 3.2)).rgb;
		base = mix(t, vec3(dot(t, vec3(0.3, 0.59, 0.11))), 0.3) * 0.9;
	}
	ALBEDO = base;
	ROUGHNESS = 0.9;
}
"""

func _dress_interiors() -> void:
	var sh := Shader.new()
	sh.code = INTERIOR
	var sm := ShaderMaterial.new()
	sm.shader = sh
	sm.set_shader_parameter("shelf_tex", load("res://tex/int_side.png"))
	for mi in _meshes(get_tree().current_scene):
		var m: Mesh = mi.mesh
		for i in m.get_surface_count():
			var mat := m.surface_get_material(i)
			if mat and mat.resource_name == "int_wall":
				mi.set_surface_override_material(i, sm)
