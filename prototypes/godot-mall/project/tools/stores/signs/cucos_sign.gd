## The Cucos sign (Steven, Oct 7 2026): an open-face neon channel sign, built the way the real
## one is. tools/stores/signs/make_cucos.py traces his photos into cu_sign.json.
##
## - The script is sheet-metal cans: black returns standing 125 mm off the fascia, a thin rim,
##   the inside (back pan and inner walls) painted brick red. The big C runs into the swash and
##   the S as one can; u, c and o are cans of their own.
## - Inside each can, glass tubes on standoffs: a run 30 mm inside the walls, a centre run where
##   the stroke is wide (three tubes abreast, as in the photo) or too narrow for two. Every run
##   ends in a pair of electrodes turned back through the pan in black boots; a closed run has
##   its gap. The tubes glow; each lays a pool of light on the red pan, and the cans throw a
##   faint halo on the planks.
## - Below, the blue cabinet with bullnose ends: two white stripes wrapping each end with a
##   white tube doubling back round the nose, and MEXICAN CAFE as white plates each with its
##   own white tube.
##
## All of it is geometry and vertex colour: no textures. Materials "sg_cu2_*" (channel.gd).

const UP = Vector3.UP
const CAN_D = 0.125      # the cans' depth (photo: the returns are about a ninth of the script's height)
const WALL = 0.004       # the rim's width
const PAN = 0.006        # the back pan stands this far off the fascia
const TUBE_R = 0.0042    # 8 mm glass (the street sign's 15 mm, at this sign's scale)
const TUBE_Z = 0.042     # tube centres above the fascia
const BAR_D = 0.15       # the cabinet's depth, and its bullnose radius
const PLATE = 0.008      # the white letters' thickness
const POOL = Color(0.42, 0.075, 0.028)     # a tube's light on the red pan (added)
const HALO = Color(0.11, 0.02, 0.008)     # the cans' spill on the fascia (added)
const WPOOL = Color(0.10, 0.11, 0.16)     # the white tubes' light on the blue face (added)

## Builds the sign with the middle of the bar's bottom edge at c (on the fascia's face), facing nn.
## g: the dynamic mesh group; g + "_glow" takes the added light.
static func build(b, g, path, c, nn):
	var J = JSON.parse_string(FileAccess.get_file_as_string(path))
	var rv = (-nn).cross(UP)
	var X = func(p, z): return c + rv * p.x + UP * p.y + nn * z
	var s_red = b.st(g, "sg_cu2_red", true)
	var s_blk = b.st(g, "sg_cu2_black", true)
	var s_tube = b.st(g, "sg_cu2_tube", true)
	var s_boot = b.st(g, "sg_cu2_boot", true)
	var s_post = b.st(g, "sg_cu2_post", true)
	var s_pool = b.st(g + "_glow", "sg_cu2_pool", true)
	# ---- the cans
	for can in J.cans:
		var tr = can.tris
		for i in range(0, tr.size(), 3):
			_tri(s_red, [X.call(_v(tr[i]), PAN), X.call(_v(tr[i + 1]), PAN), X.call(_v(tr[i + 2]), PAN)], [nn, nn, nn], nn)
		var first = true
		for lp in can.loops:
			var pts = []
			for q in lp:
				pts.append(_v(q))
			# a narrow halo, narrower still inside a counter, so it never folds over itself
			_can_walls(s_blk, s_red, s_pool, pts, X, rv, nn, CAN_D, WALL, PAN, 0.075 if first else 0.03)
			first = false
	# ---- the tubes
	for tb in J.tubes:
		var run = []
		for q in tb.pts:
			run.append(X.call(_v(q), TUBE_Z))
		if tb.closed:
			# a closed run still has two ends: leave the gap where the glass was sealed
			while run.size() > 4 and run[0].distance_to(run[run.size() - 1]) < 0.03:
				run.remove_at(run.size() - 1)
		_tube(s_tube, run, TUBE_R, nn)
		_ends(s_boot, run, TUBE_R * 1.35, nn, TUBE_Z - PAN)
		_posts(s_post, run, nn, TUBE_Z - PAN - TUBE_R, 0.21)
		_pool(s_pool, run, nn, TUBE_Z - PAN - 0.0015, 0.034, POOL)
	# ---- the blue cabinet
	_bar(b, g, J, X, rv, nn)

static func _v(q):
	return Vector2(float(q[0]), float(q[1]))

## One triangle, wound to face fn.
static func _tri(s, p, n, fn, col = [Color.WHITE, Color.WHITE, Color.WHITE]):
	var order = [0, 1, 2]
	if (p[1] - p[0]).cross(p[2] - p[0]).dot(fn) > 0.0:
		order = [0, 2, 1]
	for i in order:
		s.set_color(col[i]); s.set_normal(n[i]); s.set_uv(Vector2.ZERO); s.add_vertex(p[i])

static func _quad(s, p, n, fn, col = [Color.WHITE, Color.WHITE, Color.WHITE, Color.WHITE]):
	_tri(s, [p[0], p[1], p[2]], [n[0], n[1], n[2]], fn, [col[0], col[1], col[2]])
	_tri(s, [p[0], p[2], p[3]], [n[0], n[2], n[3]], fn, [col[0], col[2], col[3]])

## One outline of a can: the black return, the rim, the red inner wall, and the halo on the fascia.
## Outer loops run counter-clockwise and holes clockwise, so outward is the right-hand normal.
static func _can_walls(s_blk, s_red, s_pool, pts, X, rv, nn, depth = CAN_D, wall = WALL, pan = PAN, halo = 0.15, halo_col = HALO):
	var n = pts.size()
	if n < 3:
		return
	var vn = []     # outward normal at each vertex (smoothed)
	for i in n:
		var d0 = (pts[i] - pts[(i - 1 + n) % n]).normalized()
		var d1 = (pts[(i + 1) % n] - pts[i]).normalized()
		var m = Vector2(d0.y, -d0.x) + Vector2(d1.y, -d1.x)
		vn.append(m.normalized() if m.length() > 1e-5 else Vector2(d1.y, -d1.x))
	var W3 = func(v2): return (rv * v2.x + UP * v2.y).normalized()
	for i in n:
		var j = (i + 1) % n
		var e = pts[j] - pts[i]
		if e.length() < 1e-6:
			continue
		var fn = W3.call(Vector2(e.y, -e.x).normalized())
		var ni = W3.call(vn[i])
		var nj = W3.call(vn[j])
		var ii = pts[i] - vn[i] * wall
		var ij = pts[j] - vn[j] * wall
		# the return, outside
		_quad(s_blk, [X.call(pts[i], 0.0), X.call(pts[j], 0.0), X.call(pts[j], depth), X.call(pts[i], depth)], [ni, nj, nj, ni], fn)
		# the rim
		_quad(s_blk, [X.call(pts[i], depth), X.call(pts[j], depth), X.call(ij, depth), X.call(ii, depth)], [nn, nn, nn, nn], nn)
		# the inner wall, red
		_quad(s_red, [X.call(ii, pan), X.call(ij, pan), X.call(ij, depth), X.call(ii, depth)], [-ni, -nj, -nj, -ni], -fn)
		# the halo on the fascia
		if halo > 0.0:
			var oi = pts[i] + vn[i] * halo
			var oj = pts[j] + vn[j] * halo
			_quad(s_pool, [X.call(pts[i], 0.003), X.call(pts[j], 0.003), X.call(oj, 0.003), X.call(oi, 0.003)], [nn, nn, nn, nn], nn,
				[halo_col, halo_col, Color.BLACK, Color.BLACK])

## A glass tube along `run` (world points), six-sided, smooth.
static func _tube(s, run, r, nn, K = 6):
	var n = run.size()
	if n < 2:
		return
	var rings = []
	var norms = []
	for i in n:
		var tg = (run[min(i + 1, n - 1)] - run[max(i - 1, 0)]).normalized()
		var ref = nn if abs(tg.dot(nn)) < 0.9 else UP
		var side = tg.cross(ref).normalized()
		var upv = side.cross(tg).normalized()
		var ring = []
		var nr = []
		for k in K:
			var a = TAU * k / K
			var d = side * cos(a) + upv * sin(a)
			ring.append(run[i] + d * r)
			nr.append(d)
		rings.append(ring)
		norms.append(nr)
	for i in n - 1:
		for k in K:
			var k2 = (k + 1) % K
			_quad(s, [rings[i][k], rings[i + 1][k], rings[i + 1][k2], rings[i][k2]],
				[norms[i][k], norms[i + 1][k], norms[i + 1][k2], norms[i][k2]], (norms[i][k] + norms[i][k2]).normalized())

## The electrodes: each end of a run turns back to the pan in a black boot.
static func _ends(s, run, r, nn, drop):
	if run.size() < 2:
		return
	for e in [run[0], run[run.size() - 1]]:
		_tube(s, [e + nn * 0.002, e - nn * drop], r, UP, 6)

## Glass standoffs under a run, every `step` metres.
static func _posts(s, run, nn, drop, step):
	var acc = step * 0.5
	for i in run.size() - 1:
		var ln = run[i].distance_to(run[i + 1])
		acc += ln
		if acc >= step:
			acc = 0.0
			var p = (run[i] + run[i + 1]) * 0.5
			_tube(s, [p, p - nn * drop], 0.003, UP, 4)

## A tube's light on the surface behind it: a strip `drop` behind the run, bright under the tube.
static func _pool(s, run, nn, drop, half, col):
	var n = run.size()
	if n < 2:
		return
	var L = []
	var R = []
	var C = []
	for i in n:
		var d0 = run[i] - run[max(i - 1, 0)]
		var d1 = run[min(i + 1, n - 1)] - run[i]
		var tg = (d0 + d1).normalized()
		var side = tg.cross(nn).normalized()
		# narrower round a tight bend, so the strip does not fold over itself
		var h = half
		if d0.length() > 1e-5 and d1.length() > 1e-5:
			var turn = d0.angle_to(d1)
			if turn > 0.02:
				h = clamp(0.7 * (d0.length() + d1.length()) * 0.5 / turn, 0.006, half)
		var c0 = run[i] - nn * drop
		C.append(c0); L.append(c0 - side * h); R.append(c0 + side * h)
	for i in n - 1:
		_quad(s, [L[i], L[i + 1], C[i + 1], C[i]], [nn, nn, nn, nn], nn, [Color.BLACK, Color.BLACK, col, col])
		_quad(s, [C[i], C[i + 1], R[i + 1], R[i]], [nn, nn, nn, nn], nn, [col, col, Color.BLACK, Color.BLACK])

## The blue cabinet: a flat face, bullnose ends turning back to the fascia, white stripes and a
## doubled-back white tube at each end, MEXICAN CAFE as white plates with a tube each.
static func _bar(b, g, J, X, rv, nn):
	var bw = float(J.bar_w)
	var bh = float(J.bar_h)
	var R = BAR_D
	var s_blue = b.st(g, "sg_cu2_blue", true)
	var s_white = b.st(g, "sg_cu2_white", true)
	var s_wtube = b.st(g, "sg_cu2_wtube", true)
	var s_boot = b.st(g, "sg_cu2_boot", true)
	var s_pool = b.st(g + "_glow", "sg_cu2_pool", true)
	var xl = -bw * 0.5 + R
	var xr = bw * 0.5 - R
	# P(x, y, z): a point of the sign's frame
	var P = func(x, y, z): return X.call(Vector2(x, y), z)
	_quad(s_blue, [P.call(xl, 0.0, R), P.call(xr, 0.0, R), P.call(xr, bh, R), P.call(xl, bh, R)], [nn, nn, nn, nn], nn)
	_quad(s_blue, [P.call(xl, bh, 0.0), P.call(xr, bh, 0.0), P.call(xr, bh, R), P.call(xl, bh, R)], [UP, UP, UP, UP], UP)
	_quad(s_blue, [P.call(xl, 0.0, 0.0), P.call(xr, 0.0, 0.0), P.call(xr, 0.0, R), P.call(xl, 0.0, R)], [-UP, -UP, -UP, -UP], -UP)
	var SEG = 10
	for sd in [-1.0, 1.0]:
		var xc = xl if sd < 0.0 else xr
		for k in SEG:
			var a0 = PI * 0.5 * k / SEG
			var a1 = PI * 0.5 * (k + 1) / SEG
			var n0 = (rv * (sd * sin(a0)) + nn * cos(a0)).normalized()
			var n1 = (rv * (sd * sin(a1)) + nn * cos(a1)).normalized()
			var x0 = xc + sd * R * sin(a0)
			var x1 = xc + sd * R * sin(a1)
			var z0 = R * cos(a0)
			var z1 = R * cos(a1)
			_quad(s_blue, [P.call(x0, 0.0, z0), P.call(x1, 0.0, z1), P.call(x1, bh, z1), P.call(x0, bh, z0)], [n0, n1, n1, n0], (n0 + n1).normalized())
			_tri(s_blue, [P.call(xc, bh, 0.0), P.call(x0, bh, z0), P.call(x1, bh, z1)], [UP, UP, UP], UP)
			_tri(s_blue, [P.call(xc, 0.0, 0.0), P.call(x0, 0.0, z0), P.call(x1, 0.0, z1)], [-UP, -UP, -UP], -UP)
		# the two white stripes wrapping this end, and the tube that runs out along one and back
		# along the other (photo: longer stripes on the left end)
		var inner = xc - sd * (bw * (0.13 if sd < 0.0 else 0.07) - R)
		var run = []
		var back = []
		for yk in [0.70, 0.30]:
			var y0 = bh * (yk - 0.10)
			var y1 = bh * (yk + 0.10)
			var zf = R + 0.002
			_quad(s_white, [P.call(inner, y0, zf), P.call(xc, y0, zf), P.call(xc, y1, zf), P.call(inner, y1, zf)], [nn, nn, nn, nn], nn)
			var path = [P.call(inner, bh * yk, R + 0.024), P.call(xc, bh * yk, R + 0.024)]
			for k in SEG:
				var a0 = PI * 0.5 * 0.86 * k / SEG
				var a1 = PI * 0.5 * 0.86 * (k + 1) / SEG
				var n0 = (rv * (sd * sin(a0)) + nn * cos(a0)).normalized()
				var n1 = (rv * (sd * sin(a1)) + nn * cos(a1)).normalized()
				var rr = R + 0.002
				_quad(s_white, [P.call(xc + sd * rr * sin(a0), y0, rr * cos(a0)), P.call(xc + sd * rr * sin(a1), y0, rr * cos(a1)),
					P.call(xc + sd * rr * sin(a1), y1, rr * cos(a1)), P.call(xc + sd * rr * sin(a0), y1, rr * cos(a0))], [n0, n1, n1, n0], (n0 + n1).normalized())
				var rt = R + 0.024
				path.append(P.call(xc + sd * rt * sin(a1), bh * yk, rt * cos(a1)))
			if yk > 0.5:
				run = path
			else:
				back = path
		# out along the top stripe, a turn round the nose, back along the bottom one
		var tip_t = run[run.size() - 1]
		var tip_b = back[back.size() - 1]
		var outv = (tip_t - P.call(xc, bh * 0.70, 0.0)).normalized()
		var full = run.duplicate()
		for k in range(1, 8):
			var a = PI * k / 8.0
			full.append((tip_t + tip_b) * 0.5 + UP * (bh * 0.20 * cos(a)) + outv * (bh * 0.20 * sin(a)))
		back.reverse()
		full.append_array(back)
		_tube(s_wtube, full, 0.0045, nn)
		_ends(s_boot, [full[0], full[full.size() - 1]], 0.0062, nn, 0.022)
	# MEXICAN CAFE
	var zp = R + PLATE
	for pl in J.plates:
		var tr = pl.tris
		for i in range(0, tr.size(), 3):
			_tri(s_white, [X.call(_v(tr[i]), zp), X.call(_v(tr[i + 1]), zp), X.call(_v(tr[i + 2]), zp)], [nn, nn, nn], nn)
		for lp in pl.loops:
			var pts = []
			for q in lp:
				pts.append(_v(q))
			var n = pts.size()
			for i in n:
				var j = (i + 1) % n
				var e = pts[j] - pts[i]
				if e.length() < 1e-6:
					continue
				var fn = (rv * e.y - UP * e.x).normalized()
				_quad(s_white, [X.call(pts[i], R), X.call(pts[j], R), X.call(pts[j], zp), X.call(pts[i], zp)], [fn, fn, fn, fn], fn)
	for tb in J.wtubes:
		var run = []
		for q in tb.pts:
			run.append(X.call(_v(q), zp + 0.011))
		_tube(s_wtube, run, 0.0032, nn, 5)
		_ends(s_boot, run, 0.0042, nn, 0.011)
		_pool(s_pool, run, nn, 0.0105, 0.016, WPOOL)
