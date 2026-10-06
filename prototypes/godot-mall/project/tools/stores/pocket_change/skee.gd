## Pocket Change prop module `skee`: a 1990s ten-foot ticket-redemption roll-down
## ball alley (the generic "skee-ball" type; no brand, original artwork).
## Contract: tools/stores/pocket_change/README.md. Textures: paint_skee.py -> tex/pc/skee_*.png.
##
## Real form factor (classic 10 ft alley): 0.76 m wide (2'6"), 3.12 m long (10'3"),
## inclined lane (~8.4 deg) from a front ball trough up to a ramp hump, an inclined
## scoring board (10/20/30/40/50 + two 100 corner pockets) behind a welded-wire
## cage, and a backlit marquee box whose top sits at 2.30 m (beacon to 2.39 m).
## The player stands at the low front end (local z = 0).
##   tools/qa/preview.sh skee <out> "0,1.6,1.6,0,-25;1.6,1.7,1.0,50,-20" '{"number":1}' lit
##
## opts: {"number": 1..4} picks the lane number badge, the score on the LED display,
## a slight body tint, mirrored lane wear, ball jitter and which WINNER beacon is lit.

const W = 0.76          # outside width (along the player's right)
const D = 3.12          # depth (along f)
const RX = 0.32         # inner half-width (lane and board are 0.64 m wide)
const SX = 0.38         # outer half-width
const Z_LANE = 0.32     # lane starts behind the front ball trough
const Y_LANE = 0.80     # lane height at its front edge
const SLOPE = 0.147     # lane rise per metre (about 8.4 degrees)
const Z_HUMP = 1.95     # ramp hump from here ...
const Z_LIP = 2.17      # ... to its lip
const HUMP_RISE = 0.085
const PB = Vector3(0, 1.02, 2.24)   # scoring board, bottom centre
const PT = Vector3(0, 1.62, 3.06)   # scoring board, top centre
const CAGE_LO = Vector2(2.30, 1.40) # cage front, bottom bar (z, y)
const CAGE_HI = Vector2(2.82, 1.80) # cage front, top (meets the marquee box)
const MQ_Y0 = 1.80
const MQ_Y1 = 2.30
const MQ_Z0 = 2.82
const BALL_R = 0.036
const SIDE_Z = 3.12     # side texture spans z 0..3.12, y 0..1.60 (see paint_skee.py)
const SIDE_Y = 1.60

## Footprint (width, depth) in metres. Four alleys abut side by side at this width.
static func footprint(_opts = {}):
	return Vector2(W, D)

## The machine's frame: local x = player's right, y = up, z = into the machine (along f).
static func X(o, f):
	return Transform3D(Basis(f.cross(Vector3.UP), Vector3.UP, f), o)

static func lane_y(z):
	return Y_LANE + (z - Z_LANE) * SLOPE

static func rail_y(z):
	return 0.905 if z <= Z_LANE else lane_y(z) + 0.105

static func hump_y(t):
	return lane_y(Z_HUMP + (Z_LIP - Z_HUMP) * t) + HUMP_RISE * t * t

## Smooth normal of the ramp hump at parameter t (0 = foot, 1 = lip).
static func hump_n(t):
	var dz = Z_LIP - Z_HUMP
	var dy = SLOPE * dz + 2.0 * HUMP_RISE * t
	return Vector3(0, dz, -dy).normalized()

## Local quad with its normal from the winding, flipped to agree with `hint`.
static func q(b, g, m, xf, p, hint, uvs = null, dyn = false):
	var n = (p[1] - p[0]).cross(p[3] - p[0])
	if n.length() < 1e-9:
		n = (p[2] - p[1]).cross(p[3] - p[1])
	n = n.normalized()
	if n.dot(hint) < 0.0:
		n = -n
	var w = []
	for v in p:
		w.append(xf * v)
	b.quad(g, m, w, (xf.basis * n).normalized(), [] if uvs == null else uvs, dyn)

## Smooth-shaded local quad (per-vertex normals).
static func qn(b, s, xf, p, n, uv, face_n):
	var wp = []
	var wn = []
	for i in 4:
		wp.append(xf * p[i])
		wn.append((xf.basis * n[i]).normalized())
	var fn = (xf.basis * face_n).normalized()
	b._tri_n(s, [wp[0], wp[1], wp[2]], [wn[0], wn[1], wn[2]], [uv[0], uv[1], uv[2]], fn)
	b._tri_n(s, [wp[0], wp[2], wp[3]], [wn[0], wn[2], wn[3]], [uv[0], uv[2], uv[3]], fn)

## A box along an arbitrary local direction (tubes, bars).
static func bar(b, g, m, xf, a, c, th, dyn = true):
	var d = c - a
	var az = d.normalized()
	var ax = Vector3.UP.cross(az).normalized() if abs(az.y) < 0.9 else Vector3.RIGHT
	var ay = az.cross(ax).normalized()
	b.box(g, m, Vector3.ZERO, Vector3(th, th, d.length()), xf * Transform3D(Basis(ax, ay, az), (a + c) * 0.5), [], dyn)

static func side_uv(z, y):
	return Vector2(z / SIDE_Z, (SIDE_Y - y) / SIDE_Y)

## Builds one alley. The player stands at `o` (floor, centre of the front edge) facing `f`.
static func build(b, g, o, f, opts = {}):
	var xf = X(o, f)
	var num = clampi(int(opts.get("number", 1)), 1, 4)
	var sk = "pc_skee_side%d" % num
	var fk = "pc_skee_front%d" % num
	var rng = RandomNumberGenerator.new()
	rng.seed = 7700 + num
	b.cur_color = Color.WHITE
	var L = Vector3.LEFT
	var R = Vector3.RIGHT
	var U = Vector3.UP
	var DN = Vector3.DOWN
	var FW = Vector3(0, 0, -1)   # local -z, toward the player
	var BK = Vector3(0, 0, 1)    # local +z, into the machine

	# ---------------------------------------------------------------- side panels (outer faces)
	var side_quads = [
		[Vector2(0, 0.28), Vector2(0, 0.895), Vector2(Z_LANE, 0.895), Vector2(Z_LANE, 0.28)],
		[Vector2(Z_LANE, 0.28), Vector2(Z_LANE, 0.895), Vector2(2.18, rail_y(2.18) - 0.01), Vector2(2.18, 0.28)],
		[Vector2(2.18, 0.0), Vector2(2.18, rail_y(2.18) - 0.01), Vector2(CAGE_LO.x, CAGE_LO.y), Vector2(CAGE_LO.x, 0.0)],
		[Vector2(CAGE_LO.x, 0.0), Vector2(CAGE_LO.x, CAGE_LO.y), Vector2(D, 1.52), Vector2(D, 0.0)],
	]
	for sx in [-1.0, 1.0]:
		for sq in side_quads:
			var p = []
			var uv = []
			for v in sq:
				p.append(Vector3(sx * SX, v.y, v.x))
				uv.append(side_uv(v.x, v.y))
			q(b, g, sk, xf, p, Vector3(sx, 0, 0), uv)
	# lettering decal on both sides (separate so it reads correctly from either side)
	for sx in [-1.0, 1.0]:
		var za = 1.60; var zb = 2.30
		var ya = 0.40; var yb = 0.575
		var x = sx * (SX + 0.0015)
		# from outside, the reading direction is +z on the right side and -z on the left
		var u0 = 0.0 if sx > 0 else 1.0
		var u1 = 1.0 - u0
		q(b, g, "pc_skee_sidetext", xf, [Vector3(x, ya, za), Vector3(x, ya, zb), Vector3(x, yb, zb), Vector3(x, yb, za)],
			Vector3(sx, 0, 0), [Vector2(u0, 1), Vector2(u1, 1), Vector2(u1, 0), Vector2(u0, 0)], true)

	# ---------------------------------------------------------------- rail caps (yellow) with a bevel on the outer edge
	var rail_pts = [0.10, Z_LANE, 2.18]
	for sx in [-1.0, 1.0]:
		for i in 2:
			var z0 = rail_pts[i]; var z1 = rail_pts[i + 1]
			var y0 = rail_y(z0); var y1 = rail_y(z1)
			var v0 = 1.0 - z0 / 2.18; var v1 = 1.0 - z1 / 2.18
			var xa = sx * RX; var xb = sx * (SX - 0.01)
			q(b, g, "pc_skee_rail", xf, [Vector3(xa, y0, z0), Vector3(xb, y0, z0), Vector3(xb, y1, z1), Vector3(xa, y1, z1)],
				U, [Vector2(0, v0), Vector2(0.85, v0), Vector2(0.85, v1), Vector2(0, v1)])
			var xc = sx * SX
			q(b, g, "pc_skee_rail", xf, [Vector3(xb, y0, z0), Vector3(xc, y0 - 0.01, z0), Vector3(xc, y1 - 0.01, z1), Vector3(xb, y1, z1)],
				Vector3(sx, 1, 0), [Vector2(0.85, v0), Vector2(1, v0), Vector2(1, v1), Vector2(0.85, v1)])
		# top of the back section of the side panel (painted black edge)
		var e0 = Vector2(2.18, rail_y(2.18) - 0.01)
		var e1 = CAGE_LO
		var e2 = Vector2(D, 1.52)
		for seg in [[e0, e1], [e1, e2]]:
			var a = seg[0]; var c = seg[1]
			q(b, g, "pc_skee_edge", xf, [Vector3(sx * RX, a.y, a.x), Vector3(sx * SX, a.y, a.x), Vector3(sx * SX, c.y, c.x), Vector3(sx * RX, c.y, c.x)],
				Vector3(0, 1, -0.2))

	# ---------------------------------------------------------------- front face, aluminium cap, trough
	q(b, g, fk, xf, [Vector3(-SX, 0.28, 0), Vector3(SX, 0.28, 0), Vector3(SX, 0.80, 0), Vector3(-SX, 0.80, 0)], FW,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	b.box(g, "pc_skee_metal", Vector3(0, 0.8525, 0.045), Vector3(W + 0.02, 0.105, 0.11), xf)
	# front cap's rounded lip: a 45 degree chamfer strip along the top front edge
	q(b, g, "pc_skee_metal", xf, [Vector3(-SX - 0.01, 0.905, -0.01), Vector3(SX + 0.01, 0.905, -0.01), Vector3(SX + 0.01, 0.915, 0.0), Vector3(-SX - 0.01, 0.915, 0.0)],
		Vector3(0, 1, -1), [Vector2(0, 0), Vector2(0.78, 0), Vector2(0.78, 0.02), Vector2(0, 0.02)])
	q(b, g, "pc_skee_metal", xf, [Vector3(-SX - 0.01, 0.915, 0.0), Vector3(SX + 0.01, 0.915, 0.0), Vector3(SX + 0.01, 0.915, 0.09), Vector3(-SX - 0.01, 0.915, 0.09)],
		U, [Vector2(0, 0.1), Vector2(0.78, 0.1), Vector2(0.78, 0.2), Vector2(0, 0.2)])
	q(b, g, "pc_skee_metal", xf, [Vector3(-SX - 0.01, 0.915, 0.09), Vector3(SX + 0.01, 0.915, 0.09), Vector3(SX + 0.01, 0.905, 0.10), Vector3(-SX - 0.01, 0.905, 0.10)],
		Vector3(0, 1, 1), [Vector2(0, 0.3), Vector2(0.78, 0.3), Vector2(0.78, 0.32), Vector2(0, 0.32)])
	# aluminium angle on the two front vertical corners (as on real alleys)
	for sx in [-1.0, 1.0]:
		b.box(g, "pc_skee_metal", Vector3(sx * (SX - 0.007), 0.54, -0.003), Vector3(0.03, 0.52, 0.006), xf)
		b.box(g, "pc_skee_metal", Vector3(sx * (SX + 0.003), 0.54, 0.012), Vector3(0.006, 0.52, 0.03), xf)
	# ball trough (ball return) across the front, below lane level
	q(b, g, "pc_skee_trough", xf, [Vector3(-RX, 0.77, 0.10), Vector3(RX, 0.77, 0.10), Vector3(RX, 0.77, Z_LANE), Vector3(-RX, 0.77, Z_LANE)], U)
	q(b, g, "pc_skee_trough", xf, [Vector3(-RX, 0.77, 0.10), Vector3(RX, 0.77, 0.10), Vector3(RX, 0.80, 0.10), Vector3(-RX, 0.80, 0.10)], BK)
	q(b, g, "pc_skee_metal", xf, [Vector3(-RX, 0.77, Z_LANE), Vector3(RX, 0.77, Z_LANE), Vector3(RX, Y_LANE, Z_LANE), Vector3(-RX, Y_LANE, Z_LANE)], FW,
		[Vector2(0, 0.5), Vector2(0.64, 0.5), Vector2(0.64, 0.56), Vector2(0, 0.56)])

	# ---------------------------------------------------------------- lane and ramp hump
	var mir = num % 2 == 0
	var ul = 1.0 if mir else 0.0
	var ur = 0.0 if mir else 1.0
	var hv = 0.13   # lane texture: v 0..0.13 is the hump, 0.13..1 the lane (back to front)
	q(b, g, "pc_skee_lane", xf, [Vector3(-RX, Y_LANE, Z_LANE), Vector3(RX, Y_LANE, Z_LANE), Vector3(RX, lane_y(Z_HUMP), Z_HUMP), Vector3(-RX, lane_y(Z_HUMP), Z_HUMP)],
		U, [Vector2(ul, 1), Vector2(ur, 1), Vector2(ur, hv), Vector2(ul, hv)])
	var HS = 8
	var ls = b.st(g, "pc_skee_lane")
	for i in HS:
		var t0 = float(i) / HS; var t1 = float(i + 1) / HS
		var z0 = Z_HUMP + (Z_LIP - Z_HUMP) * t0; var z1 = Z_HUMP + (Z_LIP - Z_HUMP) * t1
		var y0 = hump_y(t0); var y1 = hump_y(t1)
		var n0 = hump_n(t0); var n1 = hump_n(t1)
		qn(b, ls, xf, [Vector3(-RX, y0, z0), Vector3(RX, y0, z0), Vector3(RX, y1, z1), Vector3(-RX, y1, z1)], [n0, n0, n1, n1],
			[Vector2(ul, hv * (1 - t0)), Vector2(ur, hv * (1 - t0)), Vector2(ur, hv * (1 - t1)), Vector2(ul, hv * (1 - t1))], (n0 + n1).normalized())
		# inner rail faces along the hump (black bumper)
		for sx in [-1.0, 1.0]:
			q(b, g, "pc_skee_bumper", xf, [Vector3(sx * RX, y0, z0), Vector3(sx * RX, rail_y(z0), z0), Vector3(sx * RX, rail_y(z1), z1), Vector3(sx * RX, y1, z1)],
				Vector3(-sx, 0, 0))
	# hump lip (rounded, worn hardwood) and its drop into the gutter
	var yl = hump_y(1.0)
	q(b, g, "pc_skee_lane", xf, [Vector3(-RX, yl, Z_LIP), Vector3(RX, yl, Z_LIP), Vector3(RX, yl - 0.012, Z_LIP + 0.01), Vector3(-RX, yl - 0.012, Z_LIP + 0.01)],
		Vector3(0, 1, 1), [Vector2(0, 0.0), Vector2(1, 0.0), Vector2(1, 0.004), Vector2(0, 0.004)])
	q(b, g, "pc_skee_dark", xf, [Vector3(-RX, yl - 0.012, Z_LIP + 0.01), Vector3(RX, yl - 0.012, Z_LIP + 0.01), Vector3(RX, 0.96, Z_LIP + 0.01), Vector3(-RX, 0.96, Z_LIP + 0.01)], BK)
	q(b, g, "pc_skee_dark", xf, [Vector3(-RX, 0.96, Z_LIP + 0.01), Vector3(RX, 0.96, Z_LIP + 0.01), Vector3(RX, 0.96, PB.z), Vector3(-RX, 0.96, PB.z)], U)
	q(b, g, "pc_skee_dark", xf, [Vector3(-RX, 0.96, PB.z), Vector3(RX, 0.96, PB.z), Vector3(RX, PB.y, PB.z), Vector3(-RX, PB.y, PB.z)], FW)
	# inner rail faces along trough and lane
	for sx in [-1.0, 1.0]:
		var x = sx * RX
		q(b, g, "pc_skee_bumper", xf, [Vector3(x, 0.77, 0.10), Vector3(x, 0.905, 0.10), Vector3(x, 0.905, Z_LANE), Vector3(x, 0.77, Z_LANE)], Vector3(-sx, 0, 0))
		q(b, g, "pc_skee_bumper", xf, [Vector3(x, Y_LANE, Z_LANE), Vector3(x, rail_y(Z_LANE + 0.001), Z_LANE), Vector3(x, rail_y(Z_HUMP), Z_HUMP), Vector3(x, lane_y(Z_HUMP), Z_HUMP)], Vector3(-sx, 0, 0))
		# inner walls of the scoring section (dark, seen through the cage)
		q(b, g, "pc_skee_inner", xf, [Vector3(x, 0.95, Z_LIP), Vector3(x, rail_y(2.18) - 0.01, Z_LIP), Vector3(x, CAGE_LO.y, CAGE_LO.x), Vector3(x, 0.95, CAGE_LO.x)], Vector3(-sx, 0, 0))
		q(b, g, "pc_skee_inner", xf, [Vector3(x, 0.95, CAGE_LO.x), Vector3(x, CAGE_LO.y, CAGE_LO.x), Vector3(x, 1.514, 3.08), Vector3(x, 0.95, 3.08)], Vector3(-sx, 0, 0))
		# the 6 cm side wall's open top inside the cage (dark)
	# metal lip at the front edge of the lane and the ball gate rod
	b.box(g, "pc_skee_metal", Vector3(0, Y_LANE + 0.004, Z_LANE + 0.012), Vector3(0.64, 0.008, 0.024), xf, [], true)
	b.box(g, "pc_skee_chrome", Vector3(0, Y_LANE + 0.06, Z_LANE - 0.004), Vector3(0.64, 0.009, 0.009), xf, [], true)

	# ---------------------------------------------------------------- scoring board with raised rings
	var dv = (PT - PB).normalized()
	var BL = (PT - PB).length()
	var nb = Vector3(0, dv.z, -dv.y)   # up and toward the player
	q(b, g, "pc_skee_board", xf, [PB + Vector3(-RX, 0, 0), PB + Vector3(RX, 0, 0), PT + Vector3(RX, 0, 0), PT + Vector3(-RX, 0, 0)], nb,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	q(b, g, "pc_skee_inner", xf, [PT + Vector3(-RX, 0, 0), PT + Vector3(RX, 0, 0), Vector3(RX, 1.62, 3.08), Vector3(-RX, 1.62, 3.08)], U)
	q(b, g, "pc_skee_inner", xf, [Vector3(-RX, 1.62, 3.08), Vector3(RX, 1.62, 3.08), Vector3(RX, MQ_Y0, 3.08), Vector3(-RX, MQ_Y0, 3.08)], FW)
	# rims: (centre u, centre v, radius, height) in board metres (u across from the left edge, v up the slope)
	var rims = [[0.32, 0.40, 0.28, 0.045], [0.32, 0.44, 0.20, 0.04], [0.32, 0.47, 0.13, 0.035], [0.32, 0.49, 0.058, 0.03],
		[0.32, 0.79, 0.058, 0.03], [0.075, 0.875, 0.052, 0.03], [0.565, 0.875, 0.052, 0.03]]
	var rs = b.st(g, "pc_skee_rim")
	var BX = Vector3.RIGHT
	for rm in rims:
		var seg = 36 if rm[2] > 0.1 else 20
		var th = 0.006
		for i in seg:
			var a0 = TAU * i / seg; var a1 = TAU * (i + 1) / seg
			var d0 = BX * cos(a0) + dv * sin(a0)
			var d1 = BX * cos(a1) + dv * sin(a1)
			var c = PB + BX * (rm[0] - RX) + dv * rm[1]
			var h = nb * rm[3]
			var o0 = c + d0 * (rm[2] + th); var o1 = c + d1 * (rm[2] + th)
			var i0 = c + d0 * (rm[2] - th); var i1 = c + d1 * (rm[2] - th)
			var uv4 = [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)]
			qn(b, rs, xf, [o0, o1, o1 + h, o0 + h], [d0, d1, d1, d0], uv4, (d0 + d1).normalized())
			qn(b, rs, xf, [i0 + h, i1 + h, i1, i0], [-d0, -d1, -d1, -d0], uv4, -(d0 + d1).normalized())
			var t0 = (d0 + nb).normalized(); var t1 = (d1 + nb).normalized()
			var s0 = (-d0 + nb).normalized(); var s1 = (-d1 + nb).normalized()
			qn(b, rs, xf, [o0 + h, o1 + h, i1 + h, i0 + h], [t0, t1, s1, s0], uv4, nb)

	# ---------------------------------------------------------------- back panel and bottom
	q(b, g, "pc_skee_back", xf, [Vector3(-SX, 0, D), Vector3(SX, 0, D), Vector3(SX, MQ_Y0, D), Vector3(-SX, MQ_Y0, D)], BK)
	q(b, g, "pc_skee_dark", xf, [Vector3(-SX, 0.28, 0), Vector3(SX, 0.28, 0), Vector3(SX, 0.28, 2.18), Vector3(-SX, 0.28, 2.18)], DN)
	q(b, g, "pc_skee_dark", xf, [Vector3(-SX, 0, 2.18), Vector3(SX, 0, 2.18), Vector3(SX, 0.28, 2.18), Vector3(-SX, 0.28, 2.18)], FW)
	b.box(g, "pc_skee_plinth", Vector3(0, 0.14, 0.34), Vector3(0.70, 0.28, 0.36), xf, ["+y"])
	b.box(g, "pc_skee_plinth", Vector3(0, 0.14, 1.45), Vector3(0.70, 0.28, 0.30), xf, ["+y"])

	# ---------------------------------------------------------------- marquee box, lit art, LED digits, number badge, beacon
	var mz = (MQ_Z0 + D) * 0.5
	b.box(g, "pc_skee_mqbody", Vector3(0, (MQ_Y0 + MQ_Y1) * 0.5, mz), Vector3(W + 0.02, MQ_Y1 - MQ_Y0, D - MQ_Z0), xf, ["-z"])
	# the box's front frame (black channel around the translucent panel)
	var fz = MQ_Z0 - 0.004
	var ax0 = -0.37; var ax1 = 0.37; var ay0 = 1.82; var ay1 = 2.28
	q(b, g, "pc_skee_mqbody", xf, [Vector3(-SX - 0.01, MQ_Y0, MQ_Z0), Vector3(SX + 0.01, MQ_Y0, MQ_Z0), Vector3(SX + 0.01, ay0, MQ_Z0), Vector3(-SX - 0.01, ay0, MQ_Z0)], FW)
	q(b, g, "pc_skee_mqbody", xf, [Vector3(-SX - 0.01, ay1, MQ_Z0), Vector3(SX + 0.01, ay1, MQ_Z0), Vector3(SX + 0.01, MQ_Y1, MQ_Z0), Vector3(-SX - 0.01, MQ_Y1, MQ_Z0)], FW)
	q(b, g, "pc_skee_mqbody", xf, [Vector3(-SX - 0.01, ay0, MQ_Z0), Vector3(ax0, ay0, MQ_Z0), Vector3(ax0, ay1, MQ_Z0), Vector3(-SX - 0.01, ay1, MQ_Z0)], FW)
	q(b, g, "pc_skee_mqbody", xf, [Vector3(ax1, ay0, MQ_Z0), Vector3(SX + 0.01, ay0, MQ_Z0), Vector3(SX + 0.01, ay1, MQ_Z0), Vector3(ax1, ay1, MQ_Z0)], FW)
	q(b, g, "pc_skee_marquee", xf, [Vector3(ax0, ay0, MQ_Z0 + 0.012), Vector3(ax1, ay0, MQ_Z0 + 0.012), Vector3(ax1, ay1, MQ_Z0 + 0.012), Vector3(ax0, ay1, MQ_Z0 + 0.012)], FW,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	# recess walls between the frame and the panel
	for e in [[Vector3(ax0, ay0, 0), Vector3(ax1, ay0, 0), U], [Vector3(ax0, ay1, 0), Vector3(ax1, ay1, 0), DN],
			[Vector3(ax0, ay0, 0), Vector3(ax0, ay1, 0), R], [Vector3(ax1, ay0, 0), Vector3(ax1, ay1, 0), L]]:
		var p0 = e[0] + Vector3(0, 0, MQ_Z0); var p1 = e[1] + Vector3(0, 0, MQ_Z0)
		q(b, g, "pc_skee_mqbody", xf, [p0, p1, p1 + Vector3(0, 0, 0.012), p0 + Vector3(0, 0, 0.012)], e[2])
	# LED window (marquee px 232..792 x 214..354 of 1024 x 640)
	var lx0 = ax0 + (ax1 - ax0) * 232.0 / 1024.0; var lx1 = ax0 + (ax1 - ax0) * 792.0 / 1024.0
	var ly1 = ay1 - (ay1 - ay0) * 214.0 / 640.0; var ly0 = ay1 - (ay1 - ay0) * 354.0 / 640.0
	var r0 = float(num - 1) / 4.0; var r1 = float(num) / 4.0
	q(b, g, "pc_skee_led", xf, [Vector3(lx0, ly0, MQ_Z0 + 0.009), Vector3(lx1, ly0, MQ_Z0 + 0.009), Vector3(lx1, ly1, MQ_Z0 + 0.009), Vector3(lx0, ly1, MQ_Z0 + 0.009)], FW,
		[Vector2(0, r1), Vector2(1, r1), Vector2(1, r0), Vector2(0, r0)])
	# lane number badge (marquee px 52..124 x 46..118)
	var nx0 = ax0 + (ax1 - ax0) * 52.0 / 1024.0; var nx1 = ax0 + (ax1 - ax0) * 124.0 / 1024.0
	var ny1 = ay1 - (ay1 - ay0) * 46.0 / 640.0; var ny0 = ay1 - (ay1 - ay0) * 118.0 / 640.0
	var c0 = float(num - 1) / 4.0; var c1 = float(num) / 4.0
	q(b, g, "pc_skee_num", xf, [Vector3(nx0, ny0, MQ_Z0 + 0.009), Vector3(nx1, ny0, MQ_Z0 + 0.009), Vector3(nx1, ny1, MQ_Z0 + 0.009), Vector3(nx0, ny1, MQ_Z0 + 0.009)], FW,
		[Vector2(c0, 1), Vector2(c1, 1), Vector2(c1, 0), Vector2(c0, 0)])
	# fluorescent strip under the marquee box, lighting the rings
	q(b, g, "pc_skee_tube", xf, [Vector3(-0.30, MQ_Y0 - 0.004, MQ_Z0 + 0.03), Vector3(0.30, MQ_Y0 - 0.004, MQ_Z0 + 0.03), Vector3(0.30, MQ_Y0 - 0.004, 3.05), Vector3(-0.30, MQ_Y0 - 0.004, 3.05)], DN)
	# WINNER beacon (one of the four is lit: someone just hit the 100)
	var bc = xf * Vector3(0, MQ_Y1, mz)
	b.cur_color = Color("#1a1a1c")
	b.cyl(g, "vcolor", bc, 0.048, 0.046, 0.022, 14, true, false, true)
	b.cur_color = Color.WHITE
	b.cyl(g, "pc_skee_beacon_on" if num == 3 else "pc_skee_beacon_off", bc + Vector3(0, 0.022, 0), 0.040, 0.030, 0.06, 14, false, false, true)
	b.cyl(g, "pc_skee_beacon_on" if num == 3 else "pc_skee_beacon_off", bc + Vector3(0, 0.082, 0), 0.030, 0.012, 0.012, 14, true, false, true)

	# ---------------------------------------------------------------- wire cage
	for sx in [-1.0, 1.0]:
		var x = sx * (SX - 0.002)
		var cp = [Vector3(x, CAGE_LO.y, CAGE_LO.x), Vector3(x, CAGE_HI.y, CAGE_HI.x), Vector3(x, MQ_Y0, D), Vector3(x, 1.52, D)]
		var uv = []
		for p in cp:
			uv.append(Vector2(p.z, -p.y) * 10.0)
		q(b, g, "pc_skee_mesh", xf, cp, Vector3(sx, 0, 0), uv, true)
	var fp = [Vector3(-SX, CAGE_LO.y, CAGE_LO.x), Vector3(SX, CAGE_LO.y, CAGE_LO.x), Vector3(SX, CAGE_HI.y, CAGE_HI.x), Vector3(-SX, CAGE_HI.y, CAGE_HI.x)]
	var cl = Vector2(CAGE_HI.x - CAGE_LO.x, CAGE_HI.y - CAGE_LO.y).length()
	q(b, g, "pc_skee_mesh", xf, fp, Vector3(0, 1, -1.3), [Vector2(0, cl * 10), Vector2(W * 10, cl * 10), Vector2(W * 10, 0), Vector2(0, 0)], true)
	var tb = 0.022
	var lo = Vector3(0, CAGE_LO.y, CAGE_LO.x); var hi = Vector3(0, CAGE_HI.y, CAGE_HI.x)
	bar(b, g, "pc_skee_frame", xf, lo + Vector3(-SX, 0, 0), lo + Vector3(SX, 0, 0), tb)
	bar(b, g, "pc_skee_frame", xf, (lo + hi) * 0.5 + Vector3(-SX, 0, 0), (lo + hi) * 0.5 + Vector3(SX, 0, 0), 0.016)
	bar(b, g, "pc_skee_frame", xf, hi + Vector3(-SX, -0.01, 0), hi + Vector3(SX, -0.01, 0), tb)
	for sx in [-1.0, 1.0]:
		var x = sx * (SX - 0.008)
		bar(b, g, "pc_skee_frame", xf, Vector3(x, CAGE_LO.y, CAGE_LO.x), Vector3(x, CAGE_HI.y, CAGE_HI.x), tb)
		bar(b, g, "pc_skee_frame", xf, Vector3(x, CAGE_LO.y, CAGE_LO.x), Vector3(x, 1.52, D - 0.01), 0.018)
		bar(b, g, "pc_skee_frame", xf, Vector3(x, MQ_Y0 - 0.01, CAGE_HI.x), Vector3(x, 1.52, D - 0.01), 0.014)

	# ---------------------------------------------------------------- balls resting in the front trough
	var bs = b.st(g, "pc_skee_ball", true)
	for i in 9:
		var cx = -RX + BALL_R + 0.002 + i * 0.0705
		var c = Vector3(cx, 0.77 + BALL_R, 0.205 + rng.randf_range(-0.012, 0.012))
		sphere(b, bs, xf, c, BALL_R, rng.randf() * TAU)

	# ---------------------------------------------------------------- coin door, coin lamps, ticket slot, ticket strip, START, lane plate
	var fw = func(x, y): return Vector2((x + SX) / W, (0.80 - y) / 0.52)
	var cd = [-0.31, 0.36, -0.07, 0.70]
	var dz = -0.006
	q(b, g, fk, xf, [Vector3(cd[0], cd[1], dz), Vector3(cd[2], cd[1], dz), Vector3(cd[2], cd[3], dz), Vector3(cd[0], cd[3], dz)], FW,
		[fw.call(cd[0], cd[1]), fw.call(cd[2], cd[1]), fw.call(cd[2], cd[3]), fw.call(cd[0], cd[3])], true)
	for e in [[Vector3(cd[0], cd[1], 0), Vector3(cd[2], cd[1], 0), DN], [Vector3(cd[0], cd[3], 0), Vector3(cd[2], cd[3], 0), U],
			[Vector3(cd[0], cd[1], 0), Vector3(cd[0], cd[3], 0), L], [Vector3(cd[2], cd[1], 0), Vector3(cd[2], cd[3], 0), R]]:
		q(b, g, "pc_skee_steel", xf, [e[0], e[1], e[1] + Vector3(0, 0, dz), e[0] + Vector3(0, 0, dz)], e[2], null, true)
	for lc in [Vector2(-0.245, 0.585), Vector2(-0.135, 0.585)]:
		var x0 = lc.x - 14 * 0.76 / 512.0; var x1 = lc.x + 14 * 0.76 / 512.0
		var y1 = lc.y + 26 * 0.52 / 352.0; var y0 = lc.y - 8 * 0.52 / 352.0
		q(b, g, "pc_skee_coinlamp" + str(num), xf, [Vector3(x0, y0, dz - 0.003), Vector3(x1, y0, dz - 0.003), Vector3(x1, y1, dz - 0.003), Vector3(x0, y1, dz - 0.003)], FW,
			[fw.call(x0, y0), fw.call(x1, y0), fw.call(x1, y1), fw.call(x0, y1)], true)
	# ticket slot bezel
	var ts = [0.12, 0.575, 0.28, 0.605]
	var bt = 0.008
	b.box(g, "pc_skee_chrome", Vector3((ts[0] + ts[2]) * 0.5, ts[3] + bt * 0.5, -0.005), Vector3(ts[2] - ts[0] + 2 * bt, bt, 0.01), xf, [], true)
	b.box(g, "pc_skee_chrome", Vector3((ts[0] + ts[2]) * 0.5, ts[1] - bt * 0.5, -0.005), Vector3(ts[2] - ts[0] + 2 * bt, bt, 0.01), xf, [], true)
	b.box(g, "pc_skee_chrome", Vector3(ts[0] - bt * 0.5, (ts[1] + ts[3]) * 0.5, -0.005), Vector3(bt, ts[3] - ts[1], 0.01), xf, [], true)
	b.box(g, "pc_skee_chrome", Vector3(ts[2] + bt * 0.5, (ts[1] + ts[3]) * 0.5, -0.005), Vector3(bt, ts[3] - ts[1], 0.01), xf, [], true)
	# a strip of tickets curling out of the slot and hanging down
	var tl = 0.17 + 0.05 * rng.randf()
	var tx = 0.20 + rng.randf_range(-0.03, 0.03)
	var tw = 0.014
	var path = []
	var N = 14
	for i in N + 1:
		var s = tl * i / N
		var p: Vector3
		if s < 0.04:
			var a = s / 0.04 * PI * 0.5
			p = Vector3(0, 0.590 - 0.025 * (1 - cos(a)), -0.004 - 0.025 * sin(a))
		else:
			var k = s - 0.04
			p = Vector3(0.004 * sin(k * 30.0), 0.565 - k, -0.029 + 0.06 * k * k)
		path.append(p)
	for i in N:
		var pa = path[i]; var pc = path[i + 1]
		var tang = (pc - pa).normalized()
		var tn = Vector3.RIGHT.cross(tang).normalized()
		var tw2 = Vector3(tw, 0, 0)
		var twist = Vector3(0, 0, 0.003 * sin(i * 0.9))
		var v0 = float(i) / N * tl / 0.22; var v1 = float(i + 1) / N * tl / 0.22
		q(b, g, "pc_skee_ticket", xf, [Vector3(tx, 0, 0) + pa - tw2 - twist, Vector3(tx, 0, 0) + pa + tw2 + twist,
			Vector3(tx, 0, 0) + pc + tw2 + twist, Vector3(tx, 0, 0) + pc - tw2 - twist], -tn,
			[Vector2(0, v0), Vector2(1, v0), Vector2(1, v1), Vector2(0, v1)], true)
	# START button on the cap's top, right side
	var sp = xf * Vector3(0.27, 0.915, 0.045)
	b.cur_color = Color("#141416")
	b.cyl(g, "vcolor", sp, 0.026, 0.025, 0.006, 16, true, false, true)
	b.cur_color = Color.WHITE
	b.cyl(g, "pc_skee_start", sp + Vector3(0, 0.006, 0), 0.019, 0.018, 0.010, 16, true, false, true)
	# lane number plate on the front face
	q(b, g, "pc_skee_numplate", xf, [Vector3(-0.025, 0.70, -0.002), Vector3(0.025, 0.70, -0.002), Vector3(0.025, 0.75, -0.002), Vector3(-0.025, 0.75, -0.002)], FW,
		[Vector2(c0, 1), Vector2(c1, 1), Vector2(c1, 0), Vector2(c0, 0)], true)

	b.cur_color = Color.WHITE
	# walk obstacle covering the footprint
	var k0 = xf * Vector3(-W * 0.5, 0, 0)
	var k1 = xf * Vector3(W * 0.5, 0, D)
	b.obst(["rect", min(k0.x, k1.x), min(k0.z, k1.z), max(k0.x, k1.x), max(k0.z, k1.z)])

## A UV sphere (smooth), equirect UVs, rotated by `yaw` so the balls differ.
static func sphere(b, s, xf, c, r, yaw):
	var LON = 10
	var LAT = 7
	for j in LAT:
		var t0 = PI * j / LAT; var t1 = PI * (j + 1) / LAT
		for i in LON:
			var a0 = TAU * i / LON + yaw; var a1 = TAU * (i + 1) / LON + yaw
			var n = [Vector3(sin(t0) * cos(a0), cos(t0), sin(t0) * sin(a0)), Vector3(sin(t0) * cos(a1), cos(t0), sin(t0) * sin(a1)),
				Vector3(sin(t1) * cos(a1), cos(t1), sin(t1) * sin(a1)), Vector3(sin(t1) * cos(a0), cos(t1), sin(t1) * sin(a0))]
			var p = []
			for v in n:
				p.append(c + v * r)
			var uv = [Vector2(float(i) / LON, float(j) / LAT), Vector2(float(i + 1) / LON, float(j) / LAT),
				Vector2(float(i + 1) / LON, float(j + 1) / LAT), Vector2(float(i) / LON, float(j + 1) / LAT)]
			var fn = (n[0] + n[1] + n[2] + n[3]).normalized()
			qn(b, s, xf, p, n, uv, fn)

const TINT = [Color(1, 1, 1), Color(0.95, 0.99, 1.03), Color(1.04, 0.97, 0.94), Color(0.98, 0.96, 0.98)]

## Material "pc_skee_<key>": fill m and return true, or return false for an unknown key.
## Textured emissives keep `emission` BLACK: Godot's ADD operator emits (emission + texture) * energy,
## so a white emission colour would wash the art out to white.
static func fill_mat(m, key, b):
	var n = int(key.right(1)) if key.right(1).is_valid_int() else 1
	var base = key.rstrip("1234") if key.begins_with("side") or key.begins_with("front") or key.begins_with("coinlamp") else key
	match base:
		"side":
			m.albedo_texture = b.tex("pc/skee_side.png"); m.albedo_color = TINT[n - 1]
			m.roughness = 0.42; m.metallic_specular = 0.55
		"front":
			m.albedo_texture = b.tex("pc/skee_front.png"); m.albedo_color = TINT[n - 1]
			m.roughness = 0.45; m.metallic_specular = 0.55
		"sidetext":
			m.albedo_texture = b.tex("pc/skee_sidetext.png"); m.roughness = 0.4
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"rail":
			m.albedo_texture = b.tex("pc/skee_rail.png"); m.roughness = 0.38; m.metallic_specular = 0.6
		"lane":
			m.albedo_texture = b.tex("pc/skee_lane.png"); m.roughness = 0.32; m.metallic_specular = 0.6
		"board":
			m.albedo_texture = b.tex("pc/skee_board.png"); m.roughness = 0.45
		"rim":
			m.albedo_color = Color("#e9e1cf"); m.roughness = 0.35
		"marquee":
			m.albedo_texture = b.tex("pc/skee_marquee.png"); m.roughness = 0.25
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.BLACK
			m.emission_energy_multiplier = 1.3
			m.set_meta("e_day", 1.3); m.set_meta("e_night", 1.3)
		"led":
			m.albedo_texture = b.tex("pc/skee_led.png"); m.roughness = 0.15
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.BLACK
			m.emission_energy_multiplier = 2.6
			m.set_meta("e_day", 2.6); m.set_meta("e_night", 2.6)
		"num":
			m.albedo_texture = b.tex("pc/skee_num.png"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.BLACK
			m.emission_energy_multiplier = 1.2
			m.set_meta("e_day", 1.2); m.set_meta("e_night", 1.2)
		"numplate":
			m.albedo_texture = b.tex("pc/skee_num.png"); m.roughness = 0.35; m.metallic = 0.3
		"tube":
			m.albedo_color = Color("#f4f1ea")
			m.emission_enabled = true; m.emission = Color("#fff3df"); m.emission_energy_multiplier = 0.9
			m.set_meta("e_day", 0.9); m.set_meta("e_night", 0.9)
		"beacon_on":
			m.albedo_color = Color("#ff8a10"); m.roughness = 0.2
			m.emission_enabled = true; m.emission = Color("#ff7a10"); m.emission_energy_multiplier = 4.0
			m.set_meta("e_day", 4.0); m.set_meta("e_night", 4.0)
		"beacon_off":
			m.albedo_color = Color("#b4500e"); m.roughness = 0.2
			m.emission_enabled = true; m.emission = Color("#ff7a10"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.25)
		"coinlamp":
			m.albedo_texture = b.tex("pc/skee_front.png")
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.BLACK
			m.emission_energy_multiplier = 2.2
			m.set_meta("e_day", 2.2); m.set_meta("e_night", 2.2)
		"start":
			m.albedo_color = Color("#ffd23a"); m.roughness = 0.25
			m.emission_enabled = true; m.emission = Color("#ffc020"); m.emission_energy_multiplier = 2.4
			m.set_meta("e_day", 2.4); m.set_meta("e_night", 2.4)
		"metal":
			m.albedo_texture = b.tex("pc/skee_metal.png"); m.albedo_color = Color(0.92, 0.92, 0.94)
			m.metallic = 0.6; m.roughness = 0.38
		"chrome":
			m.albedo_color = Color("#d8d8dc"); m.metallic = 0.95; m.roughness = 0.18
		"steel":
			m.albedo_color = Color("#3c3e42"); m.metallic = 0.6; m.roughness = 0.45
		"frame":
			m.albedo_color = Color("#2a2b2e"); m.metallic = 0.5; m.roughness = 0.5
		"mesh":
			m.albedo_texture = b.tex("pc/skee_mesh.png"); m.metallic = 0.6; m.roughness = 0.45
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"ticket":
			m.albedo_texture = b.tex("pc/skee_ticket.png"); m.roughness = 0.85
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"ball":
			m.albedo_texture = b.tex("pc/skee_ball.png"); m.roughness = 0.35
		"bumper":
			m.albedo_color = Color("#151515"); m.roughness = 0.75
		"trough":
			m.albedo_color = Color("#1c1b1a"); m.roughness = 0.6; m.metallic = 0.3
		"inner":
			m.albedo_color = Color("#14182a"); m.roughness = 0.8
		"dark":
			m.albedo_color = Color("#0e0e10"); m.roughness = 0.9
		"edge":
			m.albedo_color = Color("#161414"); m.roughness = 0.6
		"back":
			m.albedo_color = Color("#1e1c1c"); m.roughness = 0.85
		"plinth":
			m.albedo_color = Color("#111112"); m.roughness = 0.7
		"mqbody":
			m.albedo_color = Color("#151417"); m.roughness = 0.5
		_:
			return false
	return true
