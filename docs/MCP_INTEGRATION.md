# MCP Integration Guide

Model Context Protocol (MCP) server integration for enhanced development workflow.

## Overview

The traffic simulator includes a comprehensive MCP server that provides streamlined Git operations and task execution, integrating with the existing Bazel/uv/task workflow.

## Features

### Git Tools
- **`git_status`** - Get current repository status
- **`git_sync`** - Sync with remote (pull/push with conflict resolution)
- **`git_commit_workflow`** - Complete commit workflow with staging and validation
- **`git_diff`** - Get diff for specified paths or all changes

### Task Tools
- **`run_quality`** - Quality analysis with Bazel primary, uv fallback
- **`run_tests`** - Test execution with Bazel primary, uv fallback
- **`run_performance`** - Performance benchmarking and scaling analysis
- **`run_analysis`** - Comprehensive analysis combining multiple operations

### Prompt Management Tools
- **`execute_prompt`** - Execute prompts with structured input/output
- **`register_prompt`** - Register new prompts in the registry
- **`get_active_prompt`** - Get active prompt for a mode
- **`optimize_prompts`** - Optimize prompts using meta-optimizer
- **`list_prompts`** - List prompts in the registry
- **`run_continuous_optimization`** - Advanced optimization with DSPy
- **`generate_training_data`** - Generate training data for optimization
- **`evaluate_prompt_performance`** - Evaluate prompt performance

## Installation

```bash
# Install dependencies
cd mcp/
uv sync

# Run server
uv run python mcp_traffic_sim/server.py
```

## Cursor Integration

Add to your Cursor configuration (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "traffic-sim": {
      "command": "/home/gxx/projects/traffic-simulator/venv/bin/python",
      "args": ["/home/gxx/projects/traffic-simulator/mcp/mcp_traffic_sim/server.py"],
      "env": {
        "MCP_REPO_PATH": "/home/gxx/projects/traffic-simulator",
        "MCP_LOG_DIR": "/home/gxx/projects/traffic-simulator/runs/mcp"
      }
    }
  }
}
```

## Configuration

### Environment Variables
- `MCP_REPO_PATH` - Repository path (default: `/home/gxx/projects/traffic-simulator`)
- `MCP_LOG_DIR` - Log directory (default: `runs/mcp/`)
- `MCP_CONFIRM_REQUIRED` - Require confirmation for operations (default: `true`)
- `MCP_MAX_TIMEOUT_S` - Maximum timeout for operations (default: `300`)

### Config File (`config/mcp.yaml`)
```yaml
git:
  conventional_commits: true
  branch_naming: "^feat/|^fix/|^docs/|^style/|^refactor/|^test/|^chore/"
  auto_conflict_resolution: true

tasks:
  bazel_timeout: 300
  uv_timeout: 180
  parallel_analysis: true

  fallback_strategy:
    quality: "bazel_fail_to_uv"
    tests: "bazel_fail_to_uv"
    performance: "task_only"

security:
  require_confirmation: true
  max_output_size: 1048576
  redact_tokens: true
```

## Usage Examples

### Git Operations
```python
# Get repository status
result = await git_status()

# Sync with remote
result = await git_sync(pull_first=True, push_after=True, confirm=True)

# Commit workflow
result = await git_commit_workflow(
    message="feat: add new feature",
    paths=["src/new_feature.py"],
    preview=True
)
```

### Task Operations
```python
# Run quality analysis
result = await run_quality(mode="check", fallback_to_uv=False)

# Run tests
result = await run_tests(targets=["//tests:unit_tests"], fallback_to_uv=True)

# Run performance analysis
result = await run_performance(mode="benchmark", duration=60)

# Run comprehensive analysis
result = await run_analysis(
    include_quality=True,
    include_performance=True,
    parallel=True
)
```

## Security Features

- **Path Allowlists**: Git operations restricted to allowed directories
- **Command Validation**: Task commands validated against allowlist
- **Token Redaction**: Sensitive tokens automatically redacted from output
- **Confirmation Required**: Destructive operations require explicit confirmation

## Performance Impact

The MCP server is designed for minimal performance impact:

- **Git Operations**: Use dulwich (pure Python) for fast, local operations
- **Task Execution**: Leverage existing Bazel/uv infrastructure
- **Parallel Execution**: `run_analysis()` can execute multiple operations simultaneously
- **Smart Caching**: Git operations cache repository state between calls
- **Timeout Management**: Proper timeouts prevent hanging operations

### Performance Metrics
- **Git Operations**: <100ms for status, <500ms for complex operations
- **Task Execution**: Same performance as direct Bazel/uv execution
- **Memory Usage**: <50MB additional memory footprint
- **Logging Overhead**: <1ms per operation

## Advanced Configuration

### Custom Allowlists
```yaml
git:
  allowlist_paths: ["src/", "config/", "docs/", "scripts/", "tests/"]

tasks:
  allowlist_commands:
    - "bazel build"
    - "bazel test"
    - "bazel run"
    - "uv run pytest"
    - "uv run pre-commit"
    - "task quality"
    - "task performance"
    - "task profile"
```

### Security Policies
```yaml
security:
  require_confirmation: true
  max_output_size: 1048576
  redact_tokens: true
  timeout_seconds: 300
  allow_destructive_operations: false
```

## Troubleshooting

### Common Issues

**MCP Server Not Starting**
- Verify Python path in `.cursor/mcp.json`
- Check virtual environment activation
- Review logs in `runs/mcp/` directory

**Tool Execution Failures**
- Verify repository path configuration
- Check command allowlists in `config/mcp.yaml`
- Review security constraints

**Performance Issues**
- Monitor logs in `runs/mcp/` for timing information
- Check timeout settings in configuration
- Verify parallel execution is enabled for `run_analysis()`

### Debug Mode
```bash
# Enable debug logging
export MCP_DEBUG=true
uv run python mcp_traffic_sim/server.py
```

## Testing

The MCP server includes comprehensive testing:

```bash
# Run MCP server tests
cd mcp/
uv run pytest mcp_traffic_sim/tests/ -v

# Run with coverage
uv run pytest mcp_traffic_sim/tests/ --cov=mcp_traffic_sim --cov-report=html
```

### Test Coverage
- **Git Operations**: Unit tests with temporary repositories
- **Task Execution**: Mock subprocess calls for deterministic testing
- **Security**: Test allowlist enforcement and validation
- **Integration**: End-to-end testing with Cursor

## Architecture

The MCP server follows a clean, modular architecture:

```
mcp/
├── mcp_traffic_sim/
│   ├── server.py              # MCP server entrypoint
│   ├── config.py              # Configuration management
│   ├── security.py            # Security and allowlists
│   ├── logging_util.py         # Structured logging
│   ├── git/                   # Git operations with dulwich
│   ├── tasks/                 # Task execution with Bazel/uv
│   └── tests/                 # Comprehensive test suite
└── pyproject.toml             # Package configuration
```

## Dependencies

- `modelcontextprotocol` - Official MCP Python SDK
- `dulwich` - Pure Python Git implementation
- `pydantic` - Data validation and serialization
- `psutil` - Process management and timeouts
- `pyyaml` - Configuration file support

## Development

The MCP server is designed to integrate seamlessly with the existing project workflow:

- **Primary**: Bazel operations (95% of workflow)
- **Fallback**: uv operations for debugging (5% of workflow)
- **Artifacts**: All outputs captured to `runs/` directory
- **Logging**: Structured logs for audit and debugging
- **Security**: Allowlists and validation for safe operation

## Reference

- [Development Guide](mdc:docs/DEVELOPMENT.md) - General development workflow
- [Architecture Guide](mdc:docs/ARCHITECTURE.md) - System architecture overview
- [Quality Standards](mdc:docs/QUALITY_STANDARDS.md) - Code quality guidelines
- [Performance Guide](mdc:docs/PERFORMANCE_GUIDE.md) - Performance optimization
