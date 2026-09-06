#!/usr/bin/env python3
"""deep_learning.html（ISLP 第 10 章）完整自學充實。冪等。

**這是補充章。** 本課（MATH524）沒有教第 10 章，所以沒有講義 PDF、沒有中文 lab、
沒有課程錄影。內容依據是 ISLP 第 10 章正文（書上 p.400–466）與課本官方的英文 lab
`Ch10-deeplearning-lab.ipynb`（intro-stat-learning/ISLP_labs，BSD 2-Clause，
釘 commit 6bf6160）。

出處紀律跟其他章一樣，只是來源換了：所有「預期輸出」逐字取自官方 lab 的實跑結果
（lab_output 找不到輸出會直接報錯），程式碼註解保持英文不翻譯，中文解說一律寫在
卡片外面。雙下降的圖表資料由 tools/frames/gen_deeplearning.py 在固定種子下產生。

注意課本表格與官方 lab 的數字**不一樣**（切分、epoch 數、torch 版本都不同），
兩邊都要標清楚是誰的數字，不要混著講。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, viz)

CH = 10
LAB = "Ch10-deeplearning-lab.ipynb"
LAB_URL = ("https://github.com/intro-stat-learning/ISLP_labs/blob/"
           "6bf6160a3dd180c6651ba06655b453e81f91dc20/Ch10-deeplearning-lab.ipynb")


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def slider(sid, label, lo, hi, step, val, fn, vid, vtext, basis="1 1 200px", vw=54, lw=34):
    """.controls-bar 裡的滑桿（照抄 enrich_svm.py，含它踩過的坑）。

    三個滑桿並排時，base.css 給的 min-width（.slider-label 60px、.slider-val 60px）
    加上 <input type="range"> 的內建最小寬度會超過一列的空間，.slider-val 於是被推出
    .slider-row 外面、藏到下一個滑桿的背景底下。所以這裡用 inline style 覆蓋這三個
    min-width，讓它們真的縮得下去。
    """
    return (f'<div class="slider-row" style="flex:{basis};margin-bottom:0;min-width:0;">'
            f'<span class="slider-label" style="min-width:{lw}px;">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}" onchange="{fn}" style="min-width:0;flex:1 1 0;">'
            f'<span class="slider-val" id="{vid}" style="min-width:{vw}px;">{vtext}</span></div>')


def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_deeplearning.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_deeplearning.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_deeplearning.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p><strong>本課沒有教第 10 章</strong>。它不在考試範圍，
  也沒有對應的講義與 lab。放上來是因為前面九章把「線性模型 → 加彈性 → 加正則化 →
  換基底 → 集成」這條線走完之後，深度學習正好是同一條線的下一步，缺了它整本書會斷掉。</p>

  <p>ISLP 從模型形式介紹神經網路：把式子攤開來看，它就是
  <strong>線性模型套一層非線性再線性組合一次</strong>。單層網路的預測函數長這樣：</p>

  $$f(X) = \\beta_0 + \\sum_{{k=1}}^{{K}} \\beta_k \\, g\\!\\left(w_{{k0}}
    + \\sum_{{j=1}}^{{p}} w_{{kj}} X_j\\right) \\tag{{10.1}}$$

  <p>把 g 換成恆等函數，整條式子會塌回線性迴歸：兩層線性組合疊起來還是線性組合。
  其中 g 提供非線性，其餘部分沿用線性組合。</p>

{info("這一章的六個主題", '''<strong>1. 單層網路（§10.1）：</strong>一層隱藏層，非線性從哪裡進來。<br>
  <strong>2. 多層與 MNIST（§10.2）：</strong>疊第二層、softmax 輸出、參數量開始失控。<br>
  <strong>3. 卷積網路（§10.3）：</strong>權重共享與池化，把影像的結構寫進架構裡。<br>
  <strong>4. 文件分類與 RNN（§10.4–10.5）：</strong>順序有意義的時候，詞袋不夠用。<br>
  <strong>5. 怎麼配適（§10.7）：</strong>反向傳播、SGD、dropout。<br>
  <strong>6. 雙下降（§10.8）：</strong>參數比樣本還多，測試誤差為什麼還會再降一次。''')}

  <p>還有一個貫串全章的問題，§10.6 專門處理：<strong>什麼時候該用深度學習、什麼時候不該。</strong>
  ISLP 的立場很明確，Hitters 那個例子就是拿來說服你的——神經網路跟線性迴歸打平，
  而線性模型看得懂、講得清。他們搬出奧坎剃刀：表現差不多的時候，挑簡單的那個。</p>

{table(["", "線性迴歸", "神經網路"],
       [["參數怎麼來", "閉式解，一次算完", "梯度下降，要迭代、要調"],
        ["有幾個要調的東西", "幾乎沒有", "層數、寬度、學習率、批次大小、dropout、epoch 數…"],
        ["係數能解讀嗎", "能，還有標準誤與 p 值", "不能，是黑盒子"],
        ["什麼時候贏", "n 不大、訊號接近線性、要解釋", "n 很大、訊噪比高、輸入有空間或時間結構"]])}

{quiz("qWhyNN", "QUIZ · 非線性從哪裡來",
      "式 10.1 裡如果把 g(z) 換成恆等函數 g(z) = z，這個「神經網路」會變成什麼？",
      [(True, "退化成 X₁, …, X_p 的線性模型，隱藏層完全白費",
        "對。代進去展開會得到 β₀ + Σₖ βₖwₖ₀ + Σⱼ (Σₖ βₖwₖⱼ) Xⱼ，"
        "括號裡那一坨就是 Xⱼ 的新係數。不管疊幾層都一樣："
        "<strong>線性組合的線性組合還是線性組合</strong>。這就是為什麼 g 非得是非線性的。"),
       (False, "還是非線性的，因為有 K 個隱藏單元在加總",
        "「多」不等於「非線性」。K 個單元各自算一個線性函數，加總起來仍然是線性函數。"
        "非線性只能從每個單元裡那個 g 進來，加總這個動作本身不會產生它。"),
       (False, "會變成 K 次多項式迴歸，因為有 K 個隱藏單元",
        "多項式要有乘冪才會出現。式 10.1 從頭到尾只有加法與乘常數，"
        "g 是恆等函數時連二次項都生不出來。順帶一提，g 若取 g(z) = z² 倒是真的會生出交互項，"
        "ISLP §10.1 式 10.8 就示範了 (X₁+X₂)²/4 − (X₁−X₂)²/4 = X₁X₂。")])}
"""

# ── P01 single ────────────────────────────────────────────────────────
BODIES["single"] = f"""
  <p>單層網路的結構只有三步：輸入做 K 組線性組合、每一組過同一個 g、
  再把 K 個結果線性組合成輸出。中間那 K 個值 ISLP 叫 <strong>activation</strong>，
  寫成 A_k：</p>

  $$A_k = h_k(X) = g\\!\\left(w_{{k0}} + \\sum_{{j=1}}^{{p}} w_{{kj}} X_j\\right),
    \\qquad f(X) = \\beta_0 + \\sum_{{k=1}}^{{K}} \\beta_k A_k \\tag{{10.2}}$$

  <p>要估的參數是所有 w 與所有 β，總共 K(p+1) + (K+1) 個。
  注意 w_{{k0}} 與 β₀ 這兩個截距在機器學習圈叫 <strong>bias</strong>——
  ISLP 在註腳特別提醒，那跟偏差–變異取捨的「偏差」是兩回事，只是撞名。</p>

{info("g 的兩個常見選擇", '''<strong>Sigmoid：</strong>g(z) = eᶻ/(1+eᶻ)，把任何實數壓進 (0, 1)。
  就是邏輯斯迴歸那個函數。缺點是 |z| 一大曲線就平掉，導數趨近 0，梯度傳不回去。<br>
  <strong>ReLU：</strong>g(z) = max(0, z)。負的歸零、正的原樣過。導數取 0 或 1，
  算得快也不會消失，現代網路的預設。''')}

{viz(svg("w11fwdSvg", 400),
     [info_card("怎麼玩",
                '<strong>直接拖左邊四個輸入節點上下移動</strong>就能改 X₁–X₄。'
                '每個隱藏單元的圓圈大小代表 A_k 的值，連線粗細代表 |權重|、'
                '紅藍代表正負。權重是固定的（隨機給定並固定種子），'
                '這裡要看的是「同一組權重下，輸入怎麼變成輸出」。', "LIVE"),
      rows_card("目前的狀態",
                [("激發函數 g", "ReLU", "w11fwdG"),
                 ("A₁ = g(w₁₀ + Σ w₁ⱼXⱼ)", "—", "w11fwdA1"),
                 ("A₂", "—", "w11fwdA2"),
                 ("A₃", "—", "w11fwdA3"),
                 ("輸出 f(X)", "—", "w11fwdOut"),
                 ("有幾個參數要估", "—", "w11fwdNp")]),
      info_card("死掉的單元",
                'ReLU 有一個代價：只要 w₁₀ + Σ w₁ⱼXⱼ 對所有訓練樣本都是負的，'
                '那個單元永遠輸出 0、導數也永遠是 0，就再也學不動了。'
                '把 w₁₀ 拉到很負就能看到 A₁ 變成灰色的 0。')],
     "w11fwdStatus", "拖左邊四個輸入節點上下移動，看隱藏單元與輸出怎麼跟著動。",
     '<label class="slider-label" style="min-width:20px;">g</label>'
     '<select id="w11fwdSel" class="mono" onchange="w11fwdDraw()">'
     '<option value="relu" selected>ReLU</option>'
     '<option value="sigmoid">Sigmoid</option>'
     '<option value="tanh">tanh</option>'
     '<option value="id">恆等（退化成線性）</option></select>'
     + slider("w11fwdB1", "w₁₀", -4, 4, 0.1, 0, "w11fwdDraw()", "w11fwdB1v", "0.0",
              basis="1 1 190px", lw=30)
     + '<button class="btn btn-reset" onclick="w11fwdReset()">重置</button>',
     provenance=("simulation", "固定未訓練權重；只示範 ISLP §10.1 的 forward pass。"))}

{qa("觀念釐清", [
    ("Q：隱藏單元的個數 K 該怎麼選？",
     "<p>沒有公式，它是超參數，跟第 6 章的 λ、第 8 章的樹深度同一個地位，"
     "用交叉驗證或驗證集選。</p>"
     "<p>實務上也常<strong>先把 K 開大，"
     "再靠正則化（dropout、權重衰減、早停）把彈性收回來</strong>，"
     "這種做法的理由見 §10.8：過度參數化的網路配上"
     "會找平滑解的 SGD，表現往往比「剛好夠用」的網路更好。</p>"),
    ("Q：為什麼要標準化輸入？",
     "<p>跟 SVM 與嶺迴歸的理由一樣：所有輸入共用同一個學習率與同一個權重衰減，"
     "尺度差很多時，數值大的那個變數會主宰梯度，小的那個幾乎不動。</p>"
     "<p>官方 lab 的 Hitters 例子在 lasso 那條路上用 <code>StandardScaler</code> "
     "包進 <code>Pipeline</code>，神經網路那條路則是先把整個 X 標準化再切訓練測試。"
     "要注意的是：<strong>標準化的統計量只能從訓練資料算</strong>，"
     "否則就是第 5 章講過的資料洩漏。</p>"),
])}

  <h3 id="dx-hit">官方 lab §10.9.1：先把線性基準立起來</h3>

  <p>ISLP 的示範順序很值得學：<strong>先跑線性迴歸與 lasso，再跑神經網路。</strong>
  沒有基準線的話，你不會知道那個神經網路到底是好是壞。資料是 <code>Hitters</code>，
  n = 263、p = 19，用三分之一當測試集。</p>

{card("lab §10.9.1 · 資料準備與線性迴歸基準",
      lab_code(CH, 22) + "\n\n" + lab_code(CH, 25) + "\n\n" + lab_code(CH, 27),
      lab_output(CH, 27), src=src("22、25、27"),
      note="測試集上的平均絕對誤差是 <strong>259.72</strong>。這是最陽春的基準，"
           "後面每個模型都要跟它比。")}

{card("lab §10.9.1 · lasso 基準（10 折 CV 選 λ）",
      lab_code(CH, 31) + "\n\n" + lab_code(CH, 33) + "\n\n" + lab_code(CH, 35),
      lab_output(CH, 35), src=src("31、33、35"),
      note="lasso 把 MAE 壓到 <strong>235.68</strong>，比最小平方好一截。"
           "注意 <code>lam_max</code> 那一行：它算出「剛好把所有係數壓成 0」的 λ，"
           "格點就從那裡往下取，這樣不必憑空猜範圍。")}

  <h3 id="dx-mod">官方 lab §10.9.1：用 torch 寫一個單層網路</h3>

  <p>PyTorch 的寫法是繼承 <code>nn.Module</code>，在 <code>__init__</code> 裡宣告要用的層、
  在 <code>forward</code> 裡寫資料怎麼流過去。這個網路是 19 → 50（ReLU、dropout 0.4）→ 1。</p>

{card("lab §10.9.1 · HittersModel 與參數量",
      lab_code(CH, 37) + "\n\n" + lab_code(CH, 42),
      lab_output(CH, 42), src=src("37、42"),
      note="1,000 + 51 = <strong>1,051 個參數</strong>，訓練樣本只有 175 筆。"
           "模型包含 <code>Dropout(0.4)</code>；這個 lab 固定訓練 50 個 epoch，沒有設定早停。"
           "單次結果不能把表現歸因於 dropout、雙下降或任何一項正則化機制。")}

{card("lab §10.9.1 · 訓練 50 個 epoch 之後測試",
      lab_code(CH, 56) + "\n\n" + lab_code(CH, 58),
      lab_output(CH, 58), src=src("56、58"),
      note="<code>test_mae</code> = <strong>221.83</strong>，比 lasso 的 235.68 好。"
           "但先別急著下結論——<strong>課本 Table 10.2 裡神經網路是輸的</strong>"
           "（MAE 257.4 對線性迴歸的 254.7）。同一份資料、同一個做法，"
           "換個切分與 epoch 數就換了名次，比較名次時也要交代這些設定。")}

{quiz("qHit", "QUIZ · 怎麼讀這組數字",
      "官方 lab 跑出線性 259.72、lasso 235.68、神經網路 221.83；"
      "課本 Table 10.2 卻是線性 254.7、lasso 252.3、神經網路 257.4。該怎麼解釋？",
      [(True, "兩邊是不同的隨機切分與訓練設定，這種量級的差距落在單一測試集的變異裡，"
        "不能當成「神經網路比較好」的證據",
        "對。測試集只有 88 筆，MAE 差二三十完全可能只是切分運氣。"
        "第 5 章講過的事在這裡照樣成立：<strong>要比較模型，得用交叉驗證或重複多次切分</strong>，"
        "需要更多切分或重複訓練的結果來判斷。ISLP 自己的結論是三個模型「表現相近」，然後選簡單的那個。"),
       (False, "官方 lab 的版本比較新，所以它的數字才是對的",
        "「比較新」不代表比較準。兩邊都只是各跑一次的單一測試集結果，"
        "新舊不會改變這一點。真要說的話，兩組數字都不該被當成定論。"),
       (False, "課本用了 dropout 而 lab 沒有，所以課本的神經網路比較差",
        "反了，而且事實不對——lab 的 <code>HittersModel</code> 裡就有 "
        "<code>nn.Dropout(0.4)</code>，課本 Table 10.2 的註腳也說用了 10% dropout。"
        "兩邊都有正則化，差別在切分與訓練長度。")])}
"""

# ── P02 multi ─────────────────────────────────────────────────────────
BODIES["multi"] = f"""
  <p>多加一層之後，第二層接收第一層的輸出 A^(1)，由它繼續計算。
  式子還是那個式子，只是套了兩次：</p>

  $$A^{{(1)}}_k = g\\!\\left(w^{{(1)}}_{{k0}} + \\sum_j w^{{(1)}}_{{kj}} X_j\\right),
    \\qquad
    A^{{(2)}}_\\ell = g\\!\\left(w^{{(2)}}_{{\\ell 0}}
      + \\sum_k w^{{(2)}}_{{\\ell k}} A^{{(1)}}_k\\right)$$

  <p>MNIST 是十類別的問題，所以輸出層要吐十個數字再轉成機率。用的是
  <strong>softmax</strong>：</p>

  $$f_m(X) = \\Pr(Y = m \\mid X)
    = \\frac{{e^{{Z_m}}}}{{\\sum_{{\\ell=0}}^{{9}} e^{{Z_\\ell}}}} \\tag{{10.13}}$$

  <p>損失函數則是負的多項式對數似然，也就是<strong>交叉熵</strong>：</p>

  $$-\\sum_{{i=1}}^{{n}} \\sum_{{m=0}}^{{9}} y_{{im}} \\log f_m(x_i) \\tag{{10.14}}$$

{info("softmax 是過度參數化的", '''把每個 Z_m 同時加上一個常數 c，分子分母各多一個 e^c，
  約掉之後機率完全不變（這正是習題 2a）。所以 softmax 的解不唯一。
  但實務上不成問題：正則化與 SGD 會把解限制在一個特定的地方。
  同樣的事在第 4 章的多元邏輯斯迴歸也發生過，那裡的處理方式是挑一個類別當基準。''')}

  <p>參數量是這一節的重點。MNIST 的輸入是 28×28 = 784 個像素，
  ISLP 用的架構是 784 → 256 → 128 → 10。光第一層就有 784×256 + 256 = 200,960 個參數，
  三層加起來 <strong>235,146</strong> 個。對照組多元邏輯斯迴歸只需要 785×9 = 7,065 個，
  差了 33 倍。</p>

{viz(svg("w11paramSvg", 380),
     [info_card("怎麼玩",
                '拖滑桿改每一層的寬度，右邊即時算出參數量。'
                '<strong>參數幾乎都集中在第一層</strong>，因為 784 這個輸入維度最大。'
                '把第一層從 256 降到 64，總參數量會掉掉四分之三，'
                '但測試準確率通常掉不了多少。這就是 CNN 想解決的浪費。', "LIVE"),
      rows_card("參數量",
                [("第 1 層 784 → h₁", "—", "w11paramL1"),
                 ("第 2 層 h₁ → h₂", "—", "w11paramL2"),
                 ("輸出層 h₂ → 10", "—", "w11paramL3"),
                 ("合計", "—", "w11paramTot"),
                 ("對照：多元邏輯斯 785×9", "7,065", "w11paramMlr"),
                 ("是它的幾倍", "—", "w11paramRatio")]),
      info_card("怎麼算",
                '一層從 a 個單元接到 b 個單元，權重 a×b 個、偏置 b 個，'
                '共 <strong>(a+1)×b</strong> 個。習題 1(d) 與 4(b) 考的就是這個，'
                '差別只在 CNN 的權重是共享的。')],
     "w11paramStatus", "拖滑桿改層寬，看參數量怎麼變。預設值就是 ISLP §10.2 的 784–256–128–10。",
     slider("w11paramH1", "h₁", 16, 512, 16, 256, "w11paramDraw()", "w11paramH1v", "256",
            basis="1 1 190px", lw=26, vw=44)
     + slider("w11paramH2", "h₂", 8, 256, 8, 128, "w11paramDraw()", "w11paramH2v", "128",
              basis="1 1 190px", lw=26, vw=44)
     + '<button class="btn btn-reset" onclick="w11paramReset()">回到 256／128</button>',
     provenance=("book-redraw", "依 ISLP §10.2 的 MNIST 784–256–128–10 架構計算參數量。"))}

  <h3 id="dx-mn">官方 lab §10.9.2：MNIST 上的兩層網路</h3>

{card("lab §10.9.2 · MNISTModel 與參數量",
      lab_code(CH, 77) + "\n\n" + lab_code(CH, 83),
      lab_output(CH, 83), src=src("77、83"),
      note="兩層的 dropout 比例不一樣（0.4 與 0.3）：靠近輸入的層通常丟得多一點。"
           "<code>nn.Flatten()</code> 把 28×28 攤成 784 的向量，"
           "<strong>這個動作把像素的空間關係整個丟掉了</strong>，"
           "下一節的卷積網路就是為了把它找回來。")}

{card("lab §10.9.2 · 測試準確率", lab_code(CH, 92), lab_output(CH, 92), src=src("92"),
      note="<code>test_accuracy</code> = <strong>0.9620</strong>，錯誤率 3.8%。"
           "課本 Table 10.1 報的是 1.8%（dropout 版），差別在訓練得比較久。")}

{card("lab §10.9.2 · 拿多元邏輯斯迴歸當對照",
      lab_code(CH, 94) + "\n\n" + lab_code(CH, 97),
      lab_output(CH, 97), src=src("94、97"),
      note="同一個 torch 框架，把中間兩層拿掉就是多元邏輯斯迴歸，"
           "<code>nn.Linear(784, 10)</code> 加 softmax 而已。準確率 "
           "<strong>0.9161</strong>，錯誤率 8.4%，是兩層網路的兩倍多。"
           "<strong>這個例子裡多的那兩層是真的有用的</strong>，"
           "跟 Hitters 那個「打平」的結論不一樣。")}

{quiz("qParam", "QUIZ · 參數量",
      "一個網路是 784 → 256 → 128 → 10 的全連接架構（每層都有偏置）。第一層有幾個參數？",
      [(True, "200,960 個：權重 784×256 = 200,704，加上 256 個偏置",
        "對。一層從 a 接到 b 就是 (a+1)×b 個參數。"
        "整個網路 200,960 + 32,896 + 1,290 = <strong>235,146</strong>，"
        "正好是 ISLP §10.2 印的那個數字。"),
       (False, "200,704 個，偏置不算參數因為它不乘任何輸入",
        "偏置也需要估計，因此計入參數個數。它就是迴歸裡的截距，線性迴歸的 β₀ 也包含在參數計數中。"
        "少算 256 個後，結果仍在相同量級；習題 1(d) 要求把偏置一併計入。"),
       (False, "1,040 個：784 + 256 個單元各一個參數",
        "把「單元個數」當成「參數個數」了。參數應按<strong>連線</strong>上的權重計數："
        "784 個輸入各自連到 256 個隱藏單元，連線數由輸入數乘上隱藏單元數得到。")])}
"""

# ── P03 cnn ───────────────────────────────────────────────────────────
BODIES["cnn"] = f"""
  <p>上一節把 28×28 攤平成 784 的那一刻，「這兩個像素相鄰」的資訊就沒了。
  對影像來說這很浪費：一隻貓的耳朵出現在左上角還是右下角，都應該算是耳朵。
  卷積網路把這個先驗直接寫進架構，做法有兩個。</p>

{info("CNN 的兩個動作", '''<strong>卷積層：</strong>拿一個小濾波器（例如 3×3）掃過整張圖，
  每個位置算一次內積。同一個濾波器在所有位置<strong>共用同一組權重</strong>，
  所以參數量跟影像大小無關，只跟濾波器大小有關。<br>
  <strong>池化層：</strong>把相鄰一小塊（例如 2×2）濃縮成一個值，最大池化取最大者。
  它降解析度，也讓結果對小幅平移不敏感：刻意丟掉一些「在哪裡」，換取「有沒有」的穩健。''')}

{viz(svg("w11convSvg", 420),
     [info_card("怎麼玩",
                '直接拖「列／行」選擇 3×3 濾波器目前對齊的位置。'
                '左邊框線標出輸入視窗，右邊同步標出對應的特徵圖格子與內積。'
                '換濾波器看看：<strong>垂直邊緣</strong>只對左右明暗交界有反應。', "LIVE"),
      rows_card("目前這一步",
                [("濾波器", "垂直邊緣", "w11convK"),
                 ("對齊位置", "—", "w11convPos"),
                 ("這一格的內積", "—", "w11convVal"),
                 ("特徵圖大小", "—", "w11convSize"),
                 ("這一層要估幾個參數", "—", "w11convNp"),
                 ("換成全連接要幾個", "—", "w11convFc")]),
      info_card("為什麼參數少這麼多",
                '3×3 濾波器不管掃 8×8 還是 1024×1024，都只有 9 個權重加 1 個偏置。'
                '同樣的輸出如果用全連接層做，每個輸出單元都要自己一組權重，'
                '那就是習題 4(d) 在算的東西。')],
     "w11convSvgStatus", "拖列與行，直接檢查任一卷積視窗和對應輸出。",
     '<label class="slider-label">濾波器</label>'
     '<select id="w11convSel" class="mono" onchange="w11convSetK()">'
     '<option value="vedge" selected>垂直邊緣</option>'
     '<option value="hedge">水平邊緣</option>'
     '<option value="blur">平均（模糊）</option>'
     '<option value="sharp">銳化</option></select>'
     '<label class="slider-label">列</label><input id="w11convRow" type="range" min="1" max="6" value="1" oninput="w11convSelect()">'
     '<label class="slider-label">行</label><input id="w11convCol" type="range" min="1" max="6" value="1" oninput="w11convSelect()">'
     '<label class="slider-label"><input id="w11convPool" type="checkbox" onchange="w11convSelect()"> 顯示 2×2 最大池化</label>'
     '<button class="btn btn-reset" onclick="w11convReset()">重置</button>',
     provenance=("illustrative", "8×8 自訂影像與標準 3×3 濾波器；只示範卷積、共享權重與池化。"))}

{qa("觀念釐清", [
    ("Q：池化為什麼要「丟掉資訊」？這樣有什麼好處？",
     "<p>丟掉的是位置的精度，留下的是「這個特徵存不存在」。對分類來說後者才是重點——"
     "你要判斷這是不是一隻貓，不需要知道耳朵精確在第 137 個像素。</p>"
     "<p>更實際的理由是它讓後面的層看得更廣。經過一次 2×2 池化，"
     "同樣一個 3×3 濾波器在原圖上涵蓋的範圍就變成兩倍。"
     "<strong>堆疊「卷積＋池化」等於一步步擴大視野</strong>："
     "前面的層看邊緣與紋理，後面的層看得到整隻動物。官方 lab 的 "
     "<code>CIFARModel</code> 疊了四組，32×32 因此縮成 2×2。</p>"),
    ("Q：資料擴增算正則化嗎？",
     "<p>算，而且 ISLP §10.3.4 就是這樣定位它的。把訓練影像隨機翻轉、平移、縮放之後標籤不變，"
     "等於在告訴模型「這些變化不該影響答案」。這是一個很強的約束，"
     "跟嶺迴歸用懲罰項限制係數是同一種事，都在縮小模型能選的函數空間。</p>"
     "<p>差別在於它是<strong>用資料表達</strong>的約束。"
     "好處是很容易加進任何模型；壞處是你得知道哪些變化是無害的（影像可以左右翻，"
     "手寫數字的 6 跟 9 就不能上下翻）。</p>"),
])}

  <h3 id="dx-cnn">官方 lab §10.9.3：CIFAR-100 上的 CNN</h3>

{card("lab §10.9.3 · 一個 building block 疊四次",
      lab_code(CH, 110) + "\n\n" + lab_code(CH, 112), None, src=src("110、112"),
      note="<code>BuildingBlock</code> 就是「卷積 → ReLU → 最大池化」三件套。"
           "通道數一路 3 → 32 → 64 → 128 → 256 加倍，空間尺寸則被池化一路砍半："
           "32 → 16 → 8 → 4 → 2。<strong>解析度換通道數</strong>是 CNN 的標準節奏。")}

{card("lab §10.9.3 · 測試準確率", lab_code(CH, 121), lab_output(CH, 121), src=src("121"),
      note="<strong>0.4270</strong>。一百個類別的隨機猜測是 1%，所以 43% 其實不算差，"
           "但也遠稱不上好：CIFAR-100 每類只有 500 張訓練影像，這種規模對 CNN 太少了。"
           "下一張卡的做法才是資料不多時該走的路。")}

{card("lab §10.9.4 · 直接用預訓練的 ResNet50",
      lab_code(CH, 136) + "\n\n" + lab_code(CH, 138),
      lab_output(CH, 138), src=src("136、138"),
      note="這個模型在 ImageNet 上訓練過，完全沒看過這幾張照片。"
           "紅鶴 0.61、拉薩犬 0.26 都對；但第一張織巢鳥被猜成 jacamar（鶲䴕），"
           "而且最高機率只有 0.30。<strong>看機率不要只看排名</strong>——"
           "0.30 這種數字本身就在說「我不太確定」。")}

{quiz("qConv", "QUIZ · 卷積的參數量",
      "輸入是 32×32 的灰階影像，一個卷積層有三個 5×5 濾波器、不做邊界填補。"
      "這一層要估幾個參數？",
      [(True, "78 個：3 × (5×5 + 1)",
        "對。每個濾波器 25 個權重加 1 個偏置，三個就是 78。"
        "<strong>跟輸入影像多大完全無關</strong>，這正是權重共享的意思。"
        "順帶算一下輸出：不填補時每張特徵圖是 (32−5+1)² = 28×28，三張共 2,352 個隱藏單元。"),
       (False, "2,352 個，因為輸出有 3 × 28 × 28 個隱藏單元",
        "這個數字計算的是<strong>單元</strong>；<strong>參數</strong>還需依共用權重計數。"
        "這 2,352 個單元全都由同樣的 78 個參數算出來，它們共享權重，"
        "只是對齊到影像的不同位置。這個區別是習題 4(c) 的重點。"),
       (False, "2,408,448 個，每個隱藏單元都要連到全部 1,024 個像素",
        "這是<strong>拿掉權重共享之後</strong>的答案，也就是習題 4(d) 問的那個數字"
        "（2,352 × 1,024）。卷積層之所以叫「加了限制的全連接層」，"
        "就是因為它把這兩百多萬個權重綁成只有 78 個自由參數。")])}
"""

# ── P04 rnn ───────────────────────────────────────────────────────────
BODIES["rnn"] = f"""
  <p>影像的結構是空間上的，文字與股價的結構是<strong>順序上的</strong>。
  ISLP 用 IMDB 影評的正負評分類當例子，先示範最笨的做法：<strong>詞袋</strong>。
  把每篇評論表示成「字典裡每個詞出現了沒有」的長向量，
  然後就當成普通的分類問題丟給 lasso 或神經網路。</p>

  <p>詞袋完全丟掉詞序，所以「這部片一點都不好看」跟「這部片好看一點都不」是同一個向量。
  詞袋在情感分類這種任務上仍可有良好表現，因為有沒有出現
  <em>terrible</em> 這個詞，本身就是很強的訊號。</p>

{card("lab §10.9.5 · 詞袋 ＋ 兩層網路的 IMDB 準確率",
      lab_code(CH, 156), lab_output(CH, 156), src=src("156"),
      note="<strong>0.8450</strong>。這是詞袋能到的水準，沒有用到任何詞序資訊。")}

  <p>要把順序找回來，就要換成<strong>遞迴神經網路</strong>。
  它依序讀入 X₁, X₂, …, X_L，每讀一個就用<strong>同一組權重</strong>更新一個隱藏狀態：</p>

  $$A_\\ell = g\\!\\left(W X_\\ell + U A_{{\\ell-1}} + b\\right),
    \\qquad O_\\ell = \\beta_0 + \\beta^{{\\top}} A_\\ell$$

  <p>W、U、b 在每個時間點都一樣。這跟 CNN 在空間上共享權重是同一個念頭，
  只是換成在時間上共享。序列多長都用同一組參數。</p>

{info("RNN 在各時間點共用參數",
      "每個時間點都套用同一組 <strong>W、U、b</strong>：目前輸入 Xℓ 與上一個狀態 Aℓ−1 "
      "一起產生新狀態 Aℓ。這些權重由訓練資料學得。", "purple")}

{table(["時間", "讀入", "共用的更新", "保留下來的資訊"],
       [["ℓ = 1", "X₁", "A₁ = g(WX₁ + UA₀ + b)", "第一個詞的脈絡"],
        ["ℓ = 2", "X₂", "A₂ = g(WX₂ + UA₁ + b)", "X₁ 與 X₂ 的摘要"],
        ["…", "…", "同一組 W、U、b", "狀態沿序列傳遞"],
        ["ℓ = L", "X_L", "A_L = g(WX_L + UA_{L−1} + b)", "供最後輸出使用的序列摘要"]])}

{info("架構與模型表現",
      "這裡只解釋 ISLP §10.5 的 recurrence 結構；模型表現回到下面官方 lab 的 LSTM 與"
      "詞袋實跑結果比較。公式說明架構，lab 結果提供這次配適的表現。")}

  <h3 id="dx-lstm">官方 lab §10.9.6：LSTM 與時間序列</h3>

{card("lab §10.9.6 · LSTM 版的 IMDB 分類",
      lab_code(CH, 178) + "\n\n" + lab_code(CH, 185),
      lab_output(CH, 185), src=src("178、185"),
      note="<strong>0.8400</strong>——比詞袋的 0.8450 還<strong>低一點點</strong>。"
           "ISLP 很誠實地把這個結果放上來：情感分類這個任務，詞序帶來的好處"
           "沒有想像中大。<code>nn.Embedding</code> 那一層把每個詞的整數編號"
           "映射成 32 維的稠密向量，是這類模型的標準第一步。")}

{card("lab §10.9.6 · NYSE 交易量的自迴歸",
      lab_code(CH, 196) + "\n\n" + lab_code(CH, 200),
      lab_output(CH, 200), src=src("196、200"),
      note="落後 5 期的線性自迴歸模型測試 R² 是 0.4129（儲存格 196），"
           "加上星期幾這個因子之後變成 <strong>0.4596</strong>。"
           "對照組是 RNN 的 0.4150（儲存格 219）與非線性自迴歸的 0.4660（儲存格 228）。"
           "<strong>四個模型全部落在 0.41 到 0.47 之間</strong>。")}

{quiz("qSeq", "QUIZ · 詞袋輸給 RNN 了嗎",
      "IMDB 上詞袋加兩層網路是 0.8450，LSTM 是 0.8400。下面哪一句最站得住腳？",
      [(True, "這個任務的訊號多半在「有沒有出現某些詞」，詞序能加的資訊有限，"
        "所以兩者打平不奇怪",
        "對。情感分類很大程度上是關鍵詞偵測，<em>terrible</em>、<em>masterpiece</em> "
        "出現與否就決定大半。ISLP 的立場一貫：<strong>先試簡單的，複雜模型要證明自己值得</strong>。"
        "順帶一提，0.845 與 0.840 這種差距在 25,000 筆測試集上也接近雜訊。"),
       (False, "LSTM 比較差，代表遞迴架構不適合處理文字",
        "一個任務與一次訓練不足以判斷整個架構的適用性。"
        "RNN 與其後繼者在機器翻譯、語音辨識上的優勢很清楚："
        "那些任務的輸出本身就是序列，詞序是完成這些任務的必要資訊。"),
       (False, "因為 LSTM 只訓練了很少的 epoch，訓練久一點就會贏",
        "沒有證據支持這個推測，而且它把問題想反了：訓練更久通常先過度配適。"
        "要主張 LSTM 有潛力，該做的是畫學習曲線看驗證誤差還有沒有在降，"
        "再根據驗證結果判斷是否繼續訓練。")])}
"""

# ── P05 fitting ───────────────────────────────────────────────────────
BODIES["fitting"] = f"""
  <p>前面都在講模型長什麼樣，這一節講怎麼把參數估出來。目標函數以量化反應為例：</p>

  $$R(\\theta) = \\frac{{1}}{{2}} \\sum_{{i=1}}^{{n}}
    \\left(y_i - f_\\theta(x_i)\\right)^2 \\tag{{10.22}}$$

  <p>問題在於這個 R(θ) <strong>不是凸函數</strong>。線性迴歸有閉式解、
  邏輯斯迴歸的對數似然是凹的所以有唯一最大值，神經網路兩個都沒有：
  它有很多局部極小，而我們只能用梯度下降慢慢滑下去、
  以找到足夠好的解為目標，保留全域最優性尚未確定的限制。</p>

{viz(chart("w11gdChart", "tall",
           "。此圖的重點：同一個函數、同一個學習率，只是起點不同，"
           "梯度下降就會滑進不同的局部極小，這是非凸最佳化可能出現的結果。"),
     [info_card("怎麼玩",
                '這是 ISLP 習題 6 的函數 R(β) = sin(β) + β/10。'
                '拖滑桿改起點 β⁰ 與學習率 ρ，看軌跡往哪裡收斂。'
                '<strong>β⁰ = 2.3 會滑到 β ≈ 4.61，β⁰ = 1.4 卻掉到 β ≈ −1.67</strong>——'
                '兩個不同的谷底，這正是 6(c) 與 6(d) 要你比較的事。'
                '學習率拉到 1.2 以上還會看到它開始跳來跳去。',
                "習題 6"),
      rows_card("這次的軌跡",
                [("起點 β⁰", "2.30", "w11gdB0"),
                 ("學習率 ρ", "0.10", "w11gdRho"),
                 ("走了幾步", "—", "w11gdSteps"),
                 ("收斂到 β ≈", "—", "w11gdEnd"),
                 ("那裡的 R(β)", "—", "w11gdVal"),
                 ("是全域最小嗎", "—", "w11gdGlobal")]),
      info_card("更新規則",
                '每一步做 β ← β − ρ·R′(β)，其中 R′(β) = cos(β) + 1/10。'
                '導數為 0 的地方就是駐點，梯度下降只保證滑到<strong>某一個</strong>駐點，'
                '不保證是最低的那個。')],
     "w11gdStatus", "拖滑桿改起點與學習率，按「開始」看軌跡。",
     slider("w11gdB0s", "β⁰", -6, 6, 0.1, 2.3, "w11gdSync()", "w11gdB0v", "2.3",
            basis="1 1 180px", lw=26, vw=44)
     + slider("w11gdRhos", "ρ", 0.02, 1.6, 0.02, 0.1, "w11gdSync()", "w11gdRhov", "0.10",
              basis="1 1 180px", lw=22, vw=44)
     + '<button class="btn btn-play" onclick="w11gdRun()">▶ 開始</button>'
     '<button class="btn btn-reset" onclick="w11gdReset()">重置</button>',
     provenance=("book-redraw", "依 ISLP Ch.10 習題 6 的 R(β)=sinβ+β/10 即時計算。"))}

{info("三個讓它跑得動的技巧", '''<strong>反向傳播：</strong>用連鎖律由輸出往回逐層算梯度，
  重複利用前一層算好的中間量，
  成本跟一次前向傳播同一個量級。<br>
  <strong>隨機梯度下降：</strong>每一步只用一小批（minibatch）樣本估梯度。
  除了便宜，取樣雜訊本身還有正則化效果，也幫忙跳出不好的局部極小。<br>
  <strong>Dropout：</strong>訓練時隨機把一部分單元設成 0，剩下的按比例放大。
  每一批看到的都是不同的子網路，沒有單元能依賴特定同伴。
  ISLP 說它的精神接近隨機森林，都靠隨機性打散相關性。''')}

  <p>另一個常用的正則化手段是<strong>早停</strong>。
  訓練誤差會一路降，驗證誤差則通常先降後升；在轉折點停下來，
  效果跟加懲罰項類似。<code>ErrorTracker</code> 回呼只記錄驗證曲線；官方 Hitters lab
  仍跑滿 <code>max_epochs=50</code>，沒有 <code>EarlyStopping</code> 回呼或依驗證結果選 epoch。</p>

{qa("觀念釐清", [
    ("Q：非凸為什麼還敢用？局部極小不會害死我們嗎？",
     "<p>會。以下幾個因素有助於找到可用的解。</p>"
     "<p>第一，實務上在高維空間裡，會嚴重影響結果的局部極小相對較少："
     "更常見的是鞍點，而 SGD 的雜訊很容易把你推離鞍點。"
     "第二，學習的目標是降低<strong>測試</strong>誤差；訓練誤差的全域最小值本身不足以衡量泛化；"
     "訓練誤差的全域最小很可能就是嚴重過度配適的那個點。</p>"
     "<p>第三，這是誠實的部分：<strong>它就是會隨機。</strong>"
     "同一份資料換一個隨機種子，跑出來的網路不一樣、測試誤差也不一樣。"
     "官方 lab 每次訓練前都呼叫 <code>seed_everything</code>，"
     "並在 <code>Trainer</code> 裡設 <code>deterministic=True</code>，"
     "就是為了讓結果可重現。</p>"),
    ("Q：dropout 為什麼要「按比例放大」？",
     "<p>因為訓練與預測時的行為必須對得起來。訓練時如果丟掉 40% 的單元，"
     "下一層收到的加總平均就只剩 60%；預測時所有單元都在，加總會突然變大 1/0.6 倍，"
     "模型等於面對一個沒見過的輸入分布。</p>"
     "<p>解法是訓練時把留下來的值除以 0.6，讓期望值維持不變，"
     "預測時就什麼都不用做。這叫 inverted dropout，也是 <code>nn.Dropout</code> 的做法。"
     "順帶一提，這就是為什麼 <code>model.eval()</code> 很重要——"
     "它會關掉 dropout；忘了呼叫的話預測會帶著隨機性。</p>"),
])}

{quiz("qSgd", "QUIZ · minibatch 的大小",
      "把批次大小從 32 改成整個訓練集（也就是每一步都用全部資料算梯度），會發生什麼？",
      [(True, "每一步的梯度更準，但一個 epoch 只更新一次參數，而且失去了雜訊帶來的正則化",
        "對。梯度更準不等於學得更好：<strong>參數更新的次數大幅減少</strong>，"
        "同樣的 epoch 數下走的路短很多。而且 SGD 的取樣雜訊是有用的："
        "它幫忙跳出不好的局部極小，也讓解偏向比較平坦、泛化比較好的區域。"),
       (False, "完全一樣，因為梯度的期望值不變",
        "期望值確實一樣，但最佳化還受到梯度變動的影響。"
        "<strong>變異數也是演算法行為的一部分</strong>——雜訊改變了它會走到哪裡去。"
        "而且更新次數差了 n/32 倍，這一點跟期望值無關。"),
       (False, "會更快，因為少了每個批次的額外開銷",
        "算一次全資料的梯度本來就比算一個批次貴 n/32 倍，總計算量沒有變少。"
        "而且大批次沒辦法塞進記憶體是很常見的實際限制，"
        "minibatch 一開始就是為了這個而發明的。")])}
"""

# ── P06 doubledesc ────────────────────────────────────────────────────
# 這排控制項有單引號，拉出來寫比在 f-string 裡跳脫乾淨
_dd_controls = (
    '<button class="btn btn-toggle" onclick="w11ddShow(&quot;err&quot;)">誤差曲線</button>'
    '<button class="btn btn-toggle" onclick="w11ddShow(&quot;fit&quot;)">看配適曲線</button>'
    '<label class="slider-label">面板 d</label>'
    '<select id="w11ddSel" class="mono" onchange="w11ddShow(&quot;fit&quot;)">'
    '<option value="8">d = 8</option><option value="20" selected>d = 20</option>'
    '<option value="42">d = 42</option><option value="80">d = 80</option></select>'
)

BODIES["doubledesc"] = f"""
  <p>從第 2 章開始，這本書一直在講同一件事：測試誤差對模型彈性是 U 形的，
  因此把訓練誤差壓到 0 後，仍需檢查泛化表現。§10.8 進一步討論雙下降現象。</p>

  <p>設定很簡單，用的還是第 7 章的自然樣條，跟神經網路無關：
  n = 20 筆資料來自 Y = sin(X) + ε，X 均勻分布在 [−5, 5]、ε 的標準差是 0.3。
  然後配自由度 d 的自然樣條，讓 d 從 2 一路加到 100。</p>

  <p>d = 20 時自由度等於樣本數，樣條剛好穿過每一個點，訓練誤差變成 0：
  這就是<strong>內插門檻</strong>。d 再往上，最小平方解不再唯一（有無限多組係數都能穿過），
  課本挑的是係數平方和最小的那一組，也就是<strong>最小範數解</strong>。</p>

{viz(chart("w11ddChart", "tall",
           "。此圖的重點：測試誤差在 d = n = 20 附近衝到最高，然後隨著自由度繼續增加"
           "又降下來，這就是雙下降。訓練誤差則在 d = 20 之後一直是 0。"),
     [info_card("怎麼看這張圖",
                '橫軸是自然樣條的自由度 d，縱軸是誤差（對數刻度）。'
                '<strong>藍線訓練誤差</strong>在 d = 20 之後貼著 0；'
                '<strong>紅線測試誤差</strong>先 U 形、在 d = 20 衝高、然後第二次下降。'
                '按「看配適曲線」切換到課本圖 10.21 的四個面板。', "圖 10.20／10.21"),
      rows_card("幾個位置",
                [("d = 8（U 形谷底）", "—", "w11dd8"),
                 ("d = 19", "—", "w11dd19"),
                 ("d = 20（內插門檻）", "—", "w11dd20"),
                 ("d = 42", "—", "w11dd42"),
                 ("d = 100", "—", "w11dd100"),
                 ("訊噪比 Var(f)/σ²", "—", "w11ddSnr")]),
      info_card("兩個要注意的地方",
                'd = 20 只有一種方式穿過 20 個點，而那一種很極端；d = 42 有無限多種，'
                '挑出的平滑解有較小的起伏。切到配適曲線會看到 Σβ² '
                '<strong>在 d = 20 最大、之後反而變小</strong>。<br>'
                '另外，訓練誤差在 d ≥ 20 之後<strong>真的是 0</strong>（10⁻²⁸ 量級），'
                '但對數軸畫不出 0，所以藍線被壓在 10⁻⁵ 的底線上。')],
     "w11ddStatus", "紅線是測試誤差、藍線是訓練誤差。注意 d = 20 那根尖峰。",
     _dd_controls,
     provenance=("simulation", "依 ISLP 圖 10.20／10.21 的設定以固定種子重新模擬；數值為本站計算。"))}

{info("雙下降沒有推翻偏差–變異取捨", '''ISLP 提醒讀者：橫軸畫的是「基底函數的個數」，
  而那並沒有正確反映內插模型實際的彈性。d = 42 的最小範數樣條，
  變異其實比 d = 20 的樣條<strong>小</strong>，它只是用比較多的基底去表達一個比較平滑的函數。<br>
  另外兩件要記住的事：<strong>這本書裡大多數方法不會出現雙下降</strong>
  （正則化方法通常不內插資料）；而且在這個例子裡，
  如果改用嶺迴歸配樣條並好好選懲罰項，測試誤差還會更低。
  <strong>判斷模型大小時，仍需比較正則化與測試誤差。</strong>''')}

  <p>這跟深度學習的關係在最後一段：訓練神經網路時我們常常用遠多於樣本數的參數，
  而且真的能把訓練誤差壓到 0 還表現得不錯。ISLP 的解釋是
  <strong>SGD 天生就偏好找到平滑的內插解</strong>，效果類似上面那個最小範數。
  這在訊噪比高的問題（自然影像辨識、語音）上特別成立。</p>

  <p>順帶把 §10.6 的建議收在這裡。ISLP 對「該不該用深度學習」的答案是：
  <strong>先跑簡單模型當基準，讓深度學習去證明自己值得。</strong>
  Hitters 那個例子就是示範：三個模型表現相近時，選看得懂的那個。
  CIFAR 的影像具有空間結構，適合發揮 CNN 的優勢；文字分類仍要實測詞袋的線性基準。
  ISLP 圖 10.11 的 IMDB 比較中，lasso 邏輯斯迴歸與兩隱藏層網路的測試準確率就相近。</p>

{quiz("qDd", "QUIZ · 雙下降在說什麼",
      "下面哪一句符合 ISLP §10.8 的說明？",
      [(True, "測試誤差的第二次下降，是因為 d > n 時我們挑了最小範數解，"
        "而它比 d = n 的唯一內插解平滑得多",
        "對。參數變多之後，<strong>有多個內插解可供選擇</strong>，"
        "而挑的規則（最小範數）偏好平滑。d = n 時只有一種穿法，別無選擇，所以最糟。"),
       (False, "偏差–變異取捨在深度學習裡不成立，模型愈大測試誤差就愈低",
        "ISLP 明確反駁了這個讀法。取捨仍然成立，只是橫軸那個「基底個數」"
        "沒有正確衡量彈性。而且課本自己說了，同一個例子改用嶺迴歸會得到"
        "<strong>更低</strong>的測試誤差。增加模型大小仍有配適與泛化的取捨。"),
       (False, "只要把訓練誤差壓到 0，測試誤差就會開始下降",
        "順序反了。d = 20 就已經把訓練誤差壓到 0，而那正是測試誤差最糟的地方。"
        "零訓練誤差是必要條件；要出現這裡的第二次下降，仍需選到夠平滑的內插解。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 10.10 第 1 題（d）",
      "一個網路有 p = 4 個輸入、第一層 2 個隱藏單元、第二層 3 個隱藏單元、單一輸出，"
      "每一層都有偏置。總共有幾個參數？",
      [(True, "23 個",
        "對。逐層算：4→2 是 (4+1)×2 = 10；2→3 是 (2+1)×3 = 9；3→1 是 (3+1)×1 = 4。"
        "合計 <strong>23</strong>。訣竅是每一層都用 (輸入數 + 1) × 輸出數，"
        "那個 +1 就是偏置。"),
       (False, "17 個",
        "這是忘了偏置的答案：4×2 + 2×3 + 3×1 = 17。"
        "偏置每一個輸出單元都有一個，這裡共 2 + 3 + 1 = 6 個，加回去才是 23。"
        "本題的 (d) 小題考的就是這個細節。"),
       (False, "10 個",
        "把單元個數加起來了（4 + 2 + 3 + 1 = 10）。"
        "應計算<strong>連線</strong>上的權重；單元表示中間量，"
        "它的值是算出來的，不需要估。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 10.10 第 2 題（a）",
      "softmax 的定義是 f_m(X) = e^{{Z_m}} / Σ_ℓ e^{{Z_ℓ}}。"
      "把每一個 Z_ℓ 都加上同一個常數 c，機率會怎麼變？",
      [(True, "完全不變，因為分子分母各多出一個 e^c，約掉了",
        "對。分子變成 e^(Z_m + c) = e^c·e^(Z_m)，分母變成 e^c·Σ e^(Z_ℓ)，"
        "e^c 上下消掉。這說明 softmax 是<strong>過度參數化</strong>的——"
        "有一整族參數給出完全一樣的預測。實務上靠正則化與 SGD 把解釘在一個地方；"
        "第 4 章的多元邏輯斯迴歸則是挑一個類別當基準來解決。"),
       (False, "每個機率都乘上 e^c，所以加總不再是 1",
        "只有分子乘上 e^c 的話確實會這樣，但<strong>分母也一起乘了</strong>——"
        "分母是所有 e^{{Z_ℓ}} 的和，每一項都多了 e^c。加總永遠是 1 是 softmax 的定義保證的。"),
       (False, "機率會變得更平均，因為指數函數把大的值壓縮了",
        "「加常數」跟「壓縮」是兩回事。若要讓機率更接近平均，可以把所有 Z_ℓ "
        "同時<strong>除以</strong>一個大於 1 的數（那就是溫度縮放），"
        "這個變換是乘法；前面的共同平移是加法。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 10.10 第 4 題（b）（d）",
      "輸入是 32×32 灰階影像，一個卷積層有三個 5×5 濾波器、不做邊界填補。"
      "「這一層的參數量」與「拿掉權重共享後的權重數」分別是多少？",
      [(True, "78 個與 2,408,448 個",
        "對。共享時是 3 × (5×5 + 1) = 78。拿掉共享的話，輸出有 3 × 28 × 28 = 2,352 "
        "個隱藏單元（32 − 5 + 1 = 28），每個都要連到全部 32 × 32 = 1,024 個像素，"
        "得到 2,352 × 1,024 = <strong>2,408,448</strong>。差了三萬倍。"
        "卷積層就是一個被綁得很緊的全連接層。"),
       (False, "78 個與 78 個，因為權重共享不改變參數量",
        "前半對、後半把題目讀反了。(d) 問的正是「<strong>如果沒有</strong>那些限制」"
        "會有幾個權重，也就是把每條連線都放開來各自估。"),
       (False, "75 個與 2,352 個",
        "75 是漏了偏置（3 × 25）。2,352 則是隱藏<strong>單元</strong>的個數，"
        "這個數字計算單元，每個單元還要各自連到 1,024 個像素。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 10.10 第 5 題",
      "課本 Table 10.2 裡，三個模型依「平均絕對誤差」排出來的名次，"
      "跟依「測試 R²」排出來的名次不一樣。這怎麼可能？",
      [(True, "兩個指標對大誤差的懲罰方式不同：R² 建立在平方誤差上，"
        "少數幾筆很大的殘差會嚴重拉低它，MAE 則是線性計入",
        "對。一筆殘差 100 對 MAE 的貢獻是另一筆殘差 50 的兩倍，"
        "對平方誤差的貢獻卻是四倍。所以<strong>「多數點準、少數點誤差很大」的模型 MAE 會贏、"
        "R² 會輸</strong>，反之亦然。Hitters 的薪水分布右偏、有幾個天價球員，"
        "正是會出現這種分歧的典型情況。"),
       (False, "因為 R² 有考慮參數量而 MAE 沒有，所以參數多的模型 R² 會被扣分",
        "會扣參數量的是調整後 R²、AIC、BIC 那一類。"
        "測試集上的 R² = 1 − RSS/TSS 完全沒有參數項，它是在<strong>測試</strong>資料上算的，"
        "本來就不需要為複雜度罰款。"),
       (False, "一定是其中一個數字算錯了，兩個指標衡量的是同一件事所以名次必須一致",
        "兩個指標都在衡量「預測準不準」，但<strong>加權方式不同就可能給出不同名次</strong>，"
        "這是完全正常的。這也是為什麼報告結果時該同時給幾個指標，"
        "並一併交代各指標的結果。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。這一章不在考試範圍，但它補充了 ISLP 的神經網路主題。</p>

  <h3>四種架構對照</h3>
{table(["架構", "適合什麼輸入", "關鍵構造", "權重共享嗎", "ISLP 節次"],
       [["單層／多層全連接", "沒有特殊結構的表格資料", "隱藏層 ＋ 激發函數", "沒有", "§10.1–10.2"],
        ["卷積網路（CNN）", "影像等有空間結構的資料", "卷積 ＋ 池化", "有，在空間上", "§10.3"],
        ["遞迴網路（RNN／LSTM）", "文字、時間序列等有順序的資料", "隱藏狀態逐步更新", "有，在時間上", "§10.5"],
        ["詞袋 ＋ 全連接", "文件（丟掉詞序）", "出現與否的長向量", "不適用", "§10.4"]])}

  <h3>官方 lab 的實跑數字</h3>
{table(["資料", "模型", "指標", "數值", "儲存格"],
       [["Hitters", "線性迴歸", "測試 MAE", "259.72", "27"],
        ["Hitters", "lasso（10 折 CV）", "測試 MAE", "235.68", "35"],
        ["Hitters", "單層網路（50 單元、dropout 0.4）", "測試 MAE", "<strong>221.83</strong>", "58"],
        ["MNIST", "多元邏輯斯迴歸", "測試準確率", "0.9161", "97"],
        ["MNIST", "兩層網路（256／128）", "測試準確率", "<strong>0.9620</strong>", "92"],
        ["CIFAR-100", "四組卷積區塊", "測試準確率", "0.4270", "121"],
        ["IMDB", "詞袋 ＋ 兩層網路", "測試準確率", "<strong>0.8450</strong>", "156"],
        ["IMDB", "LSTM", "測試準確率", "0.8400", "185"],
        ["NYSE", "線性 AR（落後 5 期）", "測試 R²", "0.4129", "196"],
        ["NYSE", "線性 AR ＋ 星期幾", "測試 R²", "<strong>0.4596</strong>", "200"],
        ["NYSE", "RNN（12 維隱藏狀態）", "測試 R²", "0.4150", "219"],
        ["NYSE", "非線性 AR", "測試 R²", "0.4660", "228"]])}
  <p style="font-size:.82rem;color:var(--muted);">這些是官方 lab 的實跑結果，
  <strong>跟課本表格的數字不一樣</strong>：Table 10.1 的 MNIST 錯誤率是 1.8%（此處 3.8%），
  Table 10.2 的 Hitters MAE 是線性 254.7／lasso 252.3／神經網路 257.4。
  差別來自切分、epoch 數與套件版本。引用時要說清楚是哪一組。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["單層網路", "$f(X) = \\beta_0 + \\sum_k \\beta_k g(w_{k0} + \\sum_j w_{kj}X_j)$",
         "式 10.1"],
        ["ReLU", "$g(z) = \\max(0, z)$", "式 10.5"],
        ["Sigmoid", "$g(z) = e^z/(1+e^z)$", "式 10.3，就是邏輯斯函數"],
        ["Softmax", "$f_m(X) = e^{Z_m} / \\sum_\\ell e^{Z_\\ell}$", "式 10.13，加常數不變"],
        ["交叉熵", "$-\\sum_i \\sum_m y_{im} \\log f_m(x_i)$", "式 10.14，M = 2 時退回邏輯斯"],
        ["平方誤差目標", "$R(\\theta) = \\tfrac12 \\sum_i (y_i - f_\\theta(x_i))^2$", "式 10.22，非凸"],
        ["梯度下降更新", "$\\theta \\leftarrow \\theta - \\rho \\nabla R(\\theta)$",
         "式 10.23，ρ 是學習率"],
        ["全連接層參數量", "$(a+1) \\times b$", "a 個輸入接到 b 個輸出，+1 是偏置"],
        ["卷積層參數量", "$(k^2 c_{in} + 1) \\times c_{out}$", "跟影像大小無關"]])}

{info("重點回顧", '''<strong>1. 神經網路是線性模型套非線性再組合一次。</strong>
  把 g 拿掉就退回線性迴歸；非線性只能從 g 進來，加總本身不會產生它。<br>
  <strong>2. 權重共享是 CNN 與 RNN 的共同心臟。</strong>
  一個在空間上共享、一個在時間上共享，兩者都透過架構指定權重共享的方式。<br>
  <strong>3. 雙下降需要連同解的選擇方式一起看。</strong>
  第二次下降與最小範數解比較平滑有關；增加參數後如何選解也需交代；
  同一個例子改用嶺迴歸還會更好。''')}

{info("使用時的檢查", '''<strong>先跑基準再跑網路。</strong>ISLP 每個例子都先給線性模型或 lasso 的數字，
  沒有基準線你不會知道網路是好是壞。<strong>輸入一定要標準化</strong>，統計量只能從訓練資料算。
  <strong>預測前記得 <code>model.eval()</code></strong>，否則 dropout 還開著、
  預測會帶隨機性。<strong>固定隨機種子</strong>：非凸最佳化換個種子就換個答案，
  官方 lab 用 <code>seed_everything</code> 加 <code>deterministic=True</code>。''', "warm")}

  <p class="ver-note">本頁的「預期輸出」逐字取自
  <a href="{LAB_URL}" target="_blank" rel="noopener">課本官方的英文 lab</a>
  （<code>{LAB}</code>，intro-stat-learning/ISLP_labs，BSD 2-Clause，
  釘 commit <code>6bf6160</code>）的實跑結果——<strong>本課沒有教第 10 章，
  所以這一章沒有中文 lab</strong>，其餘各章用的都是課程 lab。每張卡下方的「來源」
  標了儲存格編號，可以直接回去對。雙下降的圖表資料由
  <code>tools/frames/gen_deeplearning.py</code> 在固定種子下產生。</p>
"""

PAGEJS = r"""
/* ---------- 共用小工具 ----------
   stats.css 的 .viz-svg .dot / .fit / .resid 是 CSS 宣告，優先權高於 SVG 的呈現屬性。
   所以只要想自己指定 stroke 或 fill，就必須傳一個 CSS 裡沒有定義的 class（本頁一律 w11 開頭）。 */
const w11POS = 'var(--pt-a)';      // 正權重／正值
const w11NEG = 'var(--pt-b)';      // 負權重／負值
const w11OFF = 'var(--muted)';     // 關掉／零

function w11act(kind, z) {
  if (kind === 'relu') return Math.max(0, z);
  if (kind === 'sigmoid') return 1 / (1 + Math.exp(-z));
  if (kind === 'tanh') return Math.tanh(z);
  return z;
}
function w11actName(kind) {
  return { relu: 'ReLU', sigmoid: 'Sigmoid', tanh: 'tanh', id: '恆等' }[kind];
}
/* 千分位。頁面到處要印參數量。 */
function w11comma(v) {
  return String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/* ---------- P01 單層網路的前向傳播 ---------- */
const w11fwdW = (() => {
  // 權重固定（固定種子），這個元件要看的是輸入怎麼變成輸出，不是權重怎麼學
  const rand = HC.stat.lcg(1001);
  const w = [], b = [];
  for (let k = 0; k < 3; k++) {
    const row = [];
    for (let j = 0; j < 4; j++) row.push(Math.round((rand() * 2.4 - 1.2) * 100) / 100);
    w.push(row);
    b.push(Math.round((rand() * 1.2 - 0.6) * 100) / 100);
  }
  return { w: w, b: b, beta: [1.1, -0.9, 0.7], beta0: 0.2 };
})();
let w11fwdX = [1.0, -0.6, 0.4, 1.4];
let w11fwdSvc = null;
const w11fwdIX = 90, w11fwdHX = 320, w11fwdOX = 545;

function w11fwdSetup() {
  w11fwdSvc = HC.svg('w11fwdSvg', { h: 400 });
  if (!w11fwdSvc) return;
  w11fwdSvc.domain([0, 620], [0, 400]);
  w11fwdSvc.layer('edge');
  w11fwdSvc.layer('node');
  w11fwdSvc.layer('lab');
}
function w11fwdReset() {
  w11fwdX = [1.0, -0.6, 0.4, 1.4];
  const sel = $('w11fwdSel'); if (sel) sel.value = 'relu';
  const b1 = $('w11fwdB1'); if (b1) b1.value = 0;
  w11fwdDraw();
}
function w11fwdY(i) { return 70 + i * 78; }          // 輸入節點的縱向位置
function w11fwdHY(k) { return 108 + k * 92; }        // 隱藏節點

function w11fwdDraw() {
  const s = w11fwdSvc;
  if (!s) return;
  const kind = $('w11fwdSel') ? $('w11fwdSel').value : 'relu';
  const b1 = $('w11fwdB1') ? parseFloat($('w11fwdB1').value) : 0;
  if ($('w11fwdB1v')) $('w11fwdB1v').textContent = HC.fmt(b1, 1);

  const bias = w11fwdW.b.slice(); bias[0] = b1;
  const z = [], a = [];
  for (let k = 0; k < 3; k++) {
    let zz = bias[k];
    for (let j = 0; j < 4; j++) zz += w11fwdW.w[k][j] * w11fwdX[j];
    z.push(zz); a.push(w11act(kind, zz));
  }
  let out = w11fwdW.beta0;
  for (let k = 0; k < 3; k++) out += w11fwdW.beta[k] * a[k];

  const ge = s.clearLayer('edge'), gn = s.clearLayer('node'), gl = s.clearLayer('lab');
  // 連線：粗細代表 |w|，顏色代表正負
  for (let k = 0; k < 3; k++) {
    for (let j = 0; j < 4; j++) {
      const w = w11fwdW.w[k][j];
      s.add('line', { cls: 'w11edge', x1: w11fwdIX, y1: w11fwdY(j), x2: w11fwdHX, y2: w11fwdHY(k),
                      stroke: w >= 0 ? w11POS : w11NEG, 'stroke-width': 0.6 + 2.4 * Math.abs(w),
                      opacity: 0.5 }, ge);
    }
    const bt = w11fwdW.beta[k];
    s.add('line', { cls: 'w11edge', x1: w11fwdHX, y1: w11fwdHY(k), x2: w11fwdOX, y2: 200,
                    stroke: bt >= 0 ? w11POS : w11NEG, 'stroke-width': 0.6 + 2.4 * Math.abs(bt),
                    opacity: 0.62 }, ge);
  }
  // 輸入節點（可拖）
  for (let j = 0; j < 4; j++) {
    const node = s.add('circle', { cls: 'w11node', cx: w11fwdIX, cy: w11fwdY(j), r: 17,
                                   fill: 'var(--card)', stroke: 'var(--ink)', 'stroke-width': 2 }, gn);
    s.add('text', { cls: 'w11ntxt', x: w11fwdIX, y: w11fwdY(j) + 5, 'text-anchor': 'middle',
                    'font-size': 13, 'font-family': HC.MONO, fill: 'var(--ink)' }, gn)
      .textContent = HC.fmt(w11fwdX[j], 1);
    s.add('text', { cls: 'w11ntxt', x: w11fwdIX - 30, y: w11fwdY(j) + 5, 'text-anchor': 'end',
                    'font-size': 13, fill: 'var(--muted)' }, gl)
      .textContent = 'X' + '₁₂₃₄'[j];
    HC.drag(node, s, (pt) => {
      if (pt.y === null) return;
      // 拖曳回傳的是資料座標；這個 svg 的定義域就是 viewBox，所以直接把 y 換算成 −2…2
      const v = Math.max(-2, Math.min(2, (200 - pt.y) / 70));
      w11fwdX[j] = Math.round(v * 10) / 10;
      w11fwdDraw();
    }, { lockX: true });
  }
  // 隱藏節點：半徑隨 |A| 變化，A = 0 時是灰的
  for (let k = 0; k < 3; k++) {
    const mag = Math.min(1, Math.abs(a[k]) / 2.2);
    const dead = Math.abs(a[k]) < 1e-9;
    s.add('circle', { cls: 'w11node', cx: w11fwdHX, cy: w11fwdHY(k), r: 15 + 13 * mag,
                      fill: dead ? w11OFF : (a[k] >= 0 ? w11POS : w11NEG),
                      stroke: '#fff', 'stroke-width': 2, opacity: dead ? 0.45 : 0.9 }, gn);
    // 死掉的單元填的是淺灰，白字會看不見，改用深色
    s.add('text', { cls: 'w11ntxt', x: w11fwdHX, y: w11fwdHY(k) + 5, 'text-anchor': 'middle',
                    'font-size': 12, 'font-family': HC.MONO,
                    fill: dead ? 'var(--ink)' : '#fff' }, gn)
      .textContent = HC.fmt(a[k], 2);
    s.add('text', { cls: 'w11ntxt', x: w11fwdHX, y: w11fwdHY(k) - 34, 'text-anchor': 'middle',
                    'font-size': 12, fill: 'var(--muted)' }, gl)
      .textContent = 'A' + '₁₂₃'[k] + (dead ? '（死掉）' : '');
  }
  // 輸出
  s.add('circle', { cls: 'w11node', cx: w11fwdOX, cy: 200, r: 24, fill: 'var(--accent2)',
                    stroke: '#fff', 'stroke-width': 2.5 }, gn);
  s.add('text', { cls: 'w11ntxt', x: w11fwdOX, y: 205, 'text-anchor': 'middle',
                  'font-size': 13, 'font-family': HC.MONO, fill: '#fff' }, gn)
    .textContent = HC.fmt(out, 2);
  s.add('text', { cls: 'w11ntxt', x: w11fwdOX, y: 160, 'text-anchor': 'middle',
                  'font-size': 12, fill: 'var(--muted)' }, gl).textContent = 'f(X)';
  s.txtPx(w11fwdIX - 46, 26, '輸入層 p = 4', { cls: 'axtitle' }, gl);
  s.txtPx(w11fwdHX - 46, 26, '隱藏層 K = 3', { cls: 'axtitle' }, gl);
  s.txtPx(w11fwdOX - 22, 26, '輸出', { cls: 'axtitle' }, gl);

  $('w11fwdG').textContent = w11actName(kind);
  $('w11fwdA1').textContent = HC.fmt(z[0], 2) + ' → ' + HC.fmt(a[0], 3);
  $('w11fwdA2').textContent = HC.fmt(z[1], 2) + ' → ' + HC.fmt(a[1], 3);
  $('w11fwdA3').textContent = HC.fmt(z[2], 2) + ' → ' + HC.fmt(a[2], 3);
  $('w11fwdOut').textContent = HC.fmt(out, 3);
  $('w11fwdNp').textContent = '3 × (4+1) + (3+1) = 19';

  const dead = a.filter(v => Math.abs(v) < 1e-9).length;
  let msg = '目前 g 是 ' + w11actName(kind) + '。輸出 f(X) = ' + HC.fmt(out, 3) + '。';
  if (kind === 'id') {
    msg += ' <b>g 是恆等函數時，整個網路其實只是 X₁–X₄ 的一個線性函數</b>'
      + '——隱藏層完全沒有加到任何東西。';
  } else if (dead > 0) {
    msg += ' <b>有 ' + dead + ' 個單元死掉了</b>（A = 0）：它的加權和是負的，'
      + 'ReLU 把它壓成 0，導數也是 0，所以那個單元在訓練時學不動。';
  } else {
    msg += ' 圓圈愈大代表 A_k 的絕對值愈大；把 w₁₀ 往左拉會看到 A₁ 被 ReLU 壓成 0。';
  }
  setStatus('w11fwdStatus', msg);
}

/* ---------- P02 參數量計算器 ---------- */
let w11paramSvc = null;
function w11paramSetup() {
  w11paramSvc = HC.svg('w11paramSvg', { h: 380 });
  if (!w11paramSvc) return;
  w11paramSvc.domain([0, 620], [0, 380]);
  w11paramSvc.layer('bar');
  w11paramSvc.layer('lab');
}
function w11paramReset() {
  if ($('w11paramH1')) $('w11paramH1').value = 256;
  if ($('w11paramH2')) $('w11paramH2').value = 128;
  w11paramDraw();
}
function w11paramDraw() {
  const s = w11paramSvc;
  const h1 = $('w11paramH1') ? parseInt($('w11paramH1').value, 10) : 256;
  const h2 = $('w11paramH2') ? parseInt($('w11paramH2').value, 10) : 128;
  if ($('w11paramH1v')) $('w11paramH1v').textContent = h1;
  if ($('w11paramH2v')) $('w11paramH2v').textContent = h2;

  const p1 = (784 + 1) * h1, p2 = (h1 + 1) * h2, p3 = (h2 + 1) * 10;
  const tot = p1 + p2 + p3, mlr = 785 * 9;

  $('w11paramL1').textContent = '(784+1) × ' + h1 + ' = ' + w11comma(p1);
  $('w11paramL2').textContent = '(' + h1 + '+1) × ' + h2 + ' = ' + w11comma(p2);
  $('w11paramL3').textContent = '(' + h2 + '+1) × 10 = ' + w11comma(p3);
  $('w11paramTot').textContent = w11comma(tot);
  $('w11paramRatio').textContent = HC.fmt(tot / mlr, 1) + ' 倍';

  if (s) {
    const gb = s.clearLayer('bar'), gl = s.clearLayer('lab');
    // 上半：網路示意（方塊高度 ∝ 該層單元數，開根號壓縮視覺差距）
    const layers = [{ n: 784, x: 70, t: '輸入 784' }, { n: h1, x: 220, t: 'h₁ = ' + h1 },
                    { n: h2, x: 370, t: 'h₂ = ' + h2 }, { n: 10, x: 520, t: '輸出 10' }];
    layers.forEach(L => {
      const hh = 18 + 120 * Math.sqrt(L.n / 784);
      s.add('rect', { cls: 'w11lbox', x: L.x - 34, y: 130 - hh / 2, width: 68, height: hh, rx: 6,
                      fill: 'var(--accent2)', opacity: 0.28, stroke: 'var(--accent2)',
                      'stroke-width': 2 }, gb);
      s.add('text', { cls: 'w11ntxt', x: L.x, y: 130 + hh / 2 + 18, 'text-anchor': 'middle',
                      'font-size': 12, fill: 'var(--muted)' }, gl).textContent = L.t;
    });
    // 下半：三段式長條，寬度 ∝ 各層參數占比
    const segs = [{ v: p1, c: 'var(--pt-a)', t: '第 1 層' },
                  { v: p2, c: 'var(--pt-b)', t: '第 2 層' },
                  { v: p3, c: 'var(--pt-c)', t: '輸出層' }];
    let x = 60;
    const W = 500;
    s.txtPx(60, 250, '參數量占比（總共 ' + w11comma(tot) + ' 個）', { cls: 'axtitle' }, gl);
    segs.forEach(sg => {
      const w = W * sg.v / tot;
      s.add('rect', { cls: 'w11pbar', x: x, y: 262, width: Math.max(1, w), height: 36,
                      fill: sg.c, opacity: 0.85 }, gb);
      if (w > 62) {
        s.add('text', { cls: 'w11ntxt', x: x + w / 2, y: 285, 'text-anchor': 'middle',
                        'font-size': 12, 'font-family': HC.MONO, fill: '#fff' }, gl)
          .textContent = HC.pct(sg.v / tot, 0);
      }
      s.add('text', { cls: 'w11ntxt', x: x + w / 2, y: 316, 'text-anchor': 'middle',
                      'font-size': 11, fill: 'var(--muted)' }, gl)
        .textContent = w > 52 ? sg.t : '';
      x += w;
    });
    // 對照：多元邏輯斯迴歸的長條，同一個比例尺
    const wm = W * mlr / tot;
    s.add('rect', { cls: 'w11pbar', x: 60, y: 336, width: Math.max(2, wm), height: 20,
                    fill: 'var(--muted)', opacity: 0.7 }, gb);
    s.txtPx(60 + Math.max(2, wm) + 8, 351,
            '多元邏輯斯迴歸 7,065 個', { cls: 'axlab' }, gl);
  }

  setStatus('w11paramStatus',
    '總共 ' + w11comma(tot) + ' 個參數，是多元邏輯斯迴歸（7,065 個）的 '
    + HC.fmt(tot / mlr, 1) + ' 倍。<b>其中 ' + HC.pct(p1 / tot, 0)
    + ' 集中在第一層</b>——因為 784 這個輸入維度最大。'
    + (h1 === 256 && h2 === 128
      ? ' 這組預設值就是 ISLP §10.2 的架構，課本印的總數正是 235,146。'
      : ' 回到 256／128 就會看到課本印的 235,146。'));
}

/* ---------- P03 卷積與池化 ---------- */
const w11convKernels = {
  vedge: { t: '垂直邊緣', k: [[1, 0, -1], [1, 0, -1], [1, 0, -1]] },
  hedge: { t: '水平邊緣', k: [[1, 1, 1], [0, 0, 0], [-1, -1, -1]] },
  blur: { t: '平均（模糊）', k: [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]] },
  sharp: { t: '銳化', k: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]] },
};
const w11convImg = (() => {
  // 8×8 的合成影像：左半亮、右半暗，中間插一條亮縫，足以讓四個濾波器都看得出差別
  const g = [];
  for (let r = 0; r < 8; r++) {
    const row = [];
    for (let c = 0; c < 8; c++) {
      let v = c < 4 ? 0.85 : 0.15;
      if (c === 5) v = 0.8;
      if (r === 0 || r === 7) v = 0.5;
      row.push(v);
    }
    g.push(row);
  }
  return g;
})();
let w11convSvc = null, w11convKey = 'vedge';
const w11convOUT = 6;   // 8 − 3 + 1

function w11convConv(kern) {
  const out = [];
  for (let r = 0; r < w11convOUT; r++) {
    const row = [];
    for (let c = 0; c < w11convOUT; c++) {
      let v = 0;
      for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) v += kern[a][b] * w11convImg[r + a][c + b];
      row.push(v);
    }
    out.push(row);
  }
  return out;
}
function w11convPool(fm) {
  const out = [];
  for (let r = 0; r < 3; r++) {
    const row = [];
    for (let c = 0; c < 3; c++) {
      row.push(Math.max(fm[2 * r][2 * c], fm[2 * r][2 * c + 1],
                        fm[2 * r + 1][2 * c], fm[2 * r + 1][2 * c + 1]));
    }
    out.push(row);
  }
  return out;
}
function w11convSetup() {
  w11convSvc = HC.svg('w11convSvg', { h: 420 });
  if (!w11convSvc) return;
  w11convSvc.domain([0, 620], [0, 420]);
  w11convSvc.layer('cell');
  w11convSvc.layer('box');
  w11convSvc.layer('lab');
}
function w11convFrames() {
  const fr = [];
  for (let i = 0; i < w11convOUT * w11convOUT; i++) fr.push({ i: i, pool: false });
  fr.push({ i: w11convOUT * w11convOUT - 1, pool: true });
  return fr;
}
/* 輸入影像是純亮度，直接灰階。 */
function w11convGrey(v) {
  const g = Math.round(255 * Math.max(0, Math.min(1, v)));
  return 'rgb(' + g + ',' + g + ',' + g + ')';
}
/* 特徵圖要用**以 0 為中心**的發散色階，不能用「最小值→黑」。
   邊緣濾波器的輸出有正有負，而 0 常常就是最小值——第一版用線性灰階，
   內積為 0 的第一格被畫成全黑，看起來像壞掉。白＝0，紅＝正，藍＝負。 */
function w11convDiv(v, amax) {
  const t = Math.max(-1, Math.min(1, v / (amax || 1)));
  const a = Math.abs(t);
  const c = t >= 0 ? [201, 79, 61] : [58, 84, 140];
  const m = k => Math.round(255 + (c[k] - 255) * a);
  return 'rgb(' + m(0) + ',' + m(1) + ',' + m(2) + ')';
}
function w11convApply(f) {
  const s = w11convSvc;
  if (!s) return;
  const kern = w11convKernels[w11convKey].k;
  const fm = w11convConv(kern), pooled = w11convPool(fm);
  let amax = 0;
  fm.forEach(r => r.forEach(v => { amax = Math.max(amax, Math.abs(v)); }));

  const gc = s.clearLayer('cell'), gb = s.clearLayer('box'), gl = s.clearLayer('lab');
  const CS = 26, IX = 40, IY = 90, FX = 300, FY = 90, PX = 500, PY = 116;
  const done = f.i, rr = Math.floor(done / w11convOUT), cc = done % w11convOUT;

  // 輸入 8×8
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      s.add('rect', { cls: 'w11cc', x: IX + c * CS, y: IY + r * CS, width: CS, height: CS,
                      fill: w11convGrey(w11convImg[r][c]), stroke: 'var(--card-border)',
                      'stroke-width': 0.6, 'shape-rendering': 'crispEdges' }, gc);
    }
  }
  // 目前對齊的 3×3 視窗
  s.add('rect', { cls: 'w11win', x: IX + cc * CS, y: IY + rr * CS, width: 3 * CS, height: 3 * CS,
                  fill: 'none', stroke: 'var(--pt-held)', 'stroke-width': 3 }, gb);

  // 特徵圖 6×6：完整顯示，並標出目前檢查的格子。
  for (let r = 0; r < w11convOUT; r++) {
    for (let c = 0; c < w11convOUT; c++) {
      const idx = r * w11convOUT + c;
      const selected = idx === done;
      s.add('rect', { cls: 'w11cc', x: FX + c * CS, y: FY + r * CS, width: CS, height: CS,
                      fill: w11convDiv(fm[r][c], amax),
                      stroke: selected ? 'var(--accent)' : 'var(--card-border)',
                      'stroke-width': selected ? 3 : 0.6,
                      opacity: 1, 'shape-rendering': 'crispEdges' }, gc);
    }
  }
  s.add('rect', { cls: 'w11win', x: FX + cc * CS, y: FY + rr * CS, width: CS, height: CS,
                  fill: 'none', stroke: 'var(--pt-held)', 'stroke-width': 3 }, gb);

  // 池化結果 3×3（走到最後一格才畫）
  if (f.pool) {
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 3; c++) {
        s.add('rect', { cls: 'w11cc', x: PX + c * CS, y: PY + r * CS, width: CS, height: CS,
                        fill: w11convDiv(pooled[r][c], amax), stroke: 'var(--card-border)',
                        'stroke-width': 0.6, 'shape-rendering': 'crispEdges' }, gc);
      }
    }
    s.txtPx(PX, PY - 12, '2×2 最大池化 → 3×3', { cls: 'axtitle' }, gl);
  }

  s.txtPx(IX, IY - 12, '輸入 8×8（白＝亮）', { cls: 'axtitle' }, gl);
  s.txtPx(FX, FY - 12, '特徵圖 6×6（紅＝正、藍＝負、白＝0）', { cls: 'axtitle' }, gl);
  s.txtPx(IX, 42, '濾波器：' + w11convKernels[w11convKey].t
    + '　（3×3，掃過整張圖都用同一組權重）', { cls: 'axtitle' }, gl);

  $('w11convK').textContent = w11convKernels[w11convKey].t;
  $('w11convPos').textContent = '第 ' + (rr + 1) + ' 列、第 ' + (cc + 1) + ' 行';
  $('w11convVal').textContent = HC.fmt(fm[rr][cc], 3);
  $('w11convSize').textContent = f.pool ? '6×6 → 池化後 3×3' : '(8−3+1)² = 6×6';
  $('w11convNp').textContent = '3×3 + 1 = 10 個';
  $('w11convFc').textContent = '36 × 64 = 2,304 個';

  if (f.pool) {
    setStatus('w11convSvgStatus',
      '掃完了。6×6 的特徵圖經過 2×2 最大池化變成 3×3——'
      + '<b>解析度掉一半，輸出仍保留樣式出現與否的資訊</b>。'
      + '整層從頭到尾只有 10 個參數，跟影像多大無關。');
  } else {
    setStatus('w11convSvgStatus',
      '濾波器對齊第 ' + (rr + 1) + ' 列第 ' + (cc + 1) + ' 行，內積是 '
      + HC.fmt(fm[rr][cc], 3) + '。'
      + '<b>每一格都用同一組 9 個權重</b>，換位置不換權重，這就是權重共享。');
  }
}
function w11convSetK() {
  w11convKey = $('w11convSel').value;
  w11convSelect();
}
function w11convReset() {
  $('w11convRow').value = 1;
  $('w11convCol').value = 1;
  $('w11convPool').checked = false;
  w11convSelect();
}
function w11convSelect() {
  const r = Number($('w11convRow').value) - 1;
  const c = Number($('w11convCol').value) - 1;
  w11convApply({i: r * w11convOUT + c, pool: $('w11convPool').checked});
}

/* ---------- P05 梯度下降（習題 6 的函數）----------
   R(β) = sin β + β/10，R′(β) = cos β + 0.1。駐點在 cos β = −0.1，也就是
   β = ±1.671 + 2kπ。要小心哪些是極小、哪些是極大（R″ = −sin β）：
     β = −1.671 → R″ > 0 → 極小，R = −1.162   ← 這是 [−6, 6] 裡最低的
     β = +1.671 → R″ < 0 → 極大
     β = +4.612 → R″ > 0 → 極小，R = −0.534
     β = −4.612 → R″ < 0 → 極大
   第一版把 +1.671 與 −4.612 當成極小畫參考線，於是 β⁰ = 2.3 明明乖乖收斂到
   4.612，狀態列卻報「學習率太大」。 */
const w11gdMIN = [-1.671, 4.612];
function w11gdR(b) { return Math.sin(b) + b / 10; }
function w11gdD(b) { return Math.cos(b) + 0.1; }
function w11gdSync() {
  const b0 = parseFloat($('w11gdB0s').value), rho = parseFloat($('w11gdRhos').value);
  $('w11gdB0v').textContent = HC.fmt(b0, 1);
  $('w11gdRhov').textContent = HC.fmt(rho, 2);
  $('w11gdB0').textContent = HC.fmt(b0, 2);
  $('w11gdRho').textContent = HC.fmt(rho, 2);
  w11gdDraw([]);
}
function w11gdReset() {
  $('w11gdB0s').value = 2.3;
  $('w11gdRhos').value = 0.1;
  w11gdSync();
}
function w11gdDraw(path) {
  const xs = HC.stat.seq(-6, 6, 241);
  const curve = xs.map(b => ({ x: Math.round(b * 1000) / 1000, y: w11gdR(b) }));
  const sets = [{ label: 'R(β) = sin(β) + β/10', data: curve, borderColor: HC.tok.accent2,
                  backgroundColor: HC.tok.accent2, borderWidth: 2.8, pointRadius: 0, fill: false }];
  if (path.length) {
    sets.push({ label: '梯度下降的軌跡', data: path.map(b => ({ x: b, y: w11gdR(b) })),
                borderColor: HC.tok.accent3, backgroundColor: HC.tok.accent3,
                borderWidth: 1.6, pointRadius: 4, showLine: true, fill: false });
    sets.push({ label: '終點', data: [{ x: path[path.length - 1], y: w11gdR(path[path.length - 1]) }],
                borderColor: HC.tok.held, backgroundColor: HC.tok.held,
                borderWidth: 0, pointRadius: 9, showLine: false, fill: false });
  }
  HC.line('w11gdChart', { datasets: sets }, {
    interaction: { mode: 'nearest', intersect: false },
    scales: {
      x: { type: 'linear', min: -6, max: 6, title: { display: true, text: 'β' } },
      y: { min: -1.8, max: 1.8, title: { display: true, text: 'R(β)' } },
    },
  });
  HC.refs('w11gdChart', [HC.vline(w11gdMIN[0], '極小 β ≈ −1.67'),
                         HC.vline(w11gdMIN[1], '極小 β ≈ 4.61', null, 1)]);
}
function w11gdRun() {
  let b = parseFloat($('w11gdB0s').value);
  const rho = parseFloat($('w11gdRhos').value);
  const path = [Math.round(b * 1000) / 1000];
  let steps = 0;
  for (let i = 0; i < 200; i++) {
    const nb = b - rho * w11gdD(b);
    if (!isFinite(nb) || Math.abs(nb) > 40) break;
    steps++;
    b = nb;
    path.push(Math.round(b * 1000) / 1000);
    if (Math.abs(w11gdD(b)) < 1e-5) break;
  }
  w11gdDraw(path);
  let near = null;
  w11gdMIN.forEach(m => { if (Math.abs(b - m) < 0.08) near = m; });
  $('w11gdSteps').textContent = steps + ' 步';
  $('w11gdEnd').textContent = HC.fmt(b, 3);
  $('w11gdVal').textContent = HC.fmt(w11gdR(b), 3);
  $('w11gdGlobal').textContent = near === w11gdMIN[0] ? '是（−6…6 之間最低）'
    : (near === w11gdMIN[1] ? '否，收斂到較高的局部極小' : '還沒收斂');
  let msg = '從 β⁰ = ' + HC.fmt(parseFloat($('w11gdB0s').value), 2) + ' 出發、學習率 '
    + HC.fmt(rho, 2) + '，走了 ' + steps + ' 步收在 β ≈ ' + HC.fmt(b, 3) + '。';
  if (near === w11gdMIN[1]) {
    msg += ' <b>這次收斂到較高的局部極小</b>——左邊 β ≈ −1.67 那個谷底更低'
      + '（R = −1.162 對 −0.534）。把起點改成 1.4 就會掉到那邊去，'
      + '這正是習題 6(c) 與 6(d) 要你比較的事。';
  } else if (near === w11gdMIN[0]) {
    msg += ' 這次掉進了比較低的那個谷底（R = −1.162）。'
      + '把起點改回 2.3 會收到右邊那個比較淺的極小。';
  } else {
    msg += ' <b>尚未收斂：目前學習率過大，參數持續震盪。</b>'
      + '把 ρ 調小一點再試一次。';
  }
  setStatus('w11gdStatus', msg);
}

/* ---------- P06 雙下降 ---------- */
let w11ddMode = 'err';
/* 對數軸只有 10 的整數次方值得標，其餘留空。
   不設 callback 的話 Chart.js 會印成「1,000.000000」「0.000001」，一整排小數點。 */
const w11ddFLOOR = 1e-5;
function w11ddTick(v) {
  const e = Math.log10(v);
  if (Math.abs(e - Math.round(e)) > 1e-9) return '';
  const sup = String(Math.round(e)).replace('-', '⁻')
    .replace(/[0-9]/g, d => '⁰¹²³⁴⁵⁶⁷⁸⁹'[+d]);
  return Math.round(e) === 0 ? '1' : '10' + sup;
}
function w11ddShow(mode) {
  w11ddMode = mode;
  const F = FRAMES_w11dd;
  if (mode === 'err') {
    HC.line('w11ddChart', {
      labels: F.ds,
      datasets: [
        { label: '測試 MSE', data: F.test, borderColor: HC.tok.test, backgroundColor: HC.tok.test,
          borderWidth: 3, pointRadius: 2.5, fill: false },
        { label: '訓練 MSE（d ≥ 20 之後其實是 0）',
          data: F.train.map(v => Math.max(v, w11ddFLOOR)), borderColor: HC.tok.train,
          backgroundColor: HC.tok.train, borderWidth: 2.4, pointRadius: 2, fill: false },
      ],
    }, {
      scales: {
        x: { title: { display: true, text: '自然樣條的自由度 d' } },
        y: { type: 'logarithmic', min: w11ddFLOOR, max: 4000,
             ticks: { callback: w11ddTick, autoSkip: false },
             title: { display: true, text: 'MSE（對數刻度）' } },
      },
    });
    HC.refs('w11ddChart', [HC.vline(F.ds.indexOf(F.thr), '內插門檻 d = n = ' + F.thr, null, 1)]);
    setStatus('w11ddStatus',
      '測試誤差（紅）在 d = ' + F.thr + ' 附近衝到最高，然後<b>第二次下降</b>。'
      + '訓練誤差（藍）從 d = ' + F.thr + ' 開始就是 0——對數軸畫不出 0，'
      + '所以它被壓在 10⁻⁵ 那條底線上（實際值是 10⁻²⁸ 的量級）。'
      + '曲線是 ' + F.reps + ' 組重抽樣的平均：單一次模擬只有 20 筆資料，'
      + '尖峰位置會被抽樣運氣帶偏。');
  } else {
    const d = $('w11ddSel') ? $('w11ddSel').value : '20';
    const fit = F.fits[d];
    HC.line('w11ddChart', {
      datasets: [
        { label: '資料生成函數 f(X) = sin(X)', data: F.grid.map((x, i) => ({ x: x, y: F.truth[i] })),
          borderColor: HC.tok.truef, backgroundColor: HC.tok.truef, borderWidth: 2.4,
          pointRadius: 0, borderDash: [7, 4], fill: false },
        { label: '配適的樣條（d = ' + d + '）',
          data: F.grid.map((x, i) => ({ x: x, y: fit.y[i] })),
          borderColor: HC.tok.accent3, backgroundColor: HC.tok.accent3, borderWidth: 3,
          pointRadius: 0, fill: false },
        { label: '20 筆訓練資料', data: F.xtr.map((x, i) => ({ x: x, y: F.ytr[i] })),
          borderColor: HC.tok.accent2, backgroundColor: HC.tok.accent2, borderWidth: 0,
          pointRadius: 5, showLine: false, fill: false },
      ],
    }, {
      scales: {
        x: { type: 'linear', min: -5, max: 5, title: { display: true, text: 'X' } },
        y: { min: -3.2, max: 3.2, title: { display: true, text: 'Y' } },
      },
    });
    HC.refs('w11ddChart', []);
    const wild = d === '20' ? '——<b>它是唯一能穿過 20 個點的樣條，所以只能長這樣</b>'
      : (parseInt(d, 10) > 20
        ? '——同樣穿過每一個點，但這是無限多種穿法裡最平滑的那一種'
        : '——自由度不夠，它沒有穿過每一個點');
    setStatus('w11ddStatus',
      'd = ' + d + ' 的配適曲線，係數平方和 Σβ² = ' + fit.l2 + wild + '。'
      + '切到 d = 20 再切到 d = 42，比較那條橘線的起伏。');
  }
}
function w11ddInit() {
  const F = FRAMES_w11dd;
  const at = d => HC.fmt(F.test[F.ds.indexOf(d)], 2);
  $('w11dd8').textContent = at(8);
  $('w11dd19').textContent = at(19);
  $('w11dd20').textContent = at(20);
  $('w11dd42').textContent = at(42);
  $('w11dd100').textContent = at(100);
  $('w11ddSnr').textContent = F.snr + '（課本說 5.9）';
  w11ddShow('err');
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。 */
w11fwdSetup();
w11fwdDraw();
w11paramSetup();
w11paramDraw();
w11convSetup();
w11convReset();
HC.ready(() => {
  w11gdSync();
  w11ddInit();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("deep_learning", BODIES, PAGEJS, frames())
