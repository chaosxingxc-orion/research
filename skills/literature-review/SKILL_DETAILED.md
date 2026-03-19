---
name: "literature-review"
description: "Systematic literature search, evaluation and synthesis. Invoke when starting new research, understanding field status, or writing literature review sections."
---

# Literature Review Skill

## Core Competencies Required

### 1. Information Retrieval Skills
- **Database Searching**: Master PubMed, IEEE, ACM, Google Scholar, arXiv
- **Search Strategy Design**: Boolean operators, keyword combination, filters
- **Snowballing**: Forward and backward citation tracking
- **Grey Literature**: Conference proceedings, preprints, theses

### 2. Critical Appraisal Skills
- **Study Design Evaluation**: RCT, cohort, case-control, cross-sectional
- **Bias Assessment**: Selection, performance, detection, reporting bias
- **Quality Assessment Tools**: CASP, Cochrane RoB, Newcastle-Ottawa Scale
- **Evidence Grading**: GRADE system, evidence hierarchy

### 3. Information Synthesis Skills
- **Data Extraction**: Systematic data collection and organization
- **Thematic Analysis**: Identify patterns and themes across studies
- **Meta-Analysis**: Statistical synthesis when appropriate
- **Narrative Synthesis**: Qualitative integration of findings

### 4. Academic Writing Skills
- **Structure Organization**: Chronological, thematic, methodological
- **Critical Integration**: Compare, contrast, synthesize findings
- **Gap Identification**: Highlight research opportunities
- **Citation Management**: Proper attribution and formatting

## Optimization Tools & Scripts

### Automated Search Scripts

#### 1. Multi-Database Search Automation
```python
# search_automation.py
import requests
import json
from datetime import datetime

class LiteratureSearcher:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        
    def search_pubmed(self, query, max_results=100):
        """Search PubMed database"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'datetype': 'pdat'
        }
        response = requests.get(base_url, params=params)
        return response.json()
    
    def search_arxiv(self, query, max_results=50):
        """Search arXiv preprints"""
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': query,
            'max_results': max_results
        }
        response = requests.get(base_url, params=params)
        return response.text
    
    def search_ieee(self, query, max_results=50):
        """Search IEEE Xplore"""
        # Requires IEEE API key
        base_url = "http://ieeexploreapi.ieee.org/api/v1/search/articles"
        params = {
            'apikey': self.api_keys['ieee'],
            'querytext': query,
            'max_records': max_results
        }
        response = requests.get(base_url, params=params)
        return response.json()
    
    def aggregate_results(self, queries):
        """Aggregate results from multiple databases"""
        results = {
            'pubmed': [],
            'arxiv': [],
            'ieee': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for query in queries:
            results['pubmed'].extend(self.search_pubmed(query))
            results['arxiv'].extend(self.search_arxiv(query))
            results['ieee'].extend(self.search_ieee(query))
        
        return results

# Usage
searcher = LiteratureSearcher(api_keys={'ieee': 'YOUR_KEY'})
queries = [
    '("deep learning" OR "neural networks") AND "medical imaging"',
    '("artificial intelligence" OR "machine learning") AND healthcare'
]
results = searcher.aggregate_results(queries)
```

#### 2. Citation Network Analysis
```python
# citation_analysis.py
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

class CitationAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def build_citation_network(self, papers):
        """Build citation network from paper list"""
        for paper in papers:
            self.graph.add_node(paper['id'], 
                              title=paper['title'],
                              year=paper['year'])
            
            for cited_id in paper['citations']:
                self.graph.add_edge(paper['id'], cited_id)
        
        return self.graph
    
    def find_key_papers(self):
        """Identify highly cited papers (key works)"""
        in_degrees = dict(self.graph.in_degree())
        sorted_papers = sorted(in_degrees.items(), 
                              key=lambda x: x[1], 
                              reverse=True)
        return sorted_papers[:20]  # Top 20
    
    def detect_research_fronts(self):
        """Identify recent highly cited papers"""
        recent_papers = [
            node for node in self.graph.nodes()
            if self.graph.nodes[node]['year'] >= 2020
        ]
        
        recent_citations = {
            paper: self.graph.in_degree(paper)
            for paper in recent_papers
        }
        
        return sorted(recent_citations.items(), 
                     key=lambda x: x[1], 
                     reverse=True)
    
    def visualize_network(self, output_file='citation_network.png'):
        """Visualize citation network"""
        plt.figure(figsize=(15, 10))
        
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        node_sizes = [100 * (self.graph.in_degree(node) + 1) 
                     for node in self.graph.nodes()]
        
        nx.draw(self.graph, pos, 
               node_size=node_sizes,
               node_color='lightblue',
               with_labels=False,
               arrows=True)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

# Usage
analyzer = CitationAnalyzer()
analyzer.build_citation_network(papers_list)
key_papers = analyzer.find_key_papers()
research_fronts = analyzer.detect_research_fronts()
analyzer.visualize_network()
```

#### 3. Duplicate Detection & Deduplication
```python
# deduplication.py
import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

class DuplicateDetector:
    def __init__(self, threshold=85):
        self.threshold = threshold
        
    def calculate_similarity(self, title1, title2):
        """Calculate title similarity using fuzzy matching"""
        return fuzz.ratio(title1.lower(), title2.lower())
    
    def find_duplicates(self, papers):
        """Identify duplicate papers"""
        duplicates = []
        n = len(papers)
        
        for i in tqdm(range(n)):
            for j in range(i+1, n):
                similarity = self.calculate_similarity(
                    papers[i]['title'],
                    papers[j]['title']
                )
                
                if similarity >= self.threshold:
                    duplicates.append({
                        'paper1': papers[i],
                        'paper2': papers[j],
                        'similarity': similarity
                    })
        
        return duplicates
    
    def deduplicate(self, papers, keep='most_complete'):
        """Remove duplicates, keeping best version"""
        duplicates = self.find_duplicates(papers)
        
        to_remove = set()
        for dup in duplicates:
            if keep == 'most_complete':
                # Keep paper with more information
                if len(dup['paper1']['abstract']) > len(dup['paper2']['abstract']):
                    to_remove.add(dup['paper2']['id'])
                else:
                    to_remove.add(dup['paper1']['id'])
            elif keep == 'newest':
                # Keep most recent paper
                if dup['paper1']['year'] >= dup['paper2']['year']:
                    to_remove.add(dup['paper2']['id'])
                else:
                    to_remove.add(dup['paper1']['id'])
        
        return [p for p in papers if p['id'] not in to_remove]
```

### Quality Assessment Tools

#### 4. Automated Quality Scoring
```python
# quality_assessment.py

class QualityAssessor:
    def __init__(self):
        self.criteria = {
            'randomization': 0,
            'blinding': 0,
            'sample_size': 0,
            'follow_up': 0,
            'statistical_analysis': 0
        }
    
    def assess_rct(self, paper):
        """Assess RCT quality using CASP criteria"""
        score = 0
        
        # Check randomization
        if paper.get('randomization'):
            score += 2
            if paper.get('randomization_method'):
                score += 1
        
        # Check blinding
        if paper.get('blinding'):
            score += 2
            if paper.get('blinding_type') == 'double':
                score += 1
        
        # Sample size justification
        if paper.get('power_calculation'):
            score += 2
        
        # Follow-up rate
        if paper.get('follow_up_rate', 0) >= 80:
            score += 2
        elif paper.get('follow_up_rate', 0) >= 60:
            score += 1
        
        # Statistical analysis
        if paper.get('intention_to_treat'):
            score += 2
        
        return {
            'total_score': score,
            'max_score': 10,
            'percentage': (score / 10) * 100,
            'quality_level': self._categorize_quality(score)
        }
    
    def _categorize_quality(self, score):
        """Categorize quality based on score"""
        if score >= 8:
            return 'High'
        elif score >= 5:
            return 'Moderate'
        else:
            return 'Low'
    
    def batch_assess(self, papers):
        """Assess multiple papers"""
        results = []
        for paper in papers:
            assessment = self.assess_rct(paper)
            results.append({
                'paper_id': paper['id'],
                'title': paper['title'],
                **assessment
            })
        
        return pd.DataFrame(results)
```

### Visualization & Reporting

#### 5. PRISMA Flow Diagram Generator
```python
# prisma_generator.py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class PRISMAFlowGenerator:
    def __init__(self):
        self.stages = {
            'identification': 0,
            'duplicates': 0,
            'screening': 0,
            'excluded_title_abstract': 0,
            'full_text_assessed': 0,
            'excluded_full_text': 0,
            'included': 0
        }
    
    def update_stage(self, stage, count):
        """Update stage counts"""
        self.stages[stage] = count
    
    def generate_diagram(self, output_file='prisma_flow.png'):
        """Generate PRISMA flow diagram"""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Draw boxes and arrows
        boxes = [
            (5, 11, f"Identification\n{self.stages['identification']} records"),
            (5, 9, f"Duplicates removed\n{self.stages['duplicates']} records"),
            (5, 7, f"Records screened\n{self.stages['screening']} records"),
            (2, 5, f"Full-text assessed\n{self.stages['full_text_assessed']} records"),
            (8, 5, f"Excluded\n{self.stages['excluded_title_abstract']} records"),
            (2, 3, f"Studies included\n{self.stages['included']} studies"),
            (8, 3, f"Excluded\n{self.stages['excluded_full_text']} studies")
        ]
        
        for x, y, text in boxes:
            box = mpatches.FancyBboxPatch(
                (x-1.5, y-0.5), 3, 1,
                boxstyle="round,pad=0.1",
                facecolor='lightblue',
                edgecolor='black'
            )
            ax.add_patch(box)
            ax.text(x, y, text, ha='center', va='center', fontsize=10)
        
        # Add arrows (simplified)
        arrow_style = dict(arrowstyle='->', lw=1.5, color='black')
        arrows = [
            ((5, 10.5), (5, 9.5)),
            ((5, 8.5), (5, 7.5)),
            ((3.5, 6.5), (2, 5.5)),
            ((6.5, 6.5), (8, 5.5)),
            ((2, 4.5), (2, 3.5)),
            ((8, 4.5), (8, 3.5))
        ]
        
        for start, end in arrows:
            ax.annotate('', xy=end, xytext=start,
                       arrowprops=arrow_style)
        
        plt.title('PRISMA Flow Diagram', fontsize=14, fontweight='bold')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file

# Usage
prisma = PRISMAFlowGenerator()
prisma.update_stage('identification', 1250)
prisma.update_stage('duplicates', 150)
prisma.update_stage('screening', 1100)
prisma.update_stage('excluded_title_abstract', 800)
prisma.update_stage('full_text_assessed', 300)
prisma.update_stage('excluded_full_text', 200)
prisma.update_stage('included', 100)
prisma.generate_diagram()
```

## Workflow Integration

### Complete Literature Review Pipeline
```bash
#!/bin/bash
# literature_review_pipeline.sh

echo "Starting Literature Review Pipeline..."

# 1. Execute multi-database search
echo "Step 1: Multi-database search..."
python search_automation.py --config search_config.json --output raw_results.json

# 2. Deduplicate results
echo "Step 2: Removing duplicates..."
python deduplication.py --input raw_results.json --output deduplicated_results.json

# 3. Assess quality
echo "Step 3: Quality assessment..."
python quality_assessment.py --input deduplicated_results.json --output quality_scores.csv

# 4. Analyze citation network
echo "Step 4: Citation network analysis..."
python citation_analysis.py --input deduplicated_results.json --output network_analysis/

# 5. Generate PRISMA diagram
echo "Step 5: Generating PRISMA flow diagram..."
python prisma_generator.py --counts screening_counts.json --output figures/prisma_flow.png

# 6. Generate summary report
echo "Step 6: Generating summary report..."
python generate_report.py --results deduplicated_results.json --quality quality_scores.csv --output report/

echo "Literature review pipeline completed!"
```

## Best Practices

### 1. Search Strategy
- Use multiple databases for comprehensive coverage
- Include both controlled vocabulary (MeSH) and keywords
- Document all search strategies for reproducibility
- Update searches before final submission

### 2. Quality Assessment
- Use validated assessment tools (CASP, Cochrane)
- Involve multiple reviewers
- Resolve disagreements through discussion or third party
- Document assessment decisions

### 3. Data Management
- Use reference management software (Zotero, Mendeley)
- Maintain organized file structure
- Backup data regularly
- Version control all scripts and protocols

### 4. Reporting Standards
- Follow PRISMA guidelines for systematic reviews
- Register protocol in PROSPERO
- Provide complete search strategies in supplementary materials
- Include PRISMA flow diagram

## Tools & Resources

### Reference Management
- **Zotero**: Free, open-source, with cloud sync
- **Mendeley**: PDF reader integration, social features
- **EndNote**: Industry standard, institutional licenses

### Systematic Review Platforms
- **Covidence**: Web-based, collaborative
- **Rayyan**: AI-assisted screening
- **DistillerSR**: Advanced features, enterprise

### Analysis Software
- **RevMan**: Cochrane's meta-analysis tool
- **MetaXL**: Excel add-in for meta-analysis
- **R packages**: meta, metafor, dmetar

### Visualization
- **VOSviewer**: Bibliometric visualization
- **CiteSpace**: Citation network analysis
- **Gephi**: Network analysis and visualization
