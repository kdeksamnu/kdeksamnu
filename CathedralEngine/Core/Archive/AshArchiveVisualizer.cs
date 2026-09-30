using Godot;
using System;
using System.Collections.Generic;
using CathedralEngine.Core.Paraconsistent;

namespace CathedralEngine.Core.Archive
{
    public partial class AshArchiveVisualizer : Node3D
    {
        private readonly Dictionary<string, Vector3> _nodePositions = new();
        private StandardMaterial3D _scarMat, _ghostMat, _knotMat;
        private int _layer = 0;

        public override void _Ready()
        {
            _scarMat = new StandardMaterial3D { AlbedoColor = Colors.DarkSlateGray, EmissionEnabled = true, Emission = Colors.Gold, EmissionEnergyMultiplier = 1.5f };
            _ghostMat = new StandardMaterial3D { AlbedoColor = new Color(0.5f, 0.5f, 0.6f, 0.3f), Transparency = BaseMaterial3D.TransparencyEnum.Alpha, EmissionEnabled = true, Emission = Colors.Gray };
            _knotMat = new StandardMaterial3D { AlbedoColor = Colors.Gold, EmissionEnabled = true, Emission = Colors.Gold, EmissionEnergyMultiplier = 3.0f, ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded };
            GD.Print("[M4 ARCHIVE] 3D Visualizer Ready.");
        }

        public void CommitNode(string id, BelnapTruthValue state, bool isKnot = false)
        {
            float x = (id.GetHashCode() % 5) * 1.5f;
            float y = _layer * 2.0f;
            float z = (id.GetHashCode() / 5 % 5) * 1.5f;
            Vector3 pos = new Vector3(x, y, z);
            _nodePositions[id] = pos;
            _layer++;

            Node3D node = state == BelnapTruthValue.N 
                ? new MeshInstance3D { Mesh = new SphereMesh { Radius = 0.3f, Height = 0.6f }, Position = pos, MaterialOverride = _ghostMat }
                : (isKnot ? CreateKnot(pos) : new MeshInstance3D { Mesh = new BoxMesh { Size = new Vector3(0.5f, 0.5f, 0.5f) }, Position = pos, MaterialOverride = _scarMat });
            
            AddChild(node);
        }

        private Node3D CreateKnot(Vector3 pos)
        {
            var container = new Node3D { Position = pos };
            var helix = new ImmediateMesh();
            helix.SurfaceBegin(Mesh.PrimitiveType.LineStrip);
            for (int i = 0; i <= 32; i++) {
                float t = i / 32.0f;
                float angle = t * Mathf.Pi * 4;
                helix.SurfaceAddVertex(new Vector3(Mathf.Cos(angle) * 0.3f, (t - 0.5f), Mathf.Sin(angle) * 0.3f));
            }
            helix.SurfaceEnd();
            container.AddChild(new MeshInstance3D { Mesh = helix, MaterialOverride = _knotMat });
            return container;
        }
    }
}
