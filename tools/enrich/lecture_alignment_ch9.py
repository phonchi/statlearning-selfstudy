"""Current Ch9 lecture/Lab expansion; applied after historical scope cleanup."""
from hashlib import sha256
from lib import detail, card, lab_code
from teaching_scope_ch7_8_9_12 import Tree

def extend(bodies, sec, pid, content):
    marker='<!-- lecture-alignment-ch9:'+pid+':'+sha256(content.encode()).hexdigest()[:12]+' -->'
    if marker in bodies[sec]: return
    tree=Tree(bodies[sec])
    node=next(n for n in tree.nodes if n['attrs'].get('id')==pid)
    assert node['end'] is not None
    pos=bodies[sec].rfind('</div>',node['inner'],node['end'])
    assert pos >= node['inner']
    bodies[sec]=bodies[sec][:pos]+marker+content+bodies[sec][pos:]

def add(bodies, sec, pid, title, content):
    if 'id="'+pid+'"' not in bodies[sec]: bodies[sec]+=detail(pid,title,content)

def link(url,title):
    return '<a href="'+url+'" target="_blank" rel="noopener">'+title+'</a>'

def lab(cell,title,stop=None):
    code=lab_code(9,cell)
    if stop: code=code[:code.index(stop)].rstrip()
    return card(title,code,None,src='<code>Ch09-svm-lab-zh.ipynb</code> · 儲存格 '+str(cell))

def augment(bodies):
    add(bodies,'prologue','w10-detail-generative-discriminative','生成式與判別式：SVM 到底學了什麼？',r'''
<p>回想第四章：LDA 先估計每類的特徵分布，再用 Bayes 定理把它轉成類別機率；邏輯斯迴歸直接為給定特徵的類別機率建模。SVM 也屬於判別式方法，但它直接學的是分界與決策分數，沒有先建立完整的機率模型。學分界、估機率與描述每類資料，是三種不同的建模選擇。</p>
$$P(Y=k\mid x)=\frac{\pi_k p(x\mid Y=k)}{\sum_\ell\pi_\ell p(x\mid Y=\ell)},\qquad \hat y_{\rm SVM}=\operatorname{sign}(f(x)).$$
<p>生成式方法的問題是「每類通常會產生怎樣的資料？」判別式方法的問題是「給定這筆資料，類別應該怎麼分？」SVM 進一步把學習問題寫成「保留間隔，同時付出多少違反間隔的成本？」因此不需要假設每一類都是 Gaussian，也不能從沒有 Gaussian 假設推論 SVM 一定更準。</p>
<p>講義附錄以回應／特徵的資料型態整理統計方法，那是選方法的起點。LDA 需要檢查類別條件分布及共變異數假設；邏輯斯迴歸不要求特徵為非 Gaussian，也可以處理 Gaussian 特徵。ANOVA 與迴歸也不是互斥的工具：類別特徵可以透過指示碼進入迴歸。</p>
<p>高維資料即使容易分開，測試資料仍可能分錯。SVM 的正則化與核選擇尤其重要。預測只用支持向量不代表訓練成本低：核矩陣仍可能涉及大量成對計算。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/lda_qda.html" target="_blank" rel="noopener">LDA／QDA 的機率模型</a>、<a href="https://scikit-learn.org/1.6/modules/svm.html" target="_blank" rel="noopener">SVM 的用途與限制</a>。</p>''')
    extend(bodies,'maxmargin','w10-detail-hard-dual',r'''
<h3>為什麼要由 primal 轉到 dual？</h3>
<p>Primal 直接找法向量與截距，因此有 $p+1$ 個主要未知數；dual 改為找每筆資料的權重 $\alpha_i$，有 $n$ 個未知數。當特徵很多而樣本相對少時，dual 提供另一種表達；更關鍵的是，dual 只透過內積接觸特徵，可以在後面直接換成核函數。Dual 的計算速度還受資料稀疏度與求解器影響，不能只由未知數數量判斷。</p>
<p>弱對偶表示任何可行 dual 值都是 primal 最小值的下界。線性可分時，縮放一個分隔面可使所有間隔限制嚴格成立；在這個凸問題下可使用強對偶，最適值相等。KKT 條件用來檢查 primal 與 dual 是否共同達到最適。</p>
<p>實際讀解時依序檢查：$y_if(x_i)\ge1$、$\alpha_i\ge0$、$\sum_i\alpha_i y_i=0$、$w=\sum_i\alpha_i y_ix_i$，最後檢查 $\alpha_i[y_if(x_i)-1]=0$。只有正乘子的點會在最後的 $f(x)$ 留下貢獻。剛好位在間隔上的點未必都有正乘子，退化資料尤其如此。</p>
<p>最大間隔固定法向量的最佳方向；如果最小值或資料幾何有退化，不能把「加入 margin」說成任何情況下所有參數都唯一。不可分時也不能直接強迫硬邊界問題有解。</p>
<p>完整推導：<a href="https://www.csie.ntu.edu.tw/~htlin/mooc/doc/202_handout.pdf" target="_blank" rel="noopener">林軒田：Dual SVM</a>、<a href="https://cs229.stanford.edu/notes2021fall/cs229-notes3.pdf" target="_blank" rel="noopener">Stanford CS229：SVM</a>。</p>''')
    extend(bodies,'soft','w10-detail-soft-dual',r'''
<h3>預算、懲罰與錯分數不是同一個量</h3>
<p>講義的 <code>const</code> 限制總違反量；sklearn 的 <code>C</code> 則把違反量放進目標函數。預算較大表示容許更多違反；懲罰較大表示更不願付出違反量。兩者在正則化路徑上對應，但沒有適用所有資料的固定 $C=1/\mathrm{const}$ 公式。</p>
<p>若 $\epsilon_i>1$，這筆資料在分界的錯誤側，所以每個嚴格錯分點都花掉超過一單位預算。這只給錯分數的上界，不能把總 slack 直接當成錯分筆數；分類正確但進入間隔的點也會消耗預算。$\epsilon_i=1$ 則在分界上，類別取決於 tie 的約定。</p>
<p>在懲罰形式中，$0\lt\alpha_i\lt C$ 的點位在間隔上，可由 $b=y_i-w^Tx_i$ 恢復截距；$\alpha_i=C$ 只表示可能違反間隔，不表示一定錯分。如果所有支持向量都在上界，應以可行截距區間求解，不能除以不存在的自由支持向量數。</p>
<p>連到 Lab：較小 $C$ 的線性模型容許更寬的間隔，可能使用更多支持向量。支持向量多寡描述模型使用了哪些資料點；模型品質仍要以保留資料上的指標比較，不能由支持向量數直接判斷。</p>
<p>閱讀：<a href="https://www.csie.ntu.edu.tw/~htlin/mooc/doc/204_handout.pdf" target="_blank" rel="noopener">Soft-Margin SVM</a>、<a href="https://www.cs.cmu.edu/~epxing/Class/10701-08s/recitation/svm.pdf" target="_blank" rel="noopener">CMU 的 primal／dual 複習</a>。</p>''')
    add(bodies,'soft','w10-detail-tuning-practice','跟著 Lab 選 C：訓練、交叉驗證與測試各做什麼？',r'''
<p>Lab 先用模擬的兩類資料比較不同 $C$，再用五折 CV 搜尋候選值。固定一個候選 $C$ 時，五個模型分別只用四折擬合，拿剩下一折評分，將五個分數平均；接著才在候選參數間比較。搜尋物件的 <code>best_estimator_</code> 是選定參數後在傳入搜尋的完整訓練集重新擬合的模型。</p>
<p><code>mean_test_score</code> 裡的「test」是 CV 的驗證折，不是另留的外部測試集。搜尋後再用 <code>X_test</code> 評估，才能看出已選模型對未參與選擇資料的表現。若反覆看測試集來選 $C$，測試集也變成調參資料。</p>
<p>原 Lab 明確使用打散的 <code>KFold</code>；不能把原程式解說成 <code>StratifiedKFold</code>。實務上類別比例不均衡時，可考慮分層；同一病人多筆資料則還需群組隔離，這與第五章的切分原則一致。</p>'''+lab(31,'原 Lab：五折交叉驗證選擇 C','\ngrid.best_params_')+r'''
<p>線性模型若需標準化，應把縮放和分類器放在同一個 <code>Pipeline</code> 裡，使每折只用自己的訓練部分估計平均與標準差。完整訓練後的測試資料使用相同轉換，不再自行估計一組尺度。原模擬範例的兩個座標使用同一尺度；處理真實資料時仍要先檢查尺度。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/grid_search.html" target="_blank" rel="noopener">超參數搜尋</a>、<a href="resampling_methods.html#w05-detail-nested-cv">一般 CV 與 Nested CV</a>。</p>''')
    extend(bodies,'kernel','w10-detail-kernel-validity',r'''
<h3>次數、維度與核矩陣如何對回講義？</h3>
<p>兩個變數的三次多項式展開有九個非截距項：一階兩個、二階三個、三階四個。$d$ 次核中的 $d$ 是多項式次數，不是特徵空間只有 $d$ 維。含常數的 $(1+x^Tu)^d$ 與齊次的 $(x^Tu)^d$ 也不是同一個核：前者包含低階項。</p>
<p>講義的二次映射與 Lab 的 <code>my_kernel_1</code> 都是齊次二次核。sklearn 內建多項式核為 $(\gamma x^Tu+\mathrm{coef0})^d$；若沒有核對 <code>gamma</code> 與 <code>coef0</code>，不能直接聲稱它與自訂核完全相同。</p>
<p>核函數傳入兩個資料矩陣 $X$ 與 $Y$，回傳的矩陣形狀必須是「X 的樣本數 × Y 的樣本數」。訓練時計算 train–train，預測時計算 test–train；不能對測試資料改算成 test–test。核技巧省掉顯式的高維特徵，但沒有消除樣本數平方級矩陣可能帶來的負擔。</p>
<p>RBF 的指數可展開成各階內積，因此有無限多個可能的特徵座標；「無限維」並不等於必須在電腦儲存無限座標，也不等於能任意插值且保證泛化。$\gamma$ 改變相似度的衰減速度，$C$ 改變違反間隔的代價，兩者都要選。</p>
<p>閱讀：<a href="https://xavierbourretsicotte.github.io/Kernel_feature_map.html" target="_blank" rel="noopener">作者的核映射推導</a>、<a href="https://scikit-learn.org/1.6/modules/svm.html#kernel-functions" target="_blank" rel="noopener">sklearn 核函數介面</a>。</p>''')
    extend(bodies,'kernel','w10-detail-score-roc',r'''
<h3>ROC、機率與分類標籤要分開讀</h3>
<p>Lab 用 <code>RocCurveDisplay.from_estimator</code>，從模型的決策分數掃過門檻，不需要先把分數變成機率。二元分類時，先核對 <code>classes_</code> 的順序，因為正分數指向後一個類別。AUC 描述正負例的排序，與固定零門檻下的準確率不同。</p>
<p>原 Lab 比較 $\gamma=50$ 的彈性模型與 CV 選出的模型，先畫訓練 ROC 再畫測試 ROC。訓練曲線較漂亮只說明更貼近已見資料；如果測試曲線變差，就不能用訓練 AUC 宣稱改善。最後一張圖是在訓練資料調參後，分別對訓練／測試資料評分，沒有在測試資料上再次執行 GridSearchCV。</p>
<p><code>SVC(probability=True)</code> 另外以訓練資料的交叉驗證分數作 Platt scaling，二元形式可寫成 $P(Y=1\mid f)=1/(1+\exp(Af+B))$，其中 $A,B$ 另外估計。這個額外步驟提供校準機率，原本的 hinge loss 訓練目標維持不變。<code>predict()</code> 與 <code>predict_proba()</code> 的最大機率類別也可能不同；需要決策成本時，應在訓練／驗證資料上評估校準與門檻。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/svm.html#scores-and-probabilities" target="_blank" rel="noopener">分數與機率</a>、<a href="https://scikit-learn.org/1.6/modules/calibration.html" target="_blank" rel="noopener">機率校準</a>。</p>''')
    extend(bodies,'hinge','w10-detail-loss-normalization',r'''
<h3>為什麼 hinge 的轉折在 1？</h3>
<p>分類只看 $\operatorname{sign}(f)$，同時放大 $w,b$ 不改變分界。但如果沒有固定尺度，$y_if$ 不能直接拿來比較間隔。將間隔邊界定為 $y_if=1$ 是可識別的標準化約定，不是資料中有一個天然機率 1。幾何間隔仍是 $1/\|w\|$。</p>
<p>兩種標籤編碼也要先統一：$y\in\{-1,1\}$ 時用 $\log(1+e^{-yf})$；$z\in\{0,1\}$ 時用 $-z\log\sigma(f)-(1-z)\log[1-\sigma(f)]$，兩式在 $y=2z-1$ 後完全一致。損失相同不代表 hinge 與 logistic 會擬合同樣係數；hinge 在正確側間隔外為零，logistic 只會逐漸接近零。</p>
<p>將 $\tfrac12\|w\|^2+C\sum_i\ell_i$ 除以 $C$，得到 $\sum_i\ell_i+\tfrac1{2C}\|w\|^2$；若再改成平均損失，懲罰係數還要除以 $n$。因此比較 SGD 的 <code>alpha</code> 與 SVC 的 <code>C</code> 時，必須看清楚套件的目標函數，不能只比數字大小。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/sgd.html#mathematical-formulation" target="_blank" rel="noopener">SGD 的損失與正則化</a>。</p>''')
    extend(bodies,'vslogit','w10-detail-solvers',r'''
<h3>核近似為什麼可以接上 SGD？</h3>
<p>原 Lab 以 <code>RBFSampler</code> 產生有限個隨機 Fourier 特徵，再以線性的 <code>SGDClassifier(loss="hinge")</code> 擬合。此時真正儲存的是有限長度的特徵與線性係數，並不需要保留完整的訓練核矩陣。近似特徵數增加可改善核近似，但同時增加時間與記憶體；近似好壞仍不是測試誤差的保證。</p>
<p>SGD 每次用一筆或小批資料估計更新方向。hinge 在 $yf\lt1$ 時，對 $w$ 的次梯度包含 $-yx$；在 $yf>1$ 時，這筆資料的 hinge 梯度為零，但正則化仍可縮小係數。特徵尺度、步長與迭代次數都影響是否充分收斂。這是在近似後的特徵空間解線性問題，得到的是近似核模型，與精確的 RBF SVC 有別。</p>
<p>線性 SVC、LinearSVC 與 SGDClassifier 的預設損失、截距處理及求解策略不同。比較時先對齊目標再比較泛化；不能以「三個都畫直線」推成三者必定得到一樣答案。</p>
<p>閱讀：<a href="https://scikit-learn.org/1.6/modules/kernel_approximation.html" target="_blank" rel="noopener">核近似</a>、<a href="https://scikit-learn.org/1.6/modules/sgd.html" target="_blank" rel="noopener">SGDClassifier</a>。</p>''')

    add(bodies,'multiclass','w10-detail-khan-lab','Khan 基因表現資料：高維可以完全分隔，測試仍會出錯',r"""
<p>Khan 資料用基因表現預測四種腫瘤類型。每個樣本有 2,308 個基因測量值，訓練集有 63 筆、測試集有 20 筆；特徵數遠大於樣本數，所以即使用線性邊界，也可能把訓練資料完全分開。零訓練誤差在這個情況下並不難達成。</p>
<p>Lab 先以線性核及 <code>C=10</code> 擬合，再分別製作訓練與測試混淆表。它在訓練資料沒有錯分，测试資料卻有兩筆錯分；這正好說明「能找到分隔面」與「能預測未見樣本」是兩個問題。測試混淆表還能看出哪些類型容易互相混淆，資訊比單一正確率更完整。</p>"""+lab(90,'原 Lab：Khan 的線性分類器')+lab(92,'原 Lab：保留測試樣本的混淆表')+r"""
<p>線性核可作為高維資料的起點，避免先加入不必要的非線性；是否需要更靈活的核仍要由訓練資料中的驗證決定。真實基因資料還需檢查尺度、批次效應與可能的病人重複量測，不能只因 $p\gg n$ 就跳過正則化或資料切分的檢查。</p>
<p>多類別 <code>SVC</code> 的底層仍以 OVO 訓練；<code>decision_function_shape="ovr"</code> 只調整輸出形狀。原 Lab 的文字把兩種輸出形狀說成兩種訓練策略，讀程式時應依估計器的实际行為區分。</p>
<p>資料：<a href="https://islp.readthedocs.io/en/latest/datasets/Khan.html" target="_blank" rel="noopener">Khan 資料的訓練／測試欄位</a>、<a href="https://scikit-learn.org/1.6/modules/svm.html#multi-class-classification" target="_blank" rel="noopener">SVC 的多類別訓練與輸出</a>。</p>""")
    bodies['multiclass']=bodies['multiclass'].replace('問題小、類別平衡、通常分得開。','問題較小；兩類是否平衡與能否分開，仍取決於資料。').replace('好（兩類各自的量）','依兩類各自樣本數決定')
    bodies['multiclass']=bodies['multiclass'].replace('测试資料','測試資料').replace('实际行為','實際行為')

    # Correct the lecturer's appendix sign without changing source PDFs.
    extend(bodies,'maxmargin','w10-detail-perceptron',r'''
<h3>更新方向怎麼判斷？</h3>
<p>標籤採 $\{-1,1\}$ 且分類錯誤時，感知器的更新 $w\leftarrow w+\eta y_ix_i$、$b\leftarrow b+\eta y_i$ 會提高這筆資料的 signed score。若用 0／1 輸出 $o_i$ 與目標 $y_i$ 表示，修正方向是「目標減輸出」。使用「輸出減目標」卻仍加到權重上會往錯誤方向走；不同記號必須連同更新的正負號一起核對。</p>
<p>感知器找到任一分隔面便可能停止；SVM 在可行分隔面間再比較間隔。非線性可分資料上，基本感知器不保證有限步收斂，軟邊界 SVM 則明確用損失接受部分違反。閱讀：<a href="https://scikit-learn.org/1.6/modules/linear_model.html#perceptron" target="_blank" rel="noopener">Perceptron 的學習規則</a>。</p>''')
    return bodies
