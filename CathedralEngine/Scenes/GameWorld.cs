using Godot;
using System.Collections.Generic;
using CathedralEngine.Sdk;
using CathedralEngine.Extensions;

namespace CathedralEngine.Scenes
{
    public partial class GameWorld : Node2D
    {
        private CathedralSubstrate _substrate;
        private readonly Dictionary<int, Vector2> _nodeCoords = new();
        private readonly List<(int u, int v)> _edges = new();
        private double _telemetryTimer = 0.0;
        private const double TelemetryInterval = 0.6667; // 1.50 Hz somatic tempo

        public override void _Ready()
        {
            _substrate = new CathedralSubstrate(targetConnectivity: 0.15f, floorThreshold: 0.05f);

            _substrate.OnTopologyAutoBridged += (u, v) =>
            {
                GD.Print($"[HEBBIAN BRIDGE] Substrate auto-bridged seam: Node {u} <-> Node {v}");
                _edges.Add((u, v));
            };

            _substrate.OnContradictionPermineralized += (nodeId, merkleHash) =>
            {
                GD.Print($"[ASH ARCHIVE] Node {nodeId} stabilized. Root: {merkleHash[..8]}...");
            };

            SetupWorldNodes();
        }

        private void SetupWorldNodes()
        {
            int node0 = _substrate.AddNode(new Vector2(100, 100));
            int node1 = _substrate.AddNode(new Vector2(250, 120));
            int node2 = _substrate.AddNode(new Vector2(400, 200));
            int node3 = _substrate.AddNode(new Vector2(150, 300));

            _nodeCoords[node0] = new Vector2(100, 100);
            _nodeCoords[node1] = new Vector2(250, 120);
            _nodeCoords[node2] = new Vector2(400, 200);
            _nodeCoords[node3] = new Vector2(150, 300);

            Connect(node0, node1, 1.2f);
            Connect(node1, node2, 0.8f);
            Connect(node2, node3, 1.5f);
            Connect(node3, node0, 1.0f);
        }

        private void Connect(int u, int v, float weight)
        {
            _substrate.ConnectNodes(u, v, weight);
            _edges.Add((u, v));
        }

        public override void _Process(double delta)
        {
            _substrate.Update((float)delta);

            _telemetryTimer += delta;
            if (_telemetryTimer >= TelemetryInterval)
            {
                _telemetryTimer = 0.0;
                _substrate.LogSubstrateStatus();

                if (_substrate.IsNearBoundaryCollapse())
                {
                    GD.PrintRich("[color=yellow][ALERT] Topology near critical Fiedler boundary![/color]");
                }
            }

            QueueRedraw();
        }

        public override void _Draw()
        {
            foreach (var (u, v) in _edges)
            {
                if (_nodeCoords.TryGetValue(u, out Vector2 posU) && _nodeCoords.TryGetValue(v, out Vector2 posV))
                {
                    DrawLine(posU, posV, new Color(0.2f, 0.6f, 0.8f, 0.6f), 2.0f);
                }
            }

            foreach (var kvp in _nodeCoords)
            {
                DrawCircle(kvp.Value, 7.0f, Colors.Gold);
                DrawString(ThemeDB.FallbackFont, kvp.Value + new Vector2(10, 5), $"Node {kvp.Key}", HorizontalAlignment.Left, -1, 12, Colors.White);
            }

            string telemetry = $"μ2: {_substrate.AlgebraicConnectivity:F4} | Healthy: {_substrate.IsTopologyHealthy} | Root: {_substrate.LatestMerkleRoot[..8]}...";
            Color statusColor = _substrate.IsTopologyHealthy ? Colors.DarkTurquoise : Colors.Crimson;
            DrawString(ThemeDB.FallbackFont, new Vector2(20, 30), telemetry, HorizontalAlignment.Left, -1, 14, statusColor);
        }

        public override void _UnhandledInput(InputEvent @event)
        {
            if (@event.IsActionPressed("ui_accept"))
            {
                _substrate.TriggerEscalatedParadox(targetNodeId: 2, shearStress: 0.75f);
            }
            else if (@event.IsActionPressed("ui_select"))
            {
                _substrate.TriggerSwarmshear(new[] { 0, 1, 2 }, baseShear: 0.40f);
            }
        }
    }
}
