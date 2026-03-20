import requests
import feedparser
import json
import os
from datetime import datetime
from deep_translator import GoogleTranslator
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # 设置字体支持中文 (由于 GitHub Actions 环境限制，我们使用系统默认字体或导出为简单的英文报告)
        # 如果需要完美中文支持，需要上传一个 .ttf 字体文件，这里先生成一个英文+拼音的增强版
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Cryoseismology Weekly Papers Report', 0, 1, 'C')
        self.ln(10)

def search_arxiv(keywords=['icequake', 'glacier', 'seismology', 'cryoseismology'], max_results=20):
    print(f"开始搜索 arXiv, 关键词: {keywords}...")
    search_terms = '+'.join([f'all:{k}' for k in keywords])
    url = f'http://export.arxiv.org/api/query?search_query={search_terms}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'

    response = requests.get(url)
    feed = feedparser.parse(response.content)

    papers = []
    translator = GoogleTranslator(source='auto', target='zh-CN')

    print(f"共找到 {len(feed.entries)} 篇论文，开始处理和翻译...")

    for entry in feed.entries:
        abstract = entry.summary.replace('\n', ' ')
        try:
            translated_abstract = translator.translate(abstract)
        except Exception as e:
            translated_abstract = "Translation Failed"

        paper = {
            'id': entry.id.split('/')[-1],
            'title': entry.title.replace('\n', ' '),
            'abstract': abstract,
            'translated_abstract': translated_abstract,
            'authors': [author.name for author in entry.authors],
            'published': entry.published,
            'updated': entry.updated,
            'categories': [tag.term for tag in entry.tags],
            'first_author': entry.authors[0].name if entry.authors else "N/A"
        }
        papers.append(paper)

    return papers

def generate_pdf(papers, filename='report.pdf'):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, p in enumerate(papers[:10]):
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 10, f"{i+1}. {p['title']}")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Authors: {', '.join(p['authors'][:3])}", 0, 1)
        pdf.cell(0, 10, f"Link: https://arxiv.org/abs/{p['id']}", 0, 1)
        pdf.ln(5)
        # 注意：由于 FPDF 默认库不支持 UTF-8 直接写入中文，
        # 我们在 PDF 中保留摘要的英文部分，以确保生成不会报错。
        # 中文翻译请在网页端查看。
        text = p['abstract'][:500] + "..."
        pdf.multi_cell(0, 5, text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)

    pdf.output(filename)
    print(f"PDF 报告已生成: {filename}")

if __name__ == "__main__":
    try:
        results = search_arxiv()

        # 1. 保存 JSON (用于网页)
        target_dir = 'frontend'
        os.makedirs(target_dir, exist_ok=True)
        output = {'last_update': datetime.now().strftime('%Y-%m-%d %H:%M'), 'papers': results}
        with open(os.path.join(target_dir, 'data.json'), 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        # 2. 生成 PDF (用于邮件附件)
        generate_pdf(results)

        # 3. 生成邮件正文
        with open('email_body.txt', 'w', encoding='utf-8') as f:
            f.write(f"冰川地震学论文周报已更新！\n\n")
            f.write(f"最后更新时间: {output['last_update']}\n")
            f.write(f"在线查看地址: https://www.seis-jun.xyz/cryoseismology_papers/frontend/\n\n")
            f.write("主要论文列表请查看附件 PDF。\n")

    except Exception as e:
        print(f"脚本运行出错: {e}")
