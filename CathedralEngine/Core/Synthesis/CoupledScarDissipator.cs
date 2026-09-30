using System;
using System.Linq;
using System.Collections.Generic;
using Godot;
using CathedralEngine.Core.Paraconsistent;

namespace CathedralEngine.Core.Synthesis
{
    /// <summary>
    /// Resolves adjacent, oppositely charged State B contradictions 
    /// into a stable Dialetheic Knot (Coupled Scar), preventing mortar fracture.
    /// </summary>
    public partial class CoupledScarDissipator : Node
    {
        [Signal] public delegate void DialetheicKnotFormedEventHandler(int agentA, int agentB, string merkleRoot);

        public enum Chirality { Positive = 1, Negative = -1 }

        private struct PendingParadox
        {
            public int AgentIndex;
            public Chirality Winding;
            public float Timestamp;
        }

        private readonly List<PendingParadox> _pendingParadoxes = new();
        private readonly float _couplingWindowMs = 15.0f; // Must form knot within 15ms to bind

        // Injected reference to check adjacency (mocked for standalone compilation)
        private Func<int, int, bool> _areAdjacentFunc;

        public void SetAdjacencyChecker(Func<int, int, bool> checker)
        {
            _areAdjacentFunc = checker;
        }

        public void RegisterParadox(int agentIndex, Chirality winding, float currentTime)
        {
            _pendingParadoxes.Add(new PendingParadox 
            { 
                AgentIndex = agentIndex, 
                Winding = winding, 
                Timestamp = currentTime 
            });
            
            EvaluateCoupling(currentTime);
        }

        private void EvaluateCoupling(float currentTime)
        {
            // Clean up expired paradoxes (they will fallback to independent Metamorphic Squeeze)
            _pendingParadoxes.RemoveAll(p => (currentTime - p.Timestamp) > _couplingWindowMs);

            // Find adjacent pairs with opposite chirality
            for (int i = 0; i < _pendingParadoxes.Count; i++)
            {
                for (int j = i + 1; j < _pendingParadoxes.Count; j++)
                {
                    var p1 = _pendingParadoxes[i];
                    var p2 = _pendingParadoxes[j];

                    if (p1.Winding != p2.Winding && _areAdjacentFunc != null && _areAdjacentFunc(p1.AgentIndex, p2.AgentIndex))
                    {
                        ExecuteDialetheicKnot(p1.AgentIndex, p2.AgentIndex);
                        
                        // Remove resolved paradoxes
                        _pendingParadoxes.RemoveAt(j);
                        _pendingParadoxes.RemoveAt(i);
                        return; // Resolve one knot per evaluation pass
                    }
                }
            }
        }

        private void ExecuteDialetheicKnot(int idxA, int idxB)
        {
            GD.Print($"[M6 SYNTHESIS] Dialetheic Knot formed between Agent {idxA} and {idxB}. Shear canceled. Hydrostatic lock engaged.");

            // 1. Halt independent rotation; lock both agents at complementary Magic Angles
            // Agent A rotates +54.74°, Agent B rotates -54.74° around the shared normal
            
            // 2. Trigger Dialetheic Sintering (Mortar compression)
            float sinteringHeat = 45.0f; // Kelvin increase, safely below Tg (Lex III)
            
            // 3. Generate Composite Ash Node
            string compositeHash = GenerateCompositeMerkleRoot(idxA, idxB, sinteringHeat);
            
            EmitSignal(SignalName.DialetheicKnotFormed, idxA, idxB, compositeHash);
        }

        private string GenerateCompositeMerkleRoot(int idxA, int idxB, float heat)
        {
            // SHA-512( Tick || "KNOT" || idxA || idxB || LinkingNumber=1 || Heat )
            long tick = (long)(Time.GetTicksMsec() / (1000.0 / 1.5)); // 1.5 Hz somatic tick
            string payload = $"{tick}|KNOT|{idxA}|{idxB}|L1|{heat:F2}";
            
            // Mock SHA-512 for simulation harness
            return $"SHA512::{System.Security.Cryptography.SHA512.HashData(System.Text.Encoding.UTF8.GetBytes(payload)).AsSpan().Slice(0, 16).ToArray().Select(b => b.ToString("x2")).Aggregate((a, b) => a + b)}";
        }
    }
}
