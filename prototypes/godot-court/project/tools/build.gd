## Builds res://main.tscn: the Shoe Dept. Encore court (1995 tenants) with its
## halls, as lightmappable static geometry plus dynamic props.
## Run: godot --headless --path . --script res://tools/build.gd
## Units are metres. +x east, +z south, +y up. Court centre is the origin.
extends SceneTree

const LANE_H = 4.6        # flat ceiling over the store lanes
const VAULT_SPRING = 4.9  # hall vault springing
const VAULT_RISE = 1.4
const VAULT_HALF = 3.0    # hall vault half-span
const HALL_HALF = 6.0     # hall half-width
const COURT = 8.0         # court half-size
const COURT_SPRING = 6.6
const COURT_RISE = 3.0
const SKY_HALF = 2.0      # skylight half-size
const RIB_STEP = 1.8
const TEXEL = 0.09        # lightmap texel size, metres

var mall: Node3D
var mats = {}
var acc = {}        # group name -> {mat name -> SurfaceTool}
var dyn_acc = {}    # dynamic (not baked) groups
var layout: Dictionary
var obstacles: Array = []   # [x, z, r] circles the player can't enter

# ------------------------------------------------------------------ materials
func tex(p: String) -> Texture2D:
	return load("res://tex/" + p)

func mat(name: String) -> StandardMaterial3D:
	if mats.has(name):
		return mats[name]
	var m = StandardMaterial3D.new()
	m.resource_name = name
	match name:
		"floor_court", "floor_hall", "floor_corridor":
			m.albedo_texture = tex(name + ".png")
			m.roughness = 0.14
			m.metallic_specular = 0.6
			m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		"plaster":
			m.albedo_texture = tex("plaster.png")
			m.uv1_scale = Vector3(1, 1, 1)
			m.roughness = 0.92
		"trim_tan":
			m.albedo_color = Color("#a98a62"); m.roughness = 0.8
		"cream":
			m.albedo_color = Color("#ece2cf"); m.roughness = 0.85
		"bulkhead":
			m.albedo_color = Color("#efe6d3"); m.roughness = 0.8
		"lane_ceiling":
			m.albedo_color = Color("#f0e9da"); m.roughness = 0.9
		"rib":
			m.albedo_color = Color("#fbf8f2"); m.roughness = 0.6
		"vault_glow":
			m.albedo_color = Color("#f3ead8"); m.roughness = 0.9
			m.emission_enabled = true; m.emission = Color("#fff1d6"); m.emission_energy_multiplier = 0.55
		"cove":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fff4e0"); m.emission_energy_multiplier = 6.0
		"downlight":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fff3df"); m.emission_energy_multiplier = 8.0
		"stone":
			m.albedo_texture = tex("stone.png"); m.roughness = 0.55
		"bronze":
			m.albedo_color = Color("#3a2f27"); m.metallic = 0.6; m.roughness = 0.4
		"int_wall":
			m.albedo_color = Color("#f4f0e8"); m.roughness = 0.9
			m.emission_enabled = true; m.emission = Color("#fffaf0"); m.emission_energy_multiplier = 0.25
		"int_floor":
			m.albedo_color = Color("#d8d2c6"); m.roughness = 0.5
		"int_panel":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fffaf2"); m.emission_energy_multiplier = 4.0
		"pink":
			m.albedo_color = Color("#dba9a0"); m.roughness = 0.8
		"plum":
			m.albedo_color = Color("#5a2340"); m.roughness = 0.6
		"white_pilaster":
			m.albedo_color = Color("#f5f0e8"); m.roughness = 0.7
		"column":
			m.albedo_color = Color("#f6f2ea"); m.roughness = 0.45
		"wood":
			m.albedo_texture = tex("wood_dark.png"); m.roughness = 0.45
		"metal_dark":
			m.albedo_color = Color("#262220"); m.metallic = 0.5; m.roughness = 0.45
		"planter":
			m.albedo_color = Color("#efe8da"); m.roughness = 0.35
		"soil":
			m.albedo_color = Color("#3a2a1f"); m.roughness = 1.0
		"bed_wood":
			m.albedo_texture = tex("wood_dark.png"); m.roughness = 0.6
			m.albedo_color = Color(1.25, 1.1, 1.0)
		"brass":
			m.albedo_color = Color("#b88d3e"); m.metallic = 1.0; m.roughness = 0.3
		"lantern_glass":
			m.albedo_color = Color("#ffe2b0")
			m.emission_enabled = true; m.emission = Color("#ffc977"); m.emission_energy_multiplier = 3.0
		"glass":
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.albedo_color = Color(0.82, 0.9, 0.92, 0.07)
			m.roughness = 0.04; m.metallic = 0.0; m.metallic_specular = 0.25
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"skyglass":
			m.albedo_color = Color("#eef6ff")
			m.emission_enabled = true; m.emission = Color("#dfeeff"); m.emission_energy_multiplier = 2.5
			m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		"palm", "poinsettia", "leafy":
			m.albedo_texture = tex({"palm": "palm_frond.png", "poinsettia": "poinsettia.png", "leafy": "leafy.png"}[name])
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.alpha_scissor_threshold = 0.5
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.7
			m.backlight_enabled = false
		"trunk":
			m.albedo_color = Color("#6d5a3e"); m.roughness = 0.95
		"outside_ground":
			m.albedo_color = Color("#7c7a74"); m.roughness = 0.95
		_:
			if name.begins_with("c#"):
				m.albedo_color = Color(name.substr(2)); m.roughness = 0.5
			elif name.begins_with("e#"):
				m.albedo_color = Color(name.substr(2))
				m.emission_enabled = true; m.emission = Color(name.substr(2)); m.emission_energy_multiplier = 0.6
			elif name.begins_with("int_"):
				m.albedo_texture = tex(name + ".png")
				m.emission_enabled = true; m.emission_texture = m.albedo_texture
				m.emission = Color.WHITE; m.emission_energy_multiplier = 0.45
				m.roughness = 0.8
			else:
				push_error("unknown material " + name)
	mats[name] = m
	return m

# ------------------------------------------------------------- mesh helpers
func st(group: String, mname: String, dynamic = false) -> SurfaceTool:
	var A: Dictionary = dyn_acc if dynamic else acc
	if not A.has(group):
		A[group] = {}
	if not A[group].has(mname):
		var s = SurfaceTool.new()
		s.begin(Mesh.PRIMITIVE_TRIANGLES)
		A[group][mname] = s
	return A[group][mname]

## Triangle with outward normal n; winding is fixed up for Godot (clockwise front).
func tri(s: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, ua: Vector2, ub: Vector2, uc: Vector2, n: Vector3) -> void:
	if (b - a).cross(c - a).dot(n) > 0.0:
		var t = b; b = c; c = t
		var tu = ub; ub = uc; uc = tu
	for p in [[a, ua], [b, ub], [c, uc]]:
		s.set_normal(n)
		s.set_uv(p[1])
		s.add_vertex(p[0])

## Quad p0..p3 (in order around), uv by world projection unless given.
func quad(group: String, mname: String, p: Array, n: Vector3, uvs: Array = [], dynamic = false, uvscale = 1.0) -> void:
	var s = st(group, mname, dynamic)
	if uvs.is_empty():
		for v in p:
			uvs.append(proj_uv(v, n) * uvscale)
	tri(s, p[0], p[1], p[2], uvs[0], uvs[1], uvs[2], n)
	tri(s, p[0], p[2], p[3], uvs[0], uvs[2], uvs[3], n)

func proj_uv(v: Vector3, n: Vector3) -> Vector2:
	var an = n.abs()
	if an.y >= an.x and an.y >= an.z:
		return Vector2(v.x, v.z)
	elif an.x >= an.z:
		return Vector2(v.z, -v.y)
	return Vector2(v.x, -v.y)

## Axis-aligned box (optionally transformed). skip: faces to omit ("-y" etc.)
func box(group: String, mname: String, c: Vector3, size: Vector3, xf = Transform3D.IDENTITY, skip: Array = [], dynamic = false, uvscale = 1.0) -> void:
	var h = size * 0.5
	var faces = {
		"+x": [Vector3(1, 0, 0), [Vector3(h.x, -h.y, -h.z), Vector3(h.x, h.y, -h.z), Vector3(h.x, h.y, h.z), Vector3(h.x, -h.y, h.z)]],
		"-x": [Vector3(-1, 0, 0), [Vector3(-h.x, -h.y, h.z), Vector3(-h.x, h.y, h.z), Vector3(-h.x, h.y, -h.z), Vector3(-h.x, -h.y, -h.z)]],
		"+y": [Vector3(0, 1, 0), [Vector3(-h.x, h.y, -h.z), Vector3(-h.x, h.y, h.z), Vector3(h.x, h.y, h.z), Vector3(h.x, h.y, -h.z)]],
		"-y": [Vector3(0, -1, 0), [Vector3(-h.x, -h.y, h.z), Vector3(-h.x, -h.y, -h.z), Vector3(h.x, -h.y, -h.z), Vector3(h.x, -h.y, h.z)]],
		"+z": [Vector3(0, 0, 1), [Vector3(h.x, -h.y, h.z), Vector3(h.x, h.y, h.z), Vector3(-h.x, h.y, h.z), Vector3(-h.x, -h.y, h.z)]],
		"-z": [Vector3(0, 0, -1), [Vector3(-h.x, -h.y, -h.z), Vector3(-h.x, h.y, -h.z), Vector3(h.x, h.y, -h.z), Vector3(h.x, -h.y, -h.z)]],
	}
	for k in faces:
		if k in skip:
			continue
		var n: Vector3 = xf.basis * faces[k][0]
		var pts = []
		for q in faces[k][1]:
			pts.append(xf * (c + q))
		quad(group, mname, pts, n.normalized(), [], dynamic, uvscale)

## Cylinder along y. caps: draw top/bottom.
func cyl(group: String, mname: String, base: Vector3, r0: float, r1: float, hgt: float, seg = 20, top = true, bottom = false, dynamic = false) -> void:
	var s = st(group, mname, dynamic)
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var d0 = Vector3(cos(a0), 0, sin(a0))
		var d1 = Vector3(cos(a1), 0, sin(a1))
		var p0 = base + d0 * r0
		var p1 = base + d1 * r0
		var p2 = base + d1 * r1 + Vector3(0, hgt, 0)
		var p3 = base + d0 * r1 + Vector3(0, hgt, 0)
		var slope = (r0 - r1) / max(hgt, 0.001)
		var n0 = (d0 + Vector3(0, slope, 0)).normalized()
		var n1 = (d1 + Vector3(0, slope, 0)).normalized()
		var u0 = float(i) / seg * 2.0
		var u1 = float(i + 1) / seg * 2.0
		# per-vertex smooth normals
		_tri_n(s, [p0, p1, p2], [n0, n1, n1], [Vector2(u0, 1), Vector2(u1, 1), Vector2(u1, 0)], (n0 + n1).normalized())
		_tri_n(s, [p0, p2, p3], [n0, n1, n0], [Vector2(u0, 1), Vector2(u1, 0), Vector2(u0, 0)], (n0 + n1).normalized())
		if top:
			var c = base + Vector3(0, hgt, 0)
			tri(s, c, p3, p2, Vector2(0.5, 0.5), Vector2(0.5 + d0.x * 0.5, 0.5 + d0.z * 0.5), Vector2(0.5 + d1.x * 0.5, 0.5 + d1.z * 0.5), Vector3.UP)
		if bottom:
			tri(s, base, p0, p1, Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector3.DOWN)

func _tri_n(s: SurfaceTool, p: Array, n: Array, uv: Array, face_n: Vector3) -> void:
	var order = [0, 1, 2]
	if (p[1] - p[0]).cross(p[2] - p[0]).dot(face_n) > 0.0:
		order = [0, 2, 1]
	for i in order:
		s.set_normal(n[i]); s.set_uv(uv[i]); s.add_vertex(p[i])

## Flat polygon (2D outline in a plane): origin o, axes ax (u) and ay (v), normal n.
func poly(group: String, mname: String, outline: PackedVector2Array, o: Vector3, ax: Vector3, ay: Vector3, n: Vector3) -> void:
	var idx = Geometry2D.triangulate_polygon(outline)
	if idx.is_empty():
		push_error("triangulation failed for " + group)
		return
	var s = st(group, mname)
	for i in range(0, idx.size(), 3):
		var pts = []
		var uvs = []
		for j in 3:
			var q = outline[idx[i + j]]
			pts.append(o + ax * q.x + ay * q.y)
			uvs.append(Vector2(q.x, -q.y) * 0.25)
		tri(s, pts[0], pts[1], pts[2], uvs[0], uvs[1], uvs[2], n)

# --------------------------------------------------------------- vault math
## Segmental arch: returns points (u, y) across the span, u from -half to +half.
func arch_pts(half: float, spring: float, rise: float, seg: int) -> Array:
	var R = (half * half + rise * rise) / (2.0 * rise)
	var cy = spring + rise - R
	var th = asin(half / R)
	var out = []
	for i in seg + 1:
		var a = -th + 2.0 * th * i / seg
		out.append(Vector2(R * sin(a), cy + R * cos(a)))
	return out

func arch_y(u: float, half: float, spring: float, rise: float) -> float:
	var R = (half * half + rise * rise) / (2.0 * rise)
	var cy = spring + rise - R
	return cy + sqrt(max(R * R - u * u, 0.0))

## A hall section between s0 and s1 along an axis. axis "z" (N-S hall) or "x".
## cross: centre of the hall in the other coordinate. Builds lane ceilings,
## fascias, cove strips, the vault and its ribs.
func hall_ceiling(group: String, axis: String, s0: float, s1: float, cross: float) -> void:
	var P = func(u: float, y: float, s: float) -> Vector3:
		return Vector3(cross + u, y, s) if axis == "z" else Vector3(s, y, cross + u)
	var lo: float = min(s0, s1)
	var hi: float = max(s0, s1)
	# lane ceilings
	for side in [-1.0, 1.0]:
		var a: float = side * VAULT_HALF
		var b: float = side * HALL_HALF
		quad(group, "lane_ceiling", [P.call(a, LANE_H, lo), P.call(b, LANE_H, lo), P.call(b, LANE_H, hi), P.call(a, LANE_H, hi)], Vector3.DOWN)
		# fascia facing the hall centre
		var nf = (P.call(-side, 0, 0) - P.call(0, 0, 0)).normalized()
		quad(group, "bulkhead", [P.call(a, LANE_H, lo), P.call(a, VAULT_SPRING, lo), P.call(a, VAULT_SPRING, hi), P.call(a, LANE_H, hi)], nf)
		# downlights every 3 m along the lane
		var s = lo + 1.5
		while s < hi - 0.5:
			var c: Vector3 = P.call(side * (VAULT_HALF + HALL_HALF) * 0.5, LANE_H - 0.01, s)
			cyl_down(group, c, 0.18)
			add_downlight(c)
			s += 3.0
	# vault surface
	var pts = arch_pts(VAULT_HALF, VAULT_SPRING, VAULT_RISE, 16)
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var mid = (a + b) * 0.5
		# normal points toward arc centre (down/inward)
		var R = (VAULT_HALF * VAULT_HALF + VAULT_RISE * VAULT_RISE) / (2.0 * VAULT_RISE)
		var cy = VAULT_SPRING + VAULT_RISE - R
		var nn: Vector3 = (P.call(0, cy, 0) - P.call(mid.x, mid.y, 0)).normalized()
		quad(group, "vault_glow", [P.call(a.x, a.y, lo), P.call(b.x, b.y, lo), P.call(b.x, b.y, hi), P.call(a.x, a.y, hi)], nn, [Vector2(a.x, lo), Vector2(b.x, lo), Vector2(b.x, hi), Vector2(a.x, hi)])
	# ribs
	var r = lo + RIB_STEP * 0.5
	while r < hi:
		rib(group, axis, cross, r, pts)
		r += RIB_STEP

func cyl_down(group: String, c: Vector3, rad: float) -> void:
	# a flush round downlight: emissive disc a hair below the ceiling
	var s = st(group, "downlight")
	var seg = 12
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		tri(s, c, c + Vector3(cos(a0), 0, sin(a0)) * rad, c + Vector3(cos(a1), 0, sin(a1)) * rad, Vector2(0.5, 0.5), Vector2(0, 0), Vector2(1, 0), Vector3.DOWN)

func rib(group: String, axis: String, cross: float, at: float, pts: Array) -> void:
	var P = func(u: float, y: float, s: float) -> Vector3:
		return Vector3(cross + u, y, s) if axis == "z" else Vector3(s, y, cross + u)
	var w = 0.07
	var depth = 0.22
	var R = (VAULT_HALF * VAULT_HALF + VAULT_RISE * VAULT_RISE) / (2.0 * VAULT_RISE)
	var cy = VAULT_SPRING + VAULT_RISE - R
	var ax: Vector3 = (P.call(0, 0, 1) - P.call(0, 0, 0))
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var ia = Vector2(a.x, a.y) + (Vector2(0, cy) - a).normalized() * depth
		var ib = Vector2(b.x, b.y) + (Vector2(0, cy) - b).normalized() * depth
		var mid = (ia + ib) * 0.5
		var nn: Vector3 = (P.call(0, cy, 0) - P.call(mid.x, mid.y, 0)).normalized()
		# underside
		quad(group, "rib", [P.call(ia.x, ia.y, at - w), P.call(ib.x, ib.y, at - w), P.call(ib.x, ib.y, at + w), P.call(ia.x, ia.y, at + w)], nn)
		# two sides
		for sg in [-1.0, 1.0]:
			quad(group, "rib", [P.call(a.x, a.y, at + sg * w), P.call(b.x, b.y, at + sg * w), P.call(ib.x, ib.y, at + sg * w), P.call(ia.x, ia.y, at + sg * w)], ax * sg)

## Outline of the hall cross-section opening (u across, y up), floor to vault.
func hall_section_outline(seg = 16) -> PackedVector2Array:
	var o = PackedVector2Array()
	o.append(Vector2(HALL_HALF, 0))
	o.append(Vector2(HALL_HALF, LANE_H))
	o.append(Vector2(VAULT_HALF, LANE_H))
	var pts = arch_pts(VAULT_HALF, VAULT_SPRING, VAULT_RISE, seg)
	pts.reverse()
	for p in pts:
		o.append(p)
	o.append(Vector2(-VAULT_HALF, LANE_H))
	o.append(Vector2(-HALL_HALF, LANE_H))
	o.append(Vector2(-HALL_HALF, 0))
	return o

## Closed arched end wall of a hall above the lane ceiling height.
func hall_end(group: String, axis: String, at: float, cross: float, facing: float) -> void:
	var o = PackedVector2Array()
	o.append(Vector2(-VAULT_HALF, LANE_H))
	for p in arch_pts(VAULT_HALF, VAULT_SPRING, VAULT_RISE, 16):
		o.append(p)
	o.append(Vector2(VAULT_HALF, LANE_H))
	var origin: Vector3
	var ax: Vector3
	var n: Vector3
	if axis == "z":
		origin = Vector3(cross, 0, at); ax = Vector3(1, 0, 0); n = Vector3(0, 0, facing)
	else:
		origin = Vector3(at, 0, cross); ax = Vector3(0, 0, 1); n = Vector3(facing, 0, 0)
	poly(group, "cream", o, origin, ax, Vector3.UP, n)
	# white trim arch just inside the end wall
	var pts = arch_pts(VAULT_HALF, VAULT_SPRING, VAULT_RISE, 16)
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var off = n * 0.12
		var R = (VAULT_HALF * VAULT_HALF + VAULT_RISE * VAULT_RISE) / (2.0 * VAULT_RISE)
		var cy = VAULT_SPRING + VAULT_RISE - R
		var ia = a + (Vector2(0, cy) - a).normalized() * 0.3
		var ib = b + (Vector2(0, cy) - b).normalized() * 0.3
		quad(group, "rib", [origin + ax * a.x + Vector3.UP * a.y + off, origin + ax * b.x + Vector3.UP * b.y + off, origin + ax * ib.x + Vector3.UP * ib.y + off, origin + ax * ia.x + Vector3.UP * ia.y + off], n)

# ------------------------------------------------------------------ lights
var light_root: Node3D

func add_downlight(c: Vector3) -> void:
	var l = SpotLight3D.new()
	l.position = c + Vector3(0, -0.05, 0)
	l.rotation = Vector3(-PI / 2, 0, 0)
	l.spot_angle = 55.0
	l.spot_attenuation = 0.8
	l.spot_range = 7.0
	l.light_energy = 1.4
	l.light_color = Color(1.0, 0.92, 0.80)
	l.light_bake_mode = Light3D.BAKE_STATIC
	l.light_indirect_energy = 1.0
	light_root.add_child(l)

func add_omni(p: Vector3, energy: float, rng: float, col: Color, shadow = false) -> void:
	var l = OmniLight3D.new()
	l.position = p
	l.omni_range = rng
	l.light_energy = energy
	l.light_color = col
	l.light_bake_mode = Light3D.BAKE_STATIC
	l.shadow_enabled = shadow
	light_root.add_child(l)

# -------------------------------------------------------------- storefronts
func store(sd: Dictionary) -> void:
	var a = Vector3(sd.a[0], 0, sd.a[1])
	var b = Vector3(sd.b[0], 0, sd.b[1])
	var n = Vector3(sd.n[0], 0, sd.n[1])
	var t = (b - a).normalized()
	var L = a.distance_to(b)
	var g = "store_" + sd.id
	var deep = 9.0 if L > 10.0 else 5.5
	var pil = 0.4
	var open_h = 3.2
	var bulk_top = LANE_H
	# pilasters at both ends: cream with a grey stone base
	for e in [0.0, L - pil]:
		var c0 = a + t * (e + pil * 0.5)
		box(g, "stone", c0 + Vector3(0, 0.45, 0) + n * 0.06, abs_size(t, pil, 0.9, 0.12, n))
		box(g, "cream", c0 + Vector3(0, (open_h + 0.9) * 0.5 + 0.0, 0) + n * 0.03, abs_size(t, pil, open_h - 0.9, 0.06, n), Transform3D.IDENTITY, [])
	# bulkhead (sign band) across the full width
	var mid = a + t * L * 0.5
	box(g, "bulkhead", mid + Vector3(0, (open_h + bulk_top) * 0.5, 0) + n * 0.08, abs_size(t, L, bulk_top - open_h, 0.16, n))
	# sign panel + lettering
	var sw: float = min(L - 1.2, max(2.2, min(L * 0.7, 6.5)))
	var sign_c = mid + Vector3(0, open_h + (bulk_top - open_h) * 0.5, 0) + n * 0.2
	box(g, "c" + sd.bg, sign_c, abs_size(t, sw, 0.78, 0.08, n))
	var lab = Label3D.new()
	lab.text = sd.sign
	var fnt: Font = load("res://fonts/" + {"sans": "sans.otf", "serif": "serif.ttf", "script": "script.ttf"}[sd.font])
	lab.font = fnt
	lab.font_size = 128
	lab.outline_size = 0
	lab.modulate = Color(sd.fg)
	var txt_w = max(fnt.get_string_size(sd.sign, HORIZONTAL_ALIGNMENT_LEFT, -1, 128).x, sd.sign.length() * 128 * (0.66 if sd.font == "serif" else 0.58))
	var px = 0.42 / 128.0
	if txt_w * px > sw * 0.88:
		px = sw * 0.88 / txt_w
	lab.pixel_size = px
	lab.double_sided = false
	lab.shaded = false
	lab.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	lab.position = sign_c + n * 0.05
	lab.basis = Basis.looking_at(-n, Vector3.UP)
	mall.add_child(lab)
	# storefront: low stone kick base, bronze mullions, glass, centre doorway
	var inner0 = pil
	var inner1 = L - pil
	var door_w: float = min(3.0, (inner1 - inner0) * 0.45)
	var d0 = L * 0.5 - door_w * 0.5
	var d1 = L * 0.5 + door_w * 0.5
	for seg in [[inner0, d0], [d1, inner1]]:
		var s0: float = seg[0]
		var s1: float = seg[1]
		if s1 - s0 < 0.1:
			continue
		var cc = a + t * (s0 + s1) * 0.5
		box(g, "stone", cc + Vector3(0, 0.2, 0), abs_size(t, s1 - s0, 0.4, 0.2, n))
		# glass (dynamic, not baked)
		var gp = [a + t * s0 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, open_h, 0), a + t * s0 + Vector3(0, open_h, 0)]
		quad("glass", "glass", gp, n, [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
		# mullions every ~1.5 m
		var cnt: int = max(1, int(round((s1 - s0) / 1.5)))
		for k in cnt + 1:
			var mp = a + t * (s0 + (s1 - s0) * k / cnt)
			box(g, "bronze", mp + Vector3(0, (open_h + 0.4) * 0.5, 0), abs_size(t, 0.06, open_h - 0.4, 0.1, n))
	# top rail and door header
	box(g, "bronze", mid + Vector3(0, open_h - 0.04, 0), abs_size(t, inner1 - inner0, 0.08, 0.12, n))
	# interior box: back wall with merchandise, side walls, ceiling with light panels
	var back = -n * deep
	var p0 = a + t * inner0
	var p1 = a + t * inner1
	quad(g, "int_" + sd.id, [p0 + back, p1 + back, p1 + back + Vector3(0, open_h, 0), p0 + back + Vector3(0, open_h, 0)], n, [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	quad(g, "int_wall", [p0, p0 + back, p0 + back + Vector3(0, open_h, 0), p0 + Vector3(0, open_h, 0)], t)
	quad(g, "int_wall", [p1 + back, p1, p1 + Vector3(0, open_h, 0), p1 + back + Vector3(0, open_h, 0)], -t)
	quad(g, "int_floor", [p0, p1, p1 + back, p0 + back], Vector3.UP)
	quad(g, "int_wall", [p0 + Vector3(0, open_h, 0), p0 + back + Vector3(0, open_h, 0), p1 + back + Vector3(0, open_h, 0), p1 + Vector3(0, open_h, 0)], Vector3.DOWN)
	# light panels
	var rows: int = max(1, int(deep / 2.5))
	var cols: int = max(1, int((inner1 - inner0) / 2.5))
	for ri in rows:
		for ci in cols:
			var pc = p0 + t * ((inner1 - inner0) * (ci + 0.5) / cols) - n * (deep * (ri + 0.5) / rows) + Vector3(0, open_h - 0.01, 0)
			quad(g, "int_panel", [pc - t * 0.5 - n * 0.3, pc + t * 0.5 - n * 0.3, pc + t * 0.5 + n * 0.3, pc - t * 0.5 + n * 0.3], Vector3.DOWN)
	# display fixtures inside (low tables / racks in merch colors)
	var mc: Array = sd.merch
	for k in max(1, int((inner1 - inner0) / 2.8)):
		var fc = p0 + t * (1.4 + k * 2.8) - n * (deep * 0.45)
		if t.dot(fc - p0) > inner1 - inner0 - 0.8:
			break
		box(g, "c" + String(mc[k % mc.size()]), fc + Vector3(0, 0.45, 0), abs_size(t, 1.2, 0.9, 0.8, n))
	add_omni(a + t * L * 0.5 - n * deep * 0.5 + Vector3(0, open_h - 0.4, 0), 1.2, deep + 2.0, Color(1.0, 0.97, 0.9))
	obstacles.append(["seg", [a.x, a.z], [b.x, b.z], [n.x, n.z]])

## Box size given an along-axis t, length, height, depth along n.
func abs_size(t: Vector3, along: float, hgt: float, depth: float, n: Vector3) -> Vector3:
	var v = t.abs() * along + n.abs() * depth
	return Vector3(max(v.x, 0.001), hgt, max(v.z, 0.001))

# ------------------------------------------------------------------- walls
## Plain wall from a to b (x,z) facing n, floor to LANE_H, with stone base.
func plain_wall(g: String, a2: Vector2, b2: Vector2, n2: Vector2, top = LANE_H, mname = "cream") -> void:
	var a = Vector3(a2.x, 0, a2.y)
	var b = Vector3(b2.x, 0, b2.y)
	var n = Vector3(n2.x, 0, n2.y)
	quad(g, mname, [a, b, b + Vector3(0, top, 0), a + Vector3(0, top, 0)], n)
	var t = (b - a).normalized()
	box(g, "stone", (a + b) * 0.5 + Vector3(0, 0.3, 0) + n * 0.03, abs_size(t, a.distance_to(b), 0.6, 0.06, n))

## K&B's mall-facing wall: pink with plum stripes and white pilasters (0:50-0:56).
func kb_wall(g: String, z0: float, z1: float) -> void:
	var x = HALL_HALF
	var n = Vector3(-1, 0, 0)
	quad(g, "pink", [Vector3(x, 0, z0), Vector3(x, 0, z1), Vector3(x, LANE_H, z1), Vector3(x, LANE_H, z0)], n)
	for y in [1.0, 2.35]:
		box(g, "plum", Vector3(x - 0.015, y, (z0 + z1) * 0.5), Vector3(0.03, 0.16, abs(z1 - z0)))
	var z: float = min(z0, z1) + 0.3
	while z < max(z0, z1):
		box(g, "white_pilaster", Vector3(x - 0.15, LANE_H * 0.5, z), Vector3(0.3, LANE_H, 0.6))
		for y in [1.0, 2.35]:
			box(g, "plum", Vector3(x - 0.31, y, z), Vector3(0.02, 0.16, 0.62))
		z += 4.0

# ------------------------------------------------------------------ props
func bench(group: String, at: Vector3, yaw: float) -> void:
	var xf = Transform3D(Basis(Vector3.UP, yaw), at)
	var L = 1.7
	for i in 5:
		box(group, "wood", Vector3(0, 0.44, -0.2 + i * 0.105), Vector3(L, 0.035, 0.085), xf, [], false, 1.0)
	# curved back: slats on an arc behind the seat
	for i in 4:
		var a = deg_to_rad(-12 + i * 9)
		var c = Vector3(0, 0.62 + i * 0.105, 0.29 + sin(a) * 0.12 + i * 0.012)
		var bx = xf * Transform3D(Basis(Vector3.RIGHT, -0.25 - i * 0.06), c)
		box(group, "wood", Vector3.ZERO, Vector3(L, 0.085, 0.03), bx)
	for e in [-L * 0.5 + 0.08, L * 0.5 - 0.08]:
		box(group, "metal_dark", Vector3(e, 0.22, -0.1), Vector3(0.05, 0.44, 0.05), xf)
		box(group, "metal_dark", Vector3(e, 0.4, 0.3), Vector3(0.05, 0.8, 0.05), xf)
		box(group, "metal_dark", Vector3(e, 0.62, 0.0), Vector3(0.06, 0.04, 0.5), xf)
		box(group, "metal_dark", Vector3(e, 0.05, 0.1), Vector3(0.06, 0.04, 0.55), xf)
	obstacles.append([at.x, at.z, 0.85])

func planter(group: String, at: Vector3, kind: String) -> void:
	cyl(group, "planter", at, 0.42, 0.46, 0.62, 24, false)
	cyl(group, "soil", at + Vector3(0, 0.56, 0), 0.4, 0.4, 0.001, 18, true)
	if kind == "palm":
		palm(at + Vector3(0, 0.56, 0), 1.6)
	else:
		bush(at + Vector3(0, 0.56, 0), "leafy", 0.75, 5)
	obstacles.append([at.x, at.z, 0.6])

func trash(group: String, at: Vector3) -> void:
	cyl(group, "planter", at, 0.24, 0.28, 0.82, 20, false)
	cyl(group, "planter", at + Vector3(0, 0.82, 0), 0.29, 0.29, 0.05, 20, false)
	cyl(group, "planter", at + Vector3(0, 0.87, 0), 0.29, 0.12, 0.12, 20, true)
	obstacles.append([at.x, at.z, 0.45])

func palm(base: Vector3, hgt: float) -> void:
	var g = "foliage"
	cyl(g, "trunk", base, 0.07, 0.05, hgt, 8, false, false, true)
	var top = base + Vector3(0, hgt, 0)
	var n = 9
	for i in n:
		var yaw = TAU * i / n + randf() * 0.3
		var lenf = 1.3 + randf() * 0.4
		frond(top, yaw, lenf, deg_to_rad(35 + randf() * 25))

func frond(top: Vector3, yaw: float, L: float, up: float) -> void:
	var s = st("foliage", "palm", true)
	var dir = Vector3(cos(yaw), 0, sin(yaw))
	var side = Vector3(-dir.z, 0, dir.x)
	var segs = 6
	var prev_l: Vector3
	var prev_r: Vector3
	var prev_c = top
	for i in segs + 1:
		var f = float(i) / segs
		var ang = up - f * 1.6 * up - f * f * 0.9
		var c = top
		if i > 0:
			var step = L / segs
			c = prev_c + (dir * cos(ang) + Vector3.UP * sin(ang)) * step
		var w = 0.32 * sin(PI * (0.15 + 0.85 * f)) + 0.04
		var lft = c + side * w + Vector3(0, -w * 0.35, 0)
		var rgt = c - side * w + Vector3(0, -w * 0.35, 0)
		if i > 0:
			var nn = (dir * -sin(ang) + Vector3.UP * cos(ang)).normalized()
			var v0 = float(i - 1) / segs
			var v1 = f
			tri(s, prev_l, prev_r, rgt, Vector2(0, v0), Vector2(1, v0), Vector2(1, v1), nn)
			tri(s, prev_l, rgt, lft, Vector2(0, v0), Vector2(1, v1), Vector2(0, v1), nn)
		prev_l = lft; prev_r = rgt; prev_c = c

func bush(base: Vector3, mname: String, size: float, cards: int) -> void:
	var s = st("foliage", mname, true)
	for i in cards:
		var yaw = PI * i / cards
		var d = Vector3(cos(yaw), 0, sin(yaw)) * size
		var tilt = Vector3(0, size * 0.9, 0)
		var p0 = base - d + Vector3(0, 0.02, 0)
		var p1 = base + d + Vector3(0, 0.02, 0)
		tri(s, p0, p1, p1 + tilt, Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector3(-d.z, 0.3, d.x).normalized())
		tri(s, p0, p1 + tilt, p0 + tilt, Vector2(0, 1), Vector2(1, 0), Vector2(0, 0), Vector3(-d.z, 0.3, d.x).normalized())
	# a flat cap card for a fuller top
	var c = base + Vector3(0, size * 0.75, 0)
	tri(s, c + Vector3(-size, 0, -size), c + Vector3(size, 0, -size), c + Vector3(size, 0, size), Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector3.UP)
	tri(s, c + Vector3(-size, 0, -size), c + Vector3(size, 0, size), c + Vector3(-size, 0, size), Vector2(0, 0), Vector2(1, 1), Vector2(0, 1), Vector3.UP)

## Low wood-sided palm bed with poinsettias (0:36). Benches back onto it.
func palm_bed(group: String, at: Vector3, sx: float, sz: float) -> void:
	var h = 0.42
	box(group, "bed_wood", at + Vector3(0, h * 0.5, 0), Vector3(sx, h, sz), Transform3D.IDENTITY, ["-y"])
	box(group, "soil", at + Vector3(0, h + 0.005, 0), Vector3(sx - 0.1, 0.01, sz - 0.1), Transform3D.IDENTITY, ["-y"])
	# poinsettias in rows, two palms
	var nx = int(sx / 0.6)
	var nz = int(sz / 0.6)
	for i in nx:
		for j in nz:
			var p = at + Vector3(-sx * 0.5 + 0.3 + i * (sx - 0.6) / max(1, nx - 1), h, -sz * 0.5 + 0.3 + j * (sz - 0.6) / max(1, nz - 1))
			if abs(p.x - at.x) < 0.6 and abs(p.z - at.z) < sz * 0.3:
				continue
			bush(p, "poinsettia", 0.28, 3)
	palm(at + Vector3(0, h, -sz * 0.22), 2.4)
	palm(at + Vector3(0, h, sz * 0.22), 1.9)
	obstacles.append(["rect", at.x - sx * 0.5 - 0.3, at.z - sz * 0.5 - 0.3, at.x + sx * 0.5 + 0.3, at.z + sz * 0.5 + 0.3])

func lantern(at: Vector3, top_y: float) -> void:
	var g = "lanterns"
	cyl(g, "brass", Vector3(at.x, at.y + 0.55, at.z), 0.015, 0.015, top_y - at.y - 0.55, 6, false)
	# octagonal lantern body 0.5 wide x 0.75 tall
	cyl(g, "lantern_glass", at + Vector3(0, -0.2, 0), 0.2, 0.24, 0.6, 8, false, false)
	for i in 8:
		var a = TAU * i / 8
		var p = at + Vector3(cos(a) * 0.245, 0.1, sin(a) * 0.245)
		box(g, "brass", p, Vector3(0.025, 0.66, 0.025))
	cyl(g, "brass", at + Vector3(0, 0.4, 0), 0.27, 0.05, 0.18, 8, true)
	cyl(g, "brass", at + Vector3(0, -0.24, 0), 0.24, 0.26, 0.05, 8, true, true)
	cyl(g, "brass", at + Vector3(0, -0.36, 0), 0.02, 0.09, 0.12, 8, false, true)
	add_omni(at + Vector3(0, -0.05, 0), 1.6, 9.0, Color(1.0, 0.82, 0.58), false)

# ------------------------------------------------------------------- floors
func floor_rect(g: String, mname: String, x0: float, z0: float, x1: float, z1: float, uvf: Callable) -> void:
	var p = [Vector3(x0, 0, z0), Vector3(x1, 0, z0), Vector3(x1, 0, z1), Vector3(x0, 0, z1)]
	var uvs = []
	for v in p:
		uvs.append(uvf.call(v))
	quad(g, mname, p, Vector3.UP, uvs)

# ------------------------------------------------------------------ the court
func build_court() -> void:
	var g = "court"
	floor_rect(g, "floor_court", -COURT, -COURT, COURT, COURT, func(v): return Vector2((v.x + COURT) / 16.0, (v.z + COURT) / 16.0))
	# vault spans x (16 m), runs along z, springs from the x = +/-8 walls
	var pts = arch_pts(COURT, COURT_SPRING, COURT_RISE, 40)
	var R = (COURT * COURT + COURT_RISE * COURT_RISE) / (2.0 * COURT_RISE)
	var cy = COURT_SPRING + COURT_RISE - R
	var zs = []
	var z = -COURT
	while z < COURT - 0.001:
		zs.append(z); z += 1.0
	zs.append(COURT)
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var mid = (a + b) * 0.5
		var nn = (Vector3(0, cy, 0) - Vector3(mid.x, mid.y, 0)).normalized()
		for k in zs.size() - 1:
			var z0: float = zs[k]
			var z1: float = zs[k + 1]
			if abs(mid.x) < SKY_HALF and abs((z0 + z1) * 0.5) < SKY_HALF:
				continue
			var arc_a = R * asin(a.x / R)
			var arc_b = R * asin(b.x / R)
			quad(g, "plaster", [Vector3(a.x, a.y, z0), Vector3(b.x, b.y, z0), Vector3(b.x, b.y, z1), Vector3(a.x, a.y, z1)], nn,
				[Vector2(arc_a, z0) * 0.22, Vector2(arc_b, z0) * 0.22, Vector2(arc_b, z1) * 0.22, Vector2(arc_a, z1) * 0.22])
	# skylight well: four walls from the vault up to the glass
	var top = COURT_SPRING + COURT_RISE + 0.9
	var ys = arch_y(SKY_HALF, COURT, COURT_SPRING, COURT_RISE)
	for sgn in [-1.0, 1.0]:
		# walls on x = +/-2 (facing in)
		quad(g, "lane_ceiling", [Vector3(sgn * SKY_HALF, ys - 0.05, -SKY_HALF), Vector3(sgn * SKY_HALF, ys - 0.05, SKY_HALF), Vector3(sgn * SKY_HALF, top, SKY_HALF), Vector3(sgn * SKY_HALF, top, -SKY_HALF)], Vector3(-sgn, 0, 0))
		# walls on z = +/-2: bottom edge follows the vault curve
		var o = PackedVector2Array()
		var segs = 8
		for i in segs + 1:
			var u = -SKY_HALF + 2.0 * SKY_HALF * i / segs
			o.append(Vector2(u, arch_y(u, COURT, COURT_SPRING, COURT_RISE) - 0.05))
		o.append(Vector2(SKY_HALF, top)); o.append(Vector2(-SKY_HALF, top))
		poly(g, "lane_ceiling", o, Vector3(0, 0, sgn * SKY_HALF), Vector3(1, 0, 0), Vector3.UP, Vector3(0, 0, -sgn))
	# skylight frame (muntins) - dynamic so it doesn't block the bake much
	for i in 5:
		var u = -SKY_HALF + i * SKY_HALF * 0.5
		box("glass_frames", "metal_dark", Vector3(u, top - 0.05, 0), Vector3(0.05, 0.1, SKY_HALF * 2), Transform3D.IDENTITY, [], true)
		box("glass_frames", "metal_dark", Vector3(0, top - 0.05, u), Vector3(SKY_HALF * 2, 0.1, 0.05), Transform3D.IDENTITY, [], true)
	# west wall: above Woolworth's bulkhead, a band of wall, the clerestory, a trim
	var x = -COURT
	quad(g, "plaster", [Vector3(x, LANE_H, COURT), Vector3(x, LANE_H, -COURT), Vector3(x, 5.0, -COURT), Vector3(x, 5.0, COURT)], Vector3(1, 0, 0), [], false, 0.25)
	quad(g, "trim_tan", [Vector3(x, 6.25, COURT), Vector3(x, 6.25, -COURT), Vector3(x, COURT_SPRING, -COURT), Vector3(x, COURT_SPRING, COURT)], Vector3(1, 0, 0))
	box(g, "trim_tan", Vector3(x + 0.12, 6.28, 0), Vector3(0.24, 0.12, COURT * 2))   # cornice lip
	# clerestory reveal + mullions (opening itself is left open for daylight)
	for zz in range(-8, 9, 2):
		box(g, "trim_tan", Vector3(x - 0.15, 5.62, float(zz)), Vector3(0.3, 1.25, 0.14))
	quad(g, "trim_tan", [Vector3(x, 5.0, COURT), Vector3(x, 5.0, -COURT), Vector3(x - 0.3, 5.0, -COURT), Vector3(x - 0.3, 5.0, COURT)], Vector3.UP)
	quad(g, "trim_tan", [Vector3(x, 6.25, -COURT), Vector3(x, 6.25, COURT), Vector3(x - 0.3, 6.25, COURT), Vector3(x - 0.3, 6.25, -COURT)], Vector3.DOWN)
	quad("glass", "glass", [Vector3(x - 0.3, 5.0, COURT), Vector3(x - 0.3, 5.0, -COURT), Vector3(x - 0.3, 6.25, -COURT), Vector3(x - 0.3, 6.25, COURT)], Vector3(1, 0, 0), [], true)
	# east wall x = +8: corridor opening below, plaster above up to springing
	x = COURT
	var o2 = PackedVector2Array()
	# u runs along -z so that the outline's +u maps to... use world z directly
	var sec = hall_section_outline()
	o2.append(Vector2(-COURT, 0)); o2.append(Vector2(-COURT, COURT_SPRING)); o2.append(Vector2(COURT, COURT_SPRING)); o2.append(Vector2(COURT, 0))
	# notch: the corridor opening (section is symmetric so u = z)
	for p in sec:
		o2.append(Vector2(p.x, max(p.y, 0.0)))
	poly(g, "plaster", o2, Vector3(x, 0, 0), Vector3(0, 0, 1), Vector3.UP, Vector3(-1, 0, 0))
	box(g, "trim_tan", Vector3(x - 0.12, 6.28, 0), Vector3(0.24, 0.12, COURT * 2))
	quad(g, "trim_tan", [Vector3(x, 6.25, -COURT), Vector3(x, 6.25, COURT), Vector3(x, COURT_SPRING, COURT), Vector3(x, COURT_SPRING, -COURT)], Vector3(-1, 0, 0))
	for sgn in [-1.0, 1.0]:
		box(g, "stone", Vector3(x - 0.03, 0.3, sgn * 7.0), Vector3(0.06, 0.6, 2.0))
	# north and south lunettes (z = +/-8): hall opening below, arch trim band
	for sgn in [-1.0, 1.0]:
		var o3 = PackedVector2Array()
		o3.append(Vector2(-COURT, 0))
		for p in pts:
			o3.append(p)
		o3.append(Vector2(COURT, 0))
		var notch2 = Array(hall_section_outline())
		for p in notch2:
			o3.append(Vector2(p.x, max(p.y, 0.0)))
		poly(g, "plaster", o3, Vector3(0, 0, sgn * COURT), Vector3(1, 0, 0), Vector3.UP, Vector3(0, 0, -sgn))
		# darker arched trim band following the vault edge, standing proud 0.1
		for i in pts.size() - 1:
			var a: Vector2 = pts[i]
			var b: Vector2 = pts[i + 1]
			var ia = a + (Vector2(0, cy) - a).normalized() * 0.55
			var ib = b + (Vector2(0, cy) - b).normalized() * 0.55
			var zz = sgn * (COURT - 0.1)
			quad(g, "trim_tan", [Vector3(a.x, a.y, zz), Vector3(b.x, b.y, zz), Vector3(ib.x, ib.y, zz), Vector3(ia.x, ia.y, zz)], Vector3(0, 0, -sgn))
			quad(g, "trim_tan", [Vector3(ia.x, ia.y, zz), Vector3(ib.x, ib.y, zz), Vector3(ib.x, ib.y, sgn * COURT), Vector3(ia.x, ia.y, sgn * COURT)], (Vector3(0, cy, 0) - Vector3((ia.x + ib.x) * 0.5, (ia.y + ib.y) * 0.5, 0)).normalized())
		# side pieces of wall either side of the hall opening, floor to lane height
		for side in [-1.0, 1.0]:
			box(g, "stone", Vector3(side * 7.0, 0.3, sgn * (COURT - 0.03)), Vector3(2.0, 0.6, 0.06))
	# round columns at the court corners, with base and capital
	for cx in [-6.7, 6.7]:
		for cz in [-6.7, 6.7]:
			cyl(g, "column", Vector3(cx, 0.35, cz), 0.3, 0.3, COURT_SPRING - 0.6, 24, false)
			cyl(g, "stone", Vector3(cx, 0, cz), 0.4, 0.4, 0.35, 24, true)
			cyl(g, "column", Vector3(cx, COURT_SPRING - 0.25, cz), 0.3, 0.42, 0.25, 24, true, true)
			obstacles.append([cx, cz, 0.55])
	# fixtures: a central palm bed with dark benches backed onto it
	palm_bed("court_props", Vector3(0, 0, 0), 2.4, 5.0)
	bench("court_props", Vector3(-1.75, 0, -1.2), PI * 0.5)
	bench("court_props", Vector3(-1.75, 0, 1.2), PI * 0.5)
	bench("court_props", Vector3(1.75, 0, -1.2), -PI * 0.5)
	bench("court_props", Vector3(1.75, 0, 1.2), -PI * 0.5)
	trash("court_props", Vector3(-5.6, 0, 5.8))
	trash("court_props", Vector3(5.6, 0, -5.8))
	planter("court_props", Vector3(-6.0, 0, -6.0), "palm")
	planter("court_props", Vector3(6.0, 0, 6.0), "palm")
	# brass lanterns
	for p in [Vector3(-3.6, 4.3, -4.0), Vector3(3.6, 4.3, -4.0), Vector3(-3.6, 4.3, 4.0), Vector3(3.6, 4.3, 4.0)]:
		lantern(p, arch_y(p.x, COURT, COURT_SPRING, COURT_RISE))

# ------------------------------------------------------------- the halls
func hall_fixtures(g: String, axis: String, s0: float, s1: float) -> void:
	var lo: float = min(s0, s1)
	var hi: float = max(s0, s1)
	var s = lo + 5.0
	while s < hi - 3.0:
		var P = func(u: float, v: float) -> Vector3:
			return Vector3(u, 0, v) if axis == "z" else Vector3(v, 0, u)
		var yaw0 = 0.0 if axis == "z" else PI * 0.5
		planter(g, P.call(0, s), "palm" if int(s) % 2 == 0 else "leafy")
		bench(g, P.call(0, s - 1.6), yaw0 + PI)
		bench(g, P.call(0, s + 1.6), yaw0)
		trash(g, P.call(2.6, s + 4.5))
		s += 13.0

func build() -> void:
	randomize()
	seed(1995)
	layout = JSON.parse_string(FileAccess.get_file_as_string("res://layout.json"))
	mall = Node3D.new(); mall.name = "Mall"
	light_root = Node3D.new(); light_root.name = "Lights"
	mall.add_child(light_root)
	light_root.owner = mall

	build_court()
	# north hall (z -8 .. -40), south hall (8 .. 28), entrance corridor (x 8 .. 30)
	hall_ceiling("north", "z", -COURT, -40.0, 0.0)
	hall_ceiling("south", "z", COURT, 28.0, 0.0)
	hall_ceiling("corridor", "x", COURT, 30.0, 0.0)
	floor_rect("north", "floor_hall", -HALL_HALF, -40.0, HALL_HALF, -COURT, func(v): return Vector2((v.x + 6.0) / 12.0, v.z / 6.0))
	floor_rect("south", "floor_hall", -HALL_HALF, COURT, HALL_HALF, 28.0, func(v): return Vector2((v.x + 6.0) / 12.0, v.z / 6.0))
	floor_rect("corridor", "floor_corridor", COURT, -HALL_HALF, 30.0, HALL_HALF, func(v): return Vector2((v.z + 6.0) / 12.0, v.x / 6.0))
	hall_end("south", "z", 28.0, 0.0, -1.0)
	hall_end("north", "z", -40.0, 0.0, 1.0)
	hall_end("corridor", "x", 30.0, 0.0, -1.0)
	for sd in layout.stores:
		store(sd)
	# plain and K&B walls where there is no storefront
	kb_wall("north", -8.0, -18.0)
	kb_wall("north", -26.0, -34.0)
	plain_wall("north", Vector2(6, -34), Vector2(6, -40), Vector2(-1, 0))
	plain_wall("north", Vector2(-6, -33), Vector2(-6, -40), Vector2(1, 0))
	plain_wall("north", Vector2(-6, -8.4), Vector2(-6, -8.0), Vector2(1, 0))
	plain_wall("south", Vector2(-6, 18), Vector2(-6, 28), Vector2(1, 0))
	plain_wall("south", Vector2(6, 27), Vector2(6, 28), Vector2(-1, 0))
	plain_wall("south", Vector2(-6, 8), Vector2(-6, 8.4), Vector2(1, 0))
	plain_wall("south", Vector2(6, 8), Vector2(6, 8.4), Vector2(-1, 0))
	plain_wall("south", Vector2(-6, 28), Vector2(6, 28), Vector2(0, -1))
	plain_wall("corridor", Vector2(8, -6), Vector2(8.4, -6), Vector2(0, 1))
	plain_wall("corridor", Vector2(8, 6), Vector2(8.4, 6), Vector2(0, -1))
	plain_wall("court", Vector2(-8, -8), Vector2(-8, -7.6), Vector2(1, 0))
	plain_wall("court", Vector2(-8, 7.6), Vector2(-8, 8), Vector2(1, 0))
	# court corner returns (between the court's 16 m and the halls' 12 m)
	for sgn in [-1.0, 1.0]:
		plain_wall("court", Vector2(-8, sgn * 8), Vector2(-6, sgn * 8), Vector2(0, -sgn))
		plain_wall("court", Vector2(6, sgn * 8), Vector2(8, sgn * 8), Vector2(0, -sgn))
		plain_wall("court", Vector2(8, sgn * 8), Vector2(8, sgn * 6), Vector2(-1, 0))
	# main entrance: wall with a glass door opening, daylight beyond
	var eo = PackedVector2Array([Vector2(-6, 0), Vector2(-6, LANE_H), Vector2(6, LANE_H), Vector2(6, 0), Vector2(3.2, 0), Vector2(3.2, 3.0), Vector2(-3.2, 3.0), Vector2(-3.2, 0)])
	poly("corridor", "cream", eo, Vector3(30, 0, 0), Vector3(0, 0, 1), Vector3.UP, Vector3(-1, 0, 0))
	box("corridor", "bronze", Vector3(30, 3.0, 0), Vector3(0.2, 0.15, 6.4))
	for k in 5:
		var zz = -3.2 + k * 1.6
		box("corridor", "bronze", Vector3(30, 1.5, zz), Vector3(0.18, 3.0, 0.08))
	quad("glass", "glass", [Vector3(30, 0, -3.2), Vector3(30, 0, 3.2), Vector3(30, 3.0, 3.2), Vector3(30, 3.0, -3.2)], Vector3(-1, 0, 0), [], true)
	# vestibule + outside so daylight has something to bounce off
	floor_rect("outside", "outside_ground", 30.0, -14.0, 60.0, 14.0, func(v): return Vector2(v.x, v.z) * 0.25)
	quad("outside", "cream", [Vector3(34, 3.2, -4), Vector3(34, 3.2, 4), Vector3(30, 3.2, 4), Vector3(30, 3.2, -4)], Vector3.DOWN)
	# hall fixtures (benches facing across planters, trash cans)
	hall_fixtures("north_props", "z", -12.0, -38.0)
	hall_fixtures("south_props", "z", 12.0, 27.0)
	hall_fixtures("corridor_props", "x", 11.0, 29.0)

	# ---- lights and environment
	var sun = DirectionalLight3D.new()
	sun.name = "Sun"
	sun.light_bake_mode = Light3D.BAKE_STATIC
	sun.shadow_enabled = true
	sun.light_energy = 2.4
	sun.light_color = Color(1.0, 0.95, 0.86)
	sun.light_angular_distance = 1.2
	mall.add_child(sun); sun.owner = mall
	sun.look_at_from_position(Vector3.ZERO, Vector3(0.62, -0.62, 0.48), Vector3.UP)

	var env = Environment.new()
	var sky = Sky.new()
	var psky = ProceduralSkyMaterial.new()
	psky.sky_top_color = Color("#5d8fd1")
	psky.sky_horizon_color = Color("#c9dbee")
	psky.ground_horizon_color = Color("#c9c3b5")
	psky.ground_bottom_color = Color("#7b766c")
	psky.sky_energy_multiplier = 1.4
	sky.sky_material = psky
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.35
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.05
	env.tonemap_white = 6.0
	env.glow_enabled = true
	env.glow_intensity = 0.35
	env.glow_bloom = 0.04
	env.glow_hdr_threshold = 1.2
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.08
	env.adjustment_contrast = 1.04
	var we = WorldEnvironment.new()
	we.name = "Env"
	we.environment = env
	mall.add_child(we); we.owner = mall

	# ---- commit static geometry
	var static_root = Node3D.new(); static_root.name = "Static"
	mall.add_child(static_root); static_root.owner = mall
	DirAccess.make_dir_recursive_absolute("res://gen")
	for gname in acc:
		var am = ArrayMesh.new()
		var names = []
		for mname in acc[gname]:
			var s: SurfaceTool = acc[gname][mname]
			s.index()
			s.generate_tangents()
			s.commit(am)
			am.surface_set_material(am.get_surface_count() - 1, mat(mname))
		var texel = TEXEL
		if gname.begins_with("store_"):
			texel = TEXEL * 2.2
		elif gname.ends_with("props") or gname == "lanterns":
			texel = TEXEL * 0.6
		elif gname == "outside":
			texel = TEXEL * 4.0
		var err = am.lightmap_unwrap(Transform3D.IDENTITY, texel)
		if err != OK:
			push_error("unwrap failed " + gname)
		ResourceSaver.save(am, "res://gen/" + gname + ".res")
		am = load("res://gen/" + gname + ".res")
		var mi = MeshInstance3D.new()
		mi.name = gname
		mi.mesh = am
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		static_root.add_child(mi); mi.owner = mall
	var dyn_root = Node3D.new(); dyn_root.name = "Dynamic"
	mall.add_child(dyn_root); dyn_root.owner = mall
	for gname in dyn_acc:
		var am = ArrayMesh.new()
		for mname in dyn_acc[gname]:
			var s: SurfaceTool = dyn_acc[gname][mname]
			s.index()
			s.commit(am)
			am.surface_set_material(am.get_surface_count() - 1, mat(mname))
		ResourceSaver.save(am, "res://gen/dyn_" + gname + ".res")
		var mi = MeshInstance3D.new()
		mi.name = "dyn_" + gname
		mi.mesh = load("res://gen/dyn_" + gname + ".res")
		mi.gi_mode = GeometryInstance3D.GI_MODE_DYNAMIC
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		dyn_root.add_child(mi); mi.owner = mall

	# reflection probes: court, each hall
	for pr in [[Vector3(0, 4.5, 0), Vector3(16, 10, 16)], [Vector3(0, 3.2, -24), Vector3(12, 6.6, 32)], [Vector3(0, 3.2, 18), Vector3(12, 6.6, 20)], [Vector3(19, 3.2, 0), Vector3(22, 6.6, 12)]]:
		var rp = ReflectionProbe.new()
		rp.position = pr[0]
		rp.size = pr[1]
		rp.box_projection = true
		rp.interior = true
		rp.update_mode = ReflectionProbe.UPDATE_ONCE
		rp.ambient_mode = ReflectionProbe.AMBIENT_DISABLED
		rp.intensity = 0.9
		mall.add_child(rp); rp.owner = mall

	var lm = LightmapGI.new()
	lm.name = "LightmapGI"
	lm.quality = LightmapGI.BAKE_QUALITY_MEDIUM
	lm.bounces = 3
	lm.bounce_indirect_energy = 1.0
	lm.use_denoiser = true
	lm.environment_mode = LightmapGI.ENVIRONMENT_MODE_SCENE
	lm.max_texture_size = 4096
	lm.generate_probes_subdiv = LightmapGI.GENERATE_PROBES_SUBDIV_8
	mall.add_child(lm); lm.owner = mall

	for c in light_root.get_children():
		c.owner = mall
	for c in mall.get_children():
		if c is Label3D:
			c.owner = mall

	# player
	var player: Node3D = load("res://scripts/player.gd").new()
	player.name = "Player"
	player.set("obstacles", obstacles)
	mall.add_child(player); player.owner = mall

	var fm = Node.new()
	fm.set_script(load("res://scripts/floor_mirror.gd"))
	fm.name = "FloorMirror"
	mall.add_child(fm); fm.owner = mall

	var ps = PackedScene.new()
	ps.pack(mall)
	ResourceSaver.save(ps, "res://main.tscn")
	print("BUILD OK groups=", acc.size(), " dyn=", dyn_acc.size(), " lights=", light_root.get_child_count(), " obstacles=", obstacles.size())

func _initialize() -> void:
	build()
	quit()
