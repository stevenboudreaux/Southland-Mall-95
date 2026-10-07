## 5-7-9 (store n33b) on the Concourse, JW's neighbour, built to design/storefronts/579.md.
## After the 1995 North East Mall video (sign 0:33, store 8:11-8:52): a tall all-glass
## front in white frames, the yellow "5·7·9" numerals on a polished steel triangle over
## the doors, a light wood plank floor, cream walls with outfits faced out high, juniors'
## round racks and tables, and window mannequins. Cash wrap and fitting rooms are guessed.
##
## Frame: kit.gd's. u runs from the edge's start (x = -74, JW's side, the viewer's left)
## to Foot Locker's side (u = 6); d runs into the store (-z).

const CH = preload("res://tools/stores/signs/channel.gd")
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
	K.shell(b, "ap_shell", a, t, n, W, D, SIDE, CEIL, 0.0, "ap_wood", 1.0, "sg_s579_pinkwall", [1.4, 4.0], 0.9, 1.4)
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
	# Steven, Oct 7 (design/storefronts/photos/579/01, 04: "the pink 5-7-9 facade"): a polished
	# stainless portal, two broad steel piers either side of a wide open front; a white header with
	# the oval logo; hot-pink walls just inside, mannequins on pink risers either side of the way in
	b.box(g, "ap_white", P(a, t, n, W * 0.5, (HEAD + HTOP) * 0.5, -0.04), b.abs_size(t, W, HTOP - HEAD, 0.08, n))
	b.quad("ap_shell", "ap_white", [P(a, t, n, 0, HTOP, 0), P(a, t, n, W, HTOP, 0), P(a, t, n, W, LH, 0), P(a, t, n, 0, LH, 0)], n)
	# the burgundy oval ring on a silver plate, "5.7.9" raised in burgundy, centred on the header
	var tc = P(a, t, n, W * 0.5, 0, -0.08)
	var oc = tc + UP * 3.52
	CH.build(b, "apf_sign", "res://tools/stores/signs/s579_plate_logo.json", oc, n, "sg_s579_silver", "sg_s579_silver", "", 0.0, 0.04, 0.0)
	CH.build(b, "apf_sign", "res://tools/stores/signs/s579_ring_logo.json", oc, n, "sg_s579_red", "sg_s579_red_dark", "", 0.0, 0.09, 0.0, "", true)
	CH.build(b, "apf_sign", "res://tools/stores/signs/s579_digits_logo.json", oc, n, "sg_s579_red", "sg_s579_red_dark", "", 0.04, 0.09, 0.0)
	# the steel portal: broad piers, a steel lintel under the header, steel reveals into the store
	var pw = 0.55
	for s in [[0.0, pw], [W - pw, W]]:
		b.box(g, "sg_s579_steel", P(a, t, n, (s[0] + s[1]) * 0.5, HEAD * 0.5, 0.0), b.abs_size(t, s[1] - s[0], HEAD, 0.24, n), Transform3D.IDENTITY, ["-y"])
		var inner = s[1] if s[0] < 0.1 else s[0]
		var into = 1.0 if s[0] < 0.1 else -1.0
		b.quad(g, "sg_s579_steel", [P(a, t, n, inner, 0, 0.12), P(a, t, n, inner, 0, 0.9), P(a, t, n, inner, HEAD, 0.9), P(a, t, n, inner, HEAD, 0.12)], t * into)
		K.ob(b, P(a, t, n, s[0], 0, -0.15), P(a, t, n, s[1], 0, 0.9), 0.05)
	b.box(g, "sg_s579_steel", P(a, t, n, W * 0.5, HEAD - 0.06, 0.02), b.abs_size(t, W, 0.12, 0.28, n))
	# window displays just inside: pink risers with mannequins, either side of the way in
	for u in [1.15, W - 1.15]:
		b.box(g, "sg_s579_pink", P(a, t, n, u, 0.2, 1.2), b.abs_size(t, 1.1, 0.4, 0.9, n), Transform3D.IDENTITY, ["-y"])
		K.ob(b, P(a, t, n, u - 0.6, 0, 0.7), P(a, t, n, u + 0.6, 0, 1.7), 0.05)
	K.mannequin(b, P(a, t, n, 0.95, 0.4, 1.1), -n, "#1c1c20", "#24242a", 0.95)
	K.mannequin(b, P(a, t, n, 1.4, 0.4, 1.35), -n, "#e8689a", "#2a3a5a", 0.95)
	K.mannequin(b, P(a, t, n, W - 1.4, 0.4, 1.35), -n, "#c8c8cc", "#1c1c20", 0.95)
	K.mannequin(b, P(a, t, n, W - 0.95, 0.4, 1.1), -n, "#7a2a48", "#2a3a5a", 0.95)

static func inside(b, a, t, n, rng):
	var uL = SIDE
	var uR = W - SIDE
	# both walls: outfits faced out on white slatwall, high and low (video 8:17)
	K.faceout_wall(b, a, t, n, uL, t, 2.0, 21.0, 1, rng, "sg_s579_slat", 3.05)
	K.faceout_wall(b, a, t, n, uR, -t, 2.0, 12.5, 1, rng, "sg_s579_slat", 3.05)
	K.cash_wrap(b, P(a, t, n, uR - 1.25, 0, 13.0), -n, -t, 2.4, 0.6, "ap_white")
	K.faceout_wall(b, a, t, n, uR, -t, 16.0, 21.0, 1, rng, "sg_s579_slat", 3.05)
	K.fitting_rooms(b, a, t, n, 2.0, uR, D - SIDE, 2.2, 3)
	b.quad("ap_fix", "ap_mirror", [P(a, t, n, 2.0 - 0.03, 0.3, D - 0.5), P(a, t, n, 2.0 - 0.03, 0.3, D - 2.7), P(a, t, n, 2.0 - 0.03, 2.0, D - 2.7), P(a, t, n, 2.0 - 0.03, 2.0, D - 0.5)], -t)
	# the floor: round racks of juniors' wear, tables, a four-way
	K.table(b, P(a, t, n, 3.0, 0, 6.2), 0.0, 1.4, 0.85, 0, "ap_white")
	K.round_rack(b, P(a, t, n, 3.0, 0, 9.2), 0.6, 2)
	K.fourway(b, P(a, t, n, 3.0, 0, 12.4), 0.0, 2)
	K.round_rack(b, P(a, t, n, 2.7, 0, 15.6), 0.6, 3)
	K.table(b, P(a, t, n, 3.0, 0, 18.6), 0.0, 1.4, 0.85, 1, "ap_white")
	K.fourway(b, P(a, t, n, 3.0, 0, 21.8), 0.6, 2)
	K.hang_sign(b, P(a, t, n, 3.0, 2.25, 4.8), -n, 2, 0.4, 0.8, CEIL)
	K.hang_sign(b, P(a, t, n, 3.0, 2.25, 14.0), -n, 2, 0.4, 0.8, CEIL)
