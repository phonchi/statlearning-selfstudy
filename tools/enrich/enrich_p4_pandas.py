#!/usr/bin/env python3
"""p4_pandas.html（先備 P4 · pandas 資料框）完整自學充實。冪等。

內容依據：Ch01-lab-zh.ipynb（Series／DataFrame／檢視／選取／分組／串接）
與 Ch02-statlearn-lab-zh.ipynb 儲存格 185–199（Auto 的遺漏值那條線）。
所有程式碼與預期輸出逐字取自 lab，一格都沒有重跑。

規格見 tools/STYLE_CONTRACT.md §9。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LAB1 = "Ch01-lab-zh.ipynb"
LAB2 = "Ch02-statlearn-lab-zh.ipynb"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB1 if ch == 1 else LAB2
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE Series 與 DataFrame ───────────────────────────────────────
BODIES["prologue"] = f"""
  <p>NumPy 的陣列只有數字，沒有欄名。真實資料不是這樣。你會想說「取 mpg 那一欄」，
  而不是「取第 3 欄」。pandas 就是在陣列上面加了一層<strong>標籤</strong>：
  一維的叫 Series，二維的叫 DataFrame。</p>

{info("一句話", "<strong>Series ≈ 有索引的一維陣列</strong>，"
      "<strong>DataFrame ≈ 共用同一個索引的一疊 Series</strong>。"
      "底下算數字的還是 NumPy。")}

{viz(svg("w17serSvg", 320),
     [info_card("三種東西的關係",
                "按按鈕切換。字典的鍵變成索引、值變成資料；"
                "幾個 Series 疊起來、共用同一個索引，就是 DataFrame。"),
      rows_card("目前",
                [("型別", "Series", "w17serType"),
                 ("索引", "d b a c", "w17serIdx"),
                 ("dtype", "int64", "w17serDtype")]),
      info_card("每一欄可以是不同型別",
                "DataFrame 的 <code>dtypes</code> 是<strong>逐欄</strong>的："
                "state 是 object、year 是 int64、pop 是 float64。"
                "這一點跟 NumPy 陣列不同——陣列整塊只能有一個型別。")],
     "w17serStatus", "從字典開始，看它怎麼變成 Series 再變成 DataFrame。",
     '<button class="btn btn-toggle" onclick="w17serSet(0)">Python 字典</button>'
     '<button class="btn btn-toggle" onclick="w17serSet(1)">Series</button>'
     '<button class="btn btn-toggle" onclick="w17serSet(2)">DataFrame</button>',
     provenance=("course-data", "依 Ch01 lab 的 Series 與 DataFrame 建構結果重繪。"))}

{card("自訂索引的 Series", C(1, 17), O(1, 17), src=S(1, 17),
      note="左邊那一排 <code>d b a c</code> 是索引，不是資料。")}

{card("用字典建 DataFrame", C(1, 26), O(1, 26), src=S(1, 26),
      note="鍵變成欄名，值變成那一欄的內容。列索引沒指定時就是 0、1、2…")}

{card("每一欄各自的型別", C(1, 28), O(1, 28), src=S(1, 28))}

{quiz("qSer", "PART 00 · 自我檢測",
      "<code>frame['pop']</code> 拿到的是什麼？",
      [(False, "一個 NumPy 陣列",
        "很接近但不精確。底下確實是 NumPy 陣列，但你拿到的是包了一層索引的 "
        "<strong>Series</strong>。要真的拿陣列得再 <code>.to_numpy()</code>。"),
       (True, "一個 Series，帶著原本的列索引",
        "對。這就是為什麼 <code>frame['pop'] &gt; 2</code> 的結果也帶索引，"
        "可以直接拿回去索引原本的表。"),
       (False, "一個 DataFrame，只有一欄",
        "不是。用單一個字串取欄拿到的是 Series；"
        "要拿只有一欄的 DataFrame 得寫 <code>frame[['pop']]</code>（雙層中括號）。")])}
"""

# ── P01 檢視與摘要 ──────────────────────────────────────────────────────
BODIES["view"] = f"""
  <p>拿到一份沒看過的資料，前五分鐘不要急著建模。先跑這四行：
  <code>shape</code> 看有多大、<code>head()</code> 看長什麼樣、
  <code>describe()</code> 看數值範圍合不合理、<code>dtypes</code> 看有沒有欄被讀成字串。
  第四項最常出事，下一節會看到。</p>

{viz(svg("w17peekSvg", 300),
     [info_card("四行指令各自告訴你什麼",
                "按按鈕，看每一行揭露的是哪一塊資訊。"
                "四個都看完才算「認識」了這份資料。"),
      rows_card("這一行告訴你",
                [("指令", "df.shape", "w17peekCmd"),
                 ("揭露什麼", "資料有多大", "w17peekWhat"),
                 ("看到什麼要警覺", "列數比預期少很多", "w17peekWarn")]),
      info_card("順序有意義",
                "先 <code>shape</code> 再 <code>dtypes</code>——"
                "型別錯了的話，後面 <code>describe()</code> 的數字全部不能信。")],
     "w17peekStatus", "四行指令，按順序看過一遍。",
     '<button class="btn btn-toggle" onclick="w17peekSet(0)">df.shape</button>'
     '<button class="btn btn-toggle" onclick="w17peekSet(1)">df.head()</button>'
     '<button class="btn btn-toggle" onclick="w17peekSet(2)">df.dtypes</button>'
     '<button class="btn btn-toggle" onclick="w17peekSet(3)">df.describe()</button>',
     provenance=("course-data", "依 Ch01 lab 的資料檢視指令與輸出重繪。"))}

{card("看前幾列與後幾列", C(1, 31) + "\n" + C(1, 32), f"{O(1, 31)}\n{O(1, 32)}",
      src=S(1, 31, 32), note="<code>head()</code> 預設五列，<code>tail(3)</code> 給最後三列。")}

{card("五數摘要", C(1, 36), O(1, 36), src=S(1, 36),
      note="<code>count</code> 那一列很有用。它<strong>不算遺漏值</strong>，"
           "所以某一欄的 count 比別欄少，就代表那欄有 NaN。")}

{card("形狀", C(1, 38), O(1, 38), src=S(1, 38),
      note="跟 NumPy 一樣是 <code>(列數, 欄數)</code>。")}

{qa("觀念釐清", [
    ("<code>describe()</code> 為什麼漏掉某些欄？",
     "它預設只算數值欄。如果你期待的欄沒出現，那一欄多半被讀成了字串（object）——"
     "這正是下一節 Auto 的 horsepower 會遇到的事。加 "
     "<code>describe(include='all')</code> 可以連類別欄一起看。"),
    ("<code>count</code> 跟 <code>len(df)</code> 差在哪？",
     "<code>len(df)</code> 是列數，<code>count</code> 是<strong>非遺漏</strong>的個數。"
     "兩個數字不一樣，就代表那一欄有 NaN。這是最快的遺漏值偵測法。"),
])}

{quiz("qView", "PART 01 · 自我檢測",
      "<code>df.describe()</code> 的輸出裡，某一欄的 <code>count</code> 是 380，"
      "但 <code>df.shape</code> 是 <code>(392, 9)</code>。這代表什麼？",
      [(True, "那一欄有 12 個遺漏值",
        "對。<code>count</code> 只算非 NaN 的個數，392 − 380 = 12。"
        "這是最快發現遺漏值的方式，比一欄一欄 <code>isna().sum()</code> 快。"),
       (False, "資料只有 380 列，shape 印錯了",
        "不會。<code>shape</code> 是實際的列數，不受遺漏值影響。"
        "兩個數字不一致本身就是資訊，不是錯誤。"),
       (False, "那一欄有 12 個重複值",
        "重複值不影響 <code>count</code>。要看重複得用 "
        "<code>duplicated()</code> 或 <code>value_counts()</code>。")])}
"""

# ── P02 選取列與欄 ──────────────────────────────────────────────────────
BODIES["select"] = f"""
  <p>pandas 有兩套選取語法，混用是新手最大的痛苦來源。規則其實只有一句：
  <strong><code>loc</code> 靠名字、<code>iloc</code> 靠位置</strong>。
  剩下的差別都是從這一句推出來的。</p>

{info("最容易咬人的一條",
      "<code>loc</code> 的切片<strong>包含</strong>結尾，<code>iloc</code> 不包含。"
      "<code>df.loc['a':'c']</code> 會拿到 c，<code>df.iloc[0:3]</code> 只拿到 0、1、2。"
      "因為名字沒有「下一個」可言，含頭不含尾對它沒有意義。", "warm")}

{viz(svg("w17selSvg", 340),
     [info_card("按按鈕比較",
                "同一張表、四種寫法。亮起來的是被選到的格子，"
                "下面會顯示這個寫法拿到的是 DataFrame 還是 Series。"),
      rows_card("目前",
                [("寫法", "df[\\'A\\']", "w17selExpr"),
                 ("拿到的型別", "Series", "w17selType"),
                 ("形狀", "(6,)", "w17selShape")]),
      info_card("那 df[…] 直接寫呢",
                "<code>df['A']</code> 取的是<strong>欄</strong>，"
                "但 <code>df[0:3]</code> 取的是<strong>列</strong>——"
                "同一個中括號，兩種意思。這就是為什麼建議一律用 "
                "<code>loc</code>／<code>iloc</code> 寫清楚。")],
     "w17selStatus", "先猜哪幾格會亮，再按。",
     '<button class="btn btn-toggle" onclick="w17selSet(0)">df[&quot;A&quot;]</button>'
     '<button class="btn btn-toggle" onclick="w17selSet(1)">df[0:3]</button>'
     '<button class="btn btn-toggle" onclick="w17selSet(2)">df.loc[:, [&quot;A&quot;,&quot;C&quot;]]</button>'
     '<button class="btn btn-toggle" onclick="w17selSet(3)">df.iloc[3]</button>'
     '<button class="btn btn-toggle" onclick="w17selSet(4)">df[df[&quot;A&quot;]&gt;0]</button>',
     provenance=("course-data", "依 Ch01 lab 的示範 DataFrame 與 loc／iloc 選取結果重繪。"))}

{card("取一欄與取幾列", C(1, 45) + "\n" + C(1, 47), f"{O(1, 45)}\n{O(1, 47)}",
      src=S(1, 45, 47),
      note="注意兩者的差別：<code>df['A']</code> 給 Series，<code>df[0:3]</code> 給 DataFrame。")}

{card("loc 指名字、iloc 指位置", C(1, 50) + "\n" + C(1, 53), f"{O(1, 50)}\n{O(1, 53)}",
      src=S(1, 50, 53),
      note="<code>df.iloc[3]</code> 拿一整列，回來的是 Series——"
           "那一列的欄名變成了它的索引。")}

{card("用條件選列", C(1, 56), O(1, 56), src=S(1, 56),
      note="裡面的 <code>df['A'] &gt; 0</code> 就是 P3 講的布林遮罩，"
           "只是現在它帶著索引。")}

{quiz("qSel", "PART 02 · 自我檢測",
      "<code>df.loc['b':'d']</code> 與 <code>df.iloc[1:3]</code>，哪一個的敘述正確？",
      [(False, "兩個都不包含結尾",
        "只對了一半。<code>iloc</code> 確實不含結尾，但 <code>loc</code> 是<strong>含</strong>的。"),
       (True, "<code>loc</code> 會拿到 d，<code>iloc</code> 只拿到位置 1 和 2",
        "對。<code>loc</code> 用名字，名字沒有「下一個」的概念，所以含頭含尾；"
        "<code>iloc</code> 用位置，跟 Python 切片一致，含頭不含尾。"),
       (False, "兩個都包含結尾",
        "不是。<code>iloc</code> 就是一般的位置切片，"
        "<code>df.iloc[1:3]</code> 只有兩列。")])}

{hook("這在本站哪一章會用到",
      '第 3 章把類別變數放進迴歸、第 4 章切出訓練與測試集，'
      '用的都是這一節的選取語法。'
      '<a href="linear_regression.html#qualitative">→ 線性迴歸 · 類別型預測變數</a>')}
"""

# ── P03 遺漏值 ─────────────────────────────────────────────────────────
BODIES["na"] = f"""
  <p>這一節講一個真實故事。課程 lab 讀進 <code>Auto</code> 之後，
  <code>horsepower</code> 那一欄<strong>整欄是字串</strong>，因為原始檔用 <code>?</code>
  代表遺漏，pandas 看到問號就把整欄當成文字。這種錯誤不會報錯，只會讓你後面算出來的東西全錯。</p>

{viz(svg("w17naSvg", 340),
     [info_card("四個步驟",
                "按「單步」走一次：發現整欄是字串 → 找出兇手是 <code>?</code> → "
                "在<strong>讀檔時</strong>就宣告它是遺漏 → 決定要不要 dropna。"),
      rows_card("目前",
                [("步驟", "0 / 4", "w17naStep"),
                 ("horsepower 的型別", "object（字串）", "w17naType"),
                 ("列數", "397", "w17naRows")]),
      info_card("為什麼要在讀檔時處理",
                "讀進來之後才發現，你得自己寫 <code>replace</code> 再 "
                "<code>astype(float)</code>，很容易漏掉某些欄。"
                "<code>na_values=['?']</code> 一次解決，而且下次重跑也不會忘。")],
     "w17naStatus", "按「單步」看整件事怎麼發生、怎麼修。",
     '<button class="btn btn-step" onclick="w17naStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w17naReset()">重置</button>',
     provenance=("course-data", "依 Ch02 lab 的 Auto.data 讀檔、? 遺漏值與 397→392 列流程重繪。"))}

{card("找出兇手", C(2, 192), O(2, 192), src=S(2, 192),
      note="全部是<strong>帶引號的字串</strong>，輸出末尾就會看到那個 "
           "<code>'?'</code>。整欄因此被讀成 object。")}

{card("讀檔時就宣告哪些字算遺漏", C(2, 195), O(2, 195), src=S(2, 195),
      note="加上 <code>na_values=['?']</code> 之後，"
           "<code>sum()</code> 才算得出數字。那個 <code>np.float64</code> 就是證據。")}

{card("dropna：397 變成 392", C(2, 197) + "\n" + C(2, 199), f"{O(2, 197)}\n{O(2, 199)}",
      src=S(2, 197, 199),
      note="整門課後面用的 <code>Auto</code> 都是這 392 筆。"
           "你在課本裡看到的 n=392 就是從這裡來的。")}

{card("reindex 也會生出 NaN", C(1, 61), O(1, 61), src=S(1, 61),
      note="索引裡多了一個 <code>e</code>，原本沒有這一筆，pandas 就填 NaN。"
           "遺漏值不是只有讀檔會產生。")}

{table(["做法", "什麼時候用", "風險"],
       [["<code>na_values=[…]</code>（讀檔時）", "原始檔用特殊符號表示遺漏", "幾乎沒有，應該是預設動作"],
        ["<code>dropna()</code>", "遺漏很少、而且看起來是隨機遺漏", "遺漏不是隨機時會產生偏差"],
        ["<code>fillna(中位數)</code>", "想保留樣本數", "低估變異、稀釋相關性"],
        ["當成一個類別（缺失指示變數）", "「有沒有填」本身帶資訊", "多一個參數"]])}

{quiz("qNa", "PART 03 · 自我檢測",
      "<code>Auto['horsepower'].mean()</code> 在<strong>沒有</strong>加 "
      "<code>na_values=['?']</code> 的情況下會發生什麼？",
      [(False, "自動忽略問號，算出正確的平均",
        "不會。pandas 不知道 <code>?</code> 是遺漏，它只看到一欄字串。"),
       (True, "報錯或算出無意義的結果，因為整欄是字串",
        "對。這是最危險的一種錯誤——<strong>你以為在算平均，其實那一欄根本不是數字</strong>。"
        "所以拿到資料先看 <code>dtypes</code>。"),
       (False, "把問號當成 0 來算",
        "不會。pandas 不會擅自把字串轉成數字，"
        "它的選擇是把整欄保持成 object。")])}
"""

# ── P04 分組彙總 ────────────────────────────────────────────────────────
BODIES["group"] = f"""
  <p><code>groupby</code> 是 pandas 最有價值的一個動作，而它其實是三件事連在一起：
  <strong>拆分</strong>（照某一欄的值把列分堆）→ <strong>套用</strong>（每一堆各算一次）→
  <strong>合併</strong>（把結果疊回一張表）。看懂這三步，所有變形都是同一件事。</p>

{viz(svg("w17grpSvg", 340),
     [info_card("三個動作",
                "按「單步」看拆分、套用、合併。注意<strong>分組的鍵會變成新的索引</strong>——"
                "這就是為什麼結果只剩兩列。"),
      rows_card("目前",
                [("步驟", "0 / 3", "w17grpStep"),
                 ("組數", "—", "w17grpN"),
                 ("結果形狀", "—", "w17grpShape")]),
      info_card("numeric_only=True 是什麼",
                "有些欄是字串，加總沒有意義。"
                "<code>sum(numeric_only=True)</code> 明講「只算數值欄」，"
                "不寫的話新版 pandas 會警告。")],
     "w17grpStatus", "按「單步」把 groupby 拆成三個動作看。",
     '<button class="btn btn-step" onclick="w17grpStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w17grpPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w17grpReset()">重置</button>',
     provenance=("course-data", "依 Ch01 lab 儲存格 78 的 groupby 拆分、套用、合併流程重繪。"))}

{card("先數一數每一類有幾筆", C(1, 76), O(1, 76), src=S(1, 76),
      note="<code>value_counts()</code> 是拿到類別欄的第一個動作。"
           "某一類只有兩三筆的話，後面做分類會很吃力。")}

{card("拆分 → 套用 → 合併", C(1, 78), O(1, 78), src=S(1, 78),
      note="<code>A</code> 從一般的欄變成了<strong>索引</strong>，"
           "所以輸出裡它單獨一行、下面是 bar 與 foo。")}

{viz(chart("w17grpChart", fallback="：foo 那一組的 C 欄總和是負的、bar 是正的——"
                                  "分組之後兩組的方向相反。"),
     [info_card("同一份結果換一種看法",
                "上面那張表的四個數字畫成長條圖。"
                "分組彙總之後<strong>先畫圖再下結論</strong>，"
                "數字表很容易看漏正負號。"),
      info_card("這些數字哪裡來的",
                "逐字取自 lab 儲存格 78 的輸出，沒有重跑。"
                "本站所有圖表的數字都可以這樣追回來源。")],
     "w17grpStatus2", "bar 與 foo 兩組在 C 欄的方向相反。",
     '<button class="btn btn-toggle" onclick="w17grpCol(&quot;C&quot;)">看 C 欄</button>'
     '<button class="btn btn-toggle" onclick="w17grpCol(&quot;D&quot;)">看 D 欄</button>',
     provenance=("course-data", "圖中數值逐項取自 Ch01 lab 儲存格 78 的 groupby 輸出。"))}

{quiz("qGrp", "PART 04 · 自我檢測",
      "<code>df.groupby('A').sum()</code> 之後，欄 <code>A</code> 跑去哪了？",
      [(False, "還在，只是移到最後一欄",
        "不是。分組之後 <code>A</code> 不再是一般的欄。"),
       (True, "變成結果的索引",
        "對。所以要把它變回一般的欄得寫 <code>.reset_index()</code>，"
        "或一開始就寫 <code>groupby('A', as_index=False)</code>。"
        "很多「欄名找不到」的錯誤都出在這裡。"),
       (False, "被刪掉了，因為字串不能加總",
        "不對。它沒有被加總，是因為它是<strong>分組的鍵</strong>，"
        "不是被當成資料處理。")])}
"""

# ── P05 串接與讀寫 ──────────────────────────────────────────────────────
BODIES["join"] = f"""
  <p>最後兩件雜事：把切開的表接回去，以及讀檔。讀檔看起來最無聊，
  但上一節那個 <code>?</code> 的災難就是讀檔沒設好造成的——
  <strong>讀檔的參數決定你後面有多痛</strong>。</p>

{card("切成三塊再接回去", C(1, 71), O(1, 71), src=S(1, 71),
      note="切片給的是三個 DataFrame，裝在一個串列裡。")}

{card("concat 沿著列接起來", C(1, 72), O(1, 72), src=S(1, 72),
      note="接回去之後跟原本一模一樣。"
           "注意註解裡那句話：<strong>加一欄很快，加一列要複製整張表</strong>——"
           "所以不要在迴圈裡一列一列 append。")}

{card("讀檔的參數才是重點", C(2, 195), O(2, 195), src=S(2, 195),
      note="<code>sep=r&quot;\\s+&quot;</code> 是「一個以上的空白當分隔」，"
           "<code>na_values</code> 是「這些字算遺漏」。"
           "這一行寫對，後面少掉一整輪除錯。")}

{viz(svg("w17catSvg", 320),
     [info_card("疊回去",
                "三塊各自是完整的 DataFrame，欄名一樣，"
                "<code>concat</code> 沿著<strong>列</strong>把它們接起來。"),
      rows_card("目前",
                [("步驟", "0 / 3", "w17catStep"),
                 ("已接上的列數", "0", "w17catRows")]),
      info_card("axis=1 呢",
                "沿欄接：列索引要對得起來，接完欄變多。"
                "對不起來的位置會填 NaN。這是最容易產生意外遺漏值的操作。")],
     "w17catStatus", "按「單步」把三塊接回去。",
     '<button class="btn btn-step" onclick="w17catStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w17catReset()">重置</button>',
     provenance=("course-data", "依 Ch01 lab 的 DataFrame 分塊與 concat 範例重繪。"))}

{qa("觀念釐清", [
    ("<code>concat</code> 跟 <code>merge</code> 差在哪？",
     "<code>concat</code> 是<strong>疊</strong>：形狀相容就沿著某個軸接起來，"
     "預設沿列（axis=0）。<code>merge</code> 是<strong>對</strong>：照某個鍵把兩張表配對，"
     "像 SQL 的 join。本課的 lab 主要用 concat，但實務上 merge 更常見。"),
    ("為什麼不要在迴圈裡一列一列加？",
     "DataFrame 的欄是連續存放的，加一列等於整張表複製一次。"
     "一萬列就複製一萬次。正確做法是把每一塊放進 Python 串列，"
     "最後 <code>pd.concat(串列)</code> 一次接完。"),
])}

{quiz("qJoin", "PART 05 · 自我檢測",
      "你要把 500 個小 DataFrame 合成一張大表。哪一種寫法對？",
      [(False, "在 for 迴圈裡 <code>big = pd.concat([big, small])</code>",
        "能跑，但每一輪都複製整張大表，500 次下來會慢得離譜。"
        "這是很經典的效能陷阱。"),
       (True, "全部收進一個串列，最後 <code>pd.concat(串列)</code> 一次接完",
        "對。只複製一次。lab 儲存格 71–72 示範的就是這個形式："
        "先做出 <code>pieces</code> 這個串列，再一次 concat。"),
       (False, "用 <code>merge</code> 兩兩合併",
        "<code>merge</code> 是照鍵配對，不是疊起來，用在這裡是錯的工具。")])}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 讀檔",
      "某個 CSV 用 <code>NA</code> 與 <code>-999</code> 兩種方式表示遺漏。最好的處理時機是？",
      [(True, "讀檔時寫 <code>na_values=['NA', -999]</code>",
        "對。一次講清楚，之後每一次重跑都一致。"
        "Auto 那個 <code>?</code> 的教訓就是這個，讀進來之後才補救，"
        "很容易漏掉某些欄。"),
       (False, "讀完之後用 <code>replace</code> 換掉",
        "能做，但每加一個欄就要記得改一次，而且中間那段時間欄的型別是錯的。"
        "更糟的是別人重跑你的程式碼時可能漏掉這一步。"),
       (False, "建模前再用 <code>dropna()</code> 一次處理",
        "太晚了。<code>dropna</code> 只認得 NaN——"
        "<code>-999</code> 在它眼裡是一個正常的數字，會被留下來一路算進模型。")])}

{quiz("qEx2", "EXERCISE 2 · loc 與 iloc",
      "<code>df</code> 的索引是日期。想拿「第 3 到第 5 列」，正確的寫法是？",
      [(False, "<code>df.loc[3:5]</code>",
        "會出事。索引是日期，<code>loc</code> 會去找名字叫 <code>3</code> 的那一列，"
        "找不到就報錯（或在某些舊版本悄悄退回位置解讀，更可怕）。"),
       (True, "<code>df.iloc[2:5]</code>",
        "對。要用位置就用 <code>iloc</code>；而且「第 3 到第 5 列」"
        "換成 0 起算的位置是 2、3、4，所以是 <code>2:5</code>。"),
       (False, "<code>df[3:5]</code>",
        "這個確實會被解讀成位置切片，但只拿到兩列（位置 3、4），而且"
        "<strong>同一個中括號在取欄時又是另一個意思</strong>，容易誤讀。"
        "寫 <code>iloc</code> 比較清楚。")])}

{quiz("qEx3", "EXERCISE 3 · groupby",
      "想得到「每個 <code>origin</code> 的平均 <code>mpg</code>」，而且結果要是一張"
      "有 <code>origin</code> 欄的普通表，怎麼寫？",
      [(False, "<code>Auto.groupby('origin')['mpg'].mean()</code>",
        "算出來的數字是對的，但 <code>origin</code> 變成了索引，不是一般的欄——"
        "題目要的是「有 origin 欄的普通表」。"),
       (True, "<code>Auto.groupby('origin', as_index=False)['mpg'].mean()</code>",
        "對。<code>as_index=False</code>（或事後 <code>.reset_index()</code>）"
        "會把分組的鍵留成一般的欄。畫圖或再 merge 時都需要這個形式。"),
       (False, "<code>Auto[['origin', 'mpg']].mean()</code>",
        "這是把兩欄各自平均，完全沒有分組——"
        "會得到「origin 的平均值」這種沒有意義的數字。")])}

{quiz("qEx4", "EXERCISE 4 · 遺漏值的影響",
      "一份資料的收入欄有 20% 遺漏，而遺漏的多半是高收入的人。直接 <code>dropna()</code> 會怎樣？",
      [(False, "沒關係，只是樣本變小",
        "樣本變小只是表面。真正的問題是<strong>剩下的樣本不再代表原本的母體</strong>。"),
       (True, "剩下的樣本會系統性低估收入",
        "對。這叫非隨機遺漏。<code>dropna</code> 的前提是「遺漏跟你關心的變數無關」，"
        "這裡明顯不成立。至少要加一個「有沒有填」的指示變數，把這件事本身當資訊。"),
       (False, "pandas 會自動加權補償",
        "不會。<code>dropna</code> 就只是刪掉，沒有任何統計上的補償。"
        "怎麼處理是你的判斷，不是套件的。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張速查表。第一張是最常查的。</p>

{table(["你想做的事", "寫法", "拿到什麼"],
       [["取一欄", "<code>df['A']</code>", "Series"],
        ["取一欄但要 DataFrame", "<code>df[['A']]</code>", "DataFrame（一欄）"],
        ["取幾欄", "<code>df.loc[:, ['A','C']]</code>", "DataFrame"],
        ["取一列（照位置）", "<code>df.iloc[3]</code>", "Series（欄名變索引）"],
        ["取幾列（照位置）", "<code>df.iloc[1:4]</code>", "DataFrame，不含第 4"],
        ["取幾列（照名字）", "<code>df.loc['a':'c']</code>", "DataFrame，<b>含</b> c"],
        ["用條件選列", "<code>df[df['A'] &gt; 0]</code>", "DataFrame"],
        ["某一格", "<code>df.loc['a', 'A']</code>", "純量"]])}

{table(["拿到新資料的前五分鐘", "看什麼"],
       [["<code>df.shape</code>", "列數欄數跟預期一樣嗎"],
        ["<code>df.head()</code>", "欄名對嗎、有沒有整欄空白"],
        ["<code>df.dtypes</code>", "<b>該是數字的欄有沒有變成 object</b>"],
        ["<code>df.describe()</code>", "範圍合理嗎；count 比列數少就是有 NaN"],
        ["<code>df['類別欄'].value_counts()</code>", "有沒有哪一類只有兩三筆"]])}

{table(["groupby 的三個動作", "發生什麼"],
       [["拆分（split）", "照鍵的值把列分成幾堆"],
        ["套用（apply）", "每一堆各算一次彙總函式"],
        ["合併（combine）", "把結果疊成一張表，<b>鍵變成索引</b>"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 拿到資料先看 <code>dtypes</code>。</strong>"
      "該是數字的欄變成 object，代表原始檔裡有非數字的東西（例如 Auto 的 <code>?</code>）。<br>"
      "<strong>2. <code>loc</code> 靠名字、<code>iloc</code> 靠位置；<code>loc</code> 的切片含尾。</strong><br>"
      "<strong>3. groupby 之後鍵會變成索引。</strong>"
      "要它留在欄裡就 <code>as_index=False</code> 或 <code>reset_index()</code>。")}

{ver_note((1, 2))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
# SVG 的初始化一律放在 HC.ready() 外面（STYLE_CONTRACT §5）。
PAGEJS = r"""
/* 這一頁共用的小工具：畫一張表 */
function w17grid(s, g, opt) {
  const cols = opt.cols, rows = opt.rows, x0 = opt.x0, y0 = opt.y0;
  const cw = opt.cw || 82, chh = opt.chh || 30;
  cols.forEach((c, j) => {
    s.add('rect', {x: x0 + j * cw, y: y0, width: cw - 5, height: chh - 5, rx: 4,
                   fill: HC.tok.accent, opacity: 0.85}, g);
    const t = s.add('text', {x: x0 + j * cw + (cw - 5) / 2, y: y0 + 18,
                             'text-anchor': 'middle', cls: 'vlab',
                             'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = c;
  });
  rows.forEach((r, i) => {
    if (opt.index) {
      const it = s.add('text', {x: x0 - 10, y: y0 + (i + 1) * chh + 18,
                                'text-anchor': 'end', cls: 'axlab'}, g);
      it.textContent = opt.index[i];
    }
    r.forEach((v, j) => {
      const on = opt.sel ? opt.sel(i, j) : false;
      s.add('rect', {x: x0 + j * cw, y: y0 + (i + 1) * chh, width: cw - 5,
                     height: chh - 5, rx: 3,
                     fill: on ? HC.tok.accent2 : HC.tok.card,
                     stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                     opacity: on ? 1 : 0.5}, g);
      const t = s.add('text', {x: x0 + j * cw + (cw - 5) / 2, y: y0 + (i + 1) * chh + 18,
                               'text-anchor': 'middle', cls: 'vlab',
                               'font-family': HC.MONO,
                               fill: on ? HC.tok.paper : HC.tok.muted}, g);
      t.textContent = v;
    });
  });
}

/* ═══ w17ser 字典 → Series → DataFrame ═══ */
const w17serS = HC.svg('w17serSvg', {h: 320});
let w17serM = 0;
function w17serDraw() {
  const g = w17serS.clearLayer('main');
  if (w17serM === 0) {
    w17serS.txtPx(24, 34, '{"d": 4, "b": 7, "a": -5, "c": 3}', {cls: 'axtitle'}, g);
    ['d: 4', 'b: 7', 'a: -5', 'c: 3'].forEach((t, i) => {
      w17serS.add('rect', {x: 200, y: 70 + i * 50, width: 200, height: 38, rx: 6,
                           fill: HC.tok.card, stroke: HC.tok.cardBorder,
                           'stroke-width': 1.4}, g);
      const n = w17serS.add('text', {x: 300, y: 94 + i * 50, 'text-anchor': 'middle',
                                     cls: 'vlab', 'font-family': HC.MONO}, g);
      n.textContent = t;
    });
    document.getElementById('w17serType').textContent = 'dict';
    document.getElementById('w17serIdx').textContent = '（鍵）';
    document.getElementById('w17serDtype').textContent = '—';
    setStatus('w17serStatus', '字典：鍵與值成對，但<b>沒有順序上的意義</b>，也不能做向量運算。');
  } else if (w17serM === 1) {
    w17grid(w17serS, g, {cols: ['值'], rows: [['4'], ['7'], ['-5'], ['3']],
                         index: ['d', 'b', 'a', 'c'], x0: 250, y0: 60, cw: 110});
    w17serS.txtPx(24, 34, 'pd.Series([4, 7, -5, 3], index=["d","b","a","c"])',
                  {cls: 'axtitle'}, g);
    document.getElementById('w17serType').textContent = 'Series';
    document.getElementById('w17serIdx').textContent = 'd b a c';
    document.getElementById('w17serDtype').textContent = 'int64';
    setStatus('w17serStatus', 'Series：一排數字 <b>加上一排索引</b>，可以逐元素運算。');
  } else {
    w17grid(w17serS, g, {cols: ['state', 'year', 'pop'],
                         rows: [['Ohio', '2000', '1.5'], ['Ohio', '2001', '1.7'],
                                ['Ohio', '2002', '3.6'], ['Nevada', '2001', '2.4']],
                         index: ['0', '1', '2', '3'], x0: 190, y0: 60, cw: 100});
    w17serS.txtPx(24, 34, 'pd.DataFrame(data)', {cls: 'axtitle'}, g);
    document.getElementById('w17serType').textContent = 'DataFrame';
    document.getElementById('w17serIdx').textContent = '0 1 2 3 …';
    document.getElementById('w17serDtype').textContent = 'object / int64 / float64';
    setStatus('w17serStatus', 'DataFrame：幾個 Series 共用同一排索引，<b>每欄可以不同型別</b>。');
  }
}
function w17serSet(m) { w17serM = m; w17serDraw(); }
if (w17serS) w17serDraw();

/* ═══ w17peek 前五分鐘四行指令 ═══ */
const w17peekS = HC.svg('w17peekSvg', {h: 300});
const w17peekCases = [
  {cmd: 'df.shape', what: '資料有多大', warn: '列數比預期少很多',
   sel: () => false, note: '(6, 4) —— 六列四欄。'},
  {cmd: 'df.head()', what: '長什麼樣、欄名對不對', warn: '整欄空白、欄名錯位',
   sel: (i) => i < 3, note: '預設看前五列。'},
  {cmd: 'df.dtypes', what: '每一欄是什麼型別', warn: '該是數字的欄變成 object',
   sel: (i, j) => j === 0, note: '這一行最重要——型別錯了後面全錯。'},
  {cmd: 'df.describe()', what: '範圍與遺漏', warn: 'count 比列數少',
   sel: () => true, note: 'count 那一列不算 NaN。'}
];
let w17peekI = 0;
function w17peekDraw() {
  const g = w17peekS.clearLayer('main');
  const c = w17peekCases[w17peekI];
  w17grid(w17peekS, g, {cols: ['A', 'B', 'C', 'D'],
                        rows: [['-0.40', '-1.06', '1.46', '0.63'],
                               ['-0.84', '-1.59', '-0.60', '-1.50'],
                               ['0.50', '-0.66', '0.15', '0.29'],
                               ['-1.06', '-1.01', '0.55', '0.21'],
                               ['-0.11', '0.24', '-0.20', '0.70']],
                        index: ['09-01', '09-02', '09-03', '09-04', '09-05'],
                        x0: 190, y0: 56, cw: 88, sel: c.sel});
  w17peekS.txtPx(24, 34, c.cmd, {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w17peekCmd').textContent = c.cmd;
  document.getElementById('w17peekWhat').textContent = c.what;
  document.getElementById('w17peekWarn').textContent = c.warn;
  setStatus('w17peekStatus', c.note);
}
function w17peekSet(i) { w17peekI = i; w17peekDraw(); }
if (w17peekS) w17peekDraw();
"""

PAGEJS += r"""
/* ═══ w17sel loc vs iloc（本頁招牌）═══ */
const w17selS = HC.svg('w17selSvg', {h: 340});
const w17selCases = [
  {e: 'df["A"]', t: 'Series', sh: '(6,)', sel: (i, j) => j === 0,
   note: '中括號給字串 → 取<b>欄</b>，回傳 Series。'},
  {e: 'df[0:3]', t: 'DataFrame', sh: '(3, 4)', sel: (i) => i < 3,
   note: '同一個中括號給切片 → 取<b>列</b>。這就是為什麼建議一律寫 loc／iloc。'},
  {e: 'df.loc[:, ["A","C"]]', t: 'DataFrame', sh: '(6, 2)', sel: (i, j) => j === 0 || j === 2,
   note: 'loc 的第二個位置給欄<b>名字</b>。'},
  {e: 'df.iloc[3]', t: 'Series', sh: '(4,)', sel: (i) => i === 3,
   note: 'iloc 給<b>位置</b>；拿一整列回來，欄名變成它的索引。'},
  {e: 'df[df["A"] > 0]', t: 'DataFrame', sh: '(2, 4)', sel: (i) => i === 2 || i === 5,
   note: '布林遮罩：A 欄大於 0 的那兩列（09-03 與 09-06）。'}
];
let w17selI = 0;
function w17selDraw() {
  const g = w17selS.clearLayer('main');
  const c = w17selCases[w17selI];
  w17grid(w17selS, g, {cols: ['A', 'B', 'C', 'D'],
                       rows: [['-0.40', '-1.06', '1.46', '0.63'],
                              ['-0.84', '-1.59', '-0.60', '-1.50'],
                              ['0.50', '-0.66', '0.15', '0.29'],
                              ['-1.06', '-1.01', '0.55', '0.21'],
                              ['-0.11', '0.24', '-0.20', '0.70'],
                              ['0.16', '-0.97', '0.84', '1.64']],
                       index: ['09-01', '09-02', '09-03', '09-04', '09-05', '09-06'],
                       x0: 190, y0: 56, cw: 88, sel: c.sel});
  w17selS.txtPx(24, 34, c.e, {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w17selExpr').textContent = c.e;
  document.getElementById('w17selType').textContent = c.t;
  document.getElementById('w17selShape').textContent = c.sh;
  setStatus('w17selStatus', c.note);
}
function w17selSet(i) { w17selI = i; w17selDraw(); }
if (w17selS) w17selDraw();

/* ═══ w17na Auto 的遺漏值 ═══ */
const w17naS = HC.svg('w17naSvg', {h: 340});
const w17naSteps = [
  {t: 'object（字串）', r: '397', title: '讀進來，看起來很正常',
   note: '<code>Auto.shape</code> 是 (397, 9)，欄名也都對。看不出問題。'},
  {t: 'object（字串）', r: '397', title: '① dtypes：horsepower 是 object',
   note: '該是數字的欄變成字串 —— <b>這一步是唯一的預警</b>。'},
  {t: 'object（字串）', r: '397', title: '② np.unique 找出兇手：那個 ?',
   note: '整欄的值都帶引號，而且裡面混了一個 <code>?</code>。'},
  {t: 'float64', r: '397', title: '③ 讀檔時就宣告 na_values=["?"]',
   note: '型別變成 float64，問號變成 NaN。<b>現在才算讀對了。</b>'},
  {t: 'float64', r: '392', title: '④ dropna()：397 → 392',
   note: '課本裡的 n=392 就是從這裡來的。'}
];
let w17naI = 0;
function w17naDraw() {
  const g = w17naS.clearLayer('main');
  const st = w17naSteps[w17naI];
  const vals = ['130', '165', '150', w17naI >= 3 ? 'NaN' : '?', '140', '198'];
  const bad = w17naI >= 1 && w17naI <= 2;
  vals.forEach((v, i) => {
    if (w17naI >= 4 && v === 'NaN') return;
    const y = 96 + i * 36;
    const isq = (v === '?' || v === 'NaN');
    w17naS.add('rect', {x: 230, y: y, width: 160, height: 30, rx: 4,
                        fill: isq ? (w17naI >= 3 ? HC.tok.muted : HC.tok.resid) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.3,
                        opacity: isq ? 0.95 : 0.6}, g);
    const t = w17naS.add('text', {x: 310, y: y + 20, 'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: isq ? HC.tok.paper : HC.tok.ink}, g);
    t.textContent = (w17naI <= 2 ? "'" + v + "'" : v);
  });
  w17naS.txtPx(24, 34, st.title, {cls: 'axtitle', fill: bad ? HC.tok.resid : HC.tok.accent}, g);
  w17naS.txtPx(310, 76, 'horsepower', {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w17naStep').textContent = w17naI + ' / 4';
  document.getElementById('w17naType').textContent = st.t;
  document.getElementById('w17naRows').textContent = st.r;
  setStatus('w17naStatus', st.note);
}
function w17naStep() { w17naI = Math.min(4, w17naI + 1); w17naDraw(); }
function w17naReset() { w17naI = 0; w17naDraw(); }
if (w17naS) w17naDraw();
"""

PAGEJS += r"""
/* ═══ w17grp groupby 拆分-套用-合併（本頁招牌）═══ */
const w17grpS = HC.svg('w17grpSvg', {h: 340});
const w17grpRows = [
  {a: 'foo', c: 0.47, d: 0.11}, {a: 'bar', c: 0.62, d: 0.94},
  {a: 'foo', c: -1.20, d: 0.33}, {a: 'bar', c: 0.51, d: 0.78},
  {a: 'foo', c: -0.85, d: 0.09}, {a: 'bar', c: 0.62, d: 0.78},
  {a: 'foo', c: -0.73, d: 0.05}, {a: 'foo', c: -0.43, d: 0.11}
];
let w17grpI = 0, w17grpTimer = null;
function w17grpDraw() {
  const g = w17grpS.clearLayer('main');
  const st = w17grpI;
  const cw = 74, chh = 30;
  const drawRow = (r, x, y, on) => {
    [r.a, HC.fmt(r.c, 2), HC.fmt(r.d, 2)].forEach((v, j) => {
      w17grpS.add('rect', {x: x + j * cw, y: y, width: cw - 5, height: chh - 5, rx: 3,
                           fill: on ? (r.a === 'foo' ? HC.tok.accent2 : HC.tok.accent)
                                    : HC.tok.card,
                           stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                           opacity: on ? 0.95 : 0.5}, g);
      const t = w17grpS.add('text', {x: x + j * cw + (cw - 5) / 2, y: y + 18,
                                     'text-anchor': 'middle', cls: 'vlab',
                                     'font-family': HC.MONO,
                                     fill: on ? HC.tok.paper : HC.tok.muted}, g);
      t.textContent = v;
    });
  };
  if (st === 0) {
    w17grpS.txtPx(24, 34, '原始的表（A 是分組的鍵）', {cls: 'axtitle'}, g);
    w17grpRows.forEach((r, i) => drawRow(r, 210, 60 + i * chh, false));
  } else if (st === 1) {
    w17grpS.txtPx(24, 34, '① 拆分：照 A 的值分成兩堆', {cls: 'axtitle', fill: HC.tok.accent}, g);
    let yf = 60, yb = 60;
    w17grpRows.forEach(r => {
      if (r.a === 'foo') { drawRow(r, 78, yf, true); yf += chh; }
      else { drawRow(r, 352, yb, true); yb += chh; }
    });
    w17grpS.txtPx(78, 52, 'foo', {cls: 'axlab', anchor: 'start'}, g);
    w17grpS.txtPx(352, 52, 'bar', {cls: 'axlab', anchor: 'start'}, g);
  } else if (st === 2) {
    w17grpS.txtPx(24, 34, '② 套用：每一堆各加總一次', {cls: 'axtitle', fill: HC.tok.accent}, g);
    let yf = 60, yb = 60;
    w17grpRows.forEach(r => {
      if (r.a === 'foo') { drawRow(r, 78, yf, true); yf += chh; }
      else { drawRow(r, 352, yb, true); yb += chh; }
    });
    w17grpS.add('line', {x1: 84, y1: yf + 4, x2: 84 + 3 * cw - 10, y2: yf + 4,
                         stroke: HC.tok.ink, 'stroke-width': 2}, g);
    w17grpS.add('line', {x1: 358, y1: yb + 4, x2: 358 + 3 * cw - 10, y2: yb + 4,
                         stroke: HC.tok.ink, 'stroke-width': 2}, g);
    drawRow({a: 'foo', c: -2.740490, d: 0.700964}, 78, yf + 10, true);
    drawRow({a: 'bar', c: 1.747047, d: 2.499340}, 352, yb + 10, true);
  } else {
    w17grpS.txtPx(24, 34, '③ 合併：疊成一張表，A 變成索引',
                  {cls: 'axtitle', fill: HC.tok.accent}, g);
    ['', 'C', 'D'].forEach((c, j) => {
      const t = w17grpS.add('text', {x: 220 + j * 110 + 50, y: 96, 'text-anchor': 'middle',
                                     cls: 'axtitle'}, g);
      t.textContent = c;
    });
    [['bar', '1.747047', '2.499340'], ['foo', '-2.740490', '0.700964']].forEach((r, i) => {
      r.forEach((v, j) => {
        const on = j > 0;
        w17grpS.add('rect', {x: 220 + j * 110, y: 110 + i * 40, width: 100, height: 32, rx: 4,
                             fill: on ? HC.tok.accent2 : 'none',
                             stroke: on ? HC.tok.cardBorder : 'none', 'stroke-width': 1.2}, g);
        const t = w17grpS.add('text', {x: 220 + j * 110 + 50, y: 132 + i * 40,
                                       'text-anchor': 'middle', cls: 'vlab',
                                       'font-family': HC.MONO,
                                       fill: on ? HC.tok.paper : HC.tok.ink}, g);
        t.textContent = v;
      });
    });
    w17grpS.txtPx(310, 212, 'A 已經不是一般的欄了，它是索引',
                  {cls: 'axlab', anchor: 'middle'}, g);
  }
  const names = ['原始的表', '拆分 split', '套用 apply', '合併 combine'];
  document.getElementById('w17grpStep').textContent = w17grpI + ' / 3';
  document.getElementById('w17grpN').textContent = w17grpI >= 1 ? '2 組（foo、bar）' : '—';
  document.getElementById('w17grpShape').textContent = w17grpI >= 3 ? '(2, 2)' : '—';
  setStatus('w17grpStatus', names[w17grpI] + (w17grpI === 3
    ? '：<b>八列變成兩列</b>，分組的鍵成了索引。' : '。'));
}
function w17grpStep() { w17grpI = Math.min(3, w17grpI + 1); w17grpDraw(); }
function w17grpReset() {
  if (w17grpTimer) { clearTimeout(w17grpTimer); w17grpTimer = null; }
  w17grpI = 0; w17grpDraw();
}
function w17grpPlay() {
  w17grpReset();
  const tick = () => {
    if (w17grpI >= 3) { w17grpTimer = null; return; }
    w17grpStep();
    w17grpTimer = setTimeout(tick, 900);
  };
  w17grpTimer = setTimeout(tick, 500);
}
if (w17grpS) w17grpDraw();

/* ═══ w17cat concat 疊回去 ═══ */
const w17catS = HC.svg('w17catSvg', {h: 320});
let w17catI = 0;
function w17catDraw() {
  const g = w17catS.clearLayer('main');
  const pieces = [[['09-01'], ['09-02']], [['09-03'], ['09-04']], [['09-05'], ['09-06']]];
  const cols = [HC.tok.accent2, HC.tok.accent, HC.tok.accent3];
  let placed = 0;
  pieces.forEach((pc, pi) => {
    const merged = pi < w17catI;
    pc.forEach((r, ri) => {
      const x = merged ? 250 : 90 + pi * 160;
      const y = merged ? 70 + placed * 36 : 90 + ri * 36;
      w17catS.add('rect', {x: x, y: y, width: 130, height: 30, rx: 4,
                           fill: cols[pi], opacity: merged ? 0.95 : 0.55}, g);
      const t = w17catS.add('text', {x: x + 65, y: y + 20, 'text-anchor': 'middle',
                                     cls: 'vlab', 'font-family': HC.MONO,
                                     fill: HC.tok.paper}, g);
      t.textContent = r[0];
      if (merged) placed += 1;
    });
    if (!merged) {
      const lb = w17catS.add('text', {x: 90 + pi * 160 + 65, y: 80, 'text-anchor': 'middle',
                                      cls: 'axlab'}, g);
      lb.textContent = 'pieces[' + pi + ']';
    }
  });
  w17catS.txtPx(24, 34, w17catI === 0 ? 'pieces = [df[:2], df[2:4], df[4:]]'
                                      : 'pd.concat(pieces)',
                {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w17catStep').textContent = w17catI + ' / 3';
  document.getElementById('w17catRows').textContent = String(w17catI * 2);
  setStatus('w17catStatus', w17catI === 3
    ? '六列全部接回去了，跟原本的 df 一模一樣。'
    : '沿著<b>列</b>接：欄名要一樣，列直接往下疊。');
}
function w17catStep() { w17catI = Math.min(3, w17catI + 1); w17catDraw(); }
function w17catReset() { w17catI = 0; w17catDraw(); }
if (w17catS) w17catDraw();

/* ═══ w17grpChart 分組結果（數字逐字取自 lab 儲存格 78）═══ */
const w17grpBaked = {C: [1.747047, -2.740490], D: [2.499340, 0.700964]};
let w17grpColCur = 'C';
function w17grpChartDraw() {
  if (!HC.hasChart()) return;
  const vals = w17grpBaked[w17grpColCur];
  const c = HC.get('w17grpChart');
  if (c) {
    c.data.datasets[0].data = vals;
    c.data.datasets[0].label = w17grpColCur + ' 欄的總和';
    c.update();
  } else {
    HC.bar('w17grpChart', {
      labels: ['bar', 'foo'],
      datasets: [{label: w17grpColCur + ' 欄的總和', data: vals,
                  backgroundColor: [HC.tok.accent, HC.tok.accent2], borderWidth: 0}]
    }, {
      scales: {x: {title: {display: true, text: '分組鍵 A'}},
               y: {title: {display: true, text: '總和'}}},
      plugins: {legend: {display: false}}
    });
  }
  setStatus('w17grpStatus2', w17grpColCur === 'C'
    ? 'C 欄：bar 是正的、foo 是負的 —— <b>方向相反</b>，合起來看會互相抵消。'
    : 'D 欄：兩組同號，bar 大約是 foo 的三倍半。');
}
function w17grpCol(k) { w17grpColCur = k; w17grpChartDraw(); }
HC.ready(() => { w17grpChartDraw(); });
"""

apply("p4_pandas", BODIES, PAGEJS)
