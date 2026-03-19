import requests
import feedparser
import json
import os
from datetime import datetime
from deep_translator import GoogleTranslator

def search_arxiv(keywords=['icequake', 'glacier', 'seismology', '冰川地震学'], max_results=20):
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
            # 翻译摘要
            translated_abstract = translator.translate(abstract)
        except Exception as e:
            print(f"翻译失败: {e}")
            translated_abstract = "翻译失败"

        paper = {
            'id': entry.id.split('/')[-1],
            'title': entry.title.replace('\n', ' '),
            'abstract': abstract,
            'translated_abstract': translated_abstract,
            'authors': [author.name for author in entry.authors],
            'published': entry.published,
            'updated': entry.updated,
            'categories': [tag.term for tag in entry.tags],
            'first_author': entry.authors[0].name if entry.authors else "N/A",
            'importance': "冰川地震学研究对于理解气候变化、冰川动力学和自然灾害风险评估具有重要意义。",
            'related_work': "前人研究主要集中在：1) 冰川地震的检测与分类；2) 冰川运动与地震活动的关系；3) 冰川湖溃决洪水的预警研究。",
            'methods': "基于论文摘要，本文可能采用了：地震波数据分析、GPS观测、数值模拟等方法。",
            'innovation': "本文的潜在创新点可能包括：新的检测算法、多源数据融合方法、或对冰川地震机制的新见解。"
        }
        papers.append(paper)

    return papers

if __name__ == "__main__":
    try:
        results = search_arxiv()

        # 确保目录存在 - 修改为前端目录
        target_dir = 'frontend'
        os.makedirs(target_dir, exist_ok=True)

        # 保存为前端使用的 JSON
        output = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'papers': results
        }

        data_path = os.path.join(target_dir, 'data.json')
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"数据已更新并保存至 {data_path}")

        # 生成邮件正文预览
        with open('email_body.txt', 'w', encoding='utf-8') as f:
            f.write(f"冰川地震学论文周报 (更新时间: {output['last_update']})\n")
            f.write("="*50 + "\n\n")
            for p in results[:10]: # 发送前10篇
                f.write(f"标题: {p['title']}\n")
                f.write(f"作者: {', '.join(p['authors'][:3])}\n")
                f.write(f"日期: {p['published']}\n")
                f.write(f"摘要(中): {p['translated_abstract'][:300]}...\n")
                f.write(f"链接: https://arxiv.org/abs/{p['id']}\n")
                f.write("-" * 30 + "\n\n")
        print("邮件正文已生成至 email_body.txt")

    except Exception as e:
        print(f"脚本运行出错: {e}")
