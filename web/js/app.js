/* app.js —— 页面主逻辑（IIFE + 单一 state + 纯渲染函数，结构对齐 Trace Light dashboard.js） */
(function () {
  "use strict";

  /* ---------------- 收藏存储 ----------------
     顺序很重要：FAV_KEY 必须先赋值，再调用 readLocalFavs()。
     var 只提升声明、不提升赋值，早先“先调用、后赋值”的写法会让键名变成 undefined，
     于是每次刷新都读回空数组 —— 收藏根本撑不过一次页面刷新。
     另外 localStorage 按「协议 + 端口」隔离：换端口（start.bat 8790）、换浏览器、清缓存
     都会让收藏凭空消失。所以服务模式下真源是服务端 data/favs.json，localStorage 退化为
     镜像 + file:// 模式下的唯一存储；updated_at 用来判新旧，避免两端互相覆盖。 */
  var FAV_KEY = "topconf.favs";
  var FAV_AT_KEY = "topconf.favs.at";
  function readLocalFavs() {
    var ids = [], at = 0;
    try {
      var raw = JSON.parse(localStorage.getItem(FAV_KEY));
      if (Array.isArray(raw)) ids = raw.filter(function (x) { return typeof x === "string" && x; });
    } catch (e) {}
    try { at = parseInt(localStorage.getItem(FAV_AT_KEY), 10) || 0; } catch (e) { at = 0; }
    return { ids: ids, updated_at: at };
  }
  function writeLocalFavs(ids, at) {
    try {
      localStorage.setItem(FAV_KEY, JSON.stringify(ids));
      localStorage.setItem(FAV_AT_KEY, String(at || 0));
    } catch (e) { /* 隐私模式 / 禁用存储时忽略，不影响服务端那份 */ }
  }

  var localFavs = readLocalFavs();

  var state = {
    data: null,
    view: "pillars",        // pillars | topics | repro
    q: "",
    venue: null,            // 单支柱下钻
    topic: null,            // 主题下钻
    paperId: null,          // 模态框
    year: null,             // 届次下钻（近三年扩充）
    diff: null,             // 复现难度下钻（repro 视图）
    favs: localFavs.ids,    // 收藏 id：以本地服务 data/favs.json 为准，localStorage 只是镜像
    favsAt: localFavs.updated_at,
    source: null,           // inline | api
    tocOpen: localStorage.getItem("topconf.toc") !== "0"
  };

  function adoptFavs(ids, at) {
    state.favs = (ids || []).slice();
    state.favsAt = at || 0;
    writeLocalFavs(state.favs, state.favsAt);
    syncFavBtns(null);
    syncViewTabs();
    if (state.view === "fav" && state.data) { renderView(); renderToc(); }
  }
  /* 启动时与本地服务对齐：服务端新→采纳，本机新→推送，没有文件→迁移本机收藏 */
  function syncFavsFromServer() {
    if (!TL.SERVED) return;
    TL.api("/api/favs").then(function (s) {
      var sIds = Array.isArray(s.ids) ? s.ids : [];
      var sAt = s.updated_at || 0;
      if (!s.exists) {
        if (!state.favs.length) return;
        if (!state.favsAt) state.favsAt = Date.now();
        writeLocalFavs(state.favs, state.favsAt);
        pushFavs();
        TL.toast("已把本机浏览器的 " + state.favs.length + " 篇收藏写入 data/favs.json", "ok");
        return;
      }
      if (state.favsAt > sAt) { pushFavs(); return; }
      if (sAt > state.favsAt) { adoptFavs(sIds, sAt); return; }
      var merged = sIds.slice();
      state.favs.forEach(function (id) { if (merged.indexOf(id) < 0) merged.push(id); });
      if (merged.length !== sIds.length) {          // 时间戳相同：并集兜底，绝不丢
        state.favs = merged; state.favsAt = Date.now();
        writeLocalFavs(state.favs, state.favsAt);
        pushFavs();
      } else if (merged.length !== state.favs.length) {
        adoptFavs(sIds, sAt);
      }
    }).catch(function (e) {
      TL.toast("读不到本地服务的收藏，暂用本机浏览器那份：" + e.message, "warn");
    });
  }
  var favTimer = null;
  function pushFavs() {
    if (!TL.SERVED) return;                          // file:// 下没有服务端可写
    clearTimeout(favTimer);                          // 连点 ★ 只落一次盘
    favTimer = setTimeout(function () {
      var ids = state.favs.slice(), at = state.favsAt;
      fetch("/api/favs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: ids, updated_at: at })
      }).then(function (r) {
        return r.json().catch(function () { return null; })
          .then(function (d) { return { status: r.status, body: d }; });
      }).then(function (res) {
        if (res.status === 409 && res.body && Array.isArray(res.body.ids)) {
          adoptFavs(res.body.ids, res.body.updated_at);
          TL.toast("本地服务那份更新，已按它对齐（" + res.body.ids.length + " 篇）", "warn");
          return;
        }
        if (res.status !== 200) throw new Error("HTTP " + res.status);
        state.favsAt = (res.body && res.body.updated_at) || at;
        writeLocalFavs(state.favs, state.favsAt);
      }).catch(function (e) {
        TL.toast("收藏已存在本机浏览器，但写入 data/favs.json 失败：" + e.message, "warn");
      });
    }, 350);
  }

  var el = {};
  function $(id) { return document.getElementById(id); }

  /* ---------------- 数据装载：内联快照优先，服务模式可回源刷新 ---------------- */
  function loadData() {
    if (window.PAPERS_DATA && window.PAPERS_DATA.papers) {
      adopt(window.PAPERS_DATA, "inline");
      return;
    }
    if (TL.SERVED) {
      TL.api("/api/papers").then(function (d) { adopt(d, "api"); })
        .catch(function (e) { adopt(null, null); TL.toast("读取 /api/papers 失败：" + e.message, "err"); });
      return;
    }
    adopt(null, null);
  }

  function adopt(d, src) {
    if (!d) {
      $("view-root").innerHTML =
        '<div class="empty" style="margin-top:48px"><h3>没有数据</h3>' +
        '<div>请先运行 <code>python scripts/build_data.py</code> 生成 <code>web/data/papers.js</code>。</div></div>';
      return;
    }
    state.data = d; state.source = src;
    renderAll();
  }

  /* ---------------- 选择 ---------------- */
  function topicMeta(id) {
    for (var i = 0; i < state.data.topics.length; i++)
      if (state.data.topics[i].id === id) return state.data.topics[i];
    return { label: id, accent: "slate" };
  }
  function pillarMeta(key) {
    for (var i = 0; i < state.data.pillars.length; i++)
      if (state.data.pillars[i].key === key) return state.data.pillars[i];
    return { key: key, label: key, accent: "clay" };
  }

  function haystack(p) {
    return [p.title, p.title_zh, p.abstract, p.abstract_zh,
            (p.authors || []).join(" "), p.curator_note,
            (p.keywords || []).map(function (k) { return k.en + " " + k.zh; }).join(" ")
            ].join(" ").toLowerCase();
  }

  function filtered() {
    var q = state.q.trim().toLowerCase();
    return state.data.papers.filter(function (p) {
      if (state.venue && p.venue !== state.venue) return false;
      if (state.topic && p.topics.indexOf(state.topic) < 0) return false;
      if (state.year && String(p.year) !== String(state.year)) return false;
      if (state.view === "fav" && !isFav(p.id)) return false;
      if (q && haystack(p).indexOf(q) < 0) return false;
      return true;
    });
  }

  /* ---------------- 收藏 ---------------- */
  var STAR_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5-5.8-3.1-5.8 3.1 1.1-6.5L2.6 9.4l6.5-.9z" ' +
    'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
  function isFav(id) { return state.favs.indexOf(id) >= 0; }
  function toggleFav(id) {
    var i = state.favs.indexOf(id), on = i < 0;
    if (on) state.favs.push(id); else state.favs.splice(i, 1);
    state.favsAt = Date.now();
    writeLocalFavs(state.favs, state.favsAt);   // 先写镜像（file:// 模式下的唯一存储），再推服务端
    pushFavs();
    return on;
  }
  function syncFavBtns(id) {                    // id 传 null 表示全量刷新
    document.querySelectorAll('[data-act="fav"]').forEach(function (b) {
      if (id && b.dataset.val !== id) return;
      var on = isFav(b.dataset.val);
      b.classList.toggle("on", on);
      b.setAttribute("aria-pressed", String(on));
      b.setAttribute("aria-label", on ? "取消收藏" : "收藏");
      b.setAttribute("title", on ? "取消收藏" : "收藏");
      b.querySelector("path").setAttribute("fill", on ? "currentColor" : "none");
    });
  }
  function favBtn(p, cls) {
    var on = isFav(p.id);
    return '<button type="button" class="fav' + (cls ? " " + cls : "") + (on ? " on" : "") +
      '" data-act="fav" data-val="' + p.id + '" aria-pressed="' + on + '" ' +
      'aria-label="' + (on ? "取消收藏 " : "收藏 ") + TL.esc(p.title_zh || p.title) + '" ' +
      'title="' + (on ? "取消收藏" : "收藏") + '">' + STAR_SVG + "</button>";
  }

  function countsBy(fn) {
    var m = {};
    state.data.papers.forEach(function (p) {
      fn(p).forEach(function (k) { m[k] = (m[k] || 0) + 1; });
    });
    return m;
  }

  /* ---------------- 渲染 ---------------- */
  function renderAll() {
    renderFacts();
    renderYearBar();
    renderStats();
    renderFilterbar();
    renderView();
    renderExportBar();
    renderToc();
    syncToc();
    syncViewTabs();          // 顶栏「收藏」角标随收藏数刷新（启动时也要刷新）
  }

  /* ---------------- 导出（BibTeX 为出版方官方原文，RIS/MD 由已核验字段渲染） ---------------- */
  function renderExportBar() {
    var rows = filtered();
    var bar = $("exportbar");
    if (!rows.length) { bar.innerHTML = ""; return; }
    var one = state.venue ? state.venue.toLowerCase() : "all";
    var ids = rows.map(function (p) { return p.id; }).join(",");
    var fmts = [["bib", "BibTeX"], ["ris", "RIS"], ["md", "Markdown"]];
    var links = fmts.map(function (f) {
      var href = TL.SERVED
        ? "/api/export?fmt=" + f[0] + (rows.length === state.data.papers.length ? "" : "&ids=" + ids)
        : "data/export/" + one + "." + f[0];
      return '<a class="btn" href="' + href + '" download="' + one + '.' + f[0] + '" ' +
        'title="导出 ' + rows.length + ' 篇的 ' + f[1] + ' 引用">' + f[1] +
        '<span class="fmt">.' + f[0] + "</span></a>";
    }).join("");
    var hint = "";
    if (!TL.SERVED && rows.length !== state.data.papers.length) {
      hint = '<span class="hint">当前是离线快照：筛选状态下只能取整份导出（' + one +
        '.bib 等）。要按筛选导出，请用 <code>python scripts/serve.py</code> 打开。</span>';
    }
    bar.innerHTML = '<span class="label">导出引用（' + rows.length + " 篇）</span>" + links +
      '<span class="hint">BibTeX 取出版方官方原文；RIS / Markdown 由已核验字段渲染。</span>' + hint;
  }

  /* ---------------- 届次（2023–2026 共 11 届） ---------------- */
  function years() {
    var m = {};
    state.data.papers.forEach(function (p) { m[p.year] = (m[p.year] || 0) + 1; });
    return Object.keys(m).map(Number).sort().map(function (y) { return {year: y, n: m[y]}; });
  }

  function renderYearBar() {
    var ys = years();
    var bar = $("yearbar");
    if (ys.length < 2) { bar.innerHTML = ""; return; }
    var html = '<span class="label">届次</span>' +
      '<button type="button" class="chip" data-act="year" data-val="" aria-pressed="' +
      (!state.year) + '">全部<span class="n">' + state.data.papers.length + "</span></button>" +
      ys.map(function (y) {
        return '<button type="button" class="chip" data-act="year" data-val="' + y.year +
          '" aria-pressed="' + (String(state.year) === String(y.year)) + '">' + y.year +
          '<span class="n">' + y.n + "</span></button>";
      }).join("");
    var ed = {};
    state.data.papers.forEach(function (p) { ed[p.venue + p.year] = 1; });
    html += '<span class="span">跨 ' + Object.keys(ed).length + " 届精选 · 官方语料 " +
      TL.fmtNum((state.data.meta || {}).corpus_total || 0) + " 篇</span>";
    bar.innerHTML = html;
  }

  function renderFacts() {
    var d = state.data, m = d.meta || {};
    var prov = [];
    var newest = null;
    d.papers.forEach(function (p) {
      var t = p.provenance.retrieved_at;
      if (t && (!newest || t > newest)) newest = t;
    });
    var html =
      pill("精选论文", TL.fmtNum(d.papers.length) + " 篇") +
      pill("官方语料", TL.fmtNum((m.corpus_total || 0)) + " 篇", m.corpus_total ? "" : "hide") +
      pill("主题", Object.keys(countsBy(function (p) { return p.topics; })).length + " 类") +
      '<span class="pill ' + (state.source === "api" ? "live" : "offline") + '" title="' +
      (state.source === "api" ? "本地服务在线，可回源刷新" : "内联快照模式：不发网络请求，file:// 可离线打开") + '">' +
      '<i class="dot" style="--st:currentColor"></i>' +
      (state.source === "api" ? "原生连接 · 在线" : "原生连接 · 快照") + "</span>" +
      pill("抓取于", TL.fmtTime(newest));
    $("facts").innerHTML = html.replace(/<span class="pill hide">.*?<\/span>/g, "");
  }

  function pill(k, v) { return '<span class="pill"><b>' + v + "</b> " + k + "</span>"; }

  function renderStats() {
    var d = state.data;
    // 统计卡随届次筛选联动（否则选了 2024 还显示三届总量会误导）
    var byVenue = {};
    d.papers.forEach(function (p) {
      if (state.year && String(p.year) !== String(state.year)) return;
      byVenue[p.venue] = (byVenue[p.venue] || 0) + 1;
    });
    var html = d.pillars.map(function (pl) {
      var on = state.venue === pl.key;
      var mine = d.papers.filter(function (p) {
        return p.venue === pl.key && (!state.year || String(p.year) === String(state.year));
      });
      var yrs = mine.map(function (p) { return p.year; }).sort();
      var span = yrs.length ? (yrs[0] === yrs[yrs.length - 1]
        ? String(yrs[0]) : yrs[0] + "–" + yrs[yrs.length - 1]) : "";
      var nEd = Object.keys(mine.reduce(function (a, p) { a[p.year] = 1; return a; }, {})).length;
      return '<button type="button" class="stat' + (on ? " on" : "") + '" data-pillar="' + pl.key +
        '" data-act="venue" data-val="' + pl.key + '" aria-pressed="' + on + '">' +
        '<span class="k"><i class="dot"></i>' + pl.label + " " + span + "</span>" +
        '<span class="v">' + TL.fmtNum(byVenue[pl.key] || 0) + '<span style="font-size:12px;color:var(--muted);font-family:var(--sans);font-weight:400"> 篇</span></span>' +
        '<span class="s">' + TL.esc(pl.field) + " · " + nEd + " 届 · " +
          TL.esc(pl.source.split(" (")[0]) + "</span>" +
        "</button>";
    }).join("");
    var tcount = Object.keys(countsBy(function (p) { return p.topics; })).length;
    var shown = d.papers.filter(function (p) {
      return !state.year || String(p.year) === String(state.year);
    }).length;
    html += '<button type="button" class="stat" data-act="reset" style="--st:var(--accent)">' +
      '<span class="k"><i class="dot"></i>全部精选</span>' +
      '<span class="v" style="color:var(--accent)">' + TL.fmtNum(shown) +
      '<span style="font-size:12px;color:var(--muted);font-family:var(--sans);font-weight:400"> 篇</span></span>' +
      '<span class="s">跨 ' + tcount + " 个主题 · 清除筛选</span></button>";
    $("stats").innerHTML = html;
  }

  function renderFilterbar() {
    var bar = $("filterbar");
    var bits = [];
    if (state.venue) bits.push(chip("支柱：" + state.venue, "venue", "plain"));
    if (state.topic) {
      var tm = topicMeta(state.topic);
      bits.push('<button type="button" class="chip" data-act="topic" data-val="" data-accent="' +
        tm.accent + '" aria-pressed="true">主题：' + TL.esc(tm.label) + " ×</button>");
    }
    if (state.year) bits.push(chip("届次：" + state.year, "year", "plain"));
    if (state.q) bits.push(chip("搜索：“" + state.q + "”", "q", "plain"));
    if (!bits.length) {
      var cnt = countsBy(function (p) { return p.topics; });
      bar.innerHTML = '<span class="label">主题筛选</span>' + state.data.topics.filter(function (t) { return cnt[t.id]; })
        .map(function (t) {
          return '<button type="button" class="chip" data-act="topic" data-val="' + t.id +
            '" data-accent="' + t.accent + '" aria-pressed="false">' + TL.esc(t.label) +
            '<span class="n">' + cnt[t.id] + "</span></button>";
        }).join("") +
        '<span class="chip plain" title="' + TL.esc(state.data.umbrella.note) + '">' +
        TL.esc(state.data.umbrella.label) + '<span class="n">' + state.data.papers.length + "</span></span>";
      return;
    }
    bar.innerHTML = '<span class="label">当前筛选</span>' + bits.join("") +
      '<button type="button" class="btn" data-act="reset" style="padding:3px 10px;font-size:12.5px">清除全部</button>';
  }

  function chip(text, act, cls) {
    return '<button type="button" class="chip ' + (cls || "") + '" data-act="' + act +
      '" data-val="">' + TL.esc(text) + " ×</button>";
  }

  function renderView() {
    if (state.view === "topics") return renderTopics();
    if (state.view === "repro") return renderRepro();
    if (state.view === "fav") return renderFav();
    return renderPillars();
  }

  /* ---------------- 收藏视图 ---------------- */
  function favNote() {
    return TL.SERVED
      ? "收藏落盘在本地服务 data/favs.json，换浏览器 / 换端口 / 清缓存都不会丢；点论文卡右上角 ★ 收藏 / 取消"
      : "当前是 file:// 直开，收藏只存在本机浏览器；用 start.bat 打开即可写入 data/favs.json，换浏览器也不丢";
  }
  function renderFav() {
    var root = $("view-root");
    var rows = filtered();
    // 最新收藏排最前
    rows.sort(function (a, b) { return state.favs.indexOf(b.id) - state.favs.indexOf(a.id); });
    var known = {}, missing = 0;
    if (state.data) {
      state.data.papers.forEach(function (p) { known[p.id] = 1; });
      state.favs.forEach(function (id) { if (!known[id]) missing++; });
    }
    var html = '<div class="section-head"><h2>我的收藏</h2>' +
      '<span class="note">' + TL.esc(favNote()) +
      (missing ? "；另有 " + missing + " 条不在当前精选数据中（清单调整过），已保留但无法显示" : "") +
      '</span><span class="rule"></span></div>';
    if (!state.favs.length) {
      root.innerHTML = html + '<div class="empty" style="margin-top:24px"><h3>还没有收藏</h3>' +
        '<div>在「四支柱」「主题视图」「复现情报」或详情弹窗里点 ★，即可收进这里。</div>' +
        '<button type="button" class="btn" data-act="goto-pillars" style="margin-top:var(--s-4)">去逛逛四支柱</button></div>';
      return;
    }
    if (!rows.length) {
      root.innerHTML = html + '<div class="empty" style="margin-top:24px"><h3>当前筛选下没有收藏</h3>' +
        '<div>已收藏 ' + state.favs.length + ' 篇，但都不符合当前届次 / 支柱 / 搜索条件。</div>' +
        '<button type="button" class="btn" data-act="reset" style="margin-top:var(--s-4)">清除筛选</button></div>';
      return;
    }
    root.innerHTML = html + '<div class="card-grid">' + rows.map(card).join("") + "</div>";
  }

  function renderPillars() {
    var rows = filtered();
    var root = $("view-root");
    if (!rows.length) return emptyState();
    var html = '<div class="section-head"><h2>四支柱</h2>' +
      '<span class="note">每根支柱对应一个顶会，数据取自该会官方开放获取系统</span>' +
      '<span class="rule"></span></div>';
    html += '<div class="pillar-grid">' + state.data.pillars.map(function (pl) {
      if (state.venue && state.venue !== pl.key) return "";
      var items = rows.filter(function (p) { return p.venue === pl.key; });
      if (!items.length) return "";
      return '<section class="pillar" data-pillar="' + pl.key + '" id="pillar-' + pl.key + '">' +
        '<header class="pillar-head"><div class="row">' +
        '<span class="dot" aria-hidden="true"></span><h3>' + pl.label + "</h3>" +
        '<span class="year">' + pl.year + "</span>" +
        '<span class="count">' + items.length + " 篇</span></div>" +
        '<div class="full">' + TL.esc(pl.full_name_zh) + " · " + TL.esc(pl.full_name) + "</div>" +
        '<div class="src">◦ <a href="' + TL.esc(pl.source_url) + '" target="_blank" rel="noopener">' +
        TL.esc(pl.source) + "</a></div></header>" +
        '<div class="pillar-body">' + items.map(card).join("") + "</div></section>";
    }).join("") + "</div>";
    root.innerHTML = html;
  }

  function renderTopics() {
    var rows = filtered();
    var cnt = countsBy(function (p) { return p.topics; });
    var root = $("view-root");
    if (!rows.length) return emptyState();
    var um = state.data.umbrella;
    var html = '<div class="section-head"><h2>主题视图</h2>' +
      '<span class="note">' + TL.esc(state.data.topic_disclaimer || um.note) + "</span>" +
      '<span class="rule"></span></div>';
    html += '<div class="filterbar" style="margin-bottom:20px"><span class="label">总览</span>' +
      '<span class="chip plain" title="' + TL.esc(um.note) + '">' + TL.esc(um.label) +
      '<span class="n">' + state.data.papers.length + "</span></span></div>";

    state.data.topics.forEach(function (t) {
      if (state.topic && state.topic !== t.id) return;
      var items = rows.filter(function (p) { return p.topics.indexOf(t.id) >= 0; });
      if (!items.length) return;
      var mix = {};
      items.forEach(function (p) { mix[p.venue] = (mix[p.venue] || 0) + 1; });
      html += '<section class="topic-group" data-accent="' + t.accent + '" id="topic-' + t.id + '">' +
        '<header class="group-head"><span class="dot" aria-hidden="true"></span>' +
        "<h3>" + TL.esc(t.label) + '</h3><span class="en">' + TL.esc(t.label_en) + "</span>" +
        '<span class="mix">' + Object.keys(mix).map(function (v) {
          return '<span class="tag" data-pillar="' + v + '" style="background:var(--st);opacity:.85;color:#fff">' +
            v + " " + mix[v] + "</span>";
        }).join("") + "</span>" +
        '<span class="n">' + items.length + " 篇</span></header>" +
        '<div class="card-grid">' + items.map(card).join("") + "</div></section>";
    });
    root.innerHTML = html;
  }

  /* ---------------- 复现情报视图 ---------------- */
  var DIFFS = [
    { key: "easy",    label: "易复现", en: "EASY",    accent: "green" },
    { key: "medium",  label: "中等",   en: "MEDIUM",  accent: "amber" },
    { key: "hard",    label: "困难",   en: "HARD",    accent: "rose" },
    { key: "unknown", label: "未查明", en: "N/A",     accent: "slate" }
  ];
  var COMPUTE_LABEL = {
    single_gpu: "单卡可跑", multi_gpu: "多卡训练",
    large_scale: "大规模算力", n_a: "无需完整训练"
  };
  var ACCESS_LABEL = { public: "公开下载", application: "需申请", private: "私有数据", synthetic: "合成数据" };

  function reproEntry(p) {
    var r = window.REPRO_DATA;
    return (r && r.papers && r.papers[p.id]) || null;
  }
  function reproDiff(p) {
    var e = reproEntry(p);
    return (e && e.difficulty) ? e.difficulty : "unknown";
  }
  function diffMeta(key) {
    for (var i = 0; i < DIFFS.length; i++) if (DIFFS[i].key === key) return DIFFS[i];
    return DIFFS[DIFFS.length - 1];
  }
  function repoLabel(e) {
    if (!e.github) return "";
    var bits = [e.github_official ? "官方仓库" : "第三方实现"];
    if (e.github_stars) bits.push("★ " + TL.fmtNum(e.github_stars));
    return bits.join(" · ");
  }

  function repoSlug(url) {
    var m = /github\.com\/([^/]+\/[^/#?]+)/i.exec(url || "");
    return m ? m[1] : (url || "");
  }

  function reproSection(p) {
    var e = reproEntry(p);
    var d = reproDiff(p), dm = diffMeta(d);
    var html = '<section><h3>复现情报 <span class="tag" data-accent="' + dm.accent + '">' +
      dm.label + '</span>' +
      (e ? '<button type="button" class="btn" data-act="diff" data-val="' + d +
        '" style="margin-left:auto;padding:3px 10px;font-size:12px;font-weight:400">看同难度论文 →</button>' : "") +
      "</h3>";
    if (!e) {
      html += '<p style="margin:0;font-size:12.5px;color:var(--muted)">外部调研未确认到该论文的公开仓库与数据集信息。</p></section>';
      return html;
    }
    html += '<div class="repro-kv">';
    html += '<div class="k">代码</div><div class="v">' +
      (e.github ? '<a href="' + TL.esc(e.github) + '" target="_blank" rel="noopener">' +
        TL.esc(repoSlug(e.github)) + "</a> <span class=\"rl-m\">" +
        (e.github_official ? "官方仓库" : "第三方实现") +
        (e.github_stars ? " · ★ " + TL.fmtNum(e.github_stars) : "") + "</span>"
        : '<span class="rl none">未找到公开实现（需按论文自行复现）</span>') + "</div>";
    if (e.datasets && e.datasets.length) {
      html += '<div class="k">数据集</div><div class="v">' + e.datasets.map(function (ds) {
        var acc = ACCESS_LABEL[ds.accessibility] || "";
        var t = TL.esc(ds.name) + (acc ? '<span class="rl-m">' + acc + "</span>" : "");
        return ds.url ? '<a href="' + TL.esc(ds.url) + '" target="_blank" rel="noopener">' + t + "</a>"
                      : "<span>" + t + "</span>";
      }).join("、") + "</div>";
    }
    if (e.compute) {
      html += '<div class="k">算力</div><div class="v">' +
        TL.esc(COMPUTE_LABEL[e.compute] || e.compute) + "</div>";
    }
    if (e.reason) {
      html += '<div class="k">判定理由</div><div class="v">' + TL.esc(e.reason) + "</div>";
    }
    html += "</div>";
    html += '<p style="margin:8px 0 0;font-size:11.5px;color:var(--muted)">三要素口径：官方代码是否公开 × 数据集可得性 × 算力需求；' +
      "来自本项目外部调研，非出版方信息，星标为调研时约数。</p>";
    return html + "</section>";
  }

  function renderRepro() {
    var rows = filtered();
    var root = $("view-root");
    if (!rows.length) return emptyState();
    var dist = {};
    rows.forEach(function (p) { var d = reproDiff(p); dist[d] = (dist[d] || 0) + 1; });
    var html = '<div class="section-head"><h2>复现情报</h2>' +
      '<span class="note">GitHub 仓库、数据集可得性与算力需求的外部调研；易＝官方代码+公开数据+单卡可跑，中＝有代码但数据受限或需多卡，难＝无官方代码或算力/数据门槛高</span>' +
      '<span class="rule"></span></div>';
    html += '<div class="diffbar" role="group" aria-label="按复现难度筛选"><span class="label">难度筛选</span>' +
      '<button type="button" class="chip" data-act="diff" data-val="" aria-pressed="' + (!state.diff) +
      '">全部<span class="n">' + rows.length + "</span></button>" +
      DIFFS.filter(function (d) { return dist[d.key]; }).map(function (d) {
        return '<button type="button" class="chip" data-accent="' + d.accent + '" data-act="diff" data-val="' +
          d.key + '" aria-pressed="' + (state.diff === d.key) + '">' + d.label +
          '<span class="n">' + dist[d.key] + "</span></button>";
      }).join("") + "</div>";
    DIFFS.forEach(function (d) {
      if (state.diff && state.diff !== d.key) return;
      var items = rows.filter(function (p) { return reproDiff(p) === d.key; });
      if (!items.length) return;
      html += '<section class="repro-group" data-accent="' + d.accent + '" id="rdiff-' + d.key + '">' +
        '<header class="group-head"><span class="dot" aria-hidden="true"></span>' +
        "<h3>" + d.label + '</h3><span class="en">' + d.en + "</span>" +
        '<span class="n">' + items.length + " 篇</span></header>" +
        '<div class="repro-list">' + items.map(reproRow).join("") + "</div></section>";
    });
    root.innerHTML = html;
  }

  function reproRow(p) {
    var e = reproEntry(p);
    var d = reproDiff(p), dm = diffMeta(d);
    var links = "";
    if (e && e.github) {
      links += '<a class="rl" href="' + TL.esc(e.github) + '" target="_blank" rel="noopener" title="' +
        TL.esc(repoLabel(e)) + '">GitHub<span class="rl-m">' + TL.esc(e.github_official ? "官方" : "第三方") +
        (e.github_stars ? " ★" + TL.fmtNum(e.github_stars) : "") + "</span></a>";
    } else {
      links += '<span class="rl none">未找到公开仓库</span>';
    }
    ((e && e.datasets) || []).slice(0, 3).forEach(function (ds) {
      var acc = ACCESS_LABEL[ds.accessibility] || "";
      links += ds.url
        ? '<a class="rl" href="' + TL.esc(ds.url) + '" target="_blank" rel="noopener">' + TL.esc(ds.name) +
          (acc ? '<span class="rl-m">' + acc + "</span>" : "") + "</a>"
        : '<span class="rl">' + TL.esc(ds.name) + (acc ? '<span class="rl-m">' + acc + "</span>" : "") + "</span>";
    });
    var comp = e && e.compute ? (COMPUTE_LABEL[e.compute] || e.compute) : "";
    return '<article id="card-' + p.id + '" class="repro-row" data-pillar="' + TL.esc(p.venue) +
      '" data-accent="' + dm.accent + '">' +
      '<div class="repro-top"><span class="yr">' + TL.esc(p.venue) + " " + p.year + "</span>" +
      '<span class="tag" data-accent="' + dm.accent + '">' + dm.label + "</span>" +
      (comp ? '<span class="rl-m">' + comp + "</span>" : "") +
      favBtn(p, "fav-inline") +
      '<button type="button" class="repro-open" data-act="open" data-val="' + p.id + '">详情</button></div>' +
      '<h4><a href="#card-' + p.id + '" data-act="open" data-val="' + p.id + '">' +
      TL.highlight(p.title, state.q) + "</a></h4>" +
      '<p class="tzh">' + TL.highlight(p.title_zh, state.q) + "</p>" +
      '<div class="repro-links">' + links + "</div>" +
      (e && e.reason ? '<p class="repro-why">' + TL.esc(e.reason) + "</p>" :
        (e ? "" : '<p class="repro-why dim">外部调研未确认到公开仓库与数据集信息。</p>')) +
      "</article>";
  }

  /* ---------------- 目录侧栏 ---------------- */
  function tocLabel(p) {
    var s = p.title_zh || p.title || "";
    var i = Math.max(s.indexOf("："), s.indexOf(":"));
    if (i > 1 && i <= 20) return s.slice(0, i);
    return s.length > 20 ? s.slice(0, 19) + "…" : s;
  }

  function renderToc() {
    var rows = filtered();
    var nav = $("toc");
    if (!rows.length) { nav.innerHTML = '<div class="toc-head"><b>目录</b><span>无结果</span></div>'; return; }
    var head = '<div class="toc-head"><b>目录</b><span>' + rows.length + " 篇</span></div>";
    var secs = [];

    if (state.view === "pillars") {
      state.data.pillars.forEach(function (pl) {
        if (state.venue && state.venue !== pl.key) return;
        var items = rows.filter(function (p) { return p.venue === pl.key; });
        if (!items.length) return;
        var ys2 = items.map(function (p) { return p.year; }).sort();
        var span2 = ys2[0] === ys2[ys2.length - 1] ? String(ys2[0])
          : ys2[0] + "–" + ys2[ys2.length - 1];
        secs.push('<div class="toc-sec" data-pillar="' + pl.key + '">' +
          '<a class="h" href="#pillar-' + pl.key + '" data-act="jump" data-val="pillar-' + pl.key + '">' +
          '<i class="dot" aria-hidden="true"></i>' + pl.label + " " + span2 +
          '<span class="n">' + items.length + "</span></a>" +
          items.map(function (p) {
            return '<a class="toc-item" href="#card-' + p.id + '" data-act="jump" data-val="card-' + p.id +
              '" data-card="' + p.id + '"><span class="rk">' + String(p.rank).padStart(2, "0") + "</span>" +
              TL.esc(tocLabel(p)) + "</a>";
          }).join("") + "</div>");
      });
    } else if (state.view === "fav") {
      var frows = rows.slice().sort(function (a, b) {
        return state.favs.indexOf(b.id) - state.favs.indexOf(a.id);
      });
      if (frows.length) {
        secs.push('<div class="toc-sec" data-accent="amber">' +
          '<a class="h" href="#view-root" data-act="jump" data-val="view-root">' +
          '<i class="dot" aria-hidden="true" style="--st:var(--tc-fg)"></i>我的收藏' +
          '<span class="n">' + frows.length + "</span></a>" +
          frows.map(function (p) {
            return '<a class="toc-item" href="#card-' + p.id + '" data-act="jump" data-val="card-' + p.id +
              '" data-card="' + p.id + '"><span class="rk">' + p.venue + "</span>" +
              TL.esc(tocLabel(p)) + "</a>";
          }).join("") + "</div>");
      }
    } else if (state.view === "repro") {
      DIFFS.forEach(function (d) {
        if (state.diff && state.diff !== d.key) return;
        var items = rows.filter(function (p) { return reproDiff(p) === d.key; });
        if (!items.length) return;
        secs.push('<div class="toc-sec" data-accent="' + d.accent + '">' +
          '<a class="h" href="#rdiff-' + d.key + '" data-act="jump" data-val="rdiff-' + d.key + '">' +
          '<i class="dot" aria-hidden="true" style="--st:var(--tc-fg)"></i>' + d.label +
          '<span class="n">' + items.length + "</span></a>" +
          items.map(function (p) {
            return '<a class="toc-item" href="#card-' + p.id + '" data-act="jump" data-val="card-' + p.id +
              '" data-card="' + p.id + '"><span class="rk">' + p.venue + "</span>" +
              TL.esc(tocLabel(p)) + "</a>";
          }).join("") + "</div>");
      });
    } else {
      state.data.topics.forEach(function (t) {
        var items = rows.filter(function (p) { return p.topics.indexOf(t.id) >= 0; });
        if (!items.length) return;
        /* 一篇可属多个主题，全展开会重复；只在选中该主题时才列出其论文 */
        var expand = state.topic === t.id;
        secs.push('<div class="toc-sec" data-accent="' + t.accent + '">' +
          '<a class="h" href="#topic-' + t.id + '" data-act="jump" data-val="topic-' + t.id + '">' +
          '<i class="dot" aria-hidden="true" style="--st:var(--tc-fg)"></i>' + TL.esc(t.label) +
          '<span class="n">' + items.length + "</span></a>" +
          (expand ? items.map(function (p) {
            return '<a class="toc-item" href="#card-' + p.id + '" data-act="jump" data-val="card-' + p.id +
              '" data-card="' + p.id + '"><span class="rk">' + p.venue + "</span>" +
              TL.esc(tocLabel(p)) + "</a>";
          }).join("") : "") + "</div>");
      });
    }
    nav.innerHTML = head + secs.join("");
    spy();
  }

  function jumpTo(target) {
    var node = document.getElementById(target);
    if (!node) return;
    node.scrollIntoView({ behavior: "smooth", block: "start" });
    if (node.classList.contains("pcard")) {
      node.classList.remove("flash");
      void node.offsetWidth;                       /* restart the animation */
      node.classList.add("flash");
      setTimeout(function () { node.classList.remove("flash"); }, 1200);
    }
  }

  function syncToc() {
    document.body.classList.toggle("toc-closed", !state.tocOpen);
    var b = $("btn-toc");
    if (b) b.setAttribute("aria-expanded", String(state.tocOpen));
  }

  /* 滚动时同步目录高亮：取最靠近顶栏下沿的那张卡/组 */
  function spy() {
    var nav = $("toc");
    if (!nav || !state.tocOpen) return;
    var line = (parseInt(getComputedStyle(document.documentElement).getPropertyValue("--topbar-h"), 10) || 62) + 90;
    var best = null, bestTop = -Infinity;
    nav.querySelectorAll("[data-card]").forEach(function (a) {
      var card = document.getElementById("card-" + a.dataset.card);
      if (!card) return;
      var top = card.getBoundingClientRect().top;
      if (top <= line && top > bestTop) { bestTop = top; best = a; }
    });
    if (!best) {
      var first = nav.querySelector("[data-card]");
      if (first) { best = first; }
    }
    nav.querySelectorAll(".toc-item.on").forEach(function (a) { a.classList.remove("on"); });
    if (best) best.classList.add("on");
  }

  function card(p) {
    var kws = (p.keywords || []).slice(0, 3);
    var e = reproEntry(p);
    var dm = e && e.difficulty ? diffMeta(e.difficulty) : null;
    var reproTag = dm ? '<span class="tag" data-accent="' + dm.accent + '" title="复现难度（官方代码+数据集+算力三要素，外部调研派生）：' +
      dm.label + (e.github ? "，有" + (e.github_official ? "官方" : "第三方") + "代码" : "，未找到公开代码") +
      '">复现·' + dm.label.replace("复现", "") + "</span>" : "";
    return '<article id="card-' + p.id + '" ' + TL.pillarBadge(p.venue) + ' tabindex="0" role="button" ' +
      'data-act="open" data-val="' + p.id + '" aria-label="查看 ' + TL.esc(p.title) + '">' +
      favBtn(p) +
      '<span class="idx">' + String(p.rank).padStart(2, "0") + "</span>" +
      "<h4>" + TL.highlight(p.title, state.q) + "</h4>" +
      '<p class="tzh">' + TL.highlight(p.title_zh, state.q) + "</p>" +
      '<p class="auth">' + TL.esc(authorsLine(p)) + "</p>" +
      '<div class="topics"><span class="yr">' + p.year + "</span>" + reproTag + p.topics.map(function (t) {
        var tm = topicMeta(t);
        return '<span class="tag" data-accent="' + tm.accent + '">' + TL.esc(tm.label) + "</span>";
      }).join("") + "</div>" +
      '<p class="zh">' + TL.highlight(p.abstract_zh, state.q) + "</p>" +
      '<div class="kw">' + kws.map(function (k) {
        return '<span class="kw-chip">' + TL.esc(k.en) + "</span>";
      }).join("") + "</div></article>";
  }

  function authorsLine(p) {
    if (!p.authors || !p.authors.length) return "作者信息以官方页面为准";
    if (p.authors.length <= 4) return p.authors.join(" · ");
    return p.authors.slice(0, 3).join(", ") + " 等 " + p.authors.length + " 人";
  }

  function emptyState() {
    $("view-root").innerHTML = '<div class="empty" style="margin-top:24px">' +
      "<h3>没有匹配的论文</h3><div>当前筛选：" +
      (state.q ? "搜索「" + TL.esc(state.q) + "」 " : "") +
      (state.venue ? "支柱 " + state.venue + " " : "") +
      (state.topic ? "主题 " + TL.esc(topicMeta(state.topic).label) : "") +
      '</div><button type="button" class="btn" data-act="reset">清除全部筛选</button></div>';
  }

  /* ---------------- 详情模态框 ---------------- */
  // 打开时锁背景滚动并补偿滚动条宽度；关闭时原样恢复。
  function lockScroll(on) {
    var de = document.documentElement;
    var probe = document.querySelector(".wrap") || document.body;
    if (on) {
      // 先量、再锁、再量：滚动条消失/留存的行为各浏览器不一致，
      // 用真实宽度差补 padding，才能保证背景内容宽度一格不跳。
      var before = probe.getBoundingClientRect().width;
      de.classList.add("modal-open");
      var after = probe.getBoundingClientRect().width;
      var pad = parseFloat(getComputedStyle(de).paddingRight) || 0;
      de.style.paddingRight = Math.max(0, pad + (after - before)) + "px";
    } else {
      de.classList.remove("modal-open");
      de.style.paddingRight = "";
    }
  }

  function openModal(id) {
    var p = state.data.papers.filter(function (x) { return x.id === id; })[0];
    if (!p) return;
    state.paperId = id;
    var pl = pillarMeta(p.venue);
    var links = [];
    links.push(["论文页", p.links.official]);
    if (p.links.pdf) links.push(["PDF", p.links.pdf]);
    if (p.links.doi) links.push(["DOI", "https://doi.org/" + p.links.doi]);
    if (p.links.extra) links.push(["补充材料", p.links.extra]);
    if (p.links.record) links.push(["OpenAlex 记录", p.links.record]);
    var re = reproEntry(p);
    if (re && re.github) links.push([re.github_official ? "GitHub（官方代码）" : "GitHub（第三方实现）", re.github]);

    var html = '<div class="modal-scrim" data-act="close-scrim"><div class="modal" data-pillar="' +
      p.venue + '" role="dialog" aria-modal="true" aria-labelledby="m-title">' +
      '<button type="button" class="modal-close" data-act="close" aria-label="关闭">×</button>' +
      '<div class="modal-head"><h2 id="m-title">' + TL.esc(p.title) + "</h2>" +
      '<p class="tzh">' + TL.esc(p.title_zh) + "</p><div class='meta'>" +
      "<span>" + TL.esc(p.venue) + " " + p.year + "</span>" +
      "<span>" + TL.esc(pl.full_name_zh) + "</span>" +
      (p.pages ? "<span>pp. " + TL.esc(p.pages) + "</span>" : "") +
      (p.track ? "<span>" + TL.esc(p.track) + "</span>" : "") +
      (p.citations !== undefined && p.citations !== null ? "<span>OpenAlex 被引 " + TL.esc(p.citations) + "</span>" : "") +
      favBtn(p, "fav-modal") +
      "</div></div><div class='modal-body'>" +

      "<section><h3>中文摘要（人工翻译）</h3><p class='abs-zh'>" + TL.esc(p.abstract_zh) + "</p></section>" +

      "<section><h3>英文摘要（官方原文）</h3><details class='abs-en'><summary>展开 " +
      p.abstract.split(/(?<=\.)\s+/).length + " 句原文 · " + p.abstract.length + " 字符</summary>" +
      "<p>" + TL.esc(p.abstract) + "</p></details></section>" +

      "<section><h3>关键词</h3><div class='kw-list'>" + (p.keywords || []).map(function (k) {
        return '<span class="kw-pair">' + TL.esc(k.zh) + '<span class="en">' + TL.esc(k.en) + "</span></span>";
      }).join("") + "</div></section>" +

      "<section><h3>主题</h3><div class='kw-list'>" + p.topics.map(function (t) {
        var tm = topicMeta(t);
        return '<button type="button" class="chip" data-accent="' + tm.accent + '" data-act="topic" data-val="' +
          t + '">' + TL.esc(tm.label) + '<span class="n">' + tm.label_en + "</span></button>";
      }).join("") + "</div>" +
      (p.curator_note ? '<p style="margin:10px 0 0;font-size:12.5px;color:var(--muted)">策展说明：' +
        TL.esc(p.curator_note) + "</p>" : "") + "</section>" +

      "<section><h3>作者（" + p.authors.length + " 人）</h3><ul class='auth-list'>" +
      p.authors.map(function (a) { return "<li>" + TL.esc(a) + "</li>"; }).join("") + "</ul></section>" +

      reproSection(p) +

      "<section><h3>官方链接</h3><div class='link-row'>" + links.filter(function (l) { return l[1]; }).map(function (l) {
        return '<a class="btn" href="' + TL.esc(l[1]) + '" target="_blank" rel="noopener">' + l[0] + "</a>";
      }).join("") + "</div></section>" +

      "<section><h3>引用（BibTeX）</h3>" +
      (p.citation && p.citation.text
        ? '<div class="cite-head"><span class="tag" data-accent="' + (p.citation.official ? "green" : "slate") + '">' +
          (p.citation.official ? "出版方官方原文" : "本项目按已核验字段渲染") + "</span>" +
          '<span style="font-size:11.5px;color:var(--muted)">' + TL.esc(p.citation.origin) + "</span>" +
          '<button type="button" class="btn" data-act="copy-cite" data-val="' + p.id + '" ' +
          'style="margin-left:auto;padding:3px 10px;font-size:12px">复制</button></div>' +
          "<pre class='cite' id='cite-" + p.id + "'>" + TL.esc(p.citation.text) + "</pre>"
        : '<p style="margin:0;font-size:12.5px;color:var(--muted)">未取到引用条目。</p>') + "</section>" +

      "<section><h3>数据溯源</h3><div class='prov'>来源：<b>" + TL.esc(p.provenance.source) +
      "</b> ｜ 摘要取自：" + TL.esc(p.provenance.abstract_source) +
      " ｜ 抓取时间：" + TL.fmtTime(p.provenance.retrieved_at) + "（" + TL.relTime(p.provenance.retrieved_at) + "）" +
      " ｜ 官方记录号 <code>" + TL.esc(p.provenance.paper_id) + "</code><br>" +
      "中文摘要为人工翻译，与官方英文原文逐句对照；主题标签为本项目派生。" +
      (p.citations_source ? " ｜ 被引数来自 <code>" + TL.esc(p.citations_source) + "</code>" : "") +
      "</div></section>" +

      "</div></div></div>";
    $("modal-root").innerHTML = html;
    // 锁背景滚动：class 交给 CSS（html.modal-open），滚动条宽度写进 --sbw 做等宽补偿，
    // 否则滚动条消失会让整页横向抖 15px。
    lockScroll(true);
    var btn = $("modal-root").querySelector(".modal-close");
    if (btn) btn.focus();
  }

  function closeModal() {
    state.paperId = null;
    $("modal-root").innerHTML = "";
    lockScroll(false);
  }

  /* ---------------- 事件（单点委托，Trace Light 的 data-act 约定） ---------------- */
  function onClick(e) {
    var t = e.target.closest("[data-act]");
    if (!t) return;
    var act = t.dataset.act, val = t.dataset.val;
    if (act === "open") { e.preventDefault(); openModal(val); return; }
    if (act === "jump") { e.preventDefault(); jumpTo(val); return; }
    if (act === "copy-cite") {
      e.preventDefault();
      TL.copyText((document.getElementById("cite-" + val) || {}).textContent || "")
        .then(function (ok) { TL.toast(ok ? "BibTeX 已复制到剪贴板" : "浏览器拒绝了剪贴板，已选中文字，按 Ctrl+C 复制", ok ? "ok" : "warn"); });
      return;
    }
    if (act === "close" || act === "close-scrim") { if (e.target === t) closeModal(); return; }
    if (act === "venue") { state.venue = state.venue === val ? null : val; state.topic = null; renderAll(); return; }
    if (act === "year") { state.year = (!val || String(state.year) === String(val)) ? null : val; renderAll(); return; }
    if (act === "topic") {
      closeModal();
      state.topic = (!val || state.topic === val) ? null : val;
      /* 主题 chip 只有在「四支柱」视图里才兼作入口（下钻 → 主题视图）。
         在「复现情报 / 收藏 / 主题视图」里它就是一个筛选器，点一下必须就地过滤，
         不能把用户踢出当前视图 —— 在复现情报里被踢走就看不到复现信息了。 */
      if (val && state.view === "pillars") { state.view = "topics"; syncViewTabs(); }
      renderAll();
      return;
    }
    if (act === "fav") {
      e.preventDefault();
      var on = toggleFav(val);
      syncFavBtns(val);
      syncViewTabs();
      if (state.view === "fav") { renderView(); renderToc(); }
      TL.toast(on ? (TL.SERVED ? "已收藏，写入 data/favs.json" : "已收藏（仅本机浏览器，用 start.bat 打开可落盘）")
                  : "已取消收藏", on ? "ok" : null);
      return;
    }
    if (act === "goto-pillars") { state.view = "pillars"; syncViewTabs(); renderView(); renderFilterbar(); renderToc(); return; }
    if (act === "reset") { state.venue = null; state.topic = null; state.year = null; state.diff = null; state.q = ""; $("q").value = ""; syncClear(); renderAll(); return; }
    if (act === "q") { state.q = ""; $("q").value = ""; syncClear(); renderAll(); return; }
    if (act === "diff") {
      state.diff = (!val || state.diff === val) ? null : val;
      if (state.view !== "repro") { state.view = "repro"; syncViewTabs(); }
      if (state.paperId) closeModal();
      renderView(); renderToc(); return;
    }
  }

  function syncViewTabs() {
    $("view-pillars").setAttribute("aria-pressed", String(state.view === "pillars"));
    $("view-topics").setAttribute("aria-pressed", String(state.view === "topics"));
    $("view-repro").setAttribute("aria-pressed", String(state.view === "repro"));
    var n = $("view-fav-n");
    n.textContent = state.favs.length;
    n.hidden = !state.favs.length;
    $("view-fav").setAttribute("aria-pressed", String(state.view === "fav"));
  }
  function syncClear() { $("q-clear").hidden = !state.q; }

  function boot() {
    el.q = $("q");
    document.addEventListener("click", onClick);
    document.querySelectorAll("[data-view]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.view = b.dataset.view;
        if (state.view === "pillars") state.topic = null;
        syncViewTabs(); renderView(); renderFilterbar(); renderToc();
      });
    });
    $("btn-toc").addEventListener("click", function () {
      state.tocOpen = !state.tocOpen;
      localStorage.setItem("topconf.toc", state.tocOpen ? "1" : "0");
      syncToc();
      if (state.tocOpen) spy();
    });
    var spyQueued = false;
    window.addEventListener("scroll", function () {
      if (spyQueued) return;
      spyQueued = true;
      requestAnimationFrame(function () { spyQueued = false; spy(); });
    }, { passive: true });
    var timer = null;
    el.q.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { state.q = el.q.value; syncClear(); renderAll(); }, 120);
    });
    $("q-clear").addEventListener("click", function () {
      state.q = ""; el.q.value = ""; syncClear(); renderAll(); el.q.focus();
    });
    $("btn-theme").addEventListener("click", function () {
      var pref = TL.cycleTheme();
      TL.toast("主题：" + ({ auto: "跟随系统", light: "浅色", dark: "深色" })[pref]);
    });
    $("btn-refresh").addEventListener("click", refresh);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && state.paperId) closeModal();
      if (e.key === "/" && document.activeElement !== el.q) { e.preventDefault(); el.q.focus(); }
      if ((e.key === "Enter" || e.key === " ") && document.activeElement &&
          document.activeElement.dataset && document.activeElement.dataset.act === "open") {
        e.preventDefault(); openModal(document.activeElement.dataset.val);
      }
    });
    TL.paintThemeBtn();
    if (!TL.SERVED) {
      $("btn-refresh").disabled = true;
      $("btn-refresh").title = "需通过 python scripts/serve.py 打开才能回源刷新";
    }
    syncFavsFromServer();    // 先与本地服务对齐收藏，再渲染（避免闪一下再变）
    loadData();
  }

  function refresh() {
    var b = $("btn-refresh");
    b.classList.add("spin"); b.disabled = true;
    TL.api("/api/refresh", { method: "POST" }).then(function (d) {
      state.data = d; state.source = "api";
      renderAll();
      TL.toast("已直连官方源刷新：" + d.papers.length + " 篇", "ok");
    }).catch(function (e) {
      TL.toast("刷新失败：" + e.message, "err");
    }).finally(function () {
      b.classList.remove("spin"); b.disabled = false;
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
