## Gumballs (store s8), the corner candy-and-novelty shop on the Dillard's court, built to
## design/storefronts/gumballs.md.
##
## The sign and everything inside follow the 1995 North East Mall video Steven chose:
## - the cobalt-blue brush script with its swash, the gumball cluster and the "Sweet Ideas"
##   plaque on a white fascia;
## - the wall of acrylic scoop bins with plush on the shelves above;
## - satin jackets on a rail; the black slatwall of bagged T-shirts; posters; card spinners;
## - the glass candy case under a red oval sign; the big globe gumball machine;
## - lava lamps and knickknacks.
## The front wraps the corner the way the Southland unit does: open round the corner, with
## a show window at each end. All package art and graphics are original (paint_store.py).
##
## Frame: world coordinates. The unit is x X0..X1 by z Z0..Z1. The hall face is x = X1
## (looking out +x), the court face z = Z1 (looking out +z), and their corner is (X1, Z1).
## The back walls are x = X0 and z = Z0. y is up.

const X0 = -20.0
const X1 = -10.0
const Z0 = 36.0
const Z1 = 48.0
const SIDE = 0.12        # party walls' inner faces
const HEAD = 2.6         # bottom of the fascia = top of the openings
const FTOP = 4.2         # top of the fascia (the sign fills it in the video)
const PROUD = 0.12
const VEST = 1.2         # the soffit with its downlights runs this far in
const CEIL = 3.2
const HALL_OPEN = 40.2   # the hall face is open from here round the corner...
const COURT_OPEN = -15.0 # ...to here on the court face
const PIER = 0.25
const SILL = 0.45        # show window bulkhead
const UP = Vector3.UP

# ------------------------------------------------------------------ local-frame helpers (as Kay-Bee's)
static func L(o, r, f, x, y, z):
	return o + r * x + UP * y + f * z

## A quad facing `f` at depth z, x0..x1 by y0..y1, showing texture rect (ua, va)-(ub, vb)
## the right way round for someone looking at it.
static func fq(b, g, m, o, r, f, x0, x1, y0, y1, z, ua = 0.0, va = 0.0, ub = 1.0, vb = 1.0, dyn = false):
	if r.dot((-f).cross(UP)) < 0.0:
		var tmp = ua; ua = ub; ub = tmp
	b.quad(g, m, [L(o, r, f, x0, y0, z), L(o, r, f, x1, y0, z), L(o, r, f, x1, y1, z), L(o, r, f, x0, y1, z)], f,
		[Vector2(ua, vb), Vector2(ub, vb), Vector2(ub, va), Vector2(ua, va)], dyn)

static func lbox(b, g, m, o, r, f, x, y, z, w, h, dp, skip = [], dyn = false):
	var xf = Transform3D(Basis(r, UP, f), o)
	b.box(g, m, Vector3(x + w * 0.5, y + h * 0.5, z + dp * 0.5), Vector3(w, h, dp), xf, skip, dyn)

static func hq(b, g, m, o, r, f, x0, x1, z0, z1, y, up = true, dyn = false):
	b.quad(g, m, [L(o, r, f, x0, y, z0), L(o, r, f, x1, y, z0), L(o, r, f, x1, y, z1), L(o, r, f, x0, y, z1)], UP if up else Vector3.DOWN, [], dyn)

static func sq(b, g, m, o, r, f, x, z0, z1, y0, y1, sign, dyn = false):
	b.quad(g, m, [L(o, r, f, x, y0, z0), L(o, r, f, x, y0, z1), L(o, r, f, x, y1, z1), L(o, r, f, x, y1, z0)], r * sign, [], dyn)

static func ob(b, x0, z0, x1, z1, pad = 0.12):
	b.obst(["rect", min(x0, x1) - pad, min(z0, z1) - pad, max(x0, x1) + pad, max(z0, z1) + pad])

static func W(x, y, z):
	return Vector3(x, y, z)

## Called for each of the unit's two frontage edges: everything is built on the hall edge.
static func build(b, g, e, a, bb, n, t, Ln, sd):
	if n.x < 0.5:
		return
	var rng = RandomNumberGenerator.new()
	rng.seed = 1995
	front(b, "gbf_props")
	logo_sign(b, "gbf_props", W(X1 + PROUD, 0, 42.3), Vector3(1, 0, 0))
	logo_sign(b, "gbf_props", W(-15.0, 0, Z1 + PROUD), Vector3(0, 0, 1))
	room(b, "gb_shell")
	fixtures(b, rng)
	var rp = ReflectionProbe.new()
	rp.position = W((X0 + X1) * 0.5, CEIL * 0.5, (Z0 + Z1) * 0.5)
	rp.size = Vector3(X1 - X0 + 0.1, CEIL + 0.1, Z1 - Z0 + 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ the front
static func front(b, g):
	var LH = b.LANE_H
	# white fascia, standing proud, wrapping the corner (no overlap at the corner)
	b.box(g, "gb_fascia", W(X1 + PROUD * 0.5, (HEAD + FTOP) * 0.5, (Z0 + Z1) * 0.5), Vector3(PROUD, FTOP - HEAD, Z1 - Z0), Transform3D.IDENTITY, ["-x"])
	b.box(g, "gb_fascia", W((X0 + X1 + PROUD) * 0.5, (HEAD + FTOP) * 0.5, Z1 + PROUD * 0.5), Vector3(X1 + PROUD - X0, FTOP - HEAD, PROUD), Transform3D.IDENTITY, ["-z"])
	# a grey reveal over the fascia, then white bulkhead to the lane ceiling
	for face in [[Vector3(1, 0, 0), W(X1, 0, Z0), W(X1, 0, Z1)], [Vector3(0, 0, 1), W(X1, 0, Z1), W(X0, 0, Z1)]]:
		var nn = face[0]
		var p0 = face[1]
		var p1 = face[2]
		b.quad(g, "gb_grey", [p0 + UP * FTOP, p1 + UP * FTOP, p1 + UP * (FTOP + 0.1), p0 + UP * (FTOP + 0.1)], nn)
		b.quad("gb_shell", "gb_wall", [p0 + UP * (FTOP + 0.1), p1 + UP * (FTOP + 0.1), p1 + UP * LH, p0 + UP * LH], nn)
	# hall face: party-wall end post, show window (bulkhead, glass), pier; then open
	b.box(g, "gb_fascia", W(X1 - 0.15, HEAD * 0.5, Z0 + 0.06), Vector3(0.3, HEAD, 0.12))
	b.box(g, "gb_fascia", W(X1 - 0.15, SILL * 0.5, (Z0 + 0.12 + HALL_OPEN - PIER) * 0.5), Vector3(0.3, SILL, HALL_OPEN - PIER - Z0 - 0.12), Transform3D.IDENTITY, ["-y"])
	b.box(g, "gb_fascia", W(X1 - 0.15, HEAD * 0.5, HALL_OPEN - PIER * 0.5), Vector3(0.3, HEAD, PIER), Transform3D.IDENTITY, ["-y"])
	b.quad("glass", "glass", [W(X1 - 0.02, SILL, Z0 + 0.12), W(X1 - 0.02, SILL, HALL_OPEN - PIER), W(X1 - 0.02, HEAD, HALL_OPEN - PIER), W(X1 - 0.02, HEAD, Z0 + 0.12)], Vector3(1, 0, 0),
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# court face: open from the corner to the pier, then the show window to the party wall
	b.box(g, "gb_fascia", W(COURT_OPEN - PIER * 0.5, HEAD * 0.5, Z1 - 0.15), Vector3(PIER, HEAD, 0.3), Transform3D.IDENTITY, ["-y"])
	b.box(g, "gb_fascia", W((X0 + 0.12 + COURT_OPEN - PIER) * 0.5, SILL * 0.5, Z1 - 0.15), Vector3(COURT_OPEN - PIER - X0 - 0.12, SILL, 0.3), Transform3D.IDENTITY, ["-y"])
	b.box(g, "gb_fascia", W(X0 + 0.06, HEAD * 0.5, Z1 - 0.15), Vector3(0.12, HEAD, 0.3))
	b.quad("glass", "glass", [W(X0 + 0.12, SILL, Z1 - 0.02), W(COURT_OPEN - PIER, SILL, Z1 - 0.02), W(COURT_OPEN - PIER, HEAD, Z1 - 0.02), W(X0 + 0.12, HEAD, Z1 - 0.02)], Vector3(0, 0, 1),
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# the soffit under the fascia, an L round the front, with round downlights (video)
	var sp = [[X1 - VEST, X1, Z0 + SIDE, Z1], [X0 + SIDE, X1 - VEST, Z1 - VEST, Z1]]
	for s in sp:
		b.quad(g, "gb_soffit", [W(s[0], HEAD, s[2]), W(s[1], HEAD, s[2]), W(s[1], HEAD, s[3]), W(s[0], HEAD, s[3])], Vector3.DOWN)
	# the step up from the soffit to the room's ceiling
	b.quad("gb_shell", "gb_wall", [W(X1 - VEST, HEAD, Z0 + SIDE), W(X1 - VEST, HEAD, Z1 - VEST), W(X1 - VEST, CEIL, Z1 - VEST), W(X1 - VEST, CEIL, Z0 + SIDE)], Vector3(-1, 0, 0))
	b.quad("gb_shell", "gb_wall", [W(X0 + SIDE, HEAD, Z1 - VEST), W(X1 - VEST, HEAD, Z1 - VEST), W(X1 - VEST, CEIL, Z1 - VEST), W(X0 + SIDE, CEIL, Z1 - VEST)], Vector3(0, 0, -1))
	var cans = []
	var z = Z0 + 0.9
	while z < Z1 - 0.3:
		cans.append(W(X1 - 0.6, HEAD - 0.005, z)); z += 1.5
	var x = X1 - 1.8
	while x > X0 + 0.5:
		cans.append(W(x, HEAD - 0.005, Z1 - 0.6)); x -= 1.5
	for c in cans:
		b.box(g, "gb_can", c, Vector3(0.22, 0.01, 0.22), Transform3D.IDENTITY, ["+y"])
	# the windows' displays
	window_hall(b)
	window_court(b)
	ob(b, X1 - 0.3, Z0, X1, HALL_OPEN, 0.15)
	ob(b, X0, Z1 - 0.3, COURT_OPEN, Z1, 0.15)

# ------------------------------------------------------------------ the sign
## "Gumballs" in cobalt-blue acrylic on stand-offs, the gumball cluster and the plaque.
## `c` is the centre of the fascia face at floor level, `nn` the face's outward normal.
static func logo_sign(b, g, c, nn):
	var J = JSON.parse_string(FileAccess.get_file_as_string("res://tools/stores/gumballs/logo.json"))
	var rv = (-nn).cross(UP)          # the reader's right
	var wv = float(J.width)
	var y0 = 2.69
	var stand = 0.05
	var dpt = 0.07
	var X = func(p, d): return c - rv * (wv * 0.5) + rv * float(p[0]) + UP * (y0 + float(p[1])) + nn * d
	for Lt in J.letters:
		var tr = Lt.tris
		var s = b.st(g, "gb_logo", true)
		for i in range(0, tr.size(), 3):
			b.tri(s, X.call(tr[i], stand + dpt), X.call(tr[i + 1], stand + dpt), X.call(tr[i + 2], stand + dpt), Vector2(0.5, 0.2), Vector2(0.5, 0.2), Vector2(0.5, 0.2), nn)
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
				b.quad(g, "gb_logoside", [X.call(q0, stand), X.call(q1, stand), X.call(q1, stand + dpt), X.call(q0, stand + dpt)], en,
					[Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)], true)
	# the plaque, a little right of centre under "mba" (video), and the gumballs over it
	var pc = c + rv * 0.16 + UP * 2.68 + nn * 0.02
	var pw = 1.3
	var ph = 0.38
	var o = pc - rv * (pw * 0.5)
	lbox(b, g, "gb_plaqueedge", o, rv, nn, 0.0, 0.0, 0.0, pw, ph, 0.05, ["-z"], true)
	fq(b, g, "gb_plaque", o, rv, nn, 0.0, pw, 0.0, ph, 0.052, 0, 0, 1, 1, true)
	var balls = [[-0.42, 0.47, 0.085, 0], [-0.26, 0.50, 0.09, 1], [-0.09, 0.48, 0.09, 2], [0.08, 0.51, 0.09, 3], [0.25, 0.48, 0.09, 4], [0.41, 0.46, 0.08, 6],
		[-0.18, 0.64, 0.08, 5], [0.0, 0.66, 0.085, 7], [0.17, 0.64, 0.08, 1]]
	for bl in balls:
		ball(b, g, pc + rv * bl[0] + UP * (bl[1] - 0.05) + nn * 0.02, bl[2], "gb_ball%d" % bl[3])

## A sphere of stacked rings (dynamic: small and round).
static func ball(b, g, c, rad, m, seg = 8):
	for k in seg:
		var a0 = -PI * 0.5 + PI * k / seg
		var a1 = -PI * 0.5 + PI * (k + 1) / seg
		b.cyl(g, m, c + Vector3(0, sin(a0) * rad, 0), max(cos(a0) * rad, 0.001), max(cos(a1) * rad, 0.001), (sin(a1) - sin(a0)) * rad, 14, false, false, true)

# ------------------------------------------------------------------ the room
static func room(b, G):
	var xa = X0 + SIDE
	var za = Z0 + SIDE
	# white vinyl tile floor to the front line
	var fp = [W(xa, 0, za), W(X1, 0, za), W(X1, 0, Z1), W(xa, 0, Z1)]
	var fuv = []
	for p in fp:
		fuv.append(Vector2(p.x / 0.61, p.z / 0.61))
	b.quad(G, "gb_floor", fp, UP, fuv)
	# white lay-in ceiling with 2 x 2 troffers (video), inside the soffit
	var cx1 = X1 - VEST
	var cz1 = Z1 - VEST
	var cp = [W(xa, CEIL, za), W(cx1, CEIL, za), W(cx1, CEIL, cz1), W(xa, CEIL, cz1)]
	var cuv = []
	for p in cp:
		cuv.append(Vector2(p.x / 0.61, p.z / 1.22))
	b.quad(G, "kb_ceiling", cp, Vector3.DOWN, cuv)
	var j = 0
	for tx in [-18.5, -16.06, -13.62, -11.18]:
		for tz in [37.4, 39.84, 42.28, 44.72]:
			if tx > cx1 - 0.7 or tz > cz1 - 0.7:
				continue
			var tq = [W(tx, CEIL - 0.006, tz), W(tx + 0.61, CEIL - 0.006, tz), W(tx + 0.61, CEIL - 0.006, tz + 0.61), W(tx, CEIL - 0.006, tz + 0.61)]
			b.quad(G, "gb_troffer", tq, Vector3.DOWN, [Vector2(0, 0), Vector2(1, 0), Vector2(1, 0.5), Vector2(0, 0.5)])
			if j % 2 == 0:
				var l = b.add_spot(W(tx + 0.3, CEIL - 0.08, tz + 0.3), Vector3.DOWN, 1.3, 6.0, 62.0, Color(1.0, 0.98, 0.93))
				b.tag(l, "", 1.3, 1.3)
			j += 1
	# white walls
	b.quad(G, "gb_wall", [W(xa, 0, Z1), W(xa, 0, za), W(xa, CEIL, za), W(xa, CEIL, Z1)], Vector3(1, 0, 0))
	b.quad(G, "gb_wall", [W(xa, 0, za), W(X1, 0, za), W(X1, CEIL, za), W(xa, CEIL, za)], Vector3(0, 0, 1))
	# the stockroom door in the back wall behind the cash wrap, an exit sign over it
	b.cur_color = Color("#d8d6d0")
	b.box(G, "vcolor", W(-12.4, 1.05, za + 0.02), Vector3(0.95, 2.1, 0.04))
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", W(-12.4, 2.35, za + 0.05), Vector3(0.36, 0.16, 0.06))

# ------------------------------------------------------------------ fixtures
## One bay (1.22 m) of acrylic scoop bins on a white base: four tiers (0.5-1.8 m), the lids
## sloping back, a white shelf with plush over it and a second plush shelf above (video).
## `o` is the bay's left end on the wall, `r` along the wall, `f` out into the room.
static func bins_bay(b, o, r, f, variant, plush_rows = 2, rng = null):
	var G = "gb_fix"
	var w = 1.22
	lbox(b, G, "gb_white", o, r, f, 0.0, 0.0, 0.0, w, 0.5, 0.56, ["-y", "-z"])
	# the bins: a deep block with the painted fronts, lids sloping back to the wall
	fq(b, G, "gb_bins", o, r, f, 0.0, w, 0.5, 1.8, 0.52, variant * 0.5, 0.0, variant * 0.5 + 0.5, 1.0)
	b.quad(G, "gb_acrylic", [L(o, r, f, 0, 1.8, 0.52), L(o, r, f, w, 1.8, 0.52), L(o, r, f, w, 1.9, 0.1), L(o, r, f, 0, 1.9, 0.1)], (f + UP * 4.2).normalized())
	for x in [0.0, w]:
		sq(b, G, "gb_white", o, r, f, x, 0.0, 0.52, 0.5, 1.9, -1.0 if x == 0.0 else 1.0)
	var y = 1.95
	for k in plush_rows:
		lbox(b, G, "gb_white", o, r, f, 0.0, y, 0.0, w, 0.03, 0.36, ["-z"])
		var u0 = rng.randf() * 0.5 if rng else 0.0
		fq(b, G, "gb_plush", o, r, f, 0.02, w - 0.02, y + 0.03, y + 0.47, 0.22, u0, 0.18, u0 + 0.5, 1.0)
		y += 0.55

## The satin jackets hung on a rail over a bay of bins (video 3:22-3:28).
static func jacket_rail(b, o, r, f, w, u0):
	var G = "gb_fix"
	b.cur_color = Color("#b4b6ba")
	lbox(b, "gb_small", "vcolor", o, r, f, 0.0, 2.95, 0.0, w, 0.03, 0.03, [], true)
	b.cur_color = Color.WHITE
	fq(b, G, "gb_jackets", o, r, f, 0.0, w, 1.95, 2.95, 0.32, u0, 0.0, u0 + w / 2.44, 1.0)
	sq(b, G, "gb_wall", o, r, f, 0.0, 0.0, 0.32, 1.95, 2.95, -1.0)
	sq(b, G, "gb_wall", o, r, f, w, 0.0, 0.32, 1.95, 2.95, 1.0)

## The candy case: a white-framed glass showcase with three shelves of chocolates and
## lollipops, a laminate top. `o` its left end at the floor, `r` along, `f` toward shoppers.
static func showcase(b, o, r, f, w, u0 = 0.0):
	var G = "gb_fix"
	lbox(b, G, "gb_white", o, r, f, 0.0, 0.0, 0.0, w, 0.32, 0.62, ["-y"])
	lbox(b, G, "gb_white", o, r, f, 0.0, 0.32, 0.0, w, 0.7, 0.08, ["-y"])          # staff side panel
	fq(b, G, "gb_showcase", o, r, f, 0.0, w, 0.32, 1.02, 0.081, u0, 0.0, u0 + w / 1.6, 1.0)
	for x in [0.0, w - 0.04]:
		lbox(b, G, "gb_white", o, r, f, x, 0.32, 0.08, 0.04, 0.7, 0.54, ["-y"])
	lbox(b, G, "gb_counter", o, r, f, -0.03, 1.02, -0.03, w + 0.06, 0.04, 0.68, [])
	b.quad("glass", "glass", [L(o, r, f, 0.04, 0.32, 0.6), L(o, r, f, w - 0.04, 0.32, 0.6), L(o, r, f, w - 0.04, 1.02, 0.6), L(o, r, f, 0.04, 1.02, 0.6)], f,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)

## A spinner rack: a pole and four printed faces (cards), on a round foot.
static func spinner(b, c, rot, hgt = 1.7, w = 0.46, m = "gb_cards"):
	var G = "gb_fix"
	b.cur_color = Color("#3a3a3e")
	b.cyl("gb_small", "vcolor", c, 0.22, 0.22, 0.03, 16, true, false, true)
	b.cyl("gb_small", "vcolor", c, 0.02, 0.02, hgt + 0.15, 8, true, false, true)
	b.cur_color = Color.WHITE
	var basis = Basis(UP, rot)
	for k in 4:
		var f = basis * Vector3(sin(k * PI * 0.5), 0, cos(k * PI * 0.5))
		var r = (-f).cross(UP) * -1.0
		var o = c + f * (w * 0.5) - r * (w * 0.5)
		fq(b, G, m, o, r, f, 0.0, w, 0.25, hgt, 0.0, (k % 2) * 0.5, 0.0, (k % 2) * 0.5 + 0.5, 1.0)
	ob(b, c.x - 0.28, c.z - 0.28, c.x + 0.28, c.z + 0.28, 0.12)

## A lava lamp: a tapered metal base, the glowing bottle bulging at the middle, a cap.
static func lava(b, c, col, s = 1.0):
	var G = "gb_small"
	b.cyl(G, "gb_chrome", c, 0.062 * s, 0.038 * s, 0.13 * s, 14, false, true, true)
	var m = "gb_lava_%s" % col
	b.cyl(G, m, c + UP * 0.13 * s, 0.038 * s, 0.062 * s, 0.13 * s, 14, false, false, true)
	b.cyl(G, m, c + UP * 0.26 * s, 0.062 * s, 0.036 * s, 0.15 * s, 14, false, false, true)
	b.cyl(G, "gb_chrome", c + UP * 0.41 * s, 0.036 * s, 0.022 * s, 0.06 * s, 14, true, false, true)

## The big globe gumball machine by the door (video 3:30): a maroon wood stand, a chrome
## ring and coin mechanism, a clear globe two-thirds full of gumballs, a chrome lid.
static func globe_machine(b, c):
	var S = "gb_small"
	b.cyl("gb_fix", "gb_maroon", c, 0.26, 0.22, 0.95, 20, true, false)
	b.cyl(S, "gb_chrome", c + UP * 0.95, 0.28, 0.28, 0.05, 20, true, false, true)
	var gc = c + UP * 1.4
	var R = 0.43
	# the gumballs: a spherical cap up to 0.62 of the globe's height, and their flat top
	var fill_top = -R + 2.0 * R * 0.62
	var seg = 8
	for k in seg:
		var y0 = -R + (fill_top + R) * k / seg
		var y1 = -R + (fill_top + R) * (k + 1) / seg
		var r0 = sqrt(max(R * R - y0 * y0, 0.0)) * 0.97
		var r1 = sqrt(max(R * R - y1 * y1, 0.0)) * 0.97
		b.cyl(S, "gb_gumballs", gc + UP * y0, max(r0, 0.01), r1, y1 - y0, 20, k == seg - 1, false, true)
	ball(b, S, gc, R, "gb_globe", 10)
	b.cyl(S, "gb_chrome", gc + UP * (R - 0.02), 0.09, 0.07, 0.06, 16, true, false, true)
	# the coin mechanism on the stand's front, facing the court entrance
	b.box(S, "gb_chrome", c + UP * 1.12 + Vector3(0, 0, 0.27), Vector3(0.14, 0.18, 0.06), Transform3D.IDENTITY, [], true)
	ob(b, c.x - 0.3, c.z - 0.3, c.x + 0.3, c.z + 0.3, 0.12)

## A small classic gumball machine: red cast base, glass globe, gumballs.
static func small_machine(b, c):
	var S = "gb_small"
	b.cyl(S, "gb_red", c, 0.11, 0.08, 0.2, 14, true, false, true)
	var gc = c + UP * 0.33
	var R = 0.13
	b.cyl(S, "gb_gumballs", gc + UP * (-R), 0.03, R * 0.95, R * 1.2, 14, true, false, true)
	ball(b, S, gc, R, "gb_globe", 8)
	b.cyl(S, "gb_red", gc + UP * (R - 0.01), 0.05, 0.04, 0.04, 12, true, false, true)

## Everything on the floor and the walls.
static func fixtures(b, rng):
	var xa = X0 + SIDE
	var za = Z0 + SIDE
	var G = "gb_fix"
	# --- north wall: the bulk-candy wall, four bays, plush on two shelves above
	var o = W(-19.5, 0, za)
	for k in 4:
		bins_bay(b, o + Vector3(1.22 * k, 0, 0), Vector3(1, 0, 0), Vector3(0, 0, 1), k % 2, 2, rng)
	ob(b, -19.5, za, -19.5 + 4 * 1.22, za + 0.56)
	# --- west wall, back: three bays of bins with satin jackets hung above
	o = W(xa, 0, 40.26)
	for k in 3:
		var ok = o + Vector3(0, 0, -1.22 * k)
		bins_bay(b, ok, Vector3(0, 0, -1), Vector3(1, 0, 0), (k + 1) % 2, 0, rng)
		jacket_rail(b, ok, Vector3(0, 0, -1), Vector3(1, 0, 0), 1.22, k * 0.31)
	ob(b, xa, 40.26 - 3 * 1.22, xa + 0.56, 40.26)
	# --- west wall, front: black slatwall of bagged T-shirts to the ceiling (video 3:07)
	var t0 = 40.5
	var t1 = 46.0
	var tw = t1 - t0
	b.quad(G, "gb_slat_black", [W(xa + 0.02, 0, t1), W(xa + 0.02, 0, t0), W(xa + 0.02, CEIL, t0), W(xa + 0.02, CEIL, t1)], Vector3(1, 0, 0),
		[Vector2(t1 / 0.305, CEIL / 0.305), Vector2(t0 / 0.305, CEIL / 0.305), Vector2(t0 / 0.305, 0), Vector2(t1 / 0.305, 0)])
	o = W(xa, 0, t1)
	fq(b, G, "gb_tees", o, Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, tw, 0.75, 3.15, 0.05, 0.0, 0.0, tw / 2.44, 2.4 / 2.44)
	lbox(b, G, "gb_white", o, Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, 0.0, 0.0, tw, 0.6, 0.45, ["-y", "-z"])
	fq(b, G, "gb_boxes", o, Vector3(0, 0, -1), Vector3(1, 0, 0), 0.05, tw - 0.05, 0.6, 0.72, 0.3, 0.0, 0.0, 2.0, 0.25)
	ob(b, xa, t0, xa + 0.45, t1)
	# the SNACKS dispenser tower between the jackets and the T-shirts (video 3:10)
	b.box(G, "gb_blue", W(xa + 0.33, 0.95, 40.38), Vector3(0.5, 1.9, 0.5), Transform3D.IDENTITY, ["-y"])
	fq(b, G, "gb_snacks", W(xa + 0.581, 0, 40.63), Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, 0.5, 0.05, 1.85, 0.0)
	ob(b, xa, 40.13, xa + 0.6, 40.63)
	# --- west wall by the court window: posters on white slatwall, a keychain spinner
	b.quad(G, "gb_slat_white", [W(xa + 0.02, 0, Z1 - 0.3), W(xa + 0.02, 0, t1), W(xa + 0.02, CEIL, t1), W(xa + 0.02, CEIL, Z1 - 0.3)], Vector3(1, 0, 0),
		[Vector2((Z1 - 0.3) / 0.305, CEIL / 0.305), Vector2(t1 / 0.305, CEIL / 0.305), Vector2(t1 / 0.305, 0), Vector2((Z1 - 0.3) / 0.305, 0)])
	fq(b, G, "gb_posters", W(xa, 0, Z1 - 0.4), Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, 1.5, 1.2, 2.7, 0.04)
	spinner(b, W(-18.9, 0, 46.6), 0.3, 1.5, 0.42, "gb_knick")
	# --- the cash wrap in the north-east corner: an L of candy cases, the register, the oval sign
	showcase(b, W(-13.6, 0, 39.2), Vector3(1, 0, 0), Vector3(0, 0, 1), 2.5, 0.0)
	showcase(b, W(-13.6, 0, za + 0.3), Vector3(0, 0, 1), Vector3(-1, 0, 0), 2.6, 0.4)
	ob(b, -14.25, za, -10.4, 39.85)
	var S = "gb_small"
	var ro = W(-11.8, 1.06, 39.3)
	b.cur_color = Color("#d9d2bf")
	b.box(S, "vcolor", ro + Vector3(0, 0.05, 0.2), Vector3(0.42, 0.1, 0.4), Transform3D.IDENTITY, ["-y"], true)
	b.box(S, "vcolor", ro + Vector3(0, 0.24, 0.12), Vector3(0.3, 0.27, 0.22), Transform3D.IDENTITY, ["-y"], true)
	b.cur_color = Color.WHITE
	# the red oval sign hanging over the candy case (video 2:56)
	oval_sign(b, W(-12.35, 2.35, 39.55))
	# the hall window's T-shirt display and its sale card (video 3:29)
	# (window_hall builds them)
	# --- the corner: the big globe machine, two small ones, a postcard spinner
	globe_machine(b, W(-11.7, 0, 44.4))
	b.box(G, "gb_maroon", W(-14.6, 0.45, 46.95), Vector3(0.7, 0.9, 0.45), Transform3D.IDENTITY, ["-y"])
	small_machine(b, W(-14.78, 0.9, 46.95))
	small_machine(b, W(-14.42, 0.9, 46.95))
	ob(b, -14.95, 46.72, -14.25, 47.18)
	spinner(b, W(-13.1, 0, 45.6), 0.4, 1.7, 0.46, "gb_cards")
	# --- the middle: a low island of novelties and knickknacks, lava lamps on its end
	island(b, W(-16.4, 0, 41.4), rng)
	# a round bin of plush
	b.cyl("gb_fix", "gb_white", W(-13.2, 0, 42.6), 0.42, 0.42, 0.62, 18, false, false)
	b.cyl("gb_fix", "gb_plush", W(-13.2, 0.62, 42.6), 0.42, 0.12, 0.3, 18, true, false)
	ob(b, -13.62, 42.18, -12.78, 43.02)

## The low white island down the middle: two bays each side (boxed novelties on the low
## shelves, knickknacks on the top shelf) and an end cap of lava lamps toward the court.
static func island(b, o, rng):
	var G = "gb_fix"
	var ln = 2.44
	var dp = 0.5
	b.box(G, "gb_white", o + Vector3(0, 0.08, ln * 0.5), Vector3(dp * 2 + 0.06, 0.16, ln), Transform3D.IDENTITY, ["-y"])
	b.box(G, "gb_white", o + Vector3(0, 0.8, ln * 0.5), Vector3(0.06, 1.3, ln), Transform3D.IDENTITY, ["-y"])
	for sd in [-1.0, 1.0]:
		var f = Vector3(sd, 0, 0)
		var r = Vector3(0, 0, -sd)
		var oo = o + Vector3(0.03 * sd, 0, ln * 0.5) - r * (ln * 0.5)
		for y in [0.55, 1.0, 1.45]:
			lbox(b, G, "gb_white", oo, r, f, 0.0, y - 0.025, 0.0, ln, 0.025, dp, ["-z"])
		fq(b, G, "gb_boxes", oo, r, f, 0.0, ln, 0.16, 0.54, 0.3, 0.0, 0.0, 1.0, 0.5)
		fq(b, G, "gb_boxes", oo, r, f, 0.0, ln, 0.555, 0.98, 0.25, 0.0, 0.5, 1.0, 1.0)
		fq(b, G, "gb_knick", oo, r, f, 0.0, ln, 1.0, 1.44, 0.2, 0.0, 0.0, 1.0, 0.5)
		fq(b, G, "gb_knick", oo, r, f, 0.0, ln, 1.45, 1.89, 0.2, 0.0, 0.5, 1.0, 1.0)
	# the end cap toward the court entrance: three steps of lava lamps, glowing
	var ec = o + Vector3(0, 0, ln)
	b.box(G, "gb_white", ec + Vector3(0, 0.35, 0.2), Vector3(1.06, 0.7, 0.4), Transform3D.IDENTITY, ["-y"])
	b.box(G, "gb_white", ec + Vector3(0, 0.85, 0.12), Vector3(1.06, 0.3, 0.24), Transform3D.IDENTITY, ["-y"])
	var cols = ["red", "blue", "green", "purple", "orange", "pink"]
	for k in 4:
		lava(b, ec + Vector3(-0.39 + k * 0.26, 0.7, 0.3), cols[k], 1.0)
	for k in 3:
		lava(b, ec + Vector3(-0.3 + k * 0.3, 1.0, 0.12), cols[(k + 4) % 6], 1.1)
	ob(b, o.x - dp - 0.03, o.z, o.x + dp + 0.03, o.z + ln + 0.4)

## The red oval sign, both faces, hung on two wires.
static func oval_sign(b, c):
	var G = "gb_small"
	var w = 1.2
	var h = 0.6
	var seg = 28
	for s in [1.0, -1.0]:
		var nn = Vector3(0, 0, s)
		var rv = (-nn).cross(UP)
		var st = b.st(G, "gb_oval", true)
		for i in seg:
			var a0 = TAU * i / seg
			var a1 = TAU * (i + 1) / seg
			var p0 = c + nn * 0.01 + rv * (cos(a0) * w * 0.5) + UP * (sin(a0) * h * 0.5)
			var p1 = c + nn * 0.01 + rv * (cos(a1) * w * 0.5) + UP * (sin(a1) * h * 0.5)
			b.tri(st, c + nn * 0.01, p0, p1, Vector2(0.5, 0.5), Vector2(0.5 + cos(a0) * 0.5, 0.5 - sin(a0) * 0.5), Vector2(0.5 + cos(a1) * 0.5, 0.5 - sin(a1) * 0.5), nn)
	b.cur_color = Color("#c8c8c8")
	for s in [-0.35, 0.35]:
		b.box(G, "vcolor", c + Vector3(s, (CEIL - c.y) * 0.5 + 0.15, 0), Vector3(0.006, CEIL - c.y - 0.3, 0.006), Transform3D.IDENTITY, [], true)
	b.cur_color = Color.WHITE

## The hall window: a riser with T-shirts on display boards and the sale card (video 3:29).
static func window_hall(b):
	var G = "gb_fix"
	b.box(G, "gb_white", W(X1 - 0.5, SILL * 0.5, (Z0 + HALL_OPEN) * 0.5), Vector3(0.6, SILL, HALL_OPEN - Z0 - 0.5), Transform3D.IDENTITY, ["-y"])
	for k in 3:
		var z = 37.0 + k * 1.05
		# a shirt on a board, a little turned, on a stand
		fq(b, G, "gb_tees", W(X1 - 0.45, 0, z + 0.3), Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, 0.6, SILL + 0.6, SILL + 1.35, 0.0, k * 0.142, 0.0, k * 0.142 + 0.142, 0.2)
		b.cur_color = Color("#3a3a3e")
		b.box("gb_small", "vcolor", W(X1 - 0.47, SILL + 0.3, z), Vector3(0.02, 0.6, 0.02), Transform3D.IDENTITY, [], true)
		b.cur_color = Color.WHITE
	fq(b, G, "gb_sale", W(X1 - 0.3, 0, 39.75), Vector3(0, 0, -1), Vector3(1, 0, 0), 0.0, 0.4, SILL + 0.05, SILL + 0.65, 0.0)
	# a row of lava lamps along the front of the riser
	var cols = ["red", "blue", "green", "orange"]
	for k in 4:
		lava(b, W(X1 - 0.3, SILL, 36.6 + k * 0.32), cols[k], 0.9)

## The court window: a riser with boxed gifts in a pyramid, plush, a sale card.
static func window_court(b):
	var G = "gb_fix"
	var x0 = X0 + 0.15
	var x1 = COURT_OPEN - PIER - 0.05
	b.box(G, "gb_white", W((x0 + x1) * 0.5, SILL * 0.5, Z1 - 0.5), Vector3(x1 - x0, SILL, 0.6), Transform3D.IDENTITY, ["-y"])
	var o = W(x0 + 0.4, SILL, Z1 - 0.62)
	for row in 3:
		for k in 4 - row:
			var c = o + Vector3(0.35 + row * 0.18 + k * 0.36, row * 0.3, 0)
			b.box(G, "gb_white", c + Vector3(0, 0.15, 0), Vector3(0.34, 0.3, 0.3), Transform3D.IDENTITY, ["-y", "-z"])
			fq(b, G, "gb_boxes", c - Vector3(0.17, 0, -0.151), Vector3(1, 0, 0), Vector3(0, 0, 1), 0.0, 0.34, 0.0, 0.3, 0.0, (k % 4) * 0.25, row * 0.25, (k % 4) * 0.25 + 0.25, row * 0.25 + 0.25)
	fq(b, G, "gb_plush", W(x0 + 2.3, SILL, Z1 - 0.5), Vector3(1, 0, 0), Vector3(0, 0, 1), 0.0, 1.6, 0.0, 0.42, 0.0, 0.2, 0.18, 0.7, 1.0)
	var cols = ["purple", "red", "blue"]
	for k in 3:
		lava(b, W(x0 + 3.2 + k * 0.3, SILL, Z1 - 0.32), cols[k], 0.9)

# ------------------------------------------------------------------ materials
## "gb_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	if key.begins_with("lava_"):
		var c = {"red": "#ff3a20", "blue": "#3a8cff", "green": "#4cff5a", "purple": "#c04cff", "orange": "#ff9a1a", "pink": "#ff5ab4"}[key.substr(5)]
		m.albedo_texture = b.tex("gb/lava.png"); m.albedo_color = Color(c)
		m.emission_enabled = true; m.emission_texture = m.albedo_texture
		m.emission = Color(c); m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
		m.emission_energy_multiplier = 2.2
		m.set_meta("e_day", 2.0); m.set_meta("e_night", 2.4)
		m.roughness = 0.15; m.metallic_specular = 0.8
		return true
	if key.begins_with("ball"):
		var cols = ["#d8202a", "#f6c41c", "#22a03a", "#2450d0", "#f37a1a", "#8a3cc0", "#f070a8", "#f4f2ea"]
		m.albedo_color = Color(cols[int(key.substr(4)) % cols.size()]); m.roughness = 0.25; m.metallic_specular = 0.6
		return true
	match key:
		"fascia":
			# the white fascia reads bright under the mall's light (video): a touch of glow
			m.albedo_color = Color("#f2f2ee"); m.roughness = 0.35; m.metallic_specular = 0.5
			m.emission_enabled = true; m.emission = Color("#f4f4f0"); m.emission_energy_multiplier = 0.12
			m.set_meta("e_day", 0.08); m.set_meta("e_night", 0.14)
		"grey":
			m.albedo_color = Color("#9a9ca0"); m.roughness = 0.6
		"soffit":
			m.albedo_color = Color("#ecece8"); m.roughness = 0.9
		"can":
			m.albedo_color = Color("#fff4e0")
			m.emission_enabled = true; m.emission = Color("#ffe8c8"); m.emission_energy_multiplier = 8.0
			m.set_meta("e_day", 8.0); m.set_meta("e_night", 8.0)
		"logo":
			# glossy cobalt acrylic (video): bright blue faces with a hard sheen
			m.albedo_color = Color("#2a34d8"); m.roughness = 0.12; m.metallic_specular = 0.9
			m.emission_enabled = true; m.emission = Color("#2430c8"); m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.5)
		"logoside":
			m.albedo_color = Color("#141a6a"); m.roughness = 0.2; m.metallic_specular = 0.7
			m.emission_enabled = true; m.emission = Color("#121860"); m.emission_energy_multiplier = 0.2
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.2)
		"plaque":
			m.albedo_texture = b.tex("gb/plaque.png"); m.roughness = 0.2; m.metallic_specular = 0.7
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.4)
		"plaqueedge":
			m.albedo_color = Color("#1c2690"); m.roughness = 0.3
		"wall":
			m.albedo_color = Color("#eeeeea"); m.roughness = 0.9
		"white":
			m.albedo_color = Color("#f2f2ee"); m.roughness = 0.4; m.metallic_specular = 0.4
		"floor":
			m.albedo_texture = b.tex("gb/floor.png"); m.roughness = 0.3; m.metallic_specular = 0.5
		"troffer":
			m.albedo_texture = b.tex("kb/troffer.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 1.8
			m.set_meta("e_day", 1.8); m.set_meta("e_night", 1.8)
		"bins":
			m.albedo_texture = b.tex("gb/bins.png"); m.roughness = 0.15; m.metallic_specular = 0.7
		"acrylic":
			m.albedo_color = Color("#e4eaee"); m.roughness = 0.1; m.metallic_specular = 0.8
		"plush":
			m.albedo_texture = b.tex("gb/plush.png"); m.roughness = 1.0; m.metallic_specular = 0.0
		"jackets":
			m.albedo_texture = b.tex("gb/jackets.png"); m.roughness = 0.45; m.metallic_specular = 0.5
		"tees":
			m.albedo_texture = b.tex("gb/tees.png"); m.roughness = 0.35; m.metallic_specular = 0.55
		"slat_black":
			m.albedo_texture = b.tex("gb/slat_black.png"); m.roughness = 0.6
		"slat_white":
			m.albedo_texture = b.tex("gb/slat_white.png"); m.roughness = 0.6
		"posters":
			m.albedo_texture = b.tex("gb/posters.png"); m.roughness = 0.3; m.metallic_specular = 0.6
		"cards":
			m.albedo_texture = b.tex("gb/cards.png"); m.roughness = 0.6
		"boxes":
			m.albedo_texture = b.tex("gb/boxes.png"); m.roughness = 0.5
		"knick":
			m.albedo_texture = b.tex("gb/knick.png"); m.roughness = 0.5
		"showcase":
			m.albedo_texture = b.tex("gb/showcase.png"); m.roughness = 0.5
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.25)
		"counter":
			m.albedo_color = Color("#f4f2ec"); m.roughness = 0.25; m.metallic_specular = 0.55
		"oval":
			m.albedo_texture = b.tex("gb/oval.png"); m.roughness = 0.4
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.3)
		"snacks":
			m.albedo_texture = b.tex("gb/snacks.png"); m.roughness = 0.5
		"blue":
			m.albedo_color = Color("#1e46be"); m.roughness = 0.5
		"sale":
			m.albedo_texture = b.tex("gb/sale.png"); m.roughness = 0.6
		"maroon":
			m.albedo_color = Color("#6a1820"); m.roughness = 0.35; m.metallic_specular = 0.55
		"red":
			m.albedo_color = Color("#c81c24"); m.roughness = 0.3; m.metallic_specular = 0.6
		"chrome":
			m.albedo_color = Color("#d8dadc"); m.metallic = 0.85; m.roughness = 0.15
		"gumballs":
			# seen through the glass, lit from all round: a little glow of their own
			m.albedo_texture = b.tex("gb/gumballs.png"); m.roughness = 0.3; m.metallic_specular = 0.6
			m.uv1_scale = Vector3(1.5, 1.5, 1.0)
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.45); m.set_meta("e_night", 0.45)
		"globe":
			m.albedo_color = Color(0.92, 0.96, 1.0, 0.16); m.roughness = 0.03; m.metallic_specular = 1.0
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_:
			return false
	return true
