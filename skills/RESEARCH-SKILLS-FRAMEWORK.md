# 研究技能完整框架

## 概述

本文档定义了专业研究员的五项核心研究技能，包括每项技能所需的能力、优化工具和脚本。

## 五项核心研究技能

### 1. Literature Review（文献综述）
**核心能力**：
- 信息检索：数据库搜索、搜索策略设计、引文追踪
- 批判性评估：研究设计评估、偏倚评估、质量评估
- 信息综合：数据提取、主题分析、元分析
- 学术写作：结构组织、批判性整合、差距识别

**优化工具**：
- 多数据库搜索自动化脚本
- 引文网络分析工具
- 重复检测和去重脚本
- 自动化质量评分系统
- PRISMA流程图生成器

**详见**：`literature-review/SKILL.md`（已创建完整版本）

---

### 2. Paper Reading（论文阅读）

#### 核心能力要求

**2.1 快速筛选能力**
- 标题摘要快速评估（< 2分钟/篇）
- 相关性判断（高/中/低）
- 决策树应用（纳入/排除/待定）

**2.2 深度阅读能力**
- 结构化阅读方法（IMRaD）
- 关键信息提取（研究问题、方法、结果、结论）
- 批判性思维（优势、局限、适用性）

**2.3 笔记和总结能力**
- 标准化笔记模板
- 思维导图制作
- 知识图谱构建

**2.4 知识整合能力**
- 跨论文概念连接
- 理论框架构建
- 研究脉络梳理

#### 优化工具和脚本

**工具1：论文阅读助手**
```python
# paper_reading_assistant.py
import re
from typing import Dict, List
import fitz  # PyMuPDF

class PaperReadingAssistant:
    def __init__(self):
        self.sections = {
            'abstract': None,
            'introduction': None,
            'methods': None,
            'results': None,
            'discussion': None,
            'conclusion': None
        }
    
    def extract_sections(self, pdf_path):
        """自动提取论文章节"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        # 识别章节标题
        section_patterns = {
            'abstract': r'abstract[:\s]*(.*?)(?=introduction|methods|$)',
            'introduction': r'1\.?\s*introduction[:\s]*(.*?)(?=2|methods|$)',
            'methods': r'methods?[:\s]*(.*?)(?=results|3|$)',
            'results': r'results?[:\s]*(.*?)(?=discussion|4|$)',
            'discussion': r'discussion[:\s]*(.*?)(?=conclusion|5|$)',
            'conclusion': r'conclusions?[:\s]*(.*?)(?=references|$)'
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                self.sections[section] = match.group(1).strip()
        
        return self.sections
    
    def generate_summary(self):
        """生成论文摘要"""
        summary = {
            'key_findings': [],
            'methods_used': [],
            'limitations': [],
            'implications': []
        }
        
        # 使用NLP提取关键信息
        if self.sections['abstract']:
            summary['key_findings'] = self._extract_key_sentences(
                self.sections['abstract']
            )
        
        return summary
    
    def create_reading_notes(self, output_file):
        """创建标准化阅读笔记"""
        template = f"""
# Paper Reading Notes

## Basic Information
- Title: {{title}}
- Authors: {{authors}}
- Year: {{year}}
- DOI: {{doi}}

## Key Points
### Research Question
{self._extract_research_question()}

### Methods
{self.sections.get('methods', 'N/A')[:500]}...

### Main Results
{self._extract_main_results()}

### Conclusions
{self.sections.get('conclusion', 'N/A')[:300]}...

## Critical Analysis
### Strengths
- [ ] 

### Limitations
- [ ] 

### Applicability
- [ ] 

## Personal Notes
{self._generate_questions()}

## Related Papers
- 

## Tags
#research #{{field}} #{{topic}}
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return output_file
```

**工具2：论文管理器**
```python
# paper_manager.py
import os
import json
from datetime import datetime
import shutil

class PaperManager:
    def __init__(self, base_dir='papers'):
        self.base_dir = base_dir
        self.metadata_file = os.path.join(base_dir, 'metadata.json')
        self.load_metadata()
    
    def add_paper(self, pdf_file, metadata=None):
        """添加新论文到库中"""
        # 提取DOI或生成ID
        paper_id = self._extract_or_generate_id(pdf_file)
        
        # 创建论文目录
        paper_dir = os.path.join(self.base_dir, paper_id)
        os.makedirs(paper_dir, exist_ok=True)
        
        # 复制PDF
        shutil.copy(pdf_file, paper_dir)
        
        # 保存元数据
        paper_metadata = {
            'id': paper_id,
            'added_date': datetime.now().isoformat(),
            'pdf_path': os.path.join(paper_dir, os.path.basename(pdf_file)),
            'status': 'to_read',
            'tags': [],
            'notes': '',
            **(metadata or {})
        }
        
        self.metadata[paper_id] = paper_metadata
        self.save_metadata()
        
        return paper_id
    
    def organize_by_topic(self):
        """按主题组织论文"""
        topics = {}
        
        for paper_id, paper in self.metadata.items():
            for tag in paper.get('tags', []):
                if tag not in topics:
                    topics[tag] = []
                topics[tag].append(paper_id)
        
        return topics
    
    def generate_reading_list(self, criteria):
        """生成阅读列表"""
        reading_list = []
        
        for paper_id, paper in self.metadata.items():
            if self._matches_criteria(paper, criteria):
                reading_list.append({
                    'id': paper_id,
                    'title': paper.get('title', 'Unknown'),
                    'priority': paper.get('priority', 'medium'),
                    'status': paper.get('status', 'to_read')
                })
        
        return sorted(reading_list, key=lambda x: x['priority'])
```

**工具3：关键概念提取器**
```python
# concept_extractor.py
import spacy
from collections import Counter
import networkx as nx

class ConceptExtractor:
    def __init__(self):
        self.nlp = spacy.load('en_core_sci_md')  # Scientific model
    
    def extract_key_concepts(self, text, top_n=20):
        """提取关键概念"""
        doc = self.nlp(text)
        
        # 提取名词短语和实体
        concepts = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # 限制长度
                concepts.append(chunk.text.lower())
        
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'LAW']:
                concepts.append(ent.text.lower())
        
        # 统计频率
        concept_freq = Counter(concepts)
        return concept_freq.most_common(top_n)
    
    def build_concept_graph(self, papers):
        """构建概念网络图"""
        graph = nx.Graph()
        
        for paper in papers:
            concepts = self.extract_key_concepts(paper['text'])
            
            # 添加节点
            for concept, freq in concepts:
                if graph.has_node(concept):
                    graph.nodes[concept]['weight'] += freq
                else:
                    graph.add_node(concept, weight=freq)
            
            # 添加边（共现关系）
            concept_list = [c for c, _ in concepts]
            for i in range(len(concept_list)):
                for j in range(i+1, len(concept_list)):
                    if graph.has_edge(concept_list[i], concept_list[j]):
                        graph[concept_list[i]][concept_list[j]]['weight'] += 1
                    else:
                        graph.add_edge(concept_list[i], concept_list[j], weight=1)
        
        return graph
```

---

### 3. Research Proposal（研究提案）

#### 核心能力要求

**3.1 问题识别能力**
- 研究空白发现
- 实际需求分析
- 理论与实践结合

**3.2 文献综述能力**
- 现有研究总结
- 理论基础构建
- 研究脉络梳理

**3.3 研究设计能力**
- 研究问题明确化
- 假设提出
- 方法论选择

**3.4 可行性分析能力**
- 资源评估
- 时间规划
- 风险识别

**3.5 写作表达能力**
- 逻辑结构清晰
- 论证有力
- 语言准确

#### 优化工具和脚本

**工具1：提案模板生成器**
```python
# proposal_generator.py
from datetime import datetime, timedelta
import json

class ProposalGenerator:
    def __init__(self):
        self.sections = {
            'title': '',
            'abstract': '',
            'introduction': '',
            'literature_review': '',
            'research_questions': [],
            'methodology': '',
            'timeline': {},
            'budget': {},
            'expected_outcomes': [],
            'references': []
        }
    
    def generate_timeline(self, start_date, duration_months):
        """生成研究时间线"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        
        phases = {
            'Literature Review': 0.2,
            'Methodology Development': 0.15,
            'Data Collection': 0.25,
            'Data Analysis': 0.2,
            'Writing and Revision': 0.2
        }
        
        timeline = {}
        current_date = start
        
        for phase, proportion in phases.items():
            phase_duration = int(duration_months * proportion * 30)
            end_date = current_date + timedelta(days=phase_duration)
            
            timeline[phase] = {
                'start': current_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'duration_days': phase_duration
            }
            
            current_date = end_date + timedelta(days=1)
        
        return timeline
    
    def generate_budget_template(self, categories):
        """生成预算模板"""
        budget_template = {
            'personnel': {
                'researcher': {'unit': 'month', 'quantity': 0, 'rate': 0},
                'assistants': {'unit': 'month', 'quantity': 0, 'rate': 0}
            },
            'equipment': {},
            'materials': {},
            'travel': {},
            'other': {}
        }
        
        return budget_template
    
    def create_proposal_document(self, template_type='academic'):
        """创建提案文档"""
        if template_type == 'academic':
            return self._create_academic_template()
        elif template_type == 'grant':
            return self._create_grant_template()
        elif template_type == 'industry':
            return self._create_industry_template()
    
    def _create_academic_template(self):
        """学术研究提案模板"""
        template = """
# Research Proposal

## Title
{title}

## Abstract
{abstract}

## 1. Introduction
### 1.1 Background
{background}

### 1.2 Problem Statement
{problem_statement}

### 1.3 Research Objectives
{objectives}

## 2. Literature Review
{literature_review}

## 3. Research Questions and Hypotheses
{research_questions}

## 4. Methodology
### 4.1 Research Design
{research_design}

### 4.2 Data Collection
{data_collection}

### 4.3 Data Analysis
{data_analysis}

## 5. Timeline
{timeline}

## 6. Expected Outcomes
{expected_outcomes}

## 7. Budget (if applicable)
{budget}

## References
{references}
"""
        return template
```

**工具2：可行性分析器**
```python
# feasibility_analyzer.py
import pandas as pd
import matplotlib.pyplot as plt

class FeasibilityAnalyzer:
    def __init__(self):
        self.criteria = {
            'technical': [],
            'financial': [],
            'temporal': [],
            'human_resources': []
        }
    
    def assess_technical_feasibility(self, requirements):
        """评估技术可行性"""
        scores = {}
        
        for req in requirements:
            # 检查技术成熟度
            maturity = self._check_tech_maturity(req['technology'])
            # 检查资源可用性
            availability = self._check_resource_availability(req['resources'])
            
            scores[req['name']] = {
                'maturity_score': maturity,
                'availability_score': availability,
                'overall': (maturity + availability) / 2
            }
        
        return scores
    
    def assess_financial_feasibility(self, budget, available_funding):
        """评估财务可行性"""
        total_budget = sum(budget.values())
        funding_gap = total_budget - available_funding
        
        return {
            'total_budget': total_budget,
            'available_funding': available_funding,
            'funding_gap': funding_gap,
            'feasible': funding_gap <= 0,
            'coverage_ratio': available_funding / total_budget
        }
    
    def assess_temporal_feasibility(self, timeline, constraints):
        """评估时间可行性"""
        conflicts = []
        
        for phase, dates in timeline.items():
            start = datetime.strptime(dates['start'], '%Y-%m-%d')
            end = datetime.strptime(dates['end'], '%Y-%m-%d')
            
            for constraint in constraints:
                if self._has_conflict(start, end, constraint):
                    conflicts.append({
                        'phase': phase,
                        'constraint': constraint
                    })
        
        return {
            'conflicts': conflicts,
            'feasible': len(conflicts) == 0
        }
    
    def generate_feasibility_report(self, output_file):
        """生成可行性报告"""
        report = {
            'technical': self.assess_technical_feasibility(),
            'financial': self.assess_financial_feasibility(),
            'temporal': self.assess_temporal_feasibility(),
            'overall_feasibility': self._calculate_overall_feasibility(),
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
```

---

### 4. Experiments Designing & Running（实验设计与执行）

#### 核心能力要求

**4.1 实验设计能力**
- 假设操作化
- 变量控制
- 样本设计
- 对照设置

**4.2 技术实施能力**
- 设备操作
- 软件使用
- 数据采集
- 质量控制

**4.3 数据管理能力**
- 数据存储
- 数据清洗
- 数据备份
- 数据安全

**4.4 问题解决能力**
- 异常处理
- 方案调整
- 结果验证
- 文档记录

#### 优化工具和脚本

**工具1：实验设计器**
```python
# experiment_designer.py
import numpy as np
import pandas as pd
from itertools import product

class ExperimentDesigner:
    def __init__(self):
        self.factors = {}
        self.design_matrix = None
    
    def add_factor(self, name, levels):
        """添加实验因素"""
        self.factors[name] = levels
    
    def generate_full_factorial(self):
        """生成全因子设计"""
        factor_levels = [self.factors[f] for f in self.factors]
        combinations = list(product(*factor_levels))
        
        self.design_matrix = pd.DataFrame(
            combinations, 
            columns=self.factors.keys()
        )
        
        return self.design_matrix
    
    def generate_fractional_factorial(self, fraction=0.5):
        """生成分数因子设计"""
        full_design = self.generate_full_factorial()
        n_runs = int(len(full_design) * fraction)
        
        # 选择正交子集
        selected_indices = self._select_orthogonal_subset(
            full_design, n_runs
        )
        
        return full_design.iloc[selected_indices]
    
    def add_randomization(self, design_matrix, seed=None):
        """添加随机化"""
        if seed:
            np.random.seed(seed)
        
        randomized = design_matrix.sample(frac=1).reset_index(drop=True)
        return randomized
    
    def add_replicates(self, design_matrix, n_replicates=3):
        """添加重复"""
        replicated = pd.concat([design_matrix] * n_replicates, ignore_index=True)
        return self.add_randomization(replicated)
    
    def calculate_power(self, effect_size, alpha=0.05, power=0.8):
        """计算所需样本量"""
        from scipy import stats
        
        # 简化版功效分析
        n_factors = len(self.factors)
        df_num = n_factors - 1
        df_denom = None  # 需要计算
        
        # 使用公式估算
        required_n = self._estimate_sample_size(
            effect_size, alpha, power
        )
        
        return {
            'required_sample_size': required_n,
            'effect_size': effect_size,
            'alpha': alpha,
            'power': power
        }
```

**工具2：实验执行监控器**
```python
# experiment_monitor.py
import time
import json
import logging
from datetime import datetime

class ExperimentMonitor:
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        self.start_time = None
        self.logs = []
        self.metrics = {}
        
        logging.basicConfig(
            filename=f'experiment_{experiment_id}.log',
            level=logging.INFO
        )
    
    def start_experiment(self):
        """开始实验"""
        self.start_time = datetime.now()
        self.log_event('experiment_started', {
            'timestamp': self.start_time.isoformat()
        })
    
    def log_event(self, event_type, data):
        """记录事件"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        self.logs.append(event)
        logging.info(json.dumps(event))
    
    def record_metric(self, metric_name, value):
        """记录指标"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'timestamp': datetime.now().isoformat(),
            'value': value
        })
    
    def check_progress(self, current_step, total_steps):
        """检查进度"""
        progress = (current_step / total_steps) * 100
        elapsed = datetime.now() - self.start_time
        
        if current_step > 0:
            estimated_total = elapsed * (total_steps / current_step)
            estimated_remaining = estimated_total - elapsed
        else:
            estimated_remaining = None
        
        return {
            'progress_percentage': progress,
            'elapsed_time': str(elapsed),
            'estimated_remaining': str(estimated_remaining) if estimated_remaining else None
        }
    
    def detect_anomalies(self, metric_name, threshold=2.0):
        """检测异常值"""
        values = [m['value'] for m in self.metrics[metric_name]]
        mean = np.mean(values)
        std = np.std(values)
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'z_score': z_score
                })
        
        return anomalies
    
    def generate_report(self):
        """生成实验报告"""
        report = {
            'experiment_id': self.experiment_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': datetime.now().isoformat(),
            'total_events': len(self.logs),
            'metrics_summary': {
                name: {
                    'count': len(values),
                    'mean': np.mean([v['value'] for v in values]),
                    'std': np.std([v['value'] for v in values])
                }
                for name, values in self.metrics.items()
            },
            'anomalies': {
                name: self.detect_anomalies(name)
                for name in self.metrics.keys()
            }
        }
        
        return report
```

**工具3：数据质量控制**
```python
# data_quality_control.py
import pandas as pd
import numpy as np

class DataQualityControl:
    def __init__(self, data):
        self.data = data
        self.quality_report = {}
    
    def check_missing_values(self):
        """检查缺失值"""
        missing = self.data.isnull().sum()
        percentage = (missing / len(self.data)) * 100
        
        return {
            'missing_counts': missing.to_dict(),
            'missing_percentage': percentage.to_dict(),
            'columns_with_missing': missing[missing > 0].index.tolist()
        }
    
    def check_outliers(self, columns, method='iqr'):
        """检查异常值"""
        outliers = {}
        
        for col in columns:
            if method == 'iqr':
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (self.data[col] < lower_bound) | (self.data[col] > upper_bound)
                outliers[col] = {
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(self.data)) * 100,
                    'indices': self.data[outlier_mask].index.tolist()
                }
        
        return outliers
    
    def check_data_types(self, expected_types):
        """检查数据类型"""
        type_issues = []
        
        for col, expected_type in expected_types.items():
            actual_type = self.data[col].dtype
            if str(actual_type) != expected_type:
                type_issues.append({
                    'column': col,
                    'expected': expected_type,
                    'actual': str(actual_type)
                })
        
        return type_issues
    
    def check_data_range(self, column_ranges):
        """检查数据范围"""
        range_violations = []
        
        for col, (min_val, max_val) in column_ranges.items():
            violations = self.data[
                (self.data[col] < min_val) | (self.data[col] > max_val)
            ]
            
            if len(violations) > 0:
                range_violations.append({
                    'column': col,
                    'expected_range': (min_val, max_val),
                    'violation_count': len(violations),
                    'actual_min': self.data[col].min(),
                    'actual_max': self.data[col].max()
                })
        
        return range_violations
    
    def generate_quality_report(self):
        """生成完整质量报告"""
        self.quality_report = {
            'missing_values': self.check_missing_values(),
            'data_shape': self.data.shape,
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'duplicates': self.data.duplicated().sum(),
            'quality_score': self._calculate_quality_score()
        }
        
        return self.quality_report
    
    def _calculate_quality_score(self):
        """计算数据质量分数"""
        # 简化版质量评分
        missing_penalty = self.data.isnull().sum().sum() / (self.data.shape[0] * self.data.shape[1])
        duplicate_penalty = self.data.duplicated().sum() / len(self.data)
        
        quality_score = 100 * (1 - missing_penalty - duplicate_penalty)
        return max(0, quality_score)
```

---

### 5. Paper Writing（论文写作）

#### 核心能力要求

**5.1 结构组织能力**
- IMRaD结构掌握
- 逻辑流构建
- 段落组织

**5.2 学术写作能力**
- 准确性表达
- 客观性陈述
- 简洁性原则

**5.3 论证能力**
- 证据支持
- 逻辑推理
- 反驳预期质疑

**5.4 语言能力**
- 语法正确
- 用词精准
- 句式多样

**5.5 引用能力**
- 文献引用规范
- 避免抄袭
- 格式统一

#### 优化工具和脚本

**工具1：论文结构生成器**
```python
# paper_structure_generator.py
from docx import Document
from docx.shared import Pt, RGBColor

class PaperStructureGenerator:
    def __init__(self, template_type='academic'):
        self.document = Document()
        self.template_type = template_type
    
    def create_academic_paper_structure(self, title):
        """创建学术论文结构"""
        # 标题
        title_heading = self.document.add_heading(title, level=0)
        title_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 作者信息
        self.document.add_paragraph('Author Names')
        self.document.add_paragraph('Affiliation')
        self.document.add_paragraph('Email')
        
        # 摘要
        self.document.add_heading('Abstract', level=1)
        abstract_para = self.document.add_paragraph()
        abstract_para.add_run('[Write your abstract here (150-250 words)]')
        
        # 关键词
        self.document.add_heading('Keywords', level=2)
        self.document.add_paragraph('[3-5 keywords]')
        
        # 1. Introduction
        self.document.add_heading('1. Introduction', level=1)
        self.document.add_paragraph('[Introduction content]')
        
        # 1.1 Background
        self.document.add_heading('1.1 Background', level=2)
        self.document.add_paragraph('[Background information]')
        
        # 1.2 Problem Statement
        self.document.add_heading('1.2 Problem Statement', level=2)
        self.document.add_paragraph('[State the problem]')
        
        # 1.3 Research Objectives
        self.document.add_heading('1.3 Research Objectives', level=2)
        self.document.add_paragraph('[List your objectives]')
        
        # 2. Literature Review
        self.document.add_heading('2. Literature Review', level=1)
        self.document.add_paragraph('[Literature review content]')
        
        # 3. Methodology
        self.document.add_heading('3. Methodology', level=1)
        
        # 3.1 Research Design
        self.document.add_heading('3.1 Research Design', level=2)
        self.document.add_paragraph('[Describe your research design]')
        
        # 3.2 Data Collection
        self.document.add_heading('3.2 Data Collection', level=2)
        self.document.add_paragraph('[Describe data collection methods]')
        
        # 3.3 Data Analysis
        self.document.add_heading('3.3 Data Analysis', level=2)
        self.document.add_paragraph('[Describe analysis methods]')
        
        # 4. Results
        self.document.add_heading('4. Results', level=1)
        self.document.add_paragraph('[Present your results]')
        
        # 5. Discussion
        self.document.add_heading('5. Discussion', level=1)
        self.document.add_paragraph('[Discuss your findings]')
        
        # 6. Conclusion
        self.document.add_heading('6. Conclusion', level=1)
        self.document.add_paragraph('[Summarize and conclude]')
        
        # References
        self.document.add_heading('References', level=1)
        
        return self.document
    
    def add_figure(self, caption, image_path):
        """添加图表"""
        paragraph = self.document.add_paragraph()
        run = paragraph.add_run()
        run.add_picture(image_path)
        
        caption_para = self.document.add_paragraph(caption)
        caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        return paragraph
    
    def add_table(self, caption, data):
        """添加表格"""
        table = self.document.add_table(rows=len(data), cols=len(data[0]))
        table.style = 'Light Grid Accent 1'
        
        for i, row_data in enumerate(data):
            row = table.rows[i]
            for j, cell_data in enumerate(row_data):
                row.cells[j].text = str(cell_data)
        
        caption_para = self.document.add_paragraph(caption)
        caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        return table
```

**工具2：写作质量检查器**
```python
# writing_quality_checker.py
import language_tool_python
import textstat
from textblob import TextBlob

class WritingQualityChecker:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')
    
    def check_grammar(self, text):
        """检查语法错误"""
        matches = self.tool.check(text)
        
        errors = []
        for match in matches:
            errors.append({
                'message': match.message,
                'context': match.context,
                'suggestions': match.replacements,
                'rule_id': match.ruleId
            })
        
        return {
            'total_errors': len(errors),
            'errors': errors,
            'corrected_text': language_tool_python.utils.correct(text, matches)
        }
    
    def check_readability(self, text):
        """检查可读性"""
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
            'linsear_write_formula': textstat.linsear_write_formula(text),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
            'text_standard': textstat.text_standard(text)
        }
    
    def analyze_sentiment(self, text):
        """分析情感倾向（确保客观性）"""
        blob = TextBlob(text)
        
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1 (negative to positive)
            'subjectivity': blob.sentiment.subjectivity,  # 0 to 1 (objective to subjective)
            'is_objective': blob.sentiment.subjectivity < 0.3
        }
    
    def check_academic_tone(self, text):
        """检查学术语气"""
        # 检查第一人称使用
        first_person = ['I', 'me', 'my', 'we', 'us', 'our']
        first_person_count = sum(text.lower().count(word) for word in first_person)
        
        # 检查模糊词
        vague_words = ['very', 'really', 'quite', 'somewhat', 'basically']
        vague_count = sum(text.lower().count(word) for word in vague_words)
        
        # 检查过渡词
        transitions = ['however', 'therefore', 'moreover', 'furthermore', 'consequently']
        transition_count = sum(text.lower().count(word) for word in transitions)
        
        return {
            'first_person_usage': first_person_count,
            'vague_words': vague_count,
            'transition_words': transition_count,
            'academic_tone_score': self._calculate_academic_score(
                first_person_count, vague_count, transition_count, len(text.split())
            )
        }
    
    def _calculate_academic_score(self, first_person, vague, transitions, total_words):
        """计算学术语气分数"""
        # 简化评分
        score = 100
        
        # 扣除第一人称使用分
        score -= first_person * 2
        
        # 扣除模糊词使用分
        score -= vague * 3
        
        # 加分过渡词
        score += transitions * 1
        
        # 标准化
        score = max(0, min(100, score))
        
        return score
    
    def generate_quality_report(self, text):
        """生成完整质量报告"""
        return {
            'grammar': self.check_grammar(text),
            'readability': self.check_readability(text),
            'sentiment': self.analyze_sentiment(text),
            'academic_tone': self.check_academic_tone(text),
            'overall_quality': self._calculate_overall_quality()
        }
```

**工具3：引用格式化器**
```python
# citation_formatter.py
import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text

class CitationFormatter:
    def __init__(self, style='apa'):
        self.style = style
        self.references = []
    
    def load_bibtex(self, bibtex_file):
        """加载BibTeX文件"""
        with open(bibtex_file) as f:
            bib_database = bibtexparser.load(f)
        
        self.references = bib_database.entries
        return self.references
    
    def format_citation(self, entry, style='apa'):
        """格式化引用"""
        if style == 'apa':
            return self._format_apa(entry)
        elif style == 'mla':
            return self._format_mla(entry)
        elif style == 'chicago':
            return self._format_chicago(entry)
        elif style == 'ieee':
            return self._format_ieee(entry)
    
    def _format_apa(self, entry):
        """APA格式"""
        authors = entry.get('author', 'Unknown')
        year = entry.get('year', 'n.d.')
        title = entry.get('title', 'Untitled')
        journal = entry.get('journal', '')
        volume = entry.get('volume', '')
        pages = entry.get('pages', '')
        
        citation = f"{authors} ({year}). {title}."
        if journal:
            citation += f" {journal}"
            if volume:
                citation += f", {volume}"
            if pages:
                citation += f", {pages}"
            citation += "."
        
        return citation
    
    def generate_bibliography(self, output_file):
        """生成参考文献列表"""
        formatted_refs = []
        
        for ref in self.references:
            formatted = self.format_citation(ref, self.style)
            formatted_refs.append(formatted)
        
        # 排序（通常按作者姓氏）
        formatted_refs.sort()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for ref in formatted_refs:
                f.write(ref + '\n\n')
        
        return formatted_refs
    
    def check_citation_consistency(self, text, references):
        """检查引用一致性"""
        # 提取文中的引用
        in_text_citations = self._extract_citations(text)
        
        # 检查是否都在参考文献中
        missing_refs = []
        for citation in in_text_citations:
            if not self._citation_in_references(citation, references):
                missing_refs.append(citation)
        
        return {
            'total_citations': len(in_text_citations),
            'missing_references': missing_refs,
            'consistency_score': 100 - (len(missing_refs) / max(len(in_text_citations), 1)) * 100
        }
```

## 总结

这五项核心研究技能构成了一个完整的研究能力体系，每项技能都包含：

1. **明确的能力要求**：定义了需要掌握的核心能力
2. **实用的优化工具**：提供了自动化和辅助工具
3. **标准化流程**：确保工作质量和一致性
4. **持续改进机制**：通过使用反馈不断优化

通过系统化地培养和应用这些技能，研究员可以显著提升研究效率和质量。

## 下一步行动

1. **评估当前能力**：对照每项技能的要求，评估自己的强项和弱项
2. **制定学习计划**：优先提升关键弱项
3. **实践应用工具**：在实际研究中使用提供的工具和脚本
4. **持续优化**：根据使用经验改进工具和流程
5. **分享经验**：与团队分享最佳实践

这个技能框架将帮助你在研究工作中更加专业、高效和系统化！
