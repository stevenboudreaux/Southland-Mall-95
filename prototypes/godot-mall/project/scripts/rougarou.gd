## The Rougarou: the mall's first NPC (Steven, Oct 14 2026). The Cajun swamp monster of Acadiana's
## legend: a man's body with the head of a wolf or dog, said to shift between the two at will. Here
## it is a tall, gaunt, hunched figure in ragged black fur, digitigrade legs, long clawed hands,
## a short ragged tail, and two amber eyes that catch the light. Our own design from the folklore
## (no film or game creature): the Audubon Zoo's sign, the swamp painting and the animatronic Steven
## sent are the mood, not a model.
##
## Built from primitives at runtime (no model file): a joint tree of Node3D pivots carrying tapered
## cylinders and spheres, with ragged fur as MultiMesh spikes riding each part. Procedural
## animation: breathing and a slow head scan while it stands; a loping run; the head turns to a
## watched point. Behaviour (when it appears, where it bolts to) lives in scripts/rougarou_ai.gd;
## this file is only the body. Faces -Z, like a camera.
##
## Sizes: standing upright it would be about 2.3 m; hunched, as it almost always is, the top of
## its head is about 1.9 m up. Tunable at the top.
class_name Rougarou
extends Node3D

const HIP_H = 1.16           # hip joint height when standing (long digitigrade legs)
const FUR = Color("#15110e")
const FUR_LIGHT = Color("#241a13")
const SKIN = Color("#1b1410")
const CLAW = Color("#4a4642")
const TEETH = Color("#ece4cf")
const EYE = Color("#ffb13a")

var J := {}                  # joints by name: Node3D pivots
var rest := {}               # rest rotation per joint (Vector3, degrees)
var t := 0.0
var hunch := 0.85            # 0 upright .. 1 deeply hunched
var gait := 0.0              # 0 standing .. 1 running
var watch: Vector3 = Vector3.INF   # world point the head turns to; INF for none
var rng := RandomNumberGenerator.new()
var m_fur: StandardMaterial3D
var m_fur2: StandardMaterial3D
var m_skin: StandardMaterial3D
var m_claw: StandardMaterial3D
var m_teeth: StandardMaterial3D
var m_eye: StandardMaterial3D
var spike_mesh: Mesh

func _ready() -> void:
	rng.seed = 1995
	_materials()
	build()

func _materials() -> void:
	m_fur = StandardMaterial3D.new(); m_fur.albedo_color = FUR; m_fur.roughness = 1.0; m_fur.metallic_specular = 0.08
	m_fur2 = StandardMaterial3D.new(); m_fur2.albedo_color = FUR_LIGHT; m_fur2.roughness = 1.0; m_fur2.metallic_specular = 0.1
	m_skin = StandardMaterial3D.new(); m_skin.albedo_color = SKIN; m_skin.roughness = 0.75; m_skin.metallic_specular = 0.3
	m_claw = StandardMaterial3D.new(); m_claw.albedo_color = CLAW; m_claw.roughness = 0.35; m_claw.metallic_specular = 0.5
	m_teeth = StandardMaterial3D.new(); m_teeth.albedo_color = TEETH; m_teeth.roughness = 0.4
	m_eye = StandardMaterial3D.new(); m_eye.albedo_color = EYE; m_eye.emission_enabled = true
	m_eye.emission = EYE; m_eye.emission_energy_multiplier = 3.0; m_eye.roughness = 0.2
	var sp = CylinderMesh.new(); sp.top_radius = 0.0; sp.bottom_radius = 0.009; sp.height = 0.15
	sp.radial_segments = 4; sp.rings = 1; sp.material = m_fur
	spike_mesh = sp

# ------------------------------------------------------------------ building
func _pivot(parent: Node3D, name: String, pos: Vector3, rot_deg: Vector3) -> Node3D:
	var p = Node3D.new(); p.name = name; p.position = pos
	p.rotation_degrees = rot_deg
	parent.add_child(p)
	J[name] = p; rest[name] = rot_deg
	return p

## A tapered limb hanging down -Y from its joint: r0 at the joint, r1 at the end, L long.
func _limb(joint: Node3D, L: float, r0: float, r1: float, mat: Material, fur := 0) -> void:
	var cy = CylinderMesh.new(); cy.top_radius = r0; cy.bottom_radius = r1; cy.height = L
	cy.radial_segments = 10; cy.rings = 1; cy.material = mat
	var mi = MeshInstance3D.new(); mi.mesh = cy; mi.position = Vector3(0, -L * 0.5, 0)
	joint.add_child(mi)
	var s = SphereMesh.new(); s.radius = r0 * 1.05; s.height = r0 * 2.1; s.radial_segments = 10; s.rings = 6; s.material = mat
	var js = MeshInstance3D.new(); js.mesh = s; joint.add_child(js)
	if fur > 0:
		_fur(joint, fur, L, r0, r1)

## Ragged fur: n spikes on the surface of a limb, pointing out and drooping down.
func _fur(joint: Node3D, n: int, L: float, r0: float, r1: float, droop := 0.9) -> void:
	var mm = MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = spike_mesh; mm.instance_count = n
	for i in n:
		var a = rng.randf() * TAU
		var y = rng.randf() * L
		var r = lerp(r0, r1, y / L) * 0.9
		var p = Vector3(cos(a) * r, -y, sin(a) * r)
		var out = Vector3(cos(a), 0, sin(a))
		var dir = (out * (1.0 - droop * 0.75) + Vector3.DOWN * droop * 1.6 + Vector3(rng.randf() - 0.5, 0, rng.randf() - 0.5) * 0.3).normalized()
		var sc = 0.6 + rng.randf() * 0.9
		mm.set_instance_transform(i, Transform3D(_basis_y(dir).scaled(Vector3(sc, sc, sc)), p + dir * 0.08 * sc))
	var mi = MultiMeshInstance3D.new(); mi.multimesh = mm
	joint.add_child(mi)

func _basis_y(dir: Vector3) -> Basis:
	var y = dir.normalized()
	var x = y.cross(Vector3.UP)
	if x.length() < 0.01: x = Vector3.RIGHT
	x = x.normalized()
	return Basis(x, y, x.cross(y))

func _ball(parent: Node3D, pos: Vector3, r: float, mat: Material, sx := 1.0, sy := 1.0, sz := 1.0) -> MeshInstance3D:
	var s = SphereMesh.new(); s.radius = r; s.height = r * 2.0; s.radial_segments = 12; s.rings = 8; s.material = mat
	var mi = MeshInstance3D.new(); mi.mesh = s; mi.position = pos; mi.scale = Vector3(sx, sy, sz)
	parent.add_child(mi)
	return mi

func _cone(parent: Node3D, pos: Vector3, dir: Vector3, r: float, L: float, mat: Material) -> void:
	var c = CylinderMesh.new(); c.top_radius = 0.0; c.bottom_radius = r; c.height = L; c.radial_segments = 8; c.rings = 1; c.material = mat
	var mi = MeshInstance3D.new(); mi.mesh = c
	mi.transform = Transform3D(_basis_y(dir), pos + dir.normalized() * L * 0.5)
	parent.add_child(mi)

func build() -> void:
	# hips: the root of the body. The figure stands on the ground at y = 0 and faces -Z.
	var hips = _pivot(self, "hips", Vector3(0, HIP_H, 0), Vector3.ZERO)
	_ball(hips, Vector3.ZERO, 0.16, m_fur, 1.1, 0.8, 0.9)
	# spine, pitched forward into the hunch (set in _pose), then the chest and shoulders
	var spine = _pivot(hips, "spine", Vector3(0, 0.08, 0), Vector3(0, 0, 0))
	var chest = _pivot(spine, "chest", Vector3(0, 0.56, 0), Vector3.ZERO)
	var torso = CylinderMesh.new(); torso.top_radius = 0.24; torso.bottom_radius = 0.15; torso.height = 0.6; torso.radial_segments = 12; torso.material = m_fur
	var tmi = MeshInstance3D.new(); tmi.mesh = torso; tmi.position = Vector3(0, 0.3, 0); spine.add_child(tmi)
	_ball(chest, Vector3(0, 0.0, 0.0), 0.27, m_fur, 1.2, 0.75, 0.95)
	_ball(chest, Vector3(0, -0.12, -0.14), 0.17, m_fur2, 0.9, 0.9, 0.5)   # the chest's lighter front
	_fur(chest, 190, 0.5, 0.28, 0.2, 0.95)                                 # the mane over the shoulders
	_fur(spine, 50, 0.55, 0.16, 0.24, 0.95)
	# neck and head, thrust forward
	var neck = _pivot(chest, "neck", Vector3(0, 0.12, -0.1), Vector3.ZERO)
	var nk = CylinderMesh.new(); nk.top_radius = 0.1; nk.bottom_radius = 0.13; nk.height = 0.26; nk.radial_segments = 10; nk.material = m_fur
	var nmi = MeshInstance3D.new(); nmi.mesh = nk; nmi.position = Vector3(0, 0.13, 0); neck.add_child(nmi)
	var head = _pivot(neck, "head", Vector3(0, 0.26, 0), Vector3.ZERO)
	_head(head)
	# arms: long, hanging; shoulders wide
	for side in [-1.0, 1.0]:
		var sname = "l" if side < 0 else "r"
		var sh = _pivot(chest, sname + "_sh", Vector3(0.3 * side, 0.04, 0.0), Vector3(0, 0, 0))
		_limb(sh, 0.62, 0.085, 0.06, m_fur, 18)
		var el = _pivot(sh, sname + "_el", Vector3(0, -0.62, 0), Vector3.ZERO)
		_limb(el, 0.6, 0.06, 0.045, m_fur, 16)
		var wr = _pivot(el, sname + "_wr", Vector3(0, -0.6, 0), Vector3.ZERO)
		_hand(wr, side)
		# legs: digitigrade. Thigh forward-down, shin back, a long foot (metatarsus) down to toes.
		var hp = _pivot(hips, sname + "_hip", Vector3(0.13 * side, -0.04, 0), Vector3.ZERO)
		_limb(hp, 0.55, 0.1, 0.065, m_fur, 18)
		var kn = _pivot(hp, sname + "_knee", Vector3(0, -0.55, 0), Vector3.ZERO)
		_limb(kn, 0.5, 0.065, 0.045, m_fur, 12)
		var an = _pivot(kn, sname + "_ank", Vector3(0, -0.5, 0), Vector3.ZERO)
		_limb(an, 0.28, 0.045, 0.04, m_fur, 6)
		var ft = _pivot(an, sname + "_foot", Vector3(0, -0.28, 0), Vector3.ZERO)
		_foot(ft)
	# a short ragged tail
	var t1 = _pivot(hips, "tail1", Vector3(0, 0.0, 0.14), Vector3(-35, 0, 0))
	_limb(t1, 0.32, 0.055, 0.05, m_fur, 40)
	var t2 = _pivot(t1, "tail2", Vector3(0, -0.32, 0), Vector3(18, 0, 0))
	_limb(t2, 0.3, 0.05, 0.04, m_fur, 40)
	var t3 = _pivot(t2, "tail3", Vector3(0, -0.3, 0), Vector3(14, 0, 0))
	_limb(t3, 0.28, 0.04, 0.015, m_fur, 36)
	_pose(0.0)

func _head(head: Node3D) -> void:
	_ball(head, Vector3(0, 0.04, 0.02), 0.15, m_fur, 1.0, 0.95, 1.05)        # cranium
	_fur(head, 30, 0.1, 0.16, 0.16, 0.7)                                    # ragged ruff
	# the muzzle: a tapered block forward, the jaw below it, slightly open
	var mz = CylinderMesh.new(); mz.top_radius = 0.04; mz.bottom_radius = 0.1; mz.height = 0.32; mz.radial_segments = 8; mz.material = m_fur
	var mmi = MeshInstance3D.new(); mmi.mesh = mz
	mmi.transform = Transform3D(_basis_y(Vector3(0, -0.1, -1)), Vector3(0, -0.005, -0.22))
	mmi.scale = Vector3(0.8, 1.0, 1.0)
	head.add_child(mmi)
	_ball(head, Vector3(0, 0.07, -0.1), 0.11, m_fur, 1.25, 0.6, 1.0)          # the brow
	var mf = Node3D.new(); mf.position = Vector3(0, 0.05, -0.1); mf.rotation_degrees = Vector3(-80, 0, 0); head.add_child(mf)
	_fur(mf, 30, 0.22, 0.08, 0.05, 0.3)                                      # fur down the bridge of the muzzle
	_ball(head, Vector3(0, 0.012, -0.385), 0.026, m_skin)                     # nose
	var jaw = _pivot(head, "jaw", Vector3(0, -0.06, -0.06), Vector3(24, 0, 0))
	var jm = CylinderMesh.new(); jm.top_radius = 0.03; jm.bottom_radius = 0.065; jm.height = 0.27; jm.radial_segments = 8; jm.material = m_fur2
	var jmi = MeshInstance3D.new(); jmi.mesh = jm
	jmi.transform = Transform3D(_basis_y(Vector3(0, 0.02, -1)), Vector3(0, -0.02, -0.16))
	jaw.add_child(jmi)
	# teeth: four down from the muzzle, three up from the jaw
	for i in 5:
		var z = -0.12 - i * 0.055
		for side in [-1.0, 1.0]:
			_cone(head, Vector3(0.05 * side * (1.0 - i * 0.12), -0.055, z), Vector3(0, -1, 0), 0.009, 0.04 if i == 0 else 0.028, m_teeth)
	for i in 4:
		var z = -0.1 - i * 0.055
		for side in [-1.0, 1.0]:
			_cone(jaw, Vector3(0.04 * side * (1.0 - i * 0.12), 0.0, z), Vector3(0, 1, 0), 0.008, 0.035 if i == 0 else 0.024, m_teeth)
	# eyes: amber, forward-set, in a shallow socket of darker skin
	for side in [-1.0, 1.0]:
		_ball(head, Vector3(0.068 * side, 0.055, -0.12), 0.036, m_skin)
		_ball(head, Vector3(0.068 * side, 0.058, -0.135), 0.024, m_eye)
	# ears: tall, torn, canted outward
	for side in [-1.0, 1.0]:
		_cone(head, Vector3(0.08 * side, 0.12, 0.08), Vector3(0.4 * side, 0.9, 0.55), 0.04, 0.19, m_fur)   # laid back

func _hand(wr: Node3D, side: float) -> void:
	var palm = BoxMesh.new(); palm.size = Vector3(0.1, 0.13, 0.05); palm.material = m_skin
	var pm = MeshInstance3D.new(); pm.mesh = palm; pm.position = Vector3(0, -0.07, 0); wr.add_child(pm)
	for i in 4:
		var x = (i - 1.5) * 0.03
		var fp = _pivot(wr, "f%d_%d" % [int(side + 1), i], Vector3(x, -0.13, 0), Vector3(-15, 0, 0))
		var f = CylinderMesh.new(); f.top_radius = 0.008; f.bottom_radius = 0.012; f.height = 0.17; f.radial_segments = 6; f.material = m_skin
		var fm = MeshInstance3D.new(); fm.mesh = f; fm.position = Vector3(0, -0.085, 0); fp.add_child(fm)
		_cone(fp, Vector3(0, -0.17, 0), Vector3(0, -0.75, -0.65), 0.01, 0.11, m_claw)
	# a thumb
	_cone(wr, Vector3(0.06 * side, -0.07, -0.01), Vector3(0.6 * side, -0.7, -0.5), 0.013, 0.1, m_claw)

func _foot(ft: Node3D) -> void:
	var f = CylinderMesh.new(); f.top_radius = 0.05; f.bottom_radius = 0.04; f.height = 0.2; f.radial_segments = 8; f.material = m_skin
	var fm = MeshInstance3D.new(); fm.mesh = f
	fm.transform = Transform3D(_basis_y(Vector3(0, 0, -1)), Vector3(0, 0.03, -0.1))
	ft.add_child(fm)
	for i in 3:
		var x = (i - 1) * 0.045
		_cone(ft, Vector3(x, 0.03, -0.2), Vector3(0, -0.35, -1), 0.014, 0.1, m_claw)

# ------------------------------------------------------------------ posing
## Sets the rest pose for a hunch amount h (0..1); animation adds to it each frame.
func _pose(_h: float) -> void:
	# The stoop of the old engraving ("Le Rougarou, animal légendaire des Bayous de la Louisiane",
	# Steven's paradigm, Oct 14 16:50): the back arched into a hump at the shoulders, the head thrust
	# forward with the snout down, the arms hanging straight down past the knees, the legs bent in
	# a stride, the tail to the ground.
	var h = hunch
	var spine = -(10.0 + 24.0 * h)                          # negative x pitches the top forward (-Z)
	var chest = -(4.0 + 22.0 * h)                           # the hump
	rest["spine"] = Vector3(spine, 0, 0)
	rest["chest"] = Vector3(chest, 0, 0)
	var tilt = -(spine + chest)                             # how far the shoulders lean, degrees
	rest["neck"] = Vector3(tilt - 30.0, 0, 0)               # the neck back up to 30° short of level
	rest["head"] = Vector3(15.0, 0, 0)                      # snout about 15° below level
	rest["jaw"] = Vector3(24, 0, 0)
	for s in ["l", "r"]:
		var side = -1.0 if s == "l" else 1.0
		var fwd = 1.0 if s == "l" else -1.0                  # the left leg leads the stride
		rest[s + "_sh"] = Vector3(tilt - 14.0, 0, 6.0 * side)  # arms hang down, a little forward
		rest[s + "_el"] = Vector3(-12.0, 0, 0)
		rest[s + "_wr"] = Vector3(-24.0, 0, -8.0 * side)
		rest[s + "_hip"] = Vector3(-(14.0 + 12.0 * h) - 22.0 * fwd * h, 0, 3.0 * side)
		rest[s + "_knee"] = Vector3(40.0 + 16.0 * h + 22.0 * fwd * h, 0, 0)
		rest[s + "_ank"] = Vector3(-(38.0 + 8.0 * h) - 4.0 * fwd * h, 0, 0)
		rest[s + "_foot"] = Vector3(12.0 + 4.0 * h, 0, 0)
	rest["tail1"] = Vector3(-35.0, 0, 0); rest["tail2"] = Vector3(18.0, 0, 0); rest["tail3"] = Vector3(14.0, 0, 0)
	# hip height drops with the hunch and the stride so the feet stay on the floor
	J["hips"].position.y = HIP_H - 0.16 * h
	for k in rest:
		if J.has(k):
			J[k].rotation_degrees = rest[k]

func _process(dt: float) -> void:
	t += dt
	_pose(hunch)
	var g = clamp(gait, 0.0, 1.0)
	# breathing and a slow sway while standing
	var br = sin(t * 1.4) * (1.0 - g)
	J["spine"].rotation_degrees.x += br * 1.2
	J["chest"].rotation_degrees.x += br * 0.8
	J["chest"].scale = Vector3(1.0 + br * 0.012, 1.0 + br * 0.02, 1.0 + br * 0.012)
	J["hips"].rotation_degrees.z = sin(t * 0.37) * 1.3 * (1.0 - g)
	J["tail1"].rotation_degrees.z = sin(t * 0.9) * 6.0
	J["tail2"].rotation_degrees.z = sin(t * 0.9 - 0.7) * 8.0
	# the run: a lope, legs and arms crossing, the body bobbing and leaning in
	if g > 0.0:
		var w = t * 6.4
		var leg = sin(w) * 38.0 * g
		var arm = sin(w) * 26.0 * g
		J["l_hip"].rotation_degrees.x += -leg; J["r_hip"].rotation_degrees.x += leg
		J["l_knee"].rotation_degrees.x += max(0.0, -sin(w - 0.9)) * 50.0 * g
		J["r_knee"].rotation_degrees.x += max(0.0, sin(w - 0.9)) * 50.0 * g
		J["l_sh"].rotation_degrees.x += arm; J["r_sh"].rotation_degrees.x += -arm
		J["l_el"].rotation_degrees.x += -(18.0 + 12.0 * sin(w)) * g; J["r_el"].rotation_degrees.x += -(18.0 - 12.0 * sin(w)) * g
		J["spine"].rotation_degrees.x -= 10.0 * g
		J["hips"].position.y += abs(sin(w)) * 0.06 * g
		J["hips"].rotation_degrees.y = sin(w) * 5.0 * g
		J["jaw"].rotation_degrees.x += 10.0 * g
	# the head turns to the watched point (clamped), else scans slowly
	var head = J["head"]; var neck = J["neck"]
	if watch != Vector3.INF:
		var local = neck.to_local(watch)
		var yaw = clamp(rad_to_deg(atan2(-local.x, -local.z)), -70.0, 70.0)
		var up = clamp(rad_to_deg(atan2(local.y, Vector2(local.x, local.z).length())), -25.0, 30.0)
		neck.rotation_degrees.y = yaw * 0.45
		head.rotation_degrees.y = yaw * 0.55
		head.rotation_degrees.x += up * 0.8
	else:
		neck.rotation_degrees.y = sin(t * 0.23) * 22.0
		head.rotation_degrees.y = sin(t * 0.23 + 0.4) * 18.0
		head.rotation_degrees.z = sin(t * 0.11) * 4.0
	# an occasional ear twitch
	if fmod(t, 4.7) < 0.12:
		head.rotation_degrees.z += 2.5

## Where the eyes are, in world space (the AI uses it to test whether the player can see them).
func eye_pos() -> Vector3:
	return J["head"].to_global(Vector3(0, 0.058, -0.135))
