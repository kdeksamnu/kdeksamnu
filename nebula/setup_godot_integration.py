#!/usr/bin/env python3
import os

os.makedirs("scenes", exist_ok=True)
os.makedirs("shaders", exist_ok=True)
os.makedirs("scripts", exist_ok=True)

# 1. Register CathedralTransductionBridge as an Autoload in project.godot
project_godot_path = "project.godot"
autoload_line = 'CathedralTransductionBridge="*res://scripts/CathedralTransductionBridge.cs"\n'

if os.path.exists(project_godot_path):
    with open(project_godot_path, "r", encoding="utf-8") as f:
        content = f.read()
else:
    content = """; Engine configuration file.
config_version=5

[application]

config/name="Cathedral-Engine // Nebula"
run/main_scene="res://scenes/ResidualMeaningShowcase.tscn"
config/features=PackedStringArray("4.3", "C#", "Forward Plus")
"""

if "[autoload]" in content:
    if "CathedralTransductionBridge" not in content:
        content = content.replace("[autoload]", "[autoload]\n" + autoload_line)
else:
    content += "\n[autoload]\n\n" + autoload_line

with open(project_godot_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[1/3] Updated project.godot: CathedralTransductionBridge registered as Autoload.")

# 2. Build complete interactive 3D scene (ResidualMeaningShowcase.tscn)
# Applying shader and metadata on interactive meshes with collision shapes
tscn_content = """[gd_scene load_steps=7 format=3 uid="uid://c3m7r2q4k1b8p"]

[ext_resource type="Shader" path="res://shaders/cathedral_chroma_omega.gdshader" id="1_shader"]
[ext_resource type="Script" path="res://scripts/CathedralTransductionBridge.cs" id="2_bridge"]

[sub_resource type="ShaderMaterial" id="ShaderMaterial_m1"]
render_priority = 0
shader = ExtResource("1_shader")
shader_parameter/u_monad_id = 1
shader_parameter/u_opacity = 0.95
shader_parameter/u_audit_intensity = 0.0
shader_parameter/u_scar_cost = 0.12

[sub_resource type="ShaderMaterial" id="ShaderMaterial_m2"]
render_priority = 0
shader = ExtResource("1_shader")
shader_parameter/u_monad_id = 2
shader_parameter/u_opacity = 0.20
shader_parameter/u_audit_intensity = 0.0
shader_parameter/u_scar_cost = 0.28

[sub_resource type="ShaderMaterial" id="ShaderMaterial_m11"]
render_priority = 0
shader = ExtResource("1_shader")
shader_parameter/u_monad_id = 11
shader_parameter/u_opacity = 0.98
shader_parameter/u_audit_intensity = 0.0
shader_parameter/u_scar_cost = 0.30

[sub_resource type="SphereShape3D" id="SphereShape3D_omission"]
radius = 1.0

[node name="ResidualMeaningShowcase" type="Node3D"]
script = ExtResource("2_bridge")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866025, -0.353553, 0.353553, 0, 0.707107, 0.707107, -0.5, -0.612372, 0.612372, 0, 8, 0)
shadow_enabled = true

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.965926, 0.258819, 0, -0.258819, 0.965926, 0, 3, 7)
current = true

[node name="Monad1_ConsensusCore" type="MeshInstance3D" parent="."]
transform = Transform3D(1.2, 0, 0, 0, 4, 0, 0, 0, 1.2, -2.5, 2, 0)
material_override = SubResource("ShaderMaterial_m1")
metadata/monad_id = 1
metadata/opacity = 0.95

[node name="Monad2_ZoneOfOmission" type="MeshInstance3D" parent="."]
transform = Transform3D(1.5, 0, 0, 0, 1.5, 0, 0, 0, 1.5, 0, 1.5, 0)
material_override = SubResource("ShaderMaterial_m2")
metadata/monad_id = 2
metadata/opacity = 0.20

[node name="StaticBody3D" type="StaticBody3D" parent="Monad2_ZoneOfOmission"]
metadata/monad_id = 2
metadata/opacity = 0.20

[node name="CollisionShape3D" type="CollisionShape3D" parent="Monad2_ZoneOfOmission/StaticBody3D"]
shape = SubResource("SphereShape3D_omission")

[node name="Monad11_KintsugiScarNode" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 2.5, 2, 0)
material_override = SubResource("ShaderMaterial_m11")
metadata/monad_id = 11
metadata/opacity = 0.98
metadata/scar_cost = 0.30
"""

with open("scenes/ResidualMeaningShowcase.tscn", "w", encoding="utf-8") as f:
    f.write(tscn_content)

print("[2/3] Applied shaders/cathedral_chroma_omega.gdshader to MeshInstance3D nodes.")
print("[3/3] Bound metadata (opacity, monad_id) on interactive omission and scar nodes.")
print("Integration complete: Scene ready at res://scenes/ResidualMeaningShowcase.tscn")
