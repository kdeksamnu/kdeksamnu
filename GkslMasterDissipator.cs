using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using Godot;

namespace CathedralEngine.Core.Paraconsistent
{
    public enum BelnapValue
    {
        None = 0,        // N
        False = 1,       // F
        True = 2,        // T
        Both = 3         // B (Dialetheic Contradiction)
    }

    /// <summary>
    /// Governs sub-critical Pyragas time-delayed feedback and GKSL irreversible state relaxation.
    /// Commits permanent scars to the Ash Archive Merkle DAG upon contradiction resolution.
    /// </summary>
    [GlobalClass]
    public partial class GkslMasterDissipator : Node
    {
        [Export] public float DissipationRateGamma { get; set; } = 0.08f;
        [Export] public float PyragasGainK { get; set; } = 0.55f; // Must stay < 0.75 (Sub-critical)
        [Export] public float TauDelayTicks { get; set; } = 4.0f;

        private readonly Queue<float> _stateHistory = new();
        public string CurrentMerkleRoot { get; private set; } = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

        public event Action<string, float, BelnapValue> OnHarmonicScarCommitted;

        public float StepDissipation(float currentState, BelnapValue truthValue, double delta)
        {
            _stateHistory.Enqueue(currentState);
            while (_stateHistory.Count > (int)TauDelayTicks + 1)
            {
                _stateHistory.Dequeue();
            }

            float delayedState = _stateHistory.Peek();

            // Evaluate Pyragas perturbation: D(t) = K * [s(t - tau) - s(t)]
            float pyragasPerturbation = PyragasGainK * (delayedState - currentState);

            // GKSL Lindblad jump operator evaluation for State Both (B)
            float lindbladDecay = 0.0f;
            if (truthValue == BelnapValue.Both)
            {
                // Irreversible contraction toward thermal ground state
                lindbladDecay = -DissipationRateGamma * currentState;

                // Lex I: Inscribe unalterable scar to cryptographic DAG
                CommitHarmonicScar(currentState, truthValue);
            }

            float dState = (float)((pyragasPerturbation + lindbladDecay) * delta);
            return currentState + dState;
        }

        private void CommitHarmonicScar(float amplitude, BelnapValue truth)
        {
            string timestamp = Time.GetTimeStringFromSystem();
            string rawRecord = $"{CurrentMerkleRoot}|{timestamp}|{amplitude:F6}|{truth}";

            using (SHA256 sha = SHA256.Create())
            {
                byte[] hashBytes = sha.ComputeHash(Encoding.UTF8.GetBytes(rawRecord));
                string newRoot = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
                CurrentMerkleRoot = newRoot;

                OnHarmonicScarCommitted?.Invoke(newRoot, amplitude, truth);
            }
        }

        public void AppendMerkleLeaf(string payload)
        {
            using (SHA256 sha = SHA256.Create())
            {
                byte[] hashBytes = sha.ComputeHash(Encoding.UTF8.GetBytes(payload));
                CurrentMerkleRoot = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
            }
        }
    }
}
