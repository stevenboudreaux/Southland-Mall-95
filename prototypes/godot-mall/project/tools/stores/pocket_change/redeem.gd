## Pocket Change (1995): the ticket-redemption area on the left as you walk in.
## Prop contract: tools/stores/pocket_change/README.md. Textures: paint_redeem.py.
##   opts.kind = "counter"   a run of glass showcase counters full of small prizes, with a
##                           register, a ticket-counting machine and tickets on top.
##                           opts.length (default 3.6 m). Customer side at z = 0, clerk behind.
##   opts.kind = "prizewall" the big-prize wall: base cabinet, slatwall, shelves of plush,
##                           stereos and boxed prizes, hooks of hanging plush and inflatables,
##                           a lit PRIZES header. opts.length (3.6 m), opts.height (2.6 m).
##   opts.kind = "tokens"    a bill-to-token changer pedestal, 0.55 x 0.5 x 1.6 m.
## Preview: tools/qa/preview.sh redeem <out> "<cams>" '{"kind":"counter","length":3.6}' lit|dark

const CNT_D = 0.60      # showcase depth
const CNT_H = 0.97      # top of the glass
const WALL_D = 0.45
const TOK_W = 0.55
const TOK_D = 0.50
const TOK_H = 1.60

## Footprint (width, depth) in metres for the store layout.
static func footprint(opts = {}):
	match str(opts.get("kind", "counter")):
		"tokens":
			return Vector2(TOK_W, TOK_D)
		"prizewall":
			return Vector2(float(opts.get("length", 3.6)), WALL_D)
		_:
			return Vector2(float(opts.get("length", 3.6)), CNT_D)

static func X(o, f):
	return Transform3D(Basis(f.cross(Vector3.UP), Vector3.UP, f), o)

## Builds one piece; the player stands at o facing f (see the README frame).
static func build(b, g, o, f, opts = {}):
	var xf = X(o, f)
	var kind = str(opts.get("kind", "counter"))
	var fp = footprint(opts)
	match kind:
		"tokens":
			build_tokens(b, g, xf)
		"prizewall":
			build_prizewall(b, g, xf, fp.x, float(opts.get("height", 2.6)))
		_:
			build_counter(b, g, xf, fp.x)
	b.cur_color = Color.WHITE
	var c0 = xf * Vector3(-fp.x * 0.5, 0, 0)
	var c1 = xf * Vector3(fp.x * 0.5, 0, fp.y)
	b.obst(["rect", min(c0.x, c1.x), min(c0.z, c1.z), max(c0.x, c1.x), max(c0.z, c1.z)])

# =================================================================== geometry helpers
## Pixel rect of a w x h atlas as a UV Rect2.
static func R(x0, y0, x1, y1, w, h):
	return Rect2(float(x0) / w, float(y0) / h, float(x1 - x0) / w, float(y1 - y0) / h)

## One quad from four local points (bottom-left, bottom-right, top-right, top-left as seen
## from the side the normal n points to). r = UV Rect2, or null for 1 repeat per `sc` metres.
static func fq(b, g, m, xf, p, n, r = null, dyn = false, sc = 1.0):
	var w = []
	for q in p:
		w.append(xf * q)
	var uvs
	if r == null:
		var lx = (p[1] - p[0]).length() * sc
		var ly = (p[3] - p[0]).length() * sc
		var ox = (p[0].x + p[0].z) * sc
		var oy = -p[0].y * sc
		uvs = [Vector2(ox, oy), Vector2(ox + lx, oy), Vector2(ox + lx, oy - ly), Vector2(ox, oy - ly)]
	else:
		uvs = [Vector2(r.position.x, r.end.y), Vector2(r.end.x, r.end.y), Vector2(r.end.x, r.position.y), r.position]
	b.quad(g, m, w, (xf.basis * n).normalized(), uvs, dyn)

const FACES = {
	"front": [Vector3(0, 0, -1), [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]],
	"back": [Vector3(0, 0, 1), [[1, 0, 1], [0, 0, 1], [0, 1, 1], [1, 1, 1]]],
	"left": [Vector3(-1, 0, 0), [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]]],
	"right": [Vector3(1, 0, 0), [[1, 0, 0], [1, 0, 1], [1, 1, 1], [1, 1, 0]]],
	"top": [Vector3(0, 1, 0), [[0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1]]],
	"bottom": [Vector3(0, -1, 0), [[0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 0]]],
}

## Box from local lo..hi with per-face UVs: uv = {"front": Rect2, ..., "all": Rect2};
## a face without an entry gets 1 repeat per metre.
static func tbox(b, g, m, xf, lo, hi, uv = {}, dyn = false, skip = [], sc = 1.0):
	for k in FACES:
		if k in skip:
			continue
		var pts = []
		for s in FACES[k][1]:
			pts.append(Vector3(hi.x if s[0] == 1 else lo.x, hi.y if s[1] == 1 else lo.y, hi.z if s[2] == 1 else lo.z))
		var r = uv.get(k, uv.get("all", null))
		fq(b, g, m, xf, pts, FACES[k][0], r, dyn, sc)

static func _tri3(b, s, P, N, U, i0, i1, i2):
	var fn = N[i0] + N[i1] + N[i2]
	var ids = [i0, i1, i2]
	if (P[i1] - P[i0]).cross(P[i2] - P[i0]).dot(fn) > 0.0:
		ids = [i0, i2, i1]
	for i in ids:
		s.set_color(b.cur_color)
		s.set_normal(N[i])
		s.set_uv(U[i])
		s.add_vertex(P[i])

## Smooth ellipsoid at local c; B = basis whose columns are the semi-axes.
## Triangles: seg * (2 * rings - 2).
static func ell(b, g, m, xf, c, B, seg, rings, dyn = false, uvs = 1.0):
	var s = b.st(g, m, dyn)
	var Bn = B.inverse().transposed()
	var P = []
	var N = []
	var U = []
	for i in rings + 1:
		var la = -PI * 0.5 + PI * i / rings
		for j in seg + 1:
			var lo = TAU * j / seg
			var u = Vector3(cos(la) * cos(lo), sin(la), cos(la) * sin(lo))
			P.append(xf * (c + B * u))
			N.append((xf.basis * (Bn * u)).normalized())
			U.append(Vector2(float(j) / seg * uvs, float(i) / rings * uvs * 0.5))
	for i in rings:
		for j in seg:
			var a = i * (seg + 1) + j
			var d = a + seg + 1
			if i > 0:
				_tri3(b, s, P, N, U, a, a + 1, d + 1)
			if i < rings - 1:
				_tri3(b, s, P, N, U, a, d + 1, d)

## Ellipsoid whose longitude sectors take colours in turn (a beach ball's gores).
static func ell_gores(b, g, m, xf, c, r, seg, rings, cols, dyn = false):
	var per = seg / cols.size()
	for k in cols.size():
		b.cur_color = cols[k]
		var s = b.st(g, m, dyn)
		var P = []
		var N = []
		var U = []
		for i in rings + 1:
			var la = -PI * 0.5 + PI * i / rings
			for j in per + 1:
				var lo = TAU * (k * per + j) / seg
				var u = Vector3(cos(la) * cos(lo), sin(la), cos(la) * sin(lo))
				P.append(xf * (c + u * r))
				N.append((xf.basis * u).normalized())
				U.append(Vector2(float(j) / per, float(i) / rings))
		for i in rings:
			for j in per:
				var a = i * (per + 1) + j
				var d = a + per + 1
				if i > 0:
					_tri3(b, s, P, N, U, a, a + 1, d + 1)
				if i < rings - 1:
					_tri3(b, s, P, N, U, a, d + 1, d)

## Tube through local points with radii; cols = colour per segment (or empty).
static func tube(b, g, m, xf, pts, radii, seg, dyn = false, cols = [], caps = true):
	var n = pts.size()
	var rings = []
	var ref = Vector3.UP
	var t0 = (pts[1] - pts[0]).normalized()
	if abs(t0.dot(ref)) > 0.9:
		ref = Vector3.RIGHT
	var n1 = t0.cross(ref).normalized()
	for i in n:
		var t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
		n1 = (n1 - t * n1.dot(t)).normalized()
		var n2 = t.cross(n1).normalized()
		var ring = []
		for j in seg + 1:
			var a = TAU * j / seg
			var dir = n1 * cos(a) + n2 * sin(a)
			ring.append([xf * (pts[i] + dir * radii[i]), (xf.basis * dir).normalized(), Vector2(float(j) / seg, float(i) / n)])
		rings.append(ring)
	for i in n - 1:
		if cols.size() > 0:
			b.cur_color = cols[i % cols.size()]
		var s = b.st(g, m, dyn)
		var P = []
		var N = []
		var U = []
		for rr in [rings[i], rings[i + 1]]:
			for v in rr:
				P.append(v[0]); N.append(v[1]); U.append(v[2])
		for j in seg:
			_tri3(b, s, P, N, U, j, j + 1, seg + 2 + j)
			_tri3(b, s, P, N, U, j, seg + 2 + j, seg + 1 + j)
	if caps:
		for e in [[0, 1], [n - 1, n - 2]]:
			var c = xf * pts[e[0]]
			var nn = (xf.basis * (pts[e[0]] - pts[e[1]])).normalized()
			var s = b.st(g, m, dyn)
			var ring = rings[e[0]]
			for j in seg:
				b.tri(s, c, ring[j][0], ring[j + 1][0], Vector2(0.5, 0.5), Vector2(0, 0), Vector2(1, 0), nn)

## Catmull-Rom resample of a polyline (smooth snakes and handles).
static func smooth(pts, per):
	var out = []
	var n = pts.size()
	for i in n - 1:
		var p0 = pts[max(i - 1, 0)]
		var p1 = pts[i]
		var p2 = pts[i + 1]
		var p3 = pts[min(i + 2, n - 1)]
		for k in per:
			var t = float(k) / per
			var t2 = t * t
			var t3 = t2 * t
			out.append(0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3))
	out.append(pts[n - 1])
	return out

static func S(x, y, z):
	return Basis.from_scale(Vector3(x, y, z))

static func RZ(a):
	return Basis(Vector3(0, 0, 1), a)

static func RX(a):
	return Basis(Vector3(1, 0, 0), a)

# =================================================================== atlases
# redeem_tok.png 512 x 1024
static func TK(x0, y0, x1, y1):
	return R(x0, y0, x1, y1, 512, 1024)
# redeem_desk.png 512 x 512
static func DK(x0, y0, x1, y1):
	return R(x0, y0, x1, y1, 512, 512)
# redeem_toys.png 512 x 512
static func TY(x0, y0, x1, y1):
	return R(x0, y0, x1, y1, 512, 512)
# redeem_cards.png 1024 x 1024: 18 prize fronts (170 x 256), 16 price cards (128 x 64)
static func CARD(i):
	return R((i % 6) * 170 + 2, (i / 6) * 256 + 2, (i % 6) * 170 + 168, (i / 6) * 256 + 254, 1024, 1024)
static func PRICE(i):
	return R((i % 8) * 128, 768 + (i / 8) * 64, (i % 8) * 128 + 128, 768 + (i / 8) * 64 + 64, 1024, 1024)
# redeem_small.png 1024 x 1024: 16 top-down piles (256)
static func PILE(i):
	return R((i % 4) * 256 + 6, (i / 4) * 256 + 6, (i % 4) * 256 + 250, (i / 4) * 256 + 250, 1024, 1024)

const CARD_BOX = [6, 7, 14, 16]          # candy boxes / tubes: full-colour, upright boxes
const CARD_HANG = [0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 17]   # blister cards
const CARD_CUT = [8, 15]                  # lollipop, bubble bottle (cut-outs)

# =================================================================== token changer
static func build_tokens(b, g, xf):
	var W2 = TOK_W * 0.5
	var full = Rect2(0, 0, 1, 1)
	# recessed black kick
	tbox(b, g, "pc_redeem_lam", xf, Vector3(-W2 + 0.02, 0, 0.03), Vector3(W2 - 0.02, 0.06, TOK_D - 0.02), {}, false, ["bottom"])
	# wood-grain laminate pedestal, worn edges painted into every face
	tbox(b, g, "pc_redeem_wood", xf, Vector3(-W2, 0.06, 0), Vector3(W2, 0.99, TOK_D), {"all": full}, false, ["bottom", "top"])
	# service door, 1 cm proud, with a cam lock
	tbox(b, g, "pc_redeem_wood", xf, Vector3(-W2 + 0.045, 0.12, -0.01), Vector3(W2 - 0.045, 0.93, 0.0), {"all": Rect2(0.04, 0.03, 0.92, 0.9)}, false, ["back", "bottom"])
	b.cur_color = Color("#b8b8b0")
	tube(b, g, "pc_redeem_chrome", xf, [Vector3(W2 - 0.09, 0.84, -0.02), Vector3(W2 - 0.09, 0.84, -0.008)], [0.013, 0.013], 10, true)
	b.cur_color = Color.WHITE
	# black cap board with a T-molding edge
	tbox(b, g, "pc_redeem_lam", xf, Vector3(-W2 - 0.008, 0.99, -0.012), Vector3(W2 + 0.008, 1.025, TOK_D + 0.008))
	# the head: wood sides and top, almond steel faceplate
	var hz = 0.05
	tbox(b, g, "pc_redeem_wood", xf, Vector3(-W2 + 0.01, 1.025, hz), Vector3(W2 - 0.01, TOK_H - 0.015, TOK_D - 0.03), {"all": Rect2(0, 0, 1, 0.55)}, false, ["front", "bottom"])
	var fy0 = 1.025
	var fy1 = 1.445
	fq(b, g, "pc_redeem_tok", xf, [Vector3(-W2 + 0.01, fy0, hz), Vector3(W2 - 0.01, fy0, hz), Vector3(W2 - 0.01, fy1, hz), Vector3(-W2 + 0.01, fy1, hz)], Vector3(0, 0, -1), TK(0, 140, 512, 620))
	# lit TOKENS header in a black frame
	tbox(b, g, "pc_redeem_lam", xf, Vector3(-W2 + 0.01, fy1, 0.02), Vector3(W2 - 0.01, TOK_H, hz), {}, false, ["front", "back"])
	fq(b, g, "pc_redeem_toklit", xf, [Vector3(-W2 + 0.025, fy1 + 0.012, 0.018), Vector3(W2 - 0.025, fy1 + 0.012, 0.018), Vector3(W2 - 0.025, TOK_H - 0.012, 0.018), Vector3(-W2 + 0.025, TOK_H - 0.012, 0.018)], Vector3(0, 0, -1), TK(0, 0, 512, 140))
	for sx in [-1.0, 1.0]:
		tbox(b, g, "pc_redeem_alu", xf, Vector3(sx * (W2 - 0.01) - 0.008, fy1, 0.012), Vector3(sx * (W2 - 0.01) + 0.008, TOK_H, 0.022))
	tbox(b, g, "pc_redeem_alu", xf, Vector3(-W2 + 0.002, TOK_H - 0.012, 0.012), Vector3(W2 - 0.002, TOK_H, 0.022))
	tbox(b, g, "pc_redeem_alu", xf, Vector3(-W2 + 0.002, fy1, 0.012), Vector3(W2 - 0.002, fy1 + 0.012, 0.022))
	# bill acceptor bezel (texture recess: x +-0.088, y 1.087..1.237)
	var bz0 = 0.0
	tbox(b, g, "pc_redeem_lam", xf, Vector3(-0.062, 1.09, bz0 + 0.004), Vector3(0.062, 1.255, hz), {}, false, ["front", "back"])
	fq(b, g, "pc_redeem_toklit", xf, [Vector3(-0.062, 1.09, bz0), Vector3(0.062, 1.09, bz0), Vector3(0.062, 1.255, bz0), Vector3(-0.062, 1.255, bz0)], Vector3(0, 0, -1), TK(0, 640, 180, 880))
	# lip over the slot
	tbox(b, g, "pc_redeem_lam", xf, Vector3(-0.05, 1.168, bz0 - 0.012), Vector3(0.05, 1.175, bz0), {}, true)
	# key lock on the faceplate
	b.cur_color = Color("#c8c8c0")
	tube(b, g, "pc_redeem_chrome", xf, [Vector3(0.169, 1.18, hz - 0.012), Vector3(0.169, 1.18, hz)], [0.016, 0.016], 10, true)
	b.cur_color = Color.WHITE
	# stainless token cup (texture opening: x +-0.105, y 1.03..1.075)
	var cz0 = -0.07
	var cy0 = 1.03
	tbox(b, g, "pc_redeem_steel", xf, Vector3(-0.105, cy0 - 0.012, cz0), Vector3(0.105, cy0, hz), {"all": TK(256, 890, 512, 1024)})
	tbox(b, g, "pc_redeem_steel", xf, Vector3(-0.105, cy0, cz0), Vector3(0.105, cy0 + 0.035, cz0 + 0.008), {"all": TK(256, 890, 512, 1024)})
	for sx in [-1.0, 1.0]:
		var x0 = 0.097 if sx > 0 else -0.105
		tbox(b, g, "pc_redeem_steel", xf, Vector3(x0, cy0, cz0), Vector3(x0 + 0.008, cy0 + 0.05, hz), {"all": TK(256, 890, 512, 1024)})
	fq(b, g, "pc_redeem_steel", xf, [Vector3(-0.097, cy0 + 0.001, cz0 + 0.008), Vector3(0.097, cy0 + 0.001, cz0 + 0.008), Vector3(0.097, cy0 + 0.001, hz), Vector3(-0.097, cy0 + 0.001, hz)], Vector3.UP, TK(0, 890, 256, 1024))
	# a hood over the cup so tokens don't bounce out
	tbox(b, g, "pc_redeem_steel", xf, Vector3(-0.105, cy0 + 0.05, cz0 + 0.04), Vector3(0.105, cy0 + 0.058, hz), {"all": TK(256, 890, 512, 1024)})
	# a few brass tokens left in the cup
	b.cur_color = Color("#c9a24a")
	var tp = [Vector3(-0.05, 0, 0.0), Vector3(-0.02, 0.002, -0.02), Vector3(0.03, 0, 0.01), Vector3(0.055, 0.0, -0.03)]
	for p in tp:
		b.cyl(g, "pc_redeem_brass", xf * Vector3(p.x, cy0 + 0.0015 + p.y, p.z), 0.0125, 0.0125, 0.0022, 12, true, false, true)
	b.cur_color = Color.WHITE

# =================================================================== showcase counter
static func build_counter(b, g, xf, L):
	var D = CNT_D
	var H = CNT_H
	var n = max(1, int(round(L / 1.22)))
	var u = L / n
	var x0 = -L * 0.5
	var rng = RandomNumberGenerator.new()
	rng.seed = 1995 + int(L * 100.0)
	# plinth: recessed toe kick, black laminate
	tbox(b, g, "pc_redeem_lam", xf, Vector3(x0, 0, 0.035), Vector3(-x0, 0.10, D - 0.01), {}, false, ["bottom"])
	fq(b, g, "pc_redeem_chrome", xf, [Vector3(x0, 0.0, 0.034), Vector3(-x0, 0.0, 0.034), Vector3(-x0, 0.012, 0.034), Vector3(x0, 0.012, 0.034)], Vector3(0, 0, -1))
	# deck (case floor), light felt-covered board inside, black edge
	tbox(b, g, "pc_redeem_lam", xf, Vector3(x0, 0.10, 0.0), Vector3(-x0, 0.135, D), {}, false, ["bottom", "top"])
	fq(b, g, "pc_redeem_deck", xf, [Vector3(x0, 0.135, 0.0), Vector3(-x0, 0.135, 0.0), Vector3(-x0, 0.135, D), Vector3(x0, 0.135, D)], Vector3.UP)
	# frame: black anodised aluminium rails and posts, chrome edge strips
	var fw = 0.025
	for z in [0.0, D - fw]:
		tbox(b, g, "pc_redeem_alu", xf, Vector3(x0, 0.10, z), Vector3(-x0, 0.145, z + fw))
		tbox(b, g, "pc_redeem_alu", xf, Vector3(x0, H - 0.035, z), Vector3(-x0, H - 0.006, z + fw))
	fq(b, g, "pc_redeem_chrome", xf, [Vector3(x0, H - 0.012, -0.001), Vector3(-x0, H - 0.012, -0.001), Vector3(-x0, H - 0.006, -0.001), Vector3(x0, H - 0.006, -0.001)], Vector3(0, 0, -1))
	fq(b, g, "pc_redeem_chrome", xf, [Vector3(x0, 0.139, -0.001), Vector3(-x0, 0.139, -0.001), Vector3(-x0, 0.145, -0.001), Vector3(x0, 0.145, -0.001)], Vector3(0, 0, -1))
	for i in n + 1:
		var px = x0 + i * u
		var a = clamp(px - fw * 0.5, x0, -x0 - fw)
		for z in [0.0, D - fw]:
			tbox(b, g, "pc_redeem_alu", xf, Vector3(a, 0.145, z), Vector3(a + fw, H - 0.035, z + fw), {}, false, ["top", "bottom"])
		tbox(b, g, "pc_redeem_alu", xf, Vector3(a, H - 0.035, fw), Vector3(a + fw, H - 0.006, D - fw), {}, false, ["front", "back"])
	# glass: front, top, ends, sliding back doors (all dynamic, transparent)
	for i in n:
		var a = x0 + i * u + fw * 0.5
		var c = x0 + (i + 1) * u - fw * 0.5
		fq(b, g, "pc_redeem_glass", xf, [Vector3(a, 0.145, 0.012), Vector3(c, 0.145, 0.012), Vector3(c, H - 0.035, 0.012), Vector3(a, H - 0.035, 0.012)], Vector3(0, 0, -1), Rect2(rng.randf(), 0.0, (c - a) * 1.6, 1.3), true)
		tbox(b, g, "pc_redeem_glass", xf, Vector3(a - fw * 0.5, H - 0.006, 0.0), Vector3(c + fw * 0.5, H + 0.004, D), {"top": Rect2(rng.randf(), 0.2, (c - a) * 1.6, 1.0)}, true, ["bottom"])
		# sliding doors on the clerk side, overlapping in the middle
		var mid = (a + c) * 0.5
		fq(b, g, "pc_redeem_glass", xf, [Vector3(mid + 0.03, 0.15, D - 0.035), Vector3(a, 0.15, D - 0.035), Vector3(a, H - 0.04, D - 0.035), Vector3(mid + 0.03, H - 0.04, D - 0.035)], Vector3(0, 0, 1), Rect2(0.3, 0.1, 0.8, 1.2), true)
		fq(b, g, "pc_redeem_glass", xf, [Vector3(c, 0.15, D - 0.05), Vector3(mid - 0.03, 0.15, D - 0.05), Vector3(mid - 0.03, H - 0.04, D - 0.05), Vector3(c, H - 0.04, D - 0.05)], Vector3(0, 0, 1), Rect2(0.6, 0.0, 0.8, 1.2), true)
		tbox(b, g, "pc_redeem_alu", xf, Vector3(a, 0.145, D - 0.06), Vector3(c, 0.16, D - 0.025), {}, true)
		tbox(b, g, "pc_redeem_chrome", xf, Vector3(mid - 0.07, 0.5, D - 0.033), Vector3(mid - 0.04, 0.6, D - 0.028), {}, true)
		tbox(b, g, "pc_redeem_chrome", xf, Vector3(mid + 0.04, 0.5, D - 0.048), Vector3(mid + 0.07, 0.6, D - 0.043), {}, true)
		# fluorescent strip under the top, behind the front rail
		tbox(b, g, "pc_redeem_alu", xf, Vector3(a + 0.04, H - 0.05, 0.03), Vector3(c - 0.04, H - 0.035, 0.085))
		tbox(b, g, "pc_redeem_tube", xf, Vector3(a + 0.06, H - 0.064, 0.042), Vector3(c - 0.06, H - 0.05, 0.072), {}, false, ["top"])
		# two glass shelves on chrome clips
		for ys in [0.41, 0.67]:
			tbox(b, g, "pc_redeem_glass", xf, Vector3(a + 0.01, ys - 0.008, 0.035), Vector3(c - 0.01, ys, D - 0.075), {"top": Rect2(0, 0, 0.5, 0.3)}, true)
			for cx in [a + 0.02, c - 0.04]:
				for cz in [0.05, D - 0.1]:
					tbox(b, g, "pc_redeem_chrome", xf, Vector3(cx, ys - 0.02, cz), Vector3(cx + 0.02, ys - 0.008, cz + 0.02), {}, true)
		# prizes on the deck and both shelves
		for lv in 3:
			var ys = [0.135, 0.41, 0.67][lv]
			prize_level(b, g, xf, rng, a + 0.02, c - 0.02, ys, lv)
	for e in [[x0, Vector3(-1, 0, 0)], [-x0, Vector3(1, 0, 0)]]:
		var ex = e[0] - e[1].x * 0.012
		if e[1].x < 0:
			fq(b, g, "pc_redeem_glass", xf, [Vector3(ex, 0.145, D - fw), Vector3(ex, 0.145, fw), Vector3(ex, H - 0.035, fw), Vector3(ex, H - 0.035, D - fw)], e[1], Rect2(0.2, 0.0, 0.8, 1.2), true)
		else:
			fq(b, g, "pc_redeem_glass", xf, [Vector3(ex, 0.145, fw), Vector3(ex, 0.145, D - fw), Vector3(ex, H - 0.035, D - fw), Vector3(ex, H - 0.035, fw)], e[1], Rect2(0.5, 0.0, 0.8, 1.2), true)
	counter_top(b, g, xf, rng, L)

## One level of small prizes in one showcase bay: trays of loose prizes in front,
## blister cards and candy boxes standing behind, tent price cards.
static func prize_level(b, g, xf, rng, a, c, ys, lv):
	var D = CNT_D
	# back row: standing cards / boxes, leaning slightly back
	var x = a + rng.randf_range(0.0, 0.03)
	while true:
		var ci
		var r = rng.randf()
		if r < 0.3:
			ci = CARD_BOX[rng.randi() % CARD_BOX.size()]
		elif r < 0.4:
			ci = CARD_CUT[rng.randi() % CARD_CUT.size()]
		else:
			ci = CARD_HANG[rng.randi() % CARD_HANG.size()]
		var h = rng.randf_range(0.15, 0.19) if lv < 2 else rng.randf_range(0.15, 0.2)
		var w = h * 166.0 / 252.0
		if x + w > c:
			break
		var zb = D - 0.11 - rng.randf_range(0.0, 0.04)
		var lean = rng.randf_range(0.06, 0.16)
		var top = Vector3(0, h * cos(lean), h * sin(lean))
		var p0 = Vector3(x, ys + 0.001, zb)
		var p1 = Vector3(x + w, ys + 0.001, zb)
		var nrm = Vector3(0, -sin(lean), -cos(lean))
		if ci in CARD_BOX:
			# a candy box: 3 cm deep; sides take the card's edge colour
			var t = 0.03
			var bx = xf * Transform3D(RX(-lean), p0)
			tbox(b, g, "pc_redeem_cards", bx, Vector3(0, 0, 0), Vector3(w, h, t), {"front": CARD(ci), "all": Rect2(CARD(ci).position + Vector2(0.004, 0.06), Vector2(0.004, 0.1))})
		else:
			fq(b, g, "pc_redeem_cards", xf, [p0, p1, p1 + top, p0 + top], nrm, CARD(ci))
			if not ci in CARD_CUT:
				# plain printed back for the clerk's side
				var bk = -nrm * 0.0015
				fq(b, g, "pc_redeem_desk", xf, [p1 + bk, p0 + bk, p0 + top + bk, p1 + top + bk], -nrm, DK(4, 324, 124, 380))
		x += w + rng.randf_range(0.008, 0.03)
	# front row: trays of loose prizes, each with a tent price card
	x = a + rng.randf_range(0.0, 0.02)
	while true:
		var w = rng.randf_range(0.17, 0.27)
		if x + w > c:
			if c - x > 0.12:
				w = c - x - 0.005
			else:
				break
		var z0 = rng.randf_range(0.06, 0.09)
		var z1 = min(z0 + rng.randf_range(0.2, 0.28), D - 0.16)
		var th = 0.028
		var k = rng.randi() % 16
		tbox(b, g, "pc_redeem_lam", xf, Vector3(x, ys, z0), Vector3(x + w, ys + th, z1), {}, false, ["bottom", "top"])
		fq(b, g, "pc_redeem_small", xf, [Vector3(x, ys + th, z0), Vector3(x + w, ys + th, z0), Vector3(x + w, ys + th, z1), Vector3(x, ys + th, z1)], Vector3.UP, PILE(k))
		# a few loose 3D pieces heaped on the ball and gumball trays
		if k == 0 or k == 13:
			var rr = 0.016 if k == 0 else 0.011
			for j in 3:
				b.cur_color = [Color("#e8283c"), Color("#2878e6"), Color("#fac81e"), Color("#32be50"), Color("#f06ea0")][rng.randi() % 5]
				ell(b, g, "pc_redeem_vinyl", xf, Vector3(x + rng.randf_range(0.03, w - 0.03), ys + th + rr * 0.7, rng.randf_range(z0 + 0.03, z1 - 0.03)), S(rr, rr, rr), 7, 4, true)
			b.cur_color = Color.WHITE
		# tent price card at the tray front
		var pc = [0, 1, 2, 3, 4, 2, 1, 3][rng.randi() % 8] + (1 if lv == 2 else 0)
		var cw = 0.055
		var cx = x + w * 0.5 - cw * 0.5
		var ch = 0.028
		var tl = 0.45
		fq(b, g, "pc_redeem_cards", xf, [Vector3(cx, ys + th, z0 - 0.003), Vector3(cx + cw, ys + th, z0 - 0.003), Vector3(cx + cw, ys + th + ch * cos(tl), z0 - 0.003 + ch * sin(tl)), Vector3(cx, ys + th + ch * cos(tl), z0 - 0.003 + ch * sin(tl))], Vector3(0, -sin(tl), -cos(tl)), PRICE(pc), true)
		x += w + rng.randf_range(0.01, 0.025)

## Register, ticket-counting machine and tickets on top of the glass.
static func counter_top(b, g, xf, rng, L):
	var D = CNT_D
	var Y = CNT_H + 0.004
	var side = DK(270, 300, 500, 400)
	# --- cash register near the right end, keyboard toward the clerk
	var rx = L * 0.5 - 0.42
	tbox(b, g, "pc_redeem_desk", xf, Vector3(rx - 0.2, Y, 0.13), Vector3(rx + 0.2, Y + 0.10, 0.55), {"all": side, "back": DK(256, 0, 512, 128)}, false, ["bottom"])
	tbox(b, g, "pc_redeem_desk", xf, Vector3(rx - 0.19, Y + 0.10, 0.13), Vector3(rx + 0.19, Y + 0.165, 0.30), {"all": side}, false, ["bottom", "back"])
	var k0 = Vector3(rx - 0.19, Y + 0.165, 0.30)
	var k1 = Vector3(rx + 0.19, Y + 0.165, 0.30)
	var k2 = Vector3(rx + 0.19, Y + 0.115, 0.53)
	var k3 = Vector3(rx - 0.19, Y + 0.115, 0.53)
	var kn = (k1 - k0).cross(k3 - k0).normalized()
	if kn.y < 0:
		kn = -kn
	# keyboard read from the clerk's side: their left is +x
	fq(b, g, "pc_redeem_desk", xf, [k2, k3, k0, k1], kn, DK(0, 0, 256, 256))
	for sx in [-0.19, 0.19]:
		var nx = Vector3(sign(sx), 0, 0)
		fq(b, g, "pc_redeem_desk", xf, [Vector3(rx + sx, Y + 0.10, 0.30), Vector3(rx + sx, Y + 0.10, 0.53), Vector3(rx + sx, Y + 0.115, 0.53), Vector3(rx + sx, Y + 0.165, 0.30)], nx, side)
	fq(b, g, "pc_redeem_desk", xf, [Vector3(rx + 0.19, Y + 0.10, 0.53), Vector3(rx - 0.19, Y + 0.10, 0.53), Vector3(rx - 0.19, Y + 0.115, 0.53), Vector3(rx + 0.19, Y + 0.115, 0.53)], Vector3(0, 0, 1), side)
	# receipt curling out of the printer
	fq(b, g, "pc_redeem_desk", xf, [Vector3(rx - 0.14, Y + 0.165, 0.2), Vector3(rx - 0.08, Y + 0.165, 0.2), Vector3(rx - 0.08, Y + 0.22, 0.215), Vector3(rx - 0.14, Y + 0.22, 0.215)], Vector3(0, 0, -1), DK(0, 320, 128, 384), true)
	# customer pole display facing the customer
	b.cur_color = Color("#3a3a3a")
	b.cyl(g, "vcolor", xf * Vector3(rx + 0.12, Y + 0.165, 0.18), 0.011, 0.011, 0.09, 8, false, false, true)
	b.cur_color = Color.WHITE
	tbox(b, g, "pc_redeem_desk", xf, Vector3(rx + 0.05, Y + 0.25, 0.155), Vector3(rx + 0.19, Y + 0.305, 0.195), {"all": DK(258, 290, 262, 294)}, true)
	fq(b, g, "pc_redeem_led", xf, [Vector3(rx + 0.058, Y + 0.258, 0.1545), Vector3(rx + 0.182, Y + 0.258, 0.1545), Vector3(rx + 0.182, Y + 0.297, 0.1545), Vector3(rx + 0.058, Y + 0.297, 0.1545)], Vector3(0, 0, -1), DK(256, 128, 384, 160), true)
	# --- ticket-counting machine near the left end, display toward the customer
	var tx = -L * 0.5 + 0.34
	var grey = DK(258, 196, 262, 200)
	tbox(b, g, "pc_redeem_desk", xf, Vector3(tx - 0.13, Y, 0.15), Vector3(tx + 0.13, Y + 0.26, 0.50), {"all": grey, "front": DK(256, 160, 512, 288)}, false, ["bottom"])
	fq(b, g, "pc_redeem_led", xf, [Vector3(tx - 0.085, Y + 0.134, 0.1485), Vector3(tx + 0.085, Y + 0.134, 0.1485), Vector3(tx + 0.085, Y + 0.2275, 0.1485), Vector3(tx - 0.085, Y + 0.2275, 0.1485)], Vector3(0, 0, -1), DK(384, 128, 512, 160))
	fq(b, g, "pc_redeem_desk", xf, [Vector3(tx - 0.07, Y + 0.2605, 0.24), Vector3(tx + 0.07, Y + 0.2605, 0.24), Vector3(tx + 0.07, Y + 0.2605, 0.30), Vector3(tx - 0.07, Y + 0.2605, 0.30)], Vector3.UP, DK(0, 384, 128, 448))
	# a strip of tickets being fed into the throat, the tail lying on the glass
	var tf = DK(0, 256, 128, 320)
	var tpts = [Vector3(tx, Y + 0.262, 0.27), Vector3(tx, Y + 0.30, 0.235), Vector3(tx, Y + 0.32, 0.19), Vector3(tx, Y + 0.30, 0.15),
		Vector3(tx + 0.0, Y + 0.25, 0.12), Vector3(tx + 0.01, Y + 0.20, 0.10), Vector3(tx + 0.02, Y + 0.15, 0.085), Vector3(tx + 0.03, Y + 0.10, 0.075),
		Vector3(tx + 0.04, Y + 0.05, 0.07), Vector3(tx + 0.05, Y + 0.004, 0.06), Vector3(tx + 0.06, Y + 0.002, 0.035)]
	for i in tpts.size() - 1:
		var p = tpts[i]
		var q = tpts[i + 1]
		var t = (q - p)
		var side_v = Vector3(0.0255, 0, 0)
		var nn = side_v.cross(t).normalized()
		if nn.z > 0:
			nn = -nn
		fq(b, g, "pc_redeem_desk", xf, [p - side_v, p + side_v, q + side_v, q - side_v], nn, tf, true)
	# fanfold ticket bricks beside the counter machine
	var tk = {"top": tf, "all": DK(130, 258, 254, 318)}
	for j in 3:
		var bp = Vector3(tx + 0.2 + j * 0.035, Y, 0.20 + (j % 2) * 0.05)
		var hh = [0.045, 0.03, 0.06][j]
		var bx = xf * Transform3D(Basis(Vector3.UP, rng.randf_range(-0.4, 0.4)), bp)
		tbox(b, g, "pc_redeem_desk", bx, Vector3(-0.0127, 0, -0.0255), Vector3(0.0127, hh, 0.0255), tk, true, ["bottom"])
	# a few loose tickets
	for j in 4:
		var bp = Vector3(tx + 0.18 + j * 0.05, Y + 0.0015 + j * 0.0003, 0.08 + rng.randf_range(-0.02, 0.03))
		var bx = xf * Transform3D(Basis(Vector3.UP, rng.randf_range(-1.2, 1.2)), bp)
		fq(b, g, "pc_redeem_desk", bx, [Vector3(-0.0255, 0, -0.0127), Vector3(0.0255, 0, -0.0127), Vector3(0.0255, 0, 0.0127), Vector3(-0.0255, 0, 0.0127)], Vector3.UP, tf, true)

# =================================================================== plush
const PLUSH_COLS = [["#7a4e2c", "#d6b088"], ["#efeae0", "#f6c4cc"], ["#ff4fa0", "#ffe0ee"], ["#32b8e2", "#f4fbff"],
	["#8d55c8", "#e6d6ff"], ["#ffcc2e", "#fff2c2"], ["#4ec840", "#e4ffd4"], ["#c09060", "#f2e0c4"],
	["#262626", "#eeeeee"], ["#e23a3a", "#ffe0e0"], ["#f08a2a", "#fff0d8"], ["#a8d8f0", "#ffffff"]]

## A generic plush animal ("bear", "dog", "bunny", "ball"), height h, sitting at local p
## (bottom centre) or, with hang = true, hanging from local p by a loop. Faces -z.
static func plush(b, g, xf, kind, p, h, yaw, cols, hang = false):
	var base = p - Vector3(0, h + 0.015, 0) if hang else p
	var pf = xf * Transform3D(Basis(Vector3.UP, yaw), base)
	var c1 = Color(cols[0])
	var c2 = Color(cols[1])
	var lod = plush_lod(h)
	var sb = [7, 8, 9][lod]
	var rb = [4, 5, 6][lod]
	var sp = [5, 6, 6][lod]
	var rp = [3, 3, 4][lod]
	var M = "pc_redeem_plush"
	b.cur_color = c1
	if kind == "ball":
		ell(b, g, M, pf, Vector3(0, 0.5 * h, 0), S(0.5 * h, 0.48 * h, 0.5 * h), sb + 2, rb + 1, false, 3.0)
		for sx in [-1.0, 1.0]:
			ell(b, g, M, pf, Vector3(sx * 0.2 * h, 0.06 * h, -0.2 * h), S(0.12 * h, 0.07 * h, 0.15 * h), sp, rp)
		face(b, g, pf, Vector3(0, 0.6 * h, -0.47 * h), h * 1.4, c2, false)
		b.cur_color = Color.WHITE
		return
	# body + belly patch
	ell(b, g, M, pf, Vector3(0, 0.30 * h, 0.02 * h), S(0.25 * h, 0.28 * h, 0.22 * h), sb, rb, false, 3.0)
	if lod > 0:
		b.cur_color = c2
		ell(b, g, M, pf, Vector3(0, 0.29 * h, -0.135 * h), S(0.16 * h, 0.18 * h, 0.08 * h), sp, rp)
		b.cur_color = c1
	# head
	ell(b, g, M, pf, Vector3(0, 0.70 * h, -0.02 * h), S(0.22 * h, 0.2 * h, 0.2 * h), sb, rb, false, 3.0)
	# ears
	for sx in [-1.0, 1.0]:
		match kind:
			"dog":
				ell(b, g, M, pf, Vector3(sx * 0.2 * h, 0.64 * h, 0.0), RZ(sx * 0.3) * S(0.045 * h, 0.15 * h, 0.08 * h), sp, rp)
			"bunny":
				ell(b, g, M, pf, Vector3(sx * 0.08 * h, 0.98 * h, 0.0), RZ(-sx * 0.18) * S(0.05 * h, 0.17 * h, 0.03 * h), sp, rp)
			_:
				ell(b, g, M, pf, Vector3(sx * 0.15 * h, 0.87 * h, 0.0), RZ(-sx * 0.5) * S(0.07 * h, 0.07 * h, 0.035 * h), sp, rp)
	# arms
	for sx in [-1.0, 1.0]:
		if hang:
			ell(b, g, M, pf, Vector3(sx * 0.23 * h, 0.34 * h, -0.04 * h), RZ(sx * 0.25) * S(0.07 * h, 0.15 * h, 0.07 * h), sp, rp)
		else:
			ell(b, g, M, pf, Vector3(sx * 0.22 * h, 0.38 * h, -0.08 * h), RZ(sx * 0.5) * RX(-0.5) * S(0.075 * h, 0.15 * h, 0.075 * h), sp, rp)
	# legs: sitting (forward) or dangling
	for sx in [-1.0, 1.0]:
		if hang:
			ell(b, g, M, pf, Vector3(sx * 0.11 * h, 0.06 * h, -0.04 * h), S(0.085 * h, 0.14 * h, 0.085 * h), sp, rp)
		else:
			# limbs: poles along the long axis so the profile stays round
			ell(b, g, M, pf, Vector3(sx * 0.13 * h, 0.085 * h, -0.17 * h), RX(PI * 0.5) * S(0.085 * h, 0.15 * h, 0.085 * h), sp, rp)
			if lod == 2:
				b.cur_color = c2
				ell(b, g, M, pf, Vector3(sx * 0.13 * h, 0.085 * h, -0.305 * h), RX(PI * 0.5) * S(0.062 * h, 0.012 * h, 0.062 * h), 8, 2)
				b.cur_color = c1
	# muzzle
	b.cur_color = c2
	if kind == "dog":
		ell(b, g, M, pf, Vector3(0, 0.645 * h, -0.2 * h), S(0.1 * h, 0.08 * h, 0.1 * h), sp, rp)
	else:
		ell(b, g, M, pf, Vector3(0, 0.655 * h, -0.19 * h), S(0.09 * h, 0.07 * h, 0.06 * h), sp, rp)
	face(b, g, pf, Vector3(0, 0.74 * h, -0.19 * h), h, c2, kind == "dog")
	# a ribbon on some of them
	if lod > 0 and int(h * 1000.0) % 3 == 0:
		b.cur_color = Color("#d81830")
		for sx in [-1.0, 1.0]:
			ell(b, g, "pc_redeem_vinyl", pf, Vector3(sx * 0.05 * h, 0.52 * h, -0.17 * h), RZ(sx * 0.3) * S(0.055 * h, 0.03 * h, 0.018 * h), 6, 3, true)
	if hang:
		b.cur_color = Color("#e8e8e8")
		tube(b, g, "vcolor", xf, [p - Vector3(0, 0.0, 0), base + Vector3(0, 0.88 * h, -0.02 * h)], [0.002, 0.002], 3, true, [], false)
	b.cur_color = Color.WHITE

static func plush_lod(h):
	return 2 if h > 0.42 else (1 if h > 0.24 else 0)

## Approximate static triangles of one plush (budgeting the prize wall).
static func plush_cost(kind, h):
	var lod = plush_lod(h)
	if kind == "ball":
		return [72, 100, 130][lod] + [40, 48, 72][lod]
	return [224, 320, 492][lod]

## Eyes and nose (glossy black beads), centred at local c (between the eyes).
static func face(b, g, pf, c, h, c2, dog):
	b.cur_color = Color("#0c0c0e")
	var er = 0.022 * h
	for sx in [-1.0, 1.0]:
		ell(b, g, "pc_redeem_bead", pf, c + Vector3(sx * 0.075 * h, 0, 0), S(er, er, er * 0.8), 5, 3, true)
	var nr = 0.034 * h if dog else 0.028 * h
	ell(b, g, "pc_redeem_bead", pf, c + Vector3(0, -0.05 * h, -0.07 * h if dog else -0.06 * h), S(nr, nr * 0.75, nr * 0.7), 5, 3, true)

# =================================================================== prize wall
static func build_prizewall(b, g, xf, L, H):
	var D = WALL_D
	H = clamp(H, 2.0, 3.2)
	var x0 = -L * 0.5
	var rng = RandomNumberGenerator.new()
	rng.seed = 1995 + int(L * 100.0) + int(H * 10.0)
	# base cabinet (storage under the display), black laminate, chrome kick strip
	tbox(b, g, "pc_redeem_lam", xf, Vector3(x0, 0, 0.06), Vector3(-x0, 0.08, D), {}, false, ["bottom"])
	tbox(b, g, "pc_redeem_lam", xf, Vector3(x0, 0.08, 0.02), Vector3(-x0, 0.80, D), {}, false, ["bottom", "top"])
	tbox(b, g, "pc_redeem_shelf", xf, Vector3(x0 - 0.01, 0.80, 0.0), Vector3(-x0 + 0.01, 0.83, D), {}, false, ["bottom"])
	var nd = max(2, int(round(L / 0.6)))
	for i in nd:
		var dx = x0 + (i + 0.5) * L / nd
		if i > 0:
			var sx = x0 + i * L / nd
			fq(b, g, "pc_redeem_alu", xf, [Vector3(sx - 0.002, 0.1, 0.019), Vector3(sx + 0.002, 0.1, 0.019), Vector3(sx + 0.002, 0.78, 0.019), Vector3(sx - 0.002, 0.78, 0.019)], Vector3(0, 0, -1))
		var hx = dx + (0.2 if i % 2 == 0 else -0.2) * L / nd / 0.6 * 0.6
		hx = clamp(hx, x0 + i * L / nd + 0.04, x0 + (i + 1) * L / nd - 0.04)
		tbox(b, g, "pc_redeem_chrome", xf, Vector3(hx - 0.006, 0.6, 0.0), Vector3(hx + 0.006, 0.72, 0.02), {}, true)
	# slatwall
	var sy0 = 0.83
	var sy1 = H - 0.4
	tbox(b, g, "pc_redeem_slat", xf, Vector3(x0, sy0, D - 0.02), Vector3(-x0, sy1, D), {}, false, ["back", "bottom", "top"])
	for sx in [x0, -x0 - 0.02]:
		tbox(b, g, "pc_redeem_alu", xf, Vector3(sx, sy0, D - 0.04), Vector3(sx + 0.02, sy1, D))
	# shelves with price channels
	var ya = sy0 + 0.47
	var yb = ya + 0.44
	var shelves = [[0.83, 0.02]]
	shelves.append([ya, D - 0.31])
	var has_b = yb + 0.24 < sy1 - 0.1
	if has_b:
		shelves.append([yb, D - 0.22])
	for si in range(1, shelves.size()):
		var ys = shelves[si][0]
		var zf = shelves[si][1]
		tbox(b, g, "pc_redeem_shelf", xf, Vector3(x0 + 0.02, ys - 0.02, zf), Vector3(-x0 - 0.02, ys, D - 0.02), {}, false, [])
		var nb = max(2, int(round(L / 0.6)) + 1)
		for k in nb:
			var bx = x0 + 0.08 + k * (L - 0.16) / (nb - 1)
			tbox(b, g, "pc_redeem_alu", xf, Vector3(bx - 0.005, ys - 0.1, zf + 0.04), Vector3(bx + 0.005, ys - 0.02, D - 0.02), {}, true)
	for si in shelves.size():
		var ys = shelves[si][0]
		var zf = shelves[si][1]
		fq(b, g, "pc_redeem_tags", xf, [Vector3(x0 + 0.02, ys - 0.03, zf - 0.004), Vector3(-x0 - 0.02, ys - 0.03, zf - 0.004), Vector3(-x0 - 0.02, ys + 0.0, zf - 0.004), Vector3(x0 + 0.02, ys + 0.0, zf - 0.004)], Vector3(0, 0, -1), R(0, 896, 1024, 928, 1024, 1024))
	# the levels
	# plush are the triangle cost: each level gets a per-metre share (~1,400 tris/m in all)
	wall_level(b, g, xf, rng, x0, 0.83, 0.03, D - 0.02, 0.62, 2, 0.02, 760.0)
	wall_level(b, g, xf, rng, x0, ya, D - 0.31, D - 0.02, 0.36, 1, D - 0.31, 520.0)
	if has_b:
		wall_level(b, g, xf, rng, x0, yb, D - 0.22, D - 0.02, 0.21, 0, D - 0.22, 140.0)
	# hooks along the top with hanging plush, snakes and inflatables
	var yh = sy1 - 0.06
	var x = x0 + 0.22
	var kinds = ["snake", "hbear", "bat", "ball", "hdog", "snake", "hbunny", "bat", "hbear", "ball"]
	var ki = rng.randi() % kinds.size()
	while x < -x0 - 0.2:
		var kd = kinds[ki % kinds.size()]
		ki += 1
		b.cur_color = Color("#d8d8d8")
		tube(b, g, "pc_redeem_chrome", xf, [Vector3(x, yh, D - 0.02), Vector3(x, yh, 0.09), Vector3(x, yh + 0.03, 0.07)], [0.003, 0.003, 0.003], 4, true, [], false)
		b.cur_color = Color.WHITE
		var hp = Vector3(x, yh, 0.10)
		var cols = PLUSH_COLS[rng.randi() % PLUSH_COLS.size()]
		match kd:
			"snake":
				hang_snake(b, g, xf, rng, hp)
			"bat":
				hang_bat(b, g, xf, rng, hp)
			"ball":
				var r = 0.15
				ell_gores(b, g, "pc_redeem_vinyl", xf, hp - Vector3(0, r + 0.03, 0), r, 12, 6, [Color("#e82a2a"), Color("#f8f8f0"), Color("#2a6ae8"), Color("#f8d020"), Color("#f8f8f0"), Color("#30b040")])
				b.cur_color = Color("#e8e8e8")
				tube(b, g, "vcolor", xf, [hp, hp - Vector3(0, 0.03, 0)], [0.002, 0.002], 3, true, [], false)
			"hdog":
				plush(b, g, xf, "dog", hp, rng.randf_range(0.34, 0.42), rng.randf_range(-0.25, 0.25), cols, true)
			"hbunny":
				plush(b, g, xf, "bunny", hp, rng.randf_range(0.32, 0.4), rng.randf_range(-0.25, 0.25), cols, true)
			_:
				plush(b, g, xf, "bear", hp, rng.randf_range(0.36, 0.46), rng.randf_range(-0.25, 0.25), cols, true)
		# hang tag
		var tg = Vector3(x + 0.04, yh - 0.1, 0.07)
		fq(b, g, "pc_redeem_tags", xf, [tg, tg + Vector3(0.05, 0, 0), tg + Vector3(0.05, 0.065, 0), tg + Vector3(0, 0.065, 0)], Vector3(0, 0, -1), R(2, 956, 62, 1022, 1024, 1024), true)
		x += rng.randf_range(0.38, 0.5)
	# header: black canopy box, lit PRIZES panel in the middle, ticket band either side
	var hy0 = H - 0.4
	tbox(b, g, "pc_redeem_lam", xf, Vector3(x0, hy0, 0.0), Vector3(-x0, H, D), {}, false, ["back"])
	var pw = min(1.44, L - 0.1)
	var sy = hy0 + 0.02
	var ty = H - 0.02
	fq(b, g, "pc_redeem_header", xf, [Vector3(-pw * 0.5, sy, -0.004), Vector3(pw * 0.5, sy, -0.004), Vector3(pw * 0.5, ty, -0.004), Vector3(-pw * 0.5, ty, -0.004)], Vector3(0, 0, -1), Rect2(0, 0, 1, 1))
	var side_w = (L - 0.04 - pw) * 0.5
	if side_w > 0.05:
		var reps = side_w / ((ty - sy) * 4.0)
		fq(b, g, "pc_redeem_band", xf, [Vector3(x0 + 0.02, sy, -0.004), Vector3(-pw * 0.5, sy, -0.004), Vector3(-pw * 0.5, ty, -0.004), Vector3(x0 + 0.02, ty, -0.004)], Vector3(0, 0, -1), Rect2(1.0 - fmod(reps, 1.0), 0, reps, 1))
		fq(b, g, "pc_redeem_band", xf, [Vector3(pw * 0.5, sy, -0.004), Vector3(-x0 - 0.02, sy, -0.004), Vector3(-x0 - 0.02, ty, -0.004), Vector3(pw * 0.5, ty, -0.004)], Vector3(0, 0, -1), Rect2(0, 0, reps, 1))
	for xx in [-pw * 0.5, pw * 0.5]:
		tbox(b, g, "pc_redeem_chrome", xf, Vector3(xx - 0.006, sy, -0.012), Vector3(xx + 0.006, ty, -0.002))
	tbox(b, g, "pc_redeem_chrome", xf, Vector3(x0, H - 0.014, -0.01), Vector3(-x0, H - 0.002, 0.0))
	tbox(b, g, "pc_redeem_chrome", xf, Vector3(x0, hy0 + 0.002, -0.01), Vector3(-x0, hy0 + 0.014, 0.0))
	# diffuser strip under the canopy, lighting the prizes below
	fq(b, g, "pc_redeem_tube", xf, [Vector3(x0 + 0.05, hy0 - 0.002, 0.24), Vector3(-x0 - 0.05, hy0 - 0.002, 0.24), Vector3(-x0 - 0.05, hy0 - 0.002, 0.06), Vector3(x0 + 0.05, hy0 - 0.002, 0.06)], Vector3.DOWN)
	# sign lamps on short arms over the header, lighting it from above
	var nl = max(2, int(round(L / 1.0)))
	for i in nl:
		var lx = x0 + (i + 0.5) * L / nl
		tbox(b, g, "pc_redeem_alu", xf, Vector3(lx - 0.008, H, 0.02), Vector3(lx + 0.008, H + 0.012, 0.2), {}, true)
		tube(b, g, "pc_redeem_alu", xf, [Vector3(lx, H + 0.006, 0.03), Vector3(lx, H + 0.09, -0.06), Vector3(lx, H + 0.1, -0.14)], [0.006, 0.006, 0.006], 4, true, [], false)
		b.cyl(g, "pc_redeem_alu", xf * Vector3(lx, H + 0.05, -0.17), 0.045, 0.035, 0.08, 8, true, false, true)
		b.cyl(g, "pc_redeem_lamp", xf * Vector3(lx, H + 0.046, -0.17), 0.036, 0.036, 0.004, 8, false, true, true)
	b.cur_color = Color.WHITE

## Fill one display level of the prize wall from x0 to -x0.
## maxh = tallest item; size = 2 jumbo, 1 medium, 0 small.
static func wall_level(b, g, xf, rng, x0, ys, zf, zb, maxh, size, ztag, rate):
	var x = x0 + rng.randf_range(0.03, 0.08)
	var spent = 0.0
	var pool
	match size:
		2:
			pool = ["bear", "boom", "dog", "box", "bear", "bunny", "boom", "bear", "box"]
		1:
			pool = ["bear", "boom", "dog", "box", "ball", "bunny", "boom", "bear"]
		_:
			pool = ["box", "ball", "box", "bear", "box", "ball", "box", "bunny"]
	var pk = rng.randi() % pool.size()
	while true:
		var k = pool[pk % pool.size()]
		pk += 1 + (rng.randi() % 2)
		var w
		var h
		match k:
			"boom":
				w = 0.46; h = 0.24
			"box":
				w = 0.3 if size == 2 else 0.15; h = 0.22 if size == 2 else 0.15
			"ball":
				h = maxh * rng.randf_range(0.55, 0.7); w = h * 1.0
			_:
				h = maxh * rng.randf_range(0.82, 1.0); w = h * 0.72
		if k in ["bear", "dog", "bunny", "ball"]:
			var cost = plush_cost(k, h)
			if spent + cost > rate * (x + w - x0):
				# over budget here: a boxed prize or a stereo instead
				k = "boom" if size == 1 and rng.randf() < 0.5 else "box"
				w = 0.46 if k == "boom" else (0.3 if size == 2 else 0.15)
				h = 0.24 if k == "boom" else (0.22 if size == 2 else 0.15)
			else:
				spent += cost
		if x + w > -x0 - 0.02:
			break
		var cx = x + w * 0.5
		var cols = PLUSH_COLS[rng.randi() % PLUSH_COLS.size()]
		var price = 8 + (rng.randi() % 8)
		match k:
			"boom":
				var dz = 0.12
				var z0 = zb - dz - 0.02
				var bi = rng.randi() % 2
				var face_r = TY(0, 0, 256, 128) if bi == 0 else TY(256, 0, 512, 128)
				var side_r = TY(4, 132, 124, 252) if bi == 0 else TY(132, 132, 252, 252)
				var bxf = xf * Transform3D(Basis(Vector3.UP, rng.randf_range(-0.12, 0.12)), Vector3(cx, ys, z0 + dz * 0.5))
				tbox(b, g, "pc_redeem_toys", bxf, Vector3(-w * 0.5, 0, -dz * 0.5), Vector3(w * 0.5, h, dz * 0.5), {"front": face_r, "all": side_r}, false, ["bottom"])
				b.cur_color = Color("#bdbdbd")
				tube(b, g, "pc_redeem_chrome", bxf, smooth([Vector3(-0.17, h, 0), Vector3(-0.15, h + 0.06, 0), Vector3(0.15, h + 0.06, 0), Vector3(0.17, h, 0)], 3), [0.008, 0.008, 0.008, 0.008, 0.008, 0.008, 0.008, 0.008, 0.008, 0.008], 5, true, [], false)
				tube(b, g, "pc_redeem_chrome", bxf, [Vector3(0.19, h, 0.03), Vector3(0.12, h + 0.3, 0.05)], [0.003, 0.0015], 4, true)
				b.cur_color = Color.WHITE
				price = 10 + (rng.randi() % 4)
			"box":
				var dz = min(zb - zf - 0.02, 0.2 if size == 2 else 0.12)
				var bi = rng.randi() % 4
				var bxf = xf * Transform3D(Basis(Vector3.UP, rng.randf_range(-0.1, 0.1)), Vector3(cx, ys, zb - dz * 0.5 - 0.02))
				tbox(b, g, "pc_redeem_toys", bxf, Vector3(-w * 0.5, 0, -dz * 0.5), Vector3(w * 0.5, h, dz * 0.5), {"front": TY(bi * 128, 256, bi * 128 + 128, 384), "all": TY(4, 388, 124, 508)}, false, ["bottom"])
			"ball":
				plush(b, g, xf, "ball", Vector3(cx, ys, zb - h * 0.5 - 0.02), h, rng.randf_range(-0.3, 0.3), cols)
			_:
				var zc = zb - 0.25 * h - 0.03
				zc = max(zc, zf + 0.3 * h)
				plush(b, g, xf, k, Vector3(cx, ys, zc), h, rng.randf_range(-0.3, 0.3), cols)
		# price tag in the shelf's channel under the item
		var tw = 0.07
		fq(b, g, "pc_redeem_tags", xf, [Vector3(cx - tw * 0.5, ys - 0.029, ztag - 0.007), Vector3(cx + tw * 0.5, ys - 0.029, ztag - 0.007), Vector3(cx + tw * 0.5, ys + 0.006, ztag - 0.007), Vector3(cx - tw * 0.5, ys + 0.006, ztag - 0.007)], Vector3(0, 0, -1), PRICE(min(price, 15)), true)
		x += w + rng.randf_range(0.02, 0.07)

static func hang_snake(b, g, xf, rng, hp):
	var cols_sets = [[Color("#3ad040"), Color("#f0e020")], [Color("#9a40d8"), Color("#40d0f0")], [Color("#f05a20"), Color("#202020")], [Color("#ff4fa0"), Color("#ffffff")]]
	var cs = cols_sets[rng.randi() % cols_sets.size()]
	var dl = rng.randf_range(0.6, 0.8)
	var dr = rng.randf_range(0.25, 0.35)
	# draped over the hook: a long tail down the back side, the head end hanging in front
	var raw = [hp + Vector3(0.05, -dl, 0.02), hp + Vector3(0.06, -dl * 0.6, 0.03), hp + Vector3(0.05, -0.15, 0.03), hp + Vector3(0.0, 0.035, 0.0),
		hp + Vector3(-0.05, -0.12, -0.03), hp + Vector3(-0.06, -dr, -0.05), hp + Vector3(-0.03, -dr - 0.1, -0.1)]
	var pts = smooth(raw, 2)
	var radii = []
	var cols = []
	for i in pts.size():
		var t = float(i) / (pts.size() - 1)
		radii.append(lerp(0.015, 0.042, smoothstep(0.0, 0.45, t)) if t < 0.86 else 0.05)
		cols.append(cs[i % 2])
	b.cur_color = cs[0]
	tube(b, g, "pc_redeem_plush", xf, pts, radii, 6, false, cols, true)
	# head: eyes and a red felt tongue
	var hd = pts[pts.size() - 1]
	var dirv = (pts[pts.size() - 1] - pts[pts.size() - 2]).normalized()
	b.cur_color = Color("#0c0c0e")
	for sx in [-1.0, 1.0]:
		ell(b, g, "pc_redeem_bead", xf, hd + Vector3(sx * 0.028, 0.025, -0.03), S(0.01, 0.01, 0.01), 5, 3, true)
	b.cur_color = Color("#e01828")
	var tq = hd + dirv * 0.05
	fq(b, g, "vcolor", xf, [tq + Vector3(-0.007, 0, 0), tq + Vector3(0.007, 0, 0), tq + dirv * 0.05 + Vector3(0.007, 0, 0), tq + dirv * 0.05 + Vector3(-0.007, 0, 0)], Vector3(0, 0, -1), Rect2(0, 0, 1, 1), true)
	b.cur_color = Color.WHITE

static func hang_bat(b, g, xf, rng, hp):
	var cs = [[Color("#ff3a8a"), Color("#ffe040")], [Color("#30a0ff"), Color("#f0f0f0")], [Color("#ff7a20"), Color("#30d050")]][rng.randi() % 3]
	var top = hp - Vector3(0, 0.03, 0)
	var Lb = rng.randf_range(0.6, 0.75)
	# hangs knob-up: knob, handle, then the fat barrel at the bottom
	var segs = [[0.035, 0.035, 0.03, 0], [0.028, 0.028, 0.16, 1], [0.03, 0.065, Lb * 0.4, 0], [0.068, 0.068, Lb * 0.35, 1], [0.068, 0.05, 0.05, 0]]
	var y = top.y
	for s in segs:
		y -= s[2]
		b.cur_color = cs[s[3]]
		b.cyl(g, "pc_redeem_vinyl", xf * Vector3(top.x, y, top.z), s[1], s[0], s[2], 10, false, s == segs[segs.size() - 1], false)
	b.cur_color = Color("#e8e8e8")
	tube(b, g, "vcolor", xf, [hp, top], [0.002, 0.002], 3, true, [], false)
	b.cur_color = Color.WHITE

# =================================================================== materials
## Material "pc_redeem_<key>": fill m and return true, or false for an unknown key.
static func fill_mat(m, key, b):
	match key:
		"wood":
			m.albedo_texture = b.tex("pc/redeem_wood.png"); m.roughness = 0.55
		"tok":
			m.albedo_texture = b.tex("pc/redeem_tok.png"); m.roughness = 0.5; m.metallic = 0.15
		"toklit":
			var t = b.tex("pc/redeem_tok.png")
			m.albedo_texture = t; m.roughness = 0.4
			_emit(m, t, 1.4)
		"steel":
			m.albedo_texture = b.tex("pc/redeem_tok.png"); m.metallic = 0.85; m.roughness = 0.32
		"lam":
			m.albedo_texture = b.tex("pc/redeem_scuff.png"); m.albedo_color = Color("#1c1b1d"); m.roughness = 0.45
		"alu":
			m.albedo_color = Color("#1e1e22"); m.metallic = 0.7; m.roughness = 0.38
		"chrome":
			m.albedo_color = Color("#d0d0d6"); m.metallic = 0.75; m.roughness = 0.2
		"brass":
			m.albedo_color = Color("#c9a24a"); m.metallic = 0.9; m.roughness = 0.3
		"glass":
			m.albedo_texture = b.tex("pc/redeem_glass.png")
			m.albedo_color = Color(0.8, 0.95, 0.93, 1.0)
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
			m.roughness = 0.04; m.metallic_specular = 0.7
		"tube":
			m.albedo_color = Color("#f4f8ff")
			m.emission_enabled = true; m.emission = Color("#eef4ff"); m.emission_energy_multiplier = 3.0
			m.set_meta("e_day", 3.0); m.set_meta("e_night", 3.0)
		"lamp":
			m.albedo_color = Color("#fff4dc")
			m.emission_enabled = true; m.emission = Color("#fff0d0"); m.emission_energy_multiplier = 3.5
			m.set_meta("e_day", 3.5); m.set_meta("e_night", 3.5)
		"deck":
			m.albedo_texture = b.tex("pc/redeem_fur.png"); m.albedo_color = Color("#6a7288"); m.roughness = 0.95
			m.uv1_scale = Vector3(6, 6, 1)
			m.emission_enabled = true; m.emission = Color("#3a4058"); m.emission_energy_multiplier = 0.5
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 0.5)
		"small", "cards":
			# prizes inside the lit showcase: a little self-light stands in for the case's tube
			var t = b.tex("pc/redeem_%s.png" % key)
			m.albedo_texture = t; m.roughness = 0.5
			if key == "cards":
				m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR; m.alpha_scissor_threshold = 0.5
				m.cull_mode = BaseMaterial3D.CULL_DISABLED
			_emit(m, t, 0.4)
		"tags":
			var t = b.tex("pc/redeem_cards.png")
			m.albedo_texture = t; m.roughness = 0.6
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR; m.alpha_scissor_threshold = 0.5
			_emit(m, t, 0.12)
		"desk":
			m.albedo_texture = b.tex("pc/redeem_desk.png"); m.roughness = 0.55
		"led":
			var t = b.tex("pc/redeem_desk.png")
			m.albedo_texture = t; m.roughness = 0.2
			_emit(m, t, 1.8)
		"toys":
			m.albedo_texture = b.tex("pc/redeem_toys.png"); m.roughness = 0.45
		"plush":
			m.albedo_texture = b.tex("pc/redeem_fur.png"); m.vertex_color_use_as_albedo = true
			m.vertex_color_is_srgb = true; m.roughness = 1.0
			m.uv1_scale = Vector3(2, 2, 1)
		"vinyl":
			m.vertex_color_use_as_albedo = true; m.vertex_color_is_srgb = true; m.roughness = 0.22
		"bead":
			m.vertex_color_use_as_albedo = true; m.vertex_color_is_srgb = true; m.roughness = 0.08; m.metallic_specular = 0.8
		"shelf":
			m.albedo_texture = b.tex("pc/redeem_scuff.png"); m.albedo_color = Color("#9c9ea4"); m.roughness = 0.5
		"slat":
			m.albedo_texture = b.tex("pc/redeem_slat.png"); m.roughness = 0.55
		"header":
			var t = b.tex("pc/redeem_header.png")
			m.albedo_texture = t; m.roughness = 0.35
			_emit(m, t, 1.3)
		"band":
			var t = b.tex("pc/redeem_band.png")
			m.albedo_texture = t; m.roughness = 0.35
			_emit(m, t, 1.1)
		_:
			return false
	return true

static func _emit(m, t, e):
	m.emission_enabled = true
	m.emission = Color.BLACK          # EMISSION_OP_ADD: emission = colour + texture
	m.emission_texture = t
	m.emission_energy_multiplier = e
	m.set_meta("e_day", e)
	m.set_meta("e_night", e)
