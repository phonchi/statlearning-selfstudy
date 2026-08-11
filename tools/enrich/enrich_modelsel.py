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
from lib import (apply, card, chart, info, info_card, lab_code, lab_output, qa,  # noqa: E402
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
  <p>第 3 章的最小平方法很好用：沒有調整參數、有封閉解、係數可以直接解讀。
  這一章不是要換掉它，而是要問一句話：<strong>當變數很多的時候，「把全部變數丟進去做最小平方」
  還是最好的做法嗎？</strong>答案通常是不。</p>

  <p>問題出在兩個地方。第一是<strong>預測準確度</strong>：當 p 逼近 n，最小平方的估計會非常不穩定
  （變異很大）；當 p &gt; n，它連唯一解都沒有——你可以找到無限多組係數把訓練誤差壓到 0，
  而它們在新資料上都爛得一樣。第二是<strong>可解讀性</strong>：一堆跟 y 沒關係的變數留在模型裡，
  最小平方幾乎不可能把它們的係數估成剛好 0，於是你得到一個沒人看得懂的模型。</p>

{info("這一章的三大類方法", '''<strong>1. 子集選擇（subset selection）：</strong>挑出一部分變數，
  只用它們做最小平方。最佳子集、前向逐步、後向逐步。<br>
  <strong>2. 收縮（shrinkage）／正則化：</strong>全部 p 個變數都留著，但把係數往 0 壓。
  Ridge 用 L2 懲罰、Lasso 用 L1 懲罰（順便做變數選擇）。<br>
  <strong>3. 降維（dimension reduction）：</strong>把 p 個變數投影成 M &lt; p 個線性組合，
  再對這 M 個新變數做最小平方。PCR 與 PLS。''')}

  <p>三類方法都在做同一件事：<strong>用一點偏差換一大塊變異</strong>。最小平方是無偏的，
  但在 p 大的時候變異大到讓它毫無用處；只要願意接受一點偏差，測試誤差往往降得很明顯。
  整章的節奏都是這個交換。</p>

  $$\\text{{RSS}} = \\sum_{{i=1}}^{{n}}\\left(y_i - \\beta_0 - \\sum_{{j=1}}^{{p}}\\beta_j x_{{ij}}\\right)^2$$

  <p>下面這張表先放在這裡，讀完整章再回來看一次會比較有感覺。</p>

{table(["", "留幾個變數", "係數會剛好是 0 嗎", "有調整參數嗎", "座標系", "主要弱點"],
       [["最小平方", "全部 p 個", "幾乎不會", "沒有", "原始變數", "p 大時變異爆炸"],
        ["子集選擇", "k 個（自己選）", "沒被選的就是 0", "k", "原始變數", "搜尋空間太大、不穩定"],
        ["Ridge（L2）", "全部 p 個", "<strong>不會</strong>", "λ", "原始變數", "不做變數選擇"],
        ["Lasso（L1）", "由 λ 決定", "<strong>會</strong>", "λ", "原始變數", "相關變數之間的選擇很不穩"],
        ["PCR / PLS", "全部 p 個都參與", "不會", "M", "<strong>換過的座標</strong>",
         "新座標不好解讀"]])}

{quiz("qWhy", "QUIZ · 為什麼要動手術",
      "為什麼 p 逼近 n 的時候，「把全部變數丟進去做最小平方」是個壞主意？",
      [(True, "因為係數估計的變異會變得非常大，訓練資料稍微變動一點，配出來的模型就差很多",
        "對。最小平方在 p ≪ n 時是低偏差、低變異；p 逼近 n 時偏差仍然是 0，但變異大到讓測試誤差很難看。收縮就是拿一點偏差去換掉這塊變異。"),
       (False, "因為最小平方法假設誤差是常態分佈，變數多了這個假設就不成立",
        "不對。常態假設是用來做 t 檢定與信賴區間的，跟 p／n 的比例無關；而且就算誤差真的是常態，p 逼近 n 時最小平方照樣會變異爆炸。"),
       (False, "因為變數多了以後 RSS 會變大，配適品質下降",
        "反了。加變數<strong>永遠</strong>不會讓訓練 RSS 變大（多一個變數最差就是係數估成 0）。訓練 RSS 單調下降正是問題所在——它不能用來選模型。")])}
"""

# ── P01 subset ────────────────────────────────────────────────────────
_sub_code = lab_code(CH, 12) + "\n" + lab_code(CH, 13) + "\n" + lab_code(CH, 15)

BODIES["subset"] = f"""
  <p>最直白的想法：<strong>每一種變數組合都試一次，挑最好的</strong>。這就是最佳子集選擇
  （best subset selection）。p 個變數有 2<sup>p</sup> 種組合（含空模型），
  演算法分兩階段——先在每個大小 k 裡挑出訓練 RSS 最小的 M<sub>k</sub>，
  再從 M<sub>0</sub>, …, M<sub>p</sub> 裡挑一個。</p>

  $$\\text{{總共要配}} \\; \\sum_{{k=0}}^{{p}} \\binom{{p}}{{k}} = 2^{{p}} \\;
    \\text{{個模型}}$$

{info("為什麼一定要分兩階段", '''第一階段用訓練 RSS 挑同大小的贏家沒問題（同樣的 k，
  比 RSS 是公平的）。<strong>第二階段絕對不能再用訓練 RSS</strong>——因為 RSS 隨 k 單調下降、
  R² 隨 k 單調上升，你一定會選到全部變數。第二階段要用 Cp、AIC、BIC、調整後 R²，或直接用交叉驗證。''',
      "warm")}

  <p>2<sup>p</sup> 長得太快，p 超過 40 就算不完了。<strong>前向逐步選擇</strong>
  （forward stepwise selection）改成貪婪地走：從空模型開始，每一步加一個「讓 RSS 降最多」的變數。
  <strong>後向逐步選擇</strong>（backward stepwise selection）反過來，從全模型開始每次砍一個。
  兩者都只要配</p>

  $$1 + \\sum_{{k=0}}^{{p-1}} (p-k) = 1 + \\frac{{p(p+1)}}{{2}} \\; \\text{{個模型}}$$

  <p>p = 20 時這是 <strong>211</strong> 個，而最佳子集是 <strong>1,048,576</strong> 個。
  代價是：<strong>貪婪走法不保證找到最佳子集</strong>。下面第二張圖用真實的 <code>Credit</code>
  資料把這件事畫出來。</p>

{viz(svg("w06subsetSvg", 190) + "\n" + svg("w06subsetLatSvg", 300),
     [rows_card("要配幾個模型",
                [("p（變數個數）", "10", "w06subsetP2"),
                 ("最佳子集 2ᵖ", "—", "w06subsetBest"),
                 ("forward 1+p(p+1)/2", "—", "w06subsetFwd"),
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
      rows_card("Credit 的 4 變數格圖",
                [("這一步在試", "—", "w06latTry"), ("選到的", "—", "w06latPick"),
                 ("同大小的最佳子集", "—", "w06latBestSub"),
                 ("RSS 差（百萬）", "—", "w06latGap")]),
      info_card("下圖怎麼看",
                '每一個點是一個子集（<code>Balance ~ Limit + Rating + Cards + Student</code> '
                '的 16 種組合），x 是變數個數、y 是訓練 RSS。'
                '<span style="color:var(--accent);font-weight:700;">紅線</span>是每個大小的最佳子集'
                '（ISLP 圖 6.1 的紅色前緣），'
                '<span style="color:var(--accent3);font-weight:700;">綠線</span>是 forward 走出來的路。',
                "圖 6.1")],
     "w06subsetStatus", "上面的滑桿看 2ᵖ 有多可怕；下面按「開始」看 forward 在真實資料上怎麼走。",
     slider("w06subsetP", "p =", 2, 20, 1, 10, "w06subsetCounts()", "w06subsetPv", "10")
     + '<button class="btn btn-play" onclick="w06latStart()">▶ 開始</button>'
     + '<button class="btn btn-step" onclick="w06latPlayer &amp;&amp; w06latPlayer.step()">→ 單步</button>'
     + '<button class="btn btn-toggle" onclick="w06latToggleBest()">切換最佳前緣</button>'
     + '<button class="btn btn-reset" onclick="w06latReset()">重置</button>')}

{info("這張格圖的重點", '''在 <code>Credit</code> 上，forward 第一步選 <code>Rating</code>、
  第二步加 <code>Student</code>——到這裡都跟最佳子集一樣。但<strong>三變數</strong>的最佳子集是
  <code>Limit + Cards + Student</code>（RSS 15.23 百萬），forward 卻只能給
  <code>Rating + Cards + Student</code>（15.51 百萬）。原因是 forward 一旦選了
  <code>Rating</code> 就<strong>不能再把它丟掉</strong>，而 <code>Limit</code> 與
  <code>Rating</code> 幾乎共線，最佳子集會拿 <code>Limit</code> 換掉 <code>Rating</code>。
  ISLP 表 6.1 在完整的 11 個變數上是同一個現象（第四個模型開始分歧）。''')}

  <h3 id="dx-sub">講義完整實作：Hitters、前向與後向逐步選擇</h3>
{card("講義 06 · 載入 Hitters 並丟掉缺失值", _sub_code, lab_output(CH, 15),
      src=src("12、13、15"),
      note="59 名球員的 <code>Salary</code> 是缺失的，<code>dropna()</code> 之後剩 "
           "<strong>263 列、20 欄</strong>（19 個預測變數＋Salary）。"
           "整章的 Hitters 結果都建立在這 263 筆上。")}

{card("講義 06 · 自訂迴圈的前向逐步選擇", lab_code(CH, 33) + "\n\n" + lab_code(CH, 34),
      lab_output(CH, 34), src=src("33、34"),
      note="讀這段輸出的正確方式是<strong>看每一行是不是前一行的超集合</strong>："
           "<code>CRBI</code> → 加 <code>Hits</code> → 加 <code>PutOuts</code>…"
           "一路只加不減。這正是前向逐步的定義，也正是它可能錯過最佳子集的原因。")}

{card("講義 06 · 後向逐步選擇（BIC 挑出來的大小不一樣）",
      lab_code(CH, 40) + "\n\n" + lab_code(CH, 41), lab_output(CH, 41), src=src("40、41"),
      note="<code>bic_b</code> 是照 <code>models2</code> 的索引順序（1、2、…、19）收集的，"
           "0-based 的 <code>argmin() = 7</code> 指的是<strong>第 8 個</strong>元素，也就是 8 變數模型；"
           "而前向那邊（下一節）是 6 變數。<strong>同一份資料、同一個準則，兩個搜尋方向給出不同大小的模型</strong>"
           "——講義第 42 頁講的就是這件事。")}

{table(["搜尋法", "要配幾個模型", "p = 20 時", "n &lt; p 能用嗎", "保證找到最佳子集嗎"],
       [["最佳子集", "2<sup>p</sup>", "1,048,576", "不能（最多到 n−1 個變數）", "<strong>會</strong>"],
        ["前向逐步", "1 + p(p+1)/2", "211", "<strong>可以</strong>", "不保證"],
        ["後向逐步", "1 + p(p+1)/2", "211", "不能（要先配全模型）", "不保證"],
        ["混合逐步", "略多於逐步", "約 211+", "看實作", "不保證（但比較接近）"]])}

{quiz("qSub", "QUIZ · 子集選擇",
      "同一份資料上做最佳子集、前向逐步、後向逐步。<strong>大小同樣是 k</strong> 的三個模型裡，"
      "哪一個的訓練 RSS 最小？",
      [(True, "最佳子集的一定最小（或並列最小），因為它窮舉了所有 k 變數子集",
        "對。這就是 ISLP 6.6 第 1 題 (a) 的答案。注意這只說訓練 RSS——測試 RSS 誰最小完全說不準，因為窮舉的搜尋空間更大，反而更容易配到雜訊。"),
       (False, "三個一定相同，因為它們都是在同一份資料上做最小平方",
        "不對。都是最小平方沒錯，但<strong>用的變數不同</strong>。逐步法受前幾步的選擇綁住，可能拿不到那個 k 變數的最佳組合——本節的 Credit 格圖就是實例。"),
       (False, "後向逐步的最小，因為它從全模型開始，資訊最完整",
        "不對。從全模型開始只影響搜尋路徑，不代表每個大小都能找到最佳組合。後向逐步同樣是貪婪的，而且它還多一個限制：要能配出全模型，所以需要 n &gt; p。")])}
"""

# ── P02 criteria ──────────────────────────────────────────────────────
BODIES["criteria"] = f"""
  <p>第二階段的問題是：<strong>怎麼比較「大小不同」的模型？</strong>訓練 RSS 與 R² 不能用，
  因為它們單調偏好大模型。兩條路——<strong>間接</strong>（把訓練誤差加一個懲罰項，修掉它的樂觀偏差）
  與<strong>直接</strong>（用驗證集或交叉驗證真的去估測試誤差，下一節講）。</p>

  <p>間接法的四個常客。設模型有 d 個預測變數、σ̂² 是用<strong>全模型</strong>估出來的誤差變異數：</p>

  $$C_p = \\frac{{1}}{{n}}\\left(\\mathrm{{RSS}} + 2 d \\hat\\sigma^2\\right), \\qquad
    \\mathrm{{BIC}} = \\frac{{1}}{{n}}\\left(\\mathrm{{RSS}} + \\log(n)\\, d \\hat\\sigma^2\\right)$$

  $$\\text{{Adjusted }} R^2 = 1 - \\frac{{\\mathrm{{RSS}}/(n-d-1)}}{{\\mathrm{{TSS}}/(n-1)}}$$

  <p>兩個公式長得幾乎一樣，只差在<strong>每多一個變數要罰多少</strong>：Cp 罰 2σ̂²，
  BIC 罰 log(n)·σ̂²。因為 n &gt; 7 就有 log n &gt; 2，<strong>BIC 罰得比 Cp 重，所以偏好更小的模型</strong>。
  n 愈大這個差距愈誇張——<code>Credit</code> 的 n = 400，log 400 ≈ 5.99，BIC 的懲罰是 Cp 的三倍。</p>

{info("AIC 與 Cp 的關係", '''對高斯誤差的最小平方模型，課本的 AIC 就是
  RSS + 2dσ̂²，跟 Cp 成正比（所以 ISLP 圖 6.2 只畫 Cp）。
  但實作（<code>statsmodels</code> 的 <code>.aic</code>）用的是 log-likelihood 版
  −2·log L + 2k，它跟 Cp <strong>不是</strong>單調對應——所以下圖把它畫成獨立一條線。
  兩個版本都叫 AIC，看到數字差很多不要慌，先問是哪一個公式。''')}

{viz(chart("w06critChart", "tall",
           "。此圖的重點：Credit 上 Cp 選 6 個變數、BIC 選 4 個、調整後 R² 選 7 個——同一份資料，"
           "四個準則挑出三種答案，而 BIC 因為懲罰項是 log n 而不是 2，明顯偏好小模型。"),
     [rows_card("各準則挑出的大小",
                [("Cp", "—", "w06critCp"), ("AIC（log-likelihood 版）", "—", "w06critAic"),
                 ("BIC", "—", "w06critBic"), ("調整後 R²", "—", "w06critAdj"),
                 ("10-fold CV 誤差", "—", "w06critCv")], "Credit n=400"),
      info_card("怎麼看這張圖",
                '每一條線是一個準則在「最佳 d 變數模型」上的值，'
                '<strong>大圓點是它自己的最佳位置</strong>。'
                '預設把五條線各自正規化到 0–1（0 = 該準則最好），這樣單位完全不同的五個量才能放在一起比。'
                '按「切換原始單位」可以看 Cp、BIC、CV 誤差的真實數值（都是 MSE 單位）。', "圖 6.2／6.3"),
      info_card("最重要的一件事",
                '四條曲線從 d = 4 之後幾乎是平的。<strong>不要為了「哪個數字最小」去爭論</strong>——'
                'Cp 在 d=6 是 9846.8、在 d=4 是 9982.8，差 1.4%，遠在雜訊範圍內。'
                '看的是曲線在哪裡拉平。')],
     "w06critStatus", "Credit 全部 2¹¹ 個子集窮舉後，五個準則畫在同一張圖上。",
     '<button class="btn btn-toggle" onclick="w06critToggle()">切換原始單位</button>')}

{table(["準則", "式子（最小平方）", "每多一個變數罰多少", "n=400 時的懲罰", "Credit 選出"],
       [["Cp", "(RSS + 2dσ̂²)/n", "2σ̂²", "2σ̂²", "<strong>6 個</strong>"],
        ["AIC（課本）", "RSS + 2dσ̂²", "2σ̂²", "與 Cp 成正比", "同 Cp"],
        ["BIC", "(RSS + log(n)·dσ̂²)/n", "log(n)·σ̂²", "<strong>5.99σ̂²</strong>",
         "<strong>4 個</strong>"],
        ["調整後 R²", "1 − [RSS/(n−d−1)] / [TSS/(n−1)]", "分母的 n−d−1 變小", "很輕",
         "<strong>7 個</strong>"],
        ["交叉驗證", "直接估測試誤差", "不需要 σ̂²", "—", "<strong>6 個</strong>"]])}

{qa("觀念釐清", [
    ("Q：Cp、AIC、BIC 到底差在哪？為什麼 BIC 偏好小模型？",
     "<p>三個都是「訓練 RSS ＋ 一個隨模型變大而變大的懲罰」。差別只在懲罰的係數："
     "Cp 與課本版 AIC 都是 $2d\\hat\\sigma^2$，BIC 是 $\\log(n)\\, d\\hat\\sigma^2$。"
     "$\\log n > 2$ 對任何 $n > 7$ 都成立（$e^2 \\approx 7.39$），所以 BIC 一律罰得比較重，"
     "選出來的模型一律比較小或一樣大。n = 400 時 $\\log n \\approx 5.99$，懲罰差三倍。</p>"
     "<p>背後的動機不同。Cp 是<strong>估測試 MSE</strong>："
     "可以證明只要 $\\hat\\sigma^2$ 是 $\\sigma^2$ 的無偏估計，Cp 就是測試 MSE 的無偏估計。"
     "BIC 是從<strong>貝氏</strong>觀點來的，它在近似「這個模型是真模型的後驗機率」。"
     "所以兩者的目標本來就不一樣：Cp／AIC 想預測得準，BIC 想找出<em>正確的</em>模型。"
     "如果真模型確實在候選清單裡，n 夠大時 BIC 會挑中它（一致性）；AIC 不保證，它會傾向多留幾個變數。</p>"
     "<p>實務上的建議：<strong>目的是預測就用 CV（或 AIC／Cp），目的是「哪些變數真的有關」就參考 BIC</strong>。"
     "而且兩者都要求你估得出 $\\hat\\sigma^2$——這在 p &gt; n 的時候直接破功（最後一節會講）。</p>"),
    ("Q：調整後 R² 為什麼「理論基礎比較弱」？",
     "<p>Cp、AIC、BIC 都有明確的推導：Cp 是測試 MSE 的無偏估計，AIC 來自 Kullback–Leibler 距離的漸近論證，"
     "BIC 來自後驗機率的 Laplace 近似。調整後 R² 沒有這種東西——它就是「把 RSS 除以 $n-d-1$ 而不是 n」"
     "這個直覺上合理的修正。</p>"
     "<p>它的直覺是對的：真正有用的變數都進來以後，再加雜訊變數只會讓 RSS 降一點點，"
     "但 $d$ 變大會讓分母 $n-d-1$ 變小，兩者相抵之下 $\\mathrm{RSS}/(n-d-1)$ 會變大、"
     "調整後 R² 會下降。問題是「一點點」有多點沒有理論刻度，所以它的懲罰強度是任意的——"
     "在 Credit 上它比 Cp 還鬆（選 7 個 vs 6 個）。</p>"
     "<p>順便記一件事：<strong>調整後 R² 在 p &gt; n 時可以輕易做到 1</strong>，"
     "所以高維度下它完全不能用。</p>"),
])}

  <h3 id="dx-crit">講義完整實作：用 BIC 與調整後 R² 挑大小</h3>
{card("講義 06 · 前向路徑上的 BIC", lab_code(CH, 36) + "\n\n" + lab_code(CH, 37),
      lab_output(CH, 37), src=src("36、37"),
      note="<code>argmin()</code> 回傳 <strong>5</strong>，而 <code>bic_f</code> 是 0-based 的 "
           "list，所以指的是清單的第 6 個元素——<strong>6 變數模型</strong>，BIC = 3812.21。"
           "注意下一格的 <code>models1.model[5]</code> 用的是 pandas 的<em>標籤</em>索引，"
           "取到的是 5 變數模型（輸出列出 5 個特徵）。同一個 <code>5</code>，兩種索引意義完全不同，"
           "讀別人的程式碼時要分清楚。")}

{card("講義 06 · 最佳子集 + 調整後 R²",
      lab_code(CH, 97) + "\n\n" + lab_code(CH, 98) + "\n\n" + lab_code(CH, 101),
      lab_output(CH, 101), src=src("97、98、101"),
      note="這是 <code>adjust_r2()</code> 的定義（就是式 6.4）加上在最佳子集前緣上取最大值。"
           "Hitters 上調整後 R² 選出 <strong>11 個變數</strong>；BIC 選 6 個。"
           "兩個準則差了 5 個變數——這不是誰算錯，是兩個準則的懲罰強度本來就不同。")}

{quiz("qCrit", "QUIZ · 選模型的準則",
      "同一份資料上，BIC 選出的模型大小，跟 Cp 選出的比起來？",
      [(True, "一定小於或等於（n &gt; 7 時），因為 BIC 每多一個變數要罰 log(n)·σ̂² 而 Cp 只罰 2σ̂²",
        "對。log n > 2 對任何 n > 7 成立，所以 BIC 的懲罰項嚴格較重，最小值只會往左移或不動。Credit 上是 4 vs 6。"),
       (False, "不一定，取決於資料裡有多少真的有用的變數",
        "有用變數的多寡會影響<em>兩者各自</em>選幾個，但不會改變「BIC 罰得更重」這個事實。兩條曲線的 RSS 部分完全一樣，只有懲罰斜率不同，所以 BIC 的最小值不可能落在 Cp 的右邊。"),
       (False, "一定一樣，因為兩者都是測試 MSE 的無偏估計",
        "只有 Cp 是測試 MSE 的無偏估計，BIC 不是——BIC 是從後驗機率近似來的，它刻意罰得更重以便挑出「正確的」模型而不是「預測最準的」模型。")])}
"""

# @@REST@@
