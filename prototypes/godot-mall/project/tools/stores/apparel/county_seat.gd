## County Seat (store n46) on the Concourse, built to design/storefronts/county-seat.md.
## After the 1995 North East Mall video (sign 0:35, store 10:50-11:10): white raised
## "COUNTY·SEAT" capitals on a charcoal fascia over a wide-open front with a dark soffit
## and a row of downlights; inside, white tile with grey squares, rows of fluorescents
## running deep, black slatwall with denim faced out over white cubbies of folded jeans,
## denim posters, chrome four-ways and round racks, purple "25% off" cards. Cash wrap and
## fitting rooms are guessed.
##
## Frame: kit.gd's. The front faces -z onto the Concourse; u runs from the edge's start
## (x = -94, the viewer's right) to x = -86 (u = 8); d runs into the store (+z).

const K = preload("res://tools/stores/apparel/kit.gd")
const W = 8.0
const D = 40.0
const SIDE = 0.12
const HEAD = 2.9
const FTOP = 3.75
const CEIL = 3.2
const PIERW = 0.35
const UP = Vector3.UP

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 46
	front(b, "apf_props", a, t, n)
	K.shell(b, "ap_shell", a, t, n, W, D, SIDE, CEIL, 1.4, "ap_tile_cs", 2.44, "ap_white", [1.5, 4.0, 6.4], 7.0, 1.3)
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
	# charcoal fascia across the unit and charcoal piers at the ends; open between
	b.box(g, "ap_charcoal", P(a, t, n, W * 0.5, (HEAD + FTOP) * 0.5, -0.08), b.abs_size(t, W, FTOP - HEAD, 0.16, n), Transform3D.IDENTITY, [])
	b.quad("ap_shell", "ap_charcoal", [P(a, t, n, 0, FTOP, 0), P(a, t, n, W, FTOP, 0), P(a, t, n, W, LH, 0), P(a, t, n, 0, LH, 0)], n)
	for u in [0.0, W - PIERW]:
		b.box(g, "ap_charcoal", P(a, t, n, u + PIERW * 0.5, HEAD * 0.5, 0.1), b.abs_size(t, PIERW, HEAD, 0.36, n), Transform3D.IDENTITY, ["-y"])
	# the raised letters (video 0:35): white faces, dark returns
	K.letters(b, "apf_props", "res://tools/stores/apparel/cs_letters.json", P(a, t, n, W * 0.5, HEAD + 0.22, 0.0) + n * 0.16, n, "ap_letterwhite", "ap_letterdark", 0.02, 0.14)
	# the dark soffit inside the opening with its row of downlights (video 10:54)
	b.quad(g, "ap_black", [P(a, t, n, 0, HEAD, 0), P(a, t, n, W, HEAD, 0), P(a, t, n, W, HEAD, 1.4), P(a, t, n, 0, HEAD, 1.4)], Vector3.DOWN)
	b.quad("ap_shell", "ap_white", [P(a, t, n, 0, HEAD, 1.4), P(a, t, n, W, HEAD, 1.4), P(a, t, n, W, CEIL, 1.4), P(a, t, n, 0, CEIL, 1.4)], -n)
	for k in 6:
		b.box(g, "gb_can", P(a, t, n, 0.9 + k * 1.24, HEAD - 0.005, 0.7), b.abs_size(t, 0.2, 0.01, 0.2, n), Transform3D.IDENTITY, ["+y"])
	K.ob(b, P(a, t, n, 0, 0, -0.1), P(a, t, n, PIERW, 0, 0.3), 0.08)
	K.ob(b, P(a, t, n, W - PIERW, 0, -0.1), P(a, t, n, W, 0, 0.3), 0.08)

static func inside(b, a, t, n, rng):
	var uA = SIDE
	var uB = W - SIDE
	# side walls: denim faced out on black slatwall over white cubbies of folded jeans
	for side in [[uA, t], [uB, -t]]:
		K.faceout_wall(b, a, t, n, side[0], side[1], 1.6, 13.0, 1, rng)
		K.cubbies(b, a, t, n, side[0], side[1], 13.2, 21.0, 1.75)
		K.faceout_wall(b, a, t, n, side[0], side[1], 21.2, 34.0, 1 if side[0] == uA else 0, rng)
	# posters over the cubbies (video 11:07)
	for side in [[uA + 0.02, t, 15.0], [uB - 0.02, -t, 17.2]]:
		var o = P(a, t, n, side[0], 0, side[2])
		K.fq(b, "ap_fix", "ap_posters", o, -n, side[1], 0.0, 1.3, 1.9, 3.1, 0.0, 0.0, 0.0, 0.5, 1.0)
		K.fq(b, "ap_fix", "ap_posters", o - n * 1.5, -n, side[1], 0.0, 1.3, 1.9, 3.1, 0.0, 0.5, 0.0, 1.0, 1.0)
	# the cash wrap in the middle of the store, facing the door
	K.cash_wrap(b, P(a, t, n, 2.6, 0, 18.6), t, -n, 2.8, 0.65)
	b.box("ap_fix", "ap_black", P(a, t, n, 4.0, 1.4, 19.9), b.abs_size(t, 2.8, 0.04, 0.4, n), Transform3D.IDENTITY, [])
	# fitting rooms across the back, the stockroom door in the corner
	K.fitting_rooms(b, a, t, n, uA, 6.2, D - SIDE, 2.2, 4)
	b.quad("ap_fix", "ap_mirror", [P(a, t, n, 6.2 + 0.03, 0.3, D - 2.8), P(a, t, n, 6.2 + 0.03, 0.3, D - 0.5), P(a, t, n, 6.2 + 0.03, 2.0, D - 0.5), P(a, t, n, 6.2 + 0.03, 2.0, D - 2.8)], t)
	# the floor (video 10:54): four-ways and round racks in two lines, tables of folded denim
	K.table(b, P(a, t, n, 4.0, 0, 3.2), 0.0, 1.8, 1.0, 0)
	for row in [[2.3, 6.2, "4"], [5.7, 6.2, "r"], [2.3, 9.6, "r"], [5.7, 9.6, "4"], [2.3, 13.0, "4"], [5.7, 13.0, "r"],
			[2.3, 23.4, "r"], [5.7, 23.4, "4"], [4.0, 26.6, "t"], [2.3, 30.0, "4"], [5.7, 30.0, "r"], [4.0, 33.6, "r"]]:
		var c = P(a, t, n, row[0], 0, row[1])
		if row[2] == "4":
			K.fourway(b, c, 0.3, 3)
		elif row[2] == "r":
			K.round_rack(b, c, 0.6, 3 if rng.randf() < 0.6 else 0)
		else:
			K.table(b, c, 0.0, 1.8, 1.0, 1)
	K.table(b, P(a, t, n, 4.0, 0, 16.2), 0.0, 1.6, 0.9, 0)
	# the purple "special price" cards (video 11:12) hanging over the racks
	for d in [6.2, 13.0, 23.4, 30.0]:
		K.hang_sign(b, P(a, t, n, 4.0, 2.25, d), n, 1, 0.4, 0.8, CEIL)
