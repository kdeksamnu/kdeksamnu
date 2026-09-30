using System;
using System.Collections.Generic;
using Godot;

namespace CathedralEngine.Core.Topological
{
    /// <summary>
    /// Governs pre-geometric discretization and algebraic connectivity (M1: Cathedral of the Scar).
    /// Enforces the Fiedler eigenvalue floor (mu_2 >= 0.05) to prevent graph fragmentation.
    /// </summary>
    [GlobalClass]
    public partial class DiscreteLaplacianSolver : Node
    {
        [Export] public float FiedlerFloor { get; set; } = 0.05f;
        [Export] public float NominalFiedlerTarget { get; set; } = 0.15f;
        [Export] public double PlanckCutoffScale { get; set; } = 1.0e-4; // Normalized simulation ell_P

        private int _nodeCount;
        private readonly List<Vector2> _nodePositions = new();
        private readonly Dictionary<int, Dictionary<int, float>> _adjacency = new();

        public float LastComputedFiedler { get; private set; } = 0.0f;
        public bool IsTopologicallyConnected => LastComputedFiedler >= FiedlerFloor;

        public event Action<float> OnFiedlerCriticalWarning;
        public event Action<int, int, float> OnXHebbianEdgeSpawned;

        public void InitializeGraph(int initialNodeCount)
        {
            _nodeCount = initialNodeCount;
            _nodePositions.Clear();
            _adjacency.Clear();

            for (int i = 0; i < _nodeCount; i++)
            {
                _nodePositions.Add(Vector2.Zero);
                _adjacency[i] = new Dictionary<int, float>();
            }
        }

        public void SetNodePosition(int nodeIndex, Vector2 position)
        {
            if (nodeIndex >= 0 && nodeIndex < _nodePositions.Count)
            {
                _nodePositions[nodeIndex] = position;
            }
            else if (nodeIndex == _nodePositions.Count)
            {
                _nodePositions.Add(position);
            }
        }

        public void AddOrUpdateEdge(int u, int v, float weight)
        {
            if (u == v || u >= _nodeCount || v >= _nodeCount) return;

            // Enforce lower bound on vertex spacing cutoff (a >= ell_P)
            if (u < _nodePositions.Count && v < _nodePositions.Count)
            {
                float distance = _nodePositions[u].DistanceTo(_nodePositions[v]);
                if (distance < PlanckCutoffScale)
                {
                    weight = Mathf.Min(weight, 1.0f); // Saturate UV divergence
                }
            }

            _adjacency[u][v] = weight;
            _adjacency[v][u] = weight;
        }

        public void RemoveEdge(int u, int v)
        {
            if (_adjacency.ContainsKey(u)) _adjacency[u].Remove(v);
            if (_adjacency.ContainsKey(v)) _adjacency[v].Remove(u);
        }

        /// <summary>
        /// Computes algebraic connectivity mu_2 = lambda_2(L) using shift-and-invert Rayleigh-Ritz iteration.
        /// </summary>
        public float ComputeFiedlerValue(int maxIterations = 50, float tolerance = 1e-4f)
        {
            if (_nodeCount < 2) return 0.0f;

            // Construct degree vector D_ii
            float[] degrees = new float[_nodeCount];
            for (int i = 0; i < _nodeCount; i++)
            {
                float sum = 0.0f;
                foreach (var kvp in _adjacency[i])
                    sum += kvp.Value;
                degrees[i] = sum;
            }

            // Initialize random test vector orthogonal to trivial eigenvector v_1 = [1, 1, ..., 1]^T
            float[] v = new float[_nodeCount];
            var rng = new Random(119); // 119 Consecrated Seed
            float mean = 0.0f;

            for (int i = 0; i < _nodeCount; i++)
            {
                v[i] = (float)rng.NextDouble() - 0.5f;
                mean += v[i];
            }
            mean /= _nodeCount;

            float norm = 0.0f;
            for (int i = 0; i < _nodeCount; i++)
            {
                v[i] -= mean;
                norm += v[i] * v[i];
            }
            norm = Mathf.Sqrt(norm);
            if (norm > 0)
            {
                for (int i = 0; i < _nodeCount; i++) v[i] /= norm;
            }

            // Power iteration for smallest non-zero eigenvalue on (shift * I - L)
            float maxDegree = 0.0f;
            for (int i = 0; i < _nodeCount; i++)
                if (degrees[i] > maxDegree) maxDegree = degrees[i];

            float shift = 2.0f * maxDegree;
            float[] w = new float[_nodeCount];

            for (int iter = 0; iter < maxIterations; iter++)
            {
                for (int i = 0; i < _nodeCount; i++)
                {
                    float av = 0.0f;
                    foreach (var edge in _adjacency[i])
                    {
                        av += edge.Value * v[edge.Key];
                    }
                    w[i] = (shift - degrees[i]) * v[i] + av;
                }

                // Project out constant vector [1, 1, ..., 1]^T
                float proj = 0.0f;
                for (int i = 0; i < _nodeCount; i++) proj += w[i];
                proj /= _nodeCount;
                for (int i = 0; i < _nodeCount; i++) w[i] -= proj;

                // Normalize
                norm = 0.0f;
                for (int i = 0; i < _nodeCount; i++) norm += w[i] * w[i];
                norm = Mathf.Sqrt(norm);
                if (norm < 1e-9f) break;

                for (int i = 0; i < _nodeCount; i++) v[i] = w[i] / norm;
            }

            // Rayleigh quotient: mu_2 = v^T L v / (v^T v)
            float rayleighNumerator = 0.0f;
            for (int i = 0; i < _nodeCount; i++)
            {
                foreach (var edge in _adjacency[i])
                {
                    int j = edge.Key;
                    if (i < j)
                    {
                        float diff = v[i] - v[j];
                        rayleighNumerator += edge.Value * diff * diff;
                    }
                }
            }

            LastComputedFiedler = rayleighNumerator;

            if (LastComputedFiedler < FiedlerFloor)
            {
                OnFiedlerCriticalWarning?.Invoke(LastComputedFiedler);
                InjectXHebbianReinforcement(v);
            }

            return LastComputedFiedler;
        }

        private void InjectXHebbianReinforcement(float[] fiedlerVector)
        {
            int minPositiveNode = -1;
            int maxNegativeNode = -1;
            float minPosVal = float.MaxValue;
            float maxNegVal = float.MinValue;

            for (int i = 0; i < _nodeCount; i++)
            {
                if (fiedlerVector[i] >= 0 && fiedlerVector[i] < minPosVal)
                {
                    minPosVal = fiedlerVector[i];
                    minPositiveNode = i;
                }
                else if (fiedlerVector[i] < 0 && fiedlerVector[i] > maxNegVal)
                {
                    maxNegVal = fiedlerVector[i];
                    maxNegativeNode = i;
                }
            }

            if (minPositiveNode != -1 && maxNegativeNode != -1)
            {
                float restorativeWeight = NominalFiedlerTarget * 1.5f;
                AddOrUpdateEdge(minPositiveNode, maxNegativeNode, restorativeWeight);
                OnXHebbianEdgeSpawned?.Invoke(minPositiveNode, maxNegativeNode, restorativeWeight);
            }
        }
    }
}
