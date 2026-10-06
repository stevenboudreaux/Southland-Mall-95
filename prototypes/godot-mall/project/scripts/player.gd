## First-person walker for the Godot mall.
## Phone: drag on the left half to walk, drag on the right half to look.
## Desktop: WASD / arrow keys to walk, drag with the mouse to look.
## URL ?cam=x,z,yaw,pitch places the camera (used for test screenshots).
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
var last_pos := {}   # touch index -> last position
var hud: Label
var buttons: Array = []   # HUD buttons, tapped by hand since touch skips mouse emulation
var hint: Label
var stick: Control
var fps_t := 0.0
var debug := false

func _ready() -> void:
	position = Vector3(33.0, 0, 0.0)
	# the walkable grid comes from the layout file the mall was built from
	if walk_rows.is_empty() and FileAccess.file_exists("res://layout_mall.json"):
		var lay = JSON.parse_string(FileAccess.get_file_as_string("res://layout_mall.json"))
		if lay is Dictionary:
			walk_rows = PackedStringArray(lay.get("walk", []))
			map_origin = Vector2(lay.origin[0], lay.origin[1])
			map_scale = float(lay.scale)
	if FileAccess.file_exists("res://gen/collide.json"):
		var col = JSON.parse_string(FileAccess.get_file_as_string("res://gen/collide.json"))
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
		var q = JavaScriptBridge.eval("new URLSearchParams(location.search).get('cam') || ''")
		if q is String and q != "":
			var v: PackedStringArray = q.split(",")
			if v.size() >= 3:
				position = Vector3(float(v[0]), 0, float(v[1]))
				yaw = deg_to_rad(float(v[2]))
				if v.size() >= 4:
					pitch = deg_to_rad(float(v[3]))
				hint.visible = false
	_apply_rot()

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
	if not ResourceLoader.exists("res://main_day.lmbake"):
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
	if iv.length() > 0.05:
		hint.visible = false
		var fwd := -transform.basis.z
		var right := transform.basis.x
		var run := RUN if (Input.is_physical_key_pressed(KEY_X) or Input.is_physical_key_pressed(KEY_SHIFT)) else 1.0
		var step := (right * iv.x - fwd * iv.y) * SPEED * run * dt
		_try_move(Vector3(step.x, 0, 0))
		_try_move(Vector3(0, 0, step.z))
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
