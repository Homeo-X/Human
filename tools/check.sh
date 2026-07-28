#!/usr/bin/env bash
# Everything that must be green before a commit or a release.
#
# Ordered cheapest-first so a failure surfaces fast. The substrate and unit
# checks are the ones fast enough for a pre-commit hook (NFR-010); the full run
# belongs in CI and in the release pipeline (FR-VALD-004).
#
#   bash tools/check.sh          full run
#   bash tools/check.sh --quick  substrate + unit tests only (pre-commit)
set -u
FAIL=0
QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1
export PYTHONPATH="src:.${PYTHONPATH:+:$PYTHONPATH}"

step() { printf '\n=== %s ===\n' "$1"; }
check() { if [ "$1" -ne 0 ]; then echo "FAILED: $2"; FAIL=1; fi; }

step "substrate invariants (biocheck --strict)"
# INV-21 is accepted, not silenced: 98 organs are placed by system membership
# and not by containment, which is the known state of the content recorded in
# D-029, not a regression. It still prints in full on every run, and --accept
# cannot touch a blocking invariant. Remove this flag when the placement
# curation lands — the build going red is then the correct outcome.
python3 tools/biocheck.py ontology/ --strict --accept INV-21
check $? "biocheck"

step "negative tests (every invariant must be able to fail)"
python3 tools/biocheck.py ontology/ --selftest
check $? "biocheck --selftest"

step "unit tests"
python3 -m unittest discover -s tests -t . -q
check $? "unit tests"

if [ "$QUICK" -eq 1 ]; then
  [ "$FAIL" -eq 0 ] && echo -e "\nQUICK CHECKS PASSED" || echo -e "\nFINDINGS ABOVE"
  exit $FAIL
fi

step "framework tree"
bash tools/validate.sh
check $? "validate.sh"

step "generated specification"
bash tools/validate.sh --docs docs/
check $? "validate.sh --docs"

step "spec graph (strict)"
python3 tools/specgraph.py docs/ --strict
check $? "specgraph --strict"

step "implementation trace"
# Untraced Musts are expected for modules not yet built (D-011): PERS, CUR,
# AGD, SIM, and the two viewer requirements. What must stay at zero is
# "claimed" — a Must with code but no test verifying it.
CLAIMED=$(python3 tools/specgraph.py docs/ --trace src tests tools 2>&1 \
          | grep -c 'claimed (code refs only)')
echo "Musts with code but no verifying test: $CLAIMED"
[ "$CLAIMED" -eq 0 ] || { echo "FAILED: every implemented Must needs a test"; FAIL=1; }
python3 tools/specgraph.py docs/ --trace src tests tools 2>&1 \
  | grep 'no implementation trace' \
  | sed 's/.*Must \(FR-[A-Z]*\)-.*/\1/' | sort | uniq -c | sort -rn \
  | sed 's/^/  untraced (unbuilt module): /'

step "release build (validates, hashes, runs evals)"
python3 -m homeo.cli build rel-check >/dev/null
check $? "release build"

if [ "$FAIL" -eq 0 ]; then
  echo -e "\nALL CHECKS PASSED"
else
  echo -e "\nFINDINGS ABOVE"
fi
exit $FAIL
