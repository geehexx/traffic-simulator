# 🛠️ MCP Tool Reference Card

## 📋 **Quick Reference for Both Servers**

### **Server 1: `traffic-sim` (Original)**
**Purpose**: Git and Task operations for traffic simulator development

| Tool Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `git_status` | Get repository status | `repo_path` (optional) |
| `git_sync` | Sync with remote | `repo_path`, `force_push` |
| `git_commit_workflow` | Complete commit workflow | `message`, `paths`, `amend` |
| `git_diff` | Get diff for changes | `paths` (optional) |
| `run_quality` | Quality analysis | `mode`, `fallback_to_uv` |
| `run_tests` | Execute tests | `target`, `fallback_to_uv` |
| `run_performance` | Performance benchmarking | `scenario`, `iterations` |
| `run_analysis` | Comprehensive analysis | `analysis_type`, `full_report` |

### **Server 2: `traffic-sim-production` (DSPy Optimization)**
**Purpose**: Production-grade DSPy optimization and continuous improvement

| Tool Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `optimize_prompt` | Production prompt optimization | `prompt_id`, `strategy`, `training_data` |
| `auto_optimize_feedback` | Real-time feedback optimization | `prompt_id`, `user_feedback`, `feedback_threshold` |
| `evaluate_performance` | Performance evaluation | `prompt_id`, `test_cases`, `evaluation_metrics` |
| `run_improvement_cycle` | Continuous improvement | `prompt_ids`, `strategies`, `auto_deploy` |
| `get_dashboard` | Performance dashboard | `dashboard_type`, `time_range`, `include_predictions` |
| `get_analytics` | Optimization analytics | `prompt_id`, `metric_types`, `include_trends` |
| `configure_alerts` | Alert configuration | `alert_types`, `notification_channels` |
| `get_status` | System status | `include_metrics`, `include_optimization_status` |
| `deploy_prompts` | Deploy optimized prompts | `prompt_ids`, `deployment_strategy`, `rollback_on_failure` |

## 🎯 **Common Use Cases**

### **Daily Development Workflow**
```bash
# 1. Check repository status
git_status

# 2. Run quality checks
run_quality

# 3. Execute tests
run_tests

# 4. Check performance
run_performance
```

### **Prompt Optimization Workflow**
```bash
# 1. Optimize a prompt
optimize_prompt {"prompt_id": "generate_docs", "strategy": "mipro"}

# 2. Check performance dashboard
get_dashboard {"dashboard_type": "overview", "time_range": "24h"}

# 3. Set up monitoring
configure_alerts {"alert_types": [{"type": "performance", "threshold": 0.8}]}

# 4. Deploy optimized prompts
deploy_prompts {"prompt_ids": ["generate_docs_optimized"]}
```

## ⚡ **Quick Commands**

### **Git Operations**
- **Status**: `git_status`
- **Sync**: `git_sync`
- **Commit**: `git_commit_workflow {"message": "Your commit message"}`
- **Diff**: `git_diff`

### **Quality & Testing**
- **Quality Check**: `run_quality`
- **Run Tests**: `run_tests {"target": "//..."}`
- **Performance**: `run_performance {"scenario": "baseline"}`

### **DSPy Optimization**
- **Optimize**: `optimize_prompt {"prompt_id": "your_prompt", "strategy": "mipro"}`
- **Dashboard**: `get_dashboard {"dashboard_type": "overview"}`
- **Status**: `get_status`
- **Deploy**: `deploy_prompts {"prompt_ids": ["your_prompt"]}`

## 🔧 **Tool Name Lengths (Cursor Compatibility)**

| Server | Tool | Total Length | Status |
|--------|------|--------------|--------|
| traffic-sim | git_status | 25 chars | ✅ |
| traffic-sim | run_quality | 28 chars | ✅ |
| traffic-sim | run_tests | 26 chars | ✅ |
| traffic-sim-production | optimize_prompt | 39 chars | ✅ |
| traffic-sim-production | get_dashboard | 35 chars | ✅ |
| traffic-sim-production | get_status | 32 chars | ✅ |
| traffic-sim-production | deploy_prompts | 36 chars | ✅ |

**All tools are well under the 60-character limit! 🎉**

## 📊 **Optimization Strategies**

### **Available Strategies**
- **`mipro`**: MIPROv2 - Advanced joint optimization (recommended)
- **`bootstrap`**: BootstrapFewShot - Few-shot learning
- **`bayesian`**: BootstrapFewShot fallback (Bayesian not available)
- **`hybrid`**: MIPROv2-based hybrid approach

### **Auto Modes**
- **`light`**: Quick optimization (default)
- **`medium`**: Balanced optimization
- **`heavy`**: Comprehensive optimization

## 🚨 **Alert Types**

### **Performance Alerts**
- **Response Time**: > 500ms
- **Error Rate**: > 2%
- **CPU Usage**: > 80%
- **Memory Usage**: > 85%

### **Optimization Alerts**
- **Quality Drop**: > 10% decrease
- **Feedback Volume**: High negative feedback
- **Optimization Failure**: Failed optimization cycles

## 📈 **Dashboard Types**

- **`overview`**: System overview and key metrics
- **`detailed`**: Detailed performance breakdown
- **`trends`**: Historical trends and patterns
- **`alerts`**: Active alerts and notifications

## 🎯 **Best Practices**

### **For Development**
1. Use `traffic-sim` for daily Git and Task operations
2. Run quality checks before committing
3. Test performance regularly
4. Keep documentation updated

### **For Optimization**
1. Start with `mipro` strategy for best results
2. Monitor performance dashboards regularly
3. Set up appropriate alerting thresholds
4. Deploy optimizations gradually

### **For Monitoring**
1. Check system status regularly
2. Review analytics for trends
3. Configure alerts for critical metrics
4. Plan for scalability

## 🚀 **Ready to Use!**

Both MCP servers are configured and ready for use in Cursor. All tools are under the 60-character limit and fully functional. You can now:

- **Develop**: Use `traffic-sim` for Git and Task operations
- **Optimize**: Use `traffic-sim-production` for DSPy optimization
- **Monitor**: Track performance and system health
- **Improve**: Implement continuous optimization cycles

**Your production DSPy optimization system is ready! 🎉**
