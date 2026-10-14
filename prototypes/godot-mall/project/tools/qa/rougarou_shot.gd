## Renders the Rougarou (scripts/rougarou.gd) for a look: in a dark studio from four angles, or
## standing in a baked wing at night. Native opengl3 under xvfb, like wingshot.gd:
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/rougarou_shot.gd -- \
##     --studio --out=/tmp/rg                      (writes rg-front/-quarter/-side/-back.png)
##   ... --wing=1 --mode=night --npc=x,z,yaw,hunch,gait --cam=x,z,yaw,pitch --out=/tmp/x.png
## --npc may repeat. --watch makes every figure's head turn to the camera.
extends SceneTree
var frames := 0
var out := "/tmp/rg"
var vp: SubViewport
var cam: Camera3D
var studio := false
var shots := []       # [name, cam position, look-at]
var shot_i := 0
var figures := []
var watch := false
var settle := 24

func _initialize() -> void:
	var wing := 1
	var mode := "night"
	var cam_s := "-4,-91,90,0"
	var npcs := []
	for a in OS.get_cmdline_user_args():
		if a == "--studio": studio = true
		elif a == "--watch": watch = true
		elif a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--mode="): mode = a.substr(7)
		elif a.begins_with("--cam="): cam_s = a.substr(6)
		elif a.begins_with("--npc="): npcs.append(a.substr(6))
		elif a.begins_with("--out="): out = a.substr(6)
	vp = SubViewport.new(); vp.size = Vector2i(1280, 720); vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	cam = Camera3D.new(); cam.fov = 60.0
	vp.add_child(cam); root.add_child(vp); cam.current = true
	if studio:
		_studio()
		return
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	var pl = scn.get_node_or_null("Player")
	if pl:
		scn.remove_child(pl); pl.free()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, mode)
	for s in npcs:
		var v = s.split(",")
		var r = load("res://scripts/rougarou.gd").new()
		scn.add_child(r)
		r.position = Vector3(float(v[0]), 0, float(v[1]))
		r.rotation_degrees.y = float(v[2])
		if v.size() > 3: r.hunch = float(v[3])
		if v.size() > 4: r.gait = float(v[4])
		figures.append(r)
	var v = cam_s.split(",")
	cam.fov = 70.0
	cam.rotation = Vector3(deg_to_rad(float(v[3])), deg_to_rad(float(v[2])), 0)
	cam.position = Vector3(float(v[0]), 1.62, float(v[1]))
	shots = [["", cam.position, null]]

func _studio() -> void:
	var scn = Node3D.new(); root.add_child(scn); current_scene = scn
	var env = Environment.new(); env.background_mode = Environment.BG_COLOR; env.background_color = Color("#2a2622")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color = Color("#8a8480"); env.ambient_light_energy = 0.6
	env.glow_enabled = true; env.glow_intensity = 0.5; env.glow_bloom = 0.1; env.glow_hdr_threshold = 1.2
	var we = WorldEnvironment.new(); we.environment = env; scn.add_child(we)
	var floor = MeshInstance3D.new(); var pm = PlaneMesh.new(); pm.size = Vector2(12, 12)
	var fm = StandardMaterial3D.new(); fm.albedo_color = Color("#4a433c"); fm.roughness = 0.7; pm.material = fm
	floor.mesh = pm; scn.add_child(floor)
	var key = DirectionalLight3D.new(); key.rotation_degrees = Vector3(-38, 200, 0); key.light_energy = 2.2; key.light_color = Color("#ffe6c8")
	key.shadow_enabled = true; scn.add_child(key)
	var fill = DirectionalLight3D.new(); fill.rotation_degrees = Vector3(-15, 110, 0); fill.light_energy = 0.9; fill.light_color = Color("#a8c0ff"); scn.add_child(fill)
	var rim = OmniLight3D.new(); rim.position = Vector3(-1.5, 2.6, 1.8); rim.light_energy = 3.0; rim.omni_range = 7.0; rim.light_color = Color("#ffd9a0"); scn.add_child(rim)
	var r = load("res://scripts/rougarou.gd").new(); scn.add_child(r); r.position = Vector3.ZERO
	figures.append(r)
	var ref = MeshInstance3D.new(); var bm = BoxMesh.new(); bm.size = Vector3(0.45, 1.8, 0.25)
	var rm = StandardMaterial3D.new(); rm.albedo_color = Color("#8a8a90"); bm.material = rm; ref.mesh = bm
	ref.position = Vector3(1.4, 0.9, 0); scn.add_child(ref)     # a 1.8 m box for scale
	shots = [
		["front", Vector3(0.0, 1.3, -3.4), Vector3(0, 1.0, 0)],
		["quarter", Vector3(-2.4, 1.5, -2.4), Vector3(0, 1.0, 0)],
		["side", Vector3(-3.4, 1.2, 0.2), Vector3(0, 1.0, 0)],
		["back", Vector3(2.0, 1.6, 2.8), Vector3(0, 1.0, 0)],
		["face", Vector3(-0.55, 1.55, -1.1), Vector3(0, 1.42, -0.2)],
	]
	_aim()

func _aim() -> void:
	var s = shots[shot_i]
	cam.position = s[1]
	if s[2] != null:
		cam.look_at_from_position(s[1], s[2], Vector3.UP)
	if watch:
		for f in figures:
			f.watch = cam.position

func _process(_d) -> bool:
	frames += 1
	if frames == 1 and not studio and watch:
		for f in figures:
			f.watch = cam.position
	if frames < settle: return false
	var s = shots[shot_i]
	var path = out if s[0] == "" else "%s-%s.png" % [out, s[0]]
	vp.get_texture().get_image().save_png(path)
	print("wrote ", path)
	shot_i += 1
	if shot_i >= shots.size():
		return true
	_aim(); frames = 0
	return false
