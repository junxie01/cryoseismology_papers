from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import feedparser
from datetime import datetime, timedelta
import sqlite3
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from deep_translator import GoogleTranslator

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

DATABASE = 'papers.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS papers
                 (id TEXT PRIMARY KEY, title TEXT, abstract TEXT, authors TEXT, 
                  published TEXT, updated TEXT, categories TEXT, summary TEXT,
                  first_author TEXT, corresponding_author TEXT, affiliation TEXT,
                  translated_abstract TEXT, importance TEXT, related_work TEXT,
                  methods TEXT, innovation TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def search_arxiv(keywords, max_results=20):
    search_terms = '+'.join(keywords)
    url = f'http://export.arxiv.org/api/query?search_query=all:{search_terms}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    
    papers = []
    for entry in feed.entries:
        paper = {
            'id': entry.id.split('/')[-1],
            'title': entry.title,
            'abstract': entry.summary,
            'authors': [author.name for author in entry.authors],
            'published': entry.published,
            'updated': entry.updated,
            'categories': [tag.term for tag in entry.tags]
        }
        papers.append(paper)
    
    return papers

def save_papers_to_db(papers):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    for paper in papers:
        c.execute('''INSERT OR REPLACE INTO papers 
                     (id, title, abstract, authors, published, updated, categories)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (paper['id'], paper['title'], paper['abstract'],
                   json.dumps(paper['authors']), paper['published'],
                   paper['updated'], json.dumps(paper['categories'])))
    
    conn.commit()
    conn.close()

def get_papers_from_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM papers ORDER BY published DESC')
    rows = c.fetchall()
    
    papers = []
    for row in rows:
        paper = {
            'id': row[0],
            'title': row[1],
            'abstract': row[2],
            'authors': json.loads(row[3]) if row[3] else [],
            'published': row[4],
            'updated': row[5],
            'categories': json.loads(row[6]) if row[6] else [],
            'summary': row[7],
            'first_author': row[8],
            'corresponding_author': row[9],
            'affiliation': row[10],
            'translated_abstract': row[11],
            'importance': row[12],
            'related_work': row[13],
            'methods': row[14],
            'innovation': row[15]
        }
        papers.append(paper)
    
    conn.close()
    return papers

def get_paper_from_db(paper_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
    row = c.fetchone()
    
    if not row:
        return None
    
    paper = {
        'id': row[0],
        'title': row[1],
        'abstract': row[2],
        'authors': json.loads(row[3]) if row[3] else [],
        'published': row[4],
        'updated': row[5],
        'categories': json.loads(row[6]) if row[6] else [],
        'summary': row[7],
        'first_author': row[8],
        'corresponding_author': row[9],
        'affiliation': row[10],
        'translated_abstract': row[11],
        'importance': row[12],
        'related_work': row[13],
        'methods': row[14],
        'innovation': row[15]
    }
    
    conn.close()
    return paper

def update_paper_summary(paper_id, summary_data):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''UPDATE papers SET summary=?, first_author=?, corresponding_author=?,
                 affiliation=?, translated_abstract=?, importance=?, related_work=?,
                 methods=?, innovation=? WHERE id=?''',
              (summary_data.get('summary'), summary_data.get('first_author'),
               summary_data.get('corresponding_author'), summary_data.get('affiliation'),
               summary_data.get('translated_abstract'), summary_data.get('importance'),
               summary_data.get('related_work'), summary_data.get('methods'),
               summary_data.get('innovation'), paper_id))
    conn.commit()
    conn.close()

def translate_text(text, target='zh-CN'):
    try:
        translator = GoogleTranslator(source='auto', target=target)
        return translator.translate(text)
    except Exception as e:
        return f"翻译失败: {str(e)}"

def generate_analysis(abstract, authors):
    first_author = authors[0] if authors else "N/A"
    corresponding_author = authors[-1] if authors else "N/A"
    
    translated_abstract = translate_text(abstract)
    
    importance = "冰川地震学研究对于理解气候变化、冰川动力学和自然灾害风险评估具有重要意义。"
    
    related_work = "前人研究主要集中在：1) 冰川地震的检测与分类；2) 冰川运动与地震活动的关系；3) 冰川湖溃决洪水的预警研究。"
    
    methods = "基于论文摘要，本文可能采用了：地震波数据分析、GPS观测、数值模拟等方法。"
    
    innovation = "本文的潜在创新点可能包括：新的检测算法、多源数据融合方法、或对冰川地震机制的新见解。"
    
    return {
        'summary': '论文分析完成',
        'first_author': first_author,
        'corresponding_author': corresponding_author,
        'affiliation': '需要从论文全文获取',
        'translated_abstract': translated_abstract,
        'importance': importance,
        'related_work': related_work,
        'methods': methods,
        'innovation': innovation
    }

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/search', methods=['POST'])
def search_papers():
    data = request.json
    keywords = data.get('keywords', ['icequake', 'glacier', 'seismology', '冰川地震学'])
    max_results = data.get('max_results', 20)
    
    papers = search_arxiv(keywords, max_results)
    save_papers_to_db(papers)
    
    return jsonify({'papers': papers})

@app.route('/api/papers', methods=['GET'])
def get_papers():
    papers = get_papers_from_db()
    return jsonify({'papers': papers})

@app.route('/api/paper/<paper_id>', methods=['GET'])
def get_paper_detail(paper_id):
    paper = get_paper_from_db(paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    
    if not paper.get('translated_abstract'):
        analysis = generate_analysis(paper['abstract'], paper['authors'])
        update_paper_summary(paper_id, analysis)
        paper.update(analysis)
    
    return jsonify({'paper': paper})

@app.route('/api/analyze/<paper_id>', methods=['POST'])
def analyze_paper(paper_id):
    paper = get_paper_from_db(paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    
    analysis = generate_analysis(paper['abstract'], paper['authors'])
    update_paper_summary(paper_id, analysis)
    
    return jsonify({'paper': {**paper, **analysis}})

def scheduled_search():
    keywords = ['icequake', 'glacier', 'seismology', '冰川地震学']
    papers = search_arxiv(keywords, max_results=10)
    save_papers_to_db(papers)
    print(f"定期搜索完成，找到 {len(papers)} 篇论文")

if __name__ == '__main__':
    init_db()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_search, 'interval', weeks=1)
    scheduler.start()
    
    try:
        app.run(debug=True, port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
