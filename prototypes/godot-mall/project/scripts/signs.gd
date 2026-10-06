## Owner-editable signs: the arcade cabinets' marquee titles in Pocket Change and the
## department boards in Kay-Bee Toys.
##
## The build (tools/build_mall.gd sign_add) lists every such sign in res://gen/signs.json
## with its faces in world space. The painted texture keeps the original words; when a sign
## has new text, this script lays a word-free copy of its art over it and draws the new text
## with a Label3D, so a rename needs no rebuild and no rebake.
##
## Where the text comes from, in order:
##   1. the published list, play/signs.json next to the game ({"signs": {id: text}});
##   2. on the owner's browser, unpublished edits kept in localStorage "southland-signs-draft".
##
## The owner is the browser the mall editor was unlocked in (localStorage "southland-editor",
## set by the main game's secret code), or any visit with ?owner=1. The owner gets two
## buttons: "Edit signs" (then tap or click a sign to retype it) and "Publish signs", which
## writes play/signs.json to GitHub with the token the main game's Publish already keeps in
## this browser (localStorage "southland-gh"); shell.html holds that code. No secret is in
## the repo: without a token, publishing asks for one and does not keep it.
extends Node

const DRAFT_KEY := "southland-signs-draft"
const PICK_RANGE := 16.0

## The look of each sign kind. Arcade titles follow each marquee's painted title colours.
const PC_STYLE := [
	{"font": "sans_italic", "fill": "#fff3a0", "outline": "#2a0400"},   # 0 THUNDER DOJO
	{"font": "sans", "fill": "#eef2fa", "outline": "#0a0a0e"},          # 1 IRON ALLEY
	{"font": "serif", "fill": "#ffffff", "outline": "#aa1414"},         # 2 BULLSEYE PATROL
	{"font": "sans_italic", "fill": "#c8f0ff", "outline": "#2048c8"},   # 3 ORBIT RAIDER
	{"font": "sans", "fill": "#ffffff", "outline": "#0a0a0a"},          # 4 FOURTH & GOAL
	{"font": "sans_italic", "fill": "#fff6d8", "outline": "#c01880"},   # 5 LUCKY LANES
	{"font": "sans_italic", "fill": "#fff4c0", "outline": "#0a0a0a"},   # 6 RED LINE RUSH
	{"font": "sans", "fill": "#fff6dc", "outline": "#c02818"},          # 7 PADDLE PANIC
]
const KB_STYLE := {"font": "sans", "fill": "#b0f03c", "outline": ""}
const FONT_FILES := {"sans": "sans.otf", "sans_italic": "sans_italic.otf", "serif": "serif.ttf", "script": "script.ttf"}

var recs := {}          # id -> record from gen/signs.json
var order: Array = []   # ids in build order
var published := {}     # id -> text, from play/signs.json
var draft := {}         # id -> text, the owner's unpublished edits
var made := {}          # id -> [nodes]
var mats := {}
var fonts := {}
var is_owner := false
var editing := false
var web := false
var ui: CanvasLayer
var b_edit: Button
var b_pub: Button
var status: Label
var press_at := Vector2.ZERO
var press_t := 0
var pressed := false
var publishing := false
var poll_t := 0.0

func _ready() -> void:
	web = OS.has_feature("web")
	if FileAccess.file_exists("res://gen/signs.json"):
		var J = JSON.parse_string(FileAccess.get_file_as_string("res://gen/signs.json"))
		if J is Dictionary:
			for r in J.get("signs", []):
				recs[r.id] = r
				order.append(r.id)
	if not web:
		return
	var o = JavaScriptBridge.eval("(function(){try{var q=new URLSearchParams(location.search).get('owner');if(q==='1')localStorage.setItem('southland-editor','1');return localStorage.getItem('southland-editor')==='1'?'1':'0'}catch(e){return '0'}})()")
	is_owner = str(o) == "1"
	if is_owner:
		var d = JavaScriptBridge.eval("(function(){try{return localStorage.getItem('" + DRAFT_KEY + "')||''}catch(e){return ''}})()")
		if d is String and d != "":
			var dj = JSON.parse_string(d)
			if dj is Dictionary:
				draft = dj
		_build_ui()
	_fetch_published()
	_apply_all()

# ------------------------------------------------------------------ loading
func _fetch_published() -> void:
	var url = JavaScriptBridge.eval("new URL('signs.json', location.href).href")
	if not (url is String):
		return
	var h := HTTPRequest.new()
	add_child(h)
	h.request_completed.connect(func(result, code, _headers, body):
		if result == HTTPRequest.RESULT_SUCCESS and code == 200:
			var j = JSON.parse_string(body.get_string_from_utf8())
			if j is Dictionary and j.get("signs") is Dictionary:
				published = j.signs
				_apply_all()
		h.queue_free())
	h.request(url + "?t=" + str(Time.get_unix_time_from_system()))

## The text a sign shows now: the owner's draft, else the published text, else the original.
func text_of(id: String) -> String:
	if draft.has(id):
		return str(draft[id])
	if published.has(id):
		return str(published[id])
	return str(recs[id].title)

func _apply_all() -> void:
	for id in order:
		_apply(id)

func _apply(id: String) -> void:
	var r = recs[id]
	var txt = text_of(id)
	if made.has(id):
		for nd in made[id]:
			nd.queue_free()
		made.erase(id)
	if txt == str(r.title):
		return   # the painted original shows
	var nodes = []
	for f in r.faces:
		var P = []
		for p in f.p:
			P.append(Vector3(p[0], p[1], p[2]))
		var n = Vector3(f.n[0], f.n[1], f.n[2])
		nodes.append(_overlay(r, P, f.uv, n))
		if txt.strip_edges() != "":
			nodes.append(_label(r, P, n, txt))
	made[id] = nodes

## A word-free copy of the sign's art laid just in front of it.
func _overlay(r, P: Array, uv: Array, n: Vector3) -> MeshInstance3D:
	var key = r.kind
	if not mats.has(key):
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		if key == "pc_marquee":
			m.albedo_texture = load("res://tex/pc/video_marquees_blank.png")
		else:
			m.albedo_texture = load("res://tex/kb/dept_blank.png")
			m.albedo_color = Color(0.92, 0.92, 0.92)
		m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		mats[key] = m
	var am := ArrayMesh.new()
	var arr = []
	arr.resize(Mesh.ARRAY_MAX)
	var v := PackedVector3Array()
	var t := PackedVector2Array()
	var nn := PackedVector3Array()
	for i in 4:
		v.append(P[i] + n * 0.003)
		t.append(Vector2(uv[i][0], uv[i][1]))
		nn.append(n)
	arr[Mesh.ARRAY_VERTEX] = v
	arr[Mesh.ARRAY_TEX_UV] = t
	arr[Mesh.ARRAY_NORMAL] = nn
	arr[Mesh.ARRAY_INDEX] = PackedInt32Array([0, 2, 1, 0, 3, 2])
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	var mi := MeshInstance3D.new()
	mi.mesh = am
	mi.material_override = mats[key]
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	return mi

## The new words, centred on the face and fitted to it.
func _label(r, P: Array, n: Vector3, txt: String) -> Label3D:
	var st = PC_STYLE[clampi(int(r.style), 0, PC_STYLE.size() - 1)] if r.kind == "pc_marquee" else KB_STYLE
	var right = (P[1] - P[0])
	var w = right.length()
	var up = (P[3] - P[0])
	var h = up.length()
	# a flared marquee is narrower at the bottom: fit to the narrow edge
	w = min(w, (P[2] - P[3]).length())
	var lab := Label3D.new()
	if not fonts.has(st.font):
		fonts[st.font] = load("res://fonts/" + FONT_FILES[st.font])
	lab.font = fonts[st.font]
	lab.font_size = 96
	lab.text = txt
	lab.modulate = Color(st.fill)
	if st.outline != "":
		lab.outline_size = 14
		lab.outline_modulate = Color(st.outline)
	else:
		lab.outline_size = 0
	lab.shaded = false
	lab.double_sided = false
	lab.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	lab.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lab.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	var sz = lab.font.get_multiline_string_size(txt, HORIZONTAL_ALIGNMENT_CENTER, -1, 96)
	sz.x += lab.outline_size * 2
	var fw = 0.86 if r.kind == "pc_marquee" else 0.9
	var fh = 0.62 if r.kind == "pc_marquee" else 0.7
	lab.pixel_size = min(w * fw / max(sz.x, 1.0), h * fh / max(sz.y, 1.0))
	var c = (P[0] + P[1] + P[2] + P[3]) * 0.25
	lab.basis = Basis(right.normalized(), up.normalized(), n.normalized())
	lab.position = c + n * 0.006
	add_child(lab)
	return lab

# ------------------------------------------------------------------ owner UI
func _build_ui() -> void:
	ui = CanvasLayer.new()
	ui.layer = 20
	add_child(ui)
	b_edit = _btn("Edit signs", Vector2(12, 132))
	b_edit.toggle_mode = true
	b_pub = _btn("Publish signs", Vector2(12, 182))
	status = Label.new()
	status.position = Vector2(14, 230)
	status.add_theme_font_size_override("font_size", 18)
	status.add_theme_color_override("font_color", Color.WHITE)
	status.add_theme_color_override("font_outline_color", Color.BLACK)
	status.add_theme_constant_override("outline_size", 5)
	ui.add_child(status)
	_refresh_ui()

func _btn(txt: String, pos: Vector2) -> Button:
	var b := Button.new()
	b.text = txt
	b.position = pos
	b.custom_minimum_size = Vector2(170, 42)
	b.mouse_filter = Control.MOUSE_FILTER_IGNORE   # taps are hit-tested in _input (touch skips mouse emulation)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 18)
	ui.add_child(b)
	return b

func _refresh_ui() -> void:
	if ui == null:
		return
	b_edit.button_pressed = editing
	b_pub.disabled = draft.is_empty() or publishing
	b_pub.text = "Publish signs (%d)" % draft.size() if not draft.is_empty() else "Publish signs"
	if publishing:
		status.text = "Publishing..."
	elif editing:
		status.text = "Tap a sign to change its words"
	elif status.text.begins_with("Tap"):
		status.text = ""

func _input(e: InputEvent) -> void:
	if not is_owner:
		return
	var pos = null
	var down = false
	var up = false
	if e is InputEventScreenTouch:
		pos = e.position; down = e.pressed; up = not e.pressed
	elif e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
		pos = e.position; down = e.pressed; up = not e.pressed
	if pos == null:
		return
	if down:
		for b in [b_edit, b_pub]:
			if b.get_global_rect().has_point(pos):
				get_viewport().set_input_as_handled()
				if b == b_edit:
					editing = not editing
				elif not b.disabled:
					_publish()
				_refresh_ui()
				return
		pressed = true
		press_at = pos
		press_t = Time.get_ticks_msec()
	elif up and pressed:
		pressed = false
		# a tap (not a walk or look drag) while editing picks a sign
		if editing and pos.distance_to(press_at) < 14.0 and Time.get_ticks_msec() - press_t < 450:
			var id = _pick(pos)
			if id != "":
				_retype(id)

## The sign under the screen point: the nearest one whose face contains it.
func _pick(sp: Vector2) -> String:
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return ""
	var best = ""
	var best_d = 1e9
	for id in order:
		for f in recs[id].faces:
			var P = []
			var behind = false
			for p in f.p:
				var v = Vector3(p[0], p[1], p[2])
				if cam.is_position_behind(v):
					behind = true
				P.append(v)
			if behind:
				continue
			var n = Vector3(f.n[0], f.n[1], f.n[2])
			var c = (P[0] + P[1] + P[2] + P[3]) * 0.25
			var dist = cam.global_position.distance_to(c)
			if dist > PICK_RANGE or n.dot(cam.global_position - c) <= 0.0:
				continue
			var poly = PackedVector2Array()
			for v in P:
				poly.append(cam.unproject_position(v))
			# a little slack around small, far signs
			var hit = Geometry2D.is_point_in_polygon(sp, poly)
			if not hit:
				var cc = cam.unproject_position(c)
				hit = sp.distance_to(cc) < 40.0
			if hit and dist < best_d:
				best_d = dist
				best = id
	return best

func _retype(id: String) -> void:
	var cur = text_of(id)
	var q = "Words for this sign (" + id + "). Leave empty to restore \"" + str(recs[id].title) + "\"."
	var res = JavaScriptBridge.eval("(function(){var r=prompt(" + JSON.stringify(q) + "," + JSON.stringify(cur) + ");return r===null?'__CANCEL__':r})()")
	if not (res is String) or res == "__CANCEL__":
		return
	var txt = res.strip_edges().to_upper() if recs[id].kind == "kb_dept" else res.strip_edges()
	if txt == "":
		txt = str(recs[id].title)
	if txt == str(published.get(id, recs[id].title)):
		draft.erase(id)
	else:
		draft[id] = txt
	_save_draft()
	_apply(id)
	_refresh_ui()

func _save_draft() -> void:
	JavaScriptBridge.eval("(function(){try{localStorage.setItem('" + DRAFT_KEY + "'," + JSON.stringify(JSON.stringify(draft)) + ")}catch(e){}})()")

# ------------------------------------------------------------------ publishing
## Hands the draft to shell.html's mallSigns.publish(), which merges it into the live
## play/signs.json on GitHub; then polls its status.
func _publish() -> void:
	if draft.is_empty() or publishing:
		return
	var ok = JavaScriptBridge.eval("(function(){if(!window.mallSigns)return '0';window.mallSigns.publish(" + JSON.stringify(JSON.stringify(draft)) + ");return '1'})()")
	if str(ok) != "1":
		status.text = "Publishing isn't available on this page"
		return
	publishing = true
	poll_t = 0.0
	_refresh_ui()

func _process(dt: float) -> void:
	if not publishing:
		return
	poll_t += dt
	if poll_t < 0.5:
		return
	poll_t = 0.0
	var s = JavaScriptBridge.eval("window.mallSigns ? window.mallSigns.status : 'error: no publisher'")
	if not (s is String) or s == "busy":
		return
	publishing = false
	if s == "ok":
		for id in draft:
			published[id] = draft[id]
		draft.clear()
		_save_draft()
		status.text = "Published. Everyone sees it in about a minute."
	else:
		status.text = "Not published: " + s.trim_prefix("error:").strip_edges()
	_refresh_ui()
