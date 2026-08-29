#!/usr/bin/env python3
"""00c_ai_assisted.html（先備 P7 · AI 協作）完整自學充實。冪等。

跟 00A 的分工：00A 講「為什麼還要自己學」（失效模式當動機），
這一頁講「那到底該怎麼用」（提問、驗證、探索）。

概念架構參考《AI-Assisted Statistics for Data Scientists》第 11 章與各章末的
Exploration with AI，**只引用概念，例子全部用課程 lab 的資料自行重演**。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LABS = {1: "Ch01-lab-zh.ipynb", 3: "Ch03-linreg-lab-zh.ipynb", 5: "Ch05-resample-lab-zh.ipynb"}


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    return f'<code>{LABS[ch]}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 問法決定答案品質 ─────────────────────────────────────────
BODIES["prologue"] = f"""
{info("先說這一頁怎麼讀", "它排在課前準備的第三頁，<strong>所以你可以現在就讀</strong>——"
      "整頁的主張不需要任何 Python 基礎。<br>"
      "但下面會出現幾段真的程式碼與一張迴歸的 summary 表。"
      "<strong>看不懂的先跳過</strong>，抓住那一段在講的判斷原則就夠了；"
      "等你在正課裡真的跑過一次，或翻過附錄的 "
      "<a href=\"p3_numpy.html\">P3</a>–<a href=\"p6_modeling_api.html\">P6</a>，"
      "再回來一次會清楚很多。", "warm")}

  <p><a href="00a_why_code.html">00A</a> 講的是為什麼你還是得自己看得懂。
  這一頁講另一半：<strong>那到底該怎麼用它</strong>。
  結論先說——同一個問題，問法不同，答案的可用程度差非常多，
  而差別幾乎都在<strong>你給了多少脈絡</strong>。</p>

{info("一句話", "AI 看不到你的資料。你給它多少脈絡，它就只能用多少脈絡回答。"
      "「幫我分析這份資料」這種問法，得到的一定是通用答案。")}

{viz(svg("w20promptSvg", 340),
     [info_card("三種問法",
                "同一個目標，三種提問。按按鈕看每一種得到的東西"
                "以及它需要你花多少力氣去驗證。"),
      rows_card("這一種問法",
                [("你給了什麼", "—", "w20pmGave"),
                 ("會得到什麼", "—", "w20pmGet"),
                 ("驗證成本", "—", "w20pmCost")]),
      info_card("第三種為什麼值得",
                "多打三十秒的字，換來的是<strong>可以直接跑、而且你知道怎麼核對</strong>"
                "的東西。這筆交易永遠划算。")],
     "w20pmStatus", "三種問法，看它們的差別。",
     '<button class="btn btn-toggle" onclick="w20pmSet(0)">① 模糊</button>'
     '<button class="btn btn-toggle" onclick="w20pmSet(1)">② 有目標</button>'
     '<button class="btn btn-toggle" onclick="w20pmSet(2)">③ 有脈絡與驗證方式</button>')}

{table(["提問要素", "為什麼重要"],
       [["資料長什麼樣（欄名、型別、幾筆）", "它看不到你的資料"],
        ["你的目標是預測還是解釋", "決定該用哪一套 API、哪些指標"],
        ["已經做過什麼", "免得它從頭教你一遍"],
        ["要什麼形式的輸出", "「可執行的程式碼」跟「一段說明」差很多"],
        ["<b>你打算怎麼驗證</b>", "逼自己先想清楚驗收標準"]])}

{quiz("qPrompt", "PART 00 · 自我檢測",
      "下列哪一種提問最可能得到你能直接用的東西？",
      [(False, "「幫我分析 Auto 這份資料」",
        "它不知道你要預測什麼、有沒有做過前處理、也不知道你要什麼形式的輸出。"
        "得到的會是一份通用的探索流程。"),
       (True, "「Auto 有 392 列 9 欄，mpg 是反應變數，horsepower 已經處理過遺漏值。"
              "我要看非線性關係，請給可執行的 statsmodels 程式碼，並說明我該看哪個統計量來判斷」",
        "對。有資料形狀、有目標、有已做的前處理、有輸出形式，"
        "而且<strong>要求它告訴你怎麼判斷</strong>——最後這一項最值錢。"),
       (False, "「用最好的方法分析 Auto」",
        "「最好」沒有定義。不同目標下最好的方法完全不同，"
        "它只能猜一個常見的給你。")])}
"""

# ── P01 給脈絡 ────────────────────────────────────────────────────────
BODIES["context"] = f"""
  <p>給脈絡最有效率的做法有兩個：貼<strong>前五列</strong>，以及貼一份<strong>資料字典</strong>
  （每個欄位是什麼意思、單位是什麼、有沒有特殊值）。
  這兩樣加起來不到十行，但它們消除掉的誤會佔一大半。</p>

{card("前五列就是最好的脈絡", C(1, 26), O(1, 26), src=S(1, 26),
      note="欄名、型別、數值的量級一次到位。"
           "把 <code>df.head().to_csv()</code> 的輸出貼給 AI，比描述十句還準。")}

{card("再加一張摘要", C(1, 36), O(1, 36), src=S(1, 36),
      note="範圍、遺漏（看 count）、離散程度都在這裡。"
           "有了這張表，AI 就不會建議你對一個常數欄做迴歸。")}

{info("資料字典值得自己寫一份",
      "欄名 <code>origin</code> 是 1／2／3，它代表什麼？"
      "<code>year</code> 是 70 還是 1970？<code>?</code> 代表遺漏還是零？"
      "<strong>這些只有你知道</strong>——寫成幾行字放在 notebook 開頭，"
      "既是給 AI 的脈絡，也是給三個月後的自己的。")}

{viz(svg("w20ctxSvg", 320),
     [info_card("加一層看一次",
                "按「加脈絡」，看同樣的問題在得到更多脈絡之後，"
                "AI 能給出的東西怎麼變得具體。"),
      rows_card("目前",
                [("已給的脈絡", "只有問題", "w20ctHas"),
                 ("它還得用猜的", "—", "w20ctGuess"),
                 ("回答的具體程度", "—", "w20ctLevel")]),
      info_card("最後一層最重要",
                "加上「我打算怎麼驗證」之後，"
                "你會發現<strong>自己也被迫想清楚了驗收標準</strong>——"
                "這件事的價值往往比 AI 的回答還高。")],
     "w20ctStatus", "按「加脈絡」一層一層加上去。",
     '<button class="btn btn-step" onclick="w20ctStep()">→ 加脈絡</button>'
     '<button class="btn btn-reset" onclick="w20ctReset()">重置</button>')}

{quiz("qCtx", "PART 01 · 自我檢測",
      "你要問 AI 關於 Auto 資料的問題。最值得先貼給它的是什麼？",
      [(True, "<code>df.head()</code> 與 <code>df.dtypes</code> 的輸出",
        "對。欄名、型別、量級一次到位，而且只要兩行。"
        "特別是 dtypes。它能讓 AI 發現 horsepower 是字串這件事。"),
       (False, "整份資料的 CSV",
        "太長，而且多數模型會截斷；重點資訊（欄名、型別）反而被淹沒。"
        "抽樣幾列就夠了。"),
       (False, "你的分析目標就好，資料它會自己想像",
        "它會「想像」出一份合理但跟你手上不同的資料，"
        "然後給你在那份想像資料上正確的建議。")])}
"""

# ── P02 術語有兩種意思 ────────────────────────────────────────────────
BODIES["terms"] = f"""
  <p>統計與機器學習是兩個平行發展的傳統，很多詞在兩邊<strong>指的不是同一件事</strong>。
  AI 的訓練資料把兩邊混在一起，所以它常常在同一段話裡切換定義而不自知。
  你要做的是：<strong>看到這些詞就先確認它指的是哪一個</strong>。</p>

{viz(svg("w20termSvg", 340),
     [info_card("切換兩種意思",
                "按按鈕看同一個詞的兩種用法。"
                "如果 AI 的一段話在兩種意思之間滑動，那段結論就不能信。"),
      rows_card("這個詞",
                [("統計傳統裡是", "—", "w20tmA"),
                 ("機器學習傳統裡是", "—", "w20tmB"),
                 ("怎麼確認", "—", "w20tmFix")]),
      info_card("為什麼這會出事",
                "「這個變數是顯著的，所以它對預測很重要」——"
                "這句話把統計顯著性與預測重要性混為一談，"
                "而它<strong>讀起來完全通順</strong>。"
                "這種錯誤沒辦法靠語感抓，只能靠知道定義。")],
     "w20tmStatus", "五個常常被混用的詞。",
     '<button class="btn btn-toggle" onclick="w20tmSet(0)">顯著</button>'
     '<button class="btn btn-toggle" onclick="w20tmSet(1)">重要</button>'
     '<button class="btn btn-toggle" onclick="w20tmSet(2)">正規化</button>'
     '<button class="btn btn-toggle" onclick="w20tmSet(3)">驗證</button>'
     '<button class="btn btn-toggle" onclick="w20tmSet(4)">偏差</button>')}

{table(["詞", "統計傳統", "機器學習傳統", "怎麼分辨"],
       [["顯著（significant）", "p 值小於門檻", "口語的「重要」", "看有沒有講檢定與 p 值"],
        ["重要（important）", "效果量大", "特徵重要度分數", "看是在講係數還是模型內部指標"],
        ["正規化（normalization）", "轉成常態或標準分數", "縮放到 [0,1]", "看有沒有講平均與標準差"],
        ["驗證（validation）", "確認假設成立", "拿驗證集調參數", "看是在講假設還是資料切分"],
        ["偏差（bias）", "估計量的系統性偏離", "偏差—變異裡的偏差", "看有沒有跟變異成對出現"]])}

{quiz("qTerm", "PART 02 · 自我檢測",
      "AI 說：「lstat 是顯著的，所以它是最重要的預測變數。」問題在哪？",
      [(True, "把統計顯著性當成預測重要性，這是兩件事",
        "對。顯著講的是「係數不是 0」很有把握（跟樣本數有關），"
        "預測重要性講的是「拿掉它預測會變差多少」。"
        "一個變數可以非常顯著但對預測幾乎沒有貢獻。"),
       (False, "沒問題，顯著的變數就是重要的變數",
        "這正是最常見的誤解，也是這一節存在的理由。"),
       (False, "應該說「統計上顯著」比較嚴謹",
        "用詞精確一點有幫助，但問題不在措辭，"
        "在那個「<strong>所以</strong>」。那是一個站不住腳的推論。")])}
"""

# ── P03 讀 summary 的常見誤讀 ─────────────────────────────────────────
BODIES["summary"] = f"""
  <p>最實用的一節。<code>summarize(results)</code> 只有四個欄位，
  但它被講錯的方式也差不多是四種。下面拿課程 lab 真的跑出來的那張表，
  逐一對照「AI 常見的說法」與「實際上該怎麼講」。</p>

{card("課程 lab 的係數表", C(3, 26), O(3, 26), src=S(3, 26),
      note="lstat 的係數 −0.9500、標準誤 0.039、t 值 −24.528、p 值 0.0。"
           "下面每一種誤讀都是針對這張表。")}

{viz(svg("w20smSvg", 340),
     [info_card("四種誤讀",
                "按按鈕看每一種常見的錯誤說法，"
                "以及同一張表<strong>實際上</strong>支持什麼結論。"),
      rows_card("這一種",
                [("常見的說法", "—", "w20smBad"),
                 ("錯在哪", "—", "w20smWhy"),
                 ("該怎麼講", "—", "w20smGood")]),
      info_card("共同的形狀",
                "四種誤讀都是<strong>把某一欄的意思擴大解釋</strong>："
                "把「不是 0」講成「很大」、把「這份資料裡」講成「一般而言」、"
                "把「相關」講成「造成」。看到這種擴大就要停下來。")],
     "w20smStatus", "四種誤讀，各自錯在哪。",
     '<button class="btn btn-toggle" onclick="w20smSet(0)">「p 值 0.0，效果很大」</button>'
     '<button class="btn btn-toggle" onclick="w20smSet(1)">「lstat 造成 medv 下降」</button>'
     '<button class="btn btn-toggle" onclick="w20smSet(2)">「係數 −0.95，影響很小」</button>'
     '<button class="btn btn-toggle" onclick="w20smSet(3)">「不顯著＝沒有效果」</button>')}

{card("係數本身", C(3, 37), O(3, 37), src=S(3, 37),
      note="要談效果大小就看這個，而且<strong>一定要連同單位講</strong>："
           "lstat 每增加 1 個百分點，medv 平均下降 0.95 千美元。"
           "脫離單位的「0.95」沒有任何意義。")}

{qa("觀念釐清", [
    ("為什麼 p 值 0.0 不代表效果大？",
     "p 值同時受<strong>效果大小</strong>與<strong>樣本數</strong>影響。"
     "Boston 有 506 筆，樣本夠大時就算效果很小也會顯著。"
     "反過來說，樣本很小時就算效果很大也可能不顯著。"
     "所以「顯著」講的是證據強度，不是效果大小。"),
    ("那什麼時候可以講因果？",
     "觀察性資料上基本上不行。除非你有隨機分派（實驗），"
     "或用了專門處理因果的設計。迴歸係數講的是"
     "「<strong>在這個模型裡</strong>，其他變數固定時的關聯」，"
     "不是「改變 X 會讓 Y 變動多少」。這兩句話的差別是整個因果推論領域存在的理由。"),
])}

{quiz("qSum", "PART 03 · 自我檢測",
      "AI 說：「lstat 的 p 值是 0.000，這是模型裡最重要的變數。」你該怎麼回它？",
      [(True, "先問它比較的是什麼——p 值不能拿來排序變數的重要性",
        "對。p 值受樣本數影響，不同變數的 p 值不能直接比大小來排重要性。"
        "要排序得看標準化後的係數，或用「拿掉它預測會變差多少」來衡量。"),
       (False, "同意，p 值最小的就是最重要的",
        "這正是本節要拆的誤讀。"),
       (False, "要求它改用 t 值來排序",
        "t 值就是 p 值的另一種表達（t = coef / std err），同樣受樣本數影響，"
        "換一個欄位不解決問題。")])}
"""

# ── P04 驗證清單 ──────────────────────────────────────────────────────
BODIES["check"] = f"""
  <p>前面三節講的是怎麼問、怎麼讀。這一節是收尾動作：
  <strong>拿到一段 AI 產出的分析，逐項核對</strong>。
  清單只有六項，跑一次不用五分鐘。</p>

{viz(svg("w20chkSvg", 340),
     [info_card("逐項勾",
                "按「下一項」走過六個檢查點。"
                "每一項都對應一個你可以自己跑的動作，不是抽象的原則。"),
      rows_card("目前",
                [("進度", "0 / 6", "w20ckStep"),
                 ("這一項", "—", "w20ckItem"),
                 ("怎麼查", "—", "w20ckHow")]),
      info_card("沒過的話怎麼辦",
                "任何一項沒過，<strong>不是把那段丟掉，而是回去問清楚</strong>。"
                "「你這裡的標準化是在切分之前還是之後做的？」"
                "。這種追問通常會讓它自己修正。")],
     "w20ckStatus", "六個檢查點，按「下一項」逐一過。",
     '<button class="btn btn-step" onclick="w20ckStep()">→ 下一項</button>'
     '<button class="btn btn-play" onclick="w20ckPlay()">▶ 全部走一遍</button>'
     '<button class="btn btn-reset" onclick="w20ckReset()">重置</button>')}

{card("最容易被跳過的一項：評估用的是什麼資料", C(5, 34), O(5, 34), src=S(5, 34),
      note="24.2315 是<strong>留一交叉驗證</strong>的結果，不是訓練誤差。"
           "AI 給你一個誤差數字時，先確認它是在哪一份資料上算的。")}

{card("還要看它晃多少", C(5, 46), O(5, 46), src=S(5, 46),
      note="平均 23.80、標準差 1.42。"
           "只給平均不給標準差的比較，沒辦法判斷差異算不算差異。"
           "AI 很少主動給後者，<strong>你要自己要求</strong>。")}

{table(["檢查點", "怎麼查（一行）"],
       [["① 資料形狀對嗎", "<code>df.shape</code>、<code>df.dtypes</code>"],
        ["② 關鍵數字重算得出來嗎", "自己算一次那個統計量"],
        ["③ 圖跟數字一致嗎", "畫出來看，別只看摘要"],
        ["④ 評估用的是沒看過的資料嗎", "找 <code>train_test_split</code> 或 <code>cross_validate</code>"],
        ["⑤ 前處理在切分之後嗎", "找 <code>Pipeline</code>，或看 <code>fit</code> 的順序"],
        ["⑥ 隨機的地方固定種子了嗎", "找 <code>random_state</code> / <code>seed</code>"]])}

{quiz("qCheck", "PART 04 · 自我檢測",
      "AI 給的程式碼裡有 <code>StandardScaler().fit_transform(X)</code>，"
      "然後才 <code>train_test_split</code>。清單的哪一項沒過？",
      [(True, "第 ⑤ 項：前處理在切分之前做了",
        "對。這是資料洩漏，回報的測試分數會偏樂觀。"
        "回去要求它改用 <code>Pipeline</code>，讓 scaler 在每一折內部各自 fit。"),
       (False, "第 ④ 項：沒有用沒看過的資料評估",
        "它<strong>有</strong>切分，所以第 ④ 項是過的——問題出在切分與前處理的<strong>順序</strong>。"),
       (False, "都過了，這樣寫沒問題",
        "順序反了。這是 <a href=\"p6_modeling_api.html#cv\">P6</a> 花一整節在講的事。")])}
"""

# ── P05 拿它來探索 ────────────────────────────────────────────────────
BODIES["explore"] = f"""
  <p>最後講 AI 真正最有價值的用法：<strong>產生候選，不是給結論</strong>。
  「還有哪些變數可能相關」「這個模式有哪些可能的解釋」「我漏看了什麼」——
  這類問題它答得又快又廣，而且<strong>錯了也不要緊</strong>，因為你本來就要一個一個驗。</p>

{info("兩種用法的差別",
      "<strong>要結論</strong>：「這兩組有沒有顯著差異？」→ 它給一個你沒辦法驗的答案。<br>"
      "<strong>要候選</strong>：「有哪些因素可能造成這兩組的差異？請列五個，"
      "並說明各自要怎麼檢查。」→ 它給你五條可以動手查的線索。")}

{viz(chart("w20expChart", fallback="：AI 列出的五個候選解釋，逐一回到資料檢查之後，"
                                  "只有兩個站得住腳。這正是它該扮演的角色。"),
     [info_card("五個候選，逐一驗",
                "假設你問「為什麼歐洲車的 mpg 比較高」，AI 列了五個可能的解釋。"
                "按按鈕把每一個拿回資料檢查，看幾個站得住腳。"),
      rows_card("目前",
                [("已檢查", "0 / 5", "w20exDone"),
                 ("站得住腳", "—", "w20exOk"),
                 ("被推翻", "—", "w20exNo")]),
      info_card("兩個成立就很值了",
                "五個候選裡兩個成立，聽起來命中率不高，"
                "但這五個是你<strong>三十秒</strong>拿到的，"
                "而驗證每一個各花幾分鐘。這筆交易划算得不得了。")],
     "w20exStatus", "按「檢查下一個」逐一驗證五個候選解釋。",
     '<button class="btn btn-step" onclick="w20exStep()">→ 檢查下一個</button>'
     '<button class="btn btn-reset" onclick="w20exReset()">重置</button>')}

{table(["問法", "得到什麼", "風險"],
       [["「這個結果對嗎？」", "一個你沒辦法驗的判斷", "高：你只能選擇信或不信"],
        ["「幫我列五個可能的解釋，各自怎麼查」", "五條可以動手的線索", "低：本來就要一個個驗"],
        ["「這段程式碼在做什麼」", "逐行說明", "低：你可以跑一次核對"],
        ["「我漏看了什麼」", "檢查清單", "低：每一項都可以自己查"],
        ["「幫我寫報告的結論」", "一段很像樣的文字", "<b>最高</b>：錯的結論最像對的"]])}

{qa("最後兩個問題", [
    ("那我到底該花多少時間學程式？",
     "夠用就好，而這門課的「夠用」比你想的低："
     "看得懂 lab 的每一行、改得動參數、跑得出圖、算得出一個統計量。"
     "先備頁的六頁就是為這個標準寫的。"
     "剩下的時間應該花在<strong>統計本身</strong>。那才是 AI 幫不上忙的部分。"),
    ("AI 進步了之後，這一頁會不會過時？",
     "讀圖與算數字的部分會愈來愈準，這是好事。"
     "但「這個模型該不該上線」「這個差異在實務上重不重要」"
     "「這份資料能不能代表我要推論的族群」——"
     "這些問題的答案<strong>不在資料裡</strong>，它不可能替你回答。"
     "驗證清單的價值不會因為模型變強而消失。"),
])}

{quiz("qExp", "PART 05 · 自我檢測",
      "AI 最不該被拿來做哪一件事？",
      [(False, "列出可能的解釋讓你去查",
        "這正是它最划算的用法——產生候選的成本極低，而驗證是你的工作。"),
       (True, "直接寫報告的結論段落",
        "對。結論是整份分析裡<strong>最需要你自己負責</strong>的部分，"
        "而且錯的結論寫起來跟對的一樣通順，事後最難抓。"),
       (False, "解釋一段你看不懂的程式碼",
        "很划算。解釋完你可以自己跑一次核對，風險很低。")])}

{hook("先備入口層到這裡結束",
      '課前準備到這裡結束，接下來就是正課了。第 1 章會把整門課的地圖攤開，'
      '第 2 章開始每一章都有可以動手的 lab。'
      '正課讀到 Python 卡住的時候，附錄的 <a href="p3_numpy.html">P3</a>–'
      '<a href="p6_modeling_api.html">P6</a> 就是拿來翻的——不必先讀完再開始。'
      '<a href="introduction.html">→ 第 1 章 統計學習導論</a>')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 改寫提問",
      "「幫我看看這個模型好不好」。這個問題最缺的是什麼？",
      [(True, "「好」的定義：預測準？可解釋？還是穩定？",
        "對。三種目標會導向完全不同的評估方式與結論。"
        "先把「好」定義清楚，問題才有答案。"),
       (False, "模型的程式碼",
        "當然要給，但就算給了，它還是不知道你要的是哪一種「好」。"),
       (False, "資料的筆數",
        "有幫助，但不是最缺的。目標不明確的話，給再多資料細節也沒用。")])}

{quiz("qEx2", "EXERCISE 2 · 抓誤讀",
      "AI 說：「交叉驗證的 MSE 是 23.8，比另一個模型的 23.4 高，所以另一個模型比較好。」問題在哪？",
      [(True, "沒有給不確定性，0.4 的差可能只是切分的隨機性",
        "對。要求它一起回報標準差（或各折的結果）。"
        "課程 lab 的 <code>ShuffleSplit</code> 給的標準差是 1.42，"
        "遠大於這個 0.4 的差距。"),
       (False, "MSE 越小越好，所以結論沒錯",
        "方向沒錯，但「23.4 比 23.8 小」不等於「模型比較好」——"
        "差距要跟不確定性比才有意義。"),
       (False, "應該用 R² 而不是 MSE",
        "換指標不會讓不確定性消失。同樣的問題會用另一個數字重演一次。")])}

{quiz("qEx3", "EXERCISE 3 · 抓洩漏",
      "AI 建議：「先用全部資料算相關係數，挑出前十個變數，再做交叉驗證。」問題在哪？",
      [(True, "挑變數也是一種學習，用到了測試部分的資訊",
        "對。這叫變數選擇的洩漏，是很隱蔽的一種——"
        "程式碼裡看不到 <code>fit</code> 在測試集上，但挑選這個動作本身就用到了。"
        "正確做法是把變數選擇放進 Pipeline，跟著每一折一起做。"),
       (False, "沒問題，相關係數不是模型",
        "洩漏的判準不是「是不是模型」，是「有沒有用到測試部分的資訊」。"),
       (False, "十個變數太少了",
        "數量不是重點，<strong>挑選的時機</strong>才是。")])}

{quiz("qEx4", "EXERCISE 4 · 決定用不用",
      "四件事裡，哪一件最適合完全交給 AI？",
      [(False, "決定要不要把這個模型用在真實的貸款審核上",
        "這牽涉公平性、法規、族群差異與後果承擔，"
        "而且沒有標準答案。這是最不該外包的一類。"),
       (True, "把一段 R 的程式碼翻譯成 Python",
        "對。有標準答案、你可以跑一次核對兩邊結果是否一致——"
        "驗證成本極低，正是它最擅長的那一類。"),
       (False, "判斷這份樣本能不能代表全台灣的家戶",
        "這要知道資料怎麼收的、抽樣框是什麼，"
        "這些資訊不在資料裡，AI 沒辦法知道。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張表：提問的骨架、驗證清單、以及用途分級。</p>

{table(["提問的五個要素", "範例"],
       [["資料形狀", "「392 列 9 欄，mpg 是反應變數」"],
        ["已做過什麼", "「horsepower 的 ? 已經處理成 NaN 並 dropna」"],
        ["目標", "「我要預測，不是解釋」"],
        ["輸出形式", "「請給可執行的 statsmodels 程式碼」"],
        ["<b>驗證方式</b>", "「並說明我該看哪個統計量來判斷它有沒有用」"]])}

{table(["驗證清單", "一行怎麼查"],
       [["① 資料形狀對嗎", "<code>df.shape</code>、<code>df.dtypes</code>"],
        ["② 關鍵數字重算得出來嗎", "自己算一次"],
        ["③ 圖跟數字一致嗎", "畫出來看"],
        ["④ 評估用沒看過的資料嗎", "找 <code>cross_validate</code>"],
        ["⑤ 前處理在切分之後嗎", "找 <code>Pipeline</code>"],
        ["⑥ 隨機的地方固定種子了嗎", "找 <code>random_state</code>"]])}

{table(["用途", "划不划算", "為什麼"],
       [["翻譯程式碼、解釋程式碼", "✓✓ 最划算", "有標準答案，跑一次就能核對"],
        ["查語法、查參數、修環境錯誤", "✓✓", "同上"],
        ["列出可能的解釋讓你去查", "✓ 划算", "產生候選成本低，驗證是你的工作"],
        ["寫程式碼草稿", "△ 要看得懂再用", "能跑不等於做的是你要的事"],
        ["判斷結果顯不顯著、模型好不好", "✗", "它沒看過你的資料，也不知道假設成不成立"],
        ["寫報告的結論段落", "✗✗ 最不划算", "錯的結論寫起來跟對的一樣通順"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 給脈絡，尤其是「我打算怎麼驗證」。</strong>"
      "後者會逼你自己先想清楚驗收標準。<br>"
      "<strong>2. 術語在統計與機器學習裡常常不同義。</strong>"
      "「顯著」「重要」「正規化」「驗證」「偏差」看到就先確認指的是哪一個。<br>"
      "<strong>3. 拿它產生候選，不要拿它下結論。</strong>"
      "候選錯了不要緊，結論錯了最難抓。")}

{ver_note((1, 3, 5))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* 共用：一排卡片 */
function w20chips(s, g, items, opt) {
  items.forEach((it, i) => {
    const on = i === opt.cur;
    const y = opt.y + i * opt.dy;
    s.add('rect', {x: opt.x, y: y, width: opt.w, height: opt.h, rx: 7,
                   fill: on ? (it.col || HC.tok.accent2) : HC.tok.card,
                   stroke: HC.tok.cardBorder, 'stroke-width': 1.5,
                   opacity: on ? 0.95 : 0.45}, g);
    const t = s.add('text', {x: opt.x + 16, y: y + 26, cls: 'axtitle',
                             fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = it.t;
    if (it.u) {
      const u = s.add('text', {x: opt.x + 16, y: y + 46, cls: 'axlab',
                               fill: on ? HC.tok.paper : HC.tok.muted}, g);
      u.textContent = it.u;
    }
  });
}

/* ═══ w20pm 提問品質三檔 ═══ */
const w20pmS = HC.svg('w20promptSvg', {h: 340});
const w20pmCases = [
  {t: '「幫我分析這份資料」', u: '沒有目標、沒有資料形狀、沒有輸出形式',
   gave: '什麼都沒給', get: '一份通用的探索流程', cost: '高：每一句都要自己判斷適不適用',
   col: 'resid'},
  {t: '「幫我用 Auto 配一個預測 mpg 的迴歸」', u: '有目標，但沒有資料細節與驗證方式',
   gave: '目標', get: '一段能跑的程式碼，但可能用錯欄或漏掉前處理',
   cost: '中：要自己檢查它假設了什麼', col: 'accent'},
  {t: '「Auto 392 列 9 欄，mpg 是反應變數，horsepower 已處理遺漏。要看非線性關係，'
      + '請給可執行的 statsmodels 程式碼，並說明我該看哪個統計量判斷」',
   u: '資料形狀 ＋ 已做的前處理 ＋ 目標 ＋ 輸出形式 ＋ 驗證方式',
   gave: '五個要素都給了', get: '可以直接跑、而且你知道怎麼核對的東西',
   cost: '低：它自己講了驗收標準', col: 'accent2'}
];
let w20pmI = 0;
function w20pmDraw() {
  const g = w20pmS.clearLayer('main');
  w20pmCases.forEach((c, i) => {
    const on = i === w20pmI;
    const y = 64 + i * 86;
    w20pmS.add('rect', {x: 40, y: y, width: 540, height: 74, rx: 8,
                        fill: on ? HC.tok[c.col] : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.5,
                        opacity: on ? 0.92 : 0.4}, g);
    const txt = c.t.length > 44 ? c.t.slice(0, 44) + '…' : c.t;
    const t = w20pmS.add('text', {x: 58, y: y + 30, cls: 'axtitle',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = (i + 1) + '. ' + txt;
    const u = w20pmS.add('text', {x: 58, y: y + 54, cls: 'axlab',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = c.u.length > 52 ? c.u.slice(0, 52) + '…' : c.u;
  });
  const c = w20pmCases[w20pmI];
  document.getElementById('w20pmGave').textContent = c.gave;
  document.getElementById('w20pmGet').textContent = c.get;
  document.getElementById('w20pmCost').textContent = c.cost;
  setStatus('w20pmStatus', '第 ' + (w20pmI + 1) + ' 種：' + c.get + '。');
}
function w20pmSet(i) { w20pmI = i; w20pmDraw(); }
if (w20pmS) w20pmDraw();

/* ═══ w20ct 一層一層加脈絡 ═══ */
const w20ctS = HC.svg('w20ctxSvg', {h: 320});
const w20ctLayers = [
  {t: '只有問題', guess: '資料長什麼樣、你要預測還是解釋、已做過什麼', lv: '很通用'},
  {t: '＋ df.head()', guess: '你要預測還是解釋、已做過什麼', lv: '欄名對得上了'},
  {t: '＋ df.dtypes 與 describe()', guess: '你要預測還是解釋', lv: '知道有遺漏值了'},
  {t: '＋ 你的目標與已做的前處理', guess: '你打算怎麼驗證', lv: '可以直接跑'},
  {t: '＋ 你打算怎麼驗證', guess: '（沒有了）', lv: '連驗收標準都講清楚'}
];
let w20ctI = 0;
function w20ctDraw() {
  const g = w20ctS.clearLayer('main');
  w20ctLayers.forEach((L, i) => {
    const on = i <= w20ctI;
    const y = 62 + i * 46;
    w20ctS.add('rect', {x: 60, y: y, width: 500, height: 38, rx: 6,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.3,
                        opacity: on ? 0.9 - i * 0.06 : 0.35}, g);
    const t = w20ctS.add('text', {x: 78, y: y + 25, cls: 'axtitle',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = L.t;
  });
  const L = w20ctLayers[w20ctI];
  document.getElementById('w20ctHas').textContent = L.t;
  document.getElementById('w20ctGuess').textContent = L.guess;
  document.getElementById('w20ctLevel').textContent = L.lv;
  setStatus('w20ctStatus', w20ctI >= 4
    ? '最後一層最重要：<b>你被迫先想清楚驗收標準</b>。'
    : '它還得用猜的：' + L.guess + '。');
}
function w20ctStep() { w20ctI = Math.min(4, w20ctI + 1); w20ctDraw(); }
function w20ctReset() { w20ctI = 0; w20ctDraw(); }
if (w20ctS) w20ctDraw();

/* ═══ w20tm 術語雙義 ═══ */
const w20tmS = HC.svg('w20termSvg', {h: 340});
const w20tmCases = [
  {w: '顯著', a: 'p 值小於門檻，「係數不是 0」很有把握', b: '口語的「重要、明顯」',
   fix: '問它有沒有做檢定、p 值多少、門檻是什麼'},
  {w: '重要', a: '效果量大（係數大且有單位意義）', b: '特徵重要度分數（模型內部指標）',
   fix: '問它是在講係數還是 feature importance'},
  {w: '正規化', a: '轉成常態或標準分數（減平均除標準差）', b: '縮放到 [0, 1] 區間',
   fix: '問它用的是 StandardScaler 還是 MinMaxScaler'},
  {w: '驗證', a: '確認模型假設成立（殘差、常態、等變異）', b: '拿驗證集調參數',
   fix: '問它是在講假設檢查還是資料切分'},
  {w: '偏差', a: '估計量系統性偏離真值', b: '偏差—變異取捨裡的那個偏差',
   fix: '看有沒有跟「變異」成對出現'}
];
let w20tmI = 0;
function w20tmDraw() {
  const g = w20tmS.clearLayer('main');
  const c = w20tmCases[w20tmI];
  w20tmS.txtPx(310, 52, '「' + c.w + '」', {cls: 'axtitle', anchor: 'middle',
                                            fill: HC.tok.accent}, g);
  [['統計傳統', c.a, HC.tok.accent2, 74], ['機器學習傳統', c.b, HC.tok.accent, 194]]
    .forEach(e => {
      w20tmS.add('rect', {x: 50, y: e[3], width: 520, height: 100, rx: 9,
                          fill: e[2], opacity: 0.16, stroke: e[2], 'stroke-width': 2}, g);
      const t = w20tmS.add('text', {x: 70, y: e[3] + 32, cls: 'axtitle', fill: e[2]}, g);
      t.textContent = e[0];
      const parts = e[1].match(/.{1,30}/g) || [e[1]];
      parts.slice(0, 2).forEach((ln, i) => {
        const u = w20tmS.add('text', {x: 70, y: e[3] + 60 + i * 22, cls: 'vlab'}, g);
        u.textContent = ln;
      });
    });
  document.getElementById('w20tmA').textContent = c.a;
  document.getElementById('w20tmB').textContent = c.b;
  document.getElementById('w20tmFix').textContent = c.fix;
  setStatus('w20tmStatus', '「' + c.w + '」有兩種意思。確認方式：' + c.fix + '。');
}
function w20tmSet(i) { w20tmI = i; w20tmDraw(); }
if (w20tmS) w20tmDraw();
"""

PAGEJS += r"""
/* ═══ w20sm summary 的四種誤讀 ═══ */
const w20smS = HC.svg('w20smSvg', {h: 340});
const w20smCases = [
  {bad: '「p 值 0.0，所以效果很大」',
   why: 'p 值受樣本數影響，跟效果大小無關',
   good: '「係數 −0.95：lstat 每多 1 個百分點，medv 平均少 0.95 千美元」', col: 'coef'},
  {bad: '「lstat 造成 medv 下降」',
   why: '觀察性資料上迴歸係數是關聯，不是因果',
   good: '「在這個模型裡，其他變數固定時，lstat 與 medv 呈負向關聯」', col: 'coef'},
  {bad: '「係數只有 −0.95，影響很小」',
   why: '脫離單位談大小沒有意義',
   good: '「lstat 從 5 變到 15，預測的 medv 差 9.5 千美元 —— 這在這個尺度上不小」',
   col: 'coef'},
  {bad: '「這個變數不顯著，所以沒有效果」',
   why: '不顯著只代表證據不足，不代表效果是 0',
   good: '「證據不足以排除 0；信賴區間是 −0.4 到 0.1，範圍還很寬」', col: 'p'}
];
let w20smI = 0;
function w20smDraw() {
  const g = w20smS.clearLayer('main');
  const c = w20smCases[w20smI];
  const cols = ['coef', 'std err', 't', 'P>|t|'];
  const vals = ['-0.9500', '0.039', '-24.528', '0.0'];
  const hi = c.col === 'coef' ? 0 : 3;
  cols.forEach((nm, j) => {
    const on = j === hi;
    w20smS.add('rect', {x: 118 + j * 104, y: 62, width: 96, height: 30, rx: 4,
                        fill: on ? HC.tok.accent : HC.tok.muted, opacity: on ? 1 : 0.5}, g);
    const t = w20smS.add('text', {x: 166 + j * 104, y: 82, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = nm;
    w20smS.add('rect', {x: 118 + j * 104, y: 98, width: 96, height: 30, rx: 4,
                        fill: on ? HC.tok.accent2 : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                        opacity: on ? 0.95 : 0.5}, g);
    const u = w20smS.add('text', {x: 166 + j * 104, y: 118, 'text-anchor': 'middle',
                                  cls: 'vlab', 'font-family': HC.MONO,
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = vals[j];
  });
  w20smS.txtPx(78, 118, 'lstat', {cls: 'vlab', anchor: 'end'}, g);
  const block = (y, label, text, col) => {
    w20smS.add('rect', {x: 50, y: y, width: 520, height: 62, rx: 8,
                        fill: col, opacity: 0.15, stroke: col, 'stroke-width': 1.8}, g);
    const t = w20smS.add('text', {x: 68, y: y + 24, cls: 'axtitle', fill: col}, g);
    t.textContent = label;
    const parts = text.match(/.{1,34}/g) || [text];
    parts.slice(0, 1).forEach((ln, i) => {
      const u = w20smS.add('text', {x: 68, y: y + 46 + i * 20, cls: 'vlab'}, g);
      u.textContent = ln + (parts.length > 1 ? '…' : '');
    });
  };
  block(154, '常見的說法 ✗', c.bad, HC.tok.resid);
  block(232, '該怎麼講 ✓', c.good, HC.tok.accent2);
  document.getElementById('w20smBad').textContent = c.bad;
  document.getElementById('w20smWhy').textContent = c.why;
  document.getElementById('w20smGood').textContent = c.good;
  setStatus('w20smStatus', '錯在哪：' + c.why + '。');
}
function w20smSet(i) { w20smI = i; w20smDraw(); }
if (w20smS) w20smDraw();

/* ═══ w20ck 驗證清單 ═══ */
const w20ckS = HC.svg('w20chkSvg', {h: 340});
const w20ckItems = [
  {t: '① 資料形狀對嗎', h: 'df.shape、df.dtypes'},
  {t: '② 關鍵數字重算得出來嗎', h: '自己算一次那個統計量'},
  {t: '③ 圖跟數字一致嗎', h: '畫出來看，別只看摘要'},
  {t: '④ 評估用的是沒看過的資料嗎', h: '找 train_test_split 或 cross_validate'},
  {t: '⑤ 前處理在切分之後嗎', h: '找 Pipeline，或看 fit 的順序'},
  {t: '⑥ 隨機的地方固定種子了嗎', h: '找 random_state / seed'}
];
let w20ckI = 0, w20ckTimer = null;
function w20ckDraw() {
  const g = w20ckS.clearLayer('main');
  w20ckItems.forEach((it, i) => {
    const done = i < w20ckI;
    const cur = i === w20ckI - 1;
    const y = 56 + i * 46;
    w20ckS.add('rect', {x: 46, y: y, width: 528, height: 38, rx: 6,
                        fill: done ? (cur ? HC.tok.accent : HC.tok.accent2) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.3,
                        opacity: done ? 0.92 : 0.4}, g);
    const box = w20ckS.add('text', {x: 66, y: y + 25, cls: 'vlab', 'font-family': HC.MONO,
                                    fill: done ? HC.tok.paper : HC.tok.muted}, g);
    box.textContent = done ? '✓' : '☐';
    const t = w20ckS.add('text', {x: 92, y: y + 25, cls: 'axtitle',
                                  fill: done ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = it.t;
    const u = w20ckS.add('text', {x: 560, y: y + 25, 'text-anchor': 'end', cls: 'axlab',
                                  fill: done ? HC.tok.paper : HC.tok.muted}, g);
    u.textContent = it.h;
  });
  const it = w20ckItems[Math.max(0, w20ckI - 1)];
  document.getElementById('w20ckStep').textContent = w20ckI + ' / 6';
  document.getElementById('w20ckItem').textContent = w20ckI === 0 ? '—' : it.t;
  document.getElementById('w20ckHow').textContent = w20ckI === 0 ? '—' : it.h;
  setStatus('w20ckStatus', w20ckI >= 6
    ? '六項全過。這段分析<b>現在才可以拿去下結論</b>。'
    : (w20ckI === 0 ? '按「下一項」逐一過。' : it.t + '：' + it.h + '。'));
}
function w20ckStep() { w20ckI = Math.min(6, w20ckI + 1); w20ckDraw(); }
function w20ckReset() {
  if (w20ckTimer) { clearTimeout(w20ckTimer); w20ckTimer = null; }
  w20ckI = 0; w20ckDraw();
}
function w20ckPlay() {
  w20ckReset();
  const tick = () => {
    if (w20ckI >= 6) { w20ckTimer = null; return; }
    w20ckStep();
    w20ckTimer = setTimeout(tick, 750);
  };
  w20ckTimer = setTimeout(tick, 400);
}
if (w20ckS) w20ckDraw();

/* ═══ w20ex 五個候選解釋（Chart.js）═══ */
const w20exCands = [
  {t: '歐洲車排氣量比較小', ok: true, v: 1},
  {t: '歐洲車比較新（年份偏晚）', ok: false, v: 0},
  {t: '歐洲車比較輕', ok: true, v: 1},
  {t: '歐洲車樣本數太少，是巧合', ok: false, v: 0},
  {t: '歐洲的油價比較高所以車廠有動機', ok: false, v: 0}
];
let w20exI = 0;
function w20exDraw() {
  const done = w20exCands.slice(0, w20exI);
  const ok = done.filter(c => c.ok).length;
  document.getElementById('w20exDone').textContent = w20exI + ' / 5';
  document.getElementById('w20exOk').textContent = w20exI === 0 ? '—' : ok + ' 個';
  document.getElementById('w20exNo').textContent =
    w20exI === 0 ? '—' : (w20exI - ok) + ' 個';
  const last = w20exI > 0 ? w20exCands[w20exI - 1] : null;
  setStatus('w20exStatus', w20exI === 0
    ? '按「檢查下一個」，把每一個候選拿回資料驗證。'
    : (w20exI >= 5
       ? '五個候選裡 <b>' + ok + ' 個</b>站得住腳。這五個是三十秒拿到的 —— 划算。'
       : '「' + last.t + '」' + (last.ok ? '<b>站得住腳</b>（資料支持）'
                                        : '<b>被推翻</b>（資料不支持，或根本沒辦法用這份資料查）')));
  if (!HC.hasChart()) return;
  const data = w20exCands.map((c, i) => (i < w20exI ? (c.ok ? 1 : -1) : 0));
  const colors = w20exCands.map((c, i) =>
    (i < w20exI ? (c.ok ? HC.tok.accent2 : HC.tok.resid) : HC.tok.muted));
  const ch = HC.get('w20expChart');
  if (ch) {
    ch.data.datasets[0].data = data;
    ch.data.datasets[0].backgroundColor = colors;
    ch.update();
    return;
  }
  HC.bar('w20expChart', {
    labels: w20exCands.map((c, i) => '候選 ' + (i + 1)),
    datasets: [{label: '驗證結果', data: data, backgroundColor: colors, borderWidth: 0}]
  }, {
    scales: {x: {title: {display: true, text: 'AI 列出的五個候選解釋'}},
             y: {title: {display: true, text: '↑ 站得住腳　↓ 被推翻'}, min: -1.4, max: 1.4,
                 ticks: {stepSize: 1}}},
    plugins: {legend: {display: false}}
  });
}
function w20exStep() { w20exI = Math.min(5, w20exI + 1); w20exDraw(); }
function w20exReset() { w20exI = 0; w20exDraw(); }
HC.ready(() => { w20exDraw(); });
"""

apply("00c_ai_assisted", BODIES, PAGEJS)
