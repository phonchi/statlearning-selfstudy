"""第 8 章依講義、教學對話與 coin 範例再修訂：為什麼用樹、為什麼要集成。

在 reading_flow、teaching_scope、lecture_alignment 之後才套用，所以比對的是已收合的段落。
每個替換都要求比對字串恰好出現一次，上游文字改了會直接報錯，不會靜默失效。
新節 `motive` 放在 prologue 之後；舊的投票元件（w09vote*）由這裡的 w09coin* 取代。
"""
import re

from lib import detail, info_card, rows_card, svg, table, viz


def rep(bodies, sec, old, new):
    n = bodies[sec].count(old)
    if n != 1:
        raise ValueError(f"{sec}: 比對到 {n} 次：{old[:50]}")
    bodies[sec] = bodies[sec].replace(old, new)


def cut(bodies, sec, start, end, new=""):
    """把 start（含）到 end（不含）之間換成 new。"""
    b = bodies[sec]
    if b.count(start) != 1:
        raise ValueError(f"{sec}: 起點比對到 {b.count(start)} 次：{start[:50]}")
    a = b.index(start)
    z = b.find(end, a + len(start))
    if z < 0:
        raise ValueError(f"{sec}: 找不到終點：{end[:50]}")
    bodies[sec] = b[:a] + new + b[z:]


def block(body, pid):
    """回傳 id=pid 的整個 <details>…</details>（含巢狀）在 body 中的起訖位置。"""
    m = re.search(r'<details\b[^>]*\bid="' + re.escape(pid) + r'"[^>]*>', body)
    if not m:
        raise ValueError("找不到收合：" + pid)
    depth = 0
    for t in re.finditer(r"<details\b|</details>", body[m.start():]):
        depth += -1 if t.group().startswith("</") else 1
        if depth == 0:
            return m.start(), m.start() + t.end()
    raise ValueError("收合沒有結束：" + pid)


def take(bodies, sec, pid):
    """把收合整塊從 sec 取出並傳回。"""
    a, z = block(bodies[sec], pid)
    out = bodies[sec][a:z]
    bodies[sec] = bodies[sec][:a] + bodies[sec][z:]
    return out


def add(bodies, sec, pid, content):
    """接在收合內容的最後、來源連結之前。"""
    b = bodies[sec]
    a, z = block(b, pid)
    inner = b[a:z]
    # 只看這個收合自己的最外層：最後一個 source-links 若屬於巢狀收合就不算
    s = inner.rfind('<p class="source-links">')
    close = inner.rfind("</div></details>")
    if s < 0 or s < inner.rfind("</details>", 0, close):
        s = close
    bodies[sec] = b[:a] + inner[:s] + content + inner[s:] + b[z:]


def slider(sid, label, lo, hi, step, val, valtext, oninput, basis="230px"):
    return (f'<span class="slider-row" style="margin-bottom:0;flex:1 1 {basis};min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" value="{val}" '
            f'oninput="{oninput}" aria-label="{label}">'
            f'<span class="slider-val" id="{sid}Val">{valtext}</span></span>')


# ══ 新節 motive：樹的長處、代價與兩個集成直覺 ═════════════════════════════
COIN_VIZ = viz(
    svg("w09coinSvg", 330),
    [rows_card("目前設定",
               [("單一個分類器答對的機率 p", "0.51", "w09coinP"),
                ("分類器個數 M（奇數）", "1001", "w09coinM"),
                ("多數決答對的機率", "—", "w09coinAcc"),
                ("如果 M 個分類器一模一樣", "—", "w09coinSame")]),
     rows_card("講義的例子",
               [("p = 0.51，M = 1001", "—", "w09coinDeck"),
                ("p = 0.51，M = 10001", "—", "w09coinDeck2"),
                ("p = 0.49，M = 1001", "—", "w09coinBad")]),
     info_card("怎麼看這張圖",
               '上圖是「答對的票占幾成」的分佈，綠色是過半（多數決答對），紅色是沒過半。'
               'M 一大，分佈就往 p 收窄，只要 p 在 0.5 右邊，綠色就會吃掉幾乎全部。<br>'
               '下圖橫軸是 M（對數刻度）：粗線是目前的 p，虛線是 1−p，點線是 M 個分類器完全相同時的正確率，'
               '不管投幾票都停在 p。')],
    "w09coinStatus", "拖動 p 與 M，看多數決的正確率怎麼變；把 p 拖到 0.5 以下試試。",
    slider("w09coinSlP", "p", 30, 70, 1, 51, "0.51", "w09coinSet()", "300px")
    + slider("w09coinSlM", "M", 0, 100, 1, 75, "1001", "w09coinSet()", "300px")
    + '<button class="btn btn-step" onclick="w09coinJump(1)">M = 1</button>'
    + '<button class="btn btn-step" onclick="w09coinJump(1001)">M = 1001</button>'
    + '<button class="btn btn-step" onclick="w09coinJump(10001)">M = 10001</button>',
    provenance=("illustrative", "假設 M 個分類器彼此獨立、正確率都是 p；二項分佈的精確機率在瀏覽器裡即時計算。"))

RHO_VIZ = viz(
    svg("w09rhoSvg", 280),
    [rows_card("目前設定",
               [("樹與樹的相關係數 ρ", "0.50", "w09rhoR"),
                ("樹的棵數 B", "100", "w09rhoB"),
                ("平均之後的變異 ÷ σ²", "—", "w09rhoV"),
                ("其中平均不掉的 ρ", "—", "w09rhoFloor"),
                ("其中還會隨 B 變小的 (1−ρ)/B", "—", "w09rhoRest")]),
     info_card("怎麼看這張圖",
               '粗線是 $\\rho+(1-\\rho)/B$，虛線是它的地板 $\\rho$，灰線是 ρ = 0（樹彼此不相關）時的 1/B。'
               'B 從 10 加到 1000，粗線很快就貼到地板上；要再往下，只能把 ρ 本身壓低。'),
     info_card("ρ 從哪裡來",
               'bagging 的每棵樹都是從<strong>同一份</strong>訓練資料重抽出來的，樣本大量重疊，'
               '而且常常都先切同一個強變數，所以 ρ 明顯大於 0。'
               'bootstrap 沒有製造新的獨立資料，只是重複利用手上這一份。')],
    "w09rhoStatus", "拖動 ρ 與 B：B 加大只能壓掉 (1−ρ)/B 那一項。",
    slider("w09rhoSlR", "ρ", 0, 100, 1, 50, "0.50", "w09rhoSet()", "200px")
    + slider("w09rhoSlB", "B", 0, 60, 1, 40, "100", "w09rhoSet()", "200px"),
    provenance=("illustrative", "公式 ρ+(1−ρ)/B 的曲線；假設固定 x、每棵樹的預測變異都是 σ²、兩兩相關都是 ρ。"))

GREEDY_NOTE = detail("w09-detail-interaction-limits", "樹抓交互作用要切幾刀",
    r"""<p>樹的交互作用是「走到這一支，下一刀才切那個變數」。這個機制很方便，但要的刀數比想像多。</p>
<p>如果真實關係是 $Y=X_1X_2$，最粗略的近似是四個象限各給一個正負號，這需要深度 2 的樹：根節點一刀，左右兩邊各再一刀，共 3 次分裂、4 片葉子。每條從根到葉的路徑只用兩刀，但整棵樹是三刀。想把乘積曲面描得更細，就得再多切很多刀。</p>
<p>相對地，<a href="beyond_linearity.html#gam">GAM</a> 每個變數各配一條曲線再加起來，不會自己長出交互作用，要用就得自己寫進 $f_{12}(X_1,X_2)$。樹會自己找，但找得到與否要看資料和搜尋方式。</p>""")

COIN_MATH = detail("w09-detail-coin-math", "深入投票：常態近似、Condorcet 定理與講義的 75%",
    r"""<p><strong>為什麼 M 一大就穩贏。</strong>令 $S_M$ 為 M 票中答對的票數，$S_M\sim\mathrm{Bin}(M,p)$，平均 $Mp$、標準差 $\sqrt{Mp(1-p)}$。平均隨 M 線性成長，雜訊只隨 $\sqrt M$ 成長。用常態近似，</p>
$$P\!\left(S_M>\tfrac M2\right)\approx\Phi\!\left(\sqrt M\cdot\frac{p-0.5}{\sqrt{p(1-p)}}\right),$$
<p>$\Phi$ 是標準常態的累積分佈函數。$p=0.51$ 時，$M=1000$ 代入得 $\Phi(0.63)\approx73.6\%$，$M=10000$ 得 $\Phi(2.0)\approx97.7\%$。關鍵是前面的 $\sqrt M$：只要 $p>0.5$，括號裡的值就會往無限大跑。這就是 <strong>Condorcet 陪審團定理</strong>：獨立的陪審員各自比瞎猜好一點，人數愈多，多數決愈可能是對的。</p>
<p><strong>講義的「約 75%」。</strong>講義說 1000 個 51% 的分類器投票可以到約 75%。精確計算時，偶數 M 會碰到平手，答案看平手怎麼算：嚴格過半是 72.6%，平手時擲硬幣決定是 73.6%，平手也算答對則是 74.7%。最後一種只是事件機率，實際上不可能「平手時自動答對」。上面的元件只用奇數 M 避開平手，M = 1001 得 73.7%。所以 75% 是概數，大約四分之三就對了。</p>
<p><strong>兩個常見誤會。</strong>有些硬幣範例會寫「bagging 創造了獨立性」，又說只要 i.i.d. 錯誤率就指數下降。數學沒錯，錯在前提：bagging 的樹來自同一份資料，彼此高度相關（見下方「真實的樹不獨立」）。範例也把 random forest 說成「彙總成千上萬個弱分類器」，但 random forest 的樹通常長很深、各自不弱；用很多棵很弱的小樹的是 boosting。</p>""")

RHO_MATH = r"""<p>這條公式只講<strong>平均預測</strong>的變異，條件是固定 $x$、每棵樹的變異都是 $\sigma^2$、兩兩相關都是 $\rho$；推導見 <a href="#w09proof-forest-var">random forest 一節的證明</a>。它不能直接換算成分類的投票正確率：只知道兩兩相關係數，還不足以決定多數決答對的機率。這裡的變異與相關，指的是「換一份訓練資料、重新訓練」造成的變動。給定訓練資料以後，各棵樹的 bootstrap 抽樣與隨機種子可以互相獨立；可是訓練資料一換，所有樹會一起往同一個方向動，這個共同的變動就是 $\rho\sigma^2$。</p>"""

RHO_DETAIL = detail("w09-detail-rho-floor", "深入相關：平均不掉的 ρσ² 與互動圖",
    r"""<p>迴歸的情況可以算得很清楚：固定一個 $x$，設每棵樹的預測變異都是 $\sigma^2$、兩兩相關係數都是 $\rho$，B 棵樹平均之後</p>
$$\operatorname{Var}\!\left(\frac1B\sum_{b=1}^B\hat f^{b}(x)\right)=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2.$$
<p>第二項隨 B 變大而消失，第一項 $\rho\sigma^2$ <strong>不管種幾棵樹都在</strong>。硬幣的例子是 $\rho=0$ 的理想狀況。</p>
""" + RHO_VIZ + "\n" + RHO_MATH)

ROADMAP = table(
    ["方法", "怎麼組合", "主要對付", "對應的節"],
    [["Bagging", "bootstrap 重抽 B 份，各長一棵深樹再平均（或投票）", "樹與樹之間不相關的那部分變異", '<a href="#bagging">Bagging 與 OOB</a>'],
     ["Random forest", "同 bagging，但每個節點都重新抽 m 個變數，只准從中挑（不是每棵樹固定一組）", "降低樹與樹之間的相關（代價是單棵樹可能變弱）", '<a href="#rf">Random Forest</a>'],
     ["Boosting", "一棵接一棵長小樹，每棵修正前面還沒解釋的部分", "主要是偏差；它不是在平均同分佈的樹", '<a href="#boosting">Boosting</a>'],
     ["BART", "從上一輪的樹微調，跑馬可夫鏈蒙地卡羅（MCMC）再平均", "兼有隨機化與修正殘差", '<a href="#stacking">Stacking 與 BART</a>']])


def motive_body(compare):
    compare = compare.replace("比較樹與線性模型的性質", "對照表：樹與線性模型的性質")
    return r"""
  <p>Hitters 那棵樹只切兩刀，卻已經做到線性迴歸要額外設計才做得到的事：<code>Hits</code> 只在 <code>Years</code> ≥ 4.5 的那一支才有作用。這是樹自己長出來的<strong>交互作用</strong>。樹還有幾個長處：</p>
  <ul>
    <li><strong>非線性與交互作用：</strong>「走到這一支才切那個變數」就是交互作用，不必自己乘出 $X_1X_2$；不過四個象限各給一個正負號就要深度 2（3 刀），見<a href="#w09-detail-interaction-limits">下一節的收合</a>。階梯要切幾刀才逼近得了彎曲的關係，在<a href="#vslinear">「樹 vs 線性模型」</a>一節比較。</li>
    <li><strong>不怕單調轉換：</strong>切點只看大小順序。$X&lt;10$ 和標準化後的 $Z&lt;(10-\mu)/\sigma$ 是同一刀，取 log 也一樣，所以不必先標準化。</li>
    <li><strong>類別變數：</strong>可以直接把水準分成兩堆（套件支援程度要另外查）。</li>
    <li><strong>好解釋：</strong>畫得出來，一句話講得完。</li>
  </ul>
""" + compare + r"""

  <p><strong>代價是不穩定。</strong>樹的每一刀都建立在上一刀之上，資料稍微變一點，根節點換了一個切點或變數，下面整棵樹就跟著全部改寫。把訓練資料隨機切成兩半各長一棵，兩棵可能完全不像。這就是<strong>變異很大</strong>。另外，單棵樹的預測準確度通常比不上最好的方法；葉子是常數，也不會外插。</p>
  <p>解法是不要只相信一棵樹，讓很多棵一起決定。為什麼「一群不太準的模型」合起來會變準？先看一枚硬幣。</p>

  <h3>一枚 51% 的硬幣</h3>
  <p>假設一枚硬幣出現正面的機率是 51%，只比公平硬幣多 1%。擲一次，你幾乎感覺不到這個優勢。擲一千次，正面過半的機率就到了約四分之三；擲一萬次，接近 98%。</p>
  <p>把「正面」換成「答對」，就是集成的直覺：M 個分類器各投一票，以二元分類、M 為奇數為例（這裡的 M 是分類器個數，和上一節的葉子數無關），如果它們<strong>彼此獨立</strong>、每個答對的機率都是 $p$，那麼多數決答對的機率是二項分佈的尾巴：</p>
  $$P(\text{多數決答對})=\sum_{k&gt;M/2}\binom Mk p^k(1-p)^{M-k}.$$
""" + COIN_VIZ + r"""
  <p>$p&gt;0.5$ 時，M 愈大愈接近 1；$p&lt;0.5$ 時方向反過來，愈投愈錯，投票只會放大原本的傾向。元件下半那條點線是另一個極端：M 個分類器<strong>一模一樣</strong>時，投一千票和投一票沒有差別。所以獨立是整個論證的前提。講義說的「1000 個約 75%」和精確值的小差別，在下面的收合裡說明。</p>
""" + COIN_MATH + r"""

  <h3>真實的樹不獨立</h3>
  <p>同一份資料長出來的樹，錯的地方常常一樣，彼此相關。這時平均只能壓掉樹與樹之間<strong>不相關</strong>的那一部分變異；大家一起動的那一部分，種再多棵樹也壓不掉。硬幣的例子是完全不相關的理想狀況，真實的集成方法都會碰到這個限制。</p>
""" + RHO_DETAIL + r"""

  <h3>本章接下來的路線</h3>
  <p>後面幾節的集成方法，都可以用這兩個想法定位：獨立的投票會放大小優勢，樹與樹的相關會限制平均的效果。</p>
""" + ROADMAP + r"""
  <p>講義的結論是：random forest 與梯度提升樹（GBDT）是大多數表格資料任務應該最先試的模型，而且幾乎不需要前處理，很適合快速做出第一版。代價是失去單棵樹「畫得出來、一句話講完」的解釋力。在那之前，先把單棵樹怎麼長、怎麼剪弄清楚。</p>
"""


# ══ 舊投票元件（P06 vote）移除，換成 coin／rho 元件 ═══════════════════════
COIN_JS = r"""
/* ---------- P01 motive：獨立投票（硬幣）與相關的地板 ---------- */
const w09coinLF = (() => {
  const a = [0];
  for (let k = 1; k <= 10001; k++) a.push(a[k - 1] + Math.log(k));
  return a;
})();
function w09coinLogPmf(k, M, lp, lq) {
  return w09coinLF[M] - w09coinLF[k] - w09coinLF[M - k] + k * lp + (M - k) * lq;
}
/* 多數決正確率（M 為奇數）：每一項直接在 log 空間算，沒有遞推，不會下溢成全 0 */
function w09coinMaj(p, M) {
  if (p <= 0) return 0;
  if (p >= 1) return 1;
  const lp = Math.log(p), lq = Math.log(1 - p);
  let s = 0;
  for (let k = (M + 1) / 2; k <= M; k++) s += Math.exp(w09coinLogPmf(k, M, lp, lq));
  return Math.max(0, Math.min(1, s));
}
function w09coinOdd(v) {
  const m = Math.round(Math.pow(10, 4 * v / 100));
  const odd = m % 2 === 1 ? m : m + 1;
  return Math.max(1, Math.min(10001, odd));
}
const w09coinMs = (() => {
  const a = [];
  for (let v = 0; v <= 100; v += 2) { const m = w09coinOdd(v); if (!a.length || a[a.length - 1] !== m) a.push(m); }
  return a;
})();
let w09coinP = 0.51, w09coinM = 1001;
function w09coinSet() {
  const ep = document.getElementById('w09coinSlP'), em = document.getElementById('w09coinSlM');
  if (ep) w09coinP = parseInt(ep.value, 10) / 100;
  if (em) w09coinM = w09coinOdd(parseInt(em.value, 10));
  const vp = document.getElementById('w09coinSlPVal'), vm = document.getElementById('w09coinSlMVal');
  if (vp) vp.textContent = HC.fmt(w09coinP, 2);
  if (vm) vm.textContent = String(w09coinM);
  w09coinDraw();
}
function w09coinJump(M) {
  const em = document.getElementById('w09coinSlM');
  if (em) em.value = String(Math.round(100 * Math.log10(M) / 4));
  w09coinSet();
  w09coinM = M;
  const vm = document.getElementById('w09coinSlMVal');
  if (vm) vm.textContent = String(M);
  w09coinDraw();
}
function w09coinDraw() {
  const host = w09frame('w09coinSvg', 330);
  if (!host) return;
  const p = w09coinP, M = w09coinM;
  const lp = Math.log(p), lq = Math.log(1 - p);
  /* 上圖：答對比例 k/M 的分佈。橫軸以 0.5 為中心、依分佈寬度放大；
     機率本身逐項精確計算，畫圖時才合併成最多 60 格 */
  const L = 60, R = 590, T = 44, H = 88;
  const half = Math.min(0.5, Math.max(0.03, Math.abs(p - 0.5) + 4 * Math.sqrt(p * (1 - p) / M)));
  const lo = 0.5 - half, hi = 0.5 + half;
  /* 每格放 kw 個整數 k，並讓格線正好落在過半門檻 (M+1)/2，長條才不會忽高忽低 */
  const kMaj = (M + 1) / 2;
  const kw = Math.max(1, Math.ceil((2 * half * M + 1) / 60));
  const kLo = Math.max(0, kMaj - kw * Math.ceil((kMaj - Math.floor(lo * M)) / kw));
  const NB = Math.ceil((Math.min(M, Math.ceil(hi * M)) - kLo + 1) / kw);
  const bins = new Array(NB).fill(0);
  for (let k = kLo; k < kLo + NB * kw && k <= M; k++) {
    bins[Math.floor((k - kLo) / kw)] += Math.exp(w09coinLogPmf(k, M, lp, lq));
  }
  const top = Math.max(...bins) || 1;
  const xf = f => L + (R - L) * (f - lo) / (hi - lo);
  w09mk(host, 'text', { x: L, y: 16, cls: 'axtitle' }, '答對票數占 M 的比例：分佈（M = ' + M + '，橫軸已放大到 0.5 附近）');
  for (let b = 0; b < NB; b++) {
    if (bins[b] <= 0) continue;
    const k0 = kLo + b * kw, x0 = Math.max(L, xf((k0 - 0.5) / M)), x1 = Math.min(R, xf((k0 + kw - 0.5) / M));
    if (x1 - x0 < 0.5) continue;
    const h = H * bins[b] / top;
    w09mk(host, 'rect', { x: x0 + 0.5, y: T + H - h, width: Math.max(0.5, x1 - x0 - 1), height: h,
                          fill: k0 >= kMaj ? 'var(--accent3)' : 'var(--accent)', opacity: 0.85 });
  }
  w09mk(host, 'line', { x1: L, y1: T + H, x2: R, y2: T + H, stroke: 'var(--card-border)' });
  const xh = xf((kMaj - 0.5) / M);
  w09mk(host, 'line', { x1: xh, y1: T - 4, x2: xh, y2: T + H + 4, stroke: 'var(--ink)', 'stroke-width': 2 });
  w09mk(host, 'text', { x: xh - 6, y: T - 6, 'text-anchor': 'end', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, '← 沒過半');
  w09mk(host, 'text', { x: xh + 6, y: T - 6, fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, '過半 →');
  [0, 0.25, 0.5, 0.75, 1].forEach(t => w09mk(host, 'text', { x: L + t * (R - L), y: T + H + 15,
    'text-anchor': 'middle', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' },
    HC.fmt(lo + t * (hi - lo), half < 0.1 ? 3 : 2)));
  /* 下圖：多數決正確率 vs M（對數軸） */
  const T2 = 178, H2 = 118;
  const xm = m => L + (R - L) * Math.log10(m) / 4;
  const ya = a => T2 + H2 * (1 - a);
  w09mk(host, 'text', { x: L, y: T2 - 12, cls: 'axtitle' }, '多數決答對的機率 vs 分類器個數 M（對數刻度）');
  [0, 0.5, 1].forEach(a => {
    w09mk(host, 'line', { x1: L, y1: ya(a), x2: R, y2: ya(a), stroke: 'var(--card-border)',
                          'stroke-dasharray': a === 0.5 ? '4 3' : null });
    w09mk(host, 'text', { x: L - 6, y: ya(a) + 4, 'text-anchor': 'end', fill: 'var(--muted)',
                          style: w09MONO + 'font-size:10px' }, String(a));
  });
  [1, 10, 100, 1000, 10000].forEach(m => w09mk(host, 'text', { x: xm(m), y: T2 + H2 + 15,
    'text-anchor': 'middle', fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, String(m)));
  const path = pp => w09coinMs.map((m, i) => (i ? 'L' : 'M') + xm(m).toFixed(1) + ',' + ya(w09coinMaj(pp, m)).toFixed(1)).join(' ');
  w09mk(host, 'path', { d: path(1 - p), fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.6, 'stroke-dasharray': '6 4' });
  w09mk(host, 'line', { x1: L, y1: ya(p), x2: R, y2: ya(p), stroke: 'var(--ink)', 'stroke-width': 1.4, 'stroke-dasharray': '2 3' });
  w09mk(host, 'path', { d: path(p), fill: 'none', stroke: 'var(--accent)', 'stroke-width': 3 });
  const acc = w09coinMaj(p, M);
  w09mk(host, 'circle', { cx: xm(M), cy: ya(acc), r: 5, fill: 'var(--accent)', stroke: 'var(--card)', 'stroke-width': 2 });
  w09mk(host, 'text', { x: R, y: ya(p) - 5, 'text-anchor': 'end', fill: 'var(--ink)',
                        style: w09MONO + 'font-size:10px' }, '完全相同的 M 個：停在 p');
  document.getElementById('w09coinP').textContent = HC.fmt(p, 2);
  document.getElementById('w09coinM').textContent = String(M);
  document.getElementById('w09coinAcc').textContent = HC.pct(acc, 1);
  document.getElementById('w09coinSame').textContent = HC.pct(p, 1);
  document.getElementById('w09coinDeck').textContent = HC.pct(w09coinMaj(0.51, 1001), 1);
  document.getElementById('w09coinDeck2').textContent = HC.pct(w09coinMaj(0.51, 10001), 1);
  document.getElementById('w09coinBad').textContent = HC.pct(w09coinMaj(0.49, 1001), 1);
  setStatus('w09coinStatus', 'p = ' + HC.fmt(p, 2) + '、M = ' + M + ' 時，多數決答對的機率是 <strong>'
    + HC.pct(acc, 1) + '</strong>'
    + (M === 1 ? '：只有一票，正確率就是 p。' : p > 0.5 ? '，比單一個分類器高。' : (p < 0.5 ? '，比單一個分類器<strong>還低</strong>：投票放大了原本的傾向。'
                                                  : '：剛好是瞎猜，投幾票都一樣。')));
}

let w09rhoR = 0.5, w09rhoB = 100;
function w09rhoBOf(v) { return Math.max(1, Math.round(Math.pow(10, 3 * v / 60))); }
function w09rhoSet() {
  const er = document.getElementById('w09rhoSlR'), eb = document.getElementById('w09rhoSlB');
  if (er) w09rhoR = parseInt(er.value, 10) / 100;
  if (eb) w09rhoB = w09rhoBOf(parseInt(eb.value, 10));
  const vr = document.getElementById('w09rhoSlRVal'), vb = document.getElementById('w09rhoSlBVal');
  if (vr) vr.textContent = HC.fmt(w09rhoR, 2);
  if (vb) vb.textContent = String(w09rhoB);
  w09rhoDraw();
}
function w09rhoDraw() {
  const host = w09frame('w09rhoSvg', 280);
  if (!host) return;
  const r = w09rhoR, B = w09rhoB;
  const L = 60, R = 590, T = 34, H = 200;
  const xb = b => L + (R - L) * Math.log10(b) / 3;
  const yv = v => T + H * (1 - v);
  w09mk(host, 'text', { x: L, y: 20, cls: 'axtitle' }, '平均 B 棵樹之後的變異 ÷ σ²');
  [0, 0.25, 0.5, 0.75, 1].forEach(v => {
    w09mk(host, 'line', { x1: L, y1: yv(v), x2: R, y2: yv(v), stroke: 'var(--card-border)' });
    w09mk(host, 'text', { x: L - 6, y: yv(v) + 4, 'text-anchor': 'end', fill: 'var(--muted)',
                          style: w09MONO + 'font-size:10px' }, String(v));
  });
  [1, 10, 100, 1000].forEach(b => w09mk(host, 'text', { x: xb(b), y: T + H + 16, 'text-anchor': 'middle',
    fill: 'var(--muted)', style: w09MONO + 'font-size:10px' }, String(b)));
  w09mk(host, 'text', { x: (L + R) / 2, y: T + H + 32, 'text-anchor': 'middle', fill: 'var(--muted)',
                        style: w09MONO + 'font-size:10px' }, '樹的棵數 B（對數刻度）');
  const grid = [];
  for (let i = 0; i <= 120; i++) grid.push(Math.pow(10, 3 * i / 120));
  const path = f => grid.map((b, i) => (i ? 'L' : 'M') + xb(b).toFixed(1) + ',' + yv(f(b)).toFixed(1)).join(' ');
  w09mk(host, 'path', { d: path(b => 1 / b), fill: 'none', stroke: 'var(--muted)', 'stroke-width': 1.6 });
  w09mk(host, 'line', { x1: L, y1: yv(r), x2: R, y2: yv(r), stroke: 'var(--ink)', 'stroke-width': 1.6, 'stroke-dasharray': '6 4' });
  w09mk(host, 'path', { d: path(b => r + (1 - r) / b), fill: 'none', stroke: 'var(--accent)', 'stroke-width': 3 });
  const v = r + (1 - r) / B;
  w09mk(host, 'circle', { cx: xb(B), cy: yv(v), r: 5, fill: 'var(--accent)', stroke: 'var(--card)', 'stroke-width': 2 });
  w09mk(host, 'text', { x: R, y: yv(r) - 6, 'text-anchor': 'end', fill: 'var(--ink)',
                        style: w09MONO + 'font-size:10px' }, '地板 ρ = ' + HC.fmt(r, 2));
  w09mk(host, 'text', { x: xb(3) + 10, y: yv(1 / 3) + 4, fill: 'var(--muted)',
                        style: w09MONO + 'font-size:10px' }, '不相關（ρ = 0）：1/B');
  document.getElementById('w09rhoR').textContent = HC.fmt(r, 2);
  document.getElementById('w09rhoB').textContent = String(B);
  document.getElementById('w09rhoV').textContent = HC.fmt(v, 3);
  document.getElementById('w09rhoFloor').textContent = HC.fmt(r, 3);
  document.getElementById('w09rhoRest').textContent = HC.fmt((1 - r) / B, 3);
  setStatus('w09rhoStatus', 'ρ = ' + HC.fmt(r, 2) + '、B = ' + B + '：變異剩 σ² 的 <strong>'
    + HC.fmt(v, 3) + '</strong>，其中 ' + HC.fmt(r, 3) + ' 是 B 再大也壓不掉的地板。');
}
"""


def pagejs(js):
    """拿掉舊的 w09vote*，加入 w09coin*／w09rho*。"""
    a = js.index("/* ---------- P06 vote：多數投票與大數法則 ---------- */")
    z = js.index("/* ---------- P07 bag：bootstrap 與 OOB ---------- */")
    js = js[:a] + COIN_JS.lstrip("\n") + "\n" + js[z:]
    for old, new in [("w09voteRender();\n", "w09coinDraw();\nw09rhoDraw();\n"),
                     ("  w09voteChartDraw();\n", "")]:
        if js.count(old) != 1:
            raise ValueError("PAGEJS 比對失敗：" + old)
        js = js.replace(old, new)
    if "w09vote" in js:
        raise ValueError("PAGEJS 還留著 w09vote")
    return js


# ══ 各節 ═══════════════════════════════════════════════════════════════
def prologue(b):
    compare = take(b, "prologue", "w09-detail-tree-compare")
    cut(b, "prologue", "<p>最後那一列是這一整章後半的動機。", '<div class="quiz-box">',
        '<p>樹的長處和它最大的弱點，都在下一節<a href="#motive">「為什麼要種一片森林」</a>說明。</p>\n\n')
    rep(b, "prologue", "三塊的預測值就是各塊訓練資料的<strong>平均</strong>：",
        "三塊的預測值是各塊訓練資料 log 薪水的<strong>平均</strong>，換回薪水尺度是 ")
    rep(b, "prologue", "也就是約 16.5 萬、40.3 萬、84.5 萬。",
        "也就是約 16.5 萬、40.3 萬、84.5 萬（指數轉回來是幾何平均的尺度，不等於平均薪水）。")
    rep(b, "prologue", "哪個對？看真實關係長什麼樣，這是 PART 05 的主題。",
        '哪個對？看真實關係長什麼樣，這是<a href="#vslinear">「樹 vs 線性模型」</a>一節的主題。')
    return compare


def grow(b):
    rep(b, "grow", "這是樹的表達能力上限，也是 PART 05 要比較的重點。",
        '這是樹的表達能力上限，也是<a href="#vslinear">「樹 vs 線性模型」</a>要比較的重點。')
    rep(b, "grow", "<p>其中 $R_1(j,s) = \\{X \\mid X_j &lt; s\\}$、$R_2(j,s) = \\{X \\mid X_j \\ge s\\}$。</p>",
        "<p>其中 $R_1(j,s) = \\{X \\mid X_j &lt; s\\}$、$R_2(j,s) = \\{X \\mid X_j \\ge s\\}$。"
        "一直切到某個停止條件為止，例如每一塊都不超過 5 筆觀測。</p>\n"
        "  <p>方塊理論上可以是任何形狀，只用軸平行的長方形，是為了好算，也好解釋。</p>")
    rep(b, "grow", "貪婪搜尋降低了計算成本。",
        "另一個常一起出現的詞是<strong>由上而下</strong>（top-down）：從根開始往下切。"
        "它只描述切的順序；真正省下計算的是貪婪，因為不必比較所有可能的方塊組合。")
    rep(b, "grow", "下一節的剪枝，正是為了補救貪婪的短視。\n</div>",
        "下一節的剪枝處理的是「太早停下來」這種短視；不過剪枝只能從長好的大樹裡挑子樹，"
        "早期的某一刀切得不好，剪枝也改不回來。\n</div>\n" + GREEDY_NOTE)
    cut(b, "grow", "<li><strong>RSS 下降量一路遞減。</strong>", "<li><strong>只要切得夠多",
        "<li><strong>訓練 RSS 只降不升。</strong>在這個元件裡前幾刀掉很多、後面愈切愈少，但這不是定律："
        "有時某一刀本身沒什麼用，切完之後下一刀才大幅下降。該切幾刀，要交給下一節的驗證來決定。</li>\n    ")
    # 去重：「類別分割與套件支援要分開」重講了前面兩小節，只把套件那一句併回第一小節
    cut(b, "grow", "<h3>類別分割與套件支援要分開</h3>", '<p class="source-links">')
    rep(b, "grow", "不計左右互換，共有 $2^{q-1}-1$ 種。",
        "不計左右互換，共有 $2^{q-1}-1$ 種，例如 4 個水準就有 7 種。"
        "只比較「一個水準對其他全部」（one-versus-rest）只看 $q$ 種，"
        "會漏掉像 $\\{A,B\\}$ 對 $\\{C,D\\}$ 這樣的分法。")
    rep(b, "grow", "二元分類亦有相應排序捷徑，多類別問題則不可直接把類別編號平均後套用。",
        "二元分類依各水準 $Y=1$ 的比例排序，用 Gini 或交叉熵時同樣保證找到最佳分割；"
        "多類別問題沒有這個捷徑，也不可直接把類別編號平均後套用。"
        "水準很多時，用訓練資料的平均排序容易過度擬合。"
        "scikit-learn 的一般決策樹只接收數值欄，Lab 先用 <code>ModelSpec</code> 產生設計矩陣再訓練，"
        "這和原生的類別子集合分割不是同一個搜尋空間。")
    # 「從 Hitters 的三區域」後兩段重講了貪婪搜尋與 Heart 例子（F17）
    cut(b, "grow", "<p>在當前節點中，對每個特徵先排序相異值", '<p class="source-links">')
    g = b["grow"]
    i = g.index("將它指數轉換是幾何平均尺度")
    b["grow"] = g[:i] + "指數轉換之後的尺度，開場已經說明。" + g[g.index("</p>", i):]


PRUNE_EXAMPLE = r"""<h3>算一次 weakest-link：三個內部節點的例子</h3>
<p>以下把上面的臨界值記成 $g(t)=\alpha_{\rm eff}(t)$。假設一棵大樹 $T_0$ 有三個內部節點：根、A、B，A 與 B 各管兩片葉。$R(t)$ 是把節點收成一片葉的 RSS，$R(T_t)$ 是保留它底下子樹的 RSS：</p>
""" + table(["節點", "收成一片葉的 RSS", "保留子樹的 RSS", "子樹葉數", "$g(t)$"],
            [["A", "16", "10", "2", "$(16-10)/(2-1)=6$"],
             ["B", "22", "18", "2", "$(22-18)/(2-1)=4$"],
             ["根", "60", "28", "4", "$(60-28)/(4-1)=32/3$"]]) + r"""
<p>最小的是 B，所以 $\alpha_1=4$ 時先剪 B。剪完之後根底下的子樹 RSS 變成 $10+22=32$、葉數 3，根的值要<strong>重算</strong>：$(60-32)/(3-1)=14$。這時 A 的 6 比較小，$\alpha_2=6$ 剪 A；最後根的子樹 RSS 是 38、葉數 2，$\alpha_3=(60-38)/(2-1)=22$ 剪成只剩根。得到 $T_0\supset T_1\supset T_2\supset T_3$，每個 $\alpha$ 的最佳子樹都在這條路徑上，$\alpha$ 也不是事先設好的格點，而是演算法算出來的斷點。</p>
<p>容易搞混的一點：「最小化 $g(t)$」不是「在某個固定的 $\alpha$ 下，挑讓成本下降最多的那一刀」。各分支的 $|T_t|-1$ 不同，兩件事不等價；$g(t)$ 最小的分支，是 $\alpha$ 由小變大時<strong>最早</strong>不值得保留的那一支。</p>
<p>「可預測」的意思是：每棵子樹的成本 $R(T)+\alpha|T|$ 都是 $\alpha$ 的一條直線，最佳子樹是這些直線的下包絡，所以只在有限個 $\alpha$ 處換人。例如三棵子樹的成本 $100+6\alpha$、$110+4\alpha$、$130+2\alpha$，最佳子樹只在 $\alpha=5$ 與 $\alpha=10$ 換手。</p>
<h3>長樹與剪樹可以用不同準則</h3>
<p>分類樹長樹時用 Gini 或交叉熵，因為它們對純度比較敏感；剪樹時如果最終目標是預測準確率，ISLP 指出用錯誤率比較好。sklearn 實際怎麼做，見<a href="#classtree">分類樹</a>一節「剪枝路徑與選參數的指標要分開」。</p>
<p>ISLP 圖 8.4 是剪枝前的 Hitters 大樹，除了 <code>Years</code> 與 <code>Hits</code>，還用到 <code>RBI</code>、<code>Putouts</code>、<code>Walks</code>、<code>Runs</code> 等變數；交叉驗證之後只剩 3 片葉，回到開場那棵兩刀的樹。</p>
"""

NESTED_PROOF = r"""<p><strong>巢狀性質。</strong>對內部節點 $t$ 令 $d_t=R(t)-R(t_L)-R(t_R)$，代表在 $t$ 多切一刀省下的 RSS。剪枝子樹 $T$ 由它保留的內部節點集合 $I(T)$ 決定，而 $I(T)$ 對祖先封閉（保留一個節點就得保留它的所有祖先）。因為 $R(T)=R(\text{根})-\sum_{t\in I(T)}d_t$、$|T|=1+|I(T)|$，</p>
$$C_\alpha(T)=R(\text{根})+\alpha+\sum_{t\in I(T)}(\alpha-d_t).$$
<p>設 $\alpha_1&lt;\alpha_2$，$I_1$、$I_2$ 分別是兩者的最佳解。對祖先封閉的集合取聯集、交集仍然對祖先封閉，所以 $I_1\cup I_2$ 是合法的子樹。$I_1$ 在 $\alpha_1$ 下最佳，比 $I_1\cup I_2$ 不差，得到 $\sum_{t\in I_2\setminus I_1}(\alpha_1-d_t)\ge0$。於是在 $\alpha_2$ 下</p>
$$\sum_{t\in I_2\setminus I_1}(\alpha_2-d_t)\ge(\alpha_2-\alpha_1)\,|I_2\setminus I_1|.$$
<p>若 $I_2\setminus I_1$ 不空，右邊大於 0，那麼把這些節點拿掉的 $I_1\cap I_2$ 在 $\alpha_2$ 下嚴格更便宜，和 $I_2$ 最佳矛盾。所以 $I_2\subseteq I_1$：$\alpha$ 變大時，最佳子樹只會變小，不會換到另一支。同一個 $\alpha$ 有多棵並列最佳時，取葉子最少的那棵，路徑就唯一。這裡的「最佳」是在給定的 $T_0$ 之內；$T_0$ 本身是貪婪長出來的，不保證是所有樹裡最好的。</p>"""


def prune(b):
    rep(b, "prune", "<strong>這個解法是錯的</strong>", "<strong>這個做法有盲點</strong>")
    rep(b, "prune", "正確的做法是<strong>先長太大", "講義推薦的做法是<strong>先長太大")
    rep(b, "prune", "$T(\\alpha_2) \\subset T(\\alpha_1)$", "$T(\\alpha_2) \\subseteq T(\\alpha_1)$")
    cut(b, "prune", "<p>一個候選分支 $T_t$ 若收成單葉", "<p>Lab 的 <code>cost_complexity_pruning_path</code>")
    rep(b, "prune", "而且錯得很有教育意義：它太短視。", "而且這個盲點很有教育意義：它太短視。")
    rep(b, "prune", "提早停就永遠看不到那一刀。</p>",
        "提早停就永遠看不到那一刀。</p>\n"
        "  <p>直接限制樹的深度或每片葉的最少筆數（sklearn 的 <code>max_depth</code>、"
        "<code>min_samples_leaf</code>）也是常見做法，簡單好用，但上限是事先定死的，不看後面還能切出什麼。</p>")
    rep(b, "prune", "<li>用遞迴二元分裂在訓練資料上長一棵很大的樹。</li>",
        "<li>用遞迴二元分裂在訓練資料上長一棵很大的樹，直到每片葉的觀測數少於某個下限才停。</li>")
    rep(b, "prune", "weakest-link 演算法逐次選最先達到這個臨界值的分支，無須列舉所有可能子樹。</p>",
        "weakest-link 演算法逐次選最先達到這個臨界值的分支，無須列舉所有可能子樹。</p>" + NESTED_PROOF)
    add(b, "prune", "w09-detail-prune-compute", PRUNE_EXAMPLE)


IMPURITY_EXAMPLE = r"""<h3>錯誤率看不出差別的一個算例</h3>
<p>父節點有 70 筆 A、30 筆 B，錯誤率 $E=0.30$、Gini $G=1-0.7^2-0.3^2=0.42$。比較兩種各切成 50 筆的分法：</p>
""" + table(["", "左節點", "右節點", "加權錯誤率", "加權 Gini", "加權交叉熵"],
            [["分法一", "35A／15B", "35A／15B", "0.30", "0.42", "0.611"],
             ["分法二", "40A／10B", "30A／20B", "0.30", "0.40", "0.587"]]) + r"""
<p>兩種分法裡，兩個子節點的多數類別都還是 A，答錯的筆數一樣是 30，錯誤率完全沒動。可是分法二的左節點明顯比較純，Gini 從 0.42 降到 $\tfrac12(0.32)+\tfrac12(0.48)=0.40$，交叉熵（以 $e$ 為底）從 0.611 降到 0.587。用錯誤率當準則，演算法會覺得兩刀一樣沒用；Gini 與交叉熵看得出分法二比較好。</p>
"""

HEART_NOTE = r"""<h3>Heart 資料與類別分割的讀法</h3>
<p>ISLP 的 <code>Heart</code> 資料有 303 位胸痛病人，反應變數 <code>HD</code> 是血管攝影檢查有沒有心臟病，預測變數有 13 個，包括 <code>Age</code>、<code>Sex</code>、<code>Chol</code>（膽固醇）與其他心肺功能指標。交叉驗證選出的樹有 6 片葉。</p>
<p>有些預測變數是類別型，樹圖上會寫成 <code>Thal:a</code> 或 <code>ChestPain:bc</code>：左分支是該變數取第一個水準（<code>Thal</code> 的 a），或取第二、三個水準（<code>ChestPain</code> 的 b 與 c）；其餘水準走右分支。</p>
"""


def classtree(b):
    rep(b, "classtree", "兩者數值上非常接近，實務上選哪個幾乎沒差。</p>",
        "兩者數值上非常接近，實務上選哪個幾乎沒差，而且都是可微的。</p>\n"
        "  <p>評估一刀時，看的是兩個子節點不純度的<strong>加權和</strong>，權重是各自占父節點觀測的比例 $N_L$、$N_R$："
        "$N_L\\,G(R_L)+N_R\\,G(R_R)$（交叉熵同理），挑讓它最小的那一刀。</p>")
    a, z = block(b["classtree"], "w09-detail-impurity-calculation")
    inner = b["classtree"][a:z]
    anchor = '<div class="detail-body">'
    i = inner.index(anchor) + len(anchor)
    inner = inner[:i] + IMPURITY_EXAMPLE + inner[i:]
    close = inner.rfind("</div></details>")
    inner = inner[:close] + HEART_NOTE + inner[close:]
    b["classtree"] = b["classtree"][:a] + inner + b["classtree"][z:]


def vslinear(b):
    rep(b, "vslinear", "本章後半的集成方法幾乎一定打得贏兩者，",
        "本章後半的集成方法常常比單棵樹準得多（是否勝過線性模型仍要用驗證比較），")
    cut(b, "vslinear", "<p>後半章從最後一項出發。", '<div class="quiz-box">',
        '<p>後半章從最後一項「不穩定」出發，<a href="#motive">「為什麼要種一片森林」</a>那一節已經說明為什麼平均可以壓低變異。</p>\n\n')


WHY_BODY = r"""
  <p>把一個難題交給幾千位隨機選出的路人，再彙整他們的答案，彙整的答案常常比一個專家還準。這叫<strong>群眾智慧</strong>（wisdom of the crowd）。機器學習版本的說法是：<strong>一群預測器合起來，常常比裡面最好的那一個還準</strong>。這一群叫做<strong>集成</strong>（ensemble）。實務上，集成多半用在專案後段，已經有幾個不錯的模型之後；機器學習競賽的冠軍解法也常常是集成。</p>
  <p><a href="#motive">硬幣那張圖</a>說明了：在那個二元分類的例子裡，投票要有效，成員得各自比瞎猜好，而且<strong>錯的地方不能都一樣</strong>。同一份資料、同一種演算法訓練出來的模型，常常在同一批觀測上一起犯錯，這時投一百票和投一票差不多。所以每一種集成方法都得回答：多樣性從哪裡來？</p>
  <p>bagging、random forest、boosting 各自的答案，整理在<a href="#motive">路線圖</a>裡。這一節看最直接的一種：<strong>用不同的演算法</strong>，例如下面三個完全不同的分類器一起投票；更進一步讓另一個模型學怎麼組合它們，就是 <a href="#stacking">stacking</a>。</p>
  <p>最簡單的組合方式是<strong>硬投票</strong>（hard voting）：每個分類器投一票，票多的類別勝出。另一種是<strong>軟投票</strong>（soft voting）：平均各模型預測的類別機率，再挑最大的那一類。</p>
"""


def why(b):
    lab = take(b, "why", "w09-detail-why-lab")
    src = b["why"]
    s = src.index("<p>Hard voting 數各類別標籤的票")
    e = src.index("</p>", s) + len("</p>")
    soft = src[s:e]
    b["why"] = WHY_BODY + detail("w09-detail-voting-probability", "硬投票與軟投票的細節", soft) + "\n" + lab + "\n"


def bagging(b):
    cut(b, "bagging", "<p>回到樹。", "<p>所以理想的做法是",
        "<p>回到樹。單一棵樹的問題是<strong>變異太大</strong>，降變異最古典的手段是<strong>平均</strong>。"
        "設每棵樹的預測變異是 $\\sigma^2$、兩兩相關係數是 $\\rho$，B 個預測平均之後，變異剩 $\\rho\\sigma^2+(1-\\rho)\\sigma^2/B$"
        '（推導與互動圖在<a href="#w09-detail-rho-floor">開頭那節的收合</a>）；'
        "如果它們彼此獨立（$\\rho=0$），就只剩 $\\sigma^2/B$。</p>\n  ")
    rep(b, "bagging", "（B 個無偏估計的平均還是無偏）",
        "（平均之後的期望值，和單一棵 bootstrap 樹的期望值相同）")
    rep(b, "bagging", "這一點跟前兩節的直覺剛好相反", '這一點跟<a href="#prune">剪枝</a>那一節的直覺剛好相反')
    cut(b, "bagging", "<p>從公式看最清楚。固定 x", "<p>所以 bagging 的正確用法是",
        "<p>固定 x，考慮重複訓練造成的變動。設每棵 bootstrap 樹的預測期望值都是 $\\mu(x)$。"
        "平均 B 棵之後，期望值還是 $\\mu(x)$，所以偏差 $\\mu(x)-f(x)$ 和單棵 bootstrap 樹一樣。"
        "變異則不同：B 變大只能壓掉樹與樹之間不相關的那一部分，共同的那一部分"
        '（<a href="#bagging">本節開頭那條公式</a>的第一項 $\\rho\\sigma^2$）留下來，這是下一節 random forest 要對付的東西。</p>')
    rep(b, "bagging", "它把訓練資料擬合到幾乎完美（低偏差）",
        "深樹的彈性大，近似誤差（偏差）通常小")
    rep(b, "bagging", "<strong>bagging 只治變異，不治偏差。</strong>",
        "<strong>bagging 主要治變異，幾乎不治偏差。</strong>")
    rep(b, "bagging", "<strong>完全免費的測試誤差估計</strong>，不必再做交叉驗證。",
        "<strong>幾乎免費的測試誤差估計</strong>。只是要估 bagging 本身的誤差，可以不必另做交叉驗證；"
        "拿 OOB 誤差去挑超參數時則另當別論，見下方問答。")
    rep(b, "bagging", "B 太小才會欠擬合", "B 太小只是變異還沒壓下來")
    rep(b, "bagging", "通常 100 到 500 就夠。</p>",
        "通常 100 到 500 就夠。</p>\n"
        "  <p>圖 8.8 用的是 <code>Heart</code> 資料，還有三個細節：虛線是單棵分類樹的測試誤差；"
        "random forest 那條用 $m=\\sqrt p$；OOB 誤差那兩條在這張圖裡明顯比測試誤差低，ISLP 說這只是碰巧。</p>")


def rf(b):
    cut(b, "rf", "<p>上一節的公式留了一個尾巴：</p>", "<h3>Extra-trees")
    # 收合裡「為什麼特徵子抽樣必須發生在每個節點？」重講正文，只留基因表達例子
    cut(b, "rf", "<h3>為什麼特徵子抽樣必須發生在每個節點？</h3>", "<p>講義的基因表達例子",
        "<h3>講義的基因表達例子</h3>\n")
    cut(b, "rf", "<p>Extra-trees 把候選門檻也隨機化", '<p class="source-links">')
    rep(b, "rf", "它不等於完全隨機選一刀。</p>",
        "它不等於完全隨機選一刀。<code>ExtraTreesClassifier</code> 預設 <code>bootstrap=False</code>，"
        "所以不能直接假設有 OOB。</p>")
    rep(b, "rf", "<p>講義的基因表達例子先選出 500 個預測變數，再比較不同候選特徵數與樹數；",
        "<p>講義的基因表達例子有 349 位病人、4,718 個基因的表現量，反應變數有 15 類（正常或 14 種癌症之一）。"
        "先挑訓練資料中變異最大的 500 個基因當預測變數，再比較三種 $m$ 與不同樹數（圖 8.10）。"
        "單棵分類樹的測試錯誤率是 45.7%，random forest（$m&lt;p$）比 bagging（$m=p$）再好一點；")
    rep(b, "rf", "不能由 Extra-trees 名稱推定一定有 OOB。", "")
    rep(b, "rf", "<summary>深入隨機化：相關性公式、Extra-trees 與抽樣層次</summary>",
        "<summary>深入隨機化：Extra-trees、抽樣層次與基因表達例子</summary>")
    blk = take(b, "rf", "w09-detail-extra-trees")
    rep(b, "rf", "所以 bagging 只是 random forest 的一個特例。</p>",
        "所以 bagging 只是 random forest 的一個特例。</p>\n"
        "  <p>用<a href=\"#bagging\">上一節那條公式</a>來說，random forest 想把第一項 $\\rho\\sigma^2$ 壓低。"
        "<code>Heart</code> 資料有 13 個預測變數，$m\\approx\\sqrt{13}$，每次分裂只看 4 個。"
        "講義也提醒：預測變數很多、彼此又高度相關時，小一點的 $m$ 通常有幫助。</p>\n" + blk)


def boosting(b):
    rep(b, "boosting", "每棵樹都看全部資料，只是看的<strong>目標</strong>被改過。</p>",
        "每棵樹都看全部資料，只是看的<strong>目標</strong>被改過。</p>\n"
        "  <p>這是和前兩節不同的另一條路。Bagging 與 random forest 平均一堆深樹，"
        "靠平均壓低變異，所以才需要 $\\rho$ 那條公式；boosting 不是在平均同分佈的樹，"
        "而是一棵接一棵用小樹修正前面還沒解釋掉的部分，主要在降低偏差。因為每棵新樹都考慮了已經長好的樹，小樹就夠用。"
        "講義說 bagging 的每棵樹「各自建立在自己的 bootstrap 樣本上」，指的是建樹時互不參照，"
        "不是說樹的預測彼此獨立。</p>")
    add(b, "boosting", "w09-detail-boost-parameters",
        "<p>講義用同一份基因表達資料改做二元分類（癌症或正常），比較 boosting 與 random forest（圖 8.11）。"
        "兩個 boosting 模型都用 $\\lambda=0.01$：深度 1 的樹略勝深度 2，兩者都勝過 random forest；"
        "單棵樹的測試錯誤率是 24%。這和 random forest 一節那個 15 類、單樹 45.7% 的問題不同，兩個數字不能直接比。"
        "用 stump 時得到的是加法模型。</p>")
    rep(b, "boosting", "變異被 $1/B$ 壓下去", "可以平均掉的那部分變異隨 B 變小（樹之間共同的變動 $\\rho\\sigma^2$ 仍然留著）")
    rep(b, "boosting", "反過來，如果第一棵樹就長很深，它會把殘差一次完全擬合——包括雜訊；後面 4999 棵就只剩雜訊可擬合，而每一棵都在增加整體的變異。",
        "反過來，每棵樹都長很深時，模型很快就開始追著雜訊跑；深度、學習率與樹數要一起用驗證來選。")
    rep(b, "boosting", "樹長深了反而一步就把殘差完全擬合，後面的樹只能開始擬合雜訊。",
        "樹長深了，模型很快就開始追著雜訊跑。")


def stacking(b):
    rep(b, "stacking", "<p>PART 06 的 voting 是用一個",
        '<p><a href="#why">「投票分類器」</a>一節的 voting 是用一個')
    rep(b, "stacking", "（out-of-box performance）。</p>",
        "（out-of-box performance）。</p>\n"
        "  <p>ISLP 圖 8.13 在 <code>Heart</code> 資料上比較 BART 與 boosting：BART 過了 100 輪暖機之後，"
        "訓練與測試誤差就穩定下來；boosting 跑到幾百輪之後開始過度擬合。"
        "演算法的起點是讓 K 棵樹都只有一片葉，葉值是 $\\frac1{nK}\\sum_i y_i$，"
        "加起來剛好是 $y$ 的平均。</p>")


def modern(b):
    rep(b, "modern", "本頁 PART 03 的成本複雜度剪枝", '本頁<a href="#prune">剪枝</a>一節的成本複雜度剪枝')


def exercises(b):
    rep(b, "exercises", "對，本頁 PART 08 的元件就是這張圖。兩個重點：", "對。兩個重點：")


def augment(bodies, js):
    compare = prologue(bodies)
    new = {}
    for k, v in bodies.items():
        new[k] = v
        if k == "prologue":
            new["motive"] = motive_body(compare)
    bodies.clear()
    bodies.update(new)
    grow(bodies)
    prune(bodies)
    classtree(bodies)
    vslinear(bodies)
    why(bodies)
    bagging(bodies)
    rf(bodies)
    boosting(bodies)
    stacking(bodies)
    modern(bodies)
    exercises(bodies)
    for k, v in bodies.items():
        if "PART 0" in v or "PART 1" in v:
            raise ValueError(f"{k}: 還有 PART 編號")
    return pagejs(js)
