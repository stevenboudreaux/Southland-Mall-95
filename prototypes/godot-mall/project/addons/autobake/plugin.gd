@tool
extends EditorPlugin
## The bake jobs come from the AUTOBAKE environment variable (cloud) or, when
## the editor is opened from the Mac's Project Manager, from a one-shot file
## res://.autobake (deleted on pickup): "warm", or one or more jobs separated by spaces,
## each "<scene>:<mode>" (e.g. "wing1:night wing1:day wing2:night wing2:day"; a bare mode
## means wing1). Mode "night" or "day", or "fastnight" / "fastday" for a quick Medium bake.
## Each job bakes res://<scene>_<mode>.lmbake; the editor quits after the last one and
## writes res://.autobake_done listing what it baked.
var _mode := ""
func _enter_tree():
	_mode = OS.get_environment("AUTOBAKE")
	if _mode == "" and FileAccess.file_exists("res://.autobake"):
		_mode = FileAccess.get_file_as_string("res://.autobake").strip_edges()
		DirAccess.remove_absolute(ProjectSettings.globalize_path("res://.autobake"))
	if _mode == "": return
	_run.call_deferred()
func _find_buttons(n:Node, out:Array):
	if n is Button: out.append(n)
	for c in n.get_children(): _find_buttons(c, out)
func _run():
	await get_tree().create_timer(2.0).timeout
	var jobs = []
	for j in _mode.split(" ", false):
		var parts = j.split(":")
		if parts.size() == 1:
			jobs.append(["wing1", parts[0]])
		else:
			jobs.append([parts[0], parts[1]])
	var done = []
	for job in jobs:
		var r = await _bake(job[0], job[1])
		done.append("%s:%s %s" % [job[0], job[1], r])
		var df = FileAccess.open("res://.autobake_done", FileAccess.WRITE)
		df.store_string("\n".join(done) + "\n")
		df.close()
	get_tree().quit()

func _bake(scene_name, mode):
	EditorInterface.open_scene_from_path("res://%s.tscn" % scene_name)
	await get_tree().create_timer(5.0).timeout
	var fs = EditorInterface.get_resource_filesystem()
	var w = 0
	while fs.is_scanning() and w < 600:
		await get_tree().create_timer(1.0).timeout
		w += 1
	await get_tree().create_timer(10.0).timeout
	print("IMPORT SETTLED after ", w)
	if mode == "warm":
		EditorInterface.save_scene()
		await get_tree().create_timer(2.0).timeout
		return "warm"
	var root = EditorInterface.get_edited_scene_root()
	var lm = root.find_child("LightmapGI", true, false)
	var fast = mode.begins_with("fast")
	if fast:
		mode = mode.substr(4)
	if mode != "day":
		mode = "night"
	load("res://scripts/time_of_day.gd").apply(root, mode, false)
	lm.light_data = null
	var keep_quality = lm.quality
	if fast:
		lm.quality = LightmapGI.BAKE_QUALITY_MEDIUM
	print("MODE ", scene_name, " ", mode)
	EditorInterface.get_selection().clear()
	EditorInterface.get_selection().add_node(lm)
	EditorInterface.edit_node(lm)
	await get_tree().create_timer(1.0).timeout
	var bs = []
	_find_buttons(EditorInterface.get_base_control(), bs)
	var found = false
	for b in bs:
		if b.text.findn("bake lightmap") >= 0 and b.is_visible_in_tree():
			print("PRESS ", b.text); b.emit_signal("pressed"); found = true; break
	if not found:
		for b in bs:
			if b.text.findn("bake") >= 0: print("cand: ", b.text, " vis=", b.is_visible_in_tree())
	await get_tree().create_timer(2.0).timeout
	_dump(EditorInterface.get_base_control().get_tree().root)
	var fd = _find_fd(get_tree().root)
	if fd:
		var path = root.scene_file_path.get_basename() + "_" + mode + ".lmbake"
		print("SELECT ", path)
		fd.hide()
		fd.file_selected.emit(path)
	var t = 0
	while t < 3600:
		await get_tree().create_timer(1.0).timeout
		t += 1
		if lm.light_data != null: break
	print("LIGHTDATA ", lm.light_data, " after ", t)
	lm.quality = keep_quality
	EditorInterface.save_scene()
	await get_tree().create_timer(3.0).timeout
	return "ok %ds" % t if lm.light_data != null else "FAILED"

func _dump(n:Node):
	if n is Window and n.visible and n != get_tree().root:
		var txt = ""
		if n is AcceptDialog: txt = n.dialog_text
		print("WINDOW ", n.get_class(), " title=", n.title, " text=", txt)
		if n is FileDialog: print("  filedialog dir=", n.current_dir, " file=", n.current_file)
	for c in n.get_children(): _dump(c)

func _find_fd(n:Node):
	if n is EditorFileDialog and n.visible: return n
	for c in n.get_children():
		var r = _find_fd(c)
		if r: return r
	return null
