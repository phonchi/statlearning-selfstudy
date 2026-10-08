"""Lecture Ch12 teaching expansion, after historical reading-flow cleanup."""
from hashlib import sha256
from lib import detail, card, lab_code, lab_output
from teaching_scope_ch7_8_9_12 import Tree

def extend(bodies, sec, pid, content):
    marker='<!-- lecture-alignment-ch12:'+pid+':'+sha256(content.encode()).hexdigest()[:12]+' -->'
    if marker in bodies[sec]: return
    tree=Tree(bodies[sec]);node=next(n for n in tree.nodes if n['attrs'].get('id')==pid)
    assert node['end'] is not None
    pos=bodies[sec].rfind('</div>',node['inner'],node['end'])
    assert pos >= node['inner']
    bodies[sec]=bodies[sec][:pos]+marker+content+bodies[sec][pos:]

def add(bodies, sec, pid, title, content):
    if 'id="'+pid+'"' not in bodies[sec]: bodies[sec]+=detail(pid,title,content)

def lab(cell,title,stop=None,out=False):
    code=lab_code(12,cell)
    if stop: code=code[:code.index(stop)].rstrip()
    return card(title,code,lab_output(12,cell) if out else None,src='<code>Ch12-unsup-lab-zh.ipynb</code> · 儲存格 '+str(cell))

def augment(bodies):
    # Refine the original blanket statement, retaining the warning about informative missingness.
    bodies['completion']=bodies['completion'].replace('1. 缺失必須是隨機的','1. 缺失機制需要檢查').replace('「電子秤剛好沒電」可以補；「病人太重上不了秤」不行——缺失本身帶著資訊，\n  補出來的值會系統性偏低。','隨機漏測與「病人太重上不了秤」的缺失不同：後者直接依賴未觀測的重量，單靠已觀測資料的低秩補值可能系統性偏低。即使符合 MAR，也不自動保證這個特定補值演算法無偏。')
    bodies['manifold']=bodies['manifold'].replace('這一節是課堂沒細講的延伸（講義 12 · p.39–53），第一輪可以直接跳過去看\n  <a href="#exercises">EX 練習</a>。t-SNE 在論文裡到處都是，解讀前應先了解它的限制。','這一節接續線性 PCA，說明講義的流形學習與 t-SNE。先讀核心直覺，再展開演算法與限制。')
    bodies['manifold']=bodies['manifold'].replace('它沒有 <code>transform()</code>', 'sklearn 的 <code>TSNE</code> 沒有 <code>transform()</code>')
    extend(bodies,'pca','w07-detail-pca-advanced',r'''
<h3>把係數、得分與資料形狀連在一起</h3>
<p>每列是一筆觀測、每欄是一個特徵時，$X$ 是 $n\times p$，一個 loading $v$ 有 $p$ 個係數，投影 $z=Xv$ 則有 $n$ 個得分。USArrests 有 50 個州、4 個變數，因此每個方向有 4 個負荷量，每個方向上有 50 個州的得分。得分對應觀測，負荷量對應特徵，兩者的長度與用途不同。</p>
<p>置中後 $\operatorname{Var}(Xv)=v^TSv$，限制 $v^Tv=1$ 讓不同方向在同一長度下比較。把 $v$ 展開成共變異數矩陣的正交特徵向量 $v=\sum_j a_je_j$，就有 $v^TSv=\sum_j a_j^2\lambda_j$ 且 $\sum_j a_j^2=1$；這是特徵值的加權平均，最大值自然是最大的特徵值。第二方向再限制與第一方向正交，依序找下一個。</p>
<p>特徵向量正交給 $\operatorname{Cov}(Xv_j,Xv_k)=v_j^TSv_k=0$。這是「不相關」，不必然是統計獨立；要推到獨立還需要額外分布條件，例如聯合 Gaussian。置中使各欄和為零，所以 rank 最多 $n-1$；若另有線性相依，實際非零主成分還會更少。</p>
<p>若某特徵值重複，對應空間中的任一正交基都可用。此時不唯一的不只正負號，整個重複特徵值子空間都可旋轉；仍可比較該空間的投影與累積解釋變異。</p>
<p>閱讀：<a href="https://rich-d-wilkinson.github.io/MATH3030/4.2-pca-a-formal-description-with-proofs.html" target="_blank" rel="noopener">PCA 的正式推導</a>、<a href="https://scikit-learn.org/1.6/modules/decomposition.html#pca" target="_blank" rel="noopener">PCA 與 SVD 的實作</a>。</p>''')
    add(bodies,'biplot','w07-detail-biplot-reading','USArrests 的 biplot：點與箭頭各在回答什麼？',r'''
<p>圖上的州是觀測；箭頭是變數。觀測點的 PC1／PC2 座標是得分，描述每個州在兩個方向的位置；箭頭的座標由負荷量決定，描述原變數如何組成這兩個方向。講義的圖用兩套刻度呈現，因此不能直接把箭頭尖端與州名的距離當成統計距離。</p>
<p>PC1 的三個犯罪變數負荷方向相近，可以理解為共同的犯罪強度方向；PC2 額外表達城市人口比例與犯罪變數之間的差異。沿某一箭頭方向的州，通常在該變數的標準化值較高，但這是前兩個方向的投影摘要，不是每一欄原值的完整重建。</p>
$$\hat x_{ij}^{(2)}=z_{i1}v_{j1}+z_{i2}v_{j2}.$$
<p>要回到原單位，還要乘回該欄標準差並加上平均值。只有在採用合適的 biplot 縮放且兩維保留足夠資訊時，箭頭角度才可近似反映相關性；不能忽略圖的縮放方式與未顯示主成分。</p>
<p>Lab 對各欄先標準化，再用 <code>fit_transform</code> 得得分、用 <code>components_.T</code> 讀負荷量。軟體可能把某個方向整體翻號，應同時翻轉得分及箭頭來比較，不能只翻一邊。</p>
<p>資料：<a href="https://islp.readthedocs.io/en/latest/datasets/USArrests.html" target="_blank" rel="noopener">USArrests 的欄位意義</a>。</p>''')
    extend(bodies,'lowrank','w07-detail-lowrank-advanced',r'''
<h3>SVD 如何一次給出方向、得分與誤差？</h3>
<p>把中心化矩陣寫成 $X=UDV^T$。$V$ 的欄是特徵方向，$XV=UD$ 是得分，$D$ 的非負對角元素是奇異值。numpy 的第三個回傳值其實是 $V^T$；Lab 把它命名為 <code>V</code>，所以讀程式時必須以運算形狀判斷，不能只靠變數名稱。</p>
<p>取前 $M$ 個方向，重建 $X_M=U_MD_MV_M^T$；因為不同奇異方向正交，捨棄第 $M+1$ 個以後的方向帶來平方誤差 $\sum_{m>M}d_m^2$。因此增加 rank 會降低完整資料上的重建誤差，但沒有自動告訴我們哪個方向是訊號、哪個是雜訊。</p>
<p>講義把共變異數除以 $n$，sklearn 的 <code>explained_variance_</code> 則使用 $n-1$。兩者的特徵向量相同，特徵值相差比例 $n/(n-1)$；解釋變異比例不受共同分母影響。比較來源時應先對齊分母，而不是把正常尺度差異判成錯誤。</p>
<p>資料很大時，randomized SVD 先以隨機投影抓住主要子空間，再在較小矩陣做分解；oversampling 與 power iteration 改善近似品質。它是在近似主要奇異方向，不能宣稱任意近似設定都得到精確 SVD。</p>
<p>閱讀：<a href="https://github.com/fastai/numerical-linear-algebra" target="_blank" rel="noopener">講義連結的數值線性代數教材</a>、<a href="https://scikit-learn.org/1.6/modules/decomposition.html#pca-using-randomized-svd" target="_blank" rel="noopener">Randomized PCA</a>。</p>''')
    extend(bodies,'pve','w07-detail-pca-rank-selection',r'''
<h3>「選幾維」先問要保留什麼</h3>
<p>若只想描述資料，可先看每個方向的 PVE、累積 PVE 與 scree plot 的轉折，再檢查負荷量是否有可解釋的意義。若目的是分類或迴歸，rank 應依下游驗證誤差選；小變異方向可能含關鍵的回應訊號。</p>
<p>若目的是補未見格子，則可以在原本已觀測的格子中留出一部分，只用其餘格子擬合，再計算留出格子的預測誤差。完整新資料的重建誤差會隨 rank 增加而下降，光做這種評分常把 rank 推到最大，並不能取代「遮住格子後預測」的問題。</p>
<p>講義連結的高維資訊準則針對特徵值的訊號／雜訊模型設計懲罰；它不是把迴歸 AIC 的參數數量直接搬到 PCA。若沒有採用該論文的模型條件，就不能只用其公式宣稱選到真實維度。</p>
<p>閱讀：<a href="https://link.springer.com/article/10.1007/s00362-021-01276-7" target="_blank" rel="noopener">講義列出的高維 PCA 選維度研究</a>。</p>''')
    extend(bodies,'scaling','w07-detail-scaling-advanced',r'''
<h3>標準化、PCA 白化與 ZCA 白化要分清楚</h3>
<p>標準化逐欄減平均、除標準差，讓每個原變數有單位變異，但不會消除變數間的相關。PCA 白化先旋轉到主成分，再以特徵值平方根縮放每個非零方向，所以得分座標的共變異數成為單位矩陣。ZCA 則把這些白化座標旋轉回原座標系；通常保留原特徵數，卻已改變各方向尺度。</p>
<p>白化會放大小特徵值方向，連同其中的雜訊也可能放大。特徵值為零時不能直接取倒數；需限制在非零子空間或加入明確的正則化。維度縮減後再做 ZCA 所得矩陣的原座標共變異數是投影矩陣，不是完整的 $p\times p$ 單位矩陣。</p>
<p>USArrests 的欄位單位與尺度不同，因此標準化有明確理由；NCI60 的基因表現有共同量測單位，是否標準化則改變分析目標：標準化會讓低變異基因與高變異基因同等加權，並非一律較好。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.decomposition.PCA.html" target="_blank" rel="noopener">PCA 的 whiten 介面</a>。</p>''')
    extend(bodies,'completion','w07-detail-completion-advanced',r'''
<h3>跟著 USArrests 補值流程看限制</h3>
<p>Lab 從已標準化、置中的 <code>USArrests_scaled</code> 開始，再挖出缺失格。<code>low_rank()</code> 每次直接對當前填補矩陣做 SVD，保留前 M 項；它沒有逐輪重新算均值、置中或加回均值。迭代時觀測格永遠保留原值，只有缺失格由目前的低秩估計覆蓋，因此觀測值仍能約束下一輪的方向。</p>
<p>講義用 50 州、4 欄的資料，在 20 個州各挖掉一格，共 20／200＝10% 缺失，取一個主成分。100 次抽樣得到的平均相關約 $0.63$、標準差 $0.11$，是講義的重複抽樣摘要；以完整資料的主成分估計被遮格子得到約 $0.79$，已使用真值資訊，不能當成可部署的公平比較。</p>
<p>一次 Lab 的相關係數不應要求恰等於講義的 100 次平均。補值仍需檢查絕對誤差與偏差，因為相關高也可能整體偏移。推薦系統裡沒有評分通常還與使用者選擇有關，不是隨機漏測；低秩模式有用，但缺失機制與冷啟動使用者／項目仍要另外處理。</p>
<p>閱讀：<a href="https://www.statlearning.com/" target="_blank" rel="noopener">ISLP：Matrix Completion 與推薦系統</a>。</p>''')
    extend(bodies,'kmeans','w07-detail-kmeans-advanced',r'''
<h3>為什麼一定要重新指派，再重新算平均？</h3>
<p>固定中心时，每筆資料選最近中心會降低它對平方和的貢獻；固定指派時，一群的平均是平方距離總和最小的位置。輪流做這兩件事可使目標不增加，直到指派穩定或改善小於停止門檻，但只能保證局部解。</p>
<p>Lab 的 <code>n_init=20</code> 代表以多組初始化重新執行，再選群內平方和較小的一次。它降低落入差解的風險，沒有保證全域最小。群的編號只是名稱：兩次結果若只交換 0／1，分群實際相同，不能把編號不一致當成不穩定。</p>
<p>K-means 適合用平方歐氏距離定義的緊密群。細長、不同密度或不同大小的真實群，可能被它切開或併在一起。$K$ 增加會降低訓練群內平方和，因此不能只選平方和最小的 $K$；需要領域目標、結構穩定性與其他驗證。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/clustering.html#k-means" target="_blank" rel="noopener">K-means 與初始化</a>。</p>''')
    extend(bodies,'hclust','w07-detail-hclust-advanced',r'''
<h3>樹狀圖是合併歷史，不是平面地圖</h3>
<p>讀兩筆觀測的相似性，要看它們首次進入同一分支的合併高度，不看兩個葉節點的左右距離。左右子樹可以交換而不改變任何合併，這就是講義中觀測 9 與 2 看起來靠近、卻不比其他同高度合併的點更接近的原因。</p>
<p>切低一點的樹得到較多群，每個細群都嵌在更高切割的一個大群中。若最佳兩群按性別分、最佳三群按國籍分，兩種分類未必能同時由一棵巢狀樹表達。階層方法保留的是一套巢狀合併，不是每個 $K$ 都獨立求到最佳分群。</p>
<p>Centroid linkage 可能發生新合併高度低於舊高度的 inversion；Ward 的平方和增加量也不能拿去配任意非歐氏相異度。Single linkage 可以沿近鄰形成彎曲群，但一條稀疏鏈也可能把兩團接起來；Complete linkage 使用最遠距離，離群點可能明顯影響合併，不能把「較少鏈狀群」等同不受離群值影響。</p>
<p>Lab 用 <code>compute_linkage</code> 把 sklearn 合併結果轉給 scipy 的 <code>dendrogram</code>，再用 <code>cut_tree</code> 取群標籤。<code>color_threshold</code> 是畫圖顏色門檻，不能以改顏色就當成模型已產生新的群標籤。</p>
<p>閱讀：<a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html" target="_blank" rel="noopener">各種 linkage 與距離條件</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.cluster.FeatureAgglomeration.html" target="_blank" rel="noopener">把階層式分群用在特徵</a>。</p>''')
    extend(bodies,'practical','w07-detail-density',r'''
<h3>從 DBSCAN 的固定密度走到 HDBSCAN 的密度階層</h3>
<p>DBSCAN 的群由核心點的連通性決定。核心點周圍的邊界點可以加入群，但不繼續向外擴張；離群點可能先被標成雜訊，稍後才發現它屬於另一個核心點的邊界。兩個群都能接到的邊界點可能受處理順序影響，因此「每次都得到完全相同標籤」需要區分核心群與邊界指派。</p>
<p>HDBSCAN 以核心距離修正點對距離，$d_{\rm mr}(a,b)=\max\{d_{\rm core}(a),d_{\rm core}(b),d(a,b)\}$。稀疏區域的點即使偶然靠近，也會被較大的核心距離隔開。由這種距離建立最小生成樹及密度階層，再用 <code>min_cluster_size</code> 壓縮過小分支，依持續性選群。</p>
<p><code>min_cluster_size</code> 控制什麼大小算一個可保留群；<code>min_samples</code> 控制密度判斷的保守程度。較大 <code>min_samples</code> 通常讓更多點變成雜訊，但不能把這兩個參數當成同一個。HDBSCAN 能比較多種密度尺度，仍會受資料尺度、距離和群選擇設定影響。</p>
<p>Lab 使用外部 <code>hdbscan</code> 套件，而不是 sklearn 的同名估計器；兩者對 <code>min_samples</code> 是否包含自身的約定不同，不能只換 import 就宣稱設定完全相同。原 Lab 的兩種密度資料正好說明：固定一組 DBSCAN 門檻可能把稀疏群判成雜訊，同時又把密群過度合併。</p>
<p>阅读：<a href="https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html" target="_blank" rel="noopener">HDBSCAN 的密度階層</a>、<a href="https://hdbscan.readthedocs.io/en/latest/parameter_selection.html" target="_blank" rel="noopener">兩個大小參數</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.cluster.HDBSCAN.html" target="_blank" rel="noopener">sklearn 與外部實作的差別</a>。</p>''')
    add(bodies,'practical','w07-detail-density-lab','跟著 Lab 解讀 DBSCAN：群標籤、核心點與雜訊',r'''
<p>Lab 先產生三中心資料並標準化，再以 <code>eps=0.3, min_samples=10</code> 執行 DBSCAN。<code>labels_</code> 為每筆資料的群編號，<code>-1</code> 是雜訊；群數應排除這個標籤。<code>core_sample_indices_</code> 另指向核心點，因此「不是核心」還要再分邊界點與雜訊。</p>'''+lab(140,'原 Lab：DBSCAN 與群数','\nprint')+r'''
<p>這個模擬範例保留已知 <code>labels_true</code>，可以做外部檢查；真實未標記資料則沒有這個答案。ARI 比較成對觀測是否被放在同群並校正偶然一致，不要求群編號相同。輪廓係數用群內平均距離 $a_i$ 與到最近其他群的平均距離 $b_i$ 定義 $s_i=(b_i-a_i)/\max(a_i,b_i)$；它量的是所選距離下的緊密程度，不是群存在的 p 值。只有一群、每點一群或沒有可用群時，輪廓係數不適用；有雜訊時還需說明是否把它當作一群參與計算。</p>
<p>後續 Lab 在不同密度資料上變更 <code>eps</code>／<code>min_samples</code>，再比較 HDBSCAN 的 <code>min_cluster_size</code>。讀圖時同時看哪些點被保留、哪些點標成雜訊，不能只比較群數。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/clustering.html#clustering-performance-evaluation" target="_blank" rel="noopener">分群的內部與外部評估</a>。</p>''')
    extend(bodies,'practical','w07-detail-mixed-clustering',r'''
<h3>類別編碼為什麼會改變相似性的意思？</h3>
<p>把名目類別寫成 0、1、2 會人為加入次序與距離。One-hot 編碼消除這個次序，卻也改變欄位數與權重；稀有類別、連續尺度與大量二元欄仍可能主導距離。只用連續特徵可避免錯誤的類別距離，但也可能丟掉真正重要的類別資訊。</p>
<p>k-prototypes 明確把數值平方距離和類別不一致成本相加，所以需選兩部分的相對權重；FAMD 則先形成對混合欄位可比較的表示，再分群。兩者在回答不同問題，沒有不需領域判斷的自動預設。</p>
<p>以分群做監督式前處理時，群中心或特徵合併只能在每個訓練折估計。Lab 延伸的「到各群中心距離」是一組連續特徵；群編號是任意名目類別，不能直接當成連續數字。半監督情境可先找代表點請人標註，再把標籤傳到同群，但同一群可能包含不同的真實類別，須檢查群內類別是否一致，以及邊界點是否適合傳遞標籤。</p>
<p>混合模型會對每筆資料給各成分的責任值，通常仍把離群點分給某些成分。若想明確拒絕離群資料，需要離群成分或偵測規則；不能把一般 Gaussian mixture 說成自動具有 DBSCAN 的雜訊標籤。</p>
<p>閱讀：<a href="https://github.com/nicodv/kmodes" target="_blank" rel="noopener">k-modes／k-prototypes</a>、<a href="https://maxhalford.github.io/prince/famd/" target="_blank" rel="noopener">Prince：FAMD</a>、<a href="https://www.nature.com/articles/s41598-021-83340-8" target="_blank" rel="noopener">混合資料分群比較的研究條件</a>。</p>''')
    add(bodies,'practical','w07-detail-nci60-lab','NCI60：先做無監督探索，再對照癌症類型',r'''
<p>NCI60 的 64 个細胞株各有 6830 個基因表現特徵。癌症類型已有標籤，但 PCA 與分群時不使用；完成後才上色與製作交叉表。這正是「標籤只用於解讀」與「用標籤選擇模型」的差別。</p>'''+lab(159,'原 Lab：NCI60 的標準化與 PCA')+r'''
<p>Lab 的碎石圖在前幾個方向出現轉折，前七個主成分累積約解釋四成變異。可先觀察這些方向，但剩下六成仍可能含有訊號；前兩個成分也未必能分開所有癌症類型。</p>
<p>接著比較 complete、average 與 single linkage，再切成四群與癌症標籤交叉比較。白血病細胞株集中，而乳癌細胞株分散，可能反映生物異質性，也可能與量測、尺度或分析選擇有關。單張交叉表不足以建立新的疾病亞型。</p>'''+lab(172,'原 Lab：四群與已知癌症類型的交叉表')+r'''
<p>最後比較四群 K-means 與階層分群，並改用前五個 PCA 得分做階層分群。前處理改變了距離：原基因空間中的差異可能被捨棄，因此兩種分群不同是需要解讀的結果，不是必定哪一種錯誤。群編號換名不改變群成員，應用交叉表或對編號不敏感的指標比較。</p>
<p>資料：<a href="https://islp.readthedocs.io/en/latest/datasets/NCI60.html" target="_blank" rel="noopener">NCI60 的特徵與標籤</a>。</p>''')
    extend(bodies,'manifold','w07-detail-tsne-algorithm',r'''
<h3>對回講義的演算法，避免三個記號陷阱</h3>
<p>高維 SNE 的鄰居機率逐列正規化；對稱 t-SNE 的低維機率則對所有非對角配對做全域正規化。兩種分母不能混用。SNE 的單項 $p\log(p/q)$ 可以為負，完整 KL 才非負；講義的兩個單項成本例子是在說明不對稱懲罰，並不是完整散度的範例。</p>
<p>t-SNE 梯度中的 $p_{ij}-q_{ij}$ 已經包含吸引與排斥；不能再多乘一次 $q_{ij}$ 而未補回正規化常數。最佳化應沿負梯度更新，因此 $p_{ij}>q_{ij}$ 的點對在其他項不變時相互靠近。把梯度寫成加法更新時，必須同步改變差向量的方向。</p>
<p>Lab 設 <code>init="pca"</code> 讓初始座標帶有部分全域線性結構，並設 <code>learning_rate="auto"</code>。sklearn 對 learning rate 的數值定義與部分其他 t-SNE 實作相差四倍；引用「樣本數／early exaggeration」的經驗公式時必須核對實作，不直接抄成所有套件共用的數字。</p>
<p>Perplexity 是熵轉回的有效鄰居數。若機率在 $m$ 個鄰居上均勻，熵為 $\log_2m$，perplexity 就是 $m$；真實權重通常不均，因此它不是硬性的第 $k$ 近鄰截斷。不同樣本可得到不同 $\sigma_i$，這也解釋為何不同密度區域在圖上可能被放大／壓縮。</p>
<p>閱讀：<a href="https://lvdmaaten.github.io/publications/papers/JMLR_2008.pdf" target="_blank" rel="noopener">t-SNE 原始論文</a>、<a href="https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf" target="_blank" rel="noopener">Barnes–Hut t-SNE</a>、<a href="https://scikit-learn.org/1.6/modules/generated/sklearn.manifold.TSNE.html" target="_blank" rel="noopener">TSNE 參數定義</a>。</p>''')
    extend(bodies,'manifold','w07-detail-manifold-extensions',r'''
<h3>講義連結的圖與套件，各自可以支持哪種結論？</h3>
<p>讀不同 perplexity 的嵌入時，先在原始空間檢查近鄰，再看鄰居是否穩定地放在一起。t-SNE 可讓純雜訊看起來分成小團；局部結構看起來穩定也不等於全域距離、密度或群大小被保留。講義的互動展示與參數實驗用來觀察這些變化，不作分群真值。</p>
<p>FIt-SNE 以插值及 FFT 加速排斥項，Barnes–Hut 用空間樹近似遠方點，openTSNE 則提供擴充的嵌入操作。這些方法改善計算或映射能力，t-SNE 的讀圖限制仍然適用。理論文獻對資料分離、鄰居權重及 early exaggeration 的特定條件證明可視化結果；不是對任意資料都有正確群數保證。</p>
<p>UMAP 的近鄰數決定局部到較廣尺度的取捨，<code>min_dist</code> 影響低維點的緊密程度。用它做分群前處理時，擬合表示與群模型的選擇都需驗證；其嵌入也可能改變密度，不能只挑群最清楚的圖。Lab 的「先 UMAP 再分類」須在訓練資料擬合轉換，再映射測試資料；使用標籤訓練表示則是另一個有監督設定。</p>
<p>張量分解與自監督是講義附錄的後續方向。TensorLy 的 CP／Tucker 表示保留資料的多個軸；遮罩式自監督由輸入產生預測目標，仍有明確的損失與學習程序。這些方法雖然不需要人工標籤，仍有明確的訓練目標，效用要由重建或下游任務判定。</p>
<p>閱讀：<a href="https://distill.pub/2016/misread-tsne/" target="_blank" rel="noopener">t-SNE 圖的常見誤讀</a>、<a href="https://opentsne.readthedocs.io/en/latest/tsne_algorithm.html" target="_blank" rel="noopener">openTSNE 的演算法說明</a>、<a href="https://umap-learn.readthedocs.io/en/latest/clustering.html" target="_blank" rel="noopener">UMAP 用於分群的條件</a>、<a href="https://tensorly.org/stable/user_guide/tensor_decomposition.html" target="_blank" rel="noopener">TensorLy 的分解方式</a>。</p>''')

    extend(bodies,'practical','w07-detail-density',r"""
<h3>Mean shift：找密度峰，bandwidth 決定尺度</h3>
<p>講義附錄的 mean shift 不先指定群數，而是反覆把候選中心移到附近觀測的加權平均。對 bandwidth $h$ 與非負權重核 $g$，更新為 $c^{(t+1)}=\sum_i g(\|x_i-c^{(t)}\|^2/h^2)x_i/\sum_i g(\|x_i-c^{(t)}\|^2/h^2)$；若窗口內沒有點，則不能把零分母拿來更新，需要停止或重新初始化。</p>
<p>固定半徑窗口的直觀就是「看目前窗口中的平均在哪裡，把窗口搬過去再看一次」。多個初始窗口可能收斂到同一密度峰，最後合併相近的峰來形成群。它和 K-means 的差別在於：K-means 先給 $K$ 並最小化全域群內平方和；mean shift 的峰數由資料、核及 bandwidth 共同決定。</p>
<p>小 bandwidth 看見很多局部峰，可能把雜訊也切成小群；大 bandwidth 會平滑掉細節，把原本不同的峰合併。對不同密度資料也未必有一個 bandwidth 同時合適。使用時仍要選 bandwidth 並設定停止條件；省下的是事先指定群數這一步。</p>
<p>API 閱讀：<a href="https://scikit-learn.org/1.6/modules/clustering.html#mean-shift" target="_blank" rel="noopener">MeanShift 與 bandwidth</a>。講義的影像分割例子是以相似顏色／位置形成群，群的意義仍由選用特徵決定。</p>""")
    extend(bodies,'manifold','w07-detail-manifold-extensions',r"""
<h3>從自監督目標接到下游任務</h3>
<p>李宏毅的 BERT 教材以遮住文字再預測為例。未遮住的輸入提供上下文，被遮住的 token 提供目標；模型以交叉熵訓練，因此標籤不是人工另外附上的類別，而是資料自身的一部分。這與只把點畫成低維座標的 t-SNE 目標不同。</p>
<p>先在大量未標記文字預訓練，再以少量標記資料調整分類或問答，是兩個不同的階段。能預測遮罩文字不自動保證癌症分群或所有下游任務都好；要判斷學到的表示是否有用，仍需獨立評估。講義把它列為後續學習方向，這裡保留目標、資料與驗證的關係，不把它混入本章 PCA 或分群的數學假設。</p>
<p>教材：<a href="https://speech.ee.ntu.edu.tw/~hylee/ml/ml2021-course-data/bert_v8.pdf" target="_blank" rel="noopener">李宏毅：Self-Supervised Learning</a>、<a href="https://www.nature.com/articles/s41467-019-13056-x" target="_blank" rel="noopener">t-SNE 的 PCA 初始化與多尺度實務研究</a>。</p>""")
    bodies['hclust']=bodies['hclust'].replace('最常用；對離群值不算敏感','常用；最遠距離仍可能受離群值影響')

    # Traditional Chinese; source code in card payloads stays untouched.
    for sec in bodies:
        for old,new in [('50 个州','50 個州'),('固定中心时','固定中心時'),('阅读：','閱讀：'),('群数','群數'),('64 个細胞株','64 個細胞株'),('指標比較','指標比較'),('是在說明','是在說明'),('空間檢查','空間檢查'),('另一個','另一個')]:
            bodies[sec]=bodies[sec].replace(old,new)
    return bodies
