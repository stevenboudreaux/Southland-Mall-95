## Bakes Steven's Mixamo clip library (Oct 16 2026: "use as many of these animations as possible")
## into npc/anims.res, the one AnimationLibrary every NPC skin plays.
##
## Sources (gitignored, see production/npc-sources.md): npc_src/mixamo_clips/<name>.fbx, all
## downloaded "without skin" on Ch01 (Mixamo's own skeleton, so the skins' bone axes match within
## a few degrees; scripts/npc_body.gd corrects the rest). The old four clips came from the bought
## pack's Character_01, whose arm bones point ~180° away from the Mixamo skins' rest: that was the
## sideways walking and twisted arcade players in Demo 36.
##
## Per clip (CLIPS below: our name -> [source, kind]):
##   - tracks renamed Skeleton3D:mixamorig12_* -> Skeleton3D:mixamorig_* (the skins' names);
##   - "walk": the hips' travel is removed and its speed recorded (the body node moves instead);
##     "loop": net drift of the hips removed so the loop closes, sway kept; "once": kept as is;
##   - an optional [from, to] frame window (30 fps), then for loops the best-matching end frame
##     near `to` is found and the last LOOP_BLEND frames ease into the first pose, so the seam
##     doesn't pop (the arcade "play" loop: Texting While Standing frames ~91–615, phone in and
##     out of the pocket cut off);
##   - Animation.compress() for size.
## Also writes npc/anims.json: per clip length, loop, kind, mps (walks), and the clip skeleton's
## global rest rotations, which NpcBody uses to retarget onto each skin.
## Run: godot --headless --path . --script res://tools/npc/bake_clips.gd [-- --stats]
extends SceneTree

const SRC := "res://npc_src/mixamo_clips/"
const FPS := 30.0
const LOOP_BLEND := 12
# name: [source file, kind, window [from, to] frames or []]
const CLIPS := {
	# walking
	"walk_m": ["mloco_walking", "walk", []], "walk_m2": ["walk", "walk", []],
	"walk_f": ["floco_walking", "walk", []], "walk_f2": ["female_walk", "walk", []],
	"walk_bag": ["walking_with_shopping_bag", "walk", []], "walk_drunk": ["drunk_walk", "walk", []],
	# standing about
	"idle": ["idle", "loop", []], "idle_m": ["mloco_idle", "loop", []], "idle_f": ["floco_idle", "loop", []],
	"weight_shift": ["gest_weight_shift", "loop", []], "bored": ["bored", "loop", []],
	"briefcase_idle": ["standing_w_briefcase_idle", "loop", []], "phone": ["texting_while_standing", "once", []],
	# browsing, windows, confusion
	"look": ["look_around", "loop", []], "look_2": ["look_around_2", "loop", []],
	"looking_2": ["looking_around_2", "loop", []], "looking_3": ["looking_around_3", "loop", []],
	"look_down": ["looking_down", "loop", []], "thinking": ["thinking", "loop", []],
	"nervous": ["nervously_look_around", "loop", []], "point": ["pointing", "once", []],
	"point_fwd": ["pointing_forward", "once", []], "thankful": ["thankful", "once", []],
	"head_shake_thoughtful": ["gest_thoughtful_head_shake", "once", []],
	"head_shake_annoyed": ["gest_annoyed_head_shake", "once", []], "head_no": ["gest_shaking_head_no", "once", []],
	"head_yes": ["gest_head_nod_yes", "once", []], "sigh": ["gest_relieved_sigh", "once", []],
	# talking (standing pairs)
	"talk": ["talking", "loop", []], "talk_2": ["talking_2", "loop", []], "talk_3": ["talking_3", "loop", []],
	"talk_4": ["talking_4", "loop", []], "talk_5": ["talking_5", "loop", []],
	"secret": ["telling_a_secret", "once", []], "argue": ["standing_arguing", "loop", []],
	"argue_2": ["standing_arguing_2", "loop", []], "argue_3": ["standing_arguing_3", "loop", []],
	"acknowledge": ["gest_acknowledging", "once", []], "happy_hands": ["gest_happy_hand_gesture", "once", []],
	"cocky": ["gest_being_cocky", "once", []], "dismiss": ["gest_dismissing_gesture", "once", []],
	"angry": ["gest_angry_gesture", "once", []], "nod_hard": ["gest_hard_head_nod", "once", []],
	"nod_long": ["gest_lengthy_head_nod", "once", []], "look_away": ["gest_look_away_gesture", "once", []],
	"nod_sarcastic": ["gest_sarcastic_head_nod", "once", []],
	# benches
	"stand_to_sit": ["stand_to_sit", "move", []], "sit_to_stand": ["sit_to_stand", "move", []], "sit_talk_3": ["talking_6", "loop", []],
	"sit_talk": ["sitting_talking", "loop", []], "sit_talk_2": ["sitting_talking_2", "loop", []],
	"sit_idle_2": ["sitting_idle_2", "loop", []], "sit_idle_3": ["sitting_idle_3", "loop", []],
	"sit_idle_4": ["sitting_idle_4", "loop", []], "sit": ["sitting", "loop", []], "sit_2": ["sitting_2", "loop", []],
	"sit_rub_arm": ["sitting_rubbing_arm", "loop", []],
	# arcade
	"play": ["texting_while_standing", "loop", [91, 615]], "buttons": ["button_pushing", "loop", []],
	"cheer": ["cheering", "once", []], "cheer_2": ["cheering_2", "once", []], "excited": ["excited", "once", []],
	"clap": ["clapping", "once", []], "rally": ["rallying", "once", []],
	"drive": ["driving", "loop", []], "honk": ["honking_horn", "once", []], "steer_right": ["holding_turn_right", "once", []],
	# the drunk
	"drunk_idle": ["drunk_idle", "loop", []], "drunk_idle_2": ["drunk_idle_variation", "loop", []],
	"drunk_idle_3": ["drunk_idle_variation_2", "loop", []], "drunk_turn": ["drunk_turn", "once", []],
	# the Runner (scripts/runner_ai.gd; Steven's Oct 16 downloads): runs are de-travelled like walks
	"run": ["running", "walk", []], "sprint": ["sprint", "walk", []], "jog": ["jog_forward", "walk", []],
	"run_look_back": ["look_behind_run", "walk", []], "run_jump": ["running_jump", "walk", []],
	"surprised": ["surprised", "once", []], "forward_jump": ["forward_jump", "once", []],
	"turn_to_run": ["turn_to_running", "once", []], "run_to_turn": ["running_to_turn", "once", []],
	"run_turn_r": ["running_right_turn", "once", []], "run_to_stop": ["run_to_stop", "once", []],
	"stumble_back": ["stumble_backwards", "once", []],
	# confused shoppers, and the Regis customer in a styling chair
	"search_pockets": ["searching_pockets", "loop", []],
	"sit_f": ["female_sitting_pose", "loop", []], "sit_f2": ["female_sitting_pose_2", "loop", []],
	"sit_m": ["male_sitting_pose", "loop", []], "sit_disbelief": ["sitting_disbelief", "loop", []],
}

var stats := false

func _initialize() -> void:
	stats = OS.get_cmdline_user_args().has("--stats")
	var lib := AnimationLibrary.new()
	var meta := {"clips": {}, "rest": {}, "hips": 0.0}
	var rest_done := false
	for name in CLIPS:
		var c: Array = CLIPS[name]
		var path: String = SRC + str(c[0]) + ".fbx"
		var ps: PackedScene = load(path)
		if ps == null: print("MISSING ", path); continue
		var scene: Node = ps.instantiate()
		var sk: Skeleton3D = scene.find_child("Skeleton3D", true, false)
		var ap: AnimationPlayer = scene.find_child("AnimationPlayer", true, false)
		var src: Animation = ap.get_animation(ap.get_animation_list()[0])
		var hips_i := -1
		for b in range(sk.get_bone_count()):
			if sk.get_bone_name(b).ends_with("_Hips"): hips_i = b
		if not rest_done:
			for b in range(sk.get_bone_count()):
				var q := sk.get_bone_global_rest(b).basis.get_rotation_quaternion()
				meta.rest[_norm(sk.get_bone_name(b))] = [q.x, q.y, q.z, q.w]
			meta.hips = sk.get_bone_rest(hips_i).origin.y
			rest_done = true
		var a := _clip(src, str(c[1]), c[2])
		var info := _fix_hips(a, str(c[1]))
		if str(c[1]) == "walk" and float(info.get("mps", 0.0)) < 0.2:
			info["mps"] = _foot_speed(sk, src)
			info["in_place"] = true
		info["kind"] = c[1]
		info["src"] = c[0]
		if stats:
			print("%-22s %-28s %6.2fs %s" % [name, c[0], a.length, str(info)])
		a.compress()
		lib.add_animation(name, a)
		meta.clips[name] = info
		scene.free()
	if stats: quit(); return
	var err := ResourceSaver.save(lib, "res://npc/anims.res", ResourceSaver.FLAG_COMPRESS)
	var f := FileAccess.open("res://npc/anims.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(meta, "\t"))
	print("anims.res ", err, ": ", lib.get_animation_list().size(), " clips")
	quit()

static func _norm(n: String) -> String:
	var p := n.find("_")
	return "mixamorig" + n.substr(p) if n.begins_with("mixamorig") and p > 0 else n

## The clip with renamed tracks, cut to its window, sampled to keys every frame on every track
## (so windows and the loop blend can work frame by frame).
func _clip(src: Animation, kind: String, win: Array) -> Animation:
	var n := int(round(src.length * FPS))
	var f0 := 0; var f1 := n
	if win.size() == 2: f0 = int(win[0]); f1 = int(win[1])
	if kind == "loop" and win.size() == 2:
		f1 = _best_end(src, f0, f1)
	var a := Animation.new()
	a.length = float(f1 - f0) / FPS
	a.step = 1.0 / FPS
	a.loop_mode = Animation.LOOP_LINEAR if kind in ["loop", "walk"] else Animation.LOOP_NONE
	for t in range(src.get_track_count()):
		var ty := src.track_get_type(t)
		if ty != Animation.TYPE_ROTATION_3D and ty != Animation.TYPE_POSITION_3D: continue
		var p := str(src.track_get_path(t))
		var bone := p.get_slice(":", 1)
		if ty == Animation.TYPE_POSITION_3D and not bone.ends_with("_Hips"): continue
		var nt := a.add_track(ty)
		a.track_set_path(nt, NodePath("Skeleton3D:" + _norm(bone)))
		a.track_set_interpolation_type(nt, Animation.INTERPOLATION_LINEAR)
		for i in range(f1 - f0 + 1):
			var tt := float(f0 + i) / FPS
			var v = src.rotation_track_interpolate(t, tt) if ty == Animation.TYPE_ROTATION_3D else src.position_track_interpolate(t, tt)
			if ty == Animation.TYPE_ROTATION_3D: a.rotation_track_insert_key(nt, float(i) / FPS, v)
			else: a.position_track_insert_key(nt, float(i) / FPS, v)
	if kind == "loop":
		_blend_seam(a)
	return a

## The frame near `to` (within the last 40 % of the window) whose pose best matches `from`'s, so a
## loop of from..end is as seamless as the clip allows. Arms and hands weigh double.
func _best_end(src: Animation, f0: int, f1: int) -> int:
	var best := f1; var best_d := INF
	var lo := f0 + int((f1 - f0) * 0.6)
	for f in range(lo, f1 + 1):
		var d := 0.0
		for t in range(src.get_track_count()):
			if src.track_get_type(t) != Animation.TYPE_ROTATION_3D: continue
			var w := 2.0 if ("Arm" in str(src.track_get_path(t)) or "Hand" in str(src.track_get_path(t))) else 1.0
			var q0: Quaternion = src.rotation_track_interpolate(t, float(f0) / FPS)
			var q1: Quaternion = src.rotation_track_interpolate(t, float(f) / FPS)
			d += q0.angle_to(q1) * w
		if d < best_d: best_d = d; best = f
	print("  loop window ", f0, "..", f1, " -> best end ", best, " (pose distance ", snappedf(best_d, 0.01), ")")
	return best

## The last LOOP_BLEND frames ease toward the first frame's pose so the wrap is smooth.
func _blend_seam(a: Animation) -> void:
	for t in range(a.get_track_count()):
		var n := a.track_get_key_count(t)
		if n < LOOP_BLEND * 2: continue
		var first = a.track_get_key_value(t, 0)
		for k in range(LOOP_BLEND):
			var i := n - LOOP_BLEND + k
			var w := smoothstep(0.0, 1.0, float(k + 1) / float(LOOP_BLEND))
			var v = a.track_get_key_value(t, i)
			if v is Quaternion: a.track_set_key_value(t, i, (v as Quaternion).slerp(first, w))
			else: a.track_set_key_value(t, i, (v as Vector3).lerp(first, w))

## Walks: remove the hips' travel (record m/s). Loops: remove the net drift so the loop closes.
func _fix_hips(a: Animation, kind: String) -> Dictionary:
	var info := {"len": snappedf(a.length, 0.001), "loop": kind in ["loop", "walk"]}
	for t in range(a.get_track_count()):
		if a.track_get_type(t) != Animation.TYPE_POSITION_3D or not str(a.track_get_path(t)).ends_with("_Hips"): continue
		var n := a.track_get_key_count(t)
		var p0: Vector3 = a.track_get_key_value(t, 0)
		var p1: Vector3 = a.track_get_key_value(t, n - 1)
		var drift := Vector3(p1.x - p0.x, 0, p1.z - p0.z)
		if kind == "walk":
			info["mps"] = snappedf(drift.length() / a.length, 0.001)
			info["dir"] = [snappedf(drift.normalized().x, 0.01), snappedf(drift.normalized().z, 0.01)]
			# keep the bob and the sway across the walk line, drop the travel along it
			var dn := drift.normalized()
			for k in range(n):
				var v: Vector3 = a.track_get_key_value(t, k)
				var along := (Vector3(v.x - p0.x, 0, v.z - p0.z)).dot(dn)
				a.track_set_key_value(t, k, v - dn * along)
		elif kind == "loop" or kind == "once":
			for k in range(n):
				var v: Vector3 = a.track_get_key_value(t, k)
				a.track_set_key_value(t, k, v - drift * (float(k) / float(n - 1)))
		info["hips0"] = [snappedf(p0.x, 0.001), snappedf(p0.z, 0.001)]
		info["drift_m"] = snappedf(drift.length(), 0.01)
		info["hips_y"] = [snappedf(p0.y, 0.01), snappedf(p1.y, 0.01)]
	return info

## An in-place walk's speed: how fast the planted foot slides back under the body.
func _foot_speed(sk: Skeleton3D, src: Animation) -> float:
	var foot := -1
	for b in range(sk.get_bone_count()):
		if sk.get_bone_name(b).ends_with("_LeftToeBase"): foot = b
	var n := int(round(src.length * FPS))
	var ys := []; var zs := []
	for f in range(n + 1):
		var t := float(f) / FPS
		for tr in range(src.get_track_count()):
			var bn := str(src.track_get_path(tr)).get_slice(":", 1)
			var bi := sk.find_bone(bn)
			if bi < 0: continue
			if src.track_get_type(tr) == Animation.TYPE_ROTATION_3D: sk.set_bone_pose_rotation(bi, src.rotation_track_interpolate(tr, t))
			elif src.track_get_type(tr) == Animation.TYPE_POSITION_3D and bn.ends_with("_Hips"): sk.set_bone_pose_position(bi, src.position_track_interpolate(tr, t))
		var g := _fk(sk, foot).origin
		ys.append(g.y); zs.append(g.z)
	var lo: float = ys.min()
	var v := []
	for f in range(1, ys.size()):
		if ys[f] < lo + 0.02 and ys[f - 1] < lo + 0.02: v.append(-(zs[f] - zs[f - 1]) * FPS)
	print("  foot y ", snappedf(lo, 0.001), "..", snappedf(ys.max(), 0.001), " z ", snappedf(zs.min(), 0.001), "..", snappedf(zs.max(), 0.001), " planted ", v.size())
	if v.is_empty(): return 1.3
	v.sort()
	return snappedf(absf(v[v.size() / 2]), 0.001)

## Forward kinematics from the current bone poses (no scene tree needed).
func _fk(sk: Skeleton3D, b: int) -> Transform3D:
	var t := Transform3D(Basis(sk.get_bone_pose_rotation(b)), sk.get_bone_pose_position(b))
	var p := sk.get_bone_parent(b)
	return _fk(sk, p) * t if p >= 0 else t
