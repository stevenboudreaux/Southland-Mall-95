## The insides of two shoe stores still on the generic front: Footquarters (s27) and Felger's
## Footwear (n62), on the east side of the north east hall (Steven, Oct 20, 2026: "Make the
## inside of Footquarters and Felger's Footwear look like shoe stores. I don't want to be able to
## go in yet, but just make the products look more like shoes like lady footlocker").
## Seen through the glass only (their tiles stay shut): white slatwall on the side and back walls
## with clear shelves of single display shoes angled out toward the door, a lit header strip, two
## upholstered try-on benches with a fitting stool and a floor mirror, and a low display table of
## shoes on risers near the window. Footquarters carries trainers and casual shoes, Felger's dress
## shoes, loafers, boots and pumps (both guessed: no photos of either inside yet).
##
## Frame: o = the first inner corner of the frontage, r along the frontage, f into the store
## (build_mall.gd interior(): p0, t, -n). The shoes are dynamic (probe-lit, "shoe_small") so the
## many little boxes stay out of the lightmap; the fixtures are baked with the hall group `g`.

const UP = Vector3.UP
const K = preload("res://tools/stores/media/kit.gd")

const LOOK = {
	"FOOTQUARTERS": {"wall": "#f2f2ee", "bench": "#22346e", "kinds": ["trainer", "trainer", "trainer", "casual"],
		"cols": ["#f4f4f2", "#f4f4f2", "#1c1c20", "#c8202c", "#1f3f8f", "#2a8a4a", "#8a8a90", "#e8d8b8"],
		"trim": ["#c8202c", "#1f3f8f", "#1c1c20", "#e8a020", "#7a7a80"], "seed": 27},
	"FELGER'S FOOTWEAR": {"wall": "#efe6d6", "bench": "#6a1e2a", "kinds": ["dress", "loafer", "boot", "pump", "pump"],
		"cols": ["#2a1a12", "#5a3218", "#8a5a30", "#1c1c1e", "#b08a5a", "#6a1e2a", "#e8dcc4", "#3a2a24"],
		"trim": ["#2a1a12", "#1c1c1e", "#c8a050"], "seed": 62},
}

static func L(o, r, f, x, y, z):
	return o + r * x + UP * y + f * z

static func inside(b, g, o, r, f, w, deep, name):
	var lk = LOOK[name]
	var rng = RandomNumberGenerator.new()
	rng.seed = int(lk.seed)
	var wall = Color(lk.wall)
	var back = deep - 0.02
	# the back wall: a full-width shoe wall
	shoe_wall(b, g, L(o, r, f, 0.02, 0, back), r, -f, w - 0.04, lk, rng, wall)
	# the side walls, from behind the window display to the back
	var d0 = 1.4
	shoe_wall(b, g, L(o, r, f, 0.02, 0, d0), f, r, back - d0 - 0.05, lk, rng, wall)
	shoe_wall(b, g, L(o, r, f, w - 0.02, 0, back - 0.05), -f, -r, back - d0 - 0.05, lk, rng, wall)
	# try-on benches back to back down the middle, a fitting stool, a floor mirror
	var cu = w * 0.5
	var bc = Color(lk.bench)
	for k in 2:
		var bd = 3.4 + k * 2.6
		if bd > deep - 1.6:
			break
		bench(b, g, L(o, r, f, cu, 0, bd), r, f, min(2.2, w - 2.4), bc)
		stool(b, L(o, r, f, cu + 0.6, 0, bd + 0.75), f)
	mirror(b, g, L(o, r, f, w - 0.55, 0, deep * 0.62), -r)
	# a low table of shoes on risers inside the window
	table(b, g, L(o, r, f, cu, 0, 1.6), r, f, min(1.6, w - 1.6), lk, rng)

## A slatwall shoe wall `ln` long along r from o, facing f: six clear shelves of single shoes.
static func shoe_wall(b, g, o, r, f, ln, lk, rng, wall):
	b.cur_color = wall
	K.fq(b, g, "vcolor", o, r, f, 0.0, ln, 0.0, 2.75, 0.01)
	b.cur_color = Color("#d8d8d4")
	for y in [0.33, 0.66, 0.99, 1.32, 1.65, 1.98, 2.31]:
		K.lbox(b, g, "vcolor", o, r, f, 0.0, y - 0.004, 0.012, ln, 0.008, 0.004, [])
	# a coloured header strip at the top
	b.cur_color = Color(lk.trim[0])
	K.lbox(b, g, "vcolor", o, r, f, 0.0, 2.45, 0.0, ln, 0.2, 0.05, [])
	for row in 6:
		var y = 0.36 + row * 0.33
		b.cur_color = Color("#e8eef0")
		K.lbox(b, "shoe_small", "vcolor", o, r, f, 0.04, y, 0.0, ln - 0.08, 0.012, 0.26, [], true)
		var x = 0.14 + (0.12 if row % 2 else 0.0)
		while x + 0.28 < ln:
			shoe(b, L(o, r, f, x, y + 0.012, 0.14), r, f, lk, rng, 0.45)
			x += 0.42
	b.cur_color = Color.WHITE

## One display shoe at c, toe pointing out from the wall and turned `turn` (radians) toward r so
## its side shows. Kinds: trainer, casual, dress, loafer, boot, pump.
static func shoe(b, c, r, f, lk, rng, turn):
	var kind = lk.kinds[rng.randi_range(0, lk.kinds.size() - 1)]
	var col = Color(lk.cols[rng.randi_range(0, lk.cols.size() - 1)])
	var trim = Color(lk.trim[rng.randi_range(0, lk.trim.size() - 1)])
	var ff = (f * cos(turn) + r * sin(turn)).normalized()      # heel -> toe
	var rr = ff.cross(UP).normalized()
	var o = c - ff * 0.13
	var S = "shoe_small"
	match kind:
		"trainer", "casual":
			b.cur_color = Color("#f2f0ea") if kind == "trainer" else Color("#d8c8a8")
			K.lbox(b, S, "vcolor", o, rr, ff, -0.045, 0.0, 0.0, 0.09, 0.03, 0.27, [], true)
			b.cur_color = col
			K.lbox(b, S, "vcolor", o, rr, ff, -0.04, 0.03, 0.01, 0.08, 0.075, 0.13, ["-y"], true)
			K.lbox(b, S, "vcolor", o, rr, ff, -0.04, 0.03, 0.14, 0.08, 0.045, 0.12, ["-y"], true)
			b.cur_color = trim
			for s in [-1.0, 1.0]:
				K.lbox(b, S, "vcolor", o, rr, ff, 0.0405 * s - 0.001, 0.045, 0.06, 0.002, 0.03, 0.14, [], true)
		"dress", "loafer":
			b.cur_color = Color("#1a1210")
			K.lbox(b, S, "vcolor", o, rr, ff, -0.04, 0.0, 0.0, 0.08, 0.025, 0.27, [], true)
			b.cur_color = col
			K.lbox(b, S, "vcolor", o, rr, ff, -0.038, 0.025, 0.01, 0.076, 0.06, 0.11, ["-y"], true)
			K.lbox(b, S, "vcolor", o, rr, ff, -0.036, 0.025, 0.12, 0.072, 0.04, 0.14, ["-y"], true)
			if kind == "loafer":
				b.cur_color = trim
				K.lbox(b, S, "vcolor", o, rr, ff, -0.03, 0.062, 0.15, 0.06, 0.006, 0.02, [], true)
		"boot":
			b.cur_color = Color("#1a1210")
			K.lbox(b, S, "vcolor", o, rr, ff, -0.042, 0.0, 0.0, 0.084, 0.03, 0.27, [], true)
			b.cur_color = col
			K.lbox(b, S, "vcolor", o, rr, ff, -0.04, 0.03, 0.0, 0.08, 0.2, 0.11, ["-y"], true)
			K.lbox(b, S, "vcolor", o, rr, ff, -0.04, 0.03, 0.11, 0.08, 0.05, 0.15, ["-y"], true)
		"pump":
			b.cur_color = col
			K.lbox(b, S, "vcolor", o, rr, ff, -0.012, 0.0, 0.01, 0.024, 0.07, 0.025, [], true)
			K.lbox(b, S, "vcolor", o, rr, ff, -0.035, 0.065, 0.0, 0.07, 0.012, 0.09, [], true)
			# the arch running down to the toe, then the toe box
			var p0 = L(o, rr, ff, 0.0, 0.072, 0.09)
			var p1 = L(o, rr, ff, 0.0, 0.006, 0.17)
			var mid = (p0 + p1) * 0.5
			var along = (p1 - p0).normalized()
			var side = rr
			var nn = along.cross(side).normalized()
			if nn.y < 0.0:
				nn = -nn
			b.box(S, "vcolor", Vector3.ZERO, Vector3(0.07, 0.012, p0.distance_to(p1)), Transform3D(Basis(side, along.cross(side), along), mid), [], true)
			K.lbox(b, S, "vcolor", o, rr, ff, -0.034, 0.0, 0.17, 0.068, 0.04, 0.09, [], true)
	b.cur_color = Color.WHITE

## An upholstered try-on bench, back to back with a second seat, `ln` along r centred on c.
static func bench(b, g, c, r, f, ln, col):
	var o = c - r * (ln * 0.5)
	b.cur_color = Color("#3a3a3c")
	K.lbox(b, g, "vcolor", o, r, f, 0.05, 0.0, -0.4, ln - 0.1, 0.08, 0.8, ["-y"])
	b.cur_color = col
	K.lbox(b, g, "vcolor", o, r, f, 0.0, 0.08, -0.42, ln, 0.34, 0.84, [])
	K.lbox(b, g, "vcolor", o, r, f, 0.0, 0.42, -0.08, ln, 0.4, 0.16, [])
	b.cur_color = Color.WHITE

## A fitting stool: a low seat with its sloped foot rest toward f.
static func stool(b, c, f):
	var r = f.cross(UP).normalized()
	b.cur_color = Color("#3a3a3c")
	K.lbox(b, "shoe_small", "vcolor", c, r, f, -0.2, 0.0, -0.18, 0.4, 0.32, 0.3, [], true)
	b.cur_color = Color("#6a6a6e")
	var p = L(c, r, f, 0.0, 0.2, 0.2)
	var f2 = (f * cos(0.5) + UP * sin(0.5)).normalized()
	b.box("shoe_small", "vcolor", Vector3.ZERO, Vector3(0.36, 0.02, 0.3), Transform3D(Basis(r, f2.cross(r), f2), p), [], true)
	b.cur_color = Color.WHITE

## A floor mirror on a stand, facing f.
static func mirror(b, g, c, f):
	var r = f.cross(UP).normalized()
	b.cur_color = Color("#2a2a2c")
	K.lbox(b, g, "vcolor", c, r, f, -0.25, 0.0, -0.15, 0.5, 0.05, 0.3, [])
	K.lbox(b, g, "vcolor", c, r, f, -0.24, 0.05, -0.04, 0.48, 1.55, 0.04, [])
	b.cur_color = Color.WHITE
	K.fq(b, g, "ap_mirror", c, r, f, -0.21, 0.21, 0.12, 1.55, 0.001)

## A low display table near the window with shoes on two risers.
static func table(b, g, c, r, f, ln, lk, rng):
	var o = c - r * (ln * 0.5)
	b.cur_color = Color("#f2f2ee") if lk.wall == "#f2f2ee" else Color("#8a5a30")
	K.lbox(b, g, "vcolor", o, r, f, 0.0, 0.0, -0.35, ln, 0.5, 0.7, ["-y"])
	K.lbox(b, g, "vcolor", o, r, f, ln * 0.2, 0.5, -0.2, ln * 0.25, 0.14, 0.3, ["-y"])
	K.lbox(b, g, "vcolor", o, r, f, ln * 0.58, 0.5, -0.2, ln * 0.2, 0.24, 0.3, ["-y"])
	b.cur_color = Color.WHITE
	var spots = [[ln * 0.1, 0.5], [ln * 0.32, 0.64], [ln * 0.47, 0.5], [ln * 0.68, 0.74], [ln * 0.9, 0.5]]
	for s in spots:
		shoe(b, L(o, r, f, s[0], s[1], 0.0) - f * 0.05, r, -f, lk, rng, rng.randf_range(-0.9, 0.9))
