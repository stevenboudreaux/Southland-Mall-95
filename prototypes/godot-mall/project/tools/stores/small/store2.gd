## The Wave 6 shops: Radio Shack (s21b) on the west side of the east hall, B. Dalton
## Bookseller (s48) on the north side, and the two corner shops Karmelkorn (s57) and Zales
## (s7), built to design/storefronts/radio-shack.md, b-dalton.md, karmelkorn.md and zales.md.
##
## The fronts follow the Southland facade records (made from Steven's photos) and the 1993
## Hammond Square commercial; the insides are period types on the media kit. Layouts are
## guessed. The corner shops are built whole from their longer frontage; the other frontage
## edge returns without drawing (its front is part of the same build).
##
## Frame: P(a, t, n, u, y, d) = a + t u - n d + y up, u along the frontage from the edge's
## start, d into the store.

const K = preload("res://tools/stores/media/kit.gd")
const AK = preload("res://tools/stores/apparel/kit.gd")
const M2 = preload("res://tools/stores/apparel/more.gd")
const S1 = preload("res://tools/stores/small/store.gd")
const UP = Vector3.UP
const SIDE = 0.12

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 600 + int(Ln)
	var W = 8.0
	var D = 16.0
	match sd.name:
		"RADIO SHACK":
			D = 16.0
			radio_shack(b, a, t, n, W, D, rng)
		"B. DALTON BOOKSELLER":
			D = 20.0
			dalton(b, a, t, n, W, D, rng)
		"KARMELKORN":
			if Ln < 12.0:
				return   # the corner's east edge: built with the north one
			W = 16.0
			D = 10.0
			karmelkorn(b, a, t, n, W, D, rng)
		"ZALES":
			if abs(n.z) < 0.5:
				return   # the corner's east edge: built with the north one
			W = 8.0
			D = 10.0
			zales(b, a, t, n, W, D, rng)
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, W * 0.5, 1.6, D * 0.5)
	rp.size = (t * W + n * D).abs() + Vector3(0.1, 3.3, 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ Radio Shack
## A deep brown fascia box with the lit red wordmark standing off it on dark returns, a bright
## soffit, and an aluminium-and-glass front on a green marble plinth (record; Hammond 23.9 s);
## inside, pegboard walls of parts, shelves of boxed electronics, the counter at the back.
static func radio_shack(b, a, t, n, W, D, rng):
	var G = "s6r_fix"
	var F = "s6rf_props"
	var head = 2.7
	S1.upper(b, F, a, t, n, W, head, "s6_brown", 0.3)
	AK.letters(b, F, "res://tools/stores/small/rs_letters.json", P(a, t, n, W * 0.5, head + 0.55, -0.3), n, "sm_red_letter", "md_black", 0.04, 0.07)
	b.quad(F, "md_glowstrip", [P(a, t, n, 0.2, head, -0.3), P(a, t, n, W - 0.2, head, -0.3), P(a, t, n, W - 0.2, head, 0.0), P(a, t, n, 0.2, head, 0.0)], Vector3.DOWN)
	# the glass front on a green marble plinth, an aluminium-framed door left of centre
	b.box(F, "s6_marble", P(a, t, n, 4.9, 0.25, -0.05), b.abs_size(t, 5.8, 0.5, 0.2, n), Transform3D.IDENTITY, ["-y"])
	b.quad("glass", "glass", [P(a, t, n, 2.0, 0.5, -0.03), P(a, t, n, W - 0.2, 0.5, -0.03), P(a, t, n, W - 0.2, head, -0.03), P(a, t, n, 2.0, head, -0.03)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	for u in [0.0, 0.2, 2.0, 4.6, W - 0.2]:
		b.box(F, "wl_alum", P(a, t, n, u + 0.03, head * 0.5, -0.03), b.abs_size(t, 0.06, head, 0.08, n))
	b.box(F, "s6_brown", P(a, t, n, 0.1, head * 0.5, -0.1), b.abs_size(t, 0.2, head, 0.2, n), Transform3D.IDENTITY, ["-y"])
	K.ob(b, P(a, t, n, 2.0, 0, -0.15), P(a, t, n, W, 0, 0.1), 0.05)
	# the window dressed with electronics on stepped risers
	for k in 2:
		K.lbox(b, G, "md_black", P(a, t, n, 2.1, 0, 0.15 + k * 0.35), t, -n, 0.0, 0.0, 0.0, W - 2.3, 0.5 + k * 0.35, 0.35)
		K.stock_row(b, G, P(a, t, n, W - 0.2, 0, 0.15 + k * 0.35), -t, n, 0.02, W - 2.3, 0.5 + k * 0.35, 0.3, -0.05, "boxes", rng)
	K.ob(b, P(a, t, n, 2.0, 0, 0.1), P(a, t, n, W, 0, 0.9), 0.05)
	M2.shell2(b, "s6r_shell", a, t, n, W, D, 3.0, 0.0, "a2_carpet_grey", 1.0, "md_wall", "kb_ceiling", [2.0, 5.4], 6.8)
	S1.side_bays(b, G, a, t, n, W, 1.2, D - 2.5, ["acc"], ["boxes", "acc"], rng, "kb_pegboard")
	K.gondola(b, G, G, P(a, t, n, 5.2, 0, 6.0), -t, n, 1.22, 2, [0.45, 0.85, 1.25], ["acc", "boxes"], rng, 0.3)
	K.counter(b, G, "s6r_small", P(a, t, n, W - 1.0, 0, D - 2.2), -t, n, W - 2.4, "md_bb_counter", rng)

# ------------------------------------------------------------------ B. Dalton
## A deep oxblood fascia box with the flowing white script, recessed downlights under it, cream
## piers banded in brown; inside, shelf on shelf of spines with a face-out row along the top
## (record).
static func dalton(b, a, t, n, W, D, rng):
	var G = "s6b_fix"
	var F = "s6bf_props"
	var head = 2.7
	S1.upper(b, F, a, t, n, W, head, "s6_oxblood", 0.3)
	AK.letters(b, F, "res://tools/stores/small/bd_letters.json", P(a, t, n, W * 0.5 - 0.3, head + 0.42, -0.3), n, "ap_letterwhite", "ap_letterwhite", 0.0, 0.05)
	AK.letters(b, F, "res://tools/stores/small/bd_sub_letters.json", P(a, t, n, W * 0.5 + 1.1, head + 0.18, -0.3), n, "ap_letterwhite", "ap_letterwhite", 0.0, 0.03)
	for u in [1.5, 4.0, 6.5]:
		b.cyl(F, "md_downlight", P(a, t, n, u, head - 0.004, -0.15), 0.07, 0.07, 0.004, 12, false, true)
	for s in [[0.0, 0.4], [W - 0.4, W]]:
		b.box(F, "s6_cream", P(a, t, n, (s[0] + s[1]) * 0.5, head * 0.5, -0.1), b.abs_size(t, s[1] - s[0], head, 0.2, n), Transform3D.IDENTITY, ["-y"])
		for y in [0.9, 1.9]:
			b.box(F, "s6_brown", P(a, t, n, (s[0] + s[1]) * 0.5, y, -0.205), b.abs_size(t, s[1] - s[0], 0.08, 0.01, n))
		K.ob(b, P(a, t, n, s[0], 0, -0.2), P(a, t, n, s[1], 0, 0.0), 0.05)
	M2.shell2(b, "s6b_shell", a, t, n, W, D, 3.0, 0.0, "s6_red_carpet", 1.0, "s6_cream", "kb_ceiling", [2.0, 5.4], 7.0)
	M2.soffit(b, F, a, t, n, W, head, "s6_cream")
	# shelf on shelf of spines along both walls and the back, wood bays
	S1.side_bays(b, G, a, t, n, W, 1.0, D - 0.6, ["books"], ["books"], rng, "s6_wood_back", [0.35, 0.68, 1.01, 1.34, 1.67, 2.0], 0.3)
	# gondolas of books down the middle, a table of new titles by the door, the counter
	for d in [5.0, 9.0, 13.0]:
		K.gondola(b, G, G, P(a, t, n, 5.6, 0, d), -t, n, 1.22, 3, [0.4, 0.8, 1.2], ["books"], rng, 0.28)
	var tc = P(a, t, n, W * 0.5, 0, 2.2)
	b.box(G, "s6_wood_back", tc + UP * 0.38, b.abs_size(t, 1.8, 0.76, 0.9, n), Transform3D.IDENTITY, ["-y"])
	K.stock_row(b, G, tc - t * 0.9 - n * 0.45, t, -n, 0.05, 1.75, 0.76, 0.3, 0.0, "books", rng)
	K.ob(b, tc - Vector3(0.9, 0, 0.9), tc + Vector3(0.9, 0, 0.9), 0.1)
	K.counter(b, G, "s6b_small", P(a, t, n, SIDE + 0.5, 0, 2.5), -n, t, 2.4, "md_bb_counter", rng)

# ------------------------------------------------------------------ Karmelkorn
## A golden-yellow bulkhead wrapping the corner with the red logotype (a big K, slab-serif
## capitals, red with a cream edge, leaning a little), a lit soffit, an open front (record);
## inside, a counter of caramel corn under glass, kettles, tins, a yellow room.
static func karmelkorn(b, a, t, n, W, D, rng):
	var G = "s6k_fix"
	var F = "s6kf_props"
	var head = 2.7
	S1.upper(b, F, a, t, n, W, head, "s6_yellow", 0.25)
	AK.letters(b, F, "res://tools/stores/small/kk_letters.json", P(a, t, n, W * 0.5, head + 0.5, -0.25), n, "s6_kk_red", "s6_kk_edge", 0.02, 0.07)
	# the bulkhead wraps the corner: the east front (u = W, along d)
	var e0 = P(a, t, n, W, 0, 0)
	b.box(F, "s6_yellow", e0 - n * (D * 0.5) + UP * ((head + b.LANE_H) * 0.5) + t * 0.125, b.abs_size(-n, D, b.LANE_H - head, 0.25, t))
	AK.letters(b, F, "res://tools/stores/small/kk_letters.json", e0 - n * (D * 0.5) + UP * (head + 0.5) + t * 0.25, t, "s6_kk_red", "s6_kk_edge", 0.02, 0.07)
	# lit soffits on both fronts
	b.quad(F, "md_glowstrip", [P(a, t, n, 0.2, head, 0.0), P(a, t, n, W, head, 0.0), P(a, t, n, W, head, 0.6), P(a, t, n, 0.2, head, 0.6)], Vector3.DOWN)
	b.quad(F, "md_glowstrip", [P(a, t, n, W - 0.6, head, 0.0), P(a, t, n, W, head, 0.0), P(a, t, n, W, head, D - 0.2), P(a, t, n, W - 0.6, head, D - 0.2)], Vector3.DOWN)
	b.box(F, "s6_yellow", P(a, t, n, 0.1, head * 0.5, 0.0), b.abs_size(t, 0.2, head, 0.3, n), Transform3D.IDENTITY, ["-y"])
	b.box(F, "s6_yellow", P(a, t, n, W, head * 0.5, D - 0.1) + t * 0.0, b.abs_size(t, 0.3, head, 0.2, n), Transform3D.IDENTITY, ["-y"])
	# the room: yellow walls, a red tile floor, ceiling over the back half only (the front is the soffit's)
	M2.shell2(b, "s6k_shell", a, t, n, W, D, 3.0, 0.0, "s6_red_tile", 0.61, "s6_yellow_wall", "kb_ceiling", [3.0, 8.0, 13.0], 2.0, 1.3, true)
	# the long L counter: along the hall front, then down the east front; caramel corn under glass
	for seg in [[P(a, t, n, W - 1.6, 0, 1.6), -t, n, W - 3.4], [P(a, t, n, W - 1.6, 0, 1.6), -n, t, D - 4.0]]:
		var o = seg[0]
		var r = seg[1]
		var f = seg[2]
		K.lbox(b, G, "s6_kk_counter", o, r, f, 0.0, 0.0, -0.7, seg[3], 0.9, 0.7, ["-y"])
		b.quad(G, "s6_popcorn", [K.L(o, r, f, 0.05, 0.92, -0.65), K.L(o, r, f, seg[3] - 0.05, 0.92, -0.65), K.L(o, r, f, seg[3] - 0.05, 0.92, -0.05), K.L(o, r, f, 0.05, 0.92, -0.05)], UP,
			[Vector2(0, 0), Vector2(seg[3] / 0.5, 0), Vector2(seg[3] / 0.5, 1.2), Vector2(0, 1.2)])
		b.quad("glass", "glass", [K.L(o, r, f, 0.0, 0.92, -0.02), K.L(o, r, f, seg[3], 0.92, -0.02), K.L(o, r, f, seg[3], 1.25, -0.02), K.L(o, r, f, 0.0, 1.25, -0.02)], f,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
		K.lbox(b, G, "wl_steel", o, r, f, 0.0, 1.25, -0.72, seg[3], 0.03, 0.74)
		K.ob_local(b, o, r, f, 0.0, -0.7, seg[3], 0.0)
	K.register(b, "s6k_small", P(a, t, n, W - 2.6, 1.28, 1.9), -t, n)
	# kettles on the back wall: glass boxes full of corn on steel stands
	for u in [3.0, 6.0, 9.0]:
		var kc = P(a, t, n, u, 0, D - 0.8)
		b.box(G, "wl_steel", kc + UP * 0.45, Vector3(0.9, 0.9, 0.7))
		b.box(G, "s6_popcorn", kc + UP * 1.15, Vector3(0.8, 0.5, 0.6))
		b.box("glass", "glass", kc + UP * 1.25, Vector3(0.9, 0.7, 0.7), Transform3D.IDENTITY, ["-y"], true)
		b.cur_color = Color("#c8141c")
		b.box(G, "vcolor", kc + UP * 1.65, Vector3(0.92, 0.1, 0.72))
		b.cur_color = Color.WHITE
	K.ob(b, P(a, t, n, 2.4, 0, D - 1.3), P(a, t, n, 9.6, 0, D - SIDE), 0.05)
	# tins on shelves along the west wall
	K.bay(b, G, G, P(a, t, n, SIDE, 0, D - 1.0), n, t, 1.22, [0.6, 1.0, 1.4], ["candy"], rng, 0.32)
	K.bay(b, G, G, P(a, t, n, SIDE, 0, D - 2.22), n, t, 1.22, [0.6, 1.0, 1.4], ["candy"], rng, 0.32)

# ------------------------------------------------------------------ Zales
## Stone-tile piers and header, a wood fascia carrying a mauve sign box with brushed-silver
## letters, an open front onto lit glass jewellery cases on a wood base, a cream room with a
## square column (record; Hammond 18.4 s: ZALES JEWELERS in white italic on dark).
static func zales(b, a, t, n, W, D, rng):
	var G = "s6z_fix"
	var F = "s6zf_props"
	var head = 2.7
	S1.upper(b, F, a, t, n, W, head, "sm_stone", 0.2)
	K.lbox(b, F, "s6_wood", P(a, t, n, 0, 0, 0), t, n, 0.6, head + 0.15, 0.2, W - 1.2, 0.9, 0.06)
	K.lbox(b, F, "s6_mauve", P(a, t, n, 0, 0, 0), t, n, 1.6, head + 0.25, 0.26, W - 3.2, 0.7, 0.06)
	AK.letters(b, F, "res://tools/stores/small/zl_letters.json", P(a, t, n, W * 0.5, head + 0.5, -0.32), n, "s6_silver", "s6_silver", 0.0, 0.03)
	AK.letters(b, F, "res://tools/stores/small/zl_sub_letters.json", P(a, t, n, W * 0.5, head + 0.32, -0.32), n, "s6_silver", "s6_silver", 0.0, 0.02)
	# the east front: stone header and the same sign, smaller
	var e0 = P(a, t, n, W, 0, 0)
	b.box(F, "sm_stone", e0 - n * (D * 0.5) + UP * ((head + b.LANE_H) * 0.5) + t * 0.1, b.abs_size(-n, D, b.LANE_H - head, 0.2, t))
	K.lbox(b, F, "s6_mauve", e0, -n, t, D * 0.5 - 1.6, head + 0.25, 0.2, 3.2, 0.7, 0.06)
	AK.letters(b, F, "res://tools/stores/small/zl_letters.json", e0 - n * (D * 0.5) + UP * (head + 0.5) + t * 0.26, t, "s6_silver", "s6_silver", 0.0, 0.03)
	for s in [[0.0, 0.4]]:
		b.box(F, "sm_stone", P(a, t, n, 0.2, head * 0.5, 0.0), b.abs_size(t, 0.4, head, 0.4, n), Transform3D.IDENTITY, ["-y"])
	b.box(F, "sm_stone", P(a, t, n, W - 0.2, head * 0.5, 0.2), b.abs_size(t, 0.4, head, 0.4, n), Transform3D.IDENTITY, ["-y"])
	b.box(F, "sm_stone", P(a, t, n, W - 0.2, head * 0.5, D - 0.2), b.abs_size(t, 0.4, head, 0.4, n), Transform3D.IDENTITY, ["-y"])
	K.ob(b, P(a, t, n, W - 0.4, 0, 0.0), P(a, t, n, W, 0, 0.4), 0.05)
	M2.shell2(b, "s6z_shell", a, t, n, W, D, 3.0, 0.0, "s6_navy_carpet", 1.0, "ap_cream", "kb_ceiling", [2.0, 5.4], 1.0, 1.3, true)
	M2.soffit(b, F, a, t, n, W, head, "ap_cream")
	# lit glass cases on wood bases: along the west wall, across the back, and an island
	for cs in [[P(a, t, n, SIDE, 0, D - 0.6), n, t, D - 2.0], [P(a, t, n, W - 1.0, 0, D - SIDE), -t, n, W - 2.4], [P(a, t, n, 5.2, 0, 3.0), -n, t, 2.4]]:
		jewel_case(b, G, cs[0], cs[1], cs[2], cs[3])
	jewel_case(b, G, P(a, t, n, 5.2 - 0.6, 0, 5.4), n, -t, 2.4)
	# the square column in the cream room
	var cc = P(a, t, n, 3.2, 0, 6.5)
	b.box(G, "ap_cream", cc + UP * 1.5, Vector3(0.5, 3.0, 0.5), Transform3D.IDENTITY, ["-y", "+y"])
	K.ob(b, cc - Vector3(0.25, 0, 0.25), cc + Vector3(0.25, 0, 0.25), 0.1)

## A glass jewellery case on a wood base, its trays lit: `o` the start, `r` along, `f` toward shoppers.
static func jewel_case(b, G, o, r, f, w):
	K.lbox(b, G, "s6_wood", o, r, f, 0.0, 0.0, 0.0, w, 0.75, 0.55)
	b.quad(G, "s6_jewels", [K.L(o, r, f, 0.03, 0.76, 0.03), K.L(o, r, f, w - 0.03, 0.76, 0.03), K.L(o, r, f, w - 0.03, 0.76, 0.52), K.L(o, r, f, 0.03, 0.76, 0.52)], UP,
		[Vector2(0, 1), Vector2(w, 1), Vector2(w, 0), Vector2(0, 0)])
	for q in [[0.0, w, 0.55, 0.55, f], [0.0, w, 0.0, 0.0, -f]]:
		b.quad("glass", "glass", [K.L(o, r, f, q[0], 0.75, q[2]), K.L(o, r, f, q[1], 0.75, q[2]), K.L(o, r, f, q[1], 1.05, q[3]), K.L(o, r, f, q[0], 1.05, q[3])], q[4],
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	b.quad("glass", "glass", [K.L(o, r, f, 0.0, 1.05, 0.0), K.L(o, r, f, w, 1.05, 0.0), K.L(o, r, f, w, 1.05, 0.55), K.L(o, r, f, 0.0, 1.05, 0.55)], UP,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	K.lbox(b, G, "wl_steel", o, r, f, 0.0, 1.05, 0.0, w, 0.015, 0.55)
	K.ob_local(b, o, r, f, 0.0, 0.0, w, 0.55)

# ------------------------------------------------------------------ materials
## "s6_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"brown":
			m.albedo_color = Color("#4a2e1e"); m.roughness = 0.45; m.metallic_specular = 0.4
		"oxblood":
			m.albedo_color = Color("#5a1620"); m.roughness = 0.4; m.metallic_specular = 0.45
		"cream":
			m.albedo_color = Color("#e8dcc4"); m.roughness = 0.7
		"marble":
			m.albedo_texture = b.tex("sm/marble_green.png"); m.roughness = 0.15; m.metallic_specular = 0.7
		"wood_back":
			m.albedo_texture = b.tex("wood_dark.png"); m.roughness = 0.5
			m.albedo_color = Color(1.4, 1.15, 0.95)
		"wood":
			m.albedo_texture = b.tex("wood_dark.png"); m.roughness = 0.35; m.metallic_specular = 0.5
		"red_carpet":
			m.albedo_texture = b.tex("a2/carpet_mauve.png"); m.roughness = 0.95
			m.albedo_color = Color(1.1, 0.6, 0.6)
		"navy_carpet":
			m.albedo_texture = b.tex("a2/carpet_teal.png"); m.roughness = 0.95
			m.albedo_color = Color(0.6, 0.6, 1.2)
		"yellow":
			m.albedo_color = Color("#f2b81e"); m.roughness = 0.4; m.metallic_specular = 0.45
		"yellow_wall":
			m.albedo_color = Color("#f6d56a"); m.roughness = 0.8
		"red_tile":
			m.albedo_texture = b.tex("wl/floor.png"); m.roughness = 0.3; m.metallic_specular = 0.5
			m.albedo_color = Color(0.9, 0.42, 0.36)
		"kk_red":
			m.albedo_color = Color("#d22a24"); m.roughness = 0.35
			K.emit(m, Color("#e83028"), 0.6)
		"kk_edge":
			m.albedo_color = Color("#f4e6c4"); m.roughness = 0.4
		"kk_counter":
			m.albedo_color = Color("#c8141c"); m.roughness = 0.35; m.metallic_specular = 0.5
		"popcorn":
			m.albedo_texture = b.tex("sm/popcorn.png"); m.roughness = 0.6
			K.emit_tex(m, 0.3)
		"mauve":
			m.albedo_color = Color("#8a5a78"); m.roughness = 0.4; m.metallic_specular = 0.5
		"silver":
			m.albedo_color = Color("#d8dadf"); m.metallic = 0.7; m.roughness = 0.3
			K.emit(m, Color("#c0c4cc"), 0.5)
		"jewels":
			m.albedo_texture = b.tex("sm/jewels.png"); m.roughness = 0.2; m.metallic_specular = 0.8
			K.emit_tex(m, 0.6)
		_:
			return false
	return true
