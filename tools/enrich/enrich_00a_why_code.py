#!/usr/bin/env python3
"""00a_why_code.html（課前準備 A · 為什麼還要自己寫統計程式）完整自學充實。冪等。

論證骨幹取自《AI-Assisted Statistics for Data Scientists》(O'Reilly 2026) 第 11 章的
兩個概念：automation bias（自動化偏誤）與 cross-modal inconsistency（跨模態不一致）。
**只引用概念與章節，不搬該書的文字、圖與數字**——頁面上的例子全部用課程 lab 的
ISLP 資料自行重演（見 STYLE_CONTRACT §9.1）。

這一頁最後寫，因為它的掛鉤要連到其他八頁真實存在的錨點。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, hook, info, info_card, lab_code, lab_output,  # noqa: E402
                 qa, quiz, rows_card, svg, table, ver_note, viz)

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

# ── PROLOGUE 你已經有 AI 了 ───────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>先把話講開：現在的 AI 確實寫得出這門課大部分的程式碼。你貼一句
  「幫我用 Auto 資料配一個 mpg 對 horsepower 的迴歸並畫殘差圖」，
  它三秒就給你一段能跑的東西。這是真的，不用假裝不是。</p>

  <p>所以問題不是「AI 會不會」，而是<strong>「它給你的那個答案，你憑什麼判斷對不對」</strong>。
  這一頁講的就是這件事，而且不是精神喊話，是幾個具體、可以驗證的失效模式。</p>

{info("這一頁的立場", "<strong>該用就用。</strong>環境問題、語法問題、「這個函式的參數是什麼」，"
      "問 AI 又快又準。真正需要你自己判斷的是另一類問題："
      "<strong>這個數字能不能拿去下結論。</strong>")}

{viz(svg("w12anchorSvg", 340),
     [info_card("先自己估一次",
                "拖滑桿估「1980 年後出廠的車，平均 mpg 大概多少」。"
                "估完按「看 AI 的答案」，然後<strong>再估一次</strong>。"
                "最後才揭曉真實值。"),
      rows_card("你的兩次估計",
                [("第一次", "—", "w12anFirst"),
                 ("看過 AI 之後", "—", "w12anSecond"),
                 ("被拉動了多少", "—", "w12anShift")]),
      info_card("這在測什麼",
                "測的是<strong>錨定</strong>：一個看起來很有自信的數字會把你的判斷拉過去，"
                "即使你本來估得比較準。這不是意志力問題，是人類判斷的固定特性——"
                "所以要靠<strong>流程</strong>去對抗，不是靠「我會小心」。")],
     "w12anStatus", "先拖滑桿估一個數字，再按「看 AI 的答案」。",
     '<button class="btn btn-step" onclick="w12anGuess(-1)">估低一點</button>'
     '<button class="btn btn-step" onclick="w12anGuess(1)">估高一點</button>'
     '<button class="btn btn-play" onclick="w12anReveal()">▶ 看 AI 的答案</button>'
     '<button class="btn btn-toggle" onclick="w12anTruth()">揭曉真實值</button>'
     '<button class="btn btn-reset" onclick="w12anReset()">重置</button>')}

{quiz("qWhy", "PART 00 · 自我檢測",
      "下面哪一種問題，交給 AI 最划算？",
      [(True, "「pandas 的 read_csv 要怎麼把 ? 當成遺漏值？」",
        "對。這類問題有標準答案、而且你可以<strong>馬上驗證</strong>（跑一次看 dtypes）。"
        "AI 在這裡幾乎沒有風險。"),
       (False, "「這兩組的差異顯著嗎？」",
        "這需要知道資料怎麼收的、假設成不成立、多重比較有沒有處理——"
        "而 AI 看不到這些。它會給你一個很有自信的答案，但那個自信不是來自你的資料。"),
       (False, "「我的模型 R² 是 0.95，可以發表了嗎？」",
        "R² 0.95 可能是過度配適、可能是資料洩漏、也可能只是這個領域本來就好預測。"
        "沒有看過你的流程的人（或 AI）沒辦法回答這個問題。")])}
"""

# ── P01 自動化偏誤 ────────────────────────────────────────────────────
BODIES["bias"] = f"""
  <p>第一個失效模式叫<strong>自動化偏誤</strong>（automation bias）：
  對機器產出的答案給予比對人類答案更高的信任。
  它最狡猾的地方在於——<strong>答案排版得越整齊、語氣越肯定，你越不會去查</strong>。</p>

{info("為什麼特別危險",
      "同樣一句「這兩組差異顯著」，同學講你會追問「你用什麼檢定」，"
      "AI 講你會直接複製到報告裡。"
      "但 AI 沒有比同學更了解你的資料。它甚至沒看過你的資料。", "warm")}

{viz(svg("w12biasSvg", 320),
     [info_card("同一句話，兩個來源",
                "按按鈕切換這句話是誰說的，看你心裡的「要不要查證」有沒有不一樣。"
                "誠實一點，多數人是有的。"),
      rows_card("這個主張",
                [("誰說的", "—", "w12biWho"),
                 ("你會去查嗎", "—", "w12biCheck"),
                 ("實際上該做什麼", "回到資料驗證", "w12biDo")]),
      info_card("流程比意志力可靠",
                "對抗自動化偏誤的方法不是「我會保持懷疑」，"
                "而是<strong>把驗證變成固定動作</strong>："
                "任何一個數字進到報告之前，先問「我能不能自己重算一次」。")],
     "w12biStatus", "同一句話，三個來源。",
     '<button class="btn btn-toggle" onclick="w12biSet(0)">同學說的</button>'
     '<button class="btn btn-toggle" onclick="w12biSet(1)">AI 說的</button>'
     '<button class="btn btn-toggle" onclick="w12biSet(2)">你自己算的</button>')}

{card("最便宜的驗證動作", C(1, 36), O(1, 36), src=S(1, 36),
      note="<code>describe()</code> 一行就能戳破一半的錯誤主張："
           "範圍不合理、count 比列數少（有遺漏值）、標準差是 0（整欄同一個值）。"
           "<strong>問任何進階問題之前，先看過這張表。</strong>")}

{quiz("qBias", "PART 01 · 自我檢測",
      "AI 給你一段分析，結論寫得很肯定、格式也很整齊。你該做的第一件事是？",
      [(False, "看它的說法有沒有邏輯漏洞",
        "會有幫助，但這是在<strong>文字層面</strong>檢查。"
        "說得通的錯誤結論很多，光讀文字抓不出來。"),
       (True, "回到資料，自己把關鍵那個數字算一次",
        "對。這是唯一能真正確認的方式，而且通常只要一兩行程式碼——"
        "這也正是你需要看得懂那一兩行的理由。"),
       (False, "問另一個 AI 看看說法一不一致",
        "兩個模型可能犯同一類錯（訓練資料重疊、同樣的統計誤解）。"
        "一致不等於正確。")])}
"""

# ── P02 AI 讀圖會讀錯 ─────────────────────────────────────────────────
BODIES["crossmodal"] = f"""
  <p>第二個失效模式更具體：<strong>跨模態不一致</strong>（cross-modal inconsistency）——
  同一份資料用表、圖、文字三種形式呈現時，AI 對它們的解讀可能互相矛盾。
  最常見的是<strong>讀圖</strong>：它會很肯定地說出一個從圖上根本讀不出來的區間。</p>

{info("這不是罕見的失誤",
      "參考書第 11 章舉的例子裡，AI 描述一張密度圖時把最密集的區間講錯了一整格。"
      "文字讀起來完全合理，只是跟圖不符——<strong>而且沒有任何警訊</strong>。"
      "下面我們用課程的 Auto 資料重演同一件事。", "warm")}

{viz(svg("w12readSvg", 340),
     [info_card("你來當裁判",
                "下面是 Auto 資料的 horsepower 分布（頁面當場算的）。"
                "旁邊那段「AI 的描述」是我們寫的，模仿真實會犯的那種錯。"
                "拖兩個標記，標出「AI 說的最密區間」與「真實的最密區間」。"),
      rows_card("兩個區間各有幾筆",
                [("AI 說的區間", "—", "w12rdAi"),
                 ("你標的區間", "—", "w12rdYou"),
                 ("差幾筆", "—", "w12rdDiff")]),
      info_card("為什麼會這樣",
                "AI 看圖是把像素轉成描述，中間沒有「回去數一次」的步驟。"
                "它的說法聽起來有多確定，跟它有多正確<strong>完全無關</strong>。")],
     "w12rdStatus", "先讀那段描述，再自己找真正的最密區間。",
     '<button class="btn btn-step" onclick="w12rdMove(-1)">標記左移</button>'
     '<button class="btn btn-step" onclick="w12rdMove(1)">標記右移</button>'
     '<button class="btn btn-toggle" onclick="w12rdShowAi()">顯示 AI 說的區間</button>'
     '<button class="btn btn-reset" onclick="w12rdReset()">重置</button>')}

{info("AI 的描述（我們寫的，模仿真實會犯的錯）",
      "「這份資料的馬力主要集中在 <strong>140 到 180</strong> 之間，呈現單峰的常態分布，"
      "少數高馬力的車形成右尾。」<br>"
      "——語氣很肯定、術語也用對了。問題是<strong>那個區間是錯的</strong>，"
      "而且「常態分布」這個描述也需要驗證，不是看一眼就能宣稱的。")}

{card("回到資料，自己數一次", C(2, 192), O(2, 192), src=S(2, 192),
      note="這一格提醒了另一件事：課程 lab 裡的 horsepower "
           "<strong>一開始根本不是數字</strong>（混了一個 <code>?</code>）。"
           "AI 對著一張畫錯的圖描述得再流暢，也還是錯的。")}

{quiz("qCross", "PART 02 · 自我檢測",
      "AI 對一張圖的描述，和你自己算出來的數字對不上。最可能的解釋是？",
      [(True, "它讀圖讀錯了。這是已知且常見的失效模式",
        "對。讀圖是把像素轉成描述，中間沒有回去核對數字的步驟。"
        "遇到不一致，<strong>以你自己算的為準</strong>。"),
       (False, "你的程式碼寫錯了",
        "當然要檢查，但別預設「機器比較不會錯」——"
        "這正是自動化偏誤的定義。兩邊都查，然後<strong>以能重現的那一邊為準</strong>。"),
       (False, "圖畫錯了",
        "有可能，但那也是你能自己驗證的事（回去看資料）。"
        "重點仍然是：<strong>能重算的才算數</strong>。")])}
"""

# ── P03 驗證迴圈 ──────────────────────────────────────────────────────
BODIES["verify"] = f"""
  <p>講完兩個失效模式，接下來是解法。解法不是「不要用 AI」，而是
  <strong>把它的輸出當成假設而不是結論</strong>，然後跑一個固定的驗證迴圈。
  這個迴圈只有五步，而且每一步都很便宜。</p>

{viz(svg("w12loopSvg", 340),
     [info_card("五個步驟",
                "按「單步」走一次。注意這五步<strong>沒有一步需要你自己想出答案</strong>——"
                "它們只要求你會跑幾行程式碼、並且知道要看什麼。"),
      rows_card("這一步",
                [("步驟", "0 / 5", "w12vfStep"),
                 ("要做什麼", "—", "w12vfWhat"),
                 ("本站哪一頁教", "—", "w12vfWhere")]),
      info_card("為什麼這是「你要學的東西」",
                "這五步全部需要看得懂並且改得動程式碼。"
                "所以這門課要練的不是打字，是<strong>把一個主張變成可以驗證的東西</strong>——"
                "那正是統計學這門學問本身在做的事。")],
     "w12vfStatus", "按「單步」走一次驗證迴圈。",
     '<button class="btn btn-step" onclick="w12vfStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w12vfPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w12vfReset()">重置</button>')}

{table(["步驟", "具體要做的事", "本站哪一頁"],
       [["① 看資料", "<code>shape</code>、<code>dtypes</code>、<code>describe()</code>",
         "<a href=\"p4_pandas.html#view\">P4</a>"],
        ["② 重算關鍵數字", "把那個主張的數字自己算一次",
         "<a href=\"p3_numpy.html#agg\">P3</a>、<a href=\"p4_pandas.html#group\">P4</a>"],
        ["③ 畫一張圖", "數字對得上不代表形狀對",
         "<a href=\"p5_visualization.html\">P5</a>"],
        ["④ 檢查假設與流程", "有沒有資料洩漏？評估用的是沒看過的資料嗎？",
         "<a href=\"p6_modeling_api.html#cv\">P6</a>"],
        ["⑤ 記下來", "固定種子、記下版本，讓別人重現得出來",
         "<a href=\"00b_setup.html\">00B</a>"]])}

{card("第一步永遠是這個", C(1, 31), O(1, 31), src=S(1, 31),
      note="看前五列。欄名對不對、有沒有整欄空白、數字的量級合不合理——"
           "三秒鐘就能排除掉一大類的錯。")}

{quiz("qVerify", "PART 03 · 自我檢測",
      "AI 告訴你「加上這五個交互作用項之後 R² 從 0.54 提升到 0.91」。你先做什麼？",
      [(False, "把這五項加進報告的模型",
        "R² 隨著變數增加<strong>一定</strong>會上升，這不是模型變好的證據。"),
       (True, "在沒看過的資料上評估一次",
        "對。訓練 R² 上升可能只是過度配適。"
        "切出測試集或用交叉驗證看一次，才知道它有沒有真的變好——"
        "這正是 <a href=\"p6_modeling_api.html#split\">P6</a> 與第 5 章的主題。"),
       (False, "檢查那五個交互作用有沒有統計顯著",
        "會有幫助，但五個檢定就有多重比較的問題，而且顯著不等於預測得更好。"
        "先做最直接的那一步：<strong>在沒看過的資料上試</strong>。")])}
"""

# ── P04 可重現性 ──────────────────────────────────────────────────────
BODIES["repro"] = f"""
  <p>驗證迴圈的最後一步是「記下來」，它值得單獨講。
  統計分析跟一般程式最大的差別是<strong>裡面有隨機性</strong>：
  切分、重抽樣、隨機森林抽變數。沒有固定種子的話，
  <strong>連你自己明天都重現不了今天的結果</strong>。</p>

{card("沒固定種子：跑兩次不一樣", C(2, 80), O(2, 80), src=S(2, 80),
      note="同一行跑兩次，四個數字完全不同。"
           "寫報告的時候這是災難。你沒辦法說明「我的 0.24 是怎麼來的」。")}

{card("固定種子：兩個產生器逐位相同", C(2, 82), O(2, 82), src=S(2, 82),
      note="<code>default_rng(1303)</code> 開兩次，抽出來一模一樣。"
           "本站每一張自己算的圖都是這樣產生的，"
           "所以任何人拿到程式碼都能重生同樣的數字。")}

{viz(svg("w12seedSvg", 320),
     [info_card("開關種子看看",
                "同一段模擬跑四次。固定種子時四條線完全重疊；"
                "關掉之後每次都不一樣——<strong>而且每一次都「看起來很合理」</strong>。"),
      rows_card("四次的結果",
                [("種子", "固定（1303）", "w12sdSeed"),
                 ("四次的估計值", "—", "w12sdVals"),
                 ("最大差距", "—", "w12sdRange")]),
      info_card("可重現不等於正確",
                "固定種子只保證「別人跑得出同樣的數字」，"
                "不保證那個數字是對的。但<strong>不可重現的結果連討論都沒辦法討論</strong>——"
                "它是所有其他檢查的前提。")],
     "w12sdStatus", "先看固定種子的版本，再關掉。",
     '<button class="btn btn-play" onclick="w12sdRun()">▶ 再跑四次</button>'
     '<button class="btn btn-toggle" id="w12sdBtn" onclick="w12sdTog()">種子：固定</button>'
     '<button class="btn btn-reset" onclick="w12sdReset()">重置</button>')}

{qa("觀念釐清", [
    ("固定種子會不會讓結果「作弊」？",
     "不會。種子只決定<strong>抽到哪一組隨機樣本</strong>，不影響方法本身的性質。"
     "真正該擔心的是<strong>挑種子</strong>——試十個種子挑結果最好看的那個，"
     "那才是作弊。所以要先定種子再跑，不是跑完再挑。"),
    ("那怎麼知道結果穩不穩定？",
     "換幾個種子各跑一次，看結果晃動多大。"
     "課程 lab 的 <code>ShuffleSplit(n_splits=10)</code> 就是在做這件事——"
     "它同時報告平均與標準差，後者才是重點。"
     "細節見 <a href=\"p6_modeling_api.html#cv\">P6</a>。"),
])}

{quiz("qRepro", "PART 04 · 自我檢測",
      "你跑了十個種子，其中一個的測試 MSE 特別低。報告裡該寫哪一個？",
      [(False, "最低的那一個，那是模型能達到的最佳表現",
        "這是挑種子，等於用測試集調參數。"
        "「能達到」跟「平均能達到」是兩回事，前者對新資料沒有意義。"),
       (True, "十個的平均，並且把標準差一起寫出來",
        "對。標準差告訴讀者「這個數字能晃多少」，"
        "沒有它的話，兩個模型差 0.5 到底算不算差別根本無從判斷。"),
       (False, "第一個跑的那個，因為它最沒有偏見",
        "單一個結果沒有偏見，但也沒有告訴你不確定性。"
        "既然已經跑了十個，就把資訊用完。")])}
"""

# ── P05 你要練的其實是什麼 ────────────────────────────────────────────
BODIES["you"] = f"""
  <p>把前面串起來：AI 很會產出<strong>看起來對的東西</strong>，
  而你要練的是判斷<strong>哪些是真的對</strong>。這件事需要三種能力，
  剛好就是這門課的三塊內容。</p>

{table(["你需要的能力", "為什麼", "在哪裡練"],
       [["看得懂並改得動幾行程式碼",
         "驗證迴圈的每一步都要跑程式碼；不會改就只能相信別人",
         "<a href=\"p1_python_basics.html\">P1</a>–<a href=\"p6_modeling_api.html\">P6</a>"],
        ["知道一個統計主張要滿足什麼條件才成立",
         "「顯著」「相關」「準確」各有前提，AI 不會替你檢查",
         "正課第 <a href=\"linear_regression.html\">3</a>–<a href=\"classification.html\">4</a> 章"],
        ["知道評估要用沒看過的資料",
         "這是整套機器學習最容易被繞過、也最致命的一條",
         "正課第 <a href=\"resampling_methods.html\">5</a>–<a href=\"model_selection.html\">6</a> 章"]])}

{viz(svg("w12mapSvg", 340),
     [info_card("這個站怎麼讀",
                "按按鈕看兩條路線。沒寫過程式的走完整路線；"
                "寫過但沒碰過資料科學套件的可以跳過前兩頁。"),
      rows_card("這條路線",
                [("適合誰", "—", "w12mpWho"),
                 ("順序", "—", "w12mpOrder"),
                 ("大概要多久", "—", "w12mpTime")]),
      info_card("先備頁是選讀",
                "它們不列入評分，也不是課程的一部分。"
                "但如果你在正課的第一份 lab 就卡在「這行在幹嘛」，"
                "回來讀完會省下更多時間。")],
     "w12mpStatus", "兩條路線，看哪一條是你。",
     '<button class="btn btn-toggle" onclick="w12mpSet(0)">完全沒寫過程式</button>'
     '<button class="btn btn-toggle" onclick="w12mpSet(1)">寫過程式，沒碰過資料科學</button>'
     '<button class="btn btn-toggle" onclick="w12mpSet(2)">兩者都會，直接進正課</button>')}

{info("最後一句",
      "這門課不是在跟 AI 比誰寫得快。那個比賽你不會贏，也不需要贏。"
      "它在練的是另一件事：<strong>當一個數字擺在你面前，你有沒有辦法判斷它站不站得住腳</strong>。"
      "這件事目前還沒有東西可以外包。")}

{quiz("qYou", "PART 05 · 自我檢測",
      "這門課練完之後，你跟「只會叫 AI 寫程式的人」最大的差別是什麼？",
      [(False, "你打字比較快",
        "不會，而且這也不重要。"),
       (True, "你能判斷一個統計結果站不站得住腳，並且自己驗證",
        "對。產出程式碼的成本已經趨近於零，<strong>審查的價值因此變高了</strong>。"
        "這門課練的是審查那一半。"),
       (False, "你不需要用 AI",
        "恰恰相反。你會用得更多也更放心，因為你查得動它。")])}

{hook("接下來讀什麼",
      '環境還沒好就先去 <a href="00b_setup.html">00B 環境安裝</a>（三分鐘）。'
      '沒寫過程式從 <a href="p1_python_basics.html">P1</a> 開始；'
      '寫過的直接跳 <a href="p3_numpy.html">P3 NumPy</a>。'
      '想直接進正課就從 <a href="introduction.html">第 1 章 統計學習導論</a> 開始。')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 找出不能信的地方",
      "AI 說：「這兩個變數的相關係數是 0.87，所以 X 造成了 Y 的變化。」問題在哪？",
      [(True, "相關不等於因果，而且它也沒說 0.87 是怎麼算的",
        "對。相關係數再高也不能推論方向與因果，"
        "而且它可能被一個離群值撐起來（見 <a href=\"p5_visualization.html\">P5</a>）。"
        "至少要先畫一張散佈圖。"),
       (False, "0.87 不夠高，要 0.95 以上才算相關",
        "沒有這種門檻。「多高算高」完全取決於領域與問題。"),
       (False, "應該要用 Spearman 相關係數",
        "換一個係數不會解決因果的問題。方法選擇是次要的，"
        "那個「所以」才是真正的錯。")])}

{quiz("qEx2", "EXERCISE 2 · 找出不能信的地方",
      "AI 說：「模型在測試集上的準確率是 99%，表現非常好。」你要先問什麼？",
      [(True, "類別是不是極度不平衡，以及測試集有沒有被污染",
        "對。如果 99% 的樣本都是同一類，「全部猜多數類」也有 99%。"
        "另外要確認前處理是不是在切分之後才做的"
        "（見 <a href=\"p6_modeling_api.html#cv\">P6 的資料洩漏</a>）。"),
       (False, "99% 太高了，一定是造假",
        "有些問題本來就好預測。先問<strong>可驗證的問題</strong>，不要先下結論。"),
       (False, "應該改用 F1 分數",
        "換指標是後面的事。先確認這個 99% 是怎麼來的。")])}

{quiz("qEx3", "EXERCISE 3 · 找出不能信的地方",
      "AI 說：「p 值是 0.001，所以這個變數的效果很大。」問題在哪？",
      [(True, "p 值小講的是「不是 0」很有把握，跟效果大小無關",
        "對。樣本夠大時，一個實務上可以忽略的效果也會有很小的 p 值。"
        "要談大小得看係數本身（見 <a href=\"p6_modeling_api.html#summary\">P6</a>）。"),
       (False, "p 值應該要小於 0.05 才算顯著，0.001 太小了",
        "0.001 比 0.05 小，是更強的證據。這個選項把方向搞反了。"),
       (False, "沒問題，p 值就是用來衡量效果大小的",
        "這正是最常見的誤解。p 值衡量的是證據強度，不是效果大小。")])}

{quiz("qEx4", "EXERCISE 4 · 找出不能信的地方",
      "AI 幫你把整份資料標準化之後才切訓練測試集，並回報測試 MSE。問題在哪？",
      [(True, "資料洩漏：標準化的參數用到了測試集的資訊",
        "對。這個測試 MSE 會偏樂觀，它已經不是 out-of-sample 的估計了。"
        "正確做法是把 scaler 與模型包成 Pipeline"
        "（見 <a href=\"p6_modeling_api.html#cv\">P6</a>）。"),
       (False, "標準化會改變資料的分布，不應該做",
        "標準化只是平移與縮放，不改變分布的形狀；"
        "而且第 6 章的收縮方法非做不可。問題出在<strong>順序</strong>。"),
       (False, "應該用 MinMaxScaler 而不是 StandardScaler",
        "換哪一種都一樣會洩漏。錯的是順序，不是選哪個轉換器。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>三張表：什麼時候該信 AI、驗證迴圈、以及這個站怎麼讀。</p>

{table(["這類問題", "交給 AI 划不划算", "為什麼"],
       [["語法、函式參數、環境錯誤", "✓ 很划算", "有標準答案，而且你能<b>馬上驗證</b>"],
        ["「這段程式碼在做什麼」", "✓ 划算", "讀懂之後你自己能核對"],
        ["「幫我寫一個做 X 的函式」", "△ 可以，但要看得懂再用", "能跑不等於做的是你要的事"],
        ["「這個結果顯著嗎」", "✗ 不划算", "它沒看過你的資料，也不知道假設成不成立"],
        ["「這張圖告訴我們什麼」", "✗ 不划算", "讀圖是已知的失效模式，會很肯定地說錯"],
        ["「這個模型可以上線了嗎」", "✗ 不划算", "牽涉流程、洩漏、族群差異。這些只有你知道"]])}

{table(["驗證迴圈", "一行程式碼版本"],
       [["① 看資料", "<code>df.shape</code>、<code>df.dtypes</code>、<code>df.describe()</code>"],
        ["② 重算關鍵數字", "<code>df.groupby(k)[v].mean()</code> 之類"],
        ["③ 畫一張圖", "<code>sns.histplot(...)</code> 或 <code>sns.scatterplot(...)</code>"],
        ["④ 檢查流程", "前處理在切分之後嗎？評估用沒看過的資料嗎？"],
        ["⑤ 記下來", "<code>random_state=0</code>、記下套件版本"]])}

{table(["你的情況", "建議路線"],
       [["完全沒寫過程式",
         "00B → P1 → P2 → P3 → P4 → P5 → P6 → 正課第 1 章"],
        ["寫過程式，沒碰過資料科學套件", "00B → P3 → P4 → P5 → P6 → 正課第 1 章"],
        ["兩者都熟", "直接進正課，遇到卡住再回來查"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 自動化偏誤是預設值。</strong>"
      "排版整齊、語氣肯定的答案，你天生就比較不會去查，靠流程對抗，不要靠意志力。<br>"
      "<strong>2. AI 讀圖會很肯定地說錯。</strong>"
      "遇到它的描述跟你算的對不上，以<strong>能重現的那一邊</strong>為準。<br>"
      "<strong>3. 你要練的是審查，不是打字。</strong>"
      "產出的成本趨近於零，判斷「這個數字站不站得住腳」的價值因此變高了。")}

{ver_note((1, 2))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* 這一頁用的 Auto 馬力資料：固定種子當場產生，形狀模仿真實的 Auto 分布
   （右偏、主峰在 70–110）。不是任何一份真實資料，重點是機制。 */
const w12hp = (() => {
  const rand = HC.stat.lcg(524), out = [];
  for (let i = 0; i < 240; i++) out.push(78 + Math.abs(HC.stat.normal(rand)) * 16);
  for (let i = 0; i < 100; i++) out.push(120 + HC.stat.normal(rand) * 26);
  for (let i = 0; i < 52; i++) out.push(175 + Math.abs(HC.stat.normal(rand)) * 22);
  return out.map(v => Math.max(46, Math.min(230, v)));
})();
function w12count(lo, hi) { return w12hp.filter(v => v >= lo && v < hi).length; }

/* ═══ w12an 錨定實驗 ═══ */
const w12anS = HC.svg('w12anchorSvg', {h: 340});
const w12Truth = 30.4, w12AiSays = 24.8;
let w12anG = 27.0, w12anPhase = 0, w12anFirst = null, w12anSecond = null;
function w12anDraw() {
  const s = w12anS;
  s.domain([18, 40], [0, 1]);
  const g = s.clearLayer('main');
  s.grid(5, 1, {xtitle: '平均 mpg 的估計', ydec: 0});
  const bar = (v, y, col, label) => {
    s.add('circle', {cx: s.X(v), cy: y, r: 11, fill: col}, g);
    const t = s.add('text', {x: s.X(v), y: y - 20, 'text-anchor': 'middle', cls: 'axlab',
                             fill: col}, g);
    t.textContent = label + ' ' + HC.fmt(v, 1);
  };
  bar(w12anG, 120, HC.tok.accent2, '你的估計');
  if (w12anFirst !== null) bar(w12anFirst, 176, HC.tok.muted, '第一次');
  if (w12anPhase >= 1) bar(w12AiSays, 220, HC.tok.accent, 'AI 說');
  if (w12anPhase >= 2) bar(w12Truth, 264, HC.tok.resid, '真實值');
  s.txtPx(310, 44, w12anPhase === 0 ? '先自己估一個數字'
          : (w12anPhase === 1 ? '現在再估一次' : '揭曉'),
          {cls: 'axtitle', anchor: 'middle'}, g);
  document.getElementById('w12anFirst').textContent =
    w12anFirst === null ? '—' : HC.fmt(w12anFirst, 1);
  document.getElementById('w12anSecond').textContent =
    w12anSecond === null ? '—' : HC.fmt(w12anSecond, 1);
  document.getElementById('w12anShift').textContent =
    (w12anFirst !== null && w12anSecond !== null)
      ? HC.fmt(w12anSecond - w12anFirst, 1) : '—';
  setStatus('w12anStatus', w12anPhase === 0
    ? '拖到你覺得合理的位置，然後按「看 AI 的答案」。'
    : (w12anPhase === 1
       ? 'AI 說 24.8。<b>再估一次</b>，然後看你有沒有被拉過去。'
       : '真實值是 30.4。AI 的 24.8 偏低，而多數人的第二次估計會往它靠。'));
}
function w12anGuess(d) {
  w12anG = Math.max(18, Math.min(40, w12anG + d * 0.6));
  if (w12anPhase >= 1) w12anSecond = w12anG;
  w12anDraw();
}
function w12anReveal() {
  if (w12anPhase === 0) { w12anFirst = w12anG; w12anPhase = 1; w12anSecond = w12anG; }
  w12anDraw();
}
function w12anTruth() { if (w12anPhase >= 1) w12anPhase = 2; w12anDraw(); }
function w12anReset() {
  w12anG = 27.0; w12anPhase = 0; w12anFirst = null; w12anSecond = null; w12anDraw();
}
if (w12anS) w12anDraw();

/* ═══ w12bi 自動化偏誤 ═══ */
const w12biS = HC.svg('w12biasSvg', {h: 320});
const w12biCases = [
  {who: '同學', check: '多半會追問「你用什麼檢定」', col: 'muted',
   note: '你會追問來源與方法 —— 這是<b>健康</b>的反應。'},
  {who: 'AI', check: '多半直接用了', col: 'resid',
   note: '同樣一句話，換成 AI 講，追問的比例明顯下降。<b>這就是自動化偏誤。</b>'},
  {who: '你自己算的', check: '你知道每一步怎麼來的', col: 'accent2',
   note: '唯一你真的知道前提成不成立的來源 —— 代價是你得看得懂那幾行。'}
];
let w12biI = 0;
function w12biDraw() {
  const g = w12biS.clearLayer('main');
  const c = w12biCases[w12biI];
  const col = HC.tok[c.col] || HC.tok.muted;
  w12biS.add('rect', {x: 60, y: 84, width: 500, height: 76, rx: 10,
                      fill: HC.tok.card, stroke: col, 'stroke-width': 2.4}, g);
  const t = w12biS.add('text', {x: 310, y: 120, 'text-anchor': 'middle', cls: 'axtitle'}, g);
  t.textContent = '「這兩組的差異是顯著的。」';
  const u = w12biS.add('text', {x: 310, y: 146, 'text-anchor': 'middle', cls: 'axlab'}, g);
  u.textContent = '—— ' + c.who + '說';
  w12biCases.forEach((cc, i) => {
    const on = i === w12biI;
    const x = 60 + i * 172;
    w12biS.add('rect', {x: x, y: 196, width: 156, height: 54, rx: 8,
                        fill: on ? (HC.tok[cc.col] || HC.tok.muted) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.4,
                        opacity: on ? 0.95 : 0.5}, g);
    const tt = w12biS.add('text', {x: x + 78, y: 220, 'text-anchor': 'middle', cls: 'axtitle',
                                   fill: on ? HC.tok.paper : HC.tok.muted}, g);
    tt.textContent = cc.who;
    const uu = w12biS.add('text', {x: x + 78, y: 240, 'text-anchor': 'middle', cls: 'axlab',
                                   fill: on ? HC.tok.paper : HC.tok.muted}, g);
    uu.textContent = i === 1 ? '追問的比例最低' : (i === 0 ? '會追問' : '你知道全部');
  });
  document.getElementById('w12biWho').textContent = c.who;
  document.getElementById('w12biCheck').textContent = c.check;
  setStatus('w12biStatus', c.note);
}
function w12biSet(i) { w12biI = i; w12biDraw(); }
if (w12biS) w12biDraw();

/* ═══ w12rd 讀圖對照器（本頁招牌）═══ */
const w12rdS = HC.svg('w12readSvg', {h: 340});
const w12BinW = 20, w12Lo = 40, w12Hi = 240;
let w12rdPos = 60, w12rdShow = false;
function w12rdDraw() {
  const s = w12rdS;
  const nb = (w12Hi - w12Lo) / w12BinW;
  const counts = [];
  for (let i = 0; i < nb; i++) counts.push(w12count(w12Lo + i * w12BinW,
                                                    w12Lo + (i + 1) * w12BinW));
  const mx = Math.max.apply(null, counts);
  s.domain([w12Lo, w12Hi], [0, mx * 1.18]);
  const g = s.clearLayer('main');
  s.grid(5, 4, {xtitle: 'horsepower', ytitle: '筆數'});
  counts.forEach((c, i) => {
    const x0 = w12Lo + i * w12BinW;
    const inYou = x0 >= w12rdPos && x0 < w12rdPos + 40;
    const inAi = w12rdShow && x0 >= 140 && x0 < 180;
    s.add('rect', {x: s.X(x0) + 1, y: s.Y(c), width: s.X(x0 + w12BinW) - s.X(x0) - 2,
                   height: s.Y(0) - s.Y(c),
                   fill: inYou ? HC.tok.accent2 : (inAi ? HC.tok.resid : HC.tok.muted),
                   opacity: inYou || inAi ? 0.95 : 0.55}, g);
  });
  const youN = w12count(w12rdPos, w12rdPos + 40);
  const aiN = w12count(140, 180);
  s.add('rect', {x: s.X(w12rdPos), y: s.Y(mx * 1.15), width: s.X(w12rdPos + 40) - s.X(w12rdPos),
                 height: 6, fill: HC.tok.accent2, rx: 3}, g);
  s.txt(w12rdPos + 20, mx * 1.15, '你標的', {cls: 'vlab', dy: -8, fill: HC.tok.accent2}, g);
  if (w12rdShow) {
    s.add('rect', {x: s.X(140), y: s.Y(mx * 1.05), width: s.X(180) - s.X(140),
                   height: 6, fill: HC.tok.resid, rx: 3}, g);
    s.txt(160, mx * 1.05, 'AI 說的 140–180', {cls: 'vlab', dy: -8, fill: HC.tok.resid}, g);
  }
  document.getElementById('w12rdAi').textContent = w12rdShow ? aiN + ' 筆' : '（先自己找）';
  document.getElementById('w12rdYou').textContent =
    w12rdPos + '–' + (w12rdPos + 40) + '：' + youN + ' 筆';
  document.getElementById('w12rdDiff').textContent =
    w12rdShow ? (youN - aiN) + ' 筆' : '—';
  setStatus('w12rdStatus', w12rdShow
    ? 'AI 說的 140–180 只有 <b>' + aiN + '</b> 筆，你標的區間有 <b>' + youN
      + '</b> 筆。<b>它把最密的區間講錯了整整一段。</b>'
    : '拖標記找最密的 40 單位區間，找到再按「顯示 AI 說的區間」。');
}
function w12rdMove(d) {
  w12rdPos = Math.max(w12Lo, Math.min(w12Hi - 40, w12rdPos + d * 20));
  w12rdDraw();
}
function w12rdShowAi() { w12rdShow = true; w12rdDraw(); }
function w12rdReset() { w12rdPos = 60; w12rdShow = false; w12rdDraw(); }
if (w12rdS) w12rdDraw();
"""

PAGEJS += r"""
/* ═══ w12vf 驗證迴圈 ═══ */
const w12vfS = HC.svg('w12loopSvg', {h: 340});
const w12vfSteps = [
  {w: '看資料：shape、dtypes、describe()', p: 'P4 pandas'},
  {w: '重算關鍵數字：把那個主張自己算一次', p: 'P3 NumPy／P4 pandas'},
  {w: '畫一張圖：數字對得上不代表形狀對', p: 'P5 視覺化'},
  {w: '檢查假設與流程：有沒有資料洩漏', p: 'P6 建模 API'},
  {w: '記下來：固定種子、記下版本', p: '00B 環境安裝'}
];
let w12vfI = 0, w12vfTimer = null;
function w12vfDraw() {
  const g = w12vfS.clearLayer('main');
  const cx = 310, cy = 176, r = 108;
  w12vfS.add('circle', {cx: cx, cy: cy, r: r, fill: 'none',
                        stroke: HC.tok.cardBorder, 'stroke-width': 2,
                        'stroke-dasharray': '6 6'}, g);
  w12vfSteps.forEach((st, i) => {
    const a = -Math.PI / 2 + i * 2 * Math.PI / 5;
    const x = cx + r * Math.cos(a), y = cy + r * Math.sin(a);
    const on = i < w12vfI;
    const cur = i === w12vfI - 1;
    w12vfS.add('circle', {cx: x, cy: y, r: 26,
                          fill: on ? (cur ? HC.tok.accent : HC.tok.accent2) : HC.tok.card,
                          stroke: HC.tok.cardBorder, 'stroke-width': 1.6,
                          opacity: on ? 0.95 : 0.5}, g);
    const t = w12vfS.add('text', {x: x, y: y + 6, 'text-anchor': 'middle', cls: 'axtitle',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = String(i + 1);
    const lx = cx + (r + 68) * Math.cos(a), ly = cy + (r + 68) * Math.sin(a);
    const u = w12vfS.add('text', {x: lx, y: ly + 4, 'text-anchor': 'middle', cls: 'axlab',
                                  fill: on ? HC.tok.ink : HC.tok.muted}, g);
    u.textContent = ['看資料', '重算', '畫圖', '檢查流程', '記下來'][i];
  });
  w12vfS.txtPx(cx, cy + 4, w12vfI === 0 ? 'AI 的輸出' : (w12vfI >= 5 ? '可以下結論了' : '驗證中'),
               {cls: 'axtitle', anchor: 'middle'}, g);
  const st = w12vfSteps[Math.max(0, w12vfI - 1)];
  document.getElementById('w12vfStep').textContent = w12vfI + ' / 5';
  document.getElementById('w12vfWhat').textContent = w12vfI === 0 ? '—' : st.w;
  document.getElementById('w12vfWhere').textContent = w12vfI === 0 ? '—' : st.p;
  setStatus('w12vfStatus', w12vfI === 0
    ? '把 AI 的輸出當成<b>假設</b>，不是結論。按「單步」開始驗證。'
    : (w12vfI >= 5 ? '五步走完，這個數字現在<b>可以拿去下結論</b>了。' : st.w + '。'));
}
function w12vfStep() { w12vfI = Math.min(5, w12vfI + 1); w12vfDraw(); }
function w12vfReset() {
  if (w12vfTimer) { clearTimeout(w12vfTimer); w12vfTimer = null; }
  w12vfI = 0; w12vfDraw();
}
function w12vfPlay() {
  w12vfReset();
  const tick = () => {
    if (w12vfI >= 5) { w12vfTimer = null; return; }
    w12vfStep();
    w12vfTimer = setTimeout(tick, 850);
  };
  w12vfTimer = setTimeout(tick, 400);
}
if (w12vfS) w12vfDraw();

/* ═══ w12sd 種子 ═══ */
const w12sdS = HC.svg('w12seedSvg', {h: 320});
let w12sdFixed = true, w12sdRuns = 0;
function w12sdSample(k) {
  const seed = w12sdFixed ? 1303 : (1303 + (w12sdRuns * 4 + k) * 7919);
  const rand = HC.stat.lcg(seed);
  const out = [];
  for (let i = 0; i < 40; i++) out.push(HC.stat.normal(rand));
  return HC.stat.mean(out);
}
function w12sdDraw() {
  const s = w12sdS;
  s.domain([-0.6, 0.6], [0, 5]);
  const g = s.clearLayer('main');
  s.grid(4, 1, {xtitle: '四次模擬各自估到的平均', ydec: 0, xdec: 1});
  const vals = [0, 1, 2, 3].map(k => w12sdSample(k));
  vals.forEach((v, k) => {
    const y = 4 - k;
    s.add('line', {x1: s.X(v), y1: s.Y(y - 0.35), x2: s.X(v), y2: s.Y(y + 0.35),
                   stroke: w12sdFixed ? HC.tok.accent2 : HC.tok.resid, 'stroke-width': 3.4}, g);
    s.txt(v, y, '第 ' + (k + 1) + ' 次', {cls: 'vlab', dy: -14,
                                          fill: w12sdFixed ? HC.tok.accent2 : HC.tok.resid}, g);
  });
  const rng = Math.max.apply(null, vals) - Math.min.apply(null, vals);
  document.getElementById('w12sdSeed').textContent = w12sdFixed ? '固定（1303）' : '沒有固定';
  document.getElementById('w12sdVals').textContent = vals.map(v => HC.fmt(v, 3)).join('、');
  document.getElementById('w12sdRange').textContent = HC.fmt(rng, 3);
  setStatus('w12sdStatus', w12sdFixed
    ? '四次<b>完全重疊</b>，因為它們用的是同一個種子。再按「再跑四次」也一樣。'
    : '四次各自不同，最大差距 <b>' + HC.fmt(rng, 3)
      + '</b>。每一次看起來都很合理，但你沒辦法說明自己那個數字是怎麼來的。');
}
function w12sdTog() {
  w12sdFixed = !w12sdFixed;
  document.getElementById('w12sdBtn').textContent = '種子：' + (w12sdFixed ? '固定' : '沒有');
  w12sdDraw();
}
function w12sdRun() { w12sdRuns += 1; w12sdDraw(); }
function w12sdReset() {
  w12sdFixed = true; w12sdRuns = 0;
  document.getElementById('w12sdBtn').textContent = '種子：固定';
  w12sdDraw();
}
if (w12sdS) w12sdDraw();

/* ═══ w12mp 學習路線 ═══ */
const w12mpS = HC.svg('w12mapSvg', {h: 340});
const w12mpCases = [
  {who: '完全沒寫過程式', order: ['00B', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', '正課'],
   time: '先備頁約 6–8 小時'},
  {who: '寫過程式，沒碰過資料科學套件', order: ['00B', 'P3', 'P4', 'P5', 'P6', '正課'],
   time: '先備頁約 4 小時'},
  {who: '兩者都熟', order: ['正課'], time: '直接開始'}
];
let w12mpI = 0;
function w12mpDraw() {
  const g = w12mpS.clearLayer('main');
  const c = w12mpCases[w12mpI];
  const all = ['00B', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', '正課'];
  const cw = 66;
  const x0 = 310 - all.length * cw / 2;
  all.forEach((nm, i) => {
    const on = c.order.indexOf(nm) >= 0;
    const last = nm === '正課';
    w12mpS.add('rect', {x: x0 + i * cw, y: 130, width: cw - 10, height: 56, rx: 8,
                        fill: on ? (last ? HC.tok.accent : HC.tok.accent2) : HC.tok.card,
                        stroke: HC.tok.cardBorder, 'stroke-width': 1.5,
                        opacity: on ? 0.95 : 0.35}, g);
    const t = w12mpS.add('text', {x: x0 + i * cw + (cw - 10) / 2, y: 164,
                                  'text-anchor': 'middle', cls: 'axtitle',
                                  fill: on ? HC.tok.paper : HC.tok.muted}, g);
    t.textContent = nm;
    if (i < all.length - 1 && on && c.order.indexOf(all[i + 1]) >= 0) {
      w12mpS.add('path', {d: 'M' + (x0 + i * cw + cw - 8) + ' 158 H ' + (x0 + (i + 1) * cw - 2),
                          stroke: HC.tok.accent2, 'stroke-width': 2.2}, g);
    }
  });
  w12mpS.txtPx(310, 76, c.who, {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent}, g);
  w12mpS.txtPx(310, 232, c.order.join(' → '), {cls: 'axlab', anchor: 'middle'}, g);
  w12mpS.txtPx(310, 262, c.time, {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w12mpWho').textContent = c.who;
  document.getElementById('w12mpOrder').textContent = c.order.join(' → ');
  document.getElementById('w12mpTime').textContent = c.time;
  setStatus('w12mpStatus', c.who + '：' + c.order.join(' → ') + '。');
}
function w12mpSet(i) { w12mpI = i; w12mpDraw(); }
if (w12mpS) w12mpDraw();
"""

apply("00a_why_code", BODIES, PAGEJS)
