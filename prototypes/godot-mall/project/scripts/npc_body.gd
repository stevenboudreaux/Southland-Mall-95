## One shopper's body: a baked skin from npc/skins/<id>.scn (tools/npc/bake_npcs.gd) with the
## shared Mixamo clips from npc/anims.res. Behaviour lives in scripts/npcs.gd; this node only
## shows a person, faces a direction and plays walk / idle / look / sit at a speed.
##
## The pack's skins come in two scale batches, so the clips' position tracks (the hip bob) are
## scaled per skin by hips / anim_hips (npc/skins.json); one scaled library is cached per ratio.
## Models face +Z, so `face(dir)` turns +Z toward dir. The walk clip's forward travel was
## removed at bake time: `set_speed(mps)` runs the clip at mps / walk_mps so the feet keep up.
class_name NpcBody
extends Node3D

static var _libs := {}          # ratio (rounded) -> AnimationLibrary
static var _base_lib: AnimationLibrary
static var _manifest := {}
## The day light's colour on a white surface in the bake (Sears' white interior reads 214/206/193
## where an untinted white NPC shirt read 220/221/221): skins are multiplied by it so people take
## the mall's warm day colour on top of the lightmap probes (scripts/npcs.json day_tint).
static var tint := Color(1, 1, 1)

var id := ""
var entry := {}
var skin: Node3D
var ap: AnimationPlayer
var clip := ""
var walk_mps := 1.765
var yaw := 0.0
var speed := 0.0

## npc/skins.json, loaded once.
static func manifest() -> Dictionary:
	if _manifest.is_empty():
		var j = JSON.parse_string(FileAccess.get_file_as_string("res://npc/skins.json"))
		_manifest = j if j is Dictionary else {"skins": [], "anim_hips": 1.013, "walk_mps": 1.765}
	return _manifest

## Build the body for one manifest entry.
func set_skin(e: Dictionary) -> void:
	entry = e
	id = str(e.id)
	if skin:
		skin.queue_free(); skin = null
	var ps: PackedScene = load(str(e.scn))
	if ps == null:
		push_warning("npc_body: no skin " + str(e.scn)); return
	skin = ps.instantiate()
	add_child(skin)
	if tint != Color(1, 1, 1):
		for mi in skin.find_children("*", "MeshInstance3D", true, false):
			for i in range(mi.mesh.get_surface_count()):
				var mat = mi.mesh.surface_get_material(i)
				if mat is StandardMaterial3D: mat.albedo_color = tint
	var m := manifest()
	walk_mps = float(m.get("walk_mps", 1.765))
	var ratio := float(e.hips) / float(m.get("anim_hips", 1.013))
	ap = AnimationPlayer.new()
	ap.name = "Anim"
	skin.add_child(ap)
	ap.root_node = ap.get_path_to(skin)
	ap.add_animation_library("npc", _lib_for(ratio))
	ap.playback_default_blend_time = 0.25
	play("idle")

## A little light of their own, so people in dark windows and at night are not black: NPCs are
## dynamic and get only the lightmap probes (the Demo 11 mannequin lesson). The albedo is used
## as the emission texture, scaled by `k` (scripts/npcs.json self_light_day / _night). Off by day
## since Oct 16 2026: the flat glow ignored the mall's shading and warm light (Steven's video).
func set_self_light(k: float) -> void:
	if skin == null: return
	for mi in skin.find_children("*", "MeshInstance3D", true, false):
		for i in range(mi.mesh.get_surface_count()):
			var m = mi.mesh.surface_get_material(i)
			if m is StandardMaterial3D:
				m.emission_enabled = k > 0.0
				m.emission_texture = m.albedo_texture
				m.emission = Color(k, k, k)
				m.emission_energy_multiplier = 1.0

## Freeze on one frame of a clip (window mannequins, arcade players). The player keeps running
## at speed 0 rather than being switched off: a stopped player never marks the skeleton dirty,
## and then modifiers such as the hand IK never get a pass.
func freeze(name: String, at: float) -> void:
	if ap == null: return
	clip = name
	ap.active = true
	ap.play("npc/" + name, 0.0)
	ap.seek(at, true)
	ap.speed_scale = 0.0

## The clips with their position tracks scaled for a skin of this hip height.
static func _lib_for(ratio: float) -> AnimationLibrary:
	var key := snappedf(ratio, 0.01)
	if _libs.has(key):
		return _libs[key]
	if _base_lib == null:
		_base_lib = load("res://npc/anims.res")
	var lib := AnimationLibrary.new()
	for n in _base_lib.get_animation_list():
		var a: Animation = _base_lib.get_animation(n).duplicate(true)
		for t in range(a.get_track_count()):
			if a.track_get_type(t) == Animation.TYPE_POSITION_3D:
				for k in range(a.track_get_key_count(t)):
					a.track_set_key_value(t, k, a.track_get_key_value(t, k) * ratio)
		lib.add_animation(n, a)
	_libs[key] = lib
	return lib

## Play one of walk / idle / look / sit; a random start offset keeps a crowd out of step.
func play(name: String, blend := 0.25, random_start := true) -> void:
	if ap == null or clip == name:
		return
	clip = name
	ap.play("npc/" + name, blend)
	if random_start:
		ap.seek(randf() * ap.current_animation_length, false)
	if name != "walk":
		ap.speed_scale = 1.0

## Walking speed in m/s (0 stands). Scales the walk clip so the stride matches the ground.
func set_speed(mps: float) -> void:
	speed = mps
	if mps > 0.05:
		play("walk", 0.2, clip != "walk")
		ap.speed_scale = clampf(mps / walk_mps, 0.5, 1.6)
	elif clip == "walk":
		play("idle")

## Turn +Z (the model's front) toward a world direction, smoothly if `rate` is given.
func face(dir: Vector3, rate := 0.0, dt := 0.0) -> void:
	if dir.length_squared() < 1e-6:
		return
	var target := atan2(dir.x, dir.z)
	if rate <= 0.0 or dt <= 0.0:
		yaw = target
	else:
		yaw = lerp_angle(yaw, target, clampf(rate * dt, 0.0, 1.0))
	rotation.y = yaw

## Pin the hands to two world points (an arcade panel's joystick and buttons): a two-bone IK
## per arm, solved here (Godot 4.7's SkeletonIK3D did nothing on a frozen player). Shortest-arc
## deltas turn the upper arm toward a law-of-cosines elbow and the forearm toward the target,
## on top of the frame's animated pose, so the hands follow while the body keeps its stance.
## Call once; it runs every frame after the animation until `hands_off()`.
var _hands := {}            # "Left"/"Right" -> world target
var _sk: Skeleton3D
func hands_to(left: Vector3, right: Vector3) -> void:
	_hands = {"Left": left, "Right": right}
	if _sk == null and skin: _sk = skin.find_child("Skeleton3D", true, false)
	process_priority = 20       # after the AnimationPlayer has written the frame's pose
	set_process(true)

func hands_off() -> void:
	_hands = {}
	set_process(false)

func _process(_dt: float) -> void:
	if _hands.is_empty() or _sk == null: return
	for side in _hands:
		_arm_ik(side, _hands[side])

func _arm_ik(side: String, target_w: Vector3) -> void:
	var up := _sk.find_bone("mixamorig_" + side + "Arm")
	var fo := _sk.find_bone("mixamorig_" + side + "ForeArm")
	var ha := _sk.find_bone("mixamorig_" + side + "Hand")
	if up < 0 or fo < 0 or ha < 0: return
	var inv := _sk.global_transform.affine_inverse()
	var t: Vector3 = inv * target_w
	var S: Vector3 = _sk.get_bone_global_pose(up).origin
	var E: Vector3 = _sk.get_bone_global_pose(fo).origin
	var Wr: Vector3 = _sk.get_bone_global_pose(ha).origin
	var a := S.distance_to(E); var b := E.distance_to(Wr)
	var to_t := t - S
	var d := clampf(to_t.length(), 0.05, a + b - 0.01)
	var dir := to_t.normalized()
	# the elbow: angle at the shoulder from the law of cosines, bent toward a pole below and behind
	var cos_s := clampf((a * a + d * d - b * b) / (2.0 * a * d), -1.0, 1.0)
	var pole: Vector3 = Basis(_sk.get_bone_global_pose(0).basis.get_rotation_quaternion()) * Vector3(0.6 if side == "Right" else -0.6, -1.0, -0.4)
	var side_v := (pole - pole.project(dir)).normalized()
	if side_v.length_squared() < 1e-4: side_v = Vector3.DOWN
	var E1: Vector3 = S + (dir * cos(acos(cos_s)) + side_v * sin(acos(cos_s))) * a
	_turn(up, E - S, E1 - S)
	E = _sk.get_bone_global_pose(fo).origin
	Wr = _sk.get_bone_global_pose(ha).origin
	_turn(fo, Wr - E, (S + dir * d) - E)

## Rotate bone `i` so the skeleton-space direction `from` becomes `to` (shortest arc), in local terms.
func _turn(i: int, from: Vector3, to: Vector3) -> void:
	if from.length_squared() < 1e-8 or to.length_squared() < 1e-8: return
	var delta := Quaternion(from.normalized(), to.normalized())
	var parent := _sk.get_bone_parent(i)
	var pg := _sk.get_bone_global_pose(parent).basis.get_rotation_quaternion() if parent >= 0 else Quaternion()
	var local_delta := pg.inverse() * delta * pg
	_sk.set_bone_pose_rotation(i, (local_delta * _sk.get_bone_pose_rotation(i)).normalized())

## Head height for a look-at or a close-up.
func eye_pos() -> Vector3:
	return global_position + Vector3(0, float(entry.get("height_m", 1.7)) - 0.1, 0)
