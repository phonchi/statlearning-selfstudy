#!/usr/bin/env python3
"""linear_regression.html（ISLP 第 3 章）完整自學充實。冪等。

內容依據：講義 03_Regression.pdf（70 頁）、Ch03-linreg-lab-zh.ipynb、
ISLP 第 3 章（書上 p.70–134）、老師的觀念 FAQ（hackmd.io/@phonchi/regression）。
所有「預期輸出」逐字取自 lab 的實跑結果，圖表與課本各表的數字由
tools/frames/gen_regression.py 產生並在 stderr 逐位對照課本。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import proof, detail
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 3
LAB = "Ch03-linreg-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_regression.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_regression.py 失敗：\n" + r.stderr[-2000:])
    return "/* ===== 烘焙資料（tools/frames/gen_regression.py，固定種子）===== */\n" + r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>桌上只有一張表：200 個市場，每個市場在<strong>電視、廣播、報紙</strong>上各花了多少錢
  （單位：千美元），以及賣掉多少單位的產品（單位：千個）。四欄、200 列，沒有別的。
  ISLP 第 3 章開場就從這張表問出七個問題——而回答它們的工具，
  <strong>全部都是同一個線性模型</strong>。</p>

  <p>這一頁的順序就是這些問題的順序。先把「一個 x 對一個 y」講到底
  （怎麼估、估得準不準、擬合得好不好），再推到「多個 x 一起放進來」，
  最後看這個模型什麼時候會壞掉、什麼時候該換工具。線性迴歸是 1805 年的東西，
  但它幾乎是所有現代方法的骨架：第 6 章在它上面加懲罰項、第 7 章換掉基底函數、
  第 4 章把它套進連結函數。<strong>熟悉這一章的模型與推論方法，有助於理解後續章節</strong>。</p>

{info("開場先記住這四個問題", '''<strong>① 廣告預算跟銷售量有關係嗎？</strong>
  這是「整個模型有沒有用」的問題，靠 <em>F</em> 檢定回答（P04）。<br>
  <strong>② 關係有多強？</strong>靠 RSE 與 R² 回答（P03）。<br>
  <strong>③ 哪些媒體有關？</strong>靠個別係數的 <em>t</em> 檢定與 p 值回答（P02、P04）。<br>
  <strong>④ 每個媒體的條件關聯多大？</strong>靠係數本身與它的信賴區間回答（P02、P04）。<br>
  剩下三個問題——預測有多準、關係真的是線性嗎、媒體之間是否有非加法關聯——
  分別落在 P02（預測區間）、P06（殘差圖）、P05（交互作用）。''')}

  <p>先看答案。下面這一欄「Advertising 上的答案」全部是課本 §3.4 用實際資料算出來的，
  可用來回答這四個問題：</p>

{table(["問題", "用什麼回答", "在哪一節", "Advertising 上的答案"],
       [["① 有關係嗎", "<em>F</em> 檢定", "P04",
         "<em>F</em> = 570.3，p 值接近 0 → <strong>有</strong>"],
        ["② 有多強", "RSE、R²", "P03",
         "RSE = 1.69（sales 平均 14.02，約 12% 誤差）、R² = 0.897"],
        ["③ 哪些媒體", "個別 <em>t</em> 檢定", "P02、P04",
         "TV <em>t</em> = 32.81、radio <em>t</em> = 21.89、newspaper <em>t</em> = −0.18 "
         "→ <strong>只有前兩個</strong>"],
        ["④ 條件關聯多大", "係數與信賴區間", "P02、P04",
         "TV 每千美元約 +46 單位（CI 0.043–0.049）、radio 約 +189（0.172–0.206）、"
         "newspaper 的 CI 是 (−0.013, 0.011)，<strong>含 0</strong>"],
        ["⑤ 預測多準", "信賴區間 vs 預測區間", "P02", "預測區間一定比信賴區間寬"],
        ["⑥ 真的線性嗎", "殘差圖", "P06", "殘差有結構 → <strong>不完全是</strong>"],
        ["⑦ 有非加法關聯嗎", "交互作用項", "P05",
         "加入 TV×radio 後 R² 從 89.7% 跳到 <strong>96.8%</strong>"]])}

{info("報紙廣告：加入其他變數後，係數如何改變", '''單獨看 <code>newspaper</code>，
  它跟 sales 的關聯是顯著的（<em>t</em> = 3.30、p = 0.00115）。
  可是把 TV 與 radio 一起放進模型，它的係數變成 −0.001、<em>t</em> = −0.18，
  完全不顯著。<strong>資料相同，但控制的變數不同，係數與檢定結果也會改變。</strong>
  為什麼？答案在 P04 的 Q&amp;A。這也是老師 FAQ 的第 4 題。''', "warm")}

{quiz("qFour", "QUIZ · 四個問題各配哪個工具",
      "「三種媒體裡，<strong>哪些</strong>跟銷售量有關？」這個問題該看哪個統計量？",
      [(True, "多元迴歸裡<strong>每一個</strong>係數各自的 <em>t</em> 統計量與 p 值",
        "對。個別 t 檢定評估的是控制其他變數後的一個係數。整體 F 檢定可先評估是否有整體證據，但通過 F 不等於每個小 p 值都是可靠發現；同時檢定很多係數仍要處理多重比較。"),
       (False, "整個模型的 <em>F</em> 統計量",
        "不對。<em>F</em> 回答的是「<strong>至少有一個</strong>變數有用嗎」，它給你一個是／否，不會告訴你是哪一個。它提供整體證據，不能替個別變數下結論。"),
       (False, "R²，值愈高就代表愈多媒體有關",
        "不對。R² 是整體擬合程度，跟「有幾個變數有關」沒有對應關係。"
        "在同一份訓練資料上比較含截距的巢狀最小平方模型時，加變數只會讓 R² 上升或不變（P03 會算給你看）。")])}
"""


# ── 講義 p.4–5：模型與 LINE、加權平均、尺度不變（可見段落，raw string 免去 f-string 跳脫） ──
SLR_INTRO = r"""
  <p>先只用一個變數。講義的出發點是一個<strong>模型</strong>：假設 sales 與 TV 預算的關係是一條直線，
  再加上一個誤差項</p>

  $$Y = \beta_0 + \beta_1 X + \varepsilon$$

  <p>$\beta_0$ 是截距、$\beta_1$ 是斜率，兩個都是未知常數，合稱係數或參數；
  $\varepsilon$ 是誤差項，收集所有直線沒解釋到的部分。講義用四個字母交代對 $\varepsilon$ 的假設，
  合稱 <strong>LINE</strong>：</p>

  <ul>
    <li><strong>L（Linearity，線性）</strong>：$E[Y\mid X]=\beta_0+\beta_1X$，Y 的平均值真的落在一條直線上。</li>
    <li><strong>I（Independence，獨立）</strong>：不同觀測的誤差 $\varepsilon_i$ 彼此獨立。</li>
    <li><strong>N（Normality，常態）</strong>：誤差服從常態分布。</li>
    <li><strong>E（Equal variance，等變異）</strong>：每一筆誤差的變異數都是同一個 $\sigma^2$。</li>
  </ul>

  <p>四條合起來就是講義寫的 $\varepsilon_i$ i.i.d. $\sim N(0,\sigma^2)$，等價於
  $Y\mid X\sim N(\beta_0+\beta_1X,\ \sigma^2)$：給定 X 之後，Y 是以直線上那一點為中心、寬度固定的常態分布。
  這四條假設不會一開始全部用到。下表先標出<strong>哪個結果需要哪個假設</strong>，讀到 P02 與 P06 時再回來對照。</p>
""" + table(["要得到的結果", "需要的假設", "在哪一節"],
            [["最小平方解 $\\hat\\beta_0$、$\\hat\\beta_1$", "一條都不需要，純代數", "P01"],
             ["無偏：$E[\\hat\\beta_1]=\\beta_1$", "L，加上 $E[\\varepsilon\\mid X]=0$", "P02"],
             ["標準誤公式 $\\sigma^2/\\sum(x_i-\\bar x)^2$", "I 與 E（誤差不相關、同變異）", "P02"],
             ["t 分布、信賴區間、預測區間", "再加 N；n 大時中央極限定理可放寬", "P02"],
             ["哪一條壞了、怎麼看出來", "殘差圖等診斷工具", "P06"]]) + r"""

  <p>模型寫好了，但 $\beta_0$、$\beta_1$ 不知道。手上有 n 對觀測值
  $(x_1, y_1), \dots, (x_n, y_n)$，要挑一條「最靠近」這些點的線。
  「靠近」有很多種定義，但幾乎所有人都用同一個：<strong>讓殘差平方和最小</strong>。
  第 i 筆的殘差是 $e_i = y_i - \hat y_i$，於是</p>

  $$\mathrm{RSS} = e_1^2 + e_2^2 + \cdots + e_n^2
    = \sum_{i=1}^{n} \left(y_i - \hat\beta_0 - \hat\beta_1 x_i\right)^2$$

  <p>對 $\hat\beta_0$、$\hat\beta_1$ 各偏微分等於零，解出來就是<strong>封閉解</strong>——不需要反覆更新參數、
  不需要調學習率。這一步只用到代數，上面的 LINE 一條都還沒用到；它們要到 P02 問「這個斜率可信嗎」時才登場：</p>

  $$\hat\beta_1 = \frac{\sum_{i=1}^{n}(x_i-\bar x)(y_i-\bar y)}
    {\sum_{i=1}^{n}(x_i-\bar x)^2}, \qquad
    \hat\beta_0 = \bar y - \hat\beta_1 \bar x$$

  <p>第二式順便告訴你一件事：<strong>最小平方線一定通過 $(\bar x, \bar y)$</strong>。</p>

  <h3>斜率是個別資料點斜率的加權平均</h3>
  <p>講義把第一式多寫了一步：把分子的 $(x_i-\bar x)(y_i-\bar y)$ 拆成 $(x_i-\bar x)^2$ 乘上一個比值。</p>

  $$\hat\beta_1
    = \frac{\sum_{i=1}^{n}(x_i-\bar x)^2\,\dfrac{y_i-\bar y}{x_i-\bar x}}
           {\sum_{i=1}^{n}(x_i-\bar x)^2}
    = \sum_{i=1}^{n} w_i\, s_i,\qquad
    w_i=\frac{(x_i-\bar x)^2}{\sum_{j}(x_j-\bar x)^2},\quad
    s_i=\frac{y_i-\bar y}{x_i-\bar x}$$

  <p>$s_i$ 是「從中心點 $(\bar x,\bar y)$ 連到第 i 個資料點」這條線的斜率，每個點各有一條；
  $w_i$ 非負、加總為 1，所以最小平方斜率就是<strong>這 n 條個別斜率的加權平均</strong>。
  權重是 $(x_i-\bar x)^2$ 佔總和的比例：x 離平均越遠的點，權重越大；
  剛好落在 $x_i=\bar x$ 的點權重是 0，它的 $s_i$ 沒有定義也無妨，因為它對斜率完全沒有發言權。
  這解釋了兩件事：為什麼拖動最右邊的點斜率動得特別厲害（下面的元件可以試），
  以及 P06 的槓桿值為什麼長成 $h_i = 1/n + w_i$ 這個樣子。</p>

  <h3>尺度與標準化不改變擬合值</h3>
  <p>講義在同一頁補了一句：<strong>x 的尺度不影響 $\hat y$ 的估計</strong>。
  換單位、減掉平均、除以標準差，這些都是線性重新參數化 $x'=(x-c)/s$；代進公式，斜率與截距跟著換算</p>

  $$\hat\beta_1' = s\,\hat\beta_1,\qquad \hat\beta_0' = \hat\beta_0 + c\,\hat\beta_1,$$

  <p>但每一筆的 $\hat y_i$、殘差、RSS、R²、t 統計量一個都不變（本節結尾的 QUIZ 會再考一次換單位）。
  所以在多元迴歸裡不能拿係數大小比較變數重要性；P05 的收合盒也會談中心化為什麼只改變截距的意義。
  對 y 做線性變換 $y'=ay+b$ 同理，擬合值變成 $\hat y'=a\hat y+b$。</p>
""" + proof('w03proofScale', '線性重新參數化不改變擬合值', r"""
<p>令 $x_i'=(x_i-c)/s$，$s\ne0$。則 $\bar x'=(\bar x-c)/s$、$x_i'-\bar x'=(x_i-\bar x)/s$，代入最小平方解：</p>
$$\hat\beta_1'=\frac{\sum_i (x_i'-\bar x')(y_i-\bar y)}{\sum_i (x_i'-\bar x')^2}
=\frac{\frac1s\sum_i (x_i-\bar x)(y_i-\bar y)}{\frac1{s^2}\sum_i (x_i-\bar x)^2}=s\,\hat\beta_1,\qquad
\hat\beta_0'=\bar y-\hat\beta_1'\bar x'=\bar y-\hat\beta_1(\bar x-c)=\hat\beta_0+c\,\hat\beta_1.$$
<p>於是 $\hat\beta_0'+\hat\beta_1'x_i'=\hat\beta_0+c\hat\beta_1+s\hat\beta_1\cdot\frac{x_i-c}{s}=\hat\beta_0+\hat\beta_1x_i=\hat y_i$。
擬合值逐筆相同，殘差、RSS、TSS、R² 與 RSE 因此相同。
標準誤 $\mathrm{SE}(\hat\beta_1')=\hat\sigma/\sqrt{\sum(x_i'-\bar x')^2}=s\,\mathrm{SE}(\hat\beta_1)$，與係數同比例放大，t 統計量不變。</p>
<p>矩陣版更短：任何可逆的線性重新參數化 $X'=XA$（A 可逆）有相同欄空間，
擬合值 $\hat y=X(X^TX)^{-1}X^Ty$ 只依賴欄空間，故不變；係數換成 $\hat\beta'=A^{-1}\hat\beta$。
對 y 作 $y'=ay+b$ 時，含截距的模型把 b 吸進截距欄，得 $\hat y'=a\hat y+b$。</p>
""") + r"""

  <p>拖動下面元件中的任何一個點，係數、RSS、R² 全部即時重算。
  先預測「把最右邊那個點往上拖，斜率會怎麼變」，再動手驗證。</p>
"""

# ── 講義 p.7–11：抽樣分布、線性組合 → 常態 → t → 區間（收合） ──
NORMAL_DETAIL = detail('w03-detail-normal-ci', '計算細節：斜率估計是 y 的線性組合，所以服從常態', r"""
<p>P01 的 N 假設到這裡才派上用場。若 $\varepsilon_i$ 獨立且服從 $N(0,\sigma^2)$，則每個 $y_i$ 是獨立的常態變數，
而<strong>獨立常態變數的線性組合仍是常態</strong>。所以</p>
$$\hat\beta_1=\sum_i c_i\,y_i\ \sim\ N\!\left(\beta_1,\ \frac{\sigma^2}{S_{xx}}\right),\qquad
\frac{\hat\beta_1-\beta_1}{\sigma/\sqrt{S_{xx}}}\sim N(0,1).$$
<p>這就是 $\hat\beta_1$ 抽樣分布的完整形狀，不只是中心與標準差。母體 σ 不知道，換成殘差算出的 RSE 之後，
分母多了一個獨立的 $\sqrt{\chi^2_{n-2}/(n-2)}$：常態模型下 $\mathrm{RSS}/\sigma^2$ 服從 $\chi^2_{n-2}$ 且與 $\hat\beta$ 獨立
（矩陣版證明見下方「係數共變異數與 CI／PI」），比值變成自由度 n−2 的 t 分布：</p>
$$\frac{\hat\beta_1-\beta_1}{\mathrm{SE}(\hat\beta_1)}\sim t_{n-2},\qquad
\mathrm{SE}(\hat\beta_1)=\frac{\mathrm{RSE}}{\sqrt{S_{xx}}}.$$
<p>信賴區間就是把這句話反過來讀：這個比值有 95% 的機率落在 $\pm t_{0.975,\,n-2}$ 之間，整理成 $\beta_1$ 的範圍，得到</p>
$$\hat\beta_1\pm t_{0.975,\,n-2}\,\mathrm{SE}(\hat\beta_1).$$
<p>n 超過約 30 之後 $t_{0.975,\,n-2}$ 已經接近 1.96，所以講義直接寫成 $\hat\beta_1\pm2\,\mathrm{SE}(\hat\beta_1)$。
t 檢定則是把 $\beta_1=0$ 代進同一個比值：$t=\hat\beta_1/\mathrm{SE}(\hat\beta_1)$ 讀作「$\hat\beta_1$ 離 0 有幾個標準誤」，
$H_0$ 成立時它服從 $t_{n-2}$，所以 |t| 超過 2 左右就落在 5% 的尾巴外。
沒有常態假設時，這個比值在大樣本下仍近似常態（中央極限定理），小樣本則沒有精確的 t 分布。</p>
""")

# ── 講義 p.23–24：CI 與 PI（可見小節＋示意元件） ──
CIPI_SECTION = r"""
  <h3>信賴區間與預測區間：兩個問題、兩種寬度</h3>
  <p>同一個 $x_0$，模型給出同一個點估計 $\hat y_0=\hat\beta_0+\hat\beta_1x_0$，但它可以回答兩個不同的問題：</p>
  <ul>
    <li><strong>信賴區間</strong>（confidence interval, CI）：所有 $X=x_0$ 的個體，<em>平均</em> Y 是多少？
      它只反映我們對母體迴歸線 $f(x_0)=\beta_0+\beta_1x_0$ 估得多準，也就是第二章說的<strong>可縮減誤差</strong>。</li>
    <li><strong>預測區間</strong>（prediction interval, PI）：<em>某一個</em>新的 $X=x_0$ 個體，它的 Y 會落在哪裡？
      就算 $\beta_0$、$\beta_1$ 全知道，這個個體還帶著自己的 $\varepsilon$，也就是<strong>不可縮減誤差</strong>；
      PI 要把兩種誤差一起算進去。</li>
  </ul>
  <p>講義的簡單迴歸公式把差別寫得很清楚，兩式只差根號裡多了一個 1：</p>
  $$\text{CI}:\ \hat y_0\pm t_{\alpha/2,\,n-2}\,\hat\sigma\sqrt{\frac1n+\frac{(x_0-\bar x)^2}{S_{xx}}},\qquad
    \text{PI}:\ \hat y_0\pm t_{\alpha/2,\,n-2}\,\hat\sigma\sqrt{1+\frac1n+\frac{(x_0-\bar x)^2}{S_{xx}}}$$
""" + table(["", "信賴區間（CI）", "預測區間（PI）"],
            [["回答的問題", "$X=x_0$ 時 Y 的<em>平均</em>在哪裡", "<em>一個新個體</em>的 Y 在哪裡"],
             ["包含的不確定性", "只有估計 f 的誤差（可縮減）", "估計 f 的誤差＋個體自己的 ε（不可縮減）"],
             ["寬度", "較窄；在 $\\bar x$ 最窄，往兩側張開", "一定較寬；同樣在 $\\bar x$ 最窄"],
             ["n 變大時", "縮到 0：平均可以估到任意準", "不會縮到 0：最窄也約 $\\pm2\\sigma$"]]) + r"""
  <p>用教材的數字對照。lab 用 Boston 的 <code>medv</code> 對 <code>lstat</code>，
  在 <code>lstat = 10</code> 這一點預測值是 <strong>25.05</strong>，
  CI 是 (24.47, 25.63)，PI 是 (12.83, 37.28)，程式在下方「完整實作」。
  課本的 Advertising 版本：TV 花 100,000 美元、radio 花 20,000 美元時預測銷售 11,256 單位，
  CI 是 [10,985, 11,528]，PI 是 [7,930, 14,580]。兩個區間中心相同，PI 寬了好幾倍，
  因為市場與市場之間的 ε 遠比「平均線估不準」大得多。下面的示意元件讓你調 n 與 σ，
  看兩條帶各自怎麼變：</p>
""" + viz(svg("w03bandSvg", 330)
          + '\n      <div class="viz-legend">'
            '<span><i style="background:rgba(44,62,122,.35);"></i>信賴區間（平均反應）</span>'
            '<span><i style="background:rgba(26,107,74,.18);"></i>預測區間（新觀測）</span>'
            '<span><i class="ln" style="border-top-color:var(--fit-line);"></i>最小平方線</span>'
            '</div>',
          [rows_card("在 x 的平均這一點",
                     [("n", "—", "w03bandNr"), ("RSE（估計的 σ）", "—", "w03bandRse"),
                      ("CI 半寬", "—", "w03bandCi"), ("PI 半寬", "—", "w03bandPi"),
                      ("PI 半寬 ÷ CI 半寬", "—", "w03bandRatio")], "LIVE"),
           info_card("怎麼看這張圖",
                     '深藍帶是 CI、淡綠帶是 PI，兩條都在 $\\bar x$ 最窄、往兩側張開。'
                     '<br>① 把 n 拉大：CI 明顯變窄，PI 幾乎不動，因為個體的 ε 不會因為樣本多而變小；'
                     '<br>② 把 σ 拉大：兩條都變寬，但 PI 寬得多；'
                     '<br>③ 按「重抽一次」：換一份樣本，線與帶都會動，這就是 P02 開頭的抽樣變動。'),
           info_card("對照教材",
                     '講義的兩條公式只差根號裡的 1；課本 Advertising 的 CI [10,985, 11,528] 與 '
                     'PI [7,930, 14,580] 中心同為 11,256。', "講義 03")],
          "w03bandStatus", "推 n 的滑桿：CI 帶會變窄，PI 帶幾乎不變。",
          '<div class="slider-row" style="flex:1 1 220px;margin-bottom:0;">'
          '<span class="slider-label">n</span>'
          '<input type="range" id="w03bandN" min="20" max="200" step="10" value="40" oninput="w03bandRender()">'
          '<span class="slider-val" id="w03bandNv">40</span></div>'
          '<div class="slider-row" style="flex:1 1 220px;margin-bottom:0;">'
          '<span class="slider-label">σ</span>'
          '<input type="range" id="w03bandS" min="5" max="40" step="5" value="25" oninput="w03bandRender()">'
          '<span class="slider-val" id="w03bandSv">2.5</span></div>'
          '<button class="btn btn-step" onclick="w03bandRedraw()">→ 重抽一次</button>'
          '<button class="btn btn-reset" onclick="w03bandReset()">重置</button>',
          provenance=("illustrative", "固定種子示意資料；兩條帶依講義的 CI／PI 公式即時計算"))


# ── 講義附錄：兩張靜態 DAG（中介／混淆） ──
def _dag(mid, nodes, arrows, note):
    """三個節點的小型有向圖；純靜態 SVG，不經 viz()。"""
    out = [f'<svg viewBox="0 0 340 120" width="340" style="max-width:100%;height:auto;display:block;margin:.4rem auto;" '
           f'role="img" aria-label="{note}">'
           f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M0,0 L10,5 L0,10 z" fill="#2c3e7a"/></marker></defs>']
    for (x, y, label) in nodes:
        out.append(f'<rect x="{x-44}" y="{y-16}" width="88" height="32" rx="8" fill="#fffdf7" stroke="#2c3e7a" stroke-width="1.4"/>'
                   f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="13" font-family="JetBrains Mono, monospace" fill="#1a1a2e">{label}</text>')
    for (x1, y1, x2, y2, dashed) in arrows:
        d = ' stroke-dasharray="5,4"' if dashed else ''
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2c3e7a" stroke-width="1.6" marker-end="url(#{mid})"{d}/>')
    out.append('</svg>')
    return ''.join(out)

DAG_MED = _dag('w03dagArrowMed',
               [(60, 60, 'newspaper'), (170, 60, 'radio'), (280, 60, 'sales')],
               [(106, 60, 124, 60, False), (216, 60, 234, 60, False)],
               '中介結構：newspaper 影響 radio，radio 影響 sales')
DAG_CONF = _dag('w03dagArrowConf',
                [(170, 24, '預算／規模'), (60, 96, 'newspaper'), (170, 96, 'radio'), (280, 96, 'sales')],
                [(140, 40, 82, 78, False), (170, 40, 170, 78, False), (216, 96, 234, 96, False)],
                '混淆結構：共同原因同時影響 newspaper 與 radio，只有 radio 影響 sales')

# ── 講義 p.37–52：問題與工具箱（可見段落） ──
P06_INTRO = r"""
  <p>線性迴歸擬合起來很容易，擬合出<strong>錯的</strong>結論也一樣容易。先回頭看 P01 的 LINE：
  哪一條假設失效，壞掉的東西不一樣。</p>
  <ul>
    <li><strong>L 壞掉</strong>：$E[Y\mid X]$ 根本不是直線，係數描述的形狀就是錯的，後面的推論再精準也沒有意義。</li>
    <li><strong>I 壞掉</strong>：誤差彼此相關，資料的有效筆數比 n 少，傳統 SE 通常低估，t、p 值與區間都偏樂觀。</li>
    <li><strong>E 壞掉</strong>：變異隨 x 改變，SE 公式把每一筆都當成同樣可信，SE 與檢定失準；
      只要 $E[\varepsilon\mid X]=0$ 仍成立，係數本身仍無偏。</li>
    <li><strong>N 壞掉</strong>：小樣本的 t 與 F 分布不再精確；n 大時中央極限定理會幫忙。</li>
    <li><strong>$E[\varepsilon\mid X]=0$ 失敗</strong>（例如漏掉重要變數）：係數本身會偏掉，這不是 SE 的問題，也不是換一種 SE 就能修的。</li>
  </ul>
  <p>講義整理了六個最常見的潛在問題，每一個都有對應的<strong>診斷工具</strong>（diagnostic tool）與處理方式；
  講義自己也說，辨認與處理這些問題「既是科學也是藝術」。先看全表，再逐一動手看：</p>
""" + table(["#", "問題", "診斷工具（標準名稱）", "為什麼這個工具看得到它", "講義的處理方式"],
            [["1", "<strong>非線性</strong>（non-linearity）",
              "殘差圖（residual plot）：$e_i$ 對 $\\hat y_i$",
              "直線假設正確時殘差沒有結構；殘差隨 $\\hat y$ 彎成 U 形，就是模型漏了曲率",
              "加入 $x^2$ 等多項式項"],
             ["2", "<strong>誤差相關</strong>（correlated errors）",
              "殘差對觀測順序圖（residuals vs time／order plot）",
              "時間或空間相鄰的觀測若誤差相關，相鄰殘差會同號、成串漂移",
              "指出後果：SE 低估、區間太窄；有時間結構的資料要換模型"],
             ["3", "<strong>異質變異</strong>（heteroscedasticity）",
              "同一張殘差圖看漏斗形",
              "變異隨反應水準放大時，殘差的散布隨橫軸張開",
              "對 Y 取 $\\log$ 或開根號"],
             ["4", "<strong>離群值</strong>（outlier，y 怪）",
              "學生化殘差圖（studentized residual plot）",
              "原始殘差各筆尺度不同，除以自己的 SE 後才能用同一把尺比；$|r_i|>3$ 可疑",
              "確認是記錄錯誤才刪；否則可能是模型缺變數"],
             ["5", "<strong>高槓桿</strong>（high leverage，x 怪）",
              "槓桿統計量（leverage statistic）$h_i$、Cook's distance、影響圖（influence plot）",
              "$h_i$ 是第 i 筆的 y 對自己擬合值的權重；遠超過平均 $(p+1)/n$ 的點能扳動整條線",
              "檢查該筆資料是否有效；那一區資料太少時補資料"],
             ["6", "<strong>共線性</strong>（collinearity）",
              "相關矩陣（correlation matrix）、變異數膨脹因子（VIF）",
              "兩個變數幾乎重複時，RSS 沿一條溝幾乎不變，係數各自估不準，SE 膨脹 $\\sqrt{\\mathrm{VIF}}$",
              "拿掉一個，或合成一個變數"]], fontsize=".82rem")

P06_AXES = r"""
  <h3>診斷圖的橫軸為什麼是 ŷ，不是觀測編號或 y</h3>
  <p>殘差圖（residual plot）是後面幾乎每一個工具的底圖，先把它的橫軸講清楚。
  殘差 $e_i=y_i-\hat y_i$ 放縱軸沒有爭議，橫軸有三種候選：</p>
  <ul>
    <li><strong>觀測編號 i</strong>：只在順序本身有意義時才是資訊。時間序列的編號就是時間，
      殘差對它畫能看出相鄰殘差同號，這正是第 2 個問題的工具。但 Advertising 的 200 個市場排序是任意的，
      把資料列洗牌一次，圖就整個變樣；一張換個排序就改變結論的圖，不能拿來當診斷。</li>
    <li><strong>擬合值 $\hat y_i$</strong>：它是模型對<em>所有</em>預測變數的一維摘要
      $\hat\beta_0+\sum_j\hat\beta_jx_{ij}$，而且按「模型認為的訊號大小」排序。
      簡單迴歸時它只是 x 的線性變換，殘差對 $\hat y$ 就是殘差對 x；多元迴歸時 p 個變數畫不進一個橫軸，
      $\hat y$ 把它們壓成一條。更重要的是，含截距的最小平方保證 $\sum_i e_i=0$ 與 $\sum_i e_i\hat y_i=0$，
      也就是殘差與擬合值<strong>正交</strong>：殘差對 $\hat y$ 的最小平方直線斜率恰好是 0，
      圖上絕不會出現假的線性趨勢；看到 U 形或漏斗，就是模型真的漏了東西。</li>
    <li><strong>觀測值 $y_i$</strong>：它含有殘差本身（$y_i=\hat y_i+e_i$），所以 $\mathrm{Cov}(e,y)=\mathrm{Var}(e)$ 恆為正。
      殘差對 y 的相關係數恰好是 $\sqrt{1-R^2}$，最小平方斜率是 $1-R^2$；R² 越低這條假趨勢越陡，
      會讓人誤以為模型誤設。</li>
  </ul>
  <p>結論：整體形狀（非線性、漏斗）看殘差對 $\hat y$；要知道<em>是哪一個</em>變數需要非線性項，
  改看殘差對單一 $x_j$，或 P04 收合盒裡的部分迴歸圖；懷疑誤差相關時才看殘差對時間。
  下面用同一組示意資料把三種橫軸擺在一起，按「洗牌觀測順序」看哪一張會變：</p>
""" + viz(svg("w03axisSvg", 320),
          [rows_card("這一張圖的數字",
                     [("橫軸", "擬合值 ŷ", "w03axisModeV"),
                      ("corr(e, 橫軸)", "—", "w03axisCorr"),
                      ("殘差對橫軸的最小平方斜率", "—", "w03axisSlope"),
                      ("理論值", "0", "w03axisPred"),
                      ("這組資料的 R²", "—", "w03axisR2")], "LIVE"),
           info_card("怎麼看",
                     '同一組殘差（縱軸）、三種橫軸。'
                     '<br>① <strong>ŷ</strong>：紅線斜率恰為 0，形狀是真的；'
                     '<br>② <strong>y</strong>：紅線一定往右上，斜率 ≈ 1−R²，相關 ≈ √(1−R²)，這是假象；'
                     '<br>③ <strong>編號</strong>：按「洗牌觀測順序」，只有這張會變，'
                     '因為橫斷面資料的編號沒有資訊。'),
           info_card("對應講義",
                     '講義的殘差圖橫軸是 $\\hat y_i$、縱軸是 $e_i=y_i-\\hat y_i$，多元迴歸也一樣；'
                     '要看時間相依才改用觀測順序當橫軸。', "講義 03")],
          "w03axisStatus", "橫軸是 ŷ：殘差與擬合值正交，紅線斜率恰為 0。切換橫軸比較看看。",
          '<button class="btn btn-toggle" onclick="w03axisSet(\'fit\')">橫軸：擬合值 ŷ</button>'
          '<button class="btn btn-toggle" onclick="w03axisSet(\'y\')">橫軸：觀測值 y</button>'
          '<button class="btn btn-toggle" onclick="w03axisSet(\'idx\')">橫軸：觀測編號</button>'
          '<button class="btn btn-step" onclick="w03axisShuffleOrder()">→ 洗牌觀測順序</button>'
          '<button class="btn btn-reset" onclick="w03axisReset()">重置</button>',
          provenance=("illustrative", "固定種子示意資料；三種橫軸由同一組殘差即時繪製")) + proof('w03proofResidualAxes', '殘差與觀測值的共用成分', r"""
<p>在 $\operatorname{Cov}(\varepsilon\mid X)=\sigma^2I$ 下，$e=(I-H)\varepsilon$、$\hat y=X\beta+H\varepsilon$，故</p>
$$\operatorname{Cov}(e,\hat y\mid X)=\sigma^2(I-H)H=0,\qquad
\operatorname{Cov}(e,y\mid X)=\sigma^2(I-H).$$
<p>單筆的共變異數因此為 $\sigma^2(1-h_{ii})$，通常為正；即使線性平均模型正確，也不應期待 e 與原始 y 無關。
樣本層次更直接：由 normal equations，$\sum_i e_i=0$、$\sum_i e_i\hat y_i=0$，所以 e 對 $\hat y$ 的樣本共變異數為零；
而 $\sum_i e_i y_i=\sum_i e_i(\hat y_i+e_i)=\mathrm{RSS}$，故 e 對 y 的樣本相關係數為
$\mathrm{RSS}/\sqrt{\mathrm{RSS}\cdot\mathrm{TSS}}=\sqrt{1-R^2}$，最小平方斜率為 $\mathrm{RSS}/\mathrm{TSS}=1-R^2$。</p>
""") + r"""
  <p class="source-note">講義補充連結：<a href="https://stats.stackexchange.com/questions/71352/why-are-residual-plots-constructed-using-the-residuals-vs-the-predicted-values" target="_blank" rel="noopener">為什麼殘差圖用擬合值當橫軸</a>、
  <a href="https://stats.stackexchange.com/questions/5235/what-is-the-expected-correlation-between-residual-and-the-dependent-variable" target="_blank" rel="noopener">殘差與反應變數的相關係數</a>。</p>
"""

P06_TOOLS_A = r"""
  <h3>殘差圖（residual plot）：非線性與異質變異</h3>
  <p>橫軸 $\hat y_i$、縱軸 $e_i$，理想狀況是一團沒有結構的雲。講義用 Auto 資料示範：mpg 對 horsepower 的殘差彎成明顯的 U 形，
  這是<strong>非線性</strong>的強烈證據；加入 horsepower² 之後 U 形消失，殘差幾乎沒有形狀，表示二次項確實改善了模型
  （上方元件的第 ② 組就是這份資料）。同一張圖也看<strong>異質變異</strong>：殘差的散布隨 $\hat y$ 張開成漏斗形，
  表示誤差的變異隨反應水準放大。講義的處理方式是對反應變數做壓縮尺度的變換，例如 $\log Y$ 或 $\sqrt{Y}$，
  大值被壓得比小值多，漏斗就收攏了。</p>

  <h3>殘差對觀測順序圖（residuals vs time／order plot）：誤差相關</h3>
  <p>LINE 的 I 假設說誤差互不相關：知道 $\varepsilon_i$ 是正的，對 $\varepsilon_{i+1}$ 的正負沒有任何提示。
  時間序列資料最容易違反，相鄰時間點的誤差往往同號。診斷方式是把殘差依時間（或收集順序）畫出來：
  誤差不相關時看不到任何模式；相關越強，相鄰殘差越傾向取相近的值，圖上就出現一段一段的漂移。</p>
  <p>後果講義用一個極端例子說明：把資料不小心複製一份，n 變成 2n，最小平方解完全不變，但 SE 公式以為多了一倍的資訊，
  信賴區間會縮成原來的 $1/\sqrt2$，這當然是假的。一般而言誤差正相關時，估計出的 SE 會<strong>低估</strong>真正的 SE，
  信賴區間與預測區間都比應有的窄，p 值偏小。這種資料要換用能描述時間相依的模型，超出本章範圍。</p>
  <p class="source-note">講義補充連結：<a href="https://math.stackexchange.com/questions/2957686/explain-about-the-correlation-of-error-terms-in-linear-regression-models" target="_blank" rel="noopener">誤差相關對線性迴歸的影響</a>。</p>

  <h3>學生化殘差圖（studentized residual plot）：離群值</h3>
  <p>離群值是 y 離模型預測很遠的點。要判斷「多遠算遠」，不能直接比原始殘差，因為每一筆殘差的尺度不一樣。
  <strong>學生化殘差</strong>（studentized residual）是把殘差除以它自己的估計標準差：</p>

  $$r_i = \frac{e_i}{\mathrm{RSE}\sqrt{1-h_i}}$$

  <p>為什麼要除以 $\sqrt{1-h_i}$？因為 $\mathrm{Var}(e_i) = \sigma^2(1-h_i)$，高槓桿點的殘差天生就小，
  直接比原始殘差對它不公平。學生化之後才有共同尺度，講義的判準是 $|r_i|>3$ 的觀測是可能的<strong>離群值</strong>（outlier）。
  把 $r_i$ 對 $\hat y_i$ 畫出來就是學生化殘差圖，上方元件的第 ④ 組可以看到那一個點。</p>
  <p>離群值對最小平方線的影響通常有限（它的 x 不怪、槓桿低），但會推高 RSE：課本的例子裡，
  含那一點時 RSE 是 1.09，拿掉後只有 0.77。RSE 是所有 SE、區間與 p 值的原料，一個點就能改變整份推論的解讀。
  處理方式：確認是資料收集或記錄錯誤才刪除；否則它可能在提醒模型缺了一個變數。</p>
  <p class="source-note">講義補充連結：<a href="https://en.wikipedia.org/wiki/Studentized_residual" target="_blank" rel="noopener">Studentized residual</a>。</p>

  <h3>槓桿統計量（leverage statistic）、Cook's distance 與影響圖（influence plot）：高槓桿與影響點</h3>
  <p><strong>槓桿值</strong> $h_i$ 是帽子矩陣的對角元，衡量「第 i 筆的 x 有多不尋常」。簡單線性迴歸有明確公式：</p>

  $$h_i = \frac{1}{n} + \frac{(x_i-\bar x)^2}{\sum_{j=1}^{n}(x_j-\bar x)^2}$$

  <p>回想 P01：$h_i=1/n+w_i$，第二項正是第 i 筆在「斜率是加權平均」裡的權重。更一般地 $\hat y_i=\sum_j h_{ij}y_j$，
  所以 $h_i$ 就是第 i 筆自己的 y 對自己擬合值的權重，介於 1/n 與 1 之間，而且<strong>所有 $h_i$ 的平均恰好是 $(p+1)/n$</strong>。
  遠超過這個平均（實務上常用 2 倍或 3 倍當門檻值）的點就是<strong>高槓桿點</strong>（high leverage point）：
  它的 x 不尋常，一個點就能扳動整條線。</p>
  <p>高槓桿不等於有影響。講義區分兩個詞：拿掉之後迴歸式明顯改變的觀測叫<strong>影響點</strong>（influential observation）；
  影響點通常槓桿高，但高槓桿點若剛好落在趨勢上，反而幫忙把 x 的範圍拉開、降低 $\mathrm{SE}(\hat\beta_1)$。
  要同時看「x 怪不怪」與「y 怪不怪」，講義用 <strong>Cook's distance</strong>：</p>

  $$D_i=\frac{\sum_{j=1}^{n}\left(\hat y_j-\hat y_{j(-i)}\right)^2}{(p+1)\,\hat\sigma^2}
       =\frac{r_i^2}{p+1}\cdot\frac{h_i}{1-h_i}$$

  <p>$\hat y_{j(-i)}$ 是拿掉第 i 筆後重新擬合、對第 j 筆的預測值；左式問「少了這一筆，全部的擬合值一共動了多少」，
  右式說這個量正好是學生化殘差平方乘上槓桿比 $h_i/(1-h_i)$。把 $h_i$ 放橫軸、$r_i$ 放縱軸、氣泡大小畫 $D_i$，
  就是<strong>影響圖</strong>（influence plot），也就是上方元件的「殘差對槓桿圖」（residuals vs leverage plot）：
  右上與右下角的點最危險。講義給的處理方式有兩個：這些點特別值得回頭檢查資料是否有效；
  它們也標出設計空間裡資料太少的區域，能補資料就補。</p>
"""

P06_TOOLS_B = r"""
  <p class="source-note">講義補充連結：<a href="https://en.wikipedia.org/wiki/Leverage_(statistics)" target="_blank" rel="noopener">Leverage (statistics)</a>、
  <a href="https://stats.stackexchange.com/questions/65912/precise-meaning-of-and-comparison-between-influential-point-high-leverage-point" target="_blank" rel="noopener">影響點與高槓桿點的差別</a>。</p>

  <h3>相關矩陣（correlation matrix）與變異數膨脹因子（VIF）：共線性</h3>
  <p>第六個問題自己一節。<strong>共線性</strong>（collinearity）是指兩個以上的預測變數彼此高度相關。
  它不會讓估計有偏，但會讓 RSS 的等高線<strong>從碗變成一條狹長的溝</strong>——
  沿著溝走，RSS 幾乎不變，於是「哪一組係數最好」變得極難分辨，係數的 SE 跟著膨脹、檢定力下降。
  最直接的檢查是看預測變數的<strong>相關矩陣</strong>：某一對相關係數很高就要留意。
  但講義提醒這不夠：三個以上的變數可能整體高度共線（multicollinearity），而任何一對的相關都不特別高。
  更好的工具是<strong>變異數膨脹因子</strong>：</p>
"""

P06_EXTRA = detail('w03-detail-extra-diagnostics', '延伸閱讀：講義之外的診斷與補救', r"""
<p>以下工具不在講義的教學範圍，lab 的 <code>results.summary()</code> 輸出或課本會提到，列出名稱與用途供查閱。</p>
<ul style="padding-left:1.4rem;">
  <li><strong>常態分位圖</strong>（normal Q-Q plot）：學生化殘差的分位數對標準常態分位數作圖，貼著 45 度線表示殘差接近常態，
    兩端翹起表示厚尾或離群值。lab 摘要表下方的 Omnibus 與 Jarque-Bera 是對應的常態性檢定。上方元件的「Q-Q 圖」按鈕就是這張。</li>
  <li><strong>尺度–位置圖</strong>（scale-location plot）：$\sqrt{|r_i|}$ 對 $\hat y_i$ 作圖，專門看變異是否隨擬合值上升；
    漏斗形在殘差圖上不明顯時，這張圖會放大它。上方元件的「scale-location」按鈕就是這張。</li>
  <li><strong>Durbin–Watson 統計量</strong>：檢查相鄰殘差的一階自相關，理想值接近 2，明顯小於 2 表示正相關。
    lab 的 Boston 模型給出 0.892，殘差有明顯的順序相依。</li>
  <li><strong>加權最小平方</strong>（weighted least squares）：課本對異質變異的另一個處理，知道各筆變異的比例時，
    把每筆觀測乘上權重 $1/\sigma_i$ 再做最小平方。</li>
  <li><strong>穩健標準誤</strong>（heteroscedasticity-consistent standard errors）：係數不變，只把 SE 的估計換成不依賴等變異假設的版本。</li>
</ul>
""")

# ── P01 slr ───────────────────────────────────────────────────────────
BODIES["slr"] = f"""
{SLR_INTRO}
{viz(svg("w03dragSvg", 350)
     + '\n      <div class="viz-legend">'
       '<span><i style="background:var(--pt-train);"></i>可拖動的觀測值</span>'
       '<span><i class="ln" style="border-top-color:var(--fit-line);"></i>最小平方線</span>'
       '<span><i class="ln" style="border-top-color:var(--resid);"></i>殘差（要平方後相加）</span>'
       '<span><i class="ln" style="border-top-color:var(--fit-true);"></i>展開 RSS 計算細節可調整的試探線</span>'
       '</div>',
     [rows_card("即時最小平方解",
                [("$\\hat\\beta_0$（截距）", "—", "w03dragB0"), ("$\\hat\\beta_1$（斜率）", "—", "w03dragB1"),
                 ("RSS", "—", "w03dragRss"), ("RSE", "—", "w03dragRse"),
                 ("R²", "—", "w03dragR2"), ("$\\mathrm{{SE}}(\\hat\\beta_1)$", "—", "w03dragSe1"),
                 ("$t=\\hat\\beta_1/\\mathrm{{SE}}(\\hat\\beta_1)$", "—", "w03dragT1")], "LIVE"),
      info_card("怎麼玩",
                '用滑鼠或手指<strong>直接把點拖走</strong>。三件事值得試：'
                '<br>① 把某一點往上下拖 → 看 RSS 怎麼跳；'
                '<br>② 把<strong>最右邊</strong>那點上下拖 → 斜率動得比拖中間的點厲害得多：'
                '它離 $\\bar x$ 最遠、權重 $w_i$ 最大，這也是 P06「高槓桿點」的預告；'
                '<br>③ 把所有點排成一條線 → RSS 趨近 0、R² 趨近 1。'),
      info_card("對照課本",
                'ISLP 圖 3.1 是同一件事的 Advertising 版本：'
                'sales 對 TV 的最小平方線是 $\\hat\\beta_0 = 7.03$、$\\hat\\beta_1 = 0.0475$。'
                '斜率的意思是「TV 預算多花 1000 美元，平均多賣約 47.5 單位」。', "ISLP 圖 3.1")],
     "w03dragStatus", "拖動任何一個藍點，係數與 RSS 會即時重算。灰紫色虛線是殘差。",
     '<button class="btn btn-reset" onclick="w03dragReset()">重置</button>'
     '<button class="btn btn-step" onclick="w03dragNewData()">→ 換一組資料</button>'
     '<button class="btn btn-toggle" id="w03dragResBtn" onclick="w03dragToggleRes()">隱藏殘差線段</button>',
     provenance=("illustrative", "固定種子模擬；最小平方量由目前資料即時計算"))}

  <p>接著把同一件事換個角度看。上面那張圖的橫軸是 x、縱軸是 y；
  下面這張圖的<strong>兩個軸都是參數</strong>：橫軸 β₀、縱軸 β₁，
  每一個點代表「一組候選的係數」，等高線代表「這組係數的 RSS 有多大」。
  這就是老師 FAQ 裡問的<strong>誤差曲面</strong>（error surface）：</p>

  $$\\mathrm{{RSS}}(\\beta_0, \\beta_1) = \\mathrm{{RSS}}_{{\\min}}
    + n(\\beta_0-\\hat\\beta_0)^2
    + 2\\left(\\textstyle\\sum_i x_i\\right)(\\beta_0-\\hat\\beta_0)(\\beta_1-\\hat\\beta_1)
    + \\left(\\textstyle\\sum_i x_i^2\\right)(\\beta_1-\\hat\\beta_1)^2$$

  <p>這條式子精確描述 RSS，推導只用到最小平方解的兩個性質
  $\\sum e_i = 0$ 與 $\\sum e_i x_i = 0$。它是 β 的<strong>二次式</strong>，
  當 x 不全相同時，誤差曲面是一個碗、等高線是同心橢圓、最小點唯一。
  下面的等高線就是照這條式子畫的，<strong>而且會跟著上面那張圖的點一起變</strong>。</p>

{viz(svg("w03rssSvg", 330),
     [rows_card("目前的參數點",
                [("β₀", "—", "w03rssB0"), ("β₁", "—", "w03rssB1"),
                 ("RSS", "—", "w03rssVal"), ("RSS / RSS 最小值", "—", "w03rssRatio"),
                 ("最小點 $(\\hat\\beta_0, \\hat\\beta_1)$", "—", "w03rssMin")], "LIVE"),
      info_card("怎麼看這張圖",
                '紅點是最小平方解（碗底），橢圓上的標籤是 RSS 相對於最小值的倍數。'
                '推滑桿讓橘點離開碗底，<strong>看它跨過幾條等高線</strong>，'
                '同時上面那張圖會出現一條綠色虛線，那就是這組係數畫出來的線。'
                '橢圓是<strong>斜的</strong>：β₀ 猜大一點時 β₁ 要猜小一點才補得回來，'
                '這就是 $\\hat\\beta_0$ 與 $\\hat\\beta_1$ 負相關的意思。'),
      info_card("課本的版本",
                'ISLP 圖 3.2 用 Advertising 的 sales~TV 畫同一張圖：'
                '最小點在 $\\hat\\beta_0 = 7.0326$、$\\hat\\beta_1 = 0.0475$，RSS 最小值 = 2102.53。'
                '課本畫的等高線標了 2.11、2.15、2.2、2.3、2.5、3（單位是千），'
                '對應的就是這裡的倍數。', "ISLP 圖 3.2")],
     "w03rssStatus", "橘點在碗底時 RSS 最小。推滑桿讓它離開，看 RSS 上升多少倍。",
     '<div class="slider-row" style="flex:1 1 240px;margin-bottom:0;">'
     '<span class="slider-label">β₀ 偏移</span>'
     '<input type="range" id="w03rssU" min="-100" max="100" value="0" oninput="w03rssMove()">'
     '<span class="slider-val" id="w03rssUv">0.00</span></div>'
     '<div class="slider-row" style="flex:1 1 240px;margin-bottom:0;">'
     '<span class="slider-label">β₁ 偏移</span>'
     '<input type="range" id="w03rssV" min="-100" max="100" value="0" oninput="w03rssMove()">'
     '<span class="slider-val" id="w03rssVv">0.00</span></div>'
     '<button class="btn btn-reset" onclick="w03rssHome()">回到最小點</button>',
     provenance=("illustrative", "由上方同一份模擬資料的精確 RSS 二次式繪製"))}

{qa("觀念釐清", [
    ("Q：誤差曲面（error surface）到底是什麼？為什麼線性迴歸不用梯度下降？",
     "<p>把損失函數看成<strong>參數</strong>的函數，畫出來就是誤差曲面。"
     "座標軸是參數 β₀ 與 β₁，曲面的高度是這組參數在資料 x 與 y 上得到的 RSS。"
     "等高線上的每一點 RSS 相同，最佳化就是從某個起點往下走到最低點。</p>"
     "<p>線性迴歸的 RSS 是 β 的<strong>凸二次函數</strong>。上面那條精確式子就是證據，"
     "所以它只有一個最低點，而且對 β 微分等於零後是一組<strong>線性</strong>方程"
     "（正規方程 $X^\\top X\\beta = X^\\top y$）。既然線性方程有封閉解 "
     "$\\hat\\beta = (X^\\top X)^{-1}X^\\top y$，就沒有必要用梯度下降一步一步爬。</p>"
     "<p>那什麼時候才需要反覆更新參數？① 損失函數不是二次式（邏輯斯迴歸、SVM、神經網路）；"
     "② n 或 p 太大，$X^\\top X$ 這個 $p \\times p$ 矩陣算不動或存不下；"
     "③ 加了不可微的懲罰項（lasso，第 6 章）。這時候才輪到梯度下降、"
     "牛頓法、座標下降上場。</p>"),
    ("Q：迴歸裡的 X 到底是隨機變數還是常數？",
     "<p>看情境，而且兩種寫法的結論幾乎一樣。</p>"
     "<p><strong>實驗設計</strong>裡 x 是我們自己設定的（施肥 0、5、10 公斤），"
     "把它當常數很自然，模型寫成 $Y \\sim N(\\beta_0+\\beta_1 X,\\ \\sigma^2)$。"
     "<strong>觀察性研究</strong>裡 x 是跟著樣本一起抽到的（某個市場剛好花了 230.1 千美元），"
     "它本來就是隨機的，這時模型要寫成條件分佈 "
     "$Y \\mid X \\sim N(\\beta_0+\\beta_1 X,\\ \\sigma^2)$。</p>"
     "<p>為什麼結論一樣？因為我們關心的一直是<strong>條件期望</strong> $E[Y \\mid X]$——"
     "在均方誤差下它就是最好的預測。所有的推論（SE、t、F）都是「固定住觀測到的那組 x」"
     "之後做的，也就是條件在 X 上。所以課本裡 SE 的公式長得跟「x 是常數」一樣，"
     "這些式子都以觀測到的 x 為條件；在隨機設計中，x 本身仍是隨機的。</p>"
     "<p>差別會在哪裡冒出來？當你想推廣到「新的 x 分佈」時。"
     "訓練資料的 x 集中在 0–300，硬要拿去預測 x = 1000 的市場，"
     "模型沒有任何資訊支撐。這叫外推（extrapolation），跟 x 是不是隨機無關，"
     "但正是因為 x 有它自己的分佈，這件事才需要被提醒。</p>"),
])}

  <h3 id="dx-slr">講義完整實作：建立並擬合 OLS 模型</h3>
{card("講義 03 · 手動建模型矩陣 → sm.OLS → summarize",
      lab_code(CH, 22) + "\n\n" + lab_code(CH, 24) + "\n\n" + lab_code(CH, 26),
      lab_output(CH, 26), src=src("22、24、26"),
      note="lab 用 <code>Boston</code> 的 <code>medv</code>（房價中位數）對 "
           "<code>lstat</code>（低社經地位家庭百分比）示範。注意兩件事："
           "<strong>① <code>sm.OLS()</code> 不會自己加截距</strong>，"
           "所以要手動放一欄全是 1 的 <code>intercept</code>；"
           "② <code>sm.OLS()</code> 只是<em>指定</em>模型，真正擬合的是 "
           "<code>.fit()</code>。斜率 −0.95 的意思是「lstat 每高 1 個百分點，"
           "medv 平均低 0.95 千美元」。")}

{""}

{quiz("qOls", "QUIZ · 最小平方法",
      "把資料裡<strong>某一個</strong>點沿著<em>垂直</em>方向往上移動，最小平方線一定會怎麼變？",
      [(True, "整條線會往那個點的方向轉／移，而且那個點離 $\\bar x$ 愈遠、影響愈大",
        "對。RSS 對每一筆的貢獻是殘差<strong>平方</strong>，所以離線遠的點權重特別重；而 $\\hat\\beta_1$ 是個別斜率的加權平均，權重 $w_i\\propto(x_i-\\bar x)^2$，離 $\\bar x$ 愈遠的點對斜率的影響愈大。上面拖著玩就看得到。"),
       (False, "只有截距會變，斜率不變",
        "只有一種特例成立：那個點剛好在 $x=\\bar x$ 上，它的權重 $w_i$ 是 0。一般情況下 $\\hat\\beta_1$ 的分子 $\\sum(x_i-\\bar x)(y_i-\\bar y)$ 會跟著 $y_i$ 變，斜率也會動。"),
       (False, "線不會變，因為最小平方法對單一個點不敏感",
        "剛好相反。最小平方法對單一個點<strong>非常</strong>敏感，正因為它罰的是殘差平方而不是絕對值。這是 P06 要討論離群值與高槓桿點的理由。")])}
"""

# ── P02 inference ─────────────────────────────────────────────────────
BODIES["inference"] = f"""
  <p>$\\hat\\beta_1 = 0.0475$ 這個數字，可信嗎？先弄清楚在問什麼。P01 的模型說真實世界裡有一條看不到的
  <strong>母體迴歸線</strong>（population regression line）</p>

  $$Y = \\beta_0 + \\beta_1 X + \\varepsilon$$

  <p class="core-backfill">標準誤與區間還不熟時，可先複習
  <a href="s4_inference.html#standard_error">S4 的標準誤</a>與
  <a href="s4_inference.html#intervals">信賴區間</a>。</p>

  <p>我們只有一份樣本，用它算出來的是<strong>最小平方線</strong>；換一份樣本，就會得到另一條。
  把「換樣本」這件事想成可以重複做很多次：每一次都得到一個 $\\hat\\beta_1$，這些值排成的分布叫做
  <strong>抽樣分布</strong>（sampling distribution）。估計量是樣本的函數，樣本會變，估計量就有自己的分布；
  下面元件右邊的直方圖畫的就是它。抽樣分布回答兩個問題：中心在哪裡（有沒有偏）、散得多開（估得準不準）。</p>

  <p>中心先講。$\\hat\\beta_1$ 可以整理成 y 的<strong>線性組合</strong>：</p>

  $$\\hat\\beta_1=\\sum_{{i=1}}^{{n}}c_i\\,y_i,\\qquad
    c_i=\\frac{{x_i-\\bar x}}{{S_{{xx}}}},\\quad S_{{xx}}=\\sum_{{j=1}}^{{n}}(x_j-\\bar x)^2$$

  <p>係數 $c_i$ 只跟 x 有關，而且 $\\sum_i c_i=0$、$\\sum_i c_ix_i=1$。
  把 $y_i=\\beta_0+\\beta_1x_i+\\varepsilon_i$ 代進去，$\\beta_0$ 那一項被 $\\sum c_i=0$ 消掉、
  $\\beta_1$ 那一項被 $\\sum c_ix_i=1$ 留下，得到 $\\hat\\beta_1=\\beta_1+\\sum_i c_i\\varepsilon_i$。
  在 LINE 的線性假設加上 $E[\\varepsilon\\mid X]=0$ 下，最小平方估計<strong>無偏</strong>：
  抽樣分布的中心就在 $\\beta_1$。不過單獨一條線仍可能偏離母體迴歸線不少，而我們手上就只有一條。</p>

  <p>散得多開？這就是<strong>標準誤</strong>（standard error）要量的東西，也就是抽樣分布的標準差。
  由 $\\hat\\beta_1-\\beta_1=\\sum_i c_i\\varepsilon_i$，用 I 與 E（誤差不相關、同變異 $\\sigma^2$）算變異數，
  $\\mathrm{{Var}}(\\hat\\beta_1)=\\sigma^2\\sum_i c_i^2=\\sigma^2/S_{{xx}}$：</p>

  $$\\mathrm{{SE}}(\\hat\\beta_1)^2 = \\frac{{\\sigma^2}}{{\\sum_{{i=1}}^{{n}}(x_i-\\bar x)^2}},
    \\qquad
    \\mathrm{{SE}}(\\hat\\beta_0)^2 = \\sigma^2\\left[\\frac{{1}}{{n}}
    + \\frac{{\\bar x^2}}{{\\sum_{{i=1}}^{{n}}(x_i-\\bar x)^2}}\\right]$$

  <p>第一條式子把「什麼會讓斜率估得準」講完了：
  <strong>雜訊 σ² 小、樣本多、x 散得開</strong>。σ² 通常不知道，
  就用殘差算出的 RSE² 估計（下一節會定義 RSE）。下面的示意圖讓你觀察重複抽樣時，估計出的迴歸線如何改變，
  右邊的直方圖就是 $\\hat\\beta_1$ 的抽樣分布：</p>

{viz(svg("w03sampSvg", 320)
     + "\n" + chart("w03sampChart", "",
                    "。此圖是 β̂₁ 的抽樣分布：重複抽樣時斜率估計值的散布，"
                    "標準誤就是它的標準差。"),
     ["",
      rows_card("抽樣示意", [("已畫出的迴歸線", "0", "w03sampCount")], "示意"),
      info_card("為什麼要看這張圖",
                '<strong>SE 描述重複抽樣時，估計出的係數會散開多少。</strong>'
                '你手上只有一條線，永遠不知道它偏了多少；但公式可以告訴你'
                '「換一份訓練資料，估計會如何變動」。'
                '每條線代表一次重新抽樣後的估計；下圖把這些斜率排成直方圖，就是抽樣分布，'
                '它的中心在母體斜率、寬度由 SE 決定。', "ISLP 圖 3.3 右")],
     "w03sampStatus", "按「抽一次」觀察估計的變動，或多次抽樣查看斜率分布。",
     '<button class="btn btn-step" onclick="w03sampOne()">→ 抽一次</button>'
     '<button class="btn btn-play" onclick="w03sampMany()">▶ 多次抽樣</button>'
     '<button class="btn btn-reset" onclick="w03sampReset()">重置</button>',
     provenance=("illustrative", "固定種子重複抽樣；對照 ISLP 圖 3.3"))}

{NORMAL_DETAIL}

  <p>有了 SE，兩個標準工具就出來了。<strong>95% 信賴區間</strong>：</p>

  $$\\hat\\beta_1 \\pm t_{{0.975,\\,n-2}} \\cdot \\mathrm{{SE}}(\\hat\\beta_1)
    \\;\\approx\\; \\hat\\beta_1 \\pm 2\\,\\mathrm{{SE}}(\\hat\\beta_1)$$

  <p>以及<strong>假設檢定</strong>。虛無假設 $H_0: \\beta_1 = 0$（X 與 Y 沒有關係）對上
  $H_a: \\beta_1 \\neq 0$，檢定統計量是</p>

  $$t = \\frac{{\\hat\\beta_1 - 0}}{{\\mathrm{{SE}}(\\hat\\beta_1)}}$$

  <p>它衡量「$\\hat\\beta_1$ 離 0 有幾個標準誤」。$H_0$ 成立時 t 服從自由度 n − 2 的 t 分佈（為什麼是 t 分布，見上方收合的「線性組合」推導），
  n 大於約 30 之後跟標準常態幾乎一樣，所以 <strong>|t| 超過大約 2 就對應 5% 的顯著水準</strong>。
  p 值是「假設 $H_0$ 為真，看到這麼極端或更極端的 t 的機率」。
  注意它<strong>不是</strong>「$H_0$ 為真的機率」。</p>

{table(["Advertising 的三個單變數迴歸", "係數", "SE", "<em>t</em>", "p 值", "出處"],
       [["sales ~ TV 的截距", "7.0326", "0.4578", "15.36", "&lt; 0.0001", "表 3.1"],
        ["sales ~ TV 的 <code>TV</code>", "0.0475", "0.0027", "17.67", "&lt; 0.0001", "表 3.1"],
        ["sales ~ radio 的 <code>radio</code>", "0.2025", "0.0204", "9.92", "&lt; 0.0001", "表 3.3 上"],
        ["sales ~ newspaper 的 <code>newspaper</code>", "0.0547", "0.0166", "3.30", "0.00115",
         "表 3.3 下"]])}
  <p style="font-size:.82rem;color:var(--muted);">三個單獨看都顯著——<strong>包含 newspaper</strong>。
  P04 會比較這一列在多元迴歸中的變化。課本的 β₀ 信賴區間是 [6.130, 7.935]、
  β₁ 是 [0.042, 0.053]：「完全不打廣告時，銷售量平均落在 6130 到 7935 單位之間」。</p>


{CIPI_SECTION}

  <h3 id="dx-inf">講義完整實作：完整摘要與兩種區間</h3>
{card("講義 03 · print(results.summary())：一次看完 SE、t、p、信賴區間、F、R²",
      lab_code(CH, 35), None, src=src("35"), fontsize=".72rem",
      note="這一張表整理了整個模型的估計與檢定結果。左上是模型資訊，右上有 <code>R-squared 0.544</code>、"
           "<code>F-statistic 601.6</code>、<code>Prob (F-statistic) 5.08e-88</code>；"
           "中間那塊每一列是一個係數的 <code>coef</code>／<code>std err</code>／"
           "<code>t</code>／<code>P&gt;|t|</code>／95% 信賴區間 "
           "<code>[0.025 0.975]</code>。<code>lstat</code> 的區間是 "
           "[−1.026, −0.874]，離 0 很遠。下面那塊 <code>Omnibus</code>、"
           "<code>Jarque-Bera</code> 是常態性檢定，<code>Durbin-Watson 0.892</code> "
           "是殘差自相關的指標（理想值 2，這裡明顯偏低——P06 第 2 個問題）。")}

{card("講義 03 · 信賴區間 vs 預測區間",
      lab_code(CH, 39) + "\n\n" + lab_code(CH, 41) + "\n\n" + lab_code(CH, 43)
      + "\n\n" + lab_code(CH, 45),
      lab_output(CH, 45), src=src("39、41、43、45"),
      note="在 <code>lstat = 10</code> 這一點，預測值都是 <strong>25.05</strong>，但："
           "<strong>信賴區間</strong> (24.47, 25.63) 問的是「所有 lstat = 10 的社區，"
           "<em>平均</em> medv 是多少」；<strong>預測區間</strong> (12.83, 37.28) 問的是"
           "「<em>某一個</em> lstat = 10 的社區，medv 是多少」。"
           "後者寬得多，因為它還要算進個別觀測值自己的隨機誤差 ε。"
           "<code>conf_int(obs=True)</code> 就是切換這兩者的開關。")}

{quiz("qSe", "QUIZ · 標準誤",
      "同一份資料，你把預測變數 x 的單位從「元」換成「千元」（也就是全部除以 1000）。"
      "$\\hat\\beta_1$ 與它的 <em>t</em> 統計量會怎麼變？",
      [(True, "$\\hat\\beta_1$ 變成 1000 倍，$\\mathrm{{SE}}(\\hat\\beta_1)$ 也變成 1000 倍，<em>t</em> 完全不變",
        "對。單位換算只是把 x 乘上一個常數，擬合值、殘差、RSS 一個都沒動，所以 R² 與 RSE 也不變（P01 的「尺度不改變擬合值」）。$\\hat\\beta_1$ 與 $\\mathrm{{SE}}(\\hat\\beta_1)$ 同比例放大，比值 t 就被消掉了——<strong>顯著性不會因為換單位而改變</strong>，這也是為什麼不能靠「係數大小」判斷變數重不重要。"),
       (False, "$\\hat\\beta_1$ 變成 1000 倍，SE 不變，所以 <em>t</em> 也變成 1000 倍",
        "不對。$\\mathrm{{SE}}(\\hat\\beta_1)^2=\\sigma^2/\\sum(x_i-\\bar x)^2$，分母裡的 x 也跟著縮小 1000 倍，所以 $\\sum(x_i-\\bar x)^2$ 縮小 $10^6$ 倍、SE 放大 1000 倍。SE 不可能不動。"),
       (False, "兩個都不變，因為線性迴歸對單位免疫",
        "只有<strong>無單位</strong>的量（t、p、R²）免疫。有單位的量（$\\hat\\beta_1$、SE、信賴區間的端點）一定會跟著單位變。它們的單位是「y 的單位 ÷ x 的單位」。")])}
"""

# ── P03 accuracy ──────────────────────────────────────────────────────
BODIES["accuracy"] = f"""
  <p>檢定過關（「有關係」）之後，下一個問題是「擬合得<strong>多好</strong>」。
  兩個常用的量，一個有單位、一個沒有。</p>

  <p><strong>殘差標準誤</strong>（residual standard error）估的是誤差標準差 σ，
  單位跟 y 一樣：</p>

  $$\\mathrm{{RSE}} = \\sqrt{{\\frac{{\\mathrm{{RSS}}}}{{n-p-1}}}}
    \\qquad(\\text{{簡單線性迴歸的 }} p = 1,\\ \\text{{分母是 }} n-2)$$

  <p>Advertising 用三個媒體的模型 RSE = 1.69，而 sales 的平均是 14.02——
  相對誤差大約 12%。這個「12%」用銷售量的尺度呈現誤差大小。</p>

  <p><strong>R²</strong> 把它換成無單位的比例。先定義總平方和
  $\\mathrm{{TSS}} = \\sum(y_i - \\bar y)^2$（完全不看 x、只用 $\\bar y$ 猜的誤差），則</p>

  $$R^2 = \\frac{{\\mathrm{{TSS}} - \\mathrm{{RSS}}}}{{\\mathrm{{TSS}}}}
        = 1 - \\frac{{\\mathrm{{RSS}}}}{{\\mathrm{{TSS}}}}$$

  <p>讀作「y 的變異有多少比例被模型解釋掉了」。簡單線性迴歸時還有一個關係：
  <strong>$R^2$ 恰好等於 x 與 y 相關係數的平方</strong>（這是 ISLP 3.7 第 7 題）。
  多元迴歸時它等於 $\\mathrm{{Cor}}(Y, \\hat Y)^2$。</p>

{table(["Advertising 上的模型", "RSS", "自由度 n−p−1", "RSE", "R²"],
       [["只用 <code>TV</code>", "2102.53", "198", "3.259", "0.6119"],
        ["<code>TV</code> + <code>radio</code>", "556.91", "197", "1.681", "0.8972"],
        ["三個媒體都放", "556.83", "196", "1.686", "0.8972"],
        ["只用 <code>radio</code>", "3618.48", "198", "4.275", "0.3320"],
        ["只用 <code>newspaper</code>", "5134.80", "198", "5.093", "0.0521"],
        ["什麼都不放（只有截距）", "5417.15", "199", "5.218", "0.0000"]])}

{info("比較這張表的第 2 列與第 3 列", '''加入 <code>newspaper</code> 之後：
  <strong>RSS 從 556.91 只掉到 556.83</strong>（幾乎沒動，但它<em>一定</em>會掉，
  這是數學上的必然）；<strong>R² 完全沒變</strong>（0.8972 → 0.8972）；
  可是 <strong>RSE 反而從 1.681 上升到 1.686</strong>。<br>
  為什麼？因為 RSE 的分母是 n − p − 1：分子幾乎不動，分母卻從 197 掉到 196。
  <strong>「多加一個沒用的變數要付代價」這件事，R² 看不到，RSE 看得到。</strong>
  第 6 章的 Cp、AIC、BIC、調整後 R² 全都是在把這個代價算得更精細。''', "warm")}

  <p>所以請記住這個性質：<strong>在同一訓練集上比較含截距的巢狀最小平方模型時，
  R² 不會因為加變數而下降</strong>，
  因此它<strong>不能</strong>用來比較變數個數不同的模型。要比，就要用會罰複雜度的指標，
  或者乾脆用第 5 章的交叉驗證去估測試誤差。</p>

{qa("觀念釐清", [
    ("Q：R² 有可能是負的嗎？",
     "<p>用<strong>含截距的最小平方法擬合在同一份資料上</strong>時，不可能。"
     "因為「只用 $\\bar y$ 猜」本身就是這個模型的一個特例（$\\hat\\beta_1 = 0$），"
     "而最小平方法挑的是 RSS 最小的那組，所以一定 RSS ≤ TSS，於是 $R^2 \\ge 0$。</p>"
     "<p>但下面三種情況它真的會變成負的：</p><ul>"
     "<li><strong>模型沒有截距項</strong>：這時 $\\hat\\beta_1 = 0$ 不再是可選的方案，"
     "擬合出來的線可能比水平線 $\\bar y$ 還差。順帶一提，這也是為什麼 "
     "<code>sm.OLS()</code> 不自動加截距是個容易忽略的地方。</li>"
     "<li><strong>在測試資料上算 R²</strong>：$1 - \\mathrm{RSS}_{\\text{test}}/"
     "\\mathrm{TSS}_{\\text{test}}$ 完全可以是負的，意思是"
     "「你的模型在這批測試資料上，比直接猜這批測試反應值的平均還差」。"
     "<code>sklearn</code> 的 <code>.score()</code> 就是這樣算的，"
     "看到負值不要以為程式壞了。</li>"
     "<li><strong>係數不是用最小平方擬合的</strong>（ridge、lasso、手動指定、"
     "別人給的模型）：沒有「RSS 已被最小化」這個保證。</li></ul>"
     "<p>看到負的 R²，正確的反應是：這個模型比「什麼都不學」還糟，回頭檢查有沒有截距、"
     "有沒有算錯資料集、或者根本選錯了模型。</p>"),
])}
{""}

{quiz("qR2", "QUIZ · R² 與 RSE",
      "你在模型裡加了一個<strong>完全隨機、跟 y 無關</strong>的變數。訓練資料上會發生什麼？",
      [(True, "R² 一定上升（或不變），RSE 通常上升",
        "對。RSS 只會下降（最壞就是係數擬合到 0），所以 R² = 1 − RSS/TSS 只會上升。但 RSE 的分母 n−p−1 少了 1，分子幾乎不動，所以 RSE 通常反而變差。這正是 Advertising 加入 newspaper 的情況。"),
       (False, "R² 與 RSE 都會變差，因為變數沒有用",
        "R² 那半錯了。「沒有用」是<em>母體</em>層次的話；在<em>這一份</em>樣本上，最小平方法一定能靠它多刮掉一點 RSS（哪怕只是擬合到雜訊），所以訓練 R² 一定上升。"),
       (False, "兩個都不變，因為最小平方法會自動把它的係數設成 0",
        "不對。最小平方法沒有這種機制，它會給出一個剛好最貼合這份樣本雜訊的非零係數。「把沒用的係數壓成 0」要等到第 6 章的 lasso。")])}
"""

# ── P04 mlr ───────────────────────────────────────────────────────────
BODIES["mlr"] = f"""
  <p>三個媒體要不要各擬合一條簡單迴歸，然後把結論拼起來？<strong>不行。</strong>
  三條線各自忽略了另外兩個變數，而且沒辦法拿一組預算去預測銷售量。
  正確的做法是讓每個變數都有自己的斜率：</p>

  $$Y = \\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\cdots + \\beta_p X_p + \\varepsilon$$

  <p>多元迴歸的係數應這樣解讀：<strong>控制模型中的其他變數後，Xⱼ 增加一單位時，
  Y 的條件平均相差 βⱼ</strong>。這是模型中的條件關聯或預測差；
  沒有因果研究設計與額外假設時，不能解讀成介入 Xⱼ 所造成的效果。同樣用最小平方法最小化</p>

  $$\\mathrm{{RSS}} = \\sum_{{i=1}}^{{n}}
    \\left(y_i - \\hat\\beta_0 - \\hat\\beta_1 x_{{i1}} - \\cdots
    - \\hat\\beta_p x_{{ip}}\\right)^2$$

  <p>寫成矩陣就是一行。這也是本頁標題那條式子：</p>

  $$\\hat\\beta = (X^\\top X)^{{-1}} X^\\top y$$

  <p>接著是第一個問題：<strong>「至少有一個變數有用嗎」</strong>。
  虛無假設是 $H_0: \\beta_1 = \\beta_2 = \\cdots = \\beta_p = 0$，用 <em>F</em> 檢定：</p>

  $$F = \\frac{{(\\mathrm{{TSS}} - \\mathrm{{RSS}})/p}}{{\\mathrm{{RSS}}/(n-p-1)}}$$

  <p>$H_0$ 為真時分子與分母的期望值都是 σ²，所以 <strong><em>F</em> 應該在 1 附近</strong>；
  $H_a$ 為真時分子會變大，<em>F</em> 就明顯大於 1。多大才算大？取決於 n 與 p，
  交給軟體算 p 值。下表列出講義與課本的完整係數表，包含各變數的 t 值。</p>

{table(["三個媒體都放進去（ISLP 表 3.4／3.6）", "係數", "SE", "<em>t</em>", "p 值", "95% CI"],
       [["截距", "2.9389", "0.3119", "9.42", "&lt; 0.0001", "(2.324, 3.554)"],
        ["<code>TV</code>", "0.0458", "0.0014", "32.81", "&lt; 0.0001", "(0.043, 0.049)"],
        ["<code>radio</code>", "0.1885", "0.0086", "21.89", "&lt; 0.0001", "(0.172, 0.206)"],
        ["<code>newspaper</code>", "−0.0010", "0.0059", "−0.18", "0.8599",
         "(−0.013, 0.011) <strong>含 0</strong>"]])}
  <p style="font-size:.82rem;color:var(--muted);">整體 <em>F</em> = 570.3、R² = 0.8972、
  RSE = 1.686。VIF 分別是 1.005、1.145、1.145，所以 newspaper 不顯著<strong>不是</strong>
  共線性把 SE 撐大造成的（對照 P06 的 Credit 例子就知道差別）——
  是它的資訊真的被 radio 蓋掉了。</p>

{qa("觀念釐清", [
    ("Q：為什麼 newspaper 在單變數迴歸顯著，在多變數迴歸就不顯著了？",
     "<p>因為兩個迴歸問的是<strong>不同的問題</strong>。</p>"
     "<p>單變數迴歸的係數回答：「只看 newspaper 這一欄，它跟 sales 有沒有線性關聯？」"
     "多變數迴歸的係數回答：「<strong>在 TV 與 radio 都已知的情況下</strong>，"
     "再多知道 newspaper 有沒有幫助？」第二個問題嚴格得多。</p>"
     "<p>機制就在相關矩陣裡：corr(radio, newspaper) = 0.354，報紙預算高的市場，廣播預算通常也高。"
     "一個說得通的故事是<strong>中介</strong>（mediation）：行銷部門先決定報紙預算，廣播預算跟著報紙預算走，"
     "而真正帶動銷售的是廣播。</p>" + DAG_MED +
     "<p>在這個結構裡，newspaper 對 sales 沒有<em>直接</em>效果，但透過 radio 有<em>間接</em>效果。"
     "單變數迴歸看到的是總效果（間接那條路還開著），所以顯著；把 radio 放進模型等於把那條路堵住，"
     "剩下的直接效果是 0，係數就掉到 0 附近。注意這裡的「newspaper 沒用」只是「控制 radio 之後沒有額外貢獻」，"
     "它的總效果並不是 0：若減少報紙預算，廣播預算也會跟著減少，銷售照樣受影響。</p>"
     "<p>另一個同樣說得通的故事是<strong>混淆</strong>（confounding）：有一個共同原因，例如市場規模或整體行銷預算，"
     "同時推高廣播與報紙的花費，而只有廣播帶動銷售。</p>" + DAG_CONF +
     "<p>這時 newspaper 與 sales 的關聯完全是假象：它們只是共用一個上游原因。混淆變數是那個共同原因，不是 radio；"
     "radio 只是剛好坐在那條後門路徑上，所以控制它也能把假關聯關掉。</p>"
     "<p><strong>迴歸分不出這兩個故事。</strong>兩種結構都會產生「單變數顯著、加入 radio 後歸零」的同一組係數表；"
     "newspaper 是否真的影響銷售，要靠研究設計（例如隨機分配預算）或額外的因果假設才能回答。"
     "這正是講義結尾提醒的：觀察資料上應避免因果宣稱。同一個結構也可能反過來："
     "$X_j$ 單獨看不顯著、控制別的變數後才顯著（被壓抑效應蓋住）。"
     "所以「單變數篩選再進多變數模型」是個危險的習慣。</p>"
     "<p class=\"source-note\">講義補充連結：<a href=\"https://www.causeweb.org/cause/resources/fun/cartoons/ice-cream-sales-and-shark-sightings\" target=\"_blank\" rel=\"noopener\">冰淇淋銷量與鯊魚出沒</a>的漫畫是「相關不等於因果」的經典例子。</p>"
     "<p>另一個常見但<strong>不同</strong>的成因是共線性："
     "$X_j$ 真的有用，只是它跟別的變數太像，SE 被膨脹到檢不出來"
     "（P06 的 Credit <code>limit</code>／<code>rating</code>）。"
     "分辨方法：看 VIF。這裡 newspaper 的 VIF 只有 1.145，"
     "不能把不顯著歸因於高共線性；但低 VIF 也不能分辨上面的中介與混淆結構。</p>"),
    ("Q：有了 t 檢定，為什麼還要 F 檢定？",
     "<p>因為<strong>多重比較</strong>。單一個 t 檢定在 α = 0.05 下有 5% 的機率誤判；"
     "但如果你有 100 個變數、逐一做 t 檢定，即使它們全部無用，"
     "預期也會冒出 100 × 0.05 = <strong>5 個「顯著」</strong>。"
     "看到 5 個顯著就宣布發現，等於在報告雜訊。</p>"
     "<p><em>F</em> 檢定一次檢定<strong>全體</strong>："
     "$H_0$ 是所有係數同時為 0。它的分佈已經把 p 個變數的維度算進去了，"
     "在模型假設成立、顯著水準為 0.05 時，整體 F 的第一型錯誤率仍是 5%，而不是 0。</p>"
     "<p>可以先看 F 了解整體證據，再研究個別係數，但<strong>先通過 F 不等於完成個別檢定的多重比較校正</strong>。"
     "若同時探索許多變數，仍須處理假發現問題；事前指定的一個係數檢定，則與探索後挑最小 p 值不同。</p>"
     "<p>還有一個 t 做不到的用途：<em>F</em> 可以檢定<strong>一組</strong>係數"
     "（$H_0: \\beta_{p-q+1} = \\cdots = \\beta_p = 0$）。"
     "質性變數的多個虛擬欄就是這種情況——個別虛擬欄的 t 值會隨基準水準的選擇而變，"
     "「這個變數整體有沒有用」的 F 檢定則保持相同（P05 會看到）。"
     "巢狀模型的比較（<code>anova_lm()</code>）也是同一件事。</p>"
     "<p>最後一個常被忽略的細節：<strong>p ≥ n 時 F 檢定根本算不出來</strong>，"
     "因為全模型無法按一般滿欄秩、正殘差自由度的設定估計誤差變異。可接著看<a href='model_selection.html#highdim'>線性模型選擇的高維度一節</a>。</p>"),
])}

  <h3 id="dx-mlr">講義完整實作：從兩個變數到全部變數</h3>
{card("講義 03 · 兩個預測變數（lstat + age）", lab_code(CH, 74), lab_output(CH, 74),
      src=src("74"),
      note="<code>age</code> 的 <em>t</em> = 2.826、p = 0.005，在這個模型裡是顯著的。"
           "先記住這個數字，看下一張卡。")}

{card("講義 03 · 全部 12 個預測變數", lab_code(CH, 77), None, src=src("75、77"),
      note="同一個 <code>age</code>，<em>t</em> 從 2.826 掉到 <strong>0.271</strong>、"
           "p 從 0.005 變成 0.787。這就是上面 Q&amp;A 講的現象在 lab 裡的實例，"
           "跟 Advertising 的 newspaper 是同一種問題。"
           "<code>indus</code>（p = 0.829）也是。lab 的刪除 age 範例接著示範怎麼用 "
           "<code>Boston.columns.drop(['medv','age'])</code> 把 <code>age</code> 拿掉重新擬合，"
           "拿掉之後 <code>lstat</code> 的 <em>t</em> 從 −10.897 變成 −11.483，"
           "SE 從 0.051 縮到 0.048——變數少一個，剩下的反而估得更準。")}

{""}

"""

# ── P05 qualitative ───────────────────────────────────────────────────
BODIES["qualitative"] = f"""
  <p>前面所有的 x 都是數字。可是「貨架位置：好／中／差」、「是不是學生」、
  「哪一個地區」怎麼放進模型？可以用虛擬變數表示：<strong>編成 0 與 1</strong>。</p>

  <p>兩個水準只要一欄。以 Credit 資料的 <code>Student</code> 為例：</p>

  $$x_i = \\begin{{cases}} 1 & \\text{{第 }} i \\text{{ 個人是學生}} \\\\
    0 & \\text{{不是學生}} \\end{{cases}}
    \\qquad\\Longrightarrow\\qquad
    y_i = \\begin{{cases}} \\beta_0 + \\beta_1 + \\varepsilon_i & \\text{{是學生}} \\\\
    \\beta_0 + \\varepsilon_i & \\text{{不是}} \\end{{cases}}$$

  <p>於是 β₀ 是「非學生的平均」、β₁ 是「學生比非學生多出來的部分」。
  <strong>k 個水準只要 k − 1 欄</strong>；沒有分到欄的那個水準叫<strong>基準水準</strong>
  （baseline），截距代表它。為什麼不給每個水準都一欄？
  因為 k 欄加起來恆等於 1，會跟截距完全共線，矩陣就不可逆了。
  這叫虛擬變數陷阱（dummy variable trap）。</p>

{table(["Credit 上的兩個例子", "係數", "SE", "<em>t</em>", "p 值", "解讀"],
       [["截距（非學生）", "480.369", "23.434", "20.499", "&lt; 0.0001",
         "非學生的平均 balance"],
        ["<code>Student[Yes]</code>", "396.456", "74.104", "5.350", "&lt; 0.0001",
         "學生平均多 396 → 876.83"],
        ["截距（African American）", "531.00", "46.319", "11.464", "&lt; 0.0001",
         "基準水準的平均"],
        ["<code>Ethnicity[Asian]</code>", "−18.686", "65.021", "−0.287", "0.774",
         "比基準少 18.7，但 p 很大"],
        ["<code>Ethnicity[Caucasian]</code>", "−12.503", "56.681", "−0.221", "0.826",
         "比基準少 12.5，p 也很大"]])}
  <p style="font-size:.82rem;color:var(--muted);">下面三列就是 ISLP 表 3.8（課本用的欄名是
  <code>region</code>／East／South／West，ISLP 的 Python 資料集把同一欄命名為
  <code>Ethnicity</code>，數字完全一致）。三個水準的整體檢定
  <em>F</em> = 0.0434、p = <strong>0.9575</strong>——「族群跟 balance 無關」。
  重點是：<strong>個別虛擬欄的係數與 p 值會隨基準水準的選擇而變，整體的 F 檢定不會。</strong>
  所以判斷一個質性變數整體有沒有用，要看 F，不要看個別虛擬欄。</p>

  <p>接著是<strong>交互作用</strong>。標準線性模型是<em>加法</em>的：
  每個變數的條件斜率跟其他變數的值無關。可是「電視廣告與銷售的關聯會不會取決於廣播花了多少」
  這種問題（行銷上叫綜效、統計上叫交互作用）就違反加法假設。解法是丟一個乘積項進去：</p>

  $$Y = \\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\beta_3 X_1X_2 + \\varepsilon
    = \\beta_0 + (\\beta_1 + \\beta_3 X_2)\\,X_1 + \\beta_2 X_2 + \\varepsilon$$

  <p>看第二種寫法：<strong>$X_1$ 的斜率變成 $\\beta_1 + \\beta_3X_2$，
  會隨 $X_2$ 移動</strong>。當 $X_2$ 是質性變數（0／1）時這個關係很容易從圖上看出——
  就是「兩條線平不平行」：</p>

{viz(svg("w03interSvg", 340)
     + '\n      <div class="viz-legend">'
       '<span><i style="background:var(--pt-a);"></i>非學生</span>'
       '<span><i style="background:var(--pt-b);"></i>學生</span>'
       '<span><i class="ln" style="border-top-color:var(--pt-a);"></i>非學生的迴歸線</span>'
       '<span><i class="ln" style="border-top-color:var(--pt-b);"></i>學生的迴歸線</span>'
       '</div>',
     [rows_card("兩條線",
                [("模式", "—", "w03interMode"),
                 ("非學生的斜率 β₁", "—", "w03interS0"),
                 ("學生的斜率 β₁+β₃", "—", "w03interS1"),
                 ("交互作用項 β₃", "—", "w03interB3r"),
                 ("RSS", "—", "w03interRss"), ("R²", "—", "w03interR2")], "LIVE"),
      info_card("怎麼玩",
                '先按「切換」看<strong>沒有</strong>交互作用的版本：兩條線'
                '<strong>平行</strong>，只有截距不同，意思是「收入與 balance 的條件斜率，'
                '學生跟非學生完全一樣」。切到有交互作用之後推 β₃ 滑桿，'
                '看學生那條線怎麼轉。滑桿放在最小平方解上時 RSS 最小；'
                '往兩邊推，RSS 就爬起來。'),
      info_card("課本的數字",
                'ISLP 圖 3.7 就是這兩張圖。最小平方解：'
                '無交互作用時兩條線的共同斜率是 <strong>5.98</strong>；'
                '有交互作用時非學生 <strong>6.22</strong>、學生 '
                '<strong>4.22</strong>（$\\hat\\beta_3 = -2.00$）。'
                '也就是說學生組的 income–balance 條件斜率較小。'
                '不過這一項的 <em>t</em> = −1.15、p = 0.25，並不顯著。', "ISLP 圖 3.7")],
     "w03interStatus", "兩條線平行＝沒有交互作用。切換後推滑桿，看學生那條線轉起來。",
     '<button class="btn btn-toggle" id="w03interBtn" onclick="w03interToggle()">切換：加入交互作用</button>'
     '<div class="slider-row" style="flex:1 1 240px;margin-bottom:0;">'
     '<span class="slider-label">β₃</span>'
     '<input type="range" id="w03interB3" min="-800" max="400" value="-200" oninput="w03interDraw()">'
     '<span class="slider-val" id="w03interB3v">−2.00</span></div>'
     '<button class="btn btn-reset" onclick="w03interHome()">回到最小平方解</button>',
     provenance=("course-data", "ISLP Credit；對照課本圖 3.7"))}

{table(["Advertising 加入 TV×radio（ISLP 表 3.9）", "係數", "SE", "<em>t</em>", "p 值"],
       [["截距", "6.7502", "0.2479", "27.23", "&lt; 0.0001"],
        ["<code>TV</code>", "0.0191", "0.0015", "12.70", "&lt; 0.0001"],
        ["<code>radio</code>", "0.0289", "0.0089", "3.24", "0.0014"],
        ["<code>TV×radio</code>", "0.0011", "0.0001", "20.73", "&lt; 0.0001"]])}
  <p style="font-size:.82rem;color:var(--muted);">R² 從 89.7%（只有主效果）跳到
  <strong>96.8%</strong>。換個方式算更有感：加法模型擬合完後<em>剩下</em>的變異裡，
  有 (96.8 − 89.7)/(100 − 89.7) ≈ <strong>69%</strong> 被這一個乘積項解釋掉了。
  係數的解讀是「TV 預算每多 1000 美元，銷售量增加 (19 + 1.1 × radio) 單位」——
  <strong>廣播預算愈高，模型中的電視廣告斜率愈大</strong>。這是樣本中的交互作用，
  單憑觀察資料不能判定為因果綜效。</p>

{info("階層原則（hierarchical principle）", '''只要模型放了交互作用項
  <code>X₁X₂</code>，就要<strong>連主效果 <code>X₁</code> 與 <code>X₂</code> 一起放</strong>，
  即使它們的 p 值不顯著。<br>
  兩個理由：① 如果 X₁X₂ 跟 y 有關，那 X₁ 的係數是不是剛好為 0 根本不重要；
  ② 乘積項通常跟主效果高度相關，抽掉主效果會讓乘積項<strong>被迫去承擔主效果</strong>，
  它的係數就不再是「交互作用」的意思了。<br>
  同一個原則也適用於多項式：放了 <code>x²</code> 就要放 <code>x</code>。''')}

  <h3 id="dx-qual">講義完整實作：交互作用與類別變數</h3>
{card("講義 03 · 用 tuple 指定交互作用項", lab_code(CH, 93), lab_output(CH, 93), src=src("93"),
      note="<code>MS(['lstat', 'age', ('lstat', 'age')])</code> 裡的 tuple "
           "<code>('lstat','age')</code> 就是交互作用項，欄名會自動變成 "
           "<code>lstat:age</code>。它的 <em>t</em> = 2.244、p = 0.025，顯著；"
           "而 <code>age</code> 的主效果 <em>t</em> = −0.036 完全不顯著——"
           "<strong>照階層原則，還是要留著它</strong>。")}

{card("講義 03 · 三個水準的類別變數（Carseats 的 ShelveLoc）",
      lab_code(CH, 105), None, src=src("103、105"), fontsize=".74rem",
      note="<code>ShelveLoc</code> 有 <code>Bad</code>／<code>Medium</code>／"
           "<code>Good</code> 三個水準，<code>MS()</code> 自動產生兩欄 "
           "<code>ShelveLoc[Good]</code> 與 <code>ShelveLoc[Medium]</code>——"
           "<code>Bad</code> 被丟掉當基準（它是第一個水準）。"
           "係數 4.85 與 1.95 都是「相對於 Bad」的差距，"
           "順序也符合直覺：好位置 &gt; 中等 &gt; 差位置。"
           "這一格同時放了兩個交互作用 <code>Income:Advertising</code>（p = 0.007，顯著）"
           "與 <code>Price:Age</code>（p = 0.424，不顯著）。")}

{quiz("qInt", "QUIZ · 質性變數與交互作用",
      "一個三水準的質性變數，你把基準水準從「差」換成「好」。什麼會變、什麼不會變？",
      [(True, "個別虛擬欄的係數、SE、p 值都會變；擬合值、預測、R²、整體 F 檢定都不變",
        "對。換基準只是換一組座標來表達同一個模型——模型張出來的空間一模一樣，所以擬合值與所有整體指標不變。這正是為什麼「這個質性變數整體有沒有用」要看 F 而不是看某一欄的 p 值。"),
       (False, "什麼都不會變，因為虛擬變數的編碼方式不影響模型",
        "<strong>擬合</strong>不受影響；<strong>係數的意義</strong>則隨比較對象改變：它們是「相對於基準」的差距，換了基準就是換了比較對象，數字當然不同。"),
       (False, "係數不變，但 R² 會變，因為模型矩陣不同了",
        "兩個模型矩陣張出同一個線性空間，所以擬合值與 R² 完全相同；換基準會改變係數的比較對象，因此係數會變。")])}
"""

# ── P06 problems ──────────────────────────────────────────────────────
BODIES["problems"] = f"""
{P06_INTRO}
{P06_AXES}

  <p>問題 1 到 5 都靠殘差類的圖看：講義用殘差圖、殘差對觀測順序圖、學生化殘差圖，再加上槓桿值。
  下面這個元件把五組資料（一組乾淨的、四組各有一種特徵）跟四張圖交叉組合起來，
  其中 Q-Q 圖與 scale-location 是講義之外的補充。
  <strong>先切換資料，再切換診斷圖，觀察各種問題的圖形特徵</strong>：</p>

{viz(chart("w03diagChart", "square",
           "。此圖的重點：殘差圖出現 U 形＝非線性；漏斗形＝異質變異；"
           "學生化殘差絕對值超過 3＝離群值；殘差對槓桿圖右下角遠離群體＝高槓桿點。"),
     [info_card("四張圖各看什麼",
                '<strong>① 殘差對擬合值（residual plot）：</strong>講義的主工具。應該是一團沒有結構的雲，'
                '紅線（分箱平均，用來觀察殘差趨勢）應該貼著 0。有 U 形＝非線性，有漏斗＝異質變異。<br>'
                '<strong>② Q-Q 圖、③ scale-location：</strong>講義之外的補充，分別看常態性與變異是否隨擬合值上升，'
                '說明收在本節末的延伸閱讀。<br>'
                '<strong>④ 殘差對槓桿（residuals vs leverage plot）：</strong>縱軸是學生化殘差，'
                '右上／右下角的點最危險，同時是離群值又是高槓桿點；講義的影響圖就是這張。'),
      rows_card("這一組資料的診斷數字",
                [("n", "—", "w03diagN"), ("$\\hat\\beta_1$", "—", "w03diagB1"),
                 ("RSE", "—", "w03diagRse"), ("R²", "—", "w03diagR2"),
                 ("最大 |學生化殘差|", "—", "w03diagMaxRes"),
                 ("最大槓桿值", "—", "w03diagMaxLev"),
                 ("槓桿值的平均 (p+1)/n", "—", "w03diagAvgLev")]),
      info_card("課本裡的對應圖",
                '第 ② 組是真的 <code>Auto</code> 資料（mpg 對 horsepower），'
                '就是 <strong>ISLP 圖 3.9 左</strong>那張經典的 U 形殘差圖；'
                '加上 horsepower² 之後 U 形會消失（圖 3.9 右）。'
                '第 ④ ⑤ 組對應圖 3.12 與圖 3.13。', "ISLP 圖 3.9／3.12／3.13")],
     "w03diagStatus", "先用下拉選單換資料，再按四個按鈕換圖。乾淨的資料四張圖都該沒有結構。",
     '<label class="slider-label" style="margin-right:.4rem;">資料</label>'
     '<select id="w03diagSel" class="mono" onchange="w03diagSetData()">'
     '<option value="good" selected>① 乾淨的線性資料</option>'
     '<option value="nonlin">② 非線性（真的 Auto 資料）</option>'
     '<option value="hetero">③ 異質變異</option>'
     '<option value="outlier">④ 離群值</option>'
     '<option value="lever">⑤ 高槓桿點</option></select>'
     '<button class="btn btn-toggle" onclick="w03diagView(0)">殘差 vs 擬合</button>'
     '<button class="btn btn-toggle" onclick="w03diagView(1)">Q-Q 圖</button>'
     '<button class="btn btn-toggle" onclick="w03diagView(2)">scale-location</button>'
     '<button class="btn btn-toggle" onclick="w03diagView(3)">殘差 vs 槓桿</button>',
     provenance=("illustrative", "固定種子診斷案例；非線性面板使用 ISLP Auto"))}

{P06_TOOLS_A}

{info("最危險的組合是「離群值 ＋ 高槓桿」", '''只是離群值（y 怪、x 正常）：它會推高 RSE、
  拉低 R²，但因為槓桿小，對係數的影響有限。<br>
  只是高槓桿（x 怪、但落在趨勢上）：它其實幫忙。把 x 的範圍拉開會<strong>降低</strong>
  $\\mathrm{{SE}}(\\hat\\beta_1)$。<br>
  兩個同時發生（ISLP 圖 3.13 的第 41 筆）：<strong>一個點就能把整條線扳過去</strong>，
  而且因為槓桿高、殘差被壓小，它在原始殘差圖上還不一定顯眼。
  這就是為什麼一定要看殘差對槓桿圖，以及為什麼上面的 Cook's distance
  把兩者一起算進去。''', "warm")}

{P06_TOOLS_B}

  $$\\mathrm{{VIF}}(\\hat\\beta_j) = \\frac{{1}}{{1 - R^2_{{X_j \\mid X_{{-j}}}}}}
    \\qquad\\Longrightarrow\\qquad
    \\frac{{\\mathrm{{SE}}(\\hat\\beta_j)\\ \\text{{有共線性}}}}
          {{\\mathrm{{SE}}(\\hat\\beta_j)\\ \\text{{無共線性}}}}
    = \\sqrt{{\\mathrm{{VIF}}}}$$

  <p>$R^2_{{X_j \\mid X_{{-j}}}}$ 是「拿 $X_j$ 對其他所有預測變數做迴歸」得到的 R²。
  它接近 1 就代表 $X_j$ 的資訊已經被別人講完了，VIF 就會變得很大。
  最小值是 1（完全無共線性），<strong>超過 5 或 10 就要處理</strong>。
  講義給的處理方式有兩個：拿掉其中一個多餘的變數；或把共線的變數合成一個（例如取平均）。
  推下面這根滑桿，看信賴區域怎麼從圓變成溝：</p>

{viz(svg("w03vifSvg", 330),
     [rows_card("即時計算",
                [("corr(X₁, X₂) = ρ", "0.00", "w03vifRhoR"),
                 ("VIF = 1/(1−ρ²)", "1.00", "w03vifVif"),
                 ("SE 膨脹倍數 = √VIF", "1.00", "w03vifInfl"),
                 ("t 值縮小成原來的", "100%", "w03vifT"),
                 ("同樣的資料量，等效於", "—", "w03vifEq"),
                 ("判準", "沒有問題", "w03vifVerdict")], "LIVE"),
      info_card("怎麼看這張圖",
                '兩軸是兩個係數（已中心化到最小平方解）。'
                '<span style="color:var(--fit-line);font-weight:700;">紅色曲線</span>'
                '是 RSS 的等高線，也就是「RSS 相同」的係數組合；'
                '淡藍色的十字帶是<strong>各自單獨</strong>的 95% 信賴區間。'
                '<br>ρ = 0 時等高線是圓，兩個係數各自估得準。'
                'ρ → 1 時它拉成一條沿著 β₁ = −β₂ 的長溝：'
                '<strong>「兩個係數的和」還是估得很準，但「各自是多少」完全分不出來。</strong>'
                '這正是 ISLP 圖 3.15 右邊那張圖。', "ISLP 圖 3.15"),
      info_card("Credit 資料上的真實案例",
                'balance 對 <code>age</code> + <code>limit</code>：'
                '<code>limit</code> 的 SE = 0.005、<em>t</em> = 34.5、p &lt; 0.0001。'
                '<br>改成對 <code>rating</code> + <code>limit</code>：'
                '同一個 <code>limit</code> 的 SE 變成 <strong>0.064</strong>'
                '（膨脹 12.8 倍）、<em>t</em> 掉到 <strong>0.38</strong>、p = 0.70。'
                '<br>三個一起放時 VIF 是 1.01、160.67、160.59。'
                '拿掉 <code>rating</code>，R² 只從 0.754 掉到 0.750——'
                '<strong>幾乎沒損失，問題卻解決了</strong>。', "ISLP 表 3.11")],
     "w03vifStatus", "ρ = 0：等高線是圓，兩個係數互不干擾。把滑桿往右推看看。",
     '<div class="slider-row" style="flex:1 1 250px;margin-bottom:0;">'
     '<span class="slider-label">ρ</span>'
     '<input type="range" id="w03vifRho" min="0" max="99" value="0" oninput="w03vifDraw()">'
     '<span class="slider-val" id="w03vifRhoV">0.00</span></div>'
     '<button class="btn btn-step" onclick="w03vifJump()">→ 跳到 Credit 的 limit／rating</button>'
     '<button class="btn btn-reset" onclick="w03vifHome()">重置</button>',
     provenance=("book-redraw", "依 ISLP 圖 3.15 與 VIF 公式重繪"))}

  <p class="source-note">講義補充連結：<a href="https://stats.stackexchange.com/questions/545148/why-is-multicollinearity-different-than-correlation" target="_blank" rel="noopener">多重共線性與相關的差別</a>。</p>

{P06_EXTRA}

  <h3 id="dx-prob">講義完整實作：VIF、多項式與 anova_lm</h3>
{card("講義 03 · 用串列生成式算每一欄的 VIF", lab_code(CH, 87), None,
      src=src("87、89"),
      note="<code>range(1, X.shape[1])</code> 從 1 開始是為了跳過第 0 欄的截距。"
           "Boston 的 12 個變數裡最大的是 <code>tax</code> 9.00 與 <code>rad</code> 7.45"
           "——這兩個確實相關（稅率高的地區通常離高速公路近），"
           "需要留意這兩欄的共線性；Credit 的 160 則顯示更嚴重的情況。")}

{card("講義 03 · 加二次項修掉非線性", lab_code(CH, 96), lab_output(CH, 96), src=src("96"),
      note="<code>poly('lstat', degree=2)</code> 產生的是<strong>正交</strong>多項式基底"
           "（為了數值穩定），所以係數 −179.23 與 72.99 不能直接讀成"
           "「lstat 與 lstat² 的係數」；要那樣讀得加 <code>raw=True</code>。"
           "兩種基底的<strong>擬合值完全相同</strong>，只是係數不同。"
           "二次項的 p 值實質為 0，表示它確實改善了模型。")}

{card("講義 03 · anova_lm：用 F 檢定比較巢狀模型", lab_code(CH, 98), lab_output(CH, 98),
      src=src("98"),
      note="比較「lstat + age」與「poly(lstat,2) + age」兩個巢狀模型。"
           "<em>F</em> = <strong>177.28</strong>、p = 7.47e-35，"
           "二次項不能省。注意"
           "<strong>177.28 恰好是上一張卡裡二次項 <em>t</em> = 13.315 的平方</strong>"
           "（13.315² ≈ 177.3）——巢狀模型只差 1 個自由度時，F 就是 t 的平方。"
           "這也解釋了為什麼 P04 說「F 可以檢定一組係數」是 t 檢定的推廣。"
           "另外 lab 的槓桿值診斷用 <code>np.argmax(infl.hat_matrix_diag)</code> 找出 "
           "Boston 裡槓桿值最大的是第 <strong>374</strong> 筆。")}

{quiz("qDiag", "QUIZ · 診斷圖",
      "殘差對擬合值的圖呈明顯的 <strong>U 形</strong>。下面哪個結論是對的？",
      [(True, "線性假設被違反了，係數本身的解讀就已經有問題，要先修模型的形狀",
        "對。這表示目前的線性條件平均形狀不合適。若 E[ε｜X] = 0 仍成立，誤差相關或異質變異主要使傳統 SE 與檢定失準；若外生性也失敗，係數同樣可能偏掉。修法是加 x²、log x，或第 7 章的樣條。ISLP 圖 3.9 左就是這個特徵，加了 horsepower² 之後 U 形就消失了。"),
       (False, "誤差不是常態分佈，應該對 y 取 log",
        "不對。殘差對擬合值圖看的是形狀與散布，U 形講的是「模型的形狀錯了」，跟誤差的分布是兩件事；對 y 取 log 是講義處理<strong>漏斗形</strong>（異質變異）的方式，不是處理 U 形的。"),
       (False, "有離群值把殘差拉歪了，把最大的幾個殘差刪掉重新擬合就好",
        "不對。這裡的 U 形反映<strong>系統性</strong>的結構；刪掉最大的殘差之後，剩下的點仍會排成 U 形。應調整模型的形狀，避免刪除資料後仍留下同樣的問題。")])}

{""}
"""

# ── P07 vsknn ─────────────────────────────────────────────────────────
BODIES["vsknn"] = f"""
  <p>線性迴歸是<strong>參數方法</strong>（parametric）：它先假設 f 的形狀
  （一條直線），然後只需要估 p + 1 個數字。好處很多——容易擬合、係數可解讀、
  有現成的 t 與 F 檢定。主要限制是：<strong>如果那個形狀猜錯了，
  就算資料再多也無法消除</strong>。</p>

  <p>對照組是 K 近鄰迴歸（KNN regression），一種無母數方法。
  要預測 $x_0$，就找離它最近的 K 個訓練點，把它們的 y 平均起來：</p>

  $$\\hat f(x_0) = \\frac{{1}}{{K}} \\sum_{{i \\in \\mathcal{{N}}_0}} y_i$$

  <p>它對 f 的形狀不做任何假設。K 小＝很有彈性但很不穩（K = 1 會穿過每一個訓練點）；
  K 大＝很平滑但可能糊掉真正的結構。這是第 2 章介紹的偏差–變異取捨。</p>

  <p>ISLP 圖 3.19–3.20 的結論是：真實關係接近直線時線性迴歸占優勢；
  關係明顯彎曲且 p 很小時 KNN 可能較好，但加入無關變數後 KNN 會迅速受維度詛咒影響。
  第 2 章的 KNN 圖可用來複習這個彈性取捨。</p>

{info("為什麼 p 大時無母數方法較難估準", '''這叫<strong>維度詛咒</strong>
  （curse of dimensionality）。KNN 的整個邏輯建立在「最近的 K 個點跟 x₀ 很像」之上。
  可是在 20 維裡，50 個點彼此的距離都差不多遠——「最近鄰」變成一個較弱的相似性判準，
  拿它們的 y 平均就等於拿一群不相干的點平均，偏差大到無法忍受。<br>
  線性迴歸靠的是「所有 n 筆資料共同決定 p + 1 個係數」，
  每筆資料都在為全域的形狀投票，不依賴局部鄰居，所以 p 變大只讓變異增加一點。<br>
  <strong>經驗法則：每個變數分到的樣本數太少時，偏好參數方法。</strong>''')}

{table(["", "線性迴歸", "KNN 迴歸"],
       [["對 f 的假設", "線性（強）", "只假設平滑（弱）"],
        ["要估的東西", "p + 1 個係數", "沒有參數，但要留著全部訓練資料"],
        ["真相是線性時", "<strong>贏</strong>（估得又快又準）", "略差（多付了變異）"],
        ["真相很彎時", "系統性偏差，無法消除", "<strong>表現明顯較好</strong>"],
        ["p 變大時", "退化得慢", "<strong>快速退化</strong>（維度詛咒）"],
        ["可解讀性", "係數、p 值、信賴區間都有", "幾乎沒有"],
        ["雜訊變數的影響", "多估幾個接近 0 的係數而已", "直接污染距離的計算"],
        ["預測的成本", "一次乘法", "每次都要掃過全部訓練資料"]])}

  <p>最後一件事，也是課本特別強調的：<strong>就算 KNN 的測試 MSE 稍微低一點，
  選線性迴歸仍然可能是對的</strong>。能用幾個係數清楚說明模型中的關係、
  能附上 p 值與信賴區間，這些在真實工作裡值得換掉一點點預測精度。
  第 7 章會給你一個折衷方案（GAM）：保留「每個變數各自一條曲線」的可解讀性，
  同時放掉線性的限制。</p>

{quiz("qKnn", "QUIZ · 線性迴歸 vs KNN",
      "真實關係<strong>明顯非線性</strong>，n = 50。什麼情況下線性迴歸反而贏過 KNN？",
      [(True, "預測變數的個數 p 一多（大約 p ≥ 4）就會贏，因為 KNN 受到維度詛咒的明顯影響",
        "對。ISLP 圖 3.20 的實驗就是這樣：p = 1、2 時 KNN 表現明顯較好，p = 3 打平，p ≥ 4 之後線性迴歸勝，而且差距愈拉愈大。線性迴歸只多估幾個係數，KNN 卻連「誰是鄰居」都算不準了。"),
       (False, "永遠不會贏，因為 KNN 不做任何形狀假設，一定更接近真相",
        "不對。KNN 依賴局部鄰居。維度高時，鄰近樣本也可能相距很遠；雜訊變數還會影響距離計算，使選出的鄰居較難代表目標點。"),
       (False, "只要把 K 調大就會贏，因為 K 大 KNN 就退化成線性迴歸",
        "不對。K 調到極大時 KNN 退化成「全部訓練資料的平均」，那是一個<strong>水平線</strong>，不是線性迴歸。KNN 無論怎麼調 K 都不會變成線性模型。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 3.7 第 1 題",
      "課本要你描述表 3.4 的 p 值各自對應什麼虛無假設，並用 sales／TV／radio／newspaper "
      "的語言（不要用係數）講結論。下面哪個描述對了？",
      [(True, "每個 p 值對應「在<strong>其他兩個媒體的預算固定</strong>的情況下，"
              "這個媒體與 sales 無關」；結論是 TV 與 radio 有關，newspaper 沒有",
        "對。關鍵是「其他變數固定」這五個字——多元迴歸的每個 p 值都是條件式的。所以正確的說法是「在電視與廣播預算已知的情況下，報紙預算對銷售量沒有額外的關聯」，而<strong>不是</strong>「報紙預算跟銷售量無關」（單獨看它其實是顯著的，t = 3.30）。"),
       (False, "每個 p 值對應「這個媒體單獨跟 sales 無關」；結論是 newspaper 跟 sales 無關",
        "不對，這正是這一題要糾正的誤解。「單獨」的檢定是表 3.1 與表 3.3 的簡單迴歸，那三個都顯著。表 3.4 的每一個檢定都是<strong>控制住其他變數之後</strong>的檢定。"),
       (False, "四個 p 值一起對應「三個係數同時為 0」；結論要看整體的 F 檢定",
        "不對，你講的是 <em>F</em> 檢定（表 3.6 的 570.3）。表 3.4 裡每一列有自己的 p 值，各自檢定<strong>一個</strong>係數為 0，這是 t 檢定。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 3.7 第 3 題（a）",
      "模型是 salary = 50 + 20·GPA + 0.07·IQ + 35·Level + 0.01·(GPA×IQ) − 10·(GPA×Level)，"
      "其中 Level = 1 代表大學畢業。固定 IQ 與 GPA，哪個說法對？",
      [(True, "GPA 夠高時，高中畢業生的平均起薪反而比大學畢業生高",
        "對。大學減高中的差距是 35 − 10·GPA，GPA &gt; 3.5 時就變成負的。這題的教學點是：<strong>有交互作用時，主效果的係數不能單獨解讀</strong>——35 只是「GPA = 0 時」的差距。順帶把 (b) 也算完：大學、IQ = 110、GPA = 4.0 → 50 + 80 + 7.7 + 35 + 4.4 − 40 = <strong>137.1</strong> 千美元。"),
       (False, "大學畢業生的平均起薪一定比高中畢業生高，因為 Level 的係數 35 是正的",
        "不對。35 只有在 GPA = 0 時才是完整的差距；兩組的差距是 35 − 10·GPA，會隨 GPA 遞減，GPA 超過 3.5 就翻轉。"),
       (False, "GPA×IQ 的係數只有 0.01，非常小，所以幾乎沒有交互作用效果",
        "不對，這是 (c) 小題的陷阱，答案是 False。係數的<strong>大小</strong>取決於變數的單位——IQ 的範圍是 100 上下，GPA 是 0–4，0.01×GPA×IQ 在 GPA = 4、IQ = 110 時是 4.4，不小。判斷有沒有證據要看 <strong>p 值</strong>（也就是係數除以它的 SE），不是看係數本身大不大。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 3.7 第 4 題（a）（b）",
      "n = 100、單一預測變數。真實關係<strong>是</strong>線性的。"
      "把「線性迴歸」與「三次迴歸」的<strong>訓練</strong> RSS 與<strong>測試</strong> RSS 比一比，"
      "預期是什麼？",
      [(True, "訓練 RSS：三次一定較低（或相等）；測試 RSS：預期線性較低",
        "對。訓練 RSS 那半是<strong>數學必然</strong>——線性模型是三次模型的特例（β₂ = β₃ = 0），所以三次模型的最小值不可能更差。測試 RSS 那半是<strong>期望</strong>：真相既然線性，三次項只增加變異而不減少偏差，所以平均而言會更差。這正是第 5 章要用交叉驗證的理由。"),
       (False, "兩個都是三次較低，因為三次模型比較有彈性",
        "訓練那半對，測試那半錯。彈性在訓練資料上永遠是優勢，在測試資料上只有「真相真的需要那個彈性」時才是優勢。這裡真相是線性的，多出來的彈性只是在擬合雜訊。"),
       (False, "資訊不足，兩個都無法判斷",
        "訓練 RSS 是可以判斷的，而且不需要任何資訊：巢狀模型的訓練 RSS 一定單調不增。只有測試 RSS 才需要「真相是線性」這個前提——而題目已經給了。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 3.7 第 7 題",
      "課本要你證明簡單線性迴歸（只有一個 x、有截距）的 R² 等於 x 與 y 相關係數的平方。"
      "為什麼這件事在多元迴歸就不能照搬？",
      [(True, "多元迴歸有多個 x，沒有單一個「x 與 y 的相關係數」；"
              "對應的結果變成 R² = Cor(y, ŷ)²",
        "對。多元的版本是 R² = Cor(Y, Ŷ)²，也就是反應變數與<strong>擬合值</strong>的相關係數平方。而且最小平方擬合出來的 Ŷ 有一個漂亮性質：在所有線性模型中，它讓這個相關係數最大。單變數時 ŷ 是 x 的線性函數，Cor(y, ŷ) = |Cor(y, x)|，兩個版本就對上了。"),
       (False, "因為多元迴歸的 R² 不再介於 0 與 1 之間",
        "不對。含截距的最小平方多元迴歸，R² 照樣介於 0 與 1（推理跟簡單迴歸一樣：只用 $\\bar y$ 猜是它的一個特例）。會跑出負值的是沒有截距、或在測試資料上算的情況。"),
       (False, "因為多元迴歸要用調整後 R²，普通 R² 不再有意義",
        "不對。普通 R² 的意義沒有改變（被解釋的變異比例），它只是<strong>不適合用來比較變數個數不同的模型</strong>。調整後 R² 是為了那個特定用途才發明的，不是因為普通 R² 失效。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
# 講義附錄的變數選擇、部分殘差及自助信賴區間。
BODIES["mlr"] += r"""
<h3>逐步選擇：如何形成候選模型？</h3>
<p><strong>順向選擇（forward selection）</strong>從只有截距開始，每步加入讓模型改善最多的一個變數；
<strong>反向選擇（backward selection）</strong>從完整模型開始，每步移除條件貢獻最小的變數。
<strong>混合選擇（mixed selection）</strong>每次加入後也重新檢查既有變數，允許刪除後來變得多餘的項目。
傳統做法可用 p 值作停止條件；更完整的比較會使用調整 R²、Cp、AIC、BIC 或交叉驗證，詳見
<a href="model_selection.html">模型選擇</a>。</p>
<p>反向最小平方選擇須先能擬合完整模型；p 大於等於 n 時通常無法使用一般滿秩版本。
順向法可以起步，但增加變數仍受設計矩陣秩限制。逐步搜尋是貪婪程序，未必找到所有子集合中的最佳解。
若用資料選變數，評估時必須把整個選擇步驟放入訓練折；選擇後的普通 p 值也不能直接視為預先指定模型的推論。</p>
<h3>控制其他變數：CCPR 與部分迴歸圖</h3>
<p><strong>成分加部分殘差圖（component-plus-residual plot, CCPR）</strong>畫
$e_i+\hat\beta_jx_{ij}$ 對 $x_{ij}$，並畫出 $\hat\beta_jx_{ij}$ 的線性成分。
它幫助檢查在其他變數已納入後，這一項是否仍有非線性形狀。</p>
<p><strong>部分迴歸圖（partial regression／added-variable plot）</strong>則先把 y 與 $X_j$
各自對其他預測變數及截距迴歸，再把兩組殘差互相作圖。滿秩最小平方下，其斜率等於完整模型的
$\hat\beta_j$。兩種圖的座標不同，不能把 CCPR 與部分迴歸圖當成同一張圖。
高度共線性時，CCPR 顯示的散布可能低估係數的不確定性，仍須結合 VIF 與標準誤判讀。</p>
<p>「其他變數固定，Xj 增加一單位」描述條件關聯。預測變數高度相關時，這種變動可能遠離實際資料範圍；
觀察資料上的迴歸係數也不能直接當成介入效果。模型的用途要透過診斷與新資料評估確認。</p>
"""
BODIES["inference"] += r"""
<h3>用 bootstrap 建立迴歸曲線的信賴區間</h3>
<p>若觀測對 $(x_i,y_i)$ 是獨立同分佈，可有放回地抽 n 對資料，重新擬合迴歸，並在同一組固定 x 網格預測。
重複 B 次後，在每個網格點取預測分佈的 2.5% 與 97.5% 分位數，就得到逐點的近似 95% percentile 信賴區間。
它描述平均反應曲線的估計不確定性，沒有自動包含新觀測的誤差，也不是整條曲線同時被涵蓋的 95% 保證。
固定設計或有時間相依的資料須另選適合的重抽方式；自助法的抽樣單位要配合研究設計。
<a href="resampling_methods.html#bootstrap">重抽樣章</a>進一步說明標準誤、信賴區間與預測區間的差別。</p>
"""

BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["簡單線性模型", "$Y = \\beta_0 + \\beta_1 X + \\varepsilon$", "式 3.5"],
        ["最小平方解",
         "$\\hat\\beta_1 = \\frac{\\sum(x_i-\\bar x)(y_i-\\bar y)}{\\sum(x_i-\\bar x)^2}$，"
         "$\\hat\\beta_0 = \\bar y - \\hat\\beta_1\\bar x$", "式 3.4；必過 $(\\bar x,\\bar y)$"],
        ["斜率＝加權平均",
         "$\\hat\\beta_1=\\sum_i w_is_i$，$w_i=\\frac{(x_i-\\bar x)^2}{S_{xx}}$，$s_i=\\frac{y_i-\\bar y}{x_i-\\bar x}$",
         "講義；離 $\\bar x$ 遠的點權重大"],
        ["斜率＝y 的線性組合",
         "$\\hat\\beta_1=\\sum_i c_iy_i$，$c_i=\\frac{x_i-\\bar x}{S_{xx}}$",
         "$\\sum c_i=0$、$\\sum c_ix_i=1$；常態誤差下 $\\hat\\beta_1$ 服從常態"],
        ["矩陣寫法", "$\\hat\\beta = (X^\\top X)^{-1}X^\\top y$", "多元迴歸的封閉解"],
        ["斜率的標準誤", "$\\mathrm{SE}(\\hat\\beta_1)^2 = \\sigma^2/\\sum(x_i-\\bar x)^2$",
         "式 3.8；x 散得開就小"],
        ["截距的標準誤",
         "$\\mathrm{SE}(\\hat\\beta_0)^2 = \\sigma^2\\left[\\frac1n"
         "+\\frac{\\bar x^2}{\\sum(x_i-\\bar x)^2}\\right]$", "式 3.8"],
        ["95% 信賴區間", "$\\hat\\beta_1 \\pm 2\\,\\mathrm{SE}(\\hat\\beta_1)$",
         "式 3.9；嚴格版用 t 分位數"],
        ["t 統計量", "$t = \\hat\\beta_1/\\mathrm{SE}(\\hat\\beta_1)$", "式 3.14；df = n−2"],
        ["平均反應的 CI",
         "$\\hat y_0\\pm t_{\\alpha/2,n-2}\\,\\hat\\sigma\\sqrt{\\frac1n+\\frac{(x_0-\\bar x)^2}{S_{xx}}}$",
         "在 $\\bar x$ 最窄；n 大時縮到 0"],
        ["新觀測的 PI",
         "$\\hat y_0\\pm t_{\\alpha/2,n-2}\\,\\hat\\sigma\\sqrt{1+\\frac1n+\\frac{(x_0-\\bar x)^2}{S_{xx}}}$",
         "根號裡多 1，一定比 CI 寬"],
        ["殘差標準誤", "$\\mathrm{RSE} = \\sqrt{\\mathrm{RSS}/(n-p-1)}$",
         "式 3.15／3.25；有單位"],
        ["R²", "$R^2 = 1 - \\mathrm{RSS}/\\mathrm{TSS}$",
         "式 3.17；含截距的訓練 OLS 介於 0 與 1；測試 R² 可為負"],
        ["F 統計量",
         "$F = \\frac{(\\mathrm{TSS}-\\mathrm{RSS})/p}{\\mathrm{RSS}/(n-p-1)}$",
         "式 3.23；$H_0$ 下約為 1"],
        ["學生化殘差", "$r_i = e_i/(\\mathrm{RSE}\\sqrt{1-h_i})$", "$|r_i|>3$ 可疑"],
        ["槓桿值",
         "$h_i = \\frac1n + \\frac{(x_i-\\bar x)^2}{\\sum(x_j-\\bar x)^2}$",
         "式 3.37；平均恰為 $(p+1)/n$；$h_i=1/n+w_i$"],
        ["Cook's distance",
         "$D_i=\\frac{r_i^2}{p+1}\\cdot\\frac{h_i}{1-h_i}$",
         "同時算進殘差與槓桿；影響圖的氣泡大小"],
        ["VIF", "$\\mathrm{VIF}(\\hat\\beta_j) = 1/(1-R^2_{X_j\\mid X_{-j}})$",
         "$>5$ 或 $10$ 要處理；SE 膨脹 $\\sqrt{\\mathrm{VIF}}$"],
        ["交互作用", "$Y = \\beta_0 + (\\beta_1+\\beta_3X_2)X_1 + \\beta_2X_2 + \\varepsilon$",
         "式 3.33；斜率隨 $X_2$ 移動"]])}

  <h3>Advertising 的迴歸結果</h3>
{table(["模型", "截距", "TV", "radio", "newspaper", "<em>F</em>", "R²", "RSE"],
       [["只有 TV", "7.0326", "0.0475<br>(<em>t</em> 17.67)", "—", "—",
         "312.1", "0.6119", "3.259"],
        ["只有 radio", "9.3116", "—", "0.2025<br>(<em>t</em> 9.92)", "—",
         "98.4", "0.3320", "4.275"],
        ["只有 newspaper", "12.3514", "—", "—", "0.0547<br>(<em>t</em> 3.30)",
         "10.9", "0.0521", "5.093"],
        ["TV + newspaper", "5.7749", "0.0469<br>(<em>t</em> 18.17)", "—",
         "0.0442<br>(<em>t</em> <strong>4.35</strong>)", "179.6", "0.6458", "3.121"],
        ["TV + radio", "2.9211", "0.0458<br>(<em>t</em> 32.91)",
         "0.1880<br>(<em>t</em> 23.38)", "—", "859.6", "0.8972", "1.681"],
        ["三個都放", "2.9389", "0.0458<br>(<em>t</em> 32.81)",
         "0.1885<br>(<em>t</em> 21.89)", "−0.0010<br>(<em>t</em> <strong>−0.18</strong>)",
         "570.3", "0.8972", "1.686"],
        ["TV + radio + TV×radio", "6.7502", "0.0191<br>(<em>t</em> 12.70)",
         "0.0289<br>(<em>t</em> 3.24)", "TV×radio 0.0011<br>(<em>t</em> 20.73)",
         "—", "<strong>0.9678</strong>", "0.944"]])}
  <p style="font-size:.82rem;color:var(--muted);"><code>newspaper</code> 的 <em>t</em> 值一路
  從 3.30（單獨）→ 4.35（加了 TV）→ −0.18（再加 radio）。
  <strong>同一欄資料，三個結論。</strong>差別只在「控制了什麼」。</p>

  <h3>六個潛在問題的一頁速查</h3>
{table(["問題", "診斷工具（標準名稱）", "會影響係數嗎", "會影響 SE／檢定嗎"],
       [["1. 非線性", "殘差圖（residual plot）出現 U 形", "<strong>會</strong>", "會"],
        ["2. 誤差相關", "殘差對觀測順序圖（residuals vs time／order plot）", "外生性成立時不必然", "<strong>會（通常低估）</strong>"],
        ["3. 異質變異", "殘差圖呈漏斗形", "外生性成立時不會", "<strong>會</strong>"],
        ["4. 離群值", "學生化殘差圖（studentized residual plot）$|r_i|>3$", "可能（槓桿低時影響小）", "會（RSE 變大）"],
        ["5. 高槓桿", "槓桿統計量 $h_i \\gg (p+1)/n$、Cook's distance、影響圖", "<strong>會（一個點就夠）</strong>", "會"],
        ["6. 共線性", "相關矩陣（correlation matrix）、VIF", "外生性成立時不會",
         "<strong>會（SE 膨脹 $\\sqrt{\\mathrm{VIF}}$）</strong>"]])}

{info("三個一定要記住的觀念", '''<strong>1. 多元迴歸係數描述控制模型中其他變數後的條件平均差。</strong>
  單變數顯著、多變數不顯著（Advertising 的 newspaper、Boston 的 age）不是矛盾，
  是兩個問題的答案不同；因果解讀還需要研究設計與額外假設。<br>
  <strong>2. F 與 t 回答不同的假設。</strong>F 評估整體證據，t 評估指定係數；
  兩者都可能有第一型錯誤，先通過 F 也不會自動校正多個個別檢定。<br>
  <strong>3. 無偏性需要正確的條件平均與 E[ε｜X] = 0。</strong>
  在此外生性成立時，誤差相關與異質變異主要使傳統 SE 失準，方向不能只由「有相關」判定。
  因此要檢查殘差結構並選合適的推論方法。''')}


"""

# ══════════════════════════════════════════════════════════════════════
# COVERAGE-20260910 BEGIN

# 估計、推論與部分檢定的完整條件和可展開推導。
BODIES['slr'] += proof('w03proofOls', '最小平方解、殘差正交與 RSS 曲面', r"""
<p>對 $L=\sum_i(y_i-b_0-b_1x_i)^2$ 微分，得到 $\sum_i(y_i-b_0-b_1x_i)=0$ 與 $\sum_ix_i(y_i-b_0-b_1x_i)=0$。第一式給 $b_0=\bar y-b_1\bar x$；代回第二式並利用中心化和為零：</p>
$$b_1\sum_i(x_i-\bar x)^2=\sum_i(x_i-\bar x)(y_i-\bar y).$$
<p>只要 x 不全相同，分母為正，就得到正文斜率與截距。矩陣版令 X 含截距欄，梯度為 $-2X^T(y-Xb)$，所以 $X^TX\hat\beta=X^Ty$。X 滿欄秩時 $X^TX$ 正定，唯一解為 $(X^TX)^{-1}X^Ty$。</p>
<p>令 $e=y-X\hat\beta$，normal equations 給 $X^Te=0$，故對任意 $d=b-\hat\beta$：</p>
$$\|y-Xb\|^2=\|e-Xd\|^2=\|e\|^2+d^TX^TXd.$$
<p>交叉項為零，因此最小值確在 $d=0$；展開二維二次型便是正文 RSS 等高線公式。若 X 不滿秩，擬合值仍是 y 在欄空間的唯一投影，但係數未必唯一，不能直接取逆矩陣。</p>
""")
BODIES['inference'] += r"""
<h3>公式的條件與平均反應／新觀測</h3>
<p>以下給定滿欄秩 X，包含截距及 p 個預測變數，n&gt;p+1；誤差條件平均為零、共變異數為 $\sigma^2I$。係數共變異數為 $\sigma^2(X^TX)^{-1}$。再加常態誤差，才有有限樣本精確 t 與 F 分布。</p>
$$s^2=\frac{\mathrm{RSS}}{n-p-1},\quad \widehat{SE}(\hat\beta_j)=s\sqrt{[(X^TX)^{-1}]_{jj}}.$$
<p>新輸入向量 $x_0$ 包含開頭的 1，令 $h_0=x_0^T(X^TX)^{-1}x_0$。在上述常態模型下：</p>
$$\text{平均反應 CI}:\quad x_0^T\hat\beta\pm t_{1-\alpha/2,n-p-1}s\sqrt{h_0},$$
$$\text{獨立新觀測 PI}:\quad x_0^T\hat\beta\pm t_{1-\alpha/2,n-p-1}s\sqrt{1+h_0}.$$
<p>兩個區間的中心相同；預測一個新觀測還要包含它本身的雜訊。</p>
""" + proof('w03proofInference', '係數變異、自由度與兩種區間', r"""
<p>代入 $y=X\beta+\varepsilon$，有 $\hat\beta-\beta=(X^TX)^{-1}X^T\varepsilon$，所以期望為零、共變異數為 $\sigma^2(X^TX)^{-1}$。簡單迴歸中令 $S_{xx}=\sum_i(x_i-\bar x)^2$，可得 $\hat\beta_1-\beta_1=\sum_i(x_i-\bar x)\varepsilon_i/S_{xx}$，變異數為 $\sigma^2/S_{xx}$；截距的變異數為 $\sigma^2(1/n+\bar x^2/S_{xx})$。</p>
<p>帽子矩陣 $H=X(X^TX)^{-1}X^T$ 對稱且冪等，秩為 p+1。殘差為 $(I-H)\varepsilon$，故 $E[\mathrm{RSS}]=\sigma^2\operatorname{tr}(I-H)=(n-p-1)\sigma^2$。常態誤差經正交座標變換後，RSS 除以 $\sigma^2$ 是 n−p−1 個獨立標準常態平方和；投影 H 與 I−H 的座標獨立。因此標準常態係數誤差除以獨立的 $\sqrt{\chi^2_\nu/\nu}$，得到 t 分布。</p>
<p>$x_0^T(\hat\beta-\beta)$ 的變異數為 $\sigma^2h_0$。對新觀測 $Y_0=x_0^T\beta+\varepsilon_0$，獨立的 $\varepsilon_0$ 再增加 $\sigma^2$，預測誤差變異成為 $\sigma^2(1+h_0)$。分別用 s 取代 σ 並套 t 分位數，便得到兩種區間。</p>
""")
BODIES['mlr'] += r"""
<h3>一次檢定一組係數：部分 F 檢定</h3>
<p>完整模型有 p 個預測變數；受限模型固定其中 q 個係數為零，兩模型用同一批觀測、同一反應與誤差模型，並且欄空間巢狀。記兩個殘差平方和為 RSS 與 RSS₀。常態、等變異、獨立誤差與滿欄秩條件下：</p>
$$F=\frac{(\mathrm{RSS}_0-\mathrm{RSS})/q}{\mathrm{RSS}/(n-p-1)}\ \overset{H_0}{\sim}\ F_{q,n-p-1}.$$
<p>只留截距的受限模型給 RSS₀=TSS、q=p，便是整體 F 檢定。q=1 時，此 F 等於同一係數雙尾 t 檢定的 $t^2$。</p>
""" + proof('w03proofPartialF', '巢狀模型的額外平方和與 F 分布', r"""
<p>令 H、H₀ 是完整與受限模型的正交投影。巢狀性給 $HH_0=H_0H=H_0$，因此 H−H₀ 為秩 q 的投影，並與 I−H 正交。</p>
$$\mathrm{RSS}_0-\mathrm{RSS}=y^T(H-H_0)y.$$
<p>$H_0$ 成立時，平均向量落在受限欄空間，故上式等於 $\varepsilon^T(H-H_0)\varepsilon$。在常態誤差下，它除以 $\sigma^2$ 服從 $\chi^2_q$；RSS 除以 $\sigma^2$ 服從獨立的 $\chi^2_{n-p-1}$。各除自由度後取比，就是正文 F 分布。q=1 時，額外平方和等於 $\hat\beta_j^2/[(X^TX)^{-1}]_{jj}$，除以 $s^2$ 即為 $t_j^2$。</p>
""")
BODIES['mlr'] += proof('w03proofFWL', '部分迴歸圖的斜率等於完整模型係數', r"""
<p>把 X 分成其他變數 Z（含截距）與目標欄 x，令 $M_Z=I-Z(Z^TZ)^{-1}Z^T$。固定 x 的係數 b 後，對 Z 的最小平方殘差是 $M_Z(y-xb)$。因此只需最小化 $\|M_Zy-M_Zxb\|^2$。</p>
$$\hat b=\frac{x^TM_Zy}{x^TM_Zx}.$$
<p>這就是兩組殘差 $M_Zy$ 對 $M_Zx$ 的迴歸斜率。分母須為正，即 x 不在 Z 的欄空間內。CCPR 用原始 x 作橫軸，沒有這個雙重殘差化，因此兩種圖不相同。</p>
""")

# COVERAGE-20260910 END

# LINK-CLOSURE-CH1-3

BODIES['slr'] += r"""
<h3>解釋變數一定要是隨機變數嗎？</h3>
<p>實驗可由研究者固定輸入值，例如指定不同施肥量；觀察資料的輸入則可以是隨機抽到的。
兩種情況都可分析。對隨機 X，先給定實際觀察到的 X，使用 $E(\varepsilon\mid X)=0$ 及條件共變異數假設推導。
稱 X 為「independent variable」不代表各個解釋變數互相獨立，也不代表 Y 與 X 獨立。</p>
<p>常態線性模型的誤差可獨立同分布，但各筆 Y 的平均隨 x 改變，所以 Y 通常不是同分布。
在固定 σ 的 Gaussian 概似中，最大化係數概似等價於最小化 RSS；若連 σ 也估計，完整對數概似仍須保留 $-n\log\sigma$ 項。</p>
"""
BODIES['qualitative'] += r"""
<h3>中心化會改變哪個係數的意義？</h3>
<p>只有主效應且含截距的普通最小平方模型，將每欄減去常數可改寫截距而保持所有擬合值。
把 x 換成 $u=x-a$ 後，截距代表原來 x=a 時的平均反應；若再除以尺度，係數單位跟著改變。
這種可逆重新參數化不會消除原本精確的線性相依，也不會自動修復混淆。</p>
<p>有交互作用時，令 $u=x-a,v=z-b$，完整模型改寫為</p>
$$\beta_0+\beta_1x+\beta_2z+\beta_3xz
=(\beta_0+a\beta_1+b\beta_2+ab\beta_3)
+(\beta_1+b\beta_3)u+(\beta_2+a\beta_3)v+\beta_3uv.$$
<p>交互作用係數保留，但主效應係數改成另一個參考點的斜率，檢定「主效應為零」的意義也改了。
只保留 xz 卻移除 x、z，平移座標後會產生無處容納的主效應項；因此一般遵守階層原則。
有明確科學理由設定某些主效應為零仍是可能的模型，須說明該限制與選定原點的含義。</p>
"""
BODIES['problems'] += r"""
<h3>內部與外部學生化殘差</h3>
<p>令 m=p+1 為含截距的參數數，ν=n−m，X 滿欄秩。帽子矩陣 H 給出
$\operatorname{Var}(e_i\mid X)=\sigma^2(1-h_{ii})$。
前面的圖使用整份資料的 $s^2=\mathrm{RSS}/\nu$，因此是<strong>內部學生化</strong>：</p>
$$r_i=\frac{e_i}{s\sqrt{1-h_{ii}}}.$$
<p>檢查第 i 筆時，也可以刪除此筆再估 σ，得到<strong>外部學生化</strong>：</p>
$$s_{(i)}^2=\frac{\mathrm{RSS}-e_i^2/(1-h_{ii})}{\nu-1},\qquad
 t_i=\frac{e_i}{s_{(i)}\sqrt{1-h_{ii}}}
=r_i\sqrt{\frac{\nu-1}{\nu-r_i^2}}.$$
<p>這需要 ν&gt;1、$h_{ii}&lt;1$ 且刪除後殘差變異估計為正。
常態、等變異、獨立誤差模型下，固定 i 的外部學生化量服從 $t_{\nu-1}$；內部學生化量因分母也使用本筆，不服從同一 t 分布。

「絕對值大於 3」是回查線索，不是對整批觀測自動有效的多重離群檢定。</p>
""" + proof('w03proofDeletedResidual','刪除一筆後的變異與學生化',r"""
<p>令刪除第 i 筆後係數為 $\hat\beta_{(i)}$。秩一更新給</p>
$$\hat\beta_{(i)}=\hat\beta-\frac{(X^TX)^{-1}x_ie_i}{1-h_{ii}},\qquad
\mathrm{RSS}_{(i)}=\mathrm{RSS}-\frac{e_i^2}{1-h_{ii}}.$$
<p>刪除一筆使殘差自由度從 ν 變成 ν−1；以此定義 $s_{(i)}$，並用 $r_i^2=e_i^2/[s^2(1-h_{ii})]$ 整理即可得到兩者換算。
常態模型下，刪除模型對第 i 筆的預測誤差除以其真實標準差為標準常態，且與刪除模型的 RSS 獨立。
除以獨立的 $\sqrt{\chi^2_{\nu-1}/(\nu-1)}$，便得到外部學生化的 t 分布。</p>
""") + r"""
<p class="source-note">來源：講義的殘差、相關與槓桿討論；
<a href="https://stat.ethz.ch/R-manual/R-devel/library/stats/html/influence.measures.html" target="_blank" rel="noopener">R 官方刪除診斷</a>區分整體與 leave-one-out 的變異估計。
</p>
"""
BODIES['accuracy'] += r"""
<h3>相關係數平方不能取代任意預測的 R²</h3>
<p>含截距的訓練 OLS，且 y 與擬合值都有非零變異時，$R^2=\operatorname{Cor}(y,\hat y)^2$。
但對任意預測向量、測試集預測或把觀測與預測互換，這個等式不一定成立。
相關係數不會因預測整體平移而改變，但對原觀測的平方誤差會改變。
排序與方向完全一致，仍可能每筆都偏高 10；R² 的誤差定義會看見這個偏移。</p>
"""


PAGEJS = r"""
/* ===== linear_regression 本頁元件（id 與全域一律 w03 前綴）===== */

/* ---------- 共用小工具 ---------- */
/* 二次型 a·u² + 2b·uv + c·v² = L 的等高線（精確橢圓，不需要 marching squares）。
   對每個角度 θ 解 r：r² · q(θ) = L，其中 q(θ) = a·cos²θ + 2b·cosθ·sinθ + c·sin²θ。 */
function w03ellipse(a, b, c, L, m) {
  const pts = [];
  for (let i = 0; i <= m; i++) {
    const th = 2 * Math.PI * i / m, cs = Math.cos(th), sn = Math.sin(th);
    const q = a * cs * cs + 2 * b * cs * sn + c * sn * sn;
    const rr = q > 1e-12 ? Math.sqrt(L / q) : 0;
    pts.push([rr * cs, rr * sn]);
  }
  return pts;
}
/* 標準常態的反函數（Acklam 有理近似，絕對誤差 < 5e-9）。HC.stat 只有 pnorm。 */
function w03qnorm(p) {
  if (p <= 0) return -6; if (p >= 1) return 6;
  const a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
             1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
  const b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
             6.680131188771972e+01, -1.328068155288572e+01];
  const c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
             -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
  const d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
             3.754408661907416e+00];
  const pl = 0.02425;
  let q, r;
  if (p < pl) {
    q = Math.sqrt(-2 * Math.log(p));
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
         / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  }
  if (p > 1 - pl) {
    q = Math.sqrt(-2 * Math.log(1 - p));
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
          / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  }
  q = p - 0.5; r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
       / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}
/* 分箱平均：診斷圖裡那條「紅色平滑線」的窮人版 */
function w03binMean(xs, ys, nb) {
  const lo = Math.min.apply(null, xs), hi = Math.max.apply(null, xs);
  const sum = new Array(nb).fill(0), cnt = new Array(nb).fill(0);
  for (let i = 0; i < xs.length; i++) {
    let k = Math.floor((xs[i] - lo) / (hi - lo || 1) * nb);
    if (k < 0) k = 0; if (k >= nb) k = nb - 1;
    sum[k] += ys[i]; cnt[k] += 1;
  }
  const out = [];
  for (let k = 0; k < nb; k++) {
    if (cnt[k] > 0) out.push({ x: lo + (hi - lo) * (k + 0.5) / nb, y: sum[k] / cnt[k] });
  }
  return out;
}

/* ---------- P01 可拖曳散佈圖 + 即時 OLS ---------- */
const w03dragN = 12;
let w03pts = null;
let w03dragSvc = null, w03dragDots = [], w03dragIdx = -1;
let w03dragShowRes = true, w03dragSeed = 5240;

function w03dragMake(seed) {
  const rand = HC.stat.lcg(seed), xs = [], ys = [];
  for (let i = 0; i < w03dragN; i++) {
    const x = 0.7 + i * 0.77 + 0.3 * (rand() - 0.5);
    let y = 4.2 + 2.05 * x + 2.7 * HC.stat.normal(rand);
    y = Math.max(0.6, Math.min(29.4, y));
    xs.push(Math.round(x * 100) / 100);
    ys.push(Math.round(y * 100) / 100);
  }
  return { xs: xs, ys: ys };
}

function w03dragSetup() {
  w03dragSvc = HC.svg('w03dragSvg', { xd: [0, 10], yd: [0, 30], h: 350 });
  if (!w03dragSvc) return;
  const s = w03dragSvc;
  s.grid(5, 6, { xtitle: 'x（想成 TV 廣告預算）', ytitle: 'y（想成 sales）', xdec: 0, ydec: 0 });
  s.layer('fit');           /* 先建圖層，順序＝繪製順序：格線 → 擬合線 → 試探線 → 點 */
  s.layer('trial');
  const g = s.layer('pts');
  w03dragDots = [];
  for (let i = 0; i < w03dragN; i++) {
    w03dragDots.push(s.dot(0, 0, { cls: 'dot drag', r: 7.5, fill: HC.tok.train,
                                   stroke: '#fff', sw: 1.8, i: i }, g));
  }
  /* 自己先挑「離按下位置最近的點」，再讓 HC.drag 負責 pointer 事件與夾住定義域。
     這個 listener 一定要比 HC.drag 的先註冊，才會先跑。 */
  s.el.addEventListener('pointerdown', function (ev) {
    if (!w03pts) return;
    let best = -1, bd = 1e9;
    const p = s.toData(ev);
    for (let i = 0; i < w03dragN; i++) {
      const dx = (p.x - w03pts.xs[i]) / (s.xd[1] - s.xd[0]);
      const dy = (p.y - w03pts.ys[i]) / (s.yd[1] - s.yd[0]);
      const d2 = dx * dx + dy * dy;
      if (d2 < bd) { bd = d2; best = i; }
    }
    w03dragIdx = Math.sqrt(bd) < 0.07 ? best : -1;
  });
  HC.drag(s.el, s, function (m) {
    if (w03dragIdx < 0 || !w03pts) return;
    w03pts.xs[w03dragIdx] = Math.round(m.x * 100) / 100;
    w03pts.ys[w03dragIdx] = Math.round(m.y * 100) / 100;
    w03dragRender(true);
  });
}

function w03dragRender(moved) {
  const s = w03dragSvc;
  if (!s || !w03pts) return;
  const xs = w03pts.xs, ys = w03pts.ys;
  const f = HC.stat.ols(xs, ys);
  const g = s.clearLayer('fit');
  s.poly([[s.xd[0], f.b0 + f.b1 * s.xd[0]], [s.xd[1], f.b0 + f.b1 * s.xd[1]]], { cls: 'fit' }, g);
  if (w03dragShowRes) {
    for (let i = 0; i < xs.length; i++) {
      s.seg(xs[i], ys[i], xs[i], f.b0 + f.b1 * xs[i], { cls: 'resid', sw: 1.8 }, g);
    }
  }
  for (let i = 0; i < w03dragN; i++) {
    w03dragDots[i].setAttribute('cx', s.X(xs[i]));
    w03dragDots[i].setAttribute('cy', s.Y(ys[i]));
  }
  $('w03dragB0').textContent = HC.fmt(f.b0, 3);
  $('w03dragB1').textContent = HC.fmt(f.b1, 3);
  $('w03dragRss').textContent = HC.fmt(f.rss, 2);
  $('w03dragRse').textContent = HC.fmt(f.rse, 3);
  $('w03dragR2').textContent = HC.fmt(f.r2, 4);
  $('w03dragSe1').textContent = HC.fmt(f.seB1, 4);
  $('w03dragT1').textContent = HC.fmt(f.tB1, 2);
  if (moved) {
    setStatus('w03dragStatus', '這條線是 β̂₀ = ' + HC.fmt(f.b0, 2) + '、β̂₁ = '
      + HC.fmt(f.b1, 3) + '，RSS = ' + HC.fmt(f.rss, 1) + '、R² = ' + HC.fmt(f.r2, 3)
      + '。任何其他直線的 RSS 都比它大。');
  }
  w03rssRender();
}

function w03dragReset() {
  w03dragSeed = 5240;
  w03pts = w03dragMake(w03dragSeed);
  w03dragRender(false);
  setStatus('w03dragStatus', '回到原始的 12 個點。拖動任何一個藍點，係數與 RSS 會即時重算。');
}
function w03dragNewData() {
  w03dragSeed += 137;
  w03pts = w03dragMake(w03dragSeed);
  w03dragRender(false);
  setStatus('w03dragStatus', '換了一組資料（固定種子 ' + w03dragSeed
    + '，重載頁面會得到一樣的點）。RSS 與 R² 都跟著換了。');
}
function w03dragToggleRes() {
  w03dragShowRes = !w03dragShowRes;
  const b = $('w03dragResBtn');
  if (b) {
    b.textContent = w03dragShowRes ? '隱藏殘差線段' : '顯示殘差線段';
    b.classList.toggle('off', !w03dragShowRes);
  }
  w03dragRender(false);
}

/* ---------- P01 RSS 等高線（與上面的點連動） ---------- */
const w03rssLev = [1.03, 1.1, 1.25, 1.6, 2.2];
let w03rssU = 0, w03rssV = 0, w03rssSvc = null;

function w03rssSetup() {
  w03rssSvc = HC.svg('w03rssSvg', { xd: [-1, 1], yd: [-1, 1], h: 330 });
}
function w03rssMove() {
  const a = $('w03rssU'), b = $('w03rssV');
  w03rssU = a ? parseInt(a.value, 10) / 100 : 0;
  w03rssV = b ? parseInt(b.value, 10) / 100 : 0;
  w03rssRender();
}
function w03rssHome() {
  if ($('w03rssU')) $('w03rssU').value = '0';
  if ($('w03rssV')) $('w03rssV').value = '0';
  w03rssMove();
}
function w03rssRender() {
  const s = w03rssSvc;
  if (!s || !w03pts) return;
  const xs = w03pts.xs, ys = w03pts.ys, n = xs.length;
  const f = HC.stat.ols(xs, ys);
  let sx = 0, sx2 = 0;
  for (let i = 0; i < n; i++) { sx += xs[i]; sx2 += xs[i] * xs[i]; }
  const A = n, B = sx, C = sx2, det = Math.max(1e-9, A * C - B * B);
  const Lmax = (w03rssLev[w03rssLev.length - 1] - 1) * Math.max(f.rss, 1e-6);
  const umax = Math.sqrt(Lmax * C / det), vmax = Math.sqrt(Lmax * A / det);
  s.domain([f.b0 - 1.18 * umax, f.b0 + 1.18 * umax],
           [f.b1 - 1.18 * vmax, f.b1 + 1.18 * vmax]);
  s.grid(4, 4, { xtitle: 'β₀（截距）', ytitle: 'β₁（斜率）', xdec: 1, ydec: 2 });
  const g = s.clearLayer('cont');
  for (let k = 0; k < w03rssLev.length; k++) {
    const L = (w03rssLev[k] - 1) * f.rss;
    const pts = w03ellipse(A, B, C, L, 84).map(function (p) {
      return [f.b0 + p[0], f.b1 + p[1]];
    });
    s.poly(pts, { cls: 'fit', stroke: 'rgba(192,57,43,' + (0.8 - 0.11 * k).toFixed(2) + ')',
                  sw: 1.5 }, g);
    s.txt(f.b0, f.b1 + Math.sqrt(L / C), '×' + w03rssLev[k].toFixed(2),
          { cls: 'axlab', dy: -4 }, g);
  }
  const u = w03rssU * umax, v = w03rssV * vmax;
  const rss = f.rss + A * u * u + 2 * B * u * v + C * v * v;
  s.dot(f.b0, f.b1, { r: 5.5, fill: HC.tok.fit, stroke: '#fff', sw: 1.6 }, g);
  if (Math.abs(u) > 1e-9 || Math.abs(v) > 1e-9) {
    s.seg(f.b0, f.b1, f.b0 + u, f.b1 + v, { cls: 'resid', sw: 1.6 }, g);
  }
  s.dot(f.b0 + u, f.b1 + v, { r: 7, fill: HC.tok.held, stroke: '#fff', sw: 2 }, g);
  if ($('w03rssUv')) $('w03rssUv').textContent = HC.fmt(u, 2);
  if ($('w03rssVv')) $('w03rssVv').textContent = HC.fmt(v, 3);
  $('w03rssB0').textContent = HC.fmt(f.b0 + u, 3);
  $('w03rssB1').textContent = HC.fmt(f.b1 + v, 3);
  $('w03rssVal').textContent = HC.fmt(rss, 2);
  $('w03rssRatio').textContent = '× ' + HC.fmt(rss / Math.max(f.rss, 1e-9), 3);
  $('w03rssMin').textContent = HC.fmt(f.b0, 2) + ' , ' + HC.fmt(f.b1, 3);
  /* 把這組試探係數畫回上面那張散佈圖 */
  if (w03dragSvc) {
    const gt = w03dragSvc.clearLayer('trial');
    if (Math.abs(u) > 1e-9 || Math.abs(v) > 1e-9) {
      const b0 = f.b0 + u, b1 = f.b1 + v, d = w03dragSvc;
      d.poly([[d.xd[0], b0 + b1 * d.xd[0]], [d.xd[1], b0 + b1 * d.xd[1]]], { cls: 'truef' }, gt);
    }
  }
  if (Math.abs(u) < 1e-9 && Math.abs(v) < 1e-9) {
    setStatus('w03rssStatus', '橘點正好在碗底（紅點），RSS = ' + HC.fmt(f.rss, 2)
      + ' 就是最小值。推滑桿讓它離開看看。');
  } else {
    setStatus('w03rssStatus', '這組係數的 RSS = ' + HC.fmt(rss, 2) + '，是最小值的 '
      + HC.fmt(rss / Math.max(f.rss, 1e-9), 2) + ' 倍。上面那張圖出現的綠色虛線就是它畫出來的線。');
  }
}

/* ---------- P02 抽樣變異：100 條迴歸線 ---------- */
const w03sampN = 40, w03sampTrueB0 = 2, w03sampTrueB1 = 3, w03sampSigma = 2.5;
const w03sampX = HC.stat.seq(0.4, 9.6, w03sampN);
const w03sampSxx = (function () {
  const m = HC.stat.mean(w03sampX);
  let s = 0;
  for (let i = 0; i < w03sampX.length; i++) s += (w03sampX[i] - m) * (w03sampX[i] - m);
  return s;
})();
const w03sampSeForm = w03sampSigma / Math.sqrt(w03sampSxx);
let w03sampSvc = null, w03sampB1 = [];

function w03sampSetup() {
  w03sampSvc = HC.svg('w03sampSvg', { xd: [0, 10], yd: [-8, 40], h: 320 });
  if (!w03sampSvc) return;
  w03sampSvc.grid(5, 6, { xtitle: 'x（每次重抽都用同一組 x）', ytitle: 'y', xdec: 0, ydec: 0 });
  w03sampSvc.layer('lines');
  w03sampSvc.layer('over');
}
function w03sampFit(k) {
  const rand = HC.stat.lcg(310000 + k * 7919);
  const ys = w03sampX.map(function (x) {
    return w03sampTrueB0 + w03sampTrueB1 * x + w03sampSigma * HC.stat.normal(rand);
  });
  const f = HC.stat.ols(w03sampX, ys);
  f.ys = ys;
  return f;
}
function w03sampTrueLine() {
  const s = w03sampSvc;
  const g = s.clearLayer('over');
  s.poly([[s.xd[0], w03sampTrueB0 + w03sampTrueB1 * s.xd[0]],
          [s.xd[1], w03sampTrueB0 + w03sampTrueB1 * s.xd[1]]], { cls: 'truef', sw: 3 }, g);
  s.txtPx(56, 24, '綠虛線＝示意的母體迴歸線', { cls: 'axtitle' }, g);
  return g;
}
function w03sampAdd(f, highlight) {
  const s = w03sampSvc;
  if (!s) return;
  const g = s.layer('lines');
  s.poly([[s.xd[0], f.b0 + f.b1 * s.xd[0]], [s.xd[1], f.b0 + f.b1 * s.xd[1]]],
         { cls: 'fit', stroke: 'rgba(192,57,43,.22)', sw: 1.2 }, g);
  const og = w03sampTrueLine();
  if (highlight) {
    for (let i = 0; i < w03sampX.length; i++) {
      s.dot(w03sampX[i], f.ys[i], { r: 3, fill: HC.tok.train, opacity: 0.75 }, og);
    }
    s.poly([[s.xd[0], f.b0 + f.b1 * s.xd[0]], [s.xd[1], f.b0 + f.b1 * s.xd[1]]],
           { cls: 'fit', sw: 2.8 }, og);
  }
}
function w03sampStats() {
  $('w03sampCount').textContent = w03sampB1.length;
}
function w03sampHist() {
  const lo = w03sampTrueB1 - 4.2 * w03sampSeForm, hi = w03sampTrueB1 + 4.2 * w03sampSeForm;
  const bins = 20, h = new Array(bins).fill(0);
  for (let i = 0; i < w03sampB1.length; i++) {
    let k = Math.floor((w03sampB1[i] - lo) / (hi - lo) * bins);
    if (k < 0) k = 0; if (k >= bins) k = bins - 1;
    h[k] += 1;
  }
  HC.bar('w03sampChart', {
    labels: h.map(function (_, i) { return HC.fmt(lo + (hi - lo) * (i + 0.5) / bins, 2); }),
    datasets: [{ label: 'β̂₁ 的分佈', data: h,
                 backgroundColor: 'rgba(44,62,122,.72)', borderRadius: 3 }],
  }, {
    plugins: { legend: { display: false } },
    scales: { x: { title: { display: true, text: 'β̂₁（每一次重抽算出來的斜率）' } },
              y: { title: { display: true, text: '次數' }, ticks: { precision: 0 } } },
  });
  const c = HC.get('w03sampChart');
  HC.refs(c, [HC.vline(HC.fmt(w03sampTrueB1, 2), '母體斜率')]);
}
function w03sampOne() {
  const f = w03sampFit(w03sampB1.length);
  w03sampB1.push(f.b1);
  w03sampAdd(f, true);
  w03sampStats();
  w03sampHist();
  setStatus('w03sampStatus', '每條線來自一份重新抽樣的資料；觀察斜率估計值如何散開。');
}
function w03sampMany() {
  let f = null;
  while (w03sampB1.length < 100) {
    f = w03sampFit(w03sampB1.length);
    w03sampB1.push(f.b1);
    w03sampAdd(f, false);
  }
  w03sampTrueLine();
  w03sampStats();
  w03sampHist();
  setStatus('w03sampStatus', '每條線來自一份重新抽樣的資料；觀察斜率估計值如何散開。');
}
function w03sampReset() {
  w03sampB1 = [];
  if (w03sampSvc) {
    w03sampSvc.clearLayer('lines');
    w03sampTrueLine();
  }
  w03sampStats();
  HC.bar('w03sampChart', { labels: [], datasets: [{ data: [] }] },
         { plugins: { legend: { display: false } } });
  setStatus('w03sampStatus', '每條線來自一份重新抽樣的資料；觀察斜率估計值如何散開。');
}

/* ---------- P06 四張診斷圖 ---------- */
let w03diagKey = 'good', w03diagV = 0;
const w03diagVNames = ['殘差 vs 擬合值', 'Q-Q 圖', 'scale-location', '殘差 vs 槓桿值'];

function w03diagPrep(key) {
  const P = FRAMES_w03diag.panels[key], st = [];
  for (let i = 0; i < P.n; i++) {
    st.push(P.res[i] / (P.rse * Math.sqrt(Math.max(1e-6, 1 - P.lev[i]))));
  }
  return { P: P, st: st };
}
function w03diagSetData() {
  const sel = $('w03diagSel');
  if (sel) w03diagKey = sel.value;
  w03diagDraw();
}
function w03diagView(v) { w03diagV = v; w03diagDraw(); }
function w03diagDraw() {
  const d = w03diagPrep(w03diagKey), P = d.P, st = d.st;
  const pts = [], sets = [];
  let xt = '', yt = '', plugs = [];
  if (w03diagV === 0) {
    for (let i = 0; i < P.n; i++) pts.push({ x: P.fit[i], y: P.res[i] });
    sets.push({ label: '殘差', data: pts, backgroundColor: 'rgba(44,62,122,.5)',
                pointRadius: 3, showLine: false });
    sets.push({ label: '分箱平均（觀察殘差趨勢）',
                data: w03binMean(P.fit, P.res, 12), borderColor: HC.tok.accent,
                borderWidth: 2.4, pointRadius: 0, showLine: true, fill: false });
    xt = '擬合值 ŷ'; yt = '殘差 e';
    plugs = [HC.hline(0, '殘差 = 0')];
  } else if (w03diagV === 1) {
    const sorted = st.slice().sort(function (a, b) { return a - b; });
    let lo = 0, hi = 0;
    for (let i = 0; i < P.n; i++) {
      const q = w03qnorm((i + 0.5) / P.n);
      pts.push({ x: q, y: sorted[i] });
      if (q < lo) lo = q; if (q > hi) hi = q;
      if (sorted[i] < lo) lo = sorted[i]; if (sorted[i] > hi) hi = sorted[i];
    }
    sets.push({ label: '學生化殘差的分位數', data: pts,
                backgroundColor: 'rgba(44,62,122,.5)', pointRadius: 3, showLine: false });
    sets.push({ label: '完全常態的話應該落在這條線上',
                data: [{ x: lo, y: lo }, { x: hi, y: hi }], borderColor: HC.tok.accent3,
                borderWidth: 2, borderDash: [6, 4], pointRadius: 0, showLine: true,
                fill: false });
    xt = '常態理論分位數'; yt = '學生化殘差';
  } else if (w03diagV === 2) {
    const sq = [];
    for (let i = 0; i < P.n; i++) {
      sq.push(Math.sqrt(Math.abs(st[i])));
      pts.push({ x: P.fit[i], y: sq[i] });
    }
    sets.push({ label: '√|學生化殘差|', data: pts, backgroundColor: 'rgba(26,107,74,.5)',
                pointRadius: 3, showLine: false });
    sets.push({ label: '分箱平均（上升趨勢提示異質變異）',
                data: w03binMean(P.fit, sq, 12), borderColor: HC.tok.accent,
                borderWidth: 2.4, pointRadius: 0, showLine: true, fill: false });
    xt = '擬合值 ŷ'; yt = '√|學生化殘差|';
  } else {
    for (let i = 0; i < P.n; i++) pts.push({ x: P.lev[i], y: st[i] });
    sets.push({ label: '每一筆觀測值', data: pts, backgroundColor: 'rgba(192,57,43,.5)',
                pointRadius: 3, showLine: false });
    xt = '槓桿值 hᵢ'; yt = '學生化殘差';
    plugs = [HC.hline(3, '＋3'), HC.hline(-3, '−3'),
             HC.vline(2 * 2 / P.n, '2 × (p+1)/n')];
  }
  HC.scatter('w03diagChart', { datasets: sets }, {
    interaction: { mode: 'nearest', intersect: true },
    scales: { x: { type: 'linear', title: { display: true, text: xt } },
              y: { title: { display: true, text: yt } } },
  });
  const c = HC.get('w03diagChart');
  HC.refs(c, plugs);
  let mr = 0, ml = 0;
  for (let i = 0; i < P.n; i++) {
    if (Math.abs(st[i]) > mr) mr = Math.abs(st[i]);
    if (P.lev[i] > ml) ml = P.lev[i];
  }
  $('w03diagN').textContent = String(P.n);
  $('w03diagB1').textContent = HC.fmt(P.b1, 4);
  $('w03diagRse').textContent = HC.fmt(P.rse, 3);
  $('w03diagR2').textContent = HC.fmt(P.r2, 4);
  $('w03diagMaxRes').textContent = HC.fmt(mr, 2) + (mr > 3 ? ' ← 超過 3！' : '');
  $('w03diagMaxLev').textContent = HC.fmt(ml, 4);
  $('w03diagAvgLev').textContent = HC.fmt(2 / P.n, 4);
  setStatus('w03diagStatus', P.label + ' · ' + w03diagVNames[w03diagV] + '：' + P.note);
}

/* ---------- P06 共線性膨脹器 ---------- */
let w03vifSvc = null;
function w03vifSetup() {
  w03vifSvc = HC.svg('w03vifSvg', { xd: [-11, 11], yd: [-11, 11], h: 330 });
  if (!w03vifSvc) return;
  w03vifSvc.grid(4, 4, { xtitle: 'β₁ 偏離最小平方解（單位：無共線性時的 SE）',
                         ytitle: 'β₂ 的偏離', xdec: 0, ydec: 0 });
  w03vifSvc.layer('band');
  w03vifSvc.layer('ell');
}
function w03vifJump() {
  if ($('w03vifRho')) $('w03vifRho').value = '99';
  w03vifDraw();
}
function w03vifHome() {
  if ($('w03vifRho')) $('w03vifRho').value = '0';
  w03vifDraw();
}
function w03vifDraw() {
  const s = w03vifSvc;
  if (!s) return;
  const el = $('w03vifRho');
  const rho = el ? parseInt(el.value, 10) / 100 : 0;
  const vif = 1 / Math.max(1e-4, 1 - rho * rho);
  const infl = Math.sqrt(vif);
  if ($('w03vifRhoV')) $('w03vifRhoV').textContent = HC.fmt(rho, 2);
  const gb = s.clearLayer('band');
  const half = 1.96 * infl;
  s.box(-half, s.yd[0], half, s.yd[1], { cls: 'band' }, gb);
  s.box(s.xd[0], -half, s.xd[1], half, { cls: 'band' }, gb);
  const g = s.clearLayer('ell');
  /* (XᵀX) ∝ [[1,ρ],[ρ,1]]：等高線 u² + 2ρuv + v² = L */
  [1, 4, 9].forEach(function (L, k) {
    s.poly(w03ellipse(1, rho, 1, L, 96), { cls: 'fit',
           stroke: 'rgba(192,57,43,' + (0.85 - 0.22 * k).toFixed(2) + ')', sw: 1.8 }, g);
  });
  s.dot(0, 0, { r: 5.5, fill: HC.tok.accent2, stroke: '#fff', sw: 1.6 }, g);
  s.txtPx(56, 22, '紅圈＝RSS 等高線（RSS 相同的係數組合）· 淡藍十字＝各自單獨的 95% 區間',
          { cls: 'axtitle' }, g);
  $('w03vifRhoR').textContent = HC.fmt(rho, 2);
  $('w03vifVif').textContent = HC.fmt(vif, 2);
  $('w03vifInfl').textContent = '× ' + HC.fmt(infl, 2);
  $('w03vifT').textContent = HC.pct(1 / infl, 1);
  $('w03vifEq').textContent = '只有 ' + HC.fmt(100 / vif, 1) + '% 的樣本數';
  const v = vif >= 10 ? '嚴重（VIF ≥ 10）' : (vif >= 5 ? '要處理（VIF ≥ 5）' : '沒有問題');
  $('w03vifVerdict').textContent = v;
  if (rho < 0.01) {
    setStatus('w03vifStatus', 'ρ = 0：等高線是正圓，兩個係數互不干擾，VIF = 1.00。'
      + '把滑桿往右推看看。');
  } else {
    setStatus('w03vifStatus', 'ρ = ' + HC.fmt(rho, 2) + ' → VIF = ' + HC.fmt(vif, 2)
      + '，SE 膨脹 ' + HC.fmt(infl, 2) + ' 倍、t 值只剩 ' + HC.pct(1 / infl, 0)
      + '。等高線沿著 β₁ = −β₂ 的方向被拉長：兩個係數的和還估得很準，各自是多少卻分不出來。'
      + (vif >= 10 ? ' 這已經是課本說要處理的程度了。' : ''));
  }
}

/* ---------- P05 交互作用：兩條線平不平行 ---------- */
let w03interSvc = null, w03interOn = true;
function w03interSetup() {
  w03interSvc = HC.svg('w03interSvg', { xd: [0, 195], yd: [-100, 2100], h: 340 });
  if (!w03interSvc) return;
  const s = w03interSvc;
  s.grid(4, 5, { xtitle: 'income（千美元）', ytitle: 'balance（美元）', xdec: 0, ydec: 0 });
  const g = s.layer('pts');
  const C = FRAMES_w03inter.credit;
  for (let i = 0; i < C.income.length; i++) {
    s.dot(C.income[i], C.bal[i], { r: 2.8, fill: C.stu[i] ? HC.tok.b : HC.tok.a,
                                   opacity: 0.5 }, g);
  }
  s.layer('lines');
}
function w03interToggle() {
  w03interOn = !w03interOn;
  const b = $('w03interBtn');
  if (b) {
    b.textContent = w03interOn ? '切換：拿掉交互作用' : '切換：加入交互作用';
    b.classList.toggle('off', !w03interOn);
  }
  w03interDraw();
}
function w03interHome() {
  if ($('w03interB3')) $('w03interB3').value = '-200';
  w03interDraw();
}
function w03interDraw() {
  const s = w03interSvc;
  if (!s) return;
  const C = FRAMES_w03inter.credit;
  const el = $('w03interB3');
  const b3raw = el ? parseInt(el.value, 10) / 100 : -2;
  let b0, b1, b2, b3;
  if (w03interOn) {
    b0 = C.inter.coef[0]; b1 = C.inter.coef[1]; b2 = C.inter.coef[2]; b3 = b3raw;
  } else {
    b0 = C.add.coef[0]; b1 = C.add.coef[1]; b2 = C.add.coef[2]; b3 = 0;
  }
  if ($('w03interB3v')) $('w03interB3v').textContent = HC.fmt(b3raw, 2);
  let rss = 0;
  for (let i = 0; i < C.income.length; i++) {
    const p = b0 + b1 * C.income[i] + b2 * C.stu[i] + b3 * C.income[i] * C.stu[i];
    rss += (C.bal[i] - p) * (C.bal[i] - p);
  }
  const g = s.clearLayer('lines');
  const x0 = s.xd[0], x1 = s.xd[1];
  s.poly([[x0, b0 + b1 * x0], [x1, b0 + b1 * x1]],
         { cls: 'fit', stroke: HC.tok.a, sw: 3 }, g);
  s.poly([[x0, b0 + b2 + (b1 + b3) * x0], [x1, b0 + b2 + (b1 + b3) * x1]],
         { cls: 'fit', stroke: HC.tok.b, sw: 3 }, g);
  s.txtPx(56, 22, w03interOn ? '有交互作用：兩條線不平行（斜率不同）'
                             : '無交互作用：兩條線平行（只有截距不同）',
          { cls: 'axtitle' }, g);
  $('w03interMode').textContent = w03interOn ? '有交互作用' : '無交互作用（平行）';
  $('w03interS0').textContent = HC.fmt(b1, 3);
  $('w03interS1').textContent = HC.fmt(b1 + b3, 3);
  $('w03interB3r').textContent = w03interOn ? HC.fmt(b3, 3) : '0（沒有這一項）';
  $('w03interRss').textContent = HC.fmt(rss / 1000, 1) + ' 千';
  $('w03interR2').textContent = HC.fmt(1 - rss / C.tss, 4);
  if (!w03interOn) {
    setStatus('w03interStatus', '無交互作用：兩條線平行，共同斜率 ' + HC.fmt(b1, 2)
      + '。意思是「收入每多一千美元，balance 平均多 ' + HC.fmt(b1, 2)
      + '」——學生跟非學生完全一樣。R² = ' + HC.fmt(1 - rss / C.tss, 4) + '。');
  } else {
    setStatus('w03interStatus', 'β₃ = ' + HC.fmt(b3, 2) + '：非學生的斜率 '
      + HC.fmt(b1, 2) + '、學生的斜率 ' + HC.fmt(b1 + b3, 2) + '。R² = '
      + HC.fmt(1 - rss / C.tss, 4) + '、RSS = ' + HC.fmt(rss / 1000, 1) + ' 千。'
      + (Math.abs(b3 + 2) < 0.06 ? '這就是最小平方解，RSS 在這裡最小。'
                                 : '把滑桿推回 −2.00 看 RSS 降到最低。'));
  }
}

/* ---------- P02 CI 帶與 PI 帶（講義的兩條公式） ---------- */
let w03bandSvc = null, w03bandDrawNo = 0;
function w03tq975(nu) {
  /* t 分布 0.975 分位數的 Cornish–Fisher 近似；nu ≥ 5 時誤差小於 0.03 */
  const z = 1.959964;
  return z + (z * z * z + z) / (4 * nu) + (5 * Math.pow(z, 5) + 16 * z * z * z + 3 * z) / (96 * nu * nu);
}
function w03bandSetup() {
  w03bandSvc = HC.svg('w03bandSvg', { xd: [0, 10], yd: [-12, 45], h: 330 });
  if (!w03bandSvc) return;
  w03bandSvc.grid(5, 5, { xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0 });
  ['pi', 'ci', 'pts', 'fit'].forEach(function (l) { w03bandSvc.layer(l); });
}
function w03bandRedraw() { w03bandDrawNo += 1; w03bandRender(); }
function w03bandReset() {
  w03bandDrawNo = 0;
  if ($('w03bandN')) $('w03bandN').value = '40';
  if ($('w03bandS')) $('w03bandS').value = '25';
  w03bandRender();
}
function w03bandRender() {
  const s = w03bandSvc;
  if (!s) return;
  const n = $('w03bandN') ? parseInt($('w03bandN').value, 10) : 40;
  const sig = $('w03bandS') ? parseInt($('w03bandS').value, 10) / 10 : 2.5;
  if ($('w03bandNv')) $('w03bandNv').textContent = n;
  if ($('w03bandSv')) $('w03bandSv').textContent = HC.fmt(sig, 1);
  const rand = HC.stat.lcg(4200 + w03bandDrawNo * 101 + n);
  const xs = HC.stat.seq(0.3, 9.7, n);
  const ys = xs.map(function (x) { return 2 + 3 * x + sig * HC.stat.normal(rand); });
  const f = HC.stat.ols(xs, ys);
  const mx = HC.stat.mean(xs);
  let sxx = 0;
  for (let i = 0; i < n; i++) sxx += (xs[i] - mx) * (xs[i] - mx);
  const t = w03tq975(n - 2);
  const grid = HC.stat.seq(0, 10, 61), ci = [], pi = [];
  grid.forEach(function (x) {
    const m = f.b0 + f.b1 * x, q = 1 / n + (x - mx) * (x - mx) / sxx;
    const hc = t * f.rse * Math.sqrt(q), hp = t * f.rse * Math.sqrt(1 + q);
    ci.push([x, m + hc, m - hc]);
    pi.push([x, m + hp, m - hp]);
  });
  s.area(pi, { cls: 'w03piband', fill: 'rgba(26,107,74,.18)' }, s.clearLayer('pi'));
  s.area(ci, { cls: 'w03ciband', fill: 'rgba(44,62,122,.35)' }, s.clearLayer('ci'));
  const gp = s.clearLayer('pts');
  for (let i = 0; i < n; i++) s.dot(xs[i], ys[i], { r: 2.6, fill: HC.tok.train, opacity: 0.7 }, gp);
  s.poly([[0, f.b0], [10, f.b0 + 10 * f.b1]], { cls: 'fit', sw: 2.4 }, s.clearLayer('fit'));
  const hc0 = t * f.rse / Math.sqrt(n), hp0 = t * f.rse * Math.sqrt(1 + 1 / n);
  $('w03bandNr').textContent = n;
  $('w03bandRse').textContent = HC.fmt(f.rse, 2);
  $('w03bandCi').textContent = '± ' + HC.fmt(hc0, 2);
  $('w03bandPi').textContent = '± ' + HC.fmt(hp0, 2);
  $('w03bandRatio').textContent = HC.fmt(hp0 / hc0, 1) + ' 倍';
  setStatus('w03bandStatus', 'n = ' + n + '、σ = ' + HC.fmt(sig, 1) + '：在 x 的平均處，CI 半寬 ± '
    + HC.fmt(hc0, 2) + '、PI 半寬 ± ' + HC.fmt(hp0, 2) + '。CI 隨 1/√n 縮小，PI 最窄也有 ±t·σ̂。');
}

/* ---------- P06 殘差圖的三種橫軸 ---------- */
const w03axisN = 60;
let w03axisSvc = null, w03axisMode = 'fit', w03axisShuffle = 0, w03axisD = null;
function w03axisMake() {
  const rand = HC.stat.lcg(7301);
  const xs = [], ys = [];
  for (let i = 0; i < w03axisN; i++) {
    const x = 0.3 + 9.4 * rand();
    xs.push(x);
    ys.push(2 + 0.8 * x + 2.5 * HC.stat.normal(rand));
  }
  const f = HC.stat.ols(xs, ys);
  const fit = xs.map(function (x) { return f.b0 + f.b1 * x; });
  const res = ys.map(function (y, i) { return y - fit[i]; });
  const order = xs.map(function (_, i) { return i; });
  w03axisD = { xs: xs, ys: ys, fit: fit, res: res, order: order, r2: f.r2 };
}
function w03axisSetup() {
  w03axisSvc = HC.svg('w03axisSvg', { xd: [0, 1], yd: [-10, 10], h: 320 });
  if (!w03axisSvc) return;
  w03axisMake();
  ['zero', 'pts', 'trend'].forEach(function (l) { w03axisSvc.layer(l); });
}
function w03axisSet(mode) { w03axisMode = mode; w03axisDraw(); }
function w03axisShuffleOrder() {
  if (!w03axisD) return;
  w03axisShuffle += 1;
  const rand = HC.stat.lcg(9100 + w03axisShuffle * 37);
  const o = w03axisD.order;
  for (let i = o.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1)), tmp = o[i];
    o[i] = o[j]; o[j] = tmp;
  }
  w03axisMode = 'idx';
  w03axisDraw();
}
function w03axisReset() { w03axisShuffle = 0; w03axisMake(); w03axisMode = 'fit'; w03axisDraw(); }
function w03axisDraw() {
  const s = w03axisSvc, D = w03axisD;
  if (!s || !D) return;
  let hx, title, lo, hi, label;
  if (w03axisMode === 'idx') {
    const pos = new Array(D.order.length);
    D.order.forEach(function (idx, k) { pos[idx] = k + 1; });
    hx = pos; title = '觀測編號 i（目前的排列順序）'; lo = 0; hi = w03axisN + 1; label = '觀測編號 i';
  } else if (w03axisMode === 'y') {
    hx = D.ys; title = '觀測值 y'; label = '觀測值 y';
    lo = Math.min.apply(null, D.ys) - 1; hi = Math.max.apply(null, D.ys) + 1;
  } else {
    hx = D.fit; title = '擬合值 ŷ'; label = '擬合值 ŷ';
    lo = Math.min.apply(null, D.fit) - 1; hi = Math.max.apply(null, D.fit) + 1;
  }
  s.domain([lo, hi], [-10, 10]);
  s.grid(5, 4, { xtitle: title, ytitle: '殘差 e', xdec: w03axisMode === 'idx' ? 0 : 1, ydec: 0 });
  s.seg(lo, 0, hi, 0, { cls: 'truef', sw: 1.4 }, s.clearLayer('zero'));
  const gp = s.clearLayer('pts');
  for (let i = 0; i < w03axisN; i++) s.dot(hx[i], D.res[i], { r: 3.6, fill: HC.tok.train, opacity: 0.8 }, gp);
  const f = HC.stat.ols(hx, D.res);
  s.poly([[lo, f.b0 + f.b1 * lo], [hi, f.b0 + f.b1 * hi]], { cls: 'fit', sw: 2.2 }, s.clearLayer('trend'));
  const mx = HC.stat.mean(hx), my = HC.stat.mean(D.res);
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < w03axisN; i++) {
    sxy += (hx[i] - mx) * (D.res[i] - my);
    sxx += (hx[i] - mx) * (hx[i] - mx);
    syy += (D.res[i] - my) * (D.res[i] - my);
  }
  const corr = sxy / Math.sqrt(sxx * syy), r2 = D.r2;
  $('w03axisModeV').textContent = label;
  $('w03axisCorr').textContent = HC.fmt(corr, 3);
  $('w03axisSlope').textContent = HC.fmt(f.b1, 3);
  $('w03axisR2').textContent = HC.fmt(r2, 3);
  if (w03axisMode === 'y') {
    $('w03axisPred').textContent = '相關 √(1−R²) = ' + HC.fmt(Math.sqrt(1 - r2), 3) + '、斜率 1−R² = ' + HC.fmt(1 - r2, 3);
    setStatus('w03axisStatus', '橫軸是 y：相關係數 ' + HC.fmt(corr, 3) + ' 正好是 √(1−R²)，斜率 ' + HC.fmt(f.b1, 3)
      + ' 正好是 1−R²。這條上升趨勢是內建的假象，不是模型誤設。');
  } else if (w03axisMode === 'idx') {
    $('w03axisPred').textContent = '沒有理論值：編號不帶資訊';
    setStatus('w03axisStatus', '橫軸是觀測編號：這份橫斷面資料的編號沒有意義。再按一次「洗牌觀測順序」，'
      + '這張圖會整個變樣，ŷ 與 y 兩張圖則完全不變（已洗牌 ' + w03axisShuffle + ' 次）。');
  } else {
    $('w03axisPred').textContent = '相關 0、斜率 0（正交）';
    setStatus('w03axisStatus', '橫軸是 ŷ：殘差與擬合值正交，最小平方斜率 ' + HC.fmt(f.b1, 3)
      + '、相關係數 ' + HC.fmt(corr, 3) + '，只剩浮點誤差。看到的任何形狀都是真的。');
  }
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.bar / HC.line / HC.scatter 在 Chart 未載入時本來就安全地回傳 null。 */
w03dragSetup();
w03rssSetup();
w03sampSetup();
w03vifSetup();
w03interSetup();
w03bandSetup();
w03axisSetup();
w03dragReset();
w03sampReset();
w03vifDraw();
w03interDraw();
w03bandRender();
w03axisDraw();
HC.ready(function () {
  w03diagDraw();
  w03sampHist();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


# Approved reading-flow organization; keep all source-backed detail content.
from reading_flow_ch1_6 import organize
BODIES, PAGEJS = organize(3, BODIES, PAGEJS)

if __name__ == "__main__":
    apply("linear_regression", BODIES, PAGEJS, frames())
