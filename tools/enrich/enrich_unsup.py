#!/usr/bin/env python3
"""unsupervised_learning.html（站內序號 07 / ISLP 第 12 章）完整自學充實。冪等。

站內序號是 07（id 前綴 w07），ISLP 章號是 12（data/*/ch12.json、lab_ch12.md、deck_12.tsv）。
兩個編號不同是刻意的。

內容依據：講義 12_Unsupervised_learning.pdf（106 頁）、Ch12-unsup-lab-zh.ipynb、
ISLP 第 12 章（書上 p.504–556）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_unsup.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 12
LAB = "Ch12-unsup-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_unsup.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_unsup.py 失敗：\n" + r.stderr[-2000:])
    return "/* ===== 烘焙資料（tools/frames/gen_unsup.py，固定種子）===== */\n" + r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>前面十幾週，每一章都有一個 <span class="orange">y</span>。有了 y，一切都好辦：
  切出測試集、算 MSE 或錯誤率、用交叉驗證挑超參數——<strong>「哪個模型比較好」有客觀答案</strong>。</p>

  <p>這一章把 y 拿掉。手上只剩 X₁, X₂, …, X<sub>p</sub>，問題變成：
  <strong>這批資料本身有什麼結構？</strong>能不能用兩個座標軸就把 6830 個基因的樣本畫在紙上？
  這 64 個細胞株是不是可以分成幾個自然的群？</p>

  <p>麻煩的地方是：<strong>沒有 y，就沒有對錯。</strong>你沒辦法交叉驗證一個分群結果，
  因為沒有「正確的群」可以比。所以非監督式學習比監督式主觀得多，
  它的定位通常是<strong>探索式資料分析</strong>（exploratory data analysis）——
  產出的是值得進一步檢驗的假設，不是結論。</p>

{info("本章的三條主線", '''<strong>1. 主成分分析（PCA）：</strong>找幾個「變異最大」的方向，
  把 p 維壓成 2 維畫出來。它同時也是「最佳低維近似」。<br>
  <strong>2. 矩陣補全（matrix completion）：</strong>把 PCA 的想法套到有缺失值的矩陣上，
  順手就變成推薦系統。<br>
  <strong>3. 分群（clustering）：</strong>K-means 與階層式分群，兩種找子群的方式。''')}

  <p>PCA 與分群都在「化簡資料」，但化簡的方式不同，這個分工先記住：</p>

{table(["", "產出什麼", "問的問題", "要先決定什麼", "本頁的節"],
       [["PCA", "連續的低維座標（每筆資料一組新座標）", "哪幾個方向的變異最大？",
         "留幾個主成分 M", "P01–P06"],
        ["分群", "離散的群標籤（每筆資料一個編號）", "哪些觀測值彼此相似？",
         "K，或樹要切在哪", "P07–P09"]])}

{info("沒有 y 不代表可以隨便說", '''非監督式學習最大的風險不是算錯，而是<strong>過度解讀</strong>。
  任何時候把資料丟去分群，它<em>一定</em>會給你群——問題是那些群是真的子群，
  還是只是把雜訊切開而已。ISLP §12.4.3 的建議是：換不同設定多跑幾次，
  看哪些結構每次都出現；報告時說清楚這是探索結果，不是定論。''', "warm")}

{quiz("qWhy", "QUIZ · 為什麼非監督式比較難",
      "為什麼非監督式學習「無法用交叉驗證來驗證結果」？",
      [(True, "交叉驗證需要在留出的資料上比對預測與真實答案，而非監督式問題根本沒有真實答案可比",
        "對。CV 的機制是「拿沒看過的資料算誤差」，這需要 y。沒有 y 就沒有誤差可以算，"
        "所以評估只能靠可解釋性、穩定性與外部驗證。"),
       (False, "因為非監督式方法沒有參數可以調，所以不需要交叉驗證",
        "不對，而且剛好相反——非監督式方法要調的東西不少（M、K、linkage、距離、要不要標準化），"
        "正是因為<strong>沒有客觀標準</strong>可以調它們，這些選擇才特別麻煩。"),
       (False, "因為非監督式方法的計算量太大，跑 k 折會太慢",
        "不對。PCA 是一次特徵分解、K-means 是幾十次迭代，都不慢。"
        "問題出在「沒有正確答案」這個本質，不是算力。")])}
"""

# ── P01 主成分是什麼 ───────────────────────────────────────────────────
_pca_code = (lab_code(CH, 19) + "\n\n" + lab_code(CH, 21) + "\n"
             + lab_code(CH, 27) + "\n" + lab_code(CH, 29))

BODIES["pca"] = f"""
  <p>先想一個很現實的問題：p = 10 個變數，兩兩畫散佈圖有 45 張，你看不完；
  而且每一張都只含一小部分資訊。有沒有辦法用<strong>兩張圖就把大部分結構看完</strong>？</p>

  <p>PCA 的答案是：不要看原始的座標軸，去找<strong>資料變異最大的那個方向</strong>。
  第一主成分是所有標準化線性組合裡樣本變異數最大的那一個：</p>

  $$Z_1 = \\phi_{{11}} X_1 + \\phi_{{21}} X_2 + \\cdots + \\phi_{{p1}} X_p,
    \\qquad \\text{{s.t.}} \\sum_{{j=1}}^{{p}} \\phi_{{j1}}^2 = 1$$

  <p>那些係數 $\\phi_{{j1}}$ 叫做<strong>負荷量</strong>（loading），合起來是負荷向量 $\\phi_1$。
  為什麼要限制平方和等於 1？因為不限制的話，把係數全部乘 100 變異數就變 10000 倍，
  「最大」就沒有意義了。把資料先置中（每欄減掉平均）之後，要解的是</p>

  $$\\max_{{\\phi_{{11}},\\dots,\\phi_{{p1}}}}
    \\left\\{{ \\frac{{1}}{{n}}\\sum_{{i=1}}^{{n}}
    \\Big(\\sum_{{j=1}}^{{p}} \\phi_{{j1}} x_{{ij}}\\Big)^2 \\right\\}}
    \\quad \\text{{s.t.}} \\quad \\sum_{{j=1}}^{{p}} \\phi_{{j1}}^2 = 1$$

  <p>括號裡的東西就是第 i 筆資料投影到 $\\phi_1$ 上的值，叫做<strong>得分</strong>（score）
  $z_{{i1}}$。因為資料置中過，得分的平均是 0，所以上式就是得分的樣本變異數。
  <strong>負荷向量是新座標軸的方向，得分是每筆資料在新座標軸上的位置</strong>——這兩個詞不要混。</p>

  <p>下面這個元件就是把上面那個最佳化問題「用手轉一遍」：拖動角度，看投影後的變異數怎麼變。</p>

{viz(svg("w07spinSvg", 360),
     [rows_card("目前這個方向",
                [("角度", "—", "w07spinAng"), ("投影後的變異數", "—", "w07spinVar"),
                 ("佔總變異的比例", "—", "w07spinPve"),
                 ("最大變異（第一主成分）", "—", "w07spinMax"),
                 ("PC1 的方向", "—", "w07spinDir")]),
      info_card("怎麼玩",
                '拖那顆<strong>橘色的把手</strong>（或用滑桿）轉動灰色的投影軸。'
                '每個點會沿虛線垂直落到軸上，變成一個一維的數字。'
                '<strong>那些落點的變異數就是右上角那個數。</strong>'
                '轉到變異數最大的地方，元件會自動吸附並告訴你——那就是第一主成分。'),
      info_card("為什麼不是「距離最近」？",
                '其實兩者是同一件事。把點投影到軸上，'
                '「投影後散得最開」與「原始點到軸的垂直距離平方和最小」'
                '加起來是定值（畢氏定理），所以最大化前者等於最小化後者。'
                '這就是 P03 那一節要講的另一種解釋。', "P03")],
     "w07spinStatus", "拖動橘色把手轉動投影方向，看投影後的變異數怎麼變。",
     '<label class="slider-label" style="margin-right:.3rem;">角度</label>'
     '<input type="range" id="w07spinSlider" min="0" max="180" step="1" value="8" '
     'oninput="w07spinFromSlider()" style="width:150px;accent-color:var(--accent3);">'
     '<span class="mono" id="w07spinSliderVal" style="min-width:44px;'
     'font-family:\'JetBrains Mono\',monospace;font-size:.82rem;color:var(--accent);">8°</span>'
     '<button class="btn btn-play" onclick="w07spinSnap()">▶ 跳到變異最大處</button>'
     '<button class="btn btn-reset" onclick="w07spinReset()">重置</button>')}

  <p>找完第一主成分之後，第二主成分是<strong>所有跟 $Z_1$ 不相關的線性組合裡變異最大的那一個</strong>。
  「與 $Z_1$ 不相關」這個條件等價於「方向 $\\phi_2$ 與 $\\phi_1$ 垂直」，
  所以主成分就是一組互相垂直的新座標軸，總共最多有 $\\min(n-1,\\,p)$ 個。</p>

  <h3 id="dx-pca">講義完整實作：標準化 → <code>PCA()</code> → 取出負荷量</h3>
{card("講義 12 · USArrests 的 PCA", _pca_code, lab_output(CH, 29), src=src("19、21、27、29"),
      out_tag="預期輸出（儲存格 29）",
      note="<code>components_</code> 的<strong>每一列</strong>是一個負荷向量。第一列 "
           "<code>[0.536, 0.583, 0.278, 0.543]</code> 在 Murder／Assault／Rape 上幾乎一樣重、"
           "UrbanPop 明顯較輕——所以 PC1 大致就是「整體暴力犯罪率」。"
           "第二列幾乎全押在 UrbanPop（0.873），那是「都市化程度」。"
           "注意 <code>PCA()</code> 預設只置中、不縮放，所以標準化要自己先做（第 19 格）。")}

{quiz("qPc", "QUIZ · 負荷量與得分",
      "USArrests 的 <code>pcaUS.components_</code> 是 4×4、<code>scores</code> 是 50×4。哪個描述正確？",
      [(True, "components_ 的每一列是一個負荷向量（長度 p = 4），scores 的每一行是一個州的四個得分",
        "對。負荷向量的長度是變數個數 p，得分向量的長度是樣本數 n。"
        "所以 <code>components_</code> 是 4×4（4 個主成分 × 4 個變數），<code>scores</code> 是 50×4。"),
       (False, "components_ 的每一列是一個州在四個主成分上的座標",
        "不對，那是 <code>scores</code> 的一行。<code>components_</code> 跟「州」完全無關——"
        "它只描述新座標軸的方向，換一批州、同樣四個變數，形狀還是 4×4。"),
       (False, "兩者都是 50×4，因為 PCA 對每一筆資料各算一組負荷量",
        "不對。負荷量是<strong>整批資料共用</strong>的一組係數（座標軸只有一組），"
        "不是每筆資料一組。每筆資料各自不同的是得分。")])}
"""

# ── P02 Biplot ────────────────────────────────────────────────────────
BODIES["biplot"] = f"""
  <p>算完 PCA 之後，最常畫的圖是 <strong>biplot</strong>（雙標圖）：
  同一張圖上<strong>同時</strong>放得分（點）與負荷量（箭頭）。
  ISLP 圖 12.1 就是 USArrests 的 biplot——50 個州當點，4 個變數當箭頭。</p>

  <p>讀法有三條，記住就夠用：</p>

  <ul>
    <li><strong>箭頭之間的夾角 → 變數的相關。</strong>Murder、Assault、Rape 三支箭頭幾乎重疊，
    表示它們高度相關（謀殺率高的州，傷害與強制性交的通報率也高）。UrbanPop 指向別的方向，
    跟那三個關係弱。</li>
    <li><strong>點在箭頭方向上的位置 → 那筆資料在該變數上的高低。</strong>
    加州在 Rape 與 UrbanPop 方向都很遠，所以兩者都高。北達科他在犯罪方向的另一端，犯罪率低。</li>
    <li><strong>點與點的距離 → 兩筆資料在前兩個主成分上的相似度。</strong>
    印第安納接近原點，代表犯罪與都市化都接近平均。</li>
  </ul>

  <p>下面這個 biplot 用的是課本的資料。真正要玩的是那個 toggle：
  <strong>按下「未標準化」，整張圖會變形。</strong></p>

{viz(svg("w07biSvg", 400),
     [rows_card("負荷量（箭頭的座標）",
                [("Murder", "—", "w07biL0"), ("Assault", "—", "w07biL1"),
                 ("UrbanPop", "—", "w07biL2"), ("Rape", "—", "w07biL3"),
                 ("PC1 的 PVE", "—", "w07biPve")]),
      info_card("四個變數的變異數",
                '<div class="ic-row"><span class="ic-label">Murder</span>'
                '<span class="ic-value">18.97</span></div>'
                '<div class="ic-row"><span class="ic-label">Assault</span>'
                '<span class="ic-value highlight">6945.17</span></div>'
                '<div class="ic-row"><span class="ic-label">UrbanPop</span>'
                '<span class="ic-value">209.52</span></div>'
                '<div class="ic-row"><span class="ic-label">Rape</span>'
                '<span class="ic-value">87.73</span></div>'
                '<p style="font-size:.78rem;margin-top:.4rem;">Assault 是「每十萬人的件數」，'
                '數字本來就大得多。<strong>不標準化的話 PC1 幾乎等於 Assault 自己。</strong></p>',
                "儲存格 17"),
      info_card("為什麼有些州沒有標字",
                '50 個州全部標字會擠成一團。這裡只標課本正文點名的八個：'
                'CA／NV／FL（犯罪率高）、ND／MS（低）、HI（都市化高但犯罪低）、'
                'IN（兩者都接近平均）、AK。滑到點上看不到名字是刻意的——'
                '<strong>biplot 要看的是整體結構，不是逐一查表。</strong>', "圖 12.1")],
     "w07biStatus", "這是標準化後的 biplot，對應 ISLP 圖 12.1 與圖 12.4 左。",
     '<button class="btn btn-toggle" onclick="w07biToggle()">切換 標準化 / 未標準化</button>'
     '<button class="btn btn-reset" onclick="w07biSetScaled(true)">回到標準化</button>')}

  <h3 id="dx-bi">講義完整實作：手工畫 biplot</h3>
{card("講義 12 · biplot（scatter + arrow + text）", lab_code(CH, 33), None, src=src("31、33"),
      note="<code>scikit-learn</code> 沒有內建 biplot，所以 lab 用 "
           "<code>ax.scatter</code> 畫得分、<code>ax.arrow</code> 畫負荷量，"
           "再用 <code>s_ = 2</code> 把箭頭放長一點（否則負荷量都在 ±1 以內，跟得分的尺度差太多，"
           "會縮成一小坨）。<strong>箭頭長度只是為了看得清楚，可以自己乘上任何常數。</strong><br>"
           "第 2 行與第 3 行把第二個主成分的得分與負荷量同時乘上 −1。"
           "同時翻兩邊，圖只是上下鏡射，任何結論都不變——這正是 P05 要講的符號不唯一。"
           "本頁的 biplot 直接用儲存格 29 那組負荷量，跟課本表 12.1 的數字逐位相同。")}

{quiz("qBi", "QUIZ · 讀 biplot",
      "在 USArrests 的 biplot 上，Murder 與 UrbanPop 兩支箭頭夾角接近 90°。這代表什麼？",
      [(True, "這兩個變數在前兩個主成分所描述的範圍內幾乎不相關",
        "對。箭頭夾角約 90° ⇒ 相關係數接近 0。要注意「在前兩個主成分描述的範圍內」這個限定："
        "biplot 只呈現前兩個主成分，被丟掉的部分不在圖上。"),
       (False, "這兩個變數的變異數差不多大",
        "不對，那要看箭頭<strong>長度</strong>（在標準化後的 biplot 上長度反映該變數被前兩個主成分"
        "解釋了多少），而且四個變數都已經被標準化成變異數 1 了。夾角講的是相關，不是大小。"),
       (False, "這兩個變數合起來就能解釋所有變異，其他變數是多餘的",
        "不對。箭頭互相垂直只說它們彼此獨立，完全沒有「解釋了全部變異」的意思——"
        "USArrests 的前兩個主成分合起來解釋 86.8%，還有 13% 在圖外。")])}
"""

# ── P03 另一種解釋 ─────────────────────────────────────────────────────
BODIES["lowrank"] = f"""
  <p>到目前為止主成分的定義是「變異最大的方向」。現在換一個完全不同的角度看它，
  結論會一模一樣——這件事很值得多花五分鐘。</p>

  <p>第一主成分的負荷向量所定義的那條直線，是 p 維空間中<strong>離所有資料點平均平方距離最近</strong>
  的那條線。前兩個主成分張出的平面，是離所有資料點最近的那個平面（ISLP 圖 12.2 左）。
  前 M 個主成分張出的是最近的 M 維超平面。</p>

  <p>把「最近」寫成最佳化問題就清楚了。置中後的資料矩陣 $\\mathbf{{X}}$，
  在所有 $x_{{ij}} \\approx \\sum_{{m=1}}^{{M}} a_{{im}} b_{{jm}}$ 這種形式的近似裡，
  找殘差平方和最小的那一組：</p>

  $$\\min_{{A \\in \\mathbb{{R}}^{{n\\times M}},\\, B \\in \\mathbb{{R}}^{{p\\times M}}}}
    \\left\\{{ \\sum_{{j=1}}^{{p}} \\sum_{{i=1}}^{{n}}
    \\Big( x_{{ij}} - \\sum_{{m=1}}^{{M}} a_{{im}} b_{{jm}} \\Big)^2 \\right\\}}$$

  <p>解出來的 $\\hat a_{{im}}$ 就是得分 $z_{{im}}$、$\\hat b_{{jm}}$ 就是負荷量 $\\phi_{{jm}}$。
  也就是說：<strong>「變異最大」與「近似誤差最小」是同一個問題的兩種寫法。</strong>
  ISLP 式 12.11 把這件事寫得很漂亮：</p>

  $$\\underbrace{{\\sum_{{j=1}}^{{p}} \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} x_{{ij}}^2}}_{{\\text{{資料的總變異}}}}
    = \\underbrace{{\\sum_{{m=1}}^{{M}} \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} z_{{im}}^2}}_{{\\text{{前 }} M \\text{{ 個主成分的變異}}}}
    + \\underbrace{{\\frac{{1}}{{n}} \\sum_{{j=1}}^{{p}} \\sum_{{i=1}}^{{n}}
      \\Big( x_{{ij}} - \\sum_{{m=1}}^{{M}} z_{{im}}\\phi_{{jm}} \\Big)^2}}_{{M \\text{{ 維近似的 MSE}}}}$$

  <p>左邊是固定的，所以中間變大就等於右邊變小。這也是為什麼下一節的 PVE
  可以直接讀成「近似的 $R^2$」。</p>

{info("實務上怎麼算：SVD", '''求主成分不必真的做特徵分解。把置中後的資料矩陣做
  <strong>奇異值分解</strong>（singular value decomposition, SVD）
  $\\mathbf{X} = \\mathbf{U}\\mathbf{D}\\mathbf{V}^{\\mathsf T}$，
  $\\mathbf{V}$ 的每一列就是負荷向量、$\\mathbf{U}\\mathbf{D}$ 就是得分矩陣。
  <code>numpy.linalg.svd</code> 比自己算 $\\mathbf{X}^{\\mathsf T}\\mathbf{X}$ 的特徵向量穩定得多，
  而且下一節的矩陣補全就是靠它一步步逼近的。''')}

  <h3 id="dx-svd">講義完整實作：SVD 與 <code>components_</code> 的關係</h3>
{card("講義 12 · np.linalg.svd 取出負荷矩陣",
      lab_code(CH, 48) + "\n\n" + lab_code(CH, 50), lab_output(CH, 50), src=src("48、50、51"),
      out_tag="預期輸出（儲存格 50）",
      note="<code>V</code> 的每一列就是負荷向量，只差符號。跟上一節儲存格 29 的 "
           "<code>components_</code> 比：第 1、3、4 列整列變號，第 2 列一模一樣。<br>"
           "lab 儲存格 51 又印了一次 <code>components_</code>，但<strong>那時第 33 格已經把 "
           "PC2 翻號了</strong>，所以第 2 列跟儲存格 29 不同——不是印錯，是同一個物件被就地改過。"
           "儲存格 53 與 54 也是同一件事：<code>U * D</code> 跟 <code>scores</code> 差整組符號。")}

{qa("觀念釐清", [
    ("Q：既然「變異最大」與「近似最好」是同一件事，為什麼課本要講兩次？",
     "<p>因為它們通往不同的用途。</p>"
     "<p>「變異最大」的說法讓你<strong>解讀</strong>主成分：負荷量告訴你這個方向由哪些變數組成，"
     "PC1 是「整體犯罪率」、PC2 是「都市化」這種話就是從這裡讀出來的。</p>"
     "<p>「近似最好」的說法讓你<strong>把 PCA 當工具用</strong>。既然前 M 個主成分是最佳的秩 M 近似，"
     "那它就可以拿來壓縮（存 M 個得分而不是 p 個原值）、去雜訊"
     "（NCI60 那種資料常先取前幾個主成分再分群）、以及最直接的——"
     "<strong>填補缺失值</strong>。下一節 P06 的矩陣補全整個建立在這個解釋上，"
     "從「變異最大」那邊完全看不出來要怎麼做。</p>"),
])}

{quiz("qLow", "QUIZ · 最佳低維近似",
      "式 12.11 說「總變異 = 前 M 個主成分的變異 + M 維近似的 MSE」。由此可以推出什麼？",
      [(True, "把前 M 個主成分的變異最大化，等於把 M 維近似的誤差最小化",
        "對。左邊那項只跟資料有關、是固定的，所以右邊兩項是零和的。"
        "這就是「變異最大」與「近似最近」兩種說法等價的代數證明。"),
       (False, "M 愈大，前 M 個主成分的變異愈大，所以近似誤差也愈大",
        "方向剛好反了。M 愈大，第二項愈大 ⇒ 第三項（誤差）愈<strong>小</strong>。"
        "M = min(n−1, p) 時誤差為 0，近似變成完全相等。"),
       (False, "只有在資料標準化過的情況下這個等式才成立",
        "不對。這個等式只需要每一欄<strong>置中</strong>（平均為 0），不需要縮放。"
        "標準化影響的是主成分本身長什麼樣（P05 會講），不影響這個分解成不成立。")])}
"""

# ── P04 PVE ───────────────────────────────────────────────────────────
_pve_code = lab_code(CH, 35) + "\n\n" + lab_code(CH, 37) + "\n\n" + lab_code(CH, 39)

BODIES["pve"] = f"""
  <p>壓到 2 維畫出來很方便，但<strong>丟掉了多少東西？</strong>這個問題的答案叫做
  <strong>解釋變異比例</strong>（proportion of variance explained, PVE）。</p>

  <p>置中後資料的總變異是 $\\sum_{{j=1}}^{{p}} \\frac{{1}}{{n}}\\sum_{{i=1}}^{{n}} x_{{ij}}^2$，
  第 m 個主成分的變異是 $\\frac{{1}}{{n}}\\sum_{{i=1}}^{{n}} z_{{im}}^2$，所以</p>

  $$\\mathrm{{PVE}}_m
    = \\frac{{\\sum_{{i=1}}^{{n}} z_{{im}}^2}}{{\\sum_{{j=1}}^{{p}}\\sum_{{i=1}}^{{n}} x_{{ij}}^2}}
    = 1 - \\frac{{\\mathrm{{RSS}}_M}}{{\\mathrm{{TSS}}}}\\Big|_{{M=m}} - \\text{{（前 }} m-1 \\text{{ 個的部分）}}$$

  <p>所有 $\\min(n-1,p)$ 個 PVE 加起來剛好是 1。累積 PVE 就是「前 M 個主成分留住了幾成」，
  由上一節的式 12.11，它同時也是「用前 M 個主成分近似資料矩陣」的 $R^2$。</p>

{viz(chart("w07screeChart", "tall",
           "。此圖的重點：USArrests 的四個 PVE 是 62.0% / 24.7% / 8.9% / 4.3%，"
           "第二個之後就掉下來了，所以留兩個主成分（累積 86.8%）是合理的選擇。"),
     [rows_card("滑桿選的 M",
                [("M", "2", "w07screeM"), ("累積 PVE（留住的變異）", "—", "w07screeKeep"),
                 ("丟掉的變異", "—", "w07screeLost"),
                 ("M 維近似的 RSS / TSS", "—", "w07screeRss"),
                 ("要存幾個數字", "—", "w07screeCost")]),
      info_card("怎麼看這張圖",
                '<span style="color:var(--accent2);font-weight:700;">實線</span>是每個主成分自己的 '
                'PVE（這就是 <strong>scree plot</strong>），'
                '<span style="color:var(--accent3);font-weight:700;">虛線</span>是累積 PVE。'
                '虛線碰到 1.0 表示所有主成分都用上了、近似變成完全相等。', "圖 12.3"),
      info_card("肘點在哪裡？",
                '從 62% 掉到 24.7% 是一個大落差，從 24.7% 掉到 8.9% 又是一個。'
                '課本的說法是「第二個主成分之後有一個<strong>肘點</strong>（elbow）」——'
                '第三個只解釋不到 10%、第四個不到一半的一半。<br>'
                '但要老實說：<strong>這是目測，沒有客觀標準。</strong>'
                'NCI60 那種資料前七個主成分合起來也只有 40%，照樣只能目測。')],
     "w07screeStatus", "拖滑桿改變 M，看留住多少變異、丟掉多少。",
     '<label class="slider-label" style="margin-right:.3rem;">M =</label>'
     '<input type="range" id="w07screeSlider" min="1" max="4" step="1" value="2" '
     'oninput="w07screeSet()" style="width:130px;accent-color:var(--accent3);">'
     '<span id="w07screeVal" style="min-width:22px;font-family:\'JetBrains Mono\',monospace;'
     'font-size:.82rem;color:var(--accent);font-weight:600;">2</span>'
     '<button class="btn btn-toggle" onclick="w07screeToggleCum()">切換 只看 PVE / 加上累積</button>')}

  <h3 id="dx-pve">講義完整實作：<code>explained_variance_ratio_</code></h3>
{card("講義 12 · 得分的標準差、變異數與 PVE", _pve_code, lab_output(CH, 39),
      src=src("35、37、39"), out_tag="預期輸出（儲存格 39）",
      note="三格印的是同一件事的三種寫法："
           "<code>scores.std(0, ddof=1)</code> 是得分的標準差、"
           "<code>explained_variance_</code> 是它的平方、"
           "<code>explained_variance_ratio_</code> 是再除以總和。"
           "第一個 <strong>0.62006</strong> 就是課本說的「第一主成分解釋了 62.0% 的變異」。"
           "lab 儲存格 41／43 用 <code>cumsum()</code> 畫出累積版，就是課本圖 12.3 右。")}

{quiz("qPve", "QUIZ · PVE 與 scree plot",
      "USArrests 的四個 PVE 是 0.620、0.247、0.089、0.043。如果我只留前兩個主成分，"
      "那 50×4 的資料矩陣被近似得多好？",
      [(True, "近似的 R² 是 0.868，也就是殘差平方和只剩總平方和的 13.2%",
        "對。累積 PVE = 0.620 + 0.247 = 0.868，而由式 12.11，累積 PVE 就是 1 − RSS/TSS。"
        "所以「解釋了 86.8% 的變異」與「近似的 R² 是 0.868」是同一句話。"),
       (False, "無法判斷，PVE 只說變異被解釋多少，跟近似的好壞沒有關係",
        "這是最常見的誤解。式 12.11 把總變異拆成「前 M 個主成分的變異」加「M 維近似的 MSE」，"
        "兩者是零和的——PVE 高就等於近似誤差小，兩件事綁在一起。"),
       (False, "近似誤差是 0.089 + 0.043 = 0.132 個單位的 MSE",
        "數字對、單位錯。0.132 是<strong>比例</strong>（佔總平方和的 13.2%），不是 MSE 的絕對值。"
        "要換成絕對值得再乘上 TSS。")])}
"""

# ── P05 尺度化與符號 ───────────────────────────────────────────────────
BODIES["scaling"] = f"""
  <p>這一節只有兩件事，但兩件都會在實務上咬人：<strong>做 PCA 之前要不要標準化</strong>，
  以及<strong>算出來的符號可以信到什麼程度</strong>。</p>

  <h3>一、尺度：不標準化就等於在比單位</h3>

  <p>PCA 找的是「變異最大」的方向。問題是變異數<strong>跟單位有關</strong>：
  USArrests 的 Assault 是「每十萬人的件數」，變異數 6945；Murder 也是每十萬人，但只有 18.97。
  不標準化的話，第一主成分幾乎整支押在 Assault 上（負荷量 0.995），
  其他三個變數等於沒參與。回到 P02 那個
  <a href="#biplot">biplot 元件</a>把 toggle 切到「未標準化」就看得到。</p>

  <p>更糟的是這個結果<strong>是任意的</strong>。如果 Assault 改成「每一百人的件數」，
  數值全部除以 1000，變異數變成原來的百萬分之一，它就從主宰者變成陪襯。
  <strong>沒有人希望分析結論取決於別人當年怎麼選單位</strong>，所以慣例是先標準化。</p>

{info("什麼時候不該標準化", '''變數<strong>本來就同單位、而且尺度差異本身有意義</strong>的時候。
  最典型的是基因表現量：p 個基因都用同一種方法測、同一個單位，
  某些基因的變異大就是生物上的事實，把它縮成 1 反而是把訊息丟掉。
  lab 對 NCI60 還是做了 <code>StandardScaler()</code>，但也在旁邊註明
  「這裡其實可以合理主張不要縮放」——這是判斷題，不是規則題。''', "warm")}

{table(["情況", "要不要標準化", "為什麼"],
       [["變數單位不同（USArrests、房價資料）", "<strong>要</strong>",
         "否則 PC1 只是「數字最大的那個變數」"],
        ["同單位但量級差很多（收入 vs 年齡）", "<strong>要</strong>", "同上，量級差就是單位差的變形"],
        ["同單位、尺度差異有意義（基因表現、像素）", "看情況", "縮放會把真實的變異差異抹掉"],
        ["已經是比例或分數（0–1 之間）", "通常不用", "尺度已經可比"],
        ["變數是 0/1 指示變數", "小心", "標準化會放大罕見類別，考慮別的方法"]])}

  <h3>二、符號：翻掉不影響任何結論</h3>

  <p>負荷向量描述的是一個<strong>方向</strong>。把 $\\phi_1$ 整支乘上 $-1$，
  它指的還是同一條直線，只是箭頭朝反邊；投影後的變異數 $\\mathrm{{Var}}(-Z) = \\mathrm{{Var}}(Z)$
  也沒變。所以最佳化問題有兩個一樣好的解，套件挑哪一個是實作細節。</p>

  <p>關鍵在於<strong>要一起翻</strong>：近似式用的是乘積 $z_{{im}}\\phi_{{jm}}$，
  兩個都乘 $-1$ 乘積不變，重建出來的資料一模一樣。lab 儲存格 33 就是這樣做的
  （<code>scores[:,1] *= -1</code> 與 <code>components_[1] *= -1</code> 成對出現）。</p>

  <h3 id="dx-var">講義完整實作：先看變異數，再決定要不要標準化</h3>
{card("講義 12 · USArrests 的平均與變異數",
      lab_code(CH, 11) + "\n\n" + lab_code(CH, 15) + "\n\n" + lab_code(CH, 17),
      lab_output(CH, 17), src=src("11、15、17"), out_tag="預期輸出（儲存格 17）",
      note="<strong>6945 對 18.97，差了 366 倍。</strong>看到這種數字就知道非標準化不行了。<br>"
           "注意載入方式是 <code>get_rdataset('USArrests').data</code>（statsmodels 去抓 R 的資料集），"
           "不是 <code>load_data()</code>——<code>USArrests</code> 不在 <code>ISLP</code> 套件裡。"
           "資料的索引是州名，所以 <code>mean()</code>／<code>var()</code> 是逐欄算的。")}

{qa("觀念釐清", [
    ("Q：主成分的符號（正負）為什麼不唯一？這會影響結論嗎？",
     "<p>因為最佳化問題只約束了「方向」與「長度」，沒有約束「朝哪一邊」。"
     "$\\phi_1$ 與 $-\\phi_1$ 定義同一條直線；投影後 $Z_1$ 與 $-Z_1$ 的變異數相同，"
     "所以兩者都是最佳解，套件回傳哪一個取決於底層的 LAPACK 實作。"
     "同一份資料用 <code>numpy.linalg.svd</code> 與 <code>sklearn</code> 的 "
     "<code>PCA()</code> 跑，就可能拿到整組相反的符號（lab 儲存格 50 與 51 就差在這裡）。</p>"
     "<p><strong>不影響任何實質結論</strong>，但會影響你「怎麼說」。"
     "如果 PC1 的負荷量全是正的，你會說「PC1 高 = 犯罪率高」；符號翻掉之後，"
     "同一個主成分要說成「PC1 高 = 犯罪率低」。得分也一起翻，"
     "所以哪些州靠在一起、哪些州離得遠——完全一樣。</p>"
     "<p>實務上的兩個建議：（1）自己定一個約定並寫在報告裡，"
     "例如「讓負荷量總和為正」或「讓某個指標變數的負荷量為正」；"
     "（2）比較兩次分析的結果時，先對齊符號再比，不然會誤以為結果不穩定。</p>"),
    ("Q：為什麼 PCA 之前幾乎一定要標準化？什麼情況下不該標準化？",
     "<p>因為 PCA 的目標函數是變異數，而變異數的大小跟單位有關。"
     "USArrests 的 Assault 變異數 6945、Murder 只有 18.97，"
     "不標準化的話 PC1 的負荷量在 Assault 上是 0.995、在 Murder 上是 0.042——"
     "第一主成分退化成「Assault 換個名字」，PCA 什麼都沒做。</p>"
     "<p>更關鍵的是：這個結果會隨著單位改變。把 Assault 的單位從「每十萬人」改成「每百人」，"
     "它的變異數變成百萬分之一，立刻讓位給 UrbanPop。"
     "<strong>結論不該取決於資料當初是用什麼單位記錄的</strong>，"
     "所以標準化在這裡不是技巧，是為了讓答案有意義。</p>"
     "<p>不該標準化的情形：變數同單位、而且變異數的差異本身是你想保留的資訊。"
     "基因表現量、影像的像素值、同一種感測器的多個通道都屬於這一類。"
     "還有一種情形是資料已經是比例（每欄都在 0 到 1 之間），再標準化沒什麼好處。"
     "判斷的準則很簡單：<strong>問自己「如果某一欄乘上 1000，我希望結論改變嗎？」</strong>"
     "不希望就標準化。</p>"),
])}

{quiz("qScale", "QUIZ · 尺度與符號",
      "同一份 USArrests，A 同學算出 PC1 的負荷量是 <code>[0.54, 0.58, 0.28, 0.54]</code>，"
      "B 同學算出 <code>[-0.54, -0.58, -0.28, -0.54]</code>。發生了什麼事？",
      [(True, "兩人算的是同一個主成分，只差整組符號；只要得分也跟著反號，所有結論都一樣",
        "對。負荷向量描述的是方向，φ 與 −φ 是同一條直線。B 同學的得分會是 A 同學的相反數，"
        "兩人畫出來的 biplot 是彼此的鏡射，誰離誰近完全一樣。"),
       (False, "B 同學一定弄錯了，因為負荷量的平方和要等於 1，不能是負的",
        "平方和的約束沒被違反——(−0.54)² 跟 0.54² 一樣。負荷量本來就可以是負的"
        "（USArrests 的 PC2 就有負的），約束的是平方和，不是每一項的正負。"),
       (False, "B 同學忘了標準化，所以符號才會反過來",
        "不對。忘了標準化會讓<strong>負荷量的數值</strong>完全變樣（Assault 會變成 0.995），"
        "不是只有符號翻掉。B 的數值跟 A 逐位相同，純粹是符號約定不同。")])}
"""

# ── P06 矩陣補全 ───────────────────────────────────────────────────────
_mc_code = (lab_code(CH, 56) + "\n\n" + lab_code(CH, 58) + "\n\n"
            + lab_code(CH, 60) + "\n\n" + lab_code(CH, 62) + "\n\n" + lab_code(CH, 64))

BODIES["completion"] = f"""
  <p>手上的資料矩陣有缺失值，怎麼辦？兩個常見的做法都不太好：
  整列刪掉太浪費（也不現實——缺一格就丟掉一整個州），
  用該欄的平均填補則完全<strong>沒有用到變數之間的相關</strong>。</p>

  <p>P03 說過前 M 個主成分是資料矩陣的最佳秩 M 近似。
  那反過來想：如果 $x_{{ij}} \\approx \\sum_m z_{{im}}\\phi_{{jm}}$，
  那缺掉的那一格也可以用這個式子<strong>算出來</strong>。
  這就是<strong>矩陣補全</strong>（matrix completion）。</p>

  <p>問題是要算主成分得先有完整的矩陣，要有完整的矩陣得先補值——雞生蛋蛋生雞。
  ISLP 的解法是輪流做（演算法 12.1）：先用欄平均粗填，
  算主成分、用低秩近似覆蓋缺失格、再算主成分…直到目標函數不再下降。
  只在<strong>觀測到</strong>的格子上算誤差：</p>

  $$\\min_{{A,B}} \\sum_{{(i,j)\\in\\mathcal{{O}}}}
    \\Big( x_{{ij}} - \\sum_{{m=1}}^{{M}} a_{{im}} b_{{jm}} \\Big)^2$$

  <p>$\\mathcal{{O}}$ 是觀測到的位置集合。跟 P03 的式子唯一的差別就是求和範圍——
  但這一改就沒有封閉解了，只能迭代。</p>

{viz(svg("w07mcSvg", 190) + "\n"
     + chart("w07mcChart", "",
             "。此圖的重點：演算法 12.1 的目標函數（觀測格上的均方誤差）每一輪都下降，"
             "USArrests 上大約八輪就收斂。"),
     [rows_card("這一輪",
                [("缺失格數", "20 / 200", "w07mcMiss"), ("迭代次數", "0", "w07mcIter"),
                 ("觀測格上的 MSS", "—", "w07mcMss"),
                 ("相對改善", "—", "w07mcRel"),
                 ("補值與真值的相關", "—", "w07mcCorr")]),
      info_card("上面那張圖在看什麼",
                '每一欄是一個州（依字母序），四列是四個變數。'
                '顏色是標準化後的數值（藍 = 低、紅 = 高）。'
                '<strong>白色虛線框</strong>是被挖掉的格子；按「單步」之後它們會被填上顏色，'
                '外框變成橘色。<strong>橘框裡的顏色跟旁邊的真值像不像，就是這個方法準不準。</strong>'),
      info_card("這是本頁自己跑的，不是 lab 的數字",
                '缺失位置由前端的固定種子決定，跟 lab 的 <code>np.random.seed(15)</code> 不同，'
                '所以相關係數不會剛好是 0.7114。'
                'lab 的實跑數字在下面的 .deck-extra 卡裡。<br>'
                '課本另外報告了 100 次重複的平均：相關 <strong>0.63 ± 0.11</strong>；'
                '如果作弊用完整資料算，是 0.79 ± 0.08。', "ISLP §12.3")],
     "w07mcStatus", "按「單步」跑演算法 12.1 的一輪：算秩一近似 → 覆蓋缺失格 → 算目標函數。",
     '<label class="slider-label" style="margin-right:.3rem;">缺失格數</label>'
     '<input type="range" id="w07mcSlider" min="10" max="50" step="10" value="20" '
     'oninput="w07mcSetMiss()" style="width:120px;accent-color:var(--accent3);">'
     '<span id="w07mcSliderVal" style="min-width:34px;font-family:\'JetBrains Mono\',monospace;'
     'font-size:.82rem;color:var(--accent);font-weight:600;">20</span>'
     '<button class="btn btn-step" onclick="w07mcStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w07mcRun()">▶ 跑到收斂</button>'
     '<button class="btn btn-toggle" onclick="w07mcReseed()">🔀 換缺失位置</button>'
     '<button class="btn btn-reset" onclick="w07mcReset()">重置</button>')}

{info("三個前提，少一個就不要用", '''<strong>1. 缺失必須是隨機的</strong>（missing at random）。
  「電子秤剛好沒電」可以補；「病人太重上不了秤」不行——缺失本身帶著資訊，
  補出來的值會系統性偏低。<br>
  <strong>2. 變數之間要有相關。</strong>低秩近似能work是因為欄與欄之間可以互相預測；
  四個互相獨立的變數，補值不會比欄平均好。<br>
  <strong>3. M 要選。</strong>選太小補不出細節，選太大會把雜訊也配進去。
  課本第 11 題就是叫你把缺失比例從 5% 掃到 30%、M 從 1 掃到 8，看誤差怎麼變。''', "warm")}

  <h3 id="dx-mc">講義完整實作：演算法 12.1 的三十行</h3>
{card("講義 12 · 挖掉 20 格，然後用主成分反覆填補", _mc_code, lab_output(CH, 64),
      src=src("56、58、60、62、64"), out_tag="預期輸出（儲存格 64）",
      note="讀法：<code>low_rank(Xhat, M=1)</code> 是步驟 2(a)（用 SVD 取秩一近似）、"
           "<code>Xhat[ismiss] = Xapp[ismiss]</code> 是 2(b)（<strong>只覆蓋缺失格</strong>）、"
           "<code>mss</code> 是 2(c) 的目標函數。<br>"
           "MSS 從 0.395 掉到 0.381 就幾乎不動了，第 8 輪相對誤差跌破 <code>1e-7</code> 收工。"
           "注意分母用的是 <code>mss0</code> 而不是 <code>mss</code>——"
           "這樣收斂輪數就不會因為把整個 X 乘上一個常數而改變。<br>"
           "挖法也有講究：先隨機選 20 個州、每州再隨機挑一個變數，"
           "所以<strong>每一列至少留三個觀測值</strong>。整列都空的話，什麼方法都補不出來。")}

{card("講義 12 · 補得準不準", lab_code(CH, 66), lab_output(CH, 66), src=src("66、68、69"),
      note="20 個補值與真值的相關係數 <strong>0.711</strong>。"
           "lab 儲存格 68–69 換成 <code>fancyimpute</code> 的 "
           "<code>SoftImpute(max_rank=1)</code> 再跑一次，相關係數幾乎一樣——"
           "說明這支三十行的迴圈沒有偷工減料，"
           "而真的要上線時直接用套件（它有更好的收斂控制與正則化）就好。")}

{quiz("qMc", "QUIZ · 矩陣補全",
      "演算法 12.1 的步驟 2(b) 只把<strong>缺失</strong>的格子換成低秩近似值，"
      "觀測到的格子保持原值。為什麼不乾脆全部換掉？",
      [(True, "觀測值是真實資料，是唯一的資訊來源；換掉它們就沒有東西可以把近似「拉住」了",
        "對。目標函數（式 12.12）只在觀測格上算誤差，觀測格就是這個問題的「訓練資料」。"
        "全部換成低秩近似的話，迭代會收斂到一個跟原始資料無關的秩 M 矩陣。"),
       (False, "全部換掉在數學上也對，只是會多算幾輪比較慢",
        "不對，不是速度問題而是正確性問題。把觀測格也覆蓋掉，下一輪的 SVD 就是對"
        "「上一輪的秩 M 近似」做分解——它已經是秩 M 了，於是立刻「收斂」，但收斂到的東西沒有意義。"),
       (False, "因為觀測格沒有誤差，低秩近似在那些位置一定完全等於原值",
        "剛好相反：低秩近似在觀測格上<strong>也有</strong>誤差（那正是式 12.14 在算的東西）。"
        "如果沒有誤差，就不需要迭代了。")])}
"""

# ── P07 K-means ───────────────────────────────────────────────────────
_km_code = lab_code(CH, 103) + "\n\n" + lab_code(CH, 105) + "\n\n" + lab_code(CH, 107)

BODIES["kmeans"] = f"""
  <p>換一種化簡方式：不找低維座標，直接把資料<strong>分成 K 群</strong>。
  好的分群是「群內盡量像」，寫成式子就是把群內變異的總和最小化：</p>

  $$\\min_{{C_1,\\dots,C_K}} \\left\\{{ \\sum_{{k=1}}^{{K}} W(C_k) \\right\\}},
    \\qquad W(C_k) = \\frac{{1}}{{|C_k|}} \\sum_{{i,i' \\in C_k}} \\sum_{{j=1}}^{{p}}
    (x_{{ij}} - x_{{i'j}})^2$$

  <p>$W(C_k)$ 是第 k 群內所有<strong>兩點之間</strong>的平方歐氏距離總和除以群的大小。
  看起來要算 $|C_k|^2$ 個距離，但 ISLP 式 12.18 給了一個很好用的恆等式：</p>

  $$\\frac{{1}}{{|C_k|}} \\sum_{{i,i' \\in C_k}} \\sum_{{j=1}}^{{p}} (x_{{ij}} - x_{{i'j}})^2
    = 2 \\sum_{{i \\in C_k}} \\sum_{{j=1}}^{{p}} (x_{{ij}} - \\bar x_{{kj}})^2$$

  <p>右邊只需要算每個點<strong>到群心的距離</strong>。這個恆等式不只省算力，
  它直接告訴你演算法該長什麼樣：</p>

{info("演算法 12.2（K-means）", '''<strong>步驟 1：</strong>隨機給每一筆資料一個 1 到 K 的編號。<br>
  <strong>步驟 2：</strong>重複下面兩件事，直到指派不再改變：<br>
  &nbsp;&nbsp;<strong>(a)</strong> 算出每一群的<strong>形心</strong>（群內每個特徵的平均）。<br>
  &nbsp;&nbsp;<strong>(b)</strong> 把每一筆資料指派給<strong>最近</strong>的形心。<br>
  兩步都保證讓目標函數下降：(a) 因為平均是讓平方偏差最小的常數；
  (b) 因為換到更近的形心只會讓自己那一項變小。所以目標函數<strong>單調不增</strong>，一定會停。''')}

{viz(svg("w07kmSvg", 330),
     [info_card("演算法 12.2", '<div class="pseudo-code" id="w07kmCode" style="font-size:.72rem;">'
                '<span class="line" data-l="1">隨機指派 1..K 給每一點</span>\n'
                '<span class="line" data-l="2"><span class="kw">while</span> 指派還在變：</span>\n'
                '<span class="line" data-l="3">    <span class="com"># 2(a)</span> 群心 = 群內平均</span>\n'
                '<span class="line" data-l="4">    <span class="com"># 2(b)</span> 每點 → 最近的群心</span>\n'
                '<span class="line" data-l="5">回報這組指派</span></div>', "CODE"),
      rows_card("目前狀態",
                [("K", "3", "w07kmK"), ("第幾步", "—", "w07kmStepN"),
                 ("這一步在做什麼", "—", "w07kmPhase"),
                 ("群內平方和", "—", "w07kmWss"),
                 ("有幾點換了群", "—", "w07kmMoved")]),
      rows_card("換過的初始值",
                [("試過幾組", "0", "w07kmTried"), ("最好的收斂值", "—", "w07kmBest"),
                 ("最差的收斂值", "—", "w07kmWorst")], "圖 12.9"),
      info_card("重點在右邊那條曲線",
                '右邊畫的是群內平方和隨步數的變化。它<strong>只會往下，不會往上</strong>——'
                '這就是式 12.18 保證的事。曲線壓平就是收斂了。<br>'
                '但收斂到的是<strong>局部</strong>極小。按「換初始值」幾次，'
                '你會看到同樣的 K 收斂到不同的值（課本圖 12.9 在同一份資料上跑六次，'
                '得到三個不同的局部極小）。')],
     "w07kmStatus", "選 K 之後按「單步」，交替執行「算群心」與「重新指派」。",
     '<label class="slider-label" style="margin-right:.3rem;">K =</label>'
     '<select id="w07kmSel" class="mono" onchange="w07kmSetK()">'
     '<option value="2">2</option><option value="3" selected>3</option>'
     '<option value="4">4</option></select>'
     '<button class="btn btn-step" onclick="w07kmStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w07kmRun()">▶ 跑到收斂</button>'
     '<button class="btn btn-toggle" onclick="w07kmReseed()">🔀 換初始值</button>'
     '<button class="btn btn-reset" onclick="w07kmReset()">重置</button>')}

  <h3 id="dx-km">講義完整實作：<code>KMeans()</code></h3>
{card("講義 12 · K = 2 的模擬資料", _km_code, lab_output(CH, 107), src=src("103、105、107"),
      out_tag="預期輸出（儲存格 107）",
      note="資料是刻意造的：前 25 筆的平均被平移過，所以真的有兩群。"
           "<code>labels_</code> 幾乎完美地把前 25 與後 25 分開——"
           "但注意<strong>群的編號是任意的</strong>，0 與 1 交換不代表結果不同。"
           "這也是為什麼比較兩種分群結果要用 <code>pd.crosstab</code>，不能直接比對標籤。")}

{card("講義 12 · n_init 為什麼要設大", lab_code(CH, 113), lab_output(CH, 113), src=src("113"),
      note="<code>inertia_</code> 就是群內平方和（式 12.17 要最小化的那個）。"
           "<code>n_init=1</code> 得到 <strong>76.85</strong>、<code>n_init=20</code> 得到 "
           "<strong>75.06</strong>——同一份資料、同一個 K、同一個 <code>random_state</code>，"
           "差別只在試了幾組初始值。<br>"
           "<strong>76.85 是一個局部極小，不是錯誤</strong>，程式不會警告你。"
           "所以 lab 的建議是：<code>n_init</code> 設 20 或 50，"
           "並且一定要設 <code>random_state</code> 讓結果可重現。")}

{qa("觀念釐清", [
    ("Q：K-means 為什麼每次跑可能給不同答案？該怎麼辦？",
     "<p>因為演算法 12.2 的第 1 步是<strong>隨機</strong>指派。"
     "之後的每一步都只保證目標函數下降，不保證下降到全域最小——"
     "它會滑進離初始位置最近的那個「盆地」就停住。"
     "把 n 筆資料分成 K 群大約有 $K^n$ 種方式，要真的找到全域最小得全部列舉，這不可能，"
     "所以我們接受局部極小。</p>"
     "<p>ISLP 圖 12.9 把同一份資料跑六次，得到三個不同的局部極小：目標函數 235.8（四次）、"
     "320.9、310.9。其中 235.8 明顯把三群分得最開。"
     "重點是：<strong>如果你只跑一次，剛好抽到 320.9 那組初值，程式不會告訴你有問題。</strong></p>"
     "<p>標準做法就是<strong>多重初始化</strong>：跑很多組不同的初值，"
     "回報目標函數最小的那一次。<code>scikit-learn</code> 的 <code>n_init</code> 就是這件事"
     "（預設 10，lab 建議設 20 或 50）。另外一定要設 <code>random_state</code>——"
     "不是為了「挑一個好看的種子」，而是為了讓別人能重現你的數字。"
     "上面那張元件的「換初始值」按鈕，按幾次就會看到這個現象。</p>"),
])}

{quiz("qKm", "QUIZ · K-means",
      "為什麼 K-means 的群內平方和一定會單調下降，最後一定會停？",
      [(True, "步驟 2(a) 用群內平均使平方偏差最小、步驟 2(b) 把點移到更近的形心，兩步都不會讓目標變大",
        "對。而且可能的指派方式只有有限多種，目標函數又單調不增，"
        "所以不可能無限循環——一定會在某一步之後指派不再改變。"),
       (False, "因為每一步都會減少群數，群數減到 K 就停了",
        "不對。K-means 的群數從第一步開始就固定是 K，全程不變。"
        "會「合併群」的是階層式分群（下一節），不是 K-means。"),
       (False, "因為 scikit-learn 設了 max_iter 上限，跑到上限就停",
        "<code>max_iter</code> 是保險絲，不是停止的原因。"
        "K-means 在數學上就保證會收斂（通常十幾輪內），碰到 <code>max_iter</code> 反而是異常。")])}
"""

# ── P08 階層式分群 ─────────────────────────────────────────────────────
_hc_code = lab_code(CH, 117) + "\n\n" + lab_code(CH, 123) + "\n\n" + lab_code(CH, 127)

BODIES["hclust"] = f"""
  <p>K-means 有個明顯的麻煩：<strong>你得先決定 K</strong>。
  階層式分群不必——它一次把 1 到 n 群的所有結果都算出來，畫成一棵樹，
  你要幾群就切在對應的高度。</p>

  <p>做法（凝聚式，agglomerative，也叫 bottom-up）簡單到不像演算法：</p>

{info("演算法 12.3（階層式分群）", '''<strong>步驟 1：</strong>每一筆資料自己是一群，
  算出所有 $\\binom{n}{2}$ 對的相異度。<br>
  <strong>步驟 2：</strong>從 i = n 做到 2：<br>
  &nbsp;&nbsp;<strong>(a)</strong> 在目前 i 群裡找<strong>最相似</strong>的一對，把它們合併。
  這一對的相異度就是樹上合併的<strong>高度</strong>。<br>
  &nbsp;&nbsp;<strong>(b)</strong> 重算剩下 i − 1 群之間的相異度。''')}

  <p>樹狀圖（dendrogram）的讀法有一條鐵律，很多人第一次都會讀錯：</p>

{info("看高度，不要看左右", '''兩筆資料有多相似，看的是<strong>它們所在的分支第一次合併的高度</strong>，
  <strong>不是</strong>它們在水平方向上有多近。<br>
  ISLP 圖 12.12 的例子：第 9 號與第 2 號在圖上左右相鄰，
  但第 9 號跟第 2、8、5、7 號都是在同一個高度（約 1.8）才合併的，
  所以它跟這四個的相似度完全一樣。<br>
  原因是每一次合併都可以把左右兩支<strong>對調</strong>而不改變樹的意義，
  n 個葉子有 $2^{n-1}$ 種等價的畫法。水平位置只是其中一種排法而已。''', "warm")}

  <p>剩下的問題是：兩<strong>群</strong>之間的相異度怎麼定？這叫做
  <strong>連結方式</strong>（linkage），四種常見的定義在下面那張表。
  換 linkage，樹的形狀會整個變——這是這一節最重要的實驗。</p>

{viz(svg("w07dendroSvg", 350),
     [rows_card("這一刀切出什麼",
                [("linkage", "complete", "w07dendroLk"), ("切在高度", "—", "w07dendroH"),
                 ("切出幾群", "—", "w07dendroK"),
                 ("最高的合併", "—", "w07dendroMax"),
                 ("「一次只黏一顆」的合併次數", "—", "w07dendroChain")]),
      info_card("怎麼玩",
                '拖動<strong>橘色虛線</strong>（或用滑桿）上下移動切線，左邊的散佈圖會同步上色。'
                '往上切群數變少、往下切變多。<br>'
                '重點在那個 <code>select</code>：把 linkage 換成 <strong>single</strong>，'
                '看樹的形狀怎麼垮掉。'),
      info_card("single linkage 的鏈狀效應",
                'single 取兩群之間<strong>最小</strong>的距離，'
                '所以只要有一個點靠近某個大群，整群就被拉過去。'
                '結果是一個很大的群不斷把單一觀測值一顆一顆黏上去（trailing cluster），'
                '切下去往往得到「一大群 + 幾個孤兒」。'
                '<strong>右側那個「一次只黏一顆」的次數就是在量這件事。</strong>', "圖 12.14"),
      info_card("centroid 的反轉",
                '把 linkage 換成 <strong>centroid</strong>，注意有些合併會出現'
                '<strong>反轉</strong>（inversion）：兩群合併的高度比它們各自的高度還低，'
                '線段變成往上長。這種樹很難解讀，所以統計上偏好 complete 與 average。')],
     "w07dendroStatus", "拖動橘色切線改變群數，換 select 看四種 linkage 的差別。",
     '<label class="slider-label" style="margin-right:.3rem;">linkage</label>'
     '<select id="w07dendroSel" class="mono" onchange="w07dendroSetLk()">'
     '<option value="complete" selected>complete</option>'
     '<option value="average">average</option>'
     '<option value="single">single</option>'
     '<option value="centroid">centroid</option></select>'
     '<label class="slider-label" style="margin:0 .3rem 0 .5rem;">切線高度</label>'
     '<input type="range" id="w07dendroSlider" min="2" max="98" step="1" value="55" '
     'oninput="w07dendroFromSlider()" style="width:120px;accent-color:var(--accent3);">'
     '<button class="btn btn-reset" onclick="w07dendroReset()">重置</button>')}

{table(["Linkage", "群間相異度的定義", "樹的形狀", "評語"],
       [["<strong>Complete</strong>", "兩群之間<strong>最大</strong>的那個距離",
         "平衡、群大小相近", "最常用；對離群值不算敏感"],
        ["<strong>Average</strong>", "所有跨群配對距離的<strong>平均</strong>",
         "平衡", "最常用；統計上性質較好"],
        ["<strong>Single</strong>", "兩群之間<strong>最小</strong>的那個距離",
         "鏈狀、拖尾", "容易產生一大群 + 一堆孤兒，少用"],
        ["<strong>Centroid</strong>", "兩群<strong>形心</strong>之間的距離",
         "可能出現反轉", "基因體學常用，但反轉讓樹難以解讀"]])}

  <h3>相異度也要選：歐氏距離還是相關係數？</h3>

  <p>前面一直用歐氏距離。但有時候你在意的是<strong>輪廓的形狀</strong>而不是高低：
  兩位顧客一個買很多、一個買很少，但買的品項比例一致——
  歐氏距離很大，<strong>相關係數距離</strong>（$1 - r_{{ii'}}$）很小。
  ISLP 圖 12.15 就是這個對比。哪個對，取決於你的科學問題，沒有預設答案。</p>

  <h3 id="dx-hc">講義完整實作：<code>AgglomerativeClustering</code> 與 <code>cut_tree</code></h3>
{card("講義 12 · 建樹、畫樹、切樹", _hc_code, lab_output(CH, 127),
      src=src("117、119、123、127"), out_tag="預期輸出（儲存格 127）",
      note="<code>distance_threshold=0</code> 加 <code>n_clusters=None</code> 是"
           "「把整棵樹算完、先不要切」的寫法。<br>"
           "<code>scikit-learn</code> 不直接給 <code>scipy</code> 畫圖要的 "
           "<strong>linkage matrix</strong>，所以要用 <code>ISLP.cluster.compute_linkage()</code> 轉一次。"
           "<code>color_threshold=-np.inf</code> 是關掉 <code>dendrogram()</code> "
           "預設的自動上色（預設會暗示一個切法，容易誤導）。<br>"
           "<code>cut_tree(..., n_clusters=4)</code> 回傳每一筆資料的群編號。"
           "也可以給 <code>height=5</code> 用高度切——本頁那條橘色虛線做的就是這件事。")}

{quiz("qHc", "QUIZ · 讀樹狀圖",
      "在一棵樹狀圖上，第 3 號與第 7 號葉子左右緊鄰，但它們所在的分支要到高度 8 才合併；"
      "第 3 號與第 20 號隔了很遠，卻在高度 2 就合併了。誰跟第 3 號比較相似？",
      [(True, "第 20 號，因為相似度看的是「第一次合併的高度」，2 比 8 低",
        "對。水平位置完全沒有意義——每個合併點的左右兩支都可以對調，"
        "n 個葉子有 2^(n−1) 種等價畫法。只有縱軸的高度帶資訊。"),
       (False, "第 7 號，因為在樹狀圖上相鄰代表被歸在同一個小群",
        "這是最常見的誤讀。相鄰只是某一種排法的結果；ISLP 圖 12.12 就是專門用來打破這個直覺的例子。"),
       (False, "看不出來，樹狀圖只能看群數，不能比較個別觀測值",
        "不對。樹狀圖<strong>可以</strong>比較個別觀測值，方法就是看它們第一次合併的高度——"
        "那個高度正是兩群合併時的相異度。")])}
"""

# ── P09 分群的實務問題 ─────────────────────────────────────────────────
_vs_code = lab_code(CH, 152) + "\n\n" + lab_code(CH, 176)

BODIES["practical"] = f"""
  <p>演算法都很乾淨，麻煩全在做決定的地方。ISLP §12.4.3 把它們列成一張清單，
  每一項都會實質改變結果：</p>

  <ul>
    <li>要不要先<strong>標準化</strong>？</li>
    <li>階層式分群：用什麼<strong>相異度</strong>？什麼 <strong>linkage</strong>？樹要<strong>切在哪</strong>？</li>
    <li>K-means：<strong>K 取多少</strong>？</li>
    <li>資料裡的<strong>離群值</strong>怎麼辦？</li>
  </ul>

  <p>下面這個元件是課本圖 12.16 的可玩版本：一家網路商店只賣兩種東西——襪子與電腦。
  八位顧客的購買紀錄一樣，<strong>只是換一種尺度，K = 2 的分群就換一組答案</strong>。</p>

{viz(svg("w07practSvg", 340),
     [rows_card("K = 2 的結果",
                [("目前的尺度", "原始次數", "w07practMode"),
                 ("第 1 群", "—", "w07practG1"), ("第 2 群", "—", "w07practG2"),
                 ("分群其實由誰決定", "—", "w07practDrv"),
                 ("群內平方和", "—", "w07practWss")]),
      info_card("三種尺度在做什麼",
                '<strong>原始次數：</strong>襪子 0–11 雙、電腦 0–1 台。'
                '襪子的變異大得多，距離幾乎只由襪子決定，電腦等於沒參與。<br>'
                '<strong>標準化：</strong>兩個變數都變成變異數 1，電腦終於有影響力——'
                '分群變成「有買電腦」與「沒買電腦」。<br>'
                '<strong>花費金額：</strong>電腦一台 1400 元、襪子一雙 2 元，'
                '換算成金額之後<strong>反過來由電腦主宰</strong>。', "圖 12.16"),
      info_card("離群值那個 toggle",
                '按下去會加入第 9 位顧客：買了 60 雙襪子、沒買電腦。'
                'K-means <strong>一定要把每一點分進某一群</strong>，'
                '所以這一個點會硬生生把一整群拉過去，'
                '剩下八位全部被擠進另一群。<br>'
                '課本的建議是改用混合模型（mixture model，K-means 的「軟」版本），'
                '或者先把明顯的離群值挑出來單獨處理。'),
      info_card("課本第 5 題就是這一題",
                'ISLP 第 12.6 節第 5 題：「用圖 12.16 的三種尺度各跑一次 K = 2，'
                '描述你預期看到什麼。」把上面的 select 切三次就是答案。', "第 5 題")],
     "w07practStatus", "換一種尺度，同樣八位顧客的 K = 2 分群結果就變了。",
     '<label class="slider-label" style="margin-right:.3rem;">尺度</label>'
     '<select id="w07practSel" class="mono" onchange="w07practSetMode()">'
     '<option value="raw" selected>原始次數</option>'
     '<option value="scaled">標準化</option>'
     '<option value="dollar">花費金額</option></select>'
     '<button class="btn btn-toggle" onclick="w07practToggleOut()">加入 / 移除離群值</button>'
     '<button class="btn btn-reset" onclick="w07practReset()">重置</button>')}

  <h3>「分群結果對不對」有客觀標準嗎？</h3>

  <p>沒有。這不是敷衍，是這一類方法的本質限制。
  <strong>任何時候把資料丟去分群，它都會給你群</strong>——即使資料是純雜訊。
  真正想問的是「這些群在獨立的新資料上也會出現嗎」，
  文獻上有給群一個 p 值的做法，但沒有共識（細節在 ESL）。</p>

  <p>能做的是幾件比較樸素的事：</p>

{table(["做法", "怎麼做", "在檢查什麼"],
       [["換設定重跑", "換 linkage、換距離、換 K、標準化與否",
         "哪些結構每次都出現（那些比較可信）"],
        ["抽子樣本重跑", "隨機丟掉 10–20% 的資料再分群一次", "分群對擾動穩不穩（通常不太穩）"],
        ["對照外部標籤", "有領域標籤時用 <code>crosstab</code> 或 ARI 比對",
         "分群有沒有抓到已知的結構（這是<em>事後</em>檢查，不是調參依據）"],
        ["看得出解釋嗎", "每一群的變數平均長什麼樣，能不能講成一句話",
         "群有沒有實質意義，還是只是切開了連續的雲"]])}

  <h3 id="dx-vs">講義完整實作：K-means 與階層式分群給的答案不一樣</h3>
{card("講義 12 · NCI60 上兩種分群的交叉表", _vs_code, lab_output(CH, 176),
      src=src("152、172、176"), out_tag="預期輸出（儲存格 176）",
      note="同一份 NCI60（64 個細胞株 × 6830 個基因）、同樣切 4 群，"
           "兩種方法的結果<strong>只是「略有不同」而不是相同</strong>："
           "K-means 的第 3 群等於階層式的第 2 群，但 K-means 的第 0 群"
           "混了階層式第 0 群的一部分加上整個第 1 群。<br>"
           "先看群編號是任意的（所以要用 <code>crosstab</code> 而不是直接比標籤）。"
           "lab 儲存格 172 另外把階層式的 4 群對上真實癌症類型："
           "所有白血病落在同一群，但乳癌散在三群——"
           "<strong>分群抓到了一部分結構，不是全部。</strong>")}

{qa("觀念釐清", [
    ("Q：分群結果「對不對」要怎麼判斷？沒有 y 的時候有沒有客觀標準？",
     "<p>沒有一個像測試誤差那樣的單一數字。原因很直接：測試誤差需要正確答案，"
     "而分群問題裡「正確的群」並不存在（如果存在，那就是分類問題了）。</p>"
     "<p>常見的內部指標（silhouette、Calinski–Harabasz、gap statistic）能算，"
     "但它們量的是<strong>幾何上的緊密與分離</strong>，不是「這些群是不是真的」。"
     "一份純雜訊的資料照樣可以有不錯的 silhouette；"
     "反過來，兩個真實但形狀狹長交錯的子群，silhouette 會很難看。"
     "所以這些指標可以用來在同一個方法內部比較 K，不能用來宣告「分群成功」。</p>"
     "<p>比較誠實的做法是三件事併用："
     "<strong>（1）穩定性</strong>——換設定、抽子樣本重跑，看哪些群每次都在；"
     "<strong>（2）可解釋性</strong>——每一群能不能用領域語言講成一句話；"
     "<strong>（3）外部驗證</strong>——在獨立的新資料上重做一次，或對上事後才知道的標籤。"
     "ISLP 的結語值得抄下來：分群結果不該當成資料的絕對真相，"
     "而是<strong>形成科學假設的起點</strong>。</p>"),
    ("Q：PCA 與分群都在「找結構」，差在哪？",
     "<p>差在產出的東西是<strong>連續</strong>還是<strong>離散</strong>。"
     "PCA 給每一筆資料一組新的連續座標（得分），資料在低維空間裡還是一片雲；"
     "分群給每一筆資料一個離散的群編號，雲被切成幾塊。</p>"
     "<p>對應的假設也不同。PCA 假設「大部分變異集中在少數幾個方向」，"
     "它不假設資料裡有子群——如果真的只有一片橢圓形的雲，PCA 照樣給你很有用的答案。"
     "分群則假設「資料由幾個同質的子群組成」，如果實際上是連續漸變的，"
     "切出來的界線就是人造的。</p>"
     "<p>實務上兩者常常串起來用，而且順序有講究："
     "<strong>先 PCA 再分群</strong>是很常見的做法（lab 儲存格 178 就對 NCI60 的前五個得分向量做階層式分群），"
     "理由是前幾個主成分可以看成資料的低雜訊版本。"
     "反過來也有用：分群完之後，用前兩個主成分的散佈圖把群畫出來，"
     "因為 p > 2 的時候你沒別的辦法看。</p>"),
])}

{quiz("qPrac", "QUIZ · 分群的實務決策",
      "資料裡有兩三個明顯的離群值（例如那位買 60 雙襪子的顧客）。"
      "對 K-means 與階層式分群，下面哪個處理方式最站得住腳？",
      [(True, "兩種方法都會被離群值扭曲，因為它們強迫每一點都進某一群；"
              "該先辨識並單獨處理，或改用允許「不屬於任何群」的方法",
        "對。ISLP §12.4.3 明確提到這一點，並建議混合模型（K-means 的軟版本）。"
        "DBSCAN／HDBSCAN 也是一條路——它們把密度不足的點標成雜訊，不強迫入群。"),
       (False, "階層式分群不受影響，因為離群值會自己形成一個單獨的分支",
        "只有一半對。離群值確實常自己掛在樹的高處，"
        "但這會<strong>吃掉一個群的額度</strong>：切 3 群時可能得到「兩個離群值 + 全部其他人」，"
        "真正想看的結構反而被壓在一起。single linkage 更糟，離群值會把整棵樹拉成鏈狀。"),
       (False, "只要把資料標準化，離群值的影響就會被消掉",
        "不對。標準化調整的是各<strong>變數</strong>之間的相對權重，"
        "對某一<strong>筆觀測值</strong>離大家很遠這件事沒有幫助——"
        "60 雙襪子標準化之後還是離群，只是換了刻度。")])}
"""

# ── P10 流形學習與 t-SNE（ESL 進階）─────────────────────────────────────
BODIES["manifold"] = f"""
  <p class="skip-note">這一節是課堂沒細講的延伸（講義 12 · p.39–53），第一輪可以直接跳過去看
  <a href="#exercises">EX 練習</a>。t-SNE 在論文裡到處都是，值得知道它會怎麼騙人。</p>

  <p>PCA 是<strong>線性</strong>投影：它只能把資料壓到一個平面上。
  可是很多高維資料的結構是彎的——想像一張捲起來的紙，
  紙上相鄰的兩點在三維空間裡可能隔得很遠，而 PCA 只會把整捲紙壓扁，把不該相鄰的點壓在一起。
  <strong>流形學習</strong>（manifold learning）就是假設資料落在一個低維的彎曲流形上，
  想辦法把它攤平。</p>

  <p>最有名的是 <strong>t-SNE</strong>（t-distributed stochastic neighbor embedding）。
  它的想法完全不是「找方向」，而是「保住鄰居關係」：</p>

  <ol>
    <li>在高維空間把「j 是 i 的鄰居」轉成機率 $p_{{ij}}$（距離近的機率大，用高斯核，
    寬度由 <strong>perplexity</strong> 控制）。</li>
    <li>在低維空間對同一對點也定一個機率 $q_{{ij}}$，但用<strong>重尾的 t 分佈</strong>。</li>
    <li>調整低維座標，讓兩個分佈的 KL 散度最小。</li>
  </ol>

  <p>第 2 步為什麼要換成 t 分佈？因為高維空間「裝得下」的鄰居比低維多得多，
  硬要用高斯核會讓所有點擠在一起（crowding problem）；
  t 分佈的尾巴重，允許中距離的點被推得比較遠，圖才會散開。</p>

{viz(chart("w07tsneChart", "tall",
           "。此圖的重點：PCA 的線性投影把十個數字混在一起，"
           "t-SNE 則把它們分成清楚的團——但團的大小與團之間的距離都不能當真。"),
     [rows_card("目前這張圖",
                [("方法", "PCA（線性投影）", "w07tsneName"), ("點數", "—", "w07tsneN"),
                 ("原始維度", "8 × 8 = 64", "w07tsneDim"),
                 ("類別數", "10", "w07tsneCls")]),
      info_card("怎麼比",
                '同一批 500 張手寫數字（<code>load_digits</code>，8×8 灰階）用三種方法壓到 2 維，'
                '顏色是真實的數字標籤——<strong>標籤沒有參與計算，只用來上色。</strong><br>'
                '切到 <code>perplexity = 5</code> 再切到 30，看同一份資料可以長得多不一樣。'),
      info_card("t-SNE 的四個陷阱",
                '<strong>1. 座標沒有意義</strong>，軸也沒有單位，不要說「往右邊是什麼」。<br>'
                '<strong>2. 團的大小不可信</strong>——t-SNE 會把稀疏的團擴張、密的團壓縮。<br>'
                '<strong>3. 團之間的距離不可信</strong>，全域結構不保證被保留。<br>'
                '<strong>4. 換參數就換一張圖</strong>：perplexity、學習率、初始化、隨機種子都會變。'
                '所以要多跑幾組再下結論。', "講義 p.51–53")],
     "w07tsneStatus", "同一批 500 張手寫數字，換方法看嵌入結果怎麼變。",
     '<label class="slider-label" style="margin-right:.3rem;">方法</label>'
     '<select id="w07tsneSel" class="mono" onchange="w07tsneSet()">'
     '<option value="pca" selected>PCA</option>'
     '<option value="tsne5">t-SNE · perplexity 5</option>'
     '<option value="tsne30">t-SNE · perplexity 30</option></select>')}

{info("t-SNE 不是萬能，也不是 PCA 的替代品", '''<strong>t-SNE 幾乎只能用來「看」。</strong>
  它沒有 <code>transform()</code>（新資料無法投影到既有的嵌入上，
  <code>openTSNE</code> 之類的套件才另外提供近似做法），
  也不像 PCA 有負荷量可以解讀「這個方向由哪些變數組成」。<br>
  要當前處理放進 pipeline，UMAP 比較合適——它有 <code>transform()</code>，
  lab 儲存格 86–94 就示範了「先 UMAP 再分類」，
  而且 SVC 的正確率從 0.62 拉到 0.98。<strong>但那已經是監督式的評估了</strong>，
  能這樣調就是因為有 y 可以看。''', "warm")}

  <h3 id="dx-tsne">講義完整實作：<code>TSNE</code></h3>
{card("講義 12 · digits 的 t-SNE", lab_code(CH, 74) + "\n\n" + lab_code(CH, 75),
      lab_output(CH, 75), src=src("71、72、74、75"),
      note="<code>init=\"pca\"</code> 是重要的細節：用 PCA 的結果當初始位置，"
           "比隨機初始化穩定得多，也讓結果比較可重現（配上 <code>random_state=0</code>）。<br>"
           "輸出的兩個 KL 散度值得注意：早期誇張階段（early exaggeration）250 輪之後是 61.3，"
           "跑完 1000 輪降到 <strong>0.754</strong>。"
           "<strong>KL 散度只能用來比較同一份資料的不同次執行</strong>，"
           "它不是「分得好不好」的分數。<br>"
           "lab 後面還示範了 <code>openTSNE</code>（更快）、"
           "<code>UMAP</code>（有 <code>transform()</code>）與 <code>PHATE</code>（保留軌跡結構）。")}

{quiz("qTsne", "QUIZ · t-SNE 的讀法",
      "一張 t-SNE 圖上，A 團與 B 團距離很遠，A 團看起來比 B 團大三倍。可以下什麼結論？",
      [(True, "幾乎什麼都不能下：團的大小與團間距離都不是 t-SNE 保證保留的量",
        "對。t-SNE 只在意「局部鄰居關係」，會把稀疏的團擴張、把密的團壓縮，"
        "全域結構也不保證。能說的只有「A 團內部的點彼此比較像」。"),
       (False, "A 群的樣本數大約是 B 群的三倍",
        "不對。面積跟樣本數無關——t-SNE 會把密度低的團攤開、密度高的團擠緊，"
        "所以面積反映的是原始密度，而且還被非線性地扭曲過。要看樣本數就去數點。"),
       (False, "A 與 B 距離遠，代表它們在原始 64 維空間裡也離得很遠",
        "不能這樣推。t-SNE 的目標函數只懲罰「近的點被畫遠」，"
        "對「遠的點被畫得多遠」幾乎不管。要談全域距離請用 PCA 或 MDS。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP §12.6 第 1 題（b）",
      "課本第 1 題要你先證明恆等式 12.18，再<strong>用它說明</strong>演算法 12.2 每一輪都讓"
      "目標函數 12.17 下降。這個論證的關鍵是什麼？",
      [(True, "式 12.18 把「群內兩兩距離」換成「各點到群心的距離」，"
              "於是步驟 2(a) 取平均與步驟 2(b) 取最近，各自都在最小化那個和",
        "對。平均是讓平方偏差最小的常數（這給了 2(a)），"
        "把點換到更近的群心只會讓自己那一項變小（這給了 2(b)）。"
        "兩步都不增，加上可能的指派只有有限多種，所以一定收斂。"),
       (False, "因為每一輪都會有點換群，換群一定讓目標下降，所以會一直下降到 0",
        "前半句反了：收斂時就<strong>沒有</strong>點換群，那才是停止條件。"
        "而且目標函數不會降到 0（除非每群只剩一點）——它降到一個局部極小就停。"),
       (False, "因為 K-means 的目標函數是凸的，梯度下降保證收斂到全域最小",
        "目標函數對「指派」這個離散變數並不凸，K-means 也不是梯度下降。"
        "它保證的只有<strong>局部</strong>極小——這正是要設 <code>n_init</code> 的理由。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP §12.6 第 4 題（b）",
      "single linkage 與 complete linkage 各做一棵樹。在 single 的樹上"
      "$\\{{5\\}}$ 與 $\\{{6\\}}$ 這兩群在某個高度合併；complete 的樹上它們也會合併。"
      "哪一棵的合併位置比較高？",
      [(True, "一樣高，因為兩群都只有一個點，最大距離與最小距離都是 d(5,6)",
        "對。linkage 的差別只在「怎麼把多個跨群配對的距離收成一個數」。"
        "兩邊都是單點時只有一個配對，取最大、最小、平均都是同一個數。"),
       (False, "complete 比較高，因為 complete linkage 的高度總是大於或等於 single",
        "這個直覺在<strong>一般情況</strong>下對（第 4 題的 (a) 小題就是這個答案），"
        "但這一題是<strong>單點對單點</strong>的特例，等號成立。"
        "考試最愛考這一格：把一般規則套到特例上就錯。"),
       (False, "資訊不足，要看資料才知道",
        "不對，這一題不需要任何資料。只要兩群都是單點，"
        "四種 linkage 給的高度必然都等於那兩點之間的距離。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP §12.6 第 5 題",
      "課本第 5 題：用圖 12.16 的三種尺度各跑一次 K = 2（襪子與電腦），"
      "分別預期看到什麼？",
      [(True, "原始次數 → 由襪子決定；標準化 → 變成「有買電腦 / 沒買電腦」；"
              "花費金額 → 由電腦決定",
        "對。三個答案剛好對應「變異數最大的那個變數主宰歐氏距離」這一件事。"
        "本頁 P09 的元件把三種尺度都跑給你看了。"),
       (False, "三種尺度會給同樣的分群，因為 K-means 對線性變換是不變的",
        "不對。K-means 對<strong>整體</strong>的旋轉平移不變，"
        "但對<strong>逐變數</strong>乘不同常數<em>不</em>不變——那會改變各變數在距離裡的權重。"
        "會不變的是線性迴歸的配適值，不是 K-means。"),
       (False, "標準化之後電腦的影響會消失，因為 0/1 變數標準化後變異數變成 1 太小",
        "方向剛好相反。標準化把兩個變數的變異數都設成 1，"
        "電腦是從「幾乎沒有影響」變成「影響力跟襪子相同」，不是消失。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP §12.6 第 8 題",
      "課本第 8 題要你在 USArrests 上用兩種方式算 PVE："
      "(a) 讀 <code>explained_variance_ratio_</code>；(b) 拿 <code>components_</code> "
      "直接套式 12.10。提示裡特別警告了什麼？",
      [(True, "兩邊必須用<strong>同一份</strong>資料：(a) 用標準化後的資料跑 PCA，"
              "(b) 就也得先標準化再套公式",
        "對。式 12.10 的分母是「資料的總平方和」，標準化與否會讓它完全不同。"
        "這一題的教學意義是：PVE 不是 PCA 物件的內建魔法，它就是 1 − RSS/TSS。"),
       (False, "警告 components_ 的符號可能跟公式的推導相反，要先把符號翻回來",
        "不用。式 12.10 裡負荷量是<strong>平方</strong>後才加總的，符號翻掉結果一樣。"
        "符號在別的地方會咬人（解讀方向、比較兩次分析），但不在這裡。"),
       (False, "警告要用 ddof=1 算變異數，否則兩邊差一個 n/(n−1) 的因子",
        "PVE 是比例，分子分母的 ddof 會約掉，所以不影響。"
        "真正的陷阱是兩邊<strong>用了不同的資料</strong>（一邊標準化、一邊沒有）。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>PCA 與分群：同樣在化簡，問的問題不同</h3>
{table(["", "PCA", "K-means", "階層式分群"],
       [["產出", "連續的低維座標（得分）", "K 個離散群標籤", "一棵樹（1 到 n 群都在裡面）"],
        ["要先決定", "M（留幾個主成分）", "K", "相異度、linkage、切在哪"],
        ["有隨機性嗎", "沒有（只差符號）", "<strong>有</strong>（初始指派）", "沒有"],
        ["結果唯一嗎", "唯一，最多差符號", "局部極小，換初值會變", "唯一（但畫法有 2ⁿ⁻¹ 種）"],
        ["要標準化嗎", "幾乎一定要", "幾乎一定要", "幾乎一定要"],
        ["對離群值", "會被拉走（變異最大化）", "強迫入群，會扭曲", "常自己掛高處，吃掉群額度"],
        ["常見用途", "視覺化、去雜訊、補值、當特徵", "市場區隔、量化子群", "探索階層結構、基因體學"]])}

  <h3>四種 linkage</h3>
{table(["Linkage", "群間相異度", "形狀", "反轉？", "建議"],
       [["Complete", "跨群距離的<strong>最大</strong>值", "平衡", "不會", "<strong>預設首選</strong>"],
        ["Average", "跨群距離的<strong>平均</strong>", "平衡", "不會", "<strong>預設首選</strong>"],
        ["Single", "跨群距離的<strong>最小</strong>值", "鏈狀拖尾", "不會", "少用，除非真的要找細長結構"],
        ["Centroid", "兩群<strong>形心</strong>的距離", "不定", "<strong>會</strong>", "基因體學常用，讀圖要小心"]])}

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["第一主成分",
         "$\\max \\frac1n\\sum_i(\\sum_j \\phi_{j1}x_{ij})^2$ s.t. $\\sum_j\\phi_{j1}^2=1$", "式 12.3"],
        ["得分", "$z_{im} = \\sum_{j=1}^{p} \\phi_{jm} x_{ij}$", "式 12.2、12.4"],
        ["最佳低維近似", "$\\min_{A,B}\\sum_{j}\\sum_i (x_{ij}-\\sum_m a_{im}b_{jm})^2$",
         "式 12.6，解就是主成分"],
        ["PVE",
         "$\\dfrac{\\sum_i z_{im}^2}{\\sum_j\\sum_i x_{ij}^2} = 1-\\dfrac{\\mathrm{RSS}}{\\mathrm{TSS}}$",
         "式 12.10，加起來是 1"],
        ["變異分解", "總變異 = 前 M 個 PC 的變異 + M 維近似的 MSE", "式 12.11"],
        ["矩陣補全", "$\\min_{A,B}\\sum_{(i,j)\\in\\mathcal O}(x_{ij}-\\sum_m a_{im}b_{jm})^2$",
         "式 12.12，只在觀測格上算"],
        ["K-means 目標",
         "$\\min\\sum_k \\frac{1}{|C_k|}\\sum_{i,i'\\in C_k}\\sum_j (x_{ij}-x_{i'j})^2$", "式 12.17"],
        ["關鍵恆等式",
         "$\\frac{1}{|C_k|}\\sum_{i,i'\\in C_k}\\sum_j (x_{ij}-x_{i'j})^2 = 2\\sum_{i\\in C_k}\\sum_j (x_{ij}-\\bar x_{kj})^2$",
         "式 12.18，演算法 12.2 的根據"]])}

  <h3>USArrests 的實測數字</h3>
{table(["主成分", "PC1", "PC2", "PC3", "PC4"],
       [["負荷量 Murder", "0.536", "−0.418", "−0.341", "−0.649"],
        ["負荷量 Assault", "0.583", "−0.188", "−0.268", "0.743"],
        ["負荷量 UrbanPop", "0.278", "0.873", "−0.378", "−0.134"],
        ["負荷量 Rape", "0.543", "0.167", "0.818", "−0.089"],
        ["得分的變異數", "2.5309", "1.0100", "0.3638", "0.1770"],
        ["PVE", "<strong>62.0%</strong>", "<strong>24.7%</strong>", "8.9%", "4.3%"],
        ["累積 PVE", "62.0%", "<strong>86.8%</strong>", "95.7%", "100%"]])}
  <p style="font-size:.82rem;color:var(--muted);">負荷量與 lab 儲存格 29 的
  <code>components_</code> 逐位相同、PVE 與儲存格 39 的
  <code>explained_variance_ratio_</code> 相同。四個變數的原始變異數是
  18.97 / 6945.17 / 209.52 / 87.73（儲存格 17）——所以標準化不是選項而是必要。</p>

{info("三個一定要記住的觀念", '''<strong>1. PCA 的兩種解釋是同一件事。</strong>
  「變異最大的方向」＝「離資料最近的低維平面」，式 12.11 就是它們的橋；
  PVE 因此也可以讀成近似的 R²。<br>
  <strong>2. 尺度會決定答案，符號不會。</strong>不標準化，PC1 就退化成變異數最大的那個變數；
  符號整組翻掉則什麼結論都不變（前提是得分與負荷量一起翻）。<br>
  <strong>3. 分群一定會給你群，但那不代表群是真的。</strong>
  K-means 只保證局部極小（要設 <code>n_init</code>）、樹狀圖只能看高度不能看左右、
  結果對標準化與 linkage 都很敏感。換設定多跑幾次，看什麼結構每次都出現。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== unsupervised_learning 本頁元件（id 與全域一律 w07 前綴）=====
   站內序號 07；ISLP 章號是 12（烘焙資料與 lab 引用都用 12）。 */

const w07CL = [HC.tok.a, HC.tok.b, HC.tok.c, HC.tok.held];   /* 群的顏色 */
const w07DEG = 180 / Math.PI;

/* stats.css 的 .axlab / .axtitle / .vlab 都寫死了 fill，class 規則會蓋掉
   presentation attribute，所以要換顏色一律走 inline style。
   同理，畫線與畫點時若要自訂顏色，class 一定要用沒有 CSS 規則的名字（w07ln / w07pt）。 */
function w07txt(s, px, py, str, o) {
  const a = o || {};
  const n = s.add('text', {
    x: px, y: py, 'text-anchor': a.anchor || 'start', class: a.cls || 'axlab',
    style: 'fill:' + (a.fill || 'var(--muted)') + (a.bold ? ';font-weight:700' : ''),
  }, a.g);
  n.textContent = str;
  return n;
}

/* ---------- P01 可旋轉的投影方向 ---------- */
const w07spinData = (() => {
  const rand = HC.stat.lcg(7071), xs = [], ys = [];
  const th = 0.55, ca = Math.cos(th), sa = Math.sin(th);
  for (let i = 0; i < 70; i++) {
    const a = HC.stat.normal(rand) * 2.05, b = HC.stat.normal(rand) * 0.78;
    xs.push(a * ca - b * sa); ys.push(a * sa + b * ca);
  }
  const mx = HC.stat.mean(xs), my = HC.stat.mean(ys);
  return { xs: xs.map(v => v - mx), ys: ys.map(v => v - my) };
})();
const w07spinMom = (() => {
  const { xs, ys } = w07spinData, n = xs.length;
  let sxx = 0, syy = 0, sxy = 0;
  for (let i = 0; i < n; i++) { sxx += xs[i] * xs[i]; syy += ys[i] * ys[i]; sxy += xs[i] * ys[i]; }
  const d = n - 1;
  sxx /= d; syy /= d; sxy /= d;
  /* 第一主成分的角度有封閉解，不必迭代 */
  let best = 0.5 * Math.atan2(2 * sxy, sxx - syy);
  if (best < 0) best += Math.PI;
  return { sxx, syy, sxy, total: sxx + syy, best };
})();
let w07spinAngle = 8 / w07DEG, w07spinSvc = null;

function w07spinVarAt(t) {
  const m = w07spinMom, c = Math.cos(t), s = Math.sin(t);
  return m.sxx * c * c + 2 * m.sxy * c * s + m.syy * s * s;
}
function w07spinSetup() {
  const { xs, ys } = w07spinData;
  const r = Math.max(...xs.map(Math.abs), ...ys.map(Math.abs)) * 1.18;
  w07spinSvc = HC.svg('w07spinSvg', { xd: [-r, r], yd: [-r, r], h: 360 });
  w07spinSvc.grid(6, 6, { xtitle: 'X₁（已置中）', ytitle: 'X₂（已置中）', xdec: 0, ydec: 0 });
}
function w07spinDraw() {
  const s = w07spinSvc, { xs, ys } = w07spinData;
  if (!s) return;
  const t = w07spinAngle, c = Math.cos(t), sn = Math.sin(t);
  const L = s.xd[1] * 1.4;
  const g = s.clearLayer('spin');
  /* 垂直方向（第二個方向）畫淡一點當參考 */
  s.poly([[-sn * L, c * L], [sn * L, -c * L]], { cls: 'gridl', sw: 1.4 }, g);
  s.poly([[-c * L, -sn * L], [c * L, sn * L]], { stroke: HC.tok.muted, sw: 2.4 }, g);
  for (let i = 0; i < xs.length; i++) {
    const p = xs[i] * c + ys[i] * sn;
    s.seg(xs[i], ys[i], p * c, p * sn, { cls: 'resid', sw: 1 }, g);
  }
  for (let i = 0; i < xs.length; i++) {
    const p = xs[i] * c + ys[i] * sn;
    s.dot(p * c, p * sn, { r: 3.4, fill: HC.tok.b, stroke: '#fff', sw: 0.8 }, g);
    s.dot(xs[i], ys[i], { r: 4, fill: HC.tok.a, stroke: '#fff', sw: 1 }, g);
  }
  /* 把手：拖它就轉方向 */
  const hx = c * s.xd[1] * 1.02, hy = sn * s.xd[1] * 1.02;
  const h = s.dot(hx, hy, { r: 9, fill: HC.tok.held, stroke: '#fff', sw: 2, cls: 'dot drag' }, g);
  HC.drag(h, s, ({ x, y }) => {
    let a = Math.atan2(y, x);
    if (a < 0) a += Math.PI;
    if (a >= Math.PI) a -= Math.PI;
    w07spinSet(a, true);
  });
  const v = w07spinVarAt(t), m = w07spinMom;
  const vmax = w07spinVarAt(m.best);
  const near = Math.abs(t - m.best) < 0.055;
  s.txtPx(52, 20, near ? '這就是第一主成分：投影後的變異數最大'
                       : '灰線是目前的投影方向，紅點是投影後的位置',
          { cls: 'axtitle', fill: near ? HC.tok.accent : HC.tok.accent2 }, g);
  $('w07spinAng').textContent = HC.fmt(t * w07DEG, 1) + '°';
  $('w07spinVar').textContent = HC.fmt(v, 3);
  $('w07spinPve').textContent = HC.pct(v / m.total, 1);
  $('w07spinMax').textContent = HC.fmt(vmax, 3);
  $('w07spinDir').textContent = HC.fmt(m.best * w07DEG, 1) + '°';
  setStatus('w07spinStatus', near
    ? '吸附到 ' + HC.fmt(m.best * w07DEG, 1) + '°：投影後的變異數 ' + HC.fmt(v, 3)
      + '，佔總變異 ' + HC.pct(v / m.total, 1)
      + '。<strong>這就是第一主成分</strong>——再轉一點點變異數就會變小。'
    : '角度 ' + HC.fmt(t * w07DEG, 1) + '°：投影後的變異數 ' + HC.fmt(v, 3)
      + '（最大是 ' + HC.fmt(vmax, 3) + '），佔總變異 ' + HC.pct(v / m.total, 1)
      + '。紫色虛線是每個點到投影軸的垂直距離。');
}
function w07spinSet(a, fromDrag) {
  const m = w07spinMom;
  if (Math.abs(a - m.best) < 0.035) a = m.best;      /* 吸附在最大變異處 */
  w07spinAngle = a;
  const deg = Math.round(a * w07DEG);
  if (!fromDrag || $('w07spinSlider').value !== String(deg)) $('w07spinSlider').value = String(deg);
  $('w07spinSliderVal').textContent = HC.fmt(a * w07DEG, 0) + '°';
  w07spinDraw();
}
function w07spinFromSlider() { w07spinSet(parseFloat($('w07spinSlider').value) / w07DEG); }
function w07spinSnap() { w07spinSet(w07spinMom.best); }
function w07spinReset() { w07spinSet(8 / w07DEG); }

/* ---------- P02 USArrests biplot（烘焙） ---------- */
let w07biOn = true, w07biSvc = null;
function w07biSetScaled(on) { w07biOn = on; w07biDraw(); }
function w07biToggle() { w07biSetScaled(!w07biOn); }
function w07biDraw() {
  const F = FRAMES_w07bi, D = w07biOn ? F.scaled : F.unscaled, lim = D.lim;
  const s = HC.svg('w07biSvg', { xd: [-lim, lim], yd: [-lim, lim], h: 400 });
  w07biSvc = s;
  const dec = lim > 20 ? 0 : 1;
  s.grid(6, 6, { xtitle: '第一主成分的得分', ytitle: '第二主成分的得分', xdec: dec, ydec: dec });
  const g = s.clearLayer('bi');
  s.poly([[-lim, 0], [lim, 0]], { cls: 'gridl', sw: 1.2 }, g);
  s.poly([[0, -lim], [0, lim]], { cls: 'gridl', sw: 1.2 }, g);
  const call = new Set(F.callout);
  D.scores.forEach((p, i) => {
    const hot = call.has(F.tags[i]);
    s.dot(p[0], p[1], { r: hot ? 4.6 : 3.2, fill: hot ? HC.tok.a : 'rgba(44,62,122,.42)',
                        stroke: '#fff', sw: hot ? 1.4 : 0.6 }, g);
    if (hot) s.txt(p[0], p[1], F.tags[i], { dy: -9, cls: 'vlab', fill: HC.tok.accent2 }, g);
  });
  D.load.forEach((l, j) => {
    const ax = l[0] * D.arrow, ay = l[1] * D.arrow;
    s.seg(0, 0, ax, ay, { stroke: HC.tok.accent, sw: 2.2, dash: null }, g);
    /* 箭頭：在 px 座標上算一個小三角形 */
    const x2 = s.X(ax), y2 = s.Y(ay), x1 = s.X(0), y1 = s.Y(0);
    const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len, w = 4.2, h = 10;
    s.add('polygon', { points: [x2 + ',' + y2,
                                (x2 - h * ux + w * uy) + ',' + (y2 - h * uy - w * ux),
                                (x2 - h * ux - w * uy) + ',' + (y2 - h * uy + w * ux)].join(' '),
                       fill: HC.tok.accent }, g);
    s.txtPx(x2 + (ux > 0 ? 6 : -6), y2 + (uy > 0 ? 15 : -7), F.cols[j],
            { cls: 'vlab', fill: HC.tok.accent, anchor: ux > 0 ? 'start' : 'end' }, g);
  });
  for (let j = 0; j < 4; j++) {
    $('w07biL' + j).textContent = HC.fmt(D.load[j][0], 3) + ' / ' + HC.fmt(D.load[j][1], 3);
  }
  $('w07biPve').textContent = HC.pct(D.pve[0], 1);
  setStatus('w07biStatus', w07biOn
    ? '標準化後（＝ISLP 圖 12.1 與圖 12.4 左）：PC1 由 Murder／Assault／Rape 三個變數'
      + '差不多平均分擔，UrbanPop 幾乎只出現在 PC2。PC1 解釋 ' + HC.pct(D.pve[0], 1) + '。'
    : '未標準化（＝ISLP 圖 12.4 右）：Assault 的負荷量 ' + HC.fmt(D.load[1][0], 3)
      + '，PC1 幾乎就是 Assault 自己，解釋了 ' + HC.pct(D.pve[0], 1)
      + '——其他三個變數等於沒參與。注意座標軸的範圍也從 ±3 變成 ±' + HC.fmt(D.lim, 0) + '。');
}

/* ---------- P04 scree plot 與累積 PVE（烘焙） ---------- */
let w07screeCum = true;
function w07screeToggleCum() { w07screeCum = !w07screeCum; w07screeDraw(); }
function w07screeSet() {
  $('w07screeVal').textContent = $('w07screeSlider').value;
  w07screeDraw();
}
function w07screeDraw() {
  const F = FRAMES_w07pve, M = parseInt($('w07screeSlider').value, 10);
  const ticks = F.pve.map((_, i) => i + 1);
  const sets = [{ label: '每個主成分的 PVE', data: F.pve, borderColor: HC.tok.accent2,
                  backgroundColor: HC.tok.accent2, borderWidth: 2.8, pointRadius: 4, fill: false }];
  if (w07screeCum) {
    sets.push({ label: '累積 PVE', data: F.cum, borderColor: HC.tok.accent3,
                backgroundColor: HC.tok.accent3, borderWidth: 2.4, pointRadius: 4,
                borderDash: [6, 4], fill: false });
  }
  HC.line('w07screeChart', { labels: ticks, datasets: sets }, {
    scales: { x: { title: { display: true, text: '第幾個主成分' } },
              y: { min: 0, max: 1.02, title: { display: true, text: '解釋的變異比例' } } },
  });
  const c = HC.get('w07screeChart');
  if (c) { c.config.plugins = [HC.vline(M - 1, '留 M = ' + M)]; c.update('none'); }
  const keep = F.cum[M - 1];
  $('w07screeM').textContent = String(M);
  $('w07screeKeep').textContent = HC.pct(keep, 1);
  $('w07screeLost').textContent = HC.pct(1 - keep, 1);
  $('w07screeRss').textContent = HC.fmt(1 - keep, 4);
  $('w07screeCost').textContent = (F.n * M + F.p * M) + ' 個（原本 ' + (F.n * F.p) + ' 個）';
  setStatus('w07screeStatus', '留 M = ' + M + ' 個主成分：留住總變異的 '
    + HC.pct(keep, 1) + '，丟掉 ' + HC.pct(1 - keep, 1)
    + '。換句話說，用 ' + M + ' 維去近似這個 ' + F.n + '×' + F.p + ' 的矩陣，R² = '
    + HC.fmt(keep, 3) + '。');
}

/* ---------- P06 矩陣補全：即時跑演算法 12.1 ---------- */
const w07mcN = 50, w07mcP = 4;
let w07mcSeed = 1215, w07mcMissN = 20;
let w07mcMask = null, w07mcHat = null, w07mcApp = null;
let w07mcIterN = 0, w07mcHist = [], w07mcMss0 = 1, w07mcMssOld = 1, w07mcRel = 1;
let w07mcSvc = null, w07mcTimer = null, w07mcGen = 0;

function w07mcMakeMask() {
  const rand = HC.stat.lcg(w07mcSeed);
  const rows = [...Array(w07mcN).keys()];
  for (let i = rows.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1)); [rows[i], rows[j]] = [rows[j], rows[i]];
  }
  const mask = Array.from({ length: w07mcN }, () => new Array(w07mcP).fill(false));
  for (let k = 0; k < w07mcMissN; k++) mask[rows[k]][Math.floor(rand() * w07mcP)] = true;
  return mask;
}
function w07mcRank1(A) {
  /* 最佳秩一近似：對 AᵀA 做冪迭代求最大右奇異向量，再算 (A v) vᵀ */
  let v = new Array(w07mcP).fill(1 / Math.sqrt(w07mcP));
  const G = Array.from({ length: w07mcP }, () => new Array(w07mcP).fill(0));
  for (let j = 0; j < w07mcP; j++) {
    for (let k = j; k < w07mcP; k++) {
      let s = 0;
      for (let i = 0; i < w07mcN; i++) s += A[i][j] * A[i][k];
      G[j][k] = s; G[k][j] = s;
    }
  }
  for (let it = 0; it < 90; it++) {
    const w = new Array(w07mcP).fill(0);
    for (let j = 0; j < w07mcP; j++) for (let k = 0; k < w07mcP; k++) w[j] += G[j][k] * v[k];
    const nrm = Math.hypot(...w) || 1;
    v = w.map(x => x / nrm);
  }
  const out = [];
  for (let i = 0; i < w07mcN; i++) {
    let u = 0;
    for (let j = 0; j < w07mcP; j++) u += A[i][j] * v[j];
    out.push(v.map(vj => u * vj));
  }
  return out;
}
function w07mcInit() {
  const X = FRAMES_w07mc.X;
  w07mcMask = w07mcMakeMask();
  w07mcHat = X.map(r => r.slice());
  for (let j = 0; j < w07mcP; j++) {
    let s = 0, c = 0;
    for (let i = 0; i < w07mcN; i++) if (!w07mcMask[i][j]) { s += X[i][j]; c++; }
    const bar = c ? s / c : 0;
    for (let i = 0; i < w07mcN; i++) if (w07mcMask[i][j]) w07mcHat[i][j] = bar;
  }
  let s0 = 0, c0 = 0;
  for (let i = 0; i < w07mcN; i++) {
    for (let j = 0; j < w07mcP; j++) if (!w07mcMask[i][j]) { s0 += X[i][j] * X[i][j]; c0++; }
  }
  w07mcMss0 = s0 / c0; w07mcMssOld = w07mcMss0; w07mcRel = 1;
  w07mcApp = null; w07mcIterN = 0; w07mcHist = [];
}
function w07mcStep() {
  if (w07mcIterN >= 40) return false;
  const X = FRAMES_w07mc.X;
  const app = w07mcRank1(w07mcHat);
  for (let i = 0; i < w07mcN; i++) {
    for (let j = 0; j < w07mcP; j++) if (w07mcMask[i][j]) w07mcHat[i][j] = app[i][j];
  }
  let s = 0, c = 0;
  for (let i = 0; i < w07mcN; i++) {
    for (let j = 0; j < w07mcP; j++) {
      if (!w07mcMask[i][j]) { const d = X[i][j] - app[i][j]; s += d * d; c++; }
    }
  }
  const mss = s / c;
  w07mcRel = (w07mcMssOld - mss) / w07mcMss0;
  w07mcMssOld = mss; w07mcApp = app; w07mcIterN += 1;
  w07mcHist.push(mss);
  w07mcRender(); w07mcChart();
  return w07mcRel > 1e-7;
}
function w07mcRun() {
  const gen = ++w07mcGen;
  if (w07mcTimer) clearTimeout(w07mcTimer);
  const tick = () => {
    if (gen !== w07mcGen) return;
    if (w07mcStep()) w07mcTimer = setTimeout(tick, 420);
    else w07mcTimer = null;
  };
  tick();
}
function w07mcCorr() {
  if (!w07mcApp) return NaN;
  const X = FRAMES_w07mc.X, a = [], b = [];
  for (let i = 0; i < w07mcN; i++) {
    for (let j = 0; j < w07mcP; j++) if (w07mcMask[i][j]) { a.push(w07mcApp[i][j]); b.push(X[i][j]); }
  }
  if (a.length < 3) return NaN;
  const ma = HC.stat.mean(a), mb = HC.stat.mean(b);
  let sab = 0, saa = 0, sbb = 0;
  for (let k = 0; k < a.length; k++) {
    sab += (a[k] - ma) * (b[k] - mb); saa += (a[k] - ma) ** 2; sbb += (b[k] - mb) ** 2;
  }
  return sab / Math.sqrt(saa * sbb);
}
function w07mcShade(v) {
  const t = Math.max(-1, Math.min(1, v / 2.4));
  return t >= 0 ? 'rgba(192,57,43,' + (0.14 + 0.72 * t).toFixed(3) + ')'
                : 'rgba(44,62,122,' + (0.14 + 0.72 * -t).toFixed(3) + ')';
}
function w07mcRender() {
  const F = FRAMES_w07mc, s = w07mcSvc;
  if (!s) return;
  const g = s.clearLayer('grid2');
  const x0 = 52, cw = (606 - x0) / w07mcN, rh = 17, y0 = 44;
  s.txtPx(x0, 20, '標準化後的 USArrests：每一欄一個州（字母序），四列是四個變數',
          { cls: 'axtitle' }, g);
  const short = ['Mur', 'Ass', 'Urb', 'Rap'];
  for (let j = 0; j < w07mcP; j++) {
    s.txtPx(x0 - 6, y0 + j * rh + 12, short[j], { cls: 'axlab', anchor: 'end' }, g);
    for (let i = 0; i < w07mcN; i++) {
      const miss = w07mcMask[i][j], filled = miss && w07mcApp;
      s.add('rect', { x: x0 + i * cw, y: y0 + j * rh, width: cw - 0.7, height: rh - 1.6, rx: 1.6,
                      fill: miss ? (filled ? w07mcShade(w07mcHat[i][j]) : '#fff')
                                 : w07mcShade(F.X[i][j]),
                      stroke: miss ? (filled ? HC.tok.held : HC.tok.muted) : 'none',
                      'stroke-width': miss ? 1.5 : 0,
                      'stroke-dasharray': miss && !filled ? '2 1.6' : '' }, g);
    }
  }
  const ly = y0 + w07mcP * rh + 22;
  const chip = (px, fill, stroke, dash, label) => {
    s.add('rect', { x: px, y: ly - 9, width: 13, height: 11, rx: 2, fill: fill,
                    stroke: stroke, 'stroke-width': stroke ? 1.5 : 0,
                    'stroke-dasharray': dash || '' }, g);
    s.txtPx(px + 18, ly, label, { cls: 'axlab' }, g);
  };
  chip(x0, w07mcShade(1.6), null, null, '觀測值（紅高藍低）');
  chip(x0 + 168, '#fff', HC.tok.muted, '2 1.6', '被挖掉');
  chip(x0 + 268, w07mcShade(1.1), HC.tok.held, null, '已補值');
  $('w07mcMiss').textContent = w07mcMissN + ' / ' + (w07mcN * w07mcP)
    + '（' + HC.pct(w07mcMissN / (w07mcN * w07mcP), 0) + '）';
  $('w07mcIter').textContent = String(w07mcIterN);
  $('w07mcMss').textContent = w07mcHist.length ? HC.fmt(w07mcHist[w07mcHist.length - 1], 4) : '—';
  $('w07mcRel').textContent = w07mcIterN ? w07mcRel.toExponential(2) : '—';
  const r = w07mcCorr();
  $('w07mcCorr').textContent = Number.isNaN(r) ? '—' : HC.fmt(r, 4);
  setStatus('w07mcStatus', w07mcIterN === 0
    ? '起點（步驟 1）：' + w07mcMissN + ' 個格子被挖掉，先用該欄觀測值的平均填進去。'
      + '按「單步」開始迭代。'
    : '第 ' + w07mcIterN + ' 輪：觀測格上的 MSS = '
      + HC.fmt(w07mcHist[w07mcHist.length - 1], 4) + '，相對改善 ' + w07mcRel.toExponential(2)
      + '。橘框裡是補出來的值，跟真值的相關係數 ' + HC.fmt(r, 3)
      + '（相對改善跌破 1e−7 就算收斂）。');
}
function w07mcChart() {
  HC.line('w07mcChart', {
    labels: w07mcHist.map((_, i) => i + 1),
    datasets: [{ label: '觀測格上的 MSS', data: w07mcHist, borderColor: HC.tok.accent,
                 backgroundColor: HC.tok.accent, borderWidth: 2.6, pointRadius: 3.5, fill: false }],
  }, {
    scales: { x: { title: { display: true, text: '第幾輪迭代' } },
              y: { title: { display: true, text: '觀測格上的均方誤差' } } },
  });
}
function w07mcReset() {
  w07mcGen += 1;
  if (w07mcTimer) { clearTimeout(w07mcTimer); w07mcTimer = null; }
  if (!w07mcSvc) w07mcSvc = HC.svg('w07mcSvg', { h: 190 });
  w07mcInit(); w07mcRender(); w07mcChart();
}
function w07mcReseed() { w07mcSeed = (w07mcSeed * 31 + 17) % 99991; w07mcReset(); }
function w07mcSetMiss() {
  w07mcMissN = parseInt($('w07mcSlider').value, 10);
  $('w07mcSliderVal').textContent = String(w07mcMissN);
  w07mcReset();
}

/* ---------- P07 K-means 逐步器 ---------- */
const w07kmPts = (() => {
  const rand = HC.stat.lcg(1204), cen = [[-2.4, 2.1], [2.3, 1.6], [-0.2, -2.3]];
  const xs = [], ys = [];
  for (let k = 0; k < 3; k++) {
    for (let i = 0; i < 24; i++) {
      xs.push(cen[k][0] + HC.stat.normal(rand) * 1.02);
      ys.push(cen[k][1] + HC.stat.normal(rand) * 1.02);
    }
  }
  return { xs, ys, n: xs.length };
})();
let w07kmK = 3, w07kmSeed = 5, w07kmLab = null, w07kmCen = null;
let w07kmPhase = 'init', w07kmSteps = 0, w07kmHist = [], w07kmMoved = 0, w07kmDone = false;
let w07kmSvc = null, w07kmTimer = null, w07kmGen = 0, w07kmFinals = [];

function w07kmWssNow() {
  if (!w07kmCen) return NaN;
  let s = 0;
  for (let i = 0; i < w07kmPts.n; i++) {
    const c = w07kmCen[w07kmLab[i]];
    s += (w07kmPts.xs[i] - c[0]) ** 2 + (w07kmPts.ys[i] - c[1]) ** 2;
  }
  return s;
}
function w07kmCenters() {
  const sum = Array.from({ length: w07kmK }, () => [0, 0, 0]);
  for (let i = 0; i < w07kmPts.n; i++) {
    const k = w07kmLab[i];
    sum[k][0] += w07kmPts.xs[i]; sum[k][1] += w07kmPts.ys[i]; sum[k][2] += 1;
  }
  return sum.map((s, k) => (s[2] ? [s[0] / s[2], s[1] / s[2]]
                                 : (w07kmCen ? w07kmCen[k] : [0, 0])));
}
function w07kmAssign() {
  let moved = 0;
  for (let i = 0; i < w07kmPts.n; i++) {
    let bk = 0, bd = Infinity;
    for (let k = 0; k < w07kmK; k++) {
      const d = (w07kmPts.xs[i] - w07kmCen[k][0]) ** 2 + (w07kmPts.ys[i] - w07kmCen[k][1]) ** 2;
      if (d < bd) { bd = d; bk = k; }
    }
    if (bk !== w07kmLab[i]) { w07kmLab[i] = bk; moved += 1; }
  }
  return moved;
}
function w07kmStep() {
  if (w07kmDone) return false;
  if (w07kmPhase === 'assign' || w07kmPhase === 'init') {
    w07kmCen = w07kmCenters(); w07kmPhase = 'update';
  } else {
    w07kmMoved = w07kmAssign(); w07kmPhase = 'assign';
    if (w07kmMoved === 0) {
      w07kmDone = true;
      const w = w07kmWssNow();
      w07kmFinals.push(w);
    }
  }
  w07kmSteps += 1;
  w07kmHist.push(w07kmWssNow());
  w07kmRender();
  return !w07kmDone;
}
function w07kmRun() {
  const gen = ++w07kmGen;
  if (w07kmTimer) clearTimeout(w07kmTimer);
  const tick = () => {
    if (gen !== w07kmGen) return;
    if (w07kmStep() && w07kmSteps < 40) w07kmTimer = setTimeout(tick, 420);
    else w07kmTimer = null;
  };
  tick();
}
function w07kmSetup() {
  const { xs, ys } = w07kmPts;
  const pad = 1.0;
  w07kmSvc = HC.svg('w07kmSvg', {
    xd: [Math.min(...xs) - pad, Math.max(...xs) + pad],
    yd: [Math.min(...ys) - pad, Math.max(...ys) + pad], h: 330,
    pad: { l: 34, r: 268, t: 26, b: 32 },
  });
  w07kmSvc.grid(4, 4, { xdec: 0, ydec: 0 });
}
function w07kmRender() {
  const s = w07kmSvc;
  if (!s) return;
  const g = s.clearLayer('km');
  s.txtPx(34, 18, 'K = ' + w07kmK + '，第 ' + w07kmSteps + ' 步'
    + (w07kmDone ? '（已收斂）' : ''), { cls: 'axtitle' }, g);
  for (let i = 0; i < w07kmPts.n; i++) {
    s.dot(w07kmPts.xs[i], w07kmPts.ys[i],
          { r: 4, fill: w07CL[w07kmLab[i] % 4], stroke: '#fff', sw: 1 }, g);
  }
  if (w07kmCen) {
    w07kmCen.forEach((c, k) => {
      s.dot(c[0], c[1], { r: 9.5, fill: w07CL[k % 4], stroke: '#1a1a2e', sw: 2.6 }, g);
      s.dot(c[0], c[1], { r: 3, fill: '#fff' }, g);
    });
  }
  /* 右邊：群內平方和隨步數的曲線（同一個 SVG，用 px 座標自己畫） */
  const bx0 = 396, bx1 = 604, by0 = 44, by1 = 276;
  s.add('rect', { x: bx0, y: by0, width: bx1 - bx0, height: by1 - by0, rx: 6,
                  fill: '#fff', stroke: HC.tok.cardBorder }, g);
  s.txtPx(bx0, by0 - 8, '群內平方和（只會往下）', { cls: 'axtitle' }, g);
  const hs = w07kmHist.filter(v => Number.isFinite(v));
  if (hs.length) {
    const hi = Math.max(...hs) * 1.06, lo = 0;
    const px = i => bx0 + 14 + (bx1 - bx0 - 26) * (hs.length < 2 ? 0 : i / (hs.length - 1));
    const py = v => by1 - 18 - (by1 - by0 - 30) * (v - lo) / (hi - lo || 1);
    s.add('polyline', { points: hs.map((v, i) => px(i) + ',' + py(v)).join(' '),
                        fill: 'none', stroke: HC.tok.accent, 'stroke-width': 2.4 }, g);
    hs.forEach((v, i) => s.add('circle', { cx: px(i), cy: py(v), r: 3.2,
                                           fill: HC.tok.accent, stroke: '#fff',
                                           'stroke-width': 1 }, g));
    s.txtPx(bx0 + 12, by1 - 4, '步數 1 … ' + hs.length, { cls: 'axlab' }, g);
    s.txtPx(bx1 - 12, by0 + 14, HC.fmt(hs[hs.length - 1], 1),
            { cls: 'axlab', anchor: 'end', fill: HC.tok.accent }, g);
  } else {
    s.txtPx(bx0 + 14, (by0 + by1) / 2, '按「單步」開始', { cls: 'axlab' }, g);
  }
  hlLine('w07kmCode', w07kmSteps === 0 ? 1 : (w07kmDone ? 5 : (w07kmPhase === 'update' ? 3 : 4)));
  const phase = w07kmSteps === 0 ? '隨機指派（步驟 1）'
    : (w07kmPhase === 'update' ? '2(a) 算群心' : '2(b) 重新指派');
  $('w07kmK').textContent = String(w07kmK);
  $('w07kmStepN').textContent = w07kmSteps === 0 ? '—' : String(w07kmSteps);
  $('w07kmPhase').textContent = w07kmDone ? '已收斂' : phase;
  $('w07kmWss').textContent = w07kmHist.length
    ? HC.fmt(w07kmHist[w07kmHist.length - 1], 2) : '—';
  $('w07kmMoved').textContent = w07kmSteps === 0 || w07kmPhase === 'update'
    ? '—' : String(w07kmMoved);
  $('w07kmTried').textContent = String(w07kmFinals.length);
  $('w07kmBest').textContent = w07kmFinals.length ? HC.fmt(Math.min(...w07kmFinals), 2) : '—';
  $('w07kmWorst').textContent = w07kmFinals.length ? HC.fmt(Math.max(...w07kmFinals), 2) : '—';
  setStatus('w07kmStatus', w07kmSteps === 0
    ? 'K = ' + w07kmK + '，' + w07kmPts.n + ' 個點剛剛被隨機指派（種子 ' + w07kmSeed
      + '）。按「單步」交替執行「算群心」與「重新指派」。'
    : (w07kmDone
      ? '第 ' + w07kmSteps + ' 步：沒有任何點換群，收斂。群內平方和 '
        + HC.fmt(w07kmHist[w07kmHist.length - 1], 2)
        + '。按「換初始值」再跑一次，看它會不會停在別的地方。'
      : '第 ' + w07kmSteps + ' 步 · ' + phase + '：群內平方和 '
        + HC.fmt(w07kmHist[w07kmHist.length - 1], 2)
        + (w07kmPhase === 'assign' ? '，這一步有 ' + w07kmMoved + ' 個點換了群。'
                                   : '，群心移到了各群的平均位置。')));
}
function w07kmReset() {
  w07kmGen += 1;
  if (w07kmTimer) { clearTimeout(w07kmTimer); w07kmTimer = null; }
  const rand = HC.stat.lcg(w07kmSeed);
  w07kmLab = [];
  for (let i = 0; i < w07kmPts.n; i++) w07kmLab.push(Math.floor(rand() * w07kmK));
  /* 保證每一群至少有一點，否則群心會是空的 */
  for (let k = 0; k < w07kmK; k++) if (!w07kmLab.includes(k)) w07kmLab[k] = k;
  w07kmCen = null; w07kmPhase = 'init'; w07kmSteps = 0; w07kmHist = [];
  w07kmMoved = 0; w07kmDone = false;
  w07kmRender();
}
function w07kmReseed() { w07kmSeed = (w07kmSeed * 41 + 7) % 9973; w07kmReset(); }
function w07kmSetK() {
  w07kmK = parseInt($('w07kmSel').value, 10);
  w07kmFinals = [];
  w07kmReset();
}

/* ---------- P08 Dendrogram + 可拖切線（烘焙） ---------- */
let w07dLk = 'complete', w07dCut = 0.55, w07dS1 = null, w07dS2 = null, w07dReady = false;
function w07dTree() { return FRAMES_w07dendro.trees[w07dLk]; }
function w07dLabels(h) {
  const T = w07dTree(), n = FRAMES_w07dendro.n, Z = T.Z;
  const par = [...Array(2 * n - 1).keys()];
  const find = x => { while (par[x] !== x) { par[x] = par[par[x]]; x = par[x]; } return x; };
  for (let i = 0; i < Z.length; i++) {
    if (Z[i][2] <= h) { par[find(Z[i][0])] = n + i; par[find(Z[i][1])] = n + i; }
  }
  const map = new Map(), lab = new Array(n);
  T.order.forEach(leaf => {                      /* 依葉子的左右順序給編號，顏色才穩定 */
    const r = find(leaf);
    if (!map.has(r)) map.set(r, map.size);
    lab[leaf] = map.get(r);
  });
  return { lab, k: map.size, find };
}
function w07dLayout() {
  const T = w07dTree(), n = FRAMES_w07dendro.n, Z = T.Z;
  const pos = new Array(2 * n - 1).fill(0), hgt = new Array(2 * n - 1).fill(0);
  T.order.forEach((leaf, i) => { pos[leaf] = i; });
  for (let i = 0; i < Z.length; i++) {
    pos[n + i] = (pos[Z[i][0]] + pos[Z[i][1]]) / 2;
    hgt[n + i] = Z[i][2];
  }
  return { pos, hgt };
}
function w07dSetup() {
  const P = FRAMES_w07dendro.pts;
  const xs = P.map(p => p[0]), ys = P.map(p => p[1]);
  const pad = 0.9;
  w07dS1 = HC.svg('w07dendroSvg', {
    xd: [Math.min(...xs) - pad, Math.max(...xs) + pad],
    yd: [Math.min(...ys) - pad, Math.max(...ys) + pad], h: 350,
    pad: { l: 30, r: 340, t: 30, b: 34 },
  });
  w07dS1.grid(4, 4, { xdec: 0, ydec: 0 });
  w07dReady = true;
}
function w07dRescale() {
  const T = w07dTree(), n = FRAMES_w07dendro.n;
  w07dS2 = HC.svg('w07dendroSvg', {
    xd: [-0.8, n - 0.2], yd: [0, T.hmax * 1.1], h: 350,
    pad: { l: 322, r: 16, t: 30, b: 34 },
  });
  return w07dS2;
}
function w07dDraw() {
  if (!w07dReady) return;
  const F = FRAMES_w07dendro, n = F.n, T = w07dTree();
  const s2 = w07dRescale();
  const h = w07dCut * T.hmax * 1.1;
  const { lab, k, find } = w07dLabels(h);
  const { pos, hgt } = w07dLayout();
  /* 左：散佈圖，顏色跟著切線 */
  const g1 = w07dS1.clearLayer('pts');
  w07dS1.txtPx(30, 20, '左：資料（顏色 = 這一刀切出的群）', { cls: 'axtitle' }, g1);
  F.pts.forEach((p, i) => w07dS1.dot(p[0], p[1],
    { r: 5, fill: w07CL[lab[i] % 4], stroke: '#fff', sw: 1.2 }, g1));
  /* 右：樹 */
  const g2 = s2.clearLayer('tree');
  s2.txtPx(322, 20, '右：' + w07dLk + ' linkage 的樹狀圖', { cls: 'axtitle' }, g2);
  for (let t = 0; t <= 4; t++) {
    const v = T.hmax * 1.1 * t / 4;
    s2.add('line', { cls: 'gridl', x1: s2.X(s2.xd[0]), y1: s2.Y(v),
                     x2: s2.X(s2.xd[1]), y2: s2.Y(v) }, g2);
    s2.txtPx(s2.pad.l - 5, s2.Y(v) + 3.5, HC.fmt(v, 1),
             { cls: 'axlab', anchor: 'end' }, g2);
  }
  s2.txtPx((s2.pad.l + s2.W - s2.pad.r) / 2, s2.H - 6, '合併高度（縱軸）· 30 個葉子',
           { cls: 'axtitle', anchor: 'middle' }, g2);
  const colOf = node => {
    if (node < n) return w07CL[lab[node] % 4];
    const i = node - n;
    return T.Z[i][2] <= h ? w07CL[lab[find(node) === find(T.Z[i][0]) ? T.Z[i][0] : T.Z[i][0]] % 4]
                          : '#333';
  };
  for (let i = 0; i < T.Z.length; i++) {
    const a = T.Z[i][0], b = T.Z[i][1], y = T.Z[i][2];
    const col = y <= h ? w07CL[lab[a < n ? a : T.Z[a - n][0] < n ? T.Z[a - n][0] : a - n] % 4]
                       : '#333';
    const cc = y <= h ? colOf(a) : '#333';
    const sw = y <= h ? 1.8 : 1.5;
    s2.poly([[pos[a], hgt[a]], [pos[a], y], [pos[b], y], [pos[b], hgt[b]]],
            { stroke: cc || col, sw: sw, cls: 'fit' }, g2);
  }
  /* 切線（可拖） */
  const gc = s2.clearLayer('cut');
  s2.poly([[s2.xd[0], h], [s2.xd[1], h]],
          { stroke: HC.tok.held, sw: 2.6, dash: '7 4' }, gc);
  s2.dot(s2.xd[1], h, { r: 7.5, fill: HC.tok.held, stroke: '#fff', sw: 2, cls: 'dot drag' }, gc);
  s2.txtPx(s2.pad.l + 6, s2.Y(h) - 6, '切在 ' + HC.fmt(h, 2) + ' → ' + k + ' 群',
           { cls: 'axlab', fill: HC.tok.accent }, gc);
  let chain = 0;
  for (let i = 0; i < T.Z.length; i++) {
    if ((T.Z[i][0] < n) !== (T.Z[i][1] < n)) chain += 1;
  }
  $('w07dendroLk').textContent = w07dLk;
  $('w07dendroH').textContent = HC.fmt(h, 2);
  $('w07dendroK').textContent = String(k);
  $('w07dendroMax').textContent = HC.fmt(T.hmax, 2);
  $('w07dendroChain').textContent = chain + ' / ' + (n - 1);
  const sizes = {};
  lab.forEach(v => { sizes[v] = (sizes[v] || 0) + 1; });
  const arr = Object.values(sizes).sort((x, y) => y - x);
  setStatus('w07dendroStatus', w07dLk + ' linkage：切在高度 ' + HC.fmt(h, 2)
    + ' 得到 ' + k + ' 群，各群大小 ' + arr.join(' / ')
    + '。整棵樹有 ' + chain + ' 次合併是「大群黏上一顆單點」'
    + (w07dLk === 'single' ? '——鏈狀效應就是這樣長出來的。'
                           : '（把 linkage 換成 single 看這個數字怎麼變）。'));
}
function w07dInstallDrag() {
  const s2 = w07dRescale();
  const g = s2.layer('hit');
  if (g.childElementCount) return;
  const rect = s2.add('rect', {
    x: s2.pad.l, y: s2.pad.t, width: s2.W - s2.pad.l - s2.pad.r, height: s2.ih,
    fill: 'transparent', style: 'cursor:ns-resize',
  }, g);
  HC.drag(rect, s2, ({ y }) => {
    const T = w07dTree();
    w07dCut = Math.max(0.02, Math.min(0.98, y / (T.hmax * 1.1)));
    $('w07dendroSlider').value = String(Math.round(w07dCut * 100));
    w07dDraw();
  });
}
function w07dendroFromSlider() {
  w07dCut = parseFloat($('w07dendroSlider').value) / 100;
  w07dDraw();
}
function w07dendroSetLk() {
  w07dLk = $('w07dendroSel').value;
  w07dDraw();
}
function w07dendroReset() {
  w07dLk = 'complete'; w07dCut = 0.55;
  $('w07dendroSel').value = 'complete';
  $('w07dendroSlider').value = '55';
  w07dDraw();
}

/* ---------- P09 分群的實務決策（襪子與電腦） ---------- */
const w07practModes = { raw: '原始次數', scaled: '標準化', dollar: '花費金額' };
let w07practMode = 'raw', w07practOut = false, w07practSvc = null;
function w07practMat() {
  const F = FRAMES_w07shop;
  let a = F.socks.slice(), b = F.comp.slice();
  if (w07practOut) { a = a.concat([60]); b = b.concat([0]); }
  if (w07practMode === 'dollar') {
    a = a.map(v => v * F.priceSock); b = b.map(v => v * F.priceComp);
  } else if (w07practMode === 'scaled') {
    const za = HC.stat.sd(a) || 1, zb = HC.stat.sd(b) || 1;
    const ma = HC.stat.mean(a), mb = HC.stat.mean(b);
    a = a.map(v => (v - ma) / za); b = b.map(v => (v - mb) / zb);
  }
  return { a, b, n: a.length };
}
function w07practKm(M) {
  let best = null;
  for (let t = 0; t < 24; t++) {
    const rand = HC.stat.lcg(9001 + t * 131);
    let lab = [];
    for (let i = 0; i < M.n; i++) lab.push(Math.floor(rand() * 2));
    if (!lab.includes(0)) lab[0] = 0;
    if (!lab.includes(1)) lab[1] = 1;
    let cen = null;
    for (let it = 0; it < 30; it++) {
      cen = [[0, 0, 0], [0, 0, 0]];
      for (let i = 0; i < M.n; i++) {
        cen[lab[i]][0] += M.a[i]; cen[lab[i]][1] += M.b[i]; cen[lab[i]][2] += 1;
      }
      cen = cen.map(c => (c[2] ? [c[0] / c[2], c[1] / c[2]] : [NaN, NaN]));
      let moved = 0;
      for (let i = 0; i < M.n; i++) {
        const d0 = (M.a[i] - cen[0][0]) ** 2 + (M.b[i] - cen[0][1]) ** 2;
        const d1 = (M.a[i] - cen[1][0]) ** 2 + (M.b[i] - cen[1][1]) ** 2;
        const k = d0 <= d1 ? 0 : 1;
        if (k !== lab[i]) { lab[i] = k; moved += 1; }
      }
      if (!moved) break;
    }
    let w = 0;
    for (let i = 0; i < M.n; i++) {
      w += (M.a[i] - cen[lab[i]][0]) ** 2 + (M.b[i] - cen[lab[i]][1]) ** 2;
    }
    if (!best || w < best.w) best = { lab: lab.slice(), cen: cen, w: w };
  }
  return best;
}
function w07practDraw() {
  const F = FRAMES_w07shop, M = w07practMat(), R = w07practKm(M);
  const lim = Math.max(...M.a.map(Math.abs), ...M.b.map(Math.abs), 0.1);
  const lo = Math.min(0, ...M.a, ...M.b);
  const s = HC.svg('w07practSvg', { xd: [lo - lim * 0.08, lim * 1.12],
                                    yd: [lo - lim * 0.08, lim * 1.12], h: 340,
                                    pad: { l: 44, r: 250, t: 28, b: 36 } });
  w07practSvc = s;
  const dec = lim > 20 ? 0 : 1;
  s.grid(4, 4, { xtitle: '襪子（' + w07practModes[w07practMode] + '）',
                 ytitle: '電腦', xdec: dec, ydec: dec });
  const g = s.clearLayer('pt');
  s.txtPx(44, 18, '左：八位顧客在這個尺度下的位置（顏色 = K = 2 的群）', { cls: 'axtitle' }, g);
  for (let i = 0; i < M.n; i++) {
    const isOut = w07practOut && i === M.n - 1;
    s.dot(M.a[i], M.b[i], { r: isOut ? 7.5 : 5.5, fill: w07CL[R.lab[i]],
                            stroke: isOut ? HC.tok.accent : '#fff', sw: isOut ? 2.6 : 1.2 }, g);
    s.txt(M.a[i], M.b[i], isOut ? '離群' : String(i + 1),
          { dy: -10, cls: 'vlab', fill: HC.tok.accent2 }, g);
  }
  R.cen.forEach((c, k) => {
    if (!Number.isFinite(c[0])) return;
    s.dot(c[0], c[1], { r: 9, fill: w07CL[k], stroke: '#1a1a2e', sw: 2.6 }, g);
    s.dot(c[0], c[1], { r: 2.6, fill: '#fff' }, g);
  });
  /* 右：兩個變數的長條，看誰的變異大 */
  const bx0 = 388, bx1 = 604, by0 = 46, by1 = 292;
  s.add('rect', { x: bx0, y: by0, width: bx1 - bx0, height: by1 - by0, rx: 6,
                  fill: '#fff', stroke: HC.tok.cardBorder }, g);
  s.txtPx(bx0, by0 - 8, '右：每位顧客的兩個變數', { cls: 'axtitle' }, g);
  const hi = Math.max(...M.a, ...M.b, 0.1), lo2 = Math.min(0, ...M.a, ...M.b);
  const bw = (bx1 - bx0 - 24) / (M.n * 2 + 1);
  const yv = v => by1 - 22 - (by1 - by0 - 40) * (v - lo2) / (hi - lo2 || 1);
  s.add('line', { cls: 'ax', x1: bx0 + 10, y1: yv(0), x2: bx1 - 10, y2: yv(0) }, g);
  for (let i = 0; i < M.n; i++) {
    const x = bx0 + 14 + i * bw * 2;
    [[M.a[i], HC.tok.a], [M.b[i], HC.tok.c]].forEach((d, j) => {
      const y1 = yv(0), y2 = yv(d[0]);
      s.add('rect', { x: x + j * bw * 0.9, y: Math.min(y1, y2), width: bw * 0.82,
                      height: Math.max(1, Math.abs(y2 - y1)), fill: d[1], rx: 1 }, g);
    });
  }
  s.txtPx(bx0 + 12, by1 - 6, '每組左＝襪子、右＝電腦', { cls: 'axlab' }, g);
  const vA = HC.stat.variance(M.a), vB = HC.stat.variance(M.b);
  const drv = vA > vB * 1.4 ? '襪子' : (vB > vA * 1.4 ? '電腦' : '兩者相當');
  const grp = k => M.a.map((_, i) => i).filter(i => R.lab[i] === k)
    .map(i => (w07practOut && i === M.n - 1) ? '離群' : String(i + 1)).join(' ');
  $('w07practMode').textContent = w07practModes[w07practMode]
    + (w07practOut ? '（含離群值）' : '');
  $('w07practG1').textContent = '顧客 ' + grp(0);
  $('w07practG2').textContent = '顧客 ' + grp(1);
  $('w07practDrv').textContent = drv + '（變異數 ' + HC.fmt(vA, 2) + ' vs ' + HC.fmt(vB, 2) + '）';
  $('w07practWss').textContent = HC.fmt(R.w, 2);
  const msg = {
    raw: '用原始次數：襪子的變異數比電腦大幾十倍，歐氏距離幾乎只由襪子決定，'
       + '兩群就是「買比較多襪子」與「買比較少襪子」——電腦有沒有買根本沒進到答案裡。',
    scaled: '標準化之後：兩個變數的變異數都是 1，電腦終於有同等的影響力，'
          + '分群變成「有買電腦」與「沒買電腦」。同一份資料、同一個 K，答案完全不同。',
    dollar: '換成花費金額：電腦一台 1400 元、襪子一雙 2 元，'
          + '現在換成電腦主宰距離——分群還是「有買電腦 / 沒買」，但理由跟標準化完全不同。',
  }[w07practMode];
  setStatus('w07practStatus', msg
    + (w07practOut ? ' <strong>離群值已加入：</strong>那位買 60 雙襪子的顧客自己吃掉一整群，'
                     + '剩下八位被擠進另一群——K-means 強迫每一點都要有群，這是代價。' : ''));
}
function w07practSetMode() { w07practMode = $('w07practSel').value; w07practDraw(); }
function w07practToggleOut() { w07practOut = !w07practOut; w07practDraw(); }
function w07practReset() {
  w07practMode = 'raw'; w07practOut = false;
  $('w07practSel').value = 'raw';
  w07practDraw();
}

/* ---------- P10 t-SNE 與 PCA 的嵌入（烘焙） ---------- */
const w07tsneCols = ['#2c3e7a', '#c0392b', '#1a6b4a', '#f39c12', '#8e44ad',
                     '#16a085', '#d35400', '#2980b9', '#7f8c8d', '#c2185b'];
function w07tsneSet() { w07tsneDraw(); }
function w07tsneDraw() {
  const F = FRAMES_w07tsne, key = $('w07tsneSel').value, V = F.views[key];
  const sets = [];
  for (let d = 0; d < 10; d++) {
    sets.push({
      label: String(d),
      data: V.xy.map((p, i) => (F.labels[i] === d ? { x: p[0], y: p[1] } : null))
              .filter(Boolean),
      backgroundColor: w07tsneCols[d], pointRadius: 2.6, borderWidth: 0,
    });
  }
  HC.scatter('w07tsneChart', { datasets: sets }, {
    interaction: { mode: 'nearest', intersect: true },
    plugins: { legend: { labels: { boxWidth: 8, boxHeight: 8 } } },
    scales: { x: { title: { display: true, text: '第一個座標（沒有單位）' } },
              y: { title: { display: true, text: '第二個座標（沒有單位）' } } },
  });
  $('w07tsneName').textContent = V.name;
  $('w07tsneN').textContent = String(F.n);
  setStatus('w07tsneStatus', key === 'pca'
    ? 'PCA：只是線性投影，前兩個主成分把 64 維壓成 2 維，十個數字大量重疊——'
      + '線性方法抓不到「彎曲」的結構。'
    : V.name + '：同一批 ' + F.n + ' 個點被拉成清楚的團（顏色是真實標籤，沒有參與計算）。'
      + '但團的大小、團之間的距離、還有座標本身，都不可以拿來下結論。');
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉。HC.line / HC.scatter 在 Chart 未載入時安全地回傳 null。 */
w07spinSetup();
w07spinSet(8 / w07DEG);
w07biDraw();
w07mcReset();
w07kmSetup();
w07kmReset();
w07dSetup();
w07dInstallDrag();
w07dDraw();
w07practDraw();
HC.ready(() => {
  w07screeDraw();
  w07mcChart();
  w07tsneDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("unsupervised_learning", BODIES, PAGEJS, frames())
