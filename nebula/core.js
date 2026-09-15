/* ============================================================================
   PROJECT NEBULA — MLAOS Kernel (corrected architecture)
   ----------------------------------------------------------------------------
   Thesis under test:
     A deterministic SYMBOLIC kernel owns truth.
     A NEURAL materialization layer owns appearance.
     A HIERARCHICAL scheduler decides which one pays for a given decision.

   This file is dependency-free and runs identically in Node and the browser.
   It implements the five load-bearing claims of the corrected architecture:

     C1. Symbolic state as source of truth  -> idempotent, replayable, diffable
     C2. Composition, not vector averaging  -> coherent conflict resolution
     C3. Neural materializer as a CACHE     -> regenerable, never authoritative
     C4. Hierarchical inference             -> cheap micro, budgeted macro
     C5. Progressive refinement             -> latency hidden, not eliminated

   Plus the negative control: the naive "latent space as truth" design from the
   original roadmap, so the failure mode is visible rather than asserted.
   ============================================================================ */
(function (root) {
  'use strict';

  /* ==========================================================================
     0. Deterministic primitives
     ====================================================================== */

  // mulberry32 — tiny, fast, seedable. Determinism is a hard requirement:
  // any RNG here becomes part of the world's reproducibility contract.
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Spatially-coherent deterministic hash noise. Used as the neural
  // materializer's high-frequency conditioning input so detail is stable
  // across frames (no temporal shimmer) but varies per-location.
  function hash2(x, y, seed) {
    let h = Math.imul(x | 0, 374761393) ^ Math.imul(y | 0, 668265263) ^ Math.imul(seed | 0, 2147483647);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }

  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(t) { return t * t * (3 - 2 * t); }

  function makeValueNoise(seed) {
    const rng = mulberry32(seed);
    const P = 512;
    const perm = new Uint8Array(P * 2);
    const p = new Uint8Array(P);
    for (let i = 0; i < P; i++) p[i] = i;
    for (let i = P - 1; i > 0; i--) {
      const j = (rng() * (i + 1)) | 0;
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    for (let i = 0; i < P * 2; i++) perm[i] = p[i & (P - 1)];
    const grad = new Float32Array(P);
    for (let i = 0; i < P; i++) grad[i] = rng() * 2 - 1;

    return function (x, y) {
      const xi = Math.floor(x), yi = Math.floor(y);
      const xf = smooth(x - xi), yf = smooth(y - yi);
      const X = xi & (P - 1), Y = yi & (P - 1);
      const g00 = grad[perm[X + perm[Y]]];
      const g10 = grad[perm[X + 1 + perm[Y]]];
      const g01 = grad[perm[X + perm[Y + 1]]];
      const g11 = grad[perm[X + 1 + perm[Y + 1]]];
      const a = lerp(g00, g10, xf);
      const b = lerp(g01, g11, xf);
      return lerp(a, b, yf) * 0.5 + 0.5;
    };
  }

  function fbm(noise, x, y, octaves, lacunarity, gain) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let o = 0; o < octaves; o++) {
      sum += amp * noise(x * freq, y * freq);
      norm += amp;
      amp *= gain; freq *= lacunarity;
    }
    return sum / norm;
  }

  // FNV-1a over a Float32Array — gives us a cheap world fingerprint for the
  // replay/idempotency proof.
  function stateHash(f32) {
    let h = 0x811c9dc5;
    for (let i = 0; i < f32.length; i++) {
      const b = (f32[i] * 1000) | 0; // quantize; float equality is fragile
      h ^= b & 0xff; h = Math.imul(h, 0x01000193);
      h ^= (b >>> 8) & 0xff; h = Math.imul(h, 0x01000193);
      h ^= (b >>> 16) & 0xff; h = Math.imul(h, 0x01000193);
    }
    return (h >>> 0).toString(16).padStart(8, '0');
  }

  /* ==========================================================================
     1. Tiny neural net — the materializer
     --------------------------------------------------------------------------
     Deliberately minimal: 2 hidden layers, ReLU, Adam. This is a stand-in for
     the real thing (a SIREN / tiny NeRF / splat decoder running in WGSL).
     What matters architecturally is its POSITION in the system: it consumes
     symbolic features and produces appearance. It never produces state.
     ====================================================================== */

  class MLP {
    constructor(sizes, seed = 1) {
      this.sizes = sizes.slice();
      this.W = []; this.b = [];
      const rng = mulberry32(seed);
      for (let l = 0; l < sizes.length - 1; l++) {
        const nin = sizes[l], nout = sizes[l + 1];
        const std = Math.sqrt(2 / nin); // He init
        const w = new Float32Array(nin * nout);
        for (let i = 0; i < w.length; i++) w[i] = (rng() * 2 - 1) * std;
        this.W.push(w);
        this.b.push(new Float32Array(nout));
      }
      this.mW = this.W.map(w => new Float32Array(w.length));
      this.vW = this.W.map(w => new Float32Array(w.length));
      this.mb = this.b.map(b => new Float32Array(b.length));
      this.vb = this.b.map(b => new Float32Array(b.length));
      this.t = 0;
    }

    get paramCount() {
      let n = 0;
      for (const w of this.W) n += w.length;
      for (const b of this.b) n += b.length;
      return n;
    }

    // Forward pass. `out` is caller-supplied to avoid per-frame allocation —
    // at 60fps across thousands of cells, GC pressure is a real budget line.
    forward(input, out) {
      const L = this.W.length;
      let cur = input, nxt = out;
      const scratch = this._scratch || (this._scratch = []);
      for (let l = 0; l < L; l++) {
        const nin = this.sizes[l], nout = this.sizes[l + 1];
        const W = this.W[l], b = this.b[l];
        if (l === L - 1) {
          // output layer: linear
          for (let j = 0; j < nout; j++) {
            let s = b[j];
            for (let i = 0; i < nin; i++) s += cur[i] * W[i * nout + j];
            nxt[j] = s;
          }
        } else {
          let buf = scratch[l];
          if (!buf || buf.length < nout) { buf = new Float32Array(nout); scratch[l] = buf; }
          for (let j = 0; j < nout; j++) {
            let s = b[j];
            for (let i = 0; i < nin; i++) s += cur[i] * W[i * nout + j];
            buf[j] = s > 0 ? s : 0; // ReLU
          }
          nxt = buf;
        }
        cur = nxt;
      }
      return cur;
    }

    step(xs, ys, lr = 0.01) {
      // Plain SGD + Adam moments. Backprop written out explicitly: this net is
      // small enough that clarity beats generality.
      const L = this.W.length;
      const acts = [xs];
      let cur = xs;
      for (let l = 0; l < L; l++) {
        const nin = this.sizes[l], nout = this.sizes[l + 1];
        const W = this.W[l], b = this.b[l];
        const z = new Float32Array(nout), a = new Float32Array(nout);
        for (let j = 0; j < nout; j++) {
          let s = b[j];
          for (let i = 0; i < nin; i++) s += cur[i] * W[i * nout + j];
          z[j] = s;
          a[j] = (l === L - 1) ? s : (s > 0 ? s : 0);
        }
        acts.push(a);
        cur = a;
      }
      // output delta (MSE, linear output)
      const nOut = this.sizes[L];
      let delta = new Float32Array(nOut);
      let loss = 0;
      for (let j = 0; j < nOut; j++) {
        const e = cur[j] - ys[j];
        loss += e * e;
        delta[j] = e;
      }
      loss /= nOut;

      const b1 = 0.9, b2 = 0.999, eps = 1e-8;
      this.t++;
      const c1 = 1 - Math.pow(b1, this.t), c2 = 1 - Math.pow(b2, this.t);

      for (let l = L - 1; l >= 0; l--) {
        const nin = this.sizes[l], nout = this.sizes[l + 1];
        const W = this.W[l], b = this.b[l];
        const aPrev = acts[l];
        const mW = this.mW[l], vW = this.vW[l], mb = this.mb[l], vb = this.vb[l];
        const nextDelta = new Float32Array(nin);
        for (let j = 0; j < nout; j++) {
          const d = delta[j];
          // bias
          mb[j] = b1 * mb[j] + (1 - b1) * d;
          vb[j] = b2 * vb[j] + (1 - b2) * d * d;
          b[j] -= lr * (mb[j] / c1) / (Math.sqrt(vb[j] / c2) + eps);
          for (let i = 0; i < nin; i++) {
            const idx = i * nout + j;
            const g = d * aPrev[i];
            mW[idx] = b1 * mW[idx] + (1 - b1) * g;
            vW[idx] = b2 * vW[idx] + (1 - b2) * g * g;
            W[idx] -= lr * (mW[idx] / c1) / (Math.sqrt(vW[idx] / c2) + eps);
            nextDelta[i] += d * W[idx];
          }
        }
        if (l > 0) {
          // ReLU derivative on pre-activation of layer l-1's output (acts[l])
          for (let i = 0; i < nin; i++) nextDelta[i] *= acts[l][i] > 0 ? 1 : 0;
          delta = nextDelta;
        }
      }
      return loss;
    }
  }

  /* ==========================================================================
     2. Symbolic world state — the source of truth
     --------------------------------------------------------------------------
     Structured channels on a grid. Every mutation is an INTENT applied by a
     pure, idempotent function. This is the layer that answers "what is true",
     "who did it", "can we rewind", and "did two clients converge".
     ====================================================================== */

  const CH = { ELEV: 0, MOIST: 1, ROCK: 2, VEG: 3, STRUCT: 4, WATER: 5, N: 6 };
  const CH_NAMES = ['elev', 'moist', 'rock', 'veg', 'struct', 'water'];

  class World {
    constructor(w, h, seed = 1337) {
      this.w = w; this.h = h; this.seed = seed;
      this.ch = [];
      for (let i = 0; i < CH.N; i++) this.ch.push(new Float32Array(w * h));
      this.events = [];       // append-only intent log (event sourcing)
      this.applied = new Set(); // event ids — enforces idempotency
      this.settlements = [];
      this.nextEventId = 1;
      this.macroTick = 0;
      this.microTick = 0;
      this._gen(seed);
    }

    idx(x, y) { return y * this.w + x; }
    inBounds(x, y) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }

    _gen(seed) {
      const n1 = makeValueNoise(seed);
      const n2 = makeValueNoise(seed ^ 0x9e37);
      const n3 = makeValueNoise(seed ^ 0x5bf0);
      const { w, h } = this;
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const i = this.idx(x, y);
          const nx = x / w, ny = y / h;
          // island falloff so the world reads as a landmass
          const dx = (nx - 0.5) * 2, dy = (ny - 0.5) * 2;
          const d = Math.sqrt(dx * dx + dy * dy);
          const falloff = clamp(1 - Math.pow(d * 1.15, 3), 0, 1);

          let e = fbm(n1, nx * 5, ny * 5, 5, 2.0, 0.5);
          e = Math.pow(e, 1.4) * falloff;
          // a mountain ridge
          const ridge = Math.exp(-Math.pow((ny - 0.35 - 0.08 * Math.sin(nx * 6)) * 7, 2));
          e = clamp(e * 0.72 + ridge * 0.42 * falloff, 0, 1);
          this.ch[CH.ELEV][i] = e;

          const m = fbm(n2, nx * 3.5 + 11, ny * 3.5 + 7, 4, 2.0, 0.5);
          this.ch[CH.MOIST][i] = clamp(m * 0.7 + (1 - e) * 0.35, 0, 1);
          this.ch[CH.ROCK][i] = clamp(Math.pow(e, 2.2) * 1.2, 0, 1);
          this.ch[CH.WATER][i] = e < 0.30 ? clamp((0.30 - e) / 0.30, 0, 1) : 0;

          const v = fbm(n3, nx * 7 + 3, ny * 7 + 5, 3, 2.0, 0.5);
          const habitable = e > 0.32 && e < 0.78;
          this.ch[CH.VEG][i] = habitable ? clamp(v * this.ch[CH.MOIST][i] * 1.7, 0, 1) : 0;
          this.ch[CH.STRUCT][i] = 0;
        }
      }
    }

    // ---------------------------------------------------------------- intents

    /**
     * Apply an intent. Idempotent by event id, order-tolerant for spatially
     * disjoint brushes, and composable for overlapping ones.
     *
     * This is the function that replaces "consensus via vector averaging".
     * Composition is defined PER CHANNEL SEMANTIC, not per geometry:
     *   - terrain   : additive, then clamped        (mountain + valley = pass)
     *   - water     : max / carve                     (river cuts through ridge)
     *   - veg       : multiplicative survival         (fire * forest = clearing)
     *   - struct    : max with footprint exclusion    (no two buildings overlap)
     */
    apply(intent) {
      if (this.applied.has(intent.id)) return { duplicate: true };
      this.applied.add(intent.id);
      this.events.push(intent);
      const dirty = OPS[intent.op](this, intent);
      return { duplicate: false, dirty };
    }

    makeIntent(op, params) {
      return { id: this.nextEventId++, op, params, t: this.macroTick, actor: params.actor || 'player' };
    }

    /** Deterministic replay from the event log — the "save state" story. */
    static replay(events, w, h, seed) {
      const world = new World(w, h, seed);
      // Sort by id: replay order is canonical, not arrival order.
      const sorted = events.slice().sort((a, b) => a.id - b.id);
      for (const e of sorted) world.apply(e);
      return world;
    }

    fingerprint() {
      let h = 0x811c9dc5;
      for (let c = 0; c < CH.N; c++) h = (h ^ (hash32(stateHash(this.ch[c])))) >>> 0;
      return h.toString(16).padStart(8, '0');
    }

    // ------------------------------------------------------------- simulation

    /**
     * MICRO tier — every frame. Cheap, deterministic, conserves mass within
     * tolerance. This is symbolic physics; neural nets are not allowed here
     * because drift is unbounded and there is no ground truth to police.
     */
    microStep(dt) {
      this.microTick++;
      const { w, h } = this;
      const elev = this.ch[CH.ELEV], water = this.ch[CH.WATER];
      const sediment = this._sed || (this._sed = new Float32Array(w * h));
      sediment.fill(0);

      const K = 0.10 * dt;      // talus transport coefficient
      const DEP = 0.10 * dt;    // deposition
      for (let y = 1; y < h - 1; y++) {
        for (let x = 1; x < w - 1; x++) {
          const i = this.idx(x, y);
          const e = elev[i];
          if (water[i] > 0.5) continue; // underwater: no talus
          let lowest = e, li = -1;
          // 4-neighbourhood: cheaper and more stable than 8
          const n1 = i - 1, n2 = i + 1, n3 = i - w, n4 = i + w;
          if (elev[n1] < lowest) { lowest = elev[n1]; li = n1; }
          if (elev[n2] < lowest) { lowest = elev[n2]; li = n2; }
          if (elev[n3] < lowest) { lowest = elev[n3]; li = n3; }
          if (elev[n4] < lowest) { lowest = elev[n4]; li = n4; }
          if (li < 0) continue;
          const drop = (e - lowest);
          if (drop < 0.004) continue;           // angle of repose threshold
          const moved = drop * K * (0.5 + this.ch[CH.ROCK][i] * -0.3 + 0.3);
          sediment[i] -= moved;
          sediment[li] += moved * (1 - DEP);
        }
      }
      for (let i = 0; i < elev.length; i++) {
        if (sediment[i] !== 0) elev[i] = clamp(elev[i] + sediment[i], 0, 1);
      }

      // shallow water relaxation — spreads pooled water downhill
      const W = 0.06 * dt;
      for (let y = 1; y < h - 1; y++) {
        for (let x = 1; x < w - 1; x++) {
          const i = this.idx(x, y);
          if (water[i] <= 0.01) continue;
          const head = elev[i] + water[i] * 0.35;
          for (const j of [i - 1, i + 1, i - w, i + w]) {
            const oh = elev[j] + water[j] * 0.35;
            if (head > oh) {
              const f = Math.min(water[i] * W, (head - oh) * 0.25);
              water[i] -= f; water[j] += f;
            }
          }
        }
      }

      // vegetation dynamics: logistic growth gated by moisture/elevation/rock
      const veg = this.ch[CH.VEG], moist = this.ch[CH.MOIST];
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const i = this.idx(x, y);
          const e = elev[i];
          const habitable = e > 0.31 && e < 0.80 && water[i] < 0.4;
          if (!habitable) { veg[i] *= (1 - 0.02 * dt); continue; }
          const carry = clamp(moist[i] * 1.4 * (1 - this.ch[CH.ROCK][i] * 0.7), 0, 1);
          const growth = 0.035 * dt * veg[i] * (1 - veg[i] / Math.max(carry, 1e-3)) * (carry > 0 ? 1 : -1);
          veg[i] = clamp(veg[i] + growth, 0, 1);
        }
      }
    }

    /**
     * MACRO tier — infrequent, budgeted. This is where expensive model calls
     * are allowed. In production this is the LLM / policy network; here it is
     * a utility function so the demo stays deterministic and free.
     */
    macroStep(agents) {
      this.macroTick++;
      const out = [];
      for (const a of agents) out.push(...a.decide(this));
      return out;
    }
  }

  function hash32(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193); }
    return h >>> 0;
  }

  /* ==========================================================================
     3. Intent operators — the composition algebra
     ====================================================================== */

  function brushMask(world, cx, cy, r, falloff = 2) {
    const pts = [];
    const ri = Math.ceil(r);
    for (let y = cy - ri; y <= cy + ri; y++) {
      for (let x = cx - ri; x <= cx + ri; x++) {
        if (!world.inBounds(x, y)) continue;
        const d = Math.hypot(x - cx, y - cy) / r;
        if (d > 1) continue;
        pts.push({ i: world.idx(x, y), x, y, w: Math.pow(1 - d, falloff) });
      }
    }
    return pts;
  }

  function dirtyRect(world, mask, pad = 2) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (const p of mask) {
      if (p.x < x0) x0 = p.x; if (p.x > x1) x1 = p.x;
      if (p.y < y0) y0 = p.y; if (p.y > y1) y1 = p.y;
    }
    if (x1 < 0) return null;
    return {
      x0: Math.max(0, x0 - pad), y0: Math.max(0, y0 - pad),
      x1: Math.min(world.w - 1, x1 + pad), y1: Math.min(world.h - 1, y1 + pad)
    };
  }

  const OPS = {
    raise(world, it) {
      const { x, y, r, amount } = it.params;
      const mask = brushMask(world, x, y, r);
      for (const p of mask) {
        const e = world.ch[CH.ELEV][p.i];
        // additive then clamped: composition of two raises is a taller peak
        world.ch[CH.ELEV][p.i] = clamp(e + amount * p.w * (1 - e * 0.45), 0, 1);
        world.ch[CH.ROCK][p.i] = clamp(world.ch[CH.ROCK][p.i] + amount * p.w * 0.5, 0, 1);
      }
      return dirtyRect(world, mask);
    },

    lower(world, it) {
      const { x, y, r, amount } = it.params;
      const mask = brushMask(world, x, y, r);
      for (const p of mask) {
        world.ch[CH.ELEV][p.i] = clamp(world.ch[CH.ELEV][p.i] - amount * p.w, 0, 1);
        world.ch[CH.ROCK][p.i] = clamp(world.ch[CH.ROCK][p.i] - amount * p.w * 0.3, 0, 1);
      }
      return dirtyRect(world, mask);
    },

    /**
     * Carve a river. Note the composition rule: water uses `max` and elev uses
     * `min` against the bed profile. A river through a mountain therefore
     * yields a CANYON — the exact outcome the original roadmap wanted from
     * vector averaging, achieved deterministically and reproducibly.
     */
    carve(world, it) {
      const { x, y, r, depth, dir } = it.params;
      const mask = brushMask(world, x, y, r);
      const ang = (dir || 0) * Math.PI;
      for (const p of mask) {
        const along = (p.x - x) * Math.cos(ang) + (p.y - y) * Math.sin(ang);
        const bed = clamp(depth * p.w * (1 - Math.abs(along) / (r * 1.6)), 0, 1);
        world.ch[CH.ELEV][p.i] = Math.min(world.ch[CH.ELEV][p.i], Math.max(0.02, world.ch[CH.ELEV][p.i] - bed));
        world.ch[CH.WATER][p.i] = Math.max(world.ch[CH.WATER][p.i], bed > 0.05 ? clamp(bed * 2.2, 0, 1) : 0);
        world.ch[CH.VEG][p.i] *= (1 - bed * 0.8);
        world.ch[CH.MOIST][p.i] = clamp(world.ch[CH.MOIST][p.i] + bed * 0.5, 0, 1);
      }
      return dirtyRect(world, mask, 3);
    },

    /** Vegetation: multiplicative survival. Deforestation near water leaves a
     *  riparian buffer automatically because moisture raises regrowth carry. */
    deforest(world, it) {
      const { x, y, r, amount } = it.params;
      const mask = brushMask(world, x, y, r);
      let removed = 0;
      for (const p of mask) {
        const before = world.ch[CH.VEG][p.i];
        // riparian protection is a SYMBOLIC constraint, not a guardrail net
        const riparian = world.ch[CH.WATER][p.i] > 0.25 ? 0.35 : 1.0;
        world.ch[CH.VEG][p.i] = before * (1 - amount * p.w * riparian);
        removed += (before - world.ch[CH.VEG][p.i]);
      }
      it._removedVeg = removed;
      return dirtyRect(world, mask);
    },

    afforest(world, it) {
      const { x, y, r, amount } = it.params;
      const mask = brushMask(world, x, y, r);
      for (const p of mask) {
        const e = world.ch[CH.ELEV][p.i];
        if (e < 0.31 || e > 0.80 || world.ch[CH.WATER][p.i] > 0.4) continue;
        world.ch[CH.VEG][p.i] = clamp(world.ch[CH.VEG][p.i] + amount * p.w, 0, 1);
      }
      return dirtyRect(world, mask);
    },

    /** Structures: max-composition with footprint exclusion. Two builders in
     *  the same cell resolve by claim order (deterministic), not by blending. */
    build(world, it) {
      const { x, y, r, kind, actor } = it.params;
      const mask = brushMask(world, x, y, Math.max(1.5, r));
      for (const p of mask) {
        if (world.ch[CH.WATER][p.i] > 0.35) continue;
        world.ch[CH.STRUCT][p.i] = Math.max(world.ch[CH.STRUCT][p.i], clamp(0.55 + p.w * 0.45, 0, 1));
        world.ch[CH.VEG][p.i] *= (1 - 0.9 * p.w);
        world.ch[CH.ELEV][p.i] = clamp(world.ch[CH.ELEV][p.i] * (1 - 0.05 * p.w) + 0.02, 0, 1);
      }
      if (kind === 'settlement') {
        world.settlements.push({ x, y, r, owner: actor || 'player', born: world.macroTick, id: it.id });
      }
      return dirtyRect(world, mask);
    },

    /** The negotiation resolver's write primitive: restore a compromise state. */
    resolve(world, it) {
      const { ops } = it.params;
      let dirty = null;
      for (const sub of ops) {
        const d = OPS[sub.op](world, { params: sub.params, id: it.id + ':' + sub.op });
        if (d) dirty = dirty ? unionRect(dirty, d) : d;
      }
      return dirty;
    }
  };

  function unionRect(a, b) {
    return {
      x0: Math.min(a.x0, b.x0), y0: Math.min(a.y0, b.y0),
      x1: Math.max(a.x1, b.x1), y1: Math.max(a.y1, b.y1)
    };
  }

  /* ==========================================================================
     4. The negative control — "latent space as truth"
     --------------------------------------------------------------------------
     This is the original roadmap's §4.2 implemented faithfully, so its failure
     is demonstrated rather than asserted.

     Each intent maps to a fixed embedding. Overlap regions are resolved by
     averaging embeddings. A linear decoder projects embeddings back to world
     features. Watch what happens to (a) semantic coherence and (b) idempotency
     under event re-delivery.
     ====================================================================== */

  const EMBED_DIM = 24;

  // A crude but honest stand-in for "an encoder learned from data".
  // Each op gets a distinct direction in latent space.
  const OP_EMBED = {
    raise:    { elev: 1.0, rock: 0.8, water: -0.3, veg: -0.4 },
    lower:    { elev: -1.0, rock: -0.3, water: 0.5, veg: 0.2 },
    carve:    { elev: -0.6, rock: -0.2, water: 1.0, veg: -0.5 },
    deforest: { elev: 0.0, rock: 0.2, water: -0.2, veg: -1.0 },
    afforest: { elev: 0.0, rock: -0.3, water: 0.3, veg: 1.0 },
    build:    { elev: 0.2, rock: 0.6, water: -0.6, veg: -0.8, struct: 1.0 }
  };

  function embedIntent(intent) {
    const v = new Float32Array(EMBED_DIM);
    const src = OP_EMBED[intent.op] || {};
    const keys = ['elev', 'moist', 'rock', 'veg', 'struct', 'water'];
    const rng = mulberry32(hash32(intent.op) ^ 0x5eed);
    for (let d = 0; d < EMBED_DIM; d++) {
      let s = 0;
      for (let k = 0; k < keys.length; k++) s += (src[keys[k]] || 0) * basisFn(k, d);
      // every embedding also carries a little idiosyncratic noise, exactly as
      // real learned embeddings do. This is what makes averaging catastrophic.
      v[d] = s + (rng() - 0.5) * 0.55;
    }
    const n = Math.hypot(...v) || 1;
    for (let d = 0; d < EMBED_DIM; d++) v[d] /= n;
    return v;
  }

  function basisFn(k, d) {
    // fixed pseudo-random projection basis
    return Math.sin((k + 1) * 12.9898 + (d + 1) * 78.233) * 0.5;
  }

  class LatentWorld {
    /**
     * @param {boolean} average  true  = naive vector averaging (original design)
     *                            false = anchored / composed (mitigation)
     */
    constructor(w, h, seed = 1337, average = true) {
      this.w = w; this.h = h; this.average = average;
      this.latent = [];
      for (let d = 0; d < EMBED_DIM; d++) this.latent.push(new Float32Array(w * h));
      this.count = new Float32Array(w * h); // how many intents touched a cell
      this.ch = [];
      for (let i = 0; i < CH.N; i++) this.ch.push(new Float32Array(w * h));
      this.decoder = null; // fit by least squares against the symbolic world
      this.events = [];
      this.applied = new Set();
      this.nextEventId = 1;
      this.reDeliveryDrift = 0;
      this._gen(seed);
    }

    idx(x, y) { return y * this.w + x; }
    inBounds(x, y) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }

    _gen(seed) { /* seeded from the symbolic world's initial state at fit time */ }

    apply(intent) {
      const id = intent.id;
      const dup = this.applied.has(id);
      this.applied.add(id);
      this.events.push(intent);
      const v = embedIntent(intent);
      const mask = brushMask({ w: this.w, h: this.h, inBounds: (x, y) => this.inBounds(x, y), idx: (x, y) => this.idx(x, y) },
        intent.params.x, intent.params.y, intent.params.r || 3);
      for (const p of mask) {
        for (let d = 0; d < EMBED_DIM; d++) {
          if (this.average) {
            // running mean — THE bug: non-idempotent under re-delivery,
            // and off-manifold wherever two intents overlap.
            const n = this.count[p.i] || 0;
            this.latent[d][p.i] = (this.latent[d][p.i] * n + v[d] * p.w) / (n + p.w);
          } else {
            this.latent[d][p.i] += v[d] * p.w;
          }
        }
        this.count[p.i] += dup ? p.w : p.w; // duplicates still move the mean
        if (dup) this.reDeliveryDrift += 1;
      }
      return dirtyRect(this, mask);
    }

    /** Fit a linear decoder latent->features against ground truth. */
    fitDecoder(symbolicWorld, samples = 4000, seed = 7) {
      const rng = mulberry32(seed);
      const X = [], Y = [];
      for (let s = 0; s < samples; s++) {
        const i = (rng() * this.w * this.h) | 0;
        const x = new Float32Array(EMBED_DIM + 1);
        for (let d = 0; d < EMBED_DIM; d++) x[d] = this.latent[d][i];
        x[EMBED_DIM] = 1; // bias
        X.push(x);
        const y = new Float32Array(CH.N);
        for (let c = 0; c < CH.N; c++) y[c] = symbolicWorld.ch[c][i];
        Y.push(y);
      }
      this.decoder = leastSquares(X, Y, EMBED_DIM + 1, CH.N);
      return this.decodeError(X, Y);
    }

    decodeError(X, Y) {
      if (!this.decoder) return Infinity;
      let se = 0, n = 0;
      for (let s = 0; s < X.length; s++) {
        const pred = matVec(this.decoder, X[s], CH.N);
        for (let c = 0; c < CH.N; c++) { const e = pred[c] - Y[s][c]; se += e * e; n++; }
      }
      return Math.sqrt(se / n);
    }

    decodeToChannels() {
      if (!this.decoder) return this.ch;
      const x = new Float32Array(EMBED_DIM + 1);
      x[EMBED_DIM] = 1;
      for (let i = 0; i < this.w * this.h; i++) {
        for (let d = 0; d < EMBED_DIM; d++) x[d] = this.latent[d][i];
        const y = matVec(this.decoder, x, CH.N);
        for (let c = 0; c < CH.N; c++) this.ch[c][i] = clamp(y[c], 0, 1);
      }
      return this.ch;
    }

    /** How "mushy" is this world? Variance across cells, per channel.
     *  Averaging collapses variance -> low detail -> the Mush Problem. */
    mushScore() {
      let total = 0;
      for (let c = 0; c < CH.N; c++) {
        const arr = this.ch[c];
        let mean = 0;
        for (let i = 0; i < arr.length; i++) mean += arr[i];
        mean /= arr.length;
        let v = 0;
        for (let i = 0; i < arr.length; i++) { const d = arr[i] - mean; v += d * d; }
        total += Math.sqrt(v / arr.length);
      }
      return total / CH.N;
    }
  }

  function matVec(M, x, rows) {
    const out = new Float32Array(rows);
    for (let r = 0; r < rows; r++) {
      let s = 0;
      for (let c = 0; c < x.length; c++) s += M[r * x.length + c] * x[c];
      out[r] = s;
    }
    return out;
  }

  // Normal equations with Tikhonov regularization — ridge regression.
  // We regularize because the latent matrix is rank-deficient by construction:
  // this is itself a symptom of the design (24 dims cannot carry a world).
  function leastSquares(X, Y, dim, outDim, lambda = 0.8) {
    const A = new Float64Array(dim * dim);
    const B = new Float64Array(dim * outDim);
    for (let s = 0; s < X.length; s++) {
      const x = X[s], y = Y[s];
      for (let i = 0; i < dim; i++) {
        const xi = x[i];
        for (let j = 0; j < dim; j++) A[i * dim + j] += xi * x[j];
        for (let o = 0; o < outDim; o++) B[i * outDim + o] += xi * y[o];
      }
    }
    for (let i = 0; i < dim; i++) A[i * dim + i] += lambda;
    const Ainv = invert(A, dim);
    const M = new Float64Array(outDim * dim);
    for (let o = 0; o < outDim; o++) {
      for (let i = 0; i < dim; i++) {
        let s = 0;
        for (let j = 0; j < dim; j++) s += Ainv[i * dim + j] * B[j * outDim + o];
        M[o * dim + i] = s;
      }
    }
    return M;
  }

  function invert(A, n) {
    const M = new Float64Array(n * 2 * n);
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) M[i * 2 * n + j] = A[i * n + j];
      M[i * 2 * n + n + i] = 1;
    }
    for (let col = 0; col < n; col++) {
      let piv = col;
      for (let r = col + 1; r < n; r++) if (Math.abs(M[r * 2 * n + col]) > Math.abs(M[piv * 2 * n + col])) piv = r;
      if (piv !== col) for (let k = 0; k < 2 * n; k++) {
        const t = M[col * 2 * n + k]; M[col * 2 * n + k] = M[piv * 2 * n + k]; M[piv * 2 * n + k] = t;
      }
      const d = M[col * 2 * n + col] || 1e-12;
      for (let k = 0; k < 2 * n; k++) M[col * 2 * n + k] /= d;
      for (let r = 0; r < n; r++) {
        if (r === col) continue;
        const f = M[r * 2 * n + col];
        if (f === 0) continue;
        for (let k = 0; k < 2 * n; k++) M[r * 2 * n + k] -= f * M[col * 2 * n + k];
      }
    }
    const inv = new Float64Array(n * n);
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) inv[i * n + j] = M[i * 2 * n + n + j];
    return inv;
  }

  /* ==========================================================================
     5. Neural materializer — appearance as a cache
     --------------------------------------------------------------------------
     Trained ONCE against a curated target function (in production: against
     baked ground truth / reference renders). At runtime it is a pure function
     of symbolic features. It can be wrong, stale, or missing entirely and the
     world remains correct — that is the whole point of the split.
     ====================================================================== */

  const MAT_IN = 9;   // 6 channels + slope + aspect + hash noise
  const MAT_OUT = 4;  // r, g, b, micro-displacement

  // Curated target: a hand-authored biome ramp. In production this is your
  // art direction, expressed as reference renders. Either way it is SYMBOLIC
  // ground truth that the net approximates — not the net inventing the world.
  function biomeTarget(elev, moist, rock, veg, struct, water, slope, out) {
    let r, g, b, disp = 0;
    if (water > 0.35) {
      const d = clamp(water, 0, 1);
      r = lerp(70, 14, d); g = lerp(120, 46, d); b = lerp(160, 96, d);
      disp = -0.02 * d;
    } else if (elev > 0.80) {
      const t = clamp((elev - 0.80) / 0.20, 0, 1);
      r = lerp(148, 244, t); g = lerp(146, 248, t); b = lerp(150, 252, t);
    } else if (rock > 0.62 && veg < 0.25) {
      const t = clamp(rock, 0, 1);
      r = lerp(112, 150, t); g = lerp(108, 146, t); b = lerp(104, 142, t);
      disp = slope * 0.35;
    } else if (elev < 0.34) {
      r = 206; g = 190; b = 142; // shore / sand
    } else {
      // grassland -> forest by vegetation density
      const t = clamp(veg, 0, 1);
      const dry = clamp(1 - moist, 0, 1);
      r = lerp(lerp(122, 168, dry), 34, t);
      g = lerp(lerp(152, 150, dry), 88, t);
      b = lerp(lerp(78, 96, dry), 44, t);
      disp = t * 0.18;
    }
    if (struct > 0.25) {
      const t = clamp(struct, 0, 1);
      r = lerp(r, 214, t * 0.85); g = lerp(g, 196, t * 0.85); b = lerp(b, 168, t * 0.85);
      disp += t * 0.55;
    }
    out[0] = r / 255; out[1] = g / 255; out[2] = b / 255; out[3] = disp;
    return out;
  }

  class Materializer {
    constructor(seed = 42) {
      this.net = new MLP([MAT_IN, 40, 40, MAT_OUT], seed);
      this.trained = false;
      this.trainLoss = Infinity;
      this._in = new Float32Array(MAT_IN);
      this._out = new Float32Array(MAT_OUT);
    }

    /** Train against procedurally-sampled symbolic states. Bounded work:
     *  this is the OFFLINE BAKE cost, paid once, never at runtime. */
    train(world, steps = 2600, seed = 99) {
      const rng = mulberry32(seed);
      const tgt = new Float32Array(MAT_OUT);
      const xs = new Float32Array(MAT_IN);
      const ys = new Float32Array(MAT_OUT);
      // Sample both from the live world and from randomized feature space so
      // the net generalizes to states the player hasn't visited yet.
      let last = 0;
      for (let s = 0; s < steps; s++) {
        const batch = 24;
        let acc = 0;
        for (let k = 0; k < batch; k++) {
          let f;
          if (rng() < 0.55 && world) {
            const i = (rng() * world.w * world.h) | 0;
            f = featuresAt(world, i % world.w, (i / world.w) | 0, this._in);
          } else {
            f = this._in;
            f[0] = rng(); f[1] = rng(); f[2] = Math.pow(rng(), 2);
            f[3] = rng(); f[4] = Math.pow(rng(), 3); f[5] = Math.pow(rng(), 2);
            f[6] = rng() * 0.5; f[7] = rng() * 2 - 1; f[8] = rng();
          }
          biomeTarget(f[0], f[1], f[2], f[3], f[4], f[5], f[6], tgt);
          // target carries high-frequency detail the LUT cannot express;
          // this is what the neural pass BUYS you over a lookup table.
          const detail = (f[8] - 0.5) * 0.055;
          xs.set(f);
          ys[0] = clamp(tgt[0] + detail * 1.1, 0, 1);
          ys[1] = clamp(tgt[1] + detail, 0, 1);
          ys[2] = clamp(tgt[2] + detail * 0.9, 0, 1);
          ys[3] = tgt[3];
          acc += this.net.step(xs, ys, 0.012);
        }
        last = acc / batch;
      }
      this.trainLoss = last;
      this.trained = true;
      return last;
    }

    /** High-fidelity path. */
    decode(features, out) {
      return this.net.forward(features, out);
    }

    /** Low-fidelity path — NO network. This is what renders on frame 0 while
     *  the neural bake is still in flight. Instant, and never wrong enough to
     *  mislead: it is the same symbolic truth, just without learned detail. */
    decodeLoFi(features, out) {
      return biomeTarget(features[0], features[1], features[2], features[3],
        features[4], features[5], features[6], out);
    }
  }

  function featuresAt(world, x, y, out) {
    const i = world.idx(x, y);
    const elev = world.ch[CH.ELEV][i];
    let dx = 0, dy = 0;
    if (x > 0 && x < world.w - 1) dx = world.ch[CH.ELEV][i + 1] - world.ch[CH.ELEV][i - 1];
    if (y > 0 && y < world.h - 1) dy = world.ch[CH.ELEV][i + world.w] - world.ch[CH.ELEV][i - world.w];
    const slope = Math.min(1, Math.hypot(dx, dy) * 6);
    out[0] = elev;
    out[1] = world.ch[CH.MOIST][i];
    out[2] = world.ch[CH.ROCK][i];
    out[3] = world.ch[CH.VEG][i];
    out[4] = world.ch[CH.STRUCT][i];
    out[5] = world.ch[CH.WATER][i];
    out[6] = slope;
    out[7] = dx === 0 && dy === 0 ? 0 : Math.atan2(dy, dx) / Math.PI;
    out[8] = hash2(x, y, world.seed);
    return out;
  }

  /* ==========================================================================
     6. Progressive refinement — the latency story
     --------------------------------------------------------------------------
     The client never waits on generation. It renders lo-fi from symbolic truth
     IMMEDIATELY, then upgrades chunks as materialization completes. Fidelity
     arrives; responsiveness never leaves.
     ====================================================================== */

  class RefinementScheduler {
    constructor(world, chunkW, chunkH, opts = {}) {
      this.world = world;
      this.cw = chunkW; this.chh = chunkH;
      this.cols = Math.ceil(world.w / chunkW);
      this.rows = Math.ceil(world.h / chunkH);
      this.state = new Uint8Array(this.cols * this.rows); // 0=lofi 1=queued 2=hidim
      this.progress = new Float32Array(this.cols * this.rows);
      this.queue = [];
      // Simulated bake cost per chunk. In production this is a GPU job; the
      // number below is what makes the latency-hiding claim testable.
      this.bakeMsPerChunk = opts.bakeMsPerChunk ?? 90;
      this.msPerFrame = opts.msPerFrame ?? 16.7;
      this.stats = { bakes: 0, cacheHits: 0, cacheMisses: 0, bakeMsTotal: 0 };
    }

    cid(cx, cy) { return cy * this.cols + cx; }

    invalidate(rect) {
      if (!rect) return [];
      const cx0 = Math.floor(rect.x0 / this.cw), cx1 = Math.floor(rect.x1 / this.cw);
      const cy0 = Math.floor(rect.y0 / this.chh), cy1 = Math.floor(rect.y1 / this.chh);
      const touched = [];
      for (let cy = cy0; cy <= cy1; cy++) {
        for (let cx = cx0; cx <= cx1; cx++) {
          if (cx < 0 || cy < 0 || cx >= this.cols || cy >= this.rows) continue;
          const id = this.cid(cx, cy);
          if (this.state[id] === 2) this.stats.cacheMisses++;
          this.state[id] = 1;
          this.progress[id] = 0;
          if (!this.queue.includes(id)) this.queue.push(id);
          touched.push(id);
        }
      }
      return touched;
    }

    /** Advance simulated bake work by one frame's worth of budget. */
    tick(frameMs = this.msPerFrame) {
      let budget = frameMs * (this.parallelBakes || 2);
      const done = [];
      while (budget > 0 && this.queue.length) {
        const id = this.queue[0];
        const need = this.bakeMsPerChunk * (1 - this.progress[id]);
        const spend = Math.min(need, budget);
        this.progress[id] += spend / this.bakeMsPerChunk;
        budget -= spend;
        this.stats.bakeMsTotal += spend;
        if (this.progress[id] >= 1) {
          this.state[id] = 2;
          this.progress[id] = 1;
          this.queue.shift();
          this.stats.bakes++;
          done.push(id);
        }
      }
      return done;
    }

    /** Which fidelity does a given cell render at, right now? */
    fidelityAt(x, y) {
      const id = this.cid(Math.floor(x / this.cw), Math.floor(y / this.chh));
      if (this.state[id] === 2) { this.stats.cacheHits++; return 1; }
      return 0;
    }

    fractionHiFi() {
      let n = 0;
      for (let i = 0; i < this.state.length; i++) if (this.state[i] === 2) n++;
      return n / this.state.length;
    }
  }

  /* ==========================================================================
     7. Agents — macro tier only
     ====================================================================== */

  class SettlerAgent {
    constructor(id, opts = {}) {
      this.id = id;
      this.cooldown = opts.cooldown ?? 40;
      this.lastDecision = -1e9;
      this.rng = mulberry32(opts.seed ?? (id * 7919 + 13));
      this.utility = opts.utility ?? { water: 1.4, flat: 1.1, veg: 0.9, isolate: 0.7, avoidRock: 0.8 };
      this.log = [];
      this.tokenBudget = opts.tokenBudget ?? 64; // hard cap per macro decision
    }

    decide(world) {
      if (world.macroTick - this.lastDecision < this.cooldown) return [];
      this.lastDecision = world.macroTick;

      // sample candidate sites — cheap, bounded
      let best = null;
      for (let s = 0; s < 90; s++) {
        const x = 6 + ((this.rng() * (world.w - 12)) | 0);
        const y = 6 + ((this.rng() * (world.h - 12)) | 0);
        const score = this.scoreSite(world, x, y);
        if (!best || score.v > best.v) best = { x, y, v: score.v, why: score.why };
      }
      if (!best || best.v < 0.42) return [];

      const intent = world.makeIntent('build', {
        x: best.x, y: best.y, r: 2.4, kind: 'settlement', actor: 'agent:' + this.id
      });
      world.apply(intent);
      const ev = {
        tick: world.macroTick, actor: this.id, kind: 'FOUND_SETTLEMENT',
        x: best.x, y: best.y, score: +best.v.toFixed(3),
        rationale: best.why, tokens: Math.min(this.tokenBudget, 24 + ((best.v * 40) | 0))
      };
      this.log.push(ev);
      return [ev];
    }

    scoreSite(world, x, y) {
      const i = world.idx(x, y);
      const e = world.ch[CH.ELEV][i];
      if (e < 0.33 || e > 0.76 || world.ch[CH.WATER][i] > 0.3) return { v: -1, why: 'uninhabitable' };

      // water within radius
      let waterNear = 0, vegNear = 0, structNear = 0, slopeAcc = 0, n = 0;
      const R = 6;
      for (let dy = -R; dy <= R; dy++) {
        for (let dx = -R; dx <= R; dx++) {
          const xx = x + dx, yy = y + dy;
          if (!world.inBounds(xx, yy)) continue;
          const j = world.idx(xx, yy);
          const d = Math.hypot(dx, dy);
          if (d > R) continue;
          const w = 1 - d / R;
          waterNear += world.ch[CH.WATER][j] * w;
          vegNear += world.ch[CH.VEG][j] * w;
          structNear += world.ch[CH.STRUCT][j] * w;
          slopeAcc += Math.abs(world.ch[CH.ELEV][j] - e) * w;
          n += w;
        }
      }
      waterNear /= n; vegNear /= n; structNear /= n;
      const flat = 1 - clamp(slopeAcc / n * 12, 0, 1);
      const u = this.utility;
      const v = clamp(
        u.water * clamp(waterNear * 3.2, 0, 1) +
        u.flat * flat +
        u.veg * clamp(vegNear * 1.8, 0, 1) -
        u.isolate * clamp(structNear * 1.4, 0, 1) -
        u.avoidRock * world.ch[CH.ROCK][i], 0, 1) / 2.4;

      const why = [];
      if (waterNear > 0.12) why.push('fresh water');
      if (flat > 0.6) why.push('level ground');
      if (vegNear > 0.2) why.push('timber/forage');
      if (structNear > 0.2) why.push('crowded — penalized');
      return { v, why: why.join(', ') || 'marginal' };
    }
  }

  /**
   * The negotiation resolver.
   *
   * Conflict between player intent and agent intent is resolved by composing
   * SYMBOLIC operations — not by blending vectors. The output is a deterministic,
   * explainable compromise plus a narrative event the player can read.
   */
  class NegotiationResolver {
    constructor() { this.history = []; }

    /**
     * @param {World} world
     * @param {object} playerIntent  already-applied intent that caused harm
     * @returns {object|null} resolution event
     */
    resolve(world, playerIntent) {
      if (playerIntent.op !== 'deforest') return null;
      const { x, y, r } = playerIntent.params;

      // find affected settlements
      const affected = world.settlements.filter(s => Math.hypot(s.x - x, s.y - y) < r + s.r + 5);
      if (!affected.length) return null;

      const removed = playerIntent._removedVeg || 0;
      if (removed < 0.6) return null; // below the grievance threshold

      const s = affected[0];
      const grievance = clamp(removed / 6, 0, 1);

      // Compromise is a COMPOSITION of concrete operations:
      //   partial restoration + a riparian/green buffer + relocation pressure.
      const ops = [
        { op: 'afforest', params: { x, y, r: r * 0.55, amount: 0.35 + grievance * 0.45 } },
        { op: 'afforest', params: { x: s.x, y: s.y, r: s.r + 3, amount: 0.25 } }
      ];
      const compromise = world.makeIntent('resolve', { ops, actor: 'resolver' });
      const dirty = world.apply(compromise);

      const outcome =
        grievance > 0.72 ? 'PROTEST' :
        grievance > 0.40 ? 'COMPROMISE' : 'GRUMBLING';

      const ev = {
        tick: world.macroTick, kind: outcome,
        player: { x, y, r }, settlement: { x: s.x, y: s.y, owner: s.owner },
        grievance: +grievance.toFixed(3),
        text: this.narrate(outcome, grievance, s),
        opsApplied: ops.length,
        dirty
      };
      this.history.push(ev);
      return ev;
    }

    narrate(outcome, g, s) {
      const who = s.owner.startsWith('agent') ? 'the settlers' : 'the townsfolk';
      switch (outcome) {
        case 'PROTEST':
          return `${who} of the settlement at (${s.x},${s.y}) block your crews. ` +
                 `Grievance ${(g * 100) | 0}%. A green belt is replanted and your clearance is halved.`;
        case 'COMPROMISE':
          return `${who} petition you. Grievance ${(g * 100) | 0}%. ` +
                 `They accept the clearing in exchange for replanting near the water.`;
        default:
          return `${who} grumble about the felling (${(g * 100) | 0}% grievance) but let it stand.`;
      }
    }
  }

  /* ==========================================================================
     8. Cost model — because unit economics decide feasibility
     ====================================================================== */

  const PRICE = {
    // illustrative 2026 cloud pricing, USD
    gpuSecondA100: 2.5 / 3600,      // ~$2.50/hr
    cpuSecond: 0.05 / 3600,
    llmMacroCall: 0.0006,            // small model, budgeted output
    localInferenceSecond: 0.0        // runs on the player's device
  };

  class CostModel {
    constructor() { this.reset(); }
    reset() {
      this.bakes = 0; this.bakeSeconds = 0;
      this.macroCalls = 0; this.macroTokens = 0;
      this.microSeconds = 0; this.materializeSeconds = 0;
    }
    addBake(seconds) { this.bakes++; this.bakeSeconds += seconds; }
    addMacro(tokens) { this.macroCalls++; this.macroTokens += tokens; }
    addMicro(seconds) { this.microSeconds += seconds; }
    addMaterialize(seconds) { this.materializeSeconds += seconds; }

    /** Corrected architecture: bake is amortized over the lifetime of a chunk. */
    corrected(hourlyShardPlayers, chunkLifetimeHours = 24, chunksPerShard = 80) {
      const bakePerHour = (chunksPerShard / chunkLifetimeHours);
      const bakeCost = bakePerHour * this.bakeSecondsPerChunk * PRICE.gpuSecondA100;
      const macroCost = hourlyShardPlayers * 6 * PRICE.llmMacroCall * 3; // 3 macro decisions/hr/player
      const runtime = hourlyShardPlayers * PRICE.localInferenceSecond;
      const serverCpu = PRICE.cpuSecond * 3600 * 0.5;
      return { bakeCost, macroCost, runtime, serverCpu, total: bakeCost + macroCost + serverCpu };
    }

    /** Naive architecture: generate at runtime, per player, per interaction. */
    naive(hourlyShardPlayers, interactionsPerHour = 120) {
      const gen = hourlyShardPlayers * interactionsPerHour * this.bakeSecondsPerChunk * PRICE.gpuSecondA100;
      const macro = hourlyShardPlayers * 60 * PRICE.llmMacroCall * 6;
      const serverCpu = PRICE.cpuSecond * 3600 * 2;
      return { gen, macro, serverCpu, total: gen + macro + serverCpu };
    }
  }
  CostModel.prototype.bakeSecondsPerChunk = 6; // a 6s GPU bake per chunk

  /* ==========================================================================
     exports
     ====================================================================== */

  const NEBULA = {
    // primitives
    mulberry32, hash2, clamp, lerp, smooth, makeValueNoise, fbm, stateHash, hash32,
    // world
    World, CH, CH_NAMES, OPS, brushMask, dirtyRect, unionRect, featuresAt,
    // negative control
    LatentWorld, embedIntent, EMBED_DIM, OP_EMBED, leastSquares,
    // neural materialization
    MLP, Materializer, biomeTarget, MAT_IN, MAT_OUT,
    // scheduling
    RefinementScheduler,
    // agents
    SettlerAgent, NegotiationResolver,
    // economics
    CostModel, PRICE
  };

  root.NEBULA = NEBULA;
  if (typeof module !== 'undefined' && module.exports) module.exports = NEBULA;

})(typeof globalThis !== 'undefined' ? globalThis : this);