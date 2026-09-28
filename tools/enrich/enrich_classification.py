#!/usr/bin/env python3
"""classification.html（ISLP 第 4 章）完整自學充實。冪等。

內容依據：講義 04_Classification.pdf（61 頁）、Ch04-classification-lab-zh.ipynb、
ISLP 第 4 章（書上 p.136–198）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_classification.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import proof
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 4
LAB = "Ch04-classification-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def slider(sid, label, lo, hi, step, val, fn, shown=None):
    """.controls-bar 裡的滑桿。flex:1 1 100% 讓它在窄螢幕獨佔一列，不會撐爆版面。"""
    return (f'<div class="slider-row" style="flex:1 1 100%;">'
            f'<label class="slider-label" for="{sid}">{label}</label>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}()">'
            f'<span class="slider-val" id="{sid}V">{val if shown is None else shown}</span></div>')


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_classification.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_classification.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_classification.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>第 3 章的 y 是連續的數字。現在換一種問題：<strong>y 是類別</strong>。這個人會不會違約、
  今天股市漲還是跌、這封信是不是垃圾信。這叫做<strong>分類</strong>（classification）。
  本章用 ISLP 的 <code>Default</code> 資料（n = 10000，違約率 3.33%）與課程 lab 的
  <code>Smarket</code> 資料當主線。</p>

  <p>直覺會說：把類別編成數字，然後照第 3 章擬合線性迴歸就好。<strong>這樣做會遇到兩個問題</strong>，
  這兩個問題都會影響結果的解讀。</p>

{info("線性迴歸用在類別上的兩個問題", '''<strong>1. 多於兩類時，編碼本身就帶進了假設。</strong>
  把「中風 = 1、藥物過量 = 2、癲癇 = 3」丟進迴歸，等於宣告這三種病有順序，
  而且「中風到藥物過量」的距離等於「藥物過量到癲癇」的距離。換一個編碼順序，模型就變了。<br>
  <strong>2. 只有兩類時編碼沒問題，但輸出會跑出 [0, 1]。</strong>直線沒有上下界，
  模型沒有把輸出限制在機率的範圍內，可能給出負值或大於 1 的值。''', "warm")}

  <p>第二點值得寫成式子。把 y 編成 0／1，然後擬合 $p(X) = \\beta_0 + \\beta_1 X$：</p>

  $$\\hat p(\\texttt{{balance}}) = -0.0752 + 0.00013 \\times \\texttt{{balance}}$$

  <p>這是 <code>Default</code> 資料上真的擬合出來的直線。把 <code>balance</code> 代 300 進去
  得到 −0.036——<strong>負的機率</strong>。ISLP 圖 4.2 左圖畫的就是這件事。
  右圖換成邏輯斯迴歸，整條曲線就維持在 0 與 1 之間。</p>

{viz(svg("w04whySvg", 330),
     [info_card("怎麼看這張圖",
                '橫軸是 <code>balance</code>，上下兩排短刻度是真實資料：'
                '<span style="color:var(--pt-b);font-weight:700;">上排（y = 1）</span>是違約的人，'
                '<span style="color:var(--pt-a);font-weight:700;">下排（y = 0）</span>是沒違約的人。'
                '紅線是線性迴歸的擬合，綠線是邏輯斯迴歸。'
                '<strong>紅色陰影是線性版給出負機率的區段。</strong>', "圖 4.2"),
      rows_card("在這個 balance 上",
                [("balance", "1000", "w04whyBal2"),
                 ("線性迴歸 p̂", "—", "w04whyLin"),
                 ("邏輯斯 p̂", "—", "w04whyLog"),
                 ("線性版合法嗎", "—", "w04whyOk")]),
      info_card("兩個係數的來歷",
                '邏輯斯的 <strong>β̂₀ = −10.6513、β̂₁ = 0.0055</strong> 就是 ISLP 表 4.1 的數字；'
                '線性版的 −0.0752 與 0.00013 是同一份資料上的最小平方解。'
                '線性版在 balance &lt; 579 給負值；要到 balance ≈ 8279 才會超過 1，'
                '那已經在資料範圍外了，<strong>這個模型並未保證機率的有效範圍。</strong>')],
     "w04whyStatus", "拖滑桿選一個 balance，右邊會同時給出兩個模型的預測機率。",
     slider("w04whyBal", "balance", 0, 2650, 25, 1000, "w04whyMove")
     + '<button class="btn btn-step" onclick="w04whyJump(300)">→ 跳到 balance = 300</button>'
     + '<button class="btn btn-toggle" onclick="w04whyToggle()">切換：只看邏輯斯</button>'
     + '<button class="btn btn-reset" onclick="w04whyReset()">重置</button>',
     provenance=("course-data", "ISLP Default；對照課本圖 4.2"))}

  <h3>三類的編碼實驗：換個順序，模型就換了</h3>
  <p>下面同一批急診病人，只是換了編碼順序。線性迴歸看到的是「數字」，
  所以它會擬合這些完全人造的順序與間距：</p>

{table(["編碼方式", "中風", "藥物過量", "癲癇", "這個編碼隱含的假設"],
       [["編碼 A", "1", "2", "3",
         "三種病有順序，而且「中風→藥物過量」與「藥物過量→癲癇」的差距一樣大"],
        ["編碼 B", "1", "3", "2",
         "順序變成中風 &lt; 癲癇 &lt; 藥物過量——同一份資料，擬合出完全不同的模型"],
        ["編碼 C", "2", "1", "3", "又是另一個模型。哪一個才對？<strong>都不對。</strong>"]])}

  <p>這些<strong>類別沒有順序也沒有距離</strong>，數字編碼卻加入了順序與等距的假設。
  可以用二元或多類別邏輯斯迴歸，也可以用本章後半介紹的生成式分類模型。</p>

{quiz("qWhy", "QUIZ · 為什麼不用迴歸",
      "把二元反應編成 0／1 之後擬合線性迴歸，跟邏輯斯迴歸比，最根本的問題是什麼？",
      [(True, "線性模型沒有將擬合機率限制在 [0, 1]，可能給出範圍外的值",
        "對。非水平直線在整個實數範圍上沒有上下界，而機率必須落在 [0, 1]。ISLP 圖 4.2 左圖就是這個現象。"
        "邏輯斯函數把線性式子壓進 (0, 1)，這是它存在的理由。"),
       (False, "係數沒辦法用最小平方法估計，必須改用最大概似法",
        "不對。用最小平方法<strong>估得出來</strong>。上面那條 −0.0752 + 0.00013 × balance 就是。"
        "問題不在估不出來，而在估出來的東西不能當機率用。"),
       (False, "二元反應違反常態誤差假設，所以 p 值與信賴區間都不能用",
        "二元反應不符合常態誤差，但仍可使用適當的穩健推論；不能斷言所有推論都不能用。即使只要預測，"
        "負機率照樣會出現。順序上先解決值域，再談推論。")])}
"""

# ── P01 logistic ──────────────────────────────────────────────────────
_log_code1 = lab_code(CH, 25)
_log_code2 = lab_code(CH, 31) + "\n\n" + lab_code(CH, 33) + "\n\n" + lab_code(CH, 35)
_log_code3 = lab_code(CH, 45) + "\n\n" + lab_code(CH, 49)

BODIES["logistic"] = f"""
  <h3>從前一章的條件平均出發</h3>
  <p>線性迴歸用預測變數描述 $E(Y\\mid X=x)$。把二元反應編成 0／1 後，我們仍然關心這個條件平均；只是現在它恰好就是事件發生的機率：</p>
  $$\\begin{{aligned}} E(Y\\mid X=x)&=p(x),\\\\
  P(Y=1\\mid X=x)&=p(x).\\end{{aligned}}$$
  <p>因為只有 0 與 1 兩種結果，條件平均就是 $0\\{{1-p(x)\\}}+1\\cdot p(x)=p(x)$。</p>
  <p><strong>只要反應是單次的 0／1 結果，它的條件分布就一定是 Bernoulli（伯努利分布）</strong>：機率 $p(x)$ 給 1，其餘機率給 0。這不是額外猜一個分布形狀；真正要建模的是 $p(x)$ 如何隨 $x$ 改變。</p>
  $$Y\\mid X=x\\sim\\operatorname{{Bernoulli}}(p(x)).$$
  <h3>把線性分數壓回 0 與 1 之間</h3>
  <p>沿用前章的線性式 $\\eta(x)=\\beta_0+\\beta_1x$，再讓它通過<strong>logistic 函數</strong>：</p>
  $$\\begin{{aligned}}p(x)&=\\frac{{e^{{\\eta(x)}}}}{{1+e^{{\\eta(x)}}}}\\\\
  &=\\frac{{1}}{{1+e^{{-\\eta(x)}}}}.\\end{{aligned}}$$
  <p>$\\eta(x)$ 可以是任何實數，轉換後的 $p(x)$ 都落在 $(0,1)$，因此能當作機率。線性式負得愈多，機率愈接近 0；正得愈多，愈接近 1；分數為 0 時，機率是 0.5。</p>
  <h3>誤差在哪裡？為什麼沒有共同的變異數？</h3>
  <p>前章的 Gaussian 模型可寫成 $Y=\\eta(X)+\\varepsilon$，其中誤差有共同的變異數 $\\sigma^2$。Logistic regression 直接指定 $Y\\mid X$ 的 Bernoulli 分布，隨機性已經包含在這個分布裡，不必再加上一個獨立的常態誤差。</p>
  $$\\operatorname{{Var}}(Y\\mid X=x)=p(x)\\{{1-p(x)\\}}.$$
  <p>若想沿用「觀測值減掉條件平均」的想法，仍可定義 $\\varepsilon=Y-p(X)$，寫成 $Y=p(X)+\\varepsilon$。但給定 $X=x$ 後，誤差只有 $1-p(x)$ 與 $-p(x)$ 兩個可能值；它的分布和變異數會隨 $x$ 改變。這不具有前章獨立、同變異加法雜訊的結構，也沒有另一個可自由估計的 $\\sigma^2$。</p>
  <p>估計時還會假設：給定各筆預測變數後，觀測結果彼此獨立。<strong>獨立不等於同變異</strong>，因為各筆的 $p(x)$ 可以不同。</p>

  <p>整理式子後，可以定義勝算與 log-odds。先移項：</p>

  $$\\underbrace{{\\frac{{p(X)}}{{1 - p(X)}}}}_{{\\text{{勝算 odds}}}} = e^{{\\beta_0 + \\beta_1 X}}
    \\qquad\\Longleftrightarrow\\qquad
    \\underbrace{{\\log\\!\\left(\\frac{{p(X)}}{{1-p(X)}}\\right)}}_{{\\text{{log-odds / logit}}}}
    = \\beta_0 + \\beta_1 X$$

  <p><strong>勝算</strong>（odds）是「發生機率 ÷ 不發生機率」，範圍 (0, ∞)；
  取 log 之後範圍變成整個實數線，這個量叫 <strong>log-odds</strong> 或 <strong>logit</strong>。
  所以邏輯斯迴歸的 <strong>log-odds 是線性函數</strong>；機率則隨 x 呈 S 形變化，係數須依 log-odds 解讀。</p>

  <h3>為什麼仍叫線性分類器？</h3>
  <p><strong>分類是根據 $x$ 的線性函數來決定的</strong>。機率曲線雖然是 S 形，但 logistic 函數單調遞增。若用固定門檻 $0\\lt t\\lt1$：</p>
  $$p(x)>t\\iff\\beta_0+\\beta_1x_1+\\cdots+\\beta_px_p>
  \\log\\frac{{t}}{{1-t}}.$$
  <p>門檻為 0.5 時，就是看線性分數是否大於 0；兩個預測變數的邊界是直線，多個變數則是超平面。這裡指模型使用的特徵空間：若加入平方項或交互作用，邊界在原始座標中就可能彎曲。</p>
  <h3>係數如何估計？</h3>
  <p>最大概似法（MLE）選擇讓已觀察到的 0／1 結果最可能出現的係數。對每筆資料，若結果為 1 就拿 $p_i$，若為 0 就拿 $1-p_i$，再把它們乘起來：</p>
  $$L(\\beta)=\\prod_{{i=1}}^n p_i^{{y_i}}(1-p_i)^{{1-y_i}}.$$
  <p>一般沒有像 OLS 那樣的係數封閉解，要用數值方法反覆更新。這是同一個估計原則的不同模型：在獨立、同變異的 Gaussian 線性模型下，最大化概似得到的係數才會等同最小平方解。</p>
  <h3>資料完全分開時，係數為什麼可能估不出來？</h3>
  <p>估計前還要注意<strong>分離</strong>（separation）。在二元分類中，想像畫一條直線；若有更多特徵，就改成超平面：</p>
  <ul>
  <li><strong>完全分離</strong>：存在一條分界，把所有 0 與 1 嚴格分到兩側，沒有任何訓練點落在分界上。</li>
  <li><strong>準完全分離</strong>：無法將所有點嚴格分開，但仍可讓所有點都在各自正確的一側或分界上；有些點在分界上，也至少有點嚴格落在正確側。</li>
  </ul>
  <p>這時，把某些係數愈放愈大，仍可能持續提高已觀測結果的機率，卻找不到一組有限係數使概似最大。因此，<strong>資料看起來分得很清楚，不代表係數就估得穩</strong>。這裡說的是只最大化概似、沒有另外限制係數大小的 logistic 模型；這種估計也稱為未正則化或無懲罰估計。較完整的說明與證明留在「反應誤差、潛在變數與分離」收合區。</p>

  <h3>摘要表為什麼用 z，而不是 t？</h3>
  <p><strong>依據是 MLE 的大樣本常態近似。</strong>模型與一般正則條件成立、樣本夠大且有有限估計時，檢定 $H_0:\\beta_j=\\beta_{{j,0}}$ 使用</p>
  $$z=\\frac{{\\hat\\beta_j-\\beta_{{j,0}}}}{{SE(\\hat\\beta_j)}}\\approx N(0,1).$$
  <p>常見的係數表檢定 $\\beta_j=0$，所以分子只剩 $\\hat\\beta_j$。這裡的標準誤一樣是估出來的；估計標準誤本身並不代表要用 $t$。Bernoulli 沒有額外的 $\\sigma^2$，也沒有 Gaussian 線性迴歸那個精確的 $t$ 結構。小樣本或分離情況下，這個 $z$ 近似可能不可靠。</p>

{viz(svg("w04shapeSvg", 250) + "\n" + svg("w04shapeSvg2", 220),
     [rows_card("目前的模型",
                [("β₀", "−1.00", "w04shapeB0T"), ("β₁", "0.80", "w04shapeB1T"),
                 ("p(0)", "—", "w04shapeP0"), ("p(1)", "—", "w04shapeP1"),
                 ("p = 0.5 的 x", "—", "w04shapeHalf"),
                 ("勝算比 e^β₁", "—", "w04shapeOR")]),
      info_card("兩張圖要一起看",
                '上圖是機率 p(x)，<strong>S 形、有上下界、斜率一直在變</strong>；'
                '下圖是同一個模型的 log-odds，<strong>一條直線，斜率永遠是 β₁</strong>。'
                '虛線是勝算（odds），它為正，依 β₁ 的符號指數增加或減少。'
                '勝算和機率的量尺不同，讀圖時要分清楚。'),
      info_card("β₁ 的符號與大小",
                'β₁ &gt; 0 曲線往右上、β₁ &lt; 0 往右下；<strong>|β₁| 愈大轉折愈陡</strong>，'
                'β₁ = 0 時，這個模型的預測機率不隨 x 改變。'
                'β₁ 不為 0 時，固定 β₁、改變 β₀ 會水平移動曲線；p = 0.5 的位置在 x = −β₀/β₁。')],
     "w04shapeStatus", "推兩個滑桿看 S 曲線怎麼動；下面那條 log-odds 永遠是直線。",
     slider("w04shapeB0", "β₀", -8, 8, 0.2, -1, "w04shapeDraw")
     + slider("w04shapeB1", "β₁", -3, 3, 0.05, 0.8, "w04shapeDraw")
     + '<button class="btn btn-reset" onclick="w04shapeReset()">重置</button>',
     provenance=("book-redraw", "依邏輯斯函數與 logit 定義直接計算"))}

  <p>固定其他變數時，$x_j$ 增加一單位，log-odds 增加 $\\beta_j$，<strong>勝算乘上 $e^{{\\beta_j}}$</strong>。機率的增量則取決於原本的機率，不能直接把係數讀成機率差。</p>
  <details class="qa-item reading-detail" id="w04-detail-odds"><summary>勝算和賠率有什麼關係？</summary><div class="detail-body">
  <p>課本習題用「違約勝算為 0.37」作例子。這表示違約機率與不違約機率的比值為 0.37，所以</p>
  $$\\frac{{p}}{{1-p}}=0.37\\quad\\Longrightarrow\\quad p=\\frac{{0.37}}{{1+0.37}}\\approx0.270.$$
  <p>賠率常從相反方向描述：若每下注一單位，猜中時的<strong>淨利</strong>是 $b$ 單位、猜錯就損失一單位，公平賠率要求平均淨收益為零：</p>
  $$pb-(1-p)=0\\quad\\Longrightarrow\\quad b=\\frac{{1-p}}{{p}}.$$
  <p>這個淨利賠率是事件勝算的倒數；若報的是含本金的總回收倍數，則是 $b+1=1/p$。實際報價還可能含莊家利潤，不能直接當成真實機率。先確認賠率的定義，再和模型中的 odds 對照。</p>
  <p>回到 Default：表 4.1 的 balance 係數是 0.0055，每增加一元，違約勝算乘上 $e^{{0.0055}}\\approx1.0055$，約增加 0.55%。這不是機率增加 0.55 個百分點。對單變數模型，$dp/dx=\\beta_1p(1-p)$，同樣的係數在機率接近 0.5 時，造成的局部機率變化最大。</p>
  </div></details>
  <details class="qa-item reading-detail" id="w04-detail-z-t"><summary>和前章比較：為什麼 Gaussian regression 有精確的 t？</summary><div class="detail-body">
  <p>在固定設計、滿秩且獨立同變異的 Gaussian 誤差模型下，若 $\\sigma$ 已知，用真正標準差標準化的係數服從標準常態。當 $\\sigma$ 未知，以殘差估計 $s^2=RSS/\\nu$，其中 $\\nu=n-p-1$，會有特殊的精確結果：</p>
  $$\\frac{{\\nu s^2}}{{\\sigma^2}}\\sim\\chi^2_\\nu,\\qquad s^2\\ \\text{{與}}\\ \\hat\\beta\\ \\text{{獨立}},\\qquad
  \\frac{{N(0,1)}}{{\\sqrt{{\\chi^2_\\nu/\\nu}}}}\\sim t_\\nu.$$
  <p>最後的比值中，分子與分母必須獨立。這就是 Gaussian regression 使用 $t$ 的理由。Logistic regression 的標準誤也需要估計，但在一般大樣本條件下，估計標準誤與真正標準差的比值趨近 1，代入後仍保留常態近似：</p>
  $$\\frac{{SE(\\hat\\beta_j)}}{{SD(\\hat\\beta_j)}}\\xrightarrow{{P}}1,
  \\qquad \\frac{{\\hat\\beta_j-\\beta_j}}{{SE(\\hat\\beta_j)}}\\overset{{\\mathrm{{approx}}}}{{\\sim}}N(0,1).$$
  <p>這是 Slutsky theorem 的應用。上課先記住：logistic 的 $z$ 來自大樣本 MLE 理論；Gaussian 的精確 $t$ 則還需要上述卡方與獨立結構。</p>
  <p>延伸：<a href="https://web.stanford.edu/class/archive/stats/stats200/stats200.1172/Lecture26.pdf">講義引用的 Stanford：Logistic regression 的係數與標準誤</a>。</p>
  </div></details>

  <h3 id="dx-log">講義完整實作：在 <code>Smarket</code> 上擬合邏輯斯迴歸</h3>
{card("講義 04 · sm.GLM + Binomial（六個預測變數）", _log_code1, lab_output(CH, 25),
      src=src("25"),
      note="<code>family=sm.families.Binomial()</code> 是關鍵——同一支 <code>sm.GLM()</code>"
           "換一個 family 就變成別的廣義線性模型（最後一節會回來講）。"
           "看那排 p 值：最小的是 <code>Lag1</code> 的 0.145，各係數都未達 0.05 顯著水準。"
           "這份資料未提供這些係數異於零的充分證據；預測表現仍要另外評估。")}

{card("講義 04 · 從機率到標籤，再到混淆矩陣", _log_code2, lab_output(CH, 35),
      src=src("31、33、35"),
      note="<code>predict()</code> 回傳的是<strong>機率</strong>，不是標籤；"
           "要自己挑一個門檻值把它切成 <code>Up</code>／<code>Down</code>。"
           "這裡用 0.5，正確率 (507 + 145) / 1250 = 52.2%，但這是<strong>訓練</strong>正確率，"
           "同一批資料又訓練又評估，不能當作獨立測試；訓練表現通常較樂觀。")}

{card("講義 04 · 用 2001–2004 擬合、在 2005 年比較", _log_code3, lab_output(CH, 49),
      src=src("45、49、51"),
      note="用 2001–2004 擬合、在 2005 年比較，正確率是 <strong>48.0%</strong>（錯誤率 52.0%）。不過前一張卡已用包含 2005 年的完整資料查看係數與 p 值；"
           "因此這是課本探索流程的教材示範，2005 年不是從頭到尾未碰的獨立測試集。")}

{quiz("qLog", "QUIZ · 係數的解讀",
      "某邏輯斯迴歸模型裡 <code>balance</code> 的係數是 0.0055。下面哪個說法對？",
      [(True, "balance 每多一元，違約的勝算乘上 e^0.0055 ≈ 1.0055",
        "對。線性的是 log-odds，所以「加法」發生在 log-odds 上，換回勝算就變成「乘法」。"
        "勝算比 e^β₁ 是一個不隨 balance 改變的常數，這是它好用的地方。"),
       (False, "balance 每多一元，違約機率增加 0.0055",
        "不對。這是把 log-odds 的變化當成機率的變化。機率的變化量隨位置而變："
        "balance 從 1000 到 2000，p̂ 從 0.006 跳到 0.586，平均一元遠遠不是 0.0055。"),
       (False, "balance 每多一元，違約機率乘上 1.0055",
        "也不對。乘上 e^β₁ 的是<strong>勝算</strong> p/(1−p)，不是機率 p。"
        "當 p 很小時勝算 ≈ 機率，這個說法才勉強接近；p 大的時候會嚴重高估。")])}
"""

# ── P02 multinomial ───────────────────────────────────────────────────
BODIES["multinomial"] = f"""
  <p>把一個預測變數換成 p 個，式子幾乎不用改——線性部分變成 $\\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p$
  就好。加入變數後，<strong>原有係數可能變號</strong>。</p>

  <p>類別解釋變數的加入方式和前章相同：挑一個基準水準，其餘水準用指示變數（indicator）表示：條件成立取 1，不成立取 0。例如 $s=I(\\texttt{{student}}=\\text{{Yes}})$，以非學生為基準：</p>
  $$\\eta(x)=\\beta_0+\\beta_1\\,\\texttt{{balance}}+\\beta_2\\,\\texttt{{income}}+\\beta_3s.$$
  <p>固定 balance 與 income 時，學生相對於非學生的 log-odds 差為 $\\beta_3$，勝算比為 $e^{{\\beta_3}}$。有 $J$ 個水準時，含截距的模型通常放入 $J-1$ 個 indicator。這裡的類別解釋變數，和接下來的多類別反應是兩件事。</p>

  <p>ISLP 的 <code>Default</code> 例子呈現了這個差異。只用 <code>student</code> 一個變數擬合（表 4.2），
  <code>student[Yes]</code> 的係數是 <strong>+0.4049</strong>：學生比較容易違約。
  可是把 <code>balance</code> 與 <code>income</code> 一起放進去（表 4.3），
  同一個 <code>student[Yes]</code> 變成 <strong>−0.6468</strong>：學生比較不容易違約。
  <strong>同一份資料，符號翻過來了。</strong></p>

{info("混淆（confounding）：條件改變，係數的意義也改變", '''兩個係數都對，只是在回答不同的問題。<br>
  <strong>+0.4049 回答的是：</strong>「隨便抓一個學生跟一個非學生比，誰比較容易違約？」——學生。
  因為學生的 <code>balance</code> 整體偏高。<br>
  <strong>−0.6468 回答的是：</strong>「<em>在 balance 與 income 相同</em> 的前提下，學生跟非學生誰比較容易違約？」——非學生。<br>
  多元迴歸的每個係數描述「<strong>控制模型中其他變數後</strong>」的條件關聯。
  這是模型中的比較，沒有因果設計與相應假設時，不代表改變學生身分會造成違約率改變。
  ISLP 圖 4.3 左圖比較違約機率曲線，右圖用箱形圖呈現學生與非學生的 balance 分布。''', "warm")}

  <p>用表 4.3 的係數算兩個具體的人（ISLP 式 4.8、4.9）：balance = 1500、income = 40（千元）的
  <strong>學生</strong>違約機率是 0.058，同樣條件的<strong>非學生</strong>是 0.105——
  同樣的 balance 與 income 下，學生的預測違約機率較低。</p>

  <h3>多於兩類：多類別邏輯斯迴歸</h3>

  <p>一次觀測若只會落在 $K$ 個互斥類別之一，給定 $X=x$ 後，各類機率就完整決定了它的分布。這是 Bernoulli 的多類別版本：</p>
  $$Y\\mid X=x\\sim\\operatorname{{Categorical}}(p_1(x),\\ldots,p_K(x)),\\qquad
  p_k(x)\\ge0,\\quad\\sum_{{k=1}}^Kp_k(x)=1.$$
  <p>多類別 logistic 再用線性分數與 softmax 指定這些機率如何隨 $x$ 改變。每個指標 $I(Y=k)$ 的條件期望是 $p_k(x)$；類別的數字編碼本身沒有可解讀的平均。</p>

  <p>兩類的邏輯斯迴歸沒辦法直接處理 K &gt; 2。做法是<strong>挑一類當基準</strong>（baseline，
  習慣挑第 K 類），然後對其餘每一類寫一條 log-odds：</p>

  $$\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid X = x)}}{{\\Pr(Y = K \\mid X = x)}}\\right)
    = \\beta_{{k0}} + \\beta_{{k1}} x_1 + \\cdots + \\beta_{{kp}} x_p,
    \\qquad k = 1, \\ldots, K-1$$

  <p>只要估 K − 1 組係數。也可寫成 K 類對稱的 <strong>softmax</strong>；分母讓所有類別的機率加總為 1，但估計時仍需加識別限制，例如把基準類的整組係數固定為零，避免同一組機率對應多組係數：</p>

  $$\\Pr(Y = k \\mid X = x) = \\frac{{e^{{\\beta_{{k0}} + \\beta_{{k1}} x_1 + \\cdots + \\beta_{{kp}} x_p}}}}
    {{\\sum_{{l=1}}^{{K}} e^{{\\beta_{{l0}} + \\beta_{{l1}} x_1 + \\cdots + \\beta_{{lp}} x_p}}}}$$

{table(["", "基準類寫法（式 4.10–4.12）", "softmax 寫法（式 4.13）"],
       [["要估幾組係數", "K − 1 組", "K 組分數，須加識別限制；自由參數仍是 (K−1)(p+1)"],
        ["係數怎麼解讀", "相對於基準類的 log-odds", "只有<strong>兩類之間的差</strong> β<sub>k</sub> − β<sub>k′</sub> 有意義"],
        ["換基準／平移係數", "係數全變，但預測值不變", "每類係數同加一個向量，預測機率不變"],
        ["常見於", "統計軟體（<code>statsmodels</code>）", "機器學習與神經網路（第 10 章會再遇到）"]])}

{info("兩種寫法給的預測值完全一樣", '''ISLP §4.3.5 講得很清楚：換基準類、或用 softmax，
  <strong>擬合值、任兩類之間的 log-odds、以及分類結果都不變</strong>，變的只有係數本身的數值。
  解讀多類別係數前，先確認基準類別與參數限制，
  才能知道各係數比較的是哪兩類。''')}

  <h3 id="dx-mul">講義完整實作：只留 <code>Lag1</code> 與 <code>Lag2</code></h3>
{card("講義 04 · 探索後只留 Lag1 與 Lag2", lab_code(CH, 53), lab_output(CH, 53),
      src=src("53、55"),
      note="完整資料的 p 值看過 2005 年標籤後，才挑出看起來較有希望的兩個變數。2005 年正確率從 48.0% 升到 "
           "<strong>(35 + 106) / 252 = 56.0%</strong>；而且在「模型說會漲」的日子裡，"
           "它有 <strong>106 / (106 + 76) = 58.2%</strong> 準。"
           "那 252 天裡本來就有 141 天在漲，<strong>每天都猜漲也有 56%</strong>。"
           "這組數字適合說明流程與混淆矩陣，不能當成選模後的新測試證據。乾淨評估須只用訓練年份決定變數。")}

{quiz("qMul", "QUIZ · 混淆",
      "只用 <code>student</code> 擬合時它的係數是正的，加入 <code>balance</code> 後變成負的。"
      "該怎麼理解？",
      [(True, "兩個係數在回答不同的關聯問題：後者比較 balance 相同的人",
        "對。多元迴歸的係數描述控制模型中其他變數後的條件關聯，不會自動具有因果意義。"
        "學生整體 balance 偏高所以整體違約率高；但同樣的 balance 之下，學生反而比較不容易違約。"),
       (False, "其中一個模型擬合錯了，應該相信變數比較多的那一個",
        "兩個模型都沒擬合錯，各自都是它所設定問題的正確答案。「相信變數多的」也不是普遍原則——"
        "要看你問的是<strong>邊際關聯</strong>還是<strong>條件關聯</strong>。想預測「該不該發卡給這個學生」用後者；"
        "想知道「學生族群整體風險」用前者。"),
       (False, "這是共線性造成的，把 student 或 balance 移掉一個就好",
        "方向不對。<code>student</code> 與 <code>balance</code> 確實相關，但這裡的現象是混淆"
        "（confounding）而不是共線性造成的不穩定——係數的標準誤沒有明顯膨脹，"
        "符號翻轉可由兩個模型控制條件不同來解釋。移掉變數會改變控制的條件，也會改變係數所回答的問題。")])}
"""

# ── P03 LDA ───────────────────────────────────────────────────────────
_lda_code1 = lab_code(CH, 66) + "\n\n" + lab_code(CH, 68) + "\n\n" + lab_code(CH, 72)
_lda_code2 = lab_code(CH, 74) + "\n\n" + lab_code(CH, 77) + "\n\n" + lab_code(CH, 79)

BODIES["lda"] = f"""
  <h3>已經有 logistic，為什麼還需要其他方法？</h3>
  <p>Logistic regression 已能把線性分數轉成類別機率，但估計是否穩定、能否利用資料的分布資訊，以及能不能看出類別間的幾何關係，是另外幾個問題。講義從這三點介紹 LDA。</p>
  <h4>1. 資料容易分開，不代表 logistic 的係數容易估計</h4>
  <p>前面定義的完全分離，表示一條分界就能把訓練資料中的兩類嚴格分開。沿著正確方向放大係數，模型會把已觀察到的類別機率推得更接近 1，概似也持續增加，卻可能沒有有限的最大點。這時分類標籤看似很穩，係數和標準誤卻不穩定，不能照一般情況解讀係數表。</p>
  <p>LDA 改由各類的平均、共變異數與先驗決定邊界。只要這些量能穩定估計，兩類分得開本身不會造成 logistic 那種係數發散。不過資料太少或變數共線時，共變異數仍可能無法估穩；LDA 也有自己的限制。</p>
  <h4>2. 樣本少時，合理的分布假設能提供額外資訊</h4>
  <p>LDA 假設各類內近似常態，而且共用共變異數。這相當於先限制資料雲的形狀，再用所有類的資料一起估計共同的散布；資料少時，這些限制可能讓估計較穩定。</p>
  <p>代價是要承擔假設不合適的偏差。若類內資料明顯偏離常態，或各類散布差很多，LDA 的限制也可能妨礙預測。因此，講義說的是在假設合理時 LDA <em>可能</em>更穩定，實際表現仍需和 logistic 等方法一起比較。</p>
  <h4>3. 多類別的分類規則，也能提供低維視圖</h4>
  <p>LDA 為每一類計算一個判別分數，選分數最大的類，二類與多類使用同一套規則。Logistic 也能透過 softmax 處理多類別；LDA 的另一個用途，是找出最能呈現類別差異的投影方向。</p>
  <p>例如 Iris 有四個測量變數、三個品種。LDA 的完整判別資訊最多只需兩個方向，就能畫成一張平面圖，同時觀察類別分離與重疊的位置。為什麼最多是 $K-1$ 個方向，會在本節的 Fisher LDA 收合區用幾何方式解釋。</p>

  <h3>判別式與生成式：分別在建模什麼？</h3>
  <p>Logistic regression 是<strong>判別式模型</strong>（discriminative model），直接描述 $P(Y=k\\mid X=x)$。<strong>生成式模型</strong>（generative model）則先描述類別比例與各類的 $X$ 分布，組成聯合分布，再用 Bayes 定理求後驗機率。</p>
  <p>令 $\\pi_k=P(Y=k)$ 為先驗機率，$f_k(x)$ 為 $X\\mid Y=k$ 的密度。對連續 $X$，密度不是單點機率 $P(X=x\\mid Y=k)$。分類用的是</p>
  $$P(Y=k\\mid X=x)=\\frac{{\\pi_kf_k(x)}}{{\\sum_{{\\ell=1}}^K\\pi_\\ell f_\\ell(x)}}.$$
  <p>分母對所有類別相同，所以選 $\\pi_kf_k(x)$ 最大的類別即可。和前面的 Bernoulli／Categorical 不同，這裡接下來的常態與共變異數限制是<strong>額外的模型假設</strong>，需要檢查是否適合資料。</p>
  <details class="qa-item reading-detail" id="w04-detail-generative-uses"><summary>生成式模型除了分類，還能做什麼？</summary><div class="detail-body">
  <p>生成式模型同時描述「各類出現的比例」與「每一類裡的資料長什麼樣」。因此，有了先驗 $\\pi_k$ 和類內分布 $f_k$，就能進一步討論整筆資料如何產生、常不常見，以及未觀測部分可能是什麼。</p>
  <h4>生成新的資料：先抽類別，再抽特徵</h4>
  <p>先依各類的先驗機率抽一個 $Y$，再從該類的 $f_k$ 抽出 $X$。以 Iris 為例，先抽一個品種，再依這個品種的模型產生花萼長、花萼寬、花瓣長、花瓣寬。LDA 會使用各品種自己的平均與共用的共變異數來生成。</p>
  <p>這些是符合已建立模型的模擬資料，可以幫助理解模型假設的資料形狀；它們不等於新增的真實觀測。只描述 $P(Y\\mid X)$ 的判別式模型，則還缺少 $X$ 如何產生的模型，不能單靠這個條件機率生成整筆特徵。</p>
  <h4>異常檢查：分得出類別，不代表資料很常見</h4>
  <p>將各類密度依先驗加權相加，就得到整體資料的邊際密度：</p>
  $$f_X(x)=\\sum_{{k=1}}^K\\pi_k f_k(x).$$
  <p>若一筆觀測在每一類的模型裡都很少見，這個密度就低，可以作為異常檢查的線索。例如一朵花的測量組合與三個品種的資料雲都離得很遠，即使分類器仍選出最可能的品種，也值得回頭檢查。</p>
  <p>後驗機率比較的是各類之間的相對可能性：所有類都不太能解釋這筆資料時，其中一類仍可能遠高於其他類。因此「分類有把握」與「這筆資料符合整體分布」是不同問題。低密度也不等於資料有錯，可能是真實少見的個案，或模型沒有描述好的情況。</p>
  <h4>缺值處理：使用已觀測到的特徵</h4>
  <p>假設花瓣長缺失，但其他測量還在。將已觀測部分記為 $x_{{\\mathrm{{obs}}}}$，缺失部分記為 $x_{{\\mathrm{{mis}}}}$。若只想分類，可以把缺失的特徵積分掉：</p>
  $$f_k(x_{{\\mathrm{{obs}}}})=\\int f_k(x_{{\\mathrm{{obs}}}},x_{{\\mathrm{{mis}}}})\\,dx_{{\\mathrm{{mis}}}}.$$
  <p>接著用這個邊際密度代入 Bayes 公式，根據已知特徵計算各類的後驗機率。若想推估缺失數值，則使用缺失特徵在已知特徵下的條件分布；模型中的變數相關性，可能提供比直接填整體平均更具體的資訊。</p>
  <p>是否適合這樣處理，仍取決於模型及缺值原因。這裡說明的是聯合機率模型提供的計算途徑；一般 LDA 套件未必直接提供缺值估計功能。</p>
  </div></details>

  <p><strong>LDA</strong>（linear discriminant analysis，線性判別分析）的假設是：
  各類的平均數可不同，但變異數共用，即 $X\\mid Y=k\\sim N(\\mu_k,\\sigma^2)$。這個常態假設描述類內資料的形狀。p = 1 時</p>

  $$f_k(x) = \\frac{{1}}{{\\sqrt{{2\\pi}}\\,\\sigma}}
    \\exp\\!\\left(-\\frac{{(x - \\mu_k)^2}}{{2\\sigma^2}}\\right)$$

  <p>代進 Bayes 定理、取 log、把跟 k 無關的項全部丟掉，剩下的就是<strong>判別函數</strong>
  （discriminant function）：</p>

  $$\\delta_k(x) = x \\cdot \\frac{{\\mu_k}}{{\\sigma^2}} - \\frac{{\\mu_k^2}}{{2\\sigma^2}} + \\log \\pi_k$$

  <p>把 x 分到 $\\delta_k(x)$ 最大的那一類。<strong>δ 是 x 的一次式</strong>。這就是名字裡「線性」的來源。
  兩類平均不同且 $\\pi_1 = \\pi_2$ 時，邊界剛好落在兩個平均數的中點 $(\\mu_1 + \\mu_2)/2$。</p>

  <details class="qa-item reading-detail" id="w04-detail-lda-discriminant-1d"><summary>推導：一維 LDA 的判別函數從哪裡來？</summary><div class="detail-body">
  <p><strong>第一步：比較後驗機率。</strong>Bayes 公式的分母對所有類別相同，因此最大化後驗機率，等同最大化 $\\pi_k f_k(x)$。各類先驗為正時，再取單調遞增的 log，也不會改變大小順序：</p>
  $$\\arg\\max_k P(Y=k\\mid X=x)=\\arg\\max_k\\{{\\log\\pi_k+\\log f_k(x)\\}}.$$
  <p><strong>第二步：代入類內常態密度。</strong>LDA 假設 $X\\mid Y=k\\sim N(\\mu_k,\\sigma^2)$，且各類共用 $\\sigma^2>0$，所以</p>
  $$\\log\\pi_k+\\log f_k(x)=\\log\\pi_k-\\log(\\sqrt{{2\\pi}}\\sigma)-\\frac{{(x-\\mu_k)^2}}{{2\\sigma^2}}.$$
  <p><strong>第三步：展開平方。</strong>利用 $(x-\\mu_k)^2=x^2-2x\\mu_k+\\mu_k^2$：</p>
  $$\\begin{{aligned}}
  \\log\\pi_k+\\log f_k(x)
  &=\\underbrace{{-\\log(\\sqrt{{2\\pi}}\\sigma)-\\frac{{x^2}}{{2\\sigma^2}}}}_{{C(x)\\text{{，不隨類別改變}}}}\\\\
  &\\quad+\\frac{{x\\mu_k}}{{\\sigma^2}}-\\frac{{\\mu_k^2}}{{2\\sigma^2}}+\\log\\pi_k.
  \\end{{aligned}}$$
  <p><strong>第四步：移除共同項。</strong>分類時 $x$ 已固定，$C(x)$ 對每類都一樣，不影響哪個分數最大。留下</p>
  $$\\boxed{{\\delta_k(x)=\\frac{{x\\mu_k}}{{\\sigma^2}}-\\frac{{\\mu_k^2}}{{2\\sigma^2}}+\\log\\pi_k}}.$$
  <p>這個分數是 $x$ 的一次式。實際分類把未知的先驗、平均與變異數換成估計值，再選判別分數最大的類別。</p>
  </div></details>

  <h3>直接用資料估計參數</h3>
  <p>第 $k$ 類有 $n_k$ 筆資料，總共 $n$ 筆。先驗用類別比例估計，平均用類內樣本平均；所有類的變異數合併估計：</p>
  $$\\hat\\pi_k=\\frac{{n_k}}{{n}},\\qquad
  \\hat\\mu_k=\\frac1{{n_k}}\\sum_{{i:y_i=k}}x_i,$$
  $$\\hat\\sigma^2=\\frac1{{n-K}}\\sum_{{k=1}}^K\\sum_{{i:y_i=k}}(x_i-\\hat\\mu_k)^2
  =\\sum_{{k=1}}^K\\frac{{n_k-1}}{{n-K}}\\hat\\sigma_k^2.$$
  <p>這些都是<strong>封閉解</strong>（closed-form estimates），可以直接計算，再代入判別函數。上式採講義的不偏估計，分母為 $n-K$；嚴格的最大概似估計則用分母 $n$。兩者不要混稱。</p>

{viz(svg("w04lda1Svg", 320),
     [rows_card("目前的設定",
                [("模型", "LDA（共用 σ）", "w04lda1Mode"),
                 ("π₁ · π₂", "0.50 · 0.50", "w04lda1Pri"),
                 ("使用的 σ₁ · σ₂", "—", "w04lda1Sig"),
                 ("決策邊界", "—", "w04lda1Bnd"),
                 ("中點 (μ₁+μ₂)/2", "—", "w04lda1Mid")]),
      info_card("為什麼畫的是 πₖ·fₖ(x) 而不是 fₖ(x)",
                '因為要讓「兩條曲線的交點」正好就是決策邊界。'
                'Bayes 分類器比的是 π<sub>k</sub>f<sub>k</sub>(x) 的大小，'
                '所以把先驗乘進去畫，<strong>交點在哪裡、邊界就在哪裡</strong>，'
                '不用另外算。在初始設定中，第 1 類位於左側，拉大 π₁ 會讓邊界往右移；一般而言，提高某類先驗'
                '會擴大該類的決策區域。', "圖 4.4"),
      info_card("勾了「允許不同 σ」就變成 QDA",
                '共用 σ 時 x² 的係數在相減時剛好抵消，只剩一次項，當兩類平均不同時，邊界是<strong>一個點</strong>；平均相同時，分數差只剩先驗差異。'
                '一旦 σ₁ ≠ σ₂，x² 的係數不再抵消，邊界變成二次方程式的根——'
                '<strong>可能有兩個點</strong>。這就是兩者決策邊界不同的原因。')],
     "w04lda1Status", "推 μ 與 σ 的滑桿看兩個常態密度怎麼動，虛線是決策邊界。",
     slider("w04lda1M1", "μ₁", -4, 1, 0.1, -1.25, "w04lda1Draw")
     + slider("w04lda1M2", "μ₂", -1, 4, 0.1, 1.25, "w04lda1Draw")
     + slider("w04lda1S1", "σ₁", 0.4, 2.5, 0.05, 1, "w04lda1Draw")
     + slider("w04lda1S2", "σ₂", 0.4, 2.5, 0.05, 1, "w04lda1Draw")
     + slider("w04lda1P1", "π₁", 0.05, 0.95, 0.05, 0.5, "w04lda1Draw")
     + '<button class="btn btn-toggle" onclick="w04lda1Toggle()">允許不同 σ（QDA）</button>'
     + '<button class="btn btn-reset" onclick="w04lda1Reset()">重置</button>',
     provenance=("book-redraw", "依講義圖 4.4 的一維常態判別模型重繪"))}

  <p>p &gt; 1 時把常態換成<strong>多變量常態</strong> $N(\\mu_k, \\Sigma)$，
  $\\mu_k$ 是各類自己的平均向量、$\\Sigma$ 是<strong>所有類共用</strong>的共變異數矩陣。
  判別函數變成矩陣版：</p>

  $$\\delta_k(x) = x^{{\\mathsf{{T}}}} \\Sigma^{{-1}} \\mu_k
    - \\frac{{1}}{{2}} \\mu_k^{{\\mathsf{{T}}}} \\Sigma^{{-1}} \\mu_k + \\log \\pi_k$$

  <details class="qa-item reading-detail" id="w04-detail-lda-discriminant-multi"><summary>推導：多變數 LDA 為什麼仍是線性判別函數？</summary><div class="detail-body">
  <p>沿用一維的比較方式，從 $\\log\\pi_k+\\log f_k(x)$ 出發。現在 $X\\mid Y=k\\sim N_p(\\mu_k,\\Sigma)$，所有類共用正定的共變異數矩陣 $\\Sigma$：</p>
  $$f_k(x)=\\frac{{1}}{{(2\\pi)^{{p/2}}|\\Sigma|^{{1/2}}}}
  \\exp\\!\\left[-\\frac12(x-\\mu_k)^T\\Sigma^{{-1}}(x-\\mu_k)\\right].$$
  <p>其中 $|\\Sigma|$ 是行列式。取 log 後，指數變成二次型：</p>
  $$\\log\\pi_k+\\log f_k(x)=\\log\\pi_k-\\frac p2\\log(2\\pi)-\\frac12\\log|\\Sigma|
  -\\frac12(x-\\mu_k)^T\\Sigma^{{-1}}(x-\\mu_k).$$
  <p>因為 $\\Sigma^{{-1}}$ 對稱，兩個交叉項相同，展開得到</p>
  $$\\begin{{aligned}}(x-\\mu_k)^T\\Sigma^{{-1}}(x-\\mu_k)
  &=x^T\\Sigma^{{-1}}x-2x^T\\Sigma^{{-1}}\\mu_k\\\\
  &\\quad+\\mu_k^T\\Sigma^{{-1}}\\mu_k.
  \\end{{aligned}}$$
  <p>代回並整理：</p>
  $$\\log\\pi_k+\\log f_k(x)=C(x)+x^T\\Sigma^{{-1}}\\mu_k
  -\\frac12\\mu_k^T\\Sigma^{{-1}}\\mu_k+\\log\\pi_k,$$
  $$C(x)=-\\frac p2\\log(2\\pi)-\\frac12\\log|\\Sigma|-\\frac12x^T\\Sigma^{{-1}}x.$$
  <p>$C(x)$ 不隨類別改變，移除後不影響分類。因此</p>
  $$\\boxed{{\\delta_k(x)=x^T\\Sigma^{{-1}}\\mu_k-\\frac12\\mu_k^T\\Sigma^{{-1}}\\mu_k+\\log\\pi_k}}.$$
  <p><strong>共用共變異數是關鍵。</strong>它使含 $x$ 的二次項對每類都相同，能從比較中消去。剩下的 $x^T\\Sigma^{{-1}}\\mu_k$ 對 $x$ 線性，其餘都是該類的常數；比較兩類分數就得到線性邊界。</p>
  <p>QDA 則讓各類使用自己的 $\\Sigma_k$，二次項與 $\\log|\\Sigma_k|$ 都不能消去，於是保留</p>
  $$\\delta_k^{{\\mathrm{{QDA}}}}(x)=-\\frac12(x-\\mu_k)^T\\Sigma_k^{{-1}}(x-\\mu_k)
  -\\frac12\\log|\\Sigma_k|+\\log\\pi_k.$$
  <p>來源：講義的 LDA／QDA 推導，及其引用的<a href="https://dafriedman97.github.io/mlbook/content/c4/concept.html">Discriminative analysis 教材</a>。</p>
  </div></details>

  <p>矩陣寫法看似複雜，但令 $c_k=\\Sigma^{{-1}}\\mu_k$、$c_{{k0}}=-\\mu_k^\\mathsf T\\Sigma^{{-1}}\\mu_k/2+\\log\\pi_k$，就能看出</p>
  $$\\boxed{{\\delta_k(x)=c_{{k0}}+c_{{k1}}x_1+\\cdots+c_{{kp}}x_p}}.$$
  <p>它是 $x$ 的線性函數（含截距）。比較兩類分數的邊界 $\\delta_k(x)=\\delta_\\ell(x)$ 是超平面。在二維、三類的圖中，至多有三條兩兩分數相等的直線；只有沒有被第三類分數超過的部分才構成實際分類邊界。</p>
  <p>多變數時，類別平均改成向量，共用變異數改成共變異數矩陣：</p>
  $$\\hat\\mu_k=\\frac1{{n_k}}\\sum_{{i:y_i=k}}x_i,\\qquad
  \\hat\\Sigma=\\frac1{{n-K}}\\sum_{{k=1}}^K\\sum_{{i:y_i=k}}
  (x_i-\\hat\\mu_k)(x_i-\\hat\\mu_k)^\\mathsf T.$$
  <p>這同樣是不偏的 pooled 估計；MLE 分母仍為 $n$。以下使用共變異數可逆的情況，推導與估計細節可在本節收合區查閱。</p>

{qa("觀念釐清", [
    ("Q：LDA 與邏輯斯迴歸都給線性邊界，那差在哪？什麼時候該選哪個？",
     "<p>差在<strong>係數是怎麼決定的</strong>。ISLP §4.5.1 把兩者都寫成同一個形式：</p>"
     "<p>$\\log\\!\\left(\\frac{\\Pr(Y=k|X=x)}{\\Pr(Y=K|X=x)}\\right) = a_k + \\sum_{j=1}^{p} b_{kj}x_j$</p>"
     "<p>兩邊的<strong>函數形式一模一樣</strong>，都是 x 的線性函數。差別是："
     "LDA 的 $a_k, b_{kj}$ 是「假設各類 X 服從共用共變異數的常態」之後，"
     "由 $\\hat\\pi_k, \\hat\\mu_k, \\hat\\Sigma$ 算出來的；"
     "邏輯斯迴歸的係數則是直接讓<strong>條件概似</strong>最大。它不要求 X 的類內分布為常態，但仍對條件機率的形式作了假設。</p>"
     "<p>可依資料與用途比較：</p>"
     "<ul><li><strong>各類內的 X 真的近似常態、n 又小</strong>：共用共變異數也合理時，可優先比較 LDA。它利用了分布資訊，"
     "估計可能較穩定。ISLP 情境 1 中 LDA 表現良好。</li>"
     "<li><strong>X 明顯不常態（重尾、類別型變數、極端值多）</strong>：可考慮邏輯斯迴歸，並評估條件機率形式是否合理。"
     "ISLP 情境 3 把資料換成 t 分布，邏輯斯就贏了 LDA。</li>"
     "<li><strong>兩類完全可分</strong>：未正則化 logistic 可能沒有有限 MLE；共變異數能穩定估計時，可比較 LDA。</li>"
     "<li><strong>要做推論、要 p 值、要處理類別型預測變數</strong>：邏輯斯迴歸能直接納入 indicator，並用係數、標準誤與檢定描述條件關聯。</li></ul>"
     "<p>兩者可能給出相近的分類結果。以 Lag1、Lag2 擬合的 LDA 混淆矩陣"
     "（35／35／76／106）跟使用相同變數的邏輯斯<strong>相同</strong>。"
     "這是這份資料上的結果。式 4.32 只說兩者的 log-odds 都是線性形式；估計係數的方法不同，並不保證預測機率、分類結果或混淆矩陣相同。</p>"),
])}

  <h3 id="dx-lda">講義完整實作：<code>LinearDiscriminantAnalysis</code></h3>
{card("講義 04 · 擬合 LDA 並讀出估計的參數", _lda_code1, lab_output(CH, 68),
      src=src("66、68、72"),
      note="<code>means_</code> 是 μ̂₁、μ̂₂（每一列一類、每一欄一個變數）："
           "市場下跌的日子前兩天報酬偏正，上漲的日子前兩天偏負。"
           "<code>priors_</code>給 π̂ = <code>[0.49198397, 0.50801603]</code>，"
           "就是訓練資料裡 Down／Up 的比例——LDA 的先驗預設就是這樣估的。"
           "注意 <code>drop(columns=['intercept'])</code>：<code>LDA</code> 自己會處理截距。")}

{card("講義 04 · 線性判別方向與預測結果", _lda_code2, lab_output(CH, 79),
      src=src("74、77、79"),
      note="<code>scalings_</code> = <code>[[-0.642], [-0.514]]</code> 是那條線性組合的方向："
           "它描述投影方向；實際分類還要依平均、尺度與先驗設定切點。"
           "混淆矩陣跟邏輯斯<strong>完全相同</strong>。"
           "相同混淆矩陣不代表兩個方法的機率或邊界完全相同。")}

{quiz("qLda", "QUIZ · LDA 的假設",
      "LDA（p &gt; 1）到底假設了什麼？",
      [(True, "每一類的 X 服從多變量常態，各類有自己的平均向量，共變異數矩陣所有類共用",
        "對。類別平均的差異提供區分類別的資訊，「共變異數共用」讓 x² 項在判別函數相減時抵消，"
        "邊界因此是線性的。放掉共用這一條就變成 QDA。"),
       (False, "每一類的 X 服從多變量常態，平均與共變異數矩陣都各類共用",
        "平均與共變異數都相同時，X 無法提供區分類別的資訊，分類只剩先驗差異。LDA 的平均向量允許各類不同；若平均相同，就只能靠先驗區分類別。"),
       (False, "X 的各個分量在每一類內互相獨立，且服從常態",
        "這是 <strong>Naive Bayes</strong>（配上常態密度）的假設，不是 LDA。"
        "LDA 允許變數之間相關——相關結構就寫在共用的 Σ 的非對角元素裡。"
        "常態版 Naive Bayes 一般對應各類 Σₖ 為對角矩陣的 QDA；只有各變數的變異數也跨類別共用時，才成為對角 Σ 的 LDA（ISLP §4.4.4、§4.5.1）。")])}

{table(["", "要估的參數", "p = 2, K = 2 時", "p = 50, K = 2 時"],
       [["先驗 π<sub>k</sub>", "K − 1 個", "1", "1"],
        ["平均 μ<sub>k</sub>", "K × p 個", "4", "100"],
        ["共用 Σ（LDA）", "p(p+1)/2 個", "3", "1275"],
        ["各自 Σ<sub>k</sub>（QDA）", "K·p(p+1)/2 個", "6", "<strong>2550</strong>"]])}
"""


# 講義的判別子空間推導；使用 raw string 保留數學語法。
BODIES["lda"] += r"""
<h3 id="w04fisher">LDA 與 Fisher LDA：分類規則與判別方向</h3>
<p>生成式 LDA 從各類的常態分布與共用共變異數出發，計算後驗機率。
Fisher 線性判別分析則直接尋找「類別平均分得開、同類資料又集中」的投影方向；
定義這個準則不需要常態假設。當兩者使用相同的類別平均與共用類內共變異數時，判別方向有相同的幾何結構。</p>
<p>先把 LDA 的分數改寫成距離。省略與類別無關的項，分類等同於最小化</p>
$$\frac12(x-\mu_k)^T\Sigma^{-1}(x-\mu_k)-\log\pi_k.$$
<p>第一項是 Mahalanobis 距離平方的一半。令 $z=\Sigma^{-1/2}x$、
$m_k=\Sigma^{-1/2}\mu_k$，就是把共用類內共變異數變成單位矩陣的<strong>白化（whitening）</strong>。
此時第一項變成 $\|z-m_k\|^2/2$。先驗相等時選最近的中心；先驗不等時仍須扣掉 $\log\pi_k$，
較常見的類別因而得到較大的決策區域。</p>
<p>白化可以想成先轉動座標，再依類內散布縮放各方向，讓同類資料不再沿某個方向特別拉長。這時 Mahalanobis 距離就成了普通的 Euclidean 距離。</p>
<p>白化後的 $K$ 個平均向量 $m_1,\ldots,m_K$ 都在某個至多 $K-1$ 維的仿射子空間 $H$：兩點在一條線上，三點在一個平面上。把新點 $z$ 投影到 $H$，各類距離平方都減去相同的垂直距離：</p>
$$\|z-m_k\|^2=\|\operatorname{proj}_H(z)-m_k\|^2+
\|z-\operatorname{proj}_H(z)\|^2.$$
<p>最後一項不隨類別改變，因此投影不會改變距離的比較，加上相同的先驗修正後也保留分類。LDA 的分類資訊於是集中在至多 $\min(p,K-1)$ 維。這是白化後的幾何關係；不能直接在未白化的原始座標中用普通距離取代 Mahalanobis 距離。</p>
<p>來源：<a href="https://scikit-learn.org/stable/modules/lda_qda.html#mathematical-formulation-of-lda-dimensionality-reduction">講義引用的 LDA 幾何與降維說明</a>。</p>
<p>以 $n_k$ 表示第 k 類筆數、$\bar x_k$ 表示類平均、$\bar x$ 表示總平均，定義類內與類間散布矩陣：</p>
$$W=\sum_{k=1}^K\sum_{i\in C_k}(x_i-\bar x_k)(x_i-\bar x_k)^T.$$
$$B=\sum_{k=1}^K n_k(\bar x_k-\bar x)(\bar x_k-\bar x)^T.$$
<p>$W$ 加總同類觀測的散布，$B$ 加總各類中心相對於總中心的散布；它們尚未除以自由度。
投影成 $a^Tx$ 後，Fisher 比值為</p>
$$J(a)=\frac{a^TBa}{a^TWa}.$$
<p>假設 $W$ 正定，Fisher 最優方向滿足廣義特徵值問題
$Ba=\lambda Wa$。取最大特徵值對應的方向，再依特徵值遞減取後續方向。
不同方向可規範成 $a_i^TWa_j=\delta_{ij}$：這是 <strong>W 內積下的正交</strong>，原始座標中不一定垂直。
也可以先解對稱矩陣 $W^{-1/2}BW^{-1/2}$，再轉回原始座標。</p>
<h4>二類：Fisher 的方向就是 LDA 邊界的法向量</h4>
$$B=\frac{n_1n_2}{n}(\bar x_1-\bar x_2)(\bar x_1-\bar x_2)^T.$$
$$a\propto W^{-1}(\bar x_1-\bar x_2).$$
<p>由於 pooled 共變異數 $\hat\Sigma=W/(n-K)$ 只差一個倍數，
LDA 分數差中的 $\hat\Sigma^{-1}(\bar x_1-\bar x_2)$ 和 Fisher 方向平行。
<strong>方向相同還不等於分類完全相同</strong>：仍要用平均、尺度與先驗設定切點；任意取投影零點當切點並不正確。</p>
<h4>多類：為什麼最多只有 K−1 個方向？</h4>
<p>類間散布的秩滿足 $\operatorname{rank}(B)\le\min(p,K-1)$。
在白化空間中，各類中心都落在至多 K−1 維的仿射子空間。完整的距離分解見下方證明。保留完整的判別子空間，並保留同樣的尺度與先驗，便可重現原 LDA 分類。</p>
<p>若只保留前 $L&lt;\operatorname{rank}(B)$ 個方向，就得到<strong>降秩 LDA（reduced-rank LDA）</strong>。
它依 Fisher 準則保留分離最強的方向；在共用常態模型下可連結到類平均的秩受限最大概似估計。
刪去非零判別方向可能改變分類與後驗機率。K 大於 3 時的二維圖因此通常只是近似視圖。
用 $W$ 規範的座標做最近中心分類前，還須換成共變異數白化尺度；先驗項不能隨意和距離乘上不同倍數。
若 $W$ 奇異，須先處理共線性、降維或使用正則化，不能直接套逆矩陣公式。</p>
<h4>講義的 Iris 例子</h4>
<p>Iris 有花萼長、花萼寬、花瓣長、花瓣寬四個變數；Setosa、Versicolor、Virginica 各 50 筆。
三類最多兩個判別方向，因此完整二維判別圖能保留這個 LDA 分類規則。
使用全部 150 筆擬合、經驗先驗各 1/3，訓練混淆矩陣如下（列是真實類別，欄是預測類別）：</p>
<div style="overflow-x:auto;"><table class="cmp-table" style="width:100%;font-size:.85rem;"><thead><tr><th>真實／預測</th><th>Setosa</th><th>Versicolor</th><th>Virginica</th></tr></thead><tbody>
<tr><th>Setosa</th><td>50</td><td>0</td><td>0</td></tr>
<tr><th>Versicolor</th><td>0</td><td>48</td><td>2</td></tr>
<tr><th>Virginica</th><td>0</td><td>1</td><td>49</td></tr></tbody></table></div>
<p>合計錯 3 筆，訓練正確率 98%，與講義一致。這是對擬合資料的回算，不能當作新花朵的測試正確率。
兩個非零廣義特徵值約 32.191929、0.285391；它們衡量類間與類內散布比，不是原始資料的 PCA 解釋變異比。</p>
""" + quiz("qFisher", "QUIZ · 判別方向與分類", "三類、四個變數的 LDA，保留兩個判別方向一定可以解讀成什麼？", [
(True, "使用相同尺度與先驗，可保留完整 LDA 決策所需的類平均差異", "類間散布的秩至多為 2；完整白化判別子空間以外的距離對各類相同。"),
(False, "兩個方向必定解釋原始資料最多的變異", "這是 PCA 的目標；Fisher LDA 使用類別標籤，最大化類間／類內散布比。"),
(False, "先驗機率不再影響分類", "即使降到完整判別子空間，仍須保留先驗的 log 項。")])

# ── P04 QDA / Naive Bayes ─────────────────────────────────────────────
_qda_code = lab_code(CH, 89) + "\n\n" + lab_code(CH, 93) + "\n\n" + lab_code(CH, 95)
_nb_code = (lab_code(CH, 102) + "\n\n" + lab_code(CH, 110) + "\n\n"
            + lab_code(CH, 116) + "\n\n" + lab_code(CH, 117))

BODIES["qda"] = f"""
  <p>LDA 要求所有類共用同一個 $\\Sigma$。<strong>QDA</strong>（quadratic discriminant analysis）
  讓每一類有自己的共變異數，即 $X\\mid Y=k\\sim N_p(\\mu_k,\\Sigma_k)$。它仍使用 Gaussian 類內分布，但放寬共用共變異數的假設。判別函數為：</p>

  $$\\delta_k(x) = -\\frac{{1}}{{2}}(x - \\mu_k)^{{\\mathsf{{T}}}} \\Sigma_k^{{-1}} (x - \\mu_k)
    - \\frac{{1}}{{2}} \\log |\\Sigma_k| + \\log \\pi_k$$

  <p>展開之後會出現 $x^{{\\mathsf{{T}}}} \\Sigma_k^{{-1}} x$。<strong>因為 $\\Sigma_k$ 隨 k 不同，
  這一項在兩類相減時不會抵消</strong>，所以邊界是 x 的二次曲面——名字裡的「二次」就是這麼來的。</p>

  <p>先驗與類別平均的估法和 LDA 相同，各類共變異數則分別計算：</p>
  $$\\hat\\Sigma_k=\\frac1{{n_k-1}}\\sum_{{i:y_i=k}}(x_i-\\hat\\mu_k)(x_i-\\hat\\mu_k)^\\mathsf T.$$
  <p>這是不偏估計；Gaussian MLE 改除以 $n_k$。每一類都要有足夠資料估計自己的共變異數，這也是 QDA 比 LDA 需要更多資料的原因。</p>

{info("共用 Σ 與否，涉及偏差–變異取捨", '''<strong>參數量：</strong>LDA 只估一個 Σ，
  要 p(p+1)/2 個數；QDA 每類一個，要 K·p(p+1)/2 個。p = 50、K = 2 時是
  1275 對 <strong>2550</strong>。<br>
  <strong>選擇時：</strong>訓練資料少且共用共變異數合理，可先比較 LDA；每類資料充足，
  且各類共變異數明顯不同時，可比較 QDA。<br>
  ISLP 圖 4.9 兩張圖可直接比較這個差異：左圖真實邊界是線性的，LDA 贏（QDA 增加了估計變異）；
  右圖兩類的相關係數一個 +0.7 一個 −0.7，真實邊界是彎的，QDA 贏。''', "warm")}

{viz(svg("w04lda2Svg", 360),
     [rows_card("目前的設定",
                [("模式", "LDA（共用 Σ）", "w04lda2Mode"),
                 ("ρ₁（藍類）", "0.70", "w04lda2R1T"),
                 ("ρ₂（紅類）", "0.70", "w04lda2R2T"),
                 ("邊界的形狀", "—", "w04lda2Shape"),
                 ("獨立測試錯誤（4000 點）", "—", "w04lda2Err")]),
      info_card("怎麼看這張圖",
                '兩個橢圓是各類含 95% 機率的等高線，點是各類固定的 30 筆抽樣。'
                '<span style="color:var(--fit-line);font-weight:700;">紅線</span>是目前模式的決策邊界，'
                '<span style="color:var(--muted);font-weight:700;">灰虛線</span>永遠是 LDA 的線性邊界，'
                '留在那裡當對照。<strong>把 ρ₁ 與 ρ₂ 調成一樣，紅線會壓在灰線上</strong>，'
                '因為 Σ₁ = Σ₂ 時 QDA 退化成 LDA。', "圖 4.9"),
      info_card("為什麼 QDA 的邊界會是圓錐曲線",
                '$\\delta_1(x) - \\delta_2(x) = 0$ 是 x 的二次式，'
                '所以邊界一般是圓錐曲線，特殊參數下也可能退化成直線等情況。'
                '把 ρ₁ 與 ρ₂ 拉到正負兩端，你會看到邊界彎成兩支。'
                '<strong>切換 LDA／QDA 時資料點不會改變</strong>；只改用來分類同一批資料的規則。')],
     "w04lda2Status", "切換共用／各自共變異數，看邊界從直線變成二次曲線。",
     slider("w04lda2R1", "ρ₁", -0.9, 0.9, 0.05, 0.7, "w04lda2Draw")
     + slider("w04lda2R2", "ρ₂", -0.9, 0.9, 0.05, 0.7, "w04lda2Draw")
     + slider("w04lda2D", "μ 位移", 0.6, 2.4, 0.1, 1.4, "w04lda2Draw")
     + '<button class="btn btn-toggle" onclick="w04lda2Toggle()">切換 LDA ↔ QDA</button>'
     + '<button class="btn btn-reset" onclick="w04lda2Reset()">重置</button>',
     provenance=("illustrative", "固定種子同一資料；只切換 LDA／QDA 分類規則"))}

  <h3>Naive Bayes：用類內條件獨立簡化模型</h3>

  <p>LDA 與 QDA 都在猜 $f_k(x)$ 的<strong>形狀</strong>（多變量常態）。
  Naive Bayes 換一個方向：各變數的分布形式可以不同，但假設<strong>在每一類裡面，p 個預測變數互相獨立</strong>：</p>

  $$f_k(x) = f_{{k1}}(x_1) \\times f_{{k2}}(x_2) \\times \\cdots \\times f_{{kp}}(x_p)$$

  <p>條件獨立是額外的簡化假設，不是類別資料自動具有的性質。它把估計一個 $p$ 維聯合分布，拆成估計 $p$ 個一維分布；即使不完全成立，也可能藉由減少估計變異而有不錯的預測表現。</p>
  <p>一維分布仍需選擇或估計。講義對連續特徵使用 Gaussian，估計各類內的平均與變異數；對類別特徵則用該類內各水準的比例。Gaussian Naive Bayes 允許各類有不同的對角共變異數；它對應對角版本的 QDA，若變異數也跨類共用才退回對角版本的 LDA。</p>

{table(["", "對 f<sub>k</sub>(x) 的假設", "邊界形狀", "參數量（p 大時）", "適合考慮的情境"],
       [["LDA", "多變量常態，Σ 共用", "線性", "少", "真實邊界線性、各類近常態、n 小"],
        ["QDA", "多變量常態，Σ<sub>k</sub> 各自", "二次", "多（K·p(p+1)/2）", "邊界明顯彎曲、n 大"],
        ["Naive Bayes", "類內獨立，一維密度任意", "加性（可彎，但沒有交互項）", "Gaussian 版本為 2Kp 個平均與變異數",
         "p 大 n 小、變數近似獨立"],
        ["邏輯斯迴歸", "不假設（直接建模後驗）", "線性", "少（(K−1)(p+1)）", "X 不常態、要做推論"],
        ["KNN", "不指定分布與邊界形式；仍依賴距離及鄰域", "任意", "—（存全部資料）", "邊界極度彎曲、n ≫ p"]])}

  <h3 id="dx-qda">講義完整實作：QDA 與 Naive Bayes</h3>
{card("講義 04 · QuadraticDiscriminantAnalysis", _qda_code, lab_output(CH, 95),
      src=src("89、93、95"),
      note="<code>covariance_[0]</code>是<strong>第一類自己的</strong> Σ̂₁ = "
           "<code>[[1.5066, -0.0392], [-0.0392, 1.5356]]</code>——QDA 每類一個，這是它跟 LDA 的主要差別。"
           "QDA 的 2005 年正確率 <strong>0.5992</strong>，"
           "比 LDA 的 0.560 高。lab 的股市分類比較提醒：股市資料上多出這幾個百分點，"
           "仍需用新的資料評估能否推廣。")}

{card("講義 04 · GaussianNB", _nb_code, lab_output(CH, 116),
      src=src("102、110、116、117"),
      note="<code>theta_</code>跟 <code>lda.means_</code> 一模一樣——"
           "平均數的估法沒差。差別在 <code>var_</code>：Naive Bayes 每類每變數各估一個變異數、"
           "而且<strong>沒有共變異數</strong>（等於把 Σ<sub>k</sub> 限制成對角矩陣）。"
           "正確率 <strong>0.5952</strong>，比 QDA 的 0.5992 差一點、比 LDA 的 0.560 好。")}

{quiz("qQda", "QUIZ · 該用 LDA 還是 QDA",
      "只有 n = 40 筆訓練資料、p = 2，而且你有理由相信真實的決策邊界是線性的。該選哪個？",
      [(True, "可優先比較 LDA。小樣本下，較少的共變異數參數可能讓估計較穩定",
        "對。這正是 ISLP 圖 4.9 左圖與習題 4.8 第 5 題 (d) 的答案："
        "邊界是線性時 QDA 雖然「擬合得下」線性邊界，但它要估兩個 Σ，n = 40 時估計較不穩定，"
        "測試誤差可能較高，仍需用獨立資料比較。"),
       (False, "QDA。它比較有彈性，線性邊界是二次邊界的特例，所以不會更差",
        "「線性是二次的特例」這句話沒錯，但「所以不會更差」錯了。<strong>模型空間包含真解 ≠ 估得準</strong>——"
        "QDA 要多估 p(p+1)/2 = 3 個參數，n = 40 時這些估計很不穩，變異可能抵銷偏差降低的好處。"),
       (False, "兩個一樣，因為 p = 2 時共變異數矩陣只有 3 個參數，差別可以忽略",
        "不對。就算只多 3 個參數，在 n = 40 的資料上仍然是可觀的變異，"
        "而且 QDA 的邊界形狀本身就比較不穩（會彎）。ISLP 的模擬顯示這個差距看得出來。")])}
"""

# ── P05 threshold / confusion matrix / ROC ────────────────────────────
_thr_code1 = lab_code(CH, 57) + "\n\n" + lab_code(CH, 58)
_thr_code2 = lab_code(CH, 156) + "\n\n" + lab_code(CH, 158) + "\n\n" + lab_code(CH, 159)

_CM = ('<div style="overflow-x:auto;">\n'
       '      <table class="cm-table" style="margin:.4rem auto;">\n'
       '        <thead><tr><th></th><th>真實：不違約</th><th>真實：違約</th><th>合計</th></tr></thead>\n'
       '        <tbody>\n'
       '          <tr><th>預測：不違約</th>'
       '<td class="cm-tn" id="w04thrTN">9644</td>'
       '<td class="cm-fn" id="w04thrFN">252</td>'
       '<td id="w04thrRN">9896</td></tr>\n'
       '          <tr><th>預測：違約</th>'
       '<td class="cm-fp" id="w04thrFP">23</td>'
       '<td class="cm-tp" id="w04thrTP">81</td>'
       '<td id="w04thrRP">104</td></tr>\n'
       '          <tr><th>合計</th><td>9667</td><td>333</td><td>10000</td></tr>\n'
       '        </tbody>\n'
       '      </table>\n'
       '      <p class="cm-note" style="text-align:center;">'
       '綠底＝猜對（TN／TP）·　淺紅＝假陽 FP（誤報）·　深紅＝<strong>假陰 FN（漏掉的違約戶）</strong>'
       '</p>\n'
       '      </div>')

BODIES["threshold"] = f"""
  <p>回到二元分類。若兩種錯誤成本相同，用真實後驗機率以 <strong>0.5</strong> 為門檻，可最小化期望分類錯誤率。
  這個 0.5 來自 Bayes 分類器，<strong>而 Bayes 分類器最小化的是「總」錯誤率</strong>，
  這個規則給兩種錯誤相同的權重；若成本不同，應最小化相應的期望損失。</p>

  <p>ISLP 的 <code>Default</code> 例子把這個問題呈現得很清楚。LDA 在 10000 筆訓練資料上的錯誤率是
  <strong>2.75%</strong>，但還要檢查錯誤集中在哪一類：</p>

  <ul>
    <li>資料裡只有 3.33% 的人違約，所以<strong>「一律預測不會違約」這個什麼都沒學的分類器，
    錯誤率是 3.33%</strong>。2.75% 只比它好一點點。</li>
    <li>333 個真的違約的人裡面，LDA <strong>漏掉了 252 個</strong>（75.7%）。
    這個模型漏掉了大部分違約戶。</li>
  </ul>

{info("兩種錯誤有名字，而且權重通常不一樣", '''把「違約 / 有病 / 是垃圾信」當成正類（+）：<br>
  <strong>FP（假陽性）</strong>＝真實為負類，卻預測成正類。<br>
  <strong>FN（假陰性）</strong>＝真實為正類，卻預測成負類。<br>
  <strong>敏感度</strong>（sensitivity, recall）= TP/(TP+FN)＝真實正類中被正確找出的比例。<br>
  <strong>特異度</strong>（specificity）= TN/(TN+FP)＝真實負類中被正確排除的比例。<br>
  <strong>精確率</strong>（precision）= TP/(TP+FP)＝預測為正類的觀測中，實際為正類的比例。''', "warm")}

  <p>門檻值就是調節這兩種錯誤比例的設定。把 0.5 降到 0.2：</p>

  $$\\Pr(\\texttt{{default}} = \\text{{Yes}} \\mid X = x) > 0.2
    \\;\\Longrightarrow\\; \\text{{判為違約}}$$

  <p>ISLP 表 4.5 的結果是：漏掉的違約戶從 252 掉到 <strong>138</strong>（敏感度從 24.3% 升到 58.6%），
  代價是誤報從 23 升到 <strong>235</strong>，總錯誤率從 2.75% 升到 3.73%。
  是否值得取決於漏判與誤報的成本。拖動滑桿，觀察各類錯誤的變化：</p>

{viz(_CM + "\n" + chart("w04thrRoc", "square",
                        "。此圖的重點：LDA 在 Default 上的 ROC 曲線緊貼左上角，AUC = 0.95；"
                        "把門檻值從 0.5 調到 0.2，工作點沿曲線往右上移動——敏感度換來假陽率。"),
     [rows_card("目前的門檻值下",
                [("門檻值", "0.500", "w04thrT"),
                 ("預測會違約的人數", "104", "w04thrNP"),
                 ("敏感度（抓到幾成違約戶）", "24.3%", "w04thrSens"),
                 ("特異度", "99.8%", "w04thrSpec"),
                 ("精確率", "77.9%", "w04thrPrec"),
                 ("總錯誤率", "2.75%", "w04thrErr")]),
      info_card("三種分類規則的結果",
                '<strong>門檻值 0.5：</strong>錯誤率 2.75%，但漏掉 252 / 333 = 75.7% 的違約戶。<br>'
                '<strong>門檻值 0.2：</strong>錯誤率 3.73%，只漏掉 138 個（41.4%）。<br>'
                '<strong>一律猜不違約：</strong>錯誤率 3.33%，漏掉全部 333 個。<br>'
                '這三行分別呈現總錯誤率與兩種錯誤，讓你依用途比較。', "表 4.4／4.5"),
      info_card("ROC 與 AUC",
                'ROC 曲線把<strong>所有</strong>門檻值的（假陽率、真陽率）畫成一條線，'
                '橫軸是假陽率 FP/(FP+TN)，縱軸是敏感度 TP/(TP+FN)。'
                'AUC（area under the curve）是 ROC 曲線下面積，用來概括分數區分正負類的能力。'
                '<strong>AUC = 0.95</strong>（ISLP §4.4.2）；隨機猜是 0.5，完美是 1。'
                '紅點是你現在選的門檻值在曲線上的位置。')],
     "w04thrStatus", "拖動門檻值：混淆矩陣、四個指標與 ROC 上的紅點會同步重算。",
     slider("w04thrSlider", "門檻值", 0, 1, 0.005, 0.5, "w04thrMove")
     + '<button class="btn btn-step" onclick="w04thrSet(0.5)">→ 回到 0.5</button>'
     + '<button class="btn btn-step" onclick="w04thrSet(0.2)">→ 調到 0.2</button>'
     + '<button class="btn btn-reset" onclick="w04thrReset()">重置</button>',
     provenance=("course-data", "ISLP Default；對照表 4.4–4.5 與圖 4.8"))}

{qa("觀念釐清", [
    ("Q：類別不平衡時，「正確率 99%」為什麼可能沒有找出任何正類？該看什麼？",
     "<p>因為<strong>多數類的比例很高，一律預測多數類也能得到高正確率</strong>。假設 1000 個人裡有 10 個得病，"
     "你寫一支 <code>return '沒病'</code> 的程式，正確率就是 99%。它一個病人都沒抓到。</p>"
     "<p>這是<strong>多數類基準正確率</strong>；對應的<strong>多數類基準錯誤率</strong>則是 1%。兩者互為 1 減對方，報告時要跟模型用同一種量尺。"
     "ISLP 用 <code>Default</code> 示範：基準錯誤率 3.33%，LDA 的 2.75% 只是小勝。"
     "lab 的 <code>Caravan</code> 例子中，只有 6% 的人買保險，"
     "KNN 的錯誤率 11.1% 比「全猜不買」的 6.7% <strong>還差</strong>。</p>"
     "<p>該看什麼？先問「哪一種錯誤比較貴」，再挑指標：</p>"
     "<ul><li><strong>怕漏掉正類</strong>（癌症篩檢、詐欺偵測）：看<strong>敏感度／recall</strong>，"
     "並且把門檻值往下調。</li>"
     "<li><strong>怕誤報</strong>（垃圾信過濾、發送行銷成本）：可看<strong>假陽率與精確率</strong>。提高門檻會減少 FP 或保持不變，但精確率是否提高仍需檢查。</li>"
     "<li><strong>要一個不挑門檻值的總結</strong>：看 <strong>AUC</strong>，"
     "並同時查看不同門檻下的錯誤情況。</li>"
     "<li><strong>兩邊都要顧</strong>：可參考 F1（精確率與 recall 的調和平均，定義見本節收合區），但仍要考慮錯誤成本。</li></ul>"
     "<p>報告結果時，<strong>把同一量尺的多數類基準一起報出來</strong>。這樣才能判斷高正確率是否只是反映多數類比例。</p>"),
    ("Q：TP / FP / FN / TN 跟那三個比率的關係是什麼？為什麼醫學篩檢跟垃圾信過濾在意的方向剛好相反？",
     "<p>先把四格與三個比率的<strong>分母</strong>分清楚，這是最容易搞混的地方：</p>"
     "<ul><li><strong>敏感度</strong> = TP/(TP+FN)：分母是<strong>真實</strong>的正類總數（縱向看）。</li>"
     "<li><strong>特異度</strong> = TN/(TN+FP)：分母是<strong>真實</strong>的負類總數（縱向看）。</li>"
     "<li><strong>精確率</strong> = TP/(TP+FP)：分母是<strong>你預測</strong>為正的總數（橫向看）。</li></ul>"
     "<p>ISLP 表 4.7 還給了對照的別名：假陽率就是第一型錯誤、真陽率就是檢定力（power）、"
     "精確率就是正預測值（PPV）。同一個表格，不同學科各叫一套名字。</p>"
     "<p><strong>方向相反是因為兩種錯誤的成本結構不同。</strong></p>"
     "<ul><li><strong>癌症篩檢</strong>：漏掉一個病人（FN）可能致命；誤報（FP）的代價是再做一次檢查。"
     "所以把門檻值調低、犧牲特異度換<strong>高敏感度</strong>。這反映重視避免漏判的成本設定。</li>"
     "<li><strong>垃圾信過濾</strong>：把重要信件丟進垃圾桶（FP，如果正類＝垃圾信）代價很高；"
     "漏掉垃圾信則是另一種代價。因此可提高門檻以減少誤擋，再檢查假陽率及精確率是否符合需求。</li></ul>"
     "<p>lab 的 <code>Caravan</code> 是第三種情況：業務員拜訪一個人有成本，"
     "所以在意的是「被我挑中的人裡有幾成真的會買」。那是<strong>精確率</strong>。"
     "把門檻值從 0.5 降到 0.25，挑出 29 個人、9 個真的買，精確率 31%，"
     "相較於這批測試資料 6.7% 的購買比例，約為 4.6 倍。</p>"),
])}

  <h3 id="dx-thr">講義完整實作：從混淆矩陣算出四個指標</h3>
{card("講義 04 · 手動算 accuracy / sensitivity / precision / FPR", _thr_code1,
      lab_output(CH, 58), src=src("57、58"),
      note="注意 <code>confusion_matrix(真實, 預測)</code> 與 ISLP 的 "
           "<code>confusion_table(預測, 真實)</code> <strong>參數順序相反、矩陣也是轉置的</strong>。"
           "看到別人的混淆矩陣第一件事就是確認哪一軸是真實值，否則敏感度與精確率會對調。"
           "這裡敏感度 0.752 很高，但假陽率也高達 0.685——模型幾乎什麼都猜 Up。")}

{card("講義 04 · Caravan：把門檻值從 0.5 降到 0.25", _thr_code2,
      lab_output(CH, 158), src=src("156、158、159"),
      note="門檻值 0.5 時只有 2 個人被預測會買保險，而且<strong>兩個都猜錯</strong>"
           "（門檻值 0.5 的混淆矩陣為 931／67／2／0）——模型沒有找出任何實際購買者。"
           "降到 0.25 之後挑出 29 個人、其中 9 個真的買了，"
           "精確率 <strong>9/(20+9) = 31.0%</strong>，相較於同一測試集 6.7% 的購買比例，約為 4.6 倍。"
           "<strong>同一個模型、同一組係數，只換了一個門檻值。</strong>")}

{quiz("qThr", "QUIZ · 門檻值",
      "把分類門檻值從 0.5 降到 0.2，下面哪一組變化一定會發生？",
      [(True, "敏感度上升（或持平）、特異度下降（或持平）；總錯誤率不保證變好",
        "對。門檻值降低 → 更多人被判為正類 → TP 與 FP 都只會增加、FN 與 TN 都只會減少。"
        "所以敏感度單調上升、特異度單調下降。總錯誤率則不一定："
        "Default 的例子從 2.75% 升到 3.73%（變差），但這是為了換敏感度而刻意付的代價。"),
       (False, "敏感度與精確率都上升，因為抓到的正類變多了",
        "敏感度確實上升，但<strong>精確率不一定上升或下降</strong>。精確率的分母是「你預測為正的人數」，"
        "新納入觀測的正類比例決定精確率往哪個方向改變。Default 的例子：精確率從 81/104 = 77.9% 掉到 195/430 = 45.3%。"),
       (False, "總錯誤率一定下降，因為模型抓到更多真正的正類",
        "不對，方向反了。使用真實後驗機率、兩種錯誤等成本時，0.5 是最小化母體期望錯誤的門檻值，"
        "估計機率與有限測試集則沒有同樣保證；是否改善仍須在獨立資料檢查。我們願意付這個代價，是因為兩種錯誤的成本不一樣。")])}

{table(["名稱", "定義", "別名", "分母是誰"],
       [["假陽率 FPR", "FP / N", "第一型錯誤、1 − 特異度", "真實的負類"],
        ["真陽率 TPR", "TP / P", "敏感度、recall、檢定力、1 − 第二型錯誤", "真實的正類"],
        ["正預測值 PPV", "TP / P*", "精確率、1 − 錯誤發現比例", "預測為正的"],
        ["負預測值 NPV", "TN / N*", "—", "預測為負的"]])}
  <p style="font-size:.82rem;color:var(--muted);">對照 ISLP 表 4.6／4.7。
  N、P 是真實的負／正類總數；N*、P* 是被預測為負／正的總數。</p>
"""

# ── P06 compare ───────────────────────────────────────────────────────
BODIES["compare"] = f"""
  <p>把各模型的 log-odds 寫成相對於第 K 類的形式，就能比較它們允許的線性、二次與加性項。以下對照 ISLP §4.5.1：</p>

  $$\\text{{LDA：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} b_{{kj}} x_j$$

  $$\\text{{QDA：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} b_{{kj}} x_j + \\sum_{{j=1}}^{{p}}\\sum_{{l=1}}^{{p}} c_{{kjl}} x_j x_l$$

  $$\\text{{Naive Bayes：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} g_{{kj}}(x_j)$$

  <p>比較這三種形式，可得以下四個關係：</p>

{info("四種函數形式的關係（ISLP §4.5.1）", '''<strong>1. LDA 是 QDA 的特例</strong>（所有 c<sub>kjl</sub> = 0）。
  LDA 對 Gaussian 類內分布加上 Σ₁ = ⋯ = Σ<sub>K</sub> 的限制。<br>
  <strong>2. 線性的 log-odds 是加性 log-odds 的特例</strong>（取 g<sub>kj</sub>(x<sub>j</sub>) = b<sub>kj</sub>x<sub>j</sub>）。
  所以 LDA 的 log-odds 屬於這個加性函數形式。這比較的是可表達的後驗函數；LDA 的聯合分布並不因此滿足 Naive Bayes 的類內獨立假設，估計方法也不會相同。<br>
  <strong>3. 常態 Naive Bayes 一般是各類 Σₖ 為對角矩陣的 QDA。</strong>
  若再要求每個變數的變異數跨類別共用，才成為對角 Σ 的 LDA；lab 的 GaussianNB 每類各估變異數。<br>
  <strong>4. QDA 與 Naive Bayes 誰都不是誰的特例。</strong>Naive Bayes 的 g<sub>kj</sub> 可以是任意函數（更彈性），
  但在所用特徵中，它的 log-odds 是加性的，沒有不同特徵間的交互項；QDA 有交互項但被鎖在二次式裡。''')}

  <p>邏輯斯迴歸呢？多類別邏輯斯迴歸的形式跟 LDA 的第一行<strong>字面上完全一樣</strong>。
  建模對象與估計方法不同：LDA 從常態假設推出來，邏輯斯迴歸直接最大化條件概似。
  各類內近似常態、共用共變異數合理時，LDA 可能受益於這些限制；假設不合適時，logistic 可能較有彈性。兩者沒有固定的優劣順序。</p>

  <p>本章的 KNN 採用另一種估計方式：它不寫任何 log-odds 的式子，直接看鄰居投票。
  距離是否有意義、資料是否足夠密集，以及鄰居數和尺度的選擇，都會影響結果；它也不提供可直接解讀的迴歸係數。</p>

  <p>Default 上四個方法的 AUC 幾乎相同；上面的門檻值元件已經完整呈現 ROC 與 AUC，
  可用這個元件比較不同門檻值下的表現。選擇方法時，把候選方法放進
  同一個重抽樣流程，依未見資料的表現與問題的錯誤成本判斷。</p>

  <h3 id="dx-knn">講義完整實作：KNN，唯一的無母數方法</h3>
{card("講義 04 · KNeighborsClassifier(n_neighbors=1)",
      lab_code(CH, 122) + "\n\n" + lab_code(CH, 124), lab_output(CH, 122),
      src=src("122、124"),
      note="K = 1 的 2005 年正確率是 <strong>0.500</strong>，等於公平隨機猜測的期望正確率。"
           "K = 3 升到 0.532；同一份教材比較中的 QDA 正確率更高。"
           "lab 比較的這幾個設定中，在 <code>Smarket</code> 上 QDA 最好。"
           "K = 1 對個別鄰居很敏感；這次結果沒有顯示它比一律猜 Up 的基準更好。")}

{table(["ISLP 情境（§4.5.2）", "資料怎麼產生", "誰贏", "為什麼"],
       [["情境 1", "各類內兩變數不相關的常態，每類 20 筆", "LDA、邏輯斯",
         "邊界是線性的，較有彈性的 KNN 增加了估計變異"],
        ["情境 2", "同上，但類內相關 −0.5", "LDA、邏輯斯",
         "<strong>Naive Bayes 表現變差</strong>——獨立假設被違反"],
        ["情境 3", "類內強負相關的 t 分布，每類 50 筆", "邏輯斯",
         "邊界仍線性但不常態，LDA／QDA 吃虧"],
        ["情境 4", "兩類相關係數 +0.5 與 −0.5 的常態", "QDA",
         "真實邊界二次，正好是 QDA 的假設"],
        ["情境 5", "不相關常態，反應由複雜非線性函數生成", "KNN-CV",
         "邊界很彎；<strong>KNN-1 最差</strong>——平滑度沒選對"],
        ["情境 6", "各類對角但不同的 Σ，每類只有 6 筆", "Naive Bayes",
         "類內獨立假設成立，而樣本太少，QDA 共變異數估計較不穩定"]])}

{quiz("qCmp", "QUIZ · 解析比較",
      "ISLP §4.5.1 說「LDA 是 Naive Bayes 的特例」。這句話怎麼可能成立？"
      "LDA 明明允許變數相關、Naive Bayes 明明假設獨立。",
      [(True, "因為兩者的 log-odds 都能寫成 $a_k+\\sum_{j=1}^p g_{kj}(x_j)$；LDA 對應各 $g_{kj}$ 為線性函數的情況",
        "對。這裡比較的是<strong>模型能表達的函數族</strong>，包含關係可由 log-odds 的形式判斷。"
        "Naive Bayes 的 g<sub>kj</sub> 可以是任意一維函數，取成 b<sub>kj</sub>x<sub>j</sub> 就退化成線性邊界，"
        "而 LDA 的邊界正好是線性的。因此 LDA 的線性 log-odds 落在加性函數的表達範圍內；這不表示兩者的聯合分布或估計結果相同。"),
       (False, "因為當 Σ 是對角矩陣時，LDA 的變數就真的獨立了，兩者於是相同",
        "對角且共用的共變異數確實是兩種模型重合的一種情況，但不足以解釋本題對一般共變異數的比較。"
        "這裡比較的是線性與加性 log-odds 的函數形式，沒有宣稱任意 LDA 都滿足類內獨立。"),
       (False, "這句話只在 p = 1 時成立，p ≥ 2 時兩者沒有包含關係",
        "不對。p = 1 時獨立假設是空的、結論過於簡單；ISLP 那條結論對一般 p 都成立。"
        "「QDA 與 Naive Bayes 誰都不是誰的特例」表示兩者的函數族沒有包含關係。")])}
"""

# ── P07 Poisson / GLM ─────────────────────────────────────────────────
BODIES["poisson"] = f"""
  <p>講義最後用計數資料，把線性迴歸與 logistic regression 連到廣義線性模型（GLM）。</p>

  <p>前面兩種 y：連續的（第 3 章）與類別的（本章）。還有第三種常見的 y——<strong>計數</strong>。
  ISLP 用 <code>Bikeshare</code>（華盛頓特區每小時的單車租借數，n = 8645）示範。</p>

  <p>直接對計數擬合線性迴歸會遇到三個問題：</p>

  <ul>
    <li><strong>會預測出負數。</strong>ISLP 說 <code>Bikeshare</code> 上有 <strong>9.6%</strong>
    的擬合值是負的——負的租借數沒有意義。</li>
    <li><strong>變異數不是常數。</strong>清晨下雨的時段平均 5.05 人、標準差 3.73；
    春天早上晴天的時段平均 243.59 人、標準差 131.7。<strong>平均大變異也大</strong>，
    這提示變異可能隨平均改變；是否違反條件同變異假設，仍需檢查完整模型的殘差。</li>
    <li><strong>y 是整數。</strong>Gaussian 線性模型使用連續的條件分布，無法直接描述計數的離散分布；線性條件平均本身仍可用於計數。</li>
  </ul>

  <p>反應是非負整數時，可以考慮 Poisson 分布。但<strong>計數不一定服從 Poisson</strong>；這是對分布形狀與平均–變異關係的模型假設，需要依資料判斷。給定預測變數後：</p>
  $$Y\\mid X=x\\sim\\operatorname{{Poisson}}(\\lambda(x)).$$

  $$\\Pr(Y = k \\mid X=x) = \\frac{{e^{{-\\lambda}} \\lambda^k}}{{k!}}, \\qquad k = 0, 1, 2, \\ldots
    \\qquad\\text{{而且}}\\quad \\mathbb{{E}}(Y\\mid X=x) = \\mathrm{{Var}}(Y\\mid X=x) = \\lambda(x)$$

  <p><strong>Poisson 迴歸</strong>讓 λ 隨預測變數而變，而且是對 <strong>log λ</strong> 擬合線性式：</p>

  $$\\log \\lambda(X_1, \\ldots, X_p) = \\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p
    \\qquad\\Longleftrightarrow\\qquad
    \\lambda = e^{{\\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p}}$$

  <p>log link 讓 $\\lambda(x)=e^{{\\eta(x)}}$ 永遠為正，因而避免負的平均租借數。條件平均等於條件變異數，則是 Poisson 分布本身的性質。平均數可以不是整數；真正的觀測值仍是非負整數。</p>

{info("係數要用乘法解讀", '''因為線性的是 log λ，所以 X<sub>j</sub> 增加一單位讓
  <strong>λ 乘上 e^βⱼ</strong>，不是加上 βⱼ。<br>
  ISLP 表 4.11 的例子：<code>weathersit[cloudy/misty]</code> 的係數是 −0.08，
  e<sup>−0.08</sup> = 0.923——<strong>陰天的平均租借量只有晴天的 92.3%</strong>。<br>
  這跟邏輯斯迴歸的「勝算乘上 e^β」是同一個模式：<strong>連結函數取了 log，解讀就從加法變乘法。</strong>''')}

  <h3>GLM：把三個模型收進同一個框架</h3>

  <p>三種模型都先描述 $Y\\mid X$ 的條件分布，再把條件平均 $\\mu(x)=E(Y\\mid X=x)$ 接到線性預測式。用 $g$ 表示<strong>連結函數</strong>，用 $\\eta$ 表示線性分數：</p>
  $$g(\\mu(x))=\\eta(x)=\\beta_0+\\beta_1x_1+\\cdots+\\beta_px_p.$$
  <div style="overflow-x:auto"><table class="cmp-table"><thead><tr><th>模型</th><th>條件分布</th><th>條件平均</th><th>條件變異數</th><th>連結函數</th></tr></thead><tbody>
  <tr><td>Gaussian 線性迴歸</td><td>$N(\\mu(x),\\sigma^2)$</td><td>$\\mu(x)=\\eta(x)$</td><td>$\\sigma^2$</td><td>$g(\\mu)=\\mu$</td></tr>
  <tr><td>Logistic regression</td><td>$\\operatorname{{Bernoulli}}(p(x))$</td><td>$\\mu(x)=p(x)$</td><td>$p(x)(1-p(x))$</td><td>$g(p)=\\log\\{{p/(1-p)\\}}$</td></tr>
  <tr><td>Poisson regression</td><td>$\\operatorname{{Poisson}}(\\lambda(x))$</td><td>$\\mu(x)=\\lambda(x)=e^{{\\eta(x)}}$</td><td>$\\lambda(x)$</td><td>$g(\\lambda)=\\log\\lambda$</td></tr>
  </tbody></table></div>
  <p>Gaussian、Bernoulli 與 Poisson 都屬於指數分布族。GLM 以這類條件分布、線性預測式與連結函數組成模型。對單次二元結果，Bernoulli 由反應值的形式決定；Gaussian 或 Poisson 的分布形狀則仍是額外假設。</p>
  <p>在 <code>sm.GLM()</code> 中，三者分別使用 <code>sm.families.Gaussian()</code>、<code>sm.families.Binomial()</code> 與 <code>sm.families.Poisson()</code>。單次 Bernoulli 是試驗次數為 1 的 Binomial，因此 logistic 範例使用 Binomial family。</p>

  <h3 id="dx-poi">講義完整實作：用 <code>sm.GLM()</code> 建立三種模型</h3>
{card("講義 04 · Poisson 迴歸（Bikeshare）",
      lab_code(CH, 188) + "\n\n" + lab_code(CH, 190), None, src=src("188、190"),
      note="跟前面擬合邏輯斯迴歸的那一行比一比："
           "<code>family=sm.families.Binomial()</code> 換成 "
           "<code>family=sm.families.Poisson()</code>，仍沿用相同的 GLM 建模介面。"
           "係數的補齊步驟（<code>mnth[Dec]</code> 取其餘月份的負和）是因為用了 "
           "<code>contrast('mnth', 'sum')</code>。這個設定讓月份係數加總為0，"
           "因此係數呈現相對於各月份平均水準的差異。Poisson模型使用對數連結，"
           "這裡的係數是在對數尺度上比較；固定其他變數後，兩月份的係數差取指數，"
           "才是預測平均租借量的比值。對照 ISLP 表 4.11 與圖 4.15。"
           "係數可對照課本表 4.11：intercept 4.12、temp 0.79、"
           "weathersit[light rain/snow] −0.58。")}

{info("Poisson 迴歸的限制：過度分散", '''Poisson 模型要求條件變異數等於條件平均數。
  若控制預測變數後，變異仍大於平均，這叫<strong>過度分散</strong>（overdispersion）。
  ISLP 的腳註指出 <code>Bikeshare</code> 就有這個問題，
  <strong>導致表 4.11 的 z 值被高估</strong>（看起來比實際更顯著）。<br>
  補救方式是 quasi-Poisson 或負二項迴歸——超出本章範圍，但解讀結果時仍須留意：
  若條件平均模型正確且其他估計條件成立，係數仍可能一致；一般 Poisson 標準誤與 p 值則可能失準。''', "warm")}

{quiz("qPoi", "QUIZ · Poisson 迴歸",
      "Poisson 迴歸擬合的是 log λ 而不是 λ 本身。最主要的理由是什麼？",
      [(True, "使用 log link 後，平均 λ 是線性分數的指數，因此永遠為正，計數的平均不會被預測成負數",
        "對。這正是線性迴歸在 <code>Bikeshare</code> 上 9.6% 擬合值變成負數的原因。"
        "順帶的好處是係數變成乘法解讀（λ 乘上 e^βⱼ），跟邏輯斯迴歸的勝算比同一個模式。"),
       (False, "因為 log 轉換會讓計數資料變成常態分布，這樣才能用最小平方法",
        "不對。Poisson 迴歸<strong>不做</strong>「把 y 取 log 再擬合線性模型」這件事。"
        "那是另一種做法（而且 y = 0 時無法取 log）。這裡取 log 的對象是<strong>平均 λ</strong>，"
        "不是 y；估計用的是最大概似，不是最小平方。"),
       (False, "因為 log 是唯一能讓 Poisson 迴歸有封閉解的連結函數",
        "不對。一般多變數 Poisson 迴歸沒有簡單的係數封閉解，跟邏輯斯迴歸一樣要反覆更新參數。"
        "log 之所以是預設（正規連結），是因為它讓 μ 落在 (0, ∞) 也便於數學推導，不是因為有封閉解。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 4.8 第 6 題（a）",
      "某邏輯斯迴歸用 X₁ = 讀書時數、X₂ = 大學 GPA 預測「這科拿 A」，"
      "估到 β̂₀ = −6、β̂₁ = 0.05、β̂₂ = 1。一個讀 40 小時、GPA 3.5 的學生拿到 A 的機率是多少？",
      [(True, "約 0.378",
        "對。先算線性部分：$-6 + 0.05 \\times 40 + 1 \\times 3.5 = -0.5$，"
        "再代進邏輯斯函數 $p = e^{-0.5}/(1+e^{-0.5}) = 0.3775$。"
        "第 (b) 小題問「要讀幾小時才有 50% 機會」——p = 0.5 等於 log-odds = 0，"
        "解 $-6 + 0.05x + 3.5 = 0$ 得 x = <strong>50 小時</strong>。"),
       (False, "約 −0.5",
        "−0.5 是 <strong>log-odds</strong>，不是機率。機率不可能是負的。"
        "這一題就是在測「線性的是 log-odds、不是機率」——算完線性部分還要過一次邏輯斯函數。"),
       (False, "約 0.622",
        "這是 1 − 0.378，也就是「拿不到 A」的機率。方向弄反了："
        "邏輯斯函數 $e^{\\eta}/(1+e^{\\eta})$ 在 η 為負時一定小於 0.5。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 4.8 第 9 題",
      "這一題只考勝算。（a）違約勝算是 0.37 的人，實際違約的比例是多少？"
      "（b）某人違約機率 16%，她的勝算是多少？",
      [(True, "(a) 約 0.27　(b) 約 0.19",
        "對。勝算 = p/(1−p)，所以 p = odds/(1+odds) = 0.37/1.37 = <strong>0.270</strong>；"
        "反過來 odds = 0.16/0.84 = <strong>0.190</strong>。"
        "順手記一個直覺：p 很小的時候 odds ≈ p，兩者差不多；p 接近 1 時 odds 會衝向無限大。"),
       (False, "(a) 0.37　(b) 0.16",
        "這是把勝算跟機率當成同一件事。它們只在 p 很小的時候近似相等；"
        "0.37 的勝算對應的機率是 0.27，差了 0.1，不能混用。"),
       (False, "(a) 約 0.63　(b) 約 5.25",
        "兩個都取到補集或倒數了。(a) 0.63 是 1 − 0.37；(b) 5.25 = 0.84/0.16 是"
        "「不違約」的勝算。題目問的是違約，分子要放 p。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 4.8 第 8 題",
      "假設沒有同一輸入卻有衝突標籤的重複點，且最近鄰包含自己。資料切成一半訓練一半測試。邏輯斯迴歸的訓練錯誤率 20%、測試錯誤率 30%；"
      "1-NN 的「訓練與測試平均」錯誤率是 18%。該選哪一個？",
      [(True, "邏輯斯迴歸。1-NN 的訓練錯誤率是 0，所以它的測試錯誤率約 36%，比 30% 差",
        "對，這一題的陷阱就在「平均」。K = 1 時每個訓練點的最近鄰居就是它自己，"
        "訓練錯誤率必定為 0。所以 (0 + 測試) / 2 = 18% ⟹ 測試錯誤率 = <strong>36%</strong>。"
        "36% &gt; 30%，選邏輯斯迴歸。"),
       (False, "1-NN。它的平均錯誤率 18% 比邏輯斯的兩個數字都低",
        "這是直接拿平均跟測試錯誤率比。<strong>訓練與測試錯誤率不能混在一起平均之後再比較</strong>——"
        "訓練誤差是被最佳化過的，本來就偏低，1-NN 的訓練誤差甚至是 0。要比就只比測試誤差。"),
       (False, "資訊不足，因為題目沒有分別給 1-NN 的訓練與測試錯誤率",
        "資訊其實夠。關鍵是「K = 1 的訓練錯誤率必定為 0」這個結構性事實——"
        "知道它就能從平均反推測試錯誤率。這也是課本要考的點。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 4.8 第 5 題（a）（d）",
      "（a）Bayes 決策邊界是<strong>線性</strong>時，LDA 與 QDA 誰在訓練集上比較好？測試集呢？"
      "（d）「就算邊界是線性的，QDA 彈性夠大也擬合得下，所以測試誤差還是會比較好」——對嗎？",
      [(True, "依本章偏差–變異直覺，常預期 QDA 的訓練誤差較低、LDA 的測試誤差較低；(d) 沒有保證",
        "對。QDA 比較有彈性，所以<strong>訓練</strong>誤差常預期較低，但沒有逐份資料的保證；高斯最大概似最佳化的是概似，並非直接最小化分類錯誤。"
        "若 LDA 的類內常態與共用共變異數假設也合理，多出的彈性通常主要增加估計變異；僅知道邊界線性，仍不能保證偏差或測試誤差的排序。"
        "因此常預期<strong>測試</strong>誤差 LDA 較低，仍需獨立評估。(d) 的錯誤在於把「模型空間包含真解」"
        "當成「估得準」。這是偏差–變異取捨的核心誤解。"
        "第 (c) 小題討論樣本增加：QDA 的估計變異通常會降低，使它較有機會發揮彈性。"),
       (False, "兩個集合都是 LDA 較好，因為真實邊界是線性的",
        "兩個集合都保證 LDA 較好說得太強；較有彈性的 QDA 常預期能降低訓練誤差，但不保證測試誤差降低。"
        "這正是訓練誤差不能用來選模型的原因。分辨「訓練」與「測試」是這一題的全部重點。"),
       (False, "兩個集合都是 QDA 較好，因為線性邊界是二次邊界的特例",
        "兩個集合都沒有這種必然保證；這正是課本第 (d) 小題要釐清的差別。"
        "模型類包含關係不保證實際估計量的偏差或變異排序——"
        "分類可借用偏差–變異的直覺理解，但不能把平方損失的分解等式直接套到 0／1 錯誤率。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>這裡整理各模型的假設、分類規則與主要公式。</p>

  <h3>五種方法對照</h3>
{table(["方法", "在建模什麼", "邊界形狀", "關鍵假設", "參數量", "什麼時候選它"],
       [["邏輯斯迴歸", "後驗 Pr(Y|X)（判別式）", "線性", "log-odds 對 x 線性", "(K−1)(p+1)",
         "<strong>兩類的預設選擇</strong>、要推論、X 不常態"],
        ["LDA", "類條件 f<sub>k</sub>(x)（生成式）", "線性", "常態 + Σ 共用", "Kp + p(p+1)/2 + K−1",
         "各類近常態、n 小、兩類分得很開"],
        ["QDA", "類條件 f<sub>k</sub>(x)", "二次", "常態 + Σ<sub>k</sub> 各自", "Kp + K·p(p+1)/2 + K−1",
         "邊界明顯彎曲、n 大"],
        ["Naive Bayes", "類條件 f<sub>k</sub>(x)", "加性（無交互項）", "類內各變數獨立", "Gaussian 版本：2Kp + K−1",
         "<strong>p 大 n 小</strong>、變數近似獨立"],
        ["KNN", "以鄰居的類別比例估計後驗機率", "任意", "不指定參數形式；依賴距離與鄰域", "存全部資料",
         "邊界極度彎曲且 n ≫ p"]])}

  <h3>Default 的分類結果</h3>
{table(["", "TN", "FP", "FN", "TP", "錯誤率", "敏感度", "出處"],
       [["LDA，門檻值 0.5", "9644", "23", "<strong>252</strong>", "81", "2.75%", "24.3%", "ISLP 表 4.4"],
        ["LDA，門檻值 0.2", "9432", "235", "<strong>138</strong>", "195", "3.73%", "58.6%", "ISLP 表 4.5"],
        ["Naive Bayes，門檻值 0.5", "9621", "46", "244", "89", "2.90%", "26.7%", "ISLP 表 4.8"],
        ["Naive Bayes，門檻值 0.2", "9339", "328", "130", "203", "4.58%", "61.0%", "ISLP 表 4.9"],
        ["一律預測「不違約」", "9667", "0", "333", "0", "3.33%", "0.0%", "基準錯誤率"]])}


  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["邏輯斯函數", "$p(X) = \\dfrac{e^{\\beta_0+\\beta_1X}}{1+e^{\\beta_0+\\beta_1X}}$", "式 4.2"],
        ["logit / log-odds", "$\\log\\dfrac{p(X)}{1-p(X)} = \\beta_0+\\beta_1X$", "式 4.4，線性的是這個"],
        ["多類別邏輯斯", "$\\log\\dfrac{\\Pr(Y=k|x)}{\\Pr(Y=K|x)} = \\beta_{k0}+\\sum_j\\beta_{kj}x_j$",
         "式 4.12"],
        ["softmax", "$\\Pr(Y=k|x) = \\dfrac{e^{\\beta_{k0}+\\sum_j\\beta_{kj}x_j}}{\\sum_l e^{\\beta_{l0}+\\sum_j\\beta_{lj}x_j}}$",
         "式 4.13，等價寫法"],
        ["Bayes 定理", "$\\Pr(Y=k|X=x) = \\dfrac{\\pi_k f_k(x)}{\\sum_l \\pi_l f_l(x)}$", "式 4.15"],
        ["LDA 判別函數（p = 1）", "$\\delta_k(x) = x\\dfrac{\\mu_k}{\\sigma^2} - \\dfrac{\\mu_k^2}{2\\sigma^2} + \\log\\pi_k$",
         "式 4.18，x 的一次式"],
        ["LDA 邊界（K = 2, 等先驗）", "$x = \\dfrac{\\mu_1+\\mu_2}{2}$", "式 4.19，兩平均的中點"],
        ["LDA 判別函數（p &gt; 1）",
         "$\\delta_k(x) = x^{\\mathsf{T}}\\Sigma^{-1}\\mu_k - \\tfrac12\\mu_k^{\\mathsf{T}}\\Sigma^{-1}\\mu_k + \\log\\pi_k$",
         "式 4.24"],
        ["QDA 判別函數",
         "$\\delta_k(x) = -\\tfrac12(x-\\mu_k)^{\\mathsf{T}}\\Sigma_k^{-1}(x-\\mu_k) - \\tfrac12\\log|\\Sigma_k| + \\log\\pi_k$",
         "式 4.28，x 的二次式"],
        ["Naive Bayes", "$f_k(x) = \\prod_{j=1}^{p} f_{kj}(x_j)$", "式 4.29，類內獨立"],
        ["Poisson 迴歸", "$\\log\\lambda(X) = \\beta_0+\\beta_1X_1+\\cdots+\\beta_pX_p$", "式 4.36"],
        ["GLM 連結函數", "$g\\big(\\mathbb{E}(Y\\mid X)\\big) = \\eta(X) = \\beta_0+\\beta_1X_1+\\cdots+\\beta_pX_p$",
         "式 4.42"]])}

{info("本章重點", '''<strong>1. 邏輯斯迴歸線性的是 log-odds，不是機率。</strong>
  係數 β₁ 要讀成「勝算乘上 e^β₁」；同樣的 β₁ 對應的機率差異隨位置而變。
  係數描述模型中的條件關聯，因果解讀另需研究設計與假設。<br>
  <strong>2. 生成式模型描述類別比例與類內 X 分布；判別式模型直接描述 Y 的條件分布。</strong>
  LDA 的邊界形式跟邏輯斯字面上相同（式 4.32）；差別是前者從常態假設推、後者最大化條件概似。
  共用 Σ 給線性邊界、各自 Σ<sub>k</sub> 給二次邊界、類內獨立給加性邊界。<br>
  <strong>3. 0.5 這個門檻值只是「總錯誤率最小」的產物。</strong>
  比較分類規則時，先問「哪種錯誤比較貴」，再調門檻值，
  並且把同一量尺的多數類基準與混淆矩陣一起報出來。''')}


"""

# ══════════════════════════════════════════════════════════════════════
# COVERAGE-20260910 BEGIN

BODIES['logistic'] += r"""
<h3>從觀測到估計：完整的最大概似問題</h3>
<p>給定 X 後，假設各 $Y_i$ 獨立且 $Y_i\sim\operatorname{Bernoulli}(p_i)$，$p_i=\operatorname{logistic}(x_i^T\beta)$，$x_i$ 含截距。用 $\eta_i=x_i^T\beta$ 表示線性預測量，估計問題為</p>
$$\max_\beta L(\beta)=\prod_i p_i^{y_i}(1-p_i)^{1-y_i},\qquad
\ell(\beta)=\sum_i\{y_i\eta_i-\log(1+e^{\eta_i})\}.$$
<p>最小化 $-\ell$ 也就是最小化二元交叉熵。對數概似的一階導數稱為分數函數（score），二階偏導數組成 Hessian 矩陣：</p>
$$U(\beta)=X^T(y-p),\qquad \nabla^2\ell(\beta)=-X^TWX,\qquad W=\operatorname{diag}\{p_i(1-p_i)\}.$$
<p>一個 Newton 更新為 $\beta^{new}=\beta+(X^TWX)^{-1}X^T(y-p)$；實作用線性方程求解並檢查目標改善，避免直接計算逆矩陣。也可寫成反覆加權最小平方（IRLS）：令工作反應 $z=X\beta+W^{-1}(y-p)$，以 W 加權擬合 z，重算 p、W、z，直到收斂。</p>
<p>完全或準完全分離時，無懲罰的有限 MLE 可能不存在；秩不足時係數也不唯一，不能把數值停止一概當成成功估計。</p>
<p>正確指定的條件模型、有限內點 MLE 與一般大樣本正則條件下，$\widehat{\operatorname{Cov}}(\hat\beta)=(X^T\hat WX)^{-1}$；係數 SE 是對角線平方根，Wald z 為 $\hat\beta_j/\widehat{SE}_j$，近似 95% CI 為 $\hat\beta_j\pm1.96\widehat{SE}_j$。觀測獨立不等於 p 相同；給定不同 X 時，反應變異數可不同。</p>
<p>來源：<a href="https://dafriedman97.github.io/mlbook/content/c3/s1/logistic_regression.html#parameter-estimation">講義連結的概似估計教材</a>、<a href="https://web.stanford.edu/class/archive/stats/stats200/stats200.1172/Lecture26.pdf">Stanford 邏輯斯迴歸推論講義</a>。</p>
""" + proof('w04proofLogistic', '概似、梯度、Hessian 與 IRLS', r"""
<p>Bernoulli 機率質量為 $p_i^{y_i}(1-p_i)^{1-y_i}$。獨立性讓聯合概似相乘；取對數後，利用 $\log p_i=\eta_i-\log(1+e^{\eta_i})$ 與 $\log(1-p_i)=-\log(1+e^{\eta_i})$，得到正文的 ℓ。</p>
<p>$\partial p_i/\partial\eta_i=p_i(1-p_i)$，故 $\partial\ell/\partial\beta=\sum_ix_i(y_i-p_i)$，再微分為 $-\sum_i p_i(1-p_i)x_ix_i^T=-X^TWX$。任意 v 的二次型為 $-\sum_i p_i(1-p_i)(x_i^Tv)^2\le0$，所以 ℓ 凹；在有限 β、X 滿欄秩時嚴格凹，但這不保證最大值在有限處取得。</p>
<p>對 score 做一次 Taylor 線性化：$0\approx U(\beta)-X^TWX(\beta^{new}-\beta)$。解出正文 Newton 更新，並將右側寫成 $X^TW[X\beta+W^{-1}(y-p)]$，便得到 IRLS 加權 normal equations。</p>
<p>Hessian 給定 X 後不含 y，故期望負 Hessian 就是 Fisher information $I=X^TWX$。在 MLE 漸近常態條件下，其逆矩陣近似係數共變異數。若條件模型的假設不成立，此簡單逆資訊公式不一定可靠，需採用適合該資料的推論方法；不能只憑分類正確率驗證推論條件。</p>
""")
BODIES['multinomial'] += r"""
<h3>多類別模型如何估計？</h3>
<p>概念和二分類一樣：對第 $i$ 筆資料，只取模型給實際類別 $y_i$ 的機率 $p_{i,y_i}$。給定預測變數後，各筆結果獨立，因此</p>
$$L(\beta)=\prod_{i=1}^n p_{i,y_i}.$$
$$\ell(\beta)=\sum_{i=1}^n\log p_{i,y_i}.$$
<p>例如三筆資料的實際類別是 A、C、B；模型依 A、B、C 順序給出的機率如下：</p>
<table class="cmp-table"><thead><tr><th>實際類別</th><th>A</th><th>B</th><th>C</th><th>取用的機率</th></tr></thead><tbody>
<tr><td>A</td><td>0.7</td><td>0.2</td><td>0.1</td><td>0.7</td></tr>
<tr><td>C</td><td>0.1</td><td>0.2</td><td>0.7</td><td>0.7</td></tr>
<tr><td>B</td><td>0.2</td><td>0.6</td><td>0.2</td><td>0.6</td></tr></tbody></table>
$$L=0.7\times0.7\times0.6=0.294.$$
<p>MLE 調整所有係數，讓這個乘積最大。實際上通常最大化它的對數，避免把許多小機率直接相乘。</p>
<h4>第 K 類當基準</h4>
<p>對 $k=1,\ldots,K-1$ 設 $\eta_{ik}=\beta_{k0}+\sum_j\beta_{kj}x_{ij}$，並固定 $\eta_{iK}=0$，則</p>
$$p_{ik}=\frac{e^{\eta_{ik}}}{1+\sum_{\ell=1}^{K-1}e^{\eta_{i\ell}}},\quad
p_{iK}=\frac1{1+\sum_{\ell=1}^{K-1}e^{\eta_{i\ell}}}.$$
$$\ell(\beta)=\sum_i\left[\sum_{k=1}^{K-1}I(y_i=k)\eta_{ik}
-\log\left(1+\sum_{\ell=1}^{K-1}e^{\eta_{i\ell}}\right)\right].$$
<h4>對稱 softmax 與識別限制</h4>
<p>若將所有類別寫成 $p_{ik}=e^{\eta_{ik}}/\sum_\ell e^{\eta_{i\ell}}$，同一個對數概似是</p>
$$\ell(\beta)=\sum_i\left[\eta_{i,y_i}-\log\left(\sum_{\ell=1}^Ke^{\eta_{i\ell}}\right)\right].$$
<p>每類分數同時加上相同的 $c(x_i)$，分子與分母的共同倍數會抵消，機率不變。因此 K 組係數不能全部自由且唯一地估計；固定 $\beta_K=0$ 就回到基準類寫法。這是同一組類別機率的不同參數化。</p>
<p>一般沒有封閉解，仍用 Newton 等數值方法找 $\hat\beta=\arg\max_\beta\ell(\beta)$。負對數概似 $-\sum_i\log p_{i,y_i}$ 就是多類別 cross-entropy；它延續了二分類對正確類別機率的估計原則。</p>
<p>延伸：<a href="https://dafriedman97.github.io/mlbook/content/c3/s1/logistic_regression.html#multiclass-logistic-regression">講義引用的多類別 logistic 推導</a>。</p>
""" + proof('w04proofSoftmax', '多類別概似梯度與識別性', r"""
<p>令 $y_{ik}=I(y_i=k)$，表示第 $i$ 筆是否屬於第 $k$ 類；它是 0／1 指示變數，每筆恰有一類為 1。再寫 $\eta_{ik}=x_i^T\beta_k$，其中 $x_i$ 含截距，則 $\ell=\sum_{i,k}y_{ik}\eta_{ik}-\sum_i\log\sum_l e^{\eta_{il}}$，其中用到 $\sum_ky_{ik}=1$。對 $\beta_k$ 微分，第一項給 $\sum_i y_{ik}x_i$，第二項給 $\sum_i p_{ik}x_i$。若把每個 $\beta_k$ 換成 $\beta_k+c$，分子分母共同乘 $e^{x_i^Tc}$，相除抵消，故須施加識別限制。</p>
""")
BODIES['lda'] += r"""
<h3>把生成式模型的參數估出來</h3>
<p>第 k 類有 $n_k$ 筆資料。經驗先驗 $\hat\pi_k=n_k/n$，平均向量 $\hat\mu_k=\sum_{i\in C_k}x_i/n_k$。在這個收合區，$W=\sum_k\sum_{i:y_i=k}(x_i-\hat\mu_k)(x_i-\hat\mu_k)^T$ 是類內散布矩陣，和前面 logistic 的權重矩陣不同。共用共變異數的高斯最大概似估計為 W/n；課本常用的 pooled 不偏估計為 W/(n−K)，兩者須分清楚。QDA 的類別共變異數 MLE 除以 $n_k$，不偏版本除以 $n_k-1$。</p>
<p>分類時先選定一致的共變異數估法，再代入分數。LDA 要估的 Σ 正定，QDA 則每一類的 Σk 都須可逆；某類樣本少或欄位共線時，可改用正則化或降低維度。Naive Bayes 只估每類每個特徵的一維條件分布；連續變數可用常態或其他密度模型，類別變數則估機率，零計數可能讓整個乘積為零，實務上常以平滑避免這個問題。</p>
""" + proof('w04proofGenerative', '類別平均、共變異數與判別函數', r"""
<p>完整資料的對數概似可分成 $\sum_kn_k\log\pi_k$ 與各類高斯項。加上 $\sum_k\pi_k=1$ 的乘數約束，微分得 $n_k/\pi_k=\lambda$，相加給 λ=n，因此 $\hat\pi_k=n_k/n$。對 $\mu_k$ 微分得 $\Sigma^{-1}\sum_{i\in C_k}(x_i-\mu_k)=0$，故為類平均。</p>
<p>代回平均後，共用共變異數的負對數概似除去常數為 $\frac n2\log|\Sigma|+\frac12\operatorname{tr}(\Sigma^{-1}W)$。對精確度矩陣 $A=\Sigma^{-1}$ 微分給 $-\frac n2 A^{-1}+\frac12W=0$，所以 $\hat\Sigma=W/n$。估了 K 個平均後，W 的期望為 (n−K)Σ，因而不偏版本改除以 n−K。</p>
<p>分類比較 $\log\pi_k+\log f_k(x)$。展開共用 Σ 的二次型，$-x^T\Sigma^{-1}x/2$ 與 $-\log|\Sigma|/2$ 不依 k 而抵消，留下 $x^T\Sigma^{-1}\mu_k-\mu_k^T\Sigma^{-1}\mu_k/2+\log\pi_k$。QDA 的 Σk 不同，二次項與 log determinant 都不能刪掉。</p>
""")
BODIES['lda'] += proof('w04proofFisher', 'Fisher 方向、白化與判別子空間', r"""
<p>W 正定時，可把分母固定為 $a^TWa=1$。Lagrangian $a^TBa-\lambda(a^TWa-1)$ 的導數為 $2Ba-2\lambda Wa=0$。令 $u=W^{1/2}a$，得到對稱特徵問題 $W^{-1/2}BW^{-1/2}u=\lambda u$。取歐氏正交的 u，轉回後即有 $a_i^TWa_j=\delta_{ij}$。</p>
<p>二類時 $\bar x=(n_1\bar x_1+n_2\bar x_2)/n$；代入 B 的定義並合併，得 $B=(n_1n_2/n)dd^T$，$d=\bar x_1-\bar x_2$。因此非零廣義特徵方向平行於 $W^{-1}d$，也平行於 LDA 邊界法向量。</p>
<p>一般 K 類滿足 $\sum_k n_k(\bar x_k-\bar x)=0$，所以 B 的秩至多 K−1。白化後，將 z 分成類中心仿射子空間內的 $z_\parallel$ 與垂直成分 $z_\perp$，有 $\|z-m_k\|^2=\|z_\parallel-m_k\|^2+\|z_\perp\|^2$。最後一項對所有類別相同，比較距離與先驗時抵消；保留完整判別空間即可保留分類，截掉非零方向則未必。</p>
""")
BODIES['poisson'] += r"""
<h3>Poisson 的估計與 GLM 的變異數</h3>
<p>給定 X 後 $Y_i$ 獨立，$\mu_i=\exp(x_i^T\beta)$，Poisson 的對數概似為</p>
$$\ell(\beta)=\sum_i\{y_ix_i^T\beta-e^{x_i^T\beta}-\log(y_i!)\},\qquad
U=X^T(y-\mu),\quad I=X^T\operatorname{diag}(\mu_i)X.$$
<p>可採 Newton／IRLS 求解。全部計數為零時，截距 MLE 趨向負無限大，沒有有限解。</p>
<p>GLM 建模的是 $Y\mid X$。指數分布族寫成 $\exp\{[y\theta-b(\theta)]/a(\phi)+c(y,\phi)\}$，其條件平均為 $b'(\theta)$、變異數為 $a(\phi)b''(\theta)$。Bernoulli 的變異數為 $p(1-p)$，Poisson 為 μ，Gaussian 則是共同 σ²；只有條件獨立不代表同變異數。過度分散時，仍可討論平均模型，但 Poisson 的一般 SE 會失準，要另選變異模型或適當穩健推論。</p>
""" + proof('w04proofPoisson', 'Poisson score 與指數分布族的平均變異數', r"""
<p>取各筆 Poisson 質量函數的對數並相加，再以 $\mu_i=e^{x_i^T\beta}$ 代入，就得到正文 ℓ。對 β 微分分別為 $\sum_i x_i(y_i-\mu_i)$ 與 $-\sum_i\mu_ix_ix_i^T$。只有截距時 score 為 $\sum_i y_i-ne^{\beta_0}$，零點給 $e^{\hat\beta_0}=\bar y$（需平均數為正）。</p>
<p>對指數分布族的總機率 1 對 θ 微分，得到 $E[(Y-b'(\theta))/a(\phi)]=0$，所以 $E[Y]=b'(\theta)$。再用 score 的變異等於期望負二階導數，得到 $\operatorname{Var}(Y)/a(\phi)^2=b''(\theta)/a(\phi)$，即正文變異公式；交換微分與積分需一般正則條件。</p>
""")


BODIES['poisson'] += r"""
<h3>Bikeshare：同一特徵，兩種係數量尺</h3>
<p>講義比較線性迴歸與 Poisson 迴歸：月份與時段以類別變數納入，工作日、溫度與天氣則說明不同量尺的係數解讀。以下列出講義係數的四捨五入值：</p>
<table class="cmp-table"><thead><tr><th>變數</th><th>線性模型</th><th>Poisson 的 log 平均模型</th></tr></thead><tbody>
<tr><td>工作日</td><td>1.27</td><td>0.01</td></tr><tr><td>溫度</td><td>157.21</td><td>0.79</td></tr>
<tr><td>陰天／霧</td><td>−12.89</td><td>−0.08</td></tr><tr><td>小雨／雪</td><td>−66.49</td><td>−0.58</td></tr><tr><td>大雨／雪</td><td>−109.75</td><td>−0.93</td></tr></tbody></table>
<p>例如控制模型內其他欄位後，小雨／雪在線性模型中是平均租借數少約 66.49；Poisson 模型則是平均租借數乘 $e^{-0.58}\approx0.56$。溫度的一單位須依資料原來的編碼解讀，不能直接當攝氏一度。月份／時段圖顯示冬季較低、夏季較高，以及早晚時段的高峰；線性模型的縱軸是平均租借數的加法差，Poisson 圖則是 log 平均的差，兩張圖不能直接比較係數高度。</p>
"""
BODIES['logistic'] += r"""
<h3>預測機率的信賴區間</h3>
<p>對固定新輸入 $x_0$，令 $\hat\eta=x_0^T\hat\beta$、$s_\eta^2=x_0^T\widehat Vx_0$，其中 $\widehat V$ 是完整係數共變異數矩陣。常用近似 95% 機率信賴區間為 $[\operatorname{logistic}(\hat\eta-1.96s_\eta),\operatorname{logistic}(\hat\eta+1.96s_\eta)]$。不能把每個係數 CI 的下端一起代入、上端一起代入：那會漏掉係數間的共變異數。</p>
<p>這是對事件機率的估計不確定性，個別新反應仍是 0 或 1；不能照線性迴歸在 logit 的變異數裡隨意加 1 當成預測區間。</p>


""" + proof('w04proofProbabilityCI', '線性預測量到機率的區間', r"""
<p>MLE 的漸近常態近似給 $x_0^T\hat\beta$ 的變異數 $x_0^TVx_0$。logistic 函數單調遞增，所以把 η 的區間兩端逐一通過 logistic 函數，涵蓋事件 $\eta\in[L,U]$ 與 $\operatorname{logistic}(\eta)\in[\operatorname{logistic}(L),\operatorname{logistic}(U)]$ 相同。這保留 η 區間的近似涵蓋率且不越出 (0,1)。</p>
<p>若用一階 delta method，$\nabla_\beta p=p(1-p)x_0$，因此 $\widehat{SE}(\hat p)=\hat p(1-\hat p)s_\eta$。直接用 $\hat p\pm1.96SE$ 在接近 0 或 1 時可能越界；單純截到 [0,1] 不會自動修正近似涵蓋率。</p>
""")


# DIRECT-LINKS-20260910

BODIES['logistic'] += r"""
<h3>反應誤差、潛在變數與完全分離</h3>
<p>正文已用 Bernoulli 說明反應誤差。以下是講義附錄連結的另一種表示，以及完全分離的推導；可參考<a href="https://stats.stackexchange.com/questions/124818/logistic-regression-error-term-and-its-distribution">誤差與潛在變數討論</a>及<a href="https://stats.stackexchange.com/questions/254124/why-does-logistic-regression-become-unstable-when-classes-are-well-separated">分離時的估計問題</a>。</p>
<p>給定 x，logistic 模型的反應仍是 Bernoulli，不是 logistic 分布。若定義誤差 $e=Y-p(x)$，它以機率 p 取 1−p，以機率 1−p 取 −p，條件平均為零、變異數為 p(1−p)。因此不能再自由估一個與 p 無關的共同誤差變異數，也不能把 logit(p) 當成 logit(Y)。</p>
<p>另一種等價的生成表示是 $Y=I\{x^T\beta+\epsilon>0\}$，其中 $\epsilon$ 服從標準 logistic 分布。這裡的 ε 是未觀測連續變數上的誤差，和上面的二點誤差 e 不同。取相同 x 並不決定固定的 0 或 1，仍需要依 p 抽樣。</p>
<p>完全分離時，無懲罰的概似可能沒有有限最大點。資料也可能因小樣本偶然分離，不能把它當成母體機率必為 0 或 1。一般可加入正則化或使用針對分離的估計方法；對分離資料反覆做普通 pairs bootstrap 不會自動解決有限 MLE 不存在的問題。</p>
<p>用固定門檻值 t 分類，logistic 在<strong>所用特徵</strong>上的邊界為 $x^T\beta=\log[t/(1-t)]$；如果特徵包含原始變數的平方或交互作用，邊界在原始輸入空間可呈非線性。</p>
""" + proof('w04proofLatent', '潛在 logistic 表示與分離時的概似極限',r"""
<p>標準 logistic 的 CDF 為 $F(u)=1/(1+e^{-u})$。因此 </p>$$P(x^T\beta+\epsilon>0\mid x)=1-F(-x^T\beta)=\operatorname{logistic}(x^T\beta)$$<p>。另一方面，Bernoulli 反應的 $E[Y-p]=0$，</p>$$E[(Y-p)^2]=p(1-p)^2+(1-p)p^2=p(1-p)$$<p>。</p>
<p>令 $s_i=2y_i-1$。完全分離表示存在 v 使所有 $s_ix_i^Tv>0$。沿 β=cv、c→∞，每項概似為 $\operatorname{logistic}(cs_ix_i^Tv)\to1$，故總對數概似遞增趨近 0。有限 c 時每項仍小於 1，不能取得上確界，所以沒有有限 MLE。</p>
""") + proof('w04proofMLELimit', 'score 的變異與大樣本係數共變異數',r"""
<p>在正確指定且可交換微分與積分的模型，對 $\int f_\theta(z)dz=1$ 微分，得到 $E[u_\theta(Z)]=0$。再微分一次，得到 $E[u_\theta u_\theta^T]=-E[\nabla u_\theta]=J$，這是每筆資料的資訊等式。</p>
<p>假設 MLE 一致、真參數在內點、J 正定且滿足 score 中央極限定理與 Hessian 大數法則，則 $n^{-1/2}U_n(\theta_0)\Rightarrow N(0,J)$，$-n^{-1}\nabla U_n(\tilde\theta)\to J$。對 $U_n(\hat\theta)=0$ 作 Taylor 展開：</p>
$$\sqrt n(\hat\theta-\theta_0)=\left[-\frac1n\nabla U_n(\tilde\theta)\right]^{-1}\frac{U_n(\theta_0)}{\sqrt n}\Rightarrow N(0,J^{-1}).$$
<p>總資訊約為 nJ，所以估計共變異數約為總資訊的逆。模型錯置時，score 變異 B 與期望負 Hessian A 不再相同，結果變成 $A^{-1}BA^{-1}/n$。觀測資訊是<strong>負 對數概似的 Hessian</strong>，不是其逆；SE 則是逆資訊矩陣對角元素的平方根，也不是先逐一取對角元素再倒數。</p>
""")
BODIES['lda'] += r"""
<h3>為什麼二類的最小平方與 LDA 方向有關？</h3>
<p>這是講義在二元編碼處所附的<a href="https://stats.stackexchange.com/questions/31459/what-is-the-relationship-between-regression-and-linear-discriminant-analysis-ld">OLS 與 LDA 關係討論</a>；它補充前章的連結。</p>
<p>用 0／1 表示兩類，對中心化 X 做含截距的 OLS。若類內散布 W 正定、兩類平均不同，OLS 斜率向量與 $W^{-1}(\bar x_1-\bar x_0)$ 平行，也就是 Fisher／LDA 的方向；但機率尺度、截距與先驗決定的切點仍不同，不能直接推論兩者使用 0.5 門檻就必定給相同分類。</p>

""" + proof('w04proofOlsLda', '二類 OLS 與 LDA 的方向',r"""
<p>設 d 為兩類平均差、$a=n_0n_1/n$。中心化 X 的總散布為 $T=X^TX=W+add^T$，而 $X^Ty=ad$。Sherman–Morrison 等式給</p>
$$\hat\beta_{OLS}=aT^{-1}d=\frac{a}{1+ad^TW^{-1}d}W^{-1}d.$$
<p>乘數為正，所以方向平行；分類仍須使用相同尺度、中心與先驗。</p>
""")
BODIES['compare'] += r"""
<h3>QDA log-odds 中的係數到底是什麼？</h3>
<p>以第 K 類為基準，令 $A_k=\Sigma_k^{-1}$。完整形式為 $a_k+b_k^Tx+x^TC_kx$，其中</p>
$$a_k=\log\frac{\pi_k}{\pi_K}-\frac12\log\frac{|\Sigma_k|}{|\Sigma_K|}-\frac12\mu_k^TA_k\mu_k+\frac12\mu_K^TA_K\mu_K,$$
$$b_k=A_k\mu_k-A_K\mu_K,\qquad C_k=\frac12(A_K-A_k).$$
<p>注意 Ck 使用「兩個逆矩陣的差」，一般不等於 $(\Sigma_K-\Sigma_k)^{-1}/2$。對稱 Ck 的 $x^TC_kx$ 同時包含各平方項與交互作用；所有共變異數相同時 Ck=0，退回 LDA 的線性 log-odds。</p>
""" + proof('w04proofQdaCoefficients','從後驗比逐項展開QDA',r"""
<p>Bayes 分母抵消後，log 後驗比等於 $\log(\pi_k/\pi_K)+\log f_k(x)-\log f_K(x)$。高斯常數中的 $-p\log(2\pi)/2$ 抵消；留下 log determinant 差與兩個二次型。逐一展開 </p>$$-(x-\mu_k)^TA_k(x-\mu_k)/2=-x^TA_kx/2+x^TA_k\mu_k-\mu_k^TA_k\mu_k/2$$<p>，再減去基準類的對應式，收集常數、一次與二次項，便得到 a、b、C。</p>
""")
BODIES['threshold'] += r"""
<h3>F1 與隨機分數的 AUC 基準</h3>
$$F_1=\frac{2\,\mathrm{precision}\,\mathrm{recall}}{\mathrm{precision}+\mathrm{recall}}=\frac{2TP}{2TP+FP+FN}.$$
<p>F1不使用TN，適合某些重視正類的任務，但不能代替錯誤成本分析。分母為零時須事先規定回報方式。門檻值降低保證recall不降，卻不保證precision下降或上升，因為新納入觀測的真實正類比例也會變。</p>
<p>AUC可解讀為隨機抽一個正類和一個負類時，正類分數較高的機率，加上一半平手機率。若分數與類別獨立且兩類使用同一分數分布，母體AUC為0.5；有限測試集的實現值可高可低。把分數全部取反會把AUC變成1−AUC，但這個操作不能利用測試標籤來挑方向。</p>
""" + proof('w04proofRandomAuc','獨立隨機分數的AUC為二分之一',r"""
<p>在虛無情境，正類分數 S+ 與負類分數 S− 為同分布的獨立抽樣，所以交換對稱性給 $P(S_+>S_-)=P(S_->S_+)$。令平手機率為 q，兩個嚴格排序的機率各為 (1−q)/2，因此 AUC=(1−q)/2+q/2=1/2。</p>
""")

# COVERAGE-20260910 END

PAGEJS = r"""
/* ===== classification 本頁元件（id 與全域一律 w04 前綴）===== */

/* ---------- 小工具 ---------- */
function w04sv(id, v, d) { const e = $(id); if (e) e.textContent = HC.fmt(v, d); }
function w04tx(id, s) { const e = $(id); if (e) e.textContent = s; }
function w04lab(id, v, d) { const e = $(id + 'V'); if (e) e.textContent = HC.fmt(v, d); }
/* stats.css 的 .axlab / .vlab 有 fill，CSS 規則會壓過 presentation attribute，
   所以要自訂顏色時得寫成 inline style（優先權最高）。 */
function w04txt(s, px, py, str, color, g, anchor) {
  const n = s.txtPx(px, py, str, { cls: 'axlab', anchor: anchor || 'start' }, g);
  if (color) n.setAttribute('style', 'font-family:' + HC.MONO + ';font-size:11px;font-weight:600;fill:' + color);
  return n;
}
/* 把一條可能衝出 y 定義域的曲線切成幾段畫，避免給 SVG 天文數字座標 */
function w04clip(s, pts, attrs, g) {
  let run = [];
  for (const p of pts) {
    const ok = Number.isFinite(p[1]) && p[1] >= s.yd[0] && p[1] <= s.yd[1];
    if (ok) { run.push(p); } else { if (run.length > 1) s.poly(run, attrs, g); run = []; }
  }
  if (run.length > 1) s.poly(run, attrs, g);
}

/* ---------- P00 為什麼不用迴歸（hybrid：烘焙 Default 的兩組擬合，即時讀值）---------- */
let w04whySvc = null, w04whyOnlyLog = false;
function w04whySetup() {
  w04whySvc = HC.svg('w04whySvg', { xd: [0, 2700], yd: [-0.32, 1.16], h: 330 });
  w04whySvc.grid(6, 6, { xtitle: 'balance（信用卡月結餘，美元）', ytitle: '違約機率 p', ydec: 1 });
}
function w04whyDraw() {
  const F = FRAMES_w04why, s = w04whySvc;
  if (!s) return;
  const g = s.clearLayer('main');
  /* 合法區間 [0,1] 的上下界 */
  s.seg(s.xd[0], 0, s.xd[1], 0, { cls: 'resid', sw: 1.4 }, g);
  s.seg(s.xd[0], 1, s.xd[1], 1, { cls: 'resid', sw: 1.4 }, g);
  s.txtPx(s.pad.l + 6, s.Y(1) - 6, 'p = 1', { cls: 'axlab' }, g);
  /* 線性版跑出 [0,1] 的區段：標紅 */
  if (!w04whyOnlyLog) {
    s.box(0, -0.32, F.zeroAt, 0, { fill: 'rgba(192,57,43,.16)' }, g);
    w04txt(s, s.X(F.zeroAt) + 8, s.Y(-0.19), 'balance < ' + F.zeroAt.toFixed(0)
      + ' 線性版給負機率', HC.tok.accent, g);
    const lp = HC.stat.seq(s.xd[0], s.xd[1], 40).map(x => [x, F.lin.b0 + F.lin.b1 * x]);
    s.poly(lp, { cls: 'fit', sw: 2.6 }, g);
    w04txt(s, s.X(1980), s.Y(F.lin.b0 + F.lin.b1 * 1980) - 9, '線性迴歸', HC.tok.accent, g);
  }
  /* 邏輯斯 */
  const gp = HC.stat.seq(s.xd[0], s.xd[1], 160).map(x => {
    const e = Math.exp(F.logit.b0 + F.logit.b1 * x);
    return [x, e / (1 + e)];
  });
  s.poly(gp, { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g);
  w04txt(s, s.X(1700), s.Y(0.80), '邏輯斯迴歸', HC.tok.accent3, g);
  /* rug：上排 y=1 是違約、下排 y=0 是沒違約 */
  F.pts.forEach(p => {
    const y0 = p[1] ? 1 : 0, c = p[1] ? HC.tok.b : HC.tok.a;
    s.seg(p[0], y0 - 0.035, p[0], y0 + 0.035, { stroke: c, sw: 1.1, cls: 'ln' }, g);
  });
  /* 目前的 balance */
  const b = parseFloat($('w04whyBal').value);
  const el = F.lin.b0 + F.lin.b1 * b;
  const ee = Math.exp(F.logit.b0 + F.logit.b1 * b), eg = ee / (1 + ee);
  s.seg(b, s.yd[0], b, s.yd[1], { stroke: HC.tok.muted, sw: 1.3, dash: '4 3', cls: 'ln' }, g);
  if (!w04whyOnlyLog) s.dot(b, el, { r: 5.5, fill: HC.tok.accent, stroke: '#fff', sw: 1.4 }, g);
  s.dot(b, eg, { r: 5.5, fill: HC.tok.accent3, stroke: '#fff', sw: 1.4 }, g);
  w04tx('w04whyBal2', b.toFixed(0));
  w04lab('w04whyBal', b, 0);
  w04sv('w04whyLin', el, 4);
  w04sv('w04whyLog', eg, 4);
  w04tx('w04whyOk', el < 0 ? '不合法（負機率）' : (el > 1 ? '不合法（大於 1）' : '剛好還在 [0,1] 內'));
  setStatus('w04whyStatus', 'balance = ' + b.toFixed(0) + ' 時，線性迴歸給 '
    + HC.fmt(el, 4) + '，邏輯斯給 ' + HC.fmt(eg, 4) + '。'
    + (el < 0 ? '<strong>線性版是負數——這不是機率。</strong>'
      : '兩者都落在 [0,1] 裡，但線性模型的預測並未限制在此範圍內；往左移動滑桿就會出現負值。'));
}
function w04whyMove() { w04whyDraw(); }
function w04whyJump(v) { $('w04whyBal').value = String(v); w04whyDraw(); }
function w04whyToggle() {
  w04whyOnlyLog = !w04whyOnlyLog;
  w04whyDraw();
  setStatus('w04whyStatus', w04whyOnlyLog
    ? '只留邏輯斯曲線：整條線都在 0 與 1 之間，兩端逼近但永遠碰不到。'
    : '兩條一起看：紅色直線遲早會離開 [0,1]，綠色 S 曲線不會。');
}
function w04whyReset() {
  w04whyOnlyLog = false;
  $('w04whyBal').value = '1000';
  w04whyDraw();
  setStatus('w04whyStatus', '拖滑桿選一個 balance，右邊會同時給出兩個模型的預測機率。');
}

/* ---------- P01 S 曲線形狀器（live）---------- */
let w04shapeS1 = null, w04shapeS2 = null;
function w04shapeSetup() {
  w04shapeS1 = HC.svg('w04shapeSvg', { xd: [-6, 6], yd: [-0.06, 1.06], h: 250 });
  w04shapeS1.grid(6, 4, { xtitle: 'x', ytitle: '機率 p(x)', ydec: 1 });
  w04shapeS2 = HC.svg('w04shapeSvg2', { xd: [-6, 6], yd: [-8, 8], h: 220 });
  w04shapeS2.grid(6, 4, { xtitle: 'x', ytitle: 'log-odds 與 odds', ydec: 0 });
}
function w04shapeDraw() {
  const b0 = parseFloat($('w04shapeB0').value), b1 = parseFloat($('w04shapeB1').value);
  w04lab('w04shapeB0', b0, 2); w04lab('w04shapeB1', b1, 2);
  const P = x => { const e = Math.exp(b0 + b1 * x); return e / (1 + e); };
  const xs = HC.stat.seq(-6, 6, 200);
  /* 上圖：機率 */
  const s = w04shapeS1, g = s.clearLayer('main');
  s.seg(-6, 0.5, 6, 0.5, { cls: 'resid', sw: 1.2 }, g);
  s.poly(xs.map(x => [x, P(x)]), { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g);
  if (Math.abs(b1) > 1e-6) {
    const xh = -b0 / b1;
    if (xh > -6 && xh < 6) {
      s.seg(xh, -0.06, xh, 1.06, { stroke: HC.tok.accent, sw: 1.4, dash: '4 3', cls: 'ln' }, g);
      s.dot(xh, 0.5, { r: 5, fill: HC.tok.accent, stroke: '#fff', sw: 1.3 }, g);
    }
  }
  w04txt(s, s.pad.l + 8, s.Y(0.5) - 7, 'p = 0.5', HC.tok.muted, g);
  /* 下圖：log-odds（直線）與 odds（指數，超出就切斷） */
  const s2 = w04shapeS2, g2 = s2.clearLayer('main');
  s2.seg(-6, 0, 6, 0, { cls: 'resid', sw: 1.2 }, g2);
  w04clip(s2, xs.map(x => [x, b0 + b1 * x]),
    { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g2);
  w04clip(s2, xs.map(x => [x, Math.exp(b0 + b1 * x)]),
    { cls: 'ln', stroke: HC.tok.accent, sw: 2.2, dash: '6 4' }, g2);
  w04txt(s2, s2.pad.l + 8, s2.Y(6.6), 'log-odds = β₀ + β₁x（直線）', HC.tok.accent3, g2);
  w04txt(s2, s2.pad.l + 8, s2.Y(4.8), 'odds = exp(β₀+β₁x)（虛線）', HC.tok.accent, g2);
  /* 側欄 */
  w04tx('w04shapeB0T', HC.fmt(b0, 2));
  w04tx('w04shapeB1T', HC.fmt(b1, 2));
  w04sv('w04shapeP0', P(0), 4);
  w04sv('w04shapeP1', P(1), 4);
  w04tx('w04shapeHalf', Math.abs(b1) > 1e-6 ? HC.fmt(-b0 / b1, 2) : '不存在（β₁ = 0）');
  w04sv('w04shapeOR', Math.exp(b1), 4);
  setStatus('w04shapeStatus', 'β₀ = ' + HC.fmt(b0, 2) + '、β₁ = ' + HC.fmt(b1, 2)
    + '：勝算比 = ' + HC.fmt(Math.exp(b1), 3)
    + '（x 每加 1，勝算乘這個數）。上圖顯示機率，下圖那條實線永遠是直的。');
}
function w04shapeReset() {
  $('w04shapeB0').value = '-1'; $('w04shapeB1').value = '0.8';
  w04shapeDraw();
}

/* ---------- P03 一維 LDA ↔ QDA（live）---------- */
let w04lda1Svc = null, w04lda1Qda = false;
function w04lda1Setup() {
  w04lda1Svc = HC.svg('w04lda1Svg', { xd: [-7, 7], yd: [0, 0.46], h: 320 });
  w04lda1Svc.grid(7, 4, { xtitle: 'x', ytitle: 'πₖ · fₖ(x)', ydec: 2 });
}
/* 回傳目前的邊界（0、1 或 2 個點） */
function w04lda1Bounds(m1, m2, s1, s2, p1) {
  const p2 = 1 - p1;
  if (Math.abs(s1 - s2) < 1e-9) {
    if (Math.abs(m1 - m2) < 1e-9) return [];
    return [(m1 + m2) / 2 + s1 * s1 * Math.log(p2 / p1) / (m1 - m2)];
  }
  const a = 1 / (2 * s2 * s2) - 1 / (2 * s1 * s1);
  const b = m1 / (s1 * s1) - m2 / (s2 * s2);
  const c = m2 * m2 / (2 * s2 * s2) - m1 * m1 / (2 * s1 * s1)
    + Math.log(p1 / p2) + Math.log(s2 / s1);
  if (Math.abs(a) < 1e-12) return Math.abs(b) < 1e-12 ? [] : [-c / b];
  const disc = b * b - 4 * a * c;
  if (disc < 0) return [];
  const r = Math.sqrt(disc);
  return [(-b - r) / (2 * a), (-b + r) / (2 * a)].sort((u, v) => u - v);
}
function w04lda1Draw() {
  const m1 = parseFloat($('w04lda1M1').value), m2 = parseFloat($('w04lda1M2').value);
  const r1 = parseFloat($('w04lda1S1').value), r2 = parseFloat($('w04lda1S2').value);
  const p1 = parseFloat($('w04lda1P1').value), p2 = 1 - p1;
  ['w04lda1M1', 'w04lda1M2'].forEach((i, k) => w04lab(i, k ? m2 : m1, 2));
  w04lab('w04lda1S1', r1, 2); w04lab('w04lda1S2', r2, 2); w04lab('w04lda1P1', p1, 2);
  /* LDA 模式：兩類共用一個併合後的 σ */
  const pooled = Math.sqrt((r1 * r1 + r2 * r2) / 2);
  const s1 = w04lda1Qda ? r1 : pooled, s2 = w04lda1Qda ? r2 : pooled;
  const s = w04lda1Svc, g = s.clearLayer('main');
  const f1 = x => p1 * HC.stat.dnorm(x, m1, s1);
  const f2 = x => p2 * HC.stat.dnorm(x, m2, s2);
  const xs = HC.stat.seq(-7, 7, 240);
  const top = Math.max(0.12, Math.max(...xs.map(x => Math.max(f1(x), f2(x)))) * 1.18);
  s.domain([-7, 7], [0, top]);
  s.grid(7, 4, { xtitle: 'x', ytitle: 'πₖ · fₖ(x)', ydec: 2 });
  const bs = w04lda1Bounds(m1, m2, s1, s2, p1);
  bs.forEach(x => {
    if (x > -7 && x < 7) {
      s.seg(x, 0, x, top, { stroke: HC.tok.accent, sw: 2.2, dash: '6 4', cls: 'ln' }, g);
      w04txt(s, s.X(x) + 5, s.Y(top) + 13, HC.fmt(x, 2), HC.tok.accent, g);
    }
  });
  s.poly(xs.map(x => [x, f1(x)]), { stroke: HC.tok.a, sw: 2.8, cls: 'ln' }, g);
  s.poly(xs.map(x => [x, f2(x)]), { stroke: HC.tok.b, sw: 2.8, cls: 'ln' }, g);
  w04txt(s, s.X(m1), s.Y(f1(m1)) - 8, '第 1 類', HC.tok.a, g, 'middle');
  w04txt(s, s.X(m2), s.Y(f2(m2)) - 8, '第 2 類', HC.tok.b, g, 'middle');
  w04tx('w04lda1Mode', w04lda1Qda ? 'QDA（各自 σ）' : 'LDA（共用 σ）');
  w04tx('w04lda1Pri', HC.fmt(p1, 2) + ' · ' + HC.fmt(p2, 2));
  w04tx('w04lda1Sig', HC.fmt(s1, 2) + ' · ' + HC.fmt(s2, 2));
  const tied = Math.abs(m1 - m2) < 1e-10 && Math.abs(s1 - s2) < 1e-10 && Math.abs(p1 - p2) < 1e-10;
  w04tx('w04lda1Bnd', tied ? '所有位置分數相同' : (bs.length ? bs.map(v => HC.fmt(v, 2)).join(' 與 ') : '沒有切換點'));
  w04tx('w04lda1Mid', HC.fmt((m1 + m2) / 2, 2));
  const boundaryText = tied
    ? '兩類加權密度處處重合，所有位置都平手；需要另定平手規則。'
    : (bs.length ? (bs.length === 2 ? '邊界有兩個點：' : '邊界只有一個點：')
      + bs.map(v => HC.fmt(v, 2)).join(' 與 ')
      + (bs.length === 1 && !w04lda1Qda && Math.abs(p1 - 0.5) < 1e-9
        ? '，剛好是兩個平均的中點。' : '。')
      : '沒有切換點，第 ' + (f1(0) > f2(0) ? '1' : '2') + ' 類的加權密度處處較高。');
  setStatus('w04lda1Status', (w04lda1Qda ? 'QDA' : 'LDA') + ' 模式，' + boundaryText);
}
function w04lda1Toggle() {
  w04lda1Qda = !w04lda1Qda;
  w04lda1Draw();
}
function w04lda1Reset() {
  w04lda1Qda = false;
  $('w04lda1M1').value = '-1.25'; $('w04lda1M2').value = '1.25';
  $('w04lda1S1').value = '1'; $('w04lda1S2').value = '1'; $('w04lda1P1').value = '0.5';
  w04lda1Draw();
}

/* ---------- P04 二維 LDA ↔ QDA（live）---------- */
let w04lda2Svc = null, w04lda2Qda = false;
function w04lda2Setup() {
  w04lda2Svc = HC.svg('w04lda2Svg', { xd: [-5, 5], yd: [-5, 5], h: 360 });
  w04lda2Svc.grid(5, 5, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
}
function w04lda2Inv(S) {
  const d = S[0] * S[3] - S[1] * S[2];
  return { inv: [S[3] / d, -S[1] / d, -S[2] / d, S[0] / d], det: d };
}
/* 30 筆抽樣：用 Cholesky 把標準常態轉成指定的 Σ */
function w04lda2Sample(mu, rho, seed, n) {
  const rand = HC.stat.lcg(seed), out = [];
  const r = Math.max(-0.985, Math.min(0.985, rho));
  const t = Math.sqrt(1 - r * r);
  for (let i = 0; i < (n || 30); i++) {
    const z1 = HC.stat.normal(rand), z2 = HC.stat.normal(rand);
    out.push([mu[0] + z1, mu[1] + r * z1 + t * z2]);
  }
  return out;
}
function w04lda2Ellipse(mu, rho) {
  const r = Math.max(-0.985, Math.min(0.985, rho)), t = Math.sqrt(1 - r * r), k = 2.4477;
  const pts = [];
  for (let i = 0; i <= 90; i++) {
    const a = i / 90 * 2 * Math.PI, c = Math.cos(a), s = Math.sin(a);
    pts.push([mu[0] + k * c, mu[1] + k * (r * c + t * s)]);
  }
  return pts;
}
function w04lda2Draw() {
  const r1i = parseFloat($('w04lda2R1').value), r2i = parseFloat($('w04lda2R2').value);
  const d = parseFloat($('w04lda2D').value);
  w04lab('w04lda2R1', r1i, 2); w04lab('w04lda2R2', r2i, 2); w04lab('w04lda2D', d, 1);
  const pooledR = (r1i + r2i) / 2;
  const r1 = w04lda2Qda ? r1i : pooledR, r2 = w04lda2Qda ? r2i : pooledR;
  const mu1 = [-d, -d], mu2 = [d, d];
  const S1 = [1, r1, r1, 1], S2 = [1, r2, r2, 1];
  const SP = [1, pooledR, pooledR, 1];
  const A = w04lda2Inv(S1), B = w04lda2Inv(S2), P = w04lda2Inv(SP);
  const s = w04lda2Svc, g = s.clearLayer('main');
  /* LDA 的線性邊界（永遠畫，當對照）：w·x = c */
  const dm = [mu1[0] - mu2[0], mu1[1] - mu2[1]];
  const w1 = P.inv[0] * dm[0] + P.inv[1] * dm[1];
  const w2 = P.inv[2] * dm[0] + P.inv[3] * dm[1];
  const mid = [(mu1[0] + mu2[0]) / 2, (mu1[1] + mu2[1]) / 2];
  const cc = w1 * mid[0] + w2 * mid[1];
  const linePts = [];
  if (Math.abs(w2) > 1e-9) {
    HC.stat.seq(-5, 5, 60).forEach(u => linePts.push([u, (cc - w1 * u) / w2]));
  } else if (Math.abs(w1) > 1e-9) {
    HC.stat.seq(-5, 5, 60).forEach(v => linePts.push([cc / w1, v]));
  }
  if (linePts.length) {
    w04clip(s, linePts, { stroke: HC.tok.muted, sw: 1.8, dash: '5 4', cls: 'ln' }, g);
  }
  /* QDA 的二次邊界：對每個 u 解 v 的二次式（係數用三點取樣反推） */
  const Q = (u, v) => {
    const q = (M, mu) => {
      const a = u - mu[0], b = v - mu[1];
      return M[0] * a * a + (M[1] + M[2]) * a * b + M[3] * b * b;
    };
    return 0.5 * (q(B.inv, mu2) - q(A.inv, mu1)) + 0.5 * Math.log(B.det / A.det);
  };
  if (w04lda2Qda) {
    const us = HC.stat.seq(-5, 5, 170), br1 = [], br2 = [];
    us.forEach(u => {
      const f0 = Q(u, 0), fp = Q(u, 1), fm = Q(u, -1);
      const a = (fp + fm) / 2 - f0, b = (fp - fm) / 2, c = f0;
      let roots = [];
      if (Math.abs(a) < 1e-10) {
        if (Math.abs(b) > 1e-10) roots = [-c / b, NaN];
      } else {
        const disc = b * b - 4 * a * c;
        if (disc >= 0) {
          const rr = Math.sqrt(disc);
          roots = [(-b - rr) / (2 * a), (-b + rr) / (2 * a)].sort((x, y) => x - y);
        }
      }
      br1.push([u, roots.length ? roots[0] : NaN]);
      br2.push([u, roots.length > 1 ? roots[1] : NaN]);
    });
    w04clip(s, br1, { cls: 'fit', sw: 2.8 }, g);
    w04clip(s, br2, { cls: 'fit', sw: 2.8 }, g);
  } else if (linePts.length) {
    w04clip(s, linePts, { cls: 'fit', sw: 2.8 }, g);
  }
  /* 資料分布固定由輸入的 rho1/rho2 決定；切換模式只改分類規則。 */
  s.poly(w04lda2Ellipse(mu1, r1i), { stroke: HC.tok.a, sw: 2.2, cls: 'ln' }, g);
  s.poly(w04lda2Ellipse(mu2, r2i), { stroke: HC.tok.b, sw: 2.2, cls: 'ln' }, g);
  w04txt(s, s.pad.l + 8, s.pad.t + 14, '藍＝第 1 類（ρ₁）　紅＝第 2 類（ρ₂）　'
    + '灰虛線＝LDA 線性邊界', HC.tok.muted, g);
  const p1 = w04lda2Sample(mu1, r1i, 4041), p2 = w04lda2Sample(mu2, r2i, 4042);
  p1.forEach(p => s.dot(p[0], p[1], { r: 3.4, fill: HC.tok.a, stroke: '#fff', sw: .9 }, g));
  p2.forEach(p => s.dot(p[0], p[1], { r: 3.4, fill: HC.tok.b, stroke: '#fff', sw: .9 }, g));
  /* 顯示點只負責畫圖；錯誤率另用固定且獨立的 4000 個測試點。 */
  const rule = p => {
    if (w04lda2Qda) return Q(p[0], p[1]) > 0 ? 1 : 2;
    return (w1 * p[0] + w2 * p[1] - cc) > 0 ? 1 : 2;
  };
  const t1 = w04lda2Sample(mu1, r1i, 14041, 2000);
  const t2 = w04lda2Sample(mu2, r2i, 14042, 2000);
  let bad = 0;
  t1.forEach(p => { if (rule(p) !== 1) bad++; });
  t2.forEach(p => { if (rule(p) !== 2) bad++; });
  w04tx('w04lda2Mode', w04lda2Qda ? 'QDA（各自 Σ）' : 'LDA（共用 Σ）');
  w04tx('w04lda2R1T', HC.fmt(r1i, 2));
  w04tx('w04lda2R2T', HC.fmt(r2i, 2));
  w04tx('w04lda2Shape', w04lda2Qda
    ? (Math.abs(r1i - r2i) < 1e-9 ? '二次式退化成直線' : '二次曲線') : '直線');
  w04tx('w04lda2Err', bad + ' / 4000（' + HC.pct(bad / 4000, 1) + '）');
  setStatus('w04lda2Status', (w04lda2Qda ? 'QDA' : 'LDA') + ' 模式，ρ₁ = '
    + HC.fmt(r1i, 2) + '、ρ₂ = ' + HC.fmt(r2i, 2) + '，同一批 60 點上的邊界是'
    + (w04lda2Qda && Math.abs(r1i - r2i) > 1e-9 ? '二次曲線（紅）' : '直線')
    + '，灰虛線是 LDA 的線性邊界。獨立 4000 個測試點的錯誤率為 '
    + HC.pct(bad / 4000, 1) + '。');
}
function w04lda2Toggle() { w04lda2Qda = !w04lda2Qda; w04lda2Draw(); }
function w04lda2Reset() {
  w04lda2Qda = false;
  $('w04lda2R1').value = '0.7'; $('w04lda2R2').value = '0.7'; $('w04lda2D').value = '1.4';
  w04lda2Draw();
}

/* ---------- P05 閾值 + 混淆矩陣 + ROC（hybrid）---------- */
const w04thrCum = (() => {
  const F = FRAMES_w04thr, n = F.nbins;
  const cy = new Array(n + 1).fill(0), cn = new Array(n + 1).fill(0);
  for (let k = n - 1; k >= 0; k--) {
    cy[k] = cy[k + 1] + F.histYes[k];
    cn[k] = cn[k + 1] + F.histNo[k];
  }
  return { cy, cn };
})();
const w04thrRocPts = (() => {
  const F = FRAMES_w04thr, out = [];
  for (let k = 0; k <= F.nbins; k++) {
    const tp = w04thrCum.cy[k], fp = w04thrCum.cn[k];
    out.push({ x: fp / F.nNeg, y: tp / F.nPos });
  }
  return out;
})();
function w04thrStats(t) {
  const F = FRAMES_w04thr;
  const k = Math.max(0, Math.min(F.nbins, Math.round(t * F.nbins)));
  const tp = w04thrCum.cy[k], fp = w04thrCum.cn[k];
  const fn = F.nPos - tp, tn = F.nNeg - fp;
  return {
    t: k / F.nbins, tp: tp, fp: fp, fn: fn, tn: tn,
    sens: tp / F.nPos, spec: tn / F.nNeg, fpr: fp / F.nNeg,
    prec: (tp + fp) > 0 ? tp / (tp + fp) : NaN,
    err: (fp + fn) / F.n,
  };
}
function w04thrDrawRoc() {
  HC.line('w04thrRoc', {
    datasets: [
      { label: 'LDA 的 ROC', data: w04thrRocPts, borderColor: HC.tok.accent2,
        borderWidth: 2.4, pointRadius: 0, fill: false },
      { label: '目前門檻值', data: [{ x: 0, y: 0 }], borderColor: HC.tok.accent,
        backgroundColor: HC.tok.accent, pointRadius: 6.5, showLine: false },
      { label: '隨機猜', data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: HC.tok.muted,
        borderWidth: 1.2, borderDash: [5, 4], pointRadius: 0, fill: false },
    ],
  }, {
    interaction: { mode: 'nearest', intersect: true },
    scales: {
      x: { type: 'linear', min: 0, max: 1, title: { display: true, text: '假陽率 FPR = 1 − 特異度' } },
      y: { min: 0, max: 1, title: { display: true, text: '真陽率 TPR = 敏感度' } },
    },
  });
}
function w04thrApply(s) {
  w04tx('w04thrTN', String(s.tn)); w04tx('w04thrFP', String(s.fp));
  w04tx('w04thrFN', String(s.fn)); w04tx('w04thrTP', String(s.tp));
  w04tx('w04thrRN', String(s.tn + s.fn)); w04tx('w04thrRP', String(s.fp + s.tp));
  w04tx('w04thrT', HC.fmt(s.t, 3));
  w04tx('w04thrNP', String(s.fp + s.tp));
  w04tx('w04thrSens', HC.pct(s.sens, 1));
  w04tx('w04thrSpec', HC.pct(s.spec, 1));
  w04tx('w04thrPrec', Number.isNaN(s.prec) ? '—（沒有人被判為違約）' : HC.pct(s.prec, 1));
  w04tx('w04thrErr', HC.pct(s.err, 2));
  HC.update('w04thrRoc', c => { c.data.datasets[1].data = [{ x: s.fpr, y: s.sens }]; });
  setStatus('w04thrStatus', '門檻值 ' + HC.fmt(s.t, 3) + '：預測會違約 ' + (s.fp + s.tp)
    + ' 人，抓到 ' + s.tp + ' / ' + FRAMES_w04thr.nPos + ' 個真違約戶（敏感度 '
    + HC.pct(s.sens, 1) + '），誤報 ' + s.fp + ' 人，總錯誤率 ' + HC.pct(s.err, 2) + '。');
}
function w04thrMove() {
  const t = parseFloat($('w04thrSlider').value);
  w04lab('w04thrSlider', t, 3);
  w04thrApply(w04thrStats(t));
}
function w04thrSet(t) { $('w04thrSlider').value = String(t); w04thrMove(); }
function w04thrReset() { w04thrSet(0.5); }

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.line / HC.update 在 Chart 未載入時本來就安全地回傳 null。 */
w04whySetup();
w04whyDraw();
w04shapeSetup();
w04shapeDraw();
w04lda1Setup();
w04lda1Draw();
w04lda2Setup();
w04lda2Draw();
w04thrApply(w04thrStats(0.5));
HC.ready(() => {
  w04thrDrawRoc();
  w04thrApply(w04thrStats(parseFloat($('w04thrSlider').value)));
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""




def format_static_math(markup):
    """Render legacy Unicode notation as TeX; leave code and live statuses intact."""
    import re

    greek = dict(zip('αβγδεηθλμπρσΣΔ',
                     ('alpha beta gamma delta epsilon eta theta lambda mu pi rho sigma Sigma Delta').split()))
    sub = str.maketrans('₀₁₂₃₄₅₆₇₈₉ₖⱼᵢₗ', '0123456789kjil')
    sup = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹ᵀ⁻¹', '0123456789T-1')
    atom = r'(?:[αβγδεηθλμπρσΣΔ][̂̄]?[₀₁₂₃₄₅₆₇₈₉ₖⱼᵢₗ]*[⁰¹²³⁴⁵⁶⁷⁸⁹ᵀ⁻]*|[pxy][̂̄][₀₁₂₃₄₅₆₇₈₉ₖⱼᵢₗ]*|[xy][ᵀ²])'
    pattern = re.compile(r'e\^(?:'+atom+r'|[-−]?\d+(?:\.\d+)?)|'+atom)

    def tex_atom(t):
        if t.startswith('e^'):
            return 'e^{' + tex_atom(t[2:]) + '}'
        t = t.replace('−', '-')
        if t[0] not in greek and t[0] not in 'pxy':
            return t
        base = '\\' + greek[t[0]] if t[0] in greek else t[0]
        rest = t[1:]
        if rest.startswith('̂'):
            base = r'\hat{' + base + '}'; rest = rest[1:]
        elif rest.startswith('̄'):
            base = r'\bar{' + base + '}'; rest = rest[1:]
        m = re.match(r'[₀₁₂₃₄₅₆₇₈₉ₖⱼᵢₗ]+', rest)
        if m:
            base += '_{' + m[0].translate(sub) + '}'; rest = rest[len(m[0]):]
        if rest:
            base += '^{' + rest.translate(sup) + '}'
        return base

    def text_math(value):
        # Existing TeX stays byte-for-byte intact.
        parts = re.split(r'(\$\$.*?\$\$|\$[^$]*\$)', value, flags=re.S)
        return ''.join(part if part.startswith('$') else pattern.sub(
            lambda m: '$' + tex_atom(m[0]) + '$', part) for part in parts)

    from bs4 import BeautifulSoup, Comment
    soup = BeautifulSoup(markup, 'html.parser',
                         preserve_whitespace_tags={'pre', 'textarea', 'span', 'div'})
    for node in list(soup.find_all(string=True)):
        if isinstance(node, Comment) or node.find_parent(['pre', 'code', 'script', 'style', 'svg']):
            continue
        if node.find_parent(class_=['pseudo-code', 'status-banner']):
            continue
        formatted = text_math(str(node))
        if formatted != str(node):
            node.replace_with(formatted)
    # Flex containers must keep prose and inline math in the same text item.
    # Otherwise each MathJax node becomes a shrinking/distributed flex item.
    for container, separate in [('.quiz-opt', '.opt-letter'), ('.ic-title', '.ic-badge')]:
        for node in soup.select(container):
            prose_nodes = [child for child in list(node.contents)
                           if not (getattr(child, 'name', None) and child in node.select(separate))]
            if not prose_nodes:
                continue
            wrapper = soup.new_tag('span')
            wrapper['style'] = 'min-width:0;flex:1;'
            prose_nodes[0].insert_before(wrapper)
            for child in prose_nodes:
                wrapper.append(child.extract())
    for node in soup.select('[data-fb]'):
        node['data-fb'] = text_math(node['data-fb'])
    return str(soup)


# Approved reading-flow organization; keep all source-backed detail content.
from reading_flow_ch1_6 import organize
BODIES, PAGEJS = organize(4, BODIES, PAGEJS)
BODIES = {key: format_static_math(value) for key, value in BODIES.items()}

if __name__ == "__main__":
    apply("classification", BODIES, PAGEJS, frames())
