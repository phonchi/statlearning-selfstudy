# Tree Methods（XGBoost 官方文件）
- URL: https://xgboost.readthedocs.io/en/stable/treemethod.html
- 講義頁: —（委派補查；與講義 p.48、p.52–54 主題相關）
- 抓取狀態: OK（"Tree Methods — xgboost 3.4.2 documentation"）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）
- 三個內建 tree method：原文 "XGBoost has 3 builtin tree methods, namely exact, approx and hist."；`tree_method` 是 `updater` 的預設組合："the latter is just a pre-configuration of the former"（開頭段）。
- **exact**（Exact Solution 節）：
  - "Exact means XGBoost considers all candidates from data for tree splitting, but underlying the objective is still interpreted as a Taylor expansion."
  - "The vanilla gradient boosting tree algorithm described in reference paper. During split-finding, it iterates over all entries of input data."
  - "It's more accurate (among other greedy methods) but computationally slower"；分散式訓練與 external memory 不支援。
- **Approximated Solutions** 總述："These algorithms build a gradient histogram for each node and iterate through the histogram instead of real dataset."
- **approx**：原文 "It runs sketching before building each tree using all the rows (rows belonging to the root). Hessian is used as weights during sketch."
  ⇒ 每棵樹重做一次分位草圖（不是每個節點），以 **Hessian 加權**。
- **hist**：原文 "An approximation tree method used in LightGBM with slight differences in implementation. It runs sketching before training using only user provided weights instead of hessian."；"The subsequent per-node histogram is built upon this global sketch. This is the fastest algorithm as it runs sketching only once."
  ⇒ 整個訓練只 sketch 一次，**不用 Hessian，只用使用者給的樣本權重**。
- **Implications**：
  - "Some objectives like reg:squarederror have constant hessian. In this case, the hist should be preferred as weighted sketching doesn't make sense with constant weights."
  - "When using non-constant hessian objectives, sometimes approx yields better accuracy, but with slower computation performance."
  - "Most of the time using hist with higher max_bin can achieve similar or even superior accuracy while maintaining good performance."
  - "the actual implementations have some differences than pure math description."
- **Removed Updaters**：
  - `grow_local_histmaker`："During split finding, it first runs a weighted GK sketching for data points belong to current node to find split candidates, using hessian as weights."——即論文的 **local proposal**（每節點、Hessian 加權），已移除；理由之一 "This updater was rarely used in practice"，以及依賴 Rabit 的自訂 reduction 難以重構。
  - distributed colmaker（分散式 exact）："As the exact tree method is slow by itself and scaling is even less efficient, we removed it entirely."
  - `skmaker`：未維護、已移除。
- **Feature Matrix**（頁末表）：
  | | Exact | Approx | Approx (GPU) | Hist |
  |---|---|---|---|---|
  | grow_policy | Depthwise | depthwise/lossguide | depthwise/lossguide | depthwise/lossguide |
  | max_leaves | F | T | T | T |
  | sampling method | uniform | uniform | gradient_based/uniform | gradient_based/uniform |
  | categorical data | F | T | T | T |
  | External memory | F | T | P | T |
  | Distributed | F | T | T | T |
  | Vector leaf | F | F | F | T |
  "column sampling and constraints" 等未列者三者皆支援。
- 其他 updater：Prune 依 `min_split_loss`（gamma）與 `max_depth` 剪枝；Refresh 用新資料更新 cover 與 weight（`refresh_leaf` 為 true 時也更新葉值，但不改 split）。

## 可用的算例或圖解想法
- 三欄比較表（何時 sketch／用什麼權重／候選切點範圍）：
  | 方法 | 何時決定候選切點 | 權重 | 對應論文 |
  |---|---|---|---|
  | exact | 不需要（掃所有值） | — | §3.1 + §4.1 pre-sorted block |
  | approx | 每棵樹開始前，用 root 全部列 | Hessian $h_i$ | §3.2 global proposal + §3.3 |
  | hist（預設） | 訓練前一次 | 只用 user weights | 頁面稱 "used in LightGBM" |
  | ~~local（grow_local_histmaker）~~ | 每個節點 | Hessian | §3.2 local proposal，已移除 |
- 示範：`reg:squarederror` 的 $h_i\equiv1$，Hessian 加權等於不加權，所以 approx 對它沒有額外好處（官方說法）。分類時 $h=p(1-p)$ 隨輪數改變，才有每棵樹重 sketch 的意義（推論）。

## 與下列問題的關聯（只寫有關的）
- **優先查證 2**：論文主張以 $h_i$ 加權；現行實作中**只有 `approx` 這樣做**，且是「每棵樹前」重做；預設的 `hist` 不用 Hessian。教學上說「XGBoost 用 Hessian 加權分位草圖」應加註「指論文／`tree_method='approx'`」。
- **優先查證 1**：exact "iterates over all entries of input data"，approx/hist "iterate through the histogram instead of real dataset"——這是 exact 慢於直方圖法的官方說明。本頁未談 exact 是否每節點重排序（該點見論文 §4.1）。
- **優先查證 4（XGBoost 部分）**：exact 只支援 Depthwise；approx/hist 支援 depthwise/lossguide。預設值見參數筆記（`auto`=`hist`、`depthwise`）。
- quantile sketch 與近似直方圖、直方圖對誰切：候選切點由特徵值的 sketch 決定，再建 gradient histogram。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 與論文用語不同：論文的「approximate」含 global/local；現行 `approx` ≈ global（每棵樹），local 已移除。不要把現行 `approx` 等同於 local proposal。
- 本頁標題段說 "Features/parameters that are not mentioned here are universally supported for all 3 tree methods"，但表格有 4 欄（含 GPU Approx），屬文字小瑕疵。
- 頁面自承實作與數學描述有差異（"the actual implementations have some differences than pure math description"）。
