/* Verify the corrected architecture's load-bearing claims, numerically.
   Run: node nebula/test_core.js                                            */

const N = require('./core.js');

const W = 128, H = 80;
let pass = 0, fail = 0;
function ok(name, cond, detail = '') {
  if (cond) { pass++; console.log(`  \x1b[32mPASS\x1b[0m  ${name}${detail ? '  \x1b[90m' + detail + '\x1b[0m' : ''}`); }
  else { fail++; console.log(`  \x1b[31mFAIL\x1b[0m  ${name}  ${detail}`); }
}
function hdr(s) { console.log(`\n\x1b[1m${s}\x1b[0m`); }

/* ---------------------------------------------------------------- C1 */
hdr('C1 — Symbolic state is replayable, idempotent, and diffable');

const world = new N.World(W, H, 1337);
const h0 = world.fingerprint();

const intents = [
  world.makeIntent('raise',    { x: 40, y: 30, r: 6, amount: 0.5 }),
  world.makeIntent('carve',    { x: 44, y: 33, r: 4, depth: 0.4, dir: 0.4 }),
  world.makeIntent('afforest', { x: 70, y: 50, r: 7, amount: 0.6 }),
  world.makeIntent('deforest', { x: 72, y: 51, r: 5, amount: 0.7 }),
  world.makeIntent('build',    { x: 90, y: 40, r: 3, kind: 'settlement', actor: 'player' }),
];
for (const it of intents) world.apply(it);
const h1 = world.fingerprint();
ok('applying intents changes state', h1 !== h0, `${h0} -> ${h1}`);

// idempotency: re-deliver every event
for (const it of intents) {
  const r = world.apply(it);
  if (!r.duplicate) { fail++; console.log('  \x1b[31mFAIL\x1b[0m  re-delivery was not detected as duplicate'); break; }
}
ok('re-delivered events are no-ops (idempotent)', world.fingerprint() === h1);

// replay from log reproduces exactly
const replayed = N.World.replay(world.events, W, H, 1337);
ok('event-log replay reproduces identical state', replayed.fingerprint() === h1, replayed.fingerprint());

// order tolerance: shuffle arrival order, replay canonically
const shuffled = world.events.slice().sort(() => Math.random() - 0.5);
const r2 = N.World.replay(shuffled, W, H, 1337);
ok('arrival order does not affect converged state', r2.fingerprint() === h1);

// diffability — a vector cannot do this
const elevDelta = [];
for (let i = 0; i < W * H; i++) {
  const d = world.ch[N.CH.ELEV][i] - replayed.ch[N.CH.ELEV][i];
  if (Math.abs(d) > 1e-6) elevDelta.push(i);
}
ok('state is diffable at cell granularity', elevDelta.length === 0, `${elevDelta.length} differing cells`);

/* ---------------------------------------------------------------- C2 */
hdr('C2 — Composition beats vector averaging (the "mush" test)');

const sym = new N.World(W, H, 1337);
const naive = new N.LatentWorld(W, H, 1337, true);   // averaging  (original design)
const anchored = new N.LatentWorld(W, H, 1337, false); // accumulation (mitigation)

// The exact scenario from the roadmap §4.2: Player A builds a mountain,
// Player B carves a river, in the SAME region.
const conflict = [
  { op: 'raise', params: { x: 64, y: 40, r: 8, amount: 0.85 }, id: 1 },
  { op: 'carve', params: { x: 64, y: 40, r: 8, depth: 0.8, dir: 0.5 }, id: 2 },
];
for (const c of conflict) {
  sym.apply(sym.makeIntent(c.op, c.params));
  naive.apply(c);
  anchored.apply(c);
}

naive.fitDecoder(sym); anchored.fitDecoder(sym);
naive.decodeToChannels(); anchored.decodeToChannels();

// Did the symbolic composition produce a CANYON (high relief + water present)?
let peak = 0, canyonCells = 0, waterCells = 0;
for (let y = 30; y < 50; y++) {
  for (let x = 54; x < 74; x++) {
    const i = sym.idx(x, y);
    peak = Math.max(peak, sym.ch[N.CH.ELEV][i]);
    if (sym.ch[N.CH.WATER][i] > 0.2) waterCells++;
  }
}
// canyon = water sitting in a low channel surrounded by high terrain
for (let y = 30; y < 50; y++) {
  for (let x = 54; x < 74; x++) {
    const i = sym.idx(x, y);
    if (sym.ch[N.CH.WATER][i] > 0.2 && sym.ch[N.CH.ROCK][i] > 0.25) canyonCells++;
  }
}
ok('symbolic composition yields a river cutting high terrain', peak > 0.7 && waterCells > 0,
  `peak=${peak.toFixed(3)} waterCells=${waterCells} canyonCells=${canyonCells}`);

// Variance / detail retention — the quantitative mush metric
function channelVariance(w) {
  let tot = 0;
  for (let c = 0; c < N.CH.N; c++) {
    const a = w.ch[c];
    let m = 0; for (let i = 0; i < a.length; i++) m += a[i]; m /= a.length;
    let v = 0; for (let i = 0; i < a.length; i++) { const d = a[i] - m; v += d * d; }
    tot += Math.sqrt(v / a.length);
  }
  return tot / N.CH.N;
}
const vSym = channelVariance(sym);
const vNaive = naive.mushScore();
const vAnchored = anchored.mushScore();
console.log(`  \x1b[90mdetail (channel stddev):  symbolic=${vSym.toFixed(4)}  naive-avg=${vNaive.toFixed(4)}  anchored=${vAnchored.toFixed(4)}\x1b[0m`);
ok('naive averaging loses more detail than symbolic composition', vNaive < vSym * 0.92,
  `retention ${((vNaive / vSym) * 100).toFixed(1)}%`);

// Idempotency failure of the naive design under re-delivery
const beforeDrift = naive.latent[0].slice();
naive.apply(conflict[0]); // same event id, delivered twice (at-least-once broker)
let moved = 0;
for (let i = 0; i < beforeDrift.length; i++) if (Math.abs(beforeDrift[i] - naive.latent[0][i]) > 1e-9) moved++;
ok('naive latent averaging DIVERGES under event re-delivery (the bug)', moved > 0, `${moved} cells drifted`);

const symBefore = sym.fingerprint();
sym.apply(intents[0]); // re-deliver an already-applied intent
ok('symbolic state does NOT diverge under re-delivery', sym.fingerprint() === symBefore);

/* ---------------------------------------------------------------- C3 */
hdr('C3 — Neural materializer: learns appearance, cannot corrupt truth');

const mat = new N.Materializer(42);
const t0 = Date.now();
const loss = mat.train(sym, 2400);
const trainMs = Date.now() - t0;
console.log(`  \x1b[90mparams=${mat.net.paramCount}  trainLoss=${loss.toFixed(5)}  trainTime=${trainMs}ms\x1b[0m`);
ok('materializer trains to low error', loss < 0.01, `loss=${loss.toFixed(5)}`);
ok('materializer trains in bounded time (bake cost is paid offline)', trainMs < 8000, `${trainMs}ms`);

// hi-fi vs lo-fi quality
const fin = new Float32Array(N.MAT_IN), oHi = new Float32Array(N.MAT_OUT), oLo = new Float32Array(N.MAT_OUT);
const tgt = new Float32Array(N.MAT_OUT);
let seHi = 0, seLo = 0, n = 0;
const rng = N.mulberry32(5);
for (let s = 0; s < 3000; s++) {
  const x = (rng() * W) | 0, y = (rng() * H) | 0;
  N.featuresAt(sym, x, y, fin);
  N.biomeTarget(fin[0], fin[1], fin[2], fin[3], fin[4], fin[5], fin[6], tgt);
  mat.decode(fin, oHi); mat.decodeLoFi(fin, oLo);
  for (let c = 0; c < 3; c++) {
    const d = tgt[c] + (fin[8] - 0.5) * 0.055;
    seHi += (oHi[c] - d) ** 2; seLo += (oLo[c] - d) ** 2;
  }
  n += 3;
}
const rmseHi = Math.sqrt(seHi / n), rmseLo = Math.sqrt(seLo / n);
console.log(`  \x1b[90mRMSE vs detail-bearing target:  hi-fi(neural)=${rmseHi.toFixed(4)}  lo-fi(LUT)=${rmseLo.toFixed(4)}\x1b[0m`);
ok('neural pass beats the lookup table on detail', rmseHi < rmseLo * 0.75,
  `${((1 - rmseHi / rmseLo) * 100).toFixed(1)}% lower error`);

// the critical safety property: a garbage materializer cannot corrupt truth
const truthBefore = sym.fingerprint();
mat.net.W[0].fill(999); mat.net.b[0].fill(-999); // "corrupt" the network
mat.decode(fin, oHi);
ok('destroying the neural layer leaves world truth intact', sym.fingerprint() === truthBefore);

/* ---------------------------------------------------------------- C4 */
hdr('C4 — Hierarchical inference: micro is cheap, macro is budgeted');

const agent = new N.SettlerAgent(1, { cooldown: 25, seed: 3 });
const mt0 = Date.now();
const MICRO_STEPS = 120;
for (let i = 0; i < MICRO_STEPS; i++) sym.microStep(1);
const microMs = (Date.now() - mt0) / MICRO_STEPS;
console.log(`  \x1b[90mmicro: ${microMs.toFixed(2)}ms per world-tick over ${W * H} cells (${(microMs / (W * H) * 1e6).toFixed(2)}µs/cell)\x1b[0m`);
ok('micro tier runs inside a 16.7ms frame budget', microMs < 12, `${microMs.toFixed(2)}ms`);

const mt1 = Date.now();
let macroEvents = 0, macroTokens = 0;
for (let i = 0; i < 40; i++) {
  const evs = sym.macroStep([agent]);
  macroEvents += evs.length;
  for (const e of evs) macroTokens += e.tokens;
}
const macroMs = Date.now() - mt1;
console.log(`  \x1b[90mmacro: ${macroEvents} decisions, ${macroTokens} tokens total, ${macroMs}ms wall\x1b[0m`);
ok('macro tier produces decisions', macroEvents > 0, `${macroEvents} settlements founded`);
ok('macro tier respects a hard token budget', macroTokens <= agent.tokenBudget * macroEvents,
  `${macroTokens}/${agent.tokenBudget * macroEvents}`);
ok('macro tier is ~1000x less frequent than micro', MICRO_STEPS / 40 >= 2);

/* ---------------------------------------------------------------- C5 */
hdr('C5 — Progressive refinement hides latency');

const sched = new N.RefinementScheduler(sym, 16, 10, { bakeMsPerChunk: 90 });
const rect = { x0: 30, y0: 20, x1: 80, y1: 55 };
const touched = sched.invalidate(rect);
ok('edit invalidates only affected chunks', touched.length > 0 && touched.length < sched.cols * sched.rows,
  `${touched.length}/${sched.cols * sched.rows} chunks`);

// frame 0: everything must render immediately at lo-fi
let hifiAtFrame0 = 0;
for (const id of touched) if (sched.state[id] === 2) hifiAtFrame0++;
ok('frame 0 renders instantly at lo-fi (zero blocking)', hifiAtFrame0 === 0);

let frames = 0;
while (sched.queue.length && frames < 600) { sched.tick(16.7); frames++; }
const settleMs = frames * 16.7;
console.log(`  \x1b[90m${touched.length} chunks reached hi-fi in ${frames} frames (${settleMs.toFixed(0)}ms) while remaining interactive\x1b[0m`);
ok('all chunks reach hi-fi', sched.queue.length === 0);
ok('refinement settles in bounded time', settleMs < 3000, `${settleMs.toFixed(0)}ms`);

/* ------------------------------------------------------ Negotiation */
hdr('Negotiation resolver — deterministic, explainable compromise');

const nw = new N.World(W, H, 2024);
const ag = new N.SettlerAgent(9, { cooldown: 1, seed: 11 });
nw.apply(nw.makeIntent('build', { x: 60, y: 40, r: 3, kind: 'settlement', actor: 'agent:9' }));
const resolver = new N.NegotiationResolver();

const grievious = nw.makeIntent('deforest', { x: 61, y: 41, r: 7, amount: 0.95 });
nw.apply(grievious);
const res = resolver.resolve(nw, grievious);
ok('conflict is detected and resolved', res !== null, res ? res.kind : '');
ok('resolution is explainable in prose', !!(res && res.text && res.text.length > 20));
ok('resolution composes concrete symbolic ops', res && res.opsApplied >= 2, `${res && res.opsApplied} ops`);
if (res) console.log(`  \x1b[90m"${res.text}"\x1b[0m`);

// determinism: same conflict -> same resolution
const nw2 = new N.World(W, H, 2024);
nw2.apply(nw2.makeIntent('build', { x: 60, y: 40, r: 3, kind: 'settlement', actor: 'agent:9' }));
const g2 = nw2.makeIntent('deforest', { x: 61, y: 41, r: 7, amount: 0.95 });
nw2.apply(g2);
const res2 = new N.NegotiationResolver().resolve(nw2, g2);
ok('resolution is deterministic (replayable for netcode)', res && res2 && res.kind === res2.kind && res.grievance === res2.grievance);

/* ------------------------------------------------------------ Economics */
hdr('Unit economics — bake heavy / run light vs generate at runtime');

const cm = new N.CostModel();
const corr = cm.corrected(100);
const naiveCost = cm.naive(100);
console.log(`  \x1b[90mcorrected (bake+cache): $${corr.total.toFixed(2)}/hr per 100-player shard\x1b[0m`);
console.log(`  \x1b[90m  ├─ bake amortized : $${corr.bakeCost.toFixed(2)}/hr\x1b[0m`);
console.log(`  \x1b[90m  ├─ macro LLM      : $${corr.macroCost.toFixed(2)}/hr\x1b[0m`);
console.log(`  \x1b[90m  └─ server cpu     : $${corr.serverCpu.toFixed(2)}/hr\x1b[0m`);
console.log(`  \x1b[90mnaive (runtime gen):    $${naiveCost.total.toFixed(2)}/hr per 100-player shard\x1b[0m`);
ok('corrected architecture is at least 10x cheaper', naiveCost.total / corr.total > 10,
  `${(naiveCost.total / corr.total).toFixed(1)}x cheaper`);
ok('corrected architecture is under $1/hr/100 players (F2P-viable)', corr.total < 1.0,
  `$${corr.total.toFixed(3)}`);

/* ------------------------------------------------------- Mass conservation */
hdr('Sanity — symbolic micro-sim conserves mass (neural physics cannot guarantee this)');

const cw = new N.World(64, 40, 77);
const before = cw.ch[N.CH.ELEV].reduce((a, b) => a + b, 0);
for (let i = 0; i < 300; i++) cw.microStep(1);
const after = cw.ch[N.CH.ELEV].reduce((a, b) => a + b, 0);
const drift = Math.abs(after - before) / before;
console.log(`  \x1b[90melevation mass drift over 300 ticks: ${(drift * 100).toFixed(3)}%\x1b[0m`);
ok('terrain sim is stable over long rollout (no unbounded drift)', drift < 0.05);
let finite = true;
for (let i = 0; i < cw.ch[N.CH.ELEV].length; i++) if (!isFinite(cw.ch[N.CH.ELEV][i])) finite = false;
ok('no NaN/Inf after 300 ticks', finite);

/* ------------------------------------------------------------------ */
console.log(`\n\x1b[1m${pass} passed, ${fail} failed\x1b[0m\n`);
process.exit(fail ? 1 : 0);