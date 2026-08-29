#!/usr/bin/env python3
"""beyond_linearity.html（ISLP 第 7 章）完整自學充實。冪等。

站內序號 08、ISLP 章號 7：id 與全域一律 w08 前綴，資料檔與 lab_output 用 ch7。

內容依據：講義 07_Moving_Beyond_Linearity.pdf（54 頁）、Ch07-nonlin-lab-zh.ipynb、
ISLP 第 7 章（書上 p.290–328）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_nonlin.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 7
LAB = "Ch07-nonlin-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def slider(sid, label, lo, hi, step, val, valtext, oninput, basis="240px"):
    """.controls-bar 裡的滑桿。用 .slider-row 當殼，才吃得到 base.css 的滑桿樣式。"""
    return (f'<span class="slider-row" style="margin-bottom:0;flex:1 1 {basis};min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" value="{val}" '
            f'oninput="{oninput}" aria-label="{label}">'
            f'<span class="slider-val" id="{sid}Val">{valtext}</span></span>')


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_nonlin.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_nonlin.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_nonlin.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>到目前為止的每一個模型都長成 $y = \\beta_0 + \\beta_1 x_1 + \\cdots + \\beta_p x_p$。
  它好用、好解讀、推論工具齊全，但它假設「x 每增加一單位，y 就固定增加 $\\beta$」。
  真實世界很少這麼客氣。<code>Wage</code> 資料裡薪水隨年齡先升後降，
  用一條直線去配，你會得到一個「年齡愈大薪水愈高」的結論，然後在 60 歲那群人身上錯得很難看。</p>

  <p>要放寬線性假設，最極端的做法是丟掉參數化模型（KNN、樹、核方法）。
  但那樣同時丟掉了「這個變數對 y 的影響長什麼樣」這種可以畫出來、可以講給人聽的東西。
  這一章走的是中間路線：<strong>把 x 換成一組事先選好的固定轉換</strong>
  $b_1(x), \\ldots, b_K(x)$，模型對係數還是線性的。所以第 3 章那一整套
  最小平方、標準誤、F 檢定，全部可以照用，只是預測變數換人了。</p>

{info("六條路線，一個框架", '''<strong>1. 多項式迴歸：</strong>加 x²、x³…，全域一條曲線。<br>
  <strong>2. 階梯函數：</strong>把 x 切段，每段一個常數。<br>
  <strong>3. 迴歸樣條：</strong>分段三次多項式，在節點上接得平滑。<br>
  <strong>4. 自然樣條：</strong>樣條再加兩端線性約束，邊界穩定得多。<br>
  <strong>5. 平滑樣條：</strong>不選節點，直接懲罰彎曲程度。<br>
  <strong>6. 局部迴歸：</strong>每個點只看鄰居，加權配一條線。<br>
  前四個是同一個<strong>基底函數</strong>框架的特例（§7.3），第 5、6 個是「損失＋懲罰」與
  「只看附近」兩種不同的想法。最後 §7.7 的 <strong>GAM</strong> 把它們推廣到多個變數。''')}

{table(["方法", "彈性怎麼來的", "由什麼控制", "邊界行為", "一句話"],
       [["多項式", "拉高次數 d", "d（整數）", "<span class='worst'>很糟</span>，會暴衝", "最省事，但 d &gt; 4 就別碰"],
        ["階梯函數", "多切幾段", "切點數 K", "還可以（常數）", "沒有自然切點就會漏掉趨勢"],
        ["立方樣條", "多加節點", "節點數 K（df = K+4）", "偏糟，信賴帶會爆開", "次數固定 3，靠節點取得彈性"],
        ["自然樣條", "多加節點", "節點數 K（df = K+2）", "<span class='best'>好</span>，兩端是直線", "同樣的彈性、更穩的兩端"],
        ["平滑樣條", "調 λ", "有效自由度 df<sub>λ</sub>（連續）", "好（兩端線性）", "不必選節點，只要選 λ"],
        ["局部迴歸", "調鄰域大小", "跨距 s", "偏糟（單邊資料）", "每次預測都要用到全部資料"]])}

  <p>這一章的講義有 54 頁，順序就是上面這張表。往下每一節都有一個可以拖、可以推的元件。
  <strong>先猜結果再按按鈕</strong>，猜錯的地方才是你真正學到東西的地方。</p>

{quiz("qNon", "QUIZ · 為什麼它還算線性模型",
      "把 <code>age</code>、<code>age²</code>、<code>age³</code>、<code>age⁴</code> 一起丟進迴歸，"
      "為什麼書上還說這是「一般的線性迴歸模型」？",
      [(True, "因為模型對<strong>係數</strong>是線性的；x 的轉換是事先固定、已知的，只是換了預測變數",
        "對。「線性」講的是「對參數線性」。第 3 章的最小平方、標準誤、F 檢定因此全部照用。這正是基底函數框架最值錢的地方。"),
       (False, "因為配出來的曲線在資料範圍內仍然近似一條直線",
        "不對。四次多項式配出來明顯是彎的（ISLP 圖 7.1 左），一點都不像直線。「線性模型」跟「配出來的圖形是直線」是兩件不同的事。"),
       (False, "因為 age² 與 age³ 跟 age 高度相關，實際上只有一個自由的預測變數",
        "不對。它們確實高度相關（所以實作上要用正交多項式或把 x 標準化），但那是<strong>數值穩定性</strong>的問題；模型仍然有 4 個獨立的參數。")])}
"""

# ── P01 poly ──────────────────────────────────────────────────────────
BODIES["poly"] = f"""
  <p>最直接的放寬：把直線換成 d 次多項式。</p>

  $$y_i = \\beta_0 + \\beta_1 x_i + \\beta_2 x_i^2 + \\beta_3 x_i^3 + \\cdots
    + \\beta_d x_i^d + \\varepsilon_i \\tag{{7.1}}$$

  <p>係數照樣用最小平方估。但注意：<strong>個別的 $\\hat\\beta_j$ 沒有解讀價值</strong>。
  lab 儲存格 14 配出來的 <code>447.07, −478.32, 125.52, −77.91</code>，
  你沒辦法說「age 的二次項效果是 125.52」。這些數字還取決於用哪一組基底
  （正交多項式 vs 原始冪次，係數完全不同，配出來的曲線一模一樣）。
  要看的是<strong>整條配適曲線</strong>，以及它的信賴帶。</p>

  <p>信賴帶怎麼來的？在某個 $x_0$ 上，配適值是
  $\\hat f(x_0) = \\hat\\beta_0 + \\hat\\beta_1 x_0 + \\cdots + \\hat\\beta_d x_0^d$。
  令 $\\ell_0 = (1, x_0, x_0^2, \\ldots, x_0^d)^{{\\mathsf T}}$、$\\hat C$ 是 $\\hat\\beta$ 的
  共變異數矩陣，那麼</p>

  $$\\widehat{{\\operatorname{{Var}}}}\\left[\\hat f(x_0)\\right]
    = \\ell_0^{{\\mathsf T}} \\hat C \\, \\ell_0 \\tag{{7.2}}$$

  <p>把每個 $x_0$ 的 $\\hat f(x_0) \\pm 2\\,\\mathrm{{SE}}$ 連起來，就是圖 7.1 那兩條虛線。
  <strong>這個公式是整節的關鍵</strong>：$x_0$ 跑到資料邊界時 $x_0^{{15}}$ 大得離譜，
  乘上共變異數矩陣以後變異就炸開了。下面把滑桿推到 15 就看得到。</p>

{viz(svg("w08polySvg", 300) + "\n" + svg("w08polyMse", 170),
     [info_card("怎麼看這張圖",
                '上圖：灰點是 <code>Wage</code> 的 90 筆子樣本（只是背景），'
                '紅線與淡藍帶是用<strong>全部 3000 筆</strong>配出來的 d 次多項式與 95% 信賴帶。'
                '下圖：訓練 MSE（藍）一路往下，10-fold CV MSE（紅）在 d = 4 觸底之後回頭往上。',
                "圖 7.1"),
      rows_card("這個次數的成績",
                [("次數 d", "4", "w08polyDeg2"),
                 ("訓練 MSE", "—", "w08polyTrain"),
                 ("10-fold CV MSE", "—", "w08polyCv"),
                 ("18 歲那端的帶寬", "—", "w08polyWl"),
                 ("80 歲那端的帶寬", "—", "w08polyWr"),
                 ("中央（約 49 歲）帶寬", "—", "w08polyWm")]),
      info_card("重點在兩端的帶寬",
                'd 從 1 推到 15，中央的帶寬只從 3.5 長到 7.3，'
                '但 80 歲那端從 10.0 長到 <strong>78.3</strong>——'
                '<strong>邊界是多項式付出代價的地方</strong>。ISLP 圖 7.7 用 degree 15 '
                '對照 15 個自由度的自然樣條，講的就是這件事。')],
     "w08polyStatus", "把滑桿從 1 推到 15，盯著兩端的信賴帶（淡藍）而不是中間的曲線。",
     slider("w08polySl", "次數 d", 1, 15, 1, 4, "4", "w08polySetDeg()")
     + '<button class="btn btn-toggle" id="w08polyBandBtn" onclick="w08polyToggleBand()">信賴帶：開</button>'
     + '<button class="btn btn-reset" onclick="w08polyReset()">回到 d = 4</button>',
     provenance=("course-data", "Wage 全體資料配適與固定 90 筆背景子樣本；曲線、CV MSE 與信賴帶由 generator 計算。"))}

  <h3 id="dx-poly">講義完整實作：四次多項式與它的 t 檢定</h3>
{card("lab 07 · degree 4 多項式（Wage：age → wage）",
      lab_code(CH, 14), lab_output(CH, 14), src="14"[:0] + src(14),
      note="<code>poly('age', degree=4)</code> 產生的是<strong>正交</strong>多項式基底，"
           "所以四個係數彼此不相關，t 檢定可以一個一個讀。"
           "最後一項的 p 值 0.051 剛好在邊界上。這就是「三次或四次都合理」的來源。")}

{card("lab 07 · 用 ANOVA 逐步比較 degree 1 到 5", lab_code(CH, 26), lab_output(CH, 26),
      src=src(26),
      note="第 1 列（線性 vs 二次）p 值 2.4e−32，第 2 列（二次 vs 三次）0.0017，"
           "第 3 列（三次 vs 四次）0.051，第 4 列（四次 vs 五次）0.37。"
           "<strong>結論：三次或四次夠了，五次沒有必要。</strong>"
           "順帶對一下上面那張卡：$(-11.983)^2 = 143.59$ 正好是這裡的 F 統計量"
           "（lab 儲存格 29 就在算這個）。")}

{card("lab 07 · 多項式邏輯斯迴歸：Pr(wage &gt; 250)", lab_code(CH, 33), lab_output(CH, 33),
      src=src(33),
      note="同一套基底換到 GLM 上就得到 ISLP 圖 7.1 右。注意 n = 3000 但高收入者只有 79 人，"
           "所以係數的標準誤很大、信賴帶很寬，尤其在 age 大的那一端。"
           "<strong>「樣本數夠大」要看的是關鍵事件的數量，不是總筆數。</strong>")}

{quiz("qDeg", "QUIZ · 多項式的次數",
      "同一份 <code>Wage</code> 資料上，d 從 1 加到 15，訓練 MSE 一路從 1674 掉到 1585，"
      "但 10-fold CV MSE 在 d = 4 觸底（1596）之後回頭升到 1603。這說明什麼？",
      [(True, "d 超過 4 之後多出來的彈性只是在配雜訊，所以測試誤差反而變差",
        "對。訓練 MSE 必然單調下降（參數只增不減），CV MSE 才是測試誤差的估計。兩條線分岔的地方就是過度配適開始的地方。"),
       (False, "CV MSE 的估計本身有偏誤，所以它上升只是雜訊，該相信訓練 MSE",
        "不對，方向剛好反了。訓練 MSE 是<strong>系統性偏低</strong>的（第 5 章講過）；CV MSE 才是誠實的估計。而且 1596 → 1603 的上升是單調的，不像雜訊。"),
       (False, "說明 <code>Wage</code> 資料裡 age 與 wage 的真實關係是四次多項式",
        "太強了。CV 只告訴你「在多項式這個模型族裡，d = 4 附近的複雜度最合適」。真實關係很可能根本不是多項式。後面的樣條與平滑樣條會用完全不同的基底配出差不多好的結果。")])}
"""

# ── P02 step ──────────────────────────────────────────────────────────
BODIES["step"] = f"""
  <p>多項式有個結構上的毛病：它是<strong>全域</strong>的。60 歲那群人的資料會透過 $\\hat\\beta_3$
  影響 20 歲那一段的曲線形狀。階梯函數（step function）換一個想法：
  把 x 的範圍切成幾段，每段各配一個常數，段與段之間互不干涉。</p>

  <p>做法是選切點 $c_1, \\ldots, c_K$，造出 K+1 個指示變數：</p>

  $$C_0(X) = I(X < c_1),\\quad C_k(X) = I(c_k \\le X < c_{{k+1}}),\\quad
    C_K(X) = I(c_K \\le X) \\tag{{7.4}}$$

  <p>然後把 $C_1, \\ldots, C_K$ 丟進迴歸（$C_0$ 跟截距重複，要丟掉一個）：</p>

  $$y_i = \\beta_0 + \\beta_1 C_1(x_i) + \\cdots + \\beta_K C_K(x_i) + \\varepsilon_i \\tag{{7.5}}$$

{info("係數怎麼讀", '''因為每個 x 只落在一段裡，$\\beta_0$ 就是<strong>第一段的平均 y</strong>，
  $\\beta_j$ 是<strong>第 j+1 段相對於第一段的增量</strong>。
  這也意味著：只有 x 一個變數時，<strong>每一段的配適值就是那一段的樣本平均</strong>。
  下面的元件顯示的就是這個。<br>
  如果改成「保留全部 K+1 個指示變數、去掉截距」（lab 儲存格 39 的
  <code>pd.get_dummies()</code> 就是這樣），係數會直接變成各段的平均值。
  兩種編碼配出來的曲線完全一樣。''')}

{viz(svg("w08stepSvg", 330),
     [info_card("怎麼玩",
                '拖動<span style="color:var(--pt-held);font-weight:700;">橘色</span>的切點。'
                '每一段的水平紅線就是該段的樣本平均，也就是階梯函數的配適值。'
                '切點會被夾在鄰居之間（至少差 2 歲），拖不過去是刻意的。', "LIVE"),
      info_card("每一段", '<div id="w08stepRows" style="font-family:\'JetBrains Mono\',monospace;'
                'font-size:.78rem;line-height:1.75;"></div>'),
      rows_card("整體",
                [("段數", "4", "w08stepSeg"), ("切點", "—", "w08stepCutTxt"),
                 ("RSS", "—", "w08stepRss"), ("R²", "—", "w08stepR2")]),
      info_card("為什麼第一段常常很難看",
                'ISLP 圖 7.2 左的第一段完全錯過了「薪水隨年齡上升」的趨勢——'
                '一個常數沒辦法表達段內的斜率。<strong>沒有自然切點的時候，'
                '階梯函數會漏掉 action。</strong>不過流病學與生物統計很愛用它'
                '（例如固定的 5 歲一組），因為切點本身有現實意義。')],
     "w08stepStatus", "拖橘色的切點看每一段的平均怎麼變。用上面的選單改段數。",
     '<span class="slider-label" style="margin-right:.2rem;">段數</span>'
     '<select id="w08stepSel" class="mono" onchange="w08stepSetK()">'
     '<option value="2">2</option><option value="3">3</option>'
     '<option value="4" selected>4</option><option value="5">5</option>'
     '<option value="6">6</option></select>'
     '<button class="btn btn-reset" onclick="w08stepReset()">回到分位數切點</button>',
     provenance=("course-data", "Wage 資料；初始分位數切點對照 Ch07 lab 儲存格 39，拖動後由同一資料重算。"))}

  <h3 id="dx-step">講義完整實作：<code>pd.qcut</code> 切四段</h3>
{card("lab 07 · 用分位數切點配階梯函數", lab_code(CH, 39), lab_output(CH, 39), src=src(39),
      note="<code>pd.qcut(age, 4)</code> 自動用 25%／50%／75% 分位數當切點，"
           "切出 <code>(17.999, 33.75]</code>、<code>(33.75, 42.0]</code>、"
           "<code>(42.0, 51.0]</code>、<code>(51.0, 80.0]</code> 四段。"
           "因為 <code>get_dummies()</code> 保留了全部四欄（沒有丟基準組），"
           "<strong>四個係數就直接是四段的平均薪水</strong>：94.16、116.66、119.19、116.57。"
           "把它們跟上面元件裡的紅線對一下——同一件事。<br>"
           "不用分位數就改 <code>pd.cut()</code>（等寬切），lab 儲存格 41 有。")}

{quiz("qStep", "QUIZ · 階梯函數",
      "只有 <code>age</code> 一個預測變數時，階梯函數在每一段的配適值是什麼？",
      [(True, "那一段內所有觀測值的 y 平均",
        "對。段內的設計矩陣只有一個常數欄，最小平方對常數的解就是平均。所以 lab 儲存格 39 的四個係數 94.16／116.66／119.19／116.57 就是四段的平均薪水。"),
       (False, "那一段兩個端點上迴歸直線的中點",
        "不對。階梯函數段內<strong>沒有斜率</strong>，根本沒有直線可言。你想的是「分段線性」（linear spline），那是後面的事。"),
       (False, "全體樣本平均，加上該段切點對應的偏移量",
        "接近但不對。截距是<strong>第一段</strong>的平均，不是全體平均；各段係數是相對第一段的增量。全體平均只有在各段樣本數相同時才剛好等於各段平均的平均。")])}
"""

# ── P03 basis ─────────────────────────────────────────────────────────
BODIES["basis"] = f"""
  <p>停下來看一下前兩節做了什麼。多項式迴歸用的預測變數是 $x, x^2, x^3, \\ldots$；
  階梯函數用的是 $I(c_1 \\le x < c_2), I(c_2 \\le x < c_3), \\ldots$。
  形式不同，但<strong>結構完全一樣</strong>：都是「先把 x 過一組固定函數，再做線性迴歸」。
  ISLP §7.3 把這個結構抽出來叫做<strong>基底函數</strong>（basis function）：</p>

  $$y_i = \\beta_0 + \\beta_1 b_1(x_i) + \\beta_2 b_2(x_i) + \\cdots
    + \\beta_K b_K(x_i) + \\varepsilon_i \\tag{{7.7}}$$

  <p>關鍵是 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ <strong>事先選定、固定、已知</strong>。
  它們不含要估的參數。於是 (7.7) 就是一個以 $b_1(x_i), \\ldots, b_K(x_i)$ 為預測變數的
  標準線性模型，最小平方、標準誤、F 檢定原封不動搬過來。</p>

{info("這一節是整章的骨架", '''<strong>多項式：</strong>$b_j(x) = x^j$<br>
  <strong>階梯函數：</strong>$b_j(x) = I(c_j \\le x < c_{j+1})$<br>
  <strong>立方樣條：</strong>$x, x^2, x^3$ 再加每個節點一個 $(x - \\xi_k)^3_+$<br>
  <strong>自然樣條、B-樣條：</strong>同一個函數空間的另外幾組基底<br>
  換基底就換方法，但配適的機器（最小平方）從頭到尾沒換過。
  小波（wavelet）與傅立葉級數也是合法的選擇，只是這一章不講。''')}

  <p>下面這個元件是本頁最重要的一個。左邊每一個核取鈕都是一個基底函數；
  你選哪幾個，下面就用<strong>那幾個</strong>去配。三個預設按鈕分別把選擇切成
  「三次多項式」、「立方樣條」、「階梯函數」。<strong>你會看到它們只是勾選項不同而已</strong>。</p>

{viz(svg("w08basisFn", 200) + "\n" + svg("w08basisFit", 280),
     [info_card("怎麼玩",
                '上圖是被選中的每一個基底函數的<strong>形狀</strong>（各自正規化到同高，'
                '否則 x³ 會把別人壓扁）。下圖是資料與它們線性組合出來的曲線 '
                '$\\hat f(x) = \\sum_k \\hat\\beta_k b_k(x)$。'
                '節點固定在 33.75 與 51（<code>Wage</code> 的 25% 與 75% 分位數）。', "LIVE"),
      rows_card("目前的模型",
                [("選了幾個基底", "4", "w08basisK"), ("參數個數", "4", "w08basisP"),
                 ("RSS", "—", "w08basisRss"), ("R²", "—", "w08basisR2")]),
      info_card("三個預設分別是什麼",
                '<strong>三次多項式</strong>＝1, x, x², x³（4 個參數）<br>'
                '<strong>立方樣條</strong>＝上面再加 (x−33.75)³₊、(x−51)³₊（6 個參數＝K+4）<br>'
                '<strong>階梯函數</strong>＝1, I(x≥33.75), I(x≥51)（3 段，3 個參數）<br>'
                '按下去看曲線怎麼變。三種「不同的方法」在程式裡只差幾個勾。')],
     "w08basisStatus", "勾選基底函數，看它們怎麼組合成一條曲線。三個預設按鈕在最右邊。",
     '<button class="btn btn-toggle" id="w08basisB0" onclick="w08basisToggle(0)">1</button>'
     '<button class="btn btn-toggle" id="w08basisB1" onclick="w08basisToggle(1)">x</button>'
     '<button class="btn btn-toggle" id="w08basisB2" onclick="w08basisToggle(2)">x²</button>'
     '<button class="btn btn-toggle" id="w08basisB3" onclick="w08basisToggle(3)">x³</button>'
     '<button class="btn btn-toggle" id="w08basisB4" onclick="w08basisToggle(4)">(x−ξ₁)³₊</button>'
     '<button class="btn btn-toggle" id="w08basisB5" onclick="w08basisToggle(5)">(x−ξ₂)³₊</button>'
     '<button class="btn btn-toggle" id="w08basisB6" onclick="w08basisToggle(6)">I(x≥ξ₁)</button>'
     '<button class="btn btn-toggle" id="w08basisB7" onclick="w08basisToggle(7)">I(x≥ξ₂)</button>'
     '<button class="btn btn-step" onclick="w08basisPreset(\'poly\')">預設：三次多項式</button>'
     '<button class="btn btn-step" onclick="w08basisPreset(\'spline\')">預設：立方樣條</button>'
     '<button class="btn btn-step" onclick="w08basisPreset(\'step\')">預設：階梯函數</button>',
     provenance=("course-data", "Wage 固定子樣本；基底與最小平方配適依 Ch07 lab 的 polynomial／spline／step 表示。"))}

  <h3 id="dx-bs0">講義完整實作：把樣條的次數調成 0，就是階梯函數</h3>
{card("lab 07 · degree=0 的 B-樣條 ≡ 分段常數", lab_code(CH, 53), lab_output(CH, 53),
      src=src(53),
      note="這張卡是上面那個元件的程式版證據。<code>bs('age', df=3, degree=0)</code> "
           "指定 3 個自由度、次數 0，節點就落在同樣的三個分位數上，配出來的是<strong>分段常數</strong>。"
           "截距 94.158 跟 <code>qcut</code> 版一模一樣（第一段的平均），"
           "而 94.158 + 22.349 = 116.507 ≈ 116.611（第二段的平均）——"
           "差一點是因為 <code>qcut()</code> 用 ≤ 判斷區間、<code>bs()</code> 用 &lt;，"
           "邊界上那幾筆歸屬不同。<strong>同一個模型，不同編碼。</strong>")}

{quiz("qBasis", "QUIZ · 基底函數框架",
      "基底函數框架要求 $b_1(\\cdot), \\ldots, b_K(\\cdot)$ 必須「事先選定、固定且已知」。"
      "這個要求為什麼這麼重要？",
      [(True, "因為這樣模型才對參數線性，第 3 章的最小平方與推論工具（標準誤、F 檢定）才能原封不動使用",
        "對。一旦基底函數自己含有要估的參數（例如節點位置也要估），模型就變成非線性最小平方，標準誤與檢定都要重推。這就是為什麼實務上節點放在固定分位數，而不是「估」出來。"),
       (False, "因為固定的基底函數保證配出來的曲線一定平滑",
        "不對。階梯函數的基底也是固定的，配出來卻是不連續的階梯。平滑不平滑取決於<strong>選哪組基底</strong>，跟「固定」無關。"),
       (False, "因為只有固定的基底函數才能讓設計矩陣可逆",
        "不對。可逆性取決於基底函數在資料上是否線性獨立，跟固定與否是兩件事——事實上高次多項式的設計矩陣就常常接近奇異（Vandermonde 矩陣條件數很差）。")])}
"""

# ── P04 splines ───────────────────────────────────────────────────────
BODIES["splines"] = f"""
  <p>多項式的毛病是全域、次數一高就在邊界暴衝。階梯函數的毛病是段內沒有斜率。
  把兩個想法縫起來：<strong>分段配低次多項式</strong>。節點（knot）就是換係數的地方。
  一個節點在 c 的分段三次多項式長這樣：</p>

  $$y_i = \\begin{{cases}}
    \\beta_{{01}} + \\beta_{{11}} x_i + \\beta_{{21}} x_i^2 + \\beta_{{31}} x_i^3 + \\varepsilon_i
      & x_i < c \\\\
    \\beta_{{02}} + \\beta_{{12}} x_i + \\beta_{{22}} x_i^2 + \\beta_{{32}} x_i^3 + \\varepsilon_i
      & x_i \\ge c
  \\end{{cases}} \\tag{{7.8}}$$

  <p>兩段各 4 個參數，總共 8 個自由度。ISLP 圖 7.3 左上就是這樣配出來的——
  <strong>函數在節點上斷開，看起來很荒謬</strong>。解法是加約束。每加一個約束就少一個自由度：</p>

  <ul>
    <li><strong>要求連續</strong>（8 → 7）：不能跳，但接點是個 V 字，很不自然（圖 7.3 右上）。</li>
    <li><strong>再要求一階導數連續</strong>（7 → 6）：斜率也接上了，折角不見了。</li>
    <li><strong>再要求二階導數連續</strong>（6 → 5）：這就是<strong>立方樣條</strong>（圖 7.3 左下）。</li>
  </ul>

  <p>一般而言，K 個節點的立方樣條用掉 <strong>K + 4</strong> 個自由度。
  d 次樣條的定義是：分段 d 次多項式，且導數連續到 d − 1 階。
  所以線性樣條只要求函數連續（圖 7.3 右下），而 §7.2 的階梯函數就是 0 次樣條。</p>

{viz(svg("w08knotSvg", 340),
     [info_card("怎麼玩",
                '拖動<span style="color:var(--pt-held);font-weight:700;">橘色</span>的節點 ξ，'
                '再用下面的選項切換要求到第幾階連續。'
                '曲線會從<strong>斷裂 → 折角 → 平滑</strong>。'
                '每加一個約束，右邊的參數個數就少 1。', "圖 7.3"),
      rows_card("目前狀態",
                [("節點 ξ", "50.0", "w08knotXiTxt"), ("約束層級", "二階導數連續", "w08knotLvlTxt"),
                 ("參數個數（自由度）", "5", "w08knotP"),
                 ("RSS", "—", "w08knotRss"), ("R²", "—", "w08knotR2")]),
      info_card("基底是怎麼被拿掉的",
                '完整的 8 個基底是 1, x, x², x³ 再加四個截斷項 '
                'I(x&gt;ξ), (x−ξ)₊, (x−ξ)²₊, (x−ξ)³₊。'
                '<strong>要求連續＝拿掉 I(x&gt;ξ)</strong>（它是唯一會讓函數值跳的），'
                '<strong>再要求一階導數連續＝再拿掉 (x−ξ)₊</strong>，'
                '<strong>再要求二階導數連續＝再拿掉 (x−ξ)²₊</strong>。'
                '剩下的 5 個就是單節點立方樣條的基底，K + 4 = 5。')],
     "w08knotStatus", "拖節點、切換連續性層級，看曲線從斷裂變平滑，同時看自由度從 8 掉到 5。",
     '<label class="mono" style="font-size:.76rem;display:inline-flex;align-items:center;gap:.25rem;cursor:pointer;">'
     '<input type="radio" id="w08knotLv0" name="w08knotLvl" value="0" onchange="w08knotSet(0)"> 不連續</label>'
     '<label class="mono" style="font-size:.76rem;display:inline-flex;align-items:center;gap:.25rem;cursor:pointer;">'
     '<input type="radio" id="w08knotLv1" name="w08knotLvl" value="1" onchange="w08knotSet(1)"> 連續</label>'
     '<label class="mono" style="font-size:.76rem;display:inline-flex;align-items:center;gap:.25rem;cursor:pointer;">'
     '<input type="radio" id="w08knotLv2" name="w08knotLvl" value="2" onchange="w08knotSet(2)"> 一階導數連續</label>'
     '<label class="mono" style="font-size:.76rem;display:inline-flex;align-items:center;gap:.25rem;cursor:pointer;">'
     '<input type="radio" id="w08knotLv3" name="w08knotLvl" value="3" checked onchange="w08knotSet(3)"> 二階導數連續</label>'
     '<button class="btn btn-reset" onclick="w08knotReset()">重置（ξ = 50）</button>',
     provenance=("course-data", "Wage 固定子樣本上的分段多項式；連續性約束依 ISLP 圖 7.3 即時計算。"))}

  <p>那要怎麼真的把約束配進去？不必解限制式最小平方——<strong>換基底就好</strong>。
  從三次多項式的基底 $x, x^2, x^3$ 出發，每個節點加一個<strong>截斷冪基底</strong>
  （truncated power basis）函數：</p>

  $$h(x, \\xi) = (x - \\xi)^3_+ = \\begin{{cases}} (x-\\xi)^3 & x > \\xi \\\\
    0 & \\text{{否則}} \\end{{cases}} \\tag{{7.10}}$$

  <p>加上 $\\beta_4 h(x, \\xi)$ 只會讓<strong>三階</strong>導數在 ξ 跳（跳 $6\\beta_4$），
  函數值、一階、二階導數都保持連續。所以 K 個節點的立方樣條就是對
  $X, X^2, X^3, h(X,\\xi_1), \\ldots, h(X,\\xi_K)$ 做普通的最小平方，
  K + 4 個係數。這就是 (7.9)。</p>

{qa("觀念釐清", [
    ("Q：為什麼三次樣條剛好要求到<strong>二階</strong>導數連續？多一階或少一階會怎樣？",
     "<p>先看少一階。只要求函數值與一階導數連續，二階導數可以跳——"
     "二階導數是「斜率變化的速度」，也就是曲率。曲率突然改變，人眼看得出來："
     "曲線在節點附近會有一個「彈一下」的感覺。所以只到一階不夠。</p>"
     "<p>再看多一階。三次多項式的三階導數是常數 $6d$；如果連三階導數也要求連續，"
     "那 $d$ 在節點兩側必須相同，二階導數又是 $2c + 6dx$，連續加上 $d$ 相同就迫使 $c$ 也相同…"
     "一路推下去，<strong>兩段會退化成同一個三次多項式</strong>——節點等於不存在，"
     "整條曲線變回全域三次多項式，彈性全部消失。所以三次的極限就是二階。</p>"
     "<p>這也是「d 次樣條＝分段 d 次多項式 + 導數連續到 d−1 階」這個定義的來源："
     "d−1 階是<strong>還能留下彈性的最高要求</strong>。書上還補了一句很實用的話："
     "三階導數的不連續人眼幾乎偵測不到，所以立方樣條「看起來」就是平滑的。"
     "這就是為什麼實務上 degree 3 幾乎是唯一的選擇，"
     "更高次只是多花自由度，看起來沒有更平滑。</p>"),
])}

  <h3 id="dx-bs">講義完整實作：<code>BSpline</code> 與 <code>bs()</code></h3>
{card("lab 07 · 三個內部節點的立方樣條", lab_code(CH, 44) + "\n\n" + lab_code(CH, 46),
      lab_output(CH, 46), src=src("44、46"),
      note="<code>BSpline(internal_knots=[25,40,60], intercept=True)</code> 給出 "
           "<strong>7 欄</strong>＝K + 4 = 3 + 4，正好是理論值。"
           "<code>bs()</code> 預設 <code>intercept=False</code>，所以會丟掉一個基底函數"
           "讓模型自己的截距去頂，摘要裡只剩 6 個 <code>bs(age)[j]</code> 加一個 "
           "<code>intercept</code>——加起來還是 7 個參數。<br>"
           "注意這裡用的是 <strong>B-樣條</strong>基底，不是上面講的截斷冪基底。"
           "兩者張出<strong>同一個函數空間</strong>，配出來的曲線一模一樣，"
           "但 B-樣條的設計矩陣是帶狀的（每列只有 degree + 1 個非零元素），條件數低得多。")}

{card("lab 07 · 用 df 代替節點位置", lab_code(CH, 51), lab_output(CH, 51), src=src(51),
      note="要求 6 個自由度（<code>df=6</code>），轉換器就自己把 3 個節點放在 "
           "<strong>33.75、42.0、51.0</strong>——正好是 <code>age</code> 的 25%、50%、75% 分位數。"
           "6 = K + 3（不含截距）。<strong>實務上就是這樣用的：給 df，讓軟體放節點。</strong>"
           "上面那個基底積木元件的兩個節點 33.75 與 51 就是從這裡抄來的。")}

{table(["約束", "自由度（單節點）", "圖 7.3 的位置", "長相"],
       [["都不加（分段三次）", "8", "左上", "在節點斷開，很荒謬"],
        ["函數值連續", "7", "右上", "接上了，但是 V 字折角"],
        ["＋一階導數連續", "6", "（書上沒單獨畫）", "折角消失"],
        ["＋二階導數連續 ＝ <strong>立方樣條</strong>", "<span class='best'>5 = K+4</span>", "左下", "看起來完全平滑"],
        ["線性樣條（只要求連續）", "3 = K+2", "右下", "折線"]])}

{quiz("qSpl", "QUIZ · 樣條的自由度",
      "在 <code>age</code> 上配一個有 <strong>5 個</strong>內部節點的立方樣條（含截距），"
      "要估幾個參數？",
      [(True, "9 個（K + 4 = 5 + 4）",
        "對。從 x, x², x³ 的 3 個，加截距 1 個，再加 5 個截斷冪基底項 (x−ξₖ)³₊，總共 9。等價的說法：6 段 × 4 個參數 − 5 個節點 × 3 個約束 = 24 − 15 = 9。"),
       (False, "24 個（6 段各 4 個參數）",
        "這是<strong>完全不加約束</strong>的分段三次多項式的自由度。加上「連續 + 一階 + 二階導數連續」共 5 × 3 = 15 個約束後，剩下 9 個。"),
       (False, "5 個（節點數就是自由度）",
        "不對。節點數只決定<strong>額外</strong>的彈性；基礎的三次多項式本身就要 4 個參數（含截距）。df = K + 4，不是 K。")])}
"""

# ── P05 natural ───────────────────────────────────────────────────────
BODIES["natural"] = f"""
  <p>立方樣條看起來很漂亮，但有一個藏起來的問題：<strong>兩端的變異很大</strong>。
  在最小節點以左、最大節點以右，資料只從單邊來，三次多項式卻還有完整的四個自由度可以亂扭。
  ISLP 圖 7.4 就在示範這件事。三個節點的立方樣條，兩端的信賴帶「appear fairly wild」。</p>

  <p><strong>自然樣條</strong>（natural spline）的修法很直接：多加兩個邊界約束，
  <strong>要求函數在兩端的區域是線性的</strong>。線性只需要 2 個參數（截距 + 斜率），
  而三次要 4 個，所以每一端省下 2 個自由度，兩端合計省 4 個。
  K 個內部節點的自然立方樣條因此只用 <strong>K + 2</strong> 個參數（含截距）。</p>

{viz(chart("w08natChart", "tall",
           "。此圖的重點：同樣三個節點（25／40／60），立方樣條在 80 歲那端的 95% 信賴帶寬 65.8，"
           "自然樣條只有 37.1——線性約束把邊界的變異砍掉一半。"),
     [info_card("怎麼看這張圖",
                '兩條實線是配適曲線，兩片淡色帶是各自的 95% 信賴帶。'
                '兩者<strong>用完全相同的三個內部節點</strong>（25、40、60），'
                '差別只在自然樣條多了兩端的線性約束。'
                '中間幾乎重疊，<strong>兩端差很多</strong>。', "圖 7.4"),
      rows_card("實測（Wage 全體 n = 3000）",
                [("立方樣條 參數個數", "7", "w08natDfC"),
                 ("自然樣條 參數個數", "5", "w08natDfN"),
                 ("18 歲端帶寬（立方 / 自然）", "—", "w08natWl"),
                 ("80 歲端帶寬（立方 / 自然）", "—", "w08natWr"),
                 ("內部節點", "25 · 40 · 60", "w08natKnots")]),
      info_card("代價是什麼",
                '自然樣條放棄了「兩端也可以彎」的能力。如果真實函數在邊界確實彎得厲害，'
                '自然樣條會配不出來（有偏差）。但邊界的資料本來就少，'
                '<strong>那裡的「彎」通常是雜訊而不是訊號</strong>，'
                '所以這個交換在實務上幾乎總是划算的。')],
     "w08natStatus", "兩條曲線用同樣的三個節點。比較的是兩端信賴帶的寬度。",
     '<button class="btn btn-toggle" id="w08natBandBtn" onclick="w08natToggleBands()">信賴帶：開</button>'
     '<button class="btn btn-toggle" id="w08natCubBtn" onclick="w08natToggleCubic()">立方樣條：開</button>',
     provenance=("course-data", "Wage 全體 3000 筆、相同內部節點的 cubic／natural spline；generator 計算曲線與信賴帶。"))}

  <p>ISLP 圖 7.7 把這件事推到極端：<strong>15 個自由度的自然樣條 vs 15 次多項式</strong>。
  兩者複雜度相同，但多項式在尾端狂野擺盪，自然樣條還很體面。
  這就是「樣條通常優於多項式」的理由：<strong>樣條靠加節點取得彈性、把次數鎖在 3；
  多項式只能靠拉高次數，而高次的代價全部集中在邊界。</strong></p>

{qa("觀念釐清", [
    ("Q：節點該放幾個？放哪裡？",
     "<p><strong>放哪裡：</strong>理論上該把節點放在「函數變化快」的地方，變化慢的地方少放。"
     "實務上幾乎沒人這樣做，因為你事先不知道哪裡變化快。標準做法是<strong>指定自由度，"
     "讓軟體把對應數量的節點放在資料的均勻分位數上</strong>。lab 儲存格 51 的 "
     "<code>BSpline(df=6)</code> 就自動選了 33.75、42.0、51.0，正好是 25%／50%／75% 分位數。"
     "用分位數而不是等距，好處是每一段的樣本數差不多，不會出現「某一段只有 3 個點」的情況。</p>"
     "<p><strong>放幾個：</strong>用交叉驗證。ISLP 圖 7.6 對 <code>Wage</code> 掃了 df = 1 到 10 的"
     "10-fold CV MSE：自然樣條在 df = 3、立方樣條在 df = 4 就已經足夠，"
     "曲線之後就拉平了。做法跟第 5 章完全一樣——留一部分資料、配一個指定節點數的樣條、"
     "在留出的部分算誤差，換不同的 K 重複，選 CV 誤差最小的。</p>"
     "<p>還有一個很務實的答案：§7.7 配多變數 GAM 時，每個變數都要選 df 就太麻煩了，"
     "所以<strong>實務上常常直接把所有項的 df 都定成 4</strong>，先跑起來再說。"
     "書上原話是「we typically adopt a more pragmatic approach」。</p>"),
])}

  <h3 id="dx-ns">講義完整實作：<code>ns()</code> 配自然樣條</h3>
{card("lab 07 · 五個自由度的自然樣條", lab_code(CH, 56), lab_output(CH, 56), src=src(56),
      note="<code>ns('age', df=5)</code>：5 個自由度（不含截距），節點由分位數自動決定。"
           "跟前一節 <code>bs()</code> 的摘要對比一下——<strong>係數的標準誤明顯小很多</strong>"
           "（4.7～11.9 對上 9.6～19.1）。這就是邊界線性約束買到的東西。<br>"
           "ISLP 圖 7.5 用的是 4 個自由度的自然樣條（三個內部節點在 25%／50%／75% 分位數）；"
           "腳註 4 解釋了「含邊界節點共 5 個節點的立方樣條有 9 個自由度，"
           "兩端各 2 個線性約束後剩 5，扣掉被截距吸收的常數就記成 4」。")}

{quiz("qNat", "QUIZ · 自然樣條",
      "自然樣條相對於立方樣條，多了什麼約束、換到了什麼？",
      [(True, "多了「兩端區域必須是線性」的約束，換到邊界處明顯較窄的信賴帶",
        "對。每一端從 4 個參數降到 2 個，兩端共省 4 個自由度。實測：80 歲那端的帶寬從 65.8 降到 37.1。"),
       (False, "多了「節點必須放在分位數上」的約束，換到不必自己選節點位置",
        "不對，這兩件事無關。<code>bs()</code> 與 <code>ns()</code> 都可以用 <code>df</code> 讓軟體自動放分位數節點，也都可以手動指定 <code>internal_knots</code>。自然樣條的約束是關於<strong>邊界的形狀</strong>。"),
       (False, "多了「二階導數在節點連續」的約束，換到更平滑的曲線",
        "不對。二階導數連續是<strong>立方樣條本來就有的</strong>（那正是它之所以叫立方樣條的原因）。自然樣條額外要求的是兩端線性，也就是二階導數在邊界區域<em>等於零</em>。")])}
"""

# ── P06 smooth ────────────────────────────────────────────────────────
BODIES["smooth"] = f"""
  <p>迴歸樣條的流程是：選節點 → 造基底 → 最小平方。<strong>平滑樣條</strong>（smoothing spline）
  換一個完全不同的入口：直接寫下你要的東西，然後解一個最佳化問題。</p>

  <p>我們要一個配得好、又不要太扭的函數 g。「配得好」是 RSS 小，「不要太扭」怎麼寫？
  二階導數 $g''(t)$ 衡量斜率變化的速度，也就是<strong>粗糙度</strong>：
  g 在 t 附近很抖，$|g''(t)|$ 就大；直線的二階導數恆為 0。
  把它平方後在整個範圍上積起來，就得到總粗糙度。於是：</p>

  $$\\min_g \\;\\sum_{{i=1}}^{{n}} \\left(y_i - g(x_i)\\right)^2
    \\;+\\; \\lambda \\int g''(t)^2 \\, dt \\tag{{7.11}}$$

{info("這是「損失＋懲罰」，跟脊迴歸同一個套路", '''第一項是<strong>損失</strong>，逼 g 貼近資料；
  第二項是<strong>懲罰</strong>，逼 g 平滑。λ ≥ 0 是調整參數：<br>
  <strong>λ = 0：</strong>懲罰失效，g 會穿過每一個點（內插），RSS = 0，完全過度配適。<br>
  <strong>λ → ∞：</strong>懲罰無限重，只有 $\\int g''^2 = 0$ 的函數活得下來，
  也就是<strong>直線</strong>。這時損失項退化成普通的線性最小平方，
  所以 g 就是那條最小平方直線。<br>
  中間的 λ 給你介於兩者之間的東西。<strong>λ 控制的就是偏差–變異取捨。</strong>''', "warm")}

  <p>令人意外的是這個無限維最佳化有漂亮的解：使 (7.11) 最小的 g 是
  <strong>在每一個相異的 $x_1, \\ldots, x_n$ 上都有節點的自然立方樣條</strong>。
  但它不等於「拿全部 x 當節點去配自然樣條」。那樣一定過度配適；
  它是那個自然樣條的<strong>收縮版</strong>，收縮的程度由 λ 決定。</p>

  <p>既然每個點都是節點，名目上有 n 個參數。所以我們不用「參數個數」描述它的彈性，
  改用<strong>有效自由度</strong>（effective degrees of freedom）。把配適值寫成</p>

  $$\\hat g_\\lambda = S_\\lambda \\, y, \\qquad
    \\mathrm{{df}}_\\lambda = \\sum_{{i=1}}^{{n}} \\{{S_\\lambda\\}}_{{ii}} \\tag{{7.12–7.13}}$$

  <p>$S_\\lambda$ 是那個 $n \\times n$ 的平滑矩陣，$\\mathrm{{df}}_\\lambda$ 是它的跡。
  λ 從 0 增到 ∞ 時，$\\mathrm{{df}}_\\lambda$ 從 n 一路降到 2。
  它是<strong>連續值</strong>，可以是 6.8 這種數字。</p>

  <p>λ 怎麼選？交叉驗證。而且平滑樣條的 LOOCV 有捷徑，只配一次模型就算得出來
  （跟第 5 章式 5.2 同一個套路，$\\{{S_\\lambda\\}}_{{ii}}$ 扮演槓桿值的角色）：</p>

  $$\\mathrm{{RSS}}_{{\\mathrm{{cv}}}}(\\lambda) = \\sum_{{i=1}}^{{n}}
    \\left(y_i - \\hat g_\\lambda^{{(-i)}}(x_i)\\right)^2
    = \\sum_{{i=1}}^{{n}} \\left[\\frac{{y_i - \\hat g_\\lambda(x_i)}}
    {{1 - \\{{S_\\lambda\\}}_{{ii}}}}\\right]^2$$

{viz(chart("w08lamChart", "tall",
           "。此圖的重點：df = 2 幾乎是直線，df = 19 抖得離譜；"
           "pygam 依 GCV 選出 df = 5.64，跟課本圖 7.8 用 LOOCV 選出的 6.8 很接近。"),
     [info_card("怎麼看這張圖",
                '灰點是 90 筆子樣本（背景），曲線是用<strong>全部 3000 筆</strong>配的平滑樣條。'
                '滑桿的刻度是有效自由度 df<sub>λ</sub>，不是 λ 本身，'
                '因為 df 才是人看得懂的尺度（λ = 5.2×10⁹ 對上 df = 2）。', "圖 7.8"),
      rows_card("這個 df 的成績",
                [("df<sub>λ</sub>", "5.0", "w08lamDf"), ("對應的 λ", "—", "w08lamLam"),
                 ("GCV", "—", "w08lamGcv"), ("解釋的離差比例", "—", "w08lamR2")]),
      info_card("gridsearch 選出來的是什麼",
                '<code>pygam</code> 的 <code>gridsearch()</code> 依 <strong>GCV</strong>'
                '（廣義交叉驗證）挑 λ，在這份資料上選出 λ = 251.19、'
                'df<sub>λ</sub> = <strong>5.64</strong>、GCV = 1596.88。'
                '課本圖 7.8 的 <strong>6.8</strong> 是用 LOOCV 挑的，'
                '兩者的準則不同、答案自然不會完全一樣，但都落在 5～7，'
                '<strong>結論一致：這份資料不需要 16 個自由度。</strong>')],
     "w08lamStatus", "推滑桿改有效自由度。df = 2 是直線，df 愈大愈抖。",
     slider("w08lamSl", "df", 0, 9, 1, 3, "5.0", "w08lamSet()")
     + '<button class="btn btn-toggle" id="w08lamPickBtn" onclick="w08lamTogglePick()">GCV 選出的曲線：開</button>'
     + '<button class="btn btn-reset" onclick="w08lamReset()">回到 df = 5</button>',
     provenance=("course-data", "Wage 全體資料的 smoothing spline／pygam gridsearch；GCV、λ 與有效 df 由 generator 計算。"))}

{qa("觀念釐清", [
    ("Q：「自由度」在這一章出現了三次，它們是同一回事嗎？",
     "<p><strong>不完全是。</strong>前兩個是同一回事，第三個是另一種東西。</p>"
     "<p><strong>（1）多項式的次數 d、（2）樣條的 K + 4：</strong>"
     "這兩個都是<strong>老實的參數計數</strong>。你要估幾個 β，自由度就是幾。"
     "它們一定是整數，而且「d = 4」跟「3 個節點的立方樣條（df = 7）」都可以直接對應到"
     "設計矩陣有幾欄。第 3 章那套「殘差自由度 = n − p」照用。</p>"
     "<p><strong>（3）平滑樣條的 $\\mathrm{df}_\\lambda$：</strong>這個不是參數計數。"
     "平滑樣條名目上有 n 個參數（每個 x 都是節點），但它們被懲罰項<strong>綁得死死的</strong>。"
     "所以我們改量「這個平滑器實際上用掉多少彈性」，定義成平滑矩陣的跡 "
     "$\\sum_i \\{S_\\lambda\\}_{ii}$。它是連續的（6.8、5.64 都合法），"
     "而且會隨 λ 連續變化。</p>"
     "<p>把它們放在同一把尺上看是有道理的：$\\mathrm{df}_\\lambda = 5$ 的平滑樣條，"
     "彈性大約等於一個 5 個參數的迴歸樣條。這就是為什麼 <code>pygam</code> 提供 "
     "<code>approx_lam(X, term, df)</code> 讓你「用 df 指定 λ」——"
     "<strong>λ 沒有直覺，df 有</strong>。局部迴歸也可以這樣量："
     "ISLP 圖 7.10 標了「span 0.2 相當於 16.4 個自由度、span 0.7 相當於 5.3 個」。</p>"),
])}

  <h3 id="dx-lam">講義完整實作：用 df 反解 λ</h3>
{card("lab 07 · approx_lam：指定自由度，反解懲罰參數", lab_code(CH, 71), lab_output(CH, 71),
      src=src(71),
      note="<code>approx_lam(X_age, age_term, 4)</code> 找出「讓有效自由度等於 4」的那個 λ，"
           "回代驗算得到 <code>4.000000100000307</code>。"
           "注意 lab 的說明：<strong>這個 df 包含平滑樣條那個沒有被懲罰的截距與線性項，"
           "所以下限是 2</strong>。這正好對上課本「λ → ∞ 時 df 降到 2」。"
           "所以 lab 儲存格 73 畫圖時用 <code>approx_lam(..., df+1)</code>，"
           "標籤上的 <code>df=1</code> 其實就是直線配適。<br>"
           "上面元件的滑桿刻度用的是 <code>degrees_of_freedom()</code> 的定義（含截距），"
           "所以最左邊是 2 而不是 0。")}

{quiz("qLam", "QUIZ · 平滑樣條的懲罰",
      "$\\lambda \\to \\infty$ 時，(7.11) 的解 $\\hat g$ 會變成什麼？",
      [(True, "最小平方<strong>直線</strong>，因為只有二階導數恆為 0 的函數才不被懲罰",
        "對。懲罰項迫使 $\\int g''(t)^2 dt = 0$，也就是 g 必須是一次函數；在這個限制下最小化 RSS，就得到普通的最小平方直線。這時有效自由度是 2（截距 + 斜率）。"),
       (False, "常數函數 $\\hat g(x) = \\bar y$，因為懲罰項要求函數完全不變化",
        "不對，錯在懲罰的是<strong>二階</strong>導數不是一階。要求 $g' = 0$ 才會得到常數；$g'' = 0$ 允許固定的斜率。（ISLP §7.9 第 2 題就在玩這個：把懲罰換成 m 階導數，m = 1 才給常數。）"),
       (False, "在每個 xᵢ 上都有節點的自然立方樣條，因為解永遠是自然立方樹條",
        "話只對一半。解的<em>形式</em>確實永遠是那個自然立方樣條，但係數被 λ 收縮；λ → ∞ 時收縮到只剩線性部分，圖形就是一條直線。這一題問的是「長什麼樣」。")])}
"""

# ── P07 loess ─────────────────────────────────────────────────────────
BODIES["loess"] = f"""
  <p>再換一個想法。前面所有方法都在配一個<strong>全域</strong>的函數形式
  （就算是分段的，段的邊界也是事先定死的）。局部迴歸（local regression）說：
  要預測 $x_0$ 上的值，就只用 $x_0$ 附近的點，配一條加權直線，取它在 $x_0$ 的值。
  換一個 $x_0$，重配一次。</p>

{info("ISLP 演算法 7.1 · 在 X = x₀ 的局部迴歸", '''<strong>1.</strong> 取出 x 離 x₀ 最近的
  s = k/n 比例的訓練點。<br>
  <strong>2.</strong> 給鄰域內每個點一個權重 $K_{i0}$：最近的最重，最遠的那個剛好是 0，
  鄰域外全部是 0。<br>
  <strong>3.</strong> 用這些權重做加權最小平方，找 $\\hat\\beta_0, \\hat\\beta_1$ 使
  $\\sum_{i=1}^{n} K_{i0}\\left(y_i - \\beta_0 - \\beta_1 x_i\\right)^2$ 最小。<br>
  <strong>4.</strong> 在 x₀ 的配適值就是 $\\hat f(x_0) = \\hat\\beta_0 + \\hat\\beta_1 x_0$。''')}

  <p>要做的選擇有三個：權重函數 K 怎麼定、第 3 步配常數／直線／二次、以及
  <strong>跨距</strong>（span）s 取多少。前兩個影響不大，
  <strong>s 才是關鍵。它扮演的角色跟平滑樣條的 λ 一樣</strong>。
  s 小則鄰域窄、曲線抖；s 大則鄰域寬、接近全域配適。s 一樣可以用交叉驗證選。</p>

{viz(svg("w08loessSvg", 340),
     [info_card("虛擬碼",
                '<div class="pseudo-code" id="w08loessCode" style="font-size:.72rem;">'
                '<span class="line" data-l="1"><span class="kw">for</span> x0 <span class="kw">in</span> 格點:</span>\n'
                '<span class="line" data-l="2">    d = |x - x0|；取最近的 k = s·n 個</span>\n'
                '<span class="line" data-l="3">    w = tricube(d / d_max)</span>\n'
                '<span class="line" data-l="4">    b0, b1 = 加權最小平方(x, y, w)</span>\n'
                '<span class="line" data-l="5">    f[x0] = b0 + b1 * x0</span></div>', "CODE"),
      rows_card("這個目標點",
                [("跨距 s", "0.30", "w08loessSpanTxt"), ("鄰域點數 k", "—", "w08loessK"),
                 ("目標點 x₀", "—", "w08loessX0"), ("局部斜率 b₁", "—", "w08loessB1"),
                 ("配適值 f̂(x₀)", "—", "w08loessFhat")]),
      info_card("圖上的元素",
                '<span style="color:var(--pt-held);font-weight:700;">橘色垂直線</span>是目前的 x₀，'
                '橘點是它的鄰域，<strong>黃色鐘形</strong>是 tricube 權重（越高越重），'
                '短橘線段是這一次的加權迴歸直線，'
                '<span style="color:var(--fit-line);font-weight:700;">紅色粗曲線</span>是掃過去累積出來的 f̂。'
                '淡紅細線是這個 span 的完整曲線。', "圖 7.9"),
      info_card("兩個要記住的限制",
                '<strong>1. 記憶式（memory-based）：</strong>每做一次預測都要用到全部訓練資料，'
                '沒有一組係數可以存下來。模型體積 = 資料體積。<br>'
                '<strong>2. 維度一高就垮：</strong>p 超過 3 或 4，x₀ 附近幾乎找不到點'
                '（跟第 3 章 KNN 的維度詛咒同一個病）。所以局部迴歸主要用在 1～2 維，'
                '或者當 GAM 的單變數積木。')],
     "w08loessStatus", "直接調 span 與 x₀，看鄰域、權重、局部斜率與配適值怎麼一起變。",
     slider("w08loessSl", "span s", 10, 90, 5, 30, "0.30", "w08loessSetSpan()", "200px")
     + slider("w08loessXSl", "目標點 x₀", 20, 77, 1, 49, "49", "w08loessSetX0()", "200px")
     + '<button class="btn btn-play" onclick="w08loessStart()">▶ 自動掃描（可選）</button>'
     '<button class="btn btn-reset" onclick="w08loessReset()">重置</button>',
     provenance=("course-data", "Wage 固定 90 筆子樣本；tricube 權重與局部線性最小平方由瀏覽器即時計算。"))}

{table(["span s", "鄰域", "曲線", "ISLP 圖 7.10 標的有效自由度"],
       [["0.2", "20% 的資料", "抖，跟著局部起伏", "16.4"],
        ["0.7", "70% 的資料", "平滑", "5.3"],
        ["→ 1.0", "全部資料", "趨近一條全域直線", "→ 2"]])}
  <p style="font-size:.82rem;color:var(--muted);">上表的 16.4 與 5.3 取自 ISLP 圖 7.10 的圖例
  （<code>Wage</code>，局部線性）。lab 儲存格 125 畫的是 span 0.2 與 0.5。
  <strong>注意上面元件是瀏覽器即時算的 tricube 加權最小平方，不含 <code>lowess()</code>
  的穩健疊代（robustifying iterations），所以數字不會跟 lab 完全對上。
  它示範的是機制，不是重現套件的輸出。</strong></p>

  <h3 id="dx-low">講義完整實作：<code>statsmodels</code> 的 <code>lowess()</code></h3>
{card("lab 07 · 兩個 span 的局部線性迴歸", lab_code(CH, 125), None, src=src("124、125"),
      note="<code>frac=span</code> 就是跨距，<code>xvals=age_grid</code> 指定要在哪些點求配適值。"
           "lab 用 0.2 與 0.5，畫出來 0.5 明顯比 0.2 平滑。<br>"
           "這一格只存了圖沒有存文字輸出，所以這裡不放「預期輸出」——"
           "契約規定預期輸出一律逐字取自 lab，沒有就不編。<br>"
           "另外注意 lab 的註解：<strong><code>pygam</code> 不支援把局部迴歸當成 GAM 的項</strong>，"
           "有些 GAM 實作（例如 R 的 <code>gam</code>）可以。")}

{quiz("qLo", "QUIZ · 局部迴歸",
      "為什麼局部迴歸被叫做「記憶式（memory-based）」方法？",
      [(True, "因為每算一次預測都要重新用到全部訓練資料，沒有一組固定的係數可以存起來",
        "對。每換一個 x₀，權重 $K_{i0}$ 全部都變，要重配一次加權迴歸。這跟最近鄰法是同一種性質——模型「就是」資料本身。"),
       (False, "因為它把每個訓練點的預測值先算好存起來，查表時直接取用",
        "不對，方向剛好相反。真正的問題是<strong>沒辦法</strong>先算好——新的 x₀ 可以落在任何地方，都要重新配。"),
       (False, "因為它需要記住每個節點的位置與對應的係數",
        "不對，那是<strong>迴歸樣條</strong>的性質（而且樣條配完之後只要留 K + 4 個係數就好）。局部迴歸根本沒有節點。")])}
"""

# ── P08 GAM ───────────────────────────────────────────────────────────
BODIES["gam"] = f"""
  <p>前面七節都只處理<strong>一個</strong>預測變數。現在把它們裝到多變數上。
  多元線性迴歸是 $y_i = \\beta_0 + \\sum_j \\beta_j x_{{ij}} + \\varepsilon_i$；
  把每個線性項 $\\beta_j x_{{ij}}$ 換成各自的非線性函數 $f_j(x_{{ij}})$，就得到
  <strong>廣義加法模型</strong>（generalized additive model, GAM）：</p>

  $$y_i = \\beta_0 + \\sum_{{j=1}}^{{p}} f_j(x_{{ij}}) + \\varepsilon_i
    = \\beta_0 + f_1(x_{{i1}}) + \\cdots + f_p(x_{{ip}}) + \\varepsilon_i \\tag{{7.15}}$$

  <p>「加法」的意思就是：<strong>各變數的貢獻是相加的</strong>，每個 $f_j$ 各自配、再加起來。
  GAM 漂亮的地方在於前面每一種單變數方法都可以當積木用——
  自然樣條、平滑樣條、局部迴歸、甚至多項式，混搭也行。
  ISLP 圖 7.11／7.12 配的就是</p>

  $$\\mathrm{{wage}} = \\beta_0 + f_1(\\mathrm{{year}}) + f_2(\\mathrm{{age}})
    + f_3(\\mathrm{{education}}) + \\varepsilon \\tag{{7.16}}$$

  <p>其中 education 是類別變數，$f_3$ 就是「每個層級一個常數」（虛擬變數）。
  如果 $f_1, f_2$ 用<strong>自然樣條</strong>，整個模型只是一個大號的線性迴歸
  （基底矩陣橫向疊起來就好），<code>sm.OLS()</code> 一行配完。這是圖 7.11。
  如果用<strong>平滑樣條</strong>，最小平方就不夠了，要用
  <strong>逆向配適</strong>（backfitting）。這是圖 7.12。</p>

{info("逆向配適在做什麼", '''輪流更新每一個 $f_j$：更新第 j 個的時候把其他項固定，
  對<strong>偏殘差</strong>（partial residual）做一次單變數平滑。以 p = 3、更新 $f_3$ 為例：<br>
  $r_i = y_i - \\hat f_1(x_{i1}) - \\hat f_2(x_{i2})$，
  然後把 $r_i$ 當反應變數、對 $X_3$ 配一個平滑樣條，得到新的 $\\hat f_3$。<br>
  換下一個變數，重複，直到不再變動。<strong>好處是你只要有單變數的配適工具，
  就能配任意多變數的加法模型。</strong>ISLP §7.9 第 11、12 題用線性迴歸版本讓你手動跑一遍。''')}

{viz('      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.5rem;">\n'
     + chart("w08gamYear", "", "。f̂(year)：薪水隨年份微幅上升，幾乎是直線（可能是通膨）。")
     + "\n"
     + chart("w08gamAge", "", "。f̂(age)：中年最高，年輕與年長都低。這一項明顯需要非線性。")
     + "\n"
     + chart("w08gamEdu", "", "。f̂(education)：學歷愈高薪水愈高，五個層級各一個常數。")
     + "\n      </div>",
     [info_card("怎麼看這三張圖",
                '每一張都是一個 $\\hat f_k$ 的<strong>偏依賴圖</strong>：'
                '其他變數固定在平均值，只讓這一個變數在格點上跑。'
                '虛線是逐點 95% 信賴帶。<strong>三張圖的縱軸都是「對 wage 的效果」</strong>，'
                '所以可以直接比高低——age 與 education 的擺幅遠大於 year。', "圖 7.11–7.12"),
      rows_card("這一組 df 的成績",
                [("age 的 df", "5.0", "w08gamAgeDf"), ("year 的 df", "5.0", "w08gamYearDf"),
                 ("模型總有效自由度", "—", "w08gamEdof"),
                 ("deviance（＝RSS）", "—", "w08gamDev"),
                 ("Pseudo R²", "—", "w08gamR2"), ("GCV", "—", "w08gamGcv")]),
      info_card("為什麼 education 沒有滑桿",
                'education 是類別變數，在 <code>pygam</code> 裡用 <code>f_gam(2, lam=0)</code> '
                '指定——<strong>類別項就是每個層級一個常數，沒有「平滑程度」可以調</strong>，'
                '而且 <code>lam=0</code> 表示完全不收縮。'
                '它的自由度固定是「層級數 − 1」。'),
      info_card("加 df 換到多少",
                'age 的 df 從 2 加到 10，Pseudo R² 只從 0.263 爬到 0.294；'
                'year 的 df 從 2 加到 6，R² 從 0.292 到 0.293——'
                '<strong>year 幾乎不需要非線性</strong>。'
                'lab 儲存格 96 的 ANOVA 就是在檢定這件事，結論是「year 需要線性項'
                '（p = 1.7e−07）但不需要非線性」。')],
     "w08gamStatus", "推兩個滑桿改 age 與 year 的自由度，右邊看模型整體的成績怎麼變。",
     slider("w08gamAgeSl", "age df", 0, 5, 1, 3, "5.0", "w08gamSet()", "200px")
     + slider("w08gamYearSl", "year df", 0, 4, 1, 3, "5.0", "w08gamSet()", "200px")
     + '<button class="btn btn-reset" onclick="w08gamReset()">回到 lab 的設定</button>',
     provenance=("course-data", "Wage 的 year／age／education GAM；曲線、信賴帶與整體指標由 generator 計算。"))}

{table(["GAM 的優點 ✔", "GAM 的限制 ✘"],
       [["每個 $X_j$ 各配一個非線性 $f_j$，不必手動試變換", "<strong>模型被限制成加法的</strong>，變數多的時候會漏掉重要的交互作用"],
        ["非線性配適通常預測更準", "要交互作用得手動加 $X_j \\times X_k$ 或二維的 $f_{jk}$ 項"],
        ["因為是加法的，可以固定其他變數單獨看某一個變數的效果", "二維平滑器（thin-plate spline 之類）不在這一章的範圍"],
        ["每個 $f_j$ 的平滑程度可以用自由度總結", "完全一般的模型還是得靠第 8 章的隨機森林與提升法"]])}

  <p>整套邏輯搬到分類問題只要把 (7.17) 的 logit 換成加法形式：</p>

  $$\\log\\left(\\frac{{p(X)}}{{1 - p(X)}}\\right) = \\beta_0 + f_1(X_1) + f_2(X_2)
    + \\cdots + f_p(X_p) \\tag{{7.18}}$$

  <p>ISLP 圖 7.13 對 <code>Wage</code> 配 $I(\\text{{wage}} > 250)$，
  結果最後一張圖的第一個層級 <code>&lt;HS</code> 信賴帶大到看不出東西，
  因為<strong>那個層級裡一個高收入者都沒有</strong>（lab 儲存格 105 的交叉表：268 個人、0 個高收入者）。
  拿掉那群人重配就正常了（圖 7.14）。<strong>這是很典型的一課：
  模型爆掉的時候先去看列聯表，不要先怪演算法。</strong></p>

{qa("觀念釐清", [
    ("Q：GAM 保住了什麼、放棄了什麼？",
     "<p><strong>保住的是加法可解釋性。</strong>因為模型是 $\\beta_0 + \\sum_j f_j(x_j)$，"
     "每個變數的貢獻可以單獨畫出來、單獨解讀：「固定 age 與 education，"
     "wage 隨 year 微幅上升」這種句子講得出來，而且圖 7.11 那三張圖就是證據。"
     "線性模型的 $\\beta_j$ 也有這個好處，但 GAM 不必假設那個關係是直線。"
     "額外的好處是每個 $f_j$ 的複雜度可以用自由度總結，一個數字就講完。</p>"
     "<p><strong>放棄的是交互作用。</strong>加法性意味著「age 的效果」跟 education 是什麼無關。"
     "如果現實是「大學畢業的人薪水在 40 歲達到高峰，高中畢業的人在 30 歲」，"
     "GAM 抓不到。它只會給你一條平均起來的 $f_2(\\text{age})$。</p>"
     "<p>要補救有兩條路：手動加 $X_j \\times X_k$ 這種乘積項，"
     "或者加二維的 $f_{jk}(X_j, X_k)$（用二維平滑器配，講義附錄的 thin-plate spline 就是這個）。"
     "但兩條路都要你<strong>事先知道哪一對變數有交互作用</strong>。"
     "如果你不知道、又有很多變數，那就該去第 8 章找隨機森林與提升法。"
     "它們自動抓交互作用，代價是失去這裡的可解釋性。"
     "書上的定位很準：<strong>GAM 是線性模型與完全無母數方法之間一個有用的折衷。</strong></p>"),
])}

  <h3 id="dx-gam">講義完整實作：<code>pygam</code> 配 GAM</h3>
{card("lab 07 · 模型規格與用 df 設定平滑程度",
      lab_code(CH, 82) + "\n\n" + lab_code(CH, 86), None, src=src("82、86"),
      note="<code>s_gam(0)</code> 是 age 的平滑樣條、<code>s_gam(1, n_splines=7)</code> 是 year"
           "（year 只有 7 個相異值，所以基底也只給 7 個）、"
           "<code>f_gam(2, lam=0)</code> 是 education 的類別項且不收縮。<br>"
           "第二段把兩個平滑項的 λ 用 <code>approx_lam(..., df=4+1)</code> 反解成「4 個自由度」"
           "（加 1 是因為 df 含截距），再重配一次。"
           "<strong>先 fit 再設 lam 再 fit</strong> 的順序是必要的——"
           "<code>approx_lam</code> 要用到 fit 時才建好的節點資訊。"
           "上面元件的「回到 lab 的設定」就是這一組（age df 5、year df 5）。")}

  <h3 id="dx-sum">講義完整實作：GAM 的摘要，以及它自己承認的 bug</h3>
{card("lab 07 · gam_full.summary()", lab_code(CH, 98), lab_output(CH, 98), src=src(98),
      note="幾個要對的數字：<strong>Effective DoF 12.9927</strong>（age 5.1 + year 4.0 + "
           "education 4.0 + 截距）、<strong>GCV 1246.1129</strong>、"
           "<strong>Pseudo R² 0.2928</strong>。上面元件的「回到 lab 的設定」右側顯示的就是這三個數字，"
           "由 <code>tools/frames/gen_nonlin.py</code> 用同一組設定重算，對到小數第四位。<br>"
           "然後注意那三段警告。<code>pygam</code> 自己說：<strong>「平滑參數是估出來的時候，"
           "這裡的 p 值會比該有的小很多，不要拿它做推論」</strong>"
           "（<code>pyGAM</code> issue #163）。這是很好的示範——"
           "套件印給你的東西不代表你可以引用它。要檢定就用 lab 儲存格 96 的 "
           "<code>anova_gam()</code> 比巢狀模型。")}

{quiz("qGam", "QUIZ · GAM 的加法性",
      "如果真實情況是「大學畢業者的薪水在 40 歲達到高峰，高中畢業者在 30 歲」，"
      "(7.16) 這個 GAM 會發生什麼事？",
      [(True, "抓不到。它只會給一條平均起來的 f̂(age)，因為加法性假設 age 的效果與 education 無關",
        "對。這就是 GAM 唯一的重大限制。要處理的話得手動加 age × education 的交互作用項，或改用第 8 章會自動抓交互作用的樹狀集成方法。"),
       (False, "會抓到，因為 f̂(age) 是非線性的，非線性本身就包含了交互作用",
        "不對，這是把兩件事混在一起了。<strong>非線性</strong>講的是「單一變數的效果不是直線」；<strong>交互作用</strong>講的是「一個變數的效果會隨另一個變數改變」。GAM 給你前者，預設沒有後者。"),
       (False, "會抓到，因為 education 是類別變數，f̂₃ 會為每個層級各配一條 age 曲線",
        "不對。$f_3(\\text{education})$ 只是每個層級一個<strong>常數位移</strong>，它把整條 age 曲線上下平移，不會改變曲線的形狀或峰值位置。要各層級各一條曲線，那已經是交互作用了。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 7.9 第 1 題（c)(d)(e)",
      "第 1 題要你證明 $f(x) = \\beta_0 + \\beta_1 x + \\beta_2 x^2 + \\beta_3 x^3 "
      "+ \\beta_4 (x-\\xi)^3_+$ 真的是立方樣條。"
      "為什麼加上 $\\beta_4 (x-\\xi)^3_+$ 這一項不會破壞 ξ 上的連續性與一、二階導數連續？",
      [(True, "因為 $(x-\\xi)^3$ 本身與它的一階、二階導數在 $x = \\xi$ 都等於 0，只有三階導數會跳",
        "對。$(x-\\xi)^3$、$3(x-\\xi)^2$、$6(x-\\xi)$ 在 $x=\\xi$ 全是 0，所以左右兩段的 f、f′、f″ 在 ξ 上一致；第三階導數從 $6\\beta_3$ 跳到 $6(\\beta_3+\\beta_4)$。這正是截斷冪基底被設計成三次的理由。"),
       (False, "因為 $\\beta_4$ 通常估出來很小，所以造成的跳躍可以忽略",
        "不對。這一題要的是<strong>對任何</strong> $\\beta_0, \\ldots, \\beta_4$ 都成立的恆等式（題幹寫了 regardless of the values），不是「近似成立」。$\\beta_4$ 再大也不會破壞連續性。"),
       (False, "因為指示函數 $I(x > \\xi)$ 在 ξ 上有定義，所以函數在該點連續",
        "混淆了。$(x-\\xi)^3_+$ 確實可以寫成 $(x-\\xi)^3 I(x>\\xi)$，但單獨的 $I(x>\\xi)$ 會讓函數<strong>跳</strong>（本頁 P04 那個元件的「不連續」層級就是把它加進來）。連續性來自 $(x-\\xi)^3$ 這個因子在 ξ 歸零，不是來自指示函數。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 7.9 第 2 題（d)",
      "第 2 題把懲罰換成 $\\lambda \\int \\left[g^{{(m)}}(x)\\right]^2 dx$，"
      "要你畫出各種 (λ, m) 下的 $\\hat g$。當 $\\lambda = \\infty$、$m = 3$ 時，$\\hat g$ 長什麼樣？",
      [(True, "一條二次曲線（最小平方拋物線）",
        "對。$\\lambda = \\infty$ 迫使 $\\int (g^{(3)})^2 = 0$，也就是 $g''' \\equiv 0$，而三階導數恆為 0 的函數就是二次多項式。在這個限制下最小化 RSS，得到最小平方拋物線。順帶把整題背下來：m = 0 → $\\hat g = 0$；m = 1 → 常數 $\\bar y$；m = 2 → 直線；m = 3 → 拋物線。"),
       (False, "一條直線（最小平方迴歸線）",
        "這是 <strong>m = 2</strong> 的答案（$g'' = 0$ 才逼出直線）。m = 3 只要求三階導數為 0，允許二次項存在，所以還多一分彈性。"),
       (False, "一條穿過每一個資料點的內插曲線",
        "這是 <strong>λ = 0</strong> 的答案（第 (e) 小題），跟 m 是幾無關。$\\lambda = \\infty$ 的意思剛好相反：懲罰無限重，彈性被壓到極限。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 7.9 第 3 題",
      "第 3 題給基底 $b_1(X) = X$、$b_2(X) = (X-1)^2 I(X \\ge 1)$，"
      "配出 $\\hat\\beta_0 = 1, \\hat\\beta_1 = 1, \\hat\\beta_2 = -2$，要你畫出 $X \\in [-2, 2]$ 的曲線。"
      "下面哪個描述是對的？",
      [(True, "$X < 1$ 是斜率 1 的直線（在 $X=1$ 到達 2）；$X \\ge 1$ 變成開口向下的拋物線，在 $X = 1.25$ 到最高的 2.125，$X = 2$ 掉回 1；整條曲線的值與斜率在 $X=1$ 都連續",
        "對。$X<1$ 時 $\\hat Y = 1 + X$，從 $(-2,-1)$ 到 $(1,2)$。$X \\ge 1$ 時 $\\hat Y = 1 + X - 2(X-1)^2$；導數 $1 - 4(X-1)$ 在 $X=1$ 等於 1（跟左邊接得上），在 $X=1.25$ 歸零（極大值 2.125），$X=2$ 時 $\\hat Y = 1$。"),
       (False, "$X \\ge 1$ 時從 2 單調下降到 1，因為 $\\hat\\beta_2 = -2$ 是負的",
        "漏掉了極大值。$\\hat\\beta_2 < 0$ 確實讓拋物線開口向下，但頂點不在 $X=1$——導數在 $X=1$ 還是正的（等於 1），要到 $X=1.25$ 才轉負。所以曲線先升到 2.125 再降。"),
       (False, "曲線在 $X = 1$ 有一個跳躍，因為指示函數 $I(X \\ge 1)$ 在那裡開關",
        "不對。$(X-1)^2$ 這個因子在 $X=1$ 等於 0，把跳躍抹平了，而且它的一階導數 $2(X-1)$ 在 $X=1$ 也是 0，所以連斜率都連續。會跳的是像 $I(X \\ge 1)$ 這種<em>沒有</em>乘上歸零因子的項。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 7.9 第 5 題（a)",
      "第 5 題比較兩個平滑器：$\\hat g_1$ 懲罰 $\\int \\left[g^{{(3)}}\\right]^2$，"
      "$\\hat g_2$ 懲罰 $\\int \\left[g^{{(4)}}\\right]^2$。$\\lambda \\to \\infty$ 時，"
      "哪一個的<strong>訓練</strong> RSS 較小？",
      [(True, "$\\hat g_2$，因為它被逼成三次多項式，比被逼成二次多項式的 $\\hat g_1$ 更有彈性",
        "對。$\\lambda \\to \\infty$ 讓 $g^{(4)} \\equiv 0$（三次多項式）或 $g^{(3)} \\equiv 0$（二次多項式）。三次多項式的函數空間包含二次多項式，參數多一個，所以訓練 RSS 一定不會更大。第 (b) 小題的答案是「說不出來」——測試 RSS 取決於真實函數；第 (c) 小題 λ = 0 時兩者都內插，訓練與測試 RSS 都相同。"),
       (False, "$\\hat g_1$，因為懲罰的導數階數較低，代表約束較弱",
        "反了。懲罰<strong>低</strong>階導數是<strong>更強</strong>的約束：要求 $g'''=0$ 只剩二次多項式，要求 $g^{(4)}=0$ 還可以是三次多項式。階數愈高，被允許的函數族愈大。"),
       (False, "兩者相同，因為 $\\lambda \\to \\infty$ 時兩個懲罰項都趨近於 0，模型退化成同一個",
        "不對。兩個懲罰<em>積分值</em>都被壓到 0，但被壓成 0 的是<strong>不同的導數</strong>，留下的函數族不一樣（二次 vs 三次）。同樣的邏輯：m = 0 會把 $\\hat g$ 壓成常數 0，也不是「跟別人一樣」。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>七種方法對照</h3>
{table(["方法", "基底／機制", "彈性由什麼控制", "自由度", "邊界", "選參數的辦法"],
       [["多項式", "$x, x^2, \\ldots, x^d$", "次數 d", "d + 1", "<span class='worst'>差</span>", "ANOVA 或 CV"],
        ["階梯函數", "$I(c_k \\le x < c_{k+1})$", "切點數 K", "K + 1", "尚可", "CV"],
        ["線性樣條", "$x, (x-\\xi_k)_+$", "節點數 K", "K + 2", "尚可", "CV"],
        ["立方樣條", "$x, x^2, x^3, (x-\\xi_k)^3_+$", "節點數 K", "K + 4", "差（帶會爆）", "CV（圖 7.6 右）"],
        ["自然樣條", "立方樣條 + 兩端線性", "節點數 K", "K + 2", "<span class='best'>好</span>", "CV（圖 7.6 左）"],
        ["平滑樣條", "全部 x 當節點 + 二階導數懲罰", "λ", "df$_\\lambda$（連續，2 到 n）", "好", "LOOCV 捷徑 / GCV"],
        ["局部迴歸", "鄰域內加權最小平方", "跨距 s", "以等效 df 表示", "差（單邊資料）", "CV"]])}

  <h3>Wage 上的實測數字（本頁元件用的就是這些）</h3>
{table(["多項式次數 d", "1", "2", "4", "8", "15"],
       [["訓練 MSE", "1674.1", "1597.8", "1590.5", "1587.9", "1585.1"],
        ["10-fold CV MSE", "1676.7", "1600.8", "<span class='best'>1596.0</span>", "1597.2", "<span class='worst'>1603.3</span>"],
        ["80 歲端 95% 帶寬", "10.0", "23.3", "53.5", "76.8", "<span class='worst'>78.3</span>"],
        ["中央（49 歲）帶寬", "3.5", "3.7", "4.4", "5.6", "7.3"]])}
{table(["樣條（三個內部節點 25／40／60）", "參數個數", "18 歲端帶寬", "80 歲端帶寬"],
       [["立方樣條 <code>bs()</code>", "7 = K + 4", "37.1", "<span class='worst'>65.8</span>"],
        ["自然樣條 <code>ns()</code>", "5 = K + 2", "<span class='best'>20.2</span>", "<span class='best'>37.1</span>"]])}
  <p style="font-size:.82rem;color:var(--muted);">平滑樣條：<code>pygam</code> 的
  <code>gridsearch()</code> 依 GCV 選出 λ = 251.19、df<sub>λ</sub> = 5.64；
  課本圖 7.8 用 LOOCV 選出 6.8。GAM（age df 5、year df 5）：
  Effective DoF 12.99、GCV 1246.1、Pseudo R² 0.2928、deviance 3 693 143——
  跟 lab 儲存格 98 的 <code>12.9927 / 1246.1129 / 0.2928</code> 與儲存格 96 的
  <code>3.693143e+06</code> 相符。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["多項式迴歸", "$y = \\beta_0 + \\beta_1 x + \\cdots + \\beta_d x^d + \\varepsilon$", "式 7.1"],
        ["配適值的變異", "$\\widehat{\\operatorname{Var}}[\\hat f(x_0)] = \\ell_0^{\\mathsf T} \\hat C \\ell_0$",
         "式 7.2 腳註；信賴帶的來源"],
        ["階梯函數", "$y = \\beta_0 + \\beta_1 C_1(x) + \\cdots + \\beta_K C_K(x) + \\varepsilon$", "式 7.5；丟掉 $C_0$"],
        ["基底函數框架", "$y = \\beta_0 + \\sum_{k=1}^{K} \\beta_k b_k(x) + \\varepsilon$", "式 7.7；整章的骨架"],
        ["截斷冪基底", "$h(x, \\xi) = (x-\\xi)^3_+$", "式 7.10；每個節點加一個"],
        ["立方樣條的自由度", "K + 4", "K 個內部節點，含截距"],
        ["自然樣條的自由度", "K + 2", "兩端各 2 個線性約束"],
        ["平滑樣條", "$\\min_g \\sum_i (y_i - g(x_i))^2 + \\lambda \\int g''(t)^2 dt$", "式 7.11；損失＋懲罰"],
        ["有效自由度", "$\\mathrm{df}_\\lambda = \\sum_i \\{S_\\lambda\\}_{ii}$，$\\hat g_\\lambda = S_\\lambda y$",
         "式 7.12–7.13；λ: 0→∞ 時 df: n→2"],
        ["平滑樣條的 LOOCV",
         "$\\sum_i \\left[\\dfrac{y_i - \\hat g_\\lambda(x_i)}{1 - \\{S_\\lambda\\}_{ii}}\\right]^2$",
         "配一次就算完，對照式 5.2"],
        ["局部迴歸", "$\\min_{\\beta_0,\\beta_1} \\sum_i K_{i0}(y_i - \\beta_0 - \\beta_1 x_i)^2$", "式 7.14；演算法 7.1"],
        ["GAM（迴歸）", "$y = \\beta_0 + \\sum_j f_j(x_j) + \\varepsilon$", "式 7.15–7.16"],
        ["GAM（分類）", "$\\log\\dfrac{p(X)}{1-p(X)} = \\beta_0 + \\sum_j f_j(X_j)$", "式 7.18"]])}

{info("三個一定要記住的觀念", '''<strong>1. 多項式、階梯函數、樣條都是同一個基底函數框架的特例。</strong>
  換掉 $b_k(\\cdot)$ 就換掉方法，配適的機器（最小平方）從頭到尾沒變，
  第 3 章的推論工具全部照用。<br>
  <strong>2. 樣條把次數鎖在 3、靠加節點取得彈性；多項式只能拉高次數，代價全落在邊界。</strong>
  自然樣條再加兩端線性約束，實測把 80 歲那端的信賴帶從 65.8 砍到 37.1。<br>
  <strong>3. 「自由度」在這一章有兩種身分。</strong>
  多項式的 d 與樣條的 K + 4 是老實的參數計數；平滑樣條的 df$_\\lambda$ 是平滑矩陣的跡，
  是連續值。它們可以放在同一把尺上比較彈性，但不是同一個東西。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== beyond_linearity 本頁元件（站內序號 08 → id 與全域一律 w08 前綴）=====
   ISLP 章號是 7，但頁面命名空間用站內序號 08，兩者刻意不同。 */

/* ---------- 共用：最小平方（正規方程 + 高斯消去，含選用權重） ----------
   矩陣最大 8×8，直接解就好，不必為此引一個線性代數函式庫。
   w 給 null 就是普通最小平方。 */
function w08solve(X, y, w) {
  const n = X.length, p = X[0] ? X[0].length : 0;
  if (!p) return [];
  const A = [], b = new Array(p).fill(0);
  for (let j = 0; j < p; j++) A.push(new Array(p).fill(0));
  for (let i = 0; i < n; i++) {
    const wi = w ? w[i] : 1;
    if (!wi) continue;
    for (let j = 0; j < p; j++) {
      b[j] += wi * X[i][j] * y[i];
      for (let k = j; k < p; k++) A[j][k] += wi * X[i][j] * X[i][k];
    }
  }
  for (let j = 0; j < p; j++) for (let k = 0; k < j; k++) A[j][k] = A[k][j];
  for (let j = 0; j < p; j++) A[j][j] += 1e-9;      // 擋住奇異（例如某一段沒有樣本）
  for (let c = 0; c < p; c++) {
    let piv = c;
    for (let r = c + 1; r < p; r++) if (Math.abs(A[r][c]) > Math.abs(A[piv][c])) piv = r;
    if (piv !== c) {
      const t = A[c]; A[c] = A[piv]; A[piv] = t;
      const tb = b[c]; b[c] = b[piv]; b[piv] = tb;
    }
    if (Math.abs(A[c][c]) < 1e-12) continue;
    for (let r = c + 1; r < p; r++) {
      const f = A[r][c] / A[c][c];
      if (!f) continue;
      for (let k = c; k < p; k++) A[r][k] -= f * A[c][k];
      b[r] -= f * b[c];
    }
  }
  const out = new Array(p).fill(0);
  for (let c = p - 1; c >= 0; c--) {
    let s = b[c];
    for (let k = c + 1; k < p; k++) s -= A[c][k] * out[k];
    out[c] = Math.abs(A[c][c]) < 1e-12 ? 0 : s / A[c][c];
  }
  return out;
}
function w08dot(row, beta) {
  let s = 0;
  for (let j = 0; j < beta.length; j++) s += row[j] * beta[j];
  return s;
}
function w08fitStats(X, y, beta) {
  let rss = 0, tss = 0;
  const my = HC.stat.mean(y);
  for (let i = 0; i < y.length; i++) {
    rss += (y[i] - w08dot(X[i], beta)) ** 2;
    tss += (y[i] - my) ** 2;
  }
  return { rss, tss, r2: tss > 0 ? 1 - rss / tss : NaN };
}

/* 共用的 Wage 子樣本（90 筆）與四個 live 元件共用的座標範圍 */
const w08sub = (() => {
  const F = FRAMES_w08wage;
  const ylo = Math.floor(Math.min.apply(null, F.wage) / 20) * 20 - 10;
  const yhi = Math.ceil(Math.max.apply(null, F.wage) / 20) * 20 + 10;
  return { xs: F.age, ys: F.wage, n: F.age.length, xd: [16, 82], yd: [ylo, yhi] };
})();
const w08GRAY = 'rgba(120,116,104,.55)';

/* 把 age 壓到 [-1,1] 再取冪次：跟產生器的 tscale 同一個定義。
   不做這步的話 age^8 會讓正規方程的條件數爛掉，配出來的曲線會歪。 */
function w08ts(a) { return 2 * (a - 18) / (80 - 18) - 1; }

function w08scatter(s, g) {
  for (let i = 0; i < w08sub.n; i++) {
    s.dot(w08sub.xs[i], w08sub.ys[i], { r: 3.4, fill: w08GRAY, stroke: 'none' }, g);
  }
}

/* ---------- P01 多項式次數滑桿（baked：FRAMES_w08poly） ---------- */
let w08polySvc = null, w08polyMseSvc = null, w08polyBand = true;
function w08polySetup() {
  w08polySvc = HC.svg('w08polySvg', { xd: w08sub.xd, yd: w08sub.yd, h: 300 });
  w08polySvc.grid(6, 5, { xtitle: 'age（歲）', ytitle: 'wage（千美元）', xdec: 0, ydec: 0 });
  const F = FRAMES_w08poly;
  const all = F.trainMSE.concat(F.cvMSE);
  w08polyMseSvc = HC.svg('w08polyMse', {
    xd: [0.5, 15.5], yd: [Math.floor(Math.min.apply(null, all) / 10) * 10 - 5,
                          Math.ceil(Math.max.apply(null, all) / 10) * 10 + 5], h: 170,
    pad: { l: 52, r: 14, t: 16, b: 30 },
  });
  w08polyMseSvc.grid(7, 3, { xtitle: '多項式次數 d', ytitle: 'MSE', xdec: 0, ydec: 0 });
}
function w08polyDeg() { return parseInt($('w08polySl').value, 10); }
function w08polyDraw() {
  const F = FRAMES_w08poly, d = w08polyDeg(), key = String(d);
  const s = w08polySvc, g = s.clearLayer('main');
  if (w08polyBand) {
    s.area(F.grid.map((x, i) => [x, F.hi[key][i], F.lo[key][i]]),
           { fill: 'var(--band)' }, g);
  }
  w08scatter(s, g);
  s.poly(F.grid.map((x, i) => [x, F.fit[key][i]]), { cls: 'fit', sw: 3 }, g);
  if (w08polyBand) {
    s.poly(F.grid.map((x, i) => [x, F.hi[key][i]]), { cls: 'truef', sw: 1.6 }, g);
    s.poly(F.grid.map((x, i) => [x, F.lo[key][i]]), { cls: 'truef', sw: 1.6 }, g);
  }
  s.txtPx(58, 26, 'degree ' + d + ' 多項式（全部 3000 筆）', { cls: 'axtitle' }, g);

  /* 下面那張 MSE-vs-degree 小圖 */
  const m = w08polyMseSvc, mg = m.clearLayer('main');
  m.poly(F.degrees.map((k, i) => [k, F.trainMSE[i]]),
         { stroke: HC.tok.train, sw: 2.4, cls: 'fit' }, mg);
  m.poly(F.degrees.map((k, i) => [k, F.cvMSE[i]]),
         { stroke: HC.tok.accent, sw: 2.4, cls: 'fit' }, mg);
  const best = F.cvMSE.indexOf(Math.min.apply(null, F.cvMSE));
  m.seg(F.degrees[best], m.yd[0], F.degrees[best], m.yd[1],
        { stroke: HC.tok.accent3, sw: 1.4, dash: '5 4', cls: 'resid' }, mg);
  m.dot(d, F.trainMSE[d - 1], { r: 5, fill: HC.tok.train, stroke: '#fff', sw: 1.4 }, mg);
  m.dot(d, F.cvMSE[d - 1], { r: 5, fill: HC.tok.accent, stroke: '#fff', sw: 1.4 }, mg);
  m.txtPx(58, 12, '訓練 MSE（藍）· 10-fold CV MSE（紅）· 綠虛線 = CV 最低的 d = '
    + F.degrees[best], { cls: 'axtitle' }, mg);

  const wl = F.hi[key][0] - F.lo[key][0];
  const wr = F.hi[key][F.grid.length - 1] - F.lo[key][F.grid.length - 1];
  const mid = Math.floor(F.grid.length / 2);
  const wm = F.hi[key][mid] - F.lo[key][mid];
  $('w08polySlVal').textContent = String(d);
  $('w08polyDeg2').textContent = String(d);
  $('w08polyTrain').textContent = HC.fmt(F.trainMSE[d - 1], 1);
  $('w08polyCv').textContent = HC.fmt(F.cvMSE[d - 1], 1);
  $('w08polyWl').textContent = HC.fmt(wl, 1);
  $('w08polyWr').textContent = HC.fmt(wr, 1);
  $('w08polyWm').textContent = HC.fmt(wm, 1);
  setStatus('w08polyStatus', 'degree ' + d + '：訓練 MSE ' + HC.fmt(F.trainMSE[d - 1], 1)
    + '，10-fold CV MSE ' + HC.fmt(F.cvMSE[d - 1], 1)
    + '。80 歲那端的 95% 信賴帶寬 ' + HC.fmt(wr, 1)
    + '，中央只有 ' + HC.fmt(wm, 1) + '——'
    + (d >= 8 ? '兩端已經完全失控了。' : d >= 5 ? '邊界開始鬆了。' : '還算收斂。'));
}
function w08polySetDeg() { w08polyDraw(); }
function w08polyToggleBand() {
  w08polyBand = !w08polyBand;
  const b = $('w08polyBandBtn');
  b.textContent = '信賴帶：' + (w08polyBand ? '開' : '關');
  b.classList.toggle('off', !w08polyBand);
  w08polyDraw();
}
function w08polyReset() { $('w08polySl').value = '4'; w08polyDraw(); }

/* ---------- P02 階梯函數：可拖曳的切點（live） ---------- */
let w08stepSvc = null, w08stepCuts = [], w08stepK = 4;
function w08stepQuantileCuts(k) {
  const sorted = w08sub.xs.slice().sort((a, b) => a - b);
  const out = [];
  for (let j = 1; j < k; j++) out.push(HC.stat.quantile(sorted, j / k));
  return out;
}
function w08stepSetup() {
  w08stepSvc = HC.svg('w08stepSvg', { xd: w08sub.xd, yd: w08sub.yd, h: 330 });
  w08stepSvc.grid(6, 5, { xtitle: 'age（歲）', ytitle: 'wage（千美元）', xdec: 0, ydec: 0 });
}
function w08stepSegments() {
  const edges = [w08sub.xd[0]].concat(w08stepCuts, [w08sub.xd[1]]);
  const segs = [];
  for (let j = 0; j < edges.length - 1; j++) {
    const idx = [];
    for (let i = 0; i < w08sub.n; i++) {
      const x = w08sub.xs[i];
      if (x >= edges[j] && (j === edges.length - 2 ? x <= edges[j + 1] : x < edges[j + 1])) idx.push(i);
    }
    const ys = idx.map(i => w08sub.ys[i]);
    segs.push({ lo: edges[j], hi: edges[j + 1], n: ys.length,
                mean: ys.length ? HC.stat.mean(ys) : NaN, idx: idx });
  }
  return segs;
}
function w08stepDraw() {
  const s = w08stepSvc, g = s.clearLayer('main');
  const segs = w08stepSegments();
  let rss = 0, tss = 0;
  const my = HC.stat.mean(w08sub.ys);
  segs.forEach(sg => {
    sg.idx.forEach(i => { rss += (w08sub.ys[i] - sg.mean) ** 2; });
  });
  for (let i = 0; i < w08sub.n; i++) tss += (w08sub.ys[i] - my) ** 2;
  segs.forEach((sg, j) => {
    if (j % 2 === 0) s.box(sg.lo, s.yd[0], sg.hi, s.yd[1], { fill: 'rgba(44,62,122,.045)' }, g);
    sg.idx.forEach(i => s.dot(w08sub.xs[i], w08sub.ys[i],
      { r: 3.4, fill: j % 2 === 0 ? HC.tok.train : HC.tok.accent2, stroke: 'none', opacity: .5 }, g));
    if (!Number.isNaN(sg.mean)) {
      s.poly([[sg.lo, sg.mean], [sg.hi, sg.mean]], { cls: 'fit', sw: 3.4 }, g);
      s.txt((sg.lo + sg.hi) / 2, sg.mean, HC.fmt(sg.mean, 1), { dy: -8, cls: 'vlab' }, g);
    }
  });
  const drag = s.clearLayer('cuts');
  w08stepCuts.forEach((c, j) => {
    s.seg(c, s.yd[0], c, s.yd[1], { stroke: HC.tok.held, sw: 2, dash: '4 3', cls: 'resid' }, drag);
    const h = s.add('rect', {
      x: s.X(c) - 7, y: s.pad.t + 2, width: 14, height: 16, rx: 4,
      fill: HC.tok.held, stroke: '#fff', 'stroke-width': 1.5, cls: 'dot drag',
    }, drag);
    HC.drag(h, s, p => {
      const lo = j === 0 ? s.xd[0] + 2 : w08stepCuts[j - 1] + 2;
      const hi = j === w08stepCuts.length - 1 ? s.xd[1] - 2 : w08stepCuts[j + 1] - 2;
      w08stepCuts[j] = Math.max(lo, Math.min(hi, p.x));
      w08stepDraw();
    }, { lockY: true });
  });
  $('w08stepSeg').textContent = String(segs.length);
  $('w08stepCutTxt').textContent = w08stepCuts.map(c => HC.fmt(c, 1)).join(' · ');
  $('w08stepRss').textContent = HC.fmt(rss, 0);
  $('w08stepR2').textContent = HC.fmt(tss > 0 ? 1 - rss / tss : NaN, 4);
  $('w08stepRows').innerHTML = segs.map((sg, j) =>
    '<div>第 ' + (j + 1) + ' 段 [' + HC.fmt(sg.lo, 1) + ', ' + HC.fmt(sg.hi, 1) + ')'
    + ' · n = ' + sg.n + ' · 平均 <b>' + HC.fmt(sg.mean, 1) + '</b></div>').join('');
  setStatus('w08stepStatus', segs.length + ' 段，切點在 '
    + w08stepCuts.map(c => HC.fmt(c, 1)).join('、')
    + '。每一段的紅線就是那一段的樣本平均，段內 RSS 合計 ' + HC.fmt(rss, 0)
    + '，R² = ' + HC.fmt(tss > 0 ? 1 - rss / tss : NaN, 4) + '。');
}
function w08stepSetK() {
  w08stepK = parseInt($('w08stepSel').value, 10);
  w08stepReset();
}
function w08stepReset() {
  w08stepCuts = w08stepQuantileCuts(w08stepK);
  w08stepDraw();
}

/* ---------- P03 基底函數積木（live） ---------- */
const w08basisKnots = [33.75, 51];
const w08basisDefs = [
  { lab: '1', f: () => 1 },
  { lab: 'x', f: x => w08ts(x) },
  { lab: 'x²', f: x => Math.pow(w08ts(x), 2) },
  { lab: 'x³', f: x => Math.pow(w08ts(x), 3) },
  { lab: '(x−33.75)³₊', f: x => x > w08basisKnots[0] ? Math.pow(w08ts(x) - w08ts(w08basisKnots[0]), 3) : 0 },
  { lab: '(x−51)³₊', f: x => x > w08basisKnots[1] ? Math.pow(w08ts(x) - w08ts(w08basisKnots[1]), 3) : 0 },
  { lab: 'I(x≥33.75)', f: x => x >= w08basisKnots[0] ? 1 : 0 },
  { lab: 'I(x≥51)', f: x => x >= w08basisKnots[1] ? 1 : 0 },
];
const w08basisPal = ['#2c3e7a', '#c0392b', '#1a6b4a', '#8e44ad',
                     '#d68910', '#16a085', '#7f8c8d', '#b03a5b'];
let w08basisSel = [true, true, true, true, false, false, false, false];
let w08basisFnSvc = null, w08basisFitSvc = null;
function w08basisSetup() {
  w08basisFnSvc = HC.svg('w08basisFn', { xd: w08sub.xd, yd: [-1.25, 1.25], h: 200,
                                         pad: { l: 46, r: 14, t: 26, b: 28 } });
  w08basisFnSvc.grid(6, 2, { xtitle: 'age（歲）', ytitle: '形狀（各自正規化）', xdec: 0, ydec: 0 });
  w08basisFitSvc = HC.svg('w08basisFit', { xd: w08sub.xd, yd: w08sub.yd, h: 280 });
  w08basisFitSvc.grid(6, 5, { xtitle: 'age（歲）', ytitle: 'wage（千美元）', xdec: 0, ydec: 0 });
}
function w08basisCols() {
  const out = [];
  for (let j = 0; j < w08basisDefs.length; j++) if (w08basisSel[j]) out.push(j);
  return out;
}
function w08basisDraw() {
  const cols = w08basisCols();
  const grid = HC.stat.seq(w08sub.xd[0] + 1, w08sub.xd[1] - 1, 140);

  /* 上圖：每個被選中的基底函數的形狀 */
  const fs = w08basisFnSvc, fg = fs.clearLayer('main');
  cols.forEach((j, slot) => {
    const raw = grid.map(x => w08basisDefs[j].f(x));
    let m = 0;
    raw.forEach(v => { m = Math.max(m, Math.abs(v)); });
    if (m === 0) m = 1;
    fs.poly(grid.map((x, i) => [x, raw[i] / m]),
            { stroke: w08basisPal[j], sw: 2.2, cls: 'fit' }, fg);
    fs.txtPx(52 + (slot % 4) * 128, 14 + Math.floor(slot / 4) * 12,
             w08basisDefs[j].lab, { cls: 'axlab', fill: w08basisPal[j] }, fg);
  });
  if (!cols.length) fs.txtPx(52, 14, '（一個基底都沒選）', { cls: 'axlab' }, fg);

  /* 下圖：資料 + 線性組合出來的曲線 */
  const X = [];
  for (let i = 0; i < w08sub.n; i++) X.push(cols.map(j => w08basisDefs[j].f(w08sub.xs[i])));
  const beta = cols.length ? w08solve(X, w08sub.ys, null) : [];
  const st = cols.length ? w08fitStats(X, w08sub.ys, beta)
                         : { rss: w08sub.ys.reduce((s, v) => s + v * v, 0), r2: NaN };
  const ps = w08basisFitSvc, pg = ps.clearLayer('main');
  w08scatter(ps, pg);
  if (cols.length) {
    /* 有指示函數在裡面時曲線會跳，所以在節點處把折線切開 */
    const hasStep = cols.some(j => j >= 6);
    let seg = [];
    grid.forEach(x => {
      const yv = w08dot(cols.map(j => w08basisDefs[j].f(x)), beta);
      if (hasStep && seg.length
          && w08basisKnots.some(k => seg[seg.length - 1][0] < k && x >= k)) {
        ps.poly(seg, { cls: 'fit', sw: 3 }, pg);
        seg = [];
      }
      seg.push([x, yv]);
    });
    if (seg.length > 1) ps.poly(seg, { cls: 'fit', sw: 3 }, pg);
  } else {
    ps.poly([[w08sub.xd[0], 0], [w08sub.xd[1], 0]], { cls: 'fit', sw: 3 }, pg);
  }
  w08basisKnots.forEach(k => ps.seg(k, ps.yd[0], k, ps.yd[1],
    { stroke: HC.tok.held, sw: 1.4, dash: '4 3', cls: 'resid' }, pg));

  for (let j = 0; j < w08basisDefs.length; j++) {
    const b = $('w08basisB' + j);
    if (b) b.classList.toggle('off', !w08basisSel[j]);
  }
  $('w08basisK').textContent = String(cols.length);
  $('w08basisP').textContent = String(cols.length);
  $('w08basisRss').textContent = HC.fmt(st.rss, 0);
  $('w08basisR2').textContent = HC.fmt(st.r2, 4);
  setStatus('w08basisStatus', cols.length
    ? '選了 ' + cols.length + ' 個基底：' + cols.map(j => w08basisDefs[j].lab).join('、')
      + '。配出來的 RSS = ' + HC.fmt(st.rss, 0) + '，R² = ' + HC.fmt(st.r2, 4) + '。'
    : '一個基底都沒選——連截距都沒有，所以配適值恆為 0，紅線壓在座標軸底部。勾一個「1」看看。');
}
function w08basisToggle(j) { w08basisSel[j] = !w08basisSel[j]; w08basisDraw(); }
function w08basisPreset(kind) {
  if (kind === 'poly') w08basisSel = [true, true, true, true, false, false, false, false];
  else if (kind === 'spline') w08basisSel = [true, true, true, true, true, true, false, false];
  else w08basisSel = [true, false, false, false, false, false, true, true];
  w08basisDraw();
}

/* ---------- P04 節點與連續性層級（live） ---------- */
/* 完整 8 個基底：1, x, x², x³, I(x>ξ), (x−ξ)₊, (x−ξ)²₊, (x−ξ)³₊
   約束層級 L 拿掉前 L 個截斷項 → 參數個數 8, 7, 6, 5 */
const w08knotLabels = ['不連續', '連續', '一階導數連續', '二階導數連續（＝立方樣條）'];
let w08knotSvc = null, w08knotXi = 50, w08knotLevel = 3;
function w08knotSetup() {
  w08knotSvc = HC.svg('w08knotSvg', { xd: w08sub.xd, yd: w08sub.yd, h: 340 });
  w08knotSvc.grid(6, 5, { xtitle: 'age（歲）', ytitle: 'wage（千美元）', xdec: 0, ydec: 0 });
}
function w08knotRow(x) {
  const t = w08ts(x), k = w08ts(w08knotXi), d = t - k, on = x > w08knotXi ? 1 : 0;
  const full = [1, t, t * t, t * t * t, on, on * d, on * d * d, on * d * d * d];
  return full.slice(0, 4).concat(full.slice(4 + w08knotLevel));
}
function w08knotDraw() {
  const s = w08knotSvc, g = s.clearLayer('main');
  const X = [];
  for (let i = 0; i < w08sub.n; i++) X.push(w08knotRow(w08sub.xs[i]));
  const beta = w08solve(X, w08sub.ys, null);
  const st = w08fitStats(X, w08sub.ys, beta);
  w08scatter(s, g);
  /* 左右兩段分開畫，否則不連續的層級會被一條垂直線接起來 */
  const left = HC.stat.seq(s.xd[0] + 1, w08knotXi - 0.02, 90).filter(x => x <= w08knotXi);
  const right = HC.stat.seq(w08knotXi + 0.02, s.xd[1] - 1, 90);
  [left, right].forEach(part => {
    if (part.length > 1) {
      s.poly(part.map(x => [x, w08dot(w08knotRow(x), beta)]), { cls: 'fit', sw: 3 }, g);
    }
  });
  const drag = s.clearLayer('knot');
  s.seg(w08knotXi, s.yd[0], w08knotXi, s.yd[1],
        { stroke: HC.tok.held, sw: 2, dash: '5 4', cls: 'resid' }, drag);
  const h = s.add('rect', {
    x: s.X(w08knotXi) - 8, y: s.pad.t + 2, width: 16, height: 18, rx: 4,
    fill: HC.tok.held, stroke: '#fff', 'stroke-width': 1.5, cls: 'dot drag',
  }, drag);
  HC.drag(h, s, p => {
    w08knotXi = Math.max(26, Math.min(72, p.x));
    w08knotDraw();
  }, { lockY: true });
  s.txtPx(52, 26, '節點 ξ = ' + HC.fmt(w08knotXi, 1) + ' · ' + w08knotLabels[w08knotLevel]
    + ' · 參數 ' + (8 - w08knotLevel) + ' 個', { cls: 'axtitle' }, drag);

  $('w08knotXiTxt').textContent = HC.fmt(w08knotXi, 1);
  $('w08knotLvlTxt').textContent = w08knotLabels[w08knotLevel];
  $('w08knotP').textContent = String(8 - w08knotLevel);
  $('w08knotRss').textContent = HC.fmt(st.rss, 0);
  $('w08knotR2').textContent = HC.fmt(st.r2, 4);
  const tail = ['曲線在節點上直接斷開——這就是 ISLP 圖 7.3 左上那個「看起來很荒謬」的配適。',
                '接上了，但接點是個折角（斜率跳），圖 7.3 右上的 V 字。',
                '斜率也接上了，折角消失；但曲率還會跳，仔細看節點附近會彈一下。',
                '值、斜率、曲率全部連續——這就是立方樣條，看起來完全平滑。'][w08knotLevel];
  setStatus('w08knotStatus', '節點 ξ = ' + HC.fmt(w08knotXi, 1) + '，'
    + w08knotLabels[w08knotLevel] + '，用掉 ' + (8 - w08knotLevel) + ' 個參數，RSS = '
    + HC.fmt(st.rss, 0) + '。' + tail);
}
function w08knotSet(lv) { w08knotLevel = lv; w08knotDraw(); }
function w08knotReset() {
  w08knotXi = 50; w08knotLevel = 3;
  const r = $('w08knotLv3'); if (r) r.checked = true;
  w08knotDraw();
}

/* ---------- P05 自然樣條 vs 立方樣條（baked：FRAMES_w08nat） ---------- */
let w08natBands = true, w08natCubic = true;
function w08natDraw() {
  const F = FRAMES_w08nat;
  const pts = (arr) => F.grid.map((x, i) => ({ x: x, y: arr[i] }));
  const ds = [];
  ds.push({ label: 'Wage 子樣本', data: FRAMES_w08wage.age.map((a, i) =>
              ({ x: a, y: FRAMES_w08wage.wage[i] })),
            backgroundColor: w08GRAY, borderColor: w08GRAY, pointRadius: 2.6,
            showLine: false, order: 9 });
  if (w08natCubic) {
    if (w08natBands) {
      ds.push({ label: '_立方帶上', data: pts(F.cubic.hi), borderColor: 'rgba(192,57,43,.35)',
                borderWidth: 1, pointRadius: 0, fill: false });
      ds.push({ label: '_立方帶下', data: pts(F.cubic.lo), borderColor: 'rgba(192,57,43,.35)',
                borderWidth: 1, pointRadius: 0, fill: '-1',
                backgroundColor: 'rgba(192,57,43,.13)' });
    }
    ds.push({ label: '立方樣條（7 參數）', data: pts(F.cubic.fit), borderColor: HC.tok.accent,
              borderWidth: 2.8, pointRadius: 0, fill: false });
  }
  if (w08natBands) {
    ds.push({ label: '_自然帶上', data: pts(F.natural.hi), borderColor: 'rgba(26,107,74,.35)',
              borderWidth: 1, pointRadius: 0, fill: false });
    ds.push({ label: '_自然帶下', data: pts(F.natural.lo), borderColor: 'rgba(26,107,74,.35)',
              borderWidth: 1, pointRadius: 0, fill: '-1',
              backgroundColor: 'rgba(26,107,74,.15)' });
  }
  ds.push({ label: '自然樣條（5 參數）', data: pts(F.natural.fit), borderColor: HC.tok.accent3,
            borderWidth: 2.8, pointRadius: 0, fill: false });
  HC.line('w08natChart', { datasets: ds }, {
    parsing: false,
    plugins: {
      legend: { labels: { filter: it => !String(it.text).startsWith('_') } },
      tooltip: { filter: it => !String(it.dataset.label).startsWith('_') },
    },
    scales: {
      x: { type: 'linear', min: 16, max: 82,
           title: { display: true, text: 'age（歲）· 虛線是節點 25／40／60' } },
      y: { title: { display: true, text: 'wage（千美元）' } },
    },
  });
  const c = HC.get('w08natChart');
  HC.refs(c, F.knots.map(k => HC.vline(k, 'ξ = ' + k, 'rgba(243,156,18,.85)')));
  $('w08natDfC').textContent = String(F.cubic.df);
  $('w08natDfN').textContent = String(F.natural.df);
  $('w08natWl').textContent = HC.fmt(F.widthCubic[0], 1) + ' / ' + HC.fmt(F.widthNatural[0], 1);
  $('w08natWr').textContent = HC.fmt(F.widthCubic[1], 1) + ' / ' + HC.fmt(F.widthNatural[1], 1);
  $('w08natKnots').textContent = F.knots.join(' · ');
  setStatus('w08natStatus', '兩者都用內部節點 25／40／60。80 歲那端的 95% 信賴帶寬：立方樣條 '
    + HC.fmt(F.widthCubic[1], 1) + '、自然樣條 ' + HC.fmt(F.widthNatural[1], 1)
    + '——線性約束把邊界的變異砍掉了一半。中段兩條幾乎重疊。');
}
function w08natToggleBands() {
  w08natBands = !w08natBands;
  const b = $('w08natBandBtn');
  b.textContent = '信賴帶：' + (w08natBands ? '開' : '關');
  b.classList.toggle('off', !w08natBands);
  w08natDraw();
}
function w08natToggleCubic() {
  w08natCubic = !w08natCubic;
  const b = $('w08natCubBtn');
  b.textContent = '立方樣條：' + (w08natCubic ? '開' : '關');
  b.classList.toggle('off', !w08natCubic);
  w08natDraw();
}

/* ---------- P06 平滑樣條的有效自由度（baked：FRAMES_w08lam） ---------- */
let w08lamShowPick = true;
function w08lamDraw() {
  const F = FRAMES_w08lam;
  const i = parseInt($('w08lamSl').value, 10);
  const df = F.dfs[i], key = String(df);
  const ds = [{ label: 'Wage 子樣本',
                data: FRAMES_w08wage.age.map((a, k) => ({ x: a, y: FRAMES_w08wage.wage[k] })),
                backgroundColor: w08GRAY, borderColor: w08GRAY, pointRadius: 2.6,
                showLine: false, order: 9 }];
  if (w08lamShowPick) {
    ds.push({ label: 'GCV 選出的 df = ' + F.pick.df,
              data: F.grid.map((x, k) => ({ x: x, y: F.pick.curve[k] })),
              borderColor: HC.tok.accent3, borderWidth: 2, borderDash: [6, 4],
              pointRadius: 0, fill: false });
  }
  ds.push({ label: 'df = ' + df, data: F.grid.map((x, k) => ({ x: x, y: F.curves[key][k] })),
            borderColor: HC.tok.accent, borderWidth: 3, pointRadius: 0, fill: false });
  HC.line('w08lamChart', { datasets: ds }, {
    parsing: false,
    scales: {
      x: { type: 'linear', min: 16, max: 82, title: { display: true, text: 'age（歲）' } },
      y: { title: { display: true, text: 'wage（千美元）' } },
    },
  });
  $('w08lamSlVal').textContent = HC.fmt(df, 1);
  $('w08lamDf').textContent = HC.fmt(df, 1);
  $('w08lamLam').textContent = String(F.lams[key]);
  $('w08lamGcv').textContent = HC.fmt(F.gcv[key], 2);
  $('w08lamR2').textContent = HC.fmt(F.r2[key], 4);
  const best = F.dfs[Object.keys(F.gcv).map(k => F.gcv[k])
    .indexOf(Math.min.apply(null, Object.keys(F.gcv).map(k => F.gcv[k])))];
  setStatus('w08lamStatus', 'df = ' + HC.fmt(df, 1) + ' 對應 λ = ' + F.lams[key]
    + '，GCV = ' + HC.fmt(F.gcv[key], 2) + '。'
    + (df <= 2.5 ? 'df = 2 就是那條最小平方直線——λ 大到把所有彎曲都罰掉了。'
       : df >= 15 ? '抖得離譜：λ 幾乎歸零，曲線開始追雜訊。'
       : '這個刻度上 GCV 最低的是 df = ' + HC.fmt(best, 1)
         + '，gridsearch 連續搜出來的是 ' + F.pick.df + '。'));
}
function w08lamSet() { w08lamDraw(); }
function w08lamTogglePick() {
  w08lamShowPick = !w08lamShowPick;
  const b = $('w08lamPickBtn');
  b.textContent = 'GCV 選出的曲線：' + (w08lamShowPick ? '開' : '關');
  b.classList.toggle('off', !w08lamShowPick);
  w08lamDraw();
}
function w08lamReset() { $('w08lamSl').value = '3'; w08lamDraw(); }

/* ---------- P07 局部迴歸的 span 掃描器（live） ---------- */
let w08loessSvc = null, w08loessPlayer = null;
function w08loessSpan() { return parseInt($('w08loessSl').value, 10) / 100; }
function w08loessX0() { return parseFloat($('w08loessXSl').value); }
function w08loessSetup() {
  w08loessSvc = HC.svg('w08loessSvg', { xd: w08sub.xd, yd: w08sub.yd, h: 340 });
  w08loessSvc.grid(6, 5, { xtitle: 'age（歲）', ytitle: 'wage（千美元）', xdec: 0, ydec: 0 });
}
/* tricube 權重 + 加權最小平方，就是 ISLP 演算法 7.1 的第 2、3 步 */
function w08loessAt(x0, span) {
  const k = Math.max(3, Math.round(span * w08sub.n));
  const d = [];
  for (let i = 0; i < w08sub.n; i++) d.push({ i: i, d: Math.abs(w08sub.xs[i] - x0) });
  d.sort((a, b) => a.d - b.d);
  const near = d.slice(0, k), dmax = near[near.length - 1].d || 1;
  const X = [], y = [], w = [], idx = [];
  near.forEach(o => {
    const u = Math.min(1, o.d / dmax);
    const wt = Math.pow(1 - u * u * u, 3);
    X.push([1, w08sub.xs[o.i] - x0]); y.push(w08sub.ys[o.i]); w.push(wt); idx.push(o.i);
  });
  const beta = w08solve(X, y, w);
  return { k: k, dmax: dmax, idx: idx, wts: w, b0: beta[0], b1: beta[1], fit: beta[0] };
}
function w08loessFrames() {
  const span = w08loessSpan();
  const grid = HC.stat.seq(w08sub.xd[0] + 3, w08sub.xd[1] - 3, 34);
  const acc = [];
  return grid.map((x0, j) => {
    const r = w08loessAt(x0, span);
    acc.push([x0, r.fit]);
    return { j: j, x0: x0, span: span, r: r, path: acc.slice() };
  });
}
function w08loessFull(span) {
  return HC.stat.seq(w08sub.xd[0] + 3, w08sub.xd[1] - 3, 34)
    .map(x0 => [x0, w08loessAt(x0, span).fit]);
}
function w08loessApply(f) {
  const s = w08loessSvc, g = s.clearLayer('main');
  const span = f.span, r = f.r;
  s.box(f.x0 - r.dmax, s.yd[0], f.x0 + r.dmax, s.yd[1],
        { fill: 'rgba(243,156,18,.10)' }, g);
  const inN = {};
  r.idx.forEach(i => { inN[i] = true; });
  for (let i = 0; i < w08sub.n; i++) {
    s.dot(w08sub.xs[i], w08sub.ys[i],
          { r: inN[i] ? 4.4 : 3, fill: inN[i] ? HC.tok.held : w08GRAY, stroke: 'none' }, g);
  }
  /* tricube 權重的鐘形：畫在圖的下緣 */
  const bell = [];
  for (let t = -1; t <= 1.0001; t += 0.05) {
    const u = Math.abs(t), wt = Math.pow(1 - u * u * u, 3);
    bell.push([f.x0 + t * r.dmax, s.yd[0] + 6 + wt * (s.yd[1] - s.yd[0]) * 0.16]);
  }
  s.poly(bell, { stroke: '#d4ac0d', sw: 2, cls: 'fit' }, g);
  s.seg(f.x0, s.yd[0], f.x0, s.yd[1], { stroke: HC.tok.held, sw: 2, dash: '5 4', cls: 'resid' }, g);
  /* 淡紅：這個 span 的完整曲線 */
  s.poly(w08loessFull(span), { stroke: 'rgba(192,57,43,.30)', sw: 1.8, cls: 'fit' }, g);
  /* 局部加權直線（只畫鄰域那一段） */
  const x1 = f.x0 - r.dmax, x2 = f.x0 + r.dmax;
  s.poly([[x1, r.b0 + r.b1 * (x1 - f.x0)], [x2, r.b0 + r.b1 * (x2 - f.x0)]],
         { stroke: '#d68910', sw: 2.6, cls: 'fit' }, g);
  if (f.path.length > 1) s.poly(f.path, { cls: 'fit', sw: 3.4 }, g);
  s.dot(f.x0, r.fit, { r: 6, fill: HC.tok.accent, stroke: '#fff', sw: 1.6 }, g);
  s.txtPx(52, 26, 'span = ' + HC.fmt(span, 2) + ' → 鄰域 k = ' + r.k + ' / ' + w08sub.n
    + ' 點', { cls: 'axtitle' }, g);
  hlLine('w08loessCode', 4);
  $('w08loessSpanTxt').textContent = HC.fmt(span, 2);
  $('w08loessK').textContent = r.k + ' / ' + w08sub.n;
  $('w08loessX0').textContent = HC.fmt(f.x0, 1);
  $('w08loessXSl').value = String(Math.round(f.x0));
  $('w08loessXSlVal').textContent = HC.fmt(f.x0, 1);
  $('w08loessB1').textContent = HC.fmt(r.b1, 3);
  $('w08loessFhat').textContent = HC.fmt(r.fit, 1);
  setStatus('w08loessStatus', 'x₀ = ' + HC.fmt(f.x0, 1) + '：取最近的 ' + r.k
    + ' 點（橘色），用 tricube 權重（黃色鐘形）配一條加權直線（橘線段），'
    + '斜率 ' + HC.fmt(r.b1, 3) + '，它在 x₀ 的值 ' + HC.fmt(r.fit, 1)
    + ' 就是 f̂(x₀)。已經掃完 ' + f.path.length + ' / 34 個目標點。');
}
function w08loessStart() {
  w08loessPlayer = new Player({ frames: w08loessFrames(), apply: w08loessApply });
  w08loessPlayer.reset();
  w08loessPlayer.play();
}
function w08loessShowX0() {
  if (w08loessPlayer) w08loessPlayer.stop();
  const x0 = w08loessX0(), span = w08loessSpan(), r = w08loessAt(x0, span);
  w08loessApply({ j: 0, x0: x0, span: span, r: r, path: [] });
  $('w08loessXSlVal').textContent = HC.fmt(x0, 0);
}
function w08loessReset() {
  if (w08loessPlayer) w08loessPlayer.stop();
  $('w08loessSl').value = '30';
  $('w08loessXSl').value = '49';
  $('w08loessSlVal').textContent = '0.30';
  $('w08loessXSlVal').textContent = '49';
  w08loessShowX0();
  hlLine('w08loessCode', 1);
  setStatus('w08loessStatus', 'span = 0.30、x₀ = 49。直接拖任一滑桿比較鄰域與局部斜率；'
    + '「自動掃描」只是一個可選的總覽。');
}
function w08loessSetSpan() {
  $('w08loessSlVal').textContent = HC.fmt(w08loessSpan(), 2);
  w08loessShowX0();
}
function w08loessSetX0() { w08loessShowX0(); }

/* ---------- P08 GAM 三面板（baked：FRAMES_w08gam） ---------- */
function w08gamPanel(cid, xs, cur, xtitle, dash) {
  const pts = arr => xs.map((x, i) => ({ x: x, y: arr[i] }));
  HC.line(cid, {
    datasets: [
      { label: '上界', data: pts(cur.hi), borderColor: 'rgba(192,57,43,.55)',
        borderWidth: 1.4, borderDash: [5, 4], pointRadius: 0, fill: false },
      { label: '下界', data: pts(cur.lo), borderColor: 'rgba(192,57,43,.55)',
        borderWidth: 1.4, borderDash: [5, 4], pointRadius: 0, fill: '-1',
        backgroundColor: 'rgba(44,62,122,.10)' },
      { label: 'f̂', data: pts(cur.fit), borderColor: HC.tok.accent2,
        borderWidth: 2.8, pointRadius: 0, fill: false, borderDash: dash || [] },
    ],
  }, {
    plugins: { legend: { display: false } },
    scales: {
      x: { type: 'linear', title: { display: true, text: xtitle } },
      y: { min: -60, max: 60, title: { display: true, text: '對 wage 的效果' } },
    },
  });
}
function w08gamDraw() {
  const F = FRAMES_w08gam;
  const ai = parseInt($('w08gamAgeSl').value, 10), yi = parseInt($('w08gamYearSl').value, 10);
  const adf = F.ageDfs[ai], ydf = F.yearDfs[yi];
  w08gamPanel('w08gamYear', F.yearGrid, F.yearCurves[String(ydf)], 'year');
  w08gamPanel('w08gamAge', F.ageGrid, F.ageCurves[String(adf)], 'age（歲）');
  /* education 是類別項：畫成階梯（每個層級一個常數） */
  const step = [], stepLo = [], stepHi = [];
  F.eduLabels.forEach((_, k) => {
    step.push({ x: k + 0.5, y: F.edu.fit[k] }, { x: k + 1.5, y: F.edu.fit[k] });
    stepLo.push({ x: k + 0.5, y: F.edu.lo[k] }, { x: k + 1.5, y: F.edu.lo[k] });
    stepHi.push({ x: k + 0.5, y: F.edu.hi[k] }, { x: k + 1.5, y: F.edu.hi[k] });
  });
  HC.line('w08gamEdu', {
    datasets: [
      { label: '上界', data: stepHi, borderColor: 'rgba(192,57,43,.55)', borderWidth: 1.4,
        borderDash: [5, 4], pointRadius: 0, fill: false, stepped: true },
      { label: '下界', data: stepLo, borderColor: 'rgba(192,57,43,.55)', borderWidth: 1.4,
        borderDash: [5, 4], pointRadius: 0, fill: '-1', stepped: true,
        backgroundColor: 'rgba(44,62,122,.10)' },
      { label: 'f̂', data: step, borderColor: HC.tok.accent2, borderWidth: 2.8,
        pointRadius: 0, fill: false, stepped: true },
    ],
  }, {
    plugins: { legend: { display: false } },
    scales: {
      x: { type: 'linear', min: 0.5, max: 5.5,
           ticks: { stepSize: 1, callback: v => ['', '<HS', 'HS', '<Coll', 'Coll', '>Coll'][v] || '' },
           title: { display: true, text: 'education（固定 5 個層級）' } },
      y: { min: -60, max: 60, title: { display: true, text: '對 wage 的效果' } },
    },
  });
  const cell = F.grid[adf + '|' + ydf] || {};
  $('w08gamAgeSlVal').textContent = HC.fmt(adf, 1);
  $('w08gamYearSlVal').textContent = HC.fmt(ydf, 1);
  $('w08gamAgeDf').textContent = HC.fmt(adf, 1);
  $('w08gamYearDf').textContent = HC.fmt(ydf, 1);
  $('w08gamEdof').textContent = HC.fmt(cell.edof, 2);
  $('w08gamDev').textContent = cell.dev != null ? Number(cell.dev).toLocaleString('en-US') : '—';
  $('w08gamR2').textContent = HC.fmt(cell.r2, 4);
  $('w08gamGcv').textContent = HC.fmt(cell.gcv, 1);
  const isRef = adf === F.refAgeDf && ydf === F.refYearDf;
  setStatus('w08gamStatus', 'age df = ' + HC.fmt(adf, 1) + '、year df = ' + HC.fmt(ydf, 1)
    + ' → 總有效自由度 ' + HC.fmt(cell.edof, 2) + '、Pseudo R² ' + HC.fmt(cell.r2, 4)
    + '、GCV ' + HC.fmt(cell.gcv, 1) + '。'
    + (isRef ? '這就是 lab 儲存格 86／98 的那一組：EDoF 12.99、GCV 1246.1、R² 0.2928。'
             : 'year 的 df 幾乎不影響 R²，age 的 df 才有感——這一頁 P08 的 ANOVA 說的就是這件事。'));
}
function w08gamSet() { w08gamDraw(); }
function w08gamReset() {
  $('w08gamAgeSl').value = '3'; $('w08gamYearSl').value = '3';
  w08gamDraw();
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.line / HC.bar 在 Chart 未載入時本來就安全地回傳 null。 */
w08polySetup();
w08polyDraw();
w08stepSetup();
w08stepReset();
w08basisSetup();
w08basisDraw();
w08knotSetup();
w08knotDraw();
w08loessSetup();
w08loessReset();
HC.ready(() => {
  w08natDraw();
  w08lamDraw();
  w08gamDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("beyond_linearity", BODIES, PAGEJS, frames())
