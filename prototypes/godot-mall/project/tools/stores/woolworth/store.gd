## Woolworth (store s13), the five-and-dime on the east hall, built to
## design/storefronts/woolworth.md.
##
## The front follows Steven's photo of the sign (Oct 7): a dark fascia with WOOLWORTH in lit
## orange-red slab-serif channel letters, cream piers, a wide open front. The inside follows the 1991
## Signal Hill Mall (Statesville, NC) video Steven chose as "the exact Woolworth layout":
## glossy off-white vinyl with a red stripe along the main aisles, a white lay-in ceiling
## with long rows of troffers, plain square columns, a red band of department names high on
## the walls, white gondolas, numbered checkout lanes and a customer service booth, round
## racks of clothes, and the coffee-shop restaurant. Steven: the restaurant was on the
## RIGHT as you face the store, entered from the store and by its own mall door; there was
## no garden center.
##
## Frame: u runs along the 36 m frontage from the edge's start a (z = -14, the viewer's
## right) to z = 22 (u = 36). d runs into the store (-x); the room is 36 m deep.

const K = preload("res://tools/stores/media/kit.gd")
const CH = preload("res://tools/stores/signs/channel.gd")
const UNIT = 36.0
const DEPTH = 36.0
const SIDE = 0.12
const HEAD = 3.0
const FTOP = 4.4
const PROUD = 0.25
const CEIL = 3.6
const R_U = 9.0           # the restaurant's width (u 0..9) and depth (d 0..14)
const R_D = 14.0
const R_CEIL = 3.0
const WALL_T = 0.6        # the wall between the restaurant and the store (u 9.0..9.6)
const BAY = 1.22
const UP = Vector3.UP
const BOARDS = [0.35, 0.72, 1.09, 1.46, 1.83]
const LOW = [0.35, 0.75, 1.15, 1.55]

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

## Mesh groups by quadrant, so no one group's lightmap unwrap gets too big.
static func grp(kind, u, d):
	return "wl%d%d_%s" % [int(u >= 22.0), int(d >= 18.0), kind]

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var rng = RandomNumberGenerator.new()
	rng.seed = 1991
	front(b, "wlf_props", a, t, n)
	room(b, a, t, n, rng)
	restaurant(b, a, t, n, rng)
	floor_fixtures(b, a, t, n, rng)
	for c in [[22.0, 9.0, 18.0], [22.0, 27.0, 18.0], [4.5, 7.0, 14.0]]:
		var rp = ReflectionProbe.new()
		rp.position = P(a, t, n, c[0], CEIL * 0.5, c[1])
		rp.size = (t * (UNIT if c[0] > 10.0 else R_U) + n * c[2]).abs() + Vector3(0.1, CEIL + 0.1, 0.1)
		rp.box_projection = true
		rp.interior = true
		rp.update_mode = ReflectionProbe.UPDATE_ONCE
		rp.intensity = 0.6
		b.light_root.add_child(rp)

# ------------------------------------------------------------------ the front
static func front(b, G, a, t, n):
	var LH = b.LANE_H
	var o = P(a, t, n, 0, 0, 0)
	# the dark fascia across the whole frontage, standing out over the hall (Steven's photo,
	# Oct 7: design/storefronts/refs/woolworth-front.png)
	K.lbox(b, G, "sg_wl_fascia", o, t, n, 0.0, HEAD, 0.0, UNIT, FTOP - HEAD, PROUD, ["-z"])
	b.quad(G, "md_fascia_white", [P(a, t, n, 0, FTOP, 0), P(a, t, n, UNIT, FTOP, 0), P(a, t, n, UNIT, LH, 0), P(a, t, n, 0, LH, 0)], n)
	# WOOLWORTH in lit channel letters on the fascia, over the middle of the store's opening
	# (tools/stores/signs: the photo's letters, 0.78 m capitals)
	var lc = (R_U + WALL_T + UNIT) * 0.5
	CH.build(b, "wlf_sign", "res://tools/stores/signs/wl_logo.json", P(a, t, n, lc, 3.31, -PROUD), n,
		"sg_wl_face", "sg_wl_return", "sg_wl_trim", 0.02, 0.12, 0.012, "sg_wl_glow")
	# the restaurant's own front (u 0..9): a bulkhead, glass, an open door with an aluminium frame
	var al = "wl_alum"
	K.lbox(b, G, "md_fascia_white", o, t, n, 0.0, 0.0, -0.12, R_U, 0.45, 0.12)
	for s in [[0.25, 3.7], [5.3, R_U - 0.25]]:
		b.quad("glass", "glass", [P(a, t, n, s[0], 0.45, 0.05), P(a, t, n, s[1], 0.45, 0.05), P(a, t, n, s[1], HEAD, 0.05), P(a, t, n, s[0], HEAD, 0.05)], n,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
		K.ob_local(b, o, t, -n, s[0], -0.1, s[1], 0.15, 0.1)
	for u in [0.25, 2.0, 3.7, 5.3, 7.0, R_U - 0.25]:
		K.lbox(b, G, al, o, t, n, u - 0.03, 0.0, -0.08, 0.06, HEAD, 0.1)
	K.lbox(b, G, al, o, t, n, 0.0, HEAD - 0.08, -0.08, R_U, 0.08, 0.1)
	K.lbox(b, G, al, o, t, n, 3.7, 2.2, -0.08, 1.6, 0.06, 0.1)
	b.quad("glass", "glass", [P(a, t, n, 3.7, 2.26, 0.05), P(a, t, n, 5.3, 2.26, 0.05), P(a, t, n, 5.3, HEAD - 0.08, 0.05), P(a, t, n, 3.7, HEAD - 0.08, 0.05)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	# the door leaves stand open against the glass, inside
	for s in [[3.7, 1.0], [5.3, -1.0]]:
		var hinge = P(a, t, n, s[0], 0, 0.12)
		K.lbox(b, G, al, hinge, -n, t * s[1], 0.0, 0.0, 0.0, 0.8, 2.2, 0.05)
	# "Restaurant" over its door: red lit channel letters straight on the fascia, no plate behind
	# them (Steven, Oct 8; tools/stores/signs/make_wl_restaurant.py)
	CH.build(b, "wlf_sign", "res://tools/stores/signs/wlr_logo.json", P(a, t, n, 4.5, 3.5, -PROUD), n,
		"sg_wlr_face", "sg_wl_return", "sg_wl_trim", 0.02, 0.09, 0.01, "sg_wlr_glow")
	# the cream pier between the restaurant and the store, and one at the store's far end
	K.lbox(b, G, "sg_wl_cream", o, t, n, R_U, 0.0, -0.05, WALL_T, HEAD, 0.2, ["-y"])
	K.lbox(b, G, "sg_wl_cream", o, t, n, UNIT - 0.45, 0.0, -0.05, 0.45, HEAD, 0.2, ["-y"])
	K.ob_local(b, o, t, -n, UNIT - 0.45, -0.15, UNIT, 0.6)
	K.ob_local(b, o, t, -n, R_U, -0.15, R_U + WALL_T, 0.6)
	# the store's open front: a soffit just inside, a pier at the left end
	b.quad(G, "md_fascia_white", [P(a, t, n, R_U + WALL_T, HEAD, 0), P(a, t, n, UNIT - SIDE, HEAD, 0), P(a, t, n, UNIT - SIDE, HEAD, 0.8), P(a, t, n, R_U + WALL_T, HEAD, 0.8)], Vector3.DOWN)
	b.quad(G, "md_fascia_white", [P(a, t, n, R_U + WALL_T, HEAD, 0.8), P(a, t, n, UNIT - SIDE, HEAD, 0.8), P(a, t, n, UNIT - SIDE, CEIL, 0.8), P(a, t, n, R_U + WALL_T, CEIL, 0.8)], -n)
	for u in [12.0, 16.0, 20.0, 24.0, 28.0, 32.0]:
		b.cyl(G, "md_downlight", P(a, t, n, u, HEAD - 0.004, 0.4), 0.09, 0.09, 0.004, 12, false, true)
	# the clock and the exit sign over the opening, inside (video 5:34)
	b.cur_color = Color("#f4f4f0")
	b.cyl(G, "vcolor", P(a, t, n, 22.5, HEAD + 0.2, 0.84) - n * 0.0, 0.18, 0.18, 0.03, 20, true, false)
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, 26.0, HEAD + 0.25, 0.84), b.abs_size(t, 0.36, 0.16, 0.06, n))

# ------------------------------------------------------------------ the room
static func room(b, a, t, n, rng):
	var G = "wl_shell"
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	var u9 = R_U + WALL_T
	# floors: the store's glossy vinyl; behind the restaurant too
	K.floor_rect(b, G, "wl_floor", a, t, n, u9, u1, 0.0, dB, 1.22)
	K.floor_rect(b, G, "wl_floor", a, t, n, SIDE, u9, R_D, dB, 1.22)
	# the red stripe inset along the main aisle into the store and the cross aisle (video 2:28, 3:04)
	var stripes = [[20.8, 20.95, 0.9, 33.0], [24.05, 24.2, 0.9, 33.0], [u9, 35.4, 16.8, 16.95], [u9, 35.4, 20.05, 20.2]]
	for s in stripes:
		var q = [P(a, t, n, s[0], 0.003, s[2]), P(a, t, n, s[1], 0.003, s[2]), P(a, t, n, s[1], 0.003, s[3]), P(a, t, n, s[0], 0.003, s[3])]
		b.quad(G, "wl_red", q, UP)
	# the lay-in ceiling at 3.6 m with long rows of troffers; baked spots on a coarse grid
	K.ceiling(b, G, a, t, n, u9, u1, 0.8, dB, CEIL, [11.0, 14.0, 17.0, 20.0, 23.0, 26.0, 29.0, 32.0, 35.0], 2.44, false)
	K.ceiling(b, G, a, t, n, SIDE, u9, R_D + SIDE, dB, CEIL, [2.0, 5.0, 8.0], 2.44, false)
	for u in [3.5, 10.5, 17.5, 24.5, 31.5]:
		for d in [4.0, 10.0, 16.0, 22.0, 28.0, 33.5]:
			if u < R_U and d < R_D:
				continue
			var l = b.add_spot(P(a, t, n, u, CEIL - 0.08, d), Vector3.DOWN, 1.4, 7.0, 70.0, Color(0.96, 0.98, 1.0))
			b.tag(l, "", 1.4, 1.4)
	# walls
	K.wall(b, G, "md_wall", a, t, n, u1, dB, u1, 0.0, 0.0, CEIL, -t)
	K.wall(b, G, "md_wall", a, t, n, u1, dB, SIDE, dB, 0.0, CEIL, n)
	K.wall(b, G, "md_wall", a, t, n, SIDE, R_D, SIDE, dB, 0.0, CEIL, t)
	# the restaurant's walls seen from the store: its back (d 14) and its side (u 9.6), with
	# the wood-framed opening at d 9.4..11.2 (video 7:37-7:49)
	K.wall(b, G, "md_wall", a, t, n, u9, R_D, SIDE, R_D, 0.0, CEIL, -n)
	K.wall(b, G, "md_wall", a, t, n, u9, 0.0, u9, 9.4, 0.0, CEIL, t)
	K.wall(b, G, "md_wall", a, t, n, u9, 11.2, u9, R_D, 0.0, CEIL, t)
	K.wall(b, G, "md_wall", a, t, n, u9, 9.4, u9, 11.2, 2.4, CEIL, t)
	b.quad(G, "md_wall", [P(a, t, n, R_U - 0.12, 2.4, 9.4), P(a, t, n, u9, 2.4, 9.4), P(a, t, n, u9, 2.4, 11.2), P(a, t, n, R_U - 0.12, 2.4, 11.2)], Vector3.DOWN)
	for s in [[9.4, 1.0], [11.2, -1.0]]:
		b.quad(G, "wl_wood", [P(a, t, n, R_U - 0.12, 0, s[0]), P(a, t, n, u9, 0, s[0]), P(a, t, n, u9, 2.4, s[0]), P(a, t, n, R_U - 0.12, 2.4, s[0])], -n * s[1])
	var fr = P(a, t, n, u9, 0, 9.3)
	for s in [[0.0, 0.1, 0.0, 2.5], [1.9, 2.0, 0.0, 2.5], [0.0, 2.0, 2.4, 2.5]]:
		K.lbox(b, G, "wl_wood", fr, -n, t, s[0], s[2], 0.0, s[1] - s[0], s[3] - s[2], 0.04)
	K.ob_local(b, P(a, t, n, R_U - 0.12, 0, 0), -n, t, 0.0, 0.0, 9.4, WALL_T + 0.12, 0.1)
	K.ob_local(b, P(a, t, n, R_U - 0.12, 0, 0), -n, t, 11.2, 0.0, R_D, WALL_T + 0.12, 0.1)
	K.ob_local(b, P(a, t, n, SIDE, 0, R_D - 0.1), t, -n, 0.0, 0.0, R_U, 0.2, 0.1)
	# "Restaurant" in red letters on the white wall over the opening (video 7:37-7:49)
	K.fq(b, G, "wl_signs", P(a, t, n, u9, 0, 8.6), -n, t, 0.0, 3.6, 2.55, 3.35, 0.02, 0.0, 0.5, 0.5, 1.0)
	# the red band of department names high on the walls: back wall, left wall, right wall
	# left wall (u = 35.88), names over what stands below, front to back
	for s in [[6.0, 3], [12.0, 3], [18.0, 1], [24.0, 2], [30.0, 2]]:
		K.fq(b, G, "wl_dept_band", P(a, t, n, u1, 0, s[0] - 6.0), -n, -t, 0.0, 6.0, 2.65, 3.4, 0.01, 0.0, s[1] / 12.0, 1.0, (s[1] + 1) / 12.0)
	# back wall (d = 35.88), from the left corner to the right
	for s in [[36.0, 2], [30.0, 1], [24.0, 0], [18.0, 0], [12.0, 6], [6.0, 5]]:
		K.fq(b, G, "wl_dept_band", P(a, t, n, s[0], 0, dB), -t, n, 0.0, 6.0, 2.65, 3.4, 0.01, 0.0, s[1] / 12.0, 1.0, (s[1] + 1) / 12.0)
	# right wall behind the restaurant (u = 0.12)
	for s in [[R_D + 7.0, 5], [R_D + 14.0, 6], [dB, 7]]:
		K.fq(b, G, "wl_dept_band", P(a, t, n, SIDE, 0, s[0]), n, t, 0.0, 6.0, 2.65, 3.4, 0.01, 0.0, s[1] / 12.0, 1.0, (s[1] + 1) / 12.0)
	# plain square columns flanking the main aisle (video 2:04, 2:31)
	for u in [20.3, 24.7]:
		for d in [9.0, 18.5, 27.5]:
			var c = P(a, t, n, u, 0, d)
			b.box(G, "md_wall", c + UP * CEIL * 0.5, Vector3(0.5, CEIL, 0.5), Transform3D.IDENTITY, ["-y", "+y"])
			K.ob(b, c - Vector3(0.25, 0, 0.25), c + Vector3(0.25, 0, 0.25), 0.1)
	# the stockroom doors in the back wall, an exit sign over each
	for du in [21.2, 23.8]:
		b.cur_color = Color("#d8d6d0")
		b.box(G, "vcolor", P(a, t, n, du, 1.05, dB - 0.02), b.abs_size(t, 1.2, 2.1, 0.04, n))
		b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, 22.5, 2.35, dB - 0.05), b.abs_size(t, 0.36, 0.16, 0.06, n))

# ------------------------------------------------------------------ the restaurant
static func restaurant(b, a, t, n, rng):
	var G = "wl_rest"
	var S = "wl_rest_small"
	var u0 = SIDE
	var u1 = R_U - 0.12
	var dB = R_D - 0.12
	K.floor_rect(b, G, "wl_rest_floor", a, t, n, u0, u1, 0.0, dB, 0.61)
	# a darker beige ceiling with warm downlights (video 5:43, 6:01)
	var P2 = func(u, y, d): return P(a, t, n, u, y, d)
	b.quad(G, "wl_rest_ceiling", [P2.call(u0, R_CEIL, 0.0), P2.call(u1, R_CEIL, 0.0), P2.call(u1, R_CEIL, dB), P2.call(u0, R_CEIL, dB)], Vector3.DOWN)
	for u in [1.6, 4.5, 7.4]:
		for d in [2.0, 5.0, 8.0, 11.0]:
			b.cyl(G, "wl_warm_disc", P2.call(u, R_CEIL - 0.004, d), 0.08, 0.08, 0.004, 12, false, true)
	for c in [[2.5, 4.0], [6.5, 4.0], [2.5, 10.0], [6.5, 10.0]]:
		var l = b.add_omni(P2.call(c[0], R_CEIL - 0.4, c[1]), 0.5, 6.0, Color(1.0, 0.86, 0.66))
		b.tag(l, "", 0.5, 0.6)
	# walls: beige, a wood-slat wainscot, lattice panels in wood frames on the right wall,
	# brass sconces with globe shades, framed food photos (video 5:46-6:25)
	K.wall(b, G, "wl_beige", a, t, n, u0, 0.0, u0, dB, 0.9, R_CEIL, t)
	# the left wall, with the opening into the store at d 9.4..11.2
	K.wall(b, G, "wl_beige", a, t, n, u1, 9.4, u1, 0.0, 0.9, R_CEIL, -t)
	K.wall(b, G, "wl_beige", a, t, n, u1, dB, u1, 11.2, 0.9, R_CEIL, -t)
	K.wall(b, G, "wl_beige", a, t, n, u1, 11.2, u1, 9.4, 2.4, R_CEIL, -t)
	K.wall(b, G, "wl_beige", a, t, n, u1, dB, u0, dB, 0.9, R_CEIL, n)
	for w in [[u0, 0.0, u0, dB, t], [u1, 9.4, u1, 0.0, -t], [u1, dB, u1, 11.2, -t], [u1, dB, u0, dB, n]]:
		var pa = P2.call(w[0], 0, w[1])
		var pb = P2.call(w[2], 0, w[3])
		var Lw = pa.distance_to(pb)
		b.quad(G, "wl_slats", [pa, pb, pb + UP * 0.9, pa + UP * 0.9], w[4], [Vector2(0, 1.5), Vector2(Lw / 0.6, 1.5), Vector2(Lw / 0.6, 0), Vector2(0, 0)])
		b.cur_color = Color("#6a4424")
		b.box(G, "vcolor", (pa + pb) * 0.5 + UP * 0.92 + w[4] * 0.02, b.abs_size((pb - pa).normalized(), Lw, 0.05, 0.04, w[4]))
		b.cur_color = Color.WHITE
	# the right wall: lattice panels and sconces between them, booths below
	var k = 0
	for d in [1.2, 3.4, 5.6, 7.8, 10.0]:
		K.fq(b, G, "wl_lattice", P2.call(u0, 0, d), n, t, 0.0, 0.8, 1.15, 2.45, 0.01)
		if k < 4:
			var sc = P2.call(u0 + 0.12, 1.85, d + 1.5)
			b.cur_color = Color("#b88d3e")
			b.box(S, "vcolor", sc - t * 0.06, Vector3(0.05, 0.16, 0.05).abs())
			b.cur_color = Color.WHITE
			K.column(b, S, "wl_globe", sc + UP * 0.02, 0.07, 0.14, 10)
		k += 1
	# framed food photos in a loose grid on the left and back walls
	for p in [[1.2, 1.6, 0], [2.0, 2.2, 1], [3.6, 1.7, 2], [4.4, 2.3, 3], [6.0, 1.6, 1], [6.8, 2.25, 0], [8.2, 1.7, 3], [12.4, 1.9, 2]]:
		K.fq(b, G, "wl_food_photos", P2.call(u1, 0, p[0]), -n, -t, 0.0, 0.55, p[1], p[1] + 0.55, 0.01, p[2] * 0.25, 0.0, p[2] * 0.25 + 0.25, 1.0)
	# booths along the right wall: orange-red vinyl benches, a white table between (video 6:16)
	for d in [1.6, 3.8, 6.0, 8.2, 10.4]:
		booth(b, G, P2.call(u0, 0, d), -n, t, rng)
	# free-standing tables with chairs (video 6:25)
	for c in [[4.6, 3.0], [4.6, 6.2], [6.9, 3.0], [6.9, 6.2]]:
		table(b, G, P2.call(c[0], 0, c[1]))
		for s in [-1.0, 1.0]:
			chair(b, S, P2.call(c[0], 0, c[1]) - n * 0.0 + t * 0.62 * s, -t * s)
	# the counter across the back: food-photo panels on its front, a pie case, the menu board
	# with two monitors above, a soda fountain on the back bar (video 5:43, 6:01)
	var co = P2.call(u1 - 1.1, 0, dB - 2.2)
	K.lbox(b, G, "wl_laminate", co, -t, n, 0.0, 0.0, 0.0, 6.8, 1.0, 0.6, ["-y"])
	K.fq(b, G, "wl_rest_counter", co, -t, n, 0.0, 6.8, 0.0, 1.0, 0.602, 0.0, 0.0, 1.7, 1.0)
	b.cur_color = Color("#5a3a22")
	K.lbox(b, G, "vcolor", co, -t, n, -0.02, 1.0, -0.02, 6.84, 0.04, 0.66, ["-y"])
	b.cur_color = Color.WHITE
	var pie = K.L(co, -t, n, 1.0, 1.04, 0.1)
	K.lbox(b, S, "wl_steel", pie, -t, n, 0.0, 0.0, 0.0, 1.0, 0.06, 0.45)
	b.cur_color = Color("#e8d8b0")
	for j in 3:
		b.cyl(S, "vcolor", K.L(co, -t, n, 1.2 + j * 0.3, 1.12, 0.3), 0.12, 0.12, 0.05, 12, true, false)
	b.cur_color = Color.WHITE
	b.quad("glass", "glass", [K.L(co, -t, n, 1.0, 1.1, 0.45), K.L(co, -t, n, 2.0, 1.1, 0.45), K.L(co, -t, n, 2.0, 1.45, 0.45), K.L(co, -t, n, 1.0, 1.45, 0.45)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	K.lbox(b, S, "wl_steel", pie, -t, n, 0.0, 0.41, 0.0, 1.0, 0.04, 0.45)
	K.register(b, S, K.L(co, -t, n, 5.6, 1.04, 0.1), -t, n)
	K.ob_local(b, co, -t, n, 0.0, -2.1, 6.8, 0.6)
	# the back bar
	var bo = P2.call(u1, 0, dB)
	K.lbox(b, G, "wl_steel", bo, -t, n, 0.3, 0.0, 0.0, 7.4, 0.9, 0.55)
	b.cur_color = Color("#c8c8cc")
	K.lbox(b, S, "vcolor", bo, -t, n, 3.0, 0.9, 0.05, 0.8, 0.5, 0.4)
	b.cur_color = Color("#c81e28")
	K.lbox(b, S, "vcolor", bo, -t, n, 3.05, 1.3, 0.38, 0.7, 0.08, 0.03)
	b.cur_color = Color.WHITE
	# the backlit menu board and two monitors
	K.fq(b, G, "wl_menu", bo, -t, n, 1.0, 6.4, 1.75, 2.6, 0.03, 0.0, 0.0, 1.0, 1.0)
	for x in [0.3, 6.6]:
		b.cur_color = Color("#1c1c1e")
		K.lbox(b, S, "vcolor", bo, -t, n, x, 2.05, 0.0, 0.5, 0.4, 0.4)
		b.cur_color = Color.WHITE
		K.fq(b, S, "md_screens", bo, -t, n, x + 0.05, x + 0.45, 2.1, 2.4, 0.402, 0.0, 0.0, 0.5, 1.0)

## A booth: two orange-red vinyl benches facing each other across a white table, against
## the wall at `o` (`r` along the wall, `f` out into the room).
static func booth(b, G, o, r, f, rng):
	for s in [-1.0, 1.0]:
		var bo = o + r * (0.65 * s)
		var face = -r * s
		var rr = (-face).cross(UP)
		b.box(G, "wl_booth", bo + f * 0.6 + UP * 0.22, b.abs_size(rr, 1.2, 0.44, 0.5, face))
		b.box(G, "wl_booth", bo + f * 0.6 - face * 0.22 + UP * 0.72, b.abs_size(rr, 1.2, 0.56, 0.12, face))
	table(b, G, o + f * 0.6, 0.62, 1.1)
	K.ob(b, o - r * 0.95, o + r * 0.95 + f * 1.25, 0.05)

## A white laminate table on a pedestal (the restaurant's tables, video 6:25).
static func table(b, G, c, w = 0.75, l = 0.75):
	b.cur_color = Color("#2a2a2c")
	b.cyl(G, "vcolor", c, 0.22, 0.22, 0.03, 12, true, false)
	b.cyl(G, "vcolor", c, 0.04, 0.04, 0.72, 8, false, false)
	b.cur_color = Color.WHITE
	b.box(G, "wl_laminate", c + UP * 0.74, Vector3(w, 0.035, l) if true else Vector3.ONE)
	K.ob(b, c - Vector3(w, 0, l) * 0.5, c + Vector3(w, 0, l) * 0.5, 0.15)

## An orange-red vinyl chair facing `f`.
static func chair(b, S, c, f):
	var r = (-f).cross(UP)
	b.cur_color = Color("#2a2a2c")
	for q in [Vector2(-0.18, -0.18), Vector2(0.18, -0.18), Vector2(-0.18, 0.18), Vector2(0.18, 0.18)]:
		b.box(S, "vcolor", c + r * q.x + f * q.y + UP * 0.22, Vector3(0.025, 0.44, 0.025))
	b.cur_color = Color.WHITE
	b.box(S, "wl_booth", c + UP * 0.47, b.abs_size(r, 0.44, 0.07, 0.44, f))
	b.box(S, "wl_booth", c - f * 0.2 + UP * 0.75, b.abs_size(r, 0.42, 0.42, 0.05, f))

# ------------------------------------------------------------------ the sales floor
static func floor_fixtures(b, a, t, n, rng):
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	var u9 = R_U + WALL_T
	# -- perimeter wall shelving under the red band
	# left wall, front to back: apparel (folded), apparel, housewares, domestics (linens)
	var left = [["linens"], ["boxes"], ["boxes", "hba"], ["linens"], ["boxes"]]
	var d = 1.6
	var k = 0
	while d + BAY <= dB - 0.5:
		var sh = [["linens"]] if d < 12.0 else ([["boxes"]] if d < 24.0 else [["linens", "boxes"]])
		K.bay_run(b, grp("fix", 30.0, d), grp("merch", 30.0, d), P(a, t, n, u1, 0, d), -n, -t, BAY, 1, BOARDS, sh, [-1], "", 0.0, rng, 0.4)
		d += BAY
		k += 1
	# back wall, left corner to the right: housewares, toys, the stockroom doors, party goods, cards
	var u = u1 - 0.45
	while u - BAY >= SIDE + 0.45:
		if u > 20.4 and u - BAY < 24.9:
			u -= BAY
			continue   # the stockroom doors
		var sh = [["boxes"]] if u > 24.0 else ([["kb_action", "kb_vehicles"], ["kb_dolls", "kb_games"]][int(u) % 2] if u > 9.6 else [["party"]])
		K.bay_run(b, grp("fix", u, 30.0), grp("merch", u, 30.0), P(a, t, n, u, 0, dB), -t, n, BAY, 1, BOARDS, [sh] if sh[0] is String else sh, [-1], "", 0.0, rng, 0.4)
		u -= BAY
	# right wall behind the restaurant: greeting cards, then party goods
	d = dB - 0.45
	while d - BAY >= R_D + 0.6:
		var sh = [["gcards"]] if d > 24.0 else [["party"]]
		K.bay_run(b, grp("fix", 2.0, d), grp("merch", 2.0, d), P(a, t, n, SIDE, 0, d), n, t, BAY, 1, BOARDS, sh, [-1], "", 0.0, rng, 0.4)
		d -= BAY
	# -- gondola runs across the store either side of the main aisle
	# right front: health & beauty, candy, cards (u 11.2..19.7)
	for s in [[6.0, ["hba"]], [9.3, ["hba", "candy"]], [12.6, ["candy"]]]:
		K.gondola(b, grp("fix", 15.0, s[0]), grp("merch", 15.0, s[0]), P(a, t, n, 19.7, 0, s[0]), -t, n, BAY, 7, LOW, s[1], rng, 0.32)
	# right back: toys (Kay-Bee's sheets; video 0:00-1:16)
	for s in [[22.6, ["kb_action", "kb_vehicles"]], [25.9, ["kb_dolls", "kb_preschool"]], [29.2, ["kb_games", "kb_sports"]], [32.3, ["kb_vehicles", "kb_action"]]]:
		K.gondola(b, grp("fix", 15.0, s[0]), grp("merch", 15.0, s[0]), P(a, t, n, 19.7, 0, s[0]), -t, n, BAY, 7, LOW, s[1], rng, 0.32)
	# behind the restaurant: cards and party goods
	for s in [[17.8, ["gcards"]], [21.4, ["party"]], [25.0, ["gcards"]], [28.6, ["party", "candy"]]]:
		K.gondola(b, grp("fix", 5.0, s[0]), grp("merch", 5.0, s[0]), P(a, t, n, 8.3, 0, s[0]), -t, n, BAY, 4, LOW, s[1], rng, 0.32)
	# left back: housewares, small appliances, linens (video 4:16-5:22)
	for s in [[22.6, ["boxes"]], [25.9, ["boxes", "linens"]], [29.2, ["linens"]], [32.3, ["boxes"]]]:
		K.gondola(b, grp("fix", 30.0, s[0]), grp("merch", 30.0, s[0]), P(a, t, n, 34.2, 0, s[0]), -t, n, BAY, 7, LOW, s[1], rng, 0.32)
	# left front: round racks and T-stands of clothes (video 1:19-1:58, 2:28)
	for c in [[27.0, 6.5], [30.2, 6.5], [33.2, 7.2], [27.0, 10.0], [30.2, 10.0], [33.2, 10.8], [27.0, 13.5], [30.2, 13.5]]:
		round_rack(b, grp("fix", 30.0, 9.0), P(a, t, n, c[0], 0, c[1]), rng)
	# -- the front end: four checkout lanes with numbered lane lights (video 2:16), a cart
	# corral, and the customer service booth with its glass upper wall (video 2:22)
	var lanes = 0
	for uu in [11.2, 13.6, 16.0, 18.4]:
		lanes += 1
		checkout(b, P(a, t, n, uu, 0, 1.6), t, n, lanes * 2 - 1, rng)
	for j in 3:
		cart(b, "wl00_small", P(a, t, n, 20.2 + j * 0.0, 0, 1.4 + j * 0.42), n)
	K.ob(b, P(a, t, n, 19.8, 0, 1.0), P(a, t, n, 20.6, 0, 3.0), 0.1)
	service(b, a, t, n, rng)

## A round rack of hanging clothes: chrome ring on a pole, a ring of garments.
static func round_rack(b, G, c, rng):
	var rad = 0.55
	b.cyl(G, "md_chrome", c, 0.25, 0.25, 0.02, 16, true, false)
	b.cyl(G, "md_chrome", c, 0.02, 0.02, 1.35, 8, false, false)
	var seg = 14
	var u0 = rng.randf()
	for i in seg:
		var a0 = TAU * i / seg
		var a1 = TAU * (i + 1) / seg
		var d0 = Vector3(cos(a0), 0, sin(a0))
		var d1 = Vector3(cos(a1), 0, sin(a1))
		var nn = (d0 + d1).normalized()
		b.quad(G, "wl_garments", [c + d0 * rad + UP * 0.45, c + d1 * rad + UP * 0.45, c + d1 * rad + UP * 1.32, c + d0 * rad + UP * 1.32], nn,
			[Vector2(u0 + float(i) / seg, 1), Vector2(u0 + float(i + 1) / seg, 1), Vector2(u0 + float(i + 1) / seg, 0.1), Vector2(u0 + float(i) / seg, 0.1)])
	b.cyl(G, "md_chrome", c + UP * 1.32, rad + 0.02, rad + 0.02, 0.025, 20, true, false)
	K.ob(b, c - Vector3(rad, 0, rad), c + Vector3(rad, 0, rad), 0.1)

## A checkout counter running into the store (customers pass along it toward the hall),
## a register, an impulse rack at its head, and the numbered lane light on a pole.
static func checkout(b, o, t, n, num, rng):
	var G = "wl00_fix"
	var S = "wl00_small"
	var into = -n
	K.lbox(b, G, "wl_laminate", o, into, t, 0.0, 0.0, 0.0, 2.6, 0.9, 0.75, ["-y"])
	K.fq(b, G, "wl_counter", o, into, t, 0.0, 2.6, 0.0, 0.9, 0.752)
	K.fq(b, G, "wl_counter", o + into * 2.6 + t * 0.75, -into, -t, 0.0, 2.6, 0.0, 0.9, 0.752)
	K.register(b, S, K.L(o, into, t, 0.4, 0.9, 0.2), into, -t)
	# the impulse rack: candy and batteries on a low stand at the lane's head
	K.bay(b, G, "wl00_merch", o + into * 2.7, t, into, 0.75, [0.5, 0.85, 1.2], ["candy"], rng, 0.25)
	# the lane light
	var pole = K.L(o, into, t, 0.1, 0.0, 0.65)
	b.cyl(S, "md_chrome", pole, 0.025, 0.025, 2.5, 8, false, false)
	var lc = pole + UP * 2.62
	b.cur_color = Color("#f4f4f0")
	b.box(S, "vcolor", lc, Vector3(0.3, 0.3, 0.3))
	b.cur_color = Color.WHITE
	for f in [n, -n]:
		var r = (-f).cross(UP)
		K.fq(b, S, "wl_lanes", lc - r * 0.14, r, f, 0.0, 0.28, -0.14, 0.14, 0.152, (num - 1) / 8.0, 0.0, num / 8.0, 1.0)
	K.ob_local(b, o, into, t, 0.0, 0.0, 3.0, 0.75)

## A red shopping cart facing `f` (video 0:13): a wire basket, a handle, a frame on casters.
static func cart(b, S, c, f):
	var r = (-f).cross(UP)
	b.cur_color = Color("#b8141c")
	b.box(S, "vcolor", c + UP * 0.72, b.abs_size(r, 0.5, 0.42, 0.85, f), Transform3D.IDENTITY, ["+y"])
	b.box(S, "vcolor", c - f * 0.47 + UP * 1.0, b.abs_size(r, 0.5, 0.04, 0.04, f))
	b.cur_color = Color("#3a3a3c")
	b.box(S, "vcolor", c + UP * 0.25, b.abs_size(r, 0.44, 0.04, 0.8, f))
	for q in [Vector2(-0.2, -0.38), Vector2(0.2, -0.38), Vector2(-0.18, 0.38), Vector2(0.18, 0.38)]:
		b.box(S, "vcolor", c + r * q.x + f * q.y + UP * 0.05, Vector3(0.05, 0.1, 0.05))
	b.cur_color = Color.WHITE

## The customer service booth at the left front: an L counter, a glass upper wall, the
## red-lettered sign over it (video 2:22).
static func service(b, a, t, n, rng):
	var G = "wl10_fix"
	var into = -n
	# the back wall toward the hall
	K.lbox(b, G, "md_wall", P(a, t, n, 30.4, 0, 0.8), t, into, 0.0, 0.0, 0.0, UNIT - SIDE - 30.4, 2.6, 0.1)
	# the side counter facing the main aisle, glass above it, the sign over the glass
	var so = P(a, t, n, 31.0, 0, 0.9)
	K.lbox(b, G, "wl_laminate", so, into, -t, 0.0, 0.0, 0.0, 2.9, 1.05, 0.6, ["-y"])
	K.fq(b, G, "wl_counter", so, into, -t, 0.0, 2.9, 0.0, 1.05, 0.602, 0.0, 0.0, 1.0, 1.0)
	b.quad("glass", "glass", [P(a, t, n, 30.97, 1.1, 0.9), P(a, t, n, 30.97, 1.1, 3.8), P(a, t, n, 30.97, 2.5, 3.8), P(a, t, n, 30.97, 2.5, 0.9)], -t,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	K.lbox(b, G, "wl_alum", so, into, -t, 0.0, 2.5, -0.03, 2.9, 0.06, 0.06)
	K.lbox(b, G, "md_wall", so, into, -t, 0.0, 2.56, -0.05, 2.9, 0.9, 0.1)
	K.fq(b, G, "wl_signs", so, into, -t, 0.45, 2.45, 2.62, 3.42, 0.052, 0.0, 0.0, 0.5, 0.5)
	K.register(b, "wl10_small", K.L(so, into, -t, 1.2, 1.05, 0.12), into, -t)
	# the front counter facing into the store
	K.lbox(b, G, "wl_laminate", P(a, t, n, 30.4, 0, 3.8), t, into, 0.0, 0.0, 0.0, UNIT - SIDE - 30.4, 1.05, 0.6, ["-y"])
	K.fq(b, G, "wl_counter", P(a, t, n, UNIT - SIDE, 0, 3.8), -t, into, 0.0, UNIT - SIDE - 30.4, 0.0, 1.05, 0.602, 0.0, 0.0, 1.0, 1.0)
	K.ob(b, P(a, t, n, 30.4, 0, 0.8), P(a, t, n, UNIT - SIDE, 0, 4.4), 0.1)

# ------------------------------------------------------------------ materials
## "wl_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"red_panel":
			m.albedo_texture = b.tex("wl/red_panel.png"); m.roughness = 0.35; m.metallic_specular = 0.55
		"lightbox":
			m.albedo_texture = b.tex("wl/lightbox.png"); m.roughness = 0.4
			K.emit_tex(m, 1.1)
		"signs":
			m.albedo_texture = b.tex("wl/signs.png"); m.roughness = 0.5
			K.emit_tex(m, 0.25)
		"dept_band":
			m.albedo_texture = b.tex("wl/dept_band.png"); m.roughness = 0.5
			K.emit_tex(m, 0.2)
		"floor":
			m.albedo_texture = b.tex("wl/floor.png"); m.roughness = 0.12; m.metallic_specular = 0.7
		"rest_floor":
			m.albedo_texture = b.tex("wl/floor.png"); m.roughness = 0.3; m.metallic_specular = 0.5
			m.albedo_color = Color(0.78, 0.6, 0.46)
		"red":
			m.albedo_color = Color("#c4161f"); m.roughness = 0.2; m.metallic_specular = 0.6
		"alum":
			m.albedo_color = Color("#b8babd"); m.metallic = 0.6; m.roughness = 0.35
			K.emit(m, Color("#707276"), 0.2)
		"wood":
			m.albedo_texture = b.tex("wood_dark.png"); m.roughness = 0.5
			m.albedo_color = Color(1.5, 1.25, 1.0)
		"laminate":
			m.albedo_color = Color("#ecebe6"); m.roughness = 0.3; m.metallic_specular = 0.5
		"counter":
			m.albedo_texture = b.tex("wl/counter.png"); m.roughness = 0.35; m.metallic_specular = 0.45
		"lanes":
			m.albedo_texture = b.tex("wl/lanes.png")
			K.emit_tex(m, 1.2)
		"garments":
			m.albedo_texture = b.tex("wl/garments.png"); m.roughness = 0.9; m.metallic_specular = 0.1
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		"beige":
			m.albedo_color = Color("#d9c8a4"); m.roughness = 0.9
		"rest_ceiling":
			m.albedo_color = Color("#bfae8e"); m.roughness = 0.95
		"warm_disc":
			m.albedo_color = Color.WHITE
			K.emit(m, Color("#ffd9a0"), 3.0)
		"globe":
			m.albedo_color = Color("#fff0d0")
			K.emit(m, Color("#ffd49a"), 2.0)
		"slats":
			m.albedo_texture = b.tex("wl/slats.png"); m.roughness = 0.6
		"lattice":
			m.albedo_texture = b.tex("wl/lattice.png"); m.roughness = 0.8
		"food_photos":
			m.albedo_texture = b.tex("wl/food_photos.png"); m.roughness = 0.4; m.metallic_specular = 0.5
		"menu":
			m.albedo_texture = b.tex("wl/menu.png")
			K.emit_tex(m, 1.3)
		"rest_counter":
			m.albedo_texture = b.tex("wl/rest_counter.png"); m.roughness = 0.4
		"booth":
			m.albedo_texture = b.tex("wl/vinyl_booth.png"); m.roughness = 0.35; m.metallic_specular = 0.5
		"steel":
			m.albedo_color = Color("#c4c6c8"); m.metallic = 0.5; m.roughness = 0.3
			K.emit(m, Color("#606264"), 0.15)
		_:
			return false
	return true
