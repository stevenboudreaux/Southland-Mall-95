## First-person walker for the Godot mall.
## Phone: drag on the left half to walk, drag on the right half to look.
## Desktop: WASD / arrow keys to walk, drag with the mouse to look, hold the right mouse button
## (or X / Shift) to run. J (a gamepad's Y, or the "Jump to" button) opens the quick-jump menu:
## Sears, the main entrance, Dillard's or JCPenney (Steven, Oct 8).
## URL ?cam=x,z,yaw,pitch places the camera (used for test screenshots).
## Wings (design/godot-wings.md): the mall ships as two game files; near the seam between them a
## prompt offers the other wing (E / Enter, a gamepad's A, a click or a tap), and the page reloads
## into that wing's file at the same spot, facing the same way, behind a fade to black.
extends Node3D

@export var obstacles: Array = []
var fx_obstacles: Array = []     # benches, planters, trash cans (only when shown)
var fixtures_on := false
## Walkable map tiles (rows of "0"/"1"), and how map tiles map to metres.
@export var walk_rows: PackedStringArray = []
@export var map_origin := Vector2(148, 100)
@export var map_scale := 2.0
const EYE := 1.62
const SPEED := 4.0
const RUN := 2.2      # holding X (or Shift) runs: Steven, Oct 6, "add back the ability to run by hitting x"
const RADIUS := 0.3
var yaw := PI * 0.5   # looking west (-x) from the entrance
var pitch := 0.06
var cam: Camera3D
var move_touch := -1
var look_touch := -1
var move_origin := Vector2.ZERO
var move_vec := Vector2.ZERO
var dragging := false
var rmb_run := false    # the right mouse button held: run (Steven, Oct 8)
# quick jump (Steven, Oct 8): name, wing, x, z, yaw (degrees), standing in front of each entrance
# with your back to it, looking out into the mall (Steven, Oct 9)
const JUMPS := [
	["Sears", 1, -4.0, -90.0, 180.0],
	["Mall entrance", 1, 31.0, 0.0, 90.0],
	["Dillard's", 2, -4.0, 75.5, 0.0],
	["JCPenney", 2, -148.0, 56.0, -90.0]]
var jump_panel: PanelContainer
var jump_btns: Array = []
var jump_sel := 0
var jump_open_btn: Button
var last_pos := {}   # touch index -> last position
var hud: Label
var buttons: Array = []   # HUD buttons, tapped by hand since touch skips mouse emulation
var hint: Label
var stick: Control
var fps_t := 0.0
var debug := false
# wings
var wing := 0
var seam := []              # [x0, z, x1]: the seam line; the other wing lies on other_side
var other_side := 1.0
var prompt: Button
var prompt_key: Label
var prompt_text: Label
var fade: ColorRect
var leaving := false
var input_kind := "kb"      # "kb", "pad" or "touch": which glyph the prompt shows
const SEAM_NEAR := 2.6      # metres from the seam at which the prompt shows
const WING_NAMES := {1: "Wing 1 · Sears & the main entrance", 2: "Wing 2 · Dillard's & JCPenney"}

func _ready() -> void:
	position = Vector3(33.0, 0, 0.0)
	var gen: String = get_parent().get_meta("gen", "res://gen/") if get_parent() else "res://gen/"
	wing = int(get_parent().get_meta("wing", 0)) if get_parent() else 0
	var wj = null
	if FileAccess.file_exists(gen + "wing.json"):
		wj = JSON.parse_string(FileAccess.get_file_as_string(gen + "wing.json"))
	# the walkable grid comes from the layout file the mall was built from
	if walk_rows.is_empty() and FileAccess.file_exists("res://layout_mall.json"):
		var lay = JSON.parse_string(FileAccess.get_file_as_string("res://layout_mall.json"))
		if lay is Dictionary:
			walk_rows = PackedStringArray(lay.get("walk", []))
			map_origin = Vector2(lay.origin[0], lay.origin[1])
			map_scale = float(lay.scale)
	if wj is Dictionary:
		# this wing's walk grid: the other wing's tiles are closed, so the seam is a wall
		walk_rows = PackedStringArray(wj.get("walk", walk_rows))
		seam = wj.get("seam", [])
		other_side = float(wj.get("other_side", 1.0))
		var sp: Array = wj.get("spawn", [])
		if sp.size() >= 4:
			position = Vector3(float(sp[0]), 0, float(sp[1]))
			yaw = deg_to_rad(float(sp[2]))
			pitch = deg_to_rad(float(sp[3]))
	if FileAccess.file_exists(gen + "collide.json"):
		var col = JSON.parse_string(FileAccess.get_file_as_string(gen + "collide.json"))
		if col is Dictionary:
			obstacles = col.get("static", obstacles)
			fx_obstacles = col.get("fixtures", [])
	cam = Camera3D.new()
	cam.position = Vector3(0, EYE, 0)
	cam.fov = 70.0
	cam.near = 0.05
	cam.far = 200.0
	add_child(cam)
	cam.current = true
	_build_hud()
	if OS.has_feature("web"):
		debug = str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('debug') || ''")) == "1"
		if str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('refl') || ''")) == "0":
			buttons[0].button_pressed = false
		if str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('time') || ''")) == "day":
			buttons[2].button_pressed = false
		if str(JavaScriptBridge.eval("new URLSearchParams(location.search).get('fx') || ''")) == "1":
			buttons[1].button_pressed = true
		var q = JavaScriptBridge.eval("new URLSearchParams(location.search).get('cam') || ''")
		if q is String and q != "":
			var v: PackedStringArray = q.split(",")
			if v.size() >= 3:
				position = Vector3(float(v[0]), 0, float(v[1]))
				yaw = deg_to_rad(float(v[2]))
				if v.size() >= 4:
					pitch = deg_to_rad(float(v[3]))
				hint.visible = false
	elif Engine.has_meta("mall_xfer"):
		# arrived from the other wing in this same run (not on the web: the editor or a test)
		var x: Dictionary = Engine.get_meta("mall_xfer")
		Engine.remove_meta("mall_xfer")
		position = Vector3(x.x, 0, x.z)
		yaw = x.yaw
		pitch = x.pitch
		hint.visible = false
	_apply_rot()
	_build_wing_ui()
	_build_jump_ui()

func _build_hud() -> void:
	var cl := CanvasLayer.new()
	add_child(cl)
	hud = Label.new()
	hud.position = Vector2(12, 8)
	hud.add_theme_color_override("font_color", Color(1, 1, 1, 0.9))
	hud.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	hud.add_theme_constant_override("shadow_offset_x", 1)
	hud.add_theme_constant_override("shadow_offset_y", 1)
	hud.add_theme_font_size_override("font_size", 14)
	cl.add_child(hud)
	_add_button("Reflections", true, 8, func(on: bool):
		var rt = get_tree().current_scene.get_node_or_null("Runtime")
		if rt:
			rt.set_reflections(on))
	_add_button("Benches & plants", false, 48, func(on: bool):
		fixtures_on = on
		var fxn = get_tree().current_scene.get_node_or_null("Dynamic/dyn_fixtures")
		if fxn:
			fxn.visible = on)
	_add_button("Lighting", true, 88, func(night: bool):
		var rt = get_tree().current_scene.get_node_or_null("Runtime")
		if rt:
			rt.set_time("night" if night else "day"), ["day", "night"])
	# the day lighting ships separately; hide the switch until it's baked
	var scn := get_tree().current_scene
	if scn == null:
		scn = get_parent()
	if scn and not ResourceLoader.exists(load("res://scripts/time_of_day.gd").lightmap_path(scn, "day")):
		buttons[2].visible = false
	_cl = cl
	hint = Label.new()
	hint.text = "Drag left side to walk · drag right side to look"
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	hint.offset_top = -60
	hint.offset_left = -220
	hint.offset_right = 220
	hint.add_theme_font_size_override("font_size", 16)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.95))
	hint.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	hint.add_theme_constant_override("shadow_offset_x", 1)
	hint.add_theme_constant_override("shadow_offset_y", 1)
	cl.add_child(hint)
	stick = Control.new()
	stick.visible = false
	stick.draw.connect(func():
		stick.draw_circle(Vector2.ZERO, 46, Color(1, 1, 1, 0.12))
		stick.draw_arc(Vector2.ZERO, 46, 0, TAU, 32, Color(1, 1, 1, 0.5), 2.0)
		stick.draw_circle(move_vec * 46, 18, Color(1, 1, 1, 0.55)))
	cl.add_child(stick)

var _cl: CanvasLayer

## A toggle button in the top-right corner: "<name>: on/off".
func _add_button(name: String, on: bool, top: int, cb: Callable, words := ["off", "on"]) -> void:
	var btn := Button.new()
	btn.toggle_mode = true
	btn.button_pressed = on
	btn.text = "%s: %s" % [name, words[1] if on else words[0]]
	btn.focus_mode = Control.FOCUS_NONE
	btn.add_theme_font_size_override("font_size", 14)
	btn.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	btn.offset_left = -200
	btn.offset_right = -10
	btn.offset_top = top
	btn.offset_bottom = top + 32
	btn.toggled.connect(func(v: bool):
		btn.text = "%s: %s" % [name, words[1] if v else words[0]]
		cb.call(v))
	hud.get_parent().add_child(btn)
	buttons.append(btn)
	(func(): cb.call(btn.button_pressed)).call_deferred()   # current state, after any URL overrides

func _input(e: InputEvent) -> void:
	var half := get_viewport().get_visible_rect().size.x * 0.5
	if e is InputEventJoypadButton or (e is InputEventJoypadMotion and abs(e.axis_value) > 0.4):
		input_kind = "pad"
	elif e is InputEventKey or e is InputEventMouseButton:
		input_kind = "kb"
	elif e is InputEventScreenTouch:
		input_kind = "touch"
	if _jump_input(e):
		get_viewport().set_input_as_handled()
		return
	if prompt and prompt.visible and not leaving:
		var go := false
		if e is InputEventKey and e.pressed and not e.echo and e.physical_keycode in [KEY_E, KEY_ENTER, KEY_KP_ENTER]:
			go = true
		elif e is InputEventJoypadButton and e.pressed and e.button_index == JOY_BUTTON_A:
			go = true
		elif e is InputEventScreenTouch and e.pressed and prompt.get_global_rect().has_point(e.position):
			go = true
		if debug:
			print("DBG prompt input ", e)
		if go:
			get_viewport().set_input_as_handled()
			_cross()
			return
	if e is InputEventScreenTouch:
		# touches don't reach buttons (mouse emulation is off), so tap it here
		if e.pressed:
			for b in buttons:
				if b.get_global_rect().has_point(e.position):
					b.button_pressed = not b.button_pressed
					get_viewport().set_input_as_handled()
					return
		if e.pressed:
			last_pos[e.index] = e.position
			hint.visible = false
			if e.position.x < half and move_touch == -1:
				move_touch = e.index; move_origin = e.position; move_vec = Vector2.ZERO
				stick.position = e.position; stick.visible = true; stick.queue_redraw()
			elif look_touch == -1:
				look_touch = e.index
		else:
			last_pos.erase(e.index)
			if e.index == move_touch:
				move_touch = -1; move_vec = Vector2.ZERO; stick.visible = false
			if e.index == look_touch:
				look_touch = -1
	elif e is InputEventScreenDrag:
		var prev: Vector2 = last_pos.get(e.index, e.position)
		last_pos[e.index] = e.position
		if e.index == move_touch:
			move_vec = ((e.position - move_origin) / 46.0).limit_length(1.0)
			stick.queue_redraw()
		elif e.index == look_touch:
			var d: Vector2 = e.position - prev
			if d.length() < 120.0:   # ignore a jump if the browser swaps fingers
				_look(d * 0.0045)
	elif e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
		dragging = e.pressed
		hint.visible = false
	elif e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_RIGHT:
		rmb_run = e.pressed
	elif e is InputEventMouseMotion and dragging and not DisplayServer.is_touchscreen_available():
		_look(e.relative * 0.004)

func _look(d: Vector2) -> void:
	yaw -= d.x
	pitch = clamp(pitch - d.y, -1.2, 1.2)
	_apply_rot()

func _apply_rot() -> void:
	rotation = Vector3(0, yaw, 0)
	cam.rotation = Vector3(pitch, 0, 0)

func _process(dt: float) -> void:
	var iv := Vector2(
		Input.get_axis("ui_left", "ui_right") + float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
		Input.get_axis("ui_up", "ui_down") + float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
	if move_touch != -1:
		iv = move_vec
	iv = iv.limit_length(1.0)
	if leaving:
		iv = Vector2.ZERO
	if iv.length() > 0.05:
		hint.visible = false
		var fwd := -transform.basis.z
		var right := transform.basis.x
		var run := RUN if (rmb_run or Input.is_physical_key_pressed(KEY_X) or Input.is_physical_key_pressed(KEY_SHIFT)) else 1.0
		var step := (right * iv.x - fwd * iv.y) * SPEED * run * dt
		_try_move(Vector3(step.x, 0, 0))
		_try_move(Vector3(0, 0, step.z))
	_update_prompt()
	fps_t += dt
	if fps_t > 0.5:
		fps_t = 0.0
		hud.text = "Houma Mall Rewind · Godot mall (1995)   %d fps" % Engine.get_frames_per_second()
		if debug:
			print("DBG pos=", position, " touch=", move_touch, " vec=", move_vec, " iv=", iv, " free_here=", _free(position.x, position.z), " rows=", walk_rows.size())

func _try_move(d: Vector3) -> void:
	var p := position + d
	if _free(p.x, p.z):
		position = p

func _walk(x: float, z: float) -> bool:
	var tx := int(floor(x / map_scale + map_origin.x))
	var ty := int(floor(z / map_scale + map_origin.y))
	if ty < 0 or ty >= walk_rows.size() or tx < 0 or tx >= walk_rows[ty].length():
		return false
	return walk_rows[ty][tx] == "1"

func _free(x: float, z: float) -> bool:
	var r := RADIUS
	if not (_walk(x - r, z - r) and _walk(x + r, z - r) and _walk(x - r, z + r) and _walk(x + r, z + r)):
		return false
	if _hits(obstacles, x, z):
		return false
	if fixtures_on and _hits(fx_obstacles, x, z):
		return false
	return true

func _hits(list: Array, x: float, z: float) -> bool:
	for o in list:
		if o.size() == 3 and not (o[0] is String):
			if Vector2(x - o[0], z - o[1]).length() < o[2] + RADIUS * 0.5:
				return true
		elif o[0] == "rect":
			if x > o[1] and x < o[3] and z > o[2] and z < o[4]:
				return true
	return false

# ------------------------------------------------------------------ wings
## The prompt (bottom middle, as in Fallout: a key cap and where it leads) and the fade.
func _build_wing_ui() -> void:
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 1)
	fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var arriving := Engine.has_meta("mall_arrived")
	if OS.has_feature("web"):
		arriving = str(JavaScriptBridge.eval("(function(){try{var v=sessionStorage.getItem('mall-xfer')||'';sessionStorage.removeItem('mall-xfer');return v}catch(e){return ''}})()")) != ""
	if Engine.has_meta("mall_arrived"):
		Engine.remove_meta("mall_arrived")
	fade.modulate.a = 1.0 if arriving else 0.0
	var top := CanvasLayer.new()
	top.layer = 20
	add_child(top)
	if wing == 0 or seam.size() < 3:
		if arriving:
			top.add_child(fade)
			create_tween().tween_property(fade, "modulate:a", 0.0, 0.6).set_delay(0.25)
		return
	prompt = Button.new()
	prompt.focus_mode = Control.FOCUS_NONE
	prompt.visible = false
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.06, 0.05, 0.78)
	sb.border_color = Color(0.93, 0.85, 0.66, 0.85)
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 14; sb.content_margin_right = 18
	sb.content_margin_top = 8; sb.content_margin_bottom = 8
	for st_name in ["normal", "hover", "pressed", "focus"]:
		prompt.add_theme_stylebox_override(st_name, sb)
	prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	prompt.custom_minimum_size = Vector2(340, 58)
	prompt.offset_left = -170; prompt.offset_right = 170
	prompt.offset_top = -132; prompt.offset_bottom = -74
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.offset_left = 14; row.offset_right = -14
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 12)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	prompt.add_child(row)
	prompt_key = Label.new()
	prompt_key.custom_minimum_size = Vector2(38, 34)
	prompt_key.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_key.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	prompt_key.add_theme_font_size_override("font_size", 17)
	prompt_key.add_theme_color_override("font_color", Color(0.1, 0.08, 0.06))
	var kb := StyleBoxFlat.new()
	kb.bg_color = Color(0.95, 0.89, 0.74)
	kb.set_corner_radius_all(6)
	prompt_key.add_theme_stylebox_override("normal", kb)
	prompt_key.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(prompt_key)
	prompt_text = Label.new()
	prompt_text.add_theme_font_size_override("font_size", 16)
	prompt_text.add_theme_color_override("font_color", Color(1, 0.97, 0.9))
	prompt_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(prompt_text)
	prompt.pressed.connect(_cross)
	top.add_child(prompt)
	top.add_child(fade)
	if arriving:
		create_tween().tween_property(fade, "modulate:a", 0.0, 0.6).set_delay(0.25)

## Distance from the player to the seam line, or a large number when not beside it.
func _seam_dist() -> float:
	if seam.size() < 3:
		return 1e9
	var x0 := float(seam[0]); var z := float(seam[1]); var x1 := float(seam[2])
	if position.x < x0 - 0.6 or position.x > x1 + 0.6:
		return 1e9
	# only from this wing's side
	var d := (z - position.z) * other_side
	return d if d >= -0.2 else 1e9

func _update_prompt() -> void:
	if prompt == null:
		return
	var near := _seam_dist() < SEAM_NEAR and not leaving
	if near != prompt.visible:
		prompt.visible = near
	if near:
		var other := 3 - wing
		prompt_key.text = {"pad": "A", "touch": "Tap", "kb": "E"}[input_kind]
		prompt_key.custom_minimum_size.x = 50 if input_kind == "touch" else 38
		prompt_text.text = "Enter " + WING_NAMES[other]

## Walk across the seam: fade to black, then load the other wing at the same spot (1.3 m past the
## seam), facing the same way, with the same lighting and toggles.
func _cross() -> void:
	if leaving or wing == 0:
		return
	leaving = true
	print("crossing to wing ", 3 - wing)
	prompt.visible = false
	var other := 3 - wing
	var tz := float(seam[1]) + other_side * 1.3
	var tx := clampf(position.x, float(seam[0]) + 0.5, float(seam[2]) - 0.5)
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.35)
	tw.tween_callback(func():
		var day: bool = not buttons[2].button_pressed
		if OS.has_feature("web"):
			var cam_s := "%.2f,%.2f,%.1f,%.1f" % [tx, tz, rad_to_deg(yaw), rad_to_deg(pitch)]
			var js := "(function(){try{sessionStorage.setItem('mall-xfer','%d')}catch(e){}var u=new URL(location.href);var p=u.searchParams;p.set('wing','%d');p.set('cam','%s');" % [other, other, cam_s]
			js += "p.set('time','%s');" % ("day" if day else "night")
			js += "if(%s)p.set('refl','0');else p.delete('refl');" % ("true" if not buttons[0].button_pressed else "false")
			js += "if(%s)p.set('fx','1');else p.delete('fx');" % ("true" if buttons[1].button_pressed else "false")
			js += "console.log('crossing to '+u.toString());if(window.mallGoWing){window.mallGoWing(u.toString())}else{location.replace(u.toString())}})()"
			JavaScriptBridge.eval(js, true)
		else:
			Engine.set_meta("mall_xfer", {"x": tx, "z": tz, "yaw": yaw, "pitch": pitch})
			Engine.set_meta("mall_arrived", true)
			var path := "res://wing%d.tscn" % other
			if ResourceLoader.exists(path):
				get_tree().change_scene_to_file(path)
			else:
				leaving = false
				fade.modulate.a = 0.0)

# ------------------------------------------------------------------ quick jump
## A small menu (J, a gamepad's Y, or the "Jump to" button) that drops the player in front of
## Sears, the main entrance, Dillard's or JCPenney. In the other wing, it loads that wing's file
## the same way the seam does.
func _build_jump_ui() -> void:
	jump_open_btn = Button.new()
	jump_open_btn.text = "Jump to (J)"
	jump_open_btn.focus_mode = Control.FOCUS_NONE
	jump_open_btn.add_theme_font_size_override("font_size", 14)
	jump_open_btn.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	jump_open_btn.offset_left = -200; jump_open_btn.offset_right = -10
	jump_open_btn.offset_top = 128; jump_open_btn.offset_bottom = 160
	jump_open_btn.pressed.connect(func(): _jump_show(not jump_panel.visible))
	_cl.add_child(jump_open_btn)
	jump_panel = PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.08, 0.06, 0.05, 0.86)
	sb.border_color = Color(0.93, 0.85, 0.66, 0.85)
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(10)
	sb.set_content_margin_all(14)
	jump_panel.add_theme_stylebox_override("panel", sb)
	jump_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	jump_panel.custom_minimum_size = Vector2(280, 0)
	jump_panel.offset_left = -140; jump_panel.offset_right = 140
	jump_panel.offset_top = -130; jump_panel.offset_bottom = 130
	jump_panel.visible = false
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 8)
	jump_panel.add_child(col)
	var title := Label.new()
	title.text = "Jump to"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 18)
	title.add_theme_color_override("font_color", Color(1, 0.97, 0.9))
	col.add_child(title)
	for i in JUMPS.size():
		var b := Button.new()
		b.text = "%d   %s" % [i + 1, JUMPS[i][0]]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(0, 40)
		b.add_theme_font_size_override("font_size", 16)
		var k := i
		b.pressed.connect(func(): _jump_go(k))
		b.mouse_entered.connect(func(): _jump_select(k))
		col.add_child(b)
		jump_btns.append(b)
	var foot := Label.new()
	foot.text = "1–4 or arrows + Enter · gamepad: D-pad + A · Esc / B closes"
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	foot.add_theme_font_size_override("font_size", 12)
	foot.add_theme_color_override("font_color", Color(0.93, 0.85, 0.66, 0.9))
	col.add_child(foot)
	_cl.add_child(jump_panel)
	_jump_select(0)

func _jump_show(on: bool) -> void:
	if leaving:
		on = false
	jump_panel.visible = on
	if on:
		move_vec = Vector2.ZERO
		dragging = false
		_jump_select(0)

func _jump_select(i: int) -> void:
	jump_sel = posmod(i, JUMPS.size())
	for k in jump_btns.size():
		jump_btns[k].modulate = Color(1, 0.86, 0.5) if k == jump_sel else Color(1, 1, 1)

## Handles the menu's keys, pad buttons and taps. True when the event was used.
func _jump_input(e: InputEvent) -> bool:
	if jump_panel == null or leaving:
		return false
	var open := jump_panel.visible
	if e is InputEventKey and e.pressed and not e.echo:
		var k: int = e.physical_keycode
		if k == KEY_J:
			_jump_show(not open)
			return true
		if not open:
			return false
		if k == KEY_ESCAPE:
			_jump_show(false)
		elif k in [KEY_UP, KEY_W]:
			_jump_select(jump_sel - 1)
		elif k in [KEY_DOWN, KEY_S]:
			_jump_select(jump_sel + 1)
		elif k in [KEY_ENTER, KEY_KP_ENTER, KEY_E, KEY_SPACE]:
			_jump_go(jump_sel)
		elif k >= KEY_1 and k < KEY_1 + JUMPS.size():
			_jump_go(k - KEY_1)
		return true
	if e is InputEventJoypadButton and e.pressed:
		if e.button_index == JOY_BUTTON_Y:
			_jump_show(not open)
			return true
		if not open:
			return false
		match e.button_index:
			JOY_BUTTON_B, JOY_BUTTON_BACK:
				_jump_show(false)
			JOY_BUTTON_DPAD_UP:
				_jump_select(jump_sel - 1)
			JOY_BUTTON_DPAD_DOWN:
				_jump_select(jump_sel + 1)
			JOY_BUTTON_A:
				_jump_go(jump_sel)
		return true
	if e is InputEventJoypadMotion and open and e.axis == JOY_AXIS_LEFT_Y and abs(e.axis_value) > 0.6:
		if not Engine.has_meta("_jump_axis_held"):
			Engine.set_meta("_jump_axis_held", true)
			_jump_select(jump_sel + (1 if e.axis_value > 0 else -1))
		return true
	if e is InputEventJoypadMotion and e.axis == JOY_AXIS_LEFT_Y and abs(e.axis_value) < 0.3 and Engine.has_meta("_jump_axis_held"):
		Engine.remove_meta("_jump_axis_held")
	if e is InputEventScreenTouch and e.pressed:
		# touches skip mouse emulation, so the menu and its button are tapped here
		if jump_open_btn.get_global_rect().has_point(e.position):
			_jump_show(not open)
			return true
		if open:
			for i in jump_btns.size():
				if jump_btns[i].get_global_rect().has_point(e.position):
					_jump_go(i)
					return true
			if not jump_panel.get_global_rect().has_point(e.position):
				_jump_show(false)
			return true
	if open and (e is InputEventScreenDrag or (e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT and e.pressed and not jump_panel.get_global_rect().has_point(e.position))):
		if e is InputEventMouseButton:
			_jump_show(false)
		return true
	return false

## Go to JUMPS[i]: in this wing, at once; in the other wing, by loading its file there.
func _jump_go(i: int) -> void:
	var j: Array = JUMPS[i]
	_jump_show(false)
	hint.visible = false
	var tw_wing := int(j[1])
	if wing == 0 or tw_wing == wing:
		position = Vector3(float(j[2]), 0, float(j[3]))
		yaw = deg_to_rad(float(j[4]))
		pitch = deg_to_rad(3.0)
		_apply_rot()
		return
	leaving = true
	if prompt:
		prompt.visible = false
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", 1.0, 0.35)
	tw.tween_callback(func():
		var day: bool = not buttons[2].button_pressed
		if OS.has_feature("web"):
			var cam_s := "%.2f,%.2f,%.1f,%.1f" % [float(j[2]), float(j[3]), float(j[4]), 3.0]
			var js := "(function(){try{sessionStorage.setItem('mall-xfer','%d')}catch(e){}var u=new URL(location.href);var p=u.searchParams;p.set('wing','%d');p.set('cam','%s');" % [tw_wing, tw_wing, cam_s]
			js += "p.set('time','%s');" % ("day" if day else "night")
			js += "if(%s)p.set('refl','0');else p.delete('refl');" % ("true" if not buttons[0].button_pressed else "false")
			js += "if(%s)p.set('fx','1');else p.delete('fx');" % ("true" if buttons[1].button_pressed else "false")
			js += "console.log('jumping to '+u.toString());if(window.mallGoWing){window.mallGoWing(u.toString())}else{location.replace(u.toString())}})()"
			JavaScriptBridge.eval(js, true)
		else:
			Engine.set_meta("mall_xfer", {"x": float(j[2]), "z": float(j[3]), "yaw": deg_to_rad(float(j[4])), "pitch": deg_to_rad(3.0)})
			Engine.set_meta("mall_arrived", true)
			var path := "res://wing%d.tscn" % tw_wing
			if ResourceLoader.exists(path):
				get_tree().change_scene_to_file(path)
			else:
				leaving = false
				fade.modulate.a = 0.0)
