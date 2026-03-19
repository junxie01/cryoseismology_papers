# 🧊 冰川地震学论文周报系统 (Hexo 集成版)

一个自动追踪 arXiv 冰川地震学相关论文并自动翻译、分析的静态网页应用，完美集成于 Hexo 博客。

## 🚀 工作流程

1.  **自动化更新**：GitHub Actions 每周日自动运行 Python 脚本。
2.  **数据抓取**：抓取关键词 `icequake`, `glacier`, `seismology` 的最新论文。
3.  **翻译与分析**：使用 Google Translate 自动翻译摘要。
4.  **静态发布**：生成的 `data.json` 自动提交到仓库，Hexo 站点读取该文件展示。
5.  **邮件通知**：更新完成后自动发送周报到您的邮箱。

## 📂 项目结构

- `update_papers.py`: 核心 Python 脚本，负责数据抓取 and 处理。
- `frontend/`: 网页前端代码。
  - `index.html`: 展示页面。
  - `app.js`: 异步加载 `data.json` 并渲染。
  - `data.json`: 存储论文数据的静态文件（由脚本自动生成）。
- `.github/workflows/update.yml`: GitHub 自动化任务配置。

## 🛠️ 如何集成到 Hexo

1.  **复制文件**：将 `frontend` 文件夹更名为 `cryoseismology_papers`，复制到 Hexo 项目的 `source/` 目录下。
2.  **配置菜单**：在 Hexo 主题的 `_config.yml` 中添加菜单项：
    ```yaml
    menu:
      Papers: /cryoseismology_papers/
    ```
3.  **跳过渲染 (可选)**：如果 Hexo 报错，在 Hexo 的 `_config.yml` 中设置：
    ```yaml
    skip_render:
      - "cryoseismology_papers/**"
    ```

## 📧 邮件通知设置

在 GitHub 仓库的 **Settings > Secrets > Actions** 中添加：
- `MAIL_USERNAME`: 发件邮箱。
- `MAIL_PASSWORD`: 邮箱 SMTP 授权码。
- `MAIL_TO`: 您的收件邮箱。

## 许可证

MIT License
