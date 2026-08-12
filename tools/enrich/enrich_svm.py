#!/usr/bin/env python3
"""support_vector_machines.html（ISLP 第 9 章）完整自學充實。冪等。

內容依據：講義 09_Support_Vector_Machines.pdf（40 頁）、Ch09-svm-lab-zh.ipynb、
ISLP 第 9 章（書上 p.368–398）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_svm.py 重播 lab 的隨機數序列後產生，所以頁面上
每一個支持向量個數、每一組係數都能對回 lab 的某一格。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 9
LAB = "Ch09-svm-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def slider(sid, label, lo, hi, step, val, fn, vid, vtext, basis="1 1 200px", vw=54, lw=34):
    """.controls-bar 裡的滑桿。

    三個滑桿並排時，base.css 給的 min-width（.slider-label 60px、.slider-val 60px）
    加上 <input type="range"> 的內建最小寬度會超過一列的空間，.slider-val 於是被推出
    .slider-row 外面、藏到下一個滑桿的背景底下（第一次跑 browser_check 的截圖抓到的）。
    所以這裡用 inline style 覆蓋這三個 min-width，讓它們真的縮得下去。
    """
    return (f'<div class="slider-row" style="flex:{basis};margin-bottom:0;min-width:0;">'
            f'<span class="slider-label" style="min-width:{lw}px;">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}" onchange="{fn}" style="min-width:0;flex:1 1 0;">'
            f'<span class="slider-val" id="{vid}" style="min-width:{vw}px;">{vtext}</span></div>')


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_svm.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_svm.py 失敗：\n" + r.stderr[-2000:])
    return "/* ===== 烘焙資料（tools/frames/gen_svm.py，重播 lab 的抽樣順序）===== */\n" \
        + r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>前面幾章的分類器都先繞一圈：邏輯斯迴歸去估 $\\Pr(Y \\mid X)$，LDA 去估
  $\\Pr(X \\mid Y)$ 再用貝氏定理翻回來，樹去切區塊。這一章換一條路——
  <strong>直接在特徵空間裡找一片把兩類分開的平面</strong>。不估機率、不假設分佈，
  就是幾何。</p>

  <p>講義第 3 頁把整章的劇本寫得很乾淨：先試著找一片<strong>分得開</strong>的平面；
  如果找不到，往兩個方向想辦法。<strong>把「分開」的定義放鬆</strong>（軟邊界），
  以及<strong>把特徵空間變大</strong>（核）。這兩招合起來就是支持向量機。</p>

{info("三層結構，一層一層加東西", '''<strong>1. 最大邊界分類器（maximal margin classifier）：</strong>
  資料完全分得開時，選離兩邊都最遠的那一刀。<br>
  <strong>2. 支持向量分類器（support vector classifier）：</strong>允許少數點犯規，
  用一個調整參數決定容忍度。也叫軟邊界分類器。<br>
  <strong>3. 支持向量機（support vector machine, SVM）：</strong>把內積換成核，
  邊界就彎起來了。<br>
  三者不是三種方法，是<strong>同一個方法的三個層次</strong>——最外面那層用線性核時
  會原地退回最裡面那層。''')}

  <p>起點是<strong>超平面</strong>（hyperplane）。p 維空間裡的超平面是一個 p − 1 維的
  平坦仿射子空間；p = 2 就是一條線，p = 3 就是一個平面。它的方程式簡單到有點反高潮：</p>

  $$\\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\cdots + \\beta_p X_p = 0$$

  <p>寫成 $f(X) = \\beta_0 + \\beta^{{\\top}} X$。滿足 $f(X) = 0$ 的點在超平面上，
  $f(X) > 0$ 的點在一側、$f(X) < 0$ 的點在另一側。所以<strong>只要看 $f(X)$ 的正負號，
  就知道一個點站在哪一邊</strong>——分類問題被壓成一次算術。</p>

  <p>而且 $f(X)$ 的<strong>大小</strong>也有意思。向量 $\\beta = (\\beta_1,\\dots,\\beta_p)$
  是超平面的<strong>法向量</strong>（normal vector），指向與超平面垂直的方向；
  點 $x$ 到超平面的垂直距離正好是</p>

  $$\\text{{距離}} = \\frac{{|f(x)|}}{{\\lVert \\beta \\rVert}},
    \\qquad \\lVert \\beta \\rVert = \\sqrt{{\\beta_1^2 + \\cdots + \\beta_p^2}}$$

  <p>所以 $|f(x)|$ 大就是離邊界遠、這個判斷有把握；$|f(x)|$ 接近 0 就是貼在邊界上、
  隨時可能翻盤。這個「離邊界多遠 ＝ 多有把握」的直覺，是整章的地基。</p>

{viz(svg("w10hyperSvg", 330),
     [info_card("怎麼玩",
                '三個滑桿分別調 β₀、β₁、β₂。<strong>藍色區域是 f(x) &gt; 0、'
                '紅色區域是 f(x) &lt; 0</strong>，中間那條紅線就是超平面。'
                '綠色短箭頭是法向量 β 的方向。注意它永遠垂直於線。'
                '預設值 1、2、3 就是 ISLP 圖 9.1 畫的那條 1 + 2X₁ + 3X₂ = 0。', "圖 9.1"),
      rows_card("目前的超平面",
                [("方程式", "—", "w10hyperEq"), ("‖β‖", "—", "w10hyperNorm"),
                 ("A 點：f(x) ｜ 距離", "—", "w10hyperPA"),
                 ("B 點：f(x) ｜ 距離", "—", "w10hyperPB"),
                 ("C 點：f(x) ｜ 距離", "—", "w10hyperPC")]),
      info_card("兩個容易忽略的細節",
                '<strong>① 係數整組縮放不改變超平面。</strong>三個滑桿同時乘 3，'
                '線不動、f(x) 卻變三倍。<br>'
                '<strong>② β₁ 與 β₂ 同時是 0 就沒有超平面。</strong>'
                '把那兩個滑桿都推到 0 看看。')],
     "w10hyperStatus", "拖三個滑桿看超平面怎麼動，以及三個測試點的 f(x) 怎麼變。",
     slider("w10hyperB0", "β₀", -3, 3, 0.1, 1, "w10hyperDraw()", "w10hyperB0V", "1.0",
            basis="1 1 170px", vw=40, lw=26)
     + slider("w10hyperB1", "β₁", -3, 3, 0.1, 2, "w10hyperDraw()", "w10hyperB1V", "2.0",
              basis="1 1 170px", vw=40, lw=26)
     + slider("w10hyperB2", "β₂", -3, 3, 0.1, 3, "w10hyperDraw()", "w10hyperB2V", "3.0",
              basis="1 1 170px", vw=40, lw=26)
     + '<button class="btn btn-reset" onclick="w10hyperReset()">重置</button>')}

  <p>有了超平面，分類規則就寫完了：把 $y_i$ 編碼成 $\\pm 1$，
  <strong>分離超平面</strong>（separating hyperplane）就是滿足</p>

  $$y_i\\left(\\beta_0 + \\beta_1 x_{{i1}} + \\cdots + \\beta_p x_{{ip}}\\right) > 0
    \\qquad \\text{{對每一筆 }} i = 1, \\dots, n$$

  <p>的那些超平面（ISLP 式 9.8）。這一個式子把「藍色的要 $f > 0$、紫色的要 $f < 0$」
  兩條規則合成一條，因為 $y_i$ 自己會把符號翻過來。這個 $y_i f(x_i)$ 之後會一直出現，
  它就是<strong>「這一筆分對了嗎、有多篤定」</strong>的度量。</p>

  <h3 id="dx-fit">講義完整實作：造資料、配一個線性 SVC、取出係數</h3>
{card("lab 09 · SVC(kernel='linear') 的第一次配適",
      lab_code(CH, 14) + "\n\n" + lab_code(CH, 16) + "\n\n" + lab_code(CH, 29),
      lab_output(CH, 29), src=src("14、16、29"),
      out_tag="預期輸出（儲存格 29）",
      note="這 50 筆資料是本章前半的主角，本頁所有烘焙圖都是<strong>重播同一組"
           "<code>default_rng(1)</code> 抽樣</strong>算出來的。"
           "<code>coef_</code> 就是 (β₁, β₂) = (1.173, 0.773)，"
           "<code>intercept_</code> 是 β₀。配適那一格的輸出只是 "
           "<code>SVC(C=10, kernel='linear')</code>——sklearn 印的是估計器本身，不是結果。")}

{quiz("qHyp", "QUIZ · 超平面",
      "把某個超平面的係數 (β₀, β₁, β₂) 全部乘上 −2，會發生什麼事？",
      [(True, "超平面本身完全不動，但每個點的 f(x) 變成 −2 倍，正負兩側因此互換",
        "對。係數整體縮放不改變 f(x) = 0 這個集合，所以線不動；乘上負數則把兩側的符號調換。"
        "這就是為什麼式 9.10 要加上 Σβⱼ² = 1——不加限制，「距離」這個詞沒有意義。"),
       (False, "超平面會平移，但方向不變",
        "不對。平移是只改 β₀；這裡三個係數一起乘，f(x) = 0 的解集合完全一樣。"
        "你可以把滑桿的 β₀、β₁、β₂ 從 1、2、3 改成 −2、−4、−6 試試，線會停在原處。"),
       (False, "‖β‖ 不變，所以距離不變，一切照舊",
        "‖β‖ 其實變成 2 倍（不是不變）。不過結論反而對了一半：|f(x)| 與 ‖β‖ 都變 2 倍，"
        "相除之後<strong>距離真的不變</strong>，但「一切照舊」是錯的，正負號整組翻了。")])}
"""

# ── P01 maxmargin ─────────────────────────────────────────────────────
BODIES["maxmargin"] = f"""
  <p>如果資料真的分得開，麻煩來了：<strong>分離超平面有無限多個</strong>。
  隨便一條分得開的線，都可以稍微平移一點、旋轉一點，還是分得開（ISLP 圖 9.2 左畫了三條）。
  無限多個候選，總得有個挑法。</p>

  <p>挑法很自然：<strong>選離兩邊都最遠的那一條</strong>。先算每個訓練點到超平面的垂直距離，
  其中<strong>最小</strong>的那個距離叫做<strong>邊界</strong>（margin，ISLP 記為 M）；
  邊界最大的那個分離超平面就是<strong>最大邊界超平面</strong>（maximal margin hyperplane，
  也叫最佳分離超平面）。用它做分類就是<strong>最大邊界分類器</strong>。</p>

{info("一句話的幾何直覺", '''最大邊界超平面就是<strong>能塞進兩類之間那塊最寬「板子」的中線</strong>。
  板子有多寬由最擠的地方決定，所以答案只跟「最擠的那幾個點」有關。這件事等一下會變成
  整章最重要的性質。''')}

  <p>寫成最佳化問題（ISLP 式 9.9–9.11）：</p>

  $$\\begin{{aligned}}
    &\\underset{{\\beta_0,\\beta_1,\\dots,\\beta_p,\\,M}}{{\\text{{maximize}}}} \\quad M \\\\
    &\\text{{subject to}} \\quad \\sum_{{j=1}}^{{p}} \\beta_j^2 = 1, \\\\
    &\\qquad\\qquad\\quad\\; y_i\\left(\\beta_0 + \\beta_1 x_{{i1}} + \\cdots + \\beta_p x_{{ip}}\\right)
      \\ge M \\quad \\forall\\, i
  \\end{{aligned}}$$

  <p>兩個限制式各有分工。$\\sum \\beta_j^2 = 1$ <strong>不是</strong>對超平面的限制（前一節說過，
  縮放係數不改變超平面），它的作用是<strong>把 $y_i f(x_i)$ 校準成真正的距離</strong>；
  有了這個校準，第二條 $y_i f(x_i) \\ge M$ 才真的在說「每一筆都在正確一側，而且至少離 M 遠」。
  於是 M 就是邊界，而目標函數就是把它推到最大。</p>

{viz(svg("w10marginSvg", 430),
     [info_card("怎麼玩",
                '<strong>直接拖動任何一個點。</strong>元件會即時解出最大邊界超平面：'
                '紅實線是邊界、兩條虛線是 margin 的兩側、'
                '<span style="color:var(--pt-held);font-weight:700;">加粗描邊</span>的點是'
                '<strong>支持向量</strong>。<br>'
                '<strong>重點在這裡：拖動任何一個沒被描邊的點，只要不越過虛線，'
                '紅線一動也不動。</strong>拖到越過虛線，它就變成支持向量、線立刻跟著動。'),
      rows_card("即時解",
                [("margin 半寬 M", "—", "w10marginM"),
                 ("板子總寬 2M", "—", "w10marginW"),
                 ("支持向量個數", "—", "w10marginNsv"),
                 ("邊界（f = 0）", "—", "w10marginEq")]),
      info_card("解是怎麼算出來的",
                '不是跑 QP，是用一個等價的幾何事實：<strong>最大邊界超平面就是'
                '兩類凸包最近點對連線的垂直平分線</strong>，M 是那段距離的一半'
                '（紫色線段）。點很少，把所有候選組合都算一遍就好，每次拖曳都重算。<br>'
                '凸包一旦重疊就不存在分離超平面。把兩堆點拖到交錯，'
                '元件會直接說解不出來。', "LIVE")],
     "w10marginStatus", "拖動任何一個點。加粗描邊的是支持向量，只有它們會改變答案。",
     '<button class="btn btn-reset" onclick="w10marginReset()">重置點的位置</button>'
     '<button class="btn btn-toggle" onclick="w10marginToggleHull()">切換凸包顯示</button>')}

  <p>那幾個剛好落在虛線上的點就是<strong>支持向量</strong>（support vector）。
  名字的由來很直白：它們像柱子一樣「支撐」著那片超平面——移動它們，超平面跟著動；
  移動別的點，超平面完全不理你（只要那個點沒有越過 margin）。ISLP 說得很重：</p>

  <p>順便說一句：<strong>ISLP §9.7 第 3 題就是這個元件的手算版</strong>。它給你 7 個點，
  答案是 $X_2 = X_1 - 0.5$，支持向量是第 2、3、5、6 筆，$M = 1/(2\\sqrt{{2}}) \\approx 0.354$；
  第 (f) 小題問「第 7 筆稍微移動會不會影響超平面」。你在上面拖過就知道答案了。
  本頁 EX 區的第 3 題會再問一次。</p>

{info("最大邊界超平面只依賴支持向量，不依賴其他觀測值", '''這是本章反覆出現的主題。
  好處是<strong>對離邊界很遠的點極度穩健</strong>——LDA 的規則要用到每一類的平均與整體共變異，
  換掉一個遠處的點就會動；最大邊界超平面不會。<br>
  壞處是<strong>對支持向量極度敏感</strong>。ISLP 圖 9.5 就是這個代價：右圖只多加一個藍點，
  最大邊界超平面就大幅轉向，而且 margin 縮到極窄。只靠三個點決定的分類器，
  聽起來就不太可靠。這正是下一節要修的問題。''', "warm")}

  <h3 id="dx-sep">講義完整實作：把兩類推開到剛好可分開，再用超大的 C 配適</h3>
{card("lab 09 · 剛好線性可分開的情況（C = 10⁵）",
      lab_code(CH, 41) + "\n\n" + lab_code(CH, 43), lab_output(CH, 43),
      src=src("41、43"), out_tag="預期輸出（儲存格 43）",
      note="<code>X[y==1] += 1.9</code> 把兩類再推開一點，剛好變成線性可分開。"
           "用 <code>C=1e5</code>（sklearn 的 C，見下一節）配出來的分類器沒有任何訓練誤差，"
           "而且<strong>只用了 3 個支持向量</strong>。這就是最大邊界超平面。"
           "lab 儲存格 47 換成 <code>C=0.1</code>，訓練誤差同樣是 0，"
           "但支持向量變成 <strong>12 個</strong>、margin 寬得多。"
           "ISLP §9.6.1 的評語是：後者「因為點更多所以更穩定」，在測試資料上可能更好。")}

{qa("觀念釐清", [
    ("Q：為什麼叫「支持向量」？為什麼只有它們影響解？",
     "<p>先說「向量」：在 p 維空間裡，一筆觀測值 $x_i$ 就是一個 p 維向量，所以這些點本來就是向量。"
     "「支持」則是力學的比喻。它們頂在 margin 的兩側，撐著那塊板子。抽掉一根柱子，板子就塌下來換位置。</p>"
     "<p><strong>從最佳化的角度看：</strong>最大邊界問題的限制式是 $y_i f(x_i) \\ge M$。"
     "在最佳解上，只有<strong>取等號</strong>的那些限制式是「緊的」（active）；"
     "取嚴格大於的限制式等於根本沒在限制什麼，把它整條刪掉，解一模一樣。"
     "KKT 條件把這件事寫成 $\\hat\\alpha_i \\left(y_i f(x_i) - M\\right) = 0$："
     "限制式不緊時 $\\hat\\alpha_i = 0$，而解只由 $\\hat\\alpha_i > 0$ 的那些點組成"
     "（講義第 18 頁：$\\hat\\beta = \\sum_i \\hat\\alpha_i y_i x_i$）。</p>"
     "<p><strong>從損失函數的角度看：</strong>本頁 PART 03 會證明支持向量分類器等價於最小化"
     "hinge loss 加上 ridge 懲罰，而 hinge loss 在 $y_i f(x_i) \\ge 1$ 時<strong>剛好等於 0</strong>。"
     "一個對目標函數貢獻恰好為 0 的點，當然不可能影響最佳解。兩個角度說的是同一件事。</p>"),
    ("Q：margin 大在測試資料上真的比較好嗎？",
     "<p>直覺上合理：margin 大表示兩類之間有一塊很寬的無人區，新資料落進來也大概不會踩線。"
     "ISLP 就是這樣說服讀者的——「我們<em>希望</em>訓練資料上 margin 大的分類器在測試資料上 margin 也大」。</p>"
     "<p>但它明確加了一句警告：<strong>p 很大的時候最大邊界分類器會過度配適</strong>。"
     "維度愈高，愈容易找到一片「剛好」把訓練資料切開的超平面。那片超平面的位置可能完全由雜訊決定。"
     "lab 的 <code>Khan</code> 資料就是極端例子：n = 63 而 p = 2308，訓練誤差輕鬆變成 0，"
     "「這並不令人驚訝」。</p>"
     "<p>所以實務上幾乎沒有人用純粹的最大邊界分類器。真正在用的是加了正則化的軟邊界版本，"
     "而且那個調整參數要靠交叉驗證選。</p>"),
])}

{quiz("qMax", "QUIZ · 最大邊界",
      "在最大邊界分類器裡，把一個<strong>非</strong>支持向量的點往遠離邊界的方向移動一小段，"
      "解會怎麼變？",
      [(True, "完全不變。它對應的限制式本來就是鬆的，移動之後更鬆，一樣不影響最佳解",
        "對。這就是「解只依賴支持向量」的意思，也是 ISLP §9.7 第 3 題 (f) 小題的答案。"
        "反過來說，如果把它往邊界推到越過 margin，它就變成支持向量，解會立刻改變。"),
       (False, "會稍微改變，因為目標函數是所有點的距離總和",
        "不對。目標函數是 <strong>M</strong>，而 M 定義成所有距離的<strong>最小值</strong>，不是總和。"
        "最小值只由最近的那幾個點決定，遠處的點加加減減都不影響。"),
       (False, "邊界方向不變，但 β₀ 會微調，因為資料的重心動了",
        "不對，這是 LDA 的思路。LDA 的規則確實建立在各類的<strong>平均</strong>上，所以任何一點動了它都會動；"
        "最大邊界超平面完全不看重心，只看最擠的地方。")])}
"""

# ── P02 soft ──────────────────────────────────────────────────────────
BODIES["soft"] = f"""
  <p>上一節結尾的兩個問題要一起解決。第一個是<strong>資料常常根本分不開</strong>
  （講義第 10 頁：除非 n &lt; p，通常都分不開），這時 M &gt; 0 的解不存在，
  整個最佳化問題沒有答案。第二個是<strong>就算分得開，硬要分開也可能是壞主意</strong>
  ——ISLP 圖 9.5 只加一個點就讓超平面大幅轉向，margin 縮到極窄。</p>

  <p>解法是<strong>把「分開」的定義放鬆</strong>：允許少數點跑到 margin 錯的一側，
  甚至跑到超平面錯的一側。換來的是兩件 ISLP 明列的好處——
  <strong>對單一觀測值更穩健</strong>，以及<strong>大多數點分得更好</strong>。
  這個分類器叫<strong>支持向量分類器</strong>，也叫<strong>軟邊界分類器</strong>
  （margin 之所以「軟」，就是因為它可以被違反）。</p>

  $$\\begin{{aligned}}
    &\\underset{{\\beta_0,\\dots,\\beta_p,\\,\\epsilon_1,\\dots,\\epsilon_n,\\,M}}{{\\text{{maximize}}}}
      \\quad M \\\\
    &\\text{{subject to}} \\quad \\sum_{{j=1}}^{{p}} \\beta_j^2 = 1, \\\\
    &\\qquad\\qquad\\quad\\; y_i\\left(\\beta_0 + \\beta_1 x_{{i1}} + \\cdots + \\beta_p x_{{ip}}\\right)
      \\ge M\\left(1 - \\epsilon_i\\right), \\\\
    &\\qquad\\qquad\\quad\\; \\epsilon_i \\ge 0, \\quad \\sum_{{i=1}}^{{n}} \\epsilon_i \\le C
  \\end{{aligned}}$$

  <p>新東西是<strong>鬆弛變數</strong>（slack variable）$\\epsilon_i$：它記錄第 i 筆
  相對於 margin 與超平面的位置。三種狀態要分清楚：</p>

{table(["εᵢ 的值", "這一筆在哪裡", "是支持向量嗎", "分類正確嗎"],
       [["εᵢ = 0", "在 margin 正確的一側（或剛好在 margin 上）",
         "只有「剛好在 margin 上」的算", "是"],
        ["0 &lt; εᵢ ≤ 1", "違反了 margin，但還在超平面正確的一側", "是", "是"],
        ["εᵢ &gt; 1", "跑到超平面<strong>錯的</strong>一側", "是", "<strong>否</strong>"]])}

  <p>然後是 $\\sum_i \\epsilon_i \\le C$ 這一條。ISLP 把 C 說成
  <strong>「margin 可以被違反多少的預算」</strong>：C = 0 時沒有預算，
  所有 $\\epsilon_i$ 必須是 0，整個問題退回最大邊界超平面；
  C 愈大，愈容忍違反，margin 就愈寬。這裡有一個大坑，先講清楚：</p>

{info("ISLP 的 C 與 scikit-learn 的 C 方向完全相反", '''<strong>ISLP 式 9.15 的 C 是「預算」</strong>
  ——違反量的總和上限。C 大 → 容忍多 → margin 寬 → 支持向量多 → 偏差大變異小。<br>
  <strong>scikit-learn 的 <code>SVC(C=…)</code> 是「懲罰」</strong>
  ——目標函數是 ½‖β‖² + C·Σεᵢ，C 是對違反的罰款。C 大 → 罰得重 → 容忍少 →
  margin 窄 → 支持向量少 → 偏差小變異大。<br>
  講義第 18 頁把這件事寫成一行：<strong>「C 與 const 成反比」</strong>
  （const 就是 ISLP 的預算 C）。<br>
  所以看到 C 一定要先問是哪一種。下面的元件與 lab 用的都是 <strong>sklearn 的 C</strong>，
  滑桿往右推是「罰得更重、margin 更窄」。''', "warm")}

{viz(svg("w10softSvg", 360) + "\n" + chart("w10softChart", "", "。此圖的重點：sklearn 的 C 從 0.001 加到 100，支持向量個數從 50（全部）一路掉到 27 左右——C 愈大容忍愈少，參與決定邊界的點就愈少。"),
     [info_card("怎麼看",
                '上圖：<span style="color:var(--pt-a);font-weight:700;">藍</span>與'
                '<span style="color:var(--pt-b);font-weight:700;">紅</span>是兩類，'
                '紅實線是邊界、虛線是 margin 的兩側、淡藍色帶子是 margin 區域。'
                '<strong>加粗描邊的是支持向量</strong>，方框標記的是<strong>被錯誤分類</strong>'
                '（εᵢ &gt; 1）的點。<br>'
                '下圖：同一組資料掃過六個 C，支持向量個數與違反 margin 的點數。', "圖 9.7"),
      rows_card("這一格的配適",
                [("sklearn 的 C", "—", "w10softC"),
                 ("ISLP 的預算 C 相當於", "—", "w10softBudget"),
                 ("margin 半寬 1/‖β‖", "—", "w10softM"),
                 ("支持向量個數", "—", "w10softNsv"),
                 ("違反 margin 的點", "—", "w10softViol"),
                 ("被錯誤分類的點", "—", "w10softWrong")]),
      info_card("兩組資料在對什麼",
                '<strong>「不可分開」</strong>就是 lab 儲存格 14 那 50 筆。'
                'C = 10 時支持向量 29 個（lab 儲存格 22、23），C = 0.1 時 36 個'
                '（儲存格 27 的 <code>[18 18]</code>）——元件上的數字就是那些數字。<br>'
                '<strong>「剛好可分開」</strong>是儲存格 41 把兩類推開 1.9 之後的版本。'
                'C = 10⁵ 只用 3 個支持向量、C = 0.1 用 12 個，正是 ISLP §9.6.1 講的 '
                'three 與 twelve。', "BAKED"),
                ],
     "w10softStatus", "選資料集、推 C 的滑桿，看邊界、margin 帶與支持向量怎麼變。",
     '<label class="slider-label" style="margin-right:.4rem;">資料</label>'
     '<select id="w10softSel" class="mono" onchange="w10softSetData()">'
     '<option value="nonsep" selected>不可分開（儲存格 14）</option>'
     '<option value="sep">剛好可分開（儲存格 41）</option></select>'
     + slider("w10softSl", "sklearn 的 C", 0, 5, 1, 3, "w10softDraw()", "w10softSlV", "1",
              basis="1 1 240px", vw=54, lw=86))}

  <p>偏差與變異在這張圖上看得很清楚。<strong>C 小（滑桿左端）</strong>：margin 寬、支持向量多，
  決定邊界的點多，所以<strong>變異小、偏差大</strong>，配得比較鬆。
  <strong>C 大（滑桿右端）</strong>：margin 窄、支持向量少，邊界由少數點決定，
  所以<strong>偏差小、變異大</strong>，配得很緊。C 就是這一章的調整參數，
  跟 ridge 的 $\\lambda$、樹的 $\\alpha$ 是同一種東西，一律靠交叉驗證選。</p>

  <p>最重要的性質原封不動地繼承下來，而且更強：<strong>只有落在 margin 上、
  或違反 margin 的觀測值會影響超平面</strong>。嚴格待在正確一側的點，
  你把它拖到再遠的地方，分類器完全不變。這些會影響答案的點就是支持向量。</p>

  <h3 id="dx-sv">講義完整實作：支持向量是哪幾筆</h3>
{card("lab 09 · 取出支持向量（C = 10）",
      lab_code(CH, 22) + "\n\n" + lab_code(CH, 23), lab_output(CH, 23),
      src=src("21、22、23"), out_tag="預期輸出（儲存格 23）",
      note="<code>support_</code> 是支持向量在原始資料裡的<strong>索引</strong>"
           "（儲存格 22 印出 29 個），<code>n_support_</code> 是每一類各幾個："
           "<code>[15, 14]</code>，合起來 29。儲存格 21 用 "
           "<code>support_vectors_</code> 把座標印成表格。"
           "50 筆資料裡有 29 筆是支持向量。這份資料重疊得很厲害。")}

{card("lab 09 · 換成小的 C：支持向量變多", lab_code(CH, 25) + "\n\n" + lab_code(CH, 27),
      lab_output(CH, 27), src=src("25、27"), out_tag="預期輸出（儲存格 27）",
      note="<code>C=0.1</code> 的支持向量變成 <code>[18, 18]</code> = 36 個。"
           "lab 的說法是「使用較小的成本參數值，我們獲得更多的支援向量，因為邊界現在更寬」"
           "——<strong>sklearn 的 C 小 ＝ 罰得輕 ＝ margin 寬</strong>，跟 ISLP 的預算 C 剛好相反。")}

  <h3 id="dx-cv">講義完整實作：用交叉驗證選 C</h3>
{card("lab 09 · GridSearchCV 掃七個 C", lab_code(CH, 31) + "\n\n" + lab_code(CH, 33),
      lab_output(CH, 33), src=src("31、33"), out_tag="預期輸出（儲存格 33）",
      note="七個 C 的 5 折交叉驗證準確率是 <code>[0.46, 0.46, 0.72, 0.74, 0.74, 0.74, 0.74]</code>。"
           "最佳是 C = 1（儲存格 31 的輸出），但後面四個 C 的準確率完全一樣。"
           "<strong>這種平台很常見，就挑最簡單（最正則化）的那個</strong>，"
           "不要假裝 0.74 跟 0.74 有差別。"
           "注意 C = 0.001 與 0.01 的準確率只有 0.46，比亂猜還差：罰得太輕，"
           "β 被壓到幾乎是 0，分類器整組崩掉。")}

{card("lab 09 · 用選出來的 C 預測測試資料", lab_code(CH, 37), lab_output(CH, 37),
      src=src("35、37"), out_tag="預期輸出（儲存格 37）",
      note="混淆矩陣的對角線是 8 + 6 = 14，20 筆裡對了 14 筆 → <strong>70%</strong>。"
           "lab 儲存格 39 換成 <code>C=0.001</code>，正確率掉到 60%（幾乎把所有點都判成 +1）。"
           "這一頁的每一個混淆矩陣都是 <code>confusion_table(預測, 真實)</code>："
           "<strong>列是預測、欄是真實</strong>，順序跟 sklearn 的 "
           "<code>confusion_matrix</code> 相反，看的時候要注意。")}

{qa("觀念釐清", [
    ("Q：C 到底是「容忍度」還是「懲罰」？我每次都搞反。",
     "<p>兩個都對，因為那是<strong>兩個不同的 C</strong>。記一個口訣："
     "<strong>ISLP 的 C 在限制式裡，sklearn 的 C 在目標函數裡。</strong></p>"
     "<p><strong>ISLP（式 9.15）：</strong>$\\sum_i \\epsilon_i \\le C$。C 站在不等式的右邊，"
     "是「你最多可以犯多少規」的<strong>預算</strong>。預算多 → 犯規多 → margin 寬。"
     "C = 0 就是一毛錢都不准犯規，退回最大邊界分類器。</p>"
     "<p><strong>sklearn（等價的 primal 式，講義第 18 頁）：</strong>"
     "$\\min \\frac12\\lVert\\beta\\rVert^2 + C\\sum_i \\epsilon_i$。C 站在目標函數裡乘著犯規總量，"
     "是<strong>罰款單價</strong>。單價高 → 沒人敢犯規 → margin 窄。"
     "$C \\to \\infty$ 就是硬邊界。</p>"
     "<p>所以講義寫「C 與 const 成反比」。實務上你摸到的幾乎都是 sklearn 那個，"
     "記住<strong>「C 大 ＝ 配得緊 ＝ 容易過度配適」</strong>就好，"
     "跟 ridge 的 λ 剛好反向（λ 大 ＝ 配得鬆）。順便一提，"
     "$\\lambda$ 在式 9.25 裡的方向與 ISLP 的預算 C 同向。</p>"),
    ("Q：SVM 需要標準化嗎？",
     "<p>需要，而且比大多數方法更需要。講義第 33 頁講得很直接："
     "<strong>「SVM 的演算法不具尺度不變性，所以強烈建議先縮放你的資料」</strong>。</p>"
     "<p>理由就在這一章的第一句話：SVM 從頭到尾都在算<strong>距離</strong>與<strong>內積</strong>。"
     "一個以「元」為單位的收入變數（範圍幾十萬）和一個以「年」為單位的年齡變數（範圍幾十），"
     "在 ‖β‖ 與 margin 裡的權重會差好幾個數量級——收入那一維會完全主導邊界的方向，"
     "年齡等於被忽略。RBF 核更嚴重，因為 $\\exp(-\\gamma \\sum_j (x_{ij}-x_{i'j})^2)$ "
     "裡的平方距離會被大尺度的那一維吃光。</p>"
     "<p>做法跟第 5 章一樣：把 <code>StandardScaler</code> 包進 <code>Pipeline</code>，"
     "再交給 <code>GridSearchCV</code>，這樣每一折都會用該折的訓練部分重新算平均與標準差，"
     "不會洩漏。順帶一提，這也是為什麼 lab 的 <code>Khan</code> 例子用線性核就好——"
     "基因表現量本來就在同一個尺度上。</p>"),
])}

{quiz("qSoft", "QUIZ · 軟邊界與 C",
      "在 <code>scikit-learn</code> 裡把 <code>SVC(kernel='linear')</code> 的 C 從 0.1 加到 100，"
      "預期會看到什麼？",
      [(True, "margin 變窄、支持向量變少、訓練誤差變小，但過度配適的風險上升",
        "對。sklearn 的 C 是違反的<strong>懲罰</strong>，加大就是「不准犯規」，"
        "所以 margin 縮窄、只剩少數點頂在 margin 上。lab 儲存格 23／27 的 29 對 36 就是這個現象。"
        "偏差變小、變異變大。"),
       (False, "margin 變寬、支持向量變多，因為 C 是違反量的預算",
        "把兩個 C 搞混了。<strong>ISLP 式 9.15 的 C 是預算</strong>，加大確實會讓 margin 變寬；"
        "但 <code>scikit-learn</code> 的 C 是<strong>懲罰</strong>，方向相反。"
        "講義第 18 頁明說「C 與 const 成反比」。"),
       (False, "margin 不變，只有被判錯的點數會變，因為 margin 由資料的幾何決定",
        "不對。margin 半寬是 1/‖β‖，而 β 是最佳化的結果——換了 C 就換了目標函數，"
        "β 會變、margin 當然跟著變。只有在資料可分開且 C → ∞ 時，margin 才會固定成最大邊界那個值。")])}
"""

# ── P03 hinge ─────────────────────────────────────────────────────────
BODIES["hinge"] = f"""
  <p class="skip-note">📑 這一節是延伸：它解釋「為什麼只有支持向量影響答案」背後的損失函數，
  是 ISLP §9.5 與 ESL §12.3.2 的內容。第一輪讀可以先跳過，直接去 PART 04 的核技巧；
  但如果你想真正弄懂 SVM 跟邏輯斯迴歸的關係，回頭一定要讀這一節。</p>

  <p>前面把支持向量分類器寫成一個帶限制式的最佳化問題。ISLP §9.5 給了一個
  <strong>完全等價、但看起來完全不同</strong>的寫法（式 9.25）：</p>

  $$\\underset{{\\beta_0,\\beta_1,\\dots,\\beta_p}}{{\\text{{minimize}}}}
    \\left\\{{ \\sum_{{i=1}}^{{n}} \\max\\left[0,\\; 1 - y_i f(x_i)\\right]
    \\; + \\; \\lambda \\sum_{{j=1}}^{{p}} \\beta_j^2 \\right\\}}$$

  <p>這就是全書一直在用的<strong>「損失 + 懲罰」</strong>格式（式 9.26）。
  後面那一項你認得。它就是第 6 章的 ridge 懲罰。前面那一項叫
  <strong>hinge loss</strong>（合頁損失，因為它的圖長得像門的合頁）：</p>

  $$L\\left(X, y, \\beta\\right) = \\sum_{{i=1}}^{{n}}
    \\max\\left[0,\\; 1 - y_i\\left(\\beta_0 + \\beta_1 x_{{i1}} + \\cdots + \\beta_p x_{{ip}}\\right)\\right]$$

{info("λ 與 C 的對應關係", '''式 9.25 的 λ 大 → β 被壓得小 → margin 寬 → 容忍更多違反，
  所以 <strong>λ 大對應 ISLP 的預算 C 大</strong>（也就是 sklearn 的 C 小）。
  ISLP 原文：「a small value of λ in (9.25) amounts to a small value of C in (9.15)」。<br>
  注意腳註裡的一句話：在這個 hinge + 懲罰的寫法下，<strong>margin 固定對應到數值 1</strong>，
  而 margin 的實際寬度由 √Σβⱼ² 決定。所以「調 λ」跟「調 margin 寬度」是同一件事。''')}

  <p>現在看那條曲線。橫軸是 $y_i f(x_i)$——分對了是正的，愈大愈篤定；分錯了是負的。</p>

{viz(chart("w10lossChart", "tall", "。此圖的重點：hinge loss 在 y·f(x) ≥ 1 之後完全等於 0，邏輯斯損失則永遠大於 0（只是很小）。這個「完全等於 0」就是支持向量稀疏性的來源。"),
     [info_card("怎麼看這張圖",
                '<strong>綠線是 hinge</strong> max(0, 1 − y·f)，'
                '<strong>紅線是邏輯斯損失</strong> log(1 + e^(−y·f))。'
                '灰色區帶是 y·f ≥ 1——<strong>綠線在那裡貼在 0 上，紅線只是變小但永遠不是 0</strong>。'
                '其他地方兩條幾乎平行，這就是 ISLP 說「行為相當相似」的意思。', "圖 9.12"),
      rows_card("幾個位置的損失",
                [("y·f = 2（篤定分對）", "—", "w10loss2"),
                 ("y·f = 1（剛好在 margin 上）", "—", "w10loss1"),
                 ("y·f = 0（剛好在邊界上）", "—", "w10loss0"),
                 ("y·f = −2（篤定分錯）", "—", "w10lossN2")])],
     "w10lossStatus", "綠線是 hinge、紅線是邏輯斯。注意綠線在右邊完全貼著 0。",
     '<button class="btn btn-toggle" onclick="w10lossToggle01()">顯示 0–1 損失</button>'
     '<button class="btn btn-toggle" onclick="w10lossToggleZoom()">切換 y 軸範圍</button>')}

  <p>那個「剛好是 0」是本節的全部重點。一個損失恰好為 0 的點，對目標函數的貢獻是 0，
  <strong>對它求梯度也是 0</strong>。把它從資料裡整筆刪掉，最佳解一模一樣。
  所以最佳解只由 $y_i f(x_i) < 1$ 的那些點決定，而那些點正好就是
  「落在 margin 上或違反 margin」的觀測值，也就是<strong>支持向量</strong>。
  對照之下，邏輯斯迴歸的損失永遠大於 0，每一筆資料都在（微弱地）拉扯答案，
  所以它<strong>沒有</strong>稀疏性、也沒有支持向量的概念。</p>

  <p>按「顯示 0–1 損失」會疊上我們<strong>真正</strong>想最小化的東西：分錯是 1、分對是 0 的
  階梯函數。它既不連續也不凸，沒辦法直接最佳化，所以大家改去最小化它的
  <strong>凸上界</strong>。hinge 與邏輯斯都是這樣的上界，這種替身叫做
  <strong>代理損失</strong>（surrogate loss）。你在圖上會看到兩條曲線都完整地蓋在階梯之上。</p>

  <h3 id="dx-sgd">講義完整實作：直接對 hinge loss 做隨機梯度下降</h3>
{card("lab 09 · SGDClassifier(loss=\"hinge\")", lab_code(CH, 95), None, src=src("95"),
      note="講義第 32 頁的重點：<code>SGDClassifier(loss=\"hinge\")</code> 就是"
           "<strong>用隨機梯度下降去最小化式 9.25</strong>，"
           "<code>alpha</code> 就是 λ。它不解 QP，所以資料量很大時比 <code>SVC</code> 快得多，"
           "代價是解得比較粗。這一格畫的三條等高線 <code>[-1, 0, 1]</code> "
           "就是 margin 的兩側與邊界本身——跟 <code>plot_svm()</code> 畫的是同一件事。"
           "順帶一提，講義也提醒 <strong>SGD 對特徵尺度很敏感</strong>，用它之前更要標準化。")}

{quiz("qHinge", "QUIZ · Hinge loss",
      "某一筆觀測值的 y·f(x) = 3。它對式 9.25 那個目標函數的貢獻是多少？"
      "把它從訓練資料裡刪掉會發生什麼事？",
      [(True, "貢獻是 0；刪掉它最佳解完全不變（除非刪掉之後別的點的位置關係改變了 margin）",
        "對。max(0, 1 − 3) = 0，梯度也是 0。這就是稀疏性的來源："
        "只有 y·f(x) &lt; 1 的點（支持向量）在決定 β。"
        "括號裡那句是嚴謹的補充——刪點不會改變<em>這個</em>解是否最佳，"
        "但如果被刪的點原本擋住了更寬的 margin，那它就不是「y·f = 3」了。"),
       (False, "貢獻是 −2，因為 1 − y·f(x) = −2",
        "少看了外面那個 max。hinge loss 是 max(0, 1 − y·f)，<strong>不會是負的</strong>——"
        "損失函數如果可以是負的，最佳化就會去追求「分對得愈誇張愈好」，那沒有意義。"),
       (False, "貢獻很小但不是 0，所以刪掉它解會微微改變",
        "這是<strong>邏輯斯損失</strong>的性質，不是 hinge。"
        "log(1 + e^(−3)) ≈ 0.049，確實很小但不是 0；hinge 在這裡是<strong>精確的 0</strong>。"
        "兩者的差別就在這裡：邏輯斯迴歸沒有支持向量的概念。")])}
"""

# ── P04 kernel ────────────────────────────────────────────────────────
BODIES["kernel"] = f"""
  <p>軟邊界解決了「分不開」，但沒有解決「<strong>邊界根本不是直的</strong>」。
  講義第 19 頁那張圖就是這種情形：一團在中間、一圈在外面，
  無論 C 調成多少，一條直線都沒救。</p>

  <p>第 7 章遇過一模一樣的問題，答案是<strong>特徵擴張</strong>（feature expansion）：
  把 $X_1^2, X_2^2, X_1X_2, X_1^3, \\dots$ 加進特徵裡，在放大的空間配線性分類器，
  映射回原空間就變成彎的邊界。用二次項的話（ISLP 式 9.16）：</p>

  $$\\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\beta_3 X_1^2 + \\beta_4 X_2^2
    + \\beta_5 X_1 X_2 = 0$$

  <p>這在放大的空間裡是<strong>線性</strong>的，在原空間裡是二次曲線（圓、橢圓、雙曲線）。
  問題是維度爆炸得很快：講義第 21 頁做到三次多項式，兩個變數就變成九維；
  p 個變數做到 d 次是 $\\binom{{p+d}}{{d}} - 1$ 維。p = 100、d = 3 就已經 17 萬多維，
  算不動。</p>

{info("關鍵事實：解與預測只用得到內積", '''ISLP §9.3.2 揭露一件很漂亮的事：
  支持向量分類器的解與預測<strong>只需要觀測值之間的內積</strong>，用不到觀測值本身。<br>
  $$f(x) = \\beta_0 + \\sum_{i \\in S} \\alpha_i \\langle x, x_i \\rangle,
    \\qquad \\langle x_i, x_{i'} \\rangle = \\sum_{j=1}^{p} x_{ij} x_{i'j}$$
  要估 $\\alpha_1,\\dots,\\alpha_n$ 與 $\\beta_0$，只要算出所有 $\\binom{n}{2}$ 對
  訓練觀測值之間的內積就夠了（講義第 23 頁）。<br>
  而且 $\\alpha_i$ <strong>只有支持向量是非零的</strong>，所以那個和式的項數通常遠少於 n。''')}

  <p>既然演算法只透過內積接觸資料，那就<strong>把每一處內積換成別的東西</strong>：</p>

  $$\\langle x_i, x_{{i'}} \\rangle \\;\\longrightarrow\\; K(x_i, x_{{i'}})$$

  <p>$K$ 叫做<strong>核</strong>（kernel），是一個衡量兩筆觀測值有多像的函數。
  這就是<strong>核技巧</strong>（kernel trick）：講義第 22 頁一句話說完——
  <strong>「我們不需要真的知道 Φ(x)，只要在原空間用核函數計算就好」</strong>。</p>

  <p>講義第 24 頁的例子把這件事說得最清楚。取二次映射
  $\\Phi(x) = (\\sqrt{{2}}\\,x_1 x_2,\\; x_1^2,\\; x_2^2)$，那麼</p>

  $$\\Phi(a)^{{\\top}} \\Phi(b) = 2a_1a_2b_1b_2 + a_1^2b_1^2 + a_2^2b_2^2
    = \\left(a_1b_1 + a_2b_2\\right)^2 = \\left(a^{{\\top}} b\\right)^2$$

  <p>左邊要先算兩個三維向量再做內積；右邊只要在<strong>原本的二維空間</strong>做一次內積再平方。
  兩者<strong>完全相等</strong>。維度愈高這個省法愈划算；RBF 核對應的特徵空間是無限維的，
  本來就不可能真的走進去算。</p>

{viz(svg("w10kernSvg", 430),
     [info_card("怎麼玩",
                '<strong>「一維 → 二維」</strong>：按 ▶ 看點被抬到 (x, x²)。'
                '一維上紅色被藍色夾住、一個門檻切不開；抬到二維後'
                '<strong>一條水平線就分開了</strong>；映射回一維就變成兩個門檻。<br>'
                '<strong>「同心圓 → 二次核」</strong>：lab 儲存格 52 的真實資料，'
                '填色是二次核 SVM 的決策區域。', "LIVE + BAKED"),
      info_card("核技巧的三步", '<div class="pseudo-code" id="w10kernCode" style="font-size:.74rem;">'
                '<span class="line" data-l="1">原空間分不開</span>\n'
                '<span class="line" data-l="2">映射 φ：x → (x, x²)</span>\n'
                '<span class="line" data-l="3">在新空間配線性超平面</span>\n'
                '<span class="line" data-l="4">映射回去 → 彎的邊界</span>\n'
                '<span class="line" data-l="5">核技巧：跳過第 2、3 步，</span>\n'
                '<span class="line" data-l="6">直接算 K(x, x′) 就好</span></div>', "CODE"),
      rows_card("狀態",
                [("目前的空間", "—", "w10kernSpace"),
                 ("需要幾維", "—", "w10kernDim"),
                 ("線性分得開嗎", "—", "w10kernSep"),
                 ("支持向量個數", "—", "w10kernNsv"),
                 ("內圈的 x₁²+x₂² 最大", "—", "w10kernInner"),
                 ("外圈的 x₁²+x₂² 最小", "—", "w10kernOuter")])],
     "w10kernSvgStatus", "選模式後按「開始」。一維的點會被抬到二維，然後一條直線就分開了。",
     '<label class="slider-label" style="margin-right:.4rem;">模式</label>'
     '<select id="w10kernSel" class="mono" onchange="w10kernSetMode()">'
     '<option value="lift" selected>一維 → 二維（x → x²）</option>'
     '<option value="circle">同心圓 → 二次核</option></select>'
     '<button class="btn btn-play" onclick="w10kernStart()">▶ 開始</button>'
     '<button class="btn btn-step" onclick="w10kernStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w10kernReset()">重置</button>')}

  <h3 id="dx-map">講義完整實作：手寫一個二次核，跟「先映射再配線性」比對</h3>
{card("lab 09 · 特徵映射 vs 自訂核（同心圓資料）",
      lab_code(CH, 51) + "\n\n" + lab_code(CH, 52), lab_output(CH, 52),
      src=src("51、52"), out_tag="預期輸出（儲存格 52）",
      note="<code>feature_map_1</code> 把二維點送到三維 (√2·x₁x₂, x₁², x₂²)，"
           "<code>my_kernel_1</code> 則是那個映射的內積，也就是它的核。"
           "在三維空間配出來的線性超平面是 "
           "<code>w = [-0.0548, -2.5319, -2.5203]</code>、<code>b = 1.1498</code>："
           "第一個係數幾乎是 0（交互項沒用），"
           "後兩個幾乎相等且為負。<strong>它學到的其實就是「x₁² + x₂² 小的是內圈」</strong>。")}

{card("lab 09 · 兩條路的答案一模一樣", lab_code(CH, 53), lab_output(CH, 53),
      src=src("53、54"), out_tag="預期輸出（儲存格 53）",
      note="<code>SVC(kernel=my_kernel_1)</code>（只用核、留在二維）與 "
           "<code>SVC(kernel='linear').fit(Z, y)</code>（真的升到三維）"
           "訓練準確率都是 <strong>1.0</strong>。"
           "<strong>這就是核技巧的全部意思</strong>：兩條路數學上等價，"
           "但右邊那條不需要把 Φ(x) 算出來。儲存格 54 把決策區域畫出來，"
           "在原空間看是一個圓。")}

  <p>常用的核有三個（講義第 40 頁列了各自的優缺點）。<strong>線性核</strong>就是普通內積，
  等於什麼都不做：</p>

  $$K(x_i, x_{{i'}}) = \\sum_{{j=1}}^{{p}} x_{{ij}} x_{{i'j}}$$

  <p><strong>d 次多項式核</strong>（式 9.22）等於在 d 次多項式的空間裡配線性分類器：</p>

  $$K(x_i, x_{{i'}}) = \\left(1 + \\sum_{{j=1}}^{{p}} x_{{ij}} x_{{i'j}}\\right)^{{d}}$$

  <p><strong>徑向基核</strong>（radial basis kernel，RBF；式 9.24）用距離而不是內積：</p>

  $$K(x_i, x_{{i'}}) = \\exp\\left(-\\gamma \\sum_{{j=1}}^{{p}}
    \\left(x_{{ij}} - x_{{i'j}}\\right)^2\\right), \\qquad \\gamma > 0$$

  <p>RBF 的行為非常<strong>局部</strong>：如果測試點 $x^*$ 離訓練點 $x_i$ 很遠，
  那個平方距離很大、指數很小、$K(x^*, x_i)$ 幾乎是 0，於是 $x_i$ 在
  $f(x^*) = \\beta_0 + \\sum_{{i \\in S}} \\alpha_i K(x^*, x_i)$ 裡幾乎沒有發言權。
  <strong>只有附近的訓練點會影響一個測試點的預測。</strong>γ 就是「附近」有多近。</p>

{viz(svg("w10rbfSvg", 420) + "\n" + chart("w10rbfChart", "", "。此圖的重點：γ 從 0.25 加到 50，訓練錯誤率一路掉到 0，但測試錯誤率先降後升——γ = 50 時訓練幾乎完美而測試最差，這就是過度配適。"),
     [info_card("怎麼看",
                '上圖：填色是 RBF 核 SVM 的決策區域（<strong>烘焙的 40×40 格點</strong>），'
                '點是訓練資料。推滑桿掃過四組 (C, γ)。'
                '<strong>看 γ = 50 那一格</strong>：邊界縮成一個個包住單點的小島，'
                '訓練錯誤率是 0。那不是學到了結構，那是把每個點各自圈起來。<br>'
                '下圖：C = 1 固定，γ 從 0.25 掃到 50 的訓練與測試錯誤率。', "圖 9.9"),
      rows_card("這一格的配適",
                [("γ", "—", "w10rbfG"), ("sklearn 的 C", "—", "w10rbfC"),
                 ("支持向量個數", "—", "w10rbfNsv"),
                 ("訓練錯誤率", "—", "w10rbfTr"),
                 ("測試錯誤率", "—", "w10rbfTe"),
                 ("這一組的出處", "—", "w10rbfWhy")]),
      info_card("交叉驗證選出來的是哪一組",
                'lab 儲存格 67 用 5 折交叉驗證掃 C ∈ {0.1, 1, 10, 100, 1000} × '
                'γ ∈ {0.5, 1, 2, 3, 4}，選出 <strong>C = 1、γ = 0.5</strong>，'
                '測試錯誤率 <strong>12%</strong>（儲存格 69 的混淆矩陣 69／6／6／19）。'
                '滑桿最左邊那一格就是它。', "BAKED"),
      info_card("γ 也是一個正則化參數",
                '講義第 26 頁：<strong>「γ 也是一個正則化參數，過度配適時應該把它調小」</strong>。'
                'γ 小 → 每個支持向量的影響範圍大 → 邊界平滑 → 偏差大變異小；'
                'γ 大 → 影響範圍小 → 邊界破碎 → 偏差小變異大。'
                '它跟 C 要<strong>一起</strong>用網格搜尋調，因為兩者都在控制彈性。')],
     "w10rbfStatus", "推滑桿掃過四組 (C, γ)，看決策區域從平滑變成一堆小島。",
     slider("w10rbfSl", "組合", 0, 3, 1, 0, "w10rbfDraw()", "w10rbfSlV", "γ = 0.5, C = 1",
            basis="1 1 300px", vw=104, lw=30))}

  <h3 id="dx-rbf">講義完整實作：RBF 核 SVM</h3>
{card("lab 09 · 非線性邊界的資料 + RBF 核", lab_code(CH, 57) + "\n\n" + lab_code(CH, 61),
      lab_output(CH, 61), src=src("57、61"), out_tag="預期輸出（儲存格 61）",
      note="200 筆資料分成三塊：前 100 筆整體 +2、第 101–150 筆整體 −2、"
           "剩下 50 筆留在原地，標籤是 <code>[1]*150 + [2]*50</code>，"
           "所以第 2 類被第 1 類從兩邊夾住，邊界必然是非線性的。"
           "上面那張圖用的就是這 100 筆訓練資料（<code>test_size=0.5</code>）。")}

{card("lab 09 · 同時調 C 與 γ", lab_code(CH, 67), lab_output(CH, 67),
      src=src("67、69"), out_tag="預期輸出（儲存格 67）",
      note="25 組組合裡最好的是 <strong>C = 1、γ = 0.5</strong>。"
           "lab 的補充很重要：<strong>「儘管其他幾個值也達到相同的值」</strong>——"
           "網格搜尋常常有一片平原，別把 <code>best_params_</code> 當成唯一正確答案。"
           "接著儲存格 69 用它預測測試集，混淆矩陣是 69／6／6／19，錯誤率 12%。"
           "順帶一提，ISLP 書上印的 <code>Out[24]</code> 是 "
           "<code>{'C': 100, 'gamma': 1}</code>，跟 lab 實跑不同。"
           "這正是「平原上任選一點」的具體證據。")}

{qa("觀念釐清", [
    ("Q：核技巧「不用真的升維」到底是什麼意思？它省掉了什麼？",
     "<p>省掉的是<strong>把 Φ(x) 算出來、存起來、在高維空間裡做運算</strong>這三件事。</p>"
     "<p>具體看講義第 24 頁那個例子。要做二次擴張，笨方法是：對每一筆資料算出三維向量 "
     "$\\Phi(x) = (\\sqrt2 x_1x_2, x_1^2, x_2^2)$，存成一個 n × 3 的矩陣，再在三維空間裡配 SVC。"
     "核方法是：完全不動原始的 n × 2 資料，需要內積的時候就算 $(x_i^\\top x_{i'})^2$。"
     "兩者的答案<strong>數學上完全相同</strong>（lab 儲存格 53 實測都是 1.0），"
     "但後者永遠留在二維。</p>"
     "<p>二維變三維省不了多少。但 p = 100 做到 d = 3 是 17 萬多維，"
     "而 RBF 核對應的特徵空間是<strong>無限維</strong>的（講義第 26 頁：由 Mercer 定理，"
     "確切的 Φ 無法明確寫出）。ISLP 說得很白：那個空間大到「我們本來也不可能在那裡做計算」。"
     "核方法讓你使用那個空間，卻永遠不必進去。</p>"
     "<p>要付的代價是：你拿不到 β 了。線性核可以印 <code>coef_</code> 看哪個變數重要，"
     "RBF 核只有 $\\alpha_i$ 與支持向量。講義第 40 頁把這列成高斯核的缺點："
     "<strong>「神祕（沒有 w）」</strong>。可解讀性換來了彈性。</p>"),
])}

{quiz("qKern", "QUIZ · 核技巧",
      "用 RBF 核的 SVM 時，把 γ 從 0.5 調到 50，決策邊界會怎麼變？",
      [(True, "邊界從平滑的曲線變成一個個包住訓練點的小島，訓練誤差趨近 0 但測試誤差變差",
        "對。γ 大 → 每個支持向量的影響半徑小 → 只有貼著它的地方會被判成它的類別。"
        "上面元件的第四格（γ = 50）就是這個樣子，"
        "而下面的曲線顯示測試錯誤率在 γ 很大時反而上升。ISLP 圖 9.10／9.11 講的是同一件事。"),
       (False, "邊界會變得更平滑，因為 γ 是核的平滑參數",
        "方向反了。γ 出現在 exp(−γ·距離²) 的指數上，<strong>γ 愈大衰減愈快</strong>、"
        "影響範圍愈小、邊界愈破碎。要平滑就把 γ 調小。講義第 26 頁：「過度配適時應該把它調小」。"),
       (False, "邊界不變，只有支持向量的個數會變，因為 γ 只影響核值的大小",
        "不對。決策函數是 f(x) = β₀ + Σ αᵢ K(x, xᵢ)，K 的形狀變了 f 就變了，"
        "邊界 f(x) = 0 當然跟著變。γ 不是縮放常數，它改變的是「相似度隨距離衰減的速度」。")])}
"""

# ── P05 multiclass ────────────────────────────────────────────────────
BODIES["multiclass"] = f"""
  <p>到這裡整章都在講兩類。K &gt; 2 怎麼辦？ISLP §9.4 的答案有點掃興：
  <strong>分離超平面這個概念本身沒辦法自然地推廣到多類別</strong>。
  很多人提過各種做法，但實務上活下來的只有兩個，而且都是「把多類別問題拆成一堆兩類問題」。</p>

  <p><strong>一對一</strong>（one-versus-one，OVO，也叫 all-pairs）：配
  $\\binom{{K}}{{2}} = K(K-1)/2$ 個分類器，每個只比較<strong>兩個</strong>類別
  （第 k 類編成 +1、第 k′ 類編成 −1，其餘資料完全不用）。
  測試點交給每一個分類器投一票，<strong>得票最多的類別勝出</strong>。</p>

  <p><strong>一對其餘</strong>（one-versus-all，OVA，也叫 one-versus-rest）：配 K 個分類器，
  第 k 個把第 k 類編成 +1、<strong>其餘 K − 1 類全部</strong>編成 −1。
  測試點指派給 $f_k(x^*) = \\beta_{{0k}} + \\beta_{{1k}}x_1^* + \\cdots + \\beta_{{pk}}x_p^*$
  <strong>最大</strong>的那一類，因為那代表最有信心。</p>

{info("兩個關鍵差別", '''<strong>① 分類器的個數：</strong>OVO 是 K(K−1)/2，OVA 是 K。
  K = 3 時兩者都是 3（所以下面的元件看不到個數差別）；K = 10 時是 <strong>45 對 10</strong>。<br>
  <strong>② 每個分類器看到什麼：</strong>OVO 的每個分類器只吃兩類的資料，
  問題小、類別平衡、通常分得開。OVA 的每個分類器要面對一個把好幾類混在一起的
  「其餘」——樣本不平衡，而且那一團的形狀可能根本不是一片超平面切得開的。<br>
  ISLP 的建議：<strong>K 不太大就用 OVO</strong>（講義第 29 頁同樣的結論）。''')}

{viz(svg("w10ovoSvg", 410),
     [info_card("怎麼玩",
                '三類資料，按前兩個按鈕切換 OVO 與 OVA：填色是決策區域，'
                '三條虛線是那三個分類器的邊界。K = 3 時兩邊都是 3 個分類器，'
                '所以<strong>要看的不是個數，是它們把平面切成什麼形狀</strong>。<br>'
                '按<strong>「疊上不一致」</strong>會用橘色蓋住兩種規則答案不同的格子。'
                '那些地方一個測試點的預測類別會因為你選 OVO 還是 OVA 而改變。'),
      rows_card("目前的設定",
                [("方法", "—", "w10ovoMode"),
                 ("要訓練幾個分類器", "—", "w10ovoNclf"),
                 ("每個分類器用多少資料", "—", "w10ovoNdata"),
                 ("決策規則", "—", "w10ovoRule"),
                 ("兩種規則不一致的格子", "—", "w10ovoDiffN"),
                 ("OVO 三票平手的格子", "—", "w10ovoAmbN")]),
      info_card("K 變大以後要訓練幾個",
                '<table style="width:100%;font-size:.78rem;border-collapse:collapse;">'
                '<tr><td style="padding:2px 0;">K</td><td>OVO</td><td>OVA</td></tr>'
                '<tr><td style="padding:2px 0;">3</td><td>3</td><td>3</td></tr>'
                '<tr><td style="padding:2px 0;">4</td><td>6</td><td>4</td></tr>'
                '<tr><td style="padding:2px 0;">10</td><td>45</td><td>10</td></tr>'
                '<tr><td style="padding:2px 0;">100</td><td>4950</td><td>100</td></tr></table>'
                'OVO 是 K 的平方級。但 OVO 的每個問題都小得多，'
                '總計算量常常還是它划算。', "HYBRID")],
     "w10ovoStatus", "按按鈕切換 OVO 與 OVA，看兩種規則把平面切成什麼形狀。",
     '<button class="btn btn-toggle" onclick="w10ovoSetMode(\'ovo\')">一對一（OVO · 投票）</button>'
     '<button class="btn btn-toggle" onclick="w10ovoSetMode(\'ova\')">一對其餘（OVA · 取最大）</button>'
     '<button class="btn btn-play" onclick="w10ovoToggleDiff()">疊上不一致</button>')}

  <p>兩件事值得看清楚。第一，<strong>兩種規則真的會給出不同答案</strong>：
  在這組資料上，格點裡大約 7% 的位置，一個測試點的預測類別會因為你選 OVO 還是 OVA 而改變。
  差異來自 OVA 的每個分類器都被迫把「其餘兩類」當成一團來切，而 OVO 的每個分類器只處理兩類。</p>

  <p>第二，<strong>OVO 的投票在理論上可能平手</strong>。三個分類器各投一票給不同的類別，
  誰都沒過半，投票規則本身給不出答案。但你在這組資料上看到的平手格子是
  <strong>0 格</strong>：三團分得很開時，三條成對邊界幾乎就是三個間隙的垂直平分線，
  而三角形三邊的垂直平分線會交於同一點（外心），所以平手區幾乎退化成一個點。
  平手要變成真問題，得等到<strong>類別重疊</strong>或 K 變大的時候。
  實作上 <code>libsvm</code> 用 decision_function 的加總去打破平手，
  但那是實作細節，不是投票規則給的答案。</p>

{info("關於 decision_function_shape 的一個常見誤解", '''<code>SVC</code> 的
  <code>decision_function_shape</code> <strong>只改變 <code>decision_function()</code>
  輸出的形狀，不改變底層的訓練方式</strong>。<code>libsvm</code> 一律用 OVO 訓練
  K(K−1)/2 個分類器；設成 <code>'ovr'</code> 時 sklearn 是把 OVO 的結果<em>換算</em>成 K 個分數。
  真的想要「訓練 K 個一對其餘分類器」，要用 <code>OneVsRestClassifier(SVC(...))</code> 包起來。
  上面元件的 OVA 那三條線就是這樣配出來的。''', "warm")}

  <p>元件裡的三條線都是<strong>真的</strong> <code>SVC(kernel='linear', C=1)</code> 配適結果
  （OVO 的三個只吃兩類的資料、OVA 的三個吃全部資料），係數烘焙進頁面；
  <strong>投票與取最大則由前端在格點上即時算</strong>，所以切換是瞬間的。
  資料是另外造的三團 blob，沒有沿用 lab 儲存格 82 那一組。那組是環狀的非線性結構，
  線性的成對配適在上面沒有意義（lab 自己用的也是 RBF 核）。</p>

{table(["", "一對一（OVO）", "一對其餘（OVA）"],
       [["分類器個數", "K(K−1)/2", "K"],
        ["每個分類器的訓練資料", "只用相關的兩類", "全部 n 筆"],
        ["類別平衡", "好（兩類各自的量）", "差（1 對 K−1）"],
        ["決策規則", "投票，最多票者勝", "取 f_k(x*) 最大者"],
        ["模糊情形", "可能平手（票數相同）", "可能兩個 f 都很小"],
        ["sklearn 的設定",
         "<code>decision_function_shape='ovo'</code>", "<code>decision_function_shape='ovr'</code>"],
        ["ISLP 的建議", "<strong>K 不太大就用這個</strong>", "K 很大時考慮"]])}

  <h3 id="dx-khan">講義完整實作：四類的基因表現資料</h3>
{card("lab 09 · Khan 資料（4 類、p = 2308、n = 63）",
      lab_code(CH, 88) + "\n\n" + lab_code(CH, 90) + "\n\n" + lab_code(CH, 92),
      lab_output(CH, 92), src=src("88、90、92"), out_tag="預期輸出（儲存格 92）",
      note="p = 2308 遠大於 n = 63，所以 lab 直接說<strong>「這表示我們應該使用線性核，"
           "因為多項式或徑向基核產生的額外靈活性是不必要的」</strong>——"
           "維度已經夠高了，隨便都找得到分得開的超平面。"
           "訓練混淆矩陣（儲存格 90）完全對角、零訓練誤差，"
           "「這並不令人驚訝」；測試集 20 筆只錯 2 筆。"
           "這一格用的是 <code>SVC</code> 的預設多類別機制，也就是 OVO。"
           "lab 儲存格 84 則用 <code>decision_function_shape='ovo'</code> 明確指定，"
           "在三類的二維資料上把決策區域畫出來。")}

{quiz("qMulti", "QUIZ · 多類別",
      "K = 10 個類別。OVO 與 OVA 各要訓練幾個二元分類器？",
      [(True, "OVO 要 45 個（10×9/2），OVA 要 10 個",
        "對。OVO 是所有配對 C(10,2) = 45，OVA 是每類一個共 10 個。"
        "不過分類器多不等於慢：OVO 的每個問題只用兩類的資料，"
        "所以總計算量常常還是比 OVA 少。ISLP 對 K 不大的情況建議 OVO。"),
       (False, "兩者都要 10 個，只是決策規則不同（投票 vs 取最大）",
        "決策規則說對了，個數說錯了。OVO 是所有<strong>配對</strong>："
        "1 對 2、1 對 3、…、9 對 10，共 45 個。K = 3 時兩者剛好都是 3，很容易記錯。"),
       (False, "OVO 要 10 個，OVA 要 45 個",
        "反了。<strong>OVA 是「每一類一個」</strong>所以是 K = 10；"
        "OVO 是「每一對一個」所以是 K(K−1)/2 = 45。"
        "從名字記：one-versus-<em>all</em> 一次就把其餘全部處理掉，所以個數少。")])}
"""

# ── P06 vslogit ───────────────────────────────────────────────────────
BODIES["vslogit"] = f"""
  <p>SVM 在 1990 年代中期出場時很轟動：找一片盡量分開資料的超平面、允許少數違反、
  用核擴張特徵空間。這套說法看起來跟邏輯斯迴歸、LDA 完全是兩個世界的東西。
  ISLP §9.5 的任務就是把這個神祕感拆掉。</p>

  <p>拆解的關鍵就是 PART 03 那個式子。支持向量分類器等價於</p>

  $$\\underset{{\\beta}}{{\\text{{minimize}}}} \\left\\{{
    \\underbrace{{\\sum_{{i=1}}^{{n}} \\max\\left[0, 1 - y_i f(x_i)\\right]}}_{{\\text{{hinge loss}}}}
    + \\lambda \\underbrace{{\\sum_{{j=1}}^{{p}} \\beta_j^2}}_{{\\text{{ridge 懲罰}}}} \\right\\}}$$

  <p>而加了 ridge 懲罰的邏輯斯迴歸是</p>

  $$\\underset{{\\beta}}{{\\text{{minimize}}}} \\left\\{{
    \\sum_{{i=1}}^{{n}} \\log\\left(1 + e^{{-y_i f(x_i)}}\\right)
    + \\lambda \\sum_{{j=1}}^{{p}} \\beta_j^2 \\right\\}}$$

  <p><strong>只有損失函數換了一項，其他一模一樣。</strong>而 PART 03 的圖顯示這兩個損失
  除了「hinge 在右邊剛好是 0」之外幾乎平行。所以 ISLP 的結論不意外：
  <strong>「邏輯斯迴歸與支持向量分類器常常給出非常相似的結果」</strong>。</p>

{table(["", "支持向量分類器 / SVM", "邏輯斯迴歸", "LDA"],
       [["損失函數", "hinge：max(0, 1 − y·f)", "log(1 + e^(−y·f))", "（不是損失，是概似）"],
        ["在 y·f ≥ 1 時的損失", "<strong>恰好 0</strong>", "很小但 &gt; 0", "—"],
        ["解由誰決定", "<strong>只有支持向量</strong>", "全部資料（遠處權重極小）",
         "各類的平均與共變異"],
        ["機率輸出", "沒有（要另外校準）", "<strong>天生就有</strong>", "有"],
        ["類別分得很開時", "<strong>表現較好</strong>", "係數會發散、不穩定", "表現較好"],
        ["類別重疊很多時", "還可以", "<strong>通常較好</strong>", "還可以"],
        ["非線性邊界", "<strong>核，很成熟</strong>", "可以用核，但少見且較貴", "同左"],
        ["p ≫ n", "線性核 + 正則化，很強", "要正則化", "會退化"]])}

{info("怎麼選？講義第 31 頁的四句話", '''<strong>① 類別（幾乎）可分開時，SVC 比邏輯斯迴歸好，LDA 也好。</strong>
  邏輯斯迴歸在完全可分的資料上會讓係數跑到無限大（最大概似不存在），必須靠懲罰救。<br>
  <strong>② 類別重疊很多時，加了 ridge 懲罰的邏輯斯迴歸與 SVC 非常相似。</strong>
  這時選哪個多半只是習慣問題。<br>
  <strong>③ 想要機率就用邏輯斯迴歸。</strong>SVM 只吐 f(x) 的符號；
  想要機率得再套 Platt scaling（<code>SVC(probability=True)</code>），
  那是額外做一次交叉驗證去配一個 sigmoid，慢而且不見得校準得好。<br>
  <strong>④ 非線性邊界時，核 SVM 是最普及的選擇。</strong>
  但要記得：核不是 SVM 的專利，邏輯斯迴歸與 LDA 也能用核，只是計算比較貴、歷史上比較少人做。''')}

  <p>ISLP 這一節結尾還提了一個延伸：<strong>支持向量迴歸</strong>
  （support vector regression）。最小平方法讓每一筆殘差都計入損失；
  支持向量迴歸<strong>只讓絕對值超過某個正常數的殘差計入</strong>——
  等於把 margin 的概念搬到迴歸，落在「管子」裡的點對解沒有貢獻，
  稀疏性因此保留下來。<code>sklearn.svm.SVR</code> 就是它。</p>

  <h3 id="dx-rbfs">講義完整實作：用核近似 + SGD 逼近核 SVM</h3>
{card("lab 09 · RBFSampler + SGDClassifier",
      lab_code(CH, 96) + "\n\n" + lab_code(CH, 97), lab_output(CH, 97),
      src=src("96、97"), out_tag="預期輸出（儲存格 97）",
      note="<code>RBFSampler</code> 用隨機傅立葉特徵<strong>近似</strong> RBF 核："
           "它真的把資料映射到一個有限維的空間，讓內積近似 K(x, x′)，"
           "然後就可以用便宜的線性方法（這裡是 hinge loss 的 SGD）。"
           "訓練準確率 <strong>0.84</strong> 比不上真正的 <code>SVC(kernel='rbf')</code>，"
           "但它是 O(n) 的，資料上百萬筆時 <code>SVC</code> 根本跑不動。"
           "講義第 32 頁：<strong>「大規模問題就用 SGDClassifier 配 hinge loss」</strong>。")}

{qa("觀念釐清", [
    ("Q：SVM 與邏輯斯迴歸該選哪一個？",
     "<p>先問一句話：<strong>你要不要機率？</strong>要就選邏輯斯迴歸，討論結束。"
     "風險分數、期望成本決策、要調閾值、要跟別的模型做集成——全部需要校準過的機率，"
     "SVM 給不了（<code>probability=True</code> 是事後貼上去的，還會慢好幾倍）。</p>"
     "<p>不要機率的話，看類別分得多開。<strong>分得很開 → SVM</strong>："
     "邏輯斯迴歸在完全可分的資料上係數會發散，而 SVM 的 margin 概念天生就處理這種情形。"
     "<strong>重疊很多 → 邏輯斯迴歸</strong>：這時 hinge 的稀疏性沒什麼好處，"
     "而邏輯斯迴歸的機率輸出與可解讀性是白拿的。"
     "重疊的中間地帶兩者結果會很像，因為損失函數很像。</p>"
     "<p>另外兩個實務考量。<strong>n 很大</strong>：<code>SVC</code> 是 O(n²)～O(n³) 的，"
     "幾萬筆以上就開始痛，這時用 <code>LinearSVC</code>、<code>SGDClassifier</code> "
     "或邏輯斯迴歸。<strong>要看變數重要度</strong>：線性核的 <code>coef_</code> 可以看，"
     "RBF 核沒有 β 可看（講義第 40 頁列為高斯核的缺點：「神祕」）。</p>"),
    ("Q：既然核不是 SVM 的專利，為什麼「核」幾乎都跟 SVM 一起出現？",
     "<p>ISLP 明確回答了：<strong>「歷史原因」</strong>。任何只透過內積接觸資料的方法都能核化"
     "（核邏輯斯迴歸、核 PCA、核嶺迴歸都存在），但核在 SVM 的脈絡裡遠比在其他地方普及。</p>"
     "<p>不過也有技術上的理由。SVM 的解是<strong>稀疏</strong>的——"
     "只有支持向量的 $\\alpha_i$ 非零，所以預測時只要算 |S| 個核值。"
     "核邏輯斯迴歸沒有這個性質：每一筆訓練資料的權重都非零，"
     "預測一個點要算 n 個核值，訓練還要處理一個 n × n 的核矩陣。"
     "n 稍微大一點就吃不消。<strong>hinge loss 那段「剛好等於 0」，"
     "換來的正是核方法在計算上的可行性。</strong></p>"),
])}

{quiz("qVs", "QUIZ · SVM vs 邏輯斯迴歸",
      "一份資料的兩個類別重疊得相當厲害，而且你需要輸出每一筆的違約機率。該選哪個？",
      [(True, "邏輯斯迴歸（加 ridge 懲罰）：重疊時兩者表現相近，而機率輸出是它天生就有的",
        "對，兩個條件都指向邏輯斯迴歸。ISLP：「in more overlapping regimes, "
        "logistic regression is often preferred」，而 SVM 本來就不提供機率估計"
        "（講義第 4 頁把這列為 SVM 的缺點）。"),
       (False, "SVM 配 RBF 核：它比較有彈性，機率可以用 SVC(probability=True) 拿到",
        "技術上可行但不是好選擇。<code>probability=True</code> 是事後用 Platt scaling "
        "配一個 sigmoid，需要額外的內部交叉驗證（慢好幾倍），而且校準品質不保證。"
        "既然重疊時兩者準確度差不多，何必為了機率繞這一大圈。"),
       (False, "SVM 配線性核：類別重疊正是 hinge loss 的強項，因為它會忽略遠處的點",
        "把強項說反了。<strong>類別分得很開才是 SVM 的強項</strong>；"
        "重疊很厲害時大部分點都變成支持向量，hinge 的稀疏性優勢消失。"
        "而且「忽略遠處的點」在重疊資料上沒什麼可忽略的。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 9.7 第 1 題（a）",
      "課本第 1 題要你畫出超平面 $1 + 3X_1 - X_2 = 0$，並標出兩側。"
      "點 $(0, 0)$ 落在哪一側？",
      [(True, "落在 1 + 3X₁ − X₂ &gt; 0 的那一側，因為代進去得到 1",
        "對。f(0,0) = 1 + 3·0 − 0 = 1 &gt; 0。判斷一個點在哪一側完全不需要畫圖，"
        "代進去看正負號就好。這是 §9.1.1 唯一要記住的操作。"
        "順帶一提，這條線的斜率是 3（把式子改寫成 X₂ = 3X₁ + 1），法向量是 (3, −1)。"),
       (False, "落在線上，因為原點滿足任何過原點的超平面方程式",
        "這條線<strong>不</strong>過原點：β₀ = 1 ≠ 0。"
        "「仿射」（affine）這個詞就是在強調超平面不必通過原點——"
        "只有 β₀ = 0 時才會。"),
       (False, "落在 &lt; 0 的那一側，因為 −X₂ 這一項是負的",
        "不能只看某一項的符號，要把整個 f 算出來。X₂ = 0 時 −X₂ 這一項貢獻 0，"
        "剩下 β₀ = 1 是正的。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 9.7 第 2 題（c）（d）",
      "課本第 2 題的分類器規則是：$(1+X_1)^2 + (2-X_2)^2 > 4$ 判成藍色，否則紅色。"
      "四個點 $(0,0)$、$(-1,1)$、$(2,2)$、$(3,8)$ 分別是什麼顏色？"
      "而 (d) 小題問這個邊界算不算線性——答案是什麼？",
      [(True, "藍、紅、藍、藍；(d) 對 X₁、X₂ 不是線性，但對 X₁、X₁²、X₂、X₂² 是線性的",
        "對。(0,0)：1 + 4 = 5 &gt; 4 → 藍；(−1,1)：0 + 1 = 1 ≤ 4 → 紅；"
        "(2,2)：9 + 0 = 9 &gt; 4 → 藍；(3,8)：16 + 36 = 52 &gt; 4 → 藍。"
        "(d) 把括號展開就看得出來：1 + 2X₁ + X₁² + 4 − 4X₂ + X₂² = 4，"
        "每一項都是那四個特徵的一次式。<strong>這就是特徵擴張的整個想法</strong>。"),
       (False, "藍、紅、藍、藍；(d) 不是線性，因為出現了平方項，所以怎麼看都是非線性的",
        "前半對，後半錯，而且錯在最關鍵的地方。「線性」要問<strong>對誰</strong>線性。"
        "把 X₁² 當成一個<em>新的變數</em> Z₁，邊界就是 Z 的一次式，"
        "所以在放大的特徵空間裡它是一片超平面，只有映射回原空間才是彎的。"
        "整個 §9.3.1 都建立在這個觀點上。"),
       (False, "紅、紅、藍、藍；(d) 對 X₁、X₁²、X₂、X₂² 是線性的",
        "(d) 對了，但 (0,0) 算錯了。(1+0)² + (2−0)² = 1 + 4 = <strong>5</strong>，"
        "大於 4，所以是藍色。這個圓的圓心是 (−1, 2)、半徑 2，而原點到圓心的距離是 √5 ≈ 2.24 &gt; 2，"
        "確實在圓外。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 9.7 第 3 題（e）（f）",
      "課本第 3 題的 7 個點：紅色是 (3,4)、(2,2)、(4,4)、(1,4)，藍色是 (2,1)、(4,3)、(4,1)。"
      "最佳分離超平面是 $X_2 = X_1 - 0.5$。哪幾筆是支持向量？"
      "(f) 小題問「第 7 筆 (4,1) 稍微移動會不會影響超平面」——為什麼？",
      [(True, "支持向量是第 2、3、5、6 筆；第 7 筆不是支持向量，離 margin 很遠，稍微移動不影響",
        "對。把 f(x) = −0.5 + X₁ − X₂ 代進去：第 2 筆 (2,2) 得 −0.5、第 3 筆 (4,4) 得 −0.5、"
        "第 5 筆 (2,1) 得 +0.5、第 6 筆 (4,3) 得 +0.5。這四筆剛好落在 margin 上。"
        "第 7 筆 (4,1) 得 +2.5，遠在 margin 之外；它對應的限制式是鬆的，"
        "移動一小段仍然鬆，最佳解不變。M = 0.5/√2 = 1/(2√2) ≈ 0.354。"),
       (False, "支持向量是全部 7 筆，因為最大邊界問題的每一條限制式都要滿足",
        "混淆了「限制式要滿足」與「限制式是緊的」。7 條限制式當然都要滿足，"
        "但只有<strong>取等號</strong>的那幾條在決定解。"
        "第 1 筆 (3,4) 的 f = −1.5、第 4 筆 (1,4) 的 f = −3.5，都遠在 margin 外面，"
        "刪掉它們答案一模一樣。"),
       (False, "支持向量是第 1、4、7 筆（離邊界最遠的那些），第 7 筆移動會影響超平面",
        "完全反了。支持向量是<strong>離邊界最近</strong>的那些點。它們頂著 margin。"
        "離得最遠的點對解毫無影響，這正是 (f) 小題要你論證的事。"
        "本頁 PART 01 的元件可以直接拖點驗證。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 9.7 第 6 題",
      "課本第 6 題要你造一組「剛好可以線性分開」的資料，然後比較大 C 與小 C。"
      "課本的主張是什麼，理由是什麼？（這裡的 C 是 <code>sklearn</code> 的 C）",
      [(True, "小 C（會錯分幾筆訓練資料）在測試資料上可能贏過大 C，因為大 C 的邊界只由極少數點決定、變異大",
        "對，這正是 lab 儲存格 43–49 演示的事：C = 10⁵ 訓練誤差 0 但只有 3 個支持向量；"
        "C = 0.1 訓練誤差同樣 0，卻用了 12 個支持向量、margin 寬得多。"
        "ISLP §9.6.1 的評語是後者「因為數量更多，因此更穩定」，"
        "並說「使用大型測試集的簡單實驗會證實這一點」。"),
       (False, "大 C 一定更好，因為它的訓練誤差是 0，而訓練誤差 0 表示模型完全學會了資料",
        "訓練誤差 0 幾乎從來不是好消息。第 2 章與第 5 章反覆講過這件事。"
        "而且在這一題裡<strong>兩個 C 的訓練誤差都是 0</strong>（lab 儲存格 43 與 47 的混淆矩陣一樣），"
        "所以訓練誤差根本無法用來區分它們。這正是要看交叉驗證與測試誤差的理由。"),
       (False, "兩者測試誤差會一樣，因為資料可以線性分開，最佳超平面唯一",
        "「最大邊界超平面唯一」是對的，但小 C 配出來的<strong>不是</strong>最大邊界超平面。"
        "它願意犧牲那幾個貼著邊界的點去換更寬的 margin，方向會不一樣。"
        "兩個不同的超平面，測試誤差沒有理由相同。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>三個層次：一次看清楚它們的差別</h3>
{table(["", "最大邊界分類器", "支持向量分類器", "支持向量機（SVM）"],
       [["ISLP 節次", "§9.1.3–9.1.4", "§9.2", "§9.3"],
        ["資料要可分開嗎", "<strong>要</strong>，不可分就沒有解", "不用", "不用"],
        ["邊界形狀", "直的", "直的", "<strong>可以彎</strong>"],
        ["允許違反 margin", "不允許", "允許（用 C 控制）", "允許"],
        ["調整參數", "沒有", "C", "C ＋ 核的參數（d 或 γ）"],
        ["解由誰決定", "支持向量", "支持向量", "支持向量"],
        ["sklearn", "<code>SVC(kernel='linear', C=1e5)</code>",
         "<code>SVC(kernel='linear', C=…)</code>",
         "<code>SVC(kernel='rbf'/'poly', …)</code>"]])}

  <h3>三種核</h3>
{table(["核", "式子", "調的參數", "優點", "缺點"],
       [["線性", "Σⱼ xᵢⱼxᵢ′ⱼ", "只有 C",
         "快、可以看 coef_、不易過度配適；p ≫ n 的首選", "邊界只能是直的"],
        ["d 次多項式", "(1 + Σⱼ xᵢⱼxᵢ′ⱼ)^d", "C、d",
         "比線性有彈性，d 的意義很具體", "d 大時數值不穩；實務只用小 d"],
        ["徑向基（RBF）", "exp(−γ Σⱼ (xᵢⱼ−xᵢ′ⱼ)²)", "C、γ",
         "最有彈性、有界（數值穩）、只有一個核參數",
         "沒有 β 可解讀、比線性慢、容易過度配適"]])}

  <h3>lab 上的實測數字（全部逐字取自 <code>Ch09-svm-lab-zh.ipynb</code>）</h3>
{table(["情境", "設定", "支持向量", "結果", "出處"],
       [["50 筆·不可分開", "C = 10", "29（15 + 14）", "coef_ = [1.173, 0.773]", "儲存格 22、23、29"],
        ["50 筆·不可分開", "C = 0.1", "36（18 + 18）", "margin 更寬", "儲存格 27"],
        ["50 筆·不可分開", "CV 選 C", "—",
         "best C = 1，準確率 0.74", "儲存格 31、33"],
        ["50 筆·不可分開", "C = 1（測試）", "—", "70% 正確（8 + 6 / 20）", "儲存格 37"],
        ["50 筆·不可分開", "C = 0.001（測試）", "—", "60% 正確", "儲存格 39"],
        ["50 筆·可分開", "C = 10⁵", "<strong>3</strong>", "訓練誤差 0，margin 極窄", "儲存格 43–46"],
        ["50 筆·可分開", "C = 0.1", "<strong>12</strong>", "訓練誤差 0，margin 寬得多", "儲存格 47、48"],
        ["同心圓 100 筆", "二次核", "—", "訓練準確率 1.0", "儲存格 52、53"],
        ["200 筆·非線性", "RBF, CV 選 C 與 γ", "—",
         "best C = 1、γ = 0.5，測試錯誤 12%", "儲存格 67、69"],
        ["Khan（4 類）", "線性核, C = 10", "—",
         "訓練誤差 0；測試 20 筆錯 2 筆", "儲存格 88、90、92"],
        ["200 筆·核近似", "RBFSampler + SGD", "—", "訓練準確率 0.84", "儲存格 97"]])}

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["超平面", "$\\beta_0 + \\beta^{\\top}X = 0$", "式 9.1–9.2"],
        ["點到超平面的距離", "$|f(x)| / \\lVert\\beta\\rVert$", "講義第 6 頁"],
        ["分離超平面的條件", "$y_i f(x_i) > 0 \\;\\forall i$", "式 9.8"],
        ["最大邊界", "max M s.t. $\\sum\\beta_j^2=1$, $y_i f(x_i) \\ge M$", "式 9.9–9.11"],
        ["軟邊界", "多了 $y_i f(x_i) \\ge M(1-\\epsilon_i)$, $\\sum\\epsilon_i \\le C$",
         "式 9.12–9.15"],
        ["對偶問題",
         "max $\\sum_i\\alpha_i - \\frac12\\sum_i\\sum_{i'}\\alpha_i\\alpha_{i'}y_iy_{i'}"
         "\\langle x_i,x_{i'}\\rangle$", "講義第 17–18 頁；只出現內積"],
        ["線性核的解", "$f(x) = \\beta_0 + \\sum_{i \\in S}\\alpha_i\\langle x,x_i\\rangle$",
         "式 9.19；S 是支持向量的索引集"],
        ["核化的解", "$f(x) = \\beta_0 + \\sum_{i \\in S}\\alpha_i K(x,x_i)$", "式 9.23"],
        ["多項式核", "$\\left(1+\\sum_j x_{ij}x_{i'j}\\right)^{d}$", "式 9.22"],
        ["徑向基核", "$\\exp\\left(-\\gamma\\sum_j (x_{ij}-x_{i'j})^2\\right)$", "式 9.24"],
        ["損失 + 懲罰",
         "min $\\sum_i \\max[0, 1-y_if(x_i)] + \\lambda\\sum_j\\beta_j^2$",
         "式 9.25–9.26；λ 大 ↔ 預算 C 大"]])}

{info("三個一定要記住的觀念", '''<strong>1. 解只依賴支持向量。</strong>
  嚴格待在 margin 正確一側的點對答案毫無貢獻，因為 hinge loss 在那裡恰好是 0。
  這給了 SVM 對遠處離群值的穩健性，也給了核方法計算上的可行性。<br>
  <strong>2. ISLP 的 C 與 scikit-learn 的 C 方向相反。</strong>
  ISLP 的 C 是違反量的<strong>預算</strong>（C 大 → margin 寬）；
  sklearn 的 C 是違反的<strong>懲罰</strong>（C 大 → margin 窄）。
  講義第 18 頁：兩者成反比。<br>
  <strong>3. 核技巧不是「升維」，是「跳過升維」。</strong>
  演算法只透過內積接觸資料，所以把內積換成 K(x, x′) 就換掉了整個特徵空間，
  而 Φ(x) 從頭到尾不必算出來。RBF 核的特徵空間是無限維的，本來也算不出來。''')}

{info("順手提醒", '''<strong>SVM 一定要先標準化</strong>（講義第 33 頁：演算法不具尺度不變性），
  而且要包進 <code>Pipeline</code> 才不會洩漏。<strong>C 與核參數要一起用網格搜尋調</strong>，
  兩者都在控制彈性。<strong>SVM 不吐機率</strong>，需要機率就用邏輯斯迴歸，
  或接受 <code>probability=True</code> 的額外成本。''', "warm")}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== support_vector_machines 本頁元件（id 與全域一律 w10 前綴）===== */

/* ---------- 共用小工具 ---------- */
/* Sutherland–Hodgman：把多邊形裁成 g(p) >= 0 的那一半。
   半平面填色與 margin 帶都靠它，比自己算交點再排序可靠得多。 */
function w10clipPoly(poly, g) {
  const out = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length], ga = g(a), gb = g(b);
    if (ga >= 0) out.push(a);
    if ((ga >= 0) !== (gb >= 0)) {
      const t = ga / (ga - gb);
      out.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]);
    }
  }
  return out;
}
function w10box(s) {
  return [[s.xd[0], s.yd[0]], [s.xd[1], s.yd[0]], [s.xd[1], s.yd[1]], [s.xd[0], s.yd[1]]];
}
function w10fillPoly(s, poly, fill, g) {
  if (poly.length < 3) return null;
  return s.add('polygon', { points: poly.map(p => s.X(p[0]) + ',' + s.Y(p[1])).join(' '),
                            fill: fill, stroke: 'none' }, g);
}
/* 直線 β0 + β1 x + β2 y = c 在可視範圍內的兩個端點（找不到就回 null） */
function w10lineEnds(s, b0, b1, b2, c) {
  const [x0, x1] = s.xd, [y0, y1] = s.yd, eps = 1e-9, cand = [];
  if (Math.abs(b2) > eps) {
    [x0, x1].forEach(x => {
      const y = (c - b0 - b1 * x) / b2;
      if (y >= y0 - 1e-7 && y <= y1 + 1e-7) cand.push([x, y]);
    });
  }
  if (Math.abs(b1) > eps) {
    [y0, y1].forEach(y => {
      const x = (c - b0 - b2 * y) / b1;
      if (x >= x0 - 1e-7 && x <= x1 + 1e-7) cand.push([x, y]);
    });
  }
  const uniq = [];
  cand.forEach(p => {
    if (!uniq.some(q => Math.abs(q[0] - p[0]) < 1e-6 && Math.abs(q[1] - p[1]) < 1e-6)) uniq.push(p);
  });
  return uniq.length >= 2 ? [uniq[0], uniq[1]] : null;
}
/* 決策區域：rows 是每列一個字串（由上而下），字元對應 fills 的鍵。
   先把「上下相鄰而且完全相同的列」併成一塊，再把「同一列相鄰同色的格子」併成一個
   <rect>（run-length）。40×40 的格點於是只產生幾十個節點而不是 1600 個。
   矩形邊界一定要「剛好接上」並加 shape-rendering="crispEdges"：填色是半透明的 rgba，
   只要重疊一點點就會疊出比較深的接縫（第一版每邊多加 0.6px，畫出一條條橫紋）。 */
function w10gridDraw(s, rows, fills, g) {
  const ny = rows.length, nx = rows[0].length;
  const cw = (s.xd[1] - s.xd[0]) / nx, chh = (s.yd[1] - s.yd[0]) / ny;
  let r = 0;
  while (r < ny) {
    let rEnd = r;
    while (rEnd + 1 < ny && rows[rEnd + 1] === rows[r]) rEnd++;
    const row = rows[r];
    const ya = s.Y(s.yd[1] - r * chh), yb = s.Y(s.yd[1] - (rEnd + 1) * chh);
    let c = 0;
    while (c < nx) {
      let e = c;
      while (e + 1 < nx && row[e + 1] === row[c]) e++;
      const xa = s.X(s.xd[0] + c * cw), xb = s.X(s.xd[0] + (e + 1) * cw);
      s.add('rect', { x: xa, y: ya, width: xb - xa, height: yb - ya,
                      fill: fills[row[c]] || 'none', stroke: 'none',
                      'shape-rendering': 'crispEdges' }, g);
      c = e + 1;
    }
    r = rEnd + 1;
  }
}
const w10CLS = ['var(--pt-a)', 'var(--pt-b)', 'var(--pt-c)'];
const w10REG = ['var(--regionA)', 'var(--regionB)', 'var(--regionC)'];
/* 這一頁有一條反覆踩到的規則：s.dot 預設 class 是 .dot、s.seg 預設是 .resid，
   而 stats.css 的 .viz-svg .dot{stroke:#fff} / .viz-svg .resid{stroke:var(--resid);
   stroke-dasharray:2 2} 是 CSS 宣告，優先權高於呈現屬性。所以只要想自己指定
   stroke 顏色或虛實，就一定要傳一個「CSS 裡沒有的 class」（本頁用 w10 開頭）。

   支持向量的橘色描邊必須畫成「另外一顆圈」，不能靠 s.dot 的 stroke 屬性：
   stats.css 的 .viz-svg .dot{stroke:#fff} 是 CSS 宣告，優先權高於呈現屬性，
   會把橘色蓋回白色（第一次跑 browser_check 的截圖就是這樣才發現的）。 */
function w10ring(s, x, y, r, g) {
  return s.add('circle', { cls: 'w10ring', cx: s.X(x), cy: s.Y(y), r: r,
                           fill: 'none', stroke: 'var(--pt-held)', 'stroke-width': 3 }, g);
}
/* β₀ + β₁X₁ + β₂X₂ = 0 的漂亮寫法（負號直接吃進去，不要印出「+ -0.47」） */
function w10eqStr(b0, b1, b2) {
  const t = (v, name) => (v >= 0 ? ' + ' : ' − ') + HC.fmt(Math.abs(v), 2) + ' ' + name;
  return HC.fmt(b0, 2) + t(b1, 'X₁') + t(b2, 'X₂') + ' = 0';
}

/* ---------- P00 超平面：三個滑桿調 β ---------- */
const w10hyperTest = [[-1.5, 1.2], [1.6, 0.7], [0.4, -1.7]];
const w10hyperNames = ['A', 'B', 'C'];
let w10hyperSvc = null;
function w10hyperSetup() {
  w10hyperSvc = HC.svg('w10hyperSvg', { xd: [-3, 3], yd: [-3, 3], h: 330 });
  w10hyperSvc.grid(6, 6, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
  w10hyperSvc.layer('fill'); w10hyperSvc.layer('line'); w10hyperSvc.layer('pts');
}
function w10hyperReset() {
  $('w10hyperB0').value = '1'; $('w10hyperB1').value = '2'; $('w10hyperB2').value = '3';
  w10hyperDraw();
}
function w10hyperDraw() {
  const s = w10hyperSvc;
  if (!s) return;
  const b0 = parseFloat($('w10hyperB0').value);
  const b1 = parseFloat($('w10hyperB1').value);
  const b2 = parseFloat($('w10hyperB2').value);
  $('w10hyperB0V').textContent = HC.fmt(b0, 1);
  $('w10hyperB1V').textContent = HC.fmt(b1, 1);
  $('w10hyperB2V').textContent = HC.fmt(b2, 1);
  const nrm = Math.hypot(b1, b2);
  const gf = s.clearLayer('fill'), gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  $('w10hyperEq').textContent = w10eqStr(b0, b1, b2);
  $('w10hyperNorm').textContent = nrm < 1e-9 ? '0（沒有超平面）' : HC.fmt(nrm, 3);

  if (nrm > 1e-9) {
    w10fillPoly(s, w10clipPoly(w10box(s), p => b0 + b1 * p[0] + b2 * p[1]),
                'var(--regionA)', gf);
    w10fillPoly(s, w10clipPoly(w10box(s), p => -(b0 + b1 * p[0] + b2 * p[1])),
                'var(--regionB)', gf);
    const e = w10lineEnds(s, b0, b1, b2, 0);
    if (e) s.poly(e, { cls: 'fit', sw: 3 }, gl);
    /* 法向量：從離原點最近的線上點沿 β 方向畫一個單位長度 */
    const t0 = -b0 / (nrm * nrm), fx = t0 * b1, fy = t0 * b2;
    const ux = b1 / nrm, uy = b2 / nrm;
    if (Math.abs(fx) < 2.7 && Math.abs(fy) < 2.7) {
      s.seg(fx, fy, fx + ux, fy + uy,
            { cls: 'w10norm', stroke: 'var(--fit-true)', sw: 3 }, gl);
      s.dot(fx, fy, { r: 3.4, fill: 'var(--fit-true)' }, gl);
      s.txt(fx + ux, fy + uy, 'β', { dy: -8, fill: 'var(--fit-true)' }, gl);
    }
  }
  w10hyperTest.forEach((p, i) => {
    const f = b0 + b1 * p[0] + b2 * p[1];
    s.dot(p[0], p[1], { r: 7, fill: nrm < 1e-9 ? 'var(--muted)' : (f >= 0 ? w10CLS[0] : w10CLS[1]),
                        stroke: '#fff', sw: 1.8 }, gp);
    s.txt(p[0], p[1], w10hyperNames[i] + ' · f = ' + HC.fmt(f, 2), { dy: -13 }, gp);
    const d = nrm < 1e-9 ? NaN : Math.abs(f) / nrm;
    $('w10hyperP' + w10hyperNames[i]).textContent =
      HC.fmt(f, 2) + ' ｜ ' + (nrm < 1e-9 ? '—' : HC.fmt(d, 3));
  });
  if (nrm < 1e-9) {
    setStatus('w10hyperStatus', 'β₁ 與 β₂ 同時是 0：方程式退化成 β₀ = 0，'
      + '<b>根本沒有超平面</b>。把任一個滑桿推離 0 就回來了。');
  } else {
    setStatus('w10hyperStatus', '‖β‖ = ' + HC.fmt(nrm, 3)
      + '。藍區是 f(x) 為正、紅區是 f(x) 為負。'
      + 'A 點的 f = ' + HC.fmt(b0 + b1 * w10hyperTest[0][0] + b2 * w10hyperTest[0][1], 2)
      + '，除以 ‖β‖ 之後的距離是 '
      + HC.fmt(Math.abs(b0 + b1 * w10hyperTest[0][0] + b2 * w10hyperTest[0][1]) / nrm, 3)
      + '。把三個係數同時加倍：f 變兩倍，距離不變。');
  }
}

/* ---------- P01 最大邊界：拖點 + 即時解 ---------- */
/* 初始位置刻意調成「A 類的一條邊對上 B 類的一個頂點」→ 恰好 3 個支持向量，
   跟 ISLP 圖 9.3 的兩藍一紫同構；最近的非支持向量還有 35% 的餘裕，看得出差別。 */
const w10marginA0 = [[2.0, 6.6], [3.4, 8.6], [1.3, 4.4], [4.5, 7.0], [2.4, 9.4]];
const w10marginB0 = [[6.1, 3.3], [9.4, 5.1], [5.6, 1.2], [7.6, 3.6], [8.9, 1.9]];
let w10marginA = [], w10marginB = [], w10marginSvc = null;
let w10marginDots = [], w10marginPick = null, w10marginHull = false;

/* 兩類凸包的最近點對。候選＝點對點、點對(任兩點連成的線段)——
   任兩點的連線都在凸包內，所以候選的距離永遠 ≥ 真正的凸包距離，
   取全部候選的最小值就剛好是凸包距離，不必先算凸包。 */
function w10marginSolve(A, B) {
  let best = null;
  const consider = (u, v) => {
    const d = Math.hypot(v[0] - u[0], v[1] - u[1]);
    if (d > 1e-9 && (!best || d < best.d)) best = { u: u, v: v, d: d };
  };
  const proj = (p, a, b) => {
    const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
    if (L < 1e-12) return [a[0], a[1]];
    let t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L;
    t = Math.max(0, Math.min(1, t));
    return [a[0] + t * dx, a[1] + t * dy];
  };
  for (const a of A) for (const b of B) consider(a, b);
  for (const a of A) {
    for (let i = 0; i < B.length; i++) {
      for (let j = i + 1; j < B.length; j++) consider(a, proj(a, B[i], B[j]));
    }
  }
  for (const b of B) {
    for (let i = 0; i < A.length; i++) {
      for (let j = i + 1; j < A.length; j++) consider(proj(b, A[i], A[j]), b);
    }
  }
  if (!best) return { ok: false };
  const wx = best.v[0] - best.u[0], wy = best.v[1] - best.u[1], nrm = best.d;
  const mx = (best.u[0] + best.v[0]) / 2, my = (best.u[1] + best.v[1]) / 2;
  /* f(x) = w·(x − m)/‖w‖：B 類為正、A 類為負，支持向量的 |f| 恰好是 half */
  const f = p => ((p[0] - mx) * wx + (p[1] - my) * wy) / nrm;
  const half = best.d / 2, tol = 1e-6;
  let ok = true;
  A.forEach(p => { if (f(p) > -half + tol) ok = false; });
  B.forEach(p => { if (f(p) < half - tol) ok = false; });
  return { ok: ok, f: f, half: half, mx: mx, my: my, wx: wx, wy: wy, nrm: nrm };
}
function w10marginHullOf(P) {
  const pts = P.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (pts.length < 3) return pts;
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lower = [], upper = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  for (let i = pts.length - 1; i >= 0; i--) {
    const p = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop();
    upper.push(p);
  }
  return lower.slice(0, -1).concat(upper.slice(0, -1));
}
function w10marginSetup() {
  w10marginSvc = HC.svg('w10marginSvg', { xd: [0, 10], yd: [0, 10], h: 430 });
  const s = w10marginSvc;
  s.grid(5, 5, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
  s.layer('band'); s.layer('hull'); s.layer('line'); s.layer('pts');
  /* 先挑「離按下位置最近的點」，再讓 HC.drag 處理 pointer 事件與夾定義域。
     這個 listener 必須比 HC.drag 的先註冊才會先跑。 */
  s.el.addEventListener('pointerdown', function (ev) {
    const p = s.toData(ev);
    let best = null, bd = 1e9;
    [['A', w10marginA], ['B', w10marginB]].forEach(([k, arr]) => {
      arr.forEach((q, i) => {
        const dx = (p.x - q[0]) / 10, dy = (p.y - q[1]) / 10, d2 = dx * dx + dy * dy;
        if (d2 < bd) { bd = d2; best = { k: k, i: i }; }
      });
    });
    w10marginPick = Math.sqrt(bd) < 0.08 ? best : null;
  });
  HC.drag(s.el, s, function (m) {
    if (!w10marginPick) return;
    const arr = w10marginPick.k === 'A' ? w10marginA : w10marginB;
    arr[w10marginPick.i] = [Math.round(m.x * 20) / 20, Math.round(m.y * 20) / 20];
    w10marginRender();
  });
}
function w10marginReset() {
  w10marginA = w10marginA0.map(p => p.slice());
  w10marginB = w10marginB0.map(p => p.slice());
  w10marginPick = null;
  w10marginRender();
}
function w10marginToggleHull() { w10marginHull = !w10marginHull; w10marginRender(); }
function w10marginRender() {
  const s = w10marginSvc;
  if (!s) return;
  const gb = s.clearLayer('band'), gh = s.clearLayer('hull');
  const gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  const sol = w10marginSolve(w10marginA, w10marginB);
  let nsv = 0;
  const isSv = p => sol.ok && Math.abs(sol.f(p)) <= sol.half + 1e-4;

  if (w10marginHull) {
    [[w10marginA, 0], [w10marginB, 1]].forEach(([arr, k]) => {
      const h = w10marginHullOf(arr);
      if (h.length >= 3) {
        w10fillPoly(s, h, w10REG[k], gh);
        s.poly(h.concat([h[0]]), { cls: 'w10hull', stroke: w10CLS[k], sw: 1.8, dash: '5 4' }, gh);
      }
    });
  }
  if (sol.ok) {
    /* margin 帶：把可視矩形先裁 f >= −half 再裁 f <= +half */
    let poly = w10clipPoly(w10box(s), p => sol.f(p) + sol.half);
    poly = w10clipPoly(poly, p => sol.half - sol.f(p));
    w10fillPoly(s, poly, 'var(--band)', gb);
    /* 邊界與兩條 margin 線：f(x) = 0, ±half。f 是 (w·(x−m))/‖w‖ 的形式，
       換算成 b0 + b1 x + b2 y 的係數： */
    const b1 = sol.wx / sol.nrm, b2 = sol.wy / sol.nrm;
    const b0 = -(sol.mx * b1 + sol.my * b2);
    [[0, 'fit', 3], [sol.half, 'truef', 1.8], [-sol.half, 'truef', 1.8]].forEach(([c, cls, sw]) => {
      const e = w10lineEnds(s, b0, b1, b2, c);
      if (e) s.poly(e, { cls: cls, sw: sw }, gl);
    });
    s.seg(sol.mx - b1 * sol.half, sol.my - b2 * sol.half,
          sol.mx + b1 * sol.half, sol.my + b2 * sol.half,
          { cls: 'w10link', stroke: 'var(--resid)', sw: 3 }, gl);
    $('w10marginM').textContent = HC.fmt(sol.half, 3);
    $('w10marginW').textContent = HC.fmt(2 * sol.half, 3);
    $('w10marginEq').textContent = w10eqStr(b0, b1, b2);
  } else {
    $('w10marginM').textContent = '不存在';
    $('w10marginW').textContent = '不存在';
    $('w10marginEq').textContent = '兩類的凸包重疊了';
  }
  [[w10marginA, 0], [w10marginB, 1]].forEach(([arr, k]) => {
    arr.forEach(p => {
      const sv = isSv(p);
      if (sv) { nsv++; w10ring(s, p[0], p[1], 10, gp); }
      s.dot(p[0], p[1], { cls: 'dot drag', r: sv ? 6.8 : 6, fill: w10CLS[k] }, gp);
    });
  });
  $('w10marginNsv').textContent = sol.ok ? String(nsv) : '—';
  if (sol.ok) {
    setStatus('w10marginStatus', 'margin 半寬 M = <b>' + HC.fmt(sol.half, 3)
      + '</b>，支持向量 <b>' + nsv + '</b> 個（橘色描邊）。'
      + '紫色線段就是兩類凸包的最近點對，紅線是它的垂直平分線。'
      + '試著拖一個沒描邊的點——只要不越過虛線，紅線不會動。');
  } else {
    setStatus('w10marginStatus', '<b>這兩類分不開了</b>：凸包已經重疊，'
      + '不存在任何分離超平面，最大邊界問題沒有 M &gt; 0 的解。'
      + '這正是下一節要用軟邊界處理的情形。把點拖回去或按重置。');
  }
}

/* ---------- P02 軟邊界：烘焙的 C 掃描 ---------- */
let w10softSet = 'nonsep', w10softSvc = null;
function w10softSetup() {
  w10softSvc = HC.svg('w10softSvg', { h: 360 });
  w10softSvc.layer('band'); w10softSvc.layer('line'); w10softSvc.layer('pts');
}
function w10softSetData() {
  w10softSet = $('w10softSel').value;
  w10softDraw();
  HC.ready(() => w10softChart());
}
function w10softDraw() {
  const s = w10softSvc;
  if (!s) return;
  const D = FRAMES_w10soft[w10softSet];
  const cs = w10softSet === 'nonsep' ? FRAMES_w10soft.csNonsep : FRAMES_w10soft.csSep;
  const i = Math.max(0, Math.min(cs.length - 1, parseInt($('w10softSl').value, 10)));
  const fit = D.fits[i];
  $('w10softSlV').textContent = String(cs[i]);
  s.domain([D.bb[0], D.bb[1]], [D.bb[2], D.bb[3]]);
  s.grid(5, 5, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
  const gb = s.clearLayer('band'), gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  const f = p => fit.b0 + fit.b1 * p[0] + fit.b2 * p[1];
  let poly = w10clipPoly(w10box(s), p => f(p) + 1);
  poly = w10clipPoly(poly, p => 1 - f(p));
  w10fillPoly(s, poly, 'var(--band)', gb);
  [[0, 'fit', 3], [1, 'truef', 1.8], [-1, 'truef', 1.8]].forEach(([c, cls, sw]) => {
    const e = w10lineEnds(s, fit.b0, fit.b1, fit.b2, c);
    if (e) s.poly(e, { cls: cls, sw: sw }, gl);
  });
  const svSet = {};
  fit.sv.forEach(k => { svSet[k] = 1; });
  D.pts.forEach((p, k) => {
    const yf = (p[2] > 0 ? 1 : -1) * f(p);
    const sv = svSet[k] === 1;
    if (yf < 0) {
      const r = 5.4;
      s.add('rect', { x: s.X(p[0]) - r, y: s.Y(p[1]) - r, width: 2 * r, height: 2 * r,
                      fill: p[2] > 0 ? w10CLS[1] : w10CLS[0], stroke: 'var(--pt-held)',
                      'stroke-width': 2.8 }, gp);
    } else {
      if (sv) w10ring(s, p[0], p[1], 7.6, gp);
      s.dot(p[0], p[1], { r: sv ? 4.8 : 4.4, fill: p[2] > 0 ? w10CLS[1] : w10CLS[0] }, gp);
    }
  });
  $('w10softC').textContent = String(cs[i]);
  $('w10softBudget').textContent = cs[i] <= 0.01 ? '很大的預算（幾乎不罰）'
    : (cs[i] >= 1000 ? '幾乎沒有預算（硬邊界）' : '中等的預算');
  $('w10softM').textContent = HC.fmt(fit.margin, 4);
  $('w10softNsv').textContent = fit.nsv + ' / ' + D.pts.length
    + '（' + fit.nsvEach.join(' + ') + '）';
  $('w10softViol').textContent = String(fit.nViol);
  $('w10softWrong').textContent = String(fit.nWrong);
  const c = HC.get('w10softChart');
  HC.refs(c, [HC.vline(i, 'C = ' + cs[i])]);
  setStatus('w10softStatus', 'sklearn 的 C = <b>' + cs[i]
    + '</b>：margin 半寬 ' + HC.fmt(fit.margin, 3) + '、支持向量 <b>'
    + fit.nsv + '</b> 個、違反 margin 的點 ' + fit.nViol + ' 個、'
    + '被錯誤分類（方框）' + fit.nWrong + ' 個。'
    + 'C 往右推＝罰得更重＝margin 更窄＝支持向量更少。');
}
function w10softChart() {
  const D = FRAMES_w10soft[w10softSet];
  const cs = w10softSet === 'nonsep' ? FRAMES_w10soft.csNonsep : FRAMES_w10soft.csSep;
  HC.line('w10softChart', {
    labels: cs.map(String),
    datasets: [
      { label: '支持向量個數', data: D.fits.map(f => f.nsv), borderColor: HC.tok.accent2,
        backgroundColor: HC.tok.accent2, borderWidth: 2.6, pointRadius: 4, fill: false },
      { label: '違反 margin 的點', data: D.fits.map(f => f.nViol), borderColor: HC.tok.accent,
        backgroundColor: HC.tok.accent, borderWidth: 2.6, pointRadius: 4,
        borderDash: [6, 4], fill: false },
      { label: '被錯誤分類的點', data: D.fits.map(f => f.nWrong), borderColor: HC.tok.accent3,
        backgroundColor: HC.tok.accent3, borderWidth: 2.2, pointRadius: 3.5,
        borderDash: [2, 3], fill: false },
    ],
  }, {
    scales: { x: { title: { display: true, text: 'sklearn 的 C（左邊罰得輕）' } },
              y: { min: 0, title: { display: true, text: '點數' } } },
  });
  const i = parseInt($('w10softSl').value, 10);
  const c = HC.get('w10softChart');
  HC.refs(c, [HC.vline(i, 'C = ' + cs[i])]);
}

/* ---------- P03 Hinge loss vs 邏輯斯 loss ---------- */
let w10lossShow01 = false, w10lossZoom = false;
function w10lossToggle01() { w10lossShow01 = !w10lossShow01; w10lossDraw(); }
function w10lossToggleZoom() { w10lossZoom = !w10lossZoom; w10lossDraw(); }
function w10lossHinge(t) { return Math.max(0, 1 - t); }
function w10lossLogit(t) { return Math.log(1 + Math.exp(-t)); }
function w10lossDraw() {
  const ts = HC.stat.seq(-4, 3, 141);
  const mk = fn => ts.map(t => ({ x: Math.round(t * 1000) / 1000, y: fn(t) }));
  const sets = [
    { label: 'hinge loss：max(0, 1 − y·f)', data: mk(w10lossHinge),
      borderColor: HC.tok.accent3, backgroundColor: HC.tok.accent3,
      borderWidth: 3, pointRadius: 0, fill: false },
    { label: '邏輯斯損失：log(1 + e^(−y·f))', data: mk(w10lossLogit),
      borderColor: HC.tok.accent, backgroundColor: HC.tok.accent,
      borderWidth: 2.6, pointRadius: 0, borderDash: [7, 4], fill: false },
  ];
  if (w10lossShow01) {
    sets.push({ label: '0–1 損失（真正想最小化的）',
                data: mk(t => (t < 0 ? 1 : 0)), borderColor: HC.tok.muted,
                backgroundColor: HC.tok.muted, borderWidth: 2, pointRadius: 0,
                stepped: true, fill: false });
  }
  HC.line('w10lossChart', { datasets: sets }, {
    interaction: { mode: 'nearest', intersect: false },
    scales: {
      x: { type: 'linear', min: -4, max: 3,
           title: { display: true, text: 'y·f(x)：分對是正的，愈大愈篤定' } },
      y: { min: 0, max: w10lossZoom ? 1.6 : 5.2, title: { display: true, text: '損失' } },
    },
  });
  const c = HC.get('w10lossChart');
  HC.refs(c, [HC.vband(1, 3, 'rgba(138,133,120,.16)', 'hinge = 0 的區域'),
                        HC.vline(1, 'y·f = 1（margin）')]);
  $('w10loss2').textContent = 'hinge ' + HC.fmt(w10lossHinge(2), 3)
    + ' ｜ 邏輯斯 ' + HC.fmt(w10lossLogit(2), 3);
  $('w10loss1').textContent = 'hinge ' + HC.fmt(w10lossHinge(1), 3)
    + ' ｜ 邏輯斯 ' + HC.fmt(w10lossLogit(1), 3);
  $('w10loss0').textContent = 'hinge ' + HC.fmt(w10lossHinge(0), 3)
    + ' ｜ 邏輯斯 ' + HC.fmt(w10lossLogit(0), 3);
  $('w10lossN2').textContent = 'hinge ' + HC.fmt(w10lossHinge(-2), 3)
    + ' ｜ 邏輯斯 ' + HC.fmt(w10lossLogit(-2), 3);
  setStatus('w10lossStatus', 'y·f 從 1 往右，hinge 精確等於 0（灰色區帶），'
    + '邏輯斯損失只是變小：y·f = 2 時還有 ' + HC.fmt(w10lossLogit(2), 3)
    + '、y·f = 3 時還有 ' + HC.fmt(w10lossLogit(3), 3) + '。'
    + '「精確等於 0」就是支持向量稀疏性的來源。'
    + (w10lossShow01 ? ' 灰色階梯是 0–1 損失，兩條曲線都是它的凸上界。' : ''));
}

/* ---------- P04 核技巧：一維升維動畫 + 同心圓烘焙 ---------- */
const w10kernThr = 1.15;
const w10kernData = (() => {
  const rand = HC.stat.lcg(910), out = [];
  for (let i = 0; i < 24; i++) {
    const x = -2.45 + 4.9 * (i + 0.5) / 24 + 0.11 * (rand() - 0.5);
    out.push({ x: x, c: Math.abs(x) < w10kernThr ? 1 : 0 });
  }
  return out;
})();
let w10kernMode = 'lift', w10kernSvc = null, w10kernPlayer = null;
function w10kernSetup() {
  w10kernSvc = HC.svg('w10kernSvg', { h: 430 });
  w10kernSvc.layer('grid2'); w10kernSvc.layer('line'); w10kernSvc.layer('pts');
  const F = FRAMES_w10kern;
  $('w10kernInner').textContent = HC.fmt(F.r2.inner[1], 2);
  $('w10kernOuter').textContent = HC.fmt(F.r2.outer[0], 2);
}
function w10kernFrames() {
  const fr = [];
  [0, 0, 0.2, 0.45, 0.7, 0.9, 1].forEach((t, i) => fr.push({ t: t, line: i < 2 ? 1 : 2 }));
  fr.push({ t: 1, showLine: true, line: 3 });
  fr.push({ t: 1, showLine: true, back: true, line: 4 });
  fr.push({ t: 0, showLine: false, back: true, done: true, line: 5 });
  return fr;
}
function w10kernApply(f) {
  const s = w10kernSvc;
  if (!s) return;
  s.domain([-2.9, 2.9], [-1.4, 7.4]);
  s.grid(4, 5, { xtitle: 'x', ytitle: f.t > 0.02 ? 'x²（新的一維）' : '（只有一維）',
                 xdec: 0, ydec: 0 });
  s.clearLayer('grid2');
  const gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  const thr2 = w10kernThr * w10kernThr;
  if (f.back) {
    [[-2.9, -w10kernThr], [w10kernThr, 2.9]].forEach(([a, b]) => {
      w10fillPoly(s, [[a, -1.4], [b, -1.4], [b, 7.4], [a, 7.4]], 'var(--regionA)', gl);
    });
    w10fillPoly(s, [[-w10kernThr, -1.4], [w10kernThr, -1.4], [w10kernThr, 7.4],
                    [-w10kernThr, 7.4]], 'var(--regionB)', gl);
    [-w10kernThr, w10kernThr].forEach(x => {
      s.seg(x, -1.4, x, 7.4, { cls: 'w10thr', stroke: 'var(--fit-line)', sw: 2.6 }, gl);
    });
  }
  if (f.showLine) {
    s.poly([[-2.9, thr2], [2.9, thr2]], { cls: 'fit', sw: 3 }, gl);
    s.txtPx(120, 22, '在二維裡，一條水平線 x² = ' + HC.fmt(thr2, 2) + ' 就分開了',
            { cls: 'axtitle' }, gl);
  }
  s.seg(-2.9, 0, 2.9, 0, { cls: 'w10axis', stroke: 'var(--muted)', sw: 1.6 }, gl);
  w10kernData.forEach(d => {
    s.dot(d.x, f.t * d.x * d.x, { r: 6.4, fill: w10CLS[d.c === 1 ? 1 : 0],
                                  stroke: '#fff', sw: 1.6 }, gp);
  });
  hlLine('w10kernCode', f.line);
  $('w10kernSpace').textContent = f.back ? '映射回一維' : (f.t > 0.02 ? '二維 (x, x²)' : '一維 (x)');
  $('w10kernDim').textContent = f.back ? '1' : (f.t > 0.02 ? '2' : '1');
  $('w10kernSep').textContent = f.t > 0.98 && !f.back ? '可以（一條水平線）'
    : (f.back ? '在原空間是兩個門檻' : '不行');
  $('w10kernNsv').textContent = '—（這一格是示意，不是配適）';
  if (f.back && f.done) {
    setStatus('w10kernSvgStatus', '把二維的那條水平線映射回一維，就變成 x = ±'
      + HC.fmt(w10kernThr, 2) + ' 兩個門檻。'
      + '<b>在原空間看起來「彎」的邊界，在升維後的空間裡只是一片平的超平面。</b>');
  } else if (f.showLine) {
    setStatus('w10kernSvgStatus', '抬到二維之後，兩類在 x² 這一維上完全分開，'
      + '一條水平線就切得乾淨——而且它是<b>線性</b>的。');
  } else if (f.t > 0.02) {
    setStatus('w10kernSvgStatus', '正在把每個點抬到 (x, x²)。'
      + '離原點遠的點被抬得高，靠中間的留在低處，兩類於是在高度上分開了。');
  } else {
    setStatus('w10kernSvgStatus', '一維上紅色被藍色從兩邊夾住：'
      + '任何一個門檻都會切錯一邊。按「開始」看升維怎麼救。');
  }
}
function w10kernCircle() {
  const s = w10kernSvc, F = FRAMES_w10kern;
  if (!s) return;
  if (w10kernPlayer) w10kernPlayer.stop();
  s.domain([F.bb[0], F.bb[1]], [F.bb[2], F.bb[3]]);
  s.grid(4, 4, { xtitle: 'x₁', ytitle: 'x₂', xdec: 1, ydec: 1 });
  const gg = s.clearLayer('grid2'), gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  w10gridDraw(s, F.rows, { '0': w10REG[0], '1': w10REG[1] }, gg);
  s.txtPx(110, 22, '二次核 SVM 的決策區域（烘焙 ' + F.n + '×' + F.n + ' 格點）',
          { cls: 'axtitle' }, gl);
  F.pts.forEach(p => {
    s.dot(p[0], p[1], { r: 5.4, fill: w10CLS[p[2] === 1 ? 1 : 0], stroke: '#fff', sw: 1.2 }, gp);
  });
  hlLine('w10kernCode', 6);
  $('w10kernSpace').textContent = '留在二維，只換核';
  $('w10kernDim').textContent = '2（隱式的 3）';
  $('w10kernSep').textContent = '可以（訓練準確率 ' + HC.fmt(F.accKernel, 2) + '）';
  $('w10kernNsv').textContent = String(F.nsv);
  setStatus('w10kernSvgStatus', 'lab 儲存格 52–54 的同心圓資料。'
    + '用自訂的二次核直接在二維算，訓練準確率 <b>' + HC.fmt(F.accKernel, 2)
    + '</b>，跟「真的升到三維再配線性」的結果一模一樣。'
    + 'Z 空間的超平面係數是 [' + FRAMES_w10kern.w.map(v => HC.fmt(v, 3)).join(', ')
    + ']——後兩項幾乎相等，等於在說「x₁² + x₂² 小的是內圈」。');
}
function w10kernSetMode() {
  w10kernMode = $('w10kernSel').value;
  w10kernReset();
}
function w10kernReset() {
  if (w10kernPlayer) w10kernPlayer.stop();
  if (w10kernMode === 'circle') { w10kernCircle(); return; }
  w10kernPlayer = new Player({ frames: w10kernFrames(), apply: w10kernApply });
  w10kernPlayer.reset();
}
function w10kernStart() {
  if (w10kernMode === 'circle') { w10kernCircle(); return; }
  w10kernPlayer = new Player({ frames: w10kernFrames(), apply: w10kernApply });
  w10kernPlayer.reset();
  w10kernPlayer.play();
}
function w10kernStep() {
  if (w10kernMode === 'circle') { w10kernCircle(); return; }
  if (!w10kernPlayer) w10kernReset();
  w10kernPlayer.step();
}

/* ---------- P04 RBF 的 γ ---------- */
let w10rbfSvc = null;
function w10rbfSetup() {
  const F = FRAMES_w10rbf;
  w10rbfSvc = HC.svg('w10rbfSvg', { xd: [F.bb[0], F.bb[1]], yd: [F.bb[2], F.bb[3]], h: 420 });
  w10rbfSvc.grid(4, 4, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
  w10rbfSvc.layer('grid2'); w10rbfSvc.layer('pts');
}
function w10rbfDraw() {
  const s = w10rbfSvc, F = FRAMES_w10rbf;
  if (!s) return;
  const i = Math.max(0, Math.min(F.frames.length - 1, parseInt($('w10rbfSl').value, 10)));
  const fr = F.frames[i];
  $('w10rbfSlV').textContent = 'γ = ' + fr.gamma + ', C = ' + (fr.C >= 1000 ? '10⁵' : fr.C);
  const gg = s.clearLayer('grid2'), gp = s.clearLayer('pts');
  w10gridDraw(s, fr.rows, { '0': w10REG[0], '1': w10REG[1] }, gg);
  F.trainPts.forEach(p => {
    s.dot(p[0], p[1], { r: 4.8, fill: w10CLS[p[2] === 2 ? 1 : 0], stroke: '#fff', sw: 1.1 }, gp);
  });
  $('w10rbfG').textContent = String(fr.gamma);
  $('w10rbfC').textContent = fr.C >= 1000 ? '100000（幾乎硬邊界）' : String(fr.C);
  $('w10rbfNsv').textContent = fr.nsv + ' / ' + F.trainPts.length;
  $('w10rbfTr').textContent = HC.pct(fr.trainErr, 1);
  $('w10rbfTe').textContent = HC.pct(fr.testErr, 1);
  $('w10rbfWhy').textContent = fr.why;
  setStatus('w10rbfStatus', 'γ = ' + fr.gamma + '、C = ' + (fr.C >= 1000 ? '10⁵' : fr.C)
    + '：訓練錯誤率 <b>' + HC.pct(fr.trainErr, 1) + '</b>、測試錯誤率 <b>'
    + HC.pct(fr.testErr, 1) + '</b>、支持向量 ' + fr.nsv + ' 個。'
    + (fr.gamma >= 50
      ? ' 邊界已經縮成一個個包住單點的小島——訓練幾乎全對，測試最差，這就是過度配適。'
      : (fr.C >= 1000
        ? ' C 拉到極大：邊界變得很不規則，因為它不肯放過任何一個訓練點。'
        : ' 邊界還算平滑，抓到的是資料真正的結構。')));
}
function w10rbfChart() {
  const F = FRAMES_w10rbf.curve;
  HC.line('w10rbfChart', {
    datasets: [
      { label: '訓練錯誤率', data: F.gammas.map((g, i) => ({ x: g, y: F.trainErr[i] })),
        borderColor: HC.tok.accent2, backgroundColor: HC.tok.accent2,
        borderWidth: 2.6, pointRadius: 4, fill: false },
      { label: '測試錯誤率', data: F.gammas.map((g, i) => ({ x: g, y: F.testErr[i] })),
        borderColor: HC.tok.accent, backgroundColor: HC.tok.accent,
        borderWidth: 2.6, pointRadius: 4, borderDash: [6, 4], fill: false },
    ],
  }, {
    interaction: { mode: 'nearest', intersect: false },
    scales: {
      x: { type: 'logarithmic', title: { display: true, text: 'γ（對數刻度）· C = 1 固定' } },
      y: { min: 0, title: { display: true, text: '錯誤率' } },
    },
  });
  const c = HC.get('w10rbfChart');
  HC.refs(c, [HC.hline(Math.min.apply(null, F.testErr), '測試錯誤率的最低點')]);
}

/* ---------- P05 OVO vs OVA ---------- */
let w10ovoMode = 'ovo', w10ovoSvc = null, w10ovoDiff = false;
function w10ovoSetup() {
  const F = FRAMES_w10mc;
  w10ovoSvc = HC.svg('w10ovoSvg', { xd: [F.bb[0], F.bb[1]], yd: [F.bb[2], F.bb[3]], h: 410 });
  w10ovoSvc.grid(4, 4, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
  w10ovoSvc.layer('grid2'); w10ovoSvc.layer('line'); w10ovoSvc.layer('pts');
}
const w10ovoNX = 60, w10ovoNY = 38;
function w10ovoLabel(mode, x, y) {
  const F = FRAMES_w10mc;
  if (mode === 'ova') {
    let best = 0, bv = -1e18;
    F.ova.forEach(o => {
      const f = o.w[0] * x + o.w[1] * y + o.b;
      if (f > bv) { bv = f; best = o.k; }
    });
    return String(best);
  }
  const votes = [0, 0, 0];
  F.ovo.forEach(o => { votes[(o.w[0] * x + o.w[1] * y + o.b) > 0 ? o.hi : o.lo]++; });
  const mx = Math.max(votes[0], votes[1], votes[2]);
  if (votes.filter(v => v === mx).length > 1) return '?';   /* 三票各投一個 → 平手 */
  return String(votes.indexOf(mx));
}
function w10ovoGrid(mode) {
  const F = FRAMES_w10mc, rows = [];
  for (let r = 0; r < w10ovoNY; r++) {
    const y = F.bb[3] - (F.bb[3] - F.bb[2]) * (r + 0.5) / w10ovoNY;
    let line = '';
    for (let c = 0; c < w10ovoNX; c++) {
      line += w10ovoLabel(mode, F.bb[0] + (F.bb[1] - F.bb[0]) * (c + 0.5) / w10ovoNX, y);
    }
    rows.push(line);
  }
  return rows;
}
function w10ovoSetMode(m) { w10ovoMode = m; w10ovoDraw(); }
function w10ovoToggleDiff() { w10ovoDiff = !w10ovoDiff; w10ovoDraw(); }
function w10ovoDraw() {
  const s = w10ovoSvc, F = FRAMES_w10mc;
  if (!s) return;
  const gOvo = w10ovoGrid('ovo'), gOva = w10ovoGrid('ova');
  const rows = w10ovoMode === 'ova' ? gOva : gOvo;
  const diffRows = gOvo.map((row, r) => {
    let out = '';
    for (let c = 0; c < row.length; c++) out += (row[c] === gOva[r][c] ? '.' : 'D');
    return out;
  });
  const nDiff = diffRows.reduce((n, r) => n + (r.split('D').length - 1), 0);
  const nAmb = gOvo.reduce((n, r) => n + (r.split('?').length - 1), 0);
  const nCell = w10ovoNX * w10ovoNY;

  const gg = s.clearLayer('grid2'), gl = s.clearLayer('line'), gp = s.clearLayer('pts');
  w10gridDraw(s, rows, { '0': w10REG[0], '1': w10REG[1], '2': w10REG[2],
                         '?': 'rgba(138,133,120,.34)' }, gg);
  if (w10ovoDiff) {
    w10gridDraw(s, diffRows, { 'D': 'rgba(243,156,18,.40)', '.': 'none' }, gg);
  }
  const clfs = w10ovoMode === 'ova' ? F.ova : F.ovo;
  clfs.forEach(o => {
    const e = w10lineEnds(s, o.b, o.w[0], o.w[1], 0);
    if (e) s.poly(e, { stroke: 'var(--fit-line)', sw: 2.2, dash: '6 4' }, gl);
  });
  F.pts.forEach(p => {
    s.dot(p[0], p[1], { r: 5, fill: w10CLS[p[2]] }, gp);
  });
  $('w10ovoMode').textContent = w10ovoMode === 'ova' ? '一對其餘（OVA）' : '一對一（OVO）';
  $('w10ovoNclf').textContent = w10ovoMode === 'ova' ? '3 個（K 個）' : '3 個（K(K−1)/2 個）';
  $('w10ovoNdata').textContent = w10ovoMode === 'ova' ? '每個都用全部 96 筆' : '每個只用相關的兩類';
  $('w10ovoRule').textContent = w10ovoMode === 'ova' ? '取 f_k 最大的類別' : '三票裡最多票的類別';
  $('w10ovoDiffN').textContent = nDiff + ' / ' + nCell + '（' + HC.pct(nDiff / nCell, 1) + '）';
  $('w10ovoAmbN').textContent = nAmb + ' / ' + nCell;
  setStatus('w10ovoStatus', (w10ovoMode === 'ova'
    ? '<b>一對其餘</b>：3 個分類器，每一個都把某一類對上「其餘兩類合起來」，'
      + '測試點指派給 f_k 最大的那一類。'
    : '<b>一對一</b>：3 個分類器，每一個只比較兩類、其餘資料完全不看，最後投票。')
    + ' 兩種規則在 <b>' + nDiff + ' / ' + nCell + '</b> 格上給出不同答案（'
    + HC.pct(nDiff / nCell, 1) + '，按「疊上不一致」看在哪裡）。'
    + ' 三票平手的格子：' + nAmb + ' 格——'
    + (nAmb === 0
      ? '這組資料剛好三條成對邊界幾乎交於一點，所以看不到平手區。'
      : '灰色那一小塊就是投票規則給不出答案的地方。'));
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.line / HC.bar 在 Chart 未載入時本來就安全地回傳 null。 */
w10hyperSetup();
w10hyperDraw();
w10marginSetup();
w10marginReset();
w10softSetup();
w10softDraw();
w10kernSetup();
w10kernReset();
w10rbfSetup();
w10rbfDraw();
w10ovoSetup();
w10ovoDraw();
HC.ready(() => {
  w10softChart();
  w10softDraw();
  w10lossDraw();
  w10rbfChart();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("support_vector_machines", BODIES, PAGEJS, frames())
