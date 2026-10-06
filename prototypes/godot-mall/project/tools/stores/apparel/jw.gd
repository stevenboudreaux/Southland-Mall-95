## JW / Jeans West (store n33) on the Concourse, built to design/storefronts/jw.md.
## The sign and the stock follow the 1995 North East Mall video: the double white neon
## "JW" with a neon bar over it, white tile, black slatwall with men's and women's casual
## wear faced out, chrome round racks and four-ways, tables of folded jeans and khakis,
## blue "2 for $20" banners and mannequins in suits and khakis. The layout is guessed:
## cash wrap on the right, fitting rooms across the back.
##
## Frame: kit.gd's. u runs from the edge's start (x = -80, the viewer's left) to 5-7-9's
## side (u = 6); d runs into the store (-z).

const K = preload("res://tools/stores/apparel/kit.gd")
const W = 6.0
const D = 28.0
const SIDE = 0.12
const HEAD = 2.75
const HTOP = 3.8
const CEIL = 3.2
const DOOR0 = 1.55
const DOOR1 = 4.45
const UP = Vector3.UP

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 33
	front(b, "apf_props", a, t, n)
	K.shell(b, "ap_shell", a, t, n, W, D, SIDE, CEIL, 0.0, "gb_floor", 0.61, "ap_cream", [1.2, 4.2], 5.1)
	inside(b, a, t, n, rng)
	probe(b, a, t, n)

static func probe(b, a, t, n):
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, W * 0.5, CEIL * 0.5, D * 0.5)
	rp.size = (t * W + n * D).abs() + Vector3(0.1, CEIL + 0.1, 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

static func front(b, g, a, t, n):
	var LH = b.LANE_H
	# charcoal header band over the glass, charcoal bulkhead above it
	b.box(g, "ap_charcoal", P(a, t, n, W * 0.5, (HEAD + HTOP) * 0.5, -0.06), b.abs_size(t, W, HTOP - HEAD, 0.12, n), Transform3D.IDENTITY, [])
	b.quad("ap_shell", "ap_charcoal", [P(a, t, n, 0, HTOP, 0), P(a, t, n, W, HTOP, 0), P(a, t, n, W, LH, 0), P(a, t, n, 0, LH, 0)], n)
	# the neon "JW" and its bar (video 0:25)
	var c = P(a, t, n, W * 0.5, HEAD + 0.08, 0.0) + n * 0.12
	K.neon(b, "apf_neon", "res://tools/stores/apparel/jw_letters.json", c, n, "ap_neon")
	var rv = (-n).cross(UP)
	b.box("apf_neon", "ap_neon", c + UP * 0.86 + n * 0.06, (rv.abs() * 1.9 + UP * 0.02 + n.abs() * 0.02), Transform3D.IDENTITY, [], true)
	# glass front: dark frames, a bulkhead under each window, the open doorway
	for u in [0.0, DOOR0 - 0.1, DOOR1, W - 0.1]:
		b.box(g, "ap_black", P(a, t, n, u + 0.05, HEAD * 0.5, 0.05), b.abs_size(t, 0.1, HEAD, 0.1, n))
	for w in [[0.1, DOOR0 - 0.1], [DOOR1 + 0.1, W - 0.1]]:
		b.box(g, "ap_black", P(a, t, n, (w[0] + w[1]) * 0.5, 0.2, 0.05), b.abs_size(t, w[1] - w[0], 0.4, 0.1, n), Transform3D.IDENTITY, ["-y"])
		b.quad("glass", "glass", [P(a, t, n, w[0], 0.4, 0.02), P(a, t, n, w[1], 0.4, 0.02), P(a, t, n, w[1], HEAD, 0.02), P(a, t, n, w[0], HEAD, 0.02)], n,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# the soffit just inside, dark, with cans
	b.quad(g, "ap_black", [P(a, t, n, 0, HEAD, 0), P(a, t, n, W, HEAD, 0), P(a, t, n, W, HEAD, 1.0), P(a, t, n, 0, HEAD, 1.0)], Vector3.DOWN)
	b.quad("ap_shell", "ap_cream", [P(a, t, n, 0, HEAD, 1.0), P(a, t, n, W, HEAD, 1.0), P(a, t, n, W, CEIL, 1.0), P(a, t, n, 0, CEIL, 1.0)], -n)
	for u in [1.0, 3.0, 5.0]:
		b.box(g, "gb_can", P(a, t, n, u, HEAD - 0.005, 0.5), b.abs_size(t, 0.2, 0.01, 0.2, n), Transform3D.IDENTITY, ["+y"])
	# mannequins in the windows (video 3:45: a suit and khakis)
	K.mannequin(b, P(a, t, n, 0.75, 0.4, 0.55), -n, "#3a3a3e", "#4a4a4c")
	K.mannequin(b, P(a, t, n, 5.25, 0.4, 0.55), -n, "#c8b48c", "#c8b48c")
	b.box(g, "ap_white", P(a, t, n, (DOOR0 - 0.1) * 0.5, 0.2, 0.55), b.abs_size(t, DOOR0 - 0.2, 0.4, 0.8, n), Transform3D.IDENTITY, ["-y"])
	b.box(g, "ap_white", P(a, t, n, (DOOR1 + W) * 0.5, 0.2, 0.55), b.abs_size(t, W - DOOR1 - 0.2, 0.4, 0.8, n), Transform3D.IDENTITY, ["-y"])
	K.ob(b, P(a, t, n, 0, 0, -0.1), P(a, t, n, DOOR0, 0, 1.0), 0.1)
	K.ob(b, P(a, t, n, DOOR1, 0, -0.1), P(a, t, n, W, 0, 1.0), 0.1)

static func inside(b, a, t, n, rng):
	var uL = SIDE
	var uR = W - SIDE
	# walls: black slatwall faced out (video), folded jeans in cubbies further back
	K.faceout_wall(b, a, t, n, uL, t, 1.6, 14.0, 0, rng)
	K.cubbies(b, a, t, n, uL, t, 14.2, 22.0, 2.2)
	K.faceout_wall(b, a, t, n, uR, -t, 1.6, 9.8, 0, rng)
	# the cash wrap on the right, counter parallel to the wall, staff behind it
	var o = P(a, t, n, uR - 1.3, 0, 10.2)
	K.cash_wrap(b, o, -n, -t, 2.6, 0.6)
	K.faceout_wall(b, a, t, n, uR, -t, 13.4, 22.0, 0, rng)
	# fitting rooms across the back, a mirror and the stockroom door in the corridor beside them
	K.fitting_rooms(b, a, t, n, uL, 4.0, D - SIDE, 2.0, 3)
	b.quad("ap_fix", "ap_mirror", [P(a, t, n, 4.0 + 0.03, 0.3, D - 2.6), P(a, t, n, 4.0 + 0.03, 0.3, D - 0.5), P(a, t, n, 4.0 + 0.03, 2.0, D - 0.5), P(a, t, n, 4.0 + 0.03, 2.0, D - 2.6)], t)
	# the floor: a platform of mannequins, round racks, tables of folded jeans, four-ways
	var c = P(a, t, n, 3.0, 0, 2.2)
	b.box("ap_fix", "ap_white", c + UP * 0.1, b.abs_size(t, 1.6, 0.2, 0.9, n), Transform3D.IDENTITY, ["-y"])
	K.mannequin(b, c + UP * 0.2 - t * 0.4, -n, "#e8e2d2", "#2e3a5c")
	K.mannequin(b, c + UP * 0.2 + t * 0.4, -n, "#7a2a2a", "#c8b48c")
	K.round_rack(b, P(a, t, n, 3.0, 0, 5.2), 0.62, 0)
	K.table(b, P(a, t, n, 3.0, 0, 7.8), 0.0, 1.5, 0.9, 1)
	K.round_rack(b, P(a, t, n, 3.0, 0, 10.6), 0.62, 1)
	K.fourway(b, P(a, t, n, 2.6, 0, 13.6), 0.4, 0)
	K.table(b, P(a, t, n, 3.0, 0, 16.4), 0.0, 1.5, 0.9, 0)
	K.fourway(b, P(a, t, n, 3.0, 0, 19.4), 0.0, 1)
	K.round_rack(b, P(a, t, n, 3.0, 0, 22.4), 0.62, 0)
	# the blue "2 for $20" banners hanging over the racks (video 3:46)
	for d in [4.0, 9.4, 15.0, 20.8]:
		K.hang_sign(b, P(a, t, n, 3.0, 2.2, d), -n, 0, 0.42, 0.84, CEIL)
	K.hang_sign(b, P(a, t, n, 0.9, 2.15, 15.5), t, 3, 0.4, 0.8, CEIL)
