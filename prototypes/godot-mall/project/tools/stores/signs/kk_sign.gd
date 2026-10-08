## The Karmelkorn sign (Steven, Oct 7 2026): an open-face neon channel sign, built the way the
## real one is, on both fronts of the corner shop. tools/stores/signs/make_kk.py traces his photos
## into kk_sign.json (the swash K traced; the capitals Coustard Black fitted to each letter's box).
##
## - The script is sheet-metal cans: deep red returns 110 mm deep (the photos' "drop shadow"), a
##   cream trim cap on the edge, the inside painted red. The K with its arm, top bar and leg is one
##   can; the swash under the A is its own; each capital is its own.
## - Inside each can, red neon on standoffs as an outline: one run 26 mm inside the walls, a single
##   centre run in the hairlines. Every run ends in electrodes turned back through the pan in black
##   boots. The tubes glow; each lays a pool of light on the red pan; a faint halo on the bulkhead.
##
## Geometry and vertex colour only: no textures. Materials "sg_kk2_*" (channel.gd). The parts are
## cucos_sign.gd's (the walls, tubes, ends, standoffs, light pools), shared from there.

const CS = preload("res://tools/stores/signs/cucos_sign.gd")
const UP = Vector3.UP
const CAN_D = 0.11       # the cans' depth (photo 3: the returns are about a seventh of the caps)
const RIM = 0.007        # the trim cap's width
const PAN = 0.006
const TUBE_R = 0.006     # 12 mm glass (photo 3: the tubes read heavy against the strokes)
const TUBE_Z = 0.04
const POOL = Color(0.50, 0.09, 0.035)
const HALO = Color(0.09, 0.02, 0.008)

## Builds the sign with the middle of its bottom edge at c (on the bulkhead's face), facing nn.
## g: the dynamic mesh group; g + "_glow" takes the added light.
static func build(b, g, path, c, nn):
	var J = JSON.parse_string(FileAccess.get_file_as_string(path))
	var rv = (-nn).cross(UP)
	var X = func(p, z): return c + rv * p.x + UP * p.y + nn * z
	var s_red = b.st(g, "sg_kk2_red", true)
	var s_ret = b.st(g, "sg_kk2_return", true)
	var s_rim = b.st(g, "sg_kk2_rim", true)
	var s_tube = b.st(g, "sg_kk2_tube", true)
	var s_boot = b.st(g, "sg_kk2_boot", true)
	var s_post = b.st(g, "sg_kk2_post", true)
	var s_pool = b.st(g + "_glow", "sg_kk2_pool", true)
	for can in J.cans:
		var tr = can.tris
		for i in range(0, tr.size(), 3):
			CS._tri(s_red, [X.call(CS._v(tr[i]), PAN), X.call(CS._v(tr[i + 1]), PAN), X.call(CS._v(tr[i + 2]), PAN)], [nn, nn, nn], nn)
		var first = true
		for lp in can.loops:
			var pts = []
			for q in lp:
				pts.append(CS._v(q))
			_walls(s_ret, s_rim, s_red, s_pool, pts, X, rv, nn, 0.06 if first else 0.025)
			first = false
	for tb in J.tubes:
		var run = []
		for q in tb.pts:
			run.append(X.call(CS._v(q), TUBE_Z))
		if tb.closed:
			while run.size() > 4 and run[0].distance_to(run[run.size() - 1]) < 0.03:
				run.remove_at(run.size() - 1)
		CS._tube(s_tube, run, TUBE_R, nn)
		CS._ends(s_boot, run, TUBE_R * 1.35, nn, TUBE_Z - PAN)
		CS._posts(s_post, run, nn, TUBE_Z - PAN - TUBE_R, 0.21)
		CS._pool(s_pool, run, nn, TUBE_Z - PAN - 0.0015, 0.04, POOL)

## One outline of a can: the deep red return, the cream trim cap, the red inner wall, the halo.
static func _walls(s_ret, s_rim, s_red, s_pool, pts, X, rv, nn, halo):
	var n = pts.size()
	if n < 3:
		return
	var vn = []
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
		var ii = pts[i] - vn[i] * RIM
		var ij = pts[j] - vn[j] * RIM
		CS._quad(s_ret, [X.call(pts[i], 0.0), X.call(pts[j], 0.0), X.call(pts[j], CAN_D), X.call(pts[i], CAN_D)], [ni, nj, nj, ni], fn)
		CS._quad(s_rim, [X.call(pts[i], CAN_D), X.call(pts[j], CAN_D), X.call(ij, CAN_D), X.call(ii, CAN_D)], [nn, nn, nn, nn], nn)
		CS._quad(s_red, [X.call(ii, PAN), X.call(ij, PAN), X.call(ij, CAN_D), X.call(ii, CAN_D)], [-ni, -nj, -nj, -ni], -fn)
		var oi = pts[i] + vn[i] * halo
		var oj = pts[j] + vn[j] * halo
		CS._quad(s_pool, [X.call(pts[i], 0.003), X.call(pts[j], 0.003), X.call(oj, 0.003), X.call(oi, 0.003)], [nn, nn, nn, nn], nn,
			[HALO, HALO, Color.BLACK, Color.BLACK])
