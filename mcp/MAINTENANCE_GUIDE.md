# FastMCP Platform Maintenance & Operations Guide

## 🔧 Overview

This guide provides comprehensive maintenance and operations procedures for the FastMCP Traffic Simulator Optimization Platform in production environments.

## 📋 Daily Operations

### **System Health Checks**
```bash
# Check FastMCP server status
ps aux | grep fastmcp

# Check system resources
htop
df -h
free -h

# Check log files
tail -f /home/gxx/projects/traffic-simulator/runs/mcp/server.log
```

### **Performance Monitoring**
```bash
# Run performance check
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 performance_benchmarks.py

# Check continuous monitoring
python3 continuous_monitoring.py
```

### **Alert Management**
```bash
# Check active alerts
python3 -c "
from continuous_monitoring import ContinuousMonitor
from pathlib import Path
monitor = ContinuousMonitor(Path('/home/gxx/projects/traffic-simulator/runs/mcp'))
print(monitor.get_monitoring_status())
"
```

## 🔄 Weekly Maintenance

### **System Updates**
```bash
# Update virtual environment
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
pip install --upgrade fastmcp

# Check for security updates
pip audit
```

### **Log Rotation**
```bash
# Rotate log files
cd /home/gxx/projects/traffic-simulator/runs/mcp
find . -name "*.log" -mtime +7 -delete
find . -name "*.jsonl" -mtime +30 -delete
```

### **Performance Analysis**
```bash
# Run comprehensive tests
python3 test_suite.py

# Generate performance report
python3 performance_benchmarks.py
```

## 🚨 Troubleshooting

### **Common Issues**

#### FastMCP Server Not Starting
```bash
# Check server process
ps aux | grep fastmcp

# Check server logs
tail -f /home/gxx/projects/traffic-simulator/runs/mcp/server.log

# Restart server
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 fastmcp_test_server.py
```

#### High Memory Usage
```bash
# Check memory usage
ps aux --sort=-%mem | head -10

# Check for memory leaks
python3 -c "
import psutil
for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
    if 'python' in proc.info['name'].lower():
        print(f'PID: {proc.info[\"pid\"]}, Memory: {proc.info[\"memory_info\"].rss / 1024 / 1024:.1f}MB')
"
```

#### Performance Issues
```bash
# Run performance diagnostics
python3 performance_benchmarks.py

# Check system resources
htop
iostat 1 5
```

### **Error Resolution**

#### Tool Not Found Errors
1. **Check Cursor Configuration**
   ```bash
   cat .cursor/mcp.json
   ```

2. **Restart Cursor**
   - Close Cursor completely
   - Restart Cursor
   - Check tool availability

3. **Verify Server Status**
   ```bash
   ps aux | grep fastmcp
   ```

#### Connection Issues
1. **Check Server Process**
   ```bash
   ps aux | grep fastmcp
   ```

2. **Check Configuration**
   ```bash
   cat .cursor/mcp.json
   ```

3. **Test Server Manually**
   ```bash
   cd /home/gxx/projects/traffic-simulator/mcp
   source .venv/bin/activate
   python3 fastmcp_test_server.py
   ```

## 📊 Monitoring & Alerting

### **Continuous Monitoring Setup**
```bash
# Start continuous monitoring
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 -c "
from continuous_monitoring import ContinuousMonitor
from pathlib import Path
monitor = ContinuousMonitor(Path('/home/gxx/projects/traffic-simulator/runs/mcp'))
monitor.start_monitoring()
"
```

### **Alert Configuration**
```python
# Configure alerts via FastMCP tools
mcp_fastmcp-test_configure_alerts(
    alert_types=["quality_drop", "performance_issue", "optimization_failure"],
    thresholds={"quality": 0.8, "performance": 0.7, "success_rate": 0.9}
)
```

### **Performance Monitoring**
```bash
# Check system metrics
python3 -c "
from continuous_monitoring import ContinuousMonitor
from pathlib import Path
monitor = ContinuousMonitor(Path('/home/gxx/projects/traffic-simulator/runs/mcp'))
print(monitor.get_metrics_summary(hours=24))
"
```

## 🔄 Backup & Recovery

### **Backup Procedures**
```bash
# Backup configuration
cp .cursor/mcp.json /home/gxx/projects/traffic-simulator/backups/

# Backup logs and metrics
tar -czf /home/gxx/projects/traffic-simulator/backups/mcp_backup_$(date +%Y%m%d).tar.gz \
    /home/gxx/projects/traffic-simulator/runs/mcp/
```

### **Recovery Procedures**
```bash
# Restore from backup
tar -xzf /home/gxx/projects/traffic-simulator/backups/mcp_backup_YYYYMMDD.tar.gz

# Restart services
systemctl restart traffic-sim-fastmcp
```

## 🚀 Production Deployment

### **Deployment Checklist**
- [ ] **System Requirements Met**
  - Python 3.10+ installed
  - Virtual environment configured
  - FastMCP installed and working

- [ ] **Configuration Complete**
  - `.cursor/mcp.json` configured
  - Environment variables set
  - Log directories created

- [ ] **Testing Completed**
  - Test suite passed (94.1% success rate)
  - Performance benchmarks passed (80% success rate)
  - Production validation passed (100% success rate)

- [ ] **Monitoring Setup**
  - Continuous monitoring configured
  - Alert thresholds set
  - Performance tracking active

### **Deployment Commands**
```bash
# Run deployment script
cd /home/gxx/projects/traffic-simulator/mcp
source .venv/bin/activate
python3 deploy_production.py

# Install systemd service
sudo cp runs/mcp/traffic-sim-fastmcp.service /etc/systemd/system/
sudo systemctl enable traffic-sim-fastmcp
sudo systemctl start traffic-sim-fastmcp
```

## 📈 Performance Optimization

### **System Optimization**
```bash
# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONUNBUFFERED=1

# Optimize memory usage
export MALLOC_ARENA_MAX=2
```

### **Application Optimization**
```python
# Configure for high performance
mcp_fastmcp-test_configure_alerts(
    alert_types=["performance_issue"],
    thresholds={"performance": 0.9}
)

# Use batch optimization for multiple prompts
mcp_fastmcp-test_run_improvement_cycle(
    prompt_id="batch_optimization",
    iterations=10
)
```

## 🔒 Security

### **Security Checklist**
- [ ] **Access Control**
  - File permissions properly set
  - User access restricted
  - Service account configured

- [ ] **Network Security**
  - Firewall rules configured
  - Network access restricted
  - SSL/TLS enabled if applicable

- [ ] **Data Protection**
  - Log files secured
  - Sensitive data encrypted
  - Backup encryption enabled

### **Security Commands**
```bash
# Check file permissions
ls -la /home/gxx/projects/traffic-simulator/mcp/

# Check process security
ps aux | grep fastmcp

# Check network connections
netstat -tlnp | grep python
```

## 📋 Maintenance Schedule

### **Daily Tasks**
- [ ] Check system health
- [ ] Monitor performance metrics
- [ ] Review alert notifications
- [ ] Check log files for errors

### **Weekly Tasks**
- [ ] Run comprehensive tests
- [ ] Update dependencies
- [ ] Rotate log files
- [ ] Performance analysis

### **Monthly Tasks**
- [ ] Security audit
- [ ] Performance optimization
- [ ] Backup verification
- [ ] Documentation updates

## 🆘 Emergency Procedures

### **System Down**
1. **Check Process Status**
   ```bash
   ps aux | grep fastmcp
   ```

2. **Restart Services**
   ```bash
   systemctl restart traffic-sim-fastmcp
   ```

3. **Check Logs**
   ```bash
   journalctl -u traffic-sim-fastmcp
   ```

### **Performance Degradation**
1. **Check System Resources**
   ```bash
   htop
   df -h
   ```

2. **Run Performance Tests**
   ```bash
   python3 performance_benchmarks.py
   ```

3. **Optimize Configuration**
   ```bash
   python3 continuous_monitoring.py
   ```

### **Data Loss**
1. **Check Backups**
   ```bash
   ls -la /home/gxx/projects/traffic-simulator/backups/
   ```

2. **Restore from Backup**
   ```bash
   tar -xzf /home/gxx/projects/traffic-simulator/backups/mcp_backup_YYYYMMDD.tar.gz
   ```

3. **Restart Services**
   ```bash
   systemctl restart traffic-sim-fastmcp
   ```

## 📞 Support Contacts

### **Technical Support**
- **Documentation:** README.md, INTEGRATION_GUIDE.md
- **Troubleshooting:** This maintenance guide
- **Performance Issues:** performance_benchmarks.py
- **Monitoring:** continuous_monitoring.py

### **Emergency Contacts**
- **System Administrator:** [Contact Information]
- **Development Team:** [Contact Information]
- **Support Team:** [Contact Information]

## 📚 Additional Resources

### **Documentation**
- **README.md** - System overview and setup
- **INTEGRATION_GUIDE.md** - Integration and usage
- **FINAL_SUMMARY_REPORT.md** - Complete project summary

### **Tools and Scripts**
- **test_suite.py** - Comprehensive testing
- **performance_benchmarks.py** - Performance analysis
- **continuous_monitoring.py** - Monitoring system
- **deploy_production.py** - Production deployment

### **Configuration Files**
- **.cursor/mcp.json** - Cursor MCP configuration
- **runs/mcp/deployment_config.json** - Deployment configuration
- **runs/mcp/traffic-sim-fastmcp.service** - Systemd service

---

**Last Updated:** $(date)
**Platform Version:** 1.0.0
**Maintenance Guide Version:** 1.0.0
