## Automated Prompt Engineering (APE) Methodologies {#id:ape-methodologies}

### Scope
- Canonical source for APE techniques, rubrics, metrics, and positive/negative examples used in this repository.

### Methodologies
- Candidate generation with meaningful variation
- Dual-path artifacts: update/consolidate vs regenerate
- Pairwise ranking (Bradley–Terry/Elo) and PDQI‑9/RGS scoring
- Stability harness with seeded perturbations (winner threshold ≥0.85)
- Idempotent editing with stable anchors and minimal diffs

### Techniques
- Token strategy under long contexts
- Consolidation planning and SoT scoring
- Link hygiene and cross-reference integrity checks
- HITL checkpoints and decision memos

### Rubrics & Metrics
- PDQI‑9 (docs), RGS (rules)
- Global: Idempotency, Stability, Duplication/SoT, Link hygiene, Arcade API validity, Quality‑gates alignment

### Examples
- Positive: concise consolidation with stable anchors; minimal unrelated churn
- Negative: time‑bound claims; docs→rules links; unstable headings; over-broad global rules
