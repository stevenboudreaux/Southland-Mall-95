## Channel letters: the 3D shop signs, built from a logo traced off a photo
## (tools/stores/signs/make_logos.py writes <id>_logo.json and tex/sg/<id>_face.png,
## <id>_glow.png).
##
## Each letter is a real can: a lit face set forward of the fascia, returns (the sides) in
## painted metal with smooth shading round the curves, and a thin trim cap edging the face.
## The face carries the logo's face texture (lamps inside: brighter along each stroke's middle),
## and a soft halo of the letters' colour lies on the fascia behind them.
##
## Materials are "sg_<key>" (build_mall.gd's mat() calls fill_mat).

const UP = Vector3.UP

## Builds the logo in `path` centred on c (the baseline's middle, on the fascia's face), facing nn.
## face/ret/trim: material names; standoff: gap behind the cans; depth: the cans' depth;
## trim_w: the trim cap's width; glow: material name for the halo ("" for none).
## roll: turns the logo in its own plane (radians, counter-clockwise as seen) about its frame's middle.
static func build(b, g, path, c, nn, face, ret, trim, standoff = 0.02, depth = 0.11, trim_w = 0.012, glow = "", dyn = true, roll = 0.0):
	var J = JSON.parse_string(FileAccess.get_file_as_string(path))
	var rv0 = (-nn).cross(UP)
	var rv = rv0 * cos(roll) + UP * sin(roll)
	var up = -rv0 * sin(roll) + UP * cos(roll)
	var wv = float(J.width)
	var hv = float(J.cap_h)
	var C0 = c + UP * (hv * 0.5)
	var X = func(p, d): return C0 + rv * (float(p.x) - wv * 0.5) + up * (float(p.y) - hv * 0.5) + nn * d
	var zf = standoff + depth
	var sf = b.st(g, face, dyn)
	var sr = b.st(g, ret, dyn)
	var stm = b.st(g, trim if trim != "" else ret, dyn)
	for Lt in J.letters:
		var tr = Lt.tris
		for i in range(0, tr.size(), 3):
			var q = [Vector2(tr[i][0], tr[i][1]), Vector2(tr[i + 1][0], tr[i + 1][1]), Vector2(tr[i + 2][0], tr[i + 2][1])]
			b.tri(sf, X.call(q[0], zf), X.call(q[1], zf), X.call(q[2], zf),
				Vector2(q[0].x / wv, 1.0 - q[0].y / hv), Vector2(q[1].x / wv, 1.0 - q[1].y / hv), Vector2(q[2].x / wv, 1.0 - q[2].y / hv), nn)
		for lp in Lt.loops:
			var pts = []
			for q in lp:
				pts.append(Vector2(float(q[0]), float(q[1])))
			_can_side(b, sr, stm, pts, X, rv, up, nn, standoff, zf, trim_w)
	if glow != "":
		var pad = float(J.get("glow_pad", 0.3))
		var x0 = C0 - rv * (wv * 0.5 + pad)
		var x1 = C0 + rv * (wv * 0.5 + pad)
		var hh = hv * 0.5 + pad
		b.quad(g + "_glow", glow, [x0 - up * hh + nn * 0.004, x1 - up * hh + nn * 0.004, x1 + up * hh + nn * 0.004, x0 + up * hh + nn * 0.004], nn,
			[Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)], true)

## One outline: the returns (smooth where the outline curves, creased at corners) and the trim
## cap, a flat band just inside the face's edge standing 4 mm proud, with a lip over the return.
static func _can_side(b, sr, stm, pts, X, rv, up, nn, z0, z1, tw):
	var n = pts.size()
	if n < 3:
		return
	# outward normal of each edge (outer loops run counter-clockwise, holes clockwise: the
	# material is always on the left, so outward is the right-hand normal)
	var en = []
	for i in n:
		var d = (pts[(i + 1) % n] - pts[i])
		if d.length() < 1e-6:
			en.append(Vector2.ZERO)
		else:
			d = d.normalized()
			en.append(Vector2(d.y, -d.x))
	var W3 = func(v2): return (rv * v2.x + up * v2.y).normalized()
	var lip = 0.004
	var top = z1 - 0.006 if tw > 0.0 else z1
	for i in n:
		var j = (i + 1) % n
		if en[i] == Vector2.ZERO:
			continue
		# smooth the normal into a neighbour when the turn is gentle (< 35 degrees)
		var ni = en[i]
		var nj = en[i]
		var prv = en[(i - 1 + n) % n]
		var nxt = en[j]
		if prv != Vector2.ZERO and prv.dot(en[i]) > 0.82:
			ni = (prv + en[i]).normalized()
		if nxt != Vector2.ZERO and nxt.dot(en[i]) > 0.82:
			nj = (nxt + en[i]).normalized()
		var p0 = X.call(pts[i], z0)
		var p1 = X.call(pts[j], z0)
		var p2 = X.call(pts[j], top)
		var p3 = X.call(pts[i], top)
		var u0 = 0.0
		var u1 = pts[i].distance_to(pts[j])
		var fn = W3.call(en[i])
		b._tri_n(sr, [p0, p1, p2], [W3.call(ni), W3.call(nj), W3.call(nj)], [Vector2(u0, 1), Vector2(u1, 1), Vector2(u1, 0)], fn)
		b._tri_n(sr, [p0, p2, p3], [W3.call(ni), W3.call(nj), W3.call(ni)], [Vector2(u0, 1), Vector2(u1, 0), Vector2(u0, 0)], fn)
		if tw <= 0.0:
			continue
		# the trim cap's lip: the last 6 mm of the return plus 4 mm proud of the face
		var q0 = X.call(pts[i], z1 - 0.006)
		var q1 = X.call(pts[j], z1 - 0.006)
		var q2 = X.call(pts[j], z1 + lip)
		var q3 = X.call(pts[i], z1 + lip)
		b._tri_n(stm, [q0, q1, q2], [W3.call(ni), W3.call(nj), W3.call(nj)], [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1)], fn)
		b._tri_n(stm, [q0, q2, q3], [W3.call(ni), W3.call(nj), W3.call(ni)], [Vector2(0, 0), Vector2(1, 1), Vector2(0, 1)], fn)
	if tw <= 0.0:
		return
	# the cap's flat band on the face, inset by tw (mitred, clamped at sharp corners)
	var inset = []
	for i in n:
		var a0 = en[(i - 1 + n) % n]
		var a1 = en[i]
		var m = a0 + a1
		if m.length() < 1e-4:
			m = a1
		m = m.normalized()
		var cosh = max(0.35, m.dot(a1 if a1 != Vector2.ZERO else m))
		inset.append(pts[i] - m * (tw / cosh))
	for i in n:
		var j = (i + 1) % n
		if en[i] == Vector2.ZERO:
			continue
		b.tri(stm, X.call(pts[i], z1 + lip), X.call(pts[j], z1 + lip), X.call(inset[j], z1 + lip), Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), nn)
		b.tri(stm, X.call(pts[i], z1 + lip), X.call(inset[j], z1 + lip), X.call(inset[i], z1 + lip), Vector2(0, 0), Vector2(1, 1), Vector2(0, 1), nn)
		# the band's inner edge drops back to the face
		b.tri(stm, X.call(inset[i], z1 + lip), X.call(inset[j], z1 + lip), X.call(inset[j], z1), Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), -W3.call(en[i]))
		b.tri(stm, X.call(inset[i], z1 + lip), X.call(inset[j], z1), X.call(inset[i], z1), Vector2(0, 0), Vector2(1, 1), Vector2(0, 1), -W3.call(en[i]))

## "sg_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		# Radio Shack: red acrylic faces lit from inside, dark returns, a darker red trim cap
		"rs_face":
			m.albedo_texture = b.tex("sg/rs_face.png"); m.albedo_color = Color("#d8141a"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff1208"); m.emission_energy_multiplier = 1.3
			m.set_meta("e_day", 1.1); m.set_meta("e_night", 1.5)
		"rs_trim":
			m.albedo_color = Color("#8e1218"); m.roughness = 0.35; m.metallic_specular = 0.6
			m.emission_enabled = true; m.emission = Color("#ff2a2e"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.3)
		"rs_return":
			m.albedo_color = Color("#1c1414"); m.roughness = 0.42; m.metallic = 0.35
		"rs_glow":
			_glow(m, b.tex("sg/rs_glow.png"), 0.55)
		"rs_pier":
			m.albedo_color = Color("#cfcbc3"); m.roughness = 0.7
		"rs_fascia":
			m.albedo_color = Color("#141313"); m.roughness = 0.55; m.metallic_specular = 0.45
		# Woolworth: orange-red faces, dark bronze returns and trim
		"wl_face":
			m.albedo_texture = b.tex("sg/wl_face.png"); m.albedo_color = Color("#dc2e16"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff2c10"); m.emission_energy_multiplier = 1.3
			m.set_meta("e_day", 1.1); m.set_meta("e_night", 1.5)
		"wl_trim":
			m.albedo_color = Color("#7a2416"); m.roughness = 0.35; m.metallic_specular = 0.6
			m.emission_enabled = true; m.emission = Color("#ff5a32"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.3)
		"wl_return":
			m.albedo_color = Color("#2a1712"); m.roughness = 0.45; m.metallic = 0.3
		"wl_glow":
			_glow(m, b.tex("sg/wl_glow.png"), 0.5)
		"wl_fascia":
			m.albedo_color = Color("#4a221d"); m.roughness = 0.5; m.metallic_specular = 0.5
		"wl_cream":
			m.albedo_color = Color("#e9dfcb"); m.roughness = 0.6
		# Foot Locker: red letters edged in gold on diagonal wood, a white portal, the oval runner
		"fl_face":
			# lit from behind a little (Steven, Oct 7: "a little bit of backlight ... not too much")
			m.albedo_color = Color("#b3141a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ff2018"); m.emission_energy_multiplier = 0.6
			m.set_meta("e_day", 0.4); m.set_meta("e_night", 0.75)
		"fl_gold":
			m.albedo_color = Color("#e0a845"); m.roughness = 0.3; m.metallic = 0.55
			m.emission_enabled = true; m.emission = Color("#ffc060"); m.emission_energy_multiplier = 0.15
			m.set_meta("e_day", 0.1); m.set_meta("e_night", 0.2)
		"fl_return":
			m.albedo_color = Color("#4a1210"); m.roughness = 0.5
		"fl_wood":
			m.albedo_texture = b.tex("sg/fl_wood.png"); m.roughness = 0.55; m.metallic_specular = 0.4
		"fl_white":
			m.albedo_color = Color("#efede7"); m.roughness = 0.45; m.metallic_specular = 0.5
		"fl_cream":
			m.albedo_color = Color("#e9e4d4"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#fff4dc"); m.emission_energy_multiplier = 0.15
			m.set_meta("e_day", 0.1); m.set_meta("e_night", 0.2)
		"fl_black":
			m.albedo_color = Color("#141212"); m.roughness = 0.45
		# The Athlete's Foot: a black sign box, yellow pinstripe and letters, the red winged foot
		"af_box":
			m.albedo_color = Color("#1d1513"); m.roughness = 0.4; m.metallic_specular = 0.5
		"af_yellow":
			m.albedo_color = Color("#f3cf1c"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ffd42a"); m.emission_energy_multiplier = 0.45
			m.set_meta("e_day", 0.35); m.set_meta("e_night", 0.6)
		"af_red":
			m.albedo_color = Color("#d8381c"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ff3a18"); m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.45)
		"af_white":
			m.albedo_color = Color("#f4f2ee"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ffffff"); m.emission_energy_multiplier = 0.2
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.3)
		"af_return":
			m.albedo_color = Color("#3a2c12"); m.roughness = 0.5
		"af_frame":
			m.albedo_color = Color("#e4e4e0"); m.roughness = 0.35; m.metallic = 0.3
		"af_pier":
			m.albedo_color = Color("#eeece6"); m.roughness = 0.6
		"af_base":
			m.albedo_color = Color("#aaa69e"); m.roughness = 0.5; m.metallic_specular = 0.5
		"af_spandrel":
			m.albedo_color = Color("#2a313b"); m.roughness = 0.12; m.metallic = 0.4
		"af_header":
			m.albedo_color = Color("#e8e5de"); m.roughness = 0.8
		# K&B: the round logo (purple face, gold rim, red line, white letters) and lit lettering
		"kb_fascia":
			m.albedo_color = Color("#6b4630"); m.roughness = 0.45; m.metallic_specular = 0.5
		"kb_brick":
			m.albedo_texture = b.tex("sg/kb_brick.png"); m.roughness = 0.85
			m.uv1_scale = Vector3(1.0, 1.0, 1.0)
		"kb_alum":
			m.albedo_color = Color("#c8c8c4"); m.metallic = 0.6; m.roughness = 0.3
		"kb_purple":
			m.albedo_color = Color("#8e4a9e"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#a860c0"); m.emission_energy_multiplier = 0.55
			m.set_meta("e_day", 0.4); m.set_meta("e_night", 0.7)
		"kb_gold":
			m.albedo_color = Color("#e6a91c"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#ffb21c"); m.emission_energy_multiplier = 0.4
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.5)
		"kb_red":
			m.albedo_color = Color("#c8301e"); m.roughness = 0.35
		"kb_white":
			m.albedo_color = Color("#f6f3f8"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#ffffff"); m.emission_energy_multiplier = 0.6
			m.set_meta("e_day", 0.45); m.set_meta("e_night", 0.8)
		"kb_bevel":
			m.albedo_color = Color("#d8cfe0"); m.roughness = 0.3
		"kb_can":
			m.albedo_color = Color("#26242a"); m.roughness = 0.45; m.metallic = 0.3
		"kb_letter":
			m.albedo_color = Color("#e9def4"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#e8d8ff"); m.emission_energy_multiplier = 0.7
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 0.9)
		"kb_edge":
			m.albedo_color = Color("#ffffff"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#ffffff"); m.emission_energy_multiplier = 1.4
			m.set_meta("e_day", 1.0); m.set_meta("e_night", 1.6)
		"kb_return":
			m.albedo_color = Color("#3a2448"); m.roughness = 0.5
		"kb_glow_drugs":
			_glow(m, b.tex("sg/kb_drugs_glow.png"), 0.35)
		"kb_glow_tobacco":
			_glow(m, b.tex("sg/kb_tobacco_glow.png"), 0.35)
		# Blockbuster Music
		"bb_panels":
			m.albedo_texture = b.tex("sg/bb_panels.png"); m.roughness = 0.35; m.metallic_specular = 0.6
		"bb_pier":
			m.albedo_color = Color("#2c2c32"); m.roughness = 0.5
		"bb_band":
			m.albedo_color = Color("#f4f4f2"); m.roughness = 0.4
			m.emission_enabled = true; m.emission = Color("#fffaf0"); m.emission_energy_multiplier = 1.2
			m.set_meta("e_day", 0.8); m.set_meta("e_night", 1.4)
		"bb_frame":
			m.albedo_color = Color("#2a2a2e"); m.roughness = 0.35; m.metallic = 0.4
		"bb_box":
			m.albedo_color = Color("#1e1026"); m.roughness = 0.4
		"bb_music":
			m.albedo_texture = b.tex("sg/bb_music_face.png"); m.albedo_color = Color("#d22aa8"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff3cc8"); m.emission_energy_multiplier = 1.3
			m.set_meta("e_day", 1.0); m.set_meta("e_night", 1.6)
		"bb_music_trim":
			m.albedo_color = Color("#7a1a66"); m.roughness = 0.35
		"bb_music_ret":
			m.albedo_color = Color("#2a0c26"); m.roughness = 0.5
		"bb_glow":
			_glow(m, b.tex("sg/bb_music_glow.png"), 0.45)
		"bb_yellow":
			m.albedo_color = Color("#ffc81a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ffcc22"); m.emission_energy_multiplier = 0.5
			m.set_meta("e_day", 0.35); m.set_meta("e_night", 0.65)
		"bb_blue":
			m.albedo_color = Color("#1e3fb4"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#2a50e0"); m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.25); m.set_meta("e_night", 0.45)
		"bb_ticket_ret":
			m.albedo_color = Color("#16163a"); m.roughness = 0.5
		# Zales
		"zl_stone":
			m.albedo_texture = b.tex("sg/zl_stone.png"); m.roughness = 0.75
		"zl_wood":
			m.albedo_texture = b.tex("wood_dark.png"); m.albedo_color = Color(1.35, 0.85, 0.7); m.roughness = 0.45
		"zl_white":
			m.albedo_texture = b.tex("sg/zl_name_face.png"); m.albedo_color = Color("#fbf8f2"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#fffaf0"); m.emission_energy_multiplier = 1.1
			m.set_meta("e_day", 0.8); m.set_meta("e_night", 1.3)
		"zl_return":
			m.albedo_color = Color("#3a2a20"); m.roughness = 0.45; m.metallic = 0.3
		"zl_glow":
			_glow(m, b.tex("sg/zl_name_glow.png"), 0.25)
		"zl_glow_sub":
			_glow(m, b.tex("sg/zl_sub_glow.png"), 0.25)
		# The Shoe Dept
		"sd_marble":
			m.albedo_texture = b.tex("sg/sd_marble.png"); m.roughness = 0.15; m.metallic_specular = 0.7
			m.uv1_scale = Vector3(0.5, 0.5, 1.0)
		"sd_brass":
			m.albedo_color = Color("#c9a24a"); m.metallic = 0.85; m.roughness = 0.2
		"sd_white":
			m.albedo_texture = b.tex("sg/sd_name_face.png"); m.albedo_color = Color("#fbfaf6"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#fffcf4"); m.emission_energy_multiplier = 1.1
			m.set_meta("e_day", 0.8); m.set_meta("e_night", 1.3)
		"sd_trim":
			m.albedo_color = Color("#d8d6d0"); m.roughness = 0.3
		"sd_return":
			m.albedo_color = Color("#2e2c2a"); m.roughness = 0.45; m.metallic = 0.3
		"sd_glow":
			_glow(m, b.tex("sg/sd_name_glow.png"), 0.3)
		# Payless
		"pay_black":
			m.albedo_color = Color("#151517"); m.roughness = 0.4; m.metallic_specular = 0.5
		"pay_soffit":
			m.albedo_color = Color("#f2efe6"); m.roughness = 0.6
		"pay_cream":
			m.albedo_color = Color("#e8dcbc"); m.roughness = 0.6
		"pay_yellow":
			m.albedo_texture = b.tex("sg/pay_name_face.png"); m.albedo_color = Color("#ffd51c"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ffd42a"); m.emission_energy_multiplier = 1.0
			m.set_meta("e_day", 0.7); m.set_meta("e_night", 1.2)
		"pay_orange":
			m.albedo_color = Color("#ff6a14"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#ff6a14"); m.emission_energy_multiplier = 0.9
			m.set_meta("e_day", 0.6); m.set_meta("e_night", 1.1)
		"pay_return":
			m.albedo_color = Color("#5a4a10"); m.roughness = 0.5
		"pay_glow":
			_glow(m, b.tex("sg/pay_name_glow.png"), 0.3)
		# Lady Foot Locker
		"lfl_white":
			m.albedo_color = Color("#f2f2ee"); m.roughness = 0.5
		"lfl_dark":
			m.albedo_color = Color("#2c2e32"); m.roughness = 0.4
		"lfl_frame":
			m.albedo_color = Color("#d8dbd8"); m.metallic = 0.4; m.roughness = 0.3
		"lfl_green":
			m.albedo_color = Color("#2fa83a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#3cc84a"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.15); m.set_meta("e_night", 0.35)
		"lfl_green_dark":
			m.albedo_color = Color("#1a6a22"); m.roughness = 0.4
		# 5-7-9
		"s579_silver":
			m.albedo_color = Color("#d6d6d8"); m.metallic = 0.7; m.roughness = 0.25
		"s579_red":
			m.albedo_color = Color("#a3163c"); m.roughness = 0.3; m.metallic_specular = 0.7
		"s579_red_dark":
			m.albedo_color = Color("#5a0a20"); m.roughness = 0.4
		# 5-7-9's pink front (Oct 7, photos/579/01, 04): polished steel, hot pink walls and risers
		"s579_steel":
			m.albedo_color = Color("#d4d6d8"); m.metallic = 0.85; m.roughness = 0.14; m.metallic_specular = 0.8
		"s579_pink":
			m.albedo_color = Color("#e0367e"); m.roughness = 0.45
		"s579_pinkwall":
			m.albedo_color = Color("#e8509a"); m.roughness = 0.6
		"s579_slat":
			m.albedo_texture = b.tex("gb/slat_white.png")
			m.albedo_color = Color("#f07ab2"); m.roughness = 0.55
		# Rave
		"rave_box":
			m.albedo_color = Color("#141414"); m.roughness = 0.35; m.metallic = 0.3
		"rave_glass":
			m.albedo_color = Color("#1c1e22"); m.roughness = 0.05; m.metallic_specular = 0.9
		"rave_pink":
			m.albedo_texture = b.tex("sg/rave_name_face.png"); m.albedo_color = Color("#ff86c0"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff7ab8"); m.emission_energy_multiplier = 1.0
			m.set_meta("e_day", 0.8); m.set_meta("e_night", 1.3)
		"rave_pink_dark":
			m.albedo_color = Color("#8a2a5a"); m.roughness = 0.4
		"rave_glow":
			_glow(m, b.tex("sg/rave_name_glow.png"), 0.35)
		# Gordon's
		"gor_frame":
			m.albedo_color = Color("#5a1e18"); m.roughness = 0.35; m.metallic_specular = 0.5
		"gor_lit":
			m.albedo_color = Color("#f2f4ec"); m.roughness = 0.4
			m.emission_enabled = true; m.emission = Color("#eef4e6"); m.emission_energy_multiplier = 1.0
			m.set_meta("e_day", 0.7); m.set_meta("e_night", 1.2)
		"gor_black":
			m.albedo_color = Color("#141414"); m.roughness = 0.4
		# Claire's
		"cla_box":
			m.albedo_color = Color("#ebe8e2"); m.roughness = 0.5
		"cla_black":
			m.albedo_color = Color("#1c1416"); m.roughness = 0.35; m.metallic_specular = 0.6
		"cla_red":
			m.albedo_color = Color("#d8202a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ff2030"); m.emission_energy_multiplier = 0.8
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 1.0)
		"cla_glow":
			_glow(m, b.tex("sg/cla_name_glow.png"), 0.5)
		# Coach House: cream, mahogany, white letters
		"ch_cream":
			m.albedo_color = Color("#e6dcc4"); m.roughness = 0.6
		"ch_cream_lt":
			m.albedo_color = Color("#f3ecdc"); m.roughness = 0.55
		"ch_trim":
			m.albedo_color = Color("#cdbb95"); m.roughness = 0.5
		"ch_mahogany":
			m.albedo_texture = b.tex("wood_dark.png"); m.albedo_color = Color(0.95, 0.62, 0.5); m.roughness = 0.35; m.metallic_specular = 0.6
		"ch_white":
			m.albedo_texture = b.tex("sg/ch_name_face.png"); m.albedo_color = Color("#ffffff"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#fffaf0"); m.emission_energy_multiplier = 0.7
			m.set_meta("e_day", 0.45); m.set_meta("e_night", 0.9)
		"ch_return":
			m.albedo_color = Color("#8a8478"); m.roughness = 0.45
		"ch_glow":
			_glow(m, b.tex("sg/ch_name_glow.png"), 0.15)
		# Footaction
		"fa_dark":
			m.albedo_color = Color("#2a2f33"); m.roughness = 0.5
		"fa_band":
			m.albedo_color = Color("#34413f"); m.roughness = 0.35; m.metallic_specular = 0.6
		"fa_edge":
			m.albedo_color = Color("#c8ccd0"); m.metallic = 0.6; m.roughness = 0.3
		"fa_post":
			m.albedo_color = Color("#23282e"); m.roughness = 0.4
		"fa_white":
			m.albedo_texture = b.tex("sg/fa_name_face.png"); m.albedo_color = Color("#ffffff"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#f4fbff"); m.emission_energy_multiplier = 1.2
			m.set_meta("e_day", 0.9); m.set_meta("e_night", 1.4)
		"fa_blue":
			m.albedo_color = Color("#3a8cff"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#3a8cff"); m.emission_energy_multiplier = 1.6
			m.set_meta("e_day", 1.2); m.set_meta("e_night", 2.0)
		"fa_return":
			m.albedo_color = Color("#20262c"); m.roughness = 0.5
		"fa_glow":
			_glow(m, b.tex("sg/fa_name_glow.png"), 0.3)
		"fa_star_glow":
			_glow(m, b.tex("sg/fa_star_glow.png"), 0.6)
		# Champs Sports
		"cs_fascia":
			m.albedo_color = Color("#e4e2dc"); m.roughness = 0.6
		"cs_steel":
			m.albedo_color = Color("#e2e4e6"); m.metallic = 0.8; m.roughness = 0.18; m.metallic_specular = 0.8
		"cs_blue":
			m.albedo_color = Color("#23328a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#2a3ca8"); m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.2); m.set_meta("e_night", 0.4)
		"cs_red":
			m.albedo_color = Color("#c4202c"); m.roughness = 0.35
		"cs_navy":
			m.albedo_color = Color("#1c2470"); m.roughness = 0.4
		"cs_cream":
			m.albedo_texture = b.tex("sg/cs_name_face.png"); m.albedo_color = Color("#fff2dc"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#fff0d8"); m.emission_energy_multiplier = 0.9
			m.set_meta("e_day", 0.6); m.set_meta("e_night", 1.1)
		"cs_glow":
			_glow(m, b.tex("sg/cs_name_glow.png"), 0.2)
		# Sports Avenue
		"sa_bulbs":
			m.albedo_texture = b.tex("sg/sa_bulbs.png"); m.roughness = 0.4
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.WHITE
			m.emission_energy_multiplier = 0.7
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 0.9)
		"sa_red":
			m.albedo_color = Color("#c8141a"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#ff1a12"); m.emission_energy_multiplier = 0.35
			m.set_meta("e_day", 0.2); m.set_meta("e_night", 0.5)
		# Cucos (Oct 7): brick-red script, neon tubes round each letter, the blue MEXICAN CAFE band
		"cu_face":
			m.albedo_texture = b.tex("sg/cu_name_face.png"); m.albedo_color = Color("#a8361e"); m.roughness = 0.4
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff4a22"); m.emission_energy_multiplier = 0.3
			m.set_meta("e_day", 0.2); m.set_meta("e_night", 0.4)
		"cu_return":
			m.albedo_color = Color("#3a1410"); m.roughness = 0.5
		"cu_neon":
			m.albedo_color = Color("#ff7a52"); m.roughness = 0.2
			m.emission_enabled = true; m.emission = Color("#ff5a2e"); m.emission_energy_multiplier = 2.2
			m.set_meta("e_day", 1.0); m.set_meta("e_night", 1.7)
		"cu_glow":
			_glow(m, b.tex("sg/cu_name_glow.png"), 0.35)
		"cu_band":
			# lit a little from inside, so the blue still reads at night
			m.albedo_color = Color("#34488f"); m.roughness = 0.35; m.metallic_specular = 0.6
			m.emission_enabled = true; m.emission = Color("#3a56c8"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.1); m.set_meta("e_night", 0.3)
		"cu_white_trim":
			m.albedo_color = Color("#e8ecf4"); m.roughness = 0.3
		"cu_white":
			m.albedo_texture = b.tex("sg/cu_sub_face.png"); m.albedo_color = Color("#ffffff"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#f4f8ff"); m.emission_energy_multiplier = 1.0
			m.set_meta("e_day", 0.7); m.set_meta("e_night", 1.2)
		"cu_sub_glow":
			_glow(m, b.tex("sg/cu_sub_glow.png"), 0.2)
		# Cucos, the neon channel sign (Oct 7, tools/stores/signs/cucos_sign.gd): black cans painted
		# brick red inside, red neon on standoffs, the blue cabinet with white neon. Lit a little:
		# the tubes glow without washing out the cans.
		"cu2_black":
			m.albedo_color = Color("#15120f"); m.roughness = 0.5; m.metallic = 0.25
		"cu2_red":
			m.albedo_color = Color("#a22a1c"); m.roughness = 0.55
			m.emission_enabled = true; m.emission = Color("#e0341c"); m.emission_energy_multiplier = 0.5
			m.set_meta("e_day", 0.3); m.set_meta("e_night", 0.5)
		"cu2_tube":
			m.albedo_color = Color("#ff9a88"); m.roughness = 0.15
			m.emission_enabled = true; m.emission = Color("#ff3c22"); m.emission_energy_multiplier = 1.9
			m.set_meta("e_day", 1.4); m.set_meta("e_night", 1.9)
		"cu2_boot":
			m.albedo_color = Color("#0b0b0b"); m.roughness = 0.7
		"cu2_post":
			m.albedo_color = Color("#d9dad4"); m.roughness = 0.2; m.metallic_specular = 0.7
			m.emission_enabled = true; m.emission = Color("#ff6a48"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.1); m.set_meta("e_night", 0.25)
		"cu2_blue":
			m.albedo_color = Color("#4c58a8"); m.roughness = 0.4; m.metallic_specular = 0.5
			m.emission_enabled = true; m.emission = Color("#5562cc"); m.emission_energy_multiplier = 0.5
			m.set_meta("e_day", 0.32); m.set_meta("e_night", 0.5)
		"cu2_white":
			m.albedo_color = Color("#eef0f4"); m.roughness = 0.35
			m.emission_enabled = true; m.emission = Color("#eef2ff"); m.emission_energy_multiplier = 0.8
			m.set_meta("e_day", 0.5); m.set_meta("e_night", 0.8)
		"cu2_wtube":
			m.albedo_color = Color("#ffffff"); m.roughness = 0.15
			m.emission_enabled = true; m.emission = Color("#eaf2ff"); m.emission_energy_multiplier = 1.8
			m.set_meta("e_day", 1.3); m.set_meta("e_night", 1.8)
		"cu2_pool":
			# light added over what is behind it: the colour is in the vertices
			m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			m.vertex_color_use_as_albedo = true
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		# Karmelkorn, the neon channel sign on both fronts (Oct 7, tools/stores/signs/kk_sign.gd):
		# deep red returns, a cream trim cap, red inside, red neon outlines. Lit a little.
		"kk2_return":
			m.albedo_color = Color("#5c0c0e"); m.roughness = 0.45; m.metallic = 0.2
		"kk2_rim":
			m.albedo_color = Color("#eedcb4"); m.roughness = 0.35; m.metallic_specular = 0.6
		"kk2_red":
			m.albedo_color = Color("#b8281c"); m.roughness = 0.55
			m.emission_enabled = true; m.emission = Color("#ee4424"); m.emission_energy_multiplier = 0.75
			m.set_meta("e_day", 0.4); m.set_meta("e_night", 0.75)
		"kk2_tube":
			m.albedo_color = Color("#ffd2bc"); m.roughness = 0.15
			m.emission_enabled = true; m.emission = Color("#ff6440"); m.emission_energy_multiplier = 1.9
			m.set_meta("e_day", 1.4); m.set_meta("e_night", 1.9)
		"kk2_boot":
			m.albedo_color = Color("#0b0b0b"); m.roughness = 0.7
		"kk2_post":
			m.albedo_color = Color("#d9dad4"); m.roughness = 0.2; m.metallic_specular = 0.7
			m.emission_enabled = true; m.emission = Color("#ff6a48"); m.emission_energy_multiplier = 0.25
			m.set_meta("e_day", 0.1); m.set_meta("e_night", 0.25)
		"kk2_pool":
			m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			m.vertex_color_use_as_albedo = true
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
			m.cull_mode = BaseMaterial3D.CULL_DISABLED
		# Great American Cookie Co. (Oct 7): red neon script, white lit capitals, a black fascia
		"gac_neon":
			m.albedo_texture = b.tex("sg/gac_script_face.png"); m.albedo_color = Color("#ff3a2a"); m.roughness = 0.25
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#ff2a1e"); m.emission_energy_multiplier = 2.0
			m.set_meta("e_day", 1.4); m.set_meta("e_night", 2.4)
		"gac_neon_ret":
			m.albedo_color = Color("#5a0e0a"); m.roughness = 0.4
		"gac_glow":
			_glow(m, b.tex("sg/gac_script_glow.png"), 0.6)
		"gac_white":
			m.albedo_texture = b.tex("sg/gac_name_face.png"); m.albedo_color = Color("#fffdf6"); m.roughness = 0.3
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color("#fffaf0"); m.emission_energy_multiplier = 1.2
			m.set_meta("e_day", 0.8); m.set_meta("e_night", 1.4)
		"gac_white_ret":
			m.albedo_color = Color("#2a2a2c"); m.roughness = 0.4; m.metallic = 0.3
		"gac_name_glow":
			_glow(m, b.tex("sg/gac_name_glow.png"), 0.3)
		"gac_black":
			m.albedo_color = Color("#141214"); m.roughness = 0.4; m.metallic_specular = 0.5
		"gac_check":
			m.albedo_texture = b.tex("sg/gac_check.png"); m.roughness = 0.4
			m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		# Foot Locker's backlight (Oct 7): a soft red halo behind the letters
		"fl_glow":
			_glow(m, b.tex("sg/fl_glow.png"), 0.28)
		# placeholders from the 8-bit game (Steven, Oct 7): the hand-drawn panels, crisp pixels, lit
		"ph_felgers", "ph_tgmc":
			m.albedo_texture = b.tex("sg/%s_8bit.png" % ("felgers" if key == "ph_felgers" else "tgmc"))
			m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
			m.roughness = 0.5
			m.emission_enabled = true; m.emission_texture = m.albedo_texture; m.emission = Color.WHITE
			m.emission_energy_multiplier = 0.12
			m.set_meta("e_day", 0.05); m.set_meta("e_night", 0.2)
		"sa_board":
			m.albedo_color = Color("#0c0c0e"); m.roughness = 0.6
		"sa_grid":
			m.albedo_color = Color("#202024"); m.roughness = 0.5
		"sa_lamp_white":
			m.albedo_color = Color("#f6f4ea"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#fff6e4"); m.emission_energy_multiplier = 0.9
			m.set_meta("e_day", 0.6); m.set_meta("e_night", 1.2)
		"sa_lamp_red":
			m.albedo_color = Color("#d0201c"); m.roughness = 0.3
			m.emission_enabled = true; m.emission = Color("#ff2a1e"); m.emission_energy_multiplier = 0.9
			m.set_meta("e_day", 0.6); m.set_meta("e_night", 1.2)
		"sa_white":
			m.albedo_color = Color("#f4f4f0"); m.roughness = 0.4
		"sa_glow":
			_glow(m, b.tex("sg/sa_name_glow.png"), 0.1)
		_:
			return false
	return true

## The halo: unshaded, added over the fascia, no shadow, not in the bake.
static func _glow(m, tx, e):
	m.albedo_texture = tx
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_color = Color(e, e, e, 1.0)
	m.no_depth_test = false
	m.cull_mode = BaseMaterial3D.CULL_BACK
