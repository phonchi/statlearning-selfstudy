/* 3D 統計學習知識群島。build_island.py 會把本檔 inline 進 island/index.html 的 <script type="module">。
 *
 * 分兩層：
 *   1. UI 層（不需要 Three.js）：章節列表、足跡（localStorage）、面板、鍵盤操作。
 *      CDN 失效、WebGL 不可用時頁面停在 2D 地圖，這一層照常運作。
 *   2. 場景層：WebGL 可用才以 dynamic import 載入 Three.js（importmap 釘版＋integrity），
 *      成功後才在 <body> 加 .webgl-ready，切成 3D＋側欄。
 * 建築全部是程序化幾何（box/cylinder/cone/icosahedron/torus/tube），沒有任何外部模型或圖檔。
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
  current = stem; lastTrigger = trigger || lastTrigger;
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
document.addEventListener('keydown', e => { if (e.key === 'Escape') closePanel(); });
$('islClear').addEventListener('click', () => {
  if (!Object.keys(trail.visited).length && !Object.keys(trail.done).length) return;
  if (!window.confirm('清除這台裝置上的所有造訪與完成紀錄？')) return;
  trail = { visited: {}, done: {} }; saveTrail(); refreshTrail();
});
refreshTrail();

/* ── 3D 場景（可選）── */
function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (e) { return false; }
}
function fallback2D(reason) {
  document.body.classList.remove('webgl-ready');
  $('islStage').hidden = true; $('islReset').hidden = true;
  scene = null;
  console.info('3D 群島未啟用，改用 2D 地圖：' + reason);
}
if (hasWebGL()) {
  initScene().catch(err => fallback2D(err && err.message ? err.message : String(err)));
} else {
  console.info('3D 群島未啟用，改用 2D 地圖：瀏覽器沒有 WebGL');
}

async function initScene() {
  const THREE = await import('three');
  const { OrbitControls } = await import('three/addons/controls/OrbitControls.js');
  const stage = $('islStage'), canvas = $('islCanvas');
  document.body.classList.add('webgl-ready');
  stage.hidden = false;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  } catch (e) {
    throw new Error('WebGLRenderer 建立失敗');
  }
  scene = buildWorld(THREE, OrbitControls, renderer, stage, canvas);
  $('islReset').hidden = false;
  $('islReset').addEventListener('click', () => scene && scene.reset());
  document.querySelectorAll('.isl-jump-btn').forEach(b =>
    b.addEventListener('click', () => scene && scene.flyToIsle(b.dataset.grp)));
  canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); scene && scene.dispose(); fallback2D('WebGL context lost'); });
  window.__island = { screenPos: stem => scene && scene.screenPos(stem) };
  refreshTrail();
  if (current) scene.select(current, false);
}

/* ═════════════════════════ 場景 ═════════════════════════ */
function buildWorld(THREE, OrbitControls, renderer, stage, canvas) {
  const C = {
    grass: '#86b56f', grass2: '#5f9a5a', forest: '#1a6b4a', leaf: '#3f8f5a', sand: '#ecdcb5',
    paper: '#f7f3eb', cream: '#fffdf7', navy: '#2c3e7a', navyL: '#4a63a8', red: '#c0392b',
    redL: '#e8a49b', blue: '#2f6db5', blueL: '#a9c3e6', orange: '#e67e22', amber: '#f0b429',
    wood: '#a0703f', woodD: '#6e4a2b', stone: '#cfc7b6', stoneD: '#9b9384', rock: '#7d7a73',
    water: '#6f9fc4', shallow: '#9cc5dc', white: '#ffffff', ink: '#1a1a2e', teal: '#16a085',
  };
  const motion = () => !reduceMotion.matches;
  const world = new THREE.Scene();
  const rnd = mulberry32(524);

  /* ── 材質與幾何小工具 ── */
  const mats = new Map();
  function mat(color, extra) {
    const key = color + (extra ? JSON.stringify(extra) : '');
    if (!mats.has(key)) mats.set(key, new THREE.MeshLambertMaterial({ color, flatShading: true, ...extra }));
    return mats.get(key);
  }
  function put(geo, color, x = 0, y = 0, z = 0, extra) {
    const m = new THREE.Mesh(geo, extra && extra.isMaterial ? extra : mat(color, extra));
    m.position.set(x, y, z); return m;
  }
  // y 一律是「底面高度」，方便堆疊
  const box = (w, h, d, c, x = 0, y = 0, z = 0) => put(new THREE.BoxGeometry(w, h, d), c, x, y + h / 2, z);
  const cyl = (rt, rb, h, c, x = 0, y = 0, z = 0, seg = 8) => put(new THREE.CylinderGeometry(rt, rb, h, seg), c, x, y + h / 2, z);
  const cone = (r, h, c, x = 0, y = 0, z = 0, seg = 6) => put(new THREE.ConeGeometry(r, h, seg), c, x, y + h / 2, z);
  const ball = (r, c, x = 0, y = 0, z = 0, extra) => put(new THREE.IcosahedronGeometry(r, 0), c, x, y, z, extra);
  const group = (...kids) => { const g = new THREE.Group(); kids.forEach(k => g.add(k)); return g; };
  const roof = (w, h, d, c, y) => {           // 三角屋頂（擠出的三角形，屋脊沿 z 軸）
    const tri = new THREE.Shape();
    tri.moveTo(-w / 2, 0); tri.lineTo(w / 2, 0); tri.lineTo(0, h); tri.closePath();
    const geo = new THREE.ExtrudeGeometry(tri, { depth: d, bevelEnabled: false });
    geo.translate(0, 0, -d / 2);
    return put(geo, c, 0, y, 0);
  };
  const glow = color => new THREE.MeshLambertMaterial({ color, emissive: color, emissiveIntensity: .55, flatShading: true });
  const anims = [];                          // 每幀呼叫的 (t) => void
  let need = true, raf = 0, onScreen = true, alive = true;   // 繪製迴圈狀態（requestRender 很早就會被呼叫）

  /* ── 燈光 ── */
  world.add(new THREE.HemisphereLight('#fff7e6', '#4d6f96', 1.9));
  const sun = new THREE.DirectionalLight('#fff0d4', 2.4);
  sun.position.set(-30, 60, 40); world.add(sun);

  /* ── 島嶼地形 ── */
  const shape = (th, seed) => 1 + .07 * Math.sin(3 * th + seed) + .045 * Math.sin(5 * th + seed * 2.3) + .025 * Math.sin(9 * th + seed * .7);
  function shaped(geo, seed) {
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i), r = Math.hypot(x, z);
      if (r < 1e-6) continue;
      const k = shape(Math.atan2(z, x), seed); p.setX(i, x * k); p.setZ(i, z * k);
    }
    geo.computeVertexNormals(); return geo;
  }
  const GROUND = 1.0;
  const ISLE_GEO = {
    core: { x: 0, z: 0, r: 15, seed: 1.3, grass: C.grass },
    pre: { x: 19, z: 19, r: 7, seed: 4.1, grass: '#9cc27a' },
    statistics: { x: -28.3, z: 8.5, r: 9.5, seed: 2.2, grass: C.grass2 },
    appendix: { x: 8.5, z: -28.3, r: 9.5, seed: 5.7, grass: '#93b98a' },
  };
  const ocean = put(new THREE.CircleGeometry(160, 40), C.water, 0, .2, 0);
  ocean.rotation.x = -Math.PI / 2; world.add(ocean);
  Object.values(ISLE_GEO).forEach(I => {
    const g = new THREE.Group(); g.position.set(I.x, 0, I.z);
    const shallow = put(shaped(new THREE.CylinderGeometry(I.r * 1.5, I.r * 1.5, .05, 24), I.seed), C.shallow, 0, .22, 0);
    g.add(shallow);
    g.add(put(shaped(new THREE.CylinderGeometry(I.r * 1.18, I.r * .55, 2.6, 18), I.seed), C.stoneD, 0, -1.2, 0));
    g.add(put(shaped(new THREE.CylinderGeometry(I.r * 1.1, I.r * 1.18, .7, 18), I.seed), C.sand, 0, .35, 0));
    g.add(put(shaped(new THREE.CylinderGeometry(I.r, I.r * 1.03, .55, 18), I.seed), I.grass, 0, .725, 0));
    world.add(g);
    I.inside = (x, z, m = .82) => {             // 世界座標是否在島上（含邊界餘裕）
      const dx = x - I.x, dz = z - I.z;
      return Math.hypot(dx, dz) < I.r * shape(Math.atan2(dz, dx), I.seed) * m;
    };
  });
  // 主島中央的高地：深度學習（補充）在這裡
  const HILL = 1.7;
  world.add(put(new THREE.CylinderGeometry(2.2, 4.4, HILL, 9), C.grass2, 0, GROUND + HILL / 2, 0));

  /* ── 建築位置 ── */
  const SLOTS = {};
  const core = PAGES.filter(p => p.grp === 'core');
  const ring = core.filter(p => p.stem !== 'deep_learning');
  ring.forEach((p, i) => {
    const th = (70 + i * (360 - 70) / ring.length + 18) * Math.PI / 180;
    SLOTS[p.stem] = { x: Math.cos(th) * 10.6, y: GROUND, z: Math.sin(th) * 10.6 };
  });
  if (BY.deep_learning) SLOTS.deep_learning = { x: 0, y: GROUND + HILL, z: 0 };
  // 附屬島以初始視角的「螢幕座標」排版：u 往右、v 往前（畫面下方），閱讀順序＝左到右、上到下
  const local = { pre: [[-2.4, -1.6], [1.4, 5.2], [2.6, -1.2]],   // B 碼頭伸出前岸
                  statistics: [[-4.2, -2.6], [0, -2.9], [4.2, -2.6], [-4.2, 2.3], [0, 2.6], [4.2, 2.3]],
                  appendix: [[-4.2, -2.6], [0, -2.9], [4.2, -2.6], [-4.2, 2.3], [0, 2.6], [4.2, 2.3]] };
  ['pre', 'statistics', 'appendix'].forEach(grp => {
    const I = ISLE_GEO[grp];
    PAGES.filter(p => p.grp === grp).forEach((p, i) => {
      const [u, v] = local[grp][i] || [0, 0];
      SLOTS[p.stem] = { x: I.x + (u + v) * Math.SQRT1_2, y: GROUND, z: I.z + (v - u) * Math.SQRT1_2 };
    });
  });
  // 少數頁面可能被新增或刪除：沒有指定位置的頁面放在該島中心附近，確保 26 個入口都在
  PAGES.forEach((p, i) => {
    if (!SLOTS[p.stem]) { const I = ISLE_GEO[p.grp]; SLOTS[p.stem] = { x: I.x + (i % 3) - 1, y: GROUND, z: I.z + 1 }; }
  });

  /* ── 小徑、橋 ── */
  const stoneGeo = new THREE.CylinderGeometry(.42, .48, .08, 6);
  const pathPts = [];
  for (let a = 0; a < 360; a += 7.5) pathPts.push([Math.cos(a * Math.PI / 180) * 7.2, Math.sin(a * Math.PI / 180) * 7.2]);
  ring.forEach(p => {             // 環狀小徑到各棟建築的支線
    const s = SLOTS[p.stem], r = Math.hypot(s.x, s.z);
    for (let d = 8.2; d < r - 1.4; d += 1) pathPts.push([s.x / r * d, s.z / r * d]);
  });
  for (let d = 4.6; d < 6.6; d += 1) pathPts.push([d * Math.SQRT1_2 * -1, d * Math.SQRT1_2 * -1]);  // 上高地的路
  const stones = new THREE.InstancedMesh(stoneGeo, mat('#e8dcc0'), pathPts.length);
  const tmp = new THREE.Object3D();
  pathPts.forEach(([x, z], i) => {
    tmp.position.set(x, GROUND + .04, z); tmp.rotation.set(0, rnd() * 3, 0); tmp.updateMatrix();
    stones.setMatrixAt(i, tmp.matrix);
  });
  world.add(stones);

  const bridges = [];
  function bridge(grp) {
    const A = ISLE_GEO.core, B = ISLE_GEO[grp];
    const dx = B.x - A.x, dz = B.z - A.z, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L;
    const s0 = A.r * shape(Math.atan2(uz, ux), A.seed) * .9, s1 = L - B.r * shape(Math.atan2(-uz, -ux), B.seed) * .9;
    const n = Math.ceil((s1 - s0) / .55), ang = Math.atan2(ux, uz);
    const planks = new THREE.InstancedMesh(new THREE.BoxGeometry(2.3, .14, .46), mat(C.wood), n + 1);
    const posts = [];
    for (let i = 0; i <= n; i++) {
      const t = i / n, s = s0 + (s1 - s0) * t, y = GROUND - .05 + Math.sin(Math.PI * t) * .9;
      tmp.position.set(A.x + ux * s, y, A.z + uz * s); tmp.rotation.set(0, ang, 0); tmp.updateMatrix();
      planks.setMatrixAt(i, tmp.matrix);
      if (i % 3 === 0) posts.push([A.x + ux * s, y, A.z + uz * s]);
    }
    world.add(planks);
    const postGeo = new THREE.BoxGeometry(.16, .9, .16);
    const pm = new THREE.InstancedMesh(postGeo, mat(C.woodD), posts.length * 2);
    posts.forEach(([x, y, z], i) => {
      [-1, 1].forEach((side, j) => {
        tmp.position.set(x + uz * 1.1 * side, y + .45, z - ux * 1.1 * side); tmp.rotation.set(0, 0, 0); tmp.updateMatrix();
        pm.setMatrixAt(i * 2 + j, tmp.matrix);
      });
    });
    world.add(pm);
    bridges.push({ x0: A.x + ux * s0, z0: A.z + uz * s0, x1: A.x + ux * s1, z1: A.z + uz * s1 });
  }
  ['pre', 'statistics', 'appendix'].forEach(bridge);

  /* ── 建築配方 ── */
  const R = {};
  // 01 觀測塔＋漂浮散點
  R.introduction = () => {
    const g = group(cyl(1.3, 1.45, .4, C.stone), cyl(.7, .95, 3.4, C.paper, 0, .4, 0, 8),
      cyl(1.25, 1.25, .25, C.wood, 0, 3.8, 0, 8), cone(1.3, 1.3, C.navy, 0, 4.05, 0, 8),
      box(.4, .6, .1, C.navy, 0, 1.2, .9), box(.36, .36, .1, C.amber, 0, 2.6, .85));
    const dots = new THREE.Group();
    [C.red, C.navy, C.forest, C.orange, C.navy, C.red, C.forest].forEach((c, i) => {
      const a = i / 7 * Math.PI * 2; dots.add(ball(.2, c, Math.cos(a) * 1.9, 1.4 + (i * .37) % 1.9, Math.sin(a) * 1.9));
    });
    g.add(dots);
    anims.push(t => { dots.rotation.y = t * .25; });
    return g;
  };
  // 02 訓練／測試分岔路
  R.statistical_learning = () => {
    const g = group(box(.9, .08, 1.8, '#e8dcc0', 0, 0, 1));
    [-1, 1].forEach(s => { const b = box(.8, .08, 1.9, '#e8dcc0', s * .75, 0, -.55); b.rotation.y = s * .55; g.add(b); });
    g.add(cyl(.11, .13, 2.6, C.woodD, 0, 0, .2, 6));
    const a1 = box(1.5, .42, .12, C.forest, .55, 2.0, .2), a2 = box(1.3, .42, .12, C.orange, -.5, 1.45, .2);
    a1.rotation.y = -.35; a2.rotation.y = .35; g.add(a1, a2);
    [[-1.5, -1.3], [-1.1, -1.7], [-1.6, -1.8]].forEach(([x, z]) => g.add(box(.45, .45, .45, C.forest, x, 0, z)));
    g.add(box(.45, .45, .45, C.orange, 1.5, 0, -1.6));
    return g;
  };
  // 03 迴歸斜坡穿過散點
  R.linear_regression = () => {
    const g = group(box(3.8, .25, 2.4, C.stone));
    const ramp = box(4.0, .2, .8, C.navy, 0, 1.05, 0); ramp.rotation.z = .42; g.add(ramp);
    g.add(box(.22, 1.6, .22, C.woodD, 1.2, .25, 0), box(.22, .55, .22, C.woodD, -1.0, .25, 0));
    for (let i = 0; i < 9; i++) {
      const x = -1.6 + i * .4, y = 1.25 + Math.tan(.42) * x + (rnd() - .5) * .9;
      g.add(ball(.17, i % 2 ? C.red : C.forest, x, Math.max(.45, y), (rnd() - .5) * 1.4 + (i % 2 ? .55 : -.55)));
    }
    return g;
  };
  // 04 紅藍雙色分類城門
  R.classification = () => {
    const g = group(box(1.7, .06, 2.4, C.redL, -.85, 0, 0), box(1.7, .06, 2.4, C.blueL, .85, 0, 0),
      box(.9, 2.7, .9, C.red, -1.2, 0, 0), box(.9, 2.7, .9, C.blue, 1.2, 0, 0),
      box(1.35, .55, .9, C.red, -.67, 2.7, 0), box(1.35, .55, .9, C.blue, .67, 2.7, 0));
    [-1.5, -.9, .9, 1.5].forEach(x => g.add(box(.3, .3, .9, x < 0 ? C.red : C.blue, x, 3.25, 0)));
    g.add(cone(.22, .5, C.amber, 0, 3.25, 0, 4));
    return g;
  };
  // 05 Bootstrap 噴泉：球不斷被「重抽」出來
  R.resampling_methods = () => {
    const g = group(cyl(1.6, 1.75, .5, C.stone, 0, 0, 0, 10), cyl(1.4, 1.4, .06, C.shallow, 0, .46, 0, 10),
      cyl(.22, .3, 1.4, C.paper, 0, .5, 0, 6), cyl(.65, .22, .3, C.stone, 0, 1.9, 0, 8));
    const cols = [C.red, C.navy, C.forest, C.amber];
    const balls = [];
    for (let i = 0; i < 10; i++) {
      const b = ball(.15, cols[i % 4]); g.add(b);
      balls.push({ b, a: i / 10 * Math.PI * 2 + i, ph: i / 10 });
    }
    const place = t => balls.forEach(({ b, a, ph }) => {
      const u = (t * .55 + ph) % 1, r = .25 + 1.0 * u;
      b.position.set(Math.cos(a) * r, 2.15 + 2.0 * u - 2.6 * u * u, Math.sin(a) * r);
    });
    place(0.37); anims.push(place);
    return g;
  };
  // 06 修剪花園：灌木由高到低（正則化把係數往 0 收縮）
  R.model_selection = () => {
    const g = group(box(3.8, .18, 2.2, C.grass2));
    [1.7, 1.25, .9, .6, .35].forEach((h, i) => g.add(box(.6, h, .9 + h * .2, i % 2 ? C.leaf : C.forest, -1.5 + i * .75, .18, 0)));
    [-1.9, 1.9].forEach(x => [-1.05, 1.05].forEach(z => g.add(box(.12, .5, .12, C.woodD, x, .18, z))));
    g.add(box(3.9, .08, .08, C.woodD, 0, .58, 1.05), box(3.9, .08, .08, C.woodD, 0, .58, -1.05));
    return g;
  };
  // 07 樣條拱橋：曲線通過節點
  R.beyond_linearity = () => {
    const pts = [[-1.9, .2], [-1.1, 1.9], [-.2, 1.2], [.8, 2.5], [1.9, .2]].map(([x, y]) => new THREE.Vector3(x, y, 0));
    const curve = new THREE.CatmullRomCurve3(pts);
    const g = group(box(.7, .5, 1.6, C.stone, -1.9, 0, 0), box(.7, .5, 1.6, C.stone, 1.9, 0, 0));
    [-.5, .5].forEach(z => {
      const tube = put(new THREE.TubeGeometry(curve, 40, .16, 5), C.orange, 0, 0, z); g.add(tube);
    });
    pts.slice(1, -1).forEach(p => g.add(ball(.24, C.navy, p.x, p.y, -.5), ball(.24, C.navy, p.x, p.y, .5)));
    return g;
  };
  // 08 決策樹森林：一片樹＝集成
  R.tree_based_methods = () => {
    const g = new THREE.Group();
    [[0, 0, 1.25], [-1.3, .7, .9], [1.2, .8, .95], [-.8, -1.1, .8], [1.0, -1.0, .85], [0, 1.5, .7]].forEach(([x, z, s], i) => {
      g.add(cyl(.13 * s, .18 * s, 1.0 * s, C.woodD, x, 0, z, 5));
      g.add(cone(.95 * s, 1.4 * s, i % 2 ? C.leaf : C.forest, x, .8 * s, z, 6));
      g.add(cone(.7 * s, 1.1 * s, i % 2 ? C.forest : C.leaf, x, 1.6 * s, z, 6));
    });
    g.add(box(.5, .3, .12, C.amber, 0, 3.4, 0));
    return g;
  };
  // 09 最大間隔圍牆：兩群資料，中間是邊界與兩條間隔線
  R.support_vector_machines = () => {
    const g = group(box(4, .06, 3, '#e3dccb'), box(.36, 1.3, 3, C.paper, 0, .06, 0), box(.5, .16, 3.1, C.stone, 0, 1.36, 0),
      box(.1, .05, 3, C.amber, -.95, .06, 0), box(.1, .05, 3, C.amber, .95, .06, 0));
    [[-1.05, -.9], [-1.5, .3], [-1.75, -.4], [-1.3, 1.0], [-1.8, .9]].forEach(([x, z]) => g.add(box(.42, .42, .42, C.red, x, .06, z)));
    [[1.1, .6], [1.5, -.5], [1.8, .3], [1.35, -1.1], [1.75, 1.1]].forEach(([x, z]) => g.add(ball(.25, C.blue, x, .32, z)));
    return g;
  };
  // 10 群聚星球廣場
  R.unsupervised_learning = () => {
    const g = group(cyl(2.0, 2.1, .2, C.stone, 0, 0, 0, 12));
    [[C.red, -.85, .55], [C.navy, .9, .45], [C.forest, 0, -.95]].forEach(([c, cx, cz]) => {
      for (let i = 0; i < 5; i++) {
        const a = i / 5 * Math.PI * 2 + cx;
        g.add(ball(.22, c, cx + Math.cos(a) * .42, .45 + (i % 2) * .25, cz + Math.sin(a) * .42));
      }
      g.add(cone(.16, .5, C.amber, cx, .2, cz, 4));
    });
    return g;
  };
  // 11 神經網路高塔（補充，位於中央高地）
  R.deep_learning = () => {
    const g = group(cyl(1.2, 1.4, .35, C.stone, 0, 0, 0, 8), cyl(.22, .26, 4.6, C.paper, 0, .35, 0, 6));
    const layers = [5, 4, 4, 2], nodes = [];
    const pulse = layers.map(() => glow(C.amber));
    layers.forEach((n, li) => {
      const y = .9 + li * 1.15, r = 1.05 - li * .15;
      g.add(cyl(r + .25, r + .25, .12, C.navy, 0, y - .2, 0, 10));
      const row = [];
      for (let i = 0; i < n; i++) {
        const a = i / n * Math.PI * 2;
        const b = ball(.2, null, Math.cos(a) * r, y + .1, Math.sin(a) * r, pulse[li]); g.add(b);
        row.push(b.position.clone());
      }
      nodes.push(row);
    });
    const seg = [];
    for (let li = 0; li < nodes.length - 1; li++) nodes[li].forEach(a => nodes[li + 1].forEach(b => seg.push(a, b)));
    const lines = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(seg),
      new THREE.LineBasicMaterial({ color: '#f7d774', transparent: true, opacity: .55 }));
    g.add(lines, ball(.38, null, 0, 5.3, 0, glow('#f7d774')));
    anims.push(t => pulse.forEach((m, i) => { m.emissiveIntensity = .25 + .75 * Math.max(0, Math.sin(t * 2.2 - i * .9)); }));
    return g;
  };
  // 啟航島：港口語彙
  R['00a_why_code'] = () => {               // 燈塔
    const g = group(cyl(1.0, 1.15, .35, C.stone));
    [C.red, C.cream, C.red, C.cream].forEach((c, i) => g.add(cyl(.62 - i * .07, .69 - i * .07, .75, c, 0, .35 + i * .75, 0, 8)));
    const lamp = put(new THREE.CylinderGeometry(.45, .45, .5, 8), null, 0, 3.6, 0, glow('#f7d774')); g.add(lamp);
    g.add(cyl(.62, .62, .1, C.navy, 0, 3.3, 0, 8), cone(.6, .6, C.navy, 0, 3.85, 0, 8));
    anims.push(t => { lamp.material.emissiveIntensity = .45 + .4 * Math.max(0, Math.sin(t * 1.6)); });
    return g;
  };
  R['00b_setup'] = () => {                 // 補給碼頭
    const g = group(box(1.5, .14, 3.4, C.wood, 0, .05, .4));
    [-1.1, .4, 1.9].forEach(z => [-.65, .65].forEach(x => g.add(box(.16, 1.2, .16, C.woodD, x, -.9, z))));
    g.add(box(.7, .7, .7, C.wood, -.3, .19, -.6), box(.5, .5, .5, C.orange, .35, .19, -.3), box(.45, .45, .45, C.navy, -.25, .89, -.6));
    return g;
  };
  R['00c_ai_assisted'] = () => {           // 領航站
    const g = group(box(1.7, 1.2, 1.4, C.cream), roof(1.9, .9, 1.6, C.navy, 1.2),
      box(.4, .7, .06, C.woodD, 0, 0, .72), box(.4, .3, .06, '#9cc5dc', -.5, .6, .72), box(.4, .3, .06, '#9cc5dc', .5, .6, .72),
      cyl(.05, .05, 2.6, C.woodD, 1.05, 0, -.4, 5));
    const flag = box(.7, .4, .04, C.forest, 1.42, 2.1, -.4); g.add(flag);
    anims.push(t => { flag.rotation.y = Math.sin(t * 2.4) * .25; });
    return g;
  };
  // 統計森林島：樹屋語彙
  const treehouse = i => () => {
    const h = 1.5 + (i % 3) * .35;
    const g = group(cyl(.24, .32, h + .6, C.woodD, 0, 0, 0, 6), ball(1.15, C.leaf, -.3, h + 1.7, -.4), ball(.8, C.forest, .5, h + 1.9, -.6),
      cyl(1.05, 1.05, .14, C.wood, 0, h, 0, 8), box(1.0, .8, .9, C.cream, 0, h + .14, .05),
      roof(1.2, .65, 1.05, i % 2 ? C.forest : '#2f7f5a', h + .94), box(.32, .5, .05, C.woodD, 0, h + .14, .51));
    for (let k = 0; k < 4; k++) g.add(box(.5, .06, .06, C.woodD, .75, .3 + k * h / 4, .5));
    return g;
  };
  // Python 工坊島：工坊語彙
  const workshop = i => () => {
    const g = group(box(1.8, 1.1, 1.5, C.cream), roof(2.0, .85, 1.7, C.navy, 1.1),
      box(.45, .75, .06, C.woodD, -.35, 0, .76), box(.45, .32, .06, '#f7d774', .45, .45, .76),
      box(.32, .9, .32, C.stoneD, .55, 1.2, -.35));
    const gear = put(new THREE.TorusGeometry(.26, .09, 4, 8), C.amber, .45, 1.05, .8); g.add(gear);
    const puffs = [0, 1, 2].map(k => { const b = ball(.16 + k * .04, '#eef1f4', .55, 2.3, -.35); g.add(b); return b; });
    anims.push(t => {
      gear.rotation.z = t * .8 + i;
      puffs.forEach((b, k) => { const u = (t * .35 + k / 3 + i * .13) % 1; b.position.set(.55 + u * .4, 2.2 + u * 1.3, -.35); b.scale.setScalar(.6 + u); });
    });
    return g;
  };
  PAGES.filter(p => p.grp === 'statistics').forEach((p, i) => { R[p.stem] = R[p.stem] || treehouse(i); });
  PAGES.filter(p => p.grp === 'appendix').forEach((p, i) => { R[p.stem] = R[p.stem] || workshop(i); });
  const generic = () => group(box(1.4, 1.2, 1.4, C.cream), roof(1.6, .8, 1.6, C.forest, 1.2));

  /* ── 放置建築、招牌、拾取盒、足跡標記 ── */
  const BADGE = { core: '#1a6b4a', pre: '#b9770e', statistics: '#2f7f5a', appendix: '#2c3e7a' };
  const B = {};                    // stem → { g, pick, top, foot, visitRing, refRing, flag }
  const picks = [];
  const box3 = new THREE.Box3(), v3 = new THREE.Vector3();
  const pickMat = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false });
  const GLOW_VISIT = glow(C.amber), GLOW_DONE = glow(C.forest);
  const ringGeo = r => { const t = new THREE.TorusGeometry(r, .1, 4, 28); t.rotateX(Math.PI / 2); return t; };
  PAGES.forEach(p => {
    const s = SLOTS[p.stem];
    const g = (R[p.stem] || generic)();
    g.position.set(s.x, s.y, s.z);
    g.rotation.y = Math.PI / 4;              // 正面朝向初始視角
    world.add(g);
    g.updateMatrixWorld(true);
    box3.setFromObject(g);
    const size = box3.getSize(new THREE.Vector3());
    const foot = Math.max(1.2, Math.min(2.4, Math.max(size.x, size.z) / 2));
    const top = box3.max.y;
    const pick = new THREE.Mesh(new THREE.BoxGeometry(foot * 2, top - s.y + 1.2, foot * 2), pickMat);
    pick.position.set(s.x, (top + s.y + 1.2) / 2, s.z); pick.userData.stem = p.stem;
    world.add(pick); picks.push(pick);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: badge(p.code, BADGE[p.grp]), depthTest: false, transparent: true }));
    sprite.scale.set(1.5, .84, 1); sprite.position.set(s.x, top + .75, s.z); sprite.renderOrder = 10;
    world.add(sprite);
    const visitRing = new THREE.Mesh(ringGeo(foot + .25), GLOW_VISIT); visitRing.position.set(s.x, s.y + .05, s.z);
    const refRing = new THREE.Mesh(ringGeo(foot + .55), new THREE.MeshBasicMaterial({ color: C.navyL, transparent: true, opacity: .9 }));
    refRing.position.set(s.x, s.y + .07, s.z);
    const flag = group(cyl(.05, .05, 1.8, C.woodD, 0, 0, 0, 5), box(.75, .45, .04, C.forest, .4, 1.3, 0));
    flag.position.set(s.x + foot * .8, s.y, s.z + foot * .8);
    visitRing.visible = refRing.visible = flag.visible = false;
    world.add(visitRing, refRing, flag);
    B[p.stem] = { g, pick, top, foot, sprite, visitRing, refRing, flag, s };
  });

  /* ── 裝飾：樹、石頭（InstancedMesh）、帆船 ── */
  const blocked = (x, z) => Object.values(SLOTS).some(s => Math.hypot(x - s.x, z - s.z) < 2.9)
    || Math.abs(Math.hypot(x, z) - 7.2) < 1.0 || Math.hypot(x, z) < 5
    || bridges.some(b => Math.hypot(x - b.x0, z - b.z0) < 2.2 || Math.hypot(x - b.x1, z - b.z1) < 2.2);
  const treeSpots = [];
  [['core', 46], ['statistics', 34], ['pre', 5], ['appendix', 8]].forEach(([grp, n]) => {
    const I = ISLE_GEO[grp]; let tries = 0;
    while (treeSpots.length < 1e4 && n > 0 && tries++ < 4000) {
      const x = I.x + (rnd() * 2 - 1) * I.r, z = I.z + (rnd() * 2 - 1) * I.r;
      if (!I.inside(x, z, .88) || blocked(x, z) || treeSpots.some(t => Math.hypot(t[0] - x, t[1] - z) < 1.15)) continue;
      treeSpots.push([x, z, .65 + rnd() * .55, grp === 'statistics' || rnd() < .5]); n--;
    }
  });
  const trunk = new THREE.InstancedMesh(new THREE.CylinderGeometry(.1, .14, .7, 5), mat(C.woodD), treeSpots.length);
  const crownA = new THREE.InstancedMesh(new THREE.ConeGeometry(.65, 1.5, 6), mat(C.forest), treeSpots.length);
  const crownB = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.7, 0), mat(C.leaf), treeSpots.length);
  let na = 0, nb = 0;
  treeSpots.forEach(([x, z, s, pine], i) => {
    tmp.rotation.set(0, rnd() * 6, 0); tmp.scale.setScalar(s);
    tmp.position.set(x, GROUND + .35 * s, z); tmp.updateMatrix(); trunk.setMatrixAt(i, tmp.matrix);
    if (pine) { tmp.position.set(x, GROUND + (.7 + .75) * s, z); tmp.updateMatrix(); crownA.setMatrixAt(na++, tmp.matrix); }
    else { tmp.position.set(x, GROUND + (.7 + .55) * s, z); tmp.updateMatrix(); crownB.setMatrixAt(nb++, tmp.matrix); }
  });
  crownA.count = na; crownB.count = nb;
  world.add(trunk, crownA, crownB);
  const rocks = [];
  Object.values(ISLE_GEO).forEach(I => {
    for (let k = 0; k < Math.round(I.r * 1.3); k++) {
      const a = rnd() * Math.PI * 2, r = I.r * shape(a, I.seed) * (1.12 + rnd() * .12);
      const x = I.x + Math.cos(a) * r, z = I.z + Math.sin(a) * r;
      if (bridges.some(b => Math.hypot(x - b.x0, z - b.z0) < 2.6 || Math.hypot(x - b.x1, z - b.z1) < 2.6)) continue;
      rocks.push([x, z, .35 + rnd() * .45]);
    }
  });
  const rockMesh = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(1, 0), mat(C.rock), rocks.length);
  rocks.forEach(([x, z, s], i) => {
    tmp.position.set(x, .3, z); tmp.rotation.set(rnd(), rnd() * 6, rnd()); tmp.scale.set(s, s * .7, s); tmp.updateMatrix();
    rockMesh.setMatrixAt(i, tmp.matrix);
  });
  world.add(rockMesh);
  const boat = group(box(1.4, .35, .55, C.woodD, 0, 0, 0), cyl(.04, .04, 1.4, C.cream, 0, .35, 0, 4));
  const sail = put(new THREE.ConeGeometry(.55, 1.1, 3), C.cream, .1, 1.1, 0); sail.scale.set(.15, 1, 1); boat.add(sail);
  world.add(boat);
  const boatAt = t => { const a = t * .12, I = ISLE_GEO.pre; boat.position.set(I.x + Math.cos(a) * 11.5, .22, I.z + Math.sin(a) * 11.5); boat.rotation.y = -a; };
  boatAt(1.1); anims.push(boatAt);

  /* ── 選取標記 ── */
  const marker = put(new THREE.ConeGeometry(.42, .9, 4), null, 0, 0, 0, glow(C.amber)); marker.rotation.x = Math.PI; marker.visible = false; world.add(marker);
  let selected = null, refs = [];
  anims.push(t => {
    if (selected) marker.position.y = B[selected].top + 1.9 + Math.sin(t * 3) * .18;
    refs.forEach(r => { B[r].refRing.material.opacity = .55 + .4 * Math.sin(t * 3); });
  });

  /* ── 相機與操作 ── */
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 600);
  const HOME = new THREE.Vector3(1.5, 0, 1.5);
  const POLAR = 55 * Math.PI / 180;
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.minPolarAngle = controls.maxPolarAngle = POLAR;
  controls.minZoom = .75; controls.maxZoom = 4.5;
  controls.enableDamping = motion(); controls.dampingFactor = .09;
  controls.rotateSpeed = .7; controls.zoomSpeed = 1.1;
  controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_ROTATE };
  function placeCamera(target, az = Math.PI / 4) {
    controls.target.copy(target);
    camera.position.set(target.x + Math.sin(POLAR) * Math.sin(az) * 150, target.y + Math.cos(POLAR) * 150,
      target.z + Math.sin(POLAR) * Math.cos(az) * 150);
    camera.lookAt(target);
  }
  placeCamera(HOME);
  // 視錐：寬度要容納左右兩座附屬島（半寬約 37），高度至少 17；窄螢幕略為裁切兩翼
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    const narrow = w < 768, aspect = w / h;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, narrow ? 1.5 : 2));
    renderer.setSize(w, h, false);
    const half = Math.max(17, (narrow ? 29 : 37.5) / aspect);
    camera.left = -half * aspect; camera.right = half * aspect; camera.top = half; camera.bottom = -half;
    camera.updateProjectionMatrix(); requestRender();
  }
  const ro = new ResizeObserver(resize);
  ro.observe(stage);
  resize();

  // 飛行：平移 target（相機跟著平移）並調整 zoom
  let fly = null;
  function flyTo(target, zoom) {
    const from = controls.target.clone(), z0 = camera.zoom;
    if (!motion()) {
      const off = camera.position.clone().sub(controls.target);
      controls.target.copy(target); camera.position.copy(target).add(off);
      camera.zoom = zoom; camera.updateProjectionMatrix(); controls.update(); requestRender(); return;
    }
    fly = { from, to: target.clone(), z0, z1: zoom, t0: performance.now(), dur: 750 };
    requestRender();
  }
  function stepFly(now) {
    if (!fly) return false;
    const k = Math.min(1, (now - fly.t0) / fly.dur), e = 1 - Math.pow(1 - k, 3);
    const off = camera.position.clone().sub(controls.target);
    controls.target.lerpVectors(fly.from, fly.to, e);
    camera.position.copy(controls.target).add(off);
    camera.zoom = fly.z0 + (fly.z1 - fly.z0) * e; camera.updateProjectionMatrix();
    if (k >= 1) fly = null;
    return true;
  }

  /* ── 拾取與提示 ── */
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  const tip = $('islTip');
  function pickAt(cx, cy) {
    const r = canvas.getBoundingClientRect();
    ndc.set((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hit = ray.intersectObjects(picks, false)[0];
    return hit ? hit.object.userData.stem : null;
  }
  let hover = null, down = null;
  function showTip(stem) {
    if (stem === hover) { if (stem) placeTip(stem); return; }
    hover = stem;
    canvas.classList.toggle('is-hover', !!stem);
    if (!stem) { tip.classList.remove('show'); return; }
    const p = BY[stem];
    tip.replaceChildren(Object.assign(document.createElement('b'), { textContent: p.code }), document.createTextNode(p.title));
    tip.classList.add('show'); placeTip(stem);
  }
  function placeTip(stem) {
    const b = B[stem]; v3.set(b.s.x, b.top + 1.4, b.s.z).project(camera);
    tip.style.left = ((v3.x + 1) / 2 * canvas.clientWidth) + 'px';
    tip.style.top = ((1 - v3.y) / 2 * canvas.clientHeight) + 'px';
  }
  canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointermove', e => {
    if (e.pointerType === 'mouse' && !e.buttons) showTip(pickAt(e.clientX, e.clientY));
  });
  canvas.addEventListener('pointerleave', () => showTip(null));
  canvas.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) { down = null; return; }
    down = null;
    const stem = pickAt(e.clientX, e.clientY);
    if (stem) {
      select(stem, { trigger: canvas });
      const it = items.get(stem);
      if (it && window.innerWidth >= 768) {   // 側欄捲到對應項目（不用 scrollIntoView）
        const list = $('islList');
        list.scrollTop = it.li.offsetTop - list.clientHeight / 2;
      }
    } else closePanel();
  });
  canvas.addEventListener('keydown', e => {
    const step = Math.PI / 12;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const off = camera.position.clone().sub(controls.target);
      off.applyAxisAngle(new THREE.Vector3(0, 1, 0), e.key === 'ArrowLeft' ? -step : step);
      camera.position.copy(controls.target).add(off); controls.update(); requestRender(); e.preventDefault();
    } else if (e.key === '+' || e.key === '=' || e.key === '-' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      const zin = e.key === '+' || e.key === '=' || e.key === 'ArrowUp';
      camera.zoom = Math.min(controls.maxZoom, Math.max(controls.minZoom, camera.zoom * (zin ? 1.2 : 1 / 1.2)));
      camera.updateProjectionMatrix(); requestRender(); e.preventDefault();
    }
  });
  controls.addEventListener('change', () => { if (hover) placeTip(hover); requestRender(); });

  /* ── 繪製迴圈：有動畫或互動才畫；頁面不可見或畫布捲出視窗時停止動畫 ── */
  const animating = () => motion() && onScreen && document.visibilityState === 'visible';
  function requestRender() { need = true; if (!raf && alive) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0; if (!alive) return;
    const flying = stepFly(now);
    const moved = controls.update();
    const anim = animating();
    if (anim) { const t = now / 1000; anims.forEach(f => f(t)); }
    if (need || anim || flying || moved) { renderer.render(world, camera); need = false; }
    if (anim || flying || moved) raf = requestAnimationFrame(frame);
  }
  new IntersectionObserver(es => { onScreen = es[0].isIntersecting; requestRender(); }).observe(stage);
  document.addEventListener('visibilitychange', requestRender);
  reduceMotion.addEventListener('change', () => { controls.enableDamping = motion(); requestRender(); });
  anims.forEach(f => f(1.7));          // 靜態姿勢（減少動態時也看得出噴泉、帆船）
  if (selected) marker.position.y = B[selected].top + 1.9;
  requestRender();

  /* ── 對外介面 ── */
  return {
    select(stem, doFly) {
      if (selected) B[selected].g.scale.setScalar(1);
      refs.forEach(r => { B[r].refRing.visible = false; });
      selected = stem && B[stem] ? stem : null;
      refs = selected ? BY[selected].refs.filter(r => B[r]) : [];
      refs.forEach(r => { B[r].refRing.visible = true; });
      marker.visible = !!selected;
      if (doFly) showTip(null);              // 從列表選取時，收起滑鼠留下的提示
      if (selected) {
        const b = B[selected];
        marker.position.set(b.s.x, b.top + 1.9, b.s.z);
        b.g.scale.setScalar(1.06);
        if (doFly) flyTo(new THREE.Vector3(b.s.x, b.s.y, b.s.z), Math.max(camera.zoom, 2.1));
      }
      requestRender();
    },
    flyToIsle(grp) {
      const I = ISLE_GEO[grp]; if (!I) return;
      flyTo(new THREE.Vector3(I.x, GROUND, I.z), grp === 'core' ? 1.45 : 2.2);
    },
    reset() { flyTo(HOME.clone(), 1); },
    updateTrail() {
      PAGES.forEach(p => {
        const b = B[p.stem], done = !!trail.done[p.stem], visited = !!trail.visited[p.stem];
        b.flag.visible = done; b.visitRing.visible = visited || done;
        b.visitRing.material = done ? GLOW_DONE : GLOW_VISIT;
      });
      requestRender();
    },
    dispose() { alive = false; ro.disconnect(); controls.dispose(); renderer.dispose(); },
    // 給 tools/browser_check.js 用：建築在畫布上的像素位置（點擊測試）
    screenPos(stem) {
      const b = B[stem]; if (!b) return null;
      v3.set(b.s.x, b.s.y + (b.top - b.s.y) * .45, b.s.z).project(camera);
      const r = canvas.getBoundingClientRect();
      return { x: r.left + (v3.x + 1) / 2 * r.width, y: r.top + (1 - v3.y) / 2 * r.height };
    },
  };

  function badge(text, bg) {
    const c = document.createElement('canvas'); c.width = 128; c.height = 72;
    const g = c.getContext('2d');
    g.fillStyle = bg; g.strokeStyle = '#fffdf7'; g.lineWidth = 6;
    g.beginPath(); g.roundRect(5, 5, 118, 62, 28); g.fill(); g.stroke();
    g.fillStyle = '#ffffff'; g.font = '700 36px "JetBrains Mono", ui-monospace, monospace';
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, 64, 38);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
    return t;
  }
}

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
