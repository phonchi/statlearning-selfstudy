#!/usr/bin/env python3
"""classification.html（ISLP 第 4 章）完整自學充實。冪等。

內容依據：講義 04_Classification.pdf（61 頁）、Ch04-classification-lab-zh.ipynb、
ISLP 第 4 章（書上 p.136–198）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_classification.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 4
LAB = "Ch04-classification-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def slider(sid, label, lo, hi, step, val, fn, shown=None):
    """.controls-bar 裡的滑桿。flex:1 1 100% 讓它在窄螢幕獨佔一列，不會撐爆版面。"""
    return (f'<div class="slider-row" style="flex:1 1 100%;">'
            f'<label class="slider-label" for="{sid}">{label}</label>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}()">'
            f'<span class="slider-val" id="{sid}V">{val if shown is None else shown}</span></div>')


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_classification.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_classification.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_classification.py，固定種子）===== */\n"
            + r.stdout.strip())


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>第 3 章的 y 是連續的數字。現在換一種問題：<strong>y 是類別</strong>——這個人會不會違約、
  今天股市漲還是跌、這封信是不是垃圾信。這叫做<strong>分類</strong>（classification）。
  本章用 ISLP 的 <code>Default</code> 資料（n = 10000，違約率 3.33%）與課程 lab 的
  <code>Smarket</code> 資料當主線。</p>

  <p>直覺會說：把類別編成數字，然後照第 3 章配線性迴歸就好。<strong>這條路在兩個地方會撞牆</strong>，
  而且兩個都不是技術細節，是真的錯。</p>

{info("線性迴歸用在類別上的兩個致命傷", '''<strong>1. 多於兩類時，編碼本身就帶進了假設。</strong>
  把「中風 = 1、藥物過量 = 2、癲癇 = 3」丟進迴歸，等於宣告這三種病有順序，
  而且「中風到藥物過量」的距離等於「藥物過量到癲癇」的距離。換一個編碼順序，模型就變了。<br>
  <strong>2. 只有兩類時編碼沒問題，但輸出會跑出 [0, 1]。</strong>直線沒有上下界，
  一定會有某些 x 讓配出來的「機率」是負的或大於 1。''', "warm")}

  <p>第二點值得寫成式子。把 y 編成 0／1，然後配 $p(X) = \\beta_0 + \\beta_1 X$：</p>

  $$\\hat p(\\texttt{{balance}}) = -0.0752 + 0.00013 \\times \\texttt{{balance}}$$

  <p>這是 <code>Default</code> 資料上真的配出來的直線。把 <code>balance</code> 代 300 進去
  得到 −0.036——<strong>負的機率</strong>。ISLP 圖 4.2 左圖畫的就是這件事。
  右圖換成邏輯斯迴歸，整條曲線就乖乖待在 0 與 1 之間。</p>

{viz(svg("w04whySvg", 330),
     [info_card("怎麼看這張圖",
                '橫軸是 <code>balance</code>，上下兩排短刻度是真實資料：'
                '<span style="color:var(--pt-b);font-weight:700;">上排（y = 1）</span>是違約的人，'
                '<span style="color:var(--pt-a);font-weight:700;">下排（y = 0）</span>是沒違約的人。'
                '紅線是線性迴歸的配適，綠線是邏輯斯迴歸。'
                '<strong>紅色陰影是線性版給出負機率的區段。</strong>', "圖 4.2"),
      rows_card("在這個 balance 上",
                [("balance", "1000", "w04whyBal2"),
                 ("線性迴歸 p̂", "—", "w04whyLin"),
                 ("邏輯斯 p̂", "—", "w04whyLog"),
                 ("線性版合法嗎", "—", "w04whyOk")]),
      info_card("兩個係數的來歷",
                '邏輯斯的 <strong>β̂₀ = −10.6513、β̂₁ = 0.0055</strong> 就是 ISLP 表 4.1 的數字；'
                '線性版的 −0.0752 與 0.00013 是同一份資料上的最小平方解。'
                '線性版在 balance &lt; 579 給負值；要到 balance ≈ 8279 才會超過 1，'
                '那已經在資料範圍外了——<strong>但「原則上一定會超出」這件事不變。</strong>')],
     "w04whyStatus", "拖滑桿選一個 balance，右邊會同時給出兩個模型的預測機率。",
     slider("w04whyBal", "balance", 0, 2650, 25, 1000, "w04whyMove")
     + '<button class="btn btn-step" onclick="w04whyJump(300)">→ 跳到 balance = 300</button>'
     + '<button class="btn btn-toggle" onclick="w04whyToggle()">切換：只看邏輯斯</button>'
     + '<button class="btn btn-reset" onclick="w04whyReset()">重置</button>')}

  <h3>三類的編碼實驗：換個順序，模型就換了</h3>
  <p>下面同一批急診病人，只是換了編碼順序。線性迴歸看到的是「數字」，
  所以它會認真去配這些完全人造的順序與間距：</p>

{table(["編碼方式", "中風", "藥物過量", "癲癇", "這個編碼隱含的假設"],
       [["編碼 A", "1", "2", "3",
         "三種病有順序，而且「中風→藥物過量」與「藥物過量→癲癇」的差距一樣大"],
        ["編碼 B", "1", "3", "2",
         "順序變成中風 &lt; 癲癇 &lt; 藥物過量——同一份資料，配出完全不同的模型"],
        ["編碼 C", "2", "1", "3", "又是另一個模型。哪一個才對？<strong>都不對。</strong>"]])}

  <p>真正的問題是：<strong>類別沒有順序也沒有距離</strong>，硬編成數字就是在硬塞結構進去。
  正解是邏輯斯迴歸（兩類）與多元邏輯斯迴歸（多類），或者本章後半的生成式模型。</p>

{quiz("qWhy", "QUIZ · 為什麼不用迴歸",
      "把二元反應編成 0／1 之後配線性迴歸，跟邏輯斯迴歸比，最根本的問題是什麼？",
      [(True, "配出來的「機率」沒有上下界，一定有某些 x 給出小於 0 或大於 1 的值",
        "對。直線的值域是整個實數線，而機率必須落在 [0, 1]。ISLP 圖 4.2 左圖就是這個現象。"
        "邏輯斯函數把線性式子壓進 (0, 1)，這是它存在的理由。"),
       (False, "係數沒辦法用最小平方法估計，必須改用最大似然法",
        "不對。用最小平方法<strong>估得出來</strong>——上面那條 −0.0752 + 0.00013 × balance 就是。"
        "問題不在估不出來，而在估出來的東西不能當機率用。"),
       (False, "二元反應違反常態誤差假設，所以 p 值與信賴區間都不能用",
        "這句話本身沒錯，但不是「最根本」的問題。就算你完全不做推論、只要預測，"
        "負機率照樣會出現。順序上先解決值域，再談推論。")])}
"""

# ── P01 logistic ──────────────────────────────────────────────────────
_log_code1 = lab_code(CH, 25)
_log_code2 = lab_code(CH, 31) + "\n\n" + lab_code(CH, 33) + "\n\n" + lab_code(CH, 35)
_log_code3 = lab_code(CH, 45) + "\n\n" + lab_code(CH, 49)

BODIES["logistic"] = f"""
  <p>要讓輸出永遠落在 (0, 1)，最常用的做法是<strong>邏輯斯函數</strong>（logistic function）：</p>

  $$p(X) = \\frac{{e^{{\\beta_0 + \\beta_1 X}}}}{{1 + e^{{\\beta_0 + \\beta_1 X}}}}$$

  <p>把它整理一下，會冒出這一章最重要的兩個名詞。先移項：</p>

  $$\\underbrace{{\\frac{{p(X)}}{{1 - p(X)}}}}_{{\\text{{勝算 odds}}}} = e^{{\\beta_0 + \\beta_1 X}}
    \\qquad\\Longleftrightarrow\\qquad
    \\underbrace{{\\log\\!\\left(\\frac{{p(X)}}{{1-p(X)}}\\right)}}_{{\\text{{log-odds / logit}}}}
    = \\beta_0 + \\beta_1 X$$

  <p><strong>勝算</strong>（odds）是「發生機率 ÷ 不發生機率」，範圍 (0, ∞)；
  取 log 之後範圍變成整個實數線，這個量叫 <strong>log-odds</strong> 或 <strong>logit</strong>。
  所以邏輯斯迴歸真正線性的東西不是機率，<strong>是 log-odds</strong>。這句話決定了係數怎麼解讀。</p>

{info("三個一句話的重點", '''<strong>1. β₁ 是 log-odds 的斜率。</strong>x 增加一單位，log-odds 增加 β₁，
  勝算乘上 e^β₁。<strong>機率增加多少則要看你站在哪裡</strong>——同樣的 β₁，在 p ≈ 0.5 附近影響最大。<br>
  <strong>2. 係數用最大似然法（maximum likelihood）估。</strong>找一組 β 讓「觀察到的這批 0／1
  出現的機率」最大，沒有封閉解，要迭代。最小平方法只是常態假設下的最大似然特例。<br>
  <strong>3. z 統計量就是第 3 章的 t 統計量。</strong>β̂ 除以它的標準誤，大到某個程度就拒絕 β = 0。''')}

{viz(svg("w04shapeSvg", 250) + "\n" + svg("w04shapeSvg2", 220),
     [rows_card("目前的模型",
                [("β₀", "−1.00", "w04shapeB0T"), ("β₁", "0.80", "w04shapeB1T"),
                 ("p(0)", "—", "w04shapeP0"), ("p(1)", "—", "w04shapeP1"),
                 ("p = 0.5 的 x", "—", "w04shapeHalf"),
                 ("勝算比 e^β₁", "—", "w04shapeOR")]),
      info_card("兩張圖要一起看",
                '上圖是機率 p(x)，<strong>S 形、有上下界、斜率一直在變</strong>；'
                '下圖是同一個模型的 log-odds，<strong>一條直線，斜率永遠是 β₁</strong>。'
                '虛線是勝算（odds），它 ≥ 0 而且指數上升，很快就衝出圖外——'
                '這正是「不要用勝算的變化量講故事」的原因。'),
      info_card("β₁ 的符號與大小",
                'β₁ &gt; 0 曲線往右上、β₁ &lt; 0 往右下；<strong>|β₁| 愈大轉折愈陡</strong>，'
                'β₁ = 0 就是一條水平線（x 完全沒用）。'
                'β₀ 只負責左右平移：p = 0.5 的位置在 x = −β₀/β₁。')],
     "w04shapeStatus", "推兩個滑桿看 S 曲線怎麼動；下面那條 log-odds 永遠是直線。",
     slider("w04shapeB0", "β₀", -8, 8, 0.2, -1, "w04shapeDraw")
     + slider("w04shapeB1", "β₁", -3, 3, 0.05, 0.8, "w04shapeDraw")
     + '<button class="btn btn-reset" onclick="w04shapeReset()">重置</button>')}

{qa("觀念釐清", [
    ("Q：邏輯斯迴歸的係數到底怎麼解讀？「balance 每多一元，違約機率增加 0.0055」對嗎？",
     "<p><strong>不對，這是最常見的誤讀。</strong>0.0055 是 <em>log-odds</em> 的變化，不是機率的變化。"
     "正確的說法有兩種：</p>"
     "<ul><li>「<code>balance</code> 每增加一元，違約的 <strong>log-odds 增加 0.0055</strong>」；</li>"
     "<li>「違約的 <strong>勝算乘上</strong> $e^{0.0055} = 1.0055$，也就是多 0.55%」——"
     "注意是勝算多 0.55%，不是機率多 0.55 個百分點。</li></ul>"
     "<p>為什麼機率的變化講不出一個數字？因為它取決於你站在哪裡。用表 4.1 的係數算："
     "balance = 1000 時 p̂ = 0.00576；balance = 2000 時 p̂ = 0.586。"
     "同樣是多 1000 元，在低 balance 區機率幾乎沒動，在 2000 附近卻是斷崖。"
     "S 曲線最陡的地方斜率是 β₁/4——這是唯一能快速估「機率變化」的地方，"
     "而且只在 p ≈ 0.5 附近成立。</p>"
     "<p>順帶一提，這也是為什麼報告邏輯斯迴歸時大家愛講<strong>勝算比</strong>（odds ratio, $e^{\\beta_1}$）："
     "它是一個不隨 x 改變的常數，講起來才不會錯。</p>"),
])}

  <h3 id="dx-log">講義完整實作：在 <code>Smarket</code> 上配邏輯斯迴歸</h3>
{card("講義 04 · sm.GLM + Binomial（六個預測變數）", _log_code1, lab_output(CH, 25),
      src=src("25"),
      note="<code>family=sm.families.Binomial()</code> 是關鍵——同一支 <code>sm.GLM()</code>"
           "換一個 family 就變成別的廣義線性模型（最後一節會回來講）。"
           "看那排 p 值：最小的是 <code>Lag1</code> 的 0.145，<strong>連 0.05 都沒到</strong>。"
           "用前幾天的報酬預測今天的漲跌，本來就不該有效。")}

{card("講義 04 · 從機率到標籤，再到混淆矩陣", _log_code2, lab_output(CH, 35),
      src=src("31、33、35"),
      note="<code>predict()</code> 回傳的是<strong>機率</strong>，不是標籤；"
           "要自己挑一個閾值把它切成 <code>Up</code>／<code>Down</code>。"
           "這裡用 0.5，正確率 (507 + 145) / 1250 = 52.2%——但這是<strong>訓練</strong>正確率，"
           "同一批資料又訓練又測試，一定太樂觀。")}

{card("講義 04 · 誠實一點：2005 年當測試集", _log_code3, lab_output(CH, 49),
      src=src("45、49、51"),
      note="用 2001–2004 訓練、2005 測試，正確率掉到 <strong>48.0%</strong>（錯誤率 52.0%，"
           "見儲存格 51）——<strong>比丟硬幣還差</strong>。訓練 52.2% 對測試 48.0%，"
           "這個落差就是第 5 章重抽樣要處理的主題。")}

{quiz("qLog", "QUIZ · 係數的解讀",
      "某邏輯斯迴歸模型裡 <code>balance</code> 的係數是 0.0055。下面哪個說法對？",
      [(True, "balance 每多一元，違約的勝算乘上 e^0.0055 ≈ 1.0055",
        "對。線性的是 log-odds，所以「加法」發生在 log-odds 上，換回勝算就變成「乘法」。"
        "勝算比 e^β₁ 是一個不隨 balance 改變的常數，這是它好用的地方。"),
       (False, "balance 每多一元，違約機率增加 0.0055",
        "不對。這是把 log-odds 的變化當成機率的變化。機率的變化量隨位置而變："
        "balance 從 1000 到 2000，p̂ 從 0.006 跳到 0.586，平均一元遠遠不是 0.0055。"),
       (False, "balance 每多一元，違約機率乘上 1.0055",
        "也不對。乘上 e^β₁ 的是<strong>勝算</strong> p/(1−p)，不是機率 p。"
        "當 p 很小時勝算 ≈ 機率，這個說法才勉強接近；p 大的時候會嚴重高估。")])}
"""

# ── P02 multinomial ───────────────────────────────────────────────────
BODIES["multinomial"] = f"""
  <p>把一個預測變數換成 p 個，式子幾乎不用改——線性部分變成 $\\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p$
  就好。真正值得停下來的是<strong>加了變數以後係數會變號</strong>這件事。</p>

  <p>ISLP 的 <code>Default</code> 例子最經典。只用 <code>student</code> 一個變數配（表 4.2），
  <code>student[Yes]</code> 的係數是 <strong>+0.4049</strong>：學生比較容易違約。
  可是把 <code>balance</code> 與 <code>income</code> 一起放進去（表 4.3），
  同一個 <code>student[Yes]</code> 變成 <strong>−0.6468</strong>：學生比較不容易違約。
  <strong>同一份資料，符號翻過來了。</strong></p>

{info("這叫混淆（confounding），不是矛盾", '''兩個係數都對，只是在回答不同的問題。<br>
  <strong>+0.4049 回答的是：</strong>「隨便抓一個學生跟一個非學生比，誰比較容易違約？」——學生。
  因為學生的 <code>balance</code> 整體偏高。<br>
  <strong>−0.6468 回答的是：</strong>「<em>在 balance 相同</em> 的前提下，學生跟非學生誰比較容易違約？」——非學生。<br>
  多元迴歸的每個係數都是「<strong>控制住其他變數之後</strong>」的效果。
  ISLP 圖 4.3 左圖是前者、右圖（依 balance 分層的箱形圖）是後者。''', "warm")}

  <p>用表 4.3 的係數算兩個具體的人（ISLP 式 4.8、4.9）：balance = 1500、income = 40（千元）的
  <strong>學生</strong>違約機率是 0.058，同樣條件的<strong>非學生</strong>是 0.105——
  差了將近一倍，而且方向跟「學生風險高」的直覺相反。</p>

  <h3>多於兩類：多元邏輯斯迴歸</h3>

  <p>兩類的邏輯斯迴歸沒辦法直接處理 K &gt; 2。做法是<strong>挑一類當基準</strong>（baseline，
  習慣挑第 K 類），然後對其餘每一類寫一條 log-odds：</p>

  $$\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid X = x)}}{{\\Pr(Y = K \\mid X = x)}}\\right)
    = \\beta_{{k0}} + \\beta_{{k1}} x_1 + \\cdots + \\beta_{{kp}} x_p,
    \\qquad k = 1, \\ldots, K-1$$

  <p>只要估 K − 1 組係數。另一種等價的寫法叫 <strong>softmax</strong>，它不挑基準、K 類完全對稱：</p>

  $$\\Pr(Y = k \\mid X = x) = \\frac{{e^{{\\beta_{{k0}} + \\beta_{{k1}} x_1 + \\cdots + \\beta_{{kp}} x_p}}}}
    {{\\sum_{{l=1}}^{{K}} e^{{\\beta_{{l0}} + \\beta_{{l1}} x_1 + \\cdots + \\beta_{{lp}} x_p}}}}$$

{table(["", "基準類寫法（式 4.10–4.12）", "softmax 寫法（式 4.13）"],
       [["要估幾組係數", "K − 1 組", "K 組（多估一組，但有一組是多餘的）"],
        ["係數怎麼解讀", "相對於基準類的 log-odds", "只有<strong>兩類之間的差</strong> β<sub>k</sub> − β<sub>k′</sub> 有意義"],
        ["換基準／平移係數", "係數全變，但預測值不變", "全部係數同加一個常數，預測值不變"],
        ["常見於", "統計軟體（<code>statsmodels</code>）", "機器學習與神經網路（第 10 章會再遇到）"]])}

{info("兩種寫法給的預測值完全一樣", '''ISLP §4.3.5 講得很清楚：換基準類、或用 softmax，
  <strong>配適值、任兩類之間的 log-odds、以及其他關鍵輸出都不變</strong>，變的只有係數本身的數值。
  所以看到別人的多類別邏輯斯係數時，第一件事是問「基準是哪一類」——
  不問清楚就沒辦法解讀。''')}

  <h3 id="dx-mul">講義完整實作：只留 <code>Lag1</code> 與 <code>Lag2</code></h3>
{card("講義 04 · 砍掉沒用的變數再測一次", lab_code(CH, 53), lab_output(CH, 53),
      src=src("53、55"),
      note="六個變數的 p 值都很醜，那就只留看起來最有希望的兩個。測試正確率從 48.0% 升到 "
           "<strong>(35 + 106) / 252 = 56.0%</strong>；而且在「模型說會漲」的日子裡，"
           "它有 <strong>106 / (106 + 76) = 58.2%</strong> 準（儲存格 55）。"
           "不過先別開心：那 252 天裡本來就有 141 天在漲，<strong>每天都猜漲也有 56%</strong>。"
           "整體正確率在這裡根本沒有資訊量——這是下面「閾值與混淆矩陣」那一節的引子。")}

{quiz("qMul", "QUIZ · 混淆",
      "只用 <code>student</code> 配時它的係數是正的，加入 <code>balance</code> 後變成負的。"
      "該怎麼理解？",
      [(True, "兩個係數在回答不同的問題：後者是「在 balance 相同的前提下」的效果",
        "對。多元迴歸的係數一律是「控制住其他變數之後」的偏效果。"
        "學生整體 balance 偏高所以整體違約率高；但同樣的 balance 之下，學生反而比較不容易違約。"),
       (False, "其中一個模型配錯了，應該相信變數比較多的那一個",
        "兩個模型都沒配錯，各自都是它所設定問題的正確答案。「相信變數多的」也不是普遍原則——"
        "要看你問的是<strong>邊際</strong>效果還是<strong>偏</strong>效果。想預測「該不該發卡給這個學生」用後者；"
        "想知道「學生族群整體風險」用前者。"),
       (False, "這是共線性造成的，把 student 或 balance 移掉一個就好",
        "方向不對。<code>student</code> 與 <code>balance</code> 確實相關，但這裡的現象是混淆"
        "（confounding）而不是共線性造成的不穩定——係數的標準誤沒有爆掉，符號翻轉是<strong>真實的、"
        "可解釋的</strong>。移掉變數會讓你回去回答另一個問題，不是修好了什麼。")])}
"""

# ── P03 LDA ───────────────────────────────────────────────────────────
_lda_code1 = lab_code(CH, 66) + "\n\n" + lab_code(CH, 68) + "\n\n" + lab_code(CH, 72)
_lda_code2 = lab_code(CH, 74) + "\n\n" + lab_code(CH, 77) + "\n\n" + lab_code(CH, 79)

BODIES["lda"] = f"""
  <p>邏輯斯迴歸是直接建模 $\\Pr(Y = k \\mid X = x)$。這一節換一條路：
  <strong>先分別建模「每一類裡面 X 長什麼樣子」，再用 Bayes 定理翻回去</strong>。
  這類方法叫<strong>生成式模型</strong>（generative model）。</p>

  <p>設 $\\pi_k$ 是第 k 類的<strong>先驗機率</strong>（prior，隨便抓一筆資料屬於第 k 類的機率），
  $f_k(x) = \\Pr(X = x \\mid Y = k)$ 是第 k 類裡 X 的密度。Bayes 定理說：</p>

  $$\\Pr(Y = k \\mid X = x) = \\frac{{\\pi_k f_k(x)}}{{\\sum_{{l=1}}^{{K}} \\pi_l f_l(x)}}$$

{info("為什麼還要別的方法？ISLP §4.4 開頭給了三個理由", '''<strong>1. 兩類分得很開的時候，
  邏輯斯迴歸的係數會爆掉。</strong>完美可分時最大似然沒有有限解，係數往無限大跑。生成式模型不會。<br>
  <strong>2. n 小而各類內的 X 近似常態時，生成式模型更準。</strong>它用上了「常態」這個額外資訊。<br>
  <strong>3. K &gt; 2 時很自然。</strong>不用挑基準類，每一類算一個 δ<sub>k</sub>(x) 比大小就好。''')}

  <p><strong>LDA</strong>（linear discriminant analysis，線性判別分析）的假設是：
  每一類的 X 是常態，<strong>平均數各類不同，但變異數共用</strong>。p = 1 時</p>

  $$f_k(x) = \\frac{{1}}{{\\sqrt{{2\\pi}}\\,\\sigma}}
    \\exp\\!\\left(-\\frac{{(x - \\mu_k)^2}}{{2\\sigma^2}}\\right)$$

  <p>代進 Bayes 定理、取 log、把跟 k 無關的項全部丟掉，剩下的就是<strong>判別函數</strong>
  （discriminant function）：</p>

  $$\\delta_k(x) = x \\cdot \\frac{{\\mu_k}}{{\\sigma^2}} - \\frac{{\\mu_k^2}}{{2\\sigma^2}} + \\log \\pi_k$$

  <p>把 x 分到 $\\delta_k(x)$ 最大的那一類。<strong>δ 是 x 的一次式</strong>——這就是名字裡「線性」的來源。
  兩類且 $\\pi_1 = \\pi_2$ 時，邊界剛好落在兩個平均數的中點 $(\\mu_1 + \\mu_2)/2$。</p>

{viz(svg("w04lda1Svg", 320),
     [rows_card("目前的設定",
                [("模型", "LDA（共用 σ）", "w04lda1Mode"),
                 ("π₁ · π₂", "0.50 · 0.50", "w04lda1Pri"),
                 ("使用的 σ₁ · σ₂", "—", "w04lda1Sig"),
                 ("決策邊界", "—", "w04lda1Bnd"),
                 ("中點 (μ₁+μ₂)/2", "—", "w04lda1Mid")]),
      info_card("為什麼畫的是 πₖ·fₖ(x) 而不是 fₖ(x)",
                '因為要讓「兩條曲線的交點」正好就是決策邊界。'
                'Bayes 分類器比的是 π<sub>k</sub>f<sub>k</sub>(x) 的大小，'
                '所以把先驗乘進去畫，<strong>交點在哪裡、邊界就在哪裡</strong>，'
                '不用另外算。把 π₁ 拉大你會看到邊界往右跑——先驗大的那一類'
                '搶到更多地盤。', "圖 4.4"),
      info_card("勾了「允許不同 σ」就變成 QDA",
                '共用 σ 時 x² 的係數在相減時剛好抵消，只剩一次項，所以邊界是<strong>一個點</strong>。'
                '一旦 σ₁ ≠ σ₂，x² 的係數不再抵消，邊界變成二次方程式的根——'
                '<strong>可能有兩個點</strong>。這就是 QDA 與 LDA 的全部差別。')],
     "w04lda1Status", "推 μ 與 σ 的滑桿看兩個常態密度怎麼動，虛線是決策邊界。",
     slider("w04lda1M1", "μ₁", -4, 1, 0.1, -1.25, "w04lda1Draw")
     + slider("w04lda1M2", "μ₂", -1, 4, 0.1, 1.25, "w04lda1Draw")
     + slider("w04lda1S1", "σ₁", 0.4, 2.5, 0.05, 1, "w04lda1Draw")
     + slider("w04lda1S2", "σ₂", 0.4, 2.5, 0.05, 1, "w04lda1Draw")
     + slider("w04lda1P1", "π₁", 0.05, 0.95, 0.05, 0.5, "w04lda1Draw")
     + '<button class="btn btn-toggle" onclick="w04lda1Toggle()">允許不同 σ（QDA）</button>'
     + '<button class="btn btn-reset" onclick="w04lda1Reset()">重置</button>')}

  <p>p &gt; 1 時把常態換成<strong>多變量常態</strong> $N(\\mu_k, \\Sigma)$，
  $\\mu_k$ 是各類自己的平均向量、$\\Sigma$ 是<strong>所有類共用</strong>的共變異數矩陣。
  判別函數變成矩陣版：</p>

  $$\\delta_k(x) = x^{{\\mathsf{{T}}}} \\Sigma^{{-1}} \\mu_k
    - \\frac{{1}}{{2}} \\mu_k^{{\\mathsf{{T}}}} \\Sigma^{{-1}} \\mu_k + \\log \\pi_k$$

  <p>還是 x 的一次式，所以邊界是超平面。K = 3 類時會有 3 條邊界線
  （每一對類別一條），把平面切成三塊——ISLP 圖 4.6 畫的就是這個。</p>

{qa("觀念釐清", [
    ("Q：LDA 與邏輯斯迴歸都給線性邊界，那差在哪？什麼時候該選哪個？",
     "<p>差在<strong>係數是怎麼決定的</strong>。ISLP §4.5.1 把兩者都寫成同一個形式：</p>"
     "<p>$\\log\\!\\left(\\frac{\\Pr(Y=k|X=x)}{\\Pr(Y=K|X=x)}\\right) = a_k + \\sum_{j=1}^{p} b_{kj}x_j$</p>"
     "<p>兩邊的<strong>函數形式一模一樣</strong>，都是 x 的線性函數。差別是："
     "LDA 的 $a_k, b_{kj}$ 是「假設各類 X 服從共用共變異數的常態」之後，"
     "由 $\\hat\\pi_k, \\hat\\mu_k, \\hat\\Sigma$ 算出來的；"
     "邏輯斯迴歸的係數則是直接讓<strong>條件似然</strong>最大——它對 X 的分佈完全不做假設。</p>"
     "<p>所以取捨很清楚：</p>"
     "<ul><li><strong>各類內的 X 真的近似常態、n 又小</strong>：選 LDA。它多用了分佈資訊，"
     "變異較小。ISLP 情境 1 裡 LDA 表現最好。</li>"
     "<li><strong>X 明顯不常態（重尾、類別型變數、極端值多）</strong>：選邏輯斯迴歸。"
     "ISLP 情境 3 把資料換成 t 分佈，邏輯斯就贏了 LDA。</li>"
     "<li><strong>兩類分得很開</strong>：LDA（邏輯斯的最大似然會發散）。</li>"
     "<li><strong>要做推論、要 p 值、要處理類別型預測變數</strong>：邏輯斯迴歸的工具鏈成熟得多。</li></ul>"
     "<p>實務上兩者的預測往往幾乎一樣——lab 儲存格 79 的 LDA 混淆矩陣"
     "（35／35／76／106）跟儲存格 53 的邏輯斯<strong>一個數字都沒差</strong>。"
     "這不是巧合，是式 4.32 保證的。</p>"),
])}

  <h3 id="dx-lda">講義完整實作：<code>LinearDiscriminantAnalysis</code></h3>
{card("講義 04 · 配 LDA 並讀出估計的參數", _lda_code1, lab_output(CH, 68),
      src=src("66、68、72"),
      note="<code>means_</code> 是 μ̂₁、μ̂₂（每一列一類、每一欄一個變數）："
           "市場下跌的日子前兩天報酬偏正，上漲的日子前兩天偏負。"
           "<code>priors_</code>（儲存格 72）給 π̂ = <code>[0.49198397, 0.50801603]</code>，"
           "就是訓練資料裡 Down／Up 的比例——LDA 的先驗預設就是這樣估的。"
           "注意 <code>drop(columns=['intercept'])</code>：<code>LDA</code> 自己會處理截距。")}

{card("講義 04 · 線性判別方向與預測結果", _lda_code2, lab_output(CH, 79),
      src=src("74、77、79"),
      note="<code>scalings_</code> = <code>[[-0.642], [-0.514]]</code> 是那條線性組合的方向："
           "−0.64 × Lag1 − 0.51 × Lag2 很大就猜 Up、很小就猜 Down。"
           "混淆矩陣跟邏輯斯（儲存格 53）<strong>完全相同</strong>——"
           "兩個方法在這份資料上的線性邊界幾乎重疊。")}

{quiz("qLda", "QUIZ · LDA 的假設",
      "LDA（p &gt; 1）到底假設了什麼？",
      [(True, "每一類的 X 服從多變量常態，平均向量各類不同，但共變異數矩陣所有類共用",
        "對。「平均不同」讓類別分得開，「共變異數共用」讓 x² 項在判別函數相減時抵消，"
        "邊界因此是線性的。放掉共用這一條就變成 QDA。"),
       (False, "每一類的 X 服從多變量常態，平均與共變異數矩陣都各類共用",
        "平均也共用的話兩類就完全同分佈了，根本分不開。LDA 的平均向量一定是各類自己的。"),
       (False, "X 的各個分量在每一類內互相獨立，且服從常態",
        "這是 <strong>Naive Bayes</strong>（配上常態密度）的假設，不是 LDA。"
        "LDA 允許變數之間相關——相關結構就寫在共用的 Σ 的非對角元素裡。"
        "有趣的是 ISLP §4.5.1 指出：常態版的 Naive Bayes 其實是「Σ 被限制成對角矩陣」的 LDA。")])}

{table(["", "要估的參數", "p = 2, K = 2 時", "p = 50, K = 2 時"],
       [["先驗 π<sub>k</sub>", "K − 1 個", "1", "1"],
        ["平均 μ<sub>k</sub>", "K × p 個", "4", "100"],
        ["共用 Σ（LDA）", "p(p+1)/2 個", "3", "1275"],
        ["各自 Σ<sub>k</sub>（QDA）", "K·p(p+1)/2 個", "6", "<strong>2550</strong>"]])}
"""

# ── P04 QDA / Naive Bayes ─────────────────────────────────────────────
_qda_code = lab_code(CH, 89) + "\n\n" + lab_code(CH, 93) + "\n\n" + lab_code(CH, 95)
_nb_code = (lab_code(CH, 102) + "\n\n" + lab_code(CH, 110) + "\n\n"
            + lab_code(CH, 116) + "\n\n" + lab_code(CH, 117))

BODIES["qda"] = f"""
  <p>LDA 逼所有類共用同一個 $\\Sigma$。<strong>QDA</strong>（quadratic discriminant analysis）
  放掉這一條：讓每一類有自己的 $\\Sigma_k$。判別函數立刻多出二次項：</p>

  $$\\delta_k(x) = -\\frac{{1}}{{2}}(x - \\mu_k)^{{\\mathsf{{T}}}} \\Sigma_k^{{-1}} (x - \\mu_k)
    - \\frac{{1}}{{2}} \\log |\\Sigma_k| + \\log \\pi_k$$

  <p>展開之後會出現 $x^{{\\mathsf{{T}}}} \\Sigma_k^{{-1}} x$。<strong>因為 $\\Sigma_k$ 隨 k 不同，
  這一項在兩類相減時不會抵消</strong>，所以邊界是 x 的二次曲面——名字裡的「二次」就是這麼來的。</p>

{info("要不要共用 Σ，本質是偏差–變異取捨", '''<strong>參數量：</strong>LDA 只估一個 Σ，
  要 p(p+1)/2 個數；QDA 每類一個，要 K·p(p+1)/2 個。p = 50、K = 2 時是
  1275 對 <strong>2550</strong>。<br>
  <strong>所以：</strong>訓練資料少 → LDA（降變異優先）；訓練資料很多，
  或「共用共變異數」明顯站不住腳 → QDA。<br>
  ISLP 圖 4.9 兩張圖說得最白：左圖真實邊界是線性的，LDA 贏（QDA 白付了變異的代價）；
  右圖兩類的相關係數一個 +0.7 一個 −0.7，真實邊界是彎的，QDA 贏。''', "warm")}

{viz(svg("w04lda2Svg", 360),
     [rows_card("目前的設定",
                [("模式", "LDA（共用 Σ）", "w04lda2Mode"),
                 ("ρ₁（藍類）", "0.70", "w04lda2R1T"),
                 ("ρ₂（紅類）", "0.70", "w04lda2R2T"),
                 ("邊界的形狀", "—", "w04lda2Shape"),
                 ("訓練錯誤（60 點）", "—", "w04lda2Err")]),
      info_card("怎麼看這張圖",
                '兩個橢圓是各類含 95% 機率的等高線，點是各類 30 筆抽樣。'
                '<span style="color:var(--fit-line);font-weight:700;">紅線</span>是目前模式的決策邊界，'
                '<span style="color:var(--muted);font-weight:700;">灰虛線</span>永遠是 LDA 的線性邊界，'
                '留在那裡當對照。<strong>把 ρ₁ 與 ρ₂ 調成一樣，紅線會壓在灰線上</strong>——'
                '因為 Σ₁ = Σ₂ 時 QDA 退化成 LDA。', "圖 4.9"),
      info_card("為什麼 QDA 的邊界會是圓錐曲線",
                '$\\delta_1(x) - \\delta_2(x) = 0$ 是 x 的二次式，'
                '所以邊界是雙曲線、橢圓或拋物線之一（退化時是直線）。'
                '把 ρ₁ 與 ρ₂ 拉到正負兩端，你會看到邊界彎成兩支——'
                '<strong>那不是 bug，二次曲線本來就可以有兩支。</strong>')],
     "w04lda2Status", "切換共用／各自共變異數，看邊界從直線變成二次曲線。",
     slider("w04lda2R1", "ρ₁", -0.9, 0.9, 0.05, 0.7, "w04lda2Draw")
     + slider("w04lda2R2", "ρ₂", -0.9, 0.9, 0.05, 0.7, "w04lda2Draw")
     + slider("w04lda2D", "μ 位移", 0.6, 2.4, 0.1, 1.4, "w04lda2Draw")
     + '<button class="btn btn-toggle" onclick="w04lda2Toggle()">切換 LDA ↔ QDA</button>'
     + '<button class="btn btn-reset" onclick="w04lda2Reset()">重置</button>')}

  <h3>Naive Bayes：不猜分佈的形狀，改猜「互相獨立」</h3>

  <p>LDA 與 QDA 都在猜 $f_k(x)$ 的<strong>形狀</strong>（多變量常態）。
  Naive Bayes 換一個方向：形狀隨便你，但假設<strong>在每一類裡面，p 個預測變數互相獨立</strong>：</p>

  $$f_k(x) = f_{{k1}}(x_1) \\times f_{{k2}}(x_2) \\times \\cdots \\times f_{{kp}}(x_p)$$

  <p>這個假設幾乎一定是錯的——我們也知道它是錯的。但它把「估一個 p 維密度」這件難事
  換成「估 p 個一維密度」，<strong>用一點偏差換掉一大堆變異</strong>。
  p 大、n 小的時候這筆交易非常划算。</p>

{table(["", "對 f<sub>k</sub>(x) 的假設", "邊界形狀", "參數量（p 大時）", "什麼時候最強"],
       [["LDA", "多變量常態，Σ 共用", "線性", "少", "真實邊界線性、各類近常態、n 小"],
        ["QDA", "多變量常態，Σ<sub>k</sub> 各自", "二次", "多（K·p(p+1)/2）", "邊界明顯彎曲、n 大"],
        ["Naive Bayes", "類內獨立，一維密度任意", "加性（可彎，但沒有交互項）", "很少（K·2p）",
         "p 大 n 小、變數近似獨立"],
        ["邏輯斯迴歸", "不假設（直接建模後驗）", "線性", "少（(K−1)(p+1)）", "X 不常態、要做推論"],
        ["KNN", "完全不假設", "任意", "—（存全部資料）", "邊界極度彎曲、n ≫ p"]])}

  <h3 id="dx-qda">講義完整實作：QDA 與 Naive Bayes</h3>
{card("講義 04 · QuadraticDiscriminantAnalysis", _qda_code, lab_output(CH, 95),
      src=src("89、93、95"),
      note="<code>covariance_[0]</code>（儲存格 93）是<strong>第一類自己的</strong> Σ̂₁ = "
           "<code>[[1.5066, -0.0392], [-0.0392, 1.5356]]</code>——QDA 每類一個，這是它跟 LDA 的分水嶺。"
           "QDA 的測試正確率 <strong>0.5992</strong>（儲存格 97／98），"
           "比 LDA 的 0.560 高。lab 儲存格 99 提醒：股市資料上多出這幾個百分點，"
           "先在更大的測試集上驗證再說。")}

{card("講義 04 · GaussianNB", _nb_code, lab_output(CH, 116),
      src=src("102、110、116、117"),
      note="<code>theta_</code>（儲存格 108）跟 <code>lda.means_</code> 一模一樣——"
           "平均數的估法沒差。差別在 <code>var_</code>：Naive Bayes 每類每變數各估一個變異數、"
           "而且<strong>沒有共變異數</strong>（等於把 Σ<sub>k</sub> 限制成對角矩陣）。"
           "正確率 <strong>0.5952</strong>（儲存格 117），比 QDA 的 0.5992 差一點、比 LDA 的 0.560 好。")}

{quiz("qQda", "QUIZ · 該用 LDA 還是 QDA",
      "只有 n = 40 筆訓練資料、p = 2，而且你有理由相信真實的決策邊界是線性的。該選哪個？",
      [(True, "LDA。真實邊界既然是線性的，QDA 多出來的彈性只會帶來變異、換不到偏差的減少",
        "對。這正是 ISLP 圖 4.9 左圖與習題 4.8 第 5 題 (d) 的答案："
        "邊界是線性時 QDA 雖然「配得下」線性邊界，但它要估兩個 Σ，n = 40 根本不夠，"
        "測試誤差反而會變差。"),
       (False, "QDA。它比較有彈性，線性邊界是二次邊界的特例，所以不會更差",
        "「線性是二次的特例」這句話沒錯，但「所以不會更差」錯了。<strong>模型空間包含真解 ≠ 估得準</strong>——"
        "QDA 要多估 p(p+1)/2 = 3 個參數，n = 40 時這些估計很不穩，變異吃掉一切。"),
       (False, "兩個一樣，因為 p = 2 時共變異數矩陣只有 3 個參數，差別可以忽略",
        "不對。就算只多 3 個參數，在 n = 40 的資料上仍然是可觀的變異，"
        "而且 QDA 的邊界形狀本身就比較不穩（會彎）。ISLP 的模擬顯示這個差距看得出來。")])}
"""

# ── P05 threshold / confusion matrix / ROC ────────────────────────────
_thr_code1 = lab_code(CH, 57) + "\n\n" + lab_code(CH, 58)
_thr_code2 = lab_code(CH, 156) + "\n\n" + lab_code(CH, 158) + "\n\n" + lab_code(CH, 159)

_CM = ('<div style="overflow-x:auto;">\n'
       '      <table class="cm-table" style="margin:.4rem auto;">\n'
       '        <thead><tr><th></th><th>真實：不違約</th><th>真實：違約</th><th>合計</th></tr></thead>\n'
       '        <tbody>\n'
       '          <tr><th>預測：不違約</th>'
       '<td class="cm-tn" id="w04thrTN">9644</td>'
       '<td class="cm-fn" id="w04thrFN">252</td>'
       '<td id="w04thrRN">9896</td></tr>\n'
       '          <tr><th>預測：違約</th>'
       '<td class="cm-fp" id="w04thrFP">23</td>'
       '<td class="cm-tp" id="w04thrTP">81</td>'
       '<td id="w04thrRP">104</td></tr>\n'
       '          <tr><th>合計</th><td>9667</td><td>333</td><td>10000</td></tr>\n'
       '        </tbody>\n'
       '      </table>\n'
       '      <p class="cm-note" style="text-align:center;">'
       '綠底＝猜對（TN／TP）·　淺紅＝假陽 FP（誤報）·　深紅＝<strong>假陰 FN（漏掉的違約戶）</strong>'
       '</p>\n'
       '      </div>')

BODIES["threshold"] = f"""
  <p>前面所有方法的最後一步都是同一句話：「後驗機率大於 <strong>0.5</strong> 就判成正類」。
  這個 0.5 不是天上掉下來的，它來自 Bayes 分類器——<strong>而 Bayes 分類器最小化的是「總」錯誤率</strong>，
  它完全不管兩種錯誤誰比較痛。</p>

  <p>ISLP 的 <code>Default</code> 例子把這件事講得很殘忍。LDA 在 10000 筆訓練資料上的錯誤率是
  <strong>2.75%</strong>，聽起來很棒。但是：</p>

  <ul>
    <li>資料裡只有 3.33% 的人違約，所以<strong>「一律預測不會違約」這個什麼都沒學的分類器，
    錯誤率是 3.33%</strong>。2.75% 只比它好一點點。</li>
    <li>333 個真的違約的人裡面，LDA <strong>漏掉了 252 個</strong>（75.7%）。
    對信用卡公司來說，這叫做完全失效。</li>
  </ul>

{info("兩種錯誤有名字，而且權重通常不一樣", '''把「違約 / 有病 / 是垃圾信」當成正類（+）：<br>
  <strong>FP（假陽性）</strong>＝其實沒事，被你判成有事。<br>
  <strong>FN（假陰性）</strong>＝其實有事，被你放過。<br>
  <strong>靈敏度</strong>（sensitivity, recall）= TP/(TP+FN)＝真的有事的人裡你抓到幾成。<br>
  <strong>特異度</strong>（specificity）= TN/(TN+FP)＝真的沒事的人裡你放對幾成。<br>
  <strong>精確率</strong>（precision）= TP/(TP+FP)＝你喊「有事」的人裡真的有事的比例。''', "warm")}

  <p>閾值就是調節這兩種錯誤的旋鈕。把 0.5 降到 0.2：</p>

  $$\\Pr(\\texttt{{default}} = \\text{{Yes}} \\mid X = x) > 0.2
    \\;\\Longrightarrow\\; \\text{{判為違約}}$$

  <p>ISLP 表 4.5 的結果是：漏掉的違約戶從 252 掉到 <strong>138</strong>（靈敏度從 24.3% 升到 58.6%），
  代價是誤報從 23 升到 <strong>235</strong>，總錯誤率從 2.75% 微升到 3.73%。
  <strong>對信用卡公司，這是划算的交易。</strong>自己動一下滑桿看看：</p>

{viz(_CM + "\n" + chart("w04thrRoc", "square",
                        "。此圖的重點：LDA 在 Default 上的 ROC 曲線緊貼左上角，AUC = 0.95；"
                        "把閾值從 0.5 調到 0.2，工作點沿曲線往右上移動——靈敏度換來假陽率。"),
     [rows_card("目前的閾值下",
                [("閾值", "0.500", "w04thrT"),
                 ("預測會違約的人數", "104", "w04thrNP"),
                 ("靈敏度（抓到幾成違約戶）", "24.3%", "w04thrSens"),
                 ("特異度", "99.8%", "w04thrSpec"),
                 ("精確率", "77.9%", "w04thrPrec"),
                 ("總錯誤率", "2.75%", "w04thrErr")]),
      info_card("三個一定要記住的數字",
                '<strong>閾值 0.5：</strong>錯誤率 2.75%，但漏掉 252 / 333 = 75.7% 的違約戶。<br>'
                '<strong>閾值 0.2：</strong>錯誤率 3.73%，只漏掉 138 個（41.4%）。<br>'
                '<strong>一律猜不違約：</strong>錯誤率 3.33%，漏掉全部 333 個。<br>'
                '這三行完整說明了「準確率不是唯一指標」。', "表 4.4／4.5"),
      info_card("ROC 與 AUC",
                'ROC 曲線把<strong>所有</strong>閾值的（假陽率、真陽率）畫成一條線，'
                '所以它描述的是分類器本身，不是某一個閾值。'
                '<strong>AUC = 0.95</strong>（ISLP §4.4.2）；隨機猜是 0.5，完美是 1。'
                '紅點是你現在選的閾值在曲線上的位置。')],
     "w04thrStatus", "拖動閾值：混淆矩陣、四個指標與 ROC 上的紅點會同步重算。",
     slider("w04thrSlider", "閾值", 0, 1, 0.005, 0.5, "w04thrMove")
     + '<button class="btn btn-step" onclick="w04thrSet(0.5)">→ 回到 0.5</button>'
     + '<button class="btn btn-step" onclick="w04thrSet(0.2)">→ 調到 0.2</button>'
     + '<button class="btn btn-reset" onclick="w04thrReset()">重置</button>')}

{qa("觀念釐清", [
    ("Q：類別不平衡時，「準確率 99%」為什麼可能一文不值？該看什麼？",
     "<p>因為<strong>準確率的分母被多數類綁死了</strong>。假設 1000 個人裡有 10 個得病，"
     "你寫一支 <code>return '沒病'</code> 的程式，準確率就是 99%——它一個病人都沒抓到。</p>"
     "<p>這個「什麼都不做」的基準線有名字，叫 <strong>虛無率</strong>（null rate）。"
     "ISLP 用 <code>Default</code> 示範：虛無率 3.33%，LDA 的 2.75% 只是小勝。"
     "lab 的 <code>Caravan</code> 例子更誇張——只有 6% 的人買保險，"
     "KNN 的錯誤率 11.1% 比「全猜不買」的 6.7% <strong>還差</strong>（儲存格 145）。</p>"
     "<p>該看什麼？先問「哪一種錯誤比較貴」，再挑指標：</p>"
     "<ul><li><strong>怕漏掉正類</strong>（癌症篩檢、詐欺偵測）：看<strong>靈敏度／recall</strong>，"
     "並且把閾值往下調。</li>"
     "<li><strong>怕誤報</strong>（垃圾信過濾、發送行銷成本）：看<strong>精確率</strong>，閾值往上調。</li>"
     "<li><strong>要一個不挑閾值的總結</strong>：看 <strong>AUC</strong>，"
     "或在極不平衡時看 PR 曲線下面積。</li>"
     "<li><strong>兩邊都要顧</strong>：F1（精確率與 recall 的調和平均），或平衡準確率。</li></ul>"
     "<p>最後一句：<strong>永遠把虛無率一起報出來</strong>。沒有基準線的準確率是沒有資訊的數字。</p>"),
    ("Q：TP / FP / FN / TN 跟那三個比率的關係是什麼？為什麼醫學篩檢跟垃圾信過濾在意的方向剛好相反？",
     "<p>先把四格與三個比率的<strong>分母</strong>釘死，這是最容易搞混的地方：</p>"
     "<ul><li><strong>靈敏度</strong> = TP/(TP+FN)：分母是<strong>真實</strong>的正類總數（縱向看）。</li>"
     "<li><strong>特異度</strong> = TN/(TN+FP)：分母是<strong>真實</strong>的負類總數（縱向看）。</li>"
     "<li><strong>精確率</strong> = TP/(TP+FP)：分母是<strong>你預測</strong>為正的總數（橫向看）。</li></ul>"
     "<p>ISLP 表 4.7 還給了對照的別名：假陽率就是型一錯誤、真陽率就是檢定力（power）、"
     "精確率就是正預測值（PPV）。同一個表格，不同學科各叫一套名字。</p>"
     "<p><strong>方向相反是因為兩種錯誤的成本結構不同。</strong></p>"
     "<ul><li><strong>癌症篩檢</strong>：漏掉一個病人（FN）可能致命；誤報（FP）的代價是再做一次檢查。"
     "所以把閾值調低、犧牲特異度換<strong>高靈敏度</strong>。篩檢工具本來就設計成「寧可多抓」。</li>"
     "<li><strong>垃圾信過濾</strong>：把重要信件丟進垃圾桶（FP，如果正類＝垃圾信）代價很高；"
     "漏掉一封垃圾信只是煩。所以閾值調高、追求<strong>高精確率</strong>。</li></ul>"
     "<p>lab 的 <code>Caravan</code> 是第三種情況：業務員拜訪一個人有成本，"
     "所以在意的是「被我挑中的人裡有幾成真的會買」——那是<strong>精確率</strong>。"
     "把閾值從 0.5 降到 0.25，挑出 29 個人、9 個真的買，精確率 31%，"
     "是隨機猜（6%）的五倍（儲存格 158、159）。</p>"),
])}

  <h3 id="dx-thr">講義完整實作：從混淆矩陣算出四個指標</h3>
{card("講義 04 · 手動算 accuracy / sensitivity / precision / FPR", _thr_code1,
      lab_output(CH, 58), src=src("57、58"),
      note="注意 <code>confusion_matrix(真實, 預測)</code> 與 ISLP 的 "
           "<code>confusion_table(預測, 真實)</code> <strong>參數順序相反、矩陣也是轉置的</strong>。"
           "看到別人的混淆矩陣第一件事就是確認哪一軸是真實值，否則靈敏度與精確率會對調。"
           "這裡靈敏度 0.752 很高，但假陽率也高達 0.685——模型幾乎什麼都猜 Up。")}

{card("講義 04 · Caravan：把閾值從 0.5 降到 0.25", _thr_code2,
      lab_output(CH, 158), src=src("156、158、159"),
      note="閾值 0.5 時只有 2 個人被預測會買保險，而且<strong>兩個都猜錯</strong>"
           "（儲存格 156 的輸出是 931／67／2／0）——模型等於沒有產出。"
           "降到 0.25 之後挑出 29 個人、其中 9 個真的買了，"
           "精確率 <strong>9/(20+9) = 31.0%</strong>（儲存格 159），是隨機猜 6% 的五倍。"
           "<strong>同一個模型、同一組係數，只換了一個閾值。</strong>")}

{quiz("qThr", "QUIZ · 閾值",
      "把分類閾值從 0.5 降到 0.2，下面哪一組變化一定會發生？",
      [(True, "靈敏度上升（或持平）、特異度下降（或持平）；總錯誤率不保證變好",
        "對。閾值降低 → 更多人被判為正類 → TP 與 FP 都只會增加、FN 與 TN 都只會減少。"
        "所以靈敏度單調上升、特異度單調下降。總錯誤率則不一定："
        "Default 的例子從 2.75% 升到 3.73%（變差），但這是為了換靈敏度而刻意付的代價。"),
       (False, "靈敏度與精確率都上升，因為抓到的正類變多了",
        "靈敏度確實上升，但<strong>精確率通常會下降</strong>。精確率的分母是「你預測為正的人數」，"
        "閾值放寬後這個分母漲得比 TP 快。Default 的例子：精確率從 81/104 = 77.9% 掉到 195/430 = 45.3%。"),
       (False, "總錯誤率一定下降，因為模型抓到更多真正的正類",
        "不對，方向反了。0.5 這個閾值<strong>就是</strong>讓總錯誤率最小的那個（Bayes 分類器的性質），"
        "所以離開 0.5 通常會讓總錯誤率變差。我們願意付這個代價，是因為兩種錯誤的成本不一樣。")])}

{table(["名稱", "定義", "別名", "分母是誰"],
       [["假陽率 FPR", "FP / N", "型一錯誤、1 − 特異度", "真實的負類"],
        ["真陽率 TPR", "TP / P", "靈敏度、recall、檢定力、1 − 型二錯誤", "真實的正類"],
        ["正預測值 PPV", "TP / P*", "精確率、1 − 錯誤發現比例", "預測為正的"],
        ["負預測值 NPV", "TN / N*", "—", "預測為負的"]])}
  <p style="font-size:.82rem;color:var(--muted);">對照 ISLP 表 4.6／4.7。
  N、P 是真實的負／正類總數；N*、P* 是被預測為負／正的總數。</p>
"""

# ── P06 compare ───────────────────────────────────────────────────────
_SCEN = ('<div id="w04pickStage" style="background:#fafafa;border:1px solid #ececec;'
         'border-radius:8px;padding:1rem 1.1rem;min-height:190px;">\n'
         '        <div class="dx-label" id="w04pickNo">情境 1 / 6</div>\n'
         '        <p id="w04pickQ" style="margin-bottom:.6rem;">—</p>\n'
         '        <p id="w04pickFb" style="margin-bottom:0;font-size:.92rem;color:var(--muted);">'
         '按下面任一個方法看看拆解。</p>\n'
         '      </div>')

BODIES["compare"] = f"""
  <p>五個方法看起來各說各話，其實把它們統一寫成「相對於第 K 類的 log-odds」之後，
  差別就一目了然了。ISLP §4.5.1 做的就是這件事：</p>

  $$\\text{{LDA：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} b_{{kj}} x_j$$

  $$\\text{{QDA：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} b_{{kj}} x_j + \\sum_{{j=1}}^{{p}}\\sum_{{l=1}}^{{p}} c_{{kjl}} x_j x_l$$

  $$\\text{{Naive Bayes：}}\\;\\log\\!\\left(\\frac{{\\Pr(Y = k \\mid x)}}{{\\Pr(Y = K \\mid x)}}\\right)
    = a_k + \\sum_{{j=1}}^{{p}} g_{{kj}}(x_j)$$

  <p>三行擺在一起，四個結論就掉出來了：</p>

{info("四個等價關係（ISLP §4.5.1）", '''<strong>1. LDA 是 QDA 的特例</strong>（所有 c<sub>kjl</sub> = 0）。
  不意外，LDA 就是加了 Σ₁ = ⋯ = Σ<sub>K</sub> 的 QDA。<br>
  <strong>2. 任何線性邊界的分類器都是 Naive Bayes 的特例</strong>（取 g<sub>kj</sub>(x<sub>j</sub>) = b<sub>kj</sub>x<sub>j</sub>）。
  所以 <strong>LDA 是 Naive Bayes 的特例</strong>——這件事從兩者的假設完全看不出來。<br>
  <strong>3. 用常態密度的 Naive Bayes 是「Σ 被限制成對角矩陣」的 LDA。</strong><br>
  <strong>4. QDA 與 Naive Bayes 誰都不是誰的特例。</strong>Naive Bayes 的 g<sub>kj</sub> 可以是任意函數（更彈性），
  但它是純加性的、<strong>永遠沒有 x<sub>j</sub>x<sub>l</sub> 交互項</strong>；QDA 有交互項但被鎖在二次式裡。''')}

  <p>邏輯斯迴歸呢？多元邏輯斯迴歸的形式跟 LDA 的第一行<strong>字面上完全一樣</strong>。
  差別只在係數怎麼來：LDA 從常態假設推出來，邏輯斯迴歸直接最大化條件似然。
  所以「X 近似常態 → LDA 較好，否則 → 邏輯斯較好」。</p>

  <p>KNN 是唯一完全在框架外的：它不寫任何 log-odds 的式子，直接看鄰居投票。
  代價是（a）需要 n ≫ p，（b）不告訴你哪個變數重要。</p>

{viz(chart("w04rocChart", "square",
           "。此圖的重點：在 Default 上，邏輯斯／LDA／QDA 的 ROC 幾乎完全重疊（AUC 0.9495–0.9496），"
           "Naive Bayes 略低（0.9447）——理論上的等價關係在實測上真的看得到。"),
     [rows_card("AUC（Default，balance + student）",
                [("邏輯斯迴歸", "—", "w04rocA1"), ("LDA", "—", "w04rocA2"),
                 ("QDA", "—", "w04rocA3"), ("Naive Bayes", "—", "w04rocA4"),
                 ("隨機猜", "0.5000", "w04rocA0")]),
      info_card("為什麼四條幾乎疊在一起",
                '因為這份資料只有兩個預測變數、n = 10000，'
                '而 <code>balance</code> 對 <code>default</code> 的訊號非常強。'
                '<strong>訊號夠強時，模型假設的差別就淹沒在訊號裡</strong>。'
                '式 4.32 又保證 LDA 與邏輯斯的邊界形式相同，兩條當然重疊。', "圖 4.8"),
      info_card("不要因此結論「方法都差不多」",
                'ISLP 圖 4.11／4.12 用六個模擬情境示範：換掉資料的產生方式，'
                '排名就會重排。<strong>「哪個方法好」是資料的性質，不是方法的性質。</strong>'
                '按「放大左上角」看四條線在高靈敏度區真正分開的地方。')],
     "w04rocStatus", "四個方法在同一份 Default 資料、同一組預測變數上的 ROC 疊圖。",
     '<button class="btn btn-toggle" onclick="w04rocZoom(true)">放大左上角</button>'
     '<button class="btn btn-reset" onclick="w04rocZoom(false)">看整張 0–1</button>')}

  <h3>選方法的六個情境</h3>
  <p>下面六個情境改寫自 ISLP §4.5.2 的模擬與 lab 的實際資料。
  先自己想再點——每個選項都會告訴你它為什麼合理、又為什麼不是最好的答案。</p>

{viz(_SCEN,
     [rows_card("進度",
                [("目前情境", "1 / 6", "w04pickIdx"),
                 ("答對", "0", "w04pickHit"),
                 ("已作答", "0 / 6", "w04pickDone")]),
      info_card("這一組要練的判斷",
                '<strong>1. 邊界是直的還是彎的？</strong>直的 → LDA／邏輯斯；彎的 → QDA／Naive Bayes／KNN。<br>'
                '<strong>2. n 相對 p 夠不夠大？</strong>不夠 → 選參數少的。<br>'
                '<strong>3. 各類內的 X 像不像常態？</strong>不像 → 邏輯斯或 Naive Bayes。<br>'
                '<strong>4. 變數之間獨立嗎？</strong>近似獨立 → Naive Bayes 大賺；明顯相關 → 它會很慘。'),
      info_card("沒有萬用解",
                'ISLP §4.5.2 的結論：<strong>六個情境沒有任何一個方法全勝。</strong>'
                '這也是第 5 章交叉驗證存在的理由——與其猜哪個方法適合，不如量出來。')],
     "w04pickStatus", "讀完情境後點一個方法，右邊會記你答對幾題。",
     '<button class="btn btn-toggle" onclick="w04pickAns(0)">邏輯斯</button>'
     '<button class="btn btn-toggle" onclick="w04pickAns(1)">LDA</button>'
     '<button class="btn btn-toggle" onclick="w04pickAns(2)">QDA</button>'
     '<button class="btn btn-toggle" onclick="w04pickAns(3)">Naive Bayes</button>'
     '<button class="btn btn-toggle" onclick="w04pickAns(4)">KNN</button>'
     '<button class="btn btn-step" onclick="w04pickNext()">→ 下一個情境</button>'
     '<button class="btn btn-reset" onclick="w04pickReset()">重置</button>')}

  <h3 id="dx-knn">講義完整實作：KNN，唯一的無母數方法</h3>
{card("講義 04 · KNeighborsClassifier(n_neighbors=1)",
      lab_code(CH, 122) + "\n\n" + lab_code(CH, 124), lab_output(CH, 122),
      src=src("122、124"),
      note="K = 1 的測試正確率剛好 <strong>0.500</strong>（儲存格 124）——完全等於丟硬幣。"
           "K = 3 升到 0.532（儲存格 127），再加大也沒再改善。"
           "lab 儲存格 129 的結論：在 <code>Smarket</code> 上 QDA 最好。"
           "K = 1 太彈性，在 n 只有約 1000、訊號又極弱的資料上是純粹的變異。")}

{table(["ISLP 情境（§4.5.2）", "資料怎麼產生", "誰贏", "為什麼"],
       [["情境 1", "各類內兩變數不相關的常態，每類 20 筆", "LDA、邏輯斯",
         "邊界真的是線性的，KNN 白付變異"],
        ["情境 2", "同上，但類內相關 −0.5", "LDA、邏輯斯",
         "<strong>Naive Bayes 崩掉</strong>——獨立假設被違反"],
        ["情境 3", "類內強負相關的 t 分佈，每類 50 筆", "邏輯斯",
         "邊界仍線性但不常態，LDA／QDA 吃虧"],
        ["情境 4", "兩類相關係數 +0.5 與 −0.5 的常態", "QDA",
         "真實邊界二次，正好是 QDA 的假設"],
        ["情境 5", "不相關常態，反應由複雜非線性函數生成", "KNN-CV",
         "邊界很彎；<strong>KNN-1 最差</strong>——平滑度沒選對"],
        ["情境 6", "各類對角但不同的 Σ，每類只有 6 筆", "Naive Bayes",
         "假設正好成立，而 n 太小連 QDA 都撐不住"]])}

{quiz("qCmp", "QUIZ · 解析比較",
      "ISLP §4.5.1 說「LDA 是 Naive Bayes 的特例」。這句話怎麼可能成立？"
      "LDA 明明允許變數相關、Naive Bayes 明明假設獨立。",
      [(True, "因為兩者的 log-odds 都能寫成 a_k + Σ_j g_kj(x_j)；LDA 對應 g_kj 取線性函數的情況",
        "對。關鍵是<strong>比較「模型能表達的函數族」而不是比較「假設的措辭」</strong>。"
        "Naive Bayes 的 g<sub>kj</sub> 可以是任意一維函數，取成 b<sub>kj</sub>x<sub>j</sub> 就退化成線性邊界，"
        "而 LDA 的邊界正好是線性的。所以任何線性邊界的分類器都落在 Naive Bayes 的表達範圍內。"),
       (False, "因為當 Σ 是對角矩陣時，LDA 的變數就真的獨立了，兩者於是相同",
        "這句話講的是<strong>另一個</strong>結論（常態版 Naive Bayes = 對角 Σ 的 LDA），"
        "而且方向反了。「LDA 是 Naive Bayes 的特例」對<strong>任意</strong> Σ 都成立，不必是對角的——"
        "因為決定的是邊界的函數形式，不是相關結構。"),
       (False, "這句話只在 p = 1 時成立，p ≥ 2 時兩者沒有包含關係",
        "不對。p = 1 時獨立假設是空的、結論太廉價；ISLP 那條結論對一般 p 都成立。"
        "反而是「QDA 與 Naive Bayes 誰都不是誰的特例」這一條，才是真的沒有包含關係。")])}
"""

# ── P07 Poisson / GLM ─────────────────────────────────────────────────
BODIES["poisson"] = f"""
  <p class="skip-note">這一節是課堂沒細講的延伸（講義 04 · p.49–56 對應 ISLP §4.6）。
  它把「線性迴歸／邏輯斯迴歸」收進 GLM 這個大框架裡，觀念很漂亮但不影響前面各節的理解，
  第一輪可以先跳過，之後回來看。</p>

  <p>前面兩種 y：連續的（第 3 章）與類別的（本章）。還有第三種常見的 y——<strong>計數</strong>。
  ISLP 用 <code>Bikeshare</code>（華盛頓特區每小時的單車租借數，n = 8645）示範。</p>

  <p>直接對計數配線性迴歸會踩三個坑：</p>

  <ul>
    <li><strong>會預測出負數。</strong>ISLP 說 <code>Bikeshare</code> 上有 <strong>9.6%</strong>
    的配適值是負的——負的租借數沒有意義。</li>
    <li><strong>變異數不是常數。</strong>清晨下雨的時段平均 5.05 人、標準差 3.73；
    春天早上晴天的時段平均 243.59 人、標準差 131.7。<strong>平均大變異也大</strong>，
    這直接違反線性模型的同質變異假設。</li>
    <li><strong>y 是整數。</strong>線性模型的誤差是連續的，所以 y 必然被當成連續量。</li>
  </ul>

  <p>Poisson 分佈天生就長成計數的樣子：</p>

  $$\\Pr(Y = k) = \\frac{{e^{{-\\lambda}} \\lambda^k}}{{k!}}, \\qquad k = 0, 1, 2, \\ldots
    \\qquad\\text{{而且}}\\quad \\mathbb{{E}}(Y) = \\mathrm{{Var}}(Y) = \\lambda$$

  <p><strong>Poisson 迴歸</strong>讓 λ 隨預測變數而變，而且是對 <strong>log λ</strong> 配線性式：</p>

  $$\\log \\lambda(X_1, \\ldots, X_p) = \\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p
    \\qquad\\Longleftrightarrow\\qquad
    \\lambda = e^{{\\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p}}$$

  <p>取 log 有兩個好處：λ 永遠是正的（不會再預測出負的租借數），
  而且「E(Y) = Var(Y) = λ」自動把平均–變異關係包進模型。</p>

{info("係數要用乘法解讀", '''因為線性的是 log λ，所以 X<sub>j</sub> 增加一單位讓
  <strong>λ 乘上 e^βⱼ</strong>，不是加上 βⱼ。<br>
  ISLP 表 4.11 的例子：<code>weathersit[cloudy/misty]</code> 的係數是 −0.08，
  e<sup>−0.08</sup> = 0.923——<strong>陰天的平均租借量只有晴天的 92.3%</strong>。<br>
  這跟邏輯斯迴歸的「勝算乘上 e^β」是同一個模式：<strong>連結函數取了 log，解讀就從加法變乘法。</strong>''')}

  <h3>GLM：把三個模型收進同一個框架</h3>

  <p>線性迴歸、邏輯斯迴歸、Poisson 迴歸做的事其實一樣：
  假設 y 屬於某個分佈族，然後用<strong>連結函數</strong>（link function）η 把 y 的期望值
  轉換成預測變數的線性組合：</p>

  $$\\eta\\big(\\mathbb{{E}}(Y \\mid X_1, \\ldots, X_p)\\big)
    = \\beta_0 + \\beta_1 X_1 + \\cdots + \\beta_p X_p$$

{table(["", "假設 y 的分佈", "連結函數 η(μ)", "μ 的範圍", "statsmodels 的 family"],
       [["線性迴歸", "常態（Gaussian）", "μ（恆等）", "整個實數線", "<code>sm.families.Gaussian()</code>"],
        ["邏輯斯迴歸", "Bernoulli", "log(μ / (1 − μ))（logit）", "(0, 1)",
         "<code>sm.families.Binomial()</code>"],
        ["Poisson 迴歸", "Poisson", "log μ", "(0, ∞)", "<code>sm.families.Poisson()</code>"],
        ["Gamma 迴歸", "Gamma", "通常是 −1/μ 或 log μ", "(0, ∞)",
         "<code>sm.families.Gamma()</code>"]])}

  <p>常態、Bernoulli、Poisson、Gamma、負二項都屬於<strong>指數族</strong>（exponential family）。
  任何「挑一個指數族成員 + 挑一個連結函數」的迴歸都叫 GLM。
  所以 lab 裡從頭到尾只用了一支 <code>sm.GLM()</code>——換 <code>family</code> 就換模型。</p>

  <h3 id="dx-poi">講義完整實作：一支 <code>sm.GLM()</code> 打三種模型</h3>
{card("講義 04 · Poisson 迴歸（Bikeshare）",
      lab_code(CH, 188) + "\n\n" + lab_code(CH, 190), None, src=src("188、190"),
      note="跟前面配邏輯斯迴歸的那一行比一比："
           "<code>family=sm.families.Binomial()</code> 換成 "
           "<code>family=sm.families.Poisson()</code>，其他一個字都沒改。"
           "係數的補齊步驟（<code>mnth[Dec]</code> 取其餘月份的負和）是因為用了 "
           "<code>contrast('mnth', 'sum')</code> 這種和為零的編碼，"
           "係數要讀成「相對於年平均」。對照 ISLP 表 4.11 與圖 4.15。"
           "這一格 lab 沒有存下輸出，數字請看課本表 4.11：intercept 4.12、temp 0.79、"
           "weathersit[light rain/snow] −0.58。")}

{info("Poisson 迴歸的一個坑：過度分散", '''Poisson 模型硬性要求 Var(Y) = E(Y)。
  真實資料常常變異遠大於平均，這叫<strong>過度分散</strong>（overdispersion）。
  ISLP 的腳註坦承 <code>Bikeshare</code> 就有這個問題，
  <strong>導致表 4.11 的 z 值被高估</strong>（看起來比實際更顯著）。<br>
  補救方式是 quasi-Poisson 或負二項迴歸——超出本章範圍，但知道有這個坑很重要：
  <strong>係數還可信，標準誤與 p 值不可信。</strong>''', "warm")}

{quiz("qPoi", "QUIZ · Poisson 迴歸",
      "Poisson 迴歸配的是 log λ 而不是 λ 本身。最主要的理由是什麼？",
      [(True, "取 log 之後 λ = e^(線性式) 永遠是正的，計數的平均值不會被預測成負數",
        "對。這正是線性迴歸在 <code>Bikeshare</code> 上 9.6% 配適值變成負數的病根。"
        "順帶的好處是係數變成乘法解讀（λ 乘上 e^βⱼ），跟邏輯斯迴歸的勝算比同一個模式。"),
       (False, "因為 log 轉換會讓計數資料變成常態分佈，這樣才能用最小平方法",
        "不對。Poisson 迴歸<strong>不做</strong>「把 y 取 log 再配線性模型」這件事——"
        "那是另一種做法（而且 y = 0 時就爆了）。這裡取 log 的對象是<strong>平均值 λ</strong>，"
        "不是 y；估計用的是最大似然，不是最小平方。"),
       (False, "因為 log 是唯一能讓 Poisson 迴歸有封閉解的連結函數",
        "不對。Poisson 迴歸<strong>沒有</strong>封閉解，跟邏輯斯迴歸一樣要迭代。"
        "log 之所以是預設（正規連結），是因為它讓 μ 落在 (0, ∞) 又讓數學最漂亮，不是因為有封閉解。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 4.8 第 6 題（a）",
      "某邏輯斯迴歸用 X₁ = 讀書時數、X₂ = 大學 GPA 預測「這科拿 A」，"
      "估到 β̂₀ = −6、β̂₁ = 0.05、β̂₂ = 1。一個讀 40 小時、GPA 3.5 的學生拿到 A 的機率是多少？",
      [(True, "約 0.378",
        "對。先算線性部分：$-6 + 0.05 \\times 40 + 1 \\times 3.5 = -0.5$，"
        "再代進邏輯斯函數 $p = e^{-0.5}/(1+e^{-0.5}) = 0.3775$。"
        "第 (b) 小題問「要讀幾小時才有 50% 機會」——p = 0.5 等於 log-odds = 0，"
        "解 $-6 + 0.05x + 3.5 = 0$ 得 x = <strong>50 小時</strong>。"),
       (False, "約 −0.5",
        "−0.5 是 <strong>log-odds</strong>，不是機率。機率不可能是負的。"
        "這一題就是在測「線性的是 log-odds、不是機率」——算完線性部分還要過一次邏輯斯函數。"),
       (False, "約 0.622",
        "這是 1 − 0.378，也就是「拿不到 A」的機率。方向弄反了："
        "邏輯斯函數 $e^{\\eta}/(1+e^{\\eta})$ 在 η 為負時一定小於 0.5。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 4.8 第 9 題",
      "這一題只考勝算。（a）違約勝算是 0.37 的人，實際違約的比例是多少？"
      "（b）某人違約機率 16%，她的勝算是多少？",
      [(True, "(a) 約 0.27　(b) 約 0.19",
        "對。勝算 = p/(1−p)，所以 p = odds/(1+odds) = 0.37/1.37 = <strong>0.270</strong>；"
        "反過來 odds = 0.16/0.84 = <strong>0.190</strong>。"
        "順手記一個直覺：p 很小的時候 odds ≈ p，兩者差不多；p 接近 1 時 odds 會衝向無限大。"),
       (False, "(a) 0.37　(b) 0.16",
        "這是把勝算跟機率當成同一件事。它們只在 p 很小的時候近似相等；"
        "0.37 的勝算對應的機率是 0.27，差了 0.1，不能混用。"),
       (False, "(a) 約 0.63　(b) 約 5.25",
        "兩個都取到補集或倒數了。(a) 0.63 是 1 − 0.37；(b) 5.25 = 0.84/0.16 是"
        "「不違約」的勝算。題目問的是違約，分子要放 p。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 4.8 第 8 題",
      "同一份資料切成一半訓練一半測試。邏輯斯迴歸的訓練錯誤率 20%、測試錯誤率 30%；"
      "1-NN 的「訓練與測試平均」錯誤率是 18%。該選哪一個？",
      [(True, "邏輯斯迴歸。1-NN 的訓練錯誤率是 0，所以它的測試錯誤率約 36%，比 30% 差",
        "對，這一題的陷阱就在「平均」。K = 1 時每個訓練點的最近鄰居就是它自己，"
        "訓練錯誤率必定為 0。所以 (0 + 測試) / 2 = 18% ⟹ 測試錯誤率 = <strong>36%</strong>。"
        "36% &gt; 30%，選邏輯斯迴歸。"),
       (False, "1-NN。它的平均錯誤率 18% 比邏輯斯的兩個數字都低",
        "這是直接拿平均值跟測試錯誤率比。<strong>訓練與測試錯誤率不能混在一起平均之後再比較</strong>——"
        "訓練誤差是被最佳化過的，本來就偏低，1-NN 的訓練誤差甚至是 0。要比就只比測試誤差。"),
       (False, "資訊不足，因為題目沒有分別給 1-NN 的訓練與測試錯誤率",
        "資訊其實夠。關鍵是「K = 1 的訓練錯誤率必定為 0」這個結構性事實——"
        "知道它就能從平均值反推測試錯誤率。這也是課本要考的點。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 4.8 第 5 題（a）（d）",
      "（a）Bayes 決策邊界是<strong>線性</strong>時，LDA 與 QDA 誰在訓練集上比較好？測試集呢？"
      "（d）「就算邊界是線性的，QDA 彈性夠大也配得下，所以測試誤差還是會比較好」——對嗎？",
      [(True, "訓練集 QDA 通常較好，測試集 LDA 較好；(d) 是錯的",
        "對。QDA 比較有彈性，所以<strong>訓練</strong>誤差通常較低（甚至一定不會更高）。"
        "但邊界既然是線性的，多出來的彈性只帶來變異、換不到偏差的減少，"
        "所以<strong>測試</strong>誤差 LDA 較好。(d) 的錯誤在於把「模型空間包含真解」"
        "當成「估得準」——這是偏差–變異取捨的核心誤解。"
        "附帶第 (c) 小題：n 變大時 QDA 相對 LDA 會<strong>改善</strong>，因為變異的代價被 n 稀釋掉了。"),
       (False, "兩個集合都是 LDA 較好，因為真實邊界是線性的",
        "測試集對，訓練集錯。<strong>訓練誤差幾乎總是站在比較彈性的模型那一邊</strong>——"
        "這正是訓練誤差不能用來選模型的原因。分辨「訓練」與「測試」是這一題的全部重點。"),
       (False, "兩個集合都是 QDA 較好，因為線性邊界是二次邊界的特例",
        "訓練集對，測試集錯，而且理由正是課本第 (d) 小題要打掉的迷思。"
        "「特例」保證的是<strong>偏差</strong>不會更差，完全沒有保證變異——"
        "而測試誤差 = 偏差² + 變異 + 不可約誤差。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>五種方法對照</h3>
{table(["方法", "在建模什麼", "邊界形狀", "關鍵假設", "參數量", "什麼時候選它"],
       [["邏輯斯迴歸", "後驗 Pr(Y|X)（判別式）", "線性", "log-odds 對 x 線性", "(K−1)(p+1)",
         "<strong>兩類的預設選擇</strong>、要推論、X 不常態"],
        ["LDA", "類條件 f<sub>k</sub>(x)（生成式）", "線性", "常態 + Σ 共用", "Kp + p(p+1)/2",
         "各類近常態、n 小、兩類分得很開"],
        ["QDA", "類條件 f<sub>k</sub>(x)", "二次", "常態 + Σ<sub>k</sub> 各自", "Kp + K·p(p+1)/2",
         "邊界明顯彎曲、n 大"],
        ["Naive Bayes", "類條件 f<sub>k</sub>(x)", "加性（無交互項）", "類內各變數獨立", "約 2Kp",
         "<strong>p 大 n 小</strong>、變數近似獨立"],
        ["KNN", "什麼都不建模", "任意", "無（無母數）", "存全部資料",
         "邊界極度彎曲且 n ≫ p"]])}

  <h3>Default 資料上的實測數字（可以直接對回課本）</h3>
{table(["", "TN", "FP", "FN", "TP", "錯誤率", "靈敏度", "出處"],
       [["LDA，閾值 0.5", "9644", "23", "<strong>252</strong>", "81", "2.75%", "24.3%", "ISLP 表 4.4"],
        ["LDA，閾值 0.2", "9432", "235", "<strong>138</strong>", "195", "3.73%", "58.6%", "ISLP 表 4.5"],
        ["Naive Bayes，閾值 0.5", "9621", "46", "244", "89", "2.90%", "26.7%", "ISLP 表 4.8"],
        ["Naive Bayes，閾值 0.2", "9339", "328", "130", "203", "4.58%", "61.0%", "ISLP 表 4.9"],
        ["一律預測「不違約」", "9667", "0", "333", "0", "3.33%", "0.0%", "虛無率"]])}
  <p style="font-size:.82rem;color:var(--muted);">本頁 <code>w04thr</code> 元件的 2×2 表在閾值
  0.5 與 0.2 會<strong>逐格</strong>重現前兩列（我們用 <code>scikit-learn</code> 的
  <code>LinearDiscriminantAnalysis</code> 在 <code>balance</code> + <code>student</code> 上重算，
  數字與課本相同）。ISLP 表 4.8／4.9 的 Naive Bayes 實作與 <code>GaussianNB</code>
  對 <code>student</code> 的處理略有不同，所以本頁烘焙的 NB 混淆矩陣是 9618／49／238／95。</p>

  <h3>Smarket 上五個方法的測試正確率（lab 的實跑結果）</h3>
{table(["方法", "測試正確率", "混淆矩陣（預測 × 真實）", "lab 儲存格"],
       [["邏輯斯（6 個變數）", "0.4801", "77／97／34／44", "49、51"],
        ["邏輯斯（Lag1 + Lag2）", "0.5595", "35／35／76／106", "53、55"],
        ["LDA（Lag1 + Lag2）", "0.5595", "35／35／76／106", "79"],
        ["QDA（Lag1 + Lag2）", "<strong>0.5992</strong>", "30／20／81／121", "95、97"],
        ["Naive Bayes（Lag1 + Lag2）", "0.5952", "29／20／82／121", "116、117"],
        ["KNN，K = 1", "0.5000", "43／58／68／83", "122、124"],
        ["KNN，K = 3", "0.5317", "—", "127"],
        ["一律猜 Up（虛無率）", "0.5595", "—", "—"]])}
  <p style="font-size:.82rem;color:var(--muted);">注意最後一列：<strong>「每天都猜漲」就有 55.95%</strong>。
  邏輯斯與 LDA 剛好打成平手、沒有贏過它；只有 QDA 與 Naive Bayes 真的多了一點資訊。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["邏輯斯函數", "$p(X) = \\dfrac{e^{\\beta_0+\\beta_1X}}{1+e^{\\beta_0+\\beta_1X}}$", "式 4.2"],
        ["logit / log-odds", "$\\log\\dfrac{p(X)}{1-p(X)} = \\beta_0+\\beta_1X$", "式 4.4，線性的是這個"],
        ["多元邏輯斯", "$\\log\\dfrac{\\Pr(Y=k|x)}{\\Pr(Y=K|x)} = \\beta_{k0}+\\sum_j\\beta_{kj}x_j$",
         "式 4.12"],
        ["softmax", "$\\Pr(Y=k|x) = \\dfrac{e^{\\beta_{k0}+\\sum_j\\beta_{kj}x_j}}{\\sum_l e^{\\beta_{l0}+\\sum_j\\beta_{lj}x_j}}$",
         "式 4.13，等價寫法"],
        ["Bayes 定理", "$\\Pr(Y=k|X=x) = \\dfrac{\\pi_k f_k(x)}{\\sum_l \\pi_l f_l(x)}$", "式 4.15"],
        ["LDA 判別函數（p = 1）", "$\\delta_k(x) = x\\dfrac{\\mu_k}{\\sigma^2} - \\dfrac{\\mu_k^2}{2\\sigma^2} + \\log\\pi_k$",
         "式 4.18，x 的一次式"],
        ["LDA 邊界（K = 2, 等先驗）", "$x = \\dfrac{\\mu_1+\\mu_2}{2}$", "式 4.19，兩平均的中點"],
        ["LDA 判別函數（p &gt; 1）",
         "$\\delta_k(x) = x^{\\mathsf{T}}\\Sigma^{-1}\\mu_k - \\tfrac12\\mu_k^{\\mathsf{T}}\\Sigma^{-1}\\mu_k + \\log\\pi_k$",
         "式 4.24"],
        ["QDA 判別函數",
         "$\\delta_k(x) = -\\tfrac12(x-\\mu_k)^{\\mathsf{T}}\\Sigma_k^{-1}(x-\\mu_k) - \\tfrac12\\log|\\Sigma_k| + \\log\\pi_k$",
         "式 4.28，x 的二次式"],
        ["Naive Bayes", "$f_k(x) = \\prod_{j=1}^{p} f_{kj}(x_j)$", "式 4.29，類內獨立"],
        ["Poisson 迴歸", "$\\log\\lambda(X) = \\beta_0+\\beta_1X_1+\\cdots+\\beta_pX_p$", "式 4.36"],
        ["GLM 連結函數", "$\\eta\\big(\\mathbb{E}(Y|X)\\big) = \\beta_0+\\beta_1X_1+\\cdots+\\beta_pX_p$",
         "式 4.42"]])}

{info("三個一定要記住的觀念", '''<strong>1. 邏輯斯迴歸線性的是 log-odds，不是機率。</strong>
  係數 β₁ 要讀成「勝算乘上 e^β₁」；同樣的 β₁ 對機率的影響隨位置而變。<br>
  <strong>2. 生成式（LDA／QDA／Naive Bayes）與判別式（邏輯斯）的差別只在係數怎麼來。</strong>
  LDA 的邊界形式跟邏輯斯字面上相同（式 4.32）；差別是前者從常態假設推、後者最大化條件似然。
  共用 Σ 給線性邊界、各自 Σ<sub>k</sub> 給二次邊界、類內獨立給加性邊界。<br>
  <strong>3. 0.5 這個閾值只是「總錯誤率最小」的產物。</strong>
  類別不平衡或兩種錯誤成本不同時，先問「哪種錯誤比較貴」，再調閾值，
  並且永遠把虛無率與混淆矩陣一起報出來。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== classification 本頁元件（id 與全域一律 w04 前綴）===== */

/* ---------- 小工具 ---------- */
function w04sv(id, v, d) { const e = $(id); if (e) e.textContent = HC.fmt(v, d); }
function w04tx(id, s) { const e = $(id); if (e) e.textContent = s; }
function w04lab(id, v, d) { const e = $(id + 'V'); if (e) e.textContent = HC.fmt(v, d); }
/* stats.css 的 .axlab / .vlab 有 fill，CSS 規則會壓過 presentation attribute，
   所以要自訂顏色時得寫成 inline style（優先權最高）。 */
function w04txt(s, px, py, str, color, g, anchor) {
  const n = s.txtPx(px, py, str, { cls: 'axlab', anchor: anchor || 'start' }, g);
  if (color) n.setAttribute('style', 'font-family:' + HC.MONO + ';font-size:11px;font-weight:600;fill:' + color);
  return n;
}
/* 把一條可能衝出 y 定義域的曲線切成幾段畫，避免給 SVG 天文數字座標 */
function w04clip(s, pts, attrs, g) {
  let run = [];
  for (const p of pts) {
    const ok = Number.isFinite(p[1]) && p[1] >= s.yd[0] && p[1] <= s.yd[1];
    if (ok) { run.push(p); } else { if (run.length > 1) s.poly(run, attrs, g); run = []; }
  }
  if (run.length > 1) s.poly(run, attrs, g);
}

/* ---------- P00 為什麼不用迴歸（hybrid：烘焙 Default 的兩組配適，即時讀值）---------- */
let w04whySvc = null, w04whyOnlyLog = false;
function w04whySetup() {
  w04whySvc = HC.svg('w04whySvg', { xd: [0, 2700], yd: [-0.32, 1.16], h: 330 });
  w04whySvc.grid(6, 6, { xtitle: 'balance（信用卡月結餘，美元）', ytitle: '違約機率 p', ydec: 1 });
}
function w04whyDraw() {
  const F = FRAMES_w04why, s = w04whySvc;
  if (!s) return;
  const g = s.clearLayer('main');
  /* 合法區間 [0,1] 的上下界 */
  s.seg(s.xd[0], 0, s.xd[1], 0, { cls: 'resid', sw: 1.4 }, g);
  s.seg(s.xd[0], 1, s.xd[1], 1, { cls: 'resid', sw: 1.4 }, g);
  s.txtPx(s.pad.l + 6, s.Y(1) - 6, 'p = 1', { cls: 'axlab' }, g);
  /* 線性版跑出 [0,1] 的區段：標紅 */
  if (!w04whyOnlyLog) {
    s.box(0, -0.32, F.zeroAt, 0, { fill: 'rgba(192,57,43,.16)' }, g);
    w04txt(s, s.X(F.zeroAt) + 8, s.Y(-0.19), 'balance < ' + F.zeroAt.toFixed(0)
      + ' 線性版給負機率', HC.tok.accent, g);
    const lp = HC.stat.seq(s.xd[0], s.xd[1], 40).map(x => [x, F.lin.b0 + F.lin.b1 * x]);
    s.poly(lp, { cls: 'fit', sw: 2.6 }, g);
    w04txt(s, s.X(1980), s.Y(F.lin.b0 + F.lin.b1 * 1980) - 9, '線性迴歸', HC.tok.accent, g);
  }
  /* 邏輯斯 */
  const gp = HC.stat.seq(s.xd[0], s.xd[1], 160).map(x => {
    const e = Math.exp(F.logit.b0 + F.logit.b1 * x);
    return [x, e / (1 + e)];
  });
  s.poly(gp, { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g);
  w04txt(s, s.X(1700), s.Y(0.80), '邏輯斯迴歸', HC.tok.accent3, g);
  /* rug：上排 y=1 是違約、下排 y=0 是沒違約 */
  F.pts.forEach(p => {
    const y0 = p[1] ? 1 : 0, c = p[1] ? HC.tok.b : HC.tok.a;
    s.seg(p[0], y0 - 0.035, p[0], y0 + 0.035, { stroke: c, sw: 1.1, cls: 'ln' }, g);
  });
  /* 目前的 balance */
  const b = parseFloat($('w04whyBal').value);
  const el = F.lin.b0 + F.lin.b1 * b;
  const ee = Math.exp(F.logit.b0 + F.logit.b1 * b), eg = ee / (1 + ee);
  s.seg(b, s.yd[0], b, s.yd[1], { stroke: HC.tok.muted, sw: 1.3, dash: '4 3', cls: 'ln' }, g);
  if (!w04whyOnlyLog) s.dot(b, el, { r: 5.5, fill: HC.tok.accent, stroke: '#fff', sw: 1.4 }, g);
  s.dot(b, eg, { r: 5.5, fill: HC.tok.accent3, stroke: '#fff', sw: 1.4 }, g);
  w04tx('w04whyBal2', b.toFixed(0));
  w04lab('w04whyBal', b, 0);
  w04sv('w04whyLin', el, 4);
  w04sv('w04whyLog', eg, 4);
  w04tx('w04whyOk', el < 0 ? '不合法（負機率）' : (el > 1 ? '不合法（大於 1）' : '剛好還在 [0,1] 內'));
  setStatus('w04whyStatus', 'balance = ' + b.toFixed(0) + ' 時，線性迴歸給 '
    + HC.fmt(el, 4) + '，邏輯斯給 ' + HC.fmt(eg, 4) + '。'
    + (el < 0 ? '<strong>線性版是負數——這不是機率。</strong>'
      : '兩者都落在 [0,1] 裡，但線性版只是運氣好：往左推就破了。'));
}
function w04whyMove() { w04whyDraw(); }
function w04whyJump(v) { $('w04whyBal').value = String(v); w04whyDraw(); }
function w04whyToggle() {
  w04whyOnlyLog = !w04whyOnlyLog;
  w04whyDraw();
  setStatus('w04whyStatus', w04whyOnlyLog
    ? '只留邏輯斯曲線：整條線都在 0 與 1 之間，兩端逼近但永遠碰不到。'
    : '兩條一起看：紅色直線遲早會離開 [0,1]，綠色 S 曲線不會。');
}
function w04whyReset() {
  w04whyOnlyLog = false;
  $('w04whyBal').value = '1000';
  w04whyDraw();
  setStatus('w04whyStatus', '拖滑桿選一個 balance，右邊會同時給出兩個模型的預測機率。');
}

/* ---------- P01 S 曲線形狀器（live）---------- */
let w04shapeS1 = null, w04shapeS2 = null;
function w04shapeSetup() {
  w04shapeS1 = HC.svg('w04shapeSvg', { xd: [-6, 6], yd: [-0.06, 1.06], h: 250 });
  w04shapeS1.grid(6, 4, { xtitle: 'x', ytitle: '機率 p(x)', ydec: 1 });
  w04shapeS2 = HC.svg('w04shapeSvg2', { xd: [-6, 6], yd: [-8, 8], h: 220 });
  w04shapeS2.grid(6, 4, { xtitle: 'x', ytitle: 'log-odds 與 odds', ydec: 0 });
}
function w04shapeDraw() {
  const b0 = parseFloat($('w04shapeB0').value), b1 = parseFloat($('w04shapeB1').value);
  w04lab('w04shapeB0', b0, 2); w04lab('w04shapeB1', b1, 2);
  const P = x => { const e = Math.exp(b0 + b1 * x); return e / (1 + e); };
  const xs = HC.stat.seq(-6, 6, 200);
  /* 上圖：機率 */
  const s = w04shapeS1, g = s.clearLayer('main');
  s.seg(-6, 0.5, 6, 0.5, { cls: 'resid', sw: 1.2 }, g);
  s.poly(xs.map(x => [x, P(x)]), { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g);
  if (Math.abs(b1) > 1e-6) {
    const xh = -b0 / b1;
    if (xh > -6 && xh < 6) {
      s.seg(xh, -0.06, xh, 1.06, { stroke: HC.tok.accent, sw: 1.4, dash: '4 3', cls: 'ln' }, g);
      s.dot(xh, 0.5, { r: 5, fill: HC.tok.accent, stroke: '#fff', sw: 1.3 }, g);
    }
  }
  w04txt(s, s.pad.l + 8, s.Y(0.5) - 7, 'p = 0.5', HC.tok.muted, g);
  /* 下圖：log-odds（直線）與 odds（指數，超出就切斷） */
  const s2 = w04shapeS2, g2 = s2.clearLayer('main');
  s2.seg(-6, 0, 6, 0, { cls: 'resid', sw: 1.2 }, g2);
  w04clip(s2, xs.map(x => [x, b0 + b1 * x]),
    { cls: 'ln', stroke: HC.tok.accent3, sw: 3 }, g2);
  w04clip(s2, xs.map(x => [x, Math.exp(b0 + b1 * x)]),
    { cls: 'ln', stroke: HC.tok.accent, sw: 2.2, dash: '6 4' }, g2);
  w04txt(s2, s2.pad.l + 8, s2.Y(6.6), 'log-odds = β₀ + β₁x（直線）', HC.tok.accent3, g2);
  w04txt(s2, s2.pad.l + 8, s2.Y(4.8), 'odds = e^(β₀+β₁x)（虛線，很快衝出圖外）', HC.tok.accent, g2);
  /* 側欄 */
  w04tx('w04shapeB0T', HC.fmt(b0, 2));
  w04tx('w04shapeB1T', HC.fmt(b1, 2));
  w04sv('w04shapeP0', P(0), 4);
  w04sv('w04shapeP1', P(1), 4);
  w04tx('w04shapeHalf', Math.abs(b1) > 1e-6 ? HC.fmt(-b0 / b1, 2) : '不存在（β₁ = 0）');
  w04sv('w04shapeOR', Math.exp(b1), 4);
  setStatus('w04shapeStatus', 'β₀ = ' + HC.fmt(b0, 2) + '、β₁ = ' + HC.fmt(b1, 2)
    + '：勝算比 e^β₁ = ' + HC.fmt(Math.exp(b1), 3)
    + '（x 每加 1，勝算乘這個數）。上圖是 S 形，下圖那條實線永遠是直的。');
}
function w04shapeReset() {
  $('w04shapeB0').value = '-1'; $('w04shapeB1').value = '0.8';
  w04shapeDraw();
}

/* ---------- P03 一維 LDA ↔ QDA（live）---------- */
let w04lda1Svc = null, w04lda1Qda = false;
function w04lda1Setup() {
  w04lda1Svc = HC.svg('w04lda1Svg', { xd: [-7, 7], yd: [0, 0.46], h: 320 });
  w04lda1Svc.grid(7, 4, { xtitle: 'x', ytitle: 'πₖ · fₖ(x)', ydec: 2 });
}
/* 回傳目前的邊界（0、1 或 2 個點） */
function w04lda1Bounds(m1, m2, s1, s2, p1) {
  const p2 = 1 - p1;
  if (Math.abs(s1 - s2) < 1e-9) {
    if (Math.abs(m1 - m2) < 1e-9) return [];
    return [(m1 + m2) / 2 + s1 * s1 * Math.log(p2 / p1) / (m1 - m2)];
  }
  const a = 1 / (2 * s2 * s2) - 1 / (2 * s1 * s1);
  const b = m1 / (s1 * s1) - m2 / (s2 * s2);
  const c = m2 * m2 / (2 * s2 * s2) - m1 * m1 / (2 * s1 * s1)
    + Math.log(p1 / p2) + Math.log(s2 / s1);
  if (Math.abs(a) < 1e-12) return Math.abs(b) < 1e-12 ? [] : [-c / b];
  const disc = b * b - 4 * a * c;
  if (disc < 0) return [];
  const r = Math.sqrt(disc);
  return [(-b - r) / (2 * a), (-b + r) / (2 * a)].sort((u, v) => u - v);
}
function w04lda1Draw() {
  const m1 = parseFloat($('w04lda1M1').value), m2 = parseFloat($('w04lda1M2').value);
  const r1 = parseFloat($('w04lda1S1').value), r2 = parseFloat($('w04lda1S2').value);
  const p1 = parseFloat($('w04lda1P1').value), p2 = 1 - p1;
  ['w04lda1M1', 'w04lda1M2'].forEach((i, k) => w04lab(i, k ? m2 : m1, 2));
  w04lab('w04lda1S1', r1, 2); w04lab('w04lda1S2', r2, 2); w04lab('w04lda1P1', p1, 2);
  /* LDA 模式：兩類共用一個併合後的 σ */
  const pooled = Math.sqrt((r1 * r1 + r2 * r2) / 2);
  const s1 = w04lda1Qda ? r1 : pooled, s2 = w04lda1Qda ? r2 : pooled;
  const s = w04lda1Svc, g = s.clearLayer('main');
  const f1 = x => p1 * HC.stat.dnorm(x, m1, s1);
  const f2 = x => p2 * HC.stat.dnorm(x, m2, s2);
  const xs = HC.stat.seq(-7, 7, 240);
  const top = Math.max(0.12, Math.max(...xs.map(x => Math.max(f1(x), f2(x)))) * 1.18);
  s.domain([-7, 7], [0, top]);
  s.grid(7, 4, { xtitle: 'x', ytitle: 'πₖ · fₖ(x)', ydec: 2 });
  const bs = w04lda1Bounds(m1, m2, s1, s2, p1);
  bs.forEach(x => {
    if (x > -7 && x < 7) {
      s.seg(x, 0, x, top, { stroke: HC.tok.accent, sw: 2.2, dash: '6 4', cls: 'ln' }, g);
      w04txt(s, s.X(x) + 5, s.Y(top) + 13, HC.fmt(x, 2), HC.tok.accent, g);
    }
  });
  s.poly(xs.map(x => [x, f1(x)]), { stroke: HC.tok.a, sw: 2.8, cls: 'ln' }, g);
  s.poly(xs.map(x => [x, f2(x)]), { stroke: HC.tok.b, sw: 2.8, cls: 'ln' }, g);
  w04txt(s, s.X(m1), s.Y(f1(m1)) - 8, '第 1 類', HC.tok.a, g, 'middle');
  w04txt(s, s.X(m2), s.Y(f2(m2)) - 8, '第 2 類', HC.tok.b, g, 'middle');
  w04tx('w04lda1Mode', w04lda1Qda ? 'QDA（各自 σ）' : 'LDA（共用 σ）');
  w04tx('w04lda1Pri', HC.fmt(p1, 2) + ' · ' + HC.fmt(p2, 2));
  w04tx('w04lda1Sig', HC.fmt(s1, 2) + ' · ' + HC.fmt(s2, 2));
  w04tx('w04lda1Bnd', bs.length ? bs.map(v => HC.fmt(v, 2)).join(' 與 ') : '不存在');
  w04tx('w04lda1Mid', HC.fmt((m1 + m2) / 2, 2));
  setStatus('w04lda1Status', (w04lda1Qda ? 'QDA' : 'LDA') + ' 模式，'
    + (bs.length === 2 ? '邊界有兩個點：' : (bs.length === 1 ? '邊界只有一個點：' : '目前沒有邊界（'))
    + (bs.length ? bs.map(v => HC.fmt(v, 2)).join(' 與 ') : '兩個密度沒有交點）')
    + (bs.length === 1 && !w04lda1Qda && Math.abs(p1 - 0.5) < 1e-9
      ? '，剛好是兩個平均的中點。' : '。'));
}
function w04lda1Toggle() {
  w04lda1Qda = !w04lda1Qda;
  w04lda1Draw();
}
function w04lda1Reset() {
  w04lda1Qda = false;
  $('w04lda1M1').value = '-1.25'; $('w04lda1M2').value = '1.25';
  $('w04lda1S1').value = '1'; $('w04lda1S2').value = '1'; $('w04lda1P1').value = '0.5';
  w04lda1Draw();
}

/* ---------- P04 二維 LDA ↔ QDA（live）---------- */
let w04lda2Svc = null, w04lda2Qda = false;
function w04lda2Setup() {
  w04lda2Svc = HC.svg('w04lda2Svg', { xd: [-5, 5], yd: [-5, 5], h: 360 });
  w04lda2Svc.grid(5, 5, { xtitle: 'X₁', ytitle: 'X₂', xdec: 0, ydec: 0 });
}
function w04lda2Inv(S) {
  const d = S[0] * S[3] - S[1] * S[2];
  return { inv: [S[3] / d, -S[1] / d, -S[2] / d, S[0] / d], det: d };
}
/* 30 筆抽樣：用 Cholesky 把標準常態轉成指定的 Σ */
function w04lda2Sample(mu, rho, seed) {
  const rand = HC.stat.lcg(seed), out = [];
  const r = Math.max(-0.985, Math.min(0.985, rho));
  const t = Math.sqrt(1 - r * r);
  for (let i = 0; i < 30; i++) {
    const z1 = HC.stat.normal(rand), z2 = HC.stat.normal(rand);
    out.push([mu[0] + z1, mu[1] + r * z1 + t * z2]);
  }
  return out;
}
function w04lda2Ellipse(mu, rho) {
  const r = Math.max(-0.985, Math.min(0.985, rho)), t = Math.sqrt(1 - r * r), k = 2.4477;
  const pts = [];
  for (let i = 0; i <= 90; i++) {
    const a = i / 90 * 2 * Math.PI, c = Math.cos(a), s = Math.sin(a);
    pts.push([mu[0] + k * c, mu[1] + k * (r * c + t * s)]);
  }
  return pts;
}
function w04lda2Draw() {
  const r1i = parseFloat($('w04lda2R1').value), r2i = parseFloat($('w04lda2R2').value);
  const d = parseFloat($('w04lda2D').value);
  w04lab('w04lda2R1', r1i, 2); w04lab('w04lda2R2', r2i, 2); w04lab('w04lda2D', d, 1);
  const pooledR = (r1i + r2i) / 2;
  const r1 = w04lda2Qda ? r1i : pooledR, r2 = w04lda2Qda ? r2i : pooledR;
  const mu1 = [-d, -d], mu2 = [d, d];
  const S1 = [1, r1, r1, 1], S2 = [1, r2, r2, 1];
  const SP = [1, pooledR, pooledR, 1];
  const A = w04lda2Inv(S1), B = w04lda2Inv(S2), P = w04lda2Inv(SP);
  const s = w04lda2Svc, g = s.clearLayer('main');
  /* LDA 的線性邊界（永遠畫，當對照）：w·x = c */
  const dm = [mu1[0] - mu2[0], mu1[1] - mu2[1]];
  const w1 = P.inv[0] * dm[0] + P.inv[1] * dm[1];
  const w2 = P.inv[2] * dm[0] + P.inv[3] * dm[1];
  const mid = [(mu1[0] + mu2[0]) / 2, (mu1[1] + mu2[1]) / 2];
  const cc = w1 * mid[0] + w2 * mid[1];
  const linePts = [];
  if (Math.abs(w2) > 1e-9) {
    HC.stat.seq(-5, 5, 60).forEach(u => linePts.push([u, (cc - w1 * u) / w2]));
  } else if (Math.abs(w1) > 1e-9) {
    HC.stat.seq(-5, 5, 60).forEach(v => linePts.push([cc / w1, v]));
  }
  if (linePts.length) {
    w04clip(s, linePts, { stroke: HC.tok.muted, sw: 1.8, dash: '5 4', cls: 'ln' }, g);
  }
  /* QDA 的二次邊界：對每個 u 解 v 的二次式（係數用三點取樣反推） */
  const Q = (u, v) => {
    const q = (M, mu) => {
      const a = u - mu[0], b = v - mu[1];
      return M[0] * a * a + (M[1] + M[2]) * a * b + M[3] * b * b;
    };
    return 0.5 * (q(B.inv, mu2) - q(A.inv, mu1)) + 0.5 * Math.log(B.det / A.det);
  };
  if (w04lda2Qda) {
    const us = HC.stat.seq(-5, 5, 170), br1 = [], br2 = [];
    us.forEach(u => {
      const f0 = Q(u, 0), fp = Q(u, 1), fm = Q(u, -1);
      const a = (fp + fm) / 2 - f0, b = (fp - fm) / 2, c = f0;
      let roots = [];
      if (Math.abs(a) < 1e-10) {
        if (Math.abs(b) > 1e-10) roots = [-c / b, NaN];
      } else {
        const disc = b * b - 4 * a * c;
        if (disc >= 0) {
          const rr = Math.sqrt(disc);
          roots = [(-b - rr) / (2 * a), (-b + rr) / (2 * a)].sort((x, y) => x - y);
        }
      }
      br1.push([u, roots.length ? roots[0] : NaN]);
      br2.push([u, roots.length > 1 ? roots[1] : NaN]);
    });
    w04clip(s, br1, { cls: 'fit', sw: 2.8 }, g);
    w04clip(s, br2, { cls: 'fit', sw: 2.8 }, g);
  } else if (linePts.length) {
    w04clip(s, linePts, { cls: 'fit', sw: 2.8 }, g);
  }
  /* 橢圓與抽樣點 */
  s.poly(w04lda2Ellipse(mu1, r1), { stroke: HC.tok.a, sw: 2.2, cls: 'ln' }, g);
  s.poly(w04lda2Ellipse(mu2, r2), { stroke: HC.tok.b, sw: 2.2, cls: 'ln' }, g);
  w04txt(s, s.pad.l + 8, s.pad.t + 14, '藍＝第 1 類（ρ₁）　紅＝第 2 類（ρ₂）　'
    + '灰虛線＝LDA 線性邊界', HC.tok.muted, g);
  const p1 = w04lda2Sample(mu1, r1, 4041), p2 = w04lda2Sample(mu2, r2, 4042);
  p1.forEach(p => s.dot(p[0], p[1], { r: 3.4, fill: HC.tok.a, stroke: '#fff', sw: .9 }, g));
  p2.forEach(p => s.dot(p[0], p[1], { r: 3.4, fill: HC.tok.b, stroke: '#fff', sw: .9 }, g));
  /* 60 個點的訓練錯誤（用目前模式的規則判） */
  let bad = 0;
  const rule = p => {
    if (w04lda2Qda) return Q(p[0], p[1]) > 0 ? 1 : 2;
    return (w1 * p[0] + w2 * p[1] - cc) > 0 ? 1 : 2;
  };
  p1.forEach(p => { if (rule(p) !== 1) bad++; });
  p2.forEach(p => { if (rule(p) !== 2) bad++; });
  w04tx('w04lda2Mode', w04lda2Qda ? 'QDA（各自 Σ）' : 'LDA（共用 Σ）');
  w04tx('w04lda2R1T', HC.fmt(r1, 2));
  w04tx('w04lda2R2T', HC.fmt(r2, 2));
  w04tx('w04lda2Shape', w04lda2Qda
    ? (Math.abs(r1i - r2i) < 1e-9 ? '二次式退化成直線' : '二次曲線') : '直線');
  w04tx('w04lda2Err', bad + ' / 60（' + HC.pct(bad / 60, 1) + '）');
  setStatus('w04lda2Status', (w04lda2Qda ? 'QDA' : 'LDA') + ' 模式，ρ₁ = '
    + HC.fmt(r1, 2) + '、ρ₂ = ' + HC.fmt(r2, 2) + '，邊界是'
    + (w04lda2Qda && Math.abs(r1i - r2i) > 1e-9 ? '二次曲線（紅）' : '直線')
    + '，灰虛線是 LDA 的線性邊界。60 個抽樣點裡判錯 ' + bad + ' 個。');
}
function w04lda2Toggle() { w04lda2Qda = !w04lda2Qda; w04lda2Draw(); }
function w04lda2Reset() {
  w04lda2Qda = false;
  $('w04lda2R1').value = '0.7'; $('w04lda2R2').value = '0.7'; $('w04lda2D').value = '1.4';
  w04lda2Draw();
}

/* ---------- P05 閾值 + 混淆矩陣 + ROC（hybrid）---------- */
const w04thrCum = (() => {
  const F = FRAMES_w04thr, n = F.nbins;
  const cy = new Array(n + 1).fill(0), cn = new Array(n + 1).fill(0);
  for (let k = n - 1; k >= 0; k--) {
    cy[k] = cy[k + 1] + F.histYes[k];
    cn[k] = cn[k + 1] + F.histNo[k];
  }
  return { cy, cn };
})();
const w04thrRocPts = (() => {
  const F = FRAMES_w04thr, out = [];
  for (let k = 0; k <= F.nbins; k++) {
    const tp = w04thrCum.cy[k], fp = w04thrCum.cn[k];
    out.push({ x: fp / F.nNeg, y: tp / F.nPos });
  }
  return out;
})();
function w04thrStats(t) {
  const F = FRAMES_w04thr;
  const k = Math.max(0, Math.min(F.nbins, Math.round(t * F.nbins)));
  const tp = w04thrCum.cy[k], fp = w04thrCum.cn[k];
  const fn = F.nPos - tp, tn = F.nNeg - fp;
  return {
    t: k / F.nbins, tp: tp, fp: fp, fn: fn, tn: tn,
    sens: tp / F.nPos, spec: tn / F.nNeg, fpr: fp / F.nNeg,
    prec: (tp + fp) > 0 ? tp / (tp + fp) : NaN,
    err: (fp + fn) / F.n,
  };
}
function w04thrDrawRoc() {
  HC.line('w04thrRoc', {
    datasets: [
      { label: 'LDA 的 ROC', data: w04thrRocPts, borderColor: HC.tok.accent2,
        borderWidth: 2.4, pointRadius: 0, fill: false },
      { label: '目前閾值', data: [{ x: 0, y: 0 }], borderColor: HC.tok.accent,
        backgroundColor: HC.tok.accent, pointRadius: 6.5, showLine: false },
      { label: '隨機猜', data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: HC.tok.muted,
        borderWidth: 1.2, borderDash: [5, 4], pointRadius: 0, fill: false },
    ],
  }, {
    interaction: { mode: 'nearest', intersect: true },
    scales: {
      x: { type: 'linear', min: 0, max: 1, title: { display: true, text: '假陽率 FPR = 1 − 特異度' } },
      y: { min: 0, max: 1, title: { display: true, text: '真陽率 TPR = 靈敏度' } },
    },
  });
}
function w04thrApply(s) {
  w04tx('w04thrTN', String(s.tn)); w04tx('w04thrFP', String(s.fp));
  w04tx('w04thrFN', String(s.fn)); w04tx('w04thrTP', String(s.tp));
  w04tx('w04thrRN', String(s.tn + s.fn)); w04tx('w04thrRP', String(s.fp + s.tp));
  w04tx('w04thrT', HC.fmt(s.t, 3));
  w04tx('w04thrNP', String(s.fp + s.tp));
  w04tx('w04thrSens', HC.pct(s.sens, 1));
  w04tx('w04thrSpec', HC.pct(s.spec, 1));
  w04tx('w04thrPrec', Number.isNaN(s.prec) ? '—（沒有人被判為違約）' : HC.pct(s.prec, 1));
  w04tx('w04thrErr', HC.pct(s.err, 2));
  HC.update('w04thrRoc', c => { c.data.datasets[1].data = [{ x: s.fpr, y: s.sens }]; });
  setStatus('w04thrStatus', '閾值 ' + HC.fmt(s.t, 3) + '：預測會違約 ' + (s.fp + s.tp)
    + ' 人，抓到 ' + s.tp + ' / ' + FRAMES_w04thr.nPos + ' 個真違約戶（靈敏度 '
    + HC.pct(s.sens, 1) + '），誤報 ' + s.fp + ' 人，總錯誤率 ' + HC.pct(s.err, 2) + '。');
}
function w04thrMove() {
  const t = parseFloat($('w04thrSlider').value);
  w04lab('w04thrSlider', t, 3);
  w04thrApply(w04thrStats(t));
}
function w04thrSet(t) { $('w04thrSlider').value = String(t); w04thrMove(); }
function w04thrReset() { w04thrSet(0.5); }

/* ---------- P06 四方法 ROC 疊圖（Chart.js，baked）---------- */
const w04rocNames = { logit: '邏輯斯迴歸', lda: 'LDA', qda: 'QDA', nb: 'Naive Bayes' };
let w04rocZoomed = false;
function w04rocFill() {
  Object.keys(w04rocNames).forEach((k, i) => {
    w04tx('w04rocA' + (i + 1), HC.fmt(FRAMES_w04roc.auc[k], 4));
  });
}
function w04rocDraw() {
  const F = FRAMES_w04roc;
  const cols = { logit: HC.tok.accent2, lda: HC.tok.accent3, qda: HC.tok.accent, nb: '#8e44ad' };
  const dash = { logit: [], lda: [7, 3], qda: [2, 3], nb: [11, 4] };
  const wid = { logit: 3.4, lda: 2.2, qda: 2.2, nb: 2.2 };
  const ds = Object.keys(w04rocNames).map(k => ({
    label: w04rocNames[k] + '（AUC ' + HC.fmt(F.auc[k], 4) + '）',
    data: F.curves[k].map(p => ({ x: p[0], y: p[1] })),
    borderColor: cols[k], borderWidth: wid[k], borderDash: dash[k], pointRadius: 0, fill: false,
  }));
  ds.push({ label: '隨機猜', data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: HC.tok.muted,
            borderWidth: 1.2, borderDash: [5, 4], pointRadius: 0, fill: false });
  const hi = w04rocZoomed ? 0.3 : 1;
  const lo = w04rocZoomed ? 0.7 : 0;
  HC.line('w04rocChart', { datasets: ds }, {
    interaction: { mode: 'nearest', intersect: false },
    plugins: { legend: { labels: { boxWidth: 8, font: { family: HC.MONO, size: 10 } } } },
    scales: {
      x: { type: 'linear', min: 0, max: hi, title: { display: true, text: '假陽率 FPR' } },
      y: { min: lo, max: 1, title: { display: true, text: '真陽率 TPR' } },
    },
  });
  w04rocFill();
}
function w04rocZoom(on) {
  w04rocZoomed = on;
  w04rocDraw();
  setStatus('w04rocStatus', on
    ? '放大左上角（FPR 0–0.3、TPR 0.7–1）：四條線在高靈敏度區才真正分開，Naive Bayes 明顯落後。'
    : '整張 0–1 的視野：四條幾乎完全重疊——訊號夠強時模型假設的差別看不出來。');
}

/* ---------- P06 選方法情境（live）---------- */
const w04pickData = [
  { q: '兩類、每類只有 20 筆訓練資料；兩個預測變數在各類內都近似常態，而且兩類的共變異數矩陣幾乎一樣。',
    best: 1,
    fb: ['邏輯斯迴歸在這裡也不差（邊界確實線性），但它沒用到「各類內近似常態」這個額外資訊；n 只有 40 時 LDA 的變異更小。',
         '正解。這正是 LDA 的假設本身：常態 + 共用共變異數。ISLP 情境 1 裡 LDA 表現最好。',
         '不對。共變異數幾乎一樣，QDA 要多估一個 Σ 卻換不到偏差的減少——純粹的變異。',
         'Naive Bayes 只有在變數近似獨立時才划算；這裡沒說獨立，而且 n 小的問題 LDA 已經處理得更好。',
         'KNN 在 n = 40、邊界又是線性的情況下最吃虧：付了無母數的變異，卻沒有彎曲的邊界可賺。'] },
  { q: '兩類、每類 50 筆；真實邊界仍然是線性的，但兩個變數在各類內是重尾的 t 分佈（極端值不少），而且類內有強烈負相關。',
    best: 0,
    fb: ['正解。邊界線性所以要線性方法，但 t 分佈違反常態假設，LDA 的參數估計吃虧。ISLP 情境 3 裡邏輯斯贏過 LDA。',
         '方向對（線性邊界）但被非常態拖累。LDA 的係數是從常態假設推出來的，重尾資料會讓 μ̂ 與 Σ̂ 不穩。',
         '更糟。QDA 對非常態更敏感，ISLP 情境 3 裡它退化得最明顯。',
         '最差。類內有強烈負相關，獨立假設被正面違反。',
         'KNN 沒有分佈假設是優點，但邊界既然是線性的，它的彈性用不上，變異卻要照付。'] },
  { q: '兩類、n 很大；第一類的兩個變數相關係數是 +0.5，第二類是 −0.5，各類內都是常態。',
    best: 2,
    fb: ['不行。兩類的共變異數不同 ⟹ 真實邊界是二次的，線性方法有系統性偏差，加多少資料都消不掉。',
         '同樣不行。LDA 硬性假設 Σ 共用，這裡明顯不成立，會有無法消除的偏差。',
         '正解。Σ₁ ≠ Σ₂ 正好是 QDA 的假設，而 n 很大讓多估的參數不成問題。ISLP 情境 4。',
         '不好。兩類內部都明顯相關，獨立假設被違反。',
         'KNN 可以配出彎的邊界，但這裡邊界剛好是二次的——QDA 用參數形式配同一條邊界，需要的樣本少得多。'] },
  { q: 'p = 85 個預測變數、n 不到 6000（就是 lab 的 Caravan 資料），變數彼此近似獨立，正類只佔 6%。',
    best: 3,
    fb: ['邏輯斯迴歸可以跑（lab 就跑了），但 85 個變數上它需要正則化才穩；而且它沒有利用「近似獨立」。',
         'LDA 要估 85 × 86 / 2 = 3655 個共變異數參數，n 不到 6000 撐不住。',
         'QDA 更糟：要估兩倍的 3655 個，直接爆掉。',
         '正解。p 大、變數近似獨立時 Naive Bayes 的偏差很小而變異極低——它只要估 2Kp 個數。',
         'KNN 在 p = 85 時被維度詛咒（curse of dimensionality）打敗：「最近的鄰居」其實一點都不近。'] },
  { q: '兩類、p = 2、n 非常大（每類幾千筆）；真實決策邊界高度彎曲，而且不是二次曲線。',
    best: 4,
    fb: ['線性邊界配不了高度彎曲的真實邊界，偏差消不掉。',
         '同上，LDA 也只給線性邊界。',
         'QDA 能彎，但只能彎成二次曲線。真實邊界「不是二次」時它仍有偏差。',
         'Naive Bayes 可以彎（gₖⱼ 任意），但它是純加性的、沒有交互項，複雜邊界仍配不好。',
         '正解。p 小、n 極大、邊界極彎，正是 KNN 的主場。但 K 要用交叉驗證挑——ISLP 情境 5 裡 KNN-1 是全場最差。'] },
  { q: '兩類、每類只有 6 筆資料；各類的共變異數矩陣是對角的（變數獨立）但兩類不同。',
    best: 3,
    fb: ['Σ 不同 ⟹ 邊界非線性，邏輯斯迴歸有偏差；而且 n = 12 時它的估計非常不穩。',
         'LDA 假設 Σ 共用，這裡不成立。',
         'QDA 的假設對，但每類 6 筆要估一個完整的 Σ，變異太大——ISLP 情境 6 裡它輸給 Naive Bayes。',
         '正解。對角 Σ 就是「類內獨立」，Naive Bayes 的假設完全成立，而它要估的參數最少。ISLP 情境 6。',
         'n = 12 的 KNN 幾乎沒有鄰居可以看。'] },
];
let w04pickAt = 0;
const w04pickState = w04pickData.map(() => -1);
function w04pickShow() {
  const d = w04pickData[w04pickAt], names = ['邏輯斯迴歸', 'LDA', 'QDA', 'Naive Bayes', 'KNN'];
  w04tx('w04pickNo', '情境 ' + (w04pickAt + 1) + ' / ' + w04pickData.length);
  w04tx('w04pickQ', d.q);
  const a = w04pickState[w04pickAt];
  const fb = $('w04pickFb');
  if (a < 0) {
    fb.textContent = '按下面任一個方法看看拆解。';
    fb.style.color = 'var(--muted)';
  } else {
    fb.textContent = (a === d.best ? '✓ ' : '✗ ') + names[a] + '：' + d.fb[a]
      + (a === d.best ? '' : '（建議答案：' + names[d.best] + '）');
    fb.style.color = a === d.best ? 'var(--accent3)' : 'var(--accent)';
  }
  const hit = w04pickState.filter((v, i) => v === w04pickData[i].best).length;
  const done = w04pickState.filter(v => v >= 0).length;
  w04tx('w04pickIdx', (w04pickAt + 1) + ' / ' + w04pickData.length);
  w04tx('w04pickHit', String(hit));
  w04tx('w04pickDone', done + ' / ' + w04pickData.length);
  setStatus('w04pickStatus', '第 ' + (w04pickAt + 1) + ' 個情境，已作答 ' + done + ' / '
    + w04pickData.length + '，答對 ' + hit + ' 個。' + (a < 0 ? '點一個方法看拆解。'
      : (a === w04pickData[w04pickAt].best ? '這一題對了，按「下一個情境」繼續。'
        : '這一題選錯了，讀完拆解再按「下一個情境」。')));
}
function w04pickAns(k) { w04pickState[w04pickAt] = k; w04pickShow(); }
function w04pickNext() { w04pickAt = (w04pickAt + 1) % w04pickData.length; w04pickShow(); }
function w04pickReset() {
  w04pickAt = 0;
  for (let i = 0; i < w04pickState.length; i++) w04pickState[i] = -1;
  w04pickShow();
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.line / HC.update 在 Chart 未載入時本來就安全地回傳 null。 */
w04whySetup();
w04whyDraw();
w04shapeSetup();
w04shapeDraw();
w04lda1Setup();
w04lda1Draw();
w04lda2Setup();
w04lda2Draw();
w04thrApply(w04thrStats(0.5));
w04rocFill();
w04pickShow();
HC.ready(() => {
  w04thrDrawRoc();
  w04thrApply(w04thrStats(parseFloat($('w04thrSlider').value)));
  w04rocDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("classification", BODIES, PAGEJS, frames())
