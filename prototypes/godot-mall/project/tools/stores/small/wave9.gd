## The Wave 9 shops, from the Southland facade records (Steven's photos, memory and
## descriptions) and the game's flat fronts: Solarium (n8) and Rave (n9) facing east onto the
## hall by Lane Bryant; Concepts (s61) and Country Fair (n42) facing south onto the Concourse;
## the Lion's Share restaurant (n36) facing north; American Bank (s29ab) facing the Sears
## hall. Specs: design/storefronts/solarium.md, rave.md, concepts.md, country-fair.md,
## lions-share.md, american-bank.md. Insides are period types on the kits; layouts guessed.
##
## Frame: P(a, t, n, u, y, d) = a + t u - n d + y up, u along the frontage, d into the store.

const CH = preload("res://tools/stores/signs/channel.gd")
const K = preload("res://tools/stores/media/kit.gd")
const AK = preload("res://tools/stores/apparel/kit.gd")
const M2 = preload("res://tools/stores/apparel/more.gd")
const S1 = preload("res://tools/stores/small/store.gd")
const W7 = preload("res://tools/stores/small/wave7.gd")
const W8 = preload("res://tools/stores/small/wave8.gd")
const UP = Vector3.UP
const SIDE = 0.12
const LET = "res://tools/stores/small/"

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 900 + int(Ln * 10)
	var W = Ln
	var D = 10.0
	match sd.name:
		"SOLARIUM":
			D = 8.0
			solarium(b, a, t, n, W, D, rng)
		"RAVE":
			D = 12.0
			rave(b, a, t, n, W, D, rng)
		"CONCEPTS":
			D = 14.0
			concepts(b, a, t, n, W, D, rng)
		"COUNTRY FAIR":
			country_fair(b, a, t, n, W, D, rng)
		"LION'S SHARE RESTAURANT":
			D = 12.0
			lions_share(b, a, t, n, W, D, rng)
		"AMERICAN BANK":
			D = 8.0
			bank(b, a, t, n, W, D, rng)
	W7.probe(b, a, t, n, W, D)

## A black carriage lantern on a wall bracket at c (the lamp's centre), glowing, with a small
## warm light; `f` points out of the wall.
static func coach_lamp(b, G, c, f, energy = 0.35):
	b.box(G, "md_black", c - f * 0.12 + UP * 0.18, b.abs_size(f.cross(UP), 0.04, 0.04, 0.24, f))
	b.box(G, "md_black", c + UP * 0.2, Vector3(0.2, 0.03, 0.2))
	b.cyl(G, "md_black", c + UP * 0.21, 0.1, 0.02, 0.1, 4, true, false)
	b.box(G, "w9_lamp_glass", c + UP * 0.07, Vector3(0.15, 0.24, 0.15))
	b.box(G, "md_black", c - UP * 0.06, Vector3(0.18, 0.03, 0.18))
	var l = b.add_omni(c + f * 0.25 + UP * 0.05, energy, 3.5, Color(1.0, 0.82, 0.55))
	b.tag(l, "", energy * 0.5, energy)

# ------------------------------------------------------------------ Solarium
## A pale stone fascia carrying only the name, in soft aqua-green lower-case neon bent as one
## tight line; a glass front onto a calm tanning-salon lobby: sea-glass walls, a white front
## desk with an aqua stripe, a palm, a shelf of lotions, a lit beach print (record, from
## Steven's memory). The tanning rooms are behind two doors at the back.
static func solarium(b, a, t, n, W, D, rng):
	var F = "w9sf_props"
	var G = "w9s_fix"
	var head = 2.8
	S1.upper(b, F, a, t, n, W, head, "w9_stone", 0.16)
	AK.neon(b, F, LET + "sol_letters.json", P(a, t, n, W * 0.5, head + 0.62, -0.16), n, "w9_neon_aqua", 0.02, 0.016, 0.03)
	W8.pier(b, F, "w9_stone", a, t, n, 0.0, 0.2, head, 0.16)
	W8.pier(b, F, "w9_stone", a, t, n, W - 0.2, W, head, 0.16)
	W8.glass_front(b, F, a, t, n, 0.2, W - 0.2, head, W * 0.5, 1.2, "w8_white", 0.25)
	M2.shell2(b, "w9s_shell", a, t, n, W, D, 2.9, 0.0, "w9_floor_sand", 0.61, "w9_seaglass", "kb_ceiling", [W * 0.5 - 0.3], W * 0.5, 1.1)
	M2.soffit(b, F, a, t, n, W, head, "w9_stone")
	# the front desk with its aqua stripe, across from the door
	var co = P(a, t, n, W - 0.8, 0, 3.6)
	K.lbox(b, G, "w8_white", co, -t, n, 0.0, 0.0, 0.0, 2.4, 1.0, 0.6, ["-y"])
	K.lbox(b, G, "w9_aqua", co, -t, n, -0.01, 0.55, 0.58, 2.42, 0.1, 0.04)
	K.lbox(b, G, "w8_white", co, -t, n, -0.03, 1.0, -0.03, 2.46, 0.04, 0.66)
	K.register(b, "w9s_small", K.L(co, -t, n, 0.6, 1.04, 0.1), -t, n)
	K.ob_local(b, co, -t, n, 0.0, 0.0, 2.4, 0.6)
	# a potted palm by the window, a white bench, the lotions on the near wall, the beach print
	palm(b, G, P(a, t, n, 0.8, 0, 1.4))
	K.lbox(b, G, "w8_white", P(a, t, n, SIDE + 0.05, 0, 2.4), -n, t, 0.0, 0.0, 0.0, 1.6, 0.45, 0.45)
	K.ob(b, P(a, t, n, SIDE, 0, 2.4), P(a, t, n, SIDE + 0.5, 0, 4.0), 0.05)
	K.bay(b, G, G, P(a, t, n, SIDE, 0, 5.6), n, t, 1.22, [0.9, 1.25, 1.6], ["hba"], rng, 0.25)
	K.ob(b, P(a, t, n, SIDE, 0, 4.4), P(a, t, n, SIDE + 0.3, 0, 5.6), 0.05)
	K.fq(b, G, "w9_beach", P(a, t, n, W - SIDE, 0, 1.2), -n, -t, 0.0, 1.2, 1.3, 2.2, 0.02)
	# two tanning rooms across the back
	AK.fitting_rooms(b, a, t, n, SIDE, W - SIDE, D - SIDE, 2.2, 2, "w8_white")

## A potted palm at c: a pot, a trunk, a crown of fronds.
static func palm(b, G, c):
	b.cyl(G, "w8_white", c, 0.22, 0.26, 0.45, 12, true, false)
	b.cyl(G, "w9_trunk", c + UP * 0.45, 0.05, 0.035, 1.25, 8, false, false)
	var top = c + UP * 1.7
	var s = b.st(G, "w9_leaf")
	for k in 7:
		var ang = TAU * k / 7.0
		var dv = Vector3(cos(ang), 0, sin(ang))
		var side = dv.cross(UP) * 0.16
		var tip = top + dv * 0.75 - UP * 0.35
		var mid = top + dv * 0.4 + UP * 0.05
		b.tri(s, top - side * 0.3, mid + side, mid - side, Vector2(0, 0.5), Vector2(0.5, 0), Vector2(0.5, 1), UP)
		b.tri(s, mid + side, tip, mid - side, Vector2(0.5, 0), Vector2(1, 0.5), Vector2(0.5, 1), UP)
	K.ob(b, c - Vector3(0.3, 0, 0.3), c + Vector3(0.3, 0, 0.3), 0.05)

# ------------------------------------------------------------------ Rave
## Stacked, offset brushed-silver plates stepping out from the bulkhead, the white sign plate
## proud of them with heavy pink-red italics sliced by a speed line; under it a dim shop of
## posters and black clothes (record).
static func rave(b, a, t, n, W, D, rng):
	var F = "w9rf_props"
	var G = "w9r_fix"
	var head = 2.8
	S1.upper(b, F, a, t, n, W, head, "w9_dark_grey", 0.12)
	var o = P(a, t, n, 0, 0, 0)
	# Steven's sign pass (Oct 7: design/storefronts/photos/rave): a black box sign hung out over
	# the entrance, its dark glass face carrying RAVE in pink lit letters
	var bw = 3.4
	var bc = P(a, t, n, W * 0.5, head + 0.2, -0.75)
	var rv = (-n).cross(UP)
	b.box(F, "sg_rave_box", bc + UP * 0.65, b.abs_size(t, bw, 1.3, 1.2, n))
	b.box(F, "sg_rave_glass", bc + UP * 0.65 + n * 0.605, b.abs_size(t, bw - 0.16, 1.14, 0.01, n))
	b.box(F, "sg_rave_box", bc + UP * (1.3 + (b.LANE_H - head - 0.2 - 1.3) * 0.5), b.abs_size(t, 0.08, b.LANE_H - head - 1.5, 0.08, n))
	CH.build(b, "w9rf_sign", "res://tools/stores/signs/rave_name_logo.json", bc + UP * 0.33 + n * 0.61, n, "sg_rave_pink", "sg_rave_pink_dark", "", 0.0, 0.03, 0.0, "sg_rave_glow")
	W8.pier(b, F, "w9_dark_grey", a, t, n, 0.0, 0.2, head, 0.12)
	W8.pier(b, F, "w9_dark_grey", a, t, n, W - 0.2, W, head, 0.12)
	W8.glass_front(b, F, a, t, n, 0.2, W - 0.2, head, W * 0.5, 2.2, "md_black", 0.3)
	M2.shell2(b, "w9r_shell", a, t, n, W, D, 3.0, 0.0, "a2_carpet_grey", 1.0, "w9_dark_grey", "kb_ceiling", [2.0, 5.4], 6.6, 0.5)
	M2.soffit(b, F, a, t, n, W, head, "md_black")
	# forms in black and white in the windows
	AK.mannequin(b, P(a, t, n, 1.2, 0.0, 0.8), -n, "#18181a", "#18181a")
	AK.mannequin(b, P(a, t, n, W - 1.2, 0.0, 0.8), -n, "#ecebe6", "#18181a")
	# posters high on both walls, black clothes below, round racks down the middle
	for s in [[SIDE, t], [W - SIDE, -t]]:
		K.fq(b, G, "w9_posters", P(a, t, n, s[0], 0, 1.6), -n, s[1], 0.0, D - 3.6, 2.0, 2.9, 0.01, 0.0, 0.0, (D - 3.6) / 4.0, 1.0)
	for s in [[SIDE, t, 1.8, D - 2.4], [W - SIDE, -t, 1.8, D - 4.6]]:
		var wo = P(a, t, n, s[0], 0, s[2])
		var ln = s[3] - s[2]
		K.fq(b, G, "w9_black_clothes", wo, -n, s[1], 0.0, ln, 0.6, 1.95, 0.3, 0.0, 0.0, ln / 2.4, 1.0)
		K.ob(b, wo, wo - n * ln + s[1] * 0.5, 0.05)
	for k in 3:
		var rc = P(a, t, n, W * 0.5, 0, 3.4 + k * 2.6)
		b.cyl(G, "md_chrome", rc, 0.03, 0.03, 1.35, 8, false, false)
		b.cyl(G, "md_chrome", rc + UP * 1.32, 0.6, 0.6, 0.03, 20, false, false)
		b.cyl(G, "w9_black_rack", rc + UP * 0.45, 0.62, 0.62, 0.86, 20, false, false)
		b.cyl(G, "md_chrome", rc, 0.25, 0.25, 0.02, 12, true, false)
		K.ob(b, rc - Vector3(0.7, 0, 0.7), rc + Vector3(0.7, 0, 0.7), 0.05)
	AK.cash_wrap(b, P(a, t, n, W - 0.9, 0, D - 2.6), -t, n, 2.4, 0.6, "md_black")

# ------------------------------------------------------------------ Concepts
## School uniforms and backpacks for kids. Instead of windows, two deep white shadow boxes
## either side of the door, each holding huge plain geometric solids about the height of a
## three-year-old: a sphere, a cone, a cube, a cylinder (record; the colours follow the flat
## front and are a guess). Through the door, racks of navy and white uniforms, plaid jumpers,
## khakis and a wall of backpacks.
static func concepts(b, a, t, n, W, D, rng):
	var F = "w9cf_props"
	var G = "w9c_fix"
	var head = 2.8
	S1.upper(b, F, a, t, n, W, head, "w8_cream_front", 0.14)
	K.lbox(b, F, "w9_plum", P(a, t, n, 0, 0, 0), t, n, W * 0.5 - 1.85, head + 0.45, 0.14, 3.7, 0.78, 0.12)
	W8.sign_q(b, F, "w9_concepts_sign", a, t, n, W * 0.5, 3.6, head + 0.5, head + 1.18, -0.265)
	var dw = 2.6
	var boxes = [[0.25, W * 0.5 - dw * 0.5 - 0.2], [W * 0.5 + dw * 0.5 + 0.2, W - 0.25]]
	W8.pier(b, F, "w8_cream_front", a, t, n, 0.0, 0.25, head, 0.14)
	W8.pier(b, F, "w8_cream_front", a, t, n, W - 0.25, W, head, 0.14)
	for k in 2:
		var u0 = boxes[k][0]
		var u1 = boxes[k][1]
		W8.pier(b, F, "w9_plum", a, t, n, u1 if k == 0 else u0 - 0.2, (u1 + 0.2) if k == 0 else u0, head, 0.14)
		shadow_box(b, G, a, t, n, u0, u1, head, k)
	b.box(F, "w9_plum", P(a, t, n, W * 0.5, head - 0.05, -0.07), b.abs_size(t, dw + 0.4, 0.1, 0.14, n))
	M2.shell2(b, "w9c_shell", a, t, n, W, D, 3.0, 0.0, "md_vinyl", 0.61, "w8_cream", "kb_ceiling", [2.6, 7.0], 2.0, 1.3)
	b.quad(F, "w8_cream", [P(a, t, n, W * 0.5 - dw * 0.5, head, 0), P(a, t, n, W * 0.5 + dw * 0.5, head, 0), P(a, t, n, W * 0.5 + dw * 0.5, head, 1.4), P(a, t, n, W * 0.5 - dw * 0.5, head, 1.4)], Vector3.DOWN)
	# uniforms down both side walls, backpacks across the back
	for s in [[SIDE, t, 2.0, D - 3.0], [W - SIDE, -t, 2.0, D - 1.0]]:
		var wo = P(a, t, n, s[0], 0, s[2])
		var ln = s[3] - s[2]
		K.lbox(b, G, "gb_slat_white", wo, -n, s[1], 0.0, 0.0, 0.0, ln, 2.5, 0.03)
		K.fq(b, G, "w9_uniforms", wo, -n, s[1], 0.0, ln, 0.25, 2.45, 0.35, 0.0, 0.0, ln / 2.4, 1.0)
		K.ob(b, wo, wo - n * ln + s[1] * 0.5, 0.05)
	K.fq(b, G, "w9_backpacks", P(a, t, n, W - SIDE - 1.0, 0, D - SIDE), -t, n, 0.0, W - 2.4, 1.0, 2.2, 0.02, 0.0, 0.0, (W - 2.4) / 4.0, 1.0)
	# tables of folded polos and a four-way of uniforms down the middle; the cash wrap on the left
	AK.table(b, P(a, t, n, W * 0.5, 0, 3.4), 0.0, 1.5, 0.9, 0, "w8_walnut")
	AK.fourway(b, P(a, t, n, W * 0.5 - 1.2, 0, 6.4), 0.0, 1)
	AK.fourway(b, P(a, t, n, W * 0.5 + 1.2, 0, 6.4), 0.0, 0)
	AK.table(b, P(a, t, n, W * 0.5, 0, 9.2), 0.0, 1.5, 0.9, 1, "w8_walnut")
	AK.cash_wrap(b, P(a, t, n, 0.9, 0, D - 2.4), t, n, 2.4, 0.6, "w9_plum")

## A deep white shadow box from u0 to u1 behind glass: the solids standing in it, lit from
## above. k picks the pair (0: sphere and cone; 1: cube and cylinder).
static func shadow_box(b, G, a, t, n, u0, u1, head, k):
	var dB = 1.3
	var base = 0.35
	b.box(G, "w8_white", P(a, t, n, (u0 + u1) * 0.5, base * 0.5, dB * 0.5), b.abs_size(t, u1 - u0, base, dB, n), Transform3D.IDENTITY, ["-y"])
	b.quad(G, "w8_white", [P(a, t, n, u0, base, dB), P(a, t, n, u1, base, dB), P(a, t, n, u1, head, dB), P(a, t, n, u0, head, dB)], n)
	b.quad(G, "w8_white", [P(a, t, n, u0, base, 0), P(a, t, n, u0, base, dB), P(a, t, n, u0, head, dB), P(a, t, n, u0, head, 0)], t)
	b.quad(G, "w8_white", [P(a, t, n, u1, base, dB), P(a, t, n, u1, base, 0), P(a, t, n, u1, head, 0), P(a, t, n, u1, head, dB)], -t)
	b.quad(G, "w8_glow", [P(a, t, n, u0, head, 0.1), P(a, t, n, u1, head, 0.1), P(a, t, n, u1, head, dB), P(a, t, n, u0, head, dB)], Vector3.DOWN)
	W8.glass(b, a, t, n, u0, u1, base, head, -0.01)
	var c0 = P(a, t, n, u0 + (u1 - u0) * 0.3, base, 0.7)
	var c1 = P(a, t, n, u0 + (u1 - u0) * 0.72, base, 0.7)
	if k == 0:
		sphere(b, G, "w9_solid_red", c0 + UP * 0.48, 0.48)
		b.cyl(G, "w9_solid_yellow", c1, 0.4, 0.0, 1.0, 24, false, true)
	else:
		b.box(G, "w9_solid_blue", Vector3.ZERO, Vector3(0.9, 0.9, 0.9), Transform3D(Basis(UP, 0.3), c0 + UP * 0.45), ["-y"])
		b.cyl(G, "w9_solid_green", c1, 0.34, 0.34, 0.95, 24, true, false)
	K.ob(b, P(a, t, n, u0, 0, -0.05), P(a, t, n, u1, 0, dB), 0.05)

## A sphere of radius r at c, from stacked bands.
static func sphere(b, G, m, c, r):
	var bands = 10
	for i in bands:
		var a0 = -PI * 0.5 + PI * i / bands
		var a1 = -PI * 0.5 + PI * (i + 1) / bands
		b.cyl(G, m, c + UP * (sin(a0) * r), cos(a0) * r, cos(a1) * r, (sin(a1) - sin(a0)) * r, 24, false, false)

# ------------------------------------------------------------------ Country Fair
## A green fascia with the name in cream serif, a white picket fence across the front under the
## windows, a gingham valance over the door, and a shop full of country gifts: a quilt,
## baskets, candles, wooden hearts and dried flowers (record, from descriptions only).
static func country_fair(b, a, t, n, W, D, rng):
	var F = "w9ff_props"
	var G = "w9f_fix"
	var head = 2.7
	S1.upper(b, F, a, t, n, W, head, "w9_green", 0.14)
	AK.letters(b, F, LET + "cf_letters.json", P(a, t, n, W * 0.5, head + 0.62, -0.14), n, "w9_cream_letter", "w9_cream_letter", 0.02, 0.04)
	for s in [head + 0.25, head + 1.25]:
		b.box(F, "w9_cream_letter", P(a, t, n, W * 0.5, s, -0.15), b.abs_size(t, W - 0.6, 0.03, 0.03, n))
	var du = W * 0.5
	var dw = 1.6
	var wins = [[0.3, du - dw * 0.5 - 0.15], [du + dw * 0.5 + 0.15, W - 0.3]]
	W8.pier(b, F, "w9_green", a, t, n, 0.0, 0.3, head, 0.14)
	W8.pier(b, F, "w9_green", a, t, n, W - 0.3, W, head, 0.14)
	W8.pier(b, F, "w9_green", a, t, n, wins[0][1], du - dw * 0.5, head, 0.14)
	W8.pier(b, F, "w9_green", a, t, n, du + dw * 0.5, wins[1][0], head, 0.14)
	for wn in wins:
		var u0 = wn[0]
		var u1 = wn[1]
		b.box(F, "w8_white", P(a, t, n, (u0 + u1) * 0.5, 0.45, 0.0), b.abs_size(t, u1 - u0, 0.9, 0.12, n), Transform3D.IDENTITY, ["-y"])
		W8.glass(b, a, t, n, u0, u1, 0.9, head - 0.1, -0.01)
		W8.post(b, F, "w9_green", a, t, n, (u0 + u1) * 0.5, 0.05, 0.9, head - 0.1, 0.0, 0.08)
		b.box(F, "w9_green", P(a, t, n, (u0 + u1) * 0.5, head - 0.05, 0.0), b.abs_size(t, u1 - u0, 0.1, 0.12, n))
		picket(b, F, a, t, n, u0, u1, -0.12)
		K.ob(b, P(a, t, n, u0, 0, -0.25), P(a, t, n, u1, 0, 0.1), 0.05)
		# a display shelf of gifts in each window
		K.fq(b, G, "w9_country", P(a, t, n, u1, 0, 0.6), -t, n, 0.0, u1 - u0, 1.0, 2.0, 0.0, 0.0, 0.0, (u1 - u0) / 2.4, 1.0)
	# the gingham valance over the door
	W8.sign_q(b, F, "w9_gingham", a, t, n, du, dw + 0.2, head - 0.45, head - 0.12, -0.08, (dw + 0.2) / 0.3)
	M2.shell2(b, "w9f_shell", a, t, n, W, D, 3.0, 0.0, "ap_wood", 1.0, "w9_cream_wall", "kb_ceiling", [W * 0.5 - 0.3], W * 0.5, 1.2)
	M2.soffit(b, F, a, t, n, W, head, "w9_green")
	# country shelves on both walls, the quilt hung over them on one side
	for s in [[SIDE, t, 1.4, D - 1.6], [W - SIDE, -t, 1.4, D - 3.6]]:
		var wo = P(a, t, n, s[0], 0, s[2])
		var ln = s[3] - s[2]
		K.lbox(b, G, "w9_pine", wo, -n, s[1], 0.0, 0.0, 0.0, ln, 0.75, 0.4, ["-y"])
		K.fq(b, G, "w9_country", wo, -n, s[1], 0.0, ln, 0.8, 1.8, 0.02, 0.0, 0.0, ln / 2.4, 1.0)
		for y in [1.24, 1.82]:
			K.lbox(b, G, "w9_pine", wo, -n, s[1], 0.0, y, 0.0, ln, 0.03, 0.3)
		K.ob(b, wo, wo - n * ln + s[1] * 0.4, 0.05)
	K.fq(b, G, "w9_quilt", P(a, t, n, SIDE, 0, 3.0), -n, t, 0.0, 1.4, 1.95, 2.85, 0.02, 0.0, 0.0, 1.0, 0.65)
	# a pine table of baskets and candles in the middle, the counter at the back
	var tc = P(a, t, n, W * 0.5, 0, 4.4)
	K.lbox(b, G, "w9_pine", tc - t * 0.7 + n * 0.45, t, -n, 0.0, 0.0, 0.0, 1.4, 0.9, 0.9)
	K.ob(b, tc - t * 0.7 - n * 0.45, tc + t * 0.7 + n * 0.45, 0.1)
	b.cur_color = Color("#a8783e")
	for q in [Vector2(-0.4, -0.2), Vector2(0.35, 0.15)]:
		b.cyl(G, "vcolor", tc + t * q.x + n * q.y + UP * 0.92, 0.17, 0.2, 0.16, 12, false, true)
	b.cur_color = Color.WHITE
	K.stock_row(b, G, tc - t * 0.1 - n * 0.3 + UP * 0.0, t, -n, 0.0, 0.5, 0.92, 0.3, 0.0, "candles", rng)
	K.counter(b, G, "w9f_small", P(a, t, n, W - 0.4, 0, D - 2.0), -t, n, 2.6, "w9_pine", rng)

## A white picket fence from u0 to u1 at depth d (outside the glass).
static func picket(b, G, a, t, n, u0, u1, d):
	var u = u0 + 0.05
	while u < u1 - 0.02:
		b.box(G, "w8_white", P(a, t, n, u, 0.4, d), b.abs_size(t, 0.07, 0.8, 0.025, n), Transform3D.IDENTITY, ["-y"])
		var s = b.st(G, "w8_white")
		var p0 = P(a, t, n, u - 0.035, 0.8, d - 0.0125)
		var p1 = P(a, t, n, u + 0.035, 0.8, d - 0.0125)
		b.tri(s, p0, p1, P(a, t, n, u, 0.88, d - 0.0125), Vector2(0, 0), Vector2(1, 0), Vector2(0.5, 1), n)
		u += 0.12
	for y in [0.2, 0.6]:
		b.box(G, "w8_white", P(a, t, n, (u0 + u1) * 0.5, y, d + 0.025), b.abs_size(t, u1 - u0, 0.06, 0.025, n))

# ------------------------------------------------------------------ Lion's Share
## A dark brown brick front with no windows, a carved plaque with the name in gold, two coach
## lamps, and a single open doorway onto a dim passage that leads back to the dining room
## (record). The dining room is a guess: dark panelling, red carpet, white cloths, booths.
static func lions_share(b, a, t, n, W, D, rng):
	var F = "w9lf_props"
	var G = "w9l_fix"
	var du = W * 0.5 - 0.4
	var dw = 1.2
	var pd = 4.0
	S1.upper(b, F, a, t, n, W, 2.4, "w9_brick", 0.2)
	W8.pier(b, F, "w9_brick", a, t, n, 0.0, du - dw * 0.5, 2.4, 0.2)
	W8.pier(b, F, "w9_brick", a, t, n, du + dw * 0.5, W, 2.4, 0.2)
	b.box(F, "w8_dark_wood", P(a, t, n, du, 2.42, -0.1), b.abs_size(t, dw + 0.3, 0.12, 0.24, n))
	for s in [-1.0, 1.0]:
		b.box(F, "w8_dark_wood", P(a, t, n, du + s * (dw * 0.5 + 0.06), 1.2, -0.1), b.abs_size(t, 0.12, 2.4, 0.24, n), Transform3D.IDENTITY, ["-y"])
		coach_lamp(b, F, P(a, t, n, du + s * (dw * 0.5 + 0.55), 2.0, -0.38), n)
	W8.sign_q(b, F, "w9_plaque", a, t, n, W - 2.7, 1.3, 2.25, 3.88, -0.24)
	# the passage: brick walls, a low dark ceiling, red carpet
	var cg = "w9l_shell"
	for s in [-1.0, 1.0]:
		var u = du + s * (dw * 0.5 + 0.08)
		b.box(cg, "w9_brick", P(a, t, n, u, 1.2, pd * 0.5), b.abs_size(t, 0.16, 2.4, pd, n), Transform3D.IDENTITY, ["-y"])
		K.ob(b, P(a, t, n, u - 0.08, 0, 0), P(a, t, n, u + 0.08, 0, pd), 0.02)
	b.quad(cg, "w8_dark", [P(a, t, n, du - dw * 0.5, 2.4, 0), P(a, t, n, du + dw * 0.5, 2.4, 0), P(a, t, n, du + dw * 0.5, 2.4, pd), P(a, t, n, du - dw * 0.5, 2.4, pd)], Vector3.DOWN)
	var pl = b.add_omni(P(a, t, n, du, 2.2, pd * 0.5), 0.25, 3.0, Color(1.0, 0.8, 0.55))
	b.tag(pl, "", 0.2, 0.3)
	M2.shell2(b, cg, a, t, n, W, D, 2.8, 0.0, "s6_red_carpet", 1.0, "w9_panel", "w8_dark", [], W * 0.5, 0.8)
	# the closed rooms either side of the passage end in panelled walls facing the dining room
	for seg in [[SIDE, du - dw * 0.5 - 0.16], [du + dw * 0.5 + 0.16, W - SIDE]]:
		b.quad(cg, "w9_panel", [P(a, t, n, seg[0], 0, pd), P(a, t, n, seg[1], 0, pd), P(a, t, n, seg[1], 2.8, pd), P(a, t, n, seg[0], 2.8, pd)], n)
		b.quad(cg, "w8_dark", [P(a, t, n, seg[0], 2.4, 0.2), P(a, t, n, seg[1], 2.4, 0.2), P(a, t, n, seg[1], 2.4, pd), P(a, t, n, seg[0], 2.4, pd)], Vector3.DOWN)
		K.ob(b, P(a, t, n, seg[0], 0, 0), P(a, t, n, seg[1], 0, pd), 0.0)
	# the dining room: booths along the back wall, tables with white cloths, candles, sconces
	var WL = load("res://tools/stores/woolworth/store.gd")
	for k in 4:
		WL.booth(b, G, P(a, t, n, 1.6 + k * 2.9, 0, D - SIDE), t, n, rng)
	for c in [[2.4, 5.8], [5.4, 5.8], [8.6, 5.8], [3.9, 8.0], [7.2, 8.0], [10.2, 8.0]]:
		var tc = P(a, t, n, c[0], 0, c[1])
		b.cur_color = Color("#2a2a2c")
		b.cyl(G, "vcolor", tc, 0.22, 0.22, 0.03, 12, true, false)
		b.cyl(G, "vcolor", tc, 0.04, 0.04, 0.72, 8, false, false)
		b.cur_color = Color.WHITE
		b.box(G, "w9_cloth", tc + UP * 0.6, Vector3(0.9, 0.3, 0.9), Transform3D.IDENTITY, ["-y"])
		b.cyl(G, "w9_candle", tc + UP * 0.75, 0.03, 0.03, 0.09, 8, true, false)
		K.ob(b, tc - Vector3(0.45, 0, 0.45), tc + Vector3(0.45, 0, 0.45), 0.15)
		for s in [-1.0, 1.0]:
			W8.wood_chair(b, "w9l_small", tc + t * 0.66 * s, -t * s)
	for k in 3:
		for s in [[SIDE, t], [W - SIDE, -t]]:
			var wc = P(a, t, n, s[0], 1.8, 5.6 + k * 2.0)
			b.box("w9l_small", "w8_copper", wc + s[1] * 0.05, Vector3(0.08, 0.16, 0.08))
			b.cyl("w9l_small", "w8_bulb", wc + s[1] * 0.1 + UP * 0.08, 0.05, 0.07, 0.1, 10, true, false)
	for c in [[3.0, 6.9], [9.0, 6.9]]:
		var l = b.add_omni(P(a, t, n, c[0], 2.3, c[1]), 0.45, 6.0, Color(1.0, 0.78, 0.5))
		b.tag(l, "", 0.35, 0.5)

# ------------------------------------------------------------------ American Bank
## A white stucco front, the name in heavy rounded white letters on the shaded wall above, one
## wide arch closed by a wrought-iron gate, a black carriage lantern each side (record, from a
## grainy black-and-white photo of the Southland branch; the colours are a guess). Behind the
## gate a small lit lobby with the teller line; the gate is closed.
static func bank(b, a, t, n, W, D, rng):
	var F = "w9bf_props"
	var G = "w9b_fix"
	var u0 = 2.0
	var u1 = W - 2.0
	var spring = 2.5
	var rise = 0.8
	var top = b.LANE_H
	# the stucco wall with the arch cut out of it, front and back faces and the arch's reveal
	var arch_pts = []
	var seg = 16
	for i in seg + 1:
		var ang = PI * float(i) / seg
		arch_pts.append(Vector2((u0 + u1) * 0.5 + cos(ang) * (u1 - u0) * 0.5, spring + sin(ang) * rise))
	var outline = PackedVector2Array([Vector2(0, 0), Vector2(u0, 0)])
	for i in range(seg, -1, -1):
		outline.append(arch_pts[i])
	outline.append(Vector2(u1, 0))
	outline.append(Vector2(W, 0))
	outline.append(Vector2(W, top))
	outline.append(Vector2(0, top))
	b.poly(F, "w9_stucco", outline, P(a, t, n, 0, 0, -0.25), t, UP, n)
	b.poly(F, "w9_stucco", outline, P(a, t, n, 0, 0, 0.05), t, UP, -n)
	var s = b.st(F, "w9_stucco")
	for i in range(seg, -1, -1):
		var q = arch_pts[i]
		var p0 = P(a, t, n, q.x, q.y, -0.25)
		var p1 = P(a, t, n, q.x, q.y, 0.05)
		if i < seg:
			var qp = arch_pts[i + 1]
			var pp0 = P(a, t, n, qp.x, qp.y, -0.25)
			var pp1 = P(a, t, n, qp.x, qp.y, 0.05)
			var mid = (q + qp) * 0.5
			var nn = (P(a, t, n, (u0 + u1) * 0.5, spring, 0) - P(a, t, n, mid.x, mid.y, 0)).normalized()
			b.tri(s, pp0, p0, p1, Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), nn)
			b.tri(s, pp0, p1, pp1, Vector2(0, 0), Vector2(1, 1), Vector2(0, 1), nn)
	for side in [[u0, t], [u1, -t]]:
		b.quad(F, "w9_stucco", [P(a, t, n, side[0], 0, -0.25), P(a, t, n, side[0], 0, 0.05), P(a, t, n, side[0], spring, 0.05), P(a, t, n, side[0], spring, -0.25)], side[1])
	b.box(F, "w9_stucco_base", P(a, t, n, u0 * 0.5, 0.2, -0.27), b.abs_size(t, u0, 0.4, 0.06, n), Transform3D.IDENTITY, ["-y"])
	b.box(F, "w9_stucco_base", P(a, t, n, (u1 + W) * 0.5, 0.2, -0.27), b.abs_size(t, W - u1, 0.4, 0.06, n), Transform3D.IDENTITY, ["-y"])
	K.ob(b, P(a, t, n, 0, 0, -0.3), P(a, t, n, W, 0, 0.1), 0.02)
	# the name in heavy rounded white letters over the arch, the lanterns, the gate
	b.box(F, "w9_stucco_shade", P(a, t, n, W * 0.5, 3.95, -0.255), b.abs_size(t, W - 1.0, 1.25, 0.01, n))
	b.box(F, "w9_stucco", P(a, t, n, W * 0.5, 4.62, -0.4), b.abs_size(t, W - 0.6, 0.06, 0.3, n))
	AK.letters(b, F, LET + "ab_american.json", P(a, t, n, W * 0.5, 4.02, -0.26), n, "w9_bank_letter", "w9_bank_letter", 0.02, 0.07)
	AK.letters(b, F, LET + "ab_bank.json", P(a, t, n, W * 0.5, 3.46, -0.26), n, "w9_bank_letter", "w9_bank_letter", 0.02, 0.07)
	for su in [u0 * 0.5, (u1 + W) * 0.5]:
		coach_lamp(b, F, P(a, t, n, su, 2.3, -0.5), n, 0.4)
	var gate = PackedVector2Array([Vector2(u0, 0), Vector2(u1, 0)])
	for i in seg + 1:
		gate.append(arch_pts[i])
	b.poly("w9b_gate", "w9_gate", gate, P(a, t, n, 0, 0, -0.05), t, UP, n)
	# the lobby behind the gate: a pale floor, the teller line with its glass, a desk
	M2.shell2(b, "w9b_shell", a, t, n, W, D, 3.0, 0.0, "w9_lobby_floor", 0.61, "w8_cream", "kb_ceiling", [W * 0.5 - 0.3], W * 0.5, 1.0)
	var co = P(a, t, n, W - 1.0, 0, 5.2)
	K.lbox(b, G, "w8_walnut", co, -t, n, 0.0, 0.0, 0.0, W - 2.0, 1.1, 0.7, ["-y"])
	K.lbox(b, G, "w9_lobby_floor", co, -t, n, -0.03, 1.1, -0.03, W - 1.94, 0.04, 0.76)
	b.quad("glass", "glass", [K.L(co, -t, n, 0.0, 1.14, 0.35), K.L(co, -t, n, W - 2.0, 1.14, 0.35), K.L(co, -t, n, W - 2.0, 2.2, 0.35), K.L(co, -t, n, 0.0, 2.2, 0.35)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	for k in 4:
		W8.post(b, G, "w8_walnut", a, t, n, 1.0 + k * (W - 2.0) / 3.0, 0.06, 1.14, 2.2, 5.2 - 0.35, 0.06)
	K.lbox(b, G, "w8_walnut", P(a, t, n, 1.2, 0, 2.2), t, n, 0.0, 0.0, 0.0, 1.4, 0.76, 0.7)
	# stanchions with a rope across the lobby
	for k in 4:
		b.cyl(G, "w9_brass", P(a, t, n, 3.0 + k * 1.3, 0, 3.4), 0.03, 0.03, 0.95, 8, true, false)
	b.box(G, "s6_red_carpet", P(a, t, n, 3.0 + 1.95, 0.85, 3.4), b.abs_size(t, 3.9, 0.04, 0.04, n))

# ------------------------------------------------------------------ materials
## "w9_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"stone":
			m.albedo_texture = b.tex("sm/stone.png"); m.roughness = 0.6
			m.albedo_color = Color(1.05, 1.0, 0.92)
		"neon_aqua":
			m.albedo_color = Color("#b8fff0")
			m.emission_enabled = true; m.emission = Color("#40e8c8"); m.emission_energy_multiplier = 2.4
			m.set_meta("e_day", 2.0); m.set_meta("e_night", 2.4)
		"floor_sand":
			m.albedo_texture = b.tex("wl/floor.png"); m.roughness = 0.25; m.metallic_specular = 0.55
			m.albedo_color = Color(1.0, 0.95, 0.86)
		"seaglass":
			m.albedo_color = Color("#bfe0d4"); m.roughness = 0.8
		"aqua":
			m.albedo_color = Color("#2ab8a8"); m.roughness = 0.4
		"beach":
			m.albedo_texture = b.tex("w9/beach.png"); m.roughness = 0.4
			K.emit_tex(m, 0.8)
		"trunk":
			m.albedo_color = Color("#6a4e32"); m.roughness = 0.9
		"leaf":
			m.albedo_color = Color("#3c7a44"); m.roughness = 0.7
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"dark_grey":
			m.albedo_color = Color("#3a3a3e"); m.roughness = 0.7
		"brushed":
			m.albedo_color = Color("#c4c8cc"); m.metallic = 0.6; m.roughness = 0.35
		"brushed_dark":
			m.albedo_color = Color("#9a9ea4"); m.metallic = 0.6; m.roughness = 0.3
		"black_clothes":
			m.albedo_texture = b.tex("w9/black_clothes.png"); m.roughness = 0.8
			K.emit_tex(m, 0.2)
		"black_rack":
			m.albedo_texture = b.tex("w9/black_clothes.png"); m.roughness = 0.8
			m.uv1_scale = Vector3(1.5, 0.5, 1.0)
			K.emit_tex(m, 0.15)
		"stucco_shade":
			m.albedo_color = Color("#c9c6c0"); m.roughness = 0.9
		"rave_red":
			m.albedo_color = Color("#e83060"); m.roughness = 0.4
			K.emit(m, Color("#d02050"), 0.6)
		"posters":
			m.albedo_texture = b.tex("w9/posters.png"); m.roughness = 0.5
			K.emit_tex(m, 0.25)
		"plum":
			m.albedo_color = Color("#3a1828"); m.roughness = 0.5
		"concepts_sign":
			m.albedo_texture = b.tex("w9/concepts_sign.png"); m.roughness = 0.4
			K.emit_tex(m, 0.9)
		"solid_red":
			m.albedo_color = Color("#d0302a"); m.roughness = 0.35
		"solid_yellow":
			m.albedo_color = Color("#f0c830"); m.roughness = 0.35
		"solid_blue":
			m.albedo_color = Color("#2f62c8"); m.roughness = 0.35
		"solid_green":
			m.albedo_color = Color("#30a868"); m.roughness = 0.35
		"uniforms":
			m.albedo_texture = b.tex("w9/uniforms.png"); m.roughness = 0.7
			K.emit_tex(m, 0.15)
		"backpacks":
			m.albedo_texture = b.tex("w9/backpacks.png"); m.roughness = 0.7
			K.emit_tex(m, 0.15)
		"green":
			m.albedo_color = Color("#235c3a"); m.roughness = 0.5
		"cream_letter":
			m.albedo_color = Color("#f4ead0"); m.roughness = 0.4
			K.emit(m, Color("#e8dcb8"), 0.55)
		"gingham":
			m.albedo_texture = b.tex("w9/gingham.png"); m.roughness = 0.8
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"country":
			m.albedo_texture = b.tex("w9/country.png"); m.roughness = 0.7
			K.emit_tex(m, 0.15)
		"cream_wall":
			m.albedo_color = Color("#efe2c8"); m.roughness = 0.85
		"pine":
			m.albedo_texture = b.tex("wood_dark.png"); m.roughness = 0.6
			m.albedo_color = Color(1.35, 1.15, 0.9)
			m.uv1_scale = Vector3(3.0, 3.0, 1.0)
		"quilt":
			m.albedo_texture = b.tex("w9/quilt.png"); m.roughness = 0.9
		"brick":
			m.albedo_texture = b.tex("w9/brick.png"); m.roughness = 0.85
			m.albedo_color = Color(0.72, 0.6, 0.54)
			m.uv1_scale = Vector3(1.0 / 1.2, 1.0 / 0.6, 1.0)
		"plaque":
			m.albedo_texture = b.tex("w9/plaque.png"); m.roughness = 0.4
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			K.emit_tex(m, 0.35)
		"lamp_glass":
			m.albedo_color = Color("#ffe0a0")
			K.emit(m, Color("#ffcc80"), 1.6)
		"panel":
			m.albedo_texture = b.tex("wood_dark.png"); m.roughness = 0.5
			m.albedo_color = Color(0.75, 0.55, 0.42)
			m.uv1_scale = Vector3(3.0, 3.0, 1.0)
		"cloth":
			m.albedo_color = Color("#f2f0ea"); m.roughness = 0.9
		"candle":
			m.albedo_color = Color("#c02020")
			K.emit(m, Color("#ff7030"), 1.2)
		"stucco":
			m.albedo_color = Color("#f4f2ee"); m.roughness = 0.9
		"stucco_base":
			m.albedo_color = Color("#cfc8bc"); m.roughness = 0.8
		"bank_letter":
			m.albedo_color = Color("#ffffff"); m.roughness = 0.5
			K.emit(m, Color("#e8e8e4"), 0.5)
		"gate":
			m.albedo_texture = b.tex("w9/gate.png"); m.roughness = 0.6
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"lobby_floor":
			m.albedo_texture = b.tex("wl/floor.png"); m.roughness = 0.2; m.metallic_specular = 0.6
			m.albedo_color = Color(0.95, 0.9, 0.82)
		"brass":
			m.albedo_color = Color("#c8a048"); m.metallic = 0.8; m.roughness = 0.3
		_:
			return false
	return true
