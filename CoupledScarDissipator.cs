using System;
using System.Numerics;

namespace CathedralEngine.Physics.Tectonics
{
    public enum BelnapTruthValue
    {
        N = 0,
        F = 1,
        T = 2,
        B = 3
    }

    public struct BasaltBlock
    {
        public int BlockId;
        public BelnapTruthValue Truth;
        public int WindingNumber;
        public float OrientationAngleRad;
        public float ShearStressKPa;
        public Vector2 PrincipalStressKPa;
        public bool IsPermineralized;
        public bool IsQuarantined;
    }

    public sealed class CoupledScarDissipator
    {
        public const float MagicAngleRad = 0.9553166f;
        public const float TetrahedralAngleRad = 1.9106332f;

        public (BasaltBlock Left, BasaltBlock Right) ResolveCoupledPair(
            BasaltBlock left,
            BasaltBlock right,
            Action<object> commitToAshArchive)
        {
            if (left.Truth != BelnapTruthValue.B || right.Truth != BelnapTruthValue.B)
            {
                return (left, right);
            }

            int netCharge = left.WindingNumber + right.WindingNumber;

            if (netCharge == 0 && left.WindingNumber != 0)
            {
                left.OrientationAngleRad = MagicAngleRad * Math.Sign(left.WindingNumber);
                right.OrientationAngleRad = MagicAngleRad * Math.Sign(right.WindingNumber);

                left.ShearStressKPa = 0.0f;
                right.ShearStressKPa = 0.0f;

                float jointMean = (left.PrincipalStressKPa.X + left.PrincipalStressKPa.Y +
                                   right.PrincipalStressKPa.X + right.PrincipalStressKPa.Y) * 0.25f;

                left.PrincipalStressKPa = new Vector2(jointMean, jointMean);
                right.PrincipalStressKPa = new Vector2(jointMean, jointMean);

                left.IsPermineralized = true;
                right.IsPermineralized = true;

                float mutualAngle = Math.Abs(left.OrientationAngleRad - right.OrientationAngleRad);

                var commitPayload = new
                {
                    TransactionType = "BI_CRANIAL_SOLITON_COMMIT",
                    LeftBlockId = left.BlockId,
                    RightBlockId = right.BlockId,
                    WindingLeft = left.WindingNumber,
                    WindingRight = right.WindingNumber,
                    NetTopologicalCharge = 0,
                    LeftAngleRad = left.OrientationAngleRad,
                    RightAngleRad = right.OrientationAngleRad,
                    MutualAngleRad = mutualAngle,
                    MutualAngleDeg = mutualAngle * (180.0f / MathF.PI),
                    StructuralKinematics = "TETRAHEDRAL_CHEVRON_LOCK",
                    MeanCompressiveStressKPa = jointMean,
                    ResidualShearKPa = 0.0f,
                    TimestampUtc = DateTime.UtcNow.ToString("o")
                };

                commitToAshArchive(commitPayload);
            }

            return (left, right);
        }

        public BasaltBlock HandleStateNArrest(
            BasaltBlock block,
            float currentAngleRad,
            float residualShearKPa,
            Action<object> commitToAshArchive)
        {
            block.Truth = BelnapTruthValue.N;
            block.WindingNumber = 0;
            block.OrientationAngleRad = currentAngleRad;
            block.ShearStressKPa = residualShearKPa;
            block.IsPermineralized = false;
            block.IsQuarantined = true;

            var quarantinePayload = new
            {
                TransactionType = "STATE_N_ARRESTED_VOID",
                BlockId = block.BlockId,
                ArrestAngleRad = currentAngleRad,
                ArrestAngleDeg = currentAngleRad * (180.0f / MathF.PI),
                ResidualShearKPa = residualShearKPa,
                Status = "QUARANTINED_UNMINERALIZED",
                TimestampUtc = DateTime.UtcNow.ToString("o")
            };

            commitToAshArchive(quarantinePayload);
            return block;
        }
    }
}
