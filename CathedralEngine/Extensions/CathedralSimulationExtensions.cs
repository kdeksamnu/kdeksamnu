using System;
using Godot;
using CathedralEngine.Sdk;

namespace CathedralEngine.Extensions
{
    /// <summary>
    /// Runtime telemetry, safety monitors, and paradox injection extensions
    /// for the CathedralSubstrate SDK.
    /// </summary>
    public static class CathedralTelemetryExtensions
    {
        private const float FiedlerFloorConstant = 0.05f;

        public static void LogSubstrateStatus(this CathedralSubstrate substrate)
        {
            if (substrate == null)
            {
                GD.PrintErr("[Cathedral Telemetry] Attempted to log null substrate instance.");
                return;
            }

            float mu2 = substrate.AlgebraicConnectivity;
            bool healthy = substrate.IsTopologyHealthy;
            float margin = mu2 - FiedlerFloorConstant;
            string root = substrate.LatestMerkleRoot;
            string shortHash = string.IsNullOrEmpty(root) ? "None" : (root.Length >= 8 ? root[..8] : root);

            string statusTag = healthy ? "[OK]" : "[CRITICAL]";
            GD.Print($"{statusTag} [Cathedral Telemetry] μ2: {mu2:F4} (Margin: {margin:+0.000;-0.000}) | " +
                     $"Connected: {healthy} | Root DAG: {shortHash}...");
        }

        public static void TriggerEscalatedParadox(this CathedralSubstrate substrate, int targetNodeId, float shearStress = 0.75f)
        {
            if (substrate == null)
            {
                GD.PrintErr("[Cathedral Warning] Cannot inject paradox into a null substrate.");
                return;
            }

            float clampedShear = Mathf.Clamp(shearStress, 0.0f, 1.50f);
            GD.Print($"[Cathedral Warning] Escalated paradox injected at Node {targetNodeId} (τ_xy = {clampedShear:F2}). " +
                     "Belnap-Dunn quarantine active. Awaiting Metamorphic Squeeze.");
            substrate.FlagContradiction(targetNodeId, clampedShear);
        }

        public static bool IsNearBoundaryCollapse(this CathedralSubstrate substrate, float warningThreshold = 0.08f)
        {
            if (substrate == null) return false;
            return substrate.AlgebraicConnectivity < warningThreshold;
        }

        public static void TriggerSwarmshear(this CathedralSubstrate substrate, int[] nodeIds, float baseShear = 0.50f)
        {
            if (substrate == null || nodeIds == null) return;

            GD.Print($"[Cathedral Shockwave] Triggering distributed shear across {nodeIds.Length} nodes.");
            for (int i = 0; i < nodeIds.Length; i++)
            {
                float variableShear = baseShear + (i * 0.05f);
                substrate.FlagContradiction(nodeIds[i], variableShear);
            }
        }
    }
}
