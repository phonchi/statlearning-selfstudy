#!/usr/bin/env python3
"""p5_visualization.html（先備 P5 · 視覺化）完整自學充實。冪等。

內容依據：Ch01-lab-zh.ipynb 的整段 seaborn（儲存格 88–138）與
Ch02-statlearn-lab-zh.ipynb 的 matplotlib 基礎（儲存格 96–125）。

這一頁大量走 STYLE_CONTRACT §9.1 的第二條路：**繪圖儲存格沒有文字輸出**
（lab 存下來的是 `<Figure size … with N Axes>`），所以程式碼卡一律 output=None，
圖本身由頁面上的 live 元件重畫，並在 note 裡講清楚這件事。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LAB1 = "Ch01-lab-zh.ipynb"
LAB2 = "Ch02-statlearn-lab-zh.ipynb"
FIG_NOTE = "（產生的是圖，沒有文字輸出可對照。）"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB1 if ch == 1 else LAB2
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 為什麼要先畫圖 ────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>統計課教你算平均、標準差、相關係數。這些數字很有用，但它們<strong>會漏掉形狀</strong>。
  四組資料可以有幾乎一樣的平均、標準差、相關係數與迴歸線，畫出來卻完全不同。
  這不是刻意湊出的動畫，而是 Anscombe 在 1973 年提出、可以逐筆驗算的經典四重奏。</p>

{info("一句話", "<strong>先畫圖，再算數字。</strong>"
      "圖告訴你「這份資料長什麼樣」，數字告訴你「有多強」——順序反過來很容易被騙。")}

{viz(chart("w18sameChart", fallback="：Anscombe 四組資料的摘要統計幾乎相同，"
                                   "但散佈圖形狀完全不同。"),
     [info_card("按按鈕換一組",
                "四組資料的<strong>平均、標準差、相關係數與迴歸線都幾乎一樣</strong>，"
                "但形狀完全不同。只看數字的話，你會以為它們是同一回事。"),
      rows_card("這一組的摘要統計",
                [("x 平均", "—", "w18smMx"),
                 ("y 平均", "—", "w18smMy"),
                 ("x／y 樣本標準差", "—", "w18smSd"),
                 ("相關係數 r", "—", "w18smR"),
                 ("最小平方線", "—", "w18smLine")]),
      info_card("這些點哪裡來的",
                "逐筆採用 Anscombe's quartet 的經典 11 筆資料；"
                "頁面再由同一批點即時計算平均與相關係數，沒有另寫摘要數字。")],
     "w18smStatus", "四組資料，摘要統計幾乎相同。先看數字，再按按鈕看形狀。",
     '<button class="btn btn-toggle" onclick="w18smSet(0)">I</button>'
     '<button class="btn btn-toggle" onclick="w18smSet(1)">II</button>'
     '<button class="btn btn-toggle" onclick="w18smSet(2)">III</button>'
     '<button class="btn btn-toggle" onclick="w18smSet(3)">IV</button>',
     provenance=("book-redraw", "Anscombe (1973) 四重奏原始數據；摘要由圖中同一批點即時計算。"))}

{info("這一頁的程式碼卡為什麼沒有「預期輸出」",
      "繪圖的儲存格在 notebook 裡存下來的是圖，不是文字，"
      "所以下面的程式碼卡多半只有程式碼、沒有預期輸出。"
      "圖本身的行為改由每一節的互動元件重現——"
      "<strong>那些元件是頁面當場算的，不是課程圖的截圖</strong>（本站 repo 不放任何圖檔）。")}

{card("這一頁用的資料：tips", C(1, 88), O(1, 88), src=S(1, 88),
      note="244 筆餐廳帳單。<code>total_bill</code> 與 <code>tip</code> 是數值，"
           "<code>day</code>、<code>sex</code>、<code>smoker</code> 是類別——"
           "這兩種型別要配不同的圖。")}

{quiz("qSame", "PART 00 · 自我檢測",
      "兩份資料的相關係數都是 0.82。可以推論什麼？",
      [(False, "兩份資料的散佈圖會很像",
        "不一定。相關係數只量「線性關係有多強」，"
        "它看不出曲線、看不出離群值、也看不出資料是不是分成兩群。"),
       (True, "只知道兩者的線性關係強度接近，形狀可能完全不同",
        "對。所以拿到資料的第一個動作是畫圖，不是算相關係數。"
        "第 3 章講迴歸診斷時會再看到同一件事：殘差圖比 R² 誠實。"),
       (False, "兩份資料的迴歸線斜率一樣",
        "不一定。相關係數跟斜率是兩回事——斜率還取決於兩個變數的標準差比例。")])}
"""

# ── P01 Figure 與 Axes ─────────────────────────────────────────────────
BODIES["anat"] = f"""
  <p>matplotlib 的物件有兩層，搞混這兩層是所有「為什麼我的設定沒有生效」的根源：
  <strong>Figure 是整張畫布</strong>（大小、存檔、標題），
  <strong>Axes 是裡面的一個座標系</strong>（畫點、設軸範圍、加圖例）。
  一張 Figure 可以有很多個 Axes。</p>

{viz(svg("w18anatSvg", 320),
     [info_card("點名字看它管什麼",
                "按按鈕，對應的部分會亮起來，右邊會顯示「這一層負責什麼」與"
                "「動它的方法叫什麼」。"),
      rows_card("目前",
                [("物件", "Figure", "w18anObj"),
                 ("負責什麼", "整張畫布", "w18anWhat"),
                 ("常用方法", "set_size_inches、savefig", "w18anHow")]),
      info_card("為什麼 seaborn 有時候回 Figure、有時候回 Axes",
                "名字結尾是 <code>plot</code> 的多半回 Axes（<code>histplot</code>、"
                "<code>regplot</code>）；<code>relplot</code>、<code>catplot</code>、"
                "<code>lmplot</code> 這種會自己開一張新 Figure（叫 figure-level）。"
                "要塞進自己的 subplots 就得挑前者。")],
     "w18anStatus", "先分清楚哪一層是哪一層，之後查文件會快很多。",
     '<button class="btn btn-toggle" onclick="w18anSet(0)">Figure</button>'
     '<button class="btn btn-toggle" onclick="w18anSet(1)">Axes</button>'
     '<button class="btn btn-toggle" onclick="w18anSet(2)">Axis（軸）</button>'
     '<button class="btn btn-toggle" onclick="w18anSet(3)">Artist（點、線、字）</button>',
     provenance=("illustrative", "依 matplotlib 的 Figure／Axes／Axis／Artist 物件層級製作概念示意。"))}

{card("subplots 一次給你兩個東西", C(2, 96), src=S(2, 96), note="這一格畫的是圖。" + FIG_NOTE)}

{card("散佈圖與軸標籤", C(2, 105), src=S(2, 105), note="這一格畫的是圖。" + FIG_NOTE)}

{viz(svg("w18gridSvg", 300),
     [info_card("axes 是一個二維陣列",
                "<code>subplots(nrows=2, ncols=3)</code> 回傳的 <code>axes</code> "
                "是一個 <strong>(2, 3) 的 NumPy 陣列</strong>。"
                "點格子看它的索引——就是 P3 講的二維索引。"),
      rows_card("目前選到",
                [("索引", "axes[0, 0]", "w18gdIdx"),
                 ("在第幾列第幾欄", "第 0 列、第 0 欄", "w18gdPos")]),
      info_card("常見錯誤",
                "<code>nrows=1</code> 時 <code>axes</code> 會退化成一維，"
                "<code>axes[0, 1]</code> 就會報錯。"
                "要一致就寫 <code>subplots(1, 3, squeeze=False)</code>。")],
     "w18gdStatus", "點任一格，看它的索引。",
     '<button class="btn btn-step" onclick="w18gdNext()">→ 下一格</button>'
     '<button class="btn btn-reset" onclick="w18gdReset()">重置</button>',
     provenance=("course-data", "依 Ch02 lab 的 2×3 subplots 與 axes 索引範例重繪。"))}

{card("2×3 的子圖網格", C(2, 112, 114), src=S(2, 112, 114), note="這一格畫的是圖。" + FIG_NOTE)}

{quiz("qAnat", "PART 01 · 自我檢測",
      "你用 <code>sns.relplot(...)</code> 畫完圖，接著寫 <code>ax.set_xlim([0, 10])</code>，"
      "卻沒有任何效果。最可能的原因是？",
      [(True, "<code>relplot</code> 自己開了一張新的 Figure，你的 <code>ax</code> 指的是別張圖",
        "對。<code>relplot</code>／<code>catplot</code>／<code>lmplot</code> 是 figure-level，"
        "它不會畫到你手上那個 <code>ax</code> 上。要控制軸就改用 "
        "<code>scatterplot</code> 這種 axes-level 的函式並傳 <code>ax=ax</code>。"),
       (False, "<code>set_xlim</code> 要寫在畫圖之前",
        "順序不是問題。matplotlib 的設定隨時可以改，改完重新顯示就會生效。"),
       (False, "seaborn 不支援設定軸範圍",
        "支援。問題不在支不支援，在你設到了<strong>另一個 Axes</strong> 上。")])}
"""

# ── P02 分布 ────────────────────────────────────────────────────────────
BODIES["dist"] = f"""
  <p>看一個變數的分布有兩種標準做法：直方圖與密度圖。兩者都有一個<strong>你必須自己決定的參數</strong>——
  直方圖是 bins（切幾格），密度圖是頻寬（平滑多少）。這個參數不是細節，
  它可以讓同一份資料看起來有兩個峰或只有一個。</p>

{info("這是本頁最重要的一件事",
      "<strong>調參數之前先想好你要回答什麼問題。</strong>"
      "想看「有沒有兩群」就把 bins 調細一點；想看「大致集中在哪」就調粗一點。"
      "調到「圖看起來最漂亮」為止，是在騙自己。", "warm")}

{viz(svg("w18binsSvg", 340),
     [info_card("拖 bins，看結論怎麼變",
                "同一份資料（固定種子產生，實際上是<strong>兩個峰</strong>）。"
                "bins 太少會把兩個峰糊成一個，太多會讓雜訊看起來像結構。"),
      rows_card("目前",
                [("模式", "直方圖", "w18bnMode"),
                 ("bins / 頻寬", "10", "w18bnParam"),
                 ("你會看到幾個峰", "—", "w18bnPeaks")]),
      info_card("密度圖也一樣",
                "切到「密度圖」模式，改的是<strong>頻寬</strong>。"
                "頻寬大＝平滑＝可能糊掉真的結構；頻寬小＝每個點都戳出一根。"
                "兩者是同一個取捨換了個名字。")],
     "w18bnStatus", "先猜這份資料有幾個峰，再把 bins 從 4 拉到 40。",
     '<button class="btn btn-step" onclick="w18bnStep(-4)">參數 −</button>'
     '<button class="btn btn-step" onclick="w18bnStep(4)">參數 +</button>'
     '<button class="btn btn-toggle" onclick="w18bnMode()">切換：直方圖 ⇄ 密度圖</button>'
     '<button class="btn btn-reset" onclick="w18bnReset()">重置</button>',
     provenance=("simulation", "固定種子 20260828 的雙峰常態混合模擬；120 筆資料由頁面即時計算。"))}

{card("最基本的直方圖", C(1, 105), src=S(1, 105),
      note="lab 的註解就提醒了 <code>bins</code> 這個參數。" + FIG_NOTE)}

{card("依類別分色與堆疊", C(1, 106, 107), src=S(1, 106, 107),
      note="<code>hue</code> 分色、<code>multiple='stack'</code> 疊起來。"
           "分色看得出各組的形狀，堆疊看得出總量——兩種問題。" + FIG_NOTE)}

{card("密度圖", C(1, 110, 111), src=S(1, 110, 111),
      note="<code>kdeplot</code> 把每個點換成一個小鐘形再加起來，"
           "所以它<strong>一定是平滑的</strong>。那個平滑是你給的假設，不是資料本身。" + FIG_NOTE)}

{quiz("qDist", "PART 02 · 自我檢測",
      "同一份資料，bins=5 看起來是一個峰，bins=30 看起來是兩個峰。你該怎麼辦？",
      [(False, "選看起來比較漂亮的那一張放進報告",
        "這就是本節警告的事。「漂亮」不是判準。你是在挑一個支持自己想法的圖。"),
       (True, "兩張都看，再回頭問「有沒有理由相信這兩群真的存在」",
        "對。圖是提出假設的工具，不是證據本身。"
        "如果兩群對應到某個真實的分類（例如吸菸與不吸菸），"
        "就用 <code>hue</code> 分色驗證；驗不出來就不要宣稱有兩群。"),
       (False, "用預設的 bins，seaborn 的預設一定是對的",
        "沒有「一定對」的 bins。seaborn 的預設只是一個經驗法則，"
        "它不知道你要回答什麼問題。")])}
"""

# ── P03 兩個變數的關係 ──────────────────────────────────────────────────
BODIES["rel"] = f"""
  <p>兩個變數的關係圖幾乎都是散佈圖的變形。seaborn 幫你做的事是
  <strong>用顏色、大小、分面把第三、第四個變數也塞進同一張圖</strong>——
  <code>hue</code>、<code>size</code>、<code>col</code> 這三個參數值得記起來。</p>

{viz(svg("w18pickSvg", 340),
     [info_card("先問變數型別",
                "選 x 與 y 各是什麼型別，右邊會給建議的圖與對應的 seaborn 函式。"
                "這張決策樹涵蓋 lab 裡出現過的每一種圖。"),
      rows_card("建議",
                [("圖型", "—", "w18pkKind"),
                 ("函式", "—", "w18pkFn"),
                 ("它在回答什麼", "—", "w18pkQ")]),
      info_card("第三個變數怎麼辦",
                "<code>hue=</code> 用顏色、<code>size=</code> 用點的大小、"
                "<code>col=</code> 拆成好幾張小圖。"
                "超過兩個額外變數的話，多半該畫好幾張圖而不是硬塞。")],
     "w18pkStatus", "選 x 與 y 的型別。",
     '<button class="btn btn-toggle" onclick="w18pkSet(0)">數值 × 數值</button>'
     '<button class="btn btn-toggle" onclick="w18pkSet(1)">類別 × 數值</button>'
     '<button class="btn btn-toggle" onclick="w18pkSet(2)">類別 × 類別</button>'
     '<button class="btn btn-toggle" onclick="w18pkSet(3)">單一數值</button>'
     '<button class="btn btn-toggle" onclick="w18pkSet(4)">時間 × 數值</button>',
     provenance=("course-data", "依 Ch01 lab 實際使用的 seaborn 圖型與變數型別整理。"))}

{card("散佈圖，以及把第三個變數塞進去", C(1, 91, 93), src=S(1, 91, 93),
      note="<code>hue</code> 與 <code>style</code> 同時用同一個變數，"
           "是為了在黑白列印時也分得出來。這個習慣值得學。" + FIG_NOTE)}

{card("用點的大小表示第三個變數", C(1, 95), src=S(1, 95),
      note="<code>sizes=(15, 200)</code> 明確指定最小與最大的點徑。"
           "不指定的話預設範圍很窄，看不出差別。" + FIG_NOTE)}

{card("折線圖與信賴帶", C(1, 102), src=S(1, 102),
      note="<code>lineplot</code> 對同一個 x 有多筆資料時，"
           "會自動畫平均與 95% 信賴帶。那條帶子是 bootstrap 算出來的，"
           "第 5 章會講它怎麼來的。" + FIG_NOTE)}

{card("joint 與 pair", C(1, 114, 117), src=S(1, 114, 117),
      note="<code>pairplot</code> 是探索階段最划算的一張圖："
           "所有數值欄兩兩配對，一眼看完。欄多的時候會很慢，先挑幾欄再畫。" + FIG_NOTE)}

{quiz("qRel", "PART 03 · 自我檢測",
      "你想看「小費金額與帳單金額的關係，並區分吸菸與否」。最直接的寫法是？",
      [(True, "<code>sns.relplot(x='total_bill', y='tip', hue='smoker', data=tips)</code>",
        "對。兩個數值變數用散佈圖，第三個類別變數用 <code>hue</code> 上色。"
        "lab 儲存格 93 就是這一行。"),
       (False, "<code>sns.catplot(x='smoker', y='tip', data=tips)</code>",
        "這張圖只看得到吸菸與否對小費的影響，<strong>total_bill 不見了</strong>——"
        "而它才是最主要的解釋變數。"),
       (False, "畫兩張散佈圖，一張吸菸一張不吸菸",
        "可以（那就是 <code>col='smoker'</code>），但要比較兩組時"
        "疊在同一張圖上用顏色分比較容易看出差異。")])}
"""

# ── P04 類別變數的圖 ────────────────────────────────────────────────────
BODIES["cat"] = f"""
  <p>類別變數的圖最容易被誤讀，因為它們看起來都像長條，但講的事情差很多：
  <strong>countplot 講「有幾筆」、barplot 講「平均是多少」、boxplot 講「分布長怎樣」</strong>。
  三種被混用的後果是很嚴重的。</p>

{viz(svg("w18misSvg", 340),
     [info_card("同一份資料，兩種畫法",
                "左邊是誠實的版本（y 軸從 0 開始），右邊是截斷 y 軸的版本。"
                "按按鈕切換；右側倍率會由同一批資料與目前的軸起點即時計算。"),
      rows_card("兩組的真實數字",
                [("A 組平均", "2.98", "w18msA"),
                 ("B 組平均", "3.26", "w18msB"),
                 ("看起來差幾倍", "—", "w18msRatio")]),
      info_card("什麼時候可以截斷",
                "當零沒有意義時（例如體溫、年份）截斷是合理的，"
                "但要<strong>明確標出來</strong>。"
                "長條圖用長度編碼數量，截斷等於把長度的意義弄壞，所以特別不該截。")],
     "w18msStatus", "先看左邊，再按「截斷 y 軸」。",
     '<button class="btn btn-toggle" onclick="w18msSet(0)">y 軸從 0 開始</button>'
     '<button class="btn btn-toggle" onclick="w18msSet(1)">截斷 y 軸</button>'
     '<button class="btn btn-toggle" onclick="w18msSet(2)">改用盒鬚圖</button>',
     provenance=("illustrative", "A、B 兩組固定示意資料；平均、盒鬚摘要與視覺倍率皆由同一批觀測即時計算。"))}

{card("盒鬚圖：看分布", C(1, 120, 121), src=S(1, 120, 121),
      note="盒子是四分位距、線是中位數、鬚是 1.5 倍 IQR 內的極值，"
           "外面的點是離群值。<strong>在本節比較的基本類別圖中，只有盒鬚圖直接標出這些候選離群值。</strong>" + FIG_NOTE)}

{card("長條圖：看平均與不確定性", C(1, 124, 125), src=S(1, 124, 125),
      note="<code>barplot</code> 的長條高度是<strong>平均</strong>，"
           "上面那條細線是 bootstrap 信賴區間，不是標準差。" + FIG_NOTE)}

{card("計數圖：看筆數", C(1, 127), src=S(1, 127),
      note="<code>countplot</code> 只數筆數，跟 <code>value_counts()</code> 是同一件事的圖版。" + FIG_NOTE)}

{card("點估計圖：專門用來比較", C(1, 130), src=S(1, 130),
      note="把長條換成一個點加誤差線。要比較好幾組的平均時，"
           "點比長條清楚——長條的面積會搶掉注意力。" + FIG_NOTE)}

{table(["圖", "高度／位置代表什麼", "適合回答"],
       [["<code>countplot</code>", "筆數", "哪一類最多？有沒有哪一類樣本太少？"],
        ["<code>barplot</code>", "平均（＋信賴區間）", "各組的平均差多少？差得有多確定？"],
        ["<code>boxplot</code>", "中位數與四分位距", "分布形狀？有沒有離群值？"],
        ["<code>pointplot</code>", "平均（＋誤差線）", "多組平均之間的<b>比較</b>與趨勢"]])}

{quiz("qCat", "PART 04 · 自我檢測",
      "一張 <code>barplot</code> 顯示週四的小費比週五高。你還需要知道什麼才能下結論？",
      [(False, "不用，長條比較高就是比較高",
        "長條的高度是<strong>平均</strong>。兩組平均有差，不代表這個差站得住腳。"),
       (True, "兩組各有幾筆、以及誤差線有沒有重疊",
        "對。<code>barplot</code> 預設會畫 bootstrap 信賴區間，"
        "重疊很多就代表這個差可能只是抽樣的隨機性。"
        "另外週五如果只有 19 筆，那條線會很長——樣本數要一起看。"),
       (False, "只要看兩組的標準差",
        "標準差講的是個別觀測的分散程度，不是<strong>平均</strong>的不確定性。"
        "後者是標準誤，跟樣本數有關。")])}

{hook("這在本站哪一章會用到",
      '第 12 章的主成分分析要看雙標圖（biplot）、分群要看樹狀圖，都是這一節的延伸；'
      '第 3 章的殘差圖更是整章的診斷主力。'
      '<a href="unsupervised_learning.html#pca">→ 非監督式學習 · 主成分分析</a>')}
"""

# ── P05 把模型畫進圖裡 ─────────────────────────────────────────────────
BODIES["model"] = f"""
  <p>最後一種圖：<strong>把配適好的模型畫在資料上面</strong>。
  這是統計圖跟一般商業圖表最大的差別。你不只在描述資料，還在展示一個模型對不對。</p>

{viz(svg("w18corrSvg", 340),
     [info_card("熱圖在講什麼",
                "點任一格，右邊顯示那一對變數的相關係數與它的意思。"
                "對角線一定是 1（自己跟自己）。"),
      rows_card("目前選到",
                [("變數對", "—", "w18crPair"),
                 ("相關係數", "—", "w18crVal"),
                 ("怎麼讀", "—", "w18crRead")]),
      info_card("熱圖的陷阱",
                "顏色會讓「0.3 與 0.5」看起來差很多、「0.85 與 0.9」看起來差不多，"
                "端看色階怎麼設。<strong>要下結論就回去看數字</strong>，"
                "熱圖是用來快速找候選的。")],
     "w18crStatus", "點格子看那一對變數的相關係數。",
     '<button class="btn btn-step" onclick="w18crNext()">→ 下一格</button>'
     '<button class="btn btn-reset" onclick="w18crReset()">重置</button>',
     provenance=("course-data", "依 Ch01 lab 的 tips.corr(numeric_only=True) 相關矩陣重繪。"))}

{card("散佈圖加迴歸線", C(1, 133), src=S(1, 133),
      note="<code>regplot</code> 直接配一條最小平方直線並畫出 95% 信賴帶。"
           "那條帶子是<strong>對迴歸線的不確定性</strong>，不是預測區間——"
           "第 3 章會分清楚這兩者。" + FIG_NOTE)}

{card("依類別分別配適", C(1, 135, 136), src=S(1, 135, 136),
      note="<code>lmplot</code> 加 <code>hue</code> 會<strong>每一組各配一條線</strong>。"
           "兩條線的斜率明顯不同，就是交互作用的視覺證據。" + FIG_NOTE)}

{card("相關係數熱圖", C(1, 138), src=S(1, 138),
      note="<code>tips.corr(numeric_only=True)</code> 先算矩陣，"
           "<code>heatmap</code> 只負責上色。共線性的初步檢查常從這裡開始。" + FIG_NOTE)}

{qa("觀念釐清", [
    ("<code>regplot</code> 幫我配了線，是不是就等於做了迴歸分析？",
     "不是。它只給你一條線與一條帶子，<strong>沒有係數、沒有 p 值、沒有診斷</strong>。"
     "要那些東西得用 statsmodels（P6 會講）。"
     "<code>regplot</code> 的用途是「先看看有沒有線性關係」。"),
    ("熱圖看到兩個變數相關 0.9，該怎麼辦？",
     "先想它們是不是本來就在量同一件事（例如 <code>weight</code> 與 "
     "<code>displacement</code>）。真的要放進同一個迴歸模型的話，"
     "第 3 章的共線性與第 6 章的收縮方法就是在處理這件事。"),
])}

{quiz("qModel", "PART 05 · 自我檢測",
      "<code>lmplot</code> 加了 <code>hue='smoker'</code> 之後，兩組的迴歸線斜率明顯不同。"
      "這在暗示什麼？",
      [(False, "吸菸者的小費比較高",
        "斜率不同講的不是「誰比較高」（那是截距與整體位置的事），"
        "而是「<strong>帳單每增加一元，小費增加多少</strong>」在兩組之間不一樣。"),
       (True, "帳單對小費的效果在兩組之間不同，可能有交互作用",
        "對。斜率隨另一個變數改變，正是交互作用的定義。"
        "第 3 章會教怎麼在模型裡寫出來（<code>total_bill * smoker</code>），"
        "並檢定它是不是真的。"),
       (False, "資料裡有離群值",
        "離群值會影響斜率，但「兩組斜率不同」本身不是離群值的證據。"
        "要看離群值該畫盒鬚圖或殘差圖。")])}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 選圖",
      "你要呈現「三個地區（origin）的 mpg 分布，並讓讀者看得出有沒有離群值」。該畫什麼？",
      [(False, "<code>barplot</code>，三根長條比高低",
        "<code>barplot</code> 只給平均與信賴區間，"
        "<strong>離群值完全看不到</strong>。它們被平均掉了。"),
       (True, "<code>boxplot</code>（或加上 <code>stripplot</code> 疊點）",
        "對。在本節比較的基本類別圖中，盒鬚圖會把超出鬚線的觀測單獨畫成點。"
        "組數少、樣本不多的時候再疊一層原始點更誠實。"),
       (False, "<code>countplot</code>",
        "它只數每一組有幾筆，完全沒有用到 mpg 這個變數。")])}

{quiz("qEx2", "EXERCISE 2 · bins",
      "把 bins 從 10 調到 60 之後，直方圖出現很多小峰。最合理的解讀是？",
      [(True, "多半是抽樣雜訊，除非那些峰對應到某個真實的分類",
        "對。bins 越細，每一格的樣本越少，隨機起伏就越明顯。"
        "要判斷是不是真的結構，就用 <code>hue</code> 拿一個候選的分類變數去驗。"),
       (False, "資料真的有很多群，應該用 60 這張",
        "細的 bins 幾乎一定會生出更多峰，這是它的數學性質，不是資料的性質。"),
       (False, "資料有問題，應該重新收集",
        "沒有證據支持這個結論。先換個參數再看，不要跳到最貴的行動。")])}

{quiz("qEx3", "EXERCISE 3 · 圖表誠實度",
      "一張長條圖把 y 軸截在兩組平均附近，讓小差異看起來大幅放大。這張圖錯在哪？",
      [(False, "沒錯，只是放大了差異方便觀察",
        "「方便觀察」跟「誤導」的界線就在這裡。長條圖用<strong>長度</strong>編碼數值，"
        "截斷之後長度的比例不再對應數值的比例。"),
       (True, "長條圖用長度表示數量，截斷 y 軸會破壞長度的意義",
        "對。真的要放大差異，改用點估計圖（<code>pointplot</code>）——"
        "點的位置不隱含「從零開始」的承諾，截斷是可以接受的，"
        "而且要在圖上標明。"),
       (False, "應該把 y 軸改成對數尺度",
        "對數是給跨數量級的資料用的。2.98 與 3.26 差不到 10%，取對數只會更難讀。")])}

{quiz("qEx4", "EXERCISE 4 · figure-level 與 axes-level",
      "你想把四張 seaborn 圖排成 2×2 放進同一張 Figure。下列哪一個函式<strong>做不到</strong>？",
      [(False, "<code>sns.histplot(..., ax=axes[0,0])</code>",
        "做得到。名字結尾是 <code>plot</code> 的多半是 axes-level，接受 <code>ax=</code>。"),
       (False, "<code>sns.boxplot(..., ax=axes[0,1])</code>",
        "做得到，同樣是 axes-level。"),
       (True, "<code>sns.relplot(..., ax=axes[1,0])</code>",
        "對，這個做不到。<code>relplot</code> 是 figure-level，它會自己開一張新 Figure，"
        "根本不吃 <code>ax=</code> 參數。要散佈圖就改用 <code>sns.scatterplot</code>。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>選圖速查表。先問「x 與 y 各是什麼型別」，再問「我要回答什麼」。</p>

{table(["x 的型別", "y 的型別", "圖", "seaborn"],
       [["數值", "數值", "散佈圖", "<code>scatterplot</code> / <code>relplot</code>"],
        ["數值", "數值（有序、每個 x 多筆）", "折線圖＋信賴帶", "<code>lineplot</code>"],
        ["數值", "數值（要看模型）", "散佈圖＋迴歸線", "<code>regplot</code> / <code>lmplot</code>"],
        ["數值", "—", "直方圖／密度圖", "<code>histplot</code> / <code>kdeplot</code>"],
        ["類別", "數值", "盒鬚圖／長條圖／點估計圖", "<code>catplot(kind=…)</code>"],
        ["類別", "—", "計數圖", "<code>countplot</code>"],
        ["類別", "類別", "計數的交叉表＋熱圖", "<code>heatmap</code>"],
        ["多個數值欄", "—", "成對關係圖／相關熱圖", "<code>pairplot</code> / <code>heatmap</code>"]])}

{table(["figure-level（自己開 Figure）", "axes-level（可以傳 ax=）"],
       [["<code>relplot</code>", "<code>scatterplot</code>、<code>lineplot</code>"],
        ["<code>catplot</code>", "<code>boxplot</code>、<code>barplot</code>、<code>countplot</code>、<code>pointplot</code>"],
        ["<code>displot</code>", "<code>histplot</code>、<code>kdeplot</code>"],
        ["<code>lmplot</code>、<code>jointplot</code>、<code>pairplot</code>", "<code>regplot</code>、<code>heatmap</code>"]])}

{table(["參數", "做什麼", "什麼時候用"],
       [["<code>hue=</code>", "用顏色分第三個變數", "組數 ≤ 5、要疊在同一張圖比較"],
        ["<code>style=</code>", "用標記形狀分", "要黑白列印時搭配 hue 一起用"],
        ["<code>size=</code>", "用點的大小分", "第三個變數是數值且範圍大"],
        ["<code>col=</code> / <code>row=</code>", "拆成好幾張小圖", "組數多、疊起來會糊"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 先畫圖再算數字。</strong>摘要統計會漏掉形狀，"
      "相關係數一樣的兩份資料可以長得完全不同。<br>"
      "<strong>2. bins 與頻寬是你的假設，不是資料的性質。</strong>"
      "調參數之前先想好要回答什麼問題。<br>"
      "<strong>3. countplot 講筆數、barplot 講平均、boxplot 講分布。</strong>"
      "三種長條講三件事，不要混用。")}

{ver_note((1, 2))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* ═══ w18an Figure / Axes 解剖 ═══ */
const w18anS = HC.svg('w18anatSvg', {h: 320});
const w18anCases = [
  {o: 'Figure', w: '整張畫布：大小、存檔、總標題', h: 'set_size_inches、savefig、suptitle',
   note: '一張 Figure 可以裝好幾個 Axes。<code>fig.savefig()</code> 存的是整張。'},
  {o: 'Axes', w: '一個座標系：資料真正被畫進去的地方', h: 'plot、scatter、set_xlim、legend',
   note: '你 99% 的時間都在跟它打交道。seaborn 的 ax= 參數指的就是它。'},
  {o: 'Axis（軸）', w: '單一根軸的刻度與標籤', h: 'set_xlabel、set_xticks',
   note: '注意 Axes（座標系）與 Axis（軸）差一個字母，是兩個不同的東西。'},
  {o: 'Artist', w: '畫上去的每一個東西：點、線、文字', h: 'set_color、set_alpha',
   note: 'plot() 回傳的就是一串 Artist，抓住它就能事後改樣式。'}
];
let w18anI = 0;
function w18anDraw() {
  const g = w18anS.clearLayer('main');
  const c = w18anCases[w18anI];
  const on = (k, col) => (w18anI === k ? col : HC.tok.card);
  w18anS.add('rect', {x: 60, y: 50, width: 500, height: 230, rx: 8,
                      fill: on(0, HC.tok.accent), opacity: w18anI === 0 ? 0.35 : 0.12,
                      stroke: w18anI === 0 ? HC.tok.accent : HC.tok.cardBorder,
                      'stroke-width': w18anI === 0 ? 3 : 1.5}, g);
  w18anS.txtPx(70, 44, 'Figure', {cls: 'axtitle',
                                  fill: w18anI === 0 ? HC.tok.accent : HC.tok.muted}, g);
  w18anS.add('rect', {x: 110, y: 78, width: 400, height: 176, rx: 6,
                      fill: on(1, HC.tok.accent2), opacity: w18anI === 1 ? 0.35 : 0.12,
                      stroke: w18anI === 1 ? HC.tok.accent2 : HC.tok.cardBorder,
                      'stroke-width': w18anI === 1 ? 3 : 1.5}, g);
  w18anS.txtPx(120, 96, 'Axes', {cls: 'axtitle',
                                 fill: w18anI === 1 ? HC.tok.accent2 : HC.tok.muted}, g);
  const axc = w18anI === 2 ? HC.tok.accent : HC.tok.muted;
  w18anS.add('path', {d: 'M150 230 H470', stroke: axc,
                      'stroke-width': w18anI === 2 ? 4 : 2}, g);
  w18anS.add('path', {d: 'M150 230 V110', stroke: axc,
                      'stroke-width': w18anI === 2 ? 4 : 2}, g);
  [[190, 200], [240, 176], [292, 186], [340, 148], [396, 132], [440, 150]].forEach(pt => {
    w18anS.add('circle', {cx: pt[0], cy: pt[1], r: w18anI === 3 ? 7 : 5,
                          fill: w18anI === 3 ? HC.tok.accent : HC.tok.muted,
                          opacity: w18anI === 3 ? 1 : 0.55}, g);
  });
  document.getElementById('w18anObj').textContent = c.o;
  document.getElementById('w18anWhat').textContent = c.w;
  document.getElementById('w18anHow').textContent = c.h;
  setStatus('w18anStatus', c.note);
}
function w18anSet(i) { w18anI = i; w18anDraw(); }
if (w18anS) w18anDraw();

/* ═══ w18gd subplots 網格 ═══ */
const w18gdS = HC.svg('w18gridSvg', {h: 300});
let w18gdI = 0;
function w18gdDraw() {
  const g = w18gdS.clearLayer('main');
  const cw = 158, chh = 96, x0 = 60, y0 = 70;
  for (let r = 0; r < 2; r++) {
    for (let c = 0; c < 3; c++) {
      const k = r * 3 + c, on = k === w18gdI;
      w18gdS.add('rect', {x: x0 + c * cw, y: y0 + r * chh, width: cw - 14, height: chh - 14,
                          rx: 6, fill: on ? HC.tok.accent2 : HC.tok.card,
                          stroke: HC.tok.cardBorder, 'stroke-width': 1.5,
                          opacity: on ? 0.95 : 0.5}, g);
      const t = w18gdS.add('text', {x: x0 + c * cw + (cw - 14) / 2,
                                    y: y0 + r * chh + (chh - 14) / 2 + 6,
                                    'text-anchor': 'middle', cls: 'vlab',
                                    'font-family': HC.MONO,
                                    fill: on ? HC.tok.paper : HC.tok.muted}, g);
      t.textContent = 'axes[' + r + ',' + c + ']';
    }
  }
  w18gdS.txtPx(24, 40, 'subplots(nrows=2, ncols=3)', {cls: 'axtitle'}, g);
  const r = Math.floor(w18gdI / 3), c = w18gdI % 3;
  document.getElementById('w18gdIdx').textContent = 'axes[' + r + ', ' + c + ']';
  document.getElementById('w18gdPos').textContent = '第 ' + r + ' 列、第 ' + c + ' 欄';
  setStatus('w18gdStatus', 'axes 是一個 <b>(2, 3)</b> 的 NumPy 陣列，索引法跟 P3 完全一樣。');
}
function w18gdNext() { w18gdI = (w18gdI + 1) % 6; w18gdDraw(); }
function w18gdReset() { w18gdI = 0; w18gdDraw(); }
if (w18gdS) w18gdDraw();
"""

PAGEJS += r"""
/* ═══ w18bn bins 與頻寬（本頁招牌）═══ */
const w18bnS = HC.svg('w18binsSvg', {h: 340});
const w18bnData = (() => {
  /* 固定種子的雙峰資料：60 筆在 3 附近、60 筆在 8 附近 */
  const rand = HC.stat.lcg(20260828), out = [];
  for (let i = 0; i < 60; i++) out.push(3 + HC.stat.normal(rand) * 0.9);
  for (let i = 0; i < 60; i++) out.push(8 + HC.stat.normal(rand) * 1.1);
  return out;
})();
let w18bnK = 10, w18bnKde = false;
function w18bnDraw() {
  const s = w18bnS;
  s.domain([0, 12], [0, 1]);
  const g = s.clearLayer('main');
  const lo = 0, hi = 12;
  let peaks = 0;
  if (!w18bnKde) {
    const k = w18bnK, counts = new Array(k).fill(0);
    w18bnData.forEach(v => {
      const j = Math.max(0, Math.min(k - 1, Math.floor((v - lo) / (hi - lo) * k)));
      counts[j] += 1;
    });
    const mx = Math.max.apply(null, counts) || 1;
    s.domain([0, 12], [0, mx * 1.15]);
    s.grid(6, 4, {xtitle: '值', ytitle: '次數'});
    counts.forEach((c, j) => {
      const x0 = lo + (hi - lo) * j / k, x1 = lo + (hi - lo) * (j + 1) / k;
      s.add('rect', {x: s.X(x0) + 1, y: s.Y(c), width: Math.max(1, s.X(x1) - s.X(x0) - 2),
                     height: s.Y(0) - s.Y(c), fill: HC.tok.accent2, opacity: 0.9}, g);
      if (c > (counts[j - 1] || 0) && c > (counts[j + 1] || 0) && c >= mx * 0.35) peaks += 1;
    });
  } else {
    const bw = Math.max(0.15, w18bnK / 20);
    const xs = HC.stat.seq(lo, hi, 120);
    const ys = xs.map(x => HC.stat.mean(w18bnData.map(v => HC.stat.dnorm(x, v, bw))));
    const mx = Math.max.apply(null, ys) || 1;
    s.domain([0, 12], [0, mx * 1.15]);
    s.grid(6, 4, {xtitle: '值', ytitle: '密度', ydec: 2});
    s.poly(xs.map((x, i) => [x, ys[i]]), {cls: 'kdeline', stroke: HC.tok.accent2, sw: 3}, g);
    for (let i = 1; i < ys.length - 1; i++) {
      if (ys[i] > ys[i - 1] && ys[i] > ys[i + 1] && ys[i] >= mx * 0.35) peaks += 1;
    }
  }
  document.getElementById('w18bnMode').textContent = w18bnKde ? '密度圖' : '直方圖';
  document.getElementById('w18bnParam').textContent = w18bnKde
    ? '頻寬 ' + HC.fmt(Math.max(0.15, w18bnK / 20), 2) : String(w18bnK);
  document.getElementById('w18bnPeaks').textContent = peaks + ' 個峰';
  setStatus('w18bnStatus', peaks >= 2
    ? '看得到 <b>' + peaks + '</b> 個峰。這份資料本來就是兩群造出來的。'
    : '只看得到 <b>' + peaks + '</b> 個峰：參數把真正的兩群<b>糊掉了</b>。');
}
function w18bnStep(d) { w18bnK = Math.max(4, Math.min(40, w18bnK + d)); w18bnDraw(); }
function w18bnMode() { w18bnKde = !w18bnKde; w18bnDraw(); }
function w18bnReset() { w18bnK = 10; w18bnKde = false; w18bnDraw(); }
if (w18bnS) w18bnDraw();

/* ═══ w18pk 圖型選擇決策樹 ═══ */
const w18pkS = HC.svg('w18pickSvg', {h: 340});
const w18pkCases = [
  {k: '散佈圖', f: 'scatterplot / relplot', q: '兩個數值變數之間有沒有關係、什麼形狀',
   draw: 'scatter'},
  {k: '盒鬚圖／長條圖／點估計圖', f: 'catplot(kind="box"/"bar"/"point")',
   q: '各組的分布或平均差多少', draw: 'box'},
  {k: '計數的交叉表＋熱圖', f: 'heatmap(pd.crosstab(...))',
   q: '兩個類別變數的組合各有幾筆', draw: 'heat'},
  {k: '直方圖／密度圖', f: 'histplot / kdeplot', q: '這個變數的分布長什麼樣', draw: 'hist'},
  {k: '折線圖＋信賴帶', f: 'lineplot', q: '隨時間怎麼變、變化有多確定', draw: 'line'}
];
let w18pkI = 0;
function w18pkDraw() {
  const s = w18pkS;
  s.domain([0, 10], [0, 10]);
  const g = s.clearLayer('main');
  const c = w18pkCases[w18pkI];
  s.grid(5, 5, {});
  const rand = HC.stat.lcg(7);
  if (c.draw === 'scatter') {
    for (let i = 0; i < 40; i++) {
      const x = rand() * 9 + 0.5;
      s.dot(x, Math.max(0.4, Math.min(9.6, x * 0.8 + HC.stat.normal(rand) * 1.2)),
            {r: 4, fill: HC.tok.accent2}, g);
    }
  } else if (c.draw === 'box') {
    [[2, 3, 5, 7], [5, 4.2, 6, 8], [8, 2.6, 4.4, 6.4]].forEach(b => {
      s.box(b[0] - 0.7, b[1], b[0] + 0.7, b[3],
            {fill: HC.tok.accent2, stroke: HC.tok.ink, sw: 1.5, rx: 3}, g);
      s.seg(b[0] - 0.7, b[2], b[0] + 0.7, b[2], {cls: 'med', stroke: HC.tok.paper, sw: 3}, g);
    });
  } else if (c.draw === 'heat') {
    for (let r = 0; r < 3; r++) {
      for (let k = 0; k < 3; k++) {
        s.box(1 + k * 2.6, 1 + r * 2.6, 3.4 + k * 2.6, 3.4 + r * 2.6,
              {fill: HC.tok.accent2, rx: 3}, g).setAttribute('opacity',
                String(0.25 + 0.22 * ((r * 3 + k) % 4)));
      }
    }
  } else if (c.draw === 'hist') {
    [1.2, 2.6, 4.8, 7.4, 8.6, 6.2, 3.4, 1.6].forEach((h, i) => {
      s.box(0.6 + i * 1.15, 0, 1.65 + i * 1.15, h,
            {fill: HC.tok.accent2, rx: 2}, g);
    });
  } else {
    const pts = HC.stat.seq(0.4, 9.6, 40).map(x => [x, 5 + 2.6 * Math.sin(x / 1.6)]);
    s.area(pts.map(p => [p[0], p[1] + 0.9, p[1] - 0.9]),
           {fill: HC.tok.accent2, cls: 'bandx'}, g).setAttribute('opacity', '0.25');
    s.poly(pts, {cls: 'lineq', stroke: HC.tok.accent2, sw: 3}, g);
  }
  document.getElementById('w18pkKind').textContent = c.k;
  document.getElementById('w18pkFn').textContent = c.f;
  document.getElementById('w18pkQ').textContent = c.q;
  setStatus('w18pkStatus', '建議：<b>' + c.k + '</b>（' + c.f + '）。');
}
function w18pkSet(i) { w18pkI = i; w18pkDraw(); }
if (w18pkS) w18pkDraw();
"""

PAGEJS += r"""
/* ═══ w18ms 截斷 y 軸 ═══ */
const w18msS = HC.svg('w18misSvg', {h: 340});
const w18msGroups = [[1.4, 2.4, 3.0, 4.2, 3.9], [1.6, 2.7, 3.3, 4.6, 4.1]];
const w18msVals = w18msGroups.map(xs => HC.stat.mean(xs));
function w18msFive(xs) {
  const s = xs.slice().sort((a, b) => a - b);
  return [s[0], HC.stat.quantile(s, 0.25), HC.stat.quantile(s, 0.5),
          HC.stat.quantile(s, 0.75), s[s.length - 1]];
}
let w18msI = 0;
function w18msDraw() {
  const s = w18msS;
  const g = s.clearLayer('main');
  document.getElementById('w18msA').textContent = HC.fmt(w18msVals[0], 2);
  document.getElementById('w18msB').textContent = HC.fmt(w18msVals[1], 2);
  if (w18msI === 2) {
    s.domain([0, 3], [0, 5]);
    s.grid(3, 5, {ytitle: '小費', ydec: 1});
    w18msGroups.map((xs, i) => [i + 1].concat(w18msFive(xs))).forEach((b, i) => {
      s.box(b[0] - 0.28, b[2], b[0] + 0.28, b[4],
            {fill: i === 0 ? HC.tok.accent2 : HC.tok.accent, stroke: HC.tok.ink,
             sw: 1.5, rx: 3}, g);
      s.seg(b[0] - 0.28, b[3], b[0] + 0.28, b[3], {cls: 'medx', stroke: HC.tok.paper, sw: 3}, g);
      s.seg(b[0], b[1], b[0], b[2], {cls: 'whx', stroke: HC.tok.ink, sw: 1.5}, g);
      s.seg(b[0], b[4], b[0], b[5], {cls: 'whx', stroke: HC.tok.ink, sw: 1.5}, g);
      s.txt(b[0], -0.35, i === 0 ? 'A 組' : 'B 組', {cls: 'axlab'}, g);
    });
    document.getElementById('w18msRatio').textContent = '看得到重疊';
    setStatus('w18msStatus', '盒鬚圖：兩組的分布<b>大幅重疊</b>——'
              + '長條圖的「差距」其實被個體差異淹沒了。');
    return;
  }
  const y0 = w18msI === 0 ? 0 : Math.min.apply(null, w18msVals) - 0.08;
  s.domain([0, 3], [y0, 3.4]);
  s.grid(3, 5, {ytitle: '平均小費', ydec: 2});
  w18msVals.forEach((v, i) => {
    s.box(i + 0.72, y0, i + 1.28, v,
          {fill: i === 0 ? HC.tok.accent2 : HC.tok.accent, rx: 3}, g);
    s.txt(i + 1, y0 + (3.4 - y0) * 0.03, i === 0 ? 'A 組' : 'B 組',
          {cls: 'axlab', dy: 16}, g);
  });
  const hA = w18msVals[0] - y0, hB = w18msVals[1] - y0;
  document.getElementById('w18msRatio').textContent =
    w18msI === 0 ? HC.fmt(hB / hA, 2) + ' 倍' : HC.fmt(hB / hA, 1) + ' 倍（假的）';
  setStatus('w18msStatus', w18msI === 0
    ? 'y 軸從 0 開始：兩根長條幾乎一樣高，平均差距約 <b>'
      + HC.fmt((w18msVals[1] / w18msVals[0] - 1) * 100, 1) + '%</b>。'
    : '同樣的兩個數字，截斷之後看起來差 <b>' + HC.fmt(hB / hA, 1) + ' 倍</b>——數字沒變，圖說謊了。');
}
function w18msSet(i) { w18msI = i; w18msDraw(); }
if (w18msS) w18msDraw();

/* ═══ w18cr 相關係數熱圖 ═══ */
const w18crS = HC.svg('w18corrSvg', {h: 340});
const w18crNames = ['total_bill', 'tip', 'size'];
const w18crM = [[1.00, 0.68, 0.60], [0.68, 1.00, 0.49], [0.60, 0.49, 1.00]];
let w18crI = 1;
function w18crRead(v) {
  if (v >= 0.99) return '自己跟自己，一定是 1';
  if (v >= 0.6) return '中等偏強的正相關';
  if (v >= 0.3) return '中等的正相關';
  return '弱相關';
}
function w18crDraw() {
  const g = w18crS.clearLayer('main');
  const cell = 82, x0 = 190, y0 = 78;
  const r0 = Math.floor(w18crI / 3), c0 = w18crI % 3;
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      const v = w18crM[r][c], on = (r === r0 && c === c0);
      w18crS.add('rect', {x: x0 + c * cell, y: y0 + r * cell, width: cell - 4,
                          height: cell - 4, rx: 4, fill: HC.tok.accent2,
                          opacity: 0.15 + 0.8 * v,
                          stroke: on ? HC.tok.ink : 'none', 'stroke-width': on ? 3 : 0}, g);
      const t = w18crS.add('text', {x: x0 + c * cell + (cell - 4) / 2,
                                    y: y0 + r * cell + (cell - 4) / 2 + 5,
                                    'text-anchor': 'middle', cls: 'vlab',
                                    'font-family': HC.MONO,
                                    fill: v > 0.6 ? HC.tok.paper : HC.tok.ink}, g);
      t.textContent = HC.fmt(v, 2);
    }
    const rl = w18crS.add('text', {x: x0 - 12, y: y0 + r * cell + (cell - 4) / 2 + 5,
                                   'text-anchor': 'end', cls: 'axlab'}, g);
    rl.textContent = w18crNames[r];
    const cl = w18crS.add('text', {x: x0 + r * cell + (cell - 4) / 2, y: y0 - 12,
                                   'text-anchor': 'middle', cls: 'axlab'}, g);
    cl.textContent = w18crNames[r];
  }
  w18crS.txtPx(24, 40, 'sns.heatmap(tips.corr(numeric_only=True))', {cls: 'axtitle'}, g);
  const v = w18crM[r0][c0];
  document.getElementById('w18crPair').textContent = w18crNames[r0] + ' × ' + w18crNames[c0];
  document.getElementById('w18crVal').textContent = HC.fmt(v, 2);
  document.getElementById('w18crRead').textContent = w18crRead(v);
  setStatus('w18crStatus', w18crNames[r0] + ' 與 ' + w18crNames[c0]
            + ' 的相關係數是 <b>' + HC.fmt(v, 2) + '</b>：' + w18crRead(v) + '。');
}
function w18crNext() { w18crI = (w18crI + 1) % 9; w18crDraw(); }
function w18crReset() { w18crI = 1; w18crDraw(); }
if (w18crS) w18crDraw();

/* ═══ w18sm Anscombe's quartet（Chart.js）═══ */
const w18smX = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5];
const w18smData = [
  [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
  [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
  [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
  [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]
];
function w18smMake(kind) {
  const xs = kind === 3 ? [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8] : w18smX;
  return xs.map((x, i) => ({x: x, y: w18smData[kind][i]}));
}
let w18smI = 0;
function w18smDraw() {
  const pts = w18smMake(w18smI);
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const r = (() => {
    const mx = HC.stat.mean(xs), my = HC.stat.mean(ys);
    let sxy = 0, sx = 0, sy = 0;
    for (let i = 0; i < xs.length; i++) {
      sxy += (xs[i] - mx) * (ys[i] - my);
      sx += (xs[i] - mx) ** 2; sy += (ys[i] - my) ** 2;
    }
    return sxy / Math.sqrt(sx * sy);
  })();
  document.getElementById('w18smMx').textContent = HC.fmt(HC.stat.mean(xs), 2);
  document.getElementById('w18smMy').textContent = HC.fmt(HC.stat.mean(ys), 2);
  document.getElementById('w18smSd').textContent = HC.fmt(HC.stat.sd(xs), 2)
    + ' ／ ' + HC.fmt(HC.stat.sd(ys), 2);
  document.getElementById('w18smR').textContent = HC.fmt(r, 2);
  const fit = HC.stat.ols(xs, ys);
  document.getElementById('w18smLine').textContent = 'ŷ = ' + HC.fmt(fit.b0, 2)
    + ' + ' + HC.fmt(fit.b1, 2) + 'x';
  const names = ['近似線性', '明顯曲線', 'y 方向離群值', '高槓桿點'];
  setStatus('w18smStatus', '第 ' + (w18smI + 1) + ' 組（' + names[w18smI]
            + '）：x̄ ≈ ' + HC.fmt(HC.stat.mean(xs), 1) + '、ȳ ≈ '
            + HC.fmt(HC.stat.mean(ys), 1) + '、r ≈ ' + HC.fmt(r, 2) + '。');
  if (!HC.hasChart()) return;
  const c = HC.get('w18sameChart');
  if (c) { c.data.datasets[0].data = pts; c.update(); return; }
  HC.scatter('w18sameChart', {
    datasets: [{label: '觀測值', data: pts, backgroundColor: HC.tok.accent2,
                pointRadius: 5}]
  }, {
    scales: {x: {title: {display: true, text: 'x'}, min: 0, max: 20},
             y: {title: {display: true, text: 'y'}, min: 0, max: 14}},
    plugins: {legend: {display: false}}
  });
}
function w18smSet(i) { w18smI = i; w18smDraw(); }
HC.ready(() => { w18smDraw(); });
"""

apply("p5_visualization", BODIES, PAGEJS)
