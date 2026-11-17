# LightGBM Parameters（官方參數頁）
- URL: https://lightgbm.readthedocs.io/en/latest/Parameters.html
- 講義頁: p.56（講義連到 Features 頁；參數頁為委派指定補查）
- 抓取狀態: OK（curl 取得 HTML，轉純文字後 grep 各參數條目）
- 讀取日期: 2026-11-17

## 重點（以中文撰寫，術語保留原文）

| 參數（主要 alias） | 預設 | 限制／選項 | 官方原文（≤25 字） |
|---|---|---|---|
| `num_leaves`（`max_leaves`, `max_leaf_nodes`） | 31 | 1 < num_leaves ≤ 131072 | "max number of leaves in one tree" |
| `max_depth` | -1 | ≤0 表示不限 | "limit the max depth for tree model."；"Tree still grows leaf-wise" |
| `min_data_in_leaf`（`min_child_samples`, `min_samples_leaf`） | 20 | ≥0 | "minimal number of data in one leaf." |
| `min_sum_hessian_in_leaf`（`min_sum_hessian`, `min_hessian`, **`min_child_weight`**） | 1e-3 | ≥0.0 | "minimal sum hessian in one leaf." |
| `max_bin`（`max_bins`） | 255 | >1 | "max number of bins that feature values will be bucketed in" |
| `data_sample_strategy` | `bagging` | `bagging`, `goss` | "goss, Gradient-based One-Side Sampling"；"New in version 4.0.0" |
| `top_rate` | 0.2 | [0,1] | "used only in goss"；"the retain ratio of large gradient data" |
| `other_rate` | 0.1 | [0,1] | "the retain ratio of small gradient data" |
| `bagging_fraction`（`subsample`, `sub_row`） | 1.0 | (0,1] | "randomly select part of data without resampling" |
| `bagging_freq`（`subsample_freq`） | 0 | — | "0 means disable bagging" |
| `feature_fraction`（`colsample_bytree`） | 1.0 | (0,1] | "select a subset of features on each iteration (tree)" |
| `feature_fraction_bynode`（`colsample_bynode`） | 1.0 | (0,1] | "select a subset of features on each tree node" |
| `lambda_l2`（`reg_lambda`, `lambda`） | 0.0 | ≥0 | "L2 regularization" |
| `lambda_l1`（`reg_alpha`） | 0.0 | ≥0 | "L1 regularization" |
| `min_gain_to_split`（`min_split_gain`） | 0.0 | ≥0 | "the minimal gain to perform split" |
| `learning_rate`（`eta`） | 0.1 | >0 | "shrinkage rate" |
| `num_iterations`（`n_estimators`, `num_boost_round`…） | 100 | ≥0 | "number of boosting iterations" |
| `boosting` | `gbdt` | `gbdt`, `rf`, `dart` | — |
| `enable_bundle` | true | bool | "set this to false to disable Exclusive Feature Bundling (EFB)" |
| `max_cat_to_onehot` | 4 | >0 | "one-vs-other split algorithm will be used" |
| `max_cat_threshold` | 32 | >0 | "limit number of split points considered for categorical features." |
| `cat_smooth` | 10.0 | ≥0 | "reduce the effect of noises in categorical features" |
| `cat_l2` | 10.0 | ≥0 | "L2 regularization in categorical split" |
| `min_data_per_group` | 100 | >0 | "minimal number of data per categorical group" |
| `use_missing` | true | bool | "set this to false to disable the special handle of missing value" |
| `zero_as_missing` | false | bool | "set this to true to treat all zero as missing values" |
| `tree_learner` | `serial` | `serial`, `feature`, `data`, `voting` | — |

- **`min_sum_hessian_in_leaf` 就是 `min_child_weight`**（優先查證）：官方 alias 清單明列 `min_child_weight`，預設 `1e-3`。說明原文："minimal sum hessian in one leaf. Like min_data_in_leaf, it can be used to deal with over-fitting"。
- **`min_data_in_leaf` 其實靠 Hessian 近似**，所以偶爾會出現樣本數少於門檻的葉。原文："Note: this is an approximation based on the Hessian"。
- **bagging 要兩個參數一起設才生效**：原文 "Note: to enable bagging, bagging_freq should be set to a non zero value as well"。`data_sample_strategy` 條目也寫 "bagging is only effective when bagging_freq > 0 and bagging_fraction < 1.0"。
- **`feature_fraction` 與 `feature_fraction_bynode` 相乘**：原文 "the final fraction of each node is feature_fraction * feature_fraction_bynode"。另註 bynode "cannot speed up training"。
- **`max_bin` 與記憶體**：原文 "LightGBM will use uint8_t for feature value if max_bin=255"；"small number of bins may reduce training accuracy but may increase general power"。
- **`boosting` 條目末尾有一則 Note**："Note: internally, LightGBM uses gbdt mode for the first 1 / learning_rate iterations"。核對 HTML 後，這則 Note 是 `boosting` 底下的獨立列點，不屬於 gbdt／rf／dart 任一子項，頁面也沒說它適用哪個選項。（推論，未驗證：這句原本可能是附在舊版 `boosting=goss` 下的說明，GOSS 搬到 `data_sample_strategy` 後被留在原處。）教學不要引用這句。
- **GOSS 的位置**：GOSS 是 `data_sample_strategy` 的選項，4.0.0 版起才有；比例由 `top_rate`（$a$）與 `other_rate`（$b$）控制。

## 可用的算例或圖解想法
- 對照表「同一概念在三個套件的名稱」：`min_sum_hessian_in_leaf` ↔ XGBoost `min_child_weight`；`num_leaves` ↔ `max_leaves`；`bagging_fraction` ↔ `subsample`；`feature_fraction` ↔ `colsample_bytree`；`lambda_l2` ↔ `reg_lambda`。全部依官方 alias 清單。
- 預設值差異（推論，需引兄弟筆記）：LightGBM `min_sum_hessian_in_leaf` 預設 1e-3，XGBoost `min_child_weight` 預設 1（見 `xgboost-parameters.md`）。在分類任務中 $h=p(1-p)\le 0.25$，所以 LightGBM 的預設幾乎不限制 Hessian 和，主要靠 `min_data_in_leaf=20` 控制葉的大小。
- 用 `num_leaves=31` 對比 `max_depth=-1`：預設樹可以很深但只有 31 片葉，這是 leaf-wise 的典型設定。（推論：深度 5 的完全二元樹有 32 片葉。）

## 與下列問題的關聯（只寫有關的）
- **min_child_weight**：LightGBM 官方把 `min_child_weight` 當成 `min_sum_hessian_in_leaf` 的 alias，定義是葉內 Hessian 和的下限。這與兄弟筆記中 XGBoost 的官方定義 "Minimum sum of instance weight (hessian) needed in a child." 一致，但預設值不同（1e-3 vs 1）。
- **leaf-wise**：`max_depth` 條目再次寫明 "Tree still grows leaf-wise"。
- **λ 的直覺**：LightGBM 的 `lambda_l2` 預設 0，XGBoost 的 `lambda` 預設 1（兄弟筆記）。兩者預設不同，教學比較時要注意。
- **直方圖**：`max_bin` 預設 255，另有 `min_data_in_bin=3`（"use this to avoid one-data-one-bin (potential over-fitting)"）與 `bin_construct_sample_cnt=200000`（建 bin 時抽樣的筆數）。

## 注意：來源中可疑、過時或與官方文件矛盾之處
- 舊教材常寫 `boosting='goss'`。目前 `boosting` 的選項只有 `gbdt`, `rf`, `dart`，GOSS 改由 `data_sample_strategy='goss'` 指定（4.0.0 起）。講義若用舊寫法要更新。
- 這是 `latest` 文件，版本會變。`bagging_by_query` 標 "New in version 4.6.0"，可見此頁內容至少是 4.6 版之後。
- XGBoost 的 `min_child_weight` 預設與定義，本筆記沒有自行抓取，以兄弟筆記 `xgboost-parameters.md` 為準。
