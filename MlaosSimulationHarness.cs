using System;
using System.Collections.Generic;
using Godot;
using CathedralEngine.Core.Topological;
using CathedralEngine.Core.Paraconsistent;

namespace CathedralEngine.Core.Orchestration
{
    /// <summary>
    /// Master Godot 4 Orchestration scene binding Graph Laplacian, 
    /// Lindblad Dissipator, GPU Compute Shader, and Murmuration Multi-Agent System.
    /// </summary>
    public partial class MlaosSimulationHarness : Node3D
    {
        [Export] public int AgentCount { get; set; } = 48;
        [Export] public float SpatialBounds { get; set; } = 32.0f;

        private DiscreteLaplacianSolver _laplacian;
        private GkslMasterDissipator _dissipator;
        private RenderingDevice _rd;
        private Rid _shaderRid;
        private Rid _pipelineRid;

        private readonly List<Node3D> _agentInstances = new();
        private readonly List<Vector3> _agentVelocities = new();
        private readonly List<BelnapValue> _agentStates = new();

        public override void _Ready()
        {
            _laplacian = new DiscreteLaplacianSolver();
            _dissipator = new GkslMasterDissipator();
            AddChild(_laplacian);
            AddChild(_dissipator);

            _laplacian.OnFiedlerCriticalWarning += HandleFiedlerDrop;
            _laplacian.OnXHebbianEdgeSpawned += HandleEdgeSpawned;
            _dissipator.OnHarmonicScarCommitted += HandleScarCommitted;

            _laplacian.InitializeGraph(AgentCount);

            InitializeAgents();
            InitializeComputeShader();
        }

        private void InitializeAgents()
        {
            var rng = new RandomNumberGenerator();
            rng.Seed = 119;

            for (int i = 0; i < AgentCount; i++)
            {
                var meshInstance = new MeshInstance3D
                {
                    Mesh = new BoxMesh { Size = new Vector3(0.6f, 0.6f, 0.6f) },
                    Position = new Vector3(
                        rng.RandfRange(-SpatialBounds * 0.5f, SpatialBounds * 0.5f),
                        rng.RandfRange(0.0f, 4.0f),
                        rng.RandfRange(-SpatialBounds * 0.5f, SpatialBounds * 0.5f)
                    )
                };

                AddChild(meshInstance);
                _agentInstances.Add(meshInstance);
                _agentVelocities.Add(new Vector3(rng.RandfRange(-1, 1), 0, rng.RandfRange(-1, 1)).Normalized());
                _agentStates.Add((i % 7 == 0) ? BelnapValue.Both : BelnapValue.True);

                _laplacian.SetNodePosition(i, new Vector2(meshInstance.Position.X, meshInstance.Position.Z));
            }
        }

        private void InitializeComputeShader()
        {
            _rd = RenderingServer.CreateLocalRenderingDevice();
            if (_rd == null) return;

            var shaderFile = GD.Load<RDShaderFile>("res://Shaders/DialetheicBuffer.glsl");
            if (shaderFile != null)
            {
                var shaderSpirv = shaderFile.GetSpirV();
                _shaderRid = _rd.ShaderCreateFromSpirV(shaderSpirv);
                _pipelineRid = _rd.ComputePipelineCreate(_shaderRid);
            }
        }

        public override void _PhysicsProcess(double delta)
        {
            // 1. Evaluate k = 7 Topological Murmuration
            for (int i = 0; i < AgentCount; i++)
            {
                Vector3 currentPos = _agentInstances[i].Position;
                var neighbors = GetTopologicalNeighbors(i, 7);

                Vector3 alignment = Vector3.Zero;
                Vector3 cohesion = Vector3.Zero;
                Vector3 separation = Vector3.Zero;

                foreach (int nIdx in neighbors)
                {
                    alignment += _agentVelocities[nIdx];
                    cohesion += _agentInstances[nIdx].Position;

                    Vector3 diff = currentPos - _agentInstances[nIdx].Position;
                    float dist = diff.Length();
                    if (dist > 0.001f)
                    {
                        separation += diff.Normalized() / dist;
                    }

                    // Update graph adjacency weight based on metric proximity
                    float weight = Mathf.Clamp(1.0f / Mathf.Max(dist, 0.1f), 0.0f, 5.0f);
                    _laplacian.AddOrUpdateEdge(i, nIdx, weight);
                }

                if (neighbors.Count > 0)
                {
                    alignment = (alignment / neighbors.Count).Normalized();
                    cohesion = ((cohesion / neighbors.Count) - currentPos).Normalized();
                }

                Vector3 steering = alignment * 0.4f + cohesion * 0.3f + separation * 0.6f;
                _agentVelocities[i] = (_agentVelocities[i] + steering * (float)delta).Normalized();

                // 2. Lindblad Dissipation Pass on Amplitude
                float currentSpeed = _agentVelocities[i].Length();
                float dissipatedSpeed = _dissipator.StepDissipation(currentSpeed, _agentStates[i], delta);
                _agentInstances[i].Position += _agentVelocities[i] * dissipatedSpeed * 4.0f * (float)delta;

                _laplacian.SetNodePosition(i, new Vector2(_agentInstances[i].Position.X, _agentInstances[i].Position.Z));
            }

            // 3. Compute Algebraic Connectivity
            _laplacian.ComputeFiedlerValue();
        }

        private List<int> GetTopologicalNeighbors(int agentIndex, int k)
        {
            var distances = new List<(int index, float dist)>();
            Vector3 myPos = _agentInstances[agentIndex].Position;

            for (int i = 0; i < AgentCount; i++)
            {
                if (i == agentIndex) continue;
                distances.Add((i, myPos.DistanceSquaredTo(_agentInstances[i].Position)));
            }

            distances.Sort((a, b) => a.dist.CompareTo(b.dist));
            var result = new List<int>();
            int limit = Mathf.Min(k, distances.Count);
            for (int i = 0; i < limit; i++) result.Add(distances[i].index);

            return result;
        }

        private void HandleFiedlerDrop(float fiedler)
        {
            GD.PrintErr($"[M1 ARCHITECTURE WARNING] Fiedler floor breached: mu_2 = {fiedler:F4} < 0.05. Injecting xHebbian bridge.");
        }

        private void HandleEdgeSpawned(int u, int v, float w)
        {
            GD.Print($"[M1 X-HEBBIAN] Restorative hyper-edge synthesized: ({u} <---> {v}) with weight {w:F2}");
        }

        private void HandleScarCommitted(string merkleRoot, float amp, BelnapValue val)
        {
            GD.Print($"[M3 ASH ARCHIVE] Lex I Scar Inscribed. Root: {merkleRoot.Substring(0, 12)}... Amp: {amp:F3} Truth: {val}");
        }

        public override void _ExitTree()
        {
            if (_rd != null)
            {
                if (_pipelineRid.IsValid) _rd.FreeRid(_pipelineRid);
                if (_shaderRid.IsValid) _rd.FreeRid(_shaderRid);
                _rd.Dispose();
            }
        }
    }
}
