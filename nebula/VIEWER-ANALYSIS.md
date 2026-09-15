# Viewer analysis — character, lighting, shading, sun, moon

Covers `nebula-viewer.html` (built 11:21, unlit) and `nebula-viewer-lit.html`
(= `(1)`, built 11:42, lit). `(2)` was byte-identical to `(1)` and is dropped.

## 0. The project is missing most of its source tree

The HTML files are **build outputs**. Everything that produces them is absent:

| Referenced by | File | Status |
|---|---|---|
| `build.js` inlines it | `core.js` | recovered from the standalone bundle |
| viewer header comment | `build.js` | **missing** — no way to rebuild faithfully |
| viewer header comment | `splat_emit.js` | **missing** — inlined into the viewer |
| viewer header comment | `inline.js` | **missing** — inlined into `demo.html` |
| camera comment: "Verified by cam_test.js (14 assertions)" | `cam_test.js` | **missing** |
| `sprint_review.js` ports it | the submitted **Rust/CUDA** (`*.cu`) | **missing** — the audit cannot be re-run against source |
| viewer UI | `bake_production.splat`, `nebula_chunk.splat` | **missing** |

I can rebuild a standalone bundle by mimicking what `build.js` did (concatenate
`core.js` + the app inline script), but it will not be byte-identical to yours.
**If you can drop in the real `core.js`, `build.js`, `splat_emit.js` and
`cam_test.js`, everything downstream gets materially safer.**

## 1. What each viewer actually does

Both are the same three-part bundle: `core.js` (inlined) + `splat_emit.js`
(inlined) + viewer app. They differ only in the app + shader + emit signature.

| | `nebula-viewer.html` (11:21) | `nebula-viewer-lit.html` (11:42) |
|---|---|---|
| Primitive | instanced quad, `TRIANGLE_STRIP` ×4 | **`gl.POINTS`** |
| Instance attribs | center, scale, color, radius | center, color, radius, **normal** |
| Lighting | none | Lambert, `u_ambient + (1-u_ambient)·ndl·1.25` |
| Sun | — | azim 0–360, elev 5–85, ambient 10–80 |
| Moon / night / time-of-day | — | **absent** |
| Relief (heightScale) slider | — | yes, wired through `HM = HEIGHT_METRES·heightScale` |
| Normals baked at emission | — | yes: terrain from the heightfield gradient, canopy yawed, water `(0,1,0)` |

`(1)` strictly supersedes base **except** for the primitive: it traded oriented
quads for point sprites in order to get normals in cheaply.

## 2. Findings

### 2.1 Neither viewer renders anisotropic gaussians — `rot` and `scale` are dead payload

`emit()` computes real 3D gaussian geometry:
```js
scale.push(flat, flat * (1 + slope * 1.4), 0.14 + slope * 0.10);   // anisotropic
rot.push(Math.cos(a*0.5), 0, Math.sin(a*0.5), 0);                 // yaw quaternion
```
and packs both into the 32-byte `.splat` wire format. Then:

- **base** uploads `scaleArr` but the VS declares `a_scale` and *never reads it*;
  the quad is sized by `a_radius` alone, which is
  `max(scale.x, scale.z) * 1.6` — a bounding circle.
- **lit** declares `let scaleArr=null;` and never assigns it. Dead variable.
  Point sprites cannot be anisotropic at all.

So every splat is drawn as an isotropic disc, and the slope-dependent flattening
that stops the surface showing gaps between samples is discarded. That is a real
part of why terrain reads as paint: isotropic discs on a slope leave scalloped
gaps, and no amount of lighting fixes the silhouette.

The proper fix is the standard 3DGS screen-space projection — build
`Σ = R S Sᵀ Rᵀ`, project `Σ' = J W Σ Wᵀ Jᵀ`, eigendecompose the 2×2, and orient
the quad by the eigenvectors. ~30 lines of GLSL and it uses the data already
being emitted.

### 2.2 `applyStyle` claims to mirror `styledTarget` and does not — it drops grain and relief

```js
// mirror core.js styledTarget so the viewer matches the tested materializer
let R=r+warm*0.20, G=g2+cool*0.06, B=b-warm*0.10+cool*0.18;
const tint=1.0+(grain-0.25)*0.18;   // <-- a flat global multiply
```
core.js:
```js
const n = (hash - 0.5) * (0.05 + grain * 0.16);
out[0] = clamp(out[0] + warm*0.20 + n*1.15, 0, 1);
out[1] = clamp(out[1] + cool*0.06 + n*0.85, 0, 1);
out[2] = clamp(out[2] - warm*0.10 + cool*0.18 + n*0.95, 0, 1);
out[3] = out[3] + relief*0.30*(f[6]-0.3);   // micro-displacement
```
Three divergences:

1. **`n` is missing entirely.** It is a *per-cell hash* term — `hash = f[8] =
   hash2(x,y,seed)`. `applyStyle` replaces it with a uniform tint, so it modulates
   overall brightness instead of adding per-cell variation. `n` has amplitude up to
   `±(0.5·(0.05+0.16)·1.15) ≈ ±0.12` on red — comparable to the whole warm shift.
   **This is the single largest missing source of visual detail**, and per-cell
   variation is exactly what separates "terrain" from "paint". `relief` (style[3])
   is read and then unused.
2. **`applyStyle` cannot access `f[8]` anyway.** It is handed `(r, g, b, kind)`
   only, so the grain term is unreachable at render time as the pipeline is shaped.
3. **Clamping differs** — core clamps to `[0,1]`, the viewer clamps after the tint,
   so saturated biomes diverge.

### 2.3 The neural materializer is not in the viewer's path at all

`emit()` calls `N.biomeTarget(...)` — the analytic LUT — then `applyStyle` tints
it. `Materializer`, `styledTarget`, `styleNet` and the whole two-tower decoder are
bypassed. The viewer therefore renders the **lo-fi path permanently**, and the
"Regional weights" panel is a hand-written approximation of a network that was
trained to do this job properly.

That is the architectural claim (C3: *neural materializer as the appearance cache*)
not being exercised by the one artifact that shows appearance. It also means the
C3 failure in `test_core.js` is currently invisible in the viewer — the viewer
looks the same whether the network works or not.

Wiring it correctly is cheap: build a colour LUT by running `mat.decode()` over a
quantised feature grid **once per style change**, then have `emit()` sample that.
Keeps emission O(cells) and deterministic, keeps lo-fi (`decodeLoFi`) as the
frame-0 path, and makes the neural/analytic difference something you can see.

### 2.4 The `.splat` format cannot carry normals, so shading is lost on round-trip

`bytes = n * 32` is the antimatter15/splat layout: `pos 12 + scale 12 + rgba 4 +
rot 4`. `normal` is an extra array outside the wire format. So
**download → load** returns an unlit-looking world: `fillFromSplat` falls back to
`(0,1,0)` when `g.normal` is absent, and every gaussian shades as flat ground.
The UI says "Rendering path is identical, so you are comparing apples to apples" —
for a loaded file that is not true.

Options: derive normals at load time from the heightfield (only valid for
terrain-kind splats), or ship a sidecar `.normals`, or move to a 44-byte custom
layout and stop calling it `.splat`.

### 2.5 Sun is a direction, not a celestial body

`u_sun` is a unit vector from azim/elev. There is no disc, no sky, no colour
temperature shift with elevation, no horizon reddening, and no exposure
adaptation. At `elev=5` the world is lit by a low warm sun that still looks like
noon.

### 2.6 No moon, no night

Nothing in any file. There is no second light, no time parameter, no sky model,
and no night-time ambient floor. This is unbuilt work rather than a regression.

## 3. What "character building" maps to

There is no character/actor system in the viewer. The nearest thing is the
**regional character code**: `STYLE_DIM = 4` (`const STYLE_DIM = 4; // regional
"character" code`), five presets — `vanilla, arid, boreal, neon, monochrome` —
the `styleNet` tower, and the "Regional weights §6.2" panel.

So character = the 4-D style conditioning, and per §2.2/§2.3 the viewer currently
applies a **lossy hand-written version of it while ignoring the network trained to
do it**. If you meant characters-as-in-actors (settlers, agents), then
`SettlerAgent` and `NegotiationResolver` exist in core and the viewer calls
`world.macroStep([agent])` 12 times during `rebuild()` — but nothing visual is
ever emitted for them: no settlement sprites beyond `kind=3` terrain tint, no
agent bodies, no visible protest resolution.

## 4. Combine plan

Take `nebula-viewer-lit.html` as the base — it has the normals, the sun, the
relief slider, the UI and the verified camera — and port in what base does better,
then add the missing pieces:

1. **Rendering**: restore oriented quads and implement real covariance projection
   (§2.1) so `rot`/`scale` are finally used. Keep the point-sprite mode as a
   debug toggle.
2. **Lighting**: keep Lambert; add a **moon** — second direction, cool tint, much
   lower intensity — plus a **time-of-day** scrub that drives both, with sun and
   moon on opposing elevations, horizon colour ramp, and a night ambient floor.
3. **Character**: route appearance through `styledTarget`/`Materializer.decode`
   with the grain and relief terms intact (§2.2, §2.3), via a per-style LUT. Add a
   neural↔analytic A/B toggle so the C3 gap is visible.
4. **Artifacts**: make the normal round-trip honest (§2.4).

Verification available without a GPU: `emit()` output, splat packing/unpacking
round-trip, radix sort stability, the sun/moon vector math, the day-night ramp,
and the LUT-vs-direct `styledTarget` equivalence can all be asserted in Node.
Shaders cannot be compiled here (no GL toolchain, Chrome lacks system libs), so
those stay hand-reviewed and small.