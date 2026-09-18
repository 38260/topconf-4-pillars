# 顶会四支柱文献看板 · TopConf Four Pillars

四大顶级会议（CVPR / AAAI / ICCV / ACL）**最新一届**真实论文的 HTML 看板。
数据全部来自官方或权威开放接口，逐条可回溯核验；摘要提供**人工中文翻译**并保留英文原文对照。

- 顶会：`CVPR 2026`（IEEE/CVF）、`AAAI 2026`、`ICCV 2025`、`ACL 2026`
- 规模：每会精选 12 篇，共 **48 篇**
- 视图：**四支柱**（一会一柱）+ **主题视图**（深度学习 / 大模型 / 边缘计算与高效推理 / 多模态 …）
- 风格：Claude 风格配色，组件设计模式参考 Trace Light（见 `docs/design-references.md`）

## 快速开始

```bash
# 方式一：零依赖本地服务（推荐，可用「回源刷新」）
python scripts/serve.py            # http://127.0.0.1:8765/

# 方式二：直接双击 web/index.html 打开（file:// 离线可看，数据已内联）
```

## 重新抓取真实数据

```bash
python scripts/fetch_corpus.py     # 拉取四会议官方全量目录 → data/corpus.json
python scripts/build_papers.py     # 按 data/selection.json 补摘要+翻译 → data/papers.json
python scripts/build_data.py       # 注入前端 web/data/papers.js
python scripts/verify.py           # 抽样回源核验，输出 docs/verification-report.md
```

原始响应缓存在 `data/raw/`（已 gitignore，避免把几十 MB 官方页面提交进仓库）。

## 目录

```
scripts/fetchlib/   官方源适配器：cvf.py / acl_anthology.py / openalex.py + http.py（缓存重试限速）
scripts/            fetch_corpus / build_papers / build_data / verify / serve
data/               corpus.json（全量目录）· selection.json（精选清单）· papers.json（展示数据）
web/                index.html + css/ + js/ + data/papers.js（内联快照，file:// 可用）
docs/               design-references.md · verification-report.md
TODO.md             全局待办真源，每次完成同步并随代码提交
```

## 数据源

| 支柱 | 官方源 | 抓取内容 |
|------|--------|----------|
| CVPR 2026 | openaccess.thecvf.com（CVF 开放获取） | 标题 / 作者 / 官方摘要 / PDF / 页码 |
| ICCV 2025 | openaccess.thecvf.com | 同上 |
| ACL 2026 | aclanthology.org（ACL Anthology MODS XML） | 同上 |
| AAAI 2026 | api.openalex.org（Proceedings of AAAI, S4210191458） | 标题 / 作者 / 摘要 / DOI（指向 ojs.aaai.org） |

主题标签（`topics`）是基于真实标题、摘要与关键词的项目内派生分类，**不是**出版方官方学科分类，界面已标注。
