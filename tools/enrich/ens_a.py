"""集成各節 A：why（投票與基學習器）、bagging、rf、importance。

由 ensemble_deepen.augment 呼叫；old 是上游各層跑完的 BODIES 快照。
抽球元件（w09bagSvg）與重要度圖（w09vimpChart）從 old 取出，id 不變，JS 沿用；
抽球元件的理論值改成 n = 20 的有限樣本值 (1−1/20)²⁰（patch_js）。
"""
from ens_common import detail, grab_viz, info, lab, links, proof, qa, quiz, table

SECS = ["why", "bagging", "rf", "importance"]


def fill(tpl, *parts):
    """把 [[0]]、[[1]]… 換成 parts；模板用 raw string，LaTeX 的大括號與反斜線不必跳脫。"""
    for i, p in enumerate(parts):
        k = f"[[{i}]]"
        if tpl.count(k) != 1:
            raise ValueError("模板佔位錯誤：" + k)
        tpl = tpl.replace(k, p)
    return tpl
JS = ""


# ══ why：投票與基學習器 ═══════════════════════════════════════════════════
def _why():
    vote_table = table(
        ["方法", "需要的基學習器", "為什麼", "常見選擇"],
        [["Bagging／random forest", "低偏差、高變異、資料一動就變的模型",
          "平均只壓變異、不動偏差，所以成員一開始就要夠有彈性", "長很深、不剪枝的樹"],
         ["Boosting", "簡單、偏差大但變異小的弱學習器（weak learner）",
          "每一步只修正一小塊還沒解釋的部分，序列地降低偏差", "stump 或淺樹"],
         ["投票／stacking", "各自夠準、但錯在不同地方的模型",
          "成員的錯誤不重疊，合併時才互相抵銷", "邏輯斯迴歸、K 近鄰、SVM、樸素貝氏、樹，混著用"]])

    voting_detail = detail("w09-detail-voting-probability", "硬投票、軟投票、權重與機率校準", r"""
<p><strong>兩種規則的式子。</strong>設有 $M$ 個分類器，$h_j(x)$ 是第 $j$ 個的預測類別，$\hat p_{jk}(x)$ 是它給類別 $k$ 的機率。</p>
$$\text{硬投票：}\ \hat y=\arg\max_k\sum_{j=1}^M I\big(h_j(x)=k\big),\qquad
\text{軟投票：}\ \hat y=\arg\max_k\sum_{j=1}^M w_j\,\hat p_{jk}(x).$$
<p>軟投票的權重 $w_j$ 預設相等；scikit-learn 的 <code>VotingClassifier(weights=…)</code> 讓你自己指定。硬投票平手時，scikit-learn 依類別標籤的排序挑第一個。</p>
<p><strong>為什麼平均機率通常比數票好。</strong>ESL 第 8.7 節舉過一個例子：某個 $x$ 真正屬於類別 1 的機率是 0.75，但每棵樹都預測類別 1。這時「投給類別 1 的比例」是 1，完全看不出那 25% 的不確定。改成平均各樹葉子裡的類別比例，得到的數字比較接近真正的機率，而且樹的棵數少時變異也比較小。scikit-learn 的 random forest 分類器用的就是平均機率。</p>
<p><strong>軟投票的前提是機率可信。</strong>不同模型輸出的機率尺度不一樣，有的偏極端、有的擠在 0.5 附近；直接平均時，最敢講話的模型會主導結果。scikit-learn 的文件建議只在<strong>校準良好</strong>（well-calibrated）的分類器之間用軟投票，必要時先用 <code>CalibratedClassifierCV</code> 校準。「有 <code>predict_proba</code>」不代表數值可靠。</p>
<p><strong>和 stacking 的關係。</strong>ESL 第 8.8 節把等權平均稱為委員會（committee）方法。加權軟投票是同一件事，只是權重由人指定；<a href="#stacking">stacking</a> 則用折外預測<strong>從資料學</strong>權重，ESL 建議把權重限制成非負、總和為 1。所以三者是一條線：等權 → 人給權重 → 資料學權重，愈往後愈有彈性，也愈需要資料與獨立驗證。</p>""")

    bad_detail = detail("w09-detail-why-bad", "反例：0-1 損失下，bagging 一個很差的分類器會更差", r"""
<p>平方損失下，ESL 第 8.7 節證明了「理想的聚合」不會增加均方誤差：令 $f_{\rm ag}(x)=E_P\hat f^*(x)$ 是從真實母體 $P$ 重複抽訓練集、再平均的結果，則</p>
$$E_P\big[Y-\hat f^*(x)\big]^2=E_P\big[Y-f_{\rm ag}(x)\big]^2+E_P\big[\hat f^*(x)-f_{\rm ag}(x)\big]^2\ \ge\ E_P\big[Y-f_{\rm ag}(x)\big]^2 .$$
<p>平均拿掉的正好是第二項，也就是變異。注意這是對「從母體抽樣」的理想聚合成立；實際的 bagging 從同一份訓練資料重抽，書上只說這<strong>暗示</strong>它通常也會降低均方誤差，不是保證。</p>
<p>分類的 0-1 損失沒有這種分解。ESL 的反例：真實類別永遠是 1；某個分類器有 0.4 的機率把所有點都判成 1、0.6 的機率全判成 0，所以單獨用時錯誤率是 0.6。把很多份這樣的分類器拿來投票，多數票幾乎一定是 0，錯誤率變成 1.0。</p>
<p>這就是開頭硬幣例子的反面：每個成員答對的機率低於一半時，投票會把劣勢放大。結論和硬幣一樣，只是方向相反：投票只放大成員原本的傾向。</p>""")

    lab_detail = detail("w09-detail-why-lab", "Lab：Carseats 上的硬投票",
        lab("三個不同演算法的硬投票，與各自的 5 折交叉驗證準確率", 238, 238, start="clf1 =",
            note="輸出最後一列的標籤寫成 <code>StackingClassifier</code>，那是 lab 迴圈裡標籤沿用了下一格的名字；"
                 "這一列其實是硬投票 <code>vclf</code> 的結果。四個模型用同一組 <code>kf5</code> 折，所以可以直接比較："
                 "投票的 0.82 高於單一模型最好的 0.79。")
        + r"""<p>同一份資料上 stacking 的結果放在 <a href="#stacking">Stacking 一節</a>。準確率差個 0.01–0.03，對照括號裡的標準差，差距並不大；這個例子用來看流程，排名不足為據。</p>""")

    q = quiz("qWhy", "QUIZ · 投票與基學習器",
        "三個分類器對同一筆資料給「類別 1」的機率分別是 0.9、0.45、0.45。硬投票與軟投票各會預測哪一類？",
        [(True, "硬投票選類別 0，軟投票選類別 1",
          "對。後兩個分類器都以 0.45 略偏向類別 0，硬投票兩票對一票選 0；軟投票平均 (0.9+0.45+0.45)/3 = 0.6，大於 0.5，所以選 1。軟投票保留了第一個分類器「非常確定」的資訊。"),
         (False, "兩者都選類別 1，因為有一個分類器非常確定",
          "硬投票只數每個分類器的最終標籤，不看它有多確定；有 0.9 的把握和只有 0.55 的把握，在硬投票裡都只算一票。"),
         (False, "兩者都選類別 0，因為多數分類器偏向 0",
          "軟投票平均的是機率，不是票數。0.9 拉高了平均，平均 0.6 會選類別 1。")])

    return fill(r"""<p><a href="#motive">開頭的硬幣</a>說明了投票什麼時候有用：成員各自比瞎猜好，而且<strong>錯的地方不一樣</strong>。ESL 第 16.1 節把集成學習拆成兩件事：先造出一群<strong>基學習器</strong>（base learner），再決定怎麼把它們<strong>合併</strong>。後面每一節都是在回答這兩個問題的不同組合，對照表在<a href="#motive">路線圖</a>。這一節先看最直接的答案：合併的規則固定不變，多樣性來自<strong>用不同的演算法</strong>。</p>
<h3>硬投票與軟投票</h3>
<p><strong>硬投票</strong>（hard voting）讓每個分類器投一票，票多的類別勝出。<strong>軟投票</strong>（soft voting）平均各分類器給每一類的機率，再挑機率最大的那一類。兩者多半會選同一類，但不一定。三個分類器給「類別 1」的機率是 0.51、0.52、0.01 時，硬投票兩票對一票選類別 1；軟投票的平均是 (0.51+0.52+0.01)/3 ≈ 0.347，選類別 0。前兩個只是勉強偏向 1，第三個卻非常確定是 0，軟投票把「有多確定」也算進去了。</p>
[[0]]
[[1]]
<h3>基學習器怎麼挑</h3>
<p>答案取決於合併的方式要對付什麼：</p>
[[2]]
<p>不是每種模型都適合拿去平均。bagging 只對<strong>不穩定</strong>的估計有用：資料換一點、結果就大變的方法，平均起來才有東西可以壓。樣本平均這類線性統計量，bagging 之後幾乎不變（ESL 習題 15.4）；ESL 也提到 K 近鄰這類較穩定的方法通常不太受 bagging 影響。反過來，boosting 的基學習器若是線性模型，一路加起來還是線性模型，學不到新的形狀。</p>
<p>所以實務上兩邊都用樹。樹可以處理混合型態的變數、不必標準化、自己長出交互作用，而且只要調深度，就能從「很深、低偏差」一路調到「只切一刀的 stump」，同一種基學習器同時符合 bagging 與 boosting 的需求。投票和 stacking 則反過來，刻意混用不同演算法，讓錯誤不要重疊。</p>
[[3]]
[[4]]
[[5]]
[[6]]""",
        info("📌 軟投票的代價", "要平均的是機率，所以各模型的機率要可信（校準過）。硬投票只需要標籤，對機率尺度不敏感。式子、權重與校準的細節在下方收合。"),
        voting_detail,
        vote_table,
        bad_detail,
        lab_detail,
        q,
        links([("https://math.stackexchange.com/questions/4363939/how-did-you-get-75-and-97-with-which-formula", "多數決 75% 與 97% 的算法"),
        ("https://scikit-learn.org/stable/modules/ensemble.html", "scikit-learn 集成方法：投票與 stacking")]))


# ══ bagging ════════════════════════════════════════════════════════════════
def _bagging(old):
    bag_viz = grab_viz(old["bagging"], "w09bagSvg")
    bag_viz = _patch_bag_html(bag_viz)

    overfit_detail = detail("w09-detail-bag-overfit", "加樹為什麼不會過度擬合：蒙地卡羅極限與它的限制", r"""
<p><strong>B 只是蒙地卡羅的樣本數。</strong>給定訓練資料，bootstrap 是一個隨機機制；ESL 第 8.7 節把「真正的」bagging 估計寫成對這個機制取期望值 $E_{\hat P}\hat f^*(x)$，$\hat P$ 是訓練資料的經驗分佈。我們用的</p>
$$\hat f_{\rm bag}(x)=\frac1B\sum_{b=1}^B\hat f^{*b}(x)$$
<p>只是這個期望值的蒙地卡羅估計。$B$ 愈大，估計愈接近那個固定的極限；模型的形狀由每棵樹多深、資料是什麼決定，和 $B$ 無關。random forest 也一樣，ESL 第 15.3.4 節寫成</p>
$$\hat f_{\rm rf}(x)=E_\Theta T(x;\Theta)=\lim_{B\to\infty}\hat f^{B}_{\rm rf}(x),$$
<p>$\Theta$ 代表一棵樹的隨機性（抽到哪些樣本、每個節點抽到哪些變數）。所以「$B$ 加大」不會讓模型更會記住訓練資料，只會讓平均更穩。這和 boosting 不同：boosting 每多一棵樹，模型就多一塊可以擬合雜訊的彈性。</p>
<p><strong>但極限本身可能過度擬合。</strong>ESL 同一節接著說：完全長滿的樹平均起來可能是一個太複雜的模型，帶有不必要的變異。這時要調的是每棵樹的深度或葉子大小，不是 $B$。ESL 的經驗是用長滿的樹通常損失不大，還少一個要調的參數；分類問題對這件事更不敏感。</p>
<p><strong>直覺版。</strong>請很多人各自猜一個數字再平均：多找幾個人，只會讓平均更穩，不會讓平均更愛鑽牛角尖。可是如果每個人都把同一份考古題背得滾瓜爛熟，他們的平均也一樣只會背考古題。前者是 $B$，後者是每棵樹的深度與資料本身。</p>""")

    oob_detail = detail("w09-detail-oob-loocv", "OOB 為什麼接近 LOOCV：條件與限度", r"""
<p><strong>先看 OOB 預測用了哪些樹。</strong>第 $i$ 筆資料不在某份 bootstrap 樣本裡的機率是 $(1-1/n)^n$，所以 $B$ 棵樹裡大約有 $(1-1/n)^nB\approx0.37B$ 棵沒看過它。第 $i$ 筆的 OOB 預測就是這些樹的平均（或投票）。</p>
<p><strong>再看這些樹是怎麼來的。</strong>在「第 $i$ 筆沒被抽到」的條件下，這份 bootstrap 樣本等於從<strong>其餘 $n-1$ 筆</strong>有放回地抽 $n$ 次。所以這些樹全都沒有用到第 $i$ 筆，而 $B$ 很大時，它們的平均會接近「只用其餘 $n-1$ 筆做 bagging」的預測。這正是 LOOCV 對第 $i$ 筆做的事：拿掉它、用其他資料訓練、再預測它。</p>
<p><strong>兩本書都只給結論。</strong>ISLP 說 $B$ 夠大時 OOB 誤差「幾乎等於」LOOCV 誤差，ESL 說它和 $N$ 折交叉驗證幾乎相同並留作習題 15.2；兩者都沒有在正文證明。上面的論證說明了方向，也看得出兩個差別：OOB 那邊每份樣本抽 $n$ 次，LOOCV 的 bagging 若照常抽 $n-1$ 次，兩者的訓練規則就不完全相同；每筆的 OOB 預測只用了約 $0.37B$ 棵樹，所以 $B$ 要夠大，蒙地卡羅的誤差才會小。</p>
<p><strong>用 OOB 時要小心的事。</strong></p>
<ul>
<li>OOB 只排除了「這筆資料參與這棵樹的訓練」。若在切分之前就用全部資料做了目標編碼、變數篩選或其他用到 $y$ 的前處理，OOB 不會替你排除這些洩漏。</li>
<li>同一位病人有多筆記錄時，另一筆可能仍在樹裡；OOB 不保證同一群組的資料分開。</li>
<li>反覆挑 OOB 分數最好的超參數，被挑中那組的 OOB 誤差會偏樂觀（第 5 章的選擇偏差）。最後回報的誤差仍要來自沒參與選參的資料。</li>
<li>OOB 需要有袋外樣本。照 ISLP 演算法 8.2 做的 boosting 每棵樹都看全部資料，沒有 OOB；但每輪只用一部分資料的隨機梯度提升（stochastic gradient boosting）就有，scikit-learn 會給 <code>oob_improvement_</code>，不過官方文件說這個估計通常偏悲觀，建議改用交叉驗證。</li>
</ul>""")

    lab_detail = detail("w09-detail-bagging-lab", "Lab：Boston 上的 bagging",
        lab("Bagging：每次分裂都看全部 12 個變數的 random forest", 64, 64)
        + lab("測試集 MSE", 66, 66)
        + lab("樹加到 500 棵", 68, 68,
              note="從 100 棵（預設）加到 500 棵，測試 MSE 只從 14.63 變成 14.61：平均早就穩定了，再加樹只多花計算時間。")
        + r"""<p><code>RandomForestRegressor</code> 把 <code>max_features</code> 設成變數個數時，每次分裂都能看全部變數，就是 bagging。lab 用同一個函式做 bagging 和下一節的 random forest，差別只在這一個參數。</p>""")

    qas = qa("觀念釐清", [
        ("Q：Bagging 為什麼能降變異，卻幾乎不降偏差？",
         r"""<p>固定 $x$，考慮重複訓練造成的變動。每棵 bootstrap 樹的預測分佈都一樣，期望值都是 $\mu(x)$；平均 $B$ 棵之後，期望值還是 $\mu(x)$，所以偏差 $\mu(x)-f(x)$ 和單棵 bootstrap 樹相同（ESL 第 15.2 節：唯一的改善來自降低變異）。變異則會下降，但只能壓掉樹與樹之間不相關的部分，共同的 $\rho\sigma^2$ 留下來，這是下一節 random forest 要對付的。</p>
<p>所以要拿去平均的，是偏差小、變異大的東西。長很深、不剪枝的樹正是這樣：彈性大、偏差小，資料一換就長成另一棵。反過來，把每棵樹都剪成三個葉子再平均，偏差還是那麼大。</p>"""),
        ("Q：既然有 OOB 誤差，還需要交叉驗證嗎？",
         r"""<p>只是要估 bagging 或 random forest 本身的測試誤差時，OOB 就夠了，而且擬合一次就順便拿到，不必像 $k$ 折那樣擬合 $k$ 次。需要交叉驗證或獨立驗證集的情況有三種：拿誤差去挑超參數（挑完要另外估）；前處理用到了 $y$（要把前處理關在折裡）；以及沒有袋外樣本的方法，例如每棵樹都用全部資料的 boosting。細節在上方「OOB 為什麼接近 LOOCV」收合。</p>""")])

    q = quiz("qBag", "QUIZ · Bagging 與 OOB",
        "Lab 把 bagging 的樹從 100 棵加到 500 棵，測試 MSE 只從 14.63 變成 14.61。最合理的解讀是？",
        [(True, "平均已經穩定了；加樹只讓平均更接近它的極限，不會增加模型的彈性，所以挑一個大到誤差已經平掉的 B 就好",
          "對。B 是蒙地卡羅的樣本數，加大只讓平均更穩。要改變模型本身，得調每棵樹的深度、葉子大小或每次分裂可用的變數數。"),
         (False, "這表示 bagging 已經開始過度擬合，應該把 B 調回 100",
          "bagging 的 B 加大不會讓模型更會記住訓練資料；誤差持平代表平均已經收斂，不是過度擬合的跡象。"),
         (False, "這表示每棵樹太深，應該先用交叉驗證幫每棵樹剪枝",
          "bagging 刻意用不剪枝的深樹，讓每棵樹偏差小，再靠平均壓變異。B 加大誤差不變，和樹要不要剪無關。")])

    return fill(r"""<p>回到樹。單棵樹的問題是變異太大：把訓練資料隨機切成兩半各長一棵，兩棵可能完全不像。降低變異最古典的辦法是平均：$n$ 個獨立、變異都是 $\sigma^2$ 的觀測，平均的變異是 $\sigma^2/n$。所以理想的做法是蒐集 $B$ 份獨立的訓練資料，各擬合一棵樹，再把預測平均起來。</p>
<p>問題是我們只有一份資料。那就用第 5 章的 <strong>bootstrap</strong>：從 $n$ 筆訓練資料有放回地抽 $n$ 筆，重複 $B$ 次，造出 $B$ 份訓練資料。在每一份上長一棵樹，再平均，這就是 <strong>bootstrap aggregation</strong>，簡稱 <strong>bagging</strong>：</p>
$$\hat f_{\rm bag}(x)=\frac1B\sum_{b=1}^B\hat f^{*b}(x),$$
<p>其中 $\hat f^{*b}$ 是用第 $b$ 份 bootstrap 樣本長出來的樹。bootstrap 本來是用來<strong>估計</strong>一個估計量有多不穩；bagging 用同一個程序來<strong>降低</strong>它。它沒有製造新的資訊：每份 bootstrap 樣本平均只含約 63% 的不同觀測。</p>
<p>分類問題有兩種合併方式：每棵樹投一票、票多的類別勝出，或平均每棵樹給各類的機率。講義與 ISLP 用投票；scikit-learn 的 random forest 平均機率，ESL 也指出平均機率在樹少時變異較小。</p>
<p><strong>bagging 的樹要長很深，而且不剪枝。</strong>這和剪枝那一節的直覺相反，但道理一致：每棵樹偏差小、變異大，平均把變異壓下來，而偏差在平均時不會變。所以 bagging 主要治變異，幾乎不治偏差；平均多少棵樹的效果還受樹與樹之間的相關限制，見<a href="#w09-detail-rho-floor">開頭那節的收合</a>。</p>
<h3>袋外樣本：免費的驗證集</h3>
<p>有放回抽 $n$ 次，某一筆始終沒被抽到的機率是</p>
$$\left(1-\frac1n\right)^n\ \xrightarrow[n\to\infty]{}\ e^{-1}\approx0.368 .$$
<p>所以每棵樹大約只用到三分之二的資料，剩下沒用到的叫做<strong>袋外樣本</strong>（out-of-bag, OOB）。對這棵樹來說，它們是沒看過的資料。$n$ 不大時這個比例略低：$n=20$ 時是 $0.95^{20}\approx35.85\%$，$n=100$ 時是 36.60%。</p>
[[0]]
<p><strong>OOB 誤差怎麼算。</strong>對第 $i$ 筆，找出所有沒用到它的樹（大約 $B/3$ 棵），用它們預測第 $i$ 筆再平均（或投票），得到它的 OOB 預測；$n$ 筆都做一次，就得到 OOB 誤差。因為每筆都只由沒看過它的樹預測，ISLP 說這是 bagging 測試誤差的有效估計，而且 $B$ 夠大時它幾乎等於 LOOCV 誤差，成本卻只有一次擬合。這個「幾乎等於」要在什麼條件下才成立，見下方收合。</p>
<h3>樹要種幾棵</h3>
<p>講義與 ISLP 都說：$B$ 不是關鍵的參數，用很大的 $B$ 也不會過度擬合。原因是加樹並沒有增加模型的彈性，只是把「無限多棵樹的平均」估得更準；實務上挑一個大到誤差已經平掉的 $B$ 就好。不過這不表示 bagging 不會過度擬合：如果每棵樹本身長得太複雜，它們的平均也可能太複雜，這時要調的是樹，不是 $B$。</p>
<p>ISLP 圖 8.8 用 Heart 資料畫出誤差隨 $B$ 下降、然後平掉的樣子，還有三個細節：虛線是單棵分類樹的測試誤差；random forest 那條用 $m=\sqrt p$；兩條 OOB 誤差在這張圖裡明顯比測試誤差低，ISLP 說這只是碰巧。</p>
[[1]]
[[2]]
[[3]]
[[4]]
[[5]]
[[6]]""",
        bag_viz,
        overfit_detail,
        oob_detail,
        lab_detail,
        qas,
        q,
        links([("https://dafriedman97.github.io/mlbook/content/c6/s1/bagging.html", "Bagging 的流程"),
        ("https://online.stat.psu.edu/stat414/lesson/24/24.4", "樣本平均數的變異"),
        ("https://yuhangzhou88.github.io/ESL_Solution/", "ESL 習題解答（含習題 15.1 的相關平均變異）"),
        ("https://scikit-learn.org/stable/modules/ensemble.html", "scikit-learn 的 bagging 與 OOB 分數")]))


def _patch_bag_html(v):
    reps = [
        ('data-source-note="n=20 的固定種子 bootstrap 重抽；累計 OOB 比例與 1/e 理論值即時計算。"',
         'data-source-note="n=20 的固定種子 bootstrap 重抽；累計 OOB 比例與有限樣本理論值 (1−1/20)²⁰ 即時計算。"'),
        ('<span class="ic-label">理論值 1/e</span><span class="ic-value" id="w09bagTheory">36.79%</span>',
         '<span class="ic-label">理論值 (1−1/20)²⁰</span><span class="ic-value" id="w09bagTheory">35.85%</span>'),
        ("按幾十次，右邊的累計 OOB 比例就會定在 36.8% 附近。",
         "按幾十次，右邊的累計 OOB 比例會靠近 35.85%，也就是 $n=20$ 時的 $(1-1/20)^{20}$；資料筆數很大時才趨近 $1/e\\approx36.8\\%$。"),
        ("<strong>B 夠大時它幾乎等於 LOOCV 誤差</strong>，但成本只有一次擬合。",
         "ISLP 說 <strong>B 夠大時它幾乎等於 LOOCV 誤差</strong>，但成本只有一次擬合。"),
    ]
    for a, b in reps:
        if v.count(a) != 1:
            raise ValueError("bagging 元件比對失敗：" + a[:40])
        v = v.replace(a, b)
    # 「OOB 誤差怎麼算」側卡與正文重複，只留正文
    k = v.find("OOB 誤差怎麼算")
    a = v.rfind('<div class="info-card">', 0, k)
    from ens_common import _div_block
    z = _div_block(v, a)
    return v[:a] + v[z:]


def patch_js(js):
    reps = [
        ("+ HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) + '  ·  理論值 36.79%');",
         "+ HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) + '  ·  理論值 (1−1/20)²⁰ = 35.85%');"),
        ("+ HC.pct(w09bagOobSum / w09bagB / w09bagN, 2) + '，理論值 1/e ≈ 36.79%。');",
         "+ HC.pct(w09bagOobSum / w09bagB / w09bagN, 2)\n"
         "    + '；20 筆資料時的理論值是 (1−1/20)²⁰ ≈ 35.85%，資料筆數很大時才趨近 1/e ≈ 36.79%。');"),
    ]
    for a, b in reps:
        if js.count(a) != 1:
            raise ValueError("bagging JS 比對失敗：" + a[:40])
        js = js.replace(a, b)
    return js


# ══ rf：Random Forest ═════════════════════════════════════════════════════
def _rf(old):
    levels = table(
        ["做法", "抽樣本（列）", "抽變數（欄）", "在哪裡抽變數"],
        [["Pasting", "不放回抽一部分", "—", "—"],
         ["Bagging", "bootstrap", "—", "—"],
         ["Random subspace", "—", "抽一部分", "每棵樹開始前抽一次，整棵樹都用這組"],
         ["Random patches", "抽一部分", "抽一部分", "每棵樹開始前抽一次"],
         ["Random forest", "bootstrap", "抽 $m$ 個", "<strong>每個節點</strong>重新抽"],
         ["Extra-trees", "預設不抽（scikit-learn）", "抽 $m$ 個", "每個節點重新抽，切點也隨機產生"]])

    m_detail = detail("w09-detail-rf-m", "m 的取捨：相關變低、偏差變高", r"""
<p><strong>ESL 的變異分解。</strong>ESL 第 15.4 節把 random forest 在固定 $x$ 的預測變異寫成</p>
$$\operatorname{Var}\hat f_{\rm rf}(x)=\rho(x)\,\sigma^2(x),$$
<p>$\sigma^2(x)$ 是單棵隨機樹預測的變異，$\rho(x)$ 是<strong>同一份訓練資料長出來的兩棵樹</strong>在 $x$ 的相關。這個相關是對「換一份訓練資料、重新訓練」而言的理論量，不是拿一座已經長好的森林、去算樹與樹的預測相關；給定訓練資料時，兩棵樹的隨機抽樣彼此獨立（ESL 習題 15.5）。$m$ 變小時，$\rho(x)$ 下降（ESL 圖 15.9），平均的變異跟著下降。</p>
<p><strong>代價是偏差。</strong>每次分裂能挑的變數變少，常常挑不到最好的那個，所以單棵樹的偏差上升，整座森林的偏差也跟著上升（ESL 第 15.4.2 節）。ESL 的結論是：bagging 與 random forest 的改善完全來自降低變異；$m$ 的選擇是偏差與變異的取捨，和 ridge 迴歸的懲罰參數類似。</p>
<p><strong>相關變數少時，小 $m$ 會失手。</strong>如果 $p$ 個變數裡只有 $r$ 個有用，一個節點的 $m$ 個候選裡至少有一個有用變數的機率是 $1-\binom{p-r}{m}\big/\binom{p}{m}$。ESL 第 15.3.4 節的例子：2 個有用變數加 100 個雜訊變數、$m=\lfloor\sqrt{102}\rfloor=10$ 時，這個機率只有 0.19；6 個有用變數加 100 個雜訊、$m=10$ 時是 0.46。大部分的分裂都只能在雜訊裡挑，表現就會變差。</p>
<p><strong>預設值只是起點。</strong>ESL 說 random forest 的發明者建議：分類用 $m=\lfloor\sqrt p\rfloor$、最小節點大小 1；迴歸用 $m=\lfloor p/3\rfloor$、最小節點大小 5，並且明說這些值應該當成調整參數；它的 California housing 例子裡 $m=6$ 遠好於預設的 2。scikit-learn 稱這些是「經驗上不錯的預設」，分類器預設 <code>max_features='sqrt'</code>，迴歸器預設 <code>1.0</code>（也就是 bagging），並提醒最好的參數要用交叉驗證挑。沒有任何一本書推導出 $\sqrt p$。</p>""")

    proof_var = proof("w09proof-forest-var", "平均樹的變異與相關性", r"""
<p>固定預測位置 $x$。設各棵樹的預測 $T_1,\dots,T_B$ 變異都是 $\sigma^2$、兩兩相關都是 $\rho$，則</p>
$$\operatorname{Var}\Big(\frac1B\sum_{b=1}^BT_b\Big)=\frac1{B^2}\Big\{B\sigma^2+B(B-1)\rho\sigma^2\Big\}=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2 .$$
<p>第一個等號是把變異展開成 $B$ 個變異項加 $B(B-1)$ 個共變異項，每個共變異都是 $\rho\sigma^2$。只有第二項隨 $B$ 消失。這裡的 $\sigma^2$ 與 $\rho$ 是對重複訓練而言的量；跨測試點算出來的相關係數不能代進來。</p>""")

    xt_detail = detail("w09-detail-extra-trees", "隨機化的層次：random subspace、random patches 與 Extra-trees", r"""
<p><strong>變數在哪裡抽，結果不一樣。</strong>依 Louppe 與 Geurts 的整理，Ho（1998）的 random subspace 在每棵樹開始前抽一組變數，整棵樹都只用這組。Louppe 與 Geurts（2012）的 random patches 同時抽樣本與變數，也是整棵樹抽一次；他們的論文特別指出，這和 random forest、Extra-trees「在<strong>每個節點</strong>重新抽變數」不同。舉例來說，三個變數裡每棵樹固定只看其中兩個，是 subspace；同一棵樹的根節點看 $\{X_1,X_2\}$、它的子節點換成 $\{X_2,X_3\}$，才是 random forest。scikit-learn 的 <code>BaggingClassifier(max_features=…)</code> 抽的是「每個基學習器用幾個變數」，所以它做出來的是 subspace，不是 random forest。</p>
<p>Random patches 的原始動機是記憶體：資料大到放不進記憶體時，每棵樹只讀一小塊。它們在 29 個資料集上的實驗發現，抽變數對準確度很重要，只抽樣本的 pasting 常常效果很差；不過這是那組資料與調參方式下的結果，不是一般定理。</p>
<p><strong>Extra-trees。</strong>極端隨機樹（extremely randomized trees）和 random forest 一樣在每個節點抽候選變數，但不去搜尋每個變數的最佳門檻值，而是替每個候選變數<strong>隨機產生一個門檻值</strong>，再從這些隨機切點裡挑最好的。scikit-learn 文件說這通常能再降一點變異，代價是偏差稍微再增加；搜尋門檻值的計算也省下來了。scikit-learn 的 <code>ExtraTreesClassifier</code> 預設 <code>bootstrap=False</code>，每棵樹看全部樣本，所以預設沒有 OOB。</p>
<p>ESL 的文獻註記提到，「random forest」這個名稱最早由 Ho（1995）提出，指的是在隨機子空間裡長樹再取共識。</p>""")

    lab_detail = detail("w09-detail-rf-lab", "Lab：Boston 上的 random forest",
        lab("每次分裂只看 6 個變數", 70, 70,
            note="測試 MSE 20.04，比上一節 bagging 的 14.63 還差。這份資料、這個切分下，限制變數反而吃虧；$m$ 要拿驗證資料挑，不能預設愈小愈好。")
        + r"""<p>lab 也提醒了預設值的差別：<code>RandomForestRegressor()</code> 預設每次分裂看全部變數（等於 bagging），<code>RandomForestClassifier()</code> 預設看 $\sqrt p$ 個。</p>""")

    q = quiz("qRf", "QUIZ · Random Forest",
        "Random forest 每次分裂只從 m 個隨機挑出的變數裡選。這 m 個變數是怎麼抽的？",
        [(True, "每一次分裂都重新隨機抽 m 個，所以同一棵樹的不同節點可以用不同的變數組",
          "對。每個節點都重抽，強變數才會在一部分節點被擋掉，讓其他變數有機會出頭。整棵樹只抽一次的做法叫 random subspace。"),
         (False, "每棵樹開始前抽一次 m 個變數，整棵樹都只用這 m 個",
          "這是 random subspace（Ho, 1998）的做法。random forest 在每個節點重新抽，抽樣的層次不同。"),
         (False, "挑重要度最高的 m 個變數，分裂才不會浪費在雜訊上",
          "random forest 是隨機抽，不看重要度。若總是挑最強的變數，每棵樹又會長得一樣，去相關的效果就沒了。")])

    return fill(r"""<p>bagging 的樹若常常依賴同一組變數，預測也會一起出錯。設想資料裡有一個特別強的變數：幾乎每一棵 bagged 樹都會拿它當根節點的分裂變數，根一樣，下面的結構也大同小異，$B$ 棵樹像複製品，相關 $\rho$ 接近 1，平均一百棵和平均一棵差不多。</p>
<p><strong>Random forest</strong> 只改一個地方：每次要分裂時，先從 $p$ 個變數裡<strong>隨機抽 $m$ 個</strong>當候選，這一刀只能從這 $m$ 個裡選；下一次分裂再重新抽一次。於是平均有 $(p-m)/p$ 的分裂根本看不到那個強變數，其他變數才有機會出頭，樹與樹長得比較不一樣，這叫<strong>去相關</strong>（decorrelate）。$m=p$ 時 random forest 就是 bagging，所以 bagging 是它的特例。</p>
<p>以 ISLP 的 Heart 資料為例，$p=13$、取 $m\approx\sqrt{13}$ 就是每次分裂只看 4 個變數，約 $9/13\approx69\%$ 的分裂看不到任何一個指定的變數。用<a href="#w09-detail-rho-floor">開頭那節收合</a>的公式來說，random forest 想壓低的是平均不掉的那一項 $\rho\sigma^2$。</p>
[[0]]
<h3>m 為什麼常取 √p</h3>
<p>ISLP 說「通常取 $m\approx\sqrt p$」，這是 random forest 發明者的經驗建議，不是推導出來的最佳值。ESL 說分類常用 $\sqrt p$、迴歸常用 $p/3$，並明說應該當成調整參數。scikit-learn 的迴歸器甚至預設每次看全部變數。$m$ 愈小，樹與樹愈不相關，但每棵樹愈弱；預測變數很多又彼此高度相關時，小一點的 $m$ 通常有幫助，有用的變數只占少數時，太小的 $m$ 則會讓多數分裂只能在雜訊裡挑。</p>
[[1]]
[[2]]
<h3>隨機化可以發生在不同層次</h3>
<p>抽樣本、抽變數、在哪裡抽變數，可以各自開關。這張表把講義提到的幾種做法放在一起：</p>
[[3]]
<p>Random forest 結合了 bagging 的抽樣本與「每個節點抽變數」。Extra-trees 更進一步，連切點都隨機產生，講義說它通常能再降一點變異，代價是偏差稍微增加。</p>
[[4]]
<h3>講義的基因表達例子</h3>
<p>這份資料有 349 位病人、4,718 個基因的表現量，反應變數有 15 類（正常或 14 種癌症之一）。先挑訓練資料中變異最大的 500 個基因當預測變數，再比較 $m=p$、$p/2$、$\sqrt p$ 三種設定（ISLP 圖 8.10）。單棵分類樹的測試錯誤率是 45.7%，全部猜最多的那一類則是 75.4%；400 棵樹之後誤差就平掉了，$m=\sqrt p$ 比 bagging 略好。這個結果只針對這份資料與這次切分。和 bagging 一樣，random forest 也不會因為 $B$ 變大而過度擬合。</p>
[[5]]
[[6]]
[[7]]""",
        info("📌 代價", "每一刀的選擇變少，單棵樹可能變弱、偏差變大。去相關換到的變異下降，要大過偏差的上升才划算，這要用驗證資料判斷。"),
        m_detail,
        proof_var,
        levels,
        xt_detail,
        lab_detail,
        q,
        links([("https://dafriedman97.github.io/mlbook/content/c6/s1/random_forests.html", "Random forest 去相關"),
        ("https://ieeexplore.ieee.org/document/709601", "Ho（1998）random subspace"),
        ("https://link.springer.com/chapter/10.1007/978-3-642-33460-3_28", "Louppe 與 Geurts（2012）random patches"),
        ("https://scikit-learn.org/stable/modules/ensemble.html#extremely-randomized-trees", "Extra-trees 官方說明"),
        ("https://gedeck.github.io/ai-assisted-statistics-for-data-scientists/docs/python/ch06.html", "AI-Assisted Statistics 第 6 章程式範例")]))


# ══ importance：變數重要度 ════════════════════════════════════════════════
def _importance(old):
    vimp = grab_viz(old["stacking"], "w09vimpChart")
    k = vimp.index('<div class="side-panel">')
    vimp = vimp[:k] + """<div class="side-panel">
    <div class="info-card">
      <div class="ic-title">怎麼看</div>
      lab 的 random forest（每次分裂看 6 個變數）在 Boston 上的分裂重要度，數值是 lab 輸出的相對重要度（所有變數加總為 1）。lstat 與 rm 各約 0.33 到 0.36，遙遙領先；其餘變數都不到 0.07。長條只說「樹很常拿它來切、切了很有效」，不說方向，也不說因果。
    </div>
  </div>
</div>"""
    a = "依各變數的分裂純度下降量解讀其在模型中的作用。"
    if vimp.count(a) != 1:
        raise ValueError("重要度元件旁白比對失敗")
    vimp = vimp.replace(a, "長條是分裂造成的不純度下降，在所有樹上平均後的相對值。")

    bias_detail = detail("w09-detail-importance", "不純度重要度的偏誤，以及置換重要度的細節", r"""
<p><strong>不純度重要度的式子。</strong>設 $v(t)$ 是節點 $t$ 用來分裂的變數，$\Delta_t$ 是這次分裂讓 RSS（分類時是加權 Gini 指數）下降的量。第 $j$ 個變數在 $B$ 棵樹上的重要度是</p>
$$\mathrm{Imp}_j=\frac1B\sum_{b=1}^B\ \sum_{t\in T_b:\,v(t)=j}\Delta_t .$$
<p>這是講義的概念公式。scikit-learn 的 random forest 實作順序略有不同：每棵樹先把自己的重要度正規化成總和 1，再對樹平均，最後再正規化一次；所以它是各棵樹「相對重要度」的平均，和先把原始下降量平均再正規化不完全相同，排名也可能略有差異。兩種做法都是非負的。ESL 第 10.13.1 節替 boosting 定義的版本是先算每棵樹裡的（平方）改善量總和，再對 $M$ 棵樹平均，理由是平均有穩定的效果，比單棵樹可靠。</p>
<p><strong>三個偏誤。</strong></p>
<ul>
<li><strong>算在訓練資料上。</strong>$\Delta_t$ 是訓練資料上的改善，深樹在訓練資料上切出來的改善有一部分是雜訊。</li>
<li><strong>偏好可切的地方多的變數。</strong>連續值很多、或類別水準很多的變數，候選切點多，比較容易碰巧找到一個在訓練資料上看起來不錯的切法；scikit-learn 文件明白警告不純度重要度偏好這種高基數（high cardinality）變數。</li>
<li><strong>相關的變數互相分攤。</strong>兩個幾乎相同的變數，樹在不同節點會輪流挑其中一個，功勞被拆開，兩個看起來都不太重要。拆分不保證是一半一半。</li>
</ul>
<p><strong>置換重要度。</strong>在沒參與訓練的資料上（測試集，或 random forest 的 OOB 樣本），把第 $j$ 欄的值隨機打亂，重算表現，下降的量就是重要度；重複打亂 $R$ 次取平均：</p>
$$\mathrm{PI}_j=\frac1R\sum_{r=1}^R\Big[\text{表現}(\text{原資料})-\text{表現}(\text{第 }j\text{ 欄打亂後})\Big].$$
<p>它問的是「模型有多依賴這一欄」，因為用的是沒參與訓練的資料，可以是負的：打亂後表現沒有變差，只表示模型在這份評估資料上看不出這一欄有穩定的正向貢獻；要判斷是不是雜訊，得重複打亂幾次、看變動有多大。ESL 第 15.3.2 節的 OOB 版本就是在每棵樹的 OOB 樣本上這樣做，再對所有樹平均。</p>
<p>置換重要度也有限制。相關的變數同樣會互相代打：打亂一個，另一個仍然帶著差不多的資訊，下降就不多。打亂也可能造出現實中不會出現的組合。而且它衡量的是「這個模型」有多依賴這一欄，不是「拿掉這一欄、重新訓練」會差多少；ESL 提醒，重新訓練時其他變數可能接手。</p>""")

    lab_detail = detail("w09-detail-vimp-lab", "Lab：讀取 random forest 的分裂重要度",
        lab("讀取分裂重要度", 72, 72,
            note="這是由該變數的分裂造成的節點不純度總減少量，在所有樹上平均後的相對值。社區的財富水準（lstat）與房屋大小（rm）遠遠領先其他變數。")
        + r"""<p>上面的互動圖用的就是這個模型（<code>max_features=6</code>），不純度那一欄的數字與這裡相同。</p>""")

    q = quiz("qVimp", "QUIZ · 變數重要度",
        "兩個高度相關的變數 X₁、X₂ 在 random forest 的不純度重要度都只排中後段。下列哪個解讀最合理？",
        [(True, "它們可能在分攤同一份資訊；要判斷這份資訊重不重要，可以一起置換或一起拿掉兩者再比較",
          "對。樹在不同節點會輪流挑相關變數中的一個，功勞被拆開，各自的分數都不高。把兩個一起處理，才看得出它們合起來的貢獻。"),
         (False, "兩者都可以刪掉，因為重要度低代表對 y 沒有影響",
          "重要度描述的是模型怎麼使用變數，而且相關變數會互相稀釋；「排名後段就能刪」是危險的推論。"),
         (False, "改用置換重要度就能消除相關變數的問題",
          "置換重要度同樣受相關變數影響：打亂其中一個，另一個仍然帶著差不多的資訊，下降就不多。")])

    return fill(r"""<p>單一棵樹最大的優點是可以畫出來給人看。集成之後這個優點就沒了：你不可能把 500 棵樹貼在牆上。<strong>變數重要度</strong>（variable importance）是讀集成模型最常見的工具，bagging、random forest 與 boosting 都能用。</p>
<p>講義的定義：</p>
<ul>
<li><strong>迴歸樹</strong>：把某個變數在所有分裂中造成的 <strong>RSS 下降總量</strong>加起來，再對 $B$ 棵樹平均。</li>
<li><strong>分類樹</strong>：同樣的做法，改成 <strong>Gini 指數下降總量</strong>。</li>
</ul>
<p>數值大的變數，就是樹常拿來切、而且切了很有用的變數。ISLP 圖 8.9 是 Heart 資料的結果，以最大值為 100 標準化，前三名是 Thal、Ca、ChestPain。</p>
<p><strong>為什麼是平均，不是加總？</strong>平均就是加總除以 $B$，兩者的排名與相對大小完全一樣。差別在加總會隨 $B$ 一路變大：種 100 棵和種 500 棵的森林，加總的數字差五倍，平均則可以直接比較。ISLP 圖 8.9 再除以最大值，scikit-learn 則正規化成總和為 1；各來源的正規化方式不完全相同，scikit-learn 的差異見下方收合。有用的是「對很多棵樹」取平均：單棵樹的重要度很不穩，對很多棵樹平均才穩定，ESL 定義 boosting 的重要度時也是這樣說的。</p>
[[0]]
<h3>怎麼讀，不能怎麼讀</h3>
<ul>
<li><strong>它描述模型怎麼用變數，不是因果。</strong>重要度高只表示樹很愛用它來切，和「改變它就會改變 $y$」是兩回事。</li>
<li><strong>它沒有方向。</strong>迴歸係數有正負，重要度沒有；要看變數往哪個方向推預測，得另外畫偏依賴圖（partial dependence plot）。</li>
<li><strong>相關的變數會互相稀釋。</strong>兩個幾乎一樣的變數（例如公分與英吋量的身高），功勞會被拆開。重要度低不等於沒用，所以「排名最後就可以刪掉」是危險的推論。</li>
<li><strong>不純度重要度偏好可切的地方多的變數</strong>，而且算在訓練資料上。在沒參與訓練的資料上打亂一欄、看表現掉多少的<strong>置換重要度</strong>（permutation importance）可以補上這兩點。</li>
</ul>
<p><a href="#boosting">Boosting</a> 的模型也用同樣的方式讀重要度；BART 另有「每個變數在樹裡出現幾次」的摘要，放在 <a href="#stacking">Stacking 與 BART</a> 一節的收合。</p>
[[1]]
[[2]]
[[3]]
[[4]]""",
        vimp,
        bias_detail,
        lab_detail,
        q,
        links([("https://scikit-learn.org/stable/modules/ensemble.html", "scikit-learn：不純度重要度的偏誤與置換重要度")]))


def build(old):
    return {"why": _why(), "bagging": _bagging(old), "rf": _rf(old), "importance": _importance(old)}
