@tool
extends EditorPlugin
func _enter_tree():
	if not OS.get_environment("AUTOBAKE"): return
	_run.call_deferred()
func _find_buttons(n:Node, out:Array):
	if n is Button: out.append(n)
	for c in n.get_children(): _find_buttons(c, out)
func _run():
	await get_tree().create_timer(2.0).timeout
	EditorInterface.open_scene_from_path("res://main.tscn")
	await get_tree().create_timer(5.0).timeout
	var fs = EditorInterface.get_resource_filesystem()
	var w = 0
	while fs.is_scanning() and w < 600:
		await get_tree().create_timer(1.0).timeout
		w += 1
	await get_tree().create_timer(10.0).timeout
	print("IMPORT SETTLED after ", w)
	if OS.get_environment("AUTOBAKE") == "warm":
		EditorInterface.save_scene()
		await get_tree().create_timer(2.0).timeout
		get_tree().quit()
		return
	var root = EditorInterface.get_edited_scene_root()
	var lm = root.find_child("LightmapGI", true, false)
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
		var path = root.scene_file_path.get_basename() + ".lmbake"
		print("SELECT ", path)
		fd.hide()
		fd.file_selected.emit(path)
	var t = 0
	while t < 3600:
		await get_tree().create_timer(1.0).timeout
		t += 1
		if lm.light_data != null: break
	print("LIGHTDATA ", lm.light_data, " after ", t)
	EditorInterface.save_scene()
	await get_tree().create_timer(1.0).timeout
	get_tree().quit()

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
