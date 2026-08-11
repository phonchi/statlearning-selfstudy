#!/usr/bin/env python3
"""resampling_methods.html（ISLP 第 5 章）完整自學充實。冪等。

內容依據：講義 05_Resampling_Methods.pdf（42 頁）、Ch05-resample-lab-zh.ipynb、
ISLP 第 5 章（書上 p.201–228）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_resampling.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 5
LAB = "Ch05-resample-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


# ── 產生烘焙資料 ────────────────────────────────────────────────────────
def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_resampling.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_resampling.py 失敗：\n" + r.stderr[-2000:])
    return "/* ===== 烘焙資料（tools/frames/gen_resampling.py，固定種子）===== */\n" + r.stdout.strip()


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>你已經會配模型了。現在的問題換成：<strong>這個模型在沒見過的資料上會有多準？</strong>
  最直覺的做法是拿訓練資料算誤差——但那個數字幾乎一定太樂觀，因為模型是照著那批資料調出來的。
  極端一點想：一棵長到每個葉子只剩一個樣本的樹，訓練誤差是 0，可是它什麼都沒學到。</p>

  <p>如果手上有一大筆獨立的測試資料，事情很簡單。但真實情況通常是資料就這麼多，
  再切出去一塊當測試集就不夠訓練了。<strong>重抽樣</strong>（resampling）的想法是：
  反覆從同一批資料裡切出「假的」訓練／測試組合，用它們的平均表現去猜真正的測試誤差。</p>

{info("本章你會學到的三件事", '''<strong>1. 驗證集法（validation set）：</strong>切兩半，最簡單，但答案會隨切法跳動。<br>
  <strong>2. 交叉驗證（cross-validation）：</strong>LOOCV 與 <em>k</em>-fold，讓每個樣本都輪到當一次測試資料。<br>
  <strong>3. Bootstrap：</strong>有放回地重抽，不靠公式就能算出任何估計量的標準誤。''')}

  <p>這三個工具的分工可以先記住：<strong>交叉驗證是用來估「預測誤差」並藉此選模型</strong>，
  <strong>bootstrap 是用來估「某個估計量的不確定性」</strong>。兩者都在重抽樣，但問的問題不同。</p>

{table(["", "切幾次", "每次訓練用多少", "有隨機性嗎", "主要用途"],
       [["驗證集法", "1", "約 n/2", "有，換 seed 就變", "快速粗估"],
        ["LOOCV", "n", "n − 1", "沒有（分割唯一）", "小資料、要穩定"],
        ["<em>k</em>-fold CV", "k（通常 5 或 10）", "n(k−1)/k", "有，但比驗證集小很多", "選模型的標準做法"],
        ["Bootstrap", "B（通常 1000）", "n（有放回）", "有，B 大就穩", "估標準誤與信賴區間"]])}

{quiz("qWhy", "QUIZ · 為什麼不能用訓練誤差",
      "為什麼「訓練誤差」不能拿來當測試誤差的估計？",
      [(True, "模型的參數是照著這批資料挑出來的，誤差已經被最小化過，所以會系統性偏低",
        "對。訓練誤差是「已經被最佳化過的目標值」，它衡量的是配適程度，不是預測能力。模型愈有彈性，這個偏差愈大。"),
       (False, "訓練資料的樣本數太少，誤差的變異太大",
        "不對。樣本少會讓誤差不穩定（變異大），但這裡的問題是<strong>系統性偏低</strong>（偏差），不是不穩定。就算訓練資料很多，訓練誤差仍然偏低。"),
       (False, "訓練誤差用的是 MSE，測試誤差用的是別的指標，兩者不能比",
        "不對。兩邊可以用完全相同的指標；差別在於<strong>算誤差的資料有沒有參與過配適</strong>，不在於指標。")])}
"""

# ── P01 validation ────────────────────────────────────────────────────
_val_code = lab_code(CH, 16) + "\n\n" + lab_code(CH, 20)
_val_out = lab_output(CH, 20)

BODIES["validation"] = f"""
  <p>最直接的做法：把資料隨機切成兩半，一半訓練、一半當<strong>驗證集</strong>（validation set，
  也叫 hold-out set）。模型完全沒看過驗證集，所以驗證集上的 MSE 就是一個誠實的測試誤差估計：</p>

  $$\\mathrm{{MSE}}_{{\\text{{valid}}}} = \\frac{{1}}{{|V|}} \\sum_{{i \\in V}} \\left(y_i - \\hat f(x_i)\\right)^2$$

  <p>講義用 <code>Auto</code> 資料（n = 392）示範：把 196 筆拿去訓練、196 筆當驗證集，
  用 <code>horsepower</code> 預測 <code>mpg</code>。看起來很乾淨——問題是<strong>換一個切法，答案就變了</strong>。</p>

{viz(chart("w05valChart", "tall", "。此圖的重點：十種不同的隨機切分，畫出來是十條差很多的曲線——驗證集法的答案取決於你剛好怎麼切。"),
     [info_card("怎麼看這張圖",
                '每條淡線是一次隨機切分（<code>test_size=196</code>）算出的驗證 MSE，'
                'x 軸是 <code>horsepower</code> 多項式的次數。粗線是十次的平均。'
                '<strong>十條線的高低差距，就是驗證集法的變異。</strong>', "圖 5.2 右"),
      rows_card("十次切分的落點（degree 2）",
                [("最低", "—", "w05valLo"), ("最高", "—", "w05valHi"),
                 ("全距", "—", "w05valRange"), ("平均", "—", "w05valMean")]),
      info_card("結論",
                '每一條都會告訴你「二次比一次好」——這個結論很穩。但如果你想引用一個'
                '<strong>具體數字</strong>當測試 MSE，那個數字非常不可靠。')],
     "w05valStatus", "按「顯示十次切分」看同一份資料在不同切法下的驗證 MSE。",
     '<button class="btn btn-play" onclick="w05valToggle(true)">▶ 顯示十次切分</button>'
     '<button class="btn btn-reset" onclick="w05valToggle(false)">只看平均</button>')}

  <h3 id="dx-val">講義完整實作：切一半、配模型、算驗證 MSE</h3>
{card("講義 05 · 驗證集法（Auto，degree 1）", _val_code, _val_out,
      src=src("16、20"),
      note="這個 <strong>25.57</strong> 就是課本 §5.1.1 引用的數字。注意 <code>random_state=rng</code>"
           "——換掉它，下面的數字就會不一樣。")}

{card("講義 05 · 換一個切法（random_state=3）", lab_code(CH, 28), lab_output(CH, 28),
      src=src("26、28"),
      note="degree 1／2／3 的驗證 MSE 從 <code>[25.57, 22.22, 22.67]</code> 變成 "
           "<code>[20.76, 16.95, 16.97]</code>。<strong>同一份資料、同一個模型，只是切法不同，"
           "數字差了快 5。</strong>但兩次都指向同一個結論：二次比一次好，三次沒有再更好。")}

{qa("觀念釐清", [
    ("Q：驗證集法為什麼會「高估」測試誤差？",
     "<p>因為它只用了一半的資料訓練。統計模型通常餵愈多資料表現愈好，"
     "所以用 n/2 筆訓練出來的模型，本來就比用全部 n 筆訓練出來的差。"
     "你量到的是「一個比較弱的模型」的誤差，因此系統性偏高。</p>"
     "<p>這是驗證集法的兩個缺點之一。另一個是變異太大（就是上面那張圖）。"
     "交叉驗證同時改善了這兩點：每一輪都用 n(k−1)/k 筆訓練（比 n/2 多），"
     "而且做 k 輪再平均（變異變小）。</p>"),
    ("Q：那 <code>random_state</code> 到底該不該固定？",
     "<p>該固定，但理由是<strong>可重現</strong>，不是「這個 seed 比較好」。"
     "固定 seed 讓你（和讀你程式的人）能重跑出同樣的數字。</p>"
     "<p>危險的做法是「試幾個 seed，挑數字最漂亮的那個報出來」——那等於用驗證集調參，"
     "報出來的誤差就不再誠實了。要降低這種隨機性的影響，正解是改用 k-fold CV，"
     "不是換 seed。</p>"),
])}

{quiz("qVal", "QUIZ · 驗證集法",
      "驗證集法有兩個公認的缺點。下面哪一組說對了？",
      [(True, "① 估計值變異大（換切法就變）② 只用一半資料訓練，所以高估測試誤差",
        "對。ISLP §5.1.1 講的就是這兩點，而 k-fold CV 兩點都改善了。"),
       (False, "① 計算量太大 ② 只能用在迴歸，不能用在分類",
        "都不對。驗證集法是這幾種方法裡<strong>最省算力</strong>的（只配一次模型）；而它把 MSE 換成錯誤率就能用在分類。"),
       (False, "① 會用到測試資料的資訊 ② 需要假設誤差是常態分佈",
        "都不對。驗證集完全沒參與配適，所以沒有洩漏；而且整套做法不需要任何分佈假設——這正是重抽樣方法的優點。")])}
"""

# ── P02 LOOCV ─────────────────────────────────────────────────────────
BODIES["loocv"] = f"""
  <p>驗證集法浪費了一半的資料，而且答案會跳。把它推到極端：
  <strong>每次只留一個樣本當驗證集</strong>，其餘 n − 1 筆全部拿去訓練，做 n 次再平均。
  這就是留一交叉驗證（leave-one-out cross-validation, LOOCV）：</p>

  $$\\mathrm{{CV}}_{{(n)}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} \\mathrm{{MSE}}_i,
    \\qquad \\mathrm{{MSE}}_i = \\left(y_i - \\hat f^{{(-i)}}(x_i)\\right)^2$$

  <p>其中 $\\hat f^{{(-i)}}$ 是「拿掉第 i 筆」配出來的模型。這樣做有兩個好處：
  每一輪都用了幾乎全部的資料（偏差很小），而且<strong>分割方式唯一</strong>——沒有隨機性，
  跑一百次都是同一個數字。</p>

{viz(svg("w05looSvg", 300),
     [info_card("虛擬碼", '<div class="pseudo-code" id="w05looCode" style="font-size:.74rem;">'
                '<span class="line" data-l="1">total = 0</span>\n'
                '<span class="line" data-l="2"><span class="kw">for</span> i <span class="kw">in</span> <span class="kw">range</span>(n):</span>\n'
                '<span class="line" data-l="3">    留下第 i 筆，其餘訓練</span>\n'
                '<span class="line" data-l="4">    total += (y[i] - 預測)**<span class="num">2</span></span>\n'
                '<span class="line" data-l="5">CV = total / n</span></div>', "CODE"),
      rows_card("目前進度",
                [("第幾輪", "0 / 12", "w05looRound"), ("這輪的平方誤差", "—", "w05looErr"),
                 ("累計平均 CV", "—", "w05looCV")]),
      info_card("為什麼沒有隨機性",
                '「留第 1 筆」「留第 2 筆」…「留第 n 筆」——這 n 種分割是<strong>枚舉</strong>出來的，'
                '不是抽出來的。所以 LOOCV 沒有 <code>random_state</code> 可以調。')],
     "w05looStatus", "按「開始」逐筆留一：橘色是這一輪被留下來驗證的點，虛線是用其餘 11 筆配出的迴歸線。",
     '<button class="btn btn-play" onclick="w05looStart()">▶ 開始</button>'
     '<button class="btn btn-step" onclick="w05looPlayer &amp;&amp; w05looPlayer.step()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w05looReset()">重置</button>')}

  <h3 id="dx-loo">講義完整實作：用 <code>cross_validate</code> 跑 LOOCV</h3>
{card("講義 05 · LOOCV（Auto，degree 1）",
      lab_code(CH, 32), lab_output(CH, 32), src=src("32"),
      note="<strong>24.2315</strong> 就是 degree 1 的 LOOCV 估計。"
           "跟上面驗證集法的 25.57／20.76 比一比：LOOCV 只有一個答案，不會因為切法而跳。")}

{info("最小平方法有捷徑，不必真的配 n 次", '''對線性或多項式的最小平方擬合，LOOCV 有封閉解（ISLP 式 5.2）：<br>
  $$\\mathrm{CV}_{(n)} = \\frac{1}{n}\\sum_{i=1}^{n}\\left(\\frac{y_i - \\hat y_i}{1 - h_i}\\right)^2$$
  只要配<strong>一次</strong>模型，拿殘差跟槓桿值 $h_i$ 就算得出來。<br>
  但注意：<code>scikit-learn</code> 的通用 <code>cross_validate()</code> 沒有用這個公式，
  所以 lab 裡跑 LOOCV 還是慢——這是實作的事，不是理論的事。''', "warm")}

{qa("觀念釐清", [
    ("Q：LOOCV 的偏差最小，為什麼還不是首選？",
     "<p>因為它的<strong>變異</strong>偏大。LOOCV 平均的那 n 個 $\\mathrm{MSE}_i$ 彼此高度相關——"
     "任兩輪的訓練集有 n − 2 筆是重疊的，所以配出來的模型幾乎一樣。"
     "把 n 個高度相關的數字平均，並不會像平均 n 個獨立數字那樣有效地降低變異。</p>"
     "<p>k-fold（k = 5 或 10）的訓練集重疊程度低得多，各折之間比較不相關，"
     "所以平均起來變異較小。代價是每輪少用一點資料，偏差稍微大一些——這就是 k 的取捨。</p>"),
    ("Q：LOOCV 算出來的 24.23，是在估「哪個」模型的測試誤差？",
     "<p>嚴格說，它估的是「用 n − 1 筆資料訓練出來的模型」的期望測試誤差，"
     "但因為 n − 1 跟 n 幾乎一樣，實務上直接把它當成「用全部 n 筆訓練出來的那個模型」的測試誤差。</p>"
     "<p>這也是為什麼 CV 的最後一步通常是：<strong>用 CV 選出超參數（例如次數 = 2），"
     "然後用全部資料重配一次</strong>，交出那個模型。CV 的角色是選，不是產出最終模型。</p>"),
])}

{quiz("qLoo", "QUIZ · LOOCV",
      "同一份資料上，把 LOOCV 跑兩次，會得到一樣的答案嗎？",
      [(True, "會，因為 n 種「留一」分割是枚舉出來的，沒有隨機性",
        "對。這是 LOOCV 相對於驗證集法與 k-fold 的一個明確優點：結果完全可重現，沒有 seed 要煩。"),
       (False, "不會，因為每輪的訓練集不同，隨機性會累積",
        "不對。每輪的訓練集確實不同，但那是<strong>固定</strong>的 n 種分割（第 1 輪必定留第 1 筆），不是隨機抽的。"),
       (False, "不一定，取決於有沒有設 random_state",
        "不對。LOOCV 沒有 <code>random_state</code> 可以設——<code>LeaveOneOut()</code> 不接受這個參數，因為它不需要。")])}
"""

# ── P03 k-fold ────────────────────────────────────────────────────────
BODIES["kfold"] = f"""
  <p>LOOCV 要配 n 次模型，n 大就吃不消。折衷方案：把資料<strong>隨機平分成 k 份</strong>，
  每次拿一份當驗證集、其餘 k − 1 份訓練，做 k 輪再平均。這就是 <em>k</em>-fold 交叉驗證：</p>

  $$\\mathrm{{CV}}_{{(k)}} = \\frac{{1}}{{k}} \\sum_{{j=1}}^{{k}} \\mathrm{{MSE}}_j$$

  <p>LOOCV 其實就是 k = n 的特例。實務上 k 取 5 或 10——原因下一節講。</p>

{viz(svg("w05foldSvg", 260),
     [info_card("怎麼看",
                '左邊用 20 顆球示意切法：<span style="color:var(--pt-held);font-weight:700;">橘色</span>'
                '是這一輪被留下來驗證的那一折，深藍是訓練用的部分。'
                '右邊是<strong>同一個 k 在 Auto（n = 392, degree 2）上真的跑出來</strong>的每折 MSE。'),
      rows_card("這一輪",
                [("k", "5", "w05foldK"), ("第幾折", "0 / 5", "w05foldRound"),
                 ("訓練 / 驗證筆數", "—", "w05foldN"),
                 ("這折的 MSE（Auto）", "—", "w05foldMse"),
                 ("累計平均", "—", "w05foldAvg")]),
      info_card("每折 MSE 差很多，這正常嗎",
                '正常。上面五折的 MSE 從 13 跳到 24——每折只有 78 筆，'
                '本來就不穩。<strong>CV 的價值在平均，不在單一折。</strong>')],
     "w05foldStatus", "選 k 之後按「開始」，看每一折輪流當驗證集。",
     '<label class="slider-label" style="margin-right:.4rem;">k =</label>'
     '<select id="w05foldSel" class="mono" onchange="w05foldSetK()">'
     '<option value="2">2</option><option value="5" selected>5</option>'
     '<option value="10">10</option></select>'
     '<button class="btn btn-play" onclick="w05foldStart()">▶ 開始</button>'
     '<button class="btn btn-step" onclick="w05foldPlayer &amp;&amp; w05foldPlayer.step()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w05foldReset()">重置</button>')}

  <h3 id="dx-kf">講義完整實作：<code>KFold</code> 跑 10-fold</h3>
{card("講義 05 · 10-fold CV（degree 1–5）", lab_code(CH, 41), None, src=src("41"),
      note="<code>shuffle=True</code> 很重要：如果原始資料有排序（例如 <code>Auto</code> 按年份），"
           "不打亂就會讓每一折的分佈完全不同。<code>random_state=0</code> 是為了"
           "<strong>讓不同 degree 用同一組分割</strong>——這樣比較才公平。"
           "這格 lab 沒存下輸出，下一節的圖用同樣設定重算了一次。")}

{quiz("qKf", "QUIZ · k-fold",
      "比較不同模型（例如 degree 1 到 10）的 CV 誤差時，為什麼要讓每個模型用<strong>同一組</strong>折分割？",
      [(True, "否則模型之間的差異會混進「分割不同」造成的雜訊，可能比模型本身的差異還大",
        "對。這是 <code>random_state=0</code> 的用意。不然你比到的是「degree 2 加上運氣好的分割」對上「degree 3 加上運氣差的分割」。"),
       (False, "因為 scikit-learn 要求 cv 物件必須重複使用",
        "不對，<code>cross_validate</code> 每次呼叫都可以給不同的 cv 物件。這是統計上的講究，不是 API 的限制。"),
       (False, "因為用不同分割會讓 CV 誤差變成有偏估計",
        "不對。用不同分割每個模型的 CV 誤差仍然是各自無偏的；問題出在<strong>比較</strong>時多了不必要的變異，不是偏差。")])}
"""

# ── P04 k 該取多少 ─────────────────────────────────────────────────────
BODIES["kbias"] = f"""
  <p>k 該取多少？兩個方向在拉扯：</p>

  <ul>
    <li><strong>k 愈大 → 偏差愈小。</strong>每輪的訓練集有 n(k−1)/k 筆，k = n 時幾乎用了全部資料，
    所以估出來的誤差最貼近「用全部資料訓練」的真實測試誤差。k = 2 只用一半，會高估。</li>
    <li><strong>k 愈大 → 變異愈大。</strong>k 愈大，各折的訓練集重疊愈多、模型愈像、
    k 個 MSE 之間愈相關，平均起來降變異的效果愈差。</li>
  </ul>

  <p>ISLP §5.1.4 的結論是：<strong>k = 5 或 k = 10 是偏差與變異都可接受的折衷</strong>，
  而且計算量只有 LOOCV 的 5/n 或 10/n。下面這張圖是 <code>Auto</code> 上的實測：</p>

{viz(chart("w05cvChart", "tall", "。此圖的重點：從 degree 1 到 2，CV 誤差從 24.2 掉到 19.2；之後就平了。LOOCV 與 10-fold 的曲線幾乎重疊。"),
     [info_card("怎麼看這張圖",
                'x 軸是 <code>horsepower</code> 多項式的次數，y 軸是 CV 估的測試 MSE。'
                '兩條線分別是 LOOCV 與 10-fold CV。<strong>兩條幾乎重疊</strong>——'
                '這在實務上很常見，也是大家願意用便宜的 10-fold 取代 LOOCV 的理由。', "圖 5.4"),
      rows_card("最低點",
                [("LOOCV 最小", "—", "w05cvLoo"), ("10-fold 最小", "—", "w05cvKf"),
                 ("兩者最大差距", "—", "w05cvGap")]),
      info_card("讀圖的重點",
                '不要只看「哪個 degree 的數字最小」。degree 5 的 CV 誤差是 19.03、degree 2 是 19.25，'
                '差 0.2——這遠在雜訊範圍內。<strong>看的是曲線在哪裡「拉平」</strong>，'
                '拉平之後就選最簡單的那個。')],
     "w05cvStatus", "LOOCV 與 10-fold CV 在同一份 Auto 資料上的比較。",
     '<button class="btn btn-toggle" onclick="w05cvToggleLog()">切換 y 軸縮放</button>')}

{table(["k", "每輪訓練用", "偏差", "變異", "配模型次數", "評語"],
       [["2", "n/2", "最大（高估）", "最小", "2", "太粗，很少用"],
        ["5", "0.8 n", "小", "小", "5", "實務常用"],
        ["10", "0.9 n", "更小", "略大", "10", "實務最常用"],
        ["n（LOOCV）", "n − 1", "最小", "最大", "n", "小資料、或有式 5.2 捷徑時"]])}

{qa("觀念釐清", [
    ("Q：「k 愈大變異愈大」聽起來很反直覺——平均更多項不是應該更穩嗎？",
     "<p>平均更多項會更穩，<strong>前提是那些項彼此獨立</strong>。這裡不是。</p>"
     "<p>算式上看：$\\mathrm{Var}(\\bar X) = \\frac{\\sigma^2}{k} + \\frac{k-1}{k}\\rho\\sigma^2$。"
     "第一項隨 k 變大而變小，但第二項隨 $\\rho$（各折之間的相關）變大而變大。"
     "LOOCV 的 $\\rho$ 接近 1，第二項就吃掉了第一項的好處。</p>"
     "<p>直覺版：LOOCV 的 n 個模型幾乎是同一個模型，所以你其實只有「一個」意見被重複算了 n 次。</p>"),
    ("Q：跑 CV 之前要不要標準化？在哪一步做？",
     "<p>要，而且<strong>必須在每一折裡面做</strong>：用該折的訓練部分算平均與標準差，再套到驗證部分。</p>"
     "<p>如果先用全部資料標準化再切折，驗證資料的平均與標準差就洩漏進訓練流程了，"
     "CV 誤差會偏低。<code>scikit-learn</code> 的正解是把標準化包進 "
     "<code>Pipeline</code>，再把整個 pipeline 丟給 <code>cross_validate</code>——"
     "它會自動在每折內重新 fit。這跟下一節的錯誤是同一個病。</p>"),
])}

{quiz("qK", "QUIZ · k 的取捨",
      "為什麼實務上不直接用偏差最小的 LOOCV，而多半選 k = 5 或 10？",
      [(True, "LOOCV 的各折高度相關，平均後變異較大；而且要配 n 次模型",
        "對。偏差、變異、算力三者的折衷，5 或 10 在三個面向上都可接受。"),
       (False, "因為 LOOCV 會用到驗證資料的資訊，估計不誠實",
        "不對。LOOCV 每輪都完全不看被留下的那一筆，沒有洩漏問題。它的缺點是變異與算力，不是誠實度。"),
       (False, "因為 LOOCV 只能用在線性模型上",
        "不對。LOOCV 對任何模型都能做（只是慢）。<em>有捷徑公式</em>（式 5.2）的才限線性最小平方，那是加速手段，不是適用範圍。")])}
"""

# ── P05 分類上的 CV ────────────────────────────────────────────────────
BODIES["cvclass"] = f"""
  <p>整套邏輯搬到分類問題只要換一件事：把 MSE 換成<strong>錯誤率</strong>。</p>

  $$\\mathrm{{CV}}_{{(k)}} = \\frac{{1}}{{k}} \\sum_{{j=1}}^{{k}} \\mathrm{{Err}}_j,
    \\qquad \\mathrm{{Err}}_j = \\frac{{1}}{{|C_j|}} \\sum_{{i \\in C_j}} I(y_i \\neq \\hat y_i)$$

  <p>$I(\\cdot)$ 是指示函數：預測錯就是 1、對就是 0。其餘完全一樣：切 k 折、輪流當驗證集、平均。
  ISLP 圖 5.7–5.8 用邏輯斯迴歸加上不同次數的多項式項示範，
  CV 誤差率確實會在「真正的邊界複雜度」附近最低。</p>

{info("實務上要注意的三件事", '''<strong>1. 類別不平衡就要分層：</strong>用
  <code>StratifiedKFold</code>，讓每一折的類別比例跟整體一致。類別很少的時候，
  普通 <code>KFold</code> 可能切出「某一折完全沒有正例」的荒謬情況。<br>
  <strong>2. 錯誤率不一定是你要的指標：</strong>正例只佔 1% 時，全部猜負例就有 99% 正確率。
  改用 AUC、F1 或 recall，作法完全相同——換掉 <code>scoring</code> 參數就好。<br>
  <strong>3. 資料有群組結構就要用 GroupKFold：</strong>同一個病人的多次就診、
  同一個使用者的多筆紀錄，不能一部分在訓練、一部分在驗證。''')}

{table(["情況", "該用的切分器", "為什麼"],
       [["一般迴歸／分類", "<code>KFold(shuffle=True)</code>", "最基本"],
        ["類別不平衡", "<code>StratifiedKFold</code>", "保住每折的類別比例"],
        ["同一實體有多筆資料", "<code>GroupKFold</code>", "同組資料不可跨訓練／驗證"],
        ["時間序列", "<code>TimeSeriesSplit</code>", "不能用未來預測過去"],
        ["只想快速看一眼", "<code>ShuffleSplit(n_splits=1)</code>", "等於驗證集法"]])}

{qa("觀念釐清", [
    ("Q：時間序列為什麼不能用普通的 k-fold？",
     "<p>因為隨機切折會讓「未來」的資料進到訓練集、「過去」的資料留在驗證集。"
     "模型於是可以用 2026 年的資訊去預測 2025 年——這在部署時根本不可能發生，"
     "所以 CV 誤差會嚴重低估真實表現。</p>"
     "<p>正解是<strong>只往前切</strong>（<code>TimeSeriesSplit</code>）："
     "用前 100 筆訓練、預測第 101–120 筆；再用前 120 筆訓練、預測第 121–140 筆…"
     "訓練集永遠在驗證集之前。</p>"),
])}

{quiz("qCls", "QUIZ · 分類上的 CV",
      "一份資料裡正例只佔 2%。用普通的 <code>KFold(n_splits=10)</code> 會有什麼風險？",
      [(True, "某些折可能幾乎（或完全）沒有正例，那一折的錯誤率就沒有意義",
        "對。這時要用 <code>StratifiedKFold</code> 保住每折的類別比例。順便一提，這種資料也不該只看錯誤率——全猜負例就有 98%。"),
       (False, "錯誤率的公式在不平衡資料上不成立，要改用 MSE",
        "不對。錯誤率的定義沒有任何問題，它照樣算得出來；問題是它<strong>不是個有用的指標</strong>，以及分割可能退化。改用 MSE 並不能解決任何一個。"),
       (False, "k 必須小於少數類別的樣本數，否則 CV 無法執行",
        "不對。程式跑得起來——這正是危險的地方：它不會報錯，只會安靜地給你一個沒有意義的數字。")])}
"""

# ── P06 CV 的對與錯 ────────────────────────────────────────────────────
BODIES["cvwrong"] = f"""
  <p>這一節是整章最容易在實務上出錯、而且錯了不會有任何錯誤訊息的地方。</p>

  <p>常見情境：手上有 p = 500 個特徵、n = 50 筆資料。你先算每個特徵跟 y 的相關係數，
  挑出最相關的 10 個，然後對這 10 個特徵做 5-fold CV，得到一個漂亮的誤差率。
  <strong>這個數字是假的。</strong></p>

  <p>問題在於「挑特徵」這一步<strong>看過了全部的 y</strong>，包含後來被當成驗證資料的那些。
  篩選本身就是模型訓練的一部分，它必須關在每一折裡面做。</p>

{viz(chart("w05misChart", "square", "。此圖的重點：資料是純噪音（y 與 X 完全獨立），正確做法給出約 0.5 的錯誤率，錯誤做法卻只有 0.26。"),
     [info_card("這個模擬在做什麼",
                'n = 50、p = 500 的<strong>純噪音</strong>資料：y 是丟硬幣決定的，'
                '跟每一個 X 都完全無關。所以任何誠實的方法都該回報「錯誤率約 50%，'
                '這些特徵沒用」。', "ISLP §5.1.4"),
      rows_card("兩種做法",
                [("先選特徵再 CV（錯）", "—", "w05misWrong"),
                 ("在每折內選特徵（對）", "—", "w05misRight"),
                 ("誠實的答案應該是", "0.50", "w05misTruth")]),
      info_card("為什麼差這麼多",
                '從 500 個純噪音特徵裡挑「最相關的 10 個」，一定挑得到幾個'
                '<em>剛好</em>跟這 50 筆 y 對得上的。那個「剛好」也包含了驗證折的 y——'
                '模型於是在驗證資料上作弊。')],
     "w05misStatus", "同一份純噪音資料，兩種 CV 流程的結果。",
     '<button class="btn btn-play" onclick="w05misShow()">▶ 顯示結果</button>')}

{info("一句話原則", '''凡是<strong>用到 y 的步驟</strong>——特徵篩選、標準化的平均與標準差、
  缺失值填補、過抽樣、目標編碼、PCA 降維——都必須<strong>關在每一折的訓練部分裡面做</strong>。
  在 <code>scikit-learn</code> 裡，把它們串成 <code>Pipeline</code> 再交給
  <code>cross_validate</code>，這件事就自動對了。''', "warm")}

{qa("觀念釐清", [
    ("Q：只用 X 不看 y 的前處理（例如 PCA、去除零變異特徵），也要關在折裡嗎？",
     "<p>嚴格說要，實務上影響小得多。</p>"
     "<p>不看 y 的前處理不會直接把答案洩漏進來，所以偏差通常很輕微。"
     "但它仍然用到了驗證資料的<strong>分佈</strong>資訊（PCA 的方向、特徵的變異數），"
     "而在部署時你不可能先看過未來資料的分佈。既然包進 <code>Pipeline</code> 幾乎沒有額外成本，"
     "就一律包進去，不必去分辨哪種洩漏比較嚴重。</p>"),
    ("Q：我用 CV 選超參數，那 CV 誤差可以當成最終模型的測試誤差報出來嗎？",
     "<p>不太行，它會偏低。你已經拿 CV 誤差當目標挑過超參數了——"
     "被挑中的那組本來就是「在這組折上運氣最好」的那組，這叫做選擇偏差。</p>"
     "<p>要誠實的估計，用<strong>嵌套交叉驗證</strong>（nested CV）："
     "外層折只負責評估、完全不參與調參；內層折在外層的訓練部分裡調參。"
     "或者更簡單：一開始就切出一份從頭到尾沒碰過的測試集。</p>"),
])}

{quiz("qWrong", "QUIZ · CV 的錯用",
      "在 5-fold CV 之前先用<strong>全部</strong>資料把特徵標準化（減平均、除標準差）。這樣有問題嗎？",
      [(True, "有問題：平均與標準差用到了驗證折的資料，屬於洩漏，CV 誤差會偏低",
        "對。正解是把 <code>StandardScaler</code> 放進 <code>Pipeline</code>，讓它在每折的訓練部分重新 fit。這個偏差通常比「先選特徵」小，但方向一樣。"),
       (False, "沒問題：標準化只是線性變換，不改變模型的預測能力",
        "不對。對<em>單一次</em>配適來說它確實只是換單位；但這裡的問題不在變換本身，而在<strong>參數（平均、標準差）是從包含驗證資料的集合算出來的</strong>。"),
       (False, "沒問題：標準化沒有用到 y，所以不算洩漏",
        "方向對了一半。沒用到 y 讓偏差小很多，但仍然用了驗證資料的分佈資訊。既然包進 Pipeline 沒有成本，就不要留這個破口。")])}
"""

# ── P07 Bootstrap ─────────────────────────────────────────────────────
BODIES["bootstrap"] = f"""
  <p>換一個問題。前面都在問「模型的預測有多準」；現在問<strong>「我算出來的這個數字有多不確定」</strong>。</p>

  <p>ISLP §5.2 的例子：把錢分成比例 α 投資 X、1 − α 投資 Y，要讓報酬的變異最小，最佳比例是</p>

  $$\\alpha = \\frac{{\\sigma_Y^2 - \\sigma_{{XY}}}}{{\\sigma_X^2 + \\sigma_Y^2 - 2\\sigma_{{XY}}}}$$

  <p>把樣本變異數代進去就得到 $\\hat\\alpha$。但 $\\hat\\alpha$ 有多可靠？
  它的標準誤沒有簡單的公式可查。理想上我們會重新蒐集 1000 份新資料、算 1000 個 $\\hat\\alpha$、
  看它們的標準差——但我們只有一份資料。</p>

  <p><strong>Bootstrap 的把戲：把手上這份資料當成母體，從裡面有放回地抽 n 筆</strong>，
  當成一份「新」資料集，重算 $\\hat\\alpha^*$。重複 B 次，那 B 個 $\\hat\\alpha^*$ 的標準差
  就是 $\\mathrm{{SE}}(\\hat\\alpha)$ 的估計。不需要任何分佈假設，也不需要推導。</p>

{viz(svg("w05bootSvg", 210) + "\n" + chart("w05bootChart", "", "。此圖的重點：1000 次 bootstrap 重抽算出的 α̂* 分佈，它的標準差 0.0912 就是 SE(α̂) 的估計。"),
     [info_card("虛擬碼", '<div class="pseudo-code" id="w05bootCode" style="font-size:.74rem;">'
                '<span class="line" data-l="1"><span class="kw">for</span> b <span class="kw">in</span> <span class="kw">range</span>(B):</span>\n'
                '<span class="line" data-l="2">    idx = 有放回抽 n 個</span>\n'
                '<span class="line" data-l="3">    θ*[b] = f(資料[idx])</span>\n'
                '<span class="line" data-l="4">SE = std(θ*)</span></div>', "CODE"),
      rows_card("這一次重抽",
                [("抽到的樣本", "—", "w05bootDraw"),
                 ("沒被抽到（OOB）", "—", "w05bootOob"),
                 ("這次的樣本平均 θ̂*", "—", "w05bootStat"),
                 ("累計 B", "0", "w05bootB"),
                 ("累計 SE", "—", "w05bootSE")]),
      info_card("Portfolio 的真實結果",
                '用全部 100 筆算：α̂ = <strong>0.5758</strong>。跑 B = 1000 次 bootstrap 後，'
                'SE(α̂) = <strong>0.0912</strong>。下面的 lab 卡片有逐字輸出。', "ISLP §5.2")],
     "w05bootStatus", "按「單步」看一次有放回重抽：實心＝被抽到（可能重複），空心虛線＝這次沒被抽到。",
     '<button class="btn btn-step" onclick="w05bootDrawOne()">→ 抽一次</button>'
     '<button class="btn btn-play" onclick="w05bootMany()">▶ 連抽 200 次</button>'
     '<button class="btn btn-reset" onclick="w05bootReset()">重置</button>')}

  <h3 id="dx-boot">講義完整實作：<code>boot_SE()</code></h3>
{card("講義 05 · α̂ 用全部 100 筆", lab_code(CH, 55), lab_output(CH, 55), src=src("53、55"),
      note="這就是 ISLP 書上的 α̂ = 0.5758。")}

{card("講義 05 · 一次 bootstrap 重抽", lab_code(CH, 57), lab_output(CH, 57), src=src("57"),
      note="<code>replace=True</code> 是關鍵：有放回，所以同一筆可能被抽到好幾次，"
           "也會有一些完全沒被抽到。這一次抽出來的 α̂* = 0.6074，跟 0.5758 差了不少——"
           "這個「差」正是我們要量化的東西。")}

{card("講義 05 · 通用的 boot_SE", lab_code(CH, 59), None, src=src("59、61"),
      note="lab 的第 62 格寫著：SE(α̂) 的 bootstrap 估計是 <strong>0.0912</strong>。"
           "注意這支函式用 $E[\\theta^2] - (E[\\theta])^2$ 累加，不必存下 1000 個值。")}

  <h4 id="dx-632">一個漂亮的事實：bootstrap 樣本只含約 63.2% 的原始樣本</h4>
  <p>有放回地抽 n 次，某一筆<strong>始終沒被抽到</strong>的機率是 $\\left(1 - \\frac{{1}}{{n}}\\right)^n$。
  n 一大，這個數趨近 $e^{{-1}} \\approx 0.368$。所以</p>

  $$P(\\text{{第 }} i \\text{{ 筆有進 bootstrap 樣本}}) = 1 - \\left(1-\\frac{{1}}{{n}}\\right)^n
    \\;\\xrightarrow[n \\to \\infty]{{}}\\; 1 - e^{{-1}} \\approx 0.632$$

  <p>剩下那 36.8% 沒被抽到的樣本叫做 <strong>out-of-bag</strong>（OOB）。
  它們對這一輪的模型來說是天然的驗證集——第 9 章的 bagging 與 random forest 就靠這招
  免費拿到測試誤差估計。</p>

{viz(chart("w05p632Chart", "", "。此圖的重點：理論曲線 1−(1−1/n)ⁿ 從 n=2 的 0.75 很快收斂到 0.632，模擬點落在曲線上。"),
     [info_card("怎麼看",
                '藍線是理論值 $1-(1-1/n)^n$，紅點是每個 n 各跑 2000 次模擬的實測比例。'
                '<strong>收斂得非常快</strong>：n = 20 就已經是 0.642 了。'),
      rows_card("查表",
                [("n = 5", "—", "w05p632n5"), ("n = 20", "—", "w05p632n20"),
                 ("n = 100", "—", "w05p632n100"), ("極限 1 − 1/e", "0.6321", "w05p632lim")]),
      info_card("這個 0.632 會再出現",
                '第 9 章的 OOB 誤差、以及文獻裡的 .632 bootstrap 估計量，'
                '都是從這個事實長出來的。')],
     "w05p632Status", "有放回抽 n 次，某一筆至少被抽到一次的機率。",
     '<button class="btn btn-play" onclick="w05p632Run()">▶ 跑模擬</button>')}

{qa("觀念釐清", [
    ("Q：Bootstrap 可以用來估「預測誤差」嗎？",
     "<p>可以，但要很小心，而且通常比不上交叉驗證。</p>"
     "<p>問題出在重疊：bootstrap 樣本平均含有原始資料的 63.2%，"
     "所以如果你用 bootstrap 樣本訓練、用原始全部資料當測試，"
     "那個「測試集」裡有三分之二的資料模型已經看過了，誤差會嚴重低估。</p>"
     "<p>補救方式是只用 OOB 的那 36.8% 來評估，這就接近 k-fold 的精神了。"
     "所以講義第 36 頁的答案是：<strong>估標準誤用 bootstrap，估預測誤差用交叉驗證。</strong></p>"),
    ("Q：B 要取多少？",
     "<p>估標準誤時 B = 1000 通常就很夠；要估信賴區間的尾端分位數（例如 2.5% 與 97.5%），"
     "B 建議拉到 2000 以上，因為尾端需要更多樣本才穩。</p>"
     "<p>注意 B 大只會讓「bootstrap 對真實 SE 的估計」更穩定，"
     "<strong>不會讓原始資料變多</strong>。n 小的時候 bootstrap 本身就不可靠，"
     "拉高 B 也救不了——它只是把同一份薄薄的資訊算得更精確而已。</p>"),
    ("Q：bootstrap 什麼時候會失效？",
     "<p>幾個典型的坑：</p><ul>"
     "<li><strong>估計量依賴極值</strong>（最大值、最小值、全距）：bootstrap 樣本的最大值"
     "永遠不會超過原始資料的最大值，所以分佈會被截斷。</li>"
     "<li><strong>資料不獨立</strong>（時間序列、空間資料、群組結構）：直接對單筆有放回重抽會"
     "破壞相關結構。要改用 block bootstrap。</li>"
     "<li><strong>n 很小</strong>：把 10 筆資料當母體，本來就沒什麼可抽的。</li></ul>"),
])}

{quiz("qBoot", "QUIZ · Bootstrap",
      "n = 100 時，一筆特定的觀測值<strong>完全沒有</strong>出現在某個 bootstrap 樣本裡的機率約為多少？",
      [(True, "約 0.366",
        "對。$(1-1/100)^{100} \\approx 0.366$，很接近極限 $e^{-1} \\approx 0.368$。沒被抽到的那些就是 OOB 樣本。"),
       (False, "約 0.01",
        "這是「某一次抽籤剛好抽到它」的機率 1/100，不是「一百次都沒抽到」。要一百次都躲掉，是 $(1-1/100)^{100}$。"),
       (False, "0，因為有放回抽 n 次一定會抽到每一筆",
        "不對。有放回意味著同一筆可以被抽到好幾次，也就意味著<strong>一定有一些筆完全沒被抽到</strong>——平均約 36.8%。")])}
"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 5.4 第 2 題（a)(b)",
      "從 n 筆資料中<strong>有放回</strong>地抽第一筆時，抽到的<em>不是</em>第 j 筆觀測值的機率是多少？"
      "第二筆呢？",
      [(True, "兩次都是 (n−1)/n",
        "對。有放回意味著每一次抽籤的條件都一樣（獨立且同分佈），所以第 1 次與第 2 次的機率完全相同。這正是第 (c) 小題能把它們乘起來變成 $(1-1/n)^n$ 的理由。"),
       (False, "第一次 (n−1)/n，第二次 (n−2)/(n−1)",
        "這是<strong>不</strong>放回的答案。抽出不放回時母體會縮小，機率才會變。bootstrap 是有放回的。"),
       (False, "第一次 1/n，第二次 1/n",
        "這是「抽到第 j 筆」的機率，題目問的是「<em>不是</em>第 j 筆」，要取補集。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 5.4 第 3 題（b)",
      "相對於<strong>驗證集法</strong>，k-fold CV 的優點是什麼？",
      [(True, "偏差較小（每輪用 n(k−1)/k 筆訓練，多於 n/2），而且做 k 輪平均後變異也較小",
        "對，兩個缺點都改善了。代價只是要配 k 次模型而不是 1 次。"),
       (False, "k-fold CV 完全沒有隨機性，驗證集法有",
        "不對，這是 <strong>LOOCV</strong> 的性質。k-fold 要隨機分折，換 <code>random_state</code> 答案還是會動——只是幅度比驗證集法小很多。"),
       (False, "k-fold CV 不需要把資料切開，所以能用到全部資料訓練",
        "不對。每一輪都還是切開的（k−1 折訓練、1 折驗證）。差別在於「每一筆資料都輪到當一次驗證資料」，不是「不用切」。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 5.4 第 8 題",
      "課本第 8 題在模擬資料上跑 degree 1 到 4 的 LOOCV，真實模型是二次的。"
      "預期會看到什麼？",
      [(True, "degree 1 到 2 誤差大幅下降，之後幾乎不再改善（甚至微幅上升）",
        "對。這也是本頁 P04 那張 Auto 圖的形狀：真實複雜度以下，加彈性有幫助；超過之後只是在配適噪音。"),
       (False, "誤差隨 degree 單調下降，degree 4 最低",
        "這是<strong>訓練</strong>誤差的形狀。CV 誤差是估測試誤差的，過了真實複雜度就不會再降。"),
       (False, "四個 degree 的 LOOCV 誤差幾乎相同，因為 LOOCV 對模型複雜度不敏感",
        "不對。CV 的整個用途就是偵測複雜度的影響；如果它不敏感，就沒有人會用它選模型了。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 5.4 第 9 題",
      "課本第 9 題要對 <code>Boston</code> 的 <code>medv</code> 平均值做 bootstrap，"
      "並跟公式解 $\\mathrm{{SE}}(\\bar\\mu) = s/\\sqrt{{n}}$ 比較。預期結果是？",
      [(True, "兩個數字會很接近，因為 bootstrap 不需要公式也能重現公式給的答案",
        "對。這一題的教學意義就在這裡：在<em>有</em>公式的簡單情況下驗證 bootstrap 是對的，這樣你才敢在<em>沒有</em>公式的情況（例如 α̂、中位數、分位數）放心用它。"),
       (False, "bootstrap 的 SE 會明顯較小，因為它重複用了同一份資料",
        "不對。重複使用資料不會讓 SE 系統性變小；bootstrap 估的就是同一個抽樣變異，兩者會很接近。"),
       (False, "無法比較，因為 bootstrap 只能用在迴歸係數上",
        "不對。bootstrap 幾乎對任何估計量都能用——這正是它最大的優點。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>四種方法對照</h3>
{table(["方法", "在估什麼", "偏差", "變異", "算力", "隨機性", "典型用途"],
       [["驗證集法", "測試誤差", "大（高估）", "大", "1×", "有，很大", "快速看一眼"],
        ["LOOCV", "測試誤差", "最小", "大", "n×", "無", "小資料、線性有捷徑"],
        ["<em>k</em>-fold CV", "測試誤差", "小", "小", "k×", "有，較小", "<strong>選模型的標準做法</strong>"],
        ["Bootstrap", "估計量的 SE", "—", "—", "B×", "有，B 大就穩", "<strong>估不確定性</strong>"]])}

  <h3>Auto 資料上的實測數字</h3>
{table(["degree", "1", "2", "3", "5", "10"],
       [["LOOCV", "24.23", "19.25", "19.34", "19.03", "19.91"],
        ["10-fold CV", "24.21", "19.19", "19.28", "19.14", "19.87"],
        ["驗證集（seed 0）", "23.62", "18.76", "18.80", "18.45", "19.07"]])}
  <p style="font-size:.82rem;color:var(--muted);">degree 1 的 LOOCV = 24.2315，跟 lab 儲存格 32
  的 <code>np.float64(24.23151351792922)</code> 相符。三列都在 degree 2 之後就拉平了。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["LOOCV", "$\\mathrm{CV}_{(n)} = \\frac1n\\sum_i \\mathrm{MSE}_i$", "式 5.1"],
        ["LOOCV 捷徑（最小平方）",
         "$\\frac1n\\sum_i\\left(\\frac{y_i-\\hat y_i}{1-h_i}\\right)^2$", "式 5.2，只配一次模型"],
        ["<em>k</em>-fold", "$\\mathrm{CV}_{(k)} = \\frac1k\\sum_j \\mathrm{MSE}_j$", "式 5.3"],
        ["分類版", "$\\mathrm{Err}_j = \\frac{1}{|C_j|}\\sum_{i\\in C_j} I(y_i \\ne \\hat y_i)$", "式 5.4"],
        ["最小變異配置", "$\\alpha = \\frac{\\sigma_Y^2-\\sigma_{XY}}{\\sigma_X^2+\\sigma_Y^2-2\\sigma_{XY}}$", "式 5.7"],
        ["在 bootstrap 樣本裡的機率", "$1-(1-1/n)^n \\to 1-e^{-1} \\approx 0.632$", "OOB 的來源"]])}

{info("三個一定要記住的觀念", '''<strong>1. 交叉驗證估「預測誤差」，bootstrap 估「估計量的不確定性」。</strong>
  兩者都在重抽樣，但問的問題不同，不要混用。<br>
  <strong>2. k = 5 或 10 是偏差、變異、算力三方的折衷。</strong>
  LOOCV 偏差最小但各折高度相關、變異大。<br>
  <strong>3. 任何用到 y 的步驟都要關在折裡面。</strong>
  特徵篩選、標準化、填補、過抽樣、目標編碼——包進 <code>Pipeline</code> 就對了。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
PAGEJS = r"""
/* ===== resampling_methods 本頁元件（id 與全域一律 w05 前綴）===== */

/* ---------- P01 驗證集法：十次切分的曲線 ---------- */
let w05valShowAll = true;
function w05valToggle(all) {
  w05valShowAll = all;
  w05valDraw();
  setStatus('w05valStatus', all
    ? '十條淡線是十種不同的隨機切分，粗線是平均。看它們散得多開。'
    : '只留下十次切分的平均。曲線形狀很穩，但單一切分的數值不穩。');
}
function w05valDraw() {
  const F = FRAMES_w05val, d = F.degrees;
  const mean = d.map((_, j) => F.curves.reduce((s, c) => s + c[j], 0) / F.curves.length);
  const sets = [];
  if (w05valShowAll) {
    F.curves.forEach((c, i) => sets.push({
      label: i === 0 ? '個別切分' : '_' + i, data: c, borderColor: 'rgba(44,62,122,.28)',
      borderWidth: 1.4, pointRadius: 0, fill: false,
    }));
  }
  sets.push({ label: '十次平均', data: mean, borderColor: HC.tok.accent, borderWidth: 3,
              pointRadius: 3, fill: false });
  HC.line('w05valChart', { labels: d, datasets: sets }, {
    plugins: {
      legend: { labels: { filter: it => !String(it.text).startsWith('_') } },
      tooltip: { filter: it => !String(it.dataset.label).startsWith('_') },
    },
    scales: { x: { title: { display: true, text: 'horsepower 多項式次數' } },
              y: { title: { display: true, text: '驗證集 MSE' } } },
  });
  const col = F.curves.map(c => c[1]);
  const lo = Math.min(...col), hi = Math.max(...col);
  $('w05valLo').textContent = HC.fmt(lo, 2);
  $('w05valHi').textContent = HC.fmt(hi, 2);
  $('w05valRange').textContent = HC.fmt(hi - lo, 2);
  $('w05valMean').textContent = HC.fmt(col.reduce((s, v) => s + v, 0) / col.length, 2);
}

/* ---------- P02 LOOCV：逐筆留一（真的即時配線） ---------- */
const w05looN = 12;
const w05looData = (() => {
  const rand = HC.stat.lcg(524), xs = [], ys = [];
  for (let i = 0; i < w05looN; i++) {
    const x = 1 + i * 0.75 + 0.18 * (rand() - 0.5);
    xs.push(x); ys.push(2.1 + 1.35 * x + 1.5 * HC.stat.normal(rand));
  }
  return { xs, ys };
})();
let w05looPlayer = null, w05looSvc = null;
function w05looSetup() {
  const { xs, ys } = w05looData;
  const pad = 1.2;
  w05looSvc = HC.svg('w05looSvg', {
    xd: [Math.min(...xs) - pad, Math.max(...xs) + pad],
    yd: [Math.min(...ys) - pad, Math.max(...ys) + pad], h: 300,
  });
  w05looSvc.grid(5, 4, { xtitle: 'x', ytitle: 'y', xdec: 0, ydec: 0 });
}
function w05looFrames() {
  const { xs, ys } = w05looData;
  const frames = [];
  let acc = 0;
  for (let i = 0; i < w05looN; i++) {
    const tx = xs.filter((_, j) => j !== i), ty = ys.filter((_, j) => j !== i);
    const f = HC.stat.ols(tx, ty);
    const pred = f.b0 + f.b1 * xs[i];
    const err = (ys[i] - pred) ** 2;
    acc += err;
    frames.push({ i, b0: f.b0, b1: f.b1, pred, err, cv: acc / (i + 1), line: 3 });
  }
  frames.push({ i: -1, done: true, cv: acc / w05looN, line: 5 });
  return frames;
}
function w05looApply(f) {
  const { xs, ys } = w05looData, s = w05looSvc;
  const g = s.clearLayer('pts');
  if (!f.done && f.i >= 0) {
    s.poly([[s.xd[0], f.b0 + f.b1 * s.xd[0]], [s.xd[1], f.b0 + f.b1 * s.xd[1]]],
           { cls: 'truef' }, g);
    s.seg(xs[f.i], ys[f.i], xs[f.i], f.pred, { cls: 'resid', sw: 2 }, g);
  }
  xs.forEach((x, j) => s.dot(x, ys[j], {
    r: j === f.i ? 6.5 : 4.2,
    fill: j === f.i ? HC.tok.held : HC.tok.train,
    stroke: '#fff', sw: 1.2,
  }, g));
  hlLine('w05looCode', f.line);
  if (f.done) {
    $('w05looRound').textContent = w05looN + ' / ' + w05looN;
    $('w05looErr').textContent = '—';
    $('w05looCV').textContent = HC.fmt(f.cv, 3);
    setStatus('w05looStatus', '十二輪跑完。CV 就是這 12 個平方誤差的平均：<strong>'
      + HC.fmt(f.cv, 3) + '</strong>。整個過程沒有用到任何隨機數。');
    return;
  }
  $('w05looRound').textContent = (f.i + 1) + ' / ' + w05looN;
  $('w05looErr').textContent = HC.fmt(f.err, 3);
  $('w05looCV').textContent = HC.fmt(f.cv, 3);
  setStatus('w05looStatus', '第 ' + (f.i + 1) + ' 輪：留下橘色那一點，用其餘 '
    + (w05looN - 1) + ' 點配線（虛線）。紫色線段是這一點的預測誤差，平方後 = '
    + HC.fmt(f.err, 3) + '。');
}
function w05looStart() {
  w05looPlayer = new Player({ frames: w05looFrames(), apply: w05looApply });
  w05looPlayer.reset(); w05looPlayer.play();
}
function w05looReset() {
  if (w05looPlayer) w05looPlayer.stop();
  w05looPlayer = new Player({ frames: w05looFrames(), apply: w05looApply });
  w05looApply({ i: -1, b0: 0, b1: 0, cv: 0, line: 1, done: false });
  $('w05looRound').textContent = '0 / ' + w05looN;
  $('w05looErr').textContent = '—'; $('w05looCV').textContent = '—';
  setStatus('w05looStatus', '按「開始」逐筆留一。');
}

/* ---------- P03 k-fold：分割動畫器 ---------- */
const w05foldNBalls = 20;
let w05foldPlayer = null, w05foldK = 5;
function w05foldAssign(k) {
  const rand = HC.stat.lcg(2026), idx = [...Array(w05foldNBalls).keys()];
  for (let i = idx.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]];
  }
  const fold = new Array(w05foldNBalls);
  idx.forEach((b, pos) => { fold[b] = pos % k; });
  return fold;
}
function w05foldSetK() {
  w05foldK = parseInt($('w05foldSel').value, 10);
  $('w05foldK').textContent = String(w05foldK);
  w05foldReset();
}
function w05foldFrames() {
  const k = w05foldK, fold = w05foldAssign(k);
  const detail = FRAMES_w05fold.detail[String(k)] || [];
  const frames = [];
  let acc = 0;
  for (let j = 0; j < k; j++) {
    const d = detail[j] || { n_train: 0, n_held: 0, mse: NaN };
    acc += d.mse;
    frames.push({ j, fold, k, d, avg: acc / (j + 1) });
  }
  return frames;
}
function w05foldApply(f) {
  const host = $('w05foldSvg');
  const cell = 26, per = 10, gap = 5;
  // viewBox 寬度固定 620（跟其他 SVG 元件一致），否則 SVG 被拉寬時字會跟著放大
  const W = 620, H = 2 * cell + gap + 60;
  const x0 = (W - (per * cell + (per - 1) * gap)) / 2;
  host.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  while (host.firstChild) host.removeChild(host.firstChild);
  const mk = (tag, a) => {
    const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const key of Object.keys(a)) n.setAttribute(key, String(a[key]));
    host.appendChild(n); return n;
  };
  for (let b = 0; b < w05foldNBalls; b++) {
    const r = Math.floor(b / per), c = b % per;
    const held = f.fold[b] === f.j;
    mk('rect', {
      x: x0 + c * (cell + gap), y: 34 + r * (cell + gap), width: cell, height: cell, rx: 5,
      fill: held ? 'var(--pt-held)' : 'var(--pt-train)',
      stroke: held ? '#d68910' : 'none', 'stroke-width': held ? 2.5 : 0,
    });
    const t = mk('text', {
      x: x0 + c * (cell + gap) + cell / 2, y: 34 + r * (cell + gap) + cell / 2 + 4,
      'text-anchor': 'middle', fill: '#fff',
      style: "font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600",
    });
    t.textContent = String(f.fold[b] + 1);
  }
  const lab = mk('text', { x: x0, y: 22, class: 'axtitle' });
  lab.textContent = f.j < 0
    ? '20 顆球，數字是它被分到第幾折 · 按「開始」逐折驗證'
    : '20 顆球，數字是它被分到第幾折 · 這一輪留下第 ' + (f.j + 1) + ' 折';
  $('w05foldRound').textContent = (f.j + 1) + ' / ' + f.k;
  $('w05foldN').textContent = f.d.n_train + ' / ' + f.d.n_held;
  $('w05foldMse').textContent = HC.fmt(f.d.mse, 3);
  $('w05foldAvg').textContent = HC.fmt(f.avg, 3);
  setStatus('w05foldStatus', '第 ' + (f.j + 1) + ' 折當驗證集：Auto 上用 '
    + f.d.n_train + ' 筆訓練、' + f.d.n_held + ' 筆驗證，這一折的 MSE = '
    + HC.fmt(f.d.mse, 3) + '，累計平均 ' + HC.fmt(f.avg, 3) + '。');
}
function w05foldStart() {
  w05foldPlayer = new Player({ frames: w05foldFrames(), apply: w05foldApply });
  w05foldPlayer.reset(); w05foldPlayer.play();
}
function w05foldReset() {
  if (w05foldPlayer) w05foldPlayer.stop();
  w05foldPlayer = new Player({ frames: w05foldFrames(), apply: w05foldApply });
  w05foldApply({ j: -1, fold: w05foldAssign(w05foldK), k: w05foldK,
                 d: { n_train: '—', n_held: '—', mse: NaN }, avg: NaN });
  setStatus('w05foldStatus', 'k = ' + w05foldK + '。按「開始」看每一折輪流當驗證集。');
}

/* ---------- P04 LOOCV vs 10-fold ---------- */
let w05cvLog = false;
function w05cvToggleLog() { w05cvLog = !w05cvLog; w05cvDraw(); }
function w05cvDraw() {
  const F = FRAMES_w05cv;
  const best = a => a.indexOf(Math.min(...a));
  HC.line('w05cvChart', {
    labels: F.degrees,
    datasets: [
      { label: 'LOOCV', data: F.loocv, borderColor: HC.tok.accent2, backgroundColor: HC.tok.accent2,
        borderWidth: 2.6, pointRadius: 3.5, fill: false },
      { label: '10-fold CV', data: F.kfold10, borderColor: HC.tok.accent3, backgroundColor: HC.tok.accent3,
        borderWidth: 2.6, pointRadius: 3.5, borderDash: [6, 4], fill: false },
    ],
  }, {
    scales: {
      x: { title: { display: true, text: 'horsepower 多項式次數' } },
      y: { type: w05cvLog ? 'logarithmic' : 'linear',
           title: { display: true, text: 'CV 估的測試 MSE' } },
    },
    plugins: { annotationless: false },
  });
  const c = HC.get('w05cvChart');
  HC.refs(c, [HC.vline(1, 'degree 2 之後就拉平')]);
  $('w05cvLoo').textContent = 'degree ' + F.degrees[best(F.loocv)] + '（' + HC.fmt(Math.min(...F.loocv), 2) + '）';
  $('w05cvKf').textContent = 'degree ' + F.degrees[best(F.kfold10)] + '（' + HC.fmt(Math.min(...F.kfold10), 2) + '）';
  const gap = Math.max(...F.degrees.map((_, i) => Math.abs(F.loocv[i] - F.kfold10[i])));
  $('w05cvGap').textContent = HC.fmt(gap, 3);
}

/* ---------- P06 CV 的錯用 ---------- */
function w05misShow() {
  const F = FRAMES_w05misuse;
  HC.bar('w05misChart', {
    labels: ['先選特徵再 CV（錯）', '在每折內選特徵（對）'],
    datasets: [{ label: '5-fold CV 錯誤率', data: [F.wrongErr, F.rightErr],
                 backgroundColor: [HC.tok.accent, HC.tok.accent3], borderRadius: 5 }],
  }, {
    plugins: { legend: { display: false } },
    scales: { y: { min: 0, max: 0.6, title: { display: true, text: 'CV 錯誤率' } } },
  });
  const c = HC.get('w05misChart');
  HC.refs(c, [HC.hline(0.5, '誠實的答案 ≈ 0.5')]);
  $('w05misWrong').textContent = HC.fmt(F.wrongErr, 3);
  $('w05misRight').textContent = HC.fmt(F.rightErr, 3);
  setStatus('w05misStatus', 'n = ' + F.n + '、p = ' + F.p + ' 的純噪音資料，挑 ' + F.kSel
    + ' 個特徵。錯的流程回報 ' + HC.fmt(F.wrongErr, 3) + '，對的流程回報 '
    + HC.fmt(F.rightErr, 3) + '——只有後者誠實地說出「這些特徵沒用」。');
}

/* ---------- P07 Bootstrap 抽樣器 ---------- */
const w05bootBalls = [3, 8, 5, 12, 7, 2, 10, 6, 9, 4];
let w05bootStats = [];
function w05bootRand() {
  w05bootRand.seed = (w05bootRand.seed || 0) + 1;
  return HC.stat.lcg(20260810 + w05bootRand.seed * 7919);
}
function w05bootOne() {
  const rand = w05bootRand(), n = w05bootBalls.length;
  const counts = new Array(n).fill(0), drawn = [];
  for (let i = 0; i < n; i++) {
    const j = Math.floor(rand() * n); counts[j]++; drawn.push(w05bootBalls[j]);
  }
  return { counts, drawn, stat: drawn.reduce((s, v) => s + v, 0) / n };
}
function w05bootRender(d) {
  const host = $('w05bootSvg');
  const cell = 30, gap = 6, n = w05bootBalls.length;
  const W = n * cell + (n - 1) * gap + 40, H = 130;
  host.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
  while (host.firstChild) host.removeChild(host.firstChild);
  const mk = (tag, a, text) => {
    const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const k of Object.keys(a)) el.setAttribute(k, String(a[k]));
    if (text !== undefined) el.textContent = text;
    host.appendChild(el); return el;
  };
  mk('text', { x: 20, y: 18, class: 'axtitle' }, '原始 10 筆資料（數字是值，右上角是這次被抽中幾次）');
  w05bootBalls.forEach((v, j) => {
    const cx = 20 + j * (cell + gap), c = d ? d.counts[j] : 0;
    const oob = d && c === 0;
    mk('rect', { x: cx, y: 30, width: cell, height: cell, rx: 6,
                 fill: oob ? 'none' : (d ? 'var(--accent3)' : 'var(--card)'),
                 stroke: oob ? 'var(--accent)' : 'var(--card-border)',
                 'stroke-width': oob ? 2.5 : 1,
                 'stroke-dasharray': oob ? '4 3' : '' });
    mk('text', { x: cx + cell / 2, y: 50, 'text-anchor': 'middle',
                 fill: oob || !d ? 'var(--ink)' : '#fff',
                 style: "font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700" },
       String(v));
    if (d && c > 1) {
      mk('text', { x: cx + cell - 2, y: 28, 'text-anchor': 'end', fill: 'var(--accent)',
                   style: "font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700" },
         '×' + c);
    }
  });
  if (d) {
    mk('text', { x: 20, y: 82, class: 'axtitle' }, '這次抽到的 bootstrap 樣本');
    mk('text', { x: 20, y: 102, class: 'axlab',
                 style: "font-family:'JetBrains Mono',monospace;font-size:12px;fill:var(--ink)" },
       '[' + d.drawn.join(', ') + ']');
    const nOob = d.counts.filter(c => c === 0).length;
    mk('text', { x: 20, y: 120, class: 'axlab' },
       'OOB（虛線框）：' + nOob + ' / ' + w05bootBalls.length
       + ' = ' + HC.pct(nOob / w05bootBalls.length, 0) + '，理論值 36.8%');
  }
}
function w05bootHist() {
  if (!w05bootStats.length) return;
  const lo = 3.5, hi = 9.5, bins = 20;
  const h = new Array(bins).fill(0);
  w05bootStats.forEach(v => {
    const b = Math.min(bins - 1, Math.max(0, Math.floor((v - lo) / (hi - lo) * bins)));
    h[b]++;
  });
  HC.bar('w05bootChart', {
    labels: h.map((_, i) => HC.fmt(lo + (hi - lo) * (i + 0.5) / bins, 1)),
    datasets: [{ label: '樣本平均 θ̂* 的分佈', data: h,
                 backgroundColor: 'rgba(44,62,122,.72)', borderRadius: 3 }],
  }, {
    plugins: { legend: { display: false } },
    scales: { x: { title: { display: true, text: 'θ̂*（這次 bootstrap 樣本的平均）' } },
              y: { title: { display: true, text: '次數' } } },
  });
}
function w05bootUpdate(d) {
  w05bootStats.push(d.stat);
  const m = HC.stat.mean(w05bootStats);
  $('w05bootDraw').textContent = '[' + d.drawn.join(',') + ']';
  const nOob = d.counts.filter(c => c === 0).length;
  $('w05bootOob').textContent = nOob + ' 筆（' + HC.pct(nOob / w05bootBalls.length, 0) + '）';
  $('w05bootStat').textContent = HC.fmt(d.stat, 3);
  $('w05bootB').textContent = String(w05bootStats.length);
  $('w05bootSE').textContent = w05bootStats.length > 1
    ? HC.fmt(HC.stat.sd(w05bootStats), 4) : '—';
  setStatus('w05bootStatus', '第 ' + w05bootStats.length + ' 次重抽：'
    + nOob + ' 筆完全沒被抽到（虛線框），這次的樣本平均是 ' + HC.fmt(d.stat, 3)
    + '。累計 ' + w05bootStats.length + ' 次的標準差 = '
    + (w05bootStats.length > 1 ? HC.fmt(HC.stat.sd(w05bootStats), 4) : '—')
    + '（原始資料平均 ' + HC.fmt(m, 3) + '）。');
}
function w05bootDrawOne() {
  const d = w05bootOne(); w05bootRender(d); w05bootUpdate(d); w05bootHist();
  hlLine('w05bootCode', 2);
}
function w05bootMany() {
  let last = null;
  for (let i = 0; i < 200; i++) { last = w05bootOne(); w05bootStats.push(last.stat); }
  w05bootStats.pop();
  w05bootRender(last); w05bootUpdate(last); w05bootHist();
  hlLine('w05bootCode', 4);
}
function w05bootReset() {
  w05bootStats = []; w05bootRand.seed = 0;
  w05bootRender(null);
  ['w05bootDraw', 'w05bootOob', 'w05bootStat', 'w05bootSE'].forEach(i => { $(i).textContent = '—'; });
  $('w05bootB').textContent = '0';
  HC.bar('w05bootChart', { labels: [], datasets: [{ data: [] }] },
         { plugins: { legend: { display: false } } });
  hlLine('w05bootCode', null);
  setStatus('w05bootStatus', '按「抽一次」看一次有放回重抽。');
}

/* ---------- P07 1−(1−1/n)^n → 0.632 ---------- */
function w05p632Run() {
  const ns = [2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 75, 100, 150, 200];
  const theory = ns.map(n => 1 - Math.pow(1 - 1 / n, n));
  const rand = HC.stat.lcg(632);
  const sim = ns.map(n => {
    let hit = 0;
    const reps = 2000;
    for (let r = 0; r < reps; r++) {
      let got = false;
      for (let i = 0; i < n; i++) if (Math.floor(rand() * n) === 0) { got = true; break; }
      if (got) hit++;
    }
    return hit / reps;
  });
  HC.line('w05p632Chart', {
    labels: ns,
    datasets: [
      { label: '理論 1−(1−1/n)ⁿ', data: theory, borderColor: HC.tok.accent2,
        borderWidth: 2.6, pointRadius: 0, fill: false },
      { label: '模擬（每點 2000 次）', data: sim, borderColor: HC.tok.accent,
        backgroundColor: HC.tok.accent, borderWidth: 0, pointRadius: 4,
        showLine: false, fill: false },
    ],
  }, {
    scales: { x: { title: { display: true, text: 'n' } },
              y: { min: 0.6, max: 0.78,
                   title: { display: true, text: '至少被抽到一次的機率' } } },
  });
  const c = HC.get('w05p632Chart');
  HC.refs(c, [HC.hline(1 - Math.exp(-1), '1 − 1/e ≈ 0.6321')]);
  const at = n => HC.fmt(1 - Math.pow(1 - 1 / n, n), 4);
  $('w05p632n5').textContent = at(5);
  $('w05p632n20').textContent = at(20);
  $('w05p632n100').textContent = at(100);
  setStatus('w05p632Status', '模擬點（紅）落在理論曲線（藍）上。n = 5 就已經是 '
    + at(5) + '，n = 100 是 ' + at(100) + '，很快收斂到 0.6321。');
}

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.bar / HC.line 在 Chart 未載入時本來就安全地回傳 null。 */
w05looSetup();
w05looReset();
w05foldReset();
w05bootReset();
HC.ready(() => {
  w05valDraw();
  w05cvDraw();
  w05misShow();
  w05p632Run();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


if __name__ == "__main__":
    apply("resampling_methods", BODIES, PAGEJS, frames())
