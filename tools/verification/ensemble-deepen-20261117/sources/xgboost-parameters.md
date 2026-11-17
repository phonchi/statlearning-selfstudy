# XGBoost Parameters（官方參數頁）
- URL: https://xgboost.readthedocs.io/en/stable/parameter.html
- 講義頁: p.48（講義連到文件首頁；參數頁為委派指定補查）
- 抓取狀態: OK（頁面標題 "XGBoost Parameters — xgboost 3.4.2 documentation"）
- 讀取日期: 2026-11-17

所有條目位於「Parameters for Tree Booster」一節，除非另註。引文為該參數條目的定義句；預設值與 range 照頁面原樣。

## 重點（以中文撰寫，術語保留原文）

| 參數（alias） | 預設 | range／選項 | 官方原文（≤25 字） |
|---|---|---|---|
| `eta`（`learning_rate`） | 0.3 | [0,1] | "Step size shrinkage used in update to prevent overfitting." |
| `gamma`（`min_split_loss`） | 0 | [0,∞] | "Minimum loss reduction required to make a further partition on a leaf node of the tree." |
| `max_depth` | 6（int32） | [0,∞] | "Maximum depth of a tree."；"0 indicates no limit on depth."；"exact tree method requires non-zero value." |
| `min_child_weight` | 1 | [0,∞] | "Minimum sum of instance weight (hessian) needed in a child." |
| `max_delta_step` | 0 | [0,∞] | "Maximum delta step we allow each leaf output to be. If the value is set to 0, it means there is no constraint." |
| `subsample` | 1 | (0,1] | "Subsample ratio of the training instances."；"Subsampling will occur once in every boosting iteration." |
| `colsample_bytree` / `_bylevel` / `_bynode` | 1 | (0,1] | "This is a family of parameters for subsampling of columns." |
| `lambda`（`reg_lambda`） | 1 | [0,∞] | "L2 regularization term on weights."；"This is the λ described in the Introduction to Boosted Trees." |
| `alpha`（`reg_alpha`） | 0 | [0,∞] | "L1 regularization term on weights." |
| `tree_method` | `auto` | `auto`, `exact`, `approx`, `hist` | "auto: Same as the hist tree method." |
| `scale_pos_weight` | 1 | — | "Control the balance of positive and negative weights, useful for unbalanced classes." |
| `grow_policy` | `depthwise` | `depthwise`, `lossguide` | "Controls a way new nodes are added to the tree."（lossguide ≈ leaf-wise 為推論） |
| `max_leaves` | 0（int32） | — | "Maximum number of nodes to be added. Not used by exact tree method." |
| `max_bin` | 256（int32） | — | "Maximum number of discrete bins to bucket continuous features." |

細節：
- `min_child_weight` 其餘原文：若分裂後葉節點的 instance weight 和小於門檻，"then the building process will give up further partitioning."；"In linear regression task, this simply corresponds to minimum number of instances needed to be in each node."；並註明 "The larger min_child_weight is, the more conservative the algorithm will be."；向量葉時 "the mean Hessian across targets is used"。
- `gamma` 另有："Note that a tree where no splits were made might still contain a single terminal node with a non-zero score."；"This is the same γ described in the Introduction to Boosted Trees."
- `eta`："eta shrinks the feature weights to make the boosting process more conservative."
- `max_depth`："Beware that XGBoost aggressively consumes memory when training a deep tree."
- `max_delta_step`："it might help in logistic regression when class is extremely imbalanced."；"Set it to value of 1-10 might help control the update."
- `subsample`："Setting it to 0.5 means that XGBoost would randomly sample half of the training data prior to growing trees."
- `sampling_method`（預設 `uniform`）：`gradient_based` 的抽樣機率 "proportional to the regularized absolute value of gradients (more specifically, $\sqrt{g^2+\lambda h^2}$)"；"only supported when tree_method is set to hist"。
- `colsample_*`：bytree 每棵樹抽一次；bylevel "Columns are subsampled from the set of columns chosen for the current tree"；bynode "Subsampling occurs once every time a new split is evaluated"，且 "This is not supported by the exact tree method."；三者相乘："{'colsample_bytree':0.5, 'colsample_bylevel':0.5, 'colsample_bynode':0.5} with 64 features will leave 8 features to choose from at each split."
- `tree_method` 四選項原文：
  - "exact: Exact greedy algorithm. Enumerates all split candidates."
  - "approx: Approximate greedy algorithm using quantile sketch and gradient histogram."
  - "hist: Faster histogram optimized approximate greedy algorithm."
- `scale_pos_weight`："A typical value to consider: sum(negative instances) / sum(positive instances)."
- `grow_policy`："Currently supported only if tree_method is set to hist or approx."；"depthwise: split at nodes closest to the root."；"lossguide: split at nodes with highest loss change."
- `max_bin`："Only used if tree_method is set to hist or approx."；"Increasing this number improves the optimality of splits at the cost of higher computation time."
- `num_parallel_tree`（預設 1）："This option is used to support boosted random forest."
- `updater` 中的對應：`grow_colmaker`（非分散式、column-based）、`grow_histmaker`（"based on global proposal of histogram counting"）、`grow_quantile_histmaker`（"Grow tree using quantized histogram"）；`prune` "prunes the splits where loss < min_split_loss (or gamma)"。
- 類別特徵：「The exact tree method is not supported for categorical features.」；`max_cat_to_onehot`（1.6.0 加入）"When number of categories is lesser than the threshold then one-hot encoding is chosen, otherwise the categories will be partitioned into children nodes."；**本頁未列 `max_cat_to_onehot` 的預設值**。
- General Parameters：`booster` 預設 `gbtree`；"Dropout parameters like rate_drop can be used directly with tree models. booster=dart remains supported for compatibility."；`booster=gblinear` "Deprecated since version 3.3.0"。
- Dropout（DART）參數：`sample_type` 預設 uniform、`normalize_type` 預設 tree（新樹權重 $1/(k+\eta)$，被丟樹乘 $k/(k+\eta)$）、`rate_drop` 預設 0.0、`one_drop` 預設 0、`skip_drop` 預設 0.0。

## 可用的算例或圖解想法
- **`min_child_weight` 與分類（推論）**：logistic loss 下 $h_i=p_i(1-p_i)\le 0.25$，所以預設 `min_child_weight=1` 對分類而言要求子節點至少約 4 筆「最不確定」的樣本（p=0.5），若樣本已被預測得很篤定（p 接近 0 或 1），所需筆數會大很多。回歸（平方損失 h=1）時就是官方說的「最少樣本數」。這個數值例子不在官方頁面，需標推論。
- **`gamma` 與 Eq.7**：gamma 對應論文 Eq.7 的 −γ（官方句："This is the same γ described in the Introduction to Boosted Trees."）。
- 三個 colsample 相乘的 64→8 例子可直接用。
- `max_delta_step` 可連到「分類時 h 很小 ⇒ $-G/(H+\lambda)$ 可能很大」的直覺（推論；官方只說極度不平衡時可能有幫助）。

## 與下列問題的關聯（只寫有關的）
- **優先查證 3（`min_child_weight`）**：官方定義原文 "Minimum sum of instance weight (hessian) needed in a child."（Parameters for Tree Booster → min_child_weight），預設 1、range [0,∞]。與 h=p(1−p) 的連結屬推論。
- **優先查證 4（XGBoost 部分）**：`tree_method` 預設 `auto`，且 "auto: Same as the hist tree method."；`grow_policy` 預設 `depthwise`，`lossguide` 只在 hist/approx 下可用；`max_bin` 預設 256；`max_leaves` 預設 0。所以 XGBoost 預設是 depthwise，但可切成 lossguide；把兩者分別稱為 level-wise／leaf-wise 是推論（頁面未用這些詞）。
- λ 的直覺：`lambda` 預設 1，即 Eq.5 分母預設就 +1。
- leaf-wise vs level-wise：`grow_policy` 兩選項的原文定義。頁面沒有用 "leaf-wise"／"level-wise" 這兩個詞；depthwise ≈ level-wise、lossguide（"split at nodes with highest loss change"）≈ leaf-wise 屬推論。
- 直方圖：`max_bin` 是 hist/approx 的桶數。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 版本：本頁為 stable = 3.4.2；`latest` 已是 3.5.0-dev。預設值未來可能變動，引用時寫明版本。
- 舊教材常說 XGBoost 預設 `exact` 或 `approx`；現行為 `auto` = `hist`（本頁未寫此行為從哪一版開始；若要寫版本需另查 release notes）。
- `booster=dart` 已改為「dropout 參數可直接用在 tree model」，DART 教學頁也同步改寫；舊程式碼仍可用。
- `gblinear` 自 3.3.0 起 deprecated。
