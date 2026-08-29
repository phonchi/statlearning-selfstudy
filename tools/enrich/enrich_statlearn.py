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
  <p>第 1 章告訴你統計學習是幹什麼的。這一章要把它<strong>寫成一條式子</strong>，
  之後九章的所有方法都只是在這條式子的不同位置上動手腳。式子長這樣：</p>

  $$Y = f(X) + \\varepsilon$$

  <p>$Y$ 是你想預測的那個東西（銷售量、油耗、會不會違約），
  $X = (X_1, \\dots, X_p)$ 是你手上量得到的那些變數。
  $f$ 是「$X$ 對 $Y$ 提供的系統性資訊」——固定不變、真實存在，但<strong>你永遠看不到它</strong>。
  $\\varepsilon$ 是隨機誤差項，跟 $X$ 無關，平均值是 0。</p>

  <p>整章只做兩件事：<strong>（一）怎麼估 f</strong>、<strong>（二）怎麼判斷估得好不好</strong>。
  聽起來很抽象，但第二件事其實是整本書最實用的部分，因為「看起來配得很漂亮」
  跟「在新資料上真的準」是兩件常常相反的事。</p>

{info("為什麼一定要有 ε 這一項", '''把它拿掉，式子就變成 Y = f(X)，等於宣稱
  「只要知道 X 就能<strong>完全</strong>算出 Y」。這在真實世界幾乎不成立：<br>
  <strong>1. 沒量到的變數：</strong>病人對藥物的反應還跟基因、當天狀況有關，而你沒有那些欄位。<br>
  <strong>2. 無法量的變異：</strong>同一批藥的製造差異、同一個人不同天的身體狀況。<br>
  <strong>3. 量測誤差：</strong>儀器本身就有雜訊。<br>
  ε 就是這些東西的集合。它的變異數 Var(ε) 會變成你努力的天花板。這是下一節的主題。''')}

  <p>先把兩個常見的目的分清楚，因為它們會導向完全不同的方法選擇：</p>

{table(["", "預測（prediction）", "推論（inference）"],
       [["你要什麼", "Ŷ 愈接近 Y 愈好", "搞懂 X 怎麼影響 Y"],
        ["f̂ 可以是黑盒子嗎", "可以，沒人在意它長什麼樣", "不行，必須看得懂"],
        ["典型問題", "這封信是垃圾郵件嗎？這支股票明天多少？",
         "哪個媒體的廣告有效？漲價會少賣多少？"],
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
           "讀成字串（lab 儲存格 190、192 示範了那個災難）。"
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
       (False, "f 是我們配出來的模型，會隨著訓練資料改變",
        "不對，那是 <strong>f̂</strong>（f hat）。f 是真實世界的那個函數，換一份訓練資料它不會變；"
        "會變的是我們的估計 f̂——而「它變多少」正是後面「變異」的定義。"),
       (False, "f 包含了所有影響 Y 的因素，所以 ε 只是量測誤差",
        "不對。f 只用得到 <em>X 裡面有的</em>資訊。沒量到的變數影響再大，也只能被歸進 ε，"
        "所以 ε 遠不只是量測誤差。")])}
"""

# ── P01 irreducible ───────────────────────────────────────────────────
BODIES["irreducible"] = f"""
  <p>先問一個看似哲學、其實非常實用的問題：<strong>如果你猜對了 f，誤差會是 0 嗎？</strong>
  不會。假設 $\\hat f$ 與 $X$ 都固定，只有 $\\varepsilon$ 在變動，那麼</p>

  $$E\\left(Y - \\hat Y\\right)^2
    = \\underbrace{{\\left[f(X) - \\hat f(X)\\right]^2}}_{{\\text{{可縮減}}}}
    + \\underbrace{{\\mathrm{{Var}}(\\varepsilon)}}_{{\\text{{不可縮減}}}}$$

  <p>這是 ISLP 式 2.3。左邊是你會量到的平均平方誤差，右邊拆成兩塊：</p>

  <ul>
    <li><strong>可縮減誤差</strong>（reducible error）：$\\hat f$ 沒學對 $f$ 的部分。
    換更合適的方法、蒐集更多資料、把真正有用的變數加進來——都在打這一塊。</li>
    <li><strong>不可縮減誤差</strong>（irreducible error）：$\\mathrm{{Var}}(\\varepsilon)$。
    <strong>就算你神奇地得到 $\\hat f = f$，這一塊還在。</strong>
    因為 $Y$ 本來就有一部分變異跟 $X$ 沒關係。</li>
  </ul>

  <p>順帶把「最好的 f」講清楚。在平方誤差的意義下，最好的預測函數就是條件期望值，
  也就是<strong>迴歸函數</strong>（regression function）：</p>

  $$f(x) = E\\left[Y \\mid X = x\\right], \\qquad
    \\varepsilon = Y - f(x)$$

  <p>講義第 11 頁畫的就是這個：在 $x$ 這條垂直線上，$Y$ 有一整個分佈，
  $f(x)$ 是那個分佈的平均。剩下的上下散開就是 $\\varepsilon$，誰也拿不走。</p>

{viz(svg("w02irrSvg", 320),
     [info_card("怎麼玩這個元件",
                '真實的 f（綠色虛線）<strong>固定不動</strong>，只有雜訊的 σ 在變。'
                '綠色淡帶是 f ± σ 的範圍。拖滑桿把 σ 拉大，看點雲怎麼變胖——'
                '而 f 一動也沒動。', "ISLP 式 2.3"),
      rows_card("期望測試誤差的對帳",
                [("σ（雜訊的標準差）", "1.0", "w02irrSigma"),
                 ("Var(ε) = σ² ← 下限", "1.00", "w02irrVar"),
                 ("完美 f 的期望測試 MSE", "—", "w02irrPerfect"),
                 ("線性 f̂ 的期望測試 MSE", "—", "w02irrLin"),
                 ("獨立測試網格上的可縮減部分", "—", "w02irrGap")]),
      info_card("重點在哪一行",
                '這裡不再拿配適線性模型的同一批訓練點算 MSE。'
                '線性模型先在訓練樣本上配適，再到<strong>獨立而密集的 x 網格</strong>計算'
                '$E[(Y-\\hat f(X))^2]=\\sigma^2+E[(f(X)-\\hat f(X))^2]$。')],
     "w02irrStatus", "拖動 σ 滑桿，看不可縮減下限跟著抬高。",
     '<div class="slider-row" style="flex:1;min-width:190px;">'
     '<span class="slider-label">σ</span>'
     '<input type="range" id="w02irrSig" min="0.2" max="2" step="0.1" value="1" '
     'oninput="w02irrDraw()">'
     '<span class="slider-val" id="w02irrSigVal">1.0</span></div>'
     '<button class="btn btn-toggle" onclick="w02irrToggleLin()">切換線性 f̂</button>',
     provenance=("simulation", "固定訓練樣本；期望誤差在獨立 x 網格上計算"))}

  <p>講義第 12–15 頁接著問：那要怎麼估 $E[Y \\mid X = x]$？最直覺的辦法是
  <strong>最近鄰平均</strong>（nearest neighbor averaging）。把 $x$ 附近一小塊區域裡的
  $y$ 平均起來當作 $f(x)$。一維、二維時這招很好用，可是</p>

{info("維度詛咒：最近鄰平均在高維會壞掉", '''在 p 維空間裡，要圈到 10% 的資料，
  每個座標軸上平均得覆蓋 0.10<sup>1/p</sup> 的範圍：p = 1 要 10%，
  p = 10 要 <strong>80%</strong>，p = 20 要 <strong>89%</strong>。
  也就是說「最近的那幾個鄰居」其實離得非常遠，鄰域裡的 f 早就不是近似常數了，
  平均出來的東西沒有偏差保證。<br>
  這就是講義第 13–15 頁的維度詛咒（curse of dimensionality），
  也是高維問題偏好參數式模型（下一節）的根本理由。''', "warm")}

  <h3 id="dx-eps">講義完整實作：親手做出一個 Y = f(X) + ε</h3>

{card("講義 02 · 雜訊讓相關係數到不了 1", lab_code(CH, 76) + "\n" + lab_code(CH, 78),
      lab_output(CH, 78), src=src("74、76、78"),
      note="儲存格 74 先產生 50 個標準常態的 <code>x</code>。這裡的 "
           "<code>y = x + N(50, 1)</code> 意思是<strong>真實的 f(x) = x + 50，一點都沒錯</strong>，"
           "而 ε 是標準差 1 的常態。既然 f 完全正確，相關係數為什麼不是 1？"
           "因為 Var(x) = 1、Var(ε) = 1，理論相關是 1/√2 ≈ 0.707，"
           "實測 <strong>0.787</strong>（50 筆的抽樣波動）。"
           "<strong>那個缺口就是不可縮減誤差。</strong>")}

{card("講義 02 · 用樣本變異數估 Var(ε)", lab_code(CH, 84) + "\n" + lab_code(CH, 85),
      lab_output(CH, 85), src=src("84、85"),
      note="三個寫法給出同一個數字 <strong>2.7243406406465125</strong>，"
           "因為它們算的是同一件事：<code>np.mean((y - y.mean())**2)</code>。"
           "MSE 也是「平方的平均」，同一個動作。"
           "注意 <code>np.var()</code> 預設除以 n 而不是 n − 1（看 <code>ddof</code> 參數）——"
           "估 Var(ε) 時這個差別在小樣本上是會被抓出來的。")}

{qa("觀念釐清", [
    ("Q：「不可縮減誤差」到底不可縮減在哪？多蒐集資料有用嗎？多加變數呢？",
     "<p>先講結論：<strong>多蒐集資料沒用，多加變數有用，但加進來的那部分就不再算是 ε 了。</strong></p>"
     "<p>不可縮減誤差是 $\\mathrm{Var}(\\varepsilon)$，而 $\\varepsilon$ 的定義是 "
     "$Y - E[Y \\mid X]$，也就是「在給定這組 X 之後，Y 還剩下的變異」。"
     "資料量 n 變大只會讓你把 f 估得更準（打的是可縮減那一塊），"
     "$\\mathrm{Var}(\\varepsilon)$ 是母體的性質，跟你抽了幾筆完全無關。</p>"
     "<p>加變數就不一樣了。假設病人的反應其實還跟基因型有關，而你原本沒量。"
     "那部分變異現在被塞在 $\\varepsilon$ 裡。一旦把基因型加進 X，"
     "$E[Y \\mid X]$ 這個條件期望值本身就換了一個（更小的變異、更複雜的 f），"
     "$\\mathrm{Var}(\\varepsilon)$ 於是變小。所以嚴格說法是："
     "<strong>不可縮減誤差是「相對於你手上這組 X」的下限，不是宇宙常數。</strong></p>"
     "<p>實務上的意義：如果測試誤差已經逼近你估計的 $\\mathrm{Var}(\\varepsilon)$，"
     "再換模型、再調參數都是浪費時間，該去找新的變數了。"),
])}

{quiz("qIrr", "QUIZ · 兩種誤差",
      "你把模型從線性迴歸換成一個非常彈性的方法，測試 MSE 從 5.2 降到 2.4。"
      "已知 Var(ε) = 2.0。下列哪個判斷最合理？",
      [(True, "可縮減誤差從約 3.2 降到約 0.4，剩下的空間已經很小，該去找新變數而不是繼續換模型",
        "對。測試 MSE 減掉 Var(ε) 就是可縮減那一塊：5.2 − 2.0 = 3.2 → 2.4 − 2.0 = 0.4。"
        "已經吃掉 87%，繼續加彈性的邊際效益很低，而且風險是開始過度配適。"),
       (False, "還能再降到 0，因為彈性可以無限提高",
        "不對。三項拆解裡 Var(ε) = 2.0 是加在最後的常數，"
        "<strong>測試 MSE 不可能低於 2.0</strong>，不管方法多彈性。"
        "訓練 MSE 才有辦法被壓到接近 0，但那是另一回事。"),
       (False, "Var(ε) = 2.0 表示資料品質太差，應該重新蒐集同樣的資料",
        "方向錯了。重新蒐集<strong>同樣的變數</strong>不會改變 Var(ε)，它是母體的性質。"
        "要壓低它得<strong>多量一些變數</strong>，把原本躲在 ε 裡的系統性成分挖出來。")])}
"""

# ── P02 parametric ────────────────────────────────────────────────────
BODIES["parametric"] = f"""
  <p>知道要估 $f$ 了，接下來的分岔是：<strong>要不要先假設 f 的形狀？</strong>
  兩條路各有代價。</p>

  <p><strong>參數式方法</strong>（parametric method）分兩步。第一步假設形狀，
  最簡單的假設是線性：</p>

  $$f(X) = \\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\cdots + \\beta_p X_p$$

  <p>第二步用訓練資料估那 $p + 1$ 個係數（第 3 章的最小平方法）。
  這一招的威力在於：原本要估「一個任意的 $p$ 維函數」，現在只要估 $p+1$ 個數字。
  代價是——<strong>假設錯了就一路錯</strong>。ISLP 圖 2.4 的黃色平面明顯漏掉了
  真實 $f$ 的彎曲（圖 2.3 的藍色曲面）。</p>

  <p><strong>非參數式方法</strong>（non-parametric method）不預設形狀，
  只要求配出來的曲面「貼近資料又不要太粗糙」。ISLP 圖 2.5 用薄板樣條
  （thin-plate spline）配同一份 <code>Income</code> 資料，還原得非常漂亮。
  但天下沒有白吃的午餐：</p>

{info("非參數式的代價是資料量", '''因為沒把問題化簡成少數幾個參數，
  非參數式方法需要<strong>遠比參數式方法更多的觀測值</strong>才估得準。
  這跟上一節的維度詛咒是同一件事的兩種說法。<br>
  而且它還多出一個要你決定的東西：<strong>平滑程度</strong>。
  ISLP 圖 2.6 把平滑程度放鬆，配出來的曲面通過<strong>每一個</strong>訓練點、
  訓練誤差是 0——看起來完美，但它跟真實的 f（圖 2.3）差得很遠。
  這就是過度配適，也是下面兩節要量化的東西。''', "warm")}

{table(["", "參數式（parametric）", "非參數式（non-parametric）"],
       [["做法", "先假設 f 的形狀，再估參數", "不假設形狀，直接讓資料長出曲面"],
        ["要估什麼", "有限個參數（β₀…βₚ）", "整個函數，沒有固定的參數個數"],
        ["需要的資料量", "少", "多，而且隨 p 增加得非常快"],
        ["假設錯的後果", "系統性偏掉（高偏差）", "幾乎沒有這個風險"],
        ["額外要選的東西", "形狀（線性？加二次項？）", "平滑程度"],
        ["ISLP 例子", "圖 2.4 的線性平面", "圖 2.5／2.6 的薄板樣條"],
        ["本書章節", "第 3、4、6 章", "第 7（樣條、GAM）、8（樹）、9 章"]])}

  <h3 id="dx-cont">講義完整實作：先把「形狀」畫出來看看</h3>

{card("講義 02 · 用等高線圖看一個指定的 f(x, y)", lab_code(CH, 121), None,
      src=src("121"),
      note="這一格自己指定了 <code>f = cos(y) / (1 + x²)</code>，"
           "然後把它畫成等高線圖。<strong>這正是參數式的心態</strong>："
           "先寫下一個形狀，剩下的只是把數字填進去。"
           "非參數式反過來——沒有這一行 <code>f = ...</code>，形狀要從資料裡長出來。"
           "順帶記住 <code>np.multiply.outer</code> 與 <code>ax.contour</code>："
           "第 4、9 章畫決策邊界會一直用到。")}

{quiz("qPar", "QUIZ · 參數式與非參數式",
      "你有 n = 60 筆資料、p = 12 個預測變數，而且懷疑關係不是線性的。"
      "直接上一個很彈性的非參數式方法，主要的風險是什麼？",
      [(True, "p = 12 而 n = 60，非參數式方法在這種維度下沒有足夠的鄰居可以平均，"
              "會配出一個變異極大的 f̂",
        "對。非參數式方法的優點（不怕假設錯）是用<strong>資料量</strong>換來的。"
        "n = 60、p = 12 落在維度詛咒的火線上，這時反而該用有結構的參數式模型，"
        "例如線性模型加上幾個你有理由懷疑的非線性項。"),
       (False, "非參數式方法沒有參數，所以沒辦法做預測",
        "不對。「非參數」指的是<strong>不把 f 化簡成固定個數的參數</strong>，"
        "不是「沒有東西可以估」。它照樣預測，KNN 就是最簡單的例子。"),
       (False, "非參數式方法一定比參數式方法偏差大，所以在小樣本上更不準",
        "反了。非參數式方法的<strong>偏差通常更小</strong>（它不做錯誤的形狀假設）；"
        "它在小樣本上不準是因為<strong>變異大</strong>。這兩者的分工是 P05 的主題。")])}
"""

# ── P03 tradeoff ──────────────────────────────────────────────────────
BODIES["tradeoff"] = f"""
  <p>把上一節的分岔攤開，其實是一條連續的光譜。一端是<strong>彈性低但看得懂</strong>，
  另一端是<strong>彈性高但講不清楚</strong>。ISLP 圖 2.7 把本書的方法擺在這張圖上。</p>

  <p>你可能會問：既然只要預測準，為什麼不永遠選最彈性的那個？
  ISLP 的回答很直接——<strong>令人意外的是，用比較不彈性的方法常常反而預測更準。</strong>
  原因是過度配適，下一節就會用數字說清楚。</p>

{info("三個「選不彈性的」正當理由", '''<strong>1. 要做推論：</strong>
  線性模型能直接回答「TV 廣告每多花一千元，銷售大約多幾單位」。
  提升法給不出這種句子。<br>
  <strong>2. 樣本不夠：</strong>彈性高的方法要餵很多資料才穩，n 小的時候它的變異會吃掉一切。<br>
  <strong>3. 真實的 f 本來就簡單：</strong>如果 f 真的接近線性，線性迴歸的偏差幾乎是 0，
  彈性方法只是白白多付變異。這是 P05 情境 B 的畫面。''')}

  <h3 id="dx-desc">講義完整實作：決定要多彈性之前，先看資料</h3>

{card("講義 02 · 數值摘要", lab_code(CH, 271), lab_output(CH, 271), src=src("271"),
      note="<code>describe()</code> 一次給你 count／mean／std／五分位。"
           "<code>mpg</code> 的標準差 7.805 是「什麼都不做、直接猜平均」的誤差尺度——"
           "平方起來約 <strong>60.9</strong>。任何模型的測試 MSE 都要拿它當基準線比："
           "比不過它，那個模型就沒有存在的必要。")}

{card("講義 02 · 散佈圖矩陣：一眼看出線性夠不夠", lab_code(CH, 269), None,
      src=src("267、269"),
      note="<code>pd.plotting.scatter_matrix()</code> 把所有兩兩關係一次畫出來。"
           "<code>mpg</code> 對 <code>weight</code> 明顯是彎的。"
           "這就是「線性假設可能不夠」的第一手證據，也是決定要不要往彈性端走的依據。"
           "第 3 章會把這個觀察變成正式的殘差診斷。")}

{quiz("qFlex", "QUIZ · 彈性與可解釋性",
      "下列哪一組方法在 ISLP 圖 2.7 上「彈性最低、可解釋性最高」？",
      [(True, "子集選擇與 lasso",
        "對。兩者都基於線性模型，而且會把變數挑掉／把係數壓成 0，"
        "所以能生出的形狀比一般最小平方<strong>更少</strong>，最終模型也更好講。"),
       (False, "最小平方線性迴歸",
        "很接近，但不是最極端的那一端。最小平方會用上<strong>所有</strong>變數，"
        "而子集選擇與 lasso 會把一部分丟掉——形狀更受限、模型更精簡，所以在圖上更靠左上角。"),
       (False, "廣義加法模型（GAM）與決策樹",
        "不對，它們在圖的中段。GAM 允許每個變數各有一條曲線、樹允許切分區塊，"
        "都比線性模型彈性高，可解釋性也因此下降了一些。")])}
"""

# ── P04 mse ───────────────────────────────────────────────────────────
BODIES["mse"] = f"""
  <p>要比較方法，得先有量尺。迴歸問題最常用的是<strong>均方誤差</strong>（MSE）：</p>

  $$\\mathrm{{MSE}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}}
    \\left(y_i - \\hat f(x_i)\\right)^2$$

  <p>問題在於：<strong>這個平均是對哪一批資料算的？</strong>
  如果用的是配適時那批資料，它叫<strong>訓練 MSE</strong>；
  如果用的是模型完全沒見過的資料，它叫<strong>測試 MSE</strong>。
  兩者的行為完全不同，而我們真正在意的是後者。</p>

  <p>為什麼不能用訓練 MSE 當代理？因為大部分方法就是<strong>直接或間接在最小化它</strong>。
  你拿一個「已經被最佳化過的目標值」當成公正的評分，當然會太樂觀。
  極端一點：一條通過每一個訓練點的曲線，訓練 MSE 是 0，但它什麼都沒學到。</p>

{viz(svg("w02fitSvg", 300) + "\n" + svg("w02mseSvg", 250),
     [info_card("怎麼看這兩張圖",
                '<strong>上圖</strong>是同一組 50 個點（σ = 1）配上三種彈性的結果，'
                '綠色虛線是真實的 f。<strong>下圖</strong>是訓練 MSE（灰）與測試 MSE（紅）'
                '對彈性度的曲線，圓點標出上圖那三個選擇，紫色垂線是目前選的那一個。',
                "ISLP 圖 2.9"),
      rows_card("目前的選擇",
                [("樣條自由度 df", "6", "w02flexDfVal"),
                 ("訓練 MSE", "—", "w02flexTrain"),
                 ("測試 MSE", "—", "w02flexTest"),
                 ("Var(ε)（下限）", "1.00", "w02flexVar")]),
      info_card("彈性度是什麼",
                'df ＝ 配適時估的參數個數。<strong>df = 2 就是線性迴歸</strong>'
                '（截距加斜率），df ≥ 5 是三次迴歸樣條，節點依固定順序一個一個加進去，'
                '所以模型空間是巢狀的，訓練 MSE <strong>保證</strong>單調下降。')],
     "w02flexStatus", "按三個按鈕切換彈性，看訓練 MSE 與測試 MSE 各自往哪裡走。",
     '<button class="btn btn-toggle" onclick="w02flexSet(2)">線性（df 2）</button>'
     '<button class="btn btn-toggle" onclick="w02flexSet(6)">中等彈性（df 6）</button>'
     '<button class="btn btn-toggle" onclick="w02flexSet(25)">過度彈性（df 25）</button>',
     provenance=("simulation", "固定種子模擬；對照 ISLP 圖 2.9"))}

{info("這張圖的三個一定要看懂的地方", '''<strong>1. 訓練 MSE 從 3.43 一路掉到 0.48，</strong>
  單調下降，沒有轉折。它永遠獎勵更多彈性。<br>
  <strong>2. 測試 MSE 是 U 型：</strong>3.26 → 最低約 1.02（df = 7）→ 回升到 1.50。
  df = 25 的配適在訓練資料上是最好的，在新資料上卻比 df = 6 差了快 50%。<br>
  <strong>3. 那條水平虛線是 Var(ε) = 1.00。</strong>
  測試 MSE 貼近它，但永遠碰不到。這就是上一節的不可縮減誤差。''')}

  <p>ISLP 強調這個形狀是<strong>統計學習的基本性質</strong>：
  不管用什麼資料、什麼方法，訓練 MSE 會隨彈性下降，而測試 MSE 不一定。
  當訓練 MSE 很小、測試 MSE 卻很大，我們就說發生了<strong>過度配適</strong>（overfitting）。</p>

{info("過度配適的嚴格定義", '''不是「訓練 MSE 比測試 MSE 小」。
  那幾乎永遠成立，因為方法本來就在最小化訓練 MSE。<br>
  過度配適指的是：<strong>存在一個比較不彈性的模型，它的測試 MSE 反而更小。</strong>
  上圖裡 df = 25 是過度配適（df = 6 更好），而 df = 6 不是。''', "warm")}

  <h3 id="dx-mse">講義完整實作：期望值就是加權平均</h3>

{card("講義 02 · 用 zip 算加權和", lab_code(CH, 240), lab_output(CH, 240),
      src=src("240"),
      note="這一格算的是一個隨機變數的期望值：值 2、3、19，機率 0.2、0.3、0.5，"
           "E[X] = 2(0.2) + 3(0.3) + 19(0.5) = <strong>10.8</strong>。"
           "MSE 是「平方誤差的平均」、期望測試 MSE 是「對所有可能的訓練集與測試點取平均」——"
           "本章所有的 E[·] 拆到最底層都是這個加權和。"
           "<code>zip()</code> 之後會在每一次「對每筆資料算誤差再平均」時出現。")}

{qa("觀念釐清", [
    ("Q：為什麼測試 MSE 一定是 U 型？訓練 MSE 為什麼不是？",
     "<p>先講訓練 MSE。彈性愈高，模型能生出的函數集合<strong>愈大</strong>"
     "（本頁的樣條是巢狀的，df = 6 能配出的每一條曲線 df = 7 都能配出來）。"
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
      [(True, "選 B。我們要的是在新資料上的表現，A 的訓練與測試差距顯示它在配適雜訊",
        "對。A 的訓練 MSE 只有 B 的五分之一，但測試 MSE 幾乎是 B 的兩倍。"
        "這就是過度配適的典型指紋。決策一律看測試誤差。"),
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
    真實 $f$ 明顯非線性時，線性迴歸<strong>不管餵多少資料</strong>都會有高偏差。
    一般而言愈彈性 → 偏差愈低。</li>
    <li><strong>變異</strong>（variance）$= \\mathrm{{Var}}(\\hat f(x_0))$：
    換一組訓練資料重配一次，$\\hat f(x_0)$ 會抖動多少。
    彈性高的曲線緊貼著點跑，動一個點整條線就變樣。
    一般而言愈彈性 → 變異愈高。</li>
    <li><strong>$\\mathrm{{Var}}(\\varepsilon)$</strong>：跟方法無關的常數。</li>
  </ul>

{viz(chart("w02bvChart", "tall",
           "。此圖的重點：偏差² 隨彈性下降、變異隨彈性上升，兩者相加再加上 Var(ε) 就是 U 型的測試 MSE；"
           "最低點的位置隨真實 f 的形狀而變（情境 B 在 df = 2，情境 C 在 df = 18）。"),
     [info_card("這張圖怎麼算出來的",
                '固定真實的 f 與 σ = 1，<strong>重抽 M = 300 組訓練集</strong>'
                '（每組 n = 50，訓練點的 x 固定、只有 ε 重抽），對每個彈性度算出 300 條 f̂，'
                '再在 201 個測試點上算偏差²與變異並平均。三個情境共用同一組 ε。',
                "ISLP 圖 2.12"),
      rows_card("這個情境的最低點",
                [("情境", "中度非線性", "w02bvScen"),
                 ("最佳 df", "—", "w02bvBest"),
                 ("該點的總測試 MSE", "—", "w02bvTot"),
                 ("其中偏差²", "—", "w02bvBias"),
                 ("其中變異", "—", "w02bvVarv"),
                 ("Var(ε)", "1.00", "w02bvIrr")]),
      info_card("一個值得注意的巧合（其實不是巧合）",
                '三個情境的<strong>變異曲線完全相同</strong>。'
                '因為對線性平滑器來說 Var(f̂) 只跟設計矩陣與 σ² 有關，'
                '<strong>跟真實的 f 一點關係都沒有</strong>。'
                '三張圖的差別百分之百來自偏差²。')],
     "w02bvStatus", "切換三個情境：真實 f 的形狀怎麼改變最佳彈性度。",
     '<button class="btn btn-toggle" onclick="w02bvSet(\'A\')">中度非線性</button>'
     '<button class="btn btn-toggle" onclick="w02bvSet(\'B\')">接近線性</button>'
     '<button class="btn btn-toggle" onclick="w02bvSet(\'C\')">高度非線性</button>',
     provenance=("simulation", "固定種子蒙地卡羅 M=300；對照 ISLP 圖 2.12"))}

{info("三個情境的最佳 df 分別是 2、7、18", '''這就是 ISLP 圖 2.12 想講的唯一一件事：
  <strong>沒有一個放諸四海皆準的彈性度。</strong><br>
  <strong>情境 B（接近線性）：</strong>偏差²從一開始就幾乎是 0，加彈性只是白付變異，
  df = 2 最好。<br>
  <strong>情境 A（中度非線性）：</strong>偏差²一開始掉得快，總和先降後升，經典的 U。<br>
  <strong>情境 C（高度非線性）：</strong>df = 2 的偏差²高達 20.06，
  加彈性的報酬極大，要到 df = 18 才觸底。<br>
  真實的 f 你看不到，所以這個最佳點得靠<strong>第 5 章的交叉驗證</strong>去估。''')}

  <p>順帶一個 ESL §7.3 給的漂亮特例。對 KNN 迴歸，三項有封閉形式（ESL 式 7.10）：</p>

  $$\\mathrm{{Err}}(x_0) = \\sigma_\\varepsilon^2
    + \\left[f(x_0) - \\frac{{1}}{{k}} \\sum_{{\\ell=1}}^{{k}} f(x_{{(\\ell)}})\\right]^2
    + \\frac{{\\sigma_\\varepsilon^2}}{{k}}$$

  <p>看第三項：<strong>變異就是 $\\sigma_\\varepsilon^2 / k$</strong>，$k$ 愈大愈小。
  第二項是「$f(x_0)$ 與 $k$ 個鄰居上 $f$ 的平均」之差，$k$ 愈大鄰居愈遠、這個差愈大。
  一條式子把偏差–變異取捨寫得清清楚楚，也預告了本頁最後一節的 KNN。</p>

  <h3 id="dx-seed">講義完整實作：蒙地卡羅要能重現</h3>

{card("講義 02 · 沒固定種子 vs 固定種子",
      lab_code(CH, 80) + "\n\n" + lab_code(CH, 82), lab_output(CH, 82),
      src=src("80、82"),
      note="儲存格 80 連呼叫兩次 <code>np.random.normal()</code>，得到兩組不同的數字；"
           "儲存格 82 用 <code>np.random.default_rng(1303)</code> 各建一個產生器，"
           "兩次印出<strong>完全一樣</strong>的 <code>[4.09482632 -1.07485605]</code>。"
           "上面那張偏差–變異圖就是靠這件事才可信："
           "<code>default_rng(524)</code>、M = 300 組訓練集，"
           "任何人重跑 <code>tools/frames/gen_statlearn.py</code> 都會得到同樣的曲線。")}

  <div class="info-card" style="margin:1.2rem 0;">
    <div class="ic-title">蒙地卡羅拆解的虛擬碼 <span class="ic-badge">CODE</span></div>
    <div class="pseudo-code" style="font-size:.74rem;">
<span class="line"><span class="kw">for</span> d <span class="kw">in</span> 彈性度清單:</span>
<span class="line">    <span class="kw">for</span> m <span class="kw">in</span> <span class="kw">range</span>(M):            <span class="com"># M = 300 組訓練集</span></span>
<span class="line">        y = f(x_train) + rng.normal(<span class="num">0</span>, sigma)</span>
<span class="line">        fhat[m] = 用 d 配適(x_train, y).predict(x_test)</span>
<span class="line">    bias2 = mean((fhat.mean(axis=<span class="num">0</span>) - f(x_test))**<span class="num">2</span>)</span>
<span class="line">    var   = mean(fhat.var(axis=<span class="num">0</span>))</span>
<span class="line">    total = bias2 + var + sigma**<span class="num">2</span></span>
    </div>
    <p style="font-size:.82rem;margin:.6rem 0 0;color:var(--muted);">
    注意 <code>fhat.mean(axis=0)</code>：平均是<strong>跨 300 組訓練集</strong>取的，
    不是跨測試點。這正是下面 Q&amp;A 要釐清的地方。</p>
  </div>

{qa("觀念釐清", [
    ("Q：偏差–變異拆解是在對「什麼」取期望值？",
     "<p>對<strong>訓練集的重複抽樣</strong>取期望，不是對某一個已經配好的模型。"
     "這是整章最常被誤解的一句話。</p>"
     "<p>拆解式裡的 $\\hat f(x_0)$ 是一個<strong>隨機變數</strong>："
     "它的隨機性來自「你剛好抽到哪一組訓練資料」。"
     "$E[\\hat f(x_0)]$ 是「想像重複蒐集無數份訓練資料、每份都配一次模型、"
     "把這些 $\\hat f(x_0)$ 平均起來」。偏差是這個平均與真值 $f(x_0)$ 的差；"
     "變異是這些 $\\hat f(x_0)$ 自己的散開程度。</p>"
     "<p>所以下面兩句話是不同的意思，不要搞混：</p><ul>"
     "<li><strong>「這個模型的變異很大」</strong>："
     "換一份訓練資料，配出來的模型會很不一樣。這是拆解式講的變異。</li>"
     "<li><strong>「這個模型的預測值散得很開」</strong>："
     "在不同的 $x$ 上預測值差很多。這只是說 $\\hat f$ 這條曲線起伏大，"
     "跟拆解式的變異<strong>不是同一件事</strong>。</li></ul>"
     "<p>實務上的後果：你手上只有一份訓練資料，所以偏差與變異"
     "<strong>沒辦法分別算出來</strong>。上面那張圖能畫，是因為那是模擬，"
     "我們知道真實的 f，也能想抽幾組訓練集就抽幾組。真實資料上你只能估它們的"
     "<strong>總和</strong>（第 5 章的交叉驗證），然後靠這一節的直覺判斷該往哪邊調。</p>"),
])}

{quiz("qBV", "QUIZ · 偏差–變異拆解",
      "把訓練資料從 100 筆加到 10000 筆，其他都不變。對一個很彈性的方法，"
      "拆解式的三項會怎麼變？",
      [(True, "變異明顯下降，偏差幾乎不變，Var(ε) 完全不變",
        "對。資料變多讓 f̂ 對訓練集的抽樣不那麼敏感，所以<strong>變異</strong>下降；"
        "偏差是「這個模型類別能不能逼近 f」的性質，跟 n 無關；"
        "Var(ε) 是母體性質，更與 n 無關。"
        "這也解釋了為什麼<strong>資料多的時候彈性方法才划算</strong>。"),
       (False, "三項都下降，因為資料愈多估得愈準",
        "有一半對。變異確實下降，但<strong>偏差不會</strong>。"
        "ISLP 明確寫著：真實 f 明顯非線性時，線性迴歸「不管給多少訓練資料」"
        "都無法產生準確的估計。Var(ε) 更是完全不動。"),
       (False, "偏差下降、變異上升，因為模型可以配得更複雜",
        "不對。題目說「其他都不變」，也就是彈性度沒有改變，"
        "模型類別沒變 → 偏差不變。你可能想的是「資料變多之後我<em>可以</em>選更彈性的模型」。"
        "那是另一個決策，不是 n 變大的直接後果。")])}
"""

# ── P06 bayes ─────────────────────────────────────────────────────────
BODIES["bayes"] = f"""
  <p>前面全都在講迴歸。搬到分類問題，觀念一個都不用丟，只要換掉量尺：
  把 MSE 換成<strong>錯誤率</strong>（error rate）。</p>

  $$\\text{{訓練錯誤率}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} I(y_i \\neq \\hat y_i),
    \\qquad \\text{{測試錯誤率}} = \\mathrm{{Ave}}\\left(I(y_0 \\neq \\hat y_0)\\right)$$

  <p>$I(\\cdot)$ 是指示變數：分錯是 1、分對是 0，所以這個式子就是「分錯的比例」。
  跟迴歸一樣，我們在意的是測試錯誤率，而訓練錯誤率會系統性偏低。</p>

  <h3>Bayes 分類器：能做到多好的天花板</h3>

  <p>可以證明（證明超出 ISLP 範圍），測試錯誤率會被一個非常簡單的分類器最小化：
  <strong>把每一筆觀測指派給條件機率最大的那個類別</strong>。</p>

  $$\\text{{把 }} x_0 \\text{{ 指派給使 }} \\Pr(Y = j \\mid X = x_0) \\text{{ 最大的 }} j$$

  <p>這叫做 <strong>Bayes 分類器</strong>。兩類問題裡，它就是
  「$\\Pr(Y = 1 \\mid X = x_0) > 0.5$ 就猜 1，否則猜 2」。
  機率恰好等於 0.5 的那條線是 <strong>Bayes 決策邊界</strong>。
  它達到的錯誤率是<strong>所有分類器的下限</strong>：</p>

  $$\\text{{Bayes 錯誤率}} = 1 - E\\left[\\max_j \\Pr(Y = j \\mid X)\\right]$$

  <p>它大於 0，因為兩類在母體裡本來就重疊。
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
  <strong>K 最近鄰</strong>（K-nearest neighbors, KNN）用最土的辦法把它估出來：
  找出離 $x_0$ 最近的 $K$ 個訓練點（記作 $\\mathcal{{N}}_0$），數一數裡面各類佔幾成。</p>

  $$\\widehat{{\\Pr}}(Y = j \\mid X = x_0)
    = \\frac{{1}}{{K}} \\sum_{{i \\in \\mathcal{{N}}_0}} I(y_i = j)$$

  <p>然後指派給比例最高的那一類。就這樣，沒有參數、沒有假設。
  $K$ 是唯一的旋鈕，而它控制的正是彈性：<strong>$1/K$ 就是 KNN 的彈性度</strong>。</p>

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
                 ("Bayes 錯誤率（下限）", "0.1382", "w02knnBayes")]),
      info_card("三個 K 的故事",
                '<strong>K = 1：</strong>訓練錯誤率 0.000，測試 0.1964。'
                '邊界破碎，抓到的是雜訊——低偏差、極高變異。<br>'
                '<strong>K = 10：</strong>測試 0.1470，最接近 Bayes 下限 0.1382。<br>'
                '<strong>K = 100：</strong>測試 0.1758。邊界過度平滑、快變成直線——'
                '高偏差、低變異。')],
     "w02knnStatus", "切換 K，看決策區域與 Bayes 邊界（紫色虛線）差多少。",
     '<button class="btn btn-toggle" onclick="w02knnSet(1)">K = 1</button>'
     '<button class="btn btn-toggle" onclick="w02knnSet(10)">K = 10</button>'
     '<button class="btn btn-toggle" onclick="w02knnSet(100)">K = 100</button>',
     provenance=("simulation", "固定種子模擬；對照 ISLP 圖 2.15–2.16"))}

{info("Bayes 錯誤率算不出來，那講它有什麼用", '''<strong>1. 它定義了「盡力了」的意思。</strong>
  測試錯誤率已經逼近估計的 Bayes 錯誤率時，再換模型是浪費時間，該回頭找新變數——
  跟 P01 那個「測試 MSE 逼近 Var(ε)」的判斷完全平行。<br>
  <strong>2. 它是模擬研究的裁判。</strong>在已知真實分佈的模擬資料上它算得出來，
  這時「離下限多遠」比「錯誤率多少」有意義得多，上面那個元件就是這樣用的。<br>
  <strong>3. 它告訴你目標是估機率，不是估標籤。</strong>
  Bayes 分類器的形式是「比較條件機率的大小」，所以第 4 章的邏輯斯迴歸、LDA、Naive Bayes
  全都在做同一件事：各用不同的假設去估那個條件機率，再套上同一個「取最大」的規則。''')}

  <p>KNN 元件已經同時列出 K = 1、10、100 的訓練與獨立測試錯誤，足以看見
  「訓練誤差偏好高彈性、測試誤差不一定」的故事；不再重複放一張只把同一批數字連成線的圖。</p>

  <h3 id="dx-bool">講義完整實作：錯誤率其實就是布林陣列取平均</h3>

{card("講義 02 · 用布林陣列挑出「屬於這一類」的資料",
      lab_code(CH, 164) + "\n\n" + lab_code(CH, 171), lab_output(CH, 171),
      src=src("162、164、171"),
      note="<code>keep_rows</code> 是一個布林陣列，<code>A[keep_rows]</code> 只留下 "
           "<code>True</code> 的那幾列。KNN 在數「鄰居裡有幾個屬於類別 j」時做的就是這件事："
           "先算出一個布林陣列，再數它。"
           "注意 lab 儲存格 169 的對照：<code>np.array([0,1,0,1])</code> 雖然跟 "
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
    ("Q：KNN 的 K = 1 為什麼訓練錯誤率是 0，這代表它很好嗎？",
     "<p>K = 1 時，要預測訓練點 $x_i$ 的類別，KNN 會去找「離 $x_i$ 最近的 1 個訓練點」——"
     "而那個點<strong>就是 $x_i$ 自己</strong>，距離 0。於是它回報 $x_i$ 自己的標籤，"
     "百分之百正確。訓練錯誤率必定是 0，跟資料好壞完全無關。</p>"
     "<p>所以這個 0 沒有任何資訊。它是「用配適時那批資料評分」這個做法的極端失效案例，"
     "跟迴歸那邊「通過每一個點的曲線訓練 MSE = 0」是同一個病。"
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
       (False, "K = 1 的訓練錯誤率是 0，所以它一定過度配適；K 愈大一定愈好",
        "前半句對、後半句錯。K 一直加大會走到另一個極端："
        "本頁的模擬裡 K = 150 的測試錯誤率是 0.2270，比 K = 1 的 0.1964 還糟。"
        "測試錯誤率是<strong>U 型</strong>，兩端都不好。"),
       (False, "這表示資料的 Bayes 錯誤率很高，換任何 K 都沒有用",
        "不對。Bayes 錯誤率高會讓<strong>所有</strong> K 的錯誤率一起抬高，"
        "但不會造成 K = 1 與 K = 25 之間的差距。這個差距來自方法的偏差與變異，"
        "跟不可縮減的那一塊無關。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 2.4 第 1 題（b)(d)",
      "第 1 題問「彈性方法會比不彈性方法好還是差」。"
      "考慮 (b) p 極大而 n 很小，以及 (d) 誤差項的變異 σ² = Var(ε) 極大。這兩種情況呢？",
      [(True, "兩種情況都<strong>比較差</strong>：(b) 資料不夠支撐彈性方法，(d) 彈性方法會去配雜訊",
        "對。(b) n 小 p 大時，彈性方法的變異會爆掉，這是維度詛咒的直接後果。"
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
        "n 與 p 對了，但目的判斷錯。題目說的是「understanding which factors affect」——"
        "要的是看得懂的關係，不是準確的數字。這是推論。"
        "如果題目改成「猜這位新任 CEO 會拿多少」，那才是預測。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 2.4 第 3 題（a)(b)",
      "第 3 題要你在同一張圖上畫五條曲線（偏差²、變異、訓練誤差、測試誤差、Bayes／不可縮減誤差），"
      "橫軸是彈性。哪一組形狀是對的？",
      [(True, "偏差²單調下降、變異單調上升、訓練誤差單調下降、測試誤差 U 型、"
              "不可縮減誤差是一條水平線",
        "對，這就是本頁 P05 那張圖再加上訓練誤差。三個關鍵："
        "測試誤差 = 偏差² + 變異 + 不可縮減，所以它<strong>永遠在那條水平線之上</strong>；"
        "訓練誤差<strong>可以</strong>降到水平線之下（甚至到 0），因為它不誠實；"
        "測試誤差的最低點就在「偏差²下降速度 = 變異上升速度」的地方。"),
       (False, "偏差²與變異都單調下降，訓練誤差與測試誤差都是 U 型",
        "兩處錯。變異隨彈性<strong>上升</strong>（愈彈性的模型換一份資料就變一個樣）；"
        "訓練誤差<strong>單調下降</strong>不會回頭——模型空間變大，最小值只可能更小。"),
       (False, "訓練誤差與測試誤差最後會收斂到同一條線，因為彈性夠高就能學到真實的 f",
        "不對，兩者的差距<strong>隨彈性擴大</strong>。彈性極高時訓練誤差趨近 0，"
        "測試誤差卻因為變異暴增而上升。它們永遠不會會合。")])}

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
        "K = 1 錯了。最近的一筆不是第 2 筆（距離 2），而是第 5 筆 (−1,0,1)，"
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
        ["理論下限", "$\\mathrm{Var}(\\varepsilon)$（不可縮減誤差）", "Bayes 錯誤率"],
        ["訓練版的問題", "訓練 MSE 系統性偏低", "訓練錯誤率系統性偏低（K = 1 時是 0）"],
        ["彈性度的例子", "樣條自由度 df、多項式次數", "KNN 的 $1/K$"],
        ["本頁元件", "w02irr／w02flexfit／w02bv", "w02bayeserr／w02knn／w02knnerr"]])}

  <h3>參數式與非參數式</h3>
{table(["", "參數式", "非參數式"],
       [["先假設形狀嗎", "要", "不要"],
        ["要估的東西", "有限個參數", "整個函數"],
        ["主要風險", "形狀假設錯 → 高偏差", "資料不夠 → 高變異"],
        ["額外要選", "形狀", "平滑程度"],
        ["高維表現", "相對穩健", "受維度詛咒重創"],
        ["ISLP 例子", "圖 2.4 線性平面（第 3 章）", "圖 2.5／2.6 薄板樣條（第 7 章）"]])}

  <h3>本頁模擬跑出來的數字</h3>
{table(["樣條自由度 df", "2（線性）", "4", "6", "7", "12", "18", "25"],
       [["訓練 MSE（單一資料集）", "3.433", "1.125", "0.961", "0.955", "0.890", "0.788", "0.480"],
        ["測試 MSE（單一資料集）", "3.260", "1.180", "1.036", "<strong>1.021</strong>",
         "1.072", "1.170", "1.495"],
        ["情境 A 期望測試 MSE", "3.373", "1.249", "1.137", "<strong>1.136</strong>",
         "1.219", "1.332", "1.486"],
        ["情境 B（接近線性）", "<strong>1.046</strong>", "1.077", "1.116", "1.134",
         "1.219", "1.332", "1.486"],
        ["情境 C（高度非線性）", "21.099", "10.146", "4.702", "4.470", "2.432",
         "<strong>1.336</strong>", "1.486"]])}
  <p style="font-size:.82rem;color:var(--muted);">σ = 1，所以 Var(ε) = 1.00 是所有數字的下限。
  三個情境的最佳 df 分別是 2、7、18。這就是「沒有一個放諸四海皆準的彈性度」。
  數字由 <code>tools/frames/gen_statlearn.py</code> 在 <code>default_rng(524)</code>、
  M = 300 下產生。</p>

{table(["KNN（n = 200 訓練 / 5000 測試）", "K = 1", "K = 10", "K = 50", "K = 100", "K = 150"],
       [["彈性度 1/K", "1.000", "0.100", "0.020", "0.010", "0.0067"],
        ["訓練錯誤率", "<strong>0.000</strong>", "0.135", "0.125", "0.165", "0.240"],
        ["測試錯誤率", "0.1964", "0.1470", "<strong>0.1384</strong>", "0.1758", "0.2270"]])}
  <p style="font-size:.82rem;color:var(--muted);">Bayes 錯誤率 = 0.1382，是這一列的下限。
  K = 1 的訓練錯誤率必定是 0（最近的鄰居就是自己）。
  課本圖 2.15–2.17 用的是另一份模擬資料，報告 Bayes 0.1304、K = 10 為 0.1363、
  K = 1 為 0.1695、K = 100 為 0.1925——數字不同，形狀一致。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["基本框架", "$Y = f(X) + \\varepsilon$", "式 2.1，$E[\\varepsilon] = 0$ 且與 $X$ 無關"],
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
         "$\\frac1K\\sum_{i \\in \\mathcal{N}_0} I(y_i = j)$", "式 2.12，$1/K$ 是彈性度"]])}

{info("三個一定要記住的觀念", '''<strong>1. 測試 MSE 永遠不可能低於 Var(ε)。</strong>
  拆解式的三項都非負，Var(ε) 是加在最後的常數。分類版的說法是「錯誤率不可能低於 Bayes 錯誤率」。
  測試誤差逼近這條下限時，該去找新變數，不是繼續換模型。<br>
  <strong>2. 訓練誤差單調下降，測試誤差是 U 型。</strong>
  訓練誤差是被最小化過的目標值，它永遠獎勵更多彈性；只有測試誤差誠實。
  KNN 的 K = 1 訓練錯誤率必定是 0，這個 0 沒有任何資訊。<br>
  <strong>3. 偏差與變異的期望是對「重複抽訓練集」取的。</strong>
  變異是「換一份訓練資料，f̂ 會變多少」，不是「f̂ 這條曲線起伏多大」。
  真實資料上兩者無法分開估，只能估總和（第 5 章的交叉驗證）。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
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
  // 條件於目前這個已配適的 f-hat，期望測試 MSE = sigma^2 + approximation error。
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
  s.txtPx(s.pad.l + 6, 24, '綠虛線＝真實的 f · 紅線＝df = ' + w02flexDf + ' 的配適 · '
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
  m.txtPx(m.pad.l + 6, 22, '灰＝訓練 MSE（單調下降） · 紅＝測試 MSE（U 型） · 紫＝目前選的 df',
          { cls: 'axtitle' }, gm);

  $('w02flexDfVal').textContent = String(w02flexDf);
  $('w02flexTrain').textContent = idx >= 0 ? HC.fmt(F.trainMse[idx], 3) : '—';
  $('w02flexTest').textContent = idx >= 0 ? HC.fmt(F.testMse[idx], 3) : '—';
  $('w02flexVar').textContent = HC.fmt(F.sigma2, 2);
  const best = F.dfs[F.testMse.indexOf(Math.min(...F.testMse))];
  const tag = w02flexDf === 2 ? '太硬：直線配不出這個彎，偏差大'
    : (w02flexDf >= 25 ? '太軟：穿過雜訊，訓練 MSE 最小但測試 MSE 最大'
      : '差不多剛好：測試 MSE 接近最低點');
  setStatus('w02flexStatus', 'df = ' + w02flexDf + '：訓練 MSE '
    + HC.fmt(F.trainMse[idx], 3) + '、測試 MSE ' + HC.fmt(F.testMse[idx], 3)
    + '（下限 Var(ε) = ' + HC.fmt(F.sigma2, 2) + '，最佳 df = ' + best + '）。' + tag + '。');
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
      { label: '總測試 MSE', data: s.total, borderColor: HC.tok.test,
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
      y: { min: 0, suggestedMax: top, title: { display: true, text: '期望測試 MSE 的三塊' } },
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
    + '，該點總測試 MSE = ' + HC.fmt(s.total[s.argmin], 3)
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
  const tag = w02knnK === 1 ? '邊界破碎：每個訓練點都自成一個小島，抓到的是雜訊'
    : (w02knnK >= 100 ? '邊界過度平滑，快變成一條直線，明顯偏離紫色虛線'
      : '邊界跟紫色虛線很接近，測試錯誤率也最靠近下限');
  setStatus('w02knnStatus', 'K = ' + w02knnK + '（彈性度 1/K = ' + HC.fmt(1 / w02knnK, 3)
    + '）：訓練錯誤率 ' + HC.fmt(e.train, 4) + '、測試錯誤率 ' + HC.fmt(e.test, 4)
    + '，Bayes 下限 ' + HC.fmt(F.bayesErr, 4) + '。' + tag + '。');
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
    + '。這是分類問題的不可縮減誤差：任何分類器都贏不過它。');
}

/* ---------- 啟動 ---------- */
w02irrSetup();
w02irrDraw();
w02flexSetup();
w02flexDraw();
w02knnSetup();
w02knnDraw();
w02bayesSetup();
w02bayesDraw();
HC.ready(() => {
  w02bvDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("statistical_learning", BODIES, PAGEJS, frames())
