extends SceneTree

func _init() -> void:
	print("\n=== Initializing Terminal Pipeline Verification ===")
	var scene_res = load("res://scenes/AvatarPipelineHarness.tscn")
	if not scene_res:
		printerr("[FAIL] Unable to load scene resource.")
		quit(1)
		return
	
	var root = scene_res.instantiate()
	root_node_test(root)

func root_node_test(root: Node) -> void:
	var controller = root.get_node_or_null("ShaderController") as CathedralShaderPipeline
	var mesh = root.get_node_or_null("AvatarMesh") as MeshInstance3D
	
	assert(controller != null, "ShaderController node missing")
	assert(mesh != null, "AvatarMesh node missing")
	
	controller._ready()
	
	# Validate dialetheic contradiction assignment
	controller.update_dialetheic_vector(0.0, 0.0, 1.0, 0.0, 2.5)
	var mat = mesh.material_override as ShaderMaterial
	var state_vec = mat.get_shader_parameter("dialetheic_state")
	var tension = mat.get_shader_parameter("tension_intensity")
	
	print("[VERIFIED] Dialetheic Vector:", state_vec)
	print("[VERIFIED] Tension Intensity:", tension)
	
	if state_vec == Vector4(0, 0, 1, 0) and tension == 2.5:
		print("[PASS] Godot shader uniform registers successfully mapped.")
		quit(0)
	else:
		printerr("[FAIL] Parameter mismatch in uniform registers.")
		quit(1)
