# How to run it

Everything lives in two directories under the workspace root:

```
dyad/     the cross-substrate Noether theory, its audit, the J_C estimator, the rank harness
splat/    the gaussian-splat claim checks and the radius-of-validity experiment
run.sh    single entry point
```

## 1. Get the files

If you are working in this same workspace, they are already there — skip to step 2.

If you are on your own machine, copy the two directories and `run.sh` somewhere, keeping
them **side by side**, e.g.

```
~/work/
├── run.sh
├── dyad/
└── splat/
```

`run.sh` locates the tracks relative to itself, so the whole tree can live anywhere.
`verdict.py` and `sanity.py` load the `Block` class out of `radius_of_validity.py`, so
those three must stay in the same directory (they resolve it by their own path, not by
cwd, so you can invoke them from anywhere).

## 2. Install dependencies

Only two, and the second is optional.

```bash
pip install numpy                                                    # required, everything
pip install torch --index-url https://download.pytorch.org/whl/cpu   # only for splat/ radius experiment
```

CPU-only torch is enough — the Jacobian is `(T*D)^2 = 384x384`, no GPU needed.
**scipy and scikit-learn are NOT required.** `rank_harness.py` implements Spearman
itself specifically to avoid the dependency. Python 3.9+ (tested on 3.11).

## 3. Run

```bash
./run.sh              # both tracks, ~80 s, 15 scripts
./run.sh dyad         # theory + estimators only (numpy only)
./run.sh splat        # splat claims + radius experiment (needs torch)
./run.sh quick        # the four headline numbers, ~30 s
```

If torch is missing, `run.sh` prints the install command and **skips** the torch
scripts rather than failing, so `./run.sh all` still works on a numpy-only box.

Every script's output is tee'd into `logs/`, so you can diff runs or grep afterwards:

```bash
grep -A6 "JACOBIAN SPECTRUM" logs/splat_4_verdict.log
```

Or run any script directly — they are all standalone and print their own results:

```bash
cd splat && python3 verdict.py
cd dyad  && python3 validate.py
```

## 4. What to look at first

In this order, if you only read four things:

| script | the number that matters |
|---|---|
| `splat/verdict.py` | `sym(J)/||J|| = 0.810` — the Jacobian is not a Hermitian generator |
| `splat/radius_of_validity.py` | `delta*_sparse = 0.164` vs one token `= 1.000` → **6.1× past the radius** |
| `dyad/cert_test.py` | all six spectral statistics identical, response **132% wrong** |
| `dyad/validate.py` | `beta_1` recovery: pooled OLS **57.9%** vs turn fixed-effects **98.9%** |

Then the writeups, which carry the derivations and the caveats:

```
dyad/MEMO_cross_substrate_noether.md      the original audit: 4 defects, the repair
dyad/ADDENDUM_monadic_audit.md            the drive term, NESS, power-balance theorem
dyad/RESULTS_estimators_and_rank.md       estimator + rank harness results, 3 hypotheses
splat/RADIUS_OF_VALIDITY.md               the radius experiment and its verdict
```

## 5. Runtime and resources

Measured on 2 CPU cores, no GPU:

| track | time | peak RSS |
|---|---|---|
| `dyad` (10 scripts) | ~55 s | ~150 MB |
| `splat` (5 scripts) | ~28 s | ~400 MB |
| `./run.sh all` | ~80 s | ~400 MB |

The slowest single script is `dyad/part3.py` (~25 s, RK4 over `tau in [0,80]` at
`dt = 2e-4`) and `splat/sanity.py` (~24 s, six Jacobians).

## 6. Reproducing a specific claim

Each writeup states which script produces which number, and each script has a docstring
saying what it tests. To re-derive one result:

```bash
# "the rank(G) safety certificate is refuted"
cd dyad && python3 cert_test.py

# "float32 does not drift at 150 m, and near/far cannot affect screen-space xy"
cd splat && python3 claims2.py

# "quaternion quantisation costs 0.43 degrees"
cd splat && python3 claims.py
```

## 7. Known non-runs

- `dyad/rc_estimator.py` and `dyad/rank_harness.py` are **libraries**, not scripts —
  running them directly prints nothing. They are exercised by `dyad/validate.py`.
- `partial_MI` in `rc_estimator.py` is **known-broken**: it returns ~0 on ground truth
  where it should be positive. Documented in `dyad/RESULTS_estimators_and_rank.md` §2.4.
  Not fixed, deliberately — it is the open item.
- `dyad/validate.py` regenerates its synthetic session from a fixed seed
  (`seed=20260915`), so results are bit-reproducible. It writes no output files.
- Nothing here touches the network, and nothing writes outside `logs/`.
