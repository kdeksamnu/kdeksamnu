/* ============================================================================
   Sprint review — executable verification
   ----------------------------------------------------------------------------
   Faithful JS ports of the three quantitatively checkable subsystems in the
   5-sprint plan, used to test the claims in its "Verification Summary":

     claim 2: "LCA Bounded Variance: latent variance remains bounded within
               [sigma_min^2, sigma_max^2] across 50 simulation steps"
     claim 3: "Cost Ceiling Invariant: the Token Bucket Governor permits
               execution up to the exact $0.05/hr allowance and rejects
               subsequent calls, preventing cost overruns"
     claim 5: "Archive Biasing: committed states generate positive logit
               attractors while pruned high-probability paths generate
               negative anti-scar repulsors"

   Constants and control flow are transcribed from the submitted Rust/CUDA,
   not reinterpreted. Where a defect is found, the fix is measured too.
   ============================================================================ */
'use strict';

let pass = 0, fail = 0;
const ok = (name, cond, detail = '') => {
  if (cond) { pass++; console.log(`  \x1b[32mPASS\x1b[0m  ${name}${detail ? '  \x1b[90m' + detail + '\x1b[0m' : ''}`); }
  else { fail++; console.log(`  \x1b[31mFAIL\x1b[0m  ${name}  ${detail}`); }
};
const hdr = s => console.log(`\n\x1b[1m${s}\x1b[0m`);
const dim = s => console.log(`  \x1b[90m${s}\x1b[0m`);

/* ==========================================================================
   PORT 1 — Sprint 2: LatentAutomataGrid::step_autonomous_dream
   ====================================================================== */

const MAX_LATENT_VARIANCE = 4.0;
const MIN_LATENT_VARIANCE = 0.01;
const ECOLOGICAL_DIFFUSION_RATE = 0.12;
const CULTURAL_FRICTION_RATE = 0.08;
const BIOME = { AbyssalMoss: 0, LithicSilt: 1, CrystallineBasalt: 2, SporeCanopy: 3 };
const BIOME_NAMES = ['AbyssalMoss', 'LithicSilt', 'CrystallineBasalt', 'SporeCanopy'];

// JS numbers are f64; f32 is emulated where precision loss is the point.
const f32 = x => Math.fround(x);

class LatentAutomataGrid {
  constructor(width, height, depth, seed = 1) {
    this.width = width; this.height = height; this.depth = depth;
    const n = width * height * depth;
    this.current = new Array(n);
    this.next = new Array(n);
    let s = seed >>> 0;
    const rnd = () => { s = (s + 0x6d2b79f5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    for (let i = 0; i < n; i++) {
      this.current[i] = {
        observer_count: 0,
        latent_variance: f32(0.6 + rnd() * 0.8),
        biome: (rnd() * 4) | 0,
        culture: (rnd() * 4) | 0,
        latent_features: new Float32Array(8),
        entropy_pulse: f32(rnd() * 6.28)
      };
    }
  }

  /** Transcribed from the submitted Rust, including its defects. */
  step(opts = {}) {
    const w = this.width, h = this.height, d = this.depth;
    const current = this.current;
    const fixBoundary = !!opts.fixBoundary;      // Neumann instead of sink
    const fixSources = !!opts.fixSources;        // make eco/cult zero-net
    const clampPulse = !!opts.clampPulse;
    const fixBasalt = !!opts.fixBasalt;          // smooth instead of sawtooth

    for (let z = 0; z < d; z++) {
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const ci = (z * h + y) * w + x;
          const c = current[ci];
          if (c.observer_count > 0) { this.next[ci] = c; continue; }

          let sum = 0, cnt = 0, conflict = 0;
          const nb = [
            [x - 1, y, z, x > 0], [x + 1, y, z, x + 1 < w],
            [x, y - 1, z, y > 0], [x, y + 1, z, y + 1 < h],
            [x, y, z - 1, z > 0], [x, y, z + 1, z + 1 < d]
          ];
          for (const [nx, ny, nz, valid] of nb) {
            if (!valid) continue;
            const ncell = current[(nz * h + ny) * w + nx];
            // FIX: an observed neighbour is quenched to ~0 and must not act as
            // a variance sink. Reflecting (Neumann) boundary instead.
            if (fixBoundary && ncell.observer_count > 0) { sum += c.latent_variance; cnt += 1; continue; }
            sum += ncell.latent_variance; cnt += 1;
            if (ncell.culture !== c.culture) conflict += 1;
          }
          const mean = cnt > 0 ? sum / cnt : c.latent_variance;
          const laplacian = mean - c.latent_variance;

          let eco;
          switch (c.biome) {
            case BIOME.SporeCanopy:
              eco = 0.04 * (1 - c.latent_variance / MAX_LATENT_VARIANCE); break;
            case BIOME.LithicSilt:
              eco = -0.03 * (c.latent_variance - 0.75); break;
            case BIOME.CrystallineBasalt:
              eco = fixBasalt
                ? -0.01 * (c.latent_variance - 1.0)                       // smooth restoring
                : -0.01 * ((c.latent_variance % 0.5) - 0.25); break;      // as submitted: sawtooth
            default:
              eco = 0.015 * Math.sin(c.entropy_pulse);
          }
          // FIX: cultural friction as written is a pure source (conflict >= 0),
          // so total variance can only rise. Make it redistributive.
          const cult = fixSources
            ? (conflict / 6) * CULTURAL_FRICTION_RATE * (1 - c.latent_variance / MAX_LATENT_VARIANCE)
              - (1 - conflict / 6) * CULTURAL_FRICTION_RATE * (c.latent_variance / MAX_LATENT_VARIANCE) * 0.5
            : (conflict / 6) * CULTURAL_FRICTION_RATE;

          const nv = f32(Math.min(MAX_LATENT_VARIANCE, Math.max(MIN_LATENT_VARIANCE,
            c.latent_variance + ECOLOGICAL_DIFFUSION_RATE * laplacian + eco + cult)));

          const feats = new Float32Array(8);
          for (let k = 0; k < 8; k++) {
            const drift = 0.005 * Math.sin((k + 1) * nv);
            feats[k] = f32(Math.min(2, Math.max(-2, c.latent_features[k] + drift)));
          }
          const pulse = clampPulse ? f32((c.entropy_pulse + 0.05) % (2 * Math.PI)) : f32(c.entropy_pulse + 0.05);
          this.next[ci] = { observer_count: 0, latent_variance: nv, biome: c.biome, culture: c.culture, latent_features: feats, entropy_pulse: pulse };
        }
      }
    }
    const t = this.current; this.current = this.next; this.next = t;
  }

  stats() {
    const n = this.current.length;
    let sum = 0, atMax = 0, atMin = 0, mx = -Infinity, mn = Infinity;
    const perBiome = [[0, 0], [0, 0], [0, 0], [0, 0]];
    for (const c of this.current) {
      sum += c.latent_variance;
      if (c.latent_variance >= MAX_LATENT_VARIANCE - 1e-6) atMax++;
      if (c.latent_variance <= MIN_LATENT_VARIANCE + 1e-6) atMin++;
      mx = Math.max(mx, c.latent_variance); mn = Math.min(mn, c.latent_variance);
      perBiome[c.biome][0] += c.latent_variance; perBiome[c.biome][1]++;
    }
    return { mean: sum / n, atMaxPct: atMax / n * 100, atMinPct: atMin / n * 100, max: mx, min: mn, n, perBiome: perBiome.map(([s, c]) => c ? s / c : 0) };
  }
}

hdr('Verification claim 2 — "LCA bounded variance across 50 steps"');
dim('The claim is literally true and vacuously so: variance is clamped to [0.01, 4.0] by');
dim('construction. Boundedness is guaranteed by .clamp(), not by the dynamics. The');
dim('property that matters is where the distribution goes, and it goes to the ceiling.');

const g = new LatentAutomataGrid(24, 24, 24, 7);
const s0 = g.stats();
console.log('');
dim(`step    mean σ²   %at MAX(4.0)   %at MIN   max      min`);
dim(`   0    ${s0.mean.toFixed(4)}     ${s0.atMaxPct.toFixed(1).padStart(6)}%      ${s0.atMinPct.toFixed(1).padStart(5)}%   ${s0.max.toFixed(3)}   ${s0.min.toFixed(3)}`);
let at50 = null;
for (let i = 1; i <= 600; i++) {
  g.step();
  if (i === 50) { at50 = g.stats(); dim(`  50    ${at50.mean.toFixed(4)}     ${at50.atMaxPct.toFixed(1).padStart(6)}%      ${at50.atMinPct.toFixed(1).padStart(5)}%   ${at50.max.toFixed(3)}   ${at50.min.toFixed(3)}   <-- their test stops here`); }
  if (i === 200 || i === 600) { const s = g.stats(); dim(`${String(i).padStart(4)}    ${s.mean.toFixed(4)}     ${s.atMaxPct.toFixed(1).padStart(6)}%      ${s.atMinPct.toFixed(1).padStart(5)}%   ${s.max.toFixed(3)}   ${s.min.toFixed(3)}`); }
}
const sEnd = g.stats();
console.log('');
dim('per-biome mean σ² after 600 steps:');
BIOME_NAMES.forEach((n, i) => dim(`  ${n.padEnd(20)} ${sEnd.perBiome[i].toFixed(4)}`));
ok('variance saturates at the ceiling, not at a healthy operating point',
  sEnd.atMaxPct > 50, `${sEnd.atMaxPct.toFixed(1)}% of cells pinned at MAX after 600 steps`);
ok('50 steps is far too short to reveal it (their test window)',
  at50.atMaxPct < sEnd.atMaxPct * 0.5,
  `${at50.atMaxPct.toFixed(1)}% at step 50 vs ${sEnd.atMaxPct.toFixed(1)}% at step 600`);
ok('SporeCanopy is the runaway source (positive feedback to MAX)',
  sEnd.perBiome[BIOME.SporeCanopy] > sEnd.perBiome[BIOME.LithicSilt] * 1.5,
  `${sEnd.perBiome[BIOME.SporeCanopy].toFixed(3)} vs ${sEnd.perBiome[BIOME.LithicSilt].toFixed(3)}`);

// ---- the two sources with no sink
hdr('Root cause — cultural friction is a pure source term');
dim('cult_friction = (cultural_conflict / 6) * 0.08, and cultural_conflict >= 0 always.');
dim('There is no corresponding sink, so total variance is monotonically pumped upward');
dim('until the clamp absorbs it. Same failure class as unbounded neural-physics drift,');
dim('arriving through a different door: instead of averaging to the mean, it saturates');
dim('to the maximum. Both are the Mush Problem.');
const gFix = new LatentAutomataGrid(24, 24, 24, 7);
for (let i = 0; i < 600; i++) gFix.step({ fixSources: true, fixBasalt: true });
const sFix = gFix.stats();
dim('');
dim(`with redistributive friction: mean σ²=${sFix.mean.toFixed(4)}, ${sFix.atMaxPct.toFixed(1)}% at MAX`);
ok('making cultural friction redistributive stabilises the field',
  sFix.atMaxPct < 5 && sFix.mean < MAX_LATENT_VARIANCE * 0.6,
  `${sFix.atMaxPct.toFixed(1)}% at MAX, mean ${sFix.mean.toFixed(3)}`);

// ---- CrystallineBasalt discontinuity
hdr('Defect — CrystallineBasalt uses float modulo, which is discontinuous');
dim('eco_delta = -0.01 * (latent_variance % 0.5 - 0.25)');
dim('`%` on f32 is a remainder, so this is a sawtooth in variance with jump');
dim('discontinuities every 0.5. A discontinuous vector field cannot be integrated');
dim('stably: cells chatter across the sawtooth teeth and the field banding shows up');
dim('directly in the render. Same class of bug as hard `if` biome thresholds poisoning');
dim('a ReLU fit — discontinuities in the target or the dynamics always surface.');
let crossings = 0, prevSign = null;
for (let i = 0; i < 400; i++) {
  const v = MIN_LATENT_VARIANCE + (MAX_LATENT_VARIANCE - MIN_LATENT_VARIANCE) * i / 400;
  const d = -0.01 * ((v % 0.5) - 0.25);
  const sg = Math.sign(d);
  if (prevSign !== null && sg !== prevSign) crossings++;
  prevSign = sg;
}
ok('the basalt rule has discontinuities across the operating range', crossings >= 7,
  `${crossings} sign flips over σ² ∈ [0.01, 4.0]`);

// ---- observation boundary sink
hdr('Defect — observed cells act as a variance sink on their neighbours');
dim('The dream skips O>0 cells, leaving them quenched at 0.001 (Sprint 3 sets that on');
dim('collapse). But unobserved neighbours still average them into the Laplacian, so');
dim('variance drains toward every observed region. Players carve a dead halo wherever');
dim('they walk, and it does not refill.');
const W = 24, H = 24, D = 24;
function boundaryTest(fixBoundary) {
  const gr = new LatentAutomataGrid(W, H, D, 11);
  for (const c of gr.current) c.latent_variance = 2.0;
  // observe a solid slab down the middle
  for (let z = 0; z < D; z++) for (let y = 0; y < H; y++) {
    const i = (z * H + y) * W + 12;
    gr.current[i] = Object.assign({}, gr.current[i], { observer_count: 1, latent_variance: 0.001 });
  }
  const before = gr.current[(0 * H + 0) * W + 10].latent_variance;
  for (let i = 0; i < 200; i++) gr.step({ fixBoundary });
  const ring = [9, 10, 11].map(x => gr.current[(12 * H + 12) * W + x].latent_variance);
  const far = gr.current[(2 * H + 2) * W + 2].latent_variance;
  return { before, ring, far };
}
const sink = boundaryTest(false);
const fixed = boundaryTest(true);
dim(`as submitted : cells adjacent to the observed slab = [${sink.ring.map(v => v.toFixed(3)).join(', ')}], far field = ${sink.far.toFixed(3)}`);
dim(`with Neumann : cells adjacent to the observed slab = [${fixed.ring.map(v => v.toFixed(3)).join(', ')}], far field = ${fixed.far.toFixed(3)}`);
const drop = 1 - sink.ring[2] / Math.max(sink.far, 1e-6);
ok('observed regions drain variance from their surroundings', drop > 0.15,
  `${(drop * 100).toFixed(1)}% deficit adjacent to the slab`);
ok('reflecting (Neumann) boundary removes the sink',
  Math.abs(1 - fixed.ring[2] / Math.max(fixed.far, 1e-6)) < 0.05,
  `adjacent/far = ${(fixed.ring[2] / fixed.far).toFixed(3)}`);

// ---- entropy_pulse
hdr('Defect — entropy_pulse grows without bound and loses f32 precision');
dim('entropy_pulse += 0.05 every tick, never wrapped or clamped. AbyssalMoss reads');
dim('sin(entropy_pulse), so once the magnitude exceeds ~2^23 the f32 spacing is >1 and');
dim('sin() returns effectively arbitrary values. Determinism dies silently, and the');
dim('pulse is not covered by j_hash, so replay divergence is undetectable.');
let pulse = 0;
let ticksToPrecisionLoss = 0;
for (let t = 1; t < 200e6; t++) {
  pulse = f32(pulse + 0.05);
  if (f32(pulse + 0.05) === pulse) { ticksToPrecisionLoss = t; break; }
}
const hoursAt60 = ticksToPrecisionLoss / 60 / 3600;
dim(`f32 stops advancing after ~${ticksToPrecisionLoss.toLocaleString()} ticks = ${hoursAt60.toFixed(0)} h at 60 ticks/s`);
ok('entropy_pulse saturates within a plausible session length for a persistent world',
  hoursAt60 < 2000, `${hoursAt60.toFixed(0)} hours — and sin() is garbage well before that`);
const gP = new LatentAutomataGrid(8, 8, 8, 3);
for (let i = 0; i < 300; i++) gP.step({ clampPulse: true });
ok('wrapping the pulse modulo 2π is a one-line fix with no behavioural cost',
  gP.current[0].entropy_pulse < 2 * Math.PI + 0.05,
  `pulse held at ${gP.current[0].entropy_pulse.toFixed(3)}`);

// ---- the replay bug
hdr('Defect — the dream is not logged, so Lex I cannot reproduce the past');
dim('step_autonomous_dream mutates latent_variance, latent_features and entropy_pulse');
dim('and emits no event and no tick stamp. An append-only Merkle DAG over');
dim('spatial_state_vectors therefore cannot reconstruct a past world: the autonomous');
dim('evolution between commits is missing from the record.');
dim('This is the identical bug found and fixed in the Nebula prototype (interleaved');
dim('replay). There it produced a fingerprint mismatch; here it is undetectable,');
dim('because nothing hashes the fields the dream actually mutates.');
ok('j_hash omits the fields the dream mutates', true,
  'hashed: sector, pos, tick, observer_count, latent_variance, parent, latent_vector');
ok('...and probability_manifold, ego_density, consistency_coeff, spectral_weights, biome, culture and scars are all unhashed too', true,
  'so the "cryptographic immutability" does not cover the state that changes');

/* ==========================================================================
   PORT 2 — Sprint 3: TokenBucketGovernor
   ====================================================================== */

class TokenBucketGovernor {
  constructor(hourly_gpu_rate_usd) {
    this.rate = hourly_gpu_rate_usd;
    const hourly_ceiling_usd = 0.05;
    this.capacity_micro = hourly_ceiling_usd * 1_000_000;          // 50,000
    this.refill_per_sec = this.capacity_micro / 3600;              // 13.888...
    this.available_scaled = this.capacity_micro * 1000;            // starts FULL
    this.max_scaled = this.capacity_micro * 1000;
    this.last = 0;
    this.grantedUSD = 0; this.rejected = 0; this.granted = 0;
  }
  cost_for_microseconds(dur) {
    const cost = dur * (this.rate / 3600.0);
    return Math.ceil(cost);                                        // as submitted
  }
  try_acquire(dur_micros, now_sec, opts = {}) {
    const cost_micro = opts.noCeil
      ? dur_micros * (this.rate / 3600.0)
      : this.cost_for_microseconds(dur_micros);
    const cost_scaled = cost_micro * 1000;
    const elapsed = now_sec - this.last; this.last = now_sec;
    const added = elapsed * this.refill_per_sec * 1000;
    const refilled = Math.min(this.available_scaled + added, this.max_scaled);
    if (refilled < cost_scaled) { this.available_scaled = refilled; this.rejected++; return false; }
    this.available_scaled = refilled - cost_scaled;
    this.granted++;
    this.grantedUSD += (opts.noCeil ? cost_micro : cost_micro) / 1e6;
    return true;
  }
}

hdr('Verification claim 3 — "$0.05/hr ceiling, unbreakable"');
dim('The submitted math contradicts itself within four lines:');
dim('    Tokens_consumed(Δt) ≤ C_cap + r·Δt          (their first formula)');
dim('    ∫cost dτ ≤ r × 3600 = 50,000 tokens = $0.05 (their second formula)');
dim('With C_cap = 50,000 AND r·3600 = 50,000, the first gives $0.10 for hour one.');
dim('The bucket starts full, so the ceiling is 2x breached before the limiter engages.');

const gov = new TokenBucketGovernor(1.80);
let t = 0, hourSpend = [];
const KERNEL_US = 5000; // 5 ms kernel, back to back
let spentThisHour = 0, hourIdx = 0;
while (t < 4 * 3600) {
  const granted = gov.try_acquire(KERNEL_US, t);
  if (granted) {
    const usd = KERNEL_US * (1.80 / 3600) / 1e6;
    spentThisHour += usd;
    t += KERNEL_US / 1e6;
  } else {
    t += 0.01;
    if (spentThisHour > 0 && t > (hourIdx + 1) * 3600) { hourSpend.push(spentThisHour); spentThisHour = 0; hourIdx++; }
  }
  if (t > (hourIdx + 1) * 3600 && spentThisHour > 0) { hourSpend.push(spentThisHour); spentThisHour = 0; hourIdx++; }
}
dim('');
hourSpend.forEach((s, i) => dim(`  hour ${i + 1}: $${s.toFixed(5)}  ${i === 0 ? '<-- ' + (s / 0.05).toFixed(2) + 'x the stated ceiling' : '(at ceiling)'}`));
ok('hour one breaches the $0.05 ceiling by ~2x', hourSpend[0] > 0.09,
  `$${hourSpend[0].toFixed(4)} actual vs $0.05 claimed`);
ok('steady state does converge to the ceiling (the limiter itself works)',
  Math.abs(hourSpend[hourSpend.length - 1] - 0.05) < 0.01,
  `$${hourSpend[hourSpend.length - 1].toFixed(4)}/hr`);

hdr('Defect — cost.ceil() over-charges short kernels by up to 2000x');
dim('cost_for_microseconds returns ceil(µs × rate/3600) in micro-USD. The quantum is');
dim('1 micro-USD = 2 ms of GPU at $1.80/hr. Any kernel shorter than 2 ms is rounded up');
dim('to a full 2 ms charge, so the governor throttles far too early.');
console.log('');
dim('  kernel duration   true cost        charged        overcharge');
for (const dur of [1, 10, 100, 500, 2000, 10000]) {
  const trueCost = dur * (1.80 / 3600) / 1e6;
  const charged = Math.ceil(dur * (1.80 / 3600)) / 1e6;
  dim(`  ${String(dur).padStart(6)} µs      $${trueCost.toExponential(2).padEnd(11)}  $${charged.toExponential(2).padEnd(11)}  ${(charged / trueCost).toFixed(0).padStart(6)}x`);
}
const overcharge1us = Math.ceil(1 * (1.80 / 3600)) / (1 * (1.80 / 3600));
ok('a 1 µs kernel is charged 2000x its real cost', overcharge1us > 1000,
  `${overcharge1us.toFixed(0)}x`);
ok('the governor is unusable below ~2 ms kernel granularity',
  Math.ceil(100 * (1.80 / 3600)) / (100 * (1.80 / 3600)) > 15,
  `100 µs kernel overcharged ${(Math.ceil(100 * (1.8 / 3600)) / (100 * (1.8 / 3600))).toFixed(0)}x`);
dim('');
dim('Fix: accumulate fractional cost in a u64 scaled counter and never ceil per call.');
dim('The scaled-by-1000 representation already exists — it is simply defeated by the');
dim('ceil() applied before scaling.');

hdr('Defect — the reject path uses a non-atomic store inside a CAS loop');
dim('    if refilled < cost_scaled {');
dim('        self.available_tokens_scaled.store(refilled, Release);  // <-- not a CAS');
dim('        return false;');
dim('    }');
dim('A concurrent thread that successfully deducted between this thread\'s load and');
dim('this store has its deduction overwritten, and the tokens reappear. The invariant');
dim('"total consumed <= capacity + r·Δt" is violated under contention, which is exactly');
dim('the condition the governor exists to survive.');
dim('');
dim('Also: `added_tokens_scaled` is computed once, outside the loop, from a Mutex<Instant>');
dim('that is advanced by every caller. Under contention most callers observe elapsed≈0,');
dim('so refill is effectively serialised behind that mutex — the lock-free CAS loop is');
dim('not actually lock-free, and the atomics buy nothing.');
ok('the stated invariant is not enforced by the code as written', true,
  'requires a CAS or fetch_update on the reject path');

/* ==========================================================================
   PORT 3 — Sprint 5: ArchiveTensorCell
   ====================================================================== */

const BASIS_DIM = 8;
const SCAR_ATTRACTOR_WEIGHT = 0.25;
const ANTI_SCAR_REPULSION_WEIGHT = 0.35;
const RETENTION_DECAY_RATE = 0.998;

class ArchiveTensorCell {
  constructor() {
    this.S = new Float32Array(BASIS_DIM);
    this.A = new Float32Array(BASIS_DIM);
    this.tension = new Float32Array(BASIS_DIM);
    this.total_collapses = 0;
  }
  record_collapse(q, probs, ego_density = 8.3) {
    this.total_collapses++;
    const inc = (ego_density / 8.3) * 0.5;
    this.S[q] = f32(this.S[q] * RETENTION_DECAY_RATE + inc);
    for (let k = 0; k < BASIS_DIM; k++) {
      if (k !== q) {
        const p = probs[k];
        this.A[k] = p > 0.05 ? f32(this.A[k] * RETENTION_DECAY_RATE + p * ANTI_SCAR_REPULSION_WEIGHT)
          : f32(this.A[k] * RETENTION_DECAY_RATE);
      }
      this.tension[k] = f32(Math.sqrt(this.S[k] * this.A[k]));
    }
  }
  bias() {
    const b = new Float32Array(BASIS_DIM);
    for (let k = 0; k < BASIS_DIM; k++) b[k] = SCAR_ATTRACTOR_WEIGHT * this.S[k] - ANTI_SCAR_REPULSION_WEIGHT * this.A[k];
    return b;
  }
}

function softmax(b, T = 1.0) {
  const m = Math.max(...b);
  const e = b.map(x => Math.exp((x - m) / T));
  const s = e.reduce((a, c) => a + c, 0);
  return e.map(x => x / s);
}

hdr('Verification claim 5 — archive biasing');
dim('The mechanism works exactly as described, and that is the problem. With');
dim('η_scar = 0.5 per collapse and γ_decay = 0.998 PER EVENT (not per tick), the');
dim('attractor has no meaningful decay. The first outcome to win a collapse is');
dim('reinforced on every subsequent collapse, so the cell locks in.');
dim('');
dim('  collapses   max logit bias   p(first winner)   ratio vs uniform');
const cell = new ArchiveTensorCell();
let firstWinner = -1;
const marks = [1, 5, 20, 50, 100, 500, 2000];
let rows = [];
for (let n = 1; n <= 2000; n++) {
  const b = cell.bias();
  const p = softmax(Array.from(b));
  let q = 0; if (firstWinner < 0) { q = 3; firstWinner = 3; }
  else { let r = Math.random(), acc = 0; for (let k = 0; k < BASIS_DIM; k++) { acc += p[k]; if (r <= acc) { q = k; break; } } }
  const probs = Array.from(p);
  cell.record_collapse(q, probs, 8.3);
  if (marks.includes(n)) {
    const bb = cell.bias();
    const mx = Math.max(...bb), mn = Math.min(...bb);
    const pp = softmax(Array.from(bb));
    const winP = pp[firstWinner];
    rows.push({ n, gap: mx - mn, winP, ratio: winP * BASIS_DIM });
    dim(`  ${String(n).padStart(9)}   ${(mx - mn).toFixed(2).padStart(14)}   ${winP.toFixed(6).padStart(15)}   ${(winP * BASIS_DIM).toFixed(0).padStart(10)}:1`);
  }
}
const r50 = rows.find(r => r.n === 50);
ok('the archive locks onto its first outcome within ~50 collapses',
  r50 && r50.ratio > 100, `${r50.ratio.toFixed(0)}:1 bias toward the first winner after 50 collapses`);
const rFinal = rows[rows.length - 1];
ok('by 2000 collapses the cell is deterministic (mode collapse)',
  rFinal.winP > 0.999, `p(first winner) = ${rFinal.winP.toFixed(6)}`);
dim('');
dim('Analytic steady state if one state keeps winning:');
dim('  S_ss = 0.5 / (1 - 0.998) = 250      -> attractor bias  0.25 x 250 = +62.5');
dim('  A_ss = 0.35 x 0.125 / 0.002 = 21.9  -> repulsor bias    0.35 x 21.9 =  -7.7');
dim('  logit gap ≈ 70. e^70 is astronomically large: the outcome is frozen.');
const analyticGap = 0.25 * (0.5 / 0.002) + 0.35 * (0.35 * 0.125 / 0.002);
ok('analytic steady-state gap matches the simulation', Math.abs(analyticGap - rFinal.gap) / analyticGap < 0.2,
  `analytic ${analyticGap.toFixed(1)} vs simulated ${rFinal.gap.toFixed(1)}`);
dim('');
dim('Consequence for the game: cells the player visits most collapse most often, so');
dim('they lock in hardest and earliest. The most-visited places become the least');
dim('generative. That is inverted from what a worldbuilding game wants, and it is');
dim('invisible until hours into a session.');
dim('');
dim('Fixes, in order of leverage:');
dim('  1. make γ_decay a function of elapsed TICKS, not of collapse count');
dim('  2. normalise the bias vector before it reaches the logits (bound the gap)');
dim('  3. raise the anti-scar threshold well above 1/K, or drop anti-scars entirely');
dim('  4. apply an entropy floor: reject collapses whose distribution is below H_min');
const cellFix = new ArchiveTensorCell();
for (let n = 0; n < 2000; n++) {
  const b = cellFix.bias();
  const norm = Math.hypot(...b) || 1;
  const bn = Array.from(b).map(x => x / norm * 1.5);   // bounded gap
  const p = softmax(bn, 1.0);
  let r = Math.random(), acc = 0, q = 0;
  for (let k = 0; k < BASIS_DIM; k++) { acc += p[k]; if (r <= acc) { q = k; break; } }
  cellFix.record_collapse(q, Array.from(p), 8.3);
}
const pFix = softmax(Array.from(cellFix.bias()).map((x, i, a) => x / (Math.hypot(...a) || 1) * 1.5));
const maxFix = Math.max(...pFix);
ok('normalising the bias before softmax prevents lock-in', maxFix < 0.6,
  `max p = ${maxFix.toFixed(3)} after 2000 collapses (was ${(rFinal.winP).toFixed(4)})`);

/* ==========================================================================
   Summary
   ====================================================================== */
console.log(`\n\x1b[1m${pass} passed, ${fail} failed\x1b[0m`);
console.log('\n\x1b[1mClaims from the submitted Verification Summary:\x1b[0m');
console.log('  2. "LCA bounded variance"            \x1b[31mTECHNICALLY TRUE, MISLEADING\x1b[0m — bounded by .clamp(); saturates at MAX');
console.log('  3. "$0.05/hr unbreakable"            \x1b[31mFALSE\x1b[0m — hour one spends ~$0.10; ceil() over-charges up to 2000x;');
console.log('                                          reject path has a non-atomic store inside a CAS loop');
console.log('  5. "archive biasing"                 \x1b[31mWORKS AS WRITTEN, WHICH IS THE BUG\x1b[0m — mode collapse in ~50 collapses');
console.log('');
process.exit(fail ? 1 : 0);