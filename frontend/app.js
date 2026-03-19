let papers = [];

document.addEventListener('DOMContentLoaded', () => {
    loadPapers();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('paper-modal').addEventListener('click', (e) => {
        if (e.target.id === 'paper-modal') {
            closeModal();
        }
    });
}

async function loadPapers() {
    showLoading();
    try {
        // 加载生成的静态 JSON 数据
        const response = await fetch('./data.json');
        if (!response.ok) {
            throw new Error('无法加载数据文件');
        }
        const data = await response.json();
        papers = data.papers;

        // 更新显示最后更新时间
        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = data.last_update || '未知';
        }

        renderPapersList();
    } catch (error) {
        console.error('加载论文失败:', error);
        const container = document.getElementById('papers-list');
        container.innerHTML = `
            <div class="empty-state">
                <h2>❌ 加载失败</h2>
                <p>无法获取论文数据，请稍后再试。</p>
                <p style="font-size: 0.8rem; color: #999;">错误详情: ${error.message}</p>
            </div>
        `;
    } finally {
        hideLoading();
    }
}

function loadPaperDetail(paperId) {
    const paper = papers.find(p => p.id === paperId);
    if (paper) {
        showModal(paper);
    }
}

function renderPapersList() {
    const container = document.getElementById('papers-list');
    
    if (!papers || papers.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h2>📚 暂无论文</h2>
                <p>目前没有找到相关的论文。</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = papers.map(paper => `
        <div class="paper-card" onclick="loadPaperDetail('${paper.id}')">
            <h3>${escapeHtml(paper.title)}</h3>
            <div class="paper-meta">
                <span>📅 ${formatDate(paper.published)}</span>
                <span>👥 ${paper.authors.length} 位作者</span>
            </div>
            <div class="paper-authors">
                ${paper.authors.slice(0, 3).map(a => escapeHtml(a)).join(', ')}${paper.authors.length > 3 ? ' 等' : ''}
            </div>
            <div class="paper-abstract">${escapeHtml(paper.translated_abstract ? paper.translated_abstract.substring(0, 200) : paper.abstract.substring(0, 200))}...</div>
            <div class="paper-categories">
                ${paper.categories.slice(0, 3).map(cat => `<span class="category-tag">${escapeHtml(cat)}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function showModal(paper) {
    document.getElementById('modal-title').textContent = paper.title;
    
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <div class="info-grid">
            <div class="info-box">
                <h4>第一作者</h4>
                <p>${escapeHtml(paper.first_author || 'N/A')}</p>
            </div>
            <div class="info-box">
                <h4>发表日期</h4>
                <p>${formatDate(paper.published)}</p>
            </div>
            <div class="info-box">
                <h4>ID</h4>
                <p>${escapeHtml(paper.id)}</p>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>📄 摘要（中文翻译）</h3>
            <p>${escapeHtml(paper.translated_abstract || '暂无翻译')}</p>
        </div>

        <div class="analysis-section">
            <h3>🎯 研究重要性</h3>
            <p>${escapeHtml(paper.importance || '分析中...')}</p>
        </div>
        
        <div class="analysis-section">
            <h3>🔬 数据与方法</h3>
            <p>${escapeHtml(paper.methods || '分析中...')}</p>
        </div>

        <div class="analysis-section">
            <h3>💡 创新与贡献</h3>
            <p>${escapeHtml(paper.innovation || '分析中...')}</p>
        </div>
        
        <div class="analysis-section">
            <h3>📋 所有作者</h3>
            <p>${paper.authors.map(a => escapeHtml(a)).join('; ')}</p>
        </div>
        
        <div class="analysis-section">
            <h3>🏷️ 分类</h3>
            <div class="paper-categories">
                ${paper.categories.map(cat => `<span class="category-tag">${escapeHtml(cat)}</span>`).join('')}
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>🔗 原文链接</h3>
            <p><a href="https://arxiv.org/abs/${paper.id}" target="_blank" rel="noopener noreferrer">https://arxiv.org/abs/${paper.id}</a></p>
        </div>
    `;
    
    document.getElementById('paper-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('paper-modal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
