/* ============================================================
   統計學習自學站共用函式庫
   由 tools/build_page.py 內嵌到每一頁，十頁完全一致。
   規則：LaTeX 一律放靜態 HTML，這裡的字串不放 $…$；
        寫入含數學的 innerHTML 之後要呼叫 HC.retype(el)。
   ============================================================ */

const $ = id => document.getElementById(id);

/* ---------- MathJax：注入後的內容不會自動排版 ---------- */
const HC = {};
HC.retype = el => {
  if (window.MathJax && window.MathJax.typesetPromise) {
    try { window.MathJax.typesetPromise(el ? [el] : undefined); } catch (e) { /* 排版失敗不擋互動 */ }
  }
};

/* ---------- quiz ---------- */
function quizCheck(quizId, optEl) {
  const isCorrect = optEl.dataset.correct === 'true';
  optEl.parentElement.querySelectorAll('.quiz-opt').forEach(o => o.classList.remove('correct', 'wrong'));
  optEl.classList.add(isCorrect ? 'correct' : 'wrong');
  const fb = $(quizId + 'Feedback');
  if (!fb) { console.error('quizCheck: 找不到 #' + quizId + 'Feedback'); return; }
  fb.classList.remove('correct', 'wrong');
  fb.classList.add('show', isCorrect ? 'correct' : 'wrong');
  fb.innerHTML = (isCorrect ? '<strong>正確 ✓</strong> ' : '<strong>不對 ✗</strong> ') + (optEl.dataset.fb || '');
  HC.retype(fb);
}

/* ---------- 程式碼行高亮 ---------- */
function hlLine(rootId, n) {
  const root = $(rootId);
  if (!root) return;
  root.querySelectorAll('.line').forEach(l => l.classList.remove('active'));
  if (n != null) {
    const line = root.querySelector('.line[data-l="' + n + '"]');
    if (line) line.classList.add('active');
  }
}

/* ---------- 逐步播放器：frames = [{...}]，apply(frame) 負責渲染 ---------- */
class Player {
  constructor({ frames, apply, delayInput, onDone, onIndex }) {
    this.frames = frames; this.apply = apply;
    this.delayInput = delayInput; this.i = -1; this.timer = null;
    this.onDone = onDone || (() => {});
    this.onIndex = onIndex || (() => {});
  }
  get delay() { return this.delayInput ? parseInt(this.delayInput.value, 10) : 700; }
  step() {
    if (this.i + 1 >= this.frames.length) { this.stop(); this.onDone(); return false; }
    this.i += 1; this.apply(this.frames[this.i], this.i); this.onIndex(this.i); return true;
  }
  play() {
    this.stop();
    const tick = () => { if (this.step()) this.timer = setTimeout(tick, this.delay); };
    tick();
  }
  stop() { if (this.timer) { clearTimeout(this.timer); this.timer = null; } }
  get playing() { return this.timer !== null; }
  reset() { this.stop(); this.i = -1; if (this.frames.length) { this.apply(this.frames[0], 0); this.i = 0; } }
  seek(i) { this.stop(); this.i = Math.max(0, Math.min(i, this.frames.length - 1)); this.apply(this.frames[this.i], this.i); this.onIndex(this.i); }
}
HC.Player = Player;

/* ---------- 旁白列 ---------- */
function setStatus(id, html) {
  const el = $(id); if (!el) return;
  const t = el.querySelector('.status-text');
  if (t) t.innerHTML = html;
}

/* ============================================================
   HC：圖表與 SVG 共用 API
   ============================================================ */

/* 設計 token（讀 CSS 變數，樣式改一處就好） */
HC.tok = (() => {
  const cs = getComputedStyle(document.documentElement);
  const g = n => cs.getPropertyValue('--' + n).trim();
  return {
    ink: g('ink'), paper: g('paper'), accent: g('accent'), accent2: g('accent2'),
    accent3: g('accent3'), muted: g('muted'), card: g('card'), cardBorder: g('card-border'),
    grid: g('grid-line') || g('card-border'),
    train: g('pt-train'), test: g('pt-test'), held: g('pt-held'),
    a: g('pt-a'), b: g('pt-b'), c: g('pt-c'),
    fit: g('fit-line'), truef: g('fit-true'), resid: g('resid'),
  };
})();

HC.MONO = "'JetBrains Mono', ui-monospace, monospace";

/* 數字格式：固定小數位，去掉負零 */
HC.fmt = (v, d = 2) => {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  const s = Number(v).toFixed(d);
  return s === '-' + (0).toFixed(d) ? (0).toFixed(d) : s;
};
HC.pct = (v, d = 1) => HC.fmt(v * 100, d) + '%';

/* canvas 的 strokeStyle 不認得 var(--x)，要先解析成實際色值 */
HC.color = c => {
  if (!c) return null;
  const m = /^var\((--[\w-]+)\)$/.exec(String(c).trim());
  if (!m) return c;
  const v = getComputedStyle(document.documentElement).getPropertyValue(m[1]).trim();
  return v || HC.tok.muted;
};

/* ---------- Chart.js ---------- */
HC.hasChart = () => typeof window.Chart !== 'undefined';

/* Chart.js 載入失敗時不要拋錯：讓 .chart-fallback 留在畫面上 */
HC.ready = fn => {
  const run = () => {
    if (!HC.hasChart()) { console.warn('Chart.js 未載入：圖表退回 .chart-fallback 文字'); return; }
    if (!HC._refReg) { window.Chart.register(HC._refPlugin); HC._refReg = true; }
    try { fn(); } catch (e) { console.error('圖表初始化失敗', e); }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
};

HC._charts = new Map();

/* 房子的 Chart.js 預設值 */
HC.base = (type, data, opts = {}) => {
  const t = HC.tok;
  const axis = {
    grid: { color: t.grid, drawTicks: false },
    border: { color: t.muted },
    ticks: { font: { family: HC.MONO, size: 11 }, color: t.muted, padding: 6 },
    title: { font: { family: HC.MONO, size: 11, weight: '600' }, color: t.accent2 },
  };
  const deep = (a, b) => {
    const o = Array.isArray(b) ? b.slice() : Object.assign({}, a);
    if (Array.isArray(b)) return o;
    for (const k of Object.keys(b || {})) {
      o[k] = (b[k] && typeof b[k] === 'object' && !Array.isArray(b[k]))
        ? deep(a && a[k] ? a[k] : {}, b[k]) : b[k];
    }
    return o;
  };
  const defaults = {
    responsive: true, maintainAspectRatio: false, devicePixelRatio: 2,
    animation: { duration: 250 },
    interaction: { mode: 'index', intersect: false },
    layout: { padding: { top: 6, right: 10, bottom: 2, left: 2 } },
    plugins: {
      legend: {
        display: true, position: 'top', align: 'end',
        labels: { boxWidth: 10, boxHeight: 10, font: { family: HC.MONO, size: 11 }, color: t.ink, usePointStyle: true },
      },
      tooltip: {
        backgroundColor: 'rgba(26,26,46,.92)', titleFont: { family: HC.MONO, size: 11 },
        bodyFont: { family: HC.MONO, size: 11 }, padding: 8, cornerRadius: 6, displayColors: true,
      },
    },
    scales: { x: deep({}, axis), y: deep({}, axis) },
    elements: { point: { radius: 3, hoverRadius: 5 }, line: { borderWidth: 2, tension: 0 } },
  };
  const cfg = { type, data, options: deep(defaults, opts) };
  // canvas 不認得 var(--x)：傳進去會靜默變成黑色（第 6 章五條準則線全黑就是這樣）。
  // 這裡在建構前把所有顏色欄位解析成實際色值，讓這類 bug 不可能發生。
  HC._resolveColors(cfg);
  return cfg;
};

HC._COLOR_KEYS = ['borderColor', 'backgroundColor', 'pointBackgroundColor',
                  'pointBorderColor', 'hoverBackgroundColor', 'hoverBorderColor', 'color'];
HC._resolveColors = o => {
  if (!o || typeof o !== 'object') return o;
  if (Array.isArray(o)) { o.forEach(HC._resolveColors); return o; }
  for (const k of Object.keys(o)) {
    const v = o[k];
    if (typeof v === 'string' && HC._COLOR_KEYS.indexOf(k) >= 0) o[k] = HC.color(v);
    else if (Array.isArray(v) && HC._COLOR_KEYS.indexOf(k) >= 0) {
      o[k] = v.map(x => (typeof x === 'string' ? HC.color(x) : x));
    } else if (v && typeof v === 'object') HC._resolveColors(v);
  }
  return o;
};

/* 建立或更新（同一個 canvas id 重複呼叫不會洩漏 chart instance） */
HC.chart = (canvasId, type, data, opts) => {
  if (!HC.hasChart()) return null;
  const cv = $(canvasId);
  if (!cv) { console.error('HC.chart: 找不到 canvas #' + canvasId); return null; }
  const old = HC._charts.get(canvasId);
  if (old) old.destroy();
  const c = new window.Chart(cv, HC.base(type, data, opts));
  HC._charts.set(canvasId, c);
  const wrap = cv.closest('.chart-wrap');
  if (wrap) wrap.classList.add('ready');
  return c;
};
HC.line = (id, data, opts) => HC.chart(id, 'line', data, opts);
HC.scatter = (id, data, opts) => HC.chart(id, 'scatter', data, opts);
HC.bar = (id, data, opts) => HC.chart(id, 'bar', data, opts);
HC.get = id => HC._charts.get(id);

/* 就地改資料再重畫，不重建 chart（滑桿連續拖動時比較順） */
HC.update = (id, mutate) => {
  const c = HC._charts.get(id);
  if (!c) return null;
  mutate(c);
  c.update('none');
  return c;
};

/* ---------- 參考線與陰影帶：一個全域註冊的 plugin ----------
   為什麼不是「每張圖各自帶 inline plugin」：Chart.js 4 的 Config.prototype.plugins
   只有 getter、沒有 setter，所以建構之後寫 `chart.config.plugins = [...]`
   會**靜默失效**（非嚴格模式下不報錯，畫面上就是什麼都沒有）。
   實測：Object.getOwnPropertyDescriptor(proto,'plugins') → {get: fn, set: undefined}。

   正確做法是註冊一個全域 plugin，參數放在 options.plugins.hcRef，每次繪製都重讀。
   HC.hline / HC.vline / HC.vband 因此改成只回傳「標記資料」，不再是 plugin 物件。 */


/* row：多條參考線靠得很近時把標籤往下錯開一列，避免疊字 */
HC.hline = (y, label, color, row) => ({ t: 'h', y: y, label: label, color: color, row: row || 0 });
HC.vline = (x, label, color, row) => ({ t: 'v', x: x, label: label, color: color, row: row || 0 });
HC.vband = (x0, x1, fill, label) => ({ t: 'band', x0: x0, x1: x1, fill: fill, label: label });

HC._refPlugin = {
  id: 'hcRef',
  beforeDatasetsDraw(chart) {
    const marks = chart.$hcRef || [];
    const { ctx, chartArea: ca, scales } = chart;
    marks.filter(m => m && m.t === 'band').forEach(m => {
      if (!scales.x) return;
      const a = scales.x.getPixelForValue(m.x0), b = scales.x.getPixelForValue(m.x1);
      ctx.save();
      ctx.fillStyle = HC.color(m.fill) || 'rgba(44,62,122,.10)';
      ctx.fillRect(Math.min(a, b), ca.top, Math.abs(b - a), ca.bottom - ca.top);
      if (m.label) {
        ctx.font = '600 10px ' + HC.MONO; ctx.fillStyle = HC.tok.muted;
        ctx.textAlign = 'center'; ctx.textBaseline = 'top';
        ctx.fillText(m.label, (a + b) / 2, ca.top + 2);
      }
      ctx.restore();
    });
  },
  afterDatasetsDraw(chart) {
    const marks = chart.$hcRef || [];
    const { ctx, chartArea: ca, scales } = chart;
    marks.forEach(m => {
      if (!m || m.t === 'band') return;
      const vert = m.t === 'v';
      const sc = vert ? scales.x : scales.y;
      if (!sc) return;
      const p = sc.getPixelForValue(vert ? m.x : m.y);
      if (!isFinite(p)) return;
      if (vert ? (p < ca.left - 1 || p > ca.right + 1) : (p < ca.top - 1 || p > ca.bottom + 1)) return;
      const col = HC.color(m.color) || (vert ? HC.tok.accent : HC.tok.muted);
      ctx.save();
      ctx.strokeStyle = col;
      ctx.lineWidth = vert ? 1.6 : 1.4;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      if (vert) { ctx.moveTo(p, ca.top); ctx.lineTo(p, ca.bottom); }
      else { ctx.moveTo(ca.left, p); ctx.lineTo(ca.right, p); }
      ctx.stroke();
      if (m.label) {
        ctx.setLineDash([]); ctx.font = '600 10px ' + HC.MONO; ctx.fillStyle = col;
        if (vert) {
          // 靠右邊界的標籤改成向左對齊，才不會被裁掉
          const near = p > ca.right - 90;
          ctx.textAlign = near ? 'right' : 'left'; ctx.textBaseline = 'top';
          ctx.fillText(m.label, p + (near ? -4 : 4), ca.top + 2 + (m.row || 0) * 13);
        } else {
          ctx.textAlign = 'right'; ctx.textBaseline = 'bottom';
          ctx.fillText(m.label, ca.right - 4, p - 3 - (m.row || 0) * 13);
        }
      }
      ctx.restore();
    });
  },
};

/* 設定某張圖的參考線。markers 可以是單一標記或陣列。

   markers 存在 chart 實例上（chart.$hcRef），**不放進 options.plugins**：
   Chart.js 4.5.1 會對 plugin options 走一輪 key 解析，把 marker 陣列丟進去會讓它
   在內部對非字串的 key 呼叫 .startsWith 而爆掉。全域註冊的 plugin 不需要 options
   就會啟用，所以直接掛在實例上最單純也最不容易壞。 */
HC.refs = (idOrChart, markers) => {
  const c = typeof idOrChart === 'string' ? HC.get(idOrChart) : idOrChart;
  if (!c) return null;
  c.$hcRef = Array.isArray(markers) ? markers : (markers ? [markers] : []);
  c.update('none');
  return c;
};

/* ============================================================
   HC.svg：手寫 SVG 元件的座標尺度與繪圖捷徑
   用法：const s = HC.svg('w03dragSvg', {xd:[0,10], yd:[0,30]});
        s.grid(5,5); s.dot(x, y, {cls:'dot', fill:HC.tok.train});
   ============================================================ */
const NS = 'http://www.w3.org/2000/svg';

HC.svg = (id, o = {}) => {
  const host = $(id);
  if (!host) { console.error('HC.svg: 找不到 #' + id); return null; }
  const W = o.w || 620, H = o.h || 340;
  const pad = Object.assign({ l: 46, r: 14, t: 14, b: 34 }, o.pad || {});
  let el = host;
  if (host.tagName.toLowerCase() !== 'svg') {
    el = host.querySelector('svg');
    if (!el) { el = document.createElementNS(NS, 'svg'); el.setAttribute('class', 'viz-svg'); host.appendChild(el); }
  }
  el.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  el.setAttribute('preserveAspectRatio', 'xMidYMid meet');
  if (!el.getAttribute('height')) el.setAttribute('height', String(H));

  const s = {
    el, W, H, pad,
    xd: (o.xd || [0, 1]).slice(), yd: (o.yd || [0, 1]).slice(),
    get iw() { return W - pad.l - pad.r; },
    get ih() { return H - pad.t - pad.b; },
  };
  s.domain = (xd, yd) => { if (xd) s.xd = xd.slice(); if (yd) s.yd = yd.slice(); return s; };
  s.X = v => pad.l + (v - s.xd[0]) / (s.xd[1] - s.xd[0]) * s.iw;
  s.Y = v => pad.t + s.ih - (v - s.yd[0]) / (s.yd[1] - s.yd[0]) * s.ih;
  s.ix = px => s.xd[0] + (px - pad.l) / s.iw * (s.xd[1] - s.xd[0]);
  s.iy = py => s.yd[0] + (pad.t + s.ih - py) / s.ih * (s.yd[1] - s.yd[0]);

  /* client 座標 → viewBox 座標（縮放與 CSS 尺寸都會被吸收） */
  s.toView = ev => {
    const r = el.getBoundingClientRect();
    const cx = ev.clientX !== undefined ? ev.clientX : (ev.touches && ev.touches[0].clientX);
    const cy = ev.clientY !== undefined ? ev.clientY : (ev.touches && ev.touches[0].clientY);
    return { px: (cx - r.left) / r.width * W, py: (cy - r.top) / r.height * H };
  };
  s.toData = ev => { const p = s.toView(ev); return { x: s.ix(p.px), y: s.iy(p.py) }; };

  s.add = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k of Object.keys(attrs)) {
      if (attrs[k] === null || attrs[k] === undefined) continue;
      n.setAttribute(k === 'cls' ? 'class' : k, String(attrs[k]));
    }
    (parent || el).appendChild(n);
    return n;
  };
  /* 分層：只清掉自己那層，底圖不用重畫 */
  s.layer = name => {
    let g = el.querySelector('g[data-layer="' + name + '"]');
    if (!g) { g = s.add('g', { 'data-layer': name }); }
    return g;
  };
  s.clearLayer = name => { const g = s.layer(name); while (g.firstChild) g.removeChild(g.firstChild); return g; };
  s.clear = () => { while (el.firstChild) el.removeChild(el.firstChild); return s; };

  /* 座標軸 + 格線 + 刻度標籤 */
  s.grid = (nx = 5, ny = 5, opt = {}) => {
    const g = s.clearLayer('grid');
    const fx = opt.xfmt || (v => HC.fmt(v, opt.xdec ?? 0));
    const fy = opt.yfmt || (v => HC.fmt(v, opt.ydec ?? 0));
    for (let i = 0; i <= nx; i++) {
      const v = s.xd[0] + (s.xd[1] - s.xd[0]) * i / nx, x = s.X(v);
      s.add('line', { cls: 'gridl', x1: x, y1: pad.t, x2: x, y2: pad.t + s.ih }, g);
      s.add('text', { cls: 'axlab', x: x, y: pad.t + s.ih + 14, 'text-anchor': 'middle' }, g).textContent = fx(v);
    }
    for (let i = 0; i <= ny; i++) {
      const v = s.yd[0] + (s.yd[1] - s.yd[0]) * i / ny, y = s.Y(v);
      s.add('line', { cls: 'gridl', x1: pad.l, y1: y, x2: pad.l + s.iw, y2: y }, g);
      s.add('text', { cls: 'axlab', x: pad.l - 6, y: y + 3.5, 'text-anchor': 'end' }, g).textContent = fy(v);
    }
    s.add('line', { cls: 'ax', x1: pad.l, y1: pad.t + s.ih, x2: pad.l + s.iw, y2: pad.t + s.ih }, g);
    s.add('line', { cls: 'ax', x1: pad.l, y1: pad.t, x2: pad.l, y2: pad.t + s.ih }, g);
    if (opt.xtitle) s.add('text', { cls: 'axtitle', x: pad.l + s.iw / 2, y: H - 4, 'text-anchor': 'middle' }, g).textContent = opt.xtitle;
    if (opt.ytitle) {
      const t = s.add('text', { cls: 'axtitle', x: 0, y: 0, 'text-anchor': 'middle', transform: 'translate(11,' + (pad.t + s.ih / 2) + ') rotate(-90)' }, g);
      t.textContent = opt.ytitle;
    }
    return s;
  };

  s.dot = (x, y, a = {}, parent) => s.add('circle', {
    cls: a.cls || 'dot', cx: s.X(x), cy: s.Y(y), r: a.r ?? 4,
    fill: a.fill || HC.tok.accent2, stroke: a.stroke, 'stroke-width': a.sw,
    opacity: a.opacity, 'data-i': a.i,
  }, parent);

  s.poly = (pts, a = {}, parent) => s.add('polyline', {
    cls: a.cls || 'fit', points: pts.map(p => s.X(p[0]) + ',' + s.Y(p[1])).join(' '),
    stroke: a.stroke, 'stroke-width': a.sw, fill: 'none', 'stroke-dasharray': a.dash,
  }, parent);

  s.area = (pts, a = {}, parent) => {
    const up = pts.map(p => s.X(p[0]) + ',' + s.Y(p[1]));
    const dn = pts.slice().reverse().map(p => s.X(p[0]) + ',' + s.Y(p[2]));
    return s.add('polygon', { cls: a.cls || 'band', points: up.concat(dn).join(' '), fill: a.fill }, parent);
  };

  s.seg = (x1, y1, x2, y2, a = {}, parent) => s.add('line', {
    cls: a.cls || 'resid', x1: s.X(x1), y1: s.Y(y1), x2: s.X(x2), y2: s.Y(y2),
    stroke: a.stroke, 'stroke-width': a.sw, 'stroke-dasharray': a.dash,
  }, parent);

  s.box = (x0, y0, x1, y1, a = {}, parent) => s.add('rect', {
    x: Math.min(s.X(x0), s.X(x1)), y: Math.min(s.Y(y0), s.Y(y1)),
    width: Math.abs(s.X(x1) - s.X(x0)), height: Math.abs(s.Y(y1) - s.Y(y0)),
    fill: a.fill || 'none', stroke: a.stroke, 'stroke-width': a.sw, cls: a.cls, rx: a.rx,
  }, parent);

  s.txt = (x, y, str, a = {}, parent) => {
    const n = s.add('text', {
      cls: a.cls || 'vlab', x: s.X(x) + (a.dx || 0), y: s.Y(y) + (a.dy || 0),
      'text-anchor': a.anchor || 'middle', fill: a.fill,
    }, parent);
    n.textContent = str;
    return n;
  };
  /* 用 viewBox 像素座標直接放字（圖例、標題用） */
  s.txtPx = (px, py, str, a = {}, parent) => {
    const n = s.add('text', { cls: a.cls || 'axlab', x: px, y: py, 'text-anchor': a.anchor || 'start', fill: a.fill }, parent);
    n.textContent = str;
    return n;
  };
  return s;
};

/* 拖曳：pointer + touch，回呼收到資料座標；會夾在定義域內 */
HC.drag = (node, svc, onMove, opts = {}) => {
  const clampX = x => Math.max(svc.xd[0], Math.min(svc.xd[1], x));
  const clampY = y => Math.max(svc.yd[0], Math.min(svc.yd[1], y));
  let active = false;
  const start = ev => {
    active = true; node.setAttribute('data-dragging', '1');
    if (node.setPointerCapture && ev.pointerId !== undefined) node.setPointerCapture(ev.pointerId);
    ev.preventDefault();
  };
  const move = ev => {
    if (!active) return;
    const d = svc.toData(ev);
    onMove({ x: opts.lockX ? null : clampX(d.x), y: opts.lockY ? null : clampY(d.y) });
    ev.preventDefault();
  };
  const end = () => { active = false; node.removeAttribute('data-dragging'); };
  node.addEventListener('pointerdown', start);
  node.addEventListener('pointermove', move);
  node.addEventListener('pointerup', end);
  node.addEventListener('pointercancel', end);
  node.style.touchAction = 'none';
  return () => {
    node.removeEventListener('pointerdown', start);
    node.removeEventListener('pointermove', move);
    node.removeEventListener('pointerup', end);
    node.removeEventListener('pointercancel', end);
  };
};

/* ---------- 統計小工具（各頁元件共用，避免各自重寫） ---------- */
HC.stat = {
  mean: a => a.reduce((s, v) => s + v, 0) / a.length,
  variance(a) { const m = this.mean(a); return a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1); },
  sd(a) { return Math.sqrt(this.variance(a)); },
  /* 簡單線性迴歸：回傳 b0, b1, rss, tss, r2, se(b0), se(b1), t 值 */
  ols(xs, ys) {
    const n = xs.length, mx = this.mean(xs), my = this.mean(ys);
    let sxx = 0, sxy = 0;
    for (let i = 0; i < n; i++) { sxx += (xs[i] - mx) ** 2; sxy += (xs[i] - mx) * (ys[i] - my); }
    const b1 = sxx === 0 ? 0 : sxy / sxx, b0 = my - b1 * mx;
    let rss = 0, tss = 0;
    for (let i = 0; i < n; i++) { rss += (ys[i] - b0 - b1 * xs[i]) ** 2; tss += (ys[i] - my) ** 2; }
    const df = n - 2;
    const s2 = df > 0 ? rss / df : NaN;
    const seB1 = sxx > 0 ? Math.sqrt(s2 / sxx) : NaN;
    const seB0 = Math.sqrt(s2 * (1 / n + mx * mx / sxx));
    return {
      b0, b1, rss, tss, n, df, rse: Math.sqrt(s2),
      r2: tss === 0 ? NaN : 1 - rss / tss,
      seB0, seB1, tB0: b0 / seB0, tB1: b1 / seB1,
    };
  },
  /* RSS(b0,b1)，畫誤差曲面用 */
  rss(xs, ys, b0, b1) {
    let r = 0;
    for (let i = 0; i < xs.length; i++) r += (ys[i] - b0 - b1 * xs[i]) ** 2;
    return r;
  },
  /* 可重現的偽隨機（固定種子，頁面重載結果一樣） */
  lcg(seed) { let s = (seed >>> 0) || 1; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; },
  /* Box–Muller 標準常態 */
  normal(rand) {
    let u = 0, v = 0;
    while (u === 0) u = rand();
    while (v === 0) v = rand();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  },
  /* 標準常態 CDF（Abramowitz–Stegun 7.1.26 誤差函數近似） */
  pnorm(z) {
    const t = 1 / (1 + 0.2316419 * Math.abs(z));
    const p = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
    const d = Math.exp(-z * z / 2) / Math.sqrt(2 * Math.PI);
    return z >= 0 ? 1 - d * p : d * p;
  },
  dnorm(x, mu = 0, sd = 1) { const z = (x - mu) / sd; return Math.exp(-z * z / 2) / (sd * Math.sqrt(2 * Math.PI)); },
  quantile(sorted, q) {
    const h = (sorted.length - 1) * q, lo = Math.floor(h);
    return sorted[lo] + (h - lo) * ((sorted[Math.min(lo + 1, sorted.length - 1)]) - sorted[lo]);
  },
  seq(a, b, n) { return Array.from({ length: n }, (_, i) => a + (b - a) * i / (n - 1)); },
};

/* ============================================================
   頁面骨架行為
   ============================================================ */

/* 浮動導覽 scroll-spy */
(function setupNav() {
  const nav = $('floatNav');
  if (!nav) return;
  const links = Array.from(nav.querySelectorAll('a[data-target]'));
  const sections = links.map(a => $(a.dataset.target)).filter(Boolean);
  const missing = links.filter(a => !$(a.dataset.target)).map(a => a.dataset.target);
  if (missing.length) console.warn('float-nav 的 data-target 找不到對應 section：', missing);
  function update() {
    const y = window.scrollY + window.innerHeight * 0.3;
    let active = sections[0] && sections[0].id;
    for (const s of sections) if (s.offsetTop <= y) active = s.id;
    links.forEach(a => {
      const on = a.dataset.target === active;
      a.classList.toggle('active', on);
      if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
  }
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update, { passive: true });
  update();
})();

/* 觀念 Q&A：MathJax CHTML 在 display:none 下會量錯字寬，首次展開時重排一次 */
document.addEventListener('toggle', e => {
  const d = e.target;
  if (d.tagName !== 'DETAILS' || !d.open || d.dataset.mj) return;
  d.dataset.mj = '1';
  HC.retype(d);
}, true);

/* 詞彙卡（FLASHCARDS 由 tools/inject_data.py 注入在本檔之後） */
HC.initFlashcards = () => {
  const grid = $('fcGrid');
  if (!grid || typeof FLASHCARDS === 'undefined') return;
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const render = cards => {
    grid.innerHTML = cards.map(c =>
      '<div class="fc-card"><div class="fc-inner">'
      + '<div class="fc-face fc-front"><div>' + esc(c.front) + '</div><div class="fc-hint">CLICK TO FLIP</div></div>'
      + '<div class="fc-face fc-back">' + esc(c.back) + '</div>'
      + '</div></div>').join('');
  };
  render(FLASHCARDS);
  grid.addEventListener('click', e => {
    const card = e.target.closest('.fc-card');
    if (card) card.classList.toggle('flipped');
  });
  const on = (id, fn) => { const b = $(id); if (b) b.addEventListener('click', fn); };
  /* 洗牌用固定種子的 Fisher–Yates，每按一次換一個種子 */
  let shuffleSeed = 20260810;
  on('fcShuffle', () => {
    const rand = HC.stat.lcg(shuffleSeed++);
    const a = FLASHCARDS.slice();
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    render(a);
  });
  on('fcUnflip', () => grid.querySelectorAll('.fc-card').forEach(c => c.classList.remove('flipped')));
  on('fcFlipAll', () => grid.querySelectorAll('.fc-card').forEach(c => c.classList.add('flipped')));
};
