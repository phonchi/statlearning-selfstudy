"""Lecture-aligned Chapter 6 teaching additions after reading-flow organization."""
from bs4 import BeautifulSoup
from lib import detail, proof


def augment(bodies):
    bodies = dict(bodies)
    # Corrections to categorical claims, using the same variance convention as the deck.
    replacements = {
        'BIC 一律罰得比較重，': '在此共用變異數的懲罰式中，BIC 罰得比較重，',
        '選出來的模型一律比較小或一樣大': '比較同一組候選模型時，最優模型的變數數目不會較大（並列時採相同的簡約規則）',
        'PCR 之前為什麼一定要標準化？': 'PCR 之前為什麼通常要標準化？',
        'Ridge、Lasso、PCR、PLS 之前都必須標準化。': 'Ridge、Lasso、PCR、PLS 通常先標準化，或明確交代保留原量尺的理由。',
        'L1 會歸零、L2 不會，差別在形狀不在強弱。': 'L1 的尖角可產生稀疏解；L2 通常只收縮，沒有一般的零係數選擇機制。',
        '不會（用到全部變數）': '不選原始欄，個別 loading 可為零',
        '原始變數", "<strong>不會</strong>': '原始變數", "通常不會',

    }
    for sec in bodies:
        for old, new in replacements.items(): bodies[sec] = bodies[sec].replace(old,new)

    additions = {
'subset': [('subset-foundations','從空模型到逐步搜尋：每一步究竟在比較什麼？',r'''
<p>空模型只含截距，對每筆資料都預測同一個常數；即使沒有預測變數，仍然可以做預測。比較加入變數後的模型時，就以這個常數模型為基準。對平方損失，這個常數是訓練反應的平均值；預測新資料時也要沿用訓練平均，不能先看驗證資料的反應值，再用它們算平均。</p>
''' + proof('w06proofNullMean','平方損失的最佳常數是平均值',r'''
<p>對任意常數 $c$，先寫成 $y_i-c=(y_i-\bar y)+(\bar y-c)$，再展開平方。因為 $\sum_i(y_i-\bar y)=0$，交叉項消失：</p>
$$\sum_i(y_i-c)^2=\sum_i(y_i-\bar y)^2+n(c-\bar y)^2.$$
<p>第二項非負，且只有 $c=\bar y$ 時為零；所以最小 RSS 等於 TSS。這也是含截距模型的 $R^2$ 使用 TSS 當基準的原因。</p>
''') + r'''
<h3>先數資料欄，還是先數原始變數？</h3>
<p>講義的 Credit 有十個原始預測變數，但三類別的變數需要兩個虛擬欄，因此迴歸設計矩陣可有十一個斜率欄。若把虛擬欄分別搜尋，「一個變數」可能指一個欄，而不是整個類別因素。分析前要決定，是逐欄選擇，還是讓整個因素一起進出模型？這會改變候選模型的範圍，也影響選出結果如何解讀。下方 Group Lasso 就是以組為單位選擇的做法。</p>
<p>Credit 圖的每一個點是一個候選模型，紅色前緣只表示同樣大小下的訓練贏家。自由度相同的模型可用 RSS 排序；模型大小不同時，就不能只依 RSS 選出最終模型。講義的 Hitters Lab 則用 Salary 當反應，先移除缺失觀測，再透過設計矩陣處理類別欄。不要把 Credit 的圖上模型大小，當作 Hitters 的結果。</p>
<h3>Backward 與混合逐步法的限制</h3>
<p>前向法錯過 $\{X_2,X_3\}$ 的例子見正文；Backward 的限制方向相反：一旦刪掉某欄，單純後向法不會把它加回。混合逐步法允許加入之後再考慮刪除，但仍不是窮舉所有子集。逐步法的搜尋路徑由 $y$ 決定，選擇偏差的討論見上方「有效模型空間」與「第二階段的驗證」兩個收合區。</p>
<p>高維時，Forward 只在仍可識別的子模型中前進；含截距需要設計矩陣滿欄秩，$n$ 大於欄數才有正殘差自由度。Backward 先需要完整模型可估計；即使軟體用廣義逆算出一組係數，也要另外檢查係數是否唯一，以及常規推論的條件是否成立。</p>
<p>Lab 的自訂迴圈<strong>沒有列入空模型</strong>，因此搜尋範圍和講義的 $M_0,\ldots,M_p$ 不完全相同。ISLP 的完整路徑則包含空模型。讀 argmin 時，要先核對索引是「零起算位置」還是「變數個數」，不能直接把兩者畫上等號。</p>
<p>來源入口：<a href="https://islp.readthedocs.io/en/latest/datasets/Credit.html">Credit 資料字典</a>、<a href="https://islp.readthedocs.io/en/latest/datasets/Hitters.html">Hitters 資料字典</a>、<a href="https://islp.readthedocs.io/en/latest/models/selection.html#forward-selection">ISLP 逐步選擇</a>、<a href="https://scikit-learn.org/1.6/modules/feature_selection.html#sequential-feature-selection">sklearn SequentialFeatureSelector</a>。後者以交叉驗證分數逐步比較，不能未檢查 scoring 就宣稱重現 Lab 的 RSS 路徑。</p>
''')],
'criteria': [('criteria-scale','從 RSS、AIC 到調整後 $R^2$：先分清估計量與比較量尺',r'''
<h3>加變數為何不會增加訓練 RSS？</h3>
<p>只要兩個模型使用同一批觀測、相同平方損失，而舊模型是新模型的子模型，新模型可以把新增係數設為零，得到舊模型的擬合。新模型再最佳化後不可能更差。理由是新增變數後，舊模型仍是一個可行解；這個論證不需要誤差常態，但只適用於訓練 RSS，不能推出測試誤差也會下降。移除不同的缺失列或改成正則化目標後，不能直接套用這個比較。</p>
<h3>軟體的 AIC 和課本的 $C_p$ 不是同一個量尺</h3>
<p>AIC 與 $C_p$ 何時排序相同、各模型重估 $\sigma^2$ 時的 $n\log(\mathrm{RSS}/n)$ 版本，推導都在上方<a href="#w06-detail-criteria-origins">三個準則的懲罰項推導</a>。<code>statsmodels</code> 的 <code>.aic</code>、<code>.bic</code> 屬於重估 $\sigma^2$ 的對數概似尺度，並不是把課本的 $C_p$ 數值改名。只在同一資料、同一反應及相容概似設定下比較；模型用的列數改變，AIC 數字就失去原本的可比性。是否把共同截距與誤差變異數算進 $k$，影響數值常數；所有模型採相同慣例時，共同項不影響排名。</p>
<h3>調整後 $R^2$ 的「值得加入」門檻</h3>
<p>固定 $n$ 與 TSS，最大化調整後 $R^2$ 等於最小化 $\mathrm{RSS}/(n-d-1)$。舊模型有 $d$ 個斜率，再加一個欄後，必須讓 RSS 的下降抵得過少一個殘差自由度，調整後 $R^2$ 才會上升。所以 RSS 降了一點，還不夠讓調整後 $R^2$ 偏好加入新欄。</p>
''' + proof('w06proofAdjustedThreshold','加入一欄何時提高調整後 $R^2$？',r'''
<p>令 $R_0$ 是舊 RSS，$R_1$ 是新 RSS，舊殘差自由度為 $\nu=n-d-1$，新自由度為 $\nu-1&gt;0$。調整後 $R^2$ 增加等價於</p>
$$\frac{R_1}{\nu-1}\lt\frac{R_0}{\nu}\quad\Longleftrightarrow\quad R_0-R_1\gt\frac{R_0}{\nu}.$$
<p>用新模型殘差變異數寫出的單欄部分 F 值為 $(R_0-R_1)/(R_1/(\nu-1))$；上述條件也等價於 $F&gt;1$。這只是選模門檻，不等於常用顯著水準下的假設檢定門檻。</p>
''') + r'''
<p>CV 的選擇目標由 scoring 決定：用 MSE、$R^2$ 或分類對數損失可能得到不同的模型。</p>
<p>延伸對照：<a href="https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.aic.html">OLSResults.aic</a>、<a href="https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.bic.html">OLSResults.bic</a>、<a href="https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.rsquared_adj.html">調整後 $R^2$ 定義</a>。</p>
''')],
'onese': [('selection-cv','模型大小與 one-SE 規則',r'''
<p>設第 $b$ 折、大小 $k$ 的保留資料 MSE 為 $E_{bk}$，先算 $K$ 折的平均，再找最小者 $k^*$。one-SE 規則把可接受區間的上緣設為最佳模型的平均誤差加上<strong>最佳點的</strong>標準誤，最後取仍在區間內的最小 $k$：</p>
$$\hat k=\min\{k:\bar E_k\le \bar E_{k^*}+\widehat{\mathrm{SE}}(\bar E_{k^*})\}.$$
<p>標準誤怎麼估、它為什麼只是粗略指標，以及 <code>RepeatedKFold</code> 的做法，見上方的<a href="#w06-detail-cv-se">CV 標準誤收合區</a>。</p>
<p>講義 Credit 的驗證切分用四分之三訓練、四分之一驗證，CV 用十折；Hitters Lab 則示範五折及 20% 的單次驗證。二者都比較模型大小，但數據與分折設定不同，不能拿誤差值相互核對。</p>
<p>來源：<a href="https://www.cs.cmu.edu/~psarkar/sds383c_16/lecture9_scribe.pdf">講義連結的交叉驗證筆記</a>、<a href="https://scikit-learn.org/1.6/modules/cross_validation.html">sklearn CV 操作</a>。</p>
''')],
'ridge': [('ridge-bias','收縮為何可能更準？偏差與變異的取捨',r'''
<p>不懲罰截距時，$\lambda$ 趨近無限會讓斜率趨近零，預測趨近訓練平均；不是所有預測都趨近零。有限 $\lambda$ 下，Ridge 不具有 Lasso 那樣的門檻選擇機制，但個別係數可能因對稱或恰好沒有方向訊號而等於零。因此「通常不產生稀疏解」比「任何資料都絕不會有零係數」精確。</p>
<p>Ridge 接受一點偏差來減少訓練樣本擾動引起的變異；但 $\lambda$ 太大又會把真正訊號壓掉。因此測試 MSE 常先降後升，不能以「懲罰越強越好」理解正則化。</p>
<p>方法推導：<a href="https://dafriedman97.github.io/mlbook/content/c2/s1/regularized.html">原作者的正則化教材</a>；軟體目標：<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.Ridge.html">Ridge API</a>。</p>
''')],
'lambda': [('lambda-conventions','$\\lambda$ 的名稱、套件的 alpha 與最終效能：Lab 要分三步讀',r'''
<h3>第一步：先確認相同數字是否表示相同懲罰</h3>
<p>sklearn <code>Ridge</code> 最小化 $\mathrm{RSS}+\alpha\|\beta\|_2^2$，因此與本章 Ridge 的 $\lambda$ 相同。<code>Lasso</code> 的目標是 $\mathrm{RSS}/(2n)+\alpha\|\beta\|_1$，乘以 $2n$ 後才對到本章 $\lambda=2n\alpha$。<code>ElasticNet</code> 用混合比 $\rho$，目標是</p>
$$\frac{\mathrm{RSS}}{2n}+\alpha\rho\|\beta\|_1+\frac{\alpha(1-\rho)}2\|\beta\|_2^2.$$
<p>所以 $\rho=0$ 時對到 Ridge 的 $\alpha_{\text{Ridge}}=n\alpha_{\text{ElasticNet}}$；$\rho=1$ 對到 Lasso。不要把 R glmnet 的 alpha（混合比）與 sklearn 的 alpha（懲罰強度）混在一起。Lab 在 Ridge 路徑示範特別乘上樣本數以對照 ElasticNet，後面的手選網格改用 Ridge 自己的尺度。這個倍數來自目標函數的尺度換算，不能解讀成資料量增加後就應任意加強正則化。</p>
<h3>第二步：看搜尋評分，而不只看 estimator.score</h3>
<p><code>GridSearchCV</code> 會最大化 scoring，所以 <code>neg_mean_squared_error</code> 要取負號才是 MSE。若未指定 scoring，回歸估計器通常使用 $R^2$。$R^2$ 與 MSE 在單一固定測試集可作等價排序，但跨折平均時，每折的 TSS 不同，平均 $R^2$ 給的權重不同，未必選到相同 $\lambda$。Lab 畫兩種指標，就是要分清這個差別。</p>
<h3>第三步：選定參數後，分開重擬合與效能評估</h3>
<p>網格搜尋在訓練資料的內層折選 $\lambda$，再用整個訓練資料重擬合。<code>best_score_</code> 是被選中的內層分數，不能當成獨立測試效能。Lab 先示範保留 25%、其餘 75% 內做五折選 $\lambda$，這是單次保留驗證加內部 CV；後面再用外層五折、內層五折的雙層迴圈，每一個外層折都重新選 $\lambda$，得到五個完整調參程序的保留分數。兩個版本都把選參數與最終評估分開，差別在外層只評估一次或輪流評估五折。</p>
<p>將 <code>RidgeCV</code> 或 <code>ElasticNetCV</code> 放在事先標準化整個 X 的後面，並不會自動讓標準化也在其內部每一折重新估計。要嚴格避免前處理看見保留折，使用對完整 <code>Pipeline(StandardScaler, Ridge)</code> 的 <code>GridSearchCV</code>。PCR 的 PCA 與 PLS 的方向估計也遵守同一原則。</p>
<p>查用法：<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.ElasticNet.html">ElasticNet 目標</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.model_selection.GridSearchCV.html">GridSearchCV</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.RidgeCV.html">RidgeCV</a>。成分數或 $\lambda$ 選完後，最終模型仍要在允許使用的完整訓練資料重新擬合；獨立測試集只做最後評估。</p>
''')],
'pcr': [('pcr-appendix','PCA 附錄讀圖：方向、得分、白化與 PCR 的限制',r'''
<p>講義用城市人口 pop 與廣告花費 ad 說明 PCA。先減去每一欄平均，第一方向沿點雲最大的變動方向，第二方向與其垂直。每個點投影到第一方向後的座標是得分，原點到該點的距離不是得分。旋轉座標後，第一得分與原來兩欄通常都有較強關係，第二得分表示第一方向未保留的差異。</p>
<p>這個投影最小化的是<strong>各點到子空間的垂直平方距離</strong>，並不是把 ad 當反應、只最小化其縱向殘差的 OLS 直線。中心化決定方向要穿過平均點；縮放決定哪一種距離／變異受到重視。若原量尺本來具有共同科學意義，可以不標準化；若人口與費用量尺差異很大，標準化讓兩欄各以一個標準差衡量。PCA 不要求變數有相同物理單位，但要明確選定比較尺度。</p>
<h3>附錄矩陣為何看起來轉置了？</h3>
<p>本文用 $n\times p$ 的 $X$（每列一筆觀測），講義附錄用 $p\times n$ 的 $A=X^\top$（每欄一筆）。所以其 $S=AA^\top/(n-1)$ 對應本文的 $X^\top X/(n-1)$，講義得分 $U^\top A$ 對應本文 $XV$。閱讀 $U$、$V$ 時，要連同資料矩陣的排列一起看。</p>
<h3>白化是不是更好的 PCR？</h3>
<p>不是。對相同的保留方向做無懲罰 OLS，各得分的縮放會被迴歸係數抵消，擬合不變；白化的定義與限制見上方<a href="#w06-detail-whitening">共變異數、SVD 與白化</a>。</p>
<h3>解釋 $X$ 的變異，不是解釋 $y$ 的變異</h3>
<p>Lab 的 <code>explained_variance_ratio_</code> 是 PCA 對 $X$ 的變異解釋比例；不能讀成 Salary 的解釋比例。少數 PC 捕捉大部分 $X$ 變異，仍可能漏掉對 $y$ 很重要的低變異方向。講義的模擬有一組把所有反應資訊放在前五個 PC，這才讓 $M=5$ 成為特別有效的結構；一般資料沒有這個保證。$M$ 的選擇應使用預測 CV，而非只以累積 $X$ 變異達到某百分比決定。</p>
<p>PCR 的原始係數限制在前 $M$ 個方向張成的子空間。它保留的是主成分方向，而沒有直接選出一組原始欄。Lab 將 <code>StandardScaler</code>、<code>PCA</code> 與 <code>LinearRegression</code> 放在同一 Pipeline 搜尋 $M$，讓每折重新學方向。只含截距的空模型可另行計算，不能把某個 API 的零成分是否可用當成空模型不存在的理由。</p>
<p>對照：<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.decomposition.PCA.html">PCA API 與得分／解釋變異</a>、<a href="https://scikit-learn.org/1.6/auto_examples/cross_decomposition/plot_pcr_vs_pls.html">PCR 與 PLS 官方例子</a>；完整非監督式解讀見<a href="unsupervised_learning.html">非監督式學習章</a>。</p>
''')],
'pls': [('pls-reading','PLS 與 OLS：看了 $y$ 的方向是否一定較好？',r'''
<p>PLS 的第一方向由 $X^\top y$ 決定，因此需要已觀測的訓練反應；PCR 的方向只看 $X$。講義用「與 $y$ 關係愈強，權重愈大」解釋第一方向，這需要先標準化（見<a href="#w06-detail-pls-covariance">PLS 的共變異目標</a>）。</p>
<p>PLS 第一方向不等於直接求 OLS 的係數：OLS 用 $X^\top X$ 的逆（或廣義逆）處理變數之間的相關，PLS 從 $X^\top y$ 的方向開始，再逐步消去已解釋的成分。對完整秩方向使用足夠多成分，PLS 可重現 OLS 擬合；保留少數方向才施加低維限制。PLS 會形成新方向並逐步扣除已解釋的部分，不能只把各欄單變數回歸的預測值相加。</p>
<p>「看了 $y$」可避免 PCR 忽略低變異預測方向，但也可能把訓練雜訊當訊號。增加 $M$ 仍有偏差與變異取捨，所以 Lab 對 <code>PLSRegression(n_components=M)</code> 做 CV，而不是預設 $M$ 越大越好。其 <code>scale=True</code> 預設會在擬合時縮放 $X$ 與 $y$，若另加 StandardScaler 要分清每一步處理什麼；預測會回到 $y$ 的原量尺。</p>
<p>比較 PCR、PLS、Ridge 或 Lasso 時，使用同樣資料、同樣保留折與相同 MSE 定義。講義圖中的方向關係和 Lab 的 Hitters 最佳成分數，不構成某方法在所有資料上比較好的證據。</p>
<p>來源：<a href="https://scikit-learn.org/1.6/modules/cross_decomposition.html">PLS 官方方法說明</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.cross_decomposition.PLSRegression.html">PLSRegression API</a>。</p>
''')],
'highdim': [('highdim-cautions','$p$ 接近或超過 $n$：擬合完美、預測失敗與選模推論',r'''
<p>講義先用 $n=2$、截距加一個斜率示範：兩點可被直線完全通過，但沒有剩餘殘差自由度可估誤差變異。問題不是常態假設突然消失，而是訓練資料已不足以同時估模型與剩餘誤差。一般含截距模型的殘差自由度是 $n-\operatorname{rank}([1,X])$；若飽和且滿列秩，$\mathrm{RSS}=0$，通常使用 $\mathrm{RSS}/(n-p-1)$ 的估變異公式不再可用。</p>
<p>下一張圖固定 $n=20$，加入與反應沒有關係的特徵：訓練 $R^2$ 趨近一、訓練 MSE 趨近零，測試 MSE 卻變大。這不是新增資訊的功效，而是更多自由度能追蹤樣本中的偶然變動。訓練完美不能證明擷取到真實關係，低維與高維都需要獨立的預測評估。</p>
<p>講義的 Lasso 比較另固定 $n=100$，只有二十個真正有用特徵，再改變總 $p$ 與懲罰強度。即使真正訊號沒有增加，更多無關欄仍增加誤選、估計與調參的困難。這個例子說明，除了採用正則化，也必須選好 $\lambda$。「Lasso 可用於 $p&gt;n$」並不表示「任何 $\lambda$ 都能克服高維」。</p>
<p>高維下，若多欄高度相關，很多不同係數組合可能給出相似預測。Lasso 挑出其中一欄，不等於其他欄沒有作用；Ridge 分散係數，不等於每欄皆有獨立證據。若選完變數後，直接套用事先固定模型的 p 值，就漏算了用同一份反應資料挑選欄位的影響，產生選擇後推論問題。可以先以外部資料驗證預測穩定性，但預測驗證本身不提供因果結論。</p>
<p>資訊準則若依賴全模型殘差估 $\sigma^2$，在這裡失去原本的計算前提；CV 則能比較可擬合的 Ridge、Lasso、PCR、PLS，但搜尋、縮放與方向估計仍必須在折內完成。評估模型選擇程序時，再用外層保留資料將選擇與報告分開。</p>
''')],
    }
    for sec, items in additions.items():
        for slug, title, body in items:
            bodies[sec] += '\n' + detail('w06-detail-'+slug, title, body)
    # Expand existing topic blocks in place, preserving deep links and avoiding duplicates.
    extra = {
'w06-detail-shrinkage-map': r'''<p>Laplace 是連續分布，先驗本身沒有在 $\beta=0$ 放正機率的點質量，所以不能解讀成「每個係數事前有某機率恰為零」；歸零來自取後驗眾數時 L1 懲罰的尖角。原作者教材：<a href="https://dafriedman97.github.io/mlbook/content/c2/s1/bayesian.html#bayesian-regression">Bayesian Regression</a>。</p>''',
'w06-detail-deviance': r'''<h3>為何分類要輸入機率？</h3><p>離差評估的是模型為已觀察標籤分配了多少機率。預測相同類別的兩個模型，若一個機率接近 0.5、另一個非常接近正確標籤，分類錯誤率可以相同而離差不同；錯誤且過度自信時，對數損失會很大。二元逐筆 Bernoulli 的飽和概似為零，故離差是總對數損失的兩倍；合併成分組二項計數時，飽和項通常不再是零，要重新用完整定義。</p><p>sklearn 的 <code>predict_proba</code> 欄序由 <code>classes_</code> 決定；<code>log_loss</code> 的平均或總和由 <code>normalize</code> 決定。相同樣本數時兩者排序一致，數值仍相差 $n$ 倍。若要求 AIC／BIC 的常規最大概似版本，也要檢查邏輯斯模型是否取消預設正則化，而非直接把懲罰擬合當 MLE。</p><p>來源：<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.metrics.log_loss.html">log_loss 定義</a>、<a href="https://www.statsmodels.org/stable/generated/statsmodels.genmod.families.family.Binomial.deviance.html">Binomial deviance</a>。</p>'''
    }
    for sec in bodies:
        soup=BeautifulSoup(bodies[sec],'html.parser')
        for pid, html in extra.items():
            d=soup.find(id=pid)
            if d:
                content=d.select_one('.detail-body')
                content.append(BeautifulSoup(html,'html.parser'))
        bodies[sec]=str(soup)
    # 講義 p.39 的貝氏解讀放在「解釋三」旁，不留在節末。
    soup = BeautifulSoup(bodies['lasso'], 'html.parser')
    node = soup.find(id='w06-detail-shrinkage-map')
    target = soup.find(id='w06-lasso-path')
    if node is None or target is None:
        raise ValueError('Missing shrinkage-map detail or lasso path heading')
    target.insert_before(node.extract())
    bodies['lasso'] = str(soup)
    # Normalize the formula overview to the same likelihood convention as the explanation.
    overview = BeautifulSoup(bodies['reference'], 'html.parser')
    for row in overview.select('tr'):
        cells = row.find_all('td')
        if cells and cells[0].get_text(strip=True) == 'AIC':
            cells[1].string = r'$-2\hat\ell+2k$'
            cells[2].string = '最大概似版本；共同固定誤差變異數時與 $C_p$ 型排序一致'
        if cells and cells[0].get_text(strip=True) == 'Ridge（L2）':
            cells[3].string = '通常不會；不是變數選擇方法'
    bodies['reference'] = str(overview)

    # Preserve the original lecture reading entrances beside the corresponding topic.
    source_links = [('w06-detail-subset-foundations', 'https://math.stackexchange.com/questions/2554243/understanding-the-mean-minimizes-the-mean-squared-error'), ('w06-detail-subset-foundations', 'https://islp.readthedocs.io/en/latest/datasets/Credit.html'), ('w06-detail-subset-foundations', 'https://quantifyinghealth.com/best-subset-selection/'), ('w06-detail-criteria-scale', 'https://stats.stackexchange.com/questions/167827/why-is-sum-of-squared-residuals-non-increasing-when-adding-explanatory-variable'), ('w06-detail-criteria-scale', 'https://stats.stackexchange.com/questions/205439/aic-equivalent-to-mallows-cp-and-mallows-cp-unbiased-for-test-mse'), ('w06-detail-criteria-scale', 'https://stats.stackexchange.com/questions/490056/aic-bic-formula-wrong-in-james-witten'), ('w06-detail-criteria-scale', 'https://en.wikipedia.org/wiki/Coefficient_of_determination#Adjusted_R2'), ('w06-detail-selection-cv', 'https://www.cs.cmu.edu/%7Epsarkar/sds383c_16/lecture9_scribe.pdf'), ('w06-detail-ridge-bias', 'https://dafriedman97.github.io/mlbook/content/c2/s1/regularized.html'), ('w06-detail-lasso-solution', 'https://dafriedman97.github.io/mlbook/content/c2/s1/regularized.html#lasso-regression'), ('w06-detail-penalty-constraint', 'https://stats.stackexchange.com/questions/348494/the-proof-of-equivalent-formulas-of-ridge-regression'), ('lasso', 'https://stats.stackexchange.com/questions/348308/graphical-interpretation-of-lasso'), ('lasso', 'https://stats.stackexchange.com/questions/414491/understanding-lasso-regressions-sparsity-geometrically'), ('lasso', 'https://stats.stackexchange.com/questions/350046/the-graphical-intuiton-of-the-lasso-in-case-p-2?noredirect=1&lq=1'), ('w06-detail-lasso-solution', 'https://stats.stackexchange.com/questions/17781/derivation-of-closed-form-lasso-solution'), ('w06-detail-shrinkage-map', 'https://dafriedman97.github.io/mlbook/content/c2/s1/bayesian.html#bayesian-regression'), ('w06-detail-shrinkage-map', 'https://ekamperi.github.io/mathematics/2020/08/02/bayesian-connection-to-lasso-and-ridge-regression.html'), ('w06-detail-uncorrelated', 'https://stats.stackexchange.com/questions/171324/what-is-the-relationship-between-orthogonal-correlation-and-independence'), ('w06-detail-uncorrelated', 'https://stats.stackexchange.com/questions/153928/why-are-principal-component-scores-uncorrelated'), ('w06-detail-pcr-appendix', 'https://stats.stackexchange.com/questions/22329/how-does-centering-the-data-get-rid-of-the-intercept-in-regression-and-pca'), ('w06-detail-pls-covariance', 'https://stats.stackexchange.com/questions/32464/how-does-the-correlation-coefficient-differ-from-regression-slope'), ('w06-detail-pls-covariance', 'https://stats.stackexchange.com/questions/179733/theory-behind-partial-least-squares-regression'), ('w06-detail-lar-group', 'https://scikit-learn.org/stable/modules/linear_model.html#least-angle-regression'), ('w06-detail-lar-group', 'https://group-lasso.readthedocs.io/en/latest/'), ('w06-detail-deviance', 'https://stackoverflow.com/questions/50975774/calculate-residual-deviance-from-scikit-learn-logistic-regression-model')]
    for anchor, url in source_links:
        from html import escape
        for sec in bodies:
            soup = BeautifulSoup(bodies[sec], 'html.parser')
            node = soup.find(id=anchor)
            if node:
                content = node.select_one('.detail-body') or node
                if not content.find('a', href=url):
                    content.append(BeautifulSoup('<p class="source-links">講義延伸來源：<a href="'+escape(url,quote=True)+'">'+escape(url.split('/')[2])+'</a>。</p>', 'html.parser'))
                bodies[sec] = str(soup)
                break
        else:
            # A section id belongs to the outer HTML frame, not its BODIES fragment.
            if anchor in bodies:
                bodies[anchor] += '<p class="source-links">講義延伸來源：<a href="'+escape(url,quote=True)+'">'+escape(url.split('/')[2])+'</a>。</p>'
    return bodies
