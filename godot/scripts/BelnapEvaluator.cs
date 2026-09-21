using Godot;
using System;

public partial class BelnapEvaluator : Node
{
    public enum TruthState { True, False, Both, Neither }

    [Export]
    public TruthState CurrentPropositionA { get; set; } = TruthState.True;

    [Export]
    public TruthState CurrentPropositionB { get; set; } = TruthState.False;

    public TruthState ResolveContradiction()
    {
        // Resolves conflicting narrative inputs into a defined state (Belnap-Dunn matrix)
        if (CurrentPropositionA == TruthState.True && CurrentPropositionB == TruthState.True) return TruthState.True;
        if (CurrentPropositionA == TruthState.False || CurrentPropositionB == TruthState.False && CurrentPropositionA != TruthState.True) 
            return (CurrentPropositionA == TruthState.Both || CurrentPropositionB == TruthState.Both) ? TruthState.Both : TruthState.False;
        if (CurrentPropositionA == TruthState.Both || CurrentPropositionB == TruthState.Both) return TruthState.Both;
        return TruthState.Neither;
    }
}
