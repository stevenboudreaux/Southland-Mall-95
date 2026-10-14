## Franks (s33), the hot dog stand near the Shoe Dept. court (Courier, May 8 1988: "Franks, a
## restaurant specializing in a variety of gourmet hot dogs", owned with the Orange Julius next
## door by Mehrhoff Corp.). Steven, Oct 8 2026: the sign is the ads' lowercase "franks" as bare
## red neon, no backing, straight on the cream facade. Oct 8, 11:44: storefront only; Oct 14,
## 16:23: back on the side wall facing the east hall too ("you took the neon off that side wall"),
## and the tubes made "sturdier ... if it was a font you would almost put bold on it": 32 mm glass
## in place of 21 mm (38 mm), 65 mm off the wall, wider light pools. The unit is the corner of the row
## Franks, Orange Julius, Tee Tai's on the entrance hall (directory units 53, 52, 51).
##
## The facade is the mall's generic storefront (build_mall.gd storefront(), no sign box, no
## awning); the neon is built here as skeleton neon:
## - one glass tube per stroke of the logo, along the stroke's centre line (franks_sign.json,
##   traced from the menu ad by make_franks.py), 38 mm red glass 65 mm off the wall;
## - every run ends in electrodes turned back into the wall through black boots;
## - clear standoffs every 20 cm; a soft red pool of light on the wall under each tube.
## Geometry and vertex colour only (materials "sg_fr2_tube", the Karmelkorn neon's boots, posts
## and pool: channel.gd).

const CS = preload("res://tools/stores/signs/cucos_sign.gd")
const UP = Vector3.UP
const SIGN = "res://tools/stores/franks/franks_sign.json"
const TUBE_R = 0.019     # 38 mm glass (the bold cut, Oct 14; was 21 mm): one tube carries each heavy stroke
const TUBE_Z = 0.065     # tube centres off the wall
const BOTTOM = 3.24      # the sign's lowest point (the s's tail) above the floor
const POOL = Color(0.46, 0.06, 0.03)
const WIDE = Color(0.10, 0.012, 0.006)

## g, e, a, b_, n, t, Ln, sd: as build_mall.gd storefront() passes them (the front, x 2..12 at z = 6).
static func build(b, g, e, a, b_, n, t, Ln, sd):
	b.storefront(g, e, a, b_, n, t, Ln, true)
	# the storefront: centred on the frontage, on the face of the cream bulkhead (16 cm proud)
	neon(b, "frf_sign", a + t * (Ln * 0.5) + n * 0.16 + UP * BOTTOM, n)
	# the side wall on the east hall (layout edge [2,6]-[2,16], a plain cream wall at the a end of
	# the front, facing -t): the same sign, centred on the unit's depth (Steven, Oct 14)
	var deep = float(e.get("depth", 10.0))
	neon(b, "frf_sign", a - n * (deep * 0.5) + (-t) * 0.0 + UP * BOTTOM, -t)

## The neon with the middle of its bottom at c on a wall facing nn.
static func neon(b, g, c, nn):
	var J = JSON.parse_string(FileAccess.get_file_as_string(SIGN))
	var rv = (-nn).cross(UP)
	var s_tube = b.st(g, "sg_fr2_tube", true)
	var s_boot = b.st(g, "sg_kk2_boot", true)
	var s_post = b.st(g, "sg_kk2_post", true)
	var s_pool = b.st(g + "_glow", "sg_kk2_pool", true)
	for tb in J.tubes:
		var run = []
		for q in tb.pts:
			run.append(c + rv * float(q[0]) + UP * float(q[1]) + nn * TUBE_Z)
		CS._tube(s_tube, run, TUBE_R, nn, 8)
		CS._ends(s_boot, run, TUBE_R * 1.3, nn, TUBE_Z)
		CS._posts(s_post, run, nn, TUBE_Z - TUBE_R, 0.2)
		CS._pool(s_pool, run, nn, TUBE_Z - 0.003, 0.07, POOL)
		CS._pool(s_pool, run, nn, TUBE_Z - 0.002, 0.2, WIDE)
