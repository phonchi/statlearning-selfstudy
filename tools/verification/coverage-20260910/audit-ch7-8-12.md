# Ch7、Ch8、Ch12 講義與直接連結覆蓋核對

本次從 PDF 全文與圖像頁核對；以下「確認無誤」只指列出的內容，不代表外部整本書或所有程式碼均已逐字驗證。新增推導均為預設收合的 `details.qa-item.proof`；正文保留條件、結果、演算法與自訂算例。

## 逐章逐段

|章|PDF頁|網站節|核對與處理|
|---|---|---|---|
|7|1–3|prologue|封面、課綱及方法定位；不要求另造模型內容|
|7|4–7|poly|概念/多項式/CI；補 logit 區間與收合變異推導|
|7|8–9|step|確認無誤：切段與編碼；補交互作用算例|
|7|10–17|splines|確認無誤：基底與連續性元件；補一般次數、一次算例與維度證明|
|7|18–23|natural|確認無誤：自然邊界/節點CV；補基底與B-spline遞迴|
|7|24–27|smooth|確認無誤：損失與LOOCV式；補平滑矩陣/譜縮減/唯一性條件/證明|
|7|28–33|loess|確認無誤：局部演算法/跨距；補WLS算例、二維/變係數|
|7|34–44|gam|確認無誤：加法/分類/分離；補中心化IRLS與backfitting條件|
|7|45–46|natural|附錄分隔及自然基底；完整式和證明補齊|
|7|47–48|smooth|補正常方程、IRLS、計算維度修正|
|7|49–50|gam|補薄板完整表示、限制、區塊系統與算例|
|7|51–51|natural|補B-spline相關外鏈算法|
|7|52–54|gam|補四種效果圖、FWL/正交證明與PDP算例|
|8|1–14|grow|確認無誤：樹/切分/葉值；補類別子集與排序算例|
|8|15–21|prune|確認無誤：目標/CV/圖；補weakest-link值與證明|
|8|22–26|classtree|確認無誤：分類impurity與加權分裂|
|8|27–29|vslinear|確認無誤：樹與線性模型/優缺點|
|8|30–31|why|確認無誤：投票與獨立條件|
|8|32–37|bagging|確認無誤：bootstrap/OOB；相關公式的抽樣條件保留|
|8|38–42|rf|確認無誤：每節點抽特徵；補變異推導|
|8|43–51|boosting|補一般負梯度/葉更新/分類/Huber與AdaBoost尺度|
|8|52–61|modern|補XGBoost二階目標/葉值/gain與算例、GOSS/EFB/MVS/ordered/DART|
|8|62–63|reference|結論與附錄分隔；不增加聲稱|
|8|64–65|grow|补ID3/C4.5/C5.0/CART範圍|
|8|66–66|stacking|確認無誤：折外stacking流程|
|8|67–67|rf|補Extra-trees與抽樣層次|
|8|68–69|boosting|確認圖像演算法；補多類別/絕對/Huber負梯度|
|8|70–73|modern|確認編碼；補順序統計例子與評估條件|
|8|74–79|stacking|補BART觀測模型/先驗/後驗循環/葉更新與證明|
|8|80–80|reference|參考書/套件入口；不承諾全部外站內容|
|12|1–7|prologue|確認無誤：目標/評估；補密度/異常偵測|
|12|8–16|pca|確認無誤：得分負荷/biplot；補秩、重根與完整特徵證明|
|12|17–22|lowrank|補SVD最佳近似/因子不唯一/選維度目的與限制|
|12|23–28|scaling|補共變異數/白化與零特徵值條件|
|12|29–38|completion|確認無誤：補值演算法與推薦用途；補單調性證明與算例|
|12|39–53|manifold|補完整SNE/t-SNE分布、全域Z、梯度/更新/證明與算例|
|12|54–60|practical|確認無誤：分群目的；補metric learning/比較圖其他方法/fuzzy|
|12|61–68|kmeans|確認無誤：更新元件/初值；補恆等式證明與ties/空群|
|12|69–80|hclust|確認無誤：樹狀圖/linkage；補Ward證明/算例、divisive/MST|
|12|81–91|practical|補DBSCAN/HDBSCAN具體步驟/核心距離；核對度量/群驗證|
|12|92–94|practical|補k-prototypes/FAMD/Gower/PAM/CH與用途限制|
|12|95–97|manifold|附錄方向；補張量/自監督最小式，非完整深度模型課程|
|12|98–99|scaling|補白化證明；perplexity在manifold完整式/例子|
|12|100–106|practical|補Mean shift/GMM/變分/譜分群與下游用途條件|

## 來源檔可查位置

### Ch7: tools/enrich/enrich_nonlin.py
- 第 948 行：自然樣條與 B-spline 基底
- 第 951 行：平滑矩陣與邏輯斯平滑
- 第 954 行：二維平滑與效果圖的讀法
- 第 960 行：從 logit 的信賴區間回到機率
- 第 964 行：""" + proof('w08proof-logit','線性預測量的變異與區間轉換',r"""<p>固定基底向量 $b_0$ 
- 第 965 行：用切段建立可解讀的交互作用
- 第 966 行：一次樣條與一般次數
- 第 968 行：實際計算 B-spline 基底
- 第 971 行："""+proof('w08proof-natural','自然基底為何在邊界外線性',r"""<p>令 $d_k(x)=\{(x
- 第 973 行：由曲率懲罰到可計算的線性系統
- 第 980 行："""+proof('w08proof-smooth','正常方程、平滑矩陣與自由度',r"""<p>對係數微分得 $-2B^T(
- 第 982 行：二元反應的懲罰 IRLS
- 第 985 行："""+proof('w08proof-irls','懲罰 logistic 的 Newton 更新',r"""<p>負對數概似 
- 第 986 行：局部加權擬合的一次計算
- 第 988 行：讓加法成分可識別的 backfitting
- 第 989 行："""+proof('w08proof-backfit','backfitting 為何是分塊最小化',r"""<p>固定其他成分
- 第 991 行：薄板樣條的完整表示
- 第 995 行：用一個小例子區分四種效果圖
- 第 996 行："""+proof('w08proof-fwl','部分迴歸斜率與 OLS 殘差正交性',r"""<p>把完整線性設計分成 $[Z
### Ch8: tools/enrich/enrich_trees.py
- 第 1193 行：類別特徵如何編碼
- 第 1199 行：連續切點與類別分割如何搜尋
- 第 1200 行：樹的分裂規則與演算法家族
- 第 1201 行："""+proof('w09proof-leaf','葉平均與類別排序捷徑的理由',r"""<p>固定一個葉子的資料集合 $R$，
- 第 1203 行：weakest-link 的臨界值
- 第 1206 行："""+proof('w09proof-prune','剪枝臨界值',r"""<p>保留子樹與收成一葉的成本差為 $R(T_t)+
- 第 1208 行：Extra-trees、random subspaces 與 random patches
- 第 1209 行："""+proof('w09proof-forest-var','平均樹的變異與相關性',r"""<p>固定預測位置 $x$，若各
- 第 1211 行：從擬合殘差到一般負梯度
- 第 1214 行：AdaBoost 的權重尺度
- 第 1215 行："""+proof('w09proof-adaboost','AdaBoost 的半個對數勝算從哪裡來',r"""<p>固定本輪弱
- 第 1217 行：XGBoost：本輪的目標、葉值與分裂增益
- 第 1222 行："""+proof('w09proof-xgboost','二階展開、最佳葉值與 split gain',r"""<p>逐點 Ta
- 第 1224 行：大型資料如何減少搜尋量
- 第 1225 行：CatBoost 的順序與取樣
- 第 1228 行：DART：暫時拿掉部分既有樹
- 第 1231 行：BART 每一輪究竟更新什麼
- 第 1232 行："""+proof('w09proof-bart-leaf','Gaussian 葉值的條件後驗',r"""<p>固定樹結構與其他
- 第 1235 行：同一提升流程下的不同損失
### Ch12: tools/enrich/enrich_unsup.py
- 第 1133 行：從共變異數到白化
- 第 1138 行：Ward 與階層假設
- 第 1141 行：密度分群：DBSCAN、OPTICS 與 HDBSCAN
- 第 1142 行：Mean shift、混合模型與譜分群
- 第 1143 行：混合型資料與分群後的用途
- 第 1146 行：t-SNE 的目標與調整參數
- 第 1147 行：講義延伸方向
- 第 1153 行：主成分的完整條件與可重算例子
- 第 1154 行："""+proof('w07proof-pca','最大變異、特徵向量、正交與秩上限',r"""<p>限制單位長度的 Lagran
- 第 1156 行：最佳低秩近似的解與不唯一性
- 第 1157 行："""+proof('w07proof-lowrank','投影誤差、截斷 SVD 與 PVE',r"""<p>對任意正交的 $V
- 第 1159 行：白化算例與零特徵值
- 第 1160 行："""+proof('w07proof-whitening','白化的共變異數',r"""<p>$\operatorname{Co
- 第 1162 行：矩陣補全要驗證什麼
- 第 1163 行："""+proof('w07proof-completion','固定觀測格的交替補值為何使目標不增',r"""<p>令 $L^{
- 第 1165 行：一輪 K-means 與停止條件
- 第 1166 行："""+proof('w07proof-kmeans','群內兩兩距離、群心與單調性',r"""<p>對非空群 $C$，設 $m=
- 第 1168 行：合併距離的一次手算
- 第 1169 行："""+proof('w07proof-ward','Ward 的平方和增加量',r"""<p>令 $a=|A|,b=|B|$，合
- 第 1171 行：從密度鄰域到 HDBSCAN 的階層
- 第 1174 行：Mean shift 的更新式
- 第 1177 行：高斯混合模型與 EM 的完整更新
- 第 1181 行："""+proof('w07proof-gmm','EM 的更新與概似不下降',r"""<p>引入隱藏成分標籤 $z_i$。固定目
- 第 1183 行：變分貝氏混合
- 第 1184 行：譜分群：從圖走到可分群的座標
- 第 1185 行："""+proof('w07proof-laplacian','Laplacian 為何找平滑的群指示方向',r"""<p>對稱 
- 第 1187 行：混合型資料的距離與可驗證的群
- 第 1192 行：SNE、crowding 與 t-SNE 的完整機率
- 第 1199 行：perplexity 與逐輪最佳化
- 第 1200 行："""+proof('w07proof-tsne','t-SNE 梯度與吸引／排斥項',r"""<p>固定 $P$，利用 $q_{
- 第 1202 行：其他流形方法各自保留什麼
- 第 1203 行：張量與自監督延伸的最小數學框架
- 第 1207 行：模糊分群與距離學習
- 第 1208 行：用什麼目的選 PCA 的維度
- 第 1209 行：能否映射新資料，以及理論保證的範圍
- 第 1211 行：降維、分群以外的兩個目標
- 第 1214 行：分裂式與最小生成樹的具體步驟
- 第 1215 行：混合資料的其他比較基準

## 圖像頁

40 個低文字图像頁均已實際檢視：`ch7-8-12-images/montage-00.png` 至 `montage-09.png`。包含封面/分隔頁、Ch7 spline圖、Ch8演算法8.1/8.2及ESL10.3/BART、Ch12演算法12.1/12.2/12.3及群比較。Ch12 p.48 本地PDF呈现幾乎空白（僅小型數字與展示連結），沒有憑空還原互動。

## 直接 URL 處理台帳

來源以 PDF URI annotation 為準：Ch7 19次/18相異，Ch8 56次/51相異，Ch12 57次/55相異。`sources.json` 正則文字抽取亦可能包含換行截斷網址，本表不把截斷碎片當成新增外鏈。

完整逐次列表：`links-ch7-8-12.json`。primary_topic_read=已讀相關第一手段落；read_topic=已讀指定教學問題且以第一手資料/独立推導再核對；abstract_read=僅摘要；blocked_replaced=已尝試但原內容受阻，明列替代；context_or_data=資料/背景/整站入口，未宣稱逐頁通讀。

|章/頁|直接網址|狀態與限制|
|---|---|---|
|7/2|https://arxiv.org/pdf/2207.08815.pdf|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|7/2|https://arxiv.org/abs/2308.16898|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|7/5|https://islp.readthedocs.io/en/latest/datasets/Wage.html|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|7/6|https://stats.stackexchange.com/questions/136157/general-mathematics-for-confidence-interval-in-multiple-linear-regression|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/7|https://stats.stackexchange.com/questions/483362/pointwise-standard-errors-for-a-logistic-regression-fit-with-statsmodels|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/18|https://stats.stackexchange.com/questions/233232/the-definition-of-natural-cubic-splines-for-regression|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/19|https://patsy.readthedocs.io/en/latest/spline-regression.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|7/23|https://stats.stackexchange.com/questions/490306/natural-splines-degrees-of-freedom?rq=1|blocked_replaced：web 抓取失敗；自然樣條條件改用 UTC 與 ESL 核對|
|7/36|https://stats.stackexchange.com/questions/279576/partial-residuals-plot|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/47|https://github.com/empathy87/The-Elements-of-Statistical-Learning-Python-Notebooks/blob/master/examples/Bone Mineral Density.ipynb|blocked_replaced：GitHub notebook 頁回載入錯誤，未讀 notebook 本文；相同平滑矩陣依 ESL 與 UTC 計算|
|7/51|https://www.hds.utc.fr/~tdenoeux/dokuwiki/_media/en/splines.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|7/51|https://math.stackexchange.com/questions/699113/what-is-the-relationship-between-cubic-b-splines-and-cubic-splines|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/52|https://en.wikipedia.org/wiki/Partial_regression_plot|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/52|https://en.wikipedia.org/wiki/Partial_residual_plot|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/52|https://stats.stackexchange.com/questions/423375/why-is-there-residual-dots-in-plot-of-gam|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/52|https://stats.stackexchange.com/questions/189584/why-do-residuals-in-linear-regression-always-sum-to-zero-when-an-intercept-is-in|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/52|https://stats.stackexchange.com/questions/474102/why-is-the-correlation-between-independent-variables-regressor-and-residuals-zer|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|7/53|https://christophm.github.io/interpretable-ml-book/pdp.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/4|https://islp.readthedocs.io/en/latest/datasets/Hitters.html|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|8/13|https://dafriedman97.github.io/mlbook/content/c5/s1/regression_tree.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/13|https://stackoverflow.com/questions/45513511/decision-trees-choosing-thresholds-to-split-objects|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/13|https://dafriedman97.github.io/mlbook/content/c5/s1/classification_tree.html#making-splits|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/17|https://stats.stackexchange.com/questions/193538/how-to-choose-alpha-in-cost-complexity-pruning|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/22|https://dafriedman97.github.io/mlbook/content/c5/s1/classification_tree.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/26|https://github.com/JWarmenhoven/ISLR-python/blob/master/Notebooks/Data/Heart.csv|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|8/27|https://dafriedman97.github.io/mlbook/content/c5/s1/regression_tree.html#making-splits|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/29|https://catboost.ai/en/docs/concepts/algorithm-main-stages_cat-to-numberic|blocked_replaced：舊路徑抓取失敗；使用 catboost.ai/docs/en 新路徑與 CatBoost 原論文|
|8/31|https://math.stackexchange.com/questions/4363939/how-did-you-get-75-and-97-with-which-formula|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/32|https://dafriedman97.github.io/mlbook/content/c6/s1/bagging.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/32|https://online.stat.psu.edu/stat414/lesson/24/24.4|blocked_replaced：web 抓取失敗；平均變異已獨立推導|
|8/34|https://ieeexplore.ieee.org/document/709601|blocked_replaced：IEEE 僅回機器驗證；random subspaces 用講義與 sklearn 官方文件|
|8/34|https://link.springer.com/chapter/10.1007/978-3-642-33460-3_28|abstract_read：已讀原始摘要，全文需訂閱；只採摘要可支持的方法動機，不聲稱核讀付費全文或移植全部證明|
|8/37|https://yuhangzhou88.github.io/ESL_Solution/|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|8/38|https://dafriedman97.github.io/mlbook/content/c6/s1/random_forests.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/39|https://scikit-learn.org/stable/modules/ensemble.html#extremely-randomized-trees|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/44|https://dafriedman97.github.io/mlbook/content/c6/s1/boosting.html#boosting|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/45|https://www.youtube.com/watch?v=3CC4N4z3GJc&t=0s|blocked_replaced：影片頁抓取失敗，未取得字幕；相應提升/XGBoost 演算法以官方文章/原論文替代|
|8/45|https://dafriedman97.github.io/mlbook/content/c6/s1/boosting.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/45|https://sefiks.com/2018/10/04/a-step-by-step-gradient-boosting-decision-tree-example/|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/48|https://xgboost.readthedocs.io/en/latest/|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/52|https://arxiv.org/pdf/1603.02754.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/52|https://stats.stackexchange.com/questions/353462/what-are-the-implications-of-scaling-the-features-to-xgboost|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/52|https://towardsdatascience.com/catboost-vs-light-gbm-vs-xgboost-5f93620723db|blocked_replaced：web 抓取失敗；套件比較改用三者官方來源|
|8/53|https://xgboost.readthedocs.io/en/latest/tutorials/model.html#tree-boosting|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/53|https://www.youtube.com/watch?v=ZVFeW798-2I|blocked_replaced：影片頁抓取失敗，未取得字幕；相應提升/XGBoost 演算法以官方文章/原論文替代|
|8/53|https://stats.stackexchange.com/questions/202858/xgboost-loss-function-approximation-with-taylor-expansion|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/53|https://xgboost.readthedocs.io/en/stable/tutorials/categorical.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/53|https://xgboost.readthedocs.io/en/stable/faq.html#how-to-deal-with-missing-values|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/54|https://www.youtube.com/watch?v=oRrKeUCEbq8|blocked_replaced：影片頁抓取失敗，未取得字幕；相應提升/XGBoost 演算法以官方文章/原論文替代|
|8/54|https://datasketches.apache.org/docs/Quantiles/QuantilesOverview.html|blocked_replaced：web 抓取失敗；weighted quantile sketch 用 XGBoost 原論文|
|8/55|https://gist.github.com/jboner/2841832|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|8/56|https://lightgbm.readthedocs.io/en/latest/Features.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/56|https://hackmd.io/@WangJengYun/HyLtemyxI|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/57|https://datascience.stackexchange.com/questions/26699/decision-trees-leaf-wise-best-first-and-level-wise-tree-traverse|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/57|https://www.tandfonline.com/doi/abs/10.1080/01621459.1958.10501479|blocked_replaced：web 抓取失敗；分類平均排序捷徑由原始目標獨立推導並對照 LightGBM 官方|
|8/57|https://medium.com/riskified-technology/xgboost-lightgbm-or-catboost-which-boosting-algorithm-should-i-use-e7fda7bb36bc|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/58|https://proceedings.neurips.cc/paper/2018/file/14491b756b3a51daac41c24863285549-Paper.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/59|https://catboost.ai/en/docs/concepts/algorithm-main-stages_bootstrap-options#mvs|blocked_replaced：舊路徑抓取失敗；使用 catboost.ai/docs/en 新路徑與 CatBoost 原論文|
|8/59|https://neptune.ai/blog/when-to-choose-catboost-over-xgboost-or-lightgbm|blocked_replaced：舊比較文章已重導至無關 OpenAI 收購消息，不作教材依據|
|8/59|https://github.com/catboost/tutorials/blob/master/categorical_features/categorical_features_parameters.ipynb|blocked_replaced：GitHub notebook 頁未提供完整可讀 cell；類別機制改讀 CatBoost 原論文與官方|
|8/60|https://xgboost.readthedocs.io/en/stable/tutorials/dart.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/62|https://arxiv.org/pdf/2207.08815.pdf|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|8/64|https://scikit-learn.org/stable/modules/tree.html#tree-algorithms-id3-c4-5-c5-0-and-cart|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/64|https://en.wikipedia.org/wiki/ID3_algorithm|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/65|https://en.wikipedia.org/wiki/Predictive_analytics#Classification_and_regression_trees_.28CART.29|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/73|https://axk51013.medium.com/kaggle-categorical-encoding-3%E5%A4%A7%E7%B5%95%E6%8B%9B-589780119470|blocked_replaced：只回 21 行空殼，非文章正文；HDBSCAN/target encoding 已改用官方來源|
|8/73|https://medium.com/@pouryaayria/k-fold-target-encoding-dfe9a594874b|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|8/75|http://hedibert.org/wp-content/uploads/2018/06/BART.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|8/80|https://github.com/serengil/chefboost|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|12/9|https://towardsdatascience.com/visualising-high-dimensional-datasets-using-pca-and-t-sne-in-python-8ef87e7915b|blocked_replaced：web 抓取失敗；PCA/t-SNE 使用原論文與官方文檔|
|12/12|https://stats.stackexchange.com/questions/153928/why-are-principal-component-scores-uncorrelated|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/12|https://stats.stackexchange.com/questions/123318/why-are-there-only-n-1-principal-components-for-n-data-if-the-number-of-dime|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/14|https://islp.readthedocs.io/en/latest/datasets/USArrests.html|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|12/20|https://stats.stackexchange.com/questions/32174/pca-objective-function-what-is-the-connection-between-maximizing-variance-and-m|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/22|https://stats.stackexchange.com/questions/93845/how-to-perform-cross-validation-for-pca-to-determine-the-number-of-principal-com|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/22|https://link.springer.com/article/10.1007/s00362-021-01276-7|abstract_read：已讀原始摘要，全文需訂閱；只採摘要可支持的方法動機，不聲稱核讀付費全文或移植全部證明|
|12/25|https://stats.stackexchange.com/questions/134282/relationship-between-svd-and-pca-how-to-use-svd-to-perform-pca|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/26|https://www.math.uwaterloo.ca/~hwolkowi/matrixcookbook.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/27|https://rich-d-wilkinson.github.io/MATH3030/4.2-pca-a-formal-description-with-proofs.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/28|https://github.com/fastai/numerical-linear-algebra|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|12/34|https://en.wikipedia.org/wiki/Matrix_completion|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/40|https://www.twblogs.net/a/5bcb6b332b7177796822b307|blocked_replaced：舊網址抓取失敗；流形方法改讀 sklearn 官方|
|12/41|https://jlmelville.github.io/smallvis|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/46|https://epubs.siam.org/doi/pdf/10.1137/18M1216134|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/48|https://dash.gallery/dash-tsne/|blocked_replaced：只回 iframe，沒有可讀算法或可驗證展示；不宣稱已操作，本站沿用既有 t-SNE 元件|
|12/50|https://github.com/omiq-ai/Multicore-opt-SNE|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/50|https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf|blocked_replaced：web 回 Content length too large (14031289)；Barnes–Hut 機制改讀 openTSNE 官方|
|12/51|https://distill.pub/2016/misread-tsne/|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/52|https://www.nature.com/articles/s41467-019-13056-x|blocked_replaced：web 抓取失敗；初始化與全域解讀限界改讀 openTSNE、Distill|
|12/53|https://opentsne.readthedocs.io/en/latest/tsne_algorithm.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|https://github.com/KlugerLab/FIt-SNE|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|https://umap-learn.readthedocs.io/en/latest/|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|https://lvdmaaten.github.io/publications/papers/AISTATS_2009.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|http://proceedings.mlr.press/v75/arora18a/arora18a.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|https://umap-learn.readthedocs.io/en/latest/clustering.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/53|https://jlmelville.github.io/smallvis/|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/54|https://en.wikipedia.org/wiki/Cluster_analysis|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/55|http://contrib.scikit-learn.org/metric-learn/introduction.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/57|https://scikit-learn.org/stable/modules/clustering.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/60|https://en.wikipedia.org/wiki/Fuzzy_clustering|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/64|https://stats.stackexchange.com/questions/489459/in-cluster-analysis-how-does-gaussian-mixture-model-differ-from-k-means-when-we|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/65|https://www.naftaliharris.com/blog/visualizing-k-means-clustering/|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/69|https://chih-ling-hsu.github.io/2017/09/01/Divisive-Clustering|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/69|https://scikit-learn.org/stable/modules/generated/sklearn.cluster.FeatureAgglomeration.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/78|https://jbhender.github.io/Stats506/F18/GP/Group10.html|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/81|https://en.wikipedia.org/wiki/DBSCAN|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/82|https://www.naftaliharris.com/blog/visualizing-dbscan-clustering/|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/83|https://en.wikipedia.org/wiki/Spectral_clustering|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/84|https://axk51013.medium.com/2021%E5%B9%B4%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8%E5%AE%B6%E5%BF%85%E5%82%99%E5%88%86%E7%BE%A4%E6%B3%95hdbscan%E7%B0%A1%E4%BB%8B-fba8287e666c|blocked_replaced：只回 21 行空殼，非文章正文；HDBSCAN/target encoding 已改用官方來源|
|12/86|https://scikit-learn.org/stable/modules/metrics.html#metrics|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/89|https://stats.stackexchange.com/questions/723/how-can-i-test-whether-my-clustering-of-binary-data-is-significant|read_topic：已開啟核讀講義指定問題的相關文字；數學公式另以正文的官方來源與獨立推導確認，不採論壇作唯一依據|
|12/92|https://github.com/nicodv/kmodes|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/92|https://www.nature.com/articles/s41598-021-83340-8|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/92|https://github.com/MaxHalford/prince#factor-analysis-of-mixed-data-famd|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/94|https://phonchi.github.io/nsysu-math608/materials/|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|12/96|http://tensorly.org/stable/index.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/96|https://scikit-learn.org/stable/modules/manifold.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/96|https://jlmelville.github.io/smallvis/spectral.html|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/96|https://cs229.stanford.edu/syllabus.html|context_or_data：資料集、課綱/延伸課程、程式庫或整份解答入口；界定用途，不宣稱全部站頁或實驗已核讀/重跑|
|12/96|https://cs229.stanford.edu/notes2021fall/cs229-notes7b.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/96|https://scikit-learn.org/stable/modules/mixture.html#variational-bayesian-gaussian-mixture|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/97|https://speech.ee.ntu.edu.tw/~hylee/ml/ml2021-course-data/bert_v8.pdf|primary_topic_read：已讀相關官方/作者段落，用於本站相應主題；整站入口只讀本章需要的機制，不搬入全站|
|12/103|https://medium.com/temp08050309-devpblog/cv-7-segmentation-as-clustering-k-means-mixture-of-gaussians-mean-shift-fe94d39bd2fc|blocked_replaced：web 抓取失敗；Mean shift/GMM 按講義與 sklearn/Stanford 原始教材|
|12/103|https://towardsdatascience.com/the-5-clustering-algorithms-data-scientists-need-to-know-a36d136ef68|blocked_replaced：web 抓取失敗；各方法依講義及 sklearn 官方|

## 驗證

- `check-ch7-8-12.py` 與 `numeric-ch7-8-12.log`：14 項獨立數值檢查通過，涵蓋刪點重擬合LOOCV、XGBoost、PCA、BART、GMM及t-SNE有限差分梯度。
- 三頁 browser_check 第一輪均 0 問題；後續卡片/條件文字修訂重建後由最終檢查覆核。
- 譜分群已修正獨立審查的反例：無孤立點仍可能在所選特徵向量中出現零列，列正規化須先處理連通分量。
- 未重跑任何課程Lab；保留既有FRAMES及原始儲存輸出。SIZE僅為建議警告，無內容刪減。
- 沒有完整核讀受阻文章、付費全文、整套YouTube影片，不能把台帳的替代閱讀寫成原頁已核讀。


## 最終本組驗收結果

- 最終 `browser-ch7-8-12.log`：三頁均 OK，0 個問題，包含全部展開證明後 MathJax、鍵盤收合、各元件、手機版及離線 fallback。
- 已實際檢視三個長證明局部截圖 `w08proof-smooth.png`、`w09proof-xgboost.png`、`w07proof-tsne.png`，公式與文字完整可讀。
- `check_lab_rendered.py --help` 工具沒有 help 模式而實際執行全站唯讀檢查：245 張完整 Lab 卡，failures=0；本組每一張 code/output 均 True。未重新執行 Lab。
- 本組初輪 validator 三頁0失敗，Ch7/12為SIZE警告。最後共享 studyguide 模板已由主代理更新，尚待主代理統一 build 再驗 GEN-REGION，不由本組重寫共享樣板。
- 最後 HTML/證明數快照在 `snapshot-ch7-8-12.json`，主代理統一build後hash將改變。
