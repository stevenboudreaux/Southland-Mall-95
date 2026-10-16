## The shoppers: the mall's crowd (Steven, Oct 15 2026: "an engine for NPCs where they walk through
## the mall on the sides, not in the middle of the walkways, and go into stores").
##
## One node under the wing, made by player.gd, that owns every shopper (a small Shopper record plus
## a NpcBody). There are no physics bodies: shoppers walk the same 2 m walk grid as the player and
## the Rougarou, split into 1 m cells with the wing's columns, benches and planters closed off.
##
## Lanes. A distance-to-wall field over the cells gives every cell a path cost: cheapest 1.5–4 m
## from a wall, dearer toward the middle of a hall, dear right against a wall. AStarGrid2D (C++)
## finds routes with those costs, so people keep to the sides on their own, and a keep-right
## nudge while following the route makes the two directions pass each other like real mall
## traffic. Courts are wide, so their middles cost most and people round them along the edges.
##
## Goals (scripts/npcs.json weights): a store with an open interior (walk in through its door,
## stand at two or three spots inside looking around, walk out), a closed store's window (stand
## facing it a few seconds), or a far point of the hall. Then the next goal. The shape follows the
## Rembot Games tutorial Steven sent: a tiny state machine (walk / dwell) with a one-shot timer, the
## animation chosen on state entry, and a `_decide()` hook that picks the next goal; its navmesh
## agent is replaced by the grid, and its stats hook is where shopper personality can go later.
##
## Spawning happens out of the player's sight (grid line of sight, like the Rougarou), the count
## follows the clock in scripts/lighting.json (thin at 7 am and 9 pm, full at noon–7 pm), and a
## shopper far away and unseen for a while is quietly re-placed elsewhere. NPCs never block the
## player; they step aside and slow for the player and for each other.
## URL: ?npcs=0 turns them off, ?npcs=40 sets the count (tests, screenshots).
extends Node

const CFG := "res://scripts/npcs.json"
const LAYOUT := "res://layout_mall.json"
var cfg := {
	"count": 24, "hours": {"6": 0.0, "8": 0.2, "10": 0.6, "12": 1.0, "17": 1.0, "19": 0.7, "20": 0.4, "21": 0.15, "22": 0.0},
	"speed_mps": [1.0, 1.45], "lane_m": [1.5, 4.0], "centre_penalty": 0.5, "wall_hug_penalty": 1.6,
	"keep_right_m": 0.5, "separation_m": 1.3, "player_m": 1.8, "goals": {"store": 0.5, "window": 0.25, "hall": 0.25},
	"shop_s": [20.0, 60.0], "window_s": [5.0, 15.0], "pause_s": [1.0, 4.0], "store_max_m": 70.0,
	"spawn_min_m": 22.0, "see_m": 70.0, "see_cone_deg": 70.0, "recycle_unseen_s": 8.0, "recycle_m": 55.0,
	"lod_anim_m": 45.0, "groups": {"civ": 1.0, "police": 0.0, "fire": 0.0, "doctor": 0.0, "hazmat": 0.0},
	"exclude": [], "retire_after_goals": [4, 9],
	"self_light_day": 0.18, "self_light_night": 0.3, "mannequin_skins": ["Ch36"], "mannequin_pose": ["idle", 0.4],
	"types": {
		"browser": {"w": 0.4, "speed_mps": [1.1, 1.5], "goals": {"store": 0.15, "window": 0.45, "hall": 0.4}, "shop_s": [8.0, 20.0]},
		"shopper": {"w": 0.4, "speed_mps": [0.95, 1.35], "goals": {"store": 0.5, "window": 0.25, "hall": 0.25}, "shop_s": [20.0, 50.0]},
		"heavy": {"w": 0.2, "speed_mps": [0.85, 1.2], "goals": {"store": 0.75, "window": 0.15, "hall": 0.1}, "shop_s": [35.0, 80.0]}},
	"arcade_fill": 0.5, "arcade_mods": ["video", "driver", "crane"], "arcade_hands_m": [0.42, 0.97, 0.16], "arcade_yield_m": 0.9,
}
var players := []             # arcade: {body, pos, face, left, right, t}
var mannequins := []          # frozen bodies in the windows (gen/w*/mannequins.json)
var light_mode := ""
var player: Node3D
var force := ""              # ?npcs=
var rows: PackedStringArray
var map_scale := 2.0
var map_origin := Vector2(148, 100)
var cell := 1.0
var W := 0
var H := 0
var oc := Vector2.ZERO        # cell offset of world origin
var open := PackedByteArray()
var wdist := PackedInt32Array()
var grid: AStarGrid2D
var skins := []
var weights := []             # cumulative
var stores := []              # {door, n, spots, name}
var windows := []             # {door, n, spot, name}
var hall_cells := []          # open cells 2+ m from walls (Vector2i)
var shoppers := []
var rt = null
var want := 0
var tick := 0.0
var rng := RandomNumberGenerator.new()
var disabled := false
var spawn_all_now := false   # tests: fill the mall at once, in sight too

class Shopper:
	var body: NpcBody
	var pos := Vector3.ZERO
	var path := PackedVector3Array()
	var pi := 0
	var state := "dwell"
	var timer := 1.0
	var speed := 1.2
	var goal := {}          # type, spots, i, face
	var unseen := 0.0
	var stuck := 0.0
	var goals := 0
	var retire := 6
	var dwell_clip := "idle"
	var type := {}          # one of cfg.types

func _ready() -> void:
	rng.randomize()
	if FileAccess.file_exists(CFG):
		var j = JSON.parse_string(FileAccess.get_file_as_string(CFG))
		if j is Dictionary:
			for k in j: cfg[k] = j[k]
	if force == "0":
		disabled = true; return
	if force.is_valid_int():
		cfg.count = int(force)
	rows = player.walk_rows
	map_scale = player.map_scale
	map_origin = player.map_origin
	_build_grid()
	_load_skins()
	_load_places()
	rt = get_tree().current_scene.get_node_or_null("Runtime")
	_place_mannequins()
	_place_players()
	print("npcs: grid %dx%d, %d open cells, %d stores, %d windows, %d skins" % [W, H, _count_open(), stores.size(), windows.size(), skins.size()])
	set_process(true)

# ------------------------------------------------------------------ the grid
## 1 m cells from the wing's 2 m walk tiles, with the columns and fixtures closed off, a
## distance-to-wall field, and an AStarGrid2D whose costs make the sides of a hall the cheap way.
func _build_grid() -> void:
	cell = map_scale * 0.5
	W = rows[0].length() * 2 if rows.size() > 0 else 0
	H = rows.size() * 2
	oc = map_origin * 2.0
	open.resize(W * H); open.fill(0)
	var obs: Array = player.obstacles + player.fx_obstacles
	for cy in range(H):
		var r: String = rows[cy / 2]
		for cx in range(W):
			if r[cx / 2] != "1": continue
			var c := _centre(Vector2i(cx, cy))
			var blocked := false
			for o in obs:
				if o.size() == 3 and not (o[0] is String):
					if Vector2(c.x - o[0], c.z - o[1]).length() < float(o[2]) + 0.45: blocked = true; break
				elif o[0] == "rect":
					if c.x > o[1] - 0.4 and c.x < o[3] + 0.4 and c.z > o[2] - 0.4 and c.z < o[4] + 0.4: blocked = true; break
			if not blocked: open[cy * W + cx] = 1
	# distance to the nearest closed cell (4-neighbour BFS from every closed cell)
	wdist.resize(W * H); wdist.fill(-1)
	var q := PackedInt32Array(); var qi := 0
	for i in range(W * H):
		if open[i] == 0: wdist[i] = 0; q.append(i)
	while qi < q.size():
		var i := q[qi]; qi += 1
		var x := i % W; var y := i / W
		for nb: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var ux: int = x + nb.x; var uy: int = y + nb.y
			if ux < 0 or uy < 0 or ux >= W or uy >= H: continue
			var u: int = uy * W + ux
			if wdist[u] < 0: wdist[u] = wdist[i] + 1; q.append(u)
	grid = AStarGrid2D.new()
	grid.region = Rect2i(0, 0, W, H)
	grid.cell_size = Vector2(1, 1)
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_OCTILE
	grid.jumping_enabled = false
	grid.update()
	var lane: Array = cfg.lane_m
	var lo := int(round(float(lane[0]) / cell)); var hi := int(round(float(lane[1]) / cell))
	for cy in range(H):
		for cx in range(W):
			var i := cy * W + cx
			var p := Vector2i(cx, cy)
			if open[i] == 0:
				grid.set_point_solid(p, true); continue
			var d := wdist[i]
			var w := 1.0
			if d < lo: w = float(cfg.wall_hug_penalty)
			elif d > hi: w = minf(1.0 + float(cfg.centre_penalty) * float(d - hi), 4.0)
			grid.set_point_weight_scale(p, w)
			if d >= lo: hall_cells.append(p)

func _count_open() -> int:
	var n := 0
	for i in range(open.size()): n += open[i]
	return n

func _cell(p: Vector3) -> Vector2i:
	return Vector2i(int(floor(p.x / cell + oc.x)), int(floor(p.z / cell + oc.y)))

func _centre(c: Vector2i) -> Vector3:
	return Vector3((c.x + 0.5 - oc.x) * cell, 0.0, (c.y + 0.5 - oc.y) * cell)

func _open(p: Vector3) -> bool:
	var c := _cell(p)
	if c.x < 0 or c.y < 0 or c.x >= W or c.y >= H: return false
	return open[c.y * W + c.x] == 1

func _open_c(c: Vector2i) -> bool:
	if c.x < 0 or c.y < 0 or c.x >= W or c.y >= H: return false
	return open[c.y * W + c.x] == 1

## Straight line over open cells (the Rougarou's test, on the finer grid).
func _los(a: Vector3, b: Vector3) -> bool:
	var d := Vector2(b.x - a.x, b.z - a.z)
	var n := int(ceil(d.length() / 0.8))
	for i in range(1, n):
		var p: Vector2 = Vector2(a.x, a.z) + d * (float(i) / n)
		if not _open(Vector3(p.x, 0, p.y)): return false
	return true

# ------------------------------------------------------------------ skins and places
func _load_skins() -> void:
	var m := NpcBody.manifest()
	var total := 0.0
	for e in m.get("skins", []):
		if str(e.id) in cfg.exclude: continue
		var w := float(cfg.groups.get(str(e.group), 0.0))
		if w <= 0.0: continue
		skins.append(e); total += w; weights.append(total)

func _pick_skin() -> Dictionary:
	var r: float = rng.randf() * float(weights[weights.size() - 1])
	for i in range(weights.size()):
		if r <= weights[i]: return skins[i]
	return skins[skins.size() - 1]

## Store doors from the layout: a store is "open" when cells inside its door are walkable in this
## wing (the 3D interiors of design/godot-wings.md); otherwise its window is a place to stop.
func _load_places() -> void:
	if not FileAccess.file_exists(LAYOUT): return
	var lay = JSON.parse_string(FileAccess.get_file_as_string(LAYOUT))
	if not (lay is Dictionary): return
	var names: Dictionary = lay.get("stores", {})
	for e in lay.get("edges", []):
		if e.get("kind", "") != "store": continue
		var a: Array = e.a; var b: Array = e.b; var nn: Array = e.n
		var door := Vector3((float(a[0]) + float(b[0])) * 0.5, 0, (float(a[1]) + float(b[1])) * 0.5)
		var n := Vector3(float(nn[0]), 0, float(nn[1]))     # points into the hall
		if not _open(door + n * 1.2): continue              # not in this wing (or walled)
		var sid := str(e.get("store", ""))
		var name := str(names.get(sid, {}).get("name", sid))
		var spots := []
		var depth := float(e.get("depth", 6.0))
		for d in [2.5, 4.5, 7.0, 9.5]:
			if d > depth - 1.0: break
			var p: Vector3 = door - n * d
			if _open(p): spots.append(p)
			elif spots.size() > 0: break
		if spots.size() >= 1:
			stores.append({"door": door, "n": n, "spots": spots, "name": name})
		else:
			windows.append({"door": door, "n": n, "spot": door + n * 1.3, "name": name})

# ------------------------------------------------------------------ the crowd
func _process(dt: float) -> void:
	if disabled or player == null: return
	tick += dt
	if tick > 1.0:
		tick = 0.0
		_balance()
		_light_check()
	for s in shoppers:
		_step(s, dt)
	for p in players:
		_step_player(p, dt)

## Day or night changed: every body's own light follows (see NpcBody.set_self_light).
func _light_check() -> void:
	var m := "night"
	if rt and "mode" in rt: m = str(rt.mode)
	if m == light_mode: return
	light_mode = m
	var k := float(cfg.self_light_night if m == "night" else cfg.self_light_day)
	for s in shoppers: s.body.set_self_light(k)
	for b in mannequins: b.set_self_light(k)
	for p in players: p.body.set_self_light(k)

## Window mannequins: the spots the builder recorded (gen/w*/mannequins.json), each with a
## frozen body from `mannequin_skins`, facing out of the window the way the form did.
func _place_mannequins() -> void:
	var gen := str(get_tree().current_scene.get_meta("gen", "res://gen/"))
	var path := gen + "mannequins.json"
	if not FileAccess.file_exists(path): return
	var j = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (j is Dictionary): return
	var pool := []
	for e in NpcBody.manifest().get("skins", []):
		if str(e.id) in cfg.mannequin_skins: pool.append(e)
	if pool.is_empty(): return
	var i := 0
	for m in j.get("mannequins", []):
		var b := NpcBody.new()
		b.set_skin(pool[i % pool.size()]); i += 1
		add_child(b)
		var p: Array = m.pos
		b.position = Vector3(float(p[0]), float(p[1]), float(p[2]))
		b.scale = Vector3.ONE * float(m.get("s", 1.0))   # the skin scene carries its own metre scale
		var f: Array = m.face
		b.face(Vector3(float(f[0]), 0, float(f[1])))
		var pose: Array = cfg.mannequin_pose
		b.freeze(str(pose[0]), float(pose[1]) + 0.37 * (i % 3))
		mannequins.append(b)
	print("npcs: ", mannequins.size(), " window mannequins")

## Pocket Change: a share (`arcade_fill`) of the machines the builder recorded (gen/w*/machines.json)
## get a player standing at the stand spot, facing the screen, hands on the panel.
func _place_players() -> void:
	var gen := str(get_tree().current_scene.get_meta("gen", "res://gen/"))
	var path := gen + "machines.json"
	if not FileAccess.file_exists(path) or skins.is_empty(): return
	var j = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not (j is Dictionary): return
	var list := []
	for m in j.get("machines", []):
		if not (str(m.get("mod", "")) in cfg.arcade_mods): continue
		if str(m.get("mod", "")) == "driver" and str(m.get("opts", {}).get("kind", "")) == "racer": continue   # sit-down racers: no seated clip yet
		list.append(m)
	list.shuffle()
	var n := int(round(list.size() * float(cfg.arcade_fill)))
	var hm: Array = cfg.arcade_hands_m
	var deck := skins.duplicate(); deck.shuffle()    # dealt round, so neighbours differ
	for i in range(mini(n, list.size())):
		var m: Dictionary = list[i]
		var b := NpcBody.new()
		b.set_skin(deck[i % deck.size()])
		add_child(b)
		var pa: Array = m.pos; var fa: Array = m.face
		var pos := Vector3(float(pa[0]), 0, float(pa[2]))
		var face := Vector3(float(fa[0]), 0, float(fa[1])).normalized()
		b.position = pos
		b.face(face)
		b.freeze("idle", [0.3, 0.9, 1.5][i % 3])   # calm frames of the idle, varied
		var right := face.cross(Vector3.UP)
		var panel := pos + face * float(hm[0]) + Vector3(0, float(hm[1]), 0)
		players.append({"body": b, "pos": pos, "face": face, "left": panel - right * float(hm[2]), "right": panel + right * float(hm[2]),
			"t": rng.randf() * 10.0, "tap": 0.0, "aside": false})
	print("npcs: ", players.size(), " of ", list.size(), " machines have players")

## A player at a machine: hands on the stick and the buttons, with a little life in them; steps
## aside when the real player wants that machine.
func _step_player(p: Dictionary, dt: float) -> void:
	var b: NpcBody = p.body
	var d: float = Vector2(player.global_position.x - p.pos.x, player.global_position.z - p.pos.z).length()
	b.visible = d < float(cfg.see_m)
	if not b.visible: return
	p.t += dt
	var want_aside: bool = d < float(cfg.arcade_yield_m)
	if want_aside != p.aside:
		p.aside = want_aside
		var right: Vector3 = p.face.cross(Vector3.UP)
		b.position = p.pos + (right * 0.9 if want_aside else Vector3.ZERO)
	if p.aside or not bool(cfg.get("arcade_hands", true)):
		b.hands_off(); return
	# joystick: slow wander; buttons: taps every so often
	var right: Vector3 = p.face.cross(Vector3.UP)
	var jx := sin(p.t * 2.3) * 0.03 + sin(p.t * 5.1) * 0.015
	var jz := cos(p.t * 1.7) * 0.02
	p.tap -= dt
	var tap_y := 0.0
	if p.tap <= 0.0:
		p.tap = rng.randf_range(0.15, 0.9)
	elif p.tap > 0.08: tap_y = 0.0
	else: tap_y = -0.025
	b.hands_to(p.left + right * jx + p.face * jz, p.right + Vector3(0, tap_y, 0) + right * (0.03 if int(p.t * 3.0) % 2 == 0 else -0.03))

## How many people the hour wants, and spawn or retire unseen ones to get there.
func _balance() -> void:
	var h := 13.0
	if rt and "hour" in rt: h = float(rt.hour)
	var dens := _density(h)
	want = int(round(float(cfg.count) * dens))
	if force.is_valid_int() and int(force) > 0: want = int(force)
	var tries := 0
	while shoppers.size() < want and tries < (200 if spawn_all_now else 20):
		tries += 1
		if _spawn() == null: continue
	if shoppers.size() > want:
		for s in shoppers:
			if s.unseen > 2.0:
				_remove(s); break

func _density(h: float) -> float:
	var keys := []
	for k in cfg.hours: keys.append(float(k))
	keys.sort()
	if keys.is_empty(): return 1.0
	if h <= keys[0]: return float(cfg.hours[str(int(keys[0]))])
	for i in range(1, keys.size()):
		if h <= keys[i]:
			var a := float(cfg.hours[str(int(keys[i - 1]))]); var b := float(cfg.hours[str(int(keys[i]))])
			return lerpf(a, b, (h - keys[i - 1]) / (keys[i] - keys[i - 1]))
	return float(cfg.hours[str(int(keys[keys.size() - 1]))])

## Whether the player would see a point now: in front, within see_m, nothing in the way.
func _seen(p: Vector3) -> bool:
	var pp: Vector3 = player.global_position
	var to := p - pp; to.y = 0
	var d := to.length()
	if d > float(cfg.see_m): return false
	if d < 2.5: return true
	var fwd: Vector3 = -player.global_transform.basis.z; fwd.y = 0
	if fwd.normalized().dot(to / d) < cos(deg_to_rad(float(cfg.see_cone_deg))): return false
	return _los(pp, p)

## A new shopper somewhere the player cannot see.
func _spawn() -> Shopper:
	if skins.is_empty() or hall_cells.is_empty(): return null
	var p := Vector3.ZERO; var ok := false
	for i in range(30):
		var c: Vector2i = hall_cells[rng.randi() % hall_cells.size()]
		p = _centre(c)
		var d := Vector2(p.x - player.global_position.x, p.z - player.global_position.z).length()
		if d < (6.0 if spawn_all_now else float(cfg.spawn_min_m)): continue
		if not spawn_all_now and _seen(p): continue
		ok = true; break
	if not ok: return null
	var s := Shopper.new()
	s.body = NpcBody.new()
	s.body.set_skin(_pick_skin())
	add_child(s.body)
	s.body.set_self_light(float(cfg.self_light_night if light_mode == "night" else cfg.self_light_day))
	s.pos = p
	s.body.position = p
	s.body.face(Vector3(rng.randf() - 0.5, 0, rng.randf() - 0.5))
	s.type = _pick_type()
	var sp: Array = s.type.get("speed_mps", cfg.speed_mps)
	s.speed = rng.randf_range(float(sp[0]), float(sp[1]))
	var ra: Array = cfg.retire_after_goals
	s.retire = rng.randi_range(int(ra[0]), int(ra[1]))
	s.state = "dwell"; s.timer = rng.randf_range(0.2, 2.0); s.goal = {"type": "start"}
	shoppers.append(s)
	return s

## A browser, a shopper or a heavy shopper (scripts/npcs.json "types", weighted by "w").
func _pick_type() -> Dictionary:
	var total := 0.0
	for k in cfg.types: total += float(cfg.types[k].get("w", 1.0))
	var r := rng.randf() * total
	for k in cfg.types:
		r -= float(cfg.types[k].get("w", 1.0))
		if r <= 0.0: return cfg.types[k]
	return cfg.types[cfg.types.keys()[0]] if not cfg.types.is_empty() else {}

func _remove(s: Shopper) -> void:
	shoppers.erase(s)
	s.body.queue_free()

## The next goal: a store to go into, a window to look in, or a far point of the hall.
func _decide(s: Shopper) -> void:
	s.goals += 1
	var g: Dictionary = s.type.get("goals", cfg.goals)
	var r := rng.randf() * (float(g.store) + float(g.window) + float(g.hall))
	var target := Vector3.ZERO
	if r < float(g.store) and not stores.is_empty():
		var st: Dictionary = _near_place(stores, s.pos)
		s.goal = {"type": "store", "spots": st.spots, "i": 0, "name": st.name, "face": -st.n}
		target = st.spots[0]
	elif r < float(g.store) + float(g.window) and not windows.is_empty():
		var wn: Dictionary = _near_place(windows, s.pos)
		s.goal = {"type": "window", "name": wn.name, "face": -wn.n}
		target = wn.spot
	else:
		var c: Vector2i = hall_cells[rng.randi() % hall_cells.size()]
		for i in range(20):
			c = hall_cells[rng.randi() % hall_cells.size()]
			if _centre(c).distance_to(s.pos) > 15.0: break
		s.goal = {"type": "hall"}
		target = _centre(c)
	if not _route(s, target):
		s.state = "dwell"; s.timer = 1.0; s.goal = {"type": "start"}

## A random place among the nearer ones (within store_max_m when any are).
func _near_place(list: Array, from: Vector3) -> Dictionary:
	var near := []
	for p in list:
		if p.door.distance_to(from) < float(cfg.store_max_m) and p.door.distance_to(from) > 4.0: near.append(p)
	if near.is_empty(): near = list
	return near[rng.randi() % near.size()]

func _route(s: Shopper, target: Vector3) -> bool:
	var a := _cell(s.pos); var b := _cell(target)
	if not _open_c(a) or not _open_c(b): return false
	var ids := grid.get_id_path(a, b)
	if ids.size() < 2: return false
	s.path = PackedVector3Array()
	for i in range(1, ids.size()):
		s.path.append(_centre(ids[i]))
	s.path[s.path.size() - 1] = target
	s.pi = 0
	s.state = "walk"
	s.stuck = 0.0
	return true

func _arrive(s: Shopper) -> void:
	var g := s.goal
	match str(g.get("type", "")):
		"store":
			var spots: Array = g.spots
			var n := spots.size()
			s.state = "dwell"
			var ss: Array = s.type.get("shop_s", cfg.shop_s)
			s.timer = rng.randf_range(float(ss[0]), float(ss[1])) / n
			s.dwell_clip = "look" if rng.randf() < 0.6 else "idle"
			s.body.face(Vector3(rng.randf() - 0.5, 0, rng.randf() - 0.5))
			s.body.set_speed(0.0); s.body.play(s.dwell_clip)
		"window":
			s.state = "dwell"
			s.timer = rng.randf_range(float(cfg.window_s[0]), float(cfg.window_s[1]))
			s.body.face(g.face)
			s.body.set_speed(0.0); s.body.play("look")
		_:
			s.state = "dwell"
			s.timer = rng.randf_range(float(cfg.pause_s[0]), float(cfg.pause_s[1]))
			s.body.set_speed(0.0); s.body.play("idle" if rng.randf() < 0.7 else "look")

func _dwell_done(s: Shopper) -> void:
	var g := s.goal
	if g.get("type", "") == "store" and int(g.i) + 1 < g.spots.size():
		g.i = int(g.i) + 1
		if _route(s, g.spots[g.i]): return
	if s.goals >= s.retire and s.unseen > 1.0:
		_remove(s); return
	_decide(s)

func _step(s: Shopper, dt: float) -> void:
	# seen / unseen bookkeeping, far-away housekeeping
	var pp: Vector3 = player.global_position
	var d := Vector2(s.pos.x - pp.x, s.pos.z - pp.z).length()
	var seen := _seen(s.pos) if d < float(cfg.see_m) else false
	s.unseen = 0.0 if seen else s.unseen + dt
	if s.unseen > float(cfg.recycle_unseen_s) and d > float(cfg.recycle_m) and s.goals >= 1 and rng.randf() < dt * 0.1:
		_remove(s); return
	s.body.visible = d < float(cfg.see_m) + 10.0
	if s.body.ap:
		s.body.ap.active = d < float(cfg.lod_anim_m)
	match s.state:
		"dwell":
			s.timer -= dt
			if s.timer <= 0.0:
				_dwell_done(s)
		"walk":
			_follow(s, dt)

## Walk the route: keep right, step round people and the player, never through a wall.
func _follow(s: Shopper, dt: float) -> void:
	if s.pi >= s.path.size():
		_arrive(s); return
	var wp := s.path[s.pi]
	var to := wp - s.pos; to.y = 0
	var last := s.pi == s.path.size() - 1
	if to.length() < (0.35 if last else 0.6):
		s.pi += 1
		if s.pi >= s.path.size():
			s.pos = Vector3(wp.x, 0, wp.z) if last else s.pos
			s.body.position = s.pos
			_arrive(s); return
		wp = s.path[s.pi]; to = wp - s.pos; to.y = 0
	var dir := to.normalized()
	var want_dir := dir
	var spd := s.speed
	# keep right
	var right := dir.cross(Vector3.UP)
	if not last and _open(s.pos + right * float(cfg.keep_right_m)) and _open(wp + right * float(cfg.keep_right_m)):
		want_dir += right * 0.22
	# other shoppers
	var sep := float(cfg.separation_m)
	for o in shoppers:
		if o == s: continue
		var dv: Vector3 = s.pos - o.pos; dv.y = 0
		var dd: float = dv.length()
		if dd < sep and dd > 0.01:
			want_dir += dv / dd * (sep - dd) / sep * 0.9
			if dir.dot(-dv / dd) > 0.75 and dd < 1.0: spd *= 0.35
	# the player
	var pv := s.pos - player.global_position; pv.y = 0
	var pd := pv.length()
	if pd < float(cfg.player_m) and pd > 0.01:
		want_dir += pv / pd * (float(cfg.player_m) - pd) / float(cfg.player_m) * 1.5
		if dir.dot(-pv / pd) > 0.6: spd *= 0.3
	want_dir = want_dir.normalized()
	var step := want_dir * spd * dt
	var np := s.pos + step
	var moved := 0.0
	if _open(np):
		s.pos = np; moved = step.length()
	elif _open(s.pos + dir * spd * dt):
		s.pos += dir * spd * dt; moved = spd * dt
	else:
		s.stuck += dt
		if s.stuck > 1.5:
			s.stuck = 0.0
			if not _route(s, s.path[s.path.size() - 1]):
				_decide(s)
			return
	s.pos.y = 0
	s.body.position = s.pos
	s.body.face(want_dir, 9.0, dt)
	s.body.set_speed(moved / dt if dt > 0.0 else 0.0)
