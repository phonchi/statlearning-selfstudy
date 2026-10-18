#!/usr/bin/env python3
"""model_selection.html（ISLP 第 6 章）完整自學充實。冪等。

內容依據：講義 06_Linear_Model_Selection.pdf（70 頁）、Ch06-varselect-lab-zh.ipynb、
ISLP 第 6 章（書上 p.230–288）。所有「預期輸出」逐字取自 lab 的實跑結果，
圖表資料由 tools/frames/gen_modelsel.py 在固定種子下產生。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import detail, proof
from modelsel_lecture_notes import (ADJR2_CORE, AIC_BIC_CORE, CP_CORE, CV_SE_CORE,  # noqa: E402
                                    GUIDED_SEARCH, LASSO_WHY_BAYES, LASSO_WHY_DIAG,
                                    LASSO_WHY_INTRO, ORTHOGONAL_FORWARD, STEPWISE_WHY,
                                    SUBSET_DEVIANCE, SUBSET_INTRO)
from lib import (apply, card, chart, hl, info, info_card, lab_code, lab_output, qa,  # noqa: E402
                 quiz, rows_card, svg, table, ver_note, viz)

CH = 6
LAB = "Ch06-varselect-lab-zh.ipynb"


def src(cell):
    return f"<code>{LAB}</code> · 儲存格 {cell}"


def frames():
    gen = Path(__file__).resolve().parent.parent / "frames" / "gen_modelsel.py"
    r = subprocess.run(["conda", "run", "-n", "m524", "python", str(gen)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gen_modelsel.py 失敗：\n" + r.stderr[-2000:])
    return ("/* ===== 烘焙資料（tools/frames/gen_modelsel.py，固定種子）===== */\n"
            + r.stdout.strip())


def slider(sid, label, lo, hi, step, val, fn, vid, vtext):
    """.controls-bar 裡的滑桿。flex 讓它在窄螢幕縮而不撐爆版面。"""
    return (f'<div class="slider-row" style="flex:1 1 200px;margin-bottom:0;min-width:0;">'
            f'<span class="slider-label">{label}</span>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}" onchange="{fn}">'
            f'<span class="slider-val" id="{vid}">{vtext}</span></div>')


# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>第 3 章的最小平方法很好用：沒有調整參數、有封閉解、係數可以直接解讀。講義強調線性模型<strong>容易解讀，預測表現也常常不錯</strong>，所以本章不放棄線性模型，而是把「最小平方擬合」換成其他擬合方法。這在 $n\\approx p$ 或 $p>n$ 時特別重要。</p>

  <p>講義列出四個<strong>考慮替代最小平方法的理由</strong>：</p>
  <ol>
    <li><strong>預測準確度</strong>：當 $p\\approx n$，最小平方的估計變異很大；當 $p>n$，它連唯一解都沒有。若設計矩陣的列滿秩，有無限多組係數能把訓練誤差壓到 0，但它們在新資料上的預測不一定相同。需要控制變異。</li>
    <li><strong>可解讀性</strong>：把無關或重複的變數拿掉，也就是把對應係數設成 0，模型比較容易解讀。最小平方幾乎不會把係數估成剛好 0，因此需要能<strong>自動做特徵選擇</strong>的方法。</li>
    <li><strong>加快訓練與推論</strong>：變數少了，擬合、儲存與預測的計算量都會下降，上線後要蒐集的資料也比較少。</li>
    <li><strong>避開維度詛咒</strong>：維度愈高，資料在空間中愈稀疏，局部方法愈難找到夠近的鄰居（見<a href="statistical_learning.html#curse">第 2 章的維度詛咒</a>）。先降低有效維度，後續方法比較不受影響。</li>
  </ol>

{info("這一章的三大類方法", '''<strong>1. 子集選擇（subset selection）：</strong>挑出一部分變數，
  只用它們做最小平方。最佳子集、前向逐步、後向逐步。<br>
  <strong>2. 收縮（shrinkage）／正則化：</strong>全部 $p$ 個變數都留著，但把係數往 0 壓。
  Ridge 用 L2 懲罰、Lasso 用 L1 懲罰（順便做變數選擇）。<br>
  <strong>3. 降維（dimension reduction）：</strong>把 $p$ 個變數投影成 $M&lt;p$ 個線性組合，
  再對這 $M$ 個新變數做最小平方。PCR 與 PLS。''')}

  <p>三類方法都透過<strong>接受一些偏差來降低變異</strong>。最小平方是無偏的，
  但在 $p$ 大的時候，高變異會降低預測表現；只要願意接受一點偏差，測試誤差往往降得很明顯。
  本章會比較這些方法如何取捨偏差與變異。</p>

  $$\\text{{RSS}} = \\sum_{{i=1}}^{{n}}\\left(y_i - \\beta_0 - \\sum_{{j=1}}^{{p}}\\beta_j x_{{ij}}\\right)^2$$

  <p>下表整理三類方法的差別，讀完整章後可回來比較。</p>

{table(["", "留幾個變數", "係數會剛好是 0 嗎", "有調整參數嗎", "座標系", "主要弱點"],
       [["最小平方", "全部 $p$ 個", "幾乎不會", "沒有", "原始變數", "$p$ 大時變異很大"],
        ["子集選擇", "$k$ 個（自己選）", "沒被選的就是 0", "$k$", "原始變數", "搜尋空間太大、不穩定"],
        ["Ridge（L2）", "全部 $p$ 個", "<strong>不會</strong>", "$\\lambda$", "原始變數", "不做變數選擇"],
        ["Lasso（L1）", "由 $\\lambda$ 決定", "<strong>會</strong>", "$\\lambda$", "原始變數", "相關變數之間的選擇很不穩"],
        ["PCR / PLS", "全部 $p$ 個都參與", "不會", "$M$", "<strong>換過的座標</strong>",
         "新座標不好解讀"]])}

{quiz("qWhy", "QUIZ · 為什麼要調整模型",
      "為什麼 $p$ 逼近 $n$ 的時候，「把全部變數丟進去做最小平方」是個壞主意？",
      [(True, "因為係數估計的變異會變得非常大，訓練資料稍微變動一點，擬合出來的模型就差很多",
        "對。最小平方在 $p\\ll n$ 時是低偏差、低變異；$p$ 逼近 $n$ 時偏差仍然是 0，但變異大到讓測試誤差變大。收縮就是拿一點偏差去換掉這塊變異。"),
       (False, "因為最小平方法假設誤差是常態分佈，變數多了這個假設就不成立",
        "不對。常態假設是用來做 t 檢定與信賴區間的，跟 $p/n$ 的比例無關；而且就算誤差真的是常態，$p$ 逼近 $n$ 時最小平方照樣會變異很大。"),
       (False, "因為變數多了以後 RSS 會變大，擬合品質下降",
        "反了。加變數<strong>永遠</strong>不會讓訓練 RSS 變大（多一個變數最差就是係數估成 0）。訓練 RSS 單調下降正是問題所在。它不能用來選模型。")])}
"""

# ── P01 subset ────────────────────────────────────────────────────────
_sub_code = lab_code(CH, 12) + "\n" + lab_code(CH, 13) + "\n" + lab_code(CH, 15)

BODIES["subset"] = f"""
{SUBSET_INTRO}
{SUBSET_DEVIANCE}
{STEPWISE_WHY}
  <p><strong>前向逐步選擇</strong>（forward stepwise selection）從空模型開始，每一步加入一個「讓訓練 RSS 降最多」的變數，直到所有變數都在模型裡。
  <strong>後向逐步選擇</strong>（backward stepwise selection）反過來，從含全部 $p$ 個變數的模型開始，每次刪掉最沒用的一個。
  兩者都只要擬合</p>

  $$1 + \\sum_{{k=0}}^{{p-1}} (p-k) = 1 + \\frac{{p(p+1)}}{{2}} \\; \\text{{個模型}}$$

  <p>$p = 20$ 時這是 <strong>211</strong> 個，而最佳子集是 $2^{{20}}=$ <strong>1,048,576</strong> 個。
  代價是<strong>貪婪走法不保證找到最佳子集</strong>（訓練誤差最低的子集）。講義的例子：$p=3$ 時，最佳單變數模型含 $X_1$，最佳雙變數模型卻是 $\\{{X_2,X_3\\}}$；前向法的 $M_1$ 含 $X_1$，$M_2$ 也只能含 $X_1$ 再加一個，於是錯過最佳的雙變數模型。下面第二張圖用四變數示意把這件事畫出來。</p>
{GUIDED_SEARCH}
{ORTHOGONAL_FORWARD}

{viz(svg("w06subsetSvg", 190) + "\n" + svg("w06subsetLatSvg", 300),
     [rows_card("要擬合幾個模型",
                [("$p$（變數個數）", "10", "w06subsetP2"),
                 ("最佳子集 $2^p$", "—", "w06subsetBest"),
                 ("forward $1+p(p+1)/2$", "—", "w06subsetFwd"),
                 ("差幾倍", "—", "w06subsetRatio")]),
      info_card("前向逐步選擇的虛擬碼",
                '<div class="pseudo-code" id="w06subsetCode" style="font-size:.72rem;">'
                '<span class="line" data-l="1">M0 = 空模型</span>\n'
                '<span class="line" data-l="2"><span class="kw">for</span> k '
                '<span class="kw">in</span> <span class="kw">range</span>(p):</span>\n'
                '<span class="line" data-l="3">    試 p−k 個「再加一個變數」</span>\n'
                '<span class="line" data-l="4">    留 RSS 最小的 → M(k+1)</span>\n'
                '<span class="line" data-l="5">用 CV／Cp／BIC 從 M0…Mp 挑一個</span></div>',
                "CODE"),
      rows_card("四變數的流程示意", [("目前候選", "—", "w06latTry"), ("這一步選到的", "—", "w06latPick")]),
      info_card("下圖怎麼看",
                '每一個點代表四變數流程示意中的一個候選子集；x 是變數個數、y 是訓練 RSS。'
                '<span style="color:var(--accent);font-weight:700;">紅線</span>連接每個大小的最佳子集，'
                '<span style="color:var(--accent3);font-weight:700;">綠線</span>表示 forward 逐步選擇的路徑。',
                "示意")],
     "w06subsetStatus", "用上面的滑桿觀察 2 的 p 次方如何快速增加；下面按「開始」追蹤 forward 的選擇流程。",
     slider("w06subsetP", "$p$ =", 2, 20, 1, 10, "w06subsetCounts()", "w06subsetPv", "10")
     + '<button class="btn btn-play" onclick="w06latStart()">▶ 開始</button>'
     + '<button class="btn btn-step" onclick="w06latPlayer &amp;&amp; w06latPlayer.step()">→ 單步</button>'
     + '<button class="btn btn-toggle" onclick="w06latToggleBest()">切換最佳前緣</button>'
     + '<button class="btn btn-reset" onclick="w06latReset()">重置</button>',
     provenance=("illustrative", "依講義逐步選擇算法的四變數流程示意"))}

{info("逐步選擇的流程", "這張四變數示意圖用來追蹤逐步加入變數的順序。逐步法沿已選定的路徑繼續搜尋，未必等於窮舉所有子集；它不表示哪種方法對新資料一定較好。")}

  <h3 id="dx-sub">講義完整實作：Hitters、前向與後向逐步選擇</h3>
{""}

{card("講義 06 · 自訂迴圈的前向逐步選擇", lab_code(CH, 33) + "\n\n" + lab_code(CH, 34),
      None, src=src("33、34"),
      note="讀逐步加入變數時，每個候選模型包含前一步已選的變數："
           "<code>CRBI</code> → 加 <code>Hits</code> → 加 <code>PutOuts</code>…"
           "一路只加不減。這正是前向逐步的定義，也正是它可能錯過最佳子集的原因。")}

{card("講義 06 · 後向逐步選擇（BIC 挑出來的大小不一樣）",
      lab_code(CH, 40) + "\n\n" + lab_code(CH, 41), lab_output(CH, 41), src=src("40、41"),
      note="<code>bic_b</code> 是照 <code>models2</code> 的索引順序（1、2、…、19）收集的，"
           "0-based 的 <code>argmin() = 7</code> 指的是<strong>第 8 個</strong>元素，也就是 8 變數模型；"
           "而前向那邊（下一節）是 6 變數。<strong>同一份資料、同一個準則，兩個搜尋方向給出不同大小的模型</strong>"
           "——講義第 42 頁講的就是這件事。")}

{table(["搜尋法", "要擬合幾個模型", "$p=20$ 時", "$n&lt;p$ 能用嗎", "保證找到最佳子集嗎"],
       [["最佳子集", "$2^p$", "1,048,576", "可以（只比較可估計的小子集）", "<strong>會</strong>"],
        ["前向逐步", "$1+p(p+1)/2$", "211", "<strong>可以</strong>", "不保證"],
        ["後向逐步", "$1+p(p+1)/2$", "211", "不能（要先擬合全模型）", "不保證"],
        ["混合逐步", "略多於逐步", "約 211+", "看實作", "不保證（但比較接近）"]])}

{quiz("qSub", "QUIZ · 子集選擇",
      "同一份資料上做最佳子集、前向逐步、後向逐步。<strong>大小同樣是 $k$</strong> 的三個模型裡，"
      "哪一個的訓練 RSS 最小？",
      [(True, "最佳子集的一定最小（或並列最小），因為它窮舉了所有 $k$ 變數子集",
        "對。這就是 ISLP 6.6 第 1 題 (a) 的答案。注意這只說訓練 RSS——測試 RSS 誰最小完全說不準，因為窮舉的搜尋空間更大，反而更容易擬合到雜訊。"),
       (False, "三個一定相同，因為它們都是在同一份資料上做最小平方",
        "不對。都是最小平方沒錯，但<strong>用的變數不同</strong>。逐步法受前幾步的選擇綁住，可能拿不到那個 $k$ 變數的最佳組合——本節的 Credit 格圖就是實例。"),
       (False, "後向逐步的最小，因為它從全模型開始，資訊最完整",
        "不對。從全模型開始只影響搜尋路徑，不代表每個大小都能找到最佳組合。後向逐步同樣是貪婪的，而且它還多一個限制：要能擬合出全模型，所以需要 $n&gt;p$。")])}
"""

# ── P02 criteria ──────────────────────────────────────────────────────
BODIES["criteria"] = f"""
  <p>第二階段的問題是：<strong>怎麼比較「大小不同」的模型？</strong>訓練 RSS 與 $R^2$ 不能用，
  因為它們單調偏好大模型。兩條路——<strong>間接</strong>（把訓練誤差加一個懲罰項，修掉它的樂觀偏差）
  與<strong>直接</strong>（用驗證集或交叉驗證真的去估測試誤差，下一節講）。</p>

  <p>常見的間接評估準則有四個。設模型有 $d$ 個預測變數，$\\hat\\sigma^2$ 是用<strong>全模型</strong>估出來的誤差變異數：</p>

  $$C_p = \\frac{{1}}{{n}}\\left(\\mathrm{{RSS}} + 2 d \\hat\\sigma^2\\right), \\qquad
    \\mathrm{{BIC}} = \\frac{{1}}{{n}}\\left(\\mathrm{{RSS}} + \\log(n)\\, d \\hat\\sigma^2\\right)$$

  $$\\text{{Adjusted }} R^2 = 1 - \\frac{{\\mathrm{{RSS}}/(n-d-1)}}{{\\mathrm{{TSS}}/(n-1)}}$$

  <p>兩個公式長得幾乎一樣，只差在<strong>每多一個變數要罰多少</strong>：$C_p$ 罰 $2\\hat\\sigma^2$，
  BIC 罰 $\\log(n)\\,\\hat\\sigma^2$。整數樣本數 $n\\ge8$ 時 $\\log n>2$，所以<strong>BIC 罰得比 $C_p$ 重，偏好更小的模型</strong>。
  $n$ 愈大差距愈明顯：<code>Credit</code> 的 $n = 400$，$\\log 400 \\approx 5.99$，BIC 的懲罰約是 $C_p$ 的三倍。</p>
{CP_CORE}

{info("AIC 與 $C_p$ 的關係", '''對高斯誤差的最小平方模型，課本的 AIC 就是
  $\\mathrm{{RSS}}+2d\\hat\\sigma^2$，跟 $C_p$ 成正比（所以 ISLP 圖 6.2 只畫 $C_p$）。
  <code>statsmodels</code> 的 <code>.aic</code> 用的是 log-likelihood 版，數值與 $C_p$ 不同，所以下圖畫成獨立一條線；為什麼成正比見下方「懲罰項各從哪裡來」收合區，軟體量尺見「先分清估計量與比較量尺」收合區。''')}

{table(["準則", "式子（最小平方）", "每多一個變數罰多少", "$n=400$ 時的懲罰", "Credit 選出"],
       [["$C_p$", "$(\\mathrm{RSS}+2d\\hat\\sigma^2)/n$", "$2\\hat\\sigma^2$", "$2\\hat\\sigma^2$", "<strong>6 個</strong>"],
        ["AIC（課本）", "$\\mathrm{RSS}+2d\\hat\\sigma^2$", "$2\\hat\\sigma^2$", "與 $C_p$ 成正比", "同 $C_p$"],
        ["BIC", "$(\\mathrm{RSS}+\\log(n)\\,d\\hat\\sigma^2)/n$", "$\\log(n)\\,\\hat\\sigma^2$", "<strong>$5.99\\hat\\sigma^2$</strong>",
         "<strong>4 個</strong>"],
        ["調整後 $R^2$", "$1-[\\mathrm{RSS}/(n-d-1)]/[\\mathrm{TSS}/(n-1)]$", "分母的 $n-d-1$ 變小", "很輕",
         "<strong>7 個</strong>"],
        ["交叉驗證", "直接估測試誤差", "不需要 $\\hat\\sigma^2$", "—", "<strong>6 個</strong>"]])}

{AIC_BIC_CORE}
{ADJR2_CORE}

{qa("觀念釐清", [
    ("Q：$C_p$、AIC、BIC 到底差在哪？為什麼 BIC 偏好小模型？",
     "<p>形式上只差在每多一個變數的懲罰（上方公式與表格）；BIC 的懲罰在 $n\\ge8$ 時較重，所以選出來的模型一律比較小或一樣大。</p>"
     "<p>背後的動機不同：$C_p$／AIC 想預測得準，BIC 想找出<em>正確的</em>模型。三個係數各自怎麼推導出來，見上方「懲罰項各從哪裡來」收合區；目標的比較見「漸近效率、選模一致性」收合區。</p>"
     "<p>實務上的建議：<strong>目的是預測就用 CV（或 AIC／$C_p$），目的是「哪些變數真的有關」就參考 BIC</strong>。"
     "而且兩者都要求你估得出 $\\hat\\sigma^2$——這在 $p&gt;n$ 的時候無法按全模型的常規公式計算（最後一節會講）。</p>"),
    ("Q：調整後 $R^2$ 為什麼「理論基礎比較弱」？",
     "<p>$C_p$、AIC、BIC 都有明確的推導目標（見上方收合區）。調整後 $R^2$ 沒有這種東西。它就是「把 RSS 除以 $n-d-1$ 而不是 $n$」"
     "這個直覺上合理的修正。</p>"
     "<p>它的直覺（上方主文）是對的，問題是 RSS 要降多少才算值得，沒有像 $C_p$ 那樣從預測誤差推出來的刻度，所以它的懲罰強度是任意的——"
     "在 Credit 上它比 $C_p$ 還鬆（選 7 個 vs 6 個）。</p>"),
])}

  <h3 id="dx-crit">講義完整實作：用 BIC 與調整後 $R^2$ 挑大小</h3>
{card("講義 06 · 前向路徑上的 BIC", lab_code(CH, 36) + "\n\n" + lab_code(CH, 37),
      lab_output(CH, 37), src=src("36、37"),
      note="<code>argmin()</code> 回傳 <strong>5</strong>，而 <code>bic_f</code> 是 0-based 的 "
           "list，所以指的是清單的第 6 個元素——<strong>6 變數模型</strong>，BIC = 3812.21。"
           "注意下一格的 <code>models1.model[5]</code> 用的是 pandas 的<em>標籤</em>索引，"
           "取到的是 5 變數模型（輸出列出 5 個特徵）。同一個 <code>5</code>，兩種索引意義完全不同，"
           "讀別人的程式碼時要分清楚。")}

{card("講義 06 · 最佳子集 + 調整後 $R^2$",
      lab_code(CH, 97) + "\n\n" + lab_code(CH, 98) + "\n\n" + lab_code(CH, 101),
      None, src=src("97、98、101"),
      note="這是 <code>adjust_r2()</code> 的定義（就是式 6.4）加上在最佳子集前緣上取最大值。"
           "Hitters 上調整後 $R^2$ 選出 <strong>11 個變數</strong>；BIC 選 6 個。"
           "兩個準則差了 5 個變數，反映了它們對模型複雜度採用不同的懲罰強度。")}

{quiz("qCrit", "QUIZ · 選模型的準則",
      "同一份資料上，BIC 選出的模型大小，跟 $C_p$ 選出的比起來？",
      [(True, "一定小於或等於（$n\\ge8$ 時），因為 BIC 每多一個變數要罰 $\\log(n)\\,\\hat\\sigma^2$，而 $C_p$ 只罰 $2\\hat\\sigma^2$",
        "對。整數樣本數 $n\\ge8$ 時 $\\log n>2$，所以 BIC 的懲罰項嚴格較重，最小值只會往左移或不動。Credit 上是 4 vs 6。"),
       (False, "不一定，取決於資料裡有多少真的有用的變數",
        "有用變數的多寡會影響<em>兩者各自</em>選幾個，但不會改變「BIC 罰得更重」這個事實。兩條曲線的 RSS 部分完全一樣，只有懲罰斜率不同，所以 BIC 的最小值不可能落在 $C_p$ 的右邊。"),
       (False, "一定一樣，因為兩者都是測試 MSE 的無偏估計",
        "只有 $C_p$ 是測試 MSE 的無偏估計，BIC 不是——BIC 是從後驗機率近似來的，它刻意罰得更重以便挑出「正確的」模型而不是「預測最準的」模型。")])}
"""

# ── P03 用 CV 選模型 + one-SE ──────────────────────────────────────────
BODIES["onese"] = f"""
  <p>$C_p$、AIC、BIC 都需要估 $\\hat\\sigma^2$，而在 $p$ 接近 $n$ 的時候那個估計本身就不可靠。
  交叉驗證不需要 $\\hat\\sigma^2$、不需要知道自由度、也不需要假設模型是對的。
  它<strong>直接估測試誤差</strong>。所以只要算得動，CV 是首選。</p>

  <p>做法就是第 5 章那一套，只是把「模型」換成「模型大小」：對每個大小 $k$，
  在每一折的訓練部分做子集選擇、在驗證折上算誤差。
  <strong>變數選擇必須只使用各折的訓練資料</strong>。這正是第 5 章 P06 講的那個錯誤。</p>

{info("one-standard-error 規則", '''CV 誤差本身有抽樣變異。Credit 上的 CV 曲線在大小 4 到 8 之間幾乎是平的，
  差異遠小於誤差棒。這時候硬選最低點沒有道理，因為那個「最低」很可能只是運氣。<br><br>
  <strong>規則：先找到 CV 誤差最小的模型，算出它的標準誤；然後在「CV 誤差落在
  最小值 ＋ 一個標準誤」以內的所有模型裡，選最簡單的那個。</strong><br><br>
  Credit 資料上 CV 選 6 個變數，one-SE 規則選 <strong>4 個</strong>——
  四變數模型的 CV 誤差仍落在最佳點加一個標準誤的範圍內，規則因此偏好較簡單的四變數模型；這不是兩模型風險相同的統計檢定。上一節那張圖的橘色線就是 10-fold CV 誤差，
  大圓點是它的最低點。''')}

{CV_SE_CORE}

{card("講義 06 · 用 GridSearchCV 選調整參數", lab_code(CH, 134), None,
      src=src("134"),
      note="<code>Pipeline</code> 是關鍵：把標準化包進去，"
           "<code>GridSearchCV</code> 就會在每一折的訓練部分重新 fit scaler，"
           "而不是用全部資料的平均與標準差。這一步做錯，CV 誤差會偏低而且不會報錯。")}

{qa("觀念釐清", [
    ("Q：既然 CV 最好，為什麼還要教 $C_p$、AIC、BIC？",
     "<p>三個理由。第一，運算成本：最佳子集有 $2^p$ 個模型，每個都跑 k-fold 是 $k \\cdot 2^p$ 次擬合；"
     "而 $C_p$ 只要一次擬合加一個修正項。第二，這三個準則會出現在<strong>別人的論文與報表</strong>裡，"
     "你得看得懂。第三，它們示範了「懲罰複雜度」這個想法，目標的差別見上一節。</p>"
     "<p>但如果你只是要挑一個模型來預測，而且資料量算得動：用 CV。</p>"),
    ("Q：one-SE 規則會不會選出「太簡單」的模型？",
     "<p>會，而且那是刻意的。它的立場是：<strong>在最佳 CV 誤差加一個標準誤的範圍內，偏好簡單</strong>。</p>"
     "<p>這個偏好有實際理由——變數少的模型更好解釋、需要蒐集的資料更少、"
     "上線後更不容易因為某個變數的定義改變而壞掉。如果你的目標純粹是最小化預測誤差"
     "而完全不在意這些，那就選最低點；但要記得那個「最低」在下一份資料上很可能換人。</p>"),
])}

{""}
"""

# ── P04 Ridge ─────────────────────────────────────────────────────────
BODIES["ridge"] = f"""
  <p>子集選擇是離散的：一個變數只有納入或排除兩種選擇。這讓它<strong>變異很大</strong>——
  資料動一點，選出來的變數就換一批。另一條路是留下全部變數，但<strong>把係數往零壓</strong>。</p>

  <p>Ridge 在原本的 RSS 上加一個 L2 懲罰：</p>

  $$\\sum_{{i=1}}^{{n}}\\left(y_i - \\beta_0 - \\sum_{{j=1}}^{{p}}\\beta_j x_{{ij}}\\right)^2
    + \\lambda \\sum_{{j=1}}^{{p}} \\beta_j^2
    \\;=\\; \\mathrm{{RSS}} + \\lambda \\|\\beta\\|_2^2$$

  <p>$\\lambda = 0$ 就是最小平方；$\\lambda \\to \\infty$ 所有係數趨近 0。
  注意<strong>截距 $\\beta_0$ 不罰</strong>——罰它等於在乎你把 $y$ 的原點放在哪裡。</p>

{viz(chart("w06ridgeChart", "tall", "。此圖的重點：$\\lambda$ 變大時所有係數一起往零收縮，但沒有任何一個變成剛好 0。"),
     [info_card("怎麼看上圖",
                'x 軸可以切換 $\\log\\lambda$ 與 $\\|\\hat\\beta^R_\\lambda\\|_2/\\|\\hat\\beta\\|_2$（相對收縮量）。'
                '<strong>每條線是一個變數的係數。</strong>注意它們一起往中線靠，'
                '但到最右邊仍然沒有任何一條落在 0 上。', "圖 6.4"),
      rows_card("目前的 $\\lambda$",
                [("$\\lambda$", "—", "w06ridgeLam"), ("$\\|\\hat\\beta^R_\\lambda\\|_2/\\|\\hat\\beta\\|_2$", "—", "w06ridgeRatio"),
                 ("非零係數", "—", "w06ridgeNz")]),
      info_card("為什麼收縮可能更準",
                'Ridge 以小幅偏差換取較大的變異下降。第 2 章已用圖示說明這個偏差–變異取捨；'
                '這裡用 Credit 的係數路徑觀察收縮的效果。')],
     "w06ridgeStatus", "拖動滑桿看係數怎麼收縮。",
     '<label class="slider-label" style="margin-right:.4rem;">$\\log\\lambda$</label>'
     '<input type="range" id="w06ridgeSl" min="0" max="39" step="1" value="20" '
     'oninput="w06ridgeMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-toggle" onclick="w06ridgeAxis()">切換 x 軸</button>',
     provenance=("course-data", "ISLP Credit 的標準化 Ridge 路徑；對照圖 6.4"))}

{card("講義 06 · Ridge 與係數的 L2 範數",
      lab_code(CH, 122) + "\n\n" + lab_code(CH, 124), lab_output(CH, 124), src=src("122、124"),
      note="<code>ElasticNet</code> 的 <code>l1_ratio=0</code> 就是純 Ridge。"
           "係數的 L2 範數會隨 $\\lambda$ 單調下降。這個數字就是上圖 x 軸比值的分子。")}

{card("講義 06 · 用 RidgeCV 選 $\\lambda$", lab_code(CH, 144), None, src=src("144、145"),
      note="<code>RidgeCV</code> 把「掃 $\\lambda$ ＋ 交叉驗證」包成一步。"
           "<code>alphas</code> 接收一組候選值；排列順序本身不表示 <code>RidgeCV</code> 使用暖啟動。"
           "這張 lab 卡把 scaler 放在內建 CV estimator 外層，因此 scaler 會先對傳入 pipeline 的全部資料擬合，"
           "<code>RidgeCV</code> 才在縮放後的資料內切折。")}

{info("Ridge 之前一定要標準化", '''懲罰項 $\\sum \\beta_j^2$ 對<strong>單位敏感</strong>。
  同一個變數用「元」還是「千元」為單位，最小平方的預測完全一樣（係數等比例調整），
  Ridge 的懲罰會隨係數尺度改變：係數變大 1000 倍，懲罰項就變大 $10^6$ 倍，這個變數受到的收縮也會更強。<br><br>
  所以標準做法是先把每個 $x_j$ 標準化成標準差 1 再擬合。
  單純把 <code>StandardScaler</code> 放在 <code>RidgeCV</code> 或 <code>ElasticNetCV</code> 外層，
  只能保證 scaler 不會看到 pipeline 之外的外部測試集；內建 estimator 切 CV 折以前，資料已經縮放完畢。
  要讓每一折都只用該折訓練部分估平均與標準差，讓 <code>GridSearchCV</code> 搜尋一條包含
  <code>StandardScaler</code> 與 <code>Ridge</code> 的完整 pipeline。''', "warm")}

  <h3>折內標準化的概念寫法</h3>
{hl('''from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge', Ridge())
])
grid = GridSearchCV(
    pipe,
    {'ridge__alpha': [0.1, 1.0, 10.0]},
    cv=KFold(5, shuffle=True, random_state=0),
    scoring='neg_mean_squared_error'
)
grid.fit(X_train, Y_train)''')}
  <p><code>GridSearchCV</code> 會在每一折複製並擬合整條 pipeline，因此該折的 scaler
  只看該折訓練資料。這段概念碼假設已備妥外層訓練資料 <code>X_train</code>、<code>Y_train</code>；
  三個 $\\alpha$ 是示意候選值，這裡以 5 折平均 MSE 選擇。外部測試集留到選模完成後再使用。</p>

{quiz("qRidge", "QUIZ · Ridge",
      "把某個預測變數的單位從「元」改成「千元」（數值除以 1000）。Ridge 的預測會變嗎？",
      [(True, "會變，因為 L2 懲罰對單位敏感。這正是為什麼要先標準化",
        "對。係數會變成 1000 倍，懲罰項變成 $10^6$ 倍，這個變數於是被壓得特別兇，整個解就不同了。最小平方沒有這個問題。"),
       (False, "不會，因為線性模型對預測變數的線性變換不變",
        "<strong>最小平方</strong>的係數等比例調整時，預測保持相同。Ridge 的懲罰項則依調整後的係數計算，換單位會改變懲罰與擬合之間的取捨。"),
       (False, "不會，因為 scikit-learn 會自動標準化",
        "<code>Ridge</code> 預設<strong>不會</strong>標準化（早期版本的 <code>normalize</code> 參數已經移除）。你得自己包 <code>StandardScaler</code>。")])}
"""

# ── P05 補充：法線扇形、先驗形狀、訓練 R² 橫軸 ─────────────────────────
LASSO_FAN = r"""
  <p>尖角為什麼這麼容易被碰到？看菱形 $|\beta_1|+|\beta_2|\le1$ 的尖角 $P=(1,0)$。交於 $P$ 的兩條邊，外法線分別是 $(1,1)$ 與 $(1,-1)$；夾在這兩個方向之間的所有方向，都可以當作 $P$ 的支撐法線，合起來稱為 $P$ 的<strong>法線扇形</strong>（normal cone）。等高線是圓時，只要 $\hat\beta^{\mathrm{OLS}}$ 落在從 $P$ 張開的這個扇形裡，Lasso 解就是 $P$，$\beta_2$ 剛好為 0。扇形是一整塊區域，所以<strong>很多不同的最小平方解，都會對應到同一個稀疏解</strong>。圓在每一點只有一個法線方向，沒有扇形可以收留這麼多 OLS 解。</p>
""" + viz(svg("w06fanSvg", 360),
     [info_card("怎麼看",
                '藍色是限制區域，橘色陰影是尖角 $P$ 的法線扇形。拖動滑桿改變 $\\hat\\beta_2^{\\mathrm{OLS}}$'
                '（$\\hat\\beta_1^{\\mathrm{OLS}}$ 固定為 2），看綠點的 Lasso 解什麼時候離開 $P$。'),
      rows_card("目前的解",
                [("OLS 解", "—", "w06fanOls"), ("限制下的解", "—", "w06fanSol"),
                 ("OLS 在扇形內？", "—", "w06fanIn")]),
      info_card("切換成 Ridge 對照",
                '圓的邊界在每一點只有一個外法線方向，限制下的解就是把 OLS 點沿半徑拉回圓上。'
                '只要 $\\hat\\beta_2^{\\mathrm{OLS}}\\ne0$，解的 $\\beta_2$ 就不會是 0。')],
     "w06fanStatus", "OLS 在扇形內時，Lasso 解停在尖角 P=(1, 0)。",
     '<label class="slider-label" style="margin-right:.4rem;">$\\hat\\beta_2^{\\mathrm{OLS}}$</label>'
     '<input type="range" id="w06fanSl" min="-150" max="150" step="5" value="40" '
     'oninput="w06fanDraw()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-toggle" id="w06fanBtn" onclick="w06fanToggle()">切換為 L2（Ridge）</button>',
     provenance=("illustrative", "概念示意：圓形 RSS 等高線、預算 s=1；解為 OLS 點在限制區域上的歐氏投影")) + detail(
    "w06-detail-fan", "計算細節：為什麼離開尖角要付一階代價", r"""
  <p>取 $\mathrm{RSS}=(\beta_1-2)^2+(\beta_2-0.4)^2$，最小平方解是 $(2,0.4)$，限制為 $|\beta_1|+|\beta_2|\le1$。Lasso 解是 $P=(1,0)$。</p>
  <p><strong>Lasso：沿菱形的邊離開 $P$。</strong>想讓 $\beta_2$ 從 0 增加一點點 $\varepsilon\gt0$，菱形限制迫使 $\beta_1$ 至少降到 $1-\varepsilon$。RSS 的變化為</p>
  $$\begin{aligned}\Delta\mathrm{RSS}&=(1-\varepsilon-2)^2+(\varepsilon-0.4)^2-\big[(1-2)^2+0.4^2\big]\\&=1.2\,\varepsilon+2\varepsilon^2\gt0 .\end{aligned}$$
  <p>$\beta_2$ 確實更接近最小平方的 0.4，但要犧牲 $\beta_1$，讓它離 2 更遠；兩者相抵後 RSS 反而上升，所以解留在尖角。</p>
  <p><strong>扇形條件。</strong>把 $\hat\beta^{\mathrm{OLS}}-P$ 寫成兩條外法線的組合：$\hat\beta^{\mathrm{OLS}}-P=a(1,1)+c(1,-1)$，扇形內就是 $a\ge0$、$c\ge0$。解得 $a=\tfrac12(\hat\beta_1-1+\hat\beta_2)$、$c=\tfrac12(\hat\beta_1-1-\hat\beta_2)$，所以條件是</p>
  $$|\hat\beta_2^{\mathrm{OLS}}|\le\hat\beta_1^{\mathrm{OLS}}-1 .$$
  <p>本例 $\hat\beta_1^{\mathrm{OLS}}=2$，只要 $|\hat\beta_2^{\mathrm{OLS}}|\le1$，例如改成 $-0.5$ 或 $0.7$，解都仍是 $(1,0)$。嚴格的說法是：在 $P$ 點，RSS 下降最快的方向 $-\nabla\mathrm{RSS}=2(\hat\beta^{\mathrm{OLS}}-P)$ 落在法線扇形內；不是 RSS 梯度本身落在扇形內。</p>
  <p><strong>Ridge：沿圓周離開 $(1,0)$。</strong>限制換成 $\beta_1^2+\beta_2^2\le1$。把 $\beta_2$ 增加 $\varepsilon$，只需讓 $\beta_1=\sqrt{1-\varepsilon^2}\approx1-\varepsilon^2/2$。同一個 RSS 的變化變成</p>
  $$\Delta\mathrm{RSS}=4-4\sqrt{1-\varepsilon^2}-0.8\,\varepsilon\approx-0.8\,\varepsilon+2\varepsilon^2\lt0\quad(\varepsilon\text{ 很小}),$$
  <p>RSS 會下降，所以 Ridge 不會停在 $(1,0)$。</p>
""" + table(["", "Lasso（菱形）", "Ridge（圓）"],
            [["$\\beta_2$ 增加 $\\varepsilon$", "$\\beta_1$ 至少減少 $\\varepsilon$", "$\\beta_1$ 只需減少約 $\\varepsilon^2/2$"],
             ["離開座標軸的代價", "一階，$O(\\varepsilon)$", "二階，$O(\\varepsilon^2)$"]]) + r"""
  <p>尖角容易產生稀疏解，原因就在這裡：Lasso 離開座標軸必須付一階代價，只要 RSS 的一階好處不夠大，就寧願讓 $\beta_2=0$；Ridge 在座標軸附近只付二階代價，只要最小平方解的 $\beta_2\ne0$，稍微離開座標軸幾乎總是划算。</p>
""")

LASSO_PRIOR = viz(svg("w06priorSvg", 300),
     [info_card("怎麼看",
                '兩條曲線的變異數都是 1。按下按鈕切換成負對數密度，比較兩者在 0 附近的形狀：一個平滑、一個有尖角。'),
      rows_card("同變異數下比較（常態／Laplace）",
                [("0 點的密度", "0.399／0.707", "w06priorD0"),
                 ("$|\\beta|\\lt0.25$ 的機率", "0.197／0.298", "w06priorNear"),
                 ("$|\\beta|\\gt3$ 的機率", "0.0027／0.0144", "w06priorTail")])],
     "w06priorStatus", "Laplace 在 0 附近較高、尾部較厚；常態在 0 是平滑的圓頂。",
     '<button class="btn btn-toggle" id="w06priorBtn" onclick="w06priorToggle()">切換為負對數密度</button>',
     provenance=("illustrative", "概念示意：標準常態與 b=1/√2 的 Laplace，兩者變異數皆為 1"))

LASSO_RIDGE_R2 = r"""
  <h3 id="w06-lasso-ridge-r2">Lasso 與 Ridge 的模擬比較：橫軸為什麼用訓練 $R^2$</h3>
  <p>講義用兩張圖，把 Lasso 與 Ridge 的平方偏差、變異與測試 MSE 畫在一起。第一張的模擬資料中 45 個預測變數都和反應有關，Ridge 的測試 MSE 略低；第二張只有兩個變數有關，Lasso 明顯較好（何時選哪一個，見下方 Q&amp;A「Lasso 一定比 Ridge 好嗎？」）。</p>
  <p>兩張圖的橫軸都不是 $\lambda$，而是<strong>訓練資料上的 $R^2$</strong>。兩個方法的 $\lambda$ 量尺不同，同一個數字代表的收縮程度不一樣，直接用 $\lambda$ 對齊沒有意義。訓練 $R^2$ 是兩者共同的擬合指標：$\lambda$ 變大、正則化變強，訓練 $R^2$ 就下降。用它當橫軸，可以比較兩個方法在相同訓練擬合程度下的測試 MSE；它也可以當作模型複雜度的間接指標，沿著正則化路徑看偏差與變異怎麼交換。</p>
""" + detail("w06-detail-train-r2", "計算細節：訓練 $R^2$ 能當複雜度指標到什麼程度", r"""
  <p>對同一個方法，$\lambda$ 從大到小時，係數的限制愈來愈寬，訓練 RSS 不會上升，訓練 $R^2$ 因此單調增加：</p>
""" + table(["訓練 $R^2$", "正則化", "有效的模型複雜度"],
            [["低", "強（$\\lambda$ 大）", "較低"], ["高", "弱（$\\lambda$ 小）", "較高"]]) + r"""
  <p>限制是：訓練 $R^2$ 不等於正式的有效自由度。兩個方法在相同訓練 $R^2$ 下，用掉的自由度不一定相同，所以跨方法時只能說「訓練擬合程度相同」，不能說「模型複雜度完全相同」。Ridge 的有效自由度 $\mathrm{df}(\lambda)$ 見<a href="#w06-detail-primal-compute">三種限制式的計算成本</a>。</p>
""")

# ── P05 Lasso ─────────────────────────────────────────────────────────
BODIES["lasso"] = f"""
  <p>Ridge 的缺點是：它留下全部 $p$ 個變數。$p=500$ 的時候你得到 500 個很小但不為零的係數，
  模型一點也不好解釋。Lasso 把 L2 換成 <strong>L1</strong>：</p>

  $$\\mathrm{{RSS}} + \\lambda \\sum_{{j=1}}^{{p}} |\\beta_j|
    \\;=\\; \\mathrm{{RSS}} + \\lambda \\|\\beta\\|_1$$

  <p>只差一個平方，行為完全不同：<strong>$\\lambda$ 夠大時 Lasso 會把一部分係數壓成剛好 0</strong>，
  於是它同時做了收縮與變數選擇。這種解叫做<strong>稀疏</strong>（sparse）。</p>

{LASSO_WHY_INTRO}
{viz(svg("w06geomSvg", 380),
     [info_card("動手玩",
                '拖動滑桿縮小預算 $s$，看解怎麼被推出去。切換 L1／L2 比較兩者的接觸點：'
                '<strong>L1 的解常常「卡」在尖角上（某個係數變成剛好 0），'
                'L2 的解只是變小、方向幾乎不變。</strong>', "圖 6.7"),
      rows_card("這個 $s$ 之下的解",
                [("預算 $s$", "—", "w06geomS"), ("$\\beta_1$", "—", "w06geomB1"),
                 ("$\\beta_2$", "—", "w06geomB2"), ("有幾個剛好是 0", "—", "w06geomNz"),
                 ("RSS", "—", "w06geomRss")]),
      info_card("看不到尖角效應？",
                '把 $s$ 調到 1.5 以下，並注意橢圓的傾斜方向。'
                '$\\hat\\beta$ 的兩個座標差得愈多，尖角效應愈明顯。'
                '這也解釋了為什麼<strong>真實係數本來就稀疏</strong>時 Lasso 特別佔優勢。')],
     "w06geomStatus", "紅色橢圓是 RSS 等高線，藍色區域是約束。解在兩者相切處。",
     '<label class="slider-label" style="margin-right:.4rem;">預算 $s$</label>'
     '<input type="range" id="w06geomSl" min="20" max="400" step="5" value="200" '
     'oninput="w06geomMove()" style="flex:1 1 140px;max-width:200px;min-width:0;">'
     '<button class="btn btn-toggle" id="w06geomBtn" onclick="w06geomToggle()">切換為 L2（Ridge）</button>',
     provenance=("book-redraw", "依講義圖 6.7；約束最佳解以解析邊與 Lagrange 方程求得"))}
{LASSO_FAN}

{LASSO_WHY_DIAG}
{LASSO_WHY_BAYES}
{LASSO_PRIOR}
  <h3 id="w06-lasso-path">Credit 上的 Lasso 路徑</h3>
{viz(chart("w06lassoChart", "tall", "。此圖的重點：$\\lambda$ 變大時係數一個一個變成剛好 0，最後只剩幾個變數存活。"),
     [info_card("怎麼看",
                '跟 Ridge 那張圖同樣的畫法，但這裡的線會<strong>真的碰到 0 並停在 0</strong>。'
                '右側清單是在目前這個 $\\lambda$ 之下還沒被歸零的變數。', "圖 6.6"),
      rows_card("目前的 $\\lambda$",
                [("$\\lambda$", "—", "w06lassoLam"), ("非零係數", "—", "w06lassoNz"),
                 ("CV 選出的 $\\lambda$", "364.76", "w06lassoCv")]),
      info_card("保留的變數",
                '<div id="w06lassoVars" class="mono" style="font-size:.74rem;line-height:1.9;">—</div>')],
     "w06lassoStatus", "拖動滑桿看變數一個一個被淘汰。",
     '<label class="slider-label" style="margin-right:.4rem;">$\\log\\lambda$</label>'
     '<input type="range" id="w06lassoSl" min="0" max="39" step="1" value="24" '
     'oninput="w06lassoMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-reset" onclick="w06lassoCvJump()">跳到 CV 選出的 λ</button>',
     provenance=("course-data", "ISLP Credit 的標準化 Lasso 路徑；對照圖 6.6"))}

{card("講義 06 · Lasso 與被歸零的係數",
      lab_code(CH, 162) + "\n\n" + lab_code(CH, 172), lab_output(CH, 172), src=src("162、172"),
      note="這張卡用的是 Lab 的 Hitters 資料，和上圖的 Credit 不同。注意輸出裡有<strong>剛好等於 0</strong> 的係數。"
           "這是 Lasso 跟 Ridge 最實際的差別：你可以直接說「這些變數被模型丟掉了」。")}

{LASSO_RIDGE_R2}

{qa("觀念釐清", [
    ("Q：Lasso 一定比 Ridge 好嗎？",
     "<p>不一定，取決於<strong>真實的係數結構</strong>。</p>"
     "<p>如果真的只有少數幾個變數有用（真實係數稀疏），Lasso 佔優勢。它能把沒用的丟掉，"
     "省下估計它們所花的變異。如果<em>很多</em>變數都有小小的貢獻（係數密集），"
     "Ridge 通常較好——Lasso 會硬把一些真的有用的變數歸零，付出偏差的代價。</p>"
     "<p>而你事前並不知道是哪一種。實務作法是兩個都跑、用 CV 比較，"
     "或直接用 elastic net（同時放 L1 與 L2 懲罰）讓資料自己決定混合比例。</p>"),
    ("Q：Lasso 選出來的變數，可以說它們「顯著」嗎？",
     "<p>不能。Lasso 的變數選擇沒有附帶 p 值，而且「先用資料選變數、再對選出來的變數做 t 檢定」"
     "會嚴重高估顯著性。那是同一份資料用了兩次，與第 5 章的 CV 誤用有相同的問題。</p>"
     "<p>要做選後推論（post-selection inference）需要專門的方法"
     "（selective inference、debiased lasso 等），已經超出本課範圍。"
     "可以依實際的選擇結果說：<strong>「在這個 $\\lambda$ 之下，Lasso 保留了這些變數」</strong>，"
     "而不是「這些變數顯著」。</p>"),
    ("Q：兩個高度相關的變數，Lasso 會怎麼處理？",
     "<p>Lasso 可能只保留其中一個，選擇也可能隨資料的小變動而改變；但這不是因為多留一個變數就必然多付一份 L1 懲罰。</p>"
     "<p>若兩欄完全相同，係數 (2,0) 和 (1,1) 的預測相同，L1 懲罰也都等於 2，所以解的分配可能不唯一。高度相關但不完全相同時，微小差異及求解方式會影響最後保留哪一欄。解讀結果時，不能直接把被歸零的那欄判為沒有作用。</p>"
     "<p>Ridge 的平方懲罰在這個例子分別為 4 和 2，因此偏好分散係數；只有完全相同且同尺度的兩欄，對稱的 Ridge 解才精確平分。Elastic net 可促進相關欄一起保留；group lasso 則對事先指定的群組做整組選擇。</p>"),

])}

{quiz("qLasso", "QUIZ · Lasso 的幾何",
      "為什麼 L1 約束區域（菱形）會讓解落在座標軸上，而 L2（圓）不會？",
      [(True, "菱形的尖角剛好在座標軸上，橢圓等高線很容易先碰到尖角；圓處處平滑，碰到軸是機率 0 的事",
        "對。這是 ISLP 圖 6.7 的全部內容。維度更高時 L1 是超菱形，尖角與各種低維的稜、面都落在「某些座標為 0」的子空間上，所以稀疏解更容易發生。"),
       (False, "因為 L1 懲罰比 L2 懲罰強，把係數壓得更兇",
        "$\\lambda$ 可以調整懲罰強度；稀疏性來自約束區域的<strong>形狀</strong>與尖角。同樣的收縮量下，L2 只是縮短向量，L1 會把它推到軸上。"),
       (False, "因為 Lasso 用的是絕對值，絕對值函數在 0 沒有定義",
        "絕對值在 0 是有定義的（等於 0），只是<em>不可微</em>。不可微確實是機制的一部分（次微分在 0 是一整個區間），但「沒有定義」是錯的說法。")])}
"""

# ── P06 補充：為什麼用對數網格 ──────────────────────────────────────────
LAMBDA_LOG_GRID = r"""
  <p><strong>為什麼用對數等距？</strong>正則化的效果取決於 $\lambda$ 的相對大小，而不是絕對增量：同樣加 1，$\lambda$ 從 0 到 1 會讓係數縮掉一半，從 99 到 100 幾乎沒有差別。等距網格會在模型幾乎不變的大 $\lambda$ 區域放太多點；對數網格讓每個數量級分到差不多的點數，各種正則化尺度都涵蓋得到。實作上用 <code>np.logspace(-2, 5, 100)</code> 或 <code>10**np.linspace(a, b, 100)</code>。</p>
""" + viz(svg("w06gridSvg", 300),
     [info_card("怎麼看",
                '曲線是係數保留比例 $r(\\lambda)=1/(1+\\lambda)$。兩組網格都在 $[0.001,100]$ 取 10 個點：'
                '<span style="color:var(--accent);font-weight:700;">紅點</span>是等距網格，'
                '<span style="color:var(--accent2);font-weight:700;">藍點</span>是對數網格。'
                '切換橫軸，看哪一組點落在曲線真正變化的地方。'),
      rows_card("落在 0.001 到 1 之間的點數",
                [("等距網格", "1／10", "w06gridLin"), ("對數網格", "6／10", "w06gridLog")])],
     "w06gridStatus", "橫軸為 λ：等距網格幾乎全部落在曲線已經變平的右側。",
     '<button class="btn btn-toggle" id="w06gridBtn" onclick="w06gridToggle()">橫軸切換為 log₁₀ λ</button>',
     provenance=("illustrative", "概念示意：X 為單位矩陣時 Ridge 的保留比例；網格範圍自選")) + detail(
    "w06-detail-log-grid", "計算細節：最簡單的 Ridge 與係數保留比例", r"""
  <p>沿用 Lasso 節「解釋二」的對角設計（<a href="#w06-detail-diag-closed-form">推導</a>），Ridge 解為 $\hat\beta_j(\lambda)=y_j/(1+\lambda)$，所以係數保留比例是</p>
  $$r(\lambda)=\frac{\hat\beta_j(\lambda)}{y_j}=\frac1{1+\lambda}.$$
""" + table(["$\\lambda$", "係數保留比例 $r(\\lambda)$"],
            [["0", "100%"], ["0.1", "90.9%"], ["1", "50.0%"], ["10", "9.1%"], ["100", "1.0%"]]) + r"""
  <p>從 $\lambda=0$ 到 $1$，保留比例掉了一半；從 $\lambda=99$ 到 $100$，只從 1.00% 變成 0.99%。若搜尋範圍是 $[0.001,100]$，等距取 10 點時相鄰兩點差約 11.1，除了起點 0.001，其餘 9 點都落在 $\lambda\gt11$、保留比例不到 9% 的區域；對數等距時相鄰兩點的比值固定約 3.6，有 6 個點落在 $\lambda\lt1$。畫在 $\log\lambda$ 上，$r(\lambda)$ 是一條 S 形曲線，變化分散在好幾個數量級；畫在原尺度上，變化幾乎全擠在 $\lambda\lt10$ 的一小段。實際資料中，模型開始明顯改變的 $\lambda$ 事先不知道落在哪個數量級，所以在對數尺度上等距取點，讓每個數量級都分到點，也避免在模型幾乎不變的區域過度取樣。</p>
""")

# ── P06 怎麼選 λ ───────────────────────────────────────────────────────
BODIES["lambda"] = f"""
  <p>$\\lambda$ 是<strong>調整參數</strong>（tuning parameter），不是從資料估出來的參數。
  選它的方法跟第 5 章選多項式次數完全一樣：<strong>掃一排候選值，用交叉驗證比較。</strong></p>

  <ol>
    <li>選一排 $\\lambda$（通常是<strong>對數等距</strong>，例如從 $10^{{-2}}$ 到 $10^5$ 取 100 個點）。</li>
    <li>對每個 $\\lambda$ 做 k-fold CV，得到 CV 誤差。</li>
    <li>選 CV 誤差最小的 $\\lambda$，或用 one-SE 規則選一個更大（更收縮）的 $\\lambda$。</li>
    <li><strong>用全部資料在那個 $\\lambda$ 上重新擬合一次</strong>，交出這個模型。</li>
  </ol>

  <p>Credit 資料上 Lasso 的 CV 選出 $\\lambda=$ <strong>364.76</strong>，
  在那個 $\\lambda$ 之下 11 個變數全部仍保留。這份資料的係數並不稀疏，
  所以在這個設定下保留了全部變數。
  <strong>Lasso 是否產生零係數，取決於資料與 $\\lambda$ 的選擇。</strong></p>

{LAMBDA_LOG_GRID}

{card("講義 06 · 用 ElasticNetCV 選 $\\lambda$ 並取最小 CV 誤差",
      lab_code(CH, 168), lab_output(CH, 168), src=src("162、168"),
      note="<code>mse_path_</code> 的形狀是（$\\lambda$ 個數 $\\times$ 折數），"
           "<code>.mean(1)</code> 先對折取平均、再取最小值，就是 CV 曲線的最低點。"
           "這張 lab 卡同樣把 scaler 放在 <code>ElasticNetCV</code> 外層；若要在每一折內重新估縮放統計量，"
           "改用上面的 <code>GridSearchCV(Pipeline(...))</code> 結構。")}

{quiz("qLam", "QUIZ · 選 $\\lambda$",
      "用 CV 選好 $\\lambda$ 之後，最終交出的模型應該是？",
      [(True, "用全部資料、在選出的那個 $\\lambda$ 上重新擬合一次的模型",
        "對。CV 比較各個設定；每一折擬合出的模型只用了 $(k-1)/k$ 的資料。選好設定後，依本頁流程用全部訓練資料重新擬合。"),
       (False, "$k$ 折各自擬合出來的模型的平均",
        "線性模型可定義係數平均；非線性模型則缺少這種共同的係數平均定義。本頁的 CV 流程用來比較 $\\lambda$，選好後用全部訓練資料重新擬合。"),
       (False, "CV 誤差最小的那一折所擬合出來的模型",
        "那一折之所以誤差最小，很可能只是它的驗證資料剛好比較好預測。挑「運氣最好的一折」是選擇偏差的典型例子。")])}
"""

# ── P07 補充：投影、PCR 有利的模擬、Ridge 是連續版 PCR ──────────────────
PCR_PROJECTION = r"""
  <p>$Z_m=\sum_j\Phi_{jm}X_j$ 可以讀成<strong>投影</strong>：把第 $i$ 筆資料的 $p$ 個預測變數值 $(x_{i1},\ldots,x_{ip})$ 投影到方向 $(\Phi_{1m},\ldots,\Phi_{pm})$ 上，得到一個數，就是得分 $z_{im}=\sum_j\Phi_{jm}x_{ij}$。取 $M$ 個方向，就把每筆資料從 $p$ 個數換成 $M$ 個新特徵。PCA 的方向讓投影後的得分變異最大；這和「重建誤差最小」是同一件事，也和第 4 章 Fisher 判別的寫法形式類似，推導見本節末的<a href="#w06-detail-pca-objectives">收合區</a>。</p>
""" + detail("w06-detail-projection", "計算細節：得分是投影座標的條件", r"""
  <p>中心化之後，若方向滿足 $\sum_{j=1}^p\Phi_{jm}^2=1$，$z_{im}=\sum_j\Phi_{jm}x_{ij}$ 就是第 $i$ 筆資料沿該方向的<strong>正交投影座標</strong>：投影點的第 $j$ 個座標是 $z_{im}\Phi_{jm}$，剩下的殘差 $x_{ij}-z_{im}\Phi_{jm}$ 與方向垂直，因為</p>
  $$\sum_{j=1}^p\big(x_{ij}-z_{im}\Phi_{jm}\big)\Phi_{jm}=z_{im}-z_{im}\sum_j\Phi_{jm}^2=0 .$$
  <p>方向長度不是 1 時，$z_{im}$ 只是一般的線性組合，數值會隨長度等比例縮放；這也是 PCA 要加上 $\sum_j\Phi_{jm}^2=1$ 的原因，否則把 $\Phi$ 放大就能讓變異無限變大。若 $M$ 個方向彼此正交（$\sum_j\Phi_{jm}\Phi_{jl}=0$，$m\ne l$），每筆資料在這 $M$ 個方向上的投影點為 $\sum_{m=1}^Mz_{im}\Phi_{jm}$，等於把 $p$ 維資料投影到 $M$ 維子空間。</p>
""")

PCR_SIM = r"""
  <p>什麼資料對 PCR 有利？講義用一組模擬資料示範：<strong>$X$ 的前五個主成分包含關於 $Y$ 的全部資訊</strong>。此時 PCR 的測試 MSE 在 $M=5$ 有明顯的最小值；Ridge 與 Lasso 也都比最小平方好，但 PCR 和 Ridge 略勝 Lasso。要注意，只有前五個主成分和 $Y$ 有關，不代表只有前五個原始變數和 $Y$ 有關。</p>
""" + detail("w06-detail-pcr-sim", "計算細節：如何生成「訊號集中在前幾個主成分」的資料", r"""
  <p>講義與課本只說明反應完全由前五個主成分決定，沒有列出全部設定。下面用講義的符號寫出一種符合這個描述的生成方式：先產生主成分得分，讓 $Y$ 只依賴前 5 個得分，再把得分「轉回」原始預測變數。</p>
  <p><strong>第一步：產生主成分得分。</strong>對 $i=1,\ldots,n$、$m=1,\ldots,p$，獨立抽 $z_{im}\sim N(0,\sigma_m^2)$，並取 $\sigma_1^2\gt\sigma_2^2\gt\cdots\gt\sigma_p^2\gt0$，讓前面的成分變異較大。</p>
  <p><strong>第二步：用正交方向產生原始預測變數。</strong>選一組彼此正交的單位方向 $\Phi_{jm}$，滿足 $\sum_{j=1}^p\Phi_{jm}\Phi_{jl}=1$（$m=l$）或 $0$（$m\ne l$），令</p>
  $$x_{ij}=\sum_{m=1}^p z_{im}\Phi_{jm},\qquad j=1,\ldots,p .$$
  <p>此時 $\operatorname{Cov}(X_j,X_k)=\sum_m\sigma_m^2\Phi_{jm}\Phi_{km}$，原始變數通常彼此相關；母體的主成分方向正是 $\Phi_{\cdot m}$，變異依序為 $\sigma_m^2$。正交性也讓得分可以反解回來：$z_{im}=\sum_j\Phi_{jm}x_{ij}$。</p>
  <p><strong>第三步：讓 $Y$ 只依賴前 5 個得分。</strong></p>
  $$y_i=\theta_0+\sum_{m=1}^{5}\theta_m z_{im}+\varepsilon_i,\qquad \varepsilon_i\sim N(0,\sigma^2)\ \text{且與得分獨立}.$$
  <p>前五個成分包含全部可預測的訊號，第 6 到第 $p$ 個成分與 $Y$ 沒有額外關係。代回 $z_{im}=\sum_j\Phi_{jm}x_{ij}$，就得到講義降維一節的係數關係：</p>
  $$y_i=\theta_0+\sum_{j=1}^p\beta_jx_{ij}+\varepsilon_i,\qquad \beta_j=\sum_{m=1}^{5}\theta_m\Phi_{jm}.$$
  <p>$\Phi_{jm}$ 一般不為 0，所以 $\beta_1,\ldots,\beta_p$ 通常全部不為 0。<strong>主成分空間裡的稀疏，不等於原始變數空間裡的稀疏。</strong></p>
""" + table(["方法", "在這個模擬中的情況"],
            [["PCR（$M=5$）", "保留全部有效訊號，丟掉其餘 $p-5$ 個無關方向"],
             ["Ridge", "把變異小的方向縮得多、變異大的方向縮得少（見下方對照），效果接近 PCR"],
             ["Lasso", "在原始變數上做選擇；真實的 $\\beta_j$ 並不稀疏，它的長處用不上"]]) + r"""
  <p>有限樣本中，對 $X$ 算出的樣本主成分只會近似 $\Phi_{\cdot m}$，所以 PCR 用前五個樣本主成分時，只能近似地抓到全部訊號。若要在樣本中精確做到，可以先對已產生的 $x_{ij}$ 做 PCA，再用樣本得分代入第三步產生 $y_i$。反過來，若真實係數在原始變數上就稀疏（例如只有兩個 $\beta_j$ 不為 0），Lasso 才會佔優。</p>
""")

PCR_RIDGE = detail(
    "w06-detail-ridge-pcr", "延伸（超出講義範圍）：Ridge 是連續版的 PCR", r"""
  <p>把資料改用主成分得分當座標後，兩種方法的擬合值都能寫成各主成分方向的貢獻相加，差別只在每個方向乘上的收縮因子：PCR 對前 $M$ 個方向乘 1、其餘乘 0；Ridge 對第 $m$ 個方向乘 $d_m^2/(d_m^2+\lambda)$，其中 $d_m^2=\sum_iz_{im}^2$ 隨 $m$ 遞減。變異大的方向幾乎不縮，變異小的方向縮得最多，Ridge 因此像是把 PCR 的「留或丟」換成平滑的漸進收縮（ESL 第 3.4.1、3.5.1 節）。</p>
""" + viz(svg("w06shrinkSvg", 300),
     [info_card("怎麼看",
                '橫軸是主成分編號 $m$，縱軸是該方向的收縮因子。'
                '<span style="color:var(--accent2);font-weight:700;">藍點</span>是 Ridge 的 $d_m^2/(d_m^2+\\lambda)$，'
                '<span style="color:var(--accent);font-weight:700;">紅線</span>是 PCR 的 1／0 階梯。'
                '$d_m^2$ 為自選的遞減數值。'),
      rows_card("有效自由度",
                [("Ridge：$\\sum_m d_m^2/(d_m^2+\\lambda)$", "—", "w06shrinkDf"),
                 ("PCR：保留的方向數 $M$", "—", "w06shrinkM")])],
     "w06shrinkStatus", "λ 變大時，Ridge 的收縮因子從變異小的方向開始往 0 掉。",
     '<label class="slider-label" style="margin-right:.4rem;">$\\log_{10}\\lambda$</label>'
     '<input type="range" id="w06shrinkLam" min="-10" max="30" step="1" value="10" '
     'oninput="w06shrinkDraw()" style="flex:1 1 120px;max-width:180px;min-width:0;">'
     '<label class="slider-label" style="margin:0 .4rem 0 .8rem;">$M$</label>'
     '<input type="range" id="w06shrinkMSl" min="1" max="10" step="1" value="4" '
     'oninput="w06shrinkDraw()" style="flex:1 1 100px;max-width:150px;min-width:0;">',
     provenance=("illustrative", "概念示意：自選 d_m² = 100·0.6^(m−1)，m = 1,…,10；對照 ESL 圖 3.17 的收縮因子")) + r"""
  <p><strong>計算細節。</strong></p>
  <p>設 $x_{ij}$、$y_i$ 都已中心化，且 $n\gt p$、沒有完全共線。令 $\Phi_{jm}$（$m=1,\ldots,p$）是全部 $p$ 個主成分方向，彼此正交且長度為 1；得分 $z_{im}=\sum_j\Phi_{jm}x_{ij}$。主成分得分兩兩不相關：$\sum_iz_{im}z_{il}=0$（$m\ne l$），並記 $d_m^2=\sum_{i=1}^nz_{im}^2$，依 $m$ 遞減。$d_m^2$ 就是 $n$ 倍的第 $m$ 個特徵值 $\ell_m$（用 $\frac1n$ 的慣例，見本節末的<a href="#w06-detail-pca-objectives">收合區</a>）；模擬資料裡的母體變異 $\sigma_m^2$ 是它的母體對應。</p>
  <p><strong>換座標。</strong>任何線性預測都能改寫：令 $\theta_m=\sum_j\Phi_{jm}\beta_j$，因為方向正交，</p>
  $$\sum_{j=1}^p\beta_jx_{ij}=\sum_{m=1}^p\theta_mz_{im},\qquad \sum_{j=1}^p\beta_j^2=\sum_{m=1}^p\theta_m^2 .$$
  <p>第二式表示旋轉不改變係數的長度，所以 Ridge 的懲罰在新座標下形式不變。</p>
  <p><strong>Ridge 拆成 $p$ 個一維問題。</strong>展開平方，交叉項因得分正交而消失：</p>
  $$\sum_i\Big(y_i-\sum_m\theta_mz_{im}\Big)^2+\lambda\sum_m\theta_m^2=\sum_iy_i^2+\sum_{m=1}^p\Big[(d_m^2+\lambda)\theta_m^2-2\theta_m\sum_iz_{im}y_i\Big].$$
  <p>每個 $\theta_m$ 各自最小化方括號，得</p>
  $$\hat\theta_m^{\mathrm{ridge}}=\frac{\sum_iz_{im}y_i}{d_m^2+\lambda}=\frac{d_m^2}{d_m^2+\lambda}\,\hat\theta_m,\qquad \hat\theta_m=\frac{\sum_iz_{im}y_i}{d_m^2},$$
  <p>其中 $\hat\theta_m$ 是 $y$ 對第 $m$ 個得分做簡單迴歸的係數，也就是 PCR 在該方向的係數。兩種方法的擬合值因此是</p>
  $$\hat y_i^{\mathrm{ridge}}=\sum_{m=1}^p\frac{d_m^2}{d_m^2+\lambda}\,\hat\theta_mz_{im},\qquad \hat y_i^{\mathrm{PCR}}=\sum_{m=1}^M\hat\theta_mz_{im}.$$
  <p>PCR 的收縮因子是 1（$m\le M$）或 0（$m\gt M$）；Ridge 的收縮因子 $d_m^2/(d_m^2+\lambda)$ 介於 0 與 1 之間、隨 $m$ 遞減。原始係數用 $\beta_j=\sum_m\Phi_{jm}\theta_m$ 換回。</p>
  <p><strong>有效自由度。</strong>由上式，中心化後的斜率部分 $\hat y_i^{\mathrm{ridge}}=\sum_k h_{ik}(\lambda)y_k$，$h_{ik}(\lambda)=\sum_m z_{im}z_{km}/(d_m^2+\lambda)$。對角元素加總得</p>
  $$\mathrm{df}(\lambda)=\sum_{i=1}^nh_{ii}(\lambda)=\sum_{m=1}^p\frac{d_m^2}{d_m^2+\lambda},$$
  <p>從 $\lambda=0$ 時的 $p$ 平滑降到 $\lambda\to\infty$ 時的 0；PCR 用 $M$ 個方向時自由度就是 $M$。這就是前面 <a href="#w06-detail-primal-compute">GCV</a> 用到的 $\mathrm{df}(\lambda)$；加回截距那一份 $1/n$，才是留一捷徑裡的 $h_{ii}(\lambda)$。這套推導是 ESL 第 3.4.1 節（式 3.47）與第 3.5.1 節（圖 3.17）的純量寫法。</p>
""")

# ── P07 PCR ───────────────────────────────────────────────────────────
BODIES["pcr"] = f"""
  <p>第三條路：<strong>不動變數，改換座標。</strong>先把 $p$ 個相關的預測變數壓成
  $M$ 個互不相關的方向（$M\\ll p$），再對這 $M$ 個方向做最小平方。</p>

  <p>主成分迴歸（principal components regression, PCR）用的方向就是第 12 章的主成分：
  第一主成分是 $X$ 變異最大的方向，第二個是在跟第一個正交的條件下變異最大的方向，依此類推。</p>

  $$Z_m = \\sum_{{j=1}}^{{p}} \\Phi_{{jm}} X_j, \\qquad
    y_i = \\theta_0 + \\sum_{{m=1}}^{{M}} \\theta_m z_{{im}} + \\varepsilon_i$$

  <p>$M$ 是調整參數，同樣用 CV 選。$X$ 滿欄秩且 $M=p$ 時 PCR 就退回最小平方（只是換了個座標）；
  $M$ 小的時候，被丟掉的那些低變異方向就是被收縮掉的部分。</p>

{PCR_PROJECTION}

{viz(svg("w06dirSvg", 340),
     [info_card("PCA 方向 vs PLS 方向",
                '拖動滑桿改變 $y$ 對兩個 $x$ 的依賴方向。'
                '<span style="color:var(--accent2);font-weight:700;">藍線 PC1</span> '
                '只看 $X$ 的散佈，所以<strong>完全不動</strong>；'
                '<span style="color:var(--accent);font-weight:700;">紅線 PLS1</span> '
                '也看 $y$，所以會跟著轉。', "圖 6.14–6.15"),
      rows_card("目前的方向",
                [("$y$ 的真實方向", "—", "w06dirTrue"), ("PC1 方向", "—", "w06dirPca"),
                 ("PLS1 方向", "—", "w06dirPls"),
                 ("PC1 與真實方向的夾角", "—", "w06dirAng")]),
      info_card("這說明了什麼",
                'PCR 的方向<strong>完全是非監督式的</strong>。當「$X$ 變異大的方向也是跟 $y$ 有關的方向」時，截取主成分較可能保留預測訊號。'
                '這個假設常常成立，但沒有保證。PLS 讓 $y$ 參與挑方向，'
                '因此可能保留 PCR 忽略的訊號，但測試表現仍須驗證。')],
     "w06dirStatus", "灰點是資料，兩條線分別是 PC1 與 PLS1 的方向。",
     '<label class="slider-label" style="margin-right:.4rem;">$y$ 的方向</label>'
     '<input type="range" id="w06dirSl" min="0" max="180" step="3" value="20" '
     'oninput="w06dirMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-reset" onclick="w06dirReset()">重置</button>',
     provenance=("illustrative", "依講義圖 6.14–6.15 的 PCR／PLS 方向差異示意"))}

{card("講義 06 · 用 CV 選主成分個數 $M$",
      lab_code(CH, 182), None, src=src("180、182"),
      note="<code>pca__n_components</code> 這種雙底線寫法是 <code>Pipeline</code> 的參數命名慣例："
           "步驟名 ＋ <code>__</code> ＋ 該步驟的參數名。標準化同樣包在 pipeline 裡，"
           "PCA <strong>必須</strong>在標準化之後做——不然變異數大的變數會主宰第一主成分。")}

{card("講義 06 · 各主成分解釋了多少變異", lab_code(CH, 188), lab_output(CH, 188), src=src("188"),
      note="<code>explained_variance_ratio_</code> 就是第 12 章的 PVE。"
           "累加起來可以回答「留幾個主成分才夠」。")}

{PCR_SIM}

{PCR_RIDGE}

{qa("觀念釐清", [
    ("Q：PCR 算不算變數選擇？",
     "<p>不算。每一個主成分都是<strong>全部 $p$ 個原始變數的線性組合</strong>，"
     "所以就算只留 $M=2$，最終模型仍可能需要全部原始欄位；個別 loading 可為零。</p>"
     "<p>這是 PCR 跟 Lasso 最重要的差別：Lasso 給你「這 5 個變數有用、其餘丟掉」；"
     "PCR 給你「這 2 個方向有用」，而每個方向都攪拌了所有變數。"
     "後者在解釋上通常更難。你得去看 loadings 才知道那個方向大致代表什麼。</p>"),
    ("Q：PCR 之前為什麼一定要標準化？",
     "<p>因為主成分是「變異最大的方向」，而變異數的大小完全取決於單位。</p>"
     "<p>Credit 資料裡 <code>Limit</code> 的數值是幾千、<code>Cards</code> 是個位數。"
     "不標準化的話，第一主成分幾乎就等於 <code>Limit</code> 本身——"
     "這主要反映單位造成的尺度差異，不能直接當成重要性。第 12 章的 USArrests biplot 也呈現這個現象。</p>"),
])}

{quiz("qPcr", "QUIZ · PCR",
      "PCR 用 $M=2$ 個主成分。最終模型用到了幾個原始預測變數？",
      [(True, "可能仍用到全部 $p$ 個；$M$ 指成分數，並非原始變數數量",
        "對。PCR 不做變數選擇。這是它跟 Lasso 最重要的差別。它把 $p$ 維壓進 $M$ 維；一般仍可能需要全部原始欄位，個別 loading 則可以為零。"),
       (False, "2 個，就是 loadings 最大的那兩個",
        "$M=2$ 指的是<strong>主成分</strong>的個數，不是原始變數的個數。每個主成分的 loading 向量長度都是 $p$，而且通常每一項都不為零。"),
       (False, "不確定，要看 CV 選出多少",
        "CV 選的是 $M$（主成分個數）。保留的 loading 決定哪些原始變數有貢獻；$M$ 不是所用原始變數的個數。")])}
"""

# ── P08 補充：PCR 與 PLS 的目標式 ──────────────────────────────────────
PLS_OBJECTIVES = r"""
  <p>兩種方法的差別，寫成第一個方向的目標式最清楚。設各 $X_j$ 已標準化，方向長度固定為 1：</p>
  $$\text{PCR：}\ \max_{\sum_j\Phi_{j1}^2=1}\ \operatorname{Var}\Big(\sum_{j=1}^p\Phi_{j1}X_j\Big),\qquad
    \text{PLS：}\ \max_{\sum_j\Phi_{j1}^2=1}\ \operatorname{Corr}^2\Big(Y,\sum_{j=1}^p\Phi_{j1}X_j\Big)\operatorname{Var}\Big(\sum_{j=1}^p\Phi_{j1}X_j\Big).$$
  <p>PCR 只要新特徵散得開；PLS 還要求它和 $Y$ 有關，化簡後等於找與 $Y$ 共變異平方最大的線性組合。上面講義用簡單迴歸係數當權重的作法，正好就是這個最佳化的解；推導與後續方向的算法見本節末的<a href="#w06-detail-pls-covariance">收合區</a>。</p>
"""

# ── P08 PLS ───────────────────────────────────────────────────────────
BODIES["pls"] = f"""
  <p>PCR 挑方向時<strong>完全沒看 $y$</strong>。若想讓 $y$ 也參與方向的選擇，可以使用 PLS。</p>

  <p>偏最小平方（partial least squares, PLS）修掉這一點：第一個方向的權重直接取
  $\\Phi_{{j1}} \\propto$ 每個 $X_j$ 與 $y$ 的簡單線性迴歸係數，
  也就是<strong>跟 $y$ 相關性愈強的變數，權重愈大</strong>。
  取完第一個方向後，把各變數對它迴歸取殘差，再在殘差上重複同樣的步驟得到第二個方向。</p>

{PLS_OBJECTIVES}

  <p>上一節的互動示範了這個差別：拖滑桿改變 $y$ 的方向，PLS1 跟著轉、PC1 不動。</p>

{table(["", "方向怎麼挑", "有沒有用到 $y$", "做變數選擇嗎", "何時較好"],
       [["PCR", "$X$ 變異最大的方向", "沒有", "沒有", "$X$ 的主要變異方向剛好跟 $y$ 有關時"],
        ["PLS", "單位權重下與 $y$ 共變異最大的方向", "有", "沒有", "$X$ 的大變異方向跟 $y$ 無關時"],
        ["Ridge", "不換座標，全部收縮", "有（擬合時）", "沒有", "很多變數都有小貢獻"],
        ["Lasso", "不換座標，部分歸零", "有（擬合時）", "<strong>有</strong>", "真實係數稀疏"]])}

  <p>實務上 PLS 的表現常常<strong>跟 PCR 差不多</strong>，有時還略差。原因是：
  它雖然降低了偏差（方向跟 $y$ 有關），但也增加了變異（方向是估出來的，而且用到了 $y$）。
  ISLP §6.3.2 的結論就是這樣：PLS 沒有一致地贏過 PCR 或 Ridge。</p>

{card("講義 06 · 用 CV 選 PLS 的成分個數", lab_code(CH, 194), None, src=src("192、194"),
      note="<code>PLSRegression</code> 的 <code>n_components</code> 跟 PCR 的 "
           "<code>n_components</code> 是同一個角色的調整參數，一樣用 CV 選。"
           "注意它預設 <code>scale=True</code>，已經幫你標準化了。")}

{quiz("qPls", "QUIZ · PLS",
      "PLS 相對於 PCR 的差別是什麼？",
      [(True, "挑方向時用到了 $y$，所以方向會跟著 $y$ 轉；但降維與不做變數選擇這兩點跟 PCR 一樣",
        "對。這是「監督式降維」對「非監督式降維」。也因為方向是用 $y$ 估出來的，PLS 的變異比 PCR 大，兩者實務上常表現相近。"),
       (False, "PLS 會把不重要的變數歸零，所以比 PCR 好解釋",
        "不會。歸零是 <strong>Lasso</strong> 的性質。PLS 的每個成分仍然是全部 $p$ 個變數的線性組合。"),
       (False, "PLS 不需要標準化，PCR 需要",
        "兩者都需要，理由相同（方向的定義對單位敏感）。<code>PLSRegression</code> 只是預設 <code>scale=True</code> 幫你做了。")])}
"""

# ── P09 高維度 ─────────────────────────────────────────────────────────
BODIES["highdim"] = f"""
  <p>基因資料、文字資料、感測器資料常常是 <strong>$p$ 遠大於 $n$</strong>：
  幾萬個變數、幾百個樣本。這時候傳統最小平方的<strong>唯一係數解與一般推論不再適用</strong>，需要額外的結構或選解規則。</p>

  <p>當 $p\\ge n$，且含截距的設計矩陣有 $n$ 個獨立的列時，最小平方能
  <strong>完美擬合訓練資料</strong>：$\\mathrm{{RSS}}=0$；$y$ 非常數時訓練 $R^2=1$。
  這只說明模型能插值，不代表一定能或一定不能預測新資料。係數通常不唯一，
  必須說明如何選解，再用獨立資料評估；不能拿訓練滿分當作泛化證據。</p>

{""}

{info("在高維度千萬不要相信這三個數字", '''<strong>1. 訓練資料上的 $R^2$。</strong>
  模型有足夠自由度時它可能接近 1；泛化表現仍須用未參與訓練的資料評估。<br>
  <strong>2. 訓練資料上的 RSS 或 MSE。</strong>同理，可能接近 0；測試誤差需要另外評估。<br>
  <strong>3. 用同一份資料選完變數之後算出來的 p 值。</strong>
  從幾萬個變數裡挑「最顯著」的，一定挑得到看起來很顯著的，那是多重比較，不是發現。<br><br>
  唯一能信的是<strong>在完全沒參與過任何選擇的資料上</strong>算出來的誤差——
  獨立的測試集，或將所有選擇步驟留在訓練折內的交叉驗證（第 5 章 P06）。''', "warm")}

{qa("觀念釐清", [
    ("Q：$p&gt;n$ 的時候「維度的詛咒」到底詛咒了什麼？",
     "<p><strong>新增變數也會增加估計的不確定性。</strong></p>"
     "<p>每個新增變數都需要花"
     "自由度去估它的係數，而估計本身帶進變異。一個跟 $y$ 完全無關的變數，"
     "它的係數估計值是一個隨機的小數字，通常會偏離 0。那個隨機性直接進到預測裡。</p>"
     "<p>若加入的變數沒有提供新的預測資訊，"
     "加入更多候選變數後，訓練誤差下降，測試誤差卻可能上升。"
     "<strong>因此要用獨立評估判斷新增變數是否值得保留。</strong></p>"),
    ("Q：那高維度該用什麼？",
     "<p>這一章的三類工具全部都是為此設計的："
     "<strong>子集／逐步選擇</strong>（明確減少變數）、"
     "<strong>收縮</strong>（Ridge 與 Lasso，Lasso 還順便選變數）、"
     "<strong>降維</strong>（PCR 與 PLS）。它們的共同點是<em>降低變異，代價是接受一點偏差</em>。</p>"
     "<p>在 $p\\gg n$ 的場景，Lasso 與 elastic net 特別受歡迎，因為稀疏假設常常合理"
     "（幾萬個基因裡有關的通常只有少數幾個），而且結果可以直接列出「這幾個變數」。</p>"),
])}

{""}

"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 6.6 第 1 題（b）",
      "最佳子集、forward stepwise、backward stepwise 各自選出的「$k$ 個變數的最佳模型」中，"
      "<strong>測試</strong>誤差最低的會是哪一個？",
      [(True, "不確定。三者都有可能，因為測試誤差要看運氣，而三者選出的模型未必相同",
        "對。第 (a) 小題問的是<strong>訓練</strong> RSS，那個答案很確定（最佳子集必定最小或相等，因為它搜了全部）。測試誤差需要獨立評估；搜尋範圍擴大，也會增加選到恰好貼合訓練雜訊之模型的機會。"),
       (False, "最佳子集，因為它搜遍所有可能的模型",
        "這是第 (a) 小題「訓練 RSS」的答案。搜尋較廣可降低訓練 RSS，也可能擬合到更多訓練雜訊；測試誤差仍須另外評估。"),
       (False, "forward stepwise，因為它的搜尋空間小所以變異低",
        "forward stepwise 通常有<em>較低的變異</em>；測試誤差還受偏差與資料影響。題目要求確定指出贏家，這些資訊不足以決定。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 6.6 第 2 題（a）",
      "相對於最小平方，Lasso 的特性是？",
      [(True, "彈性較低，因此當「變異的下降」大於「偏差的上升」時，預測準確度會更好",
        "對。這是課本要的標準答案句型。三個小題（Lasso／Ridge／非線性方法）的差別只在彈性是低還是高——Lasso 與 Ridge 都是<strong>降低</strong>彈性換取變異的下降。"),
       (False, "彈性較高，因此當「偏差的下降」大於「變異的上升」時會更好",
        "這是第 (c) 小題<strong>非線性方法</strong>的答案。Lasso 加了懲罰項，它的彈性比最小平方<em>低</em>，不是高。"),
       (False, "彈性一樣，只是係數的解不同",
        "不一樣。$\\lambda=0$ 時兩者相同，但 $\\lambda&gt;0$ 時 Lasso 的解空間被約束住了（$\\|\\beta\\|_1\\le s$），那就是彈性較低。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 6.6 第 4 題",
      "Ridge 的懲罰參數 $\\lambda$ 從 0 開始往上增加。<strong>訓練</strong> RSS 會怎麼變化？",
      [(True, "單調上升",
        "對。$\\lambda=0$ 時就是最小平方，它<strong>定義上</strong>就是訓練 RSS 的最小值；任何約束都只會讓訓練 RSS 變大或不變。同一題還問了測試 RSS（先降後升的 U 型）、變異（單調下降）、偏差$^2$（單調上升）、不可縮減誤差（不變）。"),
       (False, "先下降再上升，呈 U 型",
        "這是<strong>測試</strong> RSS 的形狀。訓練 RSS 沒有 U 型。它在 $\\lambda=0$ 就已經是最小的了。"),
       (False, "單調下降",
        "方向相反。加懲罰只會讓「訓練 RSS 這個目標」被犧牲掉一部分，換取係數變小。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 6.6 第 9 題",
      "課本第 9 題在 <code>College</code> 資料上比較最小平方、Ridge、Lasso、PCR、PLS 的測試誤差。"
      "預期會看到什麼？",
      [(True, "需以相同資料切分與各自的調參程序比較，不能預先指定勝負",
        "資料維度與相關結構可提供線索，但不能代替實際的獨立測試。比較前應固定切分，將標準化、降維與調參都留在訓練資料內。"),
       (False, "PCR 與 PLS 明顯勝出，因為它們降了維",
        "降維可能減少變異，也可能丟失與 $y$ 有關的方向；$n$ 大於 $p$ 並不能保證最小平方或降維模型誰比較好。"),
       (False, "Lasso 一定最好，因為它同時做收縮與變數選擇",
        "Lasso 的優勢要在<strong>真實係數稀疏</strong>時才顯現。若很多變數都有小貢獻，把它們歸零反而引入偏差，Ridge 會較好。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前可用這一頁複習各種方法的差別。</p>

  <h3>三類工具對照</h3>
{table(["", "做什麼", "調整參數", "會歸零嗎", "運算成本", "何時最適合"],
       [["最佳子集", "搜遍 $2^p$ 個模型", "模型大小 $k$", "會（沒選就是 0）", "$2^p$，窮舉在 $p&gt;40$ 左右不可行", "$p$ 很小"],
        ["Forward／backward", "貪婪地一次加／減一個", "模型大小 $k$", "會", "$1+p(p+1)/2$", "$p$ 中等"],
        ["Ridge（L2）", "全部係數一起收縮", "$\\lambda$", "<strong>不會</strong>", "很快，有封閉解", "很多變數都有小貢獻"],
        ["Lasso（L1）", "收縮 ＋ 部分歸零", "$\\lambda$", "<strong>會</strong>", "很快（座標下降）", "真實係數稀疏"],
        ["PCR", "換成 $M$ 個非監督式方向", "$M$", "不會（用到全部變數）", "很快", "$X$ 的大變異方向跟 $y$ 有關"],
        ["PLS", "換成 $M$ 個監督式方向", "$M$", "不會（用到全部變數）", "很快", "$X$ 的大變異方向跟 $y$ 無關"]])}

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["$C_p$", "$\\frac{1}{n}(\\mathrm{RSS} + 2d\\hat\\sigma^2)$", "式 6.2"],
        ["AIC", "$\\frac{1}{n\\hat\\sigma^2}(\\mathrm{RSS} + 2d\\hat\\sigma^2)$", "式 6.3，常態誤差下與 $C_p$ 等價"],
        ["BIC", "$\\frac{1}{n}(\\mathrm{RSS} + \\log(n)\\,d\\hat\\sigma^2)$", "式 6.3，$\\log n > 2$ 時罰得比 $C_p$ 重"],
        ["調整後 $R^2$", "$1 - \\frac{\\mathrm{RSS}/(n-d-1)}{\\mathrm{TSS}/(n-1)}$", "式 6.4"],
        ["Ridge", "$\\mathrm{RSS} + \\lambda\\sum_j \\beta_j^2$", "式 6.5，對應限制式 $\\sum_j\\beta_j^2 \\le s$（見 Lasso 節的限制式與懲罰式）"],
        ["Lasso", "$\\mathrm{RSS} + \\lambda\\sum_j |\\beta_j|$", "式 6.7，對應限制式 $\\sum_j|\\beta_j| \\le s$"],
        ["主成分方向", "$Z_m = \\sum_j \\Phi_{jm} X_j$", "式 6.16，$\\Phi$ 由 $X$ 的變異決定"]])}

{info("四個一定要記住的觀念", '''<strong>1. 三條路：選變數、收縮係數、換座標。</strong>
  共同點都是降低變異，代價是接受一點偏差。<br>
  <strong>2. L1 會歸零、L2 不會，差別在形狀不在強弱。</strong>
  菱形有尖角而尖角落在座標軸上；圓沒有。<br>
  <strong>3. Ridge、Lasso、PCR、PLS 之前都必須標準化。</strong>
  它們的目標函數對單位敏感，最小平方的預測則不受換單位影響。<br>
  <strong>4. 高維度時訓練 $R^2$ 可能接近 1，不能據此判斷泛化。</strong>
  只信沒參與過任何選擇的資料上算出來的誤差。''')}


"""

# ══════════════════════════════════════════════════════════════════════

# 最新講義主題補全；維持既有 section 與導覽。
BODIES['lasso'] += r"""
<h3>收縮的貝氏解讀</h3>
<p>獨立常態誤差、固定誤差變異數與不懲罰截距的設定下，高斯斜率先驗的 MAP 對應 Ridge，Laplace 斜率先驗的 MAP 對應 Lasso。其 RSS 目標的 $\lambda$ 分別為 $\sigma^2/\tau^2$ 與 $2\sigma^2/b$。完整常數對應見下方證明。</p>
"""
BODIES['pcr'] += r"""
<h3>從共變異數到白化</h3>
<p>以下採每列一筆觀察的中心化矩陣 $X\in\mathbb R^{n\times p}$。若 $X=UDV^T$，則樣本共變異數 $S=X^TX/(n-1)=V\Lambda V^T$，其中 $\Lambda=D^2/(n-1)$（對角元素是特徵值 $\ell_j$，此處 $\Lambda$ 與懲罰參數 $\lambda$ 無關）。主成分方向是 $V$ 的欄，得分為 $XV=UD$；主成分方向滿足 $Sv=\ell v$；最大變異與重建誤差的關係見下方證明。講義也使用每欄一筆觀察的排列；對照公式時要連同矩陣一起轉置。</p>
<p>保留正特徵值方向後，白化得分 $Z=XV\Lambda^{-1/2}$ 的樣本共變異數為單位矩陣。ZCA 白化再乘上 $V^T$ 回到原特徵座標；保留全部正秩方向且滿秩時為 $XV\Lambda^{-1/2}V^T$。白化會把低變異方向放大，因此小特徵值可能放大雜訊；普通 PCR 不需要白化，也不能把白化當成保證改善預測的步驟。</p>
""" + proof('w06proofWhiten', '白化得分的共變異數為單位矩陣', r"""
<p>若 $X=UDV^T$，則 $S=VD^2V^T/(n-1)$，特徵值為 $d_j^2/(n-1)$，得分為 $UD$。只保留正特徵值，令 $Z=XV_r\Lambda_r^{-1/2}$，其樣本共變異數為 $\Lambda_r^{-1/2}V_r^TSV_r\Lambda_r^{-1/2}=I_r$。ZCA 的回投影 $ZV_r^T$ 在 $p$ 維中的共變異數為 $V_rV_r^T$，只有 $r=p$ 時才是 $I_p$。</p>
""")

# COVERAGE-20260910 BEGIN

BODIES['criteria'] += r"""
<h3>Cp 的風險目標、常數與選模</h3>
<p>先固定 $X$ 及候選線性模型，不用 $y$ 搜尋欄位。令 $H$ 為其投影矩陣，$r=\operatorname{rank}(H)$ 計入截距，並假設 $y=\mu+\varepsilon$、$\operatorname{Cov}(\varepsilon)=\sigma^2I$。以相同 $X$ 上一組獨立新反應 $y^{new}$ 定義固定設計預測風險，完整的 $C_p$ 型估計為</p>
$$\widehat R=\frac{\mathrm{RSS}+2r\hat\sigma^2}{n}.$$
<p>這是對訓練反應重抽的期望風險，不是某次實現的測試 MSE。若所有模型都含截距、$d$ 只數斜率，$r=d+1$；比較大小時可省掉共同的 $2\hat\sigma^2/n$，但省略後不能再宣稱數值本身是完整風險的無偏估計。</p>
<p>若每個大小的最佳模型也是用同一份 y 搜尋出來的，$H$ 已依賴 $y$，單純代入 $r$ 不會自動修正搜尋的樂觀偏差。</p>
<p>$2r\sigma^2$ 這個樂觀偏差的推導（含近似偏差項為何相消），見上方<a href="#w06-detail-criteria-origins">三個準則的懲罰項推導</a>第一部分。</p>
"""
BODIES['ridge'] += r"""
<h3>中心化後的 Ridge 解</h3>
<p>先用訓練資料把每個 $x_{ij}$ 與 $y_i$ 減去各自的平均，截距就可以分開處理。斜率最小化 $\sum_{i=1}^n\big(y_i-\sum_{j=1}^p\beta_jx_{ij}\big)^2+\lambda\sum_{j=1}^p\beta_j^2$，對每個 $\beta_j$ 偏微分設為 0，得到 $p$ 條線性方程（Ridge 的正規方程）：</p>
$$\sum_{k=1}^p\Big(\sum_{i=1}^nx_{ij}x_{ik}\Big)\beta_k+\lambda\beta_j=\sum_{i=1}^nx_{ij}y_i,\qquad j=1,\ldots,p.$$
<p>$\lambda\gt0$ 時，不論原始變數是否共線、甚至 $p\gt n$，這組方程都有唯一解。截距用 $\hat\beta_0=\bar y-\sum_j\hat\beta_j\bar x_j$ 還原；截距不能跟斜率一起用同一個 $\lambda$ 懲罰。Ridge 在各主成分方向上怎麼收縮，見 PCR 節的<a href="#w06-detail-ridge-pcr">Ridge 與 PCR 的對照</a>。</p>
""" + proof('w06proofRidge', 'Ridge 正規方程的解唯一', r"""
<p>目標對 $\beta_j$ 的偏導數是 $-2\sum_ix_{ij}\big(y_i-\sum_kx_{ik}\beta_k\big)+2\lambda\beta_j$，設為零整理即得上面的方程。</p>
<p>唯一性：任取不全為零的 $v_1,\ldots,v_p$，沿著方向 $(v_1,\ldots,v_p)$ 的二階導數為</p>
$$2\Big[\sum_{i=1}^n\Big(\sum_{j=1}^px_{ij}v_j\Big)^2+\lambda\sum_{j=1}^pv_j^2\Big]\gt0 .$$
<p>第一項可能為 0（例如變數共線時），但 $\lambda\sum_jv_j^2$ 一定為正，所以目標是嚴格凸函數，最小值只有一個。$\lambda=0$ 時少了這一項，共線就會讓解不唯一；最小平方在 $p\gt n$ 時的問題就出在這裡。</p>
""")
BODIES['lasso'] += r"""
<h3>Lasso 的零係數條件與座標更新</h3>
<p>一般的 $X$ 沒有閉式解。套件常用座標下降：固定其他係數，只對 $\beta_j$ 求解，結果是解釋二的軟門檻：令部分殘差 $r_i^{(-j)}=y_i-\sum_{k\ne j}\beta_kx_{ik}$，先對 $\sum_ix_{ij}r_i^{(-j)}$ 取門檻 $\lambda/2$ 的軟門檻，再除以 $\sum_ix_{ij}^2$，即 $\hat\beta_j=\operatorname{sign}(u_j)\,(|u_j|-\lambda/2)_+\big/\sum_ix_{ij}^2$，其中 $u_j=\sum_ix_{ij}r_i^{(-j)}$；逐一更新直到收斂。不同套件若用 $\mathrm{RSS}/(2n)$，相同 $\lambda$ 的數字不能直接比較。</p>
""" + proof('w06proofMAP', '高斯／Laplace 先驗如何變成 Ridge／Lasso', r"""
<p>獨立 $N(\beta_0+\sum_j\beta_jx_{ij},\sigma^2)$ 反應的負對數概似，除去與 $\beta$ 無關的常數後為 $\mathrm{RSS}/(2\sigma^2)$。各斜率獨立 $N(0,\tau^2)$ 的負對數先驗為 $\sum_j\beta_j^2/(2\tau^2)$；負對數後驗相加後乘以 $2\sigma^2$，成為 $\mathrm{RSS}+(\sigma^2/\tau^2)\sum_j\beta_j^2$。</p>
<p>Laplace 密度為 $e^{-|\beta_j|/b}/(2b)$，負對數先驗為 $\sum_j|\beta_j|/b$ 加常數，因此乘以 $2\sigma^2$ 後 $\lambda=2\sigma^2/b$。截距使用不懲罰的設定；$\sigma$、$\tau$、$b$ 在此視為固定。這是後驗眾數，後驗平均須積分計算，一般不會因 Laplace 先驗精確歸零。</p>
""")
BODIES['lasso'] += r"""
<h3>最小角度迴歸與 Group Lasso</h3>
<p>講義附錄只列出這兩個方法的連結，這裡各用一句話說明。LAR 從與殘差相關最大的特徵開始，沿活躍特徵的「等角」方向前進，其他特徵的相關追平時再加入；加上「係數走到零就移出」的規則，就能算出整條 Lasso 路徑（sklearn 的 <code>lars_path</code>、<code>LassoLars</code>）。</p>
<p>Group Lasso 以 $\lambda\sum_g\sqrt{p_g}\|\beta_g\|_2$ 懲罰事先指定的各組係數，讓同一類別變數的虛擬欄或同一組基底整組進出模型；選入的組內係數不必稀疏。</p>
<p>來源：<a href="https://scikit-learn.org/stable/modules/linear_model.html#least-angle-regression">LAR／Lasso 路徑官方說明</a>、<a href="https://group-lasso.readthedocs.io/en/latest/">Group Lasso 文件</a>。</p>
"""
BODIES['pcr'] += r"""
<h3>PCA 的最大變異與最小重建誤差</h3>
<p>設 $x_{ij}$ 已中心化，樣本共變異數記為 $S_{jk}=\frac1n\sum_{i=1}^nx_{ij}x_{ik}$。講義附錄定義共變異數矩陣時用 $\frac1{n-1}$，推導最大變異時用 $\frac1n$；兩者只差常數倍，方向不變，本節用 $\frac1n$。方向 $(\Phi_{11},\ldots,\Phi_{p1})$ 上的得分 $z_{i1}=\sum_j\Phi_{j1}x_{ij}$，其樣本變異數除以方向長度的平方為</p>
$$R(\Phi_{\cdot1})=\frac{\frac1n\sum_iz_{i1}^2}{\sum_j\Phi_{j1}^2}=\frac{\sum_{j=1}^p\sum_{k=1}^p\Phi_{j1}\Phi_{k1}S_{jk}}{\sum_{j=1}^p\Phi_{j1}^2}.$$
<p>這個比值稱為 <strong>Rayleigh quotient</strong>。它不受方向長度影響，所以「在 $\sum_j\Phi_{j1}^2=1$ 下最大化得分變異」等於最大化 $R(\Phi_{\cdot1})$。最大值是共變異數的最大特徵值，達到最大值的方向就是第一主成分方向；第二主成分在與第一方向正交的條件下再最大化，依此類推。</p>
<p><strong>與第 4 章 Fisher 判別的連結。</strong>第 4 章的 <a href="classification.html#w04fisher">Fisher 準則</a>同樣在找投影方向 $a$，最大化的是「投影後的類間散布 ÷ 類內散布」。兩者分子分母都是「方向的二次式」，Fisher 的比值稱為<strong>廣義</strong> Rayleigh quotient：分母換成類內散布，而不是方向的長度。PCA 不看類別，只問投影後整體散得多開；Fisher 問的是投影後類別分得多開。</p>
<p><strong>最大變異等於最小重建誤差。</strong>用單位方向的投影點 $z_{i1}\Phi_{j1}$ 重建第 $i$ 筆資料，殘差與方向垂直（見本節前面的<a href="#w06-detail-projection">投影座標</a>），所以每筆資料都滿足畢氏定理：</p>
$$\sum_{j=1}^px_{ij}^2=z_{i1}^2+\sum_{j=1}^p\big(x_{ij}-z_{i1}\Phi_{j1}\big)^2 .$$
<p>對 $i$ 加總，左邊是固定的總平方和，與方向無關；右邊第一項是 $n$ 倍的得分變異，第二項是重建誤差。兩者相加為定值，所以讓得分變異最大的方向，必定讓重建誤差最小。取 $M$ 個正交方向時同理，總平方和等於 $M$ 個得分的平方和加上重建誤差。</p>
""" + proof('w06proofPCA', 'Rayleigh quotient 的最大值是最大特徵值', r"""
<p>為了簡潔，暫時把 $\Phi_{j1}$ 寫成 $\Phi_j$。在 $\sum_j\Phi_j^2=1$ 下最大化 $\sum_j\sum_k\Phi_j\Phi_kS_{jk}$（講義附錄的作法）。引入 Lagrange 乘數 $\ell$，對 $\sum_j\sum_k\Phi_j\Phi_kS_{jk}-\ell\big(\sum_j\Phi_j^2-1\big)$ 對 $\Phi_j$ 偏微分設為 0：</p>
$$\sum_{k=1}^pS_{jk}\Phi_k=\ell\,\Phi_j,\qquad j=1,\ldots,p .$$
<p>所以極值方向必須是共變異數的特徵向量，$\ell$ 是對應的特徵值（這裡不用 $\lambda$，以免和懲罰參數混淆）。兩邊乘以 $\Phi_j$ 再對 $j$ 加總，得 $\sum_j\sum_k\Phi_j\Phi_kS_{jk}=\ell\sum_j\Phi_j^2=\ell$：在特徵向量上，得分變異恰好等於特徵值。因此最大值是最大特徵值 $\ell_1$，第一主成分就是對應的特徵向量。</p>
<p>要確認它是全域最大，把任一單位方向寫成正交特徵向量 $v_{\cdot1},\ldots,v_{\cdot p}$ 的組合 $\Phi_j=\sum_rc_rv_{jr}$，$\sum_rc_r^2=1$。代入後得分變異為 $\sum_r\ell_rc_r^2\le\ell_1\sum_rc_r^2=\ell_1$。</p>
""")
BODIES['pls'] += r"""
<h3>第一個 PLS 方向：最大化共變異</h3>
<p>設每個 $x_{ij}$ 已中心化並標準化（$\frac1n\sum_ix_{ij}^2=1$），$y_i$ 已中心化。記 $c_j=\operatorname{Cov}(X_j,Y)=\frac1n\sum_ix_{ij}y_i$。為了簡潔，下面先把第一個方向的權重 $\Phi_{j1}$ 寫成 $\Phi_j$。新特徵 $Z=\sum_j\Phi_jX_j$ 與 $Y$ 的共變異是 $\operatorname{Cov}(Y,Z)=\sum_j\Phi_jc_j$，所以第一個 PLS 方向解</p>
$$\max_{\sum_j\Phi_j^2=1}\Big(\sum_{j=1}^p\Phi_jc_j\Big)^2\quad\Longrightarrow\quad \Phi_{j1}=\frac{c_j}{\sqrt{\sum_kc_k^2}}\ \ (\text{正負號皆可}).$$
<p>另一方面，$Y$ 對單一 $X_j$ 做簡單迴歸的斜率是 $\operatorname{Cov}(X_j,Y)/\operatorname{Var}(X_j)$。標準化後 $\operatorname{Var}(X_j)=1$，斜率正好是 $c_j=\operatorname{Corr}(X_j,Y)\operatorname{SD}(Y)$。因此講義「用簡單迴歸係數當權重」與最佳化的解只差一個正規化常數，權重也與相關係數成正比。</p>
<p>注意目標是共變異而不是相關：$\operatorname{Cov}(Y,Z)=\operatorname{Corr}(Y,Z)\operatorname{SD}(Z)\operatorname{SD}(Y)$，PLS 同時考慮與 $Y$ 的關係及新特徵的變動量。若沒有先標準化，各斜率是 $\operatorname{Corr}(X_j,Y)\,\operatorname{SD}(Y)/\operatorname{SD}(X_j)$，不再與相關係數共用同一個倍數，所以講義的「權重與相關成比例」要連同標準化條件一起讀。</p>
""" + proof('w06proofPLSCov', 'Cauchy–Schwarz 給出第一 PLS 方向', r"""
<p>由 Cauchy–Schwarz 不等式，</p>
$$\Big(\sum_{j=1}^p\Phi_jc_j\Big)^2\le\Big(\sum_{j=1}^p\Phi_j^2\Big)\Big(\sum_{j=1}^pc_j^2\Big)=\sum_{j=1}^pc_j^2 .$$
<p>只要不是所有 $c_j$ 都為 0，等號成立若且唯若 $\Phi_j$ 與 $c_j$ 成比例，再由 $\sum_j\Phi_j^2=1$ 決定比例常數，就得到上面的 $\Phi_{j1}$。簡單迴歸斜率 $\hat b_j=\sum_ix_{ij}y_i/\sum_ix_{ij}^2$；代入相關係數 $r_j=\sum_ix_{ij}y_i/\sqrt{\sum_ix_{ij}^2\sum_iy_i^2}$，即得 $\hat b_j=r_j\,\mathrm{SD}(Y)/\mathrm{SD}(X_j)$。</p>
""")
BODIES['pls'] += r"""
<h3>後續方向：殘差化後重複（講義的算法）</h3>
<p>講義說後續方向是「取殘差後重複」。用純量寫出來（ESL 第 3.5.2 節的 PLS 演算法），每一輪都是「最大化共變異 → 從 $X$ 扣掉已找到的方向 → 重複」：</p>
<ol>
  <li><strong>第一個方向。</strong>$\Phi_{j1}=\sum_ix_{ij}y_i$（等於 $nc_j$；這裡不正規化成單位長度，方向乘上常數不影響最後的擬合值），得分 $z_{i1}=\sum_j\Phi_{j1}x_{ij}$。</li>
  <li><strong>殘差化（deflation）。</strong>把每個 $X_j$ 對 $Z_1$ 做簡單迴歸，留下 $Z_1$ 解釋不了的部分：
  $$x_{ij}^{(2)}=x_{ij}-a_{j1}z_{i1},\qquad a_{j1}=\frac{\sum_iz_{i1}x_{ij}}{\sum_iz_{i1}^2}.$$
  由迴歸殘差的性質，$\sum_iz_{i1}x_{ij}^{(2)}=0$：每個殘差都與 $Z_1$ 正交。</li>
  <li><strong>第二個方向。</strong>在殘差上用同樣的規則：$\Phi_{j2}=\sum_ix_{ij}^{(2)}y_i$，$z_{i2}=\sum_j\Phi_{j2}x_{ij}^{(2)}$。因為每個 $x_{ij}^{(2)}$ 都與 $Z_1$ 正交，$\sum_iz_{i1}z_{i2}=\sum_j\Phi_{j2}\sum_iz_{i1}x_{ij}^{(2)}=0$，所以 $Z_2$ 與 $Z_1$ 正交，不會重複第一個方向的資訊。</li>
  <li><strong>重複到 $M$ 個方向</strong>，最後做最小平方 $y_i=\theta_0+\sum_{m=1}^M\theta_mz_{im}+\varepsilon_i$。得分彼此正交，所以 $\hat\theta_m=\sum_iz_{im}y_i/\sum_iz_{im}^2$。</li>
</ol>
<p>把每一輪的方向換回原始變數的權重 $\alpha_j$（$Z_m=\sum_j\alpha_jX_j$，與上面作用在殘差上的 $\Phi_{jm}$ 不是同一組數字），第 $m$ 個方向等於在 $\sum_j\alpha_j^2=1$ 且「與前面的得分都正交」的條件下，最大化 $\operatorname{Cov}^2\big(Y,\sum_j\alpha_jX_j\big)$（ESL 第 3.5.2 節）。所以整個演算法就是把上面的共變異目標一輪一輪地解下去。</p>
<p>兩個細節。第一，殘差化後的 $x_{ij}^{(2)}$ 不再有單位變異數，此時 $Y$ 對它做簡單迴歸的斜率是 $\operatorname{Cov}/\operatorname{Var}$，不再等於共變異。要維持與最佳化的等價，權重應該用殘差與 $Y$ 的共變異（如上），或明確說明每一輪重新標準化並採用哪一種 PLS 版本。第二，有些演算法同時把 $y_i$ 換成殘差 $y_i-\hat y_i^{(m-1)}$。因為 $x_{ij}^{(m)}$ 與前面所有得分正交，而 $\hat y_i^{(m-1)}$ 是那些得分的線性組合，$\sum_ix_{ij}^{(m)}y_i=\sum_ix_{ij}^{(m)}\big(y_i-\hat y_i^{(m-1)}\big)$，兩種做法得到相同的方向。</p>
<p>預測新資料時，沿用訓練時估好的平均、尺度、各輪權重 $\Phi_{jm}$ 與殘差化係數 $a_{jm}$：新觀測依序算 $z_{\mathrm{new},m}=\sum_j\Phi_{jm}x_{\mathrm{new},j}^{(m)}$，再更新 $x_{\mathrm{new},j}^{(m+1)}=x_{\mathrm{new},j}^{(m)}-a_{jm}z_{\mathrm{new},m}$，不能用新資料重算方向。</p>
"""


BODIES['reference'] += r"""
<h3>在係數平面比較方法</h3>
<p>講義把兩個係數放在同一平面，以完整最小平方的 $(4,2)$ 作共同終點，讓不同複雜度的解形成路徑。最佳子集只能在坐標軸上的受限模型或完整模型之間選擇；Ridge 平滑地收縮，Lasso 可以沿軸停留到某係數進入；PCR 由保留幾個主成分決定可達子空間，PLS 的方向也使用 $y$。這張圖比較解的幾何，沒有表示所有方法都沿同一條直線縮回原點，也沒有提供測試風險的排名。</p>
"""


# DIRECT-LINKS-20260910

BODIES['pcr'] += r"""
<h3>正交、不相關與獨立是三件事</h3>
<p>向量正交表示內積為零；資料欄位的樣本不相關表示<strong>中心化之後</strong>的內積為零。PCA先中心化，得分共變異數是對角矩陣，所以不同得分欄位樣本不相關。這不等於它們統計獨立；獨立要求整個聯合分布可分解。</p>
<p>只有在聯合常態等額外條件下，不相關才足以推出獨立。對未中心化的原始$X$做SVD，主方向最大化的是相對原點的平方量，不必是相對平均的變異數。</p>
""" + proof('w06proofUncorrelated','PCA得分不相關',r"""
<p>中心化X滿足 $\mathbf1^TX=0$，故$Z=XV$也中心化。由 $S=V\Lambda V^T$，$Z^TZ/(n-1)=V^TSV=\Lambda$，所有非對角元素為零。</p>
""")


BODIES['criteria'] += r"""
<h3>分類離差的數值如何對回軟體？</h3>
<p>獨立二元觀測的飽和模型逐筆令 $p_i=y_i$，以 $0\log0=0$ 慣例，其對數概似為0。故Bernoulli離差為 $D=-2\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)]$。對單筆二元標籤，可用 <code>2 * log_loss(y, predict_proba(X), normalize=False)</code> 計算；輸入必須是機率，不能把log機率再次當機率，也不能漏掉總和與平均的$n$倍差別。</p>
<p>這是固定模型的擬合量；有懲罰的係數估計不等於無懲罰MLE，不能直接把任意兩個正則化模型的離差差值當成一般卡方概似比檢定。</p>
"""

# COVERAGE-20260910 END

PAGEJS = r"""
/* ===== model_selection 本頁元件（id 與全域一律 w06 前綴）===== */

const w06pal = ['#2c3e7a', '#c0392b', '#1a6b4a', '#8e44ad', '#f39c12', '#16a085',
                '#d35400', '#2980b9', '#7f8c8d', '#c2185b', '#00838f'];

/* ---------- P01 2^p 子集空間：規模比較 ---------- */
function w06subsetCounts() {
  const p = parseInt($('w06subsetP').value, 10);
  const best = Math.pow(2, p), step = 1 + p * (p + 1) / 2;
  $('w06subsetPv').textContent = String(p);
  $('w06subsetP2').textContent = String(p);
  $('w06subsetBest').textContent = best.toLocaleString('en-US');
  $('w06subsetFwd').textContent = step.toLocaleString('en-US');
  $('w06subsetRatio').textContent = HC.fmt(best / step, 1) + ' 倍';
  // 對數尺度的橫條：等距畫會讓 p 小的時候完全看不見
  const W = 620, H = 190;
  const s = HC.svg('w06subsetSvg', { xd: [0, 1], yd: [0, 1], h: H, w: W,
                                     pad: { l: 8, r: 8, t: 8, b: 8 } });
  s.clear();
  const g = s.layer('bars');
  const maxLog = Math.log10(Math.pow(2, 20));
  const rows = [['最佳子集 2ᵖ', best, 'var(--accent)'],
                ['forward 1+p(p+1)/2', step, 'var(--accent3)']];
  rows.forEach((row, i) => {
    const y = 54 + i * 62;
    const w = Math.max(4, (Math.log10(row[1]) / maxLog) * (W - 250));
    s.add('rect', { x: 170, y: y, width: w, height: 30, rx: 5, fill: row[2] }, g);
    const lab = s.add('text', { x: 162, y: y + 20, 'text-anchor': 'end', fill: 'var(--accent2)',
                                style: "font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600" }, g);
    lab.textContent = row[0];
    const num = s.add('text', { x: 178 + w, y: y + 20, fill: 'var(--ink)',
                                style: "font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700" }, g);
    num.textContent = row[1].toLocaleString('en-US') + ' 個模型';
  });
  const cap = s.add('text', { x: 12, y: 22, class: 'axtitle' }, g);
  cap.textContent = 'p = ' + p + ' 時要擬合的模型數（橫條長度是對數尺度）';
  const foot = s.add('text', { x: 12, y: H - 12, class: 'axlab' }, g);
  foot.textContent = 'p = 20 時最佳子集是 1,048,576 個，forward 只要 211 個——差 4,969 倍';
  setStatus('w06subsetStatus', 'p = ' + p + '：最佳子集 ' + best.toLocaleString('en-US')
    + ' 個模型，forward stepwise ' + step + ' 個，差 ' + HC.fmt(best / step, 1)
    + ' 倍。下面按「開始」看 forward 在四變數流程示意中如何逐步加入變數。');
}

/* ---------- P01 Credit 4 變數格圖：forward 逐步走 ---------- */
let w06latPlayer = null, w06latShowBest = true;
function w06latBits(m) { return [0, 1, 2, 3].filter(b => (m >> b) & 1); }
function w06latSize(m) { return w06latBits(m).length; }
function w06latBestByK() {
  const F = FRAMES_w06lat, out = [];
  for (let k = 0; k <= 4; k++) {
    let bm = -1;
    for (let m = 0; m < 16; m++) {
      if (w06latSize(m) !== k) continue;
      if (bm < 0 || F.rss[m] < F.rss[bm]) bm = m;
    }
    out.push(bm);
  }
  return out;
}
function w06latFrames() {
  const F = FRAMES_w06lat, best = w06latBestByK();
  const frames = [];
  let cur = 0;                                    // 空模型
  for (let k = 0; k < 4; k++) {
    const cands = [];
    for (let b = 0; b < 4; b++) if (!((cur >> b) & 1)) cands.push(cur | (1 << b));
    const pick = cands.reduce((a, m) => (F.rss[a] <= F.rss[m] ? a : m));
    frames.push({ k: k + 1, cur: cur, cands: cands, pick: pick, best: best[k + 1],
                  gap: F.rss[pick] - F.rss[best[k + 1]], line: k === 0 ? 1 : 3 });
    cur = pick;
  }
  frames.push({ k: 4, cur: cur, cands: [], pick: cur, best: best[4], gap: 0, line: 5, done: true });
  return frames;
}
function w06latApply(f) {
  const F = FRAMES_w06lat, best = w06latBestByK();
  const rssAll = F.rss.slice();
  const lo = Math.min.apply(null, rssAll), hi = Math.max.apply(null, rssAll);
  const svc = HC.svg('w06subsetLatSvg', { xd: [-0.4, 4.4], yd: [lo * 0.96, hi * 1.02],
                                          h: 300, w: 620 });
  svc.clear();
  svc.grid(4, 4, { xtitle: '模型裡的變數個數', ytitle: '訓練 RSS（' + F.unit + '）',
                   xdec: 0, ydec: 0 });
  const g = svc.layer('lat');
  // forward 走過的路
  const path = [];
  let c = 0;
  path.push([0, F.rss[0]]);
  for (let k = 0; k < 4; k++) {
    const cands = [];
    for (let b = 0; b < 4; b++) if (!((c >> b) & 1)) cands.push(c | (1 << b));
    c = cands.reduce((a, m) => (F.rss[a] <= F.rss[m] ? a : m));
    path.push([w06latSize(c), F.rss[c]]);
    if (w06latSize(c) >= f.k && !f.done) break;
  }
  if (w06latShowBest) {
    svc.poly(best.map((m, k) => [k, F.rss[m]]),
             { cls: 'fit', stroke: 'var(--accent)', sw: 2.6 }, g);
  }
  svc.poly(path, { cls: 'fit', stroke: 'var(--accent3)', sw: 3, dash: '6 4' }, g);
  for (let m = 0; m < 16; m++) {
    const k = w06latSize(m);
    const isCand = f.cands.indexOf(m) >= 0;
    const isPick = m === f.pick;
    const isBest = best[k] === m;
    svc.dot(k, F.rss[m], {
      r: isPick ? 7 : (isCand ? 5.5 : 3.6),
      fill: isPick ? 'var(--accent3)' : (isCand ? 'var(--pt-held)'
            : (isBest && w06latShowBest ? 'var(--accent)' : 'rgba(138,133,120,.5)')),
      stroke: isPick || isCand ? '#fff' : null, sw: isPick || isCand ? 1.6 : null,
    }, g);
  }
  const names = m => (m === 0 ? '∅' : w06latBits(m).map(b => FRAMES_w06lat.names[b]).join('+'));
  $('w06latTry').textContent = f.cands.length
    ? f.cands.map(m => FRAMES_w06lat.names[w06latBits(m).filter(
        b => !((f.cur >> b) & 1))[0]]).join('、') : '（走完了）';
  $('w06latPick').textContent = names(f.pick);
  hlLine('w06subsetCode', f.line);
  setStatus('w06latStatus', f.done ? '逐步加入變數的流程已完成；接著依驗證結果或選模準則決定模型大小。' : '在目前可加入的候選變數中，選擇使訓練 RSS 最小的一個，再進入下一步。');
}
function w06latStart() {
  w06latPlayer = new Player({ frames: w06latFrames(), apply: w06latApply });
  w06latPlayer.reset(); w06latPlayer.play();
}
function w06latReset() {
  if (w06latPlayer) w06latPlayer.stop();
  w06latPlayer = new Player({ frames: w06latFrames(), apply: w06latApply });
  w06latApply({ k: 0, cur: 0, cands: [], pick: 0, best: 0, gap: 0, line: null });
  setStatus('w06latStatus', '按「開始」看 forward stepwise 在四變數示意中如何選擇。');
}
function w06latToggleBest() { w06latShowBest = !w06latShowBest; if (w06latPlayer) w06latApply(w06latPlayer.frames[Math.max(0, w06latPlayer.i)]); }

/* ---------- P04 Ridge ---------- */
let w06ridgeByRatio = false;
function w06ridgeAxis() { w06ridgeByRatio = !w06ridgeByRatio; w06ridgeDraw(); }
function w06ridgeDraw() {
  const F = FRAMES_w06ridge;
  const xs = w06ridgeByRatio ? F.l2ratio : F.lambdas.map(l => Math.log10(l));
  HC.line('w06ridgeChart', {
    labels: xs.map(v => HC.fmt(v, w06ridgeByRatio ? 2 : 1)),
    datasets: F.names.map((nm, j) => ({ label: nm, data: F.coefs[j],
      borderColor: w06pal[j % w06pal.length], borderWidth: 2, pointRadius: 0, fill: false })),
  }, {
    interaction: { mode: 'nearest', intersect: false },
    plugins: { legend: { position: 'right', labels: { boxWidth: 8, font: { size: 10 } } } },
    scales: { x: { title: { display: true, text: w06ridgeByRatio ? '‖β̂ᴿ‖₂ ⁄ ‖β̂‖₂' : 'log₁₀ λ' } },
              y: { title: { display: true, text: '標準化後的係數' } } },
  });
  const c = HC.get('w06ridgeChart');
  HC.refs(c, [HC.hline(0, '', 'var(--muted)')]);
  w06ridgeMove();
}
function w06ridgeMove() {
  const F = FRAMES_w06ridge, i = parseInt($('w06ridgeSl').value, 10);
  const nz = F.coefs.filter(row => Math.abs(row[i]) > 1e-8).length;
  $('w06ridgeLam').textContent = HC.fmt(F.lambdas[i], F.lambdas[i] < 10 ? 3 : 1);
  $('w06ridgeRatio').textContent = HC.fmt(F.l2ratio[i], 4);
  $('w06ridgeNz').textContent = nz + ' / ' + F.names.length;
  setStatus('w06ridgeStatus', 'λ = ' + HC.fmt(F.lambdas[i], 2) + ' 時相對收縮量 '
    + HC.fmt(F.l2ratio[i], 4) + '，非零係數 ' + nz + ' / ' + F.names.length
    + '——就算收縮到只剩原本長度的 ' + HC.pct(F.l2ratio[i], 1)
    + '，也沒有任何一個變成剛好 0。');
}

/* ---------- P05 L1 vs L2 幾何 ---------- */
const w06geomBhat = [2.6, 1.4];
const w06geomA = [[1.0, 0.62], [0.62, 0.75]];
let w06geomL1 = true;
function w06geomRss(b) {
  const d0 = b[0] - w06geomBhat[0], d1 = b[1] - w06geomBhat[1];
  return w06geomA[0][0] * d0 * d0 + 2 * w06geomA[0][1] * d0 * d1 + w06geomA[1][1] * d1 * d1;
}
function w06geomQuad(b, bh, A) {
  const d0 = b[0] - bh[0], d1 = b[1] - bh[1];
  return A[0][0] * d0 * d0 + 2 * A[0][1] * d0 * d1 + A[1][1] * d1 * d1;
}
function w06geomSolveL1(s, bh = w06geomBhat, A = w06geomA) {
  /* 在菱形四條邊上做一維二次最小化；端點由 clamp 精確納入。 */
  let best = null, bestV = Infinity;
  [-1, 1].forEach(a => [-1, 1].forEach(b => {
    const c = [0, b * s], v = [a, -b];
    const d = [c[0] - bh[0], c[1] - bh[1]];
    const Av = [A[0][0] * v[0] + A[0][1] * v[1],
                A[1][0] * v[0] + A[1][1] * v[1]];
    const Ad = [A[0][0] * d[0] + A[0][1] * d[1],
                A[1][0] * d[0] + A[1][1] * d[1]];
    const den = v[0] * Av[0] + v[1] * Av[1];
    const t = Math.max(0, Math.min(s, -(v[0] * Ad[0] + v[1] * Ad[1]) / den));
    const cand = [c[0] + t * v[0], c[1] + t * v[1]];
    const value = w06geomQuad(cand, bh, A);
    if (value < bestV) { bestV = value; best = cand; }
  }));
  return best;
}
function w06geomSolveL2(s) {
  /* KKT: (A + lambda I)b = A b_OLS；解單調方程 ||b||_2 = s。 */
  const A = w06geomA, bh = w06geomBhat;
  const c0 = A[0][0] * bh[0] + A[0][1] * bh[1];
  const c1 = A[1][0] * bh[0] + A[1][1] * bh[1];
  const at = lam => {
    const a = A[0][0] + lam, d = A[1][1] + lam;
    const det = a * d - A[0][1] * A[1][0];
    return [(d * c0 - A[0][1] * c1) / det,
            (-A[1][0] * c0 + a * c1) / det];
  };
  let lo = 0, hi = 1;
  while (Math.hypot(...at(hi)) > s) hi *= 2;
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2;
    if (Math.hypot(...at(mid)) > s) lo = mid; else hi = mid;
  }
  return at(hi);
}
function w06geomSolve(s) {
  const norm = w06geomL1 ? Math.abs(w06geomBhat[0]) + Math.abs(w06geomBhat[1])
                         : Math.hypot(w06geomBhat[0], w06geomBhat[1]);
  if (norm <= s) return w06geomBhat.slice();
  return w06geomL1 ? w06geomSolveL1(s) : w06geomSolveL2(s);
}
function w06geomToggle() {
  w06geomL1 = !w06geomL1;
  $('w06geomBtn').textContent = w06geomL1 ? '切換為 L2（Ridge）' : '切換為 L1（Lasso）';
  w06geomDraw();
}
function w06geomMove() { w06geomDraw(); }
function w06geomDraw() {
  const s = parseInt($('w06geomSl').value, 10) / 100;
  const sol = w06geomSolve(s), solV = w06geomRss(sol);
  const svc = HC.svg('w06geomSvg', { xd: [-1.4, 3.8], yd: [-1.4, 3.0], h: 380, w: 620 });
  svc.clear();
  svc.grid(6, 5, { xtitle: 'β₁', ytitle: 'β₂', xdec: 1, ydec: 1 });
  const g = svc.layer('geom');
  if (w06geomL1) {
    svc.add('polygon', { points: [[s, 0], [0, s], [-s, 0], [0, -s]]
                           .map(q => svc.X(q[0]) + ',' + svc.Y(q[1])).join(' '),
                         fill: 'rgba(44,62,122,.16)', stroke: 'var(--accent2)',
                         'stroke-width': 2 }, g);
  } else {
    svc.add('ellipse', { cx: svc.X(0), cy: svc.Y(0),
                         rx: Math.abs(svc.X(s) - svc.X(0)), ry: Math.abs(svc.Y(s) - svc.Y(0)),
                         fill: 'rgba(44,62,122,.16)', stroke: 'var(--accent2)',
                         'stroke-width': 2 }, g);
  }
  [0.25, 0.8, 1.8, 3.2, 5.0, solV].sort((a, b) => a - b).forEach(L => {
    const pts = [];
    for (let t = 0; t <= 96; t++) {
      const th = t / 96 * 2 * Math.PI;
      const u0 = Math.cos(th), u1 = Math.sin(th);
      const q = w06geomA[0][0] * u0 * u0 + 2 * w06geomA[0][1] * u0 * u1 + w06geomA[1][1] * u1 * u1;
      const r = Math.sqrt(L / q);
      pts.push([w06geomBhat[0] + r * u0, w06geomBhat[1] + r * u1]);
    }
    const isSol = Math.abs(L - solV) < 1e-9;
    svc.add('polygon', { points: pts.map(q => svc.X(q[0]) + ',' + svc.Y(q[1])).join(' '),
                         fill: 'none', stroke: isSol ? 'var(--accent)' : 'rgba(192,57,43,.32)',
                         'stroke-width': isSol ? 2.8 : 1.2 }, g);
  });
  svc.dot(w06geomBhat[0], w06geomBhat[1], { r: 5, fill: 'var(--accent)', stroke: '#fff', sw: 1.5 }, g);
  svc.txt(w06geomBhat[0], w06geomBhat[1], 'β̂ (OLS)', { dy: -13, fill: 'var(--accent)' }, g);
  svc.dot(sol[0], sol[1], { r: 6.5, fill: 'var(--accent3)', stroke: '#fff', sw: 2 }, g);
  const zeros = w06geomL1 ? sol.filter(v => v === 0).length : 0;
  svc.txt(sol[0], sol[1], zeros ? '解（有係數 = 0）' : '解', { dy: 21, fill: 'var(--accent3)' }, g);
  $('w06geomS').textContent = HC.fmt(s, 2);
  $('w06geomB1').textContent = HC.fmt(sol[0], 3);
  $('w06geomB2').textContent = HC.fmt(sol[1], 3);
  $('w06geomNz').textContent = String(zeros);
  $('w06geomRss').textContent = HC.fmt(solV, 3);
  setStatus('w06geomStatus', (w06geomL1 ? 'L1（Lasso）' : 'L2（Ridge）') + '，預算 s = '
    + HC.fmt(s, 2) + ' → 解 (' + HC.fmt(sol[0], 3) + ', ' + HC.fmt(sol[1], 3) + ')。'
    + (zeros ? '<strong>有 ' + zeros + ' 個係數剛好是 0。</strong>'
             : '兩個係數都不是 0'
               + (w06geomL1 ? '——把 s 再調小一點試試。' : '（L2 幾乎不會歸零）。')));
}

/* 新增四張圖共用：裁在繪圖區內、圖例文字（.axlab/.fit 的 CSS 會蓋掉顏色屬性，改用 style） */
function w06clip(svc, id, g) {
  const clip = svc.add('clipPath', { id: id }, svc.add('defs'));
  svc.add('rect', { x: svc.pad.l, y: svc.pad.t, width: svc.iw, height: svc.ih }, clip);
  g.setAttribute('clip-path', 'url(#' + id + ')');
  return g;
}
function w06leg(svc, py, str, color, parent) {
  const n = svc.add('text', { cls: 'vlab', x: svc.W - 20, y: py, 'text-anchor': 'end', style: 'fill:' + color }, parent);
  n.textContent = str;
  return n;
}
/* ---------- P05 尖角的法線扇形（圓形等高線、預算 s = 1） ---------- */
let w06fanL1 = true;
function w06fanToggle() {
  w06fanL1 = !w06fanL1;
  $('w06fanBtn').textContent = w06fanL1 ? '切換為 L2（Ridge）' : '切換為 L1（Lasso）';
  w06fanDraw();
}
function w06fanDraw() {
  const b2 = parseInt($('w06fanSl').value, 10) / 100, bh = [2, b2];
  const I = [[1, 0], [0, 1]];
  let sol;
  if (w06fanL1) {
    sol = Math.abs(bh[0]) + Math.abs(bh[1]) <= 1 ? bh.slice() : w06geomSolveL1(1, bh, I);
  } else {
    const r = Math.hypot(bh[0], bh[1]);
    sol = r <= 1 ? bh.slice() : [bh[0] / r, bh[1] / r];
  }
  const inFan = Math.abs(b2) <= bh[0] - 1 + 1e-12;
  const svc = HC.svg('w06fanSvg', { xd: [-1.4, 3.985], yd: [-1.5, 1.5], h: 360, w: 620 });
  svc.clear();
  svc.grid(6, 6, { xtitle: 'β₁', ytitle: 'β₂', xdec: 1, ydec: 1 });
  const g = w06clip(svc, 'w06fanClip', svc.layer('geom'));
  const pts = q => q.map(v => svc.X(v[0]) + ',' + svc.Y(v[1])).join(' ');
  if (w06fanL1) {
    svc.add('polygon', { points: pts([[1, 1e-9], [2.5, 1.5], [3.985, 1.5], [3.985, -1.5], [2.5, -1.5]]),
                         fill: 'rgba(243,156,18,.18)', stroke: 'none' }, g);
    svc.seg(1, 0, 2.5, 1.5, { cls: 'w06fanEdge', stroke: '#e67e22', sw: 1.8, dash: '6 4' }, g);
    svc.seg(1, 0, 2.5, -1.5, { cls: 'w06fanEdge', stroke: '#e67e22', sw: 1.8, dash: '6 4' }, g);
    svc.add('text', { cls: 'vlab', x: svc.X(3.3), y: svc.Y(1.22), 'text-anchor': 'middle', style: 'fill:#b9770e' }, g).textContent = '法線扇形';
    svc.add('polygon', { points: pts([[1, 0], [0, 1], [-1, 0], [0, -1]]),
                         fill: 'rgba(44,62,122,.16)', stroke: 'var(--accent2)', 'stroke-width': 2 }, g);
    svc.txt(1, 0, 'P', { dx: -10, dy: -8, fill: 'var(--accent2)' }, g);
  } else {
    svc.add('ellipse', { cx: svc.X(0), cy: svc.Y(0), rx: svc.X(1) - svc.X(0), ry: svc.Y(0) - svc.Y(1),
                         fill: 'rgba(44,62,122,.16)', stroke: 'var(--accent2)', 'stroke-width': 2 }, g);
    svc.seg(0, 0, bh[0], bh[1], { stroke: 'var(--muted)', sw: 1.2, dash: '4 4' }, g);
  }
  const rSol = Math.hypot(sol[0] - bh[0], sol[1] - bh[1]);
  [0.35, 0.7, rSol, rSol + 0.45].forEach(r => {
    if (r <= 1e-9) return;
    const isSol = Math.abs(r - rSol) < 1e-12;
    svc.add('ellipse', { cx: svc.X(bh[0]), cy: svc.Y(bh[1]), rx: svc.X(r) - svc.X(0), ry: svc.Y(0) - svc.Y(r),
                         fill: 'none', stroke: isSol ? 'var(--accent)' : 'rgba(192,57,43,.32)',
                         'stroke-width': isSol ? 2.4 : 1.1 }, g);
  });
  svc.dot(bh[0], bh[1], { r: 5, fill: 'var(--accent)', stroke: '#fff', sw: 1.5 }, g);
  svc.txt(bh[0], bh[1], 'β̂ (OLS)', { dy: -12, fill: 'var(--accent)' }, g);
  svc.dot(sol[0], sol[1], { r: 6.5, fill: 'var(--accent3)', stroke: '#fff', sw: 2 }, g);
  $('w06fanOls').textContent = '(2, ' + HC.fmt(b2, 2) + ')';
  $('w06fanSol').textContent = '(' + HC.fmt(sol[0], 3) + ', ' + HC.fmt(sol[1], 3) + ')';
  $('w06fanIn').textContent = w06fanL1 ? (inFan ? '是' : '否') : '（Ridge 沒有扇形）';
  if (w06fanL1) {
    setStatus('w06fanStatus', inFan
      ? 'OLS 解 (2, ' + HC.fmt(b2, 2) + ')：第二座標的絕對值 ≤ 2 − 1 = 1，落在扇形內 → Lasso 解停在尖角 P = (1, 0)，<strong>β₂ 剛好是 0</strong>。'
      : 'OLS 解 (2, ' + HC.fmt(b2, 2) + ')：第二座標的絕對值 > 1，離開扇形 → 解滑到菱形的邊上，兩個係數都不是 0。');
  } else {
    setStatus('w06fanStatus', 'Ridge 把 OLS 點沿半徑拉回圓上，解為 (' + HC.fmt(sol[0], 3) + ', '
      + HC.fmt(sol[1], 3) + ')。' + (b2 === 0 ? 'OLS 的第二座標為 0 時，解才落在座標軸上。' : '只要 OLS 的第二座標不是 0，β₂ 就不是 0。'));
  }
}

/* ---------- P05 常態與 Laplace 先驗（變異數皆為 1） ---------- */
let w06priorLog = false;
function w06priorToggle() {
  w06priorLog = !w06priorLog;
  $('w06priorBtn').textContent = w06priorLog ? '切換為密度' : '切換為負對數密度';
  w06priorDraw();
}
function w06priorDraw() {
  const b = 1 / Math.SQRT2;
  const norm = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);
  const lap = x => Math.exp(-Math.abs(x) / b) / (2 * b);
  const f = w06priorLog ? [x => x * x / 2, x => Math.abs(x) / b] : [norm, lap];
  const svc = HC.svg('w06priorSvg', { xd: [-4, 4], yd: w06priorLog ? [0, 6] : [0, 0.75], h: 300, w: 620 });
  svc.clear();
  svc.grid(8, 5, { xtitle: 'β', ytitle: w06priorLog ? '−log 密度（減去 0 點的值）' : '先驗密度',
                   xdec: 0, ydec: w06priorLog ? 0 : 2 });
  const g = w06clip(svc, 'w06priorClip', svc.layer('curves'));
  const xs = HC.stat.seq(-4, 4, 401);
  [[f[0], 'var(--accent2)', '常態（→ Ridge）'], [f[1], 'var(--accent)', 'Laplace（→ Lasso）']].forEach((c, k) => {
    svc.poly(xs.map(x => [x, c[0](x)]), { cls: 'w06curve', stroke: c[1], sw: 2.4 }, g);
    w06leg(svc, 32 + 18 * k, '── ' + c[2], c[1]);
  });
  setStatus('w06priorStatus', w06priorLog
    ? '負對數密度：常態是平滑的拋物線 β²/2，Laplace 是在 0 有尖角的 √2·|β|，正是 Ridge 與 Lasso 的懲罰形狀。'
    : '同樣的變異數下，Laplace 在 0 的密度 0.707 高於常態的 0.399，尾部也比較厚：多數係數接近 0，少數仍可很大。');
}

/* ---------- P06 等距與對數網格 ---------- */
let w06gridLog = false;
function w06gridToggle() {
  w06gridLog = !w06gridLog;
  $('w06gridBtn').textContent = w06gridLog ? '橫軸切換為 λ' : '橫軸切換為 log₁₀ λ';
  w06gridDraw();
}
function w06gridDraw() {
  const r = l => 1 / (1 + l);
  const lin = HC.stat.seq(0.001, 100, 10);
  const logs = HC.stat.seq(-3, 2, 10).map(t => Math.pow(10, t));
  const tx = l => w06gridLog ? Math.log10(l) : l;
  const svc = HC.svg('w06gridSvg', { xd: w06gridLog ? [-3, 2] : [0, 100], yd: [0, 1.2], h: 300, w: 620 });
  svc.clear();
  const sup = { '-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³' };
  svc.grid(5, 6, { xtitle: w06gridLog ? 'λ（對數刻度）' : 'λ', ytitle: '係數保留比例 r(λ)', ydec: 1,
                   xfmt: v => w06gridLog ? '10' + String(Math.round(v)).split('').map(ch => sup[ch]).join('') : HC.fmt(v, 0) });
  const g = svc.layer('curve');
  const ts = HC.stat.seq(-3, 2, 300).map(t => Math.pow(10, t));
  svc.poly(ts.map(l => [tx(l), r(l)]), { cls: 'w06curve', stroke: 'var(--muted)', sw: 2 }, g);
  lin.forEach(l => svc.dot(tx(l), r(l), { r: 5.5, fill: 'var(--accent)', stroke: '#fff', sw: 1.2 }, g));
  logs.forEach(l => svc.dot(tx(l), r(l), { r: 4, fill: 'var(--accent2)', stroke: '#fff', sw: 1.2 }, g));
  w06leg(svc, 32, '● 等距網格', 'var(--accent)', g);
  w06leg(svc, 50, '● 對數網格', 'var(--accent2)', g);
  setStatus('w06gridStatus', w06gridLog
    ? '橫軸為 log₁₀ λ：曲線是一條 S 形，對數網格的藍點均勻散在整條曲線上；紅點幾乎全擠在右側平坦處。'
    : '橫軸為 λ：曲線在 λ < 10 就幾乎降到底，等距網格的紅點只有一個落在 λ < 1，其餘都在模型幾乎不變的區域。');
}

/* ---------- P07 Ridge 與 PCR 的收縮因子 ---------- */
function w06shrinkDraw() {
  const lam = Math.pow(10, parseInt($('w06shrinkLam').value, 10) / 10);
  const M = parseInt($('w06shrinkMSl').value, 10);
  const d2 = HC.stat.seq(1, 10, 10).map(m => 100 * Math.pow(0.6, m - 1));
  const ridge = d2.map(d => d / (d + lam));
  const df = ridge.reduce((a, v) => a + v, 0);
  const svc = HC.svg('w06shrinkSvg', { xd: [0, 11], yd: [0, 1.2], h: 300, w: 620 });
  svc.clear();
  svc.grid(11, 6, { xtitle: '主成分編號 m（變異由大到小）', ytitle: '收縮因子', ydec: 1,
                    xfmt: v => (v >= 1 && v <= 10) ? HC.fmt(v, 0) : '' });
  const g = svc.layer('bars');
  const step = [];
  for (let m = 1; m <= 10; m++) {
    const h = m <= M ? 1 : 0;
    step.push([m - 0.5, h], [m + 0.5, h]);
  }
  svc.poly(step, { cls: 'w06curve', stroke: 'var(--accent)', sw: 2.4 }, g);
  svc.poly(ridge.map((v, k) => [k + 1, v]), { cls: 'w06curve', stroke: 'var(--accent2)', sw: 1.6, dash: '4 3' }, g);
  ridge.forEach((v, k) => svc.dot(k + 1, v, { r: 5, fill: 'var(--accent2)', stroke: '#fff', sw: 1.2 }, g));
  w06leg(svc, 32, '● Ridge：d²ₘ/(d²ₘ+λ)', 'var(--accent2)', g);
  w06leg(svc, 50, '── PCR：前 M 個為 1', 'var(--accent)', g);
  $('w06shrinkDf').textContent = HC.fmt(df, 2);
  $('w06shrinkM').textContent = String(M);
  setStatus('w06shrinkStatus', 'λ = ' + HC.fmt(lam, lam < 1 ? 2 : 1) + '：Ridge 的有效自由度 ' + HC.fmt(df, 2)
    + '，第 1 個方向保留 ' + HC.pct(ridge[0], 0) + '、第 10 個只保留 ' + HC.pct(ridge[9], 0)
    + '。PCR 用 M = ' + M + ' 時自由度就是 ' + M + '，其餘方向直接歸零。');
}

/* ---------- P05 Lasso 路徑 ---------- */
function w06lassoDraw() {
  const F = FRAMES_w06lasso;
  HC.line('w06lassoChart', {
    labels: F.lambdas.map(l => HC.fmt(Math.log10(l), 1)),
    datasets: F.names.map((nm, j) => ({ label: nm, data: F.coefs[j],
      borderColor: w06pal[j % w06pal.length], borderWidth: 2, pointRadius: 0, fill: false })),
  }, {
    interaction: { mode: 'nearest', intersect: false },
    plugins: { legend: { position: 'right', labels: { boxWidth: 8, font: { size: 10 } } } },
    scales: { x: { title: { display: true, text: 'log₁₀ λ' } },
              y: { title: { display: true, text: '標準化後的係數' } } },
  });
  const c = HC.get('w06lassoChart');
  HC.refs(c, [HC.hline(0, '', 'var(--muted)')]);
  w06lassoMove();
}
function w06lassoMove() {
  const F = FRAMES_w06lasso, i = parseInt($('w06lassoSl').value, 10);
  const alive = F.names.filter((nm, j) => Math.abs(F.coefs[j][i]) > 1e-8);
  $('w06lassoLam').textContent = HC.fmt(F.lambdas[i], F.lambdas[i] < 10 ? 3 : 1);
  $('w06lassoNz').textContent = F.nz[i] + ' / ' + F.names.length;
  $('w06lassoVars').textContent = alive.length ? alive.join('、') : '（全部歸零）';
  setStatus('w06lassoStatus', 'λ = ' + HC.fmt(F.lambdas[i], 2) + ' 時還有 ' + F.nz[i]
    + ' 個非零係數。' + (F.nz[i] < F.names.length
      ? '<strong>被歸零的係數精確等於 0。</strong>'
      : '在這個 λ 下，全部變數的係數都非零。'));
}
function w06lassoCvJump() {
  const F = FRAMES_w06lasso;
  let bi = 0, bd = Infinity;
  F.lambdas.forEach((l, i) => { const d = Math.abs(l - F.cvLambda); if (d < bd) { bd = d; bi = i; } });
  $('w06lassoSl').value = String(bi);
  w06lassoMove();
  setStatus('w06lassoStatus', 'CV 選出的 λ = ' + F.cvLambda + '，在這個 λ 之下 '
    + F.cvNz + ' / ' + F.names.length + ' 個變數全部仍保留——'
    + 'Credit 的係數並不稀疏，在這個設定下保留了全部變數。是否產生零係數取決於資料與 λ。');
}

/* ---------- P07 PCA 方向 vs PLS 方向 ---------- */
const w06dirData = (() => {
  const rand = HC.stat.lcg(606), a1 = [], a2 = [];
  for (let i = 0; i < 90; i++) {
    const u = HC.stat.normal(rand) * 1.9, v = HC.stat.normal(rand) * 0.55;
    a1.push(u + 0.15 * v); a2.push(0.55 * u + v);
  }
  return { x1: a1, x2: a2 };
})();
const w06dirPcaTh = (() => {
  const x1 = w06dirData.x1, x2 = w06dirData.x2;
  const m1 = HC.stat.mean(x1), m2 = HC.stat.mean(x2);
  let s11 = 0, s22 = 0, s12 = 0;
  for (let i = 0; i < x1.length; i++) {
    s11 += (x1[i] - m1) * (x1[i] - m1);
    s22 += (x2[i] - m2) * (x2[i] - m2);
    s12 += (x1[i] - m1) * (x2[i] - m2);
  }
  return 0.5 * Math.atan2(2 * s12, s11 - s22);
})();
function w06dirMove() { w06dirDraw(); }
function w06dirReset() { $('w06dirSl').value = '20'; w06dirDraw(); }
function w06dirDraw() {
  const degTrue = parseInt($('w06dirSl').value, 10);
  const thTrue = degTrue * Math.PI / 180;
  const x1 = w06dirData.x1, x2 = w06dirData.x2;
  const rand = HC.stat.lcg(1234);
  const yv = x1.map((v, i) => Math.cos(thTrue) * v + Math.sin(thTrue) * x2[i]
                              + 0.35 * HC.stat.normal(rand));
  const my = HC.stat.mean(yv), m1 = HC.stat.mean(x1), m2 = HC.stat.mean(x2);
  let c1 = 0, c2 = 0;
  for (let i = 0; i < x1.length; i++) {
    c1 += (x1[i] - m1) * (yv[i] - my); c2 += (x2[i] - m2) * (yv[i] - my);
  }
  const thPls = Math.atan2(c2, c1);
  const svc = HC.svg('w06dirSvg', { xd: [-6, 6], yd: [-4, 4], h: 340, w: 620 });
  svc.clear();
  svc.grid(6, 4, { xtitle: 'x₁', ytitle: 'x₂', xdec: 0, ydec: 0 });
  const g = svc.layer('dir');
  x1.forEach((v, i) => svc.dot(v, x2[i], { r: 3, fill: 'rgba(138,133,120,.55)' }, g));
  const ray = (th, color, dash) => {
    const L = 5.4;
    svc.seg(-L * Math.cos(th), -L * Math.sin(th), L * Math.cos(th), L * Math.sin(th),
            { cls: 'fit', stroke: color, sw: 3, dash: dash }, g);
  };
  ray(thTrue, 'var(--fit-true)', '7 5');
  ray(w06dirPcaTh, 'var(--accent2)', null);
  ray(thPls, 'var(--accent)', null);
  svc.txtPx(56, 18, '── PC1（只看 X）', { fill: 'var(--accent2)' }, g);
  svc.txtPx(196, 18, '── PLS1（也看 y）', { fill: 'var(--accent)' }, g);
  svc.txtPx(346, 18, '- - y 的真實方向', { fill: 'var(--fit-true)' }, g);
  const deg = t => HC.fmt(((t * 180 / Math.PI) % 180 + 180) % 180, 1) + '°';
  $('w06dirTrue').textContent = deg(thTrue);
  $('w06dirPca').textContent = deg(w06dirPcaTh);
  $('w06dirPls').textContent = deg(thPls);
  const dd = Math.abs((((w06dirPcaTh - thTrue) * 180 / Math.PI) % 180 + 180) % 180);
  $('w06dirAng').textContent = HC.fmt(Math.min(dd, 180 - dd), 1) + '°';
  setStatus('w06dirStatus', 'y 的真實方向 ' + deg(thTrue) + '：PC1 仍在 ' + deg(w06dirPcaTh)
    + '（沒動），PLS1 轉到 ' + deg(thPls) + '——PLS1 追著 y 跑，PC1 只看 X 的散佈。');
}

/* ---------- P09 高維度 ---------- */
let w06hdR2 = true;
function w06hdToggle() { w06hdR2 = !w06hdR2;  }
function w06hdDraw() {
  const F = FRAMES_w06hd;
  HC.line('w06hdChart', {
    labels: F.ps,
    datasets: [
      { label: w06hdR2 ? '訓練 R²' : '訓練 MSE', data: w06hdR2 ? F.trainR2 : F.trainMse,
        borderColor: HC.tok.accent3, borderWidth: 2.6, pointRadius: 3, fill: false, yAxisID: 'y' },
      { label: '測試 MSE', data: F.testMse, borderColor: HC.tok.accent,
        borderWidth: 2.8, pointRadius: 3, fill: false, yAxisID: 'y1' },
    ],
  }, {
    scales: {
      x: { title: { display: true, text: '放進模型的變數個數 p（n = ' + F.n + '）' } },
      y: { position: 'left', title: { display: true, text: w06hdR2 ? '訓練 R²' : '訓練 MSE' } },
      y1: { position: 'right', title: { display: true, text: '測試 MSE' },
            grid: { drawOnChartArea: false } },
    },
  });
  const c = HC.get('w06hdChart');
  HC.refs(c, [HC.vline(F.n - 2, 'p + 1 = n')]);
  setStatus('w06hdStatus', 'X 與 y 完全獨立。各 p 重複 400 次，訓練 R² 取平均、測試 MSE 取中位數。p 從 1 加到 '
    + F.ps[F.ps.length - 1] + ' 時訓練 R² 從 ' + F.trainR2[0] + ' 升到 '
    + F.trainR2[F.trainR2.length - 1] + '，而測試 MSE 從 ' + F.testMse[0] + ' 升到 '
    + F.testMse[F.testMse.length - 1] + '。');
}

/* ---------- 啟動 ----------
   SVG 元件一律放在 HC.ready() 外面：Chart.js 從 CDN 載不到時 HC.ready() 不會執行，
   把 SVG 初始化放進去會讓手寫元件跟著死掉。 */
w06subsetCounts();
w06latReset();
w06geomDraw();
w06fanDraw();
w06priorDraw();
w06gridDraw();
w06shrinkDraw();
w06dirDraw();
HC.ready(() => {
  w06ridgeDraw();
  w06lassoDraw();
  
});
"""


# Approved reading-flow organization; keep all source-backed detail content.
from reading_flow_ch1_6 import organize
BODIES, PAGEJS = organize(6, BODIES, PAGEJS)
from lecture_alignment_ch6 import augment
BODIES = augment(BODIES)

if __name__ == "__main__":
    apply("model_selection", BODIES, PAGEJS, frames())
