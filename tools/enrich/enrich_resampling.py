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
from lib import detail, proof, hl
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



def links(*pairs, lead="講義補充連結"):
    """講義附的外部補充連結：中文描述＋原網址。"""
    items = "、".join(f'<a href="{u}" target="_blank" rel="noopener">{t}</a>' for t, u in pairs)
    return f'<p class="source-note">{lead}：{items}。</p>'


def slider(sid, label, lo, hi, step, val, fn, shown=None):
    return (f'<div class="slider-row" style="flex:1 1 100%;">'
            f'<label class="slider-label" for="{sid}">{label}</label>'
            f'<input type="range" id="{sid}" min="{lo}" max="{hi}" step="{step}" '
            f'value="{val}" oninput="{fn}()">'
            f'<span class="slider-val" id="{sid}V">{val if shown is None else shown}</span></div>')


# ── 講義 05 逐頁對齊（2026-10-06）────────────────────────────────────────
HYPER_SECTION = r"""
  <h3 id="w05-hyper">交叉驗證與 bootstrap</h3>
  <p>本章介紹兩種重抽樣方法。<strong>交叉驗證</strong>（cross-validation）估計測試誤差，並用它挑選適當的模型彈性，也就是選<strong>超參數</strong>（hyperparameter）。講義的定義是：超參數是用來<strong>控制學習過程</strong>的參數，無法在把模型擬合到訓練集時順便推得。它分成兩類：</p>
  <ul>
    <li><strong>模型超參數</strong>：決定「學什麼模型」，例如 KNN 的 $k$、多項式次數、ridge 的 $\lambda$。</li>
    <li><strong>演算法超參數</strong>：決定「怎麼學」，例如梯度下降的學習率、batch size。</li>
  </ul>
  <p><strong>bootstrap</strong> 則用來估計參數估計值的標準差，也用在集成學習（第 8 章的 bagging）。</p>
""" + info("兩種方法的分工", r"""<strong>交叉驗證估「預測誤差」</strong>，用來比較模型、選超參數；<strong>bootstrap 估「估計量的不確定性」</strong>，例如標準誤與信賴區間。兩者都在重抽樣，問的問題不同。""", "warm") + detail("w05-detail-hyper", "延伸閱讀：參數、超參數與兩類超參數的例子", r"""
  <p><strong>參數</strong>（parameter）是擬合時由訓練資料直接學出來的量，例如線性迴歸的 $\beta_0,\beta_1,\ldots,\beta_p$，或神經網路的權重；最佳化程序會把它們算出來。<strong>超參數</strong>則是用來<strong>控制學習過程</strong>的設定值：在擬合模型之前就要先指定，訓練程序本身不會順便把它估出來，通常要靠驗證集或交叉驗證來選。例如 ridge regression：</p>
  $$\hat\beta=\arg\min_\beta\Bigl[\sum_{i=1}^n(y_i-x_i^\mathsf{T}\beta)^2+\lambda\|\beta\|^2\Bigr].$$
  <p>這裡 $\beta$ 是參數，$\lambda$ 是超參數：給定 $\lambda$，最佳化會解出 $\hat\beta$；但若把 $\lambda$ 也拿來最小化訓練誤差，永遠會選 $\lambda=0$，所以要另外用 CV 評估。兩類超參數的對照：</p>
""" + table(["", "模型超參數（model hyperparameter）", "演算法超參數（algorithm hyperparameter）"],
            [["控制什麼", "<strong>學什麼模型</strong>：模型的形式、複雜度或假設空間", "<strong>怎麼學</strong>：最佳化程序如何把模型訓練出來"],
             ["例子", "KNN 的 $k$、多項式的次數、決策樹的最大深度、ridge 的 $\\lambda$、神經網路的層數與每層神經元數",
              "學習率、batch size、epoch 數、最佳化器的選擇、momentum"],
             ["改變它會", "改變可能的擬合結果與偏差–變異取捨", "改變收斂速度、穩定性，或最後停在哪個解"]]) + r"""
  <p>例如梯度下降 $\theta^{(t+1)}=\theta^{(t)}-\eta\nabla L(\theta^{(t)})$ 的學習率 $\eta$：太大可能跳過最佳點、甚至不收斂；太小則學得很慢。它不改變模型的形式，只控制最佳化怎麼走，所以算演算法超參數。這兩類的界線並不嚴格；dropout 比例既改變有效的模型，也影響訓練過程，常被視為訓練／模型兩用的超參數。實務上大家通常統稱為超參數，重點是：<strong>它們都不由擬合程序直接估出，要靠獨立於訓練的評估來選</strong>，本章介紹的正是這類評估工具。</p>
""")

LOOCV_INTUITION = r"""
  <h3 id="w05-loocv-shortcut">一個好用的特例：最小平方的 LOOCV 捷徑</h3>
""" + info("講義：LOOCV 的捷徑公式", r"""對最小平方的線性或多項式迴歸（ISLP 式 5.2；ESL §5.5、§7.10），
  $$\mathrm{CV}_{(n)}=\frac1n\sum_{i=1}^n\left(\frac{y_i-\hat y_i}{1-h_i}\right)^2,$$
  其中 $\hat y_i$ 是用<strong>全部資料</strong>擬合一次的預測值，$h_i$ 是第 3 章的槓桿值。只要擬合<strong>一次</strong>，就能算出 LOOCV，不必擬合 $n$ 次。""", "warm") + r"""
  <p>它像普通的訓練 MSE，只是每個殘差除以 $1-h_i$：槓桿值愈大的點，愈能把擬合結果拉向自己，訓練殘差就愈樂觀，所以要放大得愈多。這個公式只適用於最小平方這類模型；scikit-learn 的通用 <code>cross_validate()</code> 不會用它，仍然真的擬合 $n$ 次。</p>
""" + detail("w05-detail-loocv-intuition", "延伸閱讀：為什麼要除以 $1-h_i$？", r"""
  <h4>$h_i$ 是「自己對自己擬合值」的權重</h4>
  <p>最小平方的擬合值是 $\hat y=Hy$，$H=X(X^\mathsf{T}X)^{-1}X^\mathsf{T}$ 是帽子矩陣，$h_i=H_{ii}$ 是第 3 章學過的槓桿值。把第 $i$ 個擬合值拆開：</p>
  $$\hat y_i=\underbrace{h_iy_i}_{\text{自己對自己的影響}}+\underbrace{\sum_{j\ne i}H_{ij}y_j}_{\text{其他資料的影響}}.$$
  <p>$h_i$ 愈大，這筆資料愈能把擬合結果拉向自己，訓練殘差 $e_i$ 就愈<strong>過度樂觀</strong>。LOOCV 不允許 $y_i$ 參與預測自己，所以要把這部分影響拿掉；刪掉一筆後係數也會重新調整，最後精確的修正剛好是除以 $1-h_i$。代數上可以先寫出刪除後的預測</p>
  $$\hat y_{(i)}=\hat y_i-\frac{h_i}{1-h_i}\,e_i,$$
  <p>於是 $y_i-\hat y_{(i)}=e_i\bigl(1+\tfrac{h_i}{1-h_i}\bigr)=\dfrac{e_i}{1-h_i}$。完整推導見本節最後的「計算細節：LOOCV 捷徑與槓桿值」。</p>
  <h4>兩個數字感受修正幅度</h4>
  <ul>
    <li>高槓桿點 $h_i=0.8$、訓練殘差 $e_i=1$：留一殘差是 $1/(1-0.8)=5$。它在完整擬合裡大幅參與了「預測自己」，真正的樣本外誤差比訓練殘差大得多。</li>
    <li>低槓桿點 $h_i=0.02$：$e_i/0.98\approx e_i$。這筆資料本來就幾乎不影響擬合，拿掉它模型幾乎不變。</li>
  </ul>
  <p>所以這個公式看起來像普通的訓練 MSE $\frac1n\sum e_i^2$，只是每個殘差都做了<strong>槓桿修正</strong>：$e_i\to e_i/(1-h_i)$。<strong>愈能影響自己擬合值的觀測，它的訓練殘差愈不可信，LOOCV 就把它放大得愈多。</strong>可以把 $1-h_i$ 理解成「不是由自己的影響造成的那一部分」。</p>
""" + links(("LOOCV 捷徑公式的證明", "https://stats.stackexchange.com/questions/164223/proof-of-loocv-formula?noredirect=1&lq=1")))

LOOCV_DRAWBACKS = r"""
  <h3 id="w05-loocv-drawbacks">LOOCV 的缺點</h3>
  <p>講義列出三點：</p>
  <ol>
    <li><strong>對資料的擾動不夠大</strong>：每次只拿掉一筆，各輪的訓練資料幾乎相同。</li>
    <li><strong>仍然很花時間</strong>：捷徑只適用於最小平方；一般方法要真的擬合 $n$ 次。</li>
    <li><strong>各折的估計高度相關</strong>：許多高度相關的數字取平均，變異降不太下來，估計可能仍有較大的變異。</li>
  </ol>
""" + detail("w05-detail-loocv-drawbacks", "延伸閱讀：三個缺點的詳細說明與平均的變異數", r"""
  <p>假設 $n=100$。LOOCV 每次都是 99 筆訓練、1 筆驗證。例如 $D_{-1}=\{2,3,\ldots,100\}$ 與 $D_{-2}=\{1,3,\ldots,100\}$ 有 98 筆完全相同，訓練出來的兩個模型通常也非常像。講義列出三個後果：</p>
  <p><strong>1. 對資料的擾動不夠大</strong>。每次只移除一筆，$n\to n-1$，不同輪的訓練資料幾乎一樣；相比之下，10-fold CV 每次拿掉約 10%（$100\to90$），模型受到比較明顯的擾動。LOOCV 因此沒有充分觀察到「訓練樣本改變時，模型表現會怎麼變」。</p>
  <p><strong>2. 仍然很花時間。</strong>上面的捷徑只適用於最小平方這類線性平滑器。一般的機器學習方法沒有這種捷徑：$n=10000$ 時 LOOCV 要真的擬合 10000 次模型，10-fold CV 只要 10 次。對隨機森林、支持向量機、神經網路等方法，LOOCV 通常成本很高。</p>
  <p><strong>3. 各折的估計高度相關，平均之後的變異可能仍然很大。</strong>令第 $i$ 折的誤差為 $E_i$，$\mathrm{CV}=\frac1n\sum_iE_i$。若各 $E_i$ 獨立，平均的變異是 $\sigma^2/n$；但它們的訓練集幾乎相同，$\operatorname{Cov}(E_i,E_j)>0$。一般地</p>
  $$\operatorname{Var}\Bigl(\frac1n\sum_{i=1}^nE_i\Bigr)=\frac1{n^2}\Bigl[\sum_i\operatorname{Var}(E_i)+\sum_{i\ne j}\operatorname{Cov}(E_i,E_j)\Bigr].$$
  <p>各折高度正相關時，第二項很大，平均很多折也不像平均很多獨立觀測那樣有效降低變異。極端情況 $E_1=E_2=\cdots=E_n$，平均 100 次的資訊和只有 1 次差不多。所以這句話的意思<strong>不是</strong>「取平均會增加變異」，而是<strong>因為各折太相關，取平均無法像獨立樣本那樣降低變異</strong>。</p>
  <p>三點合起來看：LOOCV 偏差較低，但各折高度相關，變異可能較高，而且計算昂貴；5-fold 或 10-fold 通常提供較好的偏差、變異與計算量取捨。</p>
""")

SHUFFLE_SECTION = r"""
  <h4 id="w05-shuffle">為什麼分折前通常要先洗牌</h4>
  <p>一般的 $k$-fold CV 希望每一折都像是「從整體資料抽出的一小部分」。若原始資料有排序，不洗牌就切，各折的分布會不一樣，CV 估計就會偏掉。</p>
  <ul>
    <li><strong>依反應值排序</strong>：$y_1\le y_2\le\cdots\le y_n$ 直接切 5 折，第 1 折全是最小的一群、第 5 折全是最大的一群。驗證折與訓練資料的分布差很多，量到的除了泛化誤差，還混進了排序造成的分布偏移。</li>
    <li><strong>依類別排序</strong>：前 500 筆都是 0、後 500 筆都是 1，不洗牌的 5 折中，有些折幾乎全是類別 0，有些幾乎全是類別 1，顯然不合理。</li>
    <li><strong>課程的 Auto</strong>：資料大致依年份排列，所以 lab 的 <code>KFold</code> 加了 <code>shuffle=True</code>。</li>
  </ul>
  <p>洗牌的目的是讓<strong>每一折更接近整體資料的分布</strong>，各折之間比較公平，CV 估計也比較穩定。scikit-learn 的 <code>KFold</code> 預設<strong>不洗牌</strong>；<code>KFold(shuffle=True, random_state=0)</code> 是在分折前先洗一次，固定 <code>random_state</code> 可以讓不同模型用同一組分折比較。分類問題通常再用 <code>StratifiedKFold</code> 分層：整體是 90% 負類、10% 正類時，每一折也盡量維持接近 90／10。</p>
  <p>但<strong>不是所有 CV 都該洗牌</strong>。資料有自然結構時，亂洗反而可能造成資訊洩漏：</p>
  <ul>
    <li><strong>時間序列、縱向資料</strong>：不能洗牌後用 2023 年的資料訓練、再預測 2020 年，實務上這等於看到未來。改用只往前切的 <code>TimeSeriesSplit</code>。</li>
    <li><strong>群組資料</strong>：同一病人的重複量測、同一受試者的多張影像，應整組留在同一側，改用 <code>GroupKFold</code>。</li>
    <li><strong>空間資料</strong>：鄰近位置彼此相關，隨機切分會讓驗證點的鄰居出現在訓練集中。</li>
  </ul>
  <p>簡單記：<strong>i.i.d. 資料通常先洗牌</strong>；<strong>有時間、群組或空間結構時不能隨便洗牌</strong>。</p>

  <h4 id="w05-shufflesplit">KFold 與 ShuffleSplit：分割與重複抽樣</h4>
  <p>講義的選讀頁另外介紹可以精確控制驗證集大小的 <code>ShuffleSplit</code>。兩者的差別在於：<strong><code>KFold</code> 把資料切成互斥的 $k$ 份，每一筆資料恰好當一次驗證；<code>ShuffleSplit</code> 每次都重新隨機抽一組訓練／驗證，不同次的驗證集可以重疊。</strong>假設 100 筆資料：</p>
  <ul>
    <li><code>KFold(n_splits=5)</code>：先分成 $F_1,\ldots,F_5$，第 $j$ 次拿 $F_j$ 當驗證；各驗證折互不重疊，每筆剛好被驗證一次。</li>
    <li><code>ShuffleSplit(n_splits=5, test_size=0.2)</code>：做 5 次彼此獨立的隨機 80／20 切分。某筆資料可能多次進入驗證集，也可能一次都沒被抽到。它比較接近<strong>重複隨機切分</strong>，有時也稱為蒙地卡羅交叉驗證（Monte Carlo cross-validation）。</li>
  </ul>
""" + table(["", "<code>KFold</code>", "<code>ShuffleSplit</code>"],
            [["每次是否重新隨機抽", "否，先分成 k 折（可先洗牌一次）", "是"],
             ["驗證集是否重疊", "不重疊", "可以重疊"],
             ["每筆是否一定當驗證", "恰好一次", "不一定"],
             ["驗證集大小", "約 n/k", "自己指定 <code>test_size</code>"],
             ["切分次數", "k", "自己指定 <code>n_splits</code>"],
             ["分類、類別不平衡時", "<code>StratifiedKFold</code>", "<code>StratifiedShuffleSplit</code>"]]) + r"""
  <p>即使兩者都是「5 次、驗證 20%」，概念也不同：<strong>KFold 是分割（partition），ShuffleSplit 是重複隨機抽樣</strong>。<code>ShuffleSplit(n_splits=1)</code> 就是驗證集法；lab 用 10 次切分得到平均 23.80、標準差 1.42。lab 也提醒，因為各次的訓練樣本重疊而相關，這個標準差不能當作平均測試分數的抽樣變異，只反映換不同隨機切分時的蒙地卡羅變異。下面的元件把幾種切分畫在一起，資料依類別排序，方便看出洗牌與分層的效果。</p>
""" + "{SPLIT_VIZ}" + links(
    ("scikit-learn：不同交叉驗證切分的視覺化", "https://scikit-learn.org/stable/auto_examples/model_selection/plot_cv_indices.html"),
    ("scikit-learn：關於洗牌的說明", "https://scikit-learn.org/stable/modules/cross_validation.html#a-note-on-shuffling"),
    ("時間序列的交叉驗證討論", "https://stats.stackexchange.com/questions/326228/cross-validation-with-time-series"))

SPLIT_VIZ = viz(
    svg("w05splitSvg", 300),
    [rows_card("目前的切分",
               [("切分器", "KFold（不洗牌）", "w05splitName"),
                ("每次驗證筆數", "—", "w05splitSize"),
                ("從未被驗證的筆數", "—", "w05splitNever"),
                ("被驗證兩次以上", "—", "w05splitMulti"),
                ("各次驗證中類別 1 的比例", "—", "w05splitProp")]),
     info_card("怎麼看這張圖",
               '橫軸是 40 筆資料的索引，最上面一列是類別（前 24 筆類別 0、後 16 筆類別 1，依類別排好）。'
               '下面每一列是一次切分：<strong>深色＝驗證</strong>、淺色＝訓練。'
               '不洗牌的 KFold 會讓某幾折只含單一類別。')],
    "w05splitStatus", "切換切分器，觀察驗證集的位置、重疊與類別比例。",
    '<button class="btn btn-step" onclick="w05splitShow(0)">KFold 不洗牌</button>'
    '<button class="btn btn-step" onclick="w05splitShow(1)">KFold 洗牌</button>'
    '<button class="btn btn-step" onclick="w05splitShow(2)">StratifiedKFold</button>'
    '<button class="btn btn-step" onclick="w05splitShow(3)">ShuffleSplit</button>',
    provenance=("illustrative", "40 筆依類別排序的示意索引；在瀏覽器內以固定種子產生切分"))
SHUFFLE_SECTION = detail("w05-detail-shuffle", "〔選讀〕洗牌、KFold 與 ShuffleSplit", SHUFFLE_SECTION.replace("{SPLIT_VIZ}", SPLIT_VIZ))

MISUSE_VIZ = viz(
    chart("w05misChart", "", "。此圖的重點：在純雜訊資料上，先選特徵再做 CV 回報的錯誤率接近 0，正確流程則接近 0.5。"),
    [rows_card("100 次純雜訊模擬",
               [("錯誤流程的平均 CV 錯誤率", "—", "w05misWrong"),
                ("正確流程的平均 CV 錯誤率", "—", "w05misRight"),
                ("錯誤流程 10%–90% 百分位", "—", "w05misWrongRange"),
                ("正確流程 10%–90% 百分位", "—", "w05misRightRange")]),
     info_card("模擬怎麼做",
               '每次產生 50 筆、5000 個與類別完全無關的常態預測變數，類別隨機給 0／1。'
               '<strong>錯誤流程</strong>先用全部資料挑出和類別最相關的 100 個變數，再對 logistic regression 做 5-fold CV；'
               '<strong>正確流程</strong>在每一折的訓練部分內重新挑那 100 個變數。'
               '真實的錯誤率是 0.5，因為預測變數不含任何資訊。'),
     info_card("講義沒有規定的細節",
               '講義只給「5000 個預測變數、50 筆、挑 100 個」的流程。'
               '分類器的正則化、分折方式與重複次數是本頁的示意設定，重點是兩種流程的差距。')],
    "w05misStatus", "兩根長條是 100 次模擬的平均 CV 錯誤率。", "",
    provenance=("simulation", "依講義的 5000／50／100 流程，以純雜訊資料重複 100 次"))

BOOT_NAME = r"""
  <p>這個名字來自英文俗語「拉著自己的靴帶把自己提起來」：只靠手上這一份資料，就估出估計量的不確定性。</p>
""" + detail("w05-detail-boot-name", "延伸閱讀：bootstrap 名稱的由來", r"""
  <p>這句俗語常和吹牛男爵 Munchausen 的故事連在一起：他聲稱抓著自己的頭髮（後來的版本變成靴帶）把自己從沼澤裡拉出來。這件看似不可能的事，後來被用來形容「不靠外力、只用自己手上的東西完成」。統計上的 bootstrap 也是這樣：沒有新的資料，只從原本那一份資料重抽，就估出估計量的抽樣變異。</p>
""" + links(("bootstrap 這個名字的由來", "https://mentallyagile.com/blog/2022/5/23/bootstrap-absurdity")))

BOOT_SIM = r"""
  <h3 id="w05-boot-sim">先看理想情況：如果能從母體反覆抽樣</h3>
  <p>講義先用模擬說明 bootstrap 想近似的東西。假設知道母體參數 $\sigma_X^2=1$、$\sigma_Y^2=1.25$、$\sigma_{XY}=0.5$，代入公式得真正的 $\alpha=0.6$。每次從母體抽 100 對 $(X,Y)$、算一次 $\hat\alpha$，重複 1000 次。講義（ISLP 圖 5.9、5.10）的四個例子 $\hat\alpha$ 為 0.576、0.532、0.657、0.651；1000 次的平均是</p>
  $$\bar\alpha=\frac1{1000}\sum_{r=1}^{1000}\hat\alpha_r=0.5996,$$
  <p>很接近 $\alpha=0.6$；標準差</p>
  $$\sqrt{\frac1{1000-1}\sum_{r=1}^{1000}(\hat\alpha_r-\bar\alpha)^2}=0.083,$$
""" + info("講義的模擬結果", r"""1000 個 $\hat\alpha$ 的平均 0.5996 很接近真值 0.6；標準差 0.083，也就是 $\mathrm{SE}(\hat\alpha)\approx0.083$：$\hat\alpha$ 和 $\alpha$ 的差距大約在 0.08 這個量級。""", "warm") + r"""
  <p><strong>問題是真實世界只有一份資料，無法從母體反覆抽樣。</strong>bootstrap 改從手上的資料有放回地重抽，模仿這個過程。下圖左邊是從母體重抽的 $\hat\alpha$，右邊是只從一份資料做 bootstrap 的 $\hat\alpha^*$。書上圖 5.10 的 bootstrap 直方圖來自一份從同一母體模擬的資料，這裡改用課程 lab 的 <code>Portfolio</code>；兩者的中心不同（一個在真值 0.6 附近，一個在這份資料的 $\hat\alpha$ 附近），但<strong>散布寬度相近</strong>，而 bootstrap 要估的正是這個寬度。</p>
""" + "{SIM_VIZ}"

BOOT_WORLD = r"""
  <h3 id="w05-boot-world">bootstrap 的一般圖像：真實世界與 bootstrap 世界</h3>
  <p>講義用兩個平行的世界整理這個想法：</p>
""" + table(["", "真實世界", "bootstrap 世界"],
            [["母體", "未知的分布 $P$", "手上的資料 $Z$（每筆機率 $1/n$ 的經驗分布）"],
             ["抽一份資料", "從 $P$ 抽 $n$ 筆", "從 $Z$ <strong>有放回</strong>抽 $n$ 筆，得到 $Z^{*r}$"],
             ["算估計量", "$\\hat\\alpha$", "$\\hat\\alpha^{*r}$"],
             ["重複", "理論上重複很多次（做不到）", "$r=1,\\ldots,B$，電腦可以做"]]) + r"""
  <p>只有 3 筆資料的例子最容易看清楚：原資料是觀測 1、2、3；一份 bootstrap 樣本可能是 3、1、3，第 3 筆出現兩次、第 2 筆沒出現。重複 $B$ 次得到 $\hat\alpha^{*1},\ldots,\hat\alpha^{*B}$。</p>
""" + info("講義：bootstrap 標準誤", r"""以 $B$ 份 bootstrap 樣本 $Z^{*1},\ldots,Z^{*B}$ 算出 $\hat\alpha^{*1},\ldots,\hat\alpha^{*B}$，它們的標準差就是 $\hat\alpha$ 標準誤的估計：
  $$\mathrm{SE}_B(\hat\alpha)=\sqrt{\frac1{B-1}\sum_{r=1}^B\Bigl(\hat\alpha^{*r}-\frac1B\sum_{r'=1}^B\hat\alpha^{*r'}\Bigr)^2}.$$""", "warm") + r"""
  <p>ISLP 用 $B=1000$ 得到 $\mathrm{SE}_B(\hat\alpha)=0.087$，和上面理想模擬的 0.083 很接近；課程 lab 用自己的種子得到 0.0912。</p>
"""

SIM_VIZ = viz(
    chart("w05simChart", "tall", "。此圖的重點：從母體重抽與 bootstrap 重抽的直方圖寬度相近。"),
    [rows_card("兩種重抽的摘要",
               [("真實 α", "0.6", "w05simTrue"),
                ("母體模擬：平均", "—", "w05simMean"),
                ("母體模擬：標準差", "—", "w05simSD"),
                ("bootstrap：平均", "—", "w05simBMean"),
                ("bootstrap：標準差", "—", "w05simBSD")]),
     info_card("怎麼看這張圖",
               '兩組長條共用同一組區間。綠色是 1000 份新模擬資料的 α̂，藍色是 Portfolio 一份資料的 1000 個 bootstrap α̂*。'
               '本頁的模擬用了新的亂數種子，平均與標準差會接近、但不會和講義的 0.5996、0.083 逐位相同。'
               '書上圖 5.10 的 bootstrap 欄用的是一份模擬資料，這裡改用 Portfolio。')],
    "w05simStatus", "左右兩種重抽的分布寬度相近。", "",
    provenance=("simulation", "母體參數依講義；bootstrap 欄使用 ISLP Portfolio"))
BOOT_SIM = BOOT_SIM.replace("{SIM_VIZ}", SIM_VIZ)

BOOT_CI = r"""
  <h3 id="w05-boot-ci">bootstrap 信賴區間</h3>
  <p><strong>百分位區間。</strong>把 $B$ 個 $\hat\alpha^{*r}$ 排序，取第 5 與第 95 百分位數，就得到近似 90% 的信賴區間。講義的例子是 $(0.43,\,0.72)$。這叫 bootstrap 百分位信賴區間（percentile interval），是最簡單的一種；估計量偏差大、樣本太少或統計量不規則時，涵蓋率可能不足。</p>
  <p><strong>迴歸曲線的信賴區間。</strong>講義用局部迴歸（lowess）曲線示範，步驟是：</p>
  <ol>
    <li>從 $n$ 筆 $(x_i,y_i)$ 有放回地抽 $n$ 筆，成為一份 bootstrap 樣本。</li>
    <li>在這份樣本上重新擬合曲線。</li>
    <li>在一組固定的 $x$ 網格上記錄擬合值。</li>
    <li>重複步驟 1–3 共 $B$ 次。</li>
    <li>在每個 $x$ 取這 $B$ 個擬合值的第 2.5 與第 97.5 百分位，連起來就是逐點的 95% 帶。</li>
  </ol>
  <p>這是<strong>逐點</strong>區間：每個 $x$ 各自有 95% 的近似涵蓋，不代表整條曲線同時落在帶內的機率是 95%。它描述平均曲線的不確定性，不包含新觀測本身的雜訊，所以不是預測區間。</p>
""" + links(("statsmodels 的 lowess 範例（含 bootstrap 信賴區間帶）", "https://www.statsmodels.org/stable/examples/notebooks/generated/lowess.html")) + r"""
  <h3 id="w05-boot-block">資料不獨立時：區塊 bootstrap</h3>
  <p>bootstrap 每次抽一筆觀測，隱含假設觀測彼此獨立。時間序列的相鄰觀測相關，講義的做法是改成有放回地抽<strong>連續的區塊</strong>，以保留區塊內的相關結構。</p>
""" + detail("w05-detail-block-bootstrap", "延伸閱讀：區塊 bootstrap 怎麼做？", r"""
  <p><strong>為什麼逐筆重抽不行。</strong>逐筆有放回重抽會把相鄰觀測打散，重抽出來的序列沒有原本的自我相關；用它估出的標準誤通常偏小，因為正相關的資料提供的獨立資訊比筆數看起來少。</p>
  <p><strong>步驟</strong>（以長度 $n$ 的序列、區塊長度 $l$ 為例）：</p>
  <ol>
    <li>把序列切成區塊。不重疊的做法得到 $n/l$ 個區塊；移動區塊（moving block）則取所有連續的 $l$ 筆，共 $n-l+1$ 個，可以重疊。</li>
    <li>從這些區塊中有放回地抽出 $n/l$ 個（這裡假設 $n$ 是 $l$ 的倍數；不整除時抽 $\lceil n/l\rceil$ 個，串接後只取前 $n$ 筆）。</li>
    <li>依抽出的順序把區塊串接起來，得到一條長度 $n$ 的 bootstrap 序列。</li>
    <li>在這條序列上重算估計量；重複 $B$ 次，用這些估計值的標準差估標準誤。</li>
  </ol>
  <p><strong>區塊長度的取捨。</strong>區塊要長到足以保留主要的相關（相關持續幾期，區塊大致就要涵蓋那麼長）；但區塊太長，能組合的方式變少，bootstrap 樣本彼此太像，估計反而不穩。循環區塊（把序列頭尾接起來再切）可以讓每筆觀測被抽到的機會相同。這些變形都只保留一部分相依結構，使用時要說明所選的版本與區塊長度。</p>
""" + links(("如何對時間序列做 bootstrap", "https://stats.stackexchange.com/questions/25706/how-do-you-do-bootstrapping-with-time-series-data"),
            ("區塊 bootstrap 的應用文獻", "https://www.sciencedirect.com/science/article/pii/S0003267000008503")))

TWO_THIRDS_D = detail("w05-detail-two-thirds", "推導：為什麼每份 bootstrap 樣本約含三分之二的觀測", r"""
  <p><strong>第一步：某筆在一次抽籤中沒被抽到。</strong>從 $n$ 筆中有放回抽一次，抽到第 $j$ 筆的機率是 $1/n$，沒抽到的機率是 $1-1/n$。</p>
  <p><strong>第二步：$n$ 次都沒被抽到。</strong>各次抽籤獨立，所以第 $j$ 筆完全不在 bootstrap 樣本裡的機率是 $(1-1/n)^n$。</p>
  <p><strong>第三步：取極限。</strong>由 $\lim_{n\to\infty}(1-1/n)^n=e^{-1}\approx0.368$，第 $j$ 筆<strong>至少出現一次</strong>的機率趨近 $1-e^{-1}\approx0.632$。</p>
  <p><strong>第四步：期望的不同觀測數。</strong>令 $I_j$ 表示第 $j$ 筆是否至少出現一次，則一份 bootstrap 樣本中不同觀測的個數是 $\sum_jI_j$，期望為 $n\{1-(1-1/n)^n\}\approx0.632n$，大約三分之二。各 $I_j$ 不獨立也不影響這個期望；每一份樣本的實際比例會在 0.632 附近起伏。</p>
""" + links(("為什麼每份 bootstrap 樣本平均約含三分之二的觀測", "https://stats.stackexchange.com/questions/88980/why-on-average-does-each-bootstrap-sample-contain-roughly-two-thirds-of-observat")))

TRAIN_TEST_D = detail("w05-detail-train-test-mse", "推導：為什麼訓練 MSE 的期望小於測試 MSE？", r"""
  <p>以最小平方線性迴歸為例：$y=X\beta+\varepsilon$，$X$ 為 $n\times p$ 滿欄秩（含截距），誤差獨立、平均 0、變異數 $\sigma^2$。</p>
  <p><strong>訓練 MSE。</strong>殘差 $e=(I-H)y=(I-H)\varepsilon$，$H=X(X^\mathsf{T}X)^{-1}X^\mathsf{T}$。$I-H$ 對稱且冪等，跡為 $n-p$，所以</p>
  $$E\Bigl[\frac1n\|e\|^2\Bigr]=\frac1n E\bigl[\varepsilon^\mathsf{T}(I-H)\varepsilon\bigr]=\frac{\sigma^2}{n}\operatorname{tr}(I-H)=\sigma^2\Bigl(1-\frac pn\Bigr).$$
  <p><strong>在同樣的 $X$ 上重新觀測的測試 MSE。</strong>新反應 $y^{new}=X\beta+\varepsilon^{new}$，$\varepsilon^{new}$ 與訓練誤差獨立。預測誤差 $y^{new}-X\hat\beta=\varepsilon^{new}-H\varepsilon$，兩項獨立，</p>
  $$E\Bigl[\frac1n\|y^{new}-X\hat\beta\|^2\Bigr]=\sigma^2+\frac{\sigma^2}{n}\operatorname{tr}(H)=\sigma^2\Bigl(1+\frac pn\Bigr).$$
  <p>兩者相差 $2p\sigma^2/n$：參數愈多、樣本愈少，訓練誤差就愈樂觀。這正是第 6 章 $C_p$ 在訓練誤差上加 $2p\hat\sigma^2/n$ 的由來。更一般的結論（模型類事先固定、取訓練誤差最小者時，期望訓練誤差不大於期望測試誤差）見第 2 章的<a href="statistical_learning.html#w02proofRisk">證明</a>。</p>
""" + links(("證明訓練資料上的期望 MSE 小於測試資料", "https://stats.stackexchange.com/questions/310687/prove-that-the-expected-mse-is-smaller-in-training-than-in-test")))

BOOT_APPENDIX_LINKS = links(
    ("bootstrap 預測區間的討論", "https://stats.stackexchange.com/questions/226565/bootstrap-prediction-interval"),
    ("MAPIE：以重抽樣與保形方法建立預測區間的套件", "https://mapie.readthedocs.io/en/latest/index.html"),
    ("置換檢定", "https://en.wikipedia.org/wiki/Permutation_test"),
    ("Jackknife 重抽樣", "https://en.wikipedia.org/wiki/Jackknife_resampling"),
    ("Jackknife 與 bootstrap 的比較", "https://stats.stackexchange.com/questions/249333/comparison-of-the-jacknife-vs-the-bootstrap"),
    ("scikit-learn：用置換檢定評估分類分數的顯著性", "https://scikit-learn.org/stable/auto_examples/feature_selection/plot_permutation_test_for_classification.html#test-with-permutations-the-significance-of-a-classification-score"),
    lead="講義附錄的補充連結")

SPLITTERS_CODE = """import numpy as np
from sklearn.model_selection import (
    StratifiedKFold, GroupKFold, StratifiedGroupKFold
)

# 12 位病人，每人 5 筆觀測；6 位為負例、6 位為正例。
groups = np.repeat(np.arange(12), 5)
y = np.repeat([0] * 6 + [1] * 6, 5)
X = np.arange(60).reshape(-1, 1)

splitters = {
    "分層": StratifiedKFold(
        n_splits=3, shuffle=True, random_state=42),
    "分組": GroupKFold(n_splits=3),
    "分層且分組": StratifiedGroupKFold(n_splits=3),
}
for name, cv in splitters.items():
    folds = (cv.split(X, y) if name == "分層"
             else cv.split(X, y, groups=groups))
    for fold, (train, valid) in enumerate(folds, 1):
        shared = np.intersect1d(groups[train], groups[valid])
        print(name, fold, "驗證正例比例", y[valid].mean(),
              "兩側共用病人數", len(shared))
"""

SPLITTERS_D = detail("w05-detail-splitters", "延伸閱讀：StratifiedKFold、GroupKFold 與分類指標", r"""
  <p>承接講義的「分類問題的交叉驗證」與選讀的切分方式：Lab 匯入了 <code>StratifiedKFold</code>，但主要實作仍是 <code>Auto</code> 迴歸的 <code>KFold</code>。下面用小型分類資料展開分層與群組切分；病人編號是為了看清切分界線而設計的例子，不是 Auto 的欄位。</p>
  <h3>先問：你要預測的是新觀測，還是新病人？</h3>
  <p><strong>StratifiedKFold（分層）</strong>依照 <code>y</code> 的類別安排觀測，讓各折的類別比例<strong>盡量接近</strong>整體。例如 100 筆獨立觀測有 20 筆正例，分成 5 折時，每折 20 筆約有 4 筆正例。一般分類也可以用分層，不必等到嚴重不平衡才使用；它沒有增加少數類資料，也不會解決所有抽樣不確定性。</p>
  <p>若正例只有 3 筆卻切成 5 折，就不可能每折都有正例。折數與評估指標要配合各類的筆數；ROC AUC 等指標在只有單一類別的驗證折上無法計算。分層可避免部分不良切分，但不能保證折分數的變異完整反映母體的不確定性。</p>
  <p><strong>GroupKFold（分組）</strong>依照 <code>groups</code> 的群組編號安排<strong>整組</strong>觀測。同一病人的 5 次就診，應一起放在訓練或驗證的一側；每一折的兩側沒有共用病人，各群組在一輪 CV 中恰好當一次驗證資料。若逐筆隨機分折，模型可能在驗證時認出訓練過的病人；這樣的分數回答的是「熟悉病人的新紀錄」，不適合用來宣稱「新病人的表現」。至少要有 <code>n_splits</code> 個不同群組；群組大小不同時，驗證筆數也可能不一樣。</p>
  <p><strong>分層與分組保護的是不同界線。</strong>分層不保證病人隔離；分組不保證類別比例相同。若兩者都需要，用 <code>StratifiedGroupKFold</code>：先確保群組不跨兩側，再嘗試維持類別比例。若正例都集中在少數大群組，比例可能無法平衡，仍應列出各折的群組數與各類筆數。</p>
""" + table(["資料情境", "切分器", "切分時保留什麼"], [
    ["獨立的迴歸觀測", "<code>KFold(shuffle=True)</code>", "讓觀測分散到各折"],
    ["獨立的分類觀測", "<code>StratifiedKFold</code>", "各折類別比例盡量接近整體"],
    ["同一病人／使用者有多筆紀錄", "<code>GroupKFold</code>", "同群組不跨訓練與驗證"],
    ["分類且同一實體有多筆紀錄", "<code>StratifiedGroupKFold</code>", "群組隔離，並盡量維持類別比例"],
    ["預測未來的時間序列", "<code>TimeSeriesSplit</code>", "用較早資料預測較晚資料；必要時留間隔"],
]) + r"""
  <h3>sklearn：直接檢查每折到底切了什麼</h3>
  <p>下面的 <code>X</code> 只是用來示範索引，不拿來擬合模型。請比較各折的「驗證正例比例」與「兩側共用病人數」：分層可以維持比例，卻可能讓同一病人出現在兩側；分組版本的共用病人數應為 0。把 <code>y</code> 改成正例集中於少數病人，再觀察各折比例。</p>
""" + hl(SPLITTERS_CODE, block_id="w05-splitters-code") + r"""
  <p>真正評估模型時，例如 <code>cross_val_score(model, X, y, cv=GroupKFold(3), groups=groups)</code>，也要傳入群組。這是 sklearn 預設未啟用 metadata routing 的寫法；若已啟用，請依官方文件用 <code>params={"groups": groups}</code> 傳遞。</p>
  <p><strong>切分器與指標要分別選。</strong>正例只佔 1% 時，全猜負例也有 99% accuracy；可依問題選 recall、precision、F1 或 ROC AUC，透過 <code>scoring</code> 指定。分層不會讓 accuracy 自動成為合適的指標，分組也不能取代時間順序限制。</p>
""" + links(
    ("scikit-learn：交叉驗證與資料相依性", "https://scikit-learn.org/stable/modules/cross_validation.html"),
    ("StratifiedKFold：分層切分", "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html"),
    ("GroupKFold：群組隔離", "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html"),
    ("StratifiedGroupKFold：同時考慮類別與群組", "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html")))

NESTED_CODE = """from ISLP import load_data
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import (
    KFold, GridSearchCV, cross_val_score, cross_validate
)

# 沿用 Ch05 Lab：以 horsepower 預測 Auto 的 mpg。
Auto = load_data("Auto")
X = Auto[["horsepower"]].to_numpy()
y = Auto["mpg"].to_numpy()
model = make_pipeline(PolynomialFeatures(degree=2, include_bias=False),
                      LinearRegression())

# 對齊 Lab 的 10-fold 切法，評估事先固定的二次模型。
cv = KFold(10, shuffle=True, random_state=0)
fixed_scores = cross_val_score(
    model, X, y, cv=cv, scoring="neg_mean_squared_error")
print("固定二次模型 CV MSE", -fixed_scores.mean())

# 延伸：自動比較 Lab 的 1 到 5 次多項式。
inner = KFold(3, shuffle=True, random_state=1)
outer = KFold(5, shuffle=True, random_state=2)
search = GridSearchCV(
    model, {"polynomialfeatures__degree": [1, 2, 3, 4, 5]},
    cv=inner, scoring="neg_mean_squared_error", refit=True)
search.fit(X, y)
print("完整資料的最佳次數", search.best_params_)
print("用來選次數的 CV MSE", -search.best_score_)

# Nested CV：每次只用 outer 訓練部分執行完整搜尋。
result = cross_validate(search, X, y, cv=outer,
                        scoring="neg_mean_squared_error",
                        return_estimator=True)
print("Nested CV 外層 MSE", -result["test_score"])
print("Nested CV 外層平均 MSE", -result["test_score"].mean())
print("各 outer fold 選的次數",
      [est.best_params_ for est in result["estimator"]])

# 評估完成後，在全部可用訓練資料重新搜尋並 refit。
# 若另有 external test set，X、y 在此只包含 training data。
search.fit(X, y)
final_model = search.best_estimator_
"""

NESTED_GUIDE = r"""
  <p>承接講義「Cross-validation: right and wrong」的原則：資料驅動的選擇必須放在適當的訓練折內。Lab 用 <code>Auto</code> 的 <code>horsepower</code> 預測 <code>mpg</code>，比較 1 到 5 次多項式的 CV 誤差；以下沿用同一資料與候選模型，延伸到自動選次數與獨立的外層評估。Nested CV 是這裡的延伸實作，並非原 Lab 已執行的步驟。</p>
  <h4>一般 CV 與 Nested CV：評估的對象不同</h4>
  <p><strong>一般 CV 有兩種用途。</strong>超參數事先固定時，它可評估這個訓練程序；搭配 <code>GridSearchCV</code> 等搜尋時，它可比較設定並選超參數。若同一份 CV 分數既用來選冠軍，又用來報告冠軍的表現，就可能偏樂觀：例如很多候選設定的真實表現接近，但估計有起伏，挑最高分等於偏向挑中在這次切分中運氣好的設定。</p>
  <p><strong>Nested CV 評估包含選擇步驟的完整程序。</strong>它問的是：「收到一批新的訓練資料後，依照這套調參規則選模型，對未見資料的預測會多準？」因此每個外層折都要重新執行內層搜尋，不是先用全部資料選好設定，再做一次外層 CV。</p>
""" + table(["比較項目", "一般 CV（單層）", "Nested CV（巢狀）"], [
    ["主要目的", "評估固定訓練程序；或搭配搜尋選超參數", "評估包含超參數選擇的完整訓練程序"],
    ["CV 結構", "單層", "雙層：Inner 選擇、Outer 評估"],
    ["超參數選擇", "有搜尋時，依此層 CV 選擇；固定模型則不選", "只用各 Outer 訓練部分的 Inner CV 選擇"],
    ["效能評估", "固定模型可用 CV score；搜尋後的最佳 CV score 可能偏樂觀", "使用未參與該折選擇的 Outer CV score"],
    ["是否產生單一最佳超參數", "單次搜尋會選一組；單純 CV 不會", "評估時各 Outer Fold 各自選，結果可能相同或不同"],
    ["Selection bias（選擇偏差）", "同一 CV 同時調參與報告效能時，可能偏樂觀", "可降低調參造成的偏差；不是消除所有偏差的保證"],
    ["是否重新選擇最終超參數", "若已在全部可用訓練資料搜尋，通常不用再選；資料或流程改變則需重選", "一般會在全部可用訓練資料重新執行搜尋；不以 Outer 成績挑設定"],
    ["是否重新訓練最終模型", "通常要用全部可用訓練資料擬合；搜尋器可自動 refit", "要：最後的搜尋選好設定後，在全部可用訓練資料擬合"],
    ["計算成本", "較低；搜尋仍需對每個設定逐折擬合", "較高；每個 Outer Fold 都完整做一次 Inner 搜尋"],
    ["適用情境", "固定模型的評估；或保留獨立測試集後，在訓練資料選設定", "需要評估包含調參步驟的泛化表現，尤其沒有獨立測試集時"],
    ["有獨立 External Test Set 時", "訓練集內調參後，未碰過的測試集可作最終評估", "並非必要；可另外提供完整選模程序的內部評估"],
]) + r"""
  <h4>5 個外層折、3 個內層折：一輪怎麼做？</h4>
  <ol>
    <li><strong>外層留下 1/5。</strong>這份資料只供本輪評估；其餘 4/5 是外層訓練資料。</li>
    <li><strong>在這 4/5 裡做 3-fold Inner CV。</strong>例如比較 Lab 的多項式次數 1、2、3、4、5。補值、標準化、特徵選擇等會學到資料資訊的步驟，都只在每個內層訓練折擬合。</li>
    <li><strong>選出本輪設定後，重新擬合全部 4/5。</strong>再對最初留下的 1/5 計算一次分數。</li>
    <li><strong>換下一個外層折，從搜尋開始重做。</strong>最後整理 5 個 Outer 分數；各折選不同多項式次數是正常的。不要挑最高分的外層模型作為最終模型，也不要把外層最佳設定投票當作預設調參規則。</li>
  </ol>
  <p>5 個候選次數、3 個 Inner Fold、5 個 Outer Fold，內層搜尋共擬合 $5\times3\times5=75$ 次；各外層搜尋的 refit 再加 5 次。評估後的最終搜尋另需 $5\times3+1=16$ 次，合計 96 次。這說明巢狀 CV 的成本；不包括下面另外示範的一般 CV 與單次搜尋。</p>
  <h4>sklearn：把搜尋器交給外層 CV</h4>
  <p><code>cross_val_score</code> 搭配固定模型是一般 CV；<code>GridSearchCV</code> 用內層折選設定；把這個搜尋器傳給 <code>cross_validate</code>，就讓外層每一折重新搜尋。<code>refit=True</code> 會把選好的設定重新擬合到該次 <code>fit</code> 收到的全部訓練資料，<code>return_estimator=True</code> 則方便查看每個外層折的選擇。</p>
""" + hl(NESTED_CODE, block_id="w05-nested-code") + r"""
  <p><strong>分數方向與 Lab 對齊。</strong>Lab 以 MSE 比較模型，愈小愈好；sklearn 的搜尋器則一律最大化 score，所以此處用 <code>neg_mean_squared_error</code>，印出時乘上 −1 還原成 MSE。原 Lab 的 <code>sklearn_sm</code> 可直接回傳 MSE；不要把這兩種介面的正負號混用。固定二次模型沿用 Lab 的 10-fold、<code>random_state=0</code>；Nested 範例為縮短搜尋改用外層 5 折、內層 3 折，分數不應要求與 Lab 的 10-fold 完全相同。</p>
  <p><strong>評估完之後才訓練交付模型。</strong>上面的最後兩行會在全部可用訓練資料重新選設定並擬合。Nested CV 的平均分數描述這套程序在外層訓練規模下的表現，不是最終這個已擬合模型的獨立測試分數。若另有外部測試集，必須一直保留到所有決策完成，再評估一次；反覆看它並改模型，就失去獨立性。</p>
  <p><strong>Nested CV 仍要選對切分方式。</strong>上例沿用 Lab 將 Auto 各列視為獨立迴歸觀測的設定，所以內外層都用 KFold；若是獨立的分類觀測，可改成 StratifiedKFold。群組資料則兩層都要隔離群組，Inner 只收到當輪 Outer 訓練資料的群組編號。時間資料也要兩層遵守時間順序。巢狀結構本身不會修復病人重疊、時間洩漏或外層結果被反覆拿來挑模型的問題。</p>
""" + links(
    ("scikit-learn：一般 CV 與 Pipeline", "https://scikit-learn.org/stable/modules/cross_validation.html"),
    ("Nested versus non-nested cross-validation：官方範例", "https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html"),
    ("GridSearchCV：best_params_、best_score_ 與 refit", "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html"))

# ══════════════════════════════════════════════════════════════════════
BODIES = {}

# ── P00 prologue ──────────────────────────────────────────────────────
BODIES["prologue"] = f"""
  <p>你已經會擬合模型了。現在的問題換成：<strong>這個模型在沒見過的資料上會有多準？</strong>
  最直覺的做法是拿訓練資料算誤差，但那個數字幾乎一定太樂觀，因為模型是照著那批資料調出來的。
  極端一點想：一棵長到每個葉子只剩一個樣本的樹，訓練誤差是 0，可是它什麼都沒學到。</p>

  <p>如果手上有一大筆獨立的測試資料，事情很簡單。但真實情況通常是資料就這麼多，
  再切出去一塊當測試集就不夠訓練了。<strong>重抽樣</strong>（resampling）的想法是：
  反覆從同一批資料裡切出訓練／驗證組合，用它們的平均表現估計測試誤差。</p>
{HYPER_SECTION}

  <h3 id="w05-train-test">訓練誤差與測試誤差</h3>
  <p>講義先複習兩個定義。<strong>測試誤差</strong>是用學好的方法去預測一筆<strong>沒參與訓練</strong>的新觀測時的平均誤差；<strong>訓練誤差</strong>則把方法套回訓練用的那些觀測就能算出來，通常會低估測試誤差。</p>
{TRAIN_TEST_D}
  <p>最好的解法是一個夠大的獨立測試集，但通常拿不到。講義列出兩條替代路線：</p>
  <ol>
    <li><strong>用數學修正訓練誤差</strong>：例如 $C_p$、AIC、BIC，在訓練誤差上加一個隨模型複雜度增加的懲罰。第 6 章<a href="model_selection.html#criteria">模型選擇準則</a>會詳細介紹。</li>
    <li><strong>保留一部分訓練觀測不參與擬合</strong>，再把方法套到這些被保留的觀測上估計測試誤差。本章的驗證集法與交叉驗證都屬於這一類。</li>
  </ol>
{links(("scikit-learn：交叉驗證總覽", "https://scikit-learn.org/stable/modules/cross_validation.html"))}

{info("本章你會學到的三件事", '''<strong>1. 驗證集法（validation set）：</strong>切兩半，最簡單，但答案會隨切法跳動。<br>
  <strong>2. 交叉驗證（cross-validation）：</strong>LOOCV 與 <em>k</em>-fold，讓每個樣本都輪到當一次測試資料。<br>
  <strong>3. Bootstrap：</strong>有放回地重抽，不靠公式就能算出任何估計量的標準誤。''')}

{table(["", "切幾次", "每次訓練用多少", "有隨機性嗎", "主要用途"],
       [["驗證集法", "1", "約 n/2", "有，換 seed 就變", "快速粗估"],
        ["LOOCV", "n", "n − 1", "沒有（分割唯一）", "小資料、要穩定"],
        ["<em>k</em>-fold CV", "k（通常 5 或 10）", "n(k−1)/k", "有，但比驗證集小很多", "選模型的標準做法"],
        ["Bootstrap", "B（通常 1000）", "n（有放回）", "有，B 大就穩", "估標準誤與信賴區間"]])}

{quiz("qWhy", "QUIZ · 為什麼不能用訓練誤差",
      "為什麼「訓練誤差」不能拿來當測試誤差的估計？",
      [(True, "模型的參數是照著這批資料挑出來的，誤差已經被最小化過，所以會系統性偏低",
        "對。訓練誤差是「已經被最佳化過的目標值」，它衡量的是擬合程度，不是預測能力。模型愈有彈性，這個偏差愈大。"),
       (False, "訓練資料的樣本數太少，誤差的變異太大",
        "不對。樣本少會增加誤差估計的變異；訓練誤差還有<strong>系統性偏低</strong>的偏差。增加訓練資料後，用擬合資料自評造成的偏差仍然存在。"),
       (False, "訓練誤差用的是 MSE，測試誤差用的是別的指標，兩者不能比",
        "不對。兩邊可以用完全相同的指標；差別在於<strong>算誤差的資料有沒有參與過擬合</strong>，不在於指標。")])}
"""

# ── P01 validation ────────────────────────────────────────────────────
_val_code = lab_code(CH, 16) + "\n\n" + lab_code(CH, 20)
_val_out = lab_output(CH, 20)

BODIES["validation"] = f"""
  <p>最直接的做法：把資料隨機切成兩半，一半訓練、一半當<strong>驗證集</strong>（validation set，
  也叫 hold-out set）。模型完全沒看過驗證集，所以驗證集上的 MSE 就是一個誠實的測試誤差估計：</p>

  $$\\mathrm{{MSE}}_{{\\text{{valid}}}} = \\frac{{1}}{{|V|}} \\sum_{{i \\in V}} \\left(y_i - \\hat f(x_i)\\right)^2$$

  <p>講義用 <code>Auto</code> 資料（n = 392）示範：把 196 筆拿去訓練、196 筆當驗證集，
  用 <code>horsepower</code> 預測 <code>mpg</code>，比較線性、二次與更高次多項式 $\\texttt{{mpg}}=\\beta_0+\\sum_{{j=1}}^d\\beta_j\\,\\texttt{{horsepower}}^j$。單一次切分得到的驗證 MSE 曲線顯示二次明顯比線性好、三次以上沒有再改善。看起來很乾淨——問題是<strong>換一個切法，答案就變了</strong>。</p>
{links(("ISLP 的 Auto 資料說明", "https://islp.readthedocs.io/en/latest/datasets/Auto.html"))}

{viz(chart("w05valChart", "tall", "。此圖的重點：十種不同的隨機切分，畫出來是十條差很多的曲線——驗證集法的答案取決於你剛好怎麼切。"),
     [info_card("怎麼看這張圖",
                '每條淡線是一次隨機切分（<code>test_size=196</code>）算出的驗證 MSE，'
                'x 軸是 <code>horsepower</code> 多項式的次數。粗線是十次的平均。'
                '<strong>十條線的高低差距，就是驗證集法的變異。</strong>', "圖 5.2 右"),
      rows_card("十次切分的落點（degree 2）",
                [("最低", "—", "w05valLo"), ("最高", "—", "w05valHi"),
                 ("全距", "—", "w05valRange"), ("平均", "—", "w05valMean")]),
      info_card("結論",
                '每一條都會告訴你「二次比一次好」。這個結論很穩。但如果你想引用一個'
                '<strong>具體數字</strong>當測試 MSE，那個數字非常不可靠。')],
     "w05valStatus", "十條淡線是十種固定切分，粗線是平均。", "",
     provenance=("course-data", "ISLP Auto；固定 random_state=0..9，對照圖 5.2"))}

  <h3 id="dx-val">講義完整實作：切一半、擬合模型、算驗證 MSE</h3>
{card("講義 05 · 驗證集法（Auto，degree 1）", _val_code, _val_out,
      src=src("16、20"),
      note="這個 <strong>25.57</strong> 就是課本 §5.1.1 引用的數字。注意 <code>random_state=rng</code>"
           "——換掉它，下面的數字就會不一樣。")}

{card("講義 05 · 換一個切法（random_state=3）", lab_code(CH, 28), lab_output(CH, 28),
      src=src("26、28"),
      note="degree 1／2／3 的驗證 MSE 從 <code>[25.57, 22.22, 22.67]</code> 變成 "
           "<code>[20.76, 16.95, 16.97]</code>。<strong>同一份資料、同一個模型，只是切法不同，"
           "數字差了快 5。</strong>但兩次都指向同一個結論：二次比一次好，三次沒有再更好。")}

{info("講義：驗證集法的兩個缺點", '''<strong>1. 估計的變異很大</strong>：測試誤差的估計取決於哪些觀測剛好被分到訓練集、哪些分到驗證集，上圖十條曲線就是例子。<br>
  <strong>2. 容易高估測試誤差</strong>：只有一半的觀測用來訓練；訓練資料較少時模型通常較差，所以驗證誤差傾向高估「用全部資料訓練的模型」的測試誤差。''', "warm")}

{qa("觀念釐清", [
    ("Q：驗證集法為什麼會「高估」測試誤差？",
     "<p>因為它只用了一半的資料訓練。統計模型通常有愈多訓練資料，表現愈好，"
     "所以用 n/2 筆訓練出來的模型，本來就比用全部 n 筆訓練出來的差。"
     "你量到的是「一個比較弱的模型」的誤差，因此系統性偏高。</p>"
     "<p>這是驗證集法的兩個缺點之一。另一個是變異太大（就是上面那張圖）。"
     "交叉驗證同時改善了這兩點：每一輪都用 n(k−1)/k 筆訓練（比 n/2 多），"
     "而且做 k 輪再平均（變異變小）。</p>"),
    ("Q：那 <code>random_state</code> 到底該不該固定？",
     "<p>固定 seed 讓你和讀程式的人能重跑出同樣的數字，使結果<strong>可重現</strong>。</p>"
     "<p>危險的做法是「試幾個 seed，挑數字最漂亮的那個報出來」。那等於用驗證集調參，"
     "報出的誤差會受到這次選擇影響。可以用 k-fold CV 降低單次分割對結果的影響。</p>"),
])}

{quiz("qVal", "QUIZ · 驗證集法",
      "驗證集法有兩個公認的缺點。下面哪一組說對了？",
      [(True, "① 估計值變異大（換切法就變）② 只用一半資料訓練，所以高估測試誤差",
        "對。ISLP §5.1.1 講的就是這兩點，而 k-fold CV 兩點都改善了。"),
       (False, "① 計算量太大 ② 只能用在迴歸，不能用在分類",
        "都不對。驗證集法是這幾種方法裡<strong>計算量最小</strong>的（只擬合一次模型）；而它把 MSE 換成錯誤率就能用在分類。"),
       (False, "① 會用到測試資料的資訊 ② 需要假設誤差是常態分佈",
        "都不對。驗證集完全沒參與擬合，所以沒有洩漏；而且整套做法不需要任何分佈假設。這正是重抽樣方法的優點。")])}
"""

# ── P02 LOOCV ─────────────────────────────────────────────────────────
BODIES["loocv"] = f"""
  <p>驗證集法浪費了一半的資料，而且答案會跳。把它推到極端：
  <strong>每次只留一個樣本當驗證集</strong>，其餘 n − 1 筆全部拿去訓練，做 n 次再平均。
  這就是留一交叉驗證（leave-one-out cross-validation, LOOCV）：</p>

  $$\\mathrm{{CV}}_{{(n)}} = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} \\mathrm{{MSE}}_i,
    \\qquad \\mathrm{{MSE}}_i = \\left(y_i - \\hat f^{{(-i)}}(x_i)\\right)^2$$

  <p>其中 $\\hat f^{{(-i)}}$ 是「拿掉第 i 筆」擬合出來的模型。這樣做有兩個好處：
  每一輪都用了幾乎全部的資料（偏差很小），而且<strong>分割方式唯一</strong>——沒有隨機性，
  跑一百次都是同一個數字。</p>

{table(["輪次", "訓練資料", "驗證資料", "得到的量"],
       [["i = 1, …, n", "除了第 i 筆以外的 n−1 筆", "第 i 筆",
         "$(y_i-\\hat f^{(-i)}(x_i))^2$"],
        ["最後", "—", "—", "把 n 個平方誤差平均成 $\\mathrm{CV}_{(n)}$"]])}

  <h3 id="dx-loo">講義完整實作：用 <code>cross_validate</code> 跑 LOOCV</h3>
{card("講義 05 · LOOCV（Auto，degree 1）",
      lab_code(CH, 32), lab_output(CH, 32), src=src("32"),
      note="<strong>24.2315</strong> 就是 degree 1 的 LOOCV 估計。"
           "跟上面驗證集法的 25.57／20.76 比一比：LOOCV 只有一個答案，不會因為切法而跳。")}

{LOOCV_INTUITION}

{LOOCV_DRAWBACKS}

{qa("觀念釐清", [
    ("Q：LOOCV 算出來的 24.23，是在估「哪個」模型的測試誤差？",
     "<p>嚴格說，它估的是「用 n − 1 筆資料訓練出來的模型」的期望測試誤差，"
     "但因為 n − 1 跟 n 幾乎一樣，實務上直接把它當成「用全部 n 筆訓練出來的那個模型」的測試誤差。</p>"
     "<p>這也是為什麼 CV 的最後一步通常是：<strong>用 CV 選出超參數（例如次數 = 2），"
     "然後用全部資料重新擬合一次</strong>，交出那個模型。CV 負責比較設定，選好後再擬合最終模型。</p>"),
    ("Q：scikit-learn 的 <code>cross_validate()</code> 為什麼跑 LOOCV 還是很慢？",
     "<p>因為它是通用函式，不知道你的模型是不是最小平方，所以不使用式 5.2 的捷徑，仍然真的擬合 n 次。"
     "lab 也提到：原則上最小平方的 LOOCV 可以比 k-fold 還快，但通用函式沒有利用這個公式。</p>"),
])}

{quiz("qLoo", "QUIZ · LOOCV",
      "同一份資料上，把 LOOCV 跑兩次，會得到一樣的答案嗎？",
      [(True, "會，因為 n 種「留一」分割是枚舉出來的，沒有隨機性",
        "對。這是 LOOCV 相對於驗證集法與 k-fold 的一個明確優點：結果完全可重現，不需要指定分割用的 seed。"),
       (False, "不會，因為每輪的訓練集不同，隨機性會累積",
        "不對。每輪的訓練集確實不同，但那是<strong>固定</strong>的 n 種分割（第 1 輪必定留第 1 筆），不是隨機抽的。"),
       (False, "不一定，取決於有沒有設 random_state",
        "不對。LOOCV 沒有 <code>random_state</code> 可以設——<code>LeaveOneOut()</code> 不接受這個參數，因為它不需要。")])}
"""

# ── P03 k-fold ────────────────────────────────────────────────────────
BODIES["kfold"] = f"""
  <p>LOOCV 要擬合 n 次模型，n 大就吃不消。折衷方案：把資料<strong>隨機平分成 k 份</strong>，
  每次拿一份當驗證集、其餘 k − 1 份訓練，做 k 輪再平均。這就是 <em>k</em>-fold 交叉驗證：</p>

  <p>講義的寫法：令 $C_1,\\ldots,C_k$ 為各折觀測的索引集合，第 $j$ 折有 $n_j$ 筆（$n$ 能被 $k$ 整除時 $n_j=n/k$）。第 $j$ 折當驗證時，</p>
  $$\\mathrm{{MSE}}_j=\\frac1{{n_j}}\\sum_{{i\\in C_j}}\\bigl(y_i-\\hat y_i^{{(-j)}}\\bigr)^2,\\qquad
  \\mathrm{{CV}}_{{(k)}}=\\sum_{{j=1}}^k\\frac{{n_j}}{{n}}\\,\\mathrm{{MSE}}_j,$$
  <p>其中 $\\hat y_i^{{(-j)}}$ 是拿掉第 $j$ 折擬合的模型對 $x_i$ 的預測。各折一樣大時，權重都是 $1/k$，就是常見的 $\\frac1k\\sum_j\\mathrm{{MSE}}_j$；scikit-learn 的 <code>cross_validate()</code> 回傳各折分數，lab 直接取平均，相當於等權重，$n$ 不能被 $k$ 整除時與加權式會有些微差異。</p>

  <p>LOOCV 其實就是 k = n 的特例。實務上 k 取 5 或 10——原因下一節講。</p>

  <p>講義接著用三組模擬資料比較真正的測試 MSE、LOOCV 與 10-fold CV（ISLP 圖 5.6）。三張圖中，CV 曲線的<strong>高度</strong>有時低估、有時高估真正的測試 MSE，但<strong>最小值出現的位置</strong>大致正確。選擇模型彈性時，我們在乎的正是最小值的位置，所以 CV 即使數值不準，仍然有用。</p>

{info("講義：真正在乎的是最小值的位置", '''用 CV 選模型彈性時，重點是<strong>CV 曲線在哪個彈性達到最小</strong>，最小值本身的數字倒在其次。CV 的數值可能高估或低估真正的測試 MSE，但最小值的位置通常接近真正測試誤差最小的位置。''', "warm")}


{table(["方法", "每輪訓練", "每輪驗證", "輪數", "分割是否唯一"],
       [["5-fold", "4/5 的資料", "1/5 的資料", "5", "否；需固定分割以公平比較模型"],
        ["10-fold", "9/10 的資料", "1/10 的資料", "10", "否"],
        ["LOOCV", "n−1 筆", "1 筆", "n", "是；等同 k=n"]])}

  <h3 id="dx-kf">講義完整實作：<code>KFold</code> 跑 10-fold</h3>
{card("講義 05 · 10-fold CV（degree 1–5）", lab_code(CH, 41), None, src=src("41"),
      note="<code>shuffle=True</code> 很重要：如果原始資料有排序（例如 <code>Auto</code> 按年份），"
           "不打亂就會讓每一折的分佈完全不同。<code>random_state=0</code> 是為了"
           "<strong>讓不同 degree 用同一組分割</strong>。這樣比較才公平。"
           "這格 lab 沒存下輸出，下一節的圖用同樣設定重算了一次。")}

{quiz("qKf", "QUIZ · k-fold",
      "比較不同模型（例如 degree 1 到 10）的 CV 誤差時，為什麼要讓每個模型用<strong>同一組</strong>折分割？",
      [(True, "否則模型之間的差異會混進「分割不同」造成的雜訊，可能比模型本身的差異還大",
        "對。這是 <code>random_state=0</code> 的用意。不然你比到的是「degree 2 加上運氣好的分割」對上「degree 3 加上運氣差的分割」。"),
       (False, "因為 scikit-learn 要求 cv 物件必須重複使用",
        "不對，<code>cross_validate</code> 每次呼叫都可以給不同的 cv 物件。使用相同分割能減少比較時混入的隨機變動。"),
       (False, "因為用不同分割會讓 CV 誤差變成有偏估計",
        "不對。用不同分割每個模型的 CV 誤差仍然是各自無偏的；問題出在<strong>比較</strong>時多了不必要的變異，不是偏差。")])}
"""

# ── P04 k 該取多少 ─────────────────────────────────────────────────────
BODIES["kbias"] = f"""
  <p>k 該取多少？講義從偏差與變異兩個方向說明：</p>

  <ul>
    <li><strong>偏差：k 愈大，偏差愈小。</strong>每輪的訓練集有 $(k-1)n/k$ 筆，比完整資料少；訓練資料少通常讓模型較差，CV 因此傾向<strong>高估</strong>測試誤差。k 愈大，訓練集愈接近 $n$ 筆，這個偏差愈小；LOOCV 的偏差最小，驗證集法最大。</li>
    <li><strong>變異：LOOCV 的估計可能有較高的變異。</strong>LOOCV 平均的是 n 個訓練集幾乎相同的模型的結果，講義指出這些估計高度正相關；許多高度相關的量取平均，變異會比平均許多相關較弱的量來得大。k-fold（k &lt; n）的各折訓練集重疊較少，相關也較低。</li>
  </ul>

{info("講義的結論：k = 5 或 10", '''考慮偏差與變異的取捨，實務上通常用 <strong>k = 5 或 k = 10</strong>：經驗上，它們給出的測試誤差估計既不會偏差太大、也不會變異太高，計算量也只有 LOOCV 的 5/n 或 10/n。''', "warm")}

  <p>講義以 <code>Auto</code> 比較不同次數的模型：</p>

{viz(chart("w05cvChart", "tall", "。此圖的重點：從 degree 1 到 2，CV 誤差從 24.2 掉到 19.2；之後就平了。LOOCV 與 10-fold 的曲線幾乎重疊。"),
     [info_card("怎麼看這張圖",
                'x 軸是 <code>horsepower</code> 多項式的次數，y 軸是 CV 估的測試 MSE。'
                '兩條線分別是 LOOCV 與 10-fold CV。<strong>兩條幾乎重疊</strong>。'
                '這在實務上很常見，也是大家願意用計算量較少的 10-fold 取代 LOOCV 的理由。', "圖 5.4"),
      rows_card("最低點",
                [("LOOCV 最小", "—", "w05cvLoo"), ("10-fold 最小", "—", "w05cvKf"),
                 ("兩者最大差距", "—", "w05cvGap")]),
      info_card("讀圖的重點",
                '不要只看「哪個 degree 的數字最小」。degree 5 的 CV 誤差是 19.03、degree 2 是 19.25，'
                '差 0.2。這遠在雜訊範圍內。<strong>看的是曲線在哪裡「拉平」</strong>，'
                '拉平之後就選最簡單的那個。')],
     "w05cvStatus", "LOOCV 與 10-fold CV 在同一份 Auto 資料上的比較。", "",
     provenance=("course-data", "ISLP Auto；依 Ch05 lab 的 LOOCV／10-fold 設定重算"))}

{table(["k", "每輪訓練用", "偏差（高估測試誤差的程度）", "各折相關", "擬合模型次數", "評語"],
       [["2", "n/2", "較大", "低", "2", "太粗，很少用"],
        ["5", "0.8 n", "小", "中", "5", "實務常用"],
        ["10", "0.9 n", "較小", "中", "10", "實務最常用"],
        ["n（LOOCV）", "n − 1", "最小", "很高，估計變異可能較大", "n", "小資料、或有式 5.2 捷徑時"]])}

{qa("觀念釐清", [
    ("Q：「k 愈大變異愈大」聽起來很反直覺——平均更多項不是應該更穩嗎？",
     "<p>平均更多項會更穩，<strong>前提是那些項彼此獨立</strong>。這裡不是。</p>"
     "<p>算式上看：$\\mathrm{Var}(\\bar X) = \\frac{\\sigma^2}{k} + \\frac{k-1}{k}\\rho\\sigma^2$。"
     "第一項隨 k 變大而變小，但第二項隨 $\\rho$（各折之間的相關）變大而變大。"
     "講義的論點是 LOOCV 各折訓練出的模型幾乎相同，各折估計因而正相關；$\\rho>0$ 時第二項會抵銷一部分第一項隨 k 減小的效果。實際的相關程度依方法與資料而定，不一定接近 1。</p>"
     "<p>直覺版：LOOCV 的 n 個模型幾乎是同一個模型，所以你其實只有「一個」意見被重複算了 n 次。</p>"
     "<p>這條式子假設每折變異 $\\sigma^2$ 與兩兩相關 $\\rho$ 都相同；k 改變時 $\\sigma^2$ 與 $\\rho$ 也會一起變，詳見本節的收合補充。</p>"),
    ("Q：跑 CV 之前要不要標準化？在哪一步做？",
     "<p>要，而且<strong>必須在每一折裡面做</strong>：用該折的訓練部分算平均與標準差，再套到驗證部分。</p>"
     "<p>如果先用全部資料標準化再切折，驗證資料的平均與標準差就洩漏進訓練流程了，"
     "但 CV 誤差改變的方向與大小取決於模型與資料，不能只憑洩漏判定。"
     "例如含截距、未正則化的最小平方在線性縮放下可張出同一模型空間，預測甚至不變。"
     "<code>scikit-learn</code> 的正解仍是把標準化包進 "
     "<code>Pipeline</code>，再把整個 pipeline 丟給 <code>cross_validate</code>。"
     "它會自動在每折內重新 fit。下一節會繼續說明這類資料洩漏問題。</p>"),
])}

{quiz("qK", "QUIZ · k 的取捨",
      "為什麼實務上常選 k = 5 或 10，而不直接用 LOOCV？",
      [(True, "k=5或10常能以較少計算提供有用比較；LOOCV的變異不保證較小，通用流程要擬合n次",
        "對。偏差、變異、計算成本三者的折衷，5 或 10 在三個面向上都可接受。"),
       (False, "因為 LOOCV 會用到驗證資料的資訊，估計不誠實",
        "不對。LOOCV 每輪都完全不看被留下的那一筆，沒有洩漏問題。它的主要代價是估計變異與計算量。"),
       (False, "因為 LOOCV 只能用在線性模型上",
        "不對。LOOCV 對任何模型都能做（只是慢）。<em>有捷徑公式</em>（式 5.2）的才限線性最小平方，這個公式提供加速方式；一般 LOOCV 的適用範圍更廣。")])}
"""

# ── P05 分類上的 CV ────────────────────────────────────────────────────
BODIES["cvclass"] = f"""
  <p>整套邏輯搬到分類問題只要換一件事：把 MSE 換成<strong>錯誤率</strong>。</p>

  $$\\mathrm{{CV}}_{{(k)}} = \\sum_{{j=1}}^{{k}} \\frac{{n_j}}{{n}}\\,\\mathrm{{Err}}_j,
    \\qquad \\mathrm{{Err}}_j = \\frac{{1}}{{n_j}} \\sum_{{i \\in C_j}} I(y_i \\neq \\hat y_i)$$

  <p>$I(\\cdot)$ 是指示函數：預測錯就是 1、對就是 0。其餘完全一樣：切 k 折、輪流當驗證集、平均。
  ISLP 圖 5.7–5.8 用邏輯斯迴歸加上不同次數的多項式項示範：<strong>訓練錯誤率</strong>隨彈性增加持續下降，
  <strong>真正的測試錯誤率</strong>先降後升，而 <strong>10-fold CV 錯誤率</strong>雖然略為低估測試錯誤率，
  最小值的位置卻和測試錯誤率接近，所以能用來挑多項式的次數；KNN 的 $1/K$ 也呈現同樣的趨勢。</p>

{SPLITTERS_D}

{qa("觀念釐清", [
    ("Q：時間序列為什麼不能用普通的 k-fold？",
     "<p>因為隨機切折會讓「未來」的資料進到訓練集、「過去」的資料留在驗證集。"
     "模型於是可以用 2026 年的資訊去預測 2025 年。這在部署時根本不可能發生，"
     "所以 CV 誤差會嚴重低估真實表現。</p>"
     "<p>正解是<strong>只往前切</strong>（<code>TimeSeriesSplit</code>）："
     "用前 100 筆訓練、預測第 101–120 筆；再用前 120 筆訓練、預測第 121–140 筆…"
     "訓練集永遠在驗證集之前。</p>"),
])}

{quiz("qCls", "QUIZ · 分類上的 CV",
      "一份資料裡正例只佔 2%。用普通的 <code>KFold(n_splits=10)</code> 會有什麼風險？",
      [(True, "某些折可能幾乎（或完全）沒有正例，那一折的錯誤率就沒有意義",
        "對。這時要用 <code>StratifiedKFold</code> 維持每折的類別比例。順便一提，這種資料也不該只看錯誤率——全猜負例就有 98%。"),
       (False, "錯誤率的公式在不平衡資料上不成立，要改用 MSE",
        "不對。錯誤率的定義沒有任何問題，它照樣算得出來；問題是它<strong>不是個有用的指標</strong>，以及分割可能退化。改用 MSE 並不能解決任何一個。"),
       (False, "k 必須小於少數類別的樣本數，否則 CV 無法執行",
        "不對。程式跑得起來。這正是危險的地方：它不會報錯，只會安靜地給你一個沒有意義的數字。")])}
"""

# ── P06 CV 的對與錯 ────────────────────────────────────────────────────
BODIES["cvwrong"] = f"""
  <p>先篩選特徵再做 CV，可能讓驗證資料的資訊提前進入訓練流程；程式仍會正常執行。</p>

  <p>講義的情境：兩類資料，<strong>5000 個預測變數、50 筆樣本</strong>。步驟一：找出和類別標籤相關最大的 <strong>100 個</strong>預測變數；
  步驟二：只用這 100 個變數擬合分類器，例如 logistic regression。要估計這個分類器的測試表現，
  能不能只對步驟二做交叉驗證、忘掉步驟一？<strong>不能，這個數字受到資料洩漏（data leakage）影響。</strong></p>

  <p>問題在於「挑特徵」這一步<strong>看過了全部的 y</strong>，包含後來被當成驗證資料的那些。
  篩選本身就是模型訓練的一部分，它必須在每一折的訓練部分內重新執行。</p>

  <p>下面把兩種流程放在<strong>預測變數和類別完全無關</strong>的資料上比較，真正的錯誤率是 0.5：</p>

{MISUSE_VIZ}

  <p>錯誤流程回報的 CV 錯誤率接近 0，彷彿找到了完美的分類器；正確流程才接近真實的 0.5。在 5000 個純雜訊變數中，總會有一些<strong>剛好</strong>和這 50 個標籤高度相關，先看全部資料挑出它們，等於讓驗證折的答案參與了選擇。</p>
{links(("scikit-learn：常見陷阱中的資料洩漏", "https://scikit-learn.org/stable/common_pitfalls.html#data-leakage"))}

{info("一句話原則", '''講義：若前處理依賴資料（例如標準化、one-hot 編碼），應該只在訓練資料上計算，再用那次計算得到的參數去轉換驗證與測試資料。<br>
  凡是<strong>會從資料估計任何參數的步驟</strong>——特徵篩選、標準化的平均與標準差、
  遺漏值填補、過抽樣、目標編碼、PCA 降維——都應<strong>只用每一折的訓練部分估計</strong>。
  在 <code>scikit-learn</code> 裡，把它們串成 <code>Pipeline</code> 再交給
  <code>cross_validate</code>，這件事就自動對了。''', "warm")}

{qa("觀念釐清", [
    ("Q：只用 X 不看 y 的前處理（例如 PCA、去除零變異特徵），也要在每一折內重新估計嗎？",
     "<p>要，因為部署時無法先用未來資料估前處理參數。</p>"
     "<p>不看 y 的前處理不會直接把標籤洩漏進來，但偏差方向與大小仍取決於模型與資料，"
     "有時預測可以完全不變。"
     "但它仍然用到了驗證資料的<strong>分佈</strong>資訊（PCA 的方向、特徵的變異數），"
     "而在部署時你不可能先看過未來資料的分佈。既然包進 <code>Pipeline</code> 幾乎沒有額外成本，"
     "就一律包進去，不必去分辨哪種洩漏比較嚴重。</p>"),
    ("Q：我用 CV 選超參數，那 CV 誤差可以當成最終模型的測試誤差報出來嗎？",
     "<p>不太行，它會偏低。你已經拿 CV 誤差當目標挑過超參數了——"
     "被挑中的那組本來就是「在這組折上運氣最好」的那組，這叫做選擇偏差。</p>"
     "<p>要把調參與評估分開，可以用<strong>巢狀交叉驗證</strong>（nested CV）："
     "外層折只負責評估、完全不參與調參；內層折在外層的訓練部分裡調參。"
     "或者更簡單：一開始就切出一份從頭到尾沒碰過的測試集。</p>"),
])}

{quiz("qWrong", "QUIZ · CV 的錯用",
      "在 5-fold CV 之前先用<strong>全部</strong>資料把特徵標準化（減平均、除標準差）。這樣有問題嗎？",
      [(True, "有問題：平均與標準差用到了驗證折；應折內 fit，但誤差偏差方向不能預先斷言",
        "對。把 <code>StandardScaler</code> 放進 <code>Pipeline</code>，讓它在每折的訓練部分重新 fit。數值偏差可能高、低或為零；含截距且未正則化的最小平方在仿射縮放下甚至可得到相同預測。"),
       (False, "沒問題：標準化只是線性變換，不改變模型的預測能力",
        "這只對部分模型成立，例如含截距、未正則化的最小平方。一般流程仍不應用驗證折估平均與標準差；正則化、距離式方法等也可能改變預測。"),
       (False, "沒問題：標準化沒有用到 y，所以不算洩漏",
        "沒用到 y 不等於能用驗證折估參數；它仍用了驗證資料的分佈資訊。應在每折訓練部分 fit，再套到該折驗證部分。")])}

{SHUFFLE_SECTION}

  <h3 id="dx-kf-ss">講義完整實作：用 <code>ShuffleSplit</code> 做驗證集法與重複切分</h3>
{card("講義 05 · ShuffleSplit(n_splits=1) 就是驗證集法", lab_code(CH, 44), lab_output(CH, 44), src=src("44"),
      note="驗證 MSE 23.62。它和驗證集法一節圖中 <code>random_state=0</code> 那次切分的一次式數字相同，因為兩者用了同一種隨機切法。")}
{card("講義 05 · 重複 10 次隨機切分", lab_code(CH, 46), lab_output(CH, 46), src=src("46"),
      note="10 次切分的平均 23.80、標準差 1.42。各次的訓練樣本重疊、彼此相關，所以這個標準差只反映換不同隨機切分的<strong>蒙地卡羅變異</strong>，不能當作平均測試分數的抽樣標準誤。")}
"""

# ── P07 Bootstrap ─────────────────────────────────────────────────────
BODIES["bootstrap"] = f"""
  <p>換一個問題。前面都在問「模型的預測有多準」；現在問<strong>「我算出來的這個數字有多不確定」</strong>。</p>

  <p class="core-backfill">抽樣分佈與自助法還不熟時，可先複習
  <a href="s4_inference.html#bootstrap">S4 的 Bootstrap 入門</a>。</p>

  <p>ISLP §5.2 的例子：把錢分成比例 α 投資 X、1 − α 投資 Y，要讓報酬的變異最小，最佳比例是</p>

  $$\\alpha = \\frac{{\\sigma_Y^2 - \\sigma_{{XY}}}}{{\\sigma_X^2 + \\sigma_Y^2 - 2\\sigma_{{XY}}}}$$

  <p>把樣本變異數代進去就得到 $\\hat\\alpha$。但 $\\hat\\alpha$ 有多可靠？
  它的標準誤沒有簡單的公式可查。理想上我們會重新蒐集 1000 份新資料、算 1000 個 $\\hat\\alpha$、
  看它們的標準差，但我們只有一份資料。</p>

{BOOT_NAME}
{BOOT_SIM}
  <h3 id="w05-boot-real">回到真實世界</h3>
  <p>上面的程序在真實資料上做不到，因為無法從原本的母體產生新樣本。bootstrap 讓電腦模仿「取得新資料」的過程：它不從母體重複抽獨立的資料集，改成<strong>從原始資料有放回地重複抽樣</strong>。每份 bootstrap 資料集和原資料一樣大，所以有些觀測會出現不只一次，有些一次也沒出現。</p>
  <p><strong>Bootstrap 的做法：把手上這份資料當成母體，從裡面有放回地抽 n 筆</strong>，
  當成一份「新」資料集，重算 $\\hat\\alpha^*$。重複 B 次，那 B 個 $\\hat\\alpha^*$ 的標準差
  就是 $\\mathrm{{SE}}(\\hat\\alpha)$ 的估計。不必指定常態分布，但重抽單位須符合資料的獨立性與研究設計。</p>

{viz('      <div id="w05bootSvg" class="info-box" style="font-family:var(--mono);font-size:.78rem;">'
     '尚未重抽。按「抽一次」後會顯示 Portfolio 的抽樣索引摘要。</div>\n'
     + chart("w05bootChart", "", "。圖中每一個值都是 Portfolio 的 α̂*，其標準差估計 SE(α̂)。"),
     [info_card("虛擬碼", '<div class="pseudo-code" id="w05bootCode" style="font-size:.74rem;">'
                '<span class="line" data-l="1"><span class="kw">for</span> b <span class="kw">in</span> <span class="kw">range</span>(B):</span>\n'
                '<span class="line" data-l="2">    idx = 有放回抽 n 個</span>\n'
                '<span class="line" data-l="3">    θ*[b] = f(資料[idx])</span>\n'
                '<span class="line" data-l="4">SE = std(θ*)</span></div>', "CODE"),
      rows_card("這一次重抽",
                [("前 12 個抽樣索引", "—", "w05bootDraw"),
                 ("沒被抽到（OOB）", "—", "w05bootOob"),
                 ("這次的 α̂*", "—", "w05bootStat"),
                 ("累計 B", "0", "w05bootB"),
                 ("累計 SE", "—", "w05bootSE")]),
      info_card("Portfolio 的真實結果",
                '用全部 100 筆算：α̂ = <strong>0.5758</strong>。跑 B = 1000 次 bootstrap 後，'
                'SE(α̂) = <strong>0.0912</strong>。下面的 lab 卡片有逐字輸出。', "ISLP §5.2")],
     "w05bootStatus", "從 Portfolio 的 100 對 (X,Y) 有放回抽 100 對，再重算同一個 α̂。",
     '<button class="btn btn-step" onclick="w05bootDrawOne()">→ 抽一次</button>'
     '<button class="btn btn-play" onclick="w05bootMany()">▶ 連抽 200 次</button>'
     '<button class="btn btn-reset" onclick="w05bootReset()">重置</button>',
     provenance=("course-data", "ISLP Portfolio；與 Ch05 lab 的 α̂ 統計量一致"))}

{BOOT_WORLD}

{BOOT_CI}

  <h3 id="dx-boot">講義完整實作：<code>boot_SE()</code></h3>
{card("講義 05 · 定義 alpha_func 並用全部 100 筆", lab_code(CH, 53) + "\n\n" + lab_code(CH, 55), lab_output(CH, 55), src=src("53、55"),
      note="這就是 ISLP 書上的 α̂ = 0.5758。")}

{card("講義 05 · 一次 bootstrap 重抽", lab_code(CH, 57), lab_output(CH, 57), src=src("57"),
      note="<code>replace=True</code> 是關鍵：有放回，所以同一筆可能被抽到好幾次，"
           "也會有一些完全沒被抽到。這一次抽出來的 α̂* = 0.6074，跟 0.5758 差了不少。"
           "這個「差」正是我們要量化的東西。")}

{card("講義 05 · 通用的 boot_SE", lab_code(CH, 59), None, src=src("59、61"),
      note="在 Portfolio 資料上，SE(α̂) 的 bootstrap 估計是 <strong>0.0912</strong>。"
           "注意這支函式用 $E[\\theta^2] - (E[\\theta])^2$ 累加，不必存下 1000 個值。")}

{card("講義 05 · 用 bootstrap 估計迴歸係數的標準誤", lab_code(CH, 65) + "\n\n" + lab_code(CH, 67) + "\n\n" + lab_code(CH, 69), lab_output(CH, 69), src=src("65、67、69"),
      note="<code>partial()</code> 凍結模型與反應變數兩個參數，得到 <code>boot_SE()</code> 需要的 (D, idx) 函式。上面是前 10 份 bootstrap 樣本的截距與斜率。")}
{card("講義 05 · bootstrap 標準誤與公式標準誤", lab_code(CH, 71) + "\n\n" + lab_code(CH, 73), lab_output(CH, 73), src=src("71、73"),
      note="lab 說明 1000 次 bootstrap 給 SE(β̂₀) ≈ 0.73、SE(β̂₁) ≈ 0.00609，公式給 0.717 與 0.006。"
           "差異來自公式的假設：它用殘差估 σ²，而直線模型漏掉了非線性，殘差被誇大；公式也假設 x 固定。bootstrap 不依賴這些假設。")}
{card("講義 05 · 二次模型：兩種標準誤更接近", lab_code(CH, 75) + "\n\n" + lab_code(CH, 77), lab_output(CH, 77), src=src("75、77"),
      note="二次模型對資料的擬合好得多，bootstrap 與公式的標準誤因此對應得更好。")}

  <h4 id="dx-632">bootstrap 樣本只含約 63.2% 的原始樣本</h4>
  <p>有放回地抽 n 次，每筆至少出現一次的機率如下；它也是不同原始觀測所占比例的期望，不代表每份樣本的固定比例。</p>

  $$P(\\text{{第 }} i \\text{{ 筆有進 bootstrap 樣本}}) = 1 - \\left(1-\\frac{{1}}{{n}}\\right)^n
    \\;\\xrightarrow[n \\to \\infty]{{}}\\; 1 - e^{{-1}} \\approx 0.632$$

  <p>剩下那 36.8% 沒被抽到的樣本叫做 <strong>out-of-bag</strong>（OOB）。
  它們對這一輪的模型來說是天然的驗證集。<a href="tree_based_methods.html#bagging">樹狀方法的 bagging 與 random forest</a> 就靠這招
  不另切驗證集就能估計測試誤差。</p>

{table(["n", "5", "20", "100", "n → ∞"],
       [["$1-(1-1/n)^n$", "0.6723", "0.6415", "0.6340", "$1-e^{-1}=0.6321$"]])}

  <p>這也回答了講義的問題「bootstrap 能估預測誤差嗎？」交叉驗證的 k 個驗證折和訓練用的其他 k − 1 折<strong>沒有重疊</strong>，交叉驗證行得通靠的就是這一點。若拿每份 bootstrap 樣本訓練、用原始資料驗證，每份訓練樣本約含三分之二的原始觀測，<strong>驗證資料大量出現在訓練資料裡</strong>，會嚴重低估真正的預測誤差。只用沒抽到的觀測來驗證可以部分修正，但方法會變複雜；最後還是交叉驗證比較簡單。</p>
{info("講義：bootstrap 能估預測誤差嗎？", '''每份 bootstrap 樣本約含三分之二的原始觀測，拿它訓練、再用原始資料驗證，驗證資料大量重疊，會<strong>嚴重低估</strong>預測誤差。只用沒被抽到的觀測驗證能部分修正，但方法變得複雜。結論：<strong>估標準誤用 bootstrap，估預測誤差用交叉驗證。</strong>''', "warm")}

{TWO_THIRDS_D}

{qa("觀念釐清", [
    ("Q：Bootstrap 可以用來估「預測誤差」嗎？",
     "<p>可以，但要很小心，而且通常比不上交叉驗證。</p>"
     "<p>問題出在重疊：bootstrap 樣本平均含有原始資料的 63.2%，"
     "所以如果你用 bootstrap 樣本訓練、用原始全部資料當測試，"
     "那個「測試集」裡有三分之二的資料模型已經看過了，誤差會嚴重低估。</p>"
     "<p>補救方式是只用 OOB 的那 36.8% 來評估，這就接近 k-fold 的精神了。"
     "所以講義的答案是：<strong>估標準誤用 bootstrap，估預測誤差用交叉驗證。</strong></p>"),
    ("Q：B 要取多少？",
     "<p>估標準誤時 B = 1000 通常就很夠；要估信賴區間的尾端分位數（例如 2.5% 與 97.5%），"
     "B 建議拉到 2000 以上，因為尾端需要更多樣本才穩。</p>"
     "<p>注意 B 大只會讓「bootstrap 對真實 SE 的估計」更穩定，"
     "<strong>不會讓原始資料變多</strong>。n 小的時候 bootstrap 本身就不可靠，"
     "拉高 B 也救不了。它只是把同一份資料提供的資訊算得更精確而已。</p>"),
    ("Q：bootstrap 什麼時候會失效？",
     "<p>幾種常見的限制：</p><ul>"
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
        "不對。有放回意味著同一筆可以被抽到好幾次，也就意味著<strong>可能有觀測完全沒被抽到</strong>；n=100 時預期約 36.6%，大樣本極限約 36.8%，並非每次重抽都相同。")])}
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
        "對，兩個缺點都改善了。代價只是要擬合 k 次模型而不是 1 次。"),
       (False, "k-fold CV 完全沒有隨機性，驗證集法有",
        "不對，這是 <strong>LOOCV</strong> 的性質。k-fold 要隨機分折，換 <code>random_state</code> 答案還是會動，只是幅度比驗證集法小很多。"),
       (False, "k-fold CV 不需要把資料切開，所以能用到全部資料訓練",
        "不對。每一輪都還是切開的（k−1 折訓練、1 折驗證）。差別在於「每一筆資料都輪到當一次驗證資料」，不是「不用切」。")])}

{quiz("qEx3", "EXERCISE 3 · ISLP 5.4 第 8 題",
      "課本第 8 題在模擬資料上跑 degree 1 到 4 的 LOOCV，真實模型是二次的。"
      "預期會看到什麼？",
      [(True, "degree 1 到 2 誤差大幅下降，之後幾乎不再改善（甚至微幅上升）",
        "對。這也是本頁 P04 那張 Auto 圖的形狀：真實複雜度以下，加彈性有幫助；超過之後只是在擬合雜訊。"),
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
        "不對。bootstrap 幾乎對任何估計量都能用。這正是它最大的優點。")])}
"""

# ── REF ───────────────────────────────────────────────────────────────
# 講義選讀與附錄：資料結構、信賴區間及虛無分佈。
BODIES["cvwrong"] += r"""
<h3>分折也要反映未來的預測情境</h3>
<p>獨立同分佈資料可先打散再分折；類別不平衡時可分層保持類別比例。
同一人的多筆資料應整組分到同一側，避免模型在驗證集認出訓練過的人。
時間序列用較早資料訓練、較晚資料驗證，可採擴張或滑動訓練窗；任意打散會把未來資訊送進過去。</p>
<p>需要精確控制驗證比例時，可採重複隨機切分（ShuffleSplit），每次獨立指定訓練與驗證大小。
不同輪的驗證集可能重疊，不能當作互相獨立的測試實驗；標準化、補值、特徵選擇與調參都須遵守相同的分割界線。</p>
"""
BODIES["bootstrap"] += r"""
<h3>用 bootstrap 建立預測區間</h3>
<p>主文的百分位區間與曲線區間描述的是<strong>平均</strong>的不確定性。<strong>預測區間</strong>還須包含新觀測的隨機誤差。在獨立、同變異數的迴歸設定，可用下方固定設計流程估計參數造成的預測誤差，再加上獨立抽取的新觀測誤差，從總預測誤差的分位數建立區間。只重抽係數或平均值曲線會漏掉這一項。
異變異數、群聚或時間相依資料需要對應的殘差模型或重抽設計；block bootstrap 以連續區塊保留部分時間相依性。</p>
<h3>Jackknife：逐筆刪除，估計量會變多少？</h3>
<p>令 $\hat\theta_{(-i)}$ 是刪去第 i 筆後的估計，$\bar\theta_{(-)}$ 是這 n 個估計的平均。
Jackknife 的標準誤估計為</p>
$$\widehat{SE}_{jack}=\sqrt{\frac{n-1}{n}\sum_i(\hat\theta_{(-i)}-\bar\theta_{(-)})^2}.$$
<p>它和 LOOCV 都逐筆刪除，但這裡比較估計量本身的變化，LOOCV 則記錄被留下觀測的預測誤差。
Jackknife 適合較平滑的統計量；對最大值等不平滑統計量不能期待一般公式可靠。</p>
<h3>Permutation test：假如 X 與標籤沒有關聯？</h3>
<p>講義比較兩者：bootstrap 從<strong>估計出的母體</strong>重抽，用來估標準誤與信賴區間；在簡單情況也能做檢定，例如虛無假設 $\theta=0$ 時，看 $\theta$ 的信賴區間是否包含 0。置換方法則從<strong>估計出的虛無分佈</strong>抽樣，用來算 p 值。前者想描述某個統計量的<strong>抽樣分佈</strong>，後者想描述<strong>虛無分佈</strong>。</p>
<p>講義的置換檢定四步驟：</p>
<ol>
<li>定義檢定統計量 $T$。</li>
<li>用原始資料算出觀察到的統計量 $T_a$。</li>
<li>把資料置換 $N$ 次，每次算 $T_1,\ldots,T_N$，它們構成虛無假設下的分佈。</li>
<li>以 $|T_i|\ge|T_a|$ 的比例作為 p 值（雙尾時兩邊都取絕對值；下方加一的公式可避免 p 值為零）。</li>
</ol>
<p>Bootstrap 近似估計量的抽樣分佈；<strong>置換檢定（permutation test）</strong>則利用虛無假設下的可交換性建立參考分佈。
例如以兩組平均差為 T，在組別標籤可交換的虛無假設下打亂標籤，重算 T。
雙尾檢定比較 $|T_b|\ge|T_{obs}|$，不能只把觀察統計量取絕對值而忽略置換統計量的負尾。</p>
<p>若隨機抽 B 次置換，常用避免零 p 值的估計為</p>
$$\hat p=\frac{1+\sum_{b=1}^B I(|T_b|\ge|T_{obs}|)}{B+1}.$$
<p>分類器版本（scikit-learn 的 <code>permutation_test_score</code>）的虛無假設是：分類器沒有利用特徵與標籤之間的任何相依性，在留出資料上做出正確預測。可用交叉驗證正確率作 T：保留 X、打亂 y，每次重新訓練並執行相同評估流程，
比較置換得分是否大於等於原始得分（此時是右尾，無須取絕對值）。有監督的特徵選擇或調參亦須在每次置換內重做。
若使用損失當統計量，較小才是較好的表現，尾端方向須一起改變。</p>
<p>小 p 值表示這個流程觀察到的表現難以用無關聯的置換資料解釋；大 p 值可能是沒有關聯，也可能是分類器未能抓到關聯。
配對、群聚與時間資料不能任意逐筆置換，應使用符合虛無假設及設計的限制置換。
由信賴區間是否包含虛無值所形成的 bootstrap 檢定，與置換的虛無分佈也不是同一程序。講義的例子是：原始資料得到低 p 值，同樣的特徵配上隨機標籤則得到高 p 值。</p>
""" + BOOT_APPENDIX_LINKS + r"""
"""

BODIES["reference"] = f"""
  <p>考前把這一頁掃過去就好。</p>

  <h3>四種方法對照</h3>
{table(["方法", "在估什麼", "偏差", "變異", "計算成本", "隨機性", "典型用途"],
       [["驗證集法", "測試誤差", "大（高估）", "大", "1×", "有，很大", "快速看一眼"],
        ["LOOCV", "測試誤差", "最小", "大", "n×", "無", "小資料、線性有捷徑"],
        ["<em>k</em>-fold CV", "測試誤差", "小", "小", "k×", "有，較小", "<strong>選模型的標準做法</strong>"],
        ["Bootstrap", "估計量的 SE", "—", "—", "B×", "有，B 大就穩", "<strong>估不確定性</strong>"]])}

  <h3>公式速查</h3>
{table(["名稱", "式子", "備註"],
       [["LOOCV", "$\\mathrm{CV}_{(n)} = \\frac1n\\sum_i \\mathrm{MSE}_i$", "式 5.1"],
        ["LOOCV 捷徑（最小平方）",
         "$\\frac1n\\sum_i\\left(\\frac{y_i-\\hat y_i}{1-h_i}\\right)^2$", "式 5.2，只擬合一次模型"],
        ["<em>k</em>-fold", "$\\mathrm{CV}_{(k)} = \\frac1k\\sum_j \\mathrm{MSE}_j$", "式 5.3"],
        ["分類版", "$\\mathrm{Err}_j = \\frac{1}{|C_j|}\\sum_{i\\in C_j} I(y_i \\ne \\hat y_i)$", "式 5.4"],
        ["最小變異配置", "$\\alpha = \\frac{\\sigma_Y^2-\\sigma_{XY}}{\\sigma_X^2+\\sigma_Y^2-2\\sigma_{XY}}$", "式 5.7"],
        ["在 bootstrap 樣本裡的機率", "$1-(1-1/n)^n \\to 1-e^{-1} \\approx 0.632$", "OOB 的來源"]])}

{info("三個一定要記住的觀念", '''<strong>1. 交叉驗證估「預測誤差」，bootstrap 估「估計量的不確定性」。</strong>
  兩者都在重抽樣，但問的問題不同，不要混用。<br>
  <strong>2. k = 5 或 10 是偏差、變異、計算成本三方的折衷。</strong>
  LOOCV每輪的樣本量最接近完整資料，但變異仍依資料與方法而定。<br>
  <strong>3. 任何從資料估參數的前處理都要在每一折的訓練部分內進行。</strong>
  特徵篩選、標準化、填補、過抽樣、目標編碼——在每折訓練部分 fit，再套到驗證部分。
  洩漏造成的數值偏差方向依模型與資料而定。''')}


"""

# ══════════════════════════════════════════════════════════════════════
# COVERAGE-20260910 BEGIN

BODIES['loocv'] += r"""
<h3>LOOCV 捷徑何時可用？</h3>
<p>固定的最小平方設計矩陣 X 滿欄秩，而且每次刪一筆後仍滿欄秩，才能用 $e_i^{(-i)}=e_i/(1-h_{ii})$。其中 $H=X(X^TX)^{-1}X^T$、$h_{ii}=x_i^T(X^TX)^{-1}x_i$。例如原殘差 2、槓桿值 0.2，留一誤差為 2.5、平方誤差為 6.25。高槓桿點對自己的擬合拉力大，留掉它後誤差可能放大。</p>
<p>$h_{ii}=1$ 時分母為零，刪除後也失去滿秩，不能把 0/0 設成零。若每折重新選變數、選多項式次數或調整超參數，也不能只拿選好模型的一組 H 取代整個流程。固定基底的普通最小平方適用；非線性估計器沒有此一般捷徑。</p>
""" + proof('w05proofPress', '刪一筆殘差等於 e/(1−h)', r"""
<p>令 $A=X^TX$、$b=X^Ty$。刪除第 i 筆的 normal equations 為 $(A-x_ix_i^T)\hat\beta_{(-i)}=b-x_iy_i$。完整資料則有 $A\hat\beta=b$。兩式相減並整理：</p>
$$A(\hat\beta_{(-i)}-\hat\beta)=-x_i(y_i-x_i^T\hat\beta_{(-i)})=-x_i e_i^{(-i)}.$$
<p>左乘 $x_i^TA^{-1}$，得 $x_i^T(\hat\beta_{(-i)}-\hat\beta)=-h_{ii}e_i^{(-i)}$。而 $e_i^{(-i)}=e_i-x_i^T(\hat\beta_{(-i)}-\hat\beta)$，所以 $(1-h_{ii})e_i^{(-i)}=e_i$。平方後逐筆平均就是 LOOCV 公式。矩陣行列式引理給 $\det(A-x_ix_i^T)=\det(A)(1-h_{ii})$，也說明分母為零對應刪除後秩不足。</p>
""")
BODIES['bootstrap'] += proof('w05proofPortfolio', '投資組合最小變異權重與 bootstrap 唯一樣本數', r"""
<p>組合 $\alpha X+(1-\alpha)Y$ 的變異數為 $V(\alpha)=\alpha^2\sigma_X^2+(1-\alpha)^2\sigma_Y^2+2\alpha(1-\alpha)\sigma_{XY}$。微分並令為零：</p>
$$V'(\alpha)=2\alpha(\sigma_X^2+\sigma_Y^2-2\sigma_{XY})-2(\sigma_Y^2-\sigma_{XY})=0.$$
<p>分母 $\operatorname{Var}(X-Y)>0$ 時，二階導數為正，所以最小值在 $\alpha=(\sigma_Y^2-\sigma_{XY})/(\sigma_X^2+\sigma_Y^2-2\sigma_{XY})$。若另限制不得放空（0≤α≤1），把此解截到 [0,1]；分母為零時 X−Y 幾乎處處為常數，變異數不隨 α 改變。</p>
<p>bootstrap 每次未抽到某筆的機率為 1−1/n，獨立抽 n 次都沒抽到的機率為 $(1-1/n)^n$。以指示變數 $I_i$ 表示是否至少出現一次，線性期望給 $E[\sum_i I_i]=n[1-(1-1/n)^n]$。比例趨近 $1-e^{-1}=0.6321$；各 $I_i$ 不必彼此獨立，也不是每份樣本恰好有 63.2% 不同觀測。</p>
""")
BODIES['kbias'] += detail('w05-detail-loocv-variance', '延伸閱讀：LOOCV 的變異一定比較高嗎？', r"""
<p>講義與 ISLP 的說法是 LOOCV 的估計「傾向」有較高的變異。這是常見的經驗，但不是對每個問題都成立的定理。</p>
<ul>
<li>下式說明了正相關如何限制平均的效果；可是 k 改變時，每折誤差本身的變異 v 也會改變（LOOCV 每折只有一筆驗證資料，k-fold 每折有 n/k 筆），相關結構也不同。</li>
<li>對很穩定的學習方法（例如低次多項式的最小平方），各留一模型幾乎相同，LOOCV 與 10-fold 的估計往往很接近，前面 <code>Auto</code> 的兩條曲線就是例子；對不穩定的方法，差異才較明顯。</li>
<li>實務上的建議不變：一般用 5-fold 或 10-fold；LOOCV 適合資料很少或有最小平方捷徑的情況。</li>
</ul>
<p><strong>偏差的一面。</strong>每輪訓練集只有 $(k-1)n/k$ 筆。若測試誤差隨訓練筆數增加而下降（學習曲線向下），用較少資料訓練的模型誤差較大，所以 CV 估計傾向高估「用全部 $n$ 筆訓練」的測試誤差；$k$ 愈大，差距愈小。</p>
<p><strong>變異的一面。</strong>平均 $K$ 個折誤差 $E_k$ 時，若各折獨立、變異都是 $v$，平均的變異是 $v/K$；若兩兩相關都是 $\rho$，變異變成下式的 $v/K+(K-1)\rho v/K$，當 $K$ 很大時趨近 $\rho v$，再多平均也降不下去。</p>
""" + links(("相關與不相關資料的平均，其變異數如何不同", "https://stats.stackexchange.com/questions/223446/variance-of-the-mean-of-correlated-and-uncorrelated-data"), ("LOOCV 與 k-fold CV 的偏差與變異", "https://stats.stackexchange.com/questions/61783/bias-and-variance-in-leave-one-out-vs-k-fold-cross-validation?noredirect=1&lq=1")) + proof('w05proofCvVariance', '平均相關誤差的變異數', r"""
<p>對 K 個有有限變異數的折誤差 $E_1,\ldots,E_K$，由平方展開與期望線性性：</p>
$$\operatorname{Var}\left(\frac1K\sum_k E_k\right)=\frac1{K^2}\left[\sum_k\operatorname{Var}(E_k)+2\sum_{k\lt l}\operatorname{Cov}(E_k,E_l)\right].$$
<p>若每折變異數為 v、兩兩相關均為 ρ，則結果為 $v/K+(K-1)\rho v/K$。ρ=0 才有熟悉的 v/K；正相關會限制平均所能降低的變異。不過不同 K 的 v 與相關結構也會改變，因此這個公式解釋取捨，沒有證明每個問題的 LOOCV 都比 10-fold 變異大。</p>
"""))


# DIRECT-LINKS-20260910

BODIES['cvwrong'] += r"""
<h3>調參、外層評估與折外預測</h3>
""" + NESTED_GUIDE + r"""
<h4>折外預測：另外一個常見用途</h4>
<p><code>cross_val_predict</code>收集每筆未參與該次擬合時的折外（out-of-fold）預測，但把它們合併計算一次指標，不必等於先算每折指標再平均。逐點可加總的損失如MSE，可用折大小加權得到相同整體平均；AUC、F1等非線性指標沒有這種一般等價性。不同折的分數來自不同模型，合併AUC時也要考慮跨折分數尺度。</p>
<p>時間切分應配合未來的預測期間，必要時在訓練尾端與驗證起點間保留間隔，避免滾動特徵或觀測重疊造成洩漏。固定seed讓同一切法可重現，但一次切分不會因此消除抽樣不確定性。</p>
"""
BODIES['bootstrap'] += r"""
<h3>Jackknife也能估計偏差</h3>
<p>設 $\bar\theta_{(-)}=n^{-1}\sum_i\hat\theta_{(-i)}$。除了前面的標準誤，jackknife的偏差估計與修正後估計量為</p>
$$\widehat{\mathrm{bias}}_{jack}=(n-1)(\bar\theta_{(-)}-\hat\theta),\qquad \hat\theta_{bc}=n\hat\theta-(n-1)\bar\theta_{(-)}.$$
<p>這利用估計量偏差隨樣本數平滑變化的近似，不保證適用於最大值、中位數等非光滑統計量。平均數的jackknife偏差估計恰為零，標準誤恰為 $s/\sqrt n$；</p>
<h3>固定設計下用bootstrap估預測誤差</h3>
<p>假設 $Y=X\beta+\varepsilon$、誤差iid且同變異。先擬合OLS，使用適當中心化、按槓桿值調整的殘差（例如 $e_i/\sqrt{1-h_{ii}}$）近似新誤差分布。每輪抽出n個誤差，產生 $y^*=X\hat\beta+e^*$ 並重新擬合得到 $\hat\beta^*$；另獨立抽一個 $e_{new}^*$。對固定新輸入 $x_0$ 計算</p>
$$\Delta^*=x_0^T(\hat\beta-\hat\beta^*)+e_{new}^*.$$
<p>用 $x_0^T\hat\beta+q_{\alpha/2}(\Delta^*)$ 與 $x_0^T\hat\beta+q_{1-\alpha/2}(\Delta^*)$ 作近似PI。這是模擬「新觀測減去估計預測值」的誤差，保留參數誤差的方向；只畫bootstrap平均曲線的分位數會漏掉新觀測雜訊。異質變異或時間相依時，這個iid殘差抽樣設計不適用。</p>
<p>相依資料的一個替代是區塊自助法：選定區塊長度，抽取連續觀測區塊並串接到所需長度。區塊可重疊、循環或使用隨機長度；須說明所用版本，不能聲稱單一區塊長度保證保留全部相依性。</p>
""" + proof('w05proofJackknife','Jackknife偏差修正與平均數標準誤',r"""
<p>若 $E[\hat\theta_n]=\theta+a/n+b/n^2+O(n^{-3})$，刪一估計的期望為 $\theta+a/(n-1)+b/(n-1)^2+O(n^{-3})$。因此 $nE[\hat\theta_n]-(n-1)E[\bar\theta_{(-)}]$ 的a項抵消，剩餘偏差為O(n⁻²)。這是平滑偏差展開下的結論，不適用於所有統計量。</p>
<p>對平均數，$\bar x_{(-i)}=(n\bar x-x_i)/(n-1)$，所以刪一平均的平均是 $\bar x$，偏差估計為0。而 $\bar x_{(-i)}-\bar x=(\bar x-x_i)/(n-1)$，代入jackknife變異數公式，得到 $\sum_i(x_i-\bar x)^2/[n(n-1)]=s^2/n$。</p>
""") + ""

# COVERAGE-20260910 END

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
    datasets: [{ label: '100 次模擬的平均 5-fold CV 錯誤率',
                 data: [F.wrong.mean, F.right.mean],
                 backgroundColor: [HC.tok.accent, HC.tok.accent3], borderRadius: 5 }],
  }, {
    plugins: { legend: { display: false } },
    scales: { y: { min: 0, max: 0.6, title: { display: true, text: 'CV 錯誤率' } } },
  });
  const c = HC.get('w05misChart');
  HC.refs(c, [HC.hline(0.5, '獨立評估的錯誤率 ≈ 0.5')]);
  $('w05misWrong').textContent = HC.fmt(F.wrong.mean, 3);
  $('w05misRight').textContent = HC.fmt(F.right.mean, 3);
  $('w05misWrongRange').textContent = HC.fmt(F.wrong.q10, 2) + '–' + HC.fmt(F.wrong.q90, 2);
  $('w05misRightRange').textContent = HC.fmt(F.right.q10, 2) + '–' + HC.fmt(F.right.q90, 2);
  setStatus('w05misStatus', F.reps + ' 次獨立的 n = ' + F.n + '、p = ' + F.p
    + ' 純雜訊模擬：錯誤流程平均回報 ' + HC.fmt(F.wrong.mean, 3)
    + '，正確流程平均回報 ' + HC.fmt(F.right.mean, 3)
    + '。單次結果會波動，應一起閱讀多次模擬的分布與平均。');
}

/* ---------- P03 切分索引圖（live，示意）---------- */
const w05splitN = 40, w05splitK = 5;
const w05splitY = Array.from({ length: w05splitN }, (_, i) => (i < 24 ? 0 : 1));
let w05splitSvc = null;
function w05splitPerm(idx, seed) {
  const r = HC.stat.lcg(seed), a = idx.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
function w05splitMake(kind) {
  const all = Array.from({ length: w05splitN }, (_, i) => i), tests = [];
  if (kind === 0 || kind === 1) {
    const order = kind === 0 ? all : w05splitPerm(all, 2024);
    for (let f = 0; f < w05splitK; f++) tests.push(order.slice(f * 8, f * 8 + 8));
  } else if (kind === 2) {
    for (let f = 0; f < w05splitK; f++) tests.push([]);
    [0, 1].forEach(c => {
      const idx = w05splitPerm(all.filter(i => w05splitY[i] === c), 2025 + c);
      /* 第二類接著第一類的折序號繼續輪配，各折大小才會相同（同 scikit-learn） */
      const start = c === 0 ? 0 : 24 % w05splitK;
      idx.forEach((i, t) => tests[(start + t) % w05splitK].push(i));
    });
  } else {
    for (let f = 0; f < w05splitK; f++) tests.push(w05splitPerm(all, 3000 + f).slice(0, 8));
  }
  return tests;
}
function w05splitSetup() {
  w05splitSvc = HC.svg('w05splitSvg', { xd: [0, w05splitN], yd: [0, 6.6], h: 300, pad: { l: 78, r: 12, t: 12, b: 30 } });
}
function w05splitShow(kind) {
  const s = w05splitSvc;
  if (!s) return;
  const names = ['KFold（不洗牌）', 'KFold（洗牌）', 'StratifiedKFold', 'ShuffleSplit'];
  const tests = w05splitMake(kind), g = s.clearLayer('main');
  const rowY = r => 6 - r;                     /* r = 0 是類別列 */
  for (let i = 0; i < w05splitN; i++) {
    s.box(i + 0.06, rowY(0) - 0.38, i + 0.94, rowY(0) + 0.38,
          { fill: w05splitY[i] ? HC.tok.b : HC.tok.a }, g);
  }
  s.txtPx(8, s.Y(rowY(0)) + 4, '類別', { cls: 'axlab' }, g);
  const count = new Array(w05splitN).fill(0);
  tests.forEach((te, f) => {
    const set = new Set(te);
    te.forEach(i => count[i]++);
    for (let i = 0; i < w05splitN; i++) {
      const r = s.box(i + 0.06, rowY(f + 1) - 0.38, i + 0.94, rowY(f + 1) + 0.38,
                      { fill: set.has(i) ? HC.tok.accent : HC.tok.muted }, g);
      r.setAttribute('fill-opacity', set.has(i) ? '0.95' : '0.18');
    }
    s.txtPx(8, s.Y(rowY(f + 1)) + 4, '第 ' + (f + 1) + ' 次', { cls: 'axlab' }, g);
  });
  s.txtPx(s.X(0), s.H - 8, '資料索引 0 → 39（依類別排序）', { cls: 'axlab' }, g);
  const never = count.filter(c => c === 0).length, multi = count.filter(c => c > 1).length;
  const props = tests.map(te => HC.fmt(te.filter(i => w05splitY[i] === 1).length / te.length, 2));
  w05splitTx('w05splitName', names[kind]);
  w05splitTx('w05splitSize', tests.map(t => t.length).join('、'));
  w05splitTx('w05splitNever', String(never));
  w05splitTx('w05splitMulti', String(multi));
  w05splitTx('w05splitProp', props.join('、'));
  const msg = [
    '不洗牌的 KFold 依原順序切，前三折只有類別 0、後兩折只有類別 1，驗證折和訓練資料的分布完全不同。',
    '先洗牌一次再切成互斥的 5 折：每筆恰好驗證一次，各折類別比例接近整體，但仍有隨機起伏。',
    '分層後每一折的類別比例都接近整體的 0.40，每筆仍恰好驗證一次。',
    'ShuffleSplit 每次獨立抽 8 筆驗證：有 ' + never + ' 筆從未被驗證、' + multi + ' 筆被驗證兩次以上，各次驗證集可以重疊。',
  ][kind];
  setStatus('w05splitStatus', msg);
}
function w05splitTx(id, t) { const e = $(id); if (e) e.textContent = t; }

/* ---------- P07 母體模擬 vs bootstrap（baked）---------- */
function w05simDraw() {
  const F = FRAMES_w05sim;
  const labels = F.edges.slice(0, -1).map((e, i) => HC.fmt((e + F.edges[i + 1]) / 2, 2));
  HC.bar('w05simChart', {
    labels,
    datasets: [
      { label: '從母體重抽 1000 次的 α̂', data: F.simHist, backgroundColor: HC.tok.c, borderRadius: 2 },
      { label: 'Portfolio 的 1000 個 bootstrap α̂*', data: F.bootHist, backgroundColor: HC.tok.accent2, borderRadius: 2 },
    ],
  }, {
    scales: { x: { title: { display: true, text: 'α̂' } }, y: { title: { display: true, text: '次數' } } },
  });
  $('w05simMean').textContent = HC.fmt(F.simMean, 4);
  $('w05simSD').textContent = HC.fmt(F.simSD, 4);
  $('w05simBMean').textContent = HC.fmt(F.bootMean, 4);
  $('w05simBSD').textContent = HC.fmt(F.bootSD, 4);
  setStatus('w05simStatus', '母體模擬的標準差 ' + HC.fmt(F.simSD, 3) + '，bootstrap 的標準差 '
    + HC.fmt(F.bootSD, 3) + '：中心不同，寬度相近。');
}

/* ---------- P07 Bootstrap 抽樣器：全程使用 Portfolio 的 alpha_hat ---------- */
let w05bootStats = [];
function w05bootRand() {
  w05bootRand.seed = (w05bootRand.seed || 0) + 1;
  return HC.stat.lcg(20260810 + w05bootRand.seed * 7919);
}
function w05bootOne() {
  const F = FRAMES_w05boot, rand = w05bootRand(), n = F.n;
  const counts = new Array(n).fill(0), drawn = [];
  for (let i = 0; i < n; i++) {
    const j = Math.floor(rand() * n); counts[j]++; drawn.push(j);
  }
  const xs = drawn.map(i => F.x[i]), ys = drawn.map(i => F.y[i]);
  const mx = HC.stat.mean(xs), my = HC.stat.mean(ys);
  let sx = 0, sy = 0, sxy = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx, dy = ys[i] - my;
    sx += dx * dx; sy += dy * dy; sxy += dx * dy;
  }
  const stat = (sy - sxy) / (sx + sy - 2 * sxy);
  return { counts, drawn, stat };
}
function w05bootRender(d) {
  const host = $('w05bootSvg');
  if (!d) {
    host.textContent = '尚未重抽。按「抽一次」後會顯示 Portfolio 的抽樣索引摘要。';
    return;
  }
  const unique = d.counts.filter(c => c > 0).length;
  const repeated = d.counts.filter(c => c > 1).length;
  host.innerHTML = '<strong>這次的前 24 個索引：</strong> '
    + d.drawn.slice(0, 24).join(', ') + ' …<br>'
    + '<strong>不同原始觀測：</strong>' + unique + ' / ' + d.counts.length
    + '　<strong>重複出現的觀測：</strong>' + repeated
    + '　<strong>OOB：</strong>' + (d.counts.length - unique);
}
function w05bootHist() {
  if (!w05bootStats.length) return;
  const lo = Math.min(...w05bootStats) - 0.01, hi = Math.max(...w05bootStats) + 0.01, bins = 20;
  const h = new Array(bins).fill(0);
  w05bootStats.forEach(v => {
    const b = Math.min(bins - 1, Math.max(0, Math.floor((v - lo) / (hi - lo) * bins)));
    h[b]++;
  });
  HC.bar('w05bootChart', {
    labels: h.map((_, i) => HC.fmt(lo + (hi - lo) * (i + 0.5) / bins, 1)),
    datasets: [{ label: 'Portfolio α̂* 的分佈', data: h,
                 backgroundColor: 'rgba(44,62,122,.72)', borderRadius: 3 }],
  }, {
    plugins: { legend: { display: false } },
    scales: { x: { title: { display: true, text: 'α̂*（這次 Portfolio bootstrap 樣本）' } },
              y: { title: { display: true, text: '次數' } } },
  });
}
function w05bootUpdate(d) {
  w05bootStats.push(d.stat);
  $('w05bootDraw').textContent = d.drawn.slice(0, 12).join(', ') + ' …';
  const nOob = d.counts.filter(c => c === 0).length;
  $('w05bootOob').textContent = nOob + ' 筆（' + HC.pct(nOob / d.counts.length, 0) + '）';
  $('w05bootStat').textContent = HC.fmt(d.stat, 3);
  $('w05bootB').textContent = String(w05bootStats.length);
  $('w05bootSE').textContent = w05bootStats.length > 1
    ? HC.fmt(HC.stat.sd(w05bootStats), 4) : '—';
  setStatus('w05bootStatus', '第 ' + w05bootStats.length + ' 次重抽：'
    + nOob + ' 筆完全沒被抽到，這次的 α̂* 是 ' + HC.fmt(d.stat, 4)
    + '。累計 ' + w05bootStats.length + ' 次的標準差 = '
    + (w05bootStats.length > 1 ? HC.fmt(HC.stat.sd(w05bootStats), 4) : '—')
    + '；原始 100 筆資料的 α̂ = ' + HC.fmt(FRAMES_w05boot.alphaHat, 4) + '。');
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

/* ---------- 啟動 ----------
   規則：SVG 元件的初始化一律放在 HC.ready() 外面。
   Chart.js 從 CDN 載不到時 HC.ready() 不會執行，若把 SVG 初始化放進去，
   手寫的 SVG 元件會跟著一起死掉——那就白費了「單檔自足」的設計。
   HC.bar / HC.line 在 Chart 未載入時本來就安全地回傳 null。 */
w05bootReset();
w05splitSetup();
w05splitShow(0);
HC.onDetail('w05-detail-shuffle', { open: () => { w05splitShow(0); } });
HC.ready(() => {
  w05valDraw();
  w05cvDraw();
  w05misShow();
  w05simDraw();
});
/* 詞彙卡由 tools/inject_data.py 在 DATA 區段內呼叫 HC.initFlashcards()，
   資料一定要先於初始化，所以這裡不呼叫。 */
"""


# Approved reading-flow organization; keep all source-backed detail content.
from reading_flow_ch1_6 import organize
BODIES, PAGEJS = organize(5, BODIES, PAGEJS)

if __name__ == "__main__":
    apply("resampling_methods", BODIES, PAGEJS, frames())
