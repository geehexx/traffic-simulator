# Cursor Rules Guide

This document provides comprehensive guidance on the Cursor rules system used in the traffic simulator project for maintaining code quality and development consistency.

## Table of Contents
- [Overview](#overview)
- [Rule Categories](#rule-categories)
- [Rule Usage](#rule-usage)
- [Rule Maintenance](#rule-maintenance)
- [Best Practices](#best-practices)

## Overview

The project uses 20+ specialized Cursor rules to provide AI-assisted development guidance. These rules are stored in `.cursor/rules/` and cover various aspects of development including code quality, architecture patterns, and project-specific guidelines.

## Rule Categories

### 1. Code Quality Standards
- **arcade-api-consistency.mdc**: Arcade API compatibility and validation
- **code-quality-standards.mdc**: Core code quality guidelines
- **coding-standards.mdc**: General coding standards and patterns
- **static-analysis-standards.mdc**: Static analysis tool configuration

### 2. Architecture & Patterns
- **simulation-patterns.mdc**: Core simulation architecture patterns
- **rendering-patterns.mdc**: Arcade rendering guidelines
- **driver-vehicle-dynamics.mdc**: Driver and vehicle behavior patterns
- **perception-system.mdc**: Perception and SSD calculation patterns

### 3. Performance & Optimization
- **performance-standards.mdc**: Performance optimization guidelines
- **performance-optimization.mdc**: Performance tuning strategies
- **performance-targets.mdc**: Performance target definitions

### 4. Configuration & Management
- **configuration-patterns.mdc**: Configuration management patterns
- **configuration-management.mdc**: Configuration handling guidelines

### 5. Testing & Quality
- **testing-patterns.mdc**: Testing strategy and patterns
- **testing-standards.mdc**: Testing quality standards
- **quality-gates-enforcement.mdc**: Quality gates implementation

### 6. Documentation
- **documentation-patterns.mdc**: Documentation standards
- **documentation-standards.mdc**: Documentation quality guidelines

### 7. Development Workflow
- **development-workflow.mdc**: Development process guidelines
- **workflow.mdc**: Workflow optimization
- **handoff-guide.mdc**: Project handoff procedures

### 8. Project Context
- **project-context.mdc**: Project overview and context
- **project-structure.mdc**: Project organization guidelines
- **project-overview.mdc**: High-level project understanding

### 9. Specialized Rules
- **determinism-contracts.mdc**: Deterministic behavior requirements
- **rendering-arcade-compat.mdc**: Arcade compatibility guidelines
- **idm-controller.mdc**: IDM controller implementation
- **hud-development.mdc**: HUD development guidelines

## Rule Usage

### Activating Rules
Rules are automatically loaded by Cursor when working in the project. They provide context-aware suggestions and guidance during development.

### Rule Selection
The system uses intelligent rule selection based on:
- File context (e.g., simulation files trigger simulation-patterns)
- Code patterns (e.g., performance-critical code triggers performance rules)
- Development phase (e.g., testing triggers testing-patterns)

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
- Performance metrics
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

### Getting Help
- Check rule documentation
- Review project guidelines
- Consult with team members
- Open issues for rule improvements

## Future Enhancements

Planned improvements to the rule system:
- Dynamic rule loading based on context
- Machine learning-based rule optimization
- Integration with external quality tools
- Enhanced rule performance metrics

For questions about Cursor rules or suggestions for improvements, please open an issue or discuss in the project's communication channels.
