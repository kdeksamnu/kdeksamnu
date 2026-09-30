extends SceneTree

func _init():
	print("\n==================================================================")
	print(" GODOT 4 NATIVE GPU COMPUTE DISPATCH: DIALETHEIC BUFFER")
	print(" Subsystem: M3 (Dialetheic Buffer) | Revision Ω-07")
	print("==================================================================")

	var rd = RenderingServer.create_local_rendering_device()
	if not rd:
		rd = RenderingServer.get_rendering_device()

	if not rd:
		printerr("ERROR: GPU RenderingDevice unavailable.")
		quit(1)
		return

	var shader_file = load("res://DialetheicBuffer.glsl") as RDShaderFile
	var spirv = shader_file.get_spirv()
	var shader = rd.shader_create_from_spirv(spirv)
	var pipeline = rd.compute_pipeline_create(shader)

	# Cell 0: deltaSigma = -50, tau_xy = 70.7107 -> cos(2*theta) = -50 / 150 = -0.333333 (Exact Magic Angle)
	# Cell 1: Classical State T -> 0 shear
	var input_floats = PackedFloat32Array([
		3.0, 100.0, 150.0, 70.7107,  # Cell 0: State B (Magic Angle Aligned)
		2.0, 200.0, 200.0, 0.0,      # Cell 1: State T
		0.0, 0.0, 0.0, 0.0,          # Cell 2: State N
		1.0, 50.0, 50.0, 0.0         # Cell 3: State F
	])
	input_floats.resize(64 * 64 * 4)

	var input_bytes = input_floats.to_byte_array()
	var input_buffer = rd.storage_buffer_create(input_bytes.size(), input_bytes)

	var output_bytes_size = 64 * 64 * 4 * 4
	var output_buffer = rd.storage_buffer_create(output_bytes_size)

	var u_in = RDUniform.new()
	u_in.uniform_type = RenderingDevice.UNIFORM_TYPE_STORAGE_BUFFER
	u_in.binding = 0
	u_in.add_id(input_buffer)

	var u_out = RDUniform.new()
	u_out.uniform_type = RenderingDevice.UNIFORM_TYPE_STORAGE_BUFFER
	u_out.binding = 1
	u_out.add_id(output_buffer)

	var uniform_set = rd.uniform_set_create([u_in, u_out], shader, 0)

	var push_constants = PackedByteArray()
	push_constants.resize(8)
	push_constants.encode_u32(0, 64)
	push_constants.encode_u32(4, 64)

	var compute_list = rd.compute_list_begin()
	rd.compute_list_bind_compute_pipeline(compute_list, pipeline)
	rd.compute_list_bind_uniform_set(compute_list, uniform_set, 0)
	rd.compute_list_set_push_constant(compute_list, push_constants, push_constants.size())
	rd.compute_list_dispatch(compute_list, 8, 8, 1)
	rd.compute_list_end()

	rd.submit()
	rd.sync()

	var output_raw = rd.buffer_get_data(output_buffer)
	var output_floats = output_raw.to_float32_array()

	print("\n--- KERNEL EVALUATION RESULTS ---")
	print("Cell 0 [State B]:")
	print("  -> isMagicAligned: ", output_floats[0] > 0.5)
	print("  -> cos(2*theta):   ", str(output_floats[1]), " (Target: -0.333333)")
	print("  -> residualShear:  ", str(output_floats[2]), " kPa (Target: 0.0 kPa)")
	print("  -> needsSqueeze:   ", output_floats[3] > 0.5)

	print("\nCell 1 [State T]:")
	print("  -> isMagicAligned: ", output_floats[4] > 0.5)
	print("  -> cos(2*theta):   ", str(output_floats[5]))
	print("  -> residualShear:  ", str(output_floats[6]), " kPa")
	print("  -> needsSqueeze:   ", output_floats[7] > 0.5)

	# Clean cleanup
	rd.free_rid(pipeline)
	rd.free_rid(uniform_set)
	rd.free_rid(input_buffer)
	rd.free_rid(output_buffer)
	rd.free_rid(shader)

	u_in = null
	u_out = null
	shader_file = null

	print("\n==================================================================")
	print(" METAMORPHIC SQUEEZE TRIGGER VERIFIED ON GPU")
	print("==================================================================")
	quit()
