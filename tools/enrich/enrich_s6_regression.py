#!/usr/bin/env python3
"""s6_regression.html：Seeing Theory Ch.6 的概念型統計先備頁。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, hook, info, info_card, quiz, rows_card, svg, table, viz  # noqa: E402


WEB = "https://seeing-theory.brown.edu/regression-analysis/index.html"
PDF = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf"

BODIES = {}

BODIES["covariance"] = r"""
  <p>兩個變數一起高於各自平均，或一起低於各自平均時，中心化後的乘積為正；一高一低時為負。
  <strong>樣本共變異數（sample covariance）</strong>把這些乘積取平均，相關係數再除以兩邊的尺度。</p>
  $$s_{xy}=\frac{1}{n-1}\sum_{i=1}^n(x_i-\bar x)(y_i-\bar y),\qquad
    r=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}
    {\sqrt{\sum_i(x_i-\bar x)^2}\sqrt{\sum_i(y_i-\bar y)^2}}.$$
  <p><strong>算例。</strong>$x=(1,2,3)$、$y=(2,4,5)$，兩者平均為 2 與 $11/3$。
  中心化乘積總和為 3，所以 $s_{xy}=3/2=1.5$；平方和為 2 與 $14/3$，
  因而 $r=3/\sqrt{2(14/3)}\approx0.982$。若改成 $x=(2,2,2)$，其平方和為 0，
  分母也為 0；此時相關係數<strong>未定義</strong>，不能填成 0。</p>
  <p>高相關本身不能證明因果；例如氣溫可同時提高冷飲銷量與用電量，兩者的相關可能來自共同原因。
  相關為 0 也不保證獨立；對稱的 U 形關係可能讓正、負中心化乘積互相抵消。</p>
""" + info(
    "尺度的影響",
    "共變異數有 xy 的乘積單位，換單位會改變數值。相關係數除掉標準差，介於 −1 與 1，適合比較線性關係。",
) + table(
    ["資料形狀", "共變異數／相關", "能否推論"],
    [["沿上升直線", "正，r 接近 1", "有正向線性關係"],
     ["沿下降直線", "負，r 接近 −1", "有負向線性關係"],
     ["U 形", "r 可能接近 0", "仍可能有強烈非線性關係"],
     ["任一變數為常數", "r 未定義", "該變數沒有可標準化的變異"]],
) + quiz(
    "qCovariance", "PART 01 · 自我檢測",
    "把所有 x 值從公尺改成公分（乘以 100），且 100 為正數。相關係數會怎樣？",
    [(False, "也乘以 100", "共變異數會乘以 100，但相關係數的分子、分母會同時縮放。"),
     (True, "保持相同", "對。正的線性換單位不改變標準化後的相關係數。"),
     (False, "變成未定義", "只要原本 x 有變異，乘以 100 後仍有變異，分母不會變成 0。")],
) + f'<p><a href="{WEB}#section2">來源：Seeing Theory Ch.6 · Correlation</a>；<a href="{PDF}#page=61">講義 p.61–63</a>。</p>'

BODIES["least_squares"] = r"""
  <p>簡單線性迴歸用直線 $\hat y=b_0+b_1x$ 預測 $y$。每一筆觀測與直線的垂直差是殘差；
  普通最小平方法（ordinary least squares, OLS）選出讓殘差平方和最小的截距與斜率。</p>
  $$e_i=y_i-\hat y_i,\qquad
    \operatorname{RSS}(b_0,b_1)=\sum_{i=1}^n[y_i-(b_0+b_1x_i)]^2,$$
  $$\hat b_1=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sum_i(x_i-\bar x)^2},
    \qquad \hat b_0=\bar y-\hat b_1\bar x,\qquad S_{xx}&gt;0.$$
  <p><strong>算例。</strong>固定資料 $(0,1),(1,2),(2,2),(3,4),(4,5)$ 的
  $\bar x=2$、$\bar y=2.8$、$S_{xy}=10$、$S_{xx}=10$，所以 OLS 線是
  $\hat y=0.8+1.0x$，RSS 為 0.8。拖動下面兩個滑桿，再按「顯示 OLS 解」核對。</p>
""" + viz(
    svg("w26olsSvg", 430),
    [info_card(
        "圖上的線與方塊",
        "垂直線段是帶正負號的殘差；半透明正方形的邊長對應殘差絕對值，面積對應平方誤差。"
        "右欄 RSS 把五個面積所代表的數值加總。",
    ),
     rows_card("目前模型", [
         ("截距", "0.00", "w26b0Read"),
         ("斜率", "0.00", "w26b1Read"),
         ("RSS", "—", "w26rssRead"),
         ("與最小值差距", "—", "w26gapRead"),
     ]),
     info_card(
         "最小平方的含義",
         "「顯示 OLS 解」會找出這五筆資料中 RSS 最小的截距與斜率。"
         "若所有 x 都相同，$S_{xx}=0$，斜率便無法由資料唯一決定。",
     )],
    "w26olsStatus", "先調整斜率與截距，觀察殘差方塊與 RSS 如何一起改變。",
    '<label>截距 <input id="w26b0" type="range" min="-2" max="4" step="0.1" value="0"></label>'
    '<output id="w26b0Out">0.0</output>'
    '<label>斜率 <input id="w26b1" type="range" min="-1" max="3" step="0.1" value="0"></label>'
    '<output id="w26b1Out">0.0</output>'
    '<button class="btn btn-toggle" onclick="w26olsSolve()">顯示 OLS 解</button>'
    '<button class="btn btn-reset" onclick="w26olsReset()">重置</button>',
    provenance=("illustrative", "五筆固定資料為自訂概念示意；直線、殘差與 RSS 均由滑桿值即時計算。"),
) + quiz(
    "qLeastSquares", "PART 02 · 自我檢測",
    "目前某條線的五個殘差是 1、−1、0、2、−2。它的 RSS 是多少？",
    [(False, "0", "殘差直接相加會正負抵消；OLS 的目標是平方後再加。"),
     (False, "6", "這是殘差絕對值的總和，不是平方和。"),
     (True, "10", "對。$1^2+(-1)^2+0^2+2^2+(-2)^2=10$。")],
) + f'<p><a href="{WEB}#section1">來源：Seeing Theory Ch.6 · Ordinary Least Squares</a>；<a href="{PDF}#page=55">講義 p.55–60</a>。</p>'

BODIES["residuals"] = r"""
  <p>殘差 $e_i=y_i-\hat y_i$ 是觀測值相對於目前模型的剩餘差異。正殘差表示點在預測線上方，
  負殘差表示在下方。含截距的 OLS 會使訓練資料殘差總和為 0，但這只是一階條件，不能證明模型合適。</p>
  <p><strong>算例。</strong>上一節 OLS 線對五筆資料的預測為
  $(0.8,1.8,2.8,3.8,4.8)$，所以殘差為 $(0.2,0.2,-0.8,0.2,0.2)$。
  它們加總為 0，平方和為 $4(0.2^2)+(-0.8)^2=0.8$。中間那筆貢獻 RSS 的 80%，
  顯示平方損失會放大較大的殘差。</p>
  $$\sum_i e_i=0\quad\text{（含截距的訓練 OLS）},\qquad
    R^2=1-\frac{\sum_i e_i^2}{\sum_i(y_i-\bar y)^2}.$$
  <p>這個 R² 公式需要 y 有變異，使分母大於 0；若所有 y 相同，這個比值沒有定義。</p>
""" + info(
    "殘差圖要看什麼",
    "理想上，殘差在 0 上下沒有系統形狀，散布程度也大致穩定。彎曲、漏斗形、群聚或極端點都提示模型假設需要再檢查。",
    "warm",
) + table(
    ["看到的現象", "可能代表", "下一步"],
    [["彎曲圖樣", "線性形式漏掉曲線", "考慮轉換或非線性項"],
     ["散布隨預測值變大", "變異可能不固定", "檢查異質變異與不確定性估計"],
     ["少數很大的殘差", "離群觀測或資料問題", "回查資料並做敏感度分析"],
     ["殘差隨時間成串", "觀測可能相關", "建模時間或群組結構"]],
) + hook(
    "正課的完整診斷",
    "<a href=\"linear_regression.html#problems\">線性迴歸章的六個潛在問題</a>"
    "會接著處理非線性、異質變異、離群值、高槓桿值與共線性。",
) + quiz(
    "qResiduals", "PART 03 · 自我檢測",
    "含截距的 OLS 訓練殘差加總為 0。這足以證明直線模型正確嗎？",
    [(False, "足夠，因為平均誤差是 0", "正負殘差會抵消；彎曲或異質變異仍可能同時存在。"),
     (True, "不足，還要看殘差形狀與模型假設", "對。加總為 0 是 OLS 的代數性質，不能取代診斷。"),
     (False, "不足，因為 OLS 殘差永遠都大於 0", "殘差可正可負；它們在含截距的訓練 OLS 中才會加總為 0。")],
) + f'<p><a href="{WEB}#section1">來源：Seeing Theory Ch.6 · OLS 的誤差平方</a>；<a href="{PDF}#page=57">講義 p.57–60</a>。</p>'

BODIES["anova"] = r"""
  <p>單因子變異數分析（one-way ANOVA）檢定
  $H_0:\mu_1=\mu_2=\cdots=\mu_k$。總平方和可以精確拆成「組間」與「組內」：
  組間衡量各組平均離總平均多遠，組內衡量個體離各自組平均多遠。</p>
  $$SS_{\mathrm{Total}}=SS_{\mathrm{Between}}+SS_{\mathrm{Within}},$$
  $$SS_{\mathrm{Between}}=\sum_{j=1}^k n_j(\bar y_j-\bar y)^2,
    \qquad SS_{\mathrm{Within}}=\sum_{j=1}^k\sum_i(y_{ij}-\bar y_j)^2,$$
  $$F=\frac{MS_{\mathrm{Between}}}{MS_{\mathrm{Within}}}
    =\frac{SS_{\mathrm{Between}}/(k-1)}{SS_{\mathrm{Within}}/(n-k)}.$$
  <p><strong>算例。</strong>A 組 $(1,2)$、B 組 $(3,4)$、C 組 $(5,6)$；三組平均為 1.5、3.5、5.5，
  總平均為 3.5。$SS_{\mathrm{Between}}=16$、$SS_{\mathrm{Within}}=1.5$，
  所以 $SS_{\mathrm{Total}}=17.5$。自由度為 2 與 3，得到 $F=(16/2)/(1.5/3)=16$。</p>
""" + table(
    ["來源", "平方和", "自由度", "均方", "F"],
    [["組間", "16", "3−1=2", "8", "16"],
     ["組內", "1.5", "6−3=3", "0.5", "—"],
     ["總計", "17.5", "6−1=5", "—", "—"]],
) + info(
    "F 檢定的成立條件",
    "典型單因子 ANOVA 假設觀測互相獨立、各組誤差近似常態、各組變異數相同。"
    "F 很大表示組間差異相對於組內變動大；p 值仍須由 F 分布與自由度求得。"
    "拒絕虛無假設只表示至少一個母體平均不同，不能推出每一組彼此都不同。",
    "warm",
) + quiz(
    "qAnova", "PART 04 · 自我檢測",
    "若三組的組平均完全相同，但各組內仍有變動，ANOVA 的 F 會是多少？",
    [(True, "0", "對。組間平方和為 0，分子均方也是 0；組內均方為正時 F=0。"),
     (False, "1", "F=1 代表組間、組內均方相同；組平均完全相同時組間平方和為 0。"),
     (False, "無限大", "無限大會出現在組內均方趨近 0、組間差異仍存在的情況。")],
) + f'<p><a href="{WEB}#section3">來源：Seeing Theory Ch.6 · Analysis of Variance</a>；<a href="{PDF}#page=63">講義 p.63–66</a>。</p>'

BODIES["exercises"] = (
    quiz("qEx1", "EXERCISE 1 · 相關係數",
         "資料完全落在 $y=5-2x$ 上，而且 x 有變異。相關係數是多少？",
         [(False, "2", "相關係數必須介於 −1 與 1。"),
          (True, "−1", "對。所有點都在負斜率直線上，是完全負線性關係。"),
          (False, "0", "負斜率代表 x 增加時 y 一致下降，不是沒有線性關係。")])
    + quiz("qEx2", "EXERCISE 2 · OLS",
           "將某一殘差從 2 增加到 4，其他殘差不變。這一筆對 RSS 的貢獻增加多少？",
           [(False, "2", "這是殘差本身的增加量，RSS 使用平方。"),
            (False, "4", "原貢獻是 4，新貢獻是 16，要計算兩者差。"),
            (True, "12", "對。$4^2-2^2=16-4=12$。")])
    + quiz("qEx3", "EXERCISE 3 · 決定係數",
           "某模型 RSS=20，若只用平均數預測的總平方和 TSS=80，$R^2$ 是多少？",
           [(True, "0.75", "對。$1-20/80=0.75$。"),
            (False, "0.25", "這是 RSS/TSS，代表尚未由模型解釋的比例。"),
            (False, "4", "R² 不是 TSS/RSS；依定義應計算 1−RSS/TSS。")])
    + quiz("qEx4", "EXERCISE 4 · ANOVA",
           "四組、總樣本數 20 的單因子 ANOVA，組間與組內自由度分別是多少？",
           [(False, "4 與 16", "組間需扣掉一個總平均限制，所以不是 k。"),
            (True, "3 與 16", "對。組間 k−1=3，組內 n−k=16。"),
            (False, "3 與 19", "19 是總自由度 n−1；組內還要扣掉四個組平均。")])
    + f'<p><a href="{WEB}#section1">題目依 Seeing Theory Ch.6 的 OLS、Correlation 與 ANOVA 定義重新編寫</a>；'
      f'<a href="{PDF}#page=55">講義 p.55–66</a>。</p>'
)

BODIES["reference"] = r"""
  <p>同一個平方和在迴歸與 ANOVA 中可能使用不同縮寫。閱讀表格時先看定義與下標，再看名稱。</p>
""" + table(
    ["量", "公式核心", "用途", "原站"],
    [["相關 r", "中心化乘積／兩邊平方和", "線性方向與強度", f'<a href="{WEB}#section2">Correlation</a>'],
     ["迴歸 RSS（原站寫 SSE）", "Σ(y−ŷ)²", "選擇 OLS 線", f'<a href="{WEB}#section1">OLS</a>'],
     ["ANOVA 組間／組內 SS", "總變動的兩部分", "比較多組平均", f'<a href="{WEB}#section3">ANOVA</a>']],
) + r"""
  <p class="ver-note">本頁為不需要 Python 的概念先備頁。原始公式依 Seeing Theory Chapter 6：
  網頁列出「b̂1 = Sxy/Sxx」、「SSE = Σ(yi − (b̂0 + b̂1xi))²」、樣本相關係數 r，
  以及「F = [SST/(k−1)]/[SSE/(n−k)]」；PDF 印刷頁 55–66。
  本頁統一改用 RSS、SSBetween、SSWithin 避免同名歧義，所有算例與互動數值均重新計算。</p>
"""


PAGEJS = r"""
/* ═══ w26ols：固定資料的即時最小平方 ═══ */
const w26olsS = HC.svg('w26olsSvg', {xd: [-1, 5], yd: [-1, 7], w: 620, h: 430,
  pad: {l: 54, r: 22, t: 22, b: 42}});
const w26olsX = [0, 1, 2, 3, 4];
const w26olsY = [1, 2, 2, 4, 5];
const w26olsFit = HC.stat.ols(w26olsX, w26olsY);
let w26olsState = {b0: 0, b1: 0};

function w26olsRead() {
  w26olsState.b0 = Number(document.getElementById('w26b0').value);
  w26olsState.b1 = Number(document.getElementById('w26b1').value);
}
function w26olsDraw() {
  if (!w26olsS) return;
  w26olsRead();
  const st = w26olsState;
  const rss = HC.stat.rss(w26olsX, w26olsY, st.b0, st.b1);
  const lineEnds = [st.b0 - st.b1, st.b0 + 5 * st.b1];
  const fits = w26olsX.map(x => st.b0 + st.b1 * x);
  const allY = w26olsY.concat(fits, lineEnds);
  const lo = Math.min(...allY), hi = Math.max(...allY);
  const pad = Math.max(0.8, (hi - lo) * 0.10);
  const yStep = Math.max(1, Math.ceil((hi - lo + 2 * pad) / 4));
  const yLo = Math.floor((lo - pad) / yStep) * yStep;
  const yHi = Math.ceil((hi + pad) / yStep) * yStep;
  w26olsS.domain([-1, 5], [yLo, yHi]);
  const g = w26olsS.clearLayer('main');
  w26olsS.grid(6, (yHi - yLo) / yStep, {xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0});
  w26olsX.forEach((x, i) => {
    const yhat = st.b0 + st.b1 * x;
    const py = w26olsS.Y(w26olsY[i]), phy = w26olsS.Y(yhat);
    const side = Math.abs(py - phy);
    const left = Math.min(w26olsS.X(x) + 7, 602 - side);
    w26olsS.add('rect', {x: left, y: Math.min(py, phy), width: side, height: side,
      fill: HC.tok.accent, opacity: 0.13, stroke: HC.tok.accent, 'stroke-width': 1,
      cls: 'errsquare'}, g);
    w26olsS.seg(x, w26olsY[i], x, yhat, {cls: 'residualx', stroke: HC.tok.accent,
      sw: 2.5}, g);
  });
  w26olsS.seg(-1, st.b0 - st.b1, 5, st.b0 + 5 * st.b1,
    {cls: 'fitline', stroke: HC.tok.train, sw: 3}, g);
  w26olsX.forEach((x, i) => w26olsS.dot(x, w26olsY[i], {r: 5, fill: HC.tok.accent2,
    stroke: HC.tok.paper, sw: 1.5}, g));
  document.getElementById('w26b0Out').textContent = HC.fmt(st.b0, 1);
  document.getElementById('w26b1Out').textContent = HC.fmt(st.b1, 1);
  document.getElementById('w26b0Read').textContent = HC.fmt(st.b0, 2);
  document.getElementById('w26b1Read').textContent = HC.fmt(st.b1, 2);
  document.getElementById('w26rssRead').textContent = HC.fmt(rss, 2);
  document.getElementById('w26gapRead').textContent = HC.fmt(rss - w26olsFit.rss, 2);
  const solved = Math.abs(st.b0 - w26olsFit.b0) < 0.051 && Math.abs(st.b1 - w26olsFit.b1) < 0.051;
  setStatus('w26olsStatus', (solved ? '<b>這就是 OLS 解。</b> ' : '')
    + 'ŷ = ' + HC.fmt(st.b0, 1) + ' + ' + HC.fmt(st.b1, 1) + 'x；RSS = '
    + HC.fmt(rss, 2) + '，理論最小值 = ' + HC.fmt(w26olsFit.rss, 2) + '。');
}
function w26olsSolve() {
  document.getElementById('w26b0').value = w26olsFit.b0;
  document.getElementById('w26b1').value = w26olsFit.b1;
  w26olsDraw();
}
function w26olsReset() {
  document.getElementById('w26b0').value = 0;
  document.getElementById('w26b1').value = 0;
  w26olsDraw();
}
['w26b0', 'w26b1'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', w26olsDraw);
});
if (w26olsS) w26olsDraw();
"""


if __name__ == "__main__":
    apply("s6_regression", BODIES, PAGEJS)
