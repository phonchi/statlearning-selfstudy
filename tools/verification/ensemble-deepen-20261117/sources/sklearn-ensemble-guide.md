# 1.11. Ensembles: Gradient boosting, random forests, bagging, voting, stacking（scikit-learn User Guide）
- URL: https://scikit-learn.org/stable/modules/ensemble.html
- 補充 URL（API 參考頁，預設值出處）: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.{RandomForestClassifier, RandomForestRegressor, ExtraTreesClassifier, BaggingClassifier, VotingClassifier, StackingClassifier}.html
- 講義頁: p.39／p.67
- 抓取狀態: OK（curl，HTTP 200；頁面標題顯示版本 **scikit-learn 1.9.1**。使用者指南 §1.11.2–§1.11.7 全文讀過，§1.11.1（gradient boosting）只讀了選段：HGBT 概述、l2 正則與葉值、缺失值、Why it's faster、tree size、subsampling／OOB、feature importance；6 個 API 頁讀了 constructor 簽名並以 grep 讀取相關參數說明，非逐頁全文）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
### Random forest（使用者指南 §1.11.2.1；API 頁）
- 兩個隨機來源：每棵樹用 bootstrap 樣本；每次 split 從 `max_features` 大小的隨機特徵子集中找最佳切點。目的："to decrease the variance of the forest estimator"；並承認 "sometimes at the cost of a slight increase in bias"（§1.11.2.1）。
- **預設值（API 頁 constructor 簽名）**：`RandomForestClassifier(n_estimators=100, max_features='sqrt', bootstrap=True, oob_score=False, max_samples=None, ...)`；`RandomForestRegressor(n_estimators=100, max_features=1.0, bootstrap=True, oob_score=False, ...)`。
- RandomForestRegressor 的 `max_features` 說明："The default of 1.0 is equivalent to bagged trees and more randomness can be achieved by setting smaller values, e.g. 0.3."；兩者皆註明 "Changed in version 1.1"（舊預設 `"auto"`）。
- 使用者指南 §1.11.2.3 的建議："Empirical good default values are max_features=1.0 ... for regression problems, and max_features="sqrt" ... for classification tasks"；並說 "The best parameter values should always be cross-validated."
- `max_features` 的意義："The lower the greater the reduction of variance, but also the greater the increase in bias."（§1.11.2.3）
- `n_estimators`："The larger the better, but also the longer it will take to compute"，且超過某個臨界數後結果不再顯著變好（§1.11.2.3）。
- 聚合方式：**"the scikit-learn implementation combines classifiers by averaging their probabilistic prediction, instead of letting each classifier vote for a single class."**（並註明這與原始論文 [B2001] 不同）（§1.11.2.1）——即 sklearn 的 RF 是 soft voting。
- bootstrap 與 OOB：RF 預設 `bootstrap=True`，extra-trees 預設 `bootstrap=False`；"When using bootstrap sampling the generalization error can be estimated on the left out or out-of-bag samples. This can be enabled by setting oob_score=True."（§1.11.2.3）。API：`oob_score` "Only available if bootstrap=True"；分類預設用 `accuracy_score`、迴歸用 `r2_score`，可傳 callable。
- `max_samples=None` 時 "draw X.shape[0] samples"（每棵樹抽 $n$ 筆）。
- API 頁另述 RF 原生支援 NaN：訓練時在每個 split 學缺失值走左或右（RandomForestClassifier／Regressor 說明段）。

### Extra-Trees（§1.11.2.2）
- 與 RF 相同地抽候選特徵子集，但 "thresholds are drawn at random for each candidate feature and the best of these randomly-generated thresholds is picked as the splitting rule."
- 效果："This usually allows to reduce the variance of the model a bit more, at the expense of a slightly greater increase in bias"。
- 範例（`make_blobs`, 10 特徵 100 群，5-fold CV）：單樹 0.98、RF（10 棵）0.999、ExtraTrees（10 棵）>0.999。
- API 預設：`ExtraTreesClassifier(max_features='sqrt', bootstrap=False, ...)`。

### 變數重要度（§1.11.2.5）
- MDI（impurity-based）：把特徵在樹中所影響的樣本比例與不純度下降結合，再 "By averaging the estimates of predictive ability over several randomized trees one can reduce the variance of such an estimate"。
- 警告兩個缺陷："First they are computed on statistics derived from the training dataset"；"Secondly, they favor high cardinality features, that is features with many unique values."
- "Permutation feature importance is an alternative to impurity-based feature importance that does not suffer from these flaws."
- `feature_importances_` 非負且總和為 1.0。

### Bagging meta-estimator（§1.11.3；API）
- 依抽法命名：只抽樣本（不放回）= Pasting [B1999]；有放回抽樣本 = Bagging [B1996]；抽特徵 = Random Subspaces [H1998]；樣本與特徵都抽 = Random Patches [LG2012]。
- "bagging methods work best with strong and complex models (e.g., fully developed decision trees)"，相對地 "boosting methods which usually work best with weak models (e.g., shallow decision trees)."
- API 預設：`BaggingClassifier(estimator=None→DecisionTreeClassifier, n_estimators=10, max_samples=None, max_features=1.0, bootstrap=True, bootstrap_features=False, oob_score=False)`。**此處 `max_features` 是「每個 base estimator 抽多少特徵」**（"The number of features to draw from X to train each base estimator"），與 RF 的「每個 split 考慮多少特徵」意義不同。
- 範例：`BaggingClassifier(KNeighborsClassifier(), max_samples=0.5, max_features=0.5)`——非樹的 base learner。

### Voting（§1.11.4；API）
- Hard：取各分類器預測標籤的眾數；平手時 "select the class based on the ascending sort order"。
- Soft："returns the class label as argmax of the sum of predicted probabilities"；可加 `weights`，例：三分類器、三類別，加權平均機率 (0.37, 0.4, 0.23) → 預測類別 2。
- API：`VotingClassifier(voting='hard', weights=None)`；`'soft'` "is recommended for an ensemble of well-calibrated classifiers"；soft 需要各 estimator 支援 `predict_proba`。
- 用途："useful for a set of equally well performing models in order to balance out their individual weaknesses."
- 範例（iris 兩特徵、5-fold）：LR 0.95、RF 0.94、NB 0.91、hard voting 0.95。

### Stacking（§1.11.6；API）
- "the predictions of each individual estimator are stacked together and used as input to a final estimator"；"This final estimator is trained through cross-validation."
- 關鍵機制："the estimators are fitted on the whole training data X_train"；"the final_estimator is trained on out-samples using sklearn.model_selection.cross_val_predict internally."
- API `cv` 參數：預設 `None` = "the default 5-fold cross validation"；分類且 y 為二元／多類時用 `StratifiedKFold`，否則 `KFold`；`shuffle=False`。`cv="prefit"` 時 final estimator 用全訓練集上的預測訓練，文件警告 "there is a very high risk of overfitting"（若 base estimators 用同一份資料訓練）。
- `final_estimator` 預設：`StackingClassifier` 為 `LogisticRegression`（API 頁）。`passthrough=False`（True 時 final estimator 也看原始特徵）。
- `stack_method='auto'` 依序嘗試 `predict_proba`、`decision_function`、`predict`；二元分類用 `predict_proba` 時丟掉第一欄（兩欄完全共線）。
- 效果與成本："a stacking predictor predicts as good as the best predictor of the base layer and even sometimes outperforms it"；"training a stacking predictor is computationally expensive."
- 可多層：把 `final_estimator` 設成另一個 Stacking 物件。

### 與 boosting 有關、可順帶引用的段落
- 傳統 GBDT 為何慢（§1.11.1.1.8 "Why it's faster"）：`GradientBoostingClassifier` "requires sorting the samples at each node (for each feature)"，每節點 $O(n_\text{features}\times n\log n)$；HGBT 用直方圖，每節點 $O(n_\text{features}\times n)$，分箱的排序 "only happens once at the very beginning of the boosting process"。
- HGBT 葉值："w = -sum_gradient / (sum_hessian + l2_regularization) (see equation (5) in [XGBoost])"；分母加正則 "penalizes the leaves with small hessians (flat regions)"（§1.11.1.1.1 Details on l2 regularization）。
- HGBT 缺失值："the tree grower learns at each split point whether samples with missing values should go to the left or right child"（依 potential gain 決定）；訓練時沒見過缺失值的特徵，預測時缺失值送往樣本較多的子節點（§1.11.1.1.2）。
- 樹大小與交互作用（§1.11.1.2.2）："a tree of depth h can capture interactions of order h"；`max_leaf_nodes` 以 best-first search 長樹，且 "max_leaf_nodes == interaction.depth + 1"（對應 R gbm）。
- GB 的 OOB（§1.11.1.2.6）："OOB estimates are usually very pessimistic thus we recommend to use cross-validation instead"——**這句在 stochastic gradient boosting 段落，針對 `oob_improvement_`，不是在講 RF**。

## 可用的算例或圖解想法
- soft voting 的 3×3 加權機率表可直接搬進講義，再造一個 hard 與 soft 結果不同的例子（自擬例，非來源：二元分類，三個分類器給類別 1 的機率為 0.51, 0.51, 0.10；hard voting 兩票對一票選類別 1，soft voting 平均 $\approx0.373<0.5$ 選類別 0）。
- `BaggingClassifier(max_samples, max_features, bootstrap, bootstrap_features)` 四參數對應 Pasting／Bagging／Random Subspace／Random Patches，可做成 2×2 表。
- `RandomForestRegressor()` 預設等同 bagged trees——可做「預設 RF 迴歸 vs `max_features=0.3`」的小實驗。

## 與下列問題的關聯（只寫有關的）
- 硬／軟投票、stacking vs voting：§1.11.4、§1.11.6 及 API（stacking 用 `cross_val_predict` 產生 out-of-fold 預測訓練 meta learner；voting 不學權重，`weights` 由使用者給）。
- base learner 怎麼選：§1.11.3 "bagging ... work best with strong and complex models"、boosting "work best with weak models"。
- 為何 RF 取 $m\approx\sqrt p$：sklearn 只稱為 "Empirical good default"，並提醒應交叉驗證；迴歸預設是 1.0（全部特徵）而非 ESL 的 $p/3$。
- 變數重要度：MDI 為各樹平均；permutation importance 為替代。
- 優先查證 #1（排序成本）：sklearn 對其經典 GBDT 說「每個節點都要排序」；這是 sklearn 自己實作的描述，不代表 XGBoost exact 演算法（XGBoost 論文的 pre-sorted block 見其他筆記，推論）。
- 缺失值方向、λ 的直覺、葉值 = −G/(H+λ)：§1.11.1.1.1–1.11.1.1.2。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 同一節內前後說法不一：§1.11.2.1 說 sklearn RF "averaging their probabilistic prediction, instead of letting each classifier vote"，但幾段後比較 HGBT 時又說 "random forests use a majority vote to predict the outcome"。以前者（實作描述）為準。
- §1.11.2.3 說 "The default value of max_features=1.0 is equivalent to bagged trees"——只對 `RandomForestRegressor` 成立；Classifier 預設是 `"sqrt"`。
- §1.11.1.2.7 稱 GB 的 feature importance "is based on entropy"，但 GB 的迴歸樹以 MSE 類準則分裂（推論；未在本頁核對 `criterion` 預設，引用時避免此句）。
- 版本敏感：`max_features` 預設在 1.1 版改過；舊教材的 `"auto"` 已過時。本筆記依 1.9.1。
