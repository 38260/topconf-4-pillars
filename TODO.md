# 全局 TODO · 顶会四支柱文献看板

> 本文件是唯一的全局待办真源。每完成一项就更新状态并提交一次 git。
> 状态标记：`[ ]` 待办 · `[~]` 进行中 · `[x]` 已完成 · `[-]` 已取消/不做

## 需求台账（不可丢失的约束）

| # | 约束 | 落地位置 |
|---|------|----------|
| R1 | 四个顶会：CVPR / AAAI / ICCV / ACL（用户原文 "CUPR" 已确认为 CVPR 笔误） | 四支柱 UI |
| R2 | HTML 展示，Claude 风格 | `web/css/tokens.css` |
| R3 | 四支柱 + 原生连接（真实源直连，无 CDN、无手写假数据） | `scripts/fetchers/` + `scripts/serve.py` |
| R4 | 数据完全真实，可回溯核验 | 每条记录带 `source`/`provenance` 字段 |
| R5 | 摘要翻译为中文 | `papers[].abstract_zh`（人工翻译，非机翻占位） |
| R6 | 关键词 | `papers[].keywords` + `keywords_zh` |
| R7 | 主题视图（深度学习、边缘计算、大模型等） | `web/` 主题分组视图 |
| R8 | 参考 Trace Light 组件设计模式 | `docs/design-references.md` |
| R9 | 每完成一次提交一次 git 并同步本 TODO | 提交历史 |

## 阶段 1 · 骨架

- [x] 1.1 新建 `D:\AIWork\topconf-4-pillars`，`git init`
- [x] 1.2 目录结构：`scripts/` `data/raw/` `web/{css,js,data}` `docs/`
- [x] 1.3 本 TODO 文档 + README + .gitignore
- [x] 1.4 首次提交

## 阶段 2 · 真实数据抓取（R3 / R4）

- [x] 2.1 连通性验证：CVF Open Access、ACL Anthology、OpenAlex 三源 HTTP 200
- [x] 2.2 `fetchlib/http.py`：缓存、重试、UA 规范、限速、原始响应落盘 `data/raw/`
- [x] 2.3 `fetchlib/cvf.py`：CVPR 2026 + ICCV 2025 全量目录（`?day=all`）+ 单篇官方摘要页
- [x] 2.4 `fetchlib/acl_anthology.py`：ACL 2026 卷级 MODS 目录 + 单篇论文页官方摘要
      （实测：卷级/单篇 MODS XML 均无 `<abstract>`，摘要只在渲染页 `card-body acl-abstract` 内）
- [x] 2.5 `fetchlib/openalex.py`：AAAI 2026（Proceedings of AAAI, S4210191458）摘要/作者/DOI
- [x] 2.6 归一化为 `data/corpus.json`，统一 schema + 抓取时间戳
- [x] 2.7 语料体检：四会议条目数、摘要缺失率、重复 DOI 检查
- [x] 2.8 `rank_candidates.py`：按主题给 16,528 篇打分 → `data/candidates.md` 供人工精选

## 阶段 3 · 精选与中文翻译（R5 / R6 / R7）

- [x] 3.1 定义主题体系（11 类 + 「深度学习」总览透镜，见 `scripts/topics.py`）
- [x] 3.2 每会精选 12 篇（`data/selection.json`，含策展理由，ref 全部指向官方真实记录号）
- [~] 3.3 逐篇人工翻译摘要为中文（48 篇）：CVPR 12/12 ✔ · AAAI 0/12 · ICCV 0/12 · ACL 0/12
- [~] 3.4 逐篇抽取中英文关键词（随译文一并产出）
- [ ] 3.5 产出 `data/papers.json`（含 provenance）
- [ ] 3.6 `build_data.py`：把 JSON 注入 `web/data/papers.js`，使 `file://` 双击可开

## 阶段 4 · 界面（R2 / R3 / R8）

- [ ] 4.1 设计 token：Claude 风格米色底 + 陶土色强调，明/暗双主题仅覆盖 token
- [ ] 4.2 Trace Light 模式移植：状态→色彩映射、4 档圆角、4pt 网格、双层阴影、sticky 顶栏 + 锚点滚动
- [ ] 4.3 四支柱主视图（每支柱一会，原生连接真实数据）
- [ ] 4.4 论文卡片 + 详情模态框（英文原摘要 / 中文译文对照、关键词、主题、官方链接）
- [ ] 4.5 主题视图：按主题聚合四支柱论文
- [ ] 4.6 搜索与筛选（会议 / 主题 / 年份 / 关键词）
- [ ] 4.7 响应式与可达性（键盘焦点、`prefers-reduced-motion`、空状态）

## 阶段 5 · 验证与交付

- [ ] 5.1 `scripts/serve.py` 本地服务（静态 + `/api/papers` 原生接口 + `/api/refresh` 回源刷新）
- [ ] 5.2 浏览器实测：四支柱、主题视图、搜索、明暗切换、移动端
- [ ] 5.3 抽样回源核验（每会 ≥3 篇，比对官方标题/作者/摘要）
- [ ] 5.4 README 补「数据来源与核验步骤」章节，用户可按链接自行复核
- [ ] 5.5 最终提交与 TODO 收口

## 已知事实 / 决策记录

- 2026-09-18 用户确认：CUPR = CVPR；每会 12 篇精选共 48 篇；取各自最新一届。
- 2026-09-18 版本落点：CVPR 2026、AAAI 2026、ACL 2026、ICCV 2025（ICCV 为奇数年会议，2025 即最新一届；下一届 2027）。
- 2026-09-18 技术选型：抓取仅用 Python 标准库（urllib / html.parser / xml.etree），零第三方依赖。
- 2026-09-18 Semantic Scholar 无 key 时返回 429、DBLP 触发反爬验证，故不作为主数据源；AAAI 走 OpenAlex（实测摘要覆盖 25/25）。
- 2026-09-18 「原生连接」解释为两层：(a) 数据侧直连官方源并可刷新；(b) 界面侧无 CDN、无外部请求，`file://` 亦可离线打开。

## 语料体检（2026-09-18 实抓）

| 支柱 | 官方语料量 | 目录级摘要 | DOI | PDF | 备注 |
|------|-----------|-----------|-----|-----|------|
| CVPR 2026 | 4,042 | 0%（摘要在单篇页） | CVF 目录不给 DOI | 4,042 | 标题/作者/bibtex 页码齐全 |
| ICCV 2025 | 2,701 | 0%（同上） | 同上 | 2,701 | |
| ACL 2026 | 4,809 | 0%（摘要在论文页） | 4,809 | 4,809 | 卷分布 long 2221 / findings 2163 / industry 155 / srw 110 / demo 86 / short 74 |
| AAAI 2026 | 4,976 | 100% | 4,976 | 4,976 | OpenAlex 有 63 条同名重复，精选时按 DOI 去重 |

合计 16,528 篇真实论文进入 `data/corpus.json`（21.7 MB，已 gitignore，可由脚本重放）。

## 风险

- 主题分类是基于真实标题/摘要/关键词的规则+人工判定，不是出版方官方学科分类，界面需明确标注为「本项目派生」。
- 官方摘要缺失的论文一律不入选，不得用机翻或杜撰补齐。
