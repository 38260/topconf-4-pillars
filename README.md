# 顶会四支柱文献看板 · TopConf Four Pillars

四大顶级会议（CVPR / AAAI / ICCV / ACL）**近三年 11 届**真实论文的 HTML 看板。
数据全部来自官方或权威开放接口，逐条可回溯核验；摘要提供**人工中文翻译**并保留英文原文对照。

- 顶会：`CVPR`、`AAAI`、`ICCV`、`ACL`（四支柱＝四个会议，年份作为筛选维度）
- 时间窗：近三年 **11 届** —— CVPR 2024/2025/2026 · AAAI 2024/2025/2026 ·
  ICCV 2023/2025（奇数年会议）· ACL 2024/2025/2026
- 规模：每届精选 12 篇，共 **132 篇**；官方语料底数 **35,927 篇**
- 视图：**四支柱**（一会一柱）+ **主题视图**（深度学习 / 大模型 / 边缘计算与高效推理 / 多模态 …）
- 导航：sticky 目录侧栏（论文两级直达 + 滚动高亮，顶栏「目录」可折叠）；届次筛选条；搜索框快捷键 `/`
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
python scripts/build_papers.py     # 按 data/selection.json 补官方摘要 → data/draft.json
python scripts/build_citations.py  # 解析官方 BibTeX + 落盘 web/data/export/*
python scripts/verify.py           # 绕缓存回源逐字核验 → docs/verification-report.md
python scripts/verify.py           # 抽样回源核验，输出 docs/verification-report.md
```

原始响应缓存在 `data/raw/`（已 gitignore，避免把几十 MB 官方页面提交进仓库）。

## 目录

```
scripts/fetchlib/   官方源适配器：cvf.py / acl_anthology.py / openalex.py + http.py（缓存重试限速）
scripts/            fetch_corpus / build_papers / build_citations / build_data / verify / serve
data/               corpus.json（全量目录）· selection.json（精选清单）· papers.json（展示数据）
web/                index.html + css/ + js/ + data/papers.js（内联快照，file:// 可用）
docs/               design-references.md · verification-report.md
TODO.md             全局待办真源，每次完成同步并随代码提交
```

## 数据源

| 支柱 | 官方源 | 届次 | 抓取内容 |
|------|--------|------|----------|
| CVPR | openaccess.thecvf.com（CVF 开放获取） | 2024 / 2025 / 2026 | 标题 / 作者 / 官方摘要 / PDF / 页码 / 内嵌 BibTeX |
| ICCV | openaccess.thecvf.com | 2023 / 2025 | 同上 |
| ACL | aclanthology.org（ACL Anthology MODS XML） | 2024 / 2025 / 2026 | 标题 / 作者 / 官方摘要 / PDF / DOI / 页码 |
| AAAI | api.openalex.org（Proceedings of AAAI, S4210191458） | 2024 / 2025 / 2026 | 标题 / 作者 / 摘要 / DOI（指向 ojs.aaai.org） |

主题标签（`topics`）是基于真实标题、摘要与关键词的项目内派生分类，**不是**出版方官方学科分类，界面已标注。

## 引用导出（BibTeX / RIS / Markdown）

48 篇**全部为出版方官方 BibTeX 原文**，无一条是拼出来的：

| 支柱 | 引用来源 | 取得方式 |
|------|----------|----------|
| CVPR / ICCV | CVF Open Access | 会议目录页内嵌 `@InProceedings`（与 4,042 / 2,701 篇同时解析，零额外请求） |
| ACL | ACL Anthology | 官方 `<id>.bib` 导出 |
| AAAI | Crossref | 经 AAAI DOI 内容协商 `Accept: application/x-bibtex`（含 volume / ISSN / pages） |

- 界面：论文详情底部「引用（BibTeX）」可直接复制；顶部导出条按**当前筛选**导出。
- 离线：`web/data/export/{all,cvpr,aaai,iccv,acl}.{bib,ris,md}` 已随仓库生成，`file://` 也能下载。
- 服务端：`GET /api/export?fmt=bib|ris|md&ids=...`（或 `&venue=AAAI`）。
- RIS 与 Markdown 不是出版方原文，由本项目**已核验字段**渲染；导出文件头部会标注官方原文与渲染条目各多少条。

```bash
python scripts/build_citations.py        # 解析 + 落盘（无引用即失败退出）
python scripts/build_citations.py --force  # 重新回源解析 ACL / Crossref
```

## 如何自行核验真实性

每条记录都带 `provenance.paper_id`（官方系统内的记录号）与 `links`，可三路交叉复核：

1. **点链接复核**：卡片详情 → 「论文页」直达 CVF Open Access / ACL Anthology / AAAI DOI 落地页，
   「PDF」直达官方全文；AAAI 另给「OpenAlex 记录」链接。
2. **跑核验脚本**：`python scripts/verify.py` 会**绕过本地缓存**重新读取 132 篇官方页面，
   把摘要规范化后与仓库内 `data/papers.json` 逐字比对，并检查论文页/PDF 可达性，
   结果写入 `docs/verification-report.md`（含逐篇表格）。
3. **重放全量语料**：`python scripts/fetch_corpus.py --no-cache` 重新拉取 11 届官方目录，
   与 `data/corpus_meta.json` 的逐届体检数字对比（CVPR 4,042/2,871/2,716 · ICCV 2,701/2,156 ·
   ACL 4,809/3,351/1,952 · AAAI 4,976/3,486/2,867）。

数据口径的三条坦白：

- 精选清单是人挑的（`data/selection.json` 每篇都写了策展理由），不是自动排行榜；
  候选范围由 `scripts/rank_candidates.py` 对 16,528 篇官方语料按主题打分产生。
- 中文摘要＝人工逐句翻译，英文原文一字未改且保留在详情页可展开对照；
  `scripts/check_translations.py` 会拦下英文残留、主题误标与截断。
- 引用次数（`citations`）来自 OpenAlex，只在该库能按标题/DOI 精确匹配时才写，
  匹配不上就留空并在界面隐藏，不估算、不填充。

