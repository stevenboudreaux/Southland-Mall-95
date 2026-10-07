## Builds res://main.tscn: the whole mall (1995 map) from layout_mall.json.
## Run: godot --headless --path . --script res://tools/build_mall.gd
## Units are metres. +x east, +z south, +y up. Map tile (148, 100) is the origin.
extends SceneTree

const LANE_H = 4.6         # flat ceiling over the store lanes
const VAULT_SPRING = 4.9   # hall vault springing
const COURT_SPRING = 6.6
const RIB_STEP = 1.8
const OPEN_H = 3.2         # storefront opening height
const ANCHOR_FRONT = 24.0  # width of an anchor store's mall entrance (JCPenney's)
## Store looks that differ from the map data (from Steven's photos and memory).
const OVERRIDES = {"CORN DOG 7": {"awningColor": "#f2cf1d", "awningStripe": "#1f2d6e"}}
var TEXEL = 0.16           # lightmap texel size (metres); fast bake for demos

var mall: Node3D
var light_root: Node3D
var mats = {}
var acc = {}               # group -> {material -> SurfaceTool}
var dyn_acc = {}
var L: Dictionary          # layout
var zones = {}             # id -> zone dict
var obstacles = []
var fx_obstacles = []     # fixtures (benches, planters, trash cans): only block when shown
var signs = []             # owner-editable signs (scripts/signs.gd), written to gen/signs.json
var fx = false            # while true, geometry goes to the switchable "fixtures" mesh
var cur_color = Color.WHITE
var atlas_index = {}       # store id -> atlas cell
var fronts = {}            # "x,z|x,z" of a store edge -> captured front (fronts.json)
## The live game's flat storefront paintings on the Godot fronts (Phase 4a) are off: Steven
## (Oct 5, 18:51) prefers the plain storefronts with the vendor's sign until each store is
## built in full 3D from its photos, as Corn Dog 7 is.
const USE_FRONT_ART = false
## Stores built in full 3D: their footprint (x0, z0, x1, z1 in metres) is kept clear of the
## generic interiors of neighbouring stores, which would otherwise run through them.
const BUILT_RECTS = {"CORN DOG 7": [-138.0, 68.0, -126.0, 80.0], "POCKET CHANGE": [-110.0, 60.0, -102.0, 100.0],
	"KAY-BEE TOYS": [-34.0, -58.0, -10.0, -52.0], "GUMBALLS": [-20.0, 36.0, -10.0, 48.0],
	"JW": [-80.0, 20.0, -74.0, 48.0], "5-7-9": [-74.0, 20.0, -68.0, 48.0], "COUNTY SEAT": [-94.0, 60.0, -86.0, 100.0],
	"BABBAGE'S": [-132.0, 60.0, -124.0, 68.0], "SOUND SHOP": [-34.0, -64.0, -10.0, -58.0],
	"WOOLWORTH": [-46.0, -14.0, -10.0, 22.0], "LERNER SHOP": [-38.0, 22.0, -10.0, 36.0],
	"LANE BRYANT": [-34.0, -72.0, -10.0, -64.0], "MILLER'S OUTPOST": [-38.0, -52.0, -10.0, -40.0],
	"GADZOOKS": [-62.0, 24.0, -50.0, 48.0], "THE LIMITED": [-132.0, 20.0, -122.0, 48.0]}
var fronts_px = 64.0       # atlas pixels per 2 m tile
var facade_levels = {}     # store id -> accuracy level 0..4 (facade_records.json)
const LEVEL_COLORS = ["#8a8a8a", "#b07a3c", "#c9c9c9", "#e2b43a", "#3fae6a"]   # grey, bronze, silver, gold, green
const ATLAS_COLS = 8
const ATLAS_ROWS = 12

# ------------------------------------------------------------------ materials
func obst(o):
	if fx:
		fx_obstacles.append(o)
	else:
		obstacles.append(o)

var raw_tex = false        # previews (tools/qa/preview.gd) read the PNGs directly, no import step

func tex(p):
	if raw_tex:
		var im = Image.load_from_file(ProjectSettings.globalize_path("res://tex/" + p))
		if im == null:
			push_error("missing texture " + p)
			return null
		im.generate_mipmaps()
		return ImageTexture.create_from_image(im)
	return load("res://tex/" + p)

func mat(name):
	if mats.has(name):
		return mats[name]
	var m = StandardMaterial3D.new()
	m.resource_name = name
	match name:
		"plaster":
			m.albedo_texture = tex("plaster.png"); m.roughness = 0.92
		"plaster_white":
			m.albedo_texture = tex("plaster.png"); m.roughness = 0.9
			m.albedo_color = Color(1.25, 1.27, 1.32)
		"pink_stripe":
			m.albedo_color = Color("#e48aa0"); m.roughness = 0.6
		"crystal":
			m.albedo_color = Color("#f4f8ff"); m.metallic = 0.3; m.roughness = 0.05
			m.emission_enabled = true; m.emission = Color("#fff6e8"); m.emission_energy_multiplier = 2.5
		"cove":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#ffc98a"); m.emission_energy_multiplier = 5.0
		"ring_glow":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fff2dc"); m.emission_energy_multiplier = 1.5
		"black":
			m.albedo_color = Color("#151313"); m.roughness = 0.35
		"velvet":
			m.albedo_color = Color("#2a1a24"); m.roughness = 1.0
		"bulbs":
			m.albedo_color = Color("#fff3c4")
			m.emission_enabled = true; m.emission = Color("#ffe39a"); m.emission_energy_multiplier = 4.0
		"poster":
			m.vertex_color_use_as_albedo = true
			m.emission_enabled = true; m.emission = Color("#ffffff"); m.emission_energy_multiplier = 0.6
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
			m.emission_enabled = true; m.emission = Color("#fff1d6"); m.emission_energy_multiplier = 1.0
			m.set_meta("e_day", 0.55); m.set_meta("e_night", 0.10)
		"downlight":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fff3df"); m.emission_energy_multiplier = 8.0
			# Godot 4.7 lights the halls mostly from these discs: dim them at night (moodier night, Steven Oct 5)
			m.set_meta("e_day", 8.0); m.set_meta("e_night", 2.0)
		"stone":
			m.albedo_texture = tex("stone.png"); m.roughness = 0.55
		"bronze":
			m.albedo_color = Color("#3a2f27"); m.metallic = 0.6; m.roughness = 0.4
		"int_wall":
			m.albedo_color = Color("#ece6da"); m.roughness = 0.9
		"int_floor":
			m.vertex_color_use_as_albedo = true; m.roughness = 0.6
		"int_back":
			m.albedo_texture = tex("int_atlas.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.55)
			m.roughness = 0.8
		"front_art":
			# the live game's storefront paintings (tools/capture_fronts.py), lit
			# a little from within so the signs read at night
			m.albedo_texture = tex("fronts_atlas.png")
			# nearest keeps the live game's pixel look up close; anisotropic mipmaps keep a
			# long frontage seen down the hall from smearing
			m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS_ANISOTROPIC
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.45)
			m.roughness = 0.85
		"int_panel":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#fffaf2"); m.emission_energy_multiplier = 2.2
			m.set_meta("e_day", 2.2); m.set_meta("e_night", 2.4)
		"vcolor":
			m.vertex_color_use_as_albedo = true; m.roughness = 0.5
		"vcolor_matte":
			m.vertex_color_use_as_albedo = true; m.roughness = 0.85
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
		"door_wood":
			m.albedo_texture = tex("wood_dark.png"); m.roughness = 0.5
			m.albedo_color = Color(1.4, 1.2, 1.0)
		"metal_dark":
			m.albedo_color = Color("#262220"); m.metallic = 0.5; m.roughness = 0.45
		"grille":
			m.albedo_color = Color("#8d8a84"); m.metallic = 0.7; m.roughness = 0.5
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
			m.albedo_color = Color(0.78, 0.86, 0.86, 0.10)
			m.roughness = 0.04; m.specular_mode = BaseMaterial3D.SPECULAR_DISABLED
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"palm", "poinsettia", "leafy":
			m.albedo_texture = tex({"palm": "palm_frond.png", "poinsettia": "poinsettia.png", "leafy": "leafy.png"}[name])
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.alpha_scissor_threshold = 0.5
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.7
		"trunk":
			m.albedo_color = Color("#6d5a3e"); m.roughness = 0.95
		"cove_amber", "cove_cool", "cove_warm":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true
			m.emission = {"cove_amber": Color("#FFC98A"), "cove_cool": Color("#DCE6FF"), "cove_warm": Color("#FFD9A8")}[name]
			m.emission_energy_multiplier = 3.0
			m.set_meta("e_day", 0.0); m.set_meta("e_night", 3.0)
		"buff_tile":
			m.albedo_texture = tex("buff_tile.png"); m.roughness = 0.35
		"grey_tile":
			m.albedo_texture = tex("grey_tile.png"); m.roughness = 0.35
		"wood_diag":
			m.albedo_texture = tex("wood_diag.png"); m.roughness = 0.6
		"brown_stone":
			m.albedo_texture = tex("brown_stone.png"); m.roughness = 0.12; m.metallic_specular = 0.7
		"halo":
			m.albedo_color = Color.WHITE
			m.emission_enabled = true; m.emission = Color("#ffffff"); m.emission_energy_multiplier = 1.6
			m.set_meta("e_day", 1.6); m.set_meta("e_night", 1.0)
		"outside_ground":
			m.albedo_color = Color("#7c7a74"); m.roughness = 0.95
		"exit_sign":
			m.albedo_color = Color("#2e7d4f")
			m.emission_enabled = true; m.emission = Color("#3fae6a"); m.emission_energy_multiplier = 0.8
		_:
			if name.begins_with("cd7_"):
				# Corn Dog 7's painted textures (tools/stores/paint_corn_dog_7.py)
				var key = name.substr(4)
				if key == "soffit":
					m.albedo_color = Color("#f4f2ec"); m.roughness = 0.9
				elif key == "glass":
					# clear interior glass (food cases, the kitchen partition): barely there, a faint sheen
					m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
					m.albedo_color = Color(0.9, 0.95, 0.95, 0.06)
					m.roughness = 0.35; m.metallic_specular = 0.1
					m.cull_mode = BaseMaterial3D.CULL_DISABLED
				elif key != "glass":
					m.albedo_texture = tex("cd7/" + key + ".png")
					m.roughness = 0.8
				if key in ["tile_navy", "counter_front", "wall_yellow"]:
					# glazed tile: a soft sheen, not a mirror (the store has its own probe)
					m.roughness = 0.45; m.metallic_specular = 0.5
				elif key == "awning":
					m.roughness = 0.3; m.metallic_specular = 0.7
					m.emission_enabled = true; m.emission_texture = m.albedo_texture
					m.emission = Color.WHITE; m.emission_energy_multiplier = 0.35
					# multiply: the sign glows its own yellow (add would wash it toward white)
					m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
					m.set_meta("e_day", 0.12); m.set_meta("e_night", 0.35)
				elif key == "steel":
					# brushed stainless: mostly what the baked light gives it, a little reflection
					m.metallic = 0.4; m.roughness = 0.3; m.albedo_color = Color(1.1, 1.1, 1.12)
				elif key == "troffer":
					m.emission_enabled = true; m.emission_texture = m.albedo_texture
					m.emission = Color.WHITE; m.emission_energy_multiplier = 1.4
					m.set_meta("e_day", 1.4); m.set_meta("e_night", 1.5)
				elif key == "menu":
					# a lit screen shows its picture as is
					m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				elif key == "floor":
					m.roughness = 0.55; m.metallic_specular = 0.45
			elif name.begins_with("pc_"):
				# Pocket Change: "pc_<module>_<key>" is filled in by
				# tools/stores/pocket_change/<module>.gd's fill_mat(m, key, b)
				var parts = name.substr(3).split("_", true, 1)
				var mp = "res://tools/stores/pocket_change/%s.gd" % parts[0]
				if parts.size() < 2 or not ResourceLoader.exists(mp) or not load(mp).fill_mat(m, parts[1], self):
					push_error("unknown material " + name)
			elif name.begins_with("ap_"):
				# the clothing stores (JW, 5-7-9, County Seat): tools/stores/apparel/kit.gd's fill_mat
				if not load("res://tools/stores/apparel/kit.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("gb_"):
				# Gumballs: tools/stores/gumballs/store.gd's fill_mat(m, key, b)
				if not load("res://tools/stores/gumballs/store.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("a2_"):
				# the Wave 4 clothing stores: tools/stores/apparel/more.gd's fill_mat
				if not load("res://tools/stores/apparel/more.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("wl_"):
				# Woolworth: tools/stores/woolworth/store.gd's fill_mat
				if not load("res://tools/stores/woolworth/store.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("md_"):
				# the media kit (Babbage's, Sound Shop): tools/stores/media/kit.gd's fill_mat
				if not load("res://tools/stores/media/kit.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("kb_"):
				# Kay-Bee Toys: tools/stores/kay_bee/store.gd's fill_mat(m, key, b)
				if not load("res://tools/stores/kay_bee/store.gd").fill_mat(m, name.substr(3), self):
					push_error("unknown material " + name)
			elif name.begins_with("floorz_"):
				# bake-time stand-in; the runtime swaps in the procedural floor shader
				m.albedo_color = Color("#d4c4aa"); m.roughness = 0.14; m.metallic_specular = 0.6
			else:
				push_error("unknown material " + name)
	mats[name] = m
	return m

# ------------------------------------------------------------- mesh helpers
func st(group, mname, dynamic = false):
	if fx:
		group = "fixtures"
		dynamic = true
	var A = dyn_acc if dynamic else acc
	if not A.has(group):
		A[group] = {}
	if not A[group].has(mname):
		var s = SurfaceTool.new()
		s.begin(Mesh.PRIMITIVE_TRIANGLES)
		A[group][mname] = s
	return A[group][mname]

func tri(s, a, b, c, ua, ub, uc, n):
	if (b - a).cross(c - a).dot(n) > 0.0:
		var t = b; b = c; c = t
		var tu = ub; ub = uc; uc = tu
	for p in [[a, ua], [b, ub], [c, uc]]:
		s.set_color(cur_color)
		s.set_normal(n)
		s.set_uv(p[1])
		s.add_vertex(p[0])

func quad(group, mname, p, n, uvs = [], dynamic = false, uvscale = 1.0):
	var s = st(group, mname, dynamic)
	if uvs.is_empty():
		for v in p:
			uvs.append(proj_uv(v, n) * uvscale)
	tri(s, p[0], p[1], p[2], uvs[0], uvs[1], uvs[2], n)
	tri(s, p[0], p[2], p[3], uvs[0], uvs[2], uvs[3], n)

func proj_uv(v, n):
	var an = n.abs()
	if an.y >= an.x and an.y >= an.z:
		return Vector2(v.x, v.z)
	elif an.x >= an.z:
		return Vector2(v.z, -v.y)
	return Vector2(v.x, -v.y)

func box(group, mname, c, size, xf = Transform3D.IDENTITY, skip = [], dynamic = false):
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
		var n = (xf.basis * faces[k][0]).normalized()
		var pts = []
		for q in faces[k][1]:
			pts.append(xf * (c + q))
		quad(group, mname, pts, n, [], dynamic)

func cyl(group, mname, base, r0, r1, hgt, seg = 20, top = true, bottom = false, dynamic = false):
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
		_tri_n(s, [p0, p1, p2], [n0, n1, n1], [Vector2(u0, 1), Vector2(u1, 1), Vector2(u1, 0)], (n0 + n1).normalized())
		_tri_n(s, [p0, p2, p3], [n0, n1, n0], [Vector2(u0, 1), Vector2(u1, 0), Vector2(u0, 0)], (n0 + n1).normalized())
		if top:
			var c = base + Vector3(0, hgt, 0)
			tri(s, c, p3, p2, Vector2(0.5, 0.5), Vector2(0.5 + d0.x * 0.5, 0.5 + d0.z * 0.5), Vector2(0.5 + d1.x * 0.5, 0.5 + d1.z * 0.5), Vector3.UP)
		if bottom:
			tri(s, base, p0, p1, Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector3.DOWN)

func _tri_n(s, p, n, uv, face_n):
	var order = [0, 1, 2]
	if (p[1] - p[0]).cross(p[2] - p[0]).dot(face_n) > 0.0:
		order = [0, 2, 1]
	for i in order:
		s.set_color(cur_color); s.set_normal(n[i]); s.set_uv(uv[i]); s.add_vertex(p[i])

func poly(group, mname, outline, o, ax, ay, n):
	var idx = Geometry2D.triangulate_polygon(outline)
	if idx.is_empty():
		push_error("triangulation failed in " + group)
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

func abs_size(t, along, hgt, depth, n):
	var v = t.abs() * along + n.abs() * depth
	return Vector3(max(v.x, 0.001), hgt, max(v.z, 0.001))

# --------------------------------------------------------------- arch math
func arch_R(half, rise):
	return (half * half + rise * rise) / (2.0 * rise)

func arch_pts(half, spring, rise, seg):
	var R = arch_R(half, rise)
	var cy = spring + rise - R
	var th = asin(half / R)
	var out = []
	for i in seg + 1:
		var a = -th + 2.0 * th * i / seg
		out.append(Vector2(R * sin(a), cy + R * cos(a)))
	return out

func arch_y(u, half, spring, rise):
	var R = arch_R(half, rise)
	var cy = spring + rise - R
	return cy + sqrt(max(R * R - u * u, 0.0))

func hall_rise(vh):
	return vh * 0.47   # 3 m half-span -> 1.4 m rise, as in the proof

# --------------------------------------------------------------- zones
func rect_of(z):
	return z.rect   # [x0, z0, x1, z1]

## Hall geometry: frame helpers map (u across from centre, y, s along) to world.
func hall_P(z, u, y, s):
	var r = z.rect
	if z.axis == "z":
		return Vector3((r[0] + r[2]) * 0.5 + u, y, s)
	return Vector3(s, y, (r[1] + r[3]) * 0.5 + u)

func hall_span(z):
	var r = z.rect
	if z.axis == "z":
		return [r[1], r[3], (r[2] - r[0]) * 0.5]
	return [r[0], r[2], (r[3] - r[1]) * 0.5]

func build_hall(z):
	var g = z.id
	var sp = hall_span(z)
	var lo = sp[0]
	var hi = sp[1]
	var hw = sp[2]
	var vh = float(z.vault_half)
	var ax = (hall_P(z, 0, 0, 1) - hall_P(z, 0, 0, 0))
	if vh <= 0.0:
		# narrow corridor: flat ceiling, a line of downlights
		quad(g, "lane_ceiling", [hall_P(z, -hw, LANE_H, lo), hall_P(z, hw, LANE_H, lo), hall_P(z, hw, LANE_H, hi), hall_P(z, -hw, LANE_H, hi)], Vector3.DOWN)
		var s0 = lo + 2.0
		while s0 < hi - 1.0:
			var c = hall_P(z, 0, LANE_H - 0.01, s0)
			disc_down(g, c, 0.16)
			add_downlight(c)
			s0 += 4.0
		return
	var rise = hall_rise(vh)
	for side in [-1.0, 1.0]:
		var a = side * vh
		var b = side * hw
		quad(g, "lane_ceiling", [hall_P(z, a, LANE_H, lo), hall_P(z, b, LANE_H, lo), hall_P(z, b, LANE_H, hi), hall_P(z, a, LANE_H, hi)], Vector3.DOWN)
		var nf = (hall_P(z, -side, 0, 0) - hall_P(z, 0, 0, 0)).normalized()
		quad(g, "bulkhead", [hall_P(z, a, LANE_H, lo), hall_P(z, a, VAULT_SPRING, lo), hall_P(z, a, VAULT_SPRING, hi), hall_P(z, a, LANE_H, hi)], nf)
		if hw - vh >= 1.4:
			var s1 = lo + 2.25
			while s1 < hi - 0.8:
				var c2 = hall_P(z, side * (vh + hw) * 0.5, LANE_H - 0.01, s1)
				disc_down(g, c2, 0.17)
				add_downlight(c2)
				s1 += 4.5
	var pts = arch_pts(vh, VAULT_SPRING, rise, 16)
	var R = arch_R(vh, rise)
	var cy = VAULT_SPRING + rise - R
	var skies = []
	for sk in L.get("skylights", []):
		if sk.zone == z.id:
			skies.append(float(sk.at))
	var sku = vh * 0.55
	var skl = 1.3
	for i in pts.size() - 1:
		var a2 = pts[i]
		var b2 = pts[i + 1]
		var mid = (a2 + b2) * 0.5
		var nn = (hall_P(z, 0, cy, 0) - hall_P(z, mid.x, mid.y, 0)).normalized()
		var spans = [[lo, hi]]
		if abs(mid.x) < sku:
			spans = []
			var cur = lo
			var sorted_sk = skies.duplicate()
			sorted_sk.sort()
			for at in sorted_sk:
				spans.append([cur, at - skl])
				cur = at + skl
			spans.append([cur, hi])
		for sp2 in spans:
			var q0 = sp2[0]
			var q1 = sp2[1]
			if q1 - q0 < 0.01:
				continue
			quad(g, "vault_glow", [hall_P(z, a2.x, a2.y, q0), hall_P(z, b2.x, b2.y, q0), hall_P(z, b2.x, b2.y, q1), hall_P(z, a2.x, a2.y, q1)], nn, [Vector2(a2.x, q0), Vector2(b2.x, q0), Vector2(b2.x, q1), Vector2(a2.x, q1)])
	for at in skies:
		hall_skylight(z, at, sku, skl, vh, rise)
	var r = lo + RIB_STEP * 0.5
	while r < hi:
		rib(z, r, pts, vh, rise, ax)
		r += RIB_STEP
	for he in L.hall_ends:
		if he.zone == z.id and he.closed:
			hall_end(z, lo if he.end == "lo" else hi, 1.0 if he.end == "lo" else -1.0, vh, rise)

## A skylight in the hall vault crown between two ribs: a short light well
## with a muntin frame; the opening is real, so the bake gets daylight.
func hall_skylight(z, at, sku, skl, vh, rise):
	var g = z.id
	var crown = VAULT_SPRING + rise
	var top = crown + 0.7
	# side walls (u = +/- sku), bottom edge on the vault surface
	for sgn in [-1.0, 1.0]:
		var yb = arch_y(sku, vh, VAULT_SPRING, rise) - 0.03
		var nrm = (hall_P(z, -sgn, 0, 0) - hall_P(z, 0, 0, 0)).normalized()
		quad(g, "lane_ceiling", [hall_P(z, sgn * sku, yb, at - skl), hall_P(z, sgn * sku, yb, at + skl), hall_P(z, sgn * sku, top, at + skl), hall_P(z, sgn * sku, top, at - skl)], nrm)
	for sgn in [-1.0, 1.0]:
		var o = PackedVector2Array()
		for i in 7:
			var u = -sku + 2.0 * sku * i / 6
			o.append(Vector2(u, arch_y(u, vh, VAULT_SPRING, rise) - 0.03))
		o.append(Vector2(sku, top)); o.append(Vector2(-sku, top))
		var org = hall_P(z, 0, 0, at + sgn * skl)
		var axu = hall_P(z, 1, 0, 0) - hall_P(z, 0, 0, 0)
		var nrm2 = (hall_P(z, 0, 0, -sgn) - hall_P(z, 0, 0, 0)).normalized()
		poly(g, "lane_ceiling", o, org, axu, Vector3.UP, nrm2)
	var axs = hall_P(z, 0, 0, 1) - hall_P(z, 0, 0, 0)
	var axu2 = hall_P(z, 1, 0, 0) - hall_P(z, 0, 0, 0)
	for k in 4:
		var u = -sku + k * sku * 2.0 / 3.0
		box("glass_frames", "metal_dark", hall_P(z, u, top - 0.05, at), abs_size(axs, skl * 2, 0.08, 0.05, axu2), Transform3D.IDENTITY, [], true)
	for k in 3:
		var s2 = at - skl + k * skl
		box("glass_frames", "metal_dark", hall_P(z, 0, top - 0.05, s2), abs_size(axu2, sku * 2, 0.08, 0.05, axs), Transform3D.IDENTITY, [], true)

func rib(z, at, pts, vh, rise, ax):
	var g = z.id
	var w = 0.07
	var depth = 0.22
	var R = arch_R(vh, rise)
	var cy = VAULT_SPRING + rise - R
	for i in pts.size() - 1:
		var a = pts[i]
		var b = pts[i + 1]
		var ia = a + (Vector2(0, cy) - a).normalized() * depth
		var ib = b + (Vector2(0, cy) - b).normalized() * depth
		var mid = (ia + ib) * 0.5
		var nn = (hall_P(z, 0, cy, 0) - hall_P(z, mid.x, mid.y, 0)).normalized()
		quad(g, "rib", [hall_P(z, ia.x, ia.y, at - w), hall_P(z, ib.x, ib.y, at - w), hall_P(z, ib.x, ib.y, at + w), hall_P(z, ia.x, ia.y, at + w)], nn)
		for sg in [-1.0, 1.0]:
			quad(g, "rib", [hall_P(z, a.x, a.y, at + sg * w), hall_P(z, b.x, b.y, at + sg * w), hall_P(z, ib.x, ib.y, at + sg * w), hall_P(z, ia.x, ia.y, at + sg * w)], ax * sg)

## Closed end of a hall: arched wall above the lane ceiling, plus a white arch trim.
func hall_end(z, at, facing, vh, rise):
	var g = z.id
	var o = PackedVector2Array()
	o.append(Vector2(-vh, LANE_H))
	for p in arch_pts(vh, VAULT_SPRING, rise, 16):
		o.append(p)
	o.append(Vector2(vh, LANE_H))
	var origin = hall_P(z, 0, 0, at)
	var ax = (hall_P(z, 1, 0, 0) - hall_P(z, 0, 0, 0))
	var n = (hall_P(z, 0, 0, 1) - hall_P(z, 0, 0, 0)) * facing
	poly(g, "cream", o, origin, ax, Vector3.UP, n)
	var pts = arch_pts(vh, VAULT_SPRING, rise, 16)
	var R = arch_R(vh, rise)
	var cy = VAULT_SPRING + rise - R
	for i in pts.size() - 1:
		var a = pts[i]
		var b = pts[i + 1]
		var off = n * 0.12
		var ia = a + (Vector2(0, cy) - a).normalized() * 0.3
		var ib = b + (Vector2(0, cy) - b).normalized() * 0.3
		quad(g, "rib", [origin + ax * a.x + Vector3.UP * a.y + off, origin + ax * b.x + Vector3.UP * b.y + off, origin + ax * ib.x + Vector3.UP * ib.y + off, origin + ax * ia.x + Vector3.UP * ia.y + off], n)

# --------------------------------------------------------------- courts
## A court: segmental plaster vault over the shorter span, walls from lane
## height up to the springing with notches where hall vaults come in, a
## square skylight, and a clerestory on long sides no hall enters.
func build_court(z):
	if z.style == "dillards":
		build_court_flat(z)
		return
	var g = z.id
	var vmat = "plaster_white" if z.style == "sears" else "plaster"
	var r = z.rect
	var sx = r[2] - r[0]
	var sz = r[3] - r[1]
	var cx = (r[0] + r[2]) * 0.5
	var cz = (r[1] + r[3]) * 0.5
	var axis = "z" if sz >= sx else "x"   # vault runs along the longer side
	if z.style == "shoe":
		axis = "z"
	var half = (sx if axis == "z" else sz) * 0.5
	var length = sz if axis == "z" else sx
	var rise = clamp(half * 2.0 * 0.19, 1.6, 4.2)
	var R = arch_R(half, rise)
	var cy = COURT_SPRING + rise - R
	var sky = clamp(min(half, length * 0.5) * 0.28, 1.2, 2.2)
	# frame: u across the span (from centre), s along the vault (from centre)
	var P = func(u, y, s):
		return Vector3(cx + u, y, cz + s) if axis == "z" else Vector3(cx + s, y, cz + u)
	var pts = arch_pts(half, COURT_SPRING, rise, 40)
	var steps = int(ceil(length / 1.0))
	for i in pts.size() - 1:
		var a = pts[i]
		var b = pts[i + 1]
		var mid = (a + b) * 0.5
		var nn = (P.call(0, cy, 0) - P.call(mid.x, mid.y, 0)).normalized()
		var arc_a = R * asin(a.x / R)
		var arc_b = R * asin(b.x / R)
		for k in steps:
			var s0 = -length * 0.5 + length * k / steps
			var s1 = -length * 0.5 + length * (k + 1) / steps
			if abs(mid.x) < sky and abs((s0 + s1) * 0.5) < sky:
				continue
			quad(g, vmat, [P.call(a.x, a.y, s0), P.call(b.x, b.y, s0), P.call(b.x, b.y, s1), P.call(a.x, a.y, s1)], nn,
				[Vector2(arc_a, s0) * 0.22, Vector2(arc_b, s0) * 0.22, Vector2(arc_b, s1) * 0.22, Vector2(arc_a, s1) * 0.22])
	# skylight well
	var top = COURT_SPRING + rise + 0.9
	var ys = arch_y(sky, half, COURT_SPRING, rise)
	for sgn in [-1.0, 1.0]:
		quad(g, "lane_ceiling", [P.call(sgn * sky, ys - 0.05, -sky), P.call(sgn * sky, ys - 0.05, sky), P.call(sgn * sky, top, sky), P.call(sgn * sky, top, -sky)], (P.call(-sgn, 0, 0) - P.call(0, 0, 0)).normalized())
		var o = PackedVector2Array()
		for i in 9:
			var u = -sky + 2.0 * sky * i / 8
			o.append(Vector2(u, arch_y(u, half, COURT_SPRING, rise) - 0.05))
		o.append(Vector2(sky, top)); o.append(Vector2(-sky, top))
		var org = P.call(0, 0, sgn * sky)
		var axu = P.call(1, 0, 0) - P.call(0, 0, 0)
		poly(g, "lane_ceiling", o, org, axu, Vector3.UP, (P.call(0, 0, -sgn) - P.call(0, 0, 0)).normalized())
	for i in 5:
		var u = -sky + i * sky * 0.5
		var c1 = P.call(u, top - 0.05, 0)
		var c2 = P.call(0, top - 0.05, u)
		box("glass_frames", "metal_dark", c1, abs_size((P.call(0, 0, 1) - P.call(0, 0, 0)), sky * 2, 0.1, 0.05, (P.call(1, 0, 0) - P.call(0, 0, 0))), Transform3D.IDENTITY, [], true)
		box("glass_frames", "metal_dark", c2, abs_size((P.call(1, 0, 0) - P.call(0, 0, 0)), sky * 2, 0.1, 0.05, (P.call(0, 0, 1) - P.call(0, 0, 0))), Transform3D.IDENTITY, [], true)
	tag(add_omni(P.call(0, COURT_SPRING, 0), 1.0, half * 2.5, Color(1.0, 0.95, 0.88)), "day")
	# night: four key spots at the springing line, aimed down, so the floor
	# gets broad overlapping pools instead of one hot centre
	for qu in [-0.45, 0.45]:
		for qs in [-0.33, 0.0, 0.33]:
			tag(add_spot(P.call(qu * half, COURT_SPRING - 0.2, qs * length), Vector3.DOWN, 3.2, 12.0, 70.0, Color("#FFE9C8")), "night")
	var cove_col = {"shoe": Color("#FFC98A"), "sears": Color("#DCE6FF")}.get(z.style, Color("#FFD9A8"))
	var cove_mat = {"shoe": "cove_amber", "sears": "cove_cool"}.get(z.style, "cove_warm")
	# walls
	var sides = {}
	for cw in L.court_walls:
		if cw.zone == z.id:
			sides[cw.side] = cw.halls
	for side in ["n", "s", "w", "e"]:
		var halls = sides.get(side, [])
		var horiz = side in ["n", "s"]   # wall runs along x
		var along_vault = (horiz and axis == "x") or (not horiz and axis == "z")
		# wall line and inward normal
		var o2 = Vector3.ZERO
		var axw = Vector3.ZERO
		var nrm = Vector3.ZERO
		var u0 = 0.0
		var u1 = 0.0
		if horiz:
			o2 = Vector3(cx, 0, r[1] if side == "n" else r[3])
			axw = Vector3(1, 0, 0); u0 = r[0] - cx; u1 = r[2] - cx
			nrm = Vector3(0, 0, 1 if side == "n" else -1)
		else:
			o2 = Vector3(r[0] if side == "w" else r[2], 0, cz)
			axw = Vector3(0, 0, 1); u0 = r[1] - cz; u1 = r[3] - cz
			nrm = Vector3(1 if side == "w" else -1, 0, 0)
		var notches = []
		for hid in halls:
			var hz = zones[hid]
			var hr = hz.rect
			var hc = ((hr[0] + hr[2]) * 0.5 - cx) if horiz else ((hr[1] + hr[3]) * 0.5 - cz)
			notches.append([hc, float(hz.vault_half)])
		notches.sort_custom(func(p, q): return p[0] > q[0])
		var clerestory = along_vault and halls.is_empty()
		var bottom = LANE_H
		if clerestory:
			bottom = 6.25
			# band below the windows, the reveal, mullions and glass
			quad(g, "plaster", [o2 + axw * u0 + Vector3.UP * LANE_H, o2 + axw * u1 + Vector3.UP * LANE_H, o2 + axw * u1 + Vector3.UP * 5.0, o2 + axw * u0 + Vector3.UP * 5.0], nrm, [], false, 0.25)
			quad(g, "trim_tan", [o2 + axw * u0 + Vector3.UP * 5.0, o2 + axw * u1 + Vector3.UP * 5.0, o2 + axw * u1 + Vector3.UP * 5.0 - nrm * 0.3, o2 + axw * u0 + Vector3.UP * 5.0 - nrm * 0.3], Vector3.UP)
			quad(g, "trim_tan", [o2 + axw * u0 + Vector3.UP * 6.25, o2 + axw * u1 + Vector3.UP * 6.25, o2 + axw * u1 + Vector3.UP * 6.25 - nrm * 0.3, o2 + axw * u0 + Vector3.UP * 6.25 - nrm * 0.3], Vector3.DOWN)
			var u = u0
			while u <= u1 + 0.01:
				box(g, "trim_tan", o2 + axw * u + Vector3.UP * 5.62 - nrm * 0.15, abs_size(axw, 0.14, 1.25, 0.3, nrm))
				u += 2.0
			quad("glass", "glass", [o2 + axw * u0 + Vector3.UP * 5.0 - nrm * 0.3, o2 + axw * u1 + Vector3.UP * 5.0 - nrm * 0.3, o2 + axw * u1 + Vector3.UP * 6.25 - nrm * 0.3, o2 + axw * u0 + Vector3.UP * 6.25 - nrm * 0.3], nrm, [], true)
		var o = PackedVector2Array()
		o.append(Vector2(u0, bottom))
		if along_vault:
			o.append(Vector2(u0, COURT_SPRING)); o.append(Vector2(u1, COURT_SPRING))
		else:
			for p in pts:
				o.append(Vector2(p.x, p.y))
		o.append(Vector2(u1, bottom))
		if not clerestory:
			for nt in notches:
				var c = nt[0]
				var vh = nt[1]
				if vh <= 0.0:
					continue
				var hrise = hall_rise(vh)
				o.append(Vector2(c + vh, LANE_H))
				var ap = arch_pts(vh, VAULT_SPRING, hrise, 16)
				ap.reverse()
				for p in ap:
					o.append(Vector2(c + p.x, p.y))
				o.append(Vector2(c - vh, LANE_H))
		poly(g, vmat, o, o2, axw, Vector3.UP, nrm)
		# trim: cornice at the springing on long sides, arch band on the ends
		if along_vault:
			box(g, "trim_tan", o2 + Vector3.UP * 6.28 + nrm * 0.12, abs_size(axw, u1 - u0, 0.12, 0.24, nrm))
			# hidden cove on top of the cornice: an emissive strip (night only)
			# and three up-lights washing the vault
			quad(g, cove_mat, [o2 + axw * u0 + Vector3.UP * 6.35 + nrm * 0.03, o2 + axw * u1 + Vector3.UP * 6.35 + nrm * 0.03, o2 + axw * u1 + Vector3.UP * 6.35 + nrm * 0.2, o2 + axw * u0 + Vector3.UP * 6.35 + nrm * 0.2], Vector3.UP)
			for f in [0.2, 0.5, 0.8]:
				var up = o2 + axw * lerp(u0, u1, f) + Vector3.UP * 6.45 + nrm * 0.15
				tag(add_spot(up, (Vector3.UP * 1.0 + nrm * 0.55), 3.0, 14.0, 70.0, cove_col), "night")
		else:
			for i in pts.size() - 1:
				var a = pts[i]
				var b = pts[i + 1]
				var ia = a + (Vector2(0, cy) - a).normalized() * 0.55
				var ib = b + (Vector2(0, cy) - b).normalized() * 0.55
				var off = nrm * 0.1
				quad(g, "trim_tan", [o2 + axw * a.x + Vector3.UP * a.y + off, o2 + axw * b.x + Vector3.UP * b.y + off, o2 + axw * ib.x + Vector3.UP * ib.y + off, o2 + axw * ia.x + Vector3.UP * ia.y + off], nrm)
	# columns at the inner corners
	var inset = 1.3
	for qx in [r[0] + inset, r[2] - inset]:
		for qz in [r[1] + inset, r[3] - inset]:
			cyl(g, "column", Vector3(qx, 0.35, qz), 0.3, 0.3, COURT_SPRING - 0.6, 24, false)
			cyl(g, "stone", Vector3(qx, 0, qz), 0.4, 0.4, 0.35, 24, true)
			cyl(g, "column", Vector3(qx, COURT_SPRING - 0.25, qz), 0.3, 0.42, 0.25, 24, true, true)
			obst([qx, qz, 0.55])
	if z.style == "sears":
		# white arch beam across the court, outlined with a pink stripe (1:34),
		# and a small crystal pendant under the crown
		var axs = P.call(0, 0, 1) - P.call(0, 0, 0)
		for sbeam in [-length * 0.25, length * 0.25]:
			for i in pts.size() - 1:
				var a = pts[i]
				var b = pts[i + 1]
				if abs(a.x) > half - 0.05 and abs(b.x) > half - 0.05:
					continue
				var ia = a + (Vector2(0, cy) - a).normalized() * 0.45
				var ib = b + (Vector2(0, cy) - b).normalized() * 0.45
				var mid2 = (ia + ib) * 0.5
				var nn2 = (P.call(0, cy, 0) - P.call(mid2.x, mid2.y, 0)).normalized()
				quad(g, "rib", [P.call(ia.x, ia.y, sbeam - 0.35), P.call(ib.x, ib.y, sbeam - 0.35), P.call(ib.x, ib.y, sbeam + 0.35), P.call(ia.x, ia.y, sbeam + 0.35)], nn2)
				for sg in [-1.0, 1.0]:
					quad(g, "rib", [P.call(a.x, a.y, sbeam + sg * 0.35), P.call(b.x, b.y, sbeam + sg * 0.35), P.call(ib.x, ib.y, sbeam + sg * 0.35), P.call(ia.x, ia.y, sbeam + sg * 0.35)], axs * sg)
					var ja = ia + (a - ia) * 0.12
					var jb = ib + (b - ib) * 0.12
					var ka = ia + (a - ia) * 0.3
					var kb = ib + (b - ib) * 0.3
					quad(g, "pink_stripe", [P.call(ja.x, ja.y, sbeam + sg * 0.36), P.call(jb.x, jb.y, sbeam + sg * 0.36), P.call(kb.x, kb.y, sbeam + sg * 0.36), P.call(ka.x, ka.y, sbeam + sg * 0.36)], axs * sg)
		var crown = COURT_SPRING + rise
		cyl("lanterns", "brass", P.call(0, 5.9, 0), 0.012, 0.012, crown - 5.9, 6, false)
		# small tiered crystal pendant: rings of drops around a centre drop
		var pc = P.call(0, 5.6, 0)
		cyl("lanterns", "brass", pc + Vector3(0, 0.25, 0), 0.32, 0.32, 0.03, 16, true, true)
		for tier in 3:
			var rr = 0.3 - tier * 0.09
			var cnt = 10 - tier * 3
			for k in cnt:
				var a3 = TAU * k / cnt + tier * 0.3
				var dc = pc + Vector3(cos(a3) * rr, 0.15 - tier * 0.16, sin(a3) * rr)
				cyl("lanterns", "crystal", dc - Vector3(0, 0.08, 0), 0.0, 0.035, 0.08, 6, false)
				cyl("lanterns", "crystal", dc, 0.035, 0.0, 0.06, 6, false)
		cyl("lanterns", "crystal", pc - Vector3(0, 0.55, 0), 0.0, 0.07, 0.2, 8, false)
		cyl("lanterns", "crystal", pc - Vector3(0, 0.35, 0), 0.07, 0.0, 0.12, 8, false)
		add_omni(P.call(0, 5.5, 0), 1.0, 7.0, Color(1.0, 0.95, 0.85))
	if z.style == "shoe":
		fx = true
		palm_bed(g + "_props", Vector3(cx, 0, cz), 2.4, 5.0)
		for b in [[-1.75, -1.2, PI * 0.5], [-1.75, 1.2, PI * 0.5], [1.75, -1.2, -PI * 0.5], [1.75, 1.2, -PI * 0.5]]:
			bench(g + "_props", Vector3(cx + b[0], 0, cz + b[1]), b[2])
		fx = false
		for p in [Vector3(-3.8, 4.3, -4.2), Vector3(3.8, 4.3, -4.2), Vector3(-3.8, 4.3, 4.2), Vector3(3.8, 4.3, 4.2)]:
			var lp = Vector3(cx, 0, cz) + p
			lantern(lp, arch_y(p.x, half, COURT_SPRING, rise))

## Dillard's court (3:34): a higher flat ceiling ringed by a soffit whose
## hidden cove glows warm onto it, with a rectangular skylight well.
func build_court_flat(z):
	var g = z.id
	var r = z.rect
	var cx = (r[0] + r[2]) * 0.5
	var cz = (r[1] + r[3]) * 0.5
	var CH = 7.6
	var SOF = 6.9
	var ring = 1.4
	# soffit ring (underside), its inner face, and the cove strip on top
	var inner = [r[0] + ring, r[1] + ring, r[2] - ring, r[3] - ring]
	var outer_pts = [Vector3(r[0], SOF, r[1]), Vector3(r[2], SOF, r[1]), Vector3(r[2], SOF, r[3]), Vector3(r[0], SOF, r[3])]
	var inner_pts = [Vector3(inner[0], SOF, inner[1]), Vector3(inner[2], SOF, inner[1]), Vector3(inner[2], SOF, inner[3]), Vector3(inner[0], SOF, inner[3])]
	for i in 4:
		var j = (i + 1) % 4
		quad(g, "lane_ceiling", [outer_pts[i], outer_pts[j], inner_pts[j], inner_pts[i]], Vector3.DOWN)
		var lip = Vector3(0, 0.35, 0)
		var inward = (Vector3(cx, SOF, cz) - (inner_pts[i] + inner_pts[j]) * 0.5)
		inward = Vector3(sign(inward.x) if abs(inward.x) > abs(inward.z) else 0, 0, sign(inward.z) if abs(inward.z) >= abs(inward.x) else 0)
		quad(g, "bulkhead", [inner_pts[i], inner_pts[j], inner_pts[j] + lip, inner_pts[i] + lip], inward)
		quad(g, "bulkhead", [inner_pts[i] + lip, inner_pts[j] + lip, inner_pts[j] + lip - inward * 0.08, inner_pts[i] + lip - inward * 0.08], Vector3.UP)
		var cv0 = inner_pts[i] - inward * 0.3 + Vector3(0, 0.02, 0)
		var cv1 = inner_pts[j] - inward * 0.3 + Vector3(0, 0.02, 0)
		quad(g, "cove", [cv0, cv1, cv1 - inward * 0.25, cv0 - inward * 0.25], Vector3.UP)
	# upper ceiling with a rectangular skylight well
	var swx = min(6.0, (r[2] - r[0]) * 0.3)
	var swz = min(4.0, (r[3] - r[1]) * 0.2)
	var hx0 = cx - swx * 0.5
	var hx1 = cx + swx * 0.5
	var hz0 = cz - swz * 0.5
	var hz1 = cz + swz * 0.5
	for rr in [[r[0], r[1], r[2], hz0], [r[0], hz1, r[2], r[3]], [r[0], hz0, hx0, hz1], [hx1, hz0, r[2], hz1]]:
		quad(g, "lane_ceiling", [Vector3(rr[0], CH, rr[1]), Vector3(rr[2], CH, rr[1]), Vector3(rr[2], CH, rr[3]), Vector3(rr[0], CH, rr[3])], Vector3.DOWN)
	var top = CH + 1.2
	for wall in [[Vector3(hx0, CH, hz0), Vector3(hx1, CH, hz0), Vector3(0, 0, 1)], [Vector3(hx1, CH, hz1), Vector3(hx0, CH, hz1), Vector3(0, 0, -1)], [Vector3(hx0, CH, hz1), Vector3(hx0, CH, hz0), Vector3(1, 0, 0)], [Vector3(hx1, CH, hz0), Vector3(hx1, CH, hz1), Vector3(-1, 0, 0)]]:
		quad(g, "lane_ceiling", [wall[0], wall[1], wall[1] + Vector3(0, top - CH, 0), wall[0] + Vector3(0, top - CH, 0)], wall[2])
	for k in 5:
		var u = hx0 + (hx1 - hx0) * k / 4.0
		box("glass_frames", "metal_dark", Vector3(u, top - 0.05, cz), Vector3(0.05, 0.1, swz), Transform3D.IDENTITY, [], true)
	add_omni(Vector3(cx, 6.0, cz), 1.2, 16.0, Color(1.0, 0.88, 0.72))
	# perimeter walls from the lane ceiling up to the soffit, notched for hall vaults
	var sides = {}
	for cw in L.court_walls:
		if cw.zone == z.id:
			sides[cw.side] = cw.halls
	for side in ["n", "s", "w", "e"]:
		var horiz = side in ["n", "s"]
		var o2 = Vector3(cx, 0, r[1] if side == "n" else r[3]) if horiz else Vector3(r[0] if side == "w" else r[2], 0, cz)
		var axw = Vector3(1, 0, 0) if horiz else Vector3(0, 0, 1)
		var nrm = Vector3(0, 0, 1 if side == "n" else -1) if horiz else Vector3(1 if side == "w" else -1, 0, 0)
		var u0 = (r[0] - cx) if horiz else (r[1] - cz)
		var u1 = (r[2] - cx) if horiz else (r[3] - cz)
		var o = PackedVector2Array([Vector2(u0, LANE_H), Vector2(u0, SOF), Vector2(u1, SOF), Vector2(u1, LANE_H)])
		var notches = []
		for hid in sides.get(side, []):
			var hz = zones[hid]
			var hr = hz.rect
			notches.append([((hr[0] + hr[2]) * 0.5 - cx) if horiz else ((hr[1] + hr[3]) * 0.5 - cz), float(hz.vault_half)])
		notches.sort_custom(func(p, q): return p[0] > q[0])
		for nt in notches:
			if nt[1] <= 0.0:
				continue
			var hrise = hall_rise(nt[1])
			o.append(Vector2(nt[0] + nt[1], LANE_H))
			var ap = arch_pts(nt[1], VAULT_SPRING, hrise, 16)
			ap.reverse()
			for p in ap:
				o.append(Vector2(nt[0] + p.x, p.y))
			o.append(Vector2(nt[0] - nt[1], LANE_H))
		poly(g, "cream", o, o2, axw, Vector3.UP, nrm)
		# wall between soffit and upper ceiling, behind the cove
		quad(g, "cream", [o2 + axw * u0 + Vector3.UP * SOF, o2 + axw * u1 + Vector3.UP * SOF, o2 + axw * u1 + Vector3.UP * CH, o2 + axw * u0 + Vector3.UP * CH], nrm)
		box(g, "trim_tan", o2 + Vector3.UP * (LANE_H + 0.06) + nrm * 0.1, abs_size(axw, u1 - u0, 0.12, 0.2, nrm))
	var inset = 1.3
	for qx in [r[0] + inset, r[2] - inset]:
		for qz in [r[1] + inset, r[3] - inset]:
			cyl(g, "column", Vector3(qx, 0.35, qz), 0.3, 0.3, SOF - 0.35, 24, false)
			cyl(g, "stone", Vector3(qx, 0, qz), 0.4, 0.4, 0.35, 24, true)
			obst([qx, qz, 0.55])

# ------------------------------------------------------------------ lights
## Since Godot 4.7 the lightmapper lights the mall mostly from glowing surfaces
## (downlight discs at emission 8, the vault glow strip, store panels); a bake
## with emission off drops the Sears hall from luma 189 to 94, while spot/omni/
## sun/sky changes move it by 1-2 points. The Sears hall is the narrowest hall
## (10 m) and came out washed out at Ultra (Steven, Oct 5), so its meshes get
## their glow scaled down, in both the day and the night setup.
const HALL_GLOW = {"H1a": 0.7, "H1b": 0.7}

## mat(mname), with its emission (and the per-setup e_day / e_night metadata
## read by scripts/time_of_day.gd) scaled by HALL_GLOW for the halls listed there.
func glow_mat(gname, mname):
	var m = mat(mname)
	if not HALL_GLOW.has(gname) or not m.emission_enabled:
		return m
	var k = HALL_GLOW[gname]
	m = m.duplicate()
	m.emission_energy_multiplier *= k
	for key in ["e_day", "e_night"]:
		if m.has_meta(key):
			m.set_meta(key, m.get_meta(key) * k)
	return m

func disc_down(group, c, rad):
	var s = st(group, "downlight")
	var seg = 12
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		tri(s, c, c + Vector3(cos(a0), 0, sin(a0)) * rad, c + Vector3(cos(a1), 0, sin(a1)) * rad, Vector2(0.5, 0.5), Vector2(0, 0), Vector2(1, 0), Vector3.DOWN)

func add_downlight(c):
	var l = SpotLight3D.new()
	l.position = c + Vector3(0, -0.05, 0)
	l.rotation = Vector3(-PI / 2, 0, 0)
	l.spot_angle = 58.0
	l.spot_attenuation = 0.8
	l.spot_range = 7.0
	l.light_energy = 1.5
	l.light_color = Color(1.0, 0.92, 0.80)
	l.light_bake_mode = Light3D.BAKE_STATIC
	light_root.add_child(l)
	tag(l, "", 1.5, 1.4)

func add_omni(p, energy, rng, col, shadow = false):
	var l = OmniLight3D.new()
	l.position = p
	l.omni_range = rng
	l.light_energy = energy
	l.light_color = col
	l.light_bake_mode = Light3D.BAKE_STATIC
	l.shadow_enabled = shadow
	light_root.add_child(l)
	return l

## Time-of-day tags read by scripts/time_of_day.gd: "only" = "day"/"night"
## (the light exists in that bake only); e_day / e_night = energy per bake.
func tag(l, only = "", e_day = null, e_night = null):
	if only != "":
		l.set_meta("only", only)
	if e_day != null:
		l.set_meta("e_day", e_day)
	if e_night != null:
		l.set_meta("e_night", e_night)
	return l

func add_spot(p, dir, energy, rng, angle, col):
	var l = SpotLight3D.new()
	l.position = p
	l.light_energy = energy
	l.light_color = col
	l.spot_range = rng
	l.spot_angle = angle
	l.spot_attenuation = 0.9
	l.light_bake_mode = Light3D.BAKE_STATIC
	light_root.add_child(l)
	l.transform = Transform3D(Basis.looking_at(dir.normalized(), Vector3.UP if abs(dir.normalized().y) < 0.99 else Vector3.FORWARD), p)
	return l

# ------------------------------------------------------------------ edges
func zone_at(x, z):
	for zid in zones:
		var r = zones[zid].rect
		if x >= r[0] and x <= r[2] and z >= r[1] and z <= r[3]:
			return zid
	return "misc"

## An owner-editable sign (scripts/signs.gd draws its text live over a blank copy of the
## art). `faces`: [[p0, p1, p2, p3], [uv0..uv3], normal] per face, p0->p1 along the text,
## p0->p3 up, with an optional 4th element: a dict of per-face overrides copied into the
## face record (tex, band, span, look, lit; see signs.gd); `style` picks the look (font,
## colours) in signs.gd.
func sign_add(id, kind, title, style, faces, extra = {}):
	var F = []
	for f in faces:
		var pts = []
		var uvs = []
		for p in f[0]:
			pts.append([snappedf(p.x, 0.0001), snappedf(p.y, 0.0001), snappedf(p.z, 0.0001)])
		for q in f[1]:
			uvs.append([snappedf(q.x, 0.00001), snappedf(q.y, 0.00001)])
		var rec_f = {"p": pts, "uv": uvs, "n": [snappedf(f[2].x, 0.0001), snappedf(f[2].y, 0.0001), snappedf(f[2].z, 0.0001)]}
		# optional per-face overrides: "tex" (word-free art for this face), "band" [top, bottom]
		# and "span" [left, right] (where the words go, as fractions of the face), "look", "lit"
		if f.size() > 3 and f[3] is Dictionary:
			rec_f.merge(f[3])
		F.append(rec_f)
	var rec = {"id": id, "kind": kind, "title": title, "style": style, "faces": F}
	rec.merge(extra)
	signs.append(rec)

func label(text, fontname, fg, pos, n, max_w, cap_h = 0.56):
	var lab = Label3D.new()
	lab.text = text
	var fnt = load("res://fonts/" + {"sans": "sans.otf", "serif": "serif.ttf", "script": "script.ttf", "sans_italic": "sans_italic.otf"}[fontname])
	lab.font = fnt
	lab.font_size = 128
	lab.modulate = Color(fg)
	var est = text.length() * 128 * (0.6 if fontname == "serif" else 0.5)
	var txt_w = max(fnt.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 128).x, est)
	var px = cap_h / 128.0
	if txt_w * px > max_w:
		px = max_w / txt_w
	lab.pixel_size = px
	lab.shaded = false
	lab.double_sided = false
	lab.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	lab.position = pos
	lab.basis = Basis.looking_at(-n, Vector3.UP)
	mall.add_child(lab)
	return lab

func edge_basics(e):
	var a = Vector3(e.a[0], 0, e.a[1])
	var b = Vector3(e.b[0], 0, e.b[1])
	var n = Vector3(e.n[0], 0, e.n[1])
	return [a, b, n, (b - a).normalized(), a.distance_to(b)]

func plain_wall(g, a, b, n, top = LANE_H, wm = "cream"):
	var t = (b - a).normalized()
	quad(g, wm, [a, b, b + Vector3(0, top, 0), a + Vector3(0, top, 0)], n)
	box(g, "stone", (a + b) * 0.5 + Vector3(0, 0.3, 0) + n * 0.03, abs_size(t, a.distance_to(b), 0.6, 0.06, n))

func build_edge(e):
	var eb = edge_basics(e)
	var a = eb[0]
	var b = eb[1]
	var n = eb[2]
	var t = eb[3]
	var Ln = eb[4]
	var mid = (a + b) * 0.5
	var g = zone_at(mid.x + n.x * 1.0, mid.z + n.z * 1.0)
	match e.kind:
		"wall":
			plain_wall(g, a, b, n)
		"store":
			var sd0 = L.stores[e.store]
			if sd0.anchor and Ln > ANCHOR_FRONT + 1.0:
				# An anchor's mall entrance is one storefront about as wide as
				# JCPenney's (Steven, Oct 5), centred where the mall approaches
				# it; the rest of its frontage is solid wall.
				var c = Ln * 0.5
				var zid = zone_at(mid.x + n.x * 2.0, mid.z + n.z * 2.0)
				for zz in L.zones:
					if zz.type == "court":
						var r = zz.rect
						var cc = Vector3((r[0] + r[2]) * 0.5, 0, (r[1] + r[3]) * 0.5)
						var along = (cc - a).dot(t)
						var dist = abs((cc - a).dot(n))
						if along > 0 and along < Ln and dist < 20.0:
							c = along
				var s0 = clamp(c - ANCHOR_FRONT * 0.5, 0.0, Ln - ANCHOR_FRONT)
				var s1 = s0 + ANCHOR_FRONT
				var wm = ANCHOR_LOOK.get(sd0.name, {}).get("wall", "cream")
				if s0 > 0.01:
					plain_wall(g, a, a + t * s0, n, LANE_H, wm)
				storefront(g, e, a + t * s0, a + t * s1, n, t, ANCHOR_FRONT)
				if s1 < Ln - 0.01:
					plain_wall(g, a + t * s1, b, n, LANE_H, wm)
			else:
				storefront(g, e, a, b, n, t, Ln)
		"exit", "entrance":
			doors_out(g, e, a, b, n, t, Ln)
		"restroom":
			plain_wall(g, a, b, n)
			var sd = L.stores[e.store]
			var dp = a + t * min(1.6, Ln * 0.3)
			box(g, "door_wood", dp + Vector3(0, 1.05, 0) + n * 0.03, abs_size(t, 0.95, 2.1, 0.06, n))
			box(g, "bronze", dp + Vector3(0, 2.15, 0) + n * 0.03, abs_size(t, 1.1, 0.1, 0.08, n))
			label(sd.name.capitalize(), "sans", "#ffffff", dp + Vector3(0, 2.55, 0) + n * 0.06, n, 1.2, 0.22)
			cur_color = Color("#2b4a8a")
			box(g, "vcolor", dp + Vector3(0, 2.55, 0) + n * 0.03, abs_size(t, 1.3, 0.34, 0.04, n))
			cur_color = Color.WHITE

## A storefront along one frontage: pilasters with a stone base, bulkhead with
## the sign, bronze-framed glass (or an open front), the lit interior behind.
func storefront(g, e, a, b, n, t, Ln, inner_call = false):
	var sd = L.stores[e.store]
	if sd.name == "K&B" and not inner_call and Ln > 12.0:
		# K&B's frontage was a pink wall with plum stripes (decision 6), with
		# the store entrance in the middle
		var ew = 8.0
		var m0 = Ln * 0.5 - ew * 0.5
		kb_wall(g, a, a + t * m0, n, t)
		kb_wall(g, a + t * (m0 + ew), b, n, t)
		storefront(g, e, a + t * m0, a + t * (m0 + ew), n, t, ew, true)
		return
	if sd.anchor and ANCHOR_LOOK.has(sd.name):
		anchor_front(g, e, a, b, n, t, Ln, sd, ANCHOR_LOOK[sd.name])
		return
	if sd.name == "POCKET CHANGE" and not inner_call:
		# built in full 3D from Steven's 2009 photo of the unchanged front, with a walkable arcade (Phase 4b)
		load("res://tools/stores/pocket_change/store.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name == "KAY-BEE TOYS" and not inner_call:
		# built in full 3D: the front from Steven's photo of the Southland store, the inside from
		# the 1993 Kay-Bee home video he chose (design/storefronts/kay-bee-toys.md)
		load("res://tools/stores/kay_bee/store.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name in ["JW", "5-7-9", "COUNTY SEAT"] and not inner_call:
		# built in full 3D after the 1995 North East Mall video Steven chose: the signs and the
		# stock from the video, the layouts guessed (design/storefronts/jw.md, 579.md, county-seat.md)
		var mod = {"JW": "jw", "5-7-9": "s579", "COUNTY SEAT": "county_seat"}[sd.name]
		load("res://tools/stores/apparel/%s.gd" % mod).build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name in ["LERNER SHOP", "LANE BRYANT", "MILLER'S OUTPOST", "GADZOOKS", "THE LIMITED"] and not inner_call:
		# built in full 3D on the apparel kit from the regional videos Steven sent (Hammond
		# 1993, Pecanland 1992, the Gadzooks slideshow); layouts guessed (design/storefronts/
		# lerner.md, lane-bryant.md, millers-outpost.md, gadzooks.md, limited.md)
		load("res://tools/stores/apparel/more.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name == "WOOLWORTH" and not inner_call:
		# built in full 3D: the front from the facade record, the inside from the 1991
		# Statesville video Steven chose, the restaurant on the right with its own mall door
		# (design/storefronts/woolworth.md)
		load("res://tools/stores/woolworth/store.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name in ["BABBAGE'S", "SOUND SHOP"] and not inner_call:
		# built in full 3D with the media kit: Babbage's from the 1997 Killeen Mall video, Sound
		# Shop from the 1993 Hammond Square commercial, both laid out to Steven's memory
		# (design/storefronts/babbages.md, sound-shop.md); Babbage's jog edge comes here too
		var mod = {"BABBAGE'S": "babbages", "SOUND SHOP": "sound_shop"}[sd.name]
		load("res://tools/stores/media/%s.gd" % mod).build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name == "GUMBALLS" and not inner_call:
		# built in full 3D on the court corner: the sign and the inside from the 1995 North East
		# Mall video Steven chose (design/storefronts/gumballs.md); both frontage edges come here
		load("res://tools/stores/gumballs/store.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	if sd.name == "CORN DOG 7" and not inner_call:
		# built in full 3D from the photographs of the unchanged shop (Phase 4b)
		preload("res://tools/stores/corn_dog_7.gd").build(self, g, e, a, b, n, t, Ln, sd)
		return
	var fa = fronts.get(edge_key(e.a, e.b))
	if fa != null and not inner_call:
		front_art(g, e, a, b, n, t, Ln, sd, fa)
		return
	var pil = 0.4 if Ln > 2.5 else 0.25
	var anchor = sd.anchor
	var deep = clip_deep(a, b, n, clamp(float(e.depth), 3.0, 14.0 if anchor else 9.0))
	for ee in [0.0, Ln - pil]:
		var c0 = a + t * (ee + pil * 0.5)
		box(g, "stone", c0 + Vector3(0, 0.45, 0) + n * 0.06, abs_size(t, pil, 0.9, 0.12, n))
		box(g, "cream", c0 + Vector3(0, (OPEN_H + 0.9) * 0.5, 0) + n * 0.03, abs_size(t, pil, OPEN_H - 0.9, 0.06, n))
	var mid = a + t * Ln * 0.5
	box(g, "bulkhead", mid + Vector3(0, (OPEN_H + LANE_H) * 0.5, 0) + n * 0.08, abs_size(t, Ln, LANE_H - OPEN_H, 0.16, n))
	# sign
	var text = sd.sign
	if sd.vacant:
		text = "For Lease" + ((" · Space %d" % int(sd.unit)) if sd.unit != null else "")
	if text != "" and not sd.noSign and Ln >= 1.5:
		var sw = min(Ln - 0.8, max(1.6, min(Ln * 0.72, 9.0 if anchor else 6.5)))
		var sh = 0.95 if anchor else 0.78
		var sc = mid + Vector3(0, OPEN_H + (LANE_H - OPEN_H) * 0.5, 0) + n * 0.2
		cur_color = Color("#3a3a3a") if sd.vacant else Color(sd.bg)
		box(g, "vcolor", sc, abs_size(t, sw, sh, 0.08, n))
		cur_color = Color.WHITE
		label(text, "sans" if sd.vacant else sd.font, "#f2efe6" if sd.vacant else sd.fg, sc + n * 0.05, n, sw * 0.88, 0.62 if anchor else 0.56)
	var inner0 = pil
	var inner1 = Ln - pil
	var p0 = a + t * inner0
	var p1 = a + t * inner1
	var width = inner1 - inner0
	if sd.vacant:
		# closed grille in front of a dark space
		quad(g, "grille", [p0, p1, p1 + Vector3(0, OPEN_H, 0), p0 + Vector3(0, OPEN_H, 0)], n, [], false, 1.0)
		var k = 0.0
		while k < OPEN_H:
			box(g, "metal_dark", (p0 + p1) * 0.5 + Vector3(0, k, 0) + n * 0.02, abs_size(t, width, 0.03, 0.03, n))
			k += 0.18
		return
	var ov = OVERRIDES.get(sd.name, {})
	if sd.awning and (sd.awningColor != null or ov.has("awningColor")):
		cur_color = Color(ov.get("awningColor", sd.awningColor))
		var aw0 = a + t * Ln * 0.5 + Vector3(0, OPEN_H + 0.05, 0)
		var xf = Transform3D(Basis.looking_at(-n, Vector3.UP) * Basis(Vector3.RIGHT, 0.45), aw0 + n * 0.45)
		box(g, "vcolor_matte", Vector3.ZERO, Vector3(Ln - 0.2, 0.06, 1.0), xf)
		box(g, "vcolor_matte", aw0 + n * 0.9 + Vector3(0, -0.32, 0), abs_size(t, Ln - 0.2, 0.25, 0.04, n))
		if ov.has("awningStripe"):
			cur_color = Color(ov.awningStripe)
			box(g, "vcolor_matte", aw0 + n * 0.925 + Vector3(0, -0.26, 0), abs_size(t, Ln - 0.2, 0.06, 0.02, n))
		cur_color = Color.WHITE
	var door_w = width if sd.open else min(3.0 if not anchor else 8.0, width * 0.45)
	if sd.entry != null:
		door_w = min(width, float(sd.entry) * 2.0)
	var d0 = Ln * 0.5 - door_w * 0.5
	var d1 = Ln * 0.5 + door_w * 0.5
	if not sd.open:
		for seg in [[inner0, d0], [d1, inner1]]:
			var s0 = seg[0]
			var s1 = seg[1]
			if s1 - s0 < 0.1:
				continue
			var cc = a + t * (s0 + s1) * 0.5
			box(g, "stone", cc + Vector3(0, 0.2, 0), abs_size(t, s1 - s0, 0.4, 0.2, n))
			quad("glass", "glass", [a + t * s0 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, OPEN_H, 0), a + t * s0 + Vector3(0, OPEN_H, 0)], n, [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
			var cnt = max(1, int(round((s1 - s0) / 1.5)))
			for k in cnt + 1:
				var mp = a + t * (s0 + (s1 - s0) * k / cnt)
				box(g, "bronze", mp + Vector3(0, (OPEN_H + 0.4) * 0.5, 0), abs_size(t, 0.06, OPEN_H - 0.4, 0.1, n))
	box(g, "bronze", mid + Vector3(0, OPEN_H - 0.04, 0), abs_size(t, width, 0.08, 0.12, n))
	interior(g, e, a, n, t, Ln, sd, p0, p1, width, deep)
	if sd.name.contains("CINEMA"):
		cinema_front(g, a, n, t, Ln)

## How deep a store's generic interior may run before it would enter a store built in full 3D.
func clip_deep(a, b, n, deep):
	var into = -n
	for nm in BUILT_RECTS:
		var r = BUILT_RECTS[nm]
		# the strip from the frontage a..b running `deep` metres along `into`
		var lo_x = min(a.x, b.x); var hi_x = max(a.x, b.x)
		var lo_z = min(a.z, b.z); var hi_z = max(a.z, b.z)
		if abs(into.z) > 0.5:
			if hi_x <= r[0] + 0.01 or lo_x >= r[2] - 0.01:
				continue
			var gap = (r[1] - a.z) if into.z > 0 else (a.z - r[3])
			if gap >= -0.01:
				deep = min(deep, max(gap - 0.05, 0.5))
		else:
			if hi_z <= r[1] + 0.01 or lo_z >= r[3] - 0.01:
				continue
			var gap2 = (r[0] - a.x) if into.x > 0 else (a.x - r[2])
			if gap2 >= -0.01:
				deep = min(deep, max(gap2 - 0.05, 0.5))
	return deep

func edge_key(pa, pb):
	return "%.1f,%.1f|%.1f,%.1f" % [pa[0], pa[1], pb[0], pb[1]]

## The store behind a frontage: back wall and side walls from the interior
## atlas, floor, ceiling with lit panels, merchandise blocks, and its lights.
func interior(g, e, a, n, t, Ln, sd, p0, p1, width, deep):
	var back = -n * deep
	var cell = atlas_index.get(e.store, 0)
	var cu = float(cell % ATLAS_COLS) / ATLAS_COLS
	var cv = float(cell / ATLAS_COLS) / ATLAS_ROWS
	var du = 1.0 / ATLAS_COLS
	var dv = 1.0 / ATLAS_ROWS
	var reps = max(1, int(round(width / 6.0)))
	for k in reps:
		var q0 = p0 + t * (width * k / reps)
		var q1 = p0 + t * (width * (k + 1) / reps)
		quad(g, "int_back", [q0 + back, q1 + back, q1 + back + Vector3(0, OPEN_H, 0), q0 + back + Vector3(0, OPEN_H, 0)], n,
			[Vector2(cu, cv + dv), Vector2(cu + du, cv + dv), Vector2(cu + du, cv), Vector2(cu, cv)])
	# side walls carry the same store picture, so the glass shows the right kind of store at an angle
	var su = du * clamp(deep / 6.0, 0.3, 1.0)
	quad(g, "int_back", [p0, p0 + back, p0 + back + Vector3(0, OPEN_H, 0), p0 + Vector3(0, OPEN_H, 0)], t,
		[Vector2(cu, cv + dv), Vector2(cu + su, cv + dv), Vector2(cu + su, cv), Vector2(cu, cv)])
	quad(g, "int_back", [p1 + back, p1, p1 + Vector3(0, OPEN_H, 0), p1 + back + Vector3(0, OPEN_H, 0)], -t,
		[Vector2(cu + du - su, cv + dv), Vector2(cu + du, cv + dv), Vector2(cu + du, cv), Vector2(cu + du - su, cv)])
	cur_color = Color(sd.carpet) if sd.carpet != null else Color("#d8d2c6")
	quad(g, "int_floor", [p0, p1, p1 + back, p0 + back], Vector3.UP)
	cur_color = Color.WHITE
	quad(g, "int_wall", [p0 + Vector3(0, OPEN_H, 0), p0 + back + Vector3(0, OPEN_H, 0), p1 + back + Vector3(0, OPEN_H, 0), p1 + Vector3(0, OPEN_H, 0)], Vector3.DOWN)
	var rows = max(1, int(deep / 3.0))
	var cols = max(1, int(width / 3.0))
	for ri in rows:
		for ci in cols:
			var pc = p0 + t * (width * (ci + 0.5) / cols) - n * (deep * (ri + 0.5) / rows) + Vector3(0, OPEN_H - 0.01, 0)
			quad(g, "int_panel", [pc - t * 0.5 - n * 0.3, pc + t * 0.5 - n * 0.3, pc + t * 0.5 + n * 0.3, pc - t * 0.5 + n * 0.3], Vector3.DOWN)
	var mc = sd.merch
	var k2 = 0
	var pos = 1.4
	while pos < width - 0.8:
		cur_color = Color(mc[k2 % mc.size()])
		box(g, "vcolor", p0 + t * pos - n * (deep * 0.45) + Vector3(0, 0.45, 0), abs_size(t, 1.2, 0.9, 0.8, n))
		pos += 2.8
		k2 += 1
	cur_color = Color.WHITE
	var sl = add_omni(a + t * Ln * 0.5 - n * min(1.5, deep * 0.4) + Vector3(0, OPEN_H - 0.4, 0), 0.45, max(deep + 1.0, 6.0), Color(1.0, 0.96, 0.9))
	tag(sl, "", 0.45, 1.2)
	if Ln >= 2.0:
		var spill_at = a + t * Ln * 0.5 - n * 0.4 + Vector3(0, OPEN_H - 0.15, 0)
		tag(add_spot(spill_at, n * 0.9 + Vector3.DOWN * 1.0, 1.6, 7.0, 55.0, Color("#FFF1DC")), "night")

## A storefront painted by the live game (Phase 4, tools/capture_fronts.py):
## the painting covers the frontage floor to lane ceiling; its fascia band
## (rows 17..56 of 150 in the live game's drawing) stands 12 cm proud with
## returns; the end piers are real; door tiles are open onto the 3D interior
## with reveals, and an open front shows the whole interior under the fascia.
## Anchors keep their own 3D fronts. The picture is drawn as seen from the
## hall, so on an edge that runs right-to-left for that viewer it is mirrored.
const FRONT_ROWS = 150.0
const FASCIA_TOP_PX = 17.0
const FASCIA_BOT_PX = 56.0
func front_art(g, e, a, b, n, t, Ln, sd, fa):
	var uv = fa.uv
	var tiles = int(fa.tiles)
	var flip = bool(fa.flip)
	var H = LANE_H
	var y_top = H * (1.0 - FASCIA_TOP_PX / FRONT_ROWS)
	var y_bot = H * (1.0 - FASCIA_BOT_PX / FRONT_ROWS)
	var tu = func(f):   # fraction along the edge -> atlas u
		return uv[0] + (uv[2] - uv[0]) * ((1.0 - f) if flip else f)
	var tv = func(y):   # height -> atlas v
		return uv[1] + (uv[3] - uv[1]) * (1.0 - y / H)
	var strip = func(off, f0, f1, y0, y1):
		var q0 = a + t * (f0 * Ln) + off
		var q1 = a + t * (f1 * Ln) + off
		quad(g, "front_art", [q0 + Vector3(0, y0, 0), q1 + Vector3(0, y0, 0), q1 + Vector3(0, y1, 0), q0 + Vector3(0, y1, 0)], n,
			[Vector2(tu.call(f0), tv.call(y0)), Vector2(tu.call(f1), tv.call(y0)), Vector2(tu.call(f1), tv.call(y1)), Vector2(tu.call(f0), tv.call(y1))])
	var doors = []
	for d in fa.doors:
		doors.append(int(d))
	var open_all = bool(fa.open) or (bool(sd.open) and doors.is_empty())
	# wall picture tile by tile: door tiles (or an open front) are open up to the fascia
	for k in tiles:
		var f0 = float(k) / tiles
		var f1 = float(k + 1) / tiles
		if open_all or k in doors:
			strip.call(Vector3.ZERO, f0, f1, y_bot, H)
		else:
			strip.call(Vector3.ZERO, f0, f1, 0.0, H)
	# the fascia band stands proud, with returns
	var fd = 0.12
	strip.call(n * fd, 0.0, 1.0, y_bot, y_top)
	var fb = a + Vector3(0, y_bot, 0)
	var ft = a + Vector3(0, y_top, 0)
	var fh = Vector3(0, y_top - y_bot, 0)
	quad(g, "bulkhead", [fb, fb + n * fd, fb + t * Ln + n * fd, fb + t * Ln], Vector3.DOWN)
	quad(g, "bulkhead", [ft + t * Ln, ft + t * Ln + n * fd, ft + n * fd, ft], Vector3.UP)
	quad(g, "bulkhead", [fb, fb + fh, fb + fh + n * fd, fb + n * fd], -t)
	quad(g, "bulkhead", [fb + t * Ln + n * fd, fb + t * Ln + fh + n * fd, fb + t * Ln + fh, fb + t * Ln], t)
	# end piers over the picture's own (8 px = half a metre at the live scale)
	var pw = min(0.5, Ln * 0.2)
	for ee in [pw * 0.5, Ln - pw * 0.5]:
		var c0 = a + t * ee
		box(g, "white_pilaster", c0 + Vector3(0, y_bot * 0.5, 0) + n * 0.05, abs_size(t, pw, y_bot, 0.10, n))
		box(g, "stone", c0 + Vector3(0, 0.3, 0) + n * 0.08, abs_size(t, pw + 0.04, 0.6, 0.16, n))
	# the accuracy meter's badge (STOREFRONT-FIDELITY.md): a small plaque on the
	# viewer's-left pier in the level's colour, so a walk shows what is sourced
	if facade_levels.has(e.store):
		var lv = clamp(facade_levels[e.store], 0, 4)
		var pier_at = a + t * (Ln - pw * 0.5) if flip else a + t * (pw * 0.5)
		cur_color = Color(LEVEL_COLORS[lv])
		box(g, "vcolor", pier_at + Vector3(0, 1.45, 0) + n * 0.11, abs_size(t, 0.16, 0.16, 0.02, n))
		cur_color = Color.WHITE
	# reveals where a painted wall meets an opening
	var tile_m = Ln / tiles
	if not open_all:
		for k in doors:
			for side in [[k, 1.0], [k + 1, -1.0]]:
				var kk = side[0]
				var neighbour_open = kk - 1 in doors if side[1] > 0 else kk in doors
				if kk <= 0 or kk >= tiles or neighbour_open:
					continue
				var cc = a + t * (kk * tile_m) - n * 0.2 + Vector3(0, y_bot * 0.5, 0)
				box(g, "cream", cc, abs_size(t, 0.06, y_bot, 0.4, n))
	# the interior behind the opening
	if sd.vacant:
		return
	var deep = clamp(float(e.depth), 3.0, 9.0)
	var in0 = pw
	var in1 = Ln - pw
	interior(g, e, a, n, t, Ln, sd, a + t * in0, a + t * in1, in1 - in0, deep)

func kb_wall(g, a, b, n, t):
	var Lw = a.distance_to(b)
	quad(g, "pink", [a, b, b + Vector3(0, LANE_H, 0), a + Vector3(0, LANE_H, 0)], n)
	for y in [1.0, 2.35]:
		box(g, "plum", (a + b) * 0.5 + Vector3(0, y, 0) + n * 0.015, abs_size(t, Lw, 0.16, 0.03, n))
	var k = 0.3
	while k < Lw:
		var c = a + t * k
		box(g, "white_pilaster", c + Vector3(0, LANE_H * 0.5, 0) + n * 0.15, abs_size(t, 0.6, LANE_H, 0.3, n))
		for y in [1.0, 2.35]:
			box(g, "plum", c + Vector3(0, y, 0) + n * 0.31, abs_size(t, 0.62, 0.16, 0.02, n))
		k += 4.0

## Southland Cinema: a marquee with bulbs over the entrance and lit poster cases.
func cinema_front(g, a, n, t, Ln):
	var mid = a + t * Ln * 0.5
	var mw = min(Ln * 0.7, 10.0)
	var mc = mid + Vector3(0, 3.75, 0) + n * 0.9
	cur_color = Color("#1d1a2e")
	box(g, "vcolor", mc, abs_size(t, mw, 0.95, 1.6, n))
	cur_color = Color.WHITE
	box(g, "bulbs", mc + Vector3(0, -0.49, 0), abs_size(t, mw - 0.2, 0.03, 1.4, n))
	box(g, "bulbs", mc + Vector3(0, 0.43, 0) + n * 0.81, abs_size(t, mw, 0.06, 0.02, n))
	box(g, "bulbs", mc + Vector3(0, -0.43, 0) + n * 0.81, abs_size(t, mw, 0.06, 0.02, n))
	cur_color = Color("#f4f0e2")
	box(g, "poster", mc + n * 0.81, abs_size(t, mw - 0.4, 0.6, 0.02, n))
	cur_color = Color.WHITE
	label("Southland Cinema", "serif", "#1d1a2e", mc + n * 0.84, n, mw * 0.8, 0.42)
	for side in [-1.0, 1.0]:
		var pc = mid + t * side * (Ln * 0.5 - 1.6) + Vector3(0, 1.6, 0) + n * 0.12
		cur_color = Color("#c8202c") if side < 0 else Color("#2451c4")
		box(g, "poster", pc, abs_size(t, 1.0, 1.45, 0.06, n))
		cur_color = Color.WHITE
		box(g, "brass", pc + n * 0.035, abs_size(t, 1.1, 1.55, 0.02, n))
	add_omni(mc + Vector3(0, -0.8, 0) + n * 0.6, 0.8, 6.0, Color(1.0, 0.9, 0.7))

## Jewelry kiosks (decision 1: both there since 1991) under lit rings (decision 7).
func kiosks():
	var centers = []
	for e in L.edges:
		if e.kind == "store" and L.stores[e.store].name.begins_with("GREAT AMERICAN COOKIE"):
			var eb = edge_basics(e)
			var a = eb[0]; var b = eb[1]; var n = eb[2]; var t = eb[3]
			var corner = (a + b) * 0.5 + t * 3.2 + n * 2.7
			gold_kiosk("kiosks", corner, t, n)
			lit_ring("kiosks", corner + t * 1.0 + n * 0.7)
			centers.append(corner)
			break
	# Mr. Silverman island: position is a guess (concourse, west of the cookie shop)
	var ms = Vector3(-52.0, 0, 54.0)
	island_kiosk("kiosks", ms)
	lit_ring("kiosks", ms)
	centers.append(ms)
	return centers

func gold_kiosk(g, c, t, n):
	# two runs of waist-high cases at a right angle: one along the stores, one out into the hall
	var runs = [[c + t * 1.3, t, 2.6], [c + n * 0.9, n, 1.8]]
	for rr in runs:
		var mid = rr[0]
		var dirv = rr[1]
		var Lr = rr[2]
		var other = Vector3(-dirv.z, 0, dirv.x)
		box(g, "black", mid + Vector3(0, 0.38, 0), abs_size(dirv, Lr, 0.76, 0.62, other))
		box(g, "velvet", mid + Vector3(0, 0.77, 0), abs_size(dirv, Lr - 0.08, 0.02, 0.54, other))
		box(g, "brass", mid + Vector3(0, 1.0, 0), abs_size(dirv, Lr, 0.035, 0.64, other))
		box("glass", "glass", mid + Vector3(0, 0.88, 0), abs_size(dirv, Lr, 0.22, 0.6, other), Transform3D.IDENTITY, ["-y"], true)
		for k in 6:
			cur_color = Color("#e8c766")
			box(g, "vcolor", mid + dirv * (-Lr * 0.4 + k * Lr * 0.16) + Vector3(0, 0.8, 0), Vector3(0.08, 0.03, 0.08))
		cur_color = Color.WHITE
	# black track-light gantry
	var p0 = c - n * 0.3 - t * 0.3
	var corners = [p0, p0 + t * 3.2, p0 + n * 2.4, p0 + t * 3.2 + n * 2.4]
	for q in corners:
		box(g, "black", q + Vector3(0, 1.25, 0), Vector3(0.06, 2.5, 0.06))
	for pr in [[corners[0], corners[1]], [corners[2], corners[3]], [corners[0], corners[2]], [corners[1], corners[3]]]:
		var mm = (pr[0] + pr[1]) * 0.5 + Vector3(0, 2.5, 0)
		var dv = (pr[1] - pr[0])
		box(g, "black", mm, abs_size(dv.normalized(), dv.length(), 0.06, 0.06, Vector3(-dv.normalized().z, 0, dv.normalized().x)))
	for k in 4:
		var lp = p0 + t * (0.5 + k * 0.75) + n * 1.2 + Vector3(0, 2.4, 0)
		box(g, "downlight", lp, Vector3(0.1, 0.1, 0.1))
	add_omni(c + t * 1.2 + n * 0.9 + Vector3(0, 2.2, 0), 0.7, 4.0, Color(1.0, 0.93, 0.8))
	obst(["rect", min(corners[0].x, corners[3].x) - 0.3, min(corners[0].z, corners[3].z) - 0.3, max(corners[0].x, corners[3].x) + 0.3, max(corners[0].z, corners[3].z) + 0.3])

func island_kiosk(g, c):
	var sx = 3.4
	var sz = 1.8
	for side in [[Vector3(0, 0, -sz * 0.5), Vector3(1, 0, 0), sx], [Vector3(0, 0, sz * 0.5), Vector3(1, 0, 0), sx], [Vector3(-sx * 0.5, 0, 0), Vector3(0, 0, 1), sz], [Vector3(sx * 0.5, 0, 0), Vector3(0, 0, 1), sz]]:
		var mid = c + side[0]
		var dv = side[1]
		var ov = Vector3(-dv.z, 0, dv.x)
		box(g, "column", mid + Vector3(0, 0.38, 0), abs_size(dv, side[2], 0.76, 0.5, ov))
		box(g, "velvet", mid + Vector3(0, 0.77, 0), abs_size(dv, side[2] - 0.08, 0.02, 0.42, ov))
		box("glass", "glass", mid + Vector3(0, 0.9, 0), abs_size(dv, side[2], 0.26, 0.5, ov), Transform3D.IDENTITY, ["-y"], true)
	for qx in [-1.0, 1.0]:
		for qz in [-1.0, 1.0]:
			var q = c + Vector3(qx * (sx * 0.5 + 0.1), 0, qz * (sz * 0.5 + 0.1))
			box(g, "column", q + Vector3(0, 0.4, 0), Vector3(0.6, 0.8, 0.6))
			box("glass", "glass", q + Vector3(0, 1.3, 0), Vector3(0.58, 1.0, 0.58), Transform3D.IDENTITY, [], true)
			box(g, "lane_ceiling", q + Vector3(0, 1.82, 0), Vector3(0.62, 0.04, 0.62))
			box(g, "velvet", q + Vector3(0, 0.82, 0), Vector3(0.54, 0.02, 0.54))
	cur_color = Color("#20242e")
	box(g, "vcolor", c + Vector3(0, 1.95, 0), Vector3(1.8, 0.35, 0.06))
	cur_color = Color.WHITE
	label("Mr. Silverman", "serif", "#e8dcc0", c + Vector3(0, 1.95, 0.04), Vector3(0, 0, 1), 1.6, 0.2)
	label("Mr. Silverman", "serif", "#e8dcc0", c + Vector3(0, 1.95, -0.04), Vector3(0, 0, -1), 1.6, 0.2)
	obst(["rect", c.x - sx * 0.5 - 0.6, c.z - sz * 0.5 - 0.6, c.x + sx * 0.5 + 0.6, c.z + sz * 0.5 + 0.6])

## A floating white ring lit from inside, hung on cables, with small spots.
func lit_ring(g, c):
	var R = 2.6
	var y = 4.25
	var seg = 32
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var o0 = Vector3(cos(a0), 0, sin(a0))
		var o1 = Vector3(cos(a1), 0, sin(a1))
		var top = Vector3(0, y + 0.14, 0)
		var bot = Vector3(0, y - 0.14, 0)
		var ro = R + 0.12
		var ri = R - 0.12
		quad(g, "rib", [c + o0 * ro + bot, c + o1 * ro + bot, c + o1 * ro + top, c + o0 * ro + top], (o0 + o1).normalized())
		quad(g, "ring_glow", [c + o0 * ri + bot, c + o1 * ri + bot, c + o1 * ri + top, c + o0 * ri + top], -(o0 + o1).normalized())
		quad(g, "rib", [c + o0 * ri + bot, c + o1 * ri + bot, c + o1 * ro + bot, c + o0 * ro + bot], Vector3.DOWN)
		quad(g, "rib", [c + o0 * ri + top, c + o1 * ri + top, c + o1 * ro + top, c + o0 * ro + top], Vector3.UP)
	for k in 3:
		var a = TAU * k / 3.0
		var p = c + Vector3(cos(a), 0, sin(a)) * R + Vector3(0, y + 0.14, 0)
		cyl(g, "metal_dark", p, 0.008, 0.008, 6.5 - p.y, 4, false)
	for k in 6:
		var a = TAU * k / 6.0 + 0.3
		box(g, "black", c + Vector3(cos(a), 0, sin(a)) * R + Vector3(0, y - 0.22, 0), Vector3(0.12, 0.16, 0.12))
	add_omni(c + Vector3(0, y - 0.3, 0), 0.9, 6.0, Color(1.0, 0.95, 0.88))

## Anchor fronts, as the current game draws them from Steven's photos:
## a wide open mouth onto the sales floor under a store-specific fascia.
const ANCHOR_LOOK = {
	"SEARS": {"wall": "buff_tile", "fascia": "buff_tile", "frame": "grey_tile", "cols": "", "text": "SEARS", "font": "sans_italic", "fg": "#1f3f8f", "halo": true, "soffit": "lane_ceiling"},
	"JCPENNEY": {"wall": "cream", "fascia": "wood_diag", "frame": "", "cols": "metal_dark", "text": "JCPenney", "font": "sans", "fg": "#ffffff", "halo": false, "soffit": "lane_ceiling"},
	"DILLARD'S": {"wall": "cream", "fascia": "brown_stone", "frame": "", "cols": "", "text": "Dillard's", "font": "serif", "fg": "#ffffff", "halo": false, "soffit": "cream", "lit": true},
}

func anchor_front(g, e, a, b, n, t, Ln, sd, lk):
	var mid = a + t * Ln * 0.5
	var top = LANE_H
	var mouth_h = OPEN_H + 0.2
	var deep = clamp(float(e.depth), 6.0, 16.0)
	# fascia across the full width, standing proud of the wall line
	box(g, lk.fascia, mid + Vector3(0, (mouth_h + top) * 0.5, 0) + n * 0.15, abs_size(t, Ln, top - mouth_h, 0.3, n))
	# soffit under the fascia
	quad(g, lk.soffit, [a + Vector3(0, mouth_h, 0) + n * 0.3, b + Vector3(0, mouth_h, 0) + n * 0.3, b + Vector3(0, mouth_h, 0) - n * 0.6, a + Vector3(0, mouth_h, 0) - n * 0.6], Vector3.DOWN)
	# end piers
	for ee in [0.0, Ln - 0.6]:
		var c0 = a + t * (ee + 0.3)
		box(g, lk.fascia if lk.cols == "" else lk.cols, c0 + Vector3(0, mouth_h * 0.5, 0) + n * 0.15, abs_size(t, 0.6, mouth_h, 0.3, n))
	if lk.frame != "":
		# a darker tile band framing the mouth (Sears)
		box(g, lk.frame, mid + Vector3(0, mouth_h + 0.2, 0) + n * 0.31, abs_size(t, Ln - 1.2, 0.4, 0.02, n))
		for ee in [0.6, Ln - 0.6]:
			box(g, lk.frame, a + t * ee + Vector3(0, mouth_h * 0.5, 0) + n * 0.31, abs_size(t, 0.4, mouth_h, 0.02, n))
	if lk.cols != "":
		# dark columns across the open front (JCPenney)
		var k = 6.0
		while k < Ln - 3.0:
			box(g, lk.cols, a + t * k + Vector3(0, mouth_h * 0.5, 0) - n * 0.4, abs_size(t, 0.45, mouth_h, 0.45, n))
			k += 6.0
	# letters
	var sc = mid + Vector3(0, (mouth_h + top) * 0.5, 0) + n * 0.31
	if lk.halo:
		box(g, "halo", sc - n * 0.005, abs_size(t, min(Ln * 0.42, 9.0), 1.15, 0.01, n))
	var lab = label(lk.text, lk.font, lk.fg, sc + n * 0.02, n, min(Ln * 0.38, 8.0), 1.2)
	if lk.get("lit", false):
		lab.modulate = Color(1.3, 1.3, 1.3)
	# the sales floor behind the open mouth
	var p0 = a + t * 0.6
	var p1 = b - t * 0.6
	var back = -n * deep
	var cell = atlas_index.get(e.store, 0)
	var cu = float(cell % ATLAS_COLS) / ATLAS_COLS
	var cv = float(cell / ATLAS_COLS) / ATLAS_ROWS
	var du = 1.0 / ATLAS_COLS
	var dv = 1.0 / ATLAS_ROWS
	var reps = max(1, int(round((Ln - 1.2) / 6.0)))
	for k2 in reps:
		var q0 = p0 + t * ((Ln - 1.2) * k2 / reps)
		var q1 = p0 + t * ((Ln - 1.2) * (k2 + 1) / reps)
		quad(g, "int_back", [q0 + back, q1 + back, q1 + back + Vector3(0, mouth_h, 0), q0 + back + Vector3(0, mouth_h, 0)], n,
			[Vector2(cu, cv + dv), Vector2(cu + du, cv + dv), Vector2(cu + du, cv), Vector2(cu, cv)])
	quad(g, "int_back", [p0, p0 + back, p0 + back + Vector3(0, mouth_h, 0), p0 + Vector3(0, mouth_h, 0)], t,
		[Vector2(cu, cv + dv), Vector2(cu + du, cv + dv), Vector2(cu + du, cv), Vector2(cu, cv)])
	quad(g, "int_back", [p1 + back, p1, p1 + Vector3(0, mouth_h, 0), p1 + back + Vector3(0, mouth_h, 0)], -t,
		[Vector2(cu, cv + dv), Vector2(cu + du, cv + dv), Vector2(cu + du, cv), Vector2(cu, cv)])
	cur_color = Color(sd.carpet) if sd.carpet != null else Color("#d6cdbd")
	quad(g, "int_floor", [p0, p1, p1 + back, p0 + back], Vector3.UP)
	cur_color = Color.WHITE
	quad(g, "int_wall", [p0 + Vector3(0, mouth_h, 0), p0 + back + Vector3(0, mouth_h, 0), p1 + back + Vector3(0, mouth_h, 0), p1 + Vector3(0, mouth_h, 0)], Vector3.DOWN)
	var wd = Ln - 1.2
	for ri in max(1, int(deep / 3.0)):
		for ci in max(1, int(wd / 3.0)):
			var pc = p0 + t * (wd * (ci + 0.5) / max(1, int(wd / 3.0))) - n * (deep * (ri + 0.5) / max(1, int(deep / 3.0))) + Vector3(0, mouth_h - 0.01, 0)
			quad(g, "int_panel", [pc - t * 0.5 - n * 0.3, pc + t * 0.5 - n * 0.3, pc + t * 0.5 + n * 0.3, pc - t * 0.5 + n * 0.3], Vector3.DOWN)
	# racks and tables in the store's colours, in rows
	var mc = sd.merch
	var k3 = 0
	for row in [0.3, 0.55, 0.8]:
		var pos = 1.5
		while pos < wd - 1.0:
			cur_color = Color(mc[k3 % mc.size()])
			box(g, "vcolor", p0 + t * pos - n * (deep * row) + Vector3(0, 0.6, 0), abs_size(t, 1.6, 1.2, 0.6, n))
			pos += 3.2
			k3 += 1
	cur_color = Color.WHITE
	for k4 in 3:
		tag(add_omni(p0 + t * (wd * (k4 + 0.5) / 3.0) - n * deep * 0.45 + Vector3(0, mouth_h - 0.4, 0), 0.9, deep + 2.0, Color(1.0, 0.97, 0.9)), "", 0.9, 1.4)

## Glass doors to the outside (exits and the main entrance), with daylight beyond.
func doors_out(g, e, a, b, n, t, Ln):
	var sd = L.stores.get(e.store, {})
	var dh = 3.0
	var mid = a + t * Ln * 0.5
	var dw = min(Ln - 1.0, 9.0)
	var s0 = Ln * 0.5 - dw * 0.5
	var s1 = Ln * 0.5 + dw * 0.5
	var o = PackedVector2Array([Vector2(0, 0), Vector2(0, LANE_H), Vector2(Ln, LANE_H), Vector2(Ln, 0), Vector2(s1, 0), Vector2(s1, dh), Vector2(s0, dh), Vector2(s0, 0)])
	poly(g, "cream", o, a, t, Vector3.UP, n)
	box(g, "bronze", mid + Vector3(0, dh, 0), abs_size(t, dw + 0.2, 0.15, 0.2, n))
	var k = 0
	var cnt = max(2, int(round(dw / 1.6)))
	for i in cnt + 1:
		box(g, "bronze", a + t * (s0 + dw * i / cnt) + Vector3(0, dh * 0.5, 0), abs_size(t, 0.08, dh, 0.18, n))
	quad("glass", "glass", [a + t * s0, a + t * s1, a + t * s1 + Vector3(0, dh, 0), a + t * s0 + Vector3(0, dh, 0)], n, [], true)
	# a vestibule floor and canopy outside so the daylight has something to bounce off
	var out = -n
	var og = "outside"
	cur_color = Color.WHITE
	quad(og, "outside_ground", [a, b, b + out * 12.0, a + out * 12.0], Vector3.UP, [], false, 0.25)
	quad(og, "cream", [a + Vector3(0, dh + 0.3, 0), b + Vector3(0, dh + 0.3, 0), b + out * 4.0 + Vector3(0, dh + 0.3, 0), a + out * 4.0 + Vector3(0, dh + 0.3, 0)], Vector3.DOWN)
	# night: sodium lot lights outside and a warm spot in the vestibule
	for k5 in [-1.0, 0.0, 1.0]:
		tag(add_omni(mid + out * 14.0 + t * k5 * 10.0 + Vector3(0, 9.0, 0), 4.0, 25.0, Color("#FF9F45")), "night")
	tag(add_spot(mid + out * 2.0 + Vector3(0, dh + 0.2, 0), Vector3.DOWN, 1.5, 6.0, 60.0, Color("#FFE6C2")), "night")
	if e.kind == "exit":
		box(g, "exit_sign", mid + Vector3(0, dh + 0.55, 0) + n * 0.05, abs_size(t, 1.2, 0.36, 0.08, n))
		label("EXIT", "sans", "#ffffff", mid + Vector3(0, dh + 0.55, 0) + n * 0.1, n, 1.0, 0.24)
	else:
		label("Main Entrance", "serif", "#5b4030", mid + Vector3(0, dh + 0.75, 0) + n * 0.05, n, dw * 0.6, 0.42)

# ------------------------------------------------------------------ props
func bench(group, at, yaw):
	var xf = Transform3D(Basis(Vector3.UP, yaw), at)
	var Lb = 1.7
	for i in 5:
		box(group, "wood", Vector3(0, 0.44, -0.2 + i * 0.105), Vector3(Lb, 0.035, 0.085), xf)
	for i in 4:
		var c = Vector3(0, 0.62 + i * 0.105, 0.29 + i * 0.012)
		var bx = xf * Transform3D(Basis(Vector3.RIGHT, -0.25 - i * 0.06), c)
		box(group, "wood", Vector3.ZERO, Vector3(Lb, 0.085, 0.03), bx)
	for ee in [-Lb * 0.5 + 0.08, Lb * 0.5 - 0.08]:
		box(group, "metal_dark", Vector3(ee, 0.22, -0.1), Vector3(0.05, 0.44, 0.05), xf)
		box(group, "metal_dark", Vector3(ee, 0.4, 0.3), Vector3(0.05, 0.8, 0.05), xf)
		box(group, "metal_dark", Vector3(ee, 0.62, 0.0), Vector3(0.06, 0.04, 0.5), xf)
		box(group, "metal_dark", Vector3(ee, 0.05, 0.1), Vector3(0.06, 0.04, 0.55), xf)
	obst([at.x, at.z, 0.85])

func planter(at, kind):
	cyl("fixtures", "planter", at, 0.42, 0.46, 0.62, 24, false)
	cyl("fixtures", "soil", at + Vector3(0, 0.56, 0), 0.4, 0.4, 0.001, 18, true)
	if kind == "palm":
		palm(at + Vector3(0, 0.56, 0), 1.6)
	else:
		bush(at + Vector3(0, 0.56, 0), "leafy", 0.75, 5)
	obst([at.x, at.z, 0.6])

func trash(at):
	cyl("fixtures", "planter", at, 0.24, 0.28, 0.82, 20, false)
	cyl("fixtures", "planter", at + Vector3(0, 0.82, 0), 0.29, 0.29, 0.05, 20, false)
	cyl("fixtures", "planter", at + Vector3(0, 0.87, 0), 0.29, 0.12, 0.12, 20, true)
	obst([at.x, at.z, 0.45])

## Benches, planters and trash cans in the groupings seen in the 2018 walkthrough:
## a pair of benches facing each other across a round planter on the hall's
## centre line every ~22 m, a trash can one lane out, and planters by court
## columns. All of it goes in one mesh the player can switch on or off.
func place_fixtures(avoid):
	fx = true
	var count = 0
	for z in L.zones:
		if z.type == "hall" and float(z.vault_half) > 0.0:
			var sp = hall_span(z)
			var lo = sp[0]
			var hi = sp[1]
			if hi - lo < 14.0:
				continue
			var yaw0 = 0.0 if z.axis == "z" else PI * 0.5
			var k = 0
			var s0 = lo + 7.0
			while s0 < hi - 6.0:
				var c = hall_P(z, 0, 0, s0)
				var clear = true
				for a in avoid:
					if Vector2(c.x - a.x, c.z - a.z).length() < 7.5:
						clear = false
				if clear:
					planter(c, "palm" if k % 2 == 0 else "leafy")
					bench("fixtures", hall_P(z, 0, 0, s0 - 1.6), yaw0 + PI)
					bench("fixtures", hall_P(z, 0, 0, s0 + 1.6), yaw0)
					trash(hall_P(z, sp[2] * 0.45 * (1 if k % 2 == 0 else -1), 0, s0 + 4.5))
					count += 1
					k += 1
				s0 += 22.0
		elif z.type == "court" and z.style != "shoe":
			var r = z.rect
			planter(Vector3(r[0] + 2.3, 0, r[1] + 2.3), "palm")
			planter(Vector3(r[2] - 2.3, 0, r[3] - 2.3), "palm")
			trash(Vector3(r[2] - 2.3, 0, r[1] + 2.3))
	fx = false
	print("fixture groups: ", count)

func palm(base, hgt):
	cyl("foliage", "trunk", base, 0.07, 0.05, hgt, 8, false, false, true)
	var top = base + Vector3(0, hgt, 0)
	for i in 14:
		frond(top, TAU * i / 14 + randf() * 0.3, 1.5 + randf() * 0.6, deg_to_rad(35 + randf() * 25))

func frond(top, yaw, Lf, up):
	var s = st("foliage", "palm", true)
	var dir = Vector3(cos(yaw), 0, sin(yaw))
	var side = Vector3(-dir.z, 0, dir.x)
	var segs = 6
	var prev_l = Vector3.ZERO
	var prev_r = Vector3.ZERO
	var prev_c = top
	for i in segs + 1:
		var f = float(i) / segs
		var ang = up - f * 1.6 * up - f * f * 0.9
		var c = top
		if i > 0:
			c = prev_c + (dir * cos(ang) + Vector3.UP * sin(ang)) * (Lf / segs)
		var w = 0.46 * sin(PI * (0.15 + 0.85 * f)) + 0.05
		var lft = c + side * w + Vector3(0, -w * 0.35, 0)
		var rgt = c - side * w + Vector3(0, -w * 0.35, 0)
		if i > 0:
			var nn = (dir * -sin(ang) + Vector3.UP * cos(ang)).normalized()
			var v0 = float(i - 1) / segs
			tri(s, prev_l, prev_r, rgt, Vector2(0, v0), Vector2(1, v0), Vector2(1, f), nn)
			tri(s, prev_l, rgt, lft, Vector2(0, v0), Vector2(1, f), Vector2(0, f), nn)
		prev_l = lft; prev_r = rgt; prev_c = c

func bush(base, mname, size, cards):
	var s = st("foliage", mname, true)
	for i in cards:
		var yaw = PI * i / cards
		var d = Vector3(cos(yaw), 0, sin(yaw)) * size
		var tilt = Vector3(0, size * 0.9, 0)
		var p0 = base - d + Vector3(0, 0.02, 0)
		var p1 = base + d + Vector3(0, 0.02, 0)
		var nn = Vector3(-d.z, 0.3, d.x).normalized()
		tri(s, p0, p1, p1 + tilt, Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), nn)
		tri(s, p0, p1 + tilt, p0 + tilt, Vector2(0, 1), Vector2(1, 0), Vector2(0, 0), nn)
	var c = base + Vector3(0, size * 0.75, 0)
	tri(s, c + Vector3(-size, 0, -size), c + Vector3(size, 0, -size), c + Vector3(size, 0, size), Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector3.UP)
	tri(s, c + Vector3(-size, 0, -size), c + Vector3(size, 0, size), c + Vector3(-size, 0, size), Vector2(0, 0), Vector2(1, 1), Vector2(0, 1), Vector3.UP)

func palm_bed(group, at, sx, sz):
	var h = 0.42
	box(group, "bed_wood", at + Vector3(0, h * 0.5, 0), Vector3(sx, h, sz), Transform3D.IDENTITY, ["-y"])
	box(group, "soil", at + Vector3(0, h + 0.005, 0), Vector3(sx - 0.1, 0.01, sz - 0.1), Transform3D.IDENTITY, ["-y"])
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
	obst(["rect", at.x - sx * 0.5 - 0.3, at.z - sz * 0.5 - 0.3, at.x + sx * 0.5 + 0.3, at.z + sz * 0.5 + 0.3])

func lantern(at, top_y):
	var g = "lanterns"
	cyl(g, "brass", Vector3(at.x, at.y + 0.55, at.z), 0.015, 0.015, top_y - at.y - 0.55, 6, false)
	cyl(g, "lantern_glass", at + Vector3(0, -0.2, 0), 0.2, 0.24, 0.6, 8, false, false)
	for i in 8:
		var a = TAU * i / 8
		box(g, "brass", at + Vector3(cos(a) * 0.245, 0.1, sin(a) * 0.245), Vector3(0.025, 0.66, 0.025))
	cyl(g, "brass", at + Vector3(0, 0.4, 0), 0.27, 0.05, 0.18, 8, true)
	cyl(g, "brass", at + Vector3(0, -0.24, 0), 0.24, 0.26, 0.05, 8, true, true)
	cyl(g, "brass", at + Vector3(0, -0.36, 0), 0.02, 0.09, 0.12, 8, false, true)
	add_omni(at + Vector3(0, -0.05, 0), 1.0, 4.0, Color(1.0, 0.85, 0.63))

# ------------------------------------------------------------------ floors
## Floor quads per zone; each zone gets its own material carrying the pattern
## parameters as metadata, read by the runtime floor shader.
func floor_zone(z):
	var r = z.rect
	var mname = "floorz_" + z.id
	var m = mat(mname)
	var meta = {}
	if z.type == "hall":
		var sp = hall_span(z)
		meta = {"pattern": 1, "axis": 0 if z.axis == "x" else 1, "center": ((r[1] + r[3]) * 0.5) if z.axis == "x" else ((r[0] + r[2]) * 0.5), "half": sp[2], "medallions": 1 if z.id == "H3" else 0}
		if sp[2] < 2.5:
			meta = {"pattern": 0}
	else:
		meta = {"pattern": 2, "cx": (r[0] + r[2]) * 0.5, "cz": (r[1] + r[3]) * 0.5, "hx": (r[2] - r[0]) * 0.5, "hz": (r[3] - r[1]) * 0.5,
			"palette": {"shoe": 1, "sears": 2}.get(z.style, 0)}
	m.set_meta("floor", meta)
	quad(z.id, mname, [Vector3(r[0], 0, r[1]), Vector3(r[2], 0, r[1]), Vector3(r[2], 0, r[3]), Vector3(r[0], 0, r[3])], Vector3.UP)

# ------------------------------------------------------------- environments
## Day: soft high sun, bright sky through skylights and clerestories.
## Night (the default): navy-black sky, the interior lit by its own lights.
func make_env(mode):
	var env = Environment.new()
	var sky = Sky.new()
	var psky = ProceduralSkyMaterial.new()
	if mode == "day":
		psky.sky_top_color = Color("#6FA3D8")
		psky.sky_horizon_color = Color("#CFE0EE")
		psky.ground_horizon_color = Color("#c9c3b5")
		psky.ground_bottom_color = Color("#7b766c")
		psky.sky_energy_multiplier = 1.3
	else:
		psky.sky_top_color = Color("#0B1530")
		psky.sky_horizon_color = Color("#1B2747")
		psky.ground_horizon_color = Color("#1B2747")
		psky.ground_bottom_color = Color("#0A0A0C")
		psky.sky_energy_multiplier = 0.6
		psky.sun_angle_max = 0.0
	sky.sky_material = psky
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY if mode == "day" else Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("#2A2620")
	env.ambient_light_energy = 0.3 if mode == "day" else 0.12
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.05 if mode == "day" else 0.7
	env.tonemap_white = 6.0 if mode == "day" else 4.0
	env.glow_enabled = true
	env.glow_intensity = 0.35
	env.glow_bloom = 0.04 if mode == "day" else 0.0
	env.glow_hdr_threshold = 1.2 if mode == "day" else 1.0
	env.adjustment_enabled = true
	env.adjustment_saturation = 1.08 if mode == "day" else 1.05
	env.adjustment_contrast = 1.04 if mode == "day" else 1.05
	return env

# ------------------------------------------------------------------ build
func build():
	seed(1995)
	L = JSON.parse_string(FileAccess.get_file_as_string("res://layout_mall.json"))
	if USE_FRONT_ART and FileAccess.file_exists("res://fronts.json"):
		var fj = JSON.parse_string(FileAccess.get_file_as_string("res://fronts.json"))
		fronts_px = float(fj.atlas.px_per_tile)
		for key in fj.fronts:
			var f = fj.fronts[key]
			if f.has("uv"):
				fronts[edge_key(f.a, f.b)] = f
	if FileAccess.file_exists("res://facade_records.json"):
		var fr = JSON.parse_string(FileAccess.get_file_as_string("res://facade_records.json"))
		for sid in fr.stores:
			facade_levels[sid] = int(fr.stores[sid].level)
	for z in L.zones:
		zones[z.id] = z
	var ids = L.stores.keys()
	ids.sort()
	var ci = 0
	for sid in ids:
		atlas_index[sid] = ci
		ci += 1
	mall = Node3D.new(); mall.name = "Mall"
	light_root = Node3D.new(); light_root.name = "Lights"
	mall.add_child(light_root); light_root.owner = mall

	for z in L.zones:
		floor_zone(z)
		if z.type == "hall":
			build_hall(z)
		else:
			build_court(z)
	var lm = mat("floorz_left")
	lm.set_meta("floor", {"pattern": 0})
	for r in L.leftovers:
		quad("misc", "floorz_left", [Vector3(r[0], 0, r[1]), Vector3(r[2], 0, r[1]), Vector3(r[2], 0, r[3]), Vector3(r[0], 0, r[3])], Vector3.UP)
		quad("misc", "lane_ceiling", [Vector3(r[0], LANE_H, r[1]), Vector3(r[2], LANE_H, r[1]), Vector3(r[2], LANE_H, r[3]), Vector3(r[0], LANE_H, r[3])], Vector3.DOWN)
	for e in L.edges:
		build_edge(e)
	var avoid = kiosks()
	place_fixtures(avoid)
	# K&B's mall-facing wall: pink with plum stripes instead of a full storefront
	# is a per-store look we add in Phase 2 (decision 6); its storefront is generic for now.

	var sun = DirectionalLight3D.new()
	sun.name = "Sun"
	sun.light_bake_mode = Light3D.BAKE_STATIC
	sun.shadow_enabled = true
	sun.light_energy = 1.1
	sun.light_color = Color(1.0, 0.95, 0.86)
	sun.light_angular_distance = 3.5    # soft shadow edges, no hard bands
	sun.set_meta("only", "day")
	mall.add_child(sun); sun.owner = mall
	# high sun (about 65 degrees) so window patches land short and close to the walls
	sun.transform = Transform3D(Basis.looking_at(Vector3(0.30, -0.906, 0.30), Vector3.UP), Vector3.ZERO)

	DirAccess.make_dir_recursive_absolute("res://gen")
	ResourceSaver.save(make_env("day"), "res://gen/env_day.tres")
	ResourceSaver.save(make_env("night"), "res://gen/env_night.tres")
	var we = WorldEnvironment.new()
	we.name = "Env"; we.environment = load("res://gen/env_night.tres")
	mall.add_child(we); we.owner = mall

	var static_root = Node3D.new(); static_root.name = "Static"
	mall.add_child(static_root); static_root.owner = mall
	DirAccess.make_dir_recursive_absolute("res://gen")
	for gname in acc:
		var am = ArrayMesh.new()
		for mname in acc[gname]:
			var s = acc[gname][mname]
			s.index()
			s.commit(am)
			am.surface_set_material(am.get_surface_count() - 1, glow_mat(gname, mname))
		var texel = TEXEL
		if gname.ends_with("_mach"):
			# arcade machines: mostly lit by their own glow; a coarse texel keeps the
			# lightmap atlas to one layer (a fine one doubled the download)
			texel = TEXEL * 1.5
		elif gname.ends_with("props") or gname == "lanterns":
			texel = TEXEL * 0.6
		elif gname == "outside":
			texel = TEXEL * 4.0
		if am.lightmap_unwrap(Transform3D.IDENTITY, texel) != OK:
			push_error("unwrap failed " + gname)
		ResourceSaver.save(am, "res://gen/" + gname + ".res")
		var mi = MeshInstance3D.new()
		mi.name = gname
		mi.mesh = load("res://gen/" + gname + ".res")
		mi.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		static_root.add_child(mi); mi.owner = mall
	var dyn_root = Node3D.new(); dyn_root.name = "Dynamic"
	mall.add_child(dyn_root); dyn_root.owner = mall
	for gname in dyn_acc:
		var am = ArrayMesh.new()
		for mname in dyn_acc[gname]:
			var s = dyn_acc[gname][mname]
			s.index()
			# the arcade's many small machine parts: compressed vertex attributes halve the download
			s.commit(am, Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES if gname.begins_with("pc") else 0)
			am.surface_set_material(am.get_surface_count() - 1, mat(mname))
		ResourceSaver.save(am, "res://gen/dyn_" + gname + ".res")
		var mi = MeshInstance3D.new()
		mi.name = "dyn_" + gname
		mi.mesh = load("res://gen/dyn_" + gname + ".res")
		mi.gi_mode = GeometryInstance3D.GI_MODE_DYNAMIC
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		dyn_root.add_child(mi); mi.owner = mall

	for z in L.zones:
		var r = z.rect
		var rp = ReflectionProbe.new()
		var hgt = 10.0 if z.type == "court" else 6.6
		rp.position = Vector3((r[0] + r[2]) * 0.5, hgt * 0.5, (r[1] + r[3]) * 0.5)
		rp.size = Vector3(r[2] - r[0] + 0.5, hgt, r[3] - r[1] + 0.5)
		rp.box_projection = true
		rp.interior = true
		rp.update_mode = ReflectionProbe.UPDATE_ONCE
		rp.intensity = 0.9
		mall.add_child(rp); rp.owner = mall

	var lmg = LightmapGI.new()
	lmg.name = "LightmapGI"
	# Godot 4.7: Medium leaves blotchy low-frequency noise on the hall walls and
	# vaults (the light comes from many small emissive discs); Ultra on Steven's
	# Mac takes ~12 min per setup, and the denoiser needs more than its 0.1 default.
	lmg.quality = LightmapGI.BAKE_QUALITY_ULTRA
	lmg.bounces = 3
	lmg.use_denoiser = true
	lmg.denoiser_strength = 0.25
	lmg.environment_mode = LightmapGI.ENVIRONMENT_MODE_SCENE
	lmg.max_texture_size = 4096
	lmg.generate_probes_subdiv = LightmapGI.GENERATE_PROBES_SUBDIV_4
	mall.add_child(lmg); lmg.owner = mall

	for c in light_root.get_children():
		c.owner = mall
	for c in mall.get_children():
		if c is Label3D:
			c.owner = mall

	var sf = FileAccess.open("res://gen/signs.json", FileAccess.WRITE)
	sf.store_string(JSON.stringify({"signs": signs}))
	sf.close()
	var cf = FileAccess.open("res://gen/collide.json", FileAccess.WRITE)
	cf.store_string(JSON.stringify({"static": obstacles, "fixtures": fx_obstacles}))
	cf.close()
	var player = load("res://scripts/player.gd").new()
	player.name = "Player"
	player.set("obstacles", obstacles)
	player.set("map_origin", Vector2(L.origin[0], L.origin[1]))
	player.set("map_scale", L.scale)
	mall.add_child(player); player.owner = mall
	var rt = Node.new()
	rt.set_script(load("res://scripts/mall_runtime.gd"))
	rt.name = "Runtime"
	mall.add_child(rt); rt.owner = mall
	# owner-editable sign text (gen/signs.json); after the player so its taps come first
	var sg = Node.new()
	sg.set_script(load("res://scripts/signs.gd"))
	sg.name = "Signs"
	mall.add_child(sg); sg.owner = mall

	var ps = PackedScene.new()
	ps.pack(mall)
	ResourceSaver.save(ps, "res://main.tscn")
	var lights = light_root.get_child_count()
	print("BUILD OK static groups=", acc.size(), " dynamic=", dyn_acc.size(), " lights=", lights, " labels=", mall.get_children().filter(func(c): return c is Label3D).size())

func _initialize():
	build()
	quit()
