/* app.js —— 页面主逻辑（IIFE + 单一 state + 纯渲染函数，结构对齐 Trace Light dashboard.js） */
(function () {
  "use strict";

  var state = {
    data: null,
    view: "pillars",        // pillars | topics
    q: "",
    venue: null,            // 单支柱下钻
    topic: null,            // 主题下钻
    paperId: null,          // 模态框
    source: null            // inline | api
  };

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
      if (q && haystack(p).indexOf(q) < 0) return false;
      return true;
    });
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
    renderStats();
    renderFilterbar();
    renderView();
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
    var byVenue = countsBy(function (p) { return [p.venue]; });
    var html = d.pillars.map(function (pl) {
      var on = state.venue === pl.key;
      var sample = d.papers.filter(function (p) { return p.venue === pl.key; })[0];
      return '<button type="button" class="stat' + (on ? " on" : "") + '" data-pillar="' + pl.key +
        '" data-act="venue" data-val="' + pl.key + '" aria-pressed="' + on + '">' +
        '<span class="k"><i class="dot"></i>' + pl.label + " " + pl.year + "</span>" +
        '<span class="v">' + TL.fmtNum(byVenue[pl.key] || 0) + '<span style="font-size:12px;color:var(--muted);font-family:var(--sans);font-weight:400"> 篇</span></span>' +
        '<span class="s">' + TL.esc(pl.field) + " · " + TL.esc(pl.source.split(" (")[0]) + "</span>" +
        "</button>";
    }).join("");
    var tcount = Object.keys(countsBy(function (p) { return p.topics; })).length;
    html += '<button type="button" class="stat" data-act="reset" style="--st:var(--accent)">' +
      '<span class="k"><i class="dot"></i>全部精选</span>' +
      '<span class="v" style="color:var(--accent)">' + TL.fmtNum(d.papers.length) +
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
    return renderPillars();
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

  function card(p) {
    var kws = (p.keywords || []).slice(0, 3);
    return '<article ' + TL.pillarBadge(p.venue) + ' tabindex="0" role="button" ' +
      'data-act="open" data-val="' + p.id + '" aria-label="查看 ' + TL.esc(p.title) + '">' +
      '<span class="idx">' + String(p.rank).padStart(2, "0") + "</span>" +
      "<h4>" + TL.highlight(p.title, state.q) + "</h4>" +
      '<p class="tzh">' + TL.highlight(p.title_zh, state.q) + "</p>" +
      '<p class="auth">' + TL.esc(authorsLine(p)) + "</p>" +
      '<div class="topics">' + p.topics.map(function (t) {
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

      "<section><h3>官方链接</h3><div class='link-row'>" + links.filter(function (l) { return l[1]; }).map(function (l) {
        return '<a class="btn" href="' + TL.esc(l[1]) + '" target="_blank" rel="noopener">' + l[0] + "</a>";
      }).join("") + "</div></section>" +

      "<section><h3>数据溯源</h3><div class='prov'>来源：<b>" + TL.esc(p.provenance.source) +
      "</b> ｜ 摘要取自：" + TL.esc(p.provenance.abstract_source) +
      " ｜ 抓取时间：" + TL.fmtTime(p.provenance.retrieved_at) + "（" + TL.relTime(p.provenance.retrieved_at) + "）" +
      " ｜ 官方记录号 <code>" + TL.esc(p.provenance.paper_id) + "</code><br>" +
      "中文摘要为人工翻译，与官方英文原文逐句对照；主题标签为本项目派生。" +
      (p.citations_source ? " ｜ 被引数来自 <code>" + TL.esc(p.citations_source) + "</code>" : "") +
      "</div></section>" +

      "</div></div></div>";
    $("modal-root").innerHTML = html;
    document.body.style.overflow = "hidden";
    var btn = $("modal-root").querySelector(".modal-close");
    if (btn) btn.focus();
  }

  function closeModal() {
    state.paperId = null;
    $("modal-root").innerHTML = "";
    document.body.style.overflow = "";
  }

  /* ---------------- 事件（单点委托，Trace Light 的 data-act 约定） ---------------- */
  function onClick(e) {
    var t = e.target.closest("[data-act]");
    if (!t) return;
    var act = t.dataset.act, val = t.dataset.val;
    if (act === "open") { e.preventDefault(); openModal(val); return; }
    if (act === "close" || act === "close-scrim") { if (e.target === t) closeModal(); return; }
    if (act === "venue") { state.venue = state.venue === val ? null : val; state.topic = null; renderAll(); return; }
    if (act === "topic") {
      closeModal();
      state.topic = (!val || state.topic === val) ? null : val;
      if (val) { state.view = "topics"; syncViewTabs(); }
      renderAll();
      return;
    }
    if (act === "reset") { state.venue = null; state.topic = null; state.q = ""; $("q").value = ""; syncClear(); renderAll(); return; }
    if (act === "q") { state.q = ""; $("q").value = ""; syncClear(); renderAll(); return; }
  }

  function syncViewTabs() {
    $("view-pillars").setAttribute("aria-pressed", String(state.view === "pillars"));
    $("view-topics").setAttribute("aria-pressed", String(state.view === "topics"));
  }
  function syncClear() { $("q-clear").hidden = !state.q; }

  function boot() {
    el.q = $("q");
    document.addEventListener("click", onClick);
    document.querySelectorAll("[data-view]").forEach(function (b) {
      b.addEventListener("click", function () {
        state.view = b.dataset.view;
        if (state.view === "pillars") state.topic = null;
        syncViewTabs(); renderView(); renderFilterbar();
      });
    });
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
