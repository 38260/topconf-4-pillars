/* common.js —— 全局工具（职责对应 Trace Light app/static/js/common.js）
   主题三态 auto|light|dark + localStorage、toast、fmt、api、色类映射       */
(function () {
  "use strict";

  var THEME_KEY = "topconf.theme";
  var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function themePref() { return localStorage.getItem(THEME_KEY) || "auto"; }
  function resolveTheme(pref) {
    if (pref === "auto") return (mq && mq.matches) ? "dark" : "light";
    return pref;
  }
  function applyTheme(pref) {
    document.documentElement.dataset.theme = resolveTheme(pref);
    document.documentElement.dataset.themePref = pref;
  }
  var THEME_LABEL = { auto: "跟随系统", light: "浅色", dark: "深色" };
  var THEME_ICON = { auto: "◐", light: "☀", dark: "☾" };

  function cycleTheme() {
    var order = ["auto", "light", "dark"];
    var next = order[(order.indexOf(themePref()) + 1) % order.length];
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
    paintThemeBtn();
    return next;
  }

  function paintThemeBtn() {
    var pref = themePref();
    var ico = document.getElementById("theme-ico");
    var txt = document.getElementById("theme-txt");
    if (ico) ico.textContent = THEME_ICON[pref] || "◐";
    if (txt) txt.textContent = THEME_LABEL[pref] || pref;
  }

  if (mq) mq.addEventListener("change", function () {
    if (themePref() === "auto") applyTheme("auto");
  });

  /* ---------- toast ---------- */
  function toast(msg, type) {
    var box = document.getElementById("toast-box");
    if (!box) return null;
    var el = document.createElement("div");
    el.className = "toast " + (type || "");
    el.setAttribute("role", "status");
    el.textContent = msg;
    box.appendChild(el);
    setTimeout(function () { el.classList.add("hide"); }, 4200);
    setTimeout(function () { el.remove(); }, 4700);
    return el;
  }

  /* ---------- formatters ---------- */
  function fmtNum(n) {
    if (n === null || n === undefined || isNaN(n)) return "-";
    return Number(n).toLocaleString("zh-CN");
  }
  function fmtTime(iso) {
    if (!iso) return "未知";
    var d = new Date(iso);
    if (isNaN(d)) return iso;
    var p = function (x) { return String(x).padStart(2, "0"); };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
           " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }
  function relTime(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "-";
    var mins = Math.round((Date.now() - d.getTime()) / 60000);
    if (mins < 1) return "刚刚";
    if (mins < 60) return mins + " 分钟前";
    if (mins < 60 * 24) return Math.round(mins / 60) + " 小时前";
    return Math.round(mins / 1440) + " 天前";
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function highlight(text, needle) {
    var out = esc(text);
    if (!needle) return out;
    var i = out.toLowerCase().indexOf(esc(needle).toLowerCase());
    if (i < 0) return out;
    return out.slice(0, i) + "<mark>" + out.slice(i, i + needle.length) + "</mark>" + out.slice(i + needle.length);
  }

  /* ---------- native connection：服务模式走 /api，file:// 用内联快照 ---------- */
  var SERVED = /^https?:$/.test(location.protocol);
  function api(path, opts) {
    if (!SERVED) return Promise.reject(new Error("file:// 下不发起网络请求"));
    return fetch(path, opts).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  /* ---------- 复制到剪贴板（file:// 属于非安全上下文，须留手写降级） ---------- */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; })
        .catch(function () { return legacyCopy(text); });
    }
    return Promise.resolve(legacyCopy(text));
  }
  function legacyCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;top:-1000px;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    if (!ok && document.createRange) {        // last resort: select it for Ctrl+C
      var range = document.createRange();
      range.selectNodeContents(ta);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
    ta.remove();
    return ok;
  }

  /* ---------- 色类映射（Trace Light statusBadgeClass / tagClass 同构） ---------- */
  function pillarBadge(key) { return 'class="pcard" data-pillar="' + esc(key) + '"'; }
  function topicAccent(id, meta) { return 'data-accent="' + esc((meta && meta.accent) || "slate") + '"'; }

  window.TL = {
    themePref: themePref, applyTheme: applyTheme, cycleTheme: cycleTheme,
    paintThemeBtn: paintThemeBtn, toast: toast,
    fmtNum: fmtNum, fmtTime: fmtTime, relTime: relTime,
    esc: esc, highlight: highlight, api: api, copyText: copyText,
    pillarBadge: pillarBadge, topicAccent: topicAccent, SERVED: SERVED
  };
  applyTheme(themePref());
})();
