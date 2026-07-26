#!/usr/bin/env bash
# PRD-Agent framework static validator.
# Framework tree: bash tools/validate.sh   (run from framework root)
# Generated spec: bash tools/validate.sh --docs <dir>   (checks a docs/ set;
#   runs tools/specgraph.py semantic checks when python3 is present —
#   set STRICT=1 to promote semantic warnings to failures)
# Exits non-zero on any finding. Dependency-free.
set -u; FAIL=0; note(){ echo "FAIL: $*"; FAIL=1; }

if [ "${1:-}" = "--docs" ]; then
  D="${2:?usage: validate.sh --docs <dir>}"
  [ -f "$D/MANIFEST.md" ] || note "no MANIFEST.md in $D"
  for f in "$D"/*.md; do
    head -1 "$f" | grep -q '^---$' || note "no front-matter: $f"
    grep -q '^status: template' "$f" && note "untouched template shipped as doc: $f"
    grep -qE '^status: (draft|in-review|approved)' "$f" || note "bad/missing status: $f"
  done
  for f in "$D"/PRD_FR_*.md; do [ -e "$f" ] || continue
    case "$f" in */PRD_FR_Overview.md) continue;; esac  # index file, not a module
    for sct in "Purpose & Scope" "Requirements" "Data Touched" "Edge Cases"                "Dependencies" "Success Metrics" "Open Questions"; do
      grep -q "^## .*$sct" "$f" || note "missing section [$sct] in $f"
    done
  done
  ls "$D"/*.md | grep -E '[ &,]' | while read -r f; do note "bad chars: $f"; done
  for f in "$D"/PRD_FR_Agent_Definition*.md; do [ -e "$f" ] || continue
    for fc in Identity Goal State Memory Tools Permissions "Planning Policy" \
              "Execution Policy" Observation Recovery Evaluation "Cost Boundary"; do
      grep -q "^## Facet .*$fc" "$f" || note "agent facet missing [$fc] in $f"
    done
  done
  if ls "$D"/GDD_*.md >/dev/null 2>&1; then
    grep -q "^- \*\*Genre" "$D/MANIFEST.md" 2>/dev/null || note "game profile: no Genre line in MANIFEST.md"
    [ -f "$D/GDD_Design_Review.md" ] || note "game profile: missing GDD_Design_Review.md (rubric dispositions)"
  fi
  if ls "$D"/BIO_*.md >/dev/null 2>&1; then
    grep -q "^- \*\*Scale depth" "$D/MANIFEST.md" 2>/dev/null || note "bio profile: no Scale depth line in MANIFEST.md"
    [ -f "$D/BIO_Scale_Contract.md" ] || note "bio profile: missing BIO_Scale_Contract.md (never omitted at any tier)"
    [ -f "$D/BIO_Evidence_and_Provenance.md" ] || note "bio profile: missing BIO_Evidence_and_Provenance.md (never omitted at any tier)"
    if [ -f "$D/BIO_Model_Review.md" ]; then
      # every BRB item in the rubric must appear dispositioned in the review
      for b in $(grep -ohE '^\| BRB-[0-9]+' templates/bio/BIO_RUBRIC.md 2>/dev/null | grep -oE 'BRB-[0-9]+' | sort -u); do
        grep -qE "^\| $b \| *[A-Za-z*_\`]" "$D/BIO_Model_Review.md" || note "bio profile: $b has no disposition in BIO_Model_Review.md"
      done
      grep -qE '^\| BRB-[0-9]+ \| *\|' "$D/BIO_Model_Review.md" && note "bio profile: BIO_Model_Review.md has an empty disposition cell"
    else
      note "bio profile: missing BIO_Model_Review.md (rubric dispositions)"
    fi
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 "$(dirname "$0")/specgraph.py" "$D" ${STRICT:+--strict} || FAIL=1
  else
    echo "note: python3 absent — semantic spec-graph checks skipped"
  fi
  [ "$FAIL" -eq 0 ] && echo "DOCS CHECKS PASSED" || echo "FINDINGS ABOVE"; exit $FAIL
fi

# 0. Required root docs present
for req in AGENTS.md INTEGRATIONS.md MEMORY.md PROFILES.md README.md RED_TEAM.md SPEC_MODEL.md; do
  [ -f "$req" ] || note "missing root doc: $req"
done

# 1. Filename charset: letters/digits/underscore/dot/dash(dirs) only
find . -path ./.git -prune -o -name '*.md' -print | grep -E '[ &,]' \
  | while read -r f; do note "bad chars in filename: $f"; done

# 2. Front-matter on every template (excluding READMEs)
while read -r f; do
  head -1 "$f" | grep -q '^---$' || note "no front-matter: $f"
  awk 'NR>1 && /^---$/{ok=1;exit} END{exit !ok}' "$f" || note "unterminated front-matter: $f"
done < <(find templates -name '*.md' ! -name 'README.md')

# 3. FR modules: full section set
for f in templates/modules/*/PRD_FR_*.md templates/modules/_MODULE_TEMPLATE.md; do
  for s in "Purpose & Scope" "Requirements" "Data Touched" "Edge Cases" \
           "Dependencies" "Success Metrics" "Open Questions"; do
    grep -q "^## .*$s" "$f" || note "missing section [$s] in $f"
  done
done

# 4. AREA code uniqueness across module library
dups=$(grep -rhoE '^\| FR-[A-Z]{2,5}-' templates/modules/*/ templates/gdd/ templates/research/ templates/devtool/ templates/bio/ | grep -oE 'FR-[A-Z]{2,5}-' | sort | uniq \
  | while read -r c; do grep -rlE "^\| $c" templates/modules/*/ templates/gdd/ templates/research/ templates/devtool/ templates/bio/ | xargs -n1 basename | sort -u \
      | awk -v c="$c" 'END{if(NR>1) print c" in "NR" files"}'; done)
[ -n "$dups" ] && note "AREA code shared across modules: $dups"

# 5. File references in AGENTS.md and .claude/ resolve to real templates
#    (skip placeholders with <>, glob prefixes ending in _, generated-only files)
gen_only="MANIFEST PRD_Decision_Log_Archive DECISIONS_DIGEST"
while read -r tok; do
  case "$tok" in *"<"*|*_) continue;; esac
  base="${tok%.md}"; echo "$gen_only" | grep -q "$base" && continue
  find templates -name "${base}.md" | grep -q . || note "dead template ref '$tok' in AGENTS.md/.claude"
done < <(grep -rhoE '(PRD|TECH|GDD|RES|DEV|BIO)_[A-Za-z_<>]+' AGENTS.md INTEGRATIONS.md PROFILES.md .claude/ templates/gdd/README.md templates/research/README.md templates/devtool/README.md templates/bio/README.md | sort -u)

# 6. Section (§N) references resolve to AGENTS.md headings
maxsec=$(grep -cE '^## [0-9]+\.' AGENTS.md)
while read -r s; do
  n="${s#§}"
  [ "$n" -le "$maxsec" ] 2>/dev/null || note "dead section ref $s (AGENTS.md has $maxsec sections)"
done < <(grep -rhoE '§[0-9]+' AGENTS.md INTEGRATIONS.md .claude/ | sort -u)

# 7. No deprecated filename patterns (spaces/&/commas leaked into refs)
grep -rnE '`[A-Z]+_[^`]*[ &,][^`]*`' AGENTS.md CLAUDE.md .claude/ 2>/dev/null \
  | while read -r l; do note "deprecated filename pattern in ref: $l"; done

# 8. No backticked path/filename wrapped across lines (agents grep literally)
grep -rnE '\`[A-Za-z0-9_./]+/$|\`[A-Za-z0-9./]*[A-Za-z0-9]_$' AGENTS.md CLAUDE.md INTEGRATIONS.md .claude/ templates/README.md 2>/dev/null \
  | while read -r l; do note "path/filename wrapped mid-token: $l"; done

# 9. Tier tag vocabulary
while read -r f; do
  t=$(awk -F': *' '/^tier:/{print $2; exit}' "$f" | awk '{print $1}')
  case "$t" in light|light+|standard+|any|"") [ -z "$t" ] && note "no tier tag: $f";; 
    *) note "unknown tier tag '$t' in $f";; esac
done < <(find templates -name '*.md' ! -name 'README.md')

[ "$FAIL" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "FINDINGS ABOVE"; exit $FAIL
