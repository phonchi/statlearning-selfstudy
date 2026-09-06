#!/usr/bin/env python3
"""s4_inference.html：給完全初學者的頻率學派推論先備頁。冪等。

主要概念來源是 Seeing Theory 現行 Frequentist Inference 網頁與 2018 PDF
第 41–48 頁。網頁涵蓋點估計、信賴區間與 bootstrap；PDF 另涵蓋假設
檢定、兩類錯誤與 p 值。本頁所有例子、文字與互動均為本站重新設計。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import apply, hook, info, info_card, qa, quiz, rows_card, svg, table, viz  # noqa: E402

ST_WEB = "https://seeing-theory.brown.edu/frequentist-inference/index.html"
ST_PDF_41 = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf#page=41"
ST_PDF_43 = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf#page=43"
ST_PDF_44 = "https://seeing-theory.brown.edu/doc/seeing-theory.pdf#page=44"


def source_note(text, url, label):
    return (f'<p class="source-note"><strong>{label}：</strong>{text} '
            f'<a href="{url}" target="_blank" rel="noopener">開啟原始來源</a></p>')


BODIES = {}

BODIES["estimation"] = rf"""
  <p>統計推論從一個很實際的困難開始：你想知道整個母體的特徵，卻只能觀察其中一小部分。
  例如，一間飲料店想知道所有顧客平均要等幾分鐘，不可能永遠追蹤每一位顧客，於是先抽一批人記錄等候時間。</p>

  <p><strong>參數</strong>（parameter）是母體中固定但未知的數，例如真正的平均等候時間 $\mu$。
  <strong>統計量</strong>（statistic）是從樣本算出的數，例如樣本平均 $\bar X$。
  用來猜參數的統計量稱為<strong>估計量</strong>（estimator）；看到資料後得到的具體數字叫<strong>估計值</strong>（estimate）。</p>

  $$\bar X=\frac{{1}}{{n}}\sum_{{i=1}}^n X_i$$

  <p>估計量的<strong>偏差</strong>（bias）看的是反覆抽樣後的平均位置：</p>
  $$\operatorname{{Bias}}(\hat\theta)=E(\hat\theta)-\theta。$$
  <p>若偏差為 0，估計量稱為不偏。舉例來說，若 $X_1,\ldots,X_n$ 來自同一母體且
  $E(X_i)=\mu$，則 $E(\bar X)=\mu$，所以樣本平均是不偏估計量。
  不偏是長期平均的性質；某一次算出的 13 仍可能離真正的 $\mu$ 很遠。</p>

{info("先分清楚固定與會變的東西", "母體平均 $μ$ 在這個問題裡是一個固定值，只是我們不知道它。若反覆抽不同樣本，每次的 $X̄$ 都可能不同；推論就是利用這種抽樣變動，描述估計值離參數可能有多遠。")}

  <h3>算一次：五位顧客的平均等候時間</h3>
  <p>樣本是 12、15、11、14、13 分鐘，$n=5$。樣本平均為</p>
  $$\bar x=\frac{{12+15+11+14+13}}{{5}}=13\text{{ 分鐘}}。$$
  <p>這個 13 是對 $\mu$ 的點估計。它不保證等於母體平均，也沒有單獨告訴你估計有多穩；下一節用標準誤補上這項資訊。</p>

{qa("觀念釐清", [
    ("Q：樣本平均 13 分鐘，是否表示母體平均就是 13？",
     "<p>不能這樣斷定。13 是這一次樣本提供的估計值。換一批顧客，樣本平均通常會改變；我們需要標準誤或區間來描述這種不確定性。</p>"),
])}

{quiz("qEstimate", "QUIZ · 參數與估計量",
      "某校想估計全校學生每天的平均睡眠時數，隨機抽 100 人算出平均 6.7 小時。哪個配對正確？",
      [(True, "$μ$ 是全校真正平均；6.7 是這次樣本給的估計值",
        "對。參數屬於整個母體；6.7 由已觀察的 100 人算出，是樣本對參數的估計。"),
       (False, "6.7 是固定參數；$μ$ 會隨每次抽樣改變",
        "方向顛倒了。母體與研究問題固定後，$μ$ 固定但未知；會隨抽樣改變的是樣本平均。"),
       (False, "100 是估計量；6.7 是母體大小",
        "100 是樣本數。估計量是計算規則，例如樣本平均；6.7 是套用規則後得到的估計值。")])}

{source_note("現行網頁的 Point Estimation 用抽樣估計未知參數；本節改用等候時間重新說明。", ST_WEB, "Seeing Theory 網頁 · Point Estimation")}
"""

BODIES["standard_error"] = rf"""
  <p>估計值會因樣本而變。若能從同一母體反覆抽取大小相同的樣本，每次都算 $\bar X$，
  這些樣本平均會形成一個<strong>抽樣分佈</strong>（sampling distribution）。它的標準差就是樣本平均的
  <strong>標準誤</strong>（standard error, SE）。</p>

  <p>若觀測來自同一母體、彼此獨立，而且母體有有限變異數 $\sigma^2$，則</p>
  $$\operatorname{{SE}}(\bar X)=\frac{{\sigma}}{{\sqrt n}}。$$
  <p>這個等式不要求母體是常態分佈，也不要求研究者事先知道 $\sigma$。
  若 $\sigma$ 未知，常用樣本標準差 $s$ 代替，得到估計標準誤 $s/\sqrt n$。</p>

{info("標準差與標準誤回答不同問題", "標準差描述同一批個別觀測彼此有多分散；標準誤描述換一批樣本後，估計量會變動多少。樣本數增為四倍，平均的標準誤才會減半。", "warm")}

  <h3>算一次：增加樣本如何提高精準度</h3>
  <p>假設母體標準差已知為 $\sigma=10$。抽 $n=25$ 人時，</p>
  $$\operatorname{{SE}}(\bar X)=\frac{{10}}{{\sqrt{{25}}}}=2。$$
  <p>若想把標準誤降到 1，需要 $n=100$，因為 $10/\sqrt{{100}}=1$。
  這只表示樣本平均更穩定；個別觀測的標準差仍是 10。</p>

{table(["數量", "描述誰的變動", "這個例子的值"],
       [["母體標準差 $σ$", "個別觀測", "10"],
        ["$SE(X̄)$，$n=25$", "不同樣本的平均", "2"],
        ["$SE(X̄)$，$n=100$", "不同樣本的平均", "1"]])}

{quiz("qSE", "QUIZ · 標準誤",
      "其他條件相同，樣本數從 25 增加到 100，樣本平均的標準誤會怎樣？",
      [(False, "變成原來的四分之一",
        "標準誤與 1/√n 成正比。樣本數變四倍時，√n 只變兩倍。"),
       (True, "變成原來的一半",
        "對。SE = σ/√n，所以從 25 到 100，分母由 5 變成 10。"),
       (False, "不變，因為母體標準差沒有變",
        "母體標準差確實不變，但標準誤描述樣本平均的變動，會隨樣本數增加而下降。")])}

{source_note("PDF 的 Frequentist Inference 起始段用中央極限定理說明標準化樣本平均；本節把其中的 $σ/√n$ 抽樣尺度獨立拆開，並補上有限變異與未知 σ 的條件。", ST_PDF_41, "Seeing Theory PDF · pp. 41–42")}
"""

BODIES["intervals"] = rf"""
  <p>點估計給一個數，信賴區間（confidence interval）則用「估計值 ± 誤差範圍」表達程序的不確定性。
  先看條件最乾淨的情況：$X_1,\ldots,X_n$ 獨立來自常態母體，母體標準差 $\sigma$ 已知。</p>

  $$\bar X\pm z_{{1-\alpha/2}}\frac{{\sigma}}{{\sqrt n}}$$

  <h3>算一次：95% 信賴區間</h3>
  <p>已知 $\sigma=10$，抽 $n=25$ 人得到 $\bar x=52$。95% 的臨界值為 1.96，誤差範圍是
  $1.96\times10/\sqrt{{25}}=3.92$，因此區間為</p>
  $$[52-3.92,\ 52+3.92]=[48.08,\ 55.92]。$$

{info("95% 說的是長期涵蓋率", "若一再用同一套抽樣與造區間程序，長期約 95% 的區間會涵蓋固定的真實平均數。算出 [48.08, 55.92] 後，端點與母體參數都已固定；不能再說這一條區間有 95% 機率包含它。", "warm")}

{viz(svg("w24ciSvg", 400),
     [rows_card("累計結果", [("涵蓋", "0", "w24ciHit"),
                             ("總數", "0", "w24ciTotal"),
                             ("觀察涵蓋率", "—", "w24ciRate")]),
      info_card("顏色怎麼讀", "藍線涵蓋固定真值 50；紅線漏掉真值。每一批新增 20 條，畫面保留最近 20 條，右側則累計到重置為止。"),
      info_card("模型條件", "元件刻意使用<strong>常態母體且已知 σ = 10</strong>，所以 z 區間的涵蓋率有明確基準。真實資料若 σ 未知，常改用 t 區間。")],
     "w24ciStatus", "尚未抽樣；真實平均固定為 50。",
     '<label>樣本數 <select id="w24ciN" onchange="w24ciClear()"><option value="10">10</option><option value="30" selected>30</option><option value="100">100</option></select></label>'
     '<label>信心水準 <select id="w24ciLevel" onchange="w24ciClear()"><option value="0.90">90%</option><option value="0.95" selected>95%</option><option value="0.99">99%</option></select></label>'
     '<button class="btn btn-step" onclick="w24ciAdd()">→ 新增 20 組</button>'
     '<button class="btn btn-reset" onclick="w24ciReset()">重置</button>',
     provenance=("simulation", "常態模型 μ=50、σ=10；固定種子 240906；每批 20 組，累計最多 400 組"))}

{qa("觀念釐清", [
    ("Q：99% 區間一定比 90% 好嗎？",
     "<p>99% 的長期涵蓋率較高，但同一份資料下區間也較寬。你得到較高的涵蓋保障，同時失去一些精準度。信心水準要在看資料前依用途決定。</p>"),
])}

{quiz("qCI", "QUIZ · 信賴區間",
      "已算出一條 95% 信賴區間 [48.08, 55.92]。哪句解讀符合頻率學派？",
      [(False, "真實平均有 95% 機率落在 48.08 到 55.92",
        "區間算出後，參數與端點都固定。95% 描述造區間程序反覆使用時的長期涵蓋率。"),
       (True, "同樣程序反覆抽樣造區間，長期約 95% 的區間會涵蓋真實平均",
        "對。互動圖中的藍線比例在累積多批後會接近設定的信心水準，但有限次仍會波動。"),
       (False, "95% 的觀測值會落在這個區間",
        "信賴區間估的是母體平均，不是個別觀測的範圍。個別值通常比樣本平均分散得多。")])}

{source_note("現行網頁有反覆產生信賴區間的視覺；本頁改成已知 σ 的常態模型，並明示有限次涵蓋計數。", ST_WEB, "Seeing Theory 網頁 · Confidence Interval")}
"""

BODIES["testing"] = rf"""
  <p>假設檢定（hypothesis test）把問題改寫成兩個互斥的主張。<strong>虛無假設</strong> $H_0$
  是用來計算參考分佈的基準；<strong>對立假設</strong> $H_A$ 是資料若夠不尋常時所支持的方向。</p>

  <p>在已知 $\sigma$ 的常態平均數問題中，檢定 $H_0:\mu=\mu_0$ 可用</p>
  $$z=\frac{{\bar x-\mu_0}}{{\sigma/\sqrt n}}。$$
  <p><strong>p 值</strong>（p-value）是在 $H_0$ 成立的前提下，得到目前這麼極端或更極端結果的機率。
  它不是 $H_0$ 為真的機率，也不是「結果純屬偶然」的機率。</p>

  <h3>算一次：單尾與雙尾問的是不同問題</h3>
  <p>令 $H_0:\mu=50$，已知 $\sigma=10$，$n=25$，觀察到 $\bar x=54.4$，則
  $z=(54.4-50)/(10/5)=2.20$。若 $H_A:\mu&gt;50$，右尾 p 值約為 0.0139；
  若 $H_A:\mu\ne50$，雙尾 p 值約為 0.0278。</p>

{viz(svg("w24testSvg", 350),
     [rows_card("目前檢定", [("標準誤", "—", "w24testSE"),
                             ("z 統計量", "—", "w24testZ"),
                             ("p 值", "—", "w24testP")]),
      info_card("陰影怎麼讀", "橘色面積是在虛無假設成立時，標準常態曲線上與目前 z 一樣極端或更極端的區域。雙尾會把兩側都算入。"),
      info_card("何時能用", "這裡是<strong>已知 σ = 10</strong> 的 z 檢定，且假設觀測獨立、母體常態。若 σ 未知，通常使用 t 檢定並檢查其條件。")],
     "w24testStatus", "拖動樣本平均，觀察 z 與尾端面積如何一起改變。",
     '<label>樣本數 <select id="w24testN" onchange="w24testDraw()"><option value="10">10</option><option value="25" selected>25</option><option value="100">100</option></select></label>'
     '<label>方向 <select id="w24testSide" onchange="w24testDraw()"><option value="right">右尾：μ &gt; 50</option><option value="two">雙尾：μ ≠ 50</option></select></label>'
     '<label>樣本平均 <input id="w24testMean" type="range" min="45" max="58" value="54.4" step="0.2" oninput="w24testDraw()"><span id="w24testMeanOut">54.4</span></label>'
     '<button class="btn btn-reset" onclick="w24testReset()">重置</button>',
     provenance=("illustrative", "本站重新繪製的已知 σ 常態 z 檢定；固定 μ₀=50、σ=10"))}

{info("結論只到證據強度", "若事先設定 $α=0.05$，上例兩種 p 值都小於 0.05，因此拒絕 $H_0$。若 p 值不小，結論是「未能拒絕 $H_0$」；資料可能不足，不能宣稱已證明 $H_0$。", "warm")}

{quiz("qTest", "QUIZ · p 值",
      "某檢定得到 p = 0.03。哪個說法正確？",
      [(False, "$H_0$ 為真的機率是 3%",
        "p 值的條件方向相反。它是在假設 H₀ 成立後，計算資料至少這麼極端的機率。"),
       (False, "這項研究有 97% 機率得到正確結論",
        "p 值不提供單次結論的正確機率，也不等於 1 減去錯誤率。"),
       (True, "若 $H_0$ 成立，目前這麼極端或更極端的結果出現機率是 3%",
        "對。還要結合事先設定的 α、研究設計、效果大小與模型條件來判斷。")])}

{source_note("PDF pp. 43–48 說明檢定、拒絕域與 p 值；現行網頁的 Frequentist Inference 沒有這三段。", ST_PDF_43, "Seeing Theory PDF · pp. 43–48")}
"""

BODIES["errors"] = rf"""
  <p>檢定的結論可能犯兩種錯。型一錯誤（Type I error）是在 $H_0$ 真的時候拒絕它；
  型二錯誤（Type II error）是在 $H_0$ 不真時仍未能拒絕它。這裡的條件不能省略。</p>

  $$P(\text{{拒絕 }}H_0\mid H_0\text{{ 為真}})\leq\alpha,\qquad
    \beta(\mu)=P_\mu(\text{{未拒絕 }}H_0\mid \mu\text{{ 是指定的對立值}})。$$
  <p>一般檢定把型一錯誤率控制在 $\alpha$ 以下；在本頁這種連續、精確校準的 z 檢定中，
  邊界虛無假設下會取到等號。</p>

{table(["真實情況／決策", "未拒絕 $H_0$", "拒絕 $H_0$"],
       [["$H_0$ 為真", "正確決策", "型一錯誤；機率由 $α$ 控制"],
        ["$H_0$ 不真", "型二錯誤；機率為 $β$", "正確決策；檢定力 $1-β$"]])}

  <h3>算一次：同一個 5% 檢定的型二錯誤</h3>
  <p>右尾檢定 $H_0:\mu=50$ 對 $H_A:\mu&gt;50$，已知 $\sigma=10$、$n=25$，取 $\alpha=0.05$。
  拒絕門檻為 $50+1.645(10/5)=53.290$。若真實平均其實是 54，拒絕的機率約為 0.639，
  這是該對立值下的檢定力；型二錯誤機率約為 $1-0.639=0.361$。</p>

{info("α 不是所有研究的實際誤判比例", "α 是在 H₀ 為真且模型條件成立時，這套程序的條件錯誤率。它沒有告訴你 H₀ 在研究世界中多常為真，也沒有直接給定已拒絕 H₀ 後這次結論錯誤的機率。", "warm")}

{qa("觀念釐清", [
    ("Q：把 α 從 0.05 降到 0.01，兩種錯誤都會下降嗎？",
     "<p>在樣本數與真實效果固定時，拒絕門檻會更嚴格，型一錯誤下降，但型二錯誤通常上升。增加樣本數常能同時維持較小的 α 並提高檢定力。</p>"),
])}

{quiz("qErrors", "QUIZ · 兩類錯誤",
      "藥物其實沒有療效，但研究拒絕了「沒有療效」的虛無假設。這是哪種錯誤？",
      [(True, "型一錯誤",
        "對。H₀ 真的卻被拒絕，是型一錯誤；α 控制的是這個條件機率。"),
       (False, "型二錯誤",
        "型二錯誤發生在 H₀ 不真，研究卻未能拒絕 H₀。這題的 H₀ 其實為真。"),
       (False, "沒有錯誤，因為 p 值小就表示結論正確",
        "即使程序達到顯著門檻，仍可能在 H₀ 為真時誤拒；這正是型一錯誤。")])}

{source_note("PDF pp. 44–45 定義型一與型二錯誤。本頁將型二錯誤寫成未拒絕 H₀，並將 α 明確寫成條件機率。", ST_PDF_44, "Seeing Theory PDF · Types of Error")}
"""

BODIES["bootstrap"] = rf"""
  <p>有些估計量的標準誤很難推公式。自助法（bootstrap）把手上的樣本當成一個暫時母體，
  每次<strong>有放回</strong>抽取同樣多筆，重算估計量。重複很多次後，這些估計量的標準差可用來估標準誤。</p>

  $$\widehat{{\operatorname{{SE}}}}_{{\mathrm{{boot}}}}(\hat\theta)
    =\sqrt{{\frac{{1}}{{B-1}}\sum_{{b=1}}^B
    \left(\hat\theta^{{*(b)}}-\bar{{\hat\theta}}^*\right)^2}}。$$

  <h3>小例子：看清楚「有放回」</h3>
  <p>原始樣本是 $[2,4,4,8]$，平均為 4.5。五次示意重抽可得到
  $[2,2,4,8]$、$[4,4,4,8]$、$[8,4,2,8]$、$[2,4,2,4]$、$[8,8,4,4]$；
  對應平均為 4、5、5.5、3、6，樣本標準差約 1.204。</p>

{info("五次只用來看機制", "每次重抽都是四筆，同一個原始觀測可以重複，也可能完全沒出現。實務上 B 應遠大於 5；重抽次數增加會降低模擬誤差，但不能補救不具代表性、相依性未處理或樣本太小等資料問題。", "warm")}

{table(["重抽樣本", "bootstrap 平均"],
       [["[2, 2, 4, 8]", "4.0"], ["[4, 4, 4, 8]", "5.0"],
        ["[8, 4, 2, 8]", "5.5"], ["[2, 4, 2, 4]", "3.0"],
        ["[8, 8, 4, 4]", "6.0"]])}

{hook("接到正課的重抽樣核心", '<a href="resampling_methods.html#bootstrap">重抽樣方法 · Bootstrap</a> 有完整的有放回抽樣器、袋外樣本與較大次數的標準誤示範。先在這裡掌握機制，再到正課看它如何套到較複雜的估計量。')}

{quiz("qBootstrap", "QUIZ · 自助法",
      "原始樣本有 20 筆。一次標準 bootstrap 重抽應該怎麼做？",
      [(False, "不放回抽 20 筆，所以每筆恰好出現一次",
        "這樣只會把原資料重新排序，估計量通常完全不變，無法呈現抽樣變動。"),
       (True, "有放回抽 20 次，所以有些觀測重複、有些沒出現",
        "對。樣本大小維持 20，每一抽後放回，重複計算估計量形成 bootstrap 分佈。"),
       (False, "有放回抽 2000 筆，讓資料看起來更多",
        "B 次重抽和每份樣本的大小是兩件事。通常做 B 份樣本，每份仍抽 n 筆。")])}

{source_note("現行網頁的 The Bootstrap 示範從經驗分佈有放回重抽並估樣本平均的標準誤；本節換成四筆小資料逐筆列出。", ST_WEB, "Seeing Theory 網頁 · The Bootstrap")}
"""

BODIES["exercises"] = rf"""
{quiz("qEx1", "EXERCISE 1 · 原創整合題",
      "已知母體標準差 12。要把樣本平均的標準誤從 3 降到 1.5，樣本數應如何改變？",
      [(False, "變成兩倍",
        "SE 與 1/√n 成正比。減半需要讓 √n 加倍。"),
       (True, "變成四倍",
        "對。原本 n=(12/3)²=16，後來 n=(12/1.5)²=64，是四倍。"),
       (False, "變成八倍",
        "八倍會使 SE 乘上 1/√8，降得比一半更多；題目只要求減半。")])}

{quiz("qEx2", "EXERCISE 2 · 原創整合題",
      "其他條件相同，把信心水準由 90% 提高到 99%，區間通常會怎樣？",
      [(True, "變寬，因為臨界值增加",
        "對。更高的長期涵蓋率需要更大的誤差範圍。"),
       (False, "變窄，因為我們更有信心",
        "較高信心水準需要涵蓋更多可能的樣本結果，因此區間會變寬。"),
       (False, "不變，因為樣本平均沒有變",
        "中心仍是同一個樣本平均，但臨界值改變，所以兩端會向外移。")])}

{quiz("qEx3", "EXERCISE 3 · 原創整合題",
      "一個雙尾檢定得到 p=0.08，事先設定 α=0.05。最合適的結論是？",
      [(False, "接受 $H_0$，並證明它為真",
        "p 值不大於門檻才拒絕；沒有拒絕也不能證明 H₀。"),
       (True, "未能拒絕 $H_0$；目前資料未達設定的證據門檻",
        "對。這個說法保留資料量、效果大小與模型條件可能造成證據不足的空間。"),
       (False, "$H_0$ 為真的機率是 92%",
        "p 值不是 H₀ 的後驗機率，1−p 也不是 H₀ 為真的機率。")])}

{quiz("qEx4", "EXERCISE 4 · 原創整合題",
      "bootstrap 做了 2000 份重抽。這裡的 2000 代表什麼？",
      [(False, "每一份 bootstrap 樣本含 2000 筆",
        "每份通常仍含原樣本的 n 筆；2000 是重複建立樣本的份數 B。"),
       (False, "原始研究一定有 2000 位受試者",
        "B 是計算設定，和原始樣本數 n 可以完全不同。"),
       (True, "建立 2000 份有放回重抽樣本，得到 2000 個估計量",
        "對。再以這批估計量的分散程度估標準誤或建立適當的區間。")])}
"""

BODIES["reference"] = rf"""
{table(["想回答的問題", "工具", "核心讀法", "本頁條件"],
       [["未知參數大約是多少？", "點估計", "$X̄$ 是會隨抽樣改變的估計量", "隨機且具代表性的樣本"],
        ["估計量換樣本會變多少？", "標準誤", "$SE(X̄)=σ/√n$", "獨立同分布、有限變異；σ 未知時以 s/√n 估計"],
        ["哪些參數值與資料相容？", "信賴區間", "信心水準描述程序的長期涵蓋率", "本頁互動為常態、已知 σ"],
        ["資料對基準假設有多不尋常？", "z 檢定與 p 值", "p 值以 H₀ 成立為條件", "常態、獨立、已知 σ"],
        ["公式難推時怎麼估 SE？", "Bootstrap", "有放回抽 n 筆，重算 B 次", "樣本須能代表母體；相依資料需改方法"]])}

{info("解讀檢查清單", "看到推論結果時，依序問：母體與參數是什麼？樣本怎麼來？觀測是否可視為獨立？標準差是已知還是估計？檢定方向是否事先決定？結論有沒有把 p 值誤寫成假設為真的機率？")}

  <p class="ver-note">本頁沒有引用課程 lab 程式碼或「預期輸出」。公式依 Seeing Theory 原始來源與常態模型封閉解獨立核對；算例、表格文字與兩個 SVG 互動均為本站自製。
  信賴區間元件使用常態母體 μ=50、已知 σ=10、固定種子 240906，每批 20 組且累計上限 400 組；
  z 檢定元件使用同一已知 σ 模型，p 值由共用 <code>HC.stat.pnorm</code> 的 Abramowitz–Stegun 近似計算。
  文中數值另以常態 CDF 與封閉公式核算；有限次模擬的涵蓋率會在設定值附近波動。</p>
"""


PAGEJS = r"""
/* ===== s4_inference 本頁元件（id 與全域一律 w24 前綴） ===== */

/* ---------- 信賴區間：常態母體、已知 sigma ---------- */
const w24ciSvc = HC.svg('w24ciSvg', {
  xd: [37, 63], yd: [0, 20], h: 400, w: 620,
  pad: { l: 48, r: 18, t: 24, b: 42 },
});
let w24ciBatch = 0;
let w24ciTotal = 0;
let w24ciHit = 0;
let w24ciRows = [];

function w24ciCritical(level) {
  if (level === 0.90) return 1.6448536269514722;
  if (level === 0.99) return 2.5758293035489004;
  return 1.959963984540054;
}

function w24ciRender() {
  const s = w24ciSvc;
  if (w24ciRows.length) {
    const allEnds = w24ciRows.flatMap(d => [d.lo, d.hi]);
    const lo = Math.min(37, 50, ...allEnds) - 0.6;
    const hi = Math.max(63, 50, ...allEnds) + 0.6;
    s.domain([lo, hi], [0, 20]);
  } else {
    s.domain([37, 63], [0, 20]);
  }
  s.clear();
  s.grid(4, 4, { xdec: 0, yfmt: () => '', xtitle: '樣本平均與區間端點' });
  const g = s.layer('intervals');
  s.seg(50, 0, 50, 20, { cls: 'w24ciTruth', stroke: HC.tok.accent3, sw: 2, dash: '5 4' }, g);
  s.txtPx(s.X(50) + 5, 17, '固定真值 μ = 50', { fill: HC.tok.accent3 }, g);
  if (!w24ciRows.length) {
    s.txtPx(310, 195, '按「新增 20 組」開始', { anchor: 'middle', fill: HC.tok.muted }, g);
  }
  w24ciRows.forEach((d, i) => {
    const y = 19.25 - i * 0.92;
    const col = d.cover ? HC.tok.accent2 : HC.tok.accent;
    s.seg(d.lo, y, d.hi, y, { cls: 'w24ciInterval', stroke: col, sw: 2.4 }, g);
    s.dot(d.mean, y, { cls: 'w24ciDot', fill: col, r: 2.8 }, g);
  });
  $('w24ciHit').textContent = String(w24ciHit);
  $('w24ciTotal').textContent = String(w24ciTotal);
  $('w24ciRate').textContent = w24ciTotal ? HC.pct(w24ciHit / w24ciTotal, 1) : '—';
}

function w24ciAdd() {
  if (w24ciTotal >= 400) {
    setStatus('w24ciStatus', '已到 400 組的計算上限；按重置可從相同固定序列重新開始。');
    return;
  }
  const n = Number($('w24ciN').value);
  const level = Number($('w24ciLevel').value);
  const zc = w24ciCritical(level);
  const half = zc * 10 / Math.sqrt(n);
  const rand = HC.stat.lcg(240906 + w24ciBatch * 104729);
  const fresh = [];
  for (let b = 0; b < 20; b++) {
    let sum = 0;
    for (let i = 0; i < n; i++) sum += 50 + 10 * HC.stat.normal(rand);
    const mean = sum / n, lo = mean - half, hi = mean + half;
    const cover = lo <= 50 && 50 <= hi;
    fresh.push({ mean, lo, hi, cover });
    if (cover) w24ciHit++;
    w24ciTotal++;
  }
  w24ciRows = fresh;
  w24ciBatch++;
  w24ciRender();
  setStatus('w24ciStatus', '累計 ' + w24ciTotal + ' 組，涵蓋 ' + w24ciHit + ' 組，觀察涵蓋率 '
    + HC.pct(w24ciHit / w24ciTotal, 1) + '；設定值是 ' + HC.pct(level, 0)
    + '。有限次結果不必剛好等於設定值。');
}

function w24ciClear() {
  w24ciBatch = 0; w24ciTotal = 0; w24ciHit = 0; w24ciRows = [];
  w24ciRender();
  const level = Number($('w24ciLevel').value);
  setStatus('w24ciStatus', '已清除模擬。真實平均固定為 50；目前設定的長期涵蓋率是 '
    + HC.pct(level, 0) + '。');
}

function w24ciReset() {
  $('w24ciN').value = '30';
  $('w24ciLevel').value = '0.95';
  w24ciClear();
  setStatus('w24ciStatus', '已回到預設：n = 30、信心水準 95%，真實平均固定為 50。');
}

/* ---------- z 檢定：尾端面積 ---------- */
const w24testSvc = HC.svg('w24testSvg', {
  xd: [-4, 4], yd: [0, 0.44], h: 350, w: 620,
  pad: { l: 48, r: 18, t: 26, b: 44 },
});

function w24testDraw() {
  const s = w24testSvc;
  const n = Number($('w24testN').value);
  const mean = Number($('w24testMean').value);
  const side = $('w24testSide').value;
  const se = 10 / Math.sqrt(n);
  const z = (mean - 50) / se;
  const absz = Math.abs(z);
  const p = side === 'two' ? Math.min(1, 2 * (1 - HC.stat.pnorm(absz))) : 1 - HC.stat.pnorm(z);
  const xs = HC.stat.seq(-4, 4, 241);
  s.clear();
  s.grid(8, 4, { xdec: 0, ydec: 2, xtitle: 'H₀ 下的標準常態 z', ytitle: '密度' });
  const g = s.layer('test');
  const segment = (a, b) => {
    const inside = xs.filter(x => x > a && x < b);
    return [a, ...inside, b].map(x => [x, HC.stat.dnorm(x), 0]);
  };
  if (side === 'right' && z < 4) {
    s.area(segment(Math.max(-4, z), 4), { cls: 'w24testTail', fill: 'rgba(207,95,62,.34)' }, g);
  } else if (side === 'two' && absz < 4) {
    s.area(segment(-4, -absz), { cls: 'w24testTail', fill: 'rgba(207,95,62,.34)' }, g);
    s.area(segment(absz, 4), { cls: 'w24testTail', fill: 'rgba(207,95,62,.34)' }, g);
  }
  s.poly(xs.map(x => [x, HC.stat.dnorm(x)]), {
    cls: 'w24testCurve', stroke: HC.tok.accent2, sw: 2.5,
  }, g);
  if (z >= -4 && z <= 4) {
    s.seg(z, 0, z, HC.stat.dnorm(z), {
      cls: 'w24testMark', stroke: HC.tok.accent3, sw: 2, dash: '4 3',
    }, g);
    s.txtPx(s.X(z) + (z > 2.8 ? -5 : 5), s.Y(HC.stat.dnorm(z)) - 7,
      'z = ' + HC.fmt(z, 2), { anchor: z > 2.8 ? 'end' : 'start', fill: HC.tok.accent3 }, g);
  }
  $('w24testMeanOut').textContent = HC.fmt(mean, 1);
  $('w24testSE').textContent = HC.fmt(se, 3);
  $('w24testZ').textContent = HC.fmt(z, 3);
  $('w24testP').textContent = p < 0.0001 ? '< 0.0001' : HC.fmt(p, 4);
  const windowNote = absz > 4
    ? (side === 'right' && z < -4
      ? ' z 在圖窗左方，右尾包含整個顯示範圍；p 值仍用完整常態尾端計算。'
      : ' 極端區域在目前 −4 到 4 的圖窗之外，因此看不到陰影；p 值仍用完整常態尾端計算。')
    : '';
  setStatus('w24testStatus', 'n = ' + n + '、樣本平均 = ' + HC.fmt(mean, 1)
    + '，所以 z = ' + HC.fmt(z, 3) + '、' + (side === 'two' ? '雙尾' : '右尾')
    + ' p 值 = ' + (p < 0.0001 ? '< 0.0001' : HC.fmt(p, 4))
    + '。陰影是在 H₀ 成立的條件下計算。' + windowNote);
}

function w24testReset() {
  $('w24testN').value = '25';
  $('w24testSide').value = 'right';
  $('w24testMean').value = '54.4';
  w24testDraw();
}

/* SVG 元件不依賴 Chart.js，直接初始化。 */
w24ciReset();
w24testReset();
"""


if __name__ == "__main__":
    apply("s4_inference", BODIES, PAGEJS)
