using System;
using System.Collections.Generic;
using Godot;
using CathedralEngine.Sdk;
using CathedralEngine.Extensions;

namespace CathedralEngine.Narrative
{
    public enum ChoiceAlignment { Thesis, Antithesis, Synthesis }

    public struct DialogueChoice
    {
        public string PromptText;
        public ChoiceAlignment Alignment;
        public float DeltaMu2;
        public float DeltaShear;
        public string ConsequenceLog;
    }

    public partial class NarrativeBranchManager : Node
    {
        [Signal] public delegate void OnDialogueResolvedEventHandler(string logEntry, string merkleRoot);

        private CathedralSubstrate _substrate;
        private readonly List<string> _immutableDecisionLog = new();

        public void Initialize(CathedralSubstrate substrate)
        {
            _substrate = substrate;
        }

        public void SelectChoice(DialogueChoice choice, int targetNodeId)
        {
            if (_substrate == null) return;

            if (choice.Alignment == ChoiceAlignment.Thesis)
            {
                _substrate.ConnectNodes(targetNodeId, 0, 1.5f);
            }
            else if (choice.Alignment == ChoiceAlignment.Antithesis)
            {
                _substrate.TriggerEscalatedParadox(targetNodeId, choice.DeltaShear);
            }
            else if (choice.Alignment == ChoiceAlignment.Synthesis)
            {
                _substrate.FlagContradiction(targetNodeId, choice.DeltaShear);
                _substrate.Update(0.016f);
            }

            string logEntry = $"[DECISION] {choice.Alignment}: {choice.ConsequenceLog} | μ2: {_substrate.AlgebraicConnectivity:F3}";
            _immutableDecisionLog.Add(logEntry);

            EmitSignal(SignalName.OnDialogueResolved, logEntry, _substrate.LatestMerkleRoot);
        }

        public IReadOnlyList<string> GetDecisionHistory() => _immutableDecisionLog.AsReadOnly();
    }
}
