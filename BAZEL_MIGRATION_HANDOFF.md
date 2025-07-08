# Bazel Migration Completion - AI Agent Handoff

## Mission Statement
Complete the Bazel migration for the traffic simulator project by updating all documentation, configuration files, and references from `uv`/`pytest` to Bazel build system. The core Bazel infrastructure is functional and tested.

## Current Status
✅ **COMPLETED**: Core Bazel infrastructure, tests, build system, CI/CD, critical gitignore fixes, script consolidation
❌ **REMAINING**: Documentation updates (129+ references), configuration files, verification

## Project Context
- **Language**: Python 3.12
- **Build System**: Bazel (migrated from uv/pytest)
- **Project**: 2D traffic simulator with Arcade rendering
- **Location**: `/home/gxx/projects/traffic-simulator`
- **Git Status**: Clean working directory, all critical fixes committed

## Critical Issues Resolved
1. ✅ Bazel artifacts added to .gitignore and .cursorignore
2. ✅ Bazel symlinks removed (bazel-bin, bazel-out, bazel-testlogs)
3. ✅ Quality analysis scripts consolidated to single optimized version
4. ✅ Duplicate scripts removed

## Remaining Work (Priority Order)

### PHASE 1: Documentation Updates (HIGH PRIORITY)
**Target**: 129+ `uv run` references across 10 files need updating to Bazel commands

**Files to Update**:
1. `README.md` - Installation and usage instructions
2. `docs/DEVELOPMENT.md` - Development workflow (partially updated)
3. `docs/SCRIPTS_GUIDE.md` - Script usage examples
4. `docs/QUALITY_STANDARDS.md` - Tool usage examples
5. `docs/PERFORMANCE_GUIDE.md` - Performance testing commands
6. `docs/BENCHMARKING_GUIDE.md` - Benchmarking commands
7. `docs/QUALITY_GATES_GUIDE.md` - Quality gate commands
8. `docs/PERFORMANCE_OPTIMIZATION.md` - Optimization examples
9. `docs/TEST_CONSISTENCY_STANDARDS.md` - Test commands
10. `docs/DOCUMENTATION_GUIDE.md` - Documentation examples

**Command Mapping**:
```bash
# OLD (uv-based) → NEW (Bazel-based)
uv run python -m traffic_sim → bazel run //src/traffic_sim:traffic_sim_bin
uv run python -m pytest tests/ -v → bazel test //...
uv run python scripts/quality_analysis.py --mode=check → bazel run //scripts:quality_analysis -- --mode=check
uv run ruff check src/ --fix → bazel build //... (integrated)
uv run pyright src/ → bazel build //... (integrated)
uv run bandit -r src/ -c config/bandit.yaml → bazel build //... (integrated)
uv run radon cc src/ -a --min B → bazel build //... (integrated)
uv run pytest --cov=traffic_sim → bazel test //... (integrated)
```

### PHASE 2: Configuration Updates (MEDIUM PRIORITY)
**Files to Update**:
1. `Taskfile.yml` - Replace all `uv run` commands with Bazel equivalents
2. `AGENTS.md` - Update agent documentation and workflow examples
3. Cursor rules in `.cursor/rules/` - Update workflow references

**Taskfile.yml Updates**:
```yaml
# OLD
quality:
  cmds:
    - uv run python scripts/quality_analysis.py --mode=check

# NEW
quality:
  cmds:
    - bazel test //...
    - bazel build //...
```

### PHASE 3: Verification (MEDIUM PRIORITY)
**Actions Required**:
1. Verify all BUILD.bazel files are complete and correct
2. Test complete Bazel workflow end-to-end
3. Ensure CI/CD pipeline works with Bazel commands
4. Validate all documentation examples work

## Working Bazel Configuration

### Key Files
- `MODULE.bazel` - Module configuration with Python 3.12 toolchain
- `WORKSPACE.bazel` - Workspace configuration
- `.bazelrc` - Build and test flags
- `third_party/pip/` - Dependency management

### Essential Commands
```bash
# Build all targets
bazel build //...

# Run all tests
bazel test //...

# Run simulator
bazel run //src/traffic_sim:traffic_sim_bin

# Query build graph
bazel query //...

# Clean build artifacts
bazel clean
```

## Quality Standards
- **Type Safety**: Use `from __future__ import annotations`
- **Code Style**: 100 chars/line, functions <50 lines, classes <200 lines
- **Documentation**: Google-style docstrings for public APIs
- **Testing**: Comprehensive test coverage with Bazel integration

## Success Criteria
1. ✅ All Bazel artifacts properly ignored
2. ✅ Single quality analysis script (optimized version)
3. ❌ All documentation updated to use Bazel commands
4. ❌ Configuration files updated for Bazel workflow
5. ✅ CI/CD pipeline fully Bazel-based
6. ❌ No references to `uv run` commands in documentation
7. ✅ All tests pass with `bazel test //...`
8. ✅ All targets build with `bazel build //...`

## Implementation Strategy
1. **Systematic Documentation Update**: Process each file methodically
2. **Command Replacement**: Use consistent mapping for all `uv run` → Bazel
3. **Testing**: Verify each updated file works correctly
4. **Validation**: Ensure no broken references or examples

## Notes
- The Bazel migration is functionally complete and tested
- Focus on documentation consistency and accuracy
- Maintain the optimized quality analysis script
- Ensure all examples are executable and correct
- Test thoroughly after each phase

## References
- [Bazel Documentation](https://bazel.build/docs)
- [rules_python Documentation](https://github.com/bazelbuild/rules_python)
- [Project Quality Standards](docs/QUALITY_STANDARDS.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Batch Processing Methodology](docs/BATCH_PROCESSING_METHODOLOGY.md)

## Handoff Checklist
- [ ] Update README.md with Bazel installation/usage
- [ ] Update all docs/ files with Bazel commands
- [ ] Update Taskfile.yml with Bazel commands
- [ ] Update AGENTS.md with Bazel workflow
- [ ] Update cursor rules with Bazel references
- [ ] Verify all BUILD.bazel files are complete
- [ ] Test complete Bazel workflow
- [ ] Validate CI/CD pipeline
- [ ] Final documentation review
- [ ] Commit all changes with descriptive messages
