# Prompt Optimization Guide

This guide covers the automated prompt optimization system integrated into the MCP server, providing a repeatable methodology for optimizing, running, scoring, and iterating prompts that maintain the project's documentation and rules.

## Contents
### MCP_PROMPTS/generate-super.md
Unified Docs & Rules Maintainer super‑prompt with modes (docs | rules | hybrid) and shared APE workflow. Prefer this for future maintenance.
### MCP_PROMPTS/generate-meta-optimizer.md
High‑reasoning meta‑optimizer for prompts and artifacts. Designs criteria, runs dry‑run comparisons (update/consolidate vs regenerate), scores with PDQI‑9/RGS + stability/SoT, and selects winners. Long‑running; use sparingly.

## Purpose

Provide a thorough, reproducible workflow (APE: Automated Prompt Engineering) to:
- Generate candidate prompts with systematic variation
- Run in-memory dry-runs on standardized inputs
- Score outputs using consistent rubrics and stability testing
- Select, refine, and stabilize winners with human-in-the-loop feedback

**For detailed methodologies, see [AUTOMATED_PROMPT_ENGINEERING.md](mdc:docs/AUTOMATED_PROMPT_ENGINEERING.md#ape-methodologies).**

## Link Policy (critical)
- Documentation must not reference rule files. Docs may reference other docs.
- Rules may reference docs and other rules.
- Prompts (in this directory) are exempt and may reference rules when necessary to guide the agent.

## Quick Start

### APE Workflow Overview
1. **Define rubrics** appropriate to the task (docs vs rules)
2. **Generate 4-6 candidates** with meaningful variation
3. **Run dry-runs** in-memory with standardized inputs
4. **Score and rank** using PDQI-9/RGS + stability testing
5. **HITL review** for ties and consolidation decisions
6. **Select winner** and archive scoring summary

### Key Requirements
- **Stability Index ≥0.85** for all winners
- **Dry-run only** until winner selected and approved
- **HITL checkpoints** at critical decision points
- **Archive rationale** for traceability

**For complete methodologies, see [AUTOMATED_PROMPT_ENGINEERING.md](mdc:docs/AUTOMATED_PROMPT_ENGINEERING.md#ape-methodologies).**

## Running APE Locally

### Manual Process
1. **Stage changes** or stash work-in-progress
2. **Collect inputs** via Git commands (see APE.md for complete list)
3. **Open target prompt** (`generate-super.md` or `generate-meta-optimizer.md`)
4. **Provide inputs** and capture outputs
5. **Score using rubrics** (see APE.md for detailed scoring)
6. **Iterate and stabilize** until scores plateau
7. **Apply changes** after review and approval

### Key Principles
- **Deterministic**: Stable anchors, minimal diffs, reproducible ordering
- **Idempotent**: Re-runs produce identical output when inputs unchanged
- **Consolidation**: Merge overlapping content, maintain canonical sources
- **HITL Integration**: Human review at critical decision points

## Pre-commit Hooks Guidance
- Hooks will fix EOF/trailing whitespace automatically; re-add and commit after hook fixes
- Keep commits small and focused; use Conventional Commit messages
- Run hooks locally via `uv run pre-commit run --all-files` when in doubt

## Governance & Maintenance
- Prompts are exempt from docs→rules link restrictions; documentation pages are not
- Review prompts after major framework or policy changes
- Archive APE scoring summaries alongside commits (e.g., in PR descriptions)

## References

### Core Documentation
- **APE Methodologies**: `mdc:docs/AUTOMATED_PROMPT_ENGINEERING.md#ape-methodologies` - Complete methodologies, rubrics, and academic references
- **Quality Standards**: `mdc:docs/QUALITY_STANDARDS.md`
- **Cursor Rules**: `mdc:docs/CURSOR_RULES.md`
- **Architecture**: `mdc:docs/ARCHITECTURE.md`
- **Performance**: `mdc:docs/PERFORMANCE_GUIDE.md`

### Getting Started
For help running the APE loop:
1. **Start with** `generate-super.md` (docs/rules/hybrid mode)
2. **Provide inputs** as detailed in APE.md
3. **Follow scoring** and selection process in APE.md
4. **Use HITL checkpoints** for complex decisions
