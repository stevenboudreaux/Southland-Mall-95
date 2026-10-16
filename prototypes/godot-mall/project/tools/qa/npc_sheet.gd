## Renders the baked NPC skins (npc/skins.json) in a studio, front and three-quarter, on the
## idle clip, into one sheet. Native opengl3 under xvfb:
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/npc_sheet.gd -- \
##     --group=mixamo --out=/tmp/npcs.png [--clip=walk] [--cols=8]
extends SceneTree
var out := "/tmp/npcs.png"
var group := "mixamo"
var clip := "idle"
var cols := 8
var vp: SubViewport
var cam: Camera3D
var root3d: Node3D
var items := []
var i := 0
var frames := 0
var tiles := []
var cur: NpcBody

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--group="): group = a.substr(8)
		elif a.begins_with("--clip="): clip = a.substr(7)
		elif a.begins_with("--cols="): cols = int(a.substr(7))
	vp = SubViewport.new(); vp.size = Vector2i(240, 400); vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	get_root().add_child(vp)
	root3d = Node3D.new(); vp.add_child(root3d)
	var env = WorldEnvironment.new(); var e = Environment.new()
	e.background_mode = Environment.BG_COLOR; e.background_color = Color(0.2, 0.2, 0.22)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.6, 0.6, 0.65); e.ambient_light_energy = 0.7
	env.environment = e; root3d.add_child(env)
	var sun = DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-40, 30, 0); sun.light_energy = 1.3; root3d.add_child(sun)
	var floor = MeshInstance3D.new(); floor.mesh = PlaneMesh.new(); floor.mesh.size = Vector2(8, 8); root3d.add_child(floor)
	cam = Camera3D.new(); cam.fov = 36; root3d.add_child(cam)
	for s in NpcBody.manifest().get("skins", []):
		if group == "all" or str(s.group) == group: items.append(s)
	print("skins: ", items.size())
	_load(0)

func _load(k: int) -> void:
	if cur: cur.queue_free(); cur = null
	if k >= items.size() * 2:
		_sheet(); quit(); return
	cur = NpcBody.new(); root3d.add_child(cur)
	cur.set_skin(items[k / 2])
	cur.set_self_light(0.18)
	cur.freeze(clip, 0.6)
	cur.face(Vector3(0, 0, 1) if k % 2 == 0 else Vector3(0.7, 0, 0.7))
	var h := float(items[k / 2].get("height_m", 1.75))
	cam.position = Vector3(0, h * 0.52, h * 1.75 + 0.3)
	frames = 0; i = k

func _process(_dt: float) -> bool:
	frames += 1
	if frames == 4:
		tiles.append([str(items[i / 2].id), vp.get_texture().get_image()])
		_load(i + 1)
	return false

func _sheet() -> void:
	var w := 240; var h := 400
	var rows := int(ceil(tiles.size() / float(cols)))
	var sheet := Image.create(cols * w, rows * h, false, tiles[0][1].get_format())
	for t in range(tiles.size()):
		sheet.blit_rect(tiles[t][1], Rect2i(0, 0, w, h), Vector2i((t % cols) * w, (t / cols) * h))
	sheet.save_png(out)
	var f := FileAccess.open(out + ".txt", FileAccess.WRITE)
	for t in range(tiles.size()): f.store_line(str(t) + " " + tiles[t][0])
	print("wrote ", out, " ", tiles.size(), " tiles")
