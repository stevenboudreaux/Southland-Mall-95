## The sports stores' stock: Champs Sports and Sports Avenue (tools/stores/small/wave7.gd), shut to
## walking for now (Steven, Oct 7: "make it look like sports stuff and like jerseys rather than
## nondescript clothing"; not walkable yet: tools/narrow_stores.py). Seen through the glass:
## jerseys faced out on the left wall, a wall of trainers on the right, caps across the back,
## rounders of jerseys, bins of balls and pennants strung overhead. Every team is invented
## (tools/stores/small/paint_sports.py: colours, stripes and numbers, no names or logos).
##
## Frame: P(a, t, n, u, y, d) = a + t u - n d + y up, u along the frontage, d into the store.
## Materials are "sp_<key>" (build_mall.gd's mat() calls fill_mat).

const UP = Vector3.UP
const SIDE = 0.12
const K = preload("res://tools/stores/media/kit.gd")

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

## The whole inside, behind a front built by the caller; `ceil` the ceiling height.
static func inside(b, G, a, t, n, W, D, ceil, rng, opts = {}):
	var d0 = float(opts.get("d0", 1.4))
	var d1 = D - 1.6
	jersey_wall(b, G, a, t, n, SIDE, t, d0, d1, rng)
	shoe_wall(b, G, a, t, n, W - SIDE, -t, d0, d1, rng)
	cap_wall(b, G, a, t, n, W, D - SIDE, rng)
	# the floor: rounders of jerseys and bins of balls down the middle
	var cols = [W * 0.5] if W < 9.0 else [W * 0.36, W * 0.64]
	var k = 0
	for cu in cols:
		var d = float(opts.get("first", 3.2))
		while d < D - 3.0:
			var c = P(a, t, n, cu, 0, d)
			if k % 3 == 2:
				ball_bin(b, G, c, rng)
			else:
				rounder(b, G, c, 0.6, k % 4)
			d += 2.8
			k += 1
	# pennants on strings across the store
	var d2 = 2.5
	while d2 < D - 1.5:
		pennants(b, G, P(a, t, n, SIDE + 0.2, ceil - 0.25, d2), t, W - 2 * SIDE - 0.4, rng)
		d2 += 4.0
	# the cash wrap at the back on the right, by the stockroom door
	b.cur_color = Color("#2a2e36")
	b.box(G, "vcolor", P(a, t, n, W - 1.4, 0.5, D - 2.6), b.abs_size(t, 1.8, 1.0, 0.6, n), Transform3D.IDENTITY, ["-y"])
	b.cur_color = Color.WHITE
	b.box(G, "sp_white", P(a, t, n, W - 1.4, 1.02, D - 2.6), b.abs_size(t, 1.9, 0.04, 0.68, n))

## Jerseys faced out on black slatwall in two tiers along a side wall (d0..d1), on chrome arms.
static func jersey_wall(b, G, a, t, n, wall_u, face, d0, d1, rng):
	var o = P(a, t, n, wall_u, 0, d0)
	var r = -n
	var ln = d1 - d0
	K.fq(b, G, "gb_slat_black", o, r, face, 0.0, ln, 0.0, 3.0, 0.015, d0 / 0.305, 0.0, d1 / 0.305, 3.0 / 0.305)
	var x = 0.1
	while x + 0.55 < ln:
		for tier in [[1.55, 2.55], [0.45, 1.45]]:
			var cell = rng.randi_range(0, 15)
			var cu = (cell % 8) / 8.0
			var cv = (cell / 8) * 0.5
			# a jersey is a little narrower than its cell; it hangs 30 cm off the wall
			K.fq(b, G, "sp_jersey", o, r, face, x, x + 0.5, tier[0], tier[1], 0.3, cu, cv, cu + 0.125, cv + 0.5, true)
			K.lbox(b, "sp_small", "sp_chrome", o, r, face, x + 0.24, tier[1] - 0.03, 0.0, 0.02, 0.02, 0.32, [], true)
		x += 0.62

## A wall of trainers: white shelves, six rows, shoes in pairs angled out.
static func shoe_wall(b, G, a, t, n, wall_u, face, d0, d1, rng):
	var o = P(a, t, n, wall_u, 0, d0)
	var r = -n
	var ln = d1 - d0
	K.fq(b, G, "sp_white", o, r, face, 0.0, ln, 0.0, 3.0, 0.01)
	var cols = ["#f4f4f2", "#1c1c20", "#c8202c", "#1f3f8f", "#e8e2d2", "#2a8a4a", "#7a7a80"]
	for row in 6:
		var y = 0.4 + row * 0.42
		K.lbox(b, G, "sp_white", o, r, face, 0.0, y, 0.0, ln, 0.025, 0.3, [])
		var x = 0.12
		while x + 0.3 < ln:
			var c1 = Color(cols[rng.randi_range(0, cols.size() - 1)])
			var c2 = Color(cols[rng.randi_range(0, cols.size() - 1)])
			# a trainer: sole, upper, a swoosh-free side panel in a second colour
			b.cur_color = Color("#f2f0ea")
			K.lbox(b, "sp_small", "vcolor", o, r, face, x, y + 0.025, 0.05, 0.27, 0.035, 0.11, ["-y"], true)
			b.cur_color = c1
			K.lbox(b, "sp_small", "vcolor", o, r, face, x + 0.02, y + 0.06, 0.06, 0.2, 0.07, 0.09, ["-y"], true)
			b.cur_color = c2
			K.lbox(b, "sp_small", "vcolor", o, r, face, x + 0.06, y + 0.07, 0.15, 0.1, 0.04, 0.005, ["-y"], true)
			x += 0.36
	b.cur_color = Color.WHITE

## Caps on the back wall: rows of crowns with bills, in team colours, over a long shelf.
static func cap_wall(b, G, a, t, n, W, d_back, rng):
	var o = P(a, t, n, SIDE, 0, d_back)
	var r = t
	var f = n          # out from the back wall, toward the front
	var cols = ["#1f3f8f", "#b3141a", "#145a32", "#111114", "#4b2a7a", "#0d7c8c", "#d85a12", "#5a0f1e", "#f2f0ea"]
	var w = W - 2 * SIDE
	K.fq(b, G, "gb_slat_black", o, r, f, 0.0, w, 0.0, 3.0, 0.015, 0.0, 0.0, w / 0.305, 3.0 / 0.305)
	for row in 4:
		var y = 1.0 + row * 0.42
		var x = 0.3
		while x + 0.3 < w - 1.2:
			b.cur_color = Color(cols[rng.randi_range(0, cols.size() - 1)])
			var c = o + r * x + UP * y + f * 0.12
			b.cyl("sp_small", "vcolor", c, 0.1, 0.05, 0.1, 10, true, false, true)
			K.lbox(b, "sp_small", "vcolor", o, r, f, x - 0.08, y, 0.2, 0.16, 0.012, 0.1, [], true)
			x += 0.32
	b.cur_color = Color.WHITE

## A rounder of jerseys: a chrome ring at 1.35 m with jerseys hung all round (sp_racks bands).
static func rounder(b, G, c, rad, row):
	b.cyl("sp_small", "sp_chrome", c, 0.3, 0.3, 0.03, 16, true, false, true)
	b.cyl("sp_small", "sp_chrome", c, 0.025, 0.025, 1.36, 8, false, false, true)
	b.cyl("sp_small", "sp_chrome", c + UP * 1.33, rad, rad, 0.03, 24, false, false, true)
	var s = b.st(G, "sp_racks")
	var seg = 24
	var va = row / 4.0
	var vb = (row + 1) / 4.0
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var e0 = Vector3(cos(a0), 0, sin(a0))
		var e1 = Vector3(cos(a1), 0, sin(a1))
		var p0 = c + e0 * (rad + 0.06) + UP * 0.55
		var p1 = c + e1 * (rad + 0.06) + UP * 0.55
		var p2 = c + e1 * (rad + 0.04) + UP * 1.33
		var p3 = c + e0 * (rad + 0.04) + UP * 1.33
		var u0 = float(i) / seg * 2.0
		var u1 = float(i + 1) / seg * 2.0
		var nn = ((e0 + e1) * 0.5).normalized()
		b.tri(s, p0, p1, p2, Vector2(u0, vb), Vector2(u1, vb), Vector2(u1, va), nn)
		b.tri(s, p0, p2, p3, Vector2(u0, vb), Vector2(u1, va), Vector2(u0, va), nn)
	b.cyl(G, "sp_dark", c + UP * 1.32, rad + 0.05, max(rad - 0.15, 0.05), 0.03, 24, false, false)

## A wire bin of balls: basketballs, footballs, soccer balls and volleyballs.
static func ball_bin(b, G, c, rng):
	b.box("sp_small", "sp_chrome", c + UP * 0.35, Vector3(0.9, 0.7, 0.9), Transform3D.IDENTITY, ["+y"], true)
	var cols = ["#d8641c", "#d8641c", "#7a3e1c", "#f4f4f2", "#f2e6c8"]
	for i in 9:
		b.cur_color = Color(cols[rng.randi_range(0, cols.size() - 1)])
		var p = c + Vector3(-0.28 + (i % 3) * 0.28, 0.68 + rng.randf() * 0.06, -0.28 + (i / 3) * 0.28)
		b.cyl("sp_small", "vcolor", p - UP * 0.11, 0.06, 0.11, 0.11, 10, false, false, true)
		b.cyl("sp_small", "vcolor", p, 0.11, 0.06, 0.11, 10, true, false, true)
	b.cur_color = Color.WHITE

## A string of felt pennants across the store at height c.y, from c along r for w metres.
static func pennants(b, G, c, r, w, rng):
	b.box("sp_small", "sp_dark", c + r * (w * 0.5), b.abs_size(r, w, 0.008, 0.008, r.cross(UP)), Transform3D.IDENTITY, [], true)
	var f = r.cross(UP).normalized()
	var x = 0.25
	var s = b.st("sp_small", "sp_pennant", true)
	while x + 0.35 < w:
		var k = rng.randi_range(0, 7)
		var u0 = (k % 4) * 0.25
		var v0 = (k / 4) * 0.5
		var p0 = c + r * x
		var p1 = c + r * (x + 0.32)
		var p2 = c + r * (x + 0.16) - UP * 0.42
		# both faces; the texture's triangle runs left to right, hung point down here
		b.tri(s, p0, p1, p2, Vector2(u0 + 0.01, v0 + 0.05), Vector2(u0 + 0.01, v0 + 0.45), Vector2(u0 + 0.24, v0 + 0.25), f)
		b.tri(s, p1, p0, p2, Vector2(u0 + 0.01, v0 + 0.45), Vector2(u0 + 0.01, v0 + 0.05), Vector2(u0 + 0.24, v0 + 0.25), -f)
		x += 0.45

static func fill_mat(m, key, b):
	match key:
		"jersey":
			m.albedo_texture = b.tex("sp/jerseys.png")
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.alpha_scissor_threshold = 0.5
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.75
		"racks":
			m.albedo_texture = b.tex("sp/racks.png"); m.roughness = 0.8
		"pennant":
			m.albedo_texture = b.tex("sp/pennant.png")
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.alpha_scissor_threshold = 0.5
			m.roughness = 0.9
		"white":
			m.albedo_color = Color("#f2f0ea"); m.roughness = 0.5
		"chrome":
			m.albedo_color = Color("#d8dadc"); m.metallic = 0.8; m.roughness = 0.25
		"dark":
			m.albedo_color = Color("#26262a"); m.roughness = 0.6
		_:
			return false
	return true
