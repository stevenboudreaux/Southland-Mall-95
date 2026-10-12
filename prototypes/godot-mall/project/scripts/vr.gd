## The mall in a VR headset (Meta Quest 2 and the like), through the headset browser's WebXR.
## Spec: design/godot-vr.md. Steven, Oct 12: "make the existing game able to be played on meta
## quest 2".
##
## scripts/player.gd adds this node under the player. On the web it asks the browser whether it can
## do immersive VR; if so the page (web/shell.html, window.mallVR) shows an "Enter VR" button, and
## pressing it starts the session. In the session:
## - you stand at your real height (the headset's floor), where the flat camera stood;
## - the left stick walks the way you look (hold a grip to run), the right stick turns in 30° snaps;
## - A, X or a trigger uses what is in front of you (the other wing, a playable machine);
## - B or Y opens a menu: the four jumps, the lighting, benches and plants, leave VR;
## - prompts and the menu hang in the air in front of you (2D HUD layers do not show in a headset);
## - the floor's mirror reflection is off (it draws the mall again for each eye).
## The arcade games are flat web pages, so playing one leaves VR and opens it on the browser's panel.
## Crossing to the other wing loads another page, which also ends the session: the page then tries
## to resume it by itself (the browser's "sessiongranted"), and otherwise shows Enter VR again.
extends Node3D

## Walking speed in the headset, metres a second: slower than the flat game's 4.0, which is
## uncomfortable in VR. A guess until Steven has tried it.
const WALK := 2.4
const RUN := 1.8          # holding a grip
const SNAP := 30.0        # degrees per snap turn
const STICK_ON := 0.6
const STICK_OFF := 0.3
const DEAD := 0.15
const BOARD_DIST := 1.1   # metres from the head to the prompt board
const BOARD_DROP := 0.28

var player: Node3D
var xr: XRInterface
var origin: XROrigin3D
var head: XRCamera3D
var hands := {}
var active := false
var _cb                    # keeps the page's callback alive
var _need_centre := false
var _snap_armed := true
var _nav_armed := true
var _refl_was := true
var _play_after := ""
# the board
var board: Node3D
var back: MeshInstance3D
var lines: Array = []
var menu_open := false
var menu_sel := 0
var menu_items: Array = []
var hint_t := 0.0
var note := ""
var note_t := 0.0
var _board_shown := false
var _rep_t := 0.0
var _fail_said := false
var _msaa_was := Viewport.MSAA_2X

func _ready() -> void:
	player = get_parent()
	if not OS.has_feature("web"):
		return
	xr = XRServer.find_interface("WebXR")
	if xr == null:
		return
	xr.session_supported.connect(_on_supported)
	xr.session_started.connect(_on_started)
	xr.session_ended.connect(_on_ended)
	xr.session_failed.connect(_on_failed)
	xr.is_session_supported("immersive-vr")

func _on_supported(mode: String, ok: bool) -> void:
	if mode != "immersive-vr" or not ok:
		return
	_cb = JavaScriptBridge.create_callback(_js_enter)
	var win = JavaScriptBridge.get_interface("window")
	win.mallVREnter = _cb
	JavaScriptBridge.eval("window.mallVR && window.mallVR.offer()", true)

func _js_enter(_args) -> void:
	enter()

## Ask the browser for the VR session. Must come from a press (the page's Enter VR button).
func enter() -> void:
	if active or xr == null:
		return
	xr.session_mode = "immersive-vr"
	xr.requested_reference_space_types = "local-floor, local"
	xr.required_features = "local-floor"
	xr.optional_features = "bounded-floor"
	_fail_said = false
	if not xr.initialize() and not _fail_said:
		_on_failed("the browser would not start VR")

func _on_failed(msg: String) -> void:
	_fail_said = true
	print("VR: could not start: ", msg)
	JavaScriptBridge.eval("window.mallVR && window.mallVR.failed(%s)" % JSON.stringify(msg), true)

func _on_started() -> void:
	print("VR: session started, space ", xr.reference_space_type)
	if origin == null:
		_build_rig()
	# without a floor space the headset's zero is at the eyes: lift the playspace to eye height
	origin.position.y = 0.0 if str(xr.reference_space_type).find("floor") >= 0 else player.EYE
	_msaa_was = get_viewport().msaa_3d
	var q := str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('vrmsaa') || ''", true))
	if q != "":
		get_viewport().msaa_3d = {"0": Viewport.MSAA_DISABLED, "2": Viewport.MSAA_2X, "4": Viewport.MSAA_4X}.get(q, _msaa_was)
	get_viewport().use_xr = true
	head.current = true
	active = true
	player.vr_on = true
	_need_centre = true
	_refl_was = player.buttons[0].button_pressed
	player.buttons[0].button_pressed = false
	menu_open = false
	hint_t = 10.0
	JavaScriptBridge.eval("window.mallVR && window.mallVR.started()", true)

func _on_ended() -> void:
	if not active:
		return
	print("VR: session ended")
	active = false
	player.vr_on = false
	# stay where the head was, looking the way it looked
	var hp := head.global_position
	var f := -head.global_transform.basis.z
	player.position = Vector3(hp.x, 0, hp.z)
	if Vector2(f.x, f.z).length() > 0.01:
		player.yaw = atan2(-f.x, -f.z)
	player.pitch = 0.0
	player._apply_rot()
	get_viewport().use_xr = false
	get_viewport().msaa_3d = _msaa_was
	player.cam.current = true
	player.buttons[0].button_pressed = _refl_was
	board.visible = false
	_board_shown = false
	JavaScriptBridge.eval("window.mallVR && window.mallVR.ended()", true)
	if _play_after != "":
		var id := _play_after
		_play_after = ""
		var sg = _signs()
		if sg:
			sg._play(id)

## Leave VR (the menu's last line, or before a flat arcade game opens).
func leave() -> void:
	if not active:
		return
	xr.uninitialize()
	_on_ended.call_deferred()   # in case the browser's own "ended" does not arrive

func _signs() -> Node:
	return get_tree().current_scene.get_node_or_null("Signs") if get_tree().current_scene else null

# ------------------------------------------------------------------ the rig
func _build_rig() -> void:
	origin = XROrigin3D.new()
	add_child(origin)
	head = XRCamera3D.new()
	head.near = 0.05
	head.far = 200.0
	origin.add_child(head)
	var hm := StandardMaterial3D.new()
	hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hm.albedo_color = Color(0.93, 0.88, 0.76)
	for side in ["left", "right"]:
		var c := XRController3D.new()
		c.tracker = StringName(side + "_hand")
		origin.add_child(c)
		var m := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(0.04, 0.04, 0.11)
		m.mesh = bm
		m.material_override = hm
		m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		c.add_child(m)
		c.button_pressed.connect(_on_button.bind(side))
		hands[side] = c
	_build_board()

func _stick(side: String) -> Vector2:
	var c: XRController3D = hands.get(side)
	if c == null or not c.get_has_tracking_data():
		return Vector2.ZERO
	var v := c.get_vector2("thumbstick")
	return v if v.length() > DEAD else Vector2.ZERO

## Put the head where the player stands (player.position) facing the player's yaw, whatever spot
## of the real room the headset is in. Called on entering VR and after a jump.
func recentre() -> void:
	if head == null:
		return
	var f := -head.transform.basis.z
	var hy := atan2(-f.x, -f.z) if Vector2(f.x, f.z).length() > 0.01 else 0.0
	var want := player.position
	player.yaw = player.yaw - hy
	player._apply_rot()
	var h := head.position
	var off := Basis(Vector3.UP, player.yaw) * Vector3(h.x, 0, h.z)
	player.position = Vector3(want.x - off.x, 0, want.z - off.z)
	_board_shown = false

func _process(dt: float) -> void:
	if not active:
		return
	if _need_centre:
		# wait for the first tracked head pose
		if head.position.length() > 0.01 or origin.position.y > 0.0:
			_need_centre = false
			recentre()
	for side in hands:
		hands[side].get_child(0).visible = hands[side].get_has_tracking_data()
	if not player.leaving:
		_move(dt)
	_update_board(dt)
	# where the head is, for tools/qa/vrtest.py
	_rep_t += dt
	if _rep_t > 0.25:
		_rep_t = 0.0
		var hp := head.global_position
		var f := -head.global_transform.basis.z
		var txt := ""
		for l in lines:
			if board.visible and l.visible:
				txt += l.text + "\n"
		JavaScriptBridge.eval("window.mallVR&&(window.mallVR.at=[%.2f,%.2f,%.2f,%.1f],window.mallVR.board=%s)" % [hp.x, hp.y, hp.z, rad_to_deg(atan2(-f.x, -f.z)), JSON.stringify(txt)], true)

func _move(dt: float) -> void:
	var ls := _stick("left")
	var rs := _stick("right")
	if menu_open:
		var y := ls.y if abs(ls.y) > abs(rs.y) else rs.y
		if _nav_armed and abs(y) > STICK_ON:
			_nav_armed = false
			menu_sel = posmod(menu_sel + (-1 if y > 0 else 1), menu_items.size())
		elif abs(y) < STICK_OFF:
			_nav_armed = true
		return
	# snap turn about the head, so the view turns in place
	if _snap_armed and abs(rs.x) > STICK_ON:
		_snap_armed = false
		var before := head.global_position
		player.yaw -= sign(rs.x) * deg_to_rad(SNAP)
		player._apply_rot()
		var after := head.global_position
		player.position += Vector3(before.x - after.x, 0, before.z - after.z)
	elif abs(rs.x) < STICK_OFF:
		_snap_armed = true
	if ls == Vector2.ZERO:
		return
	hint_t = min(hint_t, 1.5)
	var hb := head.global_transform.basis
	var fwd := Vector3(-hb.z.x, 0, -hb.z.z)
	if fwd.length() < 0.01:
		return
	fwd = fwd.normalized()
	var right := Vector3(-fwd.z, 0, fwd.x)
	var run := RUN if (_grip("left") or _grip("right")) else 1.0
	var step := (right * ls.x + fwd * ls.y) * WALK * run * dt
	var hp := head.global_position
	# collide at the head, since the body is under it; if the head already leans through a wall
	# or a shelf, let the stick walk it back out
	var stuck: bool = not player._free(hp.x, hp.z)
	if stuck or player._free(hp.x + step.x, hp.z):
		player.position.x += step.x
		hp.x += step.x
	if stuck or player._free(hp.x, hp.z + step.z):
		player.position.z += step.z

func _grip(side: String) -> bool:
	var c: XRController3D = hands.get(side)
	return c != null and (c.is_button_pressed("grip_click") or c.get_float("grip") > 0.6)

func _on_button(btn: String, _side: String) -> void:
	if not active or player.leaving:
		return
	match btn:
		"ax_button", "trigger_click":
			_action()
		"by_button":
			_menu_show(not menu_open)

## A, X or a trigger: choose in the menu, else play the machine in front of you, else cross the seam.
func _action() -> void:
	if menu_open:
		var it: Array = menu_items[menu_sel]
		_menu_show(false)
		(it[1] as Callable).call()
		return
	var sg = _signs()
	if sg and str(sg.play_id) != "" and sg.b_play and sg.b_play.visible:
		# the games are flat pages: leave VR, then open it on the browser's panel
		_play_after = str(sg.play_id)
		leave()
		return
	if player.prompt and player.prompt.visible:
		note = "Walking to the other wing…"
		note_t = 5.0
		player._cross()

func _menu_show(on: bool) -> void:
	menu_open = on
	if not on:
		return
	menu_sel = 0
	_nav_armed = false
	menu_items = []
	for i in player.JUMPS.size():
		var k: int = i
		menu_items.append(["Go to " + str(player.JUMPS[i][0]), func(): player._jump_go(k)])
	if player.buttons[2].visible:
		menu_items.append(["", func(): player.buttons[2].button_pressed = not player.buttons[2].button_pressed])
	menu_items.append(["", func(): player.buttons[1].button_pressed = not player.buttons[1].button_pressed])
	menu_items.append(["Leave VR", leave])

func _menu_text(i: int) -> String:
	var t: String = menu_items[i][0]
	if t != "":
		return t
	var has_light: bool = player.buttons[2].visible
	if has_light and i == player.JUMPS.size():
		return "Lighting: " + ("night" if player.buttons[2].button_pressed else "day") + "  (switch)"
	return "Benches & plants: " + ("on" if player.buttons[1].button_pressed else "off") + "  (switch)"

# ------------------------------------------------------------------ the board
func _build_board() -> void:
	board = Node3D.new()
	board.top_level = true
	board.visible = false
	add_child(board)
	back = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(1, 1)
	back.mesh = q
	var bm := StandardMaterial3D.new()
	bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bm.albedo_color = Color(0.08, 0.06, 0.05, 0.82)
	bm.no_depth_test = true
	bm.render_priority = 100
	back.material_override = bm
	back.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	board.add_child(back)
	for i in 9:
		var l := Label3D.new()
		l.pixel_size = 0.0011
		l.font_size = 44
		l.outline_size = 8
		l.no_depth_test = true
		l.render_priority = 101
		l.outline_render_priority = 100
		l.double_sided = false
		l.shaded = false
		l.position = Vector3(0, 0, 0.002)
		board.add_child(l)
		lines.append(l)

## What the board says now: the menu, else a prompt, else the first seconds' hint.
func _board_lines() -> Array:
	if menu_open:
		var out := [["Menu", Color(0.93, 0.85, 0.66)]]
		for i in menu_items.size():
			out.append([("›  " if i == menu_sel else "    ") + _menu_text(i), Color(1, 0.86, 0.5) if i == menu_sel else Color(1, 1, 1)])
		out.append(["stick up/down · A chooses · B closes", Color(0.93, 0.85, 0.66)])
		return out
	if note_t > 0.0:
		return [[note, Color(1, 0.97, 0.9)]]
	var sg = _signs()
	if sg and sg.b_play and sg.b_play.visible and str(sg.play_id) != "":
		return [["A   " + str(sg.b_play.text), Color(1, 0.97, 0.9)], ["opens on the browser's flat screen (leaves VR)", Color(0.93, 0.85, 0.66)]]
	if player.prompt and player.prompt.visible:
		return [["A   " + str(player.prompt_text.text), Color(1, 0.97, 0.9)]]
	if hint_t > 0.0:
		return [["Left stick walks · right stick turns", Color(1, 0.97, 0.9)], ["A uses · B opens the menu · hold a grip to run", Color(0.93, 0.85, 0.66)]]
	return []

func _update_board(dt: float) -> void:
	hint_t = max(0.0, hint_t - dt)
	note_t = max(0.0, note_t - dt)
	var rows := _board_lines()
	board.visible = not rows.is_empty()
	if rows.is_empty():
		_board_shown = false
		return
	var widest := 0
	for i in lines.size():
		var l: Label3D = lines[i]
		l.visible = i < rows.size()
		if l.visible:
			l.text = rows[i][0]
			l.modulate = rows[i][1]
			l.position.y = (rows.size() - 1) * 0.03 - i * 0.06
			widest = max(widest, str(rows[i][0]).length())
	back.scale = Vector3(max(0.5, widest * 0.0265 + 0.1), rows.size() * 0.06 + 0.06, 1)
	# hang in front of the head, a little below eye level, and drift after it as it turns
	var hp := head.global_position
	var hb := head.global_transform.basis
	var f := Vector3(-hb.z.x, 0, -hb.z.z)
	if f.length() < 0.01:
		return
	f = f.normalized()
	var want := hp + f * BOARD_DIST + Vector3(0, -BOARD_DROP, 0)
	if not _board_shown:
		board.global_position = want
		_board_shown = true
	else:
		board.global_position = board.global_position.lerp(want, clamp(dt * 4.0, 0.0, 1.0))
	var away := board.global_position * 2.0 - hp
	if away.distance_to(board.global_position) > 0.01:
		board.look_at(away, Vector3.UP)
