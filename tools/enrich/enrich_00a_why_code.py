#!/usr/bin/env python3
"""00a_why_code.html：AI 時代的資料分析學習迴圈。冪等。

本頁刻意只保留一個靜態流程圖，不使用頁面專屬 JavaScript、SVG 或 Canvas。
AI 的能力與限制以近期研究及 NIST AI 600-1 為邊界；課程操作示例仍引用
既有 lab 的實跑內容。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, card, hook, info, lab_code, lab_output, quiz, table, ver_note  # noqa: E402

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

# ── PROLOGUE AI 不只會寫程式 ───────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>你想知道 Auto 汽車資料中的馬力與油耗有什麼關係。AI 能立刻給你繪圖程式，甚至寫出結論；但你還不知道欄位單位，也不知道圖會長什麼樣。這一頁練習的是：<strong>讓 AI 的幫忙留下你自己的學習過程</strong>。</p>
{info("先留一句自己的想法", "例如：『我猜馬力較大的車，mpg 較低。』mpg 是每加侖可行駛的英里數，數值越高代表同樣燃料跑得越遠。先寫下猜測與理由，後面才有東西可以對照。")}

{quiz("qPrologue", "PART 00 · 自我檢測",
      "下面哪一種分工最適合 AI 輔助的資料分析？",
      [(False, "把資料貼給 AI，直接採用它寫的結論",
        "資料的來源、收集方式與決策後果不在一句提示裡；流暢的結論仍可能越過證據。"),
       (True, "請 AI 產生候選做法，再由你執行、檢查並決定能否採用",
        "對。AI 擴大你能嘗試的範圍，你則用資料與領域知識決定哪些結果站得住腳。"),
       (False, "只把 AI 用在寫語法，其他資料工作完全不用",
        "太窄了。AI 也能協助搜尋、清理、EDA、文字探勘與報告整理；重點是每一步都要有驗收方法。")])}
"""

# ── LOOP 學習迴圈 ─────────────────────────────────────────────────────
BODIES["loop"] = f"""
  <p>有效的學習不是「看過答案」，而是反覆經歷一個小迴圈：
  <strong>先提出自己的想法，再動手嘗試，觀察證據，最後修正理解</strong>。
  AI 可以在每一步提供選項、範例或解釋，但不能替你跳過任何一步。</p>

  <div class="info-box purple" aria-label="資料分析學習迴圈">
    <span class="info-label">資料分析學習迴圈</span>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.75rem;margin:.65rem 0;">
      <div class="info-card"><div class="ic-title">① 提出想法</div>先預測結果、寫下理由，也說出你不確定的地方。</div>
      <div class="info-card"><div class="ic-title">② 動手嘗試</div>請 AI 協助拆解任務或產生初稿，再由你執行。</div>
      <div class="info-card"><div class="ic-title">③ 觀察證據</div>看資料、輸出與錯誤訊息，不只看 AI 的文字解釋。</div>
      <div class="info-card"><div class="ic-title">④ 修正理解</div>解釋預測為何不符，改一個條件後重新開始。</div>
    </div>
    <p style="margin:.5rem 0 0;"><strong>↻ 下一輪：</strong>把修正後的理解變成新的問題，而不是把第一個答案當終點。</p>
  </div>

{info("為什麼要先想再問",
      "如果一開始就看完整答案，你很難分辨自己原本懂了什麼。先寫下一句預測，"
      "再把 AI 的回答和實際輸出放在一起比對，錯誤才會變成可用的回饋。", "warm")}

{quiz("qLoop", "PART 01 · 自我檢測",
      "你要理解一份資料中兩個變數可能的關係。哪個做法最符合學習迴圈？",
      [(True, "先畫下你預期的形狀與理由，再請 AI 建議圖形，執行後比較差異",
        "對。你留下自己的預測，也用實際資料檢查 AI 和自己的想法。"),
       (False, "請 AI 直接寫出完整分析與結論，讀完就算完成",
        "你只看到了成品，沒有留下可供比較的預測，也沒有用輸出修正理解。"),
       (False, "先背熟所有繪圖函式，等完全不會出錯再碰資料",
        "學習迴圈需要小步嘗試與回饋；等到『全部會了』才開始，反而失去從錯誤學習的機會。")])}
"""

# ── WORKFLOW 每一步都能協作 ───────────────────────────────────────────
BODIES["workflow"] = f"""
  <p>沿用 Auto 這個問題，先只做一張馬力對 mpg 的散佈圖。請 AI 幫你列出需要確認的欄位、資料來源與繪圖步驟；環境操作在 <a href="00b_setup.html#data">00B</a>，完整提示寫法在 <a href="00c_ai_assisted.html#context">00C</a>。</p>
{table(["這一輪", "你留下什麼"], [["提出想法", "馬力與 mpg 可能往什麼方向變，理由是什麼"], ["動手嘗試", "執行繪圖程式，確認軸標籤與單位"], ["觀察證據", "圖是否有曲線、離群點，或沒有明顯關係"], ["修正理解", "寫一句猜測被支持或需要修改的地方，再提出下一個問題"]])}

{quiz("qWorkflow", "PART 02 · 自我檢測",
      "AI 建議你刪除某欄中的所有「?」。下一步最有學習價值的是？",
      [(False, "照做，因為問號一定是打字錯誤",
        "問號可能表示遺漏、拒答、未知或合法字元；沒有資料文件時不能直接決定。"),
       (True, "查資料說明並比較處理前後的筆數，再決定轉成遺漏值或保留",
        "對。你把 AI 的建議變成可查證的候選，並保留了清理決策的證據。"),
       (False, "換一個 AI 問同樣問題，兩者一致就刪除",
        "兩個模型可能依賴相同的通用慣例；一致仍不能替代這份資料的說明文件。")])}
"""

# ── JUDGMENT 人必須保留的判斷 ─────────────────────────────────────────
BODIES["judgment"] = f"""
  <p>即使散佈圖支持你的猜測，也不能直接寫「增加馬力造成油耗改變」。這份觀察資料還可能混有車重、年份等差異。<strong>把圖中看見的關係，和你想提出的解釋分開</strong>，正是這門課會逐步建立的能力。</p>
{info("這一輪先守住兩件事", "欄位的單位要查原始說明；圖中關係不能直接當成因果。AI 可以幫你提出其他解釋，但接受哪一個解釋仍要有資料與研究設計的支持。", "warm")}

{quiz("qJudgment", "PART 03 · 自我檢測",
      "模型在現有資料上的預測很準。下面哪個問題仍不能只靠這個分數回答？",
      [(False, "同一評估程式算出的誤差是多少",
        "這是可重算的技術問題；你可以執行程式核對。"),
       (True, "這份資料是否足以代表模型將服務的族群",
        "對。代表性取決於資料如何收集與實際使用情境，單一分數不會自動回答。"),
       (False, "資料共有幾列",
        "這也是可以直接從資料重算的事，不需要交給抽象判斷。")])}
"""

# ── HABITS 五個學習習慣 ───────────────────────────────────────────────
BODIES["habits"] = f"""
  <p>完成第一張圖後，換一個條件再練：例如只看某些年份的車，先猜圖形會怎麼變，再執行比較。不要只收藏 AI 修好的版本，要確認自己能解釋這次改動。</p>
{info("每次練習留下三句話", "① 我原本預期什麼。② 程式與資料實際顯示什麼。③ 我下一次會改哪個條件。這三句比再讀一遍完整答案更容易讓你看出還不懂哪裡。")}
{card("練習讀表：另一份課程示範資料", C(1, 31), O(1, 31), src=S(1, 31), note="這是 Ch01 的小型示範表，不是 Auto。先只指出欄名、資料型態與量級；等讀 Auto 時，也用同樣的方法確認拿到什麼。")}

{quiz("qHabits", "PART 04 · 自我檢測",
      "AI 已經幫你修好一段清理程式，而且能順利執行。怎樣確認你真的學會了？",
      [(False, "把修好的版本收藏起來，下次原樣貼上",
        "收藏答案有用，但不能證明你理解它在什麼條件下成立。"),
       (False, "再請 AI 用更簡單的話解釋一次",
        "解釋可以幫忙，但你仍可能只是在熟悉文字。"),
       (True, "改一個欄位型態或特殊值，先預測結果，再自己修改並執行",
        "對。條件改變後仍能預測、操作與解釋，才表示理解可以遷移。")])}

{hook("接下來讀什麼",
      '先到 <a href="00b_setup.html">00B 環境安裝</a>，確保每次嘗試都能真的執行；'
      '再讀 <a href="00c_ai_assisted.html">00C AI 輔助統計分析</a>，把這個學習迴圈變成具體的分析協作流程。'
      '進入先備課程後，可依序練習 <a href="p1_python_basics.html">P1–P6</a>。')}
"""

# ── EX 整合情境 ────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 公開資料搜尋",
      "你請 AI 找到一份適合研究大學生就業的公開資料。它列了三個網址與欄位。第一輪應怎麼做？",
      [(True, "逐一開啟官方來源，確認年份、抽樣對象、欄位定義與授權，再選資料",
        "對。搜尋結果是候選；來源頁與文件才是你能引用並判斷適用性的證據。"),
       (False, "選欄位最多的資料，資訊一定比較完整",
        "欄位多不代表樣本適合你的問題，也不代表收集品質較好。"),
       (False, "把三份資料合併，樣本越大越可靠",
        "定義、年份與抽樣框不同的資料不能因為欄名相似就直接合併。")])}

{quiz("qEx2", "EXERCISE 2 · 文字探勘",
      "AI 把一批訪談分成四個主題，名稱也很通順。你下一步該怎麼建立證據？",
      [(False, "把四個主題直接當成受訪者的真實觀點",
        "主題是分析產物，不是受訪者自己宣告的分類。"),
       (True, "抽查各主題的原文、尋找反例，並記錄分類規則與無法歸類的文本",
        "對。這讓你能判斷主題是否忠於材料，也保留模型分類失敗的線索。"),
       (False, "請 AI 為每個主題寫更有吸引力的名稱",
        "命名不能取代原文核對；名稱越流暢，越可能掩蓋分類本身不穩定。")])}

{quiz("qEx3", "EXERCISE 3 · 模型與報告",
      "AI 建好模型並寫道：『特徵 A 是造成結果的主要因素，因此應立即採用這項政策。』你要怎麼處理？",
      [(False, "只要測試分數高就保留原句",
        "預測表現不會自動建立因果關係，也不會替政策權衡成本與風險。"),
       (False, "把『造成』改成『相關』就可以發布",
        "用詞修正只是第一步；仍要交代資料、模型、效果大小、不確定性與適用範圍。"),
       (True, "回查研究問題與資料設計，重算關鍵結果，改寫成證據能支持的主張並列出限制",
        "對。這同時檢查問題定義、數值證據與結論邊界，也把決策責任留在人身上。")])}
"""

# ── REF 來源與安全邊界 ────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>本頁的 Auto 情境是學習活動；以下研究用來理解 AI 協作與核對的必要性，不代表所有分析都能自動完成。書籍概念參考 Bruce、Bruce 與 Gedeck 的 <cite>AI-Assisted Statistics for Data Scientists</cite> 第三版，第 11 章（2026）；完整操作流程見 <a href="00c_ai_assisted.html#reference">00C 來源與速查</a>。</p>

{table(["來源", "本頁怎麼使用", "解讀限制"],
       [["<a href=\"https://www.microsoft.com/en-us/research/publication/its-like-a-rubber-duck-that-talks-back-understanding-generative-ai-assisted-data-analysis-workflows-through-a-participatory-prompting-study/\">Drosos et al., CHIWORK 2024</a>",
         "理解 AI 輔助資料分析中的資訊搜尋、分析策略與 sensemaking 迴圈",
         "參與式研究提供工作流洞見，不是所有使用者的代表性成效估計"],
        ["<a href=\"https://www.nature.com/articles/s44387-025-00070-2\">Yang et al., npj Artificial Intelligence, 2026</a>",
         "說明 AI 可參與資料轉換、EDA、統計分析與機器學習等環節",
         "能力展示不等於每種資料、模型或決策都能無監督使用"],
        ["<a href=\"https://www.nature.com/articles/s41598-025-23798-y\">Bermejo et al., Scientific Reports, 2025</a>",
         "作為 AI 參與文字探勘的近期案例",
         "特定資料與研究設計的案例不能直接推廣成通用準確率"],
        ["<a href=\"https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence\">NIST AI 600-1: Generative AI Profile</a>",
         "支持來源追溯、輸出驗證、資料治理與人工監督的風險管理觀點",
         "這是風險管理框架，不替任何個別分析背書"],
        ["<a href=\"https://link.springer.com/article/10.1007/s10664-025-10622-4\">Ramasamy et al., Empirical Software Engineering, 2025</a>",
         "延伸閱讀：AI 如何在 notebook 的不同資料科學步驟提供建議",
         "研究任務偏簡單，不應直接外推到複雜的端到端分析"],
        ["<a href=\"https://aclanthology.org/2024.nlp4science-1.10/\">Zhou et al., NLP4Science 2024</a>",
         "延伸閱讀：從標記範例產生假設，再依錯誤案例反覆更新",
         "這裡的假設是分類模式，不等於已驗證的科學或因果理論"]])}

{info("使用資料時的最低安全線",
      "不要把未去識別的個資、機密研究資料或受限制資料直接貼進公開 AI 服務。"
      "先確認機構規範與服務條款；必要時只提供欄位結構、合成範例或去識別片段。"
      "無論工具多強，來源、單位、關鍵數字與對外結論都必須由人核對。", "warm")}

{ver_note((1,), include_frames=False)}
"""

# 本頁沒有專屬互動元件；quiz 使用全站共用 JavaScript。
PAGEJS = ""

apply("00a_why_code", BODIES, PAGEJS)
