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

        public event Action<string, float, BelnapTruthValue> OnHarmonicScarCommitted;

        private readonly Queue<Vector2> _stateHistory = new();
        private const int HistoryDelayTicks = 11;
        private DialetheicShaderBridge _bridge;

        public string CurrentMerkleRoot { get; private set; } = "0000000000000000000000000000000000000000000000000000000000000000";

        public override void _Ready()
        {
            _bridge = GetNodeOrNull<DialetheicShaderBridge>(ShaderBridgePath);
            if (_bridge != null)
            {
                _bridge.MetamorphicSqueezeTriggered += OnMetamorphicSqueezeTriggered;
                GD.Print("[GkslMasterDissipator] Connected to DialetheicShaderBridge GPU compute dispatch.");
            }
        }

        public float StepDissipation(float currentSpeed, BelnapTruthValue truth, double delta)
        {
            // GKSL Lindblad Dissipation: Contradictions (State B) suffer paraconsistent drag
            if (truth == BelnapTruthValue.B)
            {
                return currentSpeed * MathF.Max(0.0f, 1.0f - (PyragasGainK * 1.5f * (float)delta));
            }
            if (truth == BelnapTruthValue.N)
            {
                return currentSpeed * MathF.Max(0.0f, 1.0f - (PyragasGainK * 0.5f * (float)delta));
            }
            return currentSpeed * MathF.Max(0.0f, 1.0f - (EpistemicRemainderDelta * (float)delta));
        }

        private void OnMetamorphicSqueezeTriggered(int cellIndex, float cos2Theta, float residualShear)
        {
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
            OnHarmonicScarCommitted?.Invoke(CurrentMerkleRoot, crystallized.StressTensorPrincipal.X, BelnapTruthValue.B);
        }

        public DialetheicCell ExecuteMetamorphicSqueeze(DialetheicCell cell, int cellIndex)
        {
            if (cell.Truth != BelnapTruthValue.B) return cell;

            cell.OrientationAngle = MagicAngle;
            cell.ShearStress = 0.0f;

            float meanStress = (cell.StressTensorPrincipal.X + cell.StressTensorPrincipal.Y) * 0.5f;
            cell.StressTensorPrincipal = new Vector2(meanStress, meanStress);
            cell.IsPermineralized = true;

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
