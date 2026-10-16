## Runs a wing with the shoppers for a while and saves what the player sees, native opengl3
## under xvfb:
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/npc_shot.gd -- \
##     --wing=1 --mode=night --cam=x,z,yaw,pitch --count=30 --secs=20 --out=/tmp/npc.png
## --secs of crowd time pass before the shot (Engine.time_scale 8 over secs*4 frames, since the
## software renderer is slow); several --cam= may be given (one shot each, same run).
extends SceneTree
var out := "/tmp/npc"
var frames := 0
var secs := 20.0
var cams := []
var shot_i := 0
var pl: Node3D
var sh: Node

func _initialize() -> void:
	var wing := 1; var mode := "night"; var count := "30"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--mode="): mode = a.substr(7)
		elif a.begins_with("--cam="): cams.append(a.substr(6))
		elif a.begins_with("--count="): count = a.substr(8)
		elif a.begins_with("--secs="): secs = float(a.substr(7))
		elif a.begins_with("--out="): out = a.substr(6)
	if cams.is_empty(): cams = ["-4,-91,90,0"]
	root.size = Vector2i(1280, 720)
	Engine.time_scale = 8.0
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, mode)
	pl = scn.get_node("Player")
	await process_frame
	await process_frame
	sh = scn.get_node_or_null("Shoppers")
	if sh:
		sh.force = count
		sh.cfg.count = int(count)
		sh.spawn_all_now = true
	_aim()

func _aim() -> void:
	var v = cams[shot_i].split(",")
	pl.position = Vector3(float(v[0]), 0, float(v[1]))
	pl.yaw = deg_to_rad(float(v[2])); pl.pitch = deg_to_rad(float(v[3]))
	pl._apply_rot()
	frames = 0

func _process(dt: float) -> bool:
	frames += 1
	if frames < int(secs * 4.0): return false
	var path = out if cams.size() == 1 else "%s-%d.png" % [out, shot_i]
	root.get_texture().get_image().save_png(path)
	var n = sh.shoppers.size() if sh else -1
	print("wrote ", path, " shoppers=", n)
	if sh and OS.get_cmdline_user_args().has("--dump"):
		for p in sh.players.slice(0, 6):
			var b: NpcBody = p.body; var sk: Skeleton3D = b.skin.find_child("Skeleton3D", true, false)
			var ul := sk.find_bone("mixamorig_LeftUpLeg")
			var lf := sk.get_bone_global_pose(sk.find_bone("mixamorig_LeftFoot")).origin; var rf := sk.get_bone_global_pose(sk.find_bone("mixamorig_RightFoot")).origin
			var lk := sk.get_bone_global_pose(sk.find_bone("mixamorig_LeftLeg")).origin
			print("   feet L=", lf, " R=", rf, " Lknee=", lk, " skel xform=", sk.global_transform.origin, " body=", b.global_position, " skin=", b.skin.scale)
			print("player ", b.id, " clip=", b.ap.current_animation, " t=", snappedf(b.ap.current_animation_position, 0.01), " speed=", b.ap.speed_scale, " active=", b.ap.active, " playing=", b.ap.is_playing(), " at=", p.pos, " thigh=", sk.get_bone_pose_rotation(ul).get_euler() * 57.3, " dist=", snappedf(Vector2(pl.position.x - p.pos.x, pl.position.z - p.pos.z).length(), 0.1))
	shot_i += 1
	if shot_i >= cams.size(): return true
	_aim(); secs = 2.0
	return false
