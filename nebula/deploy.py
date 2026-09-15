import os

os.makedirs("shaders", exist_ok=True)
os.makedirs("scripts", exist_ok=True)
os.makedirs("scenes", exist_ok=True)

# 1. Shader
with open("shaders/cathedral_chroma_omega.gdshader", "w", encoding="utf-8") as f:
    f.write("""shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

const vec3 COLOR_THETA_GOLD    = vec3(0.85, 0.68, 0.22);
const vec3 COLOR_DELTA_BLUE    = vec3(0.08, 0.18, 0.36);
const vec3 COLOR_PSI_TEAL      = vec3(0.12, 0.52, 0.54);
const vec3 COLOR_NULL_OBSIDIAN = vec3(0.04, 0.04, 0.06);
const vec3 COLOR_KINTSUGI_HOT  = vec3(1.00, 0.82, 0.30);
const vec3 COLOR_LANDAUER_IR   = vec3(1.00, 0.35, 0.05);

uniform int u_monad_id : hint_range(1, 12) = 1;
uniform float u_opacity : hint_range(0.0, 1.0) = 0.85;
uniform float u_audit_intensity : hint_range(0.0, 5.0) = 0.0;
uniform float u_scar_cost : hint_range(0.0, 0.30) = 0.14;

varying vec3 v_world_pos;
varying vec3 v_normal;

void vertex() {
    v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    v_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
    vec3 view_dir = normalize(CAMERA_POSITION_WORLD - v_world_pos);
    float n_dot_v = max(dot(v_normal, view_dir), 0.0);

    vec3 base_albedo = COLOR_NULL_OBSIDIAN;
    vec3 emission_color = vec3(0.0);
    float roughness = 0.45;
    float metallic = 0.10;

    if (u_monad_id == 1) {
        base_albedo = mix(COLOR_NULL_OBSIDIAN, COLOR_THETA_GOLD, n_dot_v * 0.8 + 0.2);
        metallic = 0.85;
        roughness = 0.20;
    } else if (u_monad_id == 2) {
        base_albedo = COLOR_NULL_OBSIDIAN;
        roughness = 0.90;
    } else if (u_monad_id == 8 || u_monad_id == 9) {
        base_albedo = mix(COLOR_DELTA_BLUE, vec3(0.35, 0.15, 0.55), sin(v_world_pos.y * 2.0) * 0.5 + 0.5);
        roughness = 0.30;
    } else if (u_monad_id == 11) {
        vec2 local_coord = UV - vec2(0.5);
        float theta = atan(local_coord.y, local_coord.x);
        float r = length(local_coord);
        float branch_cut = sqrt(max(r, 0.001)) * cos(theta * 0.5);
        base_albedo = mix(COLOR_NULL_OBSIDIAN, COLOR_KINTSUGI_HOT, step(0.0, branch_cut));
        emission_color = COLOR_KINTSUGI_HOT * abs(branch_cut) * (u_scar_cost / 0.30) * 3.0;
        metallic = 0.95;
        roughness = 0.15;
    } else {
        base_albedo = vec3(0.15, 0.18, 0.22);
        roughness = 0.60;
    }

    if (u_opacity < 0.40 && u_audit_intensity > 0.01) {
        float pulse = sin(TIME * 6.28318 * 1.5) * 0.5 + 0.5;
        emission_color += COLOR_LANDAUER_IR * u_audit_intensity * (1.0 - u_opacity) * (pulse * 0.7 + 0.3);
    }

    ALBEDO = base_albedo;
    METALLIC = metallic;
    ROUGHNESS = roughness;
    EMISSION = emission_color;
    ALPHA = clamp(u_opacity + (u_audit_intensity * 0.15), 0.05, 1.0);
}
""")

# 2. Bridge C# Controller
with open("scripts/CathedralTransductionBridge.cs", "w", encoding="utf-8") as f:
    f.write("""using Godot;
using System;
using System.Text;
using System.Security.Cryptography;

public partial class CathedralTransductionBridge : Node3D
{
    [Export] public float QueryFrequencyHz = 1.5f;
    [Export] public float JoulesPerGasCredit = 1.0e-21f;

    private Camera3D _camera;
    private Vector3 _lastCameraPos;
    private float _timeAccumulator = 0.0f;
    private double _currentGasPool = 125.0;
    private string _currentMerkleRoot = "0x7F4C8E2B19A03D51";

    public override void _Ready()
    {
        _camera = GetViewport().GetCamera3D();
        if (_camera != null)
            _lastCameraPos = _camera.GlobalPosition;
        GD.Print("[CathedralBridge] Initialized. Root: ", _currentMerkleRoot);
    }

    public override void _Process(double delta)
    {
        _timeAccumulator += (float)delta;
        float interval = 1.0f / QueryFrequencyHz;
        if (_timeAccumulator >= interval)
        {
            _timeAccumulator -= interval;
            ExecuteCadenceTick((float)delta);
        }
    }

    private void ExecuteCadenceTick(float delta)
    {
        if (_camera == null) return;
        Vector3 currentPos = _camera.GlobalPosition;
        Vector3 velocity = (currentPos - _lastCameraPos) / Mathf.Max(delta, 1e-4f);
        _lastCameraPos = currentPos;

        var spaceState = GetWorld3D().DirectSpaceState;
        var query = PhysicsRayQueryParameters3D.Create(currentPos, currentPos - _camera.GlobalTransform.Basis.Z * 25.0f);
        var hit = spaceState.IntersectRay(query);

        if (hit.Count > 0 && hit["collider"].Obj is Node collider && collider.HasMeta("opacity"))
        {
            float opacity = (float)collider.GetMeta("opacity");
            if (opacity < 0.40f)
            {
                double tHorizon = 293.15 / (opacity + 0.001);
                double work = 1.380649e-23 * tHorizon * 0.693147 * QueryFrequencyHz * (velocity.Length() * 0.1 + 0.05);
                int minted = Math.Max(1, (int)(work / JoulesPerGasCredit));
                _currentGasPool += minted;

                if (collider is MeshInstance3D mesh && mesh.MaterialOverride is ShaderMaterial mat)
                    mat.SetShaderParameter("u_audit_intensity", Mathf.Clamp(velocity.Length() * 0.2f, 0.5f, 3.0f));

                GD.Print($"[PoE Harvest] Minted: {minted} Credits | Pool: {_currentGasPool}");
                if (_currentGasPool >= 60.0) CommitBlock(30);
            }
        }
    }

    private void CommitBlock(int count)
    {
        _currentGasPool -= count * 2;
        using SHA256 sha = SHA256.Create();
        byte[] bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(_currentMerkleRoot + DateTime.UtcNow.Ticks));
        _currentMerkleRoot = "0x" + BitConverter.ToString(bytes).Replace("-", "").Substring(0, 16);
        GD.Print($"[Ash Archive Commit] Block: {_currentMerkleRoot} | Balance: {_currentGasPool}");
    }
}
""")

# 3. ECT Inhabitant Pipeline
with open("scripts/CathedralECTPipeline.cs", "w", encoding="utf-8") as f:
    f.write("""using Godot;
using System;
using System.Collections.Generic;

public enum BelnapValue { True, False, Both, Neither }

public struct CathedralEntity
{
    public Vector3 Position;
    public Vector3 Velocity;
    public float EpistemicDebt;
    public float LandauerBurnRate;
    public int ActiveMonadAffinity;
    public BelnapValue ExistsInManifest;
}

public partial class CathedralECTPipeline : Node3D
{
    [Export] public int InitialEntityCount = 120;
    [Export] public float TorsionVorticityGamma = 1.25e-35f;

    private List<CathedralEntity> _entities = new List<CathedralEntity>();
    private MultiMeshInstance3D _multiMeshInstance;
    private MultiMesh _multiMesh;
    private Random _rng = new Random(108);

    public override void _Ready()
    {
        _multiMeshInstance = new MultiMeshInstance3D();
        _multiMesh = new MultiMesh
        {
            TransformFormat = MultiMesh.TransformFormatEnum.Transform3D,
            UseColors = true,
            InstanceCount = InitialEntityCount,
            Mesh = new BoxMesh { Size = new Vector3(0.18f, 0.18f, 0.18f) }
        };
        _multiMeshInstance.Multimesh = _multiMesh;
        AddChild(_multiMeshInstance);

        for (int i = 0; i < InitialEntityCount; i++)
        {
            Vector3 pos = new Vector3(
                (float)(_rng.NextDouble() * 12.0 - 6.0),
                (float)(_rng.NextDouble() * 6.0 - 2.0),
                (float)(_rng.NextDouble() * 12.0 - 6.0)
            );
            BelnapValue val = (i % 5 == 0) ? BelnapValue.Both : ((i % 8 == 0) ? BelnapValue.False : BelnapValue.True);
            _entities.Add(new CathedralEntity
            {
                Position = pos,
                Velocity = new Vector3((float)(_rng.NextDouble() * 0.4 - 0.2), 0, (float)(_rng.NextDouble() * 0.4 - 0.2)),
                EpistemicDebt = (float)(_rng.NextDouble() * 0.5),
                LandauerBurnRate = 2.8e-21f * (float)(1.0 + _rng.NextDouble() * 3.0),
                ActiveMonadAffinity = _rng.Next(1, 13),
                ExistsInManifest = val
            });
        }
        GD.Print($"[ECT Pipeline] Initialized {_entities.Count} entities.");
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;
        for (int i = 0; i < _entities.Count; i++)
        {
            CathedralEntity e = _entities[i];
            e.Position += e.Velocity * dt;
            if (Math.Abs(e.Position.X) > 8.0f) e.Velocity.X *= -1.0f;
            if (Math.Abs(e.Position.Z) > 8.0f) e.Velocity.Z *= -1.0f;
            _entities[i] = e;

            _multiMesh.SetInstanceTransform(i, new Transform3D(Basis.Identity, e.Position));
            Color c = e.ExistsInManifest switch
            {
                BelnapValue.True => new Color(0.85f, 0.68f, 0.22f),
                BelnapValue.False => new Color(0.12f, 0.15f, 0.20f),
                BelnapValue.Both => new Color(0.98f, 0.85f, 0.35f),
                _ => new Color(0.78f, 0.12f, 0.22f)
            };
            _multiMesh.SetInstanceColor(i, c);
        }
    }
}
""")

# 4. Project Configuration & Showcase Scene
proj_file = "project.godot"
line = 'CathedralTransductionBridge="*res://scripts/CathedralTransductionBridge.cs"\n'
if os.path.exists(proj_file):
    with open(proj_file, "r") as f:
        c = f.read()
else:
    c = "[application]\nconfig/name=\"Cathedral\"\n"

if "[autoload]" in c:
    if "CathedralTransductionBridge" not in c:
        c = c.replace("[autoload]", "[autoload]\n" + line)
else:
    c += "\n[autoload]\n\n" + line

with open(proj_file, "w") as f:
    f.write(c)

with open("scenes/ResidualMeaningShowcase.tscn", "w", encoding="utf-8") as f:
    f.write("""[gd_scene load_steps=7 format=3 uid="uid://c3m7r2q4k1b8p"]

[ext_resource type="Shader" path="res://shaders/cathedral_chroma_omega.gdshader" id="1_shader"]
[ext_resource type="Script" path="res://scripts/CathedralTransductionBridge.cs" id="2_bridge"]
[ext_resource type="Script" path="res://scripts/CathedralECTPipeline.cs" id="3_ect"]

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

[sub_resource type="SphereShape3D" id="SphereShape3D_omission"]
radius = 1.0

[node name="ResidualMeaningShowcase" type="Node3D"]
script = ExtResource("2_bridge")

[node name="ECT_Population" type="Node3D" parent="."]
script = ExtResource("3_ect")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.965926, 0.258819, 0, -0.258819, 0.965926, 0, 3, 7)
current = true

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866025, -0.353553, 0.353553, 0, 0.707107, 0.707107, -0.5, -0.612372, 0.612372, 0, 8, 0)
shadow_enabled = true

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
""")

print("All components written successfully: Shaders, Scripts, Scenes, and Autoloads.")
