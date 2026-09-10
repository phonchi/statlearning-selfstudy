#!/usr/bin/env python3
"""statistical_learning.html（ISLP 第 2 章）完整自學充實。冪等。

內容依據：講義 02_Statistical_Learning.pdf（41 頁）、Ch02-statlearn-lab-zh.ipynb、
ISLP 第 2 章（書上 p.16–66）、ESL §7.3（偏差–變異拆解）。

第 2 章的 lab 是「Python 入門」，裡面沒有任何統計學習的數字可以抄，所以：
  · .deck-extra 一律逐字取 lab 的程式碼與實跑輸出，用途是「這一節的計算需要哪個工具」；
  · 所有圖表的數字由 tools/frames/gen_statlearn.py 在固定種子下模擬產生，
    對照的是 ISLP 圖 2.9／2.12／2.13／2.15–2.17 的形狀與量級，不是它們的原始資料。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import proof
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 2
LAB = "Ch02-statlearn-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_statlearn.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_statlearn.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_statlearn.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>第 1 章介紹了統計學習的用途。這一章要把它<strong>寫成一條式子</strong>，
  之後九章的方法都可以用這條式子來理解：</p>

  $$Y = f(X) + \\varepsilon$$

  <p>$Y$ 是你想預測的那個東西（銷售量、油耗、會不會違約），
  $X = (X_1, \\dots, X_p)$ 是你手上量得到的那些變數。
  $f$ 是「$X$ 對 $Y$ 提供的系統性資訊」——固定不變、真實存在，但<strong>你永遠看不到它</strong>。
  $\\varepsilon$ 是剩餘的隨機誤差，滿足 $E[\\varepsilon\\mid X]=0$。</p>

  <p>整章只做兩件事：<strong>（一）怎麼估 f</strong>、<strong>（二）怎麼判斷估得好不好</strong>。
  第二件事會影響方法的選擇，因為「在訓練資料上擬合得好」
  不代表「在新資料上也預測得準」。</p>

{info("為什麼一定要有 ε 這一項", '''把它拿掉，式子就變成 Y = f(X)，等於宣稱
  「只要知道 X 就能<strong>完全</strong>算出 Y」。這在真實世界幾乎不成立：<br>
  <strong>1. 沒量到的變數：</strong>病人對藥物的反應還跟基因、當天狀況有關，而你沒有那些欄位。<br>
  <strong>2. 無法量的變異：</strong>同一批藥的製造差異、同一個人不同天的身體狀況。<br>
  <strong>3. 量測誤差：</strong>儀器本身就有雜訊。<br>
  ε 包含這些誤差來源。它的變異數 Var(ε) 決定可達到的誤差下限。這是下一節的主題。''')}

  <p>先把兩個常見的目的分清楚，因為它們會導向完全不同的方法選擇：</p>

{table(["", "預測（prediction）", "推論（inference）"],
       [["你要什麼", "Ŷ 愈接近 Y 愈好", "描述 X 與 Y 的條件關聯"],
        ["f̂ 可以是黑盒子嗎", "可以，重點是預測準確度", "不行，必須看得懂"],
        ["典型問題", "這封信是垃圾郵件嗎？這支股票明天多少？",
         "控制其他媒體後，哪種廣告仍與銷售量相關？價格與銷量如何一起變動？"],
        ["偏好的模型", "彈性高的（提升法、神經網路）", "可解釋的（線性模型、lasso）"],
        ["本章對應", "§2.2 怎麼量準不準", "§2.1.3 彈性換掉了解釋力"]])}

  <p>兩者也可以同時要。房價模型既想知道「靠河的房子貴多少」（推論），
  也想知道「這間房子被高估了嗎」（預測）。只是通常得在中間選一個折衷點。</p>

  <h3 id="dx-load">講義完整實作：把 (X, Y) 讀進 Python</h3>
  <p>第 2 章的 lab 是 Python 入門，所以下面每一張卡的定位是
  <strong>「這一節的計算需要哪一個工具」</strong>。先從最基本的開始：把資料讀成一張表，
  才有 X 和 Y 可以談。</p>

{card("講義 02 · 讀 Auto 並處理遺漏值", lab_code(CH, 195), lab_output(CH, 195),
      src=src("195"),
      note="<code>Auto.data</code> 裡的遺漏值是用 <code>?</code> 編碼的，"
           "不告訴 <code>pd.read_csv()</code> 這件事，整個 <code>horsepower</code> 欄位就會被"
           "讀成字串（lab 的 Auto 匯入範例示範了這個結果）。"
           "<code>na_values=['?']</code> 之後才加得起來，總和是 <strong>40952.0</strong>。")}

{card("講義 02 · n 與 p 到底是多少", lab_code(CH, 197) + "\n\n" + lab_code(CH, 199),
      lab_output(CH, 199), src=src("197、199"),
      note="原始資料 397 列、9 欄；丟掉含遺漏值的 5 列之後是 <strong>392 × 9</strong>。"
           "如果要用 <code>mpg</code> 當 Y、其他數值欄當 X，那就是 n = 392、"
           "p = 7（扣掉 <code>mpg</code> 與文字欄 <code>name</code>）。"
           "本章的符號約定就是這樣對上真實資料的。")}

{quiz("qEst", "QUIZ · Y = f(X) + ε",
      "下列哪一句話正確描述了式子 <em>Y</em> = <em>f</em>(<em>X</em>) + ε 裡的 <em>f</em>？",
      [(True, "f 是固定但未知的函數，代表 X 對 Y 提供的系統性資訊",
        "對。<strong>固定</strong>（不隨樣本改變）、<strong>未知</strong>（我們只能估）、"
        "<strong>系統性</strong>（隨機的那部分被丟進 ε）。整本書都在找它的估計 f̂。"),
       (False, "f 是我們擬合出來的模型，會隨著訓練資料改變",
        "不對，那是 <strong>f̂</strong>（f hat）。f 是真實世界的那個函數，換一份訓練資料它不會變；"
        "會變的是我們的估計 f̂——而「它變多少」正是後面「變異」的定義。"),
       (False, "f 包含了所有影響 Y 的因素，所以 ε 只是量測誤差",
        "不對。f 只用得到 <em>X 裡面有的</em>資訊。沒量到的變數影響再大，也只能被歸進 ε，"
        "所以 ε 也包含未量到的變數所造成的變動。")])}
"""

# 講義 02 · p.11 的條件均方誤差推導。用 raw string 保留 LaTeX，
# 不必為了 f-string 把每個大括號加倍。
IRR_PROOF = qa("完整推導", [(
    r"把 $E[(Y - \hat f(x))^2 \mid X = x]$ 一步一步拆成 $[f(x) - \hat f(x)]^2 + \mathrm{Var}(\varepsilon)$",
    r"""<p><strong>前提。</strong>模型是 $Y = f(X) + \varepsilon$，其中
    $E[\varepsilon \mid X] = 0$、$\mathrm{Var}(\varepsilon \mid X) = \sigma^2$。
    把 $X = x$ 固定住，並且把 $\hat f$ 當成<strong>已經訓練好、不再變動</strong>的函數。
    於是 $f(x)$ 與 $\hat f(x)$ 都只是常數，式子裡唯一還在隨機的東西只有 $\varepsilon$。</p>

    <p><strong>第 1 步：把 $Y$ 換掉。</strong>令 $d(x) = f(x) - \hat f(x)$，它是一個常數：</p>
    $$Y - \hat f(x) = f(x) + \varepsilon - \hat f(x) = d(x) + \varepsilon$$

    <p><strong>第 2 步：平方展開。</strong></p>
    $$\left(Y - \hat f(x)\right)^2 = d(x)^2 + 2\,d(x)\,\varepsilon + \varepsilon^2$$

    <p><strong>第 3 步：取條件期望。</strong>期望是線性的，常數提得出來：</p>
    $$E\left[(Y - \hat f(x))^2 \mid X = x\right]
      = d(x)^2 + 2\,d(x)\,E[\varepsilon \mid X = x] + E[\varepsilon^2 \mid X = x]$$

    <p><strong>第 4 步：把後面兩項算掉。</strong>中間那一項因為
    $E[\varepsilon \mid X = x] = 0$ 而整項消失。最後一項用同一個條件：</p>
    $$E[\varepsilon^2 \mid X = x]
      = \mathrm{Var}(\varepsilon \mid X = x) + \left(E[\varepsilon \mid X = x]\right)^2
      = \sigma^2 + 0 = \mathrm{Var}(\varepsilon)$$

    <p><strong>結論。</strong>兩項留下來，正好就是講義寫的那一行：</p>
    $$E\left[(Y - \hat f(x))^2 \mid X = x\right]
      = \underbrace{\left[f(x) - \hat f(x)\right]^2}_{\text{可縮減}}
      + \underbrace{\mathrm{Var}(\varepsilon)}_{\text{不可縮減}}$$

    <p><strong>怎麼讀它。</strong>第一項是你動得到的：換方法、加資料、加變數都會讓它變小，
    理論上可以趨近 0。第二項完全不受方法影響，就算 $\hat f = f$ 也一樣在。</p>

    <p>另外請注意「$\hat f$ 固定不動」這個前提。如果把<strong>訓練資料本身的隨機性</strong>
    也算進來（每換一份訓練集就得到不同的 $\hat f$），第一項還會再拆成偏差平方與變異兩塊，
    那是本頁後面<a href="#biasvar">偏差–變異拆解</a>那一節的事。</p>""")])


# ── P01 irreducible ───────────────────────────────────────────────────
BODIES["irreducible"] = f"""
  <p>先考慮一個問題：<strong>如果你猜對了 f，誤差會是 0 嗎？</strong>
  不會。假設 $\\hat f$ 與 $X$ 都固定，只有 $\\varepsilon$ 在變動，那麼</p>

  $$E\\left(Y - \\hat Y\\right)^2
    = \\underbrace{{\\left[f(X) - \\hat f(X)\\right]^2}}_{{\\text{{可縮減}}}}
    + \\underbrace{{\\mathrm{{Var}}(\\varepsilon)}}_{{\\text{{不可縮減}}}}$$

  <p>這是 ISLP 式 2.3。左邊是你會量到的平均平方誤差，右邊拆成兩塊：</p>

  <ul>
    <li><strong>可縮減誤差</strong>（reducible error）：$\\hat f$ 沒學對 $f$ 的部分。
    換更合適的方法、蒐集更多資料、加入有用的變數，都能減少這部分誤差。</li>
    <li><strong>不可縮減誤差</strong>（irreducible error）：$\\mathrm{{Var}}(\\varepsilon)$。
    <strong>就算你得到 $\\hat f = f$，這一塊還在。</strong>
    因為 $Y$ 本來就有一部分變異跟 $X$ 沒關係。</li>
  </ul>

  <p>講義第 11 頁把同一件事寫成<strong>條件版本</strong>——把 $X = x$ 固定住，
  只看這一個點上的均方誤差。這是後面每一章都會再用到的一行：</p>

  $$E\\left[\\left(Y - \\hat f(x)\\right)^2 \\mid X = x\\right]
    = \\left[f(x) - \\hat f(x)\\right]^2 + \\mathrm{{Var}}(\\varepsilon)$$

{IRR_PROOF}

  <p>下面的元件把這兩塊分開來看：真實的 $f$ 固定不動，只有雜訊的 $\\sigma$ 在變。
  在 $x$ 這條垂直線上，$Y$ 有一整個分佈，觀測值相對於中心的上下變動就是 $\\varepsilon$。</p>

{viz(svg("w02irrSvg", 320),
     [info_card("怎麼玩這個元件",
                '真實的 f（綠色虛線）<strong>固定不動</strong>，只有雜訊的 σ 在變。'
                '綠色淡帶是 f ± σ 的範圍。拖滑桿把 σ 拉大，觀察資料點如何變得更分散——'
                '而 f 一動也沒動。', "ISLP 式 2.3"),
      rows_card("期望測試誤差的組成",
                [("σ（雜訊的標準差）", "1.0", "w02irrSigma"),
                 ("Var(ε) = σ² ← 下限", "1.00", "w02irrVar"),
                 ("完美 f 的期望測試 MSE", "—", "w02irrPerfect"),
                 ("線性 f̂ 的期望測試 MSE", "—", "w02irrLin"),
                 ("獨立測試網格上的可縮減部分", "—", "w02irrGap")]),
      info_card("期望誤差如何計算",
                '線性模型先在訓練樣本上擬合，再到<strong>獨立而密集的 x 網格</strong>計算'
                '$E[(Y-\\hat f(X))^2]=\\sigma^2+E[(f(X)-\\hat f(X))^2]$。')],
     "w02irrStatus", "拖動 σ 滑桿，看期望測試誤差的不可縮減下限跟著抬高。",
     '<div class="slider-row" style="flex:1;min-width:190px;">'
     '<span class="slider-label">σ</span>'
     '<input type="range" id="w02irrSig" min="0.2" max="2" step="0.1" value="1" '
     'oninput="w02irrDraw()">'
     '<span class="slider-val" id="w02irrSigVal">1.0</span></div>'
     '<button class="btn btn-toggle" onclick="w02irrToggleLin()">切換線性 f̂</button>',
     provenance=("simulation", "固定訓練樣本；期望誤差在獨立 x 網格上計算"))}

  <p>到這裡還有一個坑沒有填：我們一直講「真實的 $f$」，可是
  <strong>$f$ 本身到底是什麼？</strong>在 $X = x$ 這一點上，$f(x)$ 要取哪個數字才算最好？
  下一節先把它定義清楚、證明它真的最好，再處理「拿不到它的時候怎麼辦」。</p>

  <h3 id="dx-eps">講義完整實作：親手做出一個 Y = f(X) + ε</h3>

{card("講義 02 · 雜訊讓相關係數到不了 1", lab_code(CH, 76) + "\n" + lab_code(CH, 78),
      lab_output(CH, 78), src=src("74、76、78"),
      note="lab 的相關係數範例先產生 50 個標準常態的 <code>x</code>。這裡的 "
           "<code>y = x + N(50, 1)</code> 意思是<strong>真實的 f(x) = x + 50，一點都沒錯</strong>，"
           "而 ε 是標準差 1 的常態。既然 f 完全正確，相關係數為什麼不是 1？"
           "因為 Var(x) = 1、Var(ε) = 1，理論相關是 1/√2 ≈ 0.707，"
           "實測 <strong>0.787</strong>（50 筆的抽樣波動）。"
           "<strong>雜訊把相關係數壓在 1 以下；但注意「相關係數離 1 的差距」"
           "本身不是不可縮減誤差——量綱都不一樣。</strong>這一題裡平方誤差意義下的"
           "不可縮減部分是 Var(ε) = 1。")}

{card("講義 02 · 用樣本變異數估 Var(ε)", lab_code(CH, 84) + "\n" + lab_code(CH, 85),
      lab_output(CH, 85), src=src("84、85"),
      note="下一個變異數範例，把 <code>y</code> 重新設成 10 個標準常態樣本；它不是前一張卡的 x 加雜訊。三個寫法給出同一個數字 <strong>2.7243406406465125</strong>，"
           "因為它們算的是同一件事：<code>np.mean((y - y.mean())**2)</code>。"
           "MSE 也是「平方的平均」，同一個動作。"
           "注意 <code>np.var()</code> 預設除以 n 而不是 n − 1（看 <code>ddof</code> 參數）——"
           "估 Var(ε) 時這個差別在小樣本上是會被抓出來的。")}

{qa("觀念釐清", [
    ("Q：「不可縮減誤差」到底不可縮減在哪？多蒐集資料有用嗎？多加變數呢？",
     "<p><strong>增加同類樣本不會改變不可縮減誤差；加入有用變數則會改變 ε 的定義，讓其中一部分能由 X 解釋。</strong></p>"
     "<p>不可縮減誤差是 $\\mathrm{Var}(\\varepsilon)$，而 $\\varepsilon$ 的定義是 "
     "$Y - E[Y \\mid X]$，也就是「在給定這組 X 之後，Y 還剩下的變異」。"
     "資料量 n 變大只會讓你把 f 估得更準（減少可縮減誤差），"
     "$\\mathrm{Var}(\\varepsilon)$ 是母體的性質，跟你抽了幾筆完全無關。</p>"
     "<p>加變數就不一樣了。假設病人的反應其實還跟基因型有關，而你原本沒量。"
     "那部分變異現在被塞在 $\\varepsilon$ 裡。一旦把基因型加進 X，"
     "條件期望值換成了 $E[Y \\mid X, \\text{基因型}]$——它能解釋的變異<strong>只多不少</strong>，"
     "剩下的殘差因此只小不大：$E\\big[\\mathrm{Var}(Y \\mid X, \\text{基因型})\\big] \\le "
     "E\\big[\\mathrm{Var}(Y \\mid X)\\big]$。"
     "（新變數真的帶進資訊時才會嚴格變小；毫無關係的變數只會讓等號成立。）所以嚴格說法是："
     "<strong>不可縮減誤差的下限由你使用的這組 X 決定。</strong></p>"
     "<p>實務上的意義：如果經重複評估得到的測試風險已逼近你估計的 $\\mathrm{Var}(\\varepsilon)$，"
     "可優先考慮蒐集新變數，再評估是否需要更換模型或調整參數。"),
])}

{quiz("qIrr", "QUIZ · 兩種誤差",
      "你把模型從線性迴歸換成一個非常彈性的方法，母體的期望測試 MSE 從 5.2 降到 2.4。"
      "已知 Var(ε) = 2.0。下列哪個判斷最合理？",
      [(True, "可縮減誤差從約 3.2 降到約 0.4，剩下的空間已經很小，可優先考慮蒐集新變數",
        "對。期望測試 MSE 減掉 Var(ε) 就是可縮減那一塊：5.2 − 2.0 = 3.2 → 2.4 − 2.0 = 0.4。"
        "已經減少 87.5%，可縮減的空間剩下 0.4，繼續加彈性最多也只能再拿回這麼多。"),
       (False, "還能再降到 0，因為彈性可以無限提高",
        "不對。三項拆解裡 Var(ε) = 2.0 是加在最後的常數，"
        "<strong>母體的期望測試 MSE 不可能低於 2.0</strong>，不管方法多彈性。"
        "訓練 MSE 才有辦法被壓到接近 0，但那是另一回事。"),
       (False, "Var(ε) = 2.0 表示資料品質太差，應該重新蒐集同樣的資料",
        "方向錯了。重新蒐集<strong>同樣的變數</strong>不會改變 Var(ε)，它是母體的性質。"
        "要壓低它得<strong>多量一些變數</strong>，讓原本歸入 ε 的系統性成分能由模型解釋。")])}
"""

# ── P02 regfunc（講義 02 · p.10–12） ──────────────────────────────────
# 這一節與下一節都用 raw string ＋ 串接，不用 f-string，
# 這樣 LaTeX 的大括號可以照原樣寫。
REG_PROOF = qa("完整證明", [(
    r"證明：在每一點 $X = x$ 上，$c = E[Y \mid X = x]$ 讓 $E[(Y - c)^2 \mid X = x]$ 最小",
    r"""<p><strong>要證的事。</strong>對任意函數 $f$，在每一點 $X = x$ 上都有</p>
    $$E\left[(Y - f(X))^2 \mid X = x\right] \;\ge\; E\left[(Y - \mu(x))^2 \mid X = x\right],
      \qquad \mu(x) = E[Y \mid X = x]$$

    <p><strong>第 0 步：把「對所有函數」降級成「對一個數字」。</strong>
    $X = x$ 固定之後，$f(X)$ 就只是一個數字 $f(x)$，不再是函數。
    所以「在所有函數裡找最好的」可以拆成「在每一點各自找最好的常數 $c = f(x)$」。
    只要每一點的最佳常數都是 $\mu(x)$，把這些點串起來的那個函數就是最佳函數。
    這正是講義那句<strong>「在所有函數上、在每一個 $X = x$ 點上」</strong>的意思。</p>

    <p><strong>第 1 步：加一項、減一項。</strong>硬把 $\mu(x)$ 塞進去：</p>
    $$Y - c = \underbrace{\left(Y - \mu(x)\right)}_{\text{隨機，條件期望 } 0}
      + \underbrace{\left(\mu(x) - c\right)}_{\text{常數}}$$
    <p>左邊那一塊的條件期望確實是 0：$E[Y - \mu(x) \mid X = x] = \mu(x) - \mu(x) = 0$。
    這就是整個證明的樞紐。</p>

    <p><strong>第 2 步：平方展開，取條件期望。</strong></p>
    $$E\left[(Y - c)^2 \mid X = x\right]
      = E\left[(Y - \mu(x))^2 \mid X = x\right]
      + 2\left(\mu(x) - c\right)\underbrace{E\left[Y - \mu(x) \mid X = x\right]}_{=\,0}
      + \left(\mu(x) - c\right)^2$$

    <p><strong>第 3 步：交叉項歸零。</strong>剩下乾乾淨淨的兩項：</p>
    $$E\left[(Y - c)^2 \mid X = x\right]
      = \underbrace{\mathrm{Var}\left(Y \mid X = x\right)}_{\text{跟 } c \text{ 完全無關}}
      + \underbrace{\left(\mu(x) - c\right)^2}_{\ \ge\ 0}$$

    <p><strong>第 4 步：讀式子。</strong>第一項是資料本身的條件變異，你挑什麼 $c$ 都改不動它；
    第二項是一個平方，最小值 0 只在 $c = \mu(x)$ 時取到，而且只有這一點取到。所以</p>
    $$\arg\min_{c} E\left[(Y - c)^2 \mid X = x\right] = \mu(x) = E[Y \mid X = x]$$
    <p>順帶得到一件事：<strong>能達到的最小值就是 $\mathrm{Var}(Y \mid X = x)$</strong>，
    也就是上一節的不可縮減誤差 $\mathrm{Var}(\varepsilon)$。兩節在這裡接起來了。</p>

    <p><strong>第 5 步：從一點推到全部。</strong>上式對每一個 $x$ 分別成立，
    所以函數 $f^{*}(x) = E[Y \mid X = x]$ 在每一點都不輸給任何其他函數。
    要全域版本就再對 $X$ 取一次期望（全期望公式）：</p>
    $$E\left[(Y - f(X))^2\right] = E\Big[\,E\left[(Y - f(X))^2 \mid X\right]\Big]$$
    <p>括號裡的東西逐點被 $f^{*}$ 最小化，外面再取期望當然也最小。$\blacksquare$</p>

    <p><strong>換個誤差就換個答案。</strong>如果改用絕對誤差
    $E\left[\,\left|Y - c\right| \mid X = x\right]$，最佳的 $c$ 會變成條件<strong>中位數</strong>。
    所以「取平均」不是天經地義，是<strong>平方誤差</strong>挑出來的。
    這也解釋了為什麼本課後面量準確度時，回歸看 MSE、分類看錯誤率——
    量尺不同，最佳預測就不同。</p>""")])

BODIES["regfunc"] = "".join([
    r"""
  <p>上一節一直在講「真實的 $f$」，但沒說 $f$ 在某一點上該取哪個數字。
  講義第 10 頁用一個非常具體的問題把答案逼出來：手上的資料裡，
  $X = 4$ 的地方有<strong>一整群</strong>不同的 $Y$，而你只能給一個預測值。要給哪一個？</p>
""",
    info("答案：取那一群 Y 的平均",
         """f(4) = E(Y | X = 4)，也就是「在 X = 4 的條件下，Y 的平均值」。
  每個 x 都這樣做，串起來的那個函數就叫<strong>迴歸函數</strong>（regression function）。"""),
    r"""
  $$f(x) = E\left[Y \mid X = x\right]$$

  <p>$X$ 是向量時完全一樣，只是條件多掛幾個（講義第 11 頁）：</p>

  $$f(x) = f(x_1, x_2, x_3) = E\left[Y \mid X_1 = x_1,\, X_2 = x_2,\, X_3 = x_3\right]$$

  <p>問題來了：為什麼是<strong>平均</strong>？中位數不行嗎？眾數不行嗎？
  行不行取決於你用什麼量尺算帳，而這門課的回歸量尺是平方誤差。
  講義第 11 頁那一行講的就是這件事：</p>
""",
    info("講義第 11 頁怎麼說",
         """就<strong>均方預測誤差</strong>而言，理想的（也就是最佳的）$Y$ 的預測函數是
  <strong>f(x) = E(Y | X = x)</strong>：在所有函數之中、在每一個 X = x 點上，
  它讓 E[(Y − f(X))² | X = x] 最小。<br>
  也就是說：在平方誤差之下，條件期望值不是「一個還不錯的選擇」，
  而是<strong>所有函數裡最好的那一個</strong>——沒有任何函數能贏過它。下面把它證出來。"""),
    REG_PROOF,
    r"""
  <p><strong>如果資料點夠多，事情就簡單得多。</strong>
  假設 $X = 4$ 這個位置真的躺著幾百筆觀測，那你什麼模型都不用建：
  把那幾百筆的 $y$ 平均起來，就是 $E[Y \mid X = 4]$ 的<strong>估計</strong>，
  而它要估的那個東西，照剛才的證明就是平方誤差下最好的預測。
  獨立抽樣、變異數有限時，鄰域內筆數 $m$ 愈多，樣本平均就愈接近母體的條件期望。</p>

  <p>要說清楚的是：<strong>樣本平均本身還不是「最佳」，它只是最佳解的估計。</strong>
  在 $X = 4$ 這一點上用 $m$ 筆的平均 $\bar y_m$ 去預測一筆新的 $Y$，期望平方誤差是</p>

  $$E\left[(Y_{\text{new}} - \bar y_m)^2 \mid X = 4\right]
    = \underbrace{\tau^2}_{\text{不可縮減}} + \underbrace{\frac{\tau^2}{m}}_{\text{估計誤差}},
    \qquad \tau^2 = \mathrm{Var}(Y \mid X = 4)$$

  <p>第二項要到 $m \to \infty$ 才消失。所以正確的說法是：
  <strong>資料夠多的時候，最佳解可以直接照定義估出來，不需要任何模型假設</strong>——
  這已經夠強了，強到值得把它當成整章的參照點。</p>

  <p>麻煩在於「夠多」幾乎不會發生。講義第 12 頁下一頁就潑冷水：</p>
""",
    info("講義第 12 頁：恰好落在 X = 4 的資料通常寥寥無幾，甚至一筆都沒有！",
         """X 是連續變數時，恰好落在 4 的機率是 0；就算 X 是離散的，
  只要多掛幾個維度，每一格的資料筆數也會很快掉到 1 筆或 0 筆。
  <strong>所以 E(Y | X = x) 這個定義沒辦法照字面計算。</strong>
  不是它不對，是你手上沒有那麼多剛好落在 x 的資料。""", "warm"),
    r"""
  <p>那就把定義放鬆：不要求「剛好等於 $x$」，改成「離 $x$ 夠近」。
  這就是<strong>最近鄰平均</strong>（nearest neighbor averaging），講義第 12 頁的式子：</p>

  $$\hat f(x) = \mathrm{Ave}\left(Y \mid X \in N(x)\right)$$

  <p>$N(x)$ 是 $x$ 的一個<strong>鄰域</strong>——可以是「離 $x$ 最近的 $k$ 筆」，
  也可以是「$\left|X - x\right| \le h$ 的那些筆」。這一步看起來只是權宜之計，
  其實是整個非參數式方法的原型：第 7 章的核平滑與樣條、第 8 章的樹、
  第 4 章的 KNN 分類，骨子裡都是它的變形。</p>

  <p>放鬆是有代價的，而且代價正好是一組拉鋸。下面這個元件讓你親手拉：</p>
""",
    viz(svg("w02nbrSvg", 330),
        [info_card("怎麼玩這個元件",
                   """綠虛線是真實的 f（跟上一節同一條），灰點是 200 筆觀測。
  紫線是你要預測的位置 x₀，黃帶是鄰域 |X − x₀| ≤ h，帶子裡的點會亮起來。
  橘色橫線是<strong>鄰域內 y 的平均</strong>，也就是 f̂(x₀)。<br>
  <strong>先把 h 拉到最小</strong>：鄰域裡只剩兩三個點，橘線會抖得很厲害——這是變異。
  <strong>再把 h 拉到最大</strong>：點很多、橘線很穩，但它開始明顯偏離綠虛線——這是偏差，
  因為鄰域一大，裡面的 f 就不再近似常數了。""", "講義 02 · p.12"),
         rows_card("目前這個鄰域",
                   [("鄰域寬度 h", "0.80", "w02nbrHVal2"),
                    ("鄰域內的點數 m", "—", "w02nbrM"),
                    ("鄰域平均 f̂(x₀)", "—", "w02nbrAve"),
                    ("真值 f(x₀)", "—", "w02nbrTrue"),
                    ("差距 |f̂ − f|", "—", "w02nbrErr"),
                    ("平均值的標準誤 σ/√m", "—", "w02nbrSe")]),
         info_card("為什麼這正是後面偏差–變異的伏筆",
                   """h 小 → m 小 → σ/√m 大 → <strong>變異大</strong>。<br>
  h 大 → 鄰域裡的 f 不再是常數 → <strong>偏差大</strong>。<br>
  沒有哪個 h 能同時把兩邊壓下去，只能挑一個折衷點。
  這門課後面所有「選 K、選 df、選 λ」的動作，都是同一場拉鋸的不同外衣。""")],
        "w02nbrStatus", "拖動 h 看鄰域平均如何在「抖」與「偏」之間擺盪。",
        '<div class="slider-row" style="flex:1;min-width:200px;">'
        '<span class="slider-label">鄰域寬度 h</span>'
        '<input type="range" id="w02nbrH" min="0.15" max="3.5" step="0.05" value="0.8" '
        'oninput="w02nbrDraw()">'
        '<span class="slider-val" id="w02nbrHVal">0.80</span></div>'
        '<div class="slider-row" style="flex:1;min-width:200px;">'
        '<span class="slider-label">目標位置 x₀</span>'
        '<input type="range" id="w02nbrX0" min="1" max="9" step="0.1" value="4" '
        'oninput="w02nbrDraw()">'
        '<span class="slider-val" id="w02nbrX0Val">4.0</span></div>',
        provenance=("simulation", "固定種子的 200 筆樣本，真實 f 與上一節同一條")),
    r"""
  <p>最近鄰平均能用的前提是「鄰域夠小，小到裡面的 $f$ 幾乎是常數；
  同時鄰域裡又有夠多的點，多到平均值不抖」。一維的時候這兩件事很容易同時成立。
  下一節要說的是：<strong>維度提高後，要同時做到這兩點通常需要更多資料。</strong></p>
""",
    quiz("qReg", "QUIZ · 理想的 f",
         "有人說：「既然 f(x) = E(Y | X = x) 是最好的預測，那我把它算出來，預測誤差就是 0 了。」"
         "這句話錯在哪裡？",
         [(True, "最小的條件均方誤差是 Var(Y | X = x)，不是 0；f 只是把可縮減的那一塊清成 0",
           "對。證明的第 3 步把它拆成 Var(Y | X = x) ＋ (μ(x) − c)²，"
           "選 c = μ(x) 只能讓第二項歸零，第一項是資料本身的條件變異，也就是 Var(ε)，怎麼選都在。"),
          (False, "錯在 E(Y | X = x) 其實不是最好的預測，中位數才是",
           "不對。在<strong>平方</strong>誤差之下條件期望值就是最佳解，這是證明出來的。"
           "中位數是<strong>絕對</strong>誤差的最佳解——換量尺才換答案。"),
          (False, "錯在只有 X 是離散變數時 E(Y | X = x) 才存在",
           "不對。條件期望對連續的 X 一樣有定義。"
           "連續帶來的問題是<strong>估不出來</strong>（沒有資料剛好落在 x），不是<strong>不存在</strong>。"
           "這正是下面要用鄰域平均的理由。")]),
])


# ── P03 curse（講義 02 · p.13–15） ────────────────────────────────────
BODIES["curse"] = "".join([
    r"""
  <p>講義第 13 頁先給最近鄰平均一個明確的適用範圍：
  <strong>$p \le 4$、$n$ 又大的時候它很好用</strong>，
  本課後面的核平滑與樣條（第 7 章）都是它的精緻版本。
  可是 $p$ 一大它就壞掉，而且壞得比直覺快非常多。這個現象叫
  <strong>維度詛咒</strong>（curse of dimensionality）。</p>

  <p>先想清楚鄰域為什麼不能太小。上一節的元件已經看到了：
  鄰域平均的變異大約是 $\sigma^2 / m$，$m$ 是鄰域裡的點數。要把它壓下來就得讓 $m$ 夠大。
  講義第 13 頁的做法是拿一個<strong>固定比例</strong>來示範——例如 10% 的資料。</p>

  <p>嚴格說，$n$ 一起變大時可以讓 $m \to \infty$ 而比例 $m/n \to 0$，
  所以「一定要固定比例」不是數學上的必然。固定比例是為了把問題講清楚：
  它讓「要多大的鄰域」變成一個可以直接算的幾何問題。</p>

  <p>那麼問題變成：在 $p$ 維的單位超立方體裡，要圈到 10% 的體積，
  每個座標軸上得吃掉多長？答案很短：</p>

  $$e_p(r) = r^{1/p}, \qquad e_p(0.1) = 0.1^{1/p}$$
""",
    table(["維度 p", "1", "2", "3", "5", "10", "20", "50"],
          [["每個軸要覆蓋的比例 $0.1^{1/p}$",
            "10.0%", "31.6%", "46.4%", "63.1%", "79.4%", "89.1%", "95.5%"]]),
    r"""
  <p>$p = 10$ 的時候，這個所謂的「鄰域」在<strong>每一個</strong>座標軸上都得覆蓋 79% 的範圍。
  它已經不是鄰域，是整個空間的縮小版。
  <strong>「局部」這兩個字消失了</strong>——而局部正是我們用它來近似 $E[Y \mid X = x]$ 的唯一理由。
  講義第 13 頁最後一行寫得很直接：<strong>在高維空間裡，一個 10% 的鄰域已經不再算是局部的，
  於是我們就失去了「用局部平均去估 $E(Y \mid X = x)$」的本意。</strong></p>

  <p>講義第 14–15 頁換一個角度說同一件事，而且更震撼：
  <strong>高維空間的體積幾乎全部躲在角落。</strong>
  拿一個邊長 2 的超立方體，塞進它的內接球（半徑 $R = 1$，剛好碰到每一面）。
  $p$ 維球的體積有閉式解：</p>

  $$V_{\text{ball}}(R) = \frac{\pi^{p/2}}{\Gamma\!\left(\frac{p}{2} + 1\right)} R^{p},
    \qquad V_{\text{cube}} = 2^{p}$$

  $$r = \frac{V_{\text{ball}}}{V_{\text{cube}}}
      = \frac{\pi^{p/2}}{2^{p}\,\Gamma\!\left(\frac{p}{2} + 1\right)}\, R^{p}$$

  <p>講義第 15 頁把前六維逐項列出來，值得逐格看一次：</p>
""",
    table(["$p$", "1", "2", "3", "4", "5", "6"],
          [["(a) 半徑 $R$ 的球體積",
            "$2R$", r"$\pi R^2$", r"$\frac{4}{3}\pi R^3$", r"$\frac{\pi^2}{2} R^4$",
            r"$\frac{8\pi^2}{15} R^5$", r"$\frac{\pi^3}{6} R^6$"],
           ["(b) 超立方體體積 $2^p$", "2", "4", "8", "16", "32", "64"],
           ["$r = (a)/(b)$", "$R$", r"$\frac{\pi R^2}{4}$", r"$\frac{\pi R^3}{6}$",
            r"$\frac{\pi^2 R^4}{32}$", r"$\frac{\pi^2 R^5}{60}$", r"$\frac{\pi^3 R^6}{384}$"]]),
    r"""
  <p>把 $R = 1$（剛好內接）代進去，$r$ 就是「內接球佔整個立方體的比例」：
  $p = 1$ 是 100%、$p = 2$ 是 78.5%、$p = 3$ 是 52.4%、$p = 4$ 只剩 30.8%、
  $p = 6$ 剩 8.1%、$p = 10$ 剩 <strong>0.25%</strong>、
  $p = 20$ 剩 $2.5 \times 10^{-6}\%$（比例 $2.5 \times 10^{-8}$）。
  換句話說，<strong>十維立方體裡有 99.75% 的體積落在內接球之外</strong>——
  也就是靠近各個角落的那些區域。
  你以為自己站在中間，其實資料都在你摸不到的邊邊。</p>

  <p>反過來問更有感：如果我就是要圈到超立方體的 10% 體積，球的半徑要多大？
  把上面的式子解出 $R$（講義第 15 頁）：</p>

  $$R = \frac{2}{\sqrt{\pi}}\left[\,r\,\Gamma\!\left(\frac{p}{2} + 1\right)\right]^{1/p},
    \qquad
    \Gamma\!\left(\frac{p}{2} + 1\right) \sim \sqrt{\pi p}\,\left(\frac{p}{2e}\right)^{p/2}$$

  <p>這條式子解的是「<strong>整顆球</strong>的體積等於立方體體積的 10%」。
  $R > 1$ 之後球已經有一部分跑到立方體外面，真正落在立方體<strong>裡面</strong>的比例會略低於 10%，
  所以它其實是「覆蓋 10% 所需半徑」的下界。講義第 15 頁用的是同一個簡化；
  差距很小（$p = 6$ 時實際覆蓋 9.9985%），不影響結論的方向。</p>

  <p>右邊那個 $\Gamma$ 的 Stirling 近似說明了為什麼會炸：
  $\Gamma\!\left(\frac{p}{2}+1\right)$ 大致以 $(p/2e)^{p/2}$ 的速度成長，
  開 $p$ 次方之後仍留下一個隨 $p$ 增大的 $\sqrt{p}$ 量級因子。代進去算：
  $p = 1$ 要 $R = 0.10$、$p = 3$ 要 0.58、$p = 6$ 就已經 <strong>1.04</strong>——
  超過內接球的半徑 1，球戳出立方體的面了；$p = 20$ 要 2.14，
  是立方體半邊長的兩倍多。要「只看 10% 的鄰居」，你得把手伸出房間外面。</p>
""",
    viz(svg("w02curSvg", 360) + "\n" + chart("w02curChart", fallback="；表格與公式仍可閱讀"),
        [info_card("怎麼玩這個元件",
                   """左圖是一個邊長 2 的立方體剖面（灰框）與它的內接球（綠圈，半徑 1）。
  紅色虛線圈是<strong>要圈到 10% 體積所需要的半徑</strong>。
  拖 p 看它怎麼從綠圈裡面一路長到綠圈外面、甚至戳出灰框。<br>
  圖形是二維剖面示意，但右側每一個數字都是<strong>真正 p 維的值</strong>，
  由講義第 15 頁的公式即時算出。""", "講義 02 · p.14–15"),
         rows_card("這個維度的實際數字",
                   [("維度 p", "3", "w02curPVal2"),
                    ("內接球佔立方體比例 r", "—", "w02curRatio"),
                    ("躲在角落的體積", "—", "w02curCorner"),
                    ("圈到 10% 體積所需半徑 R", "—", "w02curR"),
                    ("R 有沒有超出立方體的面", "—", "w02curOut"),
                    ("每個軸要覆蓋的比例 0.1^(1/p)", "—", "w02curEdge")]),
         info_card("下面那張圖在說什麼",
                   """兩條線都對 p = 1…20 畫。綠線是內接球佔比 r，
  它掉得比任何人的直覺都快；橘線是要圈到 10% 資料時每個軸得覆蓋的比例，
  它爬得比任何人的直覺都快。兩條線在 p = 3 與 4 之間交叉。<br>
  <strong>注意這個交叉點是兩個不同幾何量的相遇，不是 KNN 適用維度的理論門檻</strong>；
  講義第 13 頁的「p ≤ 4 才好用」是經驗準則。另外邊長那條線假設輸入均勻分布、
  鄰域取等邊超立方體；一般的歐氏 KNN 用的是球形鄰域。""")],
        "w02curStatus", "拖動 p，看紅色虛線圈什麼時候戳出立方體。",
        '<div class="slider-row" style="flex:1;min-width:220px;">'
        '<span class="slider-label">維度 p</span>'
        '<input type="range" id="w02curP" min="1" max="20" step="1" value="3" '
        'oninput="w02curDraw()">'
        '<span class="slider-val" id="w02curPVal">3</span></div>',
        provenance=("book-redraw", "講義 02 · p.15 的體積比與半徑公式，數值由閉式解即時計算")),
    info("三句話收掉維度詛咒",
         """<strong>1.</strong> 要壓低變異，鄰域就得裝進固定比例的資料。<br>
  <strong>2.</strong> 在高維，那個比例對應的鄰域大到不再局部——每個軸都要覆蓋七八成。<br>
  <strong>3.</strong> 鄰域一大，就<strong>不再保證</strong>裡面的 f 近似常數，
  平均出來的東西也就不再貼近 E(Y | X = x)。<br>
  <strong>結果：</strong>最近鄰這一類方法在 p 大的時候會很糟，
  而這正是下一節「參數式方法」存在的理由——
  先假設 f 的形狀，用結構把要估的東西從「一個 p 維任意函數」壓成「幾個參數」。""", "warm"),
    quiz('qCur','QUIZ · 維度詛咒','資料有許多預測變數。使用 KNN 時，為什麼不能只因為樣本數很多，就直接認定「最近鄰」一定夠局部？',[
            (True,'高維時，湊到足夠鄰居可能需要較寬的範圍；還要評估有效維度、鄰居數與資料分布','對。鄰域內資料多可降低平均的不穩定性，但範圍太寬可能混合不同的反應關係。應用驗證資料選擇鄰居數，而不是用單一維度或樣本數門檻斷言。'),
            (False,'只要超過四個變數，KNN 就必定不能使用','四維不是普遍的失效門檻；資料可能有低維結構，表現也取決於分布、樣本數與目標函數。'),
            (False,'KNN 只能分類，不能用來迴歸','KNN 迴歸就是對鄰居的反應值取平均；這裡的問題是鄰域是否適合，與能否定義迴歸方法不同。')]),
])


# ── P02 parametric ────────────────────────────────────────────────────
BODIES["parametric"] = f"""
  <p>知道要估 $f$ 了，接下來的分岔是：<strong>要不要先假設 f 的形狀？</strong>
  兩條路各有代價。</p>

  <p><strong>參數式方法</strong>（parametric method）分兩步。第一步假設形狀，
  最簡單的假設是線性：</p>

  $$f(X) = \\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\cdots + \\beta_p X_p$$

  <p>第二步用訓練資料估那 $p + 1$ 個係數（第 3 章的最小平方法）。
  原本要估「一個任意的 $p$ 維函數」，做了線性假設後，只要估 $p+1$ 個數字。
  代價是——<strong>函數形式假設錯誤會造成偏差</strong>。ISLP 圖 2.4 的黃色平面明顯漏掉了
  真實 $f$ 的彎曲（圖 2.3 的藍色曲面）。</p>

  <p><strong>非參數式方法</strong>（non-parametric method）不預設固定維度的函數形式，
  但仍要指定平滑、局部相似性、距離或尺度等結構。ISLP 圖 2.5 用薄板樣條
  （thin-plate spline）擬合同一份 <code>Income</code> 資料，能呈現資料中的非線性關係。
  但這個彈性也有代價：</p>

{info("非參數式的代價是資料量", '''因為沒把問題化簡成少數幾個參數，
  非參數式方法需要<strong>遠比參數式方法更多的觀測值</strong>才估得準。
  這跟上一節的維度詛咒是同一件事的兩種說法。<br>
  而且它還多出一個要你決定的東西：<strong>平滑程度</strong>。
  ISLP 圖 2.6 把平滑程度放鬆，擬合出來的曲面通過<strong>每一個</strong>訓練點、
  訓練誤差是 0——看起來完美，但它跟真實的 f（圖 2.3）差得很遠。
  這就是過度擬合，也是下面兩節要量化的東西。''', "warm")}

{table(["", "參數式（parametric）", "非參數式（non-parametric）"],
       [["做法", "先假設 f 的固定形式，再估參數", "不固定函數形式，但指定平滑或局部結構"],
        ["要估什麼", "有限個參數（β₀…βₚ）", "整個函數，沒有固定的參數個數"],
        ["需要的資料量", "少", "多，而且隨 p 增加得非常快"],
        ["結構假設錯的後果", "固定形式錯誤會造成高偏差", "距離、尺度或平滑假設錯也會造成偏差"],
        ["額外要選的東西", "形狀（線性？加二次項？）", "平滑程度"],
        ["ISLP 例子", "圖 2.4 的線性平面", "圖 2.5／2.6 的薄板樣條"],
        ["本書章節", "第 3、4、6 章", "第 7（樣條、GAM）、8（樹）、9 章"]])}

  <h3 id="dx-cont">講義完整實作：先把「形狀」畫出來看看</h3>

{card("講義 02 · 用等高線圖看一個指定的 f(x, y)", lab_code(CH, 121), None,
      src=src("121"),
      note="這一格自己指定了 <code>f = cos(y) / (1 + x²)</code>，"
           "然後把它畫成等高線圖。這只是把<strong>指定函數的形狀</strong>畫出來，還沒有用資料估計參數。"
           "真正的參數式擬合還要指定未知係數，再依資料選出它們；下一章的線性迴歸會完整示範。"
           "順帶記住 <code>np.multiply.outer</code> 與 <code>ax.contour</code>："
           "第 4、9 章畫決策邊界會一直用到。")}

{quiz("qPar", "QUIZ · 參數式與非參數式",
      "你有 n = 60 筆資料、p = 12 個預測變數，而且懷疑關係不是線性的。"
      "直接使用一個很有彈性的非參數式方法，主要的風險是什麼？",
      [(True, "p = 12 而 n = 60，非參數式方法在這種維度下沒有足夠的鄰居可以平均，"
              "會擬合出一個變異極大的 f̂",
        "對。非參數式方法少了固定函數形式的限制，但仍以平滑或局部相似性為前提，並用<strong>資料量</strong>換取彈性。"
        "n = 60、p = 12 時資料不足以支持高度彈性的估計，可考慮有結構的參數式模型，"
        "例如線性模型加上幾個你有理由懷疑的非線性項。"),
       (False, "非參數式方法沒有參數，所以沒辦法做預測",
        "不對。「非參數」指的是<strong>不把 f 化簡成固定個數的參數</strong>，"
        "不是「沒有東西可以估」。它照樣預測，KNN 就是最簡單的例子。"),
       (False, "非參數式方法一定比參數式方法偏差大，所以在小樣本上更不準",
        "反了。非參數式方法因不固定函數形式，<strong>偏差通常較小</strong>；"
        "它在小樣本上不準是因為<strong>變異大</strong>。這兩者的分工是 P05 的主題。")])}
"""

# ── P03 tradeoff ──────────────────────────────────────────────────────
BODIES["tradeoff"] = f"""
  <p>把上一節的分岔攤開，其實是一條連續的光譜。一端是<strong>彈性低但看得懂</strong>，
  另一端是<strong>彈性高但講不清楚</strong>。ISLP 圖 2.7 把本書的方法擺在這張圖上。</p>

  <p>你可能會問：既然只要預測準，為什麼不永遠選最彈性的那個？
  ISLP 的回答很直接——<strong>彈性較低的方法有時反而預測更準。</strong>
  原因是過度擬合，下一節就會用數字說清楚。</p>

{info("選擇低彈性方法的三個理由", '''<strong>1. 要做推論：</strong>
  線性模型能直接回答「TV 廣告每多花一千元，銷售大約多幾單位」。
  提升法給不出這種句子。<br>
  <strong>2. 樣本不夠：</strong>彈性高的方法需要足夠資料才能穩定估計，n 小的時候它的變異可能抵銷偏差降低的好處。<br>
  <strong>3. 真實的 f 本來就簡單：</strong>如果 f 真的接近線性，線性迴歸的偏差幾乎是 0，
  彈性方法只會增加估計變異。這是 P05 情境 B 的畫面。''')}

  <h3 id="dx-desc">講義完整實作：決定要多彈性之前，先看資料</h3>

{card("講義 02 · 數值摘要", lab_code(CH, 271), lab_output(CH, 271), src=src("271"),
      note="<code>describe()</code> 一次給你 count／mean／std／五數摘要。"
           "<code>mpg</code> 的樣本標準差 7.805 可以當成誤差的尺度參考——"
           "平方起來約 <strong>60.9</strong>（正式比較時要用訓練集的平均值去預測"
           "同一份測試資料再算 MSE，不是直接拿樣本變異數）。有了尺度感才好判斷："
           "比不過它，就要重新檢查模型是否適合這份資料。")}

{card("講義 02 · 散佈圖矩陣：一眼看出線性夠不夠", lab_code(CH, 269), None,
      src=src("267、269"),
      note="<code>pd.plotting.scatter_matrix()</code> 把所有兩兩關係一次畫出來。"
           "<code>mpg</code> 對 <code>weight</code> 明顯是彎的。"
           "這就是「線性假設可能不夠」的第一手證據，也是決定要不要往彈性端走的依據。"
           "第 3 章會把這個觀察變成正式的殘差診斷。")}

{quiz("qFlex", "QUIZ · 彈性與可解釋性",
      "下列哪一組方法在 ISLP 圖 2.7 上「彈性最低、可解釋性最高」？",
      [(True, "子集選擇與 lasso",
        "對。兩者都以線性模型為基礎，而且會把變數挑掉／把係數壓成 0，"
        "所以能生出的形狀比一般最小平方<strong>更少</strong>，最終模型也更容易解釋。"),
       (False, "最小平方線性迴歸",
        "最小平方會用上<strong>所有</strong>變數，"
        "而子集選擇與 lasso 會把一部分丟掉——形狀更受限、模型更精簡，所以在圖上更靠左上角。"),
       (False, "廣義加法模型（GAM）與決策樹",
        "不對，它們在圖的中段。GAM 允許每個變數各有一條曲線、樹允許切分區塊，"
        "都比線性模型彈性高，可解釋性也因此下降了一些。")])}
"""

# ── P04 mse ───────────────────────────────────────────────────────────
# 講義 02 · p.27 最後一行那句話的證明。raw string 保留 LaTeX。
MSE_PROOF = qa("完整證明", [(
    r"證明：$E[\text{訓練誤差}] \le E[\text{測試誤差}]$——前提是模型類事先固定，且 $\hat f$ 是它裡面訓練誤差最小的那一個",
    r"""<p><strong>先把話說精確。</strong>「典型上比較高」講的是<strong>期望值</strong>，
    不是「每一次都」。要證的是這一條：</p>
    $$E_{Tr}\left[\widehat{R}(\hat f)\right] \;\le\; E_{Tr}\left[R(\hat f)\right]$$

    <p><strong>記號。</strong>訓練集 $Tr = \{(x_i, y_i)\}_{i=1}^{n}$ 是從母體分布 $P$ 獨立抽出來的。
    對任何一個函數 $f$，定義</p>
    $$\widehat{R}(f) = \frac{1}{n}\sum_{i=1}^{n}\left(y_i - f(x_i)\right)^2
      \quad\text{（訓練誤差）},\qquad
      R(f) = E_{(X, Y)\sim P}\left[(Y - f(X))^2\right]
      \quad\text{（測試誤差）}$$
    <p>模型類 $\mathcal{F}$ <strong>事先固定、不依賴訓練資料</strong>，
    而 $\hat f = \arg\min_{f \in \mathcal{F}} \widehat{R}(f)$——
    <strong>它是看過 $Tr$ 之後才在 $\mathcal{F}$ 裡挑出來的</strong>，這是整件事的關鍵。
    （這兩個條件都要。「隨便一個看過資料才決定的 $\hat f$」不夠：
    $n = 1$、$Y$ 零均值變異 $\sigma^2$ 時，故意取 $\hat f \equiv -y_1$，
    期望訓練誤差是 $4\sigma^2$、期望測試誤差是 $2\sigma^2$，不等號會反過來。）
    再令 $f^{*} = \arg\min_{f \in \mathcal{F}} R(f)$ 是類裡真正最好的那一個
    （它只由母體決定，跟 $Tr$ 無關）。</p>

    <p><strong>第 1 步：對固定的 $f$，訓練誤差是測試誤差的不偏估計。</strong>
    只要 $f$ 不依賴 $Tr$，每一項的期望都是 $R(f)$：</p>
    $$E_{Tr}\left[\widehat{R}(f)\right]
      = \frac{1}{n}\sum_{i=1}^{n} E\left[(y_i - f(x_i))^2\right] = R(f)$$
    <p>注意這一步<strong>對 $\hat f$ 不成立</strong>，因為 $\hat f$ 是用 $y_i$ 挑出來的，
    跟 $y_i$ 有相關。整個「訓練誤差太樂觀」就是從這裡漏出來的。</p>

    <p><strong>第 2 步：訓練誤差的期望不會超過類裡最好的風險。</strong>
    $\hat f$ 是最小值，所以對<strong>每一個</strong> $f \in \mathcal{F}$ 都有
    $\widehat{R}(\hat f) \le \widehat{R}(f)$。兩邊取期望，再用第 1 步：</p>
    $$E_{Tr}\left[\widehat{R}(\hat f)\right] \;\le\; E_{Tr}\left[\widehat{R}(f)\right] = R(f)
      \qquad \text{對每個 } f \in \mathcal{F}$$
    <p>對右邊取下確界，得 $E_{Tr}[\widehat{R}(\hat f)] \le R(f^{*})$。
    （這就是 $E[\min] \le \min[E]$：先看答案再挑，當然挑得比較低。）</p>

    <p><strong>第 3 步：測試誤差的期望不會低於類裡最好的風險。</strong>
    $\hat f$ 本身也在 $\mathcal{F}$ 裡，所以不管抽到哪一份 $Tr$ 都有
    $R(\hat f) \ge R(f^{*})$。取期望：</p>
    $$E_{Tr}\left[R(\hat f)\right] \;\ge\; R(f^{*})$$

    <p><strong>合起來。</strong>把兩條夾在 $R(f^{*})$ 的兩側：</p>
    $$E_{Tr}\left[\widehat{R}(\hat f)\right] \;\le\; R(f^{*}) \;\le\; E_{Tr}\left[R(\hat f)\right]
      \qquad \blacksquare$$

    <p><strong>「typically」到底在哪裡。</strong>上面證的是期望值的不等式，
    有兩個地方會讓它在單一次實驗裡看起來不成立：<br>
    <strong>1.</strong> 有限的測試集只是 $R(\hat f)$ 的一個估計，運氣好時可以低於訓練誤差。<br>
    <strong>2.</strong> 如果 $\hat f$ <strong>不是</strong>用 $Tr$ 挑的（例如模型是別人給你的、參數也不重估），
    第 1 步就對它成立，兩邊期望相等，不等式退化成等號。
    <strong>差距完全來自「用同一批資料又挑模型又評分」。</strong></p>

    <p><strong>差距有多大？</strong>在一個更受限的設定下可以算出來（ESL §7.4）。
    <strong>把訓練輸入 $\mathbf{X}$ 固定住</strong>，只讓反應值隨機，
    並把樂觀程度定義成「同樣那些 $x_i$ 上換一批新的 $y$」與訓練誤差的差：</p>
    $$\omega(\mathbf{X}) = E\left[R_{\text{in}}(\hat f) - \widehat{R}(\hat f)
      \;\middle|\; \mathbf{X}\right]
      = \frac{2}{n}\sum_{i=1}^{n}\mathrm{Cov}\left(\hat y_i,\, y_i \;\middle|\; \mathbf{X}\right)$$
    <p>擬合愈是「跟著 $y_i$ 跑」，這個共變異數就愈大。
    <strong>條件在 $\mathbf{X}$ 上這件事不能省</strong>：不然一個完全不看資料的
    $\hat y_i = f(x_i)$ 樂觀程度明明是 0，無條件的共變異數卻是 $\mathrm{Var}(f(X_i)) \neq 0$。</p>

    <p>再多一個假設就有漂亮的閉式：若擬合是<strong>線性平滑器</strong>
    $\hat{\mathbf{y}} = S\mathbf{y}$（給定 $\mathbf{X}$ 後 $S$ 固定），
    且 $\mathrm{Cov}(\varepsilon \mid \mathbf{X}) = \sigma^2 I$，則</p>
    $$\omega(\mathbf{X}) = \frac{2\sigma^2}{n}\,\mathrm{tr}(S)$$
    <p>固定設計的普通最小平方法裡 $\mathrm{tr}(S) = \mathrm{rank}(\mathbf{X})$，
    滿秩時就是含截距的參數個數 $d$，於是回到常見的 $\omega = 2 d \sigma^2 / n$：
    <strong>參數愈多、樣本愈少，訓練誤差就愈樂觀。</strong></p>

    <p>兩個要提醒的地方：這是 <strong>in-sample</strong> 的樂觀程度（$x_i$ 沒有換），
    不是一般測試誤差差距的精確公式；而且 $d$ 要用 $\mathrm{tr}(S)$，
    <strong>資料驅動地選變數、選節點之後不能再拿名目參數個數去代</strong>。
    這條式子正是 <a href="model_selection.html">第 6 章</a> $C_p$ 與 AIC
    「罰一項與 $\mathrm{tr}(S)$ 成正比的量」的來源（BIC 的 $d\log n$ 是另一套推導）。
    它也解釋了 1-最近鄰的極端情形：它把每個訓練點都完美記住，訓練誤差 0，
    但測試誤差一點都不是 0。</p>""")])


BODIES["mse"] = f"""
  <p>要比較方法，得先有量尺。迴歸問題最常用的是<strong>均方誤差</strong>（MSE）：</p>

  $$\\mathrm{{MSE}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}}
    \\left(y_i - \\hat f(x_i)\\right)^2$$

  <p>問題在於：<strong>這個平均是對哪一批資料算的？</strong>
  如果用的是擬合時那批資料，它叫<strong>訓練 MSE</strong>；
  如果用的是模型完全沒見過的資料，它叫<strong>測試 MSE</strong>。
  兩者的行為完全不同，我們用後者評估新資料上的表現。</p>

  <p>為什麼不能用訓練 MSE 當代理？因為大部分方法就是<strong>直接或間接在最小化它</strong>。
  你拿一個「已經被最佳化過的目標值」當成公正的評分，當然會太樂觀。
  極端一點：一條通過每一個訓練點的曲線，訓練 MSE 是 0——
  而這個 0 完全沒有告訴你它在新資料上會怎樣。</p>

  <p>講義第 27 頁最後一行把這件事寫成一句斷言，值得把它證出來：</p>

{info("講義第 27 頁怎麼說", '''假設兩批資料都抽自同一個母體分布，
  一個模型的測試誤差<strong>通常會高於</strong>它的訓練誤差。<br>
  兩批資料<strong>同分布</strong>是前提；而「通常」不是模糊其辭，
  它精確地說明這是一個<strong>期望值</strong>的不等式。''')}

{MSE_PROOF}

{viz(svg("w02fitSvg", 300) + "\n" + svg("w02mseSvg", 250),
     [info_card("怎麼看這兩張圖",
                '<strong>上圖</strong>是同一組 50 個點（σ = 1）用三種彈性擬合的結果，'
                '綠色虛線是真實的 f。<strong>下圖</strong>是訓練 MSE（灰）與測試 MSE（紅）'
                '對彈性度的曲線，圓點標出上圖那三個選擇，紫色垂線是目前選的那一個。',
                "ISLP 圖 2.9"),
      rows_card("目前的選擇",
                [("樣條自由度 df", "6", "w02flexDfVal"),
                 ("訓練 MSE", "—", "w02flexTrain"),
                 ("測試 MSE", "—", "w02flexTest"),
                 ("Var(ε)（下限）", "1.00", "w02flexVar")]),
      info_card("彈性度是什麼",
                'df ＝ 擬合時估的參數個數。<strong>df = 2 就是線性迴歸</strong>'
                '（截距加斜率），df ≥ 5 是三次迴歸樣條，節點依固定順序一個一個加進去，'
                '所以模型空間是巢狀的，訓練 MSE <strong>保證</strong>單調下降。')],
     "w02flexStatus", "按三個按鈕切換彈性，看訓練 MSE 與測試 MSE 各自往哪裡走。",
     '<button class="btn btn-toggle" onclick="w02flexSet(2)">線性（df 2）</button>'
     '<button class="btn btn-toggle" onclick="w02flexSet(6)">中等彈性（df 6）</button>'
     '<button class="btn btn-toggle" onclick="w02flexSet(25)">過度彈性（df 25）</button>',
     provenance=("simulation", "固定種子模擬；對照 ISLP 圖 2.9"))}

{info("這張圖的三個一定要看懂的地方", '''<strong>1. 這組巢狀樣條的訓練 MSE 從 3.43 一路掉到 0.48，</strong>
  單調下降，沒有轉折；模型空間擴大時，訓練目標只會下降或不變。<br>
  <strong>2. 這次模擬的測試 MSE 呈 U 型：</strong>3.26 → 最低約 1.02（df = 7）→ 回升到 1.50。
  df = 25 的擬合在訓練資料上是最好的，在新資料上卻比 df = 6 差了快 50%。<br>
  <strong>3. 那條水平虛線是 Var(ε) = 1.00。</strong>
  這次有限測試集的 MSE 都在它上方；有限樣本估計值仍會波動，理論下限約束的是期望測試 MSE。''')}

  <p>這組模型依序擴大且用同一訓練目標擬合，所以訓練 MSE 單調不增；
  測試 MSE 常隨彈性先降後升，但最低點也可能落在端點。
  當訓練 MSE 很小、測試 MSE 卻很大，我們就說發生了<strong>過度擬合</strong>（overfitting）。</p>

{info("過度擬合的嚴格定義", '''不是「訓練 MSE 比測試 MSE 小」。
  那幾乎永遠成立，因為方法本來就在最小化訓練 MSE。<br>
  過度擬合指的是：<strong>存在一個比較不彈性的模型，它的測試 MSE 反而更小。</strong>
  上圖裡 df = 25 是過度擬合（df = 6 更好），而 df = 6 不是。''', "warm")}

  <h3 id="dx-mse">期望值到底在平均什麼</h3>

  <p>期望值是依機率加權的平均；MSE 則是把平方誤差平均。
  重點是<strong>對哪些隨機量取平均</strong>：只對新觀測值的誤差取平均，與連訓練資料也重抽後取平均，
  是不同的問題。若需要複習加權平均的程式寫法，可看
  <a href="p2_flow_functions.html#loop">附錄：流程控制中的 zip 與加權平均</a>（課程 Lab Ch2 的迴圈範例）。</p>

{qa("觀念釐清", [
    ("Q：為什麼這裡的測試 MSE 呈 U 型？訓練 MSE 為什麼不是？",
     "<p>先講訓練 MSE。彈性愈高，模型能生出的函數集合<strong>愈大</strong>"
     "（本頁的樣條是巢狀的，df = 6 能擬合出的每一條曲線 df = 7 都能擬合出來）。"
     "既然在更大的集合裡找最小值，最小值只可能更小或一樣。"
     "所以訓練 MSE 單調不上升。這是純粹的最佳化事實，跟資料是什麼無關。</p>"
     "<p>測試 MSE 就沒有這個保護，因為它衡量的是「在沒見過的點上」的表現。"
     "拆解式（下一節）說它等於偏差² ＋ 變異 ＋ $\\mathrm{Var}(\\varepsilon)$。"
     "彈性上升時偏差²下降、變異上升。<strong>一開始偏差²掉得比變異漲得快，"
     "所以總和往下；某個點之後偏差²已經幾乎為 0、沒東西可掉了，"
     "變異卻還在漲，總和於是往上。</strong>兩個反向的量相加，形狀就是 U。</p>"
     "<p>要注意「U 型」講的是<strong>一般趨勢</strong>。真實 f 剛好接近線性時，"
     "偏差²從一開始就幾乎是 0，U 的左半邊等於不存在，圖看起來就是單調上升"
     "（下一節的情境 B）。所以嚴格的說法是：測試 MSE 的最低點可能落在任何位置，"
     "包含最左邊。</p>"),
])}

{quiz("qMSE", "QUIZ · 訓練與測試 MSE",
      "手上有兩個模型：A 的訓練 MSE = 0.20、測試 MSE = 1.90；"
      "B 的訓練 MSE = 0.95、測試 MSE = 1.05。應該選哪一個？為什麼？",
      [(True, "選 B。我們要的是在新資料上的表現，A 的訓練與測試差距顯示它在擬合雜訊",
        "對。A 的訓練 MSE 只有 B 的五分之一，但測試 MSE 幾乎是 B 的兩倍。"
        "這是過度擬合的典型表現。決策一律看測試誤差。"),
       (False, "選 A。訓練 MSE 小表示它真的學到了資料裡的結構",
        "不對。訓練 MSE 小只表示它<strong>貼合了這批資料</strong>，"
        "而其中一部分是隨機的巧合。把彈性拉滿可以讓訓練 MSE 變成 0，"
        "那並不代表學到了任何東西。"),
       (False, "資訊不足，還要看兩個模型的訓練 MSE 差距是否顯著",
        "不對。訓練 MSE 的差距對「該選哪個」這個問題沒有參考價值；"
        "它甚至<strong>系統性地偏好較彈性的模型</strong>。有測試 MSE 可以看的時候，"
        "直接看它就好。")])}
"""

# ── P05 biasvar ───────────────────────────────────────────────────────
# 講義 02 · p.28 只寫了「Proof of the decomposition」，這裡把它補完。
BV_PROOF = qa("完整證明", [(
    r"證明：$E\left[(y_0 - \hat f(x_0))^2\right] = \mathrm{Var}(\hat f(x_0)) + \left[\mathrm{Bias}(\hat f(x_0))\right]^2 + \mathrm{Var}(\varepsilon)$",
    r"""<p><strong>設定與記號。</strong>把測試點的位置 $x_0$ 固定住，
    真實模型是 $Y = f(X) + \varepsilon$，其中 $f(x) = E[Y \mid X = x]$、
    $E[\varepsilon \mid X] = 0$，並沿用本章的<strong>同變異假設</strong>
    $\mathrm{Var}(\varepsilon \mid X) = \sigma^2$（允許異變異時，
    下面的 $\mathrm{Var}(\varepsilon)$ 都要讀成 $\mathrm{Var}(Y \mid X = x_0)$）。測試觀測值是</p>
    $$y_0 = f(x_0) + \varepsilon_0$$
    <p>為了讀起來不擠，令 $f_0 = f(x_0)$、$\hat\mu = \hat f(x_0, Tr)$、
    $m = E_{Tr}\left[\hat\mu\right]$。</p>

    <p><strong>這裡有兩層隨機，一定要分清楚：</strong><br>
    <strong>1.</strong> 訓練集 $Tr$——每換一份訓練資料，$\hat\mu$ 就是另一個數字。<br>
    <strong>2.</strong> 測試點的雜訊 $\varepsilon_0$——它是<strong>新抽的</strong>，沒有參與訓練。<br>
    所以 $\varepsilon_0$ 與 $Tr$ 獨立，因而與 $\hat\mu$ 獨立。外面那個 $E$ 是對這兩層一起取的，
    這正是講義那句<strong>「這個期望值同時把 $y_0$ 的變動與 $Tr$ 的變動都平均掉」</strong>的意思。
    <strong>本頁 P01 那條推導是把 $\hat f$ 固定住的版本，
    這裡把 $\hat f$ 的隨機性也放進來，所以可縮減的那一塊會再裂成兩塊。</strong></p>

    <p><strong>第 1 步：把 $y_0$ 換掉、湊出 $\varepsilon_0$。</strong></p>
    $$y_0 - \hat\mu = \left(f_0 + \varepsilon_0\right) - \hat\mu
      = \varepsilon_0 + \left(f_0 - \hat\mu\right)$$

    <p><strong>第 2 步：平方展開、取期望。</strong></p>
    $$E\left[(y_0 - \hat\mu)^2\right]
      = E\left[\varepsilon_0^2\right]
      + 2\,E\left[\varepsilon_0\left(f_0 - \hat\mu\right)\right]
      + E\left[\left(f_0 - \hat\mu\right)^2\right]$$
    <p>中間那一項因為獨立而可以拆開，再用 $E[\varepsilon_0] = 0$：</p>
    $$E\left[\varepsilon_0\left(f_0 - \hat\mu\right)\right]
      = E[\varepsilon_0]\;E\left[f_0 - \hat\mu\right] = 0$$
    <p>第一項則是 $E[\varepsilon_0^2] = \mathrm{Var}(\varepsilon) = \sigma^2$。
    於是只剩下</p>
    $$E\left[(y_0 - \hat\mu)^2\right]
      = \mathrm{Var}(\varepsilon) + E\left[\left(\hat\mu - f_0\right)^2\right]$$

    <p><strong>第 3 步：把剩下那一項再拆一次——一樣是加一項、減一項。</strong>
    這次塞進去的是 $\hat\mu$ 自己的平均 $m$：</p>
    $$\hat\mu - f_0 = \underbrace{\left(\hat\mu - m\right)}_{\text{隨 } Tr \text{ 變動，期望 } 0}
      + \underbrace{\left(m - f_0\right)}_{\text{常數}}$$
    $$E\left[\left(\hat\mu - f_0\right)^2\right]
      = E\left[\left(\hat\mu - m\right)^2\right]
      + 2\left(m - f_0\right)\underbrace{E\left[\hat\mu - m\right]}_{=\,0}
      + \left(m - f_0\right)^2$$

    <p><strong>第 4 步：認出這兩塊是誰。</strong></p>
    $$E\left[\left(\hat\mu - m\right)^2\right] = \mathrm{Var}_{Tr}\left(\hat f(x_0)\right),
      \qquad
      m - f_0 = E\left[\hat f(x_0)\right] - f(x_0) = \mathrm{Bias}\left(\hat f(x_0)\right)$$

    <p><strong>合起來就是講義第 28 頁那一行：</strong></p>
    $$E\left[\left(y_0 - \hat f(x_0)\right)^2\right]
      = \underbrace{\mathrm{Var}\!\left(\hat f(x_0)\right)}_{\text{換一份訓練資料會抖多少}}
      + \underbrace{\left[\mathrm{Bias}\!\left(\hat f(x_0)\right)\right]^2}_{\text{平均而言偏掉多少}}
      + \underbrace{\mathrm{Var}(\varepsilon)}_{\text{怎麼樣都在}}
      \qquad \blacksquare$$

    <p><strong>三個立刻讀得出來的推論。</strong><br>
    <strong>1.</strong> 三項都非負，所以期望測試 MSE 有下限 $\mathrm{Var}(\varepsilon)$，
    跟 <a href="#irreducible">P01</a> 得到的下限是同一件事。<br>
    <strong>2.</strong> 偏差與變異都是<strong>對 $Tr$ 取的</strong>統計量，
    所以「這一次擬合的殘差有多大」跟它們是兩回事——要看它們得想像重抽很多份訓練集。<br>
    <strong>3.</strong> 彈性一升，$\mathrm{Var}(\hat f(x_0))$ 通常上去、
    $\mathrm{Bias}$ 通常下來，兩者相加才有 U 型。<strong>沒有哪一邊可以單獨最佳化</strong>——
    這就是講義說的 bias-variance trade-off。</p>

    <p><strong>整條曲線的版本。</strong>上面只證了單一個 $x_0$。
    把等式對測試點的分布再取一次期望（或在測試網格上平均），
    左邊變成期望測試 MSE、右邊三項變成各自的平均，形式一模一樣。
    下面那張圖畫的就是這個平均版本。</p>""")])


BODIES["biasvar"] = f"""
  <p>上一節看到了 U 型，這一節解釋它是怎麼長出來的。可以證明：
  在某個測試點 $x_0$ 上，<strong>期望</strong>測試 MSE 一定能拆成三塊
  （ISLP 式 2.7、ESL 式 7.9）：</p>

  $$E\\left(y_0 - \\hat f(x_0)\\right)^2
    = \\mathrm{{Var}}\\!\\left(\\hat f(x_0)\\right)
    + \\left[\\mathrm{{Bias}}\\!\\left(\\hat f(x_0)\\right)\\right]^2
    + \\mathrm{{Var}}(\\varepsilon)$$

  <p>三項都非負，所以<strong>期望測試 MSE 永遠不可能低於 $\\mathrm{{Var}}(\\varepsilon)$</strong>。
  這條式子同時給了 U 型的機制與 P01 那條下限。三項各是什麼意思：</p>

  <ul>
    <li><strong>偏差</strong>（bias）$= E[\\hat f(x_0)] - f(x_0)$：
    用一個過於簡單的模型去逼近複雜真實問題所引入的系統性錯誤。
    真實 $f$ 明顯非線性時，線性迴歸<strong>不管增加多少資料</strong>都會有高偏差。
    一般而言愈彈性 → 偏差愈低。</li>
    <li><strong>變異</strong>（variance）$= \\mathrm{{Var}}(\\hat f(x_0))$：
    換一組訓練資料重新擬合一次，$\\hat f(x_0)$ 會變動多少。
    彈性高的曲線緊貼著點跑，動一個點整條線就變樣。
    一般而言愈彈性 → 變異愈高。</li>
    <li><strong>$\\mathrm{{Var}}(\\varepsilon)$</strong>：跟方法無關的常數。</li>
  </ul>

  <p>講義第 28 頁只寫了一行「這個拆解的證明」就跳過去了，這裡補完：</p>

{BV_PROOF}

{viz(chart("w02bvChart", "tall",
           "。此圖的重點：偏差² 隨彈性下降、變異隨彈性上升，兩者相加再加上 Var(ε) 得到期望測試 MSE；"
           "最低點的位置隨真實 f 的形狀而變（情境 B 在 df = 2，情境 C 在 df = 18）。"),
     [info_card("這張圖怎麼算出來的",
                '固定真實的 f 與 σ = 1，<strong>重抽 M = 300 組訓練集</strong>'
                '（每組 n = 50，訓練點的 x 固定、只有 ε 重抽），對每個彈性度算出 300 條 f̂，'
                '再在 201 個測試點上算偏差²與變異並平均。三個情境共用同一組 ε。',
                "ISLP 圖 2.12"),
      rows_card("這個情境的最低點",
                [("情境", "中度非線性", "w02bvScen"),
                 ("最佳 df", "—", "w02bvBest"),
                 ("該點的期望測試 MSE", "—", "w02bvTot"),
                 ("其中偏差²", "—", "w02bvBias"),
                 ("其中變異", "—", "w02bvVarv"),
                 ("Var(ε)", "1.00", "w02bvIrr")]),
      info_card("為什麼變異曲線相同",
                '三個情境的<strong>變異曲線完全相同</strong>。'
                '因為對線性平滑器來說 Var(f̂) 只跟設計矩陣與 σ² 有關，'
                '<strong>跟真實的 f 一點關係都沒有</strong>。'
                '三張圖的差別百分之百來自偏差²。')],
     "w02bvStatus", "切換三個情境：真實 f 的形狀怎麼改變最佳彈性度。",
     '<button class="btn btn-toggle" onclick="w02bvSet(\'A\')">中度非線性</button>'
     '<button class="btn btn-toggle" onclick="w02bvSet(\'B\')">接近線性</button>'
     '<button class="btn btn-toggle" onclick="w02bvSet(\'C\')">高度非線性</button>',
     provenance=("simulation", "固定種子蒙地卡羅 M=300；對照 ISLP 圖 2.12"))}

{info("三個情境的最佳 df 分別是 2、7、18", '''ISLP 圖 2.12 比較了不同情境：
  <strong>沒有一個放諸四海皆準的彈性度。</strong><br>
  <strong>情境 B（接近線性）：</strong>偏差²從一開始就幾乎是 0，增加彈性只會增加估計變異，
  df = 2 最好。<br>
  <strong>情境 A（中度非線性）：</strong>偏差²一開始掉得快，總和先降後升，經典的 U。<br>
  <strong>情境 C（高度非線性）：</strong>df = 2 的偏差²高達 20.06，
  提高彈性可以大幅降低誤差，要到 df = 18 才觸底。<br>
  真實的 f 你看不到，所以這個最佳點得靠<strong>第 5 章的交叉驗證</strong>去估。''')}

  <p>ESL §7.3 也給出一個可直接計算的特例。對 KNN 迴歸，
  <strong>在固定訓練輸入（因而鄰居的位置也固定）、雜訊零均值同變異且彼此獨立</strong>的條件下，
  三項有封閉形式（ESL 式 7.10）：</p>

  $$\\mathrm{{Err}}(x_0) = \\sigma_\\varepsilon^2
    + \\left[f(x_0) - \\frac{{1}}{{k}} \\sum_{{\\ell=1}}^{{k}} f(x_{{(\\ell)}})\\right]^2
    + \\frac{{\\sigma_\\varepsilon^2}}{{k}}$$

  <p>看第三項：<strong>在這個固定設計之下，變異就是 $\\sigma_\\varepsilon^2 / k$</strong>，$k$ 愈大愈小。
  第二項是「$f(x_0)$ 與 $k$ 個鄰居上 $f$ 的平均」之差：$k$ 愈大鄰居愈遠，
  這個差<strong>通常</strong>愈大（但不保證單調——$f$ 是直線而鄰居左右對稱時，
  多收一個對面的鄰居反而可能把偏差抵消掉）。
  一條式子把偏差–變異取捨寫得清清楚楚，也預告了本頁最後一節的 KNN。</p>

  <h3 id="dx-seed">蒙地卡羅的重現性</h3>

  <p>這張圖用固定種子抽取 300 組訓練資料，讓比較可以重現。
  固定種子不會消除資料本身的不確定性；它只是讓同一個模擬流程重跑時得到相同結果。
  語法可回看<a href="p3_numpy.html#rand">附錄：NumPy 的隨機抽樣與種子</a>
  （課程 Lab Ch2 的平均與標準差範例），這裡專注看下面如何跨訓練集算偏差與變異。</p>

  <div class="info-card" style="margin:1.2rem 0;">
    <div class="ic-title">蒙地卡羅拆解的虛擬碼 <span class="ic-badge">CODE</span></div>
    <div class="pseudo-code" style="font-size:.74rem;">
<span class="line"><span class="kw">for</span> d <span class="kw">in</span> 彈性度清單:</span>
<span class="line">    <span class="kw">for</span> m <span class="kw">in</span> <span class="kw">range</span>(M):            <span class="com"># M = 300 組訓練集</span></span>
<span class="line">        y = f(x_train) + rng.normal(<span class="num">0</span>, sigma)</span>
<span class="line">        fhat[m] = 用 d 擬合(x_train, y).predict(x_test)</span>
<span class="line">    bias2 = mean((fhat.mean(axis=<span class="num">0</span>) - f(x_test))**<span class="num">2</span>)</span>
<span class="line">    var   = mean(fhat.var(axis=<span class="num">0</span>))</span>
<span class="line">    total = bias2 + var + sigma**<span class="num">2</span></span>
    </div>
    <p style="font-size:.82rem;margin:.6rem 0 0;color:var(--muted);">
    注意 <code>fhat.mean(axis=0)</code>：平均是<strong>跨 300 組訓練集</strong>取的，
    不是跨測試點。下面的 Q&amp;A 說明這兩種平均的差別。</p>
  </div>

{qa("觀念釐清", [
    ("Q：偏差–變異拆解是在對「什麼」取期望值？",
     "<p>總測試誤差同時平均<strong>重複抽到的訓練集</strong>與測試點的新反應值。"
     "其中偏差與變異描述訓練集重抽造成的模型變動，Var(ε) 則來自新反應值的雜訊。</p>"
     "<p>拆解式裡的 $\\hat f(x_0)$ 是一個<strong>隨機變數</strong>："
     "它的隨機性來自「你剛好抽到哪一組訓練資料」。"
     "$E[\\hat f(x_0)]$ 是「想像重複蒐集無數份訓練資料、每份都擬合一次模型、"
     "把這些 $\\hat f(x_0)$ 平均起來」。偏差是這個平均與真值 $f(x_0)$ 的差；"
     "變異是這些 $\\hat f(x_0)$ 自己的散開程度。</p>"
     "<p>所以下面兩句話是不同的意思，不要搞混：</p><ul>"
     "<li><strong>「這個模型的變異很大」</strong>："
     "換一份訓練資料，擬合出來的模型會很不一樣。這是拆解式講的變異。</li>"
     "<li><strong>「這個模型的預測值散得很開」</strong>："
     "在不同的 $x$ 上預測值差很多。這只是說 $\\hat f$ 這條曲線起伏大，"
     "跟拆解式的變異<strong>不是同一件事</strong>。</li></ul>"
     "<p>實務上的後果：你手上只有一份訓練資料，所以偏差與變異"
     "<strong>沒辦法分別算出來</strong>。上面那張圖能畫，是因為那是模擬，"
     "我們知道真實的 f，也能想抽幾組訓練集就抽幾組。真實資料上你只能估它們的"
     "<strong>總和</strong>（第 5 章的交叉驗證），然後靠這一節的直覺判斷該往哪邊調。</p>"),
])}

{quiz("qBV", "QUIZ · 偏差–變異拆解",
      "維持相同的母體分佈與預測變數，只增加訓練樣本數。拆解式中哪一項確定不會因此改變？",
      [(True, "不可縮減誤差 Var(ε)，因為它由這組 X 下的母體雜訊決定",
        "對。更多同類資料通常有助於把 f 估得更穩；母體的不可縮減誤差由既定資料分布決定，會保持相同。偏差與變異如何隨 n 改變，要看估計方法；不能只用模型類別是否相同來判斷。"),
       (False, "偏差，因為只要模型類別不變，它就與樣本數無關",
        "不對。偏差是 E[f̂(x)] 與 f(x) 的差，估計量的平均也可能隨 n 改變。例如固定 K 的最近鄰法，資料變多時鄰居通常更近，偏差就可能下降。線性模型無法表達曲線的限制，不能推成所有估計方法的偏差都固定。"),
       (False, "變異，因為增加資料沒有改變模型的彈性",
        "不對。即使方法與調整參數固定，增加訓練資料仍可能讓估計對抽樣不那麼敏感。彈性與 n 都會影響估計的不確定性。")])}

"""

# ── P06 bayes ─────────────────────────────────────────────────────────
# 講義 02 · p.32、34–35：分類的最佳規則。與 PART 02 的迴歸版本併排解釋，
# 並補上講義只寫了結論的證明。raw string 保留 LaTeX。
BAYES_FRAME = "".join([
    table(["用什麼量尺（損失函數）", r"在每一點 $x$ 上的最佳預測", "本站哪裡講"],
          [[r"平方誤差 $\left(Y - a\right)^2$",
            r"條件<strong>期望</strong> $E[Y \mid X = x]$", "PART 02（迴歸）"],
           [r"絕對誤差 $\left|Y - a\right|$",
            r"條件<strong>中位數</strong>", "PART 02 證明的最後一段"],
           [r"0–1 損失 $I(Y \neq a)$",
            r"條件<strong>眾數</strong> $\arg\max_k \Pr(Y = k \mid X = x)$", "本節（分類）"]]),
    info("「Bayes 分類器」的 Bayes，不是貝氏統計的那個 Bayes",
         r"""這個名字來自 <strong>Bayes 決策理論</strong>（Bayes decision theory）：
  固定一個損失函數之後，期望損失的下限叫 <strong>Bayes 風險</strong>，達到它的規則叫 Bayes 規則。
  用 0–1 損失時，Bayes 風險就是 Bayes 錯誤率。<br>
  <strong>它不需要你對未知參數指定貝氏先驗，也沒有做後驗更新。</strong>
  （類別本身的邊際機率當然存在，它已經包含在母體的聯合分布裡了。）
  式子裡出現的 $\Pr(Y = k \mid X = x)$ 只是「知道 $X$ 之後 $Y$ 的條件機率」，
  分類文獻習慣叫它後驗機率（名字的由來），但整段推導從頭到尾只用到母體的聯合分布。
  本站<a href="s5_bayesian.html">附錄的貝氏推論</a>談的是對<strong>參數</strong>給先驗，
  那是另一回事。<br>
  同一句話換個說法：<strong>迴歸的最佳解是條件期望，分類的最佳解是條件眾數，
  兩者都是「先選量尺、再逐點最小化條件期望損失」這一套框架跑出來的答案。</strong>"""),
])

BAYES_PROOF = qa("完整證明", [(
    r"證明：在 0–1 損失之下，$C^{*}(x) = \arg\max_k \Pr(Y = k \mid X = x)$ 讓期望錯誤率最小",
    r"""<p><strong>要證的事。</strong>令 $p_k(x) = \Pr(Y = k \mid X = x)$，$k = 1, \dots, K$。
    對任意分類器 $C$（任何一個把 $x$ 對應到某個類別標籤的函數）都有</p>
    $$E\left[I\!\left(Y \neq C(X)\right)\right]
      \;\ge\; E\left[I\!\left(Y \neq C^{*}(X)\right)\right]
      = 1 - E\left[\max_k p_k(X)\right]$$

    <p><strong>第 0 步：把整體錯誤率拆成逐點的問題。</strong>用全期望公式：</p>
    $$E\left[I\!\left(Y \neq C(X)\right)\right]
      = E_X\Big[\,E\left[I\!\left(Y \neq C(X)\right) \mid X\right]\Big]$$
    <p>跟 PART 02 完全一樣的招式：$X = x$ 固定之後，$C(x)$ 只是 $K$ 個標籤裡的<strong>一個</strong>，
    不再是函數。所以「在所有分類器裡找最好的」可以拆成「在每一點各自從 $K$ 個標籤裡挑一個」。</p>

    <p><strong>第 1 步：算出固定 $x$ 的條件風險。</strong>
    指示變數的期望就是機率，所以對任何一個候選標籤 $c$：</p>
    $$E\left[I(Y \neq c) \mid X = x\right]
      = \Pr\left(Y \neq c \mid X = x\right)
      = 1 - \Pr\left(Y = c \mid X = x\right)
      = 1 - p_c(x)$$

    <p><strong>第 2 步：在這一點上挑最好的標籤。</strong>
    要讓 $1 - p_c(x)$ 最小，就是要讓 $p_c(x)$ 最大：</p>
    $$\min_{c \in \{1, \dots, K\}} \left[1 - p_c(x)\right] = 1 - \max_k p_k(x),
      \qquad \text{在 } c = \arg\max_k p_k(x) \text{ 取到}$$

    <p><strong>第 3 步：逐點最小推到全域最小。</strong>
    上式對每一個 $x$ 分別成立，所以對任意 $C$ 都有
    $E[I(Y \neq C(x)) \mid X = x] \ge 1 - \max_k p_k(x)$。兩邊對 $X$ 取期望：</p>
    $$E\left[I\!\left(Y \neq C(X)\right)\right]
      \;\ge\; E_X\left[1 - \max_k p_k(X)\right]
      = 1 - E\left[\max_k \Pr(Y = k \mid X)\right]$$
    <p>而 $C^{*}$ 在每一點都取到等號，所以這個下限確實達得到。$\blacksquare$</p>

    <p><strong>兩類的特例。</strong>$K = 2$ 時 $\max\left(p_1(x),\, 1 - p_1(x)\right)$，
    所以在 $x$ 的條件錯誤率是 $\min\left(p_1(x),\, 1 - p_1(x)\right)$，
    而 Bayes 規則就是「$p_1(x) > 0.5$ 猜 1」。條件錯誤率的最大值 0.5 只在
    $p_1(x) = 0.5$ 那條線上取到——那正是 Bayes 決策邊界，也是最分不開的位置。</p>

    <p><strong>跟迴歸完全平行。</strong>把兩邊的結論並排看，會發現是同一件事的兩個外衣：</p>
    $$\min_{a} E\left[(Y - a)^2 \mid X = x\right] = \mathrm{Var}\left(Y \mid X = x\right),
      \qquad a^{*} = E[Y \mid X = x]$$
    $$\min_{c} E\left[I(Y \neq c) \mid X = x\right] = 1 - \max_k p_k(x),
      \qquad c^{*} = \arg\max_k p_k(x)$$
    <p>兩邊都是「逐點最小 ⇒ 全域最小」，也都留下一個<strong>跟方法無關的下限</strong>：
    迴歸留下 $\mathrm{Var}(\varepsilon)$，分類留下 Bayes 錯誤率。
    後者大於 0 的理由也一模一樣——只要有一塊 $x$ 沒有任何類別的條件機率是 1，
    也就是知道 $X$ 之後 $Y$ 仍有隨機性。</p>

    <p><strong>錯誤代價不一樣的時候。</strong>0–1 損失把所有錯誤看成一樣重。
    如果把病人判成健康、跟把健康判成病人代價不同，就要換成一般的損失矩陣 $L(k, c)$，
    第 1 步的條件風險變成 $\sum_k L(k, c)\, p_k(x)$，最佳規則跟著變成</p>
    $$c^{*}(x) = \arg\min_{c} \sum_{k=1}^{K} L(k, c)\, p_k(x)$$
    <p>框架沒有變，只是量尺換了——這也是<a href="classification.html">第 4 章</a>調整門檻與看 ROC 的出發點。</p>""")])


# 講義 02 · p.33：最近鄰在分類上一樣會壞掉，但對 Ĉ(x) 的衝擊小於對 p̂_k(x)。
CLS_ROBUST = qa("為什麼分類比較耐得住維度", [(
    r"講義第 33 頁：對 $\hat C(x)$ 的衝擊小於對 $\hat p_k(x)$——這句話怎麼算出來",
    r"""<p><strong>直覺先講。</strong>分類最後只用到<strong>誰最大</strong>，
    不是<strong>大多少</strong>。$\arg\max$ 把一整組機率壓成一個標籤，
    是比機率本身<strong>粗糙得多</strong>的資訊。
    只要估計誤差沒有大到把排名弄反，決策就跟用真實機率時<strong>一模一樣</strong>。</p>

    <p><strong>兩類情形可以寫成等式。</strong>令 $\eta(x) = \Pr(Y = 1 \mid X = x)$，
    $C^{*}$ 是 Bayes 規則、$\hat C$ 是你手上那個插入式（plug-in）分類器
    $\hat C(x) = I\!\left(\hat\eta(x) > 0.5\right)$。把 BAYES 那條證明的第 1 步逐點展開再相減：</p>
    $$R(\hat C) - R(C^{*})
      = E\Big[\left|2\eta(X) - 1\right| \cdot
        I\!\left(\hat C(X) \neq C^{*}(X)\right)\Big]$$

    <p>這條式子有兩個很強的讀法：<br>
    <strong>1.</strong> 右邊有一個指示函數——<strong>只有在你猜錯邊的那些 $x$ 上才付代價</strong>。
    $\hat\eta$ 估成 0.9 而真值是 0.6？只要兩個都在 0.5 的同一側，超額風險是 <strong>0</strong>。<br>
    <strong>2.</strong> 付的代價還被 $\left|2\eta(x) - 1\right|$ 加權。
    愈靠近決策邊界（$\eta \approx 0.5$）猜錯，罰得<strong>愈輕</strong>；
    而那裡剛好就是最容易猜錯的地方。兩個效應互相抵消。</p>

    <p><strong>由此得到一條乾淨的界。</strong>在 $\hat C \neq C^{*}$ 的地方，
    $\hat\eta$ 與 $\eta$ 一定落在 0.5 的兩側，所以
    $\left|\eta - 0.5\right| \le \left|\hat\eta - \eta\right|$，代進去：</p>
    $$R(\hat C) - R(C^{*}) \;\le\; 2\,E\left|\hat\eta(X) - \eta(X)\right|$$

    <p><strong>這條界是單向的，而單向正是重點。</strong>
    機率估得準 $\Rightarrow$ 分類一定準；
    但<strong>反過來完全不成立</strong>——機率可以估得一塌糊塗，分類卻幾乎沒有損失。
    這就是講義那句<strong>「對 $\hat C(x)$ 的衝擊小於對 $\hat p_k(x)$」</strong>的數學內容。</p>

    <p><strong>但不要過度樂觀。</strong>講義用的字是<strong>「一樣會隨著維度增加而失效」</strong>——
    分類<strong>還是會</strong>壞掉，只是慢一點：<br>
    <strong>·</strong> 「排名弄反」的那一層薄殼繞在決策邊界附近。維度一高、鄰域不再局部，
    $\hat\eta$ 的誤差變大，這層殼就跟著變厚。<br>
    <strong>·</strong> 如果你真正要的是<strong>機率本身</strong>——風險分數、期望損失、
    調整門檻、畫 ROC——那就<strong>沒有這層保護</strong>，$\hat p_k$ 的誤差會原封不動傳下去。
    什麼時候需要機率、什麼時候只需要標籤，是<a href="classification.html">第 4 章</a>的主題。</p>""")])


BODIES["bayes"] = f"""
  <p>前面全都在講迴歸。搬到分類問題，觀念一個都不用丟，只要換掉量尺：
  把 MSE 換成<strong>錯誤率</strong>（error rate）。</p>

  <p class="core-backfill">條件機率還不熟時，可先複習
  <a href="s2_conditional.html#conditional">S2 的條件機率</a>與
  <a href="s2_conditional.html#bayes">Bayes 公式</a>。</p>

  $$\\text{{訓練錯誤率}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} I(y_i \\neq \\hat y_i),
    \\qquad \\text{{測試錯誤率}} = \\mathrm{{Ave}}\\left(I(y_0 \\neq \\hat y_0)\\right)$$

  <p>$I(\\cdot)$ 是指示變數：分錯是 1、分對是 0，所以這個式子就是「分錯的比例」。
  跟迴歸一樣，我們在意的是測試錯誤率，而訓練錯誤率會系統性偏低。</p>

  <h3>Bayes 分類器：分類錯誤率的理論下限</h3>

  <p><strong>先把「最佳」的框架講清楚，因為它跟迴歸是同一套。</strong>
  PART 02 說「最好的預測是條件期望」時，前提是<strong>用平方誤差算帳</strong>；
  換成絕對誤差，最佳解就變成條件中位數。也就是說，「什麼叫最好」永遠是
  <strong>先挑一個損失函數 $L$，再在每一點上最小化條件期望損失</strong>：</p>

  $$a^{{*}}(x) = \\arg\\min_{{a}} E\\left[L(Y, a) \\mid X = x\\right]$$

  <p>分類問題只是把損失換成 <strong>0–1 損失</strong>（分錯罰 1、分對罰 0），
  因為這裡的量尺是錯誤率。同一個框架再跑一次，答案就從「條件<strong>期望</strong>」
  變成「條件<strong>眾數</strong>」——把 $x_0$ 指派給條件機率最大的那個類別：</p>

  $$\\text{{把 }} x_0 \\text{{ 指派給使 }} \\Pr(Y = j \\mid X = x_0) \\text{{ 最大的 }} j$$

  <p>這叫做 <strong>Bayes 分類器</strong>。兩類問題裡，它就是
  「$\\Pr(Y = 1 \\mid X = x_0) > 0.5$ 就猜 1，否則猜 2」。
  機率恰好等於 0.5 的那條線是 <strong>Bayes 決策邊界</strong>。
  它達到的母體風險是<strong>所有分類器期望錯誤率的下限</strong>：</p>

  $$\\text{{Bayes 錯誤率}} = 1 - E\\left[\\max_j \\Pr(Y = j \\mid X)\\right]$$

{BAYES_FRAME}

  <p>講義第 34 頁只寫了一句「Bayes 分類器的（母體）錯誤率最小」，
  這裡把它證出來，順便看它跟迴歸那條有多像：</p>

{BAYES_PROOF}

  <p>只要有一塊 $x$（機率為正）上沒有任何類別的條件機率是 1，它就大於 0——
  也就是兩類在母體裡本來就重疊。
  <strong>Bayes 錯誤率就是分類問題版本的不可縮減誤差。</strong>
  下面這個元件把「重疊」直接畫出來：</p>

{viz(svg("w02bayesSvg", 300),
     [info_card("怎麼玩這個元件",
                '兩個等權重的常態分佈代表兩個類別。'
                '第一個滑桿拉開它們的平均值差距，第二個滑桿改變共同的 σ。'
                '<strong>橘色陰影就是重疊的部分，面積的一半就是 Bayes 錯誤率。</strong>'
                '兩個先驗相等時決策邊界固定在中線（紫色虛線）。', "ISLP 式 2.11"),
      rows_card("即時數字",
                [("平均值差距 Δμ", "2.0", "w02bayesGap"),
                 ("共同標準差 σ", "1.00", "w02bayesSd"),
                 ("標準化距離 Δμ ⁄ σ", "—", "w02bayesZ"),
                 ("Bayes 錯誤率", "—", "w02bayesErr"),
                 ("最高可能正確率", "—", "w02bayesAcc")]),
      info_card("為什麼是 Φ(−Δμ ⁄ 2σ)",
                '先驗相等、σ 相同時，邊界落在兩個平均值的中點。'
                '某一類被分錯的機率就是它落到中點另一邊的機率，'
                '也就是標準常態在 −Δμ ⁄ 2σ 以下的機率。'
                'Δμ = 0 時兩類完全重疊，錯誤率 0.500——'
                '此時<strong>任何</strong>分類器都只能瞎猜。')],
     "w02bayesStatus", "拉開兩類的距離或縮小 σ，看 Bayes 錯誤率怎麼掉。",
     '<div class="slider-row" style="flex:1;min-width:190px;">'
     '<span class="slider-label">Δμ</span>'
     '<input type="range" id="w02bayesD" min="0" max="4" step="0.1" value="2" '
     'oninput="w02bayesDraw()">'
     '<span class="slider-val" id="w02bayesDVal">2.0</span></div>'
     '<div class="slider-row" style="flex:1;min-width:190px;">'
     '<span class="slider-label">σ</span>'
     '<input type="range" id="w02bayesS" min="0.4" max="1.6" step="0.05" value="1" '
     'oninput="w02bayesDraw()">'
     '<span class="slider-val" id="w02bayesSVal">1.00</span></div>',
     provenance=("book-redraw", "依講義式 2.11 的兩類常態模型重繪"))}

  <h3>KNN：不知道真實機率時的替代方案</h3>

  <p>Bayes 分類器要求你知道 $\\Pr(Y \\mid X)$——真實資料上不可能。
  <strong>K 最近鄰</strong>（K-nearest neighbors, KNN）用鄰近樣本的類別比例估計它：
  找出離 $x_0$ 最近的 $K$ 個訓練點（記作 $\\mathcal{{N}}_0$），數一數裡面各類佔幾成。</p>

  $$\\widehat{{\\Pr}}(Y = j \\mid X = x_0)
    = \\frac{{1}}{{K}} \\sum_{{i \\in \\mathcal{{N}}_0}} I(y_i = j)$$

  <p>然後指派給比例最高的那一類。KNN 不預設固定維度的函數形式，但仍依賴距離、變數尺度，
  以及「鄰近的 X 有相近條件分佈」這項局部假設。在這個基本元件裡，$K$ 是控制平滑程度的旋鈕：
  <strong>$1/K$ 可視為 KNN 的彈性度</strong>。</p>

  <p>看到這裡應該會有一個疑問：<strong>PART 03 不是說最近鄰在高維會壞掉嗎？</strong>
  講義第 33 頁把話補完了——會壞，但分類壞得比較慢：</p>

{info("講義第 33 頁怎麼說", '''最近鄰平均在分類上一樣可以照用。
  它<strong>同樣會隨著維度增加而失效</strong>。
  不過，<strong>它對 Ĉ(x) 的衝擊小於對 p̂<sub>k</sub>(x) 的衝擊</strong>。<br>
  也就是說：<strong>估「機率」會被維度詛咒打得很慘，估「哪一類」則相對耐打。</strong>
  這不是安慰的話，可以寫成不等式。''')}

{CLS_ROBUST}

{viz(svg("w02knnSvg", 400),
     [info_card("怎麼看這張圖",
                '底色是 KNN 的<strong>決策區域</strong>（30 × 30 格點，各自問一次 KNN 要猜哪一類），'
                '紫色虛線是<strong>真實的 Bayes 決策邊界</strong>，圓點是 200 筆訓練資料。'
                '按鈕切換 K，看區域從破碎變成平滑。', "ISLP 圖 2.15–2.16"),
      rows_card("這個 K 的表現",
                [("K", "10", "w02knnK"),
                 ("彈性度 1 ⁄ K", "0.100", "w02knnInv"),
                 ("訓練錯誤率", "—", "w02knnTrain"),
                 ("測試錯誤率（5000 筆）", "—", "w02knnTest"),
                 ("Bayes 錯誤率（母體值的估計）", "0.1382", "w02knnBayes")]),
      info_card("三個 K 的結果",
                '<strong>K = 1：</strong>訓練錯誤率 0.000，測試 0.1964。'
                '邊界破碎，抓到的是雜訊——低偏差、極高變異。<br>'
                '<strong>K = 10：</strong>測試 0.1470，最接近 Bayes 錯誤率。<br>'
                '<strong>K = 100：</strong>測試 0.1758。邊界過度平滑、快變成直線——'
                '高偏差、低變異。')],
     "w02knnStatus", "切換 K，看決策區域與 Bayes 邊界（紫色虛線）差多少。",
     '<button class="btn btn-toggle" onclick="w02knnSet(1)">K = 1</button>'
     '<button class="btn btn-toggle" onclick="w02knnSet(10)">K = 10</button>'
     '<button class="btn btn-toggle" onclick="w02knnSet(100)">K = 100</button>',
     provenance=("simulation", "固定種子模擬；對照 ISLP 圖 2.15–2.16"))}

{info("Bayes 錯誤率算不出來，那講它有什麼用", '''<strong>1. 它給出母體期望錯誤率的理論下限。</strong>
  經重複評估得到的分類風險已逼近估計的 Bayes 錯誤率時，可優先考慮蒐集新變數，
  跟 P01 那個「測試 MSE 逼近 Var(ε)」的判斷完全平行。<br>
  <strong>2. 它提供模擬研究的比較基準。</strong>在已知真實分佈的模擬資料上它算得出來，
  這時「離下限多遠」比「錯誤率多少」有意義得多，上面那個元件就是這樣用的。<br>
  <strong>3. 它提供先估機率、再決定標籤的做法。</strong>
  Bayes 分類器的形式是「比較條件機率的大小」，所以第 4 章的邏輯斯迴歸、LDA、Naive Bayes
  全都在做同一件事：各用不同的假設去估那個條件機率，再套上同一個「取最大」的規則。''')}

  <p>KNN 元件已經同時列出 K = 1、10、100 的訓練與獨立測試錯誤，足以看見
  「訓練誤差偏好高彈性、測試誤差不一定」的差異。</p>

  <h3 id="dx-bool">講義完整實作：錯誤率其實就是布林陣列取平均</h3>

{card("講義 02 · 用布林陣列挑出「屬於這一類」的資料",
      lab_code(CH, 164) + "\n\n" + lab_code(CH, 171), lab_output(CH, 171),
      src=src("162、164、171"),
      note="<code>keep_rows</code> 是一個布林陣列，<code>A[keep_rows]</code> 只留下 "
           "<code>True</code> 的那幾列。KNN 在數「鄰居裡有幾個屬於類別 j」時做的就是這件事："
           "先算出一個布林陣列，再數它。"
           "注意 lab 的整數索引與布林索引對照：<code>np.array([0,1,0,1])</code> 雖然跟 "
           "<code>keep_rows</code> 用 <code>==</code> 比是相等的，"
           "但當索引用時 <strong>numpy 會把整數當位置、把布林當遮罩</strong>，結果完全不同。")}

{card("講義 02 · 布林取平均就是比例", lab_code(CH, 244), lab_output(CH, 244),
      src=src("243、244"),
      note="<code>np.isnan(D[col]).mean()</code>：對布林陣列取平均，"
           "<code>True</code> 當 1、<code>False</code> 當 0，"
           "算出來就是「成立的比例」。錯誤率 (1/n)ΣI(yᵢ ≠ ŷᵢ) 完全是同一個動作，"
           "程式上寫成 <code>(y != y_hat).mean()</code>。"
           "指示變數 I(·) 在 Python 裡就是一個布林陣列。")}

{qa("觀念釐清", [
    ("Q：本頁 KNN 的 K = 1 為什麼訓練錯誤率是 0，這代表它很好嗎？",
     "<p>K = 1 時，要預測訓練點 $x_i$ 的類別，KNN 會去找「離 $x_i$ 最近的 1 個訓練點」——"
     "而那個點<strong>就是 $x_i$ 自己</strong>，距離 0。本頁資料沒有重複的 X，實作也把自己算進鄰居，"
     "所以它回報自己的標籤，訓練錯誤率為 0。若相同 X 出現相反標籤，或評分時排除自己，就沒有這項保證。</p>"
     "<p>這個 0 本身不能證明過度擬合；還要和較不彈性模型的新資料表現比較。"
     "它也不能提供泛化表現的證據，因為使用的是擬合時那批資料。"
     "跟迴歸那邊「通過每一個點的曲線訓練 MSE = 0」是同一種評估問題。"
     "本頁的模擬裡，K = 1 的測試錯誤率是 0.1964，是所有 K 之中最差的幾個之一，"
     "而 Bayes 下限只有 0.1382。</p>"
     "<p>那 K = 1 有什麼用？它是<strong>彈性的極端</strong>："
     "偏差極低（決策邊界可以任意扭曲）、變異極高（換一份訓練資料邊界就整個變樣）。"
     "資料量非常大、雜訊非常小的時候，K = 1 是可以贏的。ISLP 第 4 章與第 9 章"
     "會再回到這個取捨。"),
])}

{quiz("qKnn", "QUIZ · Bayes 分類器與 KNN",
      "在一份二維兩類資料上，你發現 K = 1 的測試錯誤率比 K = 25 高很多。"
      "最合理的解讀是什麼？",
      [(True, "K = 1 太有彈性，決策邊界抓到了訓練資料的雜訊；K = 25 平滑掉雜訊後更接近真實邊界",
        "對。K 小 → 低偏差、高變異。當 Bayes 邊界不是特別破碎、而資料又有相當的重疊時，"
        "平滑一點反而更接近真相。這就是 ISLP 圖 2.17 那條 U 型測試曲線的左半邊。"),
       (False, "K = 1 的訓練錯誤率是 0，所以它一定過度擬合；K 愈大一定愈好",
        "兩個「一定」都不成立。K = 1 的訓練錯誤率即使是 0，也要看到較不彈性模型的測試表現更好，才能判定過度擬合。K 一直加大還會走到另一個極端："
        "本頁的模擬裡 K = 150 的測試錯誤率是 0.2270，比 K = 1 的 0.1964 還糟。"
        "本頁模擬的測試錯誤率呈 U 型，兩端都不好。"),
       (False, "這表示資料的 Bayes 錯誤率很高，換任何 K 都沒有用",
        "不對。Bayes 錯誤率高會讓<strong>所有</strong> K 的錯誤率一起抬高，"
        "但不同 K 之間的差距反映的是各方法估計條件機率與決策邊界的品質，"
        "不是 Bayes 錯誤率本身。<strong>注意迴歸那條三項拆解不能原封不動搬到 0–1 損失</strong>——"
        "分類的超額風險有自己的寫法，見本節後面的補充。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 2.4 第 1 題（b)(d)",
      "第 1 題問「彈性方法會比不彈性方法好還是差」。"
      "考慮 (b) p 極大而 n 很小，以及 (d) 誤差項的變異 σ² = Var(ε) 極大。這兩種情況呢？",
      [(True, "兩種情況都<strong>比較差</strong>：(b) 資料不夠支撐彈性方法，(d) 彈性方法會去擬合雜訊",
        "對。(b) n 小 p 大時，彈性方法的變異會很大，這是維度詛咒的直接後果。"
        "(d) σ² 大表示資料裡的隨機成分多，彈性方法會把那些隨機起伏當成訊號學進去——"
        "而那些起伏在測試資料上完全不會重現。"
        "順便記住另兩小題：(a) n 極大 p 小 → 彈性<strong>較好</strong>；"
        "(c) 關係高度非線性 → 彈性<strong>較好</strong>。"),
       (False, "(b) 較差、(d) 較好，因為雜訊大的時候更需要彈性去捕捉細節",
        "(d) 的判斷剛好相反。雜訊大的時候那些「細節」<strong>就是雜訊</strong>，"
        "捕捉它們只會讓測試誤差變大。σ² 大時應該更保守，選偏差稍高但變異低的方法。"),
       (False, "兩種情況都<strong>比較好</strong>，因為彈性方法適用範圍更廣",
        "不對。彈性方法的優勢建立在「有足夠資料」與「訊號比雜訊強」這兩個前提上。"
        "兩個前提都不成立時（正是 (b) 與 (d)），它會輸給簡單模型。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 2.4 第 2 題（a)",
      "第 2 題 (a)：蒐集美國前 500 大公司的資料，每家記錄「利潤、員工數、產業、CEO 薪水」，"
      "想了解<strong>哪些因素影響 CEO 薪水</strong>。這是什麼問題、n 與 p 是多少？",
      [(True, "迴歸問題、目的是推論，n = 500、p = 3",
        "對。CEO 薪水是連續的數值 → 迴歸；「想了解哪些因素影響」是典型的推論而非預測。"
        "反應變數是 CEO 薪水，剩下三個（利潤、員工數、產業）是預測變數，所以 p = 3、n = 500。"),
       (False, "分類問題、目的是預測，n = 500、p = 4",
        "兩處都錯。反應變數是薪水（連續數值），不是類別，所以是迴歸；"
        "而 p 要<strong>扣掉反應變數本身</strong>，四個欄位裡有一個是 Y，所以 p = 3。"),
       (False, "迴歸問題、目的是預測，n = 500、p = 3",
        "n 與 p 對了，但目的判斷錯。題目說的是「理解哪些因素會影響」——"
        "目的是理解因素與薪水的關係，屬於推論。"
        "如果題目改成「猜這位新任 CEO 會拿多少」，那才是預測。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 2.4 第 3 題（a)(b)",
      "第 3 題要你在同一張圖上畫五條曲線（偏差²、變異、訓練誤差、測試誤差、Bayes／不可縮減誤差），"
      "橫軸是彈性。哪一組形狀是對的？",
      [(True, "偏差²單調下降、變異單調上升、訓練誤差單調下降、測試誤差 U 型、"
              "不可縮減誤差是一條水平線",
        "對，這就是本頁 P05 那張圖再加上訓練誤差。三個關鍵："
        "期望測試誤差 = 偏差² + 變異 + 不可縮減，所以它<strong>不低於那條水平線</strong>；"
        "訓練誤差<strong>可以</strong>降到水平線之下（甚至到 0），因為這些資料已參與擬合；"
        "測試誤差的最低點落在「偏差²下降速度 = 變異上升速度」的地方"
        "（這是把彈性當成連續、且最低點在內部時的說法；離散的 df 或最低點在端點時就不適用）。"
        "另外請注意這題問的是<strong>典型形狀</strong>：單調下降的偏差²與單調上升的變異是常見趨勢，"
        "不是每個問題都必然如此。"),
       (False, "偏差²與變異都單調下降，訓練誤差與測試誤差都是 U 型",
        "兩處錯。變異隨彈性<strong>上升</strong>（愈彈性的模型換一份資料就變一個樣）；"
        "訓練誤差<strong>單調下降</strong>不會回頭——模型空間變大，最小值只可能更小。"),
       (False, "訓練誤差與測試誤差最後會收斂到同一條線，因為彈性夠高就能學到真實的 f",
        "不對。彈性極高時訓練誤差趨近 0，測試誤差卻因為變異上升而回頭，"
        "兩者的差距<strong>隨彈性擴大</strong>——那個差距正是本頁 P06 講的「樂觀程度」。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 2.4 第 7 題（b）（c）",
      "第 7 題給了六筆資料（X₁, X₂, X₃, Y）："
      "(0,3,0,紅)、(2,0,0,紅)、(0,1,3,紅)、(0,1,2,綠)、(−1,0,1,綠)、(1,1,1,紅)。"
      "要在測試點 X₁ = X₂ = X₃ = 0 上用 KNN 預測。K = 1 與 K = 3 分別預測什麼？",
      [(True, "K = 1 預測綠，K = 3 預測紅",
        "對。到原點的歐氏距離依序是 3、2、√10 ≈ 3.16、√5 ≈ 2.24、√2 ≈ 1.41、√3 ≈ 1.73。"
        "最近的是第 5 筆（√2，綠）→ K = 1 預測<strong>綠</strong>。"
        "最近的三筆是第 5（√2，綠）、第 6（√3，紅）、第 2（2，紅）→ 二比一，"
        "K = 3 預測<strong>紅</strong>。順帶 (d)：Bayes 邊界高度非線性時應該選<strong>小</strong>的 K，"
        "因為小 K 的決策邊界才彎得起來。"),
       (False, "K = 1 預測紅，K = 3 預測紅",
        "K = 1 錯了。第 2 筆的距離為 2；最近的是第 5 筆 (−1,0,1)，"
        "距離 √((−1)² + 0² + 1²) = √2 ≈ 1.41，它的類別是<strong>綠</strong>。"
        "算距離的時候不要漏掉負號那一維。"),
       (False, "K = 1 預測綠，K = 3 預測綠",
        "K = 3 錯了。最近三筆是第 5（綠）、第 6（紅）、第 2（紅），"
        "紅佔 2/3。KNN 是<strong>多數決</strong>，所以預測紅。"
        "第 4 筆 (0,1,2) 的距離是 √5 ≈ 2.24，排第四，沒進前三名。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>迴歸與分類：同一套邏輯的兩種語言</h3>
{table(["", "迴歸（regression）", "分類（classification）"],
       [["Y 是什麼", "數值", "類別"],
        ["量尺", "MSE $= \\frac1n\\sum (y_i - \\hat f(x_i))^2$",
         "錯誤率 $= \\frac1n\\sum I(y_i \\ne \\hat y_i)$"],
        ["最好的預測函數", "迴歸函數 $f(x) = E[Y \\mid X = x]$", "Bayes 分類器（取條件機率最大者）"],
        ["期望風險的理論下限", "$\\mathrm{Var}(\\varepsilon)$（不可縮減誤差）", "Bayes 錯誤率"],
        ["訓練版的問題", "用擬合資料自評會偏樂觀", "用擬合資料自評會偏樂觀（本例 K = 1 時是 0）"],
        ["彈性度的例子", "樣條自由度 df、多項式次數", "KNN 的 $1/K$"],
        ["本頁元件", "w02irr／w02flexfit／w02bv", "w02bayeserr／w02knn／w02knnerr"]])}

  <h3>參數式與非參數式</h3>
{table(["", "參數式", "非參數式"],
       [["固定函數形式", "先指定", "不預先固定"],
        ["仍需的結構", "線性等形式", "平滑、局部相似性、距離或尺度"],
        ["要估的東西", "有限個參數", "整個函數"],
        ["主要風險", "形狀假設錯 → 高偏差", "資料不夠 → 高變異"],
        ["額外要選", "形狀", "平滑程度"],
        ["高維表現", "相對穩健", "容易受維度詛咒影響"],
        ["ISLP 例子", "圖 2.4 線性平面（第 3 章）", "圖 2.5／2.6 薄板樣條（第 7 章）"]])}

  <h3>本頁模擬跑出來的數字</h3>
{table(["樣條自由度 df", "2（線性）", "4", "6", "7", "12", "18", "25"],
       [["訓練 MSE（單一資料集）", "3.432", "1.125", "0.961", "0.955", "0.890", "0.787", "0.480"],
        ["測試 MSE（單一資料集）", "3.260", "1.180", "1.036", "<strong>1.021</strong>",
         "1.072", "1.170", "1.495"],
        ["情境 A 期望測試 MSE", "3.373", "1.249", "1.137", "<strong>1.136</strong>",
         "1.219", "1.332", "1.486"],
        ["情境 B（接近線性）", "<strong>1.047</strong>", "1.077", "1.116", "1.134",
         "1.219", "1.332", "1.486"],
        ["情境 C（高度非線性）", "21.099", "10.146", "4.702", "4.470", "2.432",
         "<strong>1.336</strong>", "1.486"]])}
  <p style="font-size:.82rem;color:var(--muted);">σ = 1，所以 Var(ε) = 1.00 是三列期望測試 MSE 的下限；
  單一有限測試集的 MSE 可能因抽樣波動低於它。
  情境 A、B、C 的最佳 df 分別是 7、2、18。這就是「沒有一個放諸四海皆準的彈性度」。
  數字由 <code>tools/frames/gen_statlearn.py</code> 在 <code>default_rng(524)</code>、
  M = 300 下產生。</p>

{table(["KNN（n = 200 訓練 / 5000 測試）", "K = 1", "K = 10", "K = 50", "K = 100", "K = 150"],
       [["彈性度 1/K", "1.000", "0.100", "0.020", "0.010", "0.0067"],
        ["訓練錯誤率", "<strong>0.000</strong>", "0.135", "0.125", "0.165", "0.240"],
        ["測試錯誤率", "0.1964", "0.1470", "<strong>0.1384</strong>", "0.1758", "0.2270"]])}
  <p style="font-size:.82rem;color:var(--muted);">Bayes 錯誤率 = 0.1382，是母體期望錯誤率的下限；
  這列 5000 筆測試資料的錯誤率是有限樣本估計，可能在下限兩側波動。
  本例 K = 1 的訓練錯誤率為 0，因為 X 不重複且最近的鄰居包含自己。
  課本圖 2.15–2.17 用的是另一份模擬資料，報告 Bayes 0.1304、K = 10 為 0.1363、
  K = 1 為 0.1695、K = 100 為 0.1925——數字不同，形狀一致。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["基本框架", "$Y = f(X) + \\varepsilon$", "式 2.1，$E[\\varepsilon\\mid X] = 0$"],
        ["迴歸函數", "$f(x) = E[Y \\mid X = x]$", "平方誤差下最好的預測函數"],
        ["兩種誤差",
         "$E(Y-\\hat Y)^2 = [f(X)-\\hat f(X)]^2 + \\mathrm{Var}(\\varepsilon)$",
         "式 2.3，$\\hat f$ 與 $X$ 固定"],
        ["線性模型", "$f(X) = \\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p$",
         "式 2.4，參數式的代表"],
        ["MSE", "$\\frac1n\\sum_{i=1}^{n}(y_i - \\hat f(x_i))^2$", "式 2.5"],
        ["偏差–變異拆解",
         "$E(y_0-\\hat f(x_0))^2 = \\mathrm{Var}(\\hat f(x_0)) + [\\mathrm{Bias}(\\hat f(x_0))]^2 "
         "+ \\mathrm{Var}(\\varepsilon)$", "式 2.7；ESL 式 7.9 同"],
        ["KNN 迴歸的拆解",
         "$\\sigma_\\varepsilon^2 + [f(x_0) - \\frac1k\\sum_\\ell f(x_{(\\ell)})]^2 "
         "+ \\frac{\\sigma_\\varepsilon^2}{k}$", "ESL 式 7.10，變異就是 $\\sigma^2/k$"],
        ["錯誤率", "$\\frac1n\\sum_{i=1}^{n} I(y_i \\ne \\hat y_i)$", "式 2.8／2.9"],
        ["Bayes 分類器", "取使 $\\Pr(Y=j \\mid X=x_0)$ 最大的 $j$", "式 2.10"],
        ["Bayes 錯誤率", "$1 - E[\\max_j \\Pr(Y=j \\mid X)]$", "式 2.11，分類版的不可縮減誤差"],
        ["KNN 機率估計",
         "$\\frac1K\\sum_{i \\in \\mathcal{N}_0} I(y_i = j)$", "式 2.12；本頁以 $1/K$ 表示相對彈性"]])}

{info("三個一定要記住的觀念", '''<strong>1. 期望測試 MSE 不低於 Var(ε)。</strong>
  拆解式的三項都非負；分類版則是母體期望錯誤率不低於 Bayes 錯誤率。
  有限測試集的估計值會波動，不能把母體下限當成每次觀察值的硬界線。<br>
  <strong>2. 巢狀模型的訓練目標單調不增，測試誤差常呈 U 型。</strong>
  前者來自模型空間擴大；後者是一般趨勢，最低點可能在端點。本例 K = 1 的訓練錯誤率為 0，
  仍須比較新資料表現才能判定過度擬合。<br>
  <strong>3. 偏差與變異的期望是對「重複抽訓練集」取的。</strong>
  變異是「換一份訓練資料，f̂ 會變多少」，不是「f̂ 這條曲線起伏多大」。
  真實資料上、不知道真實 f 時，通常沒辦法把兩者分開算出來；
  特定模型假設或重抽樣之下可以估其中一部分，而第 5 章的交叉驗證估的是<strong>整體預測風險</strong>。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
# COVERAGE-20260910 BEGIN

# 原有完整證明保留原文，統一為可驗收的預設收合元件。
import re as _coverage_re
for _key, _old, _pid in [('irreducible', IRR_PROOF, 'w02proofIrr'),
        ('regfunc', REG_PROOF, 'w02proofMean'), ('mse', MSE_PROOF, 'w02proofRisk'),
        ('biasvar', BV_PROOF, 'w02proofBV'), ('bayes', BAYES_PROOF, 'w02proofBayes'),
        ('bayes', CLS_ROBUST, 'w02proofRobust')]:
    _m = _coverage_re.search(r'<summary>(.*?)</summary>\s*<div class="qa-a">(.*)</div>\s*</details>', _old, _coverage_re.S)
    assert _m, _pid
    BODIES[_key] = BODIES[_key].replace(_old, proof(_pid, _m[1], _m[2]))
BODIES['bayes'] += r"""
<h3>KNN 的彈性與有效自由度</h3>
<p>對固定的訓練輸入，KNN <strong>迴歸</strong>把鄰居的 y 平均，可寫成 $\hat y=Sy$。鄰域只由 X 決定、每點使用 K 個等權鄰居且包含自己時，線性平滑器的有效自由度為 $\operatorname{tr}(S)=n/K$。K 越小，模型保留越多訓練反應的個別變動。這個等式使用線性迴歸平滑器的定義；分類的多數決含非線性門檻，不能直接照搬。</p>
<p>例如 n=100、K=5 時 df=20；K=1 時 df=100，因為每點直接記住自己的 y。距離同分須固定處理方式；若不含自身，不能再使用上述對角線計算。</p>
""" + proof('w02proofKnnDf', '固定鄰域 KNN 迴歸的 n/K', r"""
<p>令 $S_{ij}=I\{j\in N_K(i)\}/K$，便有 $\hat y_i=\sum_jS_{ij}y_j$。自點包含於鄰域使 $S_{ii}=1/K$，故 $\operatorname{tr}(S)=\sum_iS_{ii}=n/K$。</p>
<p>若給定 X 後 $\operatorname{Cov}(y)=\sigma^2I$，則 $\operatorname{Cov}(\hat y_i,y_i)=\sigma^2S_{ii}$。用 $\sum_i\operatorname{Cov}(\hat y_i,y_i)/\sigma^2$ 定義自由度也得到相同結果。</p>
""")


BODIES['tradeoff'] += r"""
<h3>訓練與測試都不理想時，先找哪一種原因？</h3>
<p>先確認資料、損失定義與程式正確，再比較訓練及獨立驗證表現。訓練誤差也很高，可能是模型類太受限，也可能是最佳化尚未找到這個模型能達到的解。前者可考慮更合適的特徵或更有彈性的模型；後者先檢查最佳化過程，不能只靠加資料。</p>
<p>訓練誤差低而驗證誤差高，既可能是過度擬合，也可能是資料分布不一致（distribution mismatch）：例如訓練資料來自成人，而預測對象換成兒童。前者可考慮減少彈性、正則化或取得更多同分布訓練資料；後者需要檢查來源、收集與預測情境。只看兩個誤差數字不能辨認原因，須配合資料設計、學習曲線與誤差分析。</p>
<p>這是講義連結的<a href="https://speech.ee.ntu.edu.tw/~hylee/ml/ml2021-course-data/overfit-v6.pdf">模型誤差診斷流程</a>的閱讀方式；第二章的偏差–變異公式預設同一資料生成分布，不能自動解釋任意分布轉移。</p>
"""

# COVERAGE-20260910 END

# LINK-CLOSURE-CH1-3

BODIES['curse'] += r"""
<h3>高維球的體積集中在哪裡？</h3>
<p>在 p 維半徑 R 的球中均勻取點，距離中心不超過 $(1-\delta)R$ 的機率為 $(1-\delta)^p$。
所以外側厚度 $\delta R$ 的球殼占比是</p>
$$P\{(1-\delta)R&lt;\|X\|\le R\}=1-(1-\delta)^p,\qquad0\le\delta\le1.$$
<p>例如外側 10% 厚度，在二維占 $1-0.9^2=19\%$，十維占約 65.1%，五十維占約 99.5%。
這是<strong>均勻球內取樣</strong>的結論；真實資料不一定均勻分布在球內，也不能直接套到任意核距離。
它補充了「內接球在立方體中占比很小」以外的另一個現象：即使只看球本身，靠近中心的體積比例也很小。</p>
""" + proof('w02proofBallVolume','球體積公式與球殼占比',r"""
<p>令 Aₚ 為單位球面面積。高斯積分分別用直角座標與極座標計算：</p>
$$\pi^{p/2}=\int_{\mathbb R^p}e^{-\|x\|^2}\,dx
=A_p\int_0^\infty e^{-r^2}r^{p-1}\,dr=\frac{A_p}{2}\Gamma(p/2).$$
<p>所以半徑 R 球體積為 $A_pR^p/p=\pi^{p/2}R^p/\Gamma(p/2+1)$。
球體積與半徑的 p 次方成正比，內球除以外球即為 $(1-\delta)^p$；取補集得到球殼比例。</p>
""") + r"""
<p class="source-note">來源：講義 02 p.15 指向的 <a href="https://ttic.edu/blum/book.pdf#page=16">Blum、Hopcroft、Kannan，Foundations of Data Science，§2.3–2.4.1，pp.16–19</a>。
只延伸本節直接相關的高維幾何，不要求讀完整本書。</p>
"""


PAGEJS = r"""
/* ===== statistical_learning 本頁元件（id 與全域一律 w02 前綴）=====
   SVG 元件的初始化一律放在 HC.ready() 外面：Chart.js 從 CDN 載不到時
   HC.ready() 不會執行，SVG 元件不能跟著死掉。 */

/* ---------- P01 可縮減 vs 不可縮減誤差（live，閉式解） ---------- */
const w02irrN = 40;
const w02irrX = [];
const w02irrZ = [];
function w02irrF(x) { return 5 + 2.2 * Math.sin(x / 1.6) + 0.22 * x; }
(() => {
  const rand = HC.stat.lcg(20260202);
  for (let i = 0; i < w02irrN; i++) {
    w02irrX.push(0.3 + i * (9.4 / (w02irrN - 1)) + 0.1 * (rand() - 0.5));
    w02irrZ.push(HC.stat.normal(rand));
  }
})();
let w02irrSvc = null;
let w02irrShowLin = true;
function w02irrSetup() {
  w02irrSvc = HC.svg('w02irrSvg', { xd: [0, 10], yd: [-2.5, 14.5], h: 320 });
}
function w02irrToggleLin() { w02irrShowLin = !w02irrShowLin; w02irrDraw(); }
function w02irrDraw() {
  const s = w02irrSvc;
  if (!s) return;
  const sig = parseFloat($('w02irrSig').value);
  $('w02irrSigVal').textContent = HC.fmt(sig, 1);
  s.grid(5, 4, { xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0 });
  const g = s.clearLayer('main');
  const band = [];
  for (let i = 0; i <= 100; i++) {
    const x = i / 10;
    band.push([x, w02irrF(x) + sig, w02irrF(x) - sig]);
  }
  s.area(band, { cls: 'aux', fill: 'rgba(26,107,74,.12)' }, g);
  s.poly(band.map(p => [p[0], (p[1] + p[2]) / 2]), { cls: 'truef' }, g);
  const ys = w02irrX.map((x, i) => w02irrF(x) + sig * w02irrZ[i]);
  const fit = HC.stat.ols(w02irrX, ys);
  // 在獨立的密集 x 網格上積分，而不是把模型拿回訓練點自評。
  // 條件於目前這個已擬合的 f-hat，期望測試 MSE = sigma^2 + approximation error。
  const xTest = HC.stat.seq(0, 10, 401);
  const reducible = HC.stat.mean(xTest.map(x =>
    (w02irrF(x) - (fit.b0 + fit.b1 * x)) ** 2));
  const perfect = sig * sig;
  const lin = perfect + reducible;
  if (w02irrShowLin) {
    s.poly([[0, fit.b0], [10, fit.b0 + fit.b1 * 10]], { cls: 'fit' }, g);
  }
  w02irrX.forEach((x, i) => s.dot(x, ys[i], {
    r: 4, fill: HC.tok.train, stroke: '#fff', sw: 1,
  }, g));
  s.txtPx(s.pad.l + 6, 24, '綠虛線＝真實的 f（固定不動） · 綠帶＝f ± σ'
    + (w02irrShowLin ? ' · 紅線＝線性 f̂' : ''), { cls: 'axtitle' }, g);
  $('w02irrSigma').textContent = HC.fmt(sig, 1);
  $('w02irrVar').textContent = HC.fmt(sig * sig, 2);
  $('w02irrPerfect').textContent = HC.fmt(perfect, 2);
  $('w02irrLin').textContent = HC.fmt(lin, 2);
  $('w02irrGap').textContent = HC.fmt(reducible, 2);
  setStatus('w02irrStatus', 'σ = ' + HC.fmt(sig, 1) + ' ⇒ 不可縮減下限 Var(ε) = '
    + HC.fmt(sig * sig, 2) + '。在獨立 x 網格上，完美 f 的期望測試 MSE 是 '
    + HC.fmt(perfect, 2) + '；目前線性 f̂ 的期望測試 MSE 是 ' + HC.fmt(lin, 2)
    + '，其中 ' + HC.fmt(reducible, 2) + ' 是可縮減部分。');
}

/* ---------- P04 同資料三種擬合（baked，ISLP 圖 2.9） ---------- */
let w02flexDf = 6;
let w02fitSvc = null;
let w02mseSvc = null;
function w02flexSetup() {
  const F = FRAMES_w02flex;
  const lo = Math.min(...F.y, ...F.truef) - 1.2;
  const hi = Math.max(...F.y, ...F.truef) + 1.2;
  w02fitSvc = HC.svg('w02fitSvg', { xd: [0, 100], yd: [lo, hi], h: 300 });
  const mx = Math.max(...F.trainMse, ...F.testMse) * 1.15;
  w02mseSvc = HC.svg('w02mseSvg', { xd: [0, 26], yd: [0, mx], h: 250 });
}
function w02flexSet(d) { w02flexDf = d; w02flexDraw(); }
function w02flexDraw() {
  const F = FRAMES_w02flex;
  const idx = F.dfs.indexOf(w02flexDf);
  const s = w02fitSvc;
  if (!s) return;
  s.grid(5, 4, { xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0 });
  const g = s.clearLayer('main');
  s.poly(F.grid.map((x, i) => [x, F.truef[i]]), { cls: 'truef' }, g);
  const fit = F.fits[String(w02flexDf)];
  if (fit) s.poly(F.grid.map((x, i) => [x, fit[i]]), { cls: 'fit' }, g);
  F.x.forEach((x, i) => s.dot(x, F.y[i], {
    r: 3.6, fill: HC.tok.train, stroke: '#fff', sw: 0.9,
  }, g));
  s.txtPx(s.pad.l + 6, 24, '綠虛線＝真實的 f · 紅線＝df = ' + w02flexDf + ' 的擬合 · '
    + F.nTrain + ' 個訓練點', { cls: 'axtitle' }, g);

  const m = w02mseSvc;
  m.grid(6, 4, { xtitle: '樣條自由度 df（彈性 →）', ytitle: 'MSE', xdec: 0, ydec: 1 });
  const gm = m.clearLayer('main');
  m.poly([[0, F.sigma2], [26, F.sigma2]],
         { cls: 'aux', stroke: HC.tok.muted, sw: 1.4, dash: '5 4' }, gm);
  m.txtPx(m.X(26) - 4, m.Y(F.sigma2) - 6, 'Var(ε) = ' + HC.fmt(F.sigma2, 2),
          { cls: 'axlab', anchor: 'end' }, gm);
  m.poly(F.dfs.map((d, i) => [d, F.trainMse[i]]),
         { cls: 'aux', stroke: HC.tok.muted, sw: 2.4 }, gm);
  m.poly(F.dfs.map((d, i) => [d, F.testMse[i]]),
         { cls: 'aux', stroke: HC.tok.test, sw: 2.6 }, gm);
  F.show.forEach(d => {
    const j = F.dfs.indexOf(d);
    m.dot(d, F.trainMse[j], { r: 4, fill: HC.tok.muted, stroke: '#fff', sw: 1 }, gm);
    m.dot(d, F.testMse[j], { r: 4.4, fill: HC.tok.test, stroke: '#fff', sw: 1 }, gm);
  });
  if (idx >= 0) {
    m.seg(w02flexDf, 0, w02flexDf, m.yd[1],
          { cls: 'aux', stroke: HC.tok.resid, sw: 1.8, dash: '4 3' }, gm);
  }
  m.txtPx(m.pad.l + 6, 22, '灰＝巢狀模型訓練 MSE（單調不增） · 紅＝本次有限測試 MSE · 紫＝目前 df',
          { cls: 'axtitle' }, gm);

  $('w02flexDfVal').textContent = String(w02flexDf);
  $('w02flexTrain').textContent = idx >= 0 ? HC.fmt(F.trainMse[idx], 3) : '—';
  $('w02flexTest').textContent = idx >= 0 ? HC.fmt(F.testMse[idx], 3) : '—';
  $('w02flexVar').textContent = HC.fmt(F.sigma2, 2);
  const best = F.dfs[F.testMse.indexOf(Math.min(...F.testMse))];
  const tag = w02flexDf === 2 ? '彈性不足：直線無法呈現彎曲的關係，偏差大'
    : (w02flexDf >= 25 ? '彈性過高：擬合雜訊，訓練 MSE 最小，但測試 MSE 已從最低點回升'
      : '差不多剛好：測試 MSE 接近最低點');
  setStatus('w02flexStatus', 'df = ' + w02flexDf + '：訓練 MSE '
    + HC.fmt(F.trainMse[idx], 3) + '、測試 MSE ' + HC.fmt(F.testMse[idx], 3)
    + '（期望風險下限 Var(ε) = ' + HC.fmt(F.sigma2, 2) + '；有限測試值可波動；本次最佳 df = ' + best + '）。' + tag + '。');
}

/* ---------- P05 偏差–變異拆解掃描器（baked，ISLP 圖 2.12） ---------- */
let w02bvKey = 'A';
function w02bvSet(k) { w02bvKey = k; w02bvDraw(); }
function w02bvDraw() {
  const F = FRAMES_w02bv;
  const s = F.scen[w02bvKey];
  const irr = F.dfs.map(() => F.sigma2);
  const top = Math.max(...s.total) * 1.06;
  HC.line('w02bvChart', {
    labels: F.dfs,
    datasets: [
      { label: '期望測試 MSE', data: s.total, borderColor: HC.tok.test,
        backgroundColor: HC.tok.test, borderWidth: 3, pointRadius: 3.4, fill: false },
      { label: '偏差²', data: s.bias2, borderColor: HC.tok.accent2,
        backgroundColor: HC.tok.accent2, borderWidth: 2.2, pointRadius: 2.6, fill: false },
      { label: '變異', data: s['var'], borderColor: HC.tok.accent3,
        backgroundColor: HC.tok.accent3, borderWidth: 2.2, pointRadius: 2.6, fill: false },
      { label: 'Var(ε)', data: irr, borderColor: HC.tok.muted,
        borderWidth: 1.6, borderDash: [6, 4], pointRadius: 0, fill: false },
    ],
  }, {
    scales: {
      x: { title: { display: true, text: '樣條自由度 df（彈性 →）' } },
      y: { min: 0, suggestedMax: top, title: { display: true, text: '期望測試 MSE 的三個組成項' } },
    },
  });
  const c = HC.get('w02bvChart');
  HC.refs(c, [HC.vline(s.argmin, '最低點 df = ' + F.dfs[s.argmin])]);
  $('w02bvScen').textContent = s.label;
  $('w02bvBest').textContent = String(F.dfs[s.argmin]);
  $('w02bvTot').textContent = HC.fmt(s.total[s.argmin], 3);
  $('w02bvBias').textContent = HC.fmt(s.bias2[s.argmin], 3);
  $('w02bvVarv').textContent = HC.fmt(s['var'][s.argmin], 3);
  $('w02bvIrr').textContent = HC.fmt(F.sigma2, 2);
  setStatus('w02bvStatus', s.label + '：最佳 df = ' + F.dfs[s.argmin]
    + '，該點期望測試 MSE = ' + HC.fmt(s.total[s.argmin], 3)
    + '（偏差² ' + HC.fmt(s.bias2[s.argmin], 3) + ' ＋ 變異 '
    + HC.fmt(s['var'][s.argmin], 3) + ' ＋ Var(ε) ' + HC.fmt(F.sigma2, 2)
    + '）。df = 2 時是 ' + HC.fmt(s.total[0], 3) + '，df = 25 時是 '
    + HC.fmt(s.total[s.total.length - 1], 3) + '。');
}

/* ---------- P06 KNN 決策邊界 vs K（baked，ISLP 圖 2.15–2.16） ---------- */
let w02knnK = 10;
let w02knnSvc = null;
function w02knnSetup() {
  const F = FRAMES_w02knn;
  const H = 400, ih = H - 14 - 34;
  const iw = ih * (F.xd[1] - F.xd[0]) / (F.yd[1] - F.yd[0]);
  w02knnSvc = HC.svg('w02knnSvg', {
    xd: F.xd, yd: F.yd, h: H,
    pad: { l: 46, r: Math.max(20, 620 - 46 - iw), t: 14, b: 34 },
  });
}
function w02knnSet(k) { w02knnK = k; w02knnDraw(); }
function w02knnDraw() {
  const F = FRAMES_w02knn;
  const s = w02knnSvc;
  if (!s) return;
  s.grid(4, 4, { xtitle: 'X₁', ytitle: 'X₂', xdec: 1, ydec: 1 });
  const gr = s.clearLayer('region');
  const G = F.g;
  const reg = F.regions[String(w02knnK)];
  const hx = (F.xd[1] - F.xd[0]) / (2 * (G - 1));
  const hy = (F.yd[1] - F.yd[0]) / (2 * (G - 1));
  for (let r = 0; r < G; r++) {
    const cy = F.yd[0] + (F.yd[1] - F.yd[0]) * r / (G - 1);
    for (let cIdx = 0; cIdx < G; cIdx++) {
      const cx = F.xd[0] + (F.xd[1] - F.xd[0]) * cIdx / (G - 1);
      const one = reg.charAt(r * G + cIdx) === '1';
      s.box(Math.max(F.xd[0], cx - hx), Math.max(F.yd[0], cy - hy),
            Math.min(F.xd[1], cx + hx), Math.min(F.yd[1], cy + hy),
            { fill: one ? 'rgba(192,57,43,.17)' : 'rgba(44,62,122,.17)' }, gr);
    }
  }
  const gb = s.clearLayer('bayes');
  F.bayesSeg.forEach(sg => s.seg(sg[0], sg[1], sg[2], sg[3],
    { cls: 'aux', stroke: '#8e44ad', sw: 2, dash: '5 4' }, gb));
  const gp = s.clearLayer('pts');
  F.x1.forEach((x, i) => s.dot(x, F.x2[i], {
    r: 3.4, fill: F.y[i] === 1 ? HC.tok.b : HC.tok.a, stroke: '#fff', sw: 0.9,
  }, gp));
  const rx = 620 - s.pad.r + 8;
  s.txtPx(rx, 40, 'K = ' + w02knnK, { cls: 'axtitle' }, gp);
  s.txtPx(rx, 62, '● 類別 1（橘）', { cls: 'axlab' }, gp).style.fill = HC.tok.b;
  s.txtPx(rx, 80, '● 類別 0（藍）', { cls: 'axlab' }, gp).style.fill = HC.tok.a;
  s.txtPx(rx, 102, '底色＝KNN', { cls: 'axlab' }, gp);
  s.txtPx(rx, 118, '　決策區域', { cls: 'axlab' }, gp);
  s.txtPx(rx, 140, '紫虛線＝真實', { cls: 'axlab' }, gp).style.fill = '#8e44ad';
  s.txtPx(rx, 156, '　Bayes 邊界', { cls: 'axlab' }, gp).style.fill = '#8e44ad';
  const e = F.err[String(w02knnK)];
  $('w02knnK').textContent = String(w02knnK);
  $('w02knnInv').textContent = HC.fmt(1 / w02knnK, 3);
  $('w02knnTrain').textContent = HC.fmt(e.train, 4);
  $('w02knnTest').textContent = HC.fmt(e.test, 4);
  $('w02knnBayes').textContent = HC.fmt(F.bayesErr, 4);
  const tag = w02knnK === 1 ? '邊界破碎：每個訓練點附近都形成局部區域，抓到的是雜訊'
    : (w02knnK >= 100 ? '邊界過度平滑，快變成一條直線，明顯偏離紫色虛線'
      : '邊界跟紫色虛線很接近，本次測試錯誤率也最靠近母體下限');
  setStatus('w02knnStatus', 'K = ' + w02knnK + '（彈性度 1/K = ' + HC.fmt(1 / w02knnK, 3)
    + '）：訓練錯誤率 ' + HC.fmt(e.train, 4) + '、測試錯誤率 ' + HC.fmt(e.test, 4)
    + '，Bayes 母體風險 ' + HC.fmt(F.bayesErr, 4) + '；有限測試錯誤率可在其兩側波動。' + tag + '。');
}

/* ---------- P06 一維兩類密度與 Bayes 錯誤率（live） ---------- */
let w02bayesSvc = null;
function w02bayesSetup() {
  w02bayesSvc = HC.svg('w02bayesSvg', { xd: [-5, 5], yd: [0, 1.2], h: 300 });
}
function w02bayesDraw() {
  const s = w02bayesSvc;
  if (!s) return;
  const d = parseFloat($('w02bayesD').value);
  const sd = parseFloat($('w02bayesS').value);
  $('w02bayesDVal').textContent = HC.fmt(d, 1);
  $('w02bayesSVal').textContent = HC.fmt(sd, 2);
  const peak = HC.stat.dnorm(0, 0, sd);
  s.domain([-5, 5], [0, peak * 1.28]);
  s.grid(5, 4, { xtitle: 'x', ytitle: '密度', xdec: 0, ydec: 2 });
  const g = s.clearLayer('main');
  const xs = HC.stat.seq(-5, 5, 241);
  const f0 = xs.map(x => HC.stat.dnorm(x, -d / 2, sd));
  const f1 = xs.map(x => HC.stat.dnorm(x, d / 2, sd));
  const mn = xs.map((x, i) => Math.min(f0[i], f1[i]));
  const poly = xs.map((x, i) => s.X(x) + ',' + s.Y(mn[i]))
    .concat(xs.slice().reverse().map(x => s.X(x) + ',' + s.Y(0)));
  s.add('polygon', { points: poly.join(' '), fill: 'rgba(243,156,18,.42)' }, g);
  s.poly(xs.map((x, i) => [x, f0[i]]), { cls: 'aux', stroke: HC.tok.a, sw: 2.4 }, g);
  s.poly(xs.map((x, i) => [x, f1[i]]), { cls: 'aux', stroke: HC.tok.b, sw: 2.4 }, g);
  s.seg(0, 0, 0, s.yd[1], { cls: 'aux', stroke: '#8e44ad', sw: 1.8, dash: '5 4' }, g);
  const err = HC.stat.pnorm(-d / (2 * sd));
  s.txtPx(s.pad.l + 6, 22, '藍＝類別 0 · 橘＝類別 1 · 陰影＝重疊 · 紫虛線＝Bayes 決策邊界',
          { cls: 'axtitle' }, g);
  $('w02bayesGap').textContent = HC.fmt(d, 1);
  $('w02bayesSd').textContent = HC.fmt(sd, 2);
  $('w02bayesZ').textContent = HC.fmt(d / sd, 2);
  $('w02bayesErr').textContent = HC.fmt(err, 4);
  $('w02bayesAcc').textContent = HC.pct(1 - err, 2);
  setStatus('w02bayesStatus', 'Δμ = ' + HC.fmt(d, 1) + '、σ = ' + HC.fmt(sd, 2)
    + ' ⇒ 標準化距離 ' + HC.fmt(d / sd, 2) + '，Bayes 錯誤率 = Φ(−'
    + HC.fmt(d / (2 * sd), 2) + ') = ' + HC.fmt(err, 4)
    + '。這是母體期望錯誤率的下限；有限測試集的觀察值可以在其兩側波動。');
}

/* ---------- P02 鄰域平均：資料點不夠時的替代品（live，固定種子） ---------- */
const w02nbrN = 200;
const w02nbrSigma = 1.0;
const w02nbrX = [];
const w02nbrY = [];
(() => {
  const rand = HC.stat.lcg(20260910);
  for (let i = 0; i < w02nbrN; i++) {
    const x = 0.2 + 9.6 * rand();
    w02nbrX.push(x);
    w02nbrY.push(w02irrF(x) + w02nbrSigma * HC.stat.normal(rand));
  }
})();
let w02nbrSvc = null;
function w02nbrSetup() {
  w02nbrSvc = HC.svg('w02nbrSvg', { xd: [0, 10], yd: [-1.5, 13.5], h: 330 });
}
function w02nbrDraw() {
  const s = w02nbrSvc;
  if (!s) return;
  const h = parseFloat($('w02nbrH').value);
  const x0 = parseFloat($('w02nbrX0').value);
  $('w02nbrHVal').textContent = HC.fmt(h, 2);
  $('w02nbrX0Val').textContent = HC.fmt(x0, 1);
  $('w02nbrHVal2').textContent = HC.fmt(h, 2);
  s.grid(5, 4, { xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0 });
  const g = s.clearLayer('main');
  const lo = Math.max(0, x0 - h);
  const hi = Math.min(10, x0 + h);
  s.box(lo, s.yd[0], hi, s.yd[1],
        { fill: 'rgba(243,156,18,.16)', stroke: 'none' }, g);
  s.poly(HC.stat.seq(0, 10, 201).map(x => [x, w02irrF(x)]), { cls: 'truef' }, g);
  const inside = [];
  w02nbrX.forEach((x, i) => {
    const near = Math.abs(x - x0) <= h;
    if (near) inside.push(w02nbrY[i]);
    s.dot(x, w02nbrY[i], {
      r: near ? 4.2 : 2.6,
      fill: near ? HC.tok.train : HC.tok.muted,
      stroke: near ? '#fff' : null,
      sw: near ? 1 : null,
      opacity: near ? 1 : 0.4,
    }, g);
  });
  s.seg(x0, s.yd[0], x0, s.yd[1], { cls: 'aux', stroke: '#8e44ad', sw: 1.8, dash: '5 4' }, g);
  const truth = w02irrF(x0);
  const m = inside.length;
  const ave = m ? HC.stat.mean(inside) : null;
  if (m) s.poly([[lo, ave], [hi, ave]], { cls: 'fit', sw: 3.2 }, g);
  s.dot(x0, truth, { r: 5.2, fill: HC.tok.truef, stroke: '#fff', sw: 1.4 }, g);
  s.txtPx(s.pad.l + 6, 22,
          '綠虛線＝真實的 f · 黃帶＝鄰域 · 橘線＝鄰域平均 · 紫虛線＝目標位置 x₀',
          { cls: 'axtitle' }, g);
  const se = m ? w02nbrSigma / Math.sqrt(m) : null;
  $('w02nbrM').textContent = String(m);
  $('w02nbrAve').textContent = m ? HC.fmt(ave, 3) : '—';
  $('w02nbrTrue').textContent = HC.fmt(truth, 3);
  $('w02nbrErr').textContent = m ? HC.fmt(Math.abs(ave - truth), 3) : '—';
  $('w02nbrSe').textContent = m ? HC.fmt(se, 3) : '—';
  const tag = m === 0 ? '鄰域裡一個點都沒有，這個位置根本估不出來'
    : (m <= 6 ? '鄰域太窄：只有 ' + m + ' 個點，平均值會隨資料抖動（變異大）'
      : (h >= 2.2 ? '鄰域太寬：點雖然多，但裡面的 f 早就不是常數了（偏差大）'
        : '差不多剛好：點夠多、鄰域內的 f 又還算平坦'));
  setStatus('w02nbrStatus', 'h = ' + HC.fmt(h, 2) + '、x₀ = ' + HC.fmt(x0, 1)
    + ' ⇒ 鄰域內 ' + m + ' 個點，鄰域平均 '
    + (m ? HC.fmt(ave, 3) : '—') + '，真值 ' + HC.fmt(truth, 3)
    + '，差距 ' + (m ? HC.fmt(Math.abs(ave - truth), 3) : '—')
    + '（σ/√m ≈ ' + (m ? HC.fmt(se, 3) : '—') + '）。' + tag + '。');
}

/* ---------- P03 維度詛咒：球與超立方體（live，講義 p.15 閉式解） ---------- */
function w02lgamma(z) {
  /* Lanczos 近似（g = 7），本頁只用到 z ≥ 1，精度遠超過顯示需求 */
  const c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
             771.32342877765313, -176.61502916214059, 12.507343278686905,
             -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  const t = z - 1;
  let x = c[0];
  for (let i = 1; i < 9; i++) x += c[i] / (t + i);
  const w = t + 7.5;
  return 0.5 * Math.log(2 * Math.PI) + (t + 0.5) * Math.log(w) - w + Math.log(x);
}
/* 半徑 1 的內接球佔邊長 2 的超立方體的比例 */
function w02curRatioOf(p) {
  return Math.exp((p / 2) * Math.log(Math.PI) - p * Math.LN2 - w02lgamma(p / 2 + 1));
}
/* 要圈到比例 r 的體積，球的半徑要多大 */
function w02curRadiusOf(p, r) {
  return (2 / Math.sqrt(Math.PI)) * Math.exp((Math.log(r) + w02lgamma(p / 2 + 1)) / p);
}
function w02curPctText(v) {
  if (v >= 0.001) return HC.pct(v, 2);
  return (v * 100).toExponential(1).replace('e', ' × 10^') + '%';
}
let w02curSvc = null;
function w02curSetup() {
  w02curSvc = HC.svg('w02curSvg', { xd: [0, 1], yd: [0, 1], h: 360 });
}
function w02curDraw() {
  const s = w02curSvc;
  if (!s) return;
  const p = parseInt($('w02curP').value, 10);
  $('w02curPVal').textContent = String(p);
  $('w02curPVal2').textContent = String(p);
  const g = s.clearLayer('main');
  const U = 66, cx = 168, cy = 186;
  const r = w02curRatioOf(p);
  const R = w02curRadiusOf(p, 0.1);
  const edge = Math.pow(0.1, 1 / p);
  s.add('rect', { x: cx - U, y: cy - U, width: 2 * U, height: 2 * U, rx: 2,
                  fill: 'rgba(127,140,141,.10)', stroke: HC.tok.muted, 'stroke-width': 2 }, g);
  s.add('circle', { cx: cx, cy: cy, r: U, fill: 'rgba(26,107,74,.16)',
                    stroke: HC.tok.truef, 'stroke-width': 2 }, g);
  s.add('circle', { cx: cx, cy: cy, r: Math.min(U * R, 168), fill: 'none',
                    stroke: HC.tok.resid, 'stroke-width': 2.4, 'stroke-dasharray': '6 4' }, g);
  s.txtPx(cx, 30, '邊長 2 的超立方體剖面（灰）與內接球（綠，半徑 1）',
          { cls: 'axtitle', anchor: 'middle' }, g);
  s.txtPx(cx, cy + U + 30, '紅虛線＝要圈到 10% 體積所需半徑 R = ' + HC.fmt(R, 3),
          { cls: 'axlab', anchor: 'middle' }, g);
  s.txtPx(cx, cy + U + 50, R > 1 ? '已經戳出立方體的面：鄰域不再是局部'
                                 : '仍在立方體之內：鄰域還算局部',
          { cls: 'axlab', anchor: 'middle' }, g);
  const bx = 348, bw = 246, by = 132, bh = 28;
  s.txtPx(bx, 30, 'p = ' + p + ' 時，立方體的體積分給了誰', { cls: 'axtitle' }, g);
  s.add('rect', { x: bx, y: by, width: bw, height: bh, rx: 3,
                  fill: 'rgba(127,140,141,.20)', stroke: HC.tok.muted, 'stroke-width': 1 }, g);
  s.add('rect', { x: bx, y: by, width: Math.max(1.5, bw * r), height: bh, rx: 3,
                  fill: 'rgba(26,107,74,.55)', stroke: 'none' }, g);
  s.txtPx(bx, by - 10, '綠＝內接球 ' + w02curPctText(r)
          + ' · 灰＝角落 ' + w02curPctText(1 - r), { cls: 'axlab' }, g);
  s.txtPx(bx, by + bh + 26, '要裝下 10% 的資料，', { cls: 'axlab' }, g);
  s.txtPx(bx, by + bh + 46, '每個座標軸得覆蓋 ' + HC.pct(edge, 1) + ' 的範圍',
          { cls: 'axlab' }, g);
  s.txtPx(bx, by + bh + 76, p <= 4 ? '講義第 13 頁：p ≤ 4 時鄰域平均還好用'
                                   : '講義第 13 頁：p 大時最近鄰會很糟', { cls: 'axlab' }, g);
  $('w02curRatio').textContent = w02curPctText(r);
  $('w02curCorner').textContent = w02curPctText(1 - r);
  $('w02curR').textContent = HC.fmt(R, 3);
  $('w02curOut').textContent = R > 1 ? '已經超出（不再局部）' : '還沒超出';
  $('w02curEdge').textContent = HC.pct(edge, 1);
  setStatus('w02curStatus', 'p = ' + p + '：內接球只佔立方體的 ' + w02curPctText(r)
    + '，其餘 ' + w02curPctText(1 - r) + ' 的體積都在角落；要圈到 10% 的體積，'
    + '球的半徑要 ' + HC.fmt(R, 3) + '（內接球是 1），'
    + '而每個座標軸得覆蓋 ' + HC.pct(edge, 1) + ' 的範圍。');
}
function w02curChartDraw() {
  const ps = [];
  for (let i = 1; i <= 20; i++) ps.push(i);
  HC.line('w02curChart', {
    labels: ps,
    datasets: [
      { label: '內接球佔立方體的比例 r', data: ps.map(w02curRatioOf),
        borderColor: HC.tok.truef, backgroundColor: HC.tok.truef,
        borderWidth: 2.8, pointRadius: 2.8, fill: false },
      { label: '10% 鄰域每個軸要覆蓋的比例', data: ps.map(i => Math.pow(0.1, 1 / i)),
        borderColor: HC.tok.test, backgroundColor: HC.tok.test,
        borderWidth: 2.8, pointRadius: 2.8, fill: false },
    ],
  }, {
    scales: {
      x: { title: { display: true, text: '維度 p' } },
      y: { min: 0, max: 1, title: { display: true, text: '比例' } },
    },
  });
}

/* ---------- 啟動 ---------- */
w02irrSetup();
w02irrDraw();
w02nbrSetup();
w02nbrDraw();
w02curSetup();
w02curDraw();
w02flexSetup();
w02flexDraw();
w02knnSetup();
w02knnDraw();
w02bayesSetup();
w02bayesDraw();
HC.ready(() => {
  w02bvDraw();
  w02curChartDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


# Approved reading-flow organization; keep all source-backed detail content.
from reading_flow_ch1_6 import organize
BODIES, PAGEJS = organize(2, BODIES, PAGEJS)

if __name__ == "__main__":
    apply("statistical_learning", BODIES, PAGEJS, frames())
