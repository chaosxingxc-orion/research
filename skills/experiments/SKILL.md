---
name: "experiments"
description: "系统设计、执行和管理实验，包括实验设计、数据采集、质量控制、结果分析。当进行实验研究、A/B测试或验证假设时使用。"
---

# Experiments Designing & Running Skill

## 核心能力要求

### 1. 实验设计能力
- 假设操作化
- 变量控制
- 样本设计
- 对照设置

### 2. 技术实施能力
- 设备操作
- 软件使用
- 数据采集
- 质量控制

### 3. 数据管理能力
- 数据存储
- 数据清洗
- 数据备份
- 数据安全

### 4. 问题解决能力
- 异常处理
- 方案调整
- 结果验证
- 文档记录

## 使用步骤

### 1. 实验设计阶段
1. **明确假设**: 将研究假设转化为可测试的预测
2. **确定变量**: 
   - 自变量（实验因素）
   - 因变量（测量指标）
   - 控制变量（保持恒定）
3. **选择设计**: 
   - 全因子设计
   - 分数因子设计
   - 随机对照试验
4. **样本计划**: 
   - 样本量计算
   - 随机化方法
   - 分组策略

### 2. 实验准备阶段
1. **材料准备**: 设备、试剂、软件
2. **流程标准化**: 编写操作规程
3. **预实验**: 测试流程可行性
4. **人员培训**: 确保操作一致

### 3. 实验执行阶段
1. **按计划执行**: 严格遵循实验方案
2. **实时监控**: 监控实验进程和数据质量
3. **记录异常**: 及时记录任何偏差或异常
4. **数据备份**: 定期备份实验数据

### 4. 数据分析阶段
1. **数据清洗**: 处理缺失值和异常值
2. **统计检验**: 选择合适的统计方法
3. **结果解释**: 结合实验设计解释结果
4. **可视化**: 制作清晰的图表

## 优化工具

### 1. 实验设计器
```python
class ExperimentDesigner:
    def add_factor(self, name, levels):
        """添加实验因素"""
        
    def generate_full_factorial(self):
        """生成全因子设计"""
        
    def generate_fractional_factorial(self, fraction=0.5):
        """生成分数因子设计"""
        
    def add_randomization(self, design_matrix, seed=None):
        """添加随机化"""
        
    def add_replicates(self, design_matrix, n_replicates=3):
        """添加重复"""
        
    def calculate_power(self, effect_size, alpha=0.05, power=0.8):
        """计算所需样本量"""
```

### 2. 实验监控器
```python
class ExperimentMonitor:
    def start_experiment(self):
        """开始实验"""
        
    def log_event(self, event_type, data):
        """记录事件"""
        
    def record_metric(self, metric_name, value):
        """记录指标"""
        
    def check_progress(self, current_step, total_steps):
        """检查进度"""
        
    def detect_anomalies(self, metric_name, threshold=2.0):
        """检测异常值"""
        
    def generate_report(self):
        """生成实验报告"""
```

### 3. 数据质量控制
```python
class DataQualityControl:
    def check_missing_values(self):
        """检查缺失值"""
        
    def check_outliers(self, columns, method='iqr'):
        """检查异常值"""
        
    def check_data_types(self, expected_types):
        """检查数据类型"""
        
    def check_data_range(self, column_ranges):
        """检查数据范围"""
        
    def generate_quality_report(self):
        """生成完整质量报告"""
```

## 实验设计模板

### 实验方案文档
```markdown
# Experiment Protocol

## 基本信息
- 实验名称: [实验名称]
- 实验者: [姓名]
- 日期: [开始日期]
- 版本: [版本号]

## 1. 实验目的
[明确实验要解决的问题]

## 2. 假设
- H0: [零假设]
- H1: [备择假设]

## 3. 实验设计
### 3.1 自变量
- 因素A: [水平1, 水平2, ...]
- 因素B: [水平1, 水平2, ...]

### 3.2 因变量
- 指标1: [测量方法和单位]
- 指标2: [测量方法和单位]

### 3.3 控制变量
- [列出需要控制的因素]

## 4. 样本
- 样本量: [数量]
- 分组方法: [随机化方法]
- 纳入标准: [标准列表]
- 排除标准: [标准列表]

## 5. 材料
- 设备: [设备清单]
- 试剂: [试剂清单]
- 软件: [软件和版本]

## 6. 实验流程
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 7. 数据分析计划
- 统计方法: [方法名称]
- 显著性水平: α = [值]
- 软件: [软件名称]

## 8. 时间安排
| 阶段 | 时间 | 任务 |
|------|------|------|
| 准备 | Week 1-2 | 材料准备、预实验 |
| 执行 | Week 3-6 | 正式实验 |
| 分析 | Week 7-8 | 数据分析 |
```

## 最佳实践

### 实验设计
1. **明确假设**: 清晰定义可测试的假设
2. **控制变量**: 识别并控制所有重要变量
3. **随机化**: 使用随机化减少偏差
4. **重复**: 包含足够的重复以确保统计功效
5. **盲法**: 使用盲法避免主观偏差

### 实验执行
1. **标准化**: 使用标准化操作流程
2. **文档化**: 详细记录所有步骤和异常
3. **监控**: 实时监控实验进程
4. **质量控制**: 定期检查数据质量
5. **备份**: 及时备份所有数据

### 数据分析
1. **预分析**: 在看到数据前确定分析方法
2. **完整性**: 分析所有符合标准的数据
3. **透明性**: 报告所有分析步骤
4. **可视化**: 使用清晰的图表展示结果
5. **解释**: 结合实验设计解释结果

## 常见问题

**Q: 如何确定样本量？**
A: 进行功效分析，考虑效应大小、显著水平和统计功效

**Q: 如何处理缺失数据？**
A: 记录缺失原因，根据缺失机制选择合适的处理方法

**Q: 如何确保实验可重复？**
A: 详细记录所有步骤、参数和条件，使用标准化流程

## 相关资源

- [Design and Analysis of Experiments](https://www.wiley.com/en-us/Design+and+Analysis+of+Experiments%2C+10th+Edition-p-9781119492443)
- [Experimental Design Tutorial](https://www.statology.org/experimental-design/)
- [Power Analysis Calculator](https://www.stat.ubc.ca/~rollin/stats/ssize/)
