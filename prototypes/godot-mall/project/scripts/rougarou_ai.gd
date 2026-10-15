## The Rougarou's behaviour, v1 (Steven, Oct 14 2026): "when you log in it's not there, but after a
## few minutes you see it at the far side of the mall and it's just standing. Sometimes it'll just
## show up right behind you. Very ominous. It can be far away and then run when you turn and see
## it ... scatters off behind another wing or into a store." It never attacks.
##
## A node under the wing, made by player.gd. The sighting cycle:
##   HIDDEN  — nothing for `first_sighting_s`, then `between_sightings_s` between sightings
##   FAR     — it stands hunched 25–45 m away in the player's line of sight, more often behind
##             the player than in front, head turned to the player; after `stand_timeout_s` it
##             fades out unseen
##   BEHIND  — it stands `behind_m` straight behind the player, facing them; if they turn and see
##             it, it bolts at once; else it leaves after `behind_timeout_s`
##   BOLT    — once the player has looked at it for `look_to_bolt_s`, it runs along the walk grid
##             to the nearest tile out of the player's sight (a side hall, a store, round a corner)
##             and is gone
## "Seen" means: within `see_m`, inside the camera's view cone, line of sight clear on the walk
## grid. Timings and distances come from res://scripts/rougarou.json so Steven can tune them.
## URL: ?rougarou=0 keeps it away; ?rougarou=now brings the first sighting at once;
## ?rougarou=behind makes that first sighting the behind-you one.
##
## STALK mode, the default since Oct 14 evening (Steven, 20:48): "immediately visible down the
## first long corridor you travel, in front of you at a distance. If you try to get close to it
## it runs away. But you always see it at a distance." So from the first seconds it stands
## `stalk_m` ahead, in the player's line of sight and inside `stalk_cone_deg` of where they look.
## Walk within `flee_m` and it runs along the walk grid to a tile at least `flee_to_m` away that
## the player can still see (round a corner only if there is no such tile), then stands again.
## If the player turns away or rounds a corner so it is out of sight (or more than `lost_m` off)
## for `relocate_after_s`, it is put ahead of them again, far down whatever they now face.
## "mode" in rougarou.json: "stalk" or "sightings" (the cycle above); ?rougarou=now|behind use
## the cycle.
##
## STORY mode, the default since Oct 15 (Steven, 06:45; Demo 28): a route through the mall.
##   0 idle      nothing. Walk into Pocket Change (past the Whirlwind) and back out to arm it.
##   1 mannequin it stands stock-still in Merry-Go-Round's right-hand window, in place of the
##               form there (Wing 2's dyn_rg_mannequin, hidden from now until the route ends).
##               It stays stock-still until you are within story_mq_flee_m (5 m: the one time
##               you get close, Steven Oct 15 07:47), then runs to the back and is gone.
##   2 cucos     it stands in front of Cucos (Wing 1). Come close and it runs in and is gone.
##   3 woolworth it lurks at the back of Woolworth, ducking from aisle to aisle out of your sight.
##               Get a close look (seen within story_seen_close_m) and it runs and is gone.
##   then back to 0: the form is back in the window; Pocket Change again starts it over.
## The stage survives crossing wings (sessionStorage "mall-rg" on the web).
## ?rougarou=s1|s2|s3 jumps to a stage (tests); ?rougarou=stalk the stalk mode.
extends Node

const CFG = "res://scripts/rougarou.json"
var cfg := {
	"first_sighting_s": 180.0, "between_sightings_s": [45.0, 120.0], "far_m": [25.0, 45.0],
	"behind_m": 3.2, "behind_chance": 0.3, "see_m": 70.0, "see_cone_deg": 28.0, "look_to_bolt_s": 1.0,
	"behind_look_to_bolt_s": 0.35, "stand_timeout_s": 40.0, "behind_timeout_s": 12.0, "bolt_mps": 6.8,
	"hide_m": 14.0, "gone_after_unseen_s": 2.0,
	"mode": "story", "stalk_first_s": 30.0, "stalk_m": [27.0, 34.0], "stalk_cone_deg": 30.0,
	"flee_m": 24.0, "flee_to_m": 28.0, "lost_m": 55.0, "reappear_s": [30.0, 120.0],
	"story_mq_flee_m": 5.0, "story_mq_approach_m": 0.0, "story_cucos_flee_m": 16.0,
	"story_cucos_approach_m": 22.0, "story_seen_close_m": 10.0, "story_dart_m": 22.0,
	"story_run_mps": 7.5, "story_shuffle_s": [6.0, 11.0], "relocate_after_s": 1.0, "flee_mps": 7.5,
}
var mode := "stalk"
var player: Node3D
var fig: Node3D            # scripts/rougarou.gd
var rows: PackedStringArray
var map_scale := 2.0
var map_origin := Vector2(148, 100)
var state := "hidden"
var timer := 0.0
var looked := 0.0
var unseen := 0.0
var path := []             # Vector3 waypoints while bolting
var rng := RandomNumberGenerator.new()
var force := ""            # "", "now", "behind"
var sightings := 0
var disabled := false

func _ready() -> void:
	rng.randomize()
	if FileAccess.file_exists(CFG):
		var j = JSON.parse_string(FileAccess.get_file_as_string(CFG))
		if j is Dictionary:
			for k in j: cfg[k] = j[k]
	rows = player.walk_rows
	map_scale = player.map_scale
	map_origin = player.map_origin
	fig = load("res://scripts/rougarou.gd").new()
	fig.visible = false
	add_child(fig)
	if force == "0":
		disabled = true
	mode = str(cfg.mode)
	if force in ["now", "behind", "sightings"]:
		mode = "sightings"
	elif force == "stalk":
		mode = "stalk"
	elif force in ["s1", "s2", "s3"]:
		mode = "story"
	if mode == "story":
		_story_ready()
		set_process(true)
		return
	if mode == "stalk":
		timer = float(cfg.stalk_first_s)
	else:
		timer = 0.0 if force in ["now", "behind"] else float(cfg.first_sighting_s)
	set_process(true)

func _process(dt: float) -> void:
	if disabled or player == null:
		return
	if mode == "stalk":
		_stalk(dt)
		return
	if mode == "story":
		_story(dt)
		return
	match state:
		"hidden":
			timer -= dt
			if timer <= 0.0:
				var behind = force == "behind" or (force != "now" and sightings > 0 and rng.randf() < float(cfg.behind_chance))
				force = ""
				if behind:
					_place_behind()
				else:
					_place_far()
		"far", "behind":
			timer -= dt
			fig.watch = player.global_position + Vector3(0, 1.5, 0)
			if _seen():
				looked += dt
				unseen = 0.0
				var need = float(cfg.behind_look_to_bolt_s if state == "behind" else cfg.look_to_bolt_s)
				if looked >= need:
					_bolt()
			else:
				looked = max(0.0, looked - dt * 0.5)
				if timer <= 0.0:
					_vanish()
		"bolt":
			_run(dt)
			if not _seen():
				unseen += dt
				if unseen > float(cfg.gone_after_unseen_s):
					_vanish()
			else:
				unseen = 0.0
			if path.is_empty():
				_vanish()

# ------------------------------------------------------------------ placing
func _place_far() -> void:
	var lo = float(cfg.far_m[0]); var hi = float(cfg.far_m[1])
	var pp = player.global_position
	var fwd = -player.global_transform.basis.z
	var best = []
	var fallback = []
	for ty in rows.size():
		for tx in rows[ty].length():
			if rows[ty][tx] != "1": continue
			var c = _centre(tx, ty)
			var d = Vector2(c.x - pp.x, c.z - pp.z).length()
			if d < lo or d > hi: continue
			if not player._free(c.x, c.z): continue      # not inside a bench, planter or kiosk
			if not _los(pp, c): continue
			var behind = Vector3(c.x - pp.x, 0, c.z - pp.z).normalized().dot(fwd) < -0.2
			(best if behind else fallback).append(c)
	var pool = best if (best.size() > 0 and rng.randf() < 0.7) else fallback
	if pool.is_empty(): pool = best
	if pool.is_empty():
		# nowhere far enough in sight (a small store, say): try again shortly
		timer = 8.0
		return
	var c = pool[rng.randi() % pool.size()]
	_show(c, pp, "far", float(cfg.stand_timeout_s))

func _place_behind() -> void:
	var pp = player.global_position
	var back = player.global_transform.basis.z   # +z of the player is behind the camera
	var d = float(cfg.behind_m)
	var c = pp + back * d
	if not player._free(c.x, c.z):
		# no floor behind (a wall, a bench): a far sighting instead
		_place_far()
		return
	_show(c, pp, "behind", float(cfg.behind_timeout_s))

func _show(c: Vector3, face: Vector3, st: String, life: float) -> void:
	fig.position = Vector3(c.x, 0, c.z)
	fig.look_at(Vector3(face.x, 0, face.z), Vector3.UP)   # -Z toward the player
	fig.hunch = 0.9 if st == "far" else 0.8
	fig.gait = 0.0
	fig.visible = true
	state = st; timer = life; looked = 0.0; unseen = 0.0
	sightings += 1
	print("rougarou: ", st, " at ", fig.position)

func _vanish() -> void:
	fig.visible = false
	fig.gait = 0.0
	state = "hidden"
	var b = cfg.between_sightings_s
	timer = rng.randf_range(float(b[0]), float(b[1]))
	path = []

# ------------------------------------------------------------------ seeing
func _seen() -> bool:
	var pp = player.global_position + Vector3(0, 1.62, 0)
	var ep = fig.position + Vector3(0, 1.4, 0)
	var to = ep - pp
	var d = to.length()
	if d > float(cfg.see_m): return false
	var cam: Camera3D = player.cam
	var fwd = -(cam.global_transform.basis.z if cam else player.global_transform.basis.z)
	var ang = rad_to_deg(acos(clamp(fwd.dot(to / d), -1.0, 1.0)))
	if ang > float(cfg.see_cone_deg): return false
	return _los(player.global_position, fig.position)

## Line of sight along the walk grid: every metre between a and b is a walkable tile.
func _los(a: Vector3, b: Vector3) -> bool:
	var d = Vector2(b.x - a.x, b.z - a.z)
	var n = int(ceil(d.length() / 1.0))
	for i in range(1, n):
		var p = Vector2(a.x, a.z) + d * (float(i) / n)
		if not _walk(p.x, p.y): return false
	return true

# ------------------------------------------------------------------ the grid
func _walk(x: float, z: float) -> bool:
	var tx = int(floor(x / map_scale + map_origin.x))
	var ty = int(floor(z / map_scale + map_origin.y))
	if ty < 0 or ty >= rows.size() or tx < 0 or tx >= rows[ty].length(): return false
	return rows[ty][tx] == "1"

func _tile(p: Vector3) -> Vector2i:
	return Vector2i(int(floor(p.x / map_scale + map_origin.x)), int(floor(p.z / map_scale + map_origin.y)))

func _centre(tx: int, ty: int) -> Vector3:
	return Vector3((tx + 0.5 - map_origin.x) * map_scale, 0, (ty + 0.5 - map_origin.y) * map_scale)

# ------------------------------------------------------------------ bolting
## Breadth-first over the grid from the figure's tile; the target is the nearest tile that is at
## least hide_m from the player and out of their line of sight: round a corner, into a side hall
## or an open store. If there is none, the farthest reachable tile.
func _bolt() -> void:
	var start = _tile(fig.position)
	var pp = player.global_position
	var prev = {start: null}
	var queue = [start]
	var qi = 0
	var target = null
	var far_t = start; var far_d = 0.0
	while qi < queue.size():
		var t = queue[qi]; qi += 1
		var c = _centre(t.x, t.y)
		var d = Vector2(c.x - pp.x, c.z - pp.z).length()
		if d > far_d: far_d = d; far_t = t
		if d >= float(cfg.hide_m) and not _los(pp, c):
			target = t; break
		for nb in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var u = t + nb
			if prev.has(u): continue
			if u.y < 0 or u.y >= rows.size() or u.x < 0 or u.x >= rows[u.y].length(): continue
			if rows[u.y][u.x] != "1": continue
			prev[u] = t
			queue.append(u)
	if target == null: target = far_t
	path = []
	var t = target
	while t != null and t != start:
		path.push_front(_centre(t.x, t.y))
		t = prev[t]
	if path.is_empty():
		_vanish(); return
	state = "bolt"; fig.gait = 1.0; fig.hunch = 0.6; fig.watch = Vector3.INF; unseen = 0.0
	print("rougarou: bolts, ", path.size(), " tiles")

func _run(dt: float) -> void:
	if path.is_empty(): return
	var goal = path[0]
	var to = goal - fig.position; to.y = 0
	var step = float(cfg.bolt_mps) * dt
	if to.length() <= step:
		fig.position = goal; path.pop_front()
		if path.is_empty(): return
		goal = path[0]; to = goal - fig.position; to.y = 0
	var dir = to.normalized()
	fig.position += dir * step
	# turn into the run smoothly
	var want = atan2(-dir.x, -dir.z)
	fig.rotation.y = lerp_angle(fig.rotation.y, want, min(1.0, dt * 10.0))

# ------------------------------------------------------------------ stalk mode
func _stalk(dt: float) -> void:
	match state:
		"hidden":
			timer -= dt
			if timer <= 0.0:
				if not _stalk_place():
					timer = 0.5
		"keep":
			fig.watch = player.global_position + Vector3(0, 1.5, 0)
			var d = _dist()
			if d < float(cfg.flee_m):
				_flee()
				return
			var lost = d > float(cfg.lost_m) or not _los(player.global_position, fig.position) or _angle() > 75.0
			unseen = unseen + dt if lost else 0.0
			if unseen > float(cfg.relocate_after_s):
				if not _stalk_place():
					# no spot far enough ahead (a short hall, a store): it waits out of sight
					# rather than standing behind the player, and tries again every half second
					fig.visible = false; state = "hidden"; timer = 0.5; unseen = 0.0
		"run":
			# it runs until it is out of sight, then stays away 30 s – 2 min (reappear_s, a new
			# random wait each time) and comes back ahead of the player (Steven, Oct 15)
			_run_at(dt, float(cfg.flee_mps))
			var gone = not _los(player.global_position, fig.position) or _angle() > 75.0
			unseen = unseen + dt if gone else 0.0
			if path.is_empty() or unseen > 0.4:
				fig.visible = false; fig.gait = 0.0; path = []
				state = "hidden"
				timer = rng.randf_range(float(cfg.reappear_s[0]), float(cfg.reappear_s[1]))
				print("rougarou: gone for %.0f s" % timer)

func _dist() -> float:
	var pp = player.global_position
	return Vector2(fig.position.x - pp.x, fig.position.z - pp.z).length()

## Degrees between where the camera looks (flattened) and the figure.
func _angle(c = null) -> float:
	var pp = player.global_position
	var to = (c if c != null else fig.position) - pp; to.y = 0
	if to.length() < 0.01: return 0.0
	var cam: Camera3D = player.cam
	var fwd = -(cam.global_transform.basis.z if cam else player.global_transform.basis.z); fwd.y = 0
	return rad_to_deg(fwd.normalized().angle_to(to.normalized()))

## Stands it ahead of the player: the tile in range and in sight nearest the middle of the view,
## widening the search if the view is short (a store, a corner). False if nowhere fits.
func _stalk_place() -> bool:
	var pp = player.global_position
	var ranges = [[float(cfg.stalk_m[0]), float(cfg.stalk_m[1]), float(cfg.stalk_cone_deg)],
		[float(cfg.flee_m) + 2.0, float(cfg.lost_m) - 5.0, float(cfg.stalk_cone_deg) * 1.6]]
	for r in ranges:
		var best = null; var best_a = 1e9
		for ty in rows.size():
			for tx in rows[ty].length():
				if rows[ty][tx] != "1": continue
				var c = _centre(tx, ty)
				var d = Vector2(c.x - pp.x, c.z - pp.z).length()
				if d < r[0] or d > r[1]: continue
				var a = _angle(c)
				if a > r[2]: continue
				# the middle of the view first, then the far end of the range
				var score = a - d * 0.15
				if score >= best_a: continue
				if not player._free(c.x, c.z): continue
				if not _los(pp, c): continue
				best = c; best_a = score
		if best != null:
			_show(best, pp, "keep", 0.0)
			fig.hunch = 0.9
			unseen = 0.0
			return true
	return false

## Runs from the player along the grid: the nearest tile (from the figure) at least flee_to_m from
## the player that they can still see; else one out of sight; else the farthest reachable.
func _flee() -> void:
	var start = _tile(fig.position)
	var pp = player.global_position
	var prev = {start: null}
	var queue = [start]; var qi = 0
	var seen_t = null; var hid_t = null
	var far_t = start; var far_d = 0.0
	while qi < queue.size() and qi < 6000:
		var t = queue[qi]; qi += 1
		var c = _centre(t.x, t.y)
		var d = Vector2(c.x - pp.x, c.z - pp.z).length()
		if d > far_d: far_d = d; far_t = t
		if d >= float(cfg.flee_to_m) and player._free(c.x, c.z):
			# out of sight first: it disappears round a corner or into a store
			if not _los(pp, c):
				hid_t = t; break
			elif seen_t == null:
				seen_t = t
		for nb in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var u = t + nb
			if prev.has(u): continue
			if u.y < 0 or u.y >= rows.size() or u.x < 0 or u.x >= rows[u.y].length(): continue
			if rows[u.y][u.x] != "1": continue
			# never run through the player
			var uc = _centre(u.x, u.y)
			if Vector2(uc.x - pp.x, uc.z - pp.z).length() < 3.0: continue
			prev[u] = t
			queue.append(u)
	var target = hid_t if hid_t != null else (seen_t if seen_t != null else far_t)
	path = []
	var t = target
	while t != null and t != start:
		path.push_front(_centre(t.x, t.y))
		t = prev[t]
	if path.is_empty():
		return
	state = "run"; fig.gait = 1.0; fig.hunch = 0.6; fig.watch = Vector3.INF
	print("rougarou: flees ", path.size(), " tiles, ", "out of sight" if hid_t != null else "in sight")

func _run_at(dt: float, mps: float) -> void:
	var keep = cfg.bolt_mps
	cfg.bolt_mps = mps
	_run(dt)
	cfg.bolt_mps = keep

# ------------------------------------------------------------------ story mode
const PC_RECT = Rect2(-110.0, 61.0, 8.0, 39.0)            # Pocket Change, past the threshold (x, z)
const MQ_POS = Vector3(-95.5, 0.4, 47.45)                  # Merry-Go-Round's right-hand window form
const MQ_RUN = [Vector3(-95.5, 0, 46.2), Vector3(-96.8, 0, 41.0), Vector3(-97.5, 0, 31.0)]
const CUCOS_POS = Vector3(29.0, 0, -89.5)                  # in front of Cucos' doors
const CUCOS_RUN = [Vector3(29.0, 0, -86.8), Vector3(29.0, 0, -83.0), Vector3(28.5, 0, -77.0)]
const WOOL = Rect2(-45.0, -13.0, 34.0, 34.0)               # Woolworth's floor (x, z)
const WOOL_BACK = Rect2(-45.0, -13.0, 19.0, 34.0)          # its back half

var stage := 0
var pc_in := false
var since := 0.0           # seconds in this stage's current pose
var last_pp := Vector3.INF
var approach := 0.0        # smoothed speed of the player toward it, m/s
var wool_obs := []         # obstacle rects inside Woolworth, for line of sight
var shuffle := 0.0

func _story_ready() -> void:
	var saved = _story_load()
	if saved != "":
		var v = saved.split(",")
		stage = int(v[0]); pc_in = v.size() > 1 and v[1] == "1"
	if force in ["s1", "s2", "s3"]:
		stage = int(force.substr(1)); pc_in = false
	for o in player.obstacles:
		if o.size() == 5 and o[0] is String and o[0] == "rect":
			if Rect2(o[1], o[2], o[3] - o[1], o[4] - o[2]).intersects(WOOL.grow(1.0)):
				wool_obs.append(Rect2(o[1], o[2], o[3] - o[1], o[4] - o[2]))
	state = "hidden"
	_story_enter()

func _story_load() -> String:
	if OS.has_feature("web"):
		return str(JavaScriptBridge.eval("(function(){try{return sessionStorage.getItem('mall-rg')||''}catch(e){return ''}})()", true))
	return str(Engine.get_meta("mall_rg", ""))

func _story_save() -> void:
	var v = "%d,%d" % [stage, 1 if pc_in else 0]
	if OS.has_feature("web"):
		JavaScriptBridge.eval("try{sessionStorage.setItem('mall-rg','%s')}catch(e){}" % v, true)
	else:
		Engine.set_meta("mall_rg", v)

func _wing_ok(w: int) -> bool:
	return player.wing == 0 or player.wing == w

## Shows the figure for this stage (if it belongs to this wing) and the window form for stage 0.
func _story_enter() -> void:
	var mq = get_parent().get_node_or_null("Dynamic/dyn_rg_mannequin")
	if mq: mq.visible = stage == 0
	fig.visible = false; fig.still = false; fig.gait = 0.0; fig.watch = Vector3.INF
	path = []; since = 0.0; approach = 0.0; state = "hidden"
	match stage:
		1:
			if _wing_ok(2):
				fig.position = MQ_POS
				fig.look_at(MQ_POS + Vector3(0, 0, 5), Vector3.UP)
				fig.hunch = 0.35; fig.still = true; fig.visible = true; state = "stand"
		2:
			if _wing_ok(1):
				fig.position = CUCOS_POS
				fig.look_at(CUCOS_POS + Vector3(0, 0, -5), Vector3.UP)
				fig.hunch = 0.9; fig.visible = true; state = "stand"
		3:
			if _wing_ok(1):
				var spots = _wool_spots(WOOL_BACK)
				if not spots.is_empty():
					var c = spots[rng.randi() % spots.size()]
					fig.position = c; fig.hunch = 1.0; fig.visible = true; state = "lurk"
					fig.look_at(Vector3(-10, 0, c.z), Vector3.UP)
					shuffle = rng.randf_range(float(cfg.story_shuffle_s[0]), float(cfg.story_shuffle_s[1]))
	print("rougarou story: stage ", stage, " ", state)

func _story_next(st: int) -> void:
	stage = st
	_story_save()
	_story_enter()

func _story(dt: float) -> void:
	var pp = player.global_position
	# how fast the player closes on it
	if last_pp != Vector3.INF and fig.visible and dt > 0.0:
		var d0 = Vector2(fig.position.x - last_pp.x, fig.position.z - last_pp.z).length()
		var d1 = Vector2(fig.position.x - pp.x, fig.position.z - pp.z).length()
		approach = lerp(approach, (d0 - d1) / dt, min(1.0, dt * 4.0))
	last_pp = pp
	since += dt
	# Pocket Change arms it, from idle
	if stage == 0 and _wing_ok(2):
		var inside = PC_RECT.has_point(Vector2(pp.x, pp.z))
		if inside and not pc_in:
			pc_in = true; _story_save()
		elif pc_in and pp.z < 60.0:
			pc_in = false
			_story_next(1)
			return
	match state:
		"stand":
			var d = _dist()
			var near = float(cfg.story_mq_flee_m if stage == 1 else cfg.story_cucos_flee_m)
			var far = float(cfg.story_mq_approach_m if stage == 1 else cfg.story_cucos_approach_m)
			# the head follows you once you are near; the mannequin pose otherwise does not move
			fig.watch = pp + Vector3(0, 1.5, 0) if d < far + 6.0 else Vector3.INF
			if since > 1.5 and (d < near or (d < far and approach > 1.0)):
				path = (MQ_RUN if stage == 1 else CUCOS_RUN).duplicate()
				fig.position.y = 0.0; fig.still = false; fig.gait = 1.0; fig.hunch = 0.6; fig.watch = Vector3.INF
				state = "run_out"; since = 0.0
				print("rougarou story: runs (stage ", stage, ", d %.1f)" % d)
		"run_out":
			_run_at(dt, float(cfg.story_run_mps))
			if path.is_empty() or since > 4.0:
				_story_next(stage + 1)
		"lurk":
			var d = _dist()
			var seen = _seen_obs()
			fig.watch = pp + Vector3(0, 1.5, 0)
			shuffle -= dt
			if seen and d < float(cfg.story_seen_close_m):
				# a close look: it runs and is gone; the route ends
				_dart(true)
			elif (seen and d < float(cfg.story_dart_m)) or d < 8.0 or shuffle <= 0.0:
				_dart(false)
		"dart":
			_run_at(dt, float(cfg.story_run_mps))
			if path.is_empty():
				state = "lurk"; fig.gait = 0.0; fig.hunch = 1.0
				shuffle = rng.randf_range(float(cfg.story_shuffle_s[0]), float(cfg.story_shuffle_s[1]))
		"gone_run":
			_run_at(dt, float(cfg.story_run_mps))
			if path.is_empty() or (since > 0.6 and not _seen_obs()) or since > 4.0:
				_story_next(0)

## Seen, with Woolworth's shelves in the way: in the view cone and nothing between.
func _seen_obs() -> bool:
	if _angle() > float(cfg.see_cone_deg) + 10.0: return false
	return _los_obs(player.global_position, fig.position)

func _los_obs(a: Vector3, b: Vector3) -> bool:
	var d = Vector2(b.x - a.x, b.z - a.z)
	var n = int(ceil(d.length() / 0.6))
	for i in range(1, n):
		var p = Vector2(a.x, a.z) + d * (float(i) / n)
		if not _walk(p.x, p.y): return false
		for r in wool_obs:
			if r.has_point(p): return false
	return true

## Free floor spots in Woolworth (tile centres clear of shelves), within the rect.
func _wool_spots(area: Rect2) -> Array:
	var out = []
	for ty in rows.size():
		for tx in rows[ty].length():
			if rows[ty][tx] != "1": continue
			var c = _centre(tx, ty)
			if area.has_point(Vector2(c.x, c.z)) and player._free(c.x, c.z):
				out.append(c)
	return out

## Runs to the nearest free Woolworth tile the player cannot see, at least 10 m from them
## (gone = true: then vanish and end the route). Paths keep to free tiles inside the store.
func _dart(gone: bool) -> void:
	var start = _tile(fig.position)
	var pp = player.global_position
	var prev = {start: null}
	var queue = [start]; var qi = 0
	var target = null
	var far_t = start; var far_d = 0.0
	while qi < queue.size() and qi < 1500:
		var t = queue[qi]; qi += 1
		var c = _centre(t.x, t.y)
		var d = Vector2(c.x - pp.x, c.z - pp.z).length()
		if d > far_d: far_d = d; far_t = t
		# a real scamper: at least 5 m from where it was, 10 m from you, out of your sight
		if c.distance_to(fig.position) >= 5.0 and d >= 10.0 and not _los_obs(pp, c):
			target = t; break
		for nb in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var u = t + nb
			if prev.has(u): continue
			var uc = _centre(u.x, u.y)
			if not WOOL.has_point(Vector2(uc.x, uc.z)): continue
			if not player._free(uc.x, uc.z): continue
			if Vector2(uc.x - pp.x, uc.z - pp.z).length() < 3.0: continue
			prev[u] = t
			queue.append(u)
	if target == null: target = far_t
	path = []
	var t = target
	while t != null and t != start:
		path.push_front(_centre(t.x, t.y))
		t = prev[t]
	fig.gait = 1.0; fig.hunch = 0.7; fig.watch = Vector3.INF; since = 0.0
	state = "gone_run" if gone else "dart"
	if path.is_empty() and gone:
		_story_next(0)
	elif path.is_empty():
		state = "lurk"; fig.gait = 0.0; shuffle = 3.0
	print("rougarou story: ", "gone" if gone else "ducks", " (", path.size(), " tiles)")
