# Enforcement Troubleshooting Guide

This guide helps resolve common issues with commit message format, documentation, and rules enforcement.

## Commit Message Issues

### Problem: Commit Message Rejected
**Error**: `subject may not be empty [subject-empty]` or `type may not be empty [type-empty]`

**Solution**: Use conventional commit format:
```bash
# ✅ Good examples
feat: add support for vehicle physics optimization
fix(rendering): resolve HUD occlusion calculation bug
docs: update performance guide with new benchmarks

# ❌ Bad examples
invalid commit message
Add feature
Fix bug
```

### Problem: Commit Message Too Long
**Error**: `subject-max-length` or `body-max-line-length`

**Solution**:
- Keep subject under 72 characters
- Keep body lines under 100 characters
- Use body for detailed explanations

### Problem: Invalid Commit Type
**Error**: `type-enum` validation failed

**Solution**: Use only allowed types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

## Documentation Issues

### Problem: Markdown Linting Errors
**Error**: `MD013/line-length` or `MD022/blanks-around-headings`

**Solution**:
```bash
# Check specific file
npx markdownlint docs/DEVELOPMENT.md

# Fix automatically (if possible)
npx markdownlint docs/DEVELOPMENT.md --fix
```

### Problem: Broken Links
**Error**: `markdown-link-check` finds broken links

**Solution**:
```bash
# Check all documentation links
npx markdown-link-check docs/**/*.md

# Check specific file
npx markdown-link-check docs/DEVELOPMENT.md
```

### Problem: Spelling Errors
**Error**: `cspell` finds unknown words

**Solution**:
```bash
# Check spelling
npx cspell "docs/**/*.md"

# Add words to dictionary (config/cspell.json)
# Update the "words" array with technical terms
```

## Rules Issues

### Problem: Rules Validation Failed
**Error**: `Missing required field: globs` or `Invalid YAML in frontmatter`

**Solution**:
```bash
# Check rules validation
python3 scripts/validate_rules.py

# Fix frontmatter format
# Ensure all rules have:
# - globs: "**" or ["pattern1", "pattern2"]
# - description: "Brief description"
# - alwaysApply: true or false
```

### Problem: Too Many Global Rules
**Error**: `Too many global rules: 6 (max 5)`

**Solution**:
- Limit global rules (alwaysApply: true) to maximum 5
- Use specific glob patterns instead of "**"
- Consider combining related rules

### Problem: Rule Content Too Long
**Error**: `Rule content may exceed token limit`

**Solution**:
- Keep rules under 900 tokens (~2000 characters)
- Use references instead of duplicating content
- Focus on essential patterns only

## Pre-commit Hook Issues

### Problem: Hooks Not Running
**Error**: Pre-commit hooks not executing

**Solution**:
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run commitlint
```

### Problem: Hook Timeout
**Error**: `timeout 30` exceeded

**Solution**:
- Check for infinite loops in scripts
- Optimize validation scripts
- Increase timeout if necessary

### Problem: Node.js Dependencies Missing
**Error**: `Cannot find module` or `npm` not found

**Solution**:
```bash
# Install dependencies
npm install

# Check if tools are available
npx commitlint --version
npx markdownlint --version
npx cspell --version
```

## Quality Gates Issues

### Problem: Quality Gates Failing
**Error**: Quality gates not passing

**Solution**:
```bash
# Run quality gates manually
bazel build //...

# Check specific tool
uv run pyright --stats
uv run ruff check src/
uv run bandit -r src/ -c config/bandit.yaml
```

### Problem: Documentation Requirements Not Met
**Error**: Documentation quality gates failing

**Solution**:
- Enable documentation requirements in `config/quality_gates.yaml`
- Add docstrings to public APIs
- Ensure type hints are present
- Run documentation validation

## Common Solutions

### Reset All Enforcement
```bash
# Reinstall pre-commit hooks
uv run pre-commit uninstall
uv run pre-commit install

# Reinstall npm dependencies
rm -rf node_modules package-lock.json
npm install

# Run all validation
uv run pre-commit run --all-files
```

### Bypass Enforcement (Emergency)
```bash
# Skip pre-commit hooks (not recommended)
git commit --no-verify -m "emergency: bypass enforcement"

# Skip specific hook
SKIP=commitlint git commit -m "feat: add feature"
```

### Debug Mode
```bash
# Run with verbose output
uv run pre-commit run --all-files --verbose

# Check hook configuration
uv run pre-commit run --all-files --show-diff-on-failure
```

## Getting Help

### Resources
- **Commit Messages**: [Conventional Commits](https://www.conventionalcommits.org/)
- **Markdown**: [Markdownlint Rules](https://github.com/DavidAnson/markdownlint)
- **Spelling**: [CSpell Configuration](https://cspell.org/configuration/)
- **Rules**: [Cursor Rules Guide](docs/CURSOR_RULES.md)

### Support
- Check this troubleshooting guide first
- Review error messages carefully
- Test individual tools separately
- Check configuration files for syntax errors

---

*This troubleshooting guide is updated as new issues are discovered and resolved.*
