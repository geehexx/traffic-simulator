# Agent Documentation Update Checklist

This checklist helps AI agents determine when documentation updates are necessary and appropriate.

## Before Updating Documentation

### Decision Framework
- [ ] **Is this change permanent and stable?** (Not experimental or temporary)
- [ ] **Does this affect user workflow or configuration?** (Changes how users interact with the system)
- [ ] **Is this information that will remain relevant long-term?** (Not version-specific or hardware-dependent)
- [ ] **Does this add actionable guidance for developers?** (Provides clear instructions or configuration)
- [ ] **Is this avoiding static performance metrics?** (Focuses on how-to, not how-fast)

### Content Quality Check
- [ ] **Focuses on actionable guidance** (What to do, not what happened)
- [ ] **Avoids specific performance numbers** (No timing measurements or hardware-bound benchmarks)
- [ ] **Uses configuration examples, not results** (Shows how to configure, not what was achieved)
- [ ] **Provides clear instructions** (Step-by-step guidance)
- [ ] **References existing documentation appropriately** (Links to relevant guides)

## When to Update Documentation

### ✅ Appropriate Updates
- **New features or APIs** that change user workflow
- **Configuration changes** that affect how users set up the system
- **New tools or processes** that users need to know about
- **Bug fixes** that change behavior or requirements
- **Workflow improvements** that affect how developers work

### ❌ Inappropriate Updates
- **Performance optimizations** unless they change user-facing behavior
- **Temporary changes** or experimental features
- **Specific performance metrics** that become outdated quickly
- **Version-specific data** that changes with updates
- **Hardware-dependent measurements** that vary by system

## Content Guidelines

### Good Documentation Updates
- **Configuration guidance**: "Use `pass_filenames: false` to prevent multiple executions"
- **Tool usage**: "Configure pre-commit hooks with optimized settings"
- **Process changes**: "Updated workflow to include new validation steps"
- **Feature additions**: "Added new configuration option for performance tuning"

### Avoid These Updates
- **Performance results**: "Optimized for 64% faster execution (14.3s → 5.2s)"
- **Specific metrics**: "Achieved 11.4x improvement at 20 vehicles"
- **Timing data**: "Reduced execution time from 5.6s to 3.6s"
- **Benchmark results**: "Performance improved by 2.3x on average"

## File Organization

### Before Creating New Files
- [ ] **Check existing documentation** for similar content
- [ ] **Use appropriate file names** (no "SUMMARY" in filename)
- [ ] **Consolidate related information** into existing files when possible
- [ ] **Maintain proper cross-references** to other documentation

### File Naming Guidelines
- **✅ Good**: `PERFORMANCE_GUIDE.md`, `DEVELOPMENT.md`, `QUALITY_STANDARDS.md`
- **❌ Bad**: `PERFORMANCE_OPTIMIZATION_SUMMARY.md`, `BENCHMARKING_RESULTS.md`

## Examples

### ✅ Good Documentation Update
```markdown
## Pre-commit Hooks
Quality gates run automatically on every commit:
- **Ruff**: Linting and formatting
- **Pyright**: Type checking with optimized configuration
- **Bandit**: Security scanning
- **Radon**: Complexity analysis

**Configuration**: Uses `pass_filenames: false` to prevent multiple executions and optimize performance.
```

### ❌ Bad Documentation Update
```markdown
## Pre-commit Hooks
Quality gates run automatically on every commit with optimized performance (~5.2s):
- **Ruff**: Linting and formatting (replaces black)
- **Pyright**: Fast, accurate type checking (45s timeout, --stats enabled)
- **Bandit**: Security scanning (single execution via pass_filenames: false)
- **Radon**: Complexity analysis (single execution via pass_filenames: false)

**Performance**: Optimized for 64% faster execution (14.3s → 5.2s) by eliminating redundant tools and multiple executions.
```

## References
- [Planning and Implementation Guidelines](mdc:.cursor/rules/planning-and-implementation-guidelines.mdc) - Comprehensive planning guidelines
- [Documentation Guide](mdc:docs/DOCUMENTATION_GUIDE.md) - Documentation standards
- [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md) - Code quality standards
