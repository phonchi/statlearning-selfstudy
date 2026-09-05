#!/usr/bin/env python3
"""introduction.html（ISLP 第 1 章）完整自學充實。冪等。

內容依據：講義 01_Introduction.pdf（42 頁）、Ch01-lab-zh.ipynb、ISLP 第 1 章
（書上 p.2–13）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_intro.py 在固定種子下產生。

這一章最後寫，因為課程地圖元件要連到其他九頁真實存在的 anchor。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 1
LAB = "Ch01-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_intro.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_intro.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_intro.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue：課程地圖 ─────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>這門課有十個主題，但它們不是十件無關的事。全部可以放進<strong>一張表</strong>：
  你手上有沒有想預測的 y？y 是數字還是類別？你要的是準確度還是可解釋性？
  答案決定你該翻到哪一章。</p>

  <p>這一章不先列一張可以篩選的課程地圖；那只是在重複網站導覽。
  接下來直接用三個會真正影響分析選擇的問題組織內容：有沒有 y、y 是數字還是類別、
  以及目標是預測還是推論。</p>

{info("這一頁要做的四件事", '''<strong>1. 分清監督式與非監督式。</strong>有 y 就是監督式，沒有 y 就是非監督式。<br>
  <strong>2. 分清迴歸與分類。</strong>y 是數字就是迴歸，y 是類別就是分類。<br>
  <strong>3. 分清預測與推論。</strong>你要「猜得準」還是「看懂關係」？這決定你選什麼模型。<br>
  <strong>4. 認識符號與三份資料。</strong>n、p、Wage、Smarket、NCI60。後面每一章都會再遇到。''')}
"""

# ── P01 監督式與非監督式 ──────────────────────────────────────────────
BODIES["supervised"] = f"""
  <p>整門課最大的分水嶺只有一個問題：<strong>你手上有沒有「答案」？</strong></p>

  <p><strong>監督式學習</strong>（supervised learning）：每一筆資料都有一個
  你想預測的目標值 y。薪資、股價漲跌、房價、腫瘤是否為惡性。這些都有明確的答案，
  可以拿去對照模型猜得對不對。第 2 到 9 章全部是監督式。</p>

  <p><strong>非監督式學習</strong>（unsupervised learning）：只有 X，沒有 y。
  你不是要預測什麼，而是想知道「這堆資料裡有什麼結構」。
  哪些顧客是同一群？6830 個基因能不能壓成 2 個維度來看？
  第 12 章講這個。</p>

{info("為什麼這個分界這麼重要", '''因為<strong>沒有 y 就沒有「對錯」</strong>。<br><br>
  監督式學習可以算誤差：把預測值跟真實的 y 相減就好，所以你能用交叉驗證選模型、
  能報告測試誤差、能說「這個模型比那個好」。<br><br>
  非監督式沒有這個奢侈。分成 3 群還是 5 群「比較對」？沒有客觀答案——
  只有「對你的用途有不有用」。第 12 章會反覆碰到這件事。''')}

{table(["", "監督式", "非監督式"],
       [["資料長相", "X 與 y 都有", "只有 X"],
        ["在問什麼", "給定 X，y 是多少？", "X 裡面有什麼結構？"],
        ["怎麼知道做得好不好", "跟真實的 y 比，算誤差", "<strong>沒有客觀標準</strong>"],
        ["本課章節", "第 2–9 章", "第 12 章"],
        ["例子", "從年齡預測薪資、從 Lag 預測漲跌", "把 6830 個基因壓成 2 維、把顧客分群"]])}

{qa("觀念釐清", [
    ("Q：半監督式（semi-supervised）是什麼？本課會教嗎？",
     "<p>現實中常見的情況是：<strong>少數資料有 y，大量資料只有 X</strong>。"
     "例如你有 100 萬張照片但只有 1000 張被標註過——標註很貴。"
     "半監督式學習就是設法同時用上這兩批資料。</p>"
     "<p>本課不教（ISLP 也只在第 1 章提一句）。但值得知道它存在，"
     "因為實務上「資料很多、標註很少」幾乎是常態。</p>"),
    ("Q：分群（clustering）跟分類（classification）到底差在哪？名字很像。",
     "<p>差在<strong>類別是誰給的</strong>。</p>"
     "<p><strong>分類</strong>是監督式：類別標籤本來就在資料裡（這封信是垃圾信、"
     "這個腫瘤是惡性），你要學的是「怎麼從 X 猜出那個既有的標籤」。</p>"
     "<p><strong>分群</strong>是非監督式：<em>沒有</em>標籤，群是演算法自己劃出來的。"
     "劃完之後那些群叫什麼、有什麼意義，要靠你自己解讀。"
     "K-means 給你「第 1 群、第 2 群」，它不會告訴你第 1 群是「高消費客戶」。"
     "那是你看完之後自己命名的。</p>"),
])}

{quiz("qSup", "QUIZ · 監督式與非監督式",
      "醫院想從病歷資料裡「找出幾種還沒被命名的糖尿病亞型」。這是什麼問題？",
      [(True, "非監督式，因為「亞型」還不存在，沒有 y 可以對照",
        "對。要找的東西本身還沒有標籤，這是分群／降維的地盤（第 12 章）。找出來之後怎麼命名、有沒有臨床意義，要靠醫師解讀。這正是非監督式沒有客觀對錯的意思。"),
       (False, "監督式分類，因為最後要把病人分到某個亞型",
        "「最後會得到分組」不等於監督式。決定性的問題是<strong>訓練時有沒有正確答案可以對照</strong>；這裡沒有，所以不是分類而是分群。"),
       (False, "監督式迴歸，因為病歷裡有很多數值變數",
        "X 是數值跟這題無關。監督式與否看的是<strong>有沒有 y</strong>，不是 X 的型態。")])}
"""

# ── P02 迴歸與分類 ────────────────────────────────────────────────────
BODIES["regcls"] = f"""
  <p>確定是監督式之後，第二個問題：<strong>y 是數字還是類別？</strong></p>

  <ul>
    <li><strong>迴歸</strong>（regression）：y 是連續數值。薪資、房價、mpg、租借量。
    誤差用 MSE 這類「差多少」的量來衡量。</li>
    <li><strong>分類</strong>（classification）：y 是類別。漲/跌、良性/惡性、
    14 種癌症型別。誤差用「錯幾個」的錯誤率來衡量。</li>
  </ul>

  <p>大部分方法都有迴歸版與分類版（迴歸樹／分類樹、線性迴歸／邏輯斯迴歸），
  背後的想法一樣，只是把「差多少」換成「錯幾個」。</p>

{table(["方法", "迴歸版", "分類版", "本課章節"],
       [["線性模型", "線性迴歸", "邏輯斯迴歸", "第 3、4 章"],
        ["最近鄰", "KNN 迴歸", "KNN 分類", "第 2、3 章"],
        ["樹", "迴歸樹", "分類樹", "第 8 章"],
        ["集成", "隨機森林迴歸、GBDT", "隨機森林分類、AdaBoost", "第 8 章"],
        ["邊界法", "支持向量迴歸", "支持向量機", "第 9 章"],
        ["誤差怎麼算", "MSE：$\\frac1n\\sum(y_i-\\hat y_i)^2$",
         "錯誤率：$\\frac1n\\sum I(y_i \\ne \\hat y_i)$", "第 2 章"]])}

{info("順序型類別是個灰色地帶", '''教育程度（國中以下 &lt; 高中 &lt; 大學 &lt; 研究所）
  是類別，但它<strong>有順序</strong>。硬編成 1、2、3、4 當數字做迴歸，
  等於假設「高中到大學」跟「大學到研究所」的差距一樣大。那個假設通常不成立。<br><br>
  本課的處理方式是當成類別（第 3 章的質性預測變數、第 4 章的多類別分類）。
  這一頁下面的 Wage 資料就有這個變數，你會看到它跟薪資的關係並不等距。''')}

{quiz("qRegCls", "QUIZ · 迴歸與分類",
      "用歷史資料的「當天有沒有下雨」（0／1）訓練模型，回報明天的降雨機率。這是哪一類問題？",
      [(True, "分類問題；訓練的 y 是二元類別，分類模型也可以輸出機率",
        "對。判斷依據是<strong>訓練資料裡 y 代表什麼</strong>。邏輯斯迴歸先估機率，再視需要選閾值轉成標籤；回報機率不會讓這個二元分類任務變成連續反應的迴歸。"),
       (False, "迴歸問題，因為輸出的機率是 0 到 1 之間的連續值",
        "輸出值連續，不代表訓練的反應變數是連續量。這裡觀測到的是下雨與否，估的是類別機率。若觀測的 y 改成降雨量，才是另一個迴歸任務。"),
       (False, "非監督式問題，因為明天的答案還不知道",
        "未來的 y 未知是預測的常態。監督式與否看的是訓練資料有沒有 y，這裡的歷史資料已有下雨與否的標籤。")])}

"""

# ── P03 預測與推論 ────────────────────────────────────────────────────
BODIES["predinfer"] = f"""
  <p>第三個問題最容易被忽略，但它直接決定你該選什麼模型：
  <strong>你要的是「猜得準」還是「看懂關係」？</strong></p>

  <p><strong>預測</strong>（prediction）：只在乎 $\\hat y$ 準不準，
  $\\hat f$ 內部長什麼樣完全不重要。它可以是一座 500 棵樹的森林。</p>

  <p><strong>推論</strong>（inference）：想知道<em>哪些</em> X 影響 y、影響<em>多大</em>、
  往<em>哪個方向</em>、這個影響<em>可不可信</em>。這時 $\\hat f$ 必須看得懂，
  而且你需要標準誤與 p 值。</p>

{table(["", "預測", "推論"],
       [["在乎什麼", "$\\hat y$ 準不準", "$\\hat f$ 說了什麼"],
        ["模型可以是黑盒嗎", "可以", "<strong>不行</strong>"],
        ["需要標準誤與 p 值嗎", "通常不需要", "<strong>需要</strong>"],
        ["典型方法", "隨機森林、GBDT、SVM", "線性迴歸、邏輯斯迴歸、GAM"],
        ["典型問法", "這位客戶會不會流失？", "價格每漲 1 元，需求掉多少？"],
        ["本課章節", "第 5、8、9 章", "第 3、4、7 章"]])}

{qa("觀念釐清", [
    ("Q：為什麼「準確度」與「可解釋性」常常要二選一？",
     "<p>因為讓模型變準的手段，多半就是讓它變複雜。</p>"
     "<p>線性迴歸只有 p + 1 個係數，每一個都能講成一句人話："
     "「其他條件不變下，X₁ 每增加 1 單位，y 平均增加 β₁」。"
     "隨機森林有 500 棵樹、每棵樹幾十個分裂點。它可能準得多，"
     "但你沒辦法把它翻譯成一句話。</p>"
     "<p>第 2 章會把這個取捨畫成一張圖（彈性 vs 可解釋性），"
     "第 7 章的 GAM 則是刻意站在中間的折衷方案：允許每個變數各自彎曲，"
     "但保住「各變數的效果可以分開看」這件事。</p>"),
    ("Q：如果只做預測，是不是完全不用管模型長什麼樣？",
     "<p>理論上是，實務上不行，有三個現實理由。</p>"
     "<p><strong>除錯</strong>：模型上線後表現變差，看不懂它你就查不出原因。"
     "<strong>信任</strong>：醫療、信貸、司法這些領域，法規常常要求你能解釋每一個決策。"
     "<strong>資料洩漏</strong>：如果某個變數的重要度高得不合常理，"
     "很可能是它偷偷含有答案（例如用「是否已理賠」預測「是否出車禍」）——"
     "看得懂模型才抓得到這種錯。</p>"),
])}
"""

# ── P04 符號約定 ──────────────────────────────────────────────────────
BODIES["notation"] = f"""
  <p>後面每一章都會用到這套符號，先講清楚省得後面卡住。</p>

  <ul>
    <li><strong>n</strong>：觀測值（樣本）的個數，也就是資料表的<em>列</em>數。</li>
    <li><strong>p</strong>：預測變數（特徵）的個數，也就是資料表的<em>行</em>數（不含 y）。</li>
    <li>$x_{{ij}}$：第 i 個觀測值的第 j 個變數，i = 1…n，j = 1…p。</li>
    <li>$\\mathbf{{X}}$：n × p 的矩陣。$x_i$（下標一個數）是<strong>第 i 列</strong>，
    長度 p 的向量；$\\mathbf{{x}}_j$（粗體）是<strong>第 j 行</strong>，長度 n 的向量。</li>
    <li>$y_i$：第 i 個觀測值的目標值；$y$ 是長度 n 的向量。</li>
  </ul>

  $$\\mathbf{{X}} = \\begin{{pmatrix}}
    x_{{11}} & x_{{12}} & \\cdots & x_{{1p}} \\\\
    x_{{21}} & x_{{22}} & \\cdots & x_{{2p}} \\\\
    \\vdots & \\vdots & \\ddots & \\vdots \\\\
    x_{{n1}} & x_{{n2}} & \\cdots & x_{{np}}
  \\end{{pmatrix}}$$

{viz(svg("w01npSvg", 300),
     [info_card("怎麼看",
                '<span style="color:var(--accent3);font-weight:700;">綠色一整列</span>是'
                '一個觀測值 xᵢ（一個人、一天、一個州）；'
                '<span style="color:var(--accent);font-weight:700;">紅色一整行</span>是'
                '一個變數 xⱼ（年齡、薪資、犯罪率）。'
                '<strong>這兩件事很容易搞混，而它們的長度完全不同。</strong>'),
      rows_card("目前的形狀",
                [("n（觀測值）", "—", "w01npN"), ("p（變數）", "—", "w01npP"),
                 ("X 有幾個數字", "—", "w01npCells"),
                 ("xᵢ 的長度", "—", "w01npRow"), ("xⱼ 的長度", "—", "w01npCol")]),
      info_card("課程資料集的真實形狀",
                '<div id="w01npSets" class="mono" style="font-size:.72rem;line-height:1.9;">—</div>')],
     "w01npStatus", "固定用 n = 8、p = 4 標出列、行與單一元素。", "",
     provenance=("book-redraw", "依 ISLP 第 1 章的 n × p 記號重繪"))}

{info("p ≫ n 會出大事", '''NCI60 資料是 <strong>64 × 6830</strong>——變數比觀測值多一百倍。
  這種「高維度」設定下，最小平方係數通常不唯一；設計矩陣的列滿秩時，甚至能讓訓練 R² 等於 1。
  但訓練滿分不能證明預測能力。<a href="model_selection.html#highdim">線性模型選擇的高維度一節</a>
  會說明如何用收縮、降維與獨立評估處理這個問題。''', "warm")}

{quiz("qNota", "QUIZ · 符號",
      "$x_{{3}}$（下標一個數字 3）指的是什麼？",
      [(True, "第 3 個<strong>觀測值</strong>，是一個長度 p 的向量",
        "對。ISLP 的約定是：下標一個數字＝第幾列（一個觀測值），粗體加下標 $\\mathbf{x}_j$＝第幾行（一個變數）。兩者長度不同（p 對 n），弄反了整段推導都會錯。"),
       (False, "第 3 個<strong>變數</strong>，是一個長度 n 的向量",
        "那是 $\\mathbf{x}_3$（粗體）。ISLP 用粗細來區分列與行。這在讀第 3、6 章的矩陣式子時很關鍵。"),
       (False, "X 矩陣第 3 列第 3 行的那個數字",
        "單一個數字要兩個下標：$x_{33}$。只有一個下標時指的是整列。")])}
"""

# ── P05 資料集巡禮 ────────────────────────────────────────────────────
BODIES["datasets"] = f"""
  <p>ISLP 第 1 章用三份資料介紹三類問題。這三份會在後面的章節反覆出現，
  現在先認識它們。</p>

  <h3 id="dx-wage">Wage：迴歸問題</h3>
  <p>美國大西洋中部地區 3000 位男性的薪資與人口特徵。y 是 <code>wage</code>（連續數值），
  所以這是迴歸。ISLP 圖 1.1 畫了三件事：薪資對年齡是<strong>先升後降的曲線</strong>
  （不是直線）、對年份幾乎是<strong>緩慢的線性上升</strong>、對教育程度是
  <strong>單調但不等距</strong>的階梯。</p>

{viz(chart("w01wageAge", "", "。年齡與薪資不是直線關係。") + "\n"
     + chart("w01wageYear", "", "。年份的平均薪資呈緩慢上升。") + "\n"
     + chart("w01wageEdu", "", "。教育程度的薪資差距不等距。"),
     [info_card("三個面板",
                '三張圖依序呈現不同變數型態。<strong>年齡</strong>那張是本課第一個「線性不夠用」的證據，'
                '所以才有第 7 章。<strong>年份</strong>那張的斜率是每年 +1.35 美元，'
                '線性配得不錯。<strong>教育</strong>那張是質性變數（第 3 章）。', "圖 1.1"),
      rows_card("Wage 的事實",
                [("n × p", "3000 × 11", "w01wageShape"),
                 ("2004 年的平均薪資", "111.16", "w01wage2004"),
                 ("年份趨勢", "每年 +1.35", "w01wageTrend")]),
      info_card("為什麼薪資會在 60 歲後往下",
                '不是「變老就變窮」。這是<strong>橫斷面</strong>資料：'
                '60 歲那一群人跟 30 歲那一群人是<em>不同的人</em>。'
                '高薪的人可能提早退休而離開樣本，留下的就偏低。'
                '這種「相關不等於因果」的陷阱，推論時要特別小心。')],
     "w01wageStatus", "同時閱讀三個面板，不用按鈕切換才看得到證據。", "",
     provenance=("course-data", "ISLP Wage；對照講義圖 1.1 與 Ch01 lab"))}

{card("講義 01 · 載入 Wage 並看形狀", lab_code(CH, 146), lab_output(CH, 146), src=src("145、146"),
      note="11 個欄位裡 <code>wage</code> 是 y、<code>logwage</code> 是它的對數（別同時放進模型），"
           "其餘 9 個是候選預測變數。")}

{card("講義 01 · 2004 年的平均薪資", lab_code(CH, 148), lab_output(CH, 148), src=src("148"),
      note="這個 <strong>111.16</strong> 就是上面側欄卡裡的數字。"
           "圖表的烘焙資料跟 lab 是同一份資料、同一套演算法。")}

  <h3 id="dx-smarket">Smarket：分類問題</h3>
  <p>2001–2005 年 S&amp;P 500 的每日報酬。y 是 <code>Direction</code>（Up / Down），
  所以是分類。ISLP 圖 1.2 的重點很反直覺：<strong>前幾天的報酬（Lag1–Lag5）
  在漲日與跌日上的分佈幾乎一樣</strong>，也就是說，這件事非常難預測。</p>

{viz(svg("w01smSvg", 300),
     [info_card("怎麼看",
                '每一組是一個 Lag 變數，左右兩個箱子分別是「隔天跌」與「隔天漲」的日子。'
                '<strong>兩個箱子幾乎完全重疊。</strong>如果 Lag 真的能預測漲跌，'
                '兩個箱子應該明顯錯開。', "圖 1.2"),
      rows_card("Smarket 的事實",
                [("n × p", "1250 × 9", "w01smShape"),
                 ("漲的天數", "—", "w01smUp"),
                 ("Lag1｜跌日平均", "—", "w01smD"),
                 ("Lag1｜漲日平均", "—", "w01smU"),
                 ("兩者差距", "—", "w01smGap")]),
      info_card("這不是失敗的例子",
                '這是<strong>誠實的例子</strong>。第 4 章會真的在這份資料上跑邏輯斯迴歸與 LDA，'
                '正確率大約 50%——跟丟硬幣一樣。'
                '知道「有些東西就是預測不了」，跟知道怎麼預測一樣重要。')],
     "w01smStatus", "Lag1–Lag3 在漲日與跌日上的分佈。", "",
     provenance=("course-data", "ISLP Smarket；對照講義圖 1.2 與 Ch01 lab"))}

{card("講義 01 · Smarket 的欄位", lab_code(CH, 158), lab_output(CH, 158), src=src("157、158"),
      note="<code>Today</code> 是當天的報酬、<code>Direction</code> 是它的正負號，"
           "所以<strong>絕對不能</strong>把 <code>Today</code> 當預測變數（那就是答案本身）。"
           "這是最典型的資料洩漏。")}

  <h3 id="dx-nci">NCI60：非監督式問題</h3>
  <p>64 個癌症細胞株、每個測 6830 個基因的表現量。<strong>沒有 y</strong>。
  我們不是要預測什麼，而是想知道「這 64 個樣本會不會自己分成幾群」。
  ISLP 圖 1.4 把 6830 維壓到 2 維（第 12 章的主成分分析），
  結果同一種癌症的樣本確實傾向靠在一起。</p>

{viz(svg("w01nciSvg", 380),
     [info_card("怎麼看",
                '每個點是一個細胞株，位置由前兩個主成分決定，顏色是它的癌症型別。'
                '<strong>注意：分析時完全沒有用到型別資訊</strong>——'
                '顏色是事後塗上去驗證的。同色會聚在一起，說明基因表現量'
                '真的帶有型別的訊息。', "圖 1.4"),
      rows_card("NCI60 的事實",
                [("n × p", "64 × 6830", "w01nciShape"),
                 ("癌症型別數", "—", "w01nciTypes"),
                 ("PC1 解釋的變異", "—", "w01nciPve1"),
                 ("PC1 + PC2", "—", "w01nciPve2")]),
      info_card("p ≫ n 的極端例子",
                '6830 個變數、64 個樣本。傳統最小平方的唯一係數解與一般推論在這裡不再適用。'
                '降維與收縮提供額外結構，預測表現仍要用未見資料檢查。')],
     "w01nciStatus", "位置只由基因表現量決定；型別顏色是在分析後加上。", "",
     provenance=("course-data", "ISLP NCI60；對照講義圖 1.4 與 Ch01 lab"))}

{card("講義 01 · NCI60 的結構", lab_code(CH, 164), lab_output(CH, 164), src=src("164"),
      note="它回傳一個 dict：<code>data</code> 是 64 × 6830 的表現量矩陣、"
           "<code>labels</code> 是 64 個型別標籤。"
           "<strong>做非監督式分析時只用 data</strong>，labels 只拿來事後檢查。")}

{qa("觀念釐清", [
    ("Q：Smarket 的 Lag 幾乎沒有預測力，那為什麼課本還要用它？",
     "<p>因為它示範了一個真實而重要的事實：<strong>不是所有問題都能被預測</strong>。</p>"
     "<p>如果課本只用「配得很漂亮」的例子，你會學到一種危險的直覺——"
     "覺得只要方法夠好就一定能預測。金融市場的日報酬接近隨機漫步，"
     "這是被大量研究支持的結論，不是因為我們的模型不夠強。</p>"
     "<p>更重要的是：<strong>在這種資料上，任何回報「正確率 70%」的模型都應該被懷疑</strong>。"
     "那通常意味著資料洩漏（例如不小心把 <code>Today</code> 放進了預測變數）。</p>"),
    ("Q：NCI60 的顏色既然事後才塗，那分析到底「對」了嗎？",
     "<p>這正是非監督式學習最尷尬也最有趣的地方。</p>"
     "<p>這個例子裡我們<em>剛好</em>有標籤可以驗證，所以能說「PCA 抓到了真實的結構」。"
     "但在真正的非監督式應用裡你沒有標籤，所以你永遠無法確定看到的群是真的結構，"
     "還是只是雜訊排出來的花樣。</p>"
     "<p>實務上的做法是找<strong>外部證據</strong>：這些群在別的變數上有沒有差異？"
     "換一種方法、換一批資料還在不在？如果換個隨機種子群就變了，那大概不是真的。</p>"),
])}

{quiz("qData", "QUIZ · 三份資料",
      "同一份 Smarket 資料，如果把 <code>Today</code>（當天報酬）當成預測變數去猜 "
      "<code>Direction</code>（當天漲跌），正確率會是多少？",
      [(True, "100%，因為 Direction 就是 Today 的正負號。這是資料洩漏，不是預測",
        "對，而且這是實務上最常見的錯誤之一。任何近乎完美的正確率都該先懷疑洩漏，而不是慶祝。第 4 章跑這份資料時只用 Lag 與 Volume，正確率大約 50%。"),
       (False, "大約 50%，因為股市本來就難預測",
        "那是<strong>只用 Lag 當預測變數</strong>時的答案。<code>Today</code> 不一樣——<code>Direction</code> 是直接從它算出來的。"),
       (False, "大約 70%，因為當天報酬跟漲跌高度相關但不完全一致",
        "不是「高度相關」，是<strong>完全等價</strong>：Direction = Up 若且唯若 Today > 0。所以正確率是 100%。")])}
"""

# ── P06 統計學習與機器學習 ────────────────────────────────────────────
BODIES["slvsml"] = f"""
  <p>「統計學習」、「機器學習」、「資料科學」、「人工智慧」。這些詞常常混用，
  但它們的重心確實不同。講義第 19–22 頁討論了這件事。</p>

{table(["", "重心", "典型問法", "在意什麼"],
       [["統計學習", "從資料推論母體", "這個效果是真的嗎？多大？", "不確定性、可解釋性、模型假設"],
        ["機器學習", "在新資料上表現好", "預測誤差能壓到多低？", "泛化能力、算力、可擴展性"],
        ["資料科學", "從問題到決策的整條流程", "這個結論能支持什麼行動？", "資料品質、溝通、實際導入"],
        ["人工智慧", "讓機器展現智慧行為", "它能做這件事嗎？", "能力邊界"]])}

  <p>但這些界線在實務上非常模糊，而且愈來愈模糊。同一個隨機森林，
  統計學家與機器學習研究者都在用，只是<strong>他們問的問題不同</strong>：
  前者會問「變數重要度可不可信、能不能給信賴區間」，
  後者會問「加到 1000 棵樹還會不會更準」。</p>

{info("這門課站在哪裡", '''課名是「統計學習與資料探勘」，內容其實橫跨兩邊：
  第 3、4 章有完整的推論工具（標準誤、t 檢定、F 檢定），
  第 5 章之後的交叉驗證、正則化、集成則完全是機器學習的核心手法。<br><br>
  ISLP 作者自己的說法是：<strong>統計學習是機器學習的一個分支，
  重點放在「理解」而不只是「預測」</strong>。
  這也是為什麼本課每個方法都會問「它的假設是什麼、什麼時候會壞掉」，
  而不只是「怎麼調參數」。''')}

{quiz("qSlMl", "QUIZ · 統計學習與機器學習",
      "同一個隨機森林模型，統計學習與機器學習的取向差在哪？",
      [(True, "問的問題不同：前者更在意變數重要度可不可信、假設成不成立；後者更在意預測誤差能壓多低",
        "對。工具是共用的，差別在目的與評價標準。這也是為什麼本課每個方法都會問「假設是什麼、什麼時候會壞」。"),
       (False, "統計學習不會用隨機森林，那是機器學習的方法",
        "不對。隨機森林由 Breiman 提出，他是統計學家；本課第 8 章就在教它。方法沒有門派，取向才有。"),
       (False, "機器學習不需要考慮模型假設，統計學習才需要",
        "說得太絕。機器學習同樣受假設約束——例如交叉驗證假設資料獨立同分佈，時間序列違反這一點就會嚴重高估表現（第 5 章）。差別是強調的重點，不是有沒有假設。")])}
"""

# ── P07 Python 工具鏈 ─────────────────────────────────────────────────
BODIES["toolchain"] = f"""
  <p>本課的程式全部用 Python。你需要的套件不多，而且每一章的 lab 開頭都會列出來。</p>

{table(["套件", "做什麼", "在哪幾章會用到"],
       [["<code>numpy</code>", "陣列與線性代數", "全部"],
        ["<code>pandas</code>", "表格資料（DataFrame）", "全部"],
        ["<code>matplotlib</code> / <code>seaborn</code>", "畫圖", "全部"],
        ["<code>scikit-learn</code>", "配模型、交叉驗證、Pipeline", "第 2 章之後"],
        ["<code>statsmodels</code>", "推論用的迴歸摘要（標準誤、p 值）", "第 3、4 章"],
        ["<code>ISLP</code>", "課本的資料集與幾個輔助函式", "全部"],
        ["<code>pygam</code>", "廣義加性模型", "第 7 章"]])}

{card("講義 01 · lab 開頭的匯入", lab_code(CH, 88), None, src=src("88"),
      note="每一章的 lab 都是這個開頭。<code>ISLP</code> 的 <code>load_data()</code> "
           "會直接給你課本用的資料集，不必自己找檔案。")}

{info("環境怎麼準備", '''<strong>最省事：用 Google Colab。</strong>瀏覽器打開就能跑，
  不用裝任何東西，每章 lab 的第一格徽章可以一鍵開啟。<br><br>
  <strong>要在自己電腦上跑：</strong>裝 Anaconda 或 Miniconda，然後
  <code>pip install ISLP</code>（它會把 numpy、pandas、scikit-learn、statsmodels
  一起帶進來）。課程 repo 的 <code>packages.txt</code> 有完整的版本清單。<br><br>
  <strong>版本不同數字會不一樣</strong>。這不是你做錯了。本站每頁的
  「預期輸出」都標了來源儲存格，就是為了讓你能對照。''')}

{qa("觀念釐清", [
    ("Q：為什麼有兩套做迴歸的工具（scikit-learn 與 statsmodels）？",
     "<p>因為它們為不同目的設計，剛好對應這一頁 P03 講的預測與推論。</p>"
     "<p><code>statsmodels</code> 給你完整的<strong>推論</strong>報表："
     "係數、標準誤、t 值、p 值、信賴區間、F 檢定。第 3、4 章要的就是這些。</p>"
     "<p><code>scikit-learn</code> 給你統一的<strong>預測</strong>介面："
     "<code>fit</code> / <code>predict</code> / <code>score</code>，"
     "配上 <code>Pipeline</code> 與 <code>cross_validate</code>。"
     "它<em>刻意</em>不提供 p 值，因為在它的世界觀裡，"
     "模型好不好是用留出的資料驗證，不是用 p 值判斷。</p>"
     "<p>第 5 章的 lab 會示範怎麼用 <code>ISLP</code> 的 <code>sklearn_sm()</code> "
     "把 statsmodels 的模型包成 sklearn 介面，這樣就能拿去做交叉驗證。</p>"),
])}

{quiz("qTool", "QUIZ · 工具鏈",
      "你要報告「廣告支出對銷售額的影響有多大、可不可信」。該用哪個套件？",
      [(True, "<code>statsmodels</code>，因為你需要標準誤、信賴區間與 p 值",
        "對。這是推論問題，需要不確定性的量化。<code>statsmodels</code> 的 <code>summary()</code> 一次給你全部。"),
       (False, "<code>scikit-learn</code>，因為它是最主流的機器學習套件",
        "主流不等於適用。<code>scikit-learn</code> 刻意不提供 p 值與標準誤。它的設計目的是預測與交叉驗證，不是推論。"),
       (False, "兩個都不行，要自己用 <code>numpy</code> 算矩陣公式",
        "自己算當然做得到（第 3 章會推導那些公式），但沒必要——<code>statsmodels</code> 已經把整份推論報表算好了，而且不容易出錯。")])}
"""

# ── EX（ISLP 第 1 章沒有課後習題，改成概念自測）────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 分類問題的四個象限",
      "一家串流平台想「從觀看紀錄預測使用者下個月會不會退訂」。這在本課的地圖上是？",
      [(True, "監督式、分類、偏預測 → 第 4 章（分類）與第 8、9 章（彈性方法）",
        "對。有 y（退訂了沒有）＝監督式；y 是二元類別＝分類；平台最在意「抓得準不準」＝偏預測，所以彈性方法（隨機森林、GBDT）通常表現最好。若同時想知道「為什麼退訂」，那部分是推論，要另外用可解釋的模型。"),
       (False, "非監督式，因為要把使用者分成「會退訂」與「不會退訂」兩群",
        "「最後得到兩組」不等於非監督式。歷史資料裡<strong>已經知道</strong>誰退訂了，那就是 y，所以是監督式分類，不是分群。"),
       (False, "監督式、迴歸，因為要預測的是機率",
        "分類模型可以輸出機率。這裡訓練的 y 是「有沒有退訂」的二元事件，所以仍是分類任務；不能只憑輸出是連續機率就改判為迴歸。")])}

{quiz("qEx2", "EXERCISE 2 · 預測與推論",
      "衛生單位想知道「香菸稅每漲 10 元，青少年吸菸率會降多少」。這主要是？",
      [(True, "推論——要的是效果的大小與方向，還要能說這個估計有多不確定",
        "對，而且要能給信賴區間，因為這個數字會被拿去訂政策。這種問題要用可解釋的模型（線性迴歸、GAM），而且要非常小心因果推論的陷阱——相關不等於因果。"),
       (False, "預測——要預測未來的吸菸率",
        "如果只想知道「明年吸菸率大概幾 %」那是預測。但題目問的是<strong>稅率變動造成的影響有多大</strong>，那是在問模型內部的係數，屬於推論。"),
       (False, "兩者都不是，這是因果推論，跟統計學習無關",
        "因果推論確實是另一個領域（需要實驗設計或工具變數等額外假設），但它<strong>建立在</strong>統計推論之上。本課教的推論工具是必要基礎，只是不足以單獨支持因果宣稱。")])}

{quiz("qEx3", "EXERCISE 3 · n 與 p",
      "一份資料有 200 位病人、每人測 20000 個基因。n 與 p 各是多少，會有什麼麻煩？",
      [(True, "n = 200、p = 20000；p ≫ n，最小平方係數不唯一，訓練滿分也不能證明預測力",
        "對。當設計矩陣的列滿秩時可以插值訓練資料，但同樣的訓練預測可能來自許多不同係數，它們在新資料上的預測不一定相同。收縮與降維用額外結構約束估計，最後仍要獨立評估。"),
       (False, "n = 20000、p = 200；資料量很大所以沒問題",
        "n 與 p 弄反了。<strong>n 是觀測值個數（病人）、p 是變數個數（基因）</strong>。這裡病人只有 200 位。"),
       (False, "n = 200、p = 20000；資料量夠大，用隨機森林就沒問題",
        "n 與 p 對了，但「沒問題」錯了。大量無關變數也可能影響隨機森林的分裂選擇。是否適合這份資料，要用未參與特徵選擇與調參的資料評估，不能只憑方法名稱判斷。")])}

{quiz("qEx4", "EXERCISE 4 · 資料洩漏",
      "你用「病人是否住進加護病房」來預測「病人是否重症」，正確率 97%。最該做的事是？",
      [(True, "懷疑資料洩漏——住進加護病房幾乎就是「重症」的結果而不是原因",
        "對。近乎完美的正確率在真實問題上幾乎都是洩漏的訊號。這個變數是 y 發生<em>之後</em>才產生的，部署時根本拿不到。第 5 章的「CV 的對與錯」那一節講的是同一類病。"),
       (False, "很好，直接上線",
        "這是最危險的反應。97% 在訓練資料上成立，但部署時你沒有這個變數（或它出現得比預測時點更晚），模型會立刻失效。"),
       (False, "再多加一些變數把正確率推到 99%",
        "方向完全錯了。問題不是正確率不夠高，而是<strong>這個高正確率是假的</strong>。加更多變數只會讓假象更牢固。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>這一頁沒有公式要背，但這四個分類問題會決定你之後每次遇到新問題時該翻哪一章。</p>

  <h3>四個問題決定你翻哪一章</h3>
{table(["問題", "答案", "去哪裡"],
       [["有 y 嗎？", "有 → 監督式", "第 2–9 章"],
        ["", "沒有 → 非監督式", "第 12 章"],
        ["y 是什麼型態？", "數字 → 迴歸", "第 3、6、7 章"],
        ["", "類別 → 分類", "第 4、9 章"],
        ["要準還是要懂？", "要準 → 彈性方法", "第 8、9 章"],
        ["", "要懂 → 可解釋方法", "第 3、4、7 章"],
        ["怎麼知道做得好不好？", "重抽樣估測試誤差", "<strong>第 5 章（每一章都要用）</strong>"]])}

  <h3>符號速查</h3>
{table(["符號", "意思", "長度／形狀"],
       [["n", "觀測值個數（列數）", "純量"],
        ["p", "預測變數個數（行數）", "純量"],
        ["$\\mathbf{X}$", "預測變數矩陣", "n × p"],
        ["$x_i$", "第 i 個<strong>觀測值</strong>", "長度 p"],
        ["$\\mathbf{x}_j$", "第 j 個<strong>變數</strong>", "長度 n"],
        ["$x_{ij}$", "第 i 個觀測值的第 j 個變數", "純量"],
        ["$y$", "目標值向量", "長度 n"],
        ["$\\hat f$", "估計出來的函數", "—"],
        ["$\\hat y$", "預測值", "長度 n"]])}

  <h3>三份資料的形狀</h3>
{table(["資料集", "n", "p", "y", "問題類型", "後面在哪裡再出現"],
       [["Wage", "3000", "11", "<code>wage</code>（連續）", "迴歸", "第 7 章（樣條與 GAM）"],
        ["Smarket", "1250", "9", "<code>Direction</code>（二元）", "分類", "第 4 章（邏輯斯、LDA）"],
        ["NCI60", "64", "6830", "<strong>無</strong>", "非監督式", "第 12 章（PCA、分群）"],
        ["Auto", "392", "8", "<code>mpg</code>（連續）", "迴歸", "第 3、5 章"],
        ["Bikeshare", "8645", "15", "<code>bikers</code>（計數）", "迴歸／Poisson", "第 4 章"]])}

{info("三個一定要記住的觀念", '''<strong>1. 有沒有 y 是最大的分水嶺。</strong>
  沒有 y 就沒有客觀對錯，這件事會一路影響到第 12 章怎麼驗證分群結果。<br>
  <strong>2. 預測與推論要的模型不一樣。</strong>
  先問清楚自己要哪一個，再選方法。不要先選了隨機森林才發現老闆要的是 p 值。<br>
  <strong>3. 近乎完美的正確率幾乎都是資料洩漏。</strong>
  Smarket 的 <code>Today</code> 是課本給的示範，實務上這個坑更隱晦。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== introduction 本頁元件（id 與全域一律 w01 前綴）===== */

/* ---------- P04 n × p 矩陣 ---------- */
function w01npDraw() {
  const n = 8, p = 4;
  const W = 620, H = 300;
  const s = HC.svg('w01npSvg', { xd: [0, 1], yd: [0, 1], h: H, w: W,
                                 pad: { l: 8, r: 8, t: 8, b: 8 } });
  s.clear();
  const g = s.layer('grid');
  const cw = Math.min(46, (W - 190) / (p + 1)), chh = Math.min(24, (H - 80) / n);
  const x0 = 96, y0 = 44;
  const hiRow = Math.min(2, n - 1), hiCol = Math.min(1, p - 1);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < p; j++) {
      const isRow = i === hiRow, isCol = j === hiCol;
      s.add('rect', { x: x0 + j * cw, y: y0 + i * chh, width: cw - 2, height: chh - 2, rx: 3,
                      fill: isRow && isCol ? '#8e44ad'
                            : isRow ? 'var(--accent3)' : (isCol ? 'var(--accent)' : 'var(--card)'),
                      stroke: 'var(--card-border)', 'stroke-width': 1,
                      opacity: isRow || isCol ? 0.85 : 1 }, g);
    }
    // y 向量畫在右邊，跟 X 隔開
    s.add('rect', { x: x0 + p * cw + 14, y: y0 + i * chh, width: cw - 2, height: chh - 2, rx: 3,
                    fill: i === hiRow ? 'var(--accent3)' : 'var(--paper)',
                    stroke: 'var(--muted)', 'stroke-width': 1, opacity: 0.9 }, g);
  }
  const t = (px, py, txt, cls, anchor) => {
    const el = s.add('text', { x: px, y: py, class: cls || 'axlab',
                               'text-anchor': anchor || 'start' }, g);
    el.textContent = txt; return el;
  };
  t(8, 20, 'X 是 n × p 的矩陣，y 是長度 n 的向量', 'axtitle');
  t(x0 + p * cw / 2, y0 - 8, 'p = ' + p + ' 個變數', 'axtitle', 'middle');
  t(x0 + p * cw + 14 + cw / 2, y0 - 8, 'y', 'axtitle', 'middle');
  t(x0 - 10, y0 + hiRow * chh + chh / 2 + 3, 'xᵢ →', 'vlab', 'end');
  t(x0 + hiCol * cw + cw / 2, y0 + n * chh + 16, '↑ xⱼ', 'vlab', 'middle');
  t(8, y0 + n * chh / 2, 'n = ' + n, 'axtitle');
  $('w01npN').textContent = String(n);
  $('w01npP').textContent = String(p);
  $('w01npCells').textContent = (n * p).toLocaleString('en-US') + ' 個';
  $('w01npRow').textContent = p + '（一個觀測值有 p 個變數）';
  $('w01npCol').textContent = n + '（一個變數有 n 個觀測值）';
  if (typeof FRAMES_w01shapes !== 'undefined') {
    $('w01npSets').innerHTML = FRAMES_w01shapes.sets.map(d =>
      d.name + '：' + d.n.toLocaleString('en-US') + ' × ' + d.p.toLocaleString('en-US')
      + (d.p > d.n ? ' <span style="color:var(--accent);font-weight:700;">← p &gt; n</span>' : ''))
      .join('<br>');
  }
  setStatus('w01npStatus', 'n = ' + n + '、p = ' + p + ' → X 有 ' + (n * p)
    + ' 個數字。綠色那一列是 xᵢ（長度 ' + p + '），紅色那一行是 xⱼ（長度 ' + n
    + '）——注意它們長度不同，紫色那格是兩者的交集 xᵢⱼ。');
}

/* 三個 panel 同時出現，避免用切換按鈕把證據藏起來。 */
function w01wageDrawAll() {
  const F = FRAMES_w01wage;
  HC.scatter('w01wageAge', {
    datasets: [
      { label: '個別觀測值（固定抽 600 點）',
        data: F.scatter.map(d => ({ x: d[0], y: d[1] })),
        backgroundColor: 'rgba(138,133,120,.45)', pointRadius: 2.2, showLine: false },
      { label: '分箱平均', data: F.ageCurve.map(d => ({ x: d[0], y: d[1] })),
        borderColor: HC.tok.accent2, backgroundColor: HC.tok.accent2,
        borderWidth: 3, pointRadius: 3, showLine: true, type: 'line' },
    ],
  }, { scales: { x: { type: 'linear', title: { display: true, text: '年齡' } },
                  y: { title: { display: true, text: '薪資（千美元）' } } } });

  const ys = F.yearMean.map(d => d[0]);
  HC.line('w01wageYear', {
    labels: ys,
    datasets: [
      { label: '各年平均', data: F.yearMean.map(d => d[1]),
        borderColor: HC.tok.accent2, backgroundColor: HC.tok.accent2,
        borderWidth: 3, pointRadius: 4, fill: false },
      { label: '線性趨勢', data: ys.map(y => F.trend[0] + F.trend[1] * y),
        borderColor: HC.tok.accent, borderWidth: 2, borderDash: [6, 4],
        pointRadius: 0, fill: false },
    ],
  }, { scales: { x: { title: { display: true, text: '年份' } },
                  y: { title: { display: true, text: '平均薪資（千美元）' } } } });

  HC.bar('w01wageEdu', {
    labels: F.eduBox.map(d => d.label),
    datasets: [
      { label: '中位數', data: F.eduBox.map(d => d.med),
        backgroundColor: 'rgba(44,62,122,.75)', borderRadius: 5 },
      { label: '平均', data: F.eduBox.map(d => d.mean), type: 'line',
        borderColor: HC.tok.accent, backgroundColor: HC.tok.accent,
        borderWidth: 2.4, pointRadius: 4, fill: false },
    ],
  }, { scales: { x: { title: { display: true, text: '教育程度' } },
                  y: { title: { display: true, text: '薪資（千美元）' }, beginAtZero: true } } });

  $('w01wageShape').textContent = F.n + ' × 11';
  $('w01wage2004').textContent = HC.fmt(F.mean2004, 2);
  $('w01wageTrend').textContent = '每年 +' + HC.fmt(F.trend[1], 2);
  setStatus('w01wageStatus', '左：年齡效果會彎；中：年份趨勢近似線性；右：教育程度是有序類別，但級距不等。');
}

/* ---------- P05 Smarket 箱形圖 ---------- */
function w01smDraw() {
  const F = FRAMES_w01smarket;
  const svc = HC.svg('w01smSvg', { xd: [-0.6, F.lagBox.length - 0.4], yd: [-3.2, 3.2],
                                   h: 300, w: 620 });
  svc.clear();
  svc.grid(F.lagBox.length - 1, 4, { xtitle: '', ytitle: '前一日報酬（%）',
                                     xfmt: v => 'Lag' + (Math.round(v) + 1), ydec: 0 });
  const g = svc.layer('box');
  svc.seg(svc.xd[0], 0, svc.xd[1], 0, { cls: 'resid', stroke: HC.tok.muted, sw: 1 }, g);
  F.lagBox.forEach((row, i) => {
    [['Down', -0.16, 'var(--accent)'], ['Up', 0.16, 'var(--accent3)']].forEach(spec => {
      const b = row[spec[0]], cx = i + spec[1], hw = 0.11;
      svc.seg(cx, b.lo, cx, b.hi, { cls: 'resid', stroke: spec[2], sw: 1.4, dash: '3 3' }, g);
      svc.box(cx - hw, b.q1, cx + hw, b.q3,
              { fill: spec[2], stroke: spec[2], sw: 1.4, rx: 2 }, g);
      svc.seg(cx - hw, b.med, cx + hw, b.med, { cls: 'fit', stroke: '#fff', sw: 2.4 }, g);
      if (i === 0) svc.txt(cx, 3.0, spec[0] === 'Down' ? '隔天跌' : '隔天漲',
                           { fill: spec[2] }, g);
    });
  });
  $('w01smUp').textContent = F.nUp + ' / ' + F.n + '（' + HC.pct(F.nUp / F.n, 1) + '）';
  const d0 = F.lagBox[0].Down.mean, u0 = F.lagBox[0].Up.mean;
  $('w01smD').textContent = HC.fmt(d0, 4) + '%';
  $('w01smU').textContent = HC.fmt(u0, 4) + '%';
  $('w01smGap').textContent = HC.fmt(Math.abs(d0 - u0), 4) + ' 個百分點';
  setStatus('w01smStatus', 'Lag1 在跌日的平均是 ' + HC.fmt(d0, 4) + '%、在漲日是 '
    + HC.fmt(u0, 4) + '%——差 ' + HC.fmt(Math.abs(d0 - u0), 4)
    + ' 個百分點，而每日報酬的標準差超過 1%。'
    + '<strong>兩個箱子幾乎完全重疊，所以這件事非常難預測。</strong>');
}

/* ---------- P05 NCI60 主成分散佈圖 ---------- */
let w01NciColor = true;
function w01nciDraw(colored) {
  if (colored !== undefined) w01NciColor = colored;
  const F = FRAMES_w01nci;
  const xs = F.pts.map(p => p.x), ys = F.pts.map(p => p.y);
  const pad = 6;
  const svc = HC.svg('w01nciSvg', {
    xd: [Math.min.apply(null, xs) - pad, Math.max.apply(null, xs) + pad],
    yd: [Math.min.apply(null, ys) - pad, Math.max.apply(null, ys) + pad], h: 380, w: 620,
  });
  svc.clear();
  svc.grid(5, 4, { xtitle: 'PC1（解釋 ' + HC.pct(F.pve[0], 1) + ' 變異）',
                   ytitle: 'PC2（' + HC.pct(F.pve[1], 1) + '）', xdec: 0, ydec: 0 });
  const g = svc.layer('pts');
  const groups = [];
  F.pts.forEach(p => { if (groups.indexOf(p.g) < 0) groups.push(p.g); });
  const pal = ['#2c3e7a', '#c0392b', '#1a6b4a', '#8e44ad', '#f39c12', '#16a085',
               '#d35400', '#2980b9', '#c2185b', '#00838f', '#7f8c8d'];
  F.pts.forEach(p => svc.dot(p.x, p.y, {
    r: 5, stroke: '#fff', sw: 1.2,
    fill: w01NciColor ? pal[groups.indexOf(p.g) % pal.length] : 'rgba(90,90,90,.6)',
  }, g));
  if (w01NciColor) {
    groups.forEach((gr, i) => {
      const col = i % 3, row = Math.floor(i / 3);
      svc.add('circle', { cx: 60 + col * 190, cy: 22 + row * 16, r: 4.5,
                          fill: pal[i % pal.length] }, g);
      svc.txtPx(70 + col * 190, 26 + row * 16, gr, { fill: HC.tok.muted }, g);
    });
  }
  $('w01nciTypes').textContent = F.nTypes + ' 種';
  $('w01nciPve1').textContent = HC.pct(F.pve[0], 1);
  $('w01nciPve2').textContent = HC.pct(F.pve[0] + F.pve[1], 1);
  setStatus('w01nciStatus', w01NciColor
    ? '同一種癌症的樣本傾向靠在一起——但這個位置<strong>完全沒有用到型別資訊</strong>，'
      + '顏色是事後塗上去驗證的。前兩個主成分只解釋了 '
      + HC.pct(F.pve[0] + F.pve[1], 1) + ' 的變異，卻已經看得出結構。'
    : '這才是非監督式學習真正面對的畫面：<strong>沒有顏色</strong>。'
      + '你要自己決定這裡有幾群、哪些點算同一群——而且沒有答案可以對。');
}

/* ---------- 啟動 ----------
   SVG 元件與純 DOM 元件一律放在 HC.ready() 外面：Chart.js 從 CDN 載不到時
   HC.ready() 不會執行，放進去會讓它們跟著死掉。 */
w01npDraw();
w01smDraw();
w01nciDraw(true);
HC.ready(() => {
  w01wageDrawAll();
});
"""


if __name__ == "__main__":
    apply("introduction", BODIES, PAGEJS, frames())
