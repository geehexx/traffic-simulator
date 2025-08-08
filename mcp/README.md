# Traffic Simulator MCP Server

Model Context Protocol (MCP) server for traffic simulator Git and task operations.

## Overview

This MCP server provides streamlined Git operations and task execution for the traffic simulator project, integrating with the existing Bazel/uv/task workflow.

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

## Installation

The MCP server is designed to run in the project's virtual environment:

```bash
# Install dependencies
cd mcp/
uv sync

# Run server
uv run python mcp_traffic_sim/server.py
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

security:
  require_confirmation: true
  max_output_size: 1048576
  redact_tokens: true
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

- **Path Allowlists** - Git operations restricted to allowed directories
- **Command Validation** - Task commands validated against allowlist
- **Token Redaction** - Sensitive tokens automatically redacted from output
- **Output Truncation** - Large outputs truncated to prevent context overflow
- **Confirmation Required** - Destructive operations require explicit confirmation

## Logging

All operations are logged to `runs/mcp/` with structured JSON logs:
- Daily log files per tool type
- Operation parameters and results
- Error tracking and debugging information
- Performance metrics and timing

## Testing

Run tests with pytest:

```bash
cd mcp/
uv run pytest mcp_traffic_sim/tests/ -v
```

## Architecture

```
mcp/
├── mcp_traffic_sim/
│   ├── server.py              # MCP server entrypoint
│   ├── config.py              # Configuration management
│   ├── security.py            # Security and allowlists
│   ├── logging_util.py         # Structured logging
│   ├── git/
│   │   ├── adapter.py         # Dulwich-based Git operations
│   │   ├── tools.py           # Git MCP tool handlers
│   │   └── schemas.py         # Git data models
│   ├── tasks/
│   │   ├── bazel_runner.py    # Bazel command execution
│   │   ├── uv_runner.py       # uv command execution
│   │   ├── tools.py           # Task MCP tool handlers
│   │   └── schemas.py         # Task data models
│   └── tests/                 # Test suite
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
