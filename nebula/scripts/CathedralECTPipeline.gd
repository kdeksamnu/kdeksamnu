extends Node3D
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
