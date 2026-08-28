#!/usr/bin/env python3
"""p1_python_basics.html（先備 P1 · Python 基礎）完整自學充實。冪等。

內容依據：Ch02-statlearn-lab-zh.ipynb 的「實驗：Python 入門」（儲存格 12–23、
132–134、236–244）與 Ch01-lab-zh.ipynb 的字典段（19–26）。

這一頁假設讀者<b>完全沒寫過程式</b>，例子一律用統計脈絡，
不用「動物」「水果」那種跟課程無關的比喻。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, hook, info, info_card, lab_code, lab_output,  # noqa: E402
                 qa, quiz, rows_card, svg, table, ver_note, viz)

LAB2 = "Ch02-statlearn-lab-zh.ipynb"
LAB1 = "Ch01-lab-zh.ipynb"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB2 if ch == 2 else LAB1
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 第一行程式 ────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>這一頁假設你完全沒寫過程式。目標很具體：讀完之後，
  你能看懂課程 lab 裡那些一行一行的東西在做什麼——不是會寫，是<strong>看得懂</strong>。
  會寫是後面幾頁的事。</p>

{info("Python 只做三件事", "① <strong>算</strong>一個值；② 把值<strong>取個名字</strong>存起來；"
      "③ 把值<strong>丟給某個函式</strong>處理。"
      "課程 lab 裡每一行都是這三件事的組合，沒有第四種。")}

{viz(svg("w14readSvg", 320),
     [info_card("一行一行拆",
                "按「單步」把一段真的 lab 程式碼拆開，看每一行分別在做上面三件事的哪一件。"),
      rows_card("這一行",
                [("在做什麼", "—", "w14rdWhat"),
                 ("屬於哪一類", "—", "w14rdKind"),
                 ("結果是什麼", "—", "w14rdVal")]),
      info_card("看不懂就唸出來",
                "<code>x = [3, 4, 5]</code> 唸成「把一個裝了 3、4、5 的串列，"
                "取名叫 x」。程式碼是可以用中文唸的，唸得出來多半就懂了。")],
     "w14rdStatus", "按「單步」一行一行拆。",
     '<button class="btn btn-step" onclick="w14rdStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w14rdPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w14rdReset()">重置</button>')}

{card("印出一行字", C(2, 12), O(2, 12), src=S(2, 12),
      note="<code>print</code> 是一個函式，括號裡是要給它的東西，"
           "用逗號分開的話它會自動加空白。")}

{card("算術", C(2, 16), O(2, 16), src=S(2, 16),
      note="Jupyter 的儲存格會自動顯示<strong>最後一行的值</strong>，所以不寫 print 也看得到。")}

{card("字串相加是接起來", C(2, 18), O(2, 18), src=S(2, 18),
      note="加號對數字是相加、對字串是串接。這種「同一個符號、不同型別不同意思」的設計"
           "在 P3 的串列與陣列還會再遇到一次。")}

{quiz("qFirst", "PART 00 · 自我檢測",
      "<code>print('MSE =', 25.57)</code> 會印出什麼？",
      [(True, "<code>MSE = 25.57</code>",
        "對。逗號分開的東西會被依序印出來，中間自動補一個空白。"),
       (False, "<code>MSE =25.57</code>",
        "少了空白。<code>print</code> 用逗號分隔時預設會插入一個空白。"),
       (False, "<code>('MSE =', 25.57)</code>",
        "那是你把整個括號當成一個東西印出來的樣子。"
        "<code>print</code> 會把括號裡的每一項各自印出，不會印括號本身。")])}
"""

# ── P01 變數與型別 ─────────────────────────────────────────────────────
BODIES["var"] = f"""
  <p>變數不是盒子。<code>x = [3, 4, 5]</code> 這一行做的事是：先做出一個串列，
  然後把 <strong>x 這個名牌貼上去</strong>。同一個東西可以貼很多張名牌——
  這件事在 P3 講陣列的「檢視」時會變成一個真的會咬人的問題。</p>

{viz(svg("w14varSvg", 320),
     [info_card("名牌不是盒子",
                "按「再貼一張名牌」，兩個名字會指到<strong>同一個</strong>串列。"
                "接著按「改內容」，你會看到兩個名字看到的東西一起變了。"),
      rows_card("目前",
                [("x 看到的", "[3, 4, 5]", "w14vaX"),
                 ("y 看到的", "（還沒有 y）", "w14vaY"),
                 ("它們是同一個嗎", "—", "w14vaSame")]),
      info_card("數字與字串不會有這個問題",
                "整數與字串是<strong>不可變</strong>的，"
                "<code>a = 3; b = a; b = 4</code> 之後 a 還是 3。"
                "會被就地改掉的只有串列、字典這種可變的東西。")],
     "w14vaStatus", "先猜按下「改內容」之後 x 會變成什麼。",
     '<button class="btn btn-step" onclick="w14vaAlias()">再貼一張名牌 y = x</button>'
     '<button class="btn btn-step" onclick="w14vaMut()">改內容 y[0] = 99</button>'
     '<button class="btn btn-reset" onclick="w14vaReset()">重置</button>')}

{table(["型別", "長什麼樣", "在這門課裡是什麼"],
       [["<code>int</code>", "<code>392</code>", "樣本數 n、變數個數 p、折數 k"],
        ["<code>float</code>", "<code>25.5739</code>", "MSE、係數、p 值——幾乎所有統計量"],
        ["<code>str</code>", "<code>'lstat'</code>", "欄名、檔名、圖的標題"],
        ["<code>bool</code>", "<code>True</code> / <code>False</code>", "條件的結果，布林遮罩的元素"],
        ["<code>list</code>", "<code>[3, 4, 5]</code>", "一組欄名、一組要試的參數"],
        ["<code>dict</code>", "<code>{'R2': 0.54}</code>", "一組具名的結果"]])}

{info("整數除法會咬人",
      "<code>7 / 2</code> 給 <code>3.5</code>（浮點數），"
      "<code>7 // 2</code> 給 <code>3</code>（整數，直接砍掉小數）。"
      "算折數或索引時用得到後者，算統計量千萬不要用錯。", "warm")}

{quiz("qVar", "PART 01 · 自我檢測",
      "<code>a = [1, 2]</code>、<code>b = a</code>、<code>b.append(3)</code>。"
      "現在 <code>a</code> 是什麼？",
      [(False, "<code>[1, 2]</code>，因為 b 是複製的",
        "<code>b = a</code> 沒有複製任何東西，它只是<strong>多貼一張名牌</strong>。"
        "要複製得寫 <code>b = a.copy()</code>。"),
       (True, "<code>[1, 2, 3]</code>，因為兩個名字指的是同一個串列",
        "對。這是初學最常見的意外，而且在資料前處理時特別危險——"
        "你以為在改暫存變數，其實動到了原始資料。"),
       (False, "會報錯，a 已經被 b 取代了",
        "不會。一個東西可以有很多個名字，它們平起平坐，沒有誰取代誰。")])}
"""

# ── P02 串列 ────────────────────────────────────────────────────────────
BODIES["list"] = f"""
  <p>串列是<strong>有順序</strong>的一排東西，用中括號寫，從 <strong>0</strong> 開始數。
  課程 lab 裡最常見的用法是「一組欄名」與「一組要試的參數」。</p>

{card("做一個串列", C(2, 21), O(2, 21), src=S(2, 21))}

{card("串列相加是接起來，不是逐元素相加", C(2, 23), O(2, 23), src=S(2, 23),
      note="輸出有六個元素。要逐元素相加得用 NumPy 陣列——那是 P3 的第一節。")}

{viz(svg("w14idxSvg", 300),
     [info_card("為什麼從 0 開始",
                "把索引想成「離開頭有多遠」：第一個元素離開頭 0 步。"
                "這個想法在下一節的切片會變得很重要。"),
      rows_card("目前",
                [("索引", "0", "w14ixI"),
                 ("取到的值", "'mpg'", "w14ixV"),
                 ("負的索引", "-5", "w14ixN")]),
      info_card("負的索引從後面數",
                "<code>-1</code> 是最後一個、<code>-2</code> 是倒數第二個。"
                "要拿最後一欄寫 <code>cols[-1]</code>，"
                "不用先算長度再減一。")],
     "w14ixStatus", "按左右看每一個位置的索引。",
     '<button class="btn btn-step" onclick="w14ixMove(-1)">← 左</button>'
     '<button class="btn btn-step" onclick="w14ixMove(1)">右 →</button>'
     '<button class="btn btn-reset" onclick="w14ixReset()">重置</button>')}

{table(["你想做的事", "寫法"],
       [["拿第一個", "<code>cols[0]</code>"],
        ["拿最後一個", "<code>cols[-1]</code>"],
        ["有幾個", "<code>len(cols)</code>"],
        ["加一個到最後", "<code>cols.append('mpg')</code>"],
        ["接上另一個串列", "<code>cols + other</code> 或 <code>cols.extend(other)</code>"],
        ["在不在裡面", "<code>'mpg' in cols</code>"],
        ["複製一份", "<code>cols.copy()</code>"]])}

{quiz("qList", "PART 02 · 自我檢測",
      "<code>cols = ['mpg', 'weight', 'year']</code>，<code>cols[-1]</code> 是什麼？",
      [(True, "<code>'year'</code>",
        "對。負的索引從後面數，<code>-1</code> 就是最後一個。"
        "這比 <code>cols[len(cols)-1]</code> 好讀多了。"),
       (False, "會報錯，索引不能是負的",
        "Python 的負索引是合法的，而且很常用。"
        "（NumPy 陣列與 pandas 的 <code>iloc</code> 也支援。）"),
       (False, "<code>'mpg'</code>",
        "那是 <code>cols[0]</code>。負索引是從<strong>右邊</strong>數起。")])}
"""

# ── P03 切片 ────────────────────────────────────────────────────────────
BODIES["slice"] = f"""
  <p>切片是 <code>起:迄:步長</code>，而且<strong>迄不包含</strong>。
  這個「不包含」讓很多人第一次用就錯，但它有個好處：
  <code>a[:3]</code> 加 <code>a[3:]</code> 剛好就是整個 a，中間不會重疊也不會漏。</p>

{viz(svg("w14slSvg", 320),
     [info_card("拖端點",
                "按按鈕改起點、終點與步長，上面會標出被取到的字元。"
                "注意<strong>終點那一格永遠是灰的</strong>——它不包含在內。"),
      rows_card("目前",
                [("寫法", "s[3:6]", "w14slExpr"),
                 ("取到", "'lo '", "w14slVal"),
                 ("長度", "3", "w14slLen")]),
      info_card("同一套規則到處都是",
                "字串、串列、NumPy 陣列、pandas 的 <code>iloc</code> "
                "用的都是這一套。唯一的例外是 pandas 的 <code>loc</code>——"
                "它用名字，所以<strong>含尾</strong>（P4 會講）。")],
     "w14slStatus", "先猜 s[3:6] 會取到哪三個字。",
     '<button class="btn btn-step" onclick="w14slMove(0,-1)">起點 −</button>'
     '<button class="btn btn-step" onclick="w14slMove(0,1)">起點 +</button>'
     '<button class="btn btn-step" onclick="w14slMove(1,-1)">終點 −</button>'
     '<button class="btn btn-step" onclick="w14slMove(1,1)">終點 +</button>'
     '<button class="btn btn-toggle" onclick="w14slStepTog()">步長 1 ⇄ 2</button>'
     '<button class="btn btn-reset" onclick="w14slReset()">重置</button>')}

{card("字串也能切", C(2, 132), O(2, 132), src=S(2, 132),
      note="從第 3 個字元開始、取到第 6 個之前——三個字元，其中一個是空白。")}

{card("slice 物件是同一件事的另一種寫法", C(2, 134), O(2, 134), src=S(2, 134),
      note="<code>[3:6]</code> 只是 <code>[slice(3,6)]</code> 的語法糖。"
           "知道這件事之後，「為什麼可以把切片存成變數」就不奇怪了。")}

{quiz("qSlice", "PART 03 · 自我檢測",
      "<code>a = [0,1,2,3,4,5]</code>，<code>a[1:4]</code> 有幾個元素？",
      [(True, "3 個：1、2、3",
        "對。長度是 <code>迄 − 起</code> = 4 − 1 = 3。"
        "「迄不包含」讓算長度變得很簡單，這是它的好處。"),
       (False, "4 個：1、2、3、4",
        "把終點也算進去了。<code>a[1:4]</code> 取到索引 3 為止，不含 4。"),
       (False, "2 個：1、2",
        "少算了一個。起點<strong>是</strong>包含的，只有終點不包含。")])}
"""

# ── P04 字典 ────────────────────────────────────────────────────────────
BODIES["dict"] = f"""
  <p>串列用位置取值，字典用<strong>名字</strong>取值。統計程式裡幾乎所有「一組具名的結果」
  都是字典：模型的評分、欄名對應到型別、參數名稱對應到值。</p>

{card("用字典建一個 Series", C(1, 19), O(1, 19), src=S(1, 19),
      note="鍵變成索引、值變成資料——pandas 直接吃字典，因為兩者的結構本來就一樣。")}

{card("用字典建一整張表", C(1, 26), O(1, 26), src=S(1, 26),
      note="這次每一個值是一個<strong>串列</strong>，於是每一個鍵變成一欄。"
           "課程 lab 建示範資料幾乎都用這個寫法。")}

{viz(svg("w14dcSvg", 300),
     [info_card("兩種取值方式",
                "左邊是串列（用位置），右邊是字典（用名字）。"
                "按按鈕看同一個查詢在兩邊怎麼寫，以及為什麼字典比較不會出錯。"),
      rows_card("目前",
                [("要拿什麼", "—", "w14dcWant"),
                 ("串列寫法", "—", "w14dcList"),
                 ("字典寫法", "—", "w14dcDict")]),
      info_card("鍵不存在會怎樣",
                "<code>d['沒有這個鍵']</code> 會拋 <code>KeyError</code>。"
                "不確定在不在就用 <code>d.get('鍵', 預設值)</code>——"
                "找不到時回傳預設值而不是報錯。")],
     "w14dcStatus", "同一件事，兩種資料結構。",
     '<button class="btn btn-toggle" onclick="w14dcSet(0)">拿 R²</button>'
     '<button class="btn btn-toggle" onclick="w14dcSet(1)">拿 MSE</button>'
     '<button class="btn btn-toggle" onclick="w14dcSet(2)">多加一項</button>')}

{table(["你想做的事", "寫法"],
       [["取值", "<code>d['R2']</code>"],
        ["安全取值", "<code>d.get('R2', 0)</code>"],
        ["新增或覆寫", "<code>d['MSE'] = 38.5</code>"],
        ["鍵在不在", "<code>'R2' in d</code>"],
        ["所有鍵／所有值", "<code>d.keys()</code> / <code>d.values()</code>"],
        ["一次拿鍵和值", "<code>for k, v in d.items():</code>"]])}

{qa("觀念釐清", [
    ("字典的鍵可以是什麼？",
     "不可變的東西都可以：字串、數字、tuple。"
     "<strong>串列不行</strong>，因為它會變，變了之後就找不回原來的位置。"
     "實務上九成的鍵是字串。"),
    ("字典有順序嗎？",
     "Python 3.7 之後，字典會<strong>記住插入的順序</strong>，"
     "所以 <code>for k in d</code> 的順序是可預期的。"
     "但不要依賴它做排序——要排序就明確寫 <code>sorted(d)</code>。"),
])}

{quiz("qDict", "PART 04 · 自我檢測",
      "<code>scores = {{'R2': 0.54}}</code>，執行 <code>scores['MSE']</code> 會怎樣？",
      [(True, "拋 <code>KeyError</code>",
        "對。鍵不存在就報錯，不會給你 <code>None</code>。"
        "想要「找不到就給預設值」得寫 <code>scores.get('MSE', 0)</code>。"),
       (False, "回傳 <code>None</code>",
        "那是 <code>.get()</code> 的行為。直接用中括號取值找不到時會報錯——"
        "這是刻意的，免得你把打錯的欄名一路帶下去。"),
       (False, "自動建一個空的 MSE 項目",
        "讀取不會建立。<code>scores['MSE'] = 38.5</code> 這種<strong>賦值</strong>才會。")])}
"""

# ── P05 字串與格式化 ───────────────────────────────────────────────────
BODIES["str"] = f"""
  <p>最後一件事：把數字變成人看得懂的一行字。統計程式的輸出幾乎都要格式化——
  「MSE 是 25.573878189684412」沒有人想讀，你要的是「MSE 是 25.57」。</p>

{card("format 與格式規格", C(2, 244), O(2, 244), src=S(2, 244),
      note="<code>{{1:.2%}}</code> 的意思是「第 1 個引數，用百分比、小數兩位」。"
           "所以 0.1654 印出來是 16.54%。這一格同時示範了迴圈與格式化。")}

{card("迴圈裡的格式化", C(2, 236), O(2, 236), src=S(2, 236),
      note="<code>{{0}}</code> 是「第 0 個引數」。"
           "現在更常見的寫法是 f-string：<code>f'Total is: {{total}}'</code>，"
           "兩種都會遇到。")}

{viz(svg("w14fmtSvg", 300),
     [info_card("改格式規格看結果",
                "同一個數字 <code>25.573878</code>，換不同的格式規格。"
                "按按鈕看每一種的輸出。"),
      rows_card("目前",
                [("格式規格", "{:.2f}", "w14fmSpec"),
                 ("輸出", "25.57", "w14fmOut"),
                 ("什麼時候用", "報告統計量", "w14fmWhen")]),
      info_card("f-string 是現在的預設寫法",
                "<code>f'MSE = {{mse:.2f}}'</code> 把變數直接寫在字串裡，"
                "冒號後面接的格式規格跟 <code>format</code> 完全一樣。"
                "本站的程式碼卡兩種都會出現，因為課程 lab 兩種都用。")],
     "w14fmStatus", "同一個數字，五種格式。",
     '<button class="btn btn-toggle" onclick="w14fmSet(0)">{:.2f}</button>'
     '<button class="btn btn-toggle" onclick="w14fmSet(1)">{:.4f}</button>'
     '<button class="btn btn-toggle" onclick="w14fmSet(2)">{:.2%}</button>'
     '<button class="btn btn-toggle" onclick="w14fmSet(3)">{:.3e}</button>'
     '<button class="btn btn-toggle" onclick="w14fmSet(4)">{:>10.2f}</button>')}

{quiz("qStr", "PART 05 · 自我檢測",
      "<code>'{{:.2%}}'.format(0.1654)</code> 會印出什麼？",
      [(True, "<code>16.54%</code>",
        "對。百分比格式會<strong>先乘 100 再加百分號</strong>，"
        "所以不要自己再乘一次。lab 儲存格 244 算遺漏比例就是用這個。"),
       (False, "<code>0.17%</code>",
        "格式規格 <code>%</code> 會自己乘 100。"
        "如果你先乘了 100 再用 <code>:.2%</code>，就會多乘一次變成 1654%。"),
       (False, "<code>0.1654%</code>",
        "小數兩位是<strong>乘 100 之後</strong>才算的。")])}

{hook("這在本站哪一章會用到",
      '每一章的程式碼卡都在用這一頁的東西：串列裝欄名、字典裝評分、'
      '格式化把數字印成報告要的樣子。下一步是 '
      '<a href="p2_flow_functions.html">P2 流程與函式</a>，'
      '之後才是 <a href="p3_numpy.html">P3 NumPy</a>。')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 名牌與盒子",
      "<code>a = [1,2,3]</code>、<code>b = a[:]</code>、<code>b[0] = 99</code>。<code>a[0]</code> 是？",
      [(True, "<code>1</code>，因為 <code>a[:]</code> 是一份新的複本",
        "對。整段切片 <code>[:]</code> 會產生新的串列，"
        "跟 <code>b = a</code> 完全不同。這是最短的複製寫法。"),
       (False, "<code>99</code>，b 只是 a 的另一個名字",
        "那是 <code>b = a</code> 的情況。加了 <code>[:]</code> 就是切片，"
        "切片會產生新的串列。"),
       (False, "會報錯",
        "<code>a[:]</code> 是完全合法的寫法，取的是「從頭到尾」。")])}

{quiz("qEx2", "EXERCISE 2 · 索引",
      "<code>cols = ['mpg','cyl','hp','wt','year']</code>。"
      "想拿中間三個（cyl、hp、wt），怎麼寫？",
      [(False, "<code>cols[1:4:1]</code> 之外還要加 <code>cols[4]</code>",
        "不用。<code>cols[1:4]</code> 已經是 cyl、hp、wt 三個了，"
        "多加 <code>cols[4]</code> 會把 year 也拿進來。"),
       (True, "<code>cols[1:4]</code>",
        "對。起點 1（cyl）、終點 4 不包含（所以停在 wt）。"
        "「迄不包含」讓長度剛好是 4−1=3。"),
       (False, "<code>cols[1:3]</code>",
        "只拿到兩個（cyl、hp）。終點要寫 4 才會包含索引 3 的 wt。")])}

{quiz("qEx3", "EXERCISE 3 · 字典",
      "你想記錄三個模型的 MSE，之後要能用模型名字查。該用什麼？",
      [(False, "三個變數 <code>mse1</code>、<code>mse2</code>、<code>mse3</code>",
        "能動，但沒辦法用迴圈處理，也沒辦法「用名字查」——"
        "你得記得哪個數字對應哪個模型。"),
       (True, "一個字典 <code>{{'linear': 25.57, 'quad': 22.22, 'cubic': 22.67}}</code>",
        "對。名字直接當鍵，之後 <code>for name, mse in d.items()</code> "
        "就能一次處理完，印報告也方便。"),
       (False, "一個串列 <code>[25.57, 22.22, 22.67]</code>",
        "串列能存值但存不了名字，你得另外記「第 0 個是 linear」——"
        "那正是字典要解決的問題。")])}

{quiz("qEx4", "EXERCISE 4 · 格式化",
      "MSE 是 25.573878189684412，你想在報告裡印成兩位小數。哪一個寫法對？",
      [(True, "<code>f'MSE = {{mse:.2f}}'</code>",
        "對。冒號後面是格式規格，<code>.2f</code> 是「浮點數、小數兩位」。"
        "用 <code>'{{:.2f}}'.format(mse)</code> 也一樣。"),
       (False, "<code>f'MSE = {{round(mse)}}'</code>",
        "<code>round</code> 不給第二個引數的話會四捨五入到整數，變成 26。"
        "而且它改的是<strong>數值</strong>，格式化改的只是顯示——"
        "後者比較安全。"),
       (False, "<code>f'MSE = {{mse:2f}}'</code>",
        "少了那個點。<code>2f</code> 的 2 會被當成<strong>總寬度</strong>不是小數位數，"
        "結果會印出全部的小數。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張速查表。忘了就回來看。</p>

{table(["你想做的事", "串列", "字典"],
       [["取一個", "<code>a[0]</code>（位置）", "<code>d['R2']</code>（名字）"],
        ["安全地取", "先 <code>if len(a) &gt; 0</code>", "<code>d.get('R2', 0)</code>"],
        ["加一個", "<code>a.append(x)</code>", "<code>d['新鍵'] = x</code>"],
        ["有幾個", "<code>len(a)</code>", "<code>len(d)</code>"],
        ["走過每一個", "<code>for x in a:</code>", "<code>for k, v in d.items():</code>"],
        ["在不在", "<code>x in a</code>（比值）", "<code>k in d</code>（比<b>鍵</b>）"],
        ["複製", "<code>a.copy()</code> 或 <code>a[:]</code>", "<code>d.copy()</code>"]])}

{table(["切片", "意思"],
       [["<code>a[2:5]</code>", "索引 2、3、4（<b>不含 5</b>）"],
        ["<code>a[:3]</code>", "從頭到索引 2"],
        ["<code>a[3:]</code>", "從索引 3 到最後"],
        ["<code>a[:]</code>", "整個，而且是<b>新的一份</b>"],
        ["<code>a[::2]</code>", "每隔一個取一次"],
        ["<code>a[-1]</code>", "最後一個"],
        ["<code>a[::-1]</code>", "整個反過來"]])}

{table(["格式規格", "0.1654 印出來", "什麼時候用"],
       [["<code>{{:.2f}}</code>", "0.17", "一般統計量"],
        ["<code>{{:.4f}}</code>", "0.1654", "係數、p 值"],
        ["<code>{{:.2%}}</code>", "16.54%", "比例、遺漏率"],
        ["<code>{{:.3e}}</code>", "1.654e-01", "非常大或非常小的數"],
        ["<code>{{:>10.2f}}</code>", "　　　　　0.17", "對齊成一欄"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 變數是名牌，不是盒子。</strong>"
      "<code>b = a</code> 只是多貼一張名牌，改 b 會動到 a。<br>"
      "<strong>2. 索引從 0 開始，切片的迄不包含。</strong>"
      "所以 <code>a[:k]</code> 加 <code>a[k:]</code> 剛好是整個 a。<br>"
      "<strong>3. 串列用位置、字典用名字。</strong>"
      "有名字的東西就用字典，不要用「我記得第 2 個是 MSE」。")}

{ver_note((2, 1))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* 共用：畫一排格子 */
function w14cells(s, g, items, opt) {
  const cw = opt.cw || 74, x0 = opt.x0, y = opt.y;
  items.forEach((v, i) => {
    const on = opt.on ? opt.on(i) : false;
    s.add('rect', {x: x0 + i * cw, y: y, width: cw - 6, height: 38, rx: 5,
                   fill: on ? HC.tok.accent2 : HC.tok.card,
                   stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                   opacity: on ? 1 : 0.55}, g);
    const t = s.add('text', {x: x0 + i * cw + (cw - 6) / 2, y: y + 25,
                             'text-anchor': 'middle', cls: 'vlab',
                             'font-family': HC.MONO,
                             fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = String(v);
    if (opt.idx) {
      const n = s.add('text', {x: x0 + i * cw + (cw - 6) / 2, y: y - 8,
                               'text-anchor': 'middle', cls: 'axlab'}, g);
      n.textContent = String(i);
    }
  });
}

/* ═══ w14rd 一行一行拆 ═══ */
const w14rdS = HC.svg('w14readSvg', {h: 320});
const w14rdLines = [
  {code: "x = [3, 4, 5]", what: '做一個串列，取名叫 x', kind: '② 取名字', val: '[3, 4, 5]'},
  {code: "y = [4, 9, 7]", what: '再做一個串列，取名叫 y', kind: '② 取名字', val: '[4, 9, 7]'},
  {code: "x + y", what: '把兩個串列接起來', kind: '① 算一個值', val: '[3, 4, 5, 4, 9, 7]'},
  {code: "print('total', 24)", what: '把東西交給 print 顯示', kind: '③ 丟給函式', val: 'total 24'}
];
let w14rdI = -1, w14rdTimer = null;
function w14rdDraw() {
  const g = w14rdS.clearLayer('main');
  w14rdLines.forEach((ln, i) => {
    const on = i === w14rdI;
    w14rdS.add('rect', {x: 40, y: 58 + i * 54, width: 400, height: 42, rx: 6,
                        fill: on ? HC.tok.accent : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 0.95 : 0.5}, g);
    const t = w14rdS.add('text', {x: 58, y: 85 + i * 54, cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = ln.code;
    if (on) {
      const v = w14rdS.add('text', {x: 462, y: 85 + i * 54, cls: 'vlab',
                                    'font-family': HC.MONO, fill: HC.tok.accent2}, g);
      v.textContent = '→ ' + ln.val;
    }
  });
  const ln = w14rdLines[Math.max(0, w14rdI)];
  document.getElementById('w14rdWhat').textContent = w14rdI < 0 ? '—' : ln.what;
  document.getElementById('w14rdKind').textContent = w14rdI < 0 ? '—' : ln.kind;
  document.getElementById('w14rdVal').textContent = w14rdI < 0 ? '—' : ln.val;
  setStatus('w14rdStatus', w14rdI < 0 ? '按「單步」一行一行拆。'
            : '這一行在' + ln.what + '（' + ln.kind + '）。');
}
function w14rdStep() { w14rdI = Math.min(w14rdLines.length - 1, w14rdI + 1); w14rdDraw(); }
function w14rdReset() {
  if (w14rdTimer) { clearTimeout(w14rdTimer); w14rdTimer = null; }
  w14rdI = -1; w14rdDraw();
}
function w14rdPlay() {
  w14rdReset();
  const tick = () => {
    if (w14rdI >= w14rdLines.length - 1) { w14rdTimer = null; return; }
    w14rdStep();
    w14rdTimer = setTimeout(tick, 900);
  };
  w14rdTimer = setTimeout(tick, 400);
}
if (w14rdS) w14rdDraw();

/* ═══ w14va 名牌不是盒子 ═══ */
const w14vaS = HC.svg('w14varSvg', {h: 320});
let w14vaHasY = false, w14vaVals = [3, 4, 5];
function w14vaDraw() {
  const g = w14vaS.clearLayer('main');
  w14cells(w14vaS, g, w14vaVals, {x0: 220, y: 130, cw: 76});
  w14vaS.add('rect', {x: 206, y: 116, width: 3 * 76 + 8, height: 66, rx: 8,
                      fill: 'none', stroke: HC.tok.cardBorder, 'stroke-width': 1.6,
                      'stroke-dasharray': '5 4'}, g);
  w14vaS.txtPx(310, 200, '記憶體裡的那一個串列', {cls: 'axlab', anchor: 'middle'}, g);
  const tag = (label, y, col) => {
    w14vaS.add('rect', {x: 60, y: y, width: 78, height: 34, rx: 6, fill: col}, g);
    const t = w14vaS.add('text', {x: 99, y: y + 23, 'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = label;
    w14vaS.add('path', {d: 'M138 ' + (y + 17) + ' H 200', stroke: col,
                        'stroke-width': 2.4, fill: 'none'}, g);
    w14vaS.add('path', {d: 'M206 ' + (y + 17) + ' l -10 -6 v 12 z', fill: col}, g);
  };
  tag('x', 92, HC.tok.accent2);
  if (w14vaHasY) tag('y', 168, HC.tok.accent);
  document.getElementById('w14vaX').textContent = '[' + w14vaVals.join(', ') + ']';
  document.getElementById('w14vaY').textContent = w14vaHasY
    ? '[' + w14vaVals.join(', ') + ']' : '（還沒有 y）';
  document.getElementById('w14vaSame').textContent = w14vaHasY ? '是，同一個' : '—';
  setStatus('w14vaStatus', w14vaVals[0] === 99
    ? '改的是 y[0]，但 <b>x 也變了</b> —— 因為它們指的本來就是同一個串列。'
    : (w14vaHasY ? '兩張名牌貼在同一個串列上。接著按「改內容」。'
                 : '一個串列，一張名牌。按「再貼一張名牌」。'));
}
function w14vaAlias() { w14vaHasY = true; w14vaDraw(); }
function w14vaMut() {
  if (!w14vaHasY) { w14vaHasY = true; }
  w14vaVals = [99, 4, 5]; w14vaDraw();
}
function w14vaReset() { w14vaHasY = false; w14vaVals = [3, 4, 5]; w14vaDraw(); }
if (w14vaS) w14vaDraw();

/* ═══ w14ix 索引 ═══ */
const w14ixS = HC.svg('w14idxSvg', {h: 300});
const w14ixCols = ['mpg', 'cyl', 'hp', 'wt', 'year'];
let w14ixI = 0;
function w14ixDraw() {
  const g = w14ixS.clearLayer('main');
  w14cells(w14ixS, g, w14ixCols, {x0: 62, y: 110, cw: 100, idx: true,
                                  on: i => i === w14ixI});
  w14ixCols.forEach((v, i) => {
    const n = w14ixS.add('text', {x: 62 + i * 100 + 47, y: 176, 'text-anchor': 'middle',
                                  cls: 'axlab', fill: HC.tok.muted}, g);
    n.textContent = String(i - w14ixCols.length);
  });
  w14ixS.txtPx(310, 66, "cols = ['mpg', 'cyl', 'hp', 'wt', 'year']",
               {cls: 'axtitle', anchor: 'middle'}, g);
  w14ixS.txtPx(310, 210, '上面是正的索引，下面是負的索引',
               {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w14ixI').textContent = String(w14ixI);
  document.getElementById('w14ixV').textContent = "'" + w14ixCols[w14ixI] + "'";
  document.getElementById('w14ixN').textContent = String(w14ixI - w14ixCols.length);
  setStatus('w14ixStatus', 'cols[' + w14ixI + '] 與 cols['
            + (w14ixI - w14ixCols.length) + '] 都是 <b>' + w14ixCols[w14ixI] + '</b>。');
}
function w14ixMove(d) {
  w14ixI = Math.max(0, Math.min(w14ixCols.length - 1, w14ixI + d));
  w14ixDraw();
}
function w14ixReset() { w14ixI = 0; w14ixDraw(); }
if (w14ixS) w14ixDraw();
"""

PAGEJS += r"""
/* ═══ w14sl 切片尺規（本頁招牌）═══ */
const w14slS = HC.svg('w14slSvg', {h: 320});
const w14slStr = 'hello world';
let w14slA = 3, w14slB = 6, w14slStep2 = false;
function w14slDraw() {
  const g = w14slS.clearLayer('main');
  const chars = w14slStr.split('');
  const st = w14slStep2 ? 2 : 1;
  const taken = [];
  for (let i = w14slA; i < w14slB; i += st) taken.push(i);
  const cw = 48, x0 = 310 - chars.length * cw / 2;
  chars.forEach((ch, i) => {
    const on = taken.indexOf(i) >= 0;
    const isEnd = i === w14slB;
    w14slS.add('rect', {x: x0 + i * cw, y: 122, width: cw - 5, height: 44, rx: 5,
                        fill: on ? HC.tok.accent2 : (isEnd ? HC.tok.muted : HC.tok.card),
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 1 : (isEnd ? 0.75 : 0.5)}, g);
    const t = w14slS.add('text', {x: x0 + i * cw + (cw - 5) / 2, y: 152,
                                  'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = ch === ' ' ? '␣' : ch;
    const n = w14slS.add('text', {x: x0 + i * cw + (cw - 5) / 2, y: 112,
                                  'text-anchor': 'middle', cls: 'axlab'}, g);
    n.textContent = String(i);
  });
  const mark = (i, label, col) => {
    const x = x0 + i * cw;
    w14slS.add('path', {d: 'M' + x + ' 178 V 202', stroke: col, 'stroke-width': 2.6}, g);
    const t = w14slS.add('text', {x: x, y: 220, 'text-anchor': 'middle', cls: 'axtitle',
                                  fill: col}, g);
    t.textContent = label;
  };
  mark(w14slA, '起 ' + w14slA, HC.tok.accent2);
  mark(w14slB, '迄 ' + w14slB + '（不含）', HC.tok.resid);
  const expr = 's[' + w14slA + ':' + w14slB + (w14slStep2 ? ':2' : '') + ']';
  const val = taken.map(i => chars[i]).join('');
  w14slS.txtPx(310, 70, "s = 'hello world'", {cls: 'axtitle', anchor: 'middle'}, g);
  document.getElementById('w14slExpr').textContent = expr;
  document.getElementById('w14slVal').textContent = "'" + val + "'";
  document.getElementById('w14slLen').textContent = String(taken.length);
  setStatus('w14slStatus', expr + ' 取到 <b>' + taken.length
            + '</b> 個字元。灰色那一格是<b>迄</b>，永遠不會被取到。');
}
function w14slMove(which, d) {
  if (which === 0) w14slA = Math.max(0, Math.min(w14slB, w14slA + d));
  else w14slB = Math.max(w14slA, Math.min(w14slStr.length, w14slB + d));
  w14slDraw();
}
function w14slStepTog() { w14slStep2 = !w14slStep2; w14slDraw(); }
function w14slReset() { w14slA = 3; w14slB = 6; w14slStep2 = false; w14slDraw(); }
if (w14slS) w14slDraw();

/* ═══ w14dc 串列 vs 字典 ═══ */
const w14dcS = HC.svg('w14dcSvg', {h: 300});
const w14dcCases = [
  {want: 'R²', list: "scores[0]", dict: "scores['R2']", hit: 0},
  {want: 'MSE', list: "scores[2]", dict: "scores['MSE']", hit: 2},
  {want: '多加一項', list: "scores.append(0.31)", dict: "scores['MAE'] = 0.31", hit: -1}
];
let w14dcI = 0;
function w14dcDraw() {
  const g = w14dcS.clearLayer('main');
  const c = w14dcCases[w14dcI];
  const vals = ['0.544', '0.544', '38.48'];
  const keys = ['R2', 'Ex.Var', 'MSE'];
  w14dcS.txtPx(150, 62, '串列（用位置）', {cls: 'axtitle', anchor: 'middle'}, g);
  vals.forEach((v, i) => {
    const on = c.hit === i;
    w14dcS.add('rect', {x: 60, y: 84 + i * 52, width: 180, height: 42, rx: 5,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 1 : 0.5}, g);
    const t = w14dcS.add('text', {x: 150, y: 111 + i * 52, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = '[' + i + '] ' + v;
  });
  w14dcS.txtPx(450, 62, '字典（用名字）', {cls: 'axtitle', anchor: 'middle'}, g);
  keys.forEach((k, i) => {
    const on = c.hit === i;
    w14dcS.add('rect', {x: 340, y: 84 + i * 52, width: 220, height: 42, rx: 5,
                        fill: on ? HC.tok.accent : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 1 : 0.5}, g);
    const t = w14dcS.add('text', {x: 450, y: 111 + i * 52, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = "'" + k + "': " + vals[i];
  });
  document.getElementById('w14dcWant').textContent = c.want;
  document.getElementById('w14dcList').textContent = c.list;
  document.getElementById('w14dcDict').textContent = c.dict;
  setStatus('w14dcStatus', w14dcI === 2
    ? '加東西兩邊都容易，差別在<b>你之後怎麼找回來</b>。'
    : '要拿 ' + c.want + '：串列得記得它在第 ' + c.hit + ' 個，字典直接寫名字。');
}
function w14dcSet(i) { w14dcI = i; w14dcDraw(); }
if (w14dcS) w14dcDraw();

/* ═══ w14fm 格式規格 ═══ */
const w14fmS = HC.svg('w14fmtSvg', {h: 300});
const w14fmCases = [
  {spec: '{:.2f}', out: '25.57', when: '報告統計量'},
  {spec: '{:.4f}', out: '25.5739', when: '係數、p 值'},
  {spec: '{:.2%}', out: '2557.39%', when: '比例（先乘 100）'},
  {spec: '{:.3e}', out: '2.557e+01', when: '非常大或非常小的數'},
  {spec: '{:>10.2f}', out: '␣␣␣␣␣25.57', when: '對齊成一欄'}
];
let w14fmI = 0;
function w14fmDraw() {
  const g = w14fmS.clearLayer('main');
  const c = w14fmCases[w14fmI];
  w14fmS.txtPx(310, 76, '25.573878', {cls: 'axtitle', anchor: 'middle'}, g);
  w14fmS.add('path', {d: 'M310 92 V 128', stroke: HC.tok.accent, 'stroke-width': 2.4}, g);
  w14fmS.add('path', {d: 'M310 134 l -7 -11 h 14 z', fill: HC.tok.accent}, g);
  w14fmS.add('rect', {x: 190, y: 138, width: 240, height: 44, rx: 6,
                      fill: HC.tok.accent, opacity: 0.9}, g);
  const t = w14fmS.add('text', {x: 310, y: 166, 'text-anchor': 'middle', cls: 'vlab',
                                'font-family': HC.MONO, fill: HC.tok.paper}, g);
  t.textContent = c.spec;
  w14fmS.add('path', {d: 'M310 186 V 216', stroke: HC.tok.accent2, 'stroke-width': 2.4}, g);
  w14fmS.add('path', {d: 'M310 222 l -7 -11 h 14 z', fill: HC.tok.accent2}, g);
  w14fmS.add('rect', {x: 170, y: 226, width: 280, height: 46, rx: 6,
                      fill: HC.tok.accent2, opacity: 0.92}, g);
  const o = w14fmS.add('text', {x: 310, y: 256, 'text-anchor': 'middle', cls: 'vlab',
                                'font-family': HC.MONO, fill: HC.tok.paper}, g);
  o.textContent = c.out;
  document.getElementById('w14fmSpec').textContent = c.spec;
  document.getElementById('w14fmOut').textContent = c.out;
  document.getElementById('w14fmWhen').textContent = c.when;
  setStatus('w14fmStatus', c.spec + ' → <b>' + c.out + '</b>（' + c.when + '）。');
}
function w14fmSet(i) { w14fmI = i; w14fmDraw(); }
if (w14fmS) w14fmDraw();
"""

apply("p1_python_basics", BODIES, PAGEJS)
