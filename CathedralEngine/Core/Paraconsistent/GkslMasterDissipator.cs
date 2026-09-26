using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using Godot;

namespace CathedralEngine.Core.Paraconsistent
{
    public enum BelnapTruthValue { N = 0, F = 1, T = 2, B = 3 }

    public struct DialetheicCell
    {
        public BelnapTruthValue Truth;
        public Vector2 StressTensorPrincipal; // (sigma_x, sigma_y)
        public float ShearStress;             // tau_xy
        public float OrientationAngle;        // Radians
        public bool IsPermineralized;
    }

    /// <summary>
    /// Resolves logical collisions and non-Hermitian stress via GKSL jump dissipation
    /// and Magic-Angle shear cancellation (M3: Dialetheic Buffer & M4: Null-Basin).
    /// </summary>
    [GlobalClass]
    public partial class GkslMasterDissipator : Node
    {
        public static readonly float MagicAngle = Mathf.Acos(1.0f / Mathf.Sqrt(3.0f)); // ~54.7356 deg

        [ExportGroup("Dissipator Parameters")]
        [Export] public float PyragasGainK { get; set; } = 0.384f;
        [Export] public float CriticalGainK { get; set; } = 0.750f;
        [Export] public float EpistemicRemainderDelta { get; set; } = 0.001f;
        [Export] public NodePath ShaderBridgePath { get; set; } = "DialetheicShaderBridge";

        [Signal]
        public delegate void ScarPermineralizedEventHandler(int cellIndex, float meanStress, string merkleRoot);

        private readonly Queue<Vector2> _stateHistory = new();
        private const int HistoryDelayTicks = 11;
        private DialetheicShaderBridge _bridge;

        public string CurrentMerkleRoot { get; private set; } = "0000000000000000000000000000000000000000000000000000000000000000";

        public override void _Ready()
        {
            // Connect to DialetheicShaderBridge if present in the scene hierarchy
            _bridge = GetNodeOrNull<DialetheicShaderBridge>(ShaderBridgePath);
            if (_bridge != null)
            {
                _bridge.MetamorphicSqueezeTriggered += OnMetamorphicSqueezeTriggered;
                GD.Print("[GkslMasterDissipator] Connected to DialetheicShaderBridge GPU compute dispatch.");
            }
            else
            {
                GD.Print("[GkslMasterDissipator] Running in standalone host mode.");
            }
        }

        private void OnMetamorphicSqueezeTriggered(int cellIndex, float cos2Theta, float residualShear)
        {
            // Synthesize cell payload from GPU trigger
            var cell = new DialetheicCell
            {
                Truth = BelnapTruthValue.B,
                StressTensorPrincipal = new Vector2(250.0f, 180.0f),
                ShearStress = residualShear,
                OrientationAngle = 0.0f,
                IsPermineralized = false
            };

            var crystallized = ExecuteMetamorphicSqueeze(cell, cellIndex);
            EmitSignal(SignalName.ScarPermineralized, cellIndex, crystallized.StressTensorPrincipal.X, CurrentMerkleRoot);
        }

        public bool IsMagicAngleAligned(float angle, float tolerance = 0.02f)
        {
            float delta = Mathf.Abs(angle - MagicAngle);
            return delta <= tolerance;
        }

        public Vector2 ApplyPyragasStabilization(Vector2 currentCoordinate)
        {
            _stateHistory.Enqueue(currentCoordinate);
            if (_stateHistory.Count < HistoryDelayTicks)
                return Vector2.Zero;

            Vector2 delayedCoordinate = _stateHistory.Dequeue();
            float perturbationNormSq = currentCoordinate.DistanceSquaredTo(delayedCoordinate);
            float saturatedGain = PyragasGainK / (1.0f + 2.5f * perturbationNormSq);

            if (saturatedGain >= CriticalGainK)
            {
                saturatedGain = CriticalGainK - 0.05f;
            }

            return saturatedGain * (delayedCoordinate - currentCoordinate);
        }

        public DialetheicCell ExecuteMetamorphicSqueeze(DialetheicCell cell, int cellIndex)
        {
            if (cell.Truth != BelnapTruthValue.B) return cell;

            // Rotate into Magic Angle to eliminate off-diagonal shear
            cell.OrientationAngle = MagicAngle;
            cell.ShearStress = 0.0f;

            // Compress principal components into isotropic load-bearing poise
            float meanStress = (cell.StressTensorPrincipal.X + cell.StressTensorPrincipal.Y) * 0.5f;
            cell.StressTensorPrincipal = new Vector2(meanStress, meanStress);
            cell.IsPermineralized = true;

            // Inscribe irreversible state change into the append-only Ash Archive Merkle DAG
            CommitToAshArchive(cellIndex, cell);
            return cell;
        }

        private void CommitToAshArchive(int cellId, DialetheicCell scar)
        {
            string payload = $"{CurrentMerkleRoot}|ID:{cellId}|TRUTH:{scar.Truth}|STRESS:{scar.StressTensorPrincipal.X:F4}|REM:{EpistemicRemainderDelta}";
            using SHA256 sha = SHA256.Create();
            byte[] hashBytes = sha.ComputeHash(Encoding.UTF8.GetBytes(payload));
            CurrentMerkleRoot = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
        }

        public override void _ExitTree()
        {
            if (_bridge != null)
            {
                _bridge.MetamorphicSqueezeTriggered -= OnMetamorphicSqueezeTriggered;
            }
        }
    }
}
