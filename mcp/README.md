# FastMCP Traffic Simulator Optimization Platform

A production-ready AI prompt optimization platform built with FastMCP, providing comprehensive tools for prompt optimization, performance monitoring, and production deployment.

## 🚀 Features

### Core Optimization Tools
- **Prompt Optimization** - DSPy-based AI prompt improvement
- **Performance Evaluation** - Comprehensive testing and validation
- **Automated Cycles** - Multi-iteration optimization processes
- **User Feedback Integration** - Continuous optimization based on feedback

### Production Management
- **System Monitoring** - Real-time health and performance tracking
- **Analytics Dashboard** - Comprehensive optimization insights
- **Alert Configuration** - Customizable monitoring and thresholds
- **Production Deployment** - Safe deployment with rollback capability

### Advanced Features
- **Auto-Optimization** - Feedback-driven automatic improvements
- **Performance Monitoring** - Real-time metrics and alerting
- **Deployment Management** - Production-ready deployment workflows
- **Analytics & Reporting** - Detailed performance analytics

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd traffic-simulator/mcp

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install fastmcp --break-system-packages

# Install FastMCP in virtual environment
pip install fastmcp
```

## 🚀 Quick Start

### 1. Start the FastMCP Server
```bash
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 fastmcp_test_server.py
```

### 2. Configure Cursor
Update `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "fastmcp-test": {
      "command": "/home/gxx/projects/traffic-simulator/mcp/.venv/bin/python",
      "args": ["/home/gxx/projects/traffic-simulator/mcp/fastmcp_test_server.py"],
      "cwd": "/home/gxx/projects/traffic-simulator/mcp",
      "env": {
        "MCP_REPO_PATH": "/home/gxx/projects/traffic-simulator",
        "MCP_LOG_DIR": "/home/gxx/projects/traffic-simulator/runs/mcp"
      }
    }
  }
}
```

### 3. Restart Cursor
Restart Cursor to pick up the FastMCP server configuration.

## 📋 Available Tools

### Basic Operations
- **`get_status`** - System health and metrics monitoring
- **`get_analytics`** - Performance analytics and trends
- **`get_dashboard`** - Comprehensive optimization overview

### Optimization Tools
- **`optimize_prompt`** - DSPy-based AI prompt optimization
- **`auto_optimize_feedback`** - User feedback-driven optimization
- **`evaluate_performance`** - Performance testing and evaluation
- **`run_improvement_cycle`** - Automated multi-iteration optimization

### Production Management
- **`configure_alerts`** - Monitoring and alert configuration
- **`deploy_prompts`** - Production deployment with rollback

## 🔧 Usage Examples

### Basic Optimization Workflow
```python
# 1. Check system status
mcp_fastmcp-test_get_status(include_metrics=True, include_optimization_status=True)

# 2. Optimize a prompt
mcp_fastmcp-test_optimize_prompt(
    prompt_id="generate_docs",
    strategy="hybrid",
    auto_mode=False
)

# 3. Evaluate performance
mcp_fastmcp-test_evaluate_performance(
    prompt_id="generate_docs_optimized_v1",
    test_cases=["test_case_1", "test_case_2"]
)

# 4. Deploy to production
mcp_fastmcp-test_deploy_prompts(
    prompt_ids=["generate_docs_optimized_v1"],
    environment="production"
)
```

### Advanced Optimization
```python
# Run improvement cycle
mcp_fastmcp-test_run_improvement_cycle(
    prompt_id="generate_docs",
    iterations=5
)

# Configure monitoring alerts
mcp_fastmcp-test_configure_alerts(
    alert_types=["quality_drop", "performance_issue"],
    thresholds={"quality": 0.8, "performance": 0.7}
)

# Auto-optimize based on feedback
mcp_fastmcp-test_auto_optimize_feedback(
    prompt_id="generate_docs",
    feedback_data={
        "quality_score": 0.8,
        "user_satisfaction": 0.7,
        "suggestions": ["Add more examples", "Improve clarity"]
    }
)
```

## 📊 Monitoring & Analytics

### Performance Dashboard
The system provides comprehensive monitoring through:
- **Real-time Metrics** - System health and performance indicators
- **Optimization Analytics** - Success rates and improvement tracking
- **Alert System** - Configurable thresholds and notifications
- **Deployment Tracking** - Production deployment monitoring

### Monitoring Tools
```python
# Get system status
mcp_fastmcp-test_get_status(include_metrics=True)

# View analytics
mcp_fastmcp-test_get_analytics(
    prompt_id="generate_docs",
    metric_types=["quality", "performance"],
    include_trends=True
)

# Check dashboard
mcp_fastmcp-test_get_dashboard(include_metrics=True, include_alerts=True)
```

## 🚀 Production Deployment

### Automated Deployment
```bash
# Run deployment script
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 deploy_production.py
```

### Manual Deployment
1. **Configure Environment** - Set up production environment variables
2. **Deploy Server** - Copy FastMCP server to production location
3. **Configure Monitoring** - Set up alerting and monitoring
4. **Test Deployment** - Verify all tools are working correctly

### Systemd Service
The deployment script creates a systemd service file for production deployment:
```bash
# Install service
sudo cp runs/mcp/traffic-sim-fastmcp.service /etc/systemd/system/
sudo systemctl enable traffic-sim-fastmcp
sudo systemctl start traffic-sim-fastmcp
```

## 🔍 Troubleshooting

### Common Issues

#### FastMCP Server Not Starting
```bash
# Check virtual environment
source .venv/bin/activate
python3 -c "import fastmcp; print('FastMCP installed')"

# Test server manually
python3 fastmcp_test_server.py
```

#### Cursor Not Connecting
1. **Check Configuration** - Verify `.cursor/mcp.json` is correct
2. **Restart Cursor** - Full restart required for MCP changes
3. **Check Logs** - Review server logs for errors

#### Tool Not Found
1. **Verify Server Running** - Check if FastMCP server is active
2. **Check Tool Names** - Ensure correct tool naming convention
3. **Restart Services** - Restart both server and Cursor

### Debug Mode
```bash
# Run server with debug output
python3 fastmcp_test_server.py --debug

# Check server logs
tail -f runs/mcp/server.log
```

## 📈 Performance Optimization

### Best Practices
1. **Regular Monitoring** - Use dashboard and analytics tools
2. **Incremental Optimization** - Start with small improvements
3. **Performance Testing** - Evaluate before production deployment
4. **Alert Configuration** - Set up appropriate monitoring thresholds

### Optimization Strategies
- **Hybrid Strategy** - Combines multiple optimization approaches
- **Feedback Integration** - Use user feedback for continuous improvement
- **Automated Cycles** - Run multi-iteration optimization processes
- **Performance Evaluation** - Regular testing and validation

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd traffic-simulator/mcp

# Create development environment
python3 -m venv .venv
source .venv/bin/activate
pip install fastmcp

# Run tests
python3 monitoring_dashboard.py
```

### Adding New Tools
1. **Define Tool Function** - Add new tool to `fastmcp_test_server.py`
2. **Test Tool** - Verify tool works correctly
3. **Update Documentation** - Add tool to README and examples
4. **Deploy Changes** - Update production deployment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. **Check Documentation** - Review this README and code comments
2. **Test Tools** - Use monitoring tools to diagnose issues
3. **Review Logs** - Check server and application logs
4. **Community Support** - FastMCP community and documentation

## 🎯 Roadmap

### Planned Features
- **Advanced Analytics** - Machine learning-based optimization insights
- **Integration APIs** - REST API for external integrations
- **Batch Processing** - Bulk optimization capabilities
- **Custom Strategies** - User-defined optimization strategies

### Future Enhancements
- **Multi-Environment Support** - Development, staging, production
- **Advanced Monitoring** - Real-time dashboards and alerting
- **Performance Optimization** - Server and tool performance improvements
- **Extensibility** - Plugin system for custom tools and strategies
