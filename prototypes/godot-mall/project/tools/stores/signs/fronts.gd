## Storefronts rebuilt for their signs only (Steven's sign pass, Oct 7, 2026): the facade and
## sign in 3D from his photos, with the mall's generic interior left behind the opening until
## the store itself is built (interiors are on hold).
##   Foot Locker:      design/storefronts/refs/foot-locker-front.jpg (and foot-locker-2.jpg)
##   The Athlete's Foot: design/storefronts/refs/athletes-foot-front.jpg
## Specs: design/storefronts/foot-locker.md, athletes-foot.md.

const CH = preload("res://tools/stores/signs/channel.gd")
const K = preload("res://tools/stores/media/kit.gd")
const UP = Vector3.UP
const S = "res://tools/stores/signs/"

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	# x: metres from the viewer's left as they face the store; u: along the edge from a
	var rv = (-n).cross(UP)
	var flip = t.dot(rv) < 0.0
	var U = func(x): return Ln - x if flip else x
	match sd.name:
		"FOOT LOCKER":
			foot_locker(b, g, e, a, n, t, Ln, sd, U)
		"ATHLETE'S FOOT":
			athletes_foot(b, g, e, a, n, t, Ln, sd, U)

## Wood planks on the front plane between x0..x1, y0..y1 (1 m texture tiles); mirror swaps the slant.
static func wood(b, G, a, t, n, U, x0, x1, y0, y1, mirror):
	var u0 = U.call(x0)
	var u1 = U.call(x1)
	var p = [P(a, t, n, u0, y0, 0.0), P(a, t, n, u1, y0, 0.0), P(a, t, n, u1, y1, 0.0), P(a, t, n, u0, y1, 0.0)]
	var s = -1.0 if mirror else 1.0
	b.quad(G, "sg_fl_wood", p, n, [Vector2(x0 * s, -y0), Vector2(x1 * s, -y0), Vector2(x1 * s, -y1), Vector2(x0 * s, -y1)])

## Foot Locker (photos): diagonal wood over the whole front, the white portal with bevelled top
## corners, "foot Locker" in red letters edged in gold, the oval with the runner to its right.
static func foot_locker(b, g, e, a, n, t, Ln, sd, U):
	var G = "flf_props"
	var LH = b.LANE_H
	var mid = Ln * 0.5
	# wood: the strips beside the portal, a band over it slanting one way, the sign band the other
	wood(b, G, a, t, n, U, 0.0, mid - 2.8, 0.0, 3.3, false)
	wood(b, G, a, t, n, U, mid + 2.8, Ln, 0.0, 3.3, false)
	wood(b, G, a, t, n, U, 0.0, Ln, 3.3, 3.6, true)
	wood(b, G, a, t, n, U, 0.0, Ln, 3.6, LH, false)
	# the white portal, 22 cm deep
	CH.build(b, "flf_portal", S + "fl_portal_logo.json", P(a, t, n, U.call(mid), 0.0, 0.0), n, "sg_fl_white", "sg_fl_white", "", 0.0, 0.22, 0.0, "", false)
	for leg in [[mid - 2.8, mid - 2.4], [mid + 2.4, mid + 2.8]]:
		K.ob(b, P(a, t, n, U.call(leg[0]), 0, -0.22), P(a, t, n, U.call(leg[1]), 0, 0.0), 0.05)
	# the letters and the oval, centred on the sign band
	var tw = float(JSON.parse_string(FileAccess.get_file_as_string(S + "fl_logo.json")).width)
	var ow = float(JSON.parse_string(FileAccess.get_file_as_string(S + "fl_oval_logo.json")).width)
	var x0 = mid - (tw + 0.24 + ow) * 0.5
	CH.build(b, "flf_sign", S + "fl_logo.json", P(a, t, n, U.call(x0 + tw * 0.5), 3.8, 0.0), n, "sg_fl_face", "sg_fl_return", "sg_fl_gold", 0.03, 0.07, 0.022)
	var oc = x0 + tw + 0.24 + ow * 0.5
	CH.build(b, "flf_sign", S + "fl_oval_logo.json", P(a, t, n, U.call(oc), 3.78, 0.0), n, "sg_fl_cream", "sg_fl_black", "sg_fl_black", 0.03, 0.05, 0.028)
	CH.build(b, "flf_sign", S + "fl_fig_logo.json", P(a, t, n, U.call(oc), 3.78, 0.0), n, "sg_fl_black", "sg_fl_black", "", 0.084, 0.004, 0.0)
	# the generic interior behind the opening (interiors on hold)
	_inside(b, g, e, a, n, t, Ln, sd, U, mid - 2.4, mid + 2.4)

## The Athlete's Foot (photo): display windows either side of an open entrance between white
## piers, the black sign box over the entrance with the yellow pinstripe, "The Athlete's Foot"
## and the red winged foot, dark glass above the windows, a pale header.
static func athletes_foot(b, g, e, a, n, t, Ln, sd, U):
	var G = "aff_props"
	var LH = b.LANE_H
	var mid = Ln * 0.5
	var head = 3.85
	b.box(G, "sg_af_header", P(a, t, n, U.call(mid), (head + LH) * 0.5, -0.03), b.abs_size(t, Ln, LH - head, 0.06, n))
	for side in [[0.15, mid - 1.25], [mid + 1.25, Ln - 0.15]]:
		var s0 = side[0]
		var s1 = side[1]
		var cu = U.call((s0 + s1) * 0.5)
		var w = s1 - s0
		b.box(G, "sg_af_base", P(a, t, n, cu, 0.15, -0.04), b.abs_size(t, w, 0.3, 0.12, n))
		b.quad("glass", "glass", [P(a, t, n, U.call(s0), 0.3, 0.0), P(a, t, n, U.call(s1), 0.3, 0.0), P(a, t, n, U.call(s1), 3.2, 0.0), P(a, t, n, U.call(s0), 3.2, 0.0)], n,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)
		b.box(G, "sg_af_spandrel", P(a, t, n, cu, (3.2 + head) * 0.5, 0.0), b.abs_size(t, w, head - 3.2, 0.04, n))
		for x in [s0, (s0 + s1) * 0.5, s1]:
			b.box(G, "sg_af_frame", P(a, t, n, U.call(x), head * 0.5, -0.02), b.abs_size(t, 0.05, head, 0.08, n))
		b.box(G, "sg_af_frame", P(a, t, n, cu, 3.2, -0.02), b.abs_size(t, w, 0.05, 0.08, n))
	b.box(G, "sg_af_frame", P(a, t, n, U.call(0.075), head * 0.5, -0.02), b.abs_size(t, 0.15, head, 0.08, n))
	b.box(G, "sg_af_frame", P(a, t, n, U.call(Ln - 0.075), head * 0.5, -0.02), b.abs_size(t, 0.15, head, 0.08, n))
	# the white piers either side of the entrance
	for x in [mid - 1.1, mid + 1.1]:
		b.box(G, "sg_af_pier", P(a, t, n, U.call(x), head * 0.5, -0.1), b.abs_size(t, 0.3, head, 0.3, n), Transform3D.IDENTITY, ["-y"])
		K.ob(b, P(a, t, n, U.call(x - 0.15), 0, -0.25), P(a, t, n, U.call(x + 0.15), 0, 0.05), 0.05)
	# the sign box over the entrance, 3.1 x 1.05 m, 0.3 m deep
	var by = 2.8
	b.box(G, "sg_af_box", P(a, t, n, U.call(mid), by + 0.525, -0.17), b.abs_size(t, 3.1, 1.05, 0.34, n))
	var face = P(a, t, n, U.call(mid), by + 0.08, -0.34)
	CH.build(b, "aff_sign", S + "af_border_logo.json", face, n, "sg_af_yellow", "sg_af_return", "", 0.0, 0.008, 0.0)
	CH.build(b, "aff_sign", S + "af_text_logo.json", face, n, "sg_af_yellow", "sg_af_return", "", 0.0, 0.022, 0.0)
	CH.build(b, "aff_sign", S + "af_foot_logo.json", face, n, "sg_af_red", "sg_af_return", "", 0.0, 0.022, 0.0)
	CH.build(b, "aff_sign", S + "af_wing_logo.json", face, n, "sg_af_white", "sg_af_return", "", 0.0, 0.032, 0.0)
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.15, Ln - 0.15)

## The mall's generic interior between x0..x1 (build_mall.gd interior()).
static func _inside(b, g, e, a, n, t, Ln, sd, U, x0, x1):
	var p0 = a + t * min(U.call(x0), U.call(x1))
	var p1 = a + t * max(U.call(x0), U.call(x1))
	var deep = b.clip_deep(a, a + t * Ln, n, clamp(float(e.depth), 3.0, 9.0))
	b.interior(g, e, a, n, t, Ln, sd, p0, p1, x1 - x0, deep)
