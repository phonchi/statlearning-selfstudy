# scikit-learn User Guide 1.5. Stochastic Gradient Descent
- URL: https://scikit-learn.org/stable/modules/sgd.html（講義連結）；實際依網站版本讀 https://scikit-learn.org/1.6/modules/sgd.html
- 講義頁: p.32（錨文字未提供；本 subagent 未開講義）
- 抓取狀態: OK（curl；1.6 頁 HTTP 200、/stable/（1.9.1）HTTP 200；pandoc 轉純文字，兩版 diff）
- 讀取日期: 2026-11-22

## 重點（中文撰寫，術語保留原文）

### 定位（頁首）
- SGD 是「a simple yet very efficient approach to fitting linear classifiers and regressors under convex loss functions」，例如 (linear) SVM 與 Logistic Regression。
- 「Strictly speaking, SGD is merely an optimization technique and does not correspond to a specific family of machine learning models」；例：`SGDClassifier(loss='log_loss')` 等同以 SGD 擬合的 LogisticRegression；`SGDRegressor(loss='squared_error', penalty='l2')` 與 Ridge 解同一問題。
- 缺點：需調正則化參數與迭代次數；「SGD is sensitive to feature scaling」。Warning：先 shuffle，並以 `make_pipeline(StandardScaler(), SGDClassifier())` 標準化。
- 稀疏資料下可擴展到 >10⁵ 樣本與 >10⁵ 特徵。

### 分類（1.5.1）
- 「Below is the decision boundary of a SGDClassifier trained with the hinge loss, equivalent to a linear SVM.」
- loss：`hinge`＝(soft-margin) linear SVM；`modified_huber`＝smoothed hinge；`log_loss`＝logistic regression；也可用迴歸 loss（target 編碼 ±1）。
- 「The first two loss functions are lazy, they only update the model parameters if an example violates the margin constraint」——可得較稀疏模型。
- 原文：「Using loss="log_loss" or loss="modified_huber" enables the predict_proba method」。（推論／非原文：因此 hinge loss 的 SGDClassifier 不提供 predict_proba。）
- penalty：`l2`（預設）、`l1`、`elasticnet`（(1−l1_ratio)·L2 + l1_ratio·L1）。
- 多元：one versus all (OVA)，K 個二元分類器，取信心分數最高者。
- 支援 averaged SGD（`average=True`）。

### 迴歸（1.5.2）（Q12）
- `SGDRegressor` loss：`squared_error`、`huber`、`epsilon_insensitive`（「linear Support Vector Regression」）；ε 決定不敏感區寬度，「depends on the scale of the target variables」。建議樣本 >10,000 時用。

### Online One-Class SVM（1.5.3）
- `SGDOneClassSVM`：線性 One-Class SVM 的 SGD 版；搭配 kernel approximation 可近似 kernelized `OneClassSVM`，線性於樣本數；「the complexity of a kernelized One-Class SVM is at best quadratic in the number of samples」。
- 數學式：min ½‖w‖² − ρ + (1/(νn))Σξᵢ s.t. ⟨w,xᵢ⟩ ≥ ρ−ξᵢ、ξᵢ ≥ 0；去掉 slack 得 hinge 形式；乘 ν 並令 b=1−ρ 得 min (ν/2)‖w‖² + bν + (1/n)Σmax(0, 1−(⟨w,xᵢ⟩+b))。
- **版本差異**：1.6 寫對應的「α = ν/2」，stable（1.9.1）改為「α = ν」。（以 E=(1/n)ΣL+αR、R=½‖w‖² 計，ν/2·‖w‖² = ν·R，所以 stable 的 α=ν 才與其 R 定義一致；此為本筆記推算。）

### Complexity（1.5.5）
- 訓練成本 O(k n p̄)（k＝epochs，p̄＝每樣本平均非零特徵數），「basically linear in the number of training examples」。

### Tips on Practical Use（1.5.7）
- 「Stochastic Gradient Descent is sensitive to feature scaling, so it is highly recommended to scale your data」；只在訓練集 fit scaler；有內在尺度的特徵（詞頻、指示變數）不必縮放。
- **alpha**：「Finding a reasonable regularization term α is best done using automatic hyper-parameter search」，範圍通常 `10.0**-np.arange(1,7)`。
- 經驗上約看過 10⁶ 個樣本會收斂，`max_iter = np.ceil(10**6 / n)`。

### 數學式（1.5.8）
- 目標：E(w,b) = (1/n)ΣL(yᵢ, f(xᵢ)) + αR(w)，f(x)=wᵀx+b；「α > 0 is a non-negative hyperparameter that controls the regularization strength」。
- **hinge**：「Hinge (soft-margin): equivalent to Support Vector Classification. L = max(0, 1 − yᵢ f(xᵢ))」。
- Perceptron：max(0, −yᵢf(xᵢ))；Modified Huber；Log Loss：log(1+exp(−yᵢf(xᵢ)))，「equivalent to Logistic Regression」；Squared Error ½(y−f)²；Huber；Epsilon-Insensitive：max(0, |yᵢ−f(xᵢ)| − ε)，「equivalent to Support Vector Regression」。
- 「All of the above loss functions can be regarded as an upper bound on the misclassification error (Zero-one loss)」（附圖）。
- R：L2、L1、Elastic Net。**版本差異**：1.6 寫「R(w) := ½Σw_j² = ||w||₂²」（等號右側漏了 ½，為文件筆誤）；stable 已改為「= ½||w||₂²」。
- 與 SVC 的對應（本筆記推算，非原文）：hinge＋L2 時 E = (1/n)Σhinge + (α/2)‖w‖²，整式除以 α 得 ½‖w‖² + (1/(nα))Σhinge，與 SVC 的 ½‖w‖² + CΣhinge 對照即 C = 1/(nα)（SGD 的截距不受正則化，此點兩者一致；但 liblinear 版 LinearSVC 會正則化截距，故不完全等價）。原文沒有寫這個換算。
- SGD 更新：w ← w − η[α∂R/∂w + ∂L/∂w]；截距不正則化。分類預設學習率 `optimal`：η⁽ᵗ⁾ = 1/(α(t₀+t))（Bottou 的 heuristic）；迴歸預設 `invscaling`。
- Implementation（1.5.9）：受 Bottou 的 SvmSGD 影響，學習率排程採自 Pegasos [8]；多元用 one versus all。

### 1.6 與 /stable/ 差異
- 實質差異只有上述兩處（L2 公式的 ½、SGDOneClassSVM 的 α）；其餘為 LaTeX 化（L_2、10^5）、文法與範例清單增減。

## 與下列問題的關聯（只寫有關的題號）
- Q11：1.5.8 hinge＝SVC、log loss＝LR、E = 平均 loss + αR（hinge＋ridge 的寫法；所有 loss 是 0-1 loss 的上界）。
- Q12：epsilon_insensitive＝linear SVR。
- Q13：SGDClassifier(hinge) 等同 linear SVM、對縮放敏感、alpha 的搜尋範圍、log_loss／modified_huber 啟用 predict_proba、與 kernel approximation 搭配。
