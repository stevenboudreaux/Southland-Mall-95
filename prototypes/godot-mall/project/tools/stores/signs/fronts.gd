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
		"K&B":
			kb(b, g, e, a, n, t, Ln, sd, U)
		"BLOCKBUSTER MUSIC":
			blockbuster(b, g, e, a, n, t, Ln, sd, U)
		"THE SHOE DEPT":
			shoe_dept(b, g, e, a, n, t, Ln, sd, U)
		"PAYLESS SHOES":
			payless(b, g, e, a, n, t, Ln, sd, U)
		"LADY FOOT LOCKER":
			lady_foot_locker(b, g, e, a, n, t, Ln, sd, U)
		"FOOTACTION USA":
			footaction(b, g, e, a, n, t, Ln, sd, U)

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

## K&B (Steven, Oct 7): the front of the K&B at Prien Lake Mall, Lake Charles (same owners;
## refs/kb-prien-lake-mall.png): a brown fascia with the round logo at each end and DRUGS,
## TOBACCO in lit letters between; display windows on a brick bulkhead, the doors, then glass
## to the floor. The logo from refs/kb-logo.jpg: purple face, gold rim, a red line, white K&B.
static func kb(b, g, e, a, n, t, Ln, sd, U):
	var G = "knbf_props"
	var LH = b.LANE_H
	var head = 3.0
	b.box(G, "sg_kb_fascia", P(a, t, n, U.call(Ln * 0.5), (head + LH) * 0.5, -0.12), b.abs_size(t, Ln, LH - head, 0.24, n), Transform3D.IDENTITY, ["+z", "-z"])
	b.quad(G, "sg_kb_fascia", [P(a, t, n, 0.0, head, -0.24), P(a, t, n, Ln, head, -0.24), P(a, t, n, Ln, head, 0.0), P(a, t, n, 0.0, head, 0.0)], Vector3.DOWN)
	for x in [0.15, Ln - 0.15]:
		b.box(G, "sg_kb_fascia", P(a, t, n, U.call(x), head * 0.5, -0.08), b.abs_size(t, 0.3, head, 0.16, n), Transform3D.IDENTITY, ["-y"])
	var w0 = 0.3
	var w1 = Ln * 0.48
	var d1 = w1 + 2.2
	var g1 = Ln - 0.3
	# display windows on a brick bulkhead
	b.box(G, "sg_kb_brick", P(a, t, n, U.call((w0 + w1) * 0.5), 0.45, -0.08), b.abs_size(t, w1 - w0, 0.9, 0.16, n))
	b.box(G, "sg_kb_alum", P(a, t, n, U.call((w0 + w1) * 0.5), 0.92, -0.09), b.abs_size(t, w1 - w0, 0.05, 0.18, n))
	_glass(b, a, t, n, U, w0, w1, 0.92, head)
	_mullions(b, G, a, t, n, U, w0, w1, 0.92, head, 6)
	# the doors: a pair of aluminium-framed glass leaves standing open, a transom over them
	_glass(b, a, t, n, U, w1, d1, 2.25, head)
	_mullions(b, G, a, t, n, U, w1, d1, 0.0, head, 1)
	b.box(G, "sg_kb_alum", P(a, t, n, U.call((w1 + d1) * 0.5), 2.22, -0.02), b.abs_size(t, d1 - w1, 0.07, 0.1, n))
	for s in [[w1 + 0.05, 1.0], [d1 - 0.05, -1.0]]:
		var hinge = P(a, t, n, U.call(s[0]), 0.0, 0.1)
		K.lbox(b, G, "sg_kb_alum", hinge, -n, t, 0.0, 0.0, 0.0, 1.0, 2.2, 0.05)
	# glass to the floor on the right
	b.box(G, "sg_kb_alum", P(a, t, n, U.call((d1 + g1) * 0.5), 0.05, -0.02), b.abs_size(t, g1 - d1, 0.1, 0.1, n))
	_glass(b, a, t, n, U, d1, g1, 0.1, head)
	_mullions(b, G, a, t, n, U, d1, g1, 0.0, head, 5)
	# the sign: logo, DRUGS, TOBACCO, logo, evenly spaced along the fascia
	var face = -0.24
	var wd = float(JSON.parse_string(FileAccess.get_file_as_string(S + "kb_drugs_logo.json")).width)
	var wt = float(JSON.parse_string(FileAccess.get_file_as_string(S + "kb_tobacco_logo.json")).width)
	var l0 = 0.35 + 0.65
	var l1 = Ln - 0.35 - 0.65
	var gap = (l1 - l0 - 1.3 - wd - wt) / 3.0
	var xd = l0 + 0.65 + gap + wd * 0.5
	var xt = xd + wd * 0.5 + gap + wt * 0.5
	for x in [l0, l1]:
		var c = P(a, t, n, U.call(x), 3.15, face)
		CH.build(b, "knbf_sign", S + "kb_disc_logo.json", c, n, "sg_kb_purple", "sg_kb_can", "", 0.02, 0.2, 0.0)
		CH.build(b, "knbf_sign", S + "kb_rim_logo.json", c, n, "sg_kb_gold", "sg_kb_can", "", 0.02, 0.235, 0.0)
		CH.build(b, "knbf_sign", S + "kb_line_logo.json", c, n, "sg_kb_red", "sg_kb_can", "", 0.02, 0.21, 0.0)
		CH.build(b, "knbf_sign", S + "kb_letters_logo.json", c, n, "sg_kb_white", "sg_kb_bevel", "sg_kb_bevel", 0.22, 0.03, 0.012)
	for wv in [[xd, "drugs"], [xt, "tobacco"]]:
		CH.build(b, "knbf_sign", S + "kb_%s_logo.json" % wv[1], P(a, t, n, U.call(wv[0]), 3.5, face), n, "sg_kb_letter", "sg_kb_return", "sg_kb_edge", 0.03, 0.1, 0.022, "sg_kb_glow_" + wv[1])
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.3, Ln - 0.3)

## Blockbuster Music (Steven, Oct 7: refs/blockbuster-music-*.jpg; the street fronts for the look):
## blue panelled fascia with the yellow-edged ticket and "music" lit magenta on a dark box, a lit
## white band under it, a glass front in dark frames with the doors open.
static func blockbuster(b, g, e, a, n, t, Ln, sd, U):
	var G = "bbmf_props"
	var LH = b.LANE_H
	var head = 2.78
	for x in [0.15, Ln - 0.15]:
		b.box(G, "sg_bb_pier", P(a, t, n, U.call(x), LH * 0.5, -0.1), b.abs_size(t, 0.3, LH, 0.2, n), Transform3D.IDENTITY, ["-y"])
	b.box(G, "sg_bb_panels", P(a, t, n, U.call(Ln * 0.5), (3.0 + LH) * 0.5, -0.1), b.abs_size(t, Ln - 0.6, LH - 3.0, 0.2, n))
	b.box(G, "sg_bb_band", P(a, t, n, U.call(Ln * 0.5), (head + 3.0) * 0.5, -0.11), b.abs_size(t, Ln - 0.6, 3.0 - head, 0.22, n))
	# the glass front, the doors in the middle standing open
	var d0 = Ln * 0.5 - 1.0
	var d1 = Ln * 0.5 + 1.0
	for seg in [[0.3, d0], [d1, Ln - 0.3]]:
		_glass(b, a, t, n, U, seg[0], seg[1], 0.15, head)
		_mullions(b, G, a, t, n, U, seg[0], seg[1], 0.0, head, 2, "sg_bb_frame")
		b.box(G, "sg_bb_frame", P(a, t, n, U.call((seg[0] + seg[1]) * 0.5), 0.075, -0.02), b.abs_size(t, seg[1] - seg[0], 0.15, 0.1, n))
	_glass(b, a, t, n, U, d0, d1, 2.25, head)
	_mullions(b, G, a, t, n, U, d0, d1, 0.0, head, 1, "sg_bb_frame")
	b.box(G, "sg_bb_frame", P(a, t, n, U.call(Ln * 0.5), 2.22, -0.02), b.abs_size(t, d1 - d0, 0.07, 0.1, n))
	for x in [d0 + 0.05, d1 - 0.05]:
		K.lbox(b, G, "sg_bb_frame", P(a, t, n, U.call(x), 0.0, 0.1), -n, t, 0.0, 0.0, 0.0, 0.95, 2.2, 0.05)
	# "music" on its dark box, right of centre; the ticket, tilted, at the upper left
	var mx = Ln - 2.0
	b.box(G, "sg_bb_box", P(a, t, n, U.call(mx), 3.81, -0.24), b.abs_size(t, 3.3, 1.56, 0.08, n))
	CH.build(b, "bbmf_sign", S + "bb_music_logo.json", P(a, t, n, U.call(mx), 3.1, -0.28), n, "sg_bb_music", "sg_bb_music_ret", "sg_bb_music_trim", 0.02, 0.08, 0.015, "sg_bb_glow")
	var tc = P(a, t, n, U.call(mx - 2.7), 3.88 - 0.52, -0.2)
	var r = deg_to_rad(10.0)
	CH.build(b, "bbmf_sign", S + "bb_ticket_rim_logo.json", tc, n, "sg_bb_yellow", "sg_bb_ticket_ret", "", 0.12, 0.05, 0.0, "", true, r)
	CH.build(b, "bbmf_sign", S + "bb_ticket_face_logo.json", tc, n, "sg_bb_blue", "sg_bb_ticket_ret", "", 0.12, 0.056, 0.0, "", true, r)
	CH.build(b, "bbmf_sign", S + "bb_ticket_frame_logo.json", tc, n, "sg_bb_yellow", "sg_bb_yellow", "", 0.12, 0.06, 0.0, "", true, r)
	CH.build(b, "bbmf_sign", S + "bb_ticket_text_logo.json", tc, n, "sg_bb_yellow", "sg_bb_ticket_ret", "", 0.12, 0.068, 0.0, "", true, r)
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.3, Ln - 0.3)

## The Shoe Dept (Steven, Oct 7: "that's like the exact facade"; refs/shoe-dept-*.jpg): a dark
## marble fascia and end piers, "the SHOE DEPT." in white lit letters, brass columns either side of
## the open entrance, display windows in brass frames.
static func shoe_dept(b, g, e, a, n, t, Ln, sd, U):
	var G = "sdf_props"
	var LH = b.LANE_H
	var head = 2.95
	b.box(G, "sg_sd_marble", P(a, t, n, U.call(Ln * 0.5), (head + LH) * 0.5, -0.08), b.abs_size(t, Ln, LH - head, 0.16, n))
	for x in [0.25, Ln - 0.25]:
		b.box(G, "sg_sd_marble", P(a, t, n, U.call(x), head * 0.5, -0.08), b.abs_size(t, 0.5, head, 0.16, n), Transform3D.IDENTITY, ["-y"])
	b.box(G, "sg_sd_brass", P(a, t, n, U.call(Ln * 0.5), head + 0.03, -0.17), b.abs_size(t, Ln - 1.0, 0.06, 0.02, n))
	var e0 = Ln * 0.5 - 1.85
	var e1 = Ln * 0.5 + 1.85
	for seg in [[0.5, e0 - 0.15], [e1 + 0.15, Ln - 0.5]]:
		b.box(G, "sg_sd_brass", P(a, t, n, U.call((seg[0] + seg[1]) * 0.5), 0.15, -0.04), b.abs_size(t, seg[1] - seg[0], 0.3, 0.1, n))
		_glass(b, a, t, n, U, seg[0], seg[1], 0.3, head)
		_mullions(b, G, a, t, n, U, seg[0], seg[1], 0.3, head, 2, "sg_sd_brass")
	for x in [e0, e1]:
		b.cyl(G, "sg_sd_brass", P(a, t, n, U.call(x), 0.0, -0.1), 0.13, 0.13, head, 24, false, false)
		K.ob(b, P(a, t, n, U.call(x) - 0.15, 0, -0.25), P(a, t, n, U.call(x) + 0.15, 0, 0.05), 0.05)
	CH.build(b, "sdf_sign", S + "sd_name_logo.json", P(a, t, n, U.call(Ln * 0.5), 3.48, -0.16), n, "sg_sd_white", "sg_sd_return", "sg_sd_trim", 0.03, 0.09, 0.01, "sg_sd_glow")
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.5, Ln - 0.5)

## Payless ShoeSource (Steven, Oct 7: design/storefronts/photos/payless): a black fascia box over
## a wide open front, cream piers at the ends, "Payless ShoeSource" in yellow lit letters with the
## two O's in orange.
static func payless(b, g, e, a, n, t, Ln, sd, U):
	var G = "payf_props"
	var LH = b.LANE_H
	var head = 2.9
	b.box(G, "sg_pay_black", P(a, t, n, U.call(Ln * 0.5), (head + LH) * 0.5, -0.15), b.abs_size(t, Ln - 0.8, LH - head, 0.3, n))
	b.quad(G, "sg_pay_soffit", [P(a, t, n, U.call(0.4), head, -0.3), P(a, t, n, U.call(Ln - 0.4), head, -0.3), P(a, t, n, U.call(Ln - 0.4), head, 0.0), P(a, t, n, U.call(0.4), head, 0.0)], Vector3.DOWN)
	for x in [0.2, Ln - 0.2]:
		b.box(G, "sg_pay_cream", P(a, t, n, U.call(x), LH * 0.5, -0.12), b.abs_size(t, 0.4, LH, 0.4, n), Transform3D.IDENTITY, ["-y"])
		K.ob(b, P(a, t, n, U.call(x - 0.2), 0, -0.32), P(a, t, n, U.call(x + 0.2), 0, 0.08), 0.05)
	var c = P(a, t, n, U.call(Ln * 0.5), 3.36, -0.3)
	CH.build(b, "payf_sign", S + "pay_name_logo.json", c, n, "sg_pay_yellow", "sg_pay_return", "", 0.02, 0.1, 0.0, "sg_pay_glow")
	CH.build(b, "payf_sign", S + "pay_dots_logo.json", c + UP * 0.0, n, "sg_pay_orange", "sg_pay_return", "", 0.02, 0.1, 0.0)
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.4, Ln - 0.4)

## Lady Foot Locker (Steven, Oct 7: design/storefronts/photos/lady-foot-locker): a white fascia box
## over the entrance with "Lady Foot Locker" in green raised letters, glass display windows either
## side, white slatwall within, dark piers at the ends.
static func lady_foot_locker(b, g, e, a, n, t, Ln, sd, U):
	var G = "lflf_props"
	var LH = b.LANE_H
	var head = 2.85
	b.box(G, "sg_lfl_white", P(a, t, n, U.call(Ln * 0.5), (head + LH) * 0.5, -0.06), b.abs_size(t, Ln, LH - head, 0.12, n))
	b.box(G, "sg_lfl_white", P(a, t, n, U.call(Ln * 0.5), head + 0.65, -0.32), b.abs_size(t, Ln - 0.6, 1.1, 0.4, n))
	for x in [0.12, Ln - 0.12]:
		b.box(G, "sg_lfl_dark", P(a, t, n, U.call(x), head * 0.5, -0.06), b.abs_size(t, 0.24, head, 0.16, n), Transform3D.IDENTITY, ["-y"])
	for seg in [[0.24, 1.6], [Ln - 1.6, Ln - 0.24]]:
		_glass(b, a, t, n, U, seg[0], seg[1], 0.25, head)
		_mullions(b, G, a, t, n, U, seg[0], seg[1], 0.0, head, 1, "sg_lfl_frame")
		b.box(G, "sg_lfl_frame", P(a, t, n, U.call((seg[0] + seg[1]) * 0.5), 0.125, -0.02), b.abs_size(t, seg[1] - seg[0], 0.25, 0.1, n))
	var nm = float(JSON.parse_string(FileAccess.get_file_as_string(S + "lfl_name_logo.json")).width)
	CH.build(b, "lflf_sign", S + "lfl_name_logo.json", P(a, t, n, U.call(Ln * 0.5), head + 0.45, -0.52), n, "sg_lfl_green", "sg_lfl_green_dark", "", 0.0, 0.05, 0.0)
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.24, Ln - 0.24)

## Footaction USA (Steven, Oct 7: design/storefronts/photos/footaction): a dark slate sign band
## over a wide open front, FOOTACTION in white lit letters with the bar and USA under them, the
## blue neon star at the right breaking over the band's edge; dark posts at the ends.
static func footaction(b, g, e, a, n, t, Ln, sd, U):
	var G = "faf_props"
	var LH = b.LANE_H
	var head = 2.85
	b.box(G, "sg_fa_dark", P(a, t, n, U.call(Ln * 0.5), (head + LH) * 0.5, -0.06), b.abs_size(t, Ln, LH - head, 0.12, n))
	b.box(G, "sg_fa_band", P(a, t, n, U.call(Ln * 0.5), head + 0.6, -0.27), b.abs_size(t, Ln - 0.5, 1.2, 0.3, n))
	b.box(G, "sg_fa_edge", P(a, t, n, U.call(Ln * 0.5), head + 0.02, -0.27), b.abs_size(t, Ln - 0.5, 0.04, 0.32, n))
	for x in [0.15, Ln - 0.15]:
		b.box(G, "sg_fa_post", P(a, t, n, U.call(x), head * 0.5, -0.1), b.abs_size(t, 0.3, head, 0.2, n), Transform3D.IDENTITY, ["-y"])
		K.ob(b, P(a, t, n, U.call(x - 0.15), 0, -0.2), P(a, t, n, U.call(x + 0.15), 0, 0.0), 0.05)
	var face = -0.42
	CH.build(b, "faf_sign", S + "fa_name_logo.json", P(a, t, n, U.call(Ln * 0.5 - 0.6), head + 0.25, face), n, "sg_fa_white", "sg_fa_return", "", 0.0, 0.04, 0.0, "sg_fa_glow")
	var sc = P(a, t, n, U.call(Ln * 0.5 + 2.35), head + 0.0, face)
	CH.build(b, "faf_sign", S + "fa_star_logo.json", sc, n, "sg_fa_blue", "sg_fa_return", "", 0.0, 0.05, 0.0, "sg_fa_star_glow")
	CH.build(b, "faf_sign", S + "fa_star_in_logo.json", sc, n, "sg_fa_white", "sg_fa_return", "", 0.0, 0.06, 0.0)
	_inside(b, g, e, a, n, t, Ln, sd, U, 0.3, Ln - 0.3)

static func _glass(b, a, t, n, U, x0, x1, y0, y1):
	b.quad("glass", "glass", [P(a, t, n, U.call(x0), y0, 0.0), P(a, t, n, U.call(x1), y0, 0.0), P(a, t, n, U.call(x1), y1, 0.0), P(a, t, n, U.call(x0), y1, 0.0)], n,
		[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)

static func _mullions(b, G, a, t, n, U, x0, x1, y0, y1, k, m = "sg_kb_alum"):
	for i in k + 1:
		var x = x0 + (x1 - x0) * i / k
		b.box(G, m, P(a, t, n, U.call(x), (y0 + y1) * 0.5, -0.02), b.abs_size(t, 0.06, y1 - y0, 0.1, n))
	b.box(G, m, P(a, t, n, U.call((x0 + x1) * 0.5), y1 - 0.04, -0.02), b.abs_size(t, x1 - x0, 0.08, 0.1, n))

## The mall's generic interior between x0..x1 (build_mall.gd interior()).
static func _inside(b, g, e, a, n, t, Ln, sd, U, x0, x1):
	var p0 = a + t * min(U.call(x0), U.call(x1))
	var p1 = a + t * max(U.call(x0), U.call(x1))
	var deep = b.clip_deep(a, a + t * Ln, n, clamp(float(e.depth), 3.0, 9.0))
	b.interior(g, e, a, n, t, Ln, sd, p0, p1, x1 - x0, deep)
