#!/usr/bin/env python3
import os

os.makedirs("scripts", exist_ok=True)
os.makedirs("scenes", exist_ok=True)

# 1. Native GDScript: scripts/CathedralTransductionBridge.gd
bridge_gd = """extends Node3D
class_name CathedralTransductionBridge

@export var query_frequency_hz: float = 1.5
@export var joules_per_gas_credit: float = 1.0e-21

var _camera: Camera3D
var _last_camera_pos: Vector3
var _time_accumulator: float = 0.0
var _current_gas_pool: float = 125.0
var _current_merkle_root: String = "0x7F4C8E2B19A03D51"

func _ready() -> void:
    _camera = get_viewport().get_camera_3d()
    if _camera:
        _last_camera_pos = _camera.global_position
    print("[CathedralBridge GD] Initialized. Root: ", _current_merkle_root)

func _process(delta: float) -> void:
    _time_accumulator += delta
    var interval = 1.0 / query_frequency_hz
    if _time_accumulator >= interval:
        _time_accumulator -= interval
        _execute_cadence_tick(delta)

func _execute_cadence_tick(delta: float) -> void:
    if not _camera:
        return
    
    var current_pos = _camera.global_position
    var velocity = (current_pos - _last_camera_pos) / max(delta, 0.0001)
    _last_camera_pos = current_pos

    var space_state = get_world_3d().direct_space_state
    var ray_end = current_pos - _camera.global_transform.basis.z * 25.0
    var query = PhysicsRayQueryParameters3D.create(current_pos, ray_end)
    var hit = space_state.intersect_ray(query)

    if hit.size() > 0 and hit.collider and hit.collider.has_meta("opacity"):
        var opacity = float(hit.collider.get_meta("opacity"))
        if opacity < 0.40:
            var t_horizon = 293.15 / (opacity + 0.001)
            var work = 1.380649e-23 * t_horizon * 0.693147 * query_frequency_hz * (velocity.length() * 0.1 + 0.05)
            var minted = max(1, int(work / joules_per_gas_credit))
            _current_gas_pool += minted

            var parent_mesh = hit.collider.get_parent()
            if parent_mesh is MeshInstance3D and parent_mesh.material_override is ShaderMaterial:
                parent_mesh.material_override.set_shader_parameter("u_audit_intensity", clamp(velocity.length() * 0.2, 0.5, 3.0))

            print("[PoE Harvest] Minted: ", minted, " Credits | Pool: ", _current_gas_pool)
            if _current_gas_pool >= 60.0:
                _commit_block(30)

func _commit_block(count: int) -> void:
    _current_gas_pool -= count * 2
    var raw = _current_merkle_root + str(Time.get_ticks_msec()) + str(count)
    var ctx = HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(raw.to_utf8_buffer())
    var hash_bytes = ctx.finish()
    _current_merkle_root = "0x" + hash_bytes.hex().substr(0, 16).to_upper()
    print("[Ash Archive Commit] Block: ", _current_merkle_root, " | Balance: ", _current_gas_pool)
"""

with open("scripts/CathedralTransductionBridge.gd", "w", encoding="utf-8") as f:
    f.write(bridge_gd)
print("[1/4] Created scripts/CathedralTransductionBridge.gd")

# 2. Native GDScript: scripts/CathedralECTPipeline.gd
ect_gd = """extends Node3D
class_name CathedralECTPipeline

enum BelnapValue { TRUE, FALSE, BOTH, NEITHER }

class Entity:
    var position: Vector3
    var velocity: Vector3
    var epistemic_debt: float
    var landauer_burn_rate: float
    var monad_affinity: int
    var belnap: int

@export var initial_entity_count: int = 120
@export var torsion_vorticity_gamma: float = 1.25e-35

var _entities: Array = []
var _multi_mesh_instance: MultiMeshInstance3D
var _multi_mesh: MultiMesh

func _ready() -> void:
    _multi_mesh_instance = MultiMeshInstance3D.new()
    _multi_mesh = MultiMesh.new()
    _multi_mesh.transform_format = MultiMesh.TRANSFORM_3D
    _multi_mesh.use_colors = true
    _multi_mesh.instance_count = initial_entity_count
    
    var box = BoxMesh.new()
    box.size = Vector3(0.18, 0.18, 0.18)
    _multi_mesh.mesh = box
    _multi_mesh_instance.multimesh = _multi_mesh
    add_child(_multi_mesh_instance)

    for i in range(initial_entity_count):
        var e = Entity.new()
        e.position = Vector3(randf_range(-6.0, 6.0), randf_range(-2.0, 4.0), randf_range(-6.0, 6.0))
        e.velocity = Vector3(randf_range(-0.2, 0.2), 0, randf_range(-0.2, 0.2))
        e.epistemic_debt = randf_range(0.0, 0.5)
        e.landauer_burn_rate = 2.8e-21 * randf_range(1.0, 4.0)
        e.monad_affinity = randi_range(1, 12)
        e.belnap = BelnapValue.BOTH if (i % 5 == 0) else (BelnapValue.FALSE if (i % 8 == 0) else BelnapValue.TRUE)
        _entities.append(e)

    print("[ECT Pipeline GD] Initialized ", _entities.size(), " entities.")

func _process(delta: float) -> void:
    for i in range(_entities.size()):
        var e = _entities[i]
        e.position += e.velocity * delta
        if abs(e.position.x) > 8.0:
            e.velocity.x *= -1.0
        if abs(e.position.z) > 8.0:
            e.velocity.z *= -1.0

        var t = Transform3D(Basis(), e.position)
        _multi_mesh.set_instance_transform(i, t)

        var col: Color
        match e.belnap:
            BelnapValue.TRUE:
                col = Color(0.85, 0.68, 0.22)
            BelnapValue.FALSE:
                col = Color(0.12, 0.15, 0.20)
            BelnapValue.BOTH:
                col = Color(0.98, 0.85, 0.35)
            _:
                col = Color(0.78, 0.12, 0.22)
        _multi_mesh.set_instance_color(i, col)
"""

with open("scripts/CathedralECTPipeline.gd", "w", encoding="utf-8") as f:
    f.write(ect_gd)
print("[2/4] Created scripts/CathedralECTPipeline.gd")

# 3. Patch project.godot to load .gd instead of .cs
proj_path = "project.godot"
if os.path.exists(proj_path):
    with open(proj_path, "r", encoding="utf-8") as f:
        p = f.read()
    p = p.replace("res://scripts/CathedralTransductionBridge.cs", "res://scripts/CathedralTransductionBridge.gd")
    p = p.replace('"C#"', '"GDScript"')
    with open(proj_path, "w", encoding="utf-8") as f:
        f.write(p)
print("[3/4] Patched project.godot Autoload to use native GDScript.")

# 4. Patch scenes/ResidualMeaningShowcase.tscn
tscn_path = "scenes/ResidualMeaningShowcase.tscn"
if os.path.exists(tscn_path):
    with open(tscn_path, "r", encoding="utf-8") as f:
        s = f.read()
    s = s.replace("res://scripts/CathedralTransductionBridge.cs", "res://scripts/CathedralTransductionBridge.gd")
    s = s.replace("res://scripts/CathedralECTPipeline.cs", "res://scripts/CathedralECTPipeline.gd")
    with open(tscn_path, "w", encoding="utf-8") as f:
        f.write(s)
print("[4/4] Patched scenes/ResidualMeaningShowcase.tscn script references.")
print("Native GDScript conversion complete.")
