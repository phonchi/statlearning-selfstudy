#!/usr/bin/env python3
"""s5_bayesian.html：Seeing Theory Ch.5 的概念型統計先備頁。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, hook, info, info_card, quiz, rows_card, svg, table, viz  # noqa: E402


WEB = "https://seeing-theory.brown.edu/bayesian-inference/index.html"
PDF = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf"

BODIES = {}

BODIES["review"] = r"""
  <p>Bayes 公式處理「看到結果之後，未知狀態或假設有多可能」這類問題。先驗機率描述看到資料前的判斷，
  概似描述各個未知狀態或假設與目前資料的相容程度；兩者相乘並重新正規化，就得到後驗機率。</p>
  <p>若事件 $A$ 是「有疾病」、$+$ 是「檢驗陽性」，則</p>
  $$P(A\mid +)=\frac{P(+\mid A)P(A)}{P(+\mid A)P(A)+P(+\mid A^c)P(A^c)}.$$
  <p>回顧 <a href="s2_conditional.html#bayes">S2 的篩檢算例</a>：盛行率 1%、靈敏度 90%、
  偽陽性率 5% 時，陽性後的患病機率約為 15.4%。這一頁接著把「更新事件機率」推進到
  「用資料更新未知參數的整個分布」。需要重算人數表時，可回 S2 核對。</p>
""" + info(
    "分母在做什麼",
    "分母把所有能產生陽性的路徑加總：患者中的真陽性，加上健康者中的偽陽性。"
    "它讓後驗機率加總為 1。",
) + hook(
    "正課中的分類機率",
    "到<a href=\"classification.html#lda\">分類章的 LDA</a>時，"
    "各類別的先驗機率與類別條件密度會用同一個 Bayes 規則合成分類機率。",
) + quiz(
    "qReview", "PART 01 · 自我檢測",
    "某疾病很少見。檢驗呈陽性後，為何不能直接把敏感度當成患病機率？",
    [(False, "因為敏感度必定小於 50%", "敏感度可以很高；問題在於它是 P(+｜疾病)，方向與題目要的 P(疾病｜+) 相反。"),
     (True, "還要考慮盛行率與偽陽性", "對。真陽性與偽陽性的來源都要放進分母，盛行率決定兩群人原先有多少。"),
     (False, "因為陽性結果完全沒有資訊", "陽性通常會改變患病機率，只是改變後的數值還取決於先驗與檢驗表現。")],
) + f'<p><a href="{WEB}#section1">來源：Seeing Theory Ch.5 · Bayes\' Theorem</a>；<a href="{PDF}#page=49">講義 p.49–50</a>。</p>'

BODIES["likelihood"] = r"""
  <p>固定已觀察的資料，把未知參數當成可變輸入，就得到<strong>概似函數（likelihood）</strong>。
  它寫成 $L(p\mid x)$，數值等於在指定 $p$ 下看到資料 $x$ 的機率或密度，但閱讀方向是「哪些
  $p$ 比較支持這批固定資料」。概似不是 $p$ 的機率分布，因此不要求對 $p$ 積分為 1。</p>
  <p>假設每次投擲互相獨立，而且都使用同一個正面機率 $p$。得到 $s$ 次正面、$f$ 次反面時，
  忽略與 $p$ 無關的二項係數後，</p>
  $$L(p\mid s,f)\propto p^s(1-p)^f,\qquad
    \hat p_{\mathrm{MLE}}=\frac{s}{s+f}\quad(s+f&gt;0).$$
  <p><strong>算例。</strong>7 次正面、3 次反面時，最大概似估計是 $0.7$。
  $p=0.7$ 相對於 $p=0.5$ 的概似比為
  $0.7^7 0.3^3/(0.5^{10})\approx2.28$。這表示目前資料在前一參數下約有 2.28 倍支持度；
  它不表示「$p=0.7$ 的機率是 2.28 倍」。若完全沒有資料，所有 $p$ 都使概似達到同一最大值，
  因此 MLE 不唯一，資料無法選出單一估計。</p>
""" + info(
    "機率與概似的方向",
    "機率固定參數、比較可能資料；概似固定已看到的資料、比較可能參數。公式相同，問題方向不同。",
    "warm",
) + quiz(
    "qLikelihood", "PART 02 · 自我檢測",
    "硬幣 10 次得到 7 次正面。$L(0.7)$ 比 $L(0.5)$ 大，能得出哪個結論？",
    [(False, "$P(p=0.7)=L(0.7)$", "概似不是參數的機率分布；要談參數機率，還需要先驗並做正規化。"),
     (True, "這批資料在 $p=0.7$ 下比在 $p=0.5$ 下更有支持度", "對。概似比較的是固定資料在不同參數值下的相對支持度。"),
     (False, "下一次一定是正面", "估計 $p=0.7$ 仍代表下一次有隨機性，不能推出確定結果。")],
) + f'<p><a href="{WEB}#section2">來源：Seeing Theory Ch.5 · Likelihood Function</a>；<a href="{PDF}#page=51">講義 p.51–52</a>。</p>'

BODIES["posterior"] = r"""
  <p>Beta 分布常用來描述硬幣正面機率 $p$ 的先驗，其中 $0\le p\le1$、$\alpha&gt;0$、$\beta&gt;0$。
  $B(\alpha,\beta)$ 是正規化常數，用來讓整條密度曲線下的面積等於 1。當
  $p\sim\operatorname{Beta}(\alpha,\beta)$，而資料有 $s$ 次正面與 $f$ 次反面，後驗仍是 Beta：</p>
  $$\pi(p)=\frac{p^{\alpha-1}(1-p)^{\beta-1}}{B(\alpha,\beta)},\qquad
    p\mid s,f\sim\operatorname{Beta}(\alpha+s,\beta+f).$$
  <p>Beta 先驗可用兩個較清楚的量來讀：先驗平均是
  $\alpha/(\alpha+\beta)$，先驗總量是 $\alpha+\beta$。前者決定中心，後者描述分布集中程度。
  更新後的平均為 $(\alpha+s)/(\alpha+\beta+s+f)$。</p>
  <p><strong>算例。</strong>$\operatorname{Beta}(2,2)$ 先驗加上 7 次正面、3 次反面，得到
  $\operatorname{Beta}(9,5)$ 後驗；平均由 $1/2$ 移到 $9/14\approx0.643$。
  下圖可以重做這筆計算，也能檢查均勻先驗與零筆資料等端點。</p>
""" + viz(
    svg("w25bayesSvg", 470),
    [info_card(
        "同一張圖的三條曲線",
        "上半圖的先驗與後驗是<strong>正規化密度</strong>，曲線下面積各為 1。"
        "下半圖是<strong>相對概似</strong>，最高點縮放為 1；兩種縱軸不能拿高度直接互比。",
    ),
     rows_card("目前的更新", [
         ("先驗", "Beta(1, 1)", "w25priorRead"),
         ("資料", "0 正、0 反", "w25dataRead"),
         ("後驗", "Beta(1, 1)", "w25postRead"),
         ("後驗平均", "0.500", "w25meanRead"),
         ("MLE", "不唯一（無資料）", "w25mleRead"),
     ]),
     info_card(
         "如何核對更新",
         "後驗第一個參數等於先驗第一個參數加正面次數，第二個參數加反面次數。"
         "零筆資料時兩個參數都不變，所以後驗應與先驗完全重合。",
     )],
    "w25bayesStatus", "均勻先驗且尚無資料：先驗與後驗重合；相對概似是一條高度 1 的水平線。",
    '<label>α <input id="w25alpha" type="range" min="1" max="20" step="1" value="1"></label>'
    '<output id="w25alphaOut">1</output>'
    '<label>β <input id="w25beta" type="range" min="1" max="20" step="1" value="1"></label>'
    '<output id="w25betaOut">1</output>'
    '<label>正面 <input id="w25success" type="range" min="0" max="20" step="1" value="0"></label>'
    '<output id="w25successOut">0</output>'
    '<label>反面 <input id="w25failure" type="range" min="0" max="20" step="1" value="0"></label>'
    '<output id="w25failureOut">0</output>'
    '<button class="btn btn-reset" onclick="w25bayesReset()">重置</button>',
    provenance=("illustrative", "硬幣資料為自訂概念示意；所有曲線由目前控制值即時計算。"),
) + quiz(
    "qPosterior", "PART 03 · 自我檢測",
    r"先驗為 $\operatorname{Beta}(3,4)$，看到 5 次正面與 2 次反面後，後驗是哪一個？",
    [(True, r"$\operatorname{Beta}(8,6)$", "對。正面次數加到第一個參數，反面次數加到第二個參數。"),
     (False, r"$\operatorname{Beta}(5,2)$", "這只留下資料計數，漏掉了先驗中的參數。"),
     (False, r"$\operatorname{Beta}(6,9)$", "正、反面計數加反了；第一個參數對應正面。")],
) + f'<p><a href="{WEB}#section3">來源：Seeing Theory Ch.5 · Prior to Posterior</a>；<a href="{PDF}#page=52">講義 p.52–54</a>。</p>'

BODIES["influence"] = r"""
  <p>後驗是先驗資訊與目前資料的折衷。對 Beta–Binomial 模型，後驗平均可直接拆成兩個平均的加權：</p>
  $$E[p\mid s,f]
    =\frac{\alpha+\beta}{\alpha+\beta+s+f}\frac{\alpha}{\alpha+\beta}
    +\frac{s+f}{\alpha+\beta+s+f}\frac{s}{s+f},
    \qquad s+f&gt;0.$$
  <p>若 $s+f=0$，不要代入最後一個分數；此時後驗直接等於先驗。</p>
  <p>若要預測下一次投擲，正面的後驗預測機率等於 $p$ 的後驗平均：
  $(\alpha+s)/(\alpha+\beta+s+f)$。</p>
  <p>先驗總量 $\alpha+\beta$ 越大，資料需要越多才會明顯推動後驗。資料量增加時，資料比例的權重增加；
  這不保證先驗永遠變得無關，還要確認模型與資料收集方式合理。</p>
  <p><strong>算例。</strong>同樣觀察 3 次正面、1 次反面。均勻先驗
  $\operatorname{Beta}(1,1)$ 產生 $\operatorname{Beta}(4,2)$，後驗平均為 $2/3$；
  集中在 0.5 的 $\operatorname{Beta}(20,20)$ 產生 $\operatorname{Beta}(23,21)$，後驗平均約 0.523。
  四筆資料對較集中的先驗影響較小。</p>
""" + table(
    ["情況", "後驗參數", "後驗平均", "閱讀重點"],
    [["Beta(1,1)＋3 正 1 反", "Beta(4,2)", "0.667", "資料比例影響明顯"],
     ["Beta(20,20)＋3 正 1 反", "Beta(23,21)", "0.523", "先驗總量較大"],
     ["Beta(20,20)＋300 正 100 反", "Beta(320,120)", "0.727", "大量資料取得較大權重"]],
) + quiz(
    "qInfluence", "PART 04 · 自我檢測",
    "兩位分析者使用平均都為 0.5 的 Beta(2,2) 與 Beta(40,40) 先驗。看到相同少量資料後，何者後驗移動較少？",
    [(False, "Beta(2,2)，因為參數比較小", "較小的參數總量代表先驗較分散，少量資料就能占較大權重。"),
     (True, "Beta(40,40)，因為先驗總量較大", "對。兩者中心相同，但 Beta(40,40) 更集中，等效的先前資訊量較大。"),
     (False, "兩者完全相同，因為先驗平均相同", "先驗平均只描述中心；集中程度也會影響更新幅度。")],
) + f'<p><a href="{WEB}#section3">來源：Seeing Theory Ch.5 · Prior to Posterior</a>；<a href="{PDF}#page=52">講義 p.52–54</a>。</p>'

BODIES["exercises"] = (
    quiz("qEx1", "EXERCISE 1 · Bayes 公式",
         r"某事件先驗機率 20%，觀察 E 的條件機率在事件成立時為 0.8、不成立時為 0.2。$P(A\mid E)$ 是多少？",
         [(False, "0.20", "這是更新前的先驗，尚未使用 E 的資訊。"),
          (True, "0.50", "對。分子 0.8×0.2=0.16，分母再加 0.2×0.8=0.16，所以是 0.5。"),
          (False, "0.80", "0.8 是 P(E｜A)，條件方向與題目不同。")])
    + quiz("qEx2", "EXERCISE 2 · 概似",
           "只有 4 次正面、0 次反面時，二項概似在哪裡達最大？",
           [(False, "$p=0$", "此時 $p^4=0$，無法產生四次正面。"),
            (False, "$p=0.5$", "公平硬幣可以產生資料，但支持度不是最大。"),
            (True, "$p=1$", "對。$p^4$ 隨 p 增加，端點 1 達最大。")])
    + quiz("qEx3", "EXERCISE 3 · 共軛更新",
           "Beta(1,1) 先驗配上 0 次正面、0 次反面，後驗為何？",
           [(True, "仍是 Beta(1,1)", "對。沒有資料時，概似對所有 p 相同，後驗等於先驗。"),
            (False, "Beta(0,0)", "更新是把計數加到先驗參數；零筆資料不會把參數清零。"),
            (False, "MLE 為 0.5，所以後驗集中在 0.5", "沒有資料時每個 p 都同樣使概似最大，MLE 不唯一，也沒有理由把分布壓在 0.5。")])
    + quiz("qEx4", "EXERCISE 4 · 後驗預測",
           "後驗是 Beta(9,5)。下一次投擲出現正面的後驗預測機率是多少？",
           [(False, "$9/(9+5+1)$", "不需要再加一筆尚未觀察的資料。"),
            (True, "$9/(9+5)$", "對。Bernoulli 下一次成功的後驗預測機率等於 p 的後驗平均。"),
            (False, "$9/5$", "這是兩個參數的比值，且超過 1，不能是機率。")])
    + f'<p><a href="{WEB}#section1">題目依 Seeing Theory Ch.5 的 Bayes、Likelihood 與 Prior to Posterior 定義重新編寫</a>；'
      f'<a href="{PDF}#page=49">講義 p.49–54</a>。</p>'
)

BODIES["reference"] = r"""
  <p>先判斷你要算的是事件機率、參數的相對支持度，或參數的後驗分布，再選公式。</p>
""" + table(
    ["概念", "用途", "Seeing Theory 原站", "講義頁"],
    [["Bayes 公式", "由結果更新未知狀態", f'<a href="{WEB}#section1">Bayes\' Theorem</a>', f'<a href="{PDF}#page=49">p.49–50</a>'],
     ["概似", "固定資料，比較參數", f'<a href="{WEB}#section2">Likelihood Function</a>', f'<a href="{PDF}#page=51">p.51–52</a>'],
     ["先驗到後驗", "結合先驗與資料", f'<a href="{WEB}#section3">Prior to Posterior</a>', f'<a href="{PDF}#page=52">p.52–54</a>']],
) + r"""
  <p class="ver-note">本頁為不需要 Python 的概念先備頁。原始參數與公式依 Seeing Theory Chapter 5：
  網頁定義「L(θ | x) = P(x | θ)」，並以 Beta(α, β) 先驗更新硬幣正面機率；PDF 印刷頁 49–54。
  本頁算例、正規化密度、相對概似與端點處理均重新計算，未複製原站文字、程式碼或圖片。</p>
"""


PAGEJS = r"""
/* ═══ w25bayes：Beta–Binomial 先驗、相對概似與後驗 ═══ */
const w25bayesS = HC.svg('w25bayesSvg', {w: 620, h: 470, pad: {l: 58, r: 18, t: 24, b: 38}});
let w25bayesState = {alpha: 1, beta: 1, success: 0, failure: 0};

function w25logGamma(z) {
  const p = [0.9999999999998099, 676.5203681218851, -1259.1392167224028,
    771.3234287776531, -176.6150291621406, 12.5073432786869,
    -0.1385710952657201, 0.00000998436957802, 0.000000150563273515];
  if (z < 0.5) return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * z)) - w25logGamma(1 - z);
  z -= 1;
  let x = p[0];
  for (let i = 1; i < p.length; i++) x += p[i] / (z + i);
  const t = z + 7.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}
function w25logBeta(a, b) { return w25logGamma(a) + w25logGamma(b) - w25logGamma(a + b); }
function w25betaDensity(x, a, b) {
  if (x === 0) return a === 1 ? Math.exp(-w25logBeta(a, b)) : 0;
  if (x === 1) return b === 1 ? Math.exp(-w25logBeta(a, b)) : 0;
  return Math.exp((a - 1) * Math.log(x) + (b - 1) * Math.log1p(-x) - w25logBeta(a, b));
}
function w25logLike(x, s, f) {
  if (s + f === 0) return 0;
  if (x === 0) return s === 0 ? 0 : -Infinity;
  if (x === 1) return f === 0 ? 0 : -Infinity;
  return s * Math.log(x) + f * Math.log1p(-x);
}
function w25bayesRead() {
  w25bayesState.alpha = Number(document.getElementById('w25alpha').value);
  w25bayesState.beta = Number(document.getElementById('w25beta').value);
  w25bayesState.success = Number(document.getElementById('w25success').value);
  w25bayesState.failure = Number(document.getElementById('w25failure').value);
}
function w25bayesDraw() {
  if (!w25bayesS) return;
  w25bayesRead();
  const st = w25bayesState, pa = st.alpha + st.success, pb = st.beta + st.failure;
  const xs = HC.stat.seq(0, 1, 201);
  const prior = xs.map(x => w25betaDensity(x, st.alpha, st.beta));
  const post = xs.map(x => w25betaDensity(x, pa, pb));
  const n = st.success + st.failure;
  const mle = n ? st.success / n : NaN;
  const maxLog = n ? w25logLike(mle, st.success, st.failure) : 0;
  const like = xs.map(x => Math.exp(w25logLike(x, st.success, st.failure) - maxLog));
  const ymax = Math.max(1, ...prior, ...post) * 1.12;
  const g = w25bayesS.clearLayer('main');
  w25bayesS.domain([0, 1], [0, ymax]);
  const split = 286;
  const topY = v => 24 + (230 - 24) * (1 - v / ymax);
  const botY = v => 286 + (416 - 286) * (1 - v);
  for (let i = 0; i <= 5; i++) {
    const x = 58 + (620 - 58 - 18) * i / 5;
    w25bayesS.add('line', {x1: x, y1: 24, x2: x, y2: 416, cls: 'gridl'}, g);
    w25bayesS.txtPx(x, 438, (i / 5).toFixed(1), {anchor: 'middle'}, g);
  }
  [24, 230, split, 416].forEach(y => w25bayesS.add('line', {x1: 58, y1: y, x2: 602, y2: y, cls: 'ax'}, g));
  w25bayesS.txtPx(58, 16, '正規化密度', {cls: 'axtitle'}, g);
  [0, ymax/2, ymax].forEach(v => w25bayesS.txtPx(52, topY(v)+4, HC.fmt(v, 2), {anchor:'end'}, g));
  w25bayesS.txtPx(58, 275, '相對概似', {cls: 'axtitle'}, g);
  [0, .5, 1].forEach(v => w25bayesS.txtPx(52, botY(v)+4, HC.fmt(v, 1), {anchor:'end'}, g));
  w25bayesS.txtPx(330, 463, '硬幣正面機率 p', {cls: 'axtitle', anchor: 'middle'}, g);
  const xpx = x => 58 + (620 - 58 - 18) * x;
  const makePts = (ys, yfn) => ys.map((y, i) => xpx(xs[i]) + ',' + yfn(y)).join(' ');
  w25bayesS.add('polyline', {points: makePts(prior, topY), fill: 'none', stroke: HC.tok.accent2,
    'stroke-width': 3, cls: 'priorcurve'}, g);
  w25bayesS.add('polyline', {points: makePts(post, topY), fill: 'none', stroke: HC.tok.accent,
    'stroke-width': 3, cls: 'postcurve'}, g);
  w25bayesS.add('polyline', {points: makePts(like, botY), fill: 'none', stroke: HC.tok.train,
    'stroke-width': 3, cls: 'likecurve'}, g);
  w25bayesS.txtPx(74, 50, '先驗密度（藍）', {cls:'w25legend', fill: HC.tok.accent2}, g);
  w25bayesS.txtPx(250, 50, '後驗密度（紅）', {cls:'w25legend', fill: HC.tok.accent}, g);
  w25bayesS.txtPx(74, 316, '相對概似（峰值 = 1）', {cls:'w25legend', fill: HC.tok.train}, g);
  if (n) w25bayesS.add('line', {x1: xpx(mle), y1: 286, x2: xpx(mle), y2: 416,
    stroke: HC.tok.ink, 'stroke-width': 1.5, 'stroke-dasharray': '5 4', cls: 'mleline'}, g);
  document.getElementById('w25alphaOut').textContent = st.alpha;
  document.getElementById('w25betaOut').textContent = st.beta;
  document.getElementById('w25successOut').textContent = st.success;
  document.getElementById('w25failureOut').textContent = st.failure;
  document.getElementById('w25priorRead').textContent = 'Beta(' + st.alpha + ', ' + st.beta + ')';
  document.getElementById('w25dataRead').textContent = st.success + ' 正、' + st.failure + ' 反';
  document.getElementById('w25postRead').textContent = 'Beta(' + pa + ', ' + pb + ')';
  document.getElementById('w25meanRead').textContent = HC.fmt(pa / (pa + pb), 3);
  document.getElementById('w25mleRead').textContent = n ? HC.fmt(mle, 3) : '不唯一（無資料）';
  setStatus('w25bayesStatus', n
    ? '資料為 <b>' + st.success + ' 正、' + st.failure + ' 反</b>；後驗平均 '
      + HC.fmt(pa / (pa + pb), 3) + '，MLE ' + HC.fmt(mle, 3) + '。上下圖縱軸意義不同。'
    : '尚無資料：後驗等於先驗；相對概似處處為 1，MLE <b>不唯一</b>，資料無法選出單一值。');
}
function w25bayesReset() {
  [['w25alpha', 1], ['w25beta', 1], ['w25success', 0], ['w25failure', 0]].forEach(pair => {
    document.getElementById(pair[0]).value = pair[1];
  });
  w25bayesDraw();
}
['w25alpha', 'w25beta', 'w25success', 'w25failure'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', w25bayesDraw);
});
if (w25bayesS) w25bayesDraw();
"""


if __name__ == "__main__":
    apply("s5_bayesian", BODIES, PAGEJS)
