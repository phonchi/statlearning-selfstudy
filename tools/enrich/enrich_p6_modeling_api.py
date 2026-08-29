#!/usr/bin/env python3
"""p6_modeling_api.html（先備 P6 · 建模 API）完整自學充實。冪等。

內容依據：Ch03-linreg-lab-zh.ipynb（statsmodels 的 MS／OLS／summarize，
以及同一個模型的 sklearn 版本）與 Ch05-resample-lab-zh.ipynb
（train_test_split、cross_validate）。程式碼與輸出逐字取自 lab。

這一頁最好的教材是 lab 自己給的巧合：同一個 lstat 模型，
statsmodels 給 34.5538 / −0.9500，sklearn 給 34.5538408793831 / −0.95004935，
對 lstat=5,10,15 的預測值兩邊逐位相同。兩套 API 算的是同一件事，差別在它們回答什麼問題。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import (apply, card, chart, hook, info, info_card, lab_code,  # noqa: E402
                 lab_output, qa, quiz, rows_card, svg, table, ver_note, viz)

LAB3 = "Ch03-linreg-lab-zh.ipynb"
LAB5 = "Ch05-resample-lab-zh.ipynb"


def C(ch, *ks):
    return "\n".join(lab_code(ch, k) for k in ks)


def O(ch, k):
    return lab_output(ch, k)


def S(ch, *ks):
    lab = LAB3 if ch == 3 else LAB5
    return f'<code>{lab}</code> · 儲存格 ' + "、".join(str(k) for k in ks)


BODIES = {}

# ── PROLOGUE 兩套 API ──────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>Python 做統計建模有兩套主流工具，這門課兩套都會用到。它們算的東西常常一模一樣，
  但<strong>回答的問題不同</strong>：statsmodels 給你係數、標準誤與 p 值，
  是為了讓你<em>解釋</em>；scikit-learn 給你 <code>fit</code>／<code>predict</code>／
  <code>score</code>，是為了讓你<em>預測</em>並且評估得誠實。</p>

{info("這一頁最值得記住的一件事",
      "同一個模型在兩套 API 底下<strong>係數完全一樣</strong>——"
      "課程 lab 裡 statsmodels 給 34.5538 與 −0.9500，sklearn 給 "
      "34.5538408793831 與 −0.95004935，對 lstat = 5、10、15 的預測值逐位相同。"
      "所以「選哪一套」不是精度問題，是<strong>你要什麼輸出</strong>的問題。")}

{viz(svg("w19apiSvg", 340),
     [info_card("按按鈕比較",
                "同一件事在兩套 API 的寫法。注意 statsmodels 要你<strong>自己</strong>"
                "把截距欄放進 X，sklearn 則是用 <code>fit_intercept=True</code> 幫你處理。"),
      rows_card("這一步",
                [("statsmodels", "—", "w19apiSm"),
                 ("scikit-learn", "—", "w19apiSk"),
                 ("差在哪", "—", "w19apiWhy")]),
      info_card("什麼時候用哪一套",
                "要<strong>報告係數與顯著性</strong>（第 3、4 章）→ statsmodels。<br>"
                "要<strong>比較模型、做交叉驗證、串前處理</strong>（第 5、6 章之後）→ scikit-learn。<br>"
                "兩者可以混用：課程 lab 就用 <code>sklearn_sm</code> 把 statsmodels 的模型"
                "包成 sklearn 的估計器，好丟進 <code>cross_validate</code>。")],
     "w19apiStatus", "四個步驟，看兩套 API 各自怎麼寫。",
     '<button class="btn btn-toggle" onclick="w19apiSet(0)">① 準備 X</button>'
     '<button class="btn btn-toggle" onclick="w19apiSet(1)">② 配適</button>'
     '<button class="btn btn-toggle" onclick="w19apiSet(2)">③ 看結果</button>'
     '<button class="btn btn-toggle" onclick="w19apiSet(3)">④ 預測</button>',
     provenance=("course-data", "依 Ch03 lab 的 statsmodels 與 scikit-learn 同一 lstat 模型逐步對照。"))}

{card("statsmodels：截距要自己放進 X", C(3, 22), O(3, 22), src=S(3, 22),
      note="那一欄全是 1 的 <code>intercept</code> 不是裝飾——"
           "<code>sm.OLS</code> <strong>不會</strong>自動加截距，忘了就是配一條過原點的線。")}

{card("配適之後的係數表", C(3, 26), O(3, 26), src=S(3, 26),
      note="四個欄位：係數、標準誤、t 值、p 值。下一節逐欄拆開講。")}

{quiz("qApi", "PART 00 · 自我檢測",
      "你要在論文裡報告「每增加一個百分點的 lstat，medv 平均下降多少，這個估計有多確定」。"
      "該用哪一套？",
      [(True, "statsmodels",
        "對。你要的是<strong>係數與它的標準誤</strong>，"
        "而 sklearn 的 <code>LinearRegression</code> 只給 "
        "<code>coef_</code>，沒有標準誤、沒有 p 值、沒有信賴區間。"),
       (False, "scikit-learn，因為它比較新",
        "新舊不是判準。sklearn 刻意不提供推論用的統計量——"
        "它的設計目標是預測與模型選擇，不是推論。"),
       (False, "兩套都可以，反正係數一樣",
        "係數確實一樣，但<strong>「有多確定」那一半 sklearn 沒有給</strong>。"
        "題目問的正是那一半。")])}
"""

# ── P01 設計矩陣 ────────────────────────────────────────────────────────
BODIES["design"] = f"""
  <p>模型看到的從來不是你的資料框，而是一個矩陣 <strong>X</strong>：
  第一欄通常是全 1 的截距，後面每一欄是一個預測變數。
  類別變數要先展開成 0／1 的欄，交互作用要先乘起來變成新的一欄。
  <code>MS()</code>（ModelSpec）就是幫你做這件事的。</p>

{viz(svg("w19dsgSvg", 340),
     [info_card("按按鈕看它怎麼展開",
                "從一個資料框開始，看 <code>MS([...])</code> 一步步把它變成 X。"
                "類別變數與交互作用都是在這一層處理掉的。"),
      rows_card("目前",
                [("設定", "MS(['lstat'])", "w19dsSpec"),
                 ("X 的欄", "intercept, lstat", "w19dsCols"),
                 ("X 的 shape", "(506, 2)", "w19dsShape")]),
      info_card("fit_transform 與 transform",
                "<code>fit_transform</code> 在<strong>訓練資料</strong>上學會"
                "「有哪些欄、類別有哪幾種」；之後對新資料一律用 "
                "<code>transform</code>，不要再 fit 一次——"
                "不然兩邊的欄可能對不起來。這條規矩在最後一節會變成關鍵。")],
     "w19dsStatus", "先猜加了交互作用之後 X 有幾欄，再按按鈕。",
     '<button class="btn btn-toggle" onclick="w19dsSet(0)">MS([&quot;lstat&quot;])</button>'
     '<button class="btn btn-toggle" onclick="w19dsSet(1)">加 age</button>'
     '<button class="btn btn-toggle" onclick="w19dsSet(2)">加交互作用</button>'
     '<button class="btn btn-toggle" onclick="w19dsSet(3)">類別變數展開</button>',
     provenance=("course-data", "依 Ch03 lab 的 Boston 設計矩陣與 ModelSpec 用法重繪。"))}

{card("MS 幫你把資料框變成 X", C(3, 30, 32), f"{O(3, 30)}\n{O(3, 32)}", src=S(3, 30, 32),
      note="輸出跟上一節手工做的 X 完全一樣，差別是 <code>MS</code> "
           "會記得規格，之後可以對新資料重放一次。")}

{card("對新資料要用 transform", C(3, 39), O(3, 39), src=S(3, 39),
      note="三筆新的 lstat 值，經過同一個 <code>design</code> 之後"
           "自動長出 intercept 欄。<strong>這就是為什麼要保留那個物件。</strong>")}

{card("預測值", C(3, 41), O(3, 41), src=S(3, 41),
      note="lstat = 5、10、15 對應的預測 medv。記住這三個數字，"
           "下一節 sklearn 會算出<strong>逐位相同</strong>的結果。")}

{quiz("qDesign", "PART 01 · 自我檢測",
      "一個有 4 個類別的變數 <code>region</code> 放進迴歸，X 會多出幾欄？",
      [(False, "4 欄，每個類別一欄",
        "會多出共線性，四欄加起來永遠等於截距那一欄，矩陣就不滿秩了。"),
       (True, "3 欄，其中一個類別當基準",
        "對。這叫虛擬變數編碼，被留下來當基準的那一類叫參考組，"
        "其他三欄的係數都是「相對於參考組」的差。第 3 章會詳細講。"),
       (False, "1 欄，把類別編成 0、1、2、3",
        "這樣等於宣稱類別之間有等距的順序關係——"
        "「region 3 比 region 1 多兩單位」是沒有意義的敘述。")])}
"""

# ── P02 讀 summary 表 ──────────────────────────────────────────────────
BODIES["summary"] = f"""
  <p><code>summarize(results)</code> 給你四個欄位。很多人只看最後一欄的 p 值，
  這是最浪費的讀法——<strong>係數告訴你效果多大，標準誤告訴你這個估計多穩</strong>，
  p 值只是這兩者的比值換算出來的。</p>

{viz(svg("w19smSvg", 320),
     [info_card("點欄位看它的意思",
                "按按鈕切換，被選到的欄會亮起來，右邊解釋它在講什麼、"
                "以及看到什麼樣的值要警覺。"),
      rows_card("這一欄",
                [("欄位", "coef", "w19smCol"),
                 ("在講什麼", "效果的大小與方向", "w19smWhat"),
                 ("警訊", "符號跟預期相反", "w19smWarn")]),
      info_card("t 值怎麼來的",
                "<code>t = coef / std err</code>。lstat 那一列是 "
                "−0.9500 ÷ 0.039 ≈ −24.5，跟表上的 −24.528 對得起來。"
                "所以四個欄位其實只有前兩個是獨立的資訊。")],
     "w19smStatus", "四個欄位，一個一個看。",
     '<button class="btn btn-toggle" onclick="w19smSet(0)">coef</button>'
     '<button class="btn btn-toggle" onclick="w19smSet(1)">std err</button>'
     '<button class="btn btn-toggle" onclick="w19smSet(2)">t</button>'
     '<button class="btn btn-toggle" onclick="w19smSet(3)">P&gt;|t|</button>',
     provenance=("course-data", "係數、標準誤、t 與 p 值逐項取自 Ch03 lab 的 OLS summary。"))}

{card("只要係數的話", C(3, 37), O(3, 37), src=S(3, 37),
      note="<code>results.params</code> 回傳一個 Series，索引是欄名。"
           "要拿單一個係數就 <code>results.params['lstat']</code>。")}

{card("完整的 summary", C(3, 35), src=S(3, 35),
      note="這一格印出來很長（含 R²、F 統計量、殘差診斷），這裡不列，"
           "自己在 lab 裡跑一次看。四個核心欄位就是上面那張表。")}

{qa("觀念釐清", [
    ("p 值 0.000 是不是代表這個變數很重要？",
     "不是。p 值小只代表<strong>「係數不是 0」這件事很有把握</strong>，"
     "跟效果大不大無關。樣本夠大時，一個實務上可以忽略的效果也會有很小的 p 值。"
     "要談重要性要看係數本身的大小，以及它在你的問題裡代表什麼。"),
    ("標準誤跟標準差差在哪？",
     "標準差量的是<strong>個別觀測</strong>的分散程度；"
     "標準誤量的是<strong>估計量</strong>（例如這個係數）的分散程度。"
     "樣本變大時標準差不會變小，標準誤會。第 5 章的自助法就是在估標準誤。"),
])}

{quiz("qSummary", "PART 02 · 自我檢測",
      "兩個模型的 lstat 係數都是 −0.95，但 A 的標準誤是 0.04、B 是 0.60。這代表什麼？",
      [(True, "兩者估到的效果一樣大，但 B 的估計不確定得多",
        "對。同樣的點估計、不同的精確度。B 的 95% 信賴區間大約是 "
        "−0.95 ± 1.2，涵蓋了 0，也就是說 B 甚至不能排除「沒有效果」。"),
       (False, "B 的效果比較小",
        "效果的大小是 <code>coef</code> 這一欄，兩者都是 −0.95，一樣大。"
        "標準誤講的是「這個 −0.95 有多可信」。"),
       (False, "B 的模型配適得比較差",
        "配適好壞要看 R² 或殘差圖。標準誤大通常是樣本少、"
        "或這個變數跟其他變數共線。那是另一回事。")])}
"""

# ── P03 scikit-learn 的三個動詞 ────────────────────────────────────────
BODIES["skl"] = f"""
  <p>scikit-learn 的整個設計就是一句話：<strong>每一個模型都長一樣</strong>。
  線性迴歸、隨機森林、支持向量機，都是
  <code>fit(X, y)</code> 學參數、<code>predict(X)</code> 給預測、<code>score</code> 算分數。
  換模型只要換建構子那一行，後面完全不用改。</p>

{viz(svg("w19flowSvg", 340),
     [info_card("三個動詞",
                "按「單步」看資料怎麼流過去。注意 <code>fit</code> 是<strong>唯一</strong>"
                "會看 y 的一步。之後的 <code>predict</code> 只吃 X。"),
      rows_card("目前",
                [("步驟", "0 / 3", "w19flStep"),
                 ("這一步做什麼", "—", "w19flWhat"),
                 ("學到的東西存在哪", "—", "w19flWhere")]),
      info_card("結尾有底線的屬性",
                "<code>coef_</code>、<code>intercept_</code>、<code>classes_</code>——"
                "sklearn 的慣例是<strong>「配適之後才存在」的屬性結尾加底線</strong>。"
                "看到 <code>NotFittedError</code> 就是你還沒 fit 就想用它們。")],
     "w19flStatus", "按「單步」走一次 fit → predict → score。",
     '<button class="btn btn-step" onclick="w19flStep()">→ 單步</button>'
     '<button class="btn btn-play" onclick="w19flPlay()">▶ 連續播</button>'
     '<button class="btn btn-reset" onclick="w19flReset()">重置</button>',
     provenance=("course-data", "依 Ch03 lab 的 sklearn LinearRegression fit／predict／score 流程重繪。"))}

{card("同一個模型的 sklearn 版本", C(3, 110), O(3, 110), src=S(3, 110),
      note="輸出是 <code>(intercept_, coef_)</code>：34.5538408793831 與 −0.95004935。"
           "<strong>跟 statsmodels 的 34.5538 與 −0.9500 是同一組數字。</strong>"
           "另外注意 <code>reshape(-1, 1)</code>。sklearn 要的 X 一律是二維。")}

{card("評分", C(3, 113), O(3, 113), src=S(3, 113),
      note="R² 0.544 與 MSE 38.48。這裡算的是<strong>訓練資料</strong>上的分數，"
           "所以一定偏樂觀——下一節就在講這件事。")}

{card("預測新資料", C(3, 114), O(3, 114), src=S(3, 114),
      note="跟 statsmodels 的 <code>get_prediction</code> 給出"
           "<strong>逐位相同</strong>的三個數字。兩套 API 算的是同一件事。")}

{quiz("qSkl", "PART 03 · 自我檢測",
      "<code>model.fit(X_train, y_train)</code> 之後要在測試集評估，正確的寫法是？",
      [(False, "<code>model.fit(X_test, y_test)</code> 再看分數",
        "這樣是<strong>重新訓練</strong>一個模型，不是評估。"
        "測試集一旦被 fit 過就再也不是測試集了。"),
       (True, "<code>model.score(X_test, y_test)</code>",
        "對。<code>score</code> 只是拿已經學好的參數去預測再算分數，不會改動模型。"
        "同理 <code>predict</code> 也不會。"),
       (False, "<code>model.fit_transform(X_test)</code>",
        "<code>fit_transform</code> 是轉換器（scaler、PCA）的方法，"
        "估計器沒有它；而且對測試資料 fit 正是最後一節要講的資料洩漏。")])}
"""

# ── P04 切分訓練與測試 ─────────────────────────────────────────────────
BODIES["split"] = f"""
  <p>上一節的 R² 0.544 是<strong>拿訓練資料自己考自己</strong>算出來的，
  一定偏樂觀。模型可以把訓練資料背下來，那個分數不代表它對沒看過的資料有用。
  解法是把資料切成兩份：一份學、一份考。</p>

{info("這是整門課的分水嶺",
      "第 2 章的訓練 MSE 對測試 MSE、第 5 章的交叉驗證、第 6 章的模型選擇，"
      "全部建立在這一句上：<strong>評估要用模型沒看過的資料</strong>。", "warm")}

{card("切一刀", C(5, 16), src=S(5, 16),
      note="<code>random_state=0</code> 固定切法。不固定的話你今天的 MSE "
           "跟明天的不一樣，就沒辦法比較模型了。")}

{card("在驗證集上算 MSE", C(5, 20), O(5, 20), src=S(5, 20),
      note="25.57，比訓練資料上的分數誠實。這個數字後面會一直出現。")}

{card("三種常見的誤差指標", C(5, 22), O(5, 22), src=S(5, 22),
      note="MAE 3.99、MSE 25.57、RMSE 5.06。"
           "RMSE 跟 y 同單位（每加侖英里），比 MSE 好解釋；"
           "MAE 對離群值比較不敏感。")}

{viz(chart("w19cvChart", fallback="：驗證集的 MSE 從一次式的 25.57 降到二次式的 22.22，"
                                 "三次式反而略升到 22.67，複雜度不是越高越好。"),
     [info_card("三個多項式次數",
                "同一份資料、同一個切法，只改多項式的次數。"
                "二次式明顯比一次式好，三次式沒有再進步——"
                "<strong>這就是第 5、6 章在找的那個轉折點</strong>。"),
      rows_card("這些數字",
                [("degree 1", "25.5739", "w19cv1"),
                 ("degree 2", "22.2180", "w19cv2"),
                 ("degree 3", "22.6677", "w19cv3")]),
      info_card("單一次切分的問題",
                "換一個 <code>random_state</code>，這三個數字都會變。"
                "lab 儲存格 28 就示範了換切法之後結果不同——"
                "所以才需要交叉驗證，下一節講。")],
     "w19cvStatus", "驗證集 MSE：二次式最低，三次式沒有更好。",
     '<button class="btn btn-toggle" onclick="w19cvSet(0)">驗證集 MSE</button>'
     '<button class="btn btn-toggle" onclick="w19cvSet(1)">加上 LOOCV</button>',
     provenance=("course-data", "MSE 逐項取自 Ch05 lab 儲存格 26 與 34；圖只重畫這些輸出。"))}

{card("三個次數的驗證誤差", C(5, 26), O(5, 26), src=S(5, 26),
      note="上面那張圖的三個數字就是這一格的輸出，逐字取用。")}

{quiz("qSplit", "PART 04 · 自我檢測",
      "訓練集 R² 是 0.95、測試集 R² 是 0.42。最合理的判斷是？",
      [(True, "模型過度配適了訓練資料",
        "對。它把訓練資料的雜訊也學了進去，換一份資料就失效。"
        "第 2 章的偏差—變異取捨、第 6 章的收縮方法都在處理這件事。"),
       (False, "測試集有問題，應該換一個",
        "換到看得順眼為止就等於把測試集當訓練集用。"
        "測試集只能<strong>看一次</strong>，看多了它就失去意義。"),
       (False, "模型還不夠複雜，應該加更多變數",
        "方向反了。訓練分數遠高於測試分數是<strong>太複雜</strong>的徵狀，"
        "加變數只會更嚴重。")])}
"""

# ── P05 交叉驗證與資料洩漏 ─────────────────────────────────────────────
BODIES["cv"] = f"""
  <p>單切一刀有兩個問題：只用了一部分資料訓練，而且結果會隨著切法跳動。
  交叉驗證把資料輪流當驗證集，每一筆都當過一次，結果穩定得多。
  但用它之前得先弄清楚一件事——<strong>前處理要在切分的哪一邊做</strong>。</p>

{viz(svg("w19leakSvg", 340),
     [info_card("兩條路，一條是錯的",
                "左邊：先標準化整份資料、再切分。"
                "右邊：先切分、只用訓練集學標準化的參數。"
                "按「單步」看差別在哪一步發生。"),
      rows_card("目前",
                [("路線", "—", "w19lkPath"),
                 ("標準化用到了誰的資訊", "—", "w19lkInfo"),
                 ("評估可否解讀", "—", "w19lkValid")]),
      info_card("為什麼這叫洩漏",
                "先標準化的話，訓練集的每一筆都間接知道了測試集的平均與標準差。"
                "評估已經不再是乾淨的 out-of-sample 比較；"
                "分數可能被扭曲，卻不能只憑洩漏就預告一定改善多少。"
                "Pipeline 的存在就是為了讓這件事不可能發生。")],
     "w19lkStatus", "先找出哪條路在切分前看過測試集資訊。",
     '<button class="btn btn-toggle" onclick="w19lkSet(0)">先標準化再切分 ✗</button>'
     '<button class="btn btn-toggle" onclick="w19lkSet(1)">先切分再標準化 ✓</button>'
     '<button class="btn btn-step" onclick="w19lkStep()">→ 單步</button>'
     '<button class="btn btn-reset" onclick="w19lkReset()">重置</button>',
     provenance=("illustrative", "自訂資訊流示意；不附虛構 MSE，只判定評估流程是否洩漏。"))}

{card("留一交叉驗證", C(5, 34), O(5, 34), src=S(5, 34),
      note="24.2315。每一筆各當一次驗證集，所以只有一個數字、沒有隨機性——"
           "但要配適 n 次，資料大的時候很貴。")}

{card("重複切分：看平均，也看標準差", C(5, 46), O(5, 46), src=S(5, 46),
      note="平均 23.80、標準差 1.42。<strong>那個 1.42 才是重點</strong>："
           "它告訴你單切一刀的結果可以晃動多少，"
           "兩個模型的 MSE 差 0.5 根本不算差別。")}

{table(["順序", "標準化參數從哪裡估", "評估能否解讀", "判定"],
       [["先標準化 → 再切分", "全部資料（含之後的測試資料）",
         "不能當成乾淨的 out-of-sample 表現", "✗ 洩漏"],
        ["先切分 → 訓練集 fit；測試集只 transform", "只有訓練集",
         "可作為這次切分的測試表現", "✓"],
        ["<code>Pipeline</code> ＋ <code>cross_validate</code>", "每一折各自的訓練部分",
         "可彙整各折的驗證表現", "✓ 最推薦"]])}

{info("Pipeline 是紀律，不是語法糖",
      "把 <code>StandardScaler</code> 與模型包成 <code>Pipeline</code> 之後丟進 "
      "<code>cross_validate</code>，sklearn 會<strong>在每一折內部</strong>重新 fit "
      "那個 scaler。你想犯錯都犯不了。第 6 章的收縮方法一定要標準化，"
      "那時這件事就從「好習慣」變成「非做不可」。")}

{qa("觀念釐清", [
    ("交叉驗證跟測試集是不是同一件事？",
     "不是。交叉驗證是在<strong>訓練資料內部</strong>切來切去，用來選模型與調參數；"
     "測試集是最後才動一次的、完全獨立的一份，用來報告最終效能。"
     "拿測試集去選模型，等於把它變成訓練資料的一部分。"),
    ("為什麼 LOOCV 的結果沒有標準差？",
     "因為它<strong>沒有隨機性</strong>。每一筆各當一次驗證集，切法只有一種。"
     "k 折就不同了，切法隨機，所以 lab 才會用 "
     "<code>ShuffleSplit(n_splits=10)</code> 看它的平均與標準差。"),
])}

{quiz("qCv", "PART 05 · 自我檢測",
      "你先對整份資料做 <code>StandardScaler().fit_transform(X)</code>，"
      "再 <code>train_test_split</code>，最後回報測試 MSE。這個數字有什麼問題？",
      [(False, "沒問題，標準化不會改變模型的排序",
        "流程仍有問題。即使某些模型在這個例子中剛好得到相同數字，"
        "也不能把測試資料納入前處理參數的估計。"),
       (True, "它不再是嚴格獨立的評估；偏差方向與大小不能只靠『有洩漏』判定",
        "對。測試集的平均與標準差已經透過 scaler 進到訓練流程裡了，"
        "因此這個 MSE 不能當成乾淨的 out-of-sample 證據；但不能憑這件事"
        "直接宣稱它一定降低多少。"
        "正確做法是把 scaler 與模型包成 <code>Pipeline</code>，"
        "讓每一折自己 fit 自己的 scaler。"),
       (False, "應該改用 MinMaxScaler",
        "換哪一種 scaler 都一樣。問題出在<strong>順序</strong>，不是選哪個轉換器。")])}

{hook("這在本站哪一章會用到",
      '第 5 章整章都在講交叉驗證與自助法，第 6 章用交叉驗證挑收縮的強度 λ，'
      '第 8 章調樹的深度也是同一套。'
      '<a href="resampling_methods.html#kfold">→ 重抽樣方法 · k 折交叉驗證</a>　'
      '<a href="resampling_methods.html#cvwrong">→ 同一章的「先用全資料選特徵再 CV」</a>')}
"""

# ── EX 練習 ─────────────────────────────────────────────────────────────
BODIES["exercises"] = f"""
{quiz("qEx1", "EXERCISE 1 · 選工具",
      "你要比較五個模型並挑一個，中間需要標準化與多項式展開。該用哪一套？",
      [(True, "scikit-learn，把前處理與模型包成 Pipeline 再交叉驗證",
        "對。要比較模型就需要一致的評估流程，這正是 sklearn 的設計目的。"
        "Pipeline 還順便擋掉了資料洩漏。"),
       (False, "statsmodels，因為它給的統計量比較完整",
        "那些統計量在「比較五個模型」這件事上幫不上忙，"
        "而且 statsmodels 沒有 Pipeline 與 <code>cross_validate</code>。"
        "選定模型之後再用它報告係數是合理的。"),
       (False, "手寫迴圈，最有彈性",
        "彈性換來的是每一次都要自己記得「先切分再轉換」。"
        "Pipeline 存在的理由就是讓你不必依賴記憶力。")])}

{quiz("qEx2", "EXERCISE 2 · 截距",
      "<code>sm.OLS(y, Boston[['lstat']]).fit()</code> 少做了一件事。少了什麼？",
      [(True, "沒有截距欄，配出來的是一條過原點的線",
        "對。<code>sm.OLS</code> 不會自動加截距，"
        "要自己放一欄全 1（或用 <code>MS()</code>／<code>sm.add_constant</code>）。"
        "lab 儲存格 22 那一欄 <code>intercept</code> 就是在做這件事。"),
       (False, "沒有標準化 lstat",
        "線性迴歸不需要標準化，標準化不改變配適，只改變係數的單位。"
        "（第 6 章的收縮方法才非標準化不可。）"),
       (False, "y 應該放後面",
        "<code>sm.OLS</code> 的簽名就是 <code>(y, X)</code>，順序是對的。"
        "倒是 sklearn 的 <code>fit(X, y)</code> 反過來，兩套要記清楚。")])}

{quiz("qEx3", "EXERCISE 3 · 誤差的不確定性",
      "模型 A 的十折 CV MSE 是 23.8（標準差 1.4），模型 B 是 23.4（標準差 1.5）。結論是？",
      [(False, "B 比較好，選 B",
        "差距 0.4 遠小於兩者各自的標準差。這個差很可能只是切分的隨機性。"),
       (True, "兩者在這份資料上分不出高下，改用其他理由來選",
        "對。差距被不確定性淹沒的時候，就用簡單性、可解釋性或計算成本來決定——"
        "第 6 章的一倍標準誤法則正是這個想法的正式版。"),
       (False, "增加折數到 50 折再比一次",
        "折數變多會讓每一折的訓練集更大、估計的變異更小，但也更貴，"
        "而且不會讓兩個本來就很接近的模型突然分出勝負。")])}

{quiz("qEx4", "EXERCISE 4 · 洩漏",
      "下列哪一個做法<strong>不會</strong>造成資料洩漏？",
      [(False, "用全部資料算相關係數，挑出前十個變數，再切分做交叉驗證",
        "會洩漏。挑變數也是一種學習，用到測試部分的資訊就已經洩漏了。"
        "變數選擇要放進 Pipeline，跟著每一折一起做。"),
       (False, "用全部資料的中位數填補遺漏值，再切分",
        "會洩漏。中位數是從整份資料算的，測試部分的資訊進到了訓練流程。"
        "<code>SimpleImputer</code> 放進 Pipeline 就沒事。"),
       (True, "先切分，再用訓練集的平均與標準差去 transform 測試集",
        "對，這是正確的順序。<code>fit</code> 只看訓練集，"
        "<code>transform</code> 對兩邊都用同一組參數。")])}
"""

# ── REF 總覽 ────────────────────────────────────────────────────────────
BODIES["reference"] = f"""
  <p>兩套 API 的對照表，以及最後那條不能違反的順序。</p>

{table(["你要做的事", "statsmodels", "scikit-learn"],
       [["準備 X", "<code>MS([...]).fit_transform(df)</code>（截距要自己有）",
         "<code>X.values.reshape(-1,1)</code>；截距用 <code>fit_intercept=True</code>"],
        ["配適", "<code>sm.OLS(y, X).fit()</code>", "<code>model.fit(X, y)</code>"],
        ["看係數", "<code>summarize(results)</code>、<code>results.params</code>",
         "<code>model.coef_</code>、<code>model.intercept_</code>"],
        ["標準誤與 p 值", "有", "<b>沒有</b>"],
        ["預測", "<code>results.get_prediction(newX)</code>", "<code>model.predict(X)</code>"],
        ["評分", "<code>results.rsquared</code>", "<code>model.score(X, y)</code>"],
        ["交叉驗證", "包成 <code>sklearn_sm</code> 才有", "<code>cross_validate</code>"],
        ["串前處理", "沒有", "<code>Pipeline</code>"]])}

{table(["估計器（Estimator）", "轉換器（Transformer）"],
       [["<code>fit(X, y)</code> — 學參數", "<code>fit(X)</code> — 學轉換的參數"],
        ["<code>predict(X)</code> — 給預測", "<code>transform(X)</code> — 套用轉換"],
        ["<code>score(X, y)</code> — 算分數", "<code>fit_transform(X)</code> — 兩步合一"],
        ["例：LinearRegression、LogisticRegression", "例：StandardScaler、PCA、SimpleImputer"]])}

{table(["誤差指標", "公式的意思", "什麼時候用"],
       [["MAE", "平均絕對誤差", "對離群值不敏感；跟 y 同單位"],
        ["MSE", "平均平方誤差", "數學上好處理，整門課的預設"],
        ["RMSE", "MSE 開根號", "跟 y 同單位，最好解釋"],
        ["R²", "被解釋的變異比例", "跟其他模型比較時方便，但會隨變數增加而虛高"]])}

{info("三個一定要記住的觀念",
      "<strong>1. 兩套 API 算的是同一件事，差別在輸出。</strong>"
      "要係數與 p 值找 statsmodels，要預測與模型比較找 scikit-learn。<br>"
      "<strong>2. sklearn 的一切都是 fit / predict / score。</strong>"
      "換模型只要換建構子那一行；結尾有底線的屬性是配適之後才存在的。<br>"
      "<strong>3. 先切分，再轉換。</strong>"
      "順序反了，那個分數就不再是乾淨的 out-of-sample 評估；用 Pipeline 固定正確順序。")}

{ver_note((3, 5))}
"""

# ── 元件 JS ─────────────────────────────────────────────────────────────
PAGEJS = r"""
/* 共用：畫一個方塊 */
function w19box(s, g, x, y, w, h, label, fill, sub) {
  s.add('rect', {x: x, y: y, width: w, height: h, rx: 7, fill: fill,
                 stroke: HC.tok.cardBorder, 'stroke-width': 1.5}, g);
  const t = s.add('text', {x: x + w / 2, y: y + (sub ? h / 2 - 2 : h / 2 + 5),
                           'text-anchor': 'middle', cls: 'vlab',
                           'font-family': HC.MONO, fill: HC.tok.paper}, g);
  t.textContent = label;
  if (sub) {
    const u = s.add('text', {x: x + w / 2, y: y + h / 2 + 16, 'text-anchor': 'middle',
                             cls: 'axlab', fill: HC.tok.paper}, g);
    u.textContent = sub;
  }
}
function w19arrow(s, g, x1, y, x2, col) {
  s.add('path', {d: 'M' + x1 + ' ' + y + ' H ' + (x2 - 9), stroke: col || HC.tok.ink,
                 'stroke-width': 2.4, fill: 'none'}, g);
  s.add('path', {d: 'M' + x2 + ' ' + y + ' l -10 -6 v 12 z', fill: col || HC.tok.ink}, g);
}

/* ═══ w19api 兩套 API 對照 ═══ */
const w19apiS = HC.svg('w19apiSvg', {h: 340});
const w19apiCases = [
  {sm: "X = MS(['lstat']).fit_transform(Boston)", sk: "x = Boston.lstat.values.reshape(-1, 1)",
   why: 'statsmodels 的 X 要含截距欄；sklearn 要二維陣列，截距另外設'},
  {sm: 'results = sm.OLS(y, X).fit()', sk: 'model.fit(x, y)',
   why: '注意引數順序相反：OLS(y, X) 對上 fit(X, y)'},
  {sm: 'summarize(results)', sk: 'model.coef_、model.intercept_',
   why: 'statsmodels 多給標準誤、t 值與 p 值；sklearn 只有係數'},
  {sm: 'results.get_prediction(newX)', sk: 'model.predict(new_x)',
   why: '兩邊的預測值逐位相同：29.80359411、25.05334734、20.30310057'}
];
let w19apiI = 0;
function w19apiDraw() {
  const g = w19apiS.clearLayer('main');
  const c = w19apiCases[w19apiI];
  const names = ['① 準備 X', '② 配適', '③ 看結果', '④ 預測'];
  w19apiS.txtPx(24, 34, names[w19apiI], {cls: 'axtitle', fill: HC.tok.accent}, g);
  ['statsmodels', 'scikit-learn'].forEach((nm, i) => {
    const y = 66 + i * 118;
    w19apiS.add('rect', {x: 34, y: y, width: 552, height: 96, rx: 8,
                         fill: i === 0 ? HC.tok.accent : HC.tok.accent2, opacity: 0.14,
                         stroke: i === 0 ? HC.tok.accent : HC.tok.accent2,
                         'stroke-width': 2}, g);
    const t = w19apiS.add('text', {x: 48, y: y + 24, cls: 'axtitle',
                                   fill: i === 0 ? HC.tok.accent : HC.tok.accent2}, g);
    t.textContent = nm;
    const code = w19apiS.add('text', {x: 48, y: y + 62, cls: 'vlab',
                                      'font-family': HC.MONO}, g);
    code.textContent = i === 0 ? c.sm : c.sk;
  });
  document.getElementById('w19apiSm').textContent = c.sm;
  document.getElementById('w19apiSk').textContent = c.sk;
  document.getElementById('w19apiWhy').textContent = c.why;
  setStatus('w19apiStatus', c.why + '。');
}
function w19apiSet(i) { w19apiI = i; w19apiDraw(); }
if (w19apiS) w19apiDraw();

/* ═══ w19ds 設計矩陣 ═══ */
const w19dsS = HC.svg('w19dsgSvg', {h: 340});
const w19dsCases = [
  {spec: "MS(['lstat'])", cols: ['intercept', 'lstat'], shape: '(506, 2)',
   note: '一個預測變數，加上全 1 的截距欄。'},
  {spec: "MS(['lstat', 'age'])", cols: ['intercept', 'lstat', 'age'], shape: '(506, 3)',
   note: '多一個變數就多一欄。'},
  {spec: "MS(['lstat', 'age', ('lstat','age')])",
   cols: ['intercept', 'lstat', 'age', 'lstat:age'], shape: '(506, 4)',
   note: '交互作用是<b>兩欄相乘出來的新一欄</b>，不是什麼特別的機制。'},
  {spec: "MS(['region'])（4 個類別）",
   cols: ['intercept', 'region[B]', 'region[C]', 'region[D]'], shape: '(506, 4)',
   note: '4 個類別展開成 <b>3</b> 欄，A 當基準——4 欄會跟截距共線。'}
];
let w19dsI = 0;
function w19dsDraw() {
  const g = w19dsS.clearLayer('main');
  const c = w19dsCases[w19dsI];
  const cw = Math.min(126, 520 / c.cols.length);
  const x0 = 310 - c.cols.length * cw / 2;
  c.cols.forEach((nm, j) => {
    w19dsS.add('rect', {x: x0 + j * cw, y: 96, width: cw - 6, height: 30, rx: 4,
                        fill: nm === 'intercept' ? HC.tok.muted
                              : (nm.indexOf(':') >= 0 ? HC.tok.accent : HC.tok.accent2),
                        opacity: 0.9}, g);
    const t = w19dsS.add('text', {x: x0 + j * cw + (cw - 6) / 2, y: 116,
                                  'text-anchor': 'middle', cls: 'axlab',
                                  fill: HC.tok.paper}, g);
    t.textContent = nm;
    for (let r = 0; r < 4; r++) {
      w19dsS.add('rect', {x: x0 + j * cw, y: 132 + r * 32, width: cw - 6, height: 28,
                          rx: 3, fill: HC.tok.card, stroke: HC.tok.cardBorder,
                          'stroke-width': 1.1, opacity: 0.7}, g);
      const v = w19dsS.add('text', {x: x0 + j * cw + (cw - 6) / 2, y: 151 + r * 32,
                                    'text-anchor': 'middle', cls: 'vlab',
                                    'font-family': HC.MONO, fill: HC.tok.muted}, g);
      v.textContent = nm === 'intercept' ? '1.0'
        : (nm.indexOf('region') === 0 ? (r === 1 ? '1' : '0') : '…');
    }
  });
  w19dsS.txtPx(24, 34, c.spec, {cls: 'axtitle', fill: HC.tok.accent}, g);
  w19dsS.txtPx(310, 284, 'X 的每一欄都是模型的一個參數', {cls: 'axlab', anchor: 'middle'}, g);
  document.getElementById('w19dsSpec').textContent = c.spec;
  document.getElementById('w19dsCols').textContent = c.cols.join(', ');
  document.getElementById('w19dsShape').textContent = c.shape;
  setStatus('w19dsStatus', c.note);
}
function w19dsSet(i) { w19dsI = i; w19dsDraw(); }
if (w19dsS) w19dsDraw();

/* ═══ w19sm summary 四欄 ═══ */
const w19smS = HC.svg('w19smSvg', {h: 320});
const w19smCols = ['coef', 'std err', 't', 'P>|t|'];
const w19smRows = [['intercept', '34.5538', '0.563', '61.415', '0.0'],
                   ['lstat', '-0.9500', '0.039', '-24.528', '0.0']];
const w19smInfo = [
  {w: '效果的大小與方向', n: '符號跟預期相反、或大到不合理',
   note: 'lstat 每多 1，medv 平均少 0.95（千美元）。這是你真正要報告的東西。'},
  {w: '這個係數估得多穩', n: '大到讓信賴區間涵蓋 0',
   note: '樣本變大、或變數之間不共線時，標準誤會變小。'},
  {w: '係數是標準誤的幾倍', n: '絕對值小於 2',
   note: 't = coef / std err：−0.9500 ÷ 0.039 ≈ −24.5，跟表上對得起來。'},
  {w: '「係數其實是 0」的話有多難得到這個結果', n: '不要只看這一欄',
   note: 'p 值小只代表「不是 0」很有把握，<b>跟效果大不大無關</b>。'}
];
let w19smI = 0;
function w19smDraw() {
  const g = w19smS.clearLayer('main');
  const cw = 104, x0 = 148, y0 = 92;
  w19smCols.forEach((nm, j) => {
    const on = j === w19smI;
    w19smS.add('rect', {x: x0 + j * cw, y: y0, width: cw - 6, height: 32, rx: 4,
                        fill: on ? HC.tok.accent : HC.tok.muted, opacity: on ? 1 : 0.55}, g);
    const t = w19smS.add('text', {x: x0 + j * cw + (cw - 6) / 2, y: y0 + 21,
                                  'text-anchor': 'middle', cls: 'vlab',
                                  'font-family': HC.MONO, fill: HC.tok.paper}, g);
    t.textContent = nm;
  });
  w19smRows.forEach((r, i) => {
    const rl = w19smS.add('text', {x: x0 - 12, y: y0 + 58 + i * 40, 'text-anchor': 'end',
                                   cls: 'vlab', 'font-family': HC.MONO}, g);
    rl.textContent = r[0];
    r.slice(1).forEach((v, j) => {
      const on = j === w19smI;
      w19smS.add('rect', {x: x0 + j * cw, y: y0 + 38 + i * 40, width: cw - 6, height: 30,
                          rx: 3, fill: on ? HC.tok.accent2 : HC.tok.card,
                          stroke: HC.tok.cardBorder, 'stroke-width': 1.2,
                          opacity: on ? 0.95 : 0.5}, g);
      const t = w19smS.add('text', {x: x0 + j * cw + (cw - 6) / 2, y: y0 + 58 + i * 40,
                                    'text-anchor': 'middle', cls: 'vlab',
                                    'font-family': HC.MONO,
                                    fill: on ? HC.tok.paper : HC.tok.muted}, g);
      t.textContent = v;
    });
  });
  w19smS.txtPx(24, 40, 'summarize(results)', {cls: 'axtitle'}, g);
  const c = w19smInfo[w19smI];
  document.getElementById('w19smCol').textContent = w19smCols[w19smI];
  document.getElementById('w19smWhat').textContent = c.w;
  document.getElementById('w19smWarn').textContent = c.n;
  setStatus('w19smStatus', c.note);
}
function w19smSet(i) { w19smI = i; w19smDraw(); }
if (w19smS) w19smDraw();
"""

PAGEJS += r"""
/* ═══ w19fl fit / predict / score（本頁招牌之一）═══ */
const w19flS = HC.svg('w19flowSvg', {h: 340});
const w19flSteps = [
  {w: '還沒開始', where: '—', note: '模型剛建構出來，coef_ 還不存在。'},
  {w: 'fit(X, y)：唯一會看 y 的一步', where: 'model.coef_、model.intercept_',
   note: '學到的參數存在<b>結尾有底線</b>的屬性裡。'},
  {w: 'predict(X_new)：只吃 X', where: '回傳一個預測值陣列',
   note: '不會改動模型，也不需要 y —— 真實世界裡本來就沒有 y。'},
  {w: 'score(X, y)：拿預測跟真值比', where: '回傳一個數字（迴歸預設是 R²）',
   note: '用<b>測試</b>資料呼叫它才有意義。'}
];
let w19flI = 0, w19flTimer = null;
function w19flDraw() {
  const g = w19flS.clearLayer('main');
  const st = w19flI;
  const act = (k) => (st === k ? HC.tok.accent : HC.tok.muted);
  w19box(w19flS, g, 40, 60, 118, 58, 'X_train', st >= 1 ? HC.tok.accent2 : HC.tok.muted);
  w19box(w19flS, g, 40, 136, 118, 58, 'y_train', st >= 1 ? HC.tok.accent2 : HC.tok.muted);
  w19box(w19flS, g, 246, 98, 130, 58, 'model', act(1), st >= 1 ? 'coef_ 已學到' : '尚未配適');
  if (st >= 1) {
    w19arrow(w19flS, g, 162, 89, 242, HC.tok.accent2);
    w19arrow(w19flS, g, 162, 165, 242, HC.tok.accent2);
    w19flS.txtPx(202, 78, 'fit', {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent}, g);
  }
  if (st >= 2) {
    w19box(w19flS, g, 40, 232, 118, 52, 'X_new', HC.tok.accent2);
    w19arrow(w19flS, g, 162, 258, 242, HC.tok.accent2);
    w19arrow(w19flS, g, 312, 162, 312, HC.tok.accent);
    w19box(w19flS, g, 452, 98, 128, 58, 'y_pred', act(2));
    w19arrow(w19flS, g, 382, 127, 448, HC.tok.accent);
    w19flS.txtPx(415, 116, 'predict', {cls: 'axtitle', anchor: 'middle',
                                       fill: HC.tok.accent}, g);
  }
  if (st >= 3) {
    w19box(w19flS, g, 452, 232, 128, 52, 'score', HC.tok.accent);
    w19arrow(w19flS, g, 516, 162, 516, HC.tok.accent);
    w19flS.txtPx(516, 200, 'y_pred vs y_true', {cls: 'axlab', anchor: 'middle'}, g);
  }
  const s = w19flSteps[st];
  document.getElementById('w19flStep').textContent = st + ' / 3';
  document.getElementById('w19flWhat').textContent = s.w;
  document.getElementById('w19flWhere').textContent = s.where;
  setStatus('w19flStatus', s.note);
}
function w19flStep() { w19flI = Math.min(3, w19flI + 1); w19flDraw(); }
function w19flReset() {
  if (w19flTimer) { clearTimeout(w19flTimer); w19flTimer = null; }
  w19flI = 0; w19flDraw();
}
function w19flPlay() {
  w19flReset();
  const tick = () => {
    if (w19flI >= 3) { w19flTimer = null; return; }
    w19flStep();
    w19flTimer = setTimeout(tick, 950);
  };
  w19flTimer = setTimeout(tick, 500);
}
if (w19flS) w19flDraw();

/* ═══ w19lk 資料洩漏對照（本頁招牌之二）═══ */
const w19lkS = HC.svg('w19leakSvg', {h: 340});
let w19lkPath = 0, w19lkI = 0;
function w19lkDraw() {
  const g = w19lkS.clearLayer('main');
  const bad = w19lkPath === 0;
  const st = w19lkI;
  const col = bad ? HC.tok.resid : HC.tok.accent2;
  w19lkS.txtPx(24, 34, bad ? '先標準化 → 再切分（錯）' : '先切分 → 再標準化（對）',
               {cls: 'axtitle', fill: bad ? HC.tok.resid : HC.tok.accent2}, g);
  w19box(w19lkS, g, 40, 74, 132, 54, '全部資料', HC.tok.muted);
  if (st === 0) {
    /* 還沒開始走的時候畫出後面幾步的輪廓，免得整個 stage 空著 */
    const ghost = (x, y, w, h, label) => {
      w19lkS.add('rect', {x: x, y: y, width: w, height: h, rx: 7, fill: 'none',
                          stroke: HC.tok.cardBorder, 'stroke-width': 1.6,
                          'stroke-dasharray': '6 5'}, g);
      const t = w19lkS.add('text', {x: x + w / 2, y: y + h / 2 + 5,
                                    'text-anchor': 'middle', cls: 'axlab',
                                    fill: HC.tok.muted}, g);
      t.textContent = label;
    };
    if (bad) {
      ghost(248, 74, 150, 54, 'StandardScaler');
      ghost(456, 46, 124, 48, '訓練');
      ghost(456, 106, 124, 48, '測試');
    } else {
      ghost(244, 46, 118, 48, '訓練');
      ghost(244, 106, 118, 48, '測試');
      ghost(428, 42, 152, 56, 'scaler.fit');
      ghost(428, 106, 152, 52, 'transform');
    }
    w19lkS.txtPx(310, 250, '按「單步」開始', {cls: 'axlab', anchor: 'middle'}, g);
  }
  if (bad) {
    if (st >= 1) {
      w19arrow(w19lkS, g, 176, 101, 244, col);
      w19box(w19lkS, g, 248, 74, 150, 54, 'StandardScaler', col, 'fit 了全部');
    }
    if (st >= 2) {
      w19arrow(w19lkS, g, 402, 101, 452, col);
      w19box(w19lkS, g, 456, 46, 124, 48, '訓練', HC.tok.accent2);
      w19box(w19lkS, g, 456, 106, 124, 48, '測試', col);
      w19lkS.txtPx(518, 176, '測試集的平均已經', {cls: 'axlab', anchor: 'middle',
                                                fill: HC.tok.resid}, g);
      w19lkS.txtPx(518, 194, '進到訓練流程裡了', {cls: 'axlab', anchor: 'middle',
                                                fill: HC.tok.resid}, g);
    }
    if (st >= 3) {
      w19lkS.txtPx(310, 250, '測試資料已參與前處理參數估計：評估失去獨立性',
                   {cls: 'axtitle', anchor: 'middle', fill: HC.tok.resid}, g);
    }
  } else {
    if (st >= 1) {
      w19arrow(w19lkS, g, 176, 101, 240, col);
      w19box(w19lkS, g, 244, 46, 118, 48, '訓練', HC.tok.accent2);
      w19box(w19lkS, g, 244, 106, 118, 48, '測試', HC.tok.muted);
    }
    if (st >= 2) {
      w19arrow(w19lkS, g, 366, 70, 424, col);
      w19box(w19lkS, g, 428, 42, 152, 56, 'scaler.fit', col, '只看訓練集');
      w19arrow(w19lkS, g, 366, 130, 424, HC.tok.muted);
      w19box(w19lkS, g, 428, 106, 152, 52, 'transform', HC.tok.muted, '沿用訓練的參數');
    }
    if (st >= 3) {
      w19lkS.txtPx(310, 250, '測試資料只套用訓練集學到的轉換：評估仍可解讀',
                   {cls: 'axtitle', anchor: 'middle', fill: HC.tok.accent2}, g);
      w19lkS.txtPx(310, 282, 'Pipeline 會在每一折自動做這件事，讓你想犯錯都難',
                   {cls: 'axlab', anchor: 'middle'}, g);
    }
  }
  document.getElementById('w19lkPath').textContent = bad ? '先標準化再切分 ✗' : '先切分再標準化 ✓';
  document.getElementById('w19lkInfo').textContent =
    st >= 2 ? (bad ? '全部資料（含測試集）' : '只有訓練集') : '—';
  document.getElementById('w19lkValid').textContent =
    st >= 3 ? (bad ? '否：測試資訊已進入訓練流程' : '是：測試集只用於最後評估') : '—';
  setStatus('w19lkStatus', st === 0
    ? '按「單步」看資料怎麼流。'
    : (bad ? '注意 scaler 是在<b>切分之前</b> fit 的 —— 它看過測試集了。'
           : 'scaler 只在訓練集上 fit，測試集只被 transform。'));
}
function w19lkSet(i) { w19lkPath = i; w19lkI = 0; w19lkDraw(); }
function w19lkStep() { w19lkI = Math.min(3, w19lkI + 1); w19lkDraw(); }
function w19lkReset() { w19lkI = 0; w19lkDraw(); }
if (w19lkS) w19lkDraw();

/* ═══ w19cv 驗證誤差（數字逐字取自 lab 儲存格 26 與 34）═══ */
const w19cvVal = [25.57387819, 22.21802005, 22.66767544];
const w19cvLoo = 24.231513517929226;
let w19cvMode = 0;
function w19cvDraw() {
  if (!HC.hasChart()) return;
  const ds = [{label: '單次切分的驗證 MSE', data: w19cvVal,
               backgroundColor: HC.tok.accent2, borderWidth: 0}];
  if (w19cvMode === 1) {
    ds.push({label: 'LOOCV（degree 1）', data: [w19cvLoo, null, null],
             backgroundColor: HC.tok.accent, borderWidth: 0});
  }
  const c = HC.get('w19cvChart');
  if (c) { c.data.datasets = ds; c.update(); } else {
    HC.bar('w19cvChart', {labels: ['degree 1', 'degree 2', 'degree 3'], datasets: ds}, {
      scales: {x: {title: {display: true, text: '多項式次數'}},
               y: {title: {display: true, text: 'MSE'}, min: 20, max: 27}},
      plugins: {legend: {display: true}}
    });
  }
  setStatus('w19cvStatus', w19cvMode === 0
    ? '二次式 22.22 明顯低於一次式 25.57，三次式 22.67 沒有再進步。'
    : 'LOOCV 對 degree 1 給 24.23，跟單次切分的 25.57 不一樣 —— <b>切法會影響結論</b>。');
}
function w19cvSet(i) { w19cvMode = i; w19cvDraw(); }
HC.ready(() => { w19cvDraw(); });
"""

apply("p6_modeling_api", BODIES, PAGEJS)
