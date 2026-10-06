## Pocket Change prop module `driver`: the two machines a 1995 mall arcade
## always had along a wall: the twin sit-down driving cabinet and the pinball
## machine. Contract: tools/stores/pocket_change/README.md. Textures are painted
## by paint_driver.py (tex/pc/driver_*.png). All titles and art are invented.
##
## opts: {"kind": "racer" | "pinball", "style": 0..1 (racer) | 0..2 (pinball)}
##
## Racer (1.74 x 1.95 x 2.06 m): two moulded vinyl seats on seat bases (coin
## doors on their rear faces, toward the player), footwell plates, pedal slope
## with gas/brake, steering wheels on columns, 4-speed shifters, START/VIEW
## buttons, a full-width console, two 26-inch CRTs behind a printed bezel,
## speaker grilles under the hood and a backlit marquee across the top.
## The player stands at o behind the seats; the screens are at z ~ 1.3.
##
## Pinball (0.72 x 1.40 x 1.90 m): standard-body cabinet on four legs with
## levellers, side art, side rails, lockdown bar, flipper buttons, plunger,
## start button, coin door; the 0.52 x 1.067 m playfield at 6.3 degrees under
## glass, with apron, flippers, slingshots, pop bumpers, a plastic ramp, a wire
## habitrail, standup targets, lane guides, lit inserts and a steel ball; the
## backbox with a backlit translight, speaker panel and orange 128x32 DMD.
##   tools/qa/preview.sh driver <out> "<cams>" '{"kind":"pinball","style":1}' lit

# ------------------------------------------------------------ racer constants
const RW = 1.74
const RD = 1.95
const RH = 2.06
const R_HW = 0.87          # outer half-width (side panels)
const R_IN = 0.851         # inner half-width (front panels between the sides)
# side profile (z, y), clockwise from the floor at the toe kick
const RP = [Vector2(0.86, 0.00), Vector2(0.86, 0.22), Vector2(1.08, 0.40), Vector2(1.08, 0.60),
	Vector2(0.90, 0.78), Vector2(0.96, 1.00), Vector2(1.24, 1.02), Vector2(1.40, 1.62),
	Vector2(1.18, 1.70), Vector2(1.14, 2.06), Vector2(1.62, 2.06), Vector2(1.95, 1.84), Vector2(1.95, 0.00)]
const SEATS = [-0.435, 0.435]
const SCR_W = 0.56         # CRT opening in the bezel (26-inch tube, 4:3)
const SCR_H = 0.43
const SCR_V = 0.32         # opening centre, metres up the bezel slope
# seat loft: centreline (z, y) from the front lip of the pan to the top of the back
const SEAT_PATH = [Vector2(0.70, 0.50), Vector2(0.60, 0.53), Vector2(0.43, 0.515), Vector2(0.29, 0.485),
	Vector2(0.215, 0.56), Vector2(0.165, 0.75), Vector2(0.13, 0.95), Vector2(0.12, 1.06)]
const SEAT_X = [-0.25, -0.235, -0.18, -0.10, 0.0, 0.10, 0.18, 0.235, 0.25]
const SEAT_H = [0.0, 0.06, 0.05, 0.006, 0.0, 0.006, 0.05, 0.06, 0.0]
const SEAT_BOL = [0.45, 0.5, 0.55, 0.5, 0.9, 1.0, 1.0, 0.85]

# ---------------------------------------------------------- pinball constants
const PW = 0.72
const PD = 1.40
const P_HW = 0.30          # cabinet outer half-width
const P_IN = 0.26          # inner half-width = playfield half-width
const P_Z0 = 0.03          # cabinet front
const P_Z1 = 1.30          # cabinet back
const P_YB = 0.53          # cabinet bottom
const P_YF = 0.93          # top of the sides at the front
const P_YR = 1.07          # top of the sides at the back
const PF_W = 0.52
const PF_L = 1.067         # 20.25 x 42 inch playfield
const PF_Z = 0.10          # playfield front edge (behind the lockdown bar)
const PF_DEPTH = 0.10      # playfield below the side tops
const GLASS_DROP = 0.015
const K = 0.52 / 0.60      # layout below is in "design" units of a 0.60 m field (paint_driver.py)
const BB = [1.17, 1.40, 1.05, 1.90]   # backbox z0, z1, y0, y1

## Footprint (width, depth) in metres.
static func footprint(opts = {}):
	if str(opts.get("kind", "racer")) == "pinball":
		return Vector2(PW, PD)
	return Vector2(RW, RD)

static func X(o, f):
	return Transform3D(Basis(f.cross(Vector3.UP), Vector3.UP, f), o)

static func build(b, g, o, f, opts = {}):
	var xf = X(o, f)
	var kind = str(opts.get("kind", "racer"))
	var st = int(opts.get("style", 0))
	var fp = footprint(opts)
	if kind == "pinball":
		build_pinball(b, g, xf, clampi(st, 0, 2))
	else:
		build_racer(b, g, xf, clampi(st, 0, 1))
	b.cur_color = Color.WHITE
	var c0 = xf * Vector3(-fp.x * 0.5, 0, 0)
	var c1 = xf * Vector3(fp.x * 0.5, 0, fp.y)
	b.obst(["rect", min(c0.x, c1.x), min(c0.z, c1.z), max(c0.x, c1.x), max(c0.z, c1.z)])

# ================================================================ helpers
## Planar face: origin P0, U = viewer's right, V = up (local), w x h metres;
## r = [u0, v0, u1, v1] sub-rectangle; uvr maps the full face (top at uvr.y).
static func face(b, g, m, xf, P0, U, V, w, h, r, uvr, dyn = false, off = 0.0):
	var nl = V.cross(U).normalized()
	var n = (xf.basis * nl).normalized()
	var pts = []
	var uvs = []
	for c in [[r[0], r[1]], [r[2], r[1]], [r[2], r[3]], [r[0], r[3]]]:
		pts.append(xf * (P0 + U * c[0] + V * c[1] + nl * off))
		uvs.append(Vector2(uvr.position.x + c[0] / w * uvr.size.x, uvr.position.y + (1.0 - c[1] / h) * uvr.size.y))
	b.quad(g, m, pts, n, uvs, dyn)

## A face with a row of rectangular holes (all holes share the same v range).
static func face_holes(b, g, m, xf, P0, U, V, w, h, holes, uvr):
	var v0 = holes[0][1]
	var v1 = holes[0][3]
	face(b, g, m, xf, P0, U, V, w, h, [0, 0, w, v0], uvr)
	face(b, g, m, xf, P0, U, V, w, h, [0, v1, w, h], uvr)
	var u = 0.0
	for hl in holes:
		face(b, g, m, xf, P0, U, V, w, h, [u, v0, hl[0], v1], uvr)
		u = hl[2]
	face(b, g, m, xf, P0, U, V, w, h, [u, v0, w, v1], uvr)

## Emit a quad with per-vertex (smooth) normals; p, n local.
static func sq(b, s, xf, p, n, uv):
	var P = []
	var N = []
	for i in 4:
		P.append(xf * p[i])
		N.append((xf.basis * n[i]).normalized())
	b._tri_n(s, [P[0], P[1], P[2]], [N[0], N[1], N[2]], [uv[0], uv[1], uv[2]], (N[0] + N[1] + N[2]).normalized())
	b._tri_n(s, [P[0], P[2], P[3]], [N[0], N[2], N[3]], [uv[0], uv[2], uv[3]], (N[0] + N[2] + N[3]).normalized())

## Cylinder / frustum along any local axis.
static func ocyl(b, g, m, xf, base, axis, r0, r1, seg, top = true, bot = false, dyn = true):
	var L = axis.length()
	var a = axis / L
	var t = a.cross(Vector3.UP)
	if t.length() < 0.2:
		t = a.cross(Vector3.RIGHT)
	t = t.normalized()
	var bt = a.cross(t).normalized()
	var s = b.st(g, m, dyn)
	var slope = (r0 - r1) / L
	var na = (xf.basis * a).normalized()
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var d0 = t * cos(a0) + bt * sin(a0)
		var d1 = t * cos(a1) + bt * sin(a1)
		var p = [base + d0 * r0, base + d1 * r0, base + a * L + d1 * r1, base + a * L + d0 * r1]
		var n0 = (d0 + a * slope).normalized()
		var n1 = (d1 + a * slope).normalized()
		sq(b, s, xf, p, [n0, n1, n1, n0], [Vector2(float(i) / seg, 1), Vector2(float(i + 1) / seg, 1), Vector2(float(i + 1) / seg, 0), Vector2(float(i) / seg, 0)])
		if top and r1 > 0.0:
			b.tri(s, xf * (base + a * L), xf * p[3], xf * p[2], Vector2(0.5, 0.5), Vector2(0.5 + 0.5 * cos(a0), 0.5 + 0.5 * sin(a0)), Vector2(0.5 + 0.5 * cos(a1), 0.5 + 0.5 * sin(a1)), na)
		if bot and r0 > 0.0:
			b.tri(s, xf * base, xf * p[0], xf * p[1], Vector2(0.5, 0.5), Vector2(0.5, 0.5), Vector2(0.5, 0.5), -na)

static func rod(b, g, m, xf, p0, p1, r, seg = 4, dyn = true):
	ocyl(b, g, m, xf, p0, p1 - p0, r, r, seg, false, false, dyn)

static func sphere(b, g, m, xf, C, r, nu = 10, nv = 7, dyn = true):
	var s = b.st(g, m, dyn)
	for i in nu:
		for j in nv:
			var p = []
			var n = []
			var uv = []
			for c in [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]]:
				var th = TAU * c[0] / nu
				var ph = PI * c[1] / nv - PI * 0.5
				var d = Vector3(cos(ph) * cos(th), sin(ph), cos(ph) * sin(th))
				p.append(C + d * r)
				n.append(d)
				uv.append(Vector2(float(c[0]) / nu, 1.0 - float(c[1]) / nv))
			sq(b, s, xf, p, n, uv)

static func torus(b, g, m, xf, C, ax, e1, e2, R, r, n1, n2, dyn = true):
	var s = b.st(g, m, dyn)
	for i in n1:
		for j in n2:
			var p = []
			var n = []
			var uv = []
			for c in [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]]:
				var a = TAU * c[0] / n1
				var d = e1 * cos(a) + e2 * sin(a)
				var bb = TAU * c[1] / n2
				var nn = d * cos(bb) + ax * sin(bb)
				p.append(C + d * R + nn * r)
				n.append(nn)
				uv.append(Vector2(float(c[0]) / n1 * 4.0, float(c[1]) / n2))
			sq(b, s, xf, p, n, uv)

## Oriented box: centre c, axes (ax, ay, az) local, size.
static func obox(b, g, m, xf, c, ax, ay, size, dyn = true, skip = []):
	var az = ax.cross(ay).normalized()
	b.box(g, m, Vector3.ZERO, size, xf * Transform3D(Basis(ax.normalized(), ay.normalized(), az), c), skip, dyn)

## Side panel: profile (z, y) extruded across x in [xin, xout]; outer face
## carries the side art (u along z, front at image-left on the right side).
static func extrude(b, g, xf, prof, xin, xout, mside, medge, zr, yr, dyn = false):
	var sgn = signf(xout - xin)
	var mirror = xout < 0.0
	var pts2 = PackedVector2Array(prof)
	var idx = Geometry2D.triangulate_polygon(pts2)
	var s = b.st(g, mside, dyn)
	var n = (xf.basis * Vector3(sgn, 0, 0)).normalized()
	for k in range(0, idx.size(), 3):
		var P = []
		var U = []
		for m in 3:
			var p = prof[idx[k + m]]
			P.append(xf * Vector3(xout, p.y, p.x))
			var u = (p.x - zr.x) / (zr.y - zr.x)
			if mirror:
				u = 1.0 - u
			U.append(Vector2(u, (yr.y - p.y) / (yr.y - yr.x)))
		b.tri(s, P[0], P[1], P[2], U[0], U[1], U[2], n)
	var area = 0.0
	for i in prof.size():
		var a = prof[i]
		var c = prof[(i + 1) % prof.size()]
		area += a.x * c.y - c.x * a.y
	for i in prof.size():
		var a = prof[i]
		var c = prof[(i + 1) % prof.size()]
		if a.y < 0.001 and c.y < 0.001:
			continue
		var e = c - a
		var L = e.length()
		e /= L
		var n2 = Vector2(e.y, -e.x) if area > 0.0 else Vector2(-e.y, e.x)
		var nn = (xf.basis * Vector3(0, n2.y, n2.x)).normalized()
		var x0 = xin - sgn * 0.002
		var x1 = xout + sgn * 0.002
		b.quad(g, medge, [xf * Vector3(x0, a.y, a.x), xf * Vector3(x1, a.y, a.x), xf * Vector3(x1, c.y, c.x), xf * Vector3(x0, c.y, c.x)], nn,
			[Vector2(0, 0), Vector2(0, 1), Vector2(L * 3.0, 1), Vector2(L * 3.0, 0)], dyn)

# ================================================================ racer
static func build_racer(b, g, xf, s):
	var S = str(s)
	# side panels with T-molding
	for sgn in [-1.0, 1.0]:
		extrude(b, g, xf, RP, sgn * R_IN, sgn * R_HW, "pc_driver_rside" + S, "pc_driver_tmold" + S, Vector2(0.86, 1.95), Vector2(0.0, RH))
	# panels between the sides, edge by edge round the profile
	var WI = R_IN * 2.0
	var X1 = Vector3(1, 0, 0)
	var kick = Rect2(0, 416.0 / 512.0, 1, 96.0 / 512.0)
	var console = Rect2(0, 288.0 / 512.0, 1, 128.0 / 512.0)
	var bezel = Rect2(0, 0, 1, 288.0 / 512.0)
	for i in RP.size() - 1:
		var a = RP[i]
		var c = RP[i + 1]
		var L = (c - a).length()
		var V = Vector3(0, c.y - a.y, c.x - a.x).normalized()
		var P0 = Vector3(-R_IN, a.y, a.x)
		var full = [0, 0, WI, L]
		match i:
			0, 2:
				face(b, g, "pc_driver_rpanel" + S, xf, P0, X1, V, WI, L, full, kick)
			1:
				face(b, g, "pc_driver_diamond", xf, P0, X1, V, WI, L, full, Rect2(0, 0, WI * 3.0, L * 3.0))
			4:
				face(b, g, "pc_driver_rpanel" + S, xf, P0, X1, V, WI, L, full, console)
			6:
				var holes = []
				for sx in SEATS:
					var cu = sx + R_IN
					holes.append([cu - SCR_W * 0.5, SCR_V - SCR_H * 0.5, cu + SCR_W * 0.5, SCR_V + SCR_H * 0.5])
				face_holes(b, g, "pc_driver_rpanel" + S, xf, P0, X1, V, WI, L, holes, bezel)
				racer_screens(b, g, xf, P0, X1, V, holes, S)
			7:
				face(b, g, "pc_driver_lam", xf, P0, X1, V, WI, L, full, Rect2(0, 0, WI, L))
				for sx in SEATS:
					var cu = sx + R_IN
					face(b, g, "pc_driver_grille", xf, P0, X1, V, WI, L, [cu - 0.24, 0.035, cu + 0.24, L - 0.035], Rect2(0, 0, WI * 6.0, L * 6.0), false, 0.004)
			8:
				face(b, g, "pc_driver_rmarq" + S, xf, P0, X1, V, WI, L, full, Rect2(0, 0, 1, 1))
				# aluminium trims along the marquee's top and bottom edges
				var N = V.cross(X1).normalized()
				for e in [[a, -1.0], [c, 1.0]]:
					var cc = Vector3(0, e[0].y, e[0].x) + N * 0.012 + V * (0.006 * e[1])
					obox(b, g, "pc_driver_steel", xf, cc, X1, V, Vector3(RW + 0.004, 0.022, 0.03), false)
			_:
				face(b, g, "pc_driver_lam", xf, P0, X1, V, WI, L, full, Rect2(0, 0, WI, L))
	for pi in 2:
		racer_seat(b, g, xf, SEATS[pi], S)
		racer_controls(b, g, xf, SEATS[pi], S, pi)

static func racer_screens(b, g, xf, P0, U, V, holes, S):
	var N = V.cross(U).normalized()
	var DEP = 0.048
	for pi in holes.size():
		var hl = holes[pi]
		var c00 = P0 + U * hl[0] + V * hl[1]
		var c10 = P0 + U * hl[2] + V * hl[1]
		var c11 = P0 + U * hl[2] + V * hl[3]
		var c01 = P0 + U * hl[0] + V * hl[3]
		# black tunnel from the bezel to the tube
		for e in [[c00, c10, V], [c10, c11, -U], [c11, c01, -V], [c01, c00, U]]:
			b.quad(g, "pc_driver_black", [xf * e[0], xf * e[1], xf * (e[1] - N * DEP), xf * (e[0] - N * DEP)], (xf.basis * e[2]).normalized(),
				[Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
		# the tube face: bulged grid
		var NU = 8
		var NV = 6
		var sst = b.st(g, "pc_driver_rscr" + S, false)
		for iu in NU:
			for iv in NV:
				var p = []
				var n = []
				var uv = []
				for c in [[iu, iv], [iu + 1, iv], [iu + 1, iv + 1], [iu, iv + 1]]:
					var tu = float(c[0]) / NU
					var tv = float(c[1]) / NV
					var t = tu * 2.0 - 1.0
					var r = tv * 2.0 - 1.0
					var d = -DEP + 0.024 * (1.0 - 0.5 * (t * t + r * r))
					p.append(P0 + U * lerpf(hl[0], hl[2], tu) + V * lerpf(hl[1], hl[3], tv) + N * d)
					n.append((N - U * t * 0.25 - V * r * 0.2).normalized())
					uv.append(Vector2(pi * 0.5 + tu * 0.5, 1.0 - tv))
				sq(b, sst, xf, p, n, uv)
		# glass over the opening
		b.quad(g, "pc_driver_glass", [xf * (c00 + N * 0.002), xf * (c10 + N * 0.002), xf * (c11 + N * 0.002), xf * (c01 + N * 0.002)], (xf.basis * N).normalized(),
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)

static func racer_seat(b, g, xf, sx, S):
	# seat base: rear face (toward the player) with the coin door, sides with art
	var z0 = 0.06
	var z1 = 0.72
	var hb = 0.40
	var bw = 0.25
	var full = Rect2(0, 0, 1, 1)
	face(b, g, "pc_driver_rbase" + S, xf, Vector3(sx - bw, 0, z0), Vector3(1, 0, 0), Vector3.UP, bw * 2, hb, [0, 0, bw * 2, hb], full)
	face(b, g, "pc_driver_rbase" + S, xf, Vector3(sx + bw, 0, z0), Vector3(0, 0, 1), Vector3.UP, z1 - z0, hb, [0, 0, z1 - z0, hb], full)
	face(b, g, "pc_driver_rbase" + S, xf, Vector3(sx - bw, 0, z1), Vector3(0, 0, -1), Vector3.UP, z1 - z0, hb, [0, 0, z1 - z0, hb], full)
	face(b, g, "pc_driver_lam", xf, Vector3(sx - bw, hb, z0), Vector3(1, 0, 0), Vector3(0, 0, 1), bw * 2, z1 - z0, [0, 0, bw * 2, z1 - z0], Rect2(0, 0, 0.5, 0.66))
	# corner T-molding on the base's vertical edges and top edges
	for cx in [sx - bw, sx + bw]:
		obox(b, g, "pc_driver_tmold" + S, xf, Vector3(cx, hb * 0.5, z0), Vector3(1, 0, 0), Vector3.UP, Vector3(0.016, hb, 0.016), false)
	obox(b, g, "pc_driver_tmold" + S, xf, Vector3(sx, hb, z0), Vector3(1, 0, 0), Vector3.UP, Vector3(bw * 2 + 0.016, 0.016, 0.016), false)
	# coin door on the rear face
	var cw = 0.24
	var ch = 0.27
	var cy = 0.07
	obox(b, g, "pc_driver_black", xf, Vector3(sx, cy + ch * 0.5, z0 - 0.004), Vector3(1, 0, 0), Vector3.UP, Vector3(cw, ch, 0.008), false, ["+z"])
	face(b, g, "pc_driver_coin", xf, Vector3(sx - cw * 0.5, cy, z0 - 0.0085), Vector3(1, 0, 0), Vector3.UP, cw, ch, [0, 0, cw, ch], full)
	coin_lamps(b, g, xf, Vector3(sx - cw * 0.5, cy, z0 - 0.0095), Vector3(1, 0, 0), Vector3.UP, cw, ch)
	# seat slider / mount and the footwell plate to the pedals
	b.box(g, "pc_driver_black", Vector3(sx, 0.43, 0.43), Vector3(0.34, 0.06, 0.42), xf)
	b.box(g, "pc_driver_diamond", Vector3(sx, 0.02, (z1 + 0.86) * 0.5), Vector3(bw * 2, 0.04, 0.86 - z1), xf)
	# moulded bucket seat: vinyl front surface + fibreglass shell, lofted
	var NI = SEAT_PATH.size()
	var NJ = SEAT_X.size()
	var nrm = []
	var arc = [0.0]
	for i in NI:
		var t = SEAT_PATH[min(i + 1, NI - 1)] - SEAT_PATH[max(i - 1, 0)]
		t = t.normalized()
		nrm.append(Vector2(t.y, -t.x))   # (z, y): toward the sitter
		if i > 0:
			arc.append(arc[i - 1] + (SEAT_PATH[i] - SEAT_PATH[i - 1]).length())
	var F = []
	var B = []
	for i in NI:
		var rowf = []
		var rowb = []
		var p = SEAT_PATH[i]
		var n = nrm[i]
		var wsc = lerpf(1.0, 0.9, float(i) / (NI - 1)) if i > 3 else 1.0
		for j in NJ:
			var x = SEAT_X[j] * wsc
			var h = SEAT_H[j] * SEAT_BOL[i]
			rowf.append(Vector3(sx + x, p.y + n.y * h, p.x + n.x * h))
			var hb2 = -0.04 - 0.015 * (1.0 - pow(SEAT_X[j] / 0.25, 2))
			rowb.append(Vector3(sx + x, p.y + n.y * hb2, p.x + n.x * hb2))
		F.append(rowf)
		B.append(rowb)
	seat_surface(b, g, xf, "pc_driver_seat" + S, F, nrm, arc, 1.0)
	seat_surface(b, g, xf, "pc_driver_seatback" + S, B, nrm, arc, -1.0)
	# edges: both sides, the top of the back and the front lip of the pan
	var es = b.st(g, "pc_driver_shell" + S, false)
	for i in NI - 1:
		for j in [0, NJ - 1]:
			var sd = -1.0 if j == 0 else 1.0
			var n = Vector3(sd, 0, 0)
			sq(b, es, xf, [F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]], [n, n, n, n], [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
	for e in [[NI - 1, 1.0], [0, -1.0]]:
		var i = e[0]
		var t = (SEAT_PATH[NI - 1] - SEAT_PATH[NI - 2]) if i == NI - 1 else (SEAT_PATH[0] - SEAT_PATH[1])
		t = t.normalized()
		var n = Vector3(0, t.y, t.x)
		for j in NJ - 1:
			sq(b, es, xf, [F[i][j], F[i][j + 1], B[i][j + 1], B[i][j]], [n, n, n, n], [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])

## Grid surface with smooth normals; side = +1 faces the sitter, -1 the shell's back.
static func seat_surface(b, g, xf, m, G, nrm, arc, side):
	var NI = G.size()
	var NJ = G[0].size()
	var N = []
	for i in NI:
		var row = []
		for j in NJ:
			var du = G[i][min(j + 1, NJ - 1)] - G[i][max(j - 1, 0)]
			var dv = G[min(i + 1, NI - 1)][j] - G[max(i - 1, 0)][j]
			var n = du.cross(dv).normalized()
			var ref = Vector3(0, nrm[i].y, nrm[i].x) * side
			if n.dot(ref) < 0.0:
				n = -n
			row.append(n)
		N.append(row)
	var s = b.st(g, m, false)
	for i in NI - 1:
		for j in NJ - 1:
			var uv = []
			for c in [[i, j], [i, j + 1], [i + 1, j + 1], [i + 1, j]]:
				if side > 0.0:
					uv.append(Vector2((SEAT_X[c[1]] + 0.25) / 0.5, arc[c[0]] / 1.2))
				else:
					# shell back: rbase art across the backrest (top of image at the top edge)
					uv.append(Vector2(1.0 - (SEAT_X[c[1]] + 0.25) / 0.5, 1.0 - (arc[c[0]] - arc[3]) / (arc[arc.size() - 1] - arc[3])))
			sq(b, s, xf, [G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]], [N[i][j], N[i][j + 1], N[i + 1][j + 1], N[i + 1][j]], uv)

## Lit reject buttons over the coin door's painted PUSH buttons (texture 256x288).
static func coin_lamps(b, g, xf, P0, U, V, cw, ch):
	var nl = V.cross(U).normalized()
	for cx in [78.0, 178.0]:
		var u0 = (cx - 17.0) / 256.0
		var u1 = (cx + 17.0) / 256.0
		var v0 = 84.0 / 288.0
		var v1 = 118.0 / 288.0
		var pts = []
		var uvs = []
		for c in [[u0, v1], [u1, v1], [u1, v0], [u0, v0]]:
			pts.append(xf * (P0 + U * (c[0] * cw) + V * ((1.0 - c[1]) * ch) + nl * 0.004))
			uvs.append(Vector2(c[0], c[1]))
		b.quad(g, "pc_driver_coinlit", pts, (xf.basis * nl).normalized(), uvs, true)
		# coin slot bezel (chrome) above each lamp
		var sc = P0 + U * (cx / 256.0 * cw) + V * ((1.0 - 58.0 / 288.0) * ch) + nl * 0.004
		obox(b, g, "pc_driver_chrome", xf, sc, U, V, Vector3(0.022, 0.04, 0.008), true)
		obox(b, g, "pc_driver_black", xf, sc + nl * 0.0045, U, V, Vector3(0.004, 0.028, 0.002), true)
	# lock
	var lc = P0 + U * (0.5 * cw) + V * ((1.0 - 193.0 / 288.0) * ch)
	ocyl(b, g, "pc_driver_chrome", xf, lc, nl * 0.012, 0.011, 0.011, 10, true, false, true)

static func racer_controls(b, g, xf, sx, S, pi):
	var e = RP[4]
	var f = RP[5]
	var V = Vector3(0, f.y - e.y, f.x - e.x).normalized()
	var U = Vector3(1, 0, 0)
	var N = V.cross(U).normalized()            # console face normal, toward the driver
	var LF = (f - e).length()
	var face0 = Vector3(sx, e.y, e.x)
	# steering column and wheel
	var nw = Vector3(0, 0.42, -0.91).normalized()
	var C = Vector3(sx, 0.875, 0.80)
	var colbase = C - nw * 0.16
	ocyl(b, g, "pc_driver_black", xf, colbase, nw * 0.13, 0.045, 0.032, 12, false, false, true)
	ocyl(b, g, "pc_driver_wheel", xf, C - nw * 0.035, nw * 0.045, 0.045, 0.04, 14, true, false, true)
	b.cur_color = Color("#d82820") if S == "0" else Color("#f0c818")
	ocyl(b, g, "vcolor", xf, C + nw * 0.009, nw * 0.003, 0.032, 0.032, 14, true, false, true)
	b.cur_color = Color.WHITE
	var e1 = Vector3(1, 0, 0)
	var e2 = nw.cross(e1).normalized()
	if e2.y < 0.0:
		e2 = -e2
	var R = 0.15
	torus(b, g, "pc_driver_wheel", xf, C, nw, e1, e2, R, 0.017, 22, 6)
	for ang in [0.0, PI, PI * 1.5]:
		var d = e1 * cos(ang) + e2 * sin(ang)
		obox(b, g, "pc_driver_spoke", xf, C + d * (R * 0.55) - nw * 0.008, d, nw.cross(d), Vector3(R * 0.82, 0.04, 0.012))
	# 4-speed shifter right of the wheel: gate plate, boot, lever, knob
	var sb = face0 + Vector3(0.25, 0, 0) + V * (LF * 0.45)
	obox(b, g, "pc_driver_chrome", xf, sb + N * 0.004, U, V, Vector3(0.09, 0.10, 0.008))
	var lev = (N * 0.85 + V * 0.53).normalized()
	ocyl(b, g, "pc_driver_black", xf, sb + N * 0.006, lev * 0.06, 0.035, 0.014, 10, false, false, true)
	rod(b, g, "pc_driver_chrome", xf, sb + N * 0.05, sb + N * 0.006 + lev * 0.16, 0.007, 8)
	sphere(b, g, "pc_driver_knob", xf, sb + N * 0.006 + lev * 0.18, 0.026, 10, 7)
	# START (lit) and VIEW buttons left of the wheel
	var bx = face0 + Vector3(-0.24, 0, 0)
	var stp = bx + V * (LF * 0.45)
	ocyl(b, g, "pc_driver_chrome", xf, stp, N * 0.006, 0.024, 0.024, 14, true, false, true)
	ocyl(b, g, "pc_driver_lampstart", xf, stp + N * 0.006, N * 0.008, 0.018, 0.017, 14, true, false, true)
	var vwp = bx + V * (LF * 0.80)
	ocyl(b, g, "pc_driver_chrome", xf, vwp, N * 0.005, 0.017, 0.017, 12, true, false, true)
	ocyl(b, g, "pc_driver_lampview", xf, vwp + N * 0.005, N * 0.007, 0.013, 0.012, 12, true, false, true)
	# pedals on the slope: brake (left), gas (right), with hinge blocks
	var pb = RP[1]
	var pc = RP[2]
	var sl = Vector3(0, pc.y - pb.y, pc.x - pb.x).normalized()
	var sn = sl.cross(U).normalized()
	var up = Vector3(0, 0.87, 0.5)
	for pd in [[-0.075, 0.08, 0.12, 0.35], [0.075, 0.09, 0.20, 0.30]]:
		var base = Vector3(sx + pd[0], lerpf(pb.y, pc.y, pd[3]), lerpf(pb.x, pc.x, pd[3]))
		var c = base + sn * 0.035 + up * (pd[2] * 0.5)
		obox(b, g, "pc_driver_diamond", xf, c, U, up, Vector3(pd[1], pd[2], 0.012))
		obox(b, g, "pc_driver_black", xf, base + sn * 0.02, U, sl, Vector3(pd[1] * 0.6, 0.05, 0.04))

# ================================================================ pinball
static func yt(z):
	return P_YF + (z - P_Z0) * (P_YR - P_YF) / (P_Z1 - P_Z0)

## Playfield frame: local (px, h, pz) -> cabinet local.
static func pf_xf(xf):
	var th = atan2(P_YR - P_YF, P_Z1 - P_Z0)
	var Zd = Vector3(0, sin(th), cos(th))
	var Nn = Vector3(0, cos(th), -sin(th))
	var O = Vector3(0, yt(PF_Z) - PF_DEPTH, PF_Z)
	return xf * Transform3D(Basis(Vector3(1, 0, 0), Nn, Zd), O)

## design units (0.60 m field) -> playfield metres
static func D(px, pz, h = 0.0):
	return Vector3(px * K, h, pz)

## playfield texture pixel (512x1024) <-> playfield metres
static func pix(px, pz):
	return Vector2((px + 0.30) / 0.60 * 512.0, (1.0 - pz / PF_L) * 1024.0)

static func unpix(p, h = 0.0):
	return Vector3((p.x / 512.0 - 0.5) * PF_W, h, (1.0 - p.y / 1024.0) * PF_L)

static func build_pinball(b, g, xf, s):
	var S = str(s)
	var cab = ["#1a1a50", "#08485c", "#2a0c08"][s]
	# --- cabinet sides, front, back, bottom
	var prof = [Vector2(P_Z0, P_YB), Vector2(P_Z0, P_YF), Vector2(P_Z1, P_YR), Vector2(P_Z1, P_YB)]
	for sgn in [-1.0, 1.0]:
		extrude(b, g, xf, prof, sgn * P_IN, sgn * P_HW, "pc_driver_pside" + S, "pc_driver_pcab" + S, Vector2(P_Z0, P_Z1), Vector2(P_YB, P_YR))
	var X1 = Vector3(1, 0, 0)
	var WI = P_IN * 2.0
	face(b, g, "pc_driver_pside" + S, xf, Vector3(-P_IN, P_YB, P_Z0), X1, Vector3.UP, WI, P_YF - P_YB, [0, 0, WI, P_YF - P_YB], Rect2(0.70, 0.30, 0.20, 0.70))
	face(b, g, "pc_driver_lam", xf, Vector3(P_IN, P_YB, P_Z1), -X1, Vector3.UP, WI, P_YR - P_YB, [0, 0, WI, P_YR - P_YB], Rect2(0, 0, WI, 0.54))
	face(b, g, "pc_driver_lam", xf, Vector3(-P_IN, P_YB, P_Z1), X1, Vector3(0, 0, -1), WI, P_Z1 - P_Z0, [0, 0, WI, P_Z1 - P_Z0], Rect2(0, 0, WI, 1.27))
	# side rails along the top edges
	var th = atan2(P_YR - P_YF, P_Z1 - P_Z0)
	var Zd = Vector3(0, sin(th), cos(th))
	var Nn = Vector3(0, cos(th), -sin(th))
	var LR = (P_Z1 - P_Z0) / cos(th)
	for sgn in [-1.0, 1.0]:
		var zc = (P_Z0 + P_Z1) * 0.5
		obox(b, g, "pc_driver_rail" + S, xf, Vector3(sgn * (P_HW - 0.012), yt(zc) + 0.009, zc), X1, Nn, Vector3(0.03, 0.018, LR), false)
	# lockdown bar across the front top
	b.box(g, "pc_driver_lockbar", Vector3(0, P_YF + 0.011, (P_Z0 + PF_Z) * 0.5 - 0.004), Vector3(P_HW * 2 + 0.01, 0.022, PF_Z - P_Z0 + 0.012), xf)
	ocyl(b, g, "pc_driver_chrome", xf, Vector3(0, P_YF + 0.014, P_Z0 - 0.009), Vector3(0, 0, -0.006), 0.007, 0.007, 8, true, false, true)
	# legs (bolted to the corners, splayed front/back), bolts and levellers
	for lz in [[0.10, 0.045], [1.22, 1.29]]:
		for sgn in [-1.0, 1.0]:
			var top = Vector3(sgn * (P_HW + 0.03), P_YB + 0.20, lz[0])
			var bot = Vector3(sgn * (P_HW + 0.03), 0.045, lz[1])
			leg(b, g, xf, top, bot, 0.06, 0.048, "pc_driver_legs" + S)
			for by in [0.06, 0.15]:
				var bp = top.lerp(bot, by / (top.y - bot.y)) + Vector3(sgn * 0.031, 0, 0)
				ocyl(b, g, "pc_driver_chrome", xf, bp, Vector3(sgn * 0.006, 0, 0), 0.009, 0.008, 8, true, false, true)
			ocyl(b, g, "pc_driver_chrome", xf, bot + Vector3(0, -0.03, 0), Vector3(0, 0.032, 0), 0.006, 0.006, 6, false, false, true)
			ocyl(b, g, "pc_driver_black", xf, bot + Vector3(0, -0.045, 0), Vector3(0, 0.016, 0), 0.02, 0.018, 12, true, false, true)
	# front: coin door, start button, plunger; flipper buttons on the sides
	var cw = 0.284
	var ch = 0.32
	var cy = 0.565
	obox(b, g, "pc_driver_black", xf, Vector3(0, cy + ch * 0.5, P_Z0 - 0.004), X1, Vector3.UP, Vector3(cw, ch, 0.008), false, ["+z"])
	face(b, g, "pc_driver_coin", xf, Vector3(-cw * 0.5, cy, P_Z0 - 0.0085), X1, Vector3.UP, cw, ch, [0, 0, cw, ch], Rect2(0, 0, 1, 1))
	coin_lamps(b, g, xf, Vector3(-cw * 0.5, cy, P_Z0 - 0.0095), X1, Vector3.UP, cw, ch)
	ocyl(b, g, "pc_driver_chrome", xf, Vector3(-0.20, 0.885, P_Z0), Vector3(0, 0, -0.006), 0.022, 0.022, 14, true, false, true)
	ocyl(b, g, "pc_driver_lampstart", xf, Vector3(-0.20, 0.885, P_Z0 - 0.006), Vector3(0, 0, -0.008), 0.016, 0.015, 14, true, false, true)
	var plx = 0.2765 * K
	obox(b, g, "pc_driver_chrome", xf, Vector3(plx, 0.86, P_Z0 - 0.003), X1, Vector3.UP, Vector3(0.06, 0.07, 0.006))
	rod(b, g, "pc_driver_chrome", xf, Vector3(plx, 0.86, P_Z0 - 0.005), Vector3(plx, 0.86, P_Z0 - 0.075), 0.0055, 8)
	ocyl(b, g, "pc_driver_spring", xf, Vector3(plx, 0.86, P_Z0 - 0.006), Vector3(0, 0, -0.03), 0.011, 0.011, 8, false, false, true)
	ocyl(b, g, "pc_driver_plunger" + S, xf, Vector3(plx, 0.86, P_Z0 - 0.075), Vector3(0, 0, -0.04), 0.012, 0.017, 12, true, true, true)
	for sgn in [-1.0, 1.0]:
		var fbp = Vector3(sgn * P_HW, 0.855, 0.13)
		ocyl(b, g, "pc_driver_chrome", xf, fbp, Vector3(sgn * 0.004, 0, 0), 0.022, 0.022, 14, true, false, true)
		ocyl(b, g, "pc_driver_fbtn" + S, xf, fbp + Vector3(sgn * 0.004, 0, 0), Vector3(sgn * 0.016, 0, 0), 0.016, 0.015, 14, true, false, true)
	build_playfield(b, g, xf, s)
	build_backbox(b, g, xf, s)

static func leg(b, g, xf, top, bot, w0, w1, m):
	var corners = [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]
	for i in 4:
		var a = corners[i]
		var c = corners[(i + 1) % 4]
		var p0 = bot + Vector3(a.x * w1 * 0.5, 0, a.y * w1 * 0.5)
		var p1 = bot + Vector3(c.x * w1 * 0.5, 0, c.y * w1 * 0.5)
		var p2 = top + Vector3(c.x * w0 * 0.5, 0, c.y * w0 * 0.5)
		var p3 = top + Vector3(a.x * w0 * 0.5, 0, a.y * w0 * 0.5)
		var mid = (a + c) * 0.5
		var n = (xf.basis * Vector3(mid.x, 0, mid.y)).normalized()
		b.quad(g, m, [xf * p0, xf * p1, xf * p2, xf * p3], n, [Vector2(0, 1), Vector2(0.1, 1), Vector2(0.1, 0), Vector2(0, 0)])
	b.quad(g, m, [xf * (bot + Vector3(-w1 * 0.5, 0, -w1 * 0.5)), xf * (bot + Vector3(w1 * 0.5, 0, -w1 * 0.5)), xf * (bot + Vector3(w1 * 0.5, 0, w1 * 0.5)), xf * (bot + Vector3(-w1 * 0.5, 0, w1 * 0.5))],
		(xf.basis * Vector3.DOWN).normalized(), [Vector2(0, 0), Vector2(0.1, 0), Vector2(0.1, 0.1), Vector2(0, 0.1)])

static func build_playfield(b, g, xf, s):
	var S = str(s)
	var P = pf_xf(xf)
	var hw = PF_W * 0.5
	var HG = PF_DEPTH - GLASS_DROP
	# playfield (static, lit by its GI)
	b.quad(g, "pc_driver_pfield" + S, [P * Vector3(-hw, 0, 0), P * Vector3(hw, 0, 0), P * Vector3(hw, 0, PF_L), P * Vector3(-hw, 0, PF_L)],
		(P.basis * Vector3.UP).normalized(), [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	# interior walls up to the side tops; back wall under the backbox
	var top = PF_DEPTH + 0.002
	for sgn in [-1.0, 1.0]:
		b.quad(g, "pc_driver_wall", [P * Vector3(sgn * hw, 0, 0), P * Vector3(sgn * hw, 0, PF_L + 0.02), P * Vector3(sgn * hw, top, PF_L + 0.02), P * Vector3(sgn * hw, top, 0)],
			(P.basis * Vector3(-sgn, 0, 0)).normalized(), [Vector2(0, 1), Vector2(PF_L * 4, 1), Vector2(PF_L * 4, 0), Vector2(0, 0)])
	b.quad(g, "pc_driver_wall", [P * Vector3(-hw, 0, PF_L), P * Vector3(hw, 0, PF_L), P * Vector3(hw, top + 0.03, PF_L), P * Vector3(-hw, top + 0.03, PF_L)],
		(P.basis * Vector3(0, 0, -1)).normalized(), [Vector2(0, 1), Vector2(2, 1), Vector2(2, 0), Vector2(0, 0)])
	b.quad(g, "pc_driver_wall", [P * Vector3(-hw, 0, 0), P * Vector3(hw, 0, 0), P * Vector3(hw, top, 0), P * Vector3(-hw, top, 0)],
		(P.basis * Vector3(0, 0, 1)).normalized(), [Vector2(0, 1), Vector2(2, 1), Vector2(2, 0), Vector2(0, 0)])
	# apron: top plate with the instruction cards, back lip
	var az = 0.135
	var ah = 0.03
	b.quad(g, "pc_driver_apron", [P * Vector3(-hw, ah, 0), P * Vector3(hw, ah, 0), P * Vector3(hw, ah, az), P * Vector3(-hw, ah, az)],
		(P.basis * Vector3.UP).normalized(), [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	b.quad(g, "pc_driver_black", [P * Vector3(-hw, 0, az), P * Vector3(hw, 0, az), P * Vector3(hw, ah, az), P * Vector3(-hw, ah, az)],
		(P.basis * Vector3(0, 0, 1)).normalized(), [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	# top arch (orbit guide) and shooter lane wall
	var arch_c = Vector3(0, 0, PF_L - hw)
	var NA = 14
	for i in NA:
		var a0 = PI * i / NA
		var a1 = PI * (i + 1) / NA
		var p0 = arch_c + Vector3(cos(a0) * hw, 0, sin(a0) * hw)
		var p1 = arch_c + Vector3(cos(a1) * hw, 0, sin(a1) * hw)
		var n = -Vector3(cos((a0 + a1) * 0.5), 0, sin((a0 + a1) * 0.5))
		b.quad(g, "pc_driver_steel", [P * p0, P * p1, P * (p1 + Vector3(0, 0.035, 0)), P * (p0 + Vector3(0, 0.035, 0))], (P.basis * n).normalized(),
			[Vector2(0, 1), Vector2(0.2, 1), Vector2(0.2, 0), Vector2(0, 0)])
	b.box(g, "pc_driver_wall", D(0.253, 0.47, 0.016), Vector3(0.008, 0.032, 0.80), P)
	# glass (dynamic, transparent)
	b.quad(g, "pc_driver_glass", [P * Vector3(-hw, HG, -0.01), P * Vector3(hw, HG, -0.01), P * Vector3(hw, HG, PF_L + 0.01), P * Vector3(-hw, HG, PF_L + 0.01)],
		(P.basis * Vector3.UP).normalized(), [Vector2(0, 2), Vector2(1, 2), Vector2(1, 0), Vector2(0, 0)], true)
	# flippers
	var cx = -0.0235
	for sgn in [-1.0, 1.0]:
		var piv = Vector2((cx + sgn * 0.105) * K, 0.215)
		var dir = Vector2(-sgn * cos(deg_to_rad(28.0)), -sin(deg_to_rad(28.0)))
		flipper(b, g, P, piv, piv + dir * 0.072)
	# slingshots, inlane guides, posts
	for side in [-1.0, 1.0]:
		var tri = [Vector2(-0.20, 0.29), Vector2(-0.20, 0.40), Vector2(-0.135, 0.30)]
		var pts = []
		for t in tri:
			var x = t.x if side < 0 else (2.0 * cx - t.x)
			pts.append(Vector2(x * K, t.y))
		slingshot(b, g, P, pts, S)
		var gx = [-0.245, -0.205] if side < 0 else [2.0 * cx + 0.245, 2.0 * cx + 0.205]
		for x in gx:
			b.cur_color = Color("#c8c8cc")
			b.box(g, "vcolor", D(x, 0.31, 0.012), Vector3(0.005, 0.024, 0.18), P, [], true)
			ocyl(b, g, "pc_driver_chrome", P, D(x, 0.40), Vector3(0, 0.035, 0), 0.005, 0.005, 6, true, false, true)
			b.cur_color = Color("#f2f0ea")
			ocyl(b, g, "vcolor", P, D(x, 0.40, 0.012), Vector3(0, 0.012, 0), 0.011, 0.011, 10, true, false, true)
		# angled inlane guide down to the flipper
		var g0 = D(gx[1], 0.29)
		var piv = D(cx + side * 0.105, 0.215)
		var g1 = piv + Vector3(side * 0.014, 0, 0.012)
		var dv = g1 - g0
		b.cur_color = Color("#c8c8cc")
		obox(b, g, "vcolor", P, (g0 + g1) * 0.5 + Vector3(0, 0.012, 0), Vector3(dv.z, 0, -dv.x).normalized(), Vector3.UP, Vector3(0.005, 0.024, dv.length()))
		b.cur_color = Color.WHITE
	# pop bumpers
	for bp in [Vector2(-0.11, 0.80), Vector2(0.05, 0.82), Vector2(-0.03, 0.705)]:
		var c = D(bp.x, bp.y)
		ocyl(b, g, "pc_driver_black", P, c, Vector3(0, 0.006, 0), 0.042, 0.042, 12, true, false, true)
		b.cur_color = Color("#f4f2ea")
		ocyl(b, g, "vcolor", P, c + Vector3(0, 0.006, 0), Vector3(0, 0.03, 0), 0.026, 0.026, 10, false, false, true)
		b.cur_color = Color("#d02a20")
		ocyl(b, g, "vcolor", P, c + Vector3(0, 0.012, 0), Vector3(0, 0.005, 0), 0.04, 0.04, 12, true, false, true)
		b.cur_color = Color.WHITE
		ocyl(b, g, "pc_driver_bcap" + S, P, c + Vector3(0, 0.036, 0), Vector3(0, 0.024, 0), 0.036, 0.032, 14, true, false, true)
	# top lane guides
	for x in [-0.15, -0.07, 0.01, 0.09]:
		b.cur_color = Color("#c8c8cc")
		b.box(g, "vcolor", D(x, 0.97, 0.012), Vector3(0.006, 0.024, 0.07), P, [], true)
	b.cur_color = Color.WHITE
	# standup targets (right side)
	var tc = ["#f0d020", "#f0d020", "#f03040"]
	for i in 3:
		b.cur_color = Color(tc[i])
		b.box(g, "vcolor", D(0.215, 0.50 + i * 0.06, 0.018), Vector3(0.008, 0.032, 0.026), P, [], true)
		b.cur_color = Color("#202020")
		b.box(g, "vcolor", D(0.225, 0.50 + i * 0.06, 0.012), Vector3(0.01, 0.024, 0.012), P, [], true)
	b.cur_color = Color.WHITE
	# plastic ramp: entrance mid-left, climbing to the upper left
	var NR = 10
	var prev = []
	for i in NR + 1:
		var t = float(i) / NR
		var c = D(lerpf(-0.15, -0.225, t) + 0.035 * sin(PI * t), lerpf(0.50, 0.90, t), 0.002 + 0.10 * smoothstep(0.0, 1.0, t))
		var nxt = D(lerpf(-0.15, -0.225, t + 0.01) + 0.035 * sin(PI * (t + 0.01)), lerpf(0.50, 0.90, t + 0.01))
		var tg = (nxt - Vector3(c.x, 0, c.z)).normalized()
		var sd = Vector3(tg.z, 0, -tg.x).normalized() * 0.035
		var row = [c - sd, c + sd]
		if i > 0:
			var pr = prev
			b.quad(g, "pc_driver_ramp" + S, [P * pr[0], P * pr[1], P * row[1], P * row[0]], (P.basis * Vector3.UP).normalized(), [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)], true)
			for k in 2:
				var up = Vector3(0, 0.03, 0)
				b.quad(g, "pc_driver_ramp" + S, [P * pr[k], P * row[k], P * (row[k] + up), P * (pr[k] + up)], (P.basis * (sd * (1 if k == 1 else -1))).normalized(),
					[Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)], true)
		prev = row
		if i == 6 or i == NR:
			for k in 2:
				rod(b, g, "pc_driver_chrome", P, Vector3(row[k].x, 0, row[k].z), row[k], 0.003, 4)
	# wire habitrail from the upper right down the right side to the inlane
	var path = []
	for i in 11:
		var t = float(i) / 10.0
		path.append(D(lerpf(0.10, 0.17, t) + 0.05 * sin(PI * t), lerpf(0.94, 0.33, t), lerpf(0.11, 0.035, t)))
	for i in 10:
		var a = path[i]
		var c = path[i + 1]
		var tg = (c - a).normalized()
		var sd = Vector3(tg.z, 0, -tg.x).normalized() * 0.014
		for w in [sd, -sd, Vector3(0, 0.016, 0)]:
			rod(b, g, "pc_driver_chrome", P, a + w, c + w, 0.0018, 4)
		if i % 3 == 0:
			rod(b, g, "pc_driver_chrome", P, Vector3(a.x, 0, a.z), a, 0.002, 4)
	# lit insert overlays (match the painted inserts in paint_driver.py)
	pf_inserts(b, g, P)
	# steel ball resting in the shooter lane
	sphere(b, g, "pc_driver_ball", P, D(0.2765, 0.21, 0.0135), 0.0135, 10, 7)

static func flipper(b, g, P, piv, tip):
	var dir = (tip - piv).normalized()
	var per = Vector2(-dir.y, dir.x)
	var r0 = 0.0135
	var r1 = 0.0065
	var outl = []
	for k in 9:
		var a = PI * 0.5 + PI * k / 8.0
		outl.append(piv + (dir * cos(a) + per * sin(a)) * r0)
	for k in 9:
		var a = -PI * 0.5 + PI * k / 8.0
		outl.append(tip + (dir * cos(a) + per * sin(a)) * r1)
	var h0 = 0.003
	var h1 = 0.026
	var s = b.st(g, "vcolor", true)
	var c = (piv + tip) * 0.5
	b.cur_color = Color("#f6f4ee")
	var up = (P.basis * Vector3.UP).normalized()
	for i in outl.size():
		var a = outl[i]
		var d = outl[(i + 1) % outl.size()]
		b.tri(s, P * Vector3(c.x, h1, c.y), P * Vector3(a.x, h1, a.y), P * Vector3(d.x, h1, d.y), Vector2(), Vector2(), Vector2(), up)
	for i in outl.size():
		var a = outl[i]
		var d = outl[(i + 1) % outl.size()]
		var m = (a + d) * 0.5 - c
		var n = (P.basis * Vector3(m.x, 0, m.y)).normalized()
		b.cur_color = Color("#c81e1e")
		b.quad(g, "vcolor", [P * Vector3(a.x, h0, a.y), P * Vector3(d.x, h0, d.y), P * Vector3(d.x, 0.019, d.y), P * Vector3(a.x, 0.019, a.y)], n, [Vector2(), Vector2(), Vector2(), Vector2()], true)
		b.cur_color = Color("#f6f4ee")
		b.quad(g, "vcolor", [P * Vector3(a.x, 0.019, a.y), P * Vector3(d.x, 0.019, d.y), P * Vector3(d.x, h1, d.y), P * Vector3(a.x, h1, a.y)], n, [Vector2(), Vector2(), Vector2(), Vector2()], true)
	ocyl(b, g, "pc_driver_chrome", P, Vector3(piv.x, h1, piv.y), Vector3(0, 0.003, 0), 0.006, 0.006, 8, true, false, true)
	b.cur_color = Color.WHITE

static func slingshot(b, g, P, pts, S):
	var c = (pts[0] + pts[1] + pts[2]) / 3.0
	# white rubber band around the three posts, then the art plastic on top
	b.cur_color = Color("#f0eee6")
	for i in 3:
		var a = pts[i] + (pts[i] - c).normalized() * 0.008
		var d = pts[(i + 1) % 3] + (pts[(i + 1) % 3] - c).normalized() * 0.008
		var m = (a + d) * 0.5 - c
		b.quad(g, "vcolor", [P * Vector3(a.x, 0.006, a.y), P * Vector3(d.x, 0.006, d.y), P * Vector3(d.x, 0.024, d.y), P * Vector3(a.x, 0.024, a.y)],
			(P.basis * Vector3(m.x, 0, m.y)).normalized(), [Vector2(), Vector2(), Vector2(), Vector2()], true)
	b.cur_color = Color.WHITE
	for p in pts:
		ocyl(b, g, "pc_driver_chrome", P, Vector3(p.x, 0, p.y), Vector3(0, 0.044, 0), 0.0045, 0.0045, 6, true, false, true)
	var s = b.st(g, "pc_driver_plastic" + S, true)
	var big = []
	for p in pts:
		big.append(p + (p - c).normalized() * 0.014)
	var up = (P.basis * Vector3.UP).normalized()
	b.tri(s, P * Vector3(big[0].x, 0.045, big[0].y), P * Vector3(big[1].x, 0.045, big[1].y), P * Vector3(big[2].x, 0.045, big[2].y),
		Vector2(0.1, 0.9), Vector2(0.1, 0.1), Vector2(0.9, 0.8), up)

static func pf_inserts(b, g, P):
	var up = (P.basis * Vector3.UP).normalized()
	var items = []   # [centre_px(Vector2), half_size_px, angle, cell]
	# arrows: painter ins_arrow(px, pz, ang, L, col)
	for a in [[-0.13, 0.45, -14.0, 34.0, 0], [-0.075, 0.46, -6.0, 30.0, 1], [0.02, 0.47, 10.0, 30.0, 3], [0.09, 0.45, 28.0, 34.0, 2],
			[0.17, 0.48, -78.0, 20.0, 1], [0.17, 0.54, -78.0, 20.0, 1], [0.17, 0.60, -78.0, 20.0, 1]]:
		var k = 0.8 * a[3] / 40.0
		items.append([pix(a[0], a[1]), k, deg_to_rad(a[2]), a[4], Vector2(0, -10)])
	# circles: painter ins_circle(px, pz, r, col)
	var circ = [[-0.0235, 0.085, 14.0, 6]]
	for x in [-0.2725, -0.225, 0.178, 0.2255]:
		circ.append([x, 0.36, 8.0, 4])
	for x in [-0.11, -0.03, 0.05]:
		circ.append([x, 0.955, 8.0, 4])
	for i in 4:
		var ang = deg_to_rad(-50.0 + i * 33.0)
		circ.append([-0.0235 + sin(ang) * 0.085, 0.27 + cos(ang) * 0.06 - 0.02, 9.0, 7])
	for i in 5:
		circ.append([-0.17 + i * 0.035, 0.585, 7.0, 5 if i % 2 else 4])
	for c in circ:
		items.append([pix(c[0], c[1]), c[2] / 26.0, 0.0, c[3], Vector2(0, 0)])
	for it in items:
		var o = it[0]
		var k = it[1]
		var ca = cos(it[2])
		var sa = sin(it[2])
		var cell = it[3]
		var off = it[4]
		var u0 = (cell % 4) * 0.25
		var v0 = (cell / 4) * 0.5
		var pts = []
		var uvs = []
		for c in [[-32.0, 32.0, 0.0, 1.0], [32.0, 32.0, 1.0, 1.0], [32.0, -32.0, 1.0, 0.0], [-32.0, -32.0, 0.0, 0.0]]:
			var u = (c[0] + off.x) * k
			var v = (c[1] + off.y) * k
			var p = Vector2(o.x + u * ca - v * sa, o.y + u * sa + v * ca)
			pts.append(P * unpix(p, 0.0012))
			uvs.append(Vector2(u0 + c[2] * 0.25, v0 + c[3] * 0.5))
		b.quad(g, "pc_driver_ins", pts, up, uvs, true)

static func build_backbox(b, g, xf, s):
	var S = str(s)
	var z0 = BB[0]
	var z1 = BB[1]
	var y0 = BB[2]
	var y1 = BB[3]
	var hw = P_HW
	var X1 = Vector3(1, 0, 0)
	var dep = z1 - z0
	var hh = y1 - y0
	# sides (art from pbox's left band), back, top, bottom
	face(b, g, "pc_driver_pbox" + S, xf, Vector3(hw, y0, z0), Vector3(0, 0, 1), Vector3.UP, dep, hh, [0, 0, dep, hh], Rect2(0, 0, 0.25, 1))
	face(b, g, "pc_driver_pbox" + S, xf, Vector3(-hw, y0, z1), Vector3(0, 0, -1), Vector3.UP, dep, hh, [0, 0, dep, hh], Rect2(0, 0, 0.25, 1))
	face(b, g, "pc_driver_lam", xf, Vector3(hw, y0, z1), -X1, Vector3.UP, hw * 2, hh, [0, 0, hw * 2, hh], Rect2(0, 0, 0.6, 0.85))
	face(b, g, "pc_driver_lam", xf, Vector3(-hw, y1, z0), X1, Vector3(0, 0, 1), hw * 2, dep, [0, 0, hw * 2, dep], Rect2(0, 0, 0.6, 0.23))
	face(b, g, "pc_driver_lam", xf, Vector3(-hw, y0, z1), X1, Vector3(0, 0, -1), hw * 2, dep, [0, 0, hw * 2, dep], Rect2(0, 0, 0.6, 0.23))
	# front: trims, speaker panel with the DMD window, translight
	var F0 = Vector3(-hw, y0, z0)
	var W = hw * 2
	var trim = "pc_driver_pcab" + S
	var sp0 = 0.03
	var sp1 = 0.25          # speaker panel y0+0.03 .. y0+0.25 (0.22 tall)
	var tl0 = 0.29
	var tl1 = 0.73          # translight 0.44 tall
	var tw = 0.27           # translight half-width
	var pw = 0.29           # speaker panel half-width
	var full = [0, 0, W, hh]
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [0, 0, W, sp0], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [0, sp0, hw - pw, sp1], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [hw + pw, sp0, W, sp1], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [0, sp1, W, tl0], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [0, tl0, hw - tw, tl1], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [hw + tw, tl0, W, tl1], Rect2(0, 0, 1, 1))
	face(b, g, trim, xf, F0, X1, Vector3.UP, W, hh, [0, tl1, W, hh], Rect2(0, 0, 1, 1))
	# speaker panel (pbox x 128..512) with the DMD hole
	var SP0 = Vector3(-pw, y0 + sp0, z0)
	var spw = pw * 2
	var sph = sp1 - sp0
	var dw = 0.17
	var dh = 0.044
	var hole = [[pw - dw, sph * 0.5 - dh, pw + dw, sph * 0.5 + dh]]
	face_holes(b, g, "pc_driver_pbox" + S, xf, SP0, X1, Vector3.UP, spw, sph, hole, Rect2(0.25, 0, 0.75, 1))
	var hl = hole[0]
	var c00 = SP0 + Vector3(hl[0], hl[1], 0)
	var c10 = SP0 + Vector3(hl[2], hl[1], 0)
	var c11 = SP0 + Vector3(hl[2], hl[3], 0)
	var c01 = SP0 + Vector3(hl[0], hl[3], 0)
	var dd = Vector3(0, 0, 0.018)
	for e in [[c00, c10, Vector3.UP], [c10, c11, -X1], [c11, c01, Vector3.DOWN], [c01, c00, X1]]:
		b.quad(g, "pc_driver_black", [xf * e[0], xf * e[1], xf * (e[1] + dd), xf * (e[0] + dd)], (xf.basis * e[2]).normalized(), [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
	b.quad(g, "pc_driver_pdmd" + S, [xf * (c00 + dd), xf * (c10 + dd), xf * (c11 + dd), xf * (c01 + dd)], (xf.basis * Vector3(0, 0, -1)).normalized(),
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	b.quad(g, "pc_driver_glass", [xf * (c00 + dd * 0.3), xf * (c10 + dd * 0.3), xf * (c11 + dd * 0.3), xf * (c01 + dd * 0.3)], (xf.basis * Vector3(0, 0, -1)).normalized(),
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# translight, recessed 1.2 cm behind its glass, with a short tunnel
	var T0 = Vector3(-tw, y0 + tl0, z0)
	var th = tl1 - tl0
	var rz = Vector3(0, 0, 0.012)
	for e in [[T0, T0 + Vector3(2 * tw, 0, 0), Vector3.UP], [T0 + Vector3(2 * tw, 0, 0), T0 + Vector3(2 * tw, th, 0), -X1],
			[T0 + Vector3(2 * tw, th, 0), T0 + Vector3(0, th, 0), Vector3.DOWN], [T0 + Vector3(0, th, 0), T0, X1]]:
		b.quad(g, "pc_driver_black", [xf * e[0], xf * e[1], xf * (e[1] + rz), xf * (e[0] + rz)], (xf.basis * e[2]).normalized(), [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
	face(b, g, "pc_driver_ptrans" + S, xf, T0 + rz, X1, Vector3.UP, 2 * tw, th, [0, 0, 2 * tw, th], Rect2(0, 0, 1, 1))
	face(b, g, "pc_driver_glass", xf, T0, X1, Vector3.UP, 2 * tw, th, [0, 0, 2 * tw, th], Rect2(0, 0, 1, 1), true, 0.002)
	# glass lock channel across the top of the translight
	b.box(g, "pc_driver_steel", Vector3(0, y0 + tl1 + 0.012, z0 - 0.006), Vector3(2 * tw + 0.03, 0.024, 0.014), xf)

# ================================================================ materials
static func fill_mat(m, key, b):
	var base = key
	var s = 0
	if key.length() > 1 and key.right(1).is_valid_int():
		base = key.left(key.length() - 1)
		s = int(key.right(1))
	match base:
		"rmarq":
			lit(m, b.tex("pc/driver_rmarq%d.png" % s), 1.3)
		"rscr":
			lit(m, b.tex("pc/driver_rscr%d.png" % s), 1.6)
			m.roughness = 0.12
		"rside", "rpanel", "rbase", "pside", "pbox", "apron":
			m.albedo_texture = b.tex("pc/driver_%s.png" % key)
			m.roughness = 0.55 if base != "apron" else 0.45
		"pfield":
			lit(m, b.tex("pc/driver_pfield%d.png" % s), 0.85)
			m.roughness = 0.25
		"ptrans":
			lit(m, b.tex("pc/driver_ptrans%d.png" % s), 1.35)
		"pdmd":
			lit(m, b.tex("pc/driver_pdmd%d.png" % s), 5.0)
			m.albedo_color = Color(0.3, 0.3, 0.3)
		"ins":
			m.albedo_texture = b.tex("pc/driver_ins.png")
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.emission_enabled = true
			m.emission_texture = m.albedo_texture
			m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color.WHITE
			m.emission_energy_multiplier = 2.2
			m.set_meta("e_day", 2.2); m.set_meta("e_night", 2.2)
		"coin":
			m.albedo_texture = b.tex("pc/driver_coin.png")
			m.roughness = 0.4; m.metallic = 0.3
		"coinlit":
			lit(m, b.tex("pc/driver_coin.png"), 2.4)
		"lampstart":
			lamp(m, Color("#ff3a20"), 3.0)
		"lampview":
			lamp(m, Color("#2a8cff"), 2.5)
		"bcap":
			lamp(m, [Color("#7ab8ff"), Color("#ffa030"), Color("#ffd840")][s], 2.0)
		"seat":
			m.albedo_texture = b.tex("pc/driver_vinyl.png")
			m.albedo_color = [Color("#a81812"), Color("#1c2a64")][s]
			m.roughness = 0.42
		"seatback":
			m.albedo_texture = b.tex("pc/driver_rbase%d.png" % s)
			m.roughness = 0.35
		"shell":
			m.albedo_color = [Color("#141214"), Color("#0e1430")][s]
			m.roughness = 0.35
		"tmold":
			m.albedo_texture = b.tex("pc/driver_tmold.png")
			m.albedo_color = [Color("#2a2a2c"), Color("#1c3c9c")][s]
			m.roughness = 0.45
		"pcab":
			m.albedo_color = [Color("#1a1a50"), Color("#08485c"), Color("#2a0c08")][s]
			m.roughness = 0.5
		"rail":
			if s == 1:
				m.albedo_color = Color("#1a1a1c"); m.metallic = 0.6; m.roughness = 0.35
			else:
				m.albedo_color = Color("#c4c6ca"); m.metallic = 0.9; m.roughness = 0.25
		"legs":
			if s == 1:
				m.albedo_color = Color("#141416"); m.metallic = 0.5; m.roughness = 0.4
			else:
				m.albedo_color = Color("#c8cacf"); m.metallic = 0.9; m.roughness = 0.2
		"plastic":
			m.albedo_color = [Color("#d838a8"), Color("#f0a020"), Color("#f06010")][s]
			m.roughness = 0.3
		"ramp":
			m.albedo_color = [Color(0.5, 0.75, 1.0, 0.45), Color(1.0, 0.85, 0.4, 0.45), Color(1.0, 0.5, 0.2, 0.45)][s]
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.1; m.metallic_specular = 0.8
		"plunger":
			m.albedo_color = [Color("#e83030"), Color("#f0c020"), Color("#f0f0f0")][s]
			m.roughness = 0.25
		"fbtn":
			m.albedo_color = [Color("#e83030"), Color("#f0c020"), Color("#e83030")][s]
			m.roughness = 0.3
		"glass":
			m.albedo_texture = b.tex("pc/driver_glass.png")
			m.albedo_color = Color(0.85, 0.9, 0.95, 0.55)
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.04; m.metallic_specular = 1.0
		"lam":
			m.albedo_texture = b.tex("pc/driver_lam.png"); m.roughness = 0.6
		"wall":
			m.albedo_texture = b.tex("pc/driver_lam.png"); m.albedo_color = Color(1.6, 1.6, 1.7); m.roughness = 0.5
		"diamond":
			m.albedo_texture = b.tex("pc/driver_diamond.png"); m.metallic = 0.7; m.roughness = 0.45
		"lockbar":
			m.albedo_texture = b.tex("pc/driver_steel.png"); m.albedo_color = Color(0.55, 0.56, 0.58); m.metallic = 0.9; m.roughness = 0.35
		"steel":
			m.albedo_texture = b.tex("pc/driver_steel.png"); m.metallic = 0.85; m.roughness = 0.3
		"grille":
			m.albedo_texture = b.tex("pc/driver_grille.png"); m.roughness = 0.7
		"black":
			m.albedo_color = Color("#060607"); m.roughness = 0.8
		"chrome":
			m.albedo_color = Color("#d4d6da"); m.metallic = 0.95; m.roughness = 0.18
		"spring":
			m.albedo_color = Color("#9a9ca0"); m.metallic = 0.9; m.roughness = 0.4
		"ball":
			m.albedo_color = Color("#e4e6ea"); m.metallic = 1.0; m.roughness = 0.06
		"wheel":
			m.albedo_color = Color("#141416"); m.roughness = 0.75
		"spoke":
			m.albedo_color = Color("#3a3a40"); m.metallic = 0.7; m.roughness = 0.35
		"knob":
			m.albedo_color = Color("#101012"); m.roughness = 0.2
		_:
			return false
	return true

## A lit (emissive) painted face: screens, marquees, translights.
static func lit(m, t, e):
	m.albedo_texture = t
	m.roughness = 0.35
	m.emission_enabled = true
	m.emission_texture = t
	m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
	m.emission = Color.WHITE
	m.emission_energy_multiplier = e
	m.set_meta("e_day", e); m.set_meta("e_night", e)

static func lamp(m, c, e):
	m.albedo_color = c
	m.roughness = 0.3
	m.emission_enabled = true
	m.emission = c
	m.emission_energy_multiplier = e
	m.set_meta("e_day", e); m.set_meta("e_night", e)
