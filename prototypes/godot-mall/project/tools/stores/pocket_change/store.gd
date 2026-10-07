## Pocket Change (store s52b), the arcade on the Concourse, built to
## design/storefronts/pocket-change.md.
##
## The front follows Steven's 2009 photo of the Southland store. He says it was unchanged
## from the 1990s:
## - pale blue-green 12-inch glazed tile on the mall wall, stepping down on both sides;
## - two clear glass-block columns;
## - a tiled fascia over the opening with raised silver channel letters;
## - royal-blue returns and a polished head.
##
## Inside is the dark arcade Steven described: the redemption counter on the left, cranes
## by the door, four skee-ball alleys, four basketball games, the sit-in dinosaur ride in
## the middle, and rows of video games, racers and pinball. The machines are prop modules
## in this folder (README.md). This file builds the shell and places them.
## Textures: paint_store.py (shell) and make_letters.py (the letters' outlines).
##
## Frame: u runs along the frontage from the edge's start `a` (x = -110, the viewer's
## right; Blockbuster Music beyond it) to the Chick-fil-A side (u = 8). d runs into the
## store (+z), and d < 0 is out in the hall. y is up.

const UNIT = 8.0
const DEPTH = 40.0
const F0 = 1.5          # fascia ends (it spans both glass columns)
const F1 = 6.5
const COL = 0.2         # glass-block column: one block wide and one deep, standing proud of the wall
const PROUD = 0.2       # how far the columns and the fascia stand out into the hall
const HEAD = 2.9        # top of the opening = bottom of the fascia (raised Oct 7: Steven, "more similar to heights of nearby stores")
const FTOP = 4.3        # top of the fascia (1.4 m; was 1.05 m from the photo)
const TILE = 0.3        # 12-inch tile
const STEPS = [11, 10, 9, 8, 7]   # tile rows in each column, stepping away from the fascia (photo; two rows added Oct 7)
const WALL_T = 0.8      # the front wall with its blue returns (the photo's return runs back ~0.8 m)
const SIDE = 0.15       # party walls' inner faces from the unit edges
const CEIL = 3.6        # black ceiling inside
const TEXT_U0 = 6.3     # the sign starts 0.2 m in from the fascia's left end (viewer's left = high u)
const TEXT_Y = 3.43     # baseline: the caps sit a little above the fascia's middle
const LS = 1.05         # letter scale (Oct 7: a touch bigger with the taller fascia)
const LETTER_OFF = 0.04     # on stand-offs: they throw a shadow on the tile
const LETTER_D = 0.07
const RIGHT_BACK = 3.0  # the right-hand line of machines starts this much further in (Steven, Oct 6)
const CENTRE_U = 3.7    # the centre aisle's line, where the feature games stand
const CYC_D = 2.0       # the cyclone game's front edge, just inside the door (Steven, Oct 6 18:30: a few feet nearer the mall)
const PUSH_D = 7.4      # the coin pusher's middle, behind it, turned lengthwise down the room
const PUSH_U = 3.7      # the pusher's centre line across the room
const BACK_10FT = 3.05  # Steven (Oct 6 18:30): everything from the skee-ball back moves ~10 ft deeper; the claws stay

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var G = "pc_shell"
	# the front gets the finer props texel (its glass blocks and tile steps are small), and
	# the letters are dynamic: too small for clean lightmap texels, the probes light them evenly
	front(b, "pcf_props", a, t, n)
	letters(b, "pcf_props", a, t, n)
	room(b, G, a, t, n)
	lights(b, G, a, t, n)
	machines(b, a, t, n)
	unbake_small(b)
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, UNIT * 0.5, CEIL * 0.5, DEPTH * 0.5)
	rp.size = (t * UNIT + n * DEPTH).abs() + Vector3(0.1, CEIL + 0.1, 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ the front
## A wall-plane quad from u0..u1, y0..y1 at depth d, facing the hall, UVs in metres / `per`.
static func wq(b, g, m, a, t, n, u0, u1, y0, y1, d, per, nn = null):
	var p = [P(a, t, n, u0, y0, d), P(a, t, n, u1, y0, d), P(a, t, n, u1, y1, d), P(a, t, n, u0, y1, d)]
	# u runs right-to-left for the hall viewer, so the texture's x follows -u
	var uv = [Vector2(-u0 / per, -y0 / per), Vector2(-u1 / per, -y0 / per), Vector2(-u1 / per, -y1 / per), Vector2(-u0 / per, -y1 / per)]
	b.quad(g, m, p, n if nn == null else nn, uv)

static func front(b, g, a, t, n):
	var LH = b.LANE_H
	# the mall's own wall over the unit, with the opening cut out
	wq(b, g, "cream", a, t, n, 0.0, F0 + COL, 0.0, LH, 0.0, 1.0)
	wq(b, g, "cream", a, t, n, F1 - COL, UNIT, 0.0, LH, 0.0, 1.0)
	wq(b, g, "cream", a, t, n, F0 + COL, F1 - COL, HEAD, LH, 0.0, 1.0)
	# stepped tile either side, 1 cm proud of the wall
	for k in STEPS.size():
		var h = STEPS[k] * TILE
		wq(b, g, "pc_store_tile", a, t, n, F0 - (k + 1) * TILE, F0 - k * TILE, 0.0, h, -0.01, 1.2)
		wq(b, g, "pc_store_tile", a, t, n, F1 + k * TILE, F1 + (k + 1) * TILE, 0.0, h, -0.01, 1.2)
		# the tile's thin top edge
		for uu in [[F0 - (k + 1) * TILE, F0 - k * TILE], [F1 + k * TILE, F1 + (k + 1) * TILE]]:
			b.quad(g, "pc_store_tile", [P(a, t, n, uu[0], h, -0.01), P(a, t, n, uu[1], h, -0.01), P(a, t, n, uu[1], h, 0), P(a, t, n, uu[0], h, 0)], Vector3.UP)
	# the glass-block columns on tile plinths
	for c0 in [F0, F1 - COL]:
		var pl = 0.15
		var cc = P(a, t, n, c0 + COL * 0.5, pl * 0.5, -PROUD * 0.5)
		b.box(g, "pc_store_tile", cc, b.abs_size(t, COL + 0.1, pl, PROUD + 0.06, n), Transform3D.IDENTITY, ["-y"])
		col_faces(b, g, a, t, n, c0, c0 + COL, pl, HEAD)
	# the fascia: a tiled box standing out over the opening, a polished stainless underside
	var fu = [F0, F1]
	wq(b, g, "pc_store_tile", a, t, n, F0, F1, HEAD, FTOP, -PROUD, 1.2)
	for k in 2:
		var u = fu[k]
		var nn = -t if k == 0 else t
		var p = [P(a, t, n, u, HEAD, -PROUD), P(a, t, n, u, HEAD, 0.0), P(a, t, n, u, FTOP, 0.0), P(a, t, n, u, FTOP, -PROUD)]
		b.quad(g, "pc_store_tile", p, nn, [Vector2(0, -HEAD / 1.2), Vector2(PROUD / 1.2, -HEAD / 1.2), Vector2(PROUD / 1.2, -FTOP / 1.2), Vector2(0, -FTOP / 1.2)])
	b.quad(g, "pc_store_tile", [P(a, t, n, F0, FTOP, -PROUD), P(a, t, n, F1, FTOP, -PROUD), P(a, t, n, F1, FTOP, 0.0), P(a, t, n, F0, FTOP, 0.0)], Vector3.UP)
	b.quad(g, "pc_store_steel", [P(a, t, n, F0, HEAD, -PROUD), P(a, t, n, F1, HEAD, -PROUD), P(a, t, n, F1, HEAD, 0.0), P(a, t, n, F0, HEAD, 0.0)], Vector3.DOWN)
	# the opening's returns: royal blue, back through the front wall; a black head over them
	var o0 = F0 + COL
	var o1 = F1 - COL
	b.quad(g, "pc_store_blue", [P(a, t, n, o0, 0, 0), P(a, t, n, o0, 0, WALL_T), P(a, t, n, o0, HEAD, WALL_T), P(a, t, n, o0, HEAD, 0)], t)
	b.quad(g, "pc_store_blue", [P(a, t, n, o1, 0, WALL_T), P(a, t, n, o1, 0, 0), P(a, t, n, o1, HEAD, 0), P(a, t, n, o1, HEAD, WALL_T)], -t)
	b.quad(g, "pc_store_steel", [P(a, t, n, o0, HEAD, 0), P(a, t, n, o1, HEAD, 0), P(a, t, n, o1, HEAD, 0.12), P(a, t, n, o0, HEAD, 0.12)], Vector3.DOWN)
	b.quad(g, "pc_store_black", [P(a, t, n, o0, HEAD, 0.12), P(a, t, n, o1, HEAD, 0.12), P(a, t, n, o1, HEAD, WALL_T), P(a, t, n, o0, HEAD, WALL_T)], Vector3.DOWN)
	# a small notice on the right return, as in the photo (1995: no food or drink)
	b.cur_color = Color("#f4f2ea")
	b.box(g, "vcolor_matte", P(a, t, n, o0 + 0.005, 1.55, 0.45), b.abs_size(t, 0.01, 0.28, 0.2, n))
	b.cur_color = Color.WHITE
	# the front wall's solid parts are obstacles (columns included)
	for wr in [[0.0, o0], [o1, UNIT]]:
		var w0 = P(a, t, n, wr[0], 0, -PROUD - 0.05)
		var w1 = P(a, t, n, wr[1], 0, WALL_T)
		b.obst(["rect", min(w0.x, w1.x), min(w0.z, w1.z), max(w0.x, w1.x), max(w0.z, w1.z)])

## The four faces of a glass-block column (u0..u1, y0..y1, from the wall out to -PROUD),
## each block 0.2 m: the texture holds 2 x 4 blocks over 0.4 x 0.8 m.
static func col_faces(b, g, a, t, n, u0, u1, y0, y1):
	var vs = -y0 / 0.8
	var ve = -y1 / 0.8
	var w = (u1 - u0) / 0.4
	var dd = PROUD / 0.4
	b.quad(g, "pc_store_glassblock", [P(a, t, n, u1, y0, -PROUD), P(a, t, n, u0, y0, -PROUD), P(a, t, n, u0, y1, -PROUD), P(a, t, n, u1, y1, -PROUD)], n,
		[Vector2(0, vs), Vector2(w, vs), Vector2(w, ve), Vector2(0, ve)])
	b.quad(g, "pc_store_glassblock", [P(a, t, n, u0, y0, 0), P(a, t, n, u0, y0, -PROUD), P(a, t, n, u0, y1, -PROUD), P(a, t, n, u0, y1, 0)], -t,
		[Vector2(0, vs), Vector2(dd, vs), Vector2(dd, ve), Vector2(0, ve)])
	b.quad(g, "pc_store_glassblock", [P(a, t, n, u1, y0, -PROUD), P(a, t, n, u1, y0, 0), P(a, t, n, u1, y1, 0), P(a, t, n, u1, y1, -PROUD)], t,
		[Vector2(0, vs), Vector2(dd, vs), Vector2(dd, ve), Vector2(0, ve)])

## "POCKET CHANGE": raised letters (letters.json outlines) 2.5 cm off the fascia, 7 cm deep.
static func letters(b, g, a, t, n):
	var J = JSON.parse_string(FileAccess.get_file_as_string("res://tools/stores/pocket_change/letters.json"))
	var d_back = -PROUD - LETTER_OFF
	var d_face = d_back - LETTER_D
	var X = func(p, d): return P(a, t, n, TEXT_U0 - float(p[0]) * LS, TEXT_Y + float(p[1]) * LS, d)
	for L in J.letters:
		var tr = L.tris
		var s = b.st(g, "pc_store_letterface", true)
		for i in range(0, tr.size(), 3):
			var p0 = X.call(tr[i], d_face)
			var p1 = X.call(tr[i + 1], d_face)
			var p2 = X.call(tr[i + 2], d_face)
			b.tri(s, p0, p1, p2, Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), n)
		for lp in L.loops:
			for i in lp.size():
				var q0 = lp[i]
				var q1 = lp[(i + 1) % lp.size()]
				var dx = float(q1[0]) - float(q0[0])
				var dy = float(q1[1]) - float(q0[1])
				var ln = sqrt(dx * dx + dy * dy)
				if ln < 1e-5:
					continue
				# outward in the letter's plane: (dy, -dx) for counter-clockwise outers and clockwise holes
				var nn = (-t * (dy / ln) + Vector3.UP * (-dx / ln)).normalized()
				b.quad(g, "pc_store_letterside", [X.call(q0, d_back), X.call(q1, d_back), X.call(q1, d_face), X.call(q0, d_face)], nn,
					[Vector2(0, 0), Vector2(0, 0), Vector2(0, 0), Vector2(0, 0)], true)

# ------------------------------------------------------------------ the room
static func room(b, G, a, t, n):
	var u0 = SIDE
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	var o0 = F0 + COL
	var o1 = F1 - COL
	var up = Vector3.UP
	# carpet: through the opening and over the whole room (2 m pattern repeat)
	b.quad(G, "pc_store_carpet", [P(a, t, n, o0, 0, 0), P(a, t, n, o1, 0, 0), P(a, t, n, o1, 0, WALL_T), P(a, t, n, o0, 0, WALL_T)], up, [], false, 0.5)
	b.quad(G, "pc_store_carpet", [P(a, t, n, u0, 0, WALL_T), P(a, t, n, u1, 0, WALL_T), P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB)], up, [], false, 0.5)
	# black lay-in ceiling (2 x 4 ft)
	var cq = [P(a, t, n, u0, CEIL, WALL_T), P(a, t, n, u0, CEIL, dB), P(a, t, n, u1, CEIL, dB), P(a, t, n, u1, CEIL, WALL_T)]
	var cuv = []
	for p in cq:
		cuv.append(Vector2(p.x / 1.22, p.z / 2.44))
	b.quad(G, "pc_store_ceiling", cq, Vector3.DOWN, cuv)
	# dark walls: sides, back, and the front wall's inside
	b.quad(G, "pc_store_wall", [P(a, t, n, u0, 0, WALL_T), P(a, t, n, u0, 0, dB), P(a, t, n, u0, CEIL, dB), P(a, t, n, u0, CEIL, WALL_T)], t)
	b.quad(G, "pc_store_wall", [P(a, t, n, u1, 0, dB), P(a, t, n, u1, 0, WALL_T), P(a, t, n, u1, CEIL, WALL_T), P(a, t, n, u1, CEIL, dB)], -t)
	b.quad(G, "pc_store_wall", [P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB), P(a, t, n, u0, CEIL, dB), P(a, t, n, u1, CEIL, dB)], n)
	b.quad(G, "pc_store_wall", [P(a, t, n, u0, 0, WALL_T), P(a, t, n, o0, 0, WALL_T), P(a, t, n, o0, CEIL, WALL_T), P(a, t, n, u0, CEIL, WALL_T)], -n)
	b.quad(G, "pc_store_wall", [P(a, t, n, o1, 0, WALL_T), P(a, t, n, u1, 0, WALL_T), P(a, t, n, u1, CEIL, WALL_T), P(a, t, n, o1, CEIL, WALL_T)], -n)
	b.quad(G, "pc_store_wall", [P(a, t, n, o0, HEAD, WALL_T), P(a, t, n, o1, HEAD, WALL_T), P(a, t, n, o1, CEIL, WALL_T), P(a, t, n, o0, CEIL, WALL_T)], -n)
	# a royal-blue band round the room at 2.45-2.6 m, and a blue neon tube above it (guessed from
	# the blue returns at the door and the blue-lit Pocket Change interiors in Steven's references)
	for side in [[u0, t, WALL_T, dB], [u1, -t, dB, WALL_T]]:
		var uu = side[0]
		# the band is dynamic: 15 cm of wall was one lightmap texel tall and broke up into
		# blocks under the neon (Steven, Oct 6); it carries a soft glow of its own instead
		b.quad(G, "pc_store_band", [P(a, t, n, uu, 2.4, side[2]), P(a, t, n, uu, 2.4, side[3]), P(a, t, n, uu, 2.62, side[3]), P(a, t, n, uu, 2.62, side[2])], side[1], [], true)
		# 1990s neon: separate 1.8 m tubes with dark electrode ends, on clips, small gaps between
		var dn = WALL_T + 0.4
		while dn + 1.8 < dB - 0.3:
			var nc = P(a, t, n, uu, 3.3, dn + 0.9) + side[1] * 0.045
			b.box(G, "pc_store_neon", nc, b.abs_size(t, 0.025, 0.025, 1.7, n))
			for e in [-0.88, 0.88]:
				b.cur_color = Color("#1a1a1e")
				b.box(G, "vcolor", nc - n * e, b.abs_size(t, 0.04, 0.04, 0.06, n), Transform3D.IDENTITY, [], true)
			for e in [-0.5, 0.5]:
				b.cur_color = Color("#8a8a8a")
				b.box(G, "vcolor", nc - n * e - side[1] * 0.025, b.abs_size(t, 0.03, 0.05, 0.02, n), Transform3D.IDENTITY, [], true)
			b.cur_color = Color.WHITE
			dn += 1.9
	b.quad(G, "pc_store_band", [P(a, t, n, u1, 2.4, dB), P(a, t, n, u0, 2.4, dB), P(a, t, n, u0, 2.62, dB), P(a, t, n, u1, 2.62, dB)], n, [], true)
	# the back door (employees only) with a lit exit sign over it
	var du = 6.6
	b.cur_color = Color("#3a3c42")
	b.box(G, "vcolor", P(a, t, n, du, 1.05, dB - 0.02), b.abs_size(t, 0.95, 2.1, 0.04, n))
	b.cur_color = Color("#c9c9c9")
	b.box(G, "vcolor", P(a, t, n, du - 0.35, 1.0, dB - 0.06), b.abs_size(t, 0.12, 0.04, 0.04, n))
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, du, 2.35, dB - 0.05), b.abs_size(t, 0.36, 0.16, 0.06, n))

# ------------------------------------------------------------------ light
## A few small black can downlights down the room; the machines' own glow does the rest.
static func lights(b, G, a, t, n):
	var d = 3.0
	while d < DEPTH - 1.0:
		for u in [2.6, 5.4]:
			var c = P(a, t, n, u, CEIL - 0.005, d)
			b.cur_color = Color("#101012")
			b.cyl(G, "vcolor", c - Vector3(0, 0.02, 0), 0.09, 0.09, 0.02, 12, false, true, true)
			b.cur_color = Color.WHITE
			# the lamp's face is what lights the bake (Godot 4.7 lights mostly from emission)
			var s = b.st(G, "pc_store_can")
			for k in 12:
				var a0 = TAU * k / 12
				var a1 = TAU * (k + 1) / 12
				var cc = c - Vector3(0, 0.021, 0)
				b.tri(s, cc, cc + Vector3(cos(a0), 0, sin(a0)) * 0.07, cc + Vector3(cos(a1), 0, sin(a1)) * 0.07, Vector2(0.5, 0.5), Vector2(0, 0), Vector2(1, 0), Vector3.DOWN)
			var l = b.add_spot(c - Vector3(0, 0.05, 0), Vector3.DOWN, 2.5, 6.0, 50.0, Color(1.0, 0.86, 0.66))
			b.tag(l, "", 2.5, 2.5)
		d += 5.0
	# brighter over the redemption counter and the prize wall
	for dd in [3.6, 5.6, 7.6]:
		var l2 = b.add_spot(P(a, t, n, 6.7, CEIL - 0.05, dd), Vector3.DOWN, 3.0, 5.0, 55.0, Color(1.0, 0.93, 0.82))
		b.tag(l2, "", 3.0, 3.0)

# ------------------------------------------------------------------ the machines
## Plush piles and the skee-ball rings are thousands of tiny faces: in the lightmap each
## becomes its own chart with padding, which pushed the mall's atlas to a second size
## step (+4 MB per lighting setup and format). They move to the dynamic meshes, lit by
## the probes. The screens stay static so their glow is baked onto the room.
static func unbake_small(b):
	for gname in b.acc.keys():
		if not gname.ends_with("_mach"):
			continue
		for mname in b.acc[gname].keys():
			if not (mname.contains("plush") or mname.contains("_fur") or mname == "pc_skee_rim"):
				continue
			var s_static = b.acc[gname][mname]
			b.acc[gname].erase(mname)
			if not b.dyn_acc.has(gname):
				b.dyn_acc[gname] = {}
			if b.dyn_acc[gname].has(mname):
				var tmp = ArrayMesh.new()
				s_static.commit(tmp)
				b.dyn_acc[gname][mname].append_from(tmp, 0, Transform3D.IDENTITY)
			else:
				b.dyn_acc[gname][mname] = s_static

## Places one prop module: the player stands at (u, d) facing `dir` ("+d", "-d", "+u", "-u").
## Its walk obstacles are widened by `pad` so the camera stays out of the cabinets.
static func put(b, a, t, n, mod, u, d, dir, opts = {}, pad = 0.25):
	var f = {"+d": -n, "-d": n, "+u": t, "-u": -t}[dir]
	var M = load("res://tools/stores/pocket_change/%s.gd" % mod)
	var k0 = b.obstacles.size()
	# one mesh per 10 m of the room, so the ones out of view are culled
	M.build(b, "pc%d_mach" % int(clamp(d / 10.0, 0, 3)), P(a, t, n, u, 0, d), f, opts)
	for i in range(k0, b.obstacles.size()):
		var o = b.obstacles[i]
		if o[0] is String and o[0] == "rect":
			b.obstacles[i] = ["rect", o[1] - pad, o[2] - pad, o[3] + pad, o[4] + pad]
	return M

## Width (along the player's right) and depth of a module's machine.
static func fp(mod, opts = {}):
	return load("res://tools/stores/pocket_change/%s.gd" % mod).footprint(opts)

## A row of upright cabinets against a side wall: `wall_u` is the wall's face, facing
## the room along `dir`. They run from d0 toward +d with 3 cm gaps, cycling through
## `styles`, until the next one would pass d_max. Returns where the row ends.
static func wall_row(b, a, t, n, styles, wall_u, dir, d0, d_max = -1.0):
	var d = d0
	var k = 0
	var count = styles.size() if d_max < 0.0 else 1000
	while k < count:
		var o = {"style": styles[k % styles.size()]}
		var sz = fp("video", o)
		if d_max >= 0.0 and d + sz.x > d_max:
			break
		var u = wall_u + sz.y if dir == "-u" else wall_u - sz.y
		put(b, a, t, n, "video", u, d + sz.x * 0.5, dir, o)
		d += sz.x + 0.03
		k += 1
	return d

## A run of machines of one module with their backs flush to a side wall, side by side
## from d0 toward +d. Returns where the run ends.
static func wall_run(b, a, t, n, mod, opts_list, wall_u, dir, d0, gap = 0.0):
	var d = d0
	for o in opts_list:
		var sz = fp(mod, o)
		var u = wall_u + sz.y if dir == "-u" else wall_u - sz.y
		put(b, a, t, n, mod, u, d + sz.x * 0.5, dir, o)
		d += sz.x + gap
	return d

## The layout, as Steven remembers it (Oct 6). Walking in, everything on the right
## stands flush against the right wall in one line, front to back: the claw machines,
## the four skee-ball alleys, the four basketball games, then the video games. On the
## left are the token changers, the redemption counter and the prize wall, then video
## games, the racers and pinball. The sit-in ride and an island of uprights are in the
## middle, and two air hockey tables are in the open middle at the back.
static func machines(b, a, t, n):
	var u0 = SIDE              # the right wall (walking in)
	var u1 = UNIT - SIDE       # the left wall
	# --- left: token changers against the front wall, then the redemption counter
	for u in [6.95, 7.5]:
		put(b, a, t, n, "redeem", u, WALL_T + 0.5, "-d", {"kind": "tokens"}, 0.15)
	put(b, a, t, n, "redeem", 6.7, 2.5, "+d", {"kind": "counter", "length": 1.6}, 0.15)
	put(b, a, t, n, "redeem", 5.9, 5.6, "+u", {"kind": "counter", "length": 5.0}, 0.15)
	put(b, a, t, n, "redeem", u1 - 0.45, 5.6, "+u", {"kind": "prizewall", "length": 5.0, "height": 2.8}, 0.0)
	# --- right wall, front to back: claws, skee-ball, basketball, video games. Steven (Oct 6,
	# 12:22): the whole line starts about 10 ft further back than first built
	var d = WALL_T + 0.05 + RIGHT_BACK
	d = wall_run(b, a, t, n, "crane", [{"style": 0}, {"style": 1}, {"style": 2}], u0, "-u", d, 0.02)
	d = wall_run(b, a, t, n, "skee", [{"number": 1}, {"number": 2}, {"number": 3}, {"number": 4}], u0, "-u", d + 0.1 + BACK_10FT)
	d = wall_run(b, a, t, n, "hoops", [{"number": 1}, {"number": 2}, {"number": 3}, {"number": 4}], u0, "-u", d + 0.1)
	wall_row(b, a, t, n, [0, 3, 4, 5, 2, 6, 1, 7, 0, 4, 3, 2, 5, 6], u0, "-u", d + 0.15, DEPTH - 1.9)
	# --- left wall past the prize wall: video games, the twin racers, more video games,
	# pinball, and video games up to the back door
	d = wall_row(b, a, t, n, [1, 6, 0, 4, 3, 2], u1, "+u", 8.6, 14.4)
	d = wall_run(b, a, t, n, "driver", [{"kind": "racer", "style": 0}, {"kind": "racer", "style": 1}], u1, "+u", 14.5, 0.1)
	d = wall_row(b, a, t, n, [2, 5, 0, 7, 3, 4, 6, 1], u1, "+u", d + 0.2, 29.0)
	d = wall_run(b, a, t, n, "driver", [{"kind": "pinball", "style": 0}, {"kind": "pinball", "style": 1}, {"kind": "pinball", "style": 2}], u1, "+u", 29.2, 0.12)
	wall_row(b, a, t, n, [0, 3, 5, 2], u1, "+u", d + 0.2, DEPTH - 2.2)
	# --- the feature game dead centre as you walk in (Steven, Oct 6): the cyclone-style
	# light-ring ticket game, and the coin pusher behind it, both facing the entrance
	put(b, a, t, n, "cyclone", CENTRE_U, CYC_D, "+d", {}, 0.2)
	# the coin pusher turned lengthwise (Steven, Oct 6 18:30): its three positions face the
	# left aisle and the redemption counter, its back to the claw machines
	var ps = fp("pusher")
	put(b, a, t, n, "pusher", PUSH_U + ps.y * 0.5, PUSH_D, "-u", {}, 0.2)
	# --- the middle: the sit-in dinosaur ride, its doorway toward the entrance (you can step in)
	var ru = 4.45
	var rd = 11.4 + BACK_10FT
	var k0 = b.obstacles.size()
	put(b, a, t, n, "ride", ru, rd, "+d", {})
	b.obstacles.resize(k0)
	var rw = fp("ride")
	for r in [[-rw.x * 0.5, -0.5, 0.0, rw.y], [0.5, rw.x * 0.5, 0.0, rw.y], [-0.5, 0.5, 1.15, rw.y]]:
		var q0 = P(a, t, n, ru - r[0], 0, rd + r[2])
		var q1 = P(a, t, n, ru - r[1], 0, rd + r[3])
		b.obst(["rect", min(q0.x, q1.x) - 0.1, min(q0.z, q1.z) - 0.1, max(q0.x, q1.x) + 0.1, max(q0.z, q1.z) + 0.1])
	# --- an island of back-to-back uprights
	d = 18.6 + BACK_10FT
	for pr in [[0, 4], [2, 5], [3, 0]]:
		var sa = fp("video", {"style": pr[0]})
		var sb = fp("video", {"style": pr[1]})
		var wdt = max(sa.x, sb.x)
		put(b, a, t, n, "video", 4.0 - sa.y, d + wdt * 0.5, "+u", {"style": pr[0]})
		put(b, a, t, n, "video", 4.0 + sb.y, d + wdt * 0.5, "-u", {"style": pr[1]})
		d += wdt + 0.03
	# --- two air hockey tables in the open middle at the back, end to end down the room
	for i in 2:
		put(b, a, t, n, "airhockey", 4.0, 25.6 + BACK_10FT + i * 5.2, "+d", {"number": i + 1})
	# --- a few uprights on the back wall, right of the back door
	for i in 3:
		var s = [3, 0, 2][i]
		var sz = fp("video", {"style": s})
		put(b, a, t, n, "video", 1.9 + i * 0.75, DEPTH - SIDE - sz.y, "+d", {"style": s})

# ------------------------------------------------------------------ materials
## "pc_store_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"tile":
			# glazed wall tile: a soft sheen (the hall's probe gives it the mall's reflections)
			m.albedo_texture = b.tex("pc/store_tile.png"); m.roughness = 0.22; m.metallic_specular = 0.6
		"glassblock":
			m.albedo_texture = b.tex("pc/store_glassblock.png"); m.roughness = 0.06; m.metallic_specular = 1.0
		"steel":
			# the polished head under the fascia (a bright reflective strip in the photo)
			m.albedo_color = Color("#eceef0"); m.metallic = 0.55; m.roughness = 0.1
		"blue":
			m.albedo_color = Color("#1e48b0"); m.roughness = 0.55
		"band":
			m.albedo_color = Color("#1e48b0"); m.roughness = 0.55
			m.emission_enabled = true; m.emission = Color("#2c58d8"); m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.35); m.set_meta("e_night", 0.35)
		"black":
			m.albedo_color = Color("#0e0e12"); m.roughness = 0.8
		"letterface":
			# brushed aluminium faces read near-white in the photo, against the darker tile; the
			# letters are lit by probes (dynamic), so a little emission stands in for the hall's light
			m.albedo_color = Color("#f4f5f6"); m.metallic = 0.1; m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#e8eaec"); m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.55); m.set_meta("e_night", 0.4)
		"letterside":
			m.albedo_color = Color("#7c8084"); m.metallic = 0.2; m.roughness = 0.45
			m.emission_enabled = true; m.emission = Color("#6a6e72"); m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.35); m.set_meta("e_night", 0.25)
		"carpet":
			# plain dark carpet, no pattern and no glow (Steven, Oct 6)
			m.albedo_texture = b.tex("pc/store_carpet.png"); m.roughness = 0.95; m.metallic_specular = 0.2
		"can":
			m.albedo_color = Color("#fff4e0")
			m.emission_enabled = true; m.emission = Color("#ffe6c0"); m.emission_energy_multiplier = 10.0
			m.set_meta("e_day", 10.0); m.set_meta("e_night", 10.0)
		"ceiling":
			m.albedo_texture = b.tex("pc/store_ceiling.png"); m.roughness = 0.95
		"wall":
			m.albedo_texture = b.tex("pc/store_wall.png"); m.roughness = 0.85
		"neon":
			m.albedo_color = Color("#3a6cff")
			m.emission_enabled = true; m.emission = Color("#3f6dff"); m.emission_energy_multiplier = 5.0
			m.set_meta("e_day", 5.0); m.set_meta("e_night", 5.0)
		_:
			return false
	return true
