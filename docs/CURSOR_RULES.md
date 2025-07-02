# Cursor Rules Guide

This document provides comprehensive guidance on the Cursor rules system used in the traffic simulator project for maintaining code quality and development consistency.

## Table of Contents
- [Overview](#overview)
- [Rule Categories](#rule-categories)
- [Rule Usage](#rule-usage)
- [Rule Maintenance](#rule-maintenance)
- [Best Practices](#best-practices)

## Overview

The project uses a curated set of agent-enforced rules (taxonomy-driven) to provide AI‑assisted development guidance. The rules cover code quality, architecture patterns, performance, and project‑specific guidelines.

## Rule Categories

### 1. Code Quality Standards
- **arcade-api-consistency.mdc**: Arcade API compatibility and validation
- **code-quality-standards.mdc**: Core code quality guidelines
- **rule-generation-standard.mdc**: Rule generation standards and quality metrics

### 2. Architecture & Patterns
- **simulation-patterns.mdc**: Core simulation architecture patterns
- **rendering-patterns.mdc**: Arcade rendering guidelines

### 3. Performance & Optimization
- **performance-standards.mdc**: Performance optimization guidelines

### 4. Configuration & Management
- **configuration-patterns.mdc**: Configuration management patterns

### 5. Documentation
- **documentation-patterns.mdc**: Documentation standards

### 6. Project Context
- **project-context.mdc**: Project overview and context

## Rule Usage

### Activating Rules
Rules are automatically loaded by Cursor when working in the project. They provide context-aware suggestions and guidance during development.

**Mandatory Rule Configuration:**
- **All rules MUST include**: `globs`, `description`, and `alwaysApply` in frontmatter
- **Universal Rules**: Use `globs: "**"` and `alwaysApply: true` for rules that should always apply
- **Specific Rules**: Use targeted globs like `globs: "src/**"` and `alwaysApply: false` for file-specific rules
- **No Defaults**: Explicit configuration eliminates ambiguity and prevents errors
- **Consistency**: Uniform structure across all rules improves maintainability

### Rule Selection
The system uses file pattern matching based on:
- **File Path Patterns**: Rules trigger based on `globs` patterns (e.g., category rules for simulation or rendering)
- **Explicit Configuration**: No AI-driven analysis - rules apply based on explicit glob patterns
- **Predictable Behavior**: File path matching ensures reliable, consistent rule application

### Rule Effectiveness
Rules are designed to:
- Maintain code quality consistency
- Enforce architectural patterns
- Guide performance optimization
- Ensure proper testing practices

## Rule Maintenance

### Updating Rules
Rules should be updated when:
- Project requirements change
- New patterns emerge
- Quality standards evolve
- Performance targets shift

### Rule Validation
Rules are validated through:
- Code review feedback
- Quality gate results
- Stability and idempotency checks (deterministic anchors, minimal diffs)
- Developer experience surveys

### Rule Lifecycle
1. **Creation**: Based on identified needs or patterns
2. **Testing**: Validated in development environment
3. **Deployment**: Integrated into project workflow
4. **Monitoring**: Tracked for effectiveness
5. **Evolution**: Updated based on feedback

## Best Practices

### For Developers
- Follow rule guidance when making changes
- Provide feedback on rule effectiveness
- Suggest new rules when patterns emerge
- Update rules when requirements change

### For Rule Authors
- Keep rules focused and specific
- Use clear, actionable language
- Include examples where helpful
- Regular review and updates
- **Mandatory frontmatter**: All rules MUST include `globs`, `description`, and `alwaysApply`
- **Universal rules**: Use `globs: "**"` and `alwaysApply: true` for rules that should always apply
- **Specific rules**: Use targeted globs and `alwaysApply: false` for file-specific rules
- **Test rule application**: Verify rules are actually being applied

### For Project Maintainers
- Monitor rule effectiveness
- Balance rule coverage with complexity
- Ensure rules align with project goals
- Regular rule audit and cleanup

## Integration with Quality Gates

The Cursor rules system integrates with the quality gates framework:
- Rules guide development practices
- Quality gates enforce standards
- Combined approach ensures consistency

## Troubleshooting

### Common Issues
1. **Rule conflicts**: Resolve by prioritizing more specific rules
2. **Outdated guidance**: Update rules when code changes
3. **Performance impact**: Optimize rule complexity
4. **Missing mandatory fields**: Rules without `globs`, `description`, and `alwaysApply` are not applied
5. **Incorrect glob patterns**: Universal rules need `globs: "**"` to apply everywhere
6. **Inconsistent alwaysApply**: Use `alwaysApply: true` for universal rules, `false` for specific rules

### Link Policy and Getting Help
Documentation pages must not link directly to rule files. Reference documentation pages via `mdc:` links and refer to rule categories conceptually. Rules may reference docs and other rules.

Getting help:
- Check rule documentation
- Review project guidelines
- Consult with team members
- Open issues for rule improvements

## Rule Effectiveness Measurement

### Performance Metrics
- **Rule Application Rate**: Track how often rules are triggered
- **Developer Feedback**: Monitor rule usefulness and clarity
- **Code Quality Impact**: Measure improvements in code consistency
- **Maintenance Overhead**: Track time spent updating rules

### Testing Rule Application
- **Manual Verification**: Check rule triggers with test files
- **Glob Pattern Testing**: Validate glob patterns match intended files
- **Rule Interaction Testing**: Ensure rules work together correctly
- **Performance Testing**: Verify rule application doesn't impact development speed

For questions about Cursor rules or suggestions for improvements, please open an issue or discuss in the project's communication channels.
