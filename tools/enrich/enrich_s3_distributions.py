#!/usr/bin/env python3
"""s3_distributions.html（統計先備 S3 · 隨機變數與分佈）完整自學充實。冪等。

內容依據 Seeing Theory 第 3 章網頁與講義第 31–40 頁，文字、數值例與互動皆為
本站重新設計。這是概念頁，不引用課程 lab，也不產生 deck-extra 卡。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, hook, info, info_card, qa, quiz, rows_card, svg, table, viz  # noqa: E402

ST3 = "https://seeing-theory.brown.edu/probability-distributions/index.html"
STPDF = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf"


def source(section, page):
    return (f'<p class="source-note"><strong>原始教材：</strong>'
            f'<a href="{ST3}">Seeing Theory 第 3 章 · {section}</a> · '
            f'<a href="{STPDF}#page={page}">PDF p.{page}</a>。'
            '本頁文字、例題與圖均重新製作。</p>')


def accessible_svg(sid, label, height):
    return svg(sid, height).replace("<svg ", f'<svg role="img" aria-label="{label}" ')


BODIES = {}

BODIES["variables"] = f"""
  <p>隨機變數（random variable）是一條規則：它把每個隨機結果對應到一個數。
  隨機的是實驗結果；映射規則本身在實驗前已經定好。把結果變成數字後，我們才能談平均、變異數與分佈。</p>

  <p><strong>數值例。</strong>擲兩次公平硬幣，樣本空間是
  $\\Omega=\\{{HH,HT,TH,TT\\}}$。令 $X$ 為正面次數，則
  $X(HH)=2$、$X(HT)=X(TH)=1$、$X(TT)=0$。注意 HT 與 TH 是不同結果，卻映到同一個數值 1。</p>

{table(["原始結果 $\\omega$", "HH", "HT", "TH", "TT"], [
    ["$X(\\omega)$：正面次數", "2", "1", "1", "0"],
    ["結果本身的機率", "$1/4$", "$1/4$", "$1/4$", "$1/4$"],
])}

  <p>把映到相同數值的機率加起來，就得到 $P(X=0)=1/4$、$P(X=1)=1/2$、$P(X=2)=1/4$。
  這三個機率合起來才是 $X$ 的機率分佈（probability distribution）。</p>

{info("分清兩層", "樣本空間列的是實驗結果；隨機變數的取值是數字。"
      "兩個不同結果可以有相同的隨機變數值。")}

{quiz("qVar", "PART 01 · 自我檢測", "擲兩次公平硬幣，令 $X$ 為正面次數。$P(X=1)$ 是多少？", [
    (False, "$1/4$", "只有單一結果的機率是 1/4；X=1 包含 HT 與 TH 兩個結果。"),
    (True, "$1/2$", "對。HT 與 TH 都映到 1，所以機率為 1/4+1/4。"),
    (False, "$1$", "X 的可能值有 0、1、2；所有值的機率加總才是 1。"),
])}
{source("Random Variables", 31)}
"""

BODIES["density"] = f"""
  <p>離散隨機變數只有有限或可數個可能值，使用機率質量函數（probability mass function, PMF）：
  每根柱子的高度就是某一點的機率。連續隨機變數則使用機率密度函數（probability density function, PDF）：
  <strong>區間下方的面積</strong>才是機率。</p>
  $$P(X=x)=p(x)\\quad\\text{{（離散）}},\\qquad
    P(a\\le X\\le b)=\\int_a^b f(x)\\,dx\\quad\\text{{（連續）}}.$$

{info("密度不是點機率", "連續分佈在任何單一點的機率都是 0；密度 $f(x)$ 可以大於 1，"
      "只要整條曲線下的總面積是 1。", "warm")}

  <p><strong>數值例。</strong>若 $X\\sim U(2,6)$，密度高度為 $1/(6-2)=1/4$。
  因此 $P(3\\le X\\le5)$ 是寬 2、高 $1/4$ 的長方形面積，也就是 $1/2$。
  但 $P(X=4)=0$；單點沒有寬度，因此沒有面積。</p>
  <p><strong>累積分布函數（cumulative distribution function, CDF）</strong>
  把左側已累積的機率記成 $F(x)=P(X\\le x)$。它對離散與連續變數都適用。</p>
  $$P(a&lt;X\\le b)=F(b)-F(a).$$
  <p>若是連續分布，端點的機率為 0，上式也等於 $P(a\\le X\\le b)$。
  若是離散分布，想把左端點 $a$ 也算入，還要加上 $P(X=a)$。
  以上面的 $U(2,6)$ 為例，$F(5)=3/4$、$F(3)=1/4$，相減就得到區間機率 $1/2$。
  公式中的積分符號 ∫ 表示曲線下面積，本頁以長方形與圖形理解，不需要先會積分運算。</p>

{table(["類型", "可能值", "圖的高度代表", "區間機率"], [
    ["離散", "有限或可數", "該點的機率", "把區間內的 PMF 相加"],
    ["連續", "一段連續範圍", "每單位長度的機率密度", "對 PDF 積分，即曲線下面積"],
])}

{quiz("qDensity", "PART 02 · 自我檢測", "某連續分佈在 $x=2$ 的密度是 1.4。下列哪個判讀正確？", [
    (False, "$P(X=2)=1.4$", "連續變數在單點的機率是 0；密度高度不是點機率。"),
    (True, "密度可以高於 1，但總面積仍須等於 1", "對。很窄的支撐範圍可以有高密度，機率由面積決定。"),
    (False, "這一定是無效分佈，因為機率不能超過 1", "機率不能超過 1，但密度不是機率。需要檢查的是積分總面積。"),
])}
{source("Discrete and Continuous", 34)}
"""

BODIES["families"] = f"""
  <p>分佈族把常見的隨機機制寫成少數參數。Bernoulli 表示一次成敗；二項分佈表示
  $n$ 次獨立、同成功率的 Bernoulli 試驗中成功幾次；均勻分佈把固定區間內等長區段給相同機率；
  常態分佈由中心 $\\mu$ 與尺度 $\\sigma$ 決定。</p>

{viz(accessible_svg("w23distSvg", "所選機率分佈與指定區間機率", 360),
     [info_card("四個分佈族",
                "選分佈後調參數，再指定區間。離散分佈把區間內柱子機率相加；"
                "連續分佈計算區間下方面積。"),
      rows_card("目前摘要", [
          ("平均值", "0.5", "w23distMean"),
          ("變異數", "0.25", "w23distVar"),
          ("區間機率", "1.0000", "w23distProb"),
          ("計算方式", "區間內 PMF 相加", "w23distHow"),
      ]),
      info_card("參數條件",
                "Bernoulli／二項：$0\\le p\\le1$；二項的 $n$ 為正整數。"
                "均勻：$a&lt;b$。常態：$\\sigma&gt;0$。元件會把輸入限制在有效範圍。")],
     "w23distStatus", "Bernoulli：一次成敗，藍色柱表示指定區間內的機率。",
     '<label>分佈 <select id="w23distKind" aria-label="選擇機率分佈" onchange="w23distChange()">'
     '<option value="bernoulli">Bernoulli</option><option value="binomial">二項</option>'
     '<option value="uniform">均勻</option><option value="normal">常態</option></select></label>'
     '<label><span id="w23distALabel">p</span> <input id="w23distA" type="number" step="0.05" value="0.5" '
     'aria-label="第一個分佈參數" oninput="w23distDraw()"></label>'
     '<label><span id="w23distBLabel">未使用</span> <input id="w23distB" type="number" step="1" value="5" '
     'aria-label="第二個分佈參數" oninput="w23distDraw()" disabled></label>'
     '<label>區間左端 <input id="w23distLo" type="number" step="0.1" value="0" '
     'aria-label="機率區間左端" oninput="w23distDraw()"></label>'
     '<label>區間右端 <input id="w23distHi" type="number" step="0.1" value="1" '
     'aria-label="機率區間右端" oninput="w23distDraw()"></label>'
     '<button class="btn btn-reset" onclick="w23distReset()">重置</button>',
     provenance=("illustrative", "本站自訂即時計算；常態區間機率使用 shared.js 的常態 CDF 近似。"))}

{table(["分佈", "記號與參數", "平均值", "變異數", "常見用途"], [
    ["Bernoulli", "$X\\sim\\mathrm{{Bernoulli}}(p)$", "$p$", "$p(1-p)$", "一次成敗"],
    ["二項", "$X\\sim\\mathrm{{Binomial}}(n,p)$", "$np$", "$np(1-p)$", "$n$ 次獨立同率試驗的成功數"],
    ["均勻", "$X\\sim U(a,b)$", "$(a+b)/2$", "$(b-a)^2/12$", "區間內等長範圍等可能"],
    ["常態", "$X\\sim N(\\mu,\\sigma^2)$", "$\\mu$", "$\\sigma^2$", "許多小效應相加的連續量"],
])}

{quiz("qFamily", "PART 03 · 自我檢測", "每件產品獨立通過檢驗的機率為 0.8，隨機檢查 10 件並記錄通過件數。哪個模型最合適？", [
    (False, "$\\mathrm{{Bernoulli}}(0.8)$", "Bernoulli 只描述一次檢驗；題目記錄 10 次中的通過總數。"),
    (True, "$\\mathrm{{Binomial}}(10,0.8)$", "對。固定 10 次、各次獨立、成功率相同，並計算成功數。"),
    (False, "$N(0.8,10)$", "常態是連續分佈，會產生非整數與範圍外的值；這裡的精確模型是二項。"),
])}
{source("Discrete and Continuous", 35)}
"""

BODIES["sampling"] = f"""
  <p>母體分佈描述單一觀測 $X$ 可能長什麼樣；抽樣分佈（sampling distribution）描述
  一個統計量在<strong>重複抽取新樣本</strong>時如何變動。兩者的隨機對象不同。</p>

  <p><strong>數值例。</strong>若一次公平擲骰的平均為 $\\mu=3.5$、變異數為
  $\\sigma^2=35/12$，每次獨立擲 25 顆並取平均，則</p>
  $$E(\\bar X)=3.5,\\qquad
    \\operatorname{{Var}}(\\bar X)=\\frac{{35/12}}{{25}}=\\frac{{7}}{{60}},\\qquad
    \\operatorname{{SD}}(\\bar X)\\approx0.342.$$
  <p>單顆骰子的結果仍然散在 1 到 6；25 顆的平均會集中在 3.5 附近。
  樣本平均的變異數縮小為原來的 $1/n$，標準差縮小為 $1/\\sqrt n$。</p>

{table(["分佈", "一次重複實驗記錄什麼", "平均", "標準差"], [
    ["原始分佈", "一個觀測 $X$", "$\\mu$", "$\\sigma$"],
    ["樣本平均的抽樣分佈", "$n$ 個觀測的平均 $\\bar X$", "$\\mu$", "$\\sigma/\\sqrt n$"],
])}

{hook("後續用途", "<a href='linear_regression.html#inference'>線性迴歸的係數推論</a>要理解估計量在重複抽樣下如何變動；"
      "<a href='resampling_methods.html#bootstrap'>Bootstrap</a>則用重抽樣近似難以直接推導的抽樣分佈。")}

{quiz("qSampling", "PART 04 · 自我檢測", "母體標準差為 12。獨立抽樣 $n=36$ 時，樣本平均的標準差是多少？", [
    (False, "$12/36=1/3$", "標準差按 1/√n 縮小；按 1/n 縮小的是變異數。"),
    (True, "$12/\\sqrt{{36}}=2$", "對。樣本平均的標準差，也就是標準誤，為 σ/√n。"),
    (False, "$12\\sqrt{{36}}=72$", "平均多個獨立觀測會更集中，標準差不會放大。"),
])}
{source("Central Limit Theorem 前的抽樣準備", 38)}
"""

BODIES["clt"] = f"""
  <p>中央極限定理（central limit theorem, CLT）描述樣本平均的<strong>分佈形狀</strong>。
  若 $X_1,X_2,\\ldots$ 獨立同分佈（i.i.d.），且有有限平均 $\\mu$ 與
  $0&lt;\\sigma^2&lt;\\infty$，則</p>
  $$\\frac{{\\bar X-\\mu}}{{\\sigma/\\sqrt n}}
    \\xrightarrow{{d}}N(0,1),$$
  <p>也就是 $n$ 足夠大時，$\\bar X$ 的分佈近似 $N(\\mu,\\sigma^2/n)$。
  「足夠大」沒有統一門檻；母體愈偏斜或尾端愈重，常態近似通常需要更大的 $n$。</p>

{viz(accessible_svg("w23cltSvg", "固定種子模擬的樣本平均分佈與常態近似", 360),
     [info_card("固定母體：指數分佈",
                "原始 $X$ 右偏，平均與變異數都是 1。每次取 $n$ 個 i.i.d. 觀測的平均，"
                "重複 160 次。藍色柱為模擬樣本平均，綠線為同平均、同變異數的常態近似。"),
      rows_card("目前模擬", [
          ("每組樣本數 n", "1", "w23cltNOut"),
          ("樣本平均的平均", "—", "w23cltMean"),
          ("樣本平均的標準差", "—", "w23cltSd"),
          ("理論標準差", "1.000", "w23cltTheo"),
      ]),
      info_card("兩個定理回答不同問題",
                "大數法則（LLN）說 $\\bar X$ 會靠近 $\\mu$；CLT 說標準化後的抽樣分佈趨近常態。"
                "在條件成立時，對任何固定的正誤差門檻，平均偏離母體平均超過門檻的機率趨近 0；"
                "單次路徑不保證每加一筆都更接近。")],
     "w23cltStatus", "n=1 時，樣本平均就是原始觀測，分佈仍明顯右偏。",
     '<label>每組樣本數 <select id="w23cltN" aria-label="每組樣本數" onchange="w23cltDraw()">'
     '<option value="1">1</option><option value="2">2</option><option value="5">5</option>'
     '<option value="10">10</option></select></label>'
     '<button class="btn btn-step" onclick="w23cltNext()">→ 增加樣本數</button>'
     '<button class="btn btn-reset" onclick="w23cltReset()">重置</button>',
     provenance=("simulation", "固定種子 20260923；每次 160 組，每組最多 10 筆，共最多 1,600 次抽樣。"))}

{quiz("qClt", "PART 05 · 自我檢測", "下列哪個條件組合符合本頁使用的中央極限定理版本？", [
    (False, "觀測值必須本來就是常態分佈", "CLT 的用途之一正是讓非正常母體的樣本平均在大樣本下近似常態。"),
    (True, "觀測 i.i.d.，母體平均有限，且 $0&lt;\\sigma^2&lt;\\infty$", "對。正且有限的變異數讓標準化分母有意義；若有依賴或無限變異數，需要其他版本或方法。"),
    (False, "樣本平均必須隨每筆新資料單調靠近母體平均", "LLN 與 CLT 都沒有要求逐步單調；有限樣本的平均可以上下波動。"),
])}
{source("Central Limit Theorem", 39)}
"""

BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 原創", "擲一顆公平骰子，令 $X=1$ 表示點數大於 4，否則 $X=0$。$X$ 的分佈為何？", [
    (True, "$\\mathrm{{Bernoulli}}(1/3)$", "對。成功結果是 5、6，共占六個等可能結果中的兩個。"),
    (False, "$\\mathrm{{Binomial}}(6,1/3)$", "只擲一次，所以是一次 Bernoulli；n=6 不是骰子的面數。"),
    (False, "$U(1,6)$", "X 只取 0 或 1；均勻分佈 U(1,6) 是連續模型。"),
])}
{quiz("qEx2", "EXERCISE 2 · 原創", "若 $X\\sim U(0,8)$，$P(2\\le X\\le5)$ 為何？", [
    (False, "$2/8$", "區間 [2,5] 的長度是 3，不是左端點 2。"),
    (True, "$3/8$", "對。均勻分佈的機率等於子區間長度 3 除以總長度 8。"),
    (False, "$5/8$", "5 是右端點，不是區間長度；要用 5−2。"),
])}
{quiz("qEx3", "EXERCISE 3 · 原創", "某母體平均為 50、標準差為 18。獨立抽樣 81 筆時，樣本平均的平均與標準差為何？", [
    (False, "平均 50、標準差 18", "樣本平均保留母體平均，但標準差會縮小。"),
    (True, "平均 50、標準差 2", "對。E(平均)=50，SD(平均)=18/√81=2。"),
    (False, "平均 50/81、標準差 18/81", "取平均不會把期望值除以 n；標準差則除以 √n。"),
])}
{quiz("qEx4", "EXERCISE 4 · 原創", "增加樣本數後，某次樣本平均反而離母體平均更遠。這與大數法則矛盾嗎？", [
    (False, "矛盾，因為誤差必須每一步都下降", "大數法則沒有單調保證；單次路徑可以暫時走遠。"),
    (True, "不矛盾；定理描述長期機率行為，不保證逐步單調", "對。樣本數增加會讓大幅偏離愈來愈不可能，但某一步仍可反向波動。"),
    (False, "不矛盾，因為樣本平均永遠不會收斂", "在條件成立時樣本平均會收斂；錯的是把收斂誤讀成每一步都更近。"),
])}
  <p class="source-note"><strong>題目來源：</strong>四題均為本站原創，觀念範圍對照
  <a href="{ST3}">Seeing Theory 第 3 章</a>與<a href="{STPDF}#page=31">PDF pp.31–40</a>。</p>
"""

BODIES["reference"] = f"""
{table(["概念", "核心式", "常見誤讀"], [
    ["PMF", "$P(X=x)=p(x)$", "柱高就是離散點機率"],
    ["PDF", "$P(a\\le X\\le b)=\\int_a^b f(x)dx$", "密度高度不是單點機率"],
    ["樣本平均", "$E(\\bar X)=\\mu$", "平均不會除以 n"],
    ["樣本平均的變異", "$\\operatorname{{Var}}(\\bar X)=\\sigma^2/n$", "標準差是 $\\sigma/\\sqrt n$"],
    ["LLN", "$\\bar X$ 靠近 $\\mu$", "不保證逐步單調"],
    ["CLT", "$(\\bar X-\\mu)/(\\sigma/\\sqrt n)\\Rightarrow N(0,1)$", "描述抽樣分佈，不要求原始母體常態"],
])}
  <p><a href="{ST3}">Seeing Theory · Probability Distributions</a>提供隨機變數、離散／連續分佈與 CLT 的原始互動章節；
  <a href="{STPDF}#page=31">Seeing Theory PDF pp.31–40</a>提供定義、分佈族與定理脈絡。</p>
  <p class="ver-note">本頁例題、測驗與互動圖均為本站原創；CLT 圖使用固定種子 20260923，每次最多模擬 1,600 個觀測。頁面沒有課程 lab 卡，也沒有烘焙圖表；重置會完整回到預設分佈、參數與種子狀態。</p>
"""


PAGEJS = r"""
const w23distS = HC.svg('w23distSvg', {h: 360, pad: {l: 54, r: 18, t: 24, b: 44}});

function w23clip(v, lo, hi, fallback) {
  const x = Number(v);
  return Number.isFinite(x) ? Math.max(lo, Math.min(hi, x)) : fallback;
}

function w23choose(n, k) {
  if (k < 0 || k > n) return 0;
  let out = 1;
  const m = Math.min(k, n - k);
  for (let i = 1; i <= m; i++) out = out * (n - m + i) / i;
  return out;
}

function w23binomPmf(k, n, p) {
  return w23choose(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
}

function w23distDiscrete(kind, a, b, lo, hi) {
  const n = kind === 'bernoulli' ? 1 : Math.round(b);
  const probs = [];
  for (let k = 0; k <= n; k++) {
    probs.push(kind === 'bernoulli'
      ? (k === 1 ? a : 1 - a)
      : w23binomPmf(k, n, a));
  }
  const left = Math.ceil(Math.min(lo, hi)), right = Math.floor(Math.max(lo, hi));
  let prob = 0;
  for (let k = Math.max(0, left); k <= Math.min(n, right); k++) prob += probs[k];
  const ymax = Math.max(0.12, Math.max.apply(null, probs) * 1.18);
  w23distS.domain([-0.6, n + 0.6], [0, ymax]);
  w23distS.grid(Math.min(n + 1, 10), 4, {xtitle: 'x', ytitle: 'P(X=x)', ydec: 2});
  const g = w23distS.clearLayer('main');
  const width = Math.max(7, Math.min(34, w23distS.iw / (n + 1) * 0.62));
  probs.forEach((v, k) => {
    const selected = k >= left && k <= right;
    const x = w23distS.X(k) - width / 2, y = w23distS.Y(v);
    w23distS.add('rect', {x: x, y: y, width: width, height: w23distS.Y(0) - y,
                          rx: 3, fill: selected ? HC.tok.accent2 : HC.tok.cardBorder}, g);
  });
  return prob;
}

function w23distContinuous(kind, a, b, lo, hi) {
  let xmin, xmax, mean, sd, density, prob;
  const left = lo, right = hi;
  if (kind === 'uniform') {
    xmin = a - (b - a) * 0.15;
    xmax = b + (b - a) * 0.15;
    mean = (a + b) / 2;
    sd = (b - a) / Math.sqrt(12);
    density = x => (x >= a && x <= b ? 1 / (b - a) : 0);
    prob = Math.max(0, Math.min(b, right) - Math.max(a, left)) / (b - a);
  } else {
    mean = a;
    sd = b;
    xmin = mean - 4 * sd;
    xmax = mean + 4 * sd;
    density = x => HC.stat.dnorm(x, mean, sd);
    prob = HC.stat.pnorm((right - mean) / sd) - HC.stat.pnorm((left - mean) / sd);
  }
  const ymax = density(mean) * 1.18;
  w23distS.domain([xmin, xmax], [0, ymax]);
  w23distS.grid(6, 4, {xtitle: 'x', ytitle: '密度', xdec: 1, ydec: 2});
  const g = w23distS.clearLayer('main');
  if (kind === 'uniform') {
    const height = 1 / (b - a);
    const shadeLo = Math.max(a, left), shadeHi = Math.min(b, right);
    if (shadeHi > shadeLo) {
      w23distS.box(shadeLo, 0, shadeHi, height,
                   {fill: HC.tok.accent2, stroke: HC.tok.accent2, sw: 0}, g);
    }
    w23distS.seg(a, 0, a, height, {cls: 'w23curve', stroke: HC.tok.accent, sw: 3}, g);
    w23distS.seg(a, height, b, height, {cls: 'w23curve', stroke: HC.tok.accent, sw: 3}, g);
    w23distS.seg(b, height, b, 0, {cls: 'w23curve', stroke: HC.tok.accent, sw: 3}, g);
  } else {
    const xs = HC.stat.seq(xmin, xmax, 121);
    const pts = xs.map(x => [x, density(x)]);
    const shadeLo = Math.max(xmin, left), shadeHi = Math.min(xmax, right);
    if (shadeHi > shadeLo) {
      const areaPts = HC.stat.seq(shadeLo, shadeHi, 61).map(x => [x, density(x), 0]);
      w23distS.area(areaPts, {fill: HC.tok.accent2}, g);
    }
    w23distS.poly(pts, {cls: 'w23curve', stroke: HC.tok.accent, sw: 3}, g);
  }
  return Math.max(0, Math.min(1, prob));
}

function w23distChange() {
  const kind = document.getElementById('w23distKind').value;
  const a = document.getElementById('w23distA');
  const b = document.getElementById('w23distB');
  const al = document.getElementById('w23distALabel');
  const bl = document.getElementById('w23distBLabel');
  if (kind === 'bernoulli') {
    al.textContent = 'p'; bl.textContent = '未使用'; a.value = '0.5'; b.value = '5'; b.disabled = true;
    document.getElementById('w23distLo').value = '0'; document.getElementById('w23distHi').value = '1';
  } else if (kind === 'binomial') {
    al.textContent = 'p'; bl.textContent = 'n'; a.value = '0.5'; b.value = '10'; b.disabled = false;
    document.getElementById('w23distLo').value = '3'; document.getElementById('w23distHi').value = '7';
  } else if (kind === 'uniform') {
    al.textContent = 'a'; bl.textContent = 'b'; a.value = '0'; b.value = '8'; b.disabled = false;
    document.getElementById('w23distLo').value = '2'; document.getElementById('w23distHi').value = '5';
  } else {
    al.textContent = 'μ'; bl.textContent = 'σ'; a.value = '0'; b.value = '1'; b.disabled = false;
    document.getElementById('w23distLo').value = '-1'; document.getElementById('w23distHi').value = '1';
  }
  w23distDraw();
}

function w23distDraw() {
  if (!w23distS) return;
  const kind = document.getElementById('w23distKind').value;
  let a = Number(document.getElementById('w23distA').value);
  let b = Number(document.getElementById('w23distB').value);
  let lo = w23clip(document.getElementById('w23distLo').value, -100, 100, 0);
  let hi = w23clip(document.getElementById('w23distHi').value, -100, 100, 1);
  if (lo > hi) {
    const oldLo = lo;
    lo = hi;
    hi = oldLo;
  }
  document.getElementById('w23distLo').value = String(lo);
  document.getElementById('w23distHi').value = String(hi);
  let mean, variance, prob, how, label;
  if (kind === 'bernoulli' || kind === 'binomial') {
    a = w23clip(a, 0, 1, 0.5);
    b = kind === 'bernoulli' ? 1 : Math.round(w23clip(b, 1, 20, 10));
    document.getElementById('w23distA').value = String(a);
    if (kind === 'binomial') document.getElementById('w23distB').value = String(b);
    mean = b * a; variance = b * a * (1 - a);
    prob = w23distDiscrete(kind, a, b, lo, hi);
    how = '區間內 PMF 相加';
    label = kind === 'bernoulli' ? 'Bernoulli：一次成敗' : '二項：' + b + ' 次獨立同率試驗的成功數';
  } else if (kind === 'uniform') {
    a = w23clip(a, -50, 49.9, 0);
    b = w23clip(b, a + 0.1, 50, a + 1);
    document.getElementById('w23distA').value = String(a);
    document.getElementById('w23distB').value = String(b);
    mean = (a + b) / 2; variance = (b - a) * (b - a) / 12;
    prob = w23distContinuous(kind, a, b, lo, hi);
    how = '區間長度／總長度'; label = '均勻：等長區間有相同機率';
  } else {
    a = w23clip(a, -50, 50, 0);
    b = w23clip(b, 0.1, 20, 1);
    document.getElementById('w23distA').value = String(a);
    document.getElementById('w23distB').value = String(b);
    mean = a; variance = b * b;
    prob = w23distContinuous(kind, a, b, lo, hi);
    how = '常態 CDF 的差'; label = '常態：μ 決定中心，σ 決定尺度；圖窗只顯示 μ±4σ，機率按完整輸入區間計算';
  }
  document.getElementById('w23distMean').textContent = HC.fmt(mean, 3);
  document.getElementById('w23distVar').textContent = HC.fmt(variance, 3);
  document.getElementById('w23distProb').textContent = HC.fmt(prob, 4);
  document.getElementById('w23distHow').textContent = how;
  setStatus('w23distStatus', '<b>' + label + '</b>；著色範圍的機率為 <b>' + HC.fmt(prob, 4) + '</b>。');
}

function w23distReset() {
  document.getElementById('w23distKind').value = 'bernoulli';
  w23distChange();
}

const w23cltS = HC.svg('w23cltSvg', {h: 360, pad: {l: 54, r: 18, t: 24, b: 44}});
const w23cltNs = [1, 2, 5, 10];

function w23cltMeans(n) {
  const rand = HC.stat.lcg(20260923);
  const out = [];
  for (let r = 0; r < 160; r++) {
    let sum = 0;
    for (let i = 0; i < n; i++) sum += -Math.log(Math.max(rand(), 1e-12));
    out.push(sum / n);
  }
  return out;
}

function w23cltDraw() {
  if (!w23cltS) return;
  const n = Number(document.getElementById('w23cltN').value);
  const means = w23cltMeans(n);
  const bins = 18;
  const observedMax = Math.max.apply(null, means);
  const xmax = Math.max(2.2, Math.ceil(observedMax * 5) / 5);
  const width = xmax / bins;
  const counts = Array(bins).fill(0);
  means.forEach(v => { counts[Math.min(bins - 1, Math.floor(v / width))] += 1; });
  const densities = counts.map(c => c / (means.length * width));
  const theorySd = 1 / Math.sqrt(n);
  const normalPeak = HC.stat.dnorm(1, 1, theorySd);
  const ymax = Math.max(normalPeak, Math.max.apply(null, densities)) * 1.16;
  w23cltS.domain([0, xmax], [0, ymax]);
  w23cltS.grid(5, 4, {xtitle: '樣本平均', ytitle: '密度', xdec: 1, ydec: 2});
  const g = w23cltS.clearLayer('main');
  densities.forEach((v, i) => {
    const x0 = i * width, x1 = (i + 1) * width;
    w23cltS.box(x0, 0, x1, v, {fill: HC.tok.accent2, stroke: HC.tok.paper, sw: 0.8}, g);
  });
  const curve = HC.stat.seq(0, xmax, 121).map(x => [x, HC.stat.dnorm(x, 1, theorySd)]);
  w23cltS.poly(curve, {cls: 'w23curve', stroke: HC.tok.accent3, sw: 3}, g);
  const empiricalMean = HC.stat.mean(means), empiricalSd = HC.stat.sd(means);
  document.getElementById('w23cltNOut').textContent = String(n);
  document.getElementById('w23cltMean').textContent = HC.fmt(empiricalMean, 3);
  document.getElementById('w23cltSd').textContent = HC.fmt(empiricalSd, 3);
  document.getElementById('w23cltTheo').textContent = HC.fmt(theorySd, 3);
  setStatus('w23cltStatus', n === 1
    ? '<b>n=1：</b>樣本平均就是原始觀測，分佈仍明顯右偏。'
    : '<b>n=' + n + '：</b>平均集中到 1 附近，抽樣分佈逐漸接近綠色常態曲線。');
}

function w23cltNext() {
  const el = document.getElementById('w23cltN');
  const i = w23cltNs.indexOf(Number(el.value));
  el.value = String(w23cltNs[Math.min(i + 1, w23cltNs.length - 1)]);
  w23cltDraw();
}

function w23cltReset() {
  document.getElementById('w23cltN').value = '1';
  w23cltDraw();
}

if (w23distS) w23distReset();
if (w23cltS) w23cltReset();
"""


if __name__ == "__main__":
    apply("s3_distributions", BODIES, PAGEJS)
