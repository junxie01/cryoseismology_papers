#!/usr/bin/env python3
"""
生成论文周报 PDF 和邮件内容
文件名格式: paper_report_YYYYMMDD_YYYYMMDD.pdf
"""

import json
import os
from datetime import datetime, timedelta
from fpdf import FPDF

# 计算日期范围（最近7天）
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
start_str = start_date.strftime('%Y%m%d')
end_str = end_date.strftime('%Y%m%d')
date_range_display = f"{start_date.strftime('%Y年%m月%d日')}-{end_date.strftime('%Y年%m月%d日')}"

# 专题配置文件
TOPICS = [
    ('data_cryo.json', '冰川地震'),
    ('data_das.json', '光纤传感'),
    ('data_surface.json', '面波研究'),
    ('data_imaging.json', '地震成像'),
    ('data_earthquake.json', '地震研究'),
    ('data_ai.json', '人工智能')
]

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f'论文周报 ({date_range_display})', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def load_papers():
    """加载所有专题的论文数据"""
    all_papers = []
    for filename, topic_name in TOPICS:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for paper in data.get('papers', []):
                        paper['topic'] = topic_name
                        all_papers.append(paper)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return all_papers

def generate_pdf(papers, output_file):
    """生成 PDF 报告"""
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 尝试使用支持中文的字体
    try:
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
        font_name = 'DejaVu'
    except:
        font_name = 'Arial'
    
    if not papers:
        pdf.set_font(font_name, '', 12)
        pdf.cell(0, 10, 'No papers found for this period.', 0, 1)
        pdf.output(output_file)
        return
    
    # 按专题分组
    papers_by_topic = {}
    for paper in papers:
        topic = paper.get('topic', '其他')
        if topic not in papers_by_topic:
            papers_by_topic[topic] = []
        papers_by_topic[topic].append(paper)
    
    for topic, topic_papers in papers_by_topic.items():
        pdf.set_font(font_name, 'B', 14)
        pdf.cell(0, 10, f'【{topic}】', 0, 1)
        pdf.ln(2)
        
        for i, paper in enumerate(topic_papers[:5], 1):  # 每个专题最多显示5篇
            pdf.set_font(font_name, 'B', 11)
            title = paper.get('title', 'No Title')[:80]
            pdf.multi_cell(0, 6, f"{i}. {title}")
            
            pdf.set_font(font_name, '', 10)
            authors = paper.get('first_author', 'N/A')
            if paper.get('corr_author') and paper.get('corr_author') != 'N/A':
                authors += f", {paper.get('corr_author')}"
            
            source = paper.get('source', 'Unknown Journal')
            pdf.cell(0, 5, f"作者: {authors}", 0, 1)
            pdf.cell(0, 5, f"期刊: {source}", 0, 1)
            
            # 摘要（前200字符）
            abs_zh = paper.get('abs_zh', '')
            if abs_zh and abs_zh != '无摘要详情':
                pdf.set_font(font_name, '', 9)
                abs_text = abs_zh[:200] + '...' if len(abs_zh) > 200 else abs_zh
                pdf.multi_cell(0, 5, f"摘要: {abs_text}")
            
            pdf.ln(3)
        
        pdf.ln(5)
    
    pdf.output(output_file)
    print(f"PDF generated: {output_file}")

def generate_email_body(papers, output_file):
    """生成邮件正文"""
    lines = [
        f"{date_range_display}，论文周报更新，请查收。",
        "",
        "=" * 50,
        ""
    ]
    
    if not papers:
        lines.append("本期暂无新论文。")
    else:
        # 按专题分组
        papers_by_topic = {}
        for paper in papers:
            topic = paper.get('topic', '其他')
            if topic not in papers_by_topic:
                papers_by_topic[topic] = []
            papers_by_topic[topic].append(paper)
        
        for topic, topic_papers in papers_by_topic.items():
            lines.append(f"【{topic}】")
            lines.append("-" * 30)
            
            for i, paper in enumerate(topic_papers[:5], 1):
                title = paper.get('title', 'No Title')
                authors = paper.get('first_author', 'N/A')
                if paper.get('corr_author') and paper.get('corr_author') != 'N/A':
                    authors += f", {paper.get('corr_author')}"
                
                source = paper.get('source', 'Unknown Journal')
                url = paper.get('url', '')
                
                lines.append(f"{i}. {title}")
                lines.append(f"   作者: {authors}")
                lines.append(f"   期刊: {source}")
                if url:
                    lines.append(f"   链接: {url}")
                lines.append("")
            
            lines.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Email body generated: {output_file}")

if __name__ == "__main__":
    papers = load_papers()
    
    # 生成带日期范围的文件名
    pdf_filename = f"paper_report_{start_str}_{end_str}.pdf"
    
    generate_pdf(papers, pdf_filename)
    generate_email_body(papers, 'email_body.txt')
    
    print(f"\n报告生成完成!")
    print(f"PDF文件: {pdf_filename}")
    print(f"日期范围: {date_range_display}")
