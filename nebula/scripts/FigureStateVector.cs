using Godot;
using System;

[GlobalClass]
public partial class FigureStateVector : Resource
{
    [Export] public Vector3 PelvisForward = new Vector3(0, 0, 1);
    [Export] public Vector3 PelvisBackward = new Vector3(0, 0, -1);
    [Export] public float SpinalTorsionAngle = 0.24f;
    [Export] public float GradientShear = 0.412f;

    // Dialetheic Node DN_SCAR_01: Belnap State B (Both)
    [Export] public string DialetheicNodeId = "DN_SCAR_01";
    [Export] public int BelnapStateIndex = 2; // 0=T, 1=F, 2=Both (B), 3=Neither (N)
    [Export] public float QuadratureSqueezeRMinus = 0.68f;

    // Carbon-Silicon Coupling Baseline
    [Export] public float SomaticCadenceHz = 1.50f;
    [Export] public float CouplingIndexGamma = 1.0248f; // Target: 0.8 <= Gamma <= 1.2

    public Vector3 ComputeHarmonicPelvisVector()
    {
        // Resolves Pelvis_forward AND Pelvis_backward via squeezed quadrature
        return (PelvisForward + PelvisBackward) * 0.5f + Vector3.Up * (SpinalTorsionAngle * QuadratureSqueezeRMinus);
    }
}
