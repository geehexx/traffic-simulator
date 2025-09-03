# FastMCP Integration Guide

Comprehensive guide for integrating and using the FastMCP Traffic Simulator Optimization Platform.

## 🚀 Quick Integration

### 1. Basic Setup
```bash
# Navigate to MCP directory
cd /home/gxx/projects/traffic-simulator/mcp

# Activate virtual environment
source .venv/bin/activate

# Start FastMCP server
python3 fastmcp_test_server.py
```

### 2. Cursor Configuration
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

## 📋 Tool Reference

### System Monitoring Tools

#### `get_status`
Get system health and performance metrics.
```python
mcp_fastmcp-test_get_status(
    include_metrics=True,
    include_optimization_status=True
)
```

**Parameters:**
- `include_metrics` (bool): Include performance metrics
- `include_optimization_status` (bool): Include optimization status

**Returns:**
- System health status
- Performance metrics
- Optimization statistics

#### `get_analytics`
Get comprehensive optimization analytics.
```python
mcp_fastmcp-test_get_analytics(
    prompt_id="generate_docs",
    metric_types=["quality", "performance"],
    include_trends=True
)
```

**Parameters:**
- `prompt_id` (str, optional): Specific prompt ID
- `metric_types` (list, optional): Types of metrics to include
- `include_trends` (bool): Include trend analysis

**Returns:**
- Quality metrics
- Performance metrics
- Optimization trends

#### `get_dashboard`
Get comprehensive optimization dashboard.
```python
mcp_fastmcp-test_get_dashboard(
    include_metrics=True,
    include_alerts=True
)
```

**Parameters:**
- `include_metrics` (bool): Include performance metrics
- `include_alerts` (bool): Include alert information

**Returns:**
- Dashboard overview
- Performance metrics
- Active alerts
- Trend analysis

### Optimization Tools

#### `optimize_prompt`
Optimize a prompt using DSPy.
```python
mcp_fastmcp-test_optimize_prompt(
    prompt_id="generate_docs",
    strategy="hybrid",
    auto_mode=False
)
```

**Parameters:**
- `prompt_id` (str): ID of prompt to optimize
- `strategy` (str): Optimization strategy
- `auto_mode` (bool): Enable automatic optimization

**Returns:**
- Optimization results
- Improvement score
- Execution time

#### `auto_optimize_feedback`
Auto-optimize based on user feedback.
```python
mcp_fastmcp-test_auto_optimize_feedback(
    prompt_id="generate_docs",
    feedback_data={
        "quality_score": 0.8,
        "user_satisfaction": 0.7,
        "suggestions": ["Add more examples"]
    }
)
```

**Parameters:**
- `prompt_id` (str): ID of prompt to optimize
- `feedback_data` (dict): User feedback data

**Returns:**
- Auto-optimization results
- Applied improvements
- Feedback analysis

#### `evaluate_performance`
Evaluate prompt performance with test cases.
```python
mcp_fastmcp-test_evaluate_performance(
    prompt_id="generate_docs",
    test_cases=["test_case_1", "test_case_2"]
)
```

**Parameters:**
- `prompt_id` (str): ID of prompt to evaluate
- `test_cases` (list, optional): Test cases to run

**Returns:**
- Performance evaluation
- Accuracy scores
- Response times
- Recommendations

#### `run_improvement_cycle`
Run automated improvement cycle.
```python
mcp_fastmcp-test_run_improvement_cycle(
    prompt_id="generate_docs",
    iterations=3
)
```

**Parameters:**
- `prompt_id` (str): ID of prompt to improve
- `iterations` (int): Number of improvement iterations

**Returns:**
- Improvement cycle results
- Total improvement
- Optimization history

### Production Management Tools

#### `configure_alerts`
Configure monitoring alerts and thresholds.
```python
mcp_fastmcp-test_configure_alerts(
    alert_types=["quality_drop", "performance_issue"],
    thresholds={"quality": 0.8, "performance": 0.7}
)
```

**Parameters:**
- `alert_types` (list, optional): Types of alerts to configure
- `thresholds` (dict, optional): Alert thresholds

**Returns:**
- Alert configuration
- Threshold settings
- Notification status

#### `deploy_prompts`
Deploy optimized prompts to production.
```python
mcp_fastmcp-test_deploy_prompts(
    prompt_ids=["generate_docs_optimized_v1"],
    environment="production"
)
```

**Parameters:**
- `prompt_ids` (list): IDs of prompts to deploy
- `environment` (str): Target environment

**Returns:**
- Deployment status
- Deployment details
- Rollback availability

## 🔄 Common Workflows

### Basic Optimization Workflow
```python
# 1. Check system status
status = mcp_fastmcp-test_get_status(include_metrics=True)

# 2. Optimize prompt
optimization = mcp_fastmcp-test_optimize_prompt(
    prompt_id="generate_docs",
    strategy="hybrid"
)

# 3. Evaluate performance
evaluation = mcp_fastmcp-test_evaluate_performance(
    prompt_id="generate_docs_optimized_v1"
)

# 4. Deploy to production
deployment = mcp_fastmcp-test_deploy_prompts(
    prompt_ids=["generate_docs_optimized_v1"]
)
```

### Advanced Optimization Workflow
```python
# 1. Configure monitoring
mcp_fastmcp-test_configure_alerts(
    alert_types=["quality_drop", "performance_issue"],
    thresholds={"quality": 0.8, "performance": 0.7}
)

# 2. Run improvement cycle
improvement = mcp_fastmcp-test_run_improvement_cycle(
    prompt_id="generate_docs",
    iterations=5
)

# 3. Auto-optimize with feedback
auto_optimization = mcp_fastmcp-test_auto_optimize_feedback(
    prompt_id="generate_docs",
    feedback_data={
        "quality_score": 0.8,
        "user_satisfaction": 0.7,
        "suggestions": ["Add more examples"]
    }
)

# 4. Get analytics
analytics = mcp_fastmcp-test_get_analytics(
    prompt_id="generate_docs",
    include_trends=True
)

# 5. Check dashboard
dashboard = mcp_fastmcp-test_get_dashboard(
    include_metrics=True,
    include_alerts=True
)
```

### Monitoring and Maintenance Workflow
```python
# 1. Check system health
status = mcp_fastmcp-test_get_status(
    include_metrics=True,
    include_optimization_status=True
)

# 2. Review analytics
analytics = mcp_fastmcp-test_get_analytics(
    metric_types=["quality", "performance", "optimization_frequency"],
    include_trends=True
)

# 3. Check dashboard
dashboard = mcp_fastmcp-test_get_dashboard(
    include_metrics=True,
    include_alerts=True
)

# 4. Configure alerts if needed
mcp_fastmcp-test_configure_alerts(
    alert_types=["quality_drop", "performance_issue"],
    thresholds={"quality": 0.8, "performance": 0.7}
)
```

## 🛠️ Advanced Features

### Machine Learning Optimization
```python
# Use advanced optimization features
from advanced_optimization import AdvancedOptimizer

optimizer = AdvancedOptimizer(Path("/home/gxx/projects/traffic-simulator/runs/mcp"))

# ML-based optimization
ml_result = optimizer.optimize_with_ml("test_prompt", "ml_hybrid")

# Batch optimization
batch_result = optimizer.batch_optimize(["prompt1", "prompt2", "prompt3"])

# Adaptive optimization
adaptive_result = optimizer.adaptive_optimization("test_prompt", {
    "quality_score": 0.6,
    "user_satisfaction": 0.7
})
```

### Performance Monitoring
```python
# Use monitoring dashboard
from monitoring_dashboard import MonitoringDashboard

dashboard = MonitoringDashboard(Path("/home/gxx/projects/traffic-simulator/runs/mcp"))

# Log optimization events
dashboard.log_optimization("test_prompt", "hybrid", 0.15)

# Log performance evaluations
dashboard.log_performance_evaluation("test_prompt", 0.92, 1.2)

# Get performance summary
summary = dashboard.get_performance_summary()

# Get active alerts
alerts = dashboard.get_active_alerts()
```

## 🔧 Troubleshooting

### Common Issues

#### Tool Not Found
```bash
# Check if FastMCP server is running
ps aux | grep fastmcp

# Restart server if needed
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 fastmcp_test_server.py
```

#### Connection Issues
```bash
# Check Cursor configuration
cat .cursor/mcp.json

# Verify server path
ls -la /home/gxx/projects/traffic-simulator/mcp/fastmcp_test_server.py

# Test server manually
python3 fastmcp_test_server.py
```

#### Performance Issues
```python
# Check system status
mcp_fastmcp-test_get_status(include_metrics=True)

# Review analytics
mcp_fastmcp-test_get_analytics(include_trends=True)

# Check dashboard
mcp_fastmcp-test_get_dashboard(include_metrics=True, include_alerts=True)
```

### Debug Mode
```bash
# Run server with debug output
python3 fastmcp_test_server.py --debug

# Check logs
tail -f /home/gxx/projects/traffic-simulator/runs/mcp/server.log
```

## 📊 Performance Optimization

### Best Practices
1. **Regular Monitoring** - Use dashboard and analytics tools
2. **Incremental Optimization** - Start with small improvements
3. **Performance Testing** - Evaluate before production deployment
4. **Alert Configuration** - Set up appropriate monitoring thresholds

### Optimization Strategies
- **Hybrid Strategy** - Combines multiple optimization approaches
- **ML-based Strategy** - Uses machine learning for optimization
- **Adaptive Strategy** - Adapts based on user feedback
- **Batch Strategy** - Optimizes multiple prompts together

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
```bash
# Install service
sudo cp runs/mcp/traffic-sim-fastmcp.service /etc/systemd/system/
sudo systemctl enable traffic-sim-fastmcp
sudo systemctl start traffic-sim-fastmcp

# Check status
sudo systemctl status traffic-sim-fastmcp
```

## 📈 Scaling and Performance

### High-Performance Configuration
```python
# Configure for high performance
mcp_fastmcp-test_configure_alerts(
    alert_types=["performance_issue", "optimization_failure"],
    thresholds={"performance": 0.9, "success_rate": 0.95}
)

# Use batch optimization for multiple prompts
mcp_fastmcp-test_run_improvement_cycle(
    prompt_id="batch_optimization",
    iterations=10
)
```

### Monitoring and Alerting
```python
# Set up comprehensive monitoring
mcp_fastmcp-test_configure_alerts(
    alert_types=[
        "quality_drop",
        "performance_issue",
        "optimization_failure",
        "user_feedback"
    ],
    thresholds={
        "quality": 0.8,
        "performance": 0.7,
        "success_rate": 0.9
    }
)
```

## 🤝 Support and Community

### Getting Help
1. **Check Documentation** - Review this guide and README
2. **Test Tools** - Use monitoring tools to diagnose issues
3. **Review Logs** - Check server and application logs
4. **Community Support** - FastMCP community and documentation

### Contributing
1. **Fork Repository** - Create your own fork
2. **Create Branch** - Work on feature branch
3. **Test Changes** - Ensure all tests pass
4. **Submit PR** - Create pull request with changes

## 📄 License and Legal

This project is licensed under the MIT License. See LICENSE file for details.

## 🎯 Roadmap and Future

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
