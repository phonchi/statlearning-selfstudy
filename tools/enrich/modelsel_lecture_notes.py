"""第六章依講義補齊的段落（2026-10-13）：子集選擇、選模準則、CV 標準誤與 Lasso 歸零。

正文只放講義主線與一兩句核心直覺；推導、數值例與延伸討論放進收合區。
"""
from lib import detail, hl, info, table

# ── 子集選擇：講義 p.6–9 ────────────────────────────────────────────────
SUBSET_INTRO = r"""
  <p>最直白的想法是把每一種變數組合都試一次，挑最好的。這就是<strong>最佳子集選擇</strong>（best subset selection）。$p$ 個變數有 $2^p$ 種組合（含空模型）。講義的演算法分三步：</p>
  <ol>
    <li>令 $M_0$ 為不含任何預測變數的空模型，它對每筆資料都預測樣本平均。</li>
    <li>對 $k=1,2,\ldots,p$：擬合全部 $\binom{p}{k}$ 個恰含 $k$ 個變數的模型，挑出 RSS 最小（等價於 $R^2$ 最大）的一個，記為 $M_k$。</li>
    <li>用交叉驗證的預測誤差、$C_p$（AIC）、BIC 或調整後 $R^2$，從 $M_0,\ldots,M_p$ 中挑出一個模型。</li>
  </ol>
  $$\text{總共要擬合}\;\sum_{k=0}^{p}\binom{p}{k}=2^{p}\;\text{個模型}$$
""" + info("為什麼要分兩階段", r"""<strong>第一階段只在同樣大小 $k$ 的模型之間比較。</strong>參數個數相同，訓練 RSS 低就代表擬合得好，比較是公平的，而且每個模型只要擬合一次、算一個 RSS，不必估測試誤差。<br>
  <strong>第二階段只剩 $p+1$ 個候選</strong>，這時才花力氣估測試誤差。這一步不能再用訓練 RSS：RSS 隨 $k$ 單調下降、$R^2$ 單調上升，一定會選到全部變數。""", "warm") + detail(
    "w06-detail-two-stage", "延伸閱讀：為什麼不直接對所有子集做 CV？", r"""
  <p>可以。直接用交叉驗證比較全部 $2^p$ 個子集，在統計上合理，也可能找到比兩階段法更好的預測模型。教科書仍介紹兩階段，主要有兩個原因。</p>
  <h4>1. 計算成本</h4>
  <p>以 $p=10$ 為例，共有 $2^{10}=1024$ 個候選模型。</p>
""" + table(["做法", "第一階段", "第二階段", "總擬合次數（約）"],
            [["兩階段＋$C_p$、AIC、BIC", "1024 個模型各擬合一次、算訓練 RSS", "在 11 個模型間加上懲罰項比較", "$1024$"],
             ["直接對所有子集做 5 折 CV", "不需要", "1024 個模型各做 5 折", r"$1024\times5=5120$"]]) + r"""
  <p>兩階段搭配 $C_p$、AIC、BIC 時，可以避免對每個候選模型反覆做 CV，省下的計算最多。若第二階段用 CV，而且照規矩做（見下方），第一階段的搜尋也要在每一折的訓練部分重新執行，這時兩階段就省不了多少計算。</p>
  <h4>2. 同樣大小下，訓練 RSS 最好的模型不一定 CV 最好</h4>
  <p>假設 $p=3$，只看單變數模型：</p>
""" + table(["模型", "訓練 RSS", "CV 誤差"],
            [[r"$Y\sim X_1$", "90", "120"], [r"$Y\sim X_2$", "95", "105"], [r"$Y\sim X_3$", "110", "130"]]) + r"""
  <p>兩階段法的第一階段用訓練 RSS 選出 $X_1$（90 最小），第二階段只會看到這個單變數模型，不會再考慮 $X_2$。直接對所有模型做 CV，則會選到 CV 誤差較小的 $X_2$。也就是說，兩者一般不保證相同：</p>
  $$\underset{S:\,|S|=k}{\arg\min}\;\mathrm{RSS}(S)\;\ne\;\underset{S:\,|S|=k}{\arg\min}\;\mathrm{CV}(S)\quad\text{（一般情況）}.$$
  <h4>3. 兩階段把兩個問題分開</h4>
  <p>第一階段回答「每個大小下，哪些變數最能擬合訓練資料」：$M_k=\arg\min_{|S|=k}\mathrm{RSS}(S)$。第二階段回答「模型應該多複雜」：$k^*=\arg\min_k\text{準則}(M_k)$。這是方便、有系統的搜尋策略，方便搭配 AIC、BIC，但不是數學上非如此不可的規定。</p>
  <h4>兩個常見的陷阱</h4>
  <ul>
    <li>用 CV 選模型大小時，<strong>每一折都要在訓練部分重新做變數搜尋</strong>。先用完整資料挑出 $M_k$，再把這些固定模型拿去做 CV，驗證折已經參與過變數選擇，CV 誤差會偏低。</li>
    <li>即使直接對所有子集做 CV，挑出最小的 CV 誤差之後，這個最小值也不是無偏的泛化誤差估計，因為模型就是依它挑出來的。要報告最終模型的預測能力，仍需要獨立測試集或<a href="resampling_methods.html#w05-detail-nested-cv">巢狀 CV</a>。</li>
  </ul>
""")

SUBSET_DEVIANCE = r"""
  <p>講義接著指出，這套做法不限最小平方，邏輯斯迴歸等其他模型也能用；這時以<strong>離差</strong>（deviance）取代 RSS 當擬合量。</p>
""" + detail("w06-detail-subset-deviance", "延伸閱讀：離差為什麼能取代 RSS？", r"""
  <p>離差和負二倍最大對數概似成比例：$D=-2\log\hat L+\text{常數}$，常數只和資料有關、與模型無關。愈小代表擬合愈好，角色和 RSS 一樣。</p>
  <p>對誤差變異數 $\sigma^2$ 已知的常態線性模型，$-2\log\hat L=\mathrm{RSS}/\sigma^2+\text{常數}$，離差就是 RSS 換了量尺。所以講義的兩階段法可以原封不動搬過去：第一階段在同大小模型間比離差；第二階段同樣不能用訓練離差（巢狀模型加變數不會讓它變大），要改用 AIC、BIC 或 CV。這時 AIC 寫成 $-2\log\hat L+2k$、BIC 寫成 $-2\log\hat L+k\log n$，$k$ 計入實際估計的參數；軟體的數值量尺見下一節的<a href="#w06-detail-deviance">分類離差的數值</a>。</p>
""")

STEPWISE_WHY = r"""
  <p><strong>講義指出最佳子集的兩個問題。</strong>計算上，$2^p$ 長得太快，$p$ 超過 40 左右就算不完。統計上，搜尋空間愈大，愈容易找到在訓練資料上看起來很好、對未來資料卻沒有預測力的模型；龐大的搜尋空間會造成過度擬合，也讓係數估計的變異變大。逐步法只探索小得多的模型集合，所以是有吸引力的替代方案。</p>
""" + detail("w06-detail-snooping", "延伸閱讀：第二階段的驗證能不能抓出第一階段的過度擬合？", r"""
  <p>可以，但要看第二階段用的是什麼。這個問題常被叫做 data snooping 或 selection-induced overfitting（因大量搜尋而產生的過度擬合），和刻意搜尋顯著 $p$ 值的 p-hacking 不是同一件事。</p>
  <h4>第二階段確實能緩解</h4>
  <p>假設有 $p=100$ 個變數，全部都和 $Y$ 無關。第一階段在大量組合中搜尋，可能碰巧找到訓練 $R^2$ 很高（例如 0.8）的模型，那只是擬合到了雜訊。如果第二階段能可靠地估測試誤差，就會發現它的預測能力很差，甚至不如空模型 $M_0$，於是把它淘汰。</p>
  <h4>能緩解多少，取決於第二階段的方法</h4>
""" + table(["第二階段的方法", "能否處理第一階段的過度擬合？"],
            [["母體的期望測試誤差（理想，實際上不知道）", "可以辨識每個候選模型的真實預測風險"],
             ["獨立驗證集，或正確執行的 CV", "可以緩解，但仍有估計誤差，挑最小值也有選擇偏差"],
             ["$C_p$、AIC、BIC", "可能修正不足"]]) + r"""
  <p>$C_p$、AIC、BIC 的懲罰只看模型大小 $k$，沒有反映「從 $\binom{p}{k}$ 個候選中挑出最好的一個」所增加的選擇複雜度；它們的推導前提是模型事先固定。正確的 CV 要在每個訓練折內重新做最佳子集，見上方「為什麼要分兩階段」收合區。</p>
  <h4>什麼情況下最後的評估不受污染</h4>
  <ol>
    <li>在訓練資料上執行最佳子集選擇。</li>
    <li>用獨立的驗證資料選模型大小。</li>
    <li>用完全沒參與選模的測試資料評估最終模型。</li>
  </ol>
  <p>這時第一階段的搜尋不會直接影響第 3 步的測試誤差。但第 2 步挑出的最小驗證誤差仍偏樂觀；若還想對選中變數的係數做顯著性檢定，也不能忽略前面的選擇過程（選後推論的問題）。</p>
  <p>最佳子集在高維時容易對訓練資料過度擬合，透過適當的樣本外驗證可以大幅緩解；兩階段法本身不保證完全消除選擇偏差。</p>
""")

GUIDED_SEARCH = r"""
  <p>講義提醒：前向逐步雖然只擬合 $1+p(p+1)/2$ 個模型，卻是<strong>由資料引導的搜尋</strong>（guided search），實際涵蓋的有效模型空間遠比這個數字大。</p>
""" + detail("w06-detail-guided-search", "延伸閱讀：為什麼有效模型空間比實際擬合的模型多？", r"""
  <p>以 $p=4$ 為例，變數為 $X_1,X_2,X_3,X_4$。</p>
  <ul>
    <li>第一步：比較四個單變數模型 $\{X_1\},\{X_2\},\{X_3\},\{X_4\}$，假設選中 $X_2$。</li>
    <li>第二步：只考慮在 $X_2$ 上再加一個變數：$\{X_2,X_1\},\{X_2,X_3\},\{X_2,X_4\}$，假設選中 $\{X_2,X_4\}$。</li>
    <li>第三步：比較 $\{X_2,X_4,X_1\}$ 與 $\{X_2,X_4,X_3\}$。</li>
    <li>第四步：加入最後一個變數。</li>
  </ul>
  <p>加上空模型，一共擬合 $1+4+3+2+1=11$ 個模型，而全部可能的子集有 $2^4=16$ 個。</p>
  <p>這 11 個模型<strong>由訓練資料決定</strong>，並非事先固定。換一批資料，可能先選 $X_1$ 再選 $X_3$，也可能先選 $X_4$ 再選 $X_2$。$p=4$ 時變數加入的順序共有 $4!=24$ 種；一次執行只沿其中一條路徑前進，但走哪條路本身就用了 $y$。每個子集都是某種加入順序的前段，所以在不同資料下，全部 16 個子集都可能被選中。</p>
""" + table(["數什麼", "$p=4$ 的數量"],
            [["一次執行實際擬合的模型", "11"],
             ["不同資料下可能被選中的模型", "全部 16 個子集"],
             ["可能的加入順序", "$4!=24$"]]) + r"""
  <p>因此，統計上的選擇複雜度不能只用 11 個模型衡量，這就是講義說的 effective model space。用逐步法挑出的模型，同樣需要上一段所說的樣本外驗證。</p>
""")

ORTHOGONAL_FORWARD = detail("w06-detail-orthogonal-forward", "延伸閱讀：什麼時候前向逐步一定等於最佳子集？", r"""
  <p>在最小平方下，如果特徵<strong>在樣本中彼此正交</strong>，前向逐步選擇和最佳子集選擇對每個大小 $k$ 都會選出相同的變數組合（忽略並列的情況）。條件是樣本中的正交，不只是母體中不相關。</p>
  <h4>為什麼會相同</h4>
  <p>模型含截距，特徵已中心化，而且 $X_i^\top X_j=0\ (i\ne j)$。令 $y_c$ 為中心化後的反應，對任意變數子集 $S$，</p>
  $$\mathrm{RSS}(S)=\mathrm{TSS}-\sum_{j\in S}\frac{(X_j^\top y_c)^2}{X_j^\top X_j}.$$
  <p>右邊是每個特徵的貢獻直接相加：一個變數能讓 RSS 降多少，和其他變數有沒有在模型裡無關。要選 $k$ 個變數，最佳子集只要挑 $(X_j^\top y_c)^2/(X_j^\top X_j)$ 最大的 $k$ 個；前向逐步每一步挑的也正是剩下的變數中貢獻最大的那一個。兩者自然相同。</p>
""" + table(["特徵", "單獨加入時 RSS 的減少量"], [["$X_1$", "100"], ["$X_2$", "60"], ["$X_3$", "30"]]) + r"""
  <p>最佳子集：$k=1$ 選 $X_1$，$k=2$ 選 $\{X_1,X_2\}$，$k=3$ 選全部。前向逐步：第一步選 $X_1$（RSS 減 100），第二步選 $X_2$（再減 60），第三步選 $X_3$（再減 30）。兩者完全相同。</p>
  <h4>特徵相關時就不一定</h4>
  <p>若 $X_1$ 與 $X_2$ 高度相關，單獨用 $X_1$ 能大幅降低 RSS，但加入 $X_1$ 後，$X_2$ 能提供的額外資訊就很少；反而 $\{X_2,X_3\}$ 可能比 $\{X_1,X_3\}$ 更好。某個變數單獨表現很好，不代表它屬於最佳的多變數組合。前向逐步不能移除已選的變數，可能錯過這個組合；最佳子集則會搜尋到。</p>
""" + table(["特徵的條件", "兩種方法一定相同？"],
            [["樣本中完全正交", "是（忽略並列）"],
             ["母體中不相關，但樣本有相關", "不一定"],
             ["樣本相關性很小", "常常接近，但不保證"],
             ["特徵明顯相關", "不保證"]]) + r"""
  <p>即使母體滿足 $\operatorname{Cov}(X_1,X_2)=0$，有限樣本的 $\widehat{\operatorname{Cov}}(X_1,X_2)$ 通常也不是 0，所以母體不相關不能保證兩種演算法在訓練資料上給出相同結果。前向逐步與最佳子集的差異，來自變數之間的相依結構：單一變數的貢獻會隨已選的變數而改變。</p>
""")

# ── 選模準則：講義 p.19–21 ──────────────────────────────────────────────
CP_CORE = r"""
  <p>$C_p$ 的兩個要點：所有候選模型<strong>共用同一個</strong> $\hat\sigma^2$，通常由含全部 $p$ 個預測變數的全模型估計；$2d\hat\sigma^2$ 是在修正訓練 RSS 對測試誤差的<strong>樂觀偏差</strong>。加一個變數，訓練 RSS 必須降超過 $2\hat\sigma^2$，$C_p$ 才會變小。</p>
""" + detail("w06-detail-cp-intuition", "延伸閱讀：為什麼共用全模型的 $\\hat\\sigma^2$？$2d\\hat\\sigma^2$ 從哪裡來？", r"""
  <h4>為什麼所有模型用同一個 $\hat\sigma^2$</h4>
  <p>我們假設 $Y=f(X)+\varepsilon$、$\operatorname{Var}(\varepsilon)=\sigma^2$。$\sigma^2$ 是資料生成過程的雜訊變異數，不會因為我們換了模型而改變，所以所有候選模型用同一個估計值：</p>
  $$\hat\sigma^2=\frac{\mathrm{RSS}_{\text{full}}}{n-p-1}.$$
  <p>如果每個候選模型都用自己的 RSS 估 $\sigma^2$，較小的模型因為欠擬合，會把模型偏差也算成雜訊，估計值偏大。用全模型當共同基準，前提是全模型足以描述真實的平均反應函數；否則 $\hat\sigma^2$ 也會有偏差。</p>
  <h4>係數 2 的來源</h4>
  <p>訓練 RSS 因為擬合到雜訊，期望比 $n\sigma^2$ 少 $d\sigma^2$；拿同一組係數去預測新反應，參數估計的不確定性又讓測試 RSS 多出 $d\sigma^2$。兩半合起來是 $2d\sigma^2$。完整推導（含模型有近似偏差的情形），以及 AIC、BIC 的懲罰從哪裡來，見本節後面的<a href="#w06-detail-criteria-origins">三個準則的懲罰項推導</a>。</p>
  <h4>加一個變數，RSS 要降多少才值得</h4>
  <p>$d$ 變成 $d+1$，懲罰項增加 $2\hat\sigma^2$。只有當</p>
  $$\mathrm{RSS}_{\text{old}}-\mathrm{RSS}_{\text{new}}>2\hat\sigma^2$$
  <p>時 $C_p$ 才會下降。例如 $\hat\sigma^2=4$，新變數必須讓 RSS 降超過 8。假設某個新變數讓 RSS 降了 12：</p>
""" + table(["$\\hat\\sigma^2$", "新增一個變數的懲罰", "RSS 降 12，值得加入嗎？"],
            [["1", "2", "值得"], ["4", "8", "值得"], ["9", "18", "不值得"], ["16", "32", "不值得"]]) + r"""
  <p>直覺是：雜訊愈大，即使新變數完全沒用，也可能因為剛好擬合到隨機波動而讓 RSS 明顯下降，所以要求更大的改善才相信它。在誤差獨立、同變異的常態線性模型下，考慮一個<strong>事先指定</strong>、不在原模型欄空間內的新變數；若原模型已經正確、新變數的真實係數為 0，加入它造成的下降滿足</p>
  $$\frac{\mathrm{RSS}_{\text{old}}-\mathrm{RSS}_{\text{new}}}{\sigma^2}\sim\chi^2_1,$$
  <p>它本身就隨 $\sigma^2$ 放大（分母是母體的 $\sigma^2$；從許多候選中挑出 RSS 降最多的那個變數，下降量就不再服從這個分布）。所以 $C_p$ 的門檻其實是在看相對於雜訊的改善：$\Delta\mathrm{RSS}/\sigma^2>2$。這也表示「$\sigma^2$ 愈大，一定選愈少變數」並不嚴格成立，因為 RSS 的下降量本身也會隨雜訊改變。</p>
  <h4>和兩階段法的關係</h4>
  <p>第一階段固定 $d$，懲罰項對同大小的模型都相同，最小化 $C_p$ 等同於最小化訓練 RSS。第二階段比較不同的 $d$，$2d\hat\sigma^2$ 才發揮作用，避免只因變數變多、訓練 RSS 變小就一直加變數。</p>
""")

AIC_BIC_CORE = r"""
  <p>AIC 與 BIC 的目標不同：<strong>AIC 著重預測準確度</strong>（漸近效率），<strong>BIC 著重找出真實模型</strong>（選模一致性）。真實模型沒有模型偏差，但在有限樣本下，它的結構不一定最容易估計，也不一定預測得最好。</p>
""" + detail("w06-detail-aic-bic-goals", "延伸閱讀：漸近效率、選模一致性與「真實模型不一定預測最好」", r"""
  <h4>AIC 的漸近效率</h4>
  <p>假設候選模型為 $M_1,\ldots,M_K$，各有真實的預測風險 $R(M_k)$。若知道真實分布，就能挑出風險最小的 $M_{\text{oracle}}=\arg\min_kR(M_k)$。實際上只能用 AIC 選出 $\hat M_{\text{AIC}}$。漸近效率的典型意思是</p>
  $$\frac{R(\hat M_{\text{AIC}})}{\min_kR(M_k)}\xrightarrow{P}1\qquad(n\to\infty),$$
  <p>也就是資料愈多，AIC 所選模型的風險愈接近候選中最好的那個。這裡的風險要適當定義（例如 KL 散度或超額預測風險），而且這是特定理論條件下的性質，不是所有選模問題都成立。AIC 設計的目標就是近似模型對新資料的期望 KL 差異，所以它偏向預測表現。</p>
""" + table(["", "AIC", "BIC"],
            [["公式", "$-2\\log L+2d$", "$-2\\log L+d\\log n$"],
             ["主要目標", "預測能力", "辨識真實模型"],
             ["漸近性質（特定條件下）", "漸近效率", "選模一致性"],
             ["懲罰隨 $n$ 增加", "固定為 $2d$", "隨 $\\log n$ 增加"],
             ["對微弱訊號", "較願意保留", "較容易排除"],
             ["理論優勢", "真實函數無法用有限維模型完整表示時", "真實模型固定、有限維且在候選清單中時"]]) + r"""
  <p>例如真正的模型只含 $X_1$，候選卻還有 $X_2,X_3$。即使樣本數愈來愈多，AIC 仍有正的機率選到多餘變數，所以它沒有一般意義下的選模一致性；BIC 在真實模型屬於候選清單等條件下，選中它的機率會趨近 1。反過來，若真正的函數非常複雜（例如無限多項的多項式），沒有任何有限維候選能完全表示它，選模的目標就變成找偏差–變異取捨好的近似模型，這時 AIC 的漸近效率比較有意義。</p>
  <h4>真實模型為什麼不一定預測最好</h4>
  <p>假設真實模型為 $Y=2X_1+0.05X_2+\varepsilon$，$\varepsilon\sim N(0,1)$，$n=100$，$X_1,X_2$ 獨立且已標準化。$X_2$ 的係數 0.05 不是零，所以真實模型包含 $X_2$。比較 $X_2$ 對預測風險的額外貢獻（其他部分相同）：</p>
""" + table(["", "包含 $X_2$（真實結構）", "不包含 $X_2$"],
            [["偏差", "0", "有偏差"],
             ["額外的變異", "約 $\\sigma^2/n=0.01$", "0"],
             ["額外的平方偏差", "0", "$0.05^2=0.0025$"]]) + r"""
  <p>$0.0025<0.01$：不放 $X_2$ 反而可能有較小的測試誤差。估計這個微弱訊號付出的變異，比忽略它造成的偏差還大。</p>
  <p>當 $n\to\infty$，$\operatorname{Var}(\hat\beta_2)\approx1/n\to0$，估計 $X_2$ 的成本消失，忽略它的偏差卻一直存在。所以真實模型固定、有限維且正確指定時，樣本夠大之後選到真實模型才會佔優勢，這也是 BIC 選模一致性的價值。</p>
  <p>要分清楚：若連真正的參數值都知道，真實模型在平方誤差下當然預測最好。這裡說的是「結構選對了，參數仍要用有限樣本估計」。預測誤差同時取決於偏差與變異；有限樣本下，略有偏差但變異小得多的簡單模型，可能預測得更好。AIC 的漸近效率也不代表在每個資料集上 AIC 的測試誤差都比 BIC 小，兩者的理論優勢建立在不同的假設與目標上。</p>
""") + detail("w06-detail-criteria-origins", "推導：$C_p$、AIC、BIC 的懲罰項各從哪裡來", r"""
  <p>三個準則都是「訓練擬合＋隨模型變大的懲罰」，公式很像，懲罰的理由卻不同：</p>
  <ul>
    <li>$C_p$：修正訓練 RSS 對預測誤差的樂觀偏差。</li>
    <li>AIC：修正最大對數概似對新資料的樂觀偏差，目標是和真實分布的 KL 散度。</li>
    <li>BIC：近似貝氏的邊際概似，挑後驗機率較高的模型。</li>
  </ul>
  <p>共同的起點是：加變數不會讓訓練 RSS 變大，也不會讓最大對數概似變小，但這不代表預測變好。以下依序推導三個懲罰。記號：$d$ 是預測變數個數，$r$ 是迴歸係數個數（含截距時 $r=d+1$），$k$ 是所有實際估計的參數個數。</p>

  <h4>一、$C_p$：訓練 RSS 的樂觀偏差</h4>
  <p>先固定 $X$ 與候選模型，不用 $y$ 搜尋欄位。設 $y=\mu+\varepsilon$，$E[\varepsilon]=0$、$\operatorname{Cov}(\varepsilon)=\sigma^2I$。OLS 擬合值 $\hat y=Hy$，$H=X(X^\top X)^{-1}X^\top$ 對稱冪等，$\operatorname{tr}(H)=r$。</p>
  <p><strong>訓練 RSS。</strong>$y-\hat y=(I-H)\mu+(I-H)\varepsilon$，交叉項期望為 0，且 $E\|(I-H)\varepsilon\|^2=\sigma^2\operatorname{tr}(I-H)$：</p>
  $$E[\mathrm{RSS}]=\|(I-H)\mu\|^2+(n-r)\sigma^2.$$
  <p>第一項是近似偏差，第二項是雜訊。擬合時有 $r\sigma^2$ 的雜訊被模型「吃掉」，所以比 $n\sigma^2$ 少。</p>
  <p><strong>新反應。</strong>在相同 $X$ 上取一組獨立的 $y^{\text{new}}=\mu+\varepsilon^{\text{new}}$。$y^{\text{new}}-\hat y=(I-H)\mu+\varepsilon^{\text{new}}-H\varepsilon$，三項之間的交叉項期望都是 0：</p>
  $$E\|y^{\text{new}}-\hat y\|^2=\|(I-H)\mu\|^2+n\sigma^2+r\sigma^2.$$
  <p>多出的 $r\sigma^2$ 來自估計參數的變異。兩式相減，偏差項正好抵消：</p>
  $$E[\text{測試 RSS}]=E[\mathrm{RSS}]+2r\sigma^2.$$
  <p>每多估一個參數，訓練 RSS 相對於預測誤差的樂觀偏差就多 $2\sigma^2$：一半來自擬合雜訊，一半來自估計的不確定性。用所有模型共用的 $\hat\sigma^2$ 取代 $\sigma^2$、再除以 $n$，就是 $C_p=(\mathrm{RSS}+2d\hat\sigma^2)/n$；各模型都有截距時，共同的 $2\hat\sigma^2/n$ 可以省略。$\hat\sigma^2$ 不偏就能在期望中取代 $\sigma^2$，不需要和 RSS 獨立。若模型本身是用同一份 $y$ 搜尋出來的，$H$ 已經依賴 $y$，這個推導就不再成立（見<a href="#w06-detail-cp-risk">$C_p$ 的風險目標與常數</a>）。</p>

  <h4>二、AIC：從 KL 散度出發</h4>
  <p>設資料的真實分布為 $g$，候選模型為 $f(y\mid\theta)$，兩者的差距用 KL 散度衡量：</p>
  $$D_{\mathrm{KL}}(g\,\|\,f_\theta)=E_g\!\left[\log\frac{g(Y)}{f(Y\mid\theta)}\right]=E_g[\log g(Y)]-E_g[\log f(Y\mid\theta)].$$
  <p>第一項和候選模型無關，所以比較模型只要看第二項：期望對數概似愈大，離真實分布愈近。$g$ 未知，參數只能用最大概似估計 $\hat\theta$。我們想知道 $\hat\theta$ 在<strong>另一組</strong>同樣大小、獨立的新資料上的對數概似 $\ell_{\text{new}}(\hat\theta)$，手上卻只有訓練資料的 $\ell(\hat\theta)$。$\hat\theta$ 本來就是讓 $\ell$ 最大的值，所以 $\ell(\hat\theta)$ 偏高。</p>
  <p><strong>樂觀偏差約為 $k$。</strong>假設模型正確指定、參數個數 $k$ 固定，並滿足一般的正則條件。令 $\theta_0$ 為真實參數，$I(\theta_0)$ 為單筆觀測的費雪資訊，記 $Q=n(\hat\theta-\theta_0)^\top I(\theta_0)(\hat\theta-\theta_0)$；大樣本下 $Q$ 近似 $\chi^2_k$，$E[Q]\approx k$。在兩個最大值附近各做二階展開：</p>
  <ul>
    <li>訓練資料：$\ell$ 在 $\hat\theta$ 的梯度為 0，所以 $\ell(\hat\theta)\approx\ell(\theta_0)+\tfrac12Q$。擬合時多賺了約 $k/2$。</li>
    <li>新資料：新資料的期望對數概似在 $\theta_0$ 最大，所以 $E[\ell_{\text{new}}(\hat\theta)]\approx E[\ell_{\text{new}}(\theta_0)]-\tfrac12E[Q]$。用估計值而不是真值，又少了約 $k/2$。</li>
  </ul>
  <p>因為 $E[\ell(\theta_0)]=E[\ell_{\text{new}}(\theta_0)]$，兩式相減得</p>
  $$E[\ell(\hat\theta)]-E[\ell_{\text{new}}(\hat\theta)]\approx k.$$
  <p>結構和 $C_p$ 一樣：一半是擬合到訓練雜訊，一半是參數估計的不確定性。所以 $\ell(\hat\theta)-k$ 才是新資料對數概似的近似不偏估計，乘上 $-2$：</p>
  $$\mathrm{AIC}=-2\ell(\hat\theta)+2k.$$
  <p>模型指定錯誤時，$k$ 要換成一個跡項 $\operatorname{tr}(J^{-1}K)$（$J$ 是對數概似的負期望 Hessian、$K$ 是分數函數的變異數，這個版本稱為 TIC）；只有模型正確時 $J=K$，跡才化簡成 $k$。</p>
  <p><strong>高斯線性迴歸的寫法。</strong>$y_i\sim N(x_i^\top\beta,\sigma^2)$ 時</p>
  $$\ell(\beta,\sigma^2)=-\frac n2\log(2\pi\sigma^2)-\frac{\mathrm{RSS}}{2\sigma^2}.$$
  <p>$\sigma^2$ 也要估時，最大概似估計是 $\hat\sigma^2=\mathrm{RSS}/n$，代回得 $-2\ell(\hat\theta)=n\log(\mathrm{RSS}/n)+n[1+\log(2\pi)]$。參數有 $d$ 個斜率、截距與 $\sigma^2$，$k=d+2$；後兩個每個模型都有，比較時可以略去：</p>
  $$\mathrm{AIC}=n\log(\mathrm{RSS}/n)+2d+\text{常數}.$$
  <p><code>statsmodels</code> 的 <code>.aic</code>、<code>.bic</code> 用的就是這種對數概似量尺；常數與參數個數的算法見<a href="#w06-detail-criteria-scale">先分清估計量與比較量尺</a>。</p>

  <h4>三、AIC 與 $C_p$ 什麼時候排序相同</h4>
  <p>若 $\sigma^2$ 已知，或所有模型共用同一個固定值，只有 $r$ 個迴歸係數要估，$k=r$，而且</p>
  $$-2\ell(\hat\beta)=\frac{\mathrm{RSS}}{\sigma^2}+n\log(2\pi\sigma^2).$$
  <p>於是</p>
  $$\mathrm{AIC}=\frac{\mathrm{RSS}+2r\sigma^2}{\sigma^2}+\text{常數},$$
  <p>和 $C_p$ 只差一個正倍數與常數，排序完全相同。這時 AIC 的「$\approx k$」變成等號：第一部分的 $2r\sigma^2$ 除以 $\sigma^2$ 正好是 $2r$。這不是巧合：高斯誤差下，負對數概似就是換了量尺的平方誤差。課本的 AIC 公式 $(\mathrm{RSS}+2d\hat\sigma^2)/(n\hat\sigma^2)$ 就是這個版本，把 $\sigma^2$ 換成共用的 $\hat\sigma^2$（省略共同的截距項）。若各模型各自重估 $\sigma^2$，用的是上面 $n\log(\mathrm{RSS}/n)$ 的版本，數值不同，排序通常接近，但不保證相同。</p>

  <h4>四、BIC：從貝氏模型選擇出發</h4>
  <p>BIC 不估預測誤差，它問的是：哪個模型最可能產生這份資料？由貝氏定理，</p>
  $$P(M\mid y)\propto P(y\mid M)\,P(M),\qquad P(y\mid M)=\int f(y\mid\theta,M)\,\pi(\theta\mid M)\,d\theta.$$
  <p>$P(y\mid M)$ 稱為邊際概似（模型證據），是概似依先驗分布加權的平均。各模型的先驗機率相同時，比後驗機率就是比邊際概似。</p>
  <p><strong>Laplace 近似。</strong>$n$ 大時，概似集中在 $\hat\theta$ 附近：$\ell(\theta)\approx\ell(\hat\theta)-\tfrac12(\theta-\hat\theta)^\top J_n(\theta-\hat\theta)$，$J_n\approx nI(\hat\theta)$ 是觀測資訊矩陣。先驗在這個小範圍內近乎常數，積分變成高斯積分：</p>
  $$P(y\mid M)\approx e^{\ell(\hat\theta)}\,\pi(\hat\theta)\,(2\pi)^{k/2}\,|J_n|^{-1/2},\qquad |J_n|\approx n^k\,|I(\hat\theta)|.$$
  <p>取對數：</p>
  $$\log P(y\mid M)\approx\ell(\hat\theta)-\frac k2\log n+\underbrace{\log\pi(\hat\theta)+\frac k2\log(2\pi)-\frac12\log|I(\hat\theta)|}_{\text{不隨 }n\text{ 增長}}.$$
  <p>略去不隨 $n$ 增長的項，再乘上 $-2$：</p>
  $$\mathrm{BIC}=-2\ell(\hat\theta)+k\log n.$$
  <p>直覺：後驗在每個參數方向上只集中在寬度約 $1/\sqrt n$ 的範圍，先驗卻把機率攤在固定大小的範圍。參數愈多，先驗裡真正和資料吻合的比例愈小（約 $n^{-k/2}$），邊際概似就被這個比例拉低。複雜模型的最大概似雖然高，對整個參數空間平均起來卻不一定高。</p>
  <p>高斯線性迴歸同樣化成 $\mathrm{BIC}=n\log(\mathrm{RSS}/n)+d\log n+\text{常數}$；$\sigma^2$ 已知時是 $\mathrm{RSS}/\sigma^2+r\log n+\text{常數}$，代入共用的 $\hat\sigma^2$ 就得到課本的 $(\mathrm{RSS}+\log(n)\,d\hat\sigma^2)/n$（差一個正倍數與常數）。所以 $\log n$ 不是從預測誤差的樂觀偏差推出來的，而是對參數積分的結果。</p>

  <h4>五、三者對照</h4>
""" + table(["", "$C_p$", "AIC", "BIC"],
            [["想估計的量", "固定設計下的測試 RSS", "新資料的期望對數概似（KL 散度的相對大小）", "邊際概似 $P(y\\mid M)$"],
             ["懲罰的來源", "訓練 RSS 的樂觀偏差 $2r\\sigma^2$", "最大對數概似的樂觀偏差 $k$", "Laplace 近似的 $\\tfrac k2\\log n$"],
             ["理論工具", "投影矩陣的跡", "最大概似估計的漸近常態", "Laplace 近似"],
             ["每多一個參數的懲罰（$-2\\log L$ 量尺）", "$2$", "$2$", "$\\log n$"],
             ["主要假設", "固定設計、誤差同變異、模型不是用 $y$ 搜尋出來的", "模型正確指定、大樣本", "大樣本、先驗在 $\\hat\\theta$ 附近平滑且為正"]]) + r"""
  <p>在 $-2\log L$ 量尺下，AIC 每個參數固定罰 2，BIC 罰 $\log n$，差距隨樣本數拉大：</p>
""" + table(["$n$", "AIC／$C_p$", "BIC（$\\log n$）", "BIC 是 AIC 的幾倍"],
            [["8", "2", "2.08", "1.04"], ["100", "2", "4.61", "2.30"],
             ["400（Credit）", "2", "5.99", "3.00"], ["10000", "2", "9.21", "4.61"]]) + r"""
  <p>目標與漸近性質（漸近效率、選模一致性）的對照見上方<a href="#w06-detail-aic-bic-goals">漸近效率與選模一致性</a>。總結：$C_p$ 和 AIC 的 2 不是隨手挑的懲罰係數，而是訓練擬合相對於新資料的期望樂觀程度，可以算出來；BIC 的 $\log n$ 回答的是另一個問題（哪個模型最可能產生資料）。兩類準則的差別在目標，不只是罰多罰少。</p>
""")

ADJR2_CORE = r"""
  <p>調整後 $R^2$ 的精神：$R^2$ 問的是「加入預測變數後，訓練 RSS 比只用平均數預測時下降了多少比例」，只要加變數就不會下降。調整後 $R^2$ 改問「扣掉估計參數消耗的自由度之後，殘差變異數 $\mathrm{RSS}/(n-d-1)$ 是否真的比只用平均數時的 $\mathrm{TSS}/(n-1)$ 小」，加入的變數若沒有帶來足以抵銷自由度成本的 RSS 改善，它就會下降；不過無用的變數也可能因樣本波動剛好讓它上升。</p>
""" + detail("w06-detail-adjr2-df", "延伸閱讀：為什麼要除以自由度？$R^2$ 與調整後 $R^2$ 的比較", r"""
  <h4>先看最簡單的例子：樣本變異數</h4>
  <p>設 $Y_i=\mu+\varepsilon_i$，$\operatorname{Var}(\varepsilon_i)=\sigma^2$。$\mu$ 已知時可用 $\frac1n\sum_i(Y_i-\mu)^2$ 估 $\sigma^2$；$\mu$ 未知、改用 $\bar Y$ 估時，殘差必須滿足 $\sum_i(Y_i-\bar Y)=0$，$n$ 個殘差只有 $n-1$ 個能自由變動。可以證明</p>
  $$E\Bigl[\sum_{i=1}^n(Y_i-\bar Y)^2\Bigr]=(n-1)\sigma^2,$$
  <p>所以除以 $n-1$ 才得到 $\sigma^2$ 的不偏估計。</p>
  <h4>線性迴歸是同一個道理</h4>
  <p>模型有 $d$ 個預測變數和一個截距，OLS 估 $d+1$ 個參數，殘差 $e$ 要滿足 $d+1$ 條線性限制 $X^\top e=0$，剩下 $n-d-1$ 個自由度。線性模型正確指定、設計矩陣滿秩、誤差變異數相同時，</p>
  $$E[\mathrm{RSS}]=(n-d-1)\sigma^2\quad\Longrightarrow\quad\hat\sigma^2=\frac{\mathrm{RSS}}{n-d-1}.$$
  <p>除以自由度，是在修正「用同一批資料估參數，讓 RSS 系統性偏小」的現象。參數愈多，RSS 本來就會下降，這是預期中的事，不該每降一點都算成模型進步。</p>
  <h4>兩個 $R^2$ 的比較</h4>
  $$R^2=1-\frac{\mathrm{RSS}}{\mathrm{TSS}},\qquad R^2_{\text{adj}}=1-\frac{\mathrm{RSS}/(n-d-1)}{\mathrm{TSS}/(n-1)}.$$
""" + table(["", "$R^2$", "調整後 $R^2$"],
            [["比較基準", "只用平均數預測", "只用平均數預測"],
             ["衡量方式", "平方誤差總和", "自由度修正後的變異數"],
             ["增加預測變數", "不會下降", "可能下降"],
             ["主要目的", "樣本內解釋程度", "考慮模型複雜度後的改善"]]) + r"""
  <p>分母 $\mathrm{TSS}/(n-1)$ 是只用平均數預測時的樣本變異數；分子 $\mathrm{RSS}/(n-d-1)$ 是用了 $d$ 個預測變數之後的殘差變異數估計。因此</p>
  $$R^2_{\text{adj}}>0\iff\frac{\mathrm{RSS}}{n-d-1}<\frac{\mathrm{TSS}}{n-1},$$
  <p>也就是模型的殘差均方比只用平均數的樣本變異數還小。這仍是訓練資料上的比較，不保證測試誤差比較小；自由度修正也沒有處理「從很多候選中搜尋變數」造成的過度擬合。新增一欄何時讓調整後 $R^2$ 上升，見下方的門檻證明。</p>
""")

# ── CV 的標準誤：講義 p.24 ─────────────────────────────────────────────
CV_SE_CODE = """import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, RepeatedKFold, cross_val_score

model = LinearRegression()

# 單次 K 折：K 個折誤差的標準差 / sqrt(K)
kf = KFold(n_splits=10, shuffle=True, random_state=0)
fold_mse = -cross_val_score(model, X, y, cv=kf,
                            scoring="neg_mean_squared_error")
cv_mean = fold_mse.mean()
cv_se = fold_mse.std(ddof=1) / np.sqrt(len(fold_mse))

# 重複 K 折：換 R 種切分再平均，降低「切分運氣」造成的波動
rkf = RepeatedKFold(n_splits=10, n_repeats=5, random_state=0)
rep_mse = -cross_val_score(model, X, y, cv=rkf,
                           scoring="neg_mean_squared_error").reshape(5, 10)
repeat_means = rep_mse.mean(axis=1)          # 每一次重複的 CV 估計
print(cv_mean, cv_se, repeat_means.mean(), repeat_means.std(ddof=1))
"""

CV_SE_CORE = r"""
  <p>one-SE 規則裡的標準誤，通常用 $K$ 個折的誤差估計：$\widehat{\mathrm{SE}}=\mathrm{sd}(E_1,\ldots,E_K)/\sqrt K$。各折的訓練資料重疊、誤差並不獨立，所以它只是粗略的不確定性指標。</p>
""" + detail("w06-detail-cv-se", "計算細節：CV 的標準誤怎麼估？RepeatedKFold 與其他做法", r"""
  <h4>單次 $K$ 折</h4>
  <p>設第 $j$ 折的驗證誤差為 $E_j$（例如該折的 MSE），CV 估計是 $\bar E=\frac1K\sum_jE_j$（各折大小不同時用講義第 5 章的加權式）。把 $E_1,\ldots,E_K$ 當成 $K$ 個觀測，平均數的標準誤為</p>
  $$\widehat{\mathrm{SE}}(\bar E)=\frac{1}{\sqrt K}\sqrt{\frac{1}{K-1}\sum_{j=1}^K(E_j-\bar E)^2}.$$
  <p>Lab 用 NumPy 的 <code>std()</code>，預設 <code>ddof=0</code>（除以 $K$）；改成 <code>ddof=1</code> 除以 $K-1$，誤差棒會略長。這個公式把各折當成獨立，但任兩折的訓練集共用約 $(K-2)/K$ 的資料，$E_j$ 彼此相關，所以真實的變異通常被低估。它適合拿來看「曲線在哪裡平坦、差異是否小於誤差棒」，不能當成嚴格的信賴區間。</p>
  <h4>重複 $K$ 折（RepeatedKFold）</h4>
  <p>單次 CV 的結果還受「這一次怎麼切」影響。<code>RepeatedKFold(n_splits=K, n_repeats=R)</code> 用 $R$ 種不同的隨機切分各做一次 $K$ 折，得到 $R$ 個 CV 估計 $\bar E^{(1)},\ldots,\bar E^{(R)}$。它們的平均比單次 CV 穩定；它們的標準差描述的是<strong>切分造成的波動</strong>，不是對新資料的抽樣變異，因為 $R$ 次用的是同一份資料。若把 $R\times K$ 個折誤差全部當獨立觀測、再除以 $\sqrt{RK}$，會更嚴重地低估不確定性。</p>
""" + hl(CV_SE_CODE, block_id="w06-cv-se-code") + r"""
  <p>程式假設已備妥 <code>X</code>、<code>y</code>；比較不同模型大小時，對每個大小重複同一段計算，並讓每個模型用<strong>同一組切分</strong>，差異才不會混入切分的運氣。分類問題可改用 <code>RepeatedStratifiedKFold</code>。</p>
  <h4>其他做法</h4>
  <ul>
    <li><strong>逐筆誤差的標準誤</strong>：把每筆觀測的折外平方誤差 $e_i^2$ 當成 $n$ 個值，算 $\mathrm{sd}(e_i^2)/\sqrt n$。觀測較多時比只用 $K$ 個折誤差穩定，但同樣忽略了訓練集重疊造成的相關。</li>
    <li><strong>比較兩個模型時看差值</strong>：兩個模型用同一組切分，對每一折算誤差差 $E_j^{A}-E_j^{B}$，再算這些差值的標準誤。成對比較可以抵消兩模型共同受到的切分影響。</li>
    <li><strong>巢狀 CV 或獨立測試集</strong>：要報告選完模型後的泛化誤差及其不確定性，應使用外層 CV 或沒參與選模的測試資料；見<a href="resampling_methods.html#w05-detail-nested-cv">第 5 章的巢狀 CV</a>。</li>
  </ul>
""")

# ── Lasso 歸零的三種解釋：講義 p.35–39 ──────────────────────────────────
LASSO_WHY_INTRO = r"""
  <h3 id="dx-geom">為什麼 Lasso 會把係數壓成剛好 0：講義的三種解釋</h3>
  <p>講義從三個角度回答「為什麼 Lasso 會歸零、Ridge 不會」：限制式的幾何、正交設計下的閉式解，以及貝氏解讀。</p>
  <h4 id="w06-why-geom">解釋一：限制式的幾何</h4>
  <p>兩者都可以寫成「在預算內讓 RSS 最小」，藉由 Lagrange 乘數和懲罰式連在一起（$s$ 與 $\lambda$ 可對應，但一般不是一對一）：</p>
  $$\min_{\beta}\mathrm{RSS}\ \ \text{s.t.}\ \sum_{j=1}^p|\beta_j|\le s\ \ (\text{Lasso，菱形}),\qquad
    \min_{\beta}\mathrm{RSS}\ \ \text{s.t.}\ \sum_{j=1}^p\beta_j^2\le s\ \ (\text{Ridge，圓}).$$
  <p>最佳子集也能寫成同樣的形式（ESL 第 3 章）：限制換成 $\sum_{j=1}^pI(\beta_j\ne0)\le s$，只是這個問題在計算上不可行。</p>
  <p>RSS 的等高線是以 $\hat\beta^{\mathrm{OLS}}$ 為中心的同心橢圓。解就是<strong>橢圓第一次碰到限制區域的那一點</strong>。菱形有<em>尖角</em>而且尖角落在座標軸上，碰撞很容易發生在尖角，那裡有一個座標是 0。圓沒有尖角，碰到座標軸是機率 0 的事。</p>
"""

LASSO_WHY_DIAG = r"""
  <h4 id="w06-why-diag">解釋二：正交設計下的閉式解（習題 6）</h4>
  <p>考慮最簡單的情況：$n=p$，$X$ 是對角元素為 1 的對角矩陣，並省略截距。最小平方問題變成逐個座標最小化 $\sum_{j=1}^p(y_j-\beta_j)^2$，解為 $\hat\beta_j=y_j$。加上兩種懲罰後：</p>
  $$\text{Ridge：}\ \hat\beta_j^R=\frac{y_j}{1+\lambda},\qquad
    \text{Lasso：}\ \hat\beta_j^L=\begin{cases}y_j-\lambda/2, & y_j>\lambda/2,\\ y_j+\lambda/2, & y_j<-\lambda/2,\\ 0, & |y_j|\le\lambda/2.\end{cases}$$
  <p>Ridge 把每個係數<strong>按同一比例</strong>往 0 縮，$y_j$ 再小也只是變小，不會等於 0。Lasso 則是<strong>軟門檻</strong>（soft-thresholding）：每個係數往 0 平移 $\lambda/2$，絕對值不到 $\lambda/2$ 的直接變成 0。例如 $\lambda=2$、$y_j=0.8$：Ridge 給 $0.8/3\approx0.27$，Lasso 給 $0$；$y_j=3$ 時 Ridge 給 $1$，Lasso 給 $2$。講義指出，一般的 $X$ 沒有這麼乾淨的公式，但「Ridge 等比例收縮、Lasso 軟門檻」的主要想法仍近似成立。</p>
""" + detail("w06-detail-diag-closed-form", "推導：對角設計下 Ridge 與 Lasso 的解", r"""
  <p><strong>Ridge。</strong>逐座標最小化 $(y_j-\beta_j)^2+\lambda\beta_j^2$。微分得 $-2(y_j-\beta_j)+2\lambda\beta_j=0$，所以 $\beta_j=y_j/(1+\lambda)$；二階導數 $2(1+\lambda)>0$，是唯一最小值。</p>
  <p><strong>Lasso。</strong>逐座標最小化 $g(\beta_j)=(y_j-\beta_j)^2+\lambda|\beta_j|$。分三種情況：</p>
  <ul>
    <li>$\beta_j>0$：$g'=-2(y_j-\beta_j)+\lambda=0$，得 $\beta_j=y_j-\lambda/2$。這個解要成立，必須 $y_j-\lambda/2>0$，也就是 $y_j>\lambda/2$。</li>
    <li>$\beta_j<0$：$g'=-2(y_j-\beta_j)-\lambda=0$，得 $\beta_j=y_j+\lambda/2$，需要 $y_j<-\lambda/2$。</li>
    <li>$\beta_j=0$：絕對值在 0 不可微，改用次梯度：$0\in-2y_j+\lambda[-1,1]$，等價於 $|y_j|\le\lambda/2$。</li>
  </ul>
  <p>三種情況正好把實數線分完，合併就是 $\hat\beta_j^L=\operatorname{sign}(y_j)\,(|y_j|-\lambda/2)_+$。關鍵在第三種情況：$|\beta_j|$ 在 0 有尖角，次梯度是一整段區間 $[-1,1]$，只要 $|y_j|$ 落在 $\lambda/2$ 以內，0 就滿足最優條件。$\beta_j^2$ 在 0 是平滑的，導數只有 0 一個值，只有 $y_j=0$ 時解才會是 0。一般 $X$ 怎麼求解，見本節後面的<a href="#w06-detail-lasso-solution">座標更新</a>。</p>
""")

LASSO_WHY_BAYES = r"""
  <h4 id="w06-why-bayes">解釋三〔選讀〕：貝氏解讀（習題 7）</h4>
  <p>貝氏觀點下，後驗正比於概似乘以先驗：$p(\beta\mid X,Y)\propto f(Y\mid X,\beta)\,p(\beta)$，並假設 $p(\beta)=\prod_{j=1}^pg(\beta_j)$。若 $g$ 是平均為 0 的<strong>常態分布</strong>，後驗眾數（給定資料下最可能的 $\beta$）就是 Ridge 的解；若 $g$ 是平均為 0 的<strong>雙指數（Laplace）分布</strong>，後驗眾數就是 Lasso 的解。兩種先驗的尺度參數都對應到 $\lambda$。</p>
  <p>Laplace 密度在 0 有尖峰，取對數後就是 $-|\beta_j|/b$ 這個在 0 有尖角的懲罰，所以後驗眾數可能剛好停在 0；常態先驗在 0 是平滑的圓頂，後驗眾數通常只會被拉近 0。這和解釋二的「尖角」是同一件事。</p>
"""
