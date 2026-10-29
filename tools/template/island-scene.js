/* 3D 群島的場景層：黏土微縮風。由 island.js 的 initScene() 呼叫 buildWorld()。
 *
 * 做法（全部程序化，沒有模型或圖檔）：
 *   - 島：不規則輪廓 → 分層倒角擠出（沙底、深崖帶、草頂；11 深度學習多一層高地），外圈淺水與浪花環
 *   - 道具：PartKit 收集零件（box／圓角 box／cyl／cone／sphere／rock／prism），最後依種類合併成
 *     InstancedMesh 並逐實例上色；靜態物件投影，陰影只烘一次（shadowMap.autoUpdate = false）
 *   - 會動的東西（噴泉、小人、帆船、鳥、雲）不投影，小人與船用假陰影圓盤
 *   - 標籤是 HTML，每次繪製時投影定位，依優先序避讓；放大後才展開先備單元的標籤
 * 本檔與 island.js 共用頂層名稱：PAGES、BY、ISLES、items、trail、select、closePanel、$、reduceMotion。
 */
function buildWorld(THREE, addons, renderer, stage, canvas) {
  const { OrbitControls, RoundedBoxGeometry } = addons;
  const motion = () => !reduceMotion.matches;
  const narrow = () => stage.clientWidth < 768;
  const rnd = mulberry32(524);
  const SQ = Math.SQRT1_2;
  // 初始視角的螢幕座標（u 往右、v 往前＝畫面下方）→ 世界座標 xz
  const toWorld = (u, v) => ({ x: (u + v) * SQ, z: (v - u) * SQ });
  const world = new THREE.Scene();
  const anims = [];          // 地標小動畫 (t) => void
  const life = [];           // 生活感動畫 (t, dt) => void；效能不足時整組停用
  let need = true, raf = 0, onScreen = true, alive = true, lowPower = false;

  /* ── 色盤：低彩度的黏土色；本站的森林綠、深藍、米白作為重點色 ── */
  const C = {
    grass: '#b7cd92', grass2: '#a7c286', grass3: '#c3d59f', sand: '#eedbb0', cliff: '#dcc39a', cliffDark: '#c2a477',
    foam: '#fbfaf2', shallow: '#bfe0d6',
    cream: '#fff4de', wall: '#f5e6cb', wall2: '#efdcc0', peach: '#f0c7a5', roof: '#b9563f', roofDark: '#924231',
    roofNavy: '#3f5b80', roofGreen: '#3f7f61',
    leaf: '#9fb889', leaf2: '#8fae86', leaf3: '#7c9a76', pine: '#7b997c', pine2: '#68876c',
    wood: '#ab875d', woodDark: '#7a5c3e', stone: '#dacdb6', stoneDark: '#b6a78c', ink: '#4f5a55',
    glass: '#8cbcbc', gold: '#f2d488', white: '#fffcf3', navy: '#2f4566', forest: '#1a6b4a',
    red: '#b9654f', blue: '#5d7b93', blueL: '#c3d0dc', redL: '#ebc7bb', amber: '#d6a35c', teal: '#5aa39a',
  };
  const DAY = { bg: '#a9d0c7', hemiSky: '#fff4dc', hemiGround: '#7d9d8f', hemi: 1.3, sun: '#ffe4c4', sunI: 2.9, fill: .45, sea: '#ffffff', exposure: 1.0 };
  const NIGHT = { bg: '#1f2e44', hemiSky: '#9fb2da', hemiGround: '#2a3a52', hemi: .85, sun: '#c3cff5', sunI: .55, fill: .18, sea: '#56708f', exposure: 1.15 };

  /* ── Renderer ── */
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, narrow() ? 1.25 : 1.6));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;      // r18x 起 PCF 以 shadow.radius 柔化
  renderer.shadowMap.autoUpdate = false;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = DAY.exposure;
  world.background = new THREE.Color(DAY.bg);
  world.fog = new THREE.Fog(DAY.bg, 150, 300);       // 只讓最遠的外海淡出

  const std = (color, extra) => new THREE.MeshStandardMaterial({ color, roughness: 1, metalness: 0, ...extra });
  const basic = (color, extra) => new THREE.MeshBasicMaterial({ color, ...extra });

  /* ═════════ PartKit：零件 → InstancedMesh ═════════ */
  const prismGeo = (() => {
    const tri = new THREE.Shape();
    tri.moveTo(-.5, -.5); tri.lineTo(.5, -.5); tri.lineTo(0, .5); tri.closePath();
    const g = new THREE.ExtrudeGeometry(tri, { depth: 1, bevelEnabled: false });
    g.translate(0, 0, -.5); g.computeVertexNormals(); return g;
  })();
  const GEO = {
    box: new THREE.BoxGeometry(1, 1, 1),
    round: new RoundedBoxGeometry(1, 1, 1, 2, .14),
    cyl: new THREE.CylinderGeometry(.5, .5, 1, 12),
    cone: new THREE.ConeGeometry(.5, 1, 10),
    sphere: new THREE.SphereGeometry(.5, 12, 8),
    rock: new THREE.DodecahedronGeometry(.5, 0),
    prism: prismGeo,
    torus: new THREE.TorusGeometry(.5, .12, 8, 22),
  };
  const kitMat = std('#ffffff', { roughness: .92 });
  const glowMat = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .6, emissive: '#ffc46b', emissiveIntensity: 0 });
  const parts = [];
  const lamps = [];          // 夜間光暈的位置
  const ao = [];             // 接觸暗部（假環境光遮蔽）：[x, y, z, r]
  // y 一律是「底面高度」；rx/ry/rz 以 YXZ 順序套用（先轉向、再俯仰）
  function part(kind, x, y, z, w, h, d, color, o = {}) {
    parts.push({ kind, x, y, z, w, h, d, color, rx: o.rx || 0, ry: o.ry || 0, rz: o.rz || 0, glow: !!o.glow });
  }
  // 以 (ox,oz) 為原點、轉 rot、縮放 s 的區域座標畫零件
  function at(ox, oy, oz, rot = 0, s = 1) {
    const c = Math.cos(rot), sn = Math.sin(rot);
    const f = (kind, x, y, z, w, h, d, color, o = {}) =>
      part(kind, ox + (x * c + z * sn) * s, oy + y * s, oz + (-x * sn + z * c) * s, w * s, h * s, d * s, color,
        { ...o, ry: (o.ry || 0) + rot });
    f.ao = (x, z, r) => ao.push([ox + (x * c + z * sn) * s, oy, oz + (-x * sn + z * c) * s, r * s]);
    return f;
  }
  // 在畫筆 p 的區域座標裡再疊一層平移／旋轉／縮放
  function sub(p, ox, oz, rot = 0, s = 1) {
    const c = Math.cos(rot), sn = Math.sin(rot);
    const f = (kind, x, y, z, w, h, d, color, o = {}) =>
      p(kind, ox + (x * c + z * sn) * s, y * s, oz + (-x * sn + z * c) * s, w * s, h * s, d * s, color, { ...o, ry: (o.ry || 0) + rot });
    f.ao = (x, z, r) => p.ao && p.ao(ox + (x * c + z * sn) * s, oz + (-x * sn + z * c) * s, r * s);
    return f;
  }
  function flushParts() {
    const groups = new Map();
    parts.forEach(p => { const k = p.kind + (p.glow ? '|g' : ''); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(p); });
    const o = new THREE.Object3D(); o.rotation.order = 'YXZ';
    const col = new THREE.Color();
    groups.forEach((list, k) => {
      const glow = k.endsWith('|g');
      const mesh = new THREE.InstancedMesh(GEO[list[0].kind], glow ? glowMat : kitMat, list.length);
      list.forEach((p, i) => {
        o.position.set(p.x, p.y + p.h / 2, p.z); o.rotation.set(p.rx, p.ry, p.rz); o.scale.set(p.w, p.h, p.d);
        o.updateMatrix(); mesh.setMatrixAt(i, o.matrix); mesh.setColorAt(i, col.set(p.color));
      });
      mesh.castShadow = !glow; mesh.receiveShadow = true;
      mesh.computeBoundingSphere();
      world.add(mesh);
    });
    parts.length = 0;
  }

  /* ── 共用道具配方（p 是 part 或 at(...) 回傳的畫筆）── */
  const LEAVES = [C.leaf, C.leaf2, C.leaf3];
  // 畫筆外加一個「記錄接觸暗部」的通道：p.ao(x, z, r)
  function tree(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .75 * s);
    p('cyl', x, 0, z, .16 * s, 1.0 * s, .16 * s, C.woodDark);
    [[-.24, .75, .08, .9], [.26, .9, .05, .82], [0, 1.18, -.1, .8], [-.05, .86, -.28, .74]].forEach(([dx, dy, dz, d], i) =>
      p('sphere', x + dx * s, dy * s, z + dz * s, d * s, d * .92 * s, d * s, LEAVES[(k + i) % 3]));
  }
  function pine(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .7 * s);
    p('cyl', x, 0, z, .13 * s, .7 * s, .13 * s, C.woodDark);
    for (let i = 0; i < 3; i++) p('cone', x, (.45 + i * .42) * s, z, (1.05 - i * .24) * s, .95 * s, (1.05 - i * .24) * s, (i + k) % 2 ? C.pine : C.pine2);
  }
  function bush(p, x, z, s = 1, k = 0) {
    p.ao && p.ao(x, z, .55 * s);
    p('sphere', x, 0, z, .62 * s, .46 * s, .56 * s, LEAVES[k % 3]);
    p('sphere', x + .26 * s, 0, z + .12 * s, .42 * s, .34 * s, .4 * s, LEAVES[(k + 1) % 3]);
  }
  function flowers(p, x, z, k = 0) {
    const petals = ['#f2b8a0', '#f7e1b5', '#e9967a', '#fff4de', '#d9a0c0'];
    for (let i = 0; i < 5; i++) {
      const a = i * 1.3 + k, r = .28 + (i % 2) * .12;
      p('sphere', x + Math.cos(a) * r, 0, z + Math.sin(a) * r, .2, .16, .2, C.leaf2);
      p('sphere', x + Math.cos(a) * r, .1, z + Math.sin(a) * r, .13, .12, .13, petals[(i + k) % petals.length]);
    }
  }
  function rock(p, x, z, s = 1) {
    p('rock', x, -.05 * s, z, .7 * s, .5 * s, .6 * s, C.stoneDark, { ry: rnd() * 6 });
    p('rock', x + .35 * s, -.05 * s, z + .2 * s, .4 * s, .3 * s, .4 * s, C.stone, { ry: rnd() * 6 });
  }
  function lamp(p, x, z) {
    p('cyl', x, 0, z, .12, .12, .12, C.ink);
    p('cyl', x, 0, z, .06, 1.35, .06, C.ink);
    p('sphere', x, 1.3, z, .22, .22, .22, '#ffe9b8', { glow: true });
    p('cone', x, 1.48, z, .3, .16, .3, C.ink);
    return [x, 1.42, z];
  }
  function bench(p, x, z, ry = 0) {
    const q = at(x, 0, z, ry);
    q('box', 0, .32, 0, .9, .07, .32, C.wood); q('box', 0, .45, -.14, .9, .26, .06, C.wood);
    q('box', -.38, 0, 0, .07, .32, .28, C.woodDark); q('box', .38, 0, 0, .07, .32, .28, C.woodDark);
  }
  function cottage(p, x, z, ry, roofC = C.roof, wallC = C.wall, s = 1) {
    const q = sub(p, x, z, ry, s);
    q.ao(0, 0, 1.25);
    q('round', 0, -.02, 0, 1.62, .14, 1.38, C.stoneDark);
    q('round', 0, 0, 0, 1.5, 1.05, 1.25, wallC);
    q('prism', 0, 1.0, 0, 1.75, .78, 1.45, roofC);
    q('box', .45, 1.25, -.25, .26, .62, .26, C.stoneDark);
    q('round', 0, 0, .6, .36, .66, .08, C.woodDark);
    [-.45, .45].forEach(dx => { q('box', dx, .38, .615, .38, .36, .04, C.white); q('box', dx, .42, .62, .3, .28, .05, '#ffe1a0', { glow: true }); });
    q('box', 0, .99, .7, 1.8, .06, .08, C.white);
    q('box', -.76, .42, 0, .05, .28, .3, '#ffe1a0', { glow: true });
  }
  function crate(p, x, z, s = 1, c = C.wood) { p('round', x, 0, z, .5 * s, .5 * s, .5 * s, c, { ry: rnd() }); }

  /* ═════════ 島工廠：分層倒角擠出 ═════════ */
  const M = {
    grass: std(C.grass), grass2: std(C.grass2), grass3: std(C.grass3), sand: std(C.sand),
    cliff: std(C.cliff), cliffDark: std(C.cliffDark),
    foam: basic(C.foam, { transparent: true, opacity: .6, depthWrite: false, side: THREE.DoubleSide }),
    shallow: basic(C.shallow, { transparent: true, opacity: .5, depthWrite: false, side: THREE.DoubleSide }),
  };
  const BASE_H = 1.0, BEVEL = .08, GROUND = BASE_H + BEVEL;
  function outline(seed, radius, wobble = .17, n = 72) {
    const r = mulberry32(seed);
    const hs = [[2, .45], [3, .3], [4, .15], [7, .1]].map(([f, w]) => [f, w, r() * Math.PI * 2]);
    // 一到兩個小灣：在隨機方向往內凹，打破圓餅輪廓
    const bays = Array.from({ length: 1 + Math.floor(r() * 2) }, () => [r() * Math.PI * 2, .12 + r() * .1]);
    return Array.from({ length: n }, (_, i) => {
      const a = i / n * Math.PI * 2;
      let k = 1 + wobble * hs.reduce((s, [f, w, ph]) => s + w * Math.sin(f * a + ph), 0);
      bays.forEach(([b, d]) => { const t = Math.atan2(Math.sin(a - b), Math.cos(a - b)); k -= d * Math.exp(-t * t / .045); });
      return [Math.cos(a) * radius * k, Math.sin(a) * radius * k];
    });
  }
  const scaled = (pts, s, inset = 0) => pts.map(([x, z]) => {
    const r = Math.hypot(x, z), k = inset ? Math.max(r - inset, r * .05) / r : 1;
    return [x * s * k, z * s * k];
  });
  const shapeOf = pts => {                 // shape 的 y＝世界的 -z（rotateX(-π/2) 之後對回 z）
    const sh = new THREE.Shape();
    pts.forEach(([x, z], i) => (i ? sh.lineTo(x, -z) : sh.moveTo(x, -z)));
    sh.closePath(); return sh;
  };
  function slab(pts, depth, mats, y) {
    const g = new THREE.ExtrudeGeometry(shapeOf(pts), { depth, bevelEnabled: true, bevelThickness: BEVEL, bevelSize: .1, bevelSegments: 2, curveSegments: 4 });
    g.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, mats); m.position.y = y; m.castShadow = true; m.receiveShadow = true; return m;
  }
  function ring(pts, inner, outer, mat, y) {
    const sh = shapeOf(scaled(pts, outer));
    const hole = new THREE.Path();
    [...scaled(pts, inner)].reverse().forEach(([x, z], i) => (i ? hole.lineTo(x, -z) : hole.moveTo(x, -z)));
    sh.holes.push(hole);
    const g = new THREE.ShapeGeometry(sh, 2); g.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(g, mat); m.position.y = y; m.renderOrder = 1; return m;
  }
  const isles = [];
  function makeIsle({ u, v, radius, seed, grass = 'grass', highland = 0 }) {
    const { x, z } = toWorld(u, v);
    const pts = outline(seed, radius);
    const g = new THREE.Group(); g.position.set(x, 0, z);
    g.add(ring(pts, 1.13, 1.19, M.foam, .05));
    g.add(slab(scaled(pts, 1.12), .2, [M.sand, M.sand], -.14));
    g.add(slab(scaled(pts, 1.0), .34, [M.cliffDark, M.cliffDark], 0));
    g.add(slab(scaled(pts, 1, .07), BASE_H, [M[grass], M.cliff], 0));
    let top = GROUND;
    if (highland) {
      g.add(slab(scaled(pts, highland, .05), 1.0, [M.grass2, M.cliff], GROUND));
      top = GROUND + 1.0 + BEVEL;
    }
    world.add(g);
    const angR = a => {                    // 該方向的海岸半徑（線性內插輪廓點）
      const n = pts.length, k = ((a / (Math.PI * 2)) % 1 + 1) % 1 * n, i = Math.floor(k), f = k - i;
      const [x0, z0] = pts[i % n], [x1, z1] = pts[(i + 1) % n];
      return Math.hypot(x0, z0) * (1 - f) + Math.hypot(x1, z1) * f;
    };
    const isle = { x, z, radius, pts, top, angR, gaps: [] };
    isle.inside = (wx, wz, m = .8) => Math.hypot(wx - x, wz - z) < angR(Math.atan2(wz - z, wx - x)) * m;
    isles.push(isle);
    return isle;
  }

  /* ═════════ 佈局（螢幕座標）═════════ */
  const core = PAGES.filter(p => p.grp === 'core');
  // 11 章蛇形三列：01–04 前排往右、05–08 中排往左、09–11 後排往右；11（補充）在高地
  const CORE_UV = [[-16, 12.5], [-6.5, 13.6], [3, 12.2], [12.5, 13.4], [18.5, 1], [8.8, -.4], [-.8, 1], [-10.6, -.2],
    [-7.5, -13], [2.2, -12.2], [12.2, -13.6]];
  const SAT = { pre: { u: -26, v: 19, r: 5.6, seed: 41 }, statistics: { u: -24.5, v: -9, r: 7.2, seed: 22 },
    appendix: { u: 26, v: -9.5, r: 7.2, seed: 57 } };
  const SLOT = {};       // stem → { isle, x, z, y(base), top(地標頂), anchor }
  core.forEach((p, i) => {
    const [u, v] = CORE_UV[i] || [i * 8 - 40, 22];
    const isle = makeIsle({ u, v, radius: p.stem === 'deep_learning' ? 4.0 : 3.55, seed: 100 + i * 7, grass: i % 3 === 1 ? 'grass2' : 'grass',
      highland: p.stem === 'deep_learning' ? .55 : 0 });
    SLOT[p.stem] = { isle, x: isle.x, z: isle.z, y: isle.top };
  });
  const SAT_ISLE = {};
  Object.entries(SAT).forEach(([grp, s]) => {
    SAT_ISLE[grp] = makeIsle({ u: s.u, v: s.v, radius: s.r, seed: s.seed, grass: grp === 'statistics' ? 'grass2' : grp === 'pre' ? 'grass3' : 'grass' });
  });
  // 附屬島上各單元的位置（以初始視角排：左到右、上到下）
  const UNIT_UV = {
    pre: [[-2.2, -1.6], [2.9, 2.4], [1.6, -2.3]],
    // 六間屋子錯落圍著島中央的地標（閱讀順序仍是左到右、上到下）
    statistics: [[-4.1, -2.2], [-.3, -4.4], [3.9, -2.6], [-4.0, 2.5], [.4, 4.3], [4.2, 2.1]],
    appendix: [[-4.0, -2.5], [.3, -4.4], [4.1, -2.2], [-4.2, 2.2], [-.3, 4.4], [3.9, 2.6]],
  };
  ['pre', 'statistics', 'appendix'].forEach(grp => {
    const I = SAT_ISLE[grp];
    PAGES.filter(p => p.grp === grp).forEach((p, i) => {
      const [du, dv] = UNIT_UV[grp][i] || [(i % 3 - 1) * 2.5, 0];
      const d = toWorld(du, dv);
      SLOT[p.stem] = { isle: I, x: I.x + d.x, z: I.z + d.z, y: I.top };
    });
  });

  /* ── 拱橋：二次貝茲，木板兩色交替、細扶手、每 3 片一根柱 ── */
  const bridges = [];
  function bridge(A, B) {
    const dx = B.x - A.x, dz = B.z - A.z, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L;
    const aA = Math.atan2(uz, ux), aB = Math.atan2(-uz, -ux);
    const s0 = A.angR(aA) * .9, s1 = L - B.angR(aB) * .9;
    A.gaps.push(aA); B.gaps.push(aB);
    const p0 = new THREE.Vector3(A.x + ux * s0, A.top - .04, A.z + uz * s0);
    const p2 = new THREE.Vector3(A.x + ux * s1, B.top - .04, A.z + uz * s1);
    const p1 = p0.clone().lerp(p2, .5); p1.y = Math.max(p0.y, p2.y) + Math.min(1.6, .22 * (s1 - s0) + .4);
    const curve = new THREE.QuadraticBezierCurve3(p0, p1, p2);
    const n = Math.max(4, Math.round(curve.getLength() / .3)), pts = curve.getSpacedPoints(n);
    const ry = Math.atan2(ux, uz);
    for (let i = 0; i < n; i++) {
      const a = pts[i], b = pts[i + 1], h = Math.hypot(b.x - a.x, b.z - a.z), m = a.clone().lerp(b, .5);
      const rx = -Math.atan2(b.y - a.y, h);
      part('box', m.x, m.y - .035, m.z, 1.12, .07, h * .92, i % 3 ? C.wood : C.woodDark, { rx, ry });
      [-1, 1].forEach(side => {
        const ox = uz * .56 * side, oz = -ux * .56 * side;
        part('box', m.x + ox, m.y + .44, m.z + oz, .05, .05, h + .02, C.woodDark, { rx, ry });
        if (i % 3 === 0) part('cyl', m.x + ox, m.y - .1, m.z + oz, .08, .58, .08, C.woodDark);
      });
    }
    // 兩端在島上的一小段石板路，讓橋「接上」島
    [[A, -1, p0], [B, 1, p2]].forEach(([I, sgn, end]) => {
      for (let k = 1; k <= 3; k++) {
        const t = k * .45; part('cyl', end.x + ux * t * sgn, I.top - .02, end.z + uz * t * sgn, .5, .05, .5, '#e9dcc0', { ry: rnd() * 3 });
      }
    });
    bridges.push({ A, B, curve, pts });
  }
  const coreIsles = core.map(p => SLOT[p.stem].isle);
  for (let i = 0; i + 1 < coreIsles.length; i++) bridge(coreIsles[i], coreIsles[i + 1]);
  const nearestCore = I => coreIsles.reduce((b, c) => (Math.hypot(c.x - I.x, c.z - I.z) < Math.hypot(b.x - I.x, b.z - I.z) ? c : b));
  if (coreIsles.length) {
    bridge(SAT_ISLE.pre, coreIsles[0]);
    bridge(SAT_ISLE.statistics, nearestCore(SAT_ISLE.statistics));
    bridge(SAT_ISLE.appendix, nearestCore(SAT_ISLE.appendix));
  }
  const nearGap = (I, a, tol = .42) => I.gaps.some(g => Math.abs(Math.atan2(Math.sin(a - g), Math.cos(a - g))) < tol);

  /* ═════════ 地標 ═════════ */
  const FACE = Math.PI / 4;                       // 正面朝向初始視角
  const B = {};                                   // stem → { top, x, z, y, pickR, ... }
  const dyn = (geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); world.add(m); return m; };
  const LM = {};
  LM.introduction = (x, y, z) => {                // 觀測塔＋漂浮散點
    const q = at(x, y, z, FACE);
    q('round', 0, 0, 0, 1.9, .3, 1.9, C.stone);
    q('cyl', 0, .3, 0, 1.15, 2.7, 1.15, C.wall);
    q('cyl', 0, 1.2, 0, 1.2, .14, 1.2, C.stoneDark);
    q('cyl', 0, 3.0, 0, 1.8, .18, 1.8, C.wood);
    q('cyl', 0, 3.18, 0, 1.25, .55, 1.25, C.cream);
    q('cone', 0, 3.73, 0, 1.9, 1.05, 1.9, C.navy);
    q('box', 0, 3.3, .6, .34, .3, .06, '#ffe1a0', { glow: true });
    q('round', 0, .3, .58, .4, .7, .1, C.woodDark);
    const dots = new THREE.Group(); dots.position.set(x, y, z); world.add(dots);
    [C.red, C.navy, C.forest, C.amber, C.navy, C.red, C.forest, C.amber].forEach((c, i) => {
      const a = i / 8 * Math.PI * 2, m = new THREE.Mesh(GEO.sphere, std(c, { roughness: .7 }));
      m.scale.setScalar(.3); m.position.set(Math.cos(a) * 2.1, 1.3 + (i * .41) % 1.9, Math.sin(a) * 2.1); dots.add(m);
    });
    anims.push(t => { dots.rotation.y = t * .22; });
    return 4.8;
  };
  LM.statistical_learning = (x, y, z) => {        // 訓練／測試分岔路
    const q = at(x, y, z, FACE);
    q('cyl', 0, 0, 1.2, .9, .06, .9, '#e9dcc0'); q('cyl', 0, 0, .45, .9, .06, .9, '#e9dcc0');
    [[-.75, -.5], [-1.3, -1.2], [.75, -.5], [1.3, -1.2]].forEach(([a, b]) => q('cyl', a, 0, b, .85, .06, .85, '#e9dcc0'));
    q('cyl', 0, 0, -.05, .16, 2.7, .16, C.woodDark);
    q('round', .6, 2.05, -.05, 1.5, .44, .14, C.forest, { ry: -.3 });
    q('cone', 1.4, 2.05, -.05, .44, .44, .2, C.forest, { rz: -Math.PI / 2, ry: -.3 });
    q('round', -.55, 1.45, -.05, 1.35, .44, .14, C.amber, { ry: .3 });
    q('cone', -1.3, 1.45, -.05, .44, .44, .2, C.amber, { rz: Math.PI / 2, ry: .3 });
    [[-1.5, -1.5], [-1.15, -1.85], [-1.7, -1.95], [-1.35, -1.68]].forEach(([a, b], i) => q('round', a, i === 3 ? .42 : 0, b, .42, .42, .42, C.forest));
    q('round', 1.5, 0, -1.7, .42, .42, .42, C.amber);
    return 3.0;
  };
  LM.linear_regression = (x, y, z) => {           // 迴歸斜坡穿過散點
    const q = at(x, y, z, FACE);
    q('round', 0, 0, 0, 3.9, .26, 2.4, C.stone);
    q('round', 0, .9, 0, 4.0, .2, .82, C.navy, { rz: .38 });
    q('cyl', 1.25, .26, 0, .2, 1.5, .2, C.woodDark); q('cyl', -1.1, .26, 0, .2, .4, .2, C.woodDark);
    for (let i = 0; i < 10; i++) {
      const lx = -1.7 + i * .38, ly = 1.15 + Math.tan(.38) * lx + (rnd() - .5) * .9;
      q('sphere', lx, Math.max(.3, ly), (rnd() - .5) * 1.4 + (i % 2 ? .6 : -.6), .3, .3, .3, i % 2 ? C.red : C.forest);
    }
    return 2.6;
  };
  LM.classification = (x, y, z) => {              // 紅藍分類城門
    const q = at(x, y, z, FACE);
    q('round', -.85, 0, 0, 1.7, .08, 2.4, C.redL); q('round', .85, 0, 0, 1.7, .08, 2.4, C.blueL);
    q('round', -1.2, 0, 0, .95, 2.7, .95, C.red); q('round', 1.2, 0, 0, .95, 2.7, .95, C.blue);
    q('round', -.62, 2.6, 0, 1.3, .6, .95, C.red); q('round', .62, 2.6, 0, 1.3, .6, .95, C.blue);
    [-1.5, -.95, .95, 1.5].forEach(lx => q('round', lx, 3.2, 0, .34, .34, .95, lx < 0 ? C.red : C.blue));
    q('cone', 0, 3.2, 0, .4, .55, .4, C.gold);
    return 3.9;
  };
  LM.resampling_methods = (x, y, z) => {          // Bootstrap 噴泉：球不斷被「重抽」出來
    const q = at(x, y, z, FACE);
    q('cyl', 0, 0, 0, 3.3, .5, 3.3, C.stone); q('cyl', 0, .44, 0, 2.9, .06, 2.9, C.glass);
    q('cyl', 0, .5, 0, .45, 1.4, .45, C.wall); q('cyl', 0, 1.88, 0, 1.25, .3, 1.25, C.stone);
    const cols = [C.red, C.navy, C.forest, C.amber], balls = [];
    for (let i = 0; i < 12; i++) {
      const m = dyn(GEO.sphere, std(cols[i % 4], { roughness: .6 }), x, y, z); m.scale.setScalar(.28);
      balls.push({ m, a: i / 12 * Math.PI * 2 + i, ph: i / 12 });
    }
    const place = t => balls.forEach(({ m, a, ph }) => {
      const k = (t * .5 + ph) % 1, r = .3 + 1.05 * k;
      m.position.set(x + Math.cos(a) * r, y + 2.2 + 2.0 * k - 2.6 * k * k, z + Math.sin(a) * r);
    });
    place(.4); anims.push(place);
    return 3.0;
  };
  LM.model_selection = (x, y, z) => {             // 修剪花園：灌木由高到低（係數往 0 收縮）
    const q = at(x, y, z, FACE);
    q('round', 0, 0, 0, 3.9, .16, 2.3, C.grass2);
    [1.8, 1.3, .92, .6, .34].forEach((h, i) => q('round', -1.5 + i * .75, .16, 0, .62, h, .95 + h * .2, i % 2 ? C.leaf : C.leaf3));
    [-1.95, 1.95].forEach(lx => [-1.12, 1.12].forEach(lz => q('cyl', lx, .16, lz, .12, .5, .12, C.woodDark)));
    q('box', 0, .56, 1.12, 3.9, .07, .07, C.woodDark); q('box', 0, .56, -1.12, 3.9, .07, .07, C.woodDark);
    q('round', 1.5, .16, -.75, .5, .06, .3, C.ink); q('box', 1.75, .2, -.75, .3, .04, .08, C.stoneDark);
    return 2.2;
  };
  LM.beyond_linearity = (x, y, z) => {            // 樣條拱橋：曲線通過節點
    const q = at(x, y, z, FACE);
    q('round', -1.95, 0, 0, .75, .5, 1.6, C.stone); q('round', 1.95, 0, 0, .75, .5, 1.6, C.stone);
    const knots = [[-1.9, .3], [-1.1, 1.95], [-.2, 1.25], [.8, 2.55], [1.9, .3]];
    const c = Math.cos(FACE), s = Math.sin(FACE);
    [-.5, .5].forEach(lz => {
      const pts = knots.map(([lx, ly]) => new THREE.Vector3(x + lx * c + lz * s, y + ly, z - lx * s + lz * c));
      const tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, .17, 8), std(C.amber, { roughness: .8 }));
      tube.castShadow = true; tube.receiveShadow = true; world.add(tube);
      knots.slice(1, -1).forEach(([lx, ly]) => q('sphere', lx, ly - .2, lz, .42, .42, .42, C.navy));
    });
    return 3.0;
  };
  LM.tree_based_methods = (x, y, z) => {          // 決策樹森林：一片樹＝集成
    const p = at(x, y, z, FACE);
    [[0, 0, 1.3], [-1.3, .7, .95], [1.25, .8, 1.0], [-.85, -1.1, .85], [1.0, -1.0, .9], [0, 1.55, .78]].forEach(([lx, lz, s], i) =>
      (i % 2 ? tree : pine)(p, lx, lz, s, i));
    p('round', 0, 2.75, .2, .7, .36, .1, C.gold);
    return 3.2;
  };
  LM.support_vector_machines = (x, y, z) => {     // 最大間隔圍牆
    const q = at(x, y, z, FACE);
    q('round', 0, 0, 0, 4.1, .07, 3.0, '#e6dfcd');
    q('round', 0, .07, 0, .42, 1.35, 3.0, C.wall); q('round', 0, 1.4, 0, .6, .18, 3.1, C.stone);
    q('box', -1.0, .07, 0, .1, .04, 3.0, C.gold); q('box', 1.0, .07, 0, .1, .04, 3.0, C.gold);
    [[-1.1, -.9], [-1.55, .3], [-1.8, -.4], [-1.35, 1.0], [-1.85, .95]].forEach(([lx, lz]) => q('round', lx, .07, lz, .44, .44, .44, C.red));
    [[1.15, .6], [1.55, -.5], [1.85, .3], [1.4, -1.1], [1.8, 1.1]].forEach(([lx, lz]) => q('sphere', lx, .07, lz, .48, .48, .48, C.blue));
    return 2.2;
  };
  LM.unsupervised_learning = (x, y, z) => {       // 群聚廣場
    const q = at(x, y, z, FACE);
    q('cyl', 0, 0, 0, 4.0, .2, 4.0, C.stone); q('cyl', 0, .2, 0, 3.6, .03, 3.6, '#e9dcc0');
    [[C.red, -.85, .55], [C.navy, .9, .45], [C.forest, 0, -.95]].forEach(([c, cx, cz], j) => {
      for (let i = 0; i < 5; i++) {
        const a = i / 5 * Math.PI * 2 + j;
        q('sphere', cx + Math.cos(a) * .42, .23 + (i % 2) * .28, cz + Math.sin(a) * .42, .42, .42, .42, c);
      }
      q('cone', cx, .23, cz, .28, .7, .28, C.gold);
    });
    return 1.9;
  };
  LM.deep_learning = (x, y, z) => {               // 神經網路高塔（補充，高地）
    const q = at(x, y, z, FACE);
    q('cyl', 0, 0, 0, 2.5, .35, 2.5, C.stone); q('cyl', 0, .35, 0, .5, 4.9, .5, C.wall);
    const layers = [5, 4, 4, 2], pulse = layers.map(() => new THREE.MeshStandardMaterial({ color: C.gold, roughness: .5, emissive: '#ffbf63', emissiveIntensity: .3 }));
    const nodes = [];
    layers.forEach((n, li) => {
      const ly = .95 + li * 1.15, r = 1.05 - li * .15;
      q('cyl', 0, ly - .22, 0, (r + .3) * 2, .14, (r + .3) * 2, C.navy);
      const row = [];
      for (let i = 0; i < n; i++) {
        const a = i / n * Math.PI * 2, m = dyn(GEO.sphere, pulse[li], x + Math.cos(a) * r, y + ly + .12, z + Math.sin(a) * r);
        m.scale.setScalar(.4); row.push(m.position.clone());
      }
      nodes.push(row);
    });
    const seg = [];
    for (let li = 0; li + 1 < nodes.length; li++) nodes[li].forEach(a => nodes[li + 1].forEach(b => seg.push(a, b)));
    world.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(seg), new THREE.LineBasicMaterial({ color: '#f7d774', transparent: true, opacity: .5 })));
    const crown = dyn(new THREE.IcosahedronGeometry(.42, 1), new THREE.MeshStandardMaterial({ color: '#fff1c2', emissive: '#ffcf70', emissiveIntensity: .8 }), x, y + 5.55, z);
    anims.push(t => {
      pulse.forEach((m, i) => { m.emissiveIntensity = .25 + .9 * Math.max(0, Math.sin(t * 2.2 - i * .9)); });
      crown.rotation.y = t * .5;
    });
    return 6.0;
  };
  // 啟航島：港口語彙
  LM['00a_why_code'] = (x, y, z) => {             // 燈塔
    const q = at(x, y, z, FACE);
    q('cyl', 0, 0, 0, 2.0, .35, 2.0, C.stone);
    [C.red, C.white, C.red, C.white].forEach((c, i) => q('cyl', 0, .35 + i * .75, 0, 1.25 - i * .12, .75, 1.25 - i * .12, c));
    q('cyl', 0, 3.35, 0, 1.25, .12, 1.25, C.navy);
    q('cyl', 0, 3.47, 0, .78, .55, .78, '#fff1c2', { glow: true });
    q('cone', 0, 4.02, 0, 1.15, .7, 1.15, C.navy);
    lamps.push([x, y + 3.75, z, 1.6, true]);      // 燈塔：只有光暈，不在地上畫光斑
    return 4.8;
  };
  LM['00b_setup'] = (x, y, z) => {                // 補給碼頭（伸出前岸）
    const q = at(x, y - .3, z, FACE);
    q('box', 0, 0, .6, 1.6, .12, 3.6, C.wood);
    [-1.1, .5, 2.1].forEach(lz => [-.7, .7].forEach(lx => q('cyl', lx, -1.2, lz, .16, 1.32, .16, C.woodDark)));
    crate(q, -.35, -.5, 1.4); crate(q, .35, -.2, 1.0, C.amber); crate(q, -.3, -.5, .9, C.navy);
    return 1.8;
  };
  LM['00c_ai_assisted'] = (x, y, z) => {          // 領航站
    const p = at(x, y, z, FACE);
    cottage(p, 0, 0, 0, C.navy, C.cream, 1.1);
    p('cyl', 1.1, 0, -.5, .08, 2.8, .08, C.woodDark);
    p('round', 1.48, 2.25, -.5, .7, .42, .05, C.forest);
    return 2.2;
  };
  const treehouse = i => (x, y, z) => {           // 統計森林島：樹屋
    const p = at(x, y, z, FACE), h = 1.45 + (i % 3) * .3;
    p('cyl', 0, 0, 0, .42, h + .6, .42, C.woodDark);
    p('sphere', -.35, h + .65, -.45, 1.9, 1.7, 1.9, LEAVES[i % 3]); p('sphere', .55, h + .95, -.6, 1.3, 1.2, 1.3, LEAVES[(i + 1) % 3]);
    p('cyl', 0, h, 0, 2.0, .14, 2.0, C.wood);
    p('round', 0, h + .14, .05, 1.05, .8, .9, C.wall);
    p('prism', 0, h + .92, .05, 1.25, .62, 1.05, i % 2 ? C.roofGreen : C.forest);
    p('box', 0, h + .3, .5, .3, .3, .05, '#ffe1a0', { glow: true });
    for (let k = 0; k < 4; k++) p('box', .78, .25 + k * h / 4, .5, .5, .06, .06, C.woodDark);
    return h + 2.0;
  };
  const workshop = i => (x, y, z) => {            // Python 工坊島：工坊小屋
    const p = at(x, y, z, FACE), roofs = [C.roofNavy, C.roof, C.roofGreen];
    cottage(p, 0, 0, 0, roofs[i % 3], i % 2 ? C.wall : C.wall2, 1.05);
    p('torus', -.45, .95, .72, .5, .5, .5, C.gold, { rx: 0 });
    return 2.3;
  };
  PAGES.filter(p => p.grp === 'statistics').forEach((p, i) => { LM[p.stem] = LM[p.stem] || treehouse(i); });
  PAGES.filter(p => p.grp === 'appendix').forEach((p, i) => { LM[p.stem] = LM[p.stem] || workshop(i); });
  const genericLM = (x, y, z) => { cottage(at(x, y, z, FACE), 0, 0, 0); return 2.2; };

  PAGES.forEach(p => {
    const s = SLOT[p.stem];
    const h = (LM[p.stem] || genericLM)(s.x, s.y, s.z);
    ao.push([s.x, s.y, s.z, p.grp === 'core' ? 2.0 : 1.3]);
    const isCore = p.grp === 'core';
    B[p.stem] = { x: s.x, y: s.y, z: s.z, top: s.y + h, isle: s.isle, pickR: isCore ? s.isle.radius * .95 : 1.35, isCore };
  });

  /* ── 每座島的裝飾：小屋、兩種樹、花、岩石、路燈、長椅；避開橋的方向，島心留給地標 ── */
  function decorate(I, { houses = 1, trees = 5, edgeOnly = false, avoid = [] } = {}) {
    const free = a => !nearGap(I, a);
    const spots = [];
    for (let k = 0; k < 18; k++) {
      const a = k / 18 * Math.PI * 2 + rnd() * .2;
      if (!free(a)) continue;
      spots.push(a);
    }
    const take = () => spots.splice(Math.floor(rnd() * spots.length), 1)[0];
    const pos = (a, f) => [I.x + Math.cos(a) * I.angR(a) * f, I.z + Math.sin(a) * I.angR(a) * f];
    const ok = (x, z) => avoid.every(([ax, az, r]) => Math.hypot(x - ax, z - az) > r);
    for (let h = 0; h < houses && spots.length; h++) {
      const a = take(), [x, z] = pos(a, .66);
      if (ok(x, z)) cottage(at(x, I.top, z, -a + Math.PI / 2), 0, 0, 0, [C.roof, C.roofNavy, C.roofGreen][(h + Math.round(x)) % 3], C.wall, .74 + rnd() * .14);
    }
    for (let t = 0; t < trees && spots.length; t++) {
      const a = take(), [x, z] = pos(a, edgeOnly ? .78 : .7 + rnd() * .12);
      if (!ok(x, z)) continue;
      (t % 2 ? pine : tree)(at(x, I.top, z), 0, 0, .6 + rnd() * .3, t);
    }
    for (let k = 0; k < 2 && spots.length; k++) { const [x, z] = pos(take(), .8); if (ok(x, z)) flowers(at(x, I.top, z), 0, 0, Math.round(x) + k); }
    for (let k = 0; k < 2 && spots.length; k++) { const [x, z] = pos(take(), .84); if (ok(x, z)) bush(at(x, I.top, z), 0, 0, .8 + rnd() * .3, k); }
    if (spots.length) { const [x, z] = pos(take(), .7); if (ok(x, z)) { lamp(at(x, I.top, z), 0, 0); lamps.push([x, I.top + 1.42, z]); } }
    for (let r = 0; r < 2; r++) { const a = rnd() * Math.PI * 2; if (!nearGap(I, a, .5)) rock(at(I.x + Math.cos(a) * I.angR(a) * 1.02, 0, I.z + Math.sin(a) * I.angR(a) * 1.02), 0, 0, .8 + rnd() * .5); }
  }
  coreIsles.forEach(I => decorate(I, { houses: 1, trees: 5, edgeOnly: true }));
  // 統計森林：密林；Python 工坊：小廣場、路燈與木箱；港口：幾棵樹與船
  {
    const I = SAT_ISLE.statistics, avoid = PAGES.filter(p => p.grp === 'statistics').map(p => [SLOT[p.stem].x, SLOT[p.stem].z, 2.0]);
    avoid.push([I.x, I.z, 2.4]);
    // 中央：常態分布拱門（統計森林島的地標）
    {
      const P = at(I.x, I.top, I.z, FACE), c = Math.cos(FACE), sn = Math.sin(FACE);
      P('cyl', 0, 0, 0, 3.6, .1, 3.6, C.stone); P.ao(0, 0, 1.8);
      const pts = []; for (let k = 0; k <= 24; k++) { const lx = -1.6 + k * 3.2 / 24; pts.push(new THREE.Vector3(I.x + lx * c, I.top + .15 + 2.4 * Math.exp(-lx * lx / .5), I.z - lx * sn)); }
      const arch = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, .16, 8), std(C.forest, { roughness: .8 }));
      arch.castShadow = true; arch.receiveShadow = true; world.add(arch);
      [-1.6, 1.6].forEach(lx => P('round', lx, 0, 0, .5, .3, .5, C.stoneDark));
    }
    for (let k = 0, n = 0; k < 400 && n < 34; k++) {
      const a = rnd() * Math.PI * 2, f = rnd() ** .6 * .9, x = I.x + Math.cos(a) * I.angR(a) * f, z = I.z + Math.sin(a) * I.angR(a) * f;
      if (nearGap(I, a, .35) && f > .5) continue;
      if (avoid.some(([ax, az, r]) => Math.hypot(x - ax, z - az) < r)) continue;
      (n % 3 ? pine : tree)(at(x, I.top, z), 0, 0, .55 + rnd() * .45, n); n++;
    }
    for (let k = 0; k < 4; k++) { const a = k * 1.6 + .4; if (!nearGap(I, a, .5)) rock(at(I.x + Math.cos(a) * I.angR(a) * 1.02, 0, I.z + Math.sin(a) * I.angR(a) * 1.02), 0, 0, 1); }
  }
  {
    const I = SAT_ISLE.appendix, P = at(I.x, I.top, I.z, FACE);
    // 中央：齒輪鐘塔工坊（Python 工坊島的地標）
    P('cyl', 0, 0, 0, 5.2, .05, 5.2, '#e9dcc0'); P.ao(0, 0, 1.6);
    P('round', 0, .05, 0, 1.7, 1.9, 1.7, C.wall2); P('prism', 0, 1.95, 0, 2.0, .9, 1.9, C.roofNavy);
    P('round', .55, 2.1, -.3, .38, 1.2, .38, C.stoneDark);
    P('torus', 0, 1.0, .9, 1.0, 1.0, .5, C.gold); P('cyl', 0, 1.42, .9, .25, .2, .25, C.gold, { rx: Math.PI / 2 });
    P('round', 0, .05, .86, .5, .8, .08, C.woodDark);
    lamp(P, 1.8, 1.6);
    lamps.push([I.x + 1.8 * Math.cos(FACE) + 1.6 * Math.sin(FACE), I.top + 1.42, I.z - 1.8 * Math.sin(FACE) + 1.6 * Math.cos(FACE)]);
    [[-1.6, 1.6], [1.7, -1.5]].forEach(([a, b], k) => bush(P, a, b, .9, k));
    [[-5.4, 0], [5.4, -.2], [0, 5.6], [-4.6, 4.6]].forEach(([du, dv], k) => {
      const w = toWorld(du, dv), x = I.x + w.x, z = I.z + w.z;
      if (I.inside(x, z, .85)) (k % 2 ? tree : pine)(at(x, I.top, z), 0, 0, .7, k);
    });
    [[2.2, .6], [-2.2, .4]].forEach(([du, dv]) => { const w = toWorld(du, dv); crate(at(I.x + w.x, I.top, I.z + w.z), 0, 0, 1); });
    for (let k = 0; k < 3; k++) { const a = k * 2.1 + 1; if (!nearGap(I, a, .5)) rock(at(I.x + Math.cos(a) * I.angR(a) * 1.02, 0, I.z + Math.sin(a) * I.angR(a) * 1.02), 0, 0, .9); }
  }
  {
    const I = SAT_ISLE.pre;
    [[-3.5, 1.6], [-.2, 3.7], [3.6, -1], [-3.2, -3.2]].forEach(([du, dv], k) => {
      const w = toWorld(du, dv), x = I.x + w.x, z = I.z + w.z;
      if (I.inside(x, z, .85)) (k % 2 ? pine : tree)(at(x, I.top, z), 0, 0, .7, k);
    });
    flowers(at(I.x, I.top, I.z), 0, 0, 3);
  }
  // 外圍的小沙洲與礁岩，替畫面收邊
  const framed = isles.slice();          // 取景只算主要島嶼；外圍沙洲可以出血
  const sandbars = [[-40, 2, 2.2], [37, 9, 2.6], [-12, 26, 1.8], [17, -26, 2.0], [-36, -26, 1.6], [40, -24, 1.6], [26, 24, 1.6]];
  sandbars.forEach(([u, v, r], k) => {
    const I = makeIsle({ u, v, radius: r, seed: 300 + k * 13, grass: 'grass3' });
    if (k % 2 === 0) tree(at(I.x, I.top, I.z), 0, 0, .7, k); else rock(at(I.x, I.top - .1, I.z), 0, 0, .9);
  });

  flushParts();
  // 接觸暗部：柔邊的深色圓盤，貼在地面上（不參與陰影）
  {
    const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(40,52,40,.55)'); gr.addColorStop(.55, 'rgba(40,52,40,.25)'); gr.addColorStop(1, 'rgba(40,52,40,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    const tex = new THREE.CanvasTexture(cv);
    const geo = new THREE.PlaneGeometry(1, 1); geo.rotateX(-Math.PI / 2);
    const mesh = new THREE.InstancedMesh(geo, new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, opacity: .55 }), ao.length);
    const o = new THREE.Object3D();
    ao.forEach(([x, y, z, r], i) => { o.position.set(x, y + .015, z); o.scale.set(r * 2.2, 1, r * 2.2); o.updateMatrix(); mesh.setMatrixAt(i, o.matrix); });
    mesh.renderOrder = 2; world.add(mesh);
  }

  /* ═════════ 海面：頂點起伏＋依離岸距離的淺深色 ═════════ */
  const SEA_DAY_SHALLOW = new THREE.Color('#acd8cd'), SEA_DAY_DEEP = new THREE.Color('#7fb4b4');
  const seaGeo = new THREE.PlaneGeometry(300, 300, 150, 150); seaGeo.rotateX(-Math.PI / 2);
  {
    const pos = seaGeo.attributes.position, cols = new Float32Array(pos.count * 3), c = new THREE.Color();
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), z = pos.getZ(i);
      let d = 1e9; isles.forEach(I => { d = Math.min(d, Math.hypot(x - I.x, z - I.z) - I.radius * 1.1); });
      const t = Math.min(1, Math.max(0, d / 12)), k = t * t * (3 - 2 * t);
      c.copy(SEA_DAY_SHALLOW).lerp(SEA_DAY_DEEP, k);
      cols[i * 3] = c.r; cols[i * 3 + 1] = c.g; cols[i * 3 + 2] = c.b;
    }
    seaGeo.setAttribute('color', new THREE.BufferAttribute(cols, 3));
  }
  const seaU = { uTime: { value: 0 } };
  const seaMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .55, metalness: 0 });
  seaMat.onBeforeCompile = sh => {
    sh.uniforms.uTime = seaU.uTime;
    sh.vertexShader = 'uniform float uTime;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n transformed.y += sin(position.x * .32 + uTime * .9) * .05 + cos(position.z * .27 + uTime * .7) * .05;');
  };
  const sea = new THREE.Mesh(seaGeo, seaMat); sea.position.y = -.02; sea.receiveShadow = true; world.add(sea);
  // 風格化短浪線
  const dash = new THREE.InstancedMesh(new RoundedBoxGeometry(1, .02, .1, 1, .04), basic('#ffffff', { transparent: true, opacity: .6, depthWrite: false, fog: false }), 46);
  const dashes = [];
  for (let k = 0, n = 0; k < 2000 && n < 46; k++) {
    const x = (rnd() - .5) * 110, z = (rnd() - .5) * 110;
    if (isles.some(I => Math.hypot(x - I.x, z - I.z) < I.radius * 1.7)) continue;
    dashes.push({ x, z, l: .8 + rnd() * 1.0, ph: rnd() * 6 }); n++;
  }
  const dObj = new THREE.Object3D();
  const placeDashes = t => {
    dashes.forEach((d, i) => {
      dObj.position.set(d.x + Math.sin(t * .25 + d.ph) * .6, .06, d.z + Math.cos(t * .2 + d.ph) * .3);
      dObj.rotation.set(0, FACE, 0);              // 與畫面水平方向平行 dObj.scale.set(d.l * (.75 + .25 * Math.sin(t * .6 + d.ph)), 1, 1);
      dObj.updateMatrix(); dash.setMatrixAt(i, dObj.matrix);
    });
    dash.count = dashes.length; dash.instanceMatrix.needsUpdate = true;
  };
  placeDashes(0); world.add(dash);
  life.push(t => { seaU.uTime.value = t; placeDashes(t); });

  /* ═════════ 燈光 ═════════ */
  const hemi = new THREE.HemisphereLight(DAY.hemiSky, DAY.hemiGround, DAY.hemi); world.add(hemi);
  const bounds = isles.reduce((b, I) => ({ minX: Math.min(b.minX, I.x - I.radius), maxX: Math.max(b.maxX, I.x + I.radius),
    minZ: Math.min(b.minZ, I.z - I.radius), maxZ: Math.max(b.maxZ, I.z + I.radius) }), { minX: 1e9, maxX: -1e9, minZ: 1e9, maxZ: -1e9 });
  const center = new THREE.Vector3((bounds.minX + bounds.maxX) / 2, 0, (bounds.minZ + bounds.maxZ) / 2);
  const sun = new THREE.DirectionalLight(DAY.sun, DAY.sunI);
  sun.position.set(center.x - 30, 55, center.z + 24); sun.target.position.copy(center);
  sun.castShadow = true;
  const SM = window.innerWidth < 768 ? 2048 : 4096;   // 陰影只烘一次，貼圖可以大一點
  sun.shadow.mapSize.set(SM, SM);
  const ext = Math.max(bounds.maxX - bounds.minX, bounds.maxZ - bounds.minZ) / 2 + 6;
  Object.assign(sun.shadow.camera, { left: -ext, right: ext, top: ext, bottom: -ext, near: 1, far: 160 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -.0005; sun.shadow.normalBias = .07; sun.shadow.radius = 2.5;
  world.add(sun, sun.target);
  const fill = new THREE.DirectionalLight('#d6ecf2', DAY.fill); fill.position.set(center.x + 40, 30, center.z - 50); world.add(fill);

  /* ═════════ 生活感：小人、帆船、鳥、雲 ═════════ */
  const blobMat = basic('#20343a', { transparent: true, opacity: .16, depthWrite: false });
  const blobGeo = new THREE.CircleGeometry(.34, 16); blobGeo.rotateX(-Math.PI / 2);
  function person(shirt, pants, skin, hair) {
    const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
    const m = c => std(c, { roughness: .8 });
    const limb = (c, x, y, w, h) => { const piv = new THREE.Group(); piv.position.set(x, y, 0); const b = new THREE.Mesh(GEO.round, m(c)); b.scale.set(w, h, w); b.position.y = -h / 2; piv.add(b); body.add(piv); return piv; };
    const legL = limb(pants, -.09, .42, .13, .42), legR = limb(pants, .09, .42, .13, .42);
    const torso = new THREE.Mesh(GEO.round, m(shirt)); torso.scale.set(.36, .42, .22); torso.position.y = .63; body.add(torso);
    const armL = limb(shirt, -.24, .8, .1, .36), armR = limb(shirt, .24, .8, .1, .36);
    const head = new THREE.Mesh(GEO.sphere, m(skin)); head.scale.setScalar(.3); head.position.y = 1.0; body.add(head);
    const cap = new THREE.Mesh(GEO.sphere, m(hair)); cap.scale.set(.32, .18, .32); cap.position.set(0, 1.08, -.02); body.add(cap);
    const blob = new THREE.Mesh(blobGeo, blobMat); blob.position.y = .02; g.add(blob);
    g.userData = { legL, legR, armL, armR, body };
    return g;
  }
  const people = [];
  const PALETTE = [['#c4553a', '#3f5b80'], ['#3f7f61', '#4f5a55'], ['#e7a33e', '#2f4566'], ['#4f78ab', '#7a5c3e'], ['#f0c7a5', '#3f7f61'], ['#fff4de', '#924231']];
  const SKIN = ['#f1c9a5', '#d9a77f', '#b98063', '#f6dcc0'], HAIR = ['#3b2a20', '#1f1d1c', '#7a5c3e', '#c9a46a'];
  bridges.forEach((b, i) => {
    if (people.length >= 11) return;
    const [sh, pa] = PALETTE[i % PALETTE.length];
    const g = person(sh, pa, SKIN[i % 4], HAIR[(i + 1) % 4]); g.scale.setScalar(.72); world.add(g);
    const path = [];
    const inA = b.pts[0].clone().lerp(new THREE.Vector3(b.A.x, b.pts[0].y, b.A.z), .45), inB = b.pts[b.pts.length - 1].clone().lerp(new THREE.Vector3(b.B.x, b.pts[b.pts.length - 1].y, b.B.z), .45);
    path.push(inA, ...b.pts, inB);
    const lens = [0]; for (let k = 1; k < path.length; k++) lens.push(lens[k - 1] + path[k].distanceTo(path[k - 1]));
    people.push({ g, path, lens, total: lens[lens.length - 1], s: rnd() * lens[lens.length - 1], dir: rnd() < .5 ? 1 : -1, wait: 0, speed: .75 + rnd() * .35 });
  });
  const pv = new THREE.Vector3();
  const walk = (t, dt) => people.forEach(P => {
    const u = P.g.userData;
    if (P.wait > 0) { P.wait -= dt; u.legL.rotation.x = u.legR.rotation.x = u.armL.rotation.x = 0; u.armR.rotation.x = Math.sin(t * 6) * .8 - .8; return; }
    P.s += P.dir * P.speed * dt;
    if (P.s > P.total || P.s < 0) { P.s = Math.max(0, Math.min(P.total, P.s)); P.dir *= -1; P.wait = 1 + rnd() * 2.5; }
    let k = 1; while (k < P.lens.length - 1 && P.lens[k] < P.s) k++;
    const f = (P.s - P.lens[k - 1]) / Math.max(1e-6, P.lens[k] - P.lens[k - 1]);
    pv.copy(P.path[k - 1]).lerp(P.path[k], f); P.g.position.copy(pv);
    const a = P.path[k], b0 = P.path[k - 1];
    P.g.rotation.y = Math.atan2((a.x - b0.x) * P.dir, (a.z - b0.z) * P.dir);
    const sw = Math.sin(t * 8 * P.speed) * .55;
    u.legL.rotation.x = sw; u.legR.rotation.x = -sw; u.armL.rotation.x = -sw * .8; u.armR.rotation.x = sw * .8;
    u.body.position.y = Math.abs(Math.sin(t * 8 * P.speed)) * .04;
  });
  walk(1.3, 0); life.push(walk);

  function sailboat(sail, hull) {
    const g = new THREE.Group();
    const h = new THREE.Mesh(GEO.round, std(hull, { roughness: .8 })); h.scale.set(.75, .35, 1.9); h.position.y = .12; g.add(h);
    const deck = new THREE.Mesh(GEO.round, std(C.wood)); deck.scale.set(.62, .08, 1.6); deck.position.y = .3; g.add(deck);
    const mast = new THREE.Mesh(GEO.cyl, std(C.woodDark)); mast.scale.set(.07, 2.0, .07); mast.position.y = 1.3; g.add(mast);
    const s = new THREE.Mesh(GEO.prism, std(sail, { roughness: .9, side: THREE.DoubleSide })); s.scale.set(.06, 1.6, 1.2); s.position.set(0, 1.35, -.2); g.add(s);
    const wake = new THREE.Mesh(new THREE.PlaneGeometry(.7, 2.6), basic('#ffffff', { transparent: true, opacity: .35, depthWrite: false }));
    wake.rotation.x = -Math.PI / 2; wake.position.set(0, .04, -2.1); g.add(wake);
    return g;
  }
  const boats = [[C.cream, C.navy, 46, 30, .05, 0], [C.redL, C.white, 46, 30, .05, Math.PI], [C.white, C.red, 9, 9, -.12, 1]].map(([s, h, a, b, w, ph], i) => {
    const g = sailboat(s, h); world.add(g);
    const c0 = i === 2 ? new THREE.Vector3(SAT_ISLE.pre.x, 0, SAT_ISLE.pre.z) : center.clone();
    return { g, a, b, w, ph, c0 };
  });
  const sail = t => boats.forEach(B0 => {
    const ang = t * B0.w + B0.ph, rot = -FACE;
    const lx = Math.cos(ang) * B0.a, lz = Math.sin(ang) * B0.b;
    const x = B0.c0.x + lx * Math.cos(rot) - lz * Math.sin(rot), z = B0.c0.z + lx * Math.sin(rot) + lz * Math.cos(rot);
    const dx = -Math.sin(ang) * B0.a * Math.sign(B0.w), dz = Math.cos(ang) * B0.b * Math.sign(B0.w);
    const wx = dx * Math.cos(rot) - dz * Math.sin(rot), wz = dx * Math.sin(rot) + dz * Math.cos(rot);
    B0.g.position.set(x, .05 + Math.sin(t * 1.4 + B0.ph) * .05, z);
    B0.g.rotation.set(Math.sin(t * 1.1 + B0.ph) * .04, Math.atan2(wx, wz), Math.sin(t * .9) * .05);
  });
  sail(2); life.push(sail);

  const birds = new THREE.Group(); world.add(birds);
  const birdMat = std('#fbfaf2', { roughness: .8 });
  const flock = Array.from({ length: 7 }, (_, i) => {
    const g = new THREE.Group();
    const body = new THREE.Mesh(GEO.sphere, birdMat); body.scale.set(.18, .14, .42); g.add(body);
    const wings = [-1, 1].map(s => { const piv = new THREE.Group(); const w = new THREE.Mesh(GEO.box, birdMat); w.scale.set(.6, .03, .22); w.position.x = .3 * s; piv.add(w); g.add(piv); return piv; });
    g.position.set((i % 3 - 1) * 1.1, (i % 2) * .4, -Math.floor(i / 2) * .9); birds.add(g);
    return { g, wings, ph: i * .7 };
  });
  const flapBirds = t => {
    const a = t * .07;
    birds.position.set(center.x + Math.cos(a) * 26, 12 + Math.sin(t * .5) * .6, center.z + Math.sin(a) * 18);
    birds.rotation.y = -a + Math.PI;
    flock.forEach(b => { const f = Math.sin(t * 7 + b.ph) * .7; b.wings[0].rotation.z = f; b.wings[1].rotation.z = -f; });
  };
  flapBirds(3); life.push(flapBirds);

  const cloudMat = std('#ffffff', { roughness: 1, transparent: true, opacity: .92, emissive: '#ffffff', emissiveIntensity: .25 });
  const clouds = [[-38, 30], [36, 30], [-46, -4], [44, -2]].map(([u, v], k) => {
    const g = new THREE.Group(); const w = toWorld(u, v);
    [[0, 0, 0, 2.2], [1.6, -.3, .3, 1.6], [-1.6, -.4, -.2, 1.5], [.5, .5, -.6, 1.4]].forEach(([x, y, z, r]) => {
      const m = new THREE.Mesh(GEO.sphere, cloudMat); m.scale.set(r * 1.4, r, r * 1.2); m.position.set(x, y, z); g.add(m);
    });
    g.position.set(w.x, 9 + k % 2, w.z); world.add(g);
    return { g, x0: w.x, z0: w.z, ph: k * 1.7 };
  });
  const drift = t => clouds.forEach(c => { c.g.position.x = c.x0 + Math.sin(t * .03 + c.ph) * 6; c.g.position.z = c.z0 + Math.cos(t * .025 + c.ph) * 4; });
  life.push(drift);

  /* ═════════ 夜：星星、光暈 ═════════ */
  const glowTex = (() => {
    const cv = document.createElement('canvas'); cv.width = cv.height = 64;
    const g = cv.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,214,140,1)'); gr.addColorStop(.35, 'rgba(255,190,100,.45)'); gr.addColorStop(1, 'rgba(255,170,80,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  const haloMat = new THREE.SpriteMaterial({ map: glowTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  lamps.forEach(([x, y, z, s = 1.1]) => { const sp = new THREE.Sprite(haloMat); sp.position.set(x, y, z); sp.scale.setScalar(s * 1.6); world.add(sp); });
  // 路燈照在地上的光斑（俯瞰視角看不到天空，所以不放星星）
  const poolMat = new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending });
  const poolGeo = new THREE.PlaneGeometry(1, 1); poolGeo.rotateX(-Math.PI / 2);
  lamps.forEach(([x, y, z, s = 1.1, noPool]) => { if (noPool) return; const m = new THREE.Mesh(poolGeo, poolMat); m.position.set(x, y - 1.38, z); m.scale.set(s * 3.2, 1, s * 3.2); m.renderOrder = 3; world.add(m); });

  let night = 0, nightTarget = 0;
  const cA = new THREE.Color(), cB = new THREE.Color();
  const mix = (a, b, k) => cA.set(a).lerp(cB.set(b), k);
  function applyNight(k) {
    world.background.copy(mix(DAY.bg, NIGHT.bg, k)); world.fog.color.copy(world.background);
    hemi.color.copy(mix(DAY.hemiSky, NIGHT.hemiSky, k)); hemi.groundColor.copy(mix(DAY.hemiGround, NIGHT.hemiGround, k));
    hemi.intensity = DAY.hemi + (NIGHT.hemi - DAY.hemi) * k;
    sun.color.copy(mix(DAY.sun, NIGHT.sun, k)); sun.intensity = DAY.sunI + (NIGHT.sunI - DAY.sunI) * k;
    fill.intensity = DAY.fill + (NIGHT.fill - DAY.fill) * k;
    seaMat.color.copy(mix(DAY.sea, NIGHT.sea, k));
    renderer.toneMappingExposure = DAY.exposure + (NIGHT.exposure - DAY.exposure) * k;
    glowMat.emissiveIntensity = k * 1.5; haloMat.opacity = k * .95; poolMat.opacity = k * .7;
    cloudMat.opacity = .92 - k * .5; cloudMat.emissiveIntensity = .25 - k * .2;
    M.foam.color.copy(mix(C.foam, '#8fa3bd', k));
    dash.material.opacity = .6 - k * .45;
  }
  applyNight(0);

  /* ═════════ 足跡、選取、先備高亮 ═════════ */
  const GLOW_VISIT = new THREE.MeshStandardMaterial({ color: '#ffe0a0', emissive: '#ffb84d', emissiveIntensity: .9 });
  const FLAG = std(C.forest, { roughness: .8, side: THREE.DoubleSide });
  const refMat = basic('#3f5b9a', { transparent: true, opacity: .85, depthWrite: false });
  const refGeo = new THREE.TorusGeometry(1, .07, 6, 40); refGeo.rotateX(Math.PI / 2);
  PAGES.forEach(p => {
    const b = B[p.stem], I = b.isle;
    // 島邊（朝向鏡頭）的燈籠與旗子位置
    const a = Math.atan2(SQ, SQ) + (b.isCore ? .55 : 0);
    const ex = b.isCore ? I.x + Math.cos(a) * I.angR(a) * .8 : b.x + .9, ez = b.isCore ? I.z + Math.sin(a) * I.angR(a) * .8 : b.z + .9;
    const lan = new THREE.Group(); lan.position.set(ex, I.top, ez);
    const post = new THREE.Mesh(GEO.cyl, std(C.woodDark)); post.scale.set(.07, 1.05, .07); post.position.y = .52; lan.add(post);
    const bulb = new THREE.Mesh(GEO.round, GLOW_VISIT); bulb.scale.set(.24, .3, .24); bulb.position.y = 1.15; lan.add(bulb);
    lan.visible = false; world.add(lan);
    const fx = b.isCore ? I.x + Math.cos(a + .5) * I.angR(a + .5) * .72 : b.x - .9, fz = b.isCore ? I.z + Math.sin(a + .5) * I.angR(a + .5) * .72 : b.z + .9;
    const flag = new THREE.Group(); flag.position.set(fx, I.top, fz);
    const pole = new THREE.Mesh(GEO.cyl, std(C.white)); pole.scale.set(.06, 1.9, .06); pole.position.y = .95; flag.add(pole);
    const cloth = new THREE.Mesh(GEO.prism, FLAG); cloth.scale.set(.05, .5, .7); cloth.rotation.x = Math.PI / 2; cloth.position.set(0, 1.62, .35); flag.add(cloth);
    flag.visible = false; world.add(flag);
    const ref = new THREE.Mesh(refGeo, refMat); ref.scale.setScalar(b.isCore ? I.radius * 1.12 : 1.55); ref.position.set(b.isCore ? I.x : b.x, I.top + .06, b.isCore ? I.z : b.z); ref.visible = false; world.add(ref);
    Object.assign(b, { lan, flag, ref });
  });
  const marker = new THREE.Mesh(new THREE.ConeGeometry(.42, .9, 4), new THREE.MeshStandardMaterial({ color: '#f3c15a', emissive: '#f0a83a', emissiveIntensity: .6 }));
  marker.rotation.x = Math.PI; marker.visible = false; world.add(marker);
  let selected = null, refs = [];
  anims.push(t => {
    if (selected) marker.position.y = B[selected].top + 1.4 + Math.sin(t * 3) * .18;
    refMat.opacity = .55 + .35 * Math.sin(t * 3);
  });

  /* ═════════ 相機與操作 ═════════ */
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .1, 500);
  const POLAR = 52 * Math.PI / 180, DIST = 110;
  const HOME = center.clone();
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.minPolarAngle = 46 * Math.PI / 180; controls.maxPolarAngle = 62 * Math.PI / 180;
  controls.minZoom = .7; controls.maxZoom = 3.6;
  controls.enableDamping = motion(); controls.dampingFactor = .08;
  controls.rotateSpeed = .6; controls.zoomSpeed = 1.1;
  controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_ROTATE };
  camera.position.set(HOME.x + Math.sin(POLAR) * Math.sin(FACE) * DIST, Math.cos(POLAR) * DIST, HOME.z + Math.sin(POLAR) * Math.cos(FACE) * DIST);
  camera.lookAt(HOME); camera.updateMatrixWorld();
  // 自動取景：把主要島嶼（含地標與標籤高度）投影到鏡頭的左右／上下軸，取外接範圍
  const RV = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), UV = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
  const FV = camera.getWorldDirection(new THREE.Vector3());
  const FIT = { r: 30, u: 18 };
  {
    let r0 = 1e9, r1 = -1e9, u0 = 1e9, u1 = -1e9; const q = new THREE.Vector3();
    framed.forEach(I => {
      for (let k = 0; k < 16; k++) {
        const a = k / 16 * Math.PI * 2;
        [0, I.top + 3].forEach(h => {
          q.set(I.x + Math.cos(a) * I.radius * 1.15 - HOME.x, h, I.z + Math.sin(a) * I.radius * 1.15 - HOME.z);
          const r = q.dot(RV), u = q.dot(UV); r0 = Math.min(r0, r); r1 = Math.max(r1, r); u0 = Math.min(u0, u); u1 = Math.max(u1, u);
        });
      }
    });
    FIT.r = (r1 - r0) / 2; FIT.u = (u1 - u0) / 2;
    HOME.addScaledVector(RV, (r0 + r1) / 2).addScaledVector(UV, (u0 + u1) / 2);
    HOME.addScaledVector(FV, -HOME.y / FV.y);              // 沿視線滑回地面，畫面位置不變
  }
  controls.target.copy(HOME);
  camera.position.copy(HOME).addScaledVector(FV, -DIST); camera.lookAt(HOME);
  // 視錐：寬度涵蓋整個群島（約 ±36），窄螢幕略裁兩翼
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    const aspect = w / h;
    renderer.setPixelRatio(lowPower ? 1 : Math.min(window.devicePixelRatio || 1, narrow() ? 1.25 : 1.6));
    renderer.setSize(w, h, false);
    // 上方多留一點給島嶼跳轉鈕；窄螢幕允許兩翼略為裁切
    const half = Math.max(FIT.u * 1.12 + 1.5, FIT.r * (narrow() ? .84 : 1.03) / aspect);
    Object.assign(camera, { left: -half * aspect, right: half * aspect, top: half, bottom: -half });
    camera.updateProjectionMatrix(); measureTags(); requestRender();
  }

  let fly = null;
  function flyTo(target, zoom) {
    if (!motion()) {
      const off = camera.position.clone().sub(controls.target);
      controls.target.copy(target); camera.position.copy(target).add(off);
      camera.zoom = zoom; camera.updateProjectionMatrix(); controls.update(); requestRender(); return;
    }
    fly = { from: controls.target.clone(), to: target.clone(), z0: camera.zoom, z1: zoom, t0: performance.now(), dur: 800 };
    requestRender();
  }
  function stepFly(now) {
    if (!fly) return false;
    const k = Math.min(1, (now - fly.t0) / fly.dur), e = 1 - Math.pow(1 - k, 3);
    const off = camera.position.clone().sub(controls.target);
    controls.target.lerpVectors(fly.from, fly.to, e); camera.position.copy(controls.target).add(off);
    camera.zoom = fly.z0 + (fly.z1 - fly.z0) * e; camera.updateProjectionMatrix();
    if (k >= 1) fly = null;
    return true;
  }

  /* ── 拾取：正課整座島、附屬島的單棟建築 ── */
  const picks = [];
  const pickMat = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false });
  PAGES.forEach(p => {
    const b = B[p.stem];
    const geo = b.isCore ? new THREE.CylinderGeometry(b.pickR, b.pickR, b.top - b.y + 2.2, 16) : new THREE.BoxGeometry(2.4, b.top - b.y + 1.4, 2.4);
    const m = new THREE.Mesh(geo, pickMat);
    m.position.set(b.isCore ? b.isle.x : b.x, (b.top + b.y) / 2, b.isCore ? b.isle.z : b.z); m.userData.stem = p.stem;
    world.add(m); picks.push(m);
  });
  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), v3 = new THREE.Vector3();
  function pickAt(cx, cy) {
    const r = canvas.getBoundingClientRect();
    ndc.set((cx - r.left) / r.width * 2 - 1, -(cy - r.top) / r.height * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hit = ray.intersectObjects(picks, false)[0];
    return hit ? hit.object.userData.stem : null;
  }
  let hover = null, down = null;
  function setHover(stem) {
    if (stem === hover) return;
    hover = stem; canvas.classList.toggle('is-hover', !!stem);
    tags.forEach(T => T.el.classList.toggle('is-hover', !!stem && T.stem === stem));
    requestRender();
  }
  canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointermove', e => { if (e.pointerType === 'mouse' && !e.buttons) setHover(pickAt(e.clientX, e.clientY)); });
  canvas.addEventListener('pointerleave', () => setHover(null));
  canvas.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 6) { down = null; return; }
    down = null;
    const stem = pickAt(e.clientX, e.clientY);
    if (stem) { select(stem, { trigger: canvas, fly: true }); scrollListTo(stem); } else closePanel();
  });
  function scrollListTo(stem) {
    const it = items.get(stem);
    if (it && window.innerWidth >= 768) { const list = $('islList'); list.scrollTop = it.li.offsetTop - list.clientHeight / 2; }
  }
  canvas.addEventListener('keydown', e => {
    const step = Math.PI / 12;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const off = camera.position.clone().sub(controls.target);
      off.applyAxisAngle(new THREE.Vector3(0, 1, 0), e.key === 'ArrowLeft' ? -step : step);
      camera.position.copy(controls.target).add(off); controls.update(); requestRender(); e.preventDefault();
    } else if (['+', '=', '-', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
      const zin = e.key === '+' || e.key === '=' || e.key === 'ArrowUp';
      camera.zoom = Math.min(controls.maxZoom, Math.max(controls.minZoom, camera.zoom * (zin ? 1.2 : 1 / 1.2)));
      camera.updateProjectionMatrix(); requestRender(); e.preventDefault();
    }
  });
  controls.addEventListener('change', requestRender);

  /* ═════════ 標籤層（HTML）═════════ */
  const layer = $('islLabels');
  const tags = [];
  const UNIT_ZOOM = 1.6;               // 放大到這個倍率以上，才展開附屬島的單元標籤
  function addTag({ stem = null, grp, kind, text, code, anchor, prio }) {
    const el = document.createElement('button');
    el.type = 'button'; el.className = `isl-tag isl-tag-${kind} isl-tag-${grp}`; el.tabIndex = -1; el.setAttribute('aria-hidden', 'true');
    if (code) { const n = document.createElement('span'); n.className = 'isl-tag-num'; n.textContent = code; el.appendChild(n); }
    const t = document.createElement('span'); t.className = 'isl-tag-t'; t.textContent = text; el.appendChild(t);
    el.addEventListener('click', () => {
      if (stem) { select(stem, { trigger: canvas, fly: true }); scrollListTo(stem); } else flyToIsle(grp);
    });
    layer.appendChild(el);
    tags.push({ el, stem, grp, kind, anchor, prio, w: 0, h: 0, cw: 0, num: el.querySelector('.isl-tag-num') });
  }
  PAGES.forEach(p => {
    const b = B[p.stem];
    addTag({ stem: p.stem, grp: p.grp, kind: p.grp === 'core' ? 'core' : 'unit', text: p.title, code: p.code,
      anchor: new THREE.Vector3(b.x, b.top + .35, b.z), prio: p.grp === 'core' ? 2 : 4 });
  });
  Object.entries(SAT_ISLE).forEach(([grp, I]) => {
    addTag({ grp, kind: 'isle', text: ISLES[grp].name, anchor: new THREE.Vector3(I.x, I.top + 4.6, I.z), prio: 3 });
  });
  function measureTags() {
    tags.forEach(T => {
      T.el.classList.remove('is-compact'); T.w = T.el.offsetWidth; T.h = T.el.offsetHeight;
      T.cw = T.num ? T.num.offsetWidth + 10 : T.w;
    });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { measureTags(); requestRender(); });
  const placed = [];
  function placeTags() {
    const W = canvas.clientWidth, H = canvas.clientHeight, zoomed = camera.zoom >= UNIT_ZOOM;
    placed.length = 0;
    const sel = T => (!!T.stem && T.stem === selected ? 0 : 1);
    const order = tags.slice().sort((a, b) => sel(a) - sel(b) || a.prio - b.prio);
    order.forEach(T => {
      const isSel = !!T.stem && T.stem === selected, isRef = !!T.stem && refs.includes(T.stem);
      let show = T.kind === 'core' || (T.kind === 'unit' ? zoomed : !zoomed) || isSel || isRef;
      v3.copy(T.anchor).project(camera);
      const x = (v3.x + 1) / 2 * W, y = (1 - v3.y) / 2 * H;
      // 完整標籤與已放好的重疊時，退成只顯示編號的小圓章；仍然重疊才隱藏
      const hits = r => placed.some(q => !(r.r < q.l || r.l > q.r || r.b < q.t || r.t > q.b));
      const box = w => ({ l: x - w / 2 - 3, r: x + w / 2 + 3, t: y - T.h - 8, b: y });
      // 手機上正課標籤預設只顯示編號（選取或滑過時才展開）
      let compact = narrow() && T.kind === 'core' && !isSel && T.stem !== hover, r = box(compact ? T.cw : T.w);
      if (show && (r.l < 2 || r.r > W - 2 || r.t < 0 || r.b > H)) show = false;   // 會被切掉的就不顯示
      if (show && !isSel && hits(r) && !compact) {
        if (T.num && !hits(box(T.cw))) { compact = true; r = box(T.cw); } else show = false;
      }
      if (show) placed.push(r);
      T.el.classList.toggle('is-off', !show);
      T.el.classList.toggle('is-compact', show && compact);
      if (show) T.el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, calc(-100% - 6px))`;
    });
  }

  /* ═════════ 繪製迴圈 ═════════ */
  let last = performance.now(), fpsN = 0, fpsT = 0, slow = 0;
  const animating = () => motion() && onScreen && document.visibilityState === 'visible';
  function requestRender() { need = true; if (!raf && alive) raf = requestAnimationFrame(frame); }
  function frame(now) {
    raf = 0; if (!alive) return;
    const dt = Math.min(.1, (now - last) / 1000); last = now;
    const flying = stepFly(now), moved = controls.update(), anim = animating();
    let fading = false;
    if (night !== nightTarget) {
      night = motion() ? (nightTarget > night ? Math.min(nightTarget, night + dt / 1.2) : Math.max(nightTarget, night - dt / 1.2)) : nightTarget;
      applyNight(night); fading = true;
    }
    if (anim) {
      const t = now / 1000;
      anims.forEach(f => f(t));
      if (!lowPower) life.forEach(f => f(t, dt));
      // 效能保護：連續約 3 秒低於 22fps 就停用生活感動畫並降解析度
      fpsN++; fpsT += dt;
      if (fpsT > 1) { slow = fpsN / fpsT < 22 ? slow + 1 : 0; fpsN = 0; fpsT = 0; if (slow >= 3 && !lowPower) { lowPower = true; resize(); } }
    }
    if (need || anim || flying || moved || fading) { renderer.render(world, camera); placeTags(); need = false; }
    if (anim || flying || moved || fading) raf = requestAnimationFrame(frame);
  }
  const ro = new ResizeObserver(resize); ro.observe(stage);
  new IntersectionObserver(es => { onScreen = es[0].isIntersecting; requestRender(); }).observe(stage);
  document.addEventListener('visibilitychange', requestRender);
  reduceMotion.addEventListener('change', () => { controls.enableDamping = motion(); requestRender(); });
  anims.forEach(f => f(1.7)); life.forEach(f => f(1.7, 0));
  resize();
  renderer.shadowMap.needsUpdate = true;
  requestRender();

  function flyToIsle(grp) {
    if (grp === 'core') { const c = coreIsles.reduce((s, I) => s.add(new THREE.Vector3(I.x, 0, I.z)), new THREE.Vector3()).multiplyScalar(1 / coreIsles.length); flyTo(c, 1.35); return; }
    const I = SAT_ISLE[grp]; if (I) flyTo(new THREE.Vector3(I.x, GROUND, I.z), 2.1);
  }

  /* ═════════ 對外介面 ═════════ */
  return {
    select(stem, doFly) {
      refs.forEach(r => { B[r].ref.visible = false; });
      selected = stem && B[stem] ? stem : null;
      refs = selected ? BY[selected].refs.filter(r => B[r]) : [];
      refs.forEach(r => { B[r].ref.visible = true; });
      marker.visible = !!selected;
      tags.forEach(T => { T.el.classList.toggle('is-current', !!T.stem && T.stem === selected); T.el.classList.toggle('is-ref', !!T.stem && refs.includes(T.stem)); });
      if (selected) {
        const b = B[selected];
        marker.position.set(b.x, b.top + 1.4, b.z);
        if (doFly) {
          setHover(null);
          // 讓選到的島落在面板以外的區域：桌機面板在左下，往右讓；手機面板從下方升起，往上讓
          const zoom = Math.max(camera.zoom, b.isCore ? 1.9 : 2.3), W = canvas.clientWidth, H = canvas.clientHeight;
          const wpp = (camera.right - camera.left) / zoom / W;
          camera.updateMatrixWorld();
          const R = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), U = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
          const tgt = new THREE.Vector3(b.isCore ? b.isle.x : b.x, b.y, b.isCore ? b.isle.z : b.z);
          if (window.innerWidth >= 768) tgt.addScaledVector(R, -Math.min(210, W * .22) * wpp);
          else tgt.addScaledVector(U, -H * .2 * wpp);
          flyTo(tgt, zoom);
        }
      }
      requestRender();
    },
    flyToIsle,
    reset() { flyTo(HOME.clone(), 1); },
    setNight(on, instant) {
      nightTarget = on ? 1 : 0;
      if (instant || !motion()) { night = nightTarget; applyNight(night); }
      requestRender();
    },
    updateTrail() {
      PAGES.forEach(p => {
        const b = B[p.stem], done = !!trail.done[p.stem], visited = !!trail.visited[p.stem];
        b.flag.visible = done; b.lan.visible = visited && !done;
      });
      tags.forEach(T => {
        if (!T.stem) return;
        T.el.classList.toggle('is-done', !!trail.done[T.stem]);
        T.el.classList.toggle('is-visited', !!trail.visited[T.stem] && !trail.done[T.stem]);
      });
      renderer.shadowMap.needsUpdate = true;
      requestRender();
    },
    // 給 tools/browser_check.js 用：建築在畫布上的像素位置（點擊測試）
    screenPos(stem) {
      const b = B[stem]; if (!b) return null;
      v3.set(b.x, b.y + (b.top - b.y) * .4, b.z).project(camera);
      const r = canvas.getBoundingClientRect();
      return { x: r.left + (v3.x + 1) / 2 * r.width, y: r.top + (1 - v3.y) / 2 * r.height };
    },
    dispose() { alive = false; ro.disconnect(); controls.dispose(); renderer.dispose(); layer.replaceChildren(); },
  };
}

function mulberry32(a) {
  return function () {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
