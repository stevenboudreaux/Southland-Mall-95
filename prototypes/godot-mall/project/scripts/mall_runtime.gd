## Runtime looks that don't need a re-bake:
## - Floors: a procedural terrazzo shader (hall checker bands, plank-laid store
##   lanes, court fields with borders) driven by per-zone parameters stored on
##   each floor material, plus a mirrored-camera reflection for the polish.
## - Store side walls: shelving with merchandise.
## The baked lightmap still lights everything; these only change surface colour.
extends Node

@export var scale := 0.5          # reflection resolution vs. the screen
@export var strength := 0.6
var vp: SubViewport
var mcam: Camera3D
var floor_mats := []

const FLOOR := """
shader_type spatial;
render_mode specular_schlick_ggx;
uniform sampler2D refl_tex : source_color, filter_linear, repeat_disable;
uniform int pattern = 0;       // 0 plank field, 1 hall, 2 court
uniform int axis = 0;          // hall: 0 runs along x, 1 along z
uniform float center = 0.0;    // hall centre line (across coordinate)
uniform float half_w = 6.0;    // hall half width
uniform int medallions = 0;
uniform vec4 court = vec4(0.0, 0.0, 8.0, 8.0);  // cx, cz, hx, hz
uniform int palette = 0;       // court: 0 taupe, 1 blue-grey (Shoe Dept.), 2 charcoal/salmon (Sears)
uniform float strength = 0.5;
uniform float refl_clamp = 1.5;
uniform vec2 px = vec2(0.002, 0.003);
varying vec3 wpos;

void vertex() { wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }

float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

// anti-aliased line mask: 1 on a line of half-width w at integer values of t
float lines(float t, float w) {
	float d = abs(t - round(t));
	float fw = fwidth(t);
	return 1.0 - smoothstep(w, w + fw * 1.2, d);
}
// filtered checkerboard (0/1) on a diagonal grid
float diag_checker(vec2 p, float period) {
	vec2 q = vec2(p.x + p.y, p.x - p.y) / period;
	vec2 w = fwidth(q) + 1e-4;
	vec2 i = 2.0 * (abs(fract((q - 0.5 * w) * 0.5) - 0.5) - abs(fract((q + 0.5 * w) * 0.5) - 0.5)) / w;
	return 0.5 - 0.5 * i.x * i.y;
}
vec3 planks(float across, float along) {
	float col = floor(across / 0.30);
	float shift = mod(col, 2.0) * 0.30;
	float row = floor((along + shift) / 0.60);
	float tone = hash(vec2(col, row));
	vec3 c = vec3(0.851, 0.780, 0.659) * (0.94 + 0.08 * tone);
	float g = max(lines(across / 0.30, 0.012), lines((along + shift) / 0.60, 0.007));
	return mix(c, vec3(0.66, 0.59, 0.49), g * 0.85);
}

void fragment() {
	vec3 a;
	if (pattern == 1) {
		float across = (axis == 0 ? wpos.z : wpos.x) - center;
		float along = axis == 0 ? wpos.x : wpos.z;
		float band = half_w * 0.5;
		float d = abs(across);
		vec2 p = axis == 0 ? vec2(along, across) : vec2(across, along);
		if (d < band) {
			float k = diag_checker(p, 0.75);
			a = mix(vec3(0.561, 0.486, 0.400), vec3(0.937, 0.902, 0.824), k);
			vec2 q = vec2(p.x + p.y, p.x - p.y) / 0.75;
			a = mix(a, vec3(0.725, 0.671, 0.580), max(lines(q.x, 0.008), lines(q.y, 0.008)) * 0.7);
		} else if (d < band + 0.18) {
			a = vec3(0.227, 0.216, 0.204);
		} else {
			a = planks(across + 50.0, along);
		}
		if (medallions == 1) {
			float lane = band + 0.18 + (half_w - band - 0.18) * 0.5;
			float m = abs(d - lane) + abs(mod(along, 9.0) - 4.5);
			if (m < 0.47) a = m < 0.45 ? (m < 0.18 ? vec3(0.227, 0.216, 0.204) : vec3(0.788, 0.541, 0.451)) : vec3(0.227, 0.216, 0.204);
		}
	} else if (pattern == 2) {
		vec2 c = wpos.xz - court.xy;
		vec2 h = court.zw;
		float m0 = 1.6;
		float bw = 0.9;
		float d = min(h.x - abs(c.x), h.y - abs(c.y)) - m0;
		vec3 c1 = vec3(0.914, 0.890, 0.827);
		vec3 c2 = palette == 1 ? vec3(0.490, 0.557, 0.639) : palette == 2 ? vec3(0.30, 0.29, 0.30) : vec3(0.561, 0.486, 0.400);
		if (d > bw) {
			float k = diag_checker(c, 0.8);
			a = mix(c2, c1, k);
			vec2 q = vec2(c.x + c.y, c.x - c.y) / 0.8;
			a = mix(a, vec3(0.714, 0.698, 0.651), max(lines(q.x, 0.01), lines(q.y, 0.01)) * 0.6);
		} else if (d > 0.0) {
			a = palette == 2 ? vec3(0.788, 0.541, 0.451) : vec3(0.231, 0.227, 0.239);
			float along = (h.x - abs(c.x) < h.y - abs(c.y)) ? c.y : c.x;
			float t = mod(along, 1.5) - 0.75;
			float across2 = d - bw * 0.5;
			if (abs(t) + abs(across2) < 0.26) a = vec3(0.925, 0.894, 0.816);
			if (abs(d - 0.05) < 0.02 || abs(d - (bw - 0.05)) < 0.02) a = vec3(0.847, 0.816, 0.741);
		} else {
			a = planks(c.x + 50.0, c.y);
		}
	} else {
		a = planks(wpos.x + 50.0, wpos.z);
	}

	// Polished-floor reflection (mirrored camera). Kept subtle on purpose:
	// a 9-tap blur hides aliasing in the half-res mirror image, bright sources
	// are clamped so windows and sky can't wash the floor out, and it fades
	// with distance so far floor doesn't turn milky.
	vec2 ruv = vec2(SCREEN_UV.x, 1.0 - SCREEN_UV.y);
	vec3 r = vec3(0.0);
	float wsum = 0.0;
	for (int i = -1; i <= 1; i++) {
		for (int j = -1; j <= 1; j++) {
			float w = (i == 0 ? 2.0 : 1.0) * (j == 0 ? 2.0 : 1.0);
			r += min(texture(refl_tex, ruv + vec2(float(i) * px.x, float(j) * px.y * 1.6)).rgb, vec3(refl_clamp)) * w;
			wsum += w;
		}
	}
	r /= wsum;
	float ndv = clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float fres = 0.04 + 0.96 * pow(1.0 - ndv, 5.0);
	float k = mix(0.12, 0.55, fres) * strength;
	float dist = length(VERTEX);
	k *= clamp(1.0 - (dist - 14.0) / 30.0, 0.25, 1.0);
	float lum = dot(a, vec3(0.3, 0.59, 0.11));
	k *= mix(1.25, 0.55, lum);   // dark tiles mirror more, as real terrazzo does
	ALBEDO = a * (1.0 - k * 0.35);
	ROUGHNESS = 0.35;
	SPECULAR = 0.25;
	EMISSION = r * k;
}
"""

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

func _ready() -> void:
	vp = SubViewport.new()
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.msaa_3d = Viewport.MSAA_DISABLED
	vp.positional_shadow_atlas_size = 0
	add_child(vp)
	mcam = Camera3D.new()
	vp.add_child(mcam)
	mcam.current = true
	var fsh := Shader.new()
	fsh.code = FLOOR
	var ish := Shader.new()
	ish.code = INTERIOR
	var imat := ShaderMaterial.new()
	imat.shader = ish
	imat.set_shader_parameter("shelf_tex", load("res://tex/int_side.png"))
	var cache := {}
	for mi in _meshes(get_tree().current_scene):
		var m: Mesh = mi.mesh
		for i in m.get_surface_count():
			var sm := m.surface_get_material(i)
			if sm == null:
				continue
			if sm.resource_name.begins_with("floorz_") and sm.has_meta("floor"):
				if not cache.has(sm.resource_name):
					var f: Dictionary = sm.get_meta("floor")
					var s := ShaderMaterial.new()
					s.shader = fsh
					s.set_shader_parameter("refl_tex", vp.get_texture())
					s.set_shader_parameter("strength", strength)
					s.set_shader_parameter("pattern", int(f.get("pattern", 0)))
					s.set_shader_parameter("axis", int(f.get("axis", 0)))
					s.set_shader_parameter("center", float(f.get("center", 0.0)))
					s.set_shader_parameter("half_w", float(f.get("half", 6.0)))
					s.set_shader_parameter("medallions", int(f.get("medallions", 0)))
					s.set_shader_parameter("court", Vector4(f.get("cx", 0.0), f.get("cz", 0.0), f.get("hx", 8.0), f.get("hz", 8.0)))
					s.set_shader_parameter("palette", int(f.get("palette", 0)))
					cache[sm.resource_name] = s
					floor_mats.append(s)
				mi.set_surface_override_material(i, cache[sm.resource_name])
			elif sm.resource_name == "int_wall":
				mi.set_surface_override_material(i, imat)
	_resize()
	get_viewport().size_changed.connect(_resize)

func _meshes(n: Node) -> Array:
	var out := []
	if n is MeshInstance3D and n.mesh:
		out.append(n)
	for c in n.get_children():
		out += _meshes(c)
	return out

var refl_on := true
var mode := "night"

## Night (default) or day: swaps the baked lightmap, sky and light set.
func set_time(m: String) -> void:
	mode = m
	load("res://scripts/time_of_day.gd").apply(get_tree().current_scene, m)
	# the ribbed vaults glow softly at night instead of reading as a lit ceiling
	set_reflections(refl_on)

func _set_emission(mat_name: String, e: float) -> void:
	for mi in _meshes(get_tree().current_scene):
		for i in mi.mesh.get_surface_count():
			var sm = mi.mesh.surface_get_material(i)
			if sm is StandardMaterial3D and sm.resource_name == mat_name:
				sm.emission_energy_multiplier = e

## Turn the floor reflection on or off (it costs a second render of the scene).
func set_reflections(on: bool) -> void:
	refl_on = on
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS if on else SubViewport.UPDATE_DISABLED
	var st := strength * 1.5 if mode == "night" else strength * 0.7
	for m in floor_mats:
		m.set_shader_parameter("strength", st if on else 0.0)

func _resize() -> void:
	var s := get_viewport().get_visible_rect().size
	vp.size = Vector2i(max(64, int(s.x * scale)), max(64, int(s.y * scale)))
	for m in floor_mats:
		m.set_shader_parameter("px", Vector2(1.5 / vp.size.x, 2.0 / vp.size.y))

func _process(_dt: float) -> void:
	var cam := get_viewport().get_camera_3d()
	if cam == null or cam == mcam:
		return
	var t := cam.global_transform
	var S := Basis(Vector3(1, 0, 0), Vector3(0, -1, 0), Vector3(0, 0, 1))
	var b := S * t.basis
	b.y = -b.y
	mcam.global_transform = Transform3D(b, Vector3(t.origin.x, -t.origin.y, t.origin.z))
	mcam.fov = cam.fov
	mcam.near = cam.near
	mcam.far = cam.far
