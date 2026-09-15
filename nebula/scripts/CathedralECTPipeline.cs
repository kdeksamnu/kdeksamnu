using Godot;
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
