# Repo audit: kdeksamnu-audit

## 1. Inventory
301 files.

| ext | count |
|---|---|
| .py | 97 |
| .uid | 27 |
| .cs | 25 |
| .log | 19 |
| .md | 18 |
| .html | 14 |
| .rs | 11 |
| .png | 11 |
| .js | 10 |
| .sh | 9 |
| (none) | 9 |
| .gd | 6 |
| .json | 4 |
| .txt | 4 |
| .import | 3 |

Lines of source by language: .html=16923, .py=8694, .js=2935, .cs=2358, .rs=673, .gd=333, .sh=259, .gdshader=154, .glsl=147

## 2. Hygiene problems
- Database/WAL file in repo: `ash_archive.db-wal`
- Database/WAL file in repo: `ash_archive.db-shm`
- Database/WAL file in repo: `ash_archive.db`
- Merge-conflict markers: `MlaosSimulationHarness.cs`
- Merge-conflict markers: `README.md`
- `.godot/` cache is present.

## 3. Code substance

| file | lines | stub markers | funcs (empty/total) |
|---|---|---|---|
| `AshArchiveLedger.cs` | 64 | 0 |  |
| `CathedralEngine/Core/Archive/AshArchiveVisualizer.cs` | 53 | 0 |  |
| `CathedralEngine/Core/Audio/CathedralAudioSynth.cs` | 85 | 0 |  |
| `CathedralEngine/Core/Metaphysics/MetaphysicalCompiler.cs` | 102 | 0 |  |
| `CathedralEngine/Core/Paraconsistent/DialetheicShaderBridge.cs` | 171 | 0 |  |
| `CathedralEngine/Core/Paraconsistent/GkslMasterDissipator.cs` | 113 | 0 |  |
| `CathedralEngine/Core/Synthesis/CoupledScarDissipator.cs` | 101 | 0 |  |
| `CathedralEngine/Core/Topological/DiscreteLaplacianSolver.cs` | 208 | 0 |  |
| `CathedralEngine/Extensions/CathedralSimulationExtensions.cs` | 66 | 0 |  |
| `CathedralEngine/Narrative/NarrativeBranchManager.cs` | 58 | 0 |  |
| `CathedralEngine/Scenes/GameWorld.cs` | 110 | 0 |  |
| `CathedralEngine/Sdk/CathedralSubstrate.cs` | 96 | 0 |  |
| `CathedralEngine/UI/ClimaxMinigameController.cs` | 171 | 0 |  |
| `CathedralEngine/UI/ObserverEyeDashboard.cs` | 103 | 0 |  |
| `CoupledScarDissipator.cs` | 114 | 0 |  |
| `DialetheicBuffer.glsl` | 53 | 0 |  |
| `MlaosSimulationHarness.cs` | 243 | 0 |  |
| `Program.cs` | 50 | 0 |  |
| `PyragasDampingController.cs` | 106 | 0 |  |
| `ThermalDissipationMonitor.cs` | 70 | 0 |  |
| `alembic/env.py` | 56 | 0 | 0/2 |
| `alembic/versions/59bbc58a150a_initial_cathedral_baseline.py` | 87 | 0 | 0/2 |
| `app.py` | 130 | 0 | 0/9 |
| `ash_archive_sync_daemon.py` | 77 | 0 | 0/2 |
| `build_somatic_pipeline.sh` | 20 | 0 |  |
| `cathedral_mesh.html` | 233 | 0 |  |
| `cathedral_mesh_router/src/main.rs` | 21 | 0 |  |
| `cathedral_mesh_router/src/spectral.rs` | 66 | 0 |  |
| `complete_integration_report.sh` | 14 | 0 |  |
| `debug_hash_format.py` | 56 | 0 | 0/0 |
| `deliverables/dallmier_ventures/webhook_resilience.py` | 75 | 0 | 0/3 |
| `deploy_ash_archive.py` | 28 | 0 | 0/1 |
| `deploy_echo_cluster.sh` | 33 | 0 |  |
| `displacement_shader.js` | 27 | 0 |  |
| `duplicate_observer_core.py` | 46 | 0 | 0/2 |
| `engine/__init__.py` | 0 | 0 | 0/0 |
| `engine/api/__init__.py` | 0 | 0 | 0/0 |
| `engine/api/routes/__init__.py` | 0 | 0 | 0/0 |
| `engine/api/routes/cathedral.py` | 64 | 0 | 0/2 |
| `engine/api/routes/chain.py` | 26 | 0 | 0/1 |
| `engine/api/routes/factions.py` | 25 | 0 | 0/2 |
| `engine/api/routes/observers.py` | 28 | 0 | 0/2 |
| `engine/api/routes/spectral.py` | 45 | 0 | 0/1 |
| `engine/api/routes/visuals.py` | 73 | 0 | 0/3 |
| `engine/core/__init__.py` | 0 | 0 | 0/0 |
| `engine/core/belnap.py` | 40 | 0 | 0/2 |
| `engine/core/broadcaster.py` | 25 | 0 | 0/3 |
| `engine/core/merkle.py` | 35 | 0 | 0/2 |
| `engine/core/persistence.py` | 29 | 0 | 0/3 |
| `engine/core/services.py` | 367 | 0 | 0/8 |
| `engine/core/spectral_matrix.py` | 49 | 0 | 0/2 |
| `engine/db/__init__.py` | 0 | 0 | 0/0 |
| `engine/db/models.py` | 84 | 0 | 0/0 |
| `engine/db/session.py` | 37 | 0 | 0/3 |
| `engine/logic/belnap_dunn.py` | 70 | 0 | 0/4 |
| `engine/main.py` | 23 | 0 | 0/3 |
| `engine/schemas/__init__.py` | 0 | 0 | 0/0 |
| `engine/schemas/cathedral.py` | 19 | 0 | 0/0 |
| `engine/schemas/chain.py` | 19 | 0 | 0/0 |
| `engine/schemas/faction.py` | 25 | 0 | 0/0 |
| `engine/schemas/observer.py` | 33 | 0 | 0/0 |
| `engine/schemas/reconciliation.py` | 23 | 0 | 0/0 |
| `engine/schemas/spectral.py` | 67 | 0 | 0/4 |
| `engine/spatial/extractor.py` | 11 | 0 | 0/2 |
| `engine/thermodynamics/heat_sink.py` | 13 | 0 | 0/2 |
| `frontend/shaders/cathedral_fragment.glsl` | 61 | 1 |  |
| `frontend/shaders/dialetheic_logic.glsl` | 33 | 0 |  |
| `frontend/src/hooks/useTopologicalSmoothing.js` | 26 | 0 |  |
| `geometry_refinement.js` | 17 | 0 |  |
| `godot/scripts/BelnapEvaluator.cs` | 23 | 0 |  |
| `godot/scripts/LedgerSyncClient.cs` | 47 | 0 |  |
| `godot/scripts/MerkleValidator.cs` | 21 | 0 |  |
| `hardware/cathedral_bridge.py` | 94 | 0 | 0/6 |
| `ignite_sovereign_runtime.sh` | 22 | 0 |  |
| `initialize_cathedral_core.sh` | 20 | 0 |  |
| `inject_bone_bindings.sh` | 29 | 0 |  |
| `inject_revision.py` | 61 | 0 | 0/1 |
| `lighting_and_bloom.js` | 73 | 0 |  |
| `maestroapp/app.py` | 40 | 0 | 0/2 |
| `main.py` | 11 | 0 | 0/1 |
| `main_cathedral_node.gd` | 10 | 0 |  |
| `mlaos_prime_init.sh` | 11 | 0 |  |
| `nebula/New/cathedral_3d_studio_runtime_deck.html` | 920 | 1 |  |
| `nebula/New/cathedral_world_simulator.html` | 1234 | 0 |  |
| `nebula/New/workspace (2)/dyad/calibrate.py` | 34 | 0 | 0/1 |
| `nebula/New/workspace (2)/dyad/cert_test.py` | 53 | 0 | 0/1 |
| `nebula/New/workspace (2)/dyad/noether_check.py` | 50 | 0 | 0/4 |
| `nebula/New/workspace (2)/dyad/part2.py` | 22 | 0 | 0/0 |
| `nebula/New/workspace (2)/dyad/part3.py` | 71 | 0 | 0/7 |
| `nebula/New/workspace (2)/dyad/part4_drive.py` | 71 | 0 | 0/0 |
| `nebula/New/workspace (2)/dyad/part5_rank.py` | 47 | 0 | 0/1 |
| `nebula/New/workspace (2)/dyad/part6b.py` | 56 | 0 | 0/3 |
| `nebula/New/workspace (2)/dyad/part7_samplesize.py` | 38 | 0 | 0/1 |
| `nebula/New/workspace (2)/dyad/rank_harness.py` | 108 | 0 | 0/6 |
| `nebula/New/workspace (2)/dyad/rc_estimator.py` | 199 | 0 | 0/5 |
| `nebula/New/workspace (2)/dyad/validate.py` | 275 | 0 | 0/6 |
| `nebula/New/workspace (2)/run.sh` | 92 | 0 |  |
| `nebula/New/workspace (2)/splat/claims.py` | 40 | 0 | 0/1 |
| `nebula/New/workspace (2)/splat/claims2.py` | 145 | 0 | 0/6 |
| `nebula/New/workspace (2)/splat/radius_of_validity.py` | 266 | 0 | 0/4 |
| `nebula/New/workspace (2)/splat/sanity.py` | 60 | 0 | 0/1 |
| `nebula/New/workspace (2)/splat/verdict.py` | 54 | 0 | 0/0 |
| `nebula/RADIUS_OF_VALIDITY.html` | 2107 | 33 |  |
| `nebula/ash_archive_service.py` | 98 | 0 | 0/3 |
| `nebula/bench.py` | 46 | 0 | 0/2 |
| `nebula/cathedral_asset_bridge.py` | 88 | 0 | 0/2 |
| `nebula/cathedral_grand_unified_engine.html` | 670 | 0 |  |
| `nebula/cathedral_world_simulator.html` | 386 | 0 |  |
| `nebula/cathedral_world_simulator.py` | 25 | 0 | 0/1 |
| `nebula/core.js` | 1219 | 0 |  |
| `nebula/dbg2.js` | 16 | 0 |  |
| `nebula/demo.html` | 831 | 0 |  |
| `nebula/deploy.py` | 321 | 0 | 0/0 |
| `nebula/deploy_upgrade_18k.py` | 500 | 0 | 0/0 |
| `nebula/fix_godot_native.py` | 173 | 0 | 0/0 |
| `nebula/gemini-code-1789367477637.rs` | 55 | 0 |  |
| `nebula/gemini-code-1789367495958.rs` | 135 | 0 |  |
| `nebula/gemini-code-1789367519644.rs` | 66 | 0 |  |
| `nebula/gemini-code-1789367531987.rs` | 8 | 0 |  |
| `nebula/gemini-code-1789368291728.rs` | 67 | 0 |  |
| `nebula/gemini-code-1789368300045.rs` | 70 | 0 |  |
| `nebula/gemini-code-1789368594628.rs` | 36 | 0 |  |
| `nebula/gemini-code-1789368605528.rs` | 36 | 0 |  |
| `nebula/gemini-code-1789368628392.rs` | 113 | 0 |  |
| `nebula/harness.js` | 170 | 2 |  |
| `nebula/hash_demo.py` | 56 | 0 | 0/3 |
| `nebula/landauer_auditing_circuit.py` | 155 | 0 | 0/8 |
| `nebula/nebula-standalone.html` | 2387 | 0 |  |
| `nebula/nebula-viewer (1).html` | 2337 | 0 |  |
| `nebula/nebula-viewer (2).html` | 2337 | 0 |  |
| `nebula/nebula-viewer.html` | 2315 | 0 |  |
| `nebula/planet_neuro_simulator.html` | 541 | 0 |  |
| `nebula/proceed_local_run.py` | 122 | 0 | 0/2 |
| `nebula/scripts/CathedralECTPipeline.cs` | 83 | 0 |  |
| `nebula/scripts/CathedralECTPipeline.gd` | 68 | 0 |  |
| `nebula/scripts/CathedralTransductionBridge.cs` | 74 | 0 |  |
| `nebula/scripts/CathedralTransductionBridge.gd` | 63 | 0 |  |
| `nebula/scripts/FigureStateVector.cs` | 26 | 0 |  |
| `nebula/setup_bridge.py` | 159 | 0 | 0/0 |
| `nebula/setup_godot_integration.py` | 114 | 0 | 0/0 |
| `nebula/setup_grand_unified.py` | 679 | 0 | 0/0 |
| `nebula/setup_inhabited_manifold.py` | 251 | 0 | 0/0 |
| `nebula/setup_planet_sim.py` | 550 | 0 | 0/0 |
| `nebula/setup_world_simulator.py` | 673 | 0 | 0/0 |
| `nebula/shaders/cathedral_chroma_omega.gdshader` | 67 | 0 |  |
| `nebula/shaders/witness_plate_chiaroscuro.gdshader` | 46 | 0 |  |
| `nebula/sprint_review.js` | 504 | 0 |  |
| `nebula/telemetry_noether_guard.py` | 57 | 0 | 0/4 |
| `nebula/test_core.js` | 264 | 0 |  |
| `nebula/viewer_app.js` | 619 | 1 |  |
| `observer_client.html` | 189 | 0 |  |
| `publish_zenodo.py` | 16 | 0 | 0/0 |
| `rituals/__init__.py` | 0 | 0 | 0/0 |
| `rituals/forge_hook.py` | 54 | 0 | 0/2 |
| `rituals/forge_shader.py` | 38 | 0 | 0/2 |
| `rituals/ignite_cathedral.py` | 102 | 0 | 0/1 |
| `rituals/orchestrator.py` | 88 | 0 | 0/1 |
| `rituals/test_archive_harness.py` | 26 | 0 | 0/1 |
| `rituals/the_grand_manifestation.py` | 135 | 0 | 0/4 |
| `rituals/transduce.py` | 260 | 0 | 0/8 |
| `run_diagnostics.py` | 30 | 0 | 0/0 |
| `scripts/AureliaAvatarController.gd` | 59 | 0 |  |
| `shaders/aurelia_panoptic_dither.gdshader` | 41 | 0 |  |
| `src/mlaos_features/feature_extractor.py` | 9 | 0 | 0/2 |
| `src/mlaos_infra/serving_logger.py` | 9 | 0 | 0/1 |
| `src/mlaos_infra/skew_auditor.py` | 17 | 0 | 0/1 |
| `test_chain_formula.py` | 28 | 0 | syntax error |
| `test_dual_schema.py` | 27 | 0 | syntax error |
| `tests/__init__.py` | 0 | 0 | 0/0 |
| `tests/api/test_spectral_routes.py` | 60 | 0 | 0/4 |
| `tests/schemas/__init__.py` | 0 | 0 | 0/0 |
| `tests/schemas/test_spectral.py` | 50 | 0 | 0/3 |
| `tests/test_compute_dispatch.gd` | 96 | 0 |  |
| `tests/test_isomorphic_pipeline.py` | 72 | 0 | 0/2 |
| `tests/test_shader_pipeline.gd` | 37 | 0 |  |
| `tests/test_sovereign_unit.py` | 26 | 0 | 0/3 |
| `verify_somatic_build.sh` | 18 | 0 |  |
| `visualizer.html` | 436 | 0 |  |

## 4. Tests
11 test-like files.
- `test_chain_formula.py`
- `test_dual_schema.py`
- `tests/test_sovereign_unit.py`
- `tests/test_isomorphic_pipeline.py`
- `tests/test_shader_pipeline.gd`
- `tests/__init__.py`
- `tests/test_compute_dispatch.gd`
- `rituals/test_archive_harness.py`
- `tests/schemas/__init__.py`
- `tests/schemas/test_spectral.py`
- `tests/api/test_spectral_routes.py`
(re-run with --run-tests to execute them)

## 5. Terms in docs vs code
- **Belnap**: docs=6, code files=15 ['deploy_ash_archive.py', 'proceed_local_run.py', 'gemini-code-1789368291728.rs', 'cathedral_grand_unified_engine.html']
- **paraconsistent**: docs=6, code files=16 ['MlaosSimulationHarness.cs', 'inject_revision.py', 'deploy_ash_archive.py', 'proceed_local_run.py']
- **Merkle**: docs=8, code files=33 ['observer_client.html', 'inject_revision.py', 'visualizer.html', 'deploy_ash_archive.py']
- **WAL**: docs=0, code files=2 ['orchestrator.py', 'session.py']
- **Pyragas**: docs=3, code files=3 ['Program.cs', 'cathedral_bridge.py', 'CathedralAudioSynth.cs']
- **stereographic**: docs=2, code files=0 []
- **mutation rate**: docs=1, code files=0 []
- **Harmonic Scar**: docs=5, code files=9 ['MlaosSimulationHarness.cs', 'inject_bone_bindings.sh', 'initialize_cathedral_core.sh', 'main_cathedral_node.gd']
- **Dialetheic**: docs=7, code files=18 ['inject_revision.py', 'visualizer.html', 'proceed_local_run.py', 'setup_inhabited_manifold.py']
- **Zenodo**: docs=0, code files=1 ['publish_zenodo.py']
- **Arduino**: docs=2, code files=1 ['cathedral_bridge.py']
- **Rust**: docs=2, code files=1 ['sprint_review.js']
- **spectral router**: docs=1, code files=0 []
- **Magisterial Arbiter**: docs=0, code files=0 []
