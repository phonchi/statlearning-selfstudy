#!/usr/bin/env python3
"""p2_flow_functions.html（先備 P2 · 流程與函式）完整自學充實。冪等。

內容依據：Ch05-resample-lab-zh.ipynb 的 evalMSE 與 boot_SE 兩個自訂函式
（儲存格 24–26、59–61），以及 Ch02-statlearn-lab-zh.ipynb 的布林條件
（226–232）、for 迴圈（236–240）與那個很好用的錯誤訊息（152）。

這一頁的重點是：課程 lab 裡的函式不是教學範例，是老師真的拿來跑實驗的工具。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, hl, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LAB2 = "Ch02-statlearn-lab-zh.ipynb"
LAB5 = "Ch05-resample-lab-zh.ipynb"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB2 if ch == 2 else LAB5
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 為什麼要寫函式 ────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>先用三個小動作認識流程：依條件選一條路、對每個數字重做一次、把步驟包成可重用的函式。這一頁先練 Python，再連回課程的模型程式。把重複步驟寫成一個函式，修改時較不容易漏改其中一份。</p>
{hl("mpg = 30\nif mpg >= 25:\n    print('達到門檻')\nelse:\n    print('未達門檻')")}
  <p>這是自訂語法練習，不是 lab 的實跑輸出。先猜會執行哪一個 print，再把 mpg 改成 20 重跑。冒號開始區塊；同一區塊的縮排必須一致。</p>
{quiz("qWhy", "PART 00 · 自我檢測",
      "同一段分析程式碼在 notebook 裡複製了三次。最大的風險是什麼？",
      [(False, "檔案變大，跑得比較慢",
        "三十行跟九十行的執行時間差別可以忽略。風險不在效能。"),
       (True, "改了一份忘了改另外兩份，而且不會有人告訴你",
        "對。程式照樣跑完、照樣有數字，只是其中兩個數字是用舊邏輯算的。"
        "這種<strong>沉默的錯</strong>比報錯難查一百倍。"),
       (False, "會有變數名稱衝突",
        "有可能，但那通常會直接報錯或給出明顯離譜的結果，反而好查。")])}
"""

# ── P01 條件與布林 ─────────────────────────────────────────────────────
BODIES["cond"] = f"""
  <p>上面的 <code>if</code> 只要一個真假值。可以用 <code>and</code>／<code>or</code> 合併純量條件，例如 <code>mpg &gt; 25 and year &gt; 80</code>。先熟悉這一種，再看下面一整欄同時判斷的寫法。</p>
{hl("values = [18, 30, 24]\nfor mpg in values:\n    if mpg >= 25:\n        print(mpg)")}
  <p>這個自訂例子依序取出三個數字，每次都做相同判斷。下面的 NumPy／pandas 遮罩把整欄一起判斷；若尚不熟資料表，可以先讀下一節的基本迴圈，學完 P3、P4 再回來對照。</p>
{info("一句話講完差別",
      "<code>and</code> 一次只能判斷<strong>一個</strong>真假值；"
      "<code>&amp;</code> 是<strong>逐元素</strong>做「且」，一整排一起算。"
      "選資料的時候永遠是後者，而且<strong>每個條件都要用括號包起來</strong>，"
      "因為 <code>&amp;</code> 的優先順序比 <code>&gt;</code> 高。", "warm")}

{viz(svg("w15boolSvg", 320),
     [info_card("看每一列各自的結果",
                "兩個條件各自產生一整排 True／False，"
                "<code>&amp;</code> 把它們<strong>逐列</strong>做「且」。"
                "按按鈕切換運算子。"),
      rows_card("目前",
                [("運算子", "&", "w15blOp"),
                 ("留下幾列", "—", "w15blN"),
                 ("會不會報錯", "不會", "w15blErr")]),
      info_card("忘記括號的下場",
                "<code>df['year'] &gt; 80 &amp; df['mpg'] &gt; 30</code> 會被讀成 "
                "<code>df['year'] &gt; (80 &amp; df['mpg']) &gt; 30</code>，"
                "然後拋一個看起來莫名其妙的錯。"
                "<strong>每個條件都包括號</strong>，這條沒有例外。")],
     "w15blStatus", "兩個條件，逐列做「且」。",
     '<button class="btn btn-toggle" onclick="w15blSet(0)">year &gt; 80</button>'
     '<button class="btn btn-toggle" onclick="w15blSet(1)">mpg &gt; 30</button>'
     '<button class="btn btn-toggle" onclick="w15blSet(2)">兩者皆是（&amp;）</button>'
     '<button class="btn btn-toggle" onclick="w15blSet(3)">任一成立（|）</button>',
     provenance=("course-data", "依 Ch02 lab 的 Auto 條件篩選語法重繪。"))}

{card("一個條件", C(2, 226), O(2, 226), src=S(2, 226),
      note="先算出一整排 True／False，再拿它去 <code>loc</code> 選列。")}

{card("兩個條件用 & 串起來", C(2, 230), O(2, 230), src=S(2, 230),
      note="注意<strong>兩個條件各自都有括號</strong>。"
           "另外這裡用了 <code>lambda df:</code>。它讓你在鏈式操作中間也能引用「當下這張表」。")}

{card("& 與 | 混用", C(2, 232), O(2, 232), src=S(2, 232),
      note="排氣量小於 300，<strong>而且</strong>（是 ford <strong>或</strong> datsun）。"
           "括號決定了誰先算，跟數學一樣。")}

{table(["情境", "用什麼", "為什麼"],
       [["一個 if 判斷", "<code>and</code> / <code>or</code> / <code>not</code>",
         "只有一個真假值"],
        ["選 DataFrame 的列", "<code>&amp;</code> / <code>|</code> / <code>~</code>",
         "一整排真假值要逐元素算"],
        ["NumPy 陣列的條件", "<code>&amp;</code> / <code>|</code> / <code>~</code>", "同上"],
        ["檢查「有沒有任何一個」", "<code>.any()</code> / <code>.all()</code>",
         "把一整排收成一個真假值"]])}

{quiz("qCond", "PART 01 · 自我檢測",
      "<code>Auto[(Auto['year'] &gt; 80) and (Auto['mpg'] &gt; 30)]</code> 會發生什麼？",
      [(True, "報錯：一整排真假值沒辦法縮成單一個真或假",
        "對。<code>and</code> 想知道「左邊整體是真還是假」，"
        "但左邊是 392 個真假值，Python 不知道該算成什麼，"
        "所以拋 <code>ValueError: The truth value of a Series is ambiguous</code>。"
        "改用 <code>&amp;</code> 就對了。"),
       (False, "正常執行，跟用 <code>&amp;</code> 一樣",
        "不一樣。<code>and</code> 是純 Python 的邏輯運算，它不做逐元素的事。"),
       (False, "只會用到第一個條件",
        "不會悄悄忽略。它會直接報錯。這其實是好事，沉默的錯才可怕。")])}
"""

# ── P02 迴圈 ────────────────────────────────────────────────────────────
BODIES["loop"] = f"""
  <p>迴圈就是「把同一件事對每一個東西各做一次」。統計程式裡它出現在三個地方：
  <strong>試不同的參數</strong>（多項式次數、λ）、<strong>重抽樣</strong>（自助法的 B 次）、
  <strong>逐欄處理</strong>（每一欄算遺漏比例）。</p>

{viz(svg("w15loopSvg", 320),
     [info_card("跟著跑一次",
                "按「單步」走 <code>total += value</code> 這個迴圈，"
                "右邊的變數表會同步更新。這正是 lab 儲存格 236 的那一段。"),
      rows_card("目前",
                [("第幾圈", "0 / 3", "w15lpIter"),
                 ("value", "—", "w15lpVal"),
                 ("total", "0", "w15lpTotal")]),
      info_card("自助法就是這個形狀",
                "第 5 章的 <code>boot_SE</code> 裡面是 "
                "<code>for _ in range(B):</code>，B 通常是 1000。"
                "看懂這個三圈的迴圈，那個一千圈的也就看懂了。")],
     "w15lpStatus", "按「單步」跟著跑一次。",
     '<button class="btn btn-step" onclick="w15lpStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w15lpPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w15lpReset()">重置</button>',
     provenance=("course-data", "依 Ch02 lab 的累加迴圈逐步呈現。"))}

{card("最基本的累加迴圈", C(2, 236), O(2, 236), src=S(2, 236),
      note="<code>total += value</code> 是 <code>total = total + value</code> 的簡寫。"
           "縮排決定了哪些行屬於迴圈裡面——Python 用縮排代替大括號。")}

{card("巢狀迴圈", C(2, 238), O(2, 238), src=S(2, 238),
      note="裡面那圈跑完，外面才前進一格，所以總共跑 3×3 = 9 次。"
           "巢狀兩層以上通常代表該換個寫法了。")}

{card("zip：兩排東西配對走", C(2, 240), O(2, 240), src=S(2, 240),
      note="<code>zip</code> 把兩個串列<strong>逐位配對</strong>，"
           "所以這一段算的是加權平均。長度不一樣時，它會在短的那個結束時停下來。")}

{table(["你想走過什麼", "寫法"],
       [["一個串列的每個元素", "<code>for x in a:</code>"],
        ["連同位置一起", "<code>for i, x in enumerate(a):</code>"],
        ["兩個串列配對", "<code>for x, w in zip(a, ws):</code>"],
        ["跑固定次數", "<code>for _ in range(B):</code>"],
        ["字典的鍵與值", "<code>for k, v in d.items():</code>"],
        ["DataFrame 的每一欄", "<code>for col in df.columns:</code>"]])}

{info("能不用迴圈就不要用",
      "對整排數字做同一個運算時，NumPy 與 pandas 的向量化寫法又快又好讀（P3 接著會介紹）。"
      "迴圈留給「每一圈的內容真的不一樣」的情況——"
      "例如每一圈試一個不同的參數、或每一圈抽一份新的樣本。")}

{quiz("qLoop", "PART 02 · 自我檢測",
      "<code>for value, weight in zip([2,3,19], [0.2,0.3,0.5]):</code> 會跑幾圈？",
      [(True, "3 圈，每一圈拿到一組配對",
        "對。<code>zip</code> 逐位配對，兩個串列都是 3 個，所以跑 3 圈，"
        "每圈的 <code>value</code> 與 <code>weight</code> 是同一個位置的兩個值。"),
       (False, "6 圈，兩個串列各 3 個",
        "那是巢狀迴圈的行為（3×3=9 其實）。<code>zip</code> 是<strong>並排走</strong>，不是相乘。"),
       (False, "9 圈",
        "9 是巢狀迴圈的次數。<code>zip</code> 只走一趟。")])}
"""

# ── P03 函式 ────────────────────────────────────────────────────────────
BODIES["func"] = f"""
  <p>函式有三個部分：<strong>名字</strong>、<strong>參數</strong>（要給它什麼）、
  <strong>回傳值</strong>（它給你什麼）。寫得好的函式就像一個黑盒子——
  用的人只要知道這三件事，不必知道裡面怎麼做。</p>

{hl("def above_threshold(value, threshold=25):\n    return value >= threshold\n\nfor value in [18, 30, 24]:\n    print(above_threshold(value))")}
  <p>這是自訂函式練習。<code>def</code> 定義名字和參數；<code>return</code> 交回真假值，外面的 print 才負責顯示。先改門檻，確認每次呼叫如何使用引數。以下是學完基本語法後的課程應用；OLS、設計矩陣與 MSE 可在 <a href="p6_modeling_api.html">P6</a> 詳讀。</p>
  <p>假設你要比較三種多項式次數的驗證誤差。不寫函式的話，你會把同一段
  「切分 → 配適 → 預測 → 算 MSE」複製三次，只改中間一個數字。
  三份幾乎一樣的程式碼，就是<strong>三個各自會出錯、而且改了一份忘了改另外兩份</strong>的地方。</p>

{info("課程 lab 的做法", "把那一段包成 <code>evalMSE(terms, response, train, test)</code>，"
      "然後用一個迴圈跑三次。程式碼從多份重複變成一份共用邏輯，修改時較容易保持一致。")}

  <p>以下先讀懂函式如何被重用。要實跑，請開啟 <a href="https://github.com/phonchi/nsysu-math524-2025/blob/main/static_files/presentations/Ch05-resample-lab-zh.ipynb">重抽樣方法的課程筆記本</a>，
  先執行套件安裝與匯入（儲存格 3–4）、Auto 資料載入與切分（儲存格 8–16），再執行下面的函式與呼叫。
  這會準備好 <code>MS</code>、<code>sm</code>、<code>poly</code>、<code>Auto_train</code> 與 <code>Auto_valid</code>。</p>

{card("包成一個函式", C(5, 24), src=S(5, 24),
      note="這是課程 lab 真的在用的函式，不是教學範例。"
           "四個參數：要放哪些項、反應變數是誰、訓練集、測試集。")}

{card("然後用迴圈跑三次", C(5, 26), O(5, 26), src=S(5, 26),
      note="三個次數的驗證 MSE 一次算完。"
           "要改成試五個次數，把 <code>range(1, 4)</code> 改成 <code>range(1, 6)</code>，"
           "並把存放結果的 <code>np.zeros(3)</code> 改成 <code>np.zeros(5)</code>，避免陣列越界。")}

{viz(svg("w15whySvg", 320),
     [info_card("兩種寫法並排",
                "左邊是複製貼上三次，右邊是一個函式加一個迴圈。"
                "按「改需求」看「要多試一個次數」這件事在兩邊分別要動幾個地方。"),
      rows_card("目前",
                [("寫法", "複製貼上", "w15whyKind"),
                 ("邏輯有幾份", "—", "w15whyCopies"),
                 ("要改幾個地方", "—", "w15whyEdits")]),
      info_card("這不是美觀問題",
                "統計程式最怕的錯誤是<strong>沉默的錯</strong>——"
                "程式跑完了、有數字、但那個數字是錯的。"
                "重複的程式碼正是這種錯的溫床。")],
     "w15whyStatus", "先看兩邊的長度，再按「改需求」。",
     '<button class="btn btn-toggle" onclick="w15whySet(0)">複製貼上</button>'
     '<button class="btn btn-toggle" onclick="w15whySet(1)">函式 ＋ 迴圈</button>'
     '<button class="btn btn-step" onclick="w15whyEdit()">改需求：多試一個次數</button>'
     '<button class="btn btn-reset" onclick="w15whyReset()">重置</button>',
     provenance=("course-data", "比較 Ch05 lab 的 evalMSE 函式與逐次複製同一分析的維護差異；不以假想行數計量。"))}

{viz(svg("w15fnSvg", 340),
     [info_card("看資料怎麼進出",
                "按「單步」走一次 <code>evalMSE</code>：四個參數進去、"
                "裡面做四件事、一個數字出來。"),
      rows_card("目前",
                [("步驟", "0 / 5", "w15fnStep"),
                 ("這一步", "—", "w15fnWhat"),
                 ("函式裡的區域變數", "—", "w15fnVars")]),
      info_card("return 之後就結束了",
                "碰到 <code>return</code>，函式立刻結束並把值交出去，"
                "後面的行不會執行。沒有寫 <code>return</code> 的函式會回傳 "
                "<code>None</code>——忘記寫是很常見的 bug。")],
     "w15fnStatus", "按「單步」走一次課程 lab 的 evalMSE。",
     '<button class="btn btn-step" onclick="w15fnStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w15fnPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w15fnReset()">重置</button>',
     provenance=("course-data", "依 Ch05 lab 的 evalMSE 函式資料流重繪。"))}

  <p>這個函式由參數接收資料，較容易換資料重用。是否有副作用，還要看它會不會修改傳入物件、全域狀態或檔案。</p>

{qa("觀念釐清", [
    ("參數（parameter）與引數（argument）差在哪？",
     "定義函式時寫的名字叫參數（<code>def evalMSE(terms, response, ...)</code> 裡的 terms）；"
     "呼叫時實際傳進去的值叫引數。日常對話裡兩個字常常混用，看得懂就好。"),
    ("為什麼不要在函式裡直接用外面的變數？",
     "因為那樣它就<strong>不能重複使用</strong>了——換一份資料就得改函式本身。"
     "而且外面的變數被改掉時，函式的行為會跟著變，你卻看不出來。"
     "把需要的東西都當參數傳進去，函式才是一個可以信任的黑盒子。"),
])}

{quiz("qFunc", "PART 03 · 自我檢測",
      "一個函式忘了寫 <code>return</code>，呼叫它會拿到什麼？",
      [(False, "會報錯",
        "不會。Python 允許沒有回傳值的函式（例如只負責畫圖或存檔的那種）。"),
       (True, "<code>None</code>",
        "對，而且這是很難查的 bug——"
        "<code>mse = evalMSE(...)</code> 之後 <code>mse</code> 是 None，"
        "要等到你拿它去算東西才會爆，那時錯誤訊息已經離現場很遠了。"),
       (False, "最後一行的值",
        "那是 R 或 Jupyter 儲存格的行為。Python 的函式一定要明寫 <code>return</code>。")])}
"""

# ── P04 預設引數與作用域 ───────────────────────────────────────────────
BODIES["scope"] = f"""
  <p>兩件事：<strong>預設引數</strong>讓常用的設定不必每次都寫，
  <strong>作用域</strong>決定一個名字在哪裡看得到。
  課程 lab 的 <code>boot_SE</code> 兩者都用上了。</p>

  <p>這個進階應用同樣在重抽樣方法的課程筆記本中執行：先跑儲存格 3–4 的安裝與匯入，
  再跑儲存格 53 建立 <code>Portfolio</code> 與 <code>alpha_func</code>，最後跑下面的儲存格 59、61。
  第一輪先看引數如何傳入即可，bootstrap 的用途留待正課。</p>

{card("有預設值的參數", C(5, 59), src=S(5, 59),
      note="<code>n=None</code>、<code>B=1000</code>、<code>seed=0</code> 都有預設值，"
           "所以呼叫時可以只給前兩個。"
           "<strong>有預設值的參數一定要放在沒有預設值的後面。</strong>")}

{card("呼叫時只覆寫想改的", C(5, 61), src=S(5, 61),
      note="用<strong>關鍵字</strong>指定 <code>B=1000</code>、<code>seed=0</code>，"
           "順序就不重要了，而且讀的人一眼看得出每個數字是什麼意思。")}

{viz(svg("w15scSvg", 320),
     [info_card("誰看得到誰",
                "按按鈕看一個名字在函式裡面與外面分別是什麼。"
                "<strong>函式裡看得到外面，外面看不到裡面。</strong>"),
      rows_card("目前",
                [("情境", "—", "w15scCase"),
                 ("函式裡的值", "—", "w15scIn"),
                 ("函式外的值", "—", "w15scOut")]),
      info_card("可變預設值的陷阱",
                "<code>def f(acc=[])</code> 這種寫法，那個空串列<strong>只會建立一次</strong>，"
                "後續每次呼叫都共用同一個，於是它會越積越多。"
                "要用可變的預設值，寫 <code>def f(acc=None)</code> 再在函式裡面 "
                "<code>if acc is None: acc = []</code>。")],
     "w15scStatus", "三個情境，看名字的可見範圍。",
     '<button class="btn btn-toggle" onclick="w15scSet(0)">函式讀外面的變數</button>'
     '<button class="btn btn-toggle" onclick="w15scSet(1)">函式裡指派同名變數</button>'
     '<button class="btn btn-toggle" onclick="w15scSet(2)">可變預設值的陷阱</button>',
     provenance=("illustrative", "自訂小例子，用來比較 Python 名稱作用域與可變預設值。"))}

{info("為什麼 seed 要當參數",
      "<code>boot_SE(..., seed=0)</code> 把種子做成參數而不是寫死在函式裡，"
      "這樣你既能重現結果（給同一個 seed），也能檢查結果穩不穩定（換幾個 seed 跑跑看）。"
      "這是一個很小但很專業的習慣。")}

{quiz("qScope", "PART 04 · 自我檢測",
      "<code>def add(x, acc=[]):</code> 這樣寫有什麼問題？",
      [(False, "沒問題，這樣預設就是空串列",
        "看起來像，但那個空串列<strong>只在定義函式時建立一次</strong>。"),
       (True, "那個串列所有呼叫共用，會越積越多",
        "對。第一次呼叫加了一個元素，第二次呼叫看到的預設值就不是空的了。"
        "正確寫法是 <code>acc=None</code>，再在函式裡建立新的。"),
       (False, "串列不能當預設值，會報錯",
        "語法上完全合法，不會報錯。這正是它危險的地方。")])}
"""

# ── P05 讀懂錯誤訊息 ───────────────────────────────────────────────────
BODIES["err"] = f"""
  <p>程式報錯不是壞事，是<strong>它在告訴你哪裡不對</strong>。真正該怕的是不報錯的錯。
  Python 的錯誤訊息（traceback）要<strong>從最後一行開始讀</strong>：
  最後一行是錯誤的種類與說明，往上是它發生在哪一行。</p>

{card("一個真的錯誤訊息", C(2, 152), O(2, 152), src=S(2, 152), out_tag="錯誤訊息",
      note="最後一行說得很清楚：<code>shape mismatch</code>，"
           "兩個索引陣列的形狀 (2,) 與 (3,) 沒辦法一起廣播。"
           "看到 shape 就知道要去印 shape。這是 P3 的第一課。")}

{viz(svg("w15errSvg", 320),
     [info_card("從下往上讀",
                "按「單步」，反白會從最後一行往上移動，"
                "右邊說明每一層在告訴你什麼。"),
      rows_card("這一層在說",
                [("層次", "—", "w15erLevel"),
                 ("內容", "—", "w15erWhat"),
                 ("下一步該做什麼", "—", "w15erDo")]),
      info_card("最常見的四種錯",
                "<code>NameError</code> 名字沒定義（多半是打錯字或儲存格沒跑）、"
                "<code>KeyError</code> 欄名不存在、"
                "<code>IndexError</code> 索引超出範圍、"
                "<code>ValueError</code> 型別對但值不合理（形狀對不上多半是這個）。")],
     "w15erStatus", "按「單步」從最後一行往上讀。",
     '<button class="btn btn-step" onclick="w15erStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w15erReset()">重置</button>',
     provenance=("illustrative", "自訂 traceback，用來練習由錯誤末行往上定位。"))}

{info("try / except 不是拿來蓋住錯誤的",
      "<code>try: ... except: pass</code> 會把錯誤吞掉，讓程式帶著錯誤的狀態繼續跑——"
      "那正是你最不想要的「沉默的錯」。"
      "只有在你<strong>知道會發生什麼錯、而且知道該怎麼處理</strong>時才用它，"
      "例如「這個套件在 Colab 上才有，本機沒有就跳過」。", "warm")}

{hl('''try:
    from google.colab import drive
    drive.mount('/content/drive')
except ImportError:
    print('不在 Colab 上，跳過掛載')''')}

{table(["錯誤", "多半的原因", "先去做什麼"],
       [["<code>NameError</code>", "打錯字，或那個儲存格還沒跑", "從上到下重跑一次"],
        ["<code>KeyError</code>", "欄名不存在或打錯", "印 <code>df.columns</code>"],
        ["<code>IndexError</code>", "索引超出範圍", "印 <code>len()</code> 或 <code>shape</code>"],
        ["<code>ValueError: shape mismatch</code>", "兩邊形狀對不上", "印兩邊的 <code>shape</code>"],
        ["<code>TypeError</code>", "型別不對（例如字串當數字加）", "印 <code>type()</code> 或 <code>dtypes</code>"],
        ["<code>NotFittedError</code>", "還沒 fit 就 predict", "檢查有沒有漏跑 fit"]])}

{quiz("qErr", "PART 05 · 自我檢測",
      "traceback 很長，你應該先看哪一行？",
      [(True, "最後一行：錯誤的種類與說明",
        "對。最後一行講的是「發生了什麼事」，這通常直接告訴你要修什麼。"
        "看完再往上找「發生在我寫的哪一行」。"),
       (False, "第一行，因為那是最早發生的",
        "第一行是呼叫堆疊的最外層，多半是你自己那一行的位置沒錯，"
        "但它不會告訴你錯誤的種類。"),
       (False, "中間套件內部的那幾行",
        "那些是套件內部的呼叫路徑，除非你在寫套件，否則幫助不大——"
        "而且很容易讓人誤以為是套件壞了。")])}

{hook("這在本站哪一章會用到",
      '第 5 章的自助法就是一個跑 1000 圈的迴圈，裡面呼叫一個你自己寫的函式；'
      '第 6 章逐一試每個 λ、第 8 章逐一試每個樹深度，形狀都一樣。'
      '接下來是 <a href="p3_numpy.html">P3 NumPy</a>，'
      '那裡會告訴你什麼時候<strong>不</strong>該寫迴圈。')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 布林運算子",
      "你要選出「1980 年後、而且 mpg 大於 30」的車。哪一個寫法對？",
      [(True, "<code>Auto[(Auto['year'] &gt; 80) &amp; (Auto['mpg'] &gt; 30)]</code>",
        "對。逐元素的「且」用 <code>&amp;</code>，而且<strong>每個條件都包括號</strong>——"
        "因為 <code>&amp;</code> 的優先順序比 <code>&gt;</code> 高。"),
       (False, "<code>Auto[Auto['year'] &gt; 80 and Auto['mpg'] &gt; 30]</code>",
        "兩個問題：<code>and</code> 不做逐元素運算，而且沒有括號。"
        "會拋 truth value is ambiguous。"),
       (False, "<code>Auto[Auto['year'] &gt; 80 &amp; Auto['mpg'] &gt; 30]</code>",
        "運算子對了但少了括號，會被讀成 "
        "<code>Auto['year'] &gt; (80 &amp; Auto['mpg']) &gt; 30</code>，然後報一個看不懂的錯。")])}

{quiz("qEx2", "EXERCISE 2 · 迴圈",
      "想對 <code>degrees = [1,2,3]</code> 各算一次 MSE 並收集結果。哪一個寫法最好？",
      [(False, "<code>mse1 = f(1); mse2 = f(2); mse3 = f(3)</code>",
        "能動，但要多試一個次數就得再多寫一行，而且沒辦法用迴圈統一處理結果。"),
       (True, "<code>MSE = [f(d) for d in degrees]</code>（或用 for 迴圈填一個陣列）",
        "對。lab 儲存格 26 用的就是這個形狀（先開一個 <code>np.zeros(3)</code> 再用 "
        "<code>enumerate</code> 填）。要多試幾個次數只要改 degrees。"),
       (False, "寫一個巢狀迴圈，外面跑資料、裡面跑次數",
        "資料只有一份，外層迴圈沒有東西可跑。巢狀是給「兩個維度都要走」的情況用的。")])}

{quiz("qEx3", "EXERCISE 3 · 函式",
      "<code>def boot_SE(func, D, n=None, B=1000, seed=0)</code>。"
      "呼叫時想只改 B，其他都用預設，怎麼寫？",
      [(True, "<code>boot_SE(alpha_func, Portfolio, B=2000)</code>",
        "對。用關鍵字指定，其他參數各自用預設值。"
        "這也是為什麼有預設值的參數要放在後面。"),
       (False, "<code>boot_SE(alpha_func, Portfolio, 2000)</code>",
        "第三個位置是 <code>n</code> 不是 <code>B</code>，"
        "這樣會把 2000 傳給 n。這正是關鍵字引數要解決的問題。"),
       (False, "<code>boot_SE(alpha_func, Portfolio, None, None, 2000)</code>",
        "位置全錯，而且把 2000 傳給了 seed。"
        "位置引數多的時候一律用關鍵字，讀的人也輕鬆。")])}

{quiz("qEx4", "EXERCISE 4 · 錯誤訊息",
      "你看到 <code>KeyError: 'horsepower'</code>。第一件該做的事是？",
      [(False, "改用 <code>try / except</code> 把它包起來",
        "那只是把錯誤藏起來，欄還是拿不到，後面照樣錯，而且變成沉默的錯。"),
       (True, "印 <code>df.columns</code> 看實際的欄名",
        "對。KeyError 的意思就是「這個鍵不存在」，"
        "多半是打錯字、大小寫不同、或前面某一步把欄改名了。"
        "看一眼實際的欄名通常五秒就解決。"),
       (False, "重新下載資料",
        "在確認欄名之前就換資料，是最貴的一步。先看最便宜的證據。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張速查表。</p>

{table(["情境", "用 and / or", "用 &amp; / |"],
       [["一個 if 判斷", "✓", "✗"],
        ["選 DataFrame 的列", "✗（會報錯）", "✓"],
        ["NumPy 陣列的條件", "✗", "✓"],
        ["每個條件要不要括號", "不用", "<b>一定要</b>"],
        ["「非」怎麼寫", "<code>not x</code>", "<code>~mask</code>"]])}

{table(["迴圈寫法", "什麼時候用"],
       [["<code>for x in a:</code>", "只要值"],
        ["<code>for i, x in enumerate(a):</code>", "同時要位置"],
        ["<code>for x, w in zip(a, ws):</code>", "兩排東西並排走"],
        ["<code>for _ in range(B):</code>", "只是要跑 B 次（自助法）"],
        ["<code>[f(x) for x in a]</code>", "把結果收成一個串列"],
        ["向量化（不寫迴圈）", "<b>對整排數字做同一件事時的第一選擇</b>"]])}

{table(["函式的部件", "怎麼寫", "注意"],
       [["定義", "<code>def name(a, b=預設):</code>", "有預設值的參數放後面"],
        ["回傳", "<code>return 值</code>", "沒寫就回傳 None"],
        ["呼叫（位置）", "<code>name(x, y)</code>", "順序不能錯"],
        ["呼叫（關鍵字）", "<code>name(x, b=y)</code>", "參數多時一律用這個"],
        ["可變預設值", "<code>def f(acc=None)</code>", "<b>不要寫 <code>acc=[]</code></b>"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 選資料用 <code>&amp;</code>／<code>|</code>，而且每個條件都包括號。</strong>"
      "<code>and</code> 一次只判斷一個真假值。<br>"
      "<strong>2. 同一段程式碼要寫第三次，就該包成函式。</strong>"
      "重複是沉默的錯的溫床。<br>"
      "<strong>3. traceback 從最後一行讀起。</strong>"
      "最後一行說錯在哪，往上找是誰呼叫的。")}

{ver_note((2, 5))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* ═══ w15why 複製貼上 vs 函式 ═══ */
const w15whyS = HC.svg('w15whySvg', {h: 320});
let w15whyMode = 0, w15whyEdited = false;
function w15whyDraw() {
  const g = w15whyS.clearLayer('main');
  const copy = w15whyMode === 0;
  const n = copy ? (w15whyEdited ? 4 : 3) : 1;
  w15whyS.txtPx(24, 34, copy ? '複製貼上：每一種次數各一份' : '一個函式 ＋ 一個迴圈',
                {cls: 'axtitle', fill: copy ? HC.tok.resid : HC.tok.accent2}, g);
  if (copy) {
    for (let b = 0; b < n; b++) {
      const x = 40 + b * 145;
      w15whyS.add('rect', {x: x, y: 62, width: 130, height: 190, rx: 7,
                           fill: HC.tok.resid, opacity: w15whyEdited && b === n - 1 ? 0.5 : 0.22,
                           stroke: HC.tok.resid, 'stroke-width': 1.6}, g);
      for (let i = 0; i < 8; i++) {
        w15whyS.add('rect', {x: x + 12, y: 76 + i * 22, width: 90 + (i % 3) * 12, height: 10,
                             rx: 5, fill: HC.tok.ink, opacity: 0.4}, g);
      }
      const t = w15whyS.add('text', {x: x + 65, y: 270, 'text-anchor': 'middle',
                                     cls: 'axlab'}, g);
      t.textContent = 'degree = ' + (b + 1);
    }
  } else {
    w15whyS.add('rect', {x: 40, y: 62, width: 250, height: 190, rx: 7,
                         fill: HC.tok.accent2, opacity: 0.22,
                         stroke: HC.tok.accent2, 'stroke-width': 1.6}, g);
    for (let i = 0; i < 8; i++) {
      w15whyS.add('rect', {x: 56, y: 76 + i * 22, width: 150 + (i % 3) * 20, height: 10,
                           rx: 5, fill: HC.tok.ink, opacity: 0.4}, g);
    }
    w15whyS.txtPx(165, 270, 'def evalMSE(...)', {cls: 'axlab', anchor: 'middle'}, g);
    w15whyS.add('rect', {x: 330, y: 100, width: 240, height: 84, rx: 7,
                         fill: HC.tok.accent, opacity: 0.25,
                         stroke: HC.tok.accent, 'stroke-width': 1.6}, g);
    for (let i = 0; i < 3; i++) {
      w15whyS.add('rect', {x: 348, y: 114 + i * 22, width: 130 + i * 20, height: 10,
                           rx: 5, fill: HC.tok.ink, opacity: 0.4}, g);
    }
    w15whyS.txtPx(450, 204, w15whyEdited ? 'for d in range(1, 5)' : 'for d in range(1, 4)',
                  {cls: 'axlab', anchor: 'middle'}, g);
  }
  document.getElementById('w15whyKind').textContent = copy ? '複製貼上' : '函式 ＋ 迴圈';
  document.getElementById('w15whyCopies').textContent = copy ? n + ' 份' : '1 份';
  document.getElementById('w15whyEdits').textContent = w15whyEdited
    ? (copy ? '新增一份副本，之後每份都要同步' : '只改迴圈的範圍') : '—';
  setStatus('w15whyStatus', w15whyEdited
    ? (copy ? '要多試一個次數，得<b>再複製一整段</b>，而且四份都要記得同步維護。'
            : '要多試一個次數，只改 <b>range 的那個數字</b>。')
    : (copy ? '三份幾乎一樣的程式碼，三個各自會出錯的地方。'
            : '一份邏輯，一個迴圈。錯只會錯在一個地方。'));
}
function w15whySet(m) { w15whyMode = m; w15whyDraw(); }
function w15whyEdit() { w15whyEdited = true; w15whyDraw(); }
function w15whyReset() { w15whyMode = 0; w15whyEdited = false; w15whyDraw(); }
if (w15whyS) w15whyDraw();

/* ═══ w15bl 布林逐元素 ═══ */
const w15blS = HC.svg('w15boolSvg', {h: 320});
const w15blRows = [
  {name: 'toyota starlet', year: 81, mpg: 39.1},
  {name: 'ford maverick', year: 70, mpg: 21.0},
  {name: 'plymouth champ', year: 81, mpg: 39.0},
  {name: 'chevrolet impala', year: 73, mpg: 11.0},
  {name: 'honda civic 1300', year: 81, mpg: 35.1},
  {name: 'datsun pl510', year: 70, mpg: 27.0}
];
let w15blI = 2;
function w15blDraw() {
  const g = w15blS.clearLayer('main');
  const f = (r) => {
    const a = r.year > 80, b = r.mpg > 30;
    if (w15blI === 0) return a;
    if (w15blI === 1) return b;
    if (w15blI === 2) return a && b;
    return a || b;
  };
  let keep = 0;
  w15blRows.forEach((r, i) => {
    const on = f(r);
    if (on) keep += 1;
    const y = 76 + i * 36;
    w15blS.add('rect', {x: 40, y: y, width: 232, height: 30, rx: 4,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: on ? 0.95 : 0.5}, g);
    const t = w15blS.add('text', {x: 52, y: y + 20, cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = r.name;
    [[290, r.year > 80, String(r.year)], [396, r.mpg > 30, HC.fmt(r.mpg, 1)]].forEach(c => {
      const v = w15blS.add('text', {x: c[0], y: y + 20, cls: 'vlab', 'font-family': HC.MONO,
                                    fill: c[1] ? HC.tok.accent2 : HC.tok.muted}, g);
      v.textContent = c[2] + (c[1] ? ' ✓' : '');
    });
    const rr = w15blS.add('text', {x: 500, y: y + 20, cls: 'vlab', 'font-family': HC.MONO,
                                   fill: on ? HC.tok.accent : HC.tok.muted}, g);
    rr.textContent = on ? 'True' : 'False';
  });
  ['name', 'year', 'mpg', '結果'].forEach((h, j) => {
    const t = w15blS.add('text', {x: [52, 290, 396, 500][j], y: 62, cls: 'axlab'}, g);
    t.textContent = h;
  });
  const ops = ["Auto['year'] > 80", "Auto['mpg'] > 30",
               "(Auto['year'] > 80) & (Auto['mpg'] > 30)",
               "(Auto['year'] > 80) | (Auto['mpg'] > 30)"];
  w15blS.txtPx(24, 34, ops[w15blI], {cls: 'axtitle', fill: HC.tok.accent}, g);
  document.getElementById('w15blOp').textContent = ['&gt;', '&gt;', '&amp;', '|'][w15blI];
  document.getElementById('w15blN').textContent = keep + ' 列';
  document.getElementById('w15blErr').textContent = '不會（用的是 & 不是 and）';
  setStatus('w15blStatus', '留下 <b>' + keep + '</b> 列。每一列各自算一次，'
            + '所以結果是一整排真假值。');
}
function w15blSet(i) { w15blI = i; w15blDraw(); }
if (w15blS) w15blDraw();

/* ═══ w15lp 迴圈逐步 ═══ */
const w15lpS = HC.svg('w15loopSvg', {h: 320});
const w15lpVals = [3, 2, 19];
let w15lpI = -1, w15lpTimer = null;
function w15lpDraw() {
  const g = w15lpS.clearLayer('main');
  const code = ['total = 0', 'for value in [3, 2, 19]:', '    total += value',
                "print('Total is: {0}'.format(total))"];
  code.forEach((ln, i) => {
    const on = (w15lpI < 0 && i === 0) || (w15lpI >= 0 && w15lpI < 3 && i === 2)
               || (w15lpI >= 3 && i === 3);
    w15lpS.add('rect', {x: 34, y: 60 + i * 40, width: 340, height: 32, rx: 5,
                        fill: on ? HC.tok.accent : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: on ? 0.95 : 0.45}, g);
    const t = w15lpS.add('text', {x: 48, y: 81 + i * 40, cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = ln;
  });
  let total = 0;
  for (let k = 0; k <= Math.min(w15lpI, 2); k++) total += w15lpVals[k];
  const cur = w15lpI >= 0 && w15lpI < 3 ? w15lpVals[w15lpI] : null;
  w15lpS.txtPx(470, 76, '變數表', {cls: 'axtitle', anchor: 'middle'}, g);
  [['value', cur === null ? '—' : String(cur)], ['total', String(total)]].forEach((r, i) => {
    w15lpS.add('rect', {x: 396, y: 96 + i * 52, width: 150, height: 40, rx: 5,
                        fill: HC.tok.card, stroke: HC.tok.cardBorder, 'stroke-width': 1.3}, g);
    const t = w15lpS.add('text', {x: 471, y: 121 + i * 52, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO}, g);
    t.textContent = r[0] + ' = ' + r[1];
  });
  w15lpVals.forEach((v, i) => {
    const done = i <= w15lpI;
    w15lpS.add('rect', {x: 396 + i * 52, y: 210, width: 44, height: 34, rx: 4,
                        fill: done ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: done ? 0.95 : 0.5}, g);
    const t = w15lpS.add('text', {x: 418 + i * 52, y: 233, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: done ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = String(v);
  });
  w15lpS.txtPx(471, 268, '走過的元素', {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w15lpIter').textContent = Math.max(0, Math.min(w15lpI + 1, 3)) + ' / 3';
  document.getElementById('w15lpVal').textContent = cur === null ? '—' : String(cur);
  document.getElementById('w15lpTotal').textContent = String(total);
  setStatus('w15lpStatus', w15lpI >= 3
    ? '迴圈結束，印出 <b>Total is: 24</b>。'
    : (w15lpI < 0 ? '按「單步」跟著跑一次。'
                  : '第 ' + (w15lpI + 1) + ' 圈：total 加上 ' + cur + '，變成 ' + total + '。'));
}
function w15lpStep() { w15lpI = Math.min(3, w15lpI + 1); w15lpDraw(); }
function w15lpReset() {
  if (w15lpTimer) { clearTimeout(w15lpTimer); w15lpTimer = null; }
  w15lpI = -1; w15lpDraw();
}
function w15lpPlay() {
  w15lpReset();
  const tick = () => {
    if (w15lpI >= 3) { w15lpTimer = null; return; }
    w15lpStep();
    w15lpTimer = setTimeout(tick, 850);
  };
  w15lpTimer = setTimeout(tick, 400);
}
if (w15lpS) w15lpDraw();
"""

PAGEJS += r"""
/* ═══ w15fn 函式的資料進出 ═══ */
const w15fnS = HC.svg('w15fnSvg', {h: 340});
const w15fnSteps = [
  {w: '還沒呼叫', v: '—'},
  {w: '四個引數傳進去', v: 'terms, response, train, test'},
  {w: '用 train 學設計矩陣的規格', v: '＋ mm, X_train, y_train'},
  {w: '對 test 只做 transform', v: '＋ X_test, y_test'},
  {w: '配適並預測', v: '＋ results, test_pred'},
  {w: 'return 一個數字，函式結束', v: '全部消失，只有回傳值留下'}
];
let w15fnI = 0, w15fnTimer = null;
function w15fnDraw() {
  const g = w15fnS.clearLayer('main');
  const st = w15fnI;
  w15fnS.add('rect', {x: 168, y: 66, width: 288, height: 200, rx: 10,
                      fill: HC.tok.accent2, opacity: st >= 1 && st < 5 ? 0.18 : 0.08,
                      stroke: HC.tok.accent2, 'stroke-width': 2}, g);
  w15fnS.txtPx(312, 90, 'evalMSE(...)', {cls: 'axtitle', anchor: 'middle',
                                         fill: HC.tok.accent2}, g);
  ['terms', 'response', 'train', 'test'].forEach((nm, i) => {
    const on = st >= 1;
    w15fnS.add('rect', {x: 24, y: 74 + i * 46, width: 108, height: 34, rx: 5,
                        fill: on ? HC.tok.accent : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: on ? 0.9 : 0.45}, g);
    const t = w15fnS.add('text', {x: 78, y: 96 + i * 46, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = nm;
    if (on) {
      w15fnS.add('path', {d: 'M136 ' + (91 + i * 46) + ' H 162', stroke: HC.tok.accent,
                          'stroke-width': 2}, g);
    }
  });
  const inner = ['mm = MS(terms)', 'X_train / y_train', 'X_test / y_test',
                 'results = OLS(...).fit()', 'test_pred = predict'];
  inner.forEach((ln, i) => {
    const on = st >= 2 && (i < (st - 1) * 2);
    w15fnS.add('rect', {x: 188, y: 108 + i * 30, width: 248, height: 24, rx: 4,
                        fill: on ? HC.tok.card : 'none',
                        stroke: on ? HC.tok.cardBorder : 'none', 'stroke-width': 1.1}, g);
    const t = w15fnS.add('text', {x: 200, y: 125 + i * 30, cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: on ? HC.tok.ink : HC.tok.muted, opacity: on ? 1 : 0.3}, g);
    t.textContent = ln;
  });
  if (st >= 5) {
    w15fnS.add('path', {d: 'M460 166 H 520', stroke: HC.tok.accent2, 'stroke-width': 2.6}, g);
    w15fnS.add('path', {d: 'M528 166 l -10 -6 v 12 z', fill: HC.tok.accent2}, g);
    w15fnS.add('rect', {x: 464, y: 190, width: 132, height: 44, rx: 6,
                        fill: HC.tok.accent2}, g);
    const t = w15fnS.add('text', {x: 530, y: 218, 'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = '25.5739';
    w15fnS.txtPx(530, 258, 'return 的值', {cls: 'axlab', anchor: 'middle'}, g);
  }
  const s = w15fnSteps[st];
  document.getElementById('w15fnStep').textContent = st + ' / 5';
  document.getElementById('w15fnWhat').textContent = s.w;
  document.getElementById('w15fnVars').textContent = s.v;
  setStatus('w15fnStatus', st >= 5
    ? '<b>return 之後函式就結束了</b>，裡面的區域變數全部消失，只有回傳值留下來。'
    : s.w + '。');
}
function w15fnStep() { w15fnI = Math.min(5, w15fnI + 1); w15fnDraw(); }
function w15fnReset() {
  if (w15fnTimer) { clearTimeout(w15fnTimer); w15fnTimer = null; }
  w15fnI = 0; w15fnDraw();
}
function w15fnPlay() {
  w15fnReset();
  const tick = () => {
    if (w15fnI >= 5) { w15fnTimer = null; return; }
    w15fnStep();
    w15fnTimer = setTimeout(tick, 850);
  };
  w15fnTimer = setTimeout(tick, 400);
}
if (w15fnS) w15fnDraw();

/* ═══ w15sc 作用域 ═══ */
const w15scS = HC.svg('w15scSvg', {h: 320});
const w15scCases = [
  {c: '函式讀外面的變數', inv: 'B = 1000（讀得到）', out: 'B = 1000',
   note: '函式裡<b>看得到</b>外面的名字。方便，但也讓函式的行為依賴外面的狀態。'},
  {c: '函式裡指派同名變數', inv: 'B = 50（新的區域變數）', out: 'B = 1000（沒被動到）',
   note: '一旦在函式裡指派，那就是<b>新的區域變數</b>，外面的完全不受影響。'},
  {c: '可變預設值的陷阱', inv: 'acc = [1, 2]（累積中）', out: '下次呼叫還是那一個',
   note: '<code>def f(acc=[])</code> 的空串列只建立一次，<b>所有呼叫共用</b>。'}
];
let w15scI = 0;
function w15scDraw() {
  const g = w15scS.clearLayer('main');
  const c = w15scCases[w15scI];
  w15scS.add('rect', {x: 34, y: 60, width: 552, height: 212, rx: 10,
                      fill: HC.tok.muted, opacity: 0.1,
                      stroke: HC.tok.cardBorder, 'stroke-width': 1.6}, g);
  w15scS.txtPx(52, 84, '模組層級（外面）', {cls: 'axtitle'}, g);
  w15scS.add('rect', {x: 200, y: 108, width: 350, height: 140, rx: 8,
                      fill: HC.tok.accent2, opacity: 0.16,
                      stroke: HC.tok.accent2, 'stroke-width': 2}, g);
  w15scS.txtPx(218, 132, '函式裡面（區域）', {cls: 'axtitle', fill: HC.tok.accent2}, g);
  const chip = (x, y, label, col) => {
    w15scS.add('rect', {x: x, y: y, width: 190, height: 38, rx: 6, fill: col}, g);
    const t = w15scS.add('text', {x: x + 95, y: y + 25, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: HC.tok.paper}, g);
    t.textContent = label;
  };
  chip(52, 172, c.out, HC.tok.accent);
  chip(222, 168, c.inv, HC.tok.accent2);
  if (w15scI === 0) {
    w15scS.add('path', {d: 'M248 191 H 214', stroke: HC.tok.accent, 'stroke-width': 2.4}, g);
    w15scS.add('path', {d: 'M244 191 l 10 -6 v 12 z', fill: HC.tok.accent}, g);
    w15scS.txtPx(310, 232, '看得到 ↑', {cls: 'axlab', anchor: 'middle'}, g);
  } else if (w15scI === 1) {
    w15scS.txtPx(310, 232, '各自獨立，互不影響', {cls: 'axlab', anchor: 'middle'}, g);
  } else {
    w15scS.txtPx(310, 232, '預設值只建立一次，所有呼叫共用同一個',
                 {cls: 'axlab', anchor: 'middle', fill: HC.tok.resid}, g);
  }
  document.getElementById('w15scCase').textContent = c.c;
  document.getElementById('w15scIn').textContent = c.inv;
  document.getElementById('w15scOut').textContent = c.out;
  setStatus('w15scStatus', c.note);
}
function w15scSet(i) { w15scI = i; w15scDraw(); }
if (w15scS) w15scDraw();

/* ═══ w15er 從最後一行讀起 ═══ */
const w15erS = HC.svg('w15errSvg', {h: 320});
const w15erLines = [
  {t: 'Traceback (most recent call last):', lv: '標題', w: '下面是呼叫的路徑', d: '跳過'},
  {t: '  File "<ipython-input>", line 3, in <module>', lv: '你的程式碼',
   w: '錯誤發生在你寫的第 3 行', d: '記住這一行，等一下回去看'},
  {t: '    A[[1,3],[0,2,3]]', lv: '出事的那一行', w: '就是這一行的內容',
   d: '看它用到哪些變數'},
  {t: 'IndexError: shape mismatch: indexing arrays could not be',
   lv: '錯誤種類與說明', w: '兩個索引陣列的形狀對不上', d: '<b>先讀這一行</b>：印出兩邊的 shape'}
];
let w15erI = 3;
function w15erDraw() {
  const g = w15erS.clearLayer('main');
  w15erLines.forEach((ln, i) => {
    const on = i === w15erI;
    w15erS.add('rect', {x: 34, y: 76 + i * 50, width: 552, height: 40, rx: 5,
                        fill: on ? (i === 3 ? HC.tok.resid : HC.tok.accent) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: on ? 0.95 : 0.45}, g);
    const t = w15erS.add('text', {x: 48, y: 101 + i * 50, cls: 'vlab',
                                  'font-family': HC.MONO, fontsize: '.7rem',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = ln.t.length > 58 ? ln.t.slice(0, 58) + '…' : ln.t;
  });
  w15erS.add('path', {d: 'M20 286 V 96', stroke: HC.tok.accent2, 'stroke-width': 2.4}, g);
  w15erS.add('path', {d: 'M20 88 l -6 12 h 12 z', fill: HC.tok.accent2}, g);
  w15erS.txtPx(24, 300, '讀的方向', {cls: 'axlab'}, g);
  const c = w15erLines[w15erI];
  document.getElementById('w15erLevel').textContent = c.lv;
  document.getElementById('w15erWhat').textContent = c.w;
  document.getElementById('w15erDo').textContent = c.d.replace(/<[^>]+>/g, '');
  setStatus('w15erStatus', c.lv + '：' + c.w + '。');
}
function w15erStep() { w15erI = w15erI > 0 ? w15erI - 1 : 3; w15erDraw(); }
function w15erReset() { w15erI = 3; w15erDraw(); }
if (w15erS) w15erDraw();
"""

apply("p2_flow_functions", BODIES, PAGEJS)
