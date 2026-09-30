# File: main_cathedral_node.gd
extends Node3D

@onready var avatar_controller: AureliaAvatarController = $AureliaAvatarController

func _ready() -> void:
	print("[MLAOS-Prime] Cathedral-Engine Core online. Instantiating Sovereign Space.")
	if avatar_controller:
		avatar_controller.evaluate_stress_yield(0.92) # Triggers Harmonic Scar Crystallization

