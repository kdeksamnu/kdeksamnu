using System;
using System.Collections.Generic;
using Godot;
using CathedralEngine.Core.Topological;
using CathedralEngine.Core.Paraconsistent;

namespace CathedralEngine.Sdk
{
    /// <summary>
    /// High-level entry point for independent developers integrating
    /// non-Euclidean topologies and paraconsistent logic.
    /// Automatically manages the Fiedler floor and Merkle DAG persistence.
    /// </summary>
    public class CathedralSubstrate
    {
        private readonly DiscreteLaplacianSolver _solver;
        private readonly GkslMasterDissipator _dissipator;
        private readonly Dictionary<int, DialetheicCell> _cells = new();
        private int _nextId = 0;

        public float AlgebraicConnectivity => _solver.LastComputedFiedler;
        public bool IsTopologyHealthy => _solver.IsTopologicallyConnected;
        public string LatestMerkleRoot => _dissipator.CurrentMerkleRoot;

        public event Action<int, int> OnTopologyAutoBridged;
        public event Action<int, string> OnContradictionPermineralized;

        public CathedralSubstrate(float targetConnectivity = 0.15f, float floorThreshold = 0.05f)
        {
            _solver = new DiscreteLaplacianSolver
            {
                NominalFiedlerTarget = targetConnectivity,
                FiedlerFloor = floorThreshold
            };
            _dissipator = new GkslMasterDissipator();

            _solver.OnXHebbianEdgeSpawned += (u, v, weight) =>
            {
                OnTopologyAutoBridged?.Invoke(u, v);
            };
        }

        public int AddNode(Vector2 position, BelnapTruthValue initialTruth = BelnapTruthValue.T)
        {
            int id = _nextId++;
            _solver.InitializeGraph(_nextId);
            _solver.SetNodePosition(id, position);

            _cells[id] = new DialetheicCell
            {
                Truth = initialTruth,
                StressTensorPrincipal = Vector2.One,
                ShearStress = 0.0f,
                OrientationAngle = 0.0f,
                IsPermineralized = false
            };

            return id;
        }

        public void ConnectNodes(int nodeIdA, int nodeIdB, float weight = 1.0f)
        {
            _solver.AddOrUpdateEdge(nodeIdA, nodeIdB, weight);
        }

        public void FlagContradiction(int nodeId, float initialShearStress = 0.45f)
        {
            if (!_cells.ContainsKey(nodeId)) return;

            var cell = _cells[nodeId];
            cell.Truth = BelnapTruthValue.B;
            cell.ShearStress = initialShearStress;
            _cells[nodeId] = cell;
        }

        public void Update(float delta)
        {
            // 1. Evaluate graph connectivity; automatically injects xHebbian bridges if mu2 < 0.05
            _solver.ComputeFiedlerValue(maxIterations: 25);

            // 2. Process and relax contradictions
            foreach (var kvp in _cells)
            {
                int id = kvp.Key;
                var cell = kvp.Value;

                if (cell.Truth == BelnapTruthValue.B && !cell.IsPermineralized)
                {
                    var relaxedCell = _dissipator.ExecuteMetamorphicSqueeze(cell, id);
                    _cells[id] = relaxedCell;
                    OnContradictionPermineralized?.Invoke(id, _dissipator.CurrentMerkleRoot);
                }
            }
        }
    }
}
