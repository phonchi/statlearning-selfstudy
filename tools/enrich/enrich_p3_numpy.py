#!/usr/bin/env python3
"""p3_numpy.html（先備 P3 · NumPy 陣列）完整自學充實。冪等。

內容依據：Ch02-statlearn-lab-zh.ipynb 的「實驗：Python 入門」整段
（儲存格 21–176）。所有程式碼與「預期輸出」逐字取自該 lab，
一格都沒有重跑。那些數字是老師在課程環境跑出來的。

這是先備入口層的 pilot 頁，prep 頁的規格由它凍結：
每節一個 quiz、EX 區四題自訂、元件以 live SVG 機制動畫為主、
所有 id 與頂層 JS 宣告都帶 w16 前綴。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, hl, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

CH = 2
LAB = "Ch02-statlearn-lab-zh.ipynb"


def C(*ks):
    """把數個儲存格的程式碼接成一張卡。逐字取自 lab，不改一個字。"""
    return "\n".join(lab_code(CH, k) for k in ks)


def O(k):
    return lab_output(CH, k)


def S(*ks):
    return f'<code>{LAB}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 為什麼不用串列 ─────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>統計程式從頭到尾都在做同一件事：<strong>對一整排數字做同一個運算</strong>。
  算殘差是每一筆都減掉配適值，算標準化是每一筆都減平均再除標準差。
  Python 內建的串列（list）做不到這件事。它的 <code>+</code> 是「接起來」，不是「加起來」。</p>

{info("一句話", "串列的 <code>+</code> 是串接，陣列的 <code>+</code> 是逐元素相加。"
      "這一個差別就是你需要 NumPy 的全部理由。")}

{viz(svg("w16listArrSvg", 300),
     [info_card("兩種 +",
                "上排是<strong>串列</strong>：<code>x + y</code> 把 y 接在 x 後面，長度變成 6。<br>"
                "下排是<strong>陣列</strong>：<code>x + y</code> 把對齊的元素相加，長度還是 3。"),
      rows_card("目前的結果",
                [("x + y（串列）", "—", "w16laList"),
                 ("x + y（陣列）", "—", "w16laArr"),
                 ("長度", "—", "w16laLen")]),
      info_card("為什麼串列要這樣設計",
                "串列裝的東西可以是任何型別，數字、字串、另一個串列混在一起都行，"
                "所以「相加」對它沒有意義，只能定義成串接。"
                "陣列規定<strong>整塊都是同一個型別</strong>，才談得上逐元素運算。")],
     "w16laStatus", "按「切換」看同一組數字在兩種容器裡的行為。",
     '<button class="btn btn-step" onclick="w16laTog()">切換：串列 ⇄ 陣列</button>'
     '<button class="btn btn-reset" onclick="w16laReset()">重置</button>')}

{card("串列的 + 是串接", C(21, 23), O(23), src=S(21, 23),
      note="注意輸出是 <code>[3, 4, 5, 4, 9, 7]</code>，六個元素，不是三個。")}

{card("陣列的 + 是逐元素相加", C(31, 34), O(34), src=S(31, 34),
      note="同一組數字，換成 <code>np.array</code> 之後 <code>+</code> 的意思就變了。")}

{qa("常見疑問", [
    ("那我可以只用 pandas，不學 NumPy 嗎？",
     "不行，而且你已經在用了。<code>DataFrame</code> 的每一欄底下就是一個 NumPy 陣列，"
     "<code>df['mpg'].mean()</code> 走的是 NumPy 的路。"
     "pandas 幫你管欄名與索引，真正算數字的還是 NumPy。"),
    ("陣列比串列快在哪裡？",
     "兩件事。一是<strong>記憶體連續</strong>：整塊同型別的數字排在一起，CPU 一次抓一批；"
     "串列存的是一堆指標，每個元素都要再跳一次。"
     "二是<strong>迴圈在 C 裡面跑</strong>：<code>x**2</code> 不會回到 Python 逐個平方。"),
])}

{quiz("qArr", "PART 00 · 自我檢測",
      "<code>a = [1, 2]</code>、<code>b = [3, 4]</code>，那麼 <code>a + b</code> 是什麼？",
      [(False, "<code>[4, 6]</code>",
        "你想的是逐元素相加，那是<strong>陣列</strong>的行為。"
        "串列的 <code>+</code> 是串接，不會去對齊位置。"),
       (True, "<code>[1, 2, 3, 4]</code>",
        "對。串列的 <code>+</code> 把兩個串列接起來，長度是 2+2=4。"
        "要逐元素相加得先 <code>np.array(a) + np.array(b)</code>。"),
       (False, "會報錯，長度一樣才能相加",
        "串列相加不檢查長度，因為它根本不是在對齊——"
        "<code>[1,2] + [3]</code> 也會乖乖給你 <code>[1, 2, 3]</code>。")])}
"""

# ── P01 建立陣列與 shape ────────────────────────────────────────────────
BODIES["create"] = f"""
  <p>一個陣列的身分由三個屬性決定：<code>ndim</code>（幾維）、<code>dtype</code>（裝什麼型別）、
  <code>shape</code>（每一維多長）。看不懂錯誤訊息的時候，先把這三個印出來，八成就找到原因了。</p>

{info("先記這一條", "<code>shape</code> 是一個 tuple。二維陣列的 <code>shape</code> 是 "
      "<code>(列數, 欄數)</code>，<strong>列在前、欄在後</strong>。", "warm")}

{card("建立二維陣列", C(36), O(36), src=S(36))}

{card("三個身分證欄位", C(38) + "\n" + C(40) + "\n" + C(48),
      f"{O(38)}\n{O(40)}\n{O(48)}", src=S(38, 40, 48),
      note="lab 裡這三格是分開跑的，這裡併成一張卡方便對照；"
           "輸出仍逐字取自各自的儲存格。")}

{info("dtype 會被最寬的元素決定",
      "<code>np.array([[1, 2], [3.0, 4]])</code> 裡只要有一個浮點數，"
      "整塊就變成 <code>float64</code>——陣列不允許同一塊裡混型別。"
      "想指定就寫 <code>np.array([[1, 2], [3, 4]], float)</code>。")}

{quiz("qShape", "PART 01 · 自我檢測",
      "<code>X.shape</code> 是 <code>(10, 3)</code>，這個陣列是什麼？",
      [(True, "10 列 3 欄：10 筆觀測、每筆 3 個變數",
        "對。統計資料的慣例就是這樣擺：<strong>列是觀測、欄是變數</strong>，"
        "所以 n=10、p=3。整門課的 X 都是這個形狀。"),
       (False, "10 個變數、每個變數 3 筆觀測",
        "順序反了。<code>shape</code> 的第一個數字是<strong>列</strong>數。"
        "如果真的是 10 個變數 3 筆觀測，shape 會是 <code>(3, 10)</code>。"),
       (False, "一個 10 維陣列，每一維長度 3",
        "「幾維」看的是 <code>ndim</code>，也就是 shape 這個 tuple 的長度。"
        "這裡 tuple 只有兩個數字，所以是二維。")])}
"""

# ── P02 reshape 與轉置 ──────────────────────────────────────────────────
BODIES["reshape"] = f"""
  <p><code>reshape</code> 不搬資料。它給你的是<strong>同一塊記憶體的另一種讀法</strong>——
  六個數字排成一排，或排成兩列三欄，底下是同一塊。這件事不知道的話，
  之後改了一個變數卻發現另一個也跟著變，會找很久。</p>

{viz(svg("w16reshapeSvg", 320),
     [info_card("拖或按都可以",
                "按下方的形狀按鈕，看同樣六個數字被切成不同的樣子。"
                "注意<strong>數字的順序從頭到尾沒變</strong>，變的只是換行的位置。"),
      rows_card("目前狀態",
                [("shape", "(6,)", "w16rsShape"),
                 ("ndim", "1", "w16rsDim"),
                 ("讀法", "一排六個", "w16rsRead")]),
      info_card("C 順序（row-major）",
                "NumPy 預設<strong>先填滿一列再換下一列</strong>。"
                "所以 <code>reshape((2, 3))</code> 得到的第一列是前三個數字，"
                "不是每隔一個取一次。")],
     "w16rsStatus", "選一個形狀，看六個數字怎麼被重新分行。",
     '<button class="btn btn-toggle" onclick="w16rsSet(1,6)">(6,)</button>'
     '<button class="btn btn-toggle" onclick="w16rsSet(2,3)">(2, 3)</button>'
     '<button class="btn btn-toggle" onclick="w16rsSet(3,2)">(3, 2)</button>'
     '<button class="btn btn-toggle" onclick="w16rsSet(6,1)">(6, 1)</button>')}

{card("reshape 成兩列三欄", C(54), O(54), src=S(54))}

{card("改 reshape 出來的元素，原陣列也會變", C(61), O(61), src=S(61),
      note="這就是「同一塊記憶體」的證據：改 <code>x_reshape[0, 0]</code>，"
           "<code>x</code> 的第一個元素跟著變成 5。")}

{card("shape、ndim 與轉置", C(66), O(66), src=S(66),
      note="<code>.T</code> 同樣不搬資料，它只是把「先走列還是先走欄」對調。")}

{qa("觀念釐清", [
    ("什麼時候會真的複製一份？",
     "切片（<code>A[1:3]</code>）與 <code>reshape</code> 給的是<strong>檢視（view）</strong>，"
     "不複製；<strong>花式索引</strong>（用整數串列或布林陣列去挑，例如 <code>A[[1,3]]</code>）"
     "與明確呼叫 <code>.copy()</code> 才會複製。"
     "不確定就 <code>.copy()</code>，安全比省記憶體重要。"),
    ("為什麼 reshape 要傳一個 tuple？",
     "因為形狀本來就是一個 tuple。<code>x.reshape((2, 3))</code> 與 "
     "<code>x.reshape(2, 3)</code> 都可以，前者跟 <code>shape</code> 屬性的寫法一致，"
     "讀起來比較不會誤會。"),
])}

{quiz("qView", "PART 02 · 自我檢測",
      "<code>x = np.array([1,2,3,4,5,6])</code>、<code>y = x.reshape((2,3))</code>，"
      "接著執行 <code>y[0,0] = 99</code>。<code>x[0]</code> 現在是多少？",
      [(False, "還是 1，y 是新的陣列",
        "這正是 lab 那一格要示範的陷阱。<code>reshape</code> 回傳的是"
        "<strong>同一塊資料的檢視</strong>，不是複本。"),
       (True, "99，因為 y 跟 x 共用同一塊資料",
        "對。要切斷連結得寫 <code>y = x.reshape((2,3)).copy()</code>。"
        "在資料前處理時這個坑很常見：你以為在改暫存變數，其實動到了原始資料。"),
       (False, "會報錯，view 不能改",
        "view 是可以寫入的。它就是拿來讓你原地修改的。"
        "唯讀的 view 要另外設 <code>flags.writeable = False</code>。")])}

{hook("這在本站哪一章會用到",
      '第 3 章把資料組成設計矩陣 X 時，<code>reshape(-1, 1)</code> 幾乎每次都會出現；'
      '第 12 章做主成分之前要先把資料中心化，靠的就是這裡的 shape 對齊。'
      '<a href="linear_regression.html#mlr">→ 線性迴歸 · 多元迴歸</a>')}
"""

# ── P03 索引、切片與子矩陣 ──────────────────────────────────────────────
BODIES["index"] = f"""
  <p>接下來這一節是整頁最容易出錯的地方。lab 裡老師特地留了一格叫
  <em>「糟糕——發生了什麼？」</em>，因為 <code>A[[1,3],[0,2]]</code> 拿到的
  <strong>不是</strong> 第 1、3 列與第 0、2 欄交叉的那個 2×2 子矩陣。</p>

{viz(svg("w16idxSvg", 340),
     [info_card("四種寫法",
                "按按鈕切換寫法，被選到的格子會亮起來。"
                "<code>A[[1,3],[0,2]]</code> 亮的只有兩格——"
                "它把兩個索引串列<strong>配對</strong>成 (1,0) 與 (3,2)。"),
      rows_card("這個寫法拿到什麼",
                [("寫法", "A", "w16idxExpr"),
                 ("結果 shape", "(4, 4)", "w16idxShape"),
                 ("拿到的值", "全部", "w16idxVals")]),
      info_card("要子矩陣就用 np.ix_",
                "<code>np.ix_([1,3],[0,2])</code> 明講「這兩組是要交叉的」，"
                "或者分兩步 <code>A[[1,3]][:,[0,2]]</code>。"
                "兩種都對，<code>np.ix_</code> 少複製一次。")],
     "w16idxStatus", "先自己猜哪幾格會亮，再按按鈕。",
     '<button class="btn btn-toggle" onclick="w16idxSet(0)">A</button>'
     '<button class="btn btn-toggle" onclick="w16idxSet(1)">A[[1,3]]</button>'
     '<button class="btn btn-toggle" onclick="w16idxSet(2)">A[:,[0,2]]</button>'
     '<button class="btn btn-toggle" onclick="w16idxSet(3)">A[[1,3],[0,2]]</button>'
     '<button class="btn btn-toggle" onclick="w16idxSet(4)">np.ix_([1,3],[0,2])</button>'
     '<button class="btn btn-toggle" onclick="w16idxSet(5)">A[1:4:2,0:3:2]</button>')}

{card("先做一個 4×4 的 A", C(138), O(138), src=S(138))}

{card("挑列、挑欄", C(144) + "\n" + C(146), f"{O(144)}\n{O(146)}", src=S(144, 146),
      note="單獨挑列或單獨挑欄都很直覺，問題出在兩個一起寫。")}

{card("糟糕——發生了什麼？", C(148), O(148), src=S(148),
      note="只拿到兩個數字：<code>A[1,0]</code> 與 <code>A[3,2]</code>。"
           "兩個索引串列被<strong>逐位配對</strong>，不是交叉。")}

{card("長度不一樣就直接報錯", C(152), O(152), src=S(152),
      out_tag="錯誤訊息",
      note="錯誤訊息裡的 <code>could not be broadcast together</code> 已經在暗示："
           "花式索引走的是廣播規則，不是交叉。")}

{card("真的要子矩陣：兩種寫法", C(154) + "\n" + C(156),
      f"{O(154)}\n{O(156)}", src=S(154, 156),
      note="<code>A[[1,3]][:,[0,2]]</code> 會產生一個中間陣列；"
           "<code>np.ix_</code> 一步到位。")}

{card("等距切片也能取子矩陣", C(158), O(158), src=S(158),
      note="切片是 <code>起:迄:步長</code>，迄不包含。"
           "<code>1:4:2</code> 取到第 1、3 列，<code>0:3:2</code> 取到第 0、2 欄。")}

{quiz("qFancy", "PART 03 · 自我檢測",
      "想從 <code>A</code> 取出「第 0、2 列」與「第 1、3 欄」交叉的 2×2 子矩陣，"
      "下列哪一個<strong>不會</strong>給你想要的東西？",
      [(False, "<code>A[np.ix_([0,2],[1,3])]</code>",
        "這個是對的。<code>np.ix_</code> 的用途就是把兩組索引展開成交叉。"),
       (False, "<code>A[[0,2]][:,[1,3]]</code>",
        "這個也是對的。先挑列得到 2×4，再挑欄得到 2×2，只是多產生一個中間陣列。"),
       (True, "<code>A[[0,2],[1,3]]</code>",
        "對，這個不行。它是本節的陷阱。兩個串列會被逐位配對成 (0,1) 與 (2,3)，"
        "只拿到兩個數字，shape 是 <code>(2,)</code> 不是 <code>(2,2)</code>。")])}
"""

# ── P04 布林索引 ────────────────────────────────────────────────────────
BODIES["bool"] = f"""
  <p>統計程式裡挑資料，九成不是靠位置，是靠<strong>條件</strong>：
  「馬力大於 150 的那些車」「訓練集的那些列」。做法是先算出一排 True／False，
  再拿它去索引。這排布林值的長度必須跟那一維一樣長。</p>

{info("布林索引與整數索引不一樣",
      "<code>A[np.array([0,1,0,1])]</code> 是<strong>整數</strong>索引，"
      "意思是「第 0、1、0、1 列」，會拿到四列而且有重複；"
      "<code>A[np.array([False,True,False,True])]</code> 才是布林索引，拿到兩列。"
      "長得很像，結果差很多。", "warm")}

{viz(svg("w16maskSvg", 320),
     [info_card("拖門檻",
                "拖那條線，看有多少列被留下。左邊是每一列的值，"
                "右邊亮起來的是 <code>值 &gt; 門檻</code> 為 True 的列。"),
      rows_card("目前",
                [("門檻", "8", "w16maskThr"),
                 ("遮罩", "—", "w16maskVec"),
                 ("留下幾列", "—", "w16maskN")]),
      info_card("為什麼不用 for 迴圈",
                "同樣的事寫成迴圈要五行，而且慢一到兩個數量級。"
                "更重要的是——<strong>條件寫成一行才看得出你在挑什麼</strong>，"
                "半年後回來看還讀得懂。")],
     "w16maskStatus", "拖動門檻線，看遮罩怎麼變。",
     '<button class="btn btn-step" onclick="w16maskStep(-2)">門檻 −2</button>'
     '<button class="btn btn-step" onclick="w16maskStep(2)">門檻 +2</button>'
     '<button class="btn btn-reset" onclick="w16maskReset()">重置</button>')}

{card("做一個布林遮罩", C(162) + "\n" + C(164), f"{O(162)}\n{O(164)}", src=S(162, 164),
      note="<code>np.zeros(n, bool)</code> 開一排 False，再把要的位置設成 True。")}

{card("整數索引 vs 布林索引", C(169) + "\n" + C(171), f"{O(169)}\n{O(171)}", src=S(169, 171),
      note="同樣是 <code>[0,1,0,1]</code>，型別不同結果就不同："
           "整數版拿到四列（還重複了），布林版拿到兩列。")}

{card("布林也能配 np.ix_ 取子矩陣", C(174), O(174), src=S(174))}

{quiz("qMask", "PART 04 · 自我檢測",
      "<code>Auto</code> 有 392 列。<code>mask = Auto['mpg'] &gt; 30</code> 之後，"
      "<code>mask</code> 的長度是多少？",
      [(True, "392，每一列一個 True 或 False",
        "對。遮罩是<strong>跟被索引那一維一樣長</strong>的布林陣列，"
        "不是「符合條件的筆數」。真正的筆數要 <code>mask.sum()</code>。"),
       (False, "符合條件的筆數，例如 89",
        "那是 <code>mask.sum()</code> 的結果。"
        "遮罩本身必須跟原資料一樣長，否則 NumPy 不知道每個 True 對應哪一列。"),
       (False, "1，因為它是一個條件",
        "<code>Auto['mpg'] &gt; 30</code> 是<strong>向量化</strong>比較，"
        "392 個數字各比一次，得到 392 個布林值。")])}
"""

# ── P05 廣播 ────────────────────────────────────────────────────────────
BODIES["bcast"] = f"""
  <p>形狀不一樣的兩個陣列也能相加，NumPy 會照一套固定規則把它們對齊，這叫<strong>廣播</strong>
  （broadcasting）。標準化資料 <code>(X - X.mean(0)) / X.std(0)</code> 就是靠它——
  左邊是 (10, 3)，右邊是 (3,)，形狀不同卻能直接相減。</p>

{info("廣播三步驟",
      "① <strong>右對齊</strong>兩個 shape；② 缺的維度<strong>補 1</strong>；"
      "③ 長度是 1 的維度<strong>拉伸</strong>到對方的長度。"
      "任何一維兩邊既不相等、也沒有一邊是 1，就報錯。")}

{viz(svg("w16bcastSvg", 340),
     [info_card("一步一步看",
                "按「單步」走完三個步驟。紅色代表這一維對不上、會報錯；"
                "綠色代表這一維可以拉伸。"),
      rows_card("目前",
                [("A 的 shape", "(10, 3)", "w16bcA"),
                 ("B 的 shape", "(3,)", "w16bcB"),
                 ("結果", "—", "w16bcOut")]),
      info_card("為什麼標準化寫得出來",
                "<code>X.mean(0)</code> 的 shape 是 <code>(3,)</code>，"
                "右對齊補成 <code>(1, 3)</code>，再把第一維拉伸成 10——"
                "等於<strong>每一列都減同一組欄平均</strong>，正是我們要的。")],
     "w16bcStatus", "選一組 shape，再按單步。",
     '<button class="btn btn-toggle" onclick="w16bcCase(0)">(10,3) 與 (3,)</button>'
     '<button class="btn btn-toggle" onclick="w16bcCase(1)">(10,3) 與 (10,1)</button>'
     '<button class="btn btn-toggle" onclick="w16bcCase(2)">(10,3) 與 (10,)　✗</button>'
     '<button class="btn btn-step" onclick="w16bcStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w16bcReset()">重置</button>')}

{card("最單純的廣播：陣列與純量", C(68) + "\n" + C(70), f"{O(68)}\n{O(70)}", src=S(68, 70),
      note="<code>x**2</code> 的 2 是純量，shape 是 <code>()</code>，"
           "被拉伸成跟 x 一樣長。你早就在用廣播了，只是沒察覺。")}

{table(["A 的 shape", "B 的 shape", "結果", "為什麼"],
       [["(10, 3)", "(3,)", "(10, 3)", "右對齊補成 (1,3)，第一維 1→10"],
        ["(10, 3)", "(10, 1)", "(10, 3)", "第二維 1→3"],
        ["(10, 3)", "(10,)", "✗ 報錯", "右對齊後是 (1,10)，第二維 3 vs 10 對不上"],
        ["(10, 3)", "(10, 3)", "(10, 3)", "完全一樣，不用拉伸"]])}

{info("減欄平均要小心方向",
      "<code>X - X.mean(0)</code> 對，因為 <code>(3,)</code> 會對到欄。"
      "但 <code>X - X.mean(1)</code> 會報錯——<code>(10,)</code> 右對齊之後跑去對欄了。"
      "要減列平均得寫 <code>X - X.mean(1, keepdims=True)</code>，"
      "或 <code>X - X.mean(1)[:, None]</code>。", "warm")}

{quiz("qBcast", "PART 05 · 自我檢測",
      "<code>X.shape</code> 是 <code>(100, 5)</code>。下列哪一個會報錯？",
      [(False, "<code>X - X.mean(0)</code>",
        "這個沒問題。<code>X.mean(0)</code> 是 <code>(5,)</code>，"
        "右對齊補成 <code>(1,5)</code>，第一維拉伸成 100。這就是標準化的寫法。"),
       (True, "<code>X - X.mean(1)</code>",
        "對，這個會報錯。<code>X.mean(1)</code> 是 <code>(100,)</code>，"
        "右對齊之後變成 <code>(1,100)</code>，跟 5 對不上。"
        "要減列平均得加 <code>keepdims=True</code>。"),
       (False, "<code>X - X.mean()</code>",
        "這個沒問題。不給 axis 就是把整塊 500 個數字平均成一個純量，"
        "純量對任何形狀都能廣播。")])}
"""

# ── P06 彙總與 axis ─────────────────────────────────────────────────────
BODIES["agg"] = f"""
  <p><code>axis</code> 是初學最常猜錯的參數。記法只有一句：
  <strong>axis 指的是「被摺掉」的那一維</strong>。
  <code>X.mean(0)</code> 摺掉第 0 維（列），剩下每一欄一個平均。</p>

{viz(svg("w16axisSvg", 320),
     [info_card("看箭頭的方向",
                "按按鈕切換 axis。箭頭是「加總掃過去」的方向，"
                "被掃掉的那一維就消失了。"),
      rows_card("目前",
                [("呼叫", "X.mean(0)", "w16axCall"),
                 ("摺掉哪一維", "列（axis 0）", "w16axWhich"),
                 ("結果 shape", "(3,)", "w16axShape")]),
      info_card("keepdims 是什麼",
                "加了 <code>keepdims=True</code>，被摺掉的那一維會留下長度 1，"
                "<code>(10,3)</code> 摺 axis 0 得到 <code>(1,3)</code> 而不是 <code>(3,)</code>。"
                "這樣廣播回去就不會對錯邊。")],
     "w16axStatus", "先猜結果的 shape，再按按鈕。",
     '<button class="btn btn-toggle" onclick="w16axSet(0)">axis=0（往下摺）</button>'
     '<button class="btn btn-toggle" onclick="w16axSet(1)">axis=1（往右摺）</button>'
     '<button class="btn btn-toggle" onclick="w16axSet(2)">不給 axis（全摺）</button>')}

{card("變異數的三種寫法會一致", C(84) + "\n" + C(85), f"{O(84)}\n{O(85)}", src=S(84, 85),
      note="<code>np.var</code> 預設除以 n（不是 n−1），所以它跟"
           "<code>np.mean((y - y.mean())**2)</code> 完全相同。"
           "要不偏估計得寫 <code>np.var(y, ddof=1)</code>。第 2 章會再遇到這件事。")}

{card("標準差就是變異數開根號", C(87), O(87), src=S(87))}

{card("沿 axis=0 取欄平均", C(89) + "\n" + C(91), f"{O(89)}\n{O(91)}", src=S(89, 91),
      note="X 是 (10, 3)，摺掉列之後剩三個數字，每一欄一個平均。")}

{qa("觀念釐清", [
    ("<code>X.mean(0)</code> 與 <code>X.mean(axis=0)</code> 有差嗎？",
     "沒有，第一個位置參數就是 axis。lab 裡兩種寫法都出現過，輸出完全一樣。"
     "寫 <code>axis=0</code> 比較好讀，尤其後面還要接 <code>keepdims</code> 的時候。"),
    ("為什麼 np.var 預設除以 n？",
     "NumPy 的立場是「我算的是這批數字本身的變異數」，那就是除以 n。"
     "統計上要估母體變異數才需要 n−1。<strong>pandas 的 <code>.var()</code> 預設是 ddof=1</strong>，"
     "兩邊不一致——同一份資料用兩個套件算會得到不同的數字，這是很經典的踩雷點。"),
])}

{quiz("qAxis", "PART 06 · 自我檢測",
      "<code>X.shape</code> 是 <code>(10, 3)</code>，<code>X.sum(axis=1).shape</code> 是什麼？",
      [(False, "<code>(3,)</code>",
        "那是 <code>axis=0</code> 的結果。<code>axis=1</code> 摺掉的是"
        "<strong>欄</strong>，剩下的是列的數量。"),
       (True, "<code>(10,)</code>",
        "對。axis=1 把每一列的三個數字加起來，十列就得到十個數字。"
        "口訣：axis 指的是被摺掉的那一維。"),
       (False, "<code>(10, 1)</code>",
        "不完全對，要加 <code>keepdims=True</code> 才會是 <code>(10,1)</code>。"
        "不加的話那一維會直接消失，得到 <code>(10,)</code>。")])}

{hook("這在本站哪一章會用到",
      '第 2 章算訓練 MSE 與測試 MSE，就是 <code>((y - yhat)**2).mean()</code>；'
      '偏差—變異分解的每一項都是沿某個 axis 的平均。'
      '<a href="statistical_learning.html#mse">→ 統計學習 · 評估配適品質</a>')}
"""

# ── P07 亂數與模擬 ──────────────────────────────────────────────────────
BODIES["rand"] = f"""
  <p>這門課後面每一章都要模擬：自助法重抽、交叉驗證切分、隨機森林抽變數。
  只要用到亂數，就一定要<strong>固定種子</strong>，否則你今天的圖跟明天的圖不一樣，
  跟同學的也不一樣，討論就無從討論起。</p>

{info("現在的寫法是 default_rng",
      "<code>np.random.normal(...)</code> 用的是全域狀態，"
      "誰在哪裡呼叫都會動到它。新版建議自己開一個產生器："
      "<code>rng = np.random.default_rng(1303)</code>，之後都用 <code>rng.</code> 開頭。")}

{viz(chart("w16randChart", fallback="：固定種子時，兩次抽樣的直方圖會完全重合；"
                                   "不固定種子則每次都不同。"),
     [info_card("按重抽看差別",
                "打開「固定種子」再按幾次重抽，直方圖<strong>一動也不動</strong>；"
                "關掉之後每按一次就變一次。"),
      rows_card("這一次抽樣",
                [("樣本數 n", "50", "w16rdN"),
                 ("樣本平均", "—", "w16rdMean"),
                 ("樣本標準差", "—", "w16rdSd")]),
      info_card("n 變大會怎樣",
                "把 n 從 50 拉到 500，樣本平均會越來越靠近 0——"
                "這就是大數法則。第 5 章的自助法整套建立在這個現象上。")],
     "w16rdStatus", "先固定種子按兩次重抽，再取消固定按兩次。",
     '<button class="btn btn-play" onclick="w16rdDraw()">▶ 重抽一次</button>'
     '<button class="btn btn-toggle" id="w16rdSeedBtn" onclick="w16rdSeedTog()">固定種子：開</button>'
     '<button class="btn btn-step" onclick="w16rdSize()">切換 n：50 ⇄ 500</button>'
     '<button class="btn btn-reset" onclick="w16rdReset()">重置</button>')}

{card("沒固定種子：兩次結果不同", C(80), O(80), src=S(80),
      note="同一行跑兩次，數字完全不一樣。這在寫報告時是災難。")}

{card("固定種子：兩個產生器給一模一樣的數", C(82), O(82), src=S(82),
      note="<code>default_rng(1303)</code> 開兩次，抽出來逐位相同。"
           "本站每一張自己算的圖都是這樣產生的。")}

{card("相關係數矩陣", C(78), O(78), src=S(78),
      note="對角線一定是 1，非對角線是兩個變數的相關係數。"
           "第 3 章看共線性時會一直用到這個矩陣。")}

{quiz("qSeed", "PART 07 · 自我檢測",
      "你在報告裡寫「自助法 1000 次估出的標準誤是 0.24」，但助教跑出 0.26。最可能的原因是？",
      [(False, "自助法本身有 bug",
        "不太可能。自助法是很成熟的做法，先懷疑自己的重現性設定，"
        "再懷疑演算法。這個順序在除錯時幾乎永遠是對的。"),
       (True, "沒有固定種子，兩次抽到的重抽樣本不同",
        "對。自助法的估計本身就有隨機性，B=1000 的蒙地卡羅誤差足以造成這種差距。"
        "寫 <code>rng = np.random.default_rng(0)</code> 並在報告裡註明種子，"
        "別人才重現得出來。"),
       (False, "樣本數不夠大",
        "樣本數影響的是估計的精確度，不是「同一份資料跑兩次結果不同」。"
        "這裡的差異來自重抽的隨機性，不是資料量。")])}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 形狀推理",
      "<code>A</code> 是 <code>(4, 4)</code>。<code>A[1:4:2, 0:3:2].shape</code> 是什麼？",
      [(True, "<code>(2, 2)</code>",
        "對。<code>1:4:2</code> 取第 1、3 列（迄不包含 4），"
        "<code>0:3:2</code> 取第 0、2 欄，所以是 2 列 2 欄。"
        "lab 儲存格 158 的輸出正是這個。"),
       (False, "<code>(2, 3)</code>",
        "<code>0:3:2</code> 的步長是 2，從 0 開始只會取到 0 和 2 兩欄；"
        "步長 1 才會取到 0、1、2 三欄。"),
       (False, "<code>(3, 3)</code>",
        "切片的「迄」不包含在內，而且步長 2 會跳著取——"
        "兩個因素都會讓長度變短。")])}

{quiz("qEx2", "EXERCISE 2 · 花式索引",
      "<code>A[[0,1,2],[0,1,2]]</code> 拿到的是什麼？",
      [(False, "左上角 3×3 的子矩陣",
        "這是最常見的誤解。要子矩陣得用 <code>np.ix_</code> "
        "或 <code>A[[0,1,2]][:,[0,1,2]]</code>。"),
       (True, "對角線上的三個數字",
        "對。兩個串列被逐位配對成 (0,0)、(1,1)、(2,2)，"
        "所以拿到的是對角線，shape 是 <code>(3,)</code>。"),
       (False, "會報錯，兩個串列不能同時給",
        "不會報錯，長度一樣就合法。長度不一樣才會像 lab 儲存格 152 那樣"
        "拋 <code>shape mismatch</code>。")])}

{quiz("qEx3", "EXERCISE 3 · 廣播",
      "<code>a.shape</code> 是 <code>(3, 1)</code>、<code>b.shape</code> 是 <code>(1, 4)</code>，"
      "<code>(a + b).shape</code> 是什麼？",
      [(False, "會報錯，形狀完全不同",
        "廣播不要求形狀相同，只要求每一維<strong>要嘛相等、要嘛有一邊是 1</strong>。"
        "這裡兩維都有一邊是 1。"),
       (True, "<code>(3, 4)</code>",
        "對。第一維是 3 與 1 → 拉伸成 3；第二維是 1 與 4 → 拉伸成 4。"
        "這種「行向量加欄向量得到矩陣」的寫法在算距離矩陣時很常用。"),
       (False, "<code>(3, 1)</code>",
        "廣播的結果是<strong>兩邊各維取較大者</strong>，"
        "不會停在其中一個的形狀。")])}

{quiz("qEx4", "EXERCISE 4 · 檢視與複本",
      "下列哪一個操作<strong>會</strong>複製一份資料？",
      [(False, "<code>B = A[1:3]</code>",
        "基本切片給的是檢視，改 B 會動到 A。"),
       (False, "<code>B = A.reshape((2, 8))</code>",
        "reshape 只是換一種讀法，底下還是同一塊——"
        "lab 儲存格 61 示範過改一個另一個跟著變。"),
       (True, "<code>B = A[[1, 3]]</code>",
        "會。用整數串列的<strong>花式索引</strong>沒辦法用「同一塊記憶體的不同讀法」表示，"
        "所以 NumPy 一定會配一塊新的。布林索引也一樣。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>這一頁的東西之後每一章都會用到。下面三張表當速查用。</p>

{table(["你想做的事", "寫法", "回傳的是檢視還是複本"],
       [["取連續的列", "<code>A[1:3]</code>", "檢視"],
        ["取指定的幾列", "<code>A[[1, 3]]</code>", "複本"],
        ["取指定的幾欄", "<code>A[:, [0, 2]]</code>", "複本"],
        ["取子矩陣（交叉）", "<code>A[np.ix_([1,3], [0,2])]</code>", "複本"],
        ["用條件挑列", "<code>A[mask]</code>（mask 是布林陣列）", "複本"],
        ["換形狀", "<code>A.reshape((2, 3))</code>", "檢視"],
        ["轉置", "<code>A.T</code>", "檢視"],
        ["確定要獨立一份", "<code>A.copy()</code>", "複本"]])}

{table(["彙總", "axis=0", "axis=1", "不給 axis"],
       [["(10, 3) 的輸入", "摺掉列 → <code>(3,)</code>", "摺掉欄 → <code>(10,)</code>",
         "全摺 → 純量"],
        ["直覺說法", "每一欄一個數字", "每一列一個數字", "整塊一個數字"],
        ["常見用途", "欄平均、欄標準差（標準化）", "每筆觀測的總和",
         "整體 MSE"]])}

{table(["容易搞混的一對", "差在哪"],
       [["<code>np.var(y)</code> vs <code>y.var()</code>", "沒差，兩個都是除以 n"],
        ["<code>np.var(y)</code> vs pandas 的 <code>s.var()</code>",
         "<strong>有差</strong>：NumPy 預設 ddof=0，pandas 預設 ddof=1"],
        ["<code>A[[0,1]]</code> vs <code>A[np.array([False,True])]</code>",
         "整數索引挑「第 0、1 列」；布林索引挑「True 的那些列」"],
        ["<code>X.mean(1)</code> vs <code>X.mean(1, keepdims=True)</code>",
         "前者 <code>(10,)</code> 廣播會對錯邊；後者 <code>(10,1)</code> 才對得回列"],
        ["<code>np.random.normal</code> vs <code>rng.normal</code>",
         "前者動到全域狀態；後者是你自己的產生器，可重現"]])}

{info("三個一定要記住的觀念",
      "<strong>1. shape 是 (列, 欄)，列在前。</strong>看不懂錯誤訊息就先印 shape。<br>"
      "<strong>2. reshape 與切片給的是檢視，花式索引與布林索引給的是複本。</strong>"
      "不確定就 <code>.copy()</code>。<br>"
      "<strong>3. axis 指的是被摺掉的那一維。</strong>"
      "axis=0 往下摺得到欄的統計量，axis=1 往右摺得到列的統計量。")}

{ver_note((2,))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
# 六個手寫 SVG 元件的初始化<strong>刻意放在 HC.ready() 外面</strong>：
# Chart.js 從 CDN 載不到時 HC.ready() 不會執行，放進去它們會跟著死掉，
# 就白費了單檔自足的設計（STYLE_CONTRACT §5）。
PAGEJS = r"""
/* ═══ w16la 串列 vs 陣列 ═══ */
const w16laS = HC.svg('w16listArrSvg', {h: 300});
let w16laMode = 0;
function w16laBox(g, x, y, v, fill, w) {
  w = w || 46;
  w16laS.add('rect', {x: x, y: y, width: w, height: 34, rx: 5,
                      fill: fill, stroke: HC.tok.cardBorder, 'stroke-width': 1.5}, g);
  const t = w16laS.add('text', {x: x + w / 2, y: y + 22, 'text-anchor': 'middle',
                                cls: 'vlab', 'font-family': HC.MONO}, g);
  t.textContent = String(v);
}
function w16laDraw() {
  const g = w16laS.clearLayer('main');
  const xs = [3, 4, 5], ys = [4, 9, 7];
  const isArr = w16laMode === 1;
  w16laS.txtPx(24, 30, isArr ? 'np.array([3, 4, 5])' : 'x = [3, 4, 5]',
               {cls: 'axtitle'}, g);
  xs.forEach((v, i) => w16laBox(g, 24 + i * 54, 44, v, HC.tok.card));
  w16laS.txtPx(24, 108, isArr ? 'np.array([4, 9, 7])' : 'y = [4, 9, 7]',
               {cls: 'axtitle'}, g);
  ys.forEach((v, i) => w16laBox(g, 24 + i * 54, 122, v, HC.tok.card));
  w16laS.txtPx(24, 186, 'x + y', {cls: 'axtitle'}, g);
  let out;
  if (isArr) {
    out = xs.map((v, i) => v + ys[i]);
    out.forEach((v, i) => w16laBox(g, 24 + i * 54, 200, v, HC.tok.accent2));
    for (let i = 0; i < 3; i++) {
      w16laS.add('path', {d: 'M' + (47 + i * 54) + ' 82 V 118', stroke: HC.tok.accent2,
                          'stroke-width': 2, 'marker-end': '', fill: 'none',
                          'stroke-dasharray': '4 3'}, g);
    }
  } else {
    out = xs.concat(ys);
    out.forEach((v, i) => w16laBox(g, 24 + i * 54, 200, v, HC.tok.accent3));
  }
  document.getElementById('w16laList').textContent = isArr ? '（切到陣列了）' : '[3, 4, 5, 4, 9, 7]';
  document.getElementById('w16laArr').textContent = isArr ? 'array([ 7, 13, 12])' : '（切到串列了）';
  document.getElementById('w16laLen').textContent = String(out.length);
  setStatus('w16laStatus', isArr
    ? '陣列：位置對齊之後逐元素相加，長度還是 <b>3</b>。'
    : '串列：直接把 y 接在 x 後面，長度變成 <b>6</b>。');
}
function w16laTog() { w16laMode = 1 - w16laMode; w16laDraw(); }
function w16laReset() { w16laMode = 0; w16laDraw(); }
if (w16laS) w16laDraw();

/* ═══ w16rs reshape ═══ */
const w16rsS = HC.svg('w16reshapeSvg', {h: 320});
let w16rsR = 1, w16rsC = 6;
function w16rsDraw() {
  const g = w16rsS.clearLayer('main');
  const vals = [1, 2, 3, 4, 5, 6];
  const cw = 62, ch = 40;
  const x0 = 310 - w16rsC * cw / 2, y0 = 150 - w16rsR * ch / 2;
  w16rsS.txtPx(24, 34, 'x = np.array([1, 2, 3, 4, 5, 6])', {cls: 'axtitle'}, g);
  for (let r = 0; r < w16rsR; r++) {
    for (let c = 0; c < w16rsC; c++) {
      const x = x0 + c * cw, y = y0 + r * ch;
      w16rsS.add('rect', {x: x, y: y, width: cw - 8, height: ch - 8, rx: 5,
                          fill: HC.tok.card, stroke: HC.tok.accent2, 'stroke-width': 1.6}, g);
      const t = w16rsS.add('text', {x: x + (cw - 8) / 2, y: y + 22, 'text-anchor': 'middle',
                                    cls: 'vlab', 'font-family': HC.MONO}, g);
      t.textContent = String(vals[r * w16rsC + c]);
    }
  }
  w16rsS.txtPx(310, 264, '底下永遠是同一塊記憶體，順序 1→2→3→4→5→6 沒有變過',
               {cls: 'axlab', anchor: 'middle'}, g);
  const sh = w16rsR === 1 ? '(6,)' : '(' + w16rsR + ', ' + w16rsC + ')';
  document.getElementById('w16rsShape').textContent = sh;
  document.getElementById('w16rsDim').textContent = w16rsR === 1 ? '1' : '2';
  document.getElementById('w16rsRead').textContent =
    w16rsR === 1 ? '一排六個' : w16rsR + ' 列 ' + w16rsC + ' 欄';
  setStatus('w16rsStatus', 'reshape 成 <b>' + sh + '</b>：先填滿一列再換下一列（C 順序）。');
}
function w16rsSet(r, c) { w16rsR = r; w16rsC = c; w16rsDraw(); }
if (w16rsS) w16rsDraw();
"""

PAGEJS += r"""
/* ═══ w16idx 4×4 索引器 ═══ */
const w16idxS = HC.svg('w16idxSvg', {h: 340});
const w16idxCases = [
  {e: 'A', sh: '(4, 4)', v: '全部 16 個', sel: null},
  {e: 'A[[1,3]]', sh: '(2, 4)', v: '第 1、3 列', sel: [[1,0],[1,1],[1,2],[1,3],[3,0],[3,1],[3,2],[3,3]]},
  {e: 'A[:,[0,2]]', sh: '(4, 2)', v: '第 0、2 欄', sel: [[0,0],[1,0],[2,0],[3,0],[0,2],[1,2],[2,2],[3,2]]},
  {e: 'A[[1,3],[0,2]]', sh: '(2,)', v: '只有 4 與 14', sel: [[1,0],[3,2]]},
  {e: 'A[np.ix_([1,3],[0,2])]', sh: '(2, 2)', v: '4、6、12、14', sel: [[1,0],[1,2],[3,0],[3,2]]},
  {e: 'A[1:4:2,0:3:2]', sh: '(2, 2)', v: '4、6、12、14', sel: [[1,0],[1,2],[3,0],[3,2]]}
];
let w16idxCur = 0;
function w16idxDraw() {
  const g = w16idxS.clearLayer('main');
  const c = w16idxCases[w16idxCur];
  const cw = 64, chh = 46, x0 = 176, y0 = 74;
  for (let r = 0; r < 4; r++) {
    for (let k = 0; k < 4; k++) {
      const on = c.sel === null || c.sel.some(p => p[0] === r && p[1] === k);
      const x = x0 + k * cw, y = y0 + r * chh;
      w16idxS.add('rect', {x: x, y: y, width: cw - 6, height: chh - 6, rx: 5,
                           fill: on ? HC.tok.accent2 : HC.tok.card,
                           stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                           opacity: on ? 1 : 0.45}, g);
      const t = w16idxS.add('text', {x: x + (cw - 6) / 2, y: y + 28, 'text-anchor': 'middle',
                                     cls: 'vlab', 'font-family': HC.MONO,
                                     fill: on ? HC.tok.paper : HC.tok.muted}, g);
      t.textContent = String(r * 4 + k);
    }
    const rl = w16idxS.add('text', {x: x0 - 16, y: y0 + r * chh + 28, 'text-anchor': 'end',
                                    cls: 'axlab'}, g);
    rl.textContent = '列 ' + r;
  }
  for (let k = 0; k < 4; k++) {
    const cl = w16idxS.add('text', {x: x0 + k * cw + (cw - 6) / 2, y: y0 - 10,
                                    'text-anchor': 'middle', cls: 'axlab'}, g);
    cl.textContent = '欄 ' + k;
  }
  w16idxS.txtPx(24, 34, c.e, {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w16idxExpr').textContent = c.e;
  document.getElementById('w16idxShape').textContent = c.sh;
  document.getElementById('w16idxVals').textContent = c.v;
  setStatus('w16idxStatus', w16idxCur === 3
    ? '看到了嗎——只有<b>兩格</b>。兩個串列被逐位配對成 (1,0) 與 (3,2)。'
    : '這個寫法拿到 <b>' + c.v + '</b>，shape 是 <b>' + c.sh + '</b>。');
}
function w16idxSet(i) { w16idxCur = i; w16idxDraw(); }
if (w16idxS) w16idxDraw();

/* ═══ w16mask 布林遮罩 ═══ */
const w16maskS = HC.svg('w16maskSvg', {h: 320});
const w16maskVals = [3, 11, 7, 15, 4, 12, 9, 2];
let w16maskThr = 8;
function w16maskDraw() {
  const g = w16maskS.clearLayer('main');
  const bh = 30, y0 = 52, x0 = 60, maxv = 16, scale = 16;
  const keep = [];
  w16maskVals.forEach((v, i) => {
    const y = y0 + i * bh;
    const on = v > w16maskThr;
    if (on) keep.push(i);
    w16maskS.add('rect', {x: x0, y: y, width: v * scale, height: bh - 8, rx: 3,
                          fill: on ? HC.tok.accent2 : HC.tok.muted,
                          opacity: on ? 0.95 : 0.35}, g);
    const lb = w16maskS.add('text', {x: x0 - 8, y: y + 16, 'text-anchor': 'end', cls: 'axlab'}, g);
    lb.textContent = '列 ' + i;
    const vt = w16maskS.add('text', {x: x0 + v * scale + 8, y: y + 16, cls: 'vlab',
                                     'font-family': HC.MONO}, g);
    vt.textContent = String(v);
    const bt = w16maskS.add('text', {x: 452, y: y + 16, cls: 'vlab', 'font-family': HC.MONO,
                                     fill: on ? HC.tok.accent2 : HC.tok.muted}, g);
    bt.textContent = on ? 'True' : 'False';
  });
  const tx = x0 + w16maskThr * scale;
  w16maskS.add('line', {x1: tx, y1: 40, x2: tx, y2: y0 + w16maskVals.length * bh - 4,
                        stroke: HC.tok.accent, 'stroke-width': 2.5,
                        'stroke-dasharray': '6 4'}, g);
  const tl = w16maskS.add('text', {x: tx, y: 32, 'text-anchor': 'middle', cls: 'axtitle',
                                   fill: HC.tok.accent}, g);
  tl.textContent = '門檻 ' + w16maskThr;
  w16maskS.txtPx(452, 40, 'mask', {cls: 'axtitle'}, g);
  document.getElementById('w16maskThr').textContent = String(w16maskThr);
  document.getElementById('w16maskVec').textContent =
    '[' + w16maskVals.map(v => (v > w16maskThr ? 'T' : 'F')).join(' ') + ']';
  document.getElementById('w16maskN').textContent = keep.length + ' 列';
  setStatus('w16maskStatus', 'A[mask] 會留下 <b>' + keep.length +
            '</b> 列——遮罩本身永遠是 <b>8</b> 個布林值，跟原資料一樣長。');
}
function w16maskStep(d) {
  w16maskThr = Math.max(0, Math.min(16, w16maskThr + d));
  w16maskDraw();
}
function w16maskReset() { w16maskThr = 8; w16maskDraw(); }
if (w16maskS) w16maskDraw();
"""

PAGEJS += r"""
/* ═══ w16bc 廣播三步驟（本頁招牌元件）═══ */
const w16bcS = HC.svg('w16bcastSvg', {h: 340});
const w16bcCases = [
  {a: [10, 3], b: [3], ok: true, out: '(10, 3)'},
  {a: [10, 3], b: [10, 1], ok: true, out: '(10, 3)'},
  {a: [10, 3], b: [10], ok: false, out: '✗ 報錯'}
];
let w16bcI = 0, w16bcStep_ = 0;
function w16bcShapeTxt(s) { return '(' + s.join(', ') + (s.length === 1 ? ',' : '') + ')'; }
function w16bcDraw() {
  const g = w16bcS.clearLayer('main');
  const c = w16bcCases[w16bcI];
  const step = w16bcStep_;
  const a = c.a.slice();
  let b = c.b.slice();
  if (step >= 1) { while (b.length < a.length) b.unshift(1); }
  const cw = 108, yA = 96, yB = 156, yO = 236;
  const nmax = Math.max(a.length, b.length);
  const x0 = 330 - nmax * cw / 2;
  /* B 一律靠右畫 —— 「右對齊」就是這一節要看的東西，不能畫成靠左 */
  const drawRow = (arr, y, label, colors, startCol) => {
    const sc = startCol || 0;
    const lb = w16bcS.add('text', {x: x0 - 18, y: y + 26, 'text-anchor': 'end', cls: 'axtitle'}, g);
    lb.textContent = label;
    arr.forEach((v, i) => {
      const x = x0 + (sc + i) * cw;
      w16bcS.add('rect', {x: x, y: y, width: cw - 12, height: 38, rx: 5,
                          fill: colors ? colors[i] : HC.tok.card,
                          stroke: HC.tok.cardBorder, 'stroke-width': 1.5}, g);
      const t = w16bcS.add('text', {x: x + (cw - 12) / 2, y: y + 25, 'text-anchor': 'middle',
                                    cls: 'vlab', 'font-family': HC.MONO}, g);
      t.textContent = String(v);
    });
  };
  drawRow(a, yA, 'A');
  let bcol = null;
  if (step >= 2) {
    bcol = b.map((v, i) => (v === a[i + (a.length - b.length)] ? HC.tok.card
                            : (v === 1 ? HC.tok.accent2 : HC.tok.resid)));
    /* 注意：step>=1 之後 b 已經補到跟 a 一樣長，位移是 0 */
  }
  const bOff = a.length - b.length;
  drawRow(b, yB, 'B', bcol, bOff);
  if (step >= 2) {
    b.forEach((v, i) => {
      if (v === 1 && a[i] !== 1) {
        const x = x0 + (bOff + i) * cw + (cw - 12) / 2;
        w16bcS.add('path', {d: 'M' + x + ' ' + (yB - 6) + ' V ' + (yA + 44),
                            stroke: HC.tok.accent2, 'stroke-width': 2, fill: 'none',
                            'stroke-dasharray': '4 3'}, g);
        const tt = w16bcS.add('text', {x: x + 30, y: yB - 12, cls: 'axlab',
                                       fill: HC.tok.accent2}, g);
        tt.textContent = '1 → ' + a[i];
      }
    });
  }
  if (step >= 3) {
    drawRow(c.ok ? a : b.map((v, i) => (v === a[i] || v === 1 ? v : '✗')), yO,
            c.ok ? '結果' : '對不上',
            c.ok ? a.map(() => HC.tok.accent2) : b.map((v, i) =>
              (v === a[i] || v === 1 ? HC.tok.card : HC.tok.resid)), 0);
  }
  const names = ['① 右對齊', '② 缺的維度補 1', '③ 長度 1 的維度拉伸'];
  w16bcS.txtPx(24, 34, step === 0 ? '按「單步」開始' : names[Math.min(step, 3) - 1],
               {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w16bcA').textContent = w16bcShapeTxt(c.a);
  document.getElementById('w16bcB').textContent = w16bcShapeTxt(c.b);
  document.getElementById('w16bcOut').textContent = step >= 3 ? c.out : '—';
  setStatus('w16bcStatus', step === 0
    ? '選好 shape 了，按「單步」看 NumPy 怎麼對齊。'
    : (step >= 3
       ? (c.ok ? '可以廣播，結果是 <b>' + c.out + '</b>。'
               : '第二維是 3 對 10，既不相等也沒有一邊是 1 —— <b>報錯</b>。')
       : names[step - 1] + '：' + (step === 1 ? 'shape 從右邊開始對齊'
                                             : '長度 1 的那一維可以被拉伸')));
}
function w16bcStep() { w16bcStep_ = Math.min(3, w16bcStep_ + 1); w16bcDraw(); }
function w16bcCase(i) { w16bcI = i; w16bcStep_ = 0; w16bcDraw(); }
function w16bcReset() { w16bcStep_ = 0; w16bcDraw(); }
if (w16bcS) w16bcDraw();

/* ═══ w16ax axis 摺疊方向 ═══ */
const w16axS = HC.svg('w16axisSvg', {h: 320});
let w16axMode = 0;
function w16axDraw() {
  const g = w16axS.clearLayer('main');
  const rows = 5, cols = 3, cw = 58, chh = 38, x0 = 190, y0 = 78;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      w16axS.add('rect', {x: x0 + c * cw, y: y0 + r * chh, width: cw - 8, height: chh - 8,
                          rx: 4, fill: HC.tok.card, stroke: HC.tok.cardBorder,
                          'stroke-width': 1.3}, g);
    }
  }
  const arrow = (x1, y1, x2, y2) => {
    w16axS.add('path', {d: 'M' + x1 + ' ' + y1 + ' L ' + x2 + ' ' + y2,
                        stroke: HC.tok.accent, 'stroke-width': 2.6, fill: 'none'}, g);
    w16axS.add('path', {d: 'M' + x2 + ' ' + y2 + ' l -5 -7 l 10 0 z',
                        fill: HC.tok.accent,
                        transform: 'rotate(' + (x1 === x2 ? 180 : 90) + ' ' + x2 + ' ' + y2 + ')'}, g);
  };
  let call, which, shape;
  if (w16axMode === 0) {
    for (let c = 0; c < cols; c++) {
      arrow(x0 + c * cw + 25, y0 - 6, x0 + c * cw + 25, y0 + rows * chh + 4);
      w16axS.add('rect', {x: x0 + c * cw, y: y0 + rows * chh + 12, width: cw - 8, height: 30,
                          rx: 4, fill: HC.tok.accent2}, g);
    }
    call = 'X.mean(0)'; which = '列（axis 0）'; shape = '(3,)';
  } else if (w16axMode === 1) {
    for (let r = 0; r < rows; r++) {
      arrow(x0 - 6, y0 + r * chh + 15, x0 + cols * cw + 4, y0 + r * chh + 15);
      w16axS.add('rect', {x: x0 + cols * cw + 12, y: y0 + r * chh, width: cw - 8,
                          height: chh - 8, rx: 4, fill: HC.tok.accent2}, g);
    }
    call = 'X.mean(1)'; which = '欄（axis 1）'; shape = '(5,)';
  } else {
    w16axS.add('rect', {x: x0, y: y0, width: cols * cw - 8, height: rows * chh - 8, rx: 6,
                        fill: 'none', stroke: HC.tok.accent, 'stroke-width': 2.5,
                        'stroke-dasharray': '7 4'}, g);
    w16axS.add('rect', {x: x0 + cols * cw / 2 - 25, y: y0 + rows * chh + 12, width: 50,
                        height: 30, rx: 4, fill: HC.tok.accent2}, g);
    call = 'X.mean()'; which = '全部'; shape = '純量';
  }
  w16axS.txtPx(24, 34, 'X 的 shape 是 (5, 3)', {cls: 'axtitle'}, g);
  document.getElementById('w16axCall').textContent = call;
  document.getElementById('w16axWhich').textContent = which;
  document.getElementById('w16axShape').textContent = shape;
  setStatus('w16axStatus', '<b>' + call + '</b> 摺掉 ' + which + '，結果 shape 是 <b>' + shape + '</b>。');
}
function w16axSet(m) { w16axMode = m; w16axDraw(); }
if (w16axS) w16axDraw();
"""

PAGEJS += r"""
/* ═══ w16rd 亂數與種子（Chart.js；載不到時退 .chart-fallback）═══ */
let w16rdSeeded = true, w16rdN = 50, w16rdRun = 0;
function w16rdSample() {
  const seed = w16rdSeeded ? 1303 : (1303 + w16rdRun * 7919);
  const rand = HC.stat.lcg(seed);
  const out = [];
  for (let i = 0; i < w16rdN; i++) out.push(HC.stat.normal(rand));
  return out;
}
function w16rdBins(xs) {
  const lo = -3, hi = 3, k = 24, counts = new Array(k).fill(0);
  xs.forEach(v => {
    const j = Math.max(0, Math.min(k - 1, Math.floor((v - lo) / (hi - lo) * k)));
    counts[j] += 1;
  });
  return counts.map(c => c / xs.length);
}
function w16rdRender() {
  const xs = w16rdSample();
  const dens = w16rdBins(xs);
  const labels = HC.stat.seq(-3, 3, 24).map(v => HC.fmt(v, 1));
  const m = HC.stat.mean(xs), s = HC.stat.sd(xs);
  document.getElementById('w16rdN').textContent = String(w16rdN);
  document.getElementById('w16rdMean').textContent = HC.fmt(m, 3);
  document.getElementById('w16rdSd').textContent = HC.fmt(s, 3);
  setStatus('w16rdStatus', w16rdSeeded
    ? '種子固定在 1303：<b>再按幾次，圖一動也不動</b>，樣本平均永遠是 ' + HC.fmt(m, 3) + '。'
    : '沒有固定種子：每按一次就換一組數，樣本平均這次是 ' + HC.fmt(m, 3) + '。');
  if (!HC.hasChart()) return;
  const c = HC.get('w16randChart');
  if (c) {
    c.data.labels = labels;
    c.data.datasets[0].data = dens;
    c.update();
    return;
  }
  HC.bar('w16randChart', {
    labels: labels,
    datasets: [{label: '相對次數', data: dens, backgroundColor: HC.tok.accent2,
                borderColor: HC.tok.accent2, borderWidth: 0}]
  }, {
    scales: {x: {title: {display: true, text: '標準常態抽樣值'}},
             y: {title: {display: true, text: '相對次數'}, beginAtZero: true}},
    plugins: {legend: {display: false}}
  });
}
function w16rdSeedTog() {
  w16rdSeeded = !w16rdSeeded;
  document.getElementById('w16rdSeedBtn').textContent = '固定種子：' + (w16rdSeeded ? '開' : '關');
  w16rdRender();
}
function w16rdSize() { w16rdN = w16rdN === 50 ? 500 : 50; w16rdDraw(); }
function w16rdReset() {
  w16rdSeeded = true; w16rdN = 50; w16rdRun = 0;
  document.getElementById('w16rdSeedBtn').textContent = '固定種子：開';
  w16rdRender();
}
function w16rdDraw() { w16rdRun += 1; w16rdRender(); }
HC.ready(() => { w16rdRender(); });
"""

apply("p3_numpy", BODIES, PAGEJS)
