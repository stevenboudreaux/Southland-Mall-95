## Babbage's (store n39b), the video game shop by Corn Dog 7, built to
## design/storefronts/babbages.md.
##
## The front and the inside follow the 1997 Killeen Mall video Steven chose ("hands down
## the best"): a white fascia with fat rounded pink-red neon letters, a maroon column at
## each side of a wide open front, a white soffit with downlights just inside, dark grey
## carpet, white wall bays with radiused ends and lit header boxes, maroon columns, a white
## slatwall cash wrap with a yellow new-release board. The layout is Steven's: registers on
## the LEFT looking in, a shallow store, open floor, a few low rows of books, then the
## shelving that wraps round the back and both sides.
##
## Frame: u runs along the 6 m frontage from the edge's start a (x = -130, the viewer's
## right) to x = -124 (u = 6). d runs into the store (+z); d < 0 is the hall. The stall
## also takes a 2 m jog on the right (u -2..0) whose front stands 2 m back (d = 2); the
## room is 8 m deep (Corn Dog 7's dining room is behind it).

const K = preload("res://tools/stores/media/kit.gd")
const UNIT = 6.0
const JOG = 2.0          # the jog's width (u -2..0) and set-back (d 0..2)
const DEPTH = 8.0
const SIDE = 0.12
const HEAD = 2.75        # top of the opening = bottom of the fascia
const FTOP = 3.65
const PROUD = 0.30
const CEIL = 3.0
const SOFF = 2.62        # the perimeter soffit's underside
const HY = 2.25          # header boxes' bottom
const BAY = 1.22
const UP = Vector3.UP
const BOARDS = [0.45, 0.78, 1.11, 1.44, 1.77]

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	if Ln < 4.0:
		return   # the 2 m jog's edge: built with the main front below
	var rng = RandomNumberGenerator.new()
	rng.seed = 1997
	front(b, "bbf_props", a, t, n)
	room(b, "bb_shell", a, t, n)
	fixtures(b, a, t, n, rng)
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, (UNIT - JOG) * 0.5, CEIL * 0.5, DEPTH * 0.5)
	rp.size = Vector3(UNIT + JOG + 0.1, CEIL + 0.1, DEPTH + 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.6
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ the front
static func front(b, G, a, t, n):
	var LH = b.LANE_H
	var o = P(a, t, n, 0, 0, 0)
	# the mall wall over the fascia, white, with a return-air grille (video 19:50)
	b.quad(G, "md_fascia_white", [P(a, t, n, 0, FTOP, 0), P(a, t, n, UNIT, FTOP, 0), P(a, t, n, UNIT, LH, 0), P(a, t, n, 0, LH, 0)], n)
	b.cur_color = Color("#5a5a5e")
	K.lbox(b, G, "vcolor", o, t, n, 1.2, FTOP + 0.35, 0.0, 1.0, 0.3, 0.02)
	b.cur_color = Color.WHITE
	# the white fascia, standing out over the hall, its bottom edge rounded (video 20:04)
	K.lbox(b, G, "md_fascia_white", o, t, n, 0.0, HEAD + 0.12, 0.0, UNIT, FTOP - HEAD - 0.12, PROUD, ["-z", "-y"])
	var seg = 6
	for i in seg:
		var a0 = PI * 0.5 * i / seg
		var a1 = PI * 0.5 * (i + 1) / seg
		var c = Vector3(0, HEAD + 0.12, 0)
		var q0 = n * (PROUD - 0.12 + sin(a0) * 0.12) + Vector3(0, -cos(a0) * 0.12, 0)
		var q1 = n * (PROUD - 0.12 + sin(a1) * 0.12) + Vector3(0, -cos(a1) * 0.12, 0)
		var nn = (n * sin((a0 + a1) * 0.5) - UP * cos((a0 + a1) * 0.5)).normalized()
		b.quad(G, "md_fascia_white", [o + c + q0, o + t * UNIT + c + q0, o + t * UNIT + c + q1, o + c + q1], nn)
	b.quad(G, "md_fascia_white", [P(a, t, n, 0, HEAD, 0), P(a, t, n, UNIT, HEAD, 0), P(a, t, n, UNIT, HEAD, -(PROUD - 0.12)), P(a, t, n, 0, HEAD, -(PROUD - 0.12))], Vector3.DOWN)
	# "Babbage's": fat rounded pink-red neon channel letters
	K.letters(b, G, "md_neon_pink", "md_neon_pink_side", "res://tools/stores/media/bb_letters.json", P(a, t, n, UNIT, 0, 0), -t, n, UNIT * 0.5, HEAD + 0.24, PROUD, 0.09)
	# a maroon column at each side of the opening (video 20:04, 20:26)
	for u in [0.2, UNIT - 0.2]:
		K.column(b, G, "md_maroon", P(a, t, n, u, 0, 0.05), 0.2, HEAD + 0.12)
	K.ob_local(b, o, t, -n, 0.0, -0.2, 0.42, 0.3)
	K.ob_local(b, o, t, -n, UNIT - 0.42, -0.2, UNIT, 0.3)
	# the white soffit just inside, with downlights (video 20:04)
	b.quad(G, "md_fascia_white", [P(a, t, n, SIDE, HEAD, 0), P(a, t, n, UNIT - SIDE, HEAD, 0), P(a, t, n, UNIT - SIDE, HEAD, 1.0), P(a, t, n, SIDE, HEAD, 1.0)], Vector3.DOWN)
	b.quad(G, "md_fascia_white", [P(a, t, n, SIDE, HEAD, 1.0), P(a, t, n, UNIT - SIDE, HEAD, 1.0), P(a, t, n, UNIT - SIDE, CEIL, 1.0), P(a, t, n, SIDE, CEIL, 1.0)], -n)
	for u in [1.0, 3.0, 5.0]:
		var c = P(a, t, n, u, HEAD - 0.004, 0.5)
		b.cyl(G, "md_downlight", c, 0.09, 0.09, 0.004, 12, false, true)
	var l = b.add_spot(P(a, t, n, 3.0, HEAD - 0.1, 0.5), Vector3.DOWN, 1.2, 5.0, 70.0, Color(1.0, 0.95, 0.86))
	b.tag(l, "", 1.2, 1.2)
	# the jog on the right (u -2..0, front at d 2): the side return and a show window
	var jo = P(a, t, n, -JOG, 0, JOG)
	K.lbox(b, G, "md_fascia_white", jo, t, n, 0.0, HEAD + 0.12, 0.0, JOG, FTOP - HEAD - 0.12, 0.12, ["-z"])
	b.quad(G, "md_fascia_white", [P(a, t, n, -JOG, FTOP, JOG), P(a, t, n, 0, FTOP, JOG), P(a, t, n, 0, LH, JOG), P(a, t, n, -JOG, LH, JOG)], n)
	K.lbox(b, G, "md_fascia_white", jo, t, n, 0.0, 0.0, -0.1, JOG, 0.55, 0.1)
	b.quad("glass", "glass", [P(a, t, n, -JOG, 0.55, JOG - 0.02), P(a, t, n, 0, 0.55, JOG - 0.02), P(a, t, n, 0, HEAD + 0.12, JOG - 0.02), P(a, t, n, -JOG, HEAD + 0.12, JOG - 0.02)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
	b.cur_color = Color("#3a3a3e")
	K.lbox(b, G, "vcolor", jo, t, n, 0.0, 0.55, -0.03, 0.04, HEAD + 0.12 - 0.55, 0.06)
	b.cur_color = Color.WHITE
	# the return wall from the opening's column back to the window (outside face)
	b.quad(G, "md_fascia_white", [P(a, t, n, 0, 0, JOG), P(a, t, n, 0, 0, 0), P(a, t, n, 0, LH, 0), P(a, t, n, 0, LH, JOG)], -t)
	K.ob_local(b, jo, t, -n, 0.0, -0.1, JOG, 0.1, 0.15)

# ------------------------------------------------------------------ the room
static func room(b, G, a, t, n):
	var u0 = SIDE
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	var uj = -JOG + SIDE
	K.floor_rect(b, G, "md_carpet_grey", a, t, n, u0, u1, 0.0, dB)
	K.floor_rect(b, G, "md_carpet_grey", a, t, n, uj, u0, JOG + SIDE, dB)
	K.ceiling(b, G, a, t, n, u0, u1, 1.0, dB, CEIL, [1.6, 4.3], 2.0)
	K.ceiling(b, G, a, t, n, uj, u0, JOG + SIDE, dB, CEIL, [], 2.44, false)
	# walls
	K.wall(b, G, "md_wall", a, t, n, u1, dB, u1, 0.0, 0.0, CEIL, -t)              # left
	K.wall(b, G, "md_wall", a, t, n, u1, dB, uj, dB, 0.0, CEIL, n)                # back
	K.wall(b, G, "md_wall", a, t, n, uj, JOG + SIDE, uj, dB, 0.0, CEIL, t)        # right, behind the jog
	K.wall(b, G, "md_wall", a, t, n, u0, 0.0, u0, JOG + SIDE, 0.0, CEIL, t)       # right, by the opening
	K.wall(b, G, "md_wall", a, t, n, uj, JOG + SIDE, u0, JOG + SIDE, HEAD + 0.12, CEIL, -n)   # over the window, inside
	# the perimeter soffit over the wall bays with its maroon trim line (video 19:42)
	var sw = 0.45
	var runs = [[u1, 1.0, u1, dB, -t], [u1, dB, uj, dB, n], [uj, dB, uj, JOG + SIDE, t]]
	for r in runs:
		var pa = P(a, t, n, r[0], 0, r[1])
		var pb = P(a, t, n, r[2], 0, r[3])
		var f = r[4]
		b.quad(G, "md_fascia_white", [pa + UP * SOFF, pb + UP * SOFF, pb + f * sw + UP * SOFF, pa + f * sw + UP * SOFF], Vector3.DOWN)
		b.quad(G, "md_fascia_white", [pa + f * sw + UP * (SOFF + 0.05), pb + f * sw + UP * (SOFF + 0.05), pb + f * sw + UP * CEIL, pa + f * sw + UP * CEIL], f)
		b.quad(G, "md_maroon", [pa + f * sw + UP * SOFF, pb + f * sw + UP * SOFF, pb + f * sw + UP * (SOFF + 0.05), pa + f * sw + UP * (SOFF + 0.05)], f)

# ------------------------------------------------------------------ fixtures
static func fixtures(b, a, t, n, rng):
	var G = "bb_fix"
	var S = "bb_small"
	var u1 = UNIT - SIDE
	var dB = DEPTH - SIDE
	var uj = -JOG + SIDE
	var into = -n
	# -- the cash wrap on the left (Steven), slatwall behind it (video 0:22-6:32)
	var wo = P(a, t, n, u1, 0, 0.35)
	b.quad(G, "md_slatwall", [wo + UP * 0.0, wo + into * 4.0, wo + into * 4.0 + UP * 2.6, wo + UP * 2.6], -t,
		[Vector2(0, 2.6 / 0.6), Vector2(4.0 / 0.6, 2.6 / 0.6), Vector2(4.0 / 0.6, 0), Vector2(0, 0)])
	# game shelves on the slatwall, the release board, more shelves, a peg run of accessories
	K.bay(b, G, "bb_merch", P(a, t, n, u1, 0, 0.5), into, -t, 1.6, [0.95, 1.3, 1.65, 2.0], ["games"], rng, 0.26, "md_slatwall")
	K.fq(b, G, "md_release", P(a, t, n, u1, 0, 2.2), into, -t, 0.0, 0.8, 1.15, 2.15, 0.02)
	K.bay(b, G, "bb_merch", P(a, t, n, u1, 0, 3.1), into, -t, 1.2, [0.95, 1.3, 1.65, 2.0], ["games", "acc"], rng, 0.26, "md_slatwall")
	var co = P(a, t, n, 4.92, 0, 0.9)
	K.counter(b, G, S, co, into, -t, 2.6, "md_bb_counter", rng)
	# the orange crate of games on the counter (video 1:00)
	b.cur_color = Color("#c8642a")
	K.lbox(b, S, "vcolor_matte", co, into, -t, 1.5, 0.985, 0.08, 0.5, 0.2, 0.4, ["-y"])
	b.cur_color = Color.WHITE
	K.stock_row(b, S, co + into * 1.5, into, -t, 0.02, 0.48, 1.05, 0.2, 0.42, "games", rng)
	K.ob_local(b, P(a, t, n, u1, 0, 0.35), into, -t, 0.0, 0.0, 4.0, 0.9)
	# -- the demo kiosk at the left of the entrance (video 19:56): white pedestal, a TV
	var ko = P(a, t, n, 3.75, 0, 0.55)
	b.cur_color = Color("#f0efea")
	b.box(G, "vcolor", ko + Vector3(0, 0.5, 0), Vector3(0.6, 1.0, 0.6))
	b.cur_color = Color("#1c1c1e")
	b.box(G, "vcolor", ko + Vector3(0, 1.24, 0), Vector3(0.52, 0.46, 0.46))
	b.cur_color = Color.WHITE
	K.fq(b, G, "md_screens", ko, -t, n, -0.2, 0.2, 1.06, 1.38, 0.235, 0.0, 0.0, 0.5, 1.0)
	K.ob(b, ko - Vector3(0.3, 0, 0.3), ko + Vector3(0.3, 0, 0.3), 0.1)
	# -- the chrome stand with the red price poster in the opening (video 20:06)
	K.sign_stand(b, G, "md_bb_cards", P(a, t, n, 1.8, 0, 0.55), -t, n, 0)
	# hanging sale cards just inside (video 20:04)
	for s in [[1.4, 1], [2.9, 2], [4.4, 3]]:
		K.hang_card(b, G, "md_bb_cards", P(a, t, n, s[0], 0, 1.4), -t, n, 0.5, 0.5, 2.1, s[1], CEIL)
	# -- the wall bays that wrap the store: left wall past the counter, the back, the right
	var games = [["games"], ["games"], ["games", "pc"], ["pc"], ["acc", "games"], ["pc"]]
	K.bay_run(b, G, "bb_merch", P(a, t, n, u1, 0, 4.75), into, -t, BAY, 2, BOARDS, [["games"], ["games"]], [0, 1], "md_bb_headers", HY, rng)
	K.end_cap(b, G, "md_white", P(a, t, n, u1, 0, 4.75), into, -t, 0.36, PI, PI * 0.5, 0.0, 2.1)
	K.column(b, G, "md_maroon", P(a, t, n, u1 - 0.2, 0, dB - 0.2), 0.17, SOFF)
	# the back wall: six bays from the left corner to the right corner
	K.bay_run(b, G, "bb_merch", P(a, t, n, u1 - 0.42, 0, dB), -t, n, (UNIT + JOG - 2 * SIDE - 0.84) / 6.0, 6, BOARDS, [["games"], ["pc"], ["pc"], ["games"], ["games"], ["acc"]], [2, 3, 4, 5, 6, 7], "md_bb_headers", HY, rng)
	K.column(b, G, "md_maroon", P(a, t, n, uj + 0.2, 0, dB - 0.2), 0.17, SOFF)
	# the right wall behind the jog
	K.bay_run(b, G, "bb_merch", P(a, t, n, uj, 0, dB - 0.42), n, t, BAY, 3, BOARDS, [["games"], ["games", "pc"], ["games"]], [11, 8, 10], "md_bb_headers", HY, rng)
	K.end_cap(b, G, "md_white", P(a, t, n, uj, 0, dB - 0.42 - 3 * BAY), n, t, 0.36, 0.0, PI * 0.5, 0.0, 2.1)
	K.column(b, G, "md_maroon", P(a, t, n, uj + 0.2, 0, JOG + 0.55), 0.17, SOFF)
	# the right wall by the opening: one bay of PC boxes
	K.bay_run(b, G, "bb_merch", P(a, t, n, SIDE, 0, 1.95), n, t, BAY, 1, BOARDS, [["pc"]], [3], "md_bb_headers", HY, rng)
	# the show window's riser, inside the jog's glass
	var ro = P(a, t, n, uj, 0, JOG + SIDE)
	K.lbox(b, G, "md_white", ro, t, -n, 0.0, 0.0, 0.0, JOG - SIDE, 0.55, 0.5)
	K.stock_row(b, G, P(a, t, n, 0.0, 0, JOG + SIDE + 0.5), -t, n, 0.05, JOG - 0.2, 0.55, 0.3, 0.36, "pc", rng)
	K.ob_local(b, ro, t, -n, 0.0, 0.0, JOG - SIDE, 0.6)
	# -- the low rows of books (Steven): two short gondolas across the middle toward the back
	for d in [4.35, 5.85]:
		K.gondola(b, G, "bb_merch", P(a, t, n, 3.55, 0, d), -t, n, BAY, 2, [0.42, 0.8], ["books", "books"], rng, 0.28)
