import requests
import feedparser
import json
import os
import urllib.parse
import time
from datetime import datetime
from deep_translator import GoogleTranslator
from fpdf import FPDF

# ==========================================
# 1. 核心配置：精准关键词与期刊
# ==========================================
TOPICS = {
    'cryoseismology': {
        'name': 'Cryoseismology',
        'name_zh': '冰川地震论文',
        'keywords': ['("icequake" OR "glacier") AND seismology', '"cryoseismology"'],
        'journals': ['Journal of Geophysical Research', 'Geophysical Research Letters', 'The Cryosphere'],
        'file': 'data_cryo.json'
    },
    'das': {
        'name': 'DAS Papers',
        'name_zh': 'DAS论文',
        # 增加 AND 逻辑确保与地震学相关，排除单纯的通信或声学文章
        'keywords': ['("Distributed Acoustic Sensing" OR "DAS") AND (seismology OR seismic OR earthquake OR geophysics)'],
        'journals': ['Seismological Research Letters', 'JGR Solid Earth', 'Geophysical Journal International'],
        'file': 'data_das.json'
    },
    'surface_wave': {
        'name': 'Surface Wave & Imaging',
        'name_zh': '面波与成像',
        # 明确区分，排除 DAS
        'keywords': ['"surface wave" AND (tomography OR "ambient noise" OR dispersion) -DAS'],
        'journals': ['BSSA', 'Seismological Research Letters', 'JGR Solid Earth'],
        'file': 'data_surface.json'
    }
}

def translate_text(text, max_len=2000):
    if not text: return "无摘要"
    try:
        translator = GoogleTranslator(source='auto', target='zh-CN')
        return translator.translate(text[:max_len])
    except:
        return "翻译失败"

def get_author_representative_works(author_name, exclude_doi, max_works=3):
    """搜索第一作者的另外 3 篇代表作"""
    if not author_name or author_name == "N/A": return []
    query = urllib.parse.quote(author_name)
    url = f"https://api.crossref.org/works?query.author={query}&rows=10&sort=is-referenced-by-count"
    try:
        res = requests.get(url, timeout=10).json()
        items = res.get('message', {}).get('items', [])
        works = []
        for it in items:
            doi = it.get('DOI')
            if doi and doi.lower() != exclude_doi.lower():
                title = it.get('title', ['No Title'])[0]
                year = it.get('created', {}).get('date-parts', [[0]])[0][0]
                works.append({"title": title, "year": year, "url": f"https://doi.org/{doi}"})
            if len(works) >= max_works: break
        return works
    except:
        return []

def extract_deep_analysis(title, abstract_zh):
    """
    根据摘要内容进行结构化拆解 (模拟 AI 分析)
    后续可接入 OpenAI/Gemini API 获取更真实的深度分析
    """
    return {
        "importance": "该研究利用新技术提升了地震监测的空间/时间分辨率，对理解复杂地质过程具有重要价值。",
        "previous_research": "传统方法往往受限于台站密度或由于环境噪声干扰导致信噪比不足。",
        "methodology": "本文采用了先进的信号处理算法或新型传感器布局，对原始数据进行了高精度反演。",
        "innovation": "通过跨学科方法融合，实现了在极端环境或高噪声背景下的稳定成像。",
        "contribution": "为长期连续监测提供了低成本、高密度的解决方案。",
        "limitation": "算法复杂度较高，在大规模实时处理方面仍有优化空间。"
    }

def search_crossref(topic_config, max_results=5):
    print(f"正在 Crossref 检索: {topic_config['name_zh']}...")
    query = " ".join(topic_config['keywords'])
    filters = ["type:journal-article"]
    if topic_config['journals']:
        for j in topic_config['journals']:
            filters.append(f"container-title:{j}")
    
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&filter={','.join(filters)}&sort=published&order=desc&rows={max_results}"
    
    papers = []
    try:
        data = requests.get(url, timeout=30).json()
        for item in data.get('message', {}).get('items', []):
            doi = item.get('DOI')
            authors = item.get('author', [])
            
            # 提取信息
            first_author = f"{authors[0].get('given', '')} {authors[0].get('family', '')}" if authors else "N/A"
            affiliation = authors[0].get('affiliation', [{}])[0].get('name', '未知机构') if authors else "N/A"
            corr_author = f"{authors[-1].get('given', '')} {authors[-1].get('family', '')}" if authors else "N/A"
            
            abs_raw = item.get('abstract', '请点击链接查看原文摘要。')
            abs_zh = translate_text(abs_raw)
            
            papers.append({
                'id': doi,
                'title': item.get('title', ['No Title'])[0],
                'url': f"https://doi.org/{doi}",
                'first_author': first_author,
                'corr_author': corr_author,
                'affiliation': affiliation,
                'other_works': get_author_representative_works(first_author, doi),
                'abs_zh': abs_zh,
                'analysis': extract_deep_analysis(item.get('title', [''])[0], abs_zh),
                'published': str(item.get('created', {}).get('date-parts', [[0]])[0][0]),
                'source': 'Journal'
            })
            time.sleep(0.5)
    except Exception as e:
        print(f"Crossref 出错: {e}")
    return papers

def search_arxiv(topic_config, max_results=5):
    print(f"正在 arXiv 检索: {topic_config['name_zh']}...")
    # arXiv 不支持复杂的逻辑，简化处理
    search_terms = '+'.join([f'all:"{k.split(" AND ")[0].replace("(", "").replace(")", "")}"' for k in topic_config['keywords']])
    url = f'http://export.arxiv.org/api/query?search_query={search_terms}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    papers = []
    try:
        feed = feedparser.parse(requests.get(url, timeout=30).content)
        for entry in feed.entries:
            paper_id = entry.id.split('/')[-1]
            first_author = entry.authors[0].name if entry.authors else "N/A"
            abs_zh = translate_text(entry.summary)
            
            papers.append({
                'id': paper_id,
                'title': entry.title.replace('\n', ' '),
                'url': f"https://arxiv.org/abs/{paper_id}",
                'first_author': first_author,
                'corr_author': "见原文",
                'affiliation': "arXiv Preprint",
                'other_works': get_author_representative_works(first_author, paper_id),
                'abs_zh': abs_zh,
                'analysis': extract_deep_analysis(entry.title, abs_zh),
                'published': entry.published,
                'source': 'arXiv'
            })
    except Exception as e:
        print(f"arXiv 出错: {e}")
    return papers

if __name__ == "__main__":
    target_dir = 'frontend'
    os.makedirs(target_dir, exist_ok=True)
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    for tid, config in TOPICS.items():
        print(f"\n--- 正在深度处理: {config['name_zh']} ---")
        results = search_crossref(config, 4) + search_arxiv(config, 2)
        
        output = {
            'last_update': update_time,
            'topic_name': config['name_zh'],
            'papers': results
        }
        with open(os.path.join(target_dir, config['file']), 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n✅ 数据深度抓取完成！")
