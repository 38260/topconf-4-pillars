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
| R10 | 追加需求：48 张卡逐条滚动太慢，要目录 | `web/js/app.js` renderToc + `.toc` 侧栏 |

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
- [x] 3.3 逐篇人工翻译摘要为中文（48/48：CVPR 12 · AAAI 12 · ICCV 12 · ACL 12）
- [x] 3.4 逐篇抽取中英文关键词（每篇 4–5 组中英对照）
- [x] 3.4b `check_translations.py` QA 闸门：中文域英文残留、未知主题、缺关键词、
      译文过短，并新增「英文原文体检」（截断 / 异常偏短）。48 篇 0 问题
- [x] 3.4c 修复 ACL 摘要解析截断：Anthology 在摘要内嵌套 `<span class=tex-math>`，
      惰性匹配 `</span>` 会从 `2.7×` 处截断；改为切片到元数据区（影响 2 篇）
- [x] 3.5 产出 `data/papers.json`（48 篇，均含 provenance / 官方链接 / 被引数）
- [x] 3.6 `build_data.py`：注入 `web/data/papers.js`（202.5 KB），`file://` 双击可开

## 阶段 4 · 界面（R2 / R3 / R8）—— 浏览器实测结果见 5.2

- [x] 4.1 设计 token：Claude 风格米色底 + 陶土色强调，明/暗双主题仅覆盖 token
      （实测：深色 `--bg #1a1915 / 文字 #f0eee6`，浅色 `#faf9f5 / #1f1e1b`，切换生效）
- [x] 4.2 Trace Light 模式移植：状态→色彩映射、4 档圆角、4pt 网格、双层阴影、sticky 顶栏 + 锚点滚动
      （实测：topbar `position:sticky`，卡片色条 `rgb(217,119,87)`，圆角 12/18px，统计卡内边距 16px）
- [x] 4.3 四支柱主视图：4 柱 × 12 卡 = 48 张卡，柱头含会名/年份/官方源链接/篇数
- [x] 4.4 论文卡片 + 详情模态框（中英摘要对照、5 组关键词、主题、9 位作者、官方链接、数据溯源）
- [x] 4.5 主题视图：11 个主题分组，组头显示跨支柱构成（如 边缘计算 CVPR 3 / AAAI 4 / ICCV 4 / ACL 4）
- [x] 4.6 搜索与筛选：搜「边缘」→ 6 张卡 4 个主题组 + 命中高亮；主题 chip 下钻 → 单组 15 篇
- [x] 4.7 可达性：48 张卡 `role=button tabindex=0`，Enter 打开、Esc 关闭并解除滚动锁；
      `prefers-reduced-motion / reduced-transparency / contrast` 三条降级保留

## 阶段 5 · 验证与交付

- [x] 5.1 `scripts/serve.py` 本地服务（静态 + `/api/papers` + `/api/health` + `/api/refresh` 回源刷新）
- [x] 5.2 浏览器实测：结构层用脚本驱动真实事件全部通过（见阶段 4 实测注）；
      `file://` 直开模式实测 48 卡渲染 + 刷新按钮禁用带说明。
      **像素级视觉核验未做** —— 本会话内置浏览器无可见表面对象（`visibilityState=hidden`、
      `viewport=0x0`），截图与窄屏媒体查询无法判定，需用户在真实浏览器打开确认。
- [x] 5.2b 原生连接端到端实测：`POST /api/refresh` 绕缓存重读 48 篇官方页并重建，
      返回 200 / 48 篇 / 中译 48 篇完整，`generated_at` 刷新 —— 幂等且不丢译文
- [x] 5.3 抽样回源核验 → 升级为**全量 48 篇**核验：`scripts/verify.py` 绕过缓存重读官方页，
      规范化后逐字比对摘要 + 检查论文页/PDF 可达，报告落 `docs/verification-report.md`。
      结果：**摘要逐字一致 48/48 · 论文页可达 48/48 · PDF 40/48（AAAI 8 篇无独立 PDF 链接，标注不适用）· 异常 0**
- [x] 5.4 README 补「如何自行核验真实性」三路复核指引 + 数据口径坦白
- [x] 5.5 最终提交与 TODO 收口

## 阶段 6 · 目录导航（R10，2026-09-18 追加需求）

- [x] 6.1 sticky 目录侧栏（Trace Light `.toc-nav` 模式）：`layout` 双栏 + `.toc` 独立滚动
- [x] 6.2 四支柱视图：4 个分节标题 + 48 条论文直达（编号 + 中文短标题）
- [x] 6.3 主题视图：默认只列 11 个分组标题，选中某主题后才展开该组论文
      （一篇可属多主题，全展开会重复计数 —— 实测 135 条 → 收敛为 11 条）
- [x] 6.4 目录跟随筛选：搜索 / 支柱下钻 / 主题下钻时目录条目与篇数同步（搜「水印」→ 目录 2 篇）
- [x] 6.5 跳转高亮：`scrollIntoView` + 目标卡 `flash` 1.1s；滚动时 rAF 节流 spy 标当前项
- [x] 6.6 顶栏「目录」按钮折叠/展开，状态存 localStorage；窄屏改为内容上方折叠面板
- [x] 6.7 浏览器实测：4+48 条、11 分组、23 篇展开、锚点 100% 可解析、折叠与持久化生效

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

## 需求逐项验收（R1–R9）

| # | 需求 | 验收证据 |
|---|------|----------|
| R1 | 四会议（CVPR/AAAI/ICCV/ACL） | `scripts/pillars.py` 四条；界面 4 柱各 12 篇 |
| R2 | Claude 风格 HTML | `web/css/tokens.css` 象牙底 `#faf9f5` + 陶土 `#d97757` + 衬线标题（computed-style 实测） |
| R3 | 四支柱 + 原生连接 | 官方源直连管线 + `POST /api/refresh` 实测 200/48 篇；前端零 CDN，`file://` 可用 |
| R4 | 数据完全真实 | 48/48 摘要与官方页逐字一致（`docs/verification-report.md`），每条带 paper_id 与官方链接 |
| R5 | 摘要中译 | 48 篇人工翻译，平均 428 字，英文原文可展开对照 |
| R6 | 关键词 | 每篇 4–5 组中英对照关键词 |
| R7 | 主题展示 | 11 个主题 + 「深度学习」总览透镜；边缘计算 15 篇、大模型 23 篇等，四会均有分布 |
| R8 | 参考 Trace Light | `docs/design-references.md` 九条逐一对应，token/状态映射/错峰动画/下钻统计卡均落地 |
| R9 | 每完成一次提交 git + 维护全局 TODO | 9 次提交，每次同步 `TODO.md`（本文件） |

## 阶段 7 · 近三年扩充（R11，2026-09-19 进行中）

- [x] 7.0 用户确认：每届 12 篇 → 共 132 篇；年份维度用「筛选 + 卡片年份徽章」承载
- [x] 7.0a 抓取管线改多届：`pillars.EDITIONS` 11 届；cvf.index(venue, year)、
      acl.index(year, volumes)、discover_volumes(year) 全部按届参数化；
      顺手修掉 cvf.index 里 `code` 被 code/data 链接正则覆盖的变量遮蔽缺陷（会让 paper_id 变成 match 对象）
- [x] 7.0b 全量拉取 11 届官方目录：**35,927 篇**（原 16,528）。逐届体检见下表
- [x] 7.0c rank_candidates.py 支持按届 + `--skip-curated`，产出新 8 节候选清单
- [x] 7.0d 人工精选 84 篇（7 届 × 12），`data/selection.json` 累计 132 篇，ref 全部可解析
- [~] 7.0e 回源补 84 篇官方摘要 + OpenAlex 被引数
- [ ] 7.0f 逐届人工翻译 84 篇（7 批，每批一提交）
- [ ] 7.0g 界面年份维度：届次筛选条 + 卡片年份徽章 + 统计卡「N 届」+ 目录届次跨度
- [ ] 7.0h 重建 papers.json / papers.js / 引用导出，并对 132 篇跑全量核验

### 逐届体检（2026-09-19 实抓）

| 届 | 官方篇数 | 目录级摘要 | DOI | PDF | 官方 BibTeX |
|---|---|---|---|---|---|
| CVPR 2026 | 4,042 | — | — | 4,042 | 4,042 |
| CVPR 2025 | 2,871 | — | — | 2,871 | 2,871 |
| CVPR 2024 | 2,716 | — | — | 2,715 | 2,716 |
| AAAI 2026 | 4,976 | 100% | 4,976 | 4,976 | 按需（Crossref） |
| AAAI 2025 | 3,486 | 100% | 3,486 | 3,486 | 同上 |
| AAAI 2024 | 2,867 | 100% | 2,867 | 2,867 | 同上 |
| ICCV 2025 | 2,701 | — | — | 2,701 | 2,701 |
| ICCV 2023 | 2,156 | — | — | 2,156 | 2,156 |
| ACL 2026 | 4,809 | — | 4,809 | 4,809 | 按需（官方 .bib） |
| ACL 2025 | 3,351 | — | 3,351 | 3,351 | 同上 |
| ACL 2024 | 1,952 | — | 1,952 | 1,952 | 同上 |

## 阶段 8 · 其余候选（原阶段 7 规划，未完成）

已做过可行性实测，不是空想：

- [ ] 8.1 **全量语料检索**：解锁已抓到的 16,528 篇官方目录（目前界面只暴露 48 篇精选）。
      后端 `GET /api/search?q=&venue=&topic=&page=` 直接查 `data/corpus.json`；
      前端加「全量语料」第三视图。
      代价与口径：CVPR/ICCV/ACL 目录级记录**不含摘要**（官方摘要在单篇页，48 篇才回源取过），
      所以长尾结果只能给标题/作者/页码/官方链接，界面必须标「未取摘要 · 未翻译」，不得留白冒充缺失。
- [x] 7.2 **引用导出（BibTeX / RIS / Markdown）**：已完成，且 48/48 全是出版方官方原文，
      无一条需要本项目渲染兜底——CVF 目录内嵌 `@InProceedings`（4042/2701 条同批解析，
      零新增请求）、ACL 官方 `<id>.bib`、AAAI 经 DOI 内容协商取 Crossref `@article`。
      交付：`scripts/fetchlib/citation.py` + `scripts/build_citations.py`（缺引用即非零退出的硬门禁）、
      `data/citations.json`、`web/data/export/*.{bib,ris,md}`（15 个文件 / 192 KB）、
      `/api/export?fmt=&ids=|venue=`、详情页「复制」按钮、导出条按当前筛选联动。
      浏览器实测：48 篇与筛选后 15 篇的导出链接均正确，ACL 条目 892 字符官方原文；
      剪贴板在无手势的自动化上下文下降级为「已选中，请 Ctrl+C」并提示，不静默失败。
- [ ] 8.2 **主题 × 支柱矩阵**：一张 11×4 的真实计数表（大模型 23 = CVPR 4/AAAI 4/ICCV 3/ACL 12 等），
      回答「哪个主题在哪个会议更集中」；单元格可点击直接跳到对应筛选。
      口径提醒：分母只有 48 篇精选，是**样本构成**不是会议趋势，界面需这样写。
- [ ] 8.3 **回归门禁与定时回源**：`scripts/run_all.py`（fetch→rank→draft→check→build→verify 一键串跑，
      任一门禁非零即失败）；再挂每周 cron 回源并只在 `verify` 报告异常时通知。

已排除（实测不可行，不做假数据顶上）：

- 机构 / 作者地域分布：OpenAlex 对 AAAI 记录的 `authorships[].institutions` 返回空数组
  （实测 DOI 10.1609/aaai.v40i31.39789），CVF 目录也只给作者姓名，无单位。

待用户侧完成：

- 像素级视觉核验：本会话内置浏览器无可见表面对象，需在真实浏览器确认目录栏密度与窄屏布局。

## 风险

- 主题分类是基于真实标题/摘要/关键词的规则+人工判定，不是出版方官方学科分类，界面需明确标注为「本项目派生」。
- 官方摘要缺失的论文一律不入选，不得用机翻或杜撰补齐。
