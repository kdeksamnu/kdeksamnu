using Godot;
using System;

namespace CathedralEngine.Core.Metaphysics
{
    /// <summary>
    /// The Metaphysical Compiler enforces dimensional homogeneity and 
    /// topological saturation limits within the MLAOS-Prime universe.
    /// </summary>
    public static class MetaphysicalCompiler
    {
        public enum Axiom { Theta, Psi, Delta, Phi, Omega, Epsilon, Null }

        // PATCH 2: TRANSDUCTIVE THERMODYNAMIC CONSTANTS
        // Ensures conservation of energy during Affect -> Mechanical transduction
        public const float Kappa_AM = 1.5e-3f; // Affective-to-Mechanical coupling (J_mech / J_affect)
        public const float T_KELVIN = 293.15f; // Ambient temperature (20°C)
        public const float K_B = 1.380649e-23f; // Boltzmann constant (J/K)

        public struct AFieldTelemetry
        {
            public float MechanicalEnergy_J;   // Joules
            public float AffectiveEnergy_J;    // Joules
            public float EntropyLoss_J;        // Joules (Landauer limit dissipation)
            public float SemanticDensity;      // Dimensionless [0, 1]
            public Axiom DominantRegime;
        }

        public static AFieldTelemetry CompileAgent(
            float metabolicEnergy_J, 
            float fiedlerLocal, 
            int driveState, 
            bool isPermineralized, 
            float repFactor)
        {
            AFieldTelemetry telemetry = new AFieldTelemetry();
            telemetry.SemanticDensity = Mathf.Clamp(fiedlerLocal, 0.0f, 1.0f);

            // PATCH 3: TOPOLOGICAL SATURATION & DECAY THRESHOLD
            // If semantic density drops below critical threshold for too long, 
            // the scar transitions from load-bearing (B) to entropic ash (N).
            const float SATURATION_THRESHOLD = 0.05f;
            
            if (isPermineralized)
            {
                if (telemetry.SemanticDensity < SATURATION_THRESHOLD)
                {
                    // Garbage collection: Scar degrades into Null state
                    telemetry.DominantRegime = Axiom.Null;
                    telemetry.MechanicalEnergy_J = 0.0f;
                }
                else
                {
                    telemetry.DominantRegime = Axiom.Delta; // Stable Archive
                    telemetry.MechanicalEnergy_J = metabolicEnergy_J * 0.1f; // Residual mass
                }
                telemetry.AffectiveEnergy_J = 0.0f;
                telemetry.EntropyLoss_J = 0.0f;
            }
            else if (telemetry.SemanticDensity < SATURATION_THRESHOLD)
            {
                telemetry.DominantRegime = Axiom.Null;
                telemetry.MechanicalEnergy_J = 0.0f;
                telemetry.AffectiveEnergy_J = 0.0f;
                telemetry.EntropyLoss_J = 0.0f;
            }
            else
            {
                telemetry.DominantRegime = driveState switch
                {
                    1 => Axiom.Phi, 2 => Axiom.Theta, 3 => Axiom.Delta, _ => Axiom.Psi
                };

                // Transductive Continuity Equation: E_mech = κ * E_affect - TΔS
                telemetry.AffectiveEnergy_J = metabolicEnergy_J; 
                float topologicalStress = 1.0f / (telemetry.SemanticDensity + 0.05f);
                
                // Entropy loss due to affective collapse (Landauer limit scaled by stress)
                // ΔS = k_B * ln(2) per erased bit of topological ambiguity
                float bitsErased = topologicalStress * (1.0f - repFactor);
                telemetry.EntropyLoss_J = T_KELVIN * K_B * Mathf.Log(2.0f) * bitsErased * 1e20f; // Scaled for macroscopic visibility

                telemetry.MechanicalEnergy_J = Mathf.Max(0.0f, 
                    (Kappa_AM * telemetry.AffectiveEnergy_J) - telemetry.EntropyLoss_J);
            }

            return telemetry;
        }

        public static (Axiom globalAxiom, float globalStress) CompileGlobalField(float globalLambda2, float globalStress)
        {
            Axiom globalAxiom = globalLambda2 switch
            {
                > 0.8f => Axiom.Theta,
                > 0.5f => Axiom.Psi,
                > 0.2f => Axiom.Omega,
                _ => Axiom.Null // Triggers Merkle DAG Epoch Compression (Garbage Collection)
            };
            return (globalAxiom, globalStress);
        }
    }
}
