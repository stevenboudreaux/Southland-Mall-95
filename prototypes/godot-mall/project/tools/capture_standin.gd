## Captures one wing's storefronts from its own baked build, for the other wing's stand-in
## (design/godot-wings.md). For every slot listed in gen/w<other>/standin.json (written by
## tools/build_mall.gd), an orthographic camera stands STANDIN_OUT metres out in the hall facing the
## front and frames it floor to lane ceiling; the picture goes into its slot of the atlas
## tex/standin/from_w<wing>_<mode>.png. tools/capture_standin.sh runs it for both modes and writes a
## stamp (tex/standin/from_w<wing>.stamp): tools/publish_build.sh refuses to publish a stand-in taken
## from anything but the wing as it is now.
##
## The tone curve is linear at half exposure, with no glow or colour adjustment: the game shows
## the pictures unshaded at twice the brightness (build_mall.gd standin_mat), so its own tone
## mapping and glow apply once, as they do to the real shops.
##
## Run (needs a display: xvfb-run), from the project folder, after the wing's lightmaps are in:
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path . --rendering-driver opengl3 \
##     --script res://tools/capture_standin.gd -- --wing=2 --mode=night
## or tools/capture_standin.sh <wing> (both modes).
extends SceneTree

const SS := 2              # supersampling: rendered at twice the slot's size, then reduced
const SETTLE := 40         # frames before the first capture (reflection probes, shaders)
const PER_SLOT := 3        # frames per slot before reading it back
var wing := 2
var mode := "night"
var J: Dictionary
var slots: Array = []
var k := -1
var frames := 0
var wait := 0
var vp: SubViewport
var cam: Camera3D
var atlas: Image
var scn: Node

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="):
			wing = int(a.substr(7))
		elif a.begins_with("--mode="):
			mode = a.substr(7)
	var jp := "res://gen/w%d/standin.json" % (3 - wing)
	J = JSON.parse_string(FileAccess.get_file_as_string(jp))
	slots = J.slots
	print("capturing wing ", wing, " (", mode, "): ", slots.size(), " slots for ", jp)
	scn = load("res://wing%d.tscn" % wing).instantiate()
	# no player: its lighting switch would put the night setup back once it starts
	var pl0 = scn.get_node_or_null("Player")
	if pl0:
		scn.remove_child(pl0)
		pl0.free()
	root.add_child(scn)
	current_scene = scn
	var tod = load("res://scripts/time_of_day.gd")
	tod.apply(scn, mode)
	var lm = scn.get_node_or_null("LightmapGI")
	if lm == null or lm.light_data == null:
		push_error("no lightmap for wing %d %s: bake it and import it first" % [wing, mode])
	# the capture's tone curve (see the header)
	var envn = scn.get_node("Env")
	var env: Environment = envn.environment.duplicate()
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.tonemap_exposure = 0.5
	env.glow_enabled = false
	env.adjustment_enabled = false
	envn.environment = env
	atlas = Image.create(int(J.atlas[0]), int(J.atlas[1]), false, Image.FORMAT_RGB8)
	atlas.fill(Color(0, 0, 0))
	vp = SubViewport.new()
	vp.msaa_3d = Viewport.MSAA_4X
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.size = Vector2i(64, 64)
	cam = Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.keep_aspect = Camera3D.KEEP_HEIGHT
	cam.size = float(J.lane_h)
	cam.near = 0.01
	cam.far = 140.0
	vp.add_child(cam)
	root.add_child(vp)
	cam.current = true

func _slot_setup(s: Dictionary) -> void:
	var r: Array = s.rect
	vp.size = Vector2i(int(r[2]) * SS, int(r[3]) * SS)
	var a := Vector3(float(s.a[0]), 0, float(s.a[1]))
	var t := Vector3(float(s.t[0]), 0, float(s.t[1]))
	var n := Vector3(float(s.n[0]), 0, float(s.n[1]))
	var c := a + t * ((float(s.s0) + float(s.s1)) * 0.5) + n * float(J.out) + Vector3.UP * (float(J.lane_h) * 0.5)
	cam.global_transform = Transform3D(Basis.looking_at(-n, Vector3.UP), c)

func _process(_dt: float) -> bool:
	frames += 1
	if frames == 10:
		# once more, after everything has started: this mode's lightmap, lights and emission
		var envn = scn.get_node("Env")
		var keep: Environment = envn.environment
		load("res://scripts/time_of_day.gd").apply(scn, mode)
		envn.environment = keep
	if frames < SETTLE:
		return false
	if k == -1:
		k = 0
		_slot_setup(slots[0])
		wait = PER_SLOT
		return false
	wait -= 1
	if wait > 0:
		return false
	var s: Dictionary = slots[k]
	var r: Array = s.rect
	var im := vp.get_texture().get_image()
	im.convert(Image.FORMAT_RGB8)
	im.resize(int(r[2]), int(r[3]), Image.INTERPOLATE_LANCZOS)
	atlas.blit_rect(im, Rect2i(0, 0, int(r[2]), int(r[3])), Vector2i(int(r[0]), int(r[1])))
	k += 1
	if k % 10 == 0:
		print("  ", k, " / ", slots.size())
	if k >= slots.size():
		_finish()
		return true
	_slot_setup(slots[k])
	wait = PER_SLOT
	return false

func _finish() -> void:
	DirAccess.make_dir_recursive_absolute("res://tex/standin")
	var out := "res://tex/standin/from_w%d_%s.png" % [wing, mode]
	atlas.save_png(ProjectSettings.globalize_path(out))
	print("wrote ", out)
