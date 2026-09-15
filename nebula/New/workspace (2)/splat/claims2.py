import numpy as np, time

print("=" * 78)
print("CLAIM: 'no floating-point drift' over a 150-meter sector")
print("=" * 78)
rng = np.random.default_rng(1)


def persp(fov, asp, n, f):
    t = 1 / np.tan(np.radians(fov) / 2)
    return np.array([[t / asp, 0, 0, 0], [0, t, 0, 0],
                     [0, 0, (f + n) / (n - f), 2 * f * n / (n - f)], [0, 0, -1, 0]])


def lookat(eye, tgt, up):
    z = eye - tgt; z /= np.linalg.norm(z)
    x = np.cross(up, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.array([[*x, -x @ eye], [*y, -y @ eye], [*z, -z @ eye], [0, 0, 0, 1]])


eye = np.array([-40., 0., 15.])
V = lookat(eye, np.array([75., 0., 15.]), np.array([0, 0, 1.]))
pts = np.column_stack([rng.uniform(0, 150, 20000), rng.uniform(-50, 50, 20000),
                       rng.uniform(0, 30, 20000), np.ones(20000)])
wv = (pts @ V.T)[:, 2]
print(f"  view-space depth range: [{-wv.max():.1f}, {-wv.min():.1f}] m   all in front: {np.all(wv < 0)}")


def pxerr(M):
    a = pts @ M.T
    b = pts.astype(np.float32) @ M.astype(np.float32).T
    keep = (a[:, 3] > 1e-9) & (b[:, 3] > 1e-9)
    na = a[keep, :3] / a[keep, 3:4]; nb = b[keep, :3] / b[keep, 3:4]
    return np.linalg.norm(na - nb, axis=1) * 0.5 * 1000


print(f"\n  float64 vs float32 through the full MVP chain, error on a 1000-px axis:")
print(f"  {'near':>7}{'far':>8}{'mean px':>12}{'p99 px':>12}{'max px':>12}")
for n, f in [(0.1, 500), (0.5, 500), (1.0, 500), (0.01, 500), (0.1, 5000), (0.001, 1000)]:
    e = pxerr(persp(60, 16 / 9, n, f) @ V)
    print(f"  {n:>7}{f:>8}{e.mean():>12.2e}{np.percentile(e, 99):>12.2e}{e.max():>12.2e}")

print("""
  => Screen-space error is ~2e-5 px across the whole 150 m sector and is INVARIANT
     to near/far. That invariance is not luck: near/far scales only the z column of
     the projection, and the perspective divide cancels it in x and y. So near/far
     cannot affect screen-space xy accuracy at all.

     What near/far DOES affect is depth-buffer resolution (z-fighting) -- and
     gaussian splatting has no depth buffer, it alpha-blends in sorted order. For a
     splatter the near plane is therefore close to a free parameter, which is a nice
     property worth stating explicitly rather than leaving implicit.

     Verdict: 'no floating-point drift' HOLDS for screen-space geometry at this
     scale. float32 ULP at 150 m is 15 micrometres. The real determinism hazard is
     elsewhere -- the float->uint32 depth key conversion, and whether depth is
     quantised to an integer BEFORE sorting (if it is, the sort is bit-identical
     across platforms even though the float32 view math is not guaranteed to be).""")

print("=" * 78)
print("CLAIM: fixed 4-pass bit-inversion radix sort, O(n), n = 107k")
print("=" * 78)


def f2key(d):
    """IEEE-754 float32 -> monotone uint32 ('the bit inversion')."""
    u = np.asarray(d, np.float32).view(np.uint32).copy()
    return np.where(u >> 31 != 0, ~u, u | np.uint32(0x80000000)).astype(np.uint32)


def counting_pass(cur, keys, shift):
    """One stable LSD radix pass. A stable argsort on the 256-valued digit IS the
    counting sort -- it places equal digits in input order, which is exactly the
    stability the multi-pass scheme depends on.
    (Earlier version computed rank = arange - start[digit], which is the sequence
    index minus the bucket start, not the within-bucket rank. That produced a valid
    permutation and sorted nothing.)"""
    dg = ((keys[cur] >> np.uint32(shift)) & np.uint32(0xFF)).astype(np.int64)
    return cur[np.argsort(dg, kind='stable')]


def radix(keys, passes):
    order = np.arange(len(keys), dtype=np.int64)
    for p in range(passes):
        order = counting_pass(order, keys, 8 * p)
    return order


rng = np.random.default_rng(2)
depth = rng.uniform(0.1, 300, 107_000).astype(np.float32)
k = f2key(depth)
# sanity: the key transform must preserve order
assert np.array_equal(np.sort(k), f2key(np.sort(depth))), "bit-inversion is not monotone"
print("  float->uint32 bit inversion verified monotone against a float32 sort.")

for keys, p, lbl in [
        (k, 4, "4 passes on the full 32-bit float key"),
        ((k >> np.uint32(16)).astype(np.uint32), 2, "2 passes on a true 16-bit depth key"),
        (k, 2, "2 passes on 32-bit keys (WRONG -- see note)")]:
    t = time.perf_counter(); o = radix(keys, p); el = time.perf_counter() - t
    ok = bool(np.all(np.diff(keys[o].astype(np.int64)) >= 0))
    print(f"  {lbl:<46} {el*1000:7.1f} ms   fully sorted = {ok}")

t = time.perf_counter(); np.argsort(k, kind='stable'); el2 = time.perf_counter() - t
print(f"  {'numpy stable argsort (compiled C)':<42} {el2*1000:8.1f} ms")

print(f"""
  Note the third line: running only 2 of the 4 LSD passes over a 32-bit key yields a
  VALID PERMUTATION that is NOT sorted. It fails silently -- nothing raises, the
  output looks plausible, and the render merely looks subtly wrong. If the pass count
  is ever made configurable or keyed to a bit width, assert on the sortedness of the
  result in debug builds. This is the sort bug that is worth worrying about, and it is
  not the one about scatter vs gather.

  A vectorised numpy counting sort clears 4 passes over 107k keys in milliseconds, and
  compiled C/WASM or a GPU counting sort is faster still. So a 122 ms figure CANNOT be
  the per-frame sort. It is either cold start (shader compile + buffer upload + first
  frame) or it includes work beyond sorting. Which one matters a lot:
    - if 122 ms is the per-frame sort, the frame budget at 60 fps is 16.7 ms and the
      renderer is ~7x over, i.e. ~8 fps;
    - if 122 ms is cold start, steady-state framerate is essentially unconstrained by
      the sort and 107k splats is a comfortable load.
  The claim should say which. 'Materialising in 122 ms' reads as cold start, but
  'respecting the metal' reads as per-frame, and the two imply opposite headroom.""")

print("=" * 78)
print("CLAIM: 'seed(s) == emission(t)' as bounded determinism")
print("=" * 78)
print("""
  Holds for the parts that are integer, fails for the parts that are not:
    STABLE  : the radix sort (stable, on integer keys) -> identical permutation
              on any platform, given identical keys.
    STABLE  : bilerp over an integer heightfield, if the interpolation weights are
              computed identically.
    NOT STABLE: the view matrix and the depth key. Those come from float32 mul/add,
              and WebGL2 does NOT guarantee rounding mode, FMA contraction, or
              transcendental accuracy across drivers. Two GPUs can produce depths
              that differ by 1 ULP, which can flip the order of two nearly-equal
              splats.
  The fix is the one already implied by the design: QUANTISE depth to an integer
  grid before sorting. Then the sort is a function of integers end to end and
  seed->emission is genuinely deterministic; the residual nondeterminism is a
  sub-ULP wobble in which quantisation bin a depth lands in, which is invisible.
  Without that quantisation step the creed is aspirational, not enforced.""")
