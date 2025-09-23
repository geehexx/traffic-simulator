# Production System Restoration Prompt
## Consolidated Implementation Guide for Advanced DSPy Optimization System

### 🎯 **Mission Context**

**PROBLEM**: Production-grade DSPy optimization system was removed during cleanup (commit `b054a6e`). Current system has only basic prompt management.

**GOAL**: Restore complete production system with advanced file management, updates, consolidation, and DSPy optimization.

**CRITICAL REQUIREMENTS**:
- Restore 7 core components from commit `8af6877`
- Implement advanced file management with updates and consolidation
- Integrate DSPy optimization (MIPROv2Ov2, BootstrapFewShot, Bayesian)
- Apply hybrid, joint, and Bayesian optimization techniques
- Maintain quality standards (PDQI-9, RGS) and performance thresholds (<1.0s response, <500MB memory, >0.85 quality score)

---

## 🏗️ **Implementation Architecture**

### **Core Components to Restore**
```python
mcp/mcp_traffic_sim/
├── production_server.py          # 9 MCP tools with DSPy integration
├── production_optimizer.py       # MIPROv2Ov2, BootstrapFewShot, Bayesian
├── monitoring_system.py          # Real-time performance tracking
├── feedback_collector.py         # User feedback analysis
├── dashboard_generator.py        # Performance visualization
├── alerting_system.py            # Configurable alerting rules
└── integration_system.py         # Component orchestration
```

### **Advanced File Management**
```python
class AdvancedFileManager:
    """Production-grade file management with updates and consolidation."""

    def __init__(self, config: MCPConfig, logger: MCPLogger):
        self.config = config
        self.logger = logger
        self.quality_standards = QualityStandards()
        self.consolidation_strategies = ConsolidationStrategies()

    async def update_documentation(self, changes: Dict) -> UpdateResult:
        """Update existing documentation with intelligent merging."""
        # 1. Analyze existing documentation structure
        # 2. Identify optimal update points using hybrid optimization
        # 3. Apply changes with Bayesian quality validation
        # 4. Maintain consistency using joint optimization
        # 5. Generate comprehensive update report

    async def consolidate_files(self, strategy: str) -> ConsolidationResult:
        """Consolidate related files with quality standards."""
        # 1. Identify related files using intelligent analysis
        # 2. Apply consolidation strategy with hybrid approach
        # 3. Validate quality standards (PDQI-9 for docs, RGS for rules)
        # 4. Optimize token efficiency using joint optimization
        # 5. Remove duplication with hybrid optimization
        # 6. Generate detailed consolidation report

    async def manage_versions(self, files: List[str]) -> VersionResult:
        """Version control with rollback capabilities."""
        # 1. Create version snapshots with comprehensive metadata
        # 2. Track changes and dependencies using hybrid monitoring
        # 3. Enable rollback functionality with Bayesian validation
        # 4. Maintain version history with joint optimization
        # 5. Generate detailed version report
```

### **DSPy Optimization Integration**
```python
class ProductionOptimizer:
    """DSPy-based real-time optimization with comprehensive monitoring."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        self.config = config
        self.logger = logger
        self.security = security
        self.monitoring = MonitoringSystem(config, logger, security)

        # Initialize DSPy components with optimization strategies
        self.optimizers = {
            "MIPROv2": DSPy.MIPROv2Ov2,                    # Advanced joint optimization
            "bootstrap": DSPy.BootstrapFewShot,        # Few-shot learning
            "bayesian": DSPy.BootstrapFewShot,          # Bayesian fallback
            "hybrid": DSPy.MIPROv2Ov2,                    # Hybrid approach
        }

        # Optimization techniques integration
        self.optimization_strategies = {
            "hybrid": self._hybrid_optimization,
            "bayesian": self._bayesian_optimization,
            "joint": self._joint_optimization,
            "MIPROv2": self._MIPROv2_optimization,
            "bootstrap": self._bootstrap_optimization,
        }

    async def optimize_prompt_production(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Production-grade prompt optimization with comprehensive monitoring."""
        # 1. Validate input parameters with quality gates
        # 2. Initialize DSPy optimizer with hybrid strategy
        # 3. Run optimization with Bayesian monitoring
        # 4. Evaluate results using joint optimization
        # 5. Generate comprehensive optimization report
        # 6. Update performance metrics with real-time tracking

    async def auto_optimize_feedback(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time feedback-based optimization."""
        # 1. Process user feedback with intelligent analysis
        # 2. Analyze feedback patterns using hybrid approach
        # 3. Trigger optimization if threshold met with Bayesian validation
        # 4. Apply feedback-based improvements using joint optimization
        # 5. Monitor optimization results with comprehensive metrics

    async def evaluate_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive performance evaluation."""
        # 1. Run test cases with hybrid optimization
        # 2. Measure performance metrics using Bayesian analysis
        # 3. Evaluate quality scores with joint optimization
        # 4. Generate detailed performance report
        # 5. Provide improvement recommendations with MIPROv2Ov2 insights
```

---

## 🔧 **Optimization Techniques**

### **Hybrid Optimization Strategy**
```python
async def _hybrid_optimization(self, prompt: str, context: Dict) -> str:
    """Hybrid optimization combining multiple approaches."""
    # 1. Apply systematic prompt improvement with MIPROv2Ov2
    # 2. Enhance performance and clarity using BootstrapFewShot
    # 3. Integrate Bayesian optimization for statistical enhancement
    # 4. Apply joint optimization for comprehensive improvement
    # 5. Validate results with quality metrics (PDQI-9, RGS)
    # 6. Generate optimization report with performance insights
```

### **Bayesian Optimization Strategy**
```python
async def _bayesian_optimization(self, prompt: str, context: Dict) -> str:
    """Bayesian optimization with data-driven improvements."""
    # 1. Analyze historical performance data with statistical methods
    # 2. Apply statistical performance enhancement using Bayesian inference
    # 3. Use BootstrapFewShot for few-shot learning optimization
    # 4. Validate with performance metrics and quality standards
    # 5. Generate detailed optimization report with statistical insights
```

### **Joint Optimization Strategy**
```python
async def _joint_optimization(self, prompt: str, context: Dict) -> str:
    """Joint optimization with systematic improvement."""
    # 1. Apply joint optimization techniques using MIPROv2Ov2
    # 2. Integrate Bayesian and hybrid approaches for comprehensive optimization
    # 3. Enhance with systematic improvements using BootstrapFewShot
    # 4. Validate with comprehensive metrics and quality standards
    # 5. Generate detailed optimization report with joint insights
```

---

## 📊 **Quality Standards**

### **Documentation Standards (PDQI-9)**
- **Clarity**: Clear, concise, and well-structured documentation
- **Completeness**: Comprehensive coverage of all topics
- **Accuracy**: Factually correct and up-to-date information
- **Consistency**: Uniform style and format across all documents
- **Accessibility**: Easy to understand and navigate for all users

### **Rules Standards (RGS)**
- **Stability Index**: ≥0.85 for production deployment
- **Idempotency**: Safe to re-run without side effects
- **Quality Gates**: Enforce quality standards with automated validation
- **Token Efficiency**: Optimize for performance and resource usage
- **Duplication Avoidance**: Consolidate related content intelligently

### **Performance Standards**
- **Response Time**: <1.0s for all optimization operations
- **Memory Usage**: <500MB for system operations
- **Success Rate**: >95% for optimization operations
- **Quality Score**: >0.85 for all generated content
- **Reliability**: >99% uptime for production systems

---

## 🚀 **Implementation Workflow**

### **Step 1: System Analysis and Preparation**
```bash
# Extract removed components from git history
git show 8af6877 -- mcp/mcp_traffic_sim/production_server.py > temp_production_server.py
git show 8af6877 -- mcp/mcp_traffic_sim/production_optimizer.py > temp_production_optimizer.py
git show 8af6877 -- mcp/mcp_traffic_sim/monitoring_system.py > temp_monitoring_system.py
git show 8af6877 -- mcp/mcp_traffic_sim/feedback_collector.py > temp_feedback_collector.py
git show 8af6877 -- mcp/mcp_traffic_sim/dashboard_generator.py > temp_dashboard_generator.py
git show 8af6877 -- mcp/mcp_traffic_sim/alerting_system.py > temp_alerting_system.py
git show 8af6877 -- mcp/mcp_traffic_sim/integration_system.py > temp_integration_system.py

# Analyze current system state
ls -la mcp/mcp_traffic_sim/
cat mcp/FastMCP_production_server.py
```

### **Step 2: Core Component Restoration**
```python
# Priority Order with Optimization Integration:
1. production_optimizer.py      # Core DSPy optimization with hybrid strategies
2. monitoring_system.py         # Performance tracking with Bayesian analysis
3. production_server.py         # MCP tool integration with joint optimization
4. feedback_collector.py        # User feedback processing with hybrid approach
5. dashboard_generator.py       # Performance visualization with comprehensive metrics
6. alerting_system.py           # Alert management with intelligent thresholds
7. integration_system.py        # Component orchestration with optimization
```

### **Step 3: MCP Tool Integration**
```python
# 9 Production MCP Tools with Optimization Integration:
@server.list_tools()
async def list_tools() -> ListToolsResult:
    tools = [
        # Core Optimization Tools
        Tool(name="optimize_prompt_production",
             description="Production-grade prompt optimization using DSPy with hybrid strategies",
             inputSchema={
                 "prompt_id": {"type": "string"},
                 "strategy": {"type": "string", "enum": ["MIPROv2", "bootstrap", "bayesian", "hybrid"]},
                 "training_data": {"type": "array"},
                 "auto_mode": {"type": "string", "enum": ["light", "medium", "heavy"]},
                 "monitoring_enabled": {"type": "boolean", "default": True}
             }),

        Tool(name="auto_optimize_feedback",
             description="Real-time feedback-based optimization with Bayesian analysis",
             inputSchema={
                 "prompt_id": {"type": "string"},
                 "user_feedback": {"type": "array"},
                 "feedback_threshold": {"type": "number", "default": 0.7},
                 "max_iterations": {"type": "integer", "default": 5}
             }),

        Tool(name="evaluate_performance",
             description="Comprehensive performance evaluation with joint optimization",
             inputSchema={
                 "prompt_id": {"type": "string"},
                 "test_cases": {"type": "array"},
                 "evaluation_metrics": {"type": "array", "default": ["quality", "speed", "accuracy"]}
             }),

        # Monitoring and Analytics Tools
        Tool(name="get_system_status",
             description="Get comprehensive system status and health metrics",
             inputSchema={
                 "include_metrics": {"type": "boolean", "default": True},
                 "include_optimization_status": {"type": "boolean", "default": True}
             }),

        Tool(name="get_optimization_analytics",
             description="Get optimization analytics with performance insights",
             inputSchema={
                 "prompt_id": {"type": "string"},
                 "metric_types": {"type": "array", "items": {"type": "string"}},
                 "include_trends": {"type": "boolean", "default": True}
             }),

        Tool(name="get_dashboard",
             description="Get performance dashboard with comprehensive metrics",
             inputSchema={
                 "dashboard_type": {"type": "string", "enum": ["overview", "detailed", "trends", "alerts"]},
                 "time_range": {"type": "string", "default": "24h"},
                 "include_metrics": {"type": "boolean", "default": True}
             }),

        # Advanced Features
        Tool(name="run_improvement_cycle",
             description="Run automated improvement cycle with hybrid optimization",
             inputSchema={
                 "prompt_id": {"type": "string"},
                 "iterations": {"type": "integer", "default": 3},
                 "strategies": {"type": "array", "default": ["MIPROv2", "bayesian", "hybrid"]}
             }),

        Tool(name="configure_alerts",
             description="Configure optimization alerts and thresholds",
             inputSchema={
                 "alert_types": {"type": "array", "items": {"type": "string"}},
                 "thresholds": {"type": "object"},
                 "notification_channels": {"type": "array", "default": ["dashboard", "logs"]}
             }),

        Tool(name="deploy_prompts",
             description="Deploy optimized prompts to target environment",
             inputSchema={
                 "prompt_ids": {"type": "array", "items": {"type": "string"}},
                 "environment": {"type": "string", "default": "production"},
                 "rollback_enabled": {"type": "boolean", "default": True}
             }),
    ]
```

---

## 🎯 **Success Metrics**

### **Technical Metrics**
- **System Restoration**: 100% of removed components restored with optimization
- **Performance**: <1.0s response time for all operations
- **Quality**: >0.85 quality score for all outputs
- **Reliability**: >95% success rate for all operations
- **Memory Usage**: <500MB for system operations

### **Functional Metrics**
- **Updates**: Full documentation update capabilities with hybrid optimization
- **Consolidation**: Intelligent file consolidation with Bayesian analysis
- **Optimization**: Real-time DSPy-based optimization with joint strategies
- **Monitoring**: Comprehensive performance tracking with detailed metrics

### **Quality Metrics**
- **Documentation Quality**: PDQI-9 standards compliance
- **Rules Quality**: RGS standards compliance
- **Performance Quality**: Comprehensive performance metrics
- **User Experience**: Intuitive interface with high-quality outputs

---

## 🔧 **Implementation Checklist**

### **Pre-Implementation**
- [ ] Analyze current system state and requirements
- [ ] Extract removed components from git history (commit 8af6877)
- [ ] Validate dependencies and compatibility with current system
- [ ] Plan integration strategy with optimization techniques

### **Core Implementation**
- [ ] Restore production_server.py with 9 MCP tools
- [ ] Restore production_optimizer.py with DSPy integration
- [ ] Restore monitoring_system.py with performance tracking
- [ ] Restore feedback_collector.py with user feedback analysis
- [ ] Restore dashboard_generator.py with performance visualization
- [ ] Restore alerting_system.py with configurable alerting
- [ ] Restore integration_system.py with component orchestration

### **Advanced Features**
- [ ] Implement advanced file management with updates and consolidation
- [ ] Add hybrid, Bayesian, and joint optimization strategies
- [ ] Integrate DSPy optimization with MIPROv2Ov2 and BootstrapFewShot
- [ ] Setup comprehensive performance monitoring and analytics

### **Testing and Validation**
- [ ] Unit testing for all components with optimization validation
- [ ] Integration testing with comprehensive test coverage
- [ ] Performance testing with quality metrics validation
- [ ] Security validation with comprehensive security testing
- [ ] User acceptance testing with optimization techniques

### **Deployment**
- [ ] Production deployment with optimization integration
- [ ] Monitoring setup with comprehensive metrics
- [ ] Performance optimization with quality standards
- [ ] Documentation update with optimization techniques

---

## 🎉 **Expected Outcomes**

### **Immediate Benefits**
- **Full System Restoration**: Complete production-grade system restored with optimization
- **Advanced File Management**: Updates, consolidation, and version control with hybrid optimization
- **Real-time Optimization**: DSPy-based optimization with comprehensive monitoring
- **Performance Analytics**: Comprehensive performance tracking with detailed dashboards

### **Long-term Benefits**
- **Continuous Improvement**: Automated optimization with feedback integration
- **Scalability**: System can handle large-scale operations with optimization
- **Reliability**: Production-grade monitoring and alerting with quality standards
- **Maintainability**: Comprehensive documentation and version control with optimization

### **User Experience**
- **Intuitive Interface**: Easy-to-use system for all operations with optimization
- **High Performance**: Fast and responsive system with quality metrics
- **Quality Outputs**: High-quality documentation and results with optimization
- **Reliable Operation**: Consistent and dependable system with comprehensive monitoring

---

**This consolidated implementation prompt provides complete context for another AI to implement the advanced system restoration with full understanding of the current state, what was lost, and how to restore it with enhanced capabilities using integrated optimization techniques.**
