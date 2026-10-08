## Gold 'n' Gifts Unlimited (n39) on the corner's 45-degree front between Babbage's and the
## JCPenney court (Steven, Oct 8 2026: the 1994 directory's unit 82 on the diagonal; his marked-up
## screenshot's straight line from Babbage's pier to the court column). Before, the corner was a
## staircase of 2 m steps with this shop on two of them.
##
## The front is the mall's generic one along the diagonal: stone-based cream piers, the cream
## bulkhead with the dark sign box and the gold serif name, bronze-framed glass with an open
## doorway in the middle. Inside (guessed, as before): a small dim gift and gold shop on the
## five-sided plan behind the diagonal (Babbage's wall at x = -130, Corn Dog 7's at z = 68, the
## court's return at x = -136), taupe walls and carpet, glass jewel cases round the walls.
##
## Frame: P(a, t, n, u, y, d) = a + t u - n d + y up; a = (-136, 66), t runs north-east to
## (-130, 60), n faces the hall (north-west).

const K = preload("res://tools/stores/media/kit.gd")
const S2 = preload("res://tools/stores/small/store2.gd")
const UP = Vector3.UP
const X0 = -136.0       # the plan: x -136..-130, z 60..68, cut by the diagonal x + z = -70
const X1 = -130.0
const Z1 = 68.0
const CEIL = 3.2

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, b_, n, t, Ln, sd):
	front(b, g, a, t, n, Ln, sd)
	room(b, a, t, n, Ln)
	# obstacles just inside the glass: the walk grid's tiles along the diagonal are half shop
	var k = 0.25
	while k < Ln - 0.1:
		var p = P(a, t, n, k, 0, 0.22)
		b.obst([p.x, p.z, 0.22])
		k += 0.35

static func front(b, g, a, t, n, Ln, sd):
	# boxes are laid out in the diagonal's own frame (K.lbox: x along t, z out along n), not with
	# abs_size, which only suits fronts square to the axes
	var OPEN_H = b.OPEN_H
	var LH = b.LANE_H
	var pil = 0.4
	for ee in [0.0, Ln - pil]:
		K.lbox(b, g, "stone", a, t, n, ee, 0.0, 0.0, pil, 0.9, 0.12)
		K.lbox(b, g, "cream", a, t, n, ee, 0.9, 0.0, pil, OPEN_H - 0.9, 0.06)
	K.lbox(b, g, "bulkhead", a, t, n, 0.0, OPEN_H, 0.0, Ln, LH - OPEN_H, 0.16)
	# the sign: the dark box with the gold serif name, as before
	var sw = 5.2
	var sh = 0.78
	var sy = OPEN_H + (LH - OPEN_H) * 0.5
	b.cur_color = Color(sd.bg)
	K.lbox(b, g, "vcolor", a, t, n, (Ln - sw) * 0.5, sy - sh * 0.5, 0.16, sw, sh, 0.08)
	b.cur_color = Color.WHITE
	b.label(sd.sign, sd.font, sd.fg, a + t * (Ln * 0.5) + n * 0.25 + Vector3(0, sy, 0), n, sw * 0.88, 0.56)
	# glass either side of the open doorway, bronze mullions, the head bar
	var inner0 = pil
	var inner1 = Ln - pil
	var d0 = Ln * 0.5 - 1.2
	var d1 = Ln * 0.5 + 1.2
	for seg in [[inner0, d0], [d1, inner1]]:
		var s0 = seg[0]
		var s1 = seg[1]
		K.lbox(b, g, "stone", a, t, n, s0, 0.0, -0.1, s1 - s0, 0.4, 0.2)
		b.quad("glass", "glass", [a + t * s0 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, 0.4, 0), a + t * s1 + Vector3(0, OPEN_H, 0), a + t * s0 + Vector3(0, OPEN_H, 0)], n,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
		var cnt = max(1, int(round((s1 - s0) / 1.5)))
		for k in cnt + 1:
			var u = s0 + (s1 - s0) * k / cnt
			K.lbox(b, g, "bronze", a, t, n, u - 0.03, 0.4, -0.05, 0.06, OPEN_H - 0.4, 0.1)
	K.lbox(b, g, "bronze", a, t, n, inner0, OPEN_H - 0.08, -0.06, inner1 - inner0, 0.08, 0.12)
	# the shop's light spilling into the hall at night
	var spill_at = a + t * (Ln * 0.5) - n * 0.4 + Vector3(0, OPEN_H - 0.15, 0)
	b.tag(b.add_spot(spill_at, n * 0.9 + Vector3.DOWN * 1.0, 1.6, 7.0, 55.0, Color("#FFF1DC")), "night")

## The five-sided room behind the diagonal.
static func room(b, a, t, n, Ln):
	var G = "ggs_shell"
	var F = "ggs_fix"
	var dg = func(v): return Vector3(v.x, 0, v.y)
	# plan corners, counter-clockwise seen from above
	var pts = [Vector2(X1, 60.0), Vector2(X1, Z1), Vector2(X0, Z1), Vector2(X0, 66.0)]
	var s_f = b.st(G, "w7_taupe_carpet")
	var s_c = b.st(G, "kb_ceiling")
	for i in [1, 2]:
		var p0 = dg.call(pts[0]); var p1 = dg.call(pts[i]); var p2 = dg.call(pts[i + 1])
		b.tri(s_f, p0 + UP * 0.005, p1 + UP * 0.005, p2 + UP * 0.005, Vector2(p0.x, p0.z), Vector2(p1.x, p1.z), Vector2(p2.x, p2.z), UP)
		b.tri(s_c, p0 + UP * CEIL, p1 + UP * CEIL, p2 + UP * CEIL, Vector2(p0.x, p0.z) * 0.5, Vector2(p1.x, p1.z) * 0.5, Vector2(p2.x, p2.z) * 0.5, Vector3.DOWN)
	# walls: Babbage's side (x = -130, facing west), the back (z = 68, facing north), the court
	# return (x = -136, z 66..68, facing east)
	var walls = [[Vector3(X1, 0, 60.0), Vector3(X1, 0, Z1), Vector3(-1, 0, 0)],
		[Vector3(X1, 0, Z1), Vector3(X0, 0, Z1), Vector3(0, 0, -1)],
		[Vector3(X0, 0, Z1), Vector3(X0, 0, 66.0), Vector3(1, 0, 0)]]
	for w in walls:
		b.quad(G, "w7_taupe", [w[0], w[1], w[1] + UP * CEIL, w[0] + UP * CEIL], w[2])
		b.box(G, "md_white", (w[0] + w[1]) * 0.5 + UP * 0.05 + w[2] * 0.01, b.abs_size((w[1] - w[0]).normalized(), w[0].distance_to(w[1]), 0.1, 0.02, w[2]))
	# lay-in light panels
	for c in [Vector3(-132.5, CEIL - 0.01, 64.6), Vector3(-131.2, CEIL - 0.01, 66.6), Vector3(-134.2, CEIL - 0.01, 66.9)]:
		b.quad(G, "int_panel", [c + Vector3(-0.6, 0, -0.3), c + Vector3(0.6, 0, -0.3), c + Vector3(0.6, 0, 0.3), c + Vector3(-0.6, 0, 0.3)], Vector3.DOWN)
	# glass jewel cases round the walls, gold and gifts on glass shelves over them
	S2.jewel_case(b, F, Vector3(X1 - 0.12, 0, 62.4), Vector3(0, 0, 1), Vector3(-1, 0, 0), 5.3)
	S2.jewel_case(b, F, Vector3(X1 - 0.8, 0, Z1 - 0.12), Vector3(-1, 0, 0), Vector3(0, 0, -1), 4.4)
	for k in 3:
		var y = 1.45 + k * 0.38
		K.lbox(b, F, "md_white", Vector3(X1 - 0.12, 0, 62.4), Vector3(0, 0, 1), Vector3(-1, 0, 0), 0.0, y, 0.0, 5.3, 0.02, 0.3)
		K.lbox(b, F, "md_white", Vector3(X1 - 0.8, 0, Z1 - 0.12), Vector3(-1, 0, 0), Vector3(0, 0, -1), 0.0, y, 0.0, 4.4, 0.02, 0.3)
	# a centre case on the diagonal's axis, facing the door
	var cc = P(a, t, n, Ln * 0.5 - 0.9, 0, 2.6)
	S2.jewel_case(b, F, cc, t, -n, 1.8)
	var l = b.add_omni(Vector3(-132.6, 2.7, 65.4), 0.45, 6.0, Color(1.0, 0.94, 0.84))
	b.tag(l, "", 0.45, 1.0)
