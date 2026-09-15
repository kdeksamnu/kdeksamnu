using Godot;
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
