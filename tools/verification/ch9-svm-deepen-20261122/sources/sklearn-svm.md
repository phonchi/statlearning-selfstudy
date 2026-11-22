# scikit-learn User Guide 1.4. Support Vector Machines
- URL: https://scikit-learn.org/stable/modules/svm.html（講義連結）；實際依網站版本讀 https://scikit-learn.org/1.6/modules/svm.html
- 講義頁: p.36（錨文字未提供；本 subagent 未開講義）；內容與任務說明中引用的 p.4 字句對照
- 抓取狀態: OK（curl；1.6 頁 HTTP 200，頁面標示「scikit-learn 1.6.1 documentation」；/stable/ 同日 HTTP 200，標示「scikit-learn 1.9.1 documentation」）。以 pandoc 轉純文字後逐段讀；兩版做了文字 diff。
- 讀取日期: 2026-11-22

位置以 1.6.1 的小節號標示（兩版本頁小節號相同，皆 1.4.x）。

## 重點（中文撰寫，術語保留原文）

### 優缺點清單（頁首；與任務說明中引用的講義 p.4 字句比對，未直接開講義）
- 優點（原文四條）：
  1. 「Effective in high dimensional spaces.」
  2. 「Still effective in cases where number of dimensions is greater than the number of samples.」——與任務引用的 p.4 字句一致。
  3. 「Uses a subset of training points in the decision function (called support vectors), so it is also memory efficient.」——**原文只說 memory efficient，沒有提到 run time／執行時間，也沒說跟哪個方法比**（Q1）。
  4. 「Versatile: different Kernel functions can be specified for the decision function.」（後接：提供常用 kernel，也可自訂）
- 缺點（原文兩條）：
  1. 「If the number of features is much greater than the number of samples, avoid over-fitting in choosing Kernel functions and regularization term is crucial.」——與任務引用的 p.4 字句一致。
  2. 「SVMs do not directly provide probability estimates, these are calculated using an expensive five-fold cross-validation (see Scores and probabilities, below).」
- 頁面沒有解釋「p>n 仍有效」的理由，也沒有把它和 dual 連結。

### Classification（1.4.1）
- SVC、NuSVC、LinearSVC 皆可二元與多元分類。SVC 與 NuSVC「accept slightly different sets of parameters and have different mathematical formulations」；LinearSVC「another (faster) implementation ... for the case of a linear kernel」，缺 `support_` 等屬性。
- **LinearSVC 的差異**：「LinearSVC uses squared_hinge loss and due to its implementation in liblinear it also regularizes the intercept」，可用 `intercept_scaling` 減輕；所以結果可能與 SVC／NuSVC 不同。（注意：1.4.7.1 的 LinearSVC 數學式卻寫 hinge，見下。）
- 支持向量屬性：`support_vectors_`、`support_`、`n_support_`。

### 多元分類（1.4.1.1）
- 1.6 原文：「SVC and NuSVC implement the "one-versus-one" approach for multi-class classification. In total, n_classes * (n_classes - 1) / 2 classifiers are constructed」；`decision_function_shape` 可把 OVO 結果「monotonically transform」成 shape (n_samples, n_classes) 的 OvR 決策函數，**預設 'ovr'**。
- LinearSVC 則用「one-vs-the-rest」，訓練 n_classes 個模型；另有 `multi_class='crammer_singer'`，但「In practice, one-vs-rest classification is usually preferred」。
- `dual_coef_` 的 shape 為 (n_classes−1, n_SV)，有詳細排列例子。
- **與 /stable/ 的差異（措辭）**：stable 版明講「Internally, the solver always uses this "ovo" strategy to train the models」，並說預設 'ovr' 是為了介面一致。1.6 版意思相同但沒有「Internally ... always」這句。

### Scores and probabilities（1.4.1.2）（Q13）
- `decision_function` 給每類分數；`probability=True` 時才有 `predict_proba`／`predict_log_proba`。
- 二元情形以 Platt scaling 校準：「logistic regression on the SVM's scores, fit by an additional cross-validation on the training data」。多元情形依 Wu, Lin & Weng (2004) pairwise coupling 推廣 [10]。
- **折數**：本小節只說「an additional cross-validation」，**沒有寫幾折**；「five-fold」只出現在頁首缺點清單。
- 此程序內建於 libsvm，不走 sklearn 的 `CalibratedClassifierCV`。
- 「The cross-validation involved in Platt scaling is an expensive operation for large datasets.」
- 機率與分數可能不一致：argmax 不同；二元時 `predict` 判為正類但 `predict_proba` < 0.5 也可能發生，反之亦然。
- 「Platt's method is also known to have theoretical issues.」若只需信心分數，建議 `probability=False` 改用 `decision_function`。
- `break_ties`：ovr 且 n_classes>2 時，`predict` 預設不打破平手。

### Unbalanced（1.4.1.3）
- `class_weight` 把該類的 C 設為 C*value；`sample_weight` 把第 i 筆的 C 設為 C*sample_weight[i]。

### Regression（1.4.2）（Q12）
- 「The method of Support Vector Classification can be extended to solve regression problems. This method is called Support Vector Regression.」
- 類比：SVC 只依賴部分資料，因「the cost function ... does not care about training points that lie beyond the margin」；SVR 則「ignores samples whose prediction is close to their target」。
- 實作：SVR、NuSVR、LinearSVR（只支援線性核、liblinear 同樣正則化截距）。

### Density estimation（1.4.3）
- 只說 OneClassSVM 用於 outlier detection，並指向 Novelty and Outlier Detection 頁。**本頁沒有 OneClassSVM 的數學式**（其式子在 SGD 頁的 SGDOneClassSVM 小節，見 `sklearn-sgd.md`）。

### Complexity（1.4.4）
- 「compute and storage requirements increase rapidly with the number of training vectors」。libsvm QP solver 介於 O(n_features × n_samples²) 與 O(n_features × n_samples³)，視 cache 使用而定；稀疏資料以平均非零特徵數取代 n_features。
- LinearSVC（liblinear）「much more efficient ... can scale almost linearly to millions of samples and/or features」。

### Tips on Practical Use（1.4.5）
- 大規模線性分類且不想複製資料時建議 `SGDClassifier`，「The objective function can be configured to be almost the same as the LinearSVC model」。
- kernel cache 預設 200 MB，建議可調到 500 或 1000 MB。
- **C**：「C is 1 by default and it's a reasonable default choice」；「If you have a lot of noisy observations you should decrease it」；「decreasing C corresponds to more regularization」。
- LinearSVC／LinearSVR 在 C 大時較不敏感；大 C 訓練較久（最多約 10 倍）。
- **Scaling**：「Support Vector Machine algorithms are not scale invariant, so it is highly recommended to scale your data」；訓練與測試要用同一套縮放，建議 `make_pipeline(StandardScaler(), SVC())`。
- ν「approximates the fraction of training errors and support vectors」。
- 不平衡資料用 `class_weight='balanced'`。
- 隨機性：SVC／NuSVC 只在 `probability=True` 時用亂數洗牌（機率估計）；LinearSVC 在 `dual=True` 時有隨機性。
- `LinearSVC(penalty='l1', dual=False)` 得稀疏解；C 越大選越多特徵。

### Kernel functions（1.4.6）
- linear ⟨x,x′⟩；polynomial (γ⟨x,x′⟩+r)^d（d=`degree`、r=`coef0`）；rbf exp(−γ‖x−x′‖²)（γ=`gamma`，須 >0）；sigmoid tanh(γ⟨x,x′⟩+r)。
- 指向 Kernel Approximation 頁作為更快、更可擴展的 RBF 方案。
- **RBF 參數（1.4.6.1）**（Q9）：C「trades off misclassification of training examples against simplicity of the decision surface. A low C makes the decision surface smooth」；「gamma defines how much influence a single training example has. The larger gamma is, the closer other examples must be to be affected.」建議 GridSearchCV 以指數間距搜尋 C 與 gamma。
- **Custom kernels（1.4.6.2）**：可傳 Python 函式（輸入兩個矩陣，回傳 (n_samples_1, n_samples_2) kernel matrix）或 `kernel='precomputed'` 傳 Gram matrix（predict 時要給測試對訓練的 kernel 值）。此時 `support_vectors_` 為空，只存 `support_`；fit 的第一個參數以 reference 保存。

### Mathematical formulation（1.4.7）
- 總述：最大化與最近訓練點的距離，原文稱之為「(so-called functional margin)」——**與 CS229 用語衝突**（CS229 稱此為 geometric margin；functional margin 是 y(wᵀx+b)）。
- 「when the problem isn't linearly separable, the support vectors are the samples within the margin boundaries」（Q10）。
- **SVC primal（1.4.7.1）**：min ½wᵀw + CΣζᵢ s.t. yᵢ(wᵀφ(xᵢ)+b) ≥ 1−ζᵢ、ζᵢ ≥ 0。C「acts as an inverse regularization parameter」。
- **SVC dual**：min ½αᵀQα − eᵀα s.t. yᵀα=0、0 ≤ αᵢ ≤ C；「Q is an n by n positive semidefinite matrix, Q_ij ≡ y_i y_j K(x_i, x_j)」。sklearn 寫成 **min**（推論／非原文：等於 CS229 的 max W(α) 整體取負號）。αᵢ 稱 dual coefficients，上界為 C。
- 決策函數：Σ_{i∈SV} yᵢαᵢK(xᵢ,x)+b；只需加總支持向量「(i.e. the samples that lie within the margin)」，因為「the dual coefficients αᵢ are zero for the other samples」。`dual_coef_` 存 yᵢαᵢ。
- **Note（Q6）**：libsvm／liblinear 用 C，其他估計器多用 alpha；「when the estimator used is Ridge regression, the relation between them is given as C = 1/alpha」。
- **LinearSVC**：primal 可改寫為 min ½wᵀw + CΣmax(0, 1−yᵢ(wᵀφ(xᵢ)+b))（hinge loss），「This is the form that is directly optimized by LinearSVC」；且「this one does not involve inner products between samples, so the famous kernel trick cannot be applied」（Q11）。**與 1.4.1 的「LinearSVC uses squared_hinge loss」並存，頁面本身未調和**（實際預設 loss 未在本頁核對 API）。
- **NuSVC**：ν-SVC「is a reparameterization of the C-SVC and therefore mathematically equivalent」；ν∈(0,1] 為 margin errors 比例的上界、支持向量比例的下界；margin error＝在其 margin 邊界錯誤一側的點。
- **SVR（1.4.7.2）**：ε-SVR primal min ½wᵀw + CΣ(ζᵢ+ζᵢ*)，約束 yᵢ − wᵀφ(xᵢ) − b ≤ ε+ζᵢ、wᵀφ(xᵢ)+b−yᵢ ≤ ε+ζᵢ*；dual 以 (α−α*)；Q_ij ≡ K(xᵢ,xⱼ)；預測 Σ(αᵢ−αᵢ*)K(xᵢ,x)+b。
- **LinearSVR**：min ½wᵀw + CΣmax(0, |yᵢ−(wᵀφ(xᵢ)+b)| − ε)，「epsilon-insensitive loss, i.e. errors of less than ε are ignored」（Q12）。

### Implementation（1.4.8）
- 底層 libsvm 與 liblinear。

### 1.6 與 /stable/（1.9.1）的差異
- 文字 diff 只有：多元分類段改寫（stable 增加「Internally, the solver always uses this "ovo" strategy」）、「one-vs-the-rest」改為「one-vs-rest ("ovr")」、數處文法（correspond→corresponds）、C=1/alpha 的 LaTeX、參考文獻補全。**優缺點清單、Platt、Tips、數學式內容兩版相同。**

## 與下列問題的關聯（只寫有關的題號）
- Q1：頁首優缺點（memory efficient；p>n 仍有效；p≫n 時需注意 kernel 與正則化）。
- Q6：1.4.7.1 的 C 為 inverse regularization、C=1/alpha 的 Note；1.4.5 C 預設 1、雜訊多降 C。
- Q9：1.4.6.1 gamma 的意義。
- Q10：1.4.7「support vectors are the samples within the margin boundaries」、決策函數只加總 SV。
- Q11：LinearSVC 的 hinge 形式，以及「不涉及內積故無法 kernel trick」。
- Q12：1.4.2、1.4.7.2（SVR、ε-insensitive）。
- Q13：1.4.1.1 OVO／ovr、1.4.1.2 Platt 與 CV、1.4.4 複雜度、LinearSVC vs SVC vs NuSVC。
