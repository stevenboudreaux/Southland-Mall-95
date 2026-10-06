## Kay-Bee Toys (store s18), on the Sears-side hall, built to
## design/storefronts/kay-bee-toys.md.
##
## The front follows Steven's photo of the Southland store: white wall tile with
## scattered red and blue accent tiles, a royal-blue fascia with red channel letters
## ("KAY·BEE TOYS"), a lit slatted ceiling just inside the open front, a blue pier and a
## small show window on the left, and a blue pedestal with a red ball on the right.
##
## Inside follows the 1993 home video of a Kay-Bee (Columbus, Georgia) that Steven chose:
## tan carpet, white lay-in ceiling with fluorescent troffers, white shelving packed to
## the ceiling along both walls, low gondolas and stack-outs down the middle, teal
## department boards with lime lettering, orange price cards, and the cash wrap with the
## video game case behind it. The layout is the video's mirrored: Steven remembers the
## checkout on the left as you walk in. All package art is original (paint_store.py).
##
## Frame: u runs along the frontage from the edge's start `a` (z = -58, the viewer's
## right; Sound Shop beyond it) to Miller's Outpost's side (u = 6). d runs into the store
## (-x), and d < 0 is out in the hall. y is up.

const UNIT = 6.0
const DEPTH = 24.0
const SIDE = 0.12       # party walls' inner faces from the unit edges
const HEAD = 2.6        # top of the opening = bottom of the fascia (photo: ~1.5 x a shopper)
const FTOP = 3.4        # top of the fascia
const PROUD = 0.25      # the fascia stands out over the hall
const PIER0 = 4.7       # the blue pier left of the opening (viewer's left = high u)
const PIER1 = 5.0
const VEST = 1.5        # the lit slatted ceiling runs this far in
const CEIL = 3.2
const TEXT_W = 4.276    # letters.json width
const TEXT_Y = 2.80
const LETTER_D = 0.10
const SH_D = 0.40       # shelf depth
const BAY = 1.22        # 4 ft gondola bay
const UP = Vector3.UP
const DEPT_NAMES = ["DOLLS", "VIDEO", "GAMES", "VEHICLES", "STUFFED TOYS", "ACTION TOYS", "PRESCHOOL", "SPORTS"]   # paint_store.py DEPTS

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 1993
	front(b, "kbf_props", a, t, n)
	letters(b, "kbf_props", a, t, n)
	room(b, "kb_shell", a, t, n)
	fixtures(b, a, t, n, rng)
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, UNIT * 0.5, CEIL * 0.5, DEPTH * 0.5)
	rp.size = (t * UNIT + n * DEPTH).abs() + Vector3(0.1, CEIL + 0.1, 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ local-frame helpers
## A fixture's frame: `o` on the floor, `r` along its width, `f` out toward the shopper.
static func L(o, r, f, x, y, z):
	return o + r * x + UP * y + f * z

## A quad facing `f` at depth z, x0..x1 by y0..y1, showing the texture rectangle
## (ua, va)-(ub, vb) the right way round for someone looking at it.
static func fq(b, g, m, o, r, f, x0, x1, y0, y1, z, ua = 0.0, va = 0.0, ub = 1.0, vb = 1.0, dyn = false):
	if r.dot((-f).cross(UP)) < 0.0:
		var tmp = ua; ua = ub; ub = tmp
	b.quad(g, m, [L(o, r, f, x0, y0, z), L(o, r, f, x1, y0, z), L(o, r, f, x1, y1, z), L(o, r, f, x0, y1, z)], f,
		[Vector2(ua, vb), Vector2(ub, vb), Vector2(ub, va), Vector2(ua, va)], dyn)

## A box given by its local min corner and size.
static func lbox(b, g, m, o, r, f, x, y, z, w, h, dp, skip = [], dyn = false):
	var xf = Transform3D(Basis(r, UP, f), o)
	b.box(g, m, Vector3(x + w * 0.5, y + h * 0.5, z + dp * 0.5), Vector3(w, h, dp), xf, skip, dyn)

## A horizontal quad (facing up or down) in the local frame.
static func hq(b, g, m, o, r, f, x0, x1, z0, z1, y, up = true, dyn = false):
	b.quad(g, m, [L(o, r, f, x0, y, z0), L(o, r, f, x1, y, z0), L(o, r, f, x1, y, z1), L(o, r, f, x0, y, z1)], UP if up else Vector3.DOWN, [], dyn)

## A side quad (facing +r or -r) at local x, from z0..z1 and y0..y1.
static func sq(b, g, m, o, r, f, x, z0, z1, y0, y1, sign, dyn = false):
	b.quad(g, m, [L(o, r, f, x, y0, z0), L(o, r, f, x, y0, z1), L(o, r, f, x, y1, z1), L(o, r, f, x, y1, z0)], r * sign, [], dyn)

static func ob(b, p0, p1, pad = 0.12):
	b.obst(["rect", min(p0.x, p1.x) - pad, min(p0.z, p1.z) - pad, max(p0.x, p1.x) + pad, max(p0.z, p1.z) + pad])

# ------------------------------------------------------------------ the front
static func front(b, g, a, t, n):
	var LH = b.LANE_H
	var o = P(a, t, n, 0, 0, 0)
	# white tile with red and blue accents over the fascia: one painted panel across the unit
	b.quad(g, "kb_tile", [P(a, t, n, 0, FTOP, 0), P(a, t, n, UNIT, FTOP, 0), P(a, t, n, UNIT, LH, 0), P(a, t, n, 0, LH, 0)], n,
		[Vector2(1, 1), Vector2(0, 1), Vector2(0, 0), Vector2(1, 0)])
	# the royal-blue fascia, standing out over the hall
	lbox(b, g, "kb_blue", o, t, n, 0.0, HEAD, 0.0, UNIT, FTOP - HEAD, PROUD, ["-z"])
	# the left pier, the show window's bulkhead and end post (viewer's left = high u)
	lbox(b, g, "kb_blue", o, t, n, PIER0, 0.0, -0.3, PIER1 - PIER0, HEAD, 0.3 + 0.06, ["-y", "+y"])
	lbox(b, g, "kb_blue", o, t, n, PIER1, 0.0, -0.3, UNIT - PIER1, 0.5, 0.3, ["-y"])
	lbox(b, g, "kb_blue", o, t, n, UNIT - 0.12, 0.5, -0.3, 0.12, HEAD - 0.5, 0.3, ["-y", "+y"])
	b.quad("glass", "glass", [P(a, t, n, PIER1, 0.5, 0.02), P(a, t, n, UNIT - 0.12, 0.5, 0.02), P(a, t, n, UNIT - 0.12, HEAD, 0.02), P(a, t, n, PIER1, HEAD, 0.02)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# the blue pedestal with the red ball, standing in the right of the opening
	lbox(b, g, "kb_blue", o, t, n, 0.1, 0.0, -0.45, 0.6, 1.85, 0.6, ["-y"])
	ball(b, g, P(a, t, n, 0.4, 1.85 + 0.21, 0.15), 0.22)
	# the lit slatted ceiling just inside (the bright band under the fascia in the photo)
	var lq = [P(a, t, n, SIDE, HEAD + 0.02, 0.0), P(a, t, n, UNIT - SIDE, HEAD + 0.02, 0.0), P(a, t, n, UNIT - SIDE, HEAD + 0.02, VEST), P(a, t, n, SIDE, HEAD + 0.02, VEST)]
	var luv = []
	for u in [SIDE, UNIT - SIDE, UNIT - SIDE, SIDE]:
		luv.append(Vector2(u / 0.6, 0))
	luv[2].y = VEST / 0.6; luv[3].y = VEST / 0.6
	b.quad(g, "kb_louver", lq, Vector3.DOWN, luv)
	# obstacles: the pedestal, the pier and the window (with its display behind)
	ob(b, P(a, t, n, 0.1, 0, -0.15), P(a, t, n, 0.7, 0, 0.45), 0.2)
	ob(b, P(a, t, n, PIER0, 0, -0.06), P(a, t, n, UNIT, 0, 0.3), 0.2)

## The red ball: stacked rings.
static func ball(b, g, c, rad):
	var seg = 10
	for k in seg:
		var a0 = -PI * 0.5 + PI * k / seg
		var a1 = -PI * 0.5 + PI * (k + 1) / seg
		b.cyl(g, "kb_ball", c + Vector3(0, sin(a0) * rad, 0), max(cos(a0) * rad, 0.001), max(cos(a1) * rad, 0.001), (sin(a1) - sin(a0)) * rad, 20, false, false)

## "KAY·BEE TOYS": red lit channel letters (letters.json outlines) on the fascia.
static func letters(b, g, a, t, n):
	var J = JSON.parse_string(FileAccess.get_file_as_string("res://tools/stores/kay_bee/letters.json"))
	var u_start = UNIT * 0.5 + TEXT_W * 0.5
	var d_back = -PROUD
	var d_face = d_back - LETTER_D
	var X = func(p, d): return P(a, t, n, u_start - float(p[0]), TEXT_Y + float(p[1]), d)
	for Lt in J.letters:
		var tr = Lt.tris
		var s = b.st(g, "kb_letterface", true)
		for i in range(0, tr.size(), 3):
			b.tri(s, X.call(tr[i], d_face), X.call(tr[i + 1], d_face), X.call(tr[i + 2], d_face), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), n)
		for lp in Lt.loops:
			for i in lp.size():
				var q0 = lp[i]
				var q1 = lp[(i + 1) % lp.size()]
				var dx = float(q1[0]) - float(q0[0])
				var dy = float(q1[1]) - float(q0[1])
				var ln = sqrt(dx * dx + dy * dy)
				if ln < 1e-5:
					continue
				var nn = (-t * (dy / ln) + UP * (-dx / ln)).normalized()
				b.quad(g, "kb_letterside", [X.call(q0, d_back), X.call(q1, d_back), X.call(q1, d_face), X.call(q0, d_face)], nn,
					[Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)], true)

# ------------------------------------------------------------------ the room
static func room(b, G, a, t, n):
	var u0 = SIDE
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	# tan carpet from the threshold to the back wall
	b.quad(G, "kb_carpet", [P(a, t, n, u0, 0, 0), P(a, t, n, u1, 0, 0), P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB)], UP)
	# white lay-in ceiling (2 x 4 ft) with troffers
	var cq = [[u0, VEST], [u0, dB], [u1, dB], [u1, VEST]]
	var cp = []
	var cuv = []
	for q in cq:
		cp.append(P(a, t, n, q[0], CEIL, q[1]))
		cuv.append(Vector2(q[0] / 0.61, q[1] / 1.22))
	b.quad(G, "kb_ceiling", cp, Vector3.DOWN, cuv)
	var j = 0
	var dd = 2.44
	while dd + 1.22 < dB - 0.5:
		for uu in [1.22, 4.27]:
			var tq = [P(a, t, n, uu, CEIL - 0.006, dd), P(a, t, n, uu + 0.61, CEIL - 0.006, dd), P(a, t, n, uu + 0.61, CEIL - 0.006, dd + 1.22), P(a, t, n, uu, CEIL - 0.006, dd + 1.22)]
			b.quad(G, "kb_troffer", tq, Vector3.DOWN, [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
			if j % 2 == 0:
				var l = b.add_spot(P(a, t, n, uu + 0.3, CEIL - 0.08, dd + 0.61), Vector3.DOWN, 1.4, 6.0, 62.0, Color(1.0, 0.98, 0.92))
				b.tag(l, "", 1.4, 1.4)
		dd += 2.44
		j += 1
	# the step from the low entrance ceiling up to the room's
	b.quad(G, "kb_wall", [P(a, t, n, u0, HEAD + 0.02, VEST), P(a, t, n, u1, HEAD + 0.02, VEST), P(a, t, n, u1, CEIL, VEST), P(a, t, n, u0, CEIL, VEST)], -n)
	# walls: off-white sides (mostly behind shelving), a tan back wall as in the video
	b.quad(G, "kb_wall", [P(a, t, n, u0, 0, 0), P(a, t, n, u0, 0, dB), P(a, t, n, u0, CEIL, dB), P(a, t, n, u0, CEIL, 0)], t)
	b.quad(G, "kb_wall", [P(a, t, n, u1, 0, dB), P(a, t, n, u1, 0, 0), P(a, t, n, u1, CEIL, 0), P(a, t, n, u1, CEIL, dB)], -t)
	b.quad(G, "kb_tan", [P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB), P(a, t, n, u0, CEIL, dB), P(a, t, n, u1, CEIL, dB)], n)
	# inside of the fascia and the window's end
	b.quad(G, "kb_wall", [P(a, t, n, PIER1, 0, 0.06), P(a, t, n, PIER0, 0, 0.06), P(a, t, n, PIER0, HEAD, 0.06), P(a, t, n, PIER1, HEAD, 0.06)], -n)
	# the stockroom door in the back wall, an exit sign over it (video)
	var du = UNIT - 4.55
	b.cur_color = Color("#8c6a44")
	b.box(G, "vcolor", P(a, t, n, du, 1.05, dB - 0.02), b.abs_size(t, 0.95, 2.1, 0.04, n))
	b.cur_color = Color("#c9c9c9")
	b.box(G, "vcolor", P(a, t, n, du - 0.35, 1.0, dB - 0.06), b.abs_size(t, 0.12, 0.04, 0.04, n))
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, du, 2.35, dB - 0.05), b.abs_size(t, 0.36, 0.16, 0.06, n))

# ------------------------------------------------------------------ shelving and stock
## One row of stock on a shelf: two half-bay blocks, each showing half of one painted shelf
## row, stepped back by different amounts. `space` is the clear height above the shelf.
static func stock(b, g, o, r, f, w, y, space, depth, cat, rng, open_top = false, x_off = 0.0):
	for h in 2:
		if rng.randf() < 0.05:
			continue   # a sold-out gap
		var x0 = x_off + h * w * 0.5 + 0.012
		var x1 = x_off + (h + 1) * w * 0.5 - 0.012
		var hgt = min(space, 0.35)
		var z = depth - rng.randf_range(0.015, 0.09)
		var m = "kb_merch_" + cat
		var ua = h * 0.5
		var ub = ua + 0.5
		var va = 0.0
		var vb = 1.0
		if cat == "plush":
			m = "kb_plush"
			ua = rng.randf(); ub = ua + (x1 - x0) / 1.0
			va = rng.randf() * 0.5; vb = va + hgt / 1.0
		else:
			var row = rng.randi_range(0, 6)
			vb = (row + 1) * 146.0 / 1024.0
			va = vb - hgt / 0.35 * 146.0 / 1024.0
			if rng.randf() < 0.5:
				ua = 0.5 - ua; ub = ua + 0.5
		fq(b, g, m, o, r, f, x0, x1, y, y + hgt, z, ua, va, ub, vb)
		sq(b, g, "kb_side", o, r, f, x0, 0.02, z, y, y + hgt, -1.0)
		sq(b, g, "kb_side", o, r, f, x1, 0.02, z, y, y + hgt, 1.0)
		if open_top or hgt < space - 0.03:
			hq(b, g, "kb_side", o, r, f, x0, x1, 0.02, z, y + hgt)

## A shelving bay: pegboard back, kick base, shelf boards, stock. `boards` are the shelf
## heights above the base deck (0.15 m); the top board carries overstock when `over` > 0
## (the height available above it, up to the ceiling).
static func bay(b, g, gm, o, r, f, w, boards, cat, rng, over = 0.0, depth = SH_D):
	var top = boards[boards.size() - 1]
	# back panel
	b.quad(g, "kb_pegboard", [L(o, r, f, 0, 0.15, 0.012), L(o, r, f, w, 0.15, 0.012), L(o, r, f, w, top, 0.012), L(o, r, f, 0, top, 0.012)], f,
		[Vector2(0, 0), Vector2(w / 0.305, 0), Vector2(w / 0.305, (top - 0.15) / 0.305), Vector2(0, (top - 0.15) / 0.305)])
	lbox(b, g, "kb_white", o, r, f, 0.0, 0.0, 0.0, w, 0.15, depth + 0.04, ["-y", "-z"])
	for x in [0.0, w - 0.03]:
		lbox(b, g, "kb_white", o, r, f, x, 0.15, 0.012, 0.03, top - 0.15, 0.035, ["-y", "-z"])
	var levels = [0.15]
	for yb in boards:
		lbox(b, g, "kb_white", o, r, f, 0.0, yb - 0.025, 0.012, w, 0.025, depth - 0.012, ["-z", "+z"])
		fq(b, g, "kb_shelfedge", o, r, f, 0.0, w, yb - 0.035, yb + 0.005, depth + 0.002, 0, 0, 1, 1, true)
		levels.append(yb)
	fq(b, g, "kb_shelfedge", o, r, f, 0.0, w, 0.11, 0.15, depth + 0.042, 0, 0, 1, 1, true)
	for i in levels.size():
		var y = levels[i]
		if i < levels.size() - 1:
			stock(b, gm, o, r, f, w, y, levels[i + 1] - 0.025 - y - 0.01, depth, cat, rng)
		elif over > 0.3:
			# overstock to the ceiling: more of the same line, or shipping cartons
			var yy = y
			while yy + 0.3 < y + over:
				if rng.randf() < 0.35:
					var z = depth - rng.randf_range(0.02, 0.08)
					var x0 = rng.randf_range(0.0, 0.1)
					var x1 = w - rng.randf_range(0.0, 0.25)
					var u0 = rng.randf() * 0.3
					fq(b, gm, "kb_carton", o, r, f, x0, x1, yy, yy + 0.3, z, u0, 0.0, u0 + (x1 - x0) / 1.22, 0.5)
					sq(b, gm, "kb_kraft", o, r, f, x0, 0.02, z, yy, yy + 0.3, -1.0)
					sq(b, gm, "kb_kraft", o, r, f, x1, 0.02, z, yy, yy + 0.3, 1.0)
					hq(b, gm, "kb_kraft", o, r, f, x0, x1, 0.02, z, yy + 0.3)
					yy += 0.3
				else:
					stock(b, gm, o, r, f, w, yy, 0.35, depth, cat, rng, true)
					yy += 0.35
		elif over < 0.0:
			# a low gondola's top: stock standing in the open
			stock(b, gm, o, r, f, w, y, 0.35, depth, cat, rng, true)

## A run of wall bays from d0 along a side wall. `cats` gives each bay's department.
static func wall_run(b, a, t, n, wall_u, facing, d0, cats, rng):
	var d = d0
	for k in cats.size():
		var o = P(a, t, n, wall_u, 0, d)
		bay(b, "kb_fix", "kb%d_merch" % int(clamp(d / 8.0, 0, 2)), o, -n, facing, BAY, [0.55, 0.95, 1.35, 1.75, 2.15], cats[k], rng, CEIL - 2.15 - 0.12)
		d += BAY
	var p0 = P(a, t, n, wall_u, 0, d0)
	var p1 = P(a, t, n, wall_u, 0, d) + facing * (SH_D + 0.05)
	ob(b, p0, p1)
	return d

## A low double-sided gondola down the middle from d0, with an end cap at each end.
static func gondola(b, a, t, n, uc, d0, cats_a, cats_b, cap0, cap1, rng):
	var boards = [0.50, 0.85, 1.20]
	var d = d0
	for k in cats_a.size():
		var gm = "kb%d_merch" % int(clamp(d / 8.0, 0, 2))
		bay(b, "kb_fix", gm, P(a, t, n, uc, 0, d), -n, t, BAY, boards, cats_a[k], rng, -1.0)
		bay(b, "kb_fix", gm, P(a, t, n, uc, 0, d), -n, -t, BAY, boards, cats_b[k], rng, -1.0)
		d += BAY
	var w = SH_D * 2 + 0.08
	var gm0 = "kb%d_merch" % int(clamp(d0 / 8.0, 0, 2))
	bay(b, "kb_fix", gm0, P(a, t, n, uc - w * 0.5, 0, d0), t, n, w, boards, cap0, rng, -1.0, 0.32)
	bay(b, "kb_fix", gm0, P(a, t, n, uc - w * 0.5, 0, d), t, -n, w, boards, cap1, rng, -1.0, 0.32)
	ob(b, P(a, t, n, uc - w * 0.5, 0, d0 - 0.36), P(a, t, n, uc + w * 0.5, 0, d + 0.36))

## A stack-out: cartons of one item piled on the floor, with an orange price card on a stem.
static func stack(b, a, t, n, u, d, w, dp, layers, cat, card, rng):
	var gm = "kb%d_merch" % int(clamp(d / 8.0, 0, 2))
	var lh = 0.3
	var row = rng.randi_range(0, 6)
	for k in layers:
		var jx = rng.randf_range(-0.02, 0.02)
		var jz = rng.randf_range(-0.02, 0.02)
		var c = P(a, t, n, u + jx, 0, d + jz)
		var vb = (row + 1) * 146.0 / 1024.0
		var va = vb - lh / 0.35 * 146.0 / 1024.0
		# four printed faces
		var faces = [[c - t * w * 0.5 + n * dp * 0.5, t, n, w], [c + t * w * 0.5 - n * dp * 0.5, -t, -n, w], [c + t * w * 0.5 + n * dp * 0.5, -n, t, dp], [c - t * w * 0.5 - n * dp * 0.5, n, -t, dp]]
		for F in faces:
			var uw = min(F[3] / 1.22, 1.0)
			fq(b, gm, "kb_merch_" + cat, F[0], F[1], F[2], 0.0, F[3], k * lh, (k + 1) * lh, 0.0, 0.0, va, uw, vb)
		if k == layers - 1:
			b.quad(gm, "kb_kraft", [c - t * w * 0.5 - n * dp * 0.5 + UP * (layers * lh), c + t * w * 0.5 - n * dp * 0.5 + UP * (layers * lh), c + t * w * 0.5 + n * dp * 0.5 + UP * (layers * lh), c - t * w * 0.5 + n * dp * 0.5 + UP * (layers * lh)], UP)
	var top = layers * lh
	if card >= 0:
		var cc = P(a, t, n, u, top, d)
		b.cur_color = Color("#d8d8d4")
		b.box("kb_small", "vcolor", cc + Vector3(0, 0.12, 0), Vector3(0.015, 0.24, 0.015), Transform3D.IDENTITY)
		b.cur_color = Color.WHITE
		for s in [1.0, -1.0]:
			fq(b, "kb_small", "kb_cards", cc + n * 0.012 * s - t * 0.17 * s, t * s, n * s, 0.03, 0.31, 0.24, 0.52, 0.0, card * 0.5, 0.0, card * 0.5 + 0.5, 0.5)
	ob(b, P(a, t, n, u - w * 0.5, 0, d - dp * 0.5), P(a, t, n, u + w * 0.5, 0, d + dp * 0.5), 0.15)
	return top

## A rolling wire dump bin heaped with soft toys.
static func bin(b, a, t, n, u, d, rng):
	var o = P(a, t, n, u - 0.45, 0, d - 0.3)
	var G = "kb_small"
	for cx in [0.04, 0.86]:
		for cz in [0.04, 0.56]:
			b.cur_color = Color("#2a2a2c")
			b.cyl(G, "vcolor", L(o, t, -n, cx, 0.0, cz), 0.035, 0.035, 0.07, 8, true, false, true)
	b.cur_color = Color.WHITE
	lbox(b, "kb_fix", "kb_white", o, t, -n, 0.0, 0.08, 0.0, 0.9, 0.03, 0.6, ["-y"])
	# wire sides
	var uvw = 0.9 / 0.15
	for F in [[o, t, n, 0.9], [o + t * 0.9 - n * 0.6, -t, -n, 0.9], [o + t * 0.9, -n, t, 0.6], [o - n * 0.6, n, -t, 0.6]]:
		b.quad(G, "kb_wire", [F[0] + UP * 0.11, F[0] + F[1] * F[3] + UP * 0.11, F[0] + F[1] * F[3] + UP * 0.78, F[0] + UP * 0.78], F[2],
			[Vector2(0, 0.67 / 0.15), Vector2(F[3] / 0.15, 0.67 / 0.15), Vector2(F[3] / 0.15, 0), Vector2(0, 0)], true)
	# the heap: a low mound of four slopes with a flat top
	var y0 = 0.62
	var y1 = 0.92
	var c0 = [L(o, t, -n, 0.02, y0, 0.02), L(o, t, -n, 0.88, y0, 0.02), L(o, t, -n, 0.88, y0, 0.58), L(o, t, -n, 0.02, y0, 0.58)]
	var c1 = [L(o, t, -n, 0.25, y1, 0.18), L(o, t, -n, 0.65, y1, 0.18), L(o, t, -n, 0.65, y1, 0.42), L(o, t, -n, 0.25, y1, 0.42)]
	var uo = rng.randf()
	b.quad("kb_fix", "kb_plush", c1, UP, [Vector2(uo + 0.25, 0.2), Vector2(uo + 0.65, 0.2), Vector2(uo + 0.65, 0.5), Vector2(uo + 0.25, 0.5)])
	for k in 4:
		var k2 = (k + 1) % 4
		var nn = ((c0[k2] - c0[k]).cross(c1[k] - c0[k])).normalized()
		if nn.y < 0:
			nn = -nn
		b.quad("kb_fix", "kb_plush", [c0[k], c0[k2], c1[k2], c1[k]], nn, [Vector2(uo + k * 0.25, 0.9), Vector2(uo + k * 0.25 + 0.6, 0.9), Vector2(uo + k * 0.25 + 0.45, 0.55), Vector2(uo + k * 0.25 + 0.15, 0.55)])
	ob(b, P(a, t, n, u - 0.45, 0, d - 0.3), P(a, t, n, u + 0.45, 0, d + 0.3), 0.15)

## A toy castle standing on a stack by the door (video): pale walls, two towers, pink roofs.
static func castle(b, c, t, n):
	var G = "kb_small"
	b.cur_color = Color("#e9e6ee")
	b.box(G, "vcolor_matte", c + Vector3(0, 0.2, 0), b.abs_size(t, 0.56, 0.4, 0.34, n), Transform3D.IDENTITY, ["-y"])
	for s in [-1.0, 1.0]:
		b.cur_color = Color("#e9e6ee")
		b.cyl(G, "vcolor_matte", c + t * 0.3 * s, 0.1, 0.1, 0.62, 12, false, false)
		b.cur_color = Color("#e48ac0")
		b.cyl(G, "vcolor_matte", c + t * 0.3 * s + Vector3(0, 0.62, 0), 0.13, 0.002, 0.26, 12, false, true)
	b.cur_color = Color("#e48ac0")
	b.cyl(G, "vcolor_matte", c + Vector3(0, 0.4, 0), 0.2, 0.002, 0.3, 12, false, true)
	b.cur_color = Color("#8fb4e6")
	b.box(G, "vcolor_matte", c + n * 0.172 + Vector3(0, 0.13, 0), b.abs_size(t, 0.16, 0.26, 0.004, n), Transform3D.IDENTITY, [])
	b.cur_color = Color.WHITE

## A hanging department board (dept_signs.png row `k`), across the aisle, readable from both sides.
static func dept(b, a, t, n, u, d, k):
	var G = "kb_fix"
	var w = 1.5
	var h = 0.375
	var y0 = 2.56
	var c = P(a, t, n, u, 0, d)
	var faces = []
	for s in [1.0, -1.0]:
		fq(b, G, "kb_dept", c + n * 0.012 * s - t * w * 0.5 * s, t * s, n * s, 0.0, w, y0, y0 + h, 0.0, 0.0, k / 8.0, 1.0, (k + 1) / 8.0)
		# the same face for the owner-editable text (scripts/signs.gd): left to right as read
		var o = c + n * 0.012 * s - t * w * 0.5 * s
		var r = t * s
		var f = n * s
		var ua = 0.0
		var ub = 1.0
		if r.dot((-f).cross(UP)) < 0.0:
			# fq mirrors the u range for this side; keep the text running along the reading direction
			o = o + r * w
			r = -r
		faces.append([[L(o, r, f, 0.0, y0, 0.0), L(o, r, f, w, y0, 0.0), L(o, r, f, w, y0 + h, 0.0), L(o, r, f, 0.0, y0 + h, 0.0)],
			[Vector2(ua, 1.0), Vector2(ub, 1.0), Vector2(ub, 0.0), Vector2(ua, 0.0)], f])
	if "signs" in b:
		var j = 0
		for rr in b.signs:
			if rr.kind == "kb_dept":
				j += 1
		b.sign_add("kb.dept.%d" % (j + 1), "kb_dept", DEPT_NAMES[k], k, faces)
	b.cur_color = Color("#c8c8c8")
	for s in [-0.6, 0.6]:
		b.box("kb_small", "vcolor", c + t * s + Vector3(0, (y0 + h + CEIL) * 0.5, 0), Vector3(0.006, CEIL - y0 - h, 0.006), Transform3D.IDENTITY, [], true)
	b.cur_color = Color.WHITE

## The cash wrap on the left by the door (the caller mirrors the frame), the register, and the video game case behind it.
static func cash_wrap(b, a, t, n, rng):
	var G = "kb_fix"
	# the counter: its front faces the aisle (+u)
	var o = P(a, t, n, 0.95, 0, 4.4)
	var r = n          # toward the hall, so the front reads left to right from the aisle
	lbox(b, G, "kb_laminate", o, r, t, 0.0, 0.0, 0.0, 2.4, 0.95, 0.6, ["-y", "+z"])
	fq(b, G, "kb_counter", o, r, t, 0.0, 2.4, 0.0, 0.95, 0.6)
	# the register: beige base, a small monitor, a keyboard
	var S = "kb_small"
	var ro = L(o, r, t, 0.5, 0.95, 0.08)
	b.cur_color = Color("#d9d2bf")
	lbox(b, S, "vcolor", ro, r, t, 0.0, 0.0, 0.0, 0.42, 0.1, 0.4, ["-y"])
	lbox(b, S, "vcolor", ro, r, t, 0.06, 0.1, 0.02, 0.3, 0.27, 0.3, ["-y"])
	b.cur_color = Color("#bdb6a4")
	lbox(b, S, "vcolor", ro, r, t, 0.5, 0.0, 0.1, 0.4, 0.03, 0.18, ["-y"])
	b.cur_color = Color.WHITE
	# the staff side sees the screen
	fq(b, S, "kb_screen", ro + r * 0.36 + t * 0.018, -r, -t, 0.03, 0.27, 0.13, 0.34, 0.0, 0.5, 0.0, 1.0, 1.0)
	# bags and a charity can stand in for counter clutter
	b.cur_color = Color("#f4f2ec")
	lbox(b, S, "vcolor_matte", o, r, t, 1.7, 0.95, 0.15, 0.3, 0.02, 0.36, ["-y"])
	b.cur_color = Color.WHITE
	ob(b, P(a, t, n, SIDE, 0, 1.9), P(a, t, n, 1.55, 0, 4.5))
	# the video game case on the wall behind: tan cabinet, a demo TV, locked glass shelves
	var co = P(a, t, n, SIDE, 0, 2.0)
	var cr = -n
	b.cur_color = Color("#c9a26a")
	lbox(b, G, "vcolor_matte", co, cr, t, 0.0, 0.0, 0.0, 2.44, 0.75, 0.42, ["-y", "-z"])
	lbox(b, G, "vcolor_matte", co, cr, t, 0.0, 0.75, 0.0, 2.44, 1.55, 0.06, ["-y", "-z"])
	lbox(b, G, "vcolor_matte", co, cr, t, 0.0, 2.3, 0.0, 2.44, 0.3, 0.42, ["-z"])
	for x in [0.0, 0.8, 1.6, 2.4]:
		lbox(b, G, "vcolor_matte", co, cr, t, x, 0.75, 0.06, 0.04, 1.55, 0.36, ["-y", "+y", "-z"])
	b.cur_color = Color.WHITE
	# the TV in the middle bay
	b.cur_color = Color("#1c1c1e")
	lbox(b, G, "vcolor", co, cr, t, 0.9, 1.45, 0.06, 0.64, 0.52, 0.32, ["-z"])
	b.cur_color = Color.WHITE
	fq(b, G, "kb_screen_tv", co, cr, t, 0.97, 1.47, 1.52, 1.90, 0.385, 0.0, 0.0, 0.5, 1.0)
	# game boxes on glass shelves in the side bays and under the TV
	for bx in [[0.05, 0.8], [1.65, 2.4], [0.85, 1.6]]:
		var ys = [0.78, 1.14, 1.5, 1.86] if bx[0] != 0.85 else [0.78, 1.1]
		for y in ys:
			var row = rng.randi_range(0, 6)
			var vb = (row + 1) * 146.0 / 1024.0
			var hgt = 0.3
			var ua = rng.randf() * 0.35
			fq(b, G, "kb_merch_video", co, cr, t, bx[0], bx[1], y, y + hgt, 0.28, ua, vb - hgt / 0.35 * 146.0 / 1024.0, ua + (bx[1] - bx[0]) / 1.22, vb)
			lbox(b, G, "kb_white", co, cr, t, bx[0], y - 0.02, 0.06, bx[1] - bx[0], 0.02, 0.3, ["-z"])
	b.quad("glass", "glass", [L(co, cr, t, 0.04, 0.75, 0.42), L(co, cr, t, 2.4, 0.75, 0.42), L(co, cr, t, 2.4, 2.3, 0.42), L(co, cr, t, 0.04, 2.3, 0.42)], t,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)

## Everything on the floor, front to back (the video's order where it shows).
static func fixtures(b, a, t, n, rng):
	var uR = SIDE            # the far side wall from the cash wrap (see the mirror below)
	var uL = UNIT - SIDE
	# show window display and the first stack by the door, the castle on top (video)
	var top = stack(b, a, t, n, 5.45, 0.75, 0.8, 0.9, 4, "dolls", -1, rng)
	castle(b, P(a, t, n, 5.45, top, 0.75), t, n)
	stack(b, a, t, n, 3.3, 2.3, 0.9, 0.7, 3, "preschool", 0, rng)
	# stock piled high on both sides of the opening, as in the photo
	stack(b, a, t, n, 4.25, 0.75, 0.7, 0.7, 6, "vehicles", -1, rng)
	stack(b, a, t, n, 1.15, 1.2, 0.7, 0.6, 5, "games", -1, rng)
	# Steven (Oct 6): at Southland the checkout counter was on the LEFT as you walk in, so the
	# room is the video's layout mirrored. From here on u is measured from the left wall.
	a = a + t * UNIT
	t = -t
	cash_wrap(b, a, t, n, rng)
	# the yellow sale signs hanging at the front (photo)
	for s in [[1.5, 0], [2.9, 1], [4.1, 0]]:
		var c = P(a, t, n, s[0], 0, 0.95)
		for sg in [1.0, -1.0]:
			fq(b, "kb_fix", "kb_cards", c + n * 0.008 * sg - t * 0.3 * sg, t * sg, n * sg, 0.0, 0.6, 2.0, 2.6, 0.0, s[1] * 0.5, 0.5, s[1] * 0.5 + 0.5, 1.0)
	# wall shelving
	wall_run(b, a, t, n, uL, -t, 1.7, ["dolls", "dolls", "dolls", "dolls", "dolls", "preschool", "preschool", "preschool", "preschool", "games", "games", "games", "games", "sports", "sports", "sports", "sports"], rng)
	wall_run(b, a, t, n, uR, t, 4.6, ["video", "video", "vehicles", "vehicles", "vehicles", "vehicles", "vehicles", "action", "action", "action", "action", "action", "games", "games", "plush"], rng)
	# two bays of soft toys on the back wall, right of the stockroom door
	var dB = DEPTH - SIDE
	for k in 2:
		bay(b, "kb_fix", "kb2_merch", P(a, t, n, 0.75 + k * BAY, 0, dB), t, n, BAY, [0.55, 0.95, 1.35, 1.75, 2.15], "plush", rng, CEIL - 2.15 - 0.12)
	ob(b, P(a, t, n, 0.75, 0, dB - SH_D - 0.05), P(a, t, n, 0.75 + 2 * BAY, 0, dB))
	# the middle: a bin, a gondola, a stack-out, a second gondola, a bin
	bin(b, a, t, n, 3.0, 5.3, rng)
	gondola(b, a, t, n, 3.0, 7.2, ["preschool", "preschool", "games", "games"], ["vehicles", "vehicles", "action", "action"], "dolls", "games", rng)
	stack(b, a, t, n, 3.0, 13.4, 1.0, 0.8, 4, "action", 1, rng)
	gondola(b, a, t, n, 3.0, 15.0, ["games", "sports", "sports", "sports"], ["action", "action", "vehicles", "video"], "vehicles", "sports", rng)
	bin(b, a, t, n, 3.0, 21.4, rng)
	# department boards (mirrored with the room: VIDEO over the cash wrap on the left, DOLLS on the right)
	for s in [[4.6, 3.0, 0], [1.35, 2.7, 1], [4.6, 8.4, 6], [1.35, 7.6, 3], [4.6, 13.2, 2], [1.35, 13.6, 5], [4.6, 18.4, 7], [2.0, 21.6, 4]]:
		dept(b, a, t, n, s[0], s[1], s[2])

# ------------------------------------------------------------------ materials
## "kb_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	if key.begins_with("merch_"):
		m.albedo_texture = b.tex("kb/" + key + ".png"); m.roughness = 0.5; m.metallic_specular = 0.35
		return true
	match key:
		"tile":
			m.albedo_texture = b.tex("kb/tile_wall.png"); m.roughness = 0.25; m.metallic_specular = 0.55
		"blue":
			m.albedo_color = Color("#1c2f9c"); m.roughness = 0.45; m.metallic_specular = 0.4
		"ball":
			m.albedo_color = Color("#c81e28"); m.roughness = 0.25; m.metallic_specular = 0.6
		"letterface":
			# red acrylic faces lit from inside
			m.albedo_color = Color("#d8202c"); m.roughness = 0.4
			m.emission_enabled = true; m.emission = Color("#ff2a30"); m.emission_energy_multiplier = 1.3
			m.set_meta("e_day", 1.0); m.set_meta("e_night", 1.3)
		"letterside":
			m.albedo_color = Color("#7a1218"); m.roughness = 0.5
			m.emission_enabled = true; m.emission = Color("#8a1a20"); m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.3)
		"louver":
			m.albedo_texture = b.tex("kb/louver.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 1.6
			m.set_meta("e_day", 1.6); m.set_meta("e_night", 1.6)
		"troffer":
			m.albedo_texture = b.tex("kb/troffer.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 2.2
			m.set_meta("e_day", 2.2); m.set_meta("e_night", 2.2)
		"carpet":
			m.albedo_texture = b.tex("kb/carpet.png"); m.roughness = 0.95; m.metallic_specular = 0.1
		"ceiling":
			m.albedo_texture = b.tex("kb/ceiling.png"); m.roughness = 0.95
		"wall":
			m.albedo_color = Color("#e6e2d8"); m.roughness = 0.9
		"tan":
			m.albedo_color = Color("#b98f58"); m.roughness = 0.9
		"white":
			m.albedo_color = Color("#eeede8"); m.roughness = 0.4; m.metallic_specular = 0.4
		"laminate":
			m.albedo_color = Color("#ecebe6"); m.roughness = 0.3; m.metallic_specular = 0.5
		"pegboard":
			m.albedo_texture = b.tex("kb/pegboard.png"); m.roughness = 0.8
		"shelfedge":
			m.albedo_texture = b.tex("kb/shelf_edge.png"); m.roughness = 0.5
		"side":
			m.albedo_color = Color("#4a4640"); m.roughness = 0.8
		"kraft":
			m.albedo_color = Color("#b08c60"); m.roughness = 0.9
		"carton":
			m.albedo_texture = b.tex("kb/carton.png"); m.roughness = 0.9
		"plush":
			m.albedo_texture = b.tex("kb/plush.png"); m.roughness = 1.0; m.metallic_specular = 0.0
		"dept":
			# the boards read bright against the ceiling in the video: a little glow of their own
			m.albedo_texture = b.tex("kb/dept_signs.png"); m.roughness = 0.6
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.35); m.set_meta("e_night", 0.35)
		"cards":
			m.albedo_texture = b.tex("kb/cards.png"); m.roughness = 0.6
		"counter":
			m.albedo_texture = b.tex("kb/counter.png"); m.roughness = 0.35; m.metallic_specular = 0.45
		"screen", "screen_tv":
			m.albedo_texture = b.tex("kb/screens.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture
			m.emission = Color.WHITE; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission_energy_multiplier = 1.5
			m.set_meta("e_day", 1.5); m.set_meta("e_night", 1.5)
		"wire":
			m.albedo_texture = b.tex("kb/wire.png"); m.roughness = 0.4
			# dynamic (alpha) and so probe-lit: a little glow keeps the white wire from going grey
			m.emission_enabled = true; m.emission = Color("#d8d8d2"); m.emission_energy_multiplier = 0.5
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 0.5)
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		_:
			return false
	return true
