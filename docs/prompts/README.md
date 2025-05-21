# Cursor Prompts Directory

This directory contains specialized prompts and a repeatable methodology for optimizing, running, scoring, and iterating prompts that maintain the project’s documentation and rules.

## Contents
### generate-super.md
Unified Docs & Rules Maintainer super‑prompt with modes (docs | rules | hybrid) and shared APE workflow. Prefer this for future maintenance.

## Purpose

Provide a thorough, reproducible workflow (APE: Automated Prompt Engineering) to:
- Generate candidate prompts
- Run in-memory dry-runs on standardized inputs
- Score outputs using consistent rubrics
- Select, refine, and stabilize winners

## Link Policy (critical)
- Documentation must not reference rule files. Docs may reference other docs.
- Rules may reference docs and other rules.
- Prompts (in this directory) are exempt and may reference rules when necessary to guide the agent.

## APE Workflow (high-level)
1. Define evaluation rubric(s) appropriate to the prompt’s task.
2. Generate 4–6 candidate prompts with meaningful variation (structure, brevity, targeting).
3. Prepare standardized inputs (see below) and run all candidates in-memory (dry-run, no file writes).
4. Score each output (absolute rubric score + pairwise preferences via Bradley–Terry/Elo).
5. Self-critique top 1–2 and revise once; re-score; repeat until gains plateau (≤ +1 point across two rounds).
6. Perform stability checks (minor perturbations); pick the more stable if tied.
7. Adopt the winner and archive the scoring summary.

## Standardized Inputs (for dry-runs)
Provide as much of the following as is available:
- Git signals: branch/HEAD, baseline tag/commit, `git status --porcelain`, `git diff` (unstaged), `git diff --staged`, `git log -n 30`
- Change inventory: paths and relevant hunks for `src/`, `tests/`, `config/`, `docs/`
- Chat/issue decisions: key requirements, acceptance criteria, chosen designs
- Style guide/glossary references
- For rule prompts: current taxonomy and list of existing rules (title, globs, description, references)

Run dry-runs in-memory: do not write to the repo until a winner is selected and a plan is approved.

## Evaluation Rubrics

### Documentation generation (super-prompt docs mode)
- PDQI‑9 (45): accuracy, thoroughness, clarity, consistency, relevance, organization, timeliness, efficiency, engagement
- Workspace compliance (25): heading style (“###”), doc structure, terminology/glossary, Google-style docstrings when needed
- Mechanical coverage (10): required sections, acceptance criteria, Gherkin scenarios, link hygiene
- Determinism/idempotency (10): stable anchors, minimal diffs, re-run no-op
- Consolidation/navigation (5): deduplication, internal nav updates
- Security/redaction (5): no secrets; redact clearly

### Rule generation (super-prompt rules mode)
- RGS score (100 total base):
  - Clarity & Actionability (25)
  - Token Efficiency (20): references over repetition; structured/scan-friendly
  - Maintainability (20): future-proof; modular; version-control-friendly
  - Context Relevance (15): precise globs; appropriate scope; cross-rule links
  - Documentation Quality (10): proper references (to docs), clear structure
  - Completeness (10): covers critical aspects; anticipates edge cases
- Additional audits and penalties:
  - No transitional/time-bound content; flag instead (−3..−10 if present)
  - Global rules ≤5; −5 per extra (cap −15)
  - Token budget soft cap 500; allowed up to 900 with justification (−3 for 500–700; −8 for 700–800; −15 >800)
  - Cross-link direction: no docs→rules links in documentation; rules may link to docs/rules; prompts are exempt
  - Taxonomy/packaging rationale: category-first; specific rules only for necessary precision
  - Consolidation reviewer gate: merges with similarity >0.6 must be reviewed

## Scoring & Selection
- Absolute rubric score (0–100) per candidate
- Pairwise Bradley–Terry/Elo ranking on identical inputs
- Stability index: 1 − normalized stddev across minor-perturbation runs
- MDL brevity penalty: deduct for non-informative verbosity
- Winner must outperform alternatives and pass stability checks

## Determinism & Idempotency
- Stable heading anchors and deterministic slugging
- Minimal diffs; preserve unrelated content formatting
- Hidden metadata allowed in rules/docs sections (e.g., fingerprints) when applicable to prompts; do not introduce metadata into docs where policies forbid

## Consolidation Policy (rules)
- Prefer consolidating into canonical category rules; split overloaded rules when needed
- Require reviewer approval for merges with similarity >0.6
- Maintain redirects/aliases if supported by your environment (prompts may propose; human applies)

## Running APE Locally (manual, no CLI)
1. Stage work-in-progress changes or stash them temporarily.
2. Collect standardized inputs via Git commands listed above.
3. Open the target prompt (`generate-super.md`) and provide inputs.
4. Capture outputs and score using the rubrics in this README.
5. Iterate on the winner until scores plateau; re-run stability checks.
6. Prepare diffs; review; then apply changes manually.

## Pre-commit Hooks Guidance
- Hooks will fix EOF/trailing whitespace automatically; re-add and commit after hook fixes
- Keep commits small and focused; use Conventional Commit messages
- Run hooks locally via `uv run pre-commit run --all-files` when in doubt

## Governance & Maintenance
- Prompts are exempt from docs→rules link restrictions; documentation pages are not
- Review prompts after major framework or policy changes
- Archive APE scoring summaries alongside commits (e.g., in PR descriptions)

## References
- Quality Standards Guide: `mdc:docs/QUALITY_STANDARDS.md`
- Cursor Rules Guide: `mdc:docs/CURSOR_RULES.md`
- Architecture Guide: `mdc:docs/ARCHITECTURE.md`
- Performance Guide: `mdc:docs/PERFORMANCE_GUIDE.md`

---

If you need help running the APE loop for a particular change, start with `generate-super.md` (docs, rules, or hybrid mode), provide the standardized inputs above, and follow the Scoring & Selection process here.
