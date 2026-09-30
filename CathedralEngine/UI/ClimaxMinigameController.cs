using System;
using System.Collections.Generic;
using Godot;
using CathedralEngine.Sdk;
using CathedralEngine.Core.Paraconsistent;

namespace CathedralEngine.UI
{
    [GlobalClass]
    public partial class ClimaxMinigameController : Control
    {
        [Signal] public delegate void OnClimaxResolvedEventHandler(bool isSuccess, string finalMerkleRoot);

        [ExportGroup("Pillar 1: Logic Array")]
        [Export] public HSlider AngleSlider { get; set; }
        [Export] public HSlider DampingSlider { get; set; }
        [Export] public Label LogicStatusLabel { get; set; }
        [Export] public Button ExecuteSqueezeButton { get; set; }

        [ExportGroup("Pillar 2: Structural Mass")]
        [Export] public ProgressBar FiedlerProgressBar { get; set; }
        [Export] public Label FiedlerValueLabel { get; set; }
        [Export] public Label TokenCountLabel { get; set; }
        [Export] public Button DeployBridgeButton { get; set; }

        [ExportGroup("Pillar 3: Ash Archive Ledger")]
        [Export] public Label MerkleRootLabel { get; set; }
        [Export] public RichTextLabel LedgerAuditLog { get; set; }

        private CathedralSubstrate _substrate;
        private int _hebbianTokens = 3;
        private int _pendingContradictionNode = 2;
        private bool _isParadoxActive = true;

        private const float MagicAngleDeg = 54.7356f;
        private const float AngleToleranceDeg = 2.0f;
        private const float CriticalDampingCeiling = 0.75f;

        public override void _Ready()
        {
            _substrate = new CathedralSubstrate(targetConnectivity: 0.15f, floorThreshold: 0.05f);

            int n0 = _substrate.AddNode(new Vector2(100, 100));
            int n1 = _substrate.AddNode(new Vector2(250, 120));
            int n2 = _substrate.AddNode(new Vector2(400, 200));
            int n3 = _substrate.AddNode(new Vector2(150, 300));

            _substrate.ConnectNodes(n0, n1, 1.2f);
            _substrate.ConnectNodes(n1, n2, 0.8f);
            _substrate.ConnectNodes(n2, n3, 1.5f);
            _substrate.ConnectNodes(n3, n0, 1.0f);

            // Inject Climax state: contradiction on node 2 and severed edge (1, 2)
            _substrate.FlagContradiction(_pendingContradictionNode, initialShearStress: 0.75f);
            _substrate.ConnectNodes(1, 2, 0.0f);

            if (ExecuteSqueezeButton != null)
                ExecuteSqueezeButton.Pressed += OnExecuteSqueezePressed;

            if (DeployBridgeButton != null)
                DeployBridgeButton.Pressed += OnDeployBridgePressed;

            _substrate.OnContradictionPermineralized += OnScarPermineralized;
            _substrate.OnTopologyAutoBridged += OnTopologyRepaired;

            UpdateUI();
        }

        public override void _Process(double delta)
        {
            _substrate.Update((float)delta);
            UpdateUI();
            CheckVictoryConditions();
        }

        private void UpdateUI()
        {
            if (AngleSlider != null && DampingSlider != null && LogicStatusLabel != null)
            {
                float currentAngle = (float)AngleSlider.Value;
                float currentK = (float)DampingSlider.Value;

                bool isAngleAligned = Mathf.Abs(currentAngle - MagicAngleDeg) <= AngleToleranceDeg;
                bool isDampingSafe = currentK < CriticalDampingCeiling;

                string angleStatus = isAngleAligned ? "[ALIGNED]" : "[UNALIGNED]";
                string dampingStatus = isDampingSafe ? "[STABLE]" : "[EXPLOSION RISK]";

                LogicStatusLabel.Text = $"Angle: {currentAngle:F1}° {angleStatus} | Gain K: {currentK:F2} {dampingStatus}";
                
                if (ExecuteSqueezeButton != null)
                {
                    ExecuteSqueezeButton.Disabled = !(_isParadoxActive && isAngleAligned && isDampingSafe);
                }
            }

            if (FiedlerProgressBar != null && FiedlerValueLabel != null)
            {
                float mu2 = _substrate.AlgebraicConnectivity;
                FiedlerProgressBar.Value = Mathf.Clamp(mu2 / 0.20f * 100.0f, 0.0f, 100.0f);
                
                string healthTag = _substrate.IsTopologyHealthy ? "STABLE" : "DELAMINATING";
                FiedlerValueLabel.Text = $"μ2: {mu2:F4} ({healthTag})";
                FiedlerValueLabel.Modulate = _substrate.IsTopologyHealthy ? Colors.DarkTurquoise : Colors.Crimson;
            }

            if (TokenCountLabel != null)
            {
                TokenCountLabel.Text = $"xHebbian Tokens: {_hebbianTokens}";
            }

            if (DeployBridgeButton != null)
            {
                DeployBridgeButton.Disabled = _hebbianTokens <= 0 || _substrate.IsTopologyHealthy;
            }

            if (MerkleRootLabel != null)
            {
                string root = _substrate.LatestMerkleRoot;
                MerkleRootLabel.Text = $"Ash DAG Root: {(root.Length >= 16 ? root[..16] : root)}...";
            }
        }

        private void OnExecuteSqueezePressed()
        {
            if (!_isParadoxActive) return;

            _substrate.Update(0.016f);
            _isParadoxActive = false;
            AppendLog($"[LOGIC] Contradiction at Node {_pendingContradictionNode} permineralized at θ=54.74°.");
        }

        private void OnDeployBridgePressed()
        {
            if (_hebbianTokens <= 0) return;

            _hebbianTokens--;
            _substrate.ConnectNodes(1, 2, 1.25f);
            AppendLog("[MASS] Deployed manual xHebbian hyper-edge across Node 1 <-> 2.");
        }

        private void OnScarPermineralized(int nodeId, string merkleRoot)
        {
            AppendLog($"[PERSISTENCE] Node {nodeId} committed to Ash Archive. DAG Root: {merkleRoot[..8]}...");
        }

        private void OnTopologyRepaired(int u, int v)
        {
            AppendLog($"[MASS] Automated topological seam bridged: Node {u} <-> {v}.");
        }

        private void AppendLog(string message)
        {
            if (LedgerAuditLog != null)
            {
                LedgerAuditLog.AppendText($"{message}\n");
            }
            GD.Print(message);
        }

        private void CheckVictoryConditions()
        {
            if (!_isParadoxActive && _substrate.IsTopologyHealthy)
            {
                SetProcess(false);
                AppendLog("[VICTORY] All three pillars synchronized. Manifold stabilized under Lex I.");
                EmitSignal(SignalName.OnClimaxResolved, true, _substrate.LatestMerkleRoot);
            }
        }
    }
}
