## Shared shell and fixtures for the clothing stores built from the 1995 North East Mall
## video: JW / Jeans West, 5-7-9 and County Seat (design/storefronts/jw.md, 579.md,
## county-seat.md). Each store's store.gd places these in its own frame.
##
## Frame (as Kay-Bee's): P(a, t, n, u, y, d) = a + t u - n d + y up. u runs along the
## frontage from the edge's start `a`, d runs into the store, d < 0 is out in the hall.
## Materials are "ap_<key>", filled in by fill_mat below. Textures: paint.py -> tex/ap/.

const UP = Vector3.UP

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func L(o, r, f, x, y, z):
	return o + r * x + UP * y + f * z

## A quad facing `f`, x0..x1 by y0..y1 at depth z, texture rect (ua, va)-(ub, vb) the right way round.
static func fq(b, g, m, o, r, f, x0, x1, y0, y1, z, ua = 0.0, va = 0.0, ub = 1.0, vb = 1.0, dyn = false):
	if r.dot((-f).cross(UP)) < 0.0:
		var tmp = ua; ua = ub; ub = tmp
	b.quad(g, m, [L(o, r, f, x0, y0, z), L(o, r, f, x1, y0, z), L(o, r, f, x1, y1, z), L(o, r, f, x0, y1, z)], f,
		[Vector2(ua, vb), Vector2(ub, vb), Vector2(ub, va), Vector2(ua, va)], dyn)

static func lbox(b, g, m, o, r, f, x, y, z, w, h, dp, skip = [], dyn = false):
	var xf = Transform3D(Basis(r, UP, f), o)
	b.box(g, m, Vector3(x + w * 0.5, y + h * 0.5, z + dp * 0.5), Vector3(w, h, dp), xf, skip, dyn)

static func ob(b, p0, p1, pad = 0.12):
	b.obst(["rect", min(p0.x, p1.x) - pad, min(p0.z, p1.z) - pad, max(p0.x, p1.x) + pad, max(p0.z, p1.z) + pad])

## The room: floor, lay-in ceiling with 2 x 4 troffers in rows, side and back walls, a
## stockroom door with an exit sign. `rows` are the troffer rows' u positions.
static func shell(b, G, a, t, n, W, D, side, ceil, d_front, floor_mat, floor_tile, wall_mat, rows, door_u, light = 1.3):
	var u0 = side
	var u1 = W - side
	var dB = D - side
	var fp = [P(a, t, n, u0, 0, 0), P(a, t, n, u1, 0, 0), P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB)]
	var fuv = []
	for p in fp:
		fuv.append(Vector2(p.x / floor_tile, p.z / floor_tile))
	b.quad(G, floor_mat, fp, UP, fuv)
	var cp = [P(a, t, n, u0, ceil, d_front), P(a, t, n, u1, ceil, d_front), P(a, t, n, u1, ceil, dB), P(a, t, n, u0, ceil, dB)]
	var cuv = []
	for p in cp:
		cuv.append(Vector2(p.x / 0.61, p.z / 1.22))
	b.quad(G, "kb_ceiling", cp, Vector3.DOWN, cuv)
	var j = 0
	var dd = d_front + 1.2
	while dd + 1.22 < dB - 0.4:
		for uu in rows:
			var tq = [P(a, t, n, uu, ceil - 0.006, dd), P(a, t, n, uu + 0.61, ceil - 0.006, dd), P(a, t, n, uu + 0.61, ceil - 0.006, dd + 1.22), P(a, t, n, uu, ceil - 0.006, dd + 1.22)]
			b.quad(G, "gb_troffer", tq, Vector3.DOWN, [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
			if j % 2 == 0:
				var l = b.add_spot(P(a, t, n, uu + 0.3, ceil - 0.08, dd + 0.61), Vector3.DOWN, light, 6.0, 62.0, Color(1.0, 0.98, 0.93))
				b.tag(l, "", light, light)
		dd += 2.44
		j += 1
	b.quad(G, wall_mat, [P(a, t, n, u0, 0, 0), P(a, t, n, u0, 0, dB), P(a, t, n, u0, ceil, dB), P(a, t, n, u0, ceil, 0)], t)
	b.quad(G, wall_mat, [P(a, t, n, u1, 0, dB), P(a, t, n, u1, 0, 0), P(a, t, n, u1, ceil, 0), P(a, t, n, u1, ceil, dB)], -t)
	b.quad(G, wall_mat, [P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB), P(a, t, n, u0, ceil, dB), P(a, t, n, u1, ceil, dB)], n)
	b.cur_color = Color("#8c8a86")
	b.box(G, "vcolor", P(a, t, n, door_u, 1.05, dB - 0.02), b.abs_size(t, 0.95, 2.1, 0.04, n))
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, door_u, 2.35, dB - 0.05), b.abs_size(t, 0.36, 0.16, 0.06, n))

## A round rack: chrome base and pole, a ring rail at 1.35 m with garments hung all round.
static func round_rack(b, c, rad, row):
	var S = "ap_small"
	b.cyl(S, "ap_chrome", c, 0.3, 0.3, 0.03, 16, true, false, true)
	b.cyl(S, "ap_chrome", c, 0.025, 0.025, 1.36, 8, false, false, true)
	b.cyl(S, "ap_chrome", c + UP * 1.33, rad, rad, 0.03, 24, false, false, true)
	# the garments: a band hanging from the rail, and their shoulders seen from above
	var s = b.st("ap_fix", "ap_racks")
	var seg = 24
	var vb = (row + 1) / 4.0
	var va = row / 4.0
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var d0 = Vector3(cos(a0), 0, sin(a0))
		var d1 = Vector3(cos(a1), 0, sin(a1))
		var p0 = c + d0 * (rad + 0.06) + UP * 0.5
		var p1 = c + d1 * (rad + 0.06) + UP * 0.5
		var p2 = c + d1 * (rad + 0.04) + UP * 1.33
		var p3 = c + d0 * (rad + 0.04) + UP * 1.33
		var u0 = float(i) / seg * (TAU * rad / 2.0)
		var u1 = float(i + 1) / seg * (TAU * rad / 2.0)
		var nn = ((d0 + d1) * 0.5).normalized()
		b.tri(s, p0, p1, p2, Vector2(u0, vb), Vector2(u1, vb), Vector2(u1, va), nn)
		b.tri(s, p0, p2, p3, Vector2(u0, vb), Vector2(u1, va), Vector2(u0, va), nn)
	b.cyl("ap_fix", "ap_top", c + UP * 1.32, rad + 0.05, max(rad - 0.15, 0.05), 0.03, 24, false, false)
	ob(b, c - Vector3(rad + 0.1, 0, rad + 0.1), c + Vector3(rad + 0.1, 0, rad + 0.1), 0.1)

## A four-way: a cross of four arms at 1.4 m, each with garments hung facing out along it.
static func fourway(b, c, rot, row):
	var S = "ap_small"
	b.cyl(S, "ap_chrome", c, 0.03, 0.03, 1.45, 8, true, false, true)
	var bs = Basis(UP, rot)
	for k in 4:
		var f = bs * Vector3(sin(k * PI * 0.5), 0, cos(k * PI * 0.5))
		var r = f.cross(UP)
		# each arm and foot in the arm's own frame: sized on the world axes, a turned rack's
		# bars came out as wide slabs (Steven, Oct 6: "the areas with hanging shirts is messed up")
		var xf = Transform3D(Basis(UP, rot + k * PI * 0.5), c)
		b.box(S, "ap_chrome", Vector3(0, 1.42, 0.36), Vector3(0.025, 0.025, 0.62), xf, [], true)
		b.box(S, "ap_chrome", Vector3(0, 0.02, 0.3), Vector3(0.04, 0.04, 0.5), xf, [], true)
		# the garments hang across the arm: a block 0.6 long, 0.45 deep, from 0.6 to 1.4 m
		var o = c + f * 0.08 - r * 0.22
		var va = row / 4.0
		var vb = (row + 1) / 4.0
		fq(b, "ap_fix", "ap_racks", o, r, -f, 0.0, 0.44, 0.6, 1.4, -0.64, 0.1 * k, va, 0.1 * k + 0.22, vb)
		for sd in [0.0, 0.44]:
			b.quad("ap_fix", "ap_racks", [L(o, r, -f, sd, 0.6, -0.06), L(o, r, -f, sd, 0.6, -0.64), L(o, r, -f, sd, 1.4, -0.64), L(o, r, -f, sd, 1.4, -0.06)], r * (1.0 if sd > 0.1 else -1.0),
				[Vector2(0.3 * k, vb), Vector2(0.3 * k + 0.29, vb), Vector2(0.3 * k + 0.29, va), Vector2(0.3 * k, va)])
	ob(b, c - Vector3(0.75, 0, 0.75), c + Vector3(0.75, 0, 0.75), 0.05)

## A table of folded jeans: a wood top on a white base, three stacks on it. `half` picks
## the denim (0) or khaki (1) stacks.
static func table(b, c, rot, w, dp, half, top_mat = "ap_birch"):
	var G = "ap_fix"
	var bs = Basis(UP, rot)
	var r = bs * Vector3(1, 0, 0)
	var f = bs * Vector3(0, 0, 1)
	var o = c - r * (w * 0.5) - f * (dp * 0.5)
	lbox(b, G, "ap_white", o, r, f, 0.05, 0.0, 0.05, w - 0.1, 0.72, dp - 0.1, ["-y"])
	lbox(b, G, top_mat, o, r, f, 0.0, 0.72, 0.0, w, 0.05, dp, [])
	var n = int(w / 0.5)
	for k in n:
		var x = 0.08 + k * (w - 0.16) / n
		var sw = (w - 0.16) / n - 0.06
		lbox(b, G, "ap_folded_top", o, r, f, x, 0.77, 0.12, sw, 0.3, dp - 0.24, ["-y", "-z", "+z"])
		fq(b, G, "ap_folded", o, r, f, x, x + sw, 0.77, 1.07, dp - 0.12, half * 0.5 + 0.02, 0.5, half * 0.5 + 0.17, 1.0)
		fq(b, G, "ap_folded", o + r * w + f * dp, -r, -f, w - x - sw, w - x, 0.77, 1.07, dp - 0.12, half * 0.5 + 0.2, 0.5, half * 0.5 + 0.35, 1.0)
	ob(b, o, o + r * w + f * dp, 0.1)

## A wall of black slatwall with garments faced out on waterfall arms in two tiers, and a
## shelf of folded stacks on top. Runs along a side wall from d0 to d1; `wall_u` is the
## wall's face and `face` the direction into the room (t or -t).
static func faceout_wall(b, a, t, n, wall_u, face, d0, d1, row, rng, slat = "gb_slat_black", top = 2.95):
	var G = "ap_fix"
	var o = P(a, t, n, wall_u, 0, d0)
	var r = -n
	var ln = d1 - d0
	fq(b, G, slat, o, r, face, 0.0, ln, 0.0, top, 0.015, d0 / 0.305, 0.0, d1 / 0.305, top / 0.305)
	var x = 0.15
	var k = 0
	while x + 0.5 < ln:
		for tier in [[1.45, 2.4], [0.35, 1.3]]:
			var cell = rng.randi_range(0, 7)
			var pants = cell in [1, 4, 7] if row == 0 else cell in [1, 5]
			var h = tier[1] - tier[0]
			fq(b, "ap_faceout", "ap_faceouts", o, r, face, x, x + 0.48, tier[0], tier[0] + h, 0.32 + rng.randf() * 0.02,
				cell / 8.0, row * 0.5, (cell + 1) / 8.0, row * 0.5 + (0.5 if pants else 0.4), true)
			# the waterfall arm, chrome (it was plain grey and went black at night)
			lbox(b, "ap_small", "ap_chrome", o, r, face, x + 0.23, tier[1] - 0.04, 0.0, 0.02, 0.02, 0.34, [], true)
		x += 0.62
		k += 1
	# the top shelf with folded stacks
	lbox(b, G, "ap_white", o, r, face, 0.0, top - 0.42, 0.0, ln, 0.03, 0.36, [])
	var xs = 0.05
	while xs + 0.55 < ln:
		lbox(b, G, "ap_folded_top", o, r, face, xs, top - 0.39, 0.03, 0.5, 0.3, 0.3, ["-y", "+z"])
		fq(b, G, "ap_folded", o, r, face, xs, xs + 0.5, top - 0.39, top - 0.09, 0.33, rng.randf() * 0.3, 0.45, rng.randf() * 0.3 + 0.2, 1.0)
		xs += 0.6
	ob(b, o, o + r * ln + face * 0.4, 0.1)

## White cubbies of folded denim along a wall, to `hgt`: 0.4 m cells, 0.4 m deep.
static func cubbies(b, a, t, n, wall_u, face, d0, d1, hgt):
	var G = "ap_fix"
	var o = P(a, t, n, wall_u, 0, d0)
	var r = -n
	var ln = d1 - d0
	lbox(b, G, "ap_white", o, r, face, 0.0, 0.0, 0.0, ln, 0.12, 0.42, ["-y"])
	var rows = int((hgt - 0.12) / 0.4)
	for k in rows:
		var y = 0.12 + k * 0.4
		fq(b, G, "ap_folded", o, r, face, 0.0, ln, y, y + 0.37, 0.4, fmod(k * 0.37, 1.0) * 0.5, 0.0, fmod(k * 0.37, 1.0) * 0.5 + ln / 1.2, 1.0)
		lbox(b, G, "ap_white", o, r, face, 0.0, y + 0.37, 0.0, ln, 0.03, 0.42, [])
	var x = 0.0
	while x <= ln + 0.001:
		lbox(b, G, "ap_white", o, r, face, x - 0.015, 0.12, 0.0, 0.03, rows * 0.4, 0.42, ["-y"])
		x += 0.6
	ob(b, o, o + r * ln + face * 0.42, 0.08)

## A cash wrap: a laminate counter with a register; `o` its left end, `r` along, `f` toward shoppers.
static func cash_wrap(b, o, r, f, w, dp = 0.6, face_mat = "ap_black"):
	var G = "ap_fix"
	lbox(b, G, face_mat, o, r, f, 0.0, 0.0, 0.0, w, 0.98, dp, ["-y"])
	lbox(b, G, "ap_laminate", o, r, f, -0.03, 0.98, -0.03, w + 0.06, 0.04, dp + 0.06, [])
	var S = "ap_small"
	var ro = L(o, r, f, w * 0.35, 1.02, 0.12)
	b.cur_color = Color("#d9d2bf")
	lbox(b, S, "vcolor", ro, r, f, 0.0, 0.0, 0.0, 0.42, 0.1, 0.4, ["-y"], true)
	lbox(b, S, "vcolor", ro, r, f, 0.06, 0.1, 0.02, 0.3, 0.27, 0.26, ["-y"], true)
	b.cur_color = Color("#f4f2ec")
	lbox(b, S, "vcolor", ro, r, f, 0.7, 0.0, 0.1, 0.3, 0.12, 0.3, ["-y"], true)   # bags
	b.cur_color = Color.WHITE
	ob(b, o, o + r * w + f * dp, 0.12)

## Fitting rooms across the back: partitions, louvred doors, a long mirror on the end wall.
static func fitting_rooms(b, a, t, n, u0, u1, d_back, deep, count, door_mat = "ap_door"):
	var G = "ap_fix"
	var w = (u1 - u0) / count
	var df = d_back - deep
	for k in count + 1:
		var u = u0 + k * w
		b.box(G, "ap_white", P(a, t, n, u, 1.1, (df + d_back) * 0.5), b.abs_size(t, 0.05, 2.2, deep, n), Transform3D.IDENTITY, ["-y"])
	for k in count:
		var u = u0 + k * w + 0.08
		var dw = w - 0.16
		b.box(G, door_mat, P(a, t, n, u + dw * 0.5, 1.05, df + 0.02), b.abs_size(t, dw, 1.8, 0.04, n), Transform3D.IDENTITY, ["-y"])
	b.quad(G, "ap_white", [P(a, t, n, u0, 2.2, df), P(a, t, n, u1, 2.2, df), P(a, t, n, u1, 2.2, d_back), P(a, t, n, u0, 2.2, d_back)], UP)
	ob(b, P(a, t, n, u0, 0, df), P(a, t, n, u1, 0, d_back), 0.1)

## A plain mannequin of the period: grey-white figure, top and bottom in garment colours.
static func mannequin(b, c, facing, top_col, bot_col, s = 1.0):
	var S = "ap_small"
	var r = facing.cross(UP)
	b.cur_color = Color("#3a3a3e")
	b.cyl(S, "vcolor", c, 0.18, 0.18, 0.02, 12, true, false, true)
	b.cyl(S, "vcolor", c, 0.012, 0.012, 0.45 * s, 6, false, false, true)
	b.cur_color = Color(bot_col)
	for sd in [-1.0, 1.0]:
		b.cyl(S, "vcolor_matte", c + r * (0.09 * sd * s) + UP * 0.05, 0.065 * s, 0.075 * s, 0.9 * s, 10, false, false, true)
	b.cyl(S, "vcolor_matte", c + UP * 0.9 * s, 0.17 * s, 0.17 * s, 0.12 * s, 12, false, false, true)
	b.cur_color = Color(top_col)
	b.cyl(S, "vcolor_matte", c + UP * 1.0 * s, 0.17 * s, 0.21 * s, 0.42 * s, 12, true, false, true)
	for sd in [-1.0, 1.0]:
		b.cyl(S, "vcolor_matte", c + r * (0.23 * sd * s) + UP * 0.78 * s, 0.05 * s, 0.06 * s, 0.62 * s, 8, false, false, true)
	# a small egg-shaped head on a neck (realistic proportions, no features)
	b.cur_color = Color("#e8e6e0")
	b.cyl(S, "vcolor", c + UP * 1.42 * s, 0.04 * s, 0.04 * s, 0.07 * s, 8, false, false, true)
	b.cyl(S, "vcolor", c + UP * 1.49 * s, 0.045 * s, 0.075 * s, 0.07 * s, 10, false, false, true)
	b.cyl(S, "vcolor", c + UP * 1.56 * s, 0.075 * s, 0.07 * s, 0.07 * s, 10, false, false, true)
	b.cyl(S, "vcolor", c + UP * 1.63 * s, 0.07 * s, 0.03 * s, 0.07 * s, 10, true, false, true)
	b.cur_color = Color.WHITE
	ob(b, c - Vector3(0.25, 0, 0.25), c + Vector3(0.25, 0, 0.25), 0.05)

## A hanging sign card (signs.png cell), both faces, on two wires up to the ceiling.
static func hang_sign(b, c, facing, cell, w, h, ceil):
	var r = facing.cross(UP)
	var cu = (cell % 2) * 0.5
	var cv = (cell / 2) * 0.5
	for s in [1.0, -1.0]:
		var f = facing * s
		var rr = r * s
		var o = c - rr * (w * 0.5) + f * 0.004
		fq(b, "ap_small", "ap_signs", o, rr, f, 0.0, w, 0.0, h, 0.0, cu, cv, cu + 0.5, cv + 0.5, true)
	b.cur_color = Color("#c8c8c8")
	for sd in [-0.4, 0.4]:
		b.box("ap_small", "vcolor", c + r * (w * sd) + UP * ((ceil - c.y - h) * 0.5 + h), Vector3(0.006, ceil - c.y - h, 0.006), Transform3D.IDENTITY, [], true)
	b.cur_color = Color.WHITE

## Raised letters from a make_signs.py json: faces and returns, placed on a wall plane.
## `c` is the centre of the text's baseline on the wall, `nn` the wall's outward normal.
static func letters(b, g, path, c, nn, face_mat, side_mat, standoff = 0.03, depth = 0.08, dyn = true):
	var J = JSON.parse_string(FileAccess.get_file_as_string(path))
	var rv = (-nn).cross(UP)
	var wv = float(J.width)
	var X = func(p, d): return c - rv * (wv * 0.5) + rv * float(p[0]) + UP * float(p[1]) + nn * d
	for Lt in J.letters:
		var tr = Lt.tris
		var s = b.st(g, face_mat, dyn)
		for i in range(0, tr.size(), 3):
			b.tri(s, X.call(tr[i], standoff + depth), X.call(tr[i + 1], standoff + depth), X.call(tr[i + 2], standoff + depth), Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector2(0.5, 0.5), nn)
		for lp in Lt.loops:
			for i in lp.size():
				var q0 = lp[i]
				var q1 = lp[(i + 1) % lp.size()]
				var dx = float(q1[0]) - float(q0[0])
				var dy = float(q1[1]) - float(q0[1])
				var ln = sqrt(dx * dx + dy * dy)
				if ln < 1e-5:
					continue
				var en = (rv * (dy / ln) - UP * (dx / ln)).normalized()
				b.quad(g, side_mat, [X.call(q0, standoff), X.call(q1, standoff), X.call(q1, standoff + depth), X.call(q0, standoff + depth)], en,
					[Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)], dyn)

## Neon tubes traced along the letters' outlines (JW): each outline as a chain of thin
## boxes, and a second chain inset (the sign is double-lined).
static func neon(b, g, path, c, nn, mat, inset = 0.035, tube = 0.016, standoff = 0.06):
	var J = JSON.parse_string(FileAccess.get_file_as_string(path))
	var rv = (-nn).cross(UP)
	var wv = float(J.width)
	for Lt in J.letters:
		for lp in Lt.loops:
			var pts = []
			for q in lp:
				pts.append(Vector2(float(q[0]), float(q[1])))
			# simplify: drop points closer than 3 cm
			var simp = [pts[0]]
			for p in pts:
				if p.distance_to(simp[simp.size() - 1]) > 0.03:
					simp.append(p)
			for pass_i in 2:
				var ring = simp
				if pass_i == 1:
					ring = []
					var area = 0.0
					for i in simp.size():
						area += simp[i].x * simp[(i + 1) % simp.size()].y - simp[(i + 1) % simp.size()].x * simp[i].y
					var sgn = 1.0 if area > 0.0 else -1.0
					for i in simp.size():
						var pr = simp[(i - 1 + simp.size()) % simp.size()]
						var nx = simp[(i + 1) % simp.size()]
						var tg = (nx - pr).normalized()
						var inward = Vector2(-tg.y, tg.x) * sgn
						ring.append(simp[i] + inward * inset)
				for i in ring.size():
					var p0 = ring[i]
					var p1 = ring[(i + 1) % ring.size()]
					var w0 = c - rv * (wv * 0.5) + rv * p0.x + UP * p0.y + nn * standoff
					var w1 = c - rv * (wv * 0.5) + rv * p1.x + UP * p1.y + nn * standoff
					var dvec = w1 - w0
					var ln = dvec.length()
					if ln < 0.005:
						continue
					var yax = dvec / ln
					var xax = yax.cross(nn).normalized()
					b.box(g, mat, Vector3.ZERO, Vector3(tube, ln + tube, tube), Transform3D(Basis(xax, yax, nn), (w0 + w1) * 0.5), [], true)

# ------------------------------------------------------------------ materials
## "ap_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"racks":
			m.albedo_texture = b.tex("ap/racks.png"); m.roughness = 0.8
		"faceouts":
			m.albedo_texture = b.tex("ap/faceouts.png"); m.roughness = 0.8
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			# probe-lit (alpha): a little glow keeps them from going grey
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			# 0.25 left them near black on the black slatwall in the baked game (Steven, Oct 6:
			# "significant lighting bugs in JW"): they are lit by probes only, so carry more of their own
			m.emission_energy_multiplier = 0.75
			m.set_meta("e_day", 0.75); m.set_meta("e_night", 0.75)
		"folded":
			m.albedo_texture = b.tex("ap/folded.png"); m.roughness = 0.85
		"folded_top":
			m.albedo_color = Color("#55688e"); m.roughness = 0.9
		"top":
			m.albedo_color = Color("#3c4048"); m.roughness = 0.9
		"signs":
			m.albedo_texture = b.tex("ap/signs.png"); m.roughness = 0.6
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.3)
		"posters":
			m.albedo_texture = b.tex("ap/posters.png"); m.roughness = 0.3; m.metallic_specular = 0.6
		"wood":
			m.albedo_texture = b.tex("ap/wood.png"); m.roughness = 0.35; m.metallic_specular = 0.5
		"tile_cs":
			m.albedo_texture = b.tex("ap/tile_cs.png"); m.roughness = 0.25; m.metallic_specular = 0.55
		"chrome":
			# bright metal: half metallic so it reads light even where the probe is dim
			m.albedo_color = Color("#e4e6e8"); m.metallic = 0.5; m.roughness = 0.25
			# racks and arms are probe-lit, and the night probes by the black slatwall are dark:
			# a faint glow of their own keeps them reading as chrome, not black
			m.emission_enabled = true; m.emission = Color("#9ea2a8")
			m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.45)
		"black":
			m.albedo_color = Color("#1c1c1e"); m.roughness = 0.5
		"charcoal":
			m.albedo_color = Color("#3a3a3e"); m.roughness = 0.6
		"white":
			m.albedo_color = Color("#f0f0ec"); m.roughness = 0.45; m.metallic_specular = 0.4
		"cream":
			m.albedo_color = Color("#efe9dc"); m.roughness = 0.85
		"birch":
			m.albedo_color = Color("#d8bf94"); m.roughness = 0.45; m.metallic_specular = 0.45
		"laminate":
			m.albedo_color = Color("#ecebe6"); m.roughness = 0.3; m.metallic_specular = 0.5
		"door":
			m.albedo_color = Color("#a07a50"); m.roughness = 0.6
		"mirror":
			m.albedo_color = Color("#cfd6da"); m.metallic = 1.0; m.roughness = 0.02
		"neon":
			m.albedo_color = Color("#f4f8ff")
			m.emission_enabled = true; m.emission = Color("#eaf2ff"); m.emission_energy_multiplier = 4.0
			m.set_meta("e_day", 3.0); m.set_meta("e_night", 4.0)
		"neon_red":
			m.albedo_color = Color("#ff4050")
			m.emission_enabled = true; m.emission = Color("#ff2040"); m.emission_energy_multiplier = 3.0
			m.set_meta("e_day", 2.5); m.set_meta("e_night", 3.0)
		"yellow":
			# 5-7-9's numerals: yellow faces, a polished look (video 0:33)
			m.albedo_color = Color("#f2e21a"); m.roughness = 0.2; m.metallic_specular = 0.8
			m.emission_enabled = true; m.emission = Color("#e8d818"); m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.4)
		"steel":
			m.albedo_color = Color("#c8ccd0"); m.metallic = 0.75; m.roughness = 0.2
		"letterwhite":
			m.albedo_color = Color("#f6f6f2"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#f0f0ea"); m.emission_energy_multiplier = 0.4
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.5)
		"letterdark":
			m.albedo_color = Color("#141416"); m.roughness = 0.55
		_:
			return false
	return true
