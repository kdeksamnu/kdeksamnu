extends Node3D
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
