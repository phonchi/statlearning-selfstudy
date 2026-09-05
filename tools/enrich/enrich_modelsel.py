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
  當變數很多時，<strong>估計的穩定性與模型的可解讀性</strong>就需要更多考量。
  本章介紹子集選擇、收縮與降維，處理這兩個問題。</p>

  <p>問題出在兩個地方。第一是<strong>預測準確度</strong>：當 p 逼近 n，最小平方的估計會非常不穩定
  （變異很大）；當 p &gt; n，它連唯一解都沒有。若設計矩陣的列滿秩，可以找到無限多組係數把訓練誤差壓到 0，
  但它們在新資料上的預測不一定相同，訓練誤差無法幫你選出泛化較好的解。第二是<strong>可解讀性</strong>：一堆跟 y 沒關係的變數留在模型裡，
  最小平方幾乎不可能把它們的係數估成剛好 0，於是你得到一個難以逐項解讀的模型。</p>

{info("這一章的三大類方法", '''<strong>1. 子集選擇（subset selection）：</strong>挑出一部分變數，
  只用它們做最小平方。最佳子集、前向逐步、後向逐步。<br>
  <strong>2. 收縮（shrinkage）／正則化：</strong>全部 p 個變數都留著，但把係數往 0 壓。
  Ridge 用 L2 懲罰、Lasso 用 L1 懲罰（順便做變數選擇）。<br>
  <strong>3. 降維（dimension reduction）：</strong>把 p 個變數投影成 M &lt; p 個線性組合，
  再對這 M 個新變數做最小平方。PCR 與 PLS。''')}

  <p>三類方法都透過<strong>接受一些偏差來降低變異</strong>。最小平方是無偏的，
  但在 p 大的時候，高變異會降低預測表現；只要願意接受一點偏差，測試誤差往往降得很明顯。
  整章的節奏都是這個交換。</p>

  $$\\text{{RSS}} = \\sum_{{i=1}}^{{n}}\\left(y_i - \\beta_0 - \\sum_{{j=1}}^{{p}}\\beta_j x_{{ij}}\\right)^2$$

  <p>下面這張表先放在這裡，讀完整章再回來看一次會比較有感覺。</p>

{table(["", "留幾個變數", "係數會剛好是 0 嗎", "有調整參數嗎", "座標系", "主要弱點"],
       [["最小平方", "全部 p 個", "幾乎不會", "沒有", "原始變數", "p 大時變異很大"],
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
        "不對。常態假設是用來做 t 檢定與信賴區間的，跟 p／n 的比例無關；而且就算誤差真的是常態，p 逼近 n 時最小平方照樣會變異很大。"),
       (False, "因為變數多了以後 RSS 會變大，配適品質下降",
        "反了。加變數<strong>永遠</strong>不會讓訓練 RSS 變大（多一個變數最差就是係數估成 0）。訓練 RSS 單調下降正是問題所在。它不能用來選模型。")])}
"""

# ── P01 subset ────────────────────────────────────────────────────────
_sub_code = lab_code(CH, 12) + "\n" + lab_code(CH, 13) + "\n" + lab_code(CH, 15)

BODIES["subset"] = f"""
  <p>最直白的想法：<strong>每一種變數組合都試一次，挑最好的</strong>。這就是最佳子集選擇
  （best subset selection）。p 個變數有 2<sup>p</sup> 種組合（含空模型），
  演算法分兩階段。先在每個大小 k 裡挑出訓練 RSS 最小的 M<sub>k</sub>，
  再從 M<sub>0</sub>, …, M<sub>p</sub> 裡挑一個。</p>

  $$\\text{{總共要配}} \\; \\sum_{{k=0}}^{{p}} \\binom{{p}}{{k}} = 2^{{p}} \\;
    \\text{{個模型}}$$

{info("為什麼一定要分兩階段", '''第一階段用訓練 RSS 挑同大小的贏家沒問題（同樣的 k，
  比 RSS 是公平的）。<strong>第二階段絕對不能再用訓練 RSS</strong>，因為 RSS 隨 k 單調下降、
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
     + '<button class="btn btn-reset" onclick="w06latReset()">重置</button>',
     provenance=("course-data", "ISLP Credit；完整列舉 4 變數的 16 個子集"))}

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
       [["最佳子集", "2<sup>p</sup>", "1,048,576", "可以（只比較可估計的小子集）", "<strong>會</strong>"],
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
  −2·log L + 2k，它跟 Cp <strong>不是</strong>單調對應，所以下圖把它畫成獨立一條線。
  兩個版本都叫 AIC，看到數字差很多不要慌，先問是哪一個公式。''')}

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
     "而且兩者都要求你估得出 $\\hat\\sigma^2$——這在 p &gt; n 的時候無法按全模型的常規公式計算（最後一節會講）。</p>"),
    ("Q：調整後 R² 為什麼「理論基礎比較弱」？",
     "<p>Cp、AIC、BIC 都有明確的推導：Cp 是測試 MSE 的無偏估計，AIC 來自 Kullback–Leibler 距離的漸近論證，"
     "BIC 來自後驗機率的 Laplace 近似。調整後 R² 沒有這種東西。它就是「把 RSS 除以 $n-d-1$ 而不是 n」"
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
           "兩個準則差了 5 個變數，反映了它們對模型複雜度採用不同的懲罰強度。")}

{quiz("qCrit", "QUIZ · 選模型的準則",
      "同一份資料上，BIC 選出的模型大小，跟 Cp 選出的比起來？",
      [(True, "一定小於或等於（n &gt; 7 時），因為 BIC 每多一個變數要罰 log(n)·σ̂² 而 Cp 只罰 2σ̂²",
        "對。log n > 2 對任何 n > 7 成立，所以 BIC 的懲罰項嚴格較重，最小值只會往左移或不動。Credit 上是 4 vs 6。"),
       (False, "不一定，取決於資料裡有多少真的有用的變數",
        "有用變數的多寡會影響<em>兩者各自</em>選幾個，但不會改變「BIC 罰得更重」這個事實。兩條曲線的 RSS 部分完全一樣，只有懲罰斜率不同，所以 BIC 的最小值不可能落在 Cp 的右邊。"),
       (False, "一定一樣，因為兩者都是測試 MSE 的無偏估計",
        "只有 Cp 是測試 MSE 的無偏估計，BIC 不是——BIC 是從後驗機率近似來的，它刻意罰得更重以便挑出「正確的」模型而不是「預測最準的」模型。")])}
"""

# ── P03 用 CV 選模型 + one-SE ──────────────────────────────────────────
BODIES["onese"] = f"""
  <p>Cp、AIC、BIC 都需要估 $\\hat\\sigma^2$，而在 p 接近 n 的時候那個估計本身就不可靠。
  交叉驗證不需要 $\\hat\\sigma^2$、不需要知道自由度、也不需要假設模型是對的。
  它<strong>直接估測試誤差</strong>。所以只要算得動，CV 是首選。</p>

  <p>做法就是第 5 章那一套，只是把「模型」換成「模型大小」：對每個大小 k，
  在每一折的訓練部分做子集選擇、在驗證折上算誤差。
  <strong>注意選變數這件事必須關在折裡面</strong>。這正是第 5 章 P06 講的那個錯誤。</p>

{info("one-standard-error 規則", '''CV 誤差本身有抽樣變異。Credit 上的 CV 曲線在大小 4 到 8 之間幾乎是平的，
  差異遠小於誤差棒。這時候硬選最低點沒有道理，因為那個「最低」很可能只是運氣。<br><br>
  <strong>規則：先找到 CV 誤差最小的模型，算出它的標準誤；然後在「CV 誤差落在
  最小值 ＋ 一個標準誤」以內的所有模型裡，選最簡單的那個。</strong><br><br>
  Credit 資料上 CV 選 6 個變數，one-SE 規則選 <strong>4 個</strong>——
  少兩個變數，預測能力在統計上分不出差別。上一節那張圖的橘色線就是 10-fold CV 誤差，
  大圓點是它的最低點。''')}

{card("講義 06 · 用 GridSearchCV 選調整參數", lab_code(CH, 134), lab_output(CH, 134),
      src=src("134"),
      note="<code>Pipeline</code> 是關鍵：把標準化包進去，"
           "<code>GridSearchCV</code> 就會在每一折的訓練部分重新 fit scaler，"
           "而不是用全部資料的平均與標準差。這一步做錯，CV 誤差會偏低而且不會報錯。")}

{qa("觀念釐清", [
    ("Q：既然 CV 最好，為什麼還要教 Cp、AIC、BIC？",
     "<p>三個理由。第一，算力：最佳子集有 $2^p$ 個模型，每個都跑 k-fold 是 $k \\cdot 2^p$ 次配適；"
     "而 Cp 只要一次配適加一個修正項。第二，這三個準則會出現在<strong>別人的論文與報表</strong>裡，"
     "你得看得懂。第三，它們解釋了「懲罰複雜度」這個想法的來源——"
     "AIC 從 KL 散度來、BIC 從後驗機率來，各有各的目標。</p>"
     "<p>但如果你只是要挑一個模型來預測，而且資料量算得動：用 CV。</p>"),
    ("Q：one-SE 規則會不會選出「太簡單」的模型？",
     "<p>會，而且那是刻意的。它的立場是：<strong>在預測能力分不出差別時，偏好簡單</strong>。</p>"
     "<p>這個偏好有實際理由——變數少的模型更好解釋、需要蒐集的資料更少、"
     "上線後更不容易因為某個變數的定義改變而壞掉。如果你的目標純粹是最小化預測誤差"
     "而完全不在意這些，那就選最低點；但要記得那個「最低」在下一份資料上很可能換人。</p>"),
])}

{quiz("qOse", "QUIZ · one-SE 規則",
      "CV 誤差在模型大小 4、5、6、7 上分別是 54100、53900、53800、53850，"
      "而最小值的標準誤是 6000。one-SE 規則會選哪一個？",
      [(True, "4 個變數，因為 54100 落在 53800 ＋ 6000 = 59800 以內，而它是這些之中最簡單的",
        "對。門檻是「最小值 ＋ 一個 SE」，所有低於門檻的模型都算「一樣好」，然後取最簡單的。這裡四個全部低於門檻，所以選 4。"),
       (False, "6 個變數，因為 53800 是最小的",
        "那是直接選最低點，不是 one-SE 規則。one-SE 的整個用意就是承認 53800 與 54100 的差距（300）遠小於雜訊（SE = 6000），硬選最低點是在追雜訊。"),
       (False, "5 個變數，因為它在 4 和 6 之間取折衷",
        "one-SE 規則沒有「取折衷」這個步驟。它是明確的兩步：算門檻、取門檻內最簡單的。")])}
"""

# ── P04 Ridge ─────────────────────────────────────────────────────────
BODIES["ridge"] = f"""
  <p>子集選擇是離散的：一個變數要嘛在、要嘛不在。這讓它<strong>變異很大</strong>——
  資料動一點，選出來的變數就換一批。另一條路是留下全部變數，但<strong>把係數往零壓</strong>。</p>

  <p>Ridge 在原本的 RSS 上加一個 L2 懲罰：</p>

  $$\\sum_{{i=1}}^{{n}}\\left(y_i - \\beta_0 - \\sum_{{j=1}}^{{p}}\\beta_j x_{{ij}}\\right)^2
    + \\lambda \\sum_{{j=1}}^{{p}} \\beta_j^2
    \\;=\\; \\mathrm{{RSS}} + \\lambda \\|\\beta\\|_2^2$$

  <p>$\\lambda = 0$ 就是最小平方；$\\lambda \\to \\infty$ 所有係數趨近 0。
  注意<strong>截距 $\\beta_0$ 不罰</strong>——罰它等於在乎你把 y 的原點放在哪裡。</p>

{viz(chart("w06ridgeChart", "tall", "。此圖的重點：λ 變大時所有係數一起往零收縮，但沒有任何一個變成剛好 0。"),
     [info_card("怎麼看上圖",
                'x 軸可以切換 log λ 與 ‖β̂ᴿ‖₂ ⁄ ‖β̂‖₂（相對收縮量）。'
                '<strong>每條線是一個變數的係數。</strong>注意它們一起往中線靠，'
                '但到最右邊仍然沒有任何一條落在 0 上。', "圖 6.4"),
      rows_card("目前的 λ",
                [("λ", "—", "w06ridgeLam"), ("‖β̂ᴿ‖₂ ⁄ ‖β̂‖₂", "—", "w06ridgeRatio"),
                 ("非零係數", "—", "w06ridgeNz")]),
      info_card("為什麼收縮可能更準",
                'Ridge 以小幅偏差換取較大的變異下降。這個偏差–變異機制已在第 2 章完整畫過；'
                '此處只保留 Credit 的係數路徑，避免再放一張同概念的模擬曲線。')],
     "w06ridgeStatus", "拖動滑桿看係數怎麼收縮。",
     '<label class="slider-label" style="margin-right:.4rem;">log λ</label>'
     '<input type="range" id="w06ridgeSl" min="0" max="39" step="1" value="20" '
     'oninput="w06ridgeMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-toggle" onclick="w06ridgeAxis()">切換 x 軸</button>',
     provenance=("course-data", "ISLP Credit 的標準化 Ridge 路徑；對照圖 6.4"))}

{card("講義 06 · Ridge 與係數的 L2 範數",
      lab_code(CH, 122) + "\n\n" + lab_code(CH, 124), lab_output(CH, 124), src=src("122、124"),
      note="<code>ElasticNet</code> 的 <code>l1_ratio=0</code> 就是純 Ridge。"
           "係數的 L2 範數會隨 λ 單調下降。這個數字就是上圖 x 軸的分子。")}

{card("講義 06 · 用 RidgeCV 選 λ", lab_code(CH, 144), lab_output(CH, 144), src=src("144、145"),
      note="<code>RidgeCV</code> 把「掃 λ ＋ 交叉驗證」包成一步。"
           "注意 <code>alphas</code> 要給一整排值，而且照慣例是<strong>由大到小</strong>掃，"
           "因為暖啟動（warm start）從收縮較重的解開始比較快收斂。")}

{info("Ridge 之前一定要標準化", '''懲罰項 $\\sum \\beta_j^2$ 對<strong>單位敏感</strong>。
  同一個變數用「元」還是「千元」為單位，最小平方的預測完全一樣（係數等比例調整），
  Ridge 的懲罰會隨係數尺度改變：係數變大 1000 倍，懲罰項就變大 10⁶ 倍，這個變數受到的收縮也會更強。<br><br>
  所以標準做法是先把每個 $x_j$ 標準化成標準差 1 再配適。<code>scikit-learn</code> 的解法是
  <code>Pipeline([('scaler', StandardScaler()), ('ridge', Ridge())])</code>，
  順便解決了 CV 的洩漏問題。''', "warm")}

{quiz("qRidge", "QUIZ · Ridge",
      "把某個預測變數的單位從「元」改成「千元」（數值除以 1000）。Ridge 的預測會變嗎？",
      [(True, "會變，因為 L2 懲罰對單位敏感。這正是為什麼要先標準化",
        "對。係數會變成 1000 倍，懲罰項變成 10⁶ 倍，這個變數於是被壓得特別兇，整個解就不同了。最小平方沒有這個問題。"),
       (False, "不會，因為線性模型對預測變數的線性變換不變",
        "<strong>最小平方</strong>的係數等比例調整時，預測保持相同。Ridge 的懲罰項則依調整後的係數計算，換單位會改變懲罰與配適之間的取捨。"),
       (False, "不會，因為 scikit-learn 會自動標準化",
        "<code>Ridge</code> 預設<strong>不會</strong>標準化（早期版本的 <code>normalize</code> 參數已經移除）。你得自己包 <code>StandardScaler</code>。")])}
"""

# ── P05 Lasso ─────────────────────────────────────────────────────────
BODIES["lasso"] = f"""
  <p>Ridge 的缺點是：它留下全部 p 個變數。p = 500 的時候你得到 500 個很小但不為零的係數，
  模型一點也不好解釋。Lasso 把 L2 換成 <strong>L1</strong>：</p>

  $$\\mathrm{{RSS}} + \\lambda \\sum_{{j=1}}^{{p}} |\\beta_j|
    \\;=\\; \\mathrm{{RSS}} + \\lambda \\|\\beta\\|_1$$

  <p>只差一個平方，行為完全不同：<strong>λ 夠大時 Lasso 會把一部分係數壓成剛好 0</strong>，
  於是它同時做了收縮與變數選擇。這種解叫做<strong>稀疏</strong>（sparse）。</p>

  <h3 id="dx-geom">為什麼 L1 會歸零、L2 不會</h3>
  <p>把兩者寫成等價的約束型式（$s$ 是預算，跟 $\\lambda$ 一對一對應）：</p>

  $$\\min_{{\\beta}} \\mathrm{{RSS}} \\quad \\text{{s.t.}} \\quad
    \\|\\beta\\|_1 \\le s \\;\\;(\\text{{Lasso，菱形}})
    \\qquad\\text{{或}}\\qquad
    \\|\\beta\\|_2 \\le s \\;\\;(\\text{{Ridge，圓；預算重新參數化}})$$

  <p>RSS 的等高線是以 $\\hat\\beta^{{\\mathrm{{OLS}}}}$ 為中心的同心橢圓。解就是
  <strong>橢圓第一次碰到約束區域的那一點</strong>。菱形有<em>尖角</em>而且尖角剛好落在座標軸上，
  所以碰撞很容易發生在尖角。那裡有一個座標是 0。圓沒有尖角，碰到座標軸是機率 0 的事。</p>

{viz(svg("w06geomSvg", 380),
     [info_card("動手玩",
                '拖動滑桿縮小預算 s，看解怎麼被推出去。切換 L1／L2 比較兩者的接觸點：'
                '<strong>L1 的解常常「卡」在尖角上（某個係數變成剛好 0），'
                'L2 的解只是變小、方向幾乎不變。</strong>', "圖 6.7"),
      rows_card("這個 s 之下的解",
                [("預算 s", "—", "w06geomS"), ("β₁", "—", "w06geomB1"),
                 ("β₂", "—", "w06geomB2"), ("有幾個剛好是 0", "—", "w06geomNz"),
                 ("RSS", "—", "w06geomRss")]),
      info_card("看不到尖角效應？",
                '把 s 調到 1.5 以下，並注意橢圓的傾斜方向。'
                'β̂ 的兩個座標差得愈多，尖角效應愈明顯。'
                '這也解釋了為什麼<strong>真實係數本來就稀疏</strong>時 Lasso 特別佔優勢。')],
     "w06geomStatus", "紅色橢圓是 RSS 等高線，藍色區域是約束。解在兩者相切處。",
     '<label class="slider-label" style="margin-right:.4rem;">預算 s</label>'
     '<input type="range" id="w06geomSl" min="20" max="400" step="5" value="200" '
     'oninput="w06geomMove()" style="flex:1 1 140px;max-width:200px;min-width:0;">'
     '<button class="btn btn-toggle" id="w06geomBtn" onclick="w06geomToggle()">切換為 L2（Ridge）</button>',
     provenance=("book-redraw", "依講義圖 6.7；約束最佳解以解析邊與 Lagrange 方程求得"))}

{viz(chart("w06lassoChart", "tall", "。此圖的重點：λ 變大時係數一個一個變成剛好 0，最後只剩幾個變數存活。"),
     [info_card("怎麼看",
                '跟 Ridge 那張圖同樣的畫法，但這裡的線會<strong>真的碰到 0 並停在 0</strong>。'
                '右側清單是在目前這個 λ 之下還沒被歸零的變數。', "圖 6.6"),
      rows_card("目前的 λ",
                [("λ", "—", "w06lassoLam"), ("非零係數", "—", "w06lassoNz"),
                 ("CV 選出的 λ", "364.76", "w06lassoCv")]),
      info_card("保留的變數",
                '<div id="w06lassoVars" class="mono" style="font-size:.74rem;line-height:1.9;">—</div>')],
     "w06lassoStatus", "拖動滑桿看變數一個一個被淘汰。",
     '<label class="slider-label" style="margin-right:.4rem;">log λ</label>'
     '<input type="range" id="w06lassoSl" min="0" max="39" step="1" value="24" '
     'oninput="w06lassoMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-reset" onclick="w06lassoCvJump()">跳到 CV 選出的 λ</button>',
     provenance=("course-data", "ISLP Credit 的標準化 Lasso 路徑；對照圖 6.6"))}

{card("講義 06 · Lasso 與被歸零的係數",
      lab_code(CH, 162) + "\n\n" + lab_code(CH, 172), lab_output(CH, 172), src=src("162、172"),
      note="注意輸出裡有<strong>剛好等於 0</strong> 的係數。這些係數精確等於 0。"
           "這是 Lasso 跟 Ridge 最實際的差別：你可以直接說「這些變數被模型丟掉了」。")}

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
     "會嚴重高估顯著性。那是同一份資料用了兩次，跟第 5 章的 CV 誤用是同一個病。</p>"
     "<p>要做選後推論（post-selection inference）需要專門的方法"
     "（selective inference、debiased lasso 等），已經超出本課範圍。"
     "可以依實際的選擇結果說：<strong>「在這個 λ 之下，Lasso 保留了這些變數」</strong>，"
     "而不是「這些變數顯著」。</p>"),
    ("Q：兩個高度相關的變數，Lasso 會怎麼處理？",
     "<p>傾向<strong>隨機留一個、丟另一個</strong>，因為留一個就夠解釋，留兩個要多付一份 L1 懲罰。</p>"
     "<p>問題是「留哪一個」很不穩定，資料動一點就換人。這在解釋上很危險："
     "你可能報告「基因 A 重要、基因 B 不重要」，而重跑一次結論就反過來。</p>"
     "<p>Ridge 相反，它會讓相關的變數<strong>平分</strong>係數。想要「同進同出」的行為，"
     "elastic net 或 group lasso 是更合適的工具。</p>"),
])}

{quiz("qLasso", "QUIZ · Lasso 的幾何",
      "為什麼 L1 約束區域（菱形）會讓解落在座標軸上，而 L2（圓）不會？",
      [(True, "菱形的尖角剛好在座標軸上，橢圓等高線很容易先碰到尖角；圓處處平滑，碰到軸是機率 0 的事",
        "對。這是 ISLP 圖 6.7 的全部內容。維度更高時 L1 是超菱形，尖角與各種低維的稜、面都落在「某些座標為 0」的子空間上，所以稀疏解更容易發生。"),
       (False, "因為 L1 懲罰比 L2 懲罰強，把係數壓得更兇",
        "λ 可以調整懲罰強度；稀疏性來自約束區域的<strong>形狀</strong>與尖角。同樣的收縮量下，L2 只是縮短向量，L1 會把它推到軸上。"),
       (False, "因為 Lasso 用的是絕對值，絕對值函數在 0 沒有定義",
        "絕對值在 0 是有定義的（等於 0），只是<em>不可微</em>。不可微確實是機制的一部分（次微分在 0 是一整個區間），但「沒有定義」是錯的說法。")])}
"""

# ── P06 怎麼選 λ ───────────────────────────────────────────────────────
BODIES["lambda"] = f"""
  <p>λ 是<strong>調整參數</strong>（tuning parameter），不是從資料估出來的參數。
  選它的方法跟第 5 章選多項式次數完全一樣：<strong>掃一排候選值，用交叉驗證比較。</strong></p>

  <ol>
    <li>選一排 λ（通常是<strong>對數等距</strong>，例如從 10⁻² 到 10⁵ 取 100 個點）。</li>
    <li>對每個 λ 做 k-fold CV，得到 CV 誤差。</li>
    <li>選 CV 誤差最小的 λ，或用 one-SE 規則選一個更大（更收縮）的 λ。</li>
    <li><strong>用全部資料在那個 λ 上重配一次</strong>，交出這個模型。</li>
  </ol>

  <p>Credit 資料上 Lasso 的 CV 選出 λ = <strong>364.76</strong>，
  在那個 λ 之下 11 個變數全部仍保留。這份資料的係數並不稀疏，
  所以在這個設定下保留了全部變數。
  <strong>Lasso 是否產生零係數，取決於資料與 λ 的選擇。</strong></p>

{info("為什麼用對數等距選 λ", '''因為 λ 的作用是乘性的。從 1 到 2 的改變跟從 1000 到 1001
  的改變完全不同量級——前者讓懲罰加倍，後者幾乎沒差。等距取樣會把幾乎全部的點浪費在
  「懲罰太重、係數全被壓平」的那一端。<br><br>
  <code>np.logspace(-2, 5, 100)</code> 或 <code>10**np.linspace(a, b, 100)</code>
  才是對的做法。''')}

{card("講義 06 · 用 ElasticNetCV 選 λ 並取最小 CV 誤差",
      lab_code(CH, 168), lab_output(CH, 168), src=src("162、168"),
      note="<code>mse_path_</code> 的形狀是（λ 個數 × 折數），"
           "<code>.mean(1)</code> 先對折取平均、再取最小值，就是 CV 曲線的最低點。")}

{quiz("qLam", "QUIZ · 選 λ",
      "用 CV 選好 λ 之後，最終交出的模型應該是？",
      [(True, "用全部資料、在選出的那個 λ 上重配一次的模型",
        "對。CV 比較各個設定；每一折配出的模型只用了 (k−1)/k 的資料。選好設定後，依本頁流程用全部訓練資料重新配適。"),
       (False, "k 折各自配出來的模型的平均",
        "線性模型可定義係數平均；非線性模型則缺少這種共同的係數平均定義。本頁的 CV 流程用來比較 λ，選好後用全部訓練資料重新配適。"),
       (False, "CV 誤差最小的那一折所配出來的模型",
        "那一折之所以誤差最小，很可能只是它的驗證資料剛好比較好預測。挑「運氣最好的一折」是選擇偏差的典型例子。")])}
"""

# ── P07 PCR ───────────────────────────────────────────────────────────
BODIES["pcr"] = f"""
  <p>第三條路：<strong>不動變數，改換座標。</strong>先把 p 個相關的預測變數壓成
  M 個互不相關的方向（M ≪ p），再對這 M 個方向做最小平方。</p>

  <p>主成分迴歸（principal components regression, PCR）用的方向就是第 12 章的主成分：
  第一主成分是 X 變異最大的方向，第二個是在跟第一個正交的條件下變異最大的方向，依此類推。</p>

  $$Z_m = \\sum_{{j=1}}^{{p}} \\phi_{{jm}} X_j, \\qquad
    y_i = \\theta_0 + \\sum_{{m=1}}^{{M}} \\theta_m z_{{im}} + \\varepsilon_i$$

  <p>M 是調整參數，同樣用 CV 選。M = p 時 PCR 就退回最小平方（只是換了個座標）；
  M 小的時候，被丟掉的那些低變異方向就是被收縮掉的部分。</p>

{viz(svg("w06dirSvg", 340),
     [info_card("PCA 方向 vs PLS 方向",
                '拖動滑桿改變 y 對兩個 x 的依賴方向。'
                '<span style="color:var(--accent2);font-weight:700;">藍線 PC1</span> '
                '只看 X 的散佈，所以<strong>完全不動</strong>；'
                '<span style="color:var(--accent);font-weight:700;">紅線 PLS1</span> '
                '也看 y，所以會跟著轉。', "圖 6.14–6.15"),
      rows_card("目前的方向",
                [("y 的真實方向", "—", "w06dirTrue"), ("PC1 方向", "—", "w06dirPca"),
                 ("PLS1 方向", "—", "w06dirPls"),
                 ("PC1 與真實方向的夾角", "—", "w06dirAng")]),
      info_card("這說明了什麼",
                'PCR 的方向<strong>完全是非監督式的</strong>。它假設「X 變異大的方向也是跟 y 有關的方向」。'
                '這個假設常常成立，但沒有保證。PLS 讓 y 參與挑方向，'
                '所以在這個假設不成立時表現較好。')],
     "w06dirStatus", "灰點是資料，兩條線分別是 PC1 與 PLS1 的方向。",
     '<label class="slider-label" style="margin-right:.4rem;">y 的方向</label>'
     '<input type="range" id="w06dirSl" min="0" max="180" step="3" value="20" '
     'oninput="w06dirMove()" style="flex:1 1 140px;max-width:220px;min-width:0;">'
     '<button class="btn btn-reset" onclick="w06dirReset()">重置</button>',
     provenance=("illustrative", "依講義圖 6.14–6.15 的 PCR／PLS 方向差異示意"))}

{card("講義 06 · 用 CV 選主成分個數 M",
      lab_code(CH, 182), lab_output(CH, 182), src=src("180、182"),
      note="<code>pca__n_components</code> 這種雙底線寫法是 <code>Pipeline</code> 的參數命名慣例："
           "步驟名 ＋ <code>__</code> ＋ 該步驟的參數名。標準化同樣包在 pipeline 裡，"
           "PCA <strong>必須</strong>在標準化之後做——不然變異數大的變數會主宰第一主成分。")}

{card("講義 06 · 各主成分解釋了多少變異", lab_code(CH, 188), lab_output(CH, 188), src=src("188"),
      note="<code>explained_variance_ratio_</code> 就是第 12 章的 PVE。"
           "累加起來可以回答「留幾個主成分才夠」。")}

{qa("觀念釐清", [
    ("Q：PCR 算不算變數選擇？",
     "<p>不算。每一個主成分都是<strong>全部 p 個原始變數的線性組合</strong>，"
     "所以就算你只留 M = 2 個主成分，最終模型仍然用到了每一個原始變數。</p>"
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
      "PCR 用 M = 2 個主成分。最終模型用到了幾個原始預測變數？",
      [(True, "全部 p 個，因為每個主成分都是所有原始變數的線性組合",
        "對。PCR 不做變數選擇。這是它跟 Lasso 最重要的差別。它只是把 p 維壓進 M 維，沒有丟掉任何變數。"),
       (False, "2 個，就是 loadings 最大的那兩個",
        "M = 2 指的是<strong>主成分</strong>的個數，不是原始變數的個數。每個主成分的 loading 向量長度都是 p，而且通常每一項都不為零。"),
       (False, "不確定，要看 CV 選出多少",
        "CV 選的是 M（主成分個數）。不管 M 是多少，只要 M ≥ 1，用到的原始變數就是全部 p 個。")])}
"""

# ── P08 PLS ───────────────────────────────────────────────────────────
BODIES["pls"] = f"""
  <p>PCR 挑方向時<strong>完全沒看 y</strong>。這有點浪費。我們明明知道 y 是什麼。</p>

  <p>偏最小平方（partial least squares, PLS）修掉這一點：第一個方向的權重直接取
  $\\phi_{{j1}} \\propto$ 每個 $X_j$ 與 $y$ 的簡單線性迴歸係數，
  也就是<strong>跟 y 相關性愈強的變數，權重愈大</strong>。
  取完第一個方向後，把各變數對它迴歸取殘差，再在殘差上重複同樣的步驟得到第二個方向。</p>

  <p>上一節那個元件就是在演這件事：拖滑桿改變 y 的方向，PLS1 跟著轉、PC1 不動。</p>

{table(["", "方向怎麼挑", "有沒有用到 y", "做變數選擇嗎", "何時較好"],
       [["PCR", "X 變異最大的方向", "沒有", "沒有", "X 的主要變異方向剛好跟 y 有關時"],
        ["PLS", "跟 y 相關性最強的方向", "有", "沒有", "X 的大變異方向跟 y 無關時"],
        ["Ridge", "不換座標，全部收縮", "有（配適時）", "沒有", "很多變數都有小貢獻"],
        ["Lasso", "不換座標，部分歸零", "有（配適時）", "<strong>有</strong>", "真實係數稀疏"]])}

  <p>實務上 PLS 的表現常常<strong>跟 PCR 差不多</strong>，有時還略差。原因是：
  它雖然降低了偏差（方向跟 y 有關），但也增加了變異（方向是估出來的，而且用到了 y）。
  ISLP §6.3.2 的結論就是這樣：PLS 沒有一致地贏過 PCR 或 Ridge。</p>

{card("講義 06 · 用 CV 選 PLS 的成分個數", lab_code(CH, 194), lab_output(CH, 194), src=src("192、194"),
      note="<code>PLSRegression</code> 的 <code>n_components</code> 跟 PCR 的 "
           "<code>n_components</code> 是同一個角色的調整參數，一樣用 CV 選。"
           "注意它預設 <code>scale=True</code>，已經幫你標準化了。")}

{quiz("qPls", "QUIZ · PLS",
      "PLS 相對於 PCR 的差別是什麼？",
      [(True, "挑方向時用到了 y，所以方向會跟著 y 轉；但降維與不做變數選擇這兩點跟 PCR 一樣",
        "對。這是「監督式降維」對「非監督式降維」。也因為方向是用 y 估出來的，PLS 的變異比 PCR 大，兩者實務上常打成平手。"),
       (False, "PLS 會把不重要的變數歸零，所以比 PCR 好解釋",
        "不會。歸零是 <strong>Lasso</strong> 的性質。PLS 的每個成分仍然是全部 p 個變數的線性組合。"),
       (False, "PLS 不需要標準化，PCR 需要",
        "兩者都需要，理由相同（方向的定義對單位敏感）。<code>PLSRegression</code> 只是預設 <code>scale=True</code> 幫你做了。")])}
"""

# ── P09 高維度 ─────────────────────────────────────────────────────────
BODIES["highdim"] = f"""
  <p>基因資料、文字資料、感測器資料常常是 <strong>p 遠大於 n</strong>：
  幾萬個變數、幾百個樣本。這時候傳統最小平方的<strong>唯一係數解與一般推論不再適用</strong>，需要額外的結構或選解規則。</p>

  <p>當 p ≥ n，且含截距的設計矩陣有 n 個獨立的列時，最小平方能
  <strong>完美配適訓練資料</strong>：RSS = 0；y 非常數時訓練 R² = 1。
  這只說明模型能插值，不代表一定能或一定不能預測新資料。係數通常不唯一，
  必須說明如何選解，再用獨立資料評估；不能拿訓練滿分當作泛化證據。</p>

{viz(chart("w06hdChart", "tall", "。此圖的重點：n = 20、p 從 1 增到 19（加截距共 20 個參數）時，訓練 R² 一路衝到 1，而測試 MSE 從 1.07 爆到 46.3。"),
     [info_card("上圖在做什麼",
                'n = 20 的<strong>純雜訊</strong>模擬：X 與 y 完全獨立，沒有任何有用的預測變數。'
                'x 軸是變數個數 p；p = 19 加上截距後共 20 個參數。'
                '每個 p 重複 400 次；圖中訓練 R² 取平均，測試 MSE 取中位數。'
                '訓練 R² 從 0.051 升到 <strong>1.000</strong>，測試 MSE 從 1.07 升到 '
                '<strong>46.3</strong>。', "圖 6.22–6.23"),
      rows_card("關鍵數字",
                [("p = 1：訓練 R² ／ 測試 MSE", "0.051 ／ 1.07", "w06hdA"),
                 ("p = 19：訓練 R² ／ 測試 MSE", "1.000 ／ 46.3", "w06hdB")]),
      info_card("維度的詛咒",
                '這裡的變數全是雜訊，最小平方仍能利用樣本中的偶然關係改善訓練配適。'
                '對照新資料的誤差，才看得出這些改善沒有換來預測能力。', "圖 6.22–6.23")],
     "w06hdStatus", "純雜訊變數愈多，訓練 R² 愈好看、測試誤差愈糟。", "",
     provenance=("simulation", "固定種子 n=20 純雜訊模擬；對照 ISLP 圖 6.22–6.23"))}

{info("在高維度千萬不要相信這三個數字", '''<strong>1. 訓練資料上的 R²。</strong>
  模型有足夠自由度時它可能接近 1；泛化表現仍須用未參與訓練的資料評估。<br>
  <strong>2. 訓練資料上的 RSS 或 MSE。</strong>同理，可能接近 0；測試誤差需要另外評估。<br>
  <strong>3. 用同一份資料選完變數之後算出來的 p 值。</strong>
  從幾萬個變數裡挑「最顯著」的，一定挑得到看起來很顯著的，那是多重比較，不是發現。<br><br>
  唯一能信的是<strong>在完全沒參與過任何選擇的資料上</strong>算出來的誤差——
  獨立的測試集，或將所有選擇步驟留在訓練折內的交叉驗證（第 5 章 P06）。''', "warm")}

{qa("觀念釐清", [
    ("Q：p > n 的時候「維度的詛咒」到底詛咒了什麼？",
     "<p><strong>新增變數也會增加估計的不確定性。</strong></p>"
     "<p>每個新增變數都需要花"
     "自由度去估它的係數，而估計本身帶進變異。一個跟 y 完全無關的變數，"
     "它的係數估計值是一個隨機的小數字，通常會偏離 0。那個隨機性直接進到預測裡。</p>"
     "<p>上圖中 X 與 y 完全獨立，所有預測變數都是雜訊。"
     "加入更多候選變數後，訓練誤差下降，測試誤差卻可能上升。"
     "<strong>因此要用獨立評估判斷新增變數是否值得保留。</strong></p>"),
    ("Q：那高維度該用什麼？",
     "<p>這一章的三類工具全部都是為此設計的："
     "<strong>子集／逐步選擇</strong>（明確減少變數）、"
     "<strong>收縮</strong>（Ridge 與 Lasso，Lasso 還順便選變數）、"
     "<strong>降維</strong>（PCR 與 PLS）。它們的共同點是<em>降低變異，代價是接受一點偏差</em>。</p>"
     "<p>在 p ≫ n 的場景，Lasso 與 elastic net 特別受歡迎，因為稀疏假設常常合理"
     "（幾萬個基因裡有關的通常只有少數幾個），而且結果可以直接列出「這幾個變數」。</p>"),
])}

{quiz("qHd", "QUIZ · 高維度",
      "n = 50、p = 500 的資料，y 不是常數，含截距的設計矩陣有 50 個獨立的列。最小平方的訓練 R² 是多少？能因此判斷泛化嗎？",
      [(True, "訓練 R² = 1；新資料的預測表現仍需獨立評估",
        "對。列滿秩讓模型能插值這 50 筆資料，且有多組係數可以達成；不同選解規則可能給出不同的新資料預測。收縮、降維與獨立評估才是在處理如何選模型的問題。"),
       (False, "訓練 R² 接近 0，因為變數比樣本多",
        "在題目給的列滿秩條件下，最小平方可以把訓練 RSS 壓成 0。變數多不會阻止插值，反而讓訓練滿分失去判斷泛化的能力。"),
       (False, "無法計算任何配適值，因為係數解不唯一",
        "可以用偽逆從多組係數解中選出一組，計算配適值。選解規則的測試表現仍須由獨立評估確認，訓練 R² 只說明訓練配適。")])}

"""

# ── EX ────────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · ISLP 6.6 第 1 題（b）",
      "最佳子集、forward stepwise、backward stepwise 各自選出的「k 個變數的最佳模型」中，"
      "<strong>測試</strong>誤差最低的會是哪一個？",
      [(True, "不確定。三者都有可能，因為測試誤差要看運氣，而三者選出的模型未必相同",
        "對。第 (a) 小題問的是<strong>訓練</strong> RSS，那個答案很確定（最佳子集必定最小或相等，因為它搜了全部）。測試誤差需要獨立評估；搜尋範圍擴大，也會增加選到恰好貼合訓練雜訊之模型的機會。"),
       (False, "最佳子集，因為它搜遍所有可能的模型",
        "這是第 (a) 小題「訓練 RSS」的答案。搜尋較廣可降低訓練 RSS，也可能配到更多訓練雜訊；測試誤差仍須另外評估。"),
       (False, "forward stepwise，因為它的搜尋空間小所以變異低",
        "forward stepwise 通常有<em>較低的變異</em>；測試誤差還受偏差與資料影響。題目要求確定指出贏家，這些資訊不足以決定。")])}

{quiz("qEx2", "EXERCISE 2 · ISLP 6.6 第 2 題（a）",
      "相對於最小平方，Lasso 的特性是？",
      [(True, "彈性較低，因此當「變異的下降」大於「偏差的上升」時，預測準度會更好",
        "對。這是課本要的標準答案句型。三個小題（Lasso／Ridge／非線性方法）的差別只在彈性是低還是高——Lasso 與 Ridge 都是<strong>降低</strong>彈性換取變異的下降。"),
       (False, "彈性較高，因此當「偏差的下降」大於「變異的上升」時會更好",
        "這是第 (c) 小題<strong>非線性方法</strong>的答案。Lasso 加了懲罰項，它的彈性比最小平方<em>低</em>，不是高。"),
       (False, "彈性一樣，只是係數的解不同",
        "不一樣。λ = 0 時兩者相同，但 λ > 0 時 Lasso 的解空間被約束住了（‖β‖₁ ≤ s），那就是彈性較低。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 6.6 第 4 題",
      "Ridge 的懲罰參數 λ 從 0 開始往上增加。<strong>訓練</strong> RSS 會怎麼變化？",
      [(True, "單調上升",
        "對。λ = 0 時就是最小平方，它<strong>定義上</strong>就是訓練 RSS 的最小值；任何約束都只會讓訓練 RSS 變大或不變。同一題還問了測試 RSS（先降後升的 U 型）、變異（單調下降）、偏差²（單調上升）、不可縮減誤差（不變）。"),
       (False, "先下降再上升，呈 U 型",
        "這是<strong>測試</strong> RSS 的形狀。訓練 RSS 沒有 U 型。它在 λ = 0 就已經是最小的了。"),
       (False, "單調下降",
        "方向相反。加懲罰只會讓「訓練 RSS 這個目標」被犧牲掉一部分，換取係數變小。")])}

{quiz("qEx4", "EXERCISE 4 · ISLP 6.6 第 9 題",
      "課本第 9 題在 <code>College</code> 資料上比較最小平方、Ridge、Lasso、PCR、PLS 的測試誤差。"
      "預期會看到什麼？",
      [(True, "五者的測試誤差常常很接近，Ridge 與 Lasso 略勝最小平方；沒有哪一個一致最好",
        "對。這一題的教學意義就在這裡：這些方法各有適合的資料條件。<code>College</code> 的 n 遠大於 p，最小平方本來就不太糟，所以收縮的好處有限。"),
       (False, "PCR 與 PLS 明顯勝出，因為它們降了維",
        "降維在 p 接近或超過 n 時才有明顯好處。<code>College</code> 是 n = 777、p = 17，最小平方毫無壓力，降維反而可能丟掉有用資訊。"),
       (False, "Lasso 一定最好，因為它同時做收縮與變數選擇",
        "Lasso 的優勢要在<strong>真實係數稀疏</strong>時才顯現。若很多變數都有小貢獻，把它們歸零反而引入偏差，Ridge 會較好。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>三類工具對照</h3>
{table(["", "做什麼", "調整參數", "會歸零嗎", "算力", "何時最適合"],
       [["最佳子集", "搜遍 2^p 個模型", "模型大小 k", "會（沒選就是 0）", "2^p，p &gt; 40 不可行", "p 很小"],
        ["Forward／backward", "貪婪地一次加／減一個", "模型大小 k", "會", "1 ＋ p(p＋1)/2", "p 中等"],
        ["Ridge（L2）", "全部係數一起收縮", "λ", "<strong>不會</strong>", "很快，有封閉解", "很多變數都有小貢獻"],
        ["Lasso（L1）", "收縮 ＋ 部分歸零", "λ", "<strong>會</strong>", "很快（座標下降）", "真實係數稀疏"],
        ["PCR", "換成 M 個非監督式方向", "M", "不會（用到全部變數）", "很快", "X 的大變異方向跟 y 有關"],
        ["PLS", "換成 M 個監督式方向", "M", "不會", "很快", "X 的大變異方向跟 y 無關"]])}

  <h3>Credit 資料上六個準則選出的模型大小</h3>
{table(["準則", "選出的大小", "懲罰項", "備註"],
       [["Cp", "6", "$+2d\\hat\\sigma^2$", "測試 MSE 的無偏估計"],
        ["AIC", "6", "常態誤差下與 Cp 等價", "從 KL 散度來"],
        ["BIC", "<strong>4</strong>", "$+\\log(n)\\,d\\hat\\sigma^2$", "n &gt; 7 時罰得比 Cp 重，偏好小模型"],
        ["調整後 R²", "7", "分母帶 $n-d-1$", "罰得最輕，選最大的模型"],
        ["10-fold CV", "6", "無（直接估測試誤差）", "不需要 $\\hat\\sigma^2$"],
        ["CV ＋ one-SE", "<strong>4</strong>", "同上，再取門檻內最簡單的", "跟 BIC 一致"]])}
  <p style="font-size:.82rem;color:var(--muted);">n = 400、p = 11、$\\hat\\sigma^2$ = 9760。
  Cp 選 6 個、BIC 選 4 個、調整後 R² 選 7 個，與 ISLP 圖 6.2 的數字相符。
  最佳子集與 forward stepwise 在大小 3 之後就開始選出不同的變數組合。</p>

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["Cp", "$\\frac{1}{n}(\\mathrm{RSS} + 2d\\hat\\sigma^2)$", "式 6.2"],
        ["AIC", "$\\frac{1}{n\\hat\\sigma^2}(\\mathrm{RSS} + 2d\\hat\\sigma^2)$", "式 6.3，常態誤差下與 Cp 等價"],
        ["BIC", "$\\frac{1}{n}(\\mathrm{RSS} + \\log(n)\\,d\\hat\\sigma^2)$", "式 6.3，$\\log n > 2$ 時罰得比 Cp 重"],
        ["調整後 R²", "$1 - \\frac{\\mathrm{RSS}/(n-d-1)}{\\mathrm{TSS}/(n-1)}$", "式 6.4"],
        ["Ridge", "$\\mathrm{RSS} + \\lambda\\sum_j \\beta_j^2$", "式 6.5，等價於 $\\|\\beta\\|_2^2 \\le s$"],
        ["Lasso", "$\\mathrm{RSS} + \\lambda\\sum_j |\\beta_j|$", "式 6.7，等價於 $\\|\\beta\\|_1 \\le s$"],
        ["主成分方向", "$Z_m = \\sum_j \\phi_{jm} X_j$", "式 6.16，$\\phi$ 由 X 的變異決定"]])}

{info("四個一定要記住的觀念", '''<strong>1. 三條路：選變數、收縮係數、換座標。</strong>
  共同點都是降低變異，代價是接受一點偏差。<br>
  <strong>2. L1 會歸零、L2 不會，差別在形狀不在強弱。</strong>
  菱形有尖角而尖角落在座標軸上；圓沒有。<br>
  <strong>3. Ridge、Lasso、PCR、PLS 之前都必須標準化。</strong>
  它們的目標函數對單位敏感，最小平方的預測則不受換單位影響。<br>
  <strong>4. 高維度時訓練 R² 可能接近 1，不能據此判斷泛化。</strong>
  只信沒參與過任何選擇的資料上算出來的誤差。''')}

{ver_note()}
"""

# ══════════════════════════════════════════════════════════════════════
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
  cap.textContent = 'p = ' + p + ' 時要配適的模型數（橫條長度是對數尺度）';
  const foot = s.add('text', { x: 12, y: H - 12, class: 'axlab' }, g);
  foot.textContent = 'p = 20 時最佳子集是 1,048,576 個，forward 只要 211 個——差 4,969 倍';
  setStatus('w06subsetStatus', 'p = ' + p + '：最佳子集 ' + best.toLocaleString('en-US')
    + ' 個模型，forward stepwise ' + step + ' 個，差 ' + HC.fmt(best / step, 1)
    + ' 倍。下面按「開始」看 forward 在真實的 Credit 資料上怎麼一步一步走。');
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
  $('w06latBestSub').textContent = names(f.best);
  $('w06latGap').textContent = f.pick === f.best ? '0（一樣）' : HC.fmt(f.gap, 3);
  hlLine('w06subsetCode', f.line);
  setStatus('w06latStatus', f.done
    ? 'forward 走完四步：' + names(f.pick) + '。這條綠色虛線就是它的路徑；'
      + '紅線是每個大小的真正最佳子集。兩者在大小 '
      + FRAMES_w06lat.diverge.join('、') + ' 分歧——貪婪走法不保證找到最佳。'
    : '第 ' + f.k + ' 步：在 ' + f.cands.length + ' 個候選裡挑 RSS 最小的 → '
      + names(f.pick) + '。同大小的最佳子集是 ' + names(f.best)
      + (f.pick === f.best ? '（剛好一樣）。' : '，<strong>forward 沒挑到它</strong>。'));
}
function w06latStart() {
  w06latPlayer = new Player({ frames: w06latFrames(), apply: w06latApply });
  w06latPlayer.reset(); w06latPlayer.play();
}
function w06latReset() {
  if (w06latPlayer) w06latPlayer.stop();
  w06latPlayer = new Player({ frames: w06latFrames(), apply: w06latApply });
  w06latApply({ k: 0, cur: 0, cands: [], pick: 0, best: 0, gap: 0, line: null });
  setStatus('w06latStatus', '按「開始」看 forward stepwise 在 Credit 的 4 個變數上怎麼走。');
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
function w06geomSolveL1(s) {
  /* 在菱形四條邊上做一維二次最小化；端點由 clamp 精確納入。 */
  let best = null, bestV = Infinity;
  [-1, 1].forEach(a => [-1, 1].forEach(b => {
    const c = [0, b * s], v = [a, -b];
    const d = [c[0] - w06geomBhat[0], c[1] - w06geomBhat[1]];
    const Av = [w06geomA[0][0] * v[0] + w06geomA[0][1] * v[1],
                w06geomA[1][0] * v[0] + w06geomA[1][1] * v[1]];
    const Ad = [w06geomA[0][0] * d[0] + w06geomA[0][1] * d[1],
                w06geomA[1][0] * d[0] + w06geomA[1][1] * d[1]];
    const den = v[0] * Av[0] + v[1] * Av[1];
    const t = Math.max(0, Math.min(s, -(v[0] * Ad[0] + v[1] * Ad[1]) / den));
    const cand = [c[0] + t * v[0], c[1] + t * v[1]];
    const value = w06geomRss(cand);
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
function w06hdToggle() { w06hdR2 = !w06hdR2; w06hdDraw(); }
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
    + F.trainR2[F.trainR2.length - 1] + '，而測試 MSE 從 ' + F.testMse[0] + ' 爆到 '
    + F.testMse[F.testMse.length - 1] + '。');
}

/* ---------- 啟動 ----------
   SVG 元件一律放在 HC.ready() 外面：Chart.js 從 CDN 載不到時 HC.ready() 不會執行，
   把 SVG 初始化放進去會讓手寫元件跟著死掉。 */
w06subsetCounts();
w06latReset();
w06geomDraw();
w06dirDraw();
HC.ready(() => {
  w06ridgeDraw();
  w06lassoDraw();
  w06hdDraw();
});
"""


if __name__ == "__main__":
    apply("model_selection", BODIES, PAGEJS, frames())
