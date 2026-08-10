/* ============ shared utilities ============ */
const $ = id => document.getElementById(id);

function quizCheck(quizId, optEl) {
  const isCorrect = optEl.dataset.correct === 'true';
  optEl.parentElement.querySelectorAll('.quiz-opt').forEach(o => o.classList.remove('correct','wrong'));
  optEl.classList.add(isCorrect ? 'correct' : 'wrong');
  const fb = $(quizId + 'Feedback');
  fb.classList.remove('correct','wrong');
  fb.classList.add('show', isCorrect ? 'correct' : 'wrong');
  fb.innerHTML = (isCorrect ? '<strong>正確 ✓</strong> ' : '<strong>不對 ✗</strong> ') + (optEl.dataset.fb || '');
}

function hlLine(rootId, n) {
  const root = $(rootId);
  if (!root) return;
  root.querySelectorAll('.line').forEach(l => l.classList.remove('active'));
  if (n != null) {
    const line = root.querySelector(`.line[data-l="${n}"]`);
    if (line) line.classList.add('active');
  }
}

/* step player: frames = [{...}], apply(frame) renders */
class Player {
  constructor({frames, apply, delayInput, onDone}) {
    this.frames = frames; this.apply = apply;
    this.delayInput = delayInput; this.i = -1; this.timer = null;
    this.onDone = onDone || (()=>{});
  }
  step() {
    if (this.i + 1 >= this.frames.length) { this.stop(); this.onDone(); return; }
    this.i += 1; this.apply(this.frames[this.i]);
  }
  play() {
    this.stop();
    const tick = () => {
      if (this.i + 1 >= this.frames.length) { this.stop(); this.onDone(); return; }
      this.step();
      this.timer = setTimeout(tick, this.delayInput ? parseInt(this.delayInput.value,10) : 700);
    };
    tick();
  }
  stop() { if (this.timer) { clearTimeout(this.timer); this.timer = null; } }
  reset() { this.stop(); this.i = -1; if (this.frames.length) this.apply(this.frames[0]); }
}

function setStatus(id, html) {
  const el = $(id); if (el) el.querySelector('.status-text').innerHTML = html;
}

/* vertical box stack renderer (DOM) */
function renderBoxStack(containerId, items, opts={}) {
  const el = $(containerId); if (!el) return;
  const hl = opts.highlight ?? -1;   // index from top (0 = top)
  el.innerHTML = '';
  const label = document.createElement('div');
  label.className = 'bs-toplabel';
  label.textContent = items.length ? 'top ↓' : '(empty)';
  el.appendChild(label);
  items.slice().reverse().forEach((v, idx) => {
    const d = document.createElement('div');
    d.className = 'bs-item' + (idx === hl ? ' bs-hl' : '');
    d.textContent = v;
    el.appendChild(d);
  });
}

/* horizontal queue renderer: front at left */
function renderBoxQueue(containerId, items, opts={}) {
  const el = $(containerId); if (!el) return;
  el.innerHTML = '';
  const front = document.createElement('div');
  front.className = 'bq-label'; front.textContent = items.length ? 'front →' : '(empty)';
  el.appendChild(front);
  items.forEach((v, idx) => {
    const d = document.createElement('div');
    d.className = 'bq-item' + (idx === (opts.highlight ?? -1) ? ' bs-hl' : '');
    d.textContent = v;
    el.appendChild(d);
  });
  const rear = document.createElement('div');
  rear.className = 'bq-label'; rear.textContent = items.length ? '← rear' : '';
  el.appendChild(rear);
}

/* floating nav scroll spy */
(function setupNav() {
  const nav = $('floatNav');
  const links = nav.querySelectorAll('a[data-target]');
  const sections = Array.from(links).map(a => document.getElementById(a.dataset.target)).filter(Boolean);
  function update() {
    const y = window.scrollY + window.innerHeight * 0.3;
    let active = sections[0]?.id;
    for (const s of sections) if (s.offsetTop <= y) active = s.id;
    links.forEach(a => a.classList.toggle('active', a.dataset.target === active));
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
})();


/* ---------- P00 intro ---------- */
let introS = [], introQ = [];
function introRender(msg) {
  renderBoxStack('introStack', introS);
  renderBoxQueue('introQueue', introQ);
  if (msg) setStatus('introStatus', msg);
}
function introDemo(mode) {
  if (mode === 'push') {
    introS = []; introQ = [];
    const vals = [4, 7, 2]; let i = 0;
    const t = setInterval(() => {
      if (i >= vals.length) { clearInterval(t); introRender('放入順序都是 4 → 7 → 2。現在按「全部取出」。'); return; }
      introS.push(vals[i]); introQ.push(vals[i]); i++; introRender(`放入 ${vals[i-1]}`);
    }, 500);
  } else if (mode === 'pop') {
    const outS = [], outQ = [];
    const t = setInterval(() => {
      let moved = false;
      if (introS.length) { outS.push(introS.pop()); moved = true; }
      if (introQ.length) { outQ.push(introQ.shift()); moved = true; }
      introRender(`stack 取出：${outS.join(' ')}　|　queue 取出：${outQ.join(' ')}`);
      if (!moved) { clearInterval(t);
        setStatus('introStatus', `<strong>stack 取出 2 7 4（反轉！）；queue 取出 4 7 2（保序）。</strong>這就是 LIFO 與 FIFO 的全部差別。`); }
    }, 600);
  } else { introS = []; introQ = []; introRender('已重置。'); }
}
introRender();

/* ---------- P01 stack ---------- */
let stackItems = [4, 'dog', true];
function stackRender(msg, hl=-1) { renderBoxStack('stackVis', stackItems, {highlight: hl}); if (msg) setStatus('stackStatus', msg); }
function stackPush() {
  const v = $('stackInput').value.trim() || '?';
  stackItems.push(v); stackRender(`push(${v}) → 新 top = ${v}`, 0);
}
function stackPop() {
  if (!stackItems.length) { stackRender('stack 是空的：真實程式這裡要先檢查 is_empty()！'); return; }
  const v = stackItems.pop(); stackRender(`pop() 回傳 ${v}`);
}
function stackPeek() {
  if (!stackItems.length) { stackRender('空 stack 沒有 top。'); return; }
  stackRender(`peek() = ${stackItems[stackItems.length-1]}（只看不拿）`, 0);
}
function stackReset() { stackItems = [4, 'dog', true]; stackRender('已重置為 [4, dog, true]。'); }
stackRender();

/* Stack vs Stack2: count element moves for n pushes + n pops */
function s2Race() {
  const n = parseInt($('s2N').value, 10);
  const s1 = 0;                       // append/pop() never shift others
  let s2 = 0;
  for (let i = 0; i < n; i++) s2 += i;   // push #i shifts i elements
  for (let i = n - 1; i >= 0; i--) s2 += i;  // pop shifts the rest
  $('s2Out').innerHTML =
    `Stack（top 在尾端）：搬移 <strong>${s1}</strong> 個元素<br>` +
    `Stack2（top 在前端）：搬移 <strong>${s2.toLocaleString()}</strong> 個元素（約 n²）`;
  setStatus('s2Status', `n = ${n}：同樣的介面、同樣的答案，工作量差了 ${s2 === 0 ? 0 : s2.toLocaleString()} 倍不止。第 2 章會把這件事寫成 O(1) 對 O(n)。`);
}

/* ---------- P02 parens ---------- */
let parPlayer = null;
const OPENS = '([{', CLOSES = ')]}';
const MATCH = { ')':'(', ']':'[', '}':'{' };
function parFrames(s) {
  const frames = [{stack:[], i:-1, cls:{}, msg:'開始掃描。', line:1}];
  const st = [];
  const cls = {};
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (OPENS.includes(c)) {
      st.push(c); cls[i]='done';
      frames.push({stack:[...st], i, cls:{...cls}, msg:`'${c}' 是開符號 → push`, line:5});
    } else if (CLOSES.includes(c)) {
      if (!st.length) { cls[i]='bad';
        frames.push({stack:[], i, cls:{...cls}, msg:`'${c}' 來了但 stack 是空的 → <strong>不平衡 ✗</strong>`, line:7, fail:true});
        return frames; }
      const top = st.pop();
      if (top !== MATCH[c]) { cls[i]='bad';
        frames.push({stack:[...st], i, cls:{...cls}, msg:`pop 出 '${top}' 但要配 '${c}' → 種類不合 → <strong>不平衡 ✗</strong>`, line:8, fail:true});
        return frames; }
      cls[i]='done';
      frames.push({stack:[...st], i, cls:{...cls}, msg:`'${c}' 與 pop 出的 '${top}' 配對成功`, line:8});
    } else {
      cls[i]='done';
      frames.push({stack:[...st], i, cls:{...cls}, msg:`忽略非括號字元 '${c}'`, line:3});
    }
  }
  const ok = st.length === 0;
  frames.push({stack:[...st], i:s.length, cls, line:9,
    msg: ok ? '<strong>掃描完成且 stack 空 → 平衡 ✓</strong>'
            : `<strong>掃描完成但 stack 還有 ${st.length} 個開符號 → 不平衡 ✗</strong>`});
  return frames;
}
function parApply(f) {
  const s = $('parInput').value;
  const strip = $('parStrip'); strip.innerHTML = '';
  for (let i = 0; i < s.length; i++) {
    const d = document.createElement('div');
    d.className = 'char-cell' + (i === f.i ? ' char-cur' : (f.cls[i] ? ' char-' + f.cls[i] : ''));
    d.textContent = s[i]; strip.appendChild(d);
  }
  renderBoxStack('parStack', f.stack);
  setStatus('parStatus', f.msg); hlLine('parCode', f.line);
}
function parStart() {
  parPlayer = new Player({frames: parFrames($('parInput').value), apply: parApply});
  parPlayer.reset(); parPlayer.play();
}
function parLoad(s) { $('parInput').value = s; parStart(); }

/* ---------- P03 base ---------- */
let basePlayer = null;
function baseFrames(n0, base) {
  const digits = '0123456789ABCDEF';
  const frames = [{trace:[], stack:[], out:'', msg:`把 ${n0} 轉成 base ${base}。`, line:1}];
  let n = n0; const st = []; const tr = [];
  while (n > 0) {
    const rem = n % base; const q = Math.floor(n / base);
    st.push(digits[rem]); tr.push(`${n} ÷ ${base} = ${q} … 餘 <strong>${digits[rem]}</strong>`);
    frames.push({trace:[...tr], stack:[...st], out:'', msg:`餘數 ${digits[rem]} push 進 stack`, line:5});
    n = q;
    frames.push({trace:[...tr], stack:[...st], out:'', msg:`商變成 ${n}`, line:6});
  }
  let out = '';
  const st2 = [...st];
  while (st2.length) {
    out += st2.pop();
    frames.push({trace:tr, stack:[...st2], out, msg:`pop → 目前結果 "${out}"`, line:9});
  }
  frames.push({trace:tr, stack:[], out, msg:`<strong>${n0} (base 10) = ${out} (base ${base}) ✓</strong>`, line:10});
  return frames;
}
function baseApply(f) {
  $('baseTrace').innerHTML = f.trace.join('<br>') + (f.out ? `<br>結果：<strong>${f.out}</strong>` : '');
  renderBoxStack('baseStack', f.stack);
  setStatus('baseStatus', f.msg); hlLine('baseCode', f.line);
}
function baseStart() {
  const n = Math.max(1, parseInt($('baseInput').value || '233', 10));
  const b = parseInt($('baseSel').value, 10);
  basePlayer = new Player({frames: baseFrames(n, b), apply: baseApply});
  basePlayer.reset(); basePlayer.play();
}

/* ---------- P04 infix→postfix ---------- */
let i2pPlayer = null, pevalPlayer = null;
const PREC = {'^':4, '*':3, '/':3, '+':2, '-':2, '(':1};
function i2pFrames(expr) {
  const tokens = expr.split(/\s+/);
  const frames = [{i:-1, stack:[], out:[], msg:'開始逐 token 掃描。', line:1}];
  const st = [], out = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (/^[A-Za-z0-9]+$/.test(t)) {
      out.push(t);
      frames.push({i, stack:[...st], out:[...out], msg:`運算元 ${t} 直接輸出`, line:5});
    } else if (t === '(') {
      st.push(t);
      frames.push({i, stack:[...st], out:[...out], msg:`'(' push 進 opStack`, line:7});
    } else if (t === ')') {
      while (st.length && st[st.length-1] !== '(') {
        out.push(st.pop());
        frames.push({i, stack:[...st], out:[...out], msg:`')' → pop 輸出 ${out[out.length-1]}`, line:9});
      }
      st.pop();
      frames.push({i, stack:[...st], out:[...out], msg:`丟棄 '('`, line:9});
    } else {
      while (st.length && PREC[st[st.length-1]] >= PREC[t] && !(t === '^' && st[st.length-1] === '^')) {
        out.push(st.pop());
        frames.push({i, stack:[...st], out:[...out], msg:`stack 頂 ${out[out.length-1]} 優先權 ≥ ${t} → 先輸出`, line:11});
      }
      st.push(t);
      frames.push({i, stack:[...st], out:[...out], msg:`${t} push 進 opStack`, line:12});
    }
  }
  while (st.length) {
    out.push(st.pop());
    frames.push({i:tokens.length, stack:[...st], out:[...out], msg:`收尾：pop 輸出 ${out[out.length-1]}`, line:11});
  }
  frames.push({i:tokens.length, stack:[], out, msg:`<strong>後序：${out.join(' ')} ✓</strong>`, line:12});
  return frames;
}
function tokenStrip(id, tokens, cur) {
  const strip = $(id); strip.innerHTML = '';
  tokens.forEach((t, i) => {
    const d = document.createElement('div');
    d.className = 'char-cell' + (i === cur ? ' char-cur' : (i < cur ? ' char-done' : ''));
    d.textContent = t; strip.appendChild(d);
  });
}
function i2pApply(f) {
  tokenStrip('i2pStrip', $('i2pSel').value.split(/\s+/), f.i);
  renderBoxStack('i2pStack', f.stack);
  const out = $('i2pOut'); out.innerHTML = '';
  f.out.forEach((t, k) => {
    const d = document.createElement('div');
    d.className = 'tok' + (/[+\-*\/^]/.test(t) && t.length === 1 ? ' tok-op' : '') + (k === f.out.length-1 ? ' tok-new' : '');
    d.textContent = t; out.appendChild(d);
  });
  setStatus('i2pStatus', f.msg); hlLine('i2pCode', f.line);
}
function i2pStart() {
  i2pPlayer = new Player({frames: i2pFrames($('i2pSel').value), apply: i2pApply});
  i2pPlayer.reset(); i2pPlayer.play();
}
function pevalFrames() {
  const tokens = '7 8 + 3 2 + /'.split(' ');
  const frames = [{i:-1, stack:[], msg:'後序求值開始。', line:1}];
  const st = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (/^\d+$/.test(t)) {
      st.push(parseInt(t,10));
      frames.push({i, stack:[...st], msg:`數字 ${t} push`, line:5});
    } else {
      const r = st.pop(), l = st.pop();
      const v = t==='+'? l+r : t==='-'? l-r : t==='*'? l*r : Math.floor(l/r);
      st.push(v);
      frames.push({i, stack:[...st], msg:`pop 出 right=${r}、left=${l} → ${l} ${t} ${r} = ${v}，push 回去`, line:8});
    }
  }
  frames.push({i:tokens.length, stack:st, msg:`<strong>答案 = ${st[0]}（注意 15/5=3：pop 順序 right 先！）</strong>`, line:9});
  return frames;
}
function pevalApply(f) {
  tokenStrip('pevalStrip', '7 8 + 3 2 + /'.split(' '), f.i);
  renderBoxStack('pevalStack', f.stack);
  setStatus('pevalStatus', f.msg); hlLine('pevalCode', f.line);
}
function pevalStart() {
  pevalPlayer = new Player({frames: pevalFrames(), apply: pevalApply});
  pevalPlayer.reset(); pevalPlayer.play();
}

/* ---------- P05 queue ---------- */
let queueItems = ['4', 'dog', 'true'];
function queueRender(msg, hl=-1) { renderBoxQueue('queueVis', queueItems, {highlight:hl}); if (msg) setStatus('queueStatus', msg); }
function queueEnq() {
  const v = $('queueInput').value.trim() || '?';
  queueItems.push(v); queueRender(`enqueue(${v}) → 排到 rear`, queueItems.length-1);
}
function queueDeq() {
  if (!queueItems.length) { queueRender('queue 是空的。'); return; }
  const v = queueItems.shift(); queueRender(`dequeue() 回傳 ${v}（front 先出）`);
}
function queueReset() { queueItems = ['4','dog','true']; queueRender('已重置。'); }
queueRender();

/* ---------- P06 hot potato ---------- */
let hpPlayer = null;
function hpFrames(names, num) {
  const frames = [{q:[...names], msg:`開始！queue = [${names.join(', ')}]`, line:3, out:null}];
  const q = [...names];
  while (q.length > 1) {
    for (let i = 0; i < num; i++) {
      q.push(q.shift());
      if (q.length <= 8 || i === num-1)
        frames.push({q:[...q], msg:`傳遞 ${i+1}/${num}：${q[q.length-1]} 傳完排到隊尾`, line:6, out:null});
    }
    const out = q.shift();
    frames.push({q:[...q], msg:`數到 ${num} → <strong style="color:var(--accent);">${out} 出局！</strong>`, line:7, out});
  }
  frames.push({q, msg:`<strong>倖存者：${q[0]} 🎉</strong>`, line:8, out:null});
  return frames;
}
function hpApply(f) {
  renderBoxQueue('hpVis', f.q);
  setStatus('hpStatus', f.msg); hlLine('hpCode', f.line);
}
function hpStart() {
  const names = ['Bill','David','Susan','Jane','Kent','Brad'];
  const num = Math.max(1, parseInt($('hpNum').value||'7',10));
  hpPlayer = new Player({frames: hpFrames(names, num), apply: hpApply, delayInput: $('hpSpeed')});
  hpPlayer.reset(); hpPlayer.play();
}

/* ---------- P07 printer ---------- */
function lcg(seed) { let s = seed >>> 0; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
function printerSim(ppm, seed) {
  const rand = lcg(seed);
  const q = []; let currentTask = null, remain = 0;
  const waits = [];
  const rate = ppm / 60; // pages per second
  for (let sec = 0; sec < 3600; sec++) {
    if (Math.floor(rand() * 180) === 0) q.push({born: sec, pages: 1 + Math.floor(rand()*20)});
    if (!currentTask && q.length) {
      currentTask = q.shift(); waits.push(sec - currentTask.born);
      remain = currentTask.pages;
    }
    if (currentTask) { remain -= rate; if (remain <= 0) currentTask = null; }
  }
  return waits.length ? waits.reduce((a,b)=>a+b,0) / waits.length : 0;
}
function printerRun() {
  const tb = $('printerTable').querySelector('tbody'); tb.innerHTML = '';
  let s5 = 0, s10 = 0;
  const RUNS = 10;
  for (let r = 0; r < RUNS; r++) {
    const w5 = printerSim(5, 42 + r), w10 = printerSim(10, 42 + r);
    s5 += w5; s10 += w10;
    tb.insertAdjacentHTML('beforeend',
      `<tr><td>${r+1}</td><td>${w5.toFixed(1)}</td><td>${w10.toFixed(1)}</td></tr>`);
  }
  tb.insertAdjacentHTML('beforeend',
    `<tr style="font-weight:700;background:var(--highlight);"><td>平均</td><td>${(s5/RUNS).toFixed(1)}</td><td>${(s10/RUNS).toFixed(1)}</td></tr>`);
  setStatus('printerStatus', `同一組工作到達序列下，10 頁/分的平均等待約為 5 頁/分的 ${(s5/s10).toFixed(1)} 分之一。`);
}

/* ---------- P08 deque / palindrome ---------- */
let palPlayer = null;
function palFrames(s) {
  const frames = [{dq:[...s], i:-1, j:s.length, msg:'字元全部 addRear 進 deque。', line:3, cls:{}}];
  let dq = [...s]; const cls = {};
  let li = 0, ri = s.length - 1;
  while (dq.length > 1) {
    const first = dq.shift(); const last = dq.pop();
    if (first !== last) {
      cls[li]='bad'; cls[ri]='bad';
      frames.push({dq:[...dq], msg:`removeFront '${first}' ≠ removeRear '${last}' → <strong>不是迴文 ✗</strong>`, line:8, cls:{...cls}});
      return frames;
    }
    cls[li]='done'; cls[ri]='done';
    frames.push({dq:[...dq], msg:`'${first}' == '${last}' ✓ 繼續往內`, line:7, cls:{...cls}});
    li++; ri--;
  }
  if (dq.length === 1) cls[li]='done';
  frames.push({dq, msg:'<strong>全部配對成功 → 是迴文 ✓</strong>', line:9, cls});
  return frames;
}
function palApply(f) {
  const s = $('palInput').value;
  const strip = $('palStrip'); strip.innerHTML = '';
  for (let i = 0; i < s.length; i++) {
    const d = document.createElement('div');
    d.className = 'char-cell' + (f.cls[i] ? ' char-' + f.cls[i] : '');
    d.textContent = s[i]; strip.appendChild(d);
  }
  renderBoxQueue('palVis', f.dq);
  setStatus('palStatus', f.msg); hlLine('palCode', f.line);
}
function palStart() {
  palPlayer = new Player({frames: palFrames($('palInput').value.trim()), apply: palApply});
  palPlayer.reset(); palPlayer.play();
}
