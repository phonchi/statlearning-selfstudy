/* 3D 統計學習知識群島。build_island.py 會把本檔 inline 進 island/index.html 的 <script type="module">。
 *
 * 分兩層：
 *   1. UI 層（不需要 Three.js）：章節列表、足跡（localStorage）、面板、鍵盤操作。
 *      CDN 失效、WebGL 不可用時頁面停在 2D 地圖，這一層照常運作。
 *   2. 場景層（island-scene.js 的 buildWorld）：WebGL 可用才以 dynamic import 載入 Three.js
 *      （importmap 釘版＋integrity），成功後才在 <body> 加 .webgl-ready，切成 3D＋側欄。
 * build_island.py 把本檔與 island-scene.js 依序 inline 進同一個 module，兩者共用頂層名稱。
 */
const DATA = JSON.parse(document.getElementById('island-data').textContent);
const PAGES = DATA.pages;
const BY = Object.fromEntries(PAGES.map(p => [p.stem, p]));
const ISLES = Object.fromEntries(DATA.isles.map(i => [i.grp, i]));
const $ = id => document.getElementById(id);
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let scene = null;   // 3D 場景成功啟動後才有值

/* ── 足跡：只存在這台裝置的瀏覽器。「造訪」＝從島上點過前往教材；「完成」＝學生自己標記 ── */
const TRAIL_KEY = 'slss-island:trail:v1';
const NIGHT_KEY = 'slss-island:night';
function loadTrail() {
  try {
    const t = JSON.parse(localStorage.getItem(TRAIL_KEY) || '{}');
    return { visited: t.visited || {}, done: t.done || {} };
  } catch (e) { return { visited: {}, done: {} }; }
}
let trail = loadTrail();
function saveTrail() {
  try { localStorage.setItem(TRAIL_KEY, JSON.stringify(trail)); } catch (e) { /* 私密視窗等情況：只在本頁有效 */ }
}
function markVisited(stem) {
  if (!BY[stem] || trail.visited[stem]) return;
  trail.visited[stem] = Date.now(); saveTrail(); refreshTrail();
}
function setDone(stem, on) {
  if (on) trail.done[stem] = Date.now(); else delete trail.done[stem];
  saveTrail(); refreshTrail();
}
window.addEventListener('storage', e => { if (e.key === TRAIL_KEY) { trail = loadTrail(); refreshTrail(); } });

/* ── 列表 ── */
const items = new Map();   // stem → { li, link, mark }
document.querySelectorAll('.isl-item').forEach(li => {
  const stem = li.dataset.stem, link = li.querySelector('.isl-link');
  const mark = document.createElement('button');
  mark.type = 'button'; mark.className = 'isl-mark'; mark.textContent = '✓';
  mark.addEventListener('click', () => setDone(stem, !trail.done[stem]));
  li.appendChild(mark);
  items.set(stem, { li, link, mark });
  link.addEventListener('click', e => {
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || !scene) {
      markVisited(stem); return;               // 2D 模式或開新分頁：直接前往教材
    }
    e.preventDefault();                        // 3D 模式：先在島上選取，面板再提供前往連結
    select(stem, { fly: true, trigger: link, keyboard: e.detail === 0 });
  });
  link.addEventListener('auxclick', e => { if (e.button === 1) markVisited(stem); });
});

function refreshTrail() {
  items.forEach(({ li, mark }, stem) => {
    const done = !!trail.done[stem], visited = !!trail.visited[stem];
    li.classList.toggle('is-done', done);
    li.classList.toggle('is-visited', visited && !done);
    mark.setAttribute('aria-pressed', String(done));
    mark.setAttribute('aria-label', (done ? '取消完成標記：' : '標記為已完成：') + BY[stem].title);
    mark.title = done ? '已完成（再按一次取消）' : '標記為已完成';
  });
  if (current) syncDoneButton();
  if (scene) scene.updateTrail();
}

/* ── 面板 ── */
const panel = $('islPanel');
let current = null, lastTrigger = null;
function syncDoneButton() {
  const done = !!trail.done[current];
  $('islPanelDone').setAttribute('aria-pressed', String(done));
  $('islPanelDone').textContent = done ? '✓ 已完成' : '標記完成';
}
function select(stem, { fly = false, trigger = null, keyboard = false } = {}) {
  const p = BY[stem]; if (!p) return;
  if (tour && stem !== tourStem()) endTour();   // 導覽中點了別的地方：退出導覽，進度保留
  if (!tour) { $('islGuide').hidden = true; $('islGuideNav').hidden = true; }
  current = stem; lastTrigger = trigger || lastTrigger;
  $('islPanelPage').hidden = false;
  const isle = ISLES[p.grp];
  $('islPanelKicker').textContent = `${isle.name} · ${p.code} · ${p.label}`;
  $('islPanelTitle').textContent = p.title;
  $('islPanelLandmark').textContent = '地標：' + p.landmark;
  $('islPanelBlurb').textContent = p.blurb;
  $('islPanelGo').href = p.href;
  const refList = $('islPanelRefList');
  refList.replaceChildren(...p.refs.map(r => {
    const li = document.createElement('li'), a = document.createElement('a');
    a.href = BY[r].href; a.textContent = `${BY[r].code} ${BY[r].title}`;
    a.addEventListener('click', () => markVisited(r));
    li.appendChild(a); return li;
  }));
  $('islPanelRefs').hidden = !p.refs.length;
  const fig = p.fig;
  $('islFig').hidden = !fig;
  if (fig) {
    const img = $('islFigImg');
    img.width = fig.w; img.height = fig.h; img.src = fig.src;
    img.alt = '代表互動圖：' + fig.caption;
    $('islFigCap').textContent = fig.caption;
    $('islFigLink').href = $('islFigGo').href = fig.href;
  }
  syncDoneButton();
  panel.hidden = false;
  items.forEach(({ li }, s) => {
    li.classList.toggle('is-current', s === stem);
    li.classList.toggle('is-ref', p.refs.includes(s));
  });
  if (scene) scene.select(stem, fly);
  if (keyboard) $('islPanelGo').focus();
}
function closePanel() {
  if (panel.hidden) return;
  endTour();
  panel.hidden = true; current = null;
  items.forEach(({ li }) => li.classList.remove('is-current', 'is-ref'));
  if (scene) scene.select(null, false);
  if (lastTrigger && document.contains(lastTrigger)) lastTrigger.focus();
  lastTrigger = null;
}
$('islPanelClose').addEventListener('click', closePanel);
$('islPanelGo').addEventListener('click', () => { if (current) markVisited(current); });
$('islPanelGo').addEventListener('auxclick', e => { if (e.button === 1 && current) markVisited(current); });
$('islPanelDone').addEventListener('click', () => { if (current) setDone(current, !trail.done[current]); });
['islFigLink', 'islFigGo'].forEach(id => {
  $(id).addEventListener('click', () => { if (current) markVisited(current); });
  $(id).addEventListener('auxclick', e => { if (e.button === 1 && current) markVisited(current); });
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') closePanel(); });
$('islClear').addEventListener('click', () => {
  if (!Object.keys(trail.visited).length && !Object.keys(trail.done).length) return;
  if (!window.confirm('清除這台裝置上的所有造訪與完成紀錄？')) return;
  trail = { visited: {}, done: {} }; saveTrail(); refreshTrail();
});
refreshTrail();

/* ── 嚮導「維導」的導覽（只在 3D 模式提供）──
   路線與台詞在 DATA.tour；進度 {route, i} 存在 localStorage，結束導覽時保留，走完才清掉。
   導覽沿用同一個面板：上方是維導的對話列，中間是該站的章節內容，下方是上一站／下一站。 */
const TOUR = DATA.tour, ROUTES = Object.fromEntries(TOUR.routes.map(r => [r.key, r]));
const TOUR_KEY = 'slss-island:tour:v1';
let tour = null;                                   // 導覽中：{ route, i }
const tourStem = () => tour && ROUTES[tour.route].stems[tour.i];
function savedTour() {
  try {
    const t = JSON.parse(localStorage.getItem(TOUR_KEY) || 'null');
    if (t && ROUTES[t.route] && Number.isInteger(t.i) && t.i >= 0 && t.i < ROUTES[t.route].stems.length) return t;
  } catch (e) { /* 壞掉的紀錄當作沒有 */ }
  return null;
}
function saveTour(t) {
  try { if (t) localStorage.setItem(TOUR_KEY, JSON.stringify(t)); else localStorage.removeItem(TOUR_KEY); } catch (e) { /* 只在本頁有效 */ }
}
function say(text, step = '', choices = []) {
  $('islGuide').hidden = false;
  $('islGuideText').textContent = text;
  $('islGuideStep').textContent = step;
  $('islGuideChoices').replaceChildren(...choices.map(([label, note, fn]) => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'isl-choice';
    const t = document.createElement('b'); t.textContent = label; b.appendChild(t);
    if (note) { const n = document.createElement('span'); n.textContent = note; b.appendChild(n); }
    b.addEventListener('click', fn);
    return b;
  }));
}
// 沒有選取章節時，面板只顯示維導的對話（選路線、問要不要接著走、走完了）
function guideOnly(text, choices) {
  if (tour) endTour();
  if (current) { current = null; items.forEach(({ li }) => li.classList.remove('is-current', 'is-ref')); if (scene) scene.select(null, false); }
  $('islPanelPage').hidden = true; $('islGuideNav').hidden = true;
  say(text, '', choices);
  panel.hidden = false;
  $('islGuideChoices').querySelector('button')?.focus();
}
function routeMenu() {
  guideOnly(TOUR.ask, TOUR.routes.map(r => [r.label, `${r.note}（${r.stems.length} 站）`, () => startTour(r.key, 0)]));
}
function openTour() {
  shrinkBubble();
  const t = savedTour();
  if (!t) { routeMenu(); return; }
  const r = ROUTES[t.route], stem = r.stems[t.i];
  guideOnly(TOUR.resume.replace('{n}', t.i + 1).replace('{title}', BY[stem].title),
    [['接著走', `${r.label} · 第 ${t.i + 1}／${r.stems.length} 站`, () => startTour(t.route, t.i)],
     ['重新選路線', '', routeMenu]]);
}
function startTour(route, i) {
  tour = { route, i };
  goStop(true);
}
function goStop(focusNext) {
  const r = ROUTES[tour.route], stem = r.stems[tour.i], last = tour.i === r.stems.length - 1;
  saveTour(tour);
  select(stem, { fly: true });
  panel.scrollTop = 0;
  if (scene) scene.guideTo(stem);
  say(BY[stem].guide, `第 ${tour.i + 1}／${r.stems.length} 站 · ${r.label}`);
  $('islGuideChoices').replaceChildren();
  $('islGuideNav').hidden = false;
  $('islGuidePrev').disabled = tour.i === 0;
  $('islGuideNext').textContent = last ? '完成導覽 ✓' : '下一站 →';
  if (focusNext) $('islGuideNext').focus();
}
// 離開導覽：不論從 Esc、關閉鈕、點別的島或清單進來，都在這裡收掉對話列；save=false 表示走完了
function endTour({ save = true } = {}) {
  if (!tour) return;
  if (!save) saveTour(null);
  tour = null;
  $('islGuide').hidden = true; $('islGuideNav').hidden = true;
}
$('islGuidePrev').addEventListener('click', () => { if (tour && tour.i > 0) { tour.i--; goStop(false); } });
$('islGuideNext').addEventListener('click', () => {
  if (!tour) return;
  if (tour.i < ROUTES[tour.route].stems.length - 1) { tour.i++; goStop(false); return; }
  endTour({ save: false });
  guideOnly(TOUR.bye, [['好', '', closePanel]]);
});
$('islGuideEnd').addEventListener('click', closePanel);

const bubble = $('islBubble');
function shrinkBubble() {
  if (bubble.classList.contains('is-small')) return;
  bubble.classList.add('is-small'); bubble.textContent = TOUR.short;
}
bubble.addEventListener('click', openTour);

/* ── 3D 場景（可選）── */
function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (e) { return false; }
}
function fallback2D(reason) {
  document.documentElement.classList.remove('gl-pending');
  document.body.classList.remove('webgl-ready');
  $('islStage').hidden = true; $('islReset').hidden = true;
  scene = null;
  console.info('3D 群島未啟用，改用 2D 地圖：' + reason);
}
if (hasWebGL()) {
  initScene().catch(err => fallback2D(err && err.message ? err.message : String(err)));
} else {
  document.documentElement.classList.remove('gl-pending');
  console.info('3D 群島未啟用，改用 2D 地圖：瀏覽器沒有 WebGL');
}

async function initScene() {
  // 三個模組同時抓（<head> 已 modulepreload，通常已在快取裡）
  const [THREE, { OrbitControls }, { RoundedBoxGeometry }] = await Promise.all([
    import('three'), import('three/addons/controls/OrbitControls.js'), import('three/addons/geometries/RoundedBoxGeometry.js')]);
  const stage = $('islStage'), canvas = $('islCanvas');
  document.body.classList.add('webgl-ready');
  stage.hidden = false;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  } catch (e) {
    throw new Error('WebGLRenderer 建立失敗');
  }
  scene = buildWorld(THREE, { OrbitControls, RoundedBoxGeometry }, renderer, stage, canvas);
  $('islReset').hidden = false;
  $('islReset').addEventListener('click', () => scene && scene.reset());
  document.querySelectorAll('.isl-jump-btn').forEach(b =>
    b.addEventListener('click', () => scene && scene.flyToIsle(b.dataset.grp)));
  const night = $('islNight');
  const applyNight = (on, instant) => {
    night.setAttribute('aria-pressed', String(on));
    night.textContent = on ? '回到白天' : '入夜';
    stage.classList.toggle('is-night', on);
    if (scene) scene.setNight(on, instant);
  };
  let isNight = false;
  try { isNight = localStorage.getItem(NIGHT_KEY) === '1'; } catch (e) { /* 只在本頁有效 */ }
  applyNight(isNight, true);
  night.addEventListener('click', () => {
    isNight = !isNight; applyNight(isNight, false);
    try { localStorage.setItem(NIGHT_KEY, isNight ? '1' : '0'); } catch (e) { /* 只在本頁有效 */ }
  });
  canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); scene && scene.dispose(); fallback2D('WebGL context lost'); });
  window.__island = { screenPos: stem => scene && scene.screenPos(stem), stats: () => scene && scene.stats(),
    guidePos: () => scene && scene.guidePos() };
  refreshTrail();
  if (current) scene.select(current, false);
  await scene.warm();                       // 先編譯著色器、畫好第一幀，再淡入畫布
  document.documentElement.classList.remove('gl-pending');
  // 群島淡入後，維導冒出來打招呼；過一陣子縮成小按鈕
  bubble.setAttribute('aria-label', '請' + TOUR.name + '帶路');
  setTimeout(() => {
    if (!scene) return;
    bubble.hidden = false;
    setTimeout(shrinkBubble, 8000);
  }, 1500);
}
