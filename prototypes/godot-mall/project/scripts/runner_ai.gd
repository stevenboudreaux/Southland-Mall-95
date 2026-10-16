## The Runner (Steven, Oct 16 2026): the Rougarou's replacement, one of the window mannequins come
## to life. The featureless Ch36 figure (the one that stood in every window in Demo 36) on the
## Mixamo clips; two beats in Wing 2 for this build, the Sears side later.
##
##   1 mgr    he stands stock-still in Merry-Go-Round's right-hand window, where the Rougarou's
##            form used to be. Come within `mgr_trigger_m` and he startles ("surprised"), bursts
##            out of the door and runs east down the Concourse toward Payless, weaving round the
##            shoppers, takes a right at the court toward Dillard's and is gone through its
##            entry. He runs at `speed_x_sprint` × your sprint, so you can't keep up.
##   2 saadi  out of your sight he takes his place in Saadi's second window from the left (as
##            you face the store), frozen like the forms on the other platforms: from across the
##            hall he is just a mannequin. Come within `saadi_trigger_m` of that window and he
##            bursts out the door, runs past you, back across the court and along the Concourse
##            into Wicks 'N' Sticks, and vanishes through its back door.
##   3 done   nothing more in this build.
## The beat survives crossing wings and reloads in the same tab (sessionStorage "mall-runner").
## Merry-Go-Round's old stand-in form (dyn_rg_mannequin) is hidden: the Runner is the form now.
## Tunables: scripts/runner.json. URL: ?runner=0 off, ?runner=1|2 starts at that beat.
extends Node

const CFG := "res://scripts/runner.json"
const SPRINT_MPS := 8.8          # player.gd SPEED 4.0 × RUN 2.2
var cfg := {
	"skin": "Ch36", "pose": ["idle", 0.4], "speed_x_sprint": 1.15, "mgr_trigger_m": 5.0,
	"saadi_trigger_m": 3.0, "startle_s": 0.9, "see_m": 70.0, "see_cone_deg": 40.0,
	"weave_m": 4.0, "weave_lateral_m": 0.9, "clip_speed_max": 2.0, "inside_mps": 6.0,
}

# Beat 1: Merry-Go-Round's right-hand window → its door → east along the Concourse → the court →
# right, up Dillard's entry. "in": a segment inside a store (no weaving, no wall checks).
const MGR_SPOT := Vector3(-95.5, 0.4, 47.45)
const MGR_FACE := Vector3(0, 0, 1)
const MGR_PATH := [
	[Vector3(-95.6, 0, 46.3), "in"], [Vector3(-98.0, 0, 46.3), "in"], [Vector3(-98.0, 0, 49.6), "in"],
	[Vector3(-92.0, 0, 53.5), ""], [Vector3(-62.0, 0, 57.0), ""], [Vector3(-46.0, 0, 57.0), ""],
	[Vector3(-26.0, 0, 55.0), ""], [Vector3(-9.0, 0, 58.0), ""], [Vector3(-4.5, 0, 64.0), ""],
	[Vector3(-4.0, 0, 72.0), ""], [Vector3(-4.0, 0, 79.4), "end"]]
# Beat 2: Saadi's second window → its door (past you) → the court → the Concourse → Wicks 'N'
# Sticks' door bay → between its tiered tables and the counter → the back door.
const SAADI_SPOT := Vector3(2.8, 0.0, 72.05)   # 0.65 m in from the platform: the court pillar hid him
const SAADI_FACE := Vector3(-1, 0, 0)
const SAADI_PATH := [
	[Vector3(3.9, 0, 72.0), "in"], [Vector3(3.9, 0, 70.0), "in"], [Vector3(0.6, 0, 70.0), "in"],
	[Vector3(-6.0, 0, 64.0), ""], [Vector3(-18.0, 0, 56.5), ""], [Vector3(-29.0, 0, 53.5), ""],
	[Vector3(-32.2, 0, 49.8), ""], [Vector3(-32.3, 0, 46.8), "in"], [Vector3(-32.6, 0, 40.4), "in"],
	[Vector3(-36.0, 0, 39.9), "in"], [Vector3(-36.0, 0, 36.7), "end"]]

var player: Node3D
var force := ""
var body: NpcBody
var stage := 1
var state := "hidden"       # hidden, wait, startle, run
var path := []
var pi := 0
var timer := 0.0
var pos := Vector3.ZERO
var disabled := false
var shoppers = null          # scripts/npcs.gd, for weaving and line of sight
var mps := 10.1
var run_t := 0.0             # seconds since this beat's run began

func _ready() -> void:
	if FileAccess.file_exists(CFG):
		var j = JSON.parse_string(FileAccess.get_file_as_string(CFG))
		if j is Dictionary:
			for k in j: cfg[k] = j[k]
	mps = SPRINT_MPS * float(cfg.speed_x_sprint)
	var mq = get_parent().get_node_or_null("Dynamic/dyn_rg_mannequin")
	if mq: mq.visible = false
	if force == "0" or not (player.wing == 2 or player.wing == 0):
		disabled = true; set_process(false); return
	var e := {}
	for s in NpcBody.manifest().get("skins", []):
		if str(s.id) == str(cfg.skin): e = s
	if e.is_empty():
		push_warning("runner: no skin " + str(cfg.skin)); disabled = true; return
	body = NpcBody.new()
	body.name = "Runner"
	body.set_skin(e)
	body.visible = false
	add_child(body)
	body.walk_clip = "run"
	stage = _load()
	if force in ["1", "2"]:
		stage = int(force)
	_enter()
	print("runner: stage ", stage, " ", state, " at ", mps, " m/s")

func _load() -> int:
	var v := ""
	if OS.has_feature("web"):
		v = str(JavaScriptBridge.eval("(function(){try{return sessionStorage.getItem('mall-runner')||''}catch(e){return ''}})()", true))
	else:
		v = str(Engine.get_meta("mall_runner", ""))
	return int(v) if v.is_valid_int() else 1

func _save() -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("try{sessionStorage.setItem('mall-runner','%d')}catch(e){}" % stage, true)
	else:
		Engine.set_meta("mall_runner", str(stage))

## Put him where this beat starts (or wait until that spot is out of the player's sight).
func _enter() -> void:
	body.visible = false; path = []; pi = 0
	match stage:
		1:
			_stand(MGR_SPOT, MGR_FACE); state = "wait"
		2:
			state = "hidden"; timer = 0.5
		_:
			state = "done"

func _stand(spot: Vector3, face: Vector3) -> void:
	pos = spot
	body.position = spot
	body.face(face)
	body.freeze(str(cfg.pose[0]), float(cfg.pose[1]))
	body.visible = true
	body.set_animated(true)

func _process(dt: float) -> void:
	if disabled or player == null or body == null: return
	if shoppers == null:
		shoppers = get_parent().get_node_or_null("Shoppers")
	var pp: Vector3 = player.global_position
	match state:
		"hidden":
			timer -= dt
			if timer <= 0.0:
				timer = 0.5
				# into Saadi's window only while that window is out of sight
				if stage == 2 and not _seen(SAADI_SPOT + SAADI_FACE * 1.4):
					_stand(SAADI_SPOT, SAADI_FACE); state = "wait"
					print("runner: in Saadi's window")
		"wait":
			var spot := MGR_SPOT if stage == 1 else SAADI_SPOT
			var trig := float(cfg.mgr_trigger_m if stage == 1 else cfg.saadi_trigger_m)
			if Vector2(pp.x - spot.x, pp.z - spot.z).length() < trig:
				_startle()
		"startle":
			timer -= dt
			body.face(Vector3(pp.x - pos.x, 0, pp.z - pos.z), 6.0, dt)
			if timer <= 0.0:
				state = "run"; pi = 0
				body.walk_clip = "run"
				body.play(body.walk_clip, 0.12, false)
				run_t = 0.0
				print("runner: runs (stage ", stage, ")")
		"run":
			_run(dt)

func _startle() -> void:
	state = "startle"
	timer = float(cfg.startle_s)
	body.ap.speed_scale = 1.0
	body.gesture("surprised", 0.08)
	path = MGR_PATH if stage == 1 else SAADI_PATH
	print("runner: startled (stage ", stage, ")")

func _run(dt: float) -> void:
	if pi >= path.size():
		_gone(); return
	var wp: Vector3 = path[pi][0]
	var kind: String = path[pi][1]
	var to := wp - pos; to.y = 0
	var inside := kind == "in" or (kind == "end" and stage == 2)
	var spd := float(cfg.inside_mps) if inside else mps
	if to.length() < maxf(0.4, spd * dt * 1.5):
		pi += 1
		if kind == "end":
			_gone(); return
		return
	var dir := to.normalized()
	var want := dir
	if not inside:
		# weave: step sideways round anyone just ahead (shoppers and the player)
		var right := dir.cross(Vector3.UP)
		var others := []
		if shoppers and "shoppers" in shoppers:
			for s in shoppers.shoppers: others.append(s.pos)
		others.append(player.global_position)
		for o in others:
			var dv: Vector3 = o - pos; dv.y = 0
			var ahead := dv.dot(dir)
			if ahead <= 0.0 or ahead > float(cfg.weave_m): continue
			var lat := dv.dot(right)
			if absf(lat) > float(cfg.weave_lateral_m): continue
			var side := -1.0 if lat > 0.0 else 1.0
			want += right * side * (1.0 - ahead / float(cfg.weave_m)) * 1.6
		want = want.normalized()
	var np := pos + want * spd * dt
	if not inside and shoppers and not shoppers._open(np):
		np = pos + dir * spd * dt          # never into a wall or a fixture: straight on instead
	pos = Vector3(np.x, 0, np.z)
	body.position = pos
	body.face(want, 12.0, dt)
	# inside a store a run, out in the hall a flat-out sprint (npc/anims.json: 4.6 and 6.0 m/s
	# in the clips, so the sprint needs the smaller speed-up at his 10 m/s)
	run_t += dt
	body.walk_clip = "run" if inside else "sprint"
	# the stride follows the ground speed (de-travelled run clips, npc/anims.json mps)
	if not body.busy():
		if body.clip != body.walk_clip:
			body.play(body.walk_clip, 0.12, false)
		var own := float(NpcBody.meta().clips.get(body.walk_clip, {}).get("mps", 3.5))
		body.ap.speed_scale = clampf(spd / maxf(own, 0.5), 0.6, float(cfg.clip_speed_max))

func _gone() -> void:
	body.visible = false
	print("runner: gone (stage ", stage, ")")
	stage += 1
	_save()
	_enter()

## In the player's view: near enough, inside the camera's cone, and a clear line over the walk grid.
func _seen(p: Vector3) -> bool:
	var cam := get_viewport().get_camera_3d()
	if cam == null: return false
	var c := cam.global_position
	var d := Vector3(p.x - c.x, 0, p.z - c.z)
	if d.length() > float(cfg.see_m): return false
	var f := -cam.global_basis.z; f.y = 0
	if f.normalized().dot(d.normalized()) < cos(deg_to_rad(float(cfg.see_cone_deg))): return false
	if shoppers and shoppers.has_method("_los"):
		return shoppers._los(Vector3(c.x, 0, c.z), p)
	return true
