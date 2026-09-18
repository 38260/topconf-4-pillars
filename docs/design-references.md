# 设计模式参考 · Trace Light → 本项目

参考仓库：<https://github.com/38260/local-project-archive-desktop>（桌面应用 "Trace Light"，
FastAPI + Vue3 静态页 + 原生 CSS）。本文记录**逐条对应**的移植关系，便于审阅者核对
「参考组件设计模式」这一需求确实落地，而不是仅借用风格。

依据文件：`app/static/css/style.css`（1489 行）、`app/static/js/common.js`（565 行）、
`app/static/js/dashboard.js`。

## 1. CSS 变量作为「单一真源」

Trace Light 在 `:root` 里定义 `--bg / --panel / --text / --muted / --border / --accent`，
并显式注释「四个状态在徽章 / 卡片色条 / 分组圆点 / 下拉触发器中共用同一组变量，
改配色只需动这里」。语义色成对定义 `--c-*-bg` / `--c-*-fg`，注释说明「暗色只需覆盖这一组」。

移植：`web/css/tokens.css` 只放 token；`web/css/components.css` 一律用 `var(--x)`，
不出现硬编码色值。明/暗主题通过 `[data-theme="..."]` 覆盖同名 token 完成。

## 2. 状态 → 色彩映射（`--st` 消费模式）

```css
/* Trace Light */
[data-status="进行中"], .s-进行中 { --st: var(--st-doing); }
.card::before { background: var(--st, var(--border)); }
.badge.s-已完成 { color:#fff; background: var(--st); }
```

选择器不写死颜色，只声明 `--st`；卡片左侧 3px 色条、徽章、分组圆点都消费 `--st`。

移植：本项目把「状态」换成「支柱」与「主题」两个维度——
`[data-pillar="CVPR"] { --st: var(--pillar-cvpr) }`，卡片色条/徽标/柱头圆点共用；
新增论文卡片时不需要写任何配色代码。

## 3. 4 档圆角 + 4pt 间距网格

`--r-sm/md/lg/xl`（4/8/12/16px）与 `--s-1..--s-8`（4pt 网格）集中定义，
组件只引用档位，杜绝 7px/13px 这类漂移值。移植时原样保留该两族 token 命名。

## 4. 双层阴影 + 玻璃上沿亮边（"Trace Light" 的光线感）

```css
--shadow-sm: 0 1px 2px …, 0 1px 3px …;   /* 环境 + 投影 */
.topbar { background: var(--panel-glass); backdrop-filter: blur(18px) saturate(160%);
          box-shadow: inset 0 1px 0 var(--edge); }
```

移植：顶栏沿用 sticky + 玻璃拟态 + `inset` 亮边；`--topbar-h` 作为锚点滚动与
sticky 侧栏的共用高度（Trace Light 用 `scroll-margin-top: calc(var(--topbar-h) + 12px)`）。

## 5. 卡片进场错峰动画

`.card:nth-child(1..6) { animation-delay: 0/30/60/90/120/150ms }`，
配 `animation: fade-up .28s ease backwards`；`@media (prefers-reduced-motion: reduce)` 关闭。

移植：同结构（错峰 30ms、`backwards`、reduced-motion 降级），并额外遵循
`prefers-reduced-transparency` 关掉 backdrop-filter（Trace Light 也做了这条）。

## 6. 统计卡下钻（quick filter）

`dashboard.js` 里 `stats` 与 `quickFilter: null | "active" | "lost"` 配对，
统计卡 `.stat.on` 加 `box-shadow: 0 0 0 3px var(--accent-soft)`，点击即筛选。

移植：顶部四张「支柱卡 / 主题卡」既是概览也是筛选器，`aria-pressed` 表达选中态，
`.stat.on` 用同一套 ring 样式。

## 7. common.js 的全局工具命名空间

`window.applyTheme / cycleTheme / toast / confirmDialog / api / fmtNum / fmtTime /
statusBadgeClass / tagClass`——主题偏好存 localStorage，取值 `auto|light|dark`，
`auto` 跟随 `prefers-color-scheme`。

移植：`web/js/common.js` 提供同名职责（`cycleTheme`、`toast`、`fmtNum`、
`pillarBadgeClass`、`tagClass`），三态主题 + localStorage 行为一致；
差异是本页面 `file://` 打开时不发网络请求，`api()` 仅在本地服务模式下走 `/api/*`。

## 8. 页面脚本 = IIFE + 单一 state + 计算属性

`dashboard.js`：`(function(){ "use strict"; createApp({ data(){ … q, statusFilter,
tagFilter, sortBy … } })`，筛选/排序状态集中在一个对象里。

移植：`web/js/app.js` 用 IIFE + 显式 `state` 对象 + 纯函数 `select()/render()`，
不引入 Vue（保持零依赖、离线可开），但状态组织方式与「过滤器互不残留」的行为对齐。

## 9. 中文即一等公民

Trace Light 的状态枚举、排序标签、TOC 全用中文，同时用 `--sans` 栈里的
`"Microsoft YaHei", "PingFang SC"` 兜住中文字形。

移植：界面文案中文优先，正文栈显式包含 `ui-serif/Georgia → "Songti SC" / "Noto Serif SC"`
（Claude 风格衬线）与中文回退；中英摘要对照用同一字号不同字重，避免中英混排跳字。

## 与 Claude 风格的结合

Trace Light 提供**结构**（token 单一真源、状态映射、错峰动画、下钻统计卡），
Claude 提供**表面**：米白/羊皮纸底色（`#faf9f5` 系）、陶土橙强调（`#d97757` 系）、
衬线标题 + 无衬线正文、低饱和分隔线。两者不冲突：颜色全部进 token，结构全部进组件层。
