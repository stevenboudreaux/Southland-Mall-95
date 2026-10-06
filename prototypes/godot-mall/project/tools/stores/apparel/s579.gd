## 5-7-9 (store n33b) on the Concourse, JW's neighbour, built to design/storefronts/579.md.
## After the 1995 North East Mall video (sign 0:33, store 8:11-8:52): a tall all-glass
## front in white frames, the yellow "5·7·9" numerals on a polished steel triangle over
## the doors, a light wood plank floor, cream walls with outfits faced out high, juniors'
## round racks and tables, and window mannequins. Cash wrap and fitting rooms are guessed.
##
## Frame: kit.gd's. u runs from the edge's start (x = -74, JW's side, the viewer's left)
## to Foot Locker's side (u = 6); d runs into the store (-z).

const K = preload("res://tools/stores/apparel/kit.gd")
const W = 6.0
const D = 28.0
const SIDE = 0.12
const HEAD = 3.0         # the glass runs up to here (video: tall glass)
const HTOP = 3.7
const CEIL = 3.3
const DOOR0 = 2.0
const DOOR1 = 4.0
const UP = Vector3.UP

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 579
	front(b, "apf_props", a, t, n)
	K.shell(b, "ap_shell", a, t, n, W, D, SIDE, CEIL, 0.0, "ap_wood", 1.0, "ap_cream", [1.4, 4.0], 0.9, 1.4)
	inside(b, a, t, n, rng)
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
	# a white header over the glass, white bulkhead above
	b.box(g, "ap_white", P(a, t, n, W * 0.5, (HEAD + HTOP) * 0.5, -0.04), b.abs_size(t, W, HTOP - HEAD, 0.08, n))
	b.quad("ap_shell", "ap_white", [P(a, t, n, 0, HTOP, 0), P(a, t, n, W, HTOP, 0), P(a, t, n, W, LH, 0), P(a, t, n, 0, LH, 0)], n)
	# the steel triangle, point down, hung over the doors, and the numerals across it
	var rv = (-n).cross(UP)
	var tc = P(a, t, n, W * 0.5, 0, 0) + n * 0.1
	var tw = 2.1
	var ttop = HTOP - 0.02
	var tbot = HEAD - 0.42
	var s = b.st("apf_props", "ap_steel", true)
	var p0 = tc - rv * (tw * 0.5) + UP * ttop
	var p1 = tc + rv * (tw * 0.5) + UP * ttop
	var p2 = tc + UP * tbot
	b.tri(s, p0, p1, p2, Vector2(0, 0), Vector2(1, 0), Vector2(0.5, 1), n)
	for e in [[p0, p2], [p2, p1], [p1, p0]]:
		var en = ((e[1] - e[0]).cross(-n)).normalized()
		b.quad("apf_props", "ap_steel", [e[0], e[1], e[1] - n * 0.06, e[0] - n * 0.06], en, [], true)
	K.letters(b, "apf_props", "res://tools/stores/apparel/s579_letters.json", tc + UP * (HEAD + 0.08), n, "ap_yellow", "ap_steel", 0.03, 0.07)
	# all-glass front in white frames; glass doors standing open in the middle
	for u in [0.0, 1.0, DOOR0 - 0.06, DOOR1, 5.0 - 0.06, W - 0.06]:
		b.box(g, "ap_white", P(a, t, n, u + 0.03, HEAD * 0.5, 0.04), b.abs_size(t, 0.06, HEAD, 0.08, n))
	for w in [[0.06, DOOR0 - 0.06], [DOOR1 + 0.06, W - 0.06]]:
		b.box(g, "ap_white", P(a, t, n, (w[0] + w[1]) * 0.5, 0.15, 0.04), b.abs_size(t, w[1] - w[0], 0.3, 0.08, n), Transform3D.IDENTITY, ["-y"])
		b.quad("glass", "glass", [P(a, t, n, w[0], 0.3, 0.02), P(a, t, n, w[1], 0.3, 0.02), P(a, t, n, w[1], HEAD, 0.02), P(a, t, n, w[0], HEAD, 0.02)], n,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# window displays: torso forms on stands, a low riser
	for u in [0.6, 1.4, 4.6, 5.4]:
		b.box(g, "ap_white", P(a, t, n, u, 0.15, 0.6), b.abs_size(t, 0.78, 0.3, 0.8, n), Transform3D.IDENTITY, ["-y"])
	K.mannequin(b, P(a, t, n, 0.8, 0.3, 0.6), -n, "#1c1c20", "#24242a", 0.95)
	K.mannequin(b, P(a, t, n, 5.2, 0.3, 0.6), -n, "#c8c8cc", "#1c1c20", 0.95)
	K.ob(b, P(a, t, n, 0, 0, -0.1), P(a, t, n, DOOR0, 0, 1.05), 0.1)
	K.ob(b, P(a, t, n, DOOR1, 0, -0.1), P(a, t, n, W, 0, 1.05), 0.1)

static func inside(b, a, t, n, rng):
	var uL = SIDE
	var uR = W - SIDE
	# both walls: outfits faced out on white slatwall, high and low (video 8:17)
	K.faceout_wall(b, a, t, n, uL, t, 1.5, 21.0, 1, rng, "gb_slat_white", 3.05)
	K.faceout_wall(b, a, t, n, uR, -t, 1.5, 12.5, 1, rng, "gb_slat_white", 3.05)
	K.cash_wrap(b, P(a, t, n, uR - 1.25, 0, 13.0), -n, -t, 2.4, 0.6, "ap_white")
	K.faceout_wall(b, a, t, n, uR, -t, 16.0, 21.0, 1, rng, "gb_slat_white", 3.05)
	K.fitting_rooms(b, a, t, n, 2.0, uR, D - SIDE, 2.2, 3)
	b.quad("ap_fix", "ap_mirror", [P(a, t, n, 2.0 - 0.03, 0.3, D - 0.5), P(a, t, n, 2.0 - 0.03, 0.3, D - 2.7), P(a, t, n, 2.0 - 0.03, 2.0, D - 2.7), P(a, t, n, 2.0 - 0.03, 2.0, D - 0.5)], -t)
	# the floor: round racks of juniors' wear, tables, a four-way
	K.round_rack(b, P(a, t, n, 3.0, 0, 3.4), 0.6, 2)
	K.table(b, P(a, t, n, 3.0, 0, 6.2), 0.0, 1.4, 0.85, 0, "ap_white")
	K.round_rack(b, P(a, t, n, 3.0, 0, 9.2), 0.6, 2)
	K.fourway(b, P(a, t, n, 3.0, 0, 12.4), 0.0, 2)
	K.round_rack(b, P(a, t, n, 2.7, 0, 15.6), 0.6, 3)
	K.table(b, P(a, t, n, 3.0, 0, 18.6), 0.0, 1.4, 0.85, 1, "ap_white")
	K.fourway(b, P(a, t, n, 3.0, 0, 21.8), 0.6, 2)
	K.hang_sign(b, P(a, t, n, 3.0, 2.25, 4.8), -n, 2, 0.4, 0.8, CEIL)
	K.hang_sign(b, P(a, t, n, 3.0, 2.25, 14.0), -n, 2, 0.4, 0.8, CEIL)
