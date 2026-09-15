#!/usr/bin/env bash
# Run everything, or one track.
#
#   ./run.sh              # both tracks (~2 min)
#   ./run.sh dyad         # theory audit + estimators      (needs numpy only)
#   ./run.sh splat        # splat claims + radius experiment (needs numpy + torch)
#   ./run.sh quick        # just the headline results, ~20 s
#
# Output is tee'd to logs/ so you can diff runs.

set -uo pipefail
cd "$(dirname "$0")"
mkdir -p logs
TRACK="${1:-all}"

have() { python3 -c "import $1" >/dev/null 2>&1; }

need_numpy() {
  if ! have numpy; then
    echo "!! numpy is missing. Install it:"; echo "     pip install numpy"; exit 1
  fi
}
need_torch() {
  if ! have torch; then
    echo "!! torch is missing (needed for the radius experiment). Install CPU-only:"
    echo "     pip install torch --index-url https://download.pytorch.org/whl/cpu"
    echo "   Skipping the torch track rather than failing."
    return 1
  fi
  return 0
}

run() {  # run <subdir> <script> <logfile>
  local d="$1" s="$2" log="$3"
  printf '\n\033[1m=== %s/%s\033[0m\n' "$d" "$s"
  ( cd "$d" && python3 -W ignore "$s" ) 2>&1 | tee "logs/$log"
  local rc=${PIPESTATUS[0]}
  [ "$rc" -eq 0 ] && echo "-- ok ($rc)" || echo "-- FAILED (exit $rc)"
}

dyad_track() {
  need_numpy || exit 1
  echo "############ TRACK: dyad -- theory audit, estimators, rank harness ############"
  run dyad noether_check.py        dyad_1_noether.log
  run dyad part2.py                dyad_2_symmetry.log
  run dyad part3.py                dyad_3_repaired.log
  run dyad calibrate.py            dyad_4_calibrate.log
  run dyad part4_drive.py          dyad_5_drive.log
  run dyad part5_rank.py           dyad_6_rank.log
  run dyad part6b.py               dyad_7_governor.log
  run dyad cert_test.py            dyad_8_cert.log
  run dyad part7_samplesize.py     dyad_9_samplesize.log
  run dyad validate.py             dyad_10_validate.log
}

splat_track() {
  need_numpy || exit 1
  echo "############ TRACK: splat -- renderer claims, then radius of validity ############"
  run splat claims.py              splat_1_bytes_quat.log
  run splat claims2.py             splat_2_float_sort.log
  if need_torch; then
    run splat radius_of_validity.py splat_3_radius.log
    run splat verdict.py            splat_4_verdict.log
    run splat sanity.py             splat_5_sensitivity.log
  fi
}

quick() {
  need_numpy || exit 1
  echo "############ QUICK: the four headline numbers ############"
  run dyad cert_test.py            quick_cert.log
  run dyad part7_samplesize.py     quick_samplesize.log
  if need_torch; then
    run splat verdict.py           quick_verdict.log
    run splat sanity.py            quick_sensitivity.log
  fi
}

case "$TRACK" in
  dyad)  dyad_track ;;
  splat) splat_track ;;
  quick) quick ;;
  all)   dyad_track; splat_track ;;
  *)     echo "usage: ./run.sh [all|dyad|splat|quick]"; exit 2 ;;
esac

echo
echo "Logs in $(pwd)/logs/"
echo "Writeups: dyad/MEMO_cross_substrate_noether.md"
echo "          dyad/ADDENDUM_monadic_audit.md"
echo "          dyad/RESULTS_estimators_and_rank.md"
echo "          splat/RADIUS_OF_VALIDITY.md"
