## games, inc. (2026, store s52: the old Blockbuster Music box, 8 x 40 m, on the Concourse's
## south side next to the vacant Pocket Change unit). Built from Steven's Oct 23 2026 footage:
## IMG_4443 (the front, then the whole depth), IMG_4444 and photo IMG_4445 (the air hockey end).
##
## What the footage shows (notes: claude/session-handoff-2026-10-23-site-visit-analysis.md,
## batch B): a mustard 6x12 tile portal with two display windows full of Pokémon plush, lit
## green "games, inc." letters with the alien on a white panel; inside a bright long room:
## wood-look plank floor, white slatwall with a red-orange upper band and a mustard stripe,
## white 2x2 lay-in ceiling with parabolic troffers and track spots, one white pipe column
## mid-store and a thin black one further back. Walking in: left, a party corner (white folding
## tables and benches under a navy "games, inc. CLAW MANIA" wall), then the orange "GALACTIC
## PRIZE PORTAL" counter with lit glass showcases and a plush wall behind; right, a long row of
## white LED-framed claw machines; down the middle, dome ticket games, coin pushers and a wheel
## game, then two air hockey tables, kiddie rides and big ticket games at the back.
##
## The machines are Pocket Change's prop modules (tools/stores/pocket_change/README.md): their
## 1990s cabinets stand in for the 2026 ones until each kind is painted from the frames (the
## claws are the closest match; the "cyclone" dome stands in for the dome drop games).
## Textures: paint.py -> tex/gi/*.png. Materials "gi_<key>" via fill_mat().
##
## Frame: u runs along the frontage from the edge's start `a` (the hall viewer's right) to 8;
## d runs into the store; y is up. P() as in pocket_change/store.gd.

const UNIT = 8.0
const DEPTH = 40.0
const ROOM_D = 39.0         # the back wall
const SIDE = 0.12           # party walls' inner faces
const WALL_T = 0.45         # the front wall's thickness (the tile returns run back through it)
const CEIL = 3.4            # white lay-in ceiling (IMG_4443 f024: ~3.4 m)
const O0 = 2.1              # the opening, u
const O1 = 5.9
const HEAD = 2.75           # top of the opening
const PANEL_Y1 = 3.9        # top of the white sign panel
const BAND_Y0 = 2.45        # the orange band's bottom (slatwall below it)
const PC = "res://tools/stores/pocket_change/%s.gd"

static func P(a, t, n, u, y, d):
	return a + t * u - n * d + Vector3(0, y, 0)

## A wall-plane quad u0..u1, y0..y1 at depth d facing `nn` (default: the hall), UVs in metres / per.
static func wq(b, g, m, a, t, n, u0, u1, y0, y1, d, per, nn = null):
	var p = [P(a, t, n, u0, y0, d), P(a, t, n, u1, y0, d), P(a, t, n, u1, y1, d), P(a, t, n, u0, y1, d)]
	var uv = [Vector2(-u0 / per, -y0 / per), Vector2(-u1 / per, -y0 / per), Vector2(-u1 / per, -y1 / per), Vector2(-u0 / per, -y1 / per)]
	b.quad(g, m, p, n if nn == null else nn, uv)

static func build(b, g, e, a, bb, n, t, Ln, sd):
	var G = "gi_shell"
	front(b, "gi_front", a, t, n, sd)
	room(b, G, a, t, n)
	lights(b, G, a, t, n)
	machines(b, a, t, n)
	var rp = ReflectionProbe.new()
	rp.position = P(a, t, n, UNIT * 0.5, CEIL * 0.5, ROOM_D * 0.5)
	rp.size = (t * UNIT + n * ROOM_D).abs() + Vector3(0.1, CEIL + 0.1, 0.1)
	rp.box_projection = true
	rp.interior = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.intensity = 0.5
	b.light_root.add_child(rp)

# ------------------------------------------------------------------ the front
## Mustard tile portal: tile frames round the opening and both display windows, the white sign
## panel over the opening with the 2026 sign (y26/parts/games.json), plush piled in the windows.
static func front(b, g, a, t, n, sd):
	var LH = b.LANE_H
	# the mall's wall over everything (cream), then the tile field over the whole front to the head
	wq(b, g, "cream", a, t, n, 0.0, UNIT, PANEL_Y1, LH, 0.0, 1.0)
	# tile everywhere except the opening and the two windows (glass must not show tile behind it)
	for W in [[0.35, O0 - 0.35], [O1 + 0.35, UNIT - 0.35]]:
		wq(b, g, "gi_tile", a, t, n, W[0], W[1], 0.0, 0.45, -0.02, 0.6)
		wq(b, g, "gi_tile", a, t, n, W[0], W[1], HEAD - 0.1, HEAD + 0.35, -0.02, 0.6)
	for Pr in [[0.0, 0.35], [O0 - 0.35, O0], [O1, O1 + 0.35], [UNIT - 0.35, UNIT]]:
		wq(b, g, "gi_tile", a, t, n, Pr[0], Pr[1], 0.0, HEAD + 0.35, -0.02, 0.6)
	wq(b, g, "gi_tile", a, t, n, O0, O1, HEAD, HEAD + 0.35, -0.02, 0.6)
	wq(b, g, "gi_tile", a, t, n, 0.0, O0 - 0.3, HEAD + 0.35, PANEL_Y1, -0.02, 0.6)
	wq(b, g, "gi_tile", a, t, n, O1 + 0.3, UNIT, HEAD + 0.35, PANEL_Y1, -0.02, 0.6)
	# the white sign panel over the opening, 6 cm proud, and the lit sign on it
	b.cur_color = Color.WHITE
	b.box(g, "gi_panel", P(a, t, n, (O0 + O1) * 0.5, (HEAD + 0.35 + PANEL_Y1) * 0.5, -0.04) , b.abs_size(t, O1 - O0 + 0.6, PANEL_Y1 - HEAD - 0.35, 0.08, n))
	var mid = P(a, t, n, (O0 + O1) * 0.5, 0, -0.08)
	if not b.sign_2026(g, sd.name, mid - Vector3(0, b.OPEN_H + (b.LANE_H - b.OPEN_H) * 0.5, 0) + Vector3(0, (HEAD + 0.35 + PANEL_Y1) * 0.5, 0), n, t, O1 - O0 + 0.4):
		pass
	# the two display windows: glass in a dark frame, a white sill, plush piled behind
	for w in [[0.35, O0 - 0.35], [O1 + 0.35, UNIT - 0.35]]:
		var wu0 = w[0]
		var wu1 = w[1]
		wq(b, g, "glass", a, t, n, wu0, wu1, 0.45, HEAD - 0.1, -0.03, 1.0)
		b.cur_color = Color("#1b1b1e")
		for fr in [[wu0 - 0.04, wu0 + 0.04], [wu1 - 0.04, wu1 + 0.04]]:
			b.box(g, "vcolor", P(a, t, n, (fr[0] + fr[1]) * 0.5, (0.45 + HEAD - 0.1) * 0.5, -0.03), b.abs_size(t, 0.08, HEAD - 0.55, 0.06, n))
		b.box(g, "vcolor", P(a, t, n, (wu0 + wu1) * 0.5, HEAD - 0.08, -0.03), b.abs_size(t, wu1 - wu0 + 0.08, 0.06, 0.06, n))
		b.cur_color = Color("#e9e6dd")
		b.box(g, "vcolor_matte", P(a, t, n, (wu0 + wu1) * 0.5, 0.42, 0.25), b.abs_size(t, wu1 - wu0 + 0.08, 0.06, 0.44, n))
		# the window box behind the glass: white sides and back
		b.cur_color = Color("#f2f0ea")
		b.box(g, "vcolor_matte", P(a, t, n, (wu0 + wu1) * 0.5, (0.45 + HEAD) * 0.5, WALL_T + 0.02), b.abs_size(t, wu1 - wu0 + 0.1, HEAD - 0.4, 0.04, n))
		plush(b, g, a, t, n, wu0 + 0.1, wu1 - 0.1, 0.45, HEAD - 0.2, 0.08, WALL_T - 0.04)
		b.cur_color = Color.WHITE
	# the opening's returns in tile, a dark head
	b.quad(g, "gi_tile", [P(a, t, n, O0, 0, 0), P(a, t, n, O0, 0, WALL_T), P(a, t, n, O0, HEAD, WALL_T), P(a, t, n, O0, HEAD, 0)], t, [Vector2(0, 0), Vector2(WALL_T / 0.6, 0), Vector2(WALL_T / 0.6, -HEAD / 0.6), Vector2(0, -HEAD / 0.6)])
	b.quad(g, "gi_tile", [P(a, t, n, O1, 0, WALL_T), P(a, t, n, O1, 0, 0), P(a, t, n, O1, HEAD, 0), P(a, t, n, O1, HEAD, WALL_T)], -t, [Vector2(0, 0), Vector2(WALL_T / 0.6, 0), Vector2(WALL_T / 0.6, -HEAD / 0.6), Vector2(0, -HEAD / 0.6)])
	b.cur_color = Color("#2a2a2e")
	b.box(g, "vcolor_matte", P(a, t, n, (O0 + O1) * 0.5, HEAD + 0.03, WALL_T * 0.5), b.abs_size(t, O1 - O0, 0.06, WALL_T, n))
	b.cur_color = Color.WHITE
	# the front wall's solid parts are obstacles
	for wr in [[0.0, O0], [O1, UNIT]]:
		var w0 = P(a, t, n, wr[0], 0, -0.05)
		var w1 = P(a, t, n, wr[1], 0, WALL_T)
		b.obst(["rect", min(w0.x, w1.x), min(w0.z, w1.z), max(w0.x, w1.x), max(w0.z, w1.z)])

## Plush toys piled in a window (or on a shelf): soft rounded blocks in Pokémon colours, dynamic.
static func plush(b, g, a, t, n, u0, u1, y0, y1, d0, d1, seed = 7):
	var rng = RandomNumberGenerator.new()
	rng.seed = seed + int(u0 * 100) + int(d0 * 10)
	var cols = ["#f6d23a", "#f08a2a", "#5db5e8", "#79c66a", "#f6d23a", "#e94f6a", "#8e6bd1", "#f3f1e8"]
	var along_d = (d1 - d0) > (u1 - u0)   # a shelf runs along d; a window along u
	var y = y0
	while y < y1 - 0.2:
		var s = rng.randf_range(0.22, 0.34)
		var p = (d0 if along_d else u0)
		var p1 = (d1 if along_d else u1)
		while p < p1 - 0.15:
			s = rng.randf_range(0.22, 0.34)
			var u = (rng.randf_range(u0 + s * 0.5, max(u0 + s * 0.5, u1 - s * 0.5)) if along_d else p + s * 0.5)
			var dd = (p + s * 0.5 if along_d else rng.randf_range(d0 + s * 0.5, max(d0 + s * 0.5, d1 - s * 0.5)))
			b.cur_color = Color(cols[rng.randi() % cols.size()])
			var c = P(a, t, n, u, y + s * 0.5, dd)
			b.box(g, "vcolor_matte", c, Vector3(s * 0.9, s * 0.9, s * 0.9), Transform3D.IDENTITY, [], true)
			if rng.randf() < 0.7:
				b.box(g, "vcolor_matte", c + Vector3(0, s * 0.62, 0), Vector3(s * 0.62, s * 0.5, s * 0.62), Transform3D.IDENTITY, [], true)
			p += s * 0.95 + (0.25 if along_d else 0.0)
		y += 0.36
	b.cur_color = Color.WHITE

# ------------------------------------------------------------------ the room
static func room(b, G, a, t, n):
	var u0 = SIDE
	var u1 = UNIT - SIDE
	var dB = ROOM_D
	var up = Vector3.UP
	# plank floor through the opening and over the room (2.4 m repeat)
	b.quad(G, "gi_plank", [P(a, t, n, O0, 0, 0), P(a, t, n, O1, 0, 0), P(a, t, n, O1, 0, WALL_T), P(a, t, n, O0, 0, WALL_T)], up, [], false, 1.0 / 2.4)
	b.quad(G, "gi_plank", [P(a, t, n, u0, 0, WALL_T), P(a, t, n, u1, 0, WALL_T), P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB)], up, [], false, 1.0 / 2.4)
	# white 2x2 lay-in ceiling
	var cq = [P(a, t, n, u0, CEIL, WALL_T), P(a, t, n, u0, CEIL, dB), P(a, t, n, u1, CEIL, dB), P(a, t, n, u1, CEIL, WALL_T)]
	var cuv = []
	for p in cq:
		cuv.append(Vector2(p.x / 0.61, p.z / 0.61))
	b.quad(G, "drop_tile", cq, Vector3.DOWN, cuv)
	# walls: slatwall to the band, the orange band with its mustard stripe to the ceiling
	for side in [[u0, t, WALL_T, dB], [u1, -t, dB, WALL_T]]:
		var uu = side[0]
		b.quad(G, "gi_slat", [P(a, t, n, uu, 0, side[2]), P(a, t, n, uu, 0, side[3]), P(a, t, n, uu, BAND_Y0, side[3]), P(a, t, n, uu, BAND_Y0, side[2])], side[1],
			[Vector2(0, BAND_Y0 / 0.608), Vector2((dB - WALL_T) / 0.608, BAND_Y0 / 0.608), Vector2((dB - WALL_T) / 0.608, 0), Vector2(0, 0)])
		b.quad(G, "gi_band", [P(a, t, n, uu, BAND_Y0, side[2]), P(a, t, n, uu, BAND_Y0, side[3]), P(a, t, n, uu, CEIL, side[3]), P(a, t, n, uu, CEIL, side[2])], side[1],
			[Vector2(0, 1), Vector2((dB - WALL_T) / (CEIL - BAND_Y0), 1), Vector2((dB - WALL_T) / (CEIL - BAND_Y0), 0), Vector2(0, 0)])
	# the back wall and the front wall's inside
	b.quad(G, "gi_slat", [P(a, t, n, u1, 0, dB), P(a, t, n, u0, 0, dB), P(a, t, n, u0, BAND_Y0, dB), P(a, t, n, u1, BAND_Y0, dB)], n, [Vector2(0, BAND_Y0 / 0.608), Vector2(UNIT / 0.608, BAND_Y0 / 0.608), Vector2(UNIT / 0.608, 0), Vector2(0, 0)])
	b.quad(G, "gi_band", [P(a, t, n, u1, BAND_Y0, dB), P(a, t, n, u0, BAND_Y0, dB), P(a, t, n, u0, CEIL, dB), P(a, t, n, u1, CEIL, dB)], n, [Vector2(0, 1), Vector2(UNIT / (CEIL - BAND_Y0), 1), Vector2(UNIT / (CEIL - BAND_Y0), 0), Vector2(0, 0)])
	for fw in [[u0, O0], [O1, u1]]:
		b.quad(G, "gi_slat", [P(a, t, n, fw[0], 0, WALL_T), P(a, t, n, fw[1], 0, WALL_T), P(a, t, n, fw[1], BAND_Y0, WALL_T), P(a, t, n, fw[0], BAND_Y0, WALL_T)], -n, [Vector2(0, BAND_Y0 / 0.608), Vector2((fw[1] - fw[0]) / 0.608, BAND_Y0 / 0.608), Vector2((fw[1] - fw[0]) / 0.608, 0), Vector2(0, 0)])
	b.quad(G, "gi_band", [P(a, t, n, u0, BAND_Y0, WALL_T), P(a, t, n, u1, BAND_Y0, WALL_T), P(a, t, n, u1, CEIL, WALL_T), P(a, t, n, u0, CEIL, WALL_T)], -n, [Vector2(0, 1), Vector2(UNIT / (CEIL - BAND_Y0), 1), Vector2(UNIT / (CEIL - BAND_Y0), 0), Vector2(0, 0)])
	b.quad(G, "gi_slat", [P(a, t, n, O0, HEAD, WALL_T), P(a, t, n, O1, HEAD, WALL_T), P(a, t, n, O1, BAND_Y0, WALL_T), P(a, t, n, O0, BAND_Y0, WALL_T)], -n, [Vector2(0, 0.5), Vector2((O1 - O0) / 0.608, 0.5), Vector2((O1 - O0) / 0.608, 0), Vector2(0, 0)])
	# the party wall mural (left wall, 2 to 6 m in), 1 cm proud of the slatwall
	var mu = u1 - 0.01
	b.quad(G, "gi_mural", [P(a, t, n, mu, 0.9, 6.0), P(a, t, n, mu, 0.9, 2.0), P(a, t, n, mu, 3.5 - 0.1, 2.0), P(a, t, n, mu, 3.5 - 0.1, 6.0)], -t, [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)])
	# the plush shelf along the right wall at 2.3 m (a white shelf with toys on it), 3 to 36 m
	b.cur_color = Color("#f1efea")
	b.box(G, "vcolor_matte", P(a, t, n, u0 + 0.2, 2.3, 19.5), b.abs_size(t, 0.4, 0.04, 33.0, n))
	b.cur_color = Color.WHITE
	plush(b, G, a, t, n, u0 + 0.02, u0 + 0.38, 2.32, 2.7, 3.0, 36.0, 11)
	# columns: a white round pipe column mid-store, a thin black one further back
	b.cur_color = Color("#f4f2ee")
	b.cyl(G, "vcolor", P(a, t, n, 4.1, 0, 20.0), 0.16, 0.16, CEIL, 18, false, false)
	b.cur_color = Color("#15161a")
	b.cyl(G, "vcolor", P(a, t, n, 3.2, 0, 29.5), 0.05, 0.05, CEIL, 12, false, false)
	b.cur_color = Color.WHITE
	for c in [[4.1, 20.0, 0.16], [3.2, 29.5, 0.05]]:
		var cp = P(a, t, n, c[0], 0, c[1])
		b.obst(["rect", cp.x - c[2] - 0.1, cp.z - c[2] - 0.1, cp.x + c[2] + 0.1, cp.z + c[2] + 0.1])
	# the back door with its exit sign
	b.cur_color = Color("#3a3c42")
	b.box(G, "vcolor", P(a, t, n, 1.2, 1.05, dB - 0.02), b.abs_size(t, 0.95, 2.1, 0.04, n))
	b.cur_color = Color.WHITE
	b.box(G, "exit_sign", P(a, t, n, 1.2, 2.35, dB - 0.05), b.abs_size(t, 0.36, 0.16, 0.06, n))

# ------------------------------------------------------------------ light
## Parabolic troffers in two rows every 3.05 m (the footage's grid), and a few track spots.
static func lights(b, G, a, t, n):
	var d = WALL_T + 1.6
	while d < ROOM_D - 1.0:
		for u in [2.2, 5.8]:
			var c = P(a, t, n, u, CEIL - 0.004, d)
			b.quad(G, "cd7_troffer", [c - t * 0.3 - n * 0.6, c - t * 0.3 + n * 0.6, c + t * 0.3 + n * 0.6, c + t * 0.3 - n * 0.6], Vector3.DOWN,
				[Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)])
			var l = b.add_spot(c - Vector3(0, 0.05, 0), Vector3.DOWN, 1.6, 7.0, 70.0, Color(1.0, 0.97, 0.9))
			b.tag(l, "", 1.6, 1.6)
		d += 3.05
	# track spots over the prize counter and the party corner
	for dd in [3.5, 8.0, 10.5]:
		var l2 = b.add_spot(P(a, t, n, 6.4, CEIL - 0.08, dd), Vector3.DOWN, 2.2, 5.0, 55.0, Color(1.0, 0.94, 0.84))
		b.tag(l2, "", 2.2, 2.2)

# ------------------------------------------------------------------ the machines
## Pocket Change's placement helpers, pointed at its modules.
static func put(b, a, t, n, mod, u, d, dir, opts = {}, pad = 0.25):
	var f = {"+d": -n, "-d": n, "+u": t, "-u": -t}[dir]
	var M = load(PC % mod)
	var k0 = b.obstacles.size()
	M.build(b, "gi%d_mach" % int(clamp(d / 10.0, 0, 3)), P(a, t, n, u, 0, d), f, opts)
	for i in range(k0, b.obstacles.size()):
		var o = b.obstacles[i]
		if o[0] is String and o[0] == "rect":
			b.obstacles[i] = ["rect", o[1] - pad, o[2] - pad, o[3] + pad, o[4] + pad]
	return M

static func fp(mod, opts = {}):
	return load(PC % mod).footprint(opts)

## A run of one module along a side wall (`wall_u` is the wall's face, facing the room along
## `dir`), from d0 toward +d with `gap` between. Returns where the run ends.
static func wall_run(b, a, t, n, mod, opts_list, wall_u, dir, d0, gap = 0.03):
	var d = d0
	for o in opts_list:
		var sz = fp(mod, o)
		# the player faces the wall: against the right wall (u0) he faces -u, so the machine's front
		# edge sits sz.y out from the wall toward +u; against the left wall (u1) the reverse
		var du = sz.y if dir == "-u" else -sz.y
		put(b, a, t, n, mod, wall_u + du, d + sz.x * 0.5, dir, o)
		d += sz.x + gap
	return d

## A white folding table with two benches (the party corner), along the left wall.
static func party_table(b, G, a, t, n, u, d):
	b.cur_color = Color("#f1f0ea")
	b.box(G, "vcolor_matte", P(a, t, n, u, 0.74, d), b.abs_size(t, 0.76, 0.04, 1.83, n))
	b.cur_color = Color("#7c8088")
	for k in [-0.8, 0.8]:
		b.box(G, "vcolor", P(a, t, n, u, 0.36, d + k), b.abs_size(t, 0.6, 0.72, 0.04, n), Transform3D.IDENTITY, [], true)
	b.cur_color = Color("#e4e2dc")
	for s in [-0.62, 0.62]:
		b.box(G, "vcolor_matte", P(a, t, n, u + s, 0.45, d), b.abs_size(t, 0.3, 0.04, 1.6, n))
		b.cur_color = Color("#7c8088")
		for k in [-0.7, 0.7]:
			b.box(G, "vcolor", P(a, t, n, u + s, 0.22, d + k), b.abs_size(t, 0.26, 0.44, 0.04, n), Transform3D.IDENTITY, [], true)
		b.cur_color = Color("#e4e2dc")
	b.cur_color = Color.WHITE
	var p0 = P(a, t, n, u - 0.85, 0, d - 1.0)
	var p1 = P(a, t, n, u + 0.85, 0, d + 1.0)
	b.obst(["rect", min(p0.x, p1.x), min(p0.z, p1.z), max(p0.x, p1.x), max(p0.z, p1.z)])

static func machines(b, a, t, n):
	var u0 = SIDE              # the right wall (walking in)
	var u1 = UNIT - SIDE       # the left wall
	var G = "gi0_mach"
	# --- left, walking in: two party tables under the CLAW MANIA wall, then the prize counter
	# (glass showcases along the wall, the plush wall behind), then a token changer
	party_table(b, G, a, t, n, u1 - 0.9, 2.4)
	party_table(b, G, a, t, n, u1 - 0.9, 4.4)
	put(b, a, t, n, "redeem", u1 - 1.95, 8.3, "+u", {"kind": "counter", "length": 5.4}, 0.15)
	put(b, a, t, n, "redeem", u1 - 0.45, 8.3, "+u", {"kind": "prizewall", "length": 5.4, "height": 2.4}, 0.0)
	put(b, a, t, n, "redeem", u1 - 0.35, 12.2, "-u", {"kind": "tokens"}, 0.15)
	# --- right wall: claw machines from the front almost to the back, in banks with breathing room
	var d = WALL_T + 0.9
	for bank in 5:
		d = wall_run(b, a, t, n, "crane", [{"style": 0}, {"style": 1}, {"style": 2}, {"style": 1}], u0, "-u", d, 0.02)
		d += 1.4
	# --- left wall past the counter: more claws, then the wheel-style ticket games (video uprights stand in)
	d = wall_run(b, a, t, n, "crane", [{"style": 2}, {"style": 0}, {"style": 1}], u1, "+u", 14.6, 0.02)
	d = wall_run(b, a, t, n, "video", [{"style": 1}, {"style": 4}, {"style": 2}, {"style": 6}], u1, "+u", d + 1.0, 0.1)
	d = wall_run(b, a, t, n, "crane", [{"style": 1}, {"style": 2}], u1, "+u", d + 1.2, 0.02)
	wall_run(b, a, t, n, "driver", [{"kind": "racer", "style": 0}, {"kind": "racer", "style": 1}], u1, "+u", d + 1.2, 0.1)
	# --- the middle, front to back: a coin pusher behind the party corner, two dome ticket games
	# (the cyclone stands in), the air hockey pair across the room, two kiddie rides at the back
	var ps = fp("pusher", {"double": true})
	put(b, a, t, n, "pusher", 4.3 + ps.y * 0.5, 11.0, "-u", {"double": true}, 0.2)
	put(b, a, t, n, "cyclone", 4.1, 15.4, "+d", {}, 0.2)
	put(b, a, t, n, "cyclone", 4.1, 18.2, "-d", {}, 0.2)
	var ah = fp("airhockey")
	for i in 2:
		put(b, a, t, n, "airhockey", 4.0 - ah.y * 0.5, 24.4 + i * (ah.x + 1.6), "+u", {"number": i + 1})
	for i in 2:
		put(b, a, t, n, "ride", 2.6 + i * 2.4, 33.4, "+d", {})
	# a few uprights on the back wall
	for i in 4:
		var s = [3, 0, 2, 5][i]
		var sz = fp("video", {"style": s})
		put(b, a, t, n, "video", 2.4 + i * 0.8, ROOM_D - SIDE - sz.y, "+d", {"style": s})

# ------------------------------------------------------------------ materials
## "gi_<key>" (build_mall.gd's mat() calls this).
static func fill_mat(m, key, b):
	match key:
		"plank":
			m.albedo_texture = b.tex("gi/plank.png"); m.roughness = 0.45; m.metallic = 0.0
		"slat":
			m.albedo_texture = b.tex("gi/slat.png"); m.roughness = 0.75
		"band":
			m.albedo_texture = b.tex("gi/band.png"); m.roughness = 0.8
		"tile":
			m.albedo_texture = b.tex("gi/tile.png"); m.roughness = 0.28
		"mural":
			m.albedo_texture = b.tex("gi/mural.png"); m.roughness = 0.7
		"panel":
			m.albedo_texture = b.tex("gi/panel.png"); m.roughness = 0.5
		_:
			return false
	return true
