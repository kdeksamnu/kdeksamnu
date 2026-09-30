using System;
using System.Numerics;
using CathedralEngine.Physics.Damping;
using CathedralEngine.Physics.Tectonics;
using CathedralEngine.Storage.AshArchive;
using CathedralEngine.Thermodynamics;

namespace CathedralEngine.Tests
{
    public static class StandaloneHarness
    {
        public static void Run()
        {
            Console.WriteLine("==================================================================");
            Console.WriteLine(" CATHEDRAL-ENGINE REVISION Ω-07: INTEGRATION SUITE");
            Console.WriteLine(" Physical Datum: Olney, IL (38.7306° N, 88.0853° W) | 1.500 Hz");
            Console.WriteLine("==================================================================");

            var ledger = new AshArchiveLedger("ash_archive_ledger.ndjson");
            var dissipator = new CoupledScarDissipator();
            var pyragas = new PyragasDampingController(gainK: 0.25f, delayMs: 11.2f);
            var thermalMonitor = new ThermalDissipationMonitor();

            var leftBlock = new BasaltBlock
            {
                BlockId = 101,
                Truth = BelnapTruthValue.B,
                WindingNumber = 1,
                ShearStressKPa = 145.0f,
                PrincipalStressKPa = new Vector2(250.0f, 180.0f)
            };

            var rightBlock = new BasaltBlock
            {
                BlockId = 102,
                Truth = BelnapTruthValue.B,
                WindingNumber = -1,
                ShearStressKPa = -145.0f,
                PrincipalStressKPa = new Vector2(250.0f, 180.0f)
            };

            (leftBlock, rightBlock) = dissipator.ResolveCoupledPair(leftBlock, rightBlock, payload =>
            {
                ledger.CommitBlock(payload);
            });

            thermalMonitor.RegisterSqueezeEvent(currentTimestamp: 0.100f);
        }
    }
}
